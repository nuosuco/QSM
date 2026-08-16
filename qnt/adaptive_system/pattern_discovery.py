"""
模式发现引擎（三平台版）
从三个平台的历史数据中自动识别可盈利的市场模式
"""
import sqlite3
import numpy as np
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional

from .config import SystemConfig, PatternConfig
from .models import MarketDataPoint, SignalRecord, DiscoveredPattern

class PatternDiscovery:
    """模式发现引擎（三平台版）"""
    
    PLATFORMS = ['bitget', 'htx', 'gate']
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.pattern_config = config.pattern
        self.conn = sqlite3.connect(config.data.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # 按平台发现的策略
        self.discovered_strategies: Dict[str, Dict[str, DiscoveredPattern]] = {
            p: {} for p in self.PLATFORMS
        }
        self.strategy_performance: Dict[str, List[float]] = defaultdict(list)
    
    def analyze_all(self) -> List[DiscoveredPattern]:
        """分析所有平台的数据，发现新模式"""
        all_patterns = []
        
        for ex_name in self.PLATFORMS:
            ex_patterns = self._analyze_exchange(ex_name)
            all_patterns.extend(ex_patterns)
        
        # 评估现有策略
        self._evaluate_strategies()
        
        return all_patterns
    
    def _analyze_exchange(self, ex_name: str) -> List[DiscoveredPattern]:
        """分析单个平台的所有币种"""
        patterns = []
        for symbol in self.config.data.symbols:
            ex_patterns = self._analyze_symbol(ex_name, symbol)
            patterns.extend(ex_patterns)
        return patterns
    
    def _analyze_symbol(self, ex_name: str, symbol: str) -> List[DiscoveredPattern]:
        """分析单个平台单个币种的数据"""
        patterns = []
        
        # 1. 价差套利模式
        spread_pattern = self._detect_spread_arb_pattern(ex_name, symbol)
        if spread_pattern:
            patterns.append(spread_pattern)
        
        # 2. 均值回归模式
        mean_rev_pattern = self._detect_mean_reversion(ex_name, symbol)
        if mean_rev_pattern:
            patterns.append(mean_rev_pattern)
        
        # 3. 深度异常模式
        depth_pattern = self._detect_depth_anomaly(ex_name, symbol)
        if depth_pattern:
            patterns.append(depth_pattern)
        
        return patterns
    
    def _detect_spread_arb_pattern(self, ex_name: str, symbol: str) -> Optional[DiscoveredPattern]:
        """检测价差套利模式（按平台）"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT spread_pct, timestamp 
            FROM market_data 
            WHERE exchange = ? AND symbol = ?
            ORDER BY timestamp DESC 
            LIMIT 1000
        ''', (ex_name, symbol))
        
        rows = cursor.fetchall()
        if len(rows) < 100:
            return None
        
        spreads = np.array([r[0] for r in rows])
        
        mean_spread = np.mean(spreads)
        std_spread = np.std(spreads)
        
        threshold = mean_spread + self.pattern_config.zscore_threshold * std_spread
        high_spread_events = spreads[spreads > threshold]
        
        if len(high_spread_events) < 3:
            return None
        
        avg_profit = np.mean(high_spread_events) - 0.28
        if avg_profit <= 0:
            return None
        
        confidence = min(len(high_spread_events) / 10, 1.0)
        
        return DiscoveredPattern(
            exchange=ex_name,
            pattern_type="spread_arbitrage",
            symbol=symbol,
            confidence=float(confidence),
            profitability=float(avg_profit),
            parameters={
                "mean_spread": float(mean_spread),
                "std_spread": float(std_spread),
                "threshold": float(threshold),
                "event_count": int(len(high_spread_events))
            },
            status="active" if confidence > 0.5 else "experimental"
        )
    
    def _detect_mean_reversion(self, ex_name: str, symbol: str) -> Optional[DiscoveredPattern]:
        """检测均值回归模式（按平台）"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT spot_last, timestamp 
            FROM market_data 
            WHERE exchange = ? AND symbol = ?
            ORDER BY timestamp DESC 
            LIMIT 500
        ''', (ex_name, symbol))
        
        rows = cursor.fetchall()
        if len(rows) < 100:
            return None
        
        prices = np.array([r[0] for r in rows])
        window = 50
        if len(prices) < window * 2:
            return None
        
        revert_events = 0
        successful_reverts = 0
        
        for i in range(window, len(prices) - window):
            local_mean = np.mean(prices[i-window:i])
            local_std = np.std(prices[i-window:i])
            if local_std == 0:
                continue
            
            deviation = abs(prices[i] - local_mean) / local_std
            if deviation > 2.0:
                revert_events += 1
                if i + window < len(prices):
                    future_mean = np.mean(prices[i:i+window])
                    if abs(future_mean - local_mean) < local_std:
                        successful_reverts += 1
        
        if revert_events < 5:
            return None
        
        success_rate = successful_reverts / revert_events
        if success_rate < 0.6:
            return None
        
        return DiscoveredPattern(
            exchange=ex_name,
            pattern_type="mean_reversion",
            symbol=symbol,
            confidence=float(success_rate),
            profitability=float(success_rate * 0.5),
            parameters={
                "window": window,
                "revert_events": revert_events,
                "success_rate": float(success_rate)
            },
            status="active" if success_rate > 0.7 else "experimental"
        )
    
    def _detect_depth_anomaly(self, ex_name: str, symbol: str) -> Optional[DiscoveredPattern]:
        """检测深度异常模式（按平台）"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT depth_ratio, spread_pct, timestamp 
            FROM market_data 
            WHERE exchange = ? AND symbol = ?
            ORDER BY timestamp DESC 
            LIMIT 500
        ''', (ex_name, symbol))
        
        rows = cursor.fetchall()
        if len(rows) < 100:
            return None
        
        depths = np.array([r[0] for r in rows])
        spreads = np.array([r[1] for r in rows])
        
        imbalanced = (depths > self.pattern_config.depth_imbalance_ratio) | \
                     (depths < 1.0 / self.pattern_config.depth_imbalance_ratio)
        
        imbalance_events = np.sum(imbalanced)
        if imbalance_events < 3:
            return None
        
        abnormal_spreads = spreads[imbalanced]
        avg_spread = np.mean(np.abs(abnormal_spreads))
        if avg_spread < self.pattern_config.spread_threshold:
            return None
        
        return DiscoveredPattern(
            exchange=ex_name,
            pattern_type="depth_anomaly",
            symbol=symbol,
            confidence=float(imbalance_events / len(rows)),
            profitability=float(avg_spread - 0.28),
            parameters={
                "imbalance_events": int(imbalance_events),
                "avg_spread": float(avg_spread),
                "depth_threshold": self.pattern_config.depth_imbalance_ratio
            },
            status="experimental"
        )
    
    def _evaluate_strategies(self):
        """评估所有策略表现"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT strategy, 
                   COUNT(*) as total,
                   SUM(CASE WHEN executed = 1 AND actual_profit > 0 THEN 1 ELSE 0 END) as wins,
                   SUM(actual_profit) as total_profit
            FROM signals
            GROUP BY strategy
        ''')
        
        for strategy, total, wins, profit in cursor.fetchall():
            if total >= self.config.performance.min_samples:
                win_rate = wins / total
                avg_profit = profit / total if total > 0 else 0
                self.strategy_performance[strategy].append({
                    'win_rate': win_rate,
                    'avg_profit': avg_profit,
                    'total_trades': total
                })
    
    def get_best_strategy(self) -> Tuple[str, float]:
        """获取最佳策略"""
        best_strategy = "fat_finger_arb"
        best_score = 0.0
        
        for name, params in self.config.strategy.strategies.items():
            score = params.get('weight', 0) * params.get('params', {}).get('profitability', 0)
            if score > best_score:
                best_score = score
                best_strategy = name
        
        return best_strategy, best_score
    
    def close(self):
        if self.conn:
            self.conn.close()