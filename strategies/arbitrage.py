"""
QNT 策略 - 价差套利
"""
from typing import List, Dict, Any, Optional
try:
    from ..exchange.orderbook import OrderBook
except ImportError:
    from exchange.orderbook import OrderBook


class SpreadArbitrageStrategy:
    """价差套利策略 - 捡乌龙指"""
    
    def __init__(self, min_spread_pct: float = 0.05, max_spread_pct: float = 5.0):
        self.min_spread_pct = min_spread_pct
        self.max_spread_pct = max_spread_pct
        self.signals: List[Dict[str, Any]] = []
    
    def detect(self, orderbook: OrderBook) -> Optional[Dict[str, Any]]:
        """检测套利机会"""
        spread_pct = orderbook.get_spread_pct()
        if spread_pct is None:
            return None
        
        if self.min_spread_pct < spread_pct < self.max_spread_pct:
            signal = {
                "type": "spread_arb",
                "spread_pct": spread_pct,
                "best_bid": orderbook.get_best_bid(),
                "best_ask": orderbook.get_best_ask(),
                "mid_price": orderbook.get_mid_price(),
                "timestamp": __import__('time').time(),
                "action": "BUY_LOW_SELL_HIGH"
            }
            self.signals.append(signal)
            return signal
        
        return None
    
    def get_signals(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.signals[-limit:]
    
    def __repr__(self):
        return f"SpreadArb(min={self.min_spread_pct}%, max={self.max_spread_pct}%)"


class MarketMakingStrategy:
    """做市策略"""
    
    def __init__(self, spread_pct: float = 0.1, order_size: float = 100.0):
        self.spread_pct = spread_pct
        self.order_size = order_size
        self.pending_orders: List[Dict[str, Any]] = []
    
    def generate_orders(self, mid_price: float) -> Dict[str, float]:
        """生成挂单价格"""
        if not mid_price:
            return {}
        
        half_spread = mid_price * (self.spread_pct / 200)
        return {
            "bid": mid_price - half_spread,
            "ask": mid_price + half_spread,
            "size": self.order_size
        }
    
    def __repr__(self):
        return f"MarketMaker(spread={self.spread_pct}%, size={self.order_size})"
