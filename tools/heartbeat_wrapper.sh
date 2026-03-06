#!/bin/bash
# QEntL心跳包装脚本
# 版本: 1.0.0

cd /root/QSM
python3 tools/heartbeat_sender.py >> /tmp/qentl_heartbeat.log 2>&1

# 检查是否成功，如果不成功则使用备用方案
if [ $? -ne 0 ]; then
    echo "$(date): 心跳脚本执行失败" >> /tmp/qentl_heartbeat_errors.log
    # 尝试直接发送简单消息
    echo "⚛️ QEntL进度检查: $(date '+%Y-%m-%d %H:%M') - 开发进行中" > /tmp/qentl_status.txt
fi