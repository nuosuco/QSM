#!/bin/bash
# chain_all.sh - A 轮完成 → B 轮 → 合并 A+B → 验证
cd /root/QSM/QLife || exit 1
echo "等待 A 轮完成..." > /tmp/chain_all.log
while true; do
    if grep -q "A 轮完成" /tmp/train_5316_A.log 2>/dev/null; then
        CNT=$(ls qdfs/ns/models/qscl_32x32_b*_s*_stream.w 2>/dev/null | wc -l)
        echo "A 轮完成, $CNT/44 stream.w" >> /tmp/chain_all.log
        echo "===== B 轮 $(date '+%m-%d %H:%M:%S') =====" >> /tmp/chain_all.log
        bash qdfs/ns/train/train_5316_fast.sh B >> /tmp/chain_all.log 2>&1
        echo "===== B 轮完成, 合并 =====" >> /tmp/chain_all.log
        bash qdfs/ns/train/merge_5316.sh >> /tmp/chain_all.log 2>&1
        echo "===== 全部完成 $(date '+%m-%d %H:%M:%S') =====" >> /tmp/chain_all.log
        break
    fi
    sleep 60
done
