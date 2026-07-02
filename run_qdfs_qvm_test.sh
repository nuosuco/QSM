#!/bin/bash
# QDFS QVM验证测试脚本
BASEDIR="$(cd "$(dirname "$0")" && pwd)"
CDIR="$BASEDIR/QEntL/System/Kernel/filesystem"
PASS=0
FAIL=0
declare -a FAILED_FILES=()

for f in "$CDIR"/*.qbc; do
    name=$(basename "$f")
    output=$(./bin/qvm_boot "$f" 2>&1)
    rc=$?
    # 判定标准：exit code 0 且输出包含 "执行完成" 或 "程序退出"
    if [ $rc -eq 0 ] && echo "$output" | grep -qE "(执行完成|程序退出|STOP)"; then
        echo "✅ PASS: $name"
        PASS=$((PASS + 1))
    else
        echo "❌ FAIL: $name (rc=$rc)"
        echo "   OUTPUT: $(echo "$output" | tr '\n' ' ' | head -c 500)"
        FAIL=$((FAIL + 1))
        FAILED_FILES+=("$name")
    fi
done

TOTAL=$((PASS + FAIL))
echo ""
echo "========== QDFS QVM 验证测试报告 =========="
echo "总模块数: $TOTAL"
echo "通过: $PASS"
echo "失败: $FAIL"
echo "通过率: $(( PASS * 100 / TOTAL ))%"
echo ""
if [ $FAIL -gt 0 ]; then
    echo "===== 失败详情 ====="
    for f in "${FAILED_FILES[@]}"; do
        echo "--- $f ---"
        ./bin/qvm_boot "$CDIR/$f" 2>&1 | head -20
        echo ""
    done
fi
echo "=========================================="
