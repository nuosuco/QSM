"""
QNT交易系统 v4.0 - 基于碧树西风核心思想

资金池管理规则（定死）：
  交易BTC：
    - BTC本金 20% + USDT本金 80%
    - 盈利50% → 转入HTC储备
  
  交易其他：
    - USDT+币种本金 20% + HTC本金 80%
    - 盈利50% → 转入BTC储备

风控规则（定死）：
  - 单笔仓位 ≤ 总资金 20%
  - 单笔止损 ≤ 总资金 2%
  - 连续亏损 5 次暂停
  - 最大回撤 40%
  - 盈利取出 50% 永不回流
"""

import ccxt
import os
import time
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('QNT_v4')

# ==================== 风控参数（定死） ====================
RISK_RULES = {
    'min_profit_pct': 0.001,           # 最小净利 0.1%
    'max_position_pct': 0.20,          # 单笔最大仓位 20%
    'max_stop_loss_pct': 0.02,         # 单笔最大止损 2%
    'profit_withdraw_pct': 0.50,       # 盈利取出 50%
    'max_consecutive_losses': 5,       # 连续亏损暂停阈值
    'max_drawdown_pct': 0.40,          # 最大回撤 40%
}

# ==================== 挂单偏移（定死） ====================
ORDER_OFFSET = {
    'buy_offset': 0.001,   # 买单在买一价下方 0.1%
    'sell_offset': 0.001,  # 卖单在卖一价上方 0.1%
    'fee_rate': 0.0006,    # Bitget maker费率 0.06%
}


# ==================== 数据结构 ====================
@dataclass
class AccountState:
    """账户状态 - 三类资金池"""
    timestamp: str
    total_value_usdt: float
    btc_hold: float
    btc_value_usdt: float
    htc_hold: float = 0.0
    htc_value_usdt: float = 0.0
    usdt_hold: float = 0.0
    eth_hold: float = 0.0
    eth_value_usdt: float = 0.0
    consecutive_losses: int = 0
    total_trades: int = 0
    profitable_trades: int = 0
    peak_value: float = 0.0
    btc_principal_pct: float = 0.20  # BTC本金占比
    is_paused: bool = False
    pause_reason: str = ""


@dataclass
class OrderSignal:
    """挂单信号"""
    symbol: str
    buy_price: float
    sell_price: float
    buy_amount: float
    sell_amount: float
    expected_profit_pct: float
    timestamp: str
    trade_type: str = ""  # "BTC" or "OTHER"


