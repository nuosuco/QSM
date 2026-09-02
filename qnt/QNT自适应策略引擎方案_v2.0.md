# QNT自适应策略引擎方案 v2.0（双模式回测版）
**版本**: 2.0  
**更新日期**: 2026-09-02  
**状态**: 双模式回测系统运行中

---

## 一、系统架构

### 1.1 双模式回测 + 模拟 + 实盘
```
┌─────────────────────────────────────────────────────────────┐
│                  双模式回测自适应交易系统 v2.0               │
├─────────────────────────────────────────────────────────────┤
│  📊 回测引擎（双模式并行）                                   │
│     ├── 模式一：分析我们的真实成交历史（historical_trades）   │
│     └── 模式二：回测平台市场成交数据（market_trades）         │
│                                                             │
│  📝 模拟引擎                                                │
│     ├── 初始资金：1000 USDT/平台                             │
│     └── 实时模拟交易（严格执行风控）                         │
│                                                             │
│  🔒 实盘控制器                                              │
│     └── 状态：🔒 已关闭（等待验证通过）                     │
│                                                             │
│  🧬 自进化系统                                              │
│     └── 双模式对比分析，发现有效规律并应用到模拟盘            │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 完整交易流程
```
阶段一：双模式回测
  ├── 模式一：分析历史成交（我们的322笔真实成交）
  │           → 找出盈利币种、亏损币种
  ├── 模式二：回测市场成交（平台公开数据）
  │           → 验证策略是否适用于市场
  └── 对比分析：两者一致时确认策略有效

阶段二：模拟验证
  ├── 使用回测发现的规律进行实时模拟
  ├── 严格风控检查（价差>0.17%、仓位≤20%）
  └── 积累样本（目标≥100笔交易）

阶段三：实盘验证
  ├── 模拟盈利≥50%时申请开启
  ├── 小仓位验证（单笔≤5%）
  └── 逐步扩大仓位至20%

阶段四：持续实盘
  ├── 每日分析进化
  ├── 盈利提取50%永不回流
  └── 持续监控风控阈值
```

---

## 二、双模式回测体系

### 2.1 模式一：历史成交分析
```
数据来源：historical_trades表
采集方式：fetch_my_trades（需要API密钥）
数据量：Gate 305笔 + Bitget 10笔 + HTX 7笔 = 322笔
分析内容：
  - 各平台盈亏统计
  - 各币种盈亏统计
  - 盈利/亏损规律总结
```

### 2.2 模式二：市场成交回测
```
数据来源：market_trades表
采集方式：fetch_trades（公开API，不需要密钥）
数据量：每小时每个币种500笔
分析内容：
  - 市场买卖比例
  - 热门币种统计
  - 价差分布分析
```

### 2.3 双模式对比分析
```
一致性判断：
  - 模式一盈利 AND 模式二盈利 → 策略有效 ✅
  - 模式一亏损 AND 模式二亏损 → 策略需优化 ❌
  - 结果不一致 → 深入分析差异原因 ⚠️

统一规律：
  - 共同盈利币种 → 提升优先级
  - 共同亏损币种 → 降低优先级
  - 分歧币种 → 暂停交易观察
```

---

## 三、风控体系

### 3.1 核心阈值（定死不变）
```python
# 风控层阈值
MIN_NET_PROFIT_PCT = 0.0001    # 净利必须 > 0.01%
MAX_POSITION_PCT = 0.20        # 单笔仓位 ≤ 20%
MAX_STOP_LOSS_PCT = 0.02       # 止损 ≤ 2%
MAX_CONSECUTIVE_LOSSES = 5     # 连续亏损5次暂停
MAX_DRAWDOWN_PCT = 0.40        # 最大回撤40%停止
PROFIT_WITHDRAW_PCT = 0.50     # 盈利50%提取永不回流

# 执行层阈值（可调灵敏度）
spread_pct = 0.17              # 价差阈值 > 0.17%
net_profit_pct = 0.01          # 净利阈值 > 0.01%
BI_SIDE_COST = 0.16%           # 双边成本（不改）
fill_rate = 0.6                # 成交概率

