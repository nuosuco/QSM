"""
价差套利策略 - 核心策略
永续合约 vs 现货 价差套利
"""
import logging
from ..models import TickerSnapshot, TradeSignal
from .base import BaseStrategy

logger = logging.getLogger(__name__)


class SpreadStrategy(BaseStrategy):
    """价差套利策略"""

    name = "spread"

    def __init__(self, config: dict = None):
        super().__init__(config)
        # 成本结构：双边手续费 + 滑点
        self.bid_ask_cost = 0.0012  # 双边0.12%
        self.slippage = 0.0003       # 滑点0.03%
        self.total_cost = self.bid_ask_cost + self.slippage  # ~0.15%
        # 最小净利要求
        self.min_net_profit_pct = 0.0005  # 0.05%

    def get_name(self) -> str:
        return "spread"

    def evaluate(self, snapshot: TickerSnapshot) -> TradeSignal | None:
        """
        评估价差：
        - 永续 > 现货 → 买永续卖现货（空头）
        - 永续 < 现货 → 买现货卖永续（多头）
        """
        if snapshot.spot_bid <= 0 or snapshot.perp_ask <= 0:
            return None

        spread = snapshot.spread_pct
        net_profit = spread - self.total_cost * 100  # 转为百分比

        if net_profit < self.min_net_profit_pct * 100:
            return None

        # 判断方向
        if snapshot.mid_perp > snapshot.mid_spot:
            # 永续贵 → 卖永续买现货
            side = "sell_perp_buy_spot"
            exec_price = snapshot.perp_bid  # 卖永续的价格
        else:
            # 现货贵 → 买永续卖现货
            side = "buy_perp_sell_spot"
            exec_price = snapshot.ask  # 买现货的价格

        return TradeSignal(
            exchange=snapshot.exchange,
            symbol=snapshot.symbol,
            side=side,
            price=exec_price,
            amount=self._calc_amount(snapshot, exec_price),
            expected_profit_pct=net_profit / 100,
            timestamp=snapshot.timestamp,
            strategy=self.name,
            metadata={
                "spread_pct": spread,
                "mid_spot": snapshot.mid_spot,
                "mid_perp": snapshot.mid_perp,
                "direction": "short" if side == "sell_perp_buy_spot" else "long"
            }
        )

    def _calc_amount(self, snap: TickerSnapshot, price: float) -> float:
        """根据价格和预估仓位计算数量"""
        # 简化：固定100U仓位
        position_size = 100.0
        if price <= 0:
            return 0.0
        return position_size / price
