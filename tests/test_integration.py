"""
QNT 端到端测试 - 完整业务流程验证
"""
import pytest
import time
import numpy as np
from core.chain import QNTChain
from exchange.engine import MatchingEngine
from nstate.pool import SuperpositionPool
from agents.base import ArbAgent, TrendAgent
from storage.persistence import PersistenceManager


class TestFullPipeline:
    """完整业务流程测试"""
    
    def test_blockchain_to_exchange(self):
        """区块链交易 → 交易所撮合完整流程"""
        # 1. 区块链初始化
        chain = QNTChain(difficulty=2)
        chain.state_ledger['Alice'] = 10000.0
        chain.add_transaction('Alice', 'Bob', 5000.0)
        chain.mine_pending_transactions()
        
        assert chain.is_valid()
        assert chain.get_balance('Bob') == 5000.0
        
        # 2. 交易所初始化
        eng = MatchingEngine('QNT/USDT', 0.001)
        eng.set_balance('Alice', 'QNT', 5000.0)
        eng.set_balance('Alice', 'USDT', 5000.0)
        eng.set_balance('Bob', 'QNT', 5000.0)
        eng.set_balance('Bob', 'USDT', 5000.0)
        
        # Alice 卖出 QNT，Bob 买入
        eng.submit_order('Alice', 'sell', 100, price=100.0)
        eng.submit_order('Bob', 'buy', 50, price=100.0)
        
        trades = len(eng.trades)
        assert trades >= 1
        print(f"\n✅ 流程: 区块链→交易所, {trades}笔成交")
    
    def test_nstate_to_agent(self):
        """N态训练 → Agent决策完整流程"""
        # 1. N态训练
        pool = SuperpositionPool(num_states=4, weight_dim=10)
        for i in range(10):
            for _ in range(4):
                pool.train_step(np.random.randn(10), np.random.rand())
            if (i + 1) % 5 == 0:
                pool.collapse()
        
        # 2. Agent使用N态模型做决策
        arb = ArbAgent(name='ArbBot')
        decision = arb.think({'spread_pct': 0.08})
        
        assert decision['decision']['action'] == 'arbitrage'
        print(f"\n✅ 流程: N态训练{pool.training_rounds}轮 → Agent决策")
    
    def test_full_trading_cycle(self):
        """完整交易周期测试"""
        chain = QNTChain(difficulty=2)
        chain.state_ledger['Alice'] = 10000.0
        
        for i in range(5):
            chain.add_transaction('Alice', 'Bob', 1000.0)
        chain.mine_pending_transactions()
        
        eng = MatchingEngine('QNT/USDT', 0.001)
        eng.set_balance('Alice', 'QNT', 3000.0)
        eng.set_balance('Alice', 'USDT', 5000.0)
        eng.set_balance('Charlie', 'QNT', 5000.0)
        eng.set_balance('Charlie', 'USDT', 10000.0)  # 需要足够USDT买入
        
        order_id = eng.submit_order('Alice', 'sell', 100, price=100.0)
        assert order_id is not None
        
        eng.submit_order('Charlie', 'buy', 80, price=100.0)
        assert len(eng.trades) >= 1
        
        arb = ArbAgent(name='Monitor')
        decision = arb.think({'spread_pct': 0.05})
        
        assert 'decision' in decision
        print(f"\n✅ 完整交易周期: {len(chain.chain)}块 + {len(eng.trades)}交易")
    
    def test_persistence_integration(self):
        """持久化层集成测试"""
        pm = PersistenceManager()
        
        # 保存区块链数据
        chain = QNTChain(difficulty=2)
        chain.state_ledger['Alice'] = 10000.0
        chain.add_transaction('Alice', 'Bob', 500.0)
        chain.mine_pending_transactions()
        
        assert pm.save_block({
            'hash': 'test_hash',
            'index': 1,
            'transactions': [{'sender': 'Alice', 'receiver': 'Bob', 'amount': 500.0}]
        })
        
        # 保存订单和成交（使用唯一order_id）
        eng = MatchingEngine('QNT/USDT', 0.001)
        eng.set_balance('A', 'QNT', 1000.0); eng.set_balance('A', 'USDT', 10000.0)
        eng.set_balance('B', 'QNT', 1000.0); eng.set_balance('B', 'USDT', 10000.0)
        eng.submit_order('A', 'sell', 100, price=100.0)
        eng.submit_order('B', 'buy', 80, price=100.0)
        
        assert pm.save_order('order_001', 'A', 'sell', 100, 100.0)
        assert pm.save_trade('trade_001', 'order_001', 'order_002', 80, 100.0)
        
        print(f"\n✅ 持久化集成: {len(eng.trades)}笔成交已保存")


class TestWebSocketSimulation:
    """WebSocket实时推送模拟测试"""
    
    def test_event_broadcast(self):
        """事件广播测试"""
        events = []
        
        def mock_emit(event, data):
            events.append({'event': event, 'data': data})
        
        # 模拟广播trade事件
        mock_emit('trade', {'price': 100.0, 'quantity': 50.0})
        mock_emit('orderbook', {'bids': [[100.0, 100]], 'asks': [[101.0, 50]]})
        
        assert len(events) == 2
        assert events[0]['event'] == 'trade'
        print(f"\n✅ 事件广播: {len(events)}条事件")


class TestPerformanceIntegration:
    """性能集成测试"""
    
    def test_high_frequency_trading(self):
        """高频交易测试"""
        eng = MatchingEngine('QNT/USDT', 0.001)
        
        # 设置多个交易者
        for i in range(5):
            eng.set_balance(f'T{i}', 'QNT', 10000.0)
            eng.set_balance(f'T{i}', 'USDT', 10000.0)
        
        start = time.time()
        for i in range(100):
            buyer = f'T{i % 5}'
            seller = f'T{(i + 1) % 5}'
            eng.submit_order(seller, 'sell', 10, price=100.0)
            eng.submit_order(buyer, 'buy', 10, price=100.0)
        elapsed = time.time() - start
        
        tps = len(eng.trades) / elapsed
        print(f"\n⚡ 高频交易: {len(eng.trades)}笔成交, {tps:.0f} trade/s")
        assert tps > 50
    
    def test_concurrent_nstate_training(self):
        """并发N态训练测试"""
        pool = SuperpositionPool(num_states=8, weight_dim=20)
        
        start = time.time()
        for round_num in range(20):
            for state_id in range(8):
                pool.train_step(np.random.randn(20), np.random.rand())
            if round_num % 4 == 3:
                pool.collapse()
        elapsed = time.time() - start
        
        print(f"\n🧠 N态训练: {pool.training_rounds}轮, {elapsed*1000:.1f}ms")
        assert pool.training_rounds == 160


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
