"""
记忆承载·碧树西风交易系统 - 核心引擎
整合检测、风控、资金管理、订单执行
"""
import time
import sqlite3
import json
import threading
from typing import List, Optional
from datetime import datetime

from .config import SystemConfig
from .detector import Detector
from .exchange_adapter import ExchangeAdapter
from .risk_manager import RiskManager, TradeRecord
from .capital_manager import CapitalManager
from .backtest import BacktestEngine, BacktestConfig
from .models import FatFingerSignal, OrderSide


class TradingEngine:
    """交易引擎"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.detector = Detector(config.detection)
        self.risk_manager = RiskManager()
        self.capital_manager = CapitalManager(config.capital.initial_capital)
        
        # 初始化交易所适配器
        self.exchanges: dict = {}
        for name, ex_config in config.exchanges.items():
            adapter = ExchangeAdapter(ex_config)
            if adapter.exchange:
                self.exchanges[name] = adapter
        
        self.running = False
        self.trade_count = 0
        self.last_scan_time = 0
        
        # 数据库连接（保存信号和交易）
        self.db_path = config.data.db_path
        self._init_db()
    
    def start(self, mode: str = "backtest"):
        """启动引擎"""
        self.running = True
        print(f"🚀 交易引擎启动 (mode={mode})")
        
        if mode == "live":
            self._run_live()
        elif mode == "paper":
            self._run_paper()
        elif mode == "scan":
            self._run_scan_once()
        elif mode == "backtest":
            self._run_backtest()
    
    def _run_paper(self):
        """模拟盘模式 - 用真实实时数据，但不实际下单"""
        print(f"📊 模拟盘模式 - 监控交易对: {', '.join(self.config.symbols)}")
        print(f"  本金: {self.config.capital.initial_capital} USDT")
        print(f"  模式: 真实实时数据扫描 + 模拟下单")
        print(f"  数据库: {self.db_path}")
        print()
        
        while self.running:
            try:
                current_time = time.time()
                if current_time - self.last_scan_time < 5:
                    time.sleep(1)
                    continue
                self.last_scan_time = current_time
                
                for exchange_name, adapter in self.exchanges.items():
                    for symbol in self.config.symbols:
                        self._scan_symbol(exchange_name, adapter, symbol)
                self._check_risk()
            except KeyboardInterrupt:
                print("\n🛑 用户中断")
                break
            except Exception as e:
                print(f"⚠️ 运行时错误: {e}")
                time.sleep(5)
        self.stop()
    
    def _run_backtest(self):
        """持续回测模式 - 用模拟数据滚动回测，持续输出信号和交易"""
        print(f"📊 回测引擎启动 - 持续运行模式")
        print(f"  数据库: {self.db_path}")
        print()
        
        bt_config = BacktestConfig(
            initial_capital=self.config.capital.initial_capital,
            duration_days=30,
            fat_finger_probability=0.002,
            fat_finger_deviation_range=(2.0, 15.0),
            volatility_daily=3.0,
        )
        bt_engine = BacktestEngine(bt_config)
        
        while self.running:
            try:
                # 运行一轮回测
                result = bt_engine.run()
                
                # 保存回测结果到数据库
                self._save_backtest_results(result)
                
                # 打印摘要
                print(f"✅ 回测完成: {result.total_trades}笔, 胜率{result.win_rate*100:.1f}%, 收益{result.total_return_pct:.1f}%")
                
                # 等待下一轮（用最新随机种子，生成新数据）
                time.sleep(60)  # 每分钟跑一轮
                
            except KeyboardInterrupt:
                print("\n🛑 回测引擎停止")
                break
            except Exception as e:
                print(f"⚠️ 回测错误: {e}")
                time.sleep(10)
    
    def _save_backtest_results(self, result):
        """保存回测结果到engine_signals和engine_trades表"""
        try:
            cursor = self.conn.cursor()
            
            # 保存每个模拟交易的信号和结果
            for trade in result.trades[:50]:  # 每轮最多保存50笔
                cursor.execute('''
                    INSERT INTO engine_signals
                    (timestamp, mode, symbol, exchange, signal_type, strategy, expected_profit, executed, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade.timestamp,
                    'backtest',
                    trade.symbol,
                    trade.exchange,
                    'single_exchange',
                    'fat_finger_arb',
                    abs(trade.pnl),  # expected profit
                    1,  # executed
                    json.dumps({'deviation': 'simulated', 'pnl': trade.pnl})
                ))
                
                cursor.execute('''
                    INSERT INTO engine_trades
                    (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade.timestamp,
                    'backtest',
                    trade.symbol,
                    trade.exchange,
                    'BUY',
                    trade.price,
                    trade.amount,
                    trade.cost,
                    trade.fee,
                    trade.pnl,
                    trade.pnl / trade.cost * 100 if trade.cost > 0 else 0,
                    'completed'
                ))
            
            self.conn.commit()
            print(f"   💾 已保存 {len(result.trades[:50])} 笔回测数据到数据库")
            
        except Exception as e:
            print(f"⚠️ 保存回测结果失败: {e}")
    
    def _run_scan_once(self):
        """单次扫描 - 检测当前是否有乌龙指机会"""
        print(f"📡 单次扫描 - 检测当前市场")
        for exchange_name, adapter in self.exchanges.items():
            for symbol in self.config.symbols:
                self._scan_symbol(exchange_name, adapter, symbol)
        print(f"\n✅ 扫描完成，发现 {self.trade_count} 个信号")
    
    def _run_live(self):
        """实盘运行"""
        print(f"📊 实盘模式 - 监控交易对: {', '.join(self.config.symbols)}")
        
        while self.running:
            try:
                current_time = time.time()
                
                # 频率限制
                if current_time - self.last_scan_time < 5:
                    time.sleep(1)
                    continue
                
                self.last_scan_time = current_time
                
                # 扫描每个交易所的每个交易对
                for exchange_name, adapter in self.exchanges.items():
                    for symbol in self.config.symbols:
                        self._scan_symbol(exchange_name, adapter, symbol)
                
                # 检查风控
                self._check_risk()
                
            except KeyboardInterrupt:
                print("\n🛑 用户中断")
                break
            except Exception as e:
                print(f"⚠️ 运行时错误: {e}")
                time.sleep(5)
        
        self.stop()
    
    def _scan_symbol(self, exchange_name: str, adapter: ExchangeAdapter, symbol: str, mode: str = "paper"):
        """扫描单个交易对"""
        spot_symbol = symbol  # BTC/USDT等
        try:
            ob = adapter.fetch_orderbook(spot_symbol)
            if not ob:
                return
            
            # 检测信号
            signals = self.detector.detect_single_exchange(
                exchange_name, symbol, ob, []
            )
            
            for signal in signals:
                self._process_signal(signal, mode)
                
        except Exception as e:
            pass
    
    def _init_db(self):
        """初始化数据库表"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.conn.cursor()
            
            # 信号表（保存所有引擎的信号）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS engine_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    mode TEXT,          -- 'backtest', 'paper', 'live'
                    symbol TEXT,
                    exchange TEXT,
                    signal_type TEXT,
                    strategy TEXT,
                    expected_profit REAL,
                    actual_profit REAL,
                    executed INTEGER DEFAULT 0,
                    metadata TEXT
                )
            ''')
            
            # 交易表（保存所有引擎的交易）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS engine_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    mode TEXT,
                    symbol TEXT,
                    exchange TEXT,
                    side TEXT,
                    price REAL,
                    amount REAL,
                    cost REAL,
                    fee REAL,
                    pnl REAL,
                    pnl_pct REAL,
                    status TEXT
                )
            ''')
            
            self.conn.commit()
        except Exception as e:
            print(f"⚠️ 数据库初始化失败: {e}")
    
    def _save_signal(self, signal: FatFingerSignal, mode: str, expected_profit: float = None):
        """保存信号到数据库"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO engine_signals
                (timestamp, mode, symbol, exchange, signal_type, strategy, expected_profit, executed, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.timestamp or time.time(),
                mode,
                signal.symbol,
                signal.exchange,
                signal.signal_type.value if hasattr(signal.signal_type, 'value') else str(signal.signal_type),
                'fat_finger_arb',
                expected_profit,
                0,  # executed
                json.dumps({
                    'fair_price': signal.fair_price,
                    'deviation_pct': signal.deviation_pct,
                    'depth_available': signal.depth_available,
                    'target_side': signal.target_side.value if hasattr(signal.target_side, 'value') else str(signal.target_side)
                })
            ))
            self.conn.commit()
        except Exception as e:
            print(f"⚠️ 保存信号失败: {e}")
    
    def _save_trade(self, trade: FatFingerSignal, mode: str, pnl: float, pnl_pct: float, status: str):
        """保存交易到数据库"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO engine_trades
                (timestamp, mode, symbol, exchange, side, price, amount, cost, fee, pnl, pnl_pct, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                time.time(),
                mode,
                trade.symbol,
                trade.exchange,
                trade.target_side.value if hasattr(trade.target_side, 'value') else str(trade.target_side),
                trade.price,
                trade.depth_available / trade.price if trade.price > 0 else 0,
                trade.depth_available,
                trade.depth_available * 0.001,  # 估算手续费
                pnl,
                pnl_pct,
                status
            ))
            self.conn.commit()
        except Exception as e:
            print(f"⚠️ 保存交易失败: {e}")
    
    def _process_signal(self, signal: FatFingerSignal, mode: str = "paper"):
        """处理信号"""
        # 保存信号到数据库
        self._save_signal(signal, mode)
        
        # 风控检查（只有live模式才执行交易）
        if mode == "live":
            can_trade, reason = self.risk_manager.check_before_trade(
                signal.depth_available,
                self.config.capital.initial_capital
            )
            
            if not can_trade:
                print(f"❌ 信号过滤: {reason}")
                return
            
            # 执行交易
            self._execute_trade(signal, mode)
        else:
            # paper/backtest模式：模拟执行，不真下单
            print(f"📊 [{mode.upper}] 信号: {signal.symbol} 偏离{signal.deviation_pct:.2f}%")
            self._simulate_execute(signal, mode)
    
    def _simulate_execute(self, signal: FatFingerSignal, mode: str):
        """模拟执行交易（paper/backtest模式）"""
        # 计算模拟利润
        buy_price = signal.price  # 永续开多价格
        sell_price = signal.fair_price  # 现货卖出价格
        
        # 手续费
        fee_rate = 0.0006  # 0.06%
        slippage = 0.0002  # 0.02%
        
        # 模拟计算
        position_size = signal.depth_available * 0.1  # 10%深度
        buy_cost = position_size
        buy_fee = buy_cost * fee_rate
        buy_amount = position_size / (buy_price * (1 + slippage))
        
        sell_revenue = buy_amount * sell_price * (1 - slippage)
        sell_fee = sell_revenue * fee_rate
        
        pnl = sell_revenue - buy_cost - buy_fee - sell_fee
        pnl_pct = pnl / buy_cost * 100 if buy_cost > 0 else 0
        
        # 保存交易到数据库
        self._save_trade(signal, mode, pnl, pnl_pct, "simulated")
        
        # 更新计数
        self.trade_count += 1
        
        # 打印结果
        direction = "🟢盈利" if pnl > 0 else "🔴亏损"
        print(f"   {direction} | 模拟利润: ${pnl:.4f} ({pnl_pct:.3f}%)")
    
    def _execute_trade(self, signal: FatFingerSignal, mode: str = "live"):
        """执行交易 - 永续开多 + 现货卖单对冲"""
        print(f"🎯 执行交易: {signal.symbol} ({signal.exchange}) 偏离{signal.deviation_pct:.2f}%")
        
        try:
            adapter = self.exchanges.get(signal.exchange)
            if not adapter:
                print(f"❌ 找不到交易所适配器: {signal.exchange}")
                return
            
            # 获取当前价格
            ticker = adapter.fetch_ticker(signal.symbol.replace('/USDT', '/USDT'))
            if not ticker:
                return
            
            # 计算仓位（不超过最大仓位限制）
            max_position = self.capital_manager.get_position_size()
            position_size = min(signal.depth_available * 0.1, max_position)
            
            min_position = 5.0 if self.config.exchanges.get(signal.exchange, {}).testnet else 5.0
            if position_size < min_position:
                print(f"⚠️ 仓位太小({position_size:.2f} USDT < {min_position} U)跳过")
                return
            
            # 永续开多
            perp_symbol = f"{signal.symbol.split('/')[0]}/USDT:USDT"
            adapter.create_post_only_order(
                perp_symbol, OrderSide.BUY, position_size, signal.price * 0.99
            )
            
            # 现货卖单
            adapter.create_post_only_order(
                signal.symbol, OrderSide.SELL, position_size / signal.price, signal.price
            )
            
            self.trade_count += 1
            print(f"✅ 订单已提交: {self.trade_count}笔")
            
            # 保存交易到数据库
            # 这里简化处理，实际应该等成交后再保存
            self._save_trade(signal, mode, 0, 0, "pending")
            
        except Exception as e:
            print(f"❌ 执行失败: {e}")
    
    def _check_risk(self):
        """检查风控状态"""
        status = self.risk_manager.get_status()
        if not status['is_trading_allowed']:
            print(f"⛔ 风控触发! {status}")
    
    def stop(self):
        """停止引擎"""
        self.running = False
        for adapter in self.exchanges.values():
            adapter.close()
        if hasattr(self, 'conn'):
            try:
                self.conn.close()
            except:
                pass
        print("🛑 引擎已停止")
    
    def get_status(self) -> dict:
        """获取系统状态"""
        # 从数据库读取统计数据
        signal_count = 0
        trade_count = 0
        try:
            if hasattr(self, 'conn'):
                cursor = self.conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM engine_signals")
                signal_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM engine_trades WHERE status != 'pending'")
                trade_count = cursor.fetchone()[0]
        except:
            pass
        
        return {
            "trades": trade_count,
            "signals": signal_count,
            "risk": self.risk_manager.get_status(),
            "capital": self.capital_manager.get_status(),
            "exchanges": list(self.exchanges.keys()),
        }
