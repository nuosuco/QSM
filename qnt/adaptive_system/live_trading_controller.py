"""
实盘交易自动开关控制器

职责（明确）：
- 只控制实盘交易（ExecutionEngine）的开/停
- 回测(BacktestEngine) + 模拟(PaperEngine) 由 dual_engine 启动，**完全不受本控制器影响**

开启条件（全部满足才自动开实盘）：
1. 账户权益 >= live.min_equity        （本金不够，策略再好也下不了单）
2. 必需平台全部连接成功
3. 模拟盘滚动窗口 >= live.min_paper_trades  笔
4. 模拟盘滚动窗口胜率 >= live.min_paper_win_rate

自动停止条件（任一触发）：
- 连续亏损 >= 3 次
- 最大回撤 >= 8%
- 单日亏损 >= 3%
- 市场状态 extreme 且连续 2 次分析周期确认（防误判）

自动恢复：市场回到 volatile/normal 且无其他暂停原因 → 自动解除，无需人工干预

状态持久化到 SQLite risk_state 表（risk_manager 会读取），重启不丢失。
"""
import sqlite3
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Optional, List

logger = logging.getLogger('LiveTradingController')


class LiveTradingController:
    """实盘自动开关 - 只管控实盘，不碰回测/模拟"""

    MAX_CONSECUTIVE_LOSSES = 3     # 连续亏损次数 → 停止实盘
    MAX_DRAWDOWN_PCT = 0.08        # 最大回撤 → 停止实盘
    MAX_DAILY_LOSS_PCT = 0.03      # 单日亏损 → 停止实盘
    REQUIRE_EXTREME_CONFIRM = 2    # extreme 市场需连续确认次数

    def __init__(self, config, db_path: str, dual_engine, exec_engine,
                 platforms: Optional[List[str]] = None):
        self.config = config
        self.db_path = db_path
        self.dual_engine = dual_engine
        self.exec_engine = exec_engine
        self.platforms = platforms or ['bitget', 'htx', 'gate']

        self.running = False
        self.thread = None
        self.interval = 60  # 60秒检查一次

        self.is_live_enabled = False
        self.consecutive_losses = 0
        self.total_profit = 0.0
        self.daily_profit = 0.0
        self.daily_date = datetime.now().strftime('%Y-%m-%d')
        self.max_drawdown = 0.0
        self.peak_profit = 0.0
        self.extreme_confirm = 0
        self.suspension_reasons = []
        self.last_report = 0

    def start(self):
        live = self.config.live
        if not live.enabled:
            logger.info("=" * 60)
            logger.info("🚫 实盘自动开关已禁用（config.live.enabled=false）")
            logger.info("   回测 + 模拟照常运行，实盘保持关闭")
            logger.info("=" * 60)
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

        logger.info("=" * 60)
        logger.info("🎛️ 实盘自动开关已启动")
        logger.info(f"   开启条件: 权益>={live.min_equity}U, 平台全连, "
                    f"模拟盘>={live.min_paper_trades}笔 且 胜率>={live.min_paper_win_rate*100:.0f}%")
        logger.info(f"   停止条件: 连亏>={self.MAX_CONSECUTIVE_LOSSES}次 / "
                    f"回撤>={self.MAX_DRAWDOWN_PCT*100:.0f}% / 日亏>={self.MAX_DAILY_LOSS_PCT*100:.0f}% / 极端市场")
        logger.info("   ℹ️ 回测+模拟不受本控制器影响，始终运行")
        logger.info("=" * 60)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("🎛️ 实盘自动开关已停止")

    def _run_loop(self):
        while self.running:
            try:
                self.evaluate()
            except Exception as e:
                logger.error(f"实盘开关检查错误: {e}")
            time.sleep(self.interval)

    def evaluate(self):
        live = self.config.live

        # 状态过期日志（5分钟一条，避免刷屏）
        now = time.time()
        if now - self.last_report > 300:
            try:
                dual_st = self.dual_engine.get_status()
                bt = dual_st.get('backtest', {})
                pp = dual_st.get('paper', {})
                logger.info(f"🎛️ 实盘开关 | 实盘={'✅开' if self.is_live_enabled else '🔒关'}"
                            f" | 模拟盘{pp.get('total_trades', 0)}笔(胜率{pp.get('win_rate', 0)*100:.1f}%)"
                            f" 余额${pp.get('balance', 0):.2f}"
                            f" | 回测{bt.get('total_trades', 0)}笔"
                            f" | 原因{self.suspension_reasons or '无'}")
            except Exception:
                pass
            self.last_report = now

        # 重置每日亏损
        today = datetime.now().strftime('%Y-%m-%d')
        if today != self.daily_date:
            self.daily_profit = 0.0
            self.daily_date = today

        # 1. 硬性前置条件
        self.suspension_reasons = []

        equity = self._get_equity()
        if equity < live.min_equity:
            self.suspension_reasons.append(f"权益{equity:.2f}U < 最低{live.min_equity}U")

        connected, failed = self._check_platforms()
        if not connected:
            self.suspension_reasons.append(f"平台未连接: {','.join(failed)}")

        # 2. 市场环境
        regime = self._get_regime()
        if regime == 'extreme':
            self.extreme_confirm += 1
            if self.extreme_confirm >= self.REQUIRE_EXTREME_CONFIRM:
                self.suspension_reasons.append("极端市场(连续确认)")
        else:
            self.extreme_confirm = 0

        # 3. 模拟盘窗口表现
        pp_trades, pp_win_rate = self._get_paper_window()
        if pp_trades < live.min_paper_trades:
            self.suspension_reasons.append(
                f"模拟盘样本不足: {pp_trades}笔 < {live.min_paper_trades}笔")
        elif pp_win_rate < live.min_paper_win_rate:
            self.suspension_reasons.append(
                f"模拟盘胜率{pp_win_rate*100:.1f}% < {live.min_paper_win_rate*100:.0f}%")

        # 4. 亏损/回撤（实盘运行中才累积）
        if self.consecutive_losses >= self.MAX_CONSECUTIVE_LOSSES:
            self.suspension_reasons.append(
                f"连续亏损{self.consecutive_losses}次")
        if self.max_drawdown >= self.MAX_DRAWDOWN_PCT:
            self.suspension_reasons.append(
                f"最大回撤{self.max_drawdown*100:.1f}%")
        if self.daily_profit <= -self.MAX_DAILY_LOSS_PCT * equity:
            self.suspension_reasons.append(
                f"单日亏损{self.daily_profit:.2f}U")

        # 5. 应用开/关
        self._apply()

    def _apply(self):
        want_enabled = len(self.suspension_reasons) == 0

        if want_enabled and not self.is_live_enabled:
            self._enable_live()
        elif not want_enabled and self.is_live_enabled:
            self._disable_live()

        self._persist()

    def _enable_live(self):
        rm = getattr(self.exec_engine, 'risk_manager', None)
        if rm is not None:
            rm.is_suspended = False
            rm.suspension_reason = ''
            if hasattr(rm, 'save_state'):
                try:
                    rm.save_state()
                except Exception as e:
                    logger.error(f"保存风控状态失败: {e}")
        self.is_live_enabled = True
        logger.info("=" * 60)
        logger.info("🟢 实盘交易已自动开启")
        logger.info(f"   模拟盘窗口满足开启条件，权益充足，平台正常，市场稳定")
        logger.info("   回测 + 模拟照常运行（不受影响）")
        logger.info("=" * 60)

    def _disable_live(self):
        rm = getattr(self.exec_engine, 'risk_manager', None)
        if rm is not None:
            rm.is_suspended = True
            rm.suspension_reason = f"实盘自动暂停: {'; '.join(self.suspension_reasons)}"
            if hasattr(rm, 'save_state'):
                try:
                    rm.save_state()
                except Exception as e:
                    logger.error(f"保存风控状态失败: {e}")
        self.is_live_enabled = False
        logger.info("=" * 60)
        logger.info("🔴 实盘交易已自动停止")
        for r in self.suspension_reasons:
            logger.warning(f"   原因: {r}")
        logger.info("   ℹ️ 回测 + 模拟照常运行，继续总结规律")
        logger.info("=" * 60)

    def _persist(self):
        """持久化到 risk_state，避免重启后状态丢失"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS risk_state (key TEXT PRIMARY KEY, value TEXT)")
            c.execute("INSERT OR REPLACE INTO risk_state (key, value) VALUES (?, ?)",
                      ('live_enabled', '1' if self.is_live_enabled else '0'))
            c.execute("INSERT OR REPLACE INTO risk_state (key, value) VALUES (?, ?)",
                      ('live_reason', '; '.join(self.suspension_reasons)))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"持久化失败: {e}")

    def _get_equity(self) -> float:
        try:
            rm = getattr(self.exec_engine, 'risk_manager', None)
            if rm is not None and getattr(rm, 'equity', 0) > 0:
                return rm.equity
        except Exception:
            pass
        return 0.0

    def _check_platforms(self):
        connected, failed = True, []
        ex_map = getattr(self.exec_engine, 'exchanges', {})
        for ex in self.platforms:
            if ex not in ex_map:
                failed.append(ex)
        if failed:
            connected = False
        return connected, failed

    def _get_regime(self) -> str:
        try:
            if self.config.data.db_path != self.db_path:
                return 'unknown'
            conn = sqlite3.connect(self.db_path, timeout=10)
            c = conn.cursor()
            c.execute("""SELECT spread_pct FROM market_data
                         WHERE timestamp > strftime('%s','now','-24 hours')
                         ORDER BY timestamp DESC LIMIT 1000""")
            spreads = [r[0] for r in c.fetchall() if r[0] is not None]
            conn.close()
            if len(spreads) < 50:
                return 'unknown'
            import numpy as np
            vol = float(np.std(spreads))
            if vol < 0.02:
                return 'calm'
            if vol < 0.05:
                return 'normal'
            if vol < 0.10:
                return 'volatile'
            return 'extreme'
        except Exception as e:
            logger.debug(f"市场状态获取失败: {e}")
            return 'unknown'

    def _get_paper_window(self):
        """取模拟盘滚动窗口的交易数与胜率"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            c = conn.cursor()
            live = self.config.live
            window = int(live.paper_window_hours * 3600)
            c.execute("""SELECT COUNT(*),
                                COALESCE(SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END), 0)
                         FROM engine_trades
                         WHERE mode='paper' AND timestamp > strftime('%s','now', ?)""",
                      (f'-{window} hours',))
            row = c.fetchone()
            trades, wins = row[0], row[1]
            conn.close()
            return trades, (wins / trades if trades else 0.0)
        except Exception as e:
            logger.debug(f"模拟盘窗口读取失败: {e}")
            return 0, 0.0

    def get_status(self) -> Dict:
        return {
            'live_enabled': self.is_live_enabled,
            'suspension_reasons': list(self.suspension_reasons),
            'consecutive_losses': self.consecutive_losses,
            'max_drawdown': self.max_drawdown,
            'daily_profit': self.daily_profit,
            'extreme_confirm': self.extreme_confirm,
        }
