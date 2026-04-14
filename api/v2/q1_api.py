from flask import Flask, jsonify, request
import json, math, random
app = Flask(__name__)
with open('/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_vocab_v2.json', 'r') as f:
    vocab = json.load(f)
char_to_id, id_to_char = vocab['char_to_id'], {v:k for k,v in vocab['char_to_id'].items()}
vs, ed, nb = len(char_to_id), 64, 4
coef = [0.25]*4
ph = [random.random()*2*math.pi for _ in range(4)]
emb = [[[random.gauss(0,0.1) for _ in range(ed)] for _ in range(vs)] for _ in range(nb)]
ow = [[random.gauss(0,0.1) for _ in range(ed)] for _ in range(vs)]
def predict(x):
    h = [0.0]*ed
    for t in x[:16]:
        for b in range(nb):
            if t < vs:
                for i in range(ed): h[i] += coef[b]*math.cos(ph[b])*emb[b][t][i]
    n = math.sqrt(sum(i*i for i in h)+1e-8)
    h = [i/n for i in h]
    out = [sum(h[j]*ow[i][j] for j in range(ed)) for i in range(vs)]
    return out.index(max(out))
@app.route('/')
def s(): return jsonify({'service':'Q Series','model':'Q1','series':'Q','accuracy':'training','port':8000,'num_basis':4})
@app.route('/translate', methods=['POST'])
def t():
    d = request.get_json()
    tx = d.get('text','')
    x = [char_to_id.get(c,1) for c in tx[:32]] + [0]*(32-len(tx[:32]))
    p = predict(x)
    return jsonify({'original':tx,'translated':id_to_char.get(p,'?'),'model':'Q1'})
if __name__ == '__main__': app.run(host='0.0.0.0', port=8000)
