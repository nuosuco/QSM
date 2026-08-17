"""
QNT 风险管理测试
"""
import pytest
from strategies.risk import (
    PositionManager, RiskManager, PortfolioOptimizer,
    RiskLevel, get_risk_manager
)


class TestPositionManager:
    """仓位管理器测试"""
    
    def test_open_position(self):
        """测试开仓"""
        # 使用更大的仓位限制
        mgr = PositionManager(max_single_pct=0.5)
        pos = mgr.open_position('BTC/USDT', 'long', 1.0, 50000.0, 100000.0)
        
        assert pos is not None
        assert pos.symbol == 'BTC/USDT'
        assert pos.quantity == 1.0
    
    def test_position_limits(self):
        """测试仓位限制"""
        mgr = PositionManager(max_single_pct=0.05)
        
        # 超大仓位应该被拒绝 (100 * 50000 = 5000000 > 100000 * 0.05 = 5000)
        pos = mgr.open_position('BTC/USDT', 'long', 100.0, 50000.0, 100000.0)
        assert pos is None
    
    def test_update_price(self):
        """测试价格更新"""
        mgr = PositionManager(max_single_pct=0.5)
        mgr.open_position('BTC/USDT', 'long', 1.0, 50000.0, 100000.0)
        mgr.update_price('BTC/USDT', 51000.0)
        
        pos = mgr._positions['BTC/USDT']
        assert pos.current_price == 51000.0
        assert pos.pnl == 1000.0  # (51000-50000) * 1
    
    def test_close_position(self):
        """测试平仓"""
        mgr = PositionManager(max_single_pct=0.5)
        mgr.open_position('BTC/USDT', 'long', 1.0, 50000.0, 100000.0)
        mgr.update_price('BTC/USDT', 51000.0)
        
        pnl = mgr.close_position('BTC/USDT')
        assert pnl == 1000.0
        assert 'BTC/USDT' not in mgr._positions


class TestRiskManager:
    """风险管理器测试"""
    
    def test_check_trade(self):
        """测试交易检查"""
        # 使用宽松的仓位限制
        rm = RiskManager(max_position_pct=0.5)
        result = rm.check_trade('BTC/USDT', 'long', 1.0, 50000.0, 100000.0)
        
        assert result['allowed'] == True
        assert result['position_value'] == 50000.0
    
    def test_stop_loss_check(self):
        """测试止损检查"""
        rm = RiskManager(stop_loss_pct=0.02)
        
        # 开仓（使用宽松限制）
        rm.position_manager.max_single_pct = 0.5
        rm.position_manager.open_position('BTC/USDT', 'long', 1.0, 50000.0, 100000.0)
        
        # 价格下跌超过2%
        result = rm.check_trade('BTC/USDT', 'long', 1.0, 48900.0, 100000.0)
        assert result['checks']['stop_loss'] == False
    
    def test_should_stop_trading(self):
        """测试停止交易判断"""
        rm = RiskManager(max_drawdown_pct=0.15)  # 提高阈值
        
        # 初始权益
        rm.update_equity(100000.0)
        
        # 小幅回撤
        rm.update_equity(95000.0)
        
        # 10%回撤，没到15%阈值，不应该停止
        assert rm.should_stop_trading() == False
        
        # 大幅回撤
        rm.update_equity(70000.0)  # 30%回撤
        assert rm.should_stop_trading() == True


class TestPortfolioOptimizer:
    """投资组合优化器测试"""
    
    def test_equal_weight(self):
        """测试等权重分配"""
        returns = [
            [0.01, 0.02, -0.01],
            [0.02, 0.01, 0.01],
            [-0.01, 0.02, 0.02]
        ]
        
        weights = PortfolioOptimizer.calculate_weights(returns)
        assert len(weights) == 3
        assert abs(sum(weights.values()) - 1.0) < 0.01
    
    def test_risk_parity(self):
        """测试风险平价"""
        cov = [[1.0, 0.5], [0.5, 1.0]]
        weights = PortfolioOptimizer.risk_parity(cov)
        
        assert len(weights) == 2
        # 两个资产波动率相同，权重应该相等
        assert abs(weights['asset_0'] - weights['asset_1']) < 0.01


def test_get_risk_manager():
    """测试获取风险管理器"""
    rm = get_risk_manager()
    assert isinstance(rm, RiskManager)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
