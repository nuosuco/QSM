"""修复market_trades的spread_pct数据"""
import sqlite3
import ccxt
import time
from datetime import datetime

DB_PATH = '/root/SOM/data/trading_system/adaptive.db'

def get_spread_data(exchange_name, symbol):
    """获取永续vs现货价差"""
    try:
        exchange = ccxt.__dict__[exchange_name]({
            'enableRateLimit': True,
            'timeout': 10000
        })
        
        # 获取现货价格
        spot_ticker = exchange.fetch_ticker(symbol)
        spot_price = float(spot_ticker.get('last', 0))
        
        # 获取永续价格
        perp_symbol = f"{symbol.split('/')[0]}:USDT"
        perp_ticker = exchange.fetch_ticker(perp_symbol)
        perp_price = float(perp_ticker.get('last', 0))
        
        if spot_price > 0 and perp_price > 0:
            spread_pct = (spot_price - perp_price) / perp_price * 100
            return {
                'spot_price': spot_price,
                'perp_price': perp_price,
                'spread_pct': spread_pct
            }
    except Exception as e:
        print(f"  ❌ {exchange_name} {symbol} 获取价差失败: {e}")
    
    return None

def main():
    print("="*60)
    print("🔧 修复market_trades价差数据")
    print("="*60)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取需要更新的币种
    symbols = cursor.execute("""
        SELECT DISTINCT symbol FROM market_trades 
        WHERE spread_pct = 0 OR spread_pct IS NULL
        LIMIT 20
    """).fetchall()
    
    print(f"需要更新的币种: {len(symbols)}个")
    print()
    
    # 交易所列表
    exchanges = ['gate', 'bitget', 'htx']
    
    updated = 0
    for sym_row in symbols:
        symbol = sym_row[0]
        print(f"处理 {symbol}:")
        
        for ex in exchanges:
            data = get_spread_data(ex, symbol)
            if data:
                # 更新最近500条记录
                cursor.execute("""
                    UPDATE market_trades 
                    SET spread_pct = ?, perp_price = ?, spot_price = ?
                    WHERE symbol = ? AND exchange = ? AND (spread_pct = 0 OR spread_pct IS NULL)
                    ORDER BY timestamp DESC
                    LIMIT 500
                """, (data['spread_pct'], data['perp_price'], data['spot_price'], symbol, ex))
                
                rows = cursor.rowcount
                if rows > 0:
                    print(f"  {ex}: 价差{data['spread_pct']:+.4f}%，更新{rows}条")
                    updated += rows
            
            time.sleep(0.3)  # 限速
        
        print()
    
    conn.commit()
    conn.close()
    
    print(f"✅ 共更新{updated}条记录的价差数据")

if __name__ == '__main__':
    main()
