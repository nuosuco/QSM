"""
QNT 回测引擎测试
"""
import pytest
from strategies.backtest import BacktestEngine, MockStrategy, generate_mock_data


def test_backtest_engine():
    """回测引擎基本测试"""
    engine = BacktestEngine(initial_capital=100000.0, fee_rate=0.001)
    strategy = MockStrategy()
    data = generate_mock_data(days=7)
    
    result = engine.run(strategy, data)
    
    assert result.total_return is not None
    assert 0 <= result.win_rate <= 1
    assert len(engine.get_equity_curve()) > 0


def test_equity_curve():
    """权益曲线测试"""
    engine = BacktestEngine(initial_capital=100000.0)
    strategy = MockStrategy()
    data = generate_mock_data(days=1)
    
    engine.run(strategy, data)
    curve = engine.get_equity_curve()
    
    assert len(curve) > 0
    assert curve[0] == 100000.0  # 初始资金


def test_trades_recorded():
    """交易记录测试"""
    engine = BacktestEngine(initial_capital=100000.0)
    strategy = MockStrategy()
    data = generate_mock_data(days=3)
    
    engine.run(strategy, data)
    trades = engine.get_trades()
    
    assert isinstance(trades, list)
    for trade in trades:
        assert 'action' in trade
        assert 'price' in trade
        assert 'quantity' in trade


def test_mock_strategy():
    """模拟策略测试"""
    strategy = MockStrategy()
    
    # 测试hold决策
    decision = strategy.think({'price': 100.0}, {'capital': 100000.0})
    assert decision['action'] == 'hold'  # 第一条数据


def test_generate_data():
    """测试数据生成"""
    data = generate_mock_data(days=1, initial_price=50.0)
    
    assert len(data) == 24  # 24小时
    assert data[0]['price'] == pytest.approx(50.0, abs=1.0)  # 允许微小波动
    assert all(d['price'] > 0 for d in data)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
