#!/bin/bash
# 4000+段部首像素识别实测: 类4000~4400每50类=9样本
# 修复: 每样本前等对应端口真正监听(避重启空窗), 失败重试1次
cd /root/QSM/QLife
DATA=qdfs/ns/data/yi_glyph_5316_32x32.comma.data
LOG=/tmp/recog_4000.log
: > "$LOG"
echo "=== 4000+段 $(date '+%H:%M') ===" > "$LOG"
for C in 4000 4050 4100 4150 4200 4250 4300 4350 4400; do
  PX=$(awk -F: -v n=$((C+1)) 'NR==n{print $2}' "$DATA")
  [ -z "$PX" ] && { echo "类$C: 无像素数据 跳过" >> "$LOG"; continue; }
  PORT=9803
  # 等监听
  for w in 1 2 3 4 5 6 7 8 9 10 11 12; do
    ss -ltn 2>/dev/null | grep -q ":$PORT " && break
    sleep 1
  done
  T0=$(date +%s)
  R=$(curl -s -m 280 -X POST -H "Content-Type: text/plain" -d "$PX" http://localhost:$PORT/api/yi32 2>&1)
  EL=$(( $(date +%s) - T0 ))
  GOT=$(echo "$R" | grep -oE 'class=[0-9]+' | head -1 | cut -d= -f2)
  VOTE=$(echo "$R" | grep -oE '2态并行投票.*' | head -1)
  if [ $EL -lt 10 ] || [ -z "$GOT" ]; then
    # 撞重启窗, 重试1次
    for w in 1 2 3 4 5 6; do ss -ltn 2>/dev/null | grep -q ":$PORT " && break; sleep 1; done
    sleep 3
    T0=$(date +%s)
    R=$(curl -s -m 280 -X POST -H "Content-Type: text/plain" -d "$PX" http://localhost:$PORT/api/yi32 2>&1)
    EL=$(( $(date +%s) - T0 ))
    GOT=$(echo "$R" | grep -oE 'class=[0-9]+' | head -1 | cut -d= -f2)
    VOTE=$(echo "$R" | grep -oE '2态并行投票.*' | head -1)
  fi
  if [ "$GOT" = "$C" ]; then FLAG="对"; else FLAG="错(认成$GOT)"; fi
  echo "类$C 答=$GOT $FLAG 耗时${EL}s | $VOTE" >> "$LOG"
done
OK=$(grep -c ' 对 ' "$LOG"); BAD=$(grep -c ' 错(' "$LOG"); EMPTY=$(grep -c '认成$' "$LOG" 2>/dev/null || echo 0)
echo "4000+段识别率: 对=$OK 错=$BAD 总=$((OK+BAD))"
