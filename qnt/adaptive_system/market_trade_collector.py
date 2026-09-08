"""
市场成交数据采集器 - 获取三个平台的公开市场成交（模式二）
不需要API密钥，使用CCXT fetch_trades API
每个平台独立采集，数据独立存储
"""
import logging
import time
from typing import Dict, List
import ccxt
from .db_utils import get_connection

logger = logging.getLogger('MarketTradeCollector')


class MarketTradeCollector:
    """三平台市场成交数据采集器（模式二）"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.exchanges = {}
        self.platform_stats = {p: {'collected': 0, 'errors': 0} for p in ['gate', 'htx', 'bitget']}
        
    def init_exchange(self, name: str):
        """初始化交易所（无密钥）"""
        try:
            cls = getattr(ccxt, name, None)
            if not cls:
                logger.error(f"不支持的交易所: {name}")
                return False
            exchange = cls({'enableRateLimit': True, 'timeout': 15000})
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
            return []
        exchange = self.exchanges[exchange_name]
        all_trades = []
        
        # 现货成交
        try:
            spot = exchange.fetch_trades(symbol, limit=limit)
            if spot:
                all_trades.extend(spot)
        except Exception as e:
            logger.debug(f"{exchange_name} {symbol} 现货成交失败: {e}")
        
        # 永续合约成交 (Bitget/Gate/HTX格式: BTC/USDT:USDT)
        base = symbol.split('/')[0]
        perp_symbol = f"{base}/USDT:USDT"
        try:
            perp = exchange.fetch_trades(perp_symbol, limit=limit)
            if perp:
                all_trades.extend(perp)
        except Exception as e:
            logger.debug(f"{exchange_name} {perp_symbol} 永续成交失败: {e}")
        
        self.platform_stats[exchange_name]['collected'] += len(all_trades)
        return all_trades
    
    def fetch_spread_data(self, exchange_name: str, symbol: str) -> Dict:
        """获取永续vs现货价差数据"""
        if exchange_name not in self.exchanges:
            return {}
        exchange = self.exchanges[exchange_name]
        
        result = {
            'symbol': symbol,
            'exchange': exchange_name,
            'spot_price': None,
            'perp_price': None,
            'spread_pct': 0.0
        }
        
        try:
            # 获取现货ticker
            spot_ticker = exchange.fetch_ticker(symbol)
            if spot_ticker and spot_ticker.get('last'):
                result['spot_price'] = float(spot_ticker['last'])
        except Exception as e:
            logger.debug(f"{exchange_name} {symbol} 现货行情失败: {e}")
        
        try:
            # 获取永续合约ticker (格式: BTC/USDT:USDT)
            base = symbol.split('/')[0]
            perp_symbol = f"{base}/USDT:USDT"
            perp_ticker = exchange.fetch_ticker(perp_symbol)
            if perp_ticker and perp_ticker.get('last'):
                result['perp_price'] = float(perp_ticker['last'])
        except Exception as e:
            logger.debug(f"{exchange_name} {perp_symbol} 永续行情失败: {e}")
        
        # 计算价差
        if result['spot_price'] and result['perp_price'] and result['perp_price'] > 0:
            result['spread_pct'] = (result['spot_price'] - result['perp_price']) / result['perp_price'] * 100
        
        return result
    
    def save_market_trades(self, trades: List[Dict], exchange_name: str):
        """保存市场成交到数据库"""
        if not trades:
            return 0
        
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        inserted = 0
        
        for trade in trades:
            try:
                timestamp = trade.get('timestamp')
                if not timestamp:
                    continue
                ts = timestamp / 1000 if timestamp > 1e12 else timestamp
                
                sym = trade.get('symbol', '')
                side = trade.get('side', '')
                price = trade.get('price', 0) or 0
                amount = trade.get('amount', 0) or 0
                cost = trade.get('cost') or (price * amount)
                order_id = str(trade.get('id', '') or trade.get('order', '') or '')
                
                if not order_id or not ts or not sym or not side:
                    continue
                
                # 去重
                cursor.execute(
                    "SELECT COUNT(*) FROM market_trades WHERE order_id=? AND exchange=?",
                    (order_id, exchange_name)
                )
                if cursor.fetchone()[0] > 0:
                    continue
                
                cursor.execute('''
                    INSERT INTO market_trades 
                    (timestamp, symbol, exchange, spread_pct, side, perp_price, spot_price, amount, cost, fee, pnl, pnl_pct, status, order_id)
                    VALUES (?, ?, ?, 0, ?, ?, ?, ?, ?, 0, 0, 0, 'collected', ?)
                ''', (ts, sym, exchange_name, side, price, price, amount, cost, order_id))
                inserted += 1
            except Exception as e:
                logger.debug(f"插入失败: {e}")
        
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
                    time.sleep(0.3)
                except Exception as e:
                    logger.error(f"❌ {ex_name} {symbol} 失败: {e}")
                    time.sleep(0.5)
        logger.info(f"✅ 市场成交采集完成，共保存{total_saved}笔")
        return total_saved
