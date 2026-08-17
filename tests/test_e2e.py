"""
QNT 集成测试 - 端到端流程
"""
import pytest
import numpy as np
from core.chain import QNTChain
from exchange.engine import MatchingEngine
from nstate.pool import SuperpositionPool
from agents.base import ArbAgent


def test_full_pipeline():
    """完整流程测试"""
    # 1. 区块链
    chain = QNTChain(difficulty=2)
    chain.state_ledger['Alice'] = 10000.0
    chain.add_transaction('Alice', 'Bob', 500.0)
    chain.mine_pending_transactions()
    assert chain.is_valid()
    assert chain.get_chain_info()['height'] >= 1
    
    # 2. 交易所
    eng = MatchingEngine('QNT/USDT', 0.001)
    eng.set_balance('A', 'QNT', 500.0)
    eng.set_balance('A', 'USDT', 10000.0)
    eng.set_balance('B', 'QNT', 500.0)
    eng.set_balance('B', 'USDT', 10000.0)
    
    eng.submit_order('A', 'sell', 100, price=100.0)
    eng.submit_order('B', 'buy', 80, price=100.0)
    assert len(eng.trades) >= 1
    
    # 3. N态训练
    pool = SuperpositionPool(num_states=4, weight_dim=5)
    for _ in range(10):
        pool.train_step(np.random.randn(5), np.random.rand())
    collapse = pool.collapse()
    assert pool.training_rounds == 10
    
    # 4. Agent决策
    arb = ArbAgent(name='Test')
    dec = arb.think({'spread_pct': 0.08})
    assert dec['decision']['action'] == 'arbitrage'
    
    print("✅ 完整流程测试通过")


def test_blockchain_to_exchange():
    """区块链到交易所的数据流转"""
    chain = QNTChain()
    chain.state_ledger['Alice'] = 10000.0
    chain.add_transaction('Alice', 'Bob', 1000.0)
    chain.mine_pending_transactions()
    
    # Alice应该有余额
    assert chain.get_balance('Alice') < 10000.0
    assert chain.get_balance('Bob') == 1000.0


def test_nstate_evolution():
    """N态演化测试"""
    pool = SuperpositionPool(num_states=4, weight_dim=5)
    
    # 模拟10轮训练
    for round_num in range(10):
        for state_id in range(4):
            # 每个态独立训练
            weights = np.random.randn(5)
            error = np.random.rand()
            pool.train_step(weights, error)
        
        # 每5轮坍缩一次
        if (round_num + 1) % 5 == 0:
            collapse = pool.collapse()
            assert 'status' in collapse or 'merged_weights' in collapse
    
    assert pool.training_rounds == 40


def test_agent_decision_making():
    """Agent决策逻辑测试"""
    # 套利Agent
    arb = ArbAgent(name='Arb')
    dec_high = arb.think({'spread_pct': 0.1})
    dec_low = arb.think({'spread_pct': 0.01})
    
    assert dec_high['decision']['action'] == 'arbitrage'
    assert dec_low['decision']['action'] == 'hold'
    
    # 趋势Agent
    trend = TrendAgent(name='Trend', lookback=5)
    for i in range(10):
        trend.think({'price': 100 + i * 0.5})  # 上升趋势
    dec_trend = trend.think({'price': 105})
    assert dec_trend['decision']['action'] == 'long'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
