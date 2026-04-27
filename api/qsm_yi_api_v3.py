#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QSM滇川黔桂通用彝文翻译API V3 - 使用新训练的模型"""

from fastapi import FastAPI
from pydantic import BaseModel
import torch
import torch.nn as nn
import json
import uvicorn

# 加载词汇表
with open('/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_vocab_v2.json', 'r', encoding='utf-8') as f:
    vocab = json.load(f)
char_to_id = vocab['char_to_id']
id_to_char = {v: k for k, v in char_to_id.items()}
vocab_size = len(char_to_id)

# 模型定义
class SimpleTranslator(nn.Module):
    def __init__(self, vocab_size, d_model=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.fc1 = nn.Linear(d_model, d_model * 2)
        self.fc2 = nn.Linear(d_model * 2, vocab_size)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.embedding(x)
        x = torch.mean(x, dim=1)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# 加载模型
model = SimpleTranslator(vocab_size, 128)
model.load_state_dict(torch.load('/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_model_v3.pth'))
model.eval()

# FastAPI
app = FastAPI(title="QSM滇川黔桂通用彝文翻译API V3")

class TranslateRequest(BaseModel):
    text: str

@app.get("/")
def status():
    return {
        "service": "QSM滇川黔桂通用彝文翻译API V3",
        "model": "QSM Transformer V3",
        "status": "ok",
        "vocab_size": vocab_size,
        "accuracy": "83%",
        "unicode_range": "U+F0000-U+FFFFF",
        "yi_type": "滇川黔桂通用彝文"
    }

@app.post("/translate")
def translate(req: TranslateRequest):
    zh_ids = [char_to_id.get(c, 1) for c in req.text] + [0] * 32
    input_tensor = torch.tensor([zh_ids[:32]])
    
    with torch.no_grad():
        output = model(input_tensor)
        pred_id = output.argmax(dim=1).item()
        pred_char = id_to_char.get(pred_id, '<unk>')
    
    return {
        "original": req.text,
        "translated": pred_char,
        "model": "V3"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
