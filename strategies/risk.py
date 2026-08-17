"""
QNT 风险管理模块
支持多策略风险控制和资金管理
"""
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Position:
    """持仓"""
    symbol: str
    side: str  # 'long' or 'short'
    quantity: float
    entry_price: float
    current_price: float
    pnl: float = 0.0
    pnl_pct: float = 0.0
    opened_at: float = field(default_factory=time.time)


@dataclass
class RiskMetrics:
    """风险指标"""
    total_exposure: float = 0.0
    max_drawdown: float = 0.0
    var_95: float = 0.0
    Sharpe_ratio: float = 0.0
    portfolio_value: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW


class PositionManager:
    """仓位管理器"""
    
    def __init__(self, max_position_pct: float = 0.2, max_single_pct: float = 0.05):
        self.max_position_pct = max_position_pct
        self.max_single_pct = max_single_pct
        self._positions: Dict[str, Position] = {}
        self._trade_history: List[Dict] = []
    
    def open_position(self, symbol: str, side: str, quantity: float, 
                      price: float, capital: float) -> Optional[Position]:
        """开仓"""
        # 检查仓位限制
        position_value = quantity * price
        if position_value > capital * self.max_single_pct:
            return None
        
        if len(self._positions) >= 10:  # 最多10个仓位
            return None
        
        position = Position(
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=price,
            current_price=price
        )
        
        self._positions[symbol] = position
        self._trade_history.append({
            'action': 'open',
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'timestamp': time.time()
        })
        
        return position
    
    def update_price(self, symbol: str, price: float):
        """更新价格"""
        if symbol in self._positions:
            pos = self._positions[symbol]
            pos.current_price = price
            if pos.side == 'long':
                pos.pnl = (price - pos.entry_price) * pos.quantity
            else:
                pos.pnl = (pos.entry_price - price) * pos.quantity
            pos.pnl_pct = (pos.pnl / (pos.entry_price * pos.quantity)) * 100 if pos.entry_price > 0 else 0
    
    def close_position(self, symbol: str) -> Optional[float]:
        """平仓"""
        if symbol not in self._positions:
            return None
        
        position = self._positions.pop(symbol)
        pnl = position.pnl
        
        self._trade_history.append({
            'action': 'close',
            'symbol': symbol,
            'pnl': pnl,
            'pnl_pct': position.pnl_pct,
            'timestamp': time.time()
        })
        
        return pnl
    
    def get_positions(self) -> Dict[str, Position]:
        """获取所有持仓"""
        return dict(self._positions)
    
    def get_total_exposure(self, prices: Dict[str, float]) -> float:
        """计算总敞口"""
        total = 0.0
        for symbol, pos in self._positions.items():
            current_price = prices.get(symbol, pos.current_price)
            self.update_price(symbol, current_price)
            total += pos.quantity * current_price
        return total


class RiskManager:
    """风险管理器"""
    
    def __init__(self, 
                 max_drawdown_pct: float = 0.1,
                 max_position_pct: float = 0.2,
                 var_confidence: float = 0.95,
                 stop_loss_pct: float = 0.02):
        self.max_drawdown_pct = max_drawdown_pct
        self.max_position_pct = max_position_pct
        self.var_confidence = var_confidence
        self.stop_loss_pct = stop_loss_pct
        self._peak_value = 0.0
        self._equity_curve: List[float] = []
        self._position_mgr = PositionManager(max_position_pct)
    
    def check_trade(self, symbol: str, side: str, quantity: float, 
                    price: float, capital: float) -> Dict[str, Any]:
        """检查交易是否合规"""
        position_value = quantity * price
        exposure = self._position_mgr.get_total_exposure({symbol: price}) + position_value
        
        checks = {
            'position_limit': position_value <= capital * self.max_position_pct,
            'exposure_limit': exposure <= capital * 0.8,  # 总敞口不超过80%
            'stop_loss': True  # 默认通过，由止损检查单独处理
        }
        
        # 止损检查
        if symbol in self._position_mgr._positions:
            pos = self._position_mgr._positions[symbol]
            if pos.side == 'long' and price < pos.entry_price * (1 - self.stop_loss_pct):
                checks['stop_loss'] = False
            elif pos.side == 'short' and price > pos.entry_price * (1 + self.stop_loss_pct):
                checks['stop_loss'] = False
        
        all_passed = all(checks.values())
        
        return {
            'allowed': all_passed,
            'checks': checks,
            'position_value': position_value,
            'total_exposure': exposure
        }
    
    def update_equity(self, equity: float):
        """更新权益"""
        self._equity_curve.append(equity)
        self._peak_value = max(self._peak_value, equity)
    
    def get_risk_metrics(self, capital: float) -> RiskMetrics:
        """获取风险指标"""
        if not self._equity_curve:
            return RiskMetrics(portfolio_value=capital)
        
        # 计算最大回撤
        peak = self._equity_curve[0]
        max_dd = 0.0
        for eq in self._equity_curve:
            peak = max(peak, eq)
            dd = (peak - eq) / peak
            max_dd = max(max_dd, dd)
        
        # 计算VaR（简化版）
        returns = []
        for i in range(1, len(self._equity_curve)):
            ret = (self._equity_curve[i] - self._equity_curve[i-1]) / self._equity_curve[i-1]
            returns.append(ret)
        
        var_95 = abs(min(returns)) if returns else 0
        
        # 确定风险等级
        if max_dd > 0.15 or var_95 > 0.05:
            risk_level = RiskLevel.CRITICAL
        elif max_dd > 0.1 or var_95 > 0.03:
            risk_level = RiskLevel.HIGH
        elif max_dd > 0.05:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return RiskMetrics(
            max_drawdown=max_dd,
            var_95=var_95,
            portfolio_value=self._equity_curve[-1],
            risk_level=risk_level
        )
    
    def should_stop_trading(self) -> bool:
        """判断是否应该停止交易"""
        metrics = self.get_risk_metrics(100000)
        return metrics.risk_level == RiskLevel.CRITICAL or metrics.max_drawdown >= self.max_drawdown_pct
    
    @property
    def position_manager(self) -> PositionManager:
        return self._position_mgr


class PortfolioOptimizer:
    """投资组合优化器"""
    
    @staticmethod
    def calculate_weights(return_series: List[List[float]], 
                          target_return: float = 0.001) -> Dict[str, float]:
        """计算最优权重（简化版均值方差）"""
        n_assets = len(return_series)
        if n_assets == 0:
            return {}
        
        # 计算平均收益
        avg_returns = []
        for series in return_series:
            avg = sum(series) / len(series) if series else 0
            avg_returns.append(avg)
        
        # 等权重分配（简化）
        weight = 1.0 / n_assets
        return {f'asset_{i}': weight for i in range(n_assets)}
    
    @staticmethod
    def risk_parity(cov_matrix: List[List[float]]) -> Dict[str, float]:
        """风险平价配置"""
        n = len(cov_matrix)
        if n == 0:
            return {}
        
        # 简化版风险平价
        vols = [cov_matrix[i][i] ** 0.5 for i in range(n)]
        total_vol = sum(vols)
        
        if total_vol == 0:
            return {f'asset_{i}': 1/n for i in range(n)}
        
        weights = {f'asset_{i}': v/total_vol for i, v in enumerate(vols)}
        return weights


# 全局风险管理器
_risk_manager: Optional[RiskManager] = None


def get_risk_manager() -> RiskManager:
    """获取风险管理器"""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = RiskManager()
    return _risk_manager
