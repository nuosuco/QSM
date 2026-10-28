#!/bin/bash
# ============================================================================
# train_variants_B.sh - B侧变体训练 b16-b32 (4态×10epoch)
# ============================================================================
set -u
cd /root/QSM/QLife || exit 1
LOG=/tmp/train_variants_B.log
echo "=== B侧变体训练 b16-b32 $(date '+%H:%M') ===" > "$LOG"

for B in $(seq 16 32); do
  if [ ! -s "qdfs/ns/data/variant_b${B}.comma.data" ]; then
    echo "  b$B 无数据,跳过" >> "$LOG"
    continue
  fi
  for S in 0 1 2 3; do
    echo "  [B] b${B} s${S} $(date '+%H:%M')" >> "$LOG"
    bash qdfs/ns/train/build_run_var.sh 0 "$B" "$S" 10 >> "$LOG" 2>&1
    rc=$?
    if [ $rc -eq 0 ]; then
      ep9=$(grep -E "ep9: 正确" run/train_var_b${B}_s${S}.log 2>/dev/null | tail -1)
      echo "  [B] b${B} s${S} OK ${ep9}" >> "$LOG"
    else
      echo "  [B] b${B} s${S} FAIL rc=$rc" >> "$LOG"
    fi
  done
done
echo "=== B侧完成 $(date '+%H:%M') ===" >> "$LOG"
echo "B侧完成"
