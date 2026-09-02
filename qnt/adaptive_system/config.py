"""
自适应策略引擎 - 主配置（双模式回测版）
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
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
        "DOGE/USDT", "AVAX/USDT", "LINK/USDT", "PEPE/USDT", "WIF/USDT",
        "SUI/USDT", "SEI/USDT", "ARB/USDT", "OP/USDT", "DOT/USDT",
        "ATOM/USDT", "ONDO/USDT", "FET/USDT", "INJ/USDT", "TIA/USDT"
    ])
    # 更新频率(秒)
    update_interval: float = 1.0
    # 保留历史数据点数
    history_size: int = 10000
    # 数据库路径
    db_path: str = "/root/SOM/data/trading_system/adaptive.db"

@dataclass
class PatternConfig:
    """模式识别配置（观察用，不影响实盘交易）"""
    spread_threshold: float = 0.08
    profitable_spread: float = 0.10
    depth_imbalance_ratio: float = 3.0
    zscore_threshold: float = 1.5
    volume_spike_multiplier: float = 5.0
    price_jump_threshold: float = 1.0

@dataclass
class StrategyConfig:
    """策略配置"""
    active_strategy: str = "fat_finger_arb"
    strategies: Dict[str, Dict] = field(default_factory=lambda: {
        "fat_finger_arb": {
            "name": "捡乌龙指套利",
            "description": "永续vs现货价差套利",
            "weight": 0.3,
            "params": {"spread_threshold": 0.5, "min_profit": 0.3}
        },
        "market_maker": {
            "name": "做市策略",
            "description": "挂双边单赚取价差",
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
    """执行引擎配置（可调整）
    
    用户要求：净利=0.01%，成本=0.16%，价差=0.17%
    """
    spread_pct: float = 0.17
    net_profit_pct: float = 0.01
    fill_rate: float = 0.6  # 成交概率

@dataclass
class BacktestConfig:
    """双模式回测配置"""
    # 模式一：我们的真实成交回测
    enable_my_trades_backtest: bool = True
    # 模式二：平台公开市场成交回测
    enable_market_backtest: bool = True
    # 市场成交采集频率（小时）
    market_trade_collection_interval: int = 1
    # 每个币种采集数量
    market_trades_per_symbol: int = 1000
    # 数据对比阈值
    min_market_trades_for_comparison: int = 10000

@dataclass
class LiveTradingConfig:
    """实盘自动开关配置"""
    enabled: bool = False
    min_equity: float = 25.0
    paper_window_hours: int = 24
    min_paper_trades: int = 30
    min_paper_win_rate: float = 0.55
    slipage_mult_min: float = 0.6
    slipage_mult_max: float = 0.95

@dataclass
class PerformanceConfig:
    """性能追踪配置"""
    window_size: int = 100
    switch_threshold: float = 0.1
    min_samples: int = 10
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
    """系统总配置（双模式回测版）"""
    data: DataCollectionConfig = field(default_factory=DataCollectionConfig)
    pattern: PatternConfig = field(default_factory=PatternConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    backtest: BacktestConfig = field(default_factory=BacktestConfig)
    live: LiveTradingConfig = field(default_factory=LiveTradingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    exchanges: Dict[str, ExchangeConfig] = field(default_factory=lambda: {
        "bitget": ExchangeConfig(name="bitget", enabled=True, passphrase="qntsomtop"),
        "htx": ExchangeConfig(name="htx", enabled=True),
        "gate": ExchangeConfig(name="gate", enabled=True),
    })
    
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
