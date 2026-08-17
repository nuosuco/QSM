#!/bin/bash
# QNT 一键启动脚本

set -e

cd "$(dirname "$0")"

echo "🚀 启动 QNT 量子叠加态基础设施..."
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
pip3 install -q flask flask-cors pytest numpy 2>/dev/null || pip3 install flask flask-cors pytest numpy

# 运行测试
echo "🧪 运行测试..."
python3 -m pytest tests/ -q
if [ $? -ne 0 ]; then
    echo "❌ 测试失败，启动中止"
    exit 1
fi
echo "✅ 测试通过"

# 启动API服务
echo "🌐 启动API服务 (http://localhost:5000)..."
python3 api/app.py &
API_PID=$!

echo ""
echo "✅ QNT 启动成功!"
echo "   API: http://localhost:5000/api/health"
echo "   PID: $API_PID"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待进程
wait $API_PID
