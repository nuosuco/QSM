"""
QNT量子交易系统 - 捡乌龙指策略
基于碧树西风核心思想

捡乌龙指的核心逻辑：
1. 必须有两个以上的交易点（厅）可以交易同一品种
2. A厅价格异常（如跌停），B厅价格正常
3. 在A厅买入异常价格，同时在B厅卖出正常价格
4. 瞬间锁定利润，不持仓等待价格恢复

关键区别：
- 捡乌龙指 ≠ 网格交易/做市策略
- 捡乌龙指需要参考系（至少两个交易点）
- 做市策略是单边挂单，赚买卖价差
- 捡乌龙指是对冲操作，天然无风险
"""

from typing import Dict, List, Optional, Tuple
import ccxt
import time
import logging
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HallPrice:
    """某个'厅'的价格数据"""
    name: str           # 厅名称（现货厅、合约厅等）
    symbol: str         # 交易品种
    bid: float          # 买一价
    ask: float          # 卖一价
    last: float         # 最新价
    timestamp: float    # 时间戳


@dataclass
class OolongIndexSignal:
    """乌龙指信号"""
    symbol: str
    timestamp: datetime
    abnormal_hall: HallPrice      # 异常价格厅
    normal_hall: HallPrice        # 正常价格厅
    spread_pct: float             # 价差百分比
    action: str                   # 操作方向：buy_abnormal_sell_normal 或 sell_abnormal_buy_normal
    estimated_profit_pct: float   # 预估净利润（扣除手续费）
    is_opportunity: bool          # 是否构成机会


class OolongIndexStrategy:
    """
    捡乌龙指策略
    
    核心原理：
    同一个品种在同一个平台的不同'厅'（现货、合约、期货等）交易。
    如果A厅价格异常（如跌停），B厅价格正常，则可以在A厅买入、B厅卖出，
    瞬间锁定利润，不需要等待价格恢复。
    
    关键：必须有参考系！只有一个交易点就不是乌龙指。
    """
    
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange
        self.spread_threshold = 0.02  # 价差超过2%才认为是乌龙指
        self.fee_rate = 0.0006  # 手续费率（Bitget约0.06%）
        
        logger.info("捡乌龙指策略初始化完成")
    
    def get_hall_prices(self, base_symbol: str) -> Dict[str, HallPrice]:
        """
        获取同一品种在不同'厅'的价格
        
        Args:
            base_symbol: 基础品种，如 'BTC/USDT'
        
        Returns:
            {'现货厅': HallPrice, '永续合约厅': HallPrice, ...}
        """
        halls = {}
        
        # 解析基础品种
        parts = base_symbol.split('/')
        if len(parts) != 2:
            return halls
        
        coin, quote = parts
        
        # 构建不同'厅'的交易对
        hall_symbols = {
            '现货厅': f"{coin}/{quote}",
            '永续合约厅': f"{coin}/{quote}:{quote}",
        }
        
        for name, sym in hall_symbols.items():
            try:
                ticker = self.exchange.fetch_ticker(sym)
                halls[name] = HallPrice(
                    name=name,
                    symbol=sym,
                    bid=ticker['bid'],
                    ask=ticker['ask'],
                    last=ticker['last'],
                    timestamp=time.time()
                )
                time.sleep(0.2)  # 避免频率限制
            except Exception as e:
                logger.debug(f"{name} ({sym}) 获取失败: {e}")
        
        return halls
    
    def detect_oolong_index(self, base_symbol: str) -> Optional[OolongIndexSignal]:
        """
        检测乌龙指机会
        
        判断标准：
        1. 同一品种至少有两个'厅'可以交易
        2. A厅价格异常偏离B厅（超过阈值）
        3. 可以在A厅买入、B厅卖出（或反之）锁定利润
        """
        halls = self.get_hall_prices(base_symbol)
        
        if len(halls) < 2:
            return None
        
        hall_names = list(halls.keys())
        
        # 检查所有可能的配对
        for i in range(len(hall_names)):
            for j in range(i + 1, len(hall_names)):
                hall_a = halls[hall_names[i]]
                hall_b = halls[hall_names[j]]
                
                # 计算价差（以买一价为基准）
                spread_ab = (hall_a.bid - hall_b.ask) / hall_b.ask * 100
                spread_ba = (hall_b.bid - hall_a.ask) / hall_a.ask * 100
                
                # 检测异常情况
                opportunities = []
                
                # 情况1：A厅价格暴跌（有人敲错价格卖出）
                # 在A厅买入 @ ask，在B厅卖出 @ bid
                if hall_a.ask < hall_b.bid * (1 - self.spread_threshold / 100):
                    profit_pct = (hall_b.bid - hall_a.ask) / hall_a.ask * 100
                    net_profit = profit_pct - (self.fee_rate * 100 * 2)
                    opportunities.append({
                        'abnormal': hall_a,
                        'normal': hall_b,
                        'action': 'buy_abnormal_sell_normal',
                        'profit_pct': net_profit
                    })
                
                # 情况2：A厅价格暴涨（有人敲错价格买入）
                # 在A厅卖出 @ bid，在B厅买入 @ ask
                if hall_a.bid > hall_b.ask * (1 + self.spread_threshold / 100):
                    profit_pct = (hall_a.bid - hall_b.ask) / hall_b.ask * 100
                    net_profit = profit_pct - (self.fee_rate * 100 * 2)
                    opportunities.append({
                        'abnormal': hall_a,
                        'normal': hall_b,
                        'action': 'sell_abnormal_buy_normal',
                        'profit_pct': net_profit
                    })
                
                # 如果有机会，返回信号
                for opp in opportunities:
                    if opp['profit_pct'] > 0:
                        return OolongIndexSignal(
                            symbol=base_symbol,
                            timestamp=datetime.now(),
                            abnormal_hall=opp['abnormal'],
                            normal_hall=opp['normal'],
                            spread_pct=opp['profit_pct'],
                            action=opp['action'],
                            estimated_profit_pct=opp['profit_pct'],
                            is_opportunity=True
                        )
        
        return None
    
    def scan_all_symbols(self, symbols: List[str]) -> List[OolongIndexSignal]:
        """扫描所有品种的乌龙指机会"""
        signals = []
        
        for symbol in symbols:
            try:
                signal = self.detect_oolong_index(symbol)
                if signal:
                    signals.append(signal)
                time.sleep(0.5)
            except Exception as e:
                logger.debug(f"扫描 {symbol} 失败: {e}")
        
        return signals
    
    def generate_report(self, signal: OolongIndexSignal) -> str:
        """生成操作报告"""
        lines = [
            "=" * 70,
            "  🎯 发现乌龙指机会！",
            "=" * 70,
            "",
            f"品种: {signal.symbol}",
            f"时间: {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "异常价格厅:",
            f"  名称: {signal.abnormal_hall.name}",
            f"  交易对: {signal.abnormal_hall.symbol}",
            f"  买一: ${signal.abnormal_hall.bid:,.2f}",
            f"  卖一: ${signal.abnormal_hall.ask:,.2f}",
            "",
            "正常价格厅:",
            f"  名称: {signal.normal_hall.name}",
            f"  交易对: {signal.normal_hall.symbol}",
            f"  买一: ${signal.normal_hall.bid:,.2f}",
            f"  卖一: ${signal.normal_hall.ask:,.2f}",
            "",
            "操作方案:",
        ]
        
        if signal.action == 'buy_abnormal_sell_normal':
            lines.extend([
                f"  1. 在【{signal.abnormal_hall.name}】买入 @ ${signal.abnormal_hall.ask:,.2f}",
                f"  2. 同时在【{signal.normal_hall.name}】卖出 @ ${signal.normal_hall.bid:,.2f}",
                f"",
                f"  锁定利润: ${signal.normal_hall.bid - signal.abnormal_hall.ask:,.2f}",
                f"  利润率: {signal.spread_pct:.2f}%",
            ])
        else:
            lines.extend([
                f"  1. 在【{signal.abnormal_hall.name}】卖出 @ ${signal.abnormal_hall.bid:,.2f}",
                f"  2. 同时在【{signal.normal_hall.name}】买入 @ ${signal.normal_hall.ask:,.2f}",
                f"",
                f"  锁定利润: ${signal.abnormal_hall.bid - signal.normal_hall.ask:,.2f}",
                f"  利润率: {signal.spread_pct:.2f}%",
            ])
        
        lines.extend([
            "",
            "核心原则:",
            "  ✅ 不需要等待价格恢复",
            "  ✅ 瞬间锁定利润",
            "  ✅ 天然对冲，无风险",
            "",
            "关键条件:",
            f"  ✅ 至少有2个'厅'可交易同一品种",
            f"  ✅ 价差超过阈值（{self.spread_threshold*100:.0f}%）",
            "=" * 70,
        ])
        
        return "\n".join(lines)


