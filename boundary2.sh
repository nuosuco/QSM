#!/bin/bash
# 边界重测: 4233/4234/4300/5000 (4200已确认认成2709, 跳过)
# 关键: 识别后g_alive=0重启, 每样本前必须等端口重新监听+池就绪
cd /root/QSM/QLife
DATA=qdfs/ns/data/yi_glyph_5316_32x32.comma.data
: > /tmp/boundary2.log
for C in 4233 4234 4300 5000; do
  PX=$(awk -F: -v n=$((C+1)) 'NR==n{print $2}' "$DATA")
  NL=$(echo "$PX" | tr ',' '\n' | grep -c '^1$')
  # 等9803监听(识别后重启需要~5-8秒)
  for w in $(seq 1 15); do ss -ltn 2>/dev/null | grep -q ':9803 ' && break; sleep 1; done
  # 额外等3秒让池加载完
  sleep 3
  T0=$(date +%s)
  R=$(curl -s -m 290 -X POST -H "Content-Type: text/plain" -d "$PX" http://localhost:9803/api/yi32 2>&1)
  EL=$(( $(date +%s) - T0 ))
  GOT=$(echo "$R" | grep -oE 'class=[0-9]+' | head -1 | cut -d= -f2)
  CP=$(echo "$R" | grep -oE 'codepoint=[0-9]+' | head -1 | cut -d= -f2)
  VOTE=$(echo "$R" | grep -oE '2态并行投票.*' | head -1)
  if [ -z "$GOT" ]; then FLAG="空响应(${EL}s)"; else FLAG="答$GOT"; fi
  LINE="类$C 亮$NL $FLAG 码点=$CP ${VOTE}"
  echo "$LINE" >> /tmp/boundary2.log
  echo "$LINE"
  # 识别后等服务重启释放内存
  sleep 5
done
echo "=== 完成 $(date +%H:%M) ===" >> /tmp/boundary2.log
