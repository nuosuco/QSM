"""
数据模型 - 叠加态并行系统的数据结构
"""
from dataclasses import dataclass, field
from typing import Optional, List
import time


@dataclass
class TickerSnapshot:
    """价格快照 - 叠加态的一个状态"""
    exchange: str
    symbol: str
    bid: float
    ask: float
    timestamp: float
    # 现货 vs 永续
    spot_bid: float = 0.0
    spot_ask: float = 0.0
    perp_bid: float = 0.0
    perp_ask: float = 0.0

    @property
    def spread_pct(self) -> float:
        """现货-永续价差百分比"""
        if self.spot_bid <= 0 or self.perp_ask <= 0:
            return 0.0
        return abs(self.perp_ask - self.spot_bid) / self.spot_bid * 100

    @property
    def mid_spot(self) -> float:
        return (self.spot_bid + self.spot_ask) / 2

    @property
    def mid_perp(self) -> float:
        return (self.perp_bid + self.perp_ask) / 2


@dataclass
class TradeSignal:
    """交易信号 - Agent决策结果"""
    exchange: str
    symbol: str
    side: str  # 'buy' or 'sell'
    price: float
    amount: float
    expected_profit_pct: float
    timestamp: float
    strategy: str = "spread"
    metadata: dict = field(default_factory=dict)


@dataclass
class ChannelState:
    """通道状态 - 每个交易所的独立叠加态"""
    exchange: str
    tickers: dict = field(default_factory=dict)  # symbol -> TickerSnapshot
    open_positions: dict = field(default_factory=dict)  # symbol -> position
    balance: float = 0.0
    active: bool = True
    last_update: float = 0.0
    errors: int = 0


@dataclass
class AgentMemory:
    """Agent记忆 - 跨通道的共享记忆"""
    known_spreads: dict = field(default_factory=dict)  # (exchange, symbol) -> history
    recent_trades: List[dict] = field(default_factory=list)
    pattern_cache: dict = field(default_factory=dict)
    last_scan_time: float = 0.0
