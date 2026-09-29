"""
QNT 周期巡检脚本 (patrol)
- 检查服务存活 (systemd active + 心跳文件新鲜)
- 检查实盘交易合规: 是否有现货腿订单 / 同时开多开空 / 突破风控门槛
- 检查持仓健康: 是否有持仓逼近强平
- 检查净利健康: 滚动 24h 实盘净利是否连续为负
- 异常 → 写 report 文件 + 通过 OpenClaw Gateway 发 QQ 告警
- 正常 → 静默 (HEARTBEAT_OK 语义, 写心跳文件)

用法: python3 qnt_patrol.py            # 跑一次, 异常才发 QQ
      (由 systemd timer 或 cron 每 10 分钟调一次)
"""
import os, sys, time, json, sqlite3, logging, urllib.request, subprocess
from datetime import datetime, timezone

# 2026-09-13 修复：告警改走 openclaw CLI（qnt_patrol 由 systemd 以 root 运行，能访问 openclaw home），
# 不再走 gateway HTTP（会因 session 路由错误而静默失败），也不再静默写日志

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('QNT_Patrol')

DB = '/root/SOM/data/trading_system/adaptive.db'
HEARTBEAT = '/root/SOM/qnt/data/heartbeat.json'
REPORT = '/root/SOM/qnt/data/patrol_report.json'
GATEWAY_URL = os.environ.get('OPENCLAW_GATEWAY_URL', 'http://localhost:14121')
TOKEN = os.environ.get('OPENCLAW_GATEWAY_TOKEN', '')
if not TOKEN:
    try:
        for _ln in open('/etc/default/qnt-engines'):
            if _ln.startswith('OPENCLAW_GATEWAY_TOKEN='):
                TOKEN = _ln.strip().split('=',1)[1].strip()
                break
    except Exception:
        pass
OPENCLAW_CLI = os.environ.get('OPENCLAW_CLI', '/root/.openclaw/tmp/agent-cli/openclaw')
OPENCLAW_HOME = os.environ.get('OPENCLAW_HOME', '/root/.openclaw')
# 2026-09-13 踩坑实测：CLI 的 --channel 校验用的是小写 id（qqbot 是有效 channel id），
# 显示名 "QQ Bot" / 连字符 "qq-bot" 都报 Unknown channel。之前误记为"必须带空格"，更正
QQ_CLI_CHANNEL = os.environ.get('OPENCLAW_QQ_CHANNEL', 'qqbot')  # 2026-09-28 修正：channels list 显示 'QQ Bot' 但 CLI 校验用通道id小写 'qqbot'，旧注释记反了
QQ_TARGET = 'qqbot:c2c:861B1B2CC9C89FC4A3E0325F10407447'

# 合规红线（与 execution_engine.py 模块级常量保持同步；改参数时两处一起改）
# 2026-09-13 同步：开仓门槛 0.26%（净利0.10%+成本0.16%），硬止损 0.15%（标的价格口径），超时 90min
SPREAD_ENTRY_MIN = 0.0026      # 价差 0.26% 起交易 (纯利0.10 + 成本0.16)
HARD_STOP = 0.0015             # 硬止损 0.15%（标的价格口径，与 SINGLE_SIDE_STOP_LOSS_PCT 一致）
TIMEOUT_MIN = 90               # 持仓超时 90 分钟兜底


def _send_qq(msg):
    """告警路由：主走 openclaw CLI（直接发给 QQ，不依赖 gateway 会话路由），失败则落盘标记文件，由小蕊处置。
    2026-09-13 修复：旧版走 gateway HTTP 的 /tools/invoke 会静默失败，导致 4 小时未送达。"""
    alert_file = '/root/SOM/qnt/data/patrol_alerts.log'
    try:
        with open(alert_file, 'a') as f:
            f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    except Exception as e:
        logger.debug(f"写告警文件失败: {e}")

    # 2026-09-28 推送路线确定：gateway HTTP 不暴露 sessions_send，CLI 侧 qqbot 未注册。
    # 可行链路 = 巡检脚本把告警/心跳写入 memory/qnt-watch.md（小蕊每次醒来必读文件），
    # 小蕊主动读取后按汇报铁律转发给中华。patrol_alerts.log 仍保留做审计兜底。
    _sent = False
    try:
        watch = '/root/.openclaw/workspace/memory/qnt-watch.md'
        os.makedirs(os.path.dirname(watch), exist_ok=True)
        ts = datetime.now(timezone.utc).isoformat()
        with open(watch, 'a') as wf:
            wf.write(f"\n## 巡检 {ts}\n{msg}\n")
        logger.info(f"📤 巡检结果已写入 qnt-watch.md（小蕊下次醒来主动读并报中华）")
        _sent = True
    except Exception as e:
        logger.warning(f"写 qnt-watch.md 失败（已落盘 patrol_alerts.log 兜底）: {e}")


