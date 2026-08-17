# QNT 量子叠加态基础设施

> **QNT = Quantum Superposition Network**
>
> 区块链 + 交易所 + AI模型 三位一体的量子叠加态并行基础设施

---

## 🚀 快速开始

```bash
cd /root/QNT

# 运行验证
./verify.sh

# 启动服务
./start.sh
```

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     QNT 基础设施层                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  QNT 区块链   │  │  QNT 交易所   │  │  QNT 叠加态模型 │       │
│  │  (Layer 1)    │  │  (DEX+CEX)   │  │  (N-State)    │       │
│  │              │  │              │  │              │       │
│  │ • 叠加态共识  │  │ • 用户交易    │  │ • N态并行训练  │       │
│  │ • 多链并行    │  │ • Agent交易   │  │ • 观测坍缩    │       │
│  │ • QNT代币    │  │ • 价差套利    │  │ • 集成学习    │       │
│  │ • 智能合约    │  │ • 做市商      │  │ • 自进化     │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
│         └─────────────────┼─────────────────┘                │
│                           ▼                                  │
│              ┌────────────────────────┐                      │
│              │    Agent 交易助手层     │                      │
│              │  • 用户Agent          │                      │
│              │  • 套利Agent          │                      │
│              │  • 做市Agent          │                      │
│              │  • 趋势Agent          │                      │
│              └────────────────────────┘                      │
│                           ▼                                  │
│              ┌────────────────────────┐                      │
│              │      REST API 层       │                      │
│              │  • Flask REST         │                      │
│              │  • WebSocket实时推送   │                      │
│              └────────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

## 🧪 核心概念

### 量子叠加态并行（中华科学发现）

```
1. N态不同起点（不同初始权重）
2. 各态独立并行训练
3. 各态学到不同权重
4. 观测坍缩（合并所有态权重）
5. 最终模型含所有态知识
```

### 三平台策略（已有系统）

- Bitget / HTX / Gate.io 价差套利
- 捡乌龙指 + 做市策略
- 自适应风控引擎

## 📁 项目结构

```
/root/QNT/
├── core/           # 区块链核心
│   ├── block.py    # 区块结构
│   ├── chain.py    # 区块链引擎
│   └── contract.py # 智能合约（Token/Governance/NState）
├── exchange/       # 交易所
│   ├── orderbook.py # 订单簿
│   └── engine.py   # 撮合引擎
├── nstate/         # N态训练
│   └── pool.py     # 叠加态池
├── agents/         # Agent系统
│   └── base.py     # Arb/MM/Trend Agent
├── models/         # 预测模型
│   └── predictor.py
├── strategies/     # 交易策略
│   └── arbitrage.py
├── api/            # REST API
│   ├── app.py      # Flask应用
│   └── websocket.py # WebSocket服务
├── tests/          # 测试套件
│   ├── test_unit.py     # 单元测试（13项）
│   ├── test_integration.py # 集成测试（7项）
│   └── test_edge.py     # 边界测试（21项）
├── start.sh        # 一键启动
├── verify.sh       # 系统验证
├── PLAN.md         # 项目方案
└── README.md       # 本文档
```

## 🔧 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 语言 | Python | 3.11 |
| 深度学习 | PyTorch | 2.12.1 |
| NLP | Transformers | 5.5.0 |
| Web框架 | Flask | 3.1.3 |
| 测试 | pytest | 7.x |
| 数值计算 | NumPy | 1.24+ |

## 📈 测试结果

```
=== QNT 测试报告 ===

🧪 单元测试: 13 passed
🧪 集成测试: 7 passed  
🧪 边界测试: 21 passed
────────────────────────────
📊 总计: 41 passed, 0 failed

⏱️  执行时间: 0.23s
```

## 🎯 使用示例

### 1. 区块链交易

```python
from core.chain import QNTChain

chain = QNTChain(difficulty=2)
chain.state_ledger['Alice'] = 10000.0
chain.add_transaction('Alice', 'Bob', 500.0)
chain.mine_pending_transactions()

print(f"Block height: {chain.get_chain_info()['height']}")
print(f"Alice balance: {chain.get_balance('Alice')}")
```

### 2. 交易所撮合

```python
from exchange.engine import MatchingEngine

eng = MatchingEngine('QNT/USDT', fee_rate=0.001)
eng.set_balance('A', 'QNT', 500.0)
eng.set_balance('A', 'USDT', 10000.0)
eng.set_balance('B', 'QNT', 500.0)
eng.set_balance('B', 'USDT', 10000.0)

eng.submit_order('A', 'sell', 100, price=100.0)
eng.submit_order('B', 'buy', 80, price=100.0)

print(f"Trades: {len(eng.trades)}")
print(f"Spread: {eng.orderbook.get_spread_pct()}%")
```

### 3. N态训练

```python
from nstate.pool import SuperpositionPool
import numpy as np

pool = SuperpositionPool(num_states=4, weight_dim=5)

for i in range(10):
    pool.train_step(np.random.randn(5), np.random.rand())

collapse = pool.collapse()
print(f"Rounds: {pool.training_rounds}")
print(f"Best agent: {collapse['best_agent']}")
```

### 4. Agent决策

```python
from agents.base import ArbAgent

arb = ArbAgent(name='ArbBot')
decision = arb.think({'spread_pct': 0.08})
print(f"Action: {decision['decision']['action']}")
```

## 🌐 API接口

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/blockchain/status` | GET | 区块链状态 |
| `/api/blockchain/transaction` | POST | 添加交易 |
| `/api/blockchain/mine` | POST | 挖矿 |
| `/api/exchange/status` | GET | 交易所状态 |
| `/api/exchange/order` | POST | 提交订单 |
| `/api/nstate/train` | POST | N态训练 |
| `/api/nstate/collapse` | POST | 触发坍缩 |
| `/api/agent/think` | POST | Agent思考 |

## 📝 Git提交记录

```
7d3044f feat: 添加启动脚本和验证脚本
e5283f1 test: 边界测试41项全部通过
6c41af2 fix: 单元测试通过所有13项测试
90207a1 docs: 更新PLAN.md下一步计划
6374744 test: 集成测试7项全部通过
...
```

## 🔮 未来规划

- [ ] Phase 7: 分布式节点同步
- [ ] Phase 8: 跨链桥接
- [ ] Phase 9: DAO治理框架
- [ ] Phase 10: 生产环境部署

---

**Created:** 2026-08-18  
**Author:** 小蕊 (Agnes)  
**Version:** v0.1.0
