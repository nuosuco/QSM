"""
实时数据收集器（三平台版）
持续从 Bitget、HTX、Gate.io 三个平台并行采集订单簿、成交记录、价格时序数据
"""
import logging
import sqlite3
from .db_utils import get_connection
import time
import json
import numpy as np
from collections import deque, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Deque
import ccxt

from .config import SystemConfig, DataCollectionConfig
from .models import MarketDataPoint, SignalRecord


class ExchangeConnector:
    """单个交易所连接器"""
    
    def __init__(self, name: str, api_key: str, api_secret: str, passphrase: str = "",
                 enabled: bool = True, options: dict = None):
        self.name = name
        self.enabled = enabled
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.options = options or {'defaultType': 'spot'}
        self.exchange = None
        self.connected = False
        self.error = None
        
        if enabled:
            self._connect()
    
    def _connect(self):
        """连接交易所"""
        try:
            cls = getattr(ccxt, self.name, None)
            if not cls:
                self.error = f"不支持的交易所: {self.name}"
                self.connected = False
                return
            
            kwargs = {
                'enableRateLimit': True,
                'timeout': 10000,
                'options': self.options,
            }
            if self.api_key:
                kwargs['apiKey'] = self.api_key
            if self.api_secret:
                kwargs['secret'] = self.api_secret
            if self.passphrase:
                kwargs['password'] = self.passphrase
            
            self.exchange = cls(kwargs)
            
            # 验证连接
            t = self.exchange.fetch_ticker('BTC/USDT')
            self.connected = True
            print(f"✅ {self.name} 连接成功 (BTC: ${float(t['last']):,.0f})")
        except Exception as e:
            self.error = str(e)[:100]
            self.connected = False
            print(f"❌ {self.name} 连接失败: {self.error}")
    
    def fetch_ticker(self, symbol: str) -> dict:
        """获取行情"""
        if not self.connected or not self.exchange:
            return {}
        try:
            return self.exchange.fetch_ticker(symbol)
        except:
            return {}
    
    def fetch_order_book(self, symbol: str, limit: int = 10) -> dict:
        """获取订单簿"""
        if not self.connected or not self.exchange:
            return {}
        try:
            return self.exchange.fetch_order_book(symbol, limit)
        except:
            return {}
    
    def fetch_perp_ticker(self, symbol: str) -> dict:
        """获取永续合约行情"""
        if not self.connected or not self.exchange:
            return {}
        try:
            perp_symbol = f"{symbol.split('/')[0]}/USDT:USDT"
            return self.exchange.fetch_ticker(perp_symbol)
        except:
            return {}
    
    def get_status(self) -> dict:
        return {
            'name': self.name,
            'connected': self.connected,
            'enabled': self.enabled,
            'error': self.error
        }


