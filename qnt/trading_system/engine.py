"""
记忆承载·碧树西风交易系统 - 核心引擎
整合检测、风控、资金管理、订单执行
"""
import time
import threading
from typing import List, Optional
from datetime import datetime

from .config import SystemConfig
from .detector import Detector
from .exchange_adapter import ExchangeAdapter
from .risk_manager import RiskManager, TradeRecord
from .capital_manager import CapitalManager
from .models import FatFingerSignal, OrderSide


class TradingEngine:
    """交易引擎"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.detector = Detector(config.detection)
        self.risk_manager = RiskManager()
        self.capital_manager = CapitalManager(config.capital.initial_capital)
        
        # 初始化交易所适配器
        self.exchanges: Dict[str, ExchangeAdapter] = {}
        for name, ex_config in config.exchanges.items():
            adapter = ExchangeAdapter(ex_config)
            if adapter.exchange:
                self.exchanges[name] = adapter
        
        self.running = False
        self.trade_count = 0
        self.last_scan_time = 0
    
    def start(self, mode: str = "backtest"):
        """启动引擎"""
        self.running = True
        print(f"🚀 交易引擎启动 (mode={mode})")
        
        if mode == "live":
            self._run_live()
        elif mode == "backtest":
            self._run_backtest()
    
    def _run_live(self):
        """实盘运行"""
        print(f"📊 实盘模式 - 监控交易对: {', '.join(self.config.symbols)}")
        
        while self.running:
            try:
                current_time = time.time()
                
                # 频率限制
                if current_time - self.last_scan_time < 5:
                    time.sleep(1)
                    continue
                
                self.last_scan_time = current_time
                
                # 扫描每个交易对
                for symbol in self.config.symbols:
                    self._scan_symbol(symbol)
                
                # 检查风控
                self._check_risk()
                
            except KeyboardInterrupt:
                print("\n🛑 用户中断")
                break
            except Exception as e:
                print(f"⚠️ 运行时错误: {e}")
                time.sleep(5)
        
        self.stop()
    
    def _scan_symbol(self, symbol: str):
        """扫描单个交易对"""
        # 获取现货和永续合约
        spot_symbol = f"{symbol.replace('/USDT', '')}/USDT"
        perp_symbol = f"{symbol.replace('/', '/USDT:')} (永续)"
        
        try:
            ob = self.exchanges['bitget'].fetch_orderbook(spot_symbol)
            if not ob:
                return
            
            # 检测信号
            signals = self.detector.detect_single_exchange(
                'bitget', symbol, ob, []
            )
            
            for signal in signals:
                self._process_signal(signal)
                
        except Exception as e:
            pass
    
    def _process_signal(self, signal: FatFingerSignal):
        """处理信号"""
        # 风控检查
        can_trade, reason = self.risk_manager.check_before_trade(
            signal.depth_available,
            self.config.capital.initial_capital
        )
        
        if not can_trade:
            print(f"❌ 信号过滤: {reason}")
            return
        
        # 执行交易
        self._execute_trade(signal)
    
    def _execute_trade(self, signal: FatFingerSignal):
        """执行交易 - 永续开多 + 现货卖单对冲"""
        print(f"🎯 执行交易: {signal.symbol} 偏离{signal.deviation_pct:.2f}%")
        
        try:
            # 获取当前价格
            ticker = self.exchanges['bitget'].fetch_ticker(signal.symbol.replace(':', ''))
            if not ticker:
                return
            
            # 计算仓位（不超过最大仓位限制）
            max_position = self.capital_manager.get_position_size()
            position_size = min(signal.depth_available * 0.1, max_position)
            
            if position_size < 10:  # 最小10 USDT
                print(f"⚠️ 仓位太小: {position_size} USDT")
                return
            
            # 永续开多
            perp_symbol = f"{signal.symbol.split('/')[0]}/USDT:USDT"
            self.exchanges['bitget'].create_post_only_order(
                perp_symbol, OrderSide.BUY, position_size, signal.price * 0.99
            )
            
            # 现货卖单
            self.exchanges['bitget'].create_post_only_order(
                signal.symbol, OrderSide.SELL, position_size / signal.price, signal.price
            )
            
            self.trade_count += 1
            print(f"✅ 订单已提交: {self.trade_count}笔")
            
        except Exception as e:
            print(f"❌ 执行失败: {e}")
    
    def _check_risk(self):
        """检查风控状态"""
        status = self.risk_manager.get_status()
        if not status['is_trading_allowed']:
            print(f"⛔ 风控触发! {status}")
    
    def stop(self):
        """停止引擎"""
        self.running = False
        for adapter in self.exchanges.values():
            adapter.close()
        print("🛑 引擎已停止")
    
    def get_status(self) -> dict:
        """获取系统状态"""
        return {
            "trades": self.trade_count,
            "risk": self.risk_manager.get_status(),
            "capital": self.capital_manager.get_status(),
        }
