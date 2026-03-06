#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彝文生成模型分析脚本
详细分析训练后的彝文生成模型
"""

import torch
import torch.nn as nn
import json
import os
import math
from typing import Optional
from collections import Counter

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

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)

class QuantumTransformerModel(nn.Module):
    def __init__(self, vocab_size: int, d_model: int, nhead: int, num_encoder_layers: int, dim_feedforward: int, dropout: float = 0.1, max_seq_length: int = 8192):
        super().__init__()
        self.model_type = 'Transformer'
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout, max_len=max_seq_length)
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_encoder_layers)
        self.decoder = nn.Linear(d_model, vocab_size)
        self.init_weights()

    def init_weights(self) -> None:
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange, initrange)

    def forward(self, src: torch.Tensor, src_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        src = self.embedding(src) * math.sqrt(self.d_model)
        src = src.transpose(0, 1)
        src = self.pos_encoder(src)
        src = src.transpose(0, 1)
        output = self.transformer_encoder(src, src_mask)
        output = self.decoder(output)
        return output

class SimpleTokenizer:
    def __init__(self, vocab_path):
        with open(vocab_path, 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)
            self.char_to_id = vocab_data['char_to_id']
        self.id_to_char = {i: ch for ch, i in self.char_to_id.items()}
        self.unk_token_id = self.char_to_id.get('‪', 0)

    def encode(self, text):
        return [self.char_to_id.get(char, self.unk_token_id) for char in text]

    def decode(self, token_ids):
        return "".join([self.id_to_char.get(token_id, '') for token_id in token_ids])

    @property
    def vocab_size(self):
        return len(self.char_to_id)

class YiWenModelAnalyzer:
    def __init__(self, model_dir):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Yi Wen Model Analyzer using device: {self.device}")

        # Load tokenizer
        vocab_path = os.path.join(model_dir, 'qsm_yi_wen_vocab.json')
        self.tokenizer = SimpleTokenizer(vocab_path)
        
        # Model parameters
        model_params = {
            'vocab_size': self.tokenizer.vocab_size,
            'd_model': 256,
            'nhead': 8,
            'num_encoder_layers': 3,
            'dim_feedforward': 1024,
            'max_seq_length': 256
        }

        # Initialize model
        self.model = QuantumTransformerModel(**model_params).to(self.device)
        
        # Load trained model weights
        model_path = os.path.join(model_dir, 'qsm_yi_wen_generation_model.pth')
        try:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            print("Successfully loaded model weights")
        except Exception as e:
            print(f"Warning: Could not load model weights: {e}")
            print("Using random initialization")
        
        self.model.eval()
        print("Yi Wen generation model loaded successfully.")
        print(f"Vocabulary size: {self.tokenizer.vocab_size}")

    def analyze_vocabulary(self):
        """分析词汇表"""
        print("\n=== 词汇表分析 ===")
        
        # 统计字符类型
        chinese_chars = []
        english_chars = []
        yi_chars = []
        other_chars = []
        
        for char, char_id in self.tokenizer.char_to_id.items():
            try:
                if '\u4e00' <= char <= '\u9fff':  # 中文字符
                    chinese_chars.append(char)
                elif '\u0061' <= char <= '\u007a' or '\u0041' <= char <= '\u005a':  # 英文字符
                    english_chars.append(char)
                elif len(char) == 1 and (0x1F200 <= ord(char) <= 0x1F6FF or 0x1F900 <= ord(char) <= 0x1F9FF):  # 彝文字符
                    yi_chars.append(char)
                else:
                    other_chars.append(char)
            except (TypeError, ValueError):
                other_chars.append(char)
        
        print(f"中文字符: {len(chinese_chars)} 个")
        print(f"英文字符: {len(english_chars)} 个")
        print(f"彝文字符: {len(yi_chars)} 个")
        print(f"其他字符: {len(other_chars)} 个")
        
        if yi_chars:
            print(f"彝文字符示例: {yi_chars[:10]}")
        
        return len(yi_chars)

    def generate_response(self, prompt, max_len=30, temperature=0.7, top_k=50):
        """生成回复"""
        try:
            input_ids = self.tokenizer.encode(prompt)
            input_tensor = torch.tensor([input_ids], dtype=torch.long).to(self.device)
            
            generated_ids = []
            with torch.no_grad():
                for _ in range(max_len):
                    outputs = self.model(input_tensor)
                    next_token_logits = outputs[:, -1, :]

                    # Apply temperature
                    if temperature > 0:
                        next_token_logits = next_token_logits / temperature
                    
                    # Apply top-k sampling
                    top_k_logits, top_k_indices = torch.topk(next_token_logits, top_k)
                    probabilities = torch.nn.functional.softmax(top_k_logits, dim=-1)
                    next_token_id_index = torch.multinomial(probabilities, 1).item()
                    next_token_id = top_k_indices[0, next_token_id_index].item()
                    
                    # Stop if we generate a stop token or newline
                    decoded_token = self.tokenizer.decode([next_token_id])
                    if '\n' in decoded_token or len(generated_ids) >= max_len:
                        break
                    
                    generated_ids.append(next_token_id)
                    input_tensor = torch.cat([input_tensor, torch.tensor([[next_token_id]], device=self.device)], dim=1)
            
            response_text = self.tokenizer.decode(generated_ids).strip()
            return response_text

        except Exception as e:
            print(f"Error during generation: {e}")
            return "生成错误"

    def analyze_generation_quality(self):
        """分析生成质量"""
        print("\n=== 生成质量分析 ===")
        
        test_cases = [
            "中文：陷害 彝文：",
            "中文：兔子 彝文：",
            "中文：雪 彝文：",
            "中文：心 彝文：",
            "中文：火 彝文：",
            "中文：天 彝文：",
            "中文：人 彝文："
        ]
        
        all_generated_chars = []
        
        for test_input in test_cases:
            print(f"\n输入: {test_input}")
            response = self.generate_response(test_input)
            print(f"输出: {response}")
            
            # 分析生成的字符
            yi_chars = []
            chinese_chars = []
            other_chars = []
            
            for char in response:
                try:
                    if len(char) == 1 and (0x1F200 <= ord(char) <= 0x1F6FF or 0x1F900 <= ord(char) <= 0x1F9FF):
                        yi_chars.append(char)
                    elif '\u4e00' <= char <= '\u9fff':
                        chinese_chars.append(char)
                    else:
                        other_chars.append(char)
                except (TypeError, ValueError):
                    other_chars.append(char)
            
            all_generated_chars.extend(yi_chars)
            
            print(f"彝文字符: {len(yi_chars)} 个")
            print(f"中文字符: {len(chinese_chars)} 个")
            print(f"其他字符: {len(other_chars)} 个")
            
            if yi_chars:
                print(f"彝文字符示例: {yi_chars[:5]}")
        
        # 统计所有生成的彝文字符
        if all_generated_chars:
            char_counter = Counter(all_generated_chars)
            print(f"\n总共生成彝文字符: {len(all_generated_chars)} 个")
            print(f"不同彝文字符: {len(char_counter)} 个")
            print(f"最常见的彝文字符: {char_counter.most_common(10)}")

    def test_model_parameters(self):
        """测试模型参数"""
        print("\n=== 模型参数分析 ===")
        
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        print(f"总参数数量: {total_params:,}")
        print(f"可训练参数数量: {trainable_params:,}")
        
        # 计算模型大小
        model_size_mb = total_params * 4 / (1024 * 1024)  # 假设float32
        print(f"模型大小: {model_size_mb:.2f} MB")

if __name__ == "__main__":
    analyzer = YiWenModelAnalyzer("Models/QSM/bin")
    analyzer.analyze_vocabulary()
    analyzer.test_model_parameters()
    analyzer.analyze_generation_quality() 