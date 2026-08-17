"""
QNT量子交易系统 - 配置中心
"""

# 系统模式
MODE = 'self_use_only'  # 仅自用

# 域名
DOMAIN = 'qnt.som.top'
FULL_DOMAIN = 'https://qnt.som.top'

# 数据库
TRADING_DB = '/root/SOM/data/trading_system/trading.db'
QNT_DB = '/root/SOM/data/trading_system/qnt.db'

# 交易所配置（通过CCXT）
EXCHANGES = {
    'binance': {
        'enabled': False,
        'api_key': '',
        'secret': '',
        'note': '全球最大，支持合约+现货'
    },
    'okx': {
        'enabled': False,
        'api_key': '',
        'secret': '',
        'password': '',
        'note': '中文友好，支持合约+现货'
    }
}

# 零风险策略配置
ZERO_RISK = {
    'max_single_loss_pct': 0.02,  # 单笔最大亏损2%
    'max_daily_loss_pct': 0.05,   # 日内最大亏损5%
    'max_leverage': 1,            # 零风险不用杠杆
    'position_size_pct': 0.2,     # 单品种20%仓位
    'stop_loss_pct': 0.02,        # 2%止损
    'take_profit_pct': 0.05,      # 5%止盈
}

# 捡乌龙指配置
ARBITRAGE = {
    'min_spread': 0.001,  # 最小价差0.1%
    'max_slippage': 0.0005,  # 最大滑点0.05%
    'timeout_seconds': 10,  # 超时10秒
}

# 大户公开交易数据
PUBLIC_TRADES = {
    'enabled': True,
    'type': 'futures_and_stock',  # 期货+股票公开
    'crypto': 'hidden'  # 数字货币隐藏
}
