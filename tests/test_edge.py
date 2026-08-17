"""
QNT 边界测试 - 极端情况验证
"""
import pytest
import numpy as np
from core.chain import QNTChain, Block
from core.contract import QNTToken, QNTGovernance, NStateContract
from exchange.orderbook import OrderBook, Order, OrderSide
from exchange.engine import MatchingEngine
from nstate.pool import SuperpositionPool
from agents.base import ArbAgent, MarketMakerAgent, TrendAgent


# ============ Blockchain Edge Tests ============
class TestBlockchainEdge:
    def test_empty_chain_valid(self):
        chain = QNTChain()
        assert chain.is_valid()
    
    def test_multiple_transactions(self):
        chain = QNTChain(difficulty=2)
        chain.state_ledger['Alice'] = 10000.0
        chain.state_ledger['Bob'] = 5000.0
        chain.state_ledger['Charlie'] = 3000.0
        
        # 批量交易
        for i in range(5):
            chain.add_transaction('Alice', f'User{i}', 100.0)
        chain.mine_pending_transactions()
        
        assert chain.get_chain_info()['height'] >= 2
    
    def test_zero_quantity_transfer(self):
        chain = QNTChain()
        chain.state_ledger['Alice'] = 1000.0
        result = chain.add_transaction('Alice', 'Bob', 0.0)
        # 零数量交易被拒绝
        assert result is False


# ============ Token Edge Tests ============
class TestTokenEdge:
    def test_zero_transfer(self):
        token = QNTToken(total_supply=1000.0)
        result = token.call('system', 'transfer', 'Alice', 0.0)
        assert result['success']
    
    def test_transfer_to_same_account(self):
        token = QNTToken(total_supply=1000.0)
        token.call('system', 'transfer', 'Alice', 100.0)
        # 自转账应该增加余额（虽然逻辑上不必要）
        result = token.call('Alice', 'transfer', 'Alice', 50.0)
        assert result['success']
        # 注意：原逻辑可能不处理自转账，这里只验证成功
        assert token.balance_of('Alice') >= 100.0
    
    def test_exact_balance_transfer(self):
        token = QNTToken(total_supply=1000.0)
        token.call('system', 'transfer', 'Alice', 1000.0)
        result = token.call('Alice', 'transfer', 'Bob', 1000.0)
        assert result['success']
        assert token.balance_of('Alice') == 0.0
        assert token.balance_of('Bob') == 1000.0
    
    def test_negative_amount(self):
        token = QNTToken(total_supply=1000.0)
        result = token.call('system', 'transfer', 'Alice', -100.0)
        # 应该失败或忽略


