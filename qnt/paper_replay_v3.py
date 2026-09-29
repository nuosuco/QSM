#!/usr/bin/env python3.11
"""A策略第三轮回放验证（模式一找规律 → 升级）
规律：单边趋势市中逆势赌回归=接刀（9.9-9.13 回放亏33U，胜率17%）
升级（2026-09-13）：
  1. 趋势市（1h 中点变化 >0.15%）：只开顺势单，禁止逆势
  2. 震荡市（1h ±0.15% 内）：逆势+顺势都做（保留赚的钱源）
  3. 逆势单硬止损收紧 0.08%（保证金口径封顶 -0.31% 以内），顺势单维持 0.15%
与实盘/模拟盘同步常量口径。纯离线回放，不碰实盘。
"""
import sqlite3, time, sys
from collections import defaultdict

DB='/root/SOM/data/trading_system/adaptive.db'
BI_SIDE_COST=0.0016; MIN_NET=0.0010; ENTRY=BI_SIDE_COST+MIN_NET  # 0.26%
STOP_TREND=0.0015   # 顺势单硬止损（标的价格口径）
STOP_COUNTER=0.0008 # 逆势单硬止损收紧
TIMEOUT=5400; BLACKLIST={'WIF/USDT'}; COOL=1800; TREND=0.0015

def main():
    start=float(sys.argv[1]) if len(sys.argv)>1 else time.time()-86400*30
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
    open_pos={}; closed=[]; tp=[]; sl=[]; to_=[]; cd=defaultdict(float); skip_c=0
    for t in ticks:
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
            stop=(STOP_TREND if not pos['counter'] else STOP_COUNTER)
            hs=pnl<=-stop; tpok=net>=MIN_NET and shrink
            if hs or tpok or (age>=TIMEOUT and net>0):
                if hs: r='止损'; sl.append(net)
                elif tpok: r='止盈'; tp.append(net)
                else: r='超时'; to_.append(net)
                closed.append((ts,ex,sym,pos['side'],r,net*100,pos['counter']))
                cd[key]=ts+COOL; del open_pos[key]
            continue
        if abs(sp)<ENTRY: continue
        if ts<cd[key]: continue
        side='sell' if sp>0 else 'buy'
        pts=[p for p in series[(ex,sym)] if ts-3600<=p[0]<=ts]
        chg=(pts[-1][1]-pts[0][1])/pts[0][1] if len(pts)>=2 and pts[0][1]>0 else 0
        in_trend = chg>TREND or chg<-TREND
        with_trend = (side=='buy' and chg<TREND*0.5) or (side=='sell' and chg>-TREND*0.5)
        # 趋势市只顺势；震荡市都做
        if in_trend and not with_trend:
            skip_c+=1; continue
        counter = not with_trend  # 震荡市里的逆势单
        entry=t['perp_ask'] if side=='buy' else t['perp_bid']
        if entry<=0: continue
        amt=100.0/entry
        open_pos[key]={'side':side,'entry':entry,'esp':sp,'et':ts,'counter':counter}
    lasttick={(t['exchange'],t['symbol']):t for t in ticks[-50:]}
    for k,pos in open_pos.items():
        ex,sym=k.split('|'); t=lasttick.get((ex,sym))
        if not t: continue
        pm=(t['perp_bid']+t['perp_ask'])/2
        pnl=((pm-pos['entry'])/pos['entry']) if pos['side']=='buy' else ((pos['entry']-pm)/pos['entry'])
        net=pnl-BI_SIDE_COST
        closed.append((t['timestamp'],ex,sym,pos['side'],'强平',net*100,pos['counter']))
    n=len(closed); win=sum(1 for c in closed if c[5]>0)
    tot=sum(c[5] for c in closed)/100*100
    avg_tp=sum(tp)/len(tp)*100 if tp else 0; worst=min(sl)*100 if sl else 0
    n_counter=sum(1 for c in closed if c[6]); n_trend=n-n_counter
    print(f"\n=== A策略第三轮回放（趋势市只顺势+震荡市全做+逆势止损0.08%）===")
    print(f"平仓:{n} (顺势{n_trend}/逆势{n_counter}) 胜率:{win/n*100 if n else 0:.1f}%")
    print(f"止盈均:{avg_tp:+.3f}%(需≥0.10) 止损最差:{worst:+.3f}%(需>-0.31) 总净利点:{tot:+.2f}(需>0)")
    print(f"止盈{len(tp)} 止损{len(sl)} 超时{len(to_)} 逆势拦截{skip_c}")
    ok=n>=20 and avg_tp>=0.10 and worst>-0.31 and tot>0
    print("✅达标" if ok else "❌未达标")
    print("\n-- 逐笔 --")
    for c in closed:
        print(f"  {time.strftime('%m-%d %H:%M',time.localtime(c[0]))} {c[1]:6} {c[2]:10} {c[3]:4} [{c[4]}] {'逆' if c[6] else '顺'} {c[5]:+.3f}%")

if __name__=='__main__':
    main()
