#!/bin/bash
cd /root/QSM/QLife
PX=$(awk -F: -v n=4201 'NR==n{print $2}' qdfs/ns/data/yi_glyph_5316_32x32.comma.data)
echo "类4200 像素体长度=${#PX}字符 (tcp_recv上限4096)"
echo "亮像素=$(echo "$PX" | tr ',' '\n' | grep -c '^1$')"
