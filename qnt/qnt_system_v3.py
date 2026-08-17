"""
QNT交易系统 v3.0 - 资金管理与风控
核心规则：
1. 单笔仓位 ≤ 总资金 20%
2. 单笔止损 ≤ 总资金 2%
3. 盈利取出 50% 永不回流
4. 三币种平衡：BTC(利润) + HTC(本金储备) + USDT(交易资金)
"""

import ccxt
import os
import time
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('QNT_v3')

# ==================== 风控参数（定死） ====================
RISK_RULES = {
    'max_position_pct': 0.20,      # 单笔最大仓位 20%
    'max_stop_loss_pct': 0.02,     # 单笔最大止损 2%
    'profit_withdraw_pct': 0.50,   # 盈利取出 50%
    'min_profit_threshold': 0.001, # 最小净利阈值 0.1%
    'max_consecutive_losses': 5,   # 连续亏损暂停阈值
}

# ==================== 资金管理规则 ====================
@dataclass
class CapitalAllocation:
    """资金分配规则"""
    # 交易BTC时
    btc_trade: Dict[str, float] = None
    # 交易HTC时
    htc_trade: Dict[str, float] = None
    # 交易其他币种时
    other_trade: Dict[str, float] = None
    
    def __post_init__(self):
        if self.btc_trade is None:
            # 交易BTC：20% BTC本金 + 80% USDT本金，50%利润→HTC
            self.btc_trade = {
                'btc_principal': 0.20,
                'usdt_principal': 0.80,
                'profit_to_htc': 0.50,
                'profit_retain': 0.50
            }
        
        if self.htc_trade is None:
            # 交易HTC：20% HTC本金 + 80% USDT本金，50%利润→BTC
            self.htc_trade = {
                'htc_principal': 0.20,
                'usdt_principal': 0.80,
                'profit_to_btc': 0.50,
                'profit_retain': 0.50
            }
        
        if self.other_trade is None:
            # 交易其他：20% USDT+币种本金 + 80% HTC本金，50%利润→BTC
            self.other_trade = {
                'usdt_principal': 0.10,
                'coin_principal': 0.10,
                'htc_principal': 0.80,
                'profit_to_btc': 0.50,
                'profit_retain': 0.50
            }


# ==================== 账户状态跟踪 ====================
@dataclass
class AccountState:
    """账户状态"""
    timestamp: str
    total_value_usdt: float
    btc_hold: float
    btc_value_usdt: float
    htc_hold: float
    htc_value_usdt: float
    usdt_hold: float
    perp_pnl: float
    spot_pnl: float
    consecutive_losses: int
    total_trades: int
    profitable_trades: int
    
    def to_dict(self):
        return asdict(self)


