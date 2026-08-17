"""
QNT Agent策略测试
"""
import pytest
from agents.strategies import (
    GridTradingAgent,
    MomentumAgent,
    MeanReversionAgent,
    VolumeProfileAgent,
    create_agent
)


class TestGridTradingAgent:
    """网格交易Agent测试"""
    
    def test_create(self):
        """创建测试"""
        agent = GridTradingAgent(name='TestGrid')
        assert agent.name == 'TestGrid'
        assert agent.grid_levels == 5
    
    def test_think(self):
        """决策测试"""
        agent = GridTradingAgent()
        observation = {'mid_price': 100.0}
        result = agent.think(observation)
        
        assert result['decision'] == 'grid_orders'
        assert len(result['orders']) > 0
        assert result['confidence'] > 0
    
    def test_grid_spacing(self):
        """网格间距测试"""
        agent = GridTradingAgent(grid_spacing=0.02)
        obs = {'mid_price': 100.0}
        result = agent.think(obs)
        
        prices = [o['price'] for o in result['orders']]
        assert max(prices) - min(prices) > 0


class TestMomentumAgent:
    """动量Agent测试"""
    
    def test_insufficient_data(self):
        """数据不足测试"""
        agent = MomentumAgent(lookback=20)
        result = agent.think({'price': 100.0})
        assert result['decision'] == 'hold'
    
    def test_strong_uptrend(self):
        """强上涨测试"""
        agent = MomentumAgent(lookback=5)
        
        # 模拟上涨
        for i in range(10, 20):
            agent.think({'price': 100 + i})
        
        result = agent.think({'price': 120})
        assert result['decision'] == 'long'
        assert result['momentum'] > 0
    
    def test_strong_downtrend(self):
        """强下跌测试"""
        agent = MomentumAgent(lookback=5)
        
        # 模拟下跌
        for i in range(20, 10, -1):
            agent.think({'price': 100 + i})
        
        result = agent.think({'price': 80})
        assert result['decision'] == 'short'


class TestMeanReversionAgent:
    """均值回归Agent测试"""
    
    def test_basic_operation(self):
        """基本操作测试"""
        agent = MeanReversionAgent(lookback=10)
        
        # 填充数据
        for _ in range(15):
            agent.think({'price': 100.0})
        
        result = agent.think({'price': 105.0})
        assert 'z_score' in result
        assert 'confidence' in result


class TestVolumeProfileAgent:
    """成交量分析Agent测试"""
    
    def test_basic_operation(self):
        """基本操作测试"""
        agent = VolumeProfileAgent(lookback=10)
        
        # 填充数据
        for i in range(15):
            agent.think({'price': 100.0, 'volume': 100.0})
        
        result = agent.think({'price': 102.0, 'volume': 200.0})
        assert 'vwap' in result
        assert 'vol_ratio' in result


class TestCreateAgent:
    """Agent工厂函数测试"""
    
    def test_create_grid(self):
        agent = create_agent('grid')
        assert isinstance(agent, GridTradingAgent)
    
    def test_create_momentum(self):
        agent = create_agent('momentum')
        assert isinstance(agent, MomentumAgent)
    
    def test_create_mean_reversion(self):
        agent = create_agent('mean_reversion')
        assert isinstance(agent, MeanReversionAgent)
    
    def test_create_volume_profile(self):
        agent = create_agent('volume_profile')
        assert isinstance(agent, VolumeProfileAgent)
    
    def test_invalid_type(self):
        with pytest.raises(ValueError):
            create_agent('invalid_type')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
