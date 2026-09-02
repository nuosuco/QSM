"""
双引擎回测/模拟系统 - 双模式回测版
- 模式一：我们的真实成交回测（historical_trades表）
- 模式二：平台公开市场成交回测（market_trades表）
- PaperEngine: 实时模拟交易
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
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
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
        for row in summary:
            net = row[2] - row[1]
            logger.info(f"  {row[0]}: {row[1]}笔, 买入{row[2]:.2f}U, 卖出{row[3]:.2f}U, 净盈亏{net:+.2f}U")
            total_buy += row[1]
            total_sell += row[2]
        
        net_pnl = total_sell - total_buy
        logger.info(f"=== 总净盈亏: {net_pnl:+.2f} USDT ({net_pnl/total_buy*100:.2f}%) ===")
        
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
        
        # 保存分析结果
        cursor.execute("""
            INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status)
            VALUES (?, 'backtest_hist', 'ANALYSIS', 'all', 'STATS', 0, 0, 0, 0, ?, ?, 'completed')
        """, (time.time(), net_pnl, net_pnl/total_buy*100 if total_buy > 0 else 0))
        conn.commit()

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
        
        # 保存统计结果
        cursor.execute("""
            INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status)
            VALUES (?, 'backtest_market', 'MARKET_STATS', 'all', 'STATS', 0, 0, 0, 0, ?, ?, 'completed')
        """, (time.time(), market_count, 0))
        conn.commit()
        
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
        cost = ExecutionEngine.BI_SIDE_COST * 100
        min_net_profit = RiskManager.MIN_NET_PROFIT_PCT

        check_count = 0
        while self.running:
            try:
                # 查询最近5分钟数据
                window_start = self.last_processed_ts - 300
                cursor.execute("""
                    SELECT timestamp, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct
                    FROM market_data
                    WHERE timestamp > ? AND spread_pct IS NOT NULL AND ABS(spread_pct) < 1.0
                    ORDER BY timestamp DESC
                    LIMIT 100
                """, (window_start,))
                window_data = cursor.fetchall()
                
                if not window_data:
                    time.sleep(1)
                    continue
                
                # 更新最后处理时间
                self.last_processed_ts = max(row[0] for row in window_data)
                
                # 按exchange分组
                by_exchange = {}
                for row in window_data:
                    ex = row[1]
                    if ex not in by_exchange:
                        by_exchange[ex] = []
                    by_exchange[ex].append(row)
                
                # 每个exchange独立处理
                for exchange, ticks in by_exchange.items():
                    # 找最大价差
                    best_tick = max(ticks, key=lambda x: x[7])
                    ts, ex, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = best_tick
                    
                    if spread_pct >= cost + min_net_profit:
                        # 执行回测逻辑
                        self._try_open_position(ticks, cursor)
                        self._check_close_positions(ticks, cursor)
                
                check_count += 1
                if check_count % 100 == 0:
                    logger.debug(f"[实时回测] 检查#{check_count}, 窗口内{len(window_data)}条, 门槛={cost+min_net_profit:.2f}%")
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"实时回测错误: {e}")
                time.sleep(5)

        conn.close()

    def _try_open_position(self, window: list, cursor):
        """尝试开仓"""
        best_tick = max(window, key=lambda x: abs(x[7]))
        ts, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = best_tick
        
        # 严格检查
        min_spread = (ExecutionEngine.BI_SIDE_COST + RiskManager.MIN_NET_PROFIT_PCT) * 100
        if spread_pct < min_spread:
            return
        
        # 风控检查
        min_notional = PERP_MIN_NOTIONAL.get(exchange, 1.0)
        position = min(self.platform_balances.get(exchange, 1000) * 0.20, 200)
        
        if position < min_notional:
            return
        
        risk_check = self.risk_manager.check_risk(
            symbol=symbol,
            side='buy',
            position_size_usdt=position,
            entry_price=perp_ask,
            stop_loss_price=perp_ask * 1.02,
            ex_name=exchange
        )
        if not risk_check['allowed']:
            return
        
        # 精度检查
        amount = position / perp_ask
        if amount < 1.0:
            return
        
        # 检查持仓
        pos_key = f"{exchange}|{symbol}"
        if pos_key in self.open_positions:
            return
        
        # 开仓
        position_id = f"bt_{int(time.time() * 1000000)}_{self._bt_counter}"
        self._bt_counter += 1
        position = Position(symbol, exchange, 'buy', perp_ask, amount, position_id, ts)
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
        
        for pos_key, pos in list(self.open_positions.items()):
            symbol = pos_key.split('|', 1)[1]
            matching_ticks = [t for t in window if t[2] == symbol]
            if not matching_ticks:
                continue
            
            latest = matching_ticks[-1]
            ts, exchange, sym, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = latest
            
            close_price = spot_bid if pos.side == 'buy' else spot_ask
            pnl_result = pos.close(close_price)
            
            hold_time = ts - pos.timestamp
            should_close = (pnl_result['net_pnl'] > 0 and pnl_result['pnl_pct'] > 0.01) or hold_time > 60
            
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
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30)
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
                    
                    if spread_pct < cost + min_net_profit:
                        continue
                    
                    net_profit_pct = spread_pct - cost
                    if net_profit_pct < self.config.execution.net_profit_pct:
                        continue
                    
                    if random.random() >= self.config.live.fill_rate:
                        continue
                    
                    pos_key = f"{exchange}|{symbol}"
                    if pos_key in self.open_positions:
                        pos = self.open_positions[pos_key]
                        close_price = spot_bid if pos.side == 'buy' else spot_ask
                        pnl_result = pos.close(close_price)
                        
                        hold_time = ts - pos.timestamp
                        should_close = (pnl_result['net_pnl'] > 0 and pnl_result['pnl_pct'] > 0.01) or hold_time > 60
                        
                        if should_close:
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
                                (ts, 'paper', symbol, exchange, 'SELL', pnl_result['close_price'], 
                                 round(pos.amount, 8), pos.cost, pos.cost * pos.fee_rate,
                                 pnl_result['net_pnl'], pnl_result['pnl_pct'], 'completed')
                            )
                            
                            del self.open_positions[pos_key]
                            
                            if self.total_trades % 10 == 0:
                                win_rate = self.winning_trades / self.total_trades * 100
                                logger.info(f"   模拟盘: {self.total_trades}笔, 胜率{win_rate:.1f}%")
                        continue
                    
                    min_notional = PERP_MIN_NOTIONAL.get(exchange, 1.0)
                    platform = exchange
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
                        continue
                    
                    amount = position / perp_ask
                    if amount < 1.0:
                        continue
                    
                    position_id = f"pa_{int(time.time() * 1000000)}_{self._pa_counter}"
                    self._pa_counter += 1
                    position = Position(symbol, exchange, 'buy', perp_ask, amount, position_id, ts)
                    self.open_positions[pos_key] = position
                    self.platform_trades[platform] += 1
                    self.total_trades += 1
                    
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
