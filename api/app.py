"""
QNT API - Flask REST + WebSocket
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time


app = Flask(__name__)
CORS(app)


# ============ Blockchain API ============
@app.route('/api/blockchain/status', methods=['GET'])
def blockchain_status():
    """获取区块链状态"""
    from core.chain import QNTChain
    chain = QNTChain()
    info = chain.get_chain_info()
    return jsonify({
        "success": True,
        "data": info
    })


@app.route('/api/blockchain/transaction', methods=['POST'])
def add_transaction():
    """添加交易"""
    from core.chain import QNTChain
    data = request.get_json()
    chain = QNTChain()
    
    result = chain.add_transaction(
        data.get('sender'),
        data.get('recipient'),
        float(data.get('amount', 0))
    )
    
    return jsonify({"success": result})


@app.route('/api/blockchain/mine', methods=['POST'])
def mine_block():
    """挖矿"""
    from core.chain import QNTChain
    chain = QNTChain()
    chain.mine_pending_transactions()
    return jsonify({"success": True})


# ============ Exchange API ============
@app.route('/api/exchange/status', methods=['GET'])
def exchange_status():
    """获取交易所状态"""
    from exchange.engine import MatchingEngine
    eng = MatchingEngine()
    snapshot = eng.get_orderbook_snapshot()
    return jsonify({"success": True, "data": snapshot})


@app.route('/api/exchange/order', methods=['POST'])
def submit_order():
    """提交订单"""
    from exchange.engine import MatchingEngine
    data = request.get_json()
    eng = MatchingEngine()
    
    order_id = eng.submit_order(
        trader=data.get('trader'),
        side=data.get('side'),
        quantity=float(data.get('quantity', 0)),
        price=float(data.get('price', 0))
    )
    
    return jsonify({"success": order_id is not None, "order_id": order_id})


# ============ N-State API ============
@app.route('/api/nstate/train', methods=['POST'])
def train_state():
    """训练一个训练步"""
    from nstate.pool import SuperpositionPool
    import numpy as np
    data = request.get_json()
    pool = SuperpositionPool(
        num_states=int(data.get('num_states', 4)),
        weight_dim=int(data.get('weight_dim', 5))
    )
    
    for _ in range(int(data.get('steps', 10))):
        pool.train_step(np.random.randn(5), np.random.rand())
    
    collapse = pool.collapse()
    return jsonify({
        "success": True,
        "rounds": pool.training_rounds,
        "collapse": collapse
    })


@app.route('/api/nstate/collapse', methods=['POST'])
def collapse_state():
    """触发坍缩"""
    from nstate.pool import SuperpositionPool
    pool = SuperpositionPool(num_states=4, weight_dim=5)
    collapse = pool.collapse()
    return jsonify({"success": True, "data": collapse})


# ============ Agent API ============
@app.route('/api/agent/think', methods=['POST'])
def agent_think():
    """Agent思考"""
    from agents.base import ArbAgent
    data = request.get_json()
    arb = ArbAgent(name=data.get('name', 'agent'))
    decision = arb.think(data.get('market_data', {}))
    return jsonify({"success": True, "data": decision})


# ============ Health Check ============
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "timestamp": time.time()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
