#!/usr/bin/env python3
"""
QSM V4 Encoder-Decoder 量子翻译模型训练
真正的翻译模型：Encoder(源语言) → Cross-Attention → Decoder(目标语言)

作者: 小趣WeQ | 监督: 中华Zhoho
日期: 2026-04-28
"""
import torch
import torch.nn as nn
import torch.optim as optim
import json
import math
import os
import sys
import time
import random

# ============================================================
# 模型定义
# ============================================================

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=256):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(max_len).unsqueeze(1).float()
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term[:d_model//2])
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        return self.dropout(x + self.pe[:x.size(1)])


class QuantumGateAttention(nn.Module):
    """门控量子注意力层"""
    def __init__(self, d_model, n_heads=4, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
        # 量子旋转参数（可学习）
        self.quantum_theta = nn.Parameter(torch.randn(n_heads) * 0.1)
        
        # 门控参数
        self.gate = nn.Parameter(torch.randn(d_model) * 0.1)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, query, key, value, mask=None):
        B, S_q, D = query.shape
        S_k = key.size(1)
        
        Q = self.W_q(query).view(B, S_q, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key).view(B, S_k, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).view(B, S_k, self.n_heads, self.d_k).transpose(1, 2)
        
        # 标准注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        # 量子旋转调制
        cos_t = torch.cos(self.quantum_theta).view(1, self.n_heads, 1, 1)
        sin_t = torch.sin(self.quantum_theta).view(1, self.n_heads, 1, 1)
        
        # 旋转Q的第一个维度
        q_rotated = torch.cat([
            cos_t * Q[..., :1] - sin_t * Q[..., 1:2],
            sin_t * Q[..., :1] + cos_t * Q[..., 1:2],
            Q[..., 2:]
        ], dim=-1)
        
        scores_q = torch.matmul(q_rotated, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        # 门控混合: gate * quantum + (1-gate) * classical
        g = torch.sigmoid(self.gate).view(1, 1, 1, self.d_model)  # will be reduced
        g_scalar = torch.sigmoid(self.gate.mean())
        scores = g_scalar * scores_q + (1 - g_scalar) * scores
        
        if mask is not None:
            # mask shape: [B, 1, 1, S_k] or [B, 1, S_q, S_k] or [1, 1, S_q, S_k]
            if mask.dim() == 4 and mask.size(-1) != scores.size(-1):
                # Adjust mask to match scores dimensions
                mask = mask.expand_as(scores)
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attn = torch.softmax(scores, dim=-1)
        attn = self.dropout(attn)
        
        out = torch.matmul(attn, V)
        out = out.transpose(1, 2).contiguous().view(B, S_q, D)
        return self.W_o(out)


class EncoderLayer(nn.Module):
    def __init__(self, d_model, n_heads=4, d_ff=512, dropout=0.1):
        super().__init__()
        self.self_attn = QuantumGateAttention(d_model, n_heads, dropout)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
    
    def forward(self, x, mask=None):
        x = self.norm1(x + self.self_attn(x, x, x, mask))
        x = self.norm2(x + self.ffn(x))
        return x


class DecoderLayer(nn.Module):
    def __init__(self, d_model, n_heads=4, d_ff=512, dropout=0.1):
        super().__init__()
        self.masked_self_attn = QuantumGateAttention(d_model, n_heads, dropout)
        self.cross_attn = QuantumGateAttention(d_model, n_heads, dropout)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
    
    def forward(self, x, enc_output, tgt_mask=None, src_mask=None):
        x = self.norm1(x + self.masked_self_attn(x, x, x, tgt_mask))
        x = self.norm2(x + self.cross_attn(x, enc_output, enc_output, src_mask))
        x = self.norm3(x + self.ffn(x))
        return x


class QSM_V4(nn.Module):
    """QSM V4: Encoder-Decoder量子翻译模型"""
    def __init__(self, vocab_size, d_model=256, n_heads=4, n_layers=3, d_ff=512, 
                 dropout=0.1, max_len=64, pad_id=0):
        super().__init__()
        self.d_model = d_model
        self.pad_id = pad_id
        
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_id)
        self.pos_enc = PositionalEncoding(d_model, dropout, max_len)
        
        # Encoder
        self.encoder_layers = nn.ModuleList([
            EncoderLayer(d_model, n_heads, d_ff, dropout) for _ in range(n_layers)
        ])
        
        # Decoder
        self.decoder_layers = nn.ModuleList([
            DecoderLayer(d_model, n_heads, d_ff, dropout) for _ in range(n_layers)
        ])
        
        # Output projection (share with embedding)
        self.output_proj = nn.Linear(d_model, vocab_size, bias=False)
        # Tie weights
        self.output_proj.weight = self.embedding.weight
        
        self._init_weights()
    
    def _init_weights(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def _make_causal_mask(self, sz):
        mask = torch.triu(torch.ones(sz, sz), diagonal=1).bool()
        return ~mask  # True = allowed, False = masked
    
    def _make_pad_mask(self, x, pad_id=0):
        return (x != pad_id).unsqueeze(1).unsqueeze(2)  # [B, 1, 1, S]
    
    def encode(self, src_ids, src_mask=None):
        x = self.embedding(src_ids) * math.sqrt(self.d_model)
        x = self.pos_enc(x)
        for layer in self.encoder_layers:
            x = layer(x, src_mask)
        return x
    
    def decode(self, tgt_ids, enc_output, tgt_mask=None, src_mask=None):
        x = self.embedding(tgt_ids) * math.sqrt(self.d_model)
        x = self.pos_enc(x)
        for layer in self.decoder_layers:
            x = layer(x, enc_output, tgt_mask, src_mask)
        return self.output_proj(x)
    
    def forward(self, src_ids, tgt_ids):
        B = src_ids.size(0)
        
        # Source padding mask: [B, 1, 1, S_src]
        src_pad_mask = self._make_pad_mask(src_ids, self.pad_id)
        
        # Target causal mask + padding mask
        tgt_len = tgt_ids.size(1)
        # Causal: [tgt_len, tgt_len]
        causal_mask = self._make_causal_mask(tgt_len).to(tgt_ids.device)
        # Pad: [B, 1, 1, tgt_len] -> [B, 1, tgt_len, tgt_len] via broadcast
        tgt_pad_mask = self._make_pad_mask(tgt_ids, self.pad_id)
        # Combine: [1, 1, tgt_len, tgt_len] & [B, 1, 1, tgt_len] -> [B, 1, tgt_len, tgt_len]
        tgt_mask = causal_mask.unsqueeze(0).unsqueeze(0) & tgt_pad_mask
        
        # Encode
        enc_output = self.encode(src_ids, src_pad_mask)
        
        # Decode
        logits = self.decode(tgt_ids, enc_output, tgt_mask, src_pad_mask)
        
        return logits
    

    def translate_beam_search(self, src_ids, beam_size=5, max_len=64, length_penalty=0.6):
        """束搜索翻译 - 比sampling更高质量的解码"""
        self.eval()
        device = next(self.parameters()).device
        
        if isinstance(src_ids, list):
            src_ids = torch.tensor([src_ids], device=device)
        
        src_pad_mask = self._make_pad_mask(src_ids, self.pad_id)
        enc_output = self.encode(src_ids, src_pad_mask)
        
        BOS = 6920
        EOS = 6921
        
        # Initialize beams: list of (score, token_ids)
        beams = [(0.0, [BOS])]
        completed = []
        
        for step in range(max_len):
            new_beams = []
            for score, ids in beams:
                if ids[-1] == EOS:
                    completed.append((score, ids))
                    continue
                
                tgt = torch.tensor([ids], device=device)
                tgt_len = len(ids)
                causal_mask = self._make_causal_mask(tgt_len).to(device)
                
                with torch.no_grad():
                    logits = self.decode(tgt, enc_output, causal_mask, src_pad_mask)
                
                log_probs = torch.log_softmax(logits[:, -1, :], dim=-1).squeeze(0)
                topk_probs, topk_ids = log_probs.topk(beam_size)
                
                for i in range(beam_size):
                    new_id = topk_ids[i].item()
                    new_score = score + topk_probs[i].item()
                    new_beams.append((new_score, ids + [new_id]))
            
            # Keep top beam_size beams
            new_beams.sort(key=lambda x: x[0] / (len(x[1]) ** length_penalty), reverse=True)
            beams = new_beams[:beam_size]
            
            # Early stop if all beams ended
            if all(b[1][-1] == EOS for b in beams):
                completed.extend(beams)
                break
        
        # Add remaining beams to completed
        completed.extend(beams)
        
        # Select best beam with length penalty
        if completed:
            completed.sort(key=lambda x: x[0] / (len(x[1]) ** length_penalty), reverse=True)
            return completed[0][1]
        return [BOS]

    def translate(self, src_ids, max_len=64, temperature=1.0):
        """自回归翻译"""
        self.eval()
        device = next(self.parameters()).device
        
        if isinstance(src_ids, list):
            src_ids = torch.tensor([src_ids], device=device)
        
        src_pad_mask = self._make_pad_mask(src_ids, self.pad_id)
        enc_output = self.encode(src_ids, src_pad_mask)
        
        # BOS token
        BOS = 6920
        EOS = 6921
        
        tgt_ids = torch.tensor([[BOS]], device=device)
        
        for _ in range(max_len):
            tgt_len = tgt_ids.size(1)
            causal_mask = self._make_causal_mask(tgt_len).to(device)
            logits = self.decode(tgt_ids, enc_output, causal_mask, src_pad_mask)
            
            next_logits = logits[:, -1, :] / temperature
            probs = torch.softmax(next_logits, dim=-1)
            next_id = torch.multinomial(probs, 1)
            
            tgt_ids = torch.cat([tgt_ids, next_id], dim=1)
            
            if next_id.item() == EOS:
                break
        
        return tgt_ids[0].tolist()


# ============================================================
# 训练脚本
# ============================================================

def load_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def collate_batch(pairs, pad_id=0, max_len=64):
    src_batch = []
    tgt_batch = []
    for p in pairs:
        src = p['src'][:max_len]
        tgt = p['tgt'][:max_len]
        # Pad to same length within batch
        src_batch.append(src)
        tgt_batch.append(tgt)
    
    # Pad to max length in this batch
    max_src = max(len(s) for s in src_batch)
    max_tgt = max(len(t) for t in tgt_batch)
    
    src_padded = [s + [pad_id] * (max_src - len(s)) for s in src_batch]
    tgt_padded = [t + [pad_id] * (max_tgt - len(t)) for t in tgt_batch]
    
    return torch.tensor(src_padded), torch.tensor(tgt_padded)

def train():
    print("=" * 60)
    print("  QSM V4 Encoder-Decoder 量子翻译模型训练")
    print("  原则: 量子自举 — 用自己的语言构建自己的世界")
    print("=" * 60)
    
    # Config
    d_model = 256
    n_heads = 4
    n_layers = 3
    d_ff = 512
    dropout = 0.1
    batch_size = 8
    epochs = 20
    lr = 3e-4
    accum_steps = 4  # Gradient accumulation
    max_len = 64
    pad_id = 0
    warmup_steps = 1000
    label_smoothing = 0.1
    
    # Load data
    print("\n📂 加载训练数据...")
    train_pairs = load_data('Models/QSM/bin/v4_train_pairs_v2.json')
    val_pairs = load_data('Models/QSM/bin/v4_val_pairs_v2.json')
    
    with open('Models/QSM/bin/v4_vocab.json', 'r', encoding='utf-8') as f:
        vocab = json.load(f)
    vocab_size = len(vocab)
    
    print(f"  词汇表: {vocab_size}")
    print(f"  训练对: {len(train_pairs)}")
    print(f"  验证对: {len(val_pairs)}")
    
    # Model
    device = torch.device('cpu')
    model = QSM_V4(vocab_size, d_model, n_heads, n_layers, d_ff, dropout, max_len, pad_id)
    model = model.to(device)
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"\n🧠 模型参数: {total_params:,} ({total_params/1e6:.1f}M)")
    
    # Optimizer with weight decay
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    
    # Loss with label smoothing
    criterion = nn.CrossEntropyLoss(ignore_index=pad_id, label_smoothing=label_smoothing)
    
    # LR Scheduler: warmup + cosine decay
    total_steps = len(train_pairs) // batch_size * epochs
    def lr_lambda(step):
        if step < warmup_steps:
            return step / warmup_steps
        progress = (step - warmup_steps) / (total_steps - warmup_steps)
        return 0.5 * (1 + math.cos(math.pi * progress))
    
    scheduler = optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
    
    print(f"\n🏋️ 开始训练...")
    print(f"  epochs={epochs}, batch={batch_size}, accum={accum_steps}")
    print(f"  lr={lr}, warmup={warmup_steps}, label_smooth={label_smoothing}")
    print(f"  等效batch={batch_size * accum_steps}")
    print()
    
    best_val_loss = float('inf')
    log_file = '/tmp/qsm_v4_training.log'
    
    for epoch in range(1, epochs + 1):
        model.train()
        random.shuffle(train_pairs)
        
        total_loss = 0
        n_batches = 0
        epoch_start = time.time()
        
        optimizer.zero_grad()
        
        for i in range(0, len(train_pairs), batch_size):
            batch_pairs = train_pairs[i:i+batch_size]
            src, tgt = collate_batch(batch_pairs, pad_id, max_len)
            src, tgt = src.to(device), tgt.to(device)
            
            # Forward: predict tgt[1:] from tgt[:-1]
            tgt_input = tgt[:, :-1]
            tgt_target = tgt[:, 1:]
            
            logits = model(src, tgt_input)
            
            # Reshape for loss
            logits = logits.reshape(-1, vocab_size)
            tgt_target = tgt_target.reshape(-1)
            
            loss = criterion(logits, tgt_target) / accum_steps
            loss.backward()
            
            if (n_batches + 1) % accum_steps == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
            
            total_loss += loss.item() * accum_steps
            n_batches += 1
            
            if n_batches % 200 == 0:
                avg = total_loss / n_batches
                lr_now = scheduler.get_last_lr()[0]
                elapsed = (time.time() - epoch_start) / 60
                log = f"E{epoch}/{epochs} B{n_batches}/{len(train_pairs)//batch_size} L:{avg:.4f} lr:{lr_now:.6f} T:{elapsed:.1f}m"
                print(log, flush=True)
                with open(log_file, 'a') as f:
                    f.write(log + '\n')
        
        # Validation
        model.eval()
        val_loss = 0
        val_batches = 0
        with torch.no_grad():
            for i in range(0, len(val_pairs), batch_size):
                batch_pairs = val_pairs[i:i+batch_size]
                src, tgt = collate_batch(batch_pairs, pad_id, max_len)
                src, tgt = src.to(device), tgt.to(device)
                
                tgt_input = tgt[:, :-1]
                tgt_target = tgt[:, 1:]
                
                logits = model(src, tgt_input)
                logits = logits.reshape(-1, vocab_size)
                tgt_target = tgt_target.reshape(-1)
                
                val_loss += criterion(logits, tgt_target).item()
                val_batches += 1
        
        avg_val = val_loss / max(val_batches, 1)
        avg_train = total_loss / max(n_batches, 1)
        
        is_best = avg_val < best_val_loss
        if is_best:
            best_val_loss = avg_val
        
        log = f"✅{'Best!' if is_best else ''} Epoch {epoch} | Train:{avg_train:.4f} | Val:{avg_val:.4f} | Best:{best_val_loss:.4f}"
        print(log, flush=True)
        with open(log_file, 'a') as f:
            f.write(log + '\n')
        
        # Save checkpoint
        if is_best or epoch % 5 == 0:
            save_path = f'Models/QSM/bin/qsm_v4_quantum{"_best" if is_best else f"_e{epoch}"}.pth'
            torch.save({
                'epoch': epoch,
                'model_state': model.state_dict(),
                'optimizer_state': optimizer.state_dict(),
                'val_loss': avg_val,
                'train_loss': avg_train,
                'config': {
                    'vocab_size': vocab_size,
                    'd_model': d_model,
                    'n_heads': n_heads,
                    'n_layers': n_layers,
                    'd_ff': d_ff,
                }
            }, save_path)
            print(f"  💾 模型保存: {save_path}")
    
    print("\n🎉 V4训练完成!")
    return model

if __name__ == '__main__':
    train()
