"""
风控管理器 - v4.0定死规则
"""
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger('RiskManager')

class RiskManager:
    """风控管理器 - 规则定死不可更改"""
    
    # ========== 风控铁律（v4方案） ==========
    MAX_POSITION_PCT = 0.20        # 单笔仓位 ≤ 总资金 20%
    MAX_STOP_LOSS_PCT = 0.02       # 单笔止损 ≤ 总资金 2%
    MAX_CONSECUTIVE_LOSSES = 5     # 连续亏损 5 次暂停
    MAX_DRAWDOWN_PCT = 0.40        # 最大回撤 40% 停止
    PROFIT_WITHDRAW_PCT = 0.50     # 盈利取出 50% 永不回流
    MIN_NET_PROFIT_PCT = 0.001     # 净利必须 > 0.1% 才执行
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        
        # 运行时状态
        self.consecutive_losses = 0
        self.max_drawdown = 0.0
        self.total_profit = 0.0
        self.daily_profit = 0.0
        self.is_suspended = False
        self.suspension_reason = ""
    
    def _init_db(self):
        """初始化风控表"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        # 初始化默认值
        defaults = {
            'consecutive_losses': '0',
            'peak_equity': '0',
            'current_equity': '1.0',
            'total_profit': '0.0',
            'daily_profit': '0.0',
            'max_drawdown': '0.0',
            'is_suspended': '0',
            'suspension_reason': '',
            'last_reset_date': datetime.now().strftime('%Y-%m-%d'),
        }
        for k, v in defaults.items():
            cursor.execute('''
                INSERT OR IGNORE INTO risk_state (key, value) VALUES (?, ?)
            ''', (k, v))
        self.conn.commit()
    
    def load_state(self):
        """加载风控状态"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT key, value FROM risk_state')
        for row in cursor.fetchall():
            if row[0] == 'consecutive_losses':
                self.consecutive_losses = int(row[1])
            elif row[0] == 'current_equity':
                self.total_profit = float(row[1]) - 1.0  # 假设初始本金1 USDT
            elif row[0] == 'max_drawdown':
                self.max_drawdown = float(row[1])
            elif row[0] == 'is_suspended':
                self.is_suspended = int(row[1]) == 1
            elif row[0] == 'suspension_reason':
                self.suspension_reason = row[1]
        
        # 检查是否需要重置每日计数
        cursor.execute('SELECT value FROM risk_state WHERE key="last_reset_date"')
        last_reset = cursor.fetchone()
        if last_reset:
            last_date = datetime.strptime(last_reset[0], '%Y-%m-%d').date()
            if last_date < datetime.now().date():
                self.daily_profit = 0.0
                cursor.execute('UPDATE risk_state SET value=? WHERE key="daily_profit"', 
                             ('0',))
                cursor.execute('UPDATE risk_state SET value=? WHERE key="last_reset_date"',
                             (datetime.now().strftime('%Y-%m-%d'),))
                self.conn.commit()
    
    def save_state(self):
        """保存风控状态"""
        cursor = self.conn.cursor()
        state = {
            'consecutive_losses': str(self.consecutive_losses),
            'current_equity': str(1.0 + self.total_profit),
            'max_drawdown': str(self.max_drawdown),
            'is_suspended': '1' if self.is_suspended else '0',
            'suspension_reason': self.suspension_reason,
        }
        for k, v in state.items():
            cursor.execute('UPDATE risk_state SET value=? WHERE key=?', (v, k))
        self.conn.commit()
    
    def check_risk(self, symbol: str, side: str, position_size_usdt: float, 
                   entry_price: float, stop_loss_price: float) -> Dict:
        """
        检查风控规则
        
        Returns:
            {
                'allowed': bool,
                'reason': str,
                'max_position_usdt': float,
                'suggested_stop_loss': float,
            }
        """
        result = {
            'allowed': True,
            'reason': '',
            'max_position_usdt': 0,
            'suggested_stop_loss': stop_loss_price,
        }
        
        # 计算当前权益
        equity = 1.0 + self.total_profit  # 假设初始本金1 USDT
        
        # Rule 1: 检查是否暂停
        if self.is_suspended:
            result['allowed'] = False
            result['reason'] = f"⛔ 暂停中: {self.suspension_reason}"
            return result
        
        # Rule 1: 单笔仓位 ≤ 总资金 20%
        max_position = equity * self.MAX_POSITION_PCT
        if position_size_usdt > max_position:
            result['allowed'] = False
            result['reason'] = f"⛔ 仓位超限: {position_size_usdt:.2f}U > {max_position:.2f}U (20%)"
            result['max_position_usdt'] = max_position
            return result
        
        # Rule 2: 单笔止损 ≤ 总资金 2%
        stop_loss_distance = abs(entry_price - stop_loss_price) / entry_price
        max_stop_loss_cost = equity * self.MAX_STOP_LOSS_PCT
        max_stop_loss_distance = max_stop_loss_cost / position_size_usdt if position_size_usdt > 0 else 999
        
        if stop_loss_distance > max_stop_loss_distance:
            result['allowed'] = False
            result['reason'] = f"⛔ 止损距离过大: {stop_loss_distance:.2%} > {max_stop_loss_distance:.2%}"
            return result
        
        # Rule 4: 最大回撤 40%
        if equity < 0.6:  # 从峰值回撤超过40%
            self.is_suspended = True
            self.suspension_reason = "最大回撤40%，强制停止"
            self.save_state()
            result['allowed'] = False
            result['reason'] = "⛔ 最大回撤40%，系统暂停"
            return result
        
        # Rule 6: 净利必须 > 0.1%
        # 这需要在实际交易时检查预期利润
        
        result['max_position_usdt'] = max_position
        result['suggested_stop_loss'] = stop_loss_price
        return result
    
    def record_trade(self, pnl: float, is_win: bool):
        """记录交易结果"""
        self.total_profit += pnl
        self.daily_profit += pnl
        
        # 更新回撤
        peak = max(0, self.total_profit)
        if self.total_profit < 0:
            current_dd = abs(self.total_profit) / (1.0 + peak) if peak > 0 else 0
            self.max_drawdown = max(self.max_drawdown, current_dd)
        
        # 更新连续亏损
        if is_win:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            
            # Rule 3: 连续亏损 5 次暂停
            if self.consecutive_losses >= self.MAX_CONSECUTIVE_LOSSES:
                self.is_suspended = True
                self.suspension_reason = f"连续亏损{self.MAX_CONSECUTIVE_LOSSES}次"
        
        # Rule 5: 盈利取出 50%（简化版：记录到日志）
        if pnl > 0 and self.total_profit > 0:
            withdraw = pnl * self.PROFIT_WITHDRAW_PCT
            logger.info(f"💰 盈利取出: {withdraw:.4f}U (永不回流)")
        
        self.save_state()
    
    def get_status(self) -> Dict:
        """获取风控状态"""
        equity = 1.0 + self.total_profit
        return {
            'equity': equity,
            'total_profit': self.total_profit,
            'daily_profit': self.daily_profit,
            'consecutive_losses': self.consecutive_losses,
            'max_drawdown': self.max_drawdown,
            'is_suspended': self.is_suspended,
            'suspension_reason': self.suspension_reason,
            'max_position_usdt': equity * self.MAX_POSITION_PCT,
        }
    
    def close(self):
        self.conn.close()
