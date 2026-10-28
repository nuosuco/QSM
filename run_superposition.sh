#!/bin/bash
# 叠加态并行: 2个独立识别进程 (态A=9802, 态B=9803), 各态独立内存池1.6GB, 总3.2GB<3.5GB红线
# 原理: qvm.qbc 内部写死加载 ./target.qbc + 相对路径 qdfs/ns/..., 所以两态必须各自独立目录
#   态A: .state_a/target.qbc = server_v15(9802)
#   态B: .state_b/target.qbc = server_9803(9803, sed改过端口)
#   两态都软链 qdfs + bin, 权重文件共享 (只读, 不冲突)
cd /root/QSM/QLife || exit 1
BASE=/root/QSM/QLife
STATE_A=$BASE/.state_a
STATE_B=$BASE/.state_b
LOG_A=/tmp/state_a_9802.log
LOG_B=/tmp/state_b_9803.log

# 预编译两版 target.qbc (态A=9802, 态B=9803)
make_target() {
  local PORT=$1 OUT=$2
  sed "s/var g_port = 9802/var g_port = $PORT/" $BASE/build/server_v15.qentl > $BASE/input.qentl
  (cd $BASE && bin/qvm_boot run run/qcl.qbc > /dev/null 2>&1 && cp output.qbc $OUT)
  echo "  编译 port=$PORT -> $OUT ($(stat -c%s $OUT 2>/dev/null)字节)"
}
echo "=== 编译两版 target.qbc ==="
mkdir -p $STATE_A $STATE_B
make_target 9802 $STATE_A/target.qbc
make_target 9803 $STATE_B/target.qbc

# 各态独立目录: 软链 qdfs(权重) + bin(qvm_boot) + qvm.qbc(运行时)
ln -sfn $BASE/qdfs $STATE_A/qdfs
ln -sfn $BASE/bin $STATE_A/bin
cp $BASE/run/qvm.qbc $STATE_A/qvm.qbc
ln -sfn $BASE/qdfs $STATE_B/qdfs
ln -sfn $BASE/bin $STATE_B/bin
cp $BASE/run/qvm.qbc $STATE_B/qvm.qbc

# 态A循环 (9802)
while true; do
  cd $STATE_A || exit 1
  bin/qvm_boot run qvm.qbc >> $LOG_A 2>&1
  echo "[$(date '+%H:%M:%S')] 态A退出, 重启" >> $LOG_A
  for i in 1 2 3 4 5 6 7 8 9 10; do
    if ss -ltn 2>/dev/null | grep -q ':9802 '; then
      echo "[$(date '+%H:%M:%S')] 态A 9802 已就绪" >> $LOG_A
      break
    fi
    sleep 1
  done
done &
A_PID=$!

# 态B循环 (9803)
while true; do
  cd $STATE_B || exit 1
  bin/qvm_boot run qvm.qbc >> $LOG_B 2>&1
  echo "[$(date '+%H:%M:%S')] 态B退出, 重启" >> $LOG_B
  for i in 1 2 3 4 5 6 7 8 9 10; do
    if ss -ltn 2>/dev/null | grep -q ':9803 '; then
      echo "[$(date '+%H:%M:%S')] 态B 9803 已就绪" >> $LOG_B
      break
    fi
    sleep 1
  done
done &
B_PID=$!

echo "叠加态并行启动: 态A(9802, pid=$A_PID) 态B(9803, pid=$B_PID)"
echo "日志: $LOG_A / $LOG_B"
wait $A_PID $B_PID
