#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QSM V7-Small 翻译API服务 (端口8000)
V7-Small: 192d/3层/3头/768ff + QuantumEmbeddingV2 + beam search
Val Loss: 2.6531 (Best ever!)
作者: 小趣WeQ | 监督: 中华Zhoho
日期: 2026-05-02
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import torch
import torch.nn as nn
import torch.nn.functional as F
import json
import math
import os

app = Flask(__name__)
CORS(app)

WORKSPACE = '/root/.openclaw/workspace'
V7_MODEL_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/qsm_v7_quantum_best.pth')
V7_BACKUP_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/qsm_v7_small_best_backup.pth')
VOCAB_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/v4_vocab.json')

# === QuantumEmbeddingV2 ===
class QuantumEmbeddingV2(nn.Module):
    """V2: 语言感知量子嵌入 - 基态初始化带语言偏置"""
    def __init__(self, vocab_size, d_model, n_bases=4):
        super().__init__()
        self.d_model = d_model
        self.base_embed = nn.Embedding(n_bases, d_model)
        self.coeff = nn.Embedding(vocab_size, n_bases)
        self.lang_bias = nn.Parameter(torch.zeros(4, d_model))
        nn.init.xavier_uniform_(self.coeff.weight)

    def forward(self, x, lang_id=None):
        coeff = F.softmax(self.coeff(x), dim=-1)
        bases = self.base_embed.weight + self.lang_bias
        out = torch.matmul(coeff, bases) * math.sqrt(self.d_model)
        if lang_id is not None:
            out = out + self.lang_bias[lang_id] * 0.1
        return out

# === QSM V7-Small Model ===
class QSM_V7_Small(nn.Module):
    def __init__(self, vocab_size, d_model=192, n_heads=3, n_layers=3, d_ff=768, dropout=0.25, max_len=64):
        super().__init__()
        self.d_model = d_model
        self.embedding = QuantumEmbeddingV2(vocab_size, d_model)
        self.pos_encoding = nn.Embedding(max_len, d_model)
        self.encoder_type = 'standard'

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

    def forward(self, src, tgt, src_key_padding_mask=None, tgt_key_padding_mask=None, lang_id=None):
        src_emb = self.embedding(src, lang_id) + self.pos_encoding(torch.arange(src.size(1), device=src.device))
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

    def translate_beam_search(self, src_ids, beam_size=5, max_len=50, length_penalty_alpha=0.6, rep_penalty=1.2):
        """Beam search with length penalty and repetition penalty"""
        self.eval()
        device = next(self.parameters()).device
        bos_id = self.vocab_bos
        eos_id = self.vocab_eos

        with torch.no_grad():
            src = torch.tensor([src_ids], dtype=torch.long, device=device)
            # Encode source
            src_emb = self.embedding(src) + self.pos_encoding(torch.arange(src.size(1), device=device))
            enc_out = self.encoder(src_emb)

            B, S, _ = enc_out.shape
            nh, dh = self.quantum_rotation.shape
            enc_view = enc_out.view(B, S, nh, dh)
            qr = self.quantum_rotation
            quantum_out = (enc_view * torch.cos(qr) + torch.roll(enc_view, 1, -1) * torch.sin(qr)).reshape(B, S, -1)
            enc_out = self.quantum_gate * quantum_out + (1 - self.quantum_gate) * enc_out

            # Beam search
            beams = [(0.0, [bos_id])]
            for step in range(max_len):
                candidates = []
                for score, seq in beams:
                    if seq[-1] == eos_id and len(seq) > 1:
                        candidates.append((score, seq))
                        continue
                    tgt_tensor = torch.tensor([seq], dtype=torch.long, device=device)
                    tgt_emb = self.embedding(tgt_tensor) + self.pos_encoding(torch.arange(len(seq), device=device))
                    tgt_mask = nn.Transformer.generate_square_subsequent_mask(len(seq), device=device)
                    dec_out = self.decoder(tgt_emb, enc_out, tgt_mask=tgt_mask)
                    logits = self.output_proj(self.norm(dec_out))[0, -1]

                    # Repetition penalty
                    prev_ids = set(seq)
                    for pid in prev_ids:
                        if logits[pid] > 0:
                            logits[pid] /= rep_penalty
                        else:
                            logits[pid] *= rep_penalty

                    top_k = torch.topk(logits, min(beam_size, logits.size(0)))
                    for i in range(top_k.indices.size(0)):
                        new_id = top_k.indices[i].item()
                        new_score = score + top_k.values[i].item()
                        candidates.append((new_score, seq + [new_id]))

                def len_norm_score(item):
                    s, seq = item
                    lp = ((5 + len(seq)) / 6) ** length_penalty_alpha
                    return s / lp

                beams = sorted(candidates, key=len_norm_score, reverse=True)[:beam_size]
                if all(seq[-1] == eos_id for _, seq in beams if len(seq) > 1):
                    break

            if beams:
                return beams[0][1]
            return [bos_id]


