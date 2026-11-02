#!/bin/bash
# 精确复测: 类4200(有像素) 走像素识别, 全量抓响应
cd /root/QSM/QLife
DATA=qdfs/ns/data/yi_glyph_5316_32x32.comma.data
PX=$(awk -F: -v n=4201 'NR==n{print $2}' "$DATA")
NL=$(echo "$PX" | tr ',' '\n' | grep -c '^1$')
echo "类4200 主表亮像素=$NL"
for w in 1 2 3 4 5 6 7 8; do ss -ltn 2>/dev/null | grep -q ':9803 ' && break; sleep 1; done
T0=$(date +%s)
R=$(curl -s -m 290 -X POST -H "Content-Type: text/plain" -d "$PX" http://localhost:9803/api/yi32 2>&1)
EL=$(( $(date +%s) - T0 ))
echo "响应(${EL}s): $R"