if __name__ == '__main__':
    import os
    
    api_key = os.getenv('BITGET_API_KEY')
    api_secret = os.getenv('BITGET_API_SECRET')
    api_passphrase = os.getenv('BITGET_API_PASSPHRASE')
    
    if not api_key or not api_secret:
        print("❌ API密钥未配置")
        exit(1)
    
    exchange = ccxt.bitget({
        'apiKey': api_key,
        'secret': api_secret,
        'password': api_passphrase,
        'enableRateLimit': True,
    })
    
    print("=" * 70)
    print("  QNT量子交易系统 - 捡乌龙指策略")
    print("=" * 70)
    
    strategy = OolongIndexStrategy(exchange)
    
    # 扫描主流品种
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT']
    
    print(f"\n🔍 扫描 {len(symbols)} 个品种的异常价差...")
    print()
    
    signals = strategy.scan_all_symbols(symbols)
    
    if signals:
        print(f"\n🎯 发现 {len(signals)} 个乌龙指机会！\n")
        for signal in signals:
            print(strategy.generate_report(signal))
            print()
    else:
        print("✅ 当前没有发现异常价差")
        print("\n💡 提示：乌龙指是小概率事件，需要耐心等待")
        print("   或者尝试交投冷清、研究人少的品种")
        
        # 显示正常价差
        print("\n📊 当前各品种价差状态:")
        for sym in symbols:
            halls = strategy.get_hall_prices(sym)
            if len(halls) >= 2:
                names = list(halls.keys())
                hall_a = halls[names[0]]
                hall_b = halls[names[1]]
                spread = (hall_a.bid - hall_b.ask) / hall_b.ask * 100
                print(f"  {sym}: {names[0]}买${hall_a.bid:,.2f} vs {names[1]}卖${hall_b.ask:,.2f} = {spread:.3f}%")
    
    print("\n" + "=" * 70)
