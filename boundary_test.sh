#!/bin/bash
# 新分界实测: 4233/4234 边界 + 4200(有像素) + 5000(标点)
cd /root/QSM/QLife
DATA=qdfs/ns/data/yi_glyph_5316_32x32.comma.data
: > /tmp/boundary_test.log
for C in 4200 4233 4234 4300 5000; do
  PX=$(awk -F: -v n=$((C+1)) 'NR==n{print $2}' "$DATA")
  NL=$(echo "$PX" | tr ',' '\n' | grep -c '^1$')
  # 等9803监听(避重启窗)
  for w in 1 2 3 4 5 6 7 8 9 10; do ss -ltn 2>/dev/null | grep -q ':9803 ' && break; sleep 1; done
  T0=$(date +%s)
  R=$(curl -s -m 290 -X POST -H "Content-Type: text/plain" -d "$PX" http://localhost:9803/api/yi32 2>&1)
  EL=$(( $(date +%s) - T0 ))
  GOT=$(echo "$R" | grep -oE 'class=[0-9]+' | head -1 | cut -d= -f2)
  CP=$(echo "$R" | grep -oE 'codepoint=[0-9]+' | head -1 | cut -d= -f2)
  VOTE=$(echo "$R" | grep -oE '2态并行投票.*' | head -1)
  if [ "$GOT" = "$C" ]; then FLAG="对"; else FLAG="错(认成$GOT)"; fi
  LINE="类$C 亮$NL 答=$GOT $FLAG 码点=$CP 耗时${EL}s | $VOTE"
  echo "$LINE" >> /tmp/boundary_test.log
  echo "$LINE"
done
echo "=== 完成 ===" >> /tmp/boundary_test.log
