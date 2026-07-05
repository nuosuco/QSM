#!/usr/bin/env bash
set -euo pipefail
cd /root/QSM
COMPILER="./bin/qcl_phase2"
MODELS_DIR="QEntL/Models"
ORPHAN_COUNT=0
for model in QSM Ref SOM WeQ; do
  mdir="$MODELS_DIR/$model"
  [ -d "$mdir" ] || continue
  for qbc in "$mdir"/*.qbc "$mdir"/*/*.qbc; do
    [ -f "$qbc" ] || continue
    bn=$(basename "$qbc" .qbc)
    rel="${qbc#$mdir/}"
    in_docs=0; case "$rel" in docs/*) in_docs=1;; esac
    own=0
    case "$bn" in ${model,,}*) own=1;; esac
    if [ "$model" = "SOM" ] && [ "$bn" = "som_core_part2" ]; then own=1; fi
    if [ "$in_docs" -eq 0 ] && [ "$own" -eq 0 ]; then
      echo "ORPHAN:rm $qbc"
      rm -f "$qbc"
      ORPHAN_COUNT=$((ORPHAN_COUNT+1))
    fi
  done
done
for qbc in "$MODELS_DIR"/*.qbc; do
  [ -f "$qbc" ] || continue
  [ "$(basename "$qbc")" = "Models_QNS_Integration_Test.qbc" ] && continue
  echo "ROOT-ORPHAN:rm $qbc"
  rm -f "$qbc"
  ORPHAN_COUNT=$((ORPHAN_COUNT+1))
done
echo "ORPHANS_REMOVED=$ORPHAN_COUNT"
TOTAL=0; OK=0; WARN=0; FAIL=0
while IFS= read -r qentl; do
  qbc="${qentl%.qentl}.qbc"
  TOTAL=$((TOTAL+1))
  rel="${qentl#/root/QSM/}"
  need=0
  if [ ! -f "$qbc" ]; then need=1
  elif [ "$qentl" -nt "$qbc" ]; then need=1
  fi
  if [ "$need" -eq 0 ]; then
    sz=$(stat -c%s "$qbc"); fb=$(xxd -l1 -p "$qbc")
    echo "SKIP | $rel | ${sz}B | 0x${fb} | up-to-date"
    OK=$((OK+1)); continue
  fi
  coutput=$(timeout 15 "$COMPILER" "$qentl" 2>&1) && rc=0 || rc=$?
  if [ "$rc" -ne 0 ] || [ ! -f "$qbc" ]; then
    echo "FAIL | $rel | rc=$rc"
    FAIL=$((FAIL+1)); continue
  fi
  sz=$(stat -c%s "$qbc"); fb=$(xxd -l1 -p "$qbc")
  funcs=$(echo "$coutput" | grep -oP '函数=\K\d+' || echo "0")
  if [ "$fb" = "14" ] && [ "$sz" -gt 0 ]; then
    echo "OK   | $rel | ${sz}B | 0x14 | funcs=$funcs"
    OK=$((OK+1))
  else
    hdr=$( [ "$sz" -eq 0 ] && echo "empty" || echo "0x${fb}" )
    echo "WARN | $rel | ${sz}B | ${hdr} | funcs=$funcs"
    WARN=$((WARN+1)); OK=$((OK+1))
  fi
done < <(find "$MODELS_DIR" -name '*.qentl' -type f | sort)
echo "SUMMARY Total=$TOTAL OK=$OK WARN=$WARN FAIL=$FAIL"
