#!/bin/bash
# merge_5316.sh - 42批合并: batch 0-40 各129类, batch41 27类 (41×129+27=5316)
set -u
cd /root/QSM/QLife || exit 1
D=qdfs/ns/models
OUT=$D/qscl5316_merged.w
TMP=/tmp/merge_batch.w
> "$OUT"
MISS=0

for B in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 39 40 41; do
    > "$TMP"
    # A轮已被B轮覆盖, 只用B轮4态
    for S in 0 1 2 3; do
        F=$D/qscl_32x32_b${B}_s${S}_streamB.w
        if [ ! -s "$F" ]; then
            echo "缺 B轮 $F"
            MISS=$((MISS+1))
            continue
        fi
        if [ ! -s "$TMP" ]; then
            awk -f qdfs/ns/train/extract_stream.awk "$F" > "$TMP"
        else
            awk -f qdfs/ns/train/extract_stream.awk "$F" > /tmp/stateB.w
            awk -f qdfs/ns/train/add_two_streams.awk "$TMP" /tmp/stateB.w > /tmp/sumB.w
            mv /tmp/sumB.w "$TMP"
        fi
    done
    cat "$TMP" >> "$OUT"
    CLS=$(awk 'BEGIN{c=0} /^C[0-9]+:/{c++} END{print c}' "$TMP" 2>/dev/null)
    SZ=$(wc -c < "$TMP")
    echo "batch$B 合并: $CLS 类 $SZ字节"
done

echo "=== 合并完成: $(grep -c '^C' "$OUT") 类 ==="
echo "MISS=$MISS"
