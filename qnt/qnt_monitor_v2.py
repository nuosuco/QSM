#!/usr/bin/env python3
"""QNT系统监控脚本 - 检查回测/模拟盈亏状态"""

import sqlite3
import subprocess
import sys
from datetime import datetime

DB_PATH = '/root/SOM/data/trading_system/adaptive.db'

def get_db_stats():
    """获取数据库统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 回测统计
    cursor.execute("""
        SELECT 
            exchange,
            COUNT(*) as total,
            SUM(CASE WHEN status='closed' THEN 1 ELSE 0 END) as closed,
            ROUND(SUM(CASE WHEN status='closed' AND pnl IS NOT NULL THEN pnl ELSE 0 END), 4) as pnl
        FROM engine_trades 
        WHERE mode='backtest'
        GROUP BY exchange
        ORDER BY exchange
    """)
    backtest_stats = cursor.fetchall()
    
    # 模拟统计
    cursor.execute("""
        SELECT 
            exchange,
            COUNT(*) as total,
            SUM(CASE WHEN status='closed' THEN 1 ELSE 0 END) as closed,
            ROUND(SUM(CASE WHEN status='closed' AND pnl IS NOT NULL THEN pnl ELSE 0 END), 4) as pnl
        FROM engine_trades 
        WHERE mode='paper'
        GROUP BY exchange
        ORDER BY exchange
    """)
    paper_stats = cursor.fetchall()
    
    # 数据收集状态
    cursor.execute("""
        SELECT 
            exchange,
            COUNT(*) as total_ticks,
            datetime(MAX(timestamp), 'unixepoch') as latest
        FROM market_data 
        GROUP BY exchange
    """)
    data_stats = cursor.fetchall()
    
    conn.close()
    return backtest_stats, paper_stats, data_stats

def check_engine_status():
    """检查引擎进程状态"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'adaptive_system'],
            capture_output=True, text=True
        )
        return result.stdout.strip() != ''
    except:
        return False

def main():
    print(f"\n{'='*60}")
    print(f"📊 QNT系统监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # 检查引擎状态
    running = check_engine_status()
    print(f"🔄 引擎状态: {'✅ 运行中' if running else '❌ 未运行'}")
    
    # 获取统计
    backtest_stats, paper_stats, data_stats = get_db_stats()
    
    # 回测统计
    print(f"\n📈 回测引擎统计:")
    total_bt_pnl = 0
    for exchange, total, closed, pnl in backtest_stats:
        win_rate = (closed / total * 100) if total > 0 else 0
        status = "✅ 盈利" if pnl > 0 else "❌ 亏损"
        print(f"   {exchange:8s}: {total:4d}笔 ({closed:3d}平仓), 胜率{win_rate:5.1f}%, 盈亏${pnl:+.2f}U {status}")
        total_bt_pnl += pnl if pnl else 0
    
    print(f"   {'总计':8s}: 总盈亏${total_bt_pnl:+.2f}U")
    
    # 模拟统计
    print(f"\n📝 模拟引擎统计:")
    total_paper_pnl = 0
    for exchange, total, closed, pnl in paper_stats:
        win_rate = (closed / total * 100) if total > 0 else 0
        status = "✅ 盈利" if pnl > 0 else "⏳ 持仓中"
        print(f"   {exchange:8s}: {total:4d}笔 ({closed:3d}平仓), 胜率{win_rate:5.1f}%, 盈亏${pnl:+.2f}U {status}")
        total_paper_pnl += pnl if pnl else 0
    
    # 数据收集状态
    print(f"\n📡 数据收集状态:")
    now = datetime.now()
    for exchange, total, latest in data_stats:
        latest_dt = datetime.strptime(latest, '%Y-%m-%d %H:%M:%S')
        diff = (now - latest_dt).total_seconds() / 60
        status = "✅" if diff < 10 else "⚠️ 过时"
        print(f"   {exchange:8s}: {total:>6d}条数据, 最新{latest} ({diff:.1f}分钟前) {status}")
    
    # 判断是否盈利
    print(f"\n🎯 实盘开关判断:")
    if total_bt_pnl > 0 and total_paper_pnl > 0:
        print(f"   ✅ 回测+模拟均盈利，可以开启实盘！")
        return 0  # 盈利，可以开启实盘
    elif total_bt_pnl > 0:
        print(f"   ⚠️ 仅回测盈利，模拟仍在亏损，继续观察")
    elif total_paper_pnl > 0:
        print(f"   ⚠️ 仅模拟盈利，回测仍在亏损，继续观察")
    else:
        print(f"   🔒 回测+模拟均亏损，实盘保持关闭")
    
    return 1  # 未盈利，继续等待

if __name__ == '__main__':
    sys.exit(main())
