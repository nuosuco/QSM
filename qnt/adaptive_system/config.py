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
    symbols: List[str] = field(default_factory=lambda: ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "DOGE/USDT", "AVAX/USDT", "LINK/USDT", "PEPE/USDT", "WIF/USDT", "SUI/USDT", "SEI/USDT", "ARB/USDT", "OP/USDT", "DOT/USDT", "ATOM/USDT", "ONDO/USDT", "FET/USDT", "INJ/USDT", "TIA/USDT"])
    # 更新频率(秒)
    update_interval: float = 1.0
    # 保留历史数据点数
    history_size: int = 10000
    # 数据库路径
    db_path: str = "/root/SOM/data/trading_system/adaptive.db"

@dataclass
class PatternConfig:
    """模式识别配置（观察用，不影响实盘交易）
    
    注意:模式发现阈值与执行引擎/风控层完全独立
    只用于历史数据分析，不控制实际交易决策
    """
    # 价差模式识别阈值（0.08% < 成本线0.16%，用于识别潜在模式）
    spread_threshold: float = 0.08
    # 可盈利模式判断阈值（0.10% < 成本线0.16%，辅助分析用）
    profitable_spread: float = 0.10
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
            "description": "挂双边单赚取价差（需要>0.16%价差覆盖成本）",
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
    
    风控底线:spread>0.41%（=成本0.16%+净利0.25%），net>0.25%
    # 价差阈值:价差必须大于此值才触发信号记录（风控底线: >0.41% = 成本0.16%+净利0.25%）
    spread_pct: float = 0.5
    # 净利阈值:净利必须大于此值才标记为可交易机会（风控底线: >0.25%）
    net_profit_pct: float = 0.3

@dataclass
@dataclass
class LiveTradingConfig:
    """实盘自动开关配置

    职责:只控制实盘交易的开/停。回测+模拟始终运行，不受影响。
    开启条件（全部满足）:权益>=min_equity 且 平台全连 且 模拟盘窗口达标
    停止条件（任一触发）:连亏/回撤/日亏/极端市场
    恢复:条件满足后自动解除，无需人工
    """
    # 总开关:false = 永久关实盘，回测+模拟照常
    enabled: bool = True

    # ---- 开启门槛 ----
    # 账户最低权益（USDT）。低于此值一律不开实盘:
    # 25U 是因为 Bitget 最小下单 5U，25U×20%=5U 刚好够单
    min_equity: float = 25.0
    # 模拟盘滚动窗口小时数
    paper_window_hours: int = 24
    # 窗口内最少交易笔数（样本不足不开实盘）
    min_paper_trades: int = 30
    # 窗口内最低胜率
    min_paper_win_rate: float = 0.55

    # ---- 模拟盘/回测成交率（用于贴近实盘真实成交）----
    fill_rate: float = 0.6          # 挂单成交概率（Post-Only 偏低）
    slipage_mult_min: float = 0.6   # 滑点/执行损耗下限
    slipage_mult_max: float = 0.95  # 滑点/执行损耗上限


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
    live: LiveTradingConfig = field(default_factory=LiveTradingConfig)
    
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