"""
Agent基类 - 每个交易所的Agent
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional
import ccxt

from ..models import TickerSnapshot, TradeSignal, ChannelState
from ..strategies.base import BaseStrategy

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """交易所Agent基类"""

    def __init__(self, exchange_name: str, symbol: str, strategy: BaseStrategy):
        self.exchange_name = exchange_name
        self.symbol = symbol
        self.strategy = strategy
        self.state = ChannelState(exchange=exchange_name)
        self._ex: Optional[ccxt.Exchange] = None
        self._running = False

    @abstractmethod
    def _connect(self) -> ccxt.Exchange:
        """连接交易所"""
        pass

    async def start(self):
        """启动Agent"""
        self._ex = self._connect()
        self._running = True
        logger.info(f"🤖 {self.exchange_name} Agent启动 ({self.symbol})")

    async def stop(self):
        """停止Agent"""
        self._running = False
        if self._ex:
            try:
                self._ex.close()
            except:
                pass

    async def scan_once(self) -> Optional[TradeSignal]:
        """扫描一次市场，返回交易信号"""
        try:
            snap = await self._fetch_ticker()
            if not snap:
                self.state.errors += 1
                return None

            self.state.tickers[self.symbol] = snap
            self.state.last_update = snap.timestamp

            signal = self.strategy.evaluate(snap)
            return signal

        except Exception as e:
            self.state.errors += 1
            logger.debug(f"{self.exchange_name} 扫描异常: {e}")
            return None

    async def _fetch_ticker(self) -> Optional[TickerSnapshot]:
        """获取价格快照"""
        try:
            spot_sym = self.symbol.replace(':USDT', '')
            spot_price = self._ex.fetch_ticker(f"{spot_sym}/USDT")
            perp_price = self._ex.fetch_ticker(f"{spot_sym}/USDT:USDT")

            return TickerSnapshot(
                exchange=self.exchange_name,
                symbol=self.symbol,
                bid=spot_price.get('bid', 0),
                ask=spot_price.get('ask', 0),
                spot_bid=spot_price.get('bid', 0),
                spot_ask=spot_price.get('ask', 0),
                perp_bid=perp_price.get('bid', 0),
                perp_ask=perp_price.get('ask', 0),
                timestamp=spot_price.get('timestamp', 0) / 1000
            )
        except Exception as e:
            logger.debug(f"{self.exchange_name} 获取行情失败: {e}")
            return None

    async def execute(self, signal: TradeSignal) -> bool:
        """执行交易"""
        logger.info(f"📊 {self.exchange_name} 信号: {signal.side} {signal.symbol} @ ${signal.price:.4f}")
        return True
