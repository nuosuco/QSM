#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""极轻量级彝文训练脚本 - 适合小内存环境"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import os
import math
from datetime import datetime

# 强制释放内存
import gc
gc.collect()
torch.cuda.empty_cache() if torch.cuda.is_available() else None

class MiniTransformer(nn.Module):
    """极简Transformer模型"""
    def __init__(self, vocab_size, d_model=128, nhead=4, num_layers=2, dim_ff=256, max_len=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Parameter(torch.zeros(1, max_len, d_model))
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead, dim_ff, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.output = nn.Linear(d_model, vocab_size)
        self.d_model = d_model

    def forward(self, x):
        x = self.embedding(x) * math.sqrt(self.d_model)
        x = x + self.pos_emb[:, :x.size(1), :]
        x = self.transformer(x)
        return self.output(x)

class SimpleTokenizer:
    def __init__(self, vocab_path=None):
        if vocab_path and os.path.exists(vocab_path):
            with open(vocab_path, 'r', encoding='utf-8') as f:
                self.char_to_id = json.load(f)['char_to_id']
        else:
            self.char_to_id = {'<pad>': 0, '<unk>': 1}
        self.id_to_char = {i: ch for ch, i in self.char_to_id.items()}

    def encode(self, text):
        return [self.char_to_id.get(c, 1) for c in text]

    @property
    def vocab_size(self):
        return len(self.char_to_id)

    def add_texts(self, texts):
        for c in set(''.join(texts)):
            if c not in self.char_to_id:
                self.char_to_id[c] = len(self.char_to_id)
        self.id_to_char = {i: ch for ch, i in self.char_to_id.items()}

    def save(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'char_to_id': self.char_to_id}, f, ensure_ascii=False)

class QuickDataset(Dataset):
    def __init__(self, path, tokenizer, max_len=64):
        self.examples = []
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    d = json.loads(line)
                    if 'messages' in d and len(d['messages']) >= 2:
                        inp = d['messages'][0]['content']
                        out = d['messages'][1]['content']
                        self.examples.append((inp[:max_len], out[:max_len]))
                except:
                    pass
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Loaded: {len(self.examples)} samples")
        self.tok = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, i):
        inp, out = self.examples[i]
        inp_ids = self.tok.encode(inp)[:self.max_len]
        out_ids = self.tok.encode(out)[:self.max_len]
        # Pad
        inp_ids += [0] * (self.max_len - len(inp_ids))
        out_ids += [0] * (self.max_len - len(out_ids))
        return torch.tensor(inp_ids), torch.tensor(out_ids)

def train():
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 轻量级彝文训练启动")
    print(f"{'='*50}\n")

    device = torch.device('cpu')
    vocab_path = '/root/QSM/Models/QSM/bin/qsm_yi_wen_vocab.json'
    data_path = '/root/QSM/Models/training_data/datasets/yi_wen/通用彝文汉彝对照训练表(2.0.4.22).jsonl'
    save_path = '/root/QSM/Models/QSM/bin/qsm_yi_light.pth'

    # 加载已生成的词表
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading vocab...")
    tokenizer = SimpleTokenizer(vocab_path)
    vocab_size = tokenizer.vocab_size
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Vocab size: {vocab_size}")

    # 数据集 - 使用更小的batch
    dataset = QuickDataset(data_path, tokenizer, max_len=64)
    loader = DataLoader(dataset, batch_size=4, shuffle=True)  # 极小batch

    # 极小模型
    model = MiniTransformer(vocab_size, d_model=64, nhead=2, num_layers=1, dim_ff=128, max_len=64)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Model params: {sum(p.numel() for p in model.parameters()):,}")

    criterion = nn.CrossEntropyLoss(ignore_index=0)
    optimizer = optim.AdamW(model.parameters(), lr=1e-4)

    # 训练 - 只跑5个epoch作为验证
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting training (5 epochs)...")
    model.train()

    for epoch in range(5):
        total_loss = 0
        for i, (inp, out) in enumerate(loader):
            optimizer.zero_grad()
            logits = model(inp)
            loss = criterion(logits.view(-1, vocab_size), out.view(-1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            if i % 100 == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] E{epoch+1} B{i} L:{loss.item():.4f}")
            gc.collect()  # 每批次后清理

        avg = total_loss / len(loader)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] === Epoch {epoch+1} Avg Loss: {avg:.4f} ===")

    torch.save(model.state_dict(), save_path)
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Training complete! Saved to: {save_path}")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    train()
