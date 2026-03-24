#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM彝文训练启动器
使用已有的12,360行训练数据开始知识内化
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 设置路径
QSM_ROOT = Path('/root/QSM')
TRAINING_DATA_DIR = QSM_ROOT / 'Models' / 'training_data' / 'datasets' / 'yi_wen'
OUTPUT_DIR = QSM_ROOT / 'Models' / 'training_output'

def check_training_data():
    """检查训练数据"""
    print("=" * 50)
    print("检查训练数据")
    print("=" * 50)
    
    data_files = {
        'trilingual': TRAINING_DATA_DIR / '滇川黔贵通用彝文三语对照表.jsonl',
        'yi_han': TRAINING_DATA_DIR / '通用彝文彝汉对照训练表(2.0.4.22).jsonl',
        'han_yi': TRAINING_DATA_DIR / '通用彝文汉彝对照训练表(2.0.4.22).jsonl',
    }
    
    total_lines = 0
    for name, filepath in data_files.items():
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = sum(1 for _ in f)
            print(f"✅ {name}: {lines}行")
            total_lines += lines
        else:
            print(f"❌ {name}: 文件不存在")
            
    print(f"\n总训练数据: {total_lines}行")
    return total_lines >= 10000  # 至少1万行


def create_training_config():
    """创建训练配置"""
    config = {
        'model_name': 'QSM-YiWen-v1',
        'training_data': {
            'trilingual': str(TRAINING_DATA_DIR / '滇川黔贵通用彝文三语对照表.jsonl'),
            'vocab_size': 4120,
            'languages': ['yi', 'zh', 'en']
        },
        'training_params': {
            'epochs': 10,
            'batch_size': 32,
            'learning_rate': 0.001,
            'max_seq_length': 128
        },
        'output_dir': str(OUTPUT_DIR),
        'created_at': datetime.now().isoformat()
    }
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    config_path = OUTPUT_DIR / 'training_config.json'
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"\n配置已创建: {config_path}")
    return config


def prepare_vocab():
    """准备词汇表"""
    vocab_path = QSM_ROOT / 'Models' / 'shared' / 'unified_vocab.json'
    
    if vocab_path.exists():
        print(f"\n✅ 词汇表已存在: {vocab_path}")
        with open(vocab_path, 'r', encoding='utf-8') as f:
            vocab = json.load(f)
        print(f"   词汇量: {len(vocab)}")
        return vocab
    else:
        print(f"\n❌ 词汇表不存在: {vocab_path}")
        return None


def run_training_preparation():
    """运行训练准备"""
    print("=" * 50)
    print("QSM彝文训练准备")
    print("=" * 50)
    
    # 1. 检查数据
    print("\n[1] 检查训练数据...")
    data_ready = check_training_data()
    
    if not data_ready:
        print("\n❌ 训练数据不足")
        return False
    
    # 2. 创建配置
    print("\n[2] 创建训练配置...")
    config = create_training_config()
    
    # 3. 准备词汇表
    print("\n[3] 准备词汇表...")
    vocab = prepare_vocab()
    
    # 4. 状态总结
    print("\n" + "=" * 50)
    print("训练准备状态")
    print("=" * 50)
    print(f"数据就绪: {'✅' if data_ready else '❌'}")
    print(f"配置创建: ✅")
    print(f"词汇表: {'✅' if vocab else '❌'}")
    
    if data_ready and vocab:
        print("\n🎉 训练准备完成！可以开始训练。")
        print("\n下一步: 运行实际训练")
        print("  python3 Models/training_scripts/train_yi_wen_qsm.py")
        return True
    else:
        print("\n⚠️ 训练准备未完成")
        return False


if __name__ == "__main__":
    success = run_training_preparation()
    sys.exit(0 if success else 1)
