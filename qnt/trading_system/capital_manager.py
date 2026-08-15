"""
记忆承载·碧树西风交易系统 - 资金管理模块
碧树西风标准：翻倍取本，利润分级提取
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CapitalState:
    """资金状态"""
    total_equity: float = 0.0
    initial_capital: float = 0.0
    withdrawn_profit: float = 0.0
    peak_equity: float = 0.0
    profit_tiers: dict = None
    
    def __post_init__(self):
        if self.profit_tiers is None:
            self.profit_tiers = {}
    
    @property
    def profit(self) -> float:
        return self.total_equity - self.initial_capital
    
    @property
    def profit_pct(self) -> float:
        if self.initial_capital > 0:
            return self.profit / self.initial_capital * 100
        return 0.0
    
    @property
    def is_doubled(self) -> bool:
        """本金是否已翻倍"""
        return self.total_equity >= self.initial_capital * 2
    
    @property
    def can_withdraw_principal(self) -> bool:
        """是否可以提取原始投入"""
        return self.is_doubled and self.initial_capital > 0
    
    def calculate_withdrawal(self, withdraw_pct: float = 20.0) -> float:
        """计算可提取金额"""
        if self.profit <= 0:
            return 0.0
        
        if self.can_withdraw_principal:
            return self.initial_capital
        
        tier_thresholds = [50, 100, 200, 500, 1000]
        for threshold in tier_thresholds:
            if self.profit_pct >= threshold:
                if threshold not in self.profit_tiers:
                    withdraw_amount = self.profit * (withdraw_pct / 100)
                    self.profit_tiers[threshold] = withdraw_amount
                    return withdraw_amount
        
        return 0.0
    
    def update(self, equity: float):
        """更新资金状态"""
        self.total_equity = equity
        self.peak_equity = max(self.peak_equity, equity)
    
    def reset(self, initial_capital: float):
        """重置资金状态"""
        self.total_equity = initial_capital
        self.initial_capital = initial_capital
        self.withdrawn_profit = 0.0
        self.peak_equity = initial_capital
        self.profit_tiers = {}


class CapitalManager:
    """资金管理模块"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.state = CapitalState(initial_capital=initial_capital)
        self.withdrawal_history = []
    
    def update_equity(self, equity: float):
        """更新当前权益"""
        self.state.update(equity)
    
    def check_withdrawal(self, withdraw_pct: float = 20.0) -> dict:
        """检查是否需要提现"""
        can_withdraw = self.state.can_withdraw_principal
        withdraw_amount = self.state.calculate_withdrawal(withdraw_pct)
        
        return {
            "can_withdraw": can_withdraw,
            "amount": withdraw_amount,
            "profit": self.state.profit,
            "profit_pct": self.state.profit_pct,
            "is_doubled": self.state.is_doubled,
        }
    
    def record_withdrawal(self, amount: float, reason: str):
        """记录提现"""
        import datetime
        self.state.withdrawn_profit += amount
        self.withdrawal_history.append({
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        })
    
    def get_position_size(self, max_pct: float = 10.0) -> float:
        """计算单笔最大仓位"""
        return self.state.total_equity * (max_pct / 100)
    
    def get_status(self) -> dict:
        """获取资金状态"""
        return {
            "total_equity": self.state.total_equity,
            "initial_capital": self.state.initial_capital,
            "profit": self.state.profit,
            "profit_pct": self.state.profit_pct,
            "withdrawn_profit": self.state.withdrawn_profit,
            "peak_equity": self.state.peak_equity,
            "is_doubled": self.state.is_doubled,
            "can_withdraw_principal": self.state.can_withdraw_principal,
            "max_position": self.get_position_size(),
        }
