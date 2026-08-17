"""
记忆承载·碧树西风交易系统 - 风控模块
碧树西风标准：2%单笔/5%日亏/10%回撤/连续亏损冷却/熔断
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import ccxt


@dataclass
class TradeRecord:
    trade_id: str
    timestamp: float
    pnl: float
    symbol: str
    exchange: str


@dataclass
class RiskStatus:
    """风控状态"""
    daily_pnl: float = 0.0
    peak_equity: float = 0.0
    current_equity: float = 0.0
    consecutive_losses: int = 0
    is_circuit_breaker: bool = False
    circuit_breaker_until: Optional[datetime] = None
    last_loss_time: Optional[datetime] = None
    
    @property
    def daily_loss_pct(self) -> float:
        if self.peak_equity > 0:
            return abs(min(0, self.daily_pnl)) / self.peak_equity * 100
        return 0.0
    
    @property
    def drawdown_pct(self) -> float:
        if self.peak_equity > 0:
            return (self.peak_equity - self.current_equity) / self.peak_equity * 100
        return 0.0
    
    @property
    def is_trading_allowed(self) -> bool:
        """检查是否允许交易"""
        if self.is_circuit_breaker:
            if self.circuit_breaker_until and datetime.utcnow() < self.circuit_breaker_until:
                return False
            else:
                self.is_circuit_breaker = False
                self.circuit_breaker_until = None
        
        if self.daily_loss_pct >= 5.0:
            return False
        
        if self.consecutive_losses >= 5:
            return False
        
        if self.drawdown_pct >= 10.0:
            return False
        
        return True


class RiskManager:
    """风控模块"""
    
    def __init__(self, max_loss_per_trade_pct: float = 2.0,
                 max_daily_loss_pct: float = 5.0,
                 max_drawdown_pct: float = 10.0,
                 max_consecutive_losses: int = 5):
        self.max_loss_per_trade_pct = max_loss_per_trade_pct
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.max_consecutive_losses = max_consecutive_losses
        
        self.status = RiskStatus()
        self.daily_trades: List[TradeRecord] = []
        self.trade_history: List[TradeRecord] = []
    
    def check_before_trade(
        self, 
        position_size_usdt: float,
        initial_capital: float
    ) -> tuple:
        """交易前风控检查"""
        if not self.status.is_trading_allowed:
            return False, "Trading restricted by risk controls"
        
        max_position = initial_capital * self.max_loss_per_trade_pct / 100 * 10
        if position_size_usdt > max_position:
            return False, f"Position {position_size_usdt} exceeds max {max_position}"
        
        if self.status.daily_loss_pct >= self.max_daily_loss_pct:
            return False, f"Daily loss limit reached: {self.status.daily_loss_pct:.2f}%"
        
        if self.status.drawdown_pct >= self.max_drawdown_pct:
            return False, f"Drawdown limit reached: {self.status.drawdown_pct:.2f}%"
        
        return True, "OK"
    
    def record_trade(self, trade: TradeRecord):
        """记录交易结果"""
        self.daily_trades.append(trade)
        self.trade_history.append(trade)
        
        self.status.daily_pnl += trade.pnl
        
        if trade.pnl > 0:
            self.status.current_equity += trade.pnl
            self.status.peak_equity = max(
                self.status.peak_equity, 
                self.status.current_equity
            )
        
        if trade.pnl < 0:
            self.status.consecutive_losses += 1
            self.status.last_loss_time = datetime.utcnow()
            
            if self.status.consecutive_losses >= self.max_consecutive_losses:
                self.status.is_circuit_breaker = True
                self.status.circuit_breaker_until = datetime.utcnow() + timedelta(minutes=30)
        else:
            self.status.consecutive_losses = 0
    
    def reset_daily(self):
        """每日重置"""
        self.daily_trades.clear()
        self.status.daily_pnl = 0.0
    
    def get_status(self) -> dict:
        """获取风控状态"""
        return {
            "daily_pnl": self.status.daily_pnl,
            "daily_loss_pct": self.status.daily_loss_pct,
            "drawdown_pct": self.status.drawdown_pct,
            "consecutive_losses": self.status.consecutive_losses,
            "is_circuit_breaker": self.status.is_circuit_breaker,
            "is_trading_allowed": self.status.is_trading_allowed,
        }
