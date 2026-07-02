#!/bin/bash
# QNS训练监控脚本 - 监控准确率直到>80%
LOG="/root/QSM/models/qns_train_v5.log"
MODEL="/root/QSM/data/qns_model_v5.dat"
LAST_ACC="0"
LAST_LINE=0

while true; do
    # 检查进程是否还在运行
    if ! ps -p 312014 > /dev/null 2>&1; then
        echo "[MONITOR] 训练进程已结束，检查最终状态..."
        break
    fi
    
    # 读取日志最新行数
    LINES=$(wc -l < "$LOG")
    
    # 只处理新行
    if [ "$LINES" -gt "$LAST_LINE" ]; then
        # 查找最新的准确率
        ACC_LINE=$(grep -oP 'Accuracy: \d+/\d+ = [\d.]+ \([\d.]+%?\)' "$LOG" | tail -1)
        if [ -n "$ACC_LINE" ]; then
            ACC=$(echo "$ACC_LINE" | grep -oP '[\d.]+(?=%\)?)' | tail -1)
            # 也尝试提取百分比格式
            ACC_PCT=$(echo "$ACC_LINE" | grep -oP '[\d.]+(?=%\))')
            if [ -n "$ACC_PCT" ]; then
                ACC="$ACC_PCT"
            fi
            if [ "$ACC" != "$LAST_ACC" ]; then
                echo "[MONITOR] 最新准确率: $ACC_LINE"
                LAST_ACC="$ACC"
                
                # 检查是否超过80%
                OVER80=$(echo "$ACC > 80" | bc -l 2>/dev/null)
                if [ "$OVER80" = "1" ]; then
                    echo "[MONITOR] 准确率超过80%！保存模型..."
                    echo "ACCURACY_OVER_80" > /tmp/qns_80_flag
                    break
                fi
            fi
        fi
        
        # 检查训练是否完成
        if grep -q "Training complete" "$LOG" 2>/dev/null || grep -q "DONE" "$LOG" 2>/dev/null; then
            echo "[MONITOR] 训练完成！"
            break
        fi
        
        LAST_LINE=$LINES
    fi
    
    sleep 15
done

# 最终状态
echo "[MONITOR] 监控结束"
echo "FINAL_ACC=$LAST_ACC" > /tmp/qns_monitor_result
echo "FINAL_LINE=$LAST_LINE" >> /tmp/qns_monitor_result
