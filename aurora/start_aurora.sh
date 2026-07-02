#!/bin/bash
# Aurora Engine 启动脚本 - QEntL全栈版本
# 不依赖Python，纯QEntL构建

echo "============================================="
echo "  Aurora Engine 启动器 (QEntL全栈)"
echo "============================================="
echo ""

QSM_DIR="/root/QSM"
BIN="$QSM_DIR/bin"

# 检查QEntL编译器
if [ ! -f "$BIN/qentl_compiler" ]; then
    echo "❌ QEntL编译器不存在，先编译..."
    cd "$QSM_DIR" && make phase3 2>&1
fi

# 检查Aurora QEntL文件
AURORA_QENTL="$QSM_DIR/aurora/aurora_engine.qentl"
if [ ! -f "$AURORA_QENTL" ]; then
    echo "❌ Aurora引擎文件不存在: $AURORA_QENTL"
    exit 1
fi

echo "✅ QEntL编译器: $BIN/qentl_compiler"
echo "✅ Aurora引擎: $AURORA_QENTL"
echo ""

# 七步循环配置
echo "📋 七步循环配置:"
echo "  1. 学习 - 研究QEntL新知识"
echo "  2. 构架 - 完善QEntL架构设计"
echo "  3. 训练 - 监控/启动彝文训练"
echo "  4. 测试 - 验证模型/API状态"
echo "  5. 改进 - 根据测试结果修正"
echo "  6. 总结 - 生成周期总结"
echo "  7. 记忆 - 更新记忆文件"
echo ""

# 启动Aurora引擎
echo "🚀 启动Aurora Engine..."
echo "============================================="

# 执行Aurora引擎 (通过QEntL编译器)
$BIN/qentl_compiler "$AURORA_QENTL" "$BIN/aurora.qbc" 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Aurora引擎编译成功"
    echo "📦 字节码: $BIN/aurora.qbc"
else
    echo "⚠️  Aurora引擎编译失败 (QEntL语法可能需要调整)"
    echo "   使用Python备用引擎..."
    python3 "$QSM_DIR/aurora/engine.py" &
    echo "   Python引擎已在后台运行 (PID: $!)"
fi

echo ""
echo "============================================="
echo "  Aurora Engine 就绪"
echo "============================================="
echo ""
echo "💡 提示: 当前QEntL引擎处于设计阶段，"
echo "   实际运行需要QVM执行环境。"
echo "   建议先用Python版本维持后台调度。"
echo ""
