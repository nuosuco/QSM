"""QNT v3 - 做市策略引擎（本地模拟模式）"""
import time
import sqlite3
import ccxt
from datetime import datetime
from typing import Dict, List

MAKER_FEE = 0.0004
SLIPPAGE = 0.0002
COST_PCT = (MAKER_FEE + SLIPPAGE) * 2 * 100
THRESHOLD_PCT = 0.12
MIN_PROFIT_PCT = 0.02
SCAN_INTERVAL = 2
POSITION_SIZE_USDT = 50
SIMULATED_BALANCE_USDT = 1000.0

class SimulatedMarketMaker:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        self.exchange = ccxt.bitget({'enableRateLimit': True, 'options': {'defaultType': 'swap'}})
        self.running = False
        self.trade_count = 0
        self.profit_count = 0
        self.loss_count = 0
        self.simulated_balance = SIMULATED_BALANCE_USDT
    
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS market_trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp REAL, symbol TEXT,
            spread_pct REAL, side TEXT, perp_price REAL, spot_price REAL,
            cost REAL, fee REAL, pnl REAL, pnl_pct REAL, status TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS simulated_balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp REAL, balance REAL, total_pnl REAL)''')
        self.conn.commit()
    
    def get_spread(self, symbol):
        try:
            swap = self.exchange.fetch_ticker(symbol.replace('/USDT', '/USDT:USDT'))
            spot = self.exchange.fetch_ticker(symbol)
            spread = (swap['last'] - spot['last']) / spot['last'] * 100
            return {'symbol': symbol, 'perp_price': swap['last'], 'spot_price': spot['last'], 'spread_pct': spread}
        except: return None
    
    def simulate_trade(self, data):
        spread = data['spread_pct']
        actual_profit = spread - COST_PCT
        if actual_profit < MIN_PROFIT_PCT: return None
        
        cost = POSITION_SIZE_USDT
        pnl = cost * actual_profit / 100
        fee = cost * COST_PCT / 100
        
        trade = {'timestamp': time.time(), 'symbol': data['symbol'],
                 'spread_pct': spread, 'side': 'buy' if spread > 0 else 'sell',
                 'perp_price': data['perp_price'], 'spot_price': data['spot_price'],
                 'cost': cost, 'fee': fee, 'pnl': pnl, 'pnl_pct': actual_profit, 'status': 'simulated'}
        
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO market_trades (timestamp, symbol, spread_pct, side, perp_price, spot_price, cost, fee, pnl, pnl_pct, status) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                      (trade['timestamp'], trade['symbol'], trade['spread_pct'], trade['side'], trade['perp_price'], trade['spot_price'], trade['cost'], trade['fee'], trade['pnl'], trade['pnl_pct'], trade['status']))
        self.conn.commit()
        
        self.trade_count += 1
        self.simulated_balance += pnl
        if pnl > 0: self.profit_count += 1
        else: self.loss_count += 1
        return trade
    
    def run(self, symbols=None):
        if not symbols: symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
        self.running = True
        print(f"\n🚀 QNT模拟做市引擎启动 (无需API)")
        print(f"   阈值: >{THRESHOLD_PCT}% | 最小净利: >{MIN_PROFIT_PCT}%")
        print(f"   模拟余额: ${self.simulated_balance:.2f}")
        
        last_scan = 0
        while self.running:
            try:
                if time.time() - last_scan < SCAN_INTERVAL: time.sleep(0.5); continue
                last_scan = time.time()
                
                print(f"\n{'='*60}\n📡 {datetime.now().strftime('%H:%M:%S')} | 余额: ${self.simulated_balance:.2f}")
                
                for symbol in symbols:
                    data = self.get_spread(symbol)
                    if not data: continue
                    
                    spread = data['spread_pct']
                    profit = spread - COST_PCT
                    
                    print(f"\n{symbol}: 永续${data['perp_price']:.2f} vs 现货${data['spot_price']:.2f} | 价差{spread:.4f}% | 净利{profit:+.4f}%", end='')
                    
                    if profit >= MIN_PROFIT_PCT:
                        trade = self.simulate_trade(data)
                        if trade: print(f" ✅ 模拟利润${trade['pnl']:.4f}")
                    else: print(" ❌")
                
                print(f"\n📊 交易:{self.trade_count}笔 盈利:{self.profit_count}次 亏损:{self.loss_count}次")
                
            except KeyboardInterrupt: break
            except Exception as e: print(f"⚠️ {e}"); time.sleep(5)

if __name__ == '__main__':
    engine = SimulatedMarketMaker('/root/SOM/data/trading_system/adaptive.db')
    engine.run()
