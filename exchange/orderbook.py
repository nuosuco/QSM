"""
QNT 交易所 - 订单簿
"""
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    POST_ONLY = "post_only"


@dataclass
class Order:
    """订单"""
    order_id: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float
    timestamp: float = field(default_factory=time.time)
    trader: str = ""
    filled: float = 0.0
    
    @property
    def remaining(self) -> float:
        return self.quantity - self.filled
    
    @property
    def is_complete(self) -> bool:
        return self.remaining <= 0.0001


@dataclass
class OrderBookEntry:
    """订单簿条目"""
    price: float
    quantity: float
    orders: List[Order] = field(default_factory=list)


class OrderBook:
    """订单簿 - 买卖盘"""
    
    def __init__(self, symbol: str = "QNT/USDT"):
        self.symbol = symbol
        self.bids: List[OrderBookEntry] = []  # 买单（价格从高到低）
        self.asks: List[OrderBookEntry] = []  # 卖单（价格从低到高）
        self.order_map: Dict[str, Order] = {}
    
    def add_order(self, order: Order) -> bool:
        """添加订单"""
        if order.quantity <= 0 or order.price < 0:
            return False
        
        self.order_map[order.order_id] = order
        
        if order.side == OrderSide.BUY:
            self._add_bid(order)
        else:
            self._add_ask(order)
        
        return True
    
    def _add_bid(self, order: Order):
        """添加买单到bids"""
        inserted = False
        for i, entry in enumerate(self.bids):
            if abs(entry.price - order.price) < 0.0001:
                entry.quantity += order.remaining
                entry.orders.append(order)
                inserted = True
                break
            elif entry.price < order.price:
                self.bids.insert(i, OrderBookEntry(
                    price=order.price, quantity=order.remaining, orders=[order]
                ))
                inserted = True
                break
        
        if not inserted:
            self.bids.append(OrderBookEntry(price=order.price, quantity=order.remaining, orders=[order]))
        self.bids.sort(key=lambda x: x.price, reverse=True)
    
    def _add_ask(self, order: Order):
        """添加卖单到asks"""
        inserted = False
        for i, entry in enumerate(self.asks):
            if abs(entry.price - order.price) < 0.0001:
                entry.quantity += order.remaining
                entry.orders.append(order)
                inserted = True
                break
            elif entry.price > order.price:
                self.asks.insert(i, OrderBookEntry(
                    price=order.price, quantity=order.remaining, orders=[order]
                ))
                inserted = True
                break
        
        if not inserted:
            self.asks.append(OrderBookEntry(price=order.price, quantity=order.remaining, orders=[order]))
        self.asks.sort(key=lambda x: x.price)
    
    def get_spread(self) -> Optional[float]:
        """获取价差"""
        if self.bids and self.asks:
            best_bid = self.bids[0].price
            best_ask = self.asks[0].price
            if best_ask > best_bid:
                return best_ask - best_bid
        return None
    
    def get_spread_pct(self) -> Optional[float]:
        """获取价差点数百分比"""
        spread = self.get_spread()
        if spread and self.bids and self.asks:
            mid = (self.bids[0].price + self.asks[0].price) / 2
            return (spread / mid) * 100
        return None
    
    def get_best_bid(self) -> Optional[float]:
        return self.bids[0].price if self.bids else None
    
    def get_best_ask(self) -> Optional[float]:
        return self.asks[0].price if self.asks else None
    
    def get_mid_price(self) -> Optional[float]:
        if self.bids and self.asks:
            return (self.bids[0].price + self.asks[0].price) / 2
        return None
    
    def remove_order(self, order_id: str) -> Optional[Order]:
        """移除订单"""
        order = self.order_map.pop(order_id, None)
        if not order:
            return None
        
        if order.side == OrderSide.BUY:
            self._remove_from_bids(order)
        else:
            self._remove_from_asks(order)
        return order
    
    def _remove_from_bids(self, order: Order):
        for entry in self.bids:
            if any(o.order_id == order.order_id for o in entry.orders):
                entry.orders = [o for o in entry.orders if o.order_id != order.order_id]
                entry.quantity -= order.remaining
                if entry.quantity <= 0:
                    self.bids.remove(entry)
                return
    
    def _remove_from_asks(self, order: Order):
        for entry in self.asks:
            if any(o.order_id == order.order_id for o in entry.orders):
                entry.orders = [o for o in entry.orders if o.order_id != order.order_id]
                entry.quantity -= order.remaining
                if entry.quantity <= 0:
                    self.asks.remove(entry)
                return
    
    def get_depth(self, levels: int = 5) -> Dict[str, Any]:
        """获取深度"""
        return {
            "bids": [{"price": e.price, "quantity": e.quantity} 
                     for e in self.bids[:levels]],
            "asks": [{"price": e.price, "quantity": e.quantity} 
                     for e in self.asks[:levels]]
        }
    
    def __repr__(self):
        spread = self.get_spread_pct()
        return f"OrderBook({self.symbol}, spread={spread:.4f}%)"
