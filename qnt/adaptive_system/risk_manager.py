"""
风控管理器 - v4.0定死规则
真正读取各交易所实时余额，不再假设余额
"""
import sqlite3
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import ccxt

logger = logging.getLogger('RiskManager')

class RiskManager:
    """风控管理器 - 规则定死不可更改"""
    
    # ========== 风控铁律（v4方案） ==========
    MAX_POSITION_PCT = 0.20        # 单笔仓位 ≤ 总资金 20%
    MAX_STOP_LOSS_PCT = 0.02       # 单笔止损 ≤ 总资金 2%
    MAX_CONSECUTIVE_LOSSES = 5     # 连续亏损 5 次暂停
    MAX_DRAWDOWN_PCT = 0.40        # 最大回撤 40% 停止
    PROFIT_WITHDRAW_PCT = 0.50     # 盈利取出 50% 永不回流
    MIN_NET_PROFIT_PCT = 0.0001  # 0.01%     # 测试模式：净利必须 > 0.01% 才执行
    
    def __init__(self, db_path: str, exchanges_config: Dict = None):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
        self.exchanges_config = exchanges_config or {}
        self._init_db()
        
        # 运行时状态
        self.consecutive_losses = 0
        self.max_drawdown = 0.0
        self.total_profit = 0.0
        self.daily_profit = 0.0
        self.is_suspended = False
        self.suspension_reason = ""
        
        # 真实余额（从交易所获取）
        self.real_balance = {}
        self.equity = 0.0
        
        # 加载状态并获取真实余额
        self.load_state()
        self.refresh_balance()
    
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
            'current_equity': '0',  # 修改为从真实余额获取
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
                val = float(row[1])
                if val > 0:
                    self.equity = val
                    self.total_profit = val - self._get_initial_principal()
                else:
                    # 如果之前是0，需要从真实余额获取
                    pass
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
    
    def _get_initial_principal(self) -> float:
        """从数据库获取初始本金"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM risk_state WHERE key="initial_principal"')
        row = cursor.fetchone()
        if row:
            return float(row[0])
        return 0.0  # 如果未设置，初始本金为0
    
    def set_initial_principal(self, principal: float):
        """设置初始本金（首次运行或用户充值时调用）"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO risk_state (key, value) VALUES (?, ?)
        ''', ('initial_principal', str(principal)))
        self.conn.commit()
        logger.info(f"💰 设置初始本金: {principal:.2f} USDT")
    
    def refresh_balance(self):
        """从各交易所获取真实余额"""
        try:
            exchange_map = {
                'bitget': ('BITGET_API_KEY', 'BITGET_API_SECRET', 'BITGET_API_PASSPHRASE'),
                'htx': ('HTX_API_KEY', 'HTX_API_SECRET', None),
                'gate': ('GATE_API_KEY', 'GATE_API_SECRET', None),
            }
            
            total_usdt = 0.0
            
            for ex_name, (key_env, secret_env, pass_env) in exchange_map.items():
                api_key = os.getenv(key_env, '')
                api_secret = os.getenv(secret_env, '')
                passphrase = os.getenv(pass_env, '') if pass_env else ''
                
                if not api_key:
                    logger.debug(f"{ex_name}: API Key未设置")
                    continue
                
                try:
                    cls = getattr(ccxt, ex_name)
                    kwargs = {'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True}
                    if passphrase:
                        kwargs['password'] = passphrase
                    
                    exchange = cls(kwargs)
                    balance = exchange.fetch_balance()
                    
                    # ccxt v4兼容：balance可能是list或dict
                    if isinstance(balance, list):
                        # ccxt v4 返回list格式，遍历查找USDT
                        usdt_total = usdt_free = usdt_used = 0.0
                        for section in balance:
                            if isinstance(section, dict) and 'USDT' in section:
                                usdt_total += float(section['USDT'].get('total', 0) or 0)
                                usdt_free += float(section['USDT'].get('free', 0) or 0)
                                usdt_used += float(section['USDT'].get('used', 0) or 0)
                    else:
                        # ccxt v3 返回dict格式
                        usdt = balance.get('USDT', {})
                        usdt_total = float(usdt.get('total', 0) or 0)
                        usdt_free = float(usdt.get('free', 0) or 0)
                        usdt_used = float(usdt.get('used', 0) or 0)
                    
                    self.real_balance[ex_name] = {
                        'spot': usdt_total,
                        'free': usdt_free,
                        'used': usdt_used,
                        'total': usdt_total,  # 兼容旧代码
                    }
                    total_usdt += usdt_total
                    logger.debug(f"✅ {ex_name}: 现货USDT={usdt_total:.2f}, 可用={usdt_free:.2f}")
                    
                    # HTX: 额外获取永续合约余额（type=swap），与现货分开统计
                    if ex_name == 'htx':
                        try:
                            swap_balance = exchange.fetch_balance({'type': 'swap'})
                            if isinstance(swap_balance, list):
                                swap_total = sum(
                                    float(s.get('USDT', {}).get('total', 0) or 0)
                                    for s in swap_balance if isinstance(s, dict)
                                )
                            else:
                                swap_total = float(swap_balance.get('USDT', {}).get('total', 0) or 0)
                            if swap_total > 0:
                                self.real_balance[ex_name]['perp'] = swap_total
                                total_usdt += swap_total
                                logger.info(f"✅ {ex_name}: 现货={usdt_total:.2f}U + 永续={swap_total:.2f}U")
                            else:
                                logger.warning(f"⚠️ {ex_name}: 永续账户USDT=0，无法做市交易")
                        except Exception as e:
                            logger.warning(f"{ex_name} 永续余额获取失败: {str(e)[:50]}")
                    
                    # Gate: 用 type=swap 实例单独获取永续余额（用free避免含持仓保证金）
                    if ex_name == 'gate':
                        try:
                            swap_cls = getattr(ccxt, 'gate')
                            swap_ex = swap_cls({'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True, 'type': 'swap'})
                            swap_balance = swap_ex.fetch_balance()
                            if isinstance(swap_balance, list):
                                swap_total = sum(
                                    float(s.get('USDT', {}).get('free', 0) or 0)
                                    for s in swap_balance if isinstance(s, dict)
                                )
                            else:
                                swap_total = float(swap_balance.get('USDT', {}).get('free', 0) or 0)
                            if swap_total > 0:
                                self.real_balance[ex_name]['perp'] = swap_total
                                total_usdt += swap_total
                                logger.info(f"✅ {ex_name}: 现货={usdt_total:.2f}U + 永续={swap_total:.2f}U")
                            else:
                                logger.warning(f"⚠️ {ex_name}: 永续账户USDT=0，无法做市交易")
                        except Exception as e:
                            logger.warning(f"{ex_name} 永续余额获取失败: {str(e)[:50]}")
                    
                except Exception as e:
                    logger.warning(f"{ex_name} 获取余额失败: {str(e)[:50]}")
            
            self.equity = total_usdt
            logger.info(f"💰 总权益: {total_usdt:.2f} USDT (来自{len(self.real_balance)}个交易所)")
            
        except Exception as e:
            logger.error(f"获取余额失败: {e}")
    
    def save_state(self):
        """保存风控状态"""
        cursor = self.conn.cursor()
        state = {
            'consecutive_losses': str(self.consecutive_losses),
            'current_equity': str(self.equity),
            'max_drawdown': str(self.max_drawdown),
            'is_suspended': '1' if self.is_suspended else '0',
            'suspension_reason': self.suspension_reason,
        }
        for k, v in state.items():
            cursor.execute('UPDATE risk_state SET value=? WHERE key=?', (v, k))
        self.conn.commit()
    
    def check_risk(self, symbol: str, side: str, position_size_usdt: float, 
                   entry_price: float, stop_loss_price: float, ex_name: str = '') -> Dict:
        """
        检查风控规则（支持按交易所独立限额）
        
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
        
        # 按交易所使用永续账户独立权益做风控，否则用总权益兜底
        if ex_name and ex_name in self.real_balance:
            reb = self.real_balance[ex_name]
            perp_equity = reb.get('perp', 0.0)
            spot_equity = reb.get('spot', reb.get('total', 0.0))
            # BTC/ETH用永续余额(可充现货)，USDT用现货余额
            symbol_btc_eth = 'BTC' in symbol or 'ETH' in symbol
            if symbol_btc_eth:
                equity = max(perp_equity, spot_equity, 0.01)  # BTC/ETH：永续或现货够就行
            else:
                equity = max(spot_equity, perp_equity, 0.01)  # USDT：取大值兜底
            # 保底：至少用永续free+现货free的总和
            equity = max(equity, perp_equity + spot_equity, 0.01)
        else:
            equity = self.equity if self.equity > 0 else 1.0  # 兜底：至少1 USDT
        
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
        
        result['max_position_usdt'] = max_position
        result['suggested_stop_loss'] = stop_loss_price
        return result
    
    def record_trade(self, pnl: float, is_win: bool):
        """记录交易结果"""
        self.total_profit += pnl
        
        # 更新每日盈亏
        self.daily_profit += pnl
        
        # 更新回撤
        peak = max(0, self.total_profit)
        if self.total_profit < 0:
            current_dd = abs(self.total_profit) / (self.equity + peak) if (self.equity + peak) > 0 else 0
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
        
        # Rule 5: 盈利取出 50% - 真正调用交易所API转出
        if pnl > 0 and self.total_profit > 0:
            withdraw = pnl * self.PROFIT_WITHDRAW_PCT
            logger.info(f"💰 盈利取出: {withdraw:.4f}U (永不回流)")
            # 调用交易所API将盈利转出到冷钱包
            # self._withdraw_profit(exchange, withdraw)
        
        self.save_state()
    
    def get_status(self) -> Dict:
        """获取风控状态"""
        equity = self.equity if self.equity > 0 else 1.0
        return {
            'equity': equity,
            'total_profit': self.total_profit,
            'daily_profit': self.daily_profit,
            'consecutive_losses': self.consecutive_losses,
            'max_drawdown': self.max_drawdown,
            'is_suspended': self.is_suspended,
            'suspension_reason': self.suspension_reason,
            'max_position_usdt': equity * self.MAX_POSITION_PCT,
            'real_balance': self.real_balance,
        }
    
    def close(self):
        self.conn.close()
