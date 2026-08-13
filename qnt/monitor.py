#!/usr/bin/env python3.11
"""
QNT 实时监控系统 v2.0
- 持续记录成交数据
- 检测异常价格（乌龙指）
- 发现机会时输出警报
"""
import ccxt
import sqlite3
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import statistics

# 加载环境变量
env_file = Path.home() / '.qnt_env'
for line in open(env_file):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, _, v = line.partition('=')
        os.environ[k.strip()] = v.strip().strip('"').strip("'")

key = os.getenv('BITGET_API_KEY')
secret = os.getenv('BITGET_API_SECRET')
passphrase = os.getenv('BITGET_API_PASSPHRASE', 'qntsomtop')

DB_PATH = '/root/SOM/data/trading_system/qnt.db'
LOG_FILE = '/root/SOM/qnt/monitor.log'

# 监控币种列表
WATCHLIST = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT',
    'RVN/USDT', 'XRP/USDT', 'ADA/USDT',
    'DOGE/USDT', 'DOT/USDT', 'MATIC/USDT',
    'AVAX/USDT', 'LINK/USDT', 'UNI/USDT',
    'ATOM/USDT', 'LTC/USDT', 'BCH/USDT',
]

def log(msg):
    ts = datetime.utcnow().isoformat()
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(line + '\n')
    except:
        pass

class QNTMonitor:
    def __init__(self):
        self.bitget = ccxt.bitget({
            'apiKey': key,
            'secret': secret,
            'password': passphrase,
            'enableRateLimit': True
        })
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._init_db()
        self.tracked_symbols = set()
        
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                exchange TEXT NOT NULL DEFAULT 'bitget',
                timestamp TEXT NOT NULL,
                price REAL NOT NULL,
                amount REAL NOT NULL,
                side TEXT NOT NULL,
                trade_id TEXT,
                is_outlier INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                avg_price REAL,
                std_dev REAL,
                min_price REAL,
                max_price REAL,
                sample_count INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outlier_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                price REAL NOT NULL,
                expected_price REAL NOT NULL,
                deviation_pct REAL NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                action_taken TEXT DEFAULT 'PENDING'
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_symbol ON trade_log(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_time ON trade_log(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_outlier_symbol ON outlier_alerts(symbol)')
        self.conn.commit()
        
    def fetch_trades(self, symbol, limit=200):
        try:
            return self.bitget.fetch_trades(symbol, limit=limit)
        except Exception as e:
            log(f"获取{symbol}失败: {e}")
            return []
            
    def monitor_symbol(self, symbol):
        trades = self.fetch_trades(symbol)
        if not trades or len(trades) < 20:
            return []
            
        # 保存成交记录
        new_count = 0
        for t in trades:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO trade_log (symbol, exchange, timestamp, price, amount, side, trade_id) VALUES (?,?,?,?,?,?,?)',
                (symbol, 'bitget', t['datetime'], float(t['price']), float(t['amount']), t['side'], t['id'])
            )
            if cursor.rowcount:
                new_count += 1
        self.conn.commit()
        self.tracked_symbols.add(symbol)
        
        # 检测异常
        prices = [float(t['price']) for t in trades]
        avg = statistics.mean(prices)
        std = statistics.stdev(prices) if len(prices) > 1 else 0
        
        # 保存统计快照
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO price_stats (symbol, timestamp, avg_price, std_dev, min_price, max_price, sample_count)
            VALUES (?,?,?,?,?,?,?)
        ''', (symbol, datetime.utcnow().isoformat(), avg, std, min(prices), max(prices), len(prices)))
        self.conn.commit()
        
        # 3σ异常检测
        threshold = max(3 * std, avg * 0.001)  # 至少0.1%偏离
        outliers = []
        for t in trades:
            p = float(t['price'])
            dev = abs(p - avg)
            if dev > threshold:
                alert = {
                    'symbol': symbol,
                    'timestamp': t['datetime'],
                    'price': p,
                    'expected_price': avg,
                    'deviation_pct': dev / avg * 100,
                    'side': t['side'],
                    'amount': float(t['amount'])
                }
                outliers.append(alert)
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO outlier_alerts 
                    (symbol, timestamp, price, expected_price, deviation_pct, side, amount, action_taken)
                    VALUES (?,?,?,?,?,?,?,?)
                ''', (symbol, t['datetime'], p, avg, dev/avg*100, t['side'], float(t['amount']), 'PENDING'))
                self.conn.commit()
                
                # 标记已处理的成交
                cursor.execute('UPDATE trade_log SET is_outlier=1 WHERE trade_id=?', (t['id'],))
                self.conn.commit()
                
        return outliers
        
    def run(self, interval=15):
        log("=" * 50)
        log("QNT实时监控启动")
        log(f"监控币种: {len(WATCHLIST)}个")
        log(f"异常阈值: 3σ或0.1%")
        log("=" * 50)
        
        while True:
            all_outliers = []
            for symbol in WATCHLIST:
                try:
                    outliers = self.monitor_symbol(symbol)
                    all_outliers.extend(outliers)
                except Exception as e:
                    log(f"{symbol}监控异常: {e}")
            
            if all_outliers:
                log(f"\n{'='*50}")
                log(f"发现 {len(all_outliers)} 个异常!")
                for a in all_outliers:
                    log(f"🚨 {a['symbol']} {a['side'].upper()} ${a['price']:,.4f} @ {a['timestamp']}")
                    log(f"   预期: ${a['expected_price']:,.4f} 偏离: {a['deviation_pct']:.2f}%")
                    log(f"   数量: {a['amount']}")
                log(f"{'='*50}\n")
            else:
                # 每30轮输出一次状态
                log(f"✓ 扫描完成 - 当前监控: {len(self.tracked_symbols)}个币种")
                
            time.sleep(interval)
            
    def close(self):
        self.conn.close()

if __name__ == '__main__':
    monitor = QNTMonitor()
    try:
        monitor.run()
    except KeyboardInterrupt:
        log("监控已停止")
    finally:
        monitor.close()
