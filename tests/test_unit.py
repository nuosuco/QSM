"""
QNT 单元测试
"""
import pytest
import numpy as np
from core.chain import QNTChain, Block
from core.contract import QNTToken, QNTGovernance, NStateContract
from exchange.orderbook import OrderBook, Order, OrderSide
from exchange.engine import MatchingEngine
from nstate.pool import SuperpositionPool
from agents.base import ArbAgent, MarketMakerAgent, TrendAgent
from strategies.arbitrage import SpreadArbitrageStrategy


# ============ Blockchain Tests ============
class TestBlockchain:
    def test_genesis_block(self):
        import time
        block = Block(0, time.time(), [], "0" * 64)
        assert block.index == 0
        assert block.timestamp > 0
    
    def test_chain_valid(self):
        chain = QNTChain(difficulty=2)
        chain.state_ledger['Alice'] = 10000.0
        chain.add_transaction('Alice', 'Bob', 500.0)
        chain.mine_pending_transactions()
        assert chain.is_valid()
    
    def test_balance_tracking(self):
        chain = QNTChain()
        chain.state_ledger['Alice'] = 10000.0
        assert chain.get_balance('Alice') == 10000.0


# ============ Token Contract Tests ============
class TestTokenContract:
    def test_token_creation(self):
        token = QNTToken(total_supply=1_000_000.0)
        assert token.balance_of('system') == 1_000_000.0
    
    def test_transfer(self):
        token = QNTToken(total_supply=1_000_000.0)
        result = token.call('system', 'transfer', 'Alice', 1000.0)
        assert result['success']
        assert token.balance_of('Alice') == 1000.0
    
    def test_insufficient_balance(self):
        token = QNTToken(total_supply=100.0)
        result = token.call('system', 'transfer', 'Alice', 200.0)
        assert not result['success']


# ============ Exchange Tests ============
class TestExchange:
    def test_order_submission(self):
        eng = MatchingEngine('QNT/USDT', 0.001)
        eng.set_balance('A', 'QNT', 500.0)
        eng.set_balance('A', 'USDT', 10000.0)
        eng.set_balance('B', 'QNT', 500.0)
        eng.set_balance('B', 'USDT', 10000.0)
        
        sell_id = eng.submit_order('A', 'sell', 100, price=100.0)
        assert sell_id is not None
    
    def test_matching(self):
        eng = MatchingEngine('QNT/USDT', 0.001)
        eng.set_balance('A', 'QNT', 500.0)
        eng.set_balance('A', 'USDT', 10000.0)
        eng.set_balance('B', 'QNT', 500.0)
        eng.set_balance('B', 'USDT', 10000.0)
        
        eng.submit_order('A', 'sell', 100, price=100.0)
        eng.submit_order('B', 'buy', 80, price=100.0)
        
        assert len(eng.trades) >= 1
        assert eng.trades[0].quantity == 80.0


# ============ N-State Tests ============
class TestNState:
    def test_pool_creation(self):
        pool = SuperpositionPool(num_states=4, weight_dim=5)
        assert pool.num_states == 4
    
    def test_training_step(self):
        pool = SuperpositionPool(num_states=4, weight_dim=5)
        pool.train_step(np.random.randn(5), np.random.rand())
        assert pool.training_rounds == 1
    
    def test_collapse(self):
        pool = SuperpositionPool(num_states=4, weight_dim=5)
        for i in range(10):
            pool.train_step(np.random.randn(5), np.random.rand())
        collapse = pool.collapse()
        assert 'merged_weights' in collapse
        assert pool.num_states == 4


# ============ Agent Tests ============
class TestAgents:
    def test_arb_agent(self):
        arb = ArbAgent(name='Test')
        dec = arb.think({'spread_pct': 0.08})
        assert dec['decision']['action'] == 'arbitrage'
    
    def test_trend_agent(self):
        trend = TrendAgent(name='TrendBot', lookback=3)
        for p in [10, 11, 12]:
            trend.think({'price': float(p)})
        dec = trend.think({'price': 12.0})
        assert dec['decision']['action'] in ['buy', 'sell', 'hold']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
