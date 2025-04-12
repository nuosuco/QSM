#!/bin/bash
# 自动激活虚拟环境并启动所有必要的后台服务
# 执行方法: source ./activate_env.sh

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_status() {
    echo -e "${GREEN}[STATUS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    print_error "Python3 not found. Please install Python 3.8 or later."
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
fi

# 激活虚拟环境
print_status "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi

# 安装依赖
print_status "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    exit 1
fi

# 启动Ref系统核心
print_status "Starting Ref system core..."
python Ref/ref_core.py &
REF_PID=$!
sleep 2
if ! ps -p $REF_PID > /dev/null; then
    print_error "Failed to start Ref system core"
    exit 1
fi

# 启动量子基因标记器监控
print_status "Starting quantum gene marker monitor..."
python Ref/utils/quantum_gene_marker.py --monitor &
MARKER_PID=$!
sleep 2
if ! ps -p $MARKER_PID > /dev/null; then
    print_error "Failed to start quantum gene marker monitor"
    exit 1
fi

# 启动文件监控系统
print_status "Starting file monitoring system..."
# 获取当前目录的绝对路径
CURRENT_DIR=$(pwd)
python Ref/utils/file_monitor.py --standalone --paths "$CURRENT_DIR" "$CURRENT_DIR/Ref" "$CURRENT_DIR/QEntL" &
FILE_MONITOR_PID=$!
sleep 2
if ! ps -p $FILE_MONITOR_PID > /dev/null; then
    print_warning "Failed to start file monitoring system"
    FILE_MONITOR_PID=""
else
    print_status "File monitoring system started successfully - monitoring file movements and updating quantum entanglement"
fi

# 启动QSM API服务
print_status "Starting QSM API service..."
python QSM/app.py &
QSM_PID=$!
sleep 2
if ! ps -p $QSM_PID > /dev/null; then
    print_error "Failed to start QSM API service"
    exit 1
fi

# 启动QEntL引擎
print_status "Starting QEntL engine..."
python QEntL/engine.py &
QENTL_PID=$!
sleep 2
if ! ps -p $QENTL_PID > /dev/null; then
    print_warning "Failed to start QEntL engine"
fi

# SOM/WeQ/Ref单独服务默认不启动，通过参数控制
ENABLE_SEPARATE_SERVICES=false
for arg in "$@"; do
    if [ "$arg" = "-all" ] || [ "$arg" = "--all-services" ]; then
        ENABLE_SEPARATE_SERVICES=true
        break
    fi
done

if [ "$ENABLE_SEPARATE_SERVICES" = true ]; then
    # 启动SOM服务
    print_status "Starting SOM service..."
    python SOM/app.py &
    SOM_PID=$!
    sleep 2
    if ! ps -p $SOM_PID > /dev/null; then
        print_warning "Failed to start SOM service"
    fi

    # 启动WeQ服务
    print_status "Starting WeQ service..."
    python WeQ/app.py &
    WEQ_SERVICE_PID=$!
    sleep 2
    if ! ps -p $WEQ_SERVICE_PID > /dev/null; then
        print_warning "Failed to start WeQ service"
    fi
    
    # 如果存在Ref/app.py，则启动它
    if [ -f "Ref/app.py" ]; then
        print_status "Starting Ref API service..."
        python Ref/app.py &
        REF_API_PID=$!
        sleep 2
        if ! ps -p $REF_API_PID > /dev/null; then
            print_warning "Failed to start Ref API service"
        fi
    fi
else
    print_status "Separate services not started. Use -all or --all-services flag to start them."
    SOM_PID=""
    WEQ_SERVICE_PID=""
    REF_API_PID=""
fi

# 启动WeQ后台训练(如果存在)
print_status "启动WeQ后台训练系统 (24小时自动学习模式)..."
python WeQ/weq_train.py &
WEQ_PID=$!
sleep 5
if ! ps -p $WEQ_PID > /dev/null; then
    print_warning "WeQ训练系统启动失败"
    WEQ_PID=""
else
    print_status "WeQ训练系统已成功启动，开始24小时学习"
fi

print_status "All services started successfully!"
print_status "Press Ctrl+C to stop all services"

# 等待用户中断
trap 'kill $REF_PID $MARKER_PID $QSM_PID $QENTL_PID $SOM_PID $WEQ_SERVICE_PID $REF_API_PID $WEQ_PID $FILE_MONITOR_PID 2>/dev/null; exit' INT
wait 
#
量子基因编码: QE-ACT-29F7A9B36754
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
