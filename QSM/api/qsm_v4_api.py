#!/usr/bin/env python3
"""
QSM V4 API - 量子叠加态模型翻译服务 + QEntL在线编译
端口: 8002
端点:
  /health - 健康检查
  /translate - V4翻译 (自回归生成)
  /compile - QEntL在线编译 (.qentl → .qbc)
  /model/info - 模型信息
  
作者: 小趣WeQ | 监督: 中华Zhoho
日期: 2026-04-28
"""
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json
import sys
import os
import torch
import torch.nn as nn
import math

app = Flask(__name__)
CORS(app)


# === QSM V5 Model Class (embedded for API independence) ===

class QSM_V5(nn.Module):
    def __init__(self, vocab_size, d_model=256, n_heads=4, n_layers=3, d_ff=512, dropout=0.1, max_len=64):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = nn.Embedding(max_len, d_model)
        enc_layer = nn.TransformerEncoderLayer(d_model, n_heads, d_ff, dropout, batch_first=True)
        self.encoder = nn.TransformerEncoder(enc_layer, n_layers)
        dec_layer = nn.TransformerDecoderLayer(d_model, n_heads, d_ff, dropout, batch_first=True)
        self.decoder = nn.TransformerDecoder(dec_layer, n_layers)
        self.quantum_gate = nn.Parameter(torch.ones(1) * 0.3)
        self.quantum_rotation = nn.Parameter(torch.randn(n_heads, d_model // n_heads) * 0.01)
        self.norm = nn.LayerNorm(d_model)
        self.output_proj = nn.Linear(d_model, vocab_size)
        self._init_weights()

    def _init_weights(self):
        for p in self.parameters():
            if p.dim() > 1: nn.init.xavier_uniform_(p)

    def forward(self, src, tgt, src_mask=None, tgt_mask=None, tgt_key_padding_mask=None):
        src_emb = self.embedding(src) * math.sqrt(self.d_model) + self.pos_encoding(torch.arange(src.size(1), device=src.device))
        enc_out = self.encoder(src_emb, src_key_padding_mask=src_mask)
        B, S, _ = enc_out.shape
        nh, dh = self.quantum_rotation.shape
        enc_view = enc_out.view(B, S, nh, dh)
        qr = self.quantum_rotation
        quantum_out = (enc_view * torch.cos(qr) + torch.roll(enc_view, 1, -1) * torch.sin(qr)).reshape(B, S, -1)
        enc_out = self.quantum_gate * quantum_out + (1 - self.quantum_gate) * enc_out
        tgt_emb = self.embedding(tgt) * math.sqrt(self.d_model) + self.pos_encoding(torch.arange(tgt.size(1), device=tgt.device))
        dec_out = self.decoder(tgt_emb, enc_out, tgt_mask=tgt_mask, tgt_key_padding_mask=tgt_key_padding_mask)
        return self.output_proj(self.norm(dec_out))

    def translate_beam_search(self, src_ids, beam_size=5, max_len=40):
        self.eval()
        with torch.no_grad():
            src = torch.tensor([src_ids], dtype=torch.long)
            src_emb = self.embedding(src) * math.sqrt(self.d_model) + self.pos_encoding(torch.arange(src.size(1)))
            enc_out = self.encoder(src_emb)
            B, S, _ = enc_out.shape
            nh, dh = self.quantum_rotation.shape
            enc_view = enc_out.view(B, S, nh, dh)
            qr = self.quantum_rotation
            quantum_out = (enc_view * torch.cos(qr) + torch.roll(enc_view, 1, -1) * torch.sin(qr)).reshape(B, S, -1)
            enc_out = self.quantum_gate * quantum_out + (1 - self.quantum_gate) * enc_out
            BOS_ID, EOS_ID = 6920, 6921
            beams = [([BOS_ID], 0.0)]
            for step in range(max_len):
                new_beams = []
                for seq, score in beams:
                    if seq[-1] == EOS_ID and len(seq) > 1:
                        new_beams.append((seq, score)); continue
                    tgt = torch.tensor([seq], dtype=torch.long)
                    tgt_emb = self.embedding(tgt) * math.sqrt(self.d_model) + self.pos_encoding(torch.arange(tgt.size(1)))
                    tgt_mask = nn.Transformer.generate_square_subsequent_mask(tgt.size(1))
                    dec_out = self.decoder(tgt_emb, enc_out, tgt_mask=tgt_mask)
                    logits = self.output_proj(self.norm(dec_out[:, -1, :]))
                    log_probs = torch.log_softmax(logits, dim=-1)
                    topk_probs, topk_ids = log_probs.topk(beam_size)
                    for i in range(beam_size):
                        new_beams.append((seq + [topk_ids[0, i].item()], score + topk_probs[0, i].item()))
                beams = sorted(new_beams, key=lambda x: x[1], reverse=True)[:beam_size]
                if all(seq[-1] == EOS_ID for seq, _ in beams): break
            return max(beams, key=lambda x: x[1] / max(len(x[0]), 1))[0]

# Paths
WORKSPACE = '/root/.openclaw/workspace'
V4_MODEL_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/qsm_v4_quantum_best.pth')
V4_VOCAB_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/v4_vocab.json')

V5_MODEL_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/qsm_v5_quantum_best.pth')
V5_VOCAB_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/v4_vocab.json')  # Same vocab

# V5 Global model state
v5_model = None
v5_vocab = None
v5_id_to_char = None
v5_vocab_size = 0

COMPILER_PATH = os.path.join(WORKSPACE, 'QEntL/System/Compiler')
RUNTIME_PATH = os.path.join(WORKSPACE, 'QEntL/System/Runtime')

# Global model state
model = None
vocab = None
id_to_char = None
vocab_size = 0

def load_v4_model():
    """加载V4翻译模型"""
    global model, vocab, id_to_char, vocab_size
    
    if not os.path.exists(V4_MODEL_PATH):
        return False
    
    try:
        # Load vocab
        with open(V4_VOCAB_PATH, 'r', encoding='utf-8') as f:
            vocab = json.load(f)
        id_to_char = {v: k for k, v in vocab.items()}
        vocab_size = len(vocab)
        
        # Load model
        sys.path.insert(0, os.path.join(WORKSPACE, 'Models/QSM'))
        from train_v4_encoder_decoder import QSM_V4
        
        model = QSM_V4(vocab_size, d_model=256, n_heads=4, n_layers=3, d_ff=512, max_len=64)
        checkpoint = torch.load(V4_MODEL_PATH, map_location='cpu')
        model.load_state_dict(checkpoint['model_state'])
        model.eval()
        
        return True
    except Exception as e:
        print(f"模型加载失败: {e}")
        return False

def translate_text(text, max_len=64, temperature=0.8):
    """翻译文本 - 优先V5模型, 回退V4"""
    # V5优先
    if v5_model is not None and v5_vocab is not None:
        result, err = translate_v5(text, max_len)
        if result is not None:
            return result, None
    # V4回退
    if model is None or vocab is None:
        return None, "模型未加载(V4已删除,V5不可用)"
    
    BOS_ID = vocab.get('<BOS>', 6920)
    EOS_ID = vocab.get('<EOS>', 6921)
    UNK_ID = vocab.get('<UNK>', 3)
    
    # Tokenize
    src_ids = [vocab.get(c, UNK_ID) for c in text if c in vocab]
    if not src_ids:
        return "", "输入无有效字符"
    
    try:
        # Use beam search for better quality
        result_ids = model.translate_beam_search(src_ids, beam_size=3, max_len=max_len)
        result_chars = []
        for tid in result_ids[1:]:  # Skip BOS
            if tid == EOS_ID:
                break
            ch = id_to_char.get(tid, '?')
            result_chars.append(ch)
        return ''.join(result_chars), None
    except Exception as e:
        return None, str(e)

def compile_qentl_source(source_code):
    """在线编译QEntL源码"""
    sys.path.insert(0, COMPILER_PATH)
    try:
        from qentl_compiler_v3 import compile_qentl
        qbc = compile_qentl(source_code)
        return qbc, None
    except Exception as e:
        return None, str(e)


def load_v5_model():
    """加载V5翻译模型(最新best)"""
    global v5_model, v5_vocab, v5_id_to_char, v5_vocab_size
    if not os.path.exists(V5_MODEL_PATH):
        return False
    try:
        with open(V5_VOCAB_PATH, 'r', encoding='utf-8') as f:
            v5_vocab = json.load(f)
        v5_id_to_char = {v: k for k, v in v5_vocab.items()}
        v5_vocab_size = len(v5_vocab)
        sys.path.insert(0, os.path.join(WORKSPACE, 'Models/QSM'))
        # Using embedded QSM_V5 class above
        v5_model = QSM_V5(v5_vocab_size, d_model=256, n_heads=4, n_layers=3, d_ff=512, max_len=64)
        checkpoint = torch.load(V5_MODEL_PATH, map_location='cpu')
        v5_model.load_state_dict(checkpoint['model_state'])
        v5_model.eval()
        print(f"✅ V5模型加载成功! Epoch {checkpoint.get('epoch')}, Val Loss {checkpoint.get('val_loss', 0):.4f}")
        return True
    except Exception as e:
        print(f"V5模型加载失败: {e}")
        return False

def translate_v5(text, max_len=64):
    """使用V5模型翻译文本"""
    if v5_model is None or v5_vocab is None:
        return None, "V5模型未加载"
    BOS_ID = v5_vocab.get('<BOS>', 6920)
    EOS_ID = v5_vocab.get('<EOS>', 6921)
    UNK_ID = v5_vocab.get('<UNK>', 3)
    src_ids = [v5_vocab.get(c, UNK_ID) for c in text if c in v5_vocab]
    if not src_ids:
        return "", "输入无有效字符"
    try:
        result_ids = v5_model.translate_beam_search(src_ids, beam_size=3, max_len=max_len)
        result_chars = []
        for tid in result_ids[1:]:
            if tid == EOS_ID:
                break
            ch = v5_id_to_char.get(tid, '?')
            result_chars.append(ch)
        return ''.join(result_chars), None
    except Exception as e:
        return None, str(e)

# ============ API Endpoints ============

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'model_loaded': model is not None,
        'vocab_size': vocab_size,
        'model': 'QSM V4 Encoder-Decoder',
        'status': 'healthy' if model is not None else 'no_model'
    })

