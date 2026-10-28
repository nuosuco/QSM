#!/bin/bash
# ============================================================================
# train_variants_B2.sh - B侧变体训练续训 b33-b41 (4态×10epoch)
# 补 b33-b38 切分缺失(原0字节), b41 仅27类
# 串行: 内存铁律 单进程<2GB
# ============================================================================
set -u
cd /root/QSM/QLife || exit 1
LOG=/tmp/train_variants_B2.log
echo "=== B侧续训 b33-b41 $(date '+%m-%d %H:%M') ===" > "$LOG"

for B in $(seq 33 41); do
  if [ ! -s "qdfs/ns/data/variant_b${B}.comma.data" ]; then
    echo "  b$B 无数据,跳过" >> "$LOG"
    continue
  fi
  for S in 0 1 2 3; do
    echo "  [B2] b${B} s${S} $(date '+%H:%M')" >> "$LOG"
    bash qdfs/ns/train/build_run_var.sh 0 "$B" "$S" 10 >> "$LOG" 2>&1
    rc=$?
    if [ $rc -eq 0 ]; then
      ep9=$(grep -E "ep9: 正确" run/train_var_b${B}_s${S}.log 2>/dev/null | tail -1)
      echo "  [B2] b${B} s${S} OK ${ep9}" >> "$LOG"
    else
      echo "  [B2] b${B} s${S} FAIL rc=$rc" >> "$LOG"
    fi
  done
done
echo "=== B2侧完成 $(date '+%m-%d %H:%M') ===" >> "$LOG"
echo "B2侧完成"
