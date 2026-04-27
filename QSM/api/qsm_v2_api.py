#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QSM V2 API服务 - 支持翻译、对话、量子计算"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import torch, torch.nn as nn, json, math, os, time

app = Flask(__name__)
CORS(app)

# === 模型定义 ===
class QuantumAttentionLayer(nn.Module):
    def __init__(self, d, n):
        super().__init__()
        self.n = n; self.dh = d // n
        self.quantum_rotation = nn.Parameter(torch.randn(n, self.dh) * 0.01)
        self.quantum_phase = nn.Parameter(torch.randn(n, self.dh) * 0.01)
        self.gate = nn.Parameter(torch.ones(1) * 0.5)
    def forward(self, x):
        B, S, _ = x.shape
        xr = x.view(B, S, self.n, self.dh)
        c = torch.cos(self.quantum_rotation)
        s = torch.sin(self.quantum_rotation)
        quantum = (xr * c + torch.roll(xr, 1, -1) * s).reshape(B, S, -1)
        return self.gate * quantum + (1 - self.gate) * x

class PositionalEncoding(nn.Module):
    def __init__(self, d, dropout=0.1, max_len=256):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d, 2) * (-math.log(10000.0) / d))
        pe = torch.zeros(max_len, 1, d)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)
    def forward(self, x):
        return self.dropout(x + self.pe[:x.size(1)].transpose(0, 1))

class QSMModel(nn.Module):
    def __init__(self, vocab_size, d_model=256, nhead=8, num_layers=4, dim_ff=1024, dropout=0.1, max_len=128):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout, max_len)
        self.quantum_attn = QuantumAttentionLayer(d_model, nhead)
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead, dim_ff, dropout, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        self.decoder = nn.Linear(d_model, vocab_size)
        self.task_classifier = nn.Linear(d_model, 3)
        self.final_norm = nn.LayerNorm(d_model)

    def forward(self, x):
        h = self.embedding(x) * math.sqrt(self.d_model)
        h = self.pos_encoder(h)
        h = h + self.quantum_attn(h)
        h = self.transformer_encoder(h)
        h = self.final_norm(h)
        return self.decoder(h), self.task_classifier(h.mean(1))

# === 加载模型 ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_DIR = os.path.join(BASE_DIR, 'Models', 'QSM', 'bin')

# 加载词表
with open(os.path.join(MODEL_DIR, 'qsm_yi_wen_vocab.json'), 'r', encoding='utf-8') as f:
    vocab_data = json.load(f)
char_to_id = vocab_data['char_to_id']
id_to_char = {int(v): k for k, v in char_to_id.items()}
VOCAB_SIZE = len(char_to_id)

# 加载模型
model = None
model_version = "unknown"
MAX_LEN = 128

def load_model(version="v2"):
    global model, model_version
    if version == "v3":
        model_path = os.path.join(MODEL_DIR, 'qsm_v3_quantum.pth')
        config = {'d_model': 512, 'nhead': 8, 'num_layers': 6, 'dim_ff': 2048}
    else:
        model_path = os.path.join(MODEL_DIR, 'qsm_v2_quantum.pth')
        config = {'d_model': 256, 'nhead': 8, 'num_layers': 4, 'dim_ff': 1024}

    if os.path.exists(model_path):
        m = QSMModel(VOCAB_SIZE, max_len=MAX_LEN, **config)
        m.load_state_dict(torch.load(model_path, map_location='cpu'))
        m.eval()
        model = m
        model_version = version
        print(f"✅ 模型 {version} 加载成功 (参数: {sum(p.numel() for p in m.parameters()):,})")
    else:
        print(f"⚠️ 模型文件不存在: {model_path}")

# 尝试加载V2，后续可切换V3
try:
    load_model("v2")
except Exception as e:
    print(f"⚠️ V2模型加载失败: {e}")

# === API端点 ===
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "model_version": model_version,
        "vocab_size": VOCAB_SIZE
    })

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.json or {}
        text = data.get('text', '')
        direction = data.get('direction', 'zh2yi')  # zh2yi or yi2zh
        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Tokenize
        ids = [char_to_id.get(c, VOCAB_SIZE-1) for c in text[:MAX_LEN]]
        ids += [0] * (MAX_LEN - len(ids))
        x = torch.tensor([ids])

        # Inference
        with torch.no_grad():
            lm_out, task_out = model(x)

        pred_ids = lm_out.argmax(-1)[0].tolist()
        task_labels = ['翻译', '对话', '语法']
        task = task_labels[task_out.argmax().item()]

        # Decode
        result_chars = []
        for pid in pred_ids:
            if pid == 0:
                break
            ch = id_to_char.get(pid, '?')
            result_chars.append(ch)
        result = ''.join(result_chars)

        return jsonify({
            "input": text,
            "output": result,
            "task": task,
            "direction": direction,
            "model_version": model_version
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json or {}
        message = data.get('message', '')
        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Simple chat mode - use model to generate response
        ids = [char_to_id.get(c, VOCAB_SIZE-1) for c in message[:MAX_LEN]]
        ids += [0] * (MAX_LEN - len(ids))
        x = torch.tensor([ids])

        with torch.no_grad():
            lm_out, task_out = model(x)

        pred_ids = lm_out.argmax(-1)[0].tolist()
        result_chars = []
        for pid in pred_ids:
            if pid == 0:
                break
            ch = id_to_char.get(pid, '?')
            result_chars.append(ch)
        response = ''.join(result_chars)

        return jsonify({
            "message": message,
            "response": response,
            "model_version": model_version
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/model/switch', methods=['POST'])
def switch_model():
    """切换模型版本"""
    try:
        data = request.json or {}
        version = data.get('version', 'v2')
        load_model(version)
        return jsonify({"status": "ok", "model_version": model_version})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/model/info', methods=['GET'])
def model_info():
    return jsonify({
        "version": model_version,
        "vocab_size": VOCAB_SIZE,
        "max_len": MAX_LEN,
        "params": sum(p.numel() for p in model.parameters()) if model else 0,
        "available_models": {
            "v2": os.path.exists(os.path.join(MODEL_DIR, 'qsm_v2_quantum.pth')),
            "v3": os.path.exists(os.path.join(MODEL_DIR, 'qsm_v3_quantum.pth')),
        }
    })

@app.route('/compile', methods=['POST'])
def compile_qentl():
    """编译QEntL源码"""
    try:
        data = request.json or {}
        source = data.get('source', '')
        if not source:
            return jsonify({"error": "No source provided"}), 400

        import sys
        sys.path.insert(0, os.path.join(BASE_DIR, 'QEntL', 'System', 'Compiler'))
        from qentl_compiler_v3 import compile_qentl

        qbc = compile_qentl(source)
        return jsonify({
            "status": "compiled",
            "constants": len(qbc['constants']),
            "variables": len(qbc['variables']),
            "functions": len(qbc['functions']),
            "instructions": len(qbc['instructions']),
            "qbc": qbc
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)
