"""
QNT核心引擎 - 多交易所支持
连接Binance US + OKX + KuCoin，跨所价差套利
"""

import ccxt
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import time

class QNTEngine:
    """量子交易系统核心引擎 - 多交易所版本"""
    
    def __init__(self):
        self.db_path = '/root/SOM/data/trading_system/qnt.db'
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.init_all_exchanges()
        self._init_db()
        self._log('QNT多交易所引擎初始化完成', module='engine')
    
    def init_all_exchanges(self):
        """初始化所有可用交易所"""
        candidates = [
            ('binanceus', 'Binance US'),
            ('okx', 'OKX'),
            ('kucoin', 'KuCoin'),
        ]
        
        for name, desc in candidates:
            try:
                cls = getattr(ccxt, name)
                ex = cls({'enableRateLimit': True, 'timeout': 10000})
                # 验证连接
                t = ex.fetch_ticker('BTC/USDT')
                self.exchanges[name] = ex
                self._log(f'✅ {desc}连接成功 (BTC: ${float(t["last"]):,.2f})', module='exchange')
            except Exception as e:
                self._log(f'❌ {desc}连接失败: {e}', 'ERROR', 'exchange')
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qnt_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange TEXT, symbol TEXT, side TEXT, type TEXT,
                price REAL, amount REAL, cost REAL, fee REAL, profit REAL,
                timestamp TIMESTAMP, strategy TEXT, status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qnt_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange TEXT, symbol TEXT, side TEXT, price REAL,
                confidence REAL, reason TEXT, source TEXT,
                timestamp TIMESTAMP, executed INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qnt_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT, message TEXT, module TEXT, timestamp TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qnt_spread_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT, scan_time TIMESTAMP,
                binanceus_price REAL, okx_price REAL, kucoin_price REAL,
                best_buy TEXT, best_sell TEXT, spread_pct REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _log(self, message: str, level: str = 'INFO', module: str = 'engine'):
        """记录日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO qnt_logs (level, message, module, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (level, message, module, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        print(f"[{level}] {message}")
    
    def get_ticker(self, symbol: str, exchange: str = None) -> Optional[Dict]:
        """获取实时行情"""
        if exchange:
            if exchange not in self.exchanges:
                return None
            try:
                ticker = self.exchanges[exchange].fetch_ticker(symbol)
                return self._parse_ticker(ticker, exchange)
            except Exception as e:
                self._log(f'获取{symbol}行情失败({exchange}): {e}', 'ERROR', 'market')
                return None
        
        # 返回所有交易所的行情
        result = {}
        for name, ex in self.exchanges.items():
            try:
                ticker = ex.fetch_ticker(symbol)
                result[name] = self._parse_ticker(ticker, name)
                time.sleep(0.2)
            except Exception as e:
                self._log(f'获取{symbol}行情失败({name}): {e}', 'WARNING', 'market')
        return result if result else None
    
    def _parse_ticker(self, ticker, exchange: str) -> Dict:
        """解析ticker数据"""
        return {
            'symbol': ticker.get('symbol', 'N/A'),
            'exchange': exchange,
            'last': float(ticker.get('last', 0)),
            'bid': float(ticker.get('bid', 0)),
            'ask': float(ticker.get('ask', 0)),
            'spread': float(ticker.get('ask', 0)) - float(ticker.get('bid', 0)),
            'volume': ticker.get('quoteVolume', 0),
            'change': ticker.get('percentage', 0),
            'high': float(ticker.get('high', 0)),
            'low': float(ticker.get('low', 0)),
            'open': float(ticker.get('open', 0)),
            'timestamp': ticker.get('datetime', '')
        }
    
    def get_orderbook(self, symbol: str, limit: int = 20, exchange: str = 'binanceus') -> Optional[Dict]:
        """获取深度数据（KuCoin需要limit=20）"""
        if exchange not in self.exchanges:
            return None
        try:
            ex = self.exchanges[exchange]
            # KuCoin限制limit必须为20或100
            if exchange == 'kucoin' and limit != 20 and limit != 100:
                limit = 20
            ob = ex.fetch_order_book(symbol, limit)
            
            # 统一处理: 所有交易所都返回 [price, amount, ...] 格式
            # OKX有3个值[price, amount, num], 其他可能有更多
            bids = []
            asks = []
            for item in ob['bids']:
                price = float(item[0])
                amount = float(item[1])
                bids.append((price, amount))
            for item in ob['asks']:
                price = float(item[0])
                amount = float(item[1])
                asks.append((price, amount))
            
            return {
                'symbol': symbol,
                'exchange': exchange,
                'bids': bids,
                'asks': asks,
                'spread': float(asks[0][0]) - float(bids[0][0]) if asks and bids else 0,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self._log(f'获取{symbol}深度失败({exchange}): {e}', 'ERROR', 'market')
            return None
    
    def scan_cross_exchange_spread(self, symbol: str = 'BTC/USDT') -> Optional[Dict]:
        """扫描跨所价差"""
        prices = {}
        orderbooks = {}
        
        for name, ex in self.exchanges.items():
            try:
                ticker = ex.fetch_ticker(symbol)
                prices[name] = float(ticker['last'])
                
                ob = self.get_orderbook(symbol, exchange=name)
                if ob:
                    orderbooks[name] = {
                        'bid': ob['bids'][0][0] if ob['bids'] else 0,
                        'ask': ob['asks'][0][0] if ob['asks'] else 0,
                        'bid_vol': ob['bids'][0][1] if ob['bids'] else 0,
                        'ask_vol': ob['asks'][0][1] if ob['asks'] else 0,
                    }
                time.sleep(0.3)
            except Exception as e:
                self._log(f'{name}获取{symbol}失败: {e}', 'WARNING', 'scanner')
        
        if len(prices) < 2:
            return None
        
        # 找最佳买卖点
        sorted_prices = sorted(prices.items(), key=lambda x: x[1])
        buy_ex, buy_price = sorted_prices[0]
        sell_ex, sell_price = sorted_prices[-1]
        spread_pct = (sell_price - buy_price) / buy_price * 100
        
        # 保存扫描结果到数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO qnt_spread_scans 
            (symbol, scan_time, binanceus_price, okx_price, kucoin_price, best_buy, best_sell, spread_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol, datetime.now().isoformat(),
            prices.get('binanceus'), prices.get('okx'), prices.get('kucoin'),
            buy_ex, sell_ex, spread_pct
        ))
        conn.commit()
        conn.close()
        
        return {
            'symbol': symbol,
            'scan_time': datetime.now().isoformat(),
            'prices': prices,
            'buy_exchange': buy_ex,
            'buy_price': buy_price,
            'sell_exchange': sell_ex,
            'sell_price': sell_price,
            'spread_pct': spread_pct,
            'orderbooks': orderbooks,
            'is_opportunity': spread_pct > 0.1  # 价差超过0.1%算机会
        }
    
    def scan_all_symbols(self) -> List[Dict]:
        """扫描所有主要币种"""
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT']
        results = []
        
        for symbol in symbols:
            try:
                spread = self.scan_cross_exchange_spread(symbol)
                if spread:
                    results.append(spread)
                time.sleep(0.5)
            except Exception as e:
                self._log(f'扫描{symbol}失败: {e}', 'WARNING', 'scanner')
        
        return results
    
    def get_market_summary(self) -> Dict:
        """获取市场摘要"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'connected_exchanges': list(self.exchanges.keys()),
            'status': 'running',
            'stats': {name: 'active' for name in self.exchanges}
        }
        return summary


