# QNT自适应策略引擎方案 v1.0
**版本**: 1.0  
**更新日期**: 2026-09-01  
**状态**: 三引擎系统运行中

---

## 一、系统架构

### 1.1 三引擎设计
```
┌─────────────────────────────────────────────────────────────┐
│                    自适应进化交易系统 v1.0                   │
├─────────────────────────────────────────────────────────────┤
│  📊 回测引擎                                                │
│     ├── 历史数据回放（已完成599,154条）                      │
│     └── 实时数据监控（已切换到实时模式）                      │
│                                                             │
│  📝 模拟引擎                                                │
│     ├── 初始资金：1000 USDT                                 │
│     └── 实时模拟交易（严格执行风控）                         │
│                                                             │
│  🔒 实盘控制器                                              │
│     └── 状态：🔒 已关闭（等待验证通过）                     │
│                                                             │
│  🧬 自进化系统                                              │
│     └── 每24小时分析交易记录，优化策略参数                   │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 引擎关系
```
历史数据 → 回测引擎 → 发现规律 → 自进化系统 → 优化参数
                                              ↓
实时数据 → 回测引擎 → 验证规律 → 模拟引擎 → 验证策略
                                              ↓
                                          实盘控制器（用户确认后开启）
```

---

## 二、风控体系

### 2.1 核心阈值（定死不变）
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

# 实际交易门槛
# 成本线 = 0.16%
# 净利要求 = 0.01%
# 实际门槛 = 价差 > 0.17%
```

### 2.2 风控检查流程
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

### 2.3 资金管理规则
```
交易BTC：
  - BTC本金：20%
  - USDT本金：80%

交易其他币种：
  - USDT+币种本金：20%
  - HTC本金：80%

盈利分配：
  - 50%立即转入对应储备池
  - 永不回流交易本金
```

---

## 三、策略体系

### 3.1 核心策略
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

### 3.2 辅助策略
```
深度异常检测：
  - 监控订单簿深度变化
  - 识别大单冲击
  - 提前预判价格波动
```

---

## 四、进化机制

### 4.1 自进化流程
```
每24小时执行：
1. 收集交易数据（最近7天）
2. 分析胜率和盈亏
3. 识别失败模式
4. 调整策略参数
5. 记录进化历史
```

### 4.2 可调参数
```
敏感度参数：
  - spread_pct（价差敏感度）
  - net_profit_pct（净利敏感度）
  - 成交概率（0.6 → 可调）

风控参数（定死）：
  - MIN_NET_PROFIT_PCT
  - MAX_POSITION_PCT
  - MAX_STOP_LOSS_PCT
```

---

## 五、数据库设计

### 5.1 核心表结构
```sql
-- 交易记录表
CREATE TABLE engine_trades (
    id INTEGER PRIMARY KEY,
    timestamp REAL,
    mode TEXT,           -- backtest/paper/live
    symbol TEXT,
    exchange TEXT,
    side TEXT,           -- BUY/SELL
    price REAL,
    amount REAL,
    cost REAL,
    fee REAL,
    pnl REAL,
    pnl_pct REAL,
    status TEXT          -- opened/closed
);

-- 市场数据表
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

-- 信号记录表
CREATE TABLE engine_signals (
    timestamp REAL,
    mode TEXT,
    symbol TEXT,
    exchange TEXT,
    side TEXT,
    spread_pct REAL,
    net_profit_pct REAL,
    position_size REAL,
    status TEXT
);

-- 进化历史表
CREATE TABLE evolution_history (
    timestamp REAL,
    metrics_json TEXT,
    changes_json TEXT
);
```

---

## 六、部署架构

