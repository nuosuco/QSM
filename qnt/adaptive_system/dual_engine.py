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
    """历史回测引擎 - 完整交易周期版（真实BUY+SELL配对）"""

    def __init__(self, config: SystemConfig, db_path: str):
        self.config = config
        self.db_path = db_path
        self.running = False
        self.thread = None
        self.last_processed_ts = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.open_positions: Dict[str, Position] = {}  # {symbol: Position}
        self.paper_balance = 1000.0  # 模拟初始资金
        # 创建独立的模拟风控管理器，使用模拟余额而非实盘余额
        self.risk_manager = RiskManager(db_path, paper_mode=True, paper_balance=self.paper_balance)

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

        # 分批处理
        processed_count = 0
        window = []
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

            # 维护滑动窗口（最近30秒的数据）
            window.append({
                'ts': ts, 'exchange': exchange, 'symbol': symbol,
                'spot_bid': spot_bid, 'spot_ask': spot_ask,
                'perp_bid': perp_bid, 'perp_ask': perp_ask,
                'spread': spread_pct
            })

            # 清理超过30秒的旧数据
            while window and ts - window[0]['ts'] > 30:
                window.pop(0)

            if len(window) < 5:
                continue

            # 检查是否有开仓机会
            if spread_pct >= threshold and spread_pct >= cost + min_net_profit:
                self._try_open_position(window, cursor)

            # 检查是否需要平仓
            self._check_close_positions(window, cursor)

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
        total_pnl = self.paper_balance - 1000.0
        logger.info(f"✅ 历史回测完成: {processed_count} 条, {self.total_trades} 笔完整交易, 胜率 {win_rate:.1f}%, 总盈亏 {total_pnl:.2f}U")

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
                    
                    if spread_pct >= threshold and spread_pct >= cost + min_net_profit:
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
        
        # 严格的成本检查
        if spread_pct < ExecutionEngine.BI_SIDE_COST * 100 + RiskManager.MIN_NET_PROFIT_PCT:
            logger.debug(f"[回测] 跳过: 价差{spread_pct:.4f}% < 成本线{ExecutionEngine.BI_SIDE_COST*100:.2f}%+净利{RiskManager.MIN_NET_PROFIT_PCT*100:.2f}%")
            return
        
        # 风控检查
        risk_check = self.risk_manager.check_risk(
            symbol=symbol,
            side='buy',
            position_size_usdt=self.paper_balance * 0.20,
            entry_price=best_tick['perp_ask'],
            stop_loss_price=best_tick['perp_ask'] * 1.02,
            ex_name=exchange
        )
        if not risk_check['allowed']:
            logger.debug(f"[回测] 风控拒绝: {risk_check['reason']}")
            return
        
        # 最小金额检查
        min_notional = PERP_MIN_NOTIONAL.get(exchange, 1.0)
        position = min(self.paper_balance * 0.20, 200)
        
        if position < min_notional:
            logger.debug(f"[回测] 跳过: 仓位{position:.2f}U < 最小{min_notional}U")
            return
        
        # 精度检查
        price = best_tick['perp_ask']
        amount = position / price
        if amount < 1.0:
            logger.debug(f"[回测] 跳过: 币数量{amount:.4f} < 1.0")
            return
        
        # 成交概率（60%）
        if random.random() >= 0.6:
            logger.debug(f"[回测] 跳过: 成交概率未命中")
            return
        
        # 检查是否已有同币种同方向持仓
        if symbol in self.open_positions:
            logger.debug(f"[回测] 跳过: 已有持仓 {symbol}")
            return
        
        # 开仓
        position_id = int(time.time() * 1000)
        position = Position(symbol, exchange, 'buy', price, amount, position_id, best_tick['ts'])
        self.open_positions[symbol] = position
        
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
        
        for symbol, pos in self.open_positions.items():
            # 找最近的匹配tick
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
                to_close.append((symbol, pos, pnl_result, latest))
        
        for symbol, pos, pnl_result, tick in to_close:
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
                    self.paper_balance += pnl_result['net_pnl']
                
                # 从持仓中移除
                del self.open_positions[symbol]
                
                logger.debug(f"回测平仓: {symbol} @ {pnl_result['close_price']:.4f}, PnL={pnl_result['net_pnl']:+.4f}U ({pnl_result['pnl_pct']:+.3f}%)")
                
            except Exception as e:
                logger.debug(f"插入平仓失败: {e}")

    def get_status(self) -> Dict:
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': self.winning_trades / max(self.total_trades, 1),
            'paper_balance': self.paper_balance,
            'total_pnl': self.paper_balance - 1000.0,
            'open_positions': len(self.open_positions),
        }


