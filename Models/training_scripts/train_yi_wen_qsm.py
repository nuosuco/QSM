#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彝文QSM模型训练脚本
使用彝文训练数据重新训练QSM模型，增强彝文生成能力
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import os
import math
from typing import Optional
import time
from tqdm import tqdm

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
    def __init__(self, vocab_path=None):
        if vocab_path and os.path.exists(vocab_path):
            with open(vocab_path, 'r', encoding='utf-8') as f:
                vocab_data = json.load(f)
                self.char_to_id = vocab_data['char_to_id']
        else:
            self.char_to_id = {'<pad>': 0, '‪': 1}
        self.id_to_char = {i: ch for ch, i in self.char_to_id.items()}
        self.unk_token_id = self.char_to_id.get('‪', 0)

    def encode(self, text):
        return [self.char_to_id.get(char, self.unk_token_id) for char in text]

    def decode(self, token_ids):
        return "".join([self.id_to_char.get(token_id, '') for token_id in token_ids])

    @property
    def vocab_size(self):
        return len(self.char_to_id)

    def add_texts(self, texts):
        """Adds new characters from texts to the vocabulary."""
        new_chars = sorted(list(set("".join(texts))))
        for char in new_chars:
            if char not in self.char_to_id:
                self.char_to_id[char] = len(self.char_to_id)
        self.id_to_char = {i: ch for ch, i in self.char_to_id.items()}

    def save_vocab(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({'char_to_id': self.char_to_id}, f, ensure_ascii=False, indent=2)

class YiWenDataset(Dataset):
    def __init__(self, data_file, tokenizer, max_seq_length=256):
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length
        self.examples = []
        
        print(f"Loading Yi Wen training data from {data_file}")
        with open(data_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    if "messages" in data and len(data["messages"]) >= 2:
                        user_msg = data["messages"][0]["content"]
                        assistant_msg = data["messages"][1]["content"]
                        
                        # Create training pairs
                        input_text = f"用户：{user_msg}\n助手："
                        target_text = assistant_msg
                        
                        self.examples.append((input_text, target_text))
                        
                except json.JSONDecodeError:
                    print(f"Warning: Skipping malformed JSON on line {line_num}")
                except Exception as e:
                    print(f"Warning: Error processing line {line_num}: {e}")
        
        print(f"Loaded {len(self.examples)} training examples")

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        input_text, target_text = self.examples[idx]
        
        # Encode input and target
        input_ids = self.tokenizer.encode(input_text)
        target_ids = self.tokenizer.encode(target_text)
        
        # Pad or truncate to max_seq_length
        if len(input_ids) > self.max_seq_length:
            input_ids = input_ids[:self.max_seq_length]
        else:
            input_ids = input_ids + [self.tokenizer.char_to_id.get('<pad>', 0)] * (self.max_seq_length - len(input_ids))
        
        if len(target_ids) > self.max_seq_length:
            target_ids = target_ids[:self.max_seq_length]
        else:
            target_ids = target_ids + [self.tokenizer.char_to_id.get('<pad>', 0)] * (self.max_seq_length - len(target_ids))
        
        return torch.tensor(input_ids, dtype=torch.long), torch.tensor(target_ids, dtype=torch.long)

def train_yi_wen_model():
    # 配置参数
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # 模型参数
    d_model = 256
    nhead = 8
    num_encoder_layers = 3
    dim_feedforward = 1024
    max_seq_length = 256
    batch_size = 16
    learning_rate = 2e-05
    num_epochs = 20
    
    # 数据路径
    data_file = "Models/training_data/datasets/yi_wen/通用彝文汉彝对照训练表(2.0.4.22).jsonl"
    vocab_path = "Models/QSM/bin/vocab.json"
    model_save_path = "Models/QSM/bin/qsm_yi_wen_model.pth"
    vocab_save_path = "Models/QSM/bin/qsm_yi_wen_vocab.json"
    
    # 加载现有词表或创建新词表
    if os.path.exists(vocab_path):
        print(f"Loading existing vocabulary from {vocab_path}")
        tokenizer = SimpleTokenizer(vocab_path)
    else:
        print("Creating new vocabulary")
        tokenizer = SimpleTokenizer()
    
    # 创建数据集
    dataset = YiWenDataset(data_file, tokenizer, max_seq_length)
    
    # 更新词表（添加新字符）
    all_texts = []
    for input_text, target_text in dataset.examples:
        all_texts.append(input_text)
        all_texts.append(target_text)
    tokenizer.add_texts(all_texts)
    
    print(f"Vocabulary size: {tokenizer.vocab_size}")
    
    # 保存更新后的词表
    tokenizer.save_vocab(vocab_save_path)
    print(f"Saved vocabulary to {vocab_save_path}")
    
    # 创建数据加载器
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # 创建模型
    model = QuantumTransformerModel(
        vocab_size=tokenizer.vocab_size,
        d_model=d_model,
        nhead=nhead,
        num_encoder_layers=num_encoder_layers,
        dim_feedforward=dim_feedforward,
        max_seq_length=max_seq_length
    ).to(device)
    
    # 加载现有模型权重（如果存在）
    if os.path.exists("Models/QSM/bin/qsm_model.pth"):
        print("Loading existing model weights")
        try:
            # 先加载到临时模型以获取原始词汇表大小
            temp_model = QuantumTransformerModel(
                vocab_size=6919,  # 原始词汇表大小
                d_model=d_model,
                nhead=nhead,
                num_encoder_layers=num_encoder_layers,
                dim_feedforward=dim_feedforward,
                max_seq_length=max_seq_length
            )
            temp_model.load_state_dict(torch.load("Models/QSM/bin/qsm_model.pth", map_location=device))
            
            # 调整模型大小以匹配新词汇表
            model.resize_embedding_layer(tokenizer.vocab_size)
            
            # 复制权重
            with torch.no_grad():
                # 复制embedding权重
                num_tokens_to_copy = min(6919, tokenizer.vocab_size)
                model.embedding.weight.data[:num_tokens_to_copy, :] = temp_model.embedding.weight.data[:num_tokens_to_copy, :]
                
                # 复制decoder权重
                model.decoder.weight.data[:num_tokens_to_copy, :] = temp_model.decoder.weight.data[:num_tokens_to_copy, :]
                model.decoder.bias.data[:num_tokens_to_copy] = temp_model.decoder.bias.data[:num_tokens_to_copy]
                
                # 复制transformer权重
                for name, param in temp_model.transformer_encoder.named_parameters():
                    if name in dict(model.transformer_encoder.named_parameters()):
                        model.transformer_encoder.get_parameter(name).data.copy_(param.data)
            
            print("Successfully loaded and adapted existing model weights")
            
        except Exception as e:
            print(f"Warning: Could not load existing weights: {e}")
            print("Starting with random initialization")
    
    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.char_to_id.get('<pad>', 0))
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate)
    
    # 训练循环
    print("Starting training...")
    model.train()
    
    for epoch in range(num_epochs):
        total_loss = 0
        progress_bar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{num_epochs}")
        
        for batch_idx, (input_ids, target_ids) in enumerate(progress_bar):
            input_ids = input_ids.to(device)
            target_ids = target_ids.to(device)
            
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(input_ids)
            
            # Reshape outputs for loss calculation
            outputs = outputs.view(-1, tokenizer.vocab_size)
            targets = target_ids.view(-1)
            
            # Calculate loss
            loss = criterion(outputs, targets)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
            # Update progress bar
            progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{num_epochs}, Average Loss: {avg_loss:.4f}")
        
        # 保存模型
        if (epoch + 1) % 5 == 0:
            torch.save(model.state_dict(), model_save_path)
            print(f"Model saved to {model_save_path}")
    
    # 最终保存
    torch.save(model.state_dict(), model_save_path)
    print(f"Training completed. Final model saved to {model_save_path}")
    
    return model, tokenizer

if __name__ == "__main__":
    model, tokenizer = train_yi_wen_model()
    print("Yi Wen QSM model training completed!") 