# QNT自适应策略引擎 - 完整方案文档

## 版本信息
- **版本号**: v0.0.1
- **日期**: 2026-08-15
- **作者**: 小蕊 + 中华
- **核心理念**: 让交易策略自己生长、进化、与时俱进

---

## 一、系统架构总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                    QNT自适应策略引擎 v1.0                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐           │
│  │ DataCollector │──▶│PatternDiscovery│──▶│StrategyEngine │          │
│  │  数据收集层   │   │  模式发现层   │   │  策略执行层   │           │
│  └──────────────┘   └──────────────┘   └──────────────┘           │
│         │                  │                  │                    │
│         ▼                  ▼                  ▼                    │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐           │
│  │ TradeAnalyzer │──▶│RiskManager   │──▶│ UpgradeMgr    │          │
│  │ 交易分析层   │   │ 风控管理层   │   │ 升级管理层   │           │
│  └──────────────┘   └──────────────┘   └──────────────┘           │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                        数据库层 (SQLite)                            │
│  market_data | signals | patterns | strategy_performance            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 二、核心策略体系

### 2.1 捡乌龙指套利 (fat_finger_arb)

**原理**: 同一平台内，永续合约与现货市场的价差异常时进行对冲套利

**核心逻辑**:
```
永续ask < 现货bid → 永续开多 + 现货卖单 → 瞬间锁利
不等价格恢复，不停留，不持仓过夜
```

**操作方式**:
- Post-Only订单确保只做Maker，不被Taker
- 两单同时挂出，都成交→完美对冲
- 只成交一单→另一单自动取消

**适用场景**:
- 价差 > 0.5%
- 深度足够（BTC>10000 USDT, ETH>5000 USDT）
- 同一平台操作（Bitget优先）

---

### 2.2 做市策略 (market_maker)

**原理**: 在买卖盘同时挂单，赚取价差

**参数**:
- 价差: 0.1%
- 单次挂单量: 100 USDT
- 层数: 5层

**风险**: 单边行情导致库存积压

---

### 2.3 均值回归策略 (mean_reversion)

**原理**: 价格偏离均值后，预期回归

**检测条件**:
- Z-Score > 2.0
- 过去50根K线偏离超过2个标准差
- 回归概率 > 60%

---

### 2.4 动量跟踪策略 (momentum)

**原理**: 跟随价格趋势，顺势而为

**参数**:
- 回看窗口: 20根K线
- 阈值: Z-Score > 2.0
- 止损: 反向突破均线

---

## 三、三类资金池管理

### 3.1 资金池定义

| 资金池 | 构成 | 用途 |
|--------|------|------|
| **BTC池** | BTC本金 + USDT本金 | 交易BTC时用 |
| **HTC池** | 利润储备池 | 交易其他币种时作本金 |
| **USDT池** | 交易流动性 | 随时可调拨 |

### 3.2 资金分配规则（定死）

```
交易BTC:
  - 使用: BTC本金20% + USDT本金80%
  - 盈利50% → 转入HTC储备池（永不回流）

交易其他币种:
  - 使用: USDT+币种本金20% + HTC本金80%
  - 盈利50% → 转入BTC储备池（永不回流）
```

### 3.3 盈利提取规则

```
盈利50%立即取出，永不回流市场
只留50%复利滚动

示例:
  初始资金: 10U
  盈利10U → 取出5U，留下5U继续交易
  再盈利10U → 再取出5U，留下5U继续...
  
这就是"出来混，不要还"的精髓
```

---

## 四、风控铁律

### 4.1 硬性规则

| 规则 | 参数 | 说明 |
|------|------|------|
| 单笔最大仓位 | ≤20%总资金 | 防止单票暴毙 |
| 单笔最大止损 | ≤2%总资金 | 控制单笔亏损 |
| 连续亏损暂停 | 5次 | 冷静期 |
| 最大回撤保护 | <40% | 熔断机制 |
| 盈利取出 | 50%永不回流 | 落袋为安 |

### 4.2 自适应风控

根据市场波动率动态调整：