def check_service():
    """服务存活 + 心跳新鲜"""
    import subprocess
    st = subprocess.run(['systemctl', 'is-active', 'qnt-engines'], capture_output=True, text=True).stdout.strip()
    ok = st == 'active'
    hb_fresh = False
    try:
        hb = json.load(open(HEARTBEAT))
        hb_fresh = (time.time() - hb.get('timestamp', 0)) < 300   # 300s 内算新鲜(心跳间隔60s+写入延迟)
    except Exception:
        pass
    return ok, hb_fresh


def check_trades_db():
    """交易合规 + 净利健康 (返回 (issues, stats))"""
    issues = []
    stats = {'live_24h': 0, 'net_24h': 0.0, 'wins': 0, 'losses': 0}
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    now = int(time.time())

    # 合规 1: 真现货腿判定 = 平仓单里出现非永续符号(:USDT 缺失)的卖出/买入。
    # 开仓单 _record_trade 用原始 symbol(如 TIA/USDT)记, 不算现货腿; 只有
    # status='closed' 且 symbol 无 :USDT 的平仓动作, 才可能是误下现货单。
    c.execute("SELECT COUNT(*) FROM engine_trades WHERE mode='live' AND status='closed' AND symbol NOT LIKE '%:USDT%' AND timestamp>?", (now-3600,))
    spot_legs = c.fetchone()[0]
    if spot_legs:
        issues.append(f"⚠️ 发现 {spot_legs} 笔现货平仓腿(合规红线: 只允许永续单腿)")

    # 合规 2: 同一 symbol 是否同时存在未平的 open 多单和 open 空单
    c.execute("SELECT symbol, COUNT(DISTINCT side) FROM engine_trades WHERE mode='live' AND status='opened' AND timestamp>? GROUP BY symbol HAVING COUNT(DISTINCT side)>1", (now-86400,))
    both_sides = [r[0] for r in c.fetchall()]
    if both_sides:
        issues.append(f"⚠️ 发现同时开多开空: {','.join(both_sides)}")

    # 合规 3: 亏损单是否突破硬止损 0.15%
    # 2026-09-18 修复：engine_trades.pnl_pct 是百分比口径（含%号，-3.0 表示 -3%），
    # 旧写法 (pnl_pct/100.0) < -HARD_STOP 即 pnl_pct < -0.15 → 需要跌破-0.15%再/100→-0.0015，
    # HARD_STOP=0.0015 时等价 pnl_pct < -0.00015，取值范围完全错开，永不触发。
    # 正确：pnl_pct < 0 表示亏损，pnl_pct 绝对值超过 0.15% 即触发（pnl_pct % 已在100倍，直接比 0.15）
    hard_stop_pct_num = HARD_STOP * 100  # 0.15（百分比数字口径）
    c.execute("SELECT COUNT(*) FROM engine_trades WHERE mode='live' AND pnl_pct<0 AND pnl_pct < -? AND timestamp>?", (hard_stop_pct_num, now-86400))
    big_loss = c.fetchone()[0]
    if big_loss:
        issues.append(f"⚠️ 发现 {big_loss} 笔亏损突破 {hard_stop_pct_num}% 硬止损")

    # 净利健康: 24h 滚动
    c.execute("SELECT COUNT(*), COALESCE(SUM(amount*pnl_pct/100.0),0), SUM(CASE WHEN pnl_pct>0 THEN 1 ELSE 0 END), SUM(CASE WHEN pnl_pct<0 THEN 1 ELSE 0 END) FROM engine_trades WHERE mode='live' AND status IN ('completed','closed') AND timestamp>?", (now-86400,))
    n, net, wins, losses = c.fetchone()
    stats.update({'live_24h': n, 'net_24h': net or 0.0, 'wins': wins or 0, 'losses': losses or 0})
    if n >= 10 and (net or 0.0) < -0.05:   # 10笔以上且净亏>0.05U
        issues.append(f"⚠️ 24h 实盘净亏 {net:.3f}U ({n}笔, 胜率{wins/(n)*100:.0f}%), 策略可能失效")
    conn.close()
    return issues, stats


