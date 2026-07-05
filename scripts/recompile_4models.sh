#!/bin/bash
set -u
cd /root/QSM
QCL="./bin/qcl_phase2"
MODELS="QEntL/Models/QSM QEntL/Models/Ref QEntL/Models/SOM QEntL/Models/WeQ"

TOTAL=0; SUCCESS=0; FAIL=0
DEFPAR_OK=0; DEFPAR_BAD=0; HEADER_BAD=0; COMPILE_ERR=0
REPORT=""

for dir in $MODELS; do
    echo "=============================================="
    echo "  Compiling: $dir"
    echo "=============================================="
    for src in "$dir"/*.qentl; do
        [ -f "$src" ] || continue
        name=$(basename "$src" .qentl)
        out="${src%.qentl}.qbc"
        TOTAL=$((TOTAL+1))
        
        # Remove stale .qbc so we rebuild
        rm -f "$out"
        
        # Compile
        compile_out=$("$QCL" "$src" 2>&1)
        rc=$?
        if [ $rc -ne 0 ]; then
            FAIL=$((FAIL+1)); COMPILE_ERR=$((COMPILE_ERR+1))
            REPORT="$REPORT FAIL  | $name | rc=$rc | $(echo "$compile_out" | tail -1 | cut -c1-100)\n"
            echo "  FAIL  | $name | rc=$rc"
            continue
        fi
        
        # Check .qbc exists
        if [ ! -f "$out" ]; then
            FAIL=$((FAIL+1)); COMPILE_ERR=$((COMPILE_ERR+1))
            REPORT="$REPORT FAIL  | $name | no .qbc produced\n"
            echo "  FAIL  | $name | no .qbc produced"
            continue
        fi
        
        # Check first byte 0x14
        first=$(xxd -l 1 -p "$out" 2>/dev/null)
        sz=$(stat -c%s "$out" 2>/dev/null)
        
        if [ "$first" != "14" ]; then
            FAIL=$((FAIL+1)); HEADER_BAD=$((HEADER_BAD+1))
            REPORT="$REPORT FAIL  | $name | header=0x$first sz=$sz (expected 0x14)\n"
            echo "  FAIL  | $name | header=0x$first sz=$sz (expected 0x14)"
            continue
        fi
        
        # Check DEF/END pairing by scanning .qbc for magic markers
        # We extract DEF/END from the source text and verify the .qbc is non-trivial
        def_count=$(grep -c '^DEF ' "$src" 2>/dev/null || echo 0)
        end_count=$(grep -c '^END' "$src" 2>/dev/null || echo 0)
        # .qentl DEF/END markers — check pairing in source (compiler should enforce)
        if [ "$def_count" = "$end_count" ]; then
            DEFPAR_OK=$((DEFPAR_OK+1))
        else
            DEFPAR_BAD=$((DEFPAR_BAD+1))
        fi
        
        SUCCESS=$((SUCCESS+1))
        fcount=$(echo "$compile_out" | grep -oP '函数=\K[0-9]+' | head -1)
        fcount=${fcount:-?}
        REPORT="$REPORT OK   | $name | bytes=$sz header=0x14 defs=$def_count fns=$fcount\n"
        echo "  OK   | $name | bytes=$sz header=0x14 defs=$def_count fns=$fcount"
    done
done

echo ""
echo "============================================================"
echo "  四大模型全量编译验证报告"
echo "============================================================"
echo "  总模块数       : $TOTAL"
echo "  编译成功       : $SUCCESS"
echo "  编译失败       : $FAIL"
echo "    - 编译错误   : $COMPILE_ERR"
echo "    - 首字节!=0x14: $HEADER_BAD"
echo "  DEF/END 配对   : OK=$DEFPAR_OK BAD=$DEFPAR_BAD"
echo "============================================================"
echo ""
echo "--- 详细清单 ---"
echo -e "$REPORT"
echo "--- END ---"