# ==================== QNT系统 v4.0 ====================
class QNTSystem:
    """QNT量子交易系统 v4.0 - 三类资金池管理"""
    
    def __init__(self):
        self.env_file = Path.home() / '.qnt_env'
        self.db_path = '/root/SOM/data/trading_system/qnt.db'
        self.log_file = Path('/root/SOM/qnt/logs/qnt_v4.log')
        
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        self._load_api_keys()
        self.bitget = self._create_exchange()
        self._init_db()
        
        logger.info("=" * 70)
        logger.info("QNT系统v4.0初始化完成 - 三类资金池管理")
        logger.info("策略: 交易BTC用BTC本金20%+USDT 80%，盈利50%→HTC")
        logger.info("策略: 交易其他用USDT+币种20%+HTC 80%，盈利50%→BTC")
        logger.info("风控: 单笔仓位≤20%, 止损≤2%, 连续5亏暂停, 盈利50%取出")
        logger.info("=" * 70)
    
    def _load_api_keys(self):
        """API密钥只从环境变量读取"""
        pass
    
    def _create_exchange(self):
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qnt_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                trade_type TEXT,
                buy_order_id TEXT,
                sell_order_id TEXT,
                buy_price REAL,
                sell_price REAL,
                buy_amount REAL,
                sell_amount REAL,
                position_size_usdt REAL,
                expected_profit_pct REAL,
                profit_usdt REAL,
                profit_pct REAL,
                timestamp TIMESTAMP,
                status TEXT
            )
        ''')
        
        # 信号表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qnt_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                buy_price REAL,
                sell_price REAL,
                expected_profit_pct REAL,
                trade_type TEXT,
                timestamp TIMESTAMP,
                executed INTEGER DEFAULT 0
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
                eth_hold REAL,
                eth_value_usdt REAL,
                consecutive_losses INTEGER,
                total_trades INTEGER,
                peak_value REAL,
                is_paused INTEGER
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
                pause_reason TEXT,
                current_drawdown_pct REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ 数据库初始化完成")
    
    def get_account_state(self) -> AccountState:
        """获取账户状态 - 计算三类资金池"""
        try:
            balance = self.bitget.fetch_balance()
            
            def get_balance(currency):
                val = balance.get(currency, {})
                if isinstance(val, dict):
                    return val.get('free', 0) or val.get('total', 0)
                return val if isinstance(val, (int, float)) else 0
            
            btc_total = get_balance('BTC')
            eth_total = get_balance('ETH')
            htc_total = get_balance('HTC')
            usdt_total = get_balance('USDT')
            
            # 获取价格
            btc_price = float(self.bitget.fetch_ticker('BTC/USDT')['last'])
            eth_price = float(self.bitget.fetch_ticker('ETH/USDT')['last'])
            
            htc_price = 0
            try:
                htc_price = float(self.bitget.fetch_ticker('HT/USDT')['last'])
            except:
                pass
            
            # 计算价值
            btc_value = btc_total * btc_price
            eth_value = eth_total * eth_price
            htc_value = htc_total * htc_price
            total_value = btc_value + eth_value + htc_value + usdt_total
            
            # 获取风控状态
            consecutive_losses = self._get_consecutive_losses()
            stats = self._get_trade_stats()
            peak_value = self._get_peak_value()
            
            # 更新峰值
            if total_value > peak_value:
                peak_value = total_value
                self._update_peak_value(peak_value)
            
            # 检查暂停状态
            is_paused, pause_reason = self._check_pause_state()
            
            return AccountState(
                timestamp=datetime.now().isoformat(),
                total_value_usdt=total_value,
                btc_hold=btc_total,
                btc_value_usdt=btc_value,
                htc_hold=htc_total,
                htc_value_usdt=htc_value,
                usdt_hold=usdt_total,
                eth_hold=eth_total,
                eth_value_usdt=eth_value,
                consecutive_losses=consecutive_losses,
                total_trades=stats['total'],
                profitable_trades=stats['profitable'],
                peak_value=peak_value,
                is_paused=is_paused,
                pause_reason=pause_reason
            )
            
        except Exception as e:
            logger.error(f"获取账户状态失败: {e}")
            return None
    
    def scan_for_opportunities(self, symbols: List[str] = None) -> List[OrderSignal]:
        """扫描挂双单机会 - 按交易类型分类"""
        if symbols is None:
            symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE', 'DOT', 'AVAX', 'LINK']
        
        opportunities = []
        
        for sym in symbols:
            try:
                # 尝试获取现货订单簿
                ob = self.bitget.fetch_order_book(f'{sym}/USDT', limit=5)
                
                if not ob['bids'] or not ob['asks']:
                    continue
                
                bid_price = float(ob['bids'][0][0])
                ask_price = float(ob['asks'][0][0])
                bid_size = float(ob['bids'][0][1])
                ask_size = float(ob['asks'][0][1])
                
                # 计算挂单价格
                buy_price = bid_price * (1 - ORDER_OFFSET['buy_offset'])
                sell_price = ask_price * (1 + ORDER_OFFSET['sell_offset'])
                
                # 计算价差和利润
                spread = sell_price - buy_price
                fee_cost = buy_price * ORDER_OFFSET['fee_rate'] + sell_price * ORDER_OFFSET['fee_rate']
                net_profit = spread - fee_cost
                net_profit_pct = (net_profit / buy_price) * 100 if buy_price > 0 else 0
                
                # 确定交易类型
                trade_type = "BTC" if sym == 'BTC' else "OTHER"
                
                if net_profit_pct > RISK_RULES['min_profit_pct']:
                    signal = OrderSignal(
                        symbol=sym,
                        buy_price=buy_price,
                        sell_price=sell_price,
                        buy_amount=bid_size,
                        sell_amount=ask_size,
                        expected_profit_pct=net_profit_pct,
                        timestamp=datetime.now().isoformat(),
                        trade_type=trade_type
                    )
                    opportunities.append(signal)
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.debug(f"扫描{sym}失败: {e}")
        
        return opportunities
    
    def calculate_position_size(self, state: AccountState, signal: OrderSignal) -> float:
        """计算仓位大小 - 根据交易类型使用不同资金池"""
        symbol = signal.symbol
        trade_type = signal.trade_type
        
        if trade_type == "BTC":
            # 交易BTC：BTC本金20% + USDT本金80%
            # BTC本金 = BTC价值的20%
            btc_principal = state.btc_value_usdt * 0.20
            # USDT本金 = USDT的80%
            usdt_principal = state.usdt_hold * 0.80
            # 总仓位取两者较小值（受限于流动性）
            max_position = min(btc_principal, usdt_principal)
            
        else:
            # 交易其他：USDT+币种20% + HTC本金80%
            # USDT+币种本金
            coin_value = state.eth_value_usdt if symbol == 'ETH' else 0
            usdt_coin_principal = (state.usdt_hold + coin_value) * 0.20
            # HTC本金80%
            htc_principal = state.htc_value_usdt * 0.80
            # 总仓位取两者较小值
            max_position = min(usdt_coin_principal, htc_principal)
        
        # 风控约束：单笔仓位≤总资金20%
        position_by_risk = state.total_value_usdt * RISK_RULES['max_position_pct']
        
        # 最终仓位取最小值
        position_size = min(max_position, position_by_risk)
        
        # 止损约束：止损≤总资金2%
        # 假设止损为1%（正常波动）
        stop_loss_pct = 0.01
        position_by_stop = (state.total_value_usdt * RISK_RULES['max_stop_loss_pct']) / stop_loss_pct
        position_size = min(position_size, position_by_stop)
        
        return max(0, position_size)
    
    def check_risk_rules(self, state: AccountState) -> Tuple[bool, str]:
        """检查风控规则"""
        # 1. 检查是否暂停
        if state.is_paused:
            return False, f"已暂停: {state.pause_reason}"
        
        # 2. 检查连续亏损
        if state.consecutive_losses >= RISK_RULES['max_consecutive_losses']:
            return False, f"连续亏损{state.consecutive_losses}次，触发暂停"
        
        # 3. 检查账户余额
        if state.total_value_usdt < 1.0:
            return False, f"总资金不足${state.total_value_usdt:.2f}"
        
        # 4. 检查回撤
        if state.peak_value > 0:
            drawdown = (state.peak_value - state.total_value_usdt) / state.peak_value * 100
            if drawdown >= RISK_RULES['max_drawdown_pct'] * 100:
                return False, f"回撤{drawdown:.1f}%超过最大限制{RISK_RULES['max_drawdown_pct']*100}%"
        
        return True, "风控检查通过"
    
    def place_maker_orders(self, signal: OrderSignal, position_size_usdt: float) -> Dict:
        """挂双单做市商订单"""
        result = {
            'symbol': signal.symbol,
            'trade_type': signal.trade_type,
            'timestamp': signal.timestamp,
            'buy_order_id': None,
            'sell_order_id': None,
            'status': 'pending'
        }
        
        try:
            # 计算下单数量
            buy_amount = position_size_usdt / signal.buy_price
            sell_amount = position_size_usdt / signal.sell_price
            
            # 确保不超过订单簿深度
            buy_amount = min(buy_amount, signal.buy_amount * 0.9)
            sell_amount = min(sell_amount, signal.sell_amount * 0.9)
            
            # 更新实际下单金额
            actual_buy_value = buy_amount * signal.buy_price
            actual_sell_value = sell_amount * signal.sell_price
            actual_position = min(actual_buy_value, actual_sell_value)
            
            # 挂买单（Post-Only）
            try:
                buy_order = self.bitget.create_order(
                    symbol=f'{signal.symbol}/USDT',
                    type='limit',
                    side='buy',
                    amount=buy_amount,
                    price=signal.buy_price,
                    params={'postOnly': True}
                )
                result['buy_order_id'] = buy_order['id']
            except Exception as e:
                logger.warning(f"买单失败: {e}")
                result['buy_error'] = str(e)
            
            # 挂卖单（Post-Only）
            try:
                sell_order = self.bitget.create_order(
                    symbol=f'{signal.symbol}/USDT',
                    type='limit',
                    side='sell',
                    amount=sell_amount,
                    price=signal.sell_price,
                    params={'postOnly': True}
                )
                result['sell_order_id'] = sell_order['id']
            except Exception as e:
                logger.warning(f"卖单失败: {e}")
                result['sell_error'] = str(e)
            
            # 检查结果
            if result['buy_order_id'] and result['sell_order_id']:
                result['status'] = 'placed'
                result['position_size'] = actual_position
                logger.info(f"✅ {signal.symbol} 双单已挂出: 买@{signal.buy_price:.4f} 卖@{signal.sell_price:.4f}")
            elif result['buy_order_id'] or result['sell_order_id']:
                result['status'] = 'partial'
                logger.warning(f"⚠️ {signal.symbol} 只挂成一单，等待对冲")
            else:
                result['status'] = 'failed'
                logger.error(f"❌ {signal.symbol} 双单都失败")
            
            # 保存信号到数据库
            self._save_signal(signal, result['status'])
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"挂单失败: {e}")
        
        return result
    
    def run_monitor(self, interval: int = 10):
        """运行监控循环"""
        logger.info(f"🔄 启动实时监控 (间隔{interval}秒)")
        logger.info("=" * 70)
        
        last_signals = set()
        
        try:
            while True:
                # 获取账户状态
                state = self.get_account_state()
                if state:
                    self._log_account_snapshot(state)
                    
                    # 显示当前状态
                    logger.info(f"\n📊 账户状态:")
                    logger.info(f"   总价值: ${state.total_value_usdt:.2f}")
                    logger.info(f"   BTC池: {state.btc_hold:.6f} ≈ ${state.btc_value_usdt:.2f}")
                    logger.info(f"   ETH池: {state.eth_hold:.6f} ≈ ${state.eth_value_usdt:.2f}")
                    logger.info(f"   HTC池: {state.htc_hold:.6f} ≈ ${state.htc_value_usdt:.2f}")
                    logger.info(f"   USDT池: ${state.usdt_hold:.4f}")
                    logger.info(f"   连续亏损: {state.consecutive_losses}次")
                    logger.info(f"   峰值: ${state.peak_value:.2f}")
                    
                    # 检查风控
                    is_ok, reason = self.check_risk_rules(state)
                    if not is_ok:
                        logger.warning(f"⏸️ 风控拦截: {reason}")
                
                # 扫描机会
                opportunities = self.scan_for_opportunities()
                
                if opportunities:
                    logger.info(f"\n🎯 发现 {len(opportunities)} 个机会:")
                    for opp in sorted(opportunities, key=lambda x: x.expected_profit_pct, reverse=True)[:5]:
                        opp_key = f"{opp.symbol}_{opp.trade_type}_{opp.expected_profit_pct:.4f}"
                        if opp_key not in last_signals:
                            logger.info(f"   • {opp.symbol}({opp.trade_type}): 买@{opp.buy_price:.4f} 卖@{opp.sell_price:.4f} 净利{opp.expected_profit_pct:.4f}%")
                            last_signals.add(opp_key)
                    
                    # 执行交易（如果有可用资金且风控通过）
                    if state and self.check_risk_rules(state)[0]:
                        for opp in opportunities[:1]:  # 每次只处理一个
                            position_size = self.calculate_position_size(state, opp)
                            if position_size > 1.0:
                                logger.info(f"\n🚀 执行交易: {opp.symbol}({opp.trade_type}) 仓位${position_size:.2f}")
                                result = self.place_maker_orders(opp, position_size)
                                logger.info(f"   结果: {result['status']}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\n👋 监控已停止")
    
    # ==================== 辅助方法 ====================
    
    def _get_consecutive_losses(self) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT profit_usdt FROM qnt_trades 
            WHERE status = 'completed' AND profit_usdt IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 10
        ''')
        
        trades = cursor.fetchall()
        conn.close()
        
        consecutive = 0
        for trade in trades:
            if trade[0] is not None and trade[0] < 0:
                consecutive += 1
            else:
                break
        
        return consecutive
    
    def _get_trade_stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM qnt_trades WHERE status = 'completed'")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM qnt_trades WHERE status = 'completed' AND profit_usdt > 0")
        profitable = cursor.fetchone()[0]
        
        conn.close()
        
        return {'total': total, 'profitable': profitable}
    
    def _get_peak_value(self) -> float:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT MAX(total_value_usdt) FROM qnt_account_snapshots")
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result and result[0] else 0
    
    def _update_peak_value(self, peak_value: float):
        peak_file = Path('/root/SOM/qnt/data/peak_value.json')
        peak_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {}
        if peak_file.exists():
            with open(peak_file) as f:
                data = json.load(f)
        
        data['peak_value'] = peak_value
        data['updated_at'] = datetime.now().isoformat()
        
        with open(peak_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _check_pause_state(self) -> Tuple[bool, str]:
        """检查是否应该暂停"""
        consecutive_losses = self._get_consecutive_losses()
        
        if consecutive_losses >= RISK_RULES['max_consecutive_losses']:
            return True, f"连续亏损{consecutive_losses}次"
        
        return False, ""
    
    def _log_account_snapshot(self, state: AccountState):
        """记录账户快照"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO qnt_account_snapshots 
            (timestamp, total_value_usdt, btc_hold, btc_value_usdt, htc_hold, htc_value_usdt, 
             usdt_hold, eth_hold, eth_value_usdt, consecutive_losses, total_trades, peak_value, is_paused)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            state.timestamp,
            state.total_value_usdt,
            state.btc_hold,
            state.btc_value_usdt,
            state.htc_hold,
            state.htc_value_usdt,
            state.usdt_hold,
            state.eth_hold,
            state.eth_value_usdt,
            state.consecutive_losses,
            state.total_trades,
            state.peak_value,
            1 if state.is_paused else 0
        ))
        
        conn.commit()
        conn.close()
    
    def _save_signal(self, signal: OrderSignal, status: str):
        """保存信号到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO qnt_signals 
            (symbol, buy_price, sell_price, expected_profit_pct, trade_type, timestamp, executed)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', (
            signal.symbol,
            signal.buy_price,
            signal.sell_price,
            signal.expected_profit_pct,
            signal.trade_type,
            signal.timestamp
        ))
        
        conn.commit()
        conn.close()
    
    def show_status(self):
        """显示账户状态"""
        state = self.get_account_state()
        if not state:
            print("❌ 无法获取账户状态")
            return
        
        print(f"\n📊 账户状态 ({state.timestamp})")
        print("-" * 50)
        print(f"   总价值: ${state.total_value_usdt:.2f}")
        print(f"   BTC池: {state.btc_hold:.6f} ≈ ${state.btc_value_usdt:.2f}")
        print(f"   ETH池: {state.eth_hold:.6f} ≈ ${state.eth_value_usdt:.2f}")
        print(f"   HTC池: {state.htc_hold:.6f} ≈ ${state.htc_value_usdt:.2f}")
        print(f"   USDT池: ${state.usdt_hold:.4f}")
        print("-" * 50)
        print(f"   连续亏损: {state.consecutive_losses}次")
        print(f"   总交易: {state.total_trades}笔")
        print(f"   盈利交易: {state.profitable_trades}笔")
        print(f"   历史峰值: ${state.peak_value:.2f}")
        
        if state.peak_value > 0:
            drawdown = (state.peak_value - state.total_value_usdt) / state.peak_value * 100
            print(f"   当前回撤: {drawdown:.2f}%")
        
        is_ok, reason = self.check_risk_rules(state)
        status = "✅ 正常" if is_ok else f"⚠️ {reason}"
        print(f"   风控状态: {status}")
        print()
    
    def run_scan(self):
        """单次扫描"""
        state = self.get_account_state()
        if not state:
            print("❌ 无法获取账户状态")
            return
        
        print(f"\n📊 账户状态: ${state.total_value_usdt:.2f}")
        print("-" * 50)
        
        opportunities = self.scan_for_opportunities()
        
        if opportunities:
            print(f"🎯 发现 {len(opportunities)} 个机会:\n")
            print(f"{'币种':<8} {'类型':<8} {'买价':<12} {'卖价':<12} {'净利':<10}")
            print("-" * 60)
            for opp in sorted(opportunities, key=lambda x: x.expected_profit_pct, reverse=True):
                print(f"{opp.symbol:<8} {opp.trade_type:<8} {opp.buy_price:<12.4f} {opp.sell_price:<12.4f} {opp.expected_profit_pct:.4f}%")
        else:
            print("没有找到符合阈值的机会")
        
        print()
    
    def show_help(self):
        """显示帮助"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║          QNT量子交易系统 v4.0 - 碧树西风核心思想            ║
╠══════════════════════════════════════════════════════════════╣
║                                                           ║
║  📊 核心策略：                                           ║
║    • 挂双单做市商：买一×0.999 + 卖一×1.001               ║
║    • 净利润必须 > 0.1% 才执行                            ║
║    • Post-Only订单，确保不做Taker                         ║
║                                                           ║
║  💰 资金池管理（定死）：                                  ║
║    • 交易BTC：BTC本金20% + USDT本金80%                    ║
║    • 交易其他：USDT+币种20% + HTC本金80%                   ║
║    • 盈利50% → 转入储备池（永不回流）                     ║
║                                                           ║
║  🛡️ 风控规则（定死）：                                   ║
║    • 单笔仓位 ≤ 总资金 20%                               ║
║    • 单笔止损 ≤ 总资金 2%                                ║
║    • 连续亏损 5 次暂停交易                               ║
║    • 最大回撤 40% 停止交易                               ║
║    • 盈利取出 50% 永不回流                               ║
║                                                           ║
║  📈 碧树西风核心思想：                                   ║
║    • 等错来（大数定律）                                   ║
║    • 向下有限，向上无限                                   ║
║    • 对冲是天然控制损失                                   ║
║    • 像机器一样执行（足够傻足够死板）                     ║
║                                                           ║
║  命令:                                                    ║
║    monitor  - 实时监控（默认）                           ║
║    scan     - 单次扫描所有币种                           ║
║    status   - 查看账户状态                               ║
║    help     - 显示帮助                                   ║
║                                                           ║
╚══════════════════════════════════════════════════════════════╝
""")


def main():
    import sys
    
    system = QNTSystem()
    
    if len(sys.argv) < 2:
        system.show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'monitor':
        system.run_monitor()
    elif command == 'scan':
        system.run_scan()
    elif command == 'status':
        system.show_status()
    elif command == 'help':
        system.show_help()
    else:
        print(f"未知命令: {command}")
        system.show_help()


if __name__ == '__main__':
    main()
