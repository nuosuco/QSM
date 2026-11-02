#!/bin/bash
# 杀掉全部qvm_boot+loop, 只保留手动一对
cd /root/QSM/QLife
for pid in $(ps -eo pid,cmd | grep 'qvm_boot run qvm.qbc' | grep -v grep | awk '{print $1}'); do
  kill "$pid" 2>/dev/null
done
sleep 4
# 杀掉loop壳(它们的qvm_boot已被杀, 会再拉起新的)
pkill -f 'while true; do ../bin/qvm_boot' 2>/dev/null
sleep 2
echo "=== 剩余qvm_boot ==="
ps -eo pid,cmd | grep 'qvm_boot run qvm.qbc' | grep -v grep || echo "无"
