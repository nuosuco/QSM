#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试已有彝文模型"""

import torch
import json
import os

def test_yi_wen_model():
    print("="*50)
    print("彝文模型可用性测试")
    print("="*50)

    # 检查模型文件
    model_path = "/root/QSM/Models/QSM/bin/qsm_yi_wen_model.pth"
    vocab_path = "/root/QSM/Models/QSM/bin/qsm_yi_wen_vocab.json"

    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        return False

    if not os.path.exists(vocab_path):
        print(f"❌ 词汇表不存在: {vocab_path}")
        return False

    print(f"✅ 模型文件: {os.path.getsize(model_path)/1024/1024:.2f} MB")
    print(f"✅ 词汇表: {os.path.getsize(vocab_path)/1024:.2f} KB")

    # 加载词汇表
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab_data = json.load(f)
    char_to_id = vocab_data['char_to_id']
    print(f"✅ 词汇量: {len(char_to_id)}")

    # 检查核心彝文字符
    core_chars = {
        '心': '\U000f2737',
        '天': '\U000f27ad',
        '火': '\U000f27ae',
        '王': '\U000f27b0',
    }

    print("\n核心彝文字符检查:")
    for name, yi_char in core_chars.items():
        if yi_char in char_to_id:
            print(f"  ✅ {name} ({yi_char}): ID={char_to_id[yi_char]}")
        else:
            print(f"  ❌ {name} ({yi_char}): 未找到")

    # 尝试加载模型
    print("\n加载模型检查点...")
    try:
        checkpoint = torch.load(model_path, map_location='cpu')
        if isinstance(checkpoint, dict):
            print(f"  ✅ 模型是state_dict格式")
            if 'embedding.weight' in checkpoint:
                vocab_size = checkpoint['embedding.weight'].shape[0]
                d_model = checkpoint['embedding.weight'].shape[1]
                print(f"  ✅ 词汇表大小: {vocab_size}")
                print(f"  ✅ 模型维度: {d_model}")
        else:
            print(f"  ✅ 模型类型: {type(checkpoint)}")
        print("\n✅ 模型加载成功！")
        return True
    except Exception as e:
        print(f"  ❌ 加载失败: {e}")
        return False

if __name__ == "__main__":
    test_yi_wen_model()
