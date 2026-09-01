"""
双引擎回测/模拟系统 - 完整版（真实交易周期）
- BacktestEngine: 历史数据回放 + 实时追加回测（完整BUY+SELL周期）
- PaperEngine: 实时模拟交易（完整BUY+SELL周期，真实风控检查）
"""
import time
import logging
import sqlite3
import threading
import random
from datetime import datetime
from typing import Dict, List, Optional
import ccxt

from .config import SystemConfig
from .risk_manager import RiskManager
from .execution_engine import ExecutionEngine

# 各交易所永续合约最小金额限制
PERP_MIN_NOTIONAL = {'bitget': 5.0, 'htx': 1.0, 'gate': 3.0}

logger = logging.getLogger('DualEngine')


class Position:
    """持仓对象"""
    def __init__(self, symbol, exchange, side, price, amount, position_id, timestamp):
        self.symbol = symbol
        self.exchange = exchange
        self.side = side  # 'buy' or 'sell'
        self.price = price
        self.amount = amount
        self.position_id = position_id
        self.timestamp = timestamp
        self.cost = amount * price
        self.fee_rate = ExecutionEngine.MAKER_FEE_RATE  # 0.06%

    def close(self, close_price):
        """平仓，返回PnL"""
        if self.side == 'buy':
            # 做多：低买高卖
            gross_pnl = (close_price - self.price) * self.amount
        else:
            # 做空：高卖低买
            gross_pnl = (self.price - close_price) * self.amount
        
        # 手续费
        buy_fee = self.cost * self.fee_rate
        sell_fee = close_price * self.amount * self.fee_rate
        total_fee = buy_fee + sell_fee
        
        net_pnl = gross_pnl - total_fee
        pnl_pct = (net_pnl / self.cost * 100) if self.cost > 0 else 0
        
        return {
            'gross_pnl': gross_pnl,
            'total_fee': total_fee,
            'net_pnl': net_pnl,
            'pnl_pct': pnl_pct,
            'close_price': close_price,
            'timestamp': time.time()
        }