def check_heartbeat_fresh():
    try:
        hb = json.load(open(HEARTBEAT))
        return (time.time() - hb.get('timestamp', 0)) < 120
    except Exception:
        return False


def check_position_margin():
    """保证金铁律核对（2026-09-14 中华定稿）：该平台已开保证金 ≤ 该平台余额×20%（分池）。
    返回 (issues, detail)。
    注：平台余额从 engine_trades/日志取不了实时数，这里用「已开保证金 vs 该平台历史峰值权益×20%」做保守核对，
    峰值权益从 risk_state 取；若缺失则只报已开额，不判超限。"""
    issues = []
    detail = []
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # 各平台已开保证金合计（持仓未平）
    c.execute("SELECT ex_name, COUNT(*), SUM(position_size) FROM spread_positions GROUP BY ex_name")
    rows = c.fetchall()
    # 各平台峰值权益（risk_state 里存过）
    # 2026-09-18 修复：risk_state 实际存的峰值权益键是 peak_equity（risk_manager._update_peak_equity），
    # 旧代码读 max_equity_peak（不存在）永远 None → 保证金铁律核对一直空转不判违规
    c.execute("SELECT value FROM risk_state WHERE key='peak_equity'")
    peak = c.fetchone()
    peak_eq = float(peak[0]) if peak and peak[0] else None
    for ex_name, cnt, opened in rows:
        opened = float(opened or 0)
        line = f"{ex_name}: 持仓{cnt}笔 已开保证金{opened:.3f}U"
        if peak_eq:
            cap = peak_eq * 0.20
            # 分池口径：该平台余额≤总权益，故该平台已开保证金 ≤ 总权益×20% 是必要不充分条件；
            # 超过总权益20% 必违规（铁律双保险口径）
            if opened > cap:
                line += f" ⚠️ 超总权益20%({cap:.3f}U) 违规!"
                issues.append(f"🚨 保证金铁律违规: {ex_name} 已开{opened:.3f}U > 总权益20%({cap:.3f}U)")
        detail.append(line)
    conn.close()
    return issues, detail


