#!/bin/bash
# train_5316_fast.sh - 快速训练驱动 (跳过重复编译 qcl/qvm, 只改控制文件直接跑)
# A轮: seed=1+s*100, stream 存 stream.w
# B轮: seed=10001+s*100, stream 存 streamB.w
# 用法: bash train_5316_fast.sh [A|B]
set -u
cd /root/QSM/QLife || exit 1

ROUND="${1:-A}"
EPOCH=6
BATCHES="0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41"
STATES="0 1 2 3"
SRC=qdfs/ns/train/qscl_32x32_v10.qentl

if [ "$ROUND" = "B" ]; then
  SEED_EXPR="g_seed = 10001 + g_s * 100"
  SUFFIX="streamB"
else
  SEED_EXPR="g_seed = 1 + g_s * 100"
  SUFFIX="stream"
fi

echo "===== $ROUND 轮开始 $(date '+%m-%d %H:%M:%S') (epoch=$EPOCH) =====" > /tmp/train_5316_${ROUND}.log

# 备份 v10 源码
cp "$SRC" /tmp/v10_orig.qentl

for B in $BATCHES; do
  for S in $STATES; do
    echo "[$ROUND] b${B}_s${S} $(date '+%H:%M:%S')" | tee -a /tmp/train_5316_${ROUND}.log
    # 控制文件
    echo "$B" > qdfs/ns/train/current_batch.txt
    echo "$S" > qdfs/ns/train/current_state.txt
    echo "0" > qdfs/ns/train/smoke_limit.txt
    # epoch + seed
    sed -i "s|^var g_epoch = [0-9]*.*|var g_epoch = $EPOCH|" "$SRC"
    sed -i "s|g_seed = [0-9]+ g_s \* [0-9]*|$SEED_EXPR|" "$SRC"
    # 编译 v10
    cp "$SRC" input.qentl
    bin/qvm_boot run run/qcl.qbc > /dev/null 2>&1
    cp output.qbc target.qbc
    # 跑
    rm -f "qdfs/ns/models/qscl_32x32_b${B}_s${S}_stream.w"
    rm -f "qdfs/ns/models/qscl_32x32_b${B}_s${S}_streamB.w"
    bin/qvm_boot run run/qvm.qbc > "run/qvm_b${B}_s${S}.all" 2> "run/qvm_b${B}_s${S}.time"
    # 分流: 哨兵"=== 日志截断 ==="之后是权重流
    LOG="run/train_b${B}_s${S}.log"
    STREAM="qdfs/ns/models/qscl_32x32_b${B}_s${S}_${SUFFIX}.w"
    awk -v logf="$LOG" 'BEGIN{p=0} /=== 日志截断 ===/{p=1;next} p{print; next} {print > logf}' "run/qvm_b${B}_s${S}.all" > "$STREAM"
    SZ=$(wc -c < "$STREAM" 2>/dev/null || echo 0)
    ACC=$(grep -oE "正确[0-9]+/[0-9]+" "$LOG" 2>/dev/null | tail -1)
    echo "  -> ${B}_s${S}_${SUFFIX}=$SZ  $ACC" | tee -a /tmp/train_5316_${ROUND}.log
  done
done

# 恢复 v10
cp /tmp/v10_orig.qentl "$SRC"
echo "===== $ROUND 轮完成 $(date '+%m-%d %H:%M:%S') =====" | tee -a /tmp/train_5316_${ROUND}.log
