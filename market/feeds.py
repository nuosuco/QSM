"""
QNT 行情数据模块
"""
import asyncio
import random
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime

# 延迟导入event_bus，避免循环依赖
_event_bus = None

def _get_event_bus():
    global _event_bus
    if _event_bus is None:
        from api.websocket import event_bus
        _event_bus = event_bus
    return _event_bus


@dataclass
class MarketData:
    """市场数据"""
    symbol: str
    price: float
    volume: float
    bid: float
    ask: float
    timestamp: float


class MarketDataGenerator:
    """行情数据生成器 - 模拟市场数据"""
    
    def __init__(self, initial_price: float = 100.0, volatility: float = 0.02):
        self.current_price = initial_price
        self.volatility = volatility
        self._history: List[MarketData] = []
        self._listeners: List[Callable] = []
    
    def generate_tick(self) -> MarketData:
        """生成新的行情 tick"""
        # 随机游走
        change = random.gauss(0, self.volatility * self.current_price)
        self.current_price = max(0.01, self.current_price + change)
        
        spread = self.current_price * random.uniform(0.0001, 0.001)
        
        data = MarketData(
            symbol='QNT/USDT',
            price=self.current_price,
            volume=random.uniform(10, 1000),
            bid=self.current_price - spread / 2,
            ask=self.current_price + spread / 2,
            timestamp=time.time()
        )
        
        self._history.append(data)
        if len(self._history) > 10000:
            self._history = self._history[-5000:]
        
        # 通知监听者
        for listener in self._listeners:
            try:
                listener(data)
            except Exception as e:
                print(f"⚠️ Market data listener error: {e}")
        
        return data
    
    def add_listener(self, callback: Callable):
        """添加监听者"""
        self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        """移除监听者"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def get_history(self, limit: int = 100) -> List[MarketData]:
        """获取历史数据"""
        return self._history[-limit:]
    
    def get_latest(self) -> MarketData:
        """获取最新数据"""
        return self._history[-1] if self._history else None


class OrderBookSimulator:
    """订单簿模拟器"""
    
    def __init__(self, symbol: str = 'QNT/USDT'):
        self.symbol = symbol
        self._bids: List[Dict] = []  # [(price, quantity), ...]
        self._asks: List[Dict] = []  # [(price, quantity), ...]
        self._last_price = 100.0
    
    def update(self, market_data: MarketData):
        """根据市场数据更新订单簿"""
        self._last_price = market_data.price
        
        # 模拟订单簿深度
        spread = market_data.price * 0.001
        
        # 更新买卖盘
        self._bids = [
            (market_data.price - spread * i, random.uniform(1, 100))
            for i in range(1, 11)
        ]
        self._asks = [
            (market_data.price + spread * i, random.uniform(1, 100))
            for i in range(1, 11)
        ]
    
    def get_best_bid(self) -> Optional[float]:
        """最佳买价"""
        return max([b[0] for b in self._bids]) if self._bids else None
    
    def get_best_ask(self) -> Optional[float]:
        """最佳卖价"""
        return min([a[0] for a in self._asks] if self._asks else [])
    
    def get_spread(self) -> float:
        """买卖价差"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid and best_ask:
            return (best_ask - best_bid) / best_bid
        return 0.0


class FeedManager:
    """行情流管理器"""
    
    def __init__(self):
        self.market_data = MarketDataGenerator()
        self.order_book = OrderBookSimulator()
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self, tick_interval: float = 0.1):
        """启动行情流"""
        self._running = True
        print(f"📡 Market data feed started (interval={tick_interval}s)")
        
        while self._running:
            data = self.market_data.generate_tick()
            self.order_book.update(data)
            
            # 触发事件
            _get_event_bus().publish('market_tick', data.__dict__)
            _get_event_bus().publish('orderbook_update', {
                'symbol': self.order_book.symbol,
                'best_bid': self.order_book.get_best_bid(),
                'best_ask': self.order_book.get_best_ask(),
                'spread': self.order_book.get_spread()
            })
            
            await asyncio.sleep(tick_interval)
    
    def stop(self):
        """停止行情流"""
        self._running = False
        print("📡 Market data feed stopped")
    
    def get_market_data(self) -> MarketData:
        """获取最新市场数据"""
        return self.market_data.get_latest()
    
    def get_orderbook(self) -> Dict[str, Any]:
        """获取订单簿状态"""
        return {
            'symbol': self.order_book.symbol,
            'best_bid': self.order_book.get_best_bid(),
            'best_ask': self.order_book.get_best_ask(),
            'spread': self.order_book.get_spread(),
            'mid_price': (self.order_book.get_best_bid() + self.order_book.get_best_ask()) / 2
        }


# 全局行情管理器
feed_manager = FeedManager()
