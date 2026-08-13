"""
挂双单做市商策略 - 基于碧树西风核心思想

操作逻辑：
1. 同时挂买单和卖单（双边挂单）
2. 买入价格 = 买一价 × 0.999（下方0.1%）
3. 卖出价格 = 卖一价 × 1.001（上方0.1%）
4. 净利润 = 价差 - 手续费×2
5. 必须净利 > 0.1% 才执行

风险管理（定死规则）：
- 单笔止损 ≤ 2%本金
- 单品种仓位 ≤ 20%本金
- 连续亏损5次暂停
- 盈利取出50%永不回流
"""

from typing import Dict, List, Optional, Tuple
import ccxt
import time
import logging
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# 定死规则（不可更改）
RULES = {
    'min_profit_pct': 0.001,        # 只挂净利 > 0.1% 的品种
    'max_position_pct': 0.20,       # 单笔最大仓位 ≤ 总资金 20%
    'stop_loss_pct': 0.02,          # 单笔止损 ≤ 总资金 2%
    'max_consecutive_losses': 5,    # 连续亏损 5 次停止交易
    'profit_withdraw_pct': 0.50,    # 盈利取出 50% 永不回市场
    'buy_offset': 0.001,            # 买单偏移：买一价 × (1 - 0.001)
    'sell_offset': 0.001,           # 卖单偏移：卖一价 × (1 + 0.001)
}


@dataclass
class OrderBookSnapshot:
    """订单簿快照"""
    symbol: str
    timestamp: float
    bid_price: float
    ask_price: float
    bid_size: float
    ask_size: float
    spread: float
    spread_pct: float
    
    @property
    def mid_price(self) -> float:
        return (self.bid_price + self.ask_price) / 2


@dataclass
class MakerSignal:
    """做市信号"""
    symbol: str
    timestamp: datetime
    buy_price: float
    sell_price: float
    expected_profit_pct: float
    is_profitable: bool
    reason: str


class MakerStrategy:
    """挂双单做市商策略"""
    
    def __init__(self, exchange: ccxt.Exchange, symbol: str = 'BTC/USDT'):
        self.exchange = exchange
        self.symbol = symbol
        self.consecutive_losses = 0
        self.total_trades = 0
        self.profitable_trades = 0
        self.total_profit = 0.0
        
        logger.info(f"做市策略初始化: {symbol}")
    
    def fetch_orderbook(self, limit: int = 5) -> Optional[OrderBookSnapshot]:
        """获取订单簿快照"""
        try:
            ob = self.exchange.fetch_order_book(self.symbol, limit)
            
            if not ob['bids'] or not ob['asks']:
                logger.warning(f"订单簿为空: {self.symbol}")
                return None
            
            bid = ob['bids'][0]
            ask = ob['asks'][0]
            
            bid_price = float(bid[0])
            ask_price = float(ask[0])
            bid_size = float(bid[1])
            ask_size = float(ask[1])
            
            spread = ask_price - bid_price
            spread_pct = spread / bid_price if bid_price > 0 else 0
            
            return OrderBookSnapshot(
                symbol=self.symbol,
                timestamp=time.time(),
                bid_price=bid_price,
                ask_price=ask_price,
                bid_size=bid_size,
                ask_size=ask_size,
                spread=spread,
                spread_pct=spread_pct
            )
        except Exception as e:
            logger.error(f"获取订单簿失败: {e}")
            return None
    
    def calculate_maker_prices(self, ob: OrderBookSnapshot) -> Tuple[float, float, float]:
        """
        计算做市价格
        
        Returns:
            (buy_price, sell_price, expected_profit_pct)
        """
        # 买单价格 = 买一价下方 0.1%
        buy_price = ob.bid_price * (1 - RULES['buy_offset'])
        
        # 卖单价格 = 卖一价上方 0.1%
        sell_price = ob.ask_price * (1 + RULES['sell_offset'])
        
        # 理论价差
        spread = sell_price - buy_price
        
        # 估算手续费（Bitget maker约0.06%）
        fee_rate = 0.0006
        expected_profit = spread - (buy_price * fee_rate + sell_price * fee_rate)
        expected_profit_pct = expected_profit / buy_price if buy_price > 0 else 0
        
        return buy_price, sell_price, expected_profit_pct
    
    def generate_signal(self) -> Optional[MakerSignal]:
        """
        生成做市信号
        
        Returns:
            MakerSignal 或 None（不满足条件时）
        """
        ob = self.fetch_orderbook()
        if not ob:
            return None
        
        # 检查买卖深度是否充足
        if ob.bid_size < 0.1 or ob.ask_size < 0.1:
            logger.debug(f"深度不足: {self.symbol}")
            return None
        
        buy_price, sell_price, profit_pct = self.calculate_maker_prices(ob)
        
        # 检查是否满足利润要求
        is_profitable = profit_pct > RULES['min_profit_pct']
        
        signal = MakerSignal(
            symbol=self.symbol,
            timestamp=datetime.now(),
            buy_price=buy_price,
            sell_price=sell_price,
            expected_profit_pct=profit_pct,
            is_profitable=is_profitable,
            reason=self._generate_reason(ob, profit_pct, is_profitable)
        )
        
        return signal
    
    def _generate_reason(self, ob: OrderBookSnapshot, profit_pct: float, is_profitable: bool) -> str:
        """生成信号说明"""
        parts = []
        parts.append(f"买一={ob.bid_price:.2f}, 卖一={ob.ask_price:.2f}")
        parts.append(f"价差={ob.spread_pct:.4f}%")
        parts.append(f"预计净利={profit_pct:.4f}%")
        
        if is_profitable:
            parts.append("✅ 符合做市条件")
        else:
            parts.append("❌ 净利不足或为负")
        
        return " | ".join(parts)
    
    def should_place_orders(self, signal: MakerSignal) -> bool:
        """
        判断是否应该挂单
        
        定死规则检查：
        1. 净利必须 > 0.1%
        2. 不能连续亏损超过5次
        """
        if not signal.is_profitable:
            logger.debug(f"{signal.symbol}: 净利不足，跳过")
            return False
        
        if self.consecutive_losses >= RULES['max_consecutive_losses']:
            logger.warning(f"{signal.symbol}: 连续亏损{self.consecutive_losses}次，暂停交易")
            return False
        
        return True
    
    def execute_maker_orders(self, signal: MakerSignal, position_pct: float = 0.05) -> Dict:
        """
        执行双边挂单
        
        Args:
            signal: 做市信号
            position_pct: 仓位比例（默认5%）
        
        Returns:
            执行结果
        """
        result = {
            'symbol': signal.symbol,
            'timestamp': signal.timestamp.isoformat(),
            'buy_order': None,
            'sell_order': None,
            'status': 'pending'
        }
        
        try:
            # 获取账户余额
            balance = self.exchange.fetch_balance()
            usdt = balance['USDT']['total']
            
            # 计算下单金额（取5%或可用余额的较小值）
            position_size = min(usdt * position_pct, usdt * 0.95)
            
            # 计算下单数量
            buy_amount = position_size / signal.buy_price
            sell_amount = position_size / signal.sell_price
            
            # 挂买单（下方0.1%）
            buy_order = self.exchange.create_limit_buy_order(
                signal.symbol,
                buy_amount,
                signal.buy_price
            )
            result['buy_order'] = buy_order
            
            # 挂卖单（上方0.1%）
            sell_order = self.exchange.create_limit_sell_order(
                signal.symbol,
                sell_amount,
                signal.sell_price
            )
            result['sell_order'] = sell_order
            
            result['status'] = 'placed'
            result['expected_profit_usdt'] = position_size * signal.expected_profit_pct
            
            logger.info(f"挂单成功: {signal.symbol} 买@{signal.buy_price:.2f} 卖@{signal.sell_price:.2f}")
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"挂单失败: {e}")
        
        return result
    
    def update_stats(self, profit: float = 0, is_loss: bool = False):
        """更新统计"""
        self.total_trades += 1
        self.total_profit += profit
        
        if is_loss:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = max(0, self.consecutive_losses - 1)
            self.profitable_trades += 1
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'symbol': self.symbol,
            'total_trades': self.total_trades,
            'profitable_trades': self.profitable_trades,
            'win_rate': self.profitable_trades / max(self.total_trades, 1),
            'consecutive_losses': self.consecutive_losses,
            'total_profit': self.total_profit,
            'rules': RULES,
            'is_paused': self.consecutive_losses >= RULES['max_consecutive_losses']
        }


