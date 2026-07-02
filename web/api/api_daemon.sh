#!/bin/bash
# 四模型API守护脚本 - 自动重启

API_DIR="/var/www/som.top/api"
API_SCRIPT="four_model_api.py"
LOG_FILE="/tmp/four_model_api.log"
PID_FILE="/tmp/four_model_api.pid"

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
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动四模型API..." >> $LOG_FILE
    nohup python3 $API_SCRIPT >> $LOG_FILE 2>&1 &
    echo $! > $PID_FILE
    sleep 2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] API已启动, PID: $(cat $PID_FILE)" >> $LOG_FILE
}

# 停止API
stop_api() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        kill $PID 2>/dev/null
        rm -f $PID_FILE
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] API已停止" >> $LOG_FILE
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
        stop_api
        start_api
        ;;
    status)
        if check_api; then
            echo "API运行中, PID: $(cat $PID_FILE)"
        else
            echo "API未运行"
        fi
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
