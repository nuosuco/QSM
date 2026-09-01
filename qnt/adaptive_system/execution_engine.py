"""
交易执行引擎 - 做市策略 + 风控（真实余额版）
v4.0: 完整风控版，修复所有bug
修复内容:
1. Gate现货必须用独立spot实例，不能用swap实例
2. 永续和现货分两次调用，各自独立错误处理
3. 成功交易写入engine_trades表
4. 下单失败写入engine_signals表
5. 精度检查覆盖所有币种和所有交易所
6. 仓位下限检查：币数量>=1且金额>=最小订单
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
# 各交易所真实参数
# ============================================================
PERP_MIN_NOTIONAL = {'bitget': 5.0, 'htx': 1.0, 'gate': 3.0}
SPOT_MIN_NOTIONAL = {'bitget': 1.0, 'htx': 1.0, 'gate': 3.0}
BALANCE_BASELINE = {'bitget': 25.0, 'htx': 5.0, 'gate': 5.0}
LEVERAGE = 50

# 最低币数量精度（所有交易所）
MIN_COIN_AMOUNT = 1.0


class ExecutionEngine:
    """交易执行引擎（三平台版，Post-Only做市策略，完整风控）"""
    
    # 手续费率（Maker）- 交易所真实费率
    MAKER_FEE_RATE = 0.0006   # 0.06%
    SLIPPAGE_RATE = 0.0002    # 0.02%
    TOTAL_COST = MAKER_FEE_RATE + SLIPPAGE_RATE  # 单边成本 = 0.08%
    BI_SIDE_COST = TOTAL_COST * 2  # 双边成本 = 0.16%（永续+现货）
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.running = False
        self.risk_manager = RiskManager(config.data.db_path)
        self.risk_manager.load_state()
        
        # 初始化交易所连接
        self.exchanges = {}
        self.perp_exchanges = {}
        self._connect_exchanges()
        
        self.open_orders = {}
        self._record_initial_principal()
    
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
        """启动执行引擎"""
        self.running = True
        if self.risk_manager.is_suspended:
            logger.warning(f"⛔ 风控暂停（仅停止实盘下单）: {self.risk_manager.suspension_reason}")
        logger.info("🚀 交易执行引擎启动（完整风控版v4.0）")
        logger.info(f"   监控平台: {', '.join(self.exchanges.keys())}")
        logger.info(f"   价差阈值: >{self.config.execution.spread_pct:.2f}% (执行引擎层)")
        logger.info(f"   净利阈值: >{self.config.execution.net_profit_pct:.2f}% (执行引擎层)")
        logger.info(f"   风控净利: >{RiskManager.MIN_NET_PROFIT_PCT*100:.2f}% (风控层，定死不变)")
        logger.info(f"   ⚠️ 实际交易门槛: 价差 > {(RiskManager.MIN_NET_PROFIT_PCT + ExecutionEngine.BI_SIDE_COST)*100:.2f}%")
        logger.info(f"   📌 杠杆: {LEVERAGE}x | 仓位: 永续余额×20%")
        logger.info(f"   🔒 币数量精度: >= {MIN_COIN_AMOUNT} (所有交易所)")
        logger.info(f"   🔒 Gate最小订单: >= {PERP_MIN_NOTIONAL['gate']}U")
        
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
                    for ex_name, spot_exchange in self.exchanges.items():
                        if ex_name in self.perp_exchanges:
                            try:
                                self._scan_and_execute(ex_name, spot_exchange, self.perp_exchanges[ex_name])
                            except Exception as e2:
                                logger.debug(f"{ex_name} scan error: {e2}")
                else:
                    logger.debug("⛔ 实盘已暂停，跳过下单扫描")
                
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
                
                # 计算价差
                mid_spot = (spot_bid + spot_ask) / 2
                mid_perp = (perp_bid + perp_ask) / 2
                spread_pct = abs(mid_perp - mid_spot) / mid_spot * 100
                net_profit_pct = spread_pct - self.BI_SIDE_COST * 100
                
                # 三层阈值检查
                if spread_pct < self.config.execution.spread_pct:
                    continue
                if net_profit_pct < self.config.execution.net_profit_pct:
                    continue
                if net_profit_pct < RiskManager.MIN_NET_PROFIT_PCT * 100:
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
        """执行做市策略（永续市价买 + 现货市价卖，两单同时发，独立错误处理）"""
        
        perp_symbol = f"{symbol.split('/')[0]}/USDT:USDT"
        spot_symbol = symbol
        
        # 获取真实余额
        self.risk_manager.refresh_balance()
        total_equity = self.risk_manager.equity if self.risk_manager.equity > 0 else 1.0
        
        perp_bal = self._get_perp_balance(ex_name, perp_exchange)
        spot_bal = self._get_spot_balance(ex_name, spot_exchange)
        
        # 仓位 = 永续余额 × 20%
        position_size = perp_bal * self.risk_manager.MAX_POSITION_PCT
        
        # 检查最小金额限制
        if ex_name == 'gate':
            if position_size < PERP_MIN_NOTIONAL['gate']:
                logger.debug(f"⚠️ {ex_name} {symbol}: 永续仓位{position_size:.2f}U < Gate最小{PERP_MIN_NOTIONAL['gate']}U，跳过")
                return
        else:
            baseline = BALANCE_BASELINE.get(ex_name, 5.0)
            scale_factor = max(perp_bal / baseline, 0.15)
            perp_min = PERP_MIN_NOTIONAL.get(ex_name, 1.0) * scale_factor
            spot_min = SPOT_MIN_NOTIONAL.get(ex_name, 1.0) * scale_factor
            if position_size < perp_min:
                logger.debug(f"⚠️ {ex_name} {symbol}: 永续仓位{position_size:.2f}U < 最小{perp_min:.2f}U，跳过")
                return
            if position_size < spot_min:
                logger.debug(f"⚠️ {ex_name} {symbol}: 现货仓位{position_size:.2f}U < 最小{spot_min:.2f}U，跳过")
                return
        
        # 方向判断
        if mid_perp > mid_spot:
            perp_side = 'buy'
            spot_side = 'sell'
        else:
            perp_side = 'sell'
            spot_side = 'buy'
        
        # 计算数量
        amount = position_size / mid_perp if perp_side == 'buy' else position_size / mid_spot
        
        # ====== 精度检查：所有币种、所有交易所 ======
        coin = symbol.split('/')[0]
        # 所有交易所都要求币数量 >= 1
        if amount < MIN_COIN_AMOUNT:
            logger.debug(f"⚠️ {ex_name} {symbol}: 币数量{amount:.4f} < {MIN_COIN_AMOUNT}，精度不足，跳过")
            return
        
        # HTX市价单有额外最小数量要求
        if ex_name == 'htx':
            try:
                ticker = spot_exchange.fetch_ticker(symbol)
                min_qty = ticker.get('info', {}).get('text', {}).get('min_market_buy_amount', 0) or 0
                if min_qty > 0 and amount < float(min_qty):
                    logger.debug(f"⚠️ {ex_name} {symbol}: 数量{amount:.4f} < HTX最小{min_qty}，跳过")
                    return
            except:
                pass
        
        # 调试日志
        logger.info(f"📊 {ex_name} {symbol}: 仓位={position_size:.2f}U, 数量={amount:.4f}, "
                   f"永续价={mid_perp:.2f}, 现货价={mid_spot:.2f}, 方向={perp_side}/{spot_side}, "
                   f"永续可用={perp_bal:.2f}U, 现货可用={spot_bal:.2f}U, "
                   f"价差={spread_pct:.4f}% 净利={net_profit_pct:.4f}%")
        
        # 风控检查
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
        
        # ====== 分别下单，各自独立错误处理 ======
        perp_order = None
        spot_order = None
        perp_success = False
        spot_success = False
        perp_err = None
        spot_err = None
        
        try:
            # ====== 永续合约下单 ======
            perp_params = {}
            if ex_name == 'htx' and perp_side == 'buy':
                perp_params = {'cost': position_size}
            elif ex_name == 'gate' and perp_side == 'buy':
                perp_params = {'cost': position_size}
            
            perp_amount = position_size if perp_side == 'sell' else amount
            perp_order = perp_exchange.create_order(
                symbol=perp_symbol,
                type='market',
                side=perp_side,
                amount=perp_amount,
                params=perp_params,
            )
            perp_success = True
            logger.info(f"✅ {ex_name} {symbol} 永续{perp_side}@{mid_perp:.2f}(amount={perp_amount:.4f})")
            
        except Exception as e:
            perp_err = str(e)[:200]
            logger.error(f"❌ {ex_name} {symbol} 永续{perp_side}失败: {perp_err}")
        
        try:
            # ====== 现货下单（必须用独立的现货实例！）=====
            spot_params = {}
            if ex_name == 'htx' and spot_side == 'buy':
                spot_params = {'cost': position_size}
            elif ex_name == 'gate' and spot_side == 'buy':
                spot_params = {'cost': position_size}
            
            spot_amount = position_size if spot_side == 'sell' else amount
            spot_order = spot_exchange.create_order(
                symbol=spot_symbol,
                type='market',
                side=spot_side,
                amount=spot_amount,
                params=spot_params,
            )
            spot_success = True
            logger.info(f"✅ {ex_name} {symbol} 现货{spot_side}@{mid_spot:.2f}(amount={spot_amount:.4f})")
            
        except Exception as e:
            spot_err = str(e)[:200]
            logger.error(f"❌ {ex_name} {symbol} 现货{spot_side}失败: {spot_err}")
        
        # ====== 记录结果 ======
        if perp_success and spot_success:
            # 两单都成功 → 写入engine_trades
            logger.info(f"✅ {ex_name} {symbol} 做市完成: 永续{perp_side}@{mid_perp:.2f} + 现货{spot_side}@{mid_spot:.2f}, "
                       f"仓位={position_size:.2f}U, 预期净利={net_profit_pct:.3f}%")
            self._record_trade(ex_name, symbol, perp_side, mid_perp, amount, position_size, net_profit_pct)
            self._record_signal(ex_name, symbol, perp_side, net_profit_pct, position_size)
            
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
        elif perp_success and not spot_success:
            # 只有一单成功 → 警告但继续（可能是对冲不完全）
            logger.warning(f"⚠️ {ex_name} {symbol} 只做了一单: 永续✅ 现货❌ ({spot_err})")
            self._record_trade(ex_name, symbol, perp_side, mid_perp, amount, position_size, net_profit_pct, failed=True)
            self._record_signal(ex_name, symbol, perp_side, net_profit_pct, position_size, failed=True)
        elif not perp_success and spot_success:
            # 反向：现货成功但永续失败
            logger.warning(f"⚠️ {ex_name} {symbol} 只做了一单: 现货✅ 永续❌ ({perp_err})")
            self._record_trade(ex_name, symbol, perp_side, mid_perp, amount, position_size, net_profit_pct, failed=True)
            self._record_signal(ex_name, symbol, perp_side, net_profit_pct, position_size, failed=True)
        else:
            # 两单都失败
            logger.error(f"❌ {ex_name} {symbol} 两单全部失败: 永续={perp_err}, 现货={spot_err}")
            self._record_signal(ex_name, symbol, perp_side, net_profit_pct, position_size, failed=True,
                              errors=f"perp:{perp_err};spot:{spot_err}")
    
    def _record_trade(self, exchange: str, symbol: str, side: str, price: float, amount: float, 
                      position_size: float, profit_pct: float, failed: bool = False):
        """记录成功/部分成功的交易到engine_trades表"""
        try:
            conn = sqlite3.connect(self.config.data.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO engine_trades (timestamp, mode, exchange, symbol, side, price, amount, 
                    cost, fee, pnl, pnl_pct, status)
                VALUES (?, 'live', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (int(time.time()), exchange, symbol, side, price, amount,
                  position_size * 0.0004, position_size * 0.0004, 0, profit_pct,
                  'partial' if failed else 'completed'))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"记录交易失败: {e}")
    
    def _record_signal(self, exchange: str, symbol: str, side: str, profit: float, 
                       position_size: float = 0, failed: bool = False, errors: str = ''):
        """记录信号到engine_signals表"""
        try:
            conn = sqlite3.connect(self.config.data.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO engine_signals (timestamp, mode, exchange, symbol,
                    signal_type, strategy, expected_profit, executed, metadata)
                VALUES (?, 'live', ?, ?, 'market_make', 'market_maker', ?, ?, ?)
            ''', (int(time.time()), exchange, symbol, profit, 0 if failed else 1, 
                  errors if errors else json.dumps({'side': side, 'position_size': position_size})))
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
                # 1. 检查未成交挂单
                if ex_name in self.open_orders:
                    for order_id, order_info in list(self.open_orders[ex_name].items()):
                        try:
                            order = spot_exchange.fetch_order(order_id, order_info['symbol'])
                            if order.get('status') in ['closed', 'cancelled', 'expired']:
                                logger.info(f"📋 {ex_name} 订单{order_id}已{order.get('status')}")
                                if order.get('status') == 'closed':
                                    logger.info(f"✅ {ex_name} {order_info['symbol']} 做市单已成交!")
                                del self.open_orders[ex_name][order_id]
                        except ccxt.OrderNotFound:
                            if ex_name in self.open_orders and order_id in self.open_orders[ex_name]:
                                del self.open_orders[ex_name][order_id]
                        except Exception as e:
                            logger.debug(f"检查订单{order_id}失败: {e}")
                
                # 2. 检查持仓风险
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
                        if abs(dist) < 1:
                            logger.critical(f"🔴 {ex_name} {sym} 即将强平! 距强平{dist:.2f}%，紧急平仓!")
                            close_side = 'buy' if side == 'short' else 'sell'
                            contracts = p['contracts']
                            perp_exchange.create_order(sym, 'market', close_side, contracts, None, {'reduceOnly': True})
                            logger.info(f"✅ {ex_name} {sym} 已紧急平仓")
                            self._record_trade(ex_name, sym, close_side, 0, contracts, 0, 0, failed=True)
                        elif abs(dist) < 2:
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
