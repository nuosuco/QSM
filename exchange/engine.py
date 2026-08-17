"""
QNT 交易所 - 撮合引擎
"""
import time
import uuid
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from .orderbook import OrderBook, Order, OrderSide, OrderType


@dataclass
class Trade:
    """成交记录"""
    trade_id: str
    order_id_1: str
    order_id_2: str
    price: float
    quantity: float
    timestamp: float
    side_1: OrderSide
    side_2: OrderSide


class MatchingEngine:
    """撮合引擎"""
    
    def __init__(self, symbol: str = "QNT/USDT", fee_rate: float = 0.001):
        self.symbol = symbol
        self.orderbook = OrderBook(symbol)
        self.fee_rate = fee_rate
        self.trades: List[Trade] = []
        self.balance: Dict[str, Dict[str, float]] = {}
    
    def set_balance(self, trader: str, asset: str, amount: float):
        """设置账户余额"""
        if trader not in self.balance:
            self.balance[trader] = {}
        self.balance[trader][asset] = amount
        print(f"💰 Set balance: {trader} has {amount} {asset}")
    
    def get_balance(self, trader: str, asset: str) -> float:
        return self.balance.get(trader, {}).get(asset, 0.0)
    
    def submit_order(self, trader: str, side, quantity: float, 
                     price: float = 0.0, order_type="limit") -> Optional[str]:
        """提交订单"""
        if quantity <= 0:
            return None
        
        # 市场单自动定价
        if order_type == "market":
            if side == "buy":
                price = self.orderbook.get_best_ask() or (self.orderbook.get_mid_price() or 100) * 1.01
            else:
                price = self.orderbook.get_best_bid() or (self.orderbook.get_mid_price() or 100) * 0.99
        
        order_id = str(uuid.uuid4())[:8]
        order = Order(
            order_id=order_id,
            side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
            trader=trader
        )
        
        # 检查余额
        if order.side == OrderSide.BUY:
            cost = quantity * price
            if self.get_balance(trader, "USDT") < cost:
                print(f"❌ Insufficient balance for {trader}")
                return None
        else:
            asset = self.symbol.split("/")[0]
            if self.get_balance(trader, asset) < quantity:
                print(f"❌ Insufficient {asset} for {trader}")
                return None
        
        self.orderbook.add_order(order)
        print(f"📤 Order submitted: {side} {quantity} @ {price:.4f} ({order_id})")
        
        # 尝试撮合
        self._match_orders(order)
        
        return order_id
    
    def _match_orders(self, incoming: Order):
        """撮合订单"""
        if incoming.side == OrderSide.BUY:
            self._match_buy(incoming)
        else:
            self._match_sell(incoming)
    
    def _match_buy(self, buy_order: Order):
        """买入撮合 - 匹配ask"""
        while buy_order.remaining > 0.0001 and self.orderbook.asks:
            best_ask = self.orderbook.asks[0]
            if best_ask.price > buy_order.price:
                break  # 卖价高于买价，不成交
            
            trade_qty = min(buy_order.remaining, best_ask.quantity)
            trade_price = best_ask.price
            
            self._execute_trade(buy_order, best_ask, trade_price, trade_qty)
            
            # 扣手续费
            fee = trade_qty * trade_price * self.fee_rate
            self._deduct_fee(buy_order.trader, "USDT", fee)
            self._deduct_fee(best_ask.orders[0].trader, self.symbol.split("/")[0], 
                           trade_qty * self.fee_rate)
    
    def _match_sell(self, sell_order: Order):
        """卖出撮合 - 匹配bid"""
        while sell_order.remaining > 0.0001 and self.orderbook.bids:
            best_bid = self.orderbook.bids[0]
            if best_bid.price < sell_order.price:
                break  # 买价低于卖价，不成交
            
            trade_qty = min(sell_order.remaining, best_bid.quantity)
            trade_price = best_bid.price
            
            self._execute_trade(sell_order, best_bid, trade_price, trade_qty)
            
            # 扣手续费
            fee = trade_qty * trade_price * self.fee_rate
            self._deduct_fee(sell_order.trader, self.symbol.split("/")[0], trade_qty * self.fee_rate)
            self._deduct_fee(best_bid.orders[0].trader, "USDT", fee)
    
    def _execute_trade(self, order1: Order, book_entry, price: float, quantity: float):
        """执行成交"""
        trade_id = f"{order1.order_id}:{book_entry.orders[0].order_id}:{time.time()}"
        trade = Trade(
            trade_id=trade_id,
            order_id_1=order1.order_id,
            order_id_2=book_entry.orders[0].order_id,
            price=price,
            quantity=quantity,
            timestamp=time.time(),
            side_1=order1.side,
            side_2=OrderSide.SELL if order1.side == OrderSide.BUY else OrderSide.BUY
        )
        self.trades.append(trade)
        
        # 更新订单
        order1.filled += quantity
        for entry in [self.orderbook.bids, self.orderbook.asks]:
            for eb in entry:
                if eb is book_entry:
                    eb.quantity -= quantity
                    if eb.quantity <= 0.0001:
                        entry.remove(eb)
        
        if order1.is_complete:
            self.orderbook.remove_order(order1.order_id)
        
        print(f"✅ Trade: {quantity:.4f} @ {price:.4f}")
    
    def _deduct_fee(self, trader: str, asset: str, amount: float):
        """扣手续费"""
        bal = self.get_balance(trader, asset)
        self.balance[trader][asset] = bal - amount
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        order = self.orderbook.remove_order(order_id)
        if order:
            print(f"❌ Order cancelled: {order_id}")
            return True
        return False
    
    def get_orderbook_snapshot(self) -> Dict[str, Any]:
        """获取订单簿快照"""
        spread_pct = self.orderbook.get_spread_pct()
        return {
            "symbol": self.symbol,
            "best_bid": self.orderbook.get_best_bid(),
            "best_ask": self.orderbook.get_best_ask(),
            "spread": self.orderbook.get_spread(),
            "spread_pct": round(spread_pct, 4) if spread_pct else None,
            "depth": self.orderbook.get_depth(5),
            "recent_trades": [
                {"price": t.price, "quantity": t.quantity, "timestamp": t.timestamp}
                for t in self.trades[-10:]
            ]
        }


def create_exchange(symbol: str = "QNT/USDT", fee_rate: float = 0.001) -> MatchingEngine:
    return MatchingEngine(symbol=symbol, fee_rate=fee_rate)
