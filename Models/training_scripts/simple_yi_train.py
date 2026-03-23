#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版彝文训练脚本 - 无tqdm依赖
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import os
import math
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

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)

class QuantumTransformerModel(nn.Module):
    def __init__(self, vocab_size: int, d_model: int, nhead: int, num_encoder_layers: int,
                 dim_feedforward: int, dropout: float = 0.1, max_seq_length: int = 8192):
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

    def forward(self, src: torch.Tensor, src_mask = None) -> torch.Tensor:
        src = self.embedding(src) * math.sqrt(self.d_model)
        src = src.transpose(0, 1)
        src = self.pos_encoder(src)
        src = src.transpose(0, 1)
        output = self.transformer_encoder(src, src_mask)
        output = self.decoder(output)
        return output

class SimpleTokenizer:
    def __init__(self, vocab_path=None):
        if vocab_path and os.path.exists(vocab_path):
            with open(vocab_path, 'r', encoding='utf-8') as f:
                vocab_data = json.load(f)
            self.char_to_id = vocab_data['char_to_id']
        else:
            self.char_to_id = {'<pad>': 0, '<unk>': 1}
        self.id_to_char = {i: ch for ch, i in self.char_to_id.items()}
        self.unk_token_id = self.char_to_id.get('<unk>', 0)

    def encode(self, text):
        return [self.char_to_id.get(char, self.unk_token_id) for char in text]

    def decode(self, token_ids):
        return "".join([self.id_to_char.get(token_id, '') for token_id in token_ids])

    @property
    def vocab_size(self):
        return len(self.char_to_id)

    def add_texts(self, texts):
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
        print(f"[{datetime.now()}] Loading data from {data_file}")
        with open(data_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    if "messages" in data and len(data["messages"]) >= 2:
                        user_msg = data["messages"][0]["content"]
                        assistant_msg = data["messages"][1]["content"]
                        input_text = f"用户：{user_msg}\n助手："
                        target_text = assistant_msg
                        self.examples.append((input_text, target_text))
                except Exception as e:
                    pass
        print(f"[{datetime.now()}] Loaded {len(self.examples)} examples")

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        input_text, target_text = self.examples[idx]
        input_ids = self.tokenizer.encode(input_text)
        target_ids = self.tokenizer.encode(target_text)
        if len(input_ids) > self.max_seq_length:
            input_ids = input_ids[:self.max_seq_length]
        else:
            input_ids = input_ids + [self.tokenizer.char_to_id.get('<pad>', 0)] * (self.max_seq_length - len(input_ids))
        if len(target_ids) > self.max_seq_length:
            target_ids = target_ids[:self.max_seq_length]
        else:
            target_ids = target_ids + [self.tokenizer.char_to_id.get('<pad>', 0)] * (self.max_seq_length - len(target_ids))
        return torch.tensor(input_ids, dtype=torch.long), torch.tensor(target_ids, dtype=torch.long)

def main():
    print(f"\n{'='*60}")
    print(f"[{datetime.now()}] 滇川黔桂彝文训练启动")
    print(f"{'='*60}\n")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[{datetime.now()}] Using device: {device}")

    # 参数配置
    d_model = 256
    nhead = 8
    num_encoder_layers = 3
    dim_feedforward = 1024
    max_seq_length = 256
    batch_size = 16
    learning_rate = 2e-05
    num_epochs = 20

    data_file = "/root/QSM/Models/training_data/datasets/yi_wen/通用彝文汉彝对照训练表(2.0.4.22).jsonl"
    vocab_path = "/root/QSM/Models/QSM/bin/vocab.json"
    model_save_path = "/root/QSM/Models/QSM/bin/qsm_yi_wen_trained.pth"
    vocab_save_path = "/root/QSM/Models/QSM/bin/qsm_yi_wen_vocab.json"

    # 加载词表
    if os.path.exists(vocab_path):
        print(f"[{datetime.now()}] Loading vocabulary from {vocab_path}")
        tokenizer = SimpleTokenizer(vocab_path)
    else:
        print(f"[{datetime.now()}] Creating new vocabulary")
        tokenizer = SimpleTokenizer()

    # 创建数据集
    dataset = YiWenDataset(data_file, tokenizer, max_seq_length)

    # 更新词表
    all_texts = []
    for input_text, target_text in dataset.examples:
        all_texts.append(input_text)
        all_texts.append(target_text)
    tokenizer.add_texts(all_texts)
    print(f"[{datetime.now()}] Vocabulary size: {tokenizer.vocab_size}")
    tokenizer.save_vocab(vocab_save_path)

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

    # 加载现有权重
    existing_model_path = "/root/QSM/Models/QSM/bin/qsm_model.pth"
    if os.path.exists(existing_model_path):
        print(f"[{datetime.now()}] Loading existing weights from {existing_model_path}")
        try:
            state_dict = torch.load(existing_model_path, map_location=device)
            # 适配词表大小变化
            if 'embedding.weight' in state_dict:
                old_vocab_size = state_dict['embedding.weight'].shape[0]
                print(f"[{datetime.now()}] Old vocab size: {old_vocab_size}, New: {tokenizer.vocab_size}")
                if old_vocab_size != tokenizer.vocab_size:
                    # 调整embedding层大小
                    new_embedding = nn.Embedding(tokenizer.vocab_size, d_model)
                    new_decoder = nn.Linear(d_model, tokenizer.vocab_size)
                    with torch.no_grad():
                        num_to_copy = min(old_vocab_size, tokenizer.vocab_size)
                        new_embedding.weight.data[:num_to_copy] = state_dict['embedding.weight'][:num_to_copy]
                        new_decoder.weight.data[:num_to_copy] = state_dict['decoder.weight'][:num_to_copy]
                        new_decoder.bias.data[:num_to_copy] = state_dict['decoder.bias'][:num_to_copy]
                    state_dict['embedding.weight'] = new_embedding.weight.data
                    state_dict['decoder.weight'] = new_decoder.weight.data
                    state_dict['decoder.bias'] = new_decoder.bias.data
            model.load_state_dict(state_dict, strict=False)
            print(f"[{datetime.now()}] Weights loaded successfully")
        except Exception as e:
            print(f"[{datetime.now()}] Warning: Could not load weights: {e}")

    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.char_to_id.get('<pad>', 0))
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate)

    # 训练循环
    print(f"\n[{datetime.now()}] Starting training...")
    model.train()

    for epoch in range(num_epochs):
        total_loss = 0
        num_batches = len(dataloader)

        for batch_idx, (input_ids, target_ids) in enumerate(dataloader):
            input_ids = input_ids.to(device)
            target_ids = target_ids.to(device)

            optimizer.zero_grad()
            outputs = model(input_ids)
            outputs = outputs.view(-1, tokenizer.vocab_size)
            targets = target_ids.view(-1)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            if batch_idx % 50 == 0:
                print(f"[{datetime.now()}] Epoch {epoch+1}/{num_epochs}, Batch {batch_idx}/{num_batches}, Loss: {loss.item():.4f}")

        avg_loss = total_loss / num_batches
        print(f"[{datetime.now()}] === Epoch {epoch+1}/{num_epochs} Complete, Avg Loss: {avg_loss:.4f} ===")

        # 每5个epoch保存一次
        if (epoch + 1) % 5 == 0:
            torch.save(model.state_dict(), model_save_path)
            print(f"[{datetime.now()}] Model saved to {model_save_path}")

    # 最终保存
    torch.save(model.state_dict(), model_save_path)
    print(f"\n[{datetime.now()}] Training completed!")
    print(f"[{datetime.now()}] Final model saved to {model_save_path}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
