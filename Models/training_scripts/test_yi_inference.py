#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""彝文模型推理测试"""

import torch
import torch.nn as nn
import json
import math
import os

class QuantumTransformerModel(nn.Module):
    def __init__(self, vocab_size, d_model=256, nhead=8, num_encoder_layers=3, 
                 dim_feedforward=1024, max_seq_length=8192):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_encoder_layers)
        self.decoder = nn.Linear(d_model, vocab_size)

    def forward(self, src):
        src = self.embedding(src) * math.sqrt(self.d_model)
        output = self.transformer_encoder(src)
        return self.decoder(output)

def generate(model, tokenizer, prompt, max_len=50, temperature=1.0):
    """生成文本"""
    model.eval()
    input_ids = tokenizer.encode(prompt)
    input_tensor = torch.tensor([input_ids], dtype=torch.long)
    
    with torch.no_grad():
        for _ in range(max_len):
            outputs = model(input_tensor)
            next_token_logits = outputs[0, -1, :] / temperature
            next_token = torch.argmax(next_token_logits).item()
            
            if next_token == tokenizer.char_to_id.get('<pad>', 0):
                break
                
            input_ids.append(next_token)
            input_tensor = torch.tensor([input_ids], dtype=torch.long)
    
    return tokenizer.decode(input_ids)

def test_inference():
    print("="*60)
    print("彝文模型推理测试")
    print("="*60)
    
    model_path = "/root/QSM/Models/QSM/bin/qsm_yi_wen_model.pth"
    vocab_path = "/root/QSM/Models/QSM/bin/qsm_yi_wen_vocab.json"
    
    # 加载词汇表
    print("\n[1] 加载词汇表...")
    with open(vocab_path, 'r', encoding='utf-8') as f:
        char_to_id = json.load(f)['char_to_id']
    
    id_to_char = {v: k for k, v in char_to_id.items()}
    vocab_size = len(char_to_id)
    print(f"   词汇量: {vocab_size}")
    
    # 创建tokenizer
    class Tokenizer:
        def __init__(self, char_to_id, id_to_char):
            self.char_to_id = char_to_id
            self.id_to_char = id_to_char
        
        def encode(self, text):
            return [self.char_to_id.get(c, 1) for c in text]
        
        def decode(self, ids):
            return ''.join([self.id_to_char.get(i, '') for i in ids])
    
    tokenizer = Tokenizer(char_to_id, id_to_char)
    
    # 加载模型
    print("\n[2] 加载模型...")
    model = QuantumTransformerModel(vocab_size=vocab_size)
    state_dict = torch.load(model_path, map_location='cpu')
    
    # 适配模型大小
    old_vocab_size = state_dict['embedding.weight'].shape[0]
    print(f"   原始词汇表: {old_vocab_size}, 当前: {vocab_size}")
    
    if old_vocab_size != vocab_size:
        # 调整embedding层
        new_embedding = nn.Embedding(vocab_size, 256)
        new_decoder = nn.Linear(256, vocab_size)
        with torch.no_grad():
            num_copy = min(old_vocab_size, vocab_size)
            new_embedding.weight.data[:num_copy] = state_dict['embedding.weight'][:num_copy]
            new_decoder.weight.data[:num_copy] = state_dict['decoder.weight'][:num_copy]
            new_decoder.bias.data[:num_copy] = state_dict['decoder.bias'][:num_copy]
        state_dict['embedding.weight'] = new_embedding.weight.data
        state_dict['decoder.weight'] = new_decoder.weight.data
        state_dict['decoder.bias'] = new_decoder.bias.data
    
    model.load_state_dict(state_dict, strict=False)
    print("   ✅ 模型加载成功")
    
    # 测试推理
    print("\n[3] 推理测试...")
    
    test_prompts = [
        "用户：请用彝文说'心'",
        "用户：请翻译",
        "\U000f2737",  # 心
    ]
    
    for prompt in test_prompts:
        print(f"\n   输入: {repr(prompt)}")
        try:
            result = generate(model, tokenizer, prompt, max_len=20)
            print(f"   输出: {result[:100]}")
        except Exception as e:
            print(f"   错误: {e}")
    
    print("\n" + "="*60)
    print("推理测试完成")
    print("="*60)

if __name__ == "__main__":
    test_inference()
