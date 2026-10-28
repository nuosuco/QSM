#!/bin/bash
# train_5316_A.sh - A 轮: 11 batch × 4 态 × 10 epoch (seed 1/101/201/301)
# 串行单 QVM (守内存红线: 单进程<2GB)
# 用法: bash qdfs/ns/train/train_5316_A.sh
set -u
cd /root/QSM/QLife || exit 1
LOG=/tmp/train_5316_A.log
echo "===== A 轮开始 $(date '+%m-%d %H:%M:%S') =====" > "$LOG"

BATCHES="0 1 2 3 4 5 6 7 8 9 10"
STATES="0 1 2 3"
EPOCH=10
TOTAL=0

for B in $BATCHES; do
  for S in $STATES; do
    TOTAL=$((TOTAL + 1))
    echo "[A轮] ($TOTAL/44) batch=$B state=$S epoch=$EPOCH $(date '+%H:%M:%S')" | tee -a "$LOG"
    rm -f "qdfs/ns/models/qscl_32x32_b${B}_s${S}_stream.w"
    if bash qdfs/ns/train/build_run_v10.sh 0 $B $S $EPOCH >> "$LOG" 2>&1; then
      SZ=$(wc -c < "qdfs/ns/models/qscl_32x32_b${B}_s${S}_stream.w" 2>/dev/null || echo 0)
      echo "[A轮] b${B}_s${S} stream.w=${SZ}B $(date '+%H:%M:%S')" | tee -a "$LOG"
    else
      echo "[A轮] !!! b${B}_s${S} 训练失败, 继续 $(date '+%H:%M:%S')" | tee -a "$LOG"
    fi
  done
done
echo "===== A 轮完成 $(date '+%m-%d %H:%M:%S') =====" | tee -a "$LOG"
