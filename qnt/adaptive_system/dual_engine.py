"""
双引擎回测/模拟系统 - 不受暂停影响
- BacktestEngine: 历史数据回放 + 实时追加回测
- PaperEngine: 实时模拟交易，不实际下单
"""
import time
import logging
import sqlite3
import threading
from datetime import datetime
from typing import Dict, List, Optional
import ccxt
import random

from .config import SystemConfig
from .risk_manager import RiskManager
from .execution_engine import ExecutionEngine

logger = logging.getLogger('DualEngine')


class BacktestEngine:
    """历史回测引擎 - 回放 market_data 并追加实时数据"""

    def __init__(self, config: SystemConfig, db_path: str):
        self.config = config
        self.db_path = db_path
        self.running = False
        self.thread = None
        self.last_processed_ts = 0
        self.total_trades = 0
        self.winning_trades = 0

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("📊 回测引擎启动")

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
        logger.info(f"   数据范围: {datetime.fromtimestamp(min_ts).strftime('%m-%d %H:%M')} ~ {datetime.fromtimestamp(max_ts).strftime('%m-%d %H:%M')}")

        # 分批处理
        processed_count = 0
        window = []
        threshold = self.config.execution.spread_pct
        cost = ExecutionEngine.BI_SIDE_COST * 100

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

            # 维护滑动窗口
            window.append({
                'ts': ts, 'exchange': exchange, 'symbol': symbol,
                'spot_bid': spot_bid, 'spot_ask': spot_ask,
                'perp_bid': perp_bid, 'perp_ask': perp_ask,
                'spread': spread_pct
            })

            if len(window) >= 60:
                # 取窗口内绝对价差最大的 tick
                best_tick = max(window, key=lambda x: abs(x['spread']))
                if abs(best_tick['spread']) >= threshold:
                    self._backtest_one(best_tick, window[-1], cursor)
                window = window[-30:]

            processed_count += 1
            if processed_count % 100000 == 0:
                logger.info(f"   已处理 {processed_count} 条, {self.total_trades} 笔交易")

        # 保存进度
        cursor.execute(
            "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (time.time(), 'backtest', 'PROGRESS', 'progress', 'BUY', 0, 0, 0, 0, 0, 0, 'completed')
        )
        conn.commit()

        win_rate = self.winning_trades / max(self.total_trades, 1) * 100
        logger.info(f"✅ 历史回测完成: {processed_count} 条, {self.total_trades} 笔交易, 胜率 {win_rate:.1f}%")

        # 切换到实时模式
        logger.info("📊 切换到实时回测模式...")
        while self.running:
            try:
                cursor.execute("""
                    SELECT timestamp, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct
                    FROM market_data
                    WHERE timestamp > ? AND ABS(spread_pct) < 1.0
                    ORDER BY timestamp DESC LIMIT 1
                """, (self.last_processed_ts,))
                latest = cursor.fetchone()
                if latest:
                    self.last_processed_ts = latest[0]
                    if abs(latest[7]) >= threshold:
                        self._backtest_one_direct(latest, cursor)
                time.sleep(1)
            except Exception as e:
                logger.error(f"实时回测错误: {e}")
                time.sleep(5)

        conn.close()

    def _backtest_one(self, best_tick: dict, execute_tick: dict, cursor):
        """在滑动窗口中执行一次回测"""
        spread_pct = best_tick['spread']
        net_profit_pct = spread_pct - ExecutionEngine.BI_SIDE_COST * 100

        # 只有价差达标且随机命中才模拟交易（70%挂单成功率）
        if random.random() >= 0.7:
            return

        # 固定 10 USDT 仓位（符合各交易所最小金额要求）
        position = 10
        pnl = position * net_profit_pct / 100

        try:
            cursor.execute(
                "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (best_tick['ts'], 'backtest', best_tick['symbol'], best_tick['exchange'],
                 'BUY', best_tick['perp_ask'], 1.0, position * 0.0004, position * 0.0004,
                 pnl, net_profit_pct, 'completed')
            )
            self.total_trades += 1
            if pnl > 0:
                self.winning_trades += 1
            if self.total_trades % 100 == 0:
                win_rate = self.winning_trades / self.total_trades * 100
                logger.info(f"   回测进度: {self.total_trades} 笔, 胜率 {win_rate:.1f}%")
        except Exception as e:
            logger.debug(f"插入交易失败: {e}")

    def _backtest_one_direct(self, tick: tuple, cursor):
        """直接处理实时 tick"""
        ts, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = tick
        net_profit_pct = spread_pct - ExecutionEngine.BI_SIDE_COST * 100

        # 只有价差达标且随机命中才模拟交易（70%挂单成功率）
        if random.random() >= 0.7:
            return

        position = 10
        pnl = position * net_profit_pct / 100

        try:
            cursor.execute(
                "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (ts, 'backtest', symbol, exchange, 'BUY', perp_ask, 1.0,
                 position * 0.0004, position * 0.0004, pnl, net_profit_pct, 'completed')
            )
            self.total_trades += 1
            if pnl > 0:
                self.winning_trades += 1
        except Exception as e:
            logger.debug(f"实时回测插入失败: {e}")

    def get_status(self) -> Dict:
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': self.winning_trades / max(self.total_trades, 1),
        }


