"""
实时数据收集器
持续收集订单簿、成交记录、价格时序数据
"""
import sqlite3
import time
import json
import numpy as np
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Deque
import ccxt

from .config import SystemConfig, DataCollectionConfig
from .models import MarketDataPoint, SignalRecord

class DataCollector:
    """实时市场数据收集器"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.data_config = config.data
        
        # 数据库
        self.db_path = self.data_config.db_path
        self._init_db()
        
        # 交易所连接
        self.exchange = None
        self._connect_exchange()
        
        # 内存缓存(快速访问)
        self.price_history: Dict[str, Deque[float]] = {}
        self.volume_history: Dict[str, Deque[float]] = {}
        self.spread_history: Dict[str, Deque[float]] = {}
        self.depth_history: Dict[str, Deque[float]] = {}
        
        # 统计
        self.total_ticks = 0
        self.last_update = 0
    
    def _init_db(self):
        """初始化数据库"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # 市场数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                symbol TEXT,
                spot_bid REAL,
                spot_ask REAL,
                spot_last REAL,
                perp_bid REAL,
                perp_ask REAL,
                perp_last REAL,
                spot_volume REAL,
                perp_volume REAL,
                spread_pct REAL,
                basis_pct REAL,
                depth_ratio REAL
            )
        ''')
        
        # 信号表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                symbol TEXT,
                signal_type TEXT,
                strategy TEXT,
                expected_profit REAL,
                actual_profit REAL,
                executed INTEGER DEFAULT 0,
                metadata TEXT
            )
        ''')
        
        # 策略绩效表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
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
        
        # 模式发现表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                pattern_type TEXT,
                symbol TEXT,
                confidence REAL,
                profitability REAL,
                parameters TEXT,
                status TEXT
            )
        ''')
        
        self.conn.commit()
    
    def _connect_exchange(self):
        """连接交易所"""
        try:
            import os
            api_key = os.getenv('BITGET_API_KEY', '')
            api_secret = os.getenv('BITGET_API_SECRET', '')
            passphrase = os.getenv('BITGET_API_PASSPHRASE', 'qntsomtop')
            
            self.exchange = ccxt.bitget({
                'apiKey': api_key,
                'secret': api_secret,
                'password': passphrase,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            print(f"✅ 已连接交易所: Bitget")
        except Exception as e:
            print(f"❌ 连接失败: {e}")
    
    def collect_tick(self) -> List[MarketDataPoint]:
        """收集一 tick 数据"""
        ticks = []
        now = time.time()
        
        for symbol in self.data_config.symbols:
            try:
                # 获取现货数据
                spot_ticker = self.exchange.fetch_ticker(symbol)
                spot_ob = self.exchange.fetch_order_book(symbol, 10)
                
                # 获取永续数据
                perp_symbol = f"{symbol.split('/')[0]}/USDT:USDT"
                perp_ticker = self.exchange.fetch_ticker(perp_symbol)
                
                # 计算指标
                spot_bid = float(spot_ob['bids'][0][0]) if spot_ob['bids'] else 0
                spot_ask = float(spot_ob['asks'][0][0]) if spot_ob['asks'] else 0
                spot_last = float(spot_ticker['last'])
                
                perp_bid = float(perp_ticker['bid']) if perp_ticker['bid'] else 0
                perp_ask = float(perp_ticker['ask']) if perp_ticker['ask'] else 0
                perp_last = float(perp_ticker['last'])
                
                # 价差计算
                spread_pct = (spot_ask - perp_bid) / spot_ask * 100 if spot_ask > 0 else 0
                basis_pct = (perp_last - spot_last) / spot_last * 100 if spot_last > 0 else 0
                
                # 深度比
                spot_bid_vol = float(spot_ob['bids'][0][1]) if spot_ob['bids'] else 0
                spot_ask_vol = float(spot_ob['asks'][0][1]) if spot_ob['asks'] else 0
                depth_ratio = spot_bid_vol / spot_ask_vol if spot_ask_vol > 0 else 1.0
                
                # 保存
                tick = MarketDataPoint(
                    timestamp=now,
                    symbol=symbol,
                    spot_bid=spot_bid,
                    spot_ask=spot_ask,
                    spot_last=spot_last,
                    perp_bid=perp_bid,
                    perp_ask=perp_ask,
                    perp_last=perp_last,
                    spread_pct=spread_pct,
                    basis_pct=basis_pct,
                    depth_ratio=depth_ratio
                )
                ticks.append(tick)
                
                # 更新内存缓存
                self._update_cache(symbol, tick)
                
                # 写入数据库
                self._save_tick(tick)
                
            except Exception as e:
                print(f"⚠️ {symbol} 数据收集失败: {e}")
        
        self.total_ticks += len(ticks)
        self.last_update = now
        return ticks
    
    def _update_cache(self, symbol: str, tick: MarketDataPoint):
        """更新内存缓存"""
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=self.data_config.history_size)
            self.volume_history[symbol] = deque(maxlen=self.data_config.history_size)
            self.spread_history[symbol] = deque(maxlen=self.data_config.history_size)
            self.depth_history[symbol] = deque(maxlen=self.data_config.history_size)
        
        self.price_history[symbol].append(tick.spot_last)
        self.spread_history[symbol].append(tick.spread_pct)
        self.depth_history[symbol].append(tick.depth_ratio)
    
    def _save_tick(self, tick: MarketDataPoint):
        """保存tick到数据库"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO market_data 
            (timestamp, symbol, spot_bid, spot_ask, spot_last, 
             perp_bid, perp_ask, perp_last, spread_pct, basis_pct, depth_ratio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tick.timestamp, tick.symbol, tick.spot_bid, tick.spot_ask, tick.spot_last,
            tick.perp_bid, tick.perp_ask, tick.perp_last,
            tick.spread_pct, tick.basis_pct, tick.depth_ratio
        ))
        self.conn.commit()
    
    def get_recent_data(self, symbol: str, n: int = 100) -> Dict:
        """获取最近N条数据"""
        if symbol not in self.price_history:
            return {}
        
        prices = list(self.price_history[symbol])
        spreads = list(self.spread_history[symbol])
        depths = list(self.depth_history[symbol])
        
        return {
            'prices': prices[-n:] if prices else [],
            'spreads': spreads[-n:] if spreads else [],
            'depths': depths[-n:] if depths else [],
            'count': len(prices)
        }
    
    def get_statistics(self, symbol: str) -> Dict:
        """获取统计数据"""
        data = self.get_recent_data(symbol, 500)
        
        if not data.get('prices'):
            return {}
        
        prices = np.array(data['prices'])
        spreads = np.array(data['spreads'])
        depths = np.array(data['depths'])
        
        return {
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
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
