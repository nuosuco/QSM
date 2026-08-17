"""
自适应策略引擎 - 数据模型（三平台版）
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

@dataclass
class MarketDataPoint:
    """市场数据点"""
    timestamp: float
    exchange: str = ""
    symbol: str = ""
    spot_bid: float = 0.0
    spot_ask: float = 0.0
    spot_last: float = 0.0
    perp_bid: float = 0.0
    perp_ask: float = 0.0
    perp_last: float = 0.0
    spot_volume: float = 0.0
    perp_volume: float = 0.0
    spread_pct: float = 0.0
    basis_pct: float = 0.0
    depth_ratio: float = 1.0

@dataclass
class SignalRecord:
    """信号记录"""
    timestamp: float
    exchange: str = ""
    symbol: str = ""
    signal_type: str = ""
    strategy: str = ""
    expected_profit: float = 0.0
    actual_profit: float = 0.0
    executed: bool = False
    metadata: Dict = field(default_factory=dict)

@dataclass
class DiscoveredPattern:
    """发现的模式"""
    exchange: str = ""
    pattern_type: str = ""
    symbol: str = ""
    confidence: float = 0.0
    profitability: float = 0.0
    parameters: Dict = field(default_factory=dict)
    status: str = "experimental"
    
    @property
    def is_profitable(self) -> bool:
        return self.profitability > 0.28
    
    @property
    def is_reliable(self) -> bool:
        return self.confidence > 0.5 and self.status == "active"

@dataclass
class StrategyProfile:
    """策略档案"""
    name: str = ""
    description: str = ""
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
        return self.weight * (0.5 + self.win_rate * 0.3 + min(self.avg_profit, 1.0) * 0.2)