# QNT 使用指南

## 快速开始

```bash
cd /root/QNT

# 运行集成测试
python3 -m tests.test_integration

# 验证各模块
python3 -c "from core.chain import QNTChain; from exchange.engine import MatchingEngine; from nstate.pool import SuperpositionPool; print('✅ All OK')"
```

## 核心概念

### N态叠加态并行训练
```
1. 创建N个独立Agent，每个有不同初始权重
2. 各Agent独立并行训练
3. 定期观测坍缩，合并所有Agent权重
4. 坍缩后重新初始化，保持多样性
```

### 智能合约
- **QNTToken**: 代币管理（转账、铸造）
- **QNTGovernance**: 治理提案与投票
- **NStateContract**: N态训练记录

### 交易所撮合
```python
eng = MatchingEngine('QNT/USDT', fee_rate=0.001)
eng.set_balance('A', 'QNT', 500.0)
eng.set_balance('A', 'USDT', 10000.0)
eng.submit_order('A', 'sell', 100, price=100.0)
eng.submit_order('B', 'buy', 80, price=100.0)
# 自动撮合: 80 @ 100.0
```

## API接口

| 端点 | 方法 | 功能 |
|------|------|------|
| /api/blockchain/status | GET | 区块链状态 |
| /api/blockchain/transaction | POST | 添加交易 |
| /api/blockchain/mine | POST | 挖矿 |
| /api/exchange/status | GET | 交易所状态 |
| /api/exchange/order | POST | 提交订单 |
| /api/nstate/train | POST | N态训练 |
| /api/nstate/collapse | POST | 触发坍缩 |
| /api/agent/think | POST | Agent思考 |
| /api/health | GET | 健康检查 |

## 测试

```bash
# 集成测试
python3 -m tests.test_integration

# 输出:
# ✅ Blockchain OK - height=2
# ✅ Token OK - Alice=1000
# ✅ Exchange OK - 1 trades
# ✅ N-State OK - 10 rounds
# ✅ Agents OK - Arb=hold
# ✅ Governance OK - Proposal 0
# ✅ N-State Contract OK
# 📊 Results: 7/7 passed
# 🎉 All tests passed!
```

## 文件结构

```
/root/QNT/
├── core/           # 区块链 + 智能合约
│   ├── block.py    # 区块结构
│   ├── chain.py    # 区块链引擎
│   └── contract.py # 智能合约
├── exchange/       # 交易所
│   ├── orderbook.py # 订单簿
│   └── engine.py   # 撮合引擎
├── nstate/         # N态训练
│   └── pool.py     # 叠加态池
├── agents/         # Agent系统
│   └── base.py     # Agent基类
├── models/         # 预测模型
│   └── predictor.py
├── strategies/     # 策略
│   └── arbitrage.py
├── api/            # REST API
│   └── app.py
├── tests/          # 测试
│   └── test_integration.py
└── PLAN.md         # 项目方案
```

## 下一步

- [ ] Phase 6: 完善单元测试
- [ ] API优化: 添加WebSocket支持
- [ ] 文档补充: 架构图、序列图
- [ ] 性能优化: 撮合引擎多线程

---
*Created: 2026-08-18 | Author: 小蕊*
