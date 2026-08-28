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
        """启动回测引擎"""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("📊 回测引擎启动")
        
    def stop(self):
        """停止回测引擎"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("📊 回测引擎已停止")
    
    def _run_loop(self):
        """主循环 - 先回放历史数据，再监听实时增量"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        # 1. 回放历史数据（只处理未被回测过的数据）
        logger.info("📊 开始回放历史数据...")
        
        # 找最后处理的 timestamp
        cursor.execute("SELECT MAX(end_timestamp) FROM engine_trades WHERE mode='backtest'")
        last_ts_row = cursor.fetchone()[0]
        self.last_processed_ts = last_ts_row or 0
        
        if self.last_processed_ts > 0:
            logger.info(f"   从 {datetime.fromtimestamp(self.last_processed_ts).strftime('%m-%d %H:%M')} 继续")
        else:
            logger.info("   从头开始回放")
        
        # 获取历史数据范围
        cursor.execute("""
            SELECT MIN(timestamp), MAX(timestamp) 
            FROM market_data 
            WHERE spread_pct IS NOT NULL AND ABS(spread_pct) < 1.0
        """)
        min_ts, max_ts = cursor.fetchone()
        
        if not min_ts or not max_ts:
            logger.warning("⚠️ 没有可用的 market_data")
            conn.close()
            return
        
        logger.info(f"   数据范围: {datetime.fromtimestamp(min_ts).strftime('%m-%d %H:%M')} ~ {datetime.fromtimestamp(max_ts).strftime('%m-%d %H:%M')}")
        
        # 分批处理历史数据（每批 10000 条）
        batch_size = 10000
        processed_count = 0
        window = []
        
        cursor.execute("""
            SELECT timestamp, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct
            FROM market_data
            WHERE timestamp > ? AND spread_pct IS NOT NULL AND ABS(spread_pct) < 1.0
            ORDER BY timestamp ASC
        """, (self.last_processed_ts,))
        
        rows = cursor.fetchall()
        logger.info(f"   待处理行数: {len(rows)}")
        
        for row in rows:
            if not self.running:
                break
            
            ts, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = row
            
            # 更新最后处理时间
            self.last_processed_ts = max(self.last_processed_ts, ts)
            
            # 维护滑动窗口（最近 60 个 tick）
            window.append({
                'ts': ts,
                'exchange': exchange,
                'symbol': symbol,
                'spot_bid': spot_bid,
                'spot_ask': spot_ask,
                'perp_bid': perp_bid,
                'perp_ask': perp_ask,
                'spread': spread_pct
            })
            
            # 窗口满 60 条时进行回测
            if len(window) >= 60:
                # 用前 59 条生成信号，最后 1 条执行
                self._backtest_window(window[:-1], window[-1], cursor)
                window = window[-30:]  # 保留最近 30 条
            
            processed_count += 1
            if processed_count % 100000 == 0:
                logger.info(f"   已处理 {processed_count} 条...")
        
        # 保存进度
        cursor.execute("""
            INSERT OR REPLACE INTO engine_trades 
            (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status)
            VALUES (?, 'backtest', 'PROGRESS', ?, ?, ?, ?, ?, ?, ?, 'completed')
        """, (time.time(), 'backtest_progress', 0, self.total_trades, 0, 0, self.winning_trades, 
              self.winning_trades/max(self.total_trades, 1)*100))
        conn.commit()
        
        logger.info(f"✅ 历史回测完成: {processed_count} 条, {self.total_trades} 笔交易, 胜率 {self.winning_trades/max(self.total_trades,1)*100:.1f}%")
        
        # 2. 监听实时增量数据（每秒检查一次）
        logger.info("📊 切换到实时回测模式...")
        
        while self.running:
            try:
                cursor.execute("""
                    SELECT id, timestamp, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct
                    FROM market_data
                    WHERE timestamp > ? AND ABS(spread_pct) < 1.0
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (self.last_processed_ts,))
                
                latest = cursor.fetchone()
                if latest:
                    self.last_processed_ts = latest[1]
                    # 触发一次回测
                    self._backtest_single(latest, cursor)
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"实时回测错误: {e}")
                time.sleep(5)
        
        conn.close()
    
    def _backtest_window(self, window: List[Dict], execute_tick: Dict, cursor: sqlite3.Cursor):
        """在滑动窗口中执行一次回测"""
        # 找窗口内最大价差的 tick
        best_tick = max(window, key=lambda x: abs(x['spread']))
        
        if abs(best_tick['spread']) < self.config.execution.spread_pct:
            return  # 未达阈值
        
        # 模拟交易（Post-Only 做市策略）
        spread_pct = best_tick['spread']
        net_profit_pct = spread_pct - ExecutionEngine.BI_SIDE_COST * 100
        
        if net_profit_pct <= 0:
            return
        
        # 随机模拟：假设能挂单成功
        import random
        success_prob = 0.7  # 70% 挂单成功率
        
        if random.random() < success_prob:
            # 模拟成交
            position = 10  # 固定 10 USDT 仓位
            pnl = position * net_profit_pct / 100
            is_win = pnl > 0
            
            cursor.execute("""
                INSERT INTO engine_trades 
                (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status)
                VALUES (?, 'backtest', ?, ?, 'BUY', ?, ?, ?, ?, ?, ?, 'completed')
            """, (
                best_tick['ts'],
                best_tick['symbol'],
                best_tick['exchange'],
                best_tick['perp_last'] or best_tick['spot_last'],
                1.0,
                position,
                position * 0.0004,
                position * 0.0004,
                pnl,
                net_profit_pct,
            ))
            
            self.total_trades += 1
            if is_win:
                self.winning_trades += 1
            
            if self.total_trades % 100 == 0:
                logger.info(f"   回测进度: {self.total_trades} 笔, 胜率 {self.winning_trades/self.total_trades*100:.1f}%")
    
    def _backtest_single(self, tick: tuple, cursor: sqlite3.Cursor):
        """处理单条实时 tick"""
        ts, tick_id, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = tick
        
        if abs(spread_pct) < self.config.execution.spread_pct:
            return
        
        net_profit_pct = spread_pct - ExecutionEngine.BI_SIDE_COST * 100
        
        if net_profit_pct <= 0:
            return
        
        import random
        if random.random() < 0.7:
            position = 10
            pnl = position * net_profit_pct / 100
            
            cursor.execute("""
                INSERT INTO engine_trades 
                (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status)
                VALUES (?, 'backtest', ?, ?, 'BUY', ?, ?, ?, ?, ?, ?, 'completed')
            """, (ts, symbol, exchange, perp_ask or spot_ask, 1.0, position, 
                  position * 0.0004, position * 0.0004, pnl, net_profit_pct))
            
            self.total_trades += 1
            if pnl > 0:
                self.winning_trades += 1
    
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
        self.paper_balance = 1000.0  # 模拟初始资金 1000 USDT
        self.open_orders = {}
        
    def start(self):
        """启动模拟引擎"""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("📝 模拟引擎启动（1000 USDT 初始资金）")
    
    def stop(self):
        """停止模拟引擎"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("📝 模拟引擎已停止")
    
    def _run_loop(self):
        """主循环 - 监听实时 tick 并模拟交易"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        # 加载模拟盘状态
        cursor.execute("SELECT balance, total_pnl FROM simulated_balance WHERE id=1")
        row = cursor.fetchone()
        if row:
            self.paper_balance = row[0]
            logger.info(f"📝 恢复模拟盘余额: {self.paper_balance:.2f} USDT")
        
        last_check_ts = 0
        
        while self.running:
            try:
                # 获取最新 tick
                cursor.execute("""
                    SELECT id, timestamp, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct
                    FROM market_data
                    WHERE timestamp > ? AND ABS(spread_pct) < 1.0
                    ORDER BY timestamp DESC
                    LIMIT 5
                """, (last_check_ts,))
                
                ticks = cursor.fetchall()
                if not ticks:
                    time.sleep(1)
                    continue
                
                last_check_ts = ticks[-1][1]
                
                for tick in ticks:
                    ts, tick_id, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct = tick
                    
                    # 检查价差机会
                    if abs(spread_pct) < self.config.execution.spread_pct:
                        continue
                    
                    # 模拟执行（不做市，直接追价差）
                    self._simulate_trade(exchange, symbol, spread_pct, ts, cursor)
                
                # 定期保存状态
                if int(time.time()) % 60 == 0:
                    self._save_balance(cursor)
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"模拟引擎错误: {e}")
                time.sleep(5)
        
        conn.close()
    
    def _simulate_trade(self, exchange: str, symbol: str, spread_pct: float, ts: float, cursor: sqlite3.Cursor):
        """模拟一次交易"""
        net_profit_pct = spread_pct - ExecutionEngine.BI_SIDE_COST * 100
        
        if net_profit_pct <= 0.05:  # 至少 0.05% 净利才模拟
            return
        
        # 模拟仓位（总资金的 10%）
        position = self.paper_balance * 0.10
        if position < 10:  # 最小 10 USDT
            return
        
        # 模拟成交（90% 成功率）
        import random
        if random.random() > 0.9:
            return
        
        # 计算 PnL（正负随机）
        pnl_base = position * net_profit_pct / 100
        pnl = pnl_base * random.uniform(0.5, 1.5)  # 波动 ±50%
        
        # 记录交易
        cursor.execute("""
            INSERT INTO engine_trades
            (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status)
            VALUES (?, 'paper', ?, ?, 'BUY', ?, ?, ?, ?, ?, ?, 'completed')
        """, (ts, symbol, exchange, 0, position, position * 0.0004, position * 0.0004, pnl, net_profit_pct))
        
        self.paper_balance += pnl
        
        if int(pnl) != 0:
            direction = "📈" if pnl > 0 else "📉"
            logger.info(f"   {direction} {exchange} {symbol}: 模拟 {direction} {pnl:+.2f} USDT (净利 {net_profit_pct:.3f}%)")
    
    def _save_balance(self, cursor: sqlite3.Cursor):
        """保存模拟盘状态"""
        cursor.execute("DELETE FROM simulated_balance")
        cursor.execute("""
            INSERT INTO simulated_balance (id, timestamp, balance, total_pnl)
            VALUES (1, ?, ?, ?)
        """, (time.time(), self.paper_balance, self.paper_balance - 1000.0))
        conn = sqlite3.connect(self.db_path)
        conn.commit()
        conn.close()
    
    def get_status(self) -> Dict:
        return {
            'balance': self.paper_balance,
            'total_pnl': self.paper_balance - 1000.0,
        }


class DualEngineSystem:
    """双引擎系统 - 回测 + 模拟并行运行，不受暂停影响"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.backtest_engine = BacktestEngine(config, config.data.db_path)
        self.paper_engine = PaperEngine(config, config.data.db_path)
        
    def start(self):
        """启动双引擎"""
        self.backtest_engine.start()
        self.paper_engine.start()
        logger.info("=" * 60)
        logger.info("🚀 双引擎系统启动（回测 + 模拟，不受暂停影响）")
        logger.info("=" * 60)
    
    def stop(self):
        """停止双引擎"""
        self.backtest_engine.stop()
        self.paper_engine.stop()
        logger.info("🛑 双引擎系统已停止")
    
    def get_status(self) -> Dict:
        return {
            'backtest': self.backtest_engine.get_status(),
            'paper': self.paper_engine.get_status(),
        }
