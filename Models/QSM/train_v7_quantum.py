#!/usr/bin/env python3
"""QSM V7 量子叠加态模型训练脚本
改进: 256d/4层/4头 + gradient accumulation + 语言控制BOS + beam search解码
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import json
import math
import os
import sys
import time
import argparse
from collections import Counter

# === 量子嵌入 (4基态叠加) ===
class QuantumEmbeddingV2(nn.Module):
    """V2: 语言感知量子嵌入 - 基态初始化带语言偏置"""
    def __init__(self, vocab_size, d_model, n_bases=4):
        super().__init__()
        self.d_model = d_model
        self.base_embed = nn.Embedding(n_bases, d_model)
        self.coeff = nn.Embedding(vocab_size, n_bases)
        # 语言偏置: zh/yi/en/special
        self.lang_bias = nn.Parameter(torch.zeros(4, d_model))
        nn.init.xavier_uniform_(self.coeff.weight)
    
    def forward(self, x, lang_id=None):
        coeff = F.softmax(self.coeff(x), dim=-1)
        bases = self.base_embed.weight + self.lang_bias
        out = torch.matmul(coeff, bases) * math.sqrt(self.d_model)
        if lang_id is not None:
            out = out + self.lang_bias[lang_id] * 0.1
        return out

# === QMoE (量子混合专家) ===
class QMoELayer(nn.Module):
    """4专家路由层 - 基于量子嵌入路由"""
    def __init__(self, d_model, n_heads, d_ff, dropout=0.2, n_experts=4, top_k=2):
        super().__init__()
        self.n_experts = n_experts
        self.top_k = top_k
        self.experts = nn.ModuleList([
            nn.TransformerEncoderLayer(d_model, n_heads, d_ff, dropout, batch_first=True)
            for _ in range(n_experts)
        ])
        self.gate = nn.Linear(d_model, n_experts)
    
    def forward(self, x, src_key_padding_mask=None):
        B, S, D = x.shape
        gate_logits = self.gate(x.mean(dim=1))  # [B, n_experts]
        top_k_indices = gate_logits.topk(self.top_k, dim=-1).indices  # [B, top_k]
        
        # Run all experts (simple approach for CPU)
        expert_outputs = []
        for expert in self.experts:
            expert_outputs.append(expert(x, src_key_padding_mask=src_key_padding_mask))
        
        # Weighted combination of top-k experts
        gate_weights = F.softmax(gate_logits, dim=-1)
        output = torch.zeros_like(x)
        for b in range(B):
            for k_idx in top_k_indices[b]:
                w = gate_weights[b, k_idx]
                output[b] += w * expert_outputs[k_idx][b]
        
        return output

# === QSM V7 模型 ===
class QSM_V7(nn.Module):
    def __init__(self, vocab_size, d_model=256, n_heads=4, n_layers=4, 
                 d_ff=1024, dropout=0.2, max_len=64, use_qmoe=False):
        super().__init__()
        self.d_model = d_model
        self.embedding = QuantumEmbeddingV2(vocab_size, d_model)
        self.pos_encoding = nn.Embedding(max_len, d_model)
        
        # Encoder with optional QMoE
        if use_qmoe:
            self.encoder = nn.ModuleList([
                QMoELayer(d_model, n_heads, d_ff, dropout) for _ in range(n_layers)
            ])
            self.encoder_type = 'qmoe'
        else:
            enc_layer = nn.TransformerEncoderLayer(d_model, n_heads, d_ff, dropout, batch_first=True)
            self.encoder = nn.TransformerEncoder(enc_layer, n_layers)
            self.encoder_type = 'standard'
        
        # Decoder
        dec_layer = nn.TransformerDecoderLayer(d_model, n_heads, d_ff, dropout, batch_first=True)
        self.decoder = nn.TransformerDecoder(dec_layer, n_layers)
        
        # 门控量子注意力
        self.quantum_gate = nn.Parameter(torch.ones(1) * 0.3)
        self.quantum_rotation = nn.Parameter(torch.randn(n_heads, d_model // n_heads) * 0.01)
        self.norm = nn.LayerNorm(d_model)
        self.output_proj = nn.Linear(d_model, vocab_size)
        
        # 语言控制BOS
        self.lang_bos = None  # Set during training
        
        self._init_weights()
    
    def _init_weights(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def forward(self, src, tgt, src_key_padding_mask=None, tgt_key_padding_mask=None, lang_id=None):
        src_emb = self.embedding(src, lang_id) + self.pos_encoding(torch.arange(src.size(1), device=src.device))
        
        # Encoder
        if self.encoder_type == 'qmoe':
            enc_out = src_emb
            for layer in self.encoder:
                enc_out = layer(enc_out, src_key_padding_mask=src_key_padding_mask)
        else:
            enc_out = self.encoder(src_emb, src_key_padding_mask=src_key_padding_mask)
        
        # 门控量子混合
        B, S, _ = enc_out.shape
        nh, dh = self.quantum_rotation.shape
        enc_view = enc_out.view(B, S, nh, dh)
        qr = self.quantum_rotation
        quantum_out = (enc_view * torch.cos(qr) + torch.roll(enc_view, 1, -1) * torch.sin(qr)).reshape(B, S, -1)
        enc_out = self.quantum_gate * quantum_out + (1 - self.quantum_gate) * enc_out
        
        # Decoder
        tgt_emb = self.embedding(tgt, lang_id) + self.pos_encoding(torch.arange(tgt.size(1), device=tgt.device))
        tgt_mask = nn.Transformer.generate_square_subsequent_mask(tgt.size(1), device=tgt.device)
        dec_out = self.decoder(tgt_emb, enc_out, tgt_mask=tgt_mask, tgt_key_padding_mask=tgt_key_padding_mask)
        
        return self.output_proj(self.norm(dec_out))

# === Beam Search Decoder ===
def beam_search_decode(model, src, stoi, itos, beam_width=5, max_len=50,
                       length_penalty_alpha=0.6, rep_penalty=1.2, device='cpu'):
    """Beam search with length penalty and repetition penalty"""
    bos_id = stoi.get('<bos>', 1)
    eos_id = stoi.get('<eos>', 2)
    
    model.eval()
    with torch.no_grad():
        # Encode source
        src_emb = model.embedding(src) + model.pos_encoding(torch.arange(src.size(1), device=device))
        if model.encoder_type == 'qmoe':
            enc_out = src_emb
            for layer in model.encoder:
                enc_out = layer(enc_out)
        else:
            enc_out = model.encoder(src_emb)
        
        B, S, _ = enc_out.shape
        nh, dh = model.quantum_rotation.shape
        enc_view = enc_out.view(B, S, nh, dh)
        qr = model.quantum_rotation
        quantum_out = (enc_view * torch.cos(qr) + torch.roll(enc_view, 1, -1) * torch.sin(qr)).reshape(B, S, -1)
        enc_out = model.quantum_gate * quantum_out + (1 - model.quantum_gate) * enc_out
        
        # Initialize beams: (score, token_ids)
        beams = [(0.0, [bos_id])]
        
        for step in range(max_len):
            candidates = []
            for score, seq in beams:
                if seq[-1] == eos_id and len(seq) > 1:
                    candidates.append((score, seq))
                    continue
                
                tgt_tensor = torch.tensor([seq], dtype=torch.long, device=device)
                tgt_emb = model.embedding(tgt_tensor) + model.pos_encoding(torch.arange(len(seq), device=device))
                tgt_mask = nn.Transformer.generate_square_subsequent_mask(len(seq), device=device)
                dec_out = model.decoder(tgt_emb, enc_out, tgt_mask=tgt_mask)
                logits = model.output_proj(model.norm(dec_out))[0, -1]
                
                # Repetition penalty
                prev_ids = set(seq)
                for pid in prev_ids:
                    if logits[pid] > 0:
                        logits[pid] /= rep_penalty
                    else:
                        logits[pid] *= rep_penalty
                
                # Top-k candidates
                top_k = torch.topk(logits, min(beam_width, logits.size(0)))
                for i in range(top_k.indices.size(0)):
                    new_id = top_k.indices[i].item()
                    new_score = score + top_k.values[i].item()
                    candidates.append((new_score, seq + [new_id]))
            
            # Length-normalized scoring
            def len_norm_score(item):
                s, seq = item
                lp = ((5 + len(seq)) / 6) ** length_penalty_alpha
                return s / lp
            
            beams = sorted(candidates, key=len_norm_score, reverse=True)[:beam_width]
            
            if all(seq[-1] == eos_id for _, seq in beams if len(seq) > 1):
                break
        
        # Return best beam
        best = max(beams, key=lambda x: len_norm_score(x))
        return best[1][1:]  # Remove BOS

def decode_ids(ids, itos):
    result = []
    for id in ids:
        if id in itos:
            ch = itos[id]
            if ch == '<eos>': break
            if ch in ['<pad>', '<unk>', '<bos>']: continue
            result.append(ch)
    return ''.join(result)

# === 数据加载 ===
def load_data(path, max_len=128):
    """Load training data from JSON"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pairs = []
    for item in data:
        inp = item.get('input', '')
        out = item.get('output', '')
        if inp and out and len(inp) <= max_len and len(out) <= max_len:
            pairs.append((inp, out))
    return pairs

