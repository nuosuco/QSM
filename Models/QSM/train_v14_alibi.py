#!/usr/bin/env python3
"""QSM V14 Training Script - ALiBi + SPM 16K + True SGDR + LoRA Rank Schedule"""

import os, sys, json, math, time, argparse, random
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import sentencepiece as spm

try:
    import loralib as lora
    HAS_LORA = True
except ImportError:
    HAS_LORA = False

# ============================================================
# ALiBi Position Encoding
# ============================================================
class ALiBiBias(nn.Module):
    """ALiBi: Attention with Linear Biases - 0 learnable parameters!"""
    def __init__(self, n_heads, max_seq_len=512):
        super().__init__()
        # Slopes: m_i = 2^(-8/n_heads * (i+1))
        slopes = 2 ** (-8.0 / n_heads * torch.arange(1, n_heads + 1))
        self.register_buffer('slopes', slopes)
        
        # Precompute distance matrix
        rows = torch.arange(max_seq_len).unsqueeze(1)  # (S, 1)
        cols = torch.arange(max_seq_len).unsqueeze(0)  # (1, S)
        dist = cols - rows  # positive=look back, negative=look ahead
        # alibi: (n_heads, S, S)
        alibi = slopes.unsqueeze(1).unsqueeze(2) * dist.unsqueeze(0).float()
        self.register_buffer('alibi', alibi)
    
    def forward(self, seq_len):
        """Returns (n_heads, seq_len, seq_len) bias tensor"""
        return self.alibi[:, :seq_len, :seq_len]

# ============================================================
# ALiBi Multi-Head Attention
# ============================================================
class ALiBiMultiheadAttention(nn.Module):
    def __init__(self, d_model, n_heads, dropout=0.1, lora_r=0):
        super().__init__()
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.dropout = nn.Dropout(dropout)
        
        if lora_r > 0 and HAS_LORA:
            self.W_q = lora.Linear(d_model, d_model, r=lora_r)
            self.W_k = lora.Linear(d_model, d_model, r=lora_r)
            self.W_v = lora.Linear(d_model, d_model, r=lora_r)
            self.W_o = lora.Linear(d_model, d_model, r=lora_r)
        else:
            self.W_q = nn.Linear(d_model, d_model)
            self.W_k = nn.Linear(d_model, d_model)
            self.W_v = nn.Linear(d_model, d_model)
            self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, query, key, value, alibi_bias=None,
                key_padding_mask=None, causal=False):
        B, S, _ = query.shape
        Q = self.W_q(query).view(B, S, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key).view(B, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).view(B, -1, self.n_heads, self.d_k).transpose(1, 2)
        
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        # Add ALiBi bias
        if alibi_bias is not None:
            # alibi_bias: (n_heads, S_q, S_k)
            scores = scores + alibi_bias.unsqueeze(0)
        
        # Causal mask for decoder self-attention
        if causal:
            T = scores.size(-2)
            causal_mask = torch.triu(
                torch.ones(T, scores.size(-1), device=scores.device), diagonal=1
            ).bool()
            scores = scores.masked_fill(causal_mask.unsqueeze(0).unsqueeze(0), float('-inf'))
        
        # Key padding mask
        if key_padding_mask is not None:
            scores = scores.masked_fill(
                key_padding_mask.unsqueeze(1).unsqueeze(2), float('-inf')
            )
        
        attn = F.softmax(scores, dim=-1)
        attn = self.dropout(attn)
        out = torch.matmul(attn, V)
        out = out.transpose(1, 2).contiguous().view(B, S, -1)
        return self.W_o(out)

# ============================================================
# ALiBi Encoder Layer
# ============================================================
class ALiBiEncoderLayer(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, dropout=0.1, lora_r=0):
        super().__init__()
        self.self_attn = ALiBiMultiheadAttention(d_model, n_heads, dropout, lora_r)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(d_ff, d_model), nn.Dropout(dropout)
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
    
    def forward(self, x, alibi_bias=None, src_key_padding_mask=None):
        x2 = self.self_attn(x, x, x, alibi_bias, src_key_padding_mask, causal=False)
        x = self.norm1(x + self.dropout1(x2))
        x = self.norm2(x + self.ffn(x))
        return x

