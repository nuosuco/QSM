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
    """乌龙指检测参数"""
    price_deviation_pct: float = 2.0  # 价格偏离中间价百分比阈值
    zscore_threshold: float = 3.0  # Z-Score异常阈值
    mad_threshold: float = 3.5  # MAD异常阈值
    stat_window_size: int = 200  # 统计窗口大小(tick数)
    min_depth_btc: float = 0.01  # 最小深度(BTC)
    min_depth_usdt: float = 100.0  # 最小深度(USDT对)
    cross_exchange_spread_pct: float = 0.8  # 跨所价差阈值
    cross_exchange_min_profit_pct: float = 0.3  # 跨所最低净利润率
    cooldown_seconds: float = 5.0  # 同一交易对冷却期(秒)
    max_signals_per_minute: int = 10  # 每分钟最大信号数
    min_signal_strength: float = 0.5  # 最低信号强度


@dataclass
class RiskConfig:
    """风控参数 - 碧树西风标准"""
    max_loss_per_trade_pct: float = 2.0  # 单笔最大亏损占总资金%
    max_daily_loss_pct: float = 5.0  # 单日最大亏损占总资金%
    max_drawdown_pct: float = 10.0  # 最大回撤%
    max_consecutive_losses: int = 5  # 最大连续亏损次数
    circuit_breaker_loss_pct: float = 8.0  # 熔断触发亏损%
    cooldown_after_losses_minutes: int = 30  # 连续亏损后冷却(分钟)
    max_single_exchange_exposure_pct: float = 40.0  # 单交易所最大敞口%


@dataclass
class CapitalConfig:
    """资金管理参数 - 碧树西风标准"""
    initial_capital: float = 10000.0  # 初始资金(USDT)
    withdraw_after_double: bool = True  # 本金翻倍后提取原始投入
    profit_tier_pct: float = 50.0  # 利润分级提取阈值%
    profit_tier_withdraw_pct: float = 20.0  # 分级提取比例%
    max_position_pct: float = 10.0  # 单笔最大仓位占总资金%


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
