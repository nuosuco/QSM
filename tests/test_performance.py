"""
QNT 性能基准测试
"""
import pytest
import time
import numpy as np
from core.chain import QNTChain
from exchange.engine import MatchingEngine
from nstate.pool import SuperpositionPool
from agents.base import ArbAgent


class TestBlockchainPerformance:
    """区块链性能测试"""
    
    def test_transaction_throughput(self):
        """交易吞吐量测试"""
        chain = QNTChain(difficulty=2)
        chain.state_ledger['Alice'] = 1000000.0
        
        start = time.time()
        for i in range(100):
            chain.add_transaction('Alice', f'User{i}', 1.0)
        elapsed = time.time() - start
        
        tps = 100 / elapsed
        print(f"\n📊 交易吞吐: {tps:.0f} tx/s")
        assert tps > 10  # 至少10 TPS
    
    def test_mining_speed(self):
        """挖矿速度测试"""
        chain = QNTChain(difficulty=2)
        chain.state_ledger['Alice'] = 10000.0
        
        for _ in range(10):
            chain.add_transaction('Alice', 'Bob', 100.0)
        
        start = time.time()
        chain.mine_pending_transactions()
        elapsed = time.time() - start
        
        print(f"\n⛏️  挖矿时间: {elapsed*1000:.1f}ms")
        assert elapsed < 5.0  # 5秒内完成


class TestExchangePerformance:
    """交易所性能测试"""
    
    def test_order_throughput(self):
        """订单吞吐量测试"""
        eng = MatchingEngine('QNT/USDT', 0.001)
        
        # 设置多个账户
        for i in range(10):
            eng.set_balance(f'User{i}', 'QNT', 10000.0)
            eng.set_balance(f'User{i}', 'USDT', 10000.0)
        
        start = time.time()
        for i in range(50):
            side = 'buy' if i % 2 == 0 else 'sell'
            eng.submit_order(f'User{i%10}', side, 10, price=100.0)
        elapsed = time.time() - start
        
        tps = 50 / elapsed
        print(f"\n📈 订单吞吐: {tps:.0f} order/s")
        assert tps > 100
    
    def test_matching_speed(self):
        """撮合速度测试"""
        eng = MatchingEngine('QNT/USDT', 0.001)
        eng.set_balance('A', 'QNT', 10000.0); eng.set_balance('A', 'USDT', 10000.0)
        eng.set_balance('B', 'QNT', 10000.0); eng.set_balance('B', 'USDT', 10000.0)
        
        start = time.time()
        for i in range(50):
            eng.submit_order('A', 'sell', 10, price=100.0)
            eng.submit_order('B', 'buy', 10, price=100.0)
        elapsed = time.time() - start
        
        print(f"\n⚡ 撮合时间: {elapsed*1000:.1f}ms for {len(eng.trades)} trades")
        assert len(eng.trades) >= 40  # 至少40笔成交


class TestNStatePerformance:
    """N态性能测试"""
    
    def test_training_speed(self):
        """训练速度测试"""
        pool = SuperpositionPool(num_states=4, weight_dim=100)
        
        start = time.time()
        for _ in range(50):
            for _ in range(4):
                pool.train_step(np.random.randn(100), np.random.rand())
        elapsed = time.time() - start
        
        print(f"\n🧠 训练速度: {50/elapsed:.0f} rounds/s")
    
    def test_collapse_speed(self):
        """坍缩速度测试"""
        pool = SuperpositionPool(num_states=10, weight_dim=1000)
        
        for _ in range(20):
            for i in range(10):
                pool.train_step(np.random.randn(1000), np.random.rand())
        
        start = time.time()
        pool.collapse()
        elapsed = time.time() - start
        
        print(f"\n💥 坍缩时间: {elapsed*1000:.1f}ms")
        assert elapsed < 1.0  # 1秒内完成


class TestAgentPerformance:
    """Agent性能测试"""
    
    def test_decision_speed(self):
        """决策速度测试"""
        arb = ArbAgent(name='Test')
        
        start = time.time()
        for _ in range(1000):
            arb.think({'spread_pct': 0.05 + np.random.rand() * 0.1})
        elapsed = time.time() - start
        
        dec_per_sec = 1000 / elapsed
        print(f"\n🤖 决策速度: {dec_per_sec:.0f} decisions/s")
        assert dec_per_sec > 1000


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
