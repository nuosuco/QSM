#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彝文生成模型测试脚本
测试新训练的彝文生成模型
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

    def resize_embedding_layer(self, new_num_tokens: int):
        """Resizes the token embedding layer to accommodate a new vocabulary size."""
        old_embedding = self.embedding
        new_embedding = nn.Embedding(new_num_tokens, self.d_model)
        new_embedding.to(old_embedding.weight.device)

        # Copy weights from the old embedding to the new one
        num_tokens_to_copy = min(old_embedding.num_embeddings, new_num_tokens)
        new_embedding.weight.data[:num_tokens_to_copy, :] = old_embedding.weight.data[:num_tokens_to_copy, :]
        
        # Replace the old embedding layer
        self.embedding = new_embedding
        
        # Also resize the decoder
        old_decoder = self.decoder
        new_decoder = nn.Linear(self.d_model, new_num_tokens)
        new_decoder.to(old_decoder.weight.device)
        
        # Copy weights from the old decoder to the new one
        new_decoder.weight.data[:num_tokens_to_copy, :] = old_decoder.weight.data[:num_tokens_to_copy, :]
        new_decoder.bias.data[:num_tokens_to_copy] = old_decoder.bias.data[:num_tokens_to_copy]
        
        # Replace the old decoder
        self.decoder = new_decoder

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

class YiWenGenerationTester:
    def __init__(self, model_dir):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Yi Wen Generation Tester using device: {self.device}")

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

    def generate_response(self, prompt, max_len=30, temperature=0.7, top_k=50):
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
        
        print("\n=== 彝文生成测试 ===")
        for test_input in test_cases:
            print(f"\n输入: {test_input}")
            response = self.generate_response(test_input)
            print(f"输出: {response}")
            
            # 检查是否包含彝文字符 - 修复检测逻辑
            yi_chars = []
            for char in response:
                # 彝文字符的Unicode范围
                if (0x1F200 <= ord(char) <= 0x1F6FF) or (0x1F900 <= ord(char) <= 0x1F9FF):
                    yi_chars.append(char)
            
            if yi_chars:
                print(f"✓ 包含彝文字符: {yi_chars}")
                print(f"✓ 彝文字符数量: {len(yi_chars)}")
            else:
                print("✗ 未生成彝文字符")
            
            # 统计所有特殊字符
            special_chars = [char for char in response if ord(char) > 0xFFFF]
            if special_chars:
                print(f"特殊字符: {special_chars}")

if __name__ == "__main__":
    tester = YiWenGenerationTester("Models/QSM/bin")
    tester.test_yi_wen_generation() 