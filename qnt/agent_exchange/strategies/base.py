"""
策略基类 - 所有策略继承此类
"""
from abc import ABC, abstractmethod
from ..models import TickerSnapshot, TradeSignal
from typing import Optional


class BaseStrategy(ABC):
    """策略基类"""

    name = "base"
    min_spread_pct = 0.0  # 最小价差阈值（%）

    def __init__(self, config: dict = None):
        self.config = config or {}

    @abstractmethod
    def evaluate(self, snapshot: TickerSnapshot) -> Optional[TradeSignal]:
        """评估价格快照，返回交易信号或None"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
