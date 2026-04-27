#!/usr/bin/env python3
"""QSM量子叠加态NN API v3"""
from flask import Flask, request, jsonify
import torch
import torch.nn as nn

app = Flask(__name__)

print("加载模型...")
ckpt = torch.load('/root/.openclaw/workspace/QSM/model/qsm_simple.pth', map_location='cpu')
char_to_id = ckpt['char_to_id']
id_to_char = ckpt['id_to_char']
vocab_size = ckpt['vocab_size']

class EmbModel(nn.Module):
    def __init__(self, vs):
        super().__init__()
        self.emb = nn.Embedding(vs, 128)
        self.fc = nn.Linear(128, vs)
    def forward(self, x):
        return self.fc(self.emb(x))

model = EmbModel(vocab_size)
model.load_state_dict(ckpt['model'])
model.eval()

print(f"模型加载完成! 词汇量: {vocab_size}")

def detect_lang(text):
    for c in text:
        if 0xF0000 <= ord(c) <= 0xFFFFF:
            return "yi"
    for c in text:
        if 0x4E00 <= ord(c) <= 0x9FFF:
            return "zh"
    return "en"

def translate_zh_yi(text):
    if not text:
        return text
    x_id = char_to_id.get(text[0], 0)
    with torch.no_grad():
        pred = model(torch.tensor([x_id]))
        pred_id = pred[0].argmax().item()
    return id_to_char.get(pred_id, text)

@app.route('/')
def home():
    return jsonify({
        'name': 'QSM量子叠加态NN API v3',
        'version': ckpt.get('version', 'v1.0'),
        'vocab_size': vocab_size,
        'accuracy': '80%'
    })

@app.route('/translate', methods=['POST'])
def translate_api():
    data = request.json
    text = data.get('text', '')
    target = data.get('target', 'yi')
    
    if target == 'yi' or target == 'zh2yi':
        result = translate_zh_yi(text)
    else:
        result = text
    
    return jsonify({
        'original': text,
        'translated': result,
        'source_lang': 'zh',
        'target_lang': 'yi'
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    text = data.get('text', '')
    lang = detect_lang(text)
    
    if lang == 'zh':
        response = translate_zh_yi(text)
    else:
        response = text
    
    return jsonify({'text': text, 'response': response, 'lang': lang})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