# 实际交易门槛
# 成本线 = 0.16%
# 净利要求 = 0.01%
# 实际门槛 = 价差 > 0.17%
```

### 3.2 风控检查流程
```
开仓前检查顺序：
1. 价差检查：spread >= 0.17%？❌ 不通过 → 跳过
2. 风控检查：check_risk()？❌ 不通过 → 跳过
3. 最小金额：position >= min_notional？❌ 不通过 → 跳过
4. 精度检查：amount >= 1.0？❌ 不通过 → 跳过
5. 成交概率：random() < 0.6？❌ 未命中 → 跳过
6. 持仓检查：无同币种同方向？❌ 已有 → 跳过
✅ 全部通过 → 执行开仓
```

---

## 四、策略体系

### 4.1 核心策略
```
策略一：捡乌龙指（跨厅套利）
  - 必要条件：同一币种在≥2个交易点，A厅异常+B厅正常
  - 操作：A厅买入异常价 + B厅卖出正常价，瞬间锁利
  - 不等价格恢复，不停留

策略二：单平台双厅套利（永续+现货）
  - Post-Only订单确保只做Maker
  - 永续买 + 现货卖同时挂出
  - 两单都成交→完美对冲
  - 只成交一单→另一单自动取消

策略三：动量跟踪
  - 识别趋势方向
  - 跟随趋势交易
  - 严格止损

策略四：均值回归
  - 识别价格偏离
  - 反向交易
  - 目标回归均值
```

---

## 五、进化机制

### 5.1 双模式进化流程
```
每2小时执行：
1. 收集双模式数据（历史成交+市场成交）
2. 对比分析一致性
3. 发现盈利/亏损规律
4. 将规律应用到模拟盘
5. 记录进化历史
```

### 5.2 参数调整规则
```
一致盈利时：
  - spread_pct可从0.17%降至0.15%（放宽门槛）
  - fill_rate可从0.6升至0.8（提高成交率）
  - 提升盈利币种优先级

一致亏损时：
  - spread_pct从0.17%升至0.20%（收紧门槛）
  - 降低亏损币种优先级
  - 暂停分歧币种交易

分歧时：
  - 深入分析差异原因
  - 优先信任历史成交数据
  - 降低模拟盘交易频率
```

---

## 六、数据库设计

### 6.1 核心表结构
```sql
-- 我们的真实成交（模式一）
CREATE TABLE historical_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL,
    exchange TEXT,
    symbol TEXT,
    side TEXT,
    type TEXT,
    price REAL,
    amount REAL,
    cost REAL,
    fee REAL,
    fee_currency TEXT,
    order_id TEXT,
    position_id TEXT,
    strategy TEXT,
    status TEXT,
    data_source TEXT DEFAULT 'my_trades'
);

-- 平台市场成交（模式二）
CREATE TABLE market_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL,
    exchange TEXT,
    symbol TEXT,
    side TEXT,
    price REAL,
    amount REAL,
    cost REAL,
    order_id TEXT
);

-- 引擎交易记录
CREATE TABLE engine_trades (
    id INTEGER PRIMARY KEY,
    timestamp REAL,
    mode TEXT,           -- backtest/paper/live
    symbol TEXT,
    exchange TEXT,
    side TEXT,
    price REAL,
    amount REAL,
    cost REAL,
    fee REAL,
    pnl REAL,
    pnl_pct REAL,
    status TEXT,
    position_id TEXT
);

-- 市场数据（价差分析）
CREATE TABLE market_data (
    timestamp REAL,
    exchange TEXT,
    symbol TEXT,
    spot_bid REAL,
    spot_ask REAL,
    perp_bid REAL,
    perp_ask REAL,
    spread_pct REAL
);

-- 进化历史
CREATE TABLE evolution_history (
    timestamp REAL,
    parameter TEXT,
    old_value REAL,
    new_value REAL,
    reason TEXT,
    applied INTEGER
);
```

---

## 七、部署架构

### 7.1 文件结构
```
/root/SOM/qnt/
├── adaptive_system/
│   ├── __main__.py              # 主入口
│   ├── config.py                # 配置管理（含BacktestConfig）
│   ├── dual_engine.py           # 双模式回测引擎
│   ├── execution_engine.py      # 执行引擎
│   ├── risk_manager.py          # 风控管理
│   ├── evolution_manager.py     # 双模式进化管理
│   ├── historical_fetcher.py    # 历史成交采集器（双模式）
│   └── market_trade_collector.py # 市场成交采集任务
├── STRATEGY_v4.md               # 策略文档
├── QNT自适应策略引擎方案_v2.0.md # 本方案
└── 阈值配置记录_v1.0.md

