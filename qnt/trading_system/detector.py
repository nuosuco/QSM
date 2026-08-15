"""
记忆承载·碧树西风交易系统 - 乌龙指检测引擎
基于Z-Score/MAD统计异常检测、深度簿异常检测、跨交易所价差监控
"""
import numpy as np
from collections import deque
from typing import List, Optional, Tuple
from datetime import datetime

from .models import (FatFingerSignal, OrderBookEntry, OrderBook, 
                     SignalType, OrderSide)
from .config import DetectionConfig


class ZScoreDetector:
    """基于Z-Score的异常价格检测"""
    
    def __init__(self, threshold: float = 3.0, window: int = 200):
        self.threshold = threshold
        self.window = window
        self.prices: deque = deque(maxlen=window)
    
    def detect(self, price: float) -> Optional[float]:
        """返回Z-Score，异常时超过threshold"""
        if len(self.prices) < 30:
            self.prices.append(price)
            return None
        
        mean = np.mean(list(self.prices))
        std = np.std(list(self.prices))
        
        if std == 0:
            return None
        
        z_score = (price - mean) / std
        self.prices.append(price)
        return z_score


class MADDetector:
    """基于MAD的异常价格检测（更鲁棒）"""
    
    def __init__(self, threshold: float = 3.5, window: int = 200):
        self.threshold = threshold
        self.window = window
        self.prices: deque = deque(maxlen=window)
    
    def detect(self, price: float) -> Optional[float]:
        """返回Modified Z-Score"""
        if len(self.prices) < 50:
            self.prices.append(price)
            return None
        
        median = np.median(list(self.prices))
        mad = np.median(np.abs(np.array(list(self.prices)) - median))
        
        if mad == 0:
            return None
        
        modified_z = 0.6745 * (price - median) / mad
        self.prices.append(price)
        return modified_z