if __name__ == '__main__':
    engine = QNTEngine()
    print("=" * 70)
    print("      🌐 QNT多交易所量子交易系统")
    print("=" * 70)
    
    print(f"\n📡 已连接交易所: {list(engine.exchanges.keys())}")
    
    # 扫描跨所价差
    print("\n" + "-" * 70)
    print("🔍 跨所价差扫描:")
    print("-" * 70)
    
    opportunities = engine.scan_all_symbols()
    
    if opportunities:
        print(f"\n🎯 发现 {len(opportunities)} 个价差异常:\n")
        for opp in sorted(opportunities, key=lambda x: x['spread_pct'], reverse=True):
            if opp['is_opportunity']:
                icon = "🔥" if opp['spread_pct'] > 0.2 else "⚠️"
                print(f"  {icon} {opp['symbol']}")
                print(f"     买: {opp['buy_exchange']} @ ${opp['buy_price']:,.2f}")
                print(f"     卖: {opp['sell_exchange']} @ ${opp['sell_price']:,.2f}")
                print(f"     价差: {opp['spread_pct']:.4f}%")
                print()
            else:
                print(f"  ✅ {opp['symbol']}: 价差{opp['spread_pct']:.4f}% (正常)")
    else:
        print("\n✅ 所有币种价差正常")
    
    # 打印价格对照表
    print("-" * 70)
    print("📊 各交易所BTC价格对照:")
    print("-" * 70)
    for symbol in ['BTC/USDT']:
        tickers = engine.get_ticker(symbol)
        if tickers:
            for name, t in tickers.items():
                print(f"  {name:12s}: ${t['last']:>12,.2f}  买${t['bid']:,.2f} 卖${t['ask']:,.2f}")
    
    print("\n" + "=" * 70)
    print("✅ 扫描完成")
    print("=" * 70)
