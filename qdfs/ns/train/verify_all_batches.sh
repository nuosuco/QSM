#!/bin/bash
# verify_all_batches.sh: 9批全量独立准确率验证 (verify_accuracy.awk, 纯awk)
# 每批: 权重=merged第B行(4态累加), 数据=全量4226, 标签基址=B*515
set -u
cd /root/QSM/QLife || exit 1
M=qdfs/ns/models/qscl4226_merged.w
DATA=qdfs/ns/data/yi_glyph_4226_32x32.data
for B in 0 1 2 3 4 5 6 7 8; do
    awk -v batch=$B -v mode=merged4 -v tag=batch$B -f qdfs/ns/train/verify_accuracy.awk <(sed -n "$((B+1))p" "$M") < "$DATA" 2>&1 | grep -E '正确数|有效样本|准确率|PASS|FAIL' | head -5
done