class Detector:
    """乌龙指检测引擎"""
    
    def __init__(self, config: DetectionConfig):
        self.config = config
        self.zscore_detectors: Dict[str, ZScoreDetector] = {}
        self.mad_detectors: Dict[str, MADDetector] = {}
        self.price_history: Dict[str, deque] = {}
        self.cooldowns: Dict[str, datetime] = {}
        self.trade_timestamps: deque = deque()
    
    def _get_price_history(self, symbol: str) -> deque:
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=self.config.stat_window_size)
        return self.price_history[symbol]
    
    def detect_single_exchange(
        self, 
        exchange: str,
        symbol: str,
        orderbook: OrderBook,
        recent_trades: List[float]
    ) -> List[FatFingerSignal]:
        """单交易所检测 - 核心逻辑"""
        signals = []
        mid_price = orderbook.mid_price
        
        if mid_price <= 0:
            return signals
        
        # 使用MAD检测异常价格
        history = self._get_price_history(symbol)
        for price in recent_trades[-20:]:
            history.append(price)
        
        if len(history) < 50:
            return signals
        
        # MAD检测
        median = np.median(list(history))
        mad = np.median(np.abs(np.array(list(history)) - median))
        
        if mad > 0:
            # 检查买盘异常（价格异常低 → 买入机会）
            if orderbook.bids:
                bid_price = orderbook.bids[0].price
                bid_z = 0.6745 * (bid_price - median) / mad
                if bid_z < -self.config.mad_threshold:
                    deviation = (median - bid_price) / median * 100
                    if deviation > self.config.price_deviation_pct:
                        signal = self._create_signal(
                            SignalType.SINGLE_EXCHANGE,
                            exchange, symbol,
                            "buy", bid_price, median, deviation
                        )
                        if signal:
                            signals.append(signal)
                
                # 检查卖盘异常（价格异常高 → 卖出机会）
                if orderbook.asks:
                    ask_price = orderbook.asks[0].price
                    ask_z = 0.6745 * (ask_price - median) / mad
                    if ask_z > self.config.mad_threshold:
                        deviation = (ask_price - median) / median * 100
                        if deviation > self.config.price_deviation_pct:
                            signal = self._create_signal(
                                SignalType.SINGLE_EXCHANGE,
                                exchange, symbol,
                                "sell", ask_price, median, deviation
                            )
                            if signal:
                                signals.append(signal)
        
        # 检查深度簿价格跳跃
        jump_signals = self._detect_price_jumps(exchange, symbol, orderbook)
        signals.extend(jump_signals)
        
        return signals
    
    def _detect_price_jumps(
        self, 
        exchange: str, 
        symbol: str, 
        ob: OrderBook
    ) -> List[FatFingerSignal]:
        """检测深度簿中的价格跳跃"""
        signals = []
        
        # 检查买盘跳跃
        for i in range(1, min(len(ob.bids), 20)):
            prev_price = ob.bids[i-1].price
            curr_price = ob.bids[i].price
            if prev_price > 0:
                gap = (prev_price - curr_price) / prev_price
                if gap > self.config.price_deviation_pct / 100 * 0.5:
                    signal = self._create_signal(
                        SignalType.DEPTH_ANOMALY,
                        exchange, symbol,
                        "buy", curr_price, prev_price,
                        gap * 100
                    )
                    if signal:
                        signals.append(signal)
        
        # 检查卖盘跳跃
        for i in range(1, min(len(ob.asks), 20)):
            prev_price = ob.asks[i-1].price
            curr_price = ob.asks[i].price
            if prev_price > 0:
                gap = (curr_price - prev_price) / prev_price
                if gap > self.config.price_deviation_pct / 100 * 0.5:
                    signal = self._create_signal(
                        SignalType.DEPTH_ANOMALY,
                        exchange, symbol,
                        "sell", curr_price, prev_price,
                        gap * 100
                    )
                    if signal:
                        signals.append(signal)
        
        return signals
    
    def _create_signal(
        self,
        signal_type: SignalType,
        exchange: str,
        symbol: str,
        direction: str,
        price: float,
        fair_price: float,
        deviation_pct: float
    ) -> Optional[FatFingerSignal]:
        """创建信号，检查冷却期和流动性"""
        key = f"{exchange}:{symbol}"
        
        # 冷却期检查
        now = datetime.utcnow()
        if key in self.cooldowns:
            elapsed = (now - self.cooldowns[key]).total_seconds()
            if elapsed < self.config.cooldown_seconds:
                return None
        
        # 计算信号强度
        strength = min(deviation_pct / (self.config.price_deviation_pct * 2), 1.0)
        
        # 检查流动性
        target_side = OrderSide.BUY if direction == "buy" else OrderSide.SELL
        depth_usd = self._check_depth(exchange, symbol, target_side)
        if depth_usd < self.config.min_depth_usdt:
            return None
        
        # 检查最低信号强度
        if strength < self.config.min_signal_strength:
            return None
        
        signal = FatFingerSignal(
            signal_type=signal_type,
            symbol=symbol,
            exchange=exchange,
            price=price,
            fair_price=fair_price,
            deviation_pct=deviation_pct,
            signal_strength=strength,
            timestamp=now.timestamp(),
            depth_available=depth_usd,
            target_side=target_side,
        )
        
        self.cooldowns[key] = now
        return signal
    
    def _check_depth(
        self, exchange: str, symbol: str, side: OrderSide
    ) -> float:
        """检查深度（简化版）"""
        if "BTC" in symbol:
            return 10000.0
        elif "ETH" in symbol:
            return 5000.0
        return 1000.0
    
    def should_filter(self, signal: FatFingerSignal) -> Tuple[bool, str]:
        """信号过滤器"""
        now = datetime.utcnow()
        self.trade_timestamps = deque(
            t for t in self.trade_timestamps 
            if (now.timestamp() - t) < 60
        )
        
        if len(self.trade_timestamps) >= self.config.max_signals_per_minute:
            return False, "Rate limit exceeded"
        
        return True, "OK"
