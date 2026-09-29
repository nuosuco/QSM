#!/usr/bin/env python3.11
"""历史数据回放模拟盘验证（方案A）

中华 2026-09-13 定稿铁律：
- 模拟盘验证程序有没有严格照策略执行，策略升级先过模式一回放
- 模拟盘门槛与实盘同步 = 0.26%（0.16%成本 + 0.10%净利）
- 模拟盘不影响实盘（纯离线读 market_data 历史 tick）

本脚本：
1. 从 market_data 表读 [2026-09-13 12:00 起] 的所有 tick
2. 用与 dual_engine.PaperEngine 完全一致的逻辑回放（同门槛/同止损/同超时/同分档平仓）
3. 跑完输出验证报告：平仓笔数、止盈净利均值、止损亏损上限、超时占比
4. 达标判断：
   - 平仓笔数 >= 20
   - 止盈单净利均值 >= 0.10%
   - 止损单净利 > -0.31%（保证金口径）
   - 总净利 > 0
"""
import sqlite3
import time
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DB = '/root/SOM/data/trading_system/adaptive.db'

# ===== 与实盘/模拟盘完全同步的常量（2026-09-13 口径）=====
BI_SIDE_COST = 0.0016        # 0.16% 双边成本（保证金口径）
MIN_NET_PROFIT_PCT = 0.0010  # 0.10% 净利门槛
ENTRY_THRESHOLD = BI_SIDE_COST + MIN_NET_PROFIT_PCT  # 0.26%
SINGLE_SIDE_STOP_LOSS_PCT = 0.0015   # 标的价格口径硬止损 0.15%
SPREAD_POSITION_TIMEOUT = 5400       # 90分钟
BLACKLIST = {'WIF/USDT'}

@dataclass
class PPosition:
    symbol: str
    exchange: str
    side: str          # 'buy' | 'sell'（side 是永续侧：buy=开永续多，sell=开永续空）
    entry_price: float  # 永续侧开仓价（perp_ask or perp_bid）
    entry_spread_pct: float  # 开仓时 spot 口径价差（小数）
    entry_time: float
    amount: float
    entry_notional: float
    spot_exchange: str

def open_side(spread_pct: float) -> str:
    """spot 口径价差 > 0（升水）→ 开永续空（sell）赌回归；< 0（贴水）→ 开永续多（buy）"""
    return 'sell' if spread_pct > 0 else 'buy'

