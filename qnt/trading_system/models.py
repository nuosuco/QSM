"""
记忆承载·碧树西风交易系统 - 数据模型
核心数据结构定义
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class SignalType(Enum):
    SINGLE_EXCHANGE = "single_exchange"
    CROSS_EXCHANGE = "cross_exchange"
    DEPTH_ANOMALY = "depth_anomaly"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class OrderBookEntry:
    price: float
    amount: float


@dataclass
class OrderBook:
    exchange: str
    symbol: str
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]
    timestamp: float
    
    @property
    def mid_price(self) -> float:
        if self.bids and self.asks:
            return (self.bids[0].price + self.asks[0].price) / 2.0
        return 0.0

    @property
    def spread(self) -> float:
        if self.bids and self.asks:
            return self.asks[0].price - self.bids[0].price
        return 0.0


@dataclass
class Trade:
    id: str
    exchange: str
    symbol: str
    side: OrderSide
    price: float
    amount: float
    cost: float
    fee: float
    timestamp: float
    pnl: float = 0.0


@dataclass
class FatFingerSignal:
    signal_type: SignalType
    symbol: str
    exchange: str
    price: float
    fair_price: float
    deviation_pct: float
    signal_strength: float
    timestamp: float
    depth_available: float = 0.0
    target_side: OrderSide = OrderSide.BUY
    target_exchange: str = ""
    details: Dict = field(default_factory=dict)


@dataclass
class Order:
    order_id: str
    exchange: str
    symbol: str
    side: OrderSide
    price: float
    amount: float
    status: OrderStatus = OrderStatus.PENDING
    filled_amount: float = 0.0
    fee: float = 0.0
    timestamp: float = 0.0


@dataclass
class BacktestResult:
    initial_capital: float = 0.0
    final_equity: float = 0.0
    total_return_pct: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    max_drawdown_pct: float = 0.0
    max_consecutive_losses: int = 0
    bishu_max_loss_pct: float = 0.0
    bishu_max_gain_pct: float = 0.0
    bishu_downward_limited: bool = False
    bishu_upward_unlimited: bool = False
    bishu_fat_tail: bool = False
    pnl_distribution: Dict[str, int] = field(default_factory=dict)
    equity_curve: List[float] = field(default_factory=list)
    trades: List[Trade] = field(default_factory=list)
    total_signals: int = 0
    executed_signals: int = 0
    
    def bishu_check(self) -> Dict[str, bool]:
        return {
            "1.向下有限(最大单笔亏损≤10%)": self.bishu_downward_limited,
            "2.向上无限(最大单笔盈利>50%)": self.bishu_upward_unlimited,
            "3.肥尾(盈利分布右偏)": self.bishu_fat_tail,
            "4.最大连续亏损≤5次": self.max_consecutive_losses <= 5,
            "5.最大回撤≤10%": self.max_drawdown_pct <= 10.0,
        }

    def summary(self) -> str:
        return f"""
{'='*50}
回测结果
{'='*50}
初始资金:     ${self.initial_capital:,.2f}
最终权益:     ${self.final_equity:,.2f}
总收益率:     {self.total_return_pct:.2f}%
总交易数:     {self.total_trades}
胜率:         {self.win_rate*100:.1f}%
最大回撤:     {self.max_drawdown_pct:.2f}%
最大连续亏损: {self.max_consecutive_losses}次
{'='*50}
碧树西风标准检验:
""" + "\n".join(f"  {k}: {'✅' if v else '❌'}" for k, v in self.bishu_check().items())
