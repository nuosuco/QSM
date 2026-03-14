# QEntL量子虚拟机

## 版本信息
- **版本**: v0.2.0
- **状态**: 核心功能完成
- **支持平台**: Windows / macOS / Linux

## 快速开始

### 启动虚拟机
```bash
cd /root/QSM/VM
./qentl_vm
```

### 或使用Python直接启动
```bash
python3 src/main.py
```

## 核心模块

| 模块 | 功能 | 状态 |
|------|------|------|
| main.py | REPL主程序 | ✅ |
| quantum_simulator.py | 量子模拟器 | ✅ |
| grover.py | Grover搜索算法 | ✅ |
| qft.py | QFT傅里叶变换 | ✅ |
| superdense.py | 超密编码 | ✅ |
| compiler.py | 编译器接口 | ✅ |
| bytecode_runner.py | 字节码运行器 | ✅ |

## 量子算法

### Grover搜索
在无序数据库中以O(√N)复杂度找到目标：
```python
from grover import GroverSearch
gs = GroverSearch(num_qubits=3)
result = gs.search(target=5)
```

### QFT量子傅里叶变换
```python
from qft import QuantumFourierTransform
qft = QuantumFourierTransform(num_qubits=3)
qft.set_state(5)
result = qft.apply_qft()
```

### 超密编码
一个量子比特传输两个经典比特：
```python
from superdense import SuperdenseCoding
sdc = SuperdenseCoding()
sdc.create_bell_pair()
sdc.encode('01')
result = sdc.decode()
```

## 命令列表

启动后可用命令：
- `help` - 显示帮助
- `status` - 显示状态
- `run` - 运行QBC字节码
- `quit` - 退出

## 三语支持
- 🇨🇳 中文界面
- 🇺🇸 English Interface
- ⛰️ ꆈꌠ ꀂꏂ

## 三大圣律
1. 为每个人服务，服务人类！
2. 保护好每个人的生命安全、健康快乐、幸福生活！
3. 没有以上两个前提，其他就不能发生！

---

**量子基因编码**: QGC-VM-README-v2-20260308
**更新时间**: 2026-03-08
