#!/bin/bash
# QEntL Web桌面量子助手API守护脚本 - 自动重启
# 运行在QVM量子虚拟机上

API_DIR="/root/QSM/web/api"
API_SCRIPT="quantum_assistant_api.py"
LOG_FILE="/tmp/qentl_quantum_assistant_api.log"
PID_FILE="/tmp/qentl_quantum_assistant_api.pid"
PORT=8081

cd $API_DIR

# 检查API是否运行
check_api() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            return 0  # 运行中
        fi
    fi
    return 1  # 未运行
}

# 启动API
start_api() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动QEntL Web桌面量子助手API..." >> $LOG_FILE
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 架构: C语言启动器 → QVM → QEntL编译器 → QDFS → QNS → 四大模型" >> $LOG_FILE
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 运行在QVM量子虚拟机上" >> $LOG_FILE
    
    nohup python3 $API_SCRIPT >> $LOG_FILE 2>&1 &
    echo $! > $PID_FILE
    sleep 2
    
    if ps -p $(cat $PID_FILE) > /dev/null 2>&1; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] API已启动, PID: $(cat $PID_FILE)" >> $LOG_FILE
        echo "API已启动, PID: $(cat $PID_FILE)"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] API启动失败" >> $LOG_FILE
        echo "API启动失败"
        rm -f $PID_FILE
    fi
}

# 停止API
stop_api() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        kill $PID 2>/dev/null
        rm -f $PID_FILE
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] API已停止" >> $LOG_FILE
        echo "API已停止"
    else
        echo "API未运行"
    fi
}

# 重启API
restart_api() {
    stop_api
    sleep 1
    start_api
}

# 查看状态
status_api() {
    if check_api; then
        PID=$(cat $PID_FILE)
        echo "API运行中, PID: $PID"
        echo "端口: $PORT"
        echo "架构: C语言启动器 → QVM → QEntL编译器 → QDFS → QNS → 四大模型"
        echo "运行在QVM量子虚拟机上"
    else
        echo "API未运行"
    fi
}

# 主循环
case "$1" in
    start)
        if check_api; then
            echo "API已在运行"
        else
            start_api
        fi
        ;;
    stop)
        stop_api
        ;;
    restart)
        restart_api
        ;;
    status)
        status_api
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        echo "QEntL Web桌面量子助手API - 运行在QVM量子虚拟机上"
        exit 1
        ;;
esac
