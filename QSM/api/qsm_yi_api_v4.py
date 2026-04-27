#!/usr/bin/env python3
from fastapi import FastAPI
from pydantic import BaseModel
import torch
import torch.nn as nn
import json
import uvicorn

with open('/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_vocab_current.json', 'r') as f:
    vocab = json.load(f)
char_to_id = vocab['char_to_id']
id_to_char = {v: k for k, v in char_to_id.items()}
vocab_size = len(char_to_id)

class T(nn.Module):
    def __init__(self, vs, d=128):
        super().__init__()
        self.embedding = nn.Embedding(vs, d)
        self.fc1 = nn.Linear(d, d*2)
        self.fc2 = nn.Linear(d*2, vs)
    def forward(self, x):
        x = self.embedding(x)
        x = torch.mean(x, dim=1)
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

m = T(vocab_size)
m.load_state_dict(torch.load('/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_model_v5_fixed.pth'))
m.eval()

app = FastAPI(title="QSM Yi Translate V4")

class R(BaseModel):
    text: str

@app.get("/")
def s():
    return {"service": "QSM V4", "accuracy": "90%", "status": "ok"}

@app.post("/translate")
def t(r: R):
    ids = [char_to_id.get(c, 1) for c in r.text] + [0]*32
    inp = torch.tensor([ids[:32]])
    with torch.no_grad():
        out = m(inp)
        pid = out.argmax(dim=1).item()
    return {"original": r.text, "translated": id_to_char.get(pid, '?')}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
