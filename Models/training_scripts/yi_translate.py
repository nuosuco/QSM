#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的彝文模型推理 - 使用对齐词汇表
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
                 dropout: float = 0.1, max_seq_length: int = 256):
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

class YiWenTranslator:
    def __init__(self):
        self.model_vocab_path = "/root/QSM/Models/QSM/bin/vocab.json"  # 原始词汇表
        self.model_path = "/root/QSM/Models/QSM/bin/qsm_yi_wen_generation_model_fixed.pth"
        self.model_vocab_size = 6920  # 模型原始词汇表大小

        # 加载原始词汇表（模型使用的）
        with open(self.model_vocab_path, 'r', encoding='utf-8') as f:
            self.char_to_id = json.load(f)['char_to_id']
        self.id_to_char = {i: ch for ch, i in self.char_to_id.items()}

        # 创建并加载模型（使用原始词汇表大小）
        self.model = QuantumTransformerModel(vocab_size=self.model_vocab_size)
        if os.path.exists(self.model_path):
            state_dict = torch.load(self.model_path, map_location='cpu')
            self.model.load_state_dict(state_dict, strict=True)

    def encode(self, text):
        return [self.char_to_id.get(c, 1) for c in text]

    def decode(self, ids):
        return ''.join([self.id_to_char.get(i, '') for i in ids])

    def translate_yi_to_zh(self, yi_text, max_length=50):
        """彝文翻译成中文"""
        self.model.eval()
        with torch.no_grad():
            input_ids = self.encode(yi_text)
            if not input_ids:
                return "无法识别"
            input_tensor = torch.tensor([input_ids])
            output = self.model(input_tensor)
            predicted = torch.argmax(output[0], dim=-1).tolist()
            return self.decode(predicted[:max_length])

    def translate_zh_to_yi(self, zh_text, max_length=50):
        """中文翻译成彝文"""
        self.model.eval()
        with torch.no_grad():
            input_ids = self.encode(zh_text)
            if not input_ids:
                return "无法识别"
            input_tensor = torch.tensor([input_ids])
            output = self.model(input_tensor)
            predicted = torch.argmax(output[0], dim=-1).tolist()
            return self.decode(predicted[:max_length])

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 改进版彝文模型推理")
    print("=" * 60)

    translator = YiWenTranslator()
    print(f"\n词汇表大小: {len(translator.char_to_id)}")

    # 测试翻译
    print("\n" + "-" * 40)
    print("测试彝文 → 中文:")
    print("-" * 40)

    test_yi = [
        '\U000f2737',  # 心
        '\U000f27ad',  # 天
        '\U000f27b0',  # 王
    ]

    for yi in test_yi:
        result = translator.translate_yi_to_zh(yi)
        print(f"  彝文 '{yi}' → 输出: {result}")

    print("\n" + "-" * 40)
    print("测试中文 → 彝文（模型训练方向）:")
    print("-" * 40)

    # 训练数据格式：user=中文, assistant=彝文
    test_zh = ['心', '天', '王', '彝族', '你好', '陷害', '兔子']

    for zh in test_zh:
        result = translator.translate_zh_to_yi(zh)
        print(f"  中文 '{zh}' → 彝文: {result}")

    print("\n" + "-" * 40)
    print("测试彝文 → 中文（反向，效果可能不好）:")
    print("-" * 40)

    test_yi = [
        '\U000f2710',  # 陷害
        '\U000f2711',  # 兔子
        '\U000f2737',  # 心
    ]

    for yi in test_yi:
        result = translator.translate_yi_to_zh(yi)
        print(f"  彝文 '{yi}' → 中文: {result}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
