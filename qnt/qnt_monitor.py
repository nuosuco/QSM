#!/usr/bin/env python3
"""QNT监控系统 - 盈利时自动开启实盘"""
import sqlite3, subprocess, sys, os
from datetime import datetime

DB = '/root/SOM/data/trading_system/adaptive.db'

def get_stats():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # 回测统计
    c.execute("SELECT exchange, COUNT(*), SUM(CASE WHEN status='closed' THEN 1 ELSE 0 END), ROUND(SUM(CASE WHEN status='closed' AND pnl IS NOT NULL THEN pnl ELSE 0 END), 2) FROM engine_trades WHERE mode='backtest' GROUP BY exchange ORDER BY exchange")
    bt = c.fetchall()
    # 模拟统计
    c.execute("SELECT exchange, COUNT(*), SUM(CASE WHEN status='closed' THEN 1 ELSE 0 END), ROUND(SUM(CASE WHEN status='closed' AND pnl IS NOT NULL THEN pnl ELSE 0 END), 2) FROM engine_trades WHERE mode='paper' GROUP BY exchange ORDER BY exchange")
    pp = c.fetchall()
    conn.close()
    return bt, pp

def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    bt, pp = get_stats()
    
    print(f"\n[{now}] QNT监控报告")
    print("="*50)
    
    # 回测统计
    print("\n📈 回测引擎:")
    total_bt = 0
    for ex, t, c, pnl in bt:
        wr = c/t*100 if t>0 else 0
        s = "✅盈利" if pnl>0 else "❌亏损"
        print(f"   {ex:8s}: {t:4d}笔({c:3d}平仓) 胜率{wr:5.1f}% ${pnl:+.2f}U {s}")
        total_bt += pnl if pnl else 0
    
    # 模拟统计
    print("\n📝 模拟引擎:")
    total_pp = 0
    for ex, t, c, pnl in pp:
        wr = c/t*100 if t>0 else 0
        s = "✅盈利" if pnl>0 else "⏳持仓"
        print(f"   {ex:8s}: {t:4d}笔({c:3d}平仓) 胜率{wr:5.1f}% ${pnl:+.2f}U {s}")
        total_pp += pnl if pnl else 0
    
    # 判断
    print(f"\n{'='*50}")
    print(f"🎯 汇总: 回测${total_bt:+.2f}U  模拟${total_pp:+.2f}U")
    
    if total_bt > 0 and total_pp > 0:
        print("✅ 回测+模拟均盈利，可以开启实盘！")
        # 发送通知
        try:
            from qqbot_channel_api import send_message
            send_message("QNT系统盈利！回测${:.2f}U + 模拟${:.2f}U，建议开启实盘验证".format(total_bt, total_pp))
        except:
            pass
        return 0
    else:
        print("🔒 实盘保持关闭，继续积累盈利数据")
        return 1

if __name__ == '__main__':
    sys.exit(main())
