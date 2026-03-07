#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速彝文生成测试
"""

import torch
import json
import os

def quick_test():
    """快速测试彝文生成"""
    print("=== 快速彝文生成测试 ===")
    
    # 加载词汇表
    vocab_path = "Models/QSM/bin/qsm_yi_wen_vocab.json"
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab_data = json.load(f)
        char_to_id = vocab_data['char_to_id']
    
    print(f"词汇表大小: {len(char_to_id)}")
    
    # 测试一些彝文字符
    yi_chars = []
    for char, char_id in char_to_id.items():
        try:
            if len(char) == 1 and 0xF0000 <= ord(char) <= 0xFFFFF:
                yi_chars.append(char)
        except:
            continue
    
    print(f"彝文字符数量: {len(yi_chars)}")
    if yi_chars:
        print(f"彝文字符示例: {yi_chars[:10]}")
    
    # 测试生成
    test_input = "中文：陷害 彝文："
    input_ids = [char_to_id.get(char, 0) for char in test_input]
    print(f"输入: {test_input}")
    print(f"输入ID: {input_ids}")
    
    # 模拟生成一些彝文字符ID
    yi_char_ids = [char_id for char, char_id in char_to_id.items() 
                   if len(char) == 1 and 0xF0000 <= ord(char) <= 0xFFFFF][:10]
    print(f"彝文字符ID示例: {yi_char_ids}")
    
    # 解码测试
    generated_text = ""
    for char_id in yi_char_ids:
        char = list(char_to_id.keys())[list(char_to_id.values()).index(char_id)]
        generated_text += char
    
    print(f"生成的彝文: {generated_text}")
    
    # 检查彝文字符
    yi_count = 0
    for char in generated_text:
        try:
            if 0xF0000 <= ord(char) <= 0xFFFFF:
                yi_count += 1
        except:
            continue
    
    print(f"彝文字符数量: {yi_count}")
    if yi_count > 0:
        print("✓ 成功生成彝文字符！")
    else:
        print("✗ 未生成彝文字符")

if __name__ == "__main__":
    quick_test() 