"""
双引擎回测/模拟系统 - 双模式回测版
- 模式一：我们的真实成交回测（historical_trades表）
- 模式二：平台公开市场成交回测（market_trades表）
- PaperEngine: 实时模拟交易
"""
import time
import logging
import sqlite3
from .db_utils import get_connection
import threading
import random
from datetime import datetime
from typing import Dict, List, Optional
import ccxt

from .config import SystemConfig
from .risk_manager import RiskManager
from .execution_engine import ExecutionEngine, MIN_COIN_AMOUNT

# 各交易所永续合约最小金额限制
PERP_MIN_NOTIONAL = {'bitget': 5.0, 'htx': 1.0, 'gate': 3.0}

logger = logging.getLogger('DualEngine')


class Position:
    """持仓对象"""
    def __init__(self, symbol, exchange, side, price, amount, position_id, timestamp, spread_pct=None, entry_time=None):
        self.symbol = symbol
        self.exchange = exchange
        self.side = side  # 'buy' or 'sell'
        self.price = price
        self.amount = amount
        self.position_id = position_id
        self.timestamp = timestamp
        self.cost = amount * price
        self.fee_rate = ExecutionEngine.MAKER_FEE_RATE  # 0.06%
        # 2026-09-13 新增：记录开仓时价差，用于分档平仓（价差方向判断）
        self.entry_spread_pct = spread_pct if spread_pct is not None else 0.0
        self.entry_time = entry_time if entry_time is not None else time.time()

    def close(self, close_price):
        """平仓，返回PnL"""
        if self.side == 'buy':
            gross_pnl = (close_price - self.price) * self.amount
        else:
            gross_pnl = (self.price - close_price) * self.amount
        
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
    """双模式回测引擎
    模式一：我们的真实成交分析（historical_trades表）
    模式二：平台公开市场成交回测（market_trades表）"""

    PLATFORM_INITIAL_BALANCE = {'bitget': 1000.0, 'htx': 1000.0, 'gate': 1000.0}

    def __init__(self, config: SystemConfig, db_path: str):
        self.config = config
        self.db_path = db_path
        self.running = False
        self.thread = None
        self.last_processed_ts = 0
        
        self.platforms = ['bitget', 'htx', 'gate']
        self.platform_balances: Dict[str, float] = dict(self.PLATFORM_INITIAL_BALANCE)
        self._bt_counter = 0
        self._pa_counter = 0
        self.platform_trades: Dict[str, int] = {p: 0 for p in self.platforms}
        self.platform_wins: Dict[str, int] = {p: 0 for p in self.platforms}
        self.platform_pnl: Dict[str, float] = {p: 0.0 for p in self.platforms}
        
        self.open_positions: Dict[str, Position] = {}
        self.total_trades = 0
        self.winning_trades = 0
        
        self.risk_manager = RiskManager(db_path, paper_mode=True, paper_balance=sum(self.platform_balances.values()))

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("📊 双模式回测引擎启动")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("📊 回测引擎已停止")

    def _run_loop(self):
        conn = get_connection(self.db_path, check_same_thread=False)
        conn.isolation_level = None  # autocommit，写完立即释放锁
        cursor = conn.cursor()

        # === 模式一：分析我们的真实成交 ===
        self._analyze_historical_trades(cursor)
        
        # === 模式二：回测平台市场成交 ===
        self._backtest_market_trades(cursor)
        
        # === 切换到实时模式 ===
        self._realtime_backtest(cursor)

        conn.close()

    def _analyze_historical_trades(self, cursor):
        """模式一：分析我们的真实成交历史（不交易，只统计）"""
        logger.info("=" * 60)
        logger.info("📊 模式一：分析我们的真实成交历史")
        logger.info("=" * 60)
        
        # 检查是否有历史成交数据
        cursor.execute("SELECT COUNT(*) FROM historical_trades")
        hist_count = cursor.fetchone()[0]
        
        if hist_count == 0:
            logger.info("⚠️ 无历史成交数据")
            return
        
        # 按平台统计
        cursor.execute("""
            SELECT exchange, 
                   COUNT(*) as total,
                   SUM(CASE WHEN side='buy' THEN cost ELSE 0 END) as buy_cost,
                   SUM(CASE WHEN side='sell' THEN cost ELSE 0 END) as sell_cost
            FROM historical_trades
            GROUP BY exchange
        """)
        summary = cursor.fetchall()
        
        logger.info("=== 平台成交统计 ===")
        total_buy = 0
        total_sell = 0
        total_trades = 0
        for row in summary:
            net = row[3] - row[2]  # 卖出 - 买入 = 净盈亏
            logger.info(f"  {row[0]}: {row[1]}笔, 买入{row[2]:.2f}U, 卖出{row[3]:.2f}U, 净盈亏{net:+.2f}U")
            total_trades += row[1]
            total_buy += row[2]   # 累加买入成本
            total_sell += row[3]  # 累加卖出成本
        
        net_pnl = total_sell - total_buy
        pct = net_pnl / total_buy * 100 if total_buy > 0 else 0
        logger.info(f"=== 总净盈亏: {net_pnl:+.2f} USDT ({pct:+.2f}%) ===")
        
        # 按币种统计
        cursor.execute("""
            SELECT symbol, 
                   COUNT(*) as total,
                   SUM(CASE WHEN side='buy' THEN cost ELSE 0 END) as buy_cost,
                   SUM(CASE WHEN side='sell' THEN cost ELSE 0 END) as sell_cost
            FROM historical_trades
            GROUP BY symbol
            ORDER BY total DESC
            LIMIT 10
        """)
        top_symbols = cursor.fetchall()
        
        logger.info("=== 热门币种统计（前10）===")
        for row in top_symbols:
            net = row[3] - row[2]
            logger.info(f"  {row[0]}: {row[1]}笔, 净盈亏{net:+.2f}U")
        
        # 分析结果只记日志，不写入engine_trades（避免污染交易表）
        logger.info(f"📊 模式一完成: {total_trades}笔, 买入{total_buy:.2f}U, 卖出{total_sell:.2f}U, 净盈亏{net_pnl:+.2f}U ({pct:+.2f}%)")

    def _backtest_market_trades(self, cursor):
        """模式二：回测平台公开市场成交（不交易，只统计胜率）"""
        logger.info("=" * 60)
        logger.info("📊 模式二：回测平台市场成交数据")
        logger.info("=" * 60)
        
        # 检查是否有市场成交数据
        cursor.execute("SELECT COUNT(*) FROM market_trades")
        market_count = cursor.fetchone()[0]
        
        if market_count == 0:
            logger.info("⚠️ 无市场成交数据")
            return
        
        # 统计最近24小时市场成交
        since_ts = time.time() - 86400
        cursor.execute("""
            SELECT exchange, symbol, side, COUNT(*) as count,
                   ROUND(SUM(cost), 2) as total_cost
            FROM market_trades
            WHERE timestamp > ?
            GROUP BY exchange, symbol, side
            ORDER BY exchange, count DESC
            LIMIT 50
        """, (since_ts,))
        stats = cursor.fetchall()
        
        logger.info(f"=== 最近24小时市场成交统计（共{market_count}笔）===")
        for row in stats:
            logger.info(f"  {row[0]} {row[1]} {row[2]}: {row[3]}笔, {row[4]}U")
        
        # 计算买卖比例
        cursor.execute("""
            SELECT exchange,
                   SUM(CASE WHEN side='buy' THEN cost ELSE 0 END) as buy_cost,
                   SUM(CASE WHEN side='sell' THEN cost ELSE 0 END) as sell_cost
            FROM market_trades
            WHERE timestamp > ?
            GROUP BY exchange
        """, (since_ts,))
        summary = cursor.fetchall()
        
        logger.info("=== 平台买卖比例 ===")
        for row in summary:
            ratio = row[2] / row[1] * 100 if row[1] > 0 else 0
            logger.info(f"  {row[0]}: 买入{row[1]:.2f}U, 卖出{row[2]:.2f}U, 卖出/买入={ratio:.1f}%")
        
        # 统计结果只记日志，不写入engine_trades
        logger.info(f"✅ 模式二完成，共{market_count}笔市场成交记录")

    def _realtime_backtest(self, cursor):
        """实时回测模式：基于market_data价差信号"""
        logger.info("📊 切换到实时回测模式...")
        
        # 恢复进度
        cursor.execute("SELECT MAX(timestamp) FROM engine_trades WHERE mode='backtest_rt'")
        last_ts_row = cursor.fetchone()[0]
        self.last_processed_ts = last_ts_row or 0

        if self.last_processed_ts > 0:
            logger.info(f"   从 {datetime.fromtimestamp(self.last_processed_ts).strftime('%m-%d %H:%M')} 继续")
        else:
            logger.info("   从头开始回放")

        threshold = self.config.execution.spread_pct
        cost = ExecutionEngine.BI_SIDE_COST
        min_net_profit = RiskManager.MIN_NET_PROFIT_PCT

        check_count = 0
        # 2026-09-21 fix19: forward-window scan. Old logic took max(ts) inside window,
        # so on sparse data the cursor stuck at 09-09 10:18 for 12 days.
        # Correct: process [last, last+300s) then advance cursor by 300s.
        while self.running:
            try:
                cursor.execute("""
                    SELECT timestamp, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct
                    FROM market_data
                    WHERE timestamp > ? AND timestamp <= ? AND spread_pct IS NOT NULL AND ABS(spread_pct) < 1.0
                    ORDER BY timestamp ASC
                    LIMIT 5000
                """, (self.last_processed_ts, self.last_processed_ts + 300))
                window_data = cursor.fetchall()

                # Advance cursor by 300s regardless of whether window had data
                self.last_processed_ts += 300

                if not window_data:
                    # Empty window: if we've caught up to realtime, enter incremental mode
                    cursor.execute("SELECT MAX(timestamp) FROM market_data")
                    md_max = cursor.fetchone()[0]
                    if md_max and self.last_processed_ts >= md_max:
                        logger.info("✅ realtime backtest caught up to latest data, entering incremental mode")
                        time.sleep(30)
                        continue
                    time.sleep(0.1)
                    continue

                # Group by exchange
                by_exchange = {}
                for row in window_data:
                    ex = row[1]
                    if ex not in by_exchange:
                        by_exchange[ex] = []
                    by_exchange[ex].append(row)

                # Process each exchange independently
                for exchange, ticks in by_exchange.items():
                    best_tick = max(ticks, key=lambda x: x[7])
                    ts, ex, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = best_tick

                    # 2026-09-27 A同步（与实盘完全同门槛）：动态门槛=基础门槛+永续自身点差，
                    # 防止浅价差碎单（TIA 0.29%价差 vs 0.55%真实成本的假机会被误放行）
                    _perp_self_spread = 0.0
                    if perp_ask and perp_bid and ((perp_ask + perp_bid) / 2) > 0:
                        _perp_self_spread = max((perp_ask - perp_bid) / ((perp_ask + perp_bid) / 2), 0) * 100
                    if spread_pct >= cost + min_net_profit + _perp_self_spread:
                        self._try_open_position(ticks, cursor)
                        self._check_close_positions(ticks, cursor)

                check_count += 1
                if check_count % 50 == 0:
                    logger.info(f"📈 backtest replay progress: up to "
                                f"{datetime.fromtimestamp(self.last_processed_ts).strftime('%m-%d %H:%M')} "
                                f"(window={len(window_data)} rows)")

                time.sleep(0.05)

            except Exception as e:
                logger.error(f"realtime backtest error: {e}")
                time.sleep(5)
                time.sleep(5)

        conn.close()

    def _try_open_position(self, window: list, cursor):
        """尝试开仓"""
        best_tick = max(window, key=lambda x: abs(x[7]))
        ts, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = best_tick
        
        # 严格检查
        # 2026-09-18 修复：方向必须与实盘铁律同步——
        # market_data.spread_pct 口径=(spot_bid-perp_ask)/perp_ask（现货-永续）：
        #   spread_pct >= +门槛 → 贴水（现货高于永续）→ 开多赌回归
        #   spread_pct <= -门槛 → 升水（永续高于现货）→ 开空赌回归
        # 旧版固定开多且门槛只比正价差 → 回测验证的根本不是实盘策略
        min_spread = (ExecutionEngine.BI_SIDE_COST + RiskManager.MIN_NET_PROFIT_PCT) * 100
        # 2026-09-27 A升级同步（与实盘同门槛）：动态门槛=基础门槛+永续自身买卖点差，
        # 防止浅价差碎单（TIA 0.29%价差 vs 0.55%真实成本的假机会被误放行）
        perp_self_spread_pct = 0.0
        if perp_ask and perp_bid and ((perp_ask + perp_bid) / 2) > 0:
            perp_self_spread_pct = max((perp_ask - perp_bid) / ((perp_ask + perp_bid) / 2), 0) * 100
        if abs(spread_pct) < min_spread + perp_self_spread_pct:
            return
        open_side = 'buy' if spread_pct > 0 else 'sell'
        ref_price = perp_ask if open_side == 'buy' else perp_bid
        if ref_price <= 0:
            return
        
        # 风控检查
        # 2026-09-18 修复：仓位口径与实盘同步——平台余额×20% + 分池headroom逐单扣减
        min_notional = PERP_MIN_NOTIONAL.get(exchange, 1.0)
        platform_cap = self.platform_balances.get(exchange, 1000) * 0.20
        opened = sum(p.cost for k, p in self.open_positions.items()
                     if k.split('|', 1)[0] == exchange)
        headroom = platform_cap - opened
        if headroom <= 0:
            return
        position_size = min(headroom, self.platform_balances.get(exchange, 1000) * 0.20)
        
        if position_size < min_notional:
            return
        
        risk_check = self.risk_manager.check_risk(
            symbol=symbol,
            side=open_side,
            position_size_usdt=position_size,
            entry_price=ref_price,
            stop_loss_price=ref_price * 1.02,
            ex_name=exchange
        )
        if not risk_check['allowed']:
            return
        
        # 精度检查（与实盘 MIN_COIN_AMOUNT 同步）
        amount = position_size / ref_price
        if amount < MIN_COIN_AMOUNT:
            return
        
        # 检查持仓
        pos_key = f"{exchange}|{symbol}"
        if pos_key in self.open_positions:
            return
        
        # 开仓
        position_id = f"bt_{int(time.time() * 1000000)}_{self._bt_counter}"
        self._bt_counter += 1
        position = Position(symbol, exchange, open_side, ref_price, amount, position_id, ts)
        self.open_positions[pos_key] = position
        self.platform_balances[exchange] -= position.cost
        
        try:
            cursor.execute(
                "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status, position_id) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (ts, 'backtest_rt', symbol, exchange,
                 'BUY', perp_ask, round(amount, 8), position.cost, position.cost * position.fee_rate,
                 0, 0, 'opened', position_id)
            )
        except Exception as e:
            logger.debug(f"插入开仓失败: {e}")

    def _check_close_positions(self, window: list, cursor):
        """检查是否需要平仓"""
        to_close = []
        
        # 2026-09-18 修复：平仓口径对齐实盘（只动永续腿 + 止盈/硬止损/90min超时铁律）
        from .execution_engine import SPREAD_POSITION_TIMEOUT, SINGLE_SIDE_STOP_LOSS_PCT
        for pos_key, pos in list(self.open_positions.items()):
            symbol = pos_key.split('|', 1)[1]
            matching_ticks = [t for t in window if t[2] == symbol]
            if not matching_ticks:
                continue
            
            latest = matching_ticks[-1]
            ts, exchange, sym, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = latest
            
            # 实盘口径：多单按 perp_bid 平、空单按 perp_ask 平
            close_price = perp_bid if pos.side == 'buy' else perp_ask
            if close_price <= 0:
                continue
            pnl_result = pos.close(close_price)
            pnl_pct = pnl_result['pnl_pct']  # 价格变动百分比（含符号，未除杠杆）
            
            hard_stop = pnl_pct <= -SINGLE_SIDE_STOP_LOSS_PCT
            take_profit = pnl_result['net_pnl'] >= RiskManager.MIN_NET_PROFIT_PCT * pos.cost * 100 and abs(spread_pct) < abs(pos.spread_pct or 0)
            timed_out = ts - pos.timestamp > SPREAD_POSITION_TIMEOUT
            
            should_close = hard_stop or take_profit or timed_out
            
            if should_close:
                to_close.append((pos_key, pos, pnl_result, latest))
        
        for pos_key, pos, pnl_result, tick in to_close:
            ts, exchange, sym, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = tick
            close_price = spot_bid if pos.side == 'buy' else spot_ask
            
            try:
                cursor.execute(
                    "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status, position_id) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (ts, 'backtest_rt', pos.symbol, exchange,
                     'SELL', close_price, round(pos.amount, 8),
                     pos.cost, pos.cost * pos.fee_rate,
                     pnl_result['net_pnl'], pnl_result['pnl_pct'], 'closed', pos.position_id)
                )
                
                self.total_trades += 1
                if pnl_result['net_pnl'] > 0:
                    self.winning_trades += 1
                self.platform_trades[exchange] += 1
                self.platform_wins[exchange] += (1 if pnl_result['net_pnl'] > 0 else 0)
                self.platform_pnl[exchange] += pnl_result['net_pnl']
                self.platform_balances[exchange] += pnl_result['net_pnl']
                
                del self.open_positions[pos_key]
                
            except Exception as e:
                logger.debug(f"插入平仓失败: {e}")

    def get_status(self) -> Dict:
        platform_stats = {}
        for p in self.platforms:
            platform_stats[p] = {
                'balance': self.platform_balances[p],
                'trades': self.platform_trades[p],
                'wins': self.platform_wins[p],
                'win_rate': self.platform_wins[p] / max(self.platform_trades[p], 1) * 100,
                'pnl': self.platform_pnl[p],
            }
        
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': self.winning_trades / max(self.total_trades, 1),
            'platform_stats': platform_stats,
            'total_pnl': sum(self.platform_pnl.values()),
        }


