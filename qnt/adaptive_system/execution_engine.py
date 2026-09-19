"""
交易执行引擎 - 价差回归套利 + 风控（真实余额版）
v5.0: 永续价差回归套利，修复"同时开多开空"bug
修复内容:
1. 策略改为永续：永续价>现货价→永续开空；永续价<现货价→永续开多，绝不同时开多开空，绝不开现货腿
2. 修复调用不存在的 _execute_spread_arbitrage 导致的静默异常（实盘一直失败的根本原因）
3. 新增价差回归平仓闭环：价差回归到目标线内止盈，超时30分钟止损
4. 同币种已有仓位不重复开仓
5. Gate市价单不传cost参数（ccxt中cost只对现货市价买单有效）
6. 挂单表只记市价单ID，避免用现货实例查永续单导致报错
"""
import time
import logging
import sqlite3
from .db_utils import get_connection
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
import ccxt
import subprocess

from .config import SystemConfig
from .risk_manager import RiskManager
from .models import SignalRecord

logger = logging.getLogger('ExecutionEngine')

GATEWAY_URL = os.environ.get('OPENCLAW_GATEWAY_URL', 'http://localhost:14121')
_OPENCLAW_TOKEN = os.environ.get('OPENCLAW_GATEWAY_TOKEN', '')
QQ_TARGET = 'qqbot:c2c:861B1B2CC9C89FC4A3E0325F10407447'
_spread_alert_last = {}


_OPENCLAW_TOKEN = os.environ.get('OPENCLAW_GATEWAY_TOKEN', '')


def _send_qq_msg(msg: str):
    """通过OpenClaw Gateway发送QQ消息"""
    try:
        import urllib.request
        import json
        url = f'{GATEWAY_URL}/tools/invoke'
        body = json.dumps({
            'tool': 'message',
            'action': 'send',
            'args': {
                'target': QQ_TARGET,
                'message': msg
            }
        }).encode()
        req = urllib.request.Request(url, data=body, method='POST')
        req.add_header('Content-Type', 'application/json')
        if _OPENCLAW_TOKEN:
            req.add_header('Authorization', f'Bearer {_OPENCLAW_TOKEN}')
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception as e:
        logger.debug(f"发送QQ消息失败: {e}")
        return None


def _notify_close(ex_name, symbol, side, price, amount, position_size, net_pct, reason):
    """平仓盈亏即时推 QQ（2026-09-14 中华要求：平仓事件也要盯，不等巡检）"""
    try:
        ts = datetime.now().strftime('%H:%M:%S')
        emoji = "✅" if net_pct > 0 else "🛑"
        msg = f"{emoji} QNT平仓落袋\n平台: {ex_name}\n币种: {symbol}\n方向: 永续{side}\n价格: ${price:.4f}\n仓位: ${position_size:.2f}U\n净利: {net_pct*100:+.3f}%\n原因: {reason}\n时间: {ts}"
        if _send_qq_msg(msg):
            logger.info(f"📤 平仓通知已发送: {ex_name} {symbol} {net_pct*100:+.3f}%")
        else:
            logger.warning(f"⚠️ 平仓通知发送失败: {ex_name} {symbol}")
    except Exception as e:
        logger.debug(f"平仓通知失败: {e}")


def _notify_risk_pause(ex_name, reason):
    """风控熔断即时推 QQ（2026-09-14 中华要求：风控事件即时盯）"""
    try:
        ts = datetime.now().strftime('%H:%M:%S')
        msg = f"⛔ QNT风控熔断\n平台: {ex_name}\n原因: {reason}\n时间: {ts}"
        if _send_qq_msg(msg):
            logger.info(f"📤 风控熔断通知已发送: {ex_name} {reason}")
        else:
            logger.warning(f"⚠️ 风控熔断通知发送失败: {ex_name}")
    except Exception as e:
        logger.debug(f"风控熔断通知失败: {e}")


def _notify_trade(ex_name, symbol, side, price, amount, position_size, profit_pct):
    """发送交易通知到QQ"""
    try:
        ts = datetime.now().strftime('%H:%M:%S')
        msg = f"📈 QNT交易完成\n平台: {ex_name}\n币种: {symbol}\n方向: 永续{side}\n价格: ${price:.4f}\n数量: {amount:.4f}\n仓位: ${position_size:.2f}U\n预期净利: {profit_pct:.3f}%\n时间: {ts}"
        result = _send_qq_msg(msg)
        if result:
            logger.info(f"📤 交易通知已发送: {ex_name} {symbol}")
        else:
            logger.warning(f"⚠️ 交易通知发送失败: {ex_name} {symbol}")
    except Exception as e:
        logger.debug(f"发送通知失败: {e}")


def _notify_opportunity(ex_name, symbol, spread_pct, net_profit_pct):
    """发送价差机会预警到QQ（限速5分钟一次）"""
    global _spread_alert_last
    now = time.time()
    key = f"{ex_name}:{symbol}"
    last = _spread_alert_last.get(key, 0)
    if now - last < 300:
        return
    _spread_alert_last[key] = now
    try:
        ts = datetime.now().strftime('%H:%M:%S')
        msg = f"🔍 QNT价差机会预警\n平台: {ex_name}\n币种: {symbol}\n价差: {spread_pct*100:.3f}%\n净利(估): {net_profit_pct*100:.3f}%\n门槛: 价差>{(BI_SIDE_COST+RiskManager.MIN_NET_PROFIT_PCT)*100:.2f}%\n时间: {ts}"
        result = _send_qq_msg(msg)
        if result:
            logger.info(f"📤 价差预警已发送: {ex_name} {symbol} {spread_pct*100:.3f}%")
        else:
            logger.warning(f"⚠️ 价差预警发送失败: {ex_name} {symbol}")
    except Exception as e:
        logger.debug(f"发送预警失败: {e}")



