#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复模型和词汇表大小不匹配问题
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

def fix_model_vocab_mismatch(model_dir):
    """修复模型和词汇表大小不匹配的问题"""
    print("=== 修复模型和词汇表大小不匹配 ===")
    
    # 加载词汇表
    vocab_path = os.path.join(model_dir, 'qsm_yi_wen_vocab.json')
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab_data = json.load(f)
        char_to_id = vocab_data['char_to_id']
    
    vocab_size = len(char_to_id)
    print(f"词汇表大小: {vocab_size}")
    
    # 加载模型权重
    model_path = os.path.join(model_dir, 'qsm_yi_wen_generation_model.pth')
    checkpoint = torch.load(model_path, map_location='cpu')
    
    print("检查点中的层:")
    for key, value in checkpoint.items():
        print(f"  {key}: {value.shape}")
    
    # 检查embedding层大小
    embedding_key = 'embedding.weight'
    decoder_weight_key = 'decoder.weight'
    decoder_bias_key = 'decoder.bias'
    
    if embedding_key in checkpoint:
        checkpoint_vocab_size = checkpoint[embedding_key].shape[0]
        print(f"检查点中的词汇表大小: {checkpoint_vocab_size}")
        print(f"当前词汇表大小: {vocab_size}")
        
        if checkpoint_vocab_size != vocab_size:
            print(f"词汇表大小不匹配，需要调整模型")
            
            # 调整embedding层
            if embedding_key in checkpoint:
                old_embedding = checkpoint[embedding_key]
                new_embedding = torch.randn(vocab_size, old_embedding.shape[1])
                # 复制较小的那个大小
                min_size = min(checkpoint_vocab_size, vocab_size)
                new_embedding[:min_size, :] = old_embedding[:min_size, :]
                checkpoint[embedding_key] = new_embedding
                print(f"调整embedding层: {old_embedding.shape} -> {new_embedding.shape}")
            
            # 调整decoder层
            if decoder_weight_key in checkpoint:
                old_decoder_weight = checkpoint[decoder_weight_key]
                new_decoder_weight = torch.randn(vocab_size, old_decoder_weight.shape[1])
                # 复制较小的那个大小
                min_size = min(checkpoint_vocab_size, vocab_size)
                new_decoder_weight[:min_size, :] = old_decoder_weight[:min_size, :]
                checkpoint[decoder_weight_key] = new_decoder_weight
                print(f"调整decoder权重: {old_decoder_weight.shape} -> {new_decoder_weight.shape}")
            
            if decoder_bias_key in checkpoint:
                old_decoder_bias = checkpoint[decoder_bias_key]
                new_decoder_bias = torch.randn(vocab_size)
                # 复制较小的那个大小
                min_size = min(checkpoint_vocab_size, vocab_size)
                new_decoder_bias[:min_size] = old_decoder_bias[:min_size]
                checkpoint[decoder_bias_key] = new_decoder_bias
                print(f"调整decoder偏置: {old_decoder_bias.shape} -> {new_decoder_bias.shape}")
            
            # 保存修复后的模型
            fixed_model_path = os.path.join(model_dir, 'qsm_yi_wen_generation_model_fixed.pth')
            torch.save(checkpoint, fixed_model_path)
            print(f"修复后的模型已保存到: {fixed_model_path}")
            
            return fixed_model_path
        else:
            print("词汇表大小匹配，无需修复")
            return model_path
    else:
        print("未找到embedding层，无法修复")
        return None

def test_fixed_model(model_dir, fixed_model_path):
    """测试修复后的模型"""
    print("\n=== 测试修复后的模型 ===")
    
    # 加载词汇表
    vocab_path = os.path.join(model_dir, 'qsm_yi_wen_vocab.json')
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab_data = json.load(f)
        char_to_id = vocab_data['char_to_id']
    
    vocab_size = len(char_to_id)
    
    # 创建模型
    model_params = {
        'vocab_size': vocab_size,
        'd_model': 256,
        'nhead': 8,
        'num_encoder_layers': 3,
        'dim_feedforward': 1024,
        'max_seq_length': 256
    }
    
    model = QuantumTransformerModel(**model_params)
    
    # 加载修复后的权重
    try:
        model.load_state_dict(torch.load(fixed_model_path, map_location='cpu'))
        print("✓ 成功加载修复后的模型权重")
        
        # 测试生成
        model.eval()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        
        # 简单的生成测试
        test_input = "中文：陷害 彝文："
        input_ids = [char_to_id.get(char, 0) for char in test_input]
        input_tensor = torch.tensor([input_ids], dtype=torch.long).to(device)
        
        with torch.no_grad():
            outputs = model(input_tensor)
            print(f"模型输出形状: {outputs.shape}")
            print("✓ 模型运行正常")
            
    except Exception as e:
        print(f"✗ 加载模型失败: {e}")

if __name__ == "__main__":
    model_dir = "Models/QSM/bin"
    fixed_model_path = fix_model_vocab_mismatch(model_dir)
    if fixed_model_path:
        test_fixed_model(model_dir, fixed_model_path) 