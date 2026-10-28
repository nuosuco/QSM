#!/bin/bash
# chain_B_after_A.sh - 监控 A 轮, 完成则续 B 轮 + 合并
# 用法: 后台跑, A 完成日志出现 "A 轮完成" 后自动续
cd /root/QSM/QLife || exit 1
echo "等待 A 轮完成..."
while true; do
    if grep -q "A 轮完成" /tmp/train_5316_A.log 2>/dev/null; then
        CNT=$(ls qdfs/ns/models/qscl_32x32_b*_s*_stream.w 2>/dev/null | wc -l)
        echo "A 轮完成, 已生成 $CNT/44 个 stream.w, 启动 B 轮"
        echo "===== B 轮开始 $(date '+%m-%d %H:%M:%S') =====" > /tmp/train_5316_B.log
        # B 轮 seed 改为 10001+s*100
        cp qdfs/ns/train/qscl_32x32_v10.qentl /tmp/v10_A_bak.qentl
        sed -i 's|g_seed = 1 + g_s \* 100|g_seed = 10001 + g_s * 100|' qdfs/ns/train/qscl_32x32_v10.qentl
        for B in 0 1 2 3 4 5 6 7 8 9 10; do
            for S in 0 1 2 3; do
                echo "[B轮] batch=$B state=$S $(date '+%H:%M:%S')" >> /tmp/train_5316_B.log
                rm -f "qdfs/ns/models/qscl_32x32_b${B}_s${S}_stream.w"
                bash qdfs/ns/train/build_run_v10.sh 0 $B $S 10 >> /tmp/train_5316_B.log 2>&1
                mv "qdfs/ns/models/qscl_32x32_b${B}_s${S}_stream.w" "qdfs/ns/models/qscl_32x32_b${B}_s${S}_streamB.w" 2>/dev/null
            done
        done
        cp /tmp/v10_A_bak.qentl qdfs/ns/train/qscl_32x32_v10.qentl
        echo "===== B 轮完成, 开始合并 A+B =====" | tee -a /tmp/train_5316_B.log
        bash qdfs/ns/train/merge_5316_AB.sh 2>&1 | tee -a /tmp/train_5316_B.log
        echo "===== 全部完成 $(date '+%m-%d %H:%M:%S') =====" | tee -a /tmp/train_5316_B.log
        break
    fi
    sleep 60
done
