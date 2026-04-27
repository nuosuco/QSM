#!/usr/bin/env python3
"""
优化版彝文训练脚本
目标：将准确率从90%提升到95%+
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import csv
import time

# 配置
CONFIG = {
    'vocab_path': '/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_vocab_v2.json',
    'data_path': '/root/.openclaw/workspace/QSM/model/train/data/yi_training_data.csv',
    'model_path': '/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_model_v4.pth',
    'output_path': '/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_model_v6.pth',
    'embedding_dim': 128,
    'hidden_dim': 512,
    'epochs': 100,
    'batch_size': 64,
    'learning_rate': 0.0001,
    'dropout': 0.3,
}

class ImprovedTranslator(nn.Module):
    """改进版翻译模型"""
    def __init__(self, vocab_size, embedding_dim, hidden_dim, dropout=0.3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.dropout = nn.Dropout(dropout)
        
        # 编码器
        self.encoder = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
        )
        
        # 解码器
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, vocab_size),
        )
        
    def forward(self, x):
        x = self.embedding(x)
        x = torch.mean(x, dim=1)
        x = self.dropout(x)
        encoded = self.encoder(x)
        output = self.decoder(encoded)
        return output

def train_optimized():
    """训练优化模型"""
    # 加载词汇表
    with open(CONFIG['vocab_path'], 'r', encoding='utf-8') as f:
        vocab = json.load(f)
    char_to_id = vocab['char_to_id']
    vocab_size = len(char_to_id)
    
    # 加载模型
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ImprovedTranslator(vocab_size, CONFIG['embedding_dim'], CONFIG['hidden_dim'], CONFIG['dropout'])
    
    # 加载V4预训练权重
    try:
        model.load_state_dict(torch.load(CONFIG['model_path'], map_location=device))
        print("✓ 加载V4预训练权重成功")
    except:
        print("! 使用新初始化权重")
    
    model = model.to(device)
    
    # 加载数据
    data = []
    with open(CONFIG['data_path'], 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            zh = row.get('chinese', '')
            yi = row.get('yi_char', '')
            if zh and yi:
                data.append((zh, yi))
    
    print(f"✓ 加载数据: {len(data)}条")
    
    # 准备训练数据
    X, y = [], []
    for zh, yi in data:
        zh_ids = [char_to_id.get(c, 1) for c in zh][:32]
        zh_ids = zh_ids + [0] * (32 - len(zh_ids))
        X.append(zh_ids)
        
        yi_char = yi[0] if yi else ''
        y.append(char_to_id.get(yi_char, 0))
    
    X = torch.tensor(X, dtype=torch.long)
    y = torch.tensor(y, dtype=torch.long)
    
    # 训练
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=CONFIG['learning_rate'])
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    
    best_acc = 0.90
    batch_size = CONFIG['batch_size']
    
    print(f"\n开始训练，目标准确率: 95%+")
    print(f"设备: {device}")
    print(f"数据: {len(data)}条")
    print()
    
    for epoch in range(CONFIG['epochs']):
        model.train()
        total_loss = 0
        
        # 随机打乱
        perm = torch.randperm(len(X))
        X_shuffled = X[perm]
        y_shuffled = y[perm]
        
        for i in range(0, len(X), batch_size):
            batch_X = X_shuffled[i:i+batch_size].to(device)
            batch_y = y_shuffled[i:i+batch_size].to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        # 验证
        model.eval()
        with torch.no_grad():
            outputs = model(X.to(device))
            _, predicted = torch.max(outputs, 1)
            correct = (predicted == y.to(device)).sum().item()
            acc = correct / len(y) * 100
        
        scheduler.step(total_loss / len(X))
        
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), CONFIG['output_path'])
            print(f"Epoch {epoch+1}: Loss={total_loss/len(X):.4f}, Acc={acc:.2f}% ✓ 新最佳!")
        elif epoch % 10 == 0:
            print(f"Epoch {epoch+1}: Loss={total_loss/len(X):.4f}, Acc={acc:.2f}%")
        
        if acc >= 95.0:
            print(f"\n🎉 达成目标！准确率: {acc:.2f}%")
            break
    
    print(f"\n训练完成！最佳准确率: {best_acc:.2f}%")
    return best_acc

if __name__ == '__main__':
    train_optimized()
