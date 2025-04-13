#!/bin/bash
echo "==================================="
echo "QEntl解释器构建脚本 (Linux/macOS)"
echo "==================================="

# 检查是否安装了gcc
if ! command -v gcc &> /dev/null; then
    echo "需要安装gcc编译器"
    echo "在Ubuntu/Debian上: sudo apt install gcc"
    echo "在macOS上: xcode-select --install"
    exit 1
fi

# 创建bin目录
mkdir -p bin

# 编译QEntl解释器
echo "正在编译QEntl解释器..."
gcc -o bin/qentl bin/qentl.c -Wall -O2

if [ $? -ne 0 ]; then
    echo "编译失败"
    exit 1
fi

# 添加可执行权限
chmod +x bin/qentl

echo "编译成功！"
echo "QEntl解释器已构建: bin/qentl"

# 添加到PATH (可选)
echo
read -p "是否将QEntl添加到系统PATH? (y/n): " add_to_path
if [ "$add_to_path" = "y" ] || [ "$add_to_path" = "Y" ]; then
    echo "export PATH=\"$PATH:$(pwd)/bin\"" >> ~/.bashrc
    echo "QEntl已添加到系统PATH (需要重新启动终端)"
fi

echo
echo "可以通过以下命令测试QEntl解释器:"
echo "./bin/qentl --version"
echo 