# ==================== QNT交易系统 ====================
class QNTSystem:
    """QNT量子交易系统 v3.0"""
    
    def __init__(self):
        self.env_file = Path.home() / '.qnt_env'
        self.db_path = '/root/SOM/data/trading_system/qnt.db'
        self.config = CapitalAllocation()
        
        # 加载API密钥
        self._load_api_keys()
        
        # 初始化交易所连接
        self.bitget = self._create_exchange()
        
        # 初始化数据库
        self._init_db()
        
        logger.info("✅ QNT系统v3.0初始化完成")
    
    def _load_api_keys(self):
        """加载API密钥"""
        if not self.env_file.exists():
            raise FileNotFoundError(f"API密钥文件不存在: {self.env_file}")
        
        for line in open(self.env_file):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                os.environ[k.strip()] = v.strip().strip('"').strip("'")
    
    def _create_exchange(self):
        """创建交易所实例"""
        api_key = os.getenv('BITGET_API_KEY')
        api_secret = os.getenv('BITGET_API_SECRET')
        api_passphrase = os.getenv('BITGET_API_PASSPHRASE', 'qntsomtop')
        
        if not api_key or not api_secret:
            raise ValueError("API密钥未配置")
        
        return ccxt.bitget({
            'apiKey': api_key,
            'secret': api_secret,
            'password': api_passphrase,
            'enableRateLimit': True
        })
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qnt_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                side TEXT,
                type TEXT,
                exchange TEXT,
                price REAL,
                amount REAL,
                cost REAL,
                fee REAL,
                pnl REAL,
                pnl_pct REAL,
                leverage INTEGER,
                timestamp TIMESTAMP,
                status TEXT
            )
        ''')
        
        # 价差扫描记录
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qnt_spreads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                scan_time TIMESTAMP,
                spot_bid REAL,
                spot_ask REAL,
                perp_bid REAL,
                perp_ask REAL,
                spread_pct REAL,
                net_profit_pct REAL,
                is_opportunity INTEGER
            )
        ''')
        
        # 账户快照表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qnt_account_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                total_value_usdt REAL,
                btc_hold REAL,
                btc_value_usdt REAL,
                htc_hold REAL,
                htc_value_usdt REAL,
                usdt_hold REAL,
                consecutive_losses INTEGER,
                total_trades INTEGER
            )
        ''')
        
        # 风控状态表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qnt_risk_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                consecutive_losses INTEGER,
                total_trades INTEGER,
                is_paused INTEGER,
                pause_reason TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ 数据库初始化完成")
    
    # ==================== 核心功能 ====================
    
    def get_account_state(self) -> AccountState:
        """获取账户状态"""
        try:
            balance = self.bitget.fetch_balance()
            
            # 解析余额（支持扁平和嵌套结构）
            def get_balance(currency):
                val = balance.get(currency, {})
                if isinstance(val, dict):
                    return val.get('total', 0)
                return val if isinstance(val, (int, float)) else 0
            
            btc_total = get_balance('BTC')
            htc_total = get_balance('HTC')
            usdt_total = get_balance('USDT')
            
            # 获取价格
            btc_price = float(self.bitget.fetch_ticker('BTC/USDT')['last'])
            
            # HTC价格需要从其他来源获取，或使用估算值
            # Bitget上可能没有HTC/USDT，这里尝试多种获取方式
            htc_price = 0
            try:
                # 尝试 HT/USDT
                htc_price = float(self.bitget.fetch_ticker('HT/USDT')['last'])
            except:
                try:
                    # 尝试 HTC/BTC
                    htc_btc_rate = float(self.bitget.fetch_ticker('HTC/BTC')['last'])
                    htc_price = htc_btc_rate * btc_price
                except:
                    # 如果都没有，HTC价值设为0（账户中也没有HTC）
                    htc_price = 0
            
            # 计算总价值
            btc_value = btc_total * btc_price
            htc_value = htc_total * htc_price
            total_value = btc_value + htc_value + usdt_total
            
            # 计算盈亏（简化版，实际应该从交易历史计算）
            perp_pnl = 0.0
            spot_pnl = 0.0
            
            # 获取连续亏损数
            consecutive_losses = self._get_consecutive_losses()
            
            # 获取交易统计
            stats = self._get_trade_stats()
            
            return AccountState(
                timestamp=datetime.now().isoformat(),
                total_value_usdt=total_value,
                btc_hold=btc_total,
                btc_value_usdt=btc_value,
                htc_hold=htc_total,
                htc_value_usdt=htc_value,
                usdt_hold=usdt_total,
                perp_pnl=perp_pnl,
                spot_pnl=spot_pnl,
                consecutive_losses=consecutive_losses,
                total_trades=stats['total'],
                profitable_trades=stats['profitable']
            )
            
        except Exception as e:
            logger.error(f"获取账户状态失败: {e}")
            return None
    
    def scan_spread(self, symbol: str = 'BTC') -> Optional[Dict]:
        """扫描价差机会"""
        try:
            # 获取现货价格
            spot = self.bitget.fetch_ticker(f'{symbol}/USDT')
            spot_bid = float(spot['bid'])
            spot_ask = float(spot['ask'])
            
            # 获取永续价格
            perp = self.bitget.fetch_ticker(f'{symbol}/USDT:USDT')
            perp_bid = float(perp['bid'])
            perp_ask = float(perp['ask'])
            
            # 计算价差（捡乌龙指：永续买 < 现货卖）
            buy_price = perp_ask  # 永续开多买入价
            sell_price = spot_bid  # 现货卖空卖出价
            
            gross_spread = (sell_price - buy_price) / buy_price * 100
            net_spread = gross_spread - 0.12  # 双边手续费约0.12%
            
            is_opportunity = net_spread > RISK_RULES['min_profit_threshold']
            
            # 保存到数据库
            self._save_spread_scan(
                symbol=symbol,
                spot_bid=spot_bid,
                spot_ask=spot_ask,
                perp_bid=perp_bid,
                perp_ask=perp_ask,
                spread_pct=gross_spread,
                net_profit_pct=net_spread,
                is_opportunity=int(is_opportunity)
            )
            
            return {
                'symbol': symbol,
                'spot_bid': spot_bid,
                'spot_ask': spot_ask,
                'perp_bid': perp_bid,
                'perp_ask': perp_ask,
                'spread_pct': gross_spread,
                'net_profit_pct': net_spread,
                'is_opportunity': is_opportunity,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"扫描{symbol}价差失败: {e}")
            return None
    
    def scan_all_symbols(self, symbols: List[str] = None) -> List[Dict]:
        """扫描所有币种价差"""
        if symbols is None:
            symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE', 'DOT', 'AVAX', 'LINK']
        
        opportunities = []
        for sym in symbols:
            result = self.scan_spread(sym)
            if result and result['is_opportunity']:
                opportunities.append(result)
            time.sleep(0.1)  # 避免频率限制
        
        return opportunities
    
    def check_risk_rules(self, account_state: AccountState, position_size_usdt: float) -> Tuple[bool, str]:
        """检查风控规则"""
        # 1. 检查仓位比例
        max_position = account_state.total_value_usdt * RISK_RULES['max_position_pct']
        if position_size_usdt > max_position:
            return False, f"仓位${position_size_usdt:.2f}超过最大限制${max_position:.2f}"
        
        # 2. 检查连续亏损
        if account_state.consecutive_losses >= RISK_RULES['max_consecutive_losses']:
            return False, f"连续亏损{account_state.consecutive_losses}次，触发暂停"
        
        # 3. 检查账户余额
        if account_state.total_value_usdt < 1.0:
            return False, f"总资金不足${account_state.total_value_usdt:.2f}"
        
        return True, "风控检查通过"
    
    def calculate_position_size(self, account_state: AccountState, symbol: str) -> float:
        """
        计算单笔仓位大小
        
        资金管理规则：
        - 交易BTC：20% BTC本金 + 80% USDT本金
        - 交易HTC：20% HTC本金 + 80% USDT本金
        - 交易其他：20% USDT+币种 + 80% HTC本金
        - 盈利50% → 利润储备（BTC/HTC互换）
        
        风控约束：
        - 单笔仓位 ≤ 总资金 20%
        - 单笔止损 ≤ 总资金 2%
        """
        total_value = account_state.total_value_usdt
        
        # 基础限制：单笔仓位不超过总资金20%
        base_max = total_value * RISK_RULES['max_position_pct']
        
        # 止损约束：假设止损幅度为1%
        # 单笔止损 ≤ 总资金 2% → 最大仓位 = 总资金 × 2% / 1% = 总资金 × 2
        # 但取较小值，所以实际限制是 base_max
        stop_loss_constraint = (total_value * RISK_RULES['max_stop_loss_pct']) / 0.01
        
        # 根据交易品种调整
        if symbol == 'BTC':
            # 交易BTC：本金80%在USDT，20%在BTC
            # 实际可用USDT和BTC都要考虑
            available_usdt = account_state.usdt_hold
            available_btc_value = account_state.btc_value_usdt
            
            # 本金限制：USDT部分最多80%，BTC部分最多20%
            usdt_limit = total_value * 0.80
            btc_limit = total_value * 0.20
            
            # 取最小值（资金限制或风控限制）
            position_size = min(base_max, stop_loss_constraint, usdt_limit + btc_limit)
            
        elif symbol == 'HTC':
            # 交易HTC：本金80%在USDT，20%在HTC
            available_usdt = account_state.usdt_hold
            
            # 如果没有USDT，无法交易（HTC在Bitget上可能没有USDT交易对）
            if available_usdt < 1.0:
                logger.warning("⚠️ 交易HTC需要USDT本金，但当前USDT不足")
                return 0
            
            position_size = min(base_max, stop_loss_constraint, available_usdt)
            
        else:
            # 交易其他：本金80%在HTC，20%在USDT+币种
            # 注意：这里HTC作为本金储备，不是交易品种
            available_usdt = account_state.usdt_hold
            
            # 如果没有USDT，无法交易
            if available_usdt < 1.0:
                logger.warning(f"⚠️ 交易{symbol}需要USDT本金，但当前USDT不足")
                return 0
            
            position_size = min(base_max, stop_loss_constraint, available_usdt)
        
        # 确保不小于最小交易单位
        min_trade = 1.0  # 至少1 USDT
        return max(position_size, 0)  # 如果资金不足则返回0
    
    def execute_trade(self, symbol: str, signal: Dict) -> Dict:
        """执行交易（捡乌龙指）"""
        account_state = self.get_account_state()
        if not account_state:
            return {'success': False, 'error': '无法获取账户状态'}
        
        # 检查风控
        position_size = self.calculate_position_size(account_state, symbol)
        is_ok, reason = self.check_risk_rules(account_state, position_size)
        
        if not is_ok:
            logger.warning(f"❌ 风控拦截: {reason}")
            return {'success': False, 'error': reason}
        
        logger.info(f"🚀 执行交易: {symbol}")
        logger.info(f"   当前总资金: ${account_state.total_value_usdt:.2f}")
        logger.info(f"   仓位大小: ${position_size:.2f}")
        
        try:
            # 1. 永续开多
            perp_amount = position_size / signal['perp_ask']
            logger.info(f"   永续开多: {perp_amount:.6f} {symbol}")
            
            # 这里需要实际的下单逻辑，暂时跳过
            # perp_order = self.bitget.create_order(...)
            
            # 2. 现货卖空（等同步挂卖单）
            spot_amount = position_size / signal['spot_bid']
            logger.info(f"   现货卖空: {spot_amount:.6f} {symbol}")
            
            # 这里需要实际的下单逻辑，暂时跳过
            # spot_order = self.bitget.create_order(...)
            
            # 3. 保存交易记录
            self._save_trade(symbol, signal, position_size, status='pending')
            
            logger.info(f"✅ 交易执行完成（模拟）")
            
            return {
                'success': True,
                'symbol': symbol,
                'position_size': position_size,
                'perp_buy_price': signal['perp_ask'],
                'spot_sell_price': signal['spot_bid'],
                'expected_profit': position_size * signal['net_profit_pct'] / 100
            }
            
        except Exception as e:
            logger.error(f"❌ 交易执行失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def handle_profit(self, profit_usdt: float, symbol: str):
        """
        处理盈利分配
        
        规则：
        - 盈利50% → 利润储备（BTC/HTC互换）
        - 盈利50% → 累积本金
        
        利润储备方向：
        - 交易BTC → 利润转HTC储备
        - 交易HTC → 利润转BTC储备
        - 交易其他 → 利润转BTC储备
        """
        if profit_usdt <= 0:
            return
        
        # 取出50%作为利润储备
        withdraw_amount = profit_usdt * RISK_RULES['profit_withdraw_pct']
        retain_amount = profit_usdt - withdraw_amount
        
        logger.info(f"💰 盈利分配: 总盈利${profit_usdt:.2f}")
        logger.info(f"   ├─ 取出50% → 利润储备: ${withdraw_amount:.2f}")
        logger.info(f"   └─ 保留50% → 累积本金: ${retain_amount:.2f}")
        
        # 根据交易品种决定利润储备币种
        if symbol == 'BTC':
            # 交易BTC，利润50%转HTC储备
            logger.info(f"   📥 利润储备: 转HTC ${withdraw_amount:.2f}")
            # TODO: 实际购买HTC的逻辑
            
        elif symbol == 'HTC':
            # 交易HTC，利润50%转BTC储备
            logger.info(f"   📥 利润储备: 转BTC ${withdraw_amount:.2f}")
            # TODO: 实际购买BTC的逻辑
            
        else:
            # 交易其他，利润50%转BTC储备
            logger.info(f"   📥 利润储备: 转BTC ${withdraw_amount:.2f}")
            # TODO: 实际购买BTC的逻辑
        
        # 更新数据库
        self._update_profit_record(symbol, profit_usdt, withdraw_amount, retain_amount)
    
    # ==================== 监控循环 ====================
    
    def run_monitor(self, interval: int = 10):
        """运行监控循环"""
        logger.info(f"🔄 启动实时监控 (间隔{interval}秒)")
        logger.info("=" * 60)
        
        last_opportunities = set()
        
        try:
            while True:
                # 获取账户状态
                state = self.get_account_state()
                if state:
                    self._log_account_snapshot(state)
                
                # 扫描价差
                opportunities = self.scan_all_symbols()
                
                if opportunities:
                    for opp in opportunities:
                        opp_key = f"{opp['symbol']}_{opp['net_profit_pct']:.4f}"
                        if opp_key not in last_opportunities:
                            logger.info(f"🎯 发现机会: {opp['symbol']} 净利{opp['net_profit_pct']:.4f}%")
                            last_opportunities.add(opp_key)
                
                # 检查是否应该暂停
                if state and state.consecutive_losses >= RISK_RULES['max_consecutive_losses']:
                    logger.warning(f"⏸️ 触发暂停: 连续亏损{state.consecutive_losses}次")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\n👋 监控已停止")
    
    # ==================== 辅助方法 ====================
    
    def _get_consecutive_losses(self) -> int:
        """获取连续亏损次数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pnl FROM qnt_trades 
            WHERE status = 'completed'
            ORDER BY timestamp DESC
            LIMIT 10
        ''')
        
        trades = cursor.fetchall()
        conn.close()
        
        consecutive = 0
        for trade in trades:
            if trade[0] < 0:
                consecutive += 1
            else:
                break
        
        return consecutive
    
    def _get_trade_stats(self) -> Dict:
        """获取交易统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM qnt_trades WHERE status = \'completed\'')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM qnt_trades WHERE status = \'completed\' AND pnl > 0')
        profitable = cursor.fetchone()[0]
        
        conn.close()
        
        return {'total': total, 'profitable': profitable}
    
    def _save_spread_scan(self, **kwargs):
        """保存价差扫描记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO qnt_spreads 
            (symbol, scan_time, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct, net_profit_pct, is_opportunity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            kwargs.get('symbol'),
            kwargs.get('scan_time', datetime.now().isoformat()),
            kwargs.get('spot_bid'),
            kwargs.get('spot_ask'),
            kwargs.get('perp_bid'),
            kwargs.get('perp_ask'),
            kwargs.get('spread_pct'),
            kwargs.get('net_profit_pct'),
            kwargs.get('is_opportunity', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_trade(self, symbol: str, signal: Dict, position_size: float, status: str = 'pending'):
        """保存交易记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO qnt_trades 
            (symbol, side, type, exchange, price, amount, cost, fee, pnl, pnl_pct, leverage, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol,
            'both',  # 同时开多和卖空
            'oolong_arbitrage',
            'bitget',
            signal.get('perp_ask'),
            position_size / signal.get('perp_ask', 1),
            position_size,
            position_size * 0.0006,  # 预估手续费
            0,  # 待结算
            signal.get('net_profit_pct'),
            100,  # 杠杆
            datetime.now().isoformat(),
            status
        ))
        
        conn.commit()
        conn.close()
    
    def _log_account_snapshot(self, state: AccountState):
        """记录账户快照"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO qnt_account_snapshots
            (timestamp, total_value_usdt, btc_hold, btc_value_usdt, htc_hold, htc_value_usdt, usdt_hold, consecutive_losses, total_trades)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            state.timestamp,
            state.total_value_usdt,
            state.btc_hold,
            state.btc_value_usdt,
            state.htc_hold,
            state.htc_value_usdt,
            state.usdt_hold,
            state.consecutive_losses,
            state.total_trades
        ))
        
        conn.commit()
        conn.close()
    
    def _update_profit_record(self, symbol: str, profit: float, withdraw: float, retain: float):
        """更新盈利记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE qnt_trades 
            SET pnl = ?, status = 'completed'
            WHERE symbol = ? AND status = 'pending'
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (profit, symbol))
        
        conn.commit()
        conn.close()
    
    def close(self):
        """关闭连接"""
        pass


# ==================== 命令行入口 ====================
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='QNT量子交易系统 v3.0')
    parser.add_argument('command', nargs='?', default='monitor',
                        choices=['monitor', 'scan', 'status', 'help'])
    parser.add_argument('--interval', type=int, default=10,
                        help='监控间隔（秒）')
    
    args = parser.parse_args()
    
    system = QNTSystem()
    
    if args.command == 'help':
        print("""
