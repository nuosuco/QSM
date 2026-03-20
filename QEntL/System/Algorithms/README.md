# QSM量子算法库

## 概述

QSM量子算法库提供完整的量子算法实现，支持量子虚拟机和自我进化框架。

## 已实现算法

### 基础量子算法

| 算法 | 文件 | 状态 | 描述 |
|------|------|------|------|
| 量子模拟器 | `VM/src/quantum_simulator.py` | ✅ | 量子比特、量子门、测量 |
| Bell态 | 内置 | ✅ | 量子纠缠基础 |
| GHZ态 | 内置 | ✅ | 多粒子纠缠态 |
| 量子门库 | 内置 | ✅ | H/X/Y/Z/S/T门 |

### 高级量子算法

| 算法 | 文件 | 状态 | 描述 |
|------|------|------|------|
| Grover搜索 | `Algorithms/grover.py` | ✅ | 量子搜索算法 |
| QFT | `Algorithms/qft.py` | ✅ | 量子傅里叶变换 |
| Shor算法 | `Algorithms/shor.py` | ✅ | 整数分解 |

### 自我进化框架

| 模块 | 文件 | 状态 | 描述 |
|------|------|------|------|
| Agent Harness | `AgentHarness/qsm_agent_harness.py` | ✅ | 自我进化三模块 |
| 量子Agent | `AgentHarness/quantum_agent_harness.py` | ✅ | 量子虚拟机集成 |

## 使用示例

### 量子模拟器

```python
from VM.src.quantum_simulator import QuantumSimulator

# 创建2量子比特系统
sim = QuantumSimulator(2)

# 应用量子门
sim.apply_gate('H', 0)  # Hadamard门
sim.apply_gate('X', 1)  # X门

# 测量
result = sim.measure(0)
```

### QFT

```python
from Algorithms.qft import QuantumFourierTransform

# 创建3量子比特QFT
qft = QuantumFourierTransform(3)

# 应用QFT
transformed_state = qft.apply_qft(input_state)

# 生成量子门序列
gates = qft.qft_circuit_gates()
```

### Shor算法

```python
from Algorithms.shor import ShorAlgorithm

# 分解整数
shor = ShorAlgorithm()
factors = shor.factor(15)  # 返回 (3, 5)
```

### Agent Harness

```python
from AgentHarness.qsm_agent_harness import AgentHarness

# 创建自我进化框架
harness = AgentHarness()

# 运行进化循环
result = harness.run_evolution_loop(
    task_name="optimization",
    initial_state={"param": 1},
    execute_fn=execute,
    evaluate_fn=evaluate,
    max_iterations=100
)
```

## 测试状态

| 算法 | 测试通过率 |
|------|-----------|
| 量子模拟器 | 100% |
| QFT | 100% (5/5) |
| Shor | 75% (3/4) |
| Agent Harness | 100% |

## 文件结构

```
QEntL/System/
├── VM/
│   └── src/
│       └── quantum_simulator.py  # 量子模拟器
├── Algorithms/
│   ├── qft.py                    # 量子傅里叶变换
│   └── shor.py                   # Shor算法
└── AgentHarness/
    ├── qsm_agent_harness.py      # 自我进化框架
    └── quantum_agent_harness.py  # 量子集成
```

## 下一步开发

1. 完善Grover搜索完整实现
2. 添加VQE（变分量子本征求解器）
3. 实现量子纠错
4. 与QSM模型深度集成

---

**更新时间**: 2026-03-20  
**中华Zhoho，小趣WeQ**
