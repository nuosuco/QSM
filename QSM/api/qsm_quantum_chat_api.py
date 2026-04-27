#!/usr/bin/env python3
"""
QSM量子叠加态聊天API
真正的三语对话：彝文→彝文，中文→中文，英文→英文
"""
from flask import Flask, request, jsonify
import numpy as np
import sys
sys.path.insert(0, '/root/.openclaw/workspace/QSM/model')

app = Flask(__name__)

# 导入量子聊天模型
from quantum_superposition_nn import QuantumChatModel, QuantumSuperpositionNN

print("加载量子叠加态对话模型...")
chat_model = QuantumChatModel()
print("模型加载完成!")

def detect_lang(text):
    """检测语言"""
    for c in text:
        if 0xF0000 <= ord(c) <= 0xFFFFF:
            return "yi"
    for c in text:
        if 0x4E00 <= ord(c) <= 0x9FFF:
            return "zh"
    return "en"

@app.route('/')
def home():
    return jsonify({
        'name': 'QSM量子叠加态聊天API',
        'version': 'quantum_v1.0',
        'description': '真正的三语对话模型',
        'modes': ['chat', 'translate']
    })

@app.route('/chat', methods=['POST'])
def chat():
    """三语对话接口"""
    data = request.json
    text = data.get('text', '')
    lang = detect_lang(text)
    
    # 使用量子叠加态模型对话
    response = chat_model.chat(text)
    
    return jsonify({
        'text': text,
        'response': response,
        'lang': lang,
        'mode': 'quantum_chat'
    })

@app.route('/translate', methods=['POST'])
def translate():
    """翻译接口（使用原来的Embedding模型）"""
    import torch
    import torch.nn as nn
    
    data = request.json
    text = data.get('text', '')
    target = data.get('target', 'yi')
    
    # 加载翻译模型
    ckpt = torch.load('/root/.openclaw/workspace/QSM/model/qsm_simple.pth', map_location='cpu')
    c2id = ckpt['char_to_id']
    id2c = {k: v for k, v in ckpt['id_to_char'].items()}
    vs = ckpt['vocab_size']
    
    class EmbModel(nn.Module):
        def __init__(self, vs):
            super().__init__()
            self.emb = nn.Embedding(vs, 128)
            self.fc = nn.Linear(128, vs)
        def forward(self, x):
            return self.fc(self.emb(x))
    
    m = EmbModel(vs)
    m.load_state_dict(ckpt['model'])
    m.eval()
    
    # 翻译第一个字
    if text and text[0] in c2id:
        x = torch.tensor([c2id[text[0]]])
        with torch.no_grad():
            p = m(x)[0].argmax().item()
        result = id2c.get(p, text)
    else:
        result = text
    
    return jsonify({
        'original': text,
        'translated': result,
        'source_lang': detect_lang(text),
        'target_lang': target,
        'mode': 'translate'
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)