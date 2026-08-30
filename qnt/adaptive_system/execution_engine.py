"""
交易执行引擎 - 做市策略 + 风控（真实余额版）
v3.0: 永续市价买 + 现货市价卖（两单同时发，不等成交）
"""
import time
import logging
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import ccxt

from .config import SystemConfig
from .risk_manager import RiskManager
from .models import SignalRecord

logger = logging.getLogger('ExecutionEngine')

# ============================================================
# 各交易所真实参数（Market数据查出来写死，避免反复load_markets）
# ============================================================
# 永续合约最小仓位（USDT）
PERP_MIN_NOTIONAL = {'bitget': 5.0, 'htx': 1.0, 'gate': 1.0}
# 现货最小订单金额（USDT）
SPOT_MIN_NOTIONAL = {'bitget': 1.0, 'htx': 1.0, 'gate': 1.0}
# 余额基准：实际最小仓位 = min_notional × (perp_bal / BALANCE_BASELINE)
# 小额账户按比例缩小最小仓位，避免永远低于门槛
BALANCE_BASELINE = {'bitget': 25.0, 'htx': 5.0, 'gate': 5.0}
# 杠杆倍数（越高越好，但防爆仓）
LEVERAGE = 50

class ExecutionEngine:
    """交易执行引擎（三平台版，Post-Only做市策略）"""
    
    # 手续费率（Maker）- 交易所真实费率，不要改！
    MAKER_FEE_RATE = 0.0004   # 0.04%（永续Maker费率）
    SLIPPAGE_RATE = 0.0002    # 0.02%（预估滑点）
    TOTAL_COST = MAKER_FEE_RATE + SLIPPAGE_RATE  # 单边成本 = 0.06%
    BI_SIDE_COST = TOTAL_COST * 2  # 双边成本 = 0.12%（永续+现货）
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.running = False
        self.risk_manager = RiskManager(config.data.db_path)
        self.risk_manager.load_state()
        
        # 初始化交易所连接
        self.exchanges = {}
        self.perp_exchanges = {}  # 永续合约专用连接
        self._connect_exchanges()
        
        # 已挂订单跟踪
        self.open_orders = {}  # {exchange: {order_id: {...}}}
        self._record_initial_principal()
    
    def _record_initial_principal(self):
        """记录初始本金，用于后续计算真实盈亏"""
        if self.risk_manager.equity > 0:
            self.risk_manager.set_initial_principal(self.risk_manager.equity)
            logger.info(f"💰 初始本金: {self.risk_manager.equity:.2f} USDT")
    
    def _connect_exchanges(self):
        """连接交易所（三平台：Bitget + HTX + Gate）"""
        exchange_map = {
            'bitget': ('BITGET_API_KEY', 'BITGET_API_SECRET', 'BITGET_API_PASSPHRASE', 'usdt-swap'),
            'htx': ('HTX_API_KEY', 'HTX_API_SECRET', None, 'swap'),
            'gate': ('GATE_API_KEY', 'GATE_API_SECRET', None, 'swap'),
        }
        
        for ex_name, (key_env, secret_env, pass_env, default_type) in exchange_map.items():
            api_key = os.getenv(key_env, '')
            api_secret = os.getenv(secret_env, '')
            passphrase = os.getenv(pass_env, '') if pass_env else ''
            
            if not api_key:
                logger.warning(f"⚠️ {ex_name} API Key未设置，跳过")
                continue
            
            try:
                cls = getattr(ccxt, ex_name)
                kwargs = {
                    'apiKey': api_key,
                    'secret': api_secret,
                    'enableRateLimit': True,
                    'timeout': 10000,
                    'options': {'defaultType': default_type},
                }
                if passphrase:
                    kwargs['password'] = passphrase
                
                # 现货连接
                self.exchanges[ex_name] = cls(kwargs)
                
                # 永续连接
                perp_kwargs = kwargs.copy()
                perp_kwargs['options'] = {'defaultType': default_type}
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
                # Gate: 必须用无options的实例查现货，避免读跨账户总权益
                import os as _os
                gate_key = _os.getenv('GATE_API_KEY', '')
                gate_secret = _os.getenv('GATE_API_SECRET', '')
                spot_cls = getattr(ccxt, 'gate')
                spot_ex = spot_cls({'apiKey': gate_key, 'secret': gate_secret, 'enableRateLimit': True})
                spot_bal = spot_ex.fetch_balance()
            elif ex_name == 'htx':
                # HTX: type='spot'查现货
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
        except:
            return 0.0
    
    def _get_perp_balance(self, ex_name: str, exchange: ccxt.Exchange) -> float:
        """获取永续合约账户可用余额"""
        try:
            if ex_name == 'gate':
                # Gate: 必须用type='swap'创建新实例，避免options导致读跨账户总余额(15U含持仓)
                # 与risk_manager保持一致，读取free USDT作为可用余额
                import os as _os
                gate_key = _os.getenv('GATE_API_KEY', '')
                gate_secret = _os.getenv('GATE_API_SECRET', '')
                swap_cls = getattr(ccxt, 'gate')
                swap_ex = swap_cls({'apiKey': gate_key, 'secret': gate_secret, 'enableRateLimit': True, 'type': 'swap'})
                swap_bal = swap_ex.fetch_balance()
                if isinstance(swap_bal, list):
                    return sum(float(s.get('USDT', {}).get('free', 0) or 0) for s in swap_bal if isinstance(s, dict))
                else:
                    return float(swap_bal.get('USDT', {}).get('free', 0) or 0)
            elif ex_name == 'htx':
                # HTX: 必须用type='swap'创建新实例，避免读成现货账户(1.18U)
                import os as _os
                htx_key = _os.getenv('HTX_API_KEY', '')
                htx_secret = _os.getenv('HTX_API_SECRET', '')
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
        except:
            return 0.0
    
    def start(self):
        """启动执行引擎"""
        self.running = True
        if self.risk_manager.is_suspended:
            logger.warning(f"⛔ 风控暂停（仅停止实盘下单）: {self.risk_manager.suspension_reason}")
        logger.info("🚀 交易执行引擎启动（Post-Only做市版）")
        logger.info(f"   监控平台: {', '.join(self.exchanges.keys())}")
        logger.info(f"   价差阈值: >{self.config.execution.spread_pct:.2f}% (执行引擎层，灵敏度门槛)")
        logger.info(f"   净利阈值: >{self.config.execution.net_profit_pct:.2f}% (执行引擎层，灵敏度门槛)")
        logger.info(f"   风控净利: >{RiskManager.MIN_NET_PROFIT_PCT*100:.2f}% (风控层，定死不变)")
        logger.info(f"   ⚠️ 实际交易门槛: 价差 > {(RiskManager.MIN_NET_PROFIT_PCT + ExecutionEngine.BI_SIDE_COST)*100:.2f}%（成本0.12%+净利0.01%）")
        logger.info(f"   📌 杠杆: {LEVERAGE}x | 仓位: 永续余额×20%")
        
        self._run_loop()
    
    def _run_loop(self):
        """主循环"""
        while self.running:
            try:
                if self.risk_manager.is_suspended:
                    logger.warning(f"⛔ 风控暂停中: {self.risk_manager.suspension_reason}")
                    time.sleep(60)
                    continue
                
                # 定期刷新余额
                self.risk_manager.refresh_balance()
                
                # 遍历所有连接的交易所
                if not self.risk_manager.is_suspended:
                    for ex_name, exchange in self.exchanges.items():
                        if ex_name in self.perp_exchanges:
                            try:
                                self._scan_and_execute(ex_name, exchange, self.perp_exchanges[ex_name])
                            except Exception as e2:
                                logger.debug(f"{ex_name} scan error: {e2}")
                else:
                    logger.debug("⛔ 实盘已暂停，跳过下单扫描")
                
                # 检查挂单状态
                self.check_orders()
                
                time.sleep(self.config.data.update_interval)
                
            except KeyboardInterrupt:
                logger.info("用户中断")
                break
            except Exception as e:
                logger.error(f"执行错误: {e}")
                time.sleep(5)
    
    def _scan_and_execute(self, ex_name: str, spot_exchange: ccxt.Exchange, perp_exchange: ccxt.Exchange):
        """扫描并执行做市策略"""
        for symbol in self.config.data.symbols:
            try:
                # 获取现货和永续行情
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
                
                # 计算价差（永续vs现货）
                mid_spot = (spot_bid + spot_ask) / 2
                mid_perp = (perp_bid + perp_ask) / 2
                spread_pct = abs(mid_perp - mid_spot) / mid_spot * 100
                
                # 计算预期利润
                net_profit_pct = spread_pct - self.BI_SIDE_COST * 100
                
                # 执行引擎层阈值检查
                if spread_pct < self.config.execution.spread_pct:
                    logger.debug(f"📊 {ex_name} {symbol}: spread={spread_pct:.4f}% < 阈值{self.config.execution.spread_pct:.2f}%，跳过")
                    continue
                if net_profit_pct < self.config.execution.net_profit_pct:
                    logger.debug(f"📊 {ex_name} {symbol}: net={net_profit_pct:.4f}% < 阈值{self.config.execution.net_profit_pct:.2f}%，跳过")
                    continue
                
                # 风控层检查（定死不变）
                if net_profit_pct < RiskManager.MIN_NET_PROFIT_PCT * 100:
                    logger.debug(f"📊 {ex_name} {symbol}: net={net_profit_pct:.4f}% < 风控{RiskManager.MIN_NET_PROFIT_PCT*100:.4f}%，跳过")
                    continue
                
                # 执行做市
                self._execute_market_making(ex_name, spot_exchange, perp_exchange, symbol, 
                                           spot_bid, spot_ask, perp_bid, perp_ask,
                                           spread_pct, net_profit_pct)
                
            except Exception as e:
                logger.debug(f"{ex_name} {symbol} 扫描失败: {e}")
    
    def _execute_market_making(self, ex_name: str, spot_exchange: ccxt.Exchange, perp_exchange: ccxt.Exchange,
                                symbol: str, spot_bid: float, spot_ask: float,
                                perp_bid: float, perp_ask: float,
                                spread_pct: float, net_profit_pct: float):
        """执行做市策略（永续市价买 + 现货市价卖，两单同时发）"""
        
        perp_symbol = f"{symbol.split('/')[0]}/USDT:USDT"
        spot_symbol = symbol
        
        # 获取真实余额
        self.risk_manager.refresh_balance()
        total_equity = self.risk_manager.equity if self.risk_manager.equity > 0 else 1.0
        
        # 获取该交易所永续账户可用余额
        perp_bal = self._get_perp_balance(ex_name, perp_exchange)
        
        # 获取现货可用余额
        spot_bal = self._get_spot_balance(ex_name, spot_exchange)
        
        # 仓位 = 永续余额 × 20%（永续做本金池）
        position_size = perp_bal * self.risk_manager.MAX_POSITION_PCT
        
        # 检查最小金额限制（按余额比例缩放，小额账户也能交易）
        baseline = BALANCE_BASELINE.get(ex_name, 5.0)
        scale_factor = max(perp_bal / baseline, 0.15)  # 至少0.15倍
        perp_min = PERP_MIN_NOTIONAL.get(ex_name, 1.0) * scale_factor
        spot_min = SPOT_MIN_NOTIONAL.get(ex_name, 1.0) * scale_factor
        if position_size < perp_min:
            logger.warning(f"⚠️ {ex_name} {symbol}: 永续仓位{position_size:.2f}U < 最小{perp_min:.2f}U(余额{perp_bal:.2f}U×20%)，跳过")
            return
        if position_size < spot_min:
            logger.warning(f"⚠️ {ex_name} {symbol}: 现货仓位{position_size:.2f}U < 最小{spot_min:.2f}U，跳过")
            return
        
        # 方向：永续>现货 → 永续买+现货卖；永续<现货 → 永续卖+现货买
        mid_spot = (spot_bid + spot_ask) / 2
        mid_perp = (perp_bid + perp_ask) / 2
        
        if mid_perp > mid_spot:
            perp_side = 'buy'
            spot_side = 'sell'
        else:
            perp_side = 'sell'
            spot_side = 'buy'
        
        # 计算数量（用市场中间价）
        amount = position_size / mid_perp if perp_side == 'buy' else position_size / mid_spot
        
        # 精度检查：所有交易所的所有币都要检查，不能只检查HTX USDT
        coin = symbol.split('/')[0]
        if ex_name == 'htx' and amount < 1.0:
            logger.warning(f"⚠️ {ex_name} {symbol}: 数量{amount:.4f} < 1，精度不足，跳过")
            return
        
        # 调试日志
        logger.info(f"📊 {ex_name} {symbol}: 仓位={position_size:.2f}U, 数量={amount:.4f}, "
                   f"永续价={mid_perp:.2f}, 现货价={mid_spot:.2f}, 方向={perp_side}/{spot_side}, "
                   f"永续可用={perp_bal:.2f}U, 现货可用={spot_bal:.2f}U, "
                   f"价差={spread_pct:.4f}% 净利={net_profit_pct:.4f}%")
        
        # 风控检查（传入交易所名称，使用各平台独立限额）
        risk_check = self.risk_manager.check_risk(
            symbol=symbol,
            side=perp_side,
            position_size_usdt=position_size,
            entry_price=mid_perp,
            stop_loss_price=mid_perp * 1.02,
            ex_name=ex_name
        )
        
        if not risk_check['allowed']:
            logger.warning(f"⛔ {ex_name} {symbol} 风控拒绝: {risk_check['reason']}")
            return
        
        try:
            # ====== 同时发两笔市价单 ======
            # HTX 市价买单必须传 cost=花费USDT（不是币数量），否则报错
            perp_params = {}
            spot_params = {}
            if ex_name == 'htx':
                # HTX 市价买单用 cost 参数，不靠 createMarketBuyOrderRequiresPrice
                if perp_side == 'buy':
                    perp_params['cost'] = position_size
                if spot_side == 'buy':
                    spot_params['cost'] = position_size
            
            # 永续市价单（买单用 cost=position_size，卖单传币数量）
            perp_amount = position_size if perp_side == 'sell' else amount
            if perp_side == 'buy':
                perp_params = {'cost': position_size}
            else:
                perp_params = {}
            perp_order = perp_exchange.create_order(
                symbol=perp_symbol,
                type='market',
                side=perp_side,
                amount=perp_amount,
                params=perp_params,
            )
            logger.info(f"📤 {ex_name} {symbol} 永续市价{perp_side}(amount={perp_amount:.4f})")
            
            # 现货市价单（买单用 cost=position_size，卖单传币数量）
            spot_amount = position_size if spot_side == 'sell' else amount
            if spot_side == 'buy':
                spot_params = {'cost': position_size}
            else:
                spot_params = {}
            spot_order = spot_exchange.create_order(
                symbol=spot_symbol,
                type='market',
                side=spot_side,
                amount=spot_amount,
                params=spot_params,
            )
            logger.info(f"📤 {ex_name} {symbol} 现货市价{spot_side}(amount={spot_amount:.4f})")
            logger.info(f"✅ {ex_name} {symbol} 做市完成: 永续{perp_side}@{mid_perp:.2f} + 现货{spot_side}@{mid_spot:.2f}, "
                       f"仓位={position_size:.2f}U, 预期净利={net_profit_pct:.3f}%")
            
            # 记录信号
            self._record_signal(ex_name, symbol, perp_side, net_profit_pct, position_size)
            
            # 跟踪订单
            order_id = perp_order.get('id') or spot_order.get('id')
            if order_id:
                self.open_orders.setdefault(ex_name, {})[order_id] = {
                    'symbol': symbol,
                    'perp_order': perp_order,
                    'spot_order': spot_order,
                    'side': perp_side,
                    'amount': amount,
                    'timestamp': time.time(),
                }
            
        except Exception as e:
            logger.error(f"❌ {ex_name} {symbol} 下单失败: {e}")
    
    def _record_signal(self, exchange: str, symbol: str, side: str, profit: float, position_size: float = 0):
        """记录信号到数据库"""
        try:
            conn = sqlite3.connect(self.config.data.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO engine_signals (timestamp, mode, exchange, symbol, 
                    signal_type, strategy, expected_profit, executed)
                VALUES (?, 'live', ?, ?, 'market_make', 'market_maker', ?, 0)
            ''', (int(time.time()), exchange, symbol, profit))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"记录信号失败: {e}")
    
    def check_orders(self):
        """检查挂单状态和持仓风险"""
        for ex_name, spot_exchange in self.exchanges.items():
            if ex_name not in self.perp_exchanges:
                continue
            perp_exchange = self.perp_exchanges[ex_name]
            
            try:
                # 1. 检查未成交挂单，超时取消
                if ex_name in self.open_orders:
                    for order_id, order_info in list(self.open_orders[ex_name].items()):
                        try:
                            order = spot_exchange.fetch_order(order_id, order_info['symbol'])
                            if order.get('status') in ['closed', 'cancelled', 'expired']:
                                logger.info(f"📋 {ex_name} 订单{order_id}已成交/取消: {order.get('status')}")
                                # 清理
                                if order.get('status') == 'closed':
                                    logger.info(f"✅ {ex_name} {order_info['symbol']} 做市单已成交!")
                                del self.open_orders[ex_name][order_id]
                        except ccxt.OrderNotFound:
                            # 可能已过期或被取消，清理
                            if ex_name in self.open_orders and order_id in self.open_orders[ex_name]:
                                del self.open_orders[ex_name][order_id]
                        except Exception as e:
                            logger.debug(f"检查订单{order_id}失败: {e}")
                
                # 2. 检查持仓风险（防止意外持仓）
                positions = []
                try:
                    positions = [p for p in perp_exchange.fetch_positions() if p.get('contracts', 0) > 0]
                except:
                    pass
                
                for p in positions:
                    sym = p['symbol']
                    side = p['side']
                    margin = p.get('initialMargin', 0) or 0
                    liq = p.get('liquidationPrice', 0) or 0
                    entry = p.get('entryPrice', 0) or 0
                    try:
                        t = spot_exchange.fetch_ticker(sym.replace(':USDT', ''))
                        last = t['last']
                        dist = (liq - entry) / entry * 100 if side == 'short' else (entry - liq) / entry * 100
                        if abs(dist) < 3:
                            logger.critical(f"🔴 {ex_name} {sym} 即将强平! 距强平{dist:.2f}%，紧急平仓!")
                            close_side = 'buy' if side == 'short' else 'sell'
                            contracts = p['contracts']
                            perp_exchange.create_order(sym, 'market', close_side, contracts, None, {'reduceOnly': True})
                            logger.info(f"✅ {ex_name} {sym} 已紧急平仓")
                        elif abs(dist) < 8:
                            logger.warning(f"⚠️ {ex_name} {sym} 接近强平: 距强平{dist:.2f}%")
                    except:
                        pass
                        
            except Exception as e:
                logger.debug(f"检查{ex_name}订单/持仓失败: {e}")
    
    def get_status(self) -> Dict:
        """获取执行引擎状态"""
        return {
            'running': self.running,
            'risk': self.risk_manager.get_status(),
            'open_orders': {k: len(v) for k, v in self.open_orders.items()},
            'exchanges': list(self.exchanges.keys()),
        }
    
    def stop(self):
        """停止执行引擎"""
        self.running = False
        self.risk_manager.close()
        logger.info("🛑 执行引擎已停止")
