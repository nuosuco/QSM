"""
自适应策略引擎 - 主配置（三平台版）
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
    # 价差成本线（做市策略成本线约0.12%）
    spread_threshold: float = 0.12  # 0.12% - 成本线（价差大于此值才看）
    # 做市可盈利阈值（价差 > 成本线 + 安全边际）
    profitable_spread: float = 0.14  # 0.14% - 保守做市阈值
    # 深度异常阈值
    depth_imbalance_ratio: float = 3.0  # 买卖深度比
    # Z-Score异常检测（降低以便更容易发现价差机会）
    zscore_threshold: float = 1.5
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
            "description": "永续vs现货价差套利（需要>0.5%价差）",
            "weight": 0.3,
            "params": {"spread_threshold": 0.5, "min_profit": 0.3}
        },
        "market_maker": {
            "name": "做市策略",
            "description": "挂双边单赚取价差（需要>0.12%价差覆盖成本）",
            "weight": 0.7,
            "params": {"spread": 0.12, "order_size": 100}
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
class ExecutionConfig:
    """执行引擎配置（可调整）"""
    # 价差阈值：价差必须大于此值才考虑
    spread_pct: float = 0.05
    # 净利阈值：净利必须大于此值才交易
    net_profit_pct: float = 0.01

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
class ExchangeConfig:
    """交易所配置"""
    name: str = ""
    enabled: bool = True
    api_key: str = ""
    api_secret: str = ""
    passphrase: str = ""
    options: Dict = field(default_factory=lambda: {"defaultType": "spot"})

@dataclass
class SystemConfig:
    """系统总配置（三平台版）"""
    data: DataCollectionConfig = field(default_factory=DataCollectionConfig)
    pattern: PatternConfig = field(default_factory=PatternConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    
    # 三平台配置
    exchanges: Dict[str, ExchangeConfig] = field(default_factory=lambda: {
        "bitget": ExchangeConfig(name="bitget", enabled=True, passphrase="qntsomtop"),
        "htx": ExchangeConfig(name="htx", enabled=True),
        "gate": ExchangeConfig(name="gate", enabled=True),
    })
    
    # 执行引擎配置
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    
    def load_api_keys(self):
        """从环境变量加载API密钥"""
        exchange_map = {
            'bitget': ('BITGET_API_KEY', 'BITGET_API_SECRET', 'BITGET_API_PASSPHRASE'),
            'htx': ('HTX_API_KEY', 'HTX_API_SECRET', None),
            'gate': ('GATE_API_KEY', 'GATE_API_SECRET', None),
        }
        for ex_name, ex_cfg in self.exchanges.items():
            key, secret, passphrase = exchange_map.get(ex_name, (None, None, None))
            if key:
                ex_cfg.api_key = os.getenv(key, '')
            if secret:
                ex_cfg.api_secret = os.getenv(secret, '')
            if passphrase:
                ex_cfg.passphrase = os.getenv(passphrase, '')
    
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