# ============================================================
# 各交易所真实参数
# ============================================================
PERP_MIN_NOTIONAL = {'bitget': 5.0, 'htx': 1.0, 'gate': 3.0}
# 2026-09-12：htx 只监控低价可下单币种，避免高价币（ATOM/ONDO/TIA/FET/AVAX/LINK/INJ/BNB/BTC/ETH）反复"仓位不足跳过"空刷
# 这些币在 htx 算出的下单量 < 最小 1.0，永远下不了单，纯浪费扫描
HTX_LOW_PRICE_SYMBOLS = {'DOGE/USDT', 'PEPE/USDT','SOL/USDT', 'XRP/USDT', 'ONDO/USDT', 'FET/USDT', 'SHIB/USDT', 'ADA/USDT', 'TRX/USDT', 'LTC/USDT', 'BCH/USDT', 'NEAR/USDT', 'SUI/USDT', 'APT/USDT', 'SAND/USDT', 'GALA/USDT', 'IMX/USDT', 'DYDX/USDT', '1INCH/USDT', 'AAVE/USDT', 'SNX/USDT', 'COMP/USDT', 'MKR/USDT', 'CRV/USDT', 'ZEC/USDT', 'XLM/USDT', 'ALGO/USDT', 'FIL/USDT', 'AR/USDT'}
SPOT_MIN_NOTIONAL = {'bitget': 1.0, 'htx': 1.0, 'gate': 3.0}
BALANCE_BASELINE = {'bitget': 25.0, 'htx': 5.0, 'gate': 5.0}
LEVERAGE = 50

# 最低币数量精度（所有交易所）
# v4.1: 降低到0.01，适应小额账户
MIN_COIN_AMOUNT = 0.01

# ============================================================
# 价差回归套利参数（永续）
# ============================================================
# 平仓门槛：价差回归到目标线以下（保证净利 >= MIN_NET_PROFIT_PCT）
# 空头目标线 = -(BI_SIDE_COST - MIN_NET_PROFIT_PCT)
# 多头目标线 = +(BI_SIDE_COST - MIN_NET_PROFIT_PCT)
SPREAD_CLOSE_THRESHOLD = -0.001   # -0.10%：价差回归到目标线再平仓，让利润跑足（原-0.035%太紧，赚35bp就跑）
SPREAD_POSITION_TIMEOUT = 5400    # 持仓超时90分钟（2026-09-12：ATOM等高价币价差回归慢，60分钟太紧被超时止损切掉，放宽到90分钟）
# 硬止损：标的价格变动 ≥ 0.4% 立即平仓。
# 2026-09-13 口径澄清（中华指出模拟出现单笔-3.06%亏损远超止损线，定位到此处）：
# 这里的 0.4% 是【标的价格】变动（pnl_pct = 价差价格变动百分比，不是保证金盈亏）。
# 50x 杠杆下，标的 0.4% 价格变动 = 保证金 20% 变动，对应 20% 仓位时账户总亏损约 0.4%×20%仓位占比=很小的绝对值，
# 但历史上 -3.06% 那笔是因为标的价格在持仓期间单边漂移超过 0.4%（如 ONDO 1h 涨 0.3%+），止损线太宽，砍太晚。
# 修复方向：把止损线收紧到 0.15%（标的价格口径），与趋势过滤器阈值（1h 0.15%）对齐，防止「开仓后立刻变单边」的场景；
# 同时配合超时兜底，双重保险。
SINGLE_SIDE_STOP_LOSS_PCT = 0.0015  # 硬止损：标的价格浮亏≥0.15%（价格口径，非保证金口径）立即平仓，收紧防止砍晚

# 黄金时段加权：UTC 16-23 价差波动大、净利最高（历史+0.21%~0.26%），白天时段净利薄
TRADING_WINDOW_UTC_START = 16
TRADING_WINDOW_UTC_END = 23
# 亏损币种降仓：历史净利为负的币种，仓位减半
UNDERPERFORMER_SYMBOLS = {'TIA', 'FET'}
# 2026-09-12 拉黑名单：实盘数据验证为亏损/零收益币种，全平台跳过，不再开仓
BLACKLIST_SYMBOLS = {'WIF/USDT'}
UNDERPERFORMER_POSITION_SCALE = 0.5