class BacktestEngine:
    """历史回测引擎 - 完整交易周期版（真实BUY+SELL配对）
    铁律：每个平台独立管理余额，互不影响"""

    # 每个平台的初始回测资金
    PLATFORM_INITIAL_BALANCE = {'bitget': 1000.0, 'htx': 1000.0, 'gate': 1000.0}

    def __init__(self, config: SystemConfig, db_path: str):
        self.config = config
        self.db_path = db_path
        self.running = False
        self.thread = None
        self.last_processed_ts = 0
        
        # === 按平台独立管理余额 ===
        self.platforms = ['bitget', 'htx', 'gate']
        self.platform_balances: Dict[str, float] = dict(self.PLATFORM_INITIAL_BALANCE)  # {platform: balance}
        self.platform_trades: Dict[str, int] = {p: 0 for p in self.platforms}  # {platform: trade_count}
        self.platform_wins: Dict[str, int] = {p: 0 for p in self.platforms}  # {platform: win_count}
        self.platform_pnl: Dict[str, float] = {p: 0.0 for p in self.platforms}  # {platform: total_pnl}
        
        self.open_positions: Dict[str, Position] = {}  # {exchange|symbol: Position}
        self.total_trades = 0
        self.winning_trades = 0
        
        # 创建独立的模拟风控管理器，使用模拟余额而非实盘余额
        self.risk_manager = RiskManager(db_path, paper_mode=True, paper_balance=sum(self.platform_balances.values()))

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("📊 回测引擎启动（完整交易周期版，真实BUY+SELL配对）")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("📊 回测引擎已停止")

    def _run_loop(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        cursor = conn.cursor()

        # 找最后处理的 timestamp
        cursor.execute("SELECT MAX(timestamp) FROM engine_trades WHERE mode='backtest'")
        last_ts_row = cursor.fetchone()[0]
        self.last_processed_ts = last_ts_row or 0

        if self.last_processed_ts > 0:
            logger.info(f"   从 {datetime.fromtimestamp(self.last_processed_ts).strftime('%m-%d %H:%M')} 继续")
        else:
            logger.info("   从头开始回放")

        # 获取数据范围
        cursor.execute("""
            SELECT MIN(timestamp), MAX(timestamp)
            FROM market_data
            WHERE spread_pct IS NOT NULL AND ABS(spread_pct) < 1.0
        """)
        row = cursor.fetchone()
        if not row or not row[0]:
            logger.warning("⚠️ 没有可用的 market_data")
            conn.close()
            return

        min_ts, max_ts = row
        total_seconds = max_ts - min_ts
        total_hours = total_seconds / 3600
        logger.info(f"   数据范围: {datetime.fromtimestamp(min_ts).strftime('%m-%d %H:%M')} ~ "
                   f"{datetime.fromtimestamp(max_ts).strftime('%m-%d %H:%M')} ({total_hours:.1f}小时)")

        # 分批处理 - 按平台独立维护窗口
        processed_count = 0
        windows = {p: [] for p in self.platforms}  # 每个平台独立窗口
        threshold = self.config.execution.spread_pct
        cost = ExecutionEngine.BI_SIDE_COST * 100
        min_net_profit = RiskManager.MIN_NET_PROFIT_PCT

        cursor.execute("""
            SELECT timestamp, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct
            FROM market_data
            WHERE timestamp > ? AND spread_pct IS NOT NULL AND ABS(spread_pct) < 1.0
            ORDER BY timestamp ASC
        """, (self.last_processed_ts,))

        rows = cursor.fetchall()
        logger.info(f"   待处理行数: {len(rows)}")

        for ts, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct in rows:
            if not self.running:
                break

            self.last_processed_ts = max(self.last_processed_ts, ts)

            # 只维护当前platform的窗口（避免跨平台数据混合）
            if exchange in windows:
                tick = {
                    'ts': ts, 'exchange': exchange, 'symbol': symbol,
                    'spot_bid': spot_bid, 'spot_ask': spot_ask,
                    'perp_bid': perp_bid, 'perp_ask': perp_ask,
                    'spread': spread_pct
                }
                windows[exchange].append(tick)
                
                # 清理超过30秒的旧数据
                while windows[exchange] and ts - windows[exchange][0]['ts'] > 30:
                    windows[exchange].pop(0)
                
                # 每个平台独立检查开仓机会
                if len(windows[exchange]) >= 5:
                    # 严格检查：价差必须>0.17%（成本0.16%+净利0.01%）
                    if spread_pct >= cost + min_net_profit:
                        self._try_open_position([tick], cursor)
                
                # 检查平仓
                self._check_close_positions(windows[exchange], cursor)

            processed_count += 1
            if processed_count % 100000 == 0:
                logger.info(f"   已处理 {processed_count} 条, {self.total_trades} 笔交易, 胜率 {self.winning_trades/max(self.total_trades,1)*100:.1f}%")

        # 保存进度
        cursor.execute(
            "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (time.time(), 'backtest', 'PROGRESS', 'progress', 'BUY', 0, 0, 0, 0, 0, 0, 'completed')
        )
        conn.commit()

        win_rate = self.winning_trades / max(self.total_trades, 1) * 100

        # === 按平台统计回测结果 ===
        logger.info(f"✅ 历史回测完成: {processed_count} 条, {self.total_trades} 笔完整交易")
        logger.info(f"   总体胜率: {win_rate:.1f}%")
        logger.info(f"   按平台统计:")
        for p in self.platforms:
            p_trades = self.platform_trades[p]
            p_wins = self.platform_wins[p]
            p_pnl = self.platform_pnl[p]
            p_win_rate = p_wins / max(p_trades, 1) * 100 if p_trades > 0 else 0
            logger.info(f"     {p}: {p_trades}笔, 胜率{p_win_rate:.1f}%, 盈亏{p_pnl:+.2f}U")

        # 切换到实时模式
        logger.info("📊 切换到实时回测模式...")
        check_count = 0
        while self.running:
            try:
                cursor.execute("""
                    SELECT timestamp, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct
                    FROM market_data
                    WHERE timestamp > ? AND spread_pct > 0 AND spread_pct < 1.0
                    ORDER BY timestamp DESC LIMIT 1
                """, (self.last_processed_ts,))
                latest = cursor.fetchone()
                if latest:
                    self.last_processed_ts = latest[0]
                    ts, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = latest
                    
                    # 调试日志：每100次检查打印一次
                    check_count += 1
                    if check_count % 100 == 0:
                        logger.debug(f"[回测] 检查#{check_count}, 最新spread={spread_pct:.4f}%, 门槛={threshold:.2f}%")
                    
                    # 严格检查：价差必须>0.17%才能交易
                    if spread_pct >= cost + min_net_profit:
                        logger.debug(f"[回测] 发现机会: {exchange} {symbol} spread={spread_pct:.4f}% >= {cost+min_net_profit:.4f}%")
                        # 构造临时tick
                        tick = {'ts': ts, 'exchange': exchange, 'symbol': symbol,
                               'spot_bid': spot_bid, 'spot_ask': spot_ask,
                               'perp_bid': perp_bid, 'perp_ask': perp_ask,
                               'spread': spread_pct}
                        self._try_open_position([tick], cursor)
                        self._check_close_positions([tick], cursor)
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"实时回测错误: {e}")
                time.sleep(5)

        conn.close()

    def _try_open_position(self, window: list, cursor):
        """尝试开仓"""
        # 取窗口内价差最大的tick
        best_tick = max(window, key=lambda x: abs(x['spread']))
        
        spread_pct = best_tick['spread']
        exchange = best_tick['exchange']
        symbol = best_tick['symbol']
        
        # 调试日志
        logger.debug(f"[回测开仓检查] {exchange} {symbol} spread={spread_pct:.4f}% perp_ask={best_tick['perp_ask']}")
        
        # 严格的成本检查：价差必须>0.17%（成本0.16%+净利0.01%）
        min_spread = (ExecutionEngine.BI_SIDE_COST + RiskManager.MIN_NET_PROFIT_PCT) * 100
        if spread_pct < min_spread:
            logger.debug(f"[回测] 跳过: 价差{spread_pct:.4f}% < 门槛{min_spread:.2f}%")
            return
        
        # 风控检查
        risk_check = self.risk_manager.check_risk(
            symbol=symbol,
            side='buy',
            position_size_usdt=self.platform_balances[exchange] * 0.20,
            entry_price=best_tick['perp_ask'],
            stop_loss_price=best_tick['perp_ask'] * 1.02,
            ex_name=exchange
        )
        if not risk_check['allowed']:
            logger.debug(f"[回测] 风控拒绝: {risk_check['reason']}")
            return
        
        # 最小金额检查
        min_notional = PERP_MIN_NOTIONAL.get(exchange, 1.0)
        position = min(self.platform_balances[exchange] * 0.20, 200)
        
        if position < min_notional:
            logger.debug(f"[回测] 跳过: 仓位{position:.2f}U < 最小{min_notional}U")
            return
        
        # 精度检查
        price = best_tick['perp_ask']
        amount = position / price
        if amount < 1.0:
            logger.debug(f"[回测] 跳过: 币数量{amount:.4f} < 1.0")
            return
        
        # 成交概率（30%）- 降低过滤门槛
        if random.random() >= 0.3:
            logger.debug(f"[回测] 跳过: 成交概率未命中")
            return
        
        # 检查是否已有同币种同方向持仓（按exchange隔离）
        pos_key = f"{exchange}|{symbol}"
        if pos_key in self.open_positions:
            logger.debug(f"[回测] 跳过: 已有持仓 {pos_key}")
            return
        
        # 开仓（使用时间戳生成唯一ID）
        position_id = f"bt_{int(time.time() * 1000)}"
        position = Position(symbol, exchange, 'buy', price, amount, position_id, best_tick['ts'])
        self.open_positions[pos_key] = position
        
        # 记录到数据库
        try:
            cursor.execute(
                "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status, position_id) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (best_tick['ts'], 'backtest', symbol, exchange,
                 'BUY', price, round(amount, 8), position.cost, position.cost * position.fee_rate,
                 0, 0, 'opened', position_id)
            )
            logger.debug(f"回测开仓: {symbol} @ {price:.4f}, 数量={amount:.4f}, 仓位={position.cost:.2f}U")
        except Exception as e:
            logger.debug(f"插入开仓失败: {e}")

    def _check_close_positions(self, window: list, cursor):
        """检查是否需要平仓"""
        to_close = []
        
        for pos_key, pos in list(self.open_positions.items()):
            symbol = pos_key.split('|', 1)[1]
            # 找最近的匹配tick（只查当前platform的窗口）
            matching_ticks = [t for t in window if t['symbol'] == symbol]
            if not matching_ticks:
                continue
            
            latest = matching_ticks[-1]
            
            # 计算当前PnL
            close_price = latest['perp_bid'] if pos.side == 'buy' else latest['perp_ask']
            pnl_result = pos.close(close_price)
            
            # 平仓条件：
            # 1. 有盈利（净利>0.01%）
            # 2. 或者持仓超过60秒（强制止损）
            hold_time = latest['ts'] - pos.timestamp
            should_close = (pnl_result['net_pnl'] > 0 and pnl_result['pnl_pct'] > 0.01) or hold_time > 60
            
            if should_close:
                to_close.append((pos_key, pos, pnl_result, latest))
        
        for pos_key, pos, pnl_result, tick in to_close:
            # 平仓
            try:
                cursor.execute(
                    "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status, position_id) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (tick['ts'], 'backtest', symbol, pos.exchange,
                     'SELL', pnl_result['close_price'], round(pos.amount, 8),
                     pos.cost, pos.cost * pos.fee_rate,
                     pnl_result['net_pnl'], pnl_result['pnl_pct'], 'closed', pos.position_id)
                )
                
                self.total_trades += 1
                if pnl_result['net_pnl'] > 0:
                    self.winning_trades += 1
                self.platform_trades[pos.exchange] += 1
                self.platform_wins[pos.exchange] += (1 if pnl_result['net_pnl'] > 0 else 0)
                self.platform_pnl[pos.exchange] += pnl_result['net_pnl']
                self.platform_balances[pos.exchange] += pnl_result['net_pnl']
                
                # 从持仓中移除
                del self.open_positions[pos_key]
                
                logger.debug(f"回测平仓: {symbol} @ {pnl_result['close_price']:.4f}, PnL={pnl_result['net_pnl']:+.4f}U ({pnl_result['pnl_pct']:+.3f}%)")
                
            except Exception as e:
                logger.debug(f"插入平仓失败: {e}")

    def get_status(self) -> Dict:
        # === 按平台统计回测状态 ===
        platform_stats = {}
        for p in self.platforms:
            p_trades = self.platform_trades[p]
            p_wins = self.platform_wins[p]
            p_pnl = self.platform_pnl[p]
            platform_stats[p] = {
                'balance': self.platform_balances[p],
                'trades': p_trades,
                'wins': p_wins,
                'win_rate': p_wins / max(p_trades, 1) * 100 if p_trades > 0 else 0,
                'pnl': p_pnl,
            }
        
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': self.winning_trades / max(self.total_trades, 1),
            'platform_stats': platform_stats,
            'total_pnl': sum(self.platform_pnl.values()),
        }


