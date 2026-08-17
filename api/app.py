"""
QNT API v2 - 集成数据库和持久化层
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time

app = Flask(__name__)
CORS(app)

try:
    from flask_socketio import SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False
    socketio = None


# ============ 健康检查 ============
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "timestamp": time.time(),
        "version": "v0.1.0"
    })


# ============ 区块链API ============
@app.route('/api/blockchain/status', methods=['GET'])
def blockchain_status():
    from core.chain import QNTChain
    chain = QNTChain()
    info = chain.get_chain_info()
    return jsonify({"success": True, "data": info})


@app.route('/api/blockchain/transaction', methods=['POST'])
def add_transaction():
    from core.chain import QNTChain
    data = request.get_json()
    chain = QNTChain()
    
    result = chain.add_transaction(
        data.get('sender'),
        data.get('recipient'),
        float(data.get('amount', 0))
    )
    
    return jsonify({"success": result, "tx_hash": chain.pending_transactions[-1].get('hash') if chain.pending_transactions else None})


@app.route('/api/blockchain/mine', methods=['POST'])
def mine_block():
    from core.chain import QNTChain
    chain = QNTChain()
    block_height = chain.mine_pending_transactions()
    return jsonify({"success": block_height is not None, "block_height": block_height})


@app.route('/api/blockchain/balance/<address>', methods=['GET'])
def get_balance(address):
    from core.chain import QNTChain
    chain = QNTChain()
    balance = chain.get_balance(address)
    return jsonify({"success": True, "address": address, "balance": balance})


# ============ 交易所API ============
@app.route('/api/exchange/status', methods=['GET'])
def exchange_status():
    from exchange.engine import MatchingEngine
    eng = MatchingEngine('QNT/USDT', 0.001)
    snapshot = eng.get_orderbook_snapshot()
    return jsonify({"success": True, "data": snapshot})


@app.route('/api/exchange/order', methods=['POST'])
def submit_order():
    from exchange.engine import MatchingEngine
    data = request.get_json()
    eng = MatchingEngine('QNT/USDT', 0.001)
    
    # 设置余额
    eng.set_balance(data.get('trader'), 'QNT', float(data.get('qnt_balance', 10000)))
    eng.set_balance(data.get('trader'), 'USDT', float(data.get('usdt_balance', 10000)))
    
    order_id = eng.submit_order(
        trader=data.get('trader'),
        side=data.get('side'),
        quantity=float(data.get('quantity', 0)),
        price=float(data.get('price', 0))
    )
    
    return jsonify({
        "success": order_id is not None,
        "order_id": order_id,
        "trades": len(eng.trades)
    })


@app.route('/api/exchange/trades', methods=['GET'])
def get_trades():
    from exchange.engine import MatchingEngine
    eng = MatchingEngine('QNT/USDT', 0.001)
    trades = [{
        "trade_id": t.trade_id,
        "price": t.price,
        "quantity": t.quantity,
        "timestamp": t.timestamp
    } for t in eng.trades[-10:]]
    return jsonify({"success": True, "data": trades})


# ============ N态训练API ============
@app.route('/api/nstate/train', methods=['POST'])
def train_state():
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
    from nstate.pool import SuperpositionPool
    data = request.get_json()
    pool = SuperpositionPool(
        num_states=int(data.get('num_states', 4)),
        weight_dim=int(data.get('weight_dim', 5))
    )
    
    for _ in range(int(data.get('rounds', 20))):
        for i in range(pool.num_states):
            pool.train_step(np.random.randn(pool.weight_dim), np.random.rand())
        pool.collapse()
    
    return jsonify({
        "success": True,
        "total_rounds": pool.training_rounds,
        "collapse_count": len(pool.collapses)
    })


@app.route('/api/nstate/status', methods=['GET'])
def nstate_status():
    from nstate.pool import SuperpositionPool
    pool = SuperpositionPool(num_states=4, weight_dim=5)
    return jsonify({
        "success": True,
        "data": {
            "num_states": pool.num_states,
            "weight_dim": pool.weight_dim,
            "training_rounds": pool.training_rounds,
            "collapse_count": len(pool.collapses)
        }
    })


# ============ Agent API ============
@app.route('/api/agent/think', methods=['POST'])
def agent_think():
    from agents.base import ArbAgent, TrendAgent
    data = request.get_json()
    agent_type = data.get('type', 'arb')
    
    if agent_type == 'arb':
        arb = ArbAgent(name=data.get('name', 'agent'))
        decision = arb.think(data.get('market_data', {}))
    elif agent_type == 'trend':
        trend = TrendAgent(name=data.get('name', 'trend'), lookback=10)
        decision = trend.think(data.get('market_data', {}))
    else:
        return jsonify({"success": False, "error": "Unknown agent type"})
    
    return jsonify({"success": True, "data": decision})


@app.route('/api/agent/decisions', methods=['GET'])
def get_decisions():
    return jsonify({"success": True, "data": []})


# ============ 配置API ============
@app.route('/api/config', methods=['GET'])
def get_config():
    import sys
    sys.path.insert(0, '.')
    from config.manager import config
    return jsonify({"success": True, "data": config._to_dict()})


@app.route('/api/config', methods=['PUT'])
def update_config():
    import sys
    sys.path.insert(0, '.')
    from config.manager import config
    data = request.get_json()
    for key, value in data.items():
        config.set(key, value)
    return jsonify({"success": True})


# ============ WebSocket事件 ============
if HAS_WEBSOCKET:
    @socketio.on('connect')
    def handle_connect():
        print(f"✅ Client connected: {session.id}")
        emit('connected', {'status': 'ok'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"❌ Client disconnected: {session.id}")
    
    @socketio.on('subscribe')
    def handle_subscribe(data):
        join_room(data.get('channel', 'global'))
        emit('subscribed', {'channel': data.get('channel', 'global')})


# ============ 错误处理 ============
@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"success": False, "error": "Internal error"}), 500


# ============ 启动入口 ============
if __name__ == '__main__':
    if HAS_WEBSOCKET:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
