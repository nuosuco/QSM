# 自适应进化交易系统 v1.0 - 铁律方案

## 一、铁律（不可违背）

### 铁律1：三引擎必须真实运行
- **回测**：历史数据回放 + 实时追加，必须有完整BUY+SELL周期，不能只记BUY
- **模拟**：1000U初始资金，完整持仓管理，真实风控检查，模拟盈亏
- **实盘**：完全受控，只有满足所有开启条件才允许开实盘

### 铁律2：盈利验证才能开实盘
- 回测盈利 → 开启实盘试验
- 模拟盈利且样本足够 → 开启实盘交易
- 实盘亏损 → 立即停止，退回模拟重新验证

### 铁律3：风控层层收紧
- 执行引擎层：检查价差、净利、最小金额、精度
- 风控引擎层：检查仓位、止损、回撤、连续亏损
- 自动开关层：检查模拟盘表现、市场环境

### 铁律4：自适应进化
- 每个周期结束后分析交易记录
- 发现有效规律 → 更新策略参数
- 发现无效/亏损规律 → 废弃该策略
- 风控阈值随盈利情况动态调整

---

## 二、三引擎架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AdaptiveEvolutionSystem                  │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│ Backtest    │   Paper     │  Live       │  Evolution        │
│ Engine      │   Engine    │  Controller │  Manager          │
│ (历史+实时)  │ (实时模拟)   │ (真实交易)   │ (策略进化)         │
├─────────────┼─────────────┼─────────────┼───────────────────┤
│ - 完整BUY+S │ - 完整BUY+S │ - 真实下单   │ - 分析交易记录      │
│   ELL周期    │   ELL周期    │ - 完整风控   │ - 总结有效规律      │
│ - 1000U模拟 │ - 1000U模拟 │ - 最小金额   │ - 更新策略参数      │
│   资金       │   资金       │ - 精度检查   │ - 调整风控阈值      │
│ - 成交概率60%│ - 成交概率60%│ - 强平保护   │ - 生成进化报告      │
│ - 滑点模拟   │ - 滑点模拟   │ - 自动开关   │                   │
└─────────────┴─────────────┴─────────────┴───────────────────┘
```

### 2.1 回测引擎 (BacktestEngine)

**功能**：
- 历史数据回放（从数据库读取过去N天的market_data）
- 实时追加回测（新数据来了也回放）
- 完整BUY+SELL周期管理
- 真实风控检查（最小金额、精度、仓位限制）
- 模拟成交概率和滑点

**约束**：
- 每个交易对最多1个持仓
- 平仓条件：有盈利(净利>0.01%)或持仓超过60秒强制止损
- 不写engine_trades的live记录（只写backtest模式）
- 不触发真实下单

**输出**：
- engine_trades表（mode='backtest'）
- 回测统计报告（胜率、盈亏、最大回撤）

### 2.2 模拟引擎 (PaperEngine)

**功能**：
- 实时扫描市场数据
- 完整BUY+SELL周期管理
- 真实风控检查（同实盘）
- 模拟盘资金独立（1000U初始，不与实盘混淆）
- 成交概率60%，滑点0.02%

**约束**：
- 每个交易对最多1个持仓
- 风控检查通过后才开仓
- 平仓条件：有盈利(净利>0.01%)或持仓超过60秒强制止损
- 不写engine_trades的live记录（只写paper模式）
- 不触发真实下单

**输出**：
- engine_trades表（mode='paper'）
- 实时余额表（simulated_balance）
- 模拟盘统计报告

### 2.3 实盘控制器 (LiveTradingController)

**功能**：
- 只控制ExecutionEngine的开关
- 监控模拟盘表现
- 根据条件自动开启/停止实盘
- 风控状态持久化

**开启条件（全部满足）**：
1. 账户权益 >= min_equity (默认25U)
2. 必需平台全部连接成功
3. 模拟盘窗口 >= min_paper_trades (默认50笔)
4. 模拟盘窗口胜率 >= min_paper_win_rate (默认50%)
5. 市场环境不是extreme

**停止条件（任一触发）**：
- 连续亏损 >= MAX_CONSECUTIVE_LOSSES (默认3次)
- 最大回撤 >= MAX_DRAWDOWN_PCT (默认8%)
- 单日亏损 >= MAX_DAILY_LOSS_PCT (默认3%)
- 市场状态 extreme 且连续2次确认

**输出**：
- 控制ExecutionEngine.running标志
- 日志记录所有开关操作
- 状态持久化到risk_state表

### 2.4 自进化管理器 (EvolutionManager) ⭐新增

**功能**：
- 定期分析交易记录
- 发现有效/无效交易规律
- 自动调整策略参数
- 生成进化报告

**分析内容**：
1. **交易统计**：总交易数、胜率、平均盈亏、最大单笔盈亏
2. **策略效果**：不同策略在不同市场的表现
3. **风控有效性**：止损触发率、强平预警率
4. **市场适应性**：不同市场状态下盈利差异

**进化动作**：
- 如果发现某策略长期有效（胜率>55%，样本>100）→ 提升该策略优先级
- 如果发现某策略无效（胜率<45%）→ 降低优先级或禁用
- 如果市场波动增大但盈利稳定 → 可适当放宽阈值
- 如果市场波动增大且开始亏损 → 收紧阈值

**输出**：
- evolution_history表（记录每次进化参数）
- 进化报告（/root/SOM/qnt/evolution_report_YYYYMMDD.md）
- 自动更新config.py参数

---

## 三、风控铁律（所有引擎必须遵守）

### 3.1 成本线（定死不变）
```
成本线 = BI_SIDE_COST = 0.16%（永续+现货双边）
实际门槛 = 成本线 + MIN_NET_PROFIT_PCT = 0.16% + 0.01% = 0.17%
```

### 3.2 仓位限制（定死不变）
```
单币种最大仓位 = 账户权益 × MAX_POSITION_PCT (20%)
单交易所最大仓位 = 账户权益 × 0.50
```

### 3.3 止损机制
```
强制止损：持仓超过60秒未盈利立即平仓
硬止损：单笔亏损超过2%强制平仓
```

### 3.4 回撤保护
```
连续亏损5次 → 暂停实盘，退回模拟验证
最大回撤40% → 停止所有交易，人工介入
```

### 3.5 最小金额限制
```
Bitget: 永续≥5U, 现货≥1U
HTX:    永续≥1U, 现货≥1U
Gate:   永续≥3U, 现货≥3U
精度:   所有币数量≥1
```

---

## 四、文件清单

| 文件 | 说明 |
|------|------|
| `adaptive_system/config.py` | 配置类（阈值定义） |
| `adaptive_system/risk_manager.py` | 风控引擎（检查仓位、止损、回撤） |
| `adaptive_system/execution_engine.py` | 实盘执行引擎（真实下单） |
| `adaptive_system/dual_engine.py` | 回测+模拟双引擎（完整BUY+SELL） |
| `adaptive_system/live_trading_controller.py` | 实盘自动开关（受模拟盘表现控制） |
| `adaptive_system/evolution_manager.py` | ⭐新增：策略进化管理器 |
| `adaptive_system/__main__.py` | 主入口（协调三个引擎） |
| `STRATEGY_v4.md` | 策略文档（更新） |
| `QNT自适应策略引擎方案_v0.0.1.md` | 方案文档（更新为v1.0） |

---

## 五、验证流程

```
1. 启动系统
   ↓