╔══════════════════════════════════════════════════════════╗
║         QNT量子交易系统 v3.0 - 资金管理与风控          ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  📊 资金管理规则：                                       ║
║    • 交易BTC：20% BTC本金 + 80% USDT本金                 ║
║    • 交易HTC：20% HTC本金 + 80% USDT本金                 ║
║    • 交易其他：20% USDT+币种 + 80% HTC本金               ║
║    • 盈利50% → 利润储备（BTC/HTC互换）                   ║
║                                                          ║
║  🛡️ 风控规则（定死）：                                   ║
║    • 单笔仓位 ≤ 总资金 20%                               ║
║    • 单笔止损 ≤ 总资金 2%                                ║
║    • 连续亏损 5 次暂停                                   ║
║    • 盈利取出 50% 永不回流                               ║
║                                                          ║
║  📈 捡乌龙指逻辑：                                       ║
║    • 永续开多 + 现货卖空                                 ║
║    • 瞬间锁利，不持仓过夜                                ║
║    • 净利 > 0.1% 才执行                                  ║
║                                                          ║
║  命令:                                                   ║
║    monitor  - 实时监控（默认）                           ║
║    scan     - 单次扫描所有币种                           ║
║    status   - 查看账户状态                               ║
║    help     - 显示帮助                                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    elif args.command == 'scan':
        logger.info("🔍 开始扫描所有币种...")
        opportunities = system.scan_all_symbols()
        
        if opportunities:
            print(f"\n🎯 发现 {len(opportunities)} 个机会:\n")
            for opp in sorted(opportunities, key=lambda x: x['net_profit_pct'], reverse=True):
                print(f"  {opp['symbol']:<6} | 净利{opp['net_profit_pct']:>7.4f}% | "
                      f"永续买${opp['perp_ask']:>10,.2f} → 现货卖${opp['spot_bid']:>10,.2f}")
        else:
            print("\n✅ 当前没有异常价差机会，等待中...")
        
        system.close()
        
    elif args.command == 'status':
        state = system.get_account_state()
        if state:
            print(f"\n📊 账户状态 ({state.timestamp})")
            print("-" * 50)
            print(f"  总价值: ${state.total_value_usdt:.2f}")
            print(f"  BTC: {state.btc_hold:.6f} ≈ ${state.btc_value_usdt:.2f}")
            print(f"  HTC: {state.htc_hold:.6f} ≈ ${state.htc_value_usdt:.2f}")
            print(f"  USDT: ${state.usdt_hold:.4f}")
            print("-" * 50)
            print(f"  连续亏损: {state.consecutive_losses}次")
            print(f"  总交易: {state.total_trades}笔")
            print(f"  盈利交易: {state.profitable_trades}笔")
        system.close()
        
    elif args.command == 'monitor':
        system.run_monitor(interval=args.interval)


if __name__ == '__main__':
    main()
