#!/bin/bash

echo "==================================="
echo "量子超位态模型（QSM）项目启动脚本"
echo "==================================="

# 设置环境变量
export QSM_ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$QSM_ROOT:$PYTHONPATH"
export QSM_LOG_DIR="$QSM_ROOT/.logs"

# 创建日志目录
mkdir -p "$QSM_LOG_DIR"

echo "正在启动QSM项目..."
echo "日志位置: $QSM_LOG_DIR"

# 检查QEntl环境
if ! command -v qentl &> /dev/null; then
    echo "错误: 未找到QEntl环境，请安装QEntl解释器"
    exit 1
fi

# 获取QEntl版本
QENTL_VERSION=$(qentl --version 2>&1 | awk '{print $2}')
echo "使用 QEntl 版本: $QENTL_VERSION"

# 启动主程序
echo "正在启动量子超位态模型主程序..."
qentl "$QSM_ROOT/run.qpy" &

# 存储PID
echo $! > "$QSM_ROOT/.qsm.pid"

echo ""
echo "QSM项目已启动！"
echo "您可以通过访问 http://localhost:5999 查看服务状态"
echo "使用 ./stop_project.sh 停止服务" 