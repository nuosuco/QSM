#!/usr/bin/env python3
"""QSM V14 API - ALiBi + SPM16K + LoRA"""
import os, sys, json, math, torch, torch.nn as nn, torch.nn.functional as F
import sentencepiece as spm
from flask import Flask, request, jsonify
from flask_cors import CORS

WORKSPACE = '/root/.openclaw/workspace'
sys.path.insert(0, WORKSPACE)

from Models.QSM.train_v14_alibi import QSM_V14

app = Flask(__name__)
CORS(app)

MODEL_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/qsm_v14_best.pth')
SPM_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/qsm_spm_v14_yi.model')

model = None
best_val = 0
best_epoch = 0
sp = None

BOS_ID = 1
EOS_ID = 2
PAD_ID = 0

def load_model():
    global model, sp, best_val, best_epoch
    sp = spm.SentencePieceProcessor()
    sp.load(SPM_PATH)
    
    ckpt = torch.load(MODEL_PATH, map_location='cpu')
    vocab_size = ckpt['vocab_size']
    d_model = ckpt['d_model']
    n_heads = ckpt['n_heads']
    n_layers = ckpt['n_layers']
    d_ff = ckpt['d_ff']
    max_len = ckpt['max_len']
    
    model = QSM_V14(
        vocab_size=vocab_size,
        d_model=d_model,
        n_heads=n_heads,
        n_layers=n_layers,
        d_ff=d_ff,
        max_len=max_len,
        dropout=0.0,
        lora_r=32
    )
    
    state = ckpt['model_state']
    new_state = {}
    for k, v in state.items():
        new_state[k[7:] if k.startswith('module.') else k] = v
    model.load_state_dict(new_state, strict=False)
    model.eval()
    
    best_val = ckpt.get("best_val", 0)
    best_epoch = ckpt.get("epoch", 0)
    print(f"✅ V14 loaded: E{best_epoch} Val={best_val:.4f} Vocab={vocab_size}")

@torch.no_grad()
def translate(text, max_len=64, beam_size=3, rep_penalty=2.5):
    src_ids = sp.encode(text)
    if len(src_ids) == 0:
        return ""
    src_tensor = torch.tensor([src_ids], dtype=torch.long)
    
    enc_out = model.encode(src_tensor)
    
    # Beam search
    beams = [(0.0, [BOS_ID])]
    
    for step in range(max_len):
        candidates = []
        for score, seq in beams:
            if seq[-1] == EOS_ID and len(seq) > 3:
                candidates.append((score, seq))
                continue
            
            tgt_tensor = torch.tensor([seq], dtype=torch.long)
            dec_out = model.decode(tgt_tensor, enc_out)
            logits = model.output_proj(dec_out[0, -1])
            log_probs = F.log_softmax(logits, dim=-1)
            
            for prev_id in set(seq):
                if log_probs[prev_id] < 0:
                    log_probs[prev_id] *= rep_penalty
            # Hard ban consecutive repeats
            if len(seq) >= 2:
                for bid in set(seq[-3:]):
                    log_probs[bid] = -1e9
            
            topk = torch.topk(log_probs, beam_size)
            for i in range(beam_size):
                new_score = score + topk.values[i].item()
                new_seq = seq + [topk.indices[i].item()]
                candidates.append((new_score, new_seq))
        
        candidates.sort(key=lambda x: x[0], reverse=True)
        beams = candidates[:beam_size]
        
        if all(seq[-1] == EOS_ID and len(seq) > 3 for _, seq in beams):
            break
    
    best = max(beams, key=lambda x: x[0] / max(len(x[1]), 1))
    ids = best[1]
    if ids[0] == BOS_ID: ids = ids[1:]
    if EOS_ID in ids: ids = ids[:ids.index(EOS_ID)]
    
    return sp.decode(ids)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "model": "QSM V14 ALiBi",
        "status": "healthy" if model else "not_loaded",
        "epoch": best_epoch,
        "val_loss": best_val,
        "vocab_size": 16000,
        "architecture": "ALiBi + SPM16K + LoRA"
    })

@app.route('/translate', methods=['POST'])
def do_translate():
    data = request.json or {}
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "no text provided"}), 400
    try:
        result = translate(text)
        return jsonify({"input": text, "translated": result, "model": "QSM V14 ALiBi"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/version', methods=['GET'])
def version():
    return jsonify({"version": "14.0", "model": "QSM V14 ALiBi", "val_loss": best_val, "vocab_size": 16000})

if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=8001, debug=False)
