#!/bin/bash
# QSCL训练启动脚本: 启动4态不同起点叠加态并行训练
# 用法: ./run_train.sh [batch]
BATCH=${1:-0}

# 准备工作目录
mkdir -p qdfs/ns/models

# 每次启动new训练批次
cmd1="TRAIN_BATCH=$BATCH TRAIN_STATE=0 bin/qvm_boot run run/qscl_trainer.qbc > run/train_b${BATCH}_s0.log 2>&1 &"
cmd2="TRAIN_BATCH=$BATCH TRAIN_STATE=1 bin/qvm_boot run run/qscl_trainer.qbc > run/train_b${BATCH}_s1.log 2>&1 &"
cmd3="TRAIN_BATCH=$BATCH TRAIN_STATE=2 bin/qvm_boot run run/qscl_trainer.qbc > run/train_b${BATCH}_s2.log 2>&1 &"
cmd4="TRAIN_BATCH=$BATCH TRAIN_STATE=3 bin/qvm_boot run run/qscl_trainer.qbc > run/train_b${BATCH}_s3.log 2>&.log 2>&1 &"

echo "启动批次 $BATCH: 态0/1/2/3"
eval $cmd1
eval $cmd2
eval $cmd3
eval $cmd4

echo "启动进程:"
sleep 5
tail -5 run/train_b${BATCH}_s*.log

