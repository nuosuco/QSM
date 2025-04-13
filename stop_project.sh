#!/bin/bash

echo "==================================="
echo "量子超位态模型（QSM）项目停止脚本"
echo "==================================="

# 设置环境变量
export QSM_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "正在停止QSM项目..."

# 尝试通过PID文件停止
PID_FILE="$QSM_ROOT/.qsm.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "找到PID文件，PID: $PID"
    
    if ps -p $PID > /dev/null; then
        echo "正在停止QSM进程 (PID: $PID)..."
        kill $PID
        sleep 2
        
        # 如果进程仍然运行，使用强制终止
        if ps -p $PID > /dev/null; then
            echo "进程未响应，强制终止..."
            kill -9 $PID
        fi
        
        echo "进程已终止"
    else
        echo "PID文件中的进程不存在"
    fi
    
    # 删除PID文件
    rm -f "$PID_FILE"
else
    echo "未找到PID文件，尝试查找QSM进程..."
    # 查找并终止所有qentl run.qpy进程
    pkill -f "qentl.*run\.qpy" || echo "未找到运行中的QSM进程"
fi

# 尝试终止所有QSM相关服务
echo "正在终止所有QSM相关服务..."
pkill -f "qentl.*qsm_api\.qpy" || true
pkill -f "qentl.*weq_api\.qpy" || true
pkill -f "qentl.*som_api\.qpy" || true
pkill -f "qentl.*ref_api\.qpy" || true
pkill -f "qentl.*world_server\.qpy" || true

echo ""
echo "QSM项目已停止！" 