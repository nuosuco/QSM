#!/bin/bash
# train_5316_B.sh - B 轮: 42 batch × 4 态 × 10 epoch (seed 10001/10101/10201/10301)
# 用法: bash qdfs/ns/train/train_5316_B.sh
set -u
cd /root/QSM/QLife || exit 1
LOG=/tmp/train_5316_B.log
echo "===== B 轮开始 $(date '+%m-%d %H:%M:%S') =====" > "$LOG"

SRC=qdfs/ns/train/qscl_32x32_v10.qentl
cp "$SRC" /tmp/v10_A_backup.qentl
sed -i 's|g_seed = 1 + g_s \* 100|g_seed = 10001 + g_s * 100|' "$SRC"

BATCHES="31 32 39 40 41"
STATES="0 1 2 3"
EPOCH=10
TOTAL=0

for B in $BATCHES; do
  for S in $STATES; do
    TOTAL=$((TOTAL + 1))
    echo "[B轮] ($TOTAL/168) batch=$B state=$S epoch=$EPOCH $(date '+%H:%M:%S')" | tee -a "$LOG"
    rm -f "qdfs/ns/models/qscl_32x32_b${B}_s${S}_streamB.w"
    if bash qdfs/ns/train/build_run_v10.sh 0 $B $S $EPOCH >> "$LOG" 2>&1; then
      if [ -f "qdfs/ns/models/qscl_32x32_b${B}_s${S}_stream.w" ]; then
        mv "qdfs/ns/models/qscl_32x32_b${B}_s${S}_stream.w" "qdfs/ns/models/qscl_32x32_b${B}_s${S}_streamB.w"
        SZ=$(wc -c < "qdfs/ns/models/qscl_32x32_b${B}_s${S}_streamB.w" 2>/dev/null || echo 0)
        echo "[B轮] b${B}_s${S} streamB.w=${SZ}B $(date '+%H:%M:%S')" | tee -a "$LOG"
      fi
    fi
  done
done

cp /tmp/v10_A_backup.qentl "$SRC"
echo "===== B 轮完成 $(date '+%m-%d %H:%M:%S') =====" >> "$LOG"
