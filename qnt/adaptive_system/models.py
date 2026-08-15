"""
自适应策略引擎 - 数据模型
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

@dataclass
class MarketDataPoint:
    """市场数据点"""
    timestamp: float
    symbol: str
    spot_bid: float
    spot_ask: float
    spot_last: float
    perp_bid: float
    perp_ask: float
    perp_last: float
    spread_pct: float
    basis_pct: float
    depth_ratio: float

@dataclass
class SignalRecord:
    """信号记录"""
    timestamp: float
    symbol: str
    signal_type: str
    strategy: str
    expected_profit: float
    actual_profit: float = 0.0
    executed: bool = False
    metadata: Dict = field(default_factory=dict)

@dataclass
class DiscoveredPattern:
    """发现的模式"""
    pattern_type: str
    symbol: str
    confidence: float
    profitability: float
    parameters: Dict
    status: str = "experimental"
    
    @property
    def is_profitable(self) -> bool:
        return self.profitability > 0.28  # 扣除手续费后仍有利润
    
    @property
    def is_reliable(self) -> bool:
        return self.confidence > 0.5 and self.status == "active"

@dataclass
class StrategyProfile:
    """策略档案"""
    name: str
    description: str
    weight: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    win_rate: float = 0.0
    avg_profit: float = 0.0
    total_profit: float = 0.0
    last_active: float = 0.0
    parameters: Dict = field(default_factory=dict)
    
    @property
    def score(self) -> float:
        """综合评分"""
        return self.weight * (0.5 + self.win_rate * 0.3 + min(self.avg_profit, 1.0) * 0.2)
