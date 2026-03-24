#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彝文模型推理测试 - 验证生成效果
"""

import torch
import torch.nn as nn
import json
import math
import os
from datetime import datetime

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)

class QuantumTransformerModel(nn.Module):
    def __init__(self, vocab_size: int, d_model: int = 256, nhead: int = 8,
                 num_encoder_layers: int = 3, dim_feedforward: int = 1024,
                 dropout: float = 0.1, max_seq_length: int = 8192):
        super().__init__()
        self.model_type = 'Transformer'
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout, max_len=max_seq_length)
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_encoder_layers)
        self.decoder = nn.Linear(d_model, vocab_size)
        self.init_weights()

    def init_weights(self):
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange, initrange)

    def forward(self, src, src_mask=None):
        src = self.embedding(src) * math.sqrt(self.d_model)
        src = src.transpose(0, 1)
        src = self.pos_encoder(src)
        src = src.transpose(0, 1)
        output = self.transformer_encoder(src, src_mask)
        output = self.decoder(output)
        return output

def generate_text(model, tokenizer, prompt, max_length=50, temperature=1.0):
    """生成文本"""
    model.eval()
    with torch.no_grad():
        input_ids = tokenizer.encode(prompt)
        input_tensor = torch.tensor([input_ids])

        generated = list(input_ids)

        for _ in range(max_length):
            outputs = model(input_tensor)
            next_token_logits = outputs[0, -1, :] / temperature
            next_token = torch.argmax(next_token_logits).item()

            if next_token == tokenizer.char_to_id.get('<pad>', 0):
                break

            generated.append(next_token)
            input_tensor = torch.tensor([generated])

        return tokenizer.decode(generated)

class SimpleTokenizer:
    def __init__(self, vocab_path):
        with open(vocab_path, 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)
        self.char_to_id = vocab_data['char_to_id']
        self.id_to_char = {i: ch for ch, i in self.char_to_id.items()}

    def encode(self, text):
        return [self.char_to_id.get(c, 1) for c in text]

    def decode(self, token_ids):
        return ''.join([self.id_to_char.get(i, '') for i in token_ids])

    @property
    def vocab_size(self):
        return len(self.char_to_id)

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 彝文模型推理测试")
    print("=" * 60)

    # 路径
    vocab_path = "/root/QSM/Models/QSM/bin/qsm_yi_wen_vocab.json"
    model_path = "/root/QSM/Models/QSM/bin/qsm_yi_wen_generation_model_fixed.pth"

    # 加载词汇表
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 加载词汇表...")
    tokenizer = SimpleTokenizer(vocab_path)
    print(f"  词汇量: {tokenizer.vocab_size}")

    # 创建模型 - 使用原始词汇表大小6920
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 创建模型...")
    model = QuantumTransformerModel(vocab_size=6920, max_seq_length=256)  # 原始词汇表大小
    print(f"  模型参数: {sum(p.numel() for p in model.parameters()):,}")

    # 加载模型权重
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 加载模型权重...")
    if os.path.exists(model_path):
        state_dict = torch.load(model_path, map_location='cpu')
        model.load_state_dict(state_dict, strict=True)
        print(f"  ✅ 模型加载成功")
        # 使用原始词汇表
        original_vocab_path = "/root/QSM/Models/QSM/bin/vocab.json"
        if os.path.exists(original_vocab_path):
            tokenizer = SimpleTokenizer(original_vocab_path)
            print(f"  使用原始词汇表: {tokenizer.vocab_size} 字符")
    else:
        print(f"  ❌ 模型文件不存在: {model_path}")
        return

    # 测试生成
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 测试生成...")

    test_prompts = [
        "心",  # 彝文核心字符
        "用户：你好",
        "彝族",
    ]

    for prompt in test_prompts:
        print(f"\n  输入: {prompt}")
        try:
            output = generate_text(model, tokenizer, prompt, max_length=20, temperature=0.8)
            print(f"  输出: {output}")
        except Exception as e:
            print(f"  错误: {e}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 推理测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
