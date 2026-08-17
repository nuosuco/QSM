"""
QNT 策略注册中心测试
"""
import pytest
from strategies.registry import StrategyRegistry, StrategyMeta, get_registry, register_strategy


class DummyStrategy:
    """测试用的假策略"""
    
    def __init__(self, param1: float = 1.0, param2: str = "default"):
        self.param1 = param1
        self.param2 = param2
    
    def think(self, data: dict) -> dict:
        return {'action': 'hold'}


def test_strategy_registry():
    """测试策略注册中心"""
    registry = StrategyRegistry()
    
    # 注册策略
    meta = StrategyMeta(
        name='test_strategy',
        module='test_module',
        class_name='DummyStrategy',
        description='A test strategy',
        params_schema={'param1': {'type': 'float', 'default': 1.0}},
        tags=['test', 'dummy']
    )
    registry.register(meta)
    
    # 列出策略
    strategies = registry.list_strategies()
    assert len(strategies) == 1
    assert strategies[0]['name'] == 'test_strategy'
    assert 'test' in strategies[0]['tags']


def test_load_strategy():
    """测试加载策略"""
    registry = StrategyRegistry()
    
    # 注册一个可直接导入的策略
    meta = StrategyMeta(
        name='simple',
        module='strategies.arbitrage',
        class_name='SpreadArbitrageStrategy',
        description='Spread arbitrage',
        params_schema={'min_spread_pct': {'type': 'float', 'default': 0.05}}
    )
    registry.register(meta)
    
    # 加载策略
    instance = registry.load('simple', min_spread_pct=0.1)
    assert instance.min_spread_pct == 0.1


def test_get_meta():
    """测试获取元数据"""
    registry = StrategyRegistry()
    
    meta = StrategyMeta(
        name='my_strategy',
        module='test',
        class_name='Test',
        description='Desc',
        params_schema={}
    )
    registry.register(meta)
    
    retrieved = registry.get_meta('my_strategy')
    assert retrieved is not None
    assert retrieved.description == 'Desc'


def test_global_registry():
    """测试全局注册中心"""
    reg = get_registry()
    assert isinstance(reg, StrategyRegistry)


def test_load_nonexistent():
    """测试加载不存在的策略"""
    registry = StrategyRegistry()
    
    with pytest.raises(ValueError):
        registry.load('nonexistent')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
