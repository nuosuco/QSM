#!/bin/bash
set -u
cd /root/QSM/QLife
SRC=qdfs/ns/data/yi_glyph_4541_32x32_variant_v6.comma.data
OUT=qdfs/ns/data/variant_4541
rm -rf "$OUT"; mkdir -p "$OUT"
# 35 批, 前 34 批各 774 行, 末批 774 行? 27246/35=778.5 → 34批x780=26520+1批x726
TOTAL=$(wc -l < "$SRC")
NB=35
BASE=$((TOTAL / NB))
REM=$((TOTAL % NB))
LINES=0
for ((i=0; i<NB; i++)):
  CNT=$BASE
  if [ $i -lt $REM ]; then CNT=$((CNT+1)); fi
  FN="$OUT/variant_4541_b${i}.comma.data"
  sed -n "$((LINES+1)),$((LINES+CNT))p" "$SRC" > "$FN"
  LINES=$((LINES+CNT))
done
for i in $(seq 0 $((NB-1))); do
  echo "b${i}: $(wc -l < $OUT/variant_4541_b${i}.comma.data) 行"
done
