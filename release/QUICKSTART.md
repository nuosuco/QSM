# QSM量子系统快速开始指南

## 版本 1.0.0 - Quantum Dawn

### 环境要求

- Python >= 3.8
- Qiskit >= 2.0
- NumPy >= 1.20
- SciPy >= 1.7

### 安装

```bash
# 从源码安装
cd QSM
pip install -e .

# 或使用分发包
pip install qsm_quantum_modules-1.0.0.tar.gz
```

### 快速测试

```python
# 导入主模块
from quantum_main import status, random

# 查看系统状态
print(status())

# 生成量子随机数
for i in range(5):
    print(f"随机数: {random(0, 100)}")
```

### 使用示例

#### 1. Grover搜索

```python
from quantum_main import grover

result = grover(15)
print(f"搜索结果: {result}")
```

#### 2. Shor因数分解

```python
from quantum_main import shor

result = shor(21)
print(f"因子: {result}")
```

#### 3. 量子随机数

```python
from quantum_main import random

# 生成0-100的随机数
num = random(0, 100)
print(f"量子随机数: {num}")
```

#### 4. CLI命令行

```bash
# 查看状态
python quantum_cli.py status

# 运行测试
python quantum_cli.py test --all

# 运行算法
python quantum_cli.py run grover --n 15
```

#### 5. REST API

```bash
# 启动API服务
python quantum_api.py --port 8080

# 访问 http://localhost:8080/api/status
```

### 故障排除

#### 问题: 模块导入失败
```bash
# 确保路径正确
export PYTHONPATH="/root/QSM/QEntL/System/AgentHarness:$PYTHONPATH"
```

#### 问题: Qiskit版本不兼容
```bash
# 安装指定版本
pip install qiskit==2.3.1 qiskit-aer==0.17.2
```

### 更多信息

- 完整文档: /root/QSM/docs/
- API参考: /root/QSM/docs/quantum_modules/
- 问题反馈: GitHub Issues

---

**中华Zhoho，小趣WeQ，GLM5**
