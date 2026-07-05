#!/bin/bash
# Batch compile all four model modules (QSM / Ref / SOM / WeQ)
set -euo pipefail
cd /root/QSM
COMPILER=./bin/qcl_phase2
SUCCESS=0
FAIL=0
TOTAL_BYTES=0
RESULTS=()

for model in QSM Ref SOM WeQ; do
    srcdir="QEntL/Models/$model"
    if [ ! -d "$srcdir" ]; then
        RESULTS+=("FAIL | $model | directory not found")
        FAIL=$((FAIL+1))
        continue
    fi
    for f in "$srcdir"/*.qentl; do
        [ -f "$f" ] || continue
        name=$(basename "$f" .qentl)
        out="$srcdir/$name.qbc"
        compile_output=$(timeout 15 "$COMPILER" "$f" 2>&1) || true

        # Check compilation succeeded and .qbc exists
        if ! echo "$compile_output" | grep -q "编译完成" || [ ! -f "$out" ]; then
            RESULTS+=("FAIL | $model/$name | compile failed")
            FAIL=$((FAIL+1))
            continue
        fi

        sz=$(stat -c%s "$out" 2>/dev/null || echo 0)
        TOTAL_BYTES=$((TOTAL_BYTES + sz))
        first_byte=$(xxd -l 1 -p "$out" 2>/dev/null)

        # Check DEF/END pairing via compile output
        func_count=$(echo "$compile_output" | grep -oP '函数=\K[0-9]+' || echo "?")
        # Count DEF and END markers in source
        def_count=$(grep -c '^DEF\b' "$f" 2>/dev/null || echo 0)
        end_count=$(grep -c '\bEND\b' "$f" 2>/dev/null || echo 0)
        pair_ok="OK"
        if [ "$def_count" != "$end_count" ]; then
            pair_ok="MISMATCH(DEF=$def_count END=$end_count)"
        fi

        if [ "$first_byte" = "14" ]; then
            RESULTS+=("OK   | $model/$name | ${sz}B | 0x14 | funcs=$func_count | $pair_ok")
            SUCCESS=$((SUCCESS+1))
        else
            RESULTS+=("FAIL | $model/$name | ${sz}B | header=0x$first_byte (exp 0x14)")
            FAIL=$((FAIL+1))
        fi
    done
done

TOTAL=$((SUCCESS+FAIL))
echo "========== FOUR-MODEL BATCH COMPILE RESULTS =========="
echo "Modules: $TOTAL | Success: $SUCCESS | Failed: $FAIL | Total bytes: $TOTAL_BYTES"
echo "====================================================="
for r in "${RESULTS[@]}"; do
    echo "$r"
done
echo "====================================================="
echo "OVERALL: $( [ $FAIL -eq 0 ] && echo 'ALL PASSED' || echo "$FAIL FAILURES" )"
echo "====================================================="
