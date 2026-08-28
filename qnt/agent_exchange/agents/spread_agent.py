"""
价差套利Agent - 继承BaseAgent
"""
import logging
import os
import ccxt
from .base_agent import BaseAgent
from ..models import TickerSnapshot, TradeSignal
from ..strategies.spread import SpreadStrategy

logger = logging.getLogger(__name__)

# 交易所API配置
EXCHANGE_CONFIG = {
    'Bitget': {
        'cls': ccxt.bitget,
        'kwargs': {
            'apiKey': os.getenv('BITGET_API_KEY', ''),
            'secret': os.getenv('BITGET_API_SECRET', ''),
            'password': os.getenv('BITGET_API_PASSPHRASE', ''),
            'enableRateLimit': True
        }
    },
    'HTX': {
        'cls': ccxt.htx,
        'kwargs': {
            'apiKey': os.getenv('HTX_API_KEY', ''),
            'secret': os.getenv('HTX_API_SECRET', ''),
            'enableRateLimit': True
        }
    },
    'Gate.io': {
        'cls': ccxt.gate,
        'kwargs': {
            'apiKey': os.getenv('GATE_API_KEY', ''),
            'secret': os.getenv('GATE_API_SECRET', ''),
            'enableRateLimit': True
        }
    }
}

SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT']


class SpreadArbitrageAgent(BaseAgent):
    """价差套利Agent - 单币种单交易所"""

    def __init__(self, exchange_name: str, symbol: str):
        strategy = SpreadStrategy()
        super().__init__(exchange_name, symbol, strategy)

    def _connect(self) -> ccxt.Exchange:
        cfg = EXCHANGE_CONFIG.get(self.exchange_name)
        if not cfg:
            raise ValueError(f"不支持的交易所: {self.exchange_name}")
        return cfg['cls'](cfg['kwargs'])

    async def execute(self, signal: TradeSignal) -> bool:
        """执行价差套利"""
        logger.info(
            f"🔔 [{self.exchange_name}] {signal.strategy}信号: "
            f"{signal.side} @ ${signal.price:.4f} "
            f"预期净利 {signal.expected_profit_pct*100:.4f}%"
        )
        # TODO: 接入实际下单逻辑
        return True
