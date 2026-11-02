#!/bin/bash
# 干净重建双态: 先杀所有qvm_boot+循环, 再编两版target.qbc, 再起一对进程
cd /root/QSM/QLife
# 杀所有循环和qvm_boot
pkill -f 'run_superposition' 2>/dev/null
sleep 1
pkill -f 'qvm_boot run qvm.qbc' 2>/dev/null
sleep 2
# 编译两版
sed -e 's/^var g_port = 9802/var g_port = 9802/' -e 's/^var g_statoff = 0/var g_statoff = 0/' build/server_v15.qentl > input.qentl
bin/qvm_boot run run/qcl.qbc >/dev/null 2>&1
cp output.qbc .state_a/target.qbc
sed -e 's/^var g_port = 9802/var g_port = 9803/' -e 's/^var g_statoff = 0/var g_statoff = 2/' build/server_v15.qentl > input.qentl
bin/qvm_boot run run/qcl.qbc >/dev/null 2>&1
cp output.qbc .state_b/target.qbc
echo "编译完成 20:$(date +%M)"
# 起态A
cd .state_a && nohup ../bin/qvm_boot run qvm.qbc > /tmp/state_a_9802.log 2>&1 &
cd /root/QSM/QLife
# 起态B
cd .state_b && nohup ../bin/qvm_boot run qvm.qbc > /tmp/state_b_9803.log 2>&1 &
cd /root/QSM/QLife
echo "双态进程已启动"
