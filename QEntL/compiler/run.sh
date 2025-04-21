#!/bin/bash
# QEntL编译器Linux/macOS启动脚本

# 设置编译器根目录
QENTL_COMPILER_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "[QEntL Compiler] 启动QEntL编译器..."
echo "[QEntL Compiler] 编译器路径: $QENTL_COMPILER_ROOT"

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "[QEntL Compiler] 错误: 未找到Node.js，请确保已安装Node.js并添加到PATH环境变量"
    exit 1
fi

# 检查编译器启动文件
if [ ! -f "$QENTL_COMPILER_ROOT/run_compiler.qjs" ]; then
    echo "[QEntL Compiler] 错误: 未找到编译器启动文件"
    exit 1
fi

# 设置执行权限
chmod +x "$QENTL_COMPILER_ROOT/run_compiler.qjs"

# 执行编译器
node "$QENTL_COMPILER_ROOT/run_compiler.qjs" "$@"

# 返回编译器退出代码
exit $? 