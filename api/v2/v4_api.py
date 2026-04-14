from flask import Flask, jsonify, request
import json
import torch
import torch.nn as nn

app = Flask(__name__)

# 加载词汇表
with open('/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_vocab_v2.json', 'r') as f:
    vocab = json.load(f)

char_to_id = vocab['char_to_id']
id_to_char = {v: k for k, v in char_to_id.items()}
vocab_size = len(char_to_id)

# 定义模型结构（与V4保存时一致）
class M(nn.Module):
    def __init__(self, vocab_size, d=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d, padding_idx=0)
        self.fc1 = nn.Linear(d, 256)
        self.fc2 = nn.Linear(256, vocab_size)
    
    def forward(self, x):
        x = self.embedding(x)
        x = torch.mean(x, dim=1)
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

# 加载模型
model = M(vocab_size)
model.load_state_dict(torch.load('/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_model_v4.pth', map_location='cpu'))
model.eval()

@app.route('/')
def status():
    return jsonify({
        'service': 'V Series',
        'model': 'V4',
        'series': 'V',
        'accuracy': '90%',
        'port': 8001,
        'vocab_size': vocab_size
    })

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '')
    direction = data.get('direction', 'zh2yi')
    
    # 编码输入
    ids = [char_to_id.get(c, 1) for c in text[:32]]
    ids = ids + [0] * (32 - len(ids))
    x = torch.tensor([ids], dtype=torch.long)
    
    # 推理
    with torch.no_grad():
        output = model(x)
        pred_id = output.argmax(1).item()
    
    # 解码输出
    translated = id_to_char.get(pred_id, '?')
    
    return jsonify({
        'original': text,
        'translated': translated,
        'model': 'V4',
        'direction': direction
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