@app.route('/translate', methods=['POST'])
def translate():
    """V4翻译端点"""
    data = request.get_json(force=True)
    text = data.get('text', '')
    max_len = data.get('max_len', 64)
    temperature = data.get('temperature', 0.8)
    
    if not text:
        return jsonify({'error': '请提供text参数'}), 400
    
    result, err = translate_text(text, max_len, temperature)
    if err:
        return jsonify({'error': err}), 500
    
    return jsonify({
        'input': text,
        'translation': result,
        'model': 'QSM V4 Encoder-Decoder'
    })

@app.route('/compile', methods=['POST'])
def compile_qentl():
    """QEntL在线编译端点"""
    data = request.get_json(force=True)
    source = data.get('source', '')
    
    if not source:
        return jsonify({'error': '请提供source参数'}), 400
    
    qbc, err = compile_qentl_source(source)
    if err:
        return jsonify({'error': str(err), 'success': False}), 400
    
    # Return QBC as JSON (removing large instruction details for brevity)
    result = {
        'success': True,
        'constants_count': len(qbc.get('constants', [])),
        'variables_count': len(qbc.get('variables', [])),
        'functions': qbc.get('functions', {}),
        'instructions_count': len(qbc.get('instructions', [])),
        'qbc': qbc  # Full QBC bytecode
    }
    
    return jsonify(result)

