#!/bin/bash
# 全量 5316 训练: 42批 x 4态 (6变体), 每态存权重流
# 单态~8min, 全量~22h, 后台挂
set -u
cd /root/QSM/QLife
LOG=/tmp/train_5316_full.log
echo "===== 5316 全量训练 $(date '+%m-%d %H:%M') =====" > "$LOG"
TOTAL=0
for B in $(seq 0 41); do
  # 空批跳过
  if [ ! -s "qdfs/ns/data/variant_b${B}.comma.data" ]; then
    echo "  b$B: 空批, 跳过" >> "$LOG"
    continue
  fi
  for S in 0 1 2 3; do
    bash qdfs/ns/train/build_run_var.sh 0 "$B" "$S" 10 >> "$LOG" 2>&1
    RC=$?
    STREAM="qdfs/ns/models/variant_b${B}_s${S}_stream.w"
    SZ=$(wc -c < "$STREAM" 2>/dev/null || echo 0)
    echo "  [v6] b$B s$S rc=$RC 权重流=${SZ}字节" >> "$LOG"
    TOTAL=$((TOTAL+1))
  done
done
echo "===== 全量完成 共$TOTAL 态 $(date '+%m-%d %H:%M') =====" >> "$LOG"
# 合并权重
bash qdfs/ns/train/merge_variants.sh >> "$LOG" 2>&1
echo "===== 合并完成 $(date '+%m-%d %H:%M') =====" >> "$LOG"
