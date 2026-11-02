#!/bin/bash
# 干净重建: 态A/态B 各走独立loop, 识别后自动重启
cd /root/QSM/QLife
# 杀所有qvm_boot + 旧loop
pkill -f 'qvm_boot' 2>/dev/null
pkill -f 'run_server_loop' 2>/dev/null
sleep 3
# 起态A loop
nohup bash -c 'cd /root/QSM/QLife/.state_a && while true; do ../bin/qvm_boot run qvm.qbc >> /tmp/state_a_9802.log 2>&1; sleep 2; done' > /dev/null 2>&1 &
# 起态B loop
nohup bash -c 'cd /root/QSM/QLife/.state_b && while true; do ../bin/qvm_boot run qvm.qbc >> /tmp/state_b_9803.log 2>&1; sleep 2; done' > /dev/null 2>&1 &
echo "双态loop已启动"
sleep 15
for p in 9802 9803; do PID=$(ss -ltnp 2>/dev/null | grep ":$p "|grep -oP 'pid=\K[0-9]+'|head -1); [ -n "$PID" ] && echo "$p pid=$PID" || echo "$p 监听中"; done
