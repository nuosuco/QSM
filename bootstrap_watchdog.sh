#!/bin/bash
# 自举生长监控脚本
# 每30分钟检测一次自举链是否健康
set -e
cd /root/QSM
LOG=".bootstrap_watchdog.log"
DATE=$(date "+%Y-%m-%d %H:%M:%S")

echo "[$DATE] === 自举生长检测 ===" >> "$LOG"

# 1. 检测文件完整性
if [ ! -f "run/qcl.qbc" ] || [ ! -f "run/qvm.qbc" ] || [ ! -f "bin/q_bootstrap" ]; then
    echo "[$DATE] ❌ 核心文件缺失!" >> "$LOG"
    exit 1
fi
echo "[$DATE] ✅ 核心文件完整" >> "$LOG"

# 2. 检测自举链 - QCL编译自身
cp run/qcl.qbc target.qbc 2>/dev/null
cp components/qcl/qcl.qentl input.qentl 2>/dev/null
rm -f output.qbc
timeout 300 bin/q_bootstrap run run/qvm.qbc 2>/dev/null | grep -q "errors=0"
if [ $? -eq 0 ] && [ -f "output.qbc" ]; then
    echo "[$DATE] ✅ QCL自举链正常 (output.qbc: $(stat -c%s output.qbc 2>/dev/null)字节)" >> "$LOG"
else
    echo "[$DATE] ❌ QCL自举链异常!" >> "$LOG"
fi

# 3. 检测版本状态
if [ -f ".current_version" ]; then
    VER=$(cat .current_version)
    echo "[$DATE] 当前版本: v${VER}" >> "$LOG"
fi

# 4. 检测组件数量
COMP_COUNT=$(find components -name "*.qentl" | wc -l)
QBC_COUNT=$(find components -name "*.qbc" | wc -l)
echo "[$DATE] 组件: ${COMP_COUNT}个源码, ${QBC_COUNT}个产物" >> "$LOG"

# 清理
rm -f target.qbc input.qentl output.qbc

# 输出最后几行
echo ""
echo "=== 自举生长检测 [$(date "+%H:%M")] ==="
tail -5 "$LOG"