def main():
    start = float(sys.argv[1]) if len(sys.argv) > 1 else time.time() - 7200  # 默认回放最近3小时
    print(f"📼 历史回放模拟盘验证 | 起点: {time.strftime('%Y-%m-%d %H:%M:%S %z', time.localtime(start))}")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT id, timestamp, exchange, symbol, spot_bid, spot_ask, perp_bid, perp_ask, spread_pct
        FROM market_data
        WHERE timestamp >= ? AND ABS(spread_pct) < 1.0 AND spread_pct IS NOT NULL
        ORDER BY timestamp ASC
    """, (start,))
    ticks = cur.fetchall()
    print(f"载入 {len(ticks)} 条 tick")
    if not ticks:
        print("无数据，退出")
        return

    open_pos: Dict[str, PPosition] = {}
    closed: List[dict] = []
    tp_pnl, sl_pnl, timeout_pnl = [], [], []
    cooldown_until: Dict[str, float] = defaultdict(lambda: 0)

    for t in ticks:
        ts = t['timestamp']
        ex = t['exchange']           # 平台（数据归属平台，spot 在该平台，perp 在对端）
        sym = t['symbol']
        spot_bid, spot_ask = t['spot_bid'], t['spot_ask']
        perp_bid, perp_ask = t['perp_bid'], t['perp_ask']
        spread = t['spread_pct']
        if sym in BLACKLIST:
            continue
        spot_mid = (spot_bid + spot_ask) / 2
        perp_mid = (perp_bid + perp_ask) / 2
        pos_key = f"{ex}|{sym}"
        if pos_key in open_pos:
            pos = open_pos[pos_key]
            pnl_pct_price = (perp_mid - pos.entry_price)/pos.entry_price if pos.side=='buy' else (pos.entry_price - perp_mid)/pos.entry_price
            net = pnl_pct_price - BI_SIDE_COST
            age = ts - pos.entry_time
            cur_spread = ((perp_mid - spot_mid)/spot_mid) if spot_mid > 0 else 0
            # 价差方向：sell(开永续空赌升水回归)→回归=价差缩小；buy→价差增大
            shrinking = (pos.side=='sell' and cur_spread < pos.entry_spread_pct) or (pos.side=='buy' and cur_spread > pos.entry_spread_pct)
            hard_stop = pnl_pct_price <= -SINGLE_SIDE_STOP_LOSS_PCT
            take_profit = (net >= MIN_NET_PROFIT_PCT) and shrinking
            timed_out = age >= SPREAD_POSITION_TIMEOUT
            if hard_stop or take_profit or (timed_out and net > 0):
                if hard_stop:
                    reason='硬止损'; sl_pnl.append(net)
                elif take_profit:
                    reason='止盈'; tp_pnl.append(net)
                else:
                    reason='超时'; timeout_pnl.append(net)
                gross = pnl_pct_price * pos.entry_notional
                fee = pos.entry_notional * 0.0008 + pos.entry_notional * 0.0006  # 简估：开仓+taker
                net_abs = gross - fee
                closed.append({'ts': ts, 'ex': ex, 'sym': sym, 'side': pos.side, 'reason': reason, 'net_pct': net*100, 'net_abs': net_abs})
                cooldown_until[pos_key] = ts + 1800  # 30min 冷却
                del open_pos[pos_key]
            continue
        # 无持仓 → 开仓判断
        if abs(spread) < ENTRY_THRESHOLD:
            continue
        if ts < cooldown_until[pos_key]:
            continue
        side = open_side(spread)
        entry = perp_ask if side=='buy' else perp_bid
        if entry <= 0: continue
        amt = 100.0 / entry
        open_pos[pos_key] = PPosition(sym, ex, side, entry, spread, ts, amt, entry*amt, ex)
        print(f"📈 {time.strftime('%m-%d %H:%M:%S', time.localtime(ts))} {ex} {sym} {side.upper()} @{entry:.4f} 价差={spread*100:+.3f}%")

    # 收尾：未平仓位按最后 tick 强平（模拟收盘兜底）
    last_ts = ticks[-1]['timestamp']
    for k, pos in open_pos.items():
        t = [x for x in ticks if f"{x['exchange']}|{x['symbol']}"==k][-1]
        pm = (t['perp_bid']+t['perp_ask'])/2
        pnl_price = (pm - pos.entry_price)/pos.entry_price if pos.side=='buy' else (pos.entry_price - pm)/pos.entry_price
        net = pnl_price - BI_SIDE_COST
        closed.append({'ts': last_ts, 'ex': pos.exchange, 'sym': pos.symbol, 'side': pos.side, 'reason': '回放结束强平', 'net_pct': net*100, 'net_abs': net*pos.entry_notional})
        print(f"🏁 回放结束强平 {pos.exchange} {pos.symbol} {pos.side} 净利={net*100:+.3f}%")

    n = len(closed)
    win = sum(1 for c in closed if c['net_abs'] > 0)
    total = sum(c['net_abs'] for c in closed)
    avg_tp = (sum(tp_pnl)/len(tp_pnl)*100) if tp_pnl else 0
    worst_sl = min(sl_pnl)*100 if sl_pnl else 0
    print("\n" + "="*52)
    print(f"📊 回放验证报告（回放 tick: {len(ticks)} 条，区间 {time.strftime('%H:%M:%S', time.localtime(start))}~{time.strftime('%H:%M:%S', time.localtime(last_ts))}）")
    print(f"  平仓笔数: {n}   达标要求 >=20")
    print(f"  止盈单: {len(tp_pnl)} 笔，净利均值 {avg_tp:+.3f}%（达标 >=0.10%）")
    print(f"  止损单: {len(sl_pnl)} 笔，最差 {worst_sl:+.3f}%（达标 >-0.31%）")
    print(f"  超时单: {len(timeout_pnl)} 笔")
    print(f"  胜率: {win/n*100 if n else 0:.1f}%  总净毛利: {total:+.2f}U（>0 达标）")
    ok = n>=20 and avg_tp>=0.10 and worst_sl>-0.31 and total>0
    print(f"  {'✅ 达标，可进阶段3实盘验证' if ok else '❌ 未达标（差项见上）'}")
    print("="*52)
    for c in closed:
        print(f"  {'🏁':2} {time.strftime('%H:%M:%S', time.localtime(c['ts']))} {c['ex']:7} {c['sym']:10} {c['side']:4} [{c['reason']}] {c['net_pct']:+.3f}%")

if __name__ == '__main__':
    main()
