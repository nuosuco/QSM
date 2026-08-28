"""
风控Agent - 全局风控监控
"""
import logging
import json
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

STATE_FILE = "/root/SOM/qnt/agent_exchange/risk_state.json"


class RiskAgent:
    """
    风控Agent - 全局风险管控
    检查：连续亏损、单日亏损、仓位集中度
    """

    MAX_CONSECUTIVE_LOSSES = 5
    MAX_DAILY_LOSS_PCT = 5.0  # 单日最大亏损5%
    MAX_POSITION_PCT = 20.0   # 单币种最大20%

    def __init__(self, initial_balance: float = 0.0):
        self.balance = initial_balance
        self.peak_balance = initial_balance
        self.consecutive_losses = 0
        self.daily_pnl = 0.0
        self.trades: List[dict] = []
        self._load_state()

    def _load_state(self):
        p = Path(STATE_FILE)
        if p.exists():
            try:
                with open(p) as f:
                    d = json.load(f)
                self.balance = d.get('balance', 0)
                self.peak_balance = d.get('peak_balance', 0)
                self.consecutive_losses = d.get('consecutive_losses', 0)
                self.trades = d.get('trades', [])
            except:
                pass

    def _save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump({
                'balance': self.balance,
                'peak_balance': self.peak_balance,
                'consecutive_losses': self.consecutive_losses,
                'trades': self.trades[-100:]  # 保留最近100条
            }, f, indent=2)

    def check_risk(self, signal_profit_pct: float) -> tuple[bool, str]:
        """
        检查风控
        返回: (是否允许交易, 原因)
        """
        # 连续亏损检查
        if self.consecutive_losses >= self.MAX_CONSECUTIVE_LOSSES:
            return False, f"连续亏损{self.consecutive_losses}次，暂停交易"

        # 单日亏损检查
        if self.daily_pnl <= -self.MAX_DAILY_LOSS_PCT:
            return False, f"单日亏损{self.daily_pnl:.1f}%，达到止损线"

        # 回撤检查
        if self.peak_balance > 0:
            drawdown = (self.peak_balance - self.balance) / self.peak_balance * 100
            if drawdown >= 40:
                return False, f"回撤{drawdown:.1f}%，超过40%上限"

        return True, "风控通过"

    def record_trade(self, profit_pct: float, pnl: float):
        """记录交易结果"""
        self.trades.append({
            'pnl_pct': profit_pct,
            'pnl': pnl,
            'timestamp': __import__('time').time()
        })
        self.balance += pnl
        self.daily_pnl += profit_pct

        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        if self.balance > self.peak_balance:
            self.peak_balance = self.balance

        self._save_state()
