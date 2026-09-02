"""市场成交数据采集任务（每小时运行）
从三个平台收集公开市场成交数据，用于双模式回测"""
import sys
sys.path.insert(0, '/root/SOM/qnt/adaptive_system')

import ccxt
import sqlite3
import time
import logging
from datetime import datetime
from config import SystemConfig

logger = logging.getLogger('MarketTradeCollector')

class MarketTradeCollector:
    """市场成交数据采集器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.exchanges = {}
        
    def init_exchange(self, name: str):
        """初始化公开交易所（不需要API密钥）"""
        try:
            exchange_class = getattr(ccxt, name)
            exchange = exchange_class({
                'enableRateLimit': True,
                'timeout': 30000,
            })
            self.exchanges[name] = exchange
            logger.info(f"✅ {name} 初始化成功")
            return True
        except Exception as e:
            logger.error(f"❌ {name} 初始化失败: {e}")
            return False
    
    def fetch_market_trades(self, exchange_name: str, symbol: str, limit: int = 500):
        """获取平台公开市场成交"""
        if exchange_name not in self.exchanges:
            return []
        
        exchange = self.exchanges[exchange_name]
        
        try:
            trades = exchange.fetch_trades(symbol, limit=limit)
            logger.debug(f"{exchange_name} {symbol}: {len(trades)}笔")
            return trades
        except Exception as e:
            logger.error(f"❌ {exchange_name} {symbol} 失败: {e}")
            return []
    
    def save_trades_to_db(self, trades: list, exchange_name: str):
        """保存到数据库"""
        if not trades:
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表
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
                logger.debug(f"插入失败: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ {exchange_name} 保存{inserted}笔")
        return inserted
    
    def run(self, symbols: list):
        """运行采集任务"""
        logger.info("📊 开始采集市场成交数据...")
        
        total_saved = 0
        for ex_name in ['gate', 'bitget', 'htx']:
            if ex_name not in self.exchanges:
                self.init_exchange(ex_name)
            
            for symbol in symbols:
                trades = self.fetch_market_trades(ex_name, symbol, limit=500)
                if trades:
                    saved = self.save_trades_to_db(trades, ex_name)
                    total_saved += saved
                
                time.sleep(0.3)  # 限速
        
        logger.info(f"✅ 采集完成，共保存{total_saved}笔市场成交")
        return total_saved


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # 加载配置
    config = SystemConfig.load()
    db_path = config.data.db_path
    
    # 交易对列表（只加载现货）
    symbols = [s.replace('/USDT', '') + '/USDT' for s in config.data.symbols]
    
    collector = MarketTradeCollector(db_path)
    collector.run(symbols)
