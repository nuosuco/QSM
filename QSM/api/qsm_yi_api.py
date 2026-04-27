#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM滇川黔桂通用彝文翻译API
使用真实训练的Transformer模型
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import torch
import torch.nn as nn
import json
import math

app = Flask(__name__)
CORS(app)

# 模型路径
MODEL_PATH = '/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_model.pth'
VOCAB_PATH = '/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_vocab.json'

# 全局变量
model = None
vocab = None
char_to_id = None
id_to_char = None

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=256):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)

class QuantumTransformerModel(nn.Module):
    def __init__(self, vocab_size, d_model=256, nhead=8, num_encoder_layers=3, dim_feedforward=1024, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_encoder_layers)
        self.decoder = nn.Linear(d_model, vocab_size)
    
    def forward(self, src):
        src = self.embedding(src) * math.sqrt(self.d_model)
        src = src.transpose(0, 1)
        src = self.pos_encoder(src)
        src = src.transpose(0, 1)
        output = self.transformer_encoder(src)
        output = self.decoder(output)
        return output

def load_model():
    global model, vocab, char_to_id, id_to_char
    
    try:
        # 加载词汇表
        with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)
        
        char_to_id = vocab_data['char_to_id']
        id_to_char = {v: k for k, v in char_to_id.items()}
        
        # 创建模型
        model = QuantumTransformerModel(len(char_to_id))
        
        # 加载权重
        state_dict = torch.load(MODEL_PATH, map_location='cpu')
        model.load_state_dict(state_dict)
        model.eval()
        
        print(f'模型加载成功！词汇量: {len(char_to_id)}')
        return True
    except Exception as e:
        print(f'模型加载失败: {e}')
        return False

def translate_char(char):
    """转换单个字符"""
    if char in char_to_id:
        input_id = torch.tensor([[char_to_id[char]]])
        with torch.no_grad():
            output = model(input_id)
            pred_id = output.argmax(dim=-1).item()
            if pred_id in id_to_char:
                return id_to_char[pred_id]
    return char

@app.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'service': 'QSM 滇川黔桂通用彝文翻译API',
        'model': 'QSM Transformer v1.0',
        'vocab_size': len(char_to_id) if char_to_id else 0,
        'yi_type': '滇川黔桂通用彝文',
        'unicode_range': 'U+F0000-U+FFFFF'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'vocab_size': len(char_to_id) if char_to_id else 0
    })

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json() or {}
    text = data.get('text', '')
    direction = data.get('direction', 'zh2yi')
    
    if not text:
        return jsonify({'error': '缺少text参数'}), 400
    
    if model is None:
        return jsonify({'error': '模型未加载'}), 500
    
    try:
        result = ''
        for char in text:
            result += translate_char(char)
        
        return jsonify({
            'translated': result,
            'original': text,
            'direction': direction,
            'yi_type': '滇川黔桂通用彝文'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('========================================')
    print('QSM 滇川黔桂通用彝文翻译API')
    print('========================================')
    print('正在加载模型...')
    
    if load_model():
        print('端口: 8000')
        print('彝文类型: 滇川黔桂通用彝文')
        print('Unicode范围: U+F0000-U+FFFFF')
        app.run(host='0.0.0.0', port=8000, debug=False)
    else:
        print('模型加载失败，API未启动')
