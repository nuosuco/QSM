"""
交易系统配置
基于碧树西风（记忆承载）交易系统思想
"""

# === 数据库配置 ===
DB_PATH = '/root/SOM/data/trading_system/trading.db'

# === 资金管理 ===
INITIAL_CAPITAL = 10000  # 初始资金（可调整）
MAX_POSITION_RATIO = 0.2  # 单品种最大仓位比例
MAX_TOTAL_POSITION = 0.8  # 最大总仓位
SAFE_PAD_RATIO = 0.2  # 安全垫比例

# === 风险控制 ===
SINGLE_STOP_LOSS = 0.02  # 单笔止损 2%
DAILY_STOP_LOSS = 0.05   # 日内止损 5%
WEEKLY_STOP_LOSS = 0.10  # 周度止损 10%
MAX_CONSECUTIVE_LOSS = 5  # 最大连续亏损次数
MAX_DRAWDOWN = 0.40       # 最大回撤 40%

# === 交易品种 ===
TRADING_PRODUCTS = {
    'futures': {
        'enabled': True,
        'api': 'CTP',
        'markets': ['SHFE', 'DCE', 'CZCE', 'CFFEX', 'INE']
    },
    'stock': {
        'enabled': True,
        'api': '券商API',
        'markets': ['SSE', 'SZSE']
    },
    'crypto': {
        'enabled': False,  # 暂不启用，仅自用
        'api': '交易所API',
        'hidden': True
    }
}

# === 策略配置 ===
STRATEGIES = {
    'trend_follow': {
        'enabled': False,
        'description': '趋势跟踪策略',
        'source': '捡乌龙指思想'
    },
    'arbitrage': {
        'enabled': False,
        'description': '量化套利策略',
        'source': '碧树西风套利经验'
    },
    'options_hedge': {
        'enabled': False,
        'description': '期权对冲策略',
        'source': '记忆承载期权文章'
    }
}

# === 日志配置 ===
LOG_LEVEL = 'INFO'
LOG_PATH = '/root/SOM/trading_system/logs/'

# === 回测配置 ===
BACKTEST_START = '2020-01-01'
BACKTEST_END = '2026-08-13'

# === 核心原则 ===
CORE_PRINCIPLES = [
    '向下有限，向上无限',
    'Rule一致性，双标就是没有Rule',
    '肥尾效应：9980次打平，等最后20次暴利',
    '对冲思维：天然控制损失',
    '量化思维：只关注概率',
    '不要ALL IN：永远保留选择权',
    '缩短持仓时间：减少人性干扰',
    '建立根据地：专精一个品种',
    '稳定盈利需要足够傻足够死板'
]
