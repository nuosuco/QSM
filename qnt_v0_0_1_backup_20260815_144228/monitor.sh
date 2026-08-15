#!/bin/bash
# QNT量子交易系统 - 定时监控脚本

while true; do
    echo "===== $(date '+%Y-%m-%d %H:%M:%S') =====" >> /root/SOM/qnt/scan.log
    cd /root/SOM/qnt && python3 main.py scan >> /root/SOM/qnt/scan.log 2>&1
    echo "" >> /root/SOM/qnt/scan.log
    sleep 3600  # 每小时扫描一次
done
