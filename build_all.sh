#!/bin/bash
set -u
OUTDIR="/root/QSM/build_report"
MODELS=(QSM Ref SOM WeQ)
mkdir -p "$OUTDIR/logs"
total=0; success=0; fail=0; total_bytes=0

printf "%-55s %-8s %-8s %-10s %-12s\n" "FILE" "STATUS" "FIRST" "DEFs" "ENDs" > "$OUTDIR/build.log"
echo "" > "$OUTDIR/summary.json"

for MODEL in "${MODELS[@]}"; do
  DIR="QEntL/Models/$MODEL"
  if [ ! -d "$DIR" ]; then continue; fi
  for src in $(find "$DIR" -maxdepth 1 -name '*.qentl' | sort); do
    base=$(basename "$src" .qentl)
    dest="$OUTDIR/logs/${MODEL}_${base}.qbc"
    total=$((total+1))
    # Run compiler
    if bin/qcl_phase2 "$src" "$dest" > /dev/null 2>&1; then
      status="OK"
      success=$((success+1))
    else
      status="FAIL"
      fail=$((fail+1))
    fi
    # Inspect artifact
    if [ "$status" = "OK" ] && [ -f "$dest" ]; then
      sz=$(stat -c%s "$dest" 2>/dev/null || echo 0)
      total_bytes=$((total_bytes+sz))
      if [ "$sz" -gt 0 ]; then
        first=$(xxd -l1 -p "$dest")
      else
        first="N/A"
      fi
      defs=$(grep -c 'DEF' "$dest" 2>/dev/null || echo 0)
      ends=$(grep -c 'END' "$dest" 2>/dev/null || echo 0)
      printf "%-55s %-8s %-8s %-10s %-12s\n" "$MODEL/$src" "$status" "$first" "$defs" "$ends" >> "$OUTDIR/build.log"
    else
      printf "%-55s %-8s %-8s %-10s %-12s\n" "$MODEL/$src" "$status" "-" "-" "-" >> "$OUTDIR/build.log"
    fi
  done
done
echo ""
echo "BUILD SUMMARY"
echo "============="
echo "Total modules:  $total"
echo "Succeeded:      $success"
echo "Failed:         $fail"
echo "Total bytecode bytes: $total_bytes"
echo "Per-model:"
for MODEL in "${MODELS[@]}"; do
  DIR="QEntL/Models/$MODEL"
  cnt=$(find "$DIR" -maxdepth 1 -name '*.qentl' 2>/dev/null | wc -l)
  ok=$(grep -c "^${MODEL}.*/.*OK" "$OUTDIR/build.log" 2>/dev/null || echo 0)
  echo "  $MODEL: $cnt modules, $ok compiled"
done
cat "$OUTDIR/build.log"