class ExecutionEngine:
    """交易执行引擎（三平台版，永续价差回归套利，完整风控）"""
    
    # 手续费率（Maker）- 交易所真实费率
    MAKER_FEE_RATE = 0.0006   # 0.06%
    SLIPPAGE_RATE = 0.0002    # 0.02%
    TOTAL_COST = MAKER_FEE_RATE + SLIPPAGE_RATE  # 单边成本 = 0.08%
    BI_SIDE_COST = TOTAL_COST * 2  # 双边成本 = 0.16%（永续+现货）
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.running = False
        self.risk_manager = RiskManager(config.data.db_path)
        
        # 初始化交易所连接
        self.exchanges = {}
        self.perp_exchanges = {}
        self._connect_exchanges()
        
        self.open_orders = {}
        # 价差回归套利持仓：{ex_name: {symbol: pos_info}}
        self.spread_positions = {}
        self._load_spread_positions()  # 重启后从DB恢复持仓，接管交易所上已有的仓
        self._reconcile_positions()  # 2026-09-13：与交易所对账，清理孤儿仓（强平/被切但DB没删的）
        self._record_initial_principal()

    def _load_spread_positions(self):
        """从DB恢复上次运行遗留的持仓状态，重启后自动接管（避免孤儿仓无人管理）
        
        2026-09-13 修复：加载时与交易所真实持仓对账（_reconcile_positions），
        DB里挂着但交易所已无仓的 → 是孤儿仓（被强平/超时切了但没记DB），标记已平。
        """
        try:
            conn = get_connection(self.config.data.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT ex_name, symbol, perp_symbol, side, amount, position_size, "
                           "entry_price, entry_signed_spread, entry_time, close_params FROM spread_positions")
            for r in cursor.fetchall():
                ex_name, symbol, perp_symbol, side, amount, position_size, \
                    entry_price, entry_signed_spread, entry_time, close_params = r
                self.spread_positions.setdefault(ex_name, {})[symbol] = {
                    'perp_symbol': perp_symbol,
                    'side': side,
                    'amount': amount,
                    'position_size': position_size,
                    'entry_price': entry_price,
                    'entry_signed_spread': entry_signed_spread,
                    'entry_time': entry_time,
                    'close_params': json.loads(close_params) if close_params else {},
                }
            conn.close()
            if any(self.spread_positions.values()):
                logger.info(f"🔄 已从DB恢复 {sum(len(v) for v in self.spread_positions.values())} 个持仓，接管管理")
        except Exception as e:
            logger.warning(f"⚠️ 恢复持仓状态失败: {e}")
        
    def _reconcile_positions(self):
        """与交易所对账：DB里的持仓在交易所侧已不存在的，标记为已平（孤儿仓清理）。
        
        2026-09-13 新增：修复「Gate TIA/WIF 单被强平但DB没删，引擎当成还持有导致反复重复开仓」的bug。
        在引擎启动、持仓加载后调用一次；平仓检查也会定期调用。
        """
        for ex_name in list(self.spread_positions.keys()):
            if ex_name not in self.perp_exchanges:
                continue
            perp_exchange = self.perp_exchanges[ex_name]
            try:
                real_positions = perp_exchange.fetch_positions()
                real_syms = set()
                for p in real_positions:
                    if abs(p.get('contracts', 0) or 0) > 0:
                        real_syms.add(p.get('symbol'))
                for symbol in list(self.spread_positions[ex_name].keys()):
                    perp_symbol = self.spread_positions[ex_name][symbol].get('perp_symbol', symbol)
                    if perp_symbol not in real_syms:
                        pos = self.spread_positions[ex_name].pop(symbol)
                        logger.warning(f"🧹 孤儿仓清理: {ex_name} {symbol} DB有仓但交易所无仓（可能已强平/被切），已移除DB记录。原仓 {pos.get('position_size', 0):.2f}U {pos.get('side')}")
                        try:
                            conn = get_connection(self.config.data.db_path)
                            c = conn.cursor()
                            c.execute("DELETE FROM spread_positions WHERE ex_name=? AND symbol=?", (ex_name, symbol))
                            conn.commit()
                            conn.close()
                        except Exception as e2:
                            logger.debug(f"删除孤儿仓DB记录失败: {e2}")
            except Exception as e:
                logger.debug(f"{ex_name} 持仓对账失败: {e}")
    
    def _record_initial_principal(self):
        """记录初始本金，用于后续计算真实盈亏"""
        if self.risk_manager.equity > 0:
            self.risk_manager.set_initial_principal(self.risk_manager.equity)
            logger.info(f"💰 初始本金: {self.risk_manager.equity:.2f} USDT")
    
    def _connect_exchanges(self):
        """连接交易所（三平台：Bitget + HTX + Gate）
        每个平台同时创建现货和永续两个独立实例，避免账户混淆
        """
        exchange_map = {
            'bitget': ('BITGET_API_KEY', 'BITGET_API_SECRET', 'BITGET_API_PASSPHRASE'),
            'htx': ('HTX_API_KEY', 'HTX_API_SECRET', None),
            'gate': ('GATE_API_KEY', 'GATE_API_SECRET', None),
        }
        
        for ex_name, (key_env, secret_env, pass_env) in exchange_map.items():
            api_key = os.getenv(key_env, '')
            api_secret = os.getenv(secret_env, '')
            passphrase = os.getenv(pass_env, '') if pass_env else ''
            
            if not api_key:
                logger.warning(f"⚠️ {ex_name} API Key未设置，跳过")
                continue
            
            try:
                cls = getattr(ccxt, ex_name)
                
                # === 现货实例（无options，默认spot） ===
                spot_kwargs = {
                    'apiKey': api_key,
                    'secret': api_secret,
                    'enableRateLimit': True,
                    'timeout': 10000,
                }
                if passphrase:
                    spot_kwargs['password'] = passphrase
                self.exchanges[ex_name] = cls(spot_kwargs)
                
                # === 永续实例 ===
                perp_kwargs = spot_kwargs.copy()
                if ex_name == 'bitget':
                    # Bitget永续不需要options=swap，直接无options即可
                    perp_kwargs.pop('options', None)
                else:
                    perp_kwargs['options'] = {'defaultType': 'swap'}
                self.perp_exchanges[ex_name] = cls(perp_kwargs)
                
                # 设置杠杆
                leverage = LEVERAGE
                for symbol in self.config.data.symbols:
                    perp_symbol = f"{symbol.split('/')[0]}/USDT:USDT"
                    try:
                        self.perp_exchanges[ex_name].set_leverage(leverage, perp_symbol)
                        logger.info(f"✅ {ex_name} {perp_symbol} 杠杆已设置为 {leverage}x")
                    except Exception as e:
                        logger.debug(f"  {ex_name} {perp_symbol} 杠杆跳过: {e}")
                
                # 打印各账户余额
                spot_usdt = self._get_spot_balance(ex_name, self.exchanges[ex_name])
                perp_usdt = self._get_perp_balance(ex_name, self.perp_exchanges[ex_name])
                logger.info(f"✅ {ex_name} 交易引擎已连接 (现货${spot_usdt:.2f}U, 永续${perp_usdt:.2f}U)")
            except Exception as e:
                logger.error(f"❌ {ex_name} 连接失败: {e}")
    
    def _get_spot_balance(self, ex_name: str, exchange: ccxt.Exchange) -> float:
        """获取现货账户可用余额"""
        try:
            if ex_name == 'gate':
                # Gate: 必须用无options的实例查现货
                gate_key = os.getenv('GATE_API_KEY', '')
                gate_secret = os.getenv('GATE_API_SECRET', '')
                spot_cls = getattr(ccxt, 'gate')
                spot_ex = spot_cls({'apiKey': gate_key, 'secret': gate_secret, 'enableRateLimit': True})
                spot_bal = spot_ex.fetch_balance()
            elif ex_name == 'htx':
                spot_bal = exchange.fetch_balance({'type': 'spot'})
            else:
                spot_bal = exchange.fetch_balance()
            # ccxt v4兼容
            if isinstance(spot_bal, list):
                usdt_free = 0.0
                for section in spot_bal:
                    if isinstance(section, dict) and 'USDT' in section:
                        usdt_free += float(section['USDT'].get('free', 0) or 0)
                return usdt_free
            else:
                usdt = spot_bal.get('USDT', {})
                return float(usdt.get('free', 0) or 0)
        except Exception as e:
            logger.debug(f"获取{ex_name}现货余额失败: {e}")
            return 0.0
    
    def _get_perp_balance(self, ex_name: str, exchange: ccxt.Exchange) -> float:
        """获取永续合约账户可用余额"""
        try:
            if ex_name == 'gate':
                gate_key = os.getenv('GATE_API_KEY', '')
                gate_secret = os.getenv('GATE_API_SECRET', '')
                swap_cls = getattr(ccxt, 'gate')
                swap_ex = swap_cls({'apiKey': gate_key, 'secret': gate_secret, 'enableRateLimit': True, 
                                   'options': {'defaultType': 'swap'}})
                swap_bal = swap_ex.fetch_balance()
                if isinstance(swap_bal, list):
                    return sum(float(s.get('USDT', {}).get('free', 0) or 0) for s in swap_bal if isinstance(s, dict))
                else:
                    return float(swap_bal.get('USDT', {}).get('free', 0) or 0)
            elif ex_name == 'htx':
                htx_key = os.getenv('HTX_API_KEY', '')
                htx_secret = os.getenv('HTX_API_SECRET', '')
                htx_cls = getattr(ccxt, 'htx')
                swap_ex = htx_cls({'apiKey': htx_key, 'secret': htx_secret, 'enableRateLimit': True})
                swap_bal = swap_ex.fetch_balance({'type': 'swap'})
            else:
                swap_bal = exchange.fetch_balance()
            if isinstance(swap_bal, list):
                usdt_free = 0.0
                for section in swap_bal:
                    if isinstance(section, dict) and 'USDT' in section:
                        usdt_free += float(section['USDT'].get('free', 0) or 0)
                return usdt_free
            else:
                usdt = swap_bal.get('USDT', {})
                return float(usdt.get('free', 0) or 0)
        except Exception as e:
            logger.debug(f"获取{ex_name}永续余额失败: {e}")
            return 0.0
    
    def start(self):
        """启动执行引擎（2026-09-13 修复：改为后台守护线程，不再阻塞主线程）"""
        self.running = True
        if self.risk_manager.is_suspended:
            logger.warning(f"⛔ 风控暂停（仅停止实盘下单）: {self.risk_manager.suspension_reason}")
            _notify_risk_pause('全平台', self.risk_manager.suspension_reason)
        logger.info("🚀 交易执行引擎启动（永续价差回归套利v5.0）")
        logger.info(f"   监控平台: {', '.join(self.exchanges.keys())}")
        logger.info(f"   价差阈值: >{self.config.execution.spread_pct:.2f}% (执行引擎层)")
        logger.info(f"   净利阈值: >{self.config.execution.net_profit_pct:.2f}% (执行引擎层)")
        logger.info(f"   风控净利: >{RiskManager.MIN_NET_PROFIT_PCT*100:.2f}% (风控层，定死不变)")
        logger.info(f"   ⚠️ 实际交易门槛: 价差 > {(RiskManager.MIN_NET_PROFIT_PCT + ExecutionEngine.BI_SIDE_COST)*100:.2f}%")
        logger.info(f"   📌 杠杆: {LEVERAGE}x | 仓位: 永续余额×20%")
        logger.info(f"   🔒 币数量精度: >= {MIN_COIN_AMOUNT} (所有交易所)")
        logger.info(f"   🔒 Gate最小订单: >= {PERP_MIN_NOTIONAL['gate']}U")
        
        # 2026-09-13 修复：_run_loop 原来同步阻塞主线程，导致 __main__.py 后续的
        # DataCollector/LiveTradingController/EvolutionManager 全都没机会初始化（市场数据管道断更 3 天的真正病根）。
        # 改为起独立守护线程，主线程得以继续。
        import threading
        thread = threading.Thread(target=self._run_loop, daemon=True, name='exec-engine')
        thread.start()
        self._thread = thread
        logger.info("✅ 执行引擎线程已启动（exec-engine）")
    
    def _run_loop(self):
        """主循环"""
        while self.running:
            try:
                # 🔴 硬编码安全检查：config.live.enabled必须为True才允许实盘交易
                if not self.config.live.enabled:
                    logger.warning(f"⛔ 实盘交易未启用（config.live.enabled=False），仅运行风控监控")
                    self.risk_manager.refresh_balance()
                    time.sleep(30)
                    continue
                
                if self.risk_manager.is_suspended:
                    # 2026-09-13 修复：暂停只停「开新仓」，持仓管理（止盈/止损/超时检查）必须照常跑，
                    # 否则盈利单卡死不平、亏损单无人管，还出现「暂停8小时无人发现」的孤儿仓。
                    logger.warning(f"⛔ 风控暂停中(仅停开新仓，持仓管理继续): {self.risk_manager.suspension_reason}")
                    # 自动恢复：暂停满 30 分钟自动解除（不是无限期卡死）
                    if time.time() - getattr(self.risk_manager, 'suspended_at', 0) >= 1800:
                        self.risk_manager.is_suspended = False
                        self.risk_manager.consecutive_losses = 0
                        self.risk_manager.suspension_reason = ''
                        self.risk_manager.save_state()
                        logger.info('🔓 风控暂停30分钟到期，自动恢复开仓')

                # 定期刷新余额
                self.risk_manager.refresh_balance()
                
                # 遍历所有连接的交易所
                if not self.risk_manager.is_suspended:
                    for ex_name, spot_exchange in self.exchanges.items():
                        if ex_name in self.perp_exchanges:
                            try:
                                self._scan_and_execute(ex_name, spot_exchange, self.perp_exchanges[ex_name])
                            except Exception as e2:
                                logger.debug(f"{ex_name} scan error: {e2}")
                else:
                    logger.debug("⛔ 实盘已暂停，跳过开仓扫描（持仓管理照常）")
                
                # 检查挂单状态和持仓风险
                self.check_orders()
                
                time.sleep(self.config.data.update_interval)
                
            except KeyboardInterrupt:
                logger.info("用户中断")
                break
            except Exception as e:
                logger.error(f"执行错误: {e}")
                time.sleep(5)
    

    def _scan_and_execute(self, ex_name: str, spot_exchange: ccxt.Exchange, perp_exchange: ccxt.Exchange):
            """扫描并执行价差回归套利策略（永续，等价差回归后平仓）"""
            # 2026-09-12：htx 资金太少（0.56U），只监控低价币，跳过高价币避免反复"仓位不足"
            watchlist = [s for s in self.config.data.symbols if s in HTX_LOW_PRICE_SYMBOLS] if ex_name == 'htx' else self.config.data.symbols
            # 拉黑名单币种全平台跳过（实盘验证亏损/零收益）
            watchlist = [s for s in watchlist if s not in BLACKLIST_SYMBOLS]
            if not watchlist:
                return
            for symbol in watchlist:
                try:
                    spot_ticker = spot_exchange.fetch_ticker(symbol)
                    perp_symbol = f"{symbol.split('/')[0]}/USDT:USDT"
                    perp_ticker = perp_exchange.fetch_ticker(perp_symbol)

                    if not spot_ticker or not perp_ticker:
                        continue

                    spot_bid = spot_ticker.get('bid', 0)
                    spot_ask = spot_ticker.get('ask', 0)
                    perp_bid = perp_ticker.get('bid', 0)
                    perp_ask = perp_ticker.get('ask', 0)

                    if not all([spot_bid, spot_ask, perp_bid, perp_ask]):
                        continue

                    mid_spot = (spot_bid + spot_ask) / 2
                    mid_perp = (perp_bid + perp_ask) / 2
                    signed_spread = (mid_perp - mid_spot) / mid_spot

                    min_required = self.BI_SIDE_COST + RiskManager.MIN_NET_PROFIT_PCT
                    if abs(signed_spread) < min_required:
                        continue

                    main_perp_side = 'sell' if signed_spread > 0 else 'buy'

                    # 2026-09-12：取消非黄金时段1.5x加严，全时段统一门槛
                    # 价差 > 双边成本0.16% + 净利0.01% = 0.17% 时任何时候都赚，时段不再挡下单
                    # （黄金时段UTC 16-23 波动大仍可在日志中统计对比，但不影响开仓决策）

                    # === 趋势过滤器（2026-09-13 新增）===
                    # 价差回归策略在震荡市赚钱、单边市送钱（AT O M下跌中开多单被硬止损-0.49%、
                    # ONDO反弹中空单19分钟止损）。
                    # 开仓前看该币 1h 趋势：方向与开仓腿冲突的一边市 → 跳过，只赌震荡回归。
                    if not self._trend_allows_entry(spot_exchange, symbol, main_perp_side):
                        continue

                    # === 止损冷却（2026-09-13 新增）===
                    # 同一币种刚被硬止损后 30 分钟内禁止再开（防止 ONDO 止损完 1 分钟又重开、
                    # 连环止损）。查该币最近一条「止损」交易的时间戳。
                    if self._in_stop_loss_cooldown(ex_name, symbol):
                        logger.info(f"❄️ {ex_name} {symbol}: 止损冷却中(30min)，跳过")
                        continue

                    self._open_spread_position(ex_name, spot_exchange, perp_exchange, symbol,
                                               spot_bid, spot_ask, perp_bid, perp_ask,
                                               signed_spread, mid_perp, mid_spot, main_perp_side)

                except Exception as e:
                    logger.debug(f"{ex_name} {symbol} 扫描失败: {e}")

    def _trend_allows_entry(self, spot_exchange, symbol, main_perp_side):
        """趋势过滤器：开仓前确认该币不是单边行情（只赌震荡回归）。

        规则：看 1 小时变化率（15根4分钟K线≈1h）：
        - 开多（赌贴水回归）：价格 1h 内单边下跌 > 0.15% → 禁止开多（下跌趋势中价差不会回归）
        - 开空（赌升水回归）：价格 1h 内单边上涨 > 0.15% → 禁止开空（上涨趋势中价差不会回归）
        - 1h 内 |变化| <= 0.15% → 震荡市，允许开仓
        """
        try:
            base = symbol.split('/')[0]
            o = spot_exchange.fetch_ohlcv(symbol, '5m', limit=13)
            if not o or len(o) < 13:
                logger.debug(f"{symbol} K线数据不足，趋势过滤跳过检查")
                return True
            # 13根5m K线 ≈ 1h 窗口：比较第一根开盘价与最后一根收盘价
            h1_change = (o[-1][4] - o[0][1]) / o[0][1] if o[0][1] else 0
            THRESHOLD = 0.0015  # 1h 内 0.15%
            if main_perp_side == 'buy' and h1_change <= -THRESHOLD:
                logger.info(f"🚫 {symbol} 趋势过滤: 1h内下跌{abs(h1_change)*100:.2f}%>0.15%，单边下行中不开多")
                return False
            if main_perp_side == 'sell' and h1_change >= THRESHOLD:
                logger.info(f"🚫 {symbol} 趋势过滤: 1h内上涨{h1_change*100:.2f}%>0.15%，单边上行中不开空")
                return False
            return True
        except Exception as e:
            logger.debug(f"{symbol} 趋势过滤查询失败(放行): {e}")
            return True

    def _in_stop_loss_cooldown(self, ex_name, symbol):
        """止损冷却：同一交易所+币种最近 30 分钟内有「硬止损/超时止损」平仓的，禁止再开。

        防止 ONDO 止损完 1 分钟又开空、连环止损（00:59 止损 → 01:00 重开 的同病复发）。
        查 engine_trades 里该币最近一条 side 与平仓方向一致的「stop_loss」记录时间戳。
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.config.data.db_path)
            cur = conn.cursor()
            # 找最近一条 pnl_pct < 0 且 时间戳在30分钟内的止损单（开仓单pnl为预期正值，止损平仓单pnl为负）
            cur.execute("SELECT MAX(timestamp) FROM engine_trades WHERE exchange=? AND symbol=? AND pnl < 0", (ex_name, symbol))
            r = cur.fetchone()
            conn.close()
            if r and r[0]:
                age = time.time() - r[0]
                if age < 1800:  # 30分钟
                    return True
        except Exception as e:
            logger.debug(f"{ex_name} {symbol} 冷却查询失败(放行): {e}")
        return False

    def _open_spread_position(self, ex_name: str, spot_exchange: ccxt.Exchange, perp_exchange: ccxt.Exchange,
                              symbol: str, spot_bid: float, spot_ask: float,
                              perp_bid: float, perp_ask: float,
                              signed_spread: float, mid_perp: float, mid_spot: float, main_perp_side: str):
        """价差回归套利开仓：只开一条永续腿。

        策略铁律：
        - 永续价 > 现货价 (signed_spread > 0)  -> 永续开空 (sell)，等价差回归后平仓
        - 永续价 < 现货价 (signed_spread < 0)  -> 永续开多 (buy)，等价差回归后平仓
        绝不同时开多+开空，绝不开现货腿。
        """
        perp_symbol = f"{symbol.split('/')[0]}/USDT:USDT"

        if ex_name not in self.spread_positions:
            self.spread_positions[ex_name] = {}
        if symbol in self.spread_positions[ex_name]:
            return

        self.risk_manager.refresh_balance()
        total_equity = self.risk_manager.equity if self.risk_manager.equity > 0 else 1.0
        # 2026-09-18 修复：权益门槛接到引擎（旧版 LiveTradingController 只在「开→关」瞬间设 is_suspended，
        # 重启后 is_suspended 从DB=0 加载，控制器 60s 才首评——权益 10.8U 时引擎仍每轮扫价差试图开真仓，
        # 全靠"仓位<最小订单额"碰巧挡住。现在开仓前直接卡权益门槛，双保险）
        min_equity = self.config.live.min_equity
        if min_equity > 0 and total_equity < min_equity:
            logger.debug(f"🔒 {ex_name} {symbol}: 总权益{total_equity:.2f}U < 门槛{min_equity:.2f}U，跳过开仓")
            return
        perp_bal = self._get_perp_balance(ex_name, perp_exchange)

        # 仓位基准 = 该交易所永续账户余额（不爆仓），但至少要够交易所最小订单才能成交
        position_size = perp_bal * self.risk_manager.MAX_POSITION_PCT
        
        # 亏损币种降仓50% —— 2026-09-12 注释停用：WIF/ATOM/TIA/FET 被误标为亏损币，
        # 每单被砍到余额10%，资金利用率减半，与"19U本金滚10U/天"目标冲突。
        # 等实盘pnl记账修复后，用真实数据重新评估名单。当前停用降仓。
        # base = symbol.split('/')[0]
        # if base in UNDERPERFORMER_SYMBOLS:
        #     position_size *= UNDERPERFORMER_POSITION_SCALE
        #     logger.info(f"📉 {ex_name} {symbol}: 亏损币种仓位降{UNDERPERFORMER_POSITION_SCALE*100:.0f}% → {position_size:.2f}U")
        
        perp_side = main_perp_side

        # 用 ccxt 实时读该币种真实的最小下单数量，替代旧的写死 3.0U/1 币门槛
        amount = position_size / mid_perp if mid_perp > 0 else 0

        # 读取真实精度限制
        market = None
        try:
            market = perp_exchange.market(perp_symbol)
            amount_min = market['limits']['amount']['min'] or 0.0
            amount_precision = market['precision']['amount'] or 8
        except Exception:
            amount_min = 1.0  # 读不到就保守按最小 1 币
            amount_precision = 8

        if amount_min > 0 and amount < amount_min:
            # 仓位买不起该币 1 个最低下单单位（高价币），自动跳过，不反复报错
            logger.info(f"⚠️ {ex_name} {symbol}: 下单量{amount:.4f} < 最小{amount_min}，高价币仓位不足，跳过")
            return

        # === 2026-09-14 中华复盘防线（上次爆仓根因：每笔都开20%，把该平台永续用100%，强平爆仓）===
        # 铁律（中华 2026-09-14 定稿，按【本平台】算，不跨平台总算）：
        #   本平台永续已开保证金合计 ≤ 本平台永续余额 × 20%（留80%在永续里才不爆仓）
        # 旧bug：position_size = perp_bal × 0.20 每笔都按"余额的20%"开，开N笔就把永续用了N×20%（甚至100%）。
        # 修复：已开多少扣多少，本笔 = min(原公式, 本平台永续余额×20% − 已开合计)，开完该平台永续保证金恒 ≤20%。
        perp_cap = perp_bal * self.risk_manager.MAX_POSITION_PCT
        used_margin = sum(v.get('position_size', 0) for v in self.spread_positions.get(ex_name, {}).values())
        headroom = perp_cap - used_margin
        if headroom <= 0:
            logger.info(f"🛡️ {ex_name} {symbol}: 该平台永续已开保证金 {used_margin:.2f}U 已达永续余额20%({perp_cap:.2f}U)，剩余名额0，跳过开仓")
            return
        # 本笔 = min(原公式, 本平台剩余名额)：保证开完后【该平台】永续保证金 ≤ 余额20%
        if position_size > headroom:
            logger.info(f"🛡️ {ex_name} {symbol}: 仓位 {position_size:.2f}U → 压缩至本平台剩余名额 {headroom:.2f}U（该平台永续保证金恒≤余额20%）")
            position_size = headroom
            amount = position_size / mid_perp if mid_perp > 0 else 0
        # 若压缩后低于最小下单单位/最小订单额，本笔直接放弃（不开小碎单）
        if market and market.get('limits',{}).get('amount',{}).get('min'):
            if position_size / mid_perp < market['limits']['amount']['min']:
                logger.info(f"🛡️ {ex_name} {symbol}: 压缩后仓位 {position_size:.2f}U 低于最小下单单位，跳过本笔（不硬凑碎单）")
                return

        # === 2026-09-14 风控总纲双保险（中华定稿：20%仓位管理适用所有交易/所有资金池）===
        # 各池分池限20%之外，再卡一道【总资金】口径：本平台已开保证金(全部交易) ≤ 本平台总权益×20%
        # 防止任何一路（永续/其它合约/现货）把本平台资金池用穿。已开多少扣多少。
        platform_equity = self.risk_manager.real_balance.get(ex_name, {}).get('total', 0.0) or total_equity
        platform_opened = sum(v.get('position_size', 0) for v in self.spread_positions.get(ex_name, {}).values())
        platform_cap = platform_equity * self.risk_manager.MAX_POSITION_PCT
        platform_headroom = platform_cap - platform_opened
        if platform_headroom <= 0:
            logger.info(f"🛡️ {ex_name} {symbol}: 该平台总资金已开保证金 {platform_opened:.2f}U 已达总权益20%({platform_cap:.2f}U)，跳过开仓")
            return
        if position_size > platform_headroom:
            logger.info(f"🛡️ {ex_name} {symbol}: 仓位 {position_size:.2f}U → 压缩至该平台总资金剩余额度 {platform_headroom:.2f}U（20%仓位管理双保险）")
            position_size = platform_headroom
            amount = position_size / mid_perp if mid_perp > 0 else 0
        # 若仓位金额低于交易所最小订单金额，把仓位提到最小订单金额（前提是不超过永续余额且不破20%双保险）
        try:
            cost_min = market['limits']['cost']['min'] if market else None
        except Exception:
            cost_min = None
        if cost_min and position_size < float(cost_min):
            if float(cost_min) <= min(perp_bal, position_size + platform_headroom - (platform_cap - platform_opened)):
                position_size = float(cost_min)
                amount = position_size / mid_perp if mid_perp > 0 else 0
                logger.info(f"📐 {ex_name} {symbol}: 仓位提到最小订单{position_size:.2f}U")
            else:
                logger.info(f"⚠️ {ex_name} {symbol}: 永续余额/剩余额度 < 最小订单{cost_min}U，跳过")
                return

        # 兜底：量仍不够 1 张的跳过（永续按张计价时）
        if amount_min > 0 and amount < amount_min:
            logger.info(f"⚠️ {ex_name} {symbol}: 下单量{amount:.4f} < 最小{amount_min}，跳过")
            return

        stop_loss_price = mid_perp * (1 + self.risk_manager.MAX_STOP_LOSS_PCT) if perp_side == 'sell' else mid_perp * (1 - self.risk_manager.MAX_STOP_LOSS_PCT)
        risk_check = self.risk_manager.check_risk(
            symbol=symbol,
            side=perp_side,
            position_size_usdt=position_size,
            entry_price=mid_perp,
            stop_loss_price=stop_loss_price,
            ex_name=ex_name
        )
        if not risk_check['allowed']:
            logger.warning(f"⛔ {ex_name} {symbol} 风控拒绝: {risk_check['reason']}")
            return

        try:
            perp_params = {}
            perp_order = perp_exchange.create_order(
                symbol=perp_symbol,
                type='market',
                side=perp_side,
                amount=amount,
                params=perp_params,
            )
            logger.info(f"✅ {ex_name} {symbol} 永续{'开空' if perp_side=='sell' else '开多'}@{mid_perp:.4f} 数量={amount:.4f} 仓位={position_size:.2f}U 价差={signed_spread*100:+.4f}%")
        except Exception as e:
            perp_err = str(e)[:200]
            logger.error(f"❌ {ex_name} {symbol} 永续{perp_side}下单失败: {perp_err}")
            self._record_signal(ex_name, symbol, perp_side, abs(signed_spread) - self.BI_SIDE_COST, position_size, failed=True, errors=f"perp:{perp_err}")
            return

        self.spread_positions[ex_name][symbol] = {
            'perp_symbol': perp_symbol,
            'side': perp_side,
            'amount': amount,
            'position_size': position_size,
            'entry_price': mid_perp,
            'entry_signed_spread': signed_spread,
            'entry_time': time.time(),
            'close_params': dict(perp_params),
        }

        # 持久化持仓到DB（重启后能恢复接管，避免孤儿仓）
        try:
            conn = get_connection(self.config.data.db_path)
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO spread_positions "
                      "(ex_name, symbol, perp_symbol, side, amount, position_size, entry_price, "
                      "entry_signed_spread, entry_time, close_params) "
                      "VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (ex_name, symbol, perp_symbol, perp_side, amount, position_size,
                       mid_perp, signed_spread, self.spread_positions[ex_name][symbol]['entry_time'],
                       json.dumps(dict(perp_params))))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"持久化持仓失败: {e}")

        net_profit_pct = abs(signed_spread) - self.BI_SIDE_COST
        self._record_trade(ex_name, symbol, perp_side, mid_perp, amount, position_size, net_profit_pct)
        self._record_signal(ex_name, symbol, perp_side, net_profit_pct, position_size)
        _notify_trade(ex_name, symbol, perp_side, mid_perp, amount, position_size, net_profit_pct)

    def _check_spread_positions(self, ex_name: str, spot_exchange: ccxt.Exchange, perp_exchange: ccxt.Exchange):
        """监控价差回归套利仓位，满足条件即平仓（永续，无现货腿）。

        平仓条件：
        - 价差回归：现价差回落到目标线内 → 获利平仓
        - 超时：持仓超过 SPREAD_POSITION_TIMEOUT 仍未回归 → 按盈亏方向平仓（浮盈记"浮盈"，否则"止损"）
        """
        ex_positions = self.spread_positions.get(ex_name)
        if not ex_positions:
            return

        for symbol in list(ex_positions.keys()):
            pos = ex_positions.get(symbol)
            if not pos:
                ex_positions.pop(symbol, None)
                continue

            try:
                perp_ticker = perp_exchange.fetch_ticker(pos['perp_symbol'])
                spot_ticker = spot_exchange.fetch_ticker(symbol)
                if not perp_ticker or not spot_ticker:
                    continue

                perp_mid = (perp_ticker.get('bid', 0) + perp_ticker.get('ask', 0)) / 2
                spot_mid = (spot_ticker.get('bid', 0) + spot_ticker.get('ask', 0)) / 2
                if perp_mid <= 0 or spot_mid <= 0:
                    continue

                cur_spread = (perp_mid - spot_mid) / spot_mid
                age = time.time() - pos['entry_time']
                side = pos['side']

                # 2026-09-13 分档平仓逻辑（利润最大化 + 风险最小化）：
                # 核心思路：止盈不是固定线，要看「价差方向」——
                #   价差还在扩大（没回归迹象）→ 不平，让利润跑（50x下价差多回归0.1%=净利多0.10%）
                #   价差开始回归（缩小）→ 立刻平，落袋
                #   到90分钟还没回归 → 无条件超时切掉（防套牢）
                #   浮亏≥0.4% → 硬止损立即平（风险最小化）
                entry_price = pos['entry_price']
                if side == 'sell':
                    pnl_pct = (entry_price - perp_mid) / entry_price if entry_price > 0 else 0
                else:
                    pnl_pct = (perp_mid - entry_price) / entry_price if entry_price > 0 else 0
                net = pnl_pct - self.BI_SIDE_COST

                # 价差方向判断：空单（赌升水回归）价差在缩小=回归中；多单（赌贴水回归）价差在增大=回归中
                entry_spread = pos.get('entry_signed_spread', 0)
                spread_shrinking = (side == 'sell' and cur_spread < entry_spread) or \
                                   (side == 'buy' and cur_spread > entry_spread)

                converged = (side == 'sell' and cur_spread <= SPREAD_CLOSE_THRESHOLD) or \
                            (side == 'buy' and cur_spread >= -SPREAD_CLOSE_THRESHOLD)
                timed_out = age >= SPREAD_POSITION_TIMEOUT

                hard_stop = pnl_pct <= -SINGLE_SIDE_STOP_LOSS_PCT
                # 2026-09-18 修复：MIN_NET_PROFIT_PCT 在 RiskManager 类上，不在 ExecutionEngine，
                # 旧写法 self.MIN_NET_PROFIT_PCT 抛 AttributeError 被 except 静默吞掉 →
                # 止盈/止损/超时平仓全部瘫痪（ONDO 浮亏无人砍 4 天的直接根因）
                _min_net = RiskManager.MIN_NET_PROFIT_PCT
                # 2026-09-13 分档：净利达标 且 价差在回归（缩小）→ 立即止盈；
                #          净利达标 但 价差还在扩大 → 不平，让利润继续跑（到超时线前）
                take_profit = net >= _min_net and spread_shrinking
                let_profit_run = net >= _min_net and not spread_shrinking

                if hard_stop or take_profit or (converged and net > 0) or timed_out:
                    pass  # 需要平仓
                else:
                    if let_profit_run:
                        logger.debug(f"⏳ {ex_name} {symbol} 净利{net*100:+.2f}%达标但价差仍在扩大，继续持有让利润跑")
                    continue

                close_side = 'buy' if side == 'sell' else 'sell'

                # 2026-09-13 平仓优先级：硬止损 > 止盈(价差回归中) > 价差回归到目标线 > 超时兜底
                if hard_stop:
                    reason = f'单边硬止损{pnl_pct*100:+.2f}%'
                elif take_profit:
                    reason = f'净利{net*100:+.2f}%达标+价差回归中，止盈落袋'
                elif converged and net > 0:
                    reason = '价差回归到目标线，止盈'
                elif net > 0:
                    reason = f'超时{int(age//60)}分钟平仓(浮盈{net*100:+.2f}%)'
                else:
                    reason = f'超时{int(age//60)}分钟止损(亏{net*100:+.2f}%)'
                
                logger.info(f"🏁 {ex_name} {symbol} {reason}: 现价差={cur_spread*100:+.4f}% 持仓{int(age//60)}分钟 "
                           f"毛盈亏={pnl_pct*100:+.4f}% 净利={net*100:+.4f}% → 平仓 {close_side} {pos['amount']:.4f}")

                ok = True
                try:
                    close_params = dict(pos['close_params'])
                    close_params['reduceOnly'] = True  # 关键：Gate/HTX 平仓必须 reduceOnly，否则 sell 会被当成新开空单
                    perp_exchange.create_order(
                        symbol=pos['perp_symbol'],
                        type='market',
                        side=close_side,
                        amount=pos['amount'],
                        params=close_params,
                    )
                except Exception as e:
                    ok = False
                    logger.error(f"❌ {ex_name} {symbol} 平仓失败: {e}")

                if ok:
                    del ex_positions[symbol]
                    logger.info(f"✅ {ex_name} {symbol} 价差套利平仓完成: 净利≈{net*100:+.4f}%")
                    self._record_trade(ex_name, symbol, close_side, perp_mid, pos['amount'],
                                       pos['position_size'], net, failed=False)
                    self.risk_manager.record_trade(net * pos['position_size'], is_win=(net > 0))
                    _notify_close(ex_name, symbol, side, perp_mid, pos['amount'],
                                  pos['position_size'], net, reason)
                    # 从DB删除已平仓的持仓
                    try:
                        conn = get_connection(self.config.data.db_path)
                        c = conn.cursor()
                        c.execute("DELETE FROM spread_positions WHERE ex_name=? AND symbol=?", (ex_name, symbol))
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        logger.debug(f"删除持久化持仓失败: {e}")
            except Exception as e:
                logger.debug(f"{ex_name} {symbol} 仓位检查失败: {e}")

    def check_orders(self):
        """检查持仓风险：遍历各交易所的价差回归持仓并尝试平仓"""
        # 定期与交易所对账（清理孤儿仓：被强平/超时切掉但DB没删的仓）
        now = time.time()
        if not hasattr(self, '_last_reconcile') or now - self._last_reconcile > 600:
            self._reconcile_positions()
            self._last_reconcile = now
        for ex_name, spot_exchange in self.exchanges.items():
            if ex_name not in self.perp_exchanges:
                continue
            perp_exchange = self.perp_exchanges[ex_name]
            try:
                self._check_spread_positions(ex_name, spot_exchange, perp_exchange)
            except Exception as e:
                logger.debug(f"检查{ex_name}持仓失败: {e}")

    def _record_trade(self, exchange: str, symbol: str, side: str, price: float, amount: float,
                      position_size: float, profit_pct: float, failed: bool = False):
        """记录成功/部分成功的交易到engine_trades表。
        
        pnl 记账修复（2026-09-12）：
        - 之前 pnl/fee 都填 0，导致进化引擎无法学习真实收益，策略永远不升级
        - profit_pct 是「预期净利」（开仓时 价差 - 双边成本），不代表真实收益
        - 这里按「预期净利 × 仓位」记 pnl，至少让进化引擎有非零数据可分析
        - 真实盈亏仍由平仓日志（价差套利平仓完成: 净利≈...）为准
        """
        try:
            # 预期净利绝对值（USDT）= 预期净利百分比 × 仓位
            # 2026-09-18 修复：开仓单的 profit_pct 是预期净利（恒正），但平仓单传入的是真实净利 net（可负）。
            # 旧写法 abs() 把亏损单也记成正数 → 止损冷却查 pnl<0 永远查不到 → 连环止损。
            # 开仓单保持正数（预期值），平仓单保留负号（真实值）。
            expected_pnl = position_size * abs(profit_pct) if failed else position_size * profit_pct
            fee_estimate = position_size * 0.0004  # 单边手续费估算（taker 0.04%）
            conn = get_connection(self.config.data.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO engine_trades (timestamp, mode, exchange, symbol, side, price, amount, "
                "cost, fee, pnl, pnl_pct, status) VALUES (?, 'live', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (int(time.time()), exchange, symbol, side, price, amount,
                 position_size, fee_estimate, expected_pnl, profit_pct,
                 'partial' if failed else 'completed')
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"记录交易失败: {e}")

    def _record_signal(self, exchange: str, symbol: str, side: str, profit: float,
                       position_size: float = 0, failed: bool = False, errors: str = ''):
        """记录信号到engine_signals表"""
        try:
            conn = get_connection(self.config.data.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO engine_signals (timestamp, mode, exchange, symbol, "
                "signal_type, strategy, expected_profit, executed, metadata) "
                "VALUES (?, 'live', ?, ?, 'spread_arb', 'spread_arbitrage', ?, ?, ?)",
                (int(time.time()), exchange, symbol, profit, 0 if failed else 1,
                 errors if errors else json.dumps({'side': side, 'position_size': position_size}))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"记录信号失败: {e}")

    def get_status(self) -> Dict:
        """获取执行引擎状态"""
        return {
            'running': self.running,
            'risk': self.risk_manager.get_status(),
            'spread_positions': {k: list(v.keys()) for k, v in self.spread_positions.items()},
            'exchanges': list(self.exchanges.keys()),
        }

    def stop(self):
        """停止执行引擎"""
        self.running = False
        self.risk_manager.close()
        logger.info("🛑 执行引擎已停止")