def build_vocab(data, min_freq=1):
    """Build character-level vocabulary"""
    counter = Counter()
    for inp, out in data:
        for ch in inp + out:
            counter[ch] += 1
    
    # Special tokens
    vocab = {'<pad>': 0, '<bos>': 1, '<eos>': 2, '<unk>': 3}
    idx = 4
    for ch, freq in counter.most_common():
        if freq >= min_freq and ch not in vocab:
            vocab[ch] = idx
            idx += 1
    
    return vocab

def encode_text(text, stoi, max_len):
    ids = [stoi.get(ch, stoi.get('<unk>', 3)) for ch in text]
    ids = ids[:max_len]
    return ids

# === 训练循环 ===
def train():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='Models/QSM/bin/v7_full_dataset.json')
    parser.add_argument('--vocab', type=str, default='Models/QSM/bin/v4_vocab.json')
    parser.add_argument('--d_model', type=int, default=256)
    parser.add_argument('--n_heads', type=int, default=4)
    parser.add_argument('--n_layers', type=int, default=4)
    parser.add_argument('--d_ff', type=int, default=1024)
    parser.add_argument('--dropout', type=float, default=0.2)
    parser.add_argument('--batch_size', type=int, default=4)
    parser.add_argument('--accum_steps', type=int, default=4)
    parser.add_argument('--epochs', type=int, default=30)
    parser.add_argument('--lr', type=float, default=5e-4)
    parser.add_argument('--warmup', type=int, default=500)
    parser.add_argument('--max_len', type=int, default=64)
    parser.add_argument('--resume', type=str, default=None)
    parser.add_argument('--output_dir', type=str, default='Models/QSM/bin')
    parser.add_argument('--label_smoothing', type=float, default=0.15)
    parser.add_argument('--weight_decay', type=float, default=0.05)
    parser.add_argument('--use_qmoe', action='store_true')
    parser.add_argument('--val_interval', type=int, default=1, help='validate every N epochs')
    parser.add_argument('--lora', type=int, default=0, help='LoRA rank (0=disabled, 8/16=enabled)')
    parser.add_argument('--lora_alpha', type=int, default=16, help='LoRA alpha scaling')
    parser.add_argument('--curriculum', action='store_true', help='enable curriculum learning (difficulty-based)')
    parser.add_argument('--max_difficulty', type=int, default=4, help='max difficulty level (1-4)')
    parser.add_argument('--difficulty_schedule', type=str, default='10,30,70,100',
                        help='epochs to increase difficulty (comma-separated)')
    args = parser.parse_args()
    
    device = torch.device('cpu')
    print(f"QSM V7 Training")
    print(f"Config: d={args.d_model}, heads={args.n_heads}, layers={args.n_layers}, ff={args.d_ff}")
    print(f"Batch: {args.batch_size}x{args.accum_steps}={args.batch_size*args.accum_steps} effective")
    
    # Load vocab
    with open(args.vocab, 'r') as f:
        stoi = json.load(f)
    itos = {v: k for k, v in stoi.items()}
    vocab_size = len(stoi)
    print(f"Vocab size: {vocab_size}")
    
    # Load data
    data = load_data(args.data)
    print(f"Training data: {len(data)} pairs")
    
    # Split train/val
    import random
    random.shuffle(data)
    val_size = max(100, len(data) // 20)
    val_data = data[:val_size]
    train_data = data[val_size:]
    print(f"Train: {len(train_data)}, Val: {len(val_data)}")
    
    # Create model
    model = QSM_V7(
        vocab_size=vocab_size,
        d_model=args.d_model,
        n_heads=args.n_heads,
        n_layers=args.n_layers,
        d_ff=args.d_ff,
        dropout=args.dropout,
        max_len=args.max_len,
        use_qmoe=args.use_qmoe
    ).to(device)
    
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {n_params:,}")
    
    # Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    criterion = nn.CrossEntropyLoss(ignore_index=0, label_smoothing=args.label_smoothing)
    
    # Resume
    start_epoch = 0
    best_val = float('inf')
    global_step = 0
    
    if args.resume:
        ckpt = torch.load(args.resume, map_location=device, weights_only=False)
        model.load_state_dict(ckpt['model_state'])
        optimizer.load_state_dict(ckpt['optimizer_state'])
        start_epoch = ckpt.get('epoch', 0) + 1
        best_val = ckpt.get('best_val', float('inf'))
        global_step = ckpt.get('global_step', 0)
        print(f"Resumed from epoch {start_epoch}, best_val={best_val:.4f}")
    
    # Training
    pad_id = 0
    bos_id = stoi.get('<bos>', 1)
    eos_id = stoi.get('<eos>', 2)
    log_file = '/tmp/qsm_v7_training.log'
    
    for epoch in range(start_epoch, args.epochs):
        model.train()
        total_loss = 0
        n_batches = 0
        epoch_start = time.time()
        
        # Shuffle
        random.shuffle(epoch_train)
        
        for batch_i in range(0, len(epoch_train), args.batch_size):
            batch = epoch_train[batch_i:batch_i+args.batch_size]
            if len(batch) < 2:
                continue
            
            # Prepare batch
            src_ids = []
            tgt_ids = []
            for inp, out in batch:
                s = encode_text(inp, stoi, args.max_len)
                t = [bos_id] + encode_text(out, stoi, args.max_len - 1) + [eos_id]
                src_ids.append(s)
                tgt_ids.append(t)
            
            # Pad
            max_src = max(len(s) for s in src_ids)
            max_tgt = max(len(t) for t in tgt_ids)
            src_pad = [s + [pad_id] * (max_src - len(s)) for s in src_ids]
            tgt_pad = [t + [pad_id] * (max_tgt - len(t)) for t in tgt_ids]
            
            src_tensor = torch.tensor(src_pad, dtype=torch.long, device=device)
            tgt_tensor = torch.tensor(tgt_pad, dtype=torch.long, device=device)
            
            # Forward
            out = model(src_tensor, tgt_tensor[:, :-1])
            
            # Loss
            loss = criterion(out.reshape(-1, vocab_size), tgt_tensor[:, 1:].reshape(-1))
            loss = loss / args.accum_steps
            loss.backward()
            
            # Gradient accumulation
            if (batch_i // args.batch_size + 1) % args.accum_steps == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                
                # Manual LR with warmup + decay
                if global_step < args.warmup:
                    lr = args.lr * (global_step + 1) / args.warmup
                else:
                    lr = args.lr * (0.85 ** (global_step // (len(epoch_train) // args.batch_size)))
                
                for pg in optimizer.param_groups:
                    pg['lr'] = lr
                
                optimizer.step()
                optimizer.zero_grad()
                global_step += 1
            
            total_loss += loss.item() * args.accum_steps
            n_batches += 1
            
            # Log progress
            if n_batches % 200 == 0:
                elapsed = time.time() - epoch_start
                log_line = f"E{epoch+1}/{args.epochs} B{n_batches} L:{loss.item()*args.accum_steps:.4f} lr:{optimizer.param_groups[0]['lr']:.6f} T:{elapsed/60:.1f}m"
                print(log_line, flush=True)
                with open(log_file, 'a') as f:
                    f.write(log_line + '\n')
        
        # Validation (skip if not val_interval)
        if (epoch + 1) % args.val_interval != 0 and epoch + 1 != args.epochs:
            avg_train = total_loss / max(n_batches, 1)
            log_line = f"Epoch {epoch+1} | Train:{avg_train:.4f} | (val skipped) | T:{(time.time() - epoch_start)/60:.1f}m"
            print(log_line, flush=True)
            with open(log_file, 'a') as f:
                f.write(log_line + '\n')
            continue
        
        # Validation
        model.eval()
        val_loss = 0
        val_batches = 0
        with torch.no_grad():
            for batch_i in range(0, len(val_data), args.batch_size):
                batch = val_data[batch_i:batch_i+args.batch_size]
                if len(batch) < 2:
                    continue
                
                src_ids = []
                tgt_ids = []
                for inp, out in batch:
                    s = encode_text(inp, stoi, args.max_len)
                    t = [bos_id] + encode_text(out, stoi, args.max_len - 1) + [eos_id]
                    src_ids.append(s)
                    tgt_ids.append(t)
                
                max_src = max(len(s) for s in src_ids)
                max_tgt = max(len(t) for t in tgt_ids)
                src_pad = [s + [pad_id] * (max_src - len(s)) for s in src_ids]
                tgt_pad = [t + [pad_id] * (max_tgt - len(t)) for t in tgt_ids]
                
                src_tensor = torch.tensor(src_pad, dtype=torch.long, device=device)
                tgt_tensor = torch.tensor(tgt_pad, dtype=torch.long, device=device)
                
                out = model(src_tensor, tgt_tensor[:, :-1])
                loss = criterion(out.reshape(-1, vocab_size), tgt_tensor[:, 1:].reshape(-1))
                val_loss += loss.item()
                val_batches += 1
        
        avg_val = val_loss / max(val_batches, 1)
        avg_train = total_loss / max(n_batches, 1)
        epoch_time = (time.time() - epoch_start) / 60
        
        is_best = avg_val < best_val
        if is_best:
            best_val = avg_val
        
        log_line = f"Epoch {epoch+1} | Train:{avg_train:.4f} | Val:{avg_val:.4f} | Best:{best_val:.4f} | T:{epoch_time:.1f}m"
        if is_best:
            log_line += " ✅Best!"
        print(log_line, flush=True)
        with open(log_file, 'a') as f:
            f.write(log_line + '\n')
        
        # Save
        if is_best:
            torch.save({
                'epoch': epoch,
                'model_state': model.state_dict(),
                'optimizer_state': optimizer.state_dict(),
                'val_loss': avg_val,
                'train_loss': avg_train,
                'best_val': best_val,
                'global_step': global_step,
                'n_params': n_params,
                'config': {
                    'd_model': args.d_model,
                    'n_heads': args.n_heads,
                    'n_layers': args.n_layers,
                    'd_ff': args.d_ff,
                    'vocab_size': vocab_size,
                    'use_qmoe': args.use_qmoe,
                }
            }, os.path.join(args.output_dir, 'qsm_v7_quantum_best.pth'))
        
        # Save checkpoint every 5 epochs
        if (epoch + 1) % 5 == 0:
            torch.save({
                'epoch': epoch,
                'model_state': model.state_dict(),
                'optimizer_state': optimizer.state_dict(),
                'val_loss': avg_val,
                'train_loss': avg_train,
                'best_val': best_val,
                'global_step': global_step,
                'n_params': n_params,
            }, os.path.join(args.output_dir, f'qsm_v7_checkpoint_e{epoch+1}.pth'))
    
    print(f"\nTraining complete! Best Val: {best_val:.4f}")

if __name__ == '__main__':
    train()