class PaperEngine:
    """实时模拟引擎 - 完整交易周期版（真实风控检查）
    铁律：每个平台独立管理余额，互不影响"""

    # 每个平台的初始模拟资金
    PLATFORM_INITIAL_BALANCE = {'bitget': 1000.0, 'htx': 1000.0, 'gate': 1000.0}

    def __init__(self, config: SystemConfig, db_path: str):
        self.config = config
        self.db_path = db_path
        self.running = False
        self.thread = None
        
        # === 按平台独立管理余额 ===
        self.platforms = ['bitget', 'htx', 'gate']
        self.platform_balances: Dict[str, float] = dict(self.PLATFORM_INITIAL_BALANCE)  # {platform: balance}
        self.platform_trades: Dict[str, int] = {p: 0 for p in self.platforms}
        self.platform_wins: Dict[str, int] = {p: 0 for p in self.platforms}
        self.platform_pnl: Dict[str, float] = {p: 0.0 for p in self.platforms}
        
        self.total_trades = 0
        self.winning_trades = 0
        self.open_positions: Dict[str, Position] = {}  # {exchange|symbol: Position}
        # 创建独立的模拟风控管理器，使用模拟余额而非实盘余额
        self.risk_manager = RiskManager(db_path, paper_mode=True, paper_balance=sum(self.platform_balances.values()))
        self.last_save_time = 0

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("📝 模拟引擎启动（完整交易周期版，1000 USDT 初始资金）")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("📝 模拟引擎已停止")

    def _run_loop(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
        cursor = conn.cursor()

        # 加载模拟盘状态（按平台恢复）
        try:
            cursor.execute("SELECT platform, balance FROM simulated_platform_balance")
            for row in cursor.fetchall():
                platform, bal = row
                if platform in self.platform_balances:
                    self.platform_balances[platform] = bal
                    logger.info(f"📝 恢复{platform}模拟盘余额: {bal:.2f} USDT")
        except:
            pass  # 首次运行或表不存在，使用默认值

        # 从数据库恢复未平仓的持仓
        try:
            cursor.execute("""
                SELECT symbol, exchange, side, price, amount, timestamp, status
                FROM engine_trades
                WHERE mode='paper' AND status='opened' AND timestamp > 1000000000
            """)
            for row in cursor.fetchall():
                symbol, exchange, side, price, amount, ts, status = row
                position_id = int(time.time() * 1000)
                position = Position(symbol, exchange, side, price, amount, position_id, ts)
                pos_key = f"{exchange}|{symbol}"
                self.open_positions[pos_key] = position
                logger.info(f"📝 恢复持仓: {symbol} {exchange} {side} @ {price}")
            logger.info(f"📝 恢复了 {len(self.open_positions)} 个持仓")
        except Exception as e:
            logger.warning(f"⚠️ 恢复持仓失败: {e}")

        last_check_ts = 0
        threshold = self.config.execution.spread_pct
        cost = ExecutionEngine.BI_SIDE_COST * 100
        min_net_profit = RiskManager.MIN_NET_PROFIT_PCT

        while self.running:
            try:
                cursor.execute("""
                    SELECT id, timestamp, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct
                    FROM market_data
                    WHERE timestamp > ? AND ABS(spread_pct) < 1.0
                    ORDER BY timestamp DESC LIMIT 100
                """, (last_check_ts,))
                ticks = cursor.fetchall()
                if not ticks:
                    time.sleep(0.5)
                    continue

                last_check_ts = ticks[0][1]

                for tick in ticks:
                    ts, tick_id, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = tick
                    
                    # 严格检查：价差必须>0.17%才能交易
                    if spread_pct < cost + min_net_profit:
                        continue
                    
                    # 调试日志
                    logger.debug(f"[模拟] 检查 {exchange} {symbol} spread={spread_pct:.4f}% perp_ask={perp_ask}")
                    
                    # 执行引擎层检查
                    net_profit_pct = spread_pct - cost
                    if net_profit_pct < self.config.execution.net_profit_pct:
                        continue
                    
                    # 成交概率
                    if random.random() >= self.config.live.fill_rate:
                        continue
                    
                    # 检查是否已有同币种持仓（按exchange隔离）
                    pos_key = f"{exchange}|{symbol}"
                    if pos_key in self.open_positions:
                        # 检查是否需要平仓
                        pos = self.open_positions[pos_key]
                        close_price = perp_bid if pos.side == 'buy' else perp_ask
                        pnl_result = pos.close(close_price)
                        
                        hold_time = ts - pos.timestamp
                        should_close = (pnl_result['net_pnl'] > 0 and pnl_result['pnl_pct'] > 0.01) or hold_time > 60
                        
                        if should_close:
                            # 平仓 - 按平台统计
                            platform = exchange  # exchange已经是'bitget','htx','gate'
                            self.platform_trades[platform] += 1
                            self.total_trades += 1
                            if pnl_result['net_pnl'] > 0:
                                self.platform_wins[platform] += 1
                                self.winning_trades += 1
                            self.platform_pnl[platform] += pnl_result['net_pnl']
                            self.platform_balances[platform] += pnl_result['net_pnl']
                            
                            cursor.execute(
                                "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status) "
                                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                                (ts, 'paper', symbol, exchange, 'SELL', pnl_result['close_price'], 
                                 round(pos.amount, 8), pos.cost, pos.cost * pos.fee_rate,
                                 pnl_result['net_pnl'], pnl_result['pnl_pct'], 'completed')
                            )
                            
                            del self.open_positions[pos_key]
                            
                            if self.total_trades % 10 == 0:
                                win_rate = self.winning_trades / self.total_trades * 100
                                logger.info(f"   模拟盘: {self.total_trades}笔, 胜率{win_rate:.1f}%")
                                for p in self.platforms:
                                    logger.info(f"     {p}: {self.platform_trades[p]}笔, 盈亏{self.platform_pnl[p]:+.2f}U")
                        continue
                    
                    # === 风控检查（按平台余额）===
                    min_notional = PERP_MIN_NOTIONAL.get(exchange, 1.0)
                    platform = exchange  # exchange已经是'bitget','htx','gate'
                    position = min(self.platform_balances[platform] * 0.20, 200)
                    
                    if position < min_notional:
                        continue
                    
                    risk_check = self.risk_manager.check_risk(
                        symbol=symbol,
                        side='buy',
                        position_size_usdt=position,
                        entry_price=perp_ask,
                        stop_loss_price=perp_ask * 1.02,
                        ex_name=exchange
                    )
                    if not risk_check['allowed']:
                        logger.debug(f"模拟风控拒绝: {risk_check['reason']}")
                        continue
                    
                    # === 精度检查 ===
                    amount = position / perp_ask
                    if amount < 1.0:
                        continue
                    
                    # 开仓 - 按平台统计
                    # 使用时间戳生成唯一ID
                    position_id = f"pa_{int(time.time() * 1000)}"
                    position = Position(symbol, exchange, 'buy', perp_ask, amount, position_id, ts)
                    self.open_positions[pos_key] = position
                    self.platform_trades[platform] += 1
                    self.total_trades += 1
                    
                    # 记录到数据库
                    try:
                        cursor.execute(
                            "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status) "
                            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            (ts, 'paper', symbol, exchange, 'BUY', perp_ask, round(amount, 8),
                             position.cost, position.cost * position.fee_rate,
                             0, 0, 'opened')
                        )
                    except Exception as e:
                        logger.debug(f"插入开仓失败: {e}")

                # 每分钟保存状态（按平台）
                now = time.time()
                if now - self.last_save_time > 60:
                    cursor.execute("DELETE FROM simulated_platform_balance")
                    for p, bal in self.platform_balances.items():
                        cursor.execute(
                            "INSERT INTO simulated_platform_balance (platform, balance, updated_at) VALUES (?, ?, ?)",
                            (p, bal, now)
                        )
                    conn.commit()
                    self.last_save_time = now

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"模拟引擎错误: {e}")
                time.sleep(5)

        conn.close()

    def get_status(self) -> Dict:
        # === 按平台统计模拟状态 ===
        platform_stats = {}
        for p in self.platforms:
            p_trades = self.platform_trades[p]
            p_wins = self.platform_wins[p]
            p_pnl = self.platform_pnl[p]
            platform_stats[p] = {
                'balance': self.platform_balances[p],
                'trades': p_trades,
                'wins': p_wins,
                'win_rate': p_wins / max(p_trades, 1) * 100 if p_trades > 0 else 0,
                'pnl': p_pnl,
            }
        
        return {
            'balance': sum(self.platform_balances.values()),
            'total_pnl': sum(self.platform_pnl.values()),
            'total_trades': self.total_trades,
            'win_rate': self.winning_trades / max(self.total_trades, 1),
            'open_positions': len(self.open_positions),
            'platform_stats': platform_stats,
        }


class DualEngineSystem:
    """双引擎系统 - 回测 + 模拟并行运行，不受暂停影响"""

    def __init__(self, config: SystemConfig):
        self.config = config
        self.backtest_engine = BacktestEngine(config, config.data.db_path)
        self.paper_engine = PaperEngine(config, config.data.db_path)

    def start(self):
        self.backtest_engine.start()
        self.paper_engine.start()
        logger.info("=" * 60)
        logger.info("🚀 双引擎系统启动（回测 + 模拟，完整交易周期版）")
        logger.info("=" * 60)

    def stop(self):
        self.backtest_engine.stop()
        self.paper_engine.stop()
        logger.info("🛑 双引擎系统已停止")

    def get_status(self) -> Dict:
        return {
            'backtest': self.backtest_engine.get_status(),
            'paper': self.paper_engine.get_status(),
        }
