"""QSM V5训练 - 全小写英文 + 52K数据 + 门控量子注意力 + 课程学习"""
import torch, torch.nn as nn, json, math, time, os
from torch.utils.data import Dataset, DataLoader

CONFIG = {
    'vocab_size': 6924, 'd_model': 256, 'n_heads': 4, 'n_layers': 3,
    'd_ff': 512, 'dropout': 0.1, 'max_len': 64, 'batch_size': 16,
    'lr': 1e-3, 'weight_decay': 0.01, 'epochs': 30, 'warmup_steps': 500,
    'label_smoothing': 0.1, 'device': 'cpu',
    'train_data': '/root/.openclaw/workspace/Models/QSM/bin/v5_train_pairs.json',
    'val_data': '/root/.openclaw/workspace/Models/QSM/bin/v5_val_pairs.json',
    'vocab_path': '/root/.openclaw/workspace/Models/QSM/bin/v4_vocab.json',
    'save_dir': '/root/.openclaw/workspace/Models/QSM/bin',
}

class QSM_V5(nn.Module):
    def __init__(self, vocab_size, d_model=256, n_heads=4, n_layers=3, d_ff=512, dropout=0.1, max_len=64):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = nn.Embedding(max_len, d_model)
        enc_layer = nn.TransformerEncoderLayer(d_model, n_heads, d_ff, dropout, batch_first=True)
        self.encoder = nn.TransformerEncoder(enc_layer, n_layers)
        dec_layer = nn.TransformerDecoderLayer(d_model, n_heads, d_ff, dropout, batch_first=True)
        self.decoder = nn.TransformerDecoder(dec_layer, n_layers)
        self.quantum_gate = nn.Parameter(torch.ones(1) * 0.3)
        self.quantum_rotation = nn.Parameter(torch.randn(n_heads, d_model // n_heads) * 0.01)
        self.norm = nn.LayerNorm(d_model)
        self.output_proj = nn.Linear(d_model, vocab_size)
        self._init_weights()

    def _init_weights(self):
        for p in self.parameters():
            if p.dim() > 1: nn.init.xavier_uniform_(p)

    def forward(self, src, tgt, src_mask=None, tgt_mask=None, tgt_key_padding_mask=None):
        src_emb = self.embedding(src) * math.sqrt(self.d_model) + self.pos_encoding(torch.arange(src.size(1), device=src.device))
        enc_out = self.encoder(src_emb, src_key_padding_mask=src_mask)
        B, S, _ = enc_out.shape
        nh, dh = self.quantum_rotation.shape
        enc_view = enc_out.view(B, S, nh, dh)
        qr = self.quantum_rotation
        quantum_out = (enc_view * torch.cos(qr) + torch.roll(enc_view, 1, -1) * torch.sin(qr)).reshape(B, S, -1)
        enc_out = self.quantum_gate * quantum_out + (1 - self.quantum_gate) * enc_out
        tgt_emb = self.embedding(tgt) * math.sqrt(self.d_model) + self.pos_encoding(torch.arange(tgt.size(1), device=tgt.device))
        dec_out = self.decoder(tgt_emb, enc_out, tgt_mask=tgt_mask, tgt_key_padding_mask=tgt_key_padding_mask)
        return self.output_proj(self.norm(dec_out))

    def translate_beam_search(self, src_ids, beam_size=5, max_len=40):
        self.eval()
        with torch.no_grad():
            src = torch.tensor([src_ids], dtype=torch.long)
            src_emb = self.embedding(src) * math.sqrt(self.d_model) + self.pos_encoding(torch.arange(src.size(1)))
            enc_out = self.encoder(src_emb)
            B, S, _ = enc_out.shape
            nh, dh = self.quantum_rotation.shape
            enc_view = enc_out.view(B, S, nh, dh)
            qr = self.quantum_rotation
            quantum_out = (enc_view * torch.cos(qr) + torch.roll(enc_view, 1, -1) * torch.sin(qr)).reshape(B, S, -1)
            enc_out = self.quantum_gate * quantum_out + (1 - self.quantum_gate) * enc_out
            BOS_ID, EOS_ID = 6920, 6921
            beams = [([BOS_ID], 0.0)]
            for step in range(max_len):
                new_beams = []
                for seq, score in beams:
                    if seq[-1] == EOS_ID and len(seq) > 1:
                        new_beams.append((seq, score)); continue
                    tgt = torch.tensor([seq], dtype=torch.long)
                    tgt_emb = self.embedding(tgt) * math.sqrt(self.d_model) + self.pos_encoding(torch.arange(tgt.size(1)))
                    tgt_mask = nn.Transformer.generate_square_subsequent_mask(tgt.size(1))
                    dec_out = self.decoder(tgt_emb, enc_out, tgt_mask=tgt_mask)
                    logits = self.output_proj(self.norm(dec_out[:, -1, :]))
                    log_probs = torch.log_softmax(logits, dim=-1)
                    topk_probs, topk_ids = log_probs.topk(beam_size)
                    for i in range(beam_size):
                        new_beams.append((seq + [topk_ids[0, i].item()], score + topk_probs[0, i].item()))
                beams = sorted(new_beams, key=lambda x: x[1], reverse=True)[:beam_size]
                if all(seq[-1] == EOS_ID for seq, _ in beams): break
            return max(beams, key=lambda x: x[1] / max(len(x[0]), 1))[0]

class TranslationDataset(Dataset):
    def __init__(self, path, max_len=64):
        with open(path, 'r', encoding='utf-8') as f: self.data = json.load(f)
        self.max_len = max_len
    def __len__(self): return len(self.data)
    def __getitem__(self, idx):
        item = self.data[idx]
        src = item['src'][:self.max_len] + [0] * (self.max_len - len(item['src'][:self.max_len]))
        tgt = item['tgt'][:self.max_len]
        tgt_in = tgt[:-1] + [0] * (self.max_len - len(tgt) + 1)
        tgt_out = tgt[1:] + [0] * (self.max_len - len(tgt) + 1)
        return torch.tensor(src), torch.tensor(tgt_in[:self.max_len]), torch.tensor(tgt_out[:self.max_len])

if __name__ == '__main__':
    c = CONFIG; dev = torch.device(c['device'])
    with open(c['vocab_path'], 'r', encoding='utf-8') as f: vocab = json.load(f)
    c['vocab_size'] = len(vocab)
    print(f"=" * 60); print("QSM V5 (全小写+52K+门控量子+Warmup+Cosine+LabelSmooth)"); print("=" * 60)
    print(f"词表: {c['vocab_size']}")
    train_ds = TranslationDataset(c['train_data'], c['max_len'])
    val_ds = TranslationDataset(c['val_data'], c['max_len'])
    print(f"训练: {len(train_ds):,} 验证: {len(val_ds):,}")
    train_dl = DataLoader(train_ds, batch_size=c['batch_size'], shuffle=True)
    val_dl = DataLoader(val_ds, batch_size=c['batch_size'], shuffle=False)
    model = QSM_V5(c['vocab_size'], c['d_model'], c['n_heads'], c['n_layers'], c['d_ff'], c['dropout'], c['max_len']).to(dev)
    n_params = sum(p.numel() for p in model.parameters())
# Resume from checkpoint if available
resume_path = os.path.join(c['save_dir'], 'qsm_v5_quantum_best.pth')
start_epoch = 0
if os.path.exists(resume_path):
    ckpt = torch.load(resume_path, map_location=dev)
    model.load_state_dict(ckpt['model_state'])
    start_epoch = ckpt.get('epoch', 0)
    print(f'✅ Resume from Epoch {start_epoch}, Val Loss {ckpt.get("val_loss", "?"):.4f}')
    print(f"参数: {n_params:,}")
    optimizer = torch.optim.AdamW(model.parameters(), lr=c['lr'], weight_decay=c['weight_decay'])
    criterion = nn.CrossEntropyLoss(ignore_index=0, label_smoothing=c['label_smoothing'])
    total_steps = c['epochs'] * len(train_dl)
    def get_lr(step):
        if step < c['warmup_steps']: return c['lr'] * step / c['warmup_steps']
        p = (step - c['warmup_steps']) / max(total_steps - c['warmup_steps'], 1)
        return c['lr'] * 0.5 * (1 + math.cos(math.pi * p))
    # Manual LR scheduling (LambdaLR bug in PyTorch 2.x)
    def set_lr(optimizer, lr):
        for pg in optimizer.param_groups:
            pg['lr'] = lr
    scheduler = None  # Not using LambdaLR due to step counting bug
    best_val = float('inf'); start = time.time(); gs = 0
if os.path.exists(resume_path) and 'val_loss' in ckpt:
    best_val = ckpt['val_loss']  # Resume best_val to prevent non-best overwrites
    for ep in range(start_epoch, c['epochs']):
        model.train(); tl = 0; nb = 0
        for bi, (src, ti, to) in enumerate(train_dl):
            src, ti, to = src.to(dev), ti.to(dev), to.to(dev)
            optimizer.zero_grad()
            tgt_mask = nn.Transformer.generate_square_subsequent_mask(ti.size(1)).to(dev)
            logits = model(src, ti, tgt_mask=tgt_mask, tgt_key_padding_mask=(ti == 0))
            loss = criterion(logits.reshape(-1, c['vocab_size']), to.reshape(-1))
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step(); set_lr(optimizer, get_lr(gs+1))
            tl += loss.item(); nb += 1; gs += 1
            if bi % 400 == 0:
                print(f"E{ep+1}/{c['epochs']} B{bi}/{len(train_dl)} L:{loss.item():.4f} lr:{get_lr(gs):.6f} T:{(time.time()-start)/60:.1f}m")
        model.eval(); vl = 0; vb = 0
        with torch.no_grad():
            for src, ti, to in val_dl:
                src, ti, to = src.to(dev), ti.to(dev), to.to(dev)
                tgt_mask = nn.Transformer.generate_square_subsequent_mask(ti.size(1)).to(dev)
                logits = model(src, ti, tgt_mask=tgt_mask, tgt_key_padding_mask=(ti == 0))
                vl += criterion(logits.reshape(-1, c['vocab_size']), to.reshape(-1)).item(); vb += 1
        at, av = tl/nb, vl/vb
        if av < best_val:
            best_val = av
            torch.save({'epoch': ep+1, 'model_state': model.state_dict(), 'val_loss': av, 'train_loss': at, 'n_params': n_params}, os.path.join(c['save_dir'], 'qsm_v5_quantum_best.pth'))
            print(f"✅Best! Epoch {ep+1} | Train:{at:.4f} | Val:{av:.4f} | Best:{best_val:.4f}")
        else:
            print(f"   Epoch {ep+1} | Train:{at:.4f} | Val:{av:.4f} | Best:{best_val:.4f}")
        if (ep+1) % 5 == 0:
            torch.save({'epoch': ep+1, 'model_state': model.state_dict(), 'val_loss': av}, os.path.join(c['save_dir'], f'qsm_v5_quantum_e{ep+1}.pth'))
    print(f"\n🎉 V5完成! {(time.time()-start)/3600:.1f}h Best:{best_val:.4f}")
