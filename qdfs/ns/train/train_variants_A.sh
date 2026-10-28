#!/bin/bash
# ============================================================================
# train_variants_A.sh - A侧变体训练 b0-b15 (4态×10epoch)
# 权重流: qdfs/ns/models/variant_b{B}_s{S}_stream.w
# ============================================================================
set -u
cd /root/QSM/QLife || exit 1
LOG=/tmp/train_variants_A.log
echo "=== A侧变体训练 b0-b15 $(date '+%H:%M') ===" > "$LOG"

for B in $(seq 0 15); do
  if [ ! -s "qdfs/ns/data/variant_b${B}.comma.data" ]; then
    echo "  b$B 无数据,跳过" >> "$LOG"
    continue
  fi
  for S in 0 1 2 3; do
    echo "  [A] b${B} s${S} $(date '+%H:%M')" >> "$LOG"
    bash qdfs/ns/train/build_run_var.sh 0 "$B" "$S" 10 >> "$LOG" 2>&1
    rc=$?
    if [ $rc -eq 0 ]; then
      ep9=$(grep -E "ep9: 正确" run/train_var_b${B}_s${S}.log 2>/dev/null | tail -1)
      echo "  [A] b${B} s${S} OK ${ep9}" >> "$LOG"
    else
      echo "  [A] b${B} s${S} FAIL rc=$rc" >> "$LOG"
    fi
  done
done
echo "=== A侧完成 $(date '+%H:%M') ===" >> "$LOG"
echo "A侧完成"
