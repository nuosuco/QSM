"""
记忆承载·碧树西风交易系统 - 交易所适配器
支持Bitget多交易所连接、深度获取、订单管理
"""
import ccxt
import time
from typing import Dict, List, Optional
from datetime import datetime

from .models import OrderBookEntry, OrderBook, Order, OrderSide, OrderStatus
from .config import ExchangeConfig


class ExchangeAdapter:
    """交易所适配器"""
    
    def __init__(self, config: ExchangeConfig):
        self.config = config
        self.exchange = None
        self.load_credentials()
        self.connect()
    
    def load_credentials(self):
        """加载API凭证"""
        import os
        self.config.api_key = os.getenv(f'{self.config.name.upper()}_API_KEY', self.config.api_key)
        self.config.api_secret = os.getenv(f'{self.config.name.upper()}_API_SECRET', self.config.api_secret)
        if hasattr(self.config, 'passphrase'):
            self.config.passphrase = os.getenv(f'{self.config.name.upper()}_API_PASSPHRASE', self.config.passphrase or '')
    
    def connect(self):
        """连接交易所"""
        try:
            if self.config.name == "bitget":
                self.exchange = ccxt.bitget({
                    'apiKey': self.config.api_key,
                    'secret': self.config.api_secret,
                    'password': self.config.passphrase,
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'spot',
                    }
                })
            else:
                exchange_class = getattr(ccxt, self.config.name)
                self.exchange = exchange_class({
                    'apiKey': self.config.api_key,
                    'secret': self.config.api_secret,
                    'password': self.config.passphrase,
                    'enableRateLimit': True,
                })
            
            print(f"✅ 成功连接交易所: {self.config.name}")
            return True
        except Exception as e:
            print(f"❌ 连接交易所失败: {e}")
            return False
    
    def fetch_orderbook(self, symbol: str, limit: int = 20) -> Optional[OrderBook]:
        """获取深度簿"""
        try:
            ob = self.exchange.fetch_order_book(symbol, limit)
            bids = [OrderBookEntry(price=float(b[0]), amount=float(b[1])) 
                    for b in ob['bids'][:limit]]
            asks = [OrderBookEntry(price=float(a[0]), amount=float(a[1])) 
                    for a in ob['asks'][:limit]]
            
            return OrderBook(
                exchange=self.config.name,
                symbol=symbol,
                bids=bids,
                asks=asks,
                timestamp=time.time()
            )
        except Exception as e:
            print(f"⚠️ 获取深度簿失败 {symbol}: {e}")
            return None
    
    def fetch_ticker(self, symbol: str) -> Optional[Dict]:
        """获取行情"""
        try:
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            print(f"⚠️ 获取行情失败 {symbol}: {e}")
            return None
    
    def create_post_only_order(
        self, 
        symbol: str, 
        side: OrderSide, 
        amount: float, 
        price: float
    ) -> Optional[Order]:
        """创建Post-Only订单（确保Maker）"""
        try:
            order_type = 'limit'
            post_only = True
            
            order = self.exchange.create_order(
                symbol,
                order_type,
                side.value,
                amount,
                price,
                {'postOnly': post_only}
            )
            
            return Order(
                order_id=order.get('id', ''),
                exchange=self.config.name,
                symbol=symbol,
                side=side,
                price=price,
                amount=amount,
                status=OrderStatus.PENDING
            )
        except Exception as e:
            print(f"⚠️ 下单失败 {side.value} {symbol}: {e}")
            return None
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """取消订单"""
        try:
            self.exchange.cancel_order(order_id, symbol)
            return True
        except Exception as e:
            print(f"⚠️ 撤单失败: {e}")
            return False
    
    def get_balance(self) -> Dict[str, float]:
        """获取余额"""
        try:
            balance = self.exchange.fetch_balance()
            result = {}
            for currency, amount in balance['total'].items():
                if amount > 0:
                    result[currency] = amount
            return result
        except Exception as e:
            print(f"⚠️ 获取余额失败: {e}")
            return {}
    
    def close(self):
        """关闭连接"""
        if self.exchange:
            self.exchange.close()