class PaperEngine:
    """实时模拟引擎 - 完整交易周期版（真实风控检查）"""

    def __init__(self, config: SystemConfig, db_path: str):
        self.config = config
        self.db_path = db_path
        self.running = False
        self.thread = None
        self.paper_balance = 1000.0  # 模拟初始资金
        self.total_trades = 0
        self.winning_trades = 0
        self.open_positions: Dict[str, Position] = {}
        # 创建独立的模拟风控管理器，使用模拟余额而非实盘余额
        self.risk_manager = RiskManager(db_path, paper_mode=True, paper_balance=self.paper_balance)
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

        # 加载模拟盘状态
        cursor.execute("SELECT balance, total_pnl FROM simulated_balance WHERE id=1")
        row = cursor.fetchone()
        if row:
            self.paper_balance = row[0]
            logger.info(f"📝 恢复模拟盘余额: {self.paper_balance:.2f} USDT")

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
                    
                    # 检查是否已有同币种持仓
                    if symbol in self.open_positions:
                        # 检查是否需要平仓
                        pos = self.open_positions[symbol]
                        close_price = perp_bid if pos.side == 'buy' else perp_ask
                        pnl_result = pos.close(close_price)
                        
                        hold_time = ts - pos.timestamp
                        should_close = (pnl_result['net_pnl'] > 0 and pnl_result['pnl_pct'] > 0.01) or hold_time > 60
                        
                        if should_close:
                            # 平仓
                            self.total_trades += 1
                            if pnl_result['net_pnl'] > 0:
                                self.winning_trades += 1
                                self.paper_balance += pnl_result['net_pnl']
                            
                            cursor.execute(
                                "INSERT INTO engine_trades (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status) "
                                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                                (ts, 'paper', symbol, exchange, 'SELL', pnl_result['close_price'], 
                                 round(pos.amount, 8), pos.cost, pos.cost * pos.fee_rate,
                                 pnl_result['net_pnl'], pnl_result['pnl_pct'], 'completed')
                            )
                            
                            del self.open_positions[symbol]
                            
                            if self.total_trades % 10 == 0:
                                win_rate = self.winning_trades / self.total_trades * 100
                                total_pnl = self.paper_balance - 1000.0
                                logger.info(f"   模拟盘: {self.total_trades}笔, 胜率{win_rate:.1f}%, 余额${self.paper_balance:.2f}, 总盈亏{total_pnl:.2f}U")
                        continue
                    
                    # === 风控检查 ===
                    min_notional = PERP_MIN_NOTIONAL.get(exchange, 1.0)
                    position = min(self.paper_balance * 0.20, 200)
                    
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
                    
                    # 开仓
                    position_id = int(time.time() * 1000)
                    position = Position(symbol, exchange, 'buy', perp_ask, amount, position_id, ts)
                    self.open_positions[symbol] = position
                    
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

                # 每分钟保存状态
                now = time.time()
                if now - self.last_save_time > 60:
                    cursor.execute("DELETE FROM simulated_balance")
                    cursor.execute(
                        "INSERT INTO simulated_balance (id, timestamp, balance, total_pnl) VALUES (1, ?, ?, ?)",
                        (now, self.paper_balance, self.paper_balance - 1000.0)
                    )
                    conn.commit()
                    self.last_save_time = now

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
            'open_positions': len(self.open_positions),
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
