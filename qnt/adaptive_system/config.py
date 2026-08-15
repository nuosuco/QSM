"""
自适应策略引擎 - 主配置
"""
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

@dataclass
class DataCollectionConfig:
    """数据收集配置"""
    # 监控的交易对
    symbols: List[str] = field(default_factory=lambda: ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"])
    # 更新频率(秒)
    update_interval: float = 1.0
    # 保留历史数据点数
    history_size: int = 10000
    # 数据库路径
    db_path: str = "/root/SOM/data/trading_system/adaptive.db"

@dataclass
class PatternConfig:
    """模式识别配置"""
    # 价差异常阈值
    spread_threshold: float = 0.5  # 0.5%
    # 深度异常阈值
    depth_imbalance_ratio: float = 3.0  # 买卖深度比
    # Z-Score异常检测
    zscore_threshold: float = 3.0
    # 成交量异常倍数
    volume_spike_multiplier: float = 5.0
    # 价格跳变阈值
    price_jump_threshold: float = 1.0  # 1%

@dataclass
class StrategyConfig:
    """策略配置"""
    # 当前活跃策略
    active_strategy: str = "fat_finger_arb"
    # 策略列表
    strategies: Dict[str, Dict] = field(default_factory=lambda: {
        "fat_finger_arb": {
            "name": "捡乌龙指套利",
            "description": "永续vs现货价差套利",
            "weight": 1.0,
            "params": {"spread_threshold": 0.5, "min_profit": 0.3}
        },
        "market_maker": {
            "name": "做市策略",
            "description": "挂双边单赚取价差",
            "weight": 0.0,
            "params": {"spread": 0.1, "order_size": 100}
        },
        "momentum": {
            "name": "动量跟踪",
            "description": "跟随价格趋势",
            "weight": 0.0,
            "params": {"lookback": 20, "threshold": 2.0}
        },
        "mean_reversion": {
            "name": "均值回归",
            "description": "价格回归均值",
            "weight": 0.0,
            "params": {"window": 50, "std_threshold": 2.0}
        }
    })

@dataclass
class PerformanceConfig:
    """性能追踪配置"""
    # 滚动窗口大小
    window_size: int = 100
    # 策略切换阈值
    switch_threshold: float = 0.1
    # 最小样本数
    min_samples: int = 10
    # 回撤保护
    max_drawdown: float = 10.0

@dataclass
class SystemConfig:
    """系统总配置"""
    data: DataCollectionConfig = field(default_factory=DataCollectionConfig)
    pattern: PatternConfig = field(default_factory=PatternConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    def save(self, path: str = None):
        if path is None:
            path = os.path.expanduser("~/.adaptive_system_config.json")
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2, default=lambda o: o.__dict__)
    
    @classmethod
    def load(cls, path: str = None) -> 'SystemConfig':
        if path is None:
            path = os.path.expanduser("~/.adaptive_system_config.json")
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            config = cls()
            config.__dict__.update(data)
            return config
        return cls()
