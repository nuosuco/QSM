#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的彝文生成模型
"""

import torch
import torch.nn as nn
import json
import os
import math
from typing import Optional

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

class FixedYiWenTester:
    def __init__(self, model_dir):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Fixed Yi Wen Tester using device: {self.device}")

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
        
        # Load fixed model weights
        fixed_model_path = os.path.join(model_dir, 'qsm_yi_wen_generation_model_fixed.pth')
        self.model.load_state_dict(torch.load(fixed_model_path, map_location=self.device))
        self.model.eval()
        print("✓ 成功加载修复后的彝文生成模型")
        print(f"词汇表大小: {self.tokenizer.vocab_size}")

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

    def test_yi_wen_generation(self):
        """测试彝文生成能力"""
        test_cases = [
            "中文：陷害 彝文：",
            "中文：兔子 彝文：",
            "中文：雪 彝文：",
            "中文：心 彝文：",
            "中文：火 彝文：",
            "中文：天 彝文：",
            "中文：人 彝文：",
            "请用彝文回答：陷害",
            "翻译成彝文：兔子",
            "问：雪\n答："
        ]
        
        print("\n=== 修复后模型彝文生成测试 ===")
        total_yi_chars = 0
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"\n{i}. 输入: {test_input}")
            response = self.generate_response(test_input)
            print(f"   输出: {response}")
            
            # 检查是否包含彝文字符
            yi_chars = []
            for char in response:
                try:
                    # 彝文字符的正确Unicode范围
                    if len(char) == 1 and (0xF0000 <= ord(char) <= 0xFFFFF):
                        yi_chars.append(char)
                except (TypeError, ValueError):
                    continue
            
            if yi_chars:
                print(f"   ✓ 包含彝文字符: {len(yi_chars)} 个")
                print(f"   ✓ 彝文字符示例: {yi_chars[:5]}")
                total_yi_chars += len(yi_chars)
            else:
                print("   ✗ 未生成彝文字符")
        
        print(f"\n=== 总结 ===")
        print(f"总共生成彝文字符: {total_yi_chars} 个")
        print(f"平均每个测试用例: {total_yi_chars / len(test_cases):.1f} 个彝文字符")

if __name__ == "__main__":
    tester = FixedYiWenTester("Models/QSM/bin")
    tester.test_yi_wen_generation() 