2. 回测引擎回放历史数据（验证买入+卖出配对正确）
   ↓
3. 模拟引擎运行100笔交易（验证风控、胜率、盈亏）
   ↓
4. 检查模拟盘状态：
   - 胜率 >= 50%？
   - 样本 >= 50笔？
   - 最大回撤 < 20%？
   ↓ 不满足 → 退回步骤2重新调整策略
   ↓ 满足 → 继续
   ↓
5. 用户确认后开启实盘试验（config.live.enabled=True）
   ↓
6. 实时监控：
   - 前10笔交易每笔检查
   - 发现异常立即停止
   ↓
7. 实盘盈利且样本足够 → 全量开启
   实盘亏损 → 立即停止，退回模拟重新验证
   ↓
8. 每24小时运行进化分析
   - 总结有效规律
   - 调整策略参数
   - 更新风控阈值
   ↓
9. 循环步骤2-8，持续进化
```

---

## 六、关键代码逻辑

### 回测引擎核心逻辑（伪代码）
```python
class BacktestEngine:
    def _run_loop(self):
        for tick in market_data:
            # 检查是否有开仓机会
            if tick.spread >= cost + min_profit:
                if can_open_position(tick):
                    position = open_position(tick)
                    record_trade(position, 'opened')
            
            # 检查是否需要平仓
            for symbol, pos in open_positions:
                if should_close(pos, tick):
                    pnl_result = close_position(pos, tick)
                    record_trade(pnl_result, 'closed')
                    update_balance(pnl_result)
```

### 模拟引擎核心逻辑（伪代码）
```python
class PaperEngine:
    def _run_loop(self):
        while running:
            tick = fetch_latest_tick()
            
            # 检查持仓是否需要平仓
            for symbol, pos in open_positions:
                if should_close(pos, tick):
                    pnl = close_position(pos, tick)
                    balance += pnl
            
            # 检查是否可以开仓
            if can_open_position(tick):
                position = open_position(tick)
                record_trade(position, 'opened')
            
            time.sleep(0.5)
```

### 实盘控制器核心逻辑（伪代码）
```python
class LiveTradingController:
    def evaluate(self):
        conditions = []
        
        # 检查所有开启条件
        if equity < min_equity:
            conditions.append("权益不足")
        if not platforms_connected:
            conditions.append("平台未连接")
        if paper_trades < min_paper_trades:
            conditions.append("模拟样本不足")
        if paper_win_rate < min_win_rate:
            conditions.append("模拟胜率不足")
        if market_regime == 'extreme':
            conditions.append("极端市场")
        
        # 应用结果
        if len(conditions) == 0:
            enable_live()
        else:
            disable_live(conditions)
```

---

## 七、里程碑

- [x] v0.0.1：基础三平台连接
- [ ] v1.0：三引擎完整架构
  - [ ] 回测引擎：完整BUY+SELL周期
  - [ ] 模拟引擎：完整BUY+SELL周期
  - [ ] 实盘控制器：自动开关
  - [ ] 自进化管理器：策略优化
- [ ] v1.1：模拟盘盈利验证
- [ ] v1.2：实盘试验（小规模）
- [ ] v1.3：实盘全量（盈利确认）
- [ ] v2.0：多策略并行 + 自适应优化
