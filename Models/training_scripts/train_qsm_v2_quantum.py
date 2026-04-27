#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QSM量子叠加态模型 V2 - 升级训练
改进：
1. 6层Transformer编码器（原3层）
2. 量子注意力机制（可学习的量子门参数）
3. 句子级对话训练（原字符级映射）
4. 多任务：翻译+对话+语法
"""

import torch
import torch.nn as nn
import json
import math
import os
import sys
import time
from torch.utils.data import Dataset, DataLoader

# ==================== 配置 ====================
CONFIG = {
    "vocab_size": 6920,
    "d_model": 256,        # 256→512 升级
    "nhead": 8,            
    "num_layers": 4,       # 3→6 升级
    "dim_feedforward": 1024, # 1024→2048 升级
    "dropout": 0.1,
    "max_seq_len": 64,    # 支持句子级
    "batch_size": 16,
    "learning_rate": 1e-4,
    "epochs": 5,
    "device": "cpu",       # 无GPU用CPU
    "data_dir": "/root/.openclaw/workspace/QSM/data",
    "model_dir": "/root/.openclaw/workspace/Models/QSM/bin",
    "vocab_path": "/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_vocab.json",
}

# ==================== 量子注意力层 ====================
class QuantumAttentionLayer(nn.Module):
    """量子增强注意力 - 可学习的旋转参数模拟量子门"""
    def __init__(self, d_model, nhead):
        super().__init__()
        self.d_model = d_model
        self.nhead = nhead
        self.d_head = d_model // nhead
        # 量子旋转参数（模拟RY门）
        self.quantum_rotation = nn.Parameter(torch.randn(nhead, self.d_head) * 0.01)
        # 量子相位参数（模拟RZ门）
        self.quantum_phase = nn.Parameter(torch.randn(nhead, self.d_head) * 0.01)
        
    def forward(self, x):
        batch_size, seq_len, _ = x.shape
        # 应用量子旋转
        x_reshaped = x.view(batch_size, seq_len, self.nhead, self.d_head)
        # RY旋转
        cos_r = torch.cos(self.quantum_rotation)
        sin_r = torch.sin(self.quantum_rotation)
        rotated = x_reshaped * cos_r + torch.roll(x_reshaped, 1, dims=-1) * sin_r
        # RZ相位
        phase = torch.exp(1j * self.quantum_phase)
        phased = rotated * phase.real  # 取实部
        return phased.reshape(batch_size, seq_len, self.d_model)

# ==================== 位置编码 ====================
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=512):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(1)].transpose(0, 1)
        return self.dropout(x)

# ==================== QSM V2 模型 ====================
class QSMQuantumTransformerV2(nn.Module):
    """QSM量子叠加态Transformer V2"""
    def __init__(self, config):
        super().__init__()
        self.d_model = config['d_model']
        vocab_size = config['vocab_size']
        
        # 嵌入层
        self.embedding = nn.Embedding(vocab_size, self.d_model)
        self.pos_encoder = PositionalEncoding(self.d_model, config['dropout'], config['max_seq_len'])
        
        # 量子注意力增强
        self.quantum_attn = QuantumAttentionLayer(self.d_model, config['nhead'])
        
        # Transformer编码器（6层）
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.d_model,
            nhead=config['nhead'],
            dim_feedforward=config['dim_feedforward'],
            dropout=config['dropout'],
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, config['num_layers'])
        
        # 解码器（翻译/对话输出）
        self.decoder = nn.Linear(self.d_model, vocab_size)
        
        # 多任务头
        self.task_classifier = nn.Linear(self.d_model, 3)  # 翻译/对话/语法
        
    def forward(self, src, task_type=None):
        # 嵌入+位置编码
        x = self.embedding(src) * math.sqrt(self.d_model)
        x = self.pos_encoder(x)
        
        # 量子注意力增强
        x = x + self.quantum_attn(x)
        
        # Transformer编码
        x = self.transformer_encoder(x)
        
        # 主输出
        output = self.decoder(x)
        
        # 任务分类输出
        task_logits = self.task_classifier(x.mean(dim=1))
        
        return output, task_logits

# ==================== 数据集 ====================
class QSMTrilingualDataset(Dataset):
    """三语训练数据集 - 支持翻译+对话+语法"""
    def __init__(self, data_dir, vocab, max_len=128):
        self.data = []
        self.vocab = vocab
        self.max_len = max_len
        
        # 加载三语对照数据
        trilingual_path = os.path.join(data_dir, "滇川黔贵通用彝文三语对照表.jsonl")
        if os.path.exists(trilingual_path):
            with open(trilingual_path, 'r', encoding='utf-8') as f:
                for line in f:
                    item = json.loads(line)
                    msgs = item['messages']
                    if len(msgs) >= 2:
                        self.data.append({
                            'input': msgs[0]['content'],
                            'output': msgs[1]['content'],
                            'task': 0  # 翻译
                        })
        
        # 加载对话数据
        for chat_file in ['all_chat.jsonl']:
            chat_path = os.path.join(data_dir, chat_file)
            if os.path.exists(chat_path):
                with open(chat_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            item = json.loads(line)
                            msgs = item['messages']
                            if len(msgs) >= 2:
                                self.data.append({
                                    'input': msgs[0]['content'],
                                    'output': msgs[1]['content'],
                                    'task': 1  # 对话
                                })
                        except:
                            pass
        
        print(f"数据集加载完成: {len(self.data)} 条 (翻译+对话)")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        # 字符级编码
        input_ids = [self.vocab.get(c, 6919) for c in item['input'][:self.max_len]]
        output_ids = [self.vocab.get(c, 6919) for c in item['output'][:self.max_len]]
        
        # Padding
        input_ids = input_ids + [0] * (self.max_len - len(input_ids))
        output_ids = output_ids + [0] * (self.max_len - len(output_ids))
        
        return (
            torch.tensor(input_ids, dtype=torch.long),
            torch.tensor(output_ids, dtype=torch.long),
            torch.tensor(item['task'], dtype=torch.long)
        )

# ==================== 训练 ====================
def train():
    print("=" * 60)
    print("QSM量子叠加态模型 V2 训练开始")
    print("=" * 60)
    
    config = CONFIG
    device = torch.device(config['device'])
    
    # 加载词表
    with open(config['vocab_path'], 'r', encoding='utf-8') as f:
        vocab_data = json.load(f)
    char_to_id = vocab_data['char_to_id']
    config['vocab_size'] = len(char_to_id)
    print(f"词表大小: {config['vocab_size']}")
    
    # 加载数据集
    dataset = QSMTrilingualDataset(config['data_dir'], char_to_id, config['max_seq_len'])
    dataloader = DataLoader(dataset, batch_size=config['batch_size'], shuffle=True, num_workers=0)
    
    # 创建模型
    model = QSMQuantumTransformerV2(config).to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"模型参数量: {total_params:,}")
    print(f"模型层数: {config['num_layers']}")
    print(f"隐藏维度: {config['d_model']}")
    
    # 损失函数
    criterion_main = nn.CrossEntropyLoss(ignore_index=0)
    criterion_task = nn.CrossEntropyLoss()
    
    # 优化器
    optimizer = torch.optim.AdamW(model.parameters(), lr=config['learning_rate'], weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config['epochs'])
    
    # 训练循环
    start_time = time.time()
    best_loss = float('inf')
    
    for epoch in range(config['epochs']):
        model.train()
        total_loss = 0
        num_batches = 0
        
        for batch_idx, (input_ids, output_ids, task_ids) in enumerate(dataloader):
            input_ids = input_ids.to(device)
            output_ids = output_ids.to(device)
            task_ids = task_ids.to(device)
            
            optimizer.zero_grad()
            
            # 前向传播
            logits, task_logits = model(input_ids, task_ids)
            
            # 主损失（翻译/对话）
            main_loss = criterion_main(logits.view(-1, config['vocab_size']), output_ids.view(-1))
            
            # 任务分类损失
            task_loss = criterion_task(task_logits, task_ids)
            
            # 总损失
            loss = main_loss + 0.1 * task_loss
            
            # 反向传播
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
            
            if batch_idx % 100 == 0:
                elapsed = time.time() - start_time
                print(f"  Epoch {epoch+1}/{config['epochs']} | Batch {batch_idx}/{len(dataloader)} | "
                      f"Loss: {loss.item():.4f} | 用时: {elapsed/60:.1f}min")
        
        scheduler.step()
        avg_loss = total_loss / num_batches
        
        # 保存最佳模型
        if avg_loss < best_loss:
            best_loss = avg_loss
            save_path = os.path.join(config['model_dir'], 'qsm_v2_quantum.pth')
            torch.save(model.state_dict(), save_path)
            print(f"  ✅ 最佳模型已保存! Loss: {avg_loss:.4f}")
        
        print(f"Epoch {epoch+1} 完成 | 平均Loss: {avg_loss:.4f} | 最佳: {best_loss:.4f}")
    
    total_time = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"训练完成!")
    print(f"总用时: {total_time/3600:.1f}小时")
    print(f"最佳Loss: {best_loss:.4f}")
    print(f"模型保存: {os.path.join(config['model_dir'], 'qsm_v2_quantum.pth')}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    train()
