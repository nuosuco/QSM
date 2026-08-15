"""
记忆承载·碧树西风交易系统 - 回测引擎
模拟历史数据验证策略
"""
import numpy as np
import random
import time
from typing import List, Optional, Dict
from datetime import datetime

from .config import BacktestConfig
from .models import (BacktestResult, Trade, OrderSide, FatFingerSignal,
                     SignalType, OrderBook, OrderBookEntry)


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.result = BacktestResult()
        self._reset()
    
    def _reset(self):
        """重置状态"""
        self.equity = self.config.initial_capital
        self.peak_equity = self.config.initial_capital
        self.consecutive_losses = 0
        self.prices: List[float] = []
        self.trades: List[Trade] = []
        self.signals: List[FatFingerSignal] = []
    
    def run(self) -> BacktestResult:
        """运行回测"""
        self._reset()
        
        # 生成模拟价格数据
        price_history = self._generate_price_data()
        
        # 模拟检测乌龙指
        for i, price in enumerate(price_history):
            self.prices.append(price)
            
            # 每个tick有概率触发乌龙指
            if random.random() < self.config.fat_finger_probability:
                signal = self._simulate_fat_finger(price, i)
                if signal:
                    self.signals.append(signal)
                    
                    # 执行交易
                    trade = self._execute_signal(signal)
                    if trade:
                        self.trades.append(trade)
        
        # 计算结果
        self._calculate_results()
        return self.result
    
    def _generate_price_data(self) -> List[float]:
        """生成模拟价格数据"""
        base_price = 50000.0
        prices = [base_price]
        
        for i in range(1, self.config.duration_days * self.config.ticks_per_day):
            change = random.gauss(0, self.config.volatility_daily / 100 * base_price / np.sqrt(self.config.ticks_per_day))
            new_price = max(prices[-1] + change, base_price * 0.5)
            prices.append(new_price)
        
        return prices
    
    def _simulate_fat_finger(
        self, 
        price: float, 
        tick_index: int
    ) -> Optional[FatFingerSignal]:
        """模拟乌龙指信号 - 买盘异常（价格被敲低）"""
        deviation = random.uniform(
            self.config.fat_finger_deviation_range[0],
            self.config.fat_finger_deviation_range[1]
        )
        
        # 乌龙指：买盘价格异常低（有人敲错单买入）
        signal_price = price * (1 - deviation / 100)
        
        return FatFingerSignal(
            signal_type=SignalType.SINGLE_EXCHANGE,
            symbol="BTC/USDT",
            exchange="bitget",
            price=signal_price,
            fair_price=price,
            deviation_pct=deviation,
            signal_strength=min(deviation / 10, 1.0),
            timestamp=time.time(),
            depth_available=10000.0,
            target_side=OrderSide.BUY,
        )
    
    def _execute_signal(self, signal: FatFingerSignal) -> Optional[Trade]:
        """执行信号 - 捡乌龙指套利"""
        # 买入异常价 + 立即卖出正常价
        buy_price = signal.price
        sell_price = signal.fair_price
        
        # 手续费（双边）
        fee_rate = 0.0006  # 0.06% per side
        slippage = 0.0002  # 0.02% slippage
        
        # 实际成交价
        actual_buy = buy_price * (1 + slippage)
        actual_sell = sell_price * (1 - slippage)
        
        # 仓位大小（用10%资金）
        position_pct = 0.1
        cost = self.equity * position_pct
        amount = cost / actual_buy
        buy_fee = cost * fee_rate
        sell_amount = amount * actual_sell
        sell_fee = sell_amount * fee_rate
        
        # 净利润
        net_profit = sell_amount - cost - buy_fee - sell_fee
        pnl_pct = net_profit / cost * 100
        
        # 记录交易
        trade = Trade(
            id=f"bt_{len(self.trades)}",
            exchange="bitget",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            price=actual_buy,
            amount=amount,
            cost=cost,
            fee=buy_fee + sell_fee,
            timestamp=signal.timestamp,
            pnl=net_profit
        )
        
        # 更新权益
        self.equity += net_profit
        self.peak_equity = max(self.peak_equity, self.equity)
        
        # 更新连续亏损计数
        if net_profit < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        return trade
    
    def _calculate_results(self):
        """计算回测结果"""
        self.result.initial_capital = self.config.initial_capital
        self.result.final_equity = self.equity
        self.result.total_return_pct = (self.equity - self.config.initial_capital) / self.config.initial_capital * 100
        self.result.total_trades = len(self.trades)
        
        wins = [t for t in self.trades if t.pnl > 0]
        losses = [t for t in self.trades if t.pnl <= 0]
        
        self.result.winning_trades = len(wins)
        self.result.losing_trades = len(losses)
        self.result.win_rate = len(wins) / len(self.trades) if self.trades else 0
        
        # 计算最大回撤
        equity_curve = [self.config.initial_capital]
        peak = self.config.initial_capital
        for trade in self.trades:
            peak = max(peak, equity_curve[-1] + trade.pnl)
            equity_curve.append(peak)
        
        max_dd = 0
        for i in range(1, len(equity_curve)):
            dd = (equity_curve[i-1] - equity_curve[i]) / equity_curve[i-1] * 100 if equity_curve[i-1] > 0 else 0
            max_dd = max(max_dd, dd)
        
        self.result.max_drawdown_pct = max_dd
        self.result.max_consecutive_losses = self.consecutive_losses
        
        # 碧树西风检验
        max_loss = min((t.pnl / self.config.initial_capital * 100) for t in losses) if losses else 0
        max_gain = max((t.pnl / self.config.initial_capital * 100) for t in wins) if wins else 0
        
        self.result.bishu_max_loss_pct = abs(max_loss)
        self.result.bishu_max_gain_pct = max_gain
        self.result.bishu_downward_limited = abs(max_loss) <= 10
        self.result.bishu_upward_unlimited = max_gain > 50
        self.result.bishu_fat_tail = len(wins) > len(losses) and max_gain > abs(max_loss) * 2
        
        self.result.trades = self.trades
        self.result.equity_curve = equity_curve
        self.result.total_signals = len(self.signals)
        self.result.executed_signals = len(self.trades)
