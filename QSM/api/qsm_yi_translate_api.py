#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QSM V5 翻译API服务 (端口8000) - 最新训练模型
从V1升级到V5: encoder-decoder + 门控量子注意力
作者: 小趣WeQ | 监督: 中华Zhoho
日期: 2026-04-29
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import torch
import torch.nn as nn
import json
import math
import os

app = Flask(__name__)
CORS(app)

WORKSPACE = '/root/.openclaw/workspace'
V5_MODEL_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/qsm_v5_quantum_best.pth')
V5_VOCAB_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/v4_vocab.json')

# === QSM V5 Model Class ===
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
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

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

            BOS_ID = self.vocab_bos
            EOS_ID = self.vocab_eos
            beams = [([BOS_ID], 0.0)]
            for step in range(max_len):
                new_beams = []
                for seq, score in beams:
                    if seq[-1] == EOS_ID and len(seq) > 1:
                        new_beams.append((seq, score))
                        continue
                    tgt = torch.tensor([seq], dtype=torch.long)
                    tgt_mask = nn.Transformer.generate_square_subsequent_mask(tgt.size(1))
                    out = self.forward(src, tgt, tgt_mask=tgt_mask)
                    log_probs = torch.log_softmax(out[0, -1], dim=-1)
                    topk_probs, topk_ids = log_probs.topk(beam_size)
                    for i in range(beam_size):
                        new_seq = seq + [topk_ids[i].item()]
                        new_score = score + topk_probs[i].item()
                        new_beams.append((new_seq, new_score))
                beams = sorted(new_beams, key=lambda x: x[1], reverse=True)[:beam_size]
                if all(b[0][-1] == EOS_ID and len(b[0]) > 1 for b in beams):
                    break
            best = beams[0][0]
            return best
        return [BOS_ID]

# Load model
print("=" * 50)
print("QSM V5 翻译API (端口8000)")
print("原则: 量子自举")
print("=" * 50)
model = None
vocab = None
id_to_char = None
vocab_size = 0

try:
    with open(V5_VOCAB_PATH, 'r', encoding='utf-8') as f:
        vocab = json.load(f)
    id_to_char = {v: k for k, v in vocab.items()}
    vocab_size = len(vocab)
    model = QSM_V5(vocab_size, d_model=256, n_heads=4, n_layers=3, d_ff=512, max_len=64)
    checkpoint = torch.load(V5_MODEL_PATH, map_location='cpu')
    model.load_state_dict(checkpoint['model_state'])
    model.eval()
    model.vocab_bos = vocab.get('<BOS>', 6920)
    model.vocab_eos = vocab.get('<EOS>', 6921)
    print(f"✅ V5模型加载成功! Epoch {checkpoint.get('epoch')}, Val Loss {checkpoint.get('val_loss', 0):.4f}")
    print(f"词表: {vocab_size}, 参数: {sum(p.numel() for p in model.parameters()):,}")
except Exception as e:
    print(f"❌ 模型加载失败: {e}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'model_loaded': model is not None,
        'vocab_size': vocab_size,
        'model': 'QSM V5 Encoder-Decoder',
        'status': 'healthy' if model is not None else 'no_model'
    })

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json(force=True)
    text = data.get('text', '')
    if not text:
        return jsonify({'error': '请提供text参数'}), 400
    if model is None:
        return jsonify({'error': '模型未加载'}), 503
    UNK_ID = vocab.get('<UNK>', 3)
    src_ids = [vocab.get(c, UNK_ID) for c in text if c in vocab]
    if not src_ids:
        return jsonify({'error': '输入无有效字符'}), 400
    try:
        result_ids = model.translate_beam_search(src_ids, beam_size=3, max_len=64)
        result_chars = []
        for tid in result_ids[1:]:
            if tid == model.vocab_eos:
                break
            ch = id_to_char.get(tid, '?')
            result_chars.append(ch)
        result = ''.join(result_chars)
        return jsonify({
            'input': text,
            'translated': result,
            'model': 'QSM V5 Encoder-Decoder'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 启动V5翻译API (端口8000)...")
    app.run(host='0.0.0.0', port=8000, debug=False)
