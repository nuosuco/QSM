"""
QNT 端到端集成测试
"""
import pytest
from core.chain import QNTChain
from exchange.engine import MatchingEngine
from nstate.pool import SuperpositionPool
from agents.base import ArbAgent, MarketMakerAgent, TrendAgent
from core.contract import QNTToken
import numpy as np


class TestE2EIntegration:
    """端到端集成测试"""
    
    def test_blockchain_to_exchange(self):
        """区块链到交易所完整流程"""
        # 1. 创建区块链和代币
        chain = QNTChain(difficulty=2)
        token = QNTToken(total_supply=1000000.0)
        
        # 2. 初始化用户余额
        token.call('system', 'transfer', 'Alice', 10000.0)
        token.call('system', 'transfer', 'Bob', 10000.0)
        
        # 3. 在交易所设置余额
        eng = MatchingEngine('QNT/USDT', fee_rate=0.001)
        eng.set_balance('Alice', 'QNT', token.balance_of('Alice'))
        eng.set_balance('Alice', 'USDT', 100000.0)
        eng.set_balance('Bob', 'QNT', token.balance_of('Bob'))
        eng.set_balance('Bob', 'USDT', 100000.0)
        
        # 4. 提交交易订单
        eng.submit_order('Alice', 'sell', 100, price=100.0)
        eng.submit_order('Bob', 'buy', 80, price=100.0)
        
        # 5. 验证成交
        assert len(eng.trades) >= 1
        
        # 6. 验证余额更新
        alice_qnt_after = eng.get_balance('Alice', 'QNT')
        bob_qnt_after = eng.get_balance('Bob', 'QNT')
        
        assert alice_qnt_after < 10000.0  # Alice卖出了QNT
        assert bob_qnt_after > 0.0  # Bob收到了QNT
    
    def test_nstate_evolution(self):
        """N态自进化过程"""
        pool = SuperpositionPool(num_states=4, weight_dim=5)
        
        # 模拟多轮训练
        for round in range(10):
            for i in range(5):
                pool.train_step(np.random.randn(5), np.random.rand())
            
            # 每5轮坍缩一次
            if (round + 1) % 5 == 0:
                collapse = pool.collapse()
                assert 'status' in collapse or 'merged_weights' in collapse
        
        assert pool.training_rounds == 50
        assert len(pool.collapses) == 2
    
    def test_agent_decision_making(self):
        """Agent决策全流程"""
        # 创建不同类型的Agent
        agents = {
            'arb': ArbAgent(name='ArbBot'),
            'mm': MarketMakerAgent(name='MMBot'),
            'trend': TrendAgent(name='TrendBot', lookback=5)
        }
        
        observations = [
            {'spread_pct': 0.08, 'mid_price': 100.0},
            {'price': 100.0},
            {'best_bid': 99.0, 'best_ask': 101.0}
        ]
        
        decisions = []
        for obs in observations:
            for name, agent in agents.items():
                dec = agent.think(obs)
                decisions.append({
                    'agent': name,
                    'decision': dec['decision']
                })
        
        assert len(decisions) == 9  # 3 observations × 3 agents
        
        # 验证有有效的决策
        valid_decisions = [d for d in decisions if d['decision'].get('action') in ['arbitrage', 'long', 'short', 'hold', 'post_orders']]
        assert len(valid_decisions) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
