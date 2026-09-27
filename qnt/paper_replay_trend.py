#!/usr/bin/env python3.11
"""历史回放模拟盘 + 趋势过滤器（模式一规律升级验证）
规律（回放发现）：贴水回归多单在单边下跌中失效（1h 跌幅>0.15% 时顺势开多=接刀）。
升级：1h spot 中点变化 > +0.15% 不开空单；< -0.15% 不开多单（只赌震荡回归）。
与实盘/模拟盘同步的常量口径。
"""
import sqlite3, time, sys
from collections import defaultdict

DB='/root/SOM/data/trading_system/adaptive.db'
BI_SIDE_COST=0.0016; MIN_NET=0.0001  # 2026-09-27 与实盘 RiskManager.MIN_NET_PROFIT_PCT 一致
# A升级同步：动态门槛=基础+永续自身点差（回放按 tick 实时算，和实盘 _scan_and_execute 同口径）
ENTRY_BASE=BI_SIDE_COST+MIN_NET
STOP=0.0015; TIMEOUT=5400; BLACKLIST={'WIF/USDT'}; COOL=1800
TREND=0.0015

def _mem_guard():
    """内存闸门：可用<1.5G时跳过回放（不挤爆常驻服务），随时可跑但内存紧张自动让路"""
    try:
        with open('/proc/meminfo') as f:
            for line in f:
                if line.startswith('MemAvailable:'):
                    avail_mb = int(line.split()[1]) / 1024
                    if avail_mb < 1536:
                        print(f"⚠️ 内存闸门: 可用{avail_mb:.0f}MB<1536MB，跳过本轮回放（下轮再跑）")
                        return False
        return True
    except Exception as e:
        print(f"内存检查失败(放行): {e}")
        return True

def main():
    start=float(sys.argv[1]) if len(sys.argv)>1 else time.time()-86400  # 默认24h（不再默认720h）
    if not _mem_guard():
        return
    conn=sqlite3.connect(DB); conn.row_factory=sqlite3.Row
    cur=conn.cursor()
    cur.execute("""SELECT timestamp,exchange,symbol,spot_bid,spot_ask,perp_bid,perp_ask,spread_pct
                   FROM market_data WHERE timestamp>=? AND ABS(spread_pct)<1.0 AND spread_pct IS NOT NULL
                   ORDER BY timestamp ASC""",(start,))
    ticks=cur.fetchall()
    print(f"载入 {len(ticks)} tick | 起点 {time.strftime('%m-%d %H:%M',time.localtime(start))}")
    if not ticks: print("无数据"); return

    series=defaultdict(list)
    for t in ticks:
        series[(t['exchange'],t['symbol'])].append((t['timestamp'],(t['spot_bid']+t['spot_ask'])/2,(t['perp_bid']+t['perp_ask'])/2,t['spread_pct']))

    open_pos={}; closed=[]; tp=[]; sl=[]; to_=[]; cd=defaultdict(float)
    n_skip_trend=0
    for i,t in enumerate(ticks):
        ts=t['timestamp']; ex=t['exchange']; sym=t['symbol']
        sm=(t['spot_bid']+t['spot_ask'])/2; pm=(t['perp_bid']+t['perp_ask'])/2
        sp=t['spread_pct']; key=f"{ex}|{sym}"
        if sym in BLACKLIST: continue
        if key in open_pos:
            pos=open_pos[key]
            pnl=((pm-pos['entry'])/pos['entry']) if pos['side']=='buy' else ((pos['entry']-pm)/pos['entry'])
            net=pnl-BI_SIDE_COST; age=ts-pos['et']
            cs=((pm-sm)/sm) if sm>0 else 0
            shrink=(pos['side']=='sell' and cs<pos['esp']) or (pos['side']=='buy' and cs>pos['esp'])
            hs=pnl<=-STOP; tpok=net>=MIN_NET and shrink
            if hs or tpok or (age>=TIMEOUT and net>0):
                if hs: r='止损'; sl.append(net)
                elif tpok: r='止盈'; tp.append(net)
                else: r='超时'; to_.append(net)
                closed.append((ts,ex,sym,pos['side'],r,net*100)); cd[key]=ts+COOL
                del open_pos[key]
            continue
        # A动态门槛（与实盘同口径，分数口径，sp是分数）：门槛=基础0.17%+该tick永续自身点差
        ps_spread = ((t['perp_ask']-t['perp_bid'])/pm) if pm>0 else 0
        if abs(sp) < ENTRY_BASE + max(ps_spread,0): continue
        if ts<cd[key]: continue
        side='sell' if sp>0 else 'buy'
        # 趋势过滤器（用本 tick 之前 1h 的 spot 变化）
        pts=[p for p in series[(ex,sym)] if ts-3600<=p[0]<=ts]
        chg=(pts[-1][1]-pts[0][1])/pts[0][1] if len(pts)>=2 and pts[0][1]>0 else 0
        if (side=='buy' and chg<-TREND) or (side=='sell' and chg>TREND):
            n_skip_trend+=1; continue
        entry=t['perp_ask'] if side=='buy' else t['perp_bid']
        if entry<=0: continue
        amt=100.0/entry
        open_pos[key]={'side':side,'entry':entry,'esp':sp,'et':ts}

    lasttick={(t['exchange'],t['symbol']):t for t in ticks[-50:]}
    for k,pos in open_pos.items():
        ex,sym=k.split('|')
        t=lasttick.get((ex,sym))
        if not t: continue
        pm=(t['perp_bid']+t['perp_ask'])/2
        pnl=((pm-pos['entry'])/pos['entry']) if pos['side']=='buy' else ((pos['entry']-pm)/pos['entry'])
        net=pnl-BI_SIDE_COST
        closed.append((t['timestamp'],ex,sym,pos['side'],'强平',net*100))

    n=len(closed); win=sum(1 for c in closed if c[5]>0)
    tot=sum(c[5] for c in closed)/100*100  # 每笔 100U 仓位 → 换算成百分比点合计≈净利
    avg_tp=sum(tp)/len(tp)*100 if tp else 0; worst=min(sl)*100 if sl else 0
    print(f"\n=== 趋势过滤器回放（{TREND*100}% 1h）===")
    print(f"平仓:{n} 胜率:{win/n*100 if n else 0:.1f}% 止盈均:{avg_tp:+.3f}%(需≥0.10) 止损最差:{worst:+.3f}%(需>-0.31) 总净利点:{tot:+.2f} 趋势拦截:{n_skip_trend}")
    print(f"止盈{len(tp)} 止损{len(sl)} 超时{len(to_)} 强平{sum(1 for c in closed if c[4]=='强平')}")
    ok=n>=20 and avg_tp>=0.10 and worst>-0.31 and tot>0
    print("✅达标（≥20笔 & 止盈≥0.10% & 止损>-0.31% & 总净利>0）" if ok else "❌未达标")
    print("\n-- 逐笔 --")
    for c in closed:
        print(f"  {time.strftime('%m-%d %H:%M',time.localtime(c[0]))} {c[1]:6} {c[2]:10} {c[3]:4} [{c[4]}] {c[5]:+.3f}%")

if __name__=='__main__':
    main()