class PaperEngine:
    """实时模拟引擎"""
    PLATFORM_INITIAL_BALANCE = {'bitget': 1000.0, 'htx': 1000.0, 'gate': 1000.0}

    def __init__(self, config: SystemConfig, db_path: str):
        self.config = config
        self.db_path = db_path
        self.running = False
        self.thread = None
        
        self.platforms = ['bitget', 'htx', 'gate']
        self.platform_balances: Dict[str, float] = dict(self.PLATFORM_INITIAL_BALANCE)
        self._bt_counter = 0
        self._pa_counter = 0
        self.platform_trades: Dict[str, int] = {p: 0 for p in self.platforms}
        self.platform_wins: Dict[str, int] = {p: 0 for p in self.platforms}
        self.platform_pnl: Dict[str, float] = {p: 0.0 for p in self.platforms}
        
        self.total_trades = 0
        self.winning_trades = 0
        self.open_positions: Dict[str, Position] = {}
        self.risk_manager = RiskManager(db_path, paper_mode=True, paper_balance=sum(self.platform_balances.values()))
        self.last_save_time = 0

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("📝 模拟引擎启动（1000 USDT 初始资金）")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("📝 模拟引擎已停止")

    def _run_loop(self):
        conn = get_connection(self.db_path, check_same_thread=False)
        conn.isolation_level = None  # autocommit，写完立即释放锁
        cursor = conn.cursor()

        # 加载状态
        try:
            cursor.execute("SELECT platform, balance FROM simulated_platform_balance")
            for row in cursor.fetchall():
                platform, bal = row
                if platform in self.platform_balances:
                    self.platform_balances[platform] = bal
        except:
            pass

        try:
            cursor.execute("""
                SELECT symbol, exchange, side, price, amount, timestamp, status
                FROM engine_trades
                WHERE mode='paper' AND status='opened'
            """)
            for row in cursor.fetchall():
                symbol, exchange, side, price, amount, ts, status = row
                position_id = f"pa_{int(time.time() * 1000000)}"
                position = Position(symbol, exchange, side, price, amount, position_id, ts)
                pos_key = f"{exchange}|{symbol}"
                self.open_positions[pos_key] = position
        except:
            pass

        last_check_ts = 0
        cost_pct = ExecutionEngine.BI_SIDE_COST * 100  # 0.16%
        min_net_profit_pct = RiskManager.MIN_NET_PROFIT_PCT * 100  # 0.10%
        # 2026-09-13 铁律：模拟盘开仓门槛与实盘同步 = 0.16% 成本 + 0.10% 净利 = 0.26%
        entry_threshold = cost_pct + min_net_profit_pct
        # 2026-09-13 铁律：模拟盘仓位与实盘同步 = 20% 平台余额
        position_ratio = 0.20
        from .execution_engine import SINGLE_SIDE_STOP_LOSS_PCT, SPREAD_POSITION_TIMEOUT
        hard_stop_pct = SINGLE_SIDE_STOP_LOSS_PCT * 100  # 0.15%（标的价格口径，与实盘模块级常量同步，2026-09-13 澄清）
        timeout_sec = SPREAD_POSITION_TIMEOUT  # 5400s（模块级常量，与实盘同步）
        # 2026-09-13 铁律：模拟盘拉黑名单/白名单与实盘同步
        # 2026-09-13修复：BLACKLIST_SYMBOLS/SINGLE_SIDE_STOP_LOSS_PCT 是模块级常量
        #（execution_engine.py:129/137），不是类属性，旧写法 getattr(类) 永远拿到空集
        from .execution_engine import BLACKLIST_SYMBOLS as _BL
        blacklist = set(_BL)
        
        while self.running:
            try:
                cursor.execute("""
                    SELECT id, timestamp, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct
                    FROM market_data
                    WHERE timestamp > ? AND ABS(spread_pct) < 1.0
                    ORDER BY timestamp ASC LIMIT 500
                """, (last_check_ts,))
                ticks = cursor.fetchall()
                if not ticks:
                    time.sleep(0.5)
                    continue

                last_check_ts = ticks[-1][1]

                for tick in ticks:
                    ts, tick_id, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = tick
                    
                    # 2026-09-13：拉黑名单跳过（与实盘同步）
                    if symbol in blacklist:
                        continue

                    # 2026-09-13：开仓门槛与实盘同步（价差 >= 0.26%）
                    # 2026-09-13修复：market_data.spread_pct 是小数口径（0.0026=0.26%），
                    # entry_threshold 是百分比口径（0.26），两者必须同口径比较
                    # （历史 bug：0.0026 < 0.26 恒真，模拟盘永远开不了仓，0笔攒够4小时）
                    # 2026-09-18 修复：方向必须与实盘同步——实盘策略铁律是
                    #   永续价>现货价(升水) → 开空赌回归；永续价<现货价(贴水) → 开多赌回归。
                    # market_data.spread_pct 口径=(spot_bid-perp_ask)/perp_ask（现货-永续），
                    # 与实盘 signed_spread(永续-现货) 符号相反：
                    #   spread_pct >= +门槛 → 贴水(现货高于永续) → 开多
                    #   spread_pct <= -门槛 → 升水(永续高于现货) → 开空
                    # 旧版只开多单且只在升水(>=+门槛)开=纯逆势单，模拟盘验证的根本不是实盘策略
                    spread_pct_abs = abs(spread_pct) * 100
                    if spread_pct_abs < entry_threshold:
                        continue
                    open_side = 'buy' if spread_pct > 0 else 'sell'

                    pos_key = f"{exchange}|{symbol}"
                    if pos_key in self.open_positions:
                        pos = self.open_positions[pos_key]
                        # 当前价差（与实盘 _check_spread_positions 同口径：perp_mid vs spot_mid）
                        spot_mid = (spot_bid + spot_ask) / 2
                        perp_mid = (perp_bid + perp_ask) / 2
                        cur_spread = ((perp_mid - spot_mid) / spot_mid * 100) if spot_mid > 0 else 0
                        age = ts - pos.entry_time
                        side = pos.side
                        
                        # 毛盈亏（保证金口径，与实盘一致：(entry - perp_mid)/entry * 100）
                        entry_price = pos.price
                        if side == 'sell':
                            pnl_pct = ((entry_price - perp_mid) / entry_price * 100) if entry_price > 0 else 0
                        else:
                            pnl_pct = ((perp_mid - entry_price) / entry_price * 100) if entry_price > 0 else 0
                        net = pnl_pct - cost_pct
                        
                        # 价差方向判断（空单赌升水回归：价差缩小=回归中；多单赌贴水回归：价差增大=回归中）
                        spread_shrinking = (side == 'sell' and cur_spread < pos.entry_spread_pct) or \
                                           (side == 'buy' and cur_spread > pos.entry_spread_pct)
                        
                        # 2026-09-13 分档平仓（与实盘优先级一致）：硬止损 > 止盈(价差回归中) > 价差回归到目标线 > 90分钟超时兜底
                        hard_stop = pnl_pct <= -hard_stop_pct
                        take_profit = net >= min_net_profit_pct and spread_shrinking
                        let_profit_run = net >= min_net_profit_pct and not spread_shrinking
                        converged_and_profit = (not spread_shrinking) and net > 0
                        timed_out = age >= timeout_sec
                        
                        # 2026-09-18 修复：超时单无条件平仓（与实盘同步：到90分钟没回归→按盈亏方向平）。
                        # 旧写法 (timed_out and net > 0) 让亏损超时单永远挂死，与实盘风控铁律不同步
                        should_close = hard_stop or take_profit or timed_out
                        
                        if should_close:
                            close_price = perp_mid
                            pnl_result = pos.close(close_price)
                            
                            if hard_stop:
                                reason = f'硬止损{pnl_pct:+.2f}%'
                            elif take_profit:
                                reason = f'净利{net:+.2f}%达标+价差回归中，止盈'
                            else:
                                # 超时：浮盈记兜底平仓，浮亏记超时止损（与实盘口径一致）
                                reason = (f'超时{int(age//60)}分钟兜底({net:+.2f}%)' if net > 0
                                          else f'超时{int(age//60)}分钟止损({net:+.2f}%)')
                            
                            platform = exchange
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
                                (ts, 'paper', symbol, exchange, 'SELL' if side == 'buy' else 'BUY', close_price,
                                 round(pos.amount, 8), pos.cost, pos.cost * pos.fee_rate,
                                 pnl_result['net_pnl'], pnl_result['pnl_pct'], 'completed')
                            )
                            
                            del self.open_positions[pos_key]
                            
                            logger.info(f"🏁 模拟盘 {exchange} {symbol} {reason}: 净利={pnl_result['pnl_pct']:+.4f}% → 已平仓")
                            if self.total_trades % 10 == 0:
                                win_rate = self.winning_trades / self.total_trades * 100
                                logger.info(f"   模拟盘: {self.total_trades}笔, 胜率{win_rate:.1f}%")
                        
                        # 让利润跑：净利达标但价差还在扩大 → 不平，继续持有（记录数据点）
                        if let_profit_run and self.total_trades % 50 == 0:
                            logger.info(f"⏳ 模拟盘 {exchange} {symbol} 净利{net:+.2f}%达标但价差扩大中，继续持有让利润跑")
                        continue
                    
                    # 2026-09-13 铁律：仓位 = 平台余额 × 20%（与实盘同步，不再用 15%）
                    # 2026-09-18 修复：分池 headroom 逐单扣减（与实盘一致）——
                    # 本平台已开保证金合计 ≤ 平台余额×20%，本笔 = min(原公式, 剩余名额)
                    min_notional = PERP_MIN_NOTIONAL.get(exchange, 1.0)
                    platform = exchange
                    position = self.platform_balances[platform] * position_ratio
                    platform_cap = self.platform_balances[platform] * position_ratio
                    opened = sum(p.cost for k, p in self.open_positions.items()
                                 if k.split('|')[0] == platform)
                    headroom = platform_cap - opened
                    if headroom <= 0:
                        continue
                    if position > headroom:
                        position = headroom
                    if position < min_notional:
                        continue
                    
                    ref_price = perp_ask if open_side == 'buy' else perp_bid
                    risk_check = self.risk_manager.check_risk(
                        symbol=symbol,
                        side=open_side,
                        position_size_usdt=position,
                        entry_price=ref_price,
                        stop_loss_price=ref_price * (1 - 0.02 if open_side == 'sell' else 1.02) if open_side == 'sell' else ref_price * 1.02,
                        ex_name=exchange
                    )
                    if not risk_check['allowed']:
                        continue
                    
                    amount = position / ref_price if ref_price > 0 else 0
                    if amount < MIN_COIN_AMOUNT:
                        continue
                    
                    position_id = f"pa_{int(time.time() * 1000000)}_{self._pa_counter}"
                    self._pa_counter += 1
                    # 2026-09-13：记录开仓时价差，供后续分档平仓判断价差方向
                    # 2026-09-18：方向与实盘同步（贴水开多/升水开空），并记录带符号的入口价差百分比
                    entry_spread_signed = -spread_pct * 100 if open_side == 'buy' else spread_pct * 100
                    position = Position(symbol, exchange, open_side,
                                        perp_ask if open_side == 'buy' else perp_bid,
                                        amount, position_id, ts,
                                        spread_pct=entry_spread_signed, entry_time=ts)
                    self.open_positions[pos_key] = position
                    self.platform_trades[platform] += 1
                    self.total_trades += 1
                    
                    logger.info(f"📈 模拟盘开仓 {exchange} {symbol} BUY @{perp_ask:.4f} 数量={amount:.4f} 仓位={position:.2f}U 价差={spread_pct:.3f}% 预期净利={spread_pct - cost_pct:.3f}%")
                    
                    try:
                        cursor.execute(
                            "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status) "
                            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            (ts, 'paper', symbol, exchange, 'BUY', perp_ask, round(amount, 8),
                             position.cost, position.cost * position.fee_rate,
                             0, 0, 'opened')
                        )
                        # 2026-09-13：autocommit（isolation_level=None）下必须手动 COMMIT，
                        # 否则 INSERT 一直滞留在内存事务里，重启即丢，外部查库永远是 0 笔
                        cursor.connection.commit()
                    except Exception as e:
                        logger.warning(f"模拟盘开仓写库失败 {exchange} {symbol}: {e}")

                now = time.time()
                if now - self.last_save_time > 60:
                    cursor.execute("DELETE FROM simulated_platform_balance")
                    for p, bal in self.platform_balances.items():
                        cursor.execute(
                            "INSERT INTO simulated_platform_balance (platform, balance, updated_at) VALUES (?, ?, ?)",
                            (p, bal, now)
                        )
                    cursor.connection.commit()
                    self.last_save_time = now

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"模拟引擎错误: {e}")
                time.sleep(5)

        conn.close()

    def get_status(self) -> Dict:
        platform_stats = {}
        for p in self.platforms:
            platform_stats[p] = {
                'balance': self.platform_balances[p],
                'trades': self.platform_trades[p],
                'wins': self.platform_wins[p],
                'win_rate': self.platform_wins[p] / max(self.platform_trades[p], 1) * 100 if self.platform_trades[p] > 0 else 0,
                'pnl': self.platform_pnl[p],
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
    """双引擎系统 - 双模式回测 + 模拟并行"""

    def __init__(self, config: SystemConfig):
        self.config = config
        self.backtest_engine = BacktestEngine(config, config.data.db_path)
        self.paper_engine = PaperEngine(config, config.data.db_path)

    def start(self):
        self.backtest_engine.start()
        self.paper_engine.start()
        logger.info("=" * 60)
        logger.info("🚀 双模式回测系统启动")
        logger.info("   模式一：分析历史成交（historical_trades）")
        logger.info("   模式二：回测市场成交（market_trades）")
        logger.info("   模拟盘：实时验证策略")
        logger.info("=" * 60)

    def stop(self):
        self.backtest_engine.stop()
        self.paper_engine.stop()
        logger.info("🛑 双模式回测系统已停止")

    def get_status(self) -> Dict:
        return {
            'backtest': self.backtest_engine.get_status(),
            'paper': self.paper_engine.get_status(),
        }
