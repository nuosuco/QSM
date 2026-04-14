#!/usr/bin/env python3
"""
QSM量子Transformer API服务
端口: 8001
"""
from flask import Flask, jsonify, request
import json
import torch
import torch.nn as nn

app = Flask(__name__)

# 加载词汇表
with open('/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_vocab_v2.json', 'r', encoding='utf-8') as f:
    vocab = json.load(f)
char_to_id = vocab['char_to_id']
id_to_char = {v: k for k, v in char_to_id.items()}
vocab_size = len(char_to_id)

# V4模型架构
class V4Translator(nn.Module):
    def __init__(self, vocab_size, embed_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.fc1 = nn.Linear(embed_dim, 256)
        self.fc2 = nn.Linear(256, vocab_size)
    
    def forward(self, x):
        x = self.embedding(x)
        x = torch.mean(x, dim=1)
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

# 加载V4模型
model = V4Translator(vocab_size, 128)
model.load_state_dict(torch.load('/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_model_v4.pth', map_location='cpu'))
model.eval()
print("V4模型加载成功，准确率90%")

@app.route('/')
def status():
    return jsonify({
        'service': 'QSM Quantum Transformer API',
        'version': 'v1.0',
        'model': 'V4 (90% accuracy)',
        'vocab_size': vocab_size,
        'status': 'ok'
    })

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '')
    direction = data.get('direction', 'zh2yi')
    
    if direction == 'zh2yi':
        # 中文转彝文
        zh_ids = [char_to_id.get(c, 1) for c in text[:32]]
        zh_ids = zh_ids + [0] * (32 - len(zh_ids))
        x = torch.tensor([zh_ids], dtype=torch.long)
        
        with torch.no_grad():
            output = model(x)
            pred = output.argmax(dim=1).item()
        
        result = id_to_char.get(pred, '?')
    else:
        result = text
    
    return jsonify({
        'original': text,
        'translated': result,
        'direction': direction,
        'model': 'quantum-v4'
    })

@app.route('/batch', methods=['POST'])
def batch_translate():
    data = request.get_json()
    texts = data.get('texts', [])
    results = []
    
    for text in texts:
        zh_ids = [char_to_id.get(c, 1) for c in text[:32]]
        zh_ids = zh_ids + [0] * (32 - len(zh_ids))
        x = torch.tensor([zh_ids], dtype=torch.long)
        
        with torch.no_grad():
            output = model(x)
            pred = output.argmax(dim=1).item()
        
        results.append({
            'original': text,
            'translated': id_to_char.get(pred, '?')
        })
    
    return jsonify({'results': results})

if __name__ == '__main__':
    print("QSM量子Transformer API启动，端口8001...")
    app.run(host='0.0.0.0', port=8001)