# ============================================================
# ALiBi Decoder Layer
# ============================================================
class ALiBiDecoderLayer(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, dropout=0.1, lora_r=0):
        super().__init__()
        self.self_attn = ALiBiMultiheadAttention(d_model, n_heads, dropout, lora_r)
        self.cross_attn = ALiBiMultiheadAttention(d_model, n_heads, dropout, lora_r)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(d_ff, d_model), nn.Dropout(dropout)
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
    
    def forward(self, x, enc_out, self_alibi=None,
                tgt_key_padding_mask=None, src_key_padding_mask=None):
        # Self-attention: causal + ALiBi
        x2 = self.self_attn(x, x, x, self_alibi, tgt_key_padding_mask, causal=True)
        x = self.norm1(x + self.dropout1(x2))
        # Cross-attention: NO ALiBi (encoder already has position info)
        x2 = self.cross_attn(x, enc_out, enc_out, None, src_key_padding_mask, causal=False)
        x = self.norm2(x + self.dropout2(x2))
        x = self.norm3(x + self.ffn(x))
        return x

# ============================================================
# QSM V14 Model
# ============================================================
class QSM_V14(nn.Module):
    def __init__(self, vocab_size, d_model=256, n_heads=4, n_layers=4,
                 d_ff=1024, dropout=0.1, max_len=128, lora_r=0):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.max_len = max_len
        
        # Embedding (NO positional embedding!)
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.embed_dropout = nn.Dropout(dropout)
        
        # ALiBi bias (0 learnable parameters!)
        self.alibi = ALiBiBias(n_heads, max_seq_len=512)
        
        # Encoder layers
        self.encoder_layers = nn.ModuleList([
            ALiBiEncoderLayer(d_model, n_heads, d_ff, dropout, lora_r)
            for _ in range(n_layers)
        ])
        self.enc_norm = nn.LayerNorm(d_model)
        
        # Decoder layers
        self.decoder_layers = nn.ModuleList([
            ALiBiDecoderLayer(d_model, n_heads, d_ff, dropout, lora_r)
            for _ in range(n_layers)
        ])
        self.dec_norm = nn.LayerNorm(d_model)
        
        # Output projection
        self.output_proj = nn.Linear(d_model, vocab_size)
        
        # Quantum gate (preserved from V7)
        self.quantum_gate = nn.Parameter(torch.ones(1) * 0.3)
        self.quantum_rotation = nn.Parameter(
            torch.randn(n_heads, d_model // n_heads) * 0.01
        )
        
        self._init_weights()
    
    def _init_weights(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def encode(self, src, src_key_padding_mask=None):
        B, S = src.shape
        x = self.embed_dropout(self.embedding(src) * math.sqrt(self.d_model))
        
        # ALiBi bias for encoder (bidirectional)
        enc_alibi = self.alibi(S)
        
        for layer in self.encoder_layers:
            x = layer(x, enc_alibi, src_key_padding_mask)
        enc_out = self.enc_norm(x)
        
        # Quantum gate mixing
        nh, dh = self.quantum_rotation.shape
        enc_view = enc_out.view(B, S, nh, dh)
        qr = self.quantum_rotation
        quantum_out = (enc_view * torch.cos(qr) + 
                      torch.roll(enc_view, 1, -1) * torch.sin(qr)).reshape(B, S, -1)
        enc_out = self.quantum_gate * quantum_out + (1 - self.quantum_gate) * enc_out
        
        return enc_out
    
    def decode(self, tgt, enc_out, tgt_key_padding_mask=None, 
               src_key_padding_mask=None):
        B, T = tgt.shape
        x = self.embed_dropout(self.embedding(tgt) * math.sqrt(self.d_model))
        
        # ALiBi bias for decoder (causal)
        dec_alibi = self.alibi(T)
        
        for layer in self.decoder_layers:
            x = layer(x, enc_out, dec_alibi, tgt_key_padding_mask, src_key_padding_mask)
        return self.dec_norm(x)
    
    def forward(self, src, tgt, src_key_padding_mask=None,
                tgt_key_padding_mask=None):
        enc_out = self.encode(src, src_key_padding_mask)
        dec_out = self.decode(tgt, enc_out, tgt_key_padding_mask, src_key_padding_mask)
        return self.output_proj(dec_out)

# ============================================================
# SPM Dataset
# ============================================================
class SPMDataset(Dataset):
    def __init__(self, data_path, spm_model_path, max_len=128, 
                 max_difficulty=5, difficulty_field='difficulty'):
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(spm_model_path)
        self.max_len = max_len
        self.pad_id = self.sp.pad_id()
        self.bos_id = self.sp.bos_id()
        self.eos_id = self.sp.eos_id()
        
        with open(data_path, 'r') as f:
            raw = json.load(f)
        
        # Filter by difficulty (curriculum learning)
        self.data = []
        for item in raw:
            diff = item.get(difficulty_field, 1)
            if diff <= max_difficulty:
                self.data.append(item)
        
        print(f"SPM Dataset: {len(self.data)} samples (diff<={max_difficulty})")
    
        self.raw = raw  # Keep raw data for re-filtering

    def set_max_difficulty(self, max_difficulty):
        """Re-filter dataset by difficulty without reloading from disk"""
        self.data = []
        for item in self.raw:
            diff = item.get('difficulty', 1)
            if diff <= max_difficulty:
                self.data.append(item)
        print(f"Dataset re-filtered: {len(self.data)} samples (diff<={max_difficulty})")

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        src_ids = self.sp.encode(item['input'])[:self.max_len - 2]
        tgt_ids = self.sp.encode(item['output'])[:self.max_len - 2]
        
        src = [self.bos_id] + src_ids + [self.eos_id]
        tgt = [self.bos_id] + tgt_ids + [self.eos_id]
        
        # Pad to max_len
        src = src + [self.pad_id] * (self.max_len - len(src))
        tgt = tgt + [self.pad_id] * (self.max_len - len(tgt))
        
        src = torch.tensor(src, dtype=torch.long)
        tgt = torch.tensor(tgt, dtype=torch.long)
        
        # Padding masks
        src_mask = (src == self.pad_id)
        tgt_mask = (tgt == self.pad_id)
        
        # Teacher forcing: tgt_input = all but last, tgt_output = all but first
        tgt_input = tgt[:-1].clone()
        tgt_output = tgt[1:].clone()
        tgt_input_mask = tgt_mask[:-1].clone()
        
        return {
            'src': src,
            'tgt_input': tgt_input,
            'tgt_output': tgt_output,
            'src_mask': src_mask,
            'tgt_mask': tgt_input_mask,
        }

# ============================================================
# Training
# ============================================================

def get_max_difficulty(epoch):
    """Dynamic curriculum: increase difficulty at SGDR restart points"""
    if epoch < 10:
        return 2   # Phase1: 22K samples (easy)
    elif epoch < 30:
        return 3   # Phase2: 71K samples (medium)  
    elif epoch < 70:
        return 4   # Phase3: 80K samples (hard)
    else:
        return 5   # Phase4: 80K+ samples (all)


def train(args):
    device = torch.device('cpu')
    start_epoch = 0
    best_val = float('inf')
    
    # SPM dataset
    train_ds = SPMDataset(args.data, args.spm_model, args.max_len, max_difficulty=5)  # Load all, filter per-epoch
    vocab_size = train_ds.sp.get_piece_size()
    
    full_ds = train_ds  # Keep reference to SPMDataset for curriculum
    # Apply initial curriculum filter
    init_diff = get_max_difficulty(start_epoch)
    full_ds.set_max_difficulty(init_diff)
    full_ds._cur_diff = init_diff
    # 80/20 split
    n = len(full_ds)
    n_val = max(1, n // 5)
    n_train = n - n_val
    train_ds, val_ds = torch.utils.data.random_split(train_ds, [n_train, n_val])
    
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, 
                              num_workers=0, pin_memory=False)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                            num_workers=0, pin_memory=False)
    
    # Model
    model = QSM_V14(
        vocab_size=vocab_size,
        d_model=args.d_model,
        n_heads=args.n_heads,
        n_layers=args.n_layers,
        d_ff=args.d_ff,
        dropout=args.dropout,
        max_len=args.max_len,
        lora_r=args.lora_r if HAS_LORA else 0,
    ).to(device)
    
    total_params = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"V14 Model: {total_params:,} total, {trainable:,} trainable")
    
    # Optimizer (create BEFORE resume so load_state_dict works)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01, betas=(0.9, 0.98))

    # Resume from checkpoint if specified
    if args.resume and os.path.exists(args.resume):
        ckpt = torch.load(args.resume, map_location=device)
        model.load_state_dict(ckpt['model_state'])
        optimizer.load_state_dict(ckpt['optimizer_state'])
        start_epoch = ckpt.get('epoch', 0)
        best_val = ckpt.get('best_val', float('inf'))
        print(f"🔥 Resumed from {args.resume}: E{start_epoch}, best_val={best_val:.4f}")
            
    # TRUE SGDR scheduler (no manual LR override!)
    if args.scheduler == 'sgdr':
        scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=args.sgdr_t0, T_mult=args.sgdr_tmult, eta_min=1e-6
        )
        print(f"LR Scheduler: TRUE SGDR (T_0={args.sgdr_t0}, T_mult={args.sgdr_tmult})")
    elif args.scheduler == 'cosine':
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=args.epochs, eta_min=1e-6
        )
        print(f"LR Scheduler: Cosine Annealing")
    else:
        scheduler = None
        print("LR Scheduler: None (constant LR)")
    
    # Loss
    criterion = nn.CrossEntropyLoss(
        ignore_index=train_ds.dataset.sp.pad_id() if hasattr(train_ds, 'dataset') else 0,
        label_smoothing=args.label_smoothing
    )
    
    # Training log
    log_file = os.path.join(args.output_dir, 'v14_train.log')
    best_val = float('inf')
    
    for epoch in range(start_epoch, args.epochs):
        # Curriculum: update max_difficulty based on epoch
        cur_diff = get_max_difficulty(epoch)
        if cur_diff != getattr(full_ds, '_cur_diff', None):
            print(f"🔥 Curriculum: max_difficulty {getattr(full_ds, '_cur_diff', '?')} -> {cur_diff} (epoch {epoch})")
            full_ds.set_max_difficulty(cur_diff)
            full_ds._cur_diff = cur_diff
            # Rebuild DataLoader with new dataset size
            n = len(full_ds)
            n_val = max(1, n // 5)
            n_train = n - n_val
            train_subset, val_subset = torch.utils.data.random_split(full_ds, [n_train, n_val])
            train_loader = DataLoader(train_subset, batch_size=args.batch_size, shuffle=True, num_workers=0, pin_memory=False)
            val_loader = DataLoader(val_subset, batch_size=args.batch_size, shuffle=False, num_workers=0, pin_memory=False)
        model.train()
        total_loss = 0
        n_batches = 0
        epoch_start = time.time()
        for batch_i, batch in enumerate(train_loader):
            src = batch['src'].to(device)
            tgt_input = batch['tgt_input'].to(device)
            tgt_output = batch['tgt_output'].to(device)
            src_mask = batch['src_mask'].to(device)
            tgt_mask = batch['tgt_mask'].to(device)
            
            # Forward
            logits = model(src, tgt_input, src_key_padding_mask=src_mask, 
                          tgt_key_padding_mask=tgt_mask)
            
            # Loss: (B, T, V) → (B*T, V) vs (B*T,)
            loss = criterion(logits.reshape(-1, logits.size(-1)), tgt_output.reshape(-1))
            
            # Gradient accumulation
            loss = loss / args.accum_steps
            loss.backward()
            
            if (batch_i + 1) % args.accum_steps == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
                optimizer.step()
                optimizer.zero_grad()
            
            total_loss += loss.item() * args.accum_steps
            n_batches += 1
            
            if n_batches % 200 == 0:
                elapsed = time.time() - epoch_start
                cur_lr = optimizer.param_groups[0]['lr']
                log_line = f"E{epoch+1}/{args.epochs} B{n_batches} L:{loss.item()*args.accum_steps:.4f} lr:{cur_lr:.6f} T:{elapsed/60:.1f}m"
                print(log_line, flush=True)
                with open(log_file, 'a') as f:
                    f.write(log_line + '\n')
        
        # Step SGDR scheduler (TRUE SGDR, no manual override!)
        if scheduler is not None:
            scheduler.step()
        
        # Validation
        model.eval()
        val_loss = 0
        val_batches = 0
        with torch.no_grad():
            for batch in val_loader:
                src = batch['src'].to(device)
                tgt_input = batch['tgt_input'].to(device)
                tgt_output = batch['tgt_output'].to(device)
                src_mask = batch['src_mask'].to(device)
                tgt_mask = batch['tgt_mask'].to(device)
                
                logits = model(src, tgt_input, src_key_padding_mask=src_mask,
                              tgt_key_padding_mask=tgt_mask)
                loss = criterion(logits.reshape(-1, logits.size(-1)), tgt_output.reshape(-1))
                val_loss += loss.item()
                val_batches += 1
        
        avg_train = total_loss / max(n_batches, 1)
        avg_val = val_loss / max(val_batches, 1)
        is_best = avg_val < best_val
        if is_best:
            best_val = avg_val
        
        elapsed = (time.time() - epoch_start) / 60
        log_line = f"Epoch {epoch+1} | Train:{avg_train:.4f} | Val:{avg_val:.4f} | Best:{best_val:.4f} | T:{elapsed:.1f}m"
        if is_best:
            log_line += " ✅Best!"
        print(log_line, flush=True)
        with open(log_file, 'a') as f:
            f.write(log_line + '\n')
        
        # Save checkpoint
        ckpt = {
            'epoch': epoch + 1,
            'model_state': model.state_dict(),
            'optimizer_state': optimizer.state_dict(),
            'best_val': best_val,
            'vocab_size': vocab_size,
            'd_model': args.d_model,
            'n_heads': args.n_heads,
            'n_layers': args.n_layers,
            'd_ff': args.d_ff,
            'max_len': args.max_len,
            'lora_r': args.lora_r,
        }
        
        # Always save last checkpoint for resume
        last_path = os.path.join(args.output_dir, 'qsm_v14_last.pth')
        torch.save(ckpt, last_path)
        
        if is_best:
            best_path = os.path.join(args.output_dir, 'qsm_v14_best.pth')
            torch.save(ckpt, best_path)
            print(f"  💾 Best model saved: {best_path}")
        
        # Save every 10 epochs
        if (epoch + 1) % 10 == 0:
            ckpt_path = os.path.join(args.output_dir, f'qsm_v14_e{epoch+1}.pth')
            torch.save(ckpt, ckpt_path)
    
    print(f"\nTraining complete! Best Val: {best_val:.4f}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, required=True)
    parser.add_argument('--spm_model', type=str, required=True)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=0.0003)
    parser.add_argument('--d_model', type=int, default=256)
    parser.add_argument('--n_heads', type=int, default=4)
    parser.add_argument('--n_layers', type=int, default=4)
    parser.add_argument('--d_ff', type=int, default=1024)
    parser.add_argument('--max_len', type=int, default=128)
    parser.add_argument('--dropout', type=float, default=0.1)
    parser.add_argument('--grad_clip', type=float, default=1.0)
    parser.add_argument('--accum_steps', type=int, default=2)
    parser.add_argument('--scheduler', type=str, default='sgdr')
    parser.add_argument('--sgdr_t0', type=int, default=10)
    parser.add_argument('--sgdr_tmult', type=int, default=2)
    parser.add_argument('--lora_r', type=int, default=16)
    parser.add_argument('--max_difficulty', type=int, default=5)
    parser.add_argument('--label_smoothing', type=float, default=0.1)
    parser.add_argument('--output_dir', type=str, default='.')
    parser.add_argument('--resume', type=str, default='', help='Resume from checkpoint path')
    args = parser.parse_args()
    
    train(args)
