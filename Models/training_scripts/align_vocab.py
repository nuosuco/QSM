#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词汇表对齐脚本 - 使模型词汇表与训练数据对齐
"""

import json
import os
from datetime import datetime

def load_vocab(path):
    """加载词汇表"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('char_to_id', data)

def save_vocab(path, char_to_id):
    """保存词汇表"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'char_to_id': char_to_id}, f, ensure_ascii=False, indent=2)

def build_aligned_vocab():
    """构建对齐的词汇表"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始构建对齐词汇表...")

    # 加载原始词汇表
    old_vocab_path = "/root/QSM/Models/QSM/bin/vocab.json"
    new_vocab_path = "/root/QSM/Models/QSM/bin/qsm_yi_wen_vocab.json"

    old_vocab = load_vocab(old_vocab_path)
    new_vocab = load_vocab(new_vocab_path)

    print(f"  原始词汇表: {len(old_vocab)} 字符")
    print(f"  新词汇表: {len(new_vocab)} 字符")

    # 构建映射关系
    # 新词汇表中的字符 -> 原始词汇表ID（如果存在）或新ID
    aligned_vocab = {'<pad>': 0, '<unk>': 1}

    # 先添加原始词汇表中的所有字符
    for char, idx in old_vocab.items():
        if char not in aligned_vocab:
            aligned_vocab[char] = len(aligned_vocab)

    # 然后添加新词汇表中的彝文字符
    yi_chars_added = 0
    for char, idx in new_vocab.items():
        if char not in aligned_vocab:
            aligned_vocab[char] = len(aligned_vocab)
            yi_chars_added += 1

    print(f"  对齐后词汇表: {len(aligned_vocab)} 字符")
    print(f"  新增彝文字符: {yi_chars_added}")

    # 保存对齐后的词汇表
    aligned_path = "/root/QSM/Models/QSM/bin/qsm_yi_wen_aligned_vocab.json"
    save_vocab(aligned_path, aligned_vocab)
    print(f"  ✅ 保存到: {aligned_path}")

    # 创建映射文件
    old_to_new = {}
    for char, old_idx in old_vocab.items():
        new_idx = aligned_vocab.get(char, 1)
        old_to_new[old_idx] = new_idx

    mapping_path = "/root/QSM/Models/QSM/bin/vocab_mapping.json"
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump({'old_to_new': old_to_new, 'old_vocab_size': len(old_vocab), 'new_vocab_size': len(aligned_vocab)}, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 映射文件: {mapping_path}")

    return aligned_vocab

def test_aligned_vocab():
    """测试对齐后的词汇表"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 测试对齐词汇表...")

    aligned_path = "/root/QSM/Models/QSM/bin/qsm_yi_wen_aligned_vocab.json"
    vocab = load_vocab(aligned_path)

    # 测试核心彝文字符
    test_chars = {
        '心': '\U000f2737',
        '天': '\U000f27ad',
        '火': '\U000f27ae',
        '王': '\U000f27b0',
        '彝': '\U000f2970',
        '文': '\U000f2961',
    }

    print("\n  核心字符测试:")
    for name, yi_char in test_chars.items():
        if yi_char in vocab:
            print(f"    ✅ {name} ({yi_char}): ID={vocab[yi_char]}")
        else:
            print(f"    ❌ {name} ({yi_char}): 不存在")

    return True

if __name__ == "__main__":
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 词汇表对齐工具")
    print("=" * 60)

    build_aligned_vocab()
    test_aligned_vocab()

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 完成")
    print("=" * 60)