class MultiSymbolMakerStrategy:
    """多币种做市策略管理器"""
    
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange
        self.strategies: Dict[str, MakerStrategy] = {}
        self.default_symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT']
        
        for symbol in self.default_symbols:
            self.strategies[symbol] = MakerStrategy(exchange, symbol)
    
    def scan_all(self) -> List[MakerSignal]:
        """扫描所有币种"""
        signals = []
        for symbol, strategy in self.strategies.items():
            signal = strategy.generate_signal()
            if signal:
                signals.append(signal)
            time.sleep(0.5)  # 避免频率限制
        return signals
    
    def execute_best_opportunities(self, top_n: int = 3) -> List[Dict]:
        """执行最佳机会"""
        signals = self.scan_all()
        profitable = [s for s in signals if s.is_profitable]
        
        # 按预期利润排序
        profitable.sort(key=lambda x: x.expected_profit_pct, reverse=True)
        
        results = []
        for signal in profitable[:top_n]:
            strategy = self.strategies[signal.symbol]
            if strategy.should_place_orders(signal):
                result = strategy.execute_maker_orders(signal)
                results.append(result)
        
        return results
    
    def get_all_stats(self) -> Dict:
        """获取所有统计"""
        return {symbol: s.get_stats() for symbol, s in self.strategies.items()}


if __name__ == '__main__':
    # 测试运行
    import os
    
    api_key = os.getenv('BITGET_API_KEY')
    api_secret = os.getenv('BITGET_API_SECRET')
    api_passphrase = os.getenv('BITGET_API_PASSPHRASE', 'qntsomtop')
    
    if not api_key or not api_secret:
        print("❌ API密钥未配置")
        exit(1)
    
    exchange = ccxt.bitget({
        'apiKey': api_key,
        'secret': api_secret,
        'password': api_passphrase,
        'enableRateLimit': True,
    })
    
    print("=" * 60)
    print("  挂双单做市商策略测试")
    print("=" * 60)
    
    manager = MultiSymbolMakerStrategy(exchange)
    
    # 扫描所有币种
    print("\n🔍 扫描中...")
    signals = manager.scan_all()
    
    print(f"\n📊 发现 {len(signals)} 个信号，其中 {sum(1 for s in signals if s.is_profitable)} 个符合做市条件\n")
    
    for signal in sorted(signals, key=lambda x: x.expected_profit_pct, reverse=True):
        icon = "✅" if signal.is_profitable else "❌"
        print(f"  {icon} {signal.symbol}")
        print(f"     {signal.reason}")
        print()
    
    # 显示统计
    print("-" * 60)
    print("📈 统计:")
    stats = manager.get_all_stats()
    for symbol, s in stats.items():
        status = "⏸️ 暂停" if s['is_paused'] else "✅ 正常"
        print(f"  {symbol}: {s['total_trades']}笔交易, 胜率{s['win_rate']:.1%}, {status}")
    
    print("=" * 60)
