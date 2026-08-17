# QNT 量子叠加网络 - 运行手册

## 快速启动

```bash
cd /root/QNT
bash start.sh
```

## 项目结构

```
QNT/
├── core/           # 区块链核心
│   ├── block.py    # 区块结构
│   ├── chain.py    # 链管理
│   └── contract.py # 智能合约
├── exchange/       # 交易所
│   ├── engine.py   # 撮合引擎
│   └── orderbook.py # 订单簿
├── nstate/         # N态训练
│   └── pool.py     # 叠加池
├── agents/         # Agent系统
│   ├── base.py     # Agent基类
│   └── strategies.py # 策略实现
├── market/         # 市场数据
│   └── feeds.py    # 行情生成
├── database/       # 持久化
│   └── persistent.py
├── api/            # REST API
│   └── app.py      # Flask应用
├── tests/          # 测试套件
│   ├── test_unit.py
│   ├── test_integration.py
│   ├── test_edge.py
│   ├── test_performance.py
│   ├── test_e2e.py
│   └── test_api.py
├── main.py         # 系统入口
├── cli.py          # CLI工具
├── start.sh        # 启动脚本
└── PLAN.md         # 项目规划
```

## 核心功能

### 1. 区块链
- 工作量证明(PoW)共识
- 智能合约支持
- QNT Token标准

### 2. 交易所
- 限价单/市价单
- 撮合引擎
- 手续费系统

### 3. N态训练
- 多态并行训练
- 观测坍缩机制
- 性能评估

### 4. Agent系统
- ArbAgent (套利)
- MarketMakerAgent (做市)
- TrendAgent (趋势)
- GridTradingAgent (网格)
- MomentumAgent (动量)
- MeanReversionAgent (均值回归)
- VolumeProfileAgent (量能分析)

## CLI命令

```bash
# 区块链
python3 cli.py blockchain --action status
python3 cli.py blockchain --action mine

# 交易所
python3 cli.py exchange --action status
python3 cli.py exchange --action order --account Alice --side buy --quantity 10 --price 100

# N态训练
python3 cli.py nstate --action train --rounds 100
python3 cli.py nstate --action collapse

# Agent
python3 cli.py agents --action list
```

## API端点

```
GET  /api/health
GET  /api/blockchain/status
POST /api/blockchain/transaction
POST /api/blockchain/mine
GET  /api/exchange/status
POST /api/exchange/order
GET  /api/exchange/trades
POST /api/nstate/train
POST /api/nstate/collapse
GET  /api/nstate/status
POST /api/agent/think
```

## 测试

```bash
# 全部测试
python3 -m pytest tests/ -v

# 单元测试
python3 -m pytest tests/test_unit.py -v

# 集成测试
python3 -m pytest tests/test_integration.py -v

# 边缘测试
python3 -m pytest tests/test_edge.py -v

# 性能测试
python3 -m pytest tests/test_performance.py -v

# API测试
python3 -m pytest tests/test_api.py -v
```

## 当前版本

- **版本**: v0.1.0
- **状态**: 基础框架完成
- **测试**: 70 passed
- **代码**: 42 Python文件, 4736行
