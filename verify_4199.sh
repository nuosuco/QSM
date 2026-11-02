#!/bin/bash
# 4199上界验证: 4150(像素段,有像素应认出) 4200(类号段,像素不送argmax,走类号编码)
cd /root/QSM/QLife
DATA=qdfs/ns/data/yi_glyph_5316_32x32.comma.data
: > /tmp/verify_4199.log
for C in 4150 4200 4300; do
  PX=$(awk -F: -v n=$((C+1)) 'NR==n{print $2}' "$DATA")
  NL=$(echo "$PX" | tr ',' '\n' | grep -c '^1$')
  for w in $(seq 1 15); do ss -ltn 2>/dev/null | grep -q ':9802 ' && break; sleep 1; done
  sleep 3
  T0=$(date +%s)
  R=$(curl -s -m 290 -X POST -H "Content-Type: text/plain" -d "$PX" http://localhost:9802/api/yi32 2>&1)
  EL=$(( $(date +%s) - T0 ))
  GOT=$(echo "$R" | grep -oE 'class=[0-9]+' | head -1 | cut -d= -f2)
  CP=$(echo "$R" | grep -oE 'codepoint=[0-9]+' | head -1 | cut -d= -f2)
  VOTE=$(echo "$R" | grep -oE '2态并行投票.*' | head -1)
  if [ -z "$GOT" ]; then FLAG="空响应(${EL}s)"; else FLAG="答$GOT"; fi
  echo "类$C 亮$NL $FLAG 码点=$CP ${VOTE}" | tee -a /tmp/verify_4199.log
  sleep 5
done
echo "=== 完成 ==="
