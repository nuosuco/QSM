#!/bin/bash
# V13 Training Launch Script
# QSM V7-Small architecture with SGDR + LoRA + Curriculum Learning

cd /root/.openclaw/workspace/Models/QSM

export PYTHONDONTWRITEBYTECODE=1

# V13 Training Configuration
# Architecture: 192d/3layers/3heads/768ff (V7-Small)
# Data: v13_clean_dataset.json (78K+ pairs)
# Optimizations: SGDR + LoRA r=16 + Curriculum + Grad Clip + Label Smoothing 0.1

echo "=== V13 Training Start ==="
echo "Data: v13_clean_dataset.json (78,330 pairs)"
echo "Architecture: 192d/3L/3H/768ff"
echo "Scheduler: SGDR (T0=10, Tmult=2)"
echo "LoRA: r=16, alpha=16"
echo "Curriculum: 4 phases"
echo "============================"

python3 train_v7_quantum.py \
  --data bin/v13_clean_dataset.json \
  --d_model 192 \
  --n_heads 3 \
  --n_layers 3 \
  --d_ff 768 \
  --max_len 64 \
  --dropout 0.2 \
  --epochs 100 \
  --batch_size 32 \
  --lr 0.0003 \
  --warmup_steps 500 \
  --scheduler sgdr \
  --sgdr_t0 10 \
  --sgdr_tmult 2 \
  --lora 16 \
  --lora_alpha 16 \
  --curriculum \
  --max_difficulty 4 \
  --grad_clip 1.0 \
  --label_smoothing 0.1 \
  --val_interval 1 \
  --output_dir bin/ \
  2>&1 | tee /tmp/qsm_v13_training.log