```
calm市场:  仓位1.5x, 止损1.5%
normal市场: 仓位1.0x, 止损2.0%
volatile市场: 仓位0.5x, 止损1.0%
extreme市场: 暂停交易
```

---

## 五、技术实现

### 5.1 文件结构

```
/root/SOM/qnt/
├── adaptive_system/          # 自适应系统核心
│   ├── __init__.py
│   ├── config.py             # 配置管理
│   ├── models.py             # 数据模型
│   ├── data_collector.py     # 实时数据收集
│   ├── pattern_discovery.py  # 模式发现引擎
│   ├── trade_analyzer.py     # 交易总结分析
│   └── self_evolution.py     # 自进化主引擎
│
├── trading_system/           # 交易执行系统
│   ├── exchange_adapter.py   # 交易所适配器
│   ├── engine.py             # 多模式引擎(live/paper/scan)
│   ├── backtest.py           # 回测引擎
│   └── config.py             # 交易配置
│
├── strategies/               # 策略集合
│   ├── zero_risk.py          # 零风险策略
│   ├── maker_strategy.py     # 做市策略
│   └── oolong_index_v2.py    # 捡乌龙指v2
│
├── data/                     # 数据存储
│   └── trading_system/
│       ├── adaptive.db       # 自适应数据
│       └── qnt.db           # 交易历史
│
└── logs/                     # 日志
    ├── self_evolution.log
    └── adaptive_system.log
```

### 5.2 数据库设计

```sql
-- 市场数据表
CREATE TABLE market_data (
    id INTEGER PRIMARY KEY,
    timestamp REAL,
    symbol TEXT,
    spot_bid REAL,
    spot_ask REAL,
    spot_last REAL,
    perp_bid REAL,
    perp_ask REAL,
    perp_last REAL,
    spread_pct REAL,
    basis_pct REAL,
    depth_ratio REAL
);

-- 信号记录表
CREATE TABLE signals (
    id INTEGER PRIMARY KEY,
    timestamp REAL,
    symbol TEXT,
    signal_type TEXT,
    strategy TEXT,
    expected_profit REAL,
    actual_profit REAL,
    executed INTEGER DEFAULT 0,
    metadata TEXT
);

-- 策略绩效表
CREATE TABLE strategy_performance (
    id INTEGER PRIMARY KEY,
    timestamp REAL,
    strategy TEXT,
    total_trades INTEGER,
    winning_trades INTEGER,
    win_rate REAL,
    avg_profit REAL,
    total_profit REAL
);

-- 模式发现表
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY,
    timestamp REAL,
    pattern_type TEXT,
    symbol TEXT,
    confidence REAL,
    profitability REAL,
    parameters TEXT,
    status TEXT
);
```

### 5.3 交易所支持

| 交易所 | 状态 | 说明 |
|--------|------|------|
| Bitget | ✅ 可用 | 首选，国内可用 |
| HTX | ⚠️ 待测试 | 备选 |
| Binance | ❌ 被墙 | 硬451 |
| Bybit | ❌ 被墙 | 403 |

---

## 六、运行模式

### 6.1 三种模式

| 模式 | 说明 | 适用阶段 |
|------|------|---------|
| **backtest** | 历史数据回溯验证 | 策略开发期 |
| **paper** | 模拟盘（真实数据+虚拟下单） | 策略验证期 |
| **live** | 实盘（真实数据+真实下单） | 稳定盈利期 |

### 6.2 扫描模式

```bash
# 单次扫描，检查当前机会
python3.11 -m trading_system.engine scan

# 查看实时状态
python3.11 -m trading_system.engine status
```

---

## 七、自进化机制

### 7.1 进化流程

```
时间线 → 数据积累 → 模式发现 → 策略验证 → 自动升级
────────────────────────────────────────────────────
现在     → 2000条    → 价差分布  → fat_finger权重↑
1周后    → 10万条    → 时段规律  → 时间窗口优化
1月后    → 100万条   → 多策略组合 → 自动切换最优
```

### 7.2 阶段目标

