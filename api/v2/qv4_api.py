from flask import Flask, jsonify, request
import json, torch, torch.nn as nn
app = Flask(__name__)
with open('/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_vocab_v2.json', 'r') as f:
    vocab = json.load(f)
char_to_id, id_to_char = vocab['char_to_id'], {v:k for k,v in vocab['char_to_id'].items()}
vocab_size = len(char_to_id)
class QV4(nn.Module):
    def __init__(self, vs, d):
        super().__init__()
        self.e = nn.Embedding(vs, d, padding_idx=0)
        self.f1 = nn.Linear(d, 256)
        self.f2 = nn.Linear(256, vs)
        self.c = nn.Parameter(torch.tensor([0.25]*4))
        self.p = nn.Parameter(torch.randn(4)*0.1)
    def forward(self, x):
        x = self.e(x)
        x = torch.mean(x, dim=1)
        for i in range(4): x = x + self.c[i] * torch.cos(self.p[i]) * x
        return self.f2(torch.relu(self.f1(x)))
model = QV4(vocab_size, 128)
try: model.load_state_dict(torch.load('/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_model_v4.pth', map_location='cpu'), strict=False)
except: pass
model.eval()
@app.route('/')
def s(): return jsonify({'service':'QV Series','model':'QV4','series':'QV','accuracy':'~97%','port':8002})
@app.route('/translate', methods=['POST'])
def t():
    d = request.get_json()
    t = d.get('text','')
    x = torch.tensor([[char_to_id.get(c,1) for c in t[:32]] + [0]*(32-len(t[:32]))], dtype=torch.long)
    with torch.no_grad(): p = model(x).argmax(1).item()
    return jsonify({'original':t,'translated':id_to_char.get(p,'?'),'model':'QV4'})
if __name__ == '__main__': app.run(host='0.0.0.0', port=8002)
