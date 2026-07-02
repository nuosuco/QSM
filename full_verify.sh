#!/bin/bash
# 全量QVM验证脚本 - QEntL编译器 + QVM
set -o pipefail
cd /root/QSM

COMPILER="./bin/qcl_bootstrap"
QVM="./bin/qvm_bootstrap"
OUTDIR="./full_verify_output"
mkdir -p "$OUTDIR"

TOTAL=0; C_OK=0; C_FAIL=0; R_OK=0; R_FAIL=0
C_ERR=(); R_ERR=()

mapfile -t QENTL_FILES < <(find . -name "*.qentl" -type f | sort)
TOTAL=${#QENTL_FILES[@]}
echo "发现 $TOTAL 个 .qentl 文件"
echo "==="

for f in "${QENTL_FILES[@]}"; do
    rel="${f#./}"
    out="$OUTDIR/${rel%.qentl}.qbc"
    mkdir -p "$(dirname "$out")"
    
    # Compile
    result=$( "$COMPILER" "$f" "$out" 2>&1 )
    rc=$?
    if [ $rc -eq 0 ] && [ -f "$out" ]; then
        C_OK=$((C_OK+1))
        # Run on QVM
        run_result=$(timeout 30 "$QVM" "$out" 2>&1 )
        rc=$?
        if [ $rc -eq 0 ]; then
            R_OK=$((R_OK+1))
        else
            R_FAIL=$((R_FAIL+1))
            R_ERR+=("$rel")
        fi
    else
        C_FAIL=$((C_FAIL+1))
        C_ERR+=("$rel")
    fi
done

echo ""
echo "=== 全量QVM验证报告 ==="
echo "总文件: $TOTAL"
echo "编译成功: $C_OK / 编译失败: $C_FAIL"
echo "QVM运行成功: $R_OK / QVM运行失败: $R_FAIL"
echo ""
if [ ${#C_ERR[@]} -gt 0 ]; then
    echo "--- 编译失败 (${#C_ERR[@]}) ---"
    for e in "${C_ERR[@]}"; do echo "  - $e"; done
fi
if [ ${#R_ERR[@]} -gt 0 ]; then
    echo "--- QVM运行失败 (${#R_ERR[@]}) ---"
    for e in "${R_ERR[@]}"; do echo "  - $e"; done
fi

cat > "$OUTDIR/verify_summary.txt" <<EOF
全量QVM验证报告
日期: $(date)
总文件: $TOTAL
编译成功: $C_OK | 编译失败: $C_FAIL
QVM运行成功: $R_OK | QVM运行失败: $R_FAIL
EOF