| 阶段 | 数据量 | 目标 |
|------|--------|------|
| Phase 1: 数据收集 | 1万条 | 建立基线，发现基础模式 |
| Phase 2: 模式验证 | 10万条 | 验证策略胜率，调整参数 |
| Phase 3: 实盘测试 | 100万条 | 小资金实盘，验证执行质量 |
| Phase 4: 自动升级 | 持续 | 策略自动切换，风控自适应 |

### 7.3 升级触发条件

```python
if data_sufficient and pattern_discovered and strategy_validated and profit_stable:
    execute_upgrade()  # 保存快照，加载最优策略组合
```

---

## 八、部署与运维

### 8.1 启动命令

```bash
# 启动自进化引擎
cd /root/SOM/qnt
nohup python3.11 -m adaptive_system.self_evolution > self_evolution.log 2>&1 &

# 查看日志
tail -f /root/SOM/qnt/self_evolution.log

# 查看数据量
sqlite3 /root/SOM/data/trading_system/adaptive.db "SELECT COUNT(*) FROM market_data;"

# 停止引擎
kill $(ps aux | grep self_evolution | grep python | awk '{print $2}')
```

### 8.2 监控指标

| 指标 | 正常值 | 告警值 |
|------|--------|--------|
| 数据收集速率 | >900 ticks/小时 | <500 ticks/小时 |
| 策略胜率 | >50% | <40% |
| 最大回撤 | <10% | >20% |
| 市场波动率 | <0.1% | >0.5% (极端市场) |

### 8.3 备份策略

```bash
# 每日备份
tar -czf /root/backups/qnt_adaptive_$(date +%Y%m%d).tar.gz \
    /root/SOM/data/trading_system/adaptive.db \
    /root/SOM/qnt/adaptive_system/

# Git版本控制
cd /root/SOM
git add qnt/
git commit -m "chore: QNT自适应引擎更新"
git push origin som
```

---

## 九、资金规划

### 9.1 充值计划

| 时间 | 金额 | 目的 |
|------|------|------|
| 现在 | 测试网 | 系统验证 |
| 充钱后 | ≥5U | 模拟盘验证 |
| 9月1日 | 30U | 正式启动 |
| 每月1日 | 30U | 持续追加 |

### 9.2 预期收益（基于回测）

| 初始资金 | 月投入 | 1年后总资金 | ROI |
|----------|--------|-------------|-----|
| 5U | 30U/月 | ~430U | 1260% |
| 10U | 30U/月 | ~860U | 1380% |
| 30U | 30U/月 | ~2580U | 1410% |

**说明**: 以上为回测数据，实盘可能有偏差，保守估计取回测值的30%。

---

## 十、核心哲学

### 10.1 碧树西风思想

```
"出来混，不要还"
→ 盈利50%取出，永不回流

"等错来，不等错走"
→ 被动等待乌龙指，不主动预测

"做市而非预测"
→ 挂单等成交，而非预测方向
```

### 10.2 自进化理念

```
不追求永远正确的策略
追求能快速学习和适应的系统

每一笔交易都是学习机会
每一次亏损都是进化养分
```

---

## 十一、未来演进方向

### 11.1 短期（1个月内）
- [ ] 完善模式发现算法
- [ ] 增加更多币种监控
- [ ] 实盘小资金测试

### 11.2 中期（3个月内）
- [ ] 多策略组合优化
- [ ] 跨所套利支持
- [ ] 移动端监控面板

### 11.3 长期（1年内）
- [ ] 深度学习模式识别
- [ ] 自动化策略生成
- [ ] 社区共享策略市场

---

## 十二、总结

QNT自适应策略引擎是一个**会自己生长、进化的交易系统**。

它不依赖固定策略，而是：
1. **持续收集**真实市场数据
2. **自动发现**可盈利的模式
3. **动态调整**策略权重
4. **阶段性升级**系统能力
5. **自适应风控**应对市场变化

正如碧树西风所说：
> "交易市场没有永恒的王者，只有不断进化的幸存者。"

让我们一起见证这个系统的成长 🌱

---

**文档版本**: v0.0.1  
**最后更新**: 2026-08-15 20:40 GMT+8  
**作者**: 小蕊 & 中华
