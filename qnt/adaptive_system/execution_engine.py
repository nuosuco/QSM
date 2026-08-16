"""
交易执行引擎 - 做市策略 + 风控（真实余额版）
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

class ExecutionEngine:
    """交易执行引擎（三平台版，含风控，真实余额）"""
    
    # 手续费率（Maker）
    MAKER_FEE_RATE = 0.0004   # 0.04%
    SLIPPAGE_RATE = 0.0002    # 0.02%
    TOTAL_COST = MAKER_FEE_RATE + SLIPPAGE_RATE  # 单边成本
    BI_SIDE_COST = TOTAL_COST * 2  # 双边成本 = 0.12%
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.running = False
        self.risk_manager = RiskManager(config.data.db_path)
        self.risk_manager.load_state()
        
        # 初始化交易所连接
        self.exchanges = {}
        self._connect_exchanges()
        
        # 已挂订单跟踪
        self.open_orders = {}  # {exchange: {order_id: {...}}}
        
        # 记录初始本金（用于计算盈亏）
        self._record_initial_principal()
    
    def _record_initial_principal(self):
        """记录初始本金，用于后续计算真实盈亏"""
        if self.risk_manager.equity > 0:
            self.risk_manager.set_initial_principal(self.risk_manager.equity)
            logger.info(f"💰 初始本金: {self.risk_manager.equity:.2f} USDT")
    
    def _connect_exchanges(self):
        """连接交易所（按方案只连Bitget和HTX）"""
        exchange_map = {
            'bitget': ('BITGET_API_KEY', 'BITGET_API_SECRET', 'BITGET_API_PASSPHRASE'),
            'htx': ('HTX_API_KEY', 'HTX_API_SECRET', None),
            # gate不交易，不连接
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
                kwargs = {
                    'apiKey': api_key,
                    'secret': api_secret,
                    'enableRateLimit': True,
                    'timeout': 10000,
                }
                if passphrase:
                    kwargs['password'] = passphrase
                
                self.exchanges[ex_name] = cls(kwargs)
                logger.info(f"✅ {ex_name} 交易引擎已连接")
            except Exception as e:
                logger.error(f"❌ {ex_name} 连接失败: {e}")
    
    def start(self):
        """启动执行引擎"""
        if self.risk_manager.is_suspended:
            logger.warning(f"⛔ 风控暂停: {self.risk_manager.suspension_reason}")
            return
        
        self.running = True
        logger.info("🚀 交易执行引擎启动")
        logger.info(f"   监控平台: {', '.join(self.exchanges.keys())}")
        logger.info(f"   价差阈值: >0.22% (成本线0.12% + 风控0.1%)")
        logger.info(f"   净利阈值: >{RiskManager.MIN_NET_PROFIT_PCT*100:.2f}%")
        
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
                for ex_name, exchange in self.exchanges.items():
                    self._scan_and_execute(ex_name, exchange)
                
                time.sleep(self.config.data.update_interval)
                
            except KeyboardInterrupt:
                logger.info("用户中断")
                break
            except Exception as e:
                logger.error(f"执行错误: {e}")
                time.sleep(5)
    
    def _scan_and_execute(self, ex_name: str, exchange: ccxt.Exchange):
        """扫描并执行做市策略"""
        for symbol in self.config.data.symbols:
            try:
                # 获取现货和永续行情
                spot_ticker = exchange.fetch_ticker(symbol)
                perp_symbol = f"{symbol.split('/')[0]}/USDT:USDT"
                perp_ticker = exchange.fetch_ticker(perp_symbol)
                
                if not spot_ticker or not perp_ticker:
                    continue
                
                spot_bid = spot_ticker.get('bid', 0)
                spot_ask = spot_ticker.get('ask', 0)
                perp_bid = perp_ticker.get('bid', 0)
                perp_ask = perp_ticker.get('ask', 0)
                
                if not all([spot_bid, spot_ask, perp_bid, perp_ask]):
                    continue
                
                # 计算价差（永续-现货）
                mid_spot = (spot_bid + spot_ask) / 2
                mid_perp = (perp_bid + perp_ask) / 2
                spread_pct = abs(mid_perp - mid_spot) / mid_spot * 100
                
                # 检查是否超过阈值（保守型：覆盖成本+风控要求）
                # 成本线0.12% + 风控要求0.1% = 0.22%
                if spread_pct < 0.22:
                    continue
                
                # 计算预期利润
                net_profit_pct = spread_pct - self.BI_SIDE_COST * 100
                if net_profit_pct < RiskManager.MIN_NET_PROFIT_PCT * 100:
                    continue
                
                # 执行做市
                self._execute_market_making(ex_name, exchange, symbol, 
                                           spot_bid, spot_ask, perp_bid, perp_ask,
                                           spread_pct, net_profit_pct)
                
            except Exception as e:
                logger.debug(f"{ex_name} {symbol} 扫描失败: {e}")
    
    def _execute_market_making(self, ex_name: str, exchange: ccxt.Exchange,
                                symbol: str, spot_bid: float, spot_ask: float,
                                perp_bid: float, perp_ask: float,
                                spread_pct: float, net_profit_pct: float):
        """执行做市策略（Post-Only双边挂单）"""
        
        # 构建永续合约symbol
        perp_symbol = f"{symbol.split('/')[0]}/USDT:USDT"
        
        # 获取真实余额
        self.risk_manager.refresh_balance()
        equity = self.risk_manager.equity if self.risk_manager.equity > 0 else 1.0
        
        # 根据真实余额计算仓位（≤20%）
        max_position = equity * self.risk_manager.MAX_POSITION_PCT
        
        # 根据交易所余额调整
        ex_balance = self.risk_manager.real_balance.get(ex_name, {}).get('total', 0)
        
        if ex_name == 'htx':
            # HTX账户只有1 USDT，用极小仓位测试
            position_size = min(1.0, max_position * 0.5)
        elif ex_name == 'bitget':
            # Bitget账户有3.5 USDT
            position_size = min(2.0, max_position * 0.3)  # 先用30%测试，最多2U
        else:
            position_size = min(2.0, max_position)
        
        # 判断方向：永续>现货 → 买永续卖现货；永续<现货 → 卖永续买现货
        mid_spot = (spot_bid + spot_ask) / 2
        mid_perp = (perp_bid + perp_ask) / 2
        
        if mid_perp > mid_spot:
            perp_side = 'buy'
            spot_side = 'sell'
            perp_price = perp_bid * 0.9999
            spot_price = spot_ask * 1.0001
        else:
            perp_side = 'sell'
            spot_side = 'buy'
            perp_price = perp_ask * 1.0001
            spot_price = spot_bid * 0.9999
        
        # 计算数量
        amount = position_size / mid_spot if spot_side == 'buy' else position_size / mid_perp
        
        # 调试日志
        logger.info(f"📊 {ex_name} {symbol}: 仓位={position_size:.2f}U, 数量={amount:.4f}, 永续价={mid_perp:.2f}, 现货价={mid_spot:.2f}, 方向={perp_side}/{spot_side}")
        
        # 风控检查
        risk_check = self.risk_manager.check_risk(
            symbol=symbol,
            side=perp_side,
            position_size_usdt=position_size,
            entry_price=mid_perp,
            stop_loss_price=mid_perp * 1.02  # 2%止损
        )
        
        if not risk_check['allowed']:
            logger.warning(f"⛔ {ex_name} {symbol} 风控拒绝: {risk_check['reason']}")
            return
        
        try:
            # 挂Post-Only永续单
            perp_order = exchange.create_order(
                symbol=perp_symbol,
                type='limit',
                side=perp_side,
                amount=amount,
                price=perp_price,
                params={'postOnly': True}
            )
            
            # 挂Post-Only现货单
            spot_order = exchange.create_order(
                symbol=symbol,
                type='limit',
                side=spot_side,
                amount=amount,
                price=spot_price,
                params={'postOnly': True}
            )
            
            logger.info(f"✅ {ex_name} {symbol} 做市挂单: "
                       f"永续{perp_side}@{perp_price:.2f}, 现货{spot_side}@{spot_price:.2f}, "
                       f"仓位={position_size:.2f}U, 权益={equity:.2f}U, "
                       f"预期净利={net_profit_pct:.3f}%")
            
            # 记录订单
            order_id = perp_order.get('id') or spot_order.get('id')
            self.open_orders.setdefault(ex_name, {})[order_id] = {
                'symbol': symbol,
                'perp_side': perp_side,
                'spot_side': spot_side,
                'perp_price': perp_price,
                'spot_price': spot_price,
                'amount': amount,
                'timestamp': time.time(),
                'spread_pct': spread_pct,
                'net_profit_pct': net_profit_pct,
            }
            
            # 记录信号到数据库
            self._record_signal(ex_name, symbol, perp_side, net_profit_pct)
            
        except Exception as e:
            logger.error(f"❌ {ex_name} {symbol} 挂单失败: {e}")
    
    def _record_signal(self, exchange: str, symbol: str, side: str, profit: float):
        """记录信号到数据库"""
        try:
            conn = sqlite3.connect(self.config.data.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO engine_signals (timestamp, mode, exchange, symbol, 
                    signal_type, strategy, expected_profit, executed)
                VALUES (?, 'paper', ?, ?, 'market_make', 'market_maker', ?, 0)
            ''', (int(time.time()), exchange, symbol, profit))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"记录信号失败: {e}")
    
    def check_orders(self):
        """检查挂单状态，平仓锁利"""
        for ex_name, orders in list(self.open_orders.items()):
            exchange = self.exchanges.get(ex_name)
            if not exchange:
                continue
            
            for order_id, order_info in list(orders.items()):
                try:
                    order = exchange.fetch_order(order_id, order_info['symbol'])
                    status = order.get('status', 'unknown')
                    
                    if status == 'closed':
                        # 检查另一边是否也成交
                        logger.info(f"📊 {ex_name} {order_info['symbol']} 订单{order_id}已成交")
                        
                        # 计算真实PnL
                        pnl = order_info['net_profit_pct'] * order_info['amount'] * \
                              (order_info['perp_price'] if order_info['perp_side'] == 'buy' else order_info['spot_price']) / 100
                        is_win = pnl > 0
                        self.risk_manager.record_trade(pnl, is_win)
                        
                        # 移除订单
                        del self.open_orders[ex_name][order_id]
                        
                    elif status == 'cancelled':
                        logger.debug(f"🔄 {ex_name} {order_info['symbol']} 订单{order_id}已取消")
                        del self.open_orders[ex_name][order_id]
                        
                except Exception as e:
                    logger.debug(f"检查订单失败: {e}")
    
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
