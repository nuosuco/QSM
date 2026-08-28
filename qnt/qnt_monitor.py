#!/usr/bin/env python3
"""QNT交易系统监控 - 主动推送交易情况"""
import os
import sys
import sqlite3
import ccxt
from datetime import datetime
from pathlib import Path

DB_PATH = "/root/SOM/data/trading_system/adaptive.db"
LOG_FILE = "/root/SOM/qnt/qnt_monitor.log"
THRESHOLD = 0.17

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def get_balance():
    balances = {}
    total = 0.0
    try:
        bitget = ccxt.bitget({
            'apiKey': os.getenv('BITGET_API_KEY', ''),
            'secret': os.getenv('BITGET_API_SECRET', ''),
            'password': os.getenv('BITGET_API_PASSPHRASE', ''),
            'enableRateLimit': True
        })
        bal = bitget.fetch_balance()
        usdt = bal['USDT']['total'] if 'USDT' in bal else 0
        balances['Bitget'] = usdt
        total += usdt
    except Exception as e:
        balances['Bitget'] = 0
    try:
        htx = ccxt.htx({
            'apiKey': os.getenv('HTX_API_KEY', ''),
            'secret': os.getenv('HTX_API_SECRET', ''),
            'enableRateLimit': True
        })
        bal = htx.fetch_balance()
        usdt = bal['USDT']['total'] if 'USDT' in bal else 0
        balances['HTX'] = usdt
        total += usdt
    except Exception as e:
        balances['HTX'] = 0
    return balances, total

def get_spread_stats(hours=1):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT exchange, symbol, 
               MAX(spread_pct) as max_spread,
               AVG(spread_pct) as avg_spread,
               COUNT(*) as samples
        FROM market_data 
        WHERE timestamp > strftime('%s', 'now', '-{hours} hour')
        GROUP BY exchange, symbol
        ORDER BY max_spread DESC
    """)
    results = []
    for row in cursor.fetchall():
        results.append({
            'exchange': row[0],
            'symbol': row[1],
            'max_spread': row[2],
            'avg_spread': row[3],
            'samples': row[4]
        })
    conn.close()
    return results

def get_trade_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mode, 
               COUNT(*) as total,
               SUM(CASE WHEN executed=1 AND actual_profit>0 THEN 1 ELSE 0 END) as wins,
               COALESCE(SUM(actual_profit), 0) as profit
        FROM engine_signals 
        GROUP BY mode
    """)
    stats = {}
    for row in cursor.fetchall():
        stats[row[0]] = {
            'total': row[1],
            'wins': row[2] if row[2] else 0,
            'profit': row[3] if row[3] else 0
        }
    conn.close()
    return stats

def check_opportunities():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT exchange, symbol, spread_pct, spot_last, future_last, timestamp
        FROM market_data 
        WHERE spread_pct > ? 
        AND timestamp > strftime('%s', 'now', '-5 minutes')
        ORDER BY spread_pct DESC
        LIMIT 5
    """, (THRESHOLD,))
    opportunities = []
    for row in cursor.fetchall():
        opportunities.append({
            'exchange': row[0],
            'symbol': row[1],
            'spread': row[2],
            'spot': row[3],
            'future': row[4],
            'timestamp': row[5]
        })
    conn.close()
    return opportunities

def generate_report():
    log("=" * 60)
    log("📊 QNT交易系统监控报告")
    log("=" * 60)
    
    log("\n【系统状态】")
    try:
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'python.*adaptive' in line and 'grep' not in line:
                parts = line.split()
                log(f"  ✅ PID: {parts[1]} | CPU: {parts[2]}% | 内存: {parts[3]}%")
                break
        else:
            log("  ❌ 进程未运行")
    except Exception as e:
        log(f"  ❌ 检查失败: {e}")
    
    log("\n【账户余额】")
    balances, total = get_balance()
    for ex, bal in balances.items():
        log(f"  {ex}: ${bal:.4f} USDT")
    log(f"  💰 总权益: ${total:.4f} USDT")
    
    log("\n【交易统计】")
    stats = get_trade_stats()
    for mode, data in stats.items():
        win_rate = (data['wins'] / data['total'] * 100) if data['total'] > 0 else 0
        profit = data['profit'] if data['profit'] else 0
        log(f"  {mode}: {data['total']}笔 | 胜率{win_rate:.1f}% | 利润${profit:.4f}")
    
    log("\n【价差监控（最近1小时）】")
    spreads = get_spread_stats(1)
    if spreads:
        for s in spreads[:10]:
            flag = "🔥" if s['max_spread'] > THRESHOLD else ""
            log(f"  {s['exchange']:8} {s['symbol']:12} 最高{s['max_spread']:6.4f}% 平均{s['avg_spread']:6.4f}% {flag}")
    else:
        log("  暂无数据")
    
    log("\n【交易机会】")
    opportunities = check_opportunities()
    if opportunities:
        for opp in opportunities:
            log(f"  🔥 发现机会！{opp['exchange']} {opp['symbol']} 价差{opp['spread']:.4f}%")
        return opportunities
    else:
        log("  当前无超阈值机会（需>0.17%）")
        return []
    
    log("\n" + "=" * 60)

if __name__ == "__main__":
    opportunities = generate_report()
    if opportunities:
        print("\n🔥 OPPORTUNITY_FOUND 🔥")
        for opp in opportunities:
            print(f"  {opp['exchange']} {opp['symbol']}: {opp['spread']:.4f}%")
        sys.exit(1)
    sys.exit(0)
