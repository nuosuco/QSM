#!/bin/bash
# 50样本识别率实测: 类0~4900每100类, 走双态新4态投票
# 0~999走9802(态0/1), >=1000走9803(态2/3); 每样本前等服务真正监听避重启窗
cd /root/QSM/QLife
DATA=qdfs/ns/data/yi_glyph_5316_32x32.comma.data
OUT=/tmp/recog_rate_v28.txt
: > "$OUT"
LOG=/tmp/recog_rate_v28.log
echo "=== 50样本识别率 $(date '+%H:%M') ===" > "$LOG"
for C in $(seq 0 49); do
  CLS=$((C*100))
  PX=$(awk -F: -v n=$((CLS+1)) 'NR==n{print $2}' "$DATA")
  [ -z "$PX" ] && { echo "类$CLS: 无像素数据 跳过" >> "$LOG"; continue; }
  if [ $CLS -le 999 ]; then PORT=9802; else PORT=9803; fi
  # 等服务真正监听(避重启窗)
  for w in 1 2 3 4 5 6 7 8 9 10; do
    ss -ltn 2>/dev/null | grep -q ":$PORT " && break
    sleep 1
  done
  T0=$(date +%s)
  R=$(curl -s -m 260 -X POST -H "Content-Type: text/plain" -d "$PX" http://localhost:$PORT/api/yi32 2>&1)
  EL=$(( $(date +%s) - T0 ))
  GOT=$(echo "$R" | grep -oE 'class=[0-9]+' | head -1 | cut -d= -f2)
  FLAG=""
  if [ "$GOT" = "$CLS" ]; then FLAG="对"; else FLAG="错(认成$GOT)"; fi
  # 提取投票行
  VOTE=$(echo "$R" | grep -oE '2态并行投票.*' | head -1)
  echo "类$CLS [$PORT] 答=$GOT $FLAG 耗时${EL}s | $VOTE" >> "$LOG"
done
echo "=== 完成 $(date '+%H:%M') ===" >> "$LOG"
# 汇总
OK=$(grep -c ' 对 ' "$LOG"); BAD=$(grep -c ' 错(' "$LOG")
echo "识别率: 对=$OK 错=$BAD (样本见 $LOG)"
