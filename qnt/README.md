# QNT量子交易系统

基于CCXT连接交易所API，实现零风险交易（捡乌龙指）策略。

## 🚀 系统架构

```
QNT/
├── core/
│   └── engine.py      # 核心引擎（交易所连接、数据获取）
├── strategies/
│   └── zero_risk.py    # 零风险策略（捡乌龙指、订单流分析）
├── config/
│   └── settings.py     # 配置中心
├── main.py             # 主入口
└── README.md           # 本文档
```

## 📊 支持交易所

- ✅ **Binance US** - 硅谷服务器可直接访问
- ✅ **OKX** - 中文友好，国内可用
- ❌ Binance - 地理限制（硬451）
- ❌ Bybit - HTTP 403

## 🔧 快速开始

### 安装依赖
```bash
pip install ccxt>=4.5
```

### 运行扫描
```bash
cd /root/SOM/qnt
python3.11 main.py scan      # 扫描捡乌龙指机会
python3.11 main.py paper     # 纸面模拟交易
python3.11 main.py status    # 查看系统状态
```

### 运行结果示例
```
🎯 发现 6 个潜在机会:
  ⚠️  ATOM/USDT - 价差1.65%
  ⚠️  UNI/USDT - 价差2.72%
  ...
```

## 📈 核心策略

### 1. 捡乌龙指（Spread Arbitrage）
- 检测买卖价差异常（>0.05%）
- 在买盘低价买入，卖盘高价卖出
- 零风险套利，毫秒级执行

### 2. 订单流分析（Order Flow）
- 检测大单压盘/托盘
- 分析买卖不平衡
- 预判短期价格走势

### 3. 趋势跟踪（Trend Following）
- 多周期均线系统
- 趋势强度计算
- 顺势而为

## 🛡️ 风险管理

- 单笔止损：2%
- 单日最大亏损：5%
- 单品种仓位：≤20%
- 所有交易需人工确认

## 📁 数据库

- 路径：`/root/SOM/data/trading_system/qnt.db`
- 表：`qnt_logs`, `qnt_signals`, `qnt_trades`, `qnt_monitoring`

## 🔗 相关链接

- QNT域名：`qnt.som.top` → 170.106.196.211
- 交易系统合集：`/root/SOM/docs/TRADING_SYSTEM_COLLECTION.md`
- 交易系统方案：`/root/SOM/docs/TRADING_SYSTEM_PLAN.md`

---
_QNT v1.0 - 等错来，稳赚钱_