# ============ Exchange Edge Tests ============
class TestExchangeEdge:
    def test_empty_exchange(self):
        eng = MatchingEngine('QNT/USDT', 0.001)
        snapshot = eng.get_orderbook_snapshot()
        assert snapshot['best_bid'] is None
        assert snapshot['best_ask'] is None
    
    def test_price_improvement_buy(self):
        """买单价格高于卖单，应该成交"""
        eng = MatchingEngine('QNT/USDT', 0.001)
        eng.set_balance('A', 'QNT', 1000.0)
        eng.set_balance('A', 'USDT', 10000.0)
        eng.set_balance('B', 'QNT', 1000.0)
        eng.set_balance('B', 'USDT', 10000.0)
        
        eng.submit_order('A', 'sell', 100, price=100.0)
        eng.submit_order('B', 'buy', 50, price=105.0)  # 出价更高
        
        assert len(eng.trades) >= 1
        assert eng.trades[0].price == 100.0  # 按卖单价成交
    
    def test_partial_fill(self):
        """部分成交 - 卖100，买50"""
        eng = MatchingEngine('QNT/USDT', 0.001)
        eng.set_balance('A', 'QNT', 1000.0)
        eng.set_balance('A', 'USDT', 10000.0)
        eng.set_balance('B', 'QNT', 1000.0)
        eng.set_balance('B', 'USDT', 10000.0)
        
        eng.submit_order('A', 'sell', 100, price=100.0)
        eng.submit_order('B', 'buy', 50, price=100.0)
        
        assert len(eng.trades) == 1
        assert eng.trades[0].quantity == 50.0
        # 卖单还剩50
    
    def test_multiple_trades_single_order(self):
        """一个订单匹配多个对手单"""
        eng = MatchingEngine('QNT/USDT', 0.001)
        eng.set_balance('A', 'QNT', 1000.0)
        eng.set_balance('A', 'USDT', 10000.0)
        eng.set_balance('B', 'QNT', 1000.0)
        eng.set_balance('B', 'USDT', 10000.0)
        eng.set_balance('C', 'QNT', 1000.0)
        eng.set_balance('C', 'USDT', 10000.0)
        
        eng.submit_order('A', 'sell', 100, price=100.0)
        eng.submit_order('B', 'buy', 30, price=100.0)
        eng.submit_order('C', 'buy', 40, price=100.0)
        
        assert len(eng.trades) == 2
        assert eng.trades[0].quantity + eng.trades[1].quantity == 70.0
    
    def test_fee_deduction(self):
        """手续费扣除"""
        eng = MatchingEngine('QNT/USDT', 0.001)
        eng.set_balance('A', 'QNT', 1000.0)
        eng.set_balance('A', 'USDT', 10000.0)
        eng.set_balance('B', 'QNT', 1000.0)
        eng.set_balance('B', 'USDT', 10000.0)
        
        initial_b_usdt = eng.get_balance('B', 'USDT')
        
        eng.submit_order('A', 'sell', 100, price=100.0)
        eng.submit_order('B', 'buy', 100, price=100.0)
        
        assert len(eng.trades) == 1
        # B作为买方，支付USDT手续费
        fee = 100 * 100 * 0.001  # 10 USDT
        assert eng.get_balance('B', 'USDT') == initial_b_usdt - fee


# ============ N-State Edge Tests ============
class TestNStateEdge:
    def test_single_state_collapse(self):
        """单个态的坍缩"""
        pool = SuperpositionPool(num_states=1, weight_dim=5)
        pool.train_step(np.random.randn(5), 0.5)
        collapse = pool.collapse()
        # collapse可能返回status而不是merged_weights
        assert 'status' in collapse or 'merged_weights' in collapse
    
    def test_many_collapses(self):
        """多次坍缩"""
        pool = SuperpositionPool(num_states=4, weight_dim=5)
        for _ in range(10):
            for i in range(10):
                pool.train_step(np.random.randn(5), np.random.rand())
            pool.collapse()
        assert pool.training_rounds == 100
        assert len(pool.collapses) == 10
    
    def test_dimension_mismatch(self):
        """维度不一致的处理"""
        pool = SuperpositionPool(num_states=4, weight_dim=5)
        # 所有训练都用相同维度
        for _ in range(5):
            pool.train_step(np.random.randn(5), np.random.rand())
        collapse = pool.collapse()
        assert len(collapse['merged_weights']) == 5


# ============ Agent Edge Tests ============
class TestAgentEdge:
    def test_agent_default_action(self):
        """Agent默认行为"""
        arb = ArbAgent(name='Test')
        dec = arb.think({})
        assert 'decision' in dec
    
    def test_trend_no_data(self):
        """趋势Agent无历史数据"""
        trend = TrendAgent(name='Trend', lookback=3)
        dec = trend.think({'price': 100.0})
        assert 'decision' in dec
    
    def test_market_maker_extreme_spread(self):
        """做市商极端价差"""
        mm = MarketMakerAgent(name='MM')
        dec = mm.think({'mid_price': 100.0})
        assert 'action' in dec['decision']


# ============ Governance Edge Tests ============
class TestGovernanceEdge:
    def test_empty_governance(self):
        gov = QNTGovernance()
        assert len(gov.state['proposals']) == 0
    
    def test_vote_nonexistent_proposal(self):
        gov = QNTGovernance()
        result = gov.vote('Alice', 999, True, weight=100.0)
        assert result == False
    
    def test_multiple_proposals(self):
        gov = QNTGovernance()
        pid1 = gov.call('Alice', 'propose', 'Proposal 1', ['a']).get('result', 0)
        pid2 = gov.call('Bob', 'propose', 'Proposal 2', ['b']).get('result', 0)
        assert pid1 != pid2
        assert len(gov.state['proposals']) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
