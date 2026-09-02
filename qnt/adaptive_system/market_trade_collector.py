"""
市场成交数据采集器 - 获取三个平台的公开市场成交（模式二）
不需要API密钥，使用CCXT fetch_trades API
每个平台独立采集，数据独立存储
"""
import sqlite3
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
import ccxt

logger = logging.getLogger('MarketTradeCollector')

# market_trades表字段（与data_collector一致）
# id, timestamp, symbol, exchange, spread_pct, side, perp_price, spot_price, amount, cost, fee, pnl, pnl_pct, status, order_id


class MarketTradeCollector:
    """三平台市场成交数据采集器（模式二）"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.exchanges = {}  # {name: ccxt_exchange}
        self.platform_stats = {p: {'collected': 0, 'errors': 0} for p in ['gate', 'htx', 'bitget']}
        
    def init_exchange(self, name: str):
        """初始化交易所（无密钥）"""
        try:
            cls = getattr(ccxt, name, None)
            if not cls:
                logger.error(f"不支持的交易所: {name}")
                return False
            
            exchange = cls({'enableRateLimit': True, 'timeout': 10000})
            # 测试连接
            exchange.fetch_ticker('BTC/USDT')
            self.exchanges[name] = exchange
            logger.info(f"✅ {name} 公开市场连接器初始化成功")
            return True
        except Exception as e:
            logger.error(f"❌ {name} 初始化失败: {e}")
            return False
    
    def fetch_market_trades(self, exchange_name: str, symbol: str, limit: int = 500) -> List[Dict]:
        """获取平台公开市场成交"""
        if exchange_name not in self.exchanges:
            logger.error(f"{exchange_name} 未初始化")
            return []
        
        exchange = self.exchanges[exchange_name]
        
        try:
            # 获取现货成交
            spot_trades = exchange.fetch_trades(symbol, limit=limit)
            
            # 获取永续合约成交
            perp_symbol = f"{symbol.split('/')[0]}:USDT"
            perp_trades = []
            try:
                perp_trades = exchange.fetch_trades(perp_symbol, limit=limit)
            except Exception as e:
                logger.debug(f"{exchange_name} {perp_symbol} 永续成交失败: {e}")
            
            all_trades = spot_trades + perp_trades
            self.platform_stats[exchange_name]['collected'] += len(all_trades)
            
            logger.debug(f"{exchange_name} {symbol}: {len(all_trades)}笔市场成交")
            return all_trades
            
        except Exception as e:
            self.platform_stats[exchange_name]['errors'] += 1
            logger.error(f"❌ {exchange_name} {symbol} 获取市场成交失败: {e}")
            return []
    
    def save_market_trades(self, trades: List[Dict], exchange_name: str):
        """保存市场成交到数据库"""
        if not trades:
            return 0
        
        conn = sqlite3.connect(self.db_path, timeout=10)
        cursor = conn.cursor()
        
        inserted = 0
        for trade in trades:
            try:
                # 提取字段（market_trades表结构）
                timestamp = trade.get('timestamp') / 1000 if trade.get('timestamp') else None  # ms→s
                sym = trade.get('symbol')
                side = trade.get('side')
                price = trade.get('price')
                amount = trade.get('amount')
                cost = trade.get('cost', price * amount if price and amount else 0)
                order_id = trade.get('id') or trade.get('order')
                
                if not timestamp or not sym or not side:
                    continue
                
                # 检查是否已存在（避免重复）
                if order_id:
                    cursor.execute(
                        "SELECT COUNT(*) FROM market_trades WHERE order_id=? AND exchange=?",
                        (str(order_id), exchange_name)
                    )
                    if cursor.fetchone()[0] > 0:
                        continue
                
                # 插入（market_trades表字段：timestamp, symbol, exchange, spread_pct, side, perp_price, spot_price, amount, cost, fee, pnl, pnl_pct, status, order_id）
                cursor.execute('''
                    INSERT INTO market_trades 
                    (timestamp, symbol, exchange, spread_pct, side, perp_price, spot_price, amount, cost, fee, pnl, pnl_pct, status, order_id)
                    VALUES (?, ?, ?, NULL, ?, NULL, ?, ?, ?, NULL, NULL, NULL, 'collected', ?)
                ''', (
                    timestamp,
                    sym,
                    exchange_name,
                    side,
                    price if side == 'buy' else None,  # spot_price (buy)
                    price if side == 'sell' else None,  # perp_price (sell)
                    amount,
                    cost,
                    str(order_id)
                ))
                inserted += 1
            except Exception as e:
                logger.debug(f"插入市场成交失败: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ {exchange_name} 保存{inserted}笔市场成交")
        return inserted
    
    def collect_all(self, symbols: List[str]):
        """批量采集所有币种的市场成交"""
        total_saved = 0
        
        for ex_name in self.exchanges.keys():
            logger.info(f"📊 开始采集 {ex_name} 市场成交（模式二）...")
            
            for symbol in symbols:
                try:
                    trades = self.fetch_market_trades(ex_name, symbol, limit=300)
                    if trades:
                        saved = self.save_market_trades(trades, ex_name)
                        total_saved += saved
                    
                    time.sleep(0.2)  # 限速
                except Exception as e:
                    logger.error(f"❌ {ex_name} {symbol} 失败: {e}")
                    time.sleep(0.5)
        
        logger.info(f"✅ 市场成交采集完成，共保存{total_saved}笔")
        return total_saved
    
    def get_stats(self) -> Dict:
        """获取采集统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        for ex in ['gate', 'htx', 'bitget']:
            # 采集统计
            collected = self.platform_stats.get(ex, {}).get('collected', 0)
            errors = self.platform_stats.get(ex, {}).get('errors', 0)
            
            # 数据库中的数量
            cursor.execute("SELECT COUNT(*) FROM market_trades WHERE exchange=?", (ex,))
            db_count = cursor.fetchone()[0]
            
            stats[ex] = {
                'collected': collected,
                'errors': errors,
                'db_count': db_count,
            }
        
        conn.close()
        return stats