### 6.1 文件结构
```
/root/SOM/qnt/
├── adaptive_system/
│   ├── __main__.py          # 主入口
│   ├── config.py            # 配置管理
│   ├── dual_engine.py       # 双引擎系统
│   ├── execution_engine.py  # 执行引擎
│   ├── risk_manager.py      # 风控管理
│   ├── evolution_manager.py # 进化管理
│   └── live_trading_controller.py
├── STRATEGY_v4.md           # 策略文档
├── QNT自适应策略引擎方案_v1.0.md
└── 阈值配置记录_v1.0.md

/root/SOM/data/trading_system/
└── adaptive.db              # 主数据库

/etc/systemd/system/
└── qnt-engines.service      # 系统服务
```

### 6.2 服务配置
```ini
[Unit]
Description=QNT Adaptive Dual Engine
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

## 七、监控与告警

### 7.1 实时监控
```bash
# 查看引擎状态
systemctl status qnt-engines

# 查看实时日志
journalctl -u qnt-engines -f

# 查看交易统计
sqlite3 /root/SOM/data/trading_system/adaptive.db \
  "SELECT mode, COUNT(*), SUM(pnl) FROM engine_trades GROUP BY mode;"
```

### 7.2 告警机制
```
价差预警：
  - 价差 > 0.17% 时记录机会
  - 日志显示"[回测] 发现机会"

风控拒绝：
  - 风控检查不通过时记录原因
  - 日志显示"[回测] 风控拒绝: ..."

异常检测：
  - 连续亏损5次自动暂停
  - 回撤超过40%自动停止
```

---

## 八、当前状态（2026-09-01 22:25）

### 8.1 引擎运行状态
```
📊 回测引擎:
   状态: 运行中
   交易数: 5 笔
   胜率: 20.0%
   总盈亏: +$0.11 U
   持仓: 1 个

📝 模拟引擎:
   状态: 运行中
   交易数: 1 笔
   胜率: 100.0%
   总盈亏: +$0.21 U
   持仓: 8 个
   余额: $1000.21 U

🔒 实盘控制器:
   状态: 已关闭
   原因: 等待回测+模拟验证通过
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
  状态: ❌ 禁用（资金已亏损完毕）
  API密钥: 已清空
```

---

## 九、开启实盘流程

### 9.1 前置条件
1. ✅ 回测胜率 > 50%
2. ✅ 模拟胜率 > 50%
3. ✅ 回测+模拟累计盈利 > 0
4. ✅ 用户明确确认开启

### 9.2 开启步骤
```bash
# 1. 修改配置（用户操作）
sed -i 's/live_enabled: false/live_enabled: true/' config.py

# 2. 重启服务
systemctl restart qnt-engines

# 3. 监控日志
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
```

---

## 十、关键教训

### 10.1 HTX亏损教训（2026-08-31）
```
问题：
  - 旧代码 config.live.enabled 默认为 True
  - 实盘自动开启但日志记录不完整
  - 导致HTX账户亏损完毕

修复：
  - 默认改为 False
  - 添加硬编码安全检查
  - HTX API密钥清空，永久禁用

教训：
  - 实盘必须用户手动开启
  - 日志必须完整记录每笔交易
  - 任何代码改动必须经过回测验证
```

### 10.2 阈值配置教训
```
问题：
  - MIN_NET_PROFIT_PCT = 0.01（1%）导致门槛过高
  - 实际要求价差 > 1.16%，几乎无交易机会

修复：
  - 改为 0.0001（0.01%）
  - 实际门槛降至 0.17%

教训：
  - 阈值必须实测验证
  - 不能只看配置值，要算实际门槛
```

---

## 十一、未来规划

### 11.1 短期目标
1. 提升回测胜率至 > 50%
2. 增加模拟交易样本至50笔以上
3. 积累足够盈利后开启实盘

### 11.2 中期目标
1. 引入更多策略（趋势跟踪、均值回归）
2. 优化进化算法
3. 支持更多交易所

### 11.3 长期目标
1. 全自动自适应交易系统
2. 多策略组合
3. 风险动态调整

---

**文档维护**: 小蕊 🤖  
**最后更新**: 2026-09-01 22:25 GMT+8