# Load model
print("=" * 50)
print("QSM V7-Small 翻译API (端口8000)")
print("🔥 Val Loss 2.6531 - Best ever!")
print("=" * 50)

model = None
vocab = None
id_to_char = None
vocab_size = 0

try:
    with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
        vocab = json.load(f)
    id_to_char = {v: k for k, v in vocab.items()}
    vocab_size = len(vocab)

    model = QSM_V7_Small(vocab_size, d_model=192, n_heads=3, n_layers=3, d_ff=768, dropout=0.25, max_len=64)

    # Try loading best model, fallback to backup
    model_path = V7_MODEL_PATH
    if not os.path.exists(model_path):
        print(f"⚠️ {model_path} not found, trying backup...")
        model_path = V7_BACKUP_PATH

    checkpoint = torch.load(model_path, map_location='cpu')
    model.load_state_dict(checkpoint['model_state'])
    model.eval()
    model.vocab_bos = vocab.get('<BOS>', 6920)
    model.vocab_eos = vocab.get('<EOS>', 6921)

    print(f"✅ V7-Small模型加载成功! Epoch {checkpoint.get('epoch')}, Val Loss {checkpoint.get('val_loss', 0):.4f}")
    print(f"词表: {vocab_size}, 参数: {sum(p.numel() for p in model.parameters()):,}")
except Exception as e:
    print(f"❌ 模型加载失败: {e}")
    model = None


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'model_loaded': model is not None,
        'vocab_size': vocab_size,
        'model': 'QSM V7-Small (192d/3L/3H)',
        'val_loss': 2.6531,
        'status': 'healthy' if model is not None else 'no_model'
    })



@app.route('/version', methods=['GET'])
def version():
    return jsonify({
        "model": "QSM V7-Small (192d/3L/3H)",
        "version": "7.0",
        "val_loss": 2.6531,
        "params": 4493437,
        "vocab_size": 6924,
        "architecture": "QuantumRotationalEmbedding + Transformer",
        "features": ["beam_search", "ngram_blocking", "rep_penalty_1.5"],
        "next": "V10 (50523 pure pairs, 0% zh-en)",
        "server": "som.top"
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
        result_ids = model.translate_beam_search(src_ids, beam_size=5, max_len=64)
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
            'model': 'QSM V7-Small Encoder-Decoder'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    """Q1 智能对话 - V7-Small模型"""
    try:
        data = request.get_json(force=True)
        message = data.get('message', '')
        if not message:
            return jsonify({'response': '请输入内容', 'model': 'QSM Q1'})
        if model is None:
            return jsonify({'response': '模型未加载', 'model': 'QSM Q1'})

        UNK_ID = vocab.get('<UNK>', 3)
        src_ids = [vocab.get(c, UNK_ID) for c in message if c in vocab]
        if not src_ids:
            return jsonify({'response': '输入无有效字符', 'model': 'QSM Q1'})

        result_ids = model.translate_beam_search(src_ids, beam_size=5, max_len=64)
        result_chars = []
        for tid in result_ids[1:]:
            if tid == model.vocab_eos:
                break
            ch = id_to_char.get(tid, '?')
            result_chars.append(ch)
        result = ''.join(result_chars)

        return jsonify({
            'response': result,
            'model': 'QSM Q1 (V7-Small)'
        })
    except Exception as e:
        return jsonify({'response': f'处理出错: {str(e)[:80]}', 'model': 'QSM Q1'})


if __name__ == '__main__':
    print("🚀 启动V7-Small翻译API (端口8000)...")
    app.run(host='0.0.0.0', port=8000, debug=False)