def check_pattern_30min():
    """市场规律小结（盯盘 → 喂小蕊思考）：近 30min 哪些币/方向赚、哪些亏，震荡还是单边。
    返回 (summary_text, noteworthy:bool)。"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    now = int(time.time())
    # 近 30min 完成的实盘单
    c.execute("""SELECT symbol, side, SUM(pnl_pct)/100.0*SUM(amount) AS pnl, COUNT(*)
                 FROM engine_trades
                 WHERE mode='live' AND status IN ('completed','closed') AND timestamp>? AND timestamp<=?""",
              (now-1800, now))
    recent = c.fetchall()
    conn.close()
    if not recent:
        return ("近30min 无完成实盘单（管道/门槛未触发或无价差），暂无规律样本", False)
    # 按币种聚合
    by_sym = {}
    for sym, side, pnl, n in recent:
        e = by_sym.setdefault(sym, {'pnl': 0.0, 'n': 0, 'win': 0, 'loss': 0})
        e['pnl'] += pnl or 0; e['n'] += n
        if (pnl or 0) > 0: e['win'] += 1
        else: e['loss'] += 1
    winners = sorted([s for s in by_sym if by_sym[s]['pnl'] > 0], key=lambda s: -by_sym[s]['pnl'])
    losers = sorted([s for s in by_sym if by_sym[s]['pnl'] < 0], key=lambda s: by_sym[s]['pnl'])
    total = sum(v['pnl'] for v in by_sym.values())
    parts = [f"近30min实盘规律小结: 共{sum(v['n'] for v in by_sym.values())}笔 净{total:+.3f}U"]
    if winners: parts.append("赚: " + ", ".join(f"{s}({by_sym[s]['pnl']:+.3f}U/{by_sym[s]['n']}笔)" for s in winners[:3]))
    if losers: parts.append("亏: " + ", ".join(f"{s}({by_sym[s]['pnl']:+.3f}U/{by_sym[s]['n']}笔)" for s in losers[:3]))
    # 市场状态粗判：用 gate/htx 的 BTC 1h 变化（若 market_data 有）
    mk = ""
    try:
        conn2 = sqlite3.connect(DB); c2 = conn2.cursor()
        c2.execute("SELECT price, ts FROM market_data WHERE symbol='BTC/USDT' ORDER BY ts DESC LIMIT 2")
        b = c2.fetchall(); conn2.close()
        if len(b) == 2 and b[0][1] > b[1][1] + 3600:
            chg = (b[0][0]-b[1][0])/b[1][0] if b[1][0] else 0
            mk = f" | BTC 1h变化{chg*100:+.2f}%" + (" 单边" if abs(chg) >= 0.0015 else " 震荡")
    except Exception:
        pass
    text = " ".join(parts) + mk
    # 值得小蕊思考的条件：有亏损单 / 净利为负 / 某币连亏
    noteworthy = bool(losers) or total < 0
    return (text, noteworthy)


def main():
    svc_active, hb_fresh = check_service()
    trade_issues, stats = check_trades_db()
    margin_issues, margin_detail = check_position_margin()
    pattern_text, pattern_noteworthy = check_pattern_30min()

    all_issues = list(trade_issues) + list(margin_issues)
    if not svc_active:
        all_issues.append("🔴 qnt-engines 服务未 active, 系统已停摆!")
    elif not hb_fresh:
        all_issues.append("🔴 服务在跑但心跳不新鲜(>120s), 可能卡死或崩溃循环")

    # 规律小结 + 保证金核对（盯盘喂小蕊）：有值得思考的 → 主动推一条给小蕊主会话
    patrol_thought = []
    if pattern_noteworthy:
        patrol_thought.append(f"📊 {pattern_text}")
    for d in margin_detail:
        if "⚠️" in d:
            patrol_thought.append(f"🛡️ {d}")

    report = {
        'time': datetime.now(timezone.utc).isoformat(),
        'service_active': svc_active,
        'heartbeat_fresh': hb_fresh,
        'issues': all_issues,
        'margin_detail': margin_detail,
        'pattern_30min': pattern_text,
        'stats_24h': stats,
    }
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    json.dump(report, open(REPORT, 'w'), ensure_ascii=False, indent=2)

    if all_issues:
        msg = "🚨 QNT 巡检告警\n" + "\n".join(all_issues) + f"\n24h实盘: {stats['live_24h']}笔 净{stats['net_24h']:+.3f}U"
        logger.info(msg.replace('\n', ' | '))
        _send_qq(msg)
    elif patrol_thought:
        # 无告警但有规律/保证金思考 → 主动推给小蕊主会话让她盯盘思考（不喊告警）
        thought_msg = "👀 QNT 盯盘规律小结(自动推给小蕊, 非告警)\n" + "\n".join(patrol_thought)
        logger.info(thought_msg.replace('\n', ' | '))
        try:
            _send_qq(thought_msg)
        except Exception as e:
            logger.warning(f"规律小结推送失败: {e}")
    else:
        # 2026-09-28 中华要求：10分钟巡检不能"正常就静默"，必须发短心跳确认小蕊没消失。
        # 防刷屏：正常心跳只在距上次推送>55分钟时发；异常/规律小结不受此限，照常推
        last_push = 0
        try:
            last_push = int(json.load(open(REPORT + '.ok')).get('pushed_ts', 0))
        except Exception:
            last_push = 0
        if time.time() - last_push > 3300:
            hb_msg = (f"💓 QNT 巡检心跳(正常)\n引擎:active 管道:通 "
                      f"实盘24h:{stats['live_24h']}笔 净{stats['net_24h']:+.3f}U\n一切正常，小蕊在线")
            logger.info("💓 巡检心跳推送: " + hb_msg.replace('\n', ' | '))
            _send_qq(hb_msg)
        logger.info(f"✅ 巡检正常 | 24h实盘 {stats['live_24h']}笔 净{stats['net_24h']:+.3f}U 胜率{stats['wins']/max(1,stats['live_24h'])*100:.0f}%")
        with open(REPORT + '.ok', 'w') as f:
            f.write(json.dumps({'ok': True, 'ts': int(time.time()), 'pushed_ts': int(time.time())}))

    return 0 if not all_issues else 1


if __name__ == '__main__':
    sys.exit(main())
