#!/bin/bash
# 干净重建双态: 杀掉所有旧loop+qvm_boot, 编两版target.qbc, 起两个loop
cd /root/QSM/QLife
pkill -f 'run_superposition' 2>/dev/null
pkill -f 'while true; do ../bin' 2>/dev/null
pkill -f 'qvm_boot run qvm.qbc' 2>/dev/null
sleep 3
# 编两版
sed -e 's/^var g_port = 9802/var g_port = 9802/' -e 's/^var g_statoff = 0/var g_statoff = 0/' build/server_v15.qentl > input.qentl
bin/qvm_boot run run/qcl.qbc >/dev/null 2>&1; cp output.qbc .state_a/target.qbc
sed -e 's/^var g_port = 9802/var g_port = 9803/' -e 's/^var g_statoff = 0/var g_statoff = 2/' build/server_v15.qentl > input.qentl
bin/qvm_boot run run/qcl.qbc >/dev/null 2>&1; cp output.qbc .state_b/target.qbc
echo "编译完成 $(date +%H:%M)"
# 起态A loop
( cd .state_a && while true; do ../bin/qvm_boot run qvm.qbc >> /tmp/state_a_9802.log 2>&1; sleep 2; done ) &
# 起态B loop
( cd .state_b && while true; do ../bin/qvm_boot run qvm.qbc >> /tmp/state_b_9803.log 2>&1; sleep 2; done ) &
echo "双态loop已启动"
sleep 15
for p in 9802 9803; do
  PID=$(ss -ltnp 2>/dev/null | grep ":$p "|grep -oP 'pid=\K[0-9]+'|head -1)
  [ -n "$PID" ] && echo "$p pid=$PID $(ps -o lstart= -p $PID 2>/dev/null|awk '{print $3,$4}') RSS=$(ps -o rss= -p $PID 2>/dev/null|awk '{printf %.0f,$1/1024}')MB" || echo "$p 监听中"
done
