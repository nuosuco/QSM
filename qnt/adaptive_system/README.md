# 自适应策略引擎 v1.0

## 功能说明

持续收集真实交易数据，自动发现可盈利的市场模式，动态调整策略权重。

## 核心组件

### 1. DataCollector - 数据收集器
- 每秒收集5个币种的实时数据
- 存储：现货/永续价格、价差、深度比
- 数据库：`/root/SOM/data/trading_system/adaptive.db`

### 2. PatternDiscovery - 模式发现引擎
- 价差套利模式：永续vs现货价差异常
- 均值回归模式：价格偏离后回归
- 深度异常模式：买卖深度失衡
- 成交量突变模式：异常放量

### 3. AdaptiveEngine - 自适应引擎
- 实时监控数据
- 每5分钟分析一次
- 自动切换最优策略
- 策略权重动态调整

## 当前状态

```
监控币种: BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT, XRP/USDT
数据收集: 每1秒
策略分析: 每300秒
当前策略: fat_finger_arb (捡乌龙指套利)
```

## 数据样本 (实时)

| 币种 | 平均价差 | 最大价差 | 样本数 |
|------|---------|---------|--------|
| BTC  | 0.040%  | 0.041%  | 正常   |
| ETH  | 0.043%  | 0.043%  | 正常   |
| SOL  | 0.052%  | 0.052%  | 正常   |
| BNB  | 0.087%  | 0.087%  | 略高   |
| XRP  | 0.070%  | 0.070%  | 略高   |

**结论**: 当前市场正常，没有发现乌龙指机会（价差<0.5%）

## 启动命令

```bash
cd /root/SOM/qnt
python3.11 -m adaptive_system.engine
```

## 查看日志

```bash
tail -f /root/SOM/qnt/adaptive_system.log
```

## 查询数据库

```bash
sqlite3 /root/SOM/data/trading_system/adaptive.db
> SELECT * FROM market_data ORDER BY timestamp DESC LIMIT 10;
> SELECT * FROM signals;
> SELECT * FROM patterns;
```

## 策略演进

随着数据积累，引擎会：
1. 发现新的可盈利模式
2. 评估各策略表现
3. 自动切换更优策略
4. 记录模式发现历史

---
*基于碧树西风"记忆承载"思想，让系统从真实数据中学习*
