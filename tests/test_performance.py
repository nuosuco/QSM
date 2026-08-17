"""
QNT 性能基准测试
"""
import pytest
import time
import numpy as np
from core.chain import QNTChain
from exchange.engine import MatchingEngine
from nstate.pool import SuperpositionPool
from agents.base import ArbAgent, MarketMakerAgent, TrendAgent
from agents.strategies import GridTradingAgent, MomentumAgent


class TestBlockchainPerformance:
    """区块链性能测试"""
    
    def test_transaction_throughput(self):
        """交易吞吐量"""
        chain = QNTChain(difficulty=2)
        chain.state_ledger['Alice'] = 1000000.0
        
        start = time.time()
        for i in range(100):
            chain.add_transaction('Alice', f'User{i}', 1.0)
        elapsed = time.time() - start
        
        tps = 100 / elapsed if elapsed > 0 else float('inf')
        print(f"\n💰 交易添加: {elapsed:.4f}s ({tps:.0f} TPS)")
        assert tps > 0
    
    def test_mining_speed(self):
        """挖矿速度"""
        chain = QNTChain(difficulty=2)
        chain.state_ledger['Alice'] = 1000000.0
        
        for i in range(10):
            chain.add_transaction('Alice', f'Bob{i}', 100.0)
        
        start = time.time()
        chain.mine_pending_transactions()
        elapsed = time.time() - start
        
        print(f"\n⛏️  挖矿时间: {elapsed:.4f}s")
        assert elapsed < 1.0
    
    def test_chain_validation(self):
        """链验证性能"""
        chain = QNTChain(difficulty=2)
        chain.state_ledger['Alice'] = 10000.0
        
        for i in range(20):
            chain.add_transaction('Alice', f'Bob{i}', 100.0)
        chain.mine_pending_transactions()
        
        start = time.time()
        valid = chain.is_valid()
        elapsed = time.time() - start
        
        print(f"\n✅ 链验证: {elapsed:.4f}s (valid={valid})")
        assert valid


class TestExchangePerformance:
    """交易所性能测试"""
    
    def test_order_submission(self):
        """订单提交速度"""
        eng = MatchingEngine('QNT/USDT', 0.001)
        eng.set_balance('A', 'QNT', 100000.0)
        eng.set_balance('A', 'USDT', 1000000.0)
        eng.set_balance('B', 'QNT', 100000.0)
        eng.set_balance('B', 'USDT', 1000000.0)
        
        start = time.time()
        for i in range(50):
            eng.submit_order('A', 'sell', 10.0, price=100.0 + i * 0.1)
            eng.submit_order('B', 'buy', 10.0, price=100.0 - i * 0.1)
        elapsed = time.time() - start
        
        tps = 100 / elapsed if elapsed > 0 else float('inf')
        print(f"\n📈 订单提交: {elapsed:.4f}s ({tps:.0f} TPS)")
        assert tps > 0
    
    def test_matching_speed(self):
        """撮合速度"""
        eng = MatchingEngine('QNT/USDT', 0.001)
        eng.set_balance('A', 'QNT', 100000.0)
        eng.set_balance('A', 'USDT', 1000000.0)
        eng.set_balance('B', 'QNT', 100000.0)
        eng.set_balance('B', 'USDT', 1000000.0)
        
        for i in range(20):
            eng.submit_order('A', 'sell', 10.0, price=100.0)
            eng.submit_order('B', 'buy', 10.0, price=100.0)
        
        assert len(eng.trades) >= 20
        print(f"\n✅ 撮合完成: {len(eng.trades)} trades")


class TestNStatePerformance:
    """N态训练性能测试"""
    
    def test_training_speed(self):
        """训练速度"""
        pool = SuperpositionPool(num_states=4, weight_dim=10)
        
        start = time.time()
        for i in range(50):
            pool.train_step(np.random.randn(10), np.random.rand())
        elapsed = time.time() - start
        
        steps_per_sec = 50 / elapsed if elapsed > 0 else float('inf')
        print(f"\n🧠 训练速度: {steps_per_sec:.0f} steps/sec")
        assert steps_per_sec > 0
    
    def test_collapse_speed(self):
        """坍缩速度"""
        pool = SuperpositionPool(num_states=4, weight_dim=10)
        
        for i in range(20):
            pool.train_step(np.random.randn(10), np.random.rand())
        
        start = time.time()
        collapse = pool.collapse()
        elapsed = time.time() - start
        
        print(f"\n🔭 坍缩时间: {elapsed:.4f}s")
        assert elapsed < 0.1


class TestAgentPerformance:
    """Agent性能测试"""
    
    def test_decision_speed(self):
        """决策速度"""
        agents = [
            ArbAgent(name='Arb'),
            MarketMakerAgent(name='MM'),
            TrendAgent(name='Trend'),
            GridTradingAgent(name='Grid'),
            MomentumAgent(name='Mom')
        ]
        
        observations = [
            {'spread_pct': 0.08},
            {'mid_price': 100.0},
            {'price': 100.0}
        ]
        
        start = time.time()
        for obs in observations:
            for agent in agents:
                agent.think(obs)
        elapsed = time.time() - start
        
        decisions_per_sec = len(observations) * len(agents) / elapsed if elapsed > 0 else float('inf')
        print(f"\n🤖 决策速度: {decisions_per_sec:.0f} decisions/sec")
        assert decisions_per_sec > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
