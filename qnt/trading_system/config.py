"""
记忆承载·碧树西风交易系统 - 配置模块
基于"捡乌龙指"核心逻辑的量化交易系统配置
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ExchangeConfig:
    """交易所配置"""
    name: str = ""
    api_key: str = ""
    api_secret: str = ""
    passphrase: str = ""  # OKX/Bitget需要
    testnet: bool = True  # 默认用测试网
    rate_limit: int = 100  # 每分钟请求限制
    fees_taker: float = 0.001  # Taker手续费率
    fees_maker: float = 0.0008  # Maker手续费率


@dataclass
class DetectionConfig:
    """检测参数 - v3做市策略"""
    # 价差阈值
    spread_threshold_pct: float = 0.12  # 价差超过此值才交易（成本线0.12%）
    min_profit_threshold_pct: float = 0.02  # 最小净利润阈值（留安全边际）
    
    # 做市策略参数
    post_only_enabled: bool = True  # 强制Post-Only
    immediate_cancel: bool = True  # 立即成交则取消
    
    # 原有参数保留
    price_deviation_pct: float = 2.0
    zscore_threshold: float = 3.0
    mad_threshold: float = 3.5
    stat_window_size: int = 200
    min_depth_btc: float = 0.01
    min_depth_usdt: float = 100.0
    cooldown_seconds: float = 1.0  # 做市策略冷却时间更短
    max_signals_per_minute: int = 60  # 做市策略更高频率


@dataclass
class RiskConfig:
    """风控参数 - 做市策略版"""
    max_loss_per_trade_pct: float = 0.5  # 单笔最大亏损（做市风险低）
    max_daily_loss_pct: float = 3.0  # 单日最大亏损
    max_drawdown_pct: float = 10.0
    max_consecutive_losses: int = 10  # 做市策略可承受更多连续亏损
    circuit_breaker_loss_pct: float = 5.0
    cooldown_after_losses_minutes: int = 10


@dataclass
class CapitalConfig:
    """资金管理参数 - 做市策略版"""
    initial_capital: float = 100.0  # 做市策略本金较小
    withdraw_after_double: bool = True
    profit_tier_pct: float = 50.0
    profit_tier_withdraw_pct: float = 20.0
    max_position_pct: float = 20.0  # 做市策略仓位可稍大


@dataclass
class BacktestConfig:
    """回测参数"""
    initial_capital: float = 10000.0
    duration_days: int = 30
    ticks_per_day: int = 28800  # 每天tick数(3秒一个)
    fat_finger_probability: float = 0.002  # 每个tick出现乌龙指的概率
    fat_finger_deviation_range: tuple = (2.0, 15.0)  # 乌龙指偏离范围%
    volatility_daily: float = 3.0  # 日波动率%
    trend_probability: float = 0.3  # 趋势行情概率


@dataclass
class DataConfig:
    """数据配置"""
    db_path: str = "/root/SOM/data/trading_system/adaptive.db"

@dataclass
class SystemConfig:
    """系统总配置 - v2多交易所版"""
    exchanges: Dict[str, ExchangeConfig] = field(default_factory=lambda: {
        "bitget": ExchangeConfig(name="bitget", fees_taker=0.0006, fees_maker=0.0004, passphrase=""),
        "binance": ExchangeConfig(name="binance", fees_taker=0.001, fees_maker=0.0008),
        "okx": ExchangeConfig(name="okx", fees_taker=0.0008, fees_maker=0.0006, passphrase=""),
        "bybit": ExchangeConfig(name="bybit", fees_taker=0.001, fees_maker=0.0007),
        "htx": ExchangeConfig(name="htx", fees_taker=0.002, fees_maker=0.0015),
        "gate": ExchangeConfig(name="gate", fees_taker=0.0015, fees_maker=0.001),
    })
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    capital: CapitalConfig = field(default_factory=CapitalConfig)
    backtest: BacktestConfig = field(default_factory=BacktestConfig)
    data: DataConfig = field(default_factory=DataConfig)
    symbols: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"
    ])
    log_level: str = "INFO"

    def load_api_keys(self):
        """从环境变量或~/.qnt_env文件加载API密钥"""
        import os
        # 如果环境变量没设置，从文件读取
        if not os.getenv('BITGET_API_KEY'):
            env_file = os.path.expanduser('~/.qnt_env')
            if os.path.exists(env_file):
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            k, v = line.split('=', 1)
                            os.environ[k] = v
        for exchange in self.exchanges.values():
            exchange.api_key = os.getenv(f'{exchange.name.upper()}_API_KEY', exchange.api_key)
            exchange.api_secret = os.getenv(f'{exchange.name.upper()}_API_SECRET', exchange.api_secret)
            if exchange.passphrase:
                exchange.passphrase = os.getenv(f'{exchange.name.upper()}_API_PASSPHRASE', exchange.passphrase)
