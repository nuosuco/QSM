#!/bin/bash
# QNT 快速启动脚本
set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "   QNT Quantum Superposition Network"
echo "=========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

echo "🐍 Python: $(python3 --version)"
echo ""

# 检查依赖
echo "📦 Checking dependencies..."
pip3 install -q flask flask-cors uvicorn pytest numpy 2>/dev/null
echo "✅ Dependencies OK"
echo ""

# 创建目录
mkdir -p data logs backups
echo "📂 Directories ready"
echo ""

# 运行测试
echo "🧪 Running tests..."
python3 -m pytest tests/ -q 2>&1 | tail -3
echo ""

# 启动选项
echo "🚀 Startup options:"
echo "  1. Start API server only"
echo "  2. Start full system (API + Market Feed)"
echo "  3. Run CLI demo"
echo "  4. Exit"
echo ""

read -p "Select option [1-4]: " choice

case $choice in
    1)
        echo "🌐 Starting API server on http://0.0.0.0:5000"
        python3 -c "from api.app import app; app.run(host='0.0.0.0', port=5000, debug=False)"
        ;;
    2)
        echo "🌐 Starting full QNT system..."
        python3 main.py --host 0.0.0.0 --port 5000
        ;;
    3)
        echo "🔧 Running CLI demo..."
        python3 cli.py blockchain --action mine
        python3 cli.py exchange --action order --account Alice --side buy --quantity 10 --price 100
        python3 cli.py nstate --action train --rounds 50
        ;;
    *)
        echo "👋 Goodbye!"
        ;;
esac
