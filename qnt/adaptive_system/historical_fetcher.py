"""双模式历史成交数据采集器
模式一：我们的真实成交（fetch_my_trades，需要API密钥）
模式二：平台公开市场成交（fetch_trades，不需要密钥）
"""
import ccxt
import sqlite3
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from data_collector import ExchangeConnector

logger = logging.getLogger(__name__)

class HistoricalFetcher:
    """双模式历史成交数据采集器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.exchanges = {}  # 私有连接器（需要API密钥）
        self.public_exchanges = {}  # 公开连接器（不需要密钥）
        
    def init_exchange(self, name: str, connector: ExchangeConnector):
        """初始化交易所连接器（私有+公开）"""
        try:
            exchange_class = getattr(ccxt, name)
            # 私有连接器
            private_exchange = exchange_class({
                'apiKey': connector.api_key,
                'secret': connector.secret,
                'password': connector.passphrase if hasattr(connector, 'passphrase') else '',
                'enableRateLimit': True,
                'timeout': 30000,
            })
            self.exchanges[name] = private_exchange
            # 公开连接器（无密钥）
            public_exchange = exchange_class({'enableRateLimit': True, 'timeout': 10000})
            self.public_exchanges[name] = public_exchange
            logger.info(f"✅ {name} 双模式初始化成功")
            return True
        except Exception as e:
            logger.error(f"❌ {name} 初始化失败: {e}")
            return False
    
    def fetch_my_trades(self, exchange_name: str, symbol: str, 
                        limit: int = 100, since: Optional[int] = None) -> List[Dict]:
        """获取我们的真实成交（模式一）"""
        if exchange_name not in self.exchanges:
            logger.error(f"❌ {exchange_name} 未初始化")
            return []
        
        exchange = self.exchanges[exchange_name]
        
        try:
            trades = []
            # 尝试现货
            try:
                trades = exchange.fetch_my_trades(symbol, limit=limit, since=since)
                logger.debug(f"{exchange_name} {symbol} 现货成交: {len(trades)}笔")
            except Exception as e:
                logger.debug(f"{exchange_name} {symbol} 现货成交失败: {e}")
            
            # 尝试永续合约
            if not trades and ':' not in symbol:
                perp_symbol = f"{symbol}:USDT"
                try:
                    trades = exchange.fetch_my_trades(perp_symbol, limit=limit, since=since)
                    logger.debug(f"{exchange_name} {perp_symbol} 永续成交: {len(trades)}笔")
                except Exception as e:
                    logger.debug(f"{exchange_name} {perp_symbol} 永续成交失败: {e}")
            
            return trades
            
        except Exception as e:
            logger.error(f"❌ {exchange_name} {symbol} 获取成交失败: {e}")
            return []
    
    def fetch_market_trades(self, exchange_name: str, symbol: str,
                           limit: int = 1000) -> List[Dict]:
        """获取平台公开市场成交（模式二，不需要密钥）"""
        if exchange_name not in self.public_exchanges:
            logger.error(f"❌ {exchange_name} 未初始化")
            return []
        
        exchange = self.public_exchanges[exchange_name]
        
        try:
            trades = exchange.fetch_trades(symbol, limit=limit)
            logger.debug(f"{exchange_name} {symbol} 市场成交: {len(trades)}笔")
            return trades
        except Exception as e:
            logger.error(f"❌ {exchange_name} {symbol} 市场成交失败: {e}")
            return []
    
    def save_my_trades_to_db(self, trades: List[Dict], exchange_name: str):
        """保存我们的真实成交到数据库（模式一）"""
        if not trades:
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                exchange TEXT,
                symbol TEXT,
                side TEXT,
                type TEXT,
                price REAL,
                amount REAL,
                cost REAL,
                fee REAL,
                fee_currency TEXT,
                order_id TEXT,
                position_id TEXT,
                strategy TEXT,
                status TEXT,
                data_source TEXT DEFAULT 'my_trades'
            )
        ''')
        
        inserted = 0
        for trade in trades:
            try:
                cursor.execute('''
                    INSERT INTO historical_trades 
                    (timestamp, exchange, symbol, side, type, price, amount, cost, fee, fee_currency, order_id, position_id, strategy, status, data_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade.get('timestamp'),
                    exchange_name,
                    trade.get('symbol'),
                    trade.get('side'),
                    trade.get('type', 'market'),
                    trade.get('price'),
                    trade.get('amount'),
                    trade.get('cost'),
                    trade.get('fee', {}).get('cost', 0) if isinstance(trade.get('fee'), dict) else trade.get('fee', 0),
                    trade.get('fee', {}).get('currency', 'USDT') if isinstance(trade.get('fee'), dict) else 'USDT',
                    trade.get('order'),
                    trade.get('positionId', trade.get('position_id')),
                    'historical',
                    'filled',
                    'my_trades'
                ))
                inserted += 1
            except Exception as e:
                logger.debug(f"插入成交失败: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ {exchange_name} 保存{inserted}笔我们的成交记录")
        return inserted
    
    def save_market_trades_to_db(self, trades: List[Dict], exchange_name: str):
        """保存平台公开市场成交到数据库（模式二）"""
        if not trades:
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                exchange TEXT,
                symbol TEXT,
                side TEXT,
                price REAL,
                amount REAL,
                cost REAL,
                order_id TEXT
            )
        ''')
        
        inserted = 0
        for trade in trades:
            try:
                cursor.execute('''
                    INSERT INTO market_trades 
                    (timestamp, exchange, symbol, side, price, amount, cost, order_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade.get('timestamp'),
                    exchange_name,
                    trade.get('symbol'),
                    trade.get('side'),
                    trade.get('price'),
                    trade.get('amount'),
                    trade.get('cost', trade.get('price', 0) * trade.get('amount', 0)),
                    trade.get('id', trade.get('order'))
                ))
                inserted += 1
            except Exception as e:
                logger.debug(f"插入市场成交失败: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ {exchange_name} 保存{inserted}笔市场成交记录")
        return inserted
    
    def fetch_and_save_all(self, symbols: List[str]):
        """批量获取并保存所有币种的历史成交（双模式）"""
        total_saved = 0
        
        for ex_name in self.exchanges.keys():
            logger.info(f"📊 开始采集 {ex_name} 历史成交（模式一：我们的成交）...")
            
            for symbol in symbols:
                try:
                    trades = self.fetch_my_trades(ex_name, symbol, limit=50)
                    if trades:
                        saved = self.save_my_trades_to_db(trades, ex_name)
                        total_saved += saved
                    
                    time.sleep(0.3)  # 限速
                except Exception as e:
                    logger.error(f"❌ {ex_name} {symbol} 失败: {e}")
                    time.sleep(0.5)
        
        for ex_name in self.public_exchanges.keys():
            logger.info(f"📊 开始采集 {ex_name} 市场成交（模式二：平台公开成交）...")
            
            for symbol in symbols:
                try:
                    trades = self.fetch_market_trades(ex_name, symbol, limit=500)
                    if trades:
                        saved = self.save_market_trades_to_db(trades, ex_name)
                        total_saved += saved
                    
                    time.sleep(0.3)
                except Exception as e:
                    logger.error(f"❌ {ex_name} {symbol} 失败: {e}")
                    time.sleep(0.5)
        
        logger.info(f"✅ 历史成交采集完成，共保存{total_saved}笔")
        return total_saved
    
    def get_historical_stats(self) -> Dict:
        """获取历史成交统计（双模式）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        for ex in ['gate', 'bitget', 'htx']:
            # 模式一：我们的成交
            cursor.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN side='buy' THEN cost ELSE 0 END) as buy_cost,
                       SUM(CASE WHEN side='sell' THEN cost ELSE 0 END) as sell_cost
                FROM historical_trades
                WHERE exchange=? AND data_source='my_trades'
            ''', (ex,))
            row = cursor.fetchone()
            if row and row[0] > 0:
                stats[f'{ex}_my_trades'] = {
                    'total_trades': row[0],
                    'buy_cost': row[1] or 0,
                    'sell_cost': row[2] or 0,
                    'net_pnl': (row[2] or 0) - (row[1] or 0),
                }
            
            # 模式二：市场成交
            cursor.execute('''
                SELECT COUNT(*) as total
                FROM market_trades
                WHERE exchange=?
            ''', (ex,))
            row = cursor.fetchone()
            if row and row[0] > 0:
                stats[f'{ex}_market_trades'] = {
                    'total_trades': row[0],
                }
        
        conn.close()
        return stats