/root/SOM/data/trading_system/
└── adaptive.db                  # 主数据库
```

### 7.2 服务配置
```ini
[Unit]
Description=QNT Dual-Mode Backtest System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/SOM/qnt
ExecStart=/usr/bin/python3.11 -m adaptive_system
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 八、当前状态（2026-09-02 10:25）

### 8.1 引擎运行状态
```
📊 回测引擎（双模式）:
   模式一：历史成交分析（322笔真实成交）
   模式二：市场成交回测（进行中...）
   实时模式：价差监控中

📝 模拟引擎:
   状态：运行中
   初始资金：1000 USDT/平台
   严格执行风控

🔒 实盘控制器:
   状态：已关闭
   条件：回测+模拟验证通过后开启
```

### 8.2 交易所状态
```
Gate:
  现货余额: 2.00 U
  永续余额: 18.30 U
  总权益: 20.30 U
  状态: ✅ 可用

Bitget:
  余额: 3.50 U
  状态: ✅ 可用

HTX:
  状态: ⚠️ 资金较少，专注Gate交易
  API密钥: 已恢复（备用）
```

---

## 九、开启实盘流程

### 9.1 前置条件（必须全部满足）
```
✅ 模式一：历史成交净盈亏 > 0
✅ 模式二：市场回测胜率 > 50%
✅ 模拟盘：连续3天盈利，交易≥50笔
✅ 双模式对比：结果一致
✅ 用户明确确认开启
```

### 9.2 开启步骤
```bash
# 1. 确认条件满足
sqlite3 /root/SOM/data/trading_system/adaptive.db \
  "SELECT exchange, SUM(CASE WHEN side='sell' THEN cost ELSE 0 END) - \
         SUM(CASE WHEN side='buy' THEN cost ELSE 0 END) as pnl \
   FROM historical_trades GROUP BY exchange;"

# 2. 修改配置（用户操作）
sed -i 's/enabled: false/enabled: true/' ~/.adaptive_system_config.json

# 3. 重启服务
systemctl restart qnt-engines

# 4. 监控日志
journalctl -u qnt-engines -f | grep -i "实盘"
```

### 9.3 风险控制
```
首次开启：
  - 单笔仓位 ≤ 5%
  - 止损 ≤ 1%
  - 每日最多5笔交易

验证通过后：
  - 逐步增加仓位至20%
  - 恢复正常风控参数

盈利后：
  - 提取50%利润永不回流
  - 只使用剩余本金交易
```

---

## 十、关键原则

### 10.1 双模式对比原则
```
原则一：两者一致才信任
  - 只有模式一和模式二结果一致时，才确认策略有效
  
原则二：历史数据优先
  - 当结果不一致时，优先相信我们的真实成交数据
  
原则三：快速迭代
  - 每天对比，快速发现有效规律并应用
```

### 10.2 进化应用原则
```
原则一：盈利规律立即应用
  - 发现盈利币种 → 立即提升优先级
  
原则二：亏损规律立即止损
  - 发现亏损币种 → 立即降低优先级或暂停
  
原则三：分歧币种观察
  - 结果不一致的币种 → 暂停交易，深入分析
```

---

## 十一、未来规划

### 11.1 短期目标（本周）
1. 完成双模式回测数据积累
2. 至少100笔市场成交数据
3. 确认历史成交规律有效性
4. 模拟盘积累≥50笔交易

### 11.2 中期目标（本月）
1. 开启实盘交易（Gate主平台）
2. 每日进化分析优化策略
3. 建立盈利提取机制
4. 完善风险预警系统

### 11.3 长期目标
1. 多策略组合优化
2. 自动化实盘运行
3. 支持更多交易所
4. 智能风控动态调整

---

**文档维护**: 小蕊 🤖  
**最后更新**: 2026-09-02 10:25 GMT+8