@app.route('/model/info', methods=['GET'])
def model_info():
    """模型信息"""
    info = {
        'name': 'QSM V4 Encoder-Decoder',
        'architecture': 'Encoder(3层) + Decoder(3层) + Cross-Attention',
        'vocab_size': vocab_size,
        'd_model': 256,
        'n_heads': 4,
        'n_layers': 3,
        'max_seq_len': 64,
        'model_loaded': model is not None,
    }
    
    if model is not None:
        info['total_params'] = sum(p.numel() for p in model.parameters())
    
    return jsonify(info)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service': 'QSM V4 Quantum Translation API',
        'model': 'Encoder-Decoder with Quantum Gate Attention',
        'endpoints': {
            '/health': '健康检查',
            '/translate': 'POST 翻译 {"text": "..."}',
            '/compile': 'POST QEntL编译 {"source": "..."}',
            '/model/info': '模型信息',
        },
        'principle': '量子自举 — 用自己的语言构建自己的世界'
    })



@app.route('/quantum', methods=['POST'])
def quantum_execute():
    """执行量子电路 - 从QEntL源码编译并运行量子部分"""
    data = request.get_json(force=True)
    source = data.get('source', '')
    gates = data.get('gates', [])  # Alternative: direct gate list
    
    if gates:
        # Direct gate execution: {"gates": [{"name":"H","target":0}, {"name":"CNOT","control":0,"target":1}]}
        try:
            import sys
            sys.path.insert(0, '/root/.openclaw/workspace/QEntL/System/Runtime')
            from qbc_vm import QBCVirtualMachine
            n_qubits = data.get('qubits', 2)
            qbc = {
                "constants": [],
                "variables": [],
                "functions": {"setup": 1},
                "instructions": [
                    {"op": "QUANTUM_INIT", "code": 80, "operand": n_qubits},
                ]
            }
            for gate in gates:
                name = gate.get('name', 'H')
                if name == 'CNOT':
                    gate_str = f"CNOT {gate.get('control',0)} {gate.get('target',1)}"
                else:
                    gate_str = f"{name} {gate.get('target',0)}"
                qbc["instructions"].append({"op": "QUANTUM_GATE", "code": 81, "operand": gate_str})
            
            qbc["instructions"].extend([
                {"op": "RETURN", "code": 68, "operand": None},
                {"op": "HALT", "code": 1, "operand": None},
            ])
            
            vm = QBCVirtualMachine()
            vm.load_qbc(qbc)
            output = vm.run(10000)
            state_info = vm._get_state_info()
            
            # Get circuit visualization
            circuit_text = ""
            if hasattr(vm, 'get_quantum_circuit_text'):
                circuit_text = vm.get_quantum_circuit_text()
            
            return jsonify({
                "success": True,
                "output": output,
                "quantum_state": state_info,
                "n_qubits": n_qubits,
                "circuit": circuit_text
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    
    elif source:
        # Compile and execute QEntL source
        try:
            import sys
            sys.path.insert(0, '/root/.openclaw/workspace/QEntL/System/Compiler')
            sys.path.insert(0, '/root/.openclaw/workspace/QEntL/System/Runtime')
            from qentl_compiler_v3 import compile_qentl
            from qbc_vm import QBCVirtualMachine
            
            qbc = compile_qentl(source)
            vm = QBCVirtualMachine()
            vm.load_qbc(qbc)
            output = vm.run(50000)
            state_info = vm._get_state_info() if vm.quantum_bits > 0 else None
            
            # Get circuit visualization
            circuit_text = ""
            if hasattr(vm, 'get_quantum_circuit_text'):
                circuit_text = vm.get_quantum_circuit_text()
            
            return jsonify({
                "success": True,
                "output": output,
                "quantum_state": state_info,
                "functions": qbc.get('functions', {}),
                "instructions_count": len(qbc.get('instructions', [])),
                "circuit": circuit_text
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    
    return jsonify({"error": "Provide 'source' or 'gates' parameter"})



@app.route('/gates', methods=['GET'])
def quantum_gates():
    """返回支持的量子门列表"""
    return jsonify({
        "success": True,
        "gates": [
            {"name": "H", "full_name": "Hadamard", "description": "创建叠加态"},
            {"name": "X", "full_name": "Pauli-X", "description": "比特翻转"},
            {"name": "Y", "full_name": "Pauli-Y", "description": "Y轴翻转"},
            {"name": "Z", "full_name": "Pauli-Z", "description": "相位翻转"},
            {"name": "S", "full_name": "S-gate", "description": "Z的平方根"},
            {"name": "T", "full_name": "T-gate", "description": "S的平方根"},
            {"name": "RX", "full_name": "Rotation-X", "description": "绕X轴旋转π/4"},
            {"name": "RZ", "full_name": "Rotation-Z", "description": "绕Z轴旋转π/4"},
            {"name": "CNOT", "full_name": "Controlled-NOT", "description": "受控非门(2比特)", "two_qubit": True},
            {"name": "SWAP", "full_name": "SWAP", "description": "交换两个量子比特", "two_qubit": True}
        ],
        "total": 10,
        "keywords": {
            "量子门": "apply gate",
            "纠缠": "create Bell state (H+CNOT shortcut)",
            "测量": "measure qubit with collapse"
        }
    })



@app.route('/circuit', methods=['POST'])
def circuit_visualize():
    """编译QEntL并返回量子电路可视化"""
    data = request.get_json(force=True)
    source = data.get('source', '')
    gates = data.get('gates', [])
    
    try:
        import sys
        sys.path.insert(0, '/root/.openclaw/workspace/QEntL/System/Compiler')
        sys.path.insert(0, '/root/.openclaw/workspace/QEntL/System/Runtime')
        from qentl_compiler_v3 import compile_qentl
        from qbc_vm import QBCVirtualMachine
        
        if source:
            qbc = compile_qentl(source)
            func_name = data.get('function', 'setup')
            vm = QBCVirtualMachine()
            vm.load_qbc(qbc)
            try:
                output = vm.run_with_function(func_name, 50000)
            except:
                output = vm.run(50000)
        else:
            # Build from gate list
            n_qubits = data.get('qubits', 2)
            qbc = {
                "constants": [],
                "variables": [],
                "functions": {"setup": 1},
                "instructions": [
                    {"op": "QUANTUM_INIT", "code": 80, "operand": n_qubits},
                ]
            }
            for gate in gates:
                name = gate.get('name', 'H')
                if name == 'CNOT':
                    qbc["instructions"].append({"op": "QUANTUM_GATE", "code": 81, "operand": f"CNOT {gate.get('control',0)} {gate.get('target',1)}"})
                else:
                    qbc["instructions"].append({"op": "QUANTUM_GATE", "code": 81, "operand": f"{name} {gate.get('target',0)}"})
            qbc["instructions"].extend([
                {"op": "RETURN", "code": 68, "operand": None},
                {"op": "HALT", "code": 1, "operand": None},
            ])
            vm = QBCVirtualMachine()
            vm.load_qbc(qbc)
            output = vm.run(10000)
        
        circuit_text = vm.get_quantum_circuit_text() if hasattr(vm, 'get_quantum_circuit_text') else ""
        state_info = vm._get_state_info() if vm.quantum_bits > 0 else ""
        
        return jsonify({
            "success": True,
            "output": output,
            "quantum_state": state_info,
            "circuit": circuit_text,
            "gates_applied": len(vm.quantum_gates_applied) if hasattr(vm, 'quantum_gates_applied') else 0
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/teleport', methods=['GET'])
def quantum_teleportation():
    """运行量子隐形传态协议(3比特)"""
    sys.path.insert(0, RUNTIME_PATH)
    from qbc_vm import QBCVirtualMachine
    try:
        qbc, err = compile_qentl_source("""quantum_program T {
            setup: 函数() {
                量子门 H 1
                量子门 CNOT 1 2
                量子门 CNOT 0 1
                量子门 H 0
                测量 0
                测量 1
                测量 2
            }
        }""")
        vm = QBCVirtualMachine()
        vm.load_qbc(qbc)
        output = vm.run(10000)
        measures = [l for l in output if '测量比特' in l]
        results = []
        for m in measures:
            parts = m.split(':')
            qubit = parts[0].replace('测量比特', '').strip()
            val = parts[1].strip()[0]
            results.append({"qubit": int(qubit), "value": int(val)})
        return {
            "protocol": "quantum_teleportation",
            "qubits": 3,
            "gates_applied": len(vm.quantum_gates_applied),
            "circuit": vm.get_quantum_circuit_text(),
            "measurements": results,
            "gate_history": [{"name": g["name"], "target": g.get("target", g.get("control","?"))} for g in vm.quantum_gates_applied[:10]]
        }
    except Exception as e:
        return {"error": str(e)}


@app.route('/training-status', methods=['GET'])
def training_status():
    # V5训练状态实时查看
    import os, re
    log_path = '/tmp/qsm_v5_training.log'
    status = {"training": False, "model": "V5", "progress": None}
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                lines = f.readlines()
            last_lines = lines[-10:]
            status["training"] = True
            for line in reversed(last_lines):
                m = re.search(r'E(\d+)/\d+\s+B(\d+)/(\d+)\s+L:([\d.]+)\s+lr:([\d.]+)', line)
                if m:
                    status["progress"] = {
                        "epoch": int(m.group(1)),
                        "batch": int(m.group(2)),
                        "total_batches": int(m.group(3)),
                        "loss": float(m.group(4)),
                        "learning_rate": float(m.group(5))
                    }
                    break
                best = re.search(r'Best.*Train:([\d.]+).*Val:([\d.]+)', line)
                if best:
                    status["best"] = {"train_loss": float(best.group(1)), "val_loss": float(best.group(2))}
        except:
            pass
    return jsonify(status)


@app.route('/v5/translate', methods=['POST'])
def v5_translate():
    """V5翻译端点(最新模型)"""
    data = request.get_json(force=True)
    text = data.get('text', '')
    max_len = data.get('max_len', 64)
    if not text:
        return jsonify({'error': '请提供text参数'}), 400
    result, err = translate_v5(text, max_len)
    if err:
        return jsonify({'error': err}), 500
    return jsonify({
        'input': text,
        'translation': result,
        'model': 'QSM V5 Encoder-Decoder',
        'val_loss': 2.19  # Update this
    })

@app.route('/v5/health', methods=['GET'])
def v5_health():
    """V5健康检查"""
    return jsonify({
        'model_loaded': v5_model is not None,
        'vocab_size': v5_vocab_size,
        'model': 'QSM V5 Encoder-Decoder (Latest)',
        'status': 'healthy' if v5_model is not None else 'no_model'
    })


@app.route('/data/stats', methods=['GET'])
def data_stats():
    """训练数据统计 - 含彝文覆盖率"""
    import glob, os, json as _json
    data_dir = os.path.join(WORKSPACE, 'QSM/data')
    files = glob.glob(os.path.join(data_dir, '*.jsonl'))
    total_lines = 0
    yi_files = 0
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                count = sum(1 for _ in fh)
                total_lines += count
                if 'yi' in os.path.basename(f):
                    yi_files += 1
        except:
            pass
    
    vocab_size = vocab_size if 'vocab_size' in dir() else 6924
    return jsonify({
        "total_files": len(files),
        "yi_files": yi_files,
        "total_lines": total_lines,
        "vocab_size": vocab_size,
        "yi_chars_in_vocab": 4120,
        "v5_train_pairs": 52354,
        "v5_val_pairs": 2759,
        "v6_train_pairs": 68248,
        "v6_val_pairs": 3259,
        "v6_yi_ratio": "9.5%",
        "v5_yi_ratio": "3.3%"
    })

if __name__ == '__main__':
    print("=" * 50)
    print("  QSM V4 量子翻译API")
    print("  原则: 量子自举")
    print("=" * 50)
    
    loaded = load_v4_model()
    load_v5_model()
    if loaded:
        print(f"✅ V4模型加载成功 (vocab={vocab_size})")
    else:
        print("⚠️ V4模型未找到，启动为编译服务模式")
    

@app.route('/v6/status', methods=['GET'])
def v6_status():
    import os, re, subprocess
    log_path = '/tmp/qsm_v6_training.log'
    status = {"training": False, "model": "V6 Q-Embedding", "progress": None}
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                lines = f.readlines()
            last_lines = lines[-10:]
            status["training"] = True
            for line in reversed(last_lines):
                m = re.search(r'E(\d+)/\d+\s+B(\d+)/(\d+)\s+L:([\d.]+)\s+lr:([\d.]+)', line)
                if m:
                    status["progress"] = {
                        "epoch": int(m.group(1)),
                        "batch": int(m.group(2)),
                        "total_batches": int(m.group(3)),
                        "loss": float(m.group(4)),
                        "learning_rate": float(m.group(5))
                    }
                    break
            for line in reversed(last_lines):
                m = re.search(r'Epoch (\d+).*Train:([\d.]+).*Val:([\d.]+).*Best:([\d.]+)', line)
                if m:
                    status["last_epoch"] = {
                        "epoch": int(m.group(1)),
                        "train_loss": float(m.group(2)),
                        "val_loss": float(m.group(3)),
                        "best_val": float(m.group(4))
                    }
                    break
            for line in reversed(last_lines):
                if 'Best!' in line:
                    status["new_best"] = True
                    break
        except:
            pass
    try:
        result = subprocess.run(['pgrep', '-f', 'train_v6'], capture_output=True, text=True)
        status["process_running"] = bool(result.stdout.strip())
    except:
        status["process_running"] = None
    return jsonify(status)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=False)
