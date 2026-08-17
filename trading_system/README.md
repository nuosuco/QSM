# 交易系统项目结构

```
trading_system/
├── config/
│   └── settings.py          # 系统配置
├── core/
│   └── principles.py        # 核心交易原则
├── database/
│   └── init_db.py           # 数据库初始化
├── strategies/
│   ├── base_strategy.py     # 策略基类
│   └── patterns.py          # 具体策略实现
├── backtest/                # 回测模块（待开发）
├── execution/               # 执行模块（待开发）
├── data/                    # 数据目录
├── logs/                    # 日志目录
└── main.py                  # 主入口
```

## 数据库文件
- `/root/SOM/data/trading_system/trading.db` (68M)

## 文档
- `/root/SOM/docs/TRADING_SYSTEM_COLLECTION.md` - 碧树西风交易系统完整合集
- `/root/SOM/docs/TRADING_SYSTEM_PLAN.md` - 交易系统构建方案
