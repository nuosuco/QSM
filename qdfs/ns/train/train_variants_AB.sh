#!/bin/bash
# AB两侧变体训练: A侧 b0-b15, B侧 b16-b32
# 每批6变体, 每批10epoch, 4态并行(单QVM串行态)
# A侧 seed=1+g_s*100, B侧 seed=20001+g_s*100
set -u
cd /root/QSM/QLife

# A侧批次: 0-15
# B侧批次: 16-32
SID=1
A_BATCHES="0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"
B_BATCHES="16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32"

echo "=== A侧启动: b0-b15 $(date '+%H:%M') ==="
for B in $A_BATCHES; do
  for GS in 0 1 2 3; do
    g_base=$((B*129))
    # 变体批次文件
    DATA_FILE="qdfs/ns/data/variant_b$B.comma.data"
    if [ ! -s "$DATA_FILE" ]; then continue; fi
    SEED=$((1 + GS*100 + B))
    echo "  [A] b$B state$GS seed=$SEED"
    bash qdfs/ns/train/build_run_v10.sh \
      --batch "$B" --gstate "$GS" --seed "$SEED" \
      --data "$DATA_FILE" \
      --out "qdfs/ns/models/variant_${B}_s${GS}.w" \
      2>&1 | grep -E "exit|准确率|error|fail" || true
  done
done
echo "=== A侧完成 $(date '+%H:%M') ==="

echo "=== B侧启动: b16-b32 $(date '+%H:%M') ==="
for B in $B_BATCHES; do
  for GS in 0 1 2 3; do
    DATA_FILE="qdfs/ns/data/variant_b$B.comma.data"
    if [ ! -s "$DATA_FILE" ]; then continue; fi
    SEED=$((20001 + GS*100 + B))
    echo "  [B] b$B state$GS seed=$SEED"
    bash qdfs/ns/train/build_run_v10.sh \
      --batch "$B" --gstate "$GS" --seed "$SEED" \
      --data "$DATA_FILE" \
      --out "qdfs/ns/models/variant_${B}_s${GS}.w" \
      2>&1 | grep -E "exit|准确率|error|fail" || true
  done
done
echo "=== B侧完成 $(date '+%H:%M') ==="