class DataCollector:
    """实时市场数据收集器（三平台版）"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.data_config = config.data
        
        # 数据库
        self.db_path = self.data_config.db_path
        self._init_db()
        
        # 连接三个平台
        self.connectors: Dict[str, ExchangeConnector] = {}
        self._init_exchanges()
        
        # 内存缓存（按平台+币种）
        self.price_history: Dict[str, Dict[str, Deque[float]]] = defaultdict(lambda: defaultdict(lambda: deque(maxlen=self.data_config.history_size)))
        self.spread_history: Dict[str, Dict[str, Deque[float]]] = defaultdict(lambda: defaultdict(lambda: deque(maxlen=self.data_config.history_size)))
        self.depth_history: Dict[str, Dict[str, Deque[float]]] = defaultdict(lambda: defaultdict(lambda: deque(maxlen=self.data_config.history_size)))
        # 统计
        self.total_ticks = 0
        self.ticks_per_exchange: Dict[str, int] = defaultdict(int)
        self.last_update = 0
    
    def _init_db(self):
        """初始化数据库（增加交易所字段，兼容旧表）"""
        self.conn = get_connection(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=30000")
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # 检查旧表是否有 exchange 字段（迁移兼容）
        cursor.execute("PRAGMA table_info(market_data)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'exchange' not in columns:
            print("🔄 迁移旧表: market_data 增加 exchange 字段")
            # 重建表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    exchange TEXT DEFAULT 'bitget',
                    symbol TEXT,
                    spot_bid REAL,
                    spot_ask REAL,
                    spot_last REAL,
                    perp_bid REAL,
                    perp_ask REAL,
                    perp_last REAL,
                    spot_volume REAL DEFAULT 0,
                    perp_volume REAL DEFAULT 0,
                    spread_pct REAL,
                    basis_pct REAL,
                    depth_ratio REAL
                )
            ''')
            cursor.execute('INSERT INTO market_data_new (id, timestamp, symbol, spot_bid, spot_ask, spot_last, perp_bid, perp_ask, perp_last, spread_pct, basis_pct, depth_ratio) SELECT id, timestamp, symbol, spot_bid, spot_ask, spot_last, perp_bid, perp_ask, perp_last, spread_pct, basis_pct, depth_ratio FROM market_data')
            cursor.execute('DROP TABLE market_data')
            cursor.execute('ALTER TABLE market_data_new RENAME TO market_data')
            self.conn.commit()
            print(f"✅ 旧表迁移完成, {cursor.rowcount} 条数据已添加 exchange='bitget'")
        
        # 检查 signals 表
        try:
            cursor.execute("PRAGMA table_info(signals)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'exchange' not in columns:
                print("🔄 迁移旧表: signals 增加 exchange 字段")
                # 先建signals_new
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS signals_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL,
                        exchange TEXT DEFAULT 'bitget',
                        symbol TEXT,
                        signal_type TEXT,
                        strategy TEXT,
                        expected_profit REAL,
                        actual_profit REAL DEFAULT 0,
                        executed INTEGER DEFAULT 0,
                        metadata TEXT
                    )
                ''')
                # 检查signals是否存在且有数据
                try:
                    cursor.execute("SELECT COUNT(*) FROM signals")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        cursor.execute('INSERT INTO signals_new (id, timestamp, symbol, signal_type, strategy, expected_profit, actual_profit, executed, metadata) SELECT id, timestamp, symbol, signal_type, strategy, expected_profit, actual_profit, executed, metadata FROM signals')
                        cursor.execute('DROP TABLE signals')
                        cursor.execute('ALTER TABLE signals_new RENAME TO signals')
                        print(f"✅ signals 迁移完成 ({count}条)")
                    else:
                        # signals表为空，用signals_new替代
                        cursor.execute("SELECT COUNT(*) FROM signals_new")
                        cnt = cursor.fetchone()[0]
                        if cnt > 0:
                            cursor.execute('ALTER TABLE signals_new RENAME TO signals')
                            print(f"✅ signals 重命名完成 ({cnt}条)")
                        else:
                            # 两个都空，signals表已存在(可能是空壳)
                            pass
                except:
                    # signals表不存在
                    pass
                self.conn.commit()
        except Exception as e:
            print(f"⚠️ signals表迁移跳过: {e}")
            self.conn.commit()
        
        # 检查 strategy_performance 表
        cursor.execute("PRAGMA table_info(strategy_performance)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'exchange' not in columns:
            print("🔄 迁移旧表: strategy_performance 增加 exchange 字段")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategy_performance_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    exchange TEXT DEFAULT 'bitget',
                    strategy TEXT,
                    total_trades INTEGER,
                    winning_trades INTEGER,
                    losing_trades INTEGER,
                    win_rate REAL,
                    avg_profit REAL,
                    total_profit REAL,
                    sharpe_ratio REAL
                )
            ''')
            try:
                cursor.execute('INSERT INTO strategy_performance_new (id, timestamp, strategy, total_trades, winning_trades, losing_trades, win_rate, avg_profit, total_profit, sharpe_ratio) SELECT id, timestamp, strategy, total_trades, winning_trades, losing_trades, win_rate, avg_profit, total_profit, sharpe_ratio FROM strategy_performance')
                cursor.execute('DROP TABLE strategy_performance')
                cursor.execute('ALTER TABLE strategy_performance_new RENAME TO strategy_performance')
                print(f"✅ strategy_performance 迁移完成")
            except Exception as e:
                print(f"⚠️ strategy_performance迁移跳过: {e}")
            self.conn.commit()
        
        # 检查 patterns 表
        cursor.execute("PRAGMA table_info(patterns)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'exchange' not in columns:
            print("🔄 迁移旧表: patterns 增加 exchange 字段")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patterns_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    exchange TEXT DEFAULT 'bitget',
                    pattern_type TEXT,
                    symbol TEXT,
                    confidence REAL,
                    profitability REAL,
                    parameters TEXT,
                    status TEXT
                )
            ''')
            try:
                cursor.execute("SELECT COUNT(*) FROM patterns")
                count = cursor.fetchone()[0]
                if count > 0:
                    cursor.execute('INSERT INTO patterns_new (id, timestamp, pattern_type, symbol, confidence, profitability, parameters, status) SELECT id, timestamp, pattern_type, symbol, confidence, profitability, parameters, status FROM patterns')
                    cursor.execute('DROP TABLE patterns')
                    cursor.execute('ALTER TABLE patterns_new RENAME TO patterns')
                    print(f"✅ patterns 迁移完成 ({count}条)")
                else:
                    cursor.execute("SELECT COUNT(*) FROM patterns_new")
                    cnt = cursor.fetchone()[0]
                    if cnt > 0:
                        cursor.execute('ALTER TABLE patterns_new RENAME TO patterns')
                        print(f"✅ patterns 重命名完成 ({cnt}条)")
                    else:
                        pass
            except Exception as e:
                print(f"⚠️ patterns迁移跳过: {e}")
            self.conn.commit()
        
        # 如果表不存在，创建新表（带exchange字段）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                exchange TEXT DEFAULT 'bitget',
                symbol TEXT,
                spot_bid REAL,
                spot_ask REAL,
                spot_last REAL,
                perp_bid REAL,
                perp_ask REAL,
                perp_last REAL,
                spot_volume REAL DEFAULT 0,
                perp_volume REAL DEFAULT 0,
                spread_pct REAL,
                basis_pct REAL,
                depth_ratio REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                exchange TEXT DEFAULT 'bitget',
                symbol TEXT,
                signal_type TEXT,
                strategy TEXT,
                expected_profit REAL,
                actual_profit REAL DEFAULT 0,
                executed INTEGER DEFAULT 0,
                metadata TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                exchange TEXT DEFAULT 'bitget',
                strategy TEXT,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                win_rate REAL,
                avg_profit REAL,
                total_profit REAL,
                sharpe_ratio REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                exchange TEXT DEFAULT 'bitget',
                pattern_type TEXT,
                symbol TEXT,
                confidence REAL,
                profitability REAL,
                parameters TEXT,
                status TEXT
            )
        ''')
        self.conn.commit()
    
    def _init_exchanges(self):
        """初始化三个交易所连接"""
        self.config.load_api_keys()
        
        for ex_name, ex_cfg in self.config.exchanges.items():
            connector = ExchangeConnector(
                name=ex_name,
                api_key=ex_cfg.api_key,
                api_secret=ex_cfg.api_secret,
                passphrase=ex_cfg.passphrase,
                enabled=ex_cfg.enabled,
                options=ex_cfg.options
            )
            self.connectors[ex_name] = connector
    
    def collect_tick(self) -> List[MarketDataPoint]:
        """从所有平台收集一 tick 数据。2026-09-14 修：返回"实际成功写库的条数"(int)，不再是列表。"""
        all_ticks = []
        written_ok = 0
        now = time.time()
        
        for ex_name, connector in self.connectors.items():
            if not connector.connected:
                continue
            
            for symbol in self.data_config.symbols:
                try:
                    tick = self._collect_single(ex_name, connector, symbol, now)
                    if tick:
                        all_ticks.append(tick)
                        self._update_cache(ex_name, symbol, tick)
                        ok = self._save_tick(tick)   # 2026-09-14：_save_tick 返回 bool
                        if ok:
                            written_ok += 1
                        self.ticks_per_exchange[ex_name] += 1
                except Exception as e:
                    import logging as _logging
                    _logging.getLogger('DataCollector').warning(
                        f"⚠️ 采集 {ex_name}/{symbol} 失败: {e}")
        
        self.total_ticks += len(all_ticks)
        self.last_update = now
        # 2026-09-14 中华盯盘修正：返回"实际成功写库的条数"（int），
        # 循环里只有 >0 才刷新 last_write_ts，真正 5 分钟没写入才停摆告警
        return written_ok
    
    def _collect_single(self, ex_name: str, connector: ExchangeConnector,
                        symbol: str, now: float) -> Optional[MarketDataPoint]:
        """从单个平台采集单个币种数据"""
        # 获取现货数据
        spot_ticker = connector.fetch_ticker(symbol)
        if not spot_ticker:
            return None
        
        spot_ob = connector.fetch_order_book(symbol, 10) or {}
        
        # 获取永续数据
        perp_ticker = connector.fetch_perp_ticker(symbol) or {}
        
        # 计算指标（2026-09-14 中华盯盘修正：对 ccxt 各平台返回类型鲁棒，
        # 之前某平台返回 list 而非 dict，.get 在 list 上比较 'list'>'int' 崩溃 → 整轮采集失败、管道停摆）
        def _book_px(ob, key):
            lvl = (ob or {}).get(key) or []
            if isinstance(lvl, list) and lvl and isinstance(lvl[0], (list, tuple)) and len(lvl[0]) >= 2:
                try: return float(lvl[0][0])
                except Exception: return 0.0
            return 0.0
        def _vol(lvl):
            if isinstance(lvl, list) and lvl and isinstance(lvl[0], (list, tuple)) and len(lvl[0]) >= 2:
                try: return float(lvl[0][1])
                except Exception: return 0.0
            return 0.0
        spot_bid = _book_px(spot_ob, 'bids')
        spot_ask = _book_px(spot_ob, 'asks')
        try: spot_last = float((spot_ticker or {}).get('last', 0) or 0)
        except Exception: spot_last = 0.0
        try: perp_bid = float((perp_ticker or {}).get('bid', 0) or 0)
        except Exception: perp_bid = 0.0
        try: perp_ask = float((perp_ticker or {}).get('ask', 0) or 0)
        except Exception: perp_ask = 0.0
        try: perp_last = float((perp_ticker or {}).get('last', 0) or 0)
        except Exception: perp_last = 0.0
        
        # 价差计算 - 修复bug：当永续合约价格为0时跳过
        # 做市策略：永续合约买入(perp_ask) → 现货卖出(spot_bid)
        # 利润 = spot_bid - perp_ask - 手续费
        if perp_ask <= 0 or spot_bid <= 0:
            # 永续合约无数据，跳过此tick
            return None
        if perp_ask > 0 and spot_bid > 0:
            spread_pct = (spot_bid - perp_ask) / perp_ask  # 不乘100，存为小数形式（如0.001表示0.1%）
        else:
            spread_pct = 0
        basis_pct = (perp_last - spot_last) / spot_last * 100 if spot_last > 0 else 0
        
        # 深度比（2026-09-14 中华盯盘修正：用鲁棒的 _vol，避免 list/dict 比较崩）
        spot_bid_vol = _vol((spot_ob or {}).get('bids') or [])
        spot_ask_vol = _vol((spot_ob or {}).get('asks') or [])
        depth_ratio = spot_bid_vol / spot_ask_vol if spot_ask_vol > 0 else 1.0
        
        # 成交量（2026-09-14 中华盯盘修正：baseVolume 可能是 list/None，兜底成 0，不让整轮崩）
        try: spot_volume = float((spot_ticker or {}).get('baseVolume', 0) or 0)
        except Exception: spot_volume = 0.0
        try: perp_volume = float((perp_ticker or {}).get('baseVolume', 0) or 0)
        except Exception: perp_volume = 0.0
        
        return MarketDataPoint(
            timestamp=now,
            exchange=ex_name,
            symbol=symbol,
            spot_bid=spot_bid,
            spot_ask=spot_ask,
            spot_last=spot_last,
            perp_bid=perp_bid,
            perp_ask=perp_ask,
            perp_last=perp_last,
            spot_volume=spot_volume,
            perp_volume=perp_volume,
            spread_pct=spread_pct,
            basis_pct=basis_pct,
            depth_ratio=depth_ratio
        )
    
    def _update_cache(self, ex_name: str, symbol: str, tick: MarketDataPoint):
        """更新内存缓存"""
        self.price_history[ex_name][symbol].append(tick.spot_last)
        self.spread_history[ex_name][symbol].append(tick.spread_pct)
        self.depth_history[ex_name][symbol].append(tick.depth_ratio)
    
    def _save_tick(self, tick: MarketDataPoint) -> bool:
        """保存tick到数据库（含锁等待重试）。2026-09-14 修：返回是否写库成功，
        供 collect_tick 统计实际成功写库条数，只有真正写成功才刷新 last_write_ts，
        否则监控自身坏（写库失败但 last_write_ts 仍刷新 → 停摆告警永不触发）。"""
        def _do_insert():
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO market_data 
                (timestamp, exchange, symbol, spot_bid, spot_ask, spot_last, 
                 perp_bid, perp_ask, perp_last, spot_volume, perp_volume,
                 spread_pct, basis_pct, depth_ratio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tick.timestamp, tick.exchange, tick.symbol,
                tick.spot_bid, tick.spot_ask, tick.spot_last,
                tick.perp_bid, tick.perp_ask, tick.perp_last,
                tick.spot_volume, tick.perp_volume,
                tick.spread_pct, tick.basis_pct, tick.depth_ratio
            ))
            self.conn.commit()

        try:
            _do_insert()
            return True
        except sqlite3.OperationalError:
            # database is locked（多连接写同一WAL库）→ 重试最多3次，每次间隔0.5s
            import time as _time
            for _attempt in range(3):
                _time.sleep(0.5)
                try:
                    _do_insert()
                    return True
                except sqlite3.OperationalError:
                    continue
            import logging as _logging
            _logging.getLogger('DataCollector').error(
                f"🚨 market_data 写库失败(重试3次仍锁库): tick={tick.exchange}/{tick.symbol}")
            return False
        except Exception as e:
            # 2026-09-13：不再静默吞掉写库失败——历史上管道断更3天就是因为这里 except: pass
            import logging as _logging
            _logging.getLogger('DataCollector').error(
                f"🚨 market_data 写库失败: {e} | tick={tick.exchange}/{tick.symbol}")
            return False
    def get_recent_data(self, ex_name: str, symbol: str, n: int = 100) -> Dict:
        """获取某个平台某币种最近N条数据"""
        ex_name = ex_name.lower()
        if ex_name not in self.price_history or symbol not in self.price_history[ex_name]:
            return {}
        
        prices = list(self.price_history[ex_name][symbol])
        spreads = list(self.spread_history[ex_name][symbol])
        depths = list(self.depth_history[ex_name][symbol])
        
        return {
            'prices': prices[-n:] if prices else [],
            'spreads': spreads[-n:] if spreads else [],
            'depths': depths[-n:] if depths else [],
            'count': len(prices)
        }
    
    def get_statistics(self, ex_name: str, symbol: str) -> Dict:
        """获取某个平台某币种的统计数据"""
        data = self.get_recent_data(ex_name, symbol, 500)
        
        if not data.get('prices'):
            return {}
        
        prices = np.array(data['prices'])
        spreads = np.array(data['spreads'])
        depths = np.array(data['depths'])
        
        return {
            'exchange': ex_name,
            'symbol': symbol,
            'price_mean': float(np.mean(prices)),
            'price_std': float(np.std(prices)),
            'price_min': float(np.min(prices)),
            'price_max': float(np.max(prices)),
            'spread_mean': float(np.mean(spreads)),
            'spread_std': float(np.std(spreads)),
            'spread_max': float(np.max(np.abs(spreads))),
            'depth_mean': float(np.mean(depths)),
            'sample_count': len(prices)
        }
    
    def get_all_statistics(self) -> Dict[str, Dict]:
        """获取所有平台所有币种的统计"""
        stats = {}
        for ex_name in self.connectors:
            if not self.connectors[ex_name].connected:
                continue
            stats[ex_name] = {}
            for symbol in self.data_config.symbols:
                s = self.get_statistics(ex_name, symbol)
                if s:
                    stats[ex_name][symbol] = s
        return stats
    
    def get_exchange_status(self) -> List[Dict]:
        """获取所有平台连接状态"""
        return [c.get_status() for c in self.connectors.values()]
    
    def start(self):
        """启动数据收集（后台线程）"""
        import threading
        
        def _collect_loop():
            import traceback as _tb
            logger = logging.getLogger('DataCollector')
            logger.info("📡 数据收集器启动 (三平台并行)")
            # 2026-09-13：整个循环体包在 try/except 里，线程因任何异常崩溃都会打 ERROR + 堆栈
            last_write_ts = time.time()
            try:
                while self.running:
                    try:
                        written = self.collect_tick()   # 2026-09-14：返回"实际成功写库的条数"(int)
                        if written > 0:
                            last_write_ts = time.time()
                            logger.info(f"📡 数据采集: 写库 {written} 条 tick")
                        else:
                            logger.warning("📡 数据采集: 本轮 0 条写库成功（检查各平台连接/数据库锁）")
                    except Exception as e:
                        import traceback as _tb
                        logger.error(f"采集失败: {e}\n{_tb.format_exc()}")
                    now = time.time()
                    if now - last_write_ts > 300:
                        logger.error(f"🚨 数据管道停摆 {int((now-last_write_ts)/60)} 分钟未写入 market_data，检查各平台连接/数据库锁")
                    time.sleep(5)  # 每5秒采集一次
            except BaseException as _e:
                logger.error(f"🚨 数据采集线程崩溃退出: {_e}")
                _tb.print_exc()
        
        # 2026-09-13：加 running 开关，close() 可干净停止
        self.running = True
        thread = threading.Thread(target=_collect_loop, daemon=True, name='qnt-data-collector')
        thread.start()
        import time as _t
        _t.sleep(0.2)
        if not thread.is_alive():
            print("🚨 DataCollector 线程启动后立刻退出（self.running 初始值异常？），当前 running =", self.running)
        self._collect_thread = thread
        return thread
    
    def close(self):
        """关闭连接"""
        self.running = False
        if self.conn:
            self.conn.close()