class PaperEngine:
    """实时模拟引擎 - 实时 tick 驱动，模拟盘状态持久化"""

    def __init__(self, config: SystemConfig, db_path: str):
        self.config = config
        self.db_path = db_path
        self.running = False
        self.thread = None
        self.paper_balance = 1000.0  # 模拟初始资金
        self.total_trades = 0
        self.winning_trades = 0

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

        # 加载模拟盘状态
        cursor.execute("SELECT balance, total_pnl FROM simulated_balance WHERE id=1")
        row = cursor.fetchone()
        if row:
            self.paper_balance = row[0]
            logger.info(f"📝 恢复模拟盘余额: {self.paper_balance:.2f} USDT")

        last_check_ts = 0
        threshold = self.config.execution.spread_pct
        cost = ExecutionEngine.BI_SIDE_COST * 100

        while self.running:
            try:
                cursor.execute("""
                    SELECT id, timestamp, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct
                    FROM market_data
                    WHERE timestamp > ? AND ABS(spread_pct) < 1.0
                    ORDER BY timestamp DESC LIMIT 10
                """, (last_check_ts,))
                ticks = cursor.fetchall()
                if not ticks:
                    time.sleep(0.5)
                    continue

                last_check_ts = ticks[0][1]

                for tick in ticks:
                    ts, tick_id, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = tick
                    net_profit_pct = spread_pct - cost
                    # 净利多才考虑交易
                    if net_profit_pct < 0.05 or random.random() >= self.config.live.fill_rate:
                        continue

                    position = min(self.paper_balance * 0.10, 100)
                    if position < 10:
                        continue

                    slipage = random.uniform(
                        self.config.live.slipage_mult_min,
                        self.config.live.slipage_mult_max
                    )
                    pnl = position * net_profit_pct / 100 * slipage
                    self.paper_balance += pnl
                    self.total_trades += 1
                    if pnl > 0:
                        self.winning_trades += 1

                    cursor.execute(
                        "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (ts, 'paper', symbol, exchange, 'BUY', perp_ask, 1.0,
                         position * 0.0004, position * 0.0004, pnl, net_profit_pct, 'completed')
                    )

                    if self.total_trades % 50 == 0:
                        logger.info(f"   模拟盘: {self.total_trades}笔, 胜率{self.winning_trades/self.total_trades*100:.1f}%, 余额${self.paper_balance:.2f}")

                # 每分钟保存状态
                if int(time.time()) % 60 < 2:
                    cursor.execute("DELETE FROM simulated_balance")
                    cursor.execute(
                        "INSERT INTO simulated_balance (id, timestamp, balance, total_pnl) VALUES (1, ?, ?, ?)",
                        (time.time(), self.paper_balance, self.paper_balance - 1000.0)
                    )
                    conn.commit()

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"模拟引擎错误: {e}")
                time.sleep(5)

        conn.close()

    def get_status(self) -> Dict:
        return {
            'balance': self.paper_balance,
            'total_pnl': self.paper_balance - 1000.0,
            'total_trades': self.total_trades,
            'win_rate': self.winning_trades / max(self.total_trades, 1),
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
        logger.info("🚀 双引擎系统启动（回测 + 模拟，不受暂停影响）")
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
