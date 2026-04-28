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

app = Flask(__name__)
CORS(app)

# Paths
WORKSPACE = '/root/.openclaw/workspace'
V4_MODEL_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/qsm_v4_quantum_best.pth')
V4_VOCAB_PATH = os.path.join(WORKSPACE, 'Models/QSM/bin/v4_vocab.json')
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
    """使用V4模型翻译文本"""
    if model is None or vocab is None:
        return None, "模型未加载"
    
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
            
            return jsonify({
                "success": True,
                "output": output,
                "quantum_state": state_info,
                "n_qubits": n_qubits
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
            
            return jsonify({
                "success": True,
                "output": output,
                "quantum_state": state_info,
                "functions": qbc.get('functions', {}),
                "instructions_count": len(qbc.get('instructions', []))
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    
    return jsonify({"error": "Provide 'source' or 'gates' parameter"})

if __name__ == '__main__':
    print("=" * 50)
    print("  QSM V4 量子翻译API")
    print("  原则: 量子自举")
    print("=" * 50)
    
    loaded = load_v4_model()
    if loaded:
        print(f"✅ V4模型加载成功 (vocab={vocab_size})")
    else:
        print("⚠️ V4模型未找到，启动为编译服务模式")
    
    app.run(host='0.0.0.0', port=8002, debug=False)
