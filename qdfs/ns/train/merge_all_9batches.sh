#!/bin/bash
# merge_all_9batches.sh: 9批×4态 stream.w → 提取 → 每批4态累加坍缩 → 9批拼接 = 最终权重
# 坍缩定义(v7b): 4态直接累加, 不归一
set -u
cd /root/QSM/QLife || exit 1
D=qdfs/ns/models
OUT=$D/qscl4226_merged.w
TMP=/tmp/merged_batch_tmp.w
> "$OUT"
for B in 0 1 2 3 4 5 6 7 8; do
    # 每批4态提取+累加
    > "$TMP"
    for S in 0 1 2 3; do
        STREAM=$D/qscl_32x32_b${B}_s${S}_stream.w
        if [ ! -s "$STREAM" ]; then echo "缺 $STREAM, 中止"; exit 2; fi
        # 提取本态纯值 → 累加到 TMP
        if [ ! -s "$TMP" ]; then
            awk -f qdfs/ns/train/extract_stream.awk "$STREAM" > "$TMP"
        else
            awk -f qdfs/ns/train/extract_stream.awk "$STREAM" > /tmp/state_tmp.w
            awk -f qdfs/ns/train/add_two_streams.awk "$TMP" /tmp/state_tmp.w > /tmp/state_sum.w
            mv /tmp/state_sum.w "$TMP"
        fi
    done
    cat "$TMP" >> "$OUT"
    SZ=$(wc -c < "$TMP")
    echo "batch${B} 合并完成 ${SZ}B"
done
echo "最终权重: $OUT ($(wc -c < $OUT)B)"
