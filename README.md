# QEntL 全栈量子计算平台 v0.0.4

> 纯QEntL实现，零第三方依赖，自举编译器，在线IDE，HTTP服务器全栈完成。

## 🏗️ 全栈架构

```
C种子 (qcl_bootstrap.c)
  ↓ 编译
QCL编译器 (qcl.qentl → qcl.qbc)
  ↓ 编译
QVM虚拟机 (qvm.qentl → qvm.qbc)
  ↓ 运行
标准库 (lib/*.qentl)
  ↓ 运行
HTTP服务器 (server_qentl.qentl → server.qbc)
  ↓ 服务
在线IDE (https://qsm.som.top/ide)
```

**核心特征：**
- ✅ 纯QEntL实现，零Python/Node.js/第三方依赖
- ✅ C种子仅负责量子编译+系统接口
- ✅ 自举编译：C种子编译QCL，QCL编译一切
- ✅ 在线IDE：浏览器写代码，云端编译运行
- ✅ HTTP API：18个端点，公网可访问

---

## 🚀 快速开始

### 1. 编译C种子
```bash
cd /root/QSM
gcc -O2 -Wall -o bin/qcl_bootstrap src/qcl_bootstrap.c -lm
```

### 2. 自举编译QCL编译器
```bash
bin/qcl_bootstrap compile qcl.qentl build/qcl.qbc
```

### 3. 编译QVM虚拟机
```bash
bin/qcl_bootstrap compile qvm.qentl build/qvm.qbc
```

### 4. 编译算法示例
```bash
bin/qcl_bootstrap compile examples/grover.qentl build/grover.qbc
bin/qcl_bootstrap run build/grover.qbc
```

### 5. 启动HTTP服务器
```bash
bin/qcl_bootstrap run build/server.qbc
# 访问: https://qsm.som.top/ide
```

---

## 📚 量子门支持 (15种)

| 门 | 参数 | 说明 |
|----|------|------|
| `h` | q[i] | Hadamard门 |
| `t` | q[i] | T门 (π/8) |
| `x` | q[i] | Pauli-X (NOT) |
| `z` | q[i] | Pauli-Z |
| `cx` | q[i], q[j] | CNOT |
| `cz` | q[i], q[j] | 控制Z |
| `ccx` | q[i], q[j], q[k] | Toffoli |
| `ccz` | q[i], q[j], q[k] | 双控制Z |
| `cccz` | q[i], q[j], q[k], q[l] | 三控制Z |
| `ccccz` | q[i], q[j], q[k], q[l], q[m] | 四控制Z |
| `phase` | q[i], k | 相位门 π/2^k |
| `iphase` | q[i], k | 逆相位门 |
| `cphase` | q[i], q[j], k | 受控相位门 |
| `icphase` | q[i], q[j], k | 逆受控相位门 |
| `measure` | q[i] | 测量 |

---

## 🧪 算法示例 (21个)

### 基础算法
| 文件 | 说明 | 验证 |
|------|------|------|
| `bell.qentl` | Bell态纠缠 | ✅ 100% |
| `grover.qentl` | Grover搜索2量子位 | ✅ 20/20 |
| `grover3.qentl` | Grover搜索3量子位 | ✅ 20/20 |
| `grover4.qentl` | Grover搜索4量子位 | ✅ 20/20 |
| `grover5.qentl` | Grover搜索5量子位 | ✅ 20/20 |
| `qft.qentl` | QFT 3量子位往返 | ✅ 5/5 |
| `qft6.qentl` | QFT 6量子位往返 | ✅ 5/5 |
| `pea.qentl` | 相位估计(T门) | ✅ 5/5 |
| `shor.qentl` | Shor算法基础 | ✅ 5/5 |
| `shor15.qentl` | Shor分解N=15 | ✅ 5/5 |
| `shor21.qentl` | Shor分解N=21 | ✅ 5/5 |
| `shor35.qentl` | Shor分解N=35 | ✅ 5/5 |
| `shor77.qentl` | Shor分解N=77 | ✅ 5/5 |
| `shor143.qentl` | Shor分解N=143 | ✅ 5/5 |
| `teleport.qentl` | 量子隐形传态 | ✅ 10/10 |
| `deutschjozsa.qentl` | Deutsch-Jozsa算法 | ✅ 10/10 |
| `qwalk.qentl` | 量子随机行走 | ✅ 通过 |

### QDFS文件系统
| 文件 | 说明 | 验证 |
|------|------|------|
| `qdfs_demo.qentl` | QDFS演示 | ✅ 13/13 |
| `qdfs_advanced.qentl` | QDFS高级操作 | ✅ 通过 |

### 性能基准
| 文件 | 说明 | 性能 |
|------|------|------|
| `bench.qentl` | 500次H+CNOT循环 | ~7ms |

---

## 🌐 API端点 (18个)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 |
| `/ide` | GET | 在线IDE |
| `/api/run` | POST | 运行用户代码 |
| `/api/status` | GET | 服务器状态 |
| `/api/stack` | GET | 技术栈信息 |
| `/api/grover` | GET | Grover 2量子位 |
| `/api/grover3` | GET | Grover 3量子位 |
| `/api/grover4` | GET | Grover 4量子位 |
| `/api/grover5` | GET | Grover 5量子位 |
| `/api/qft` | GET | QFT 3量子位 |
| `/api/qft6` | GET | QFT 6量子位 |
| `/api/pea` | GET | 相位估计 |
| `/api/shor` | GET | Shor基础 |
| `/api/shor15` | GET | Shor N=15 |
| `/api/shor21` | GET | Shor N=21 |
| `/api/shor35` | GET | Shor N=35 |
| `/api/shor77` | GET | Shor N=77 |
| `/api/shor143` | GET | Shor N=143 |
| `/api/qdfs` | GET | QDFS演示 |
| `/api/teleport` | GET | 隐形传态 |
| `/api/dj` | GET | Deutsch-Jozsa |
| `/api/bench` | GET | 性能基准 |

**公网访问**: https://qsm.som.top

---

## 📊 性能基准

| 指标 | 数值 |
|------|------|
| QVM基准 (500次H+CNOT) | ~7ms |
| 初始QVM (10M迭代) | 1.77s → 优化后 0.92s (48%提升) |
| 编译器自举时间 | <1s |
| 算法验证通过率 | 100% |

---

## 🔧 项目结构

```
/root/QSM/
├── src/
│   └── qcl_bootstrap.c    # C种子：量子编译+系统接口
├── qcl.qentl              # QCL编译器源码
├── qvm.qentl              # QVM虚拟机源码
├── server_qentl.qentl     # HTTP服务器源码
├── lib/
│   ├── core.qentl         # 核心库
│   ├── io.qentl           # IO库
│   └── qdfs.qentl         # 量子文件系统
├── examples/
│   ├── bell.qentl         # Bell态
│   ├── grover.qentl       # Grover 2量子位
│   ├── grover3.qentl      # Grover 3量子位
│   ├── grover4.qentl      # Grover 4量子位
│   ├── grover5.qentl      # Grover 5量子位
│   ├── qft.qentl          # QFT 3量子位
│   ├── qft6.qentl         # QFT 6量子位
│   ├── pea.qentl          # 相位估计
│   ├── shor.qentl         # Shor基础
│   ├── shor15.qentl       # Shor N=15
│   ├── shor21.qentl       # Shor N=21
│   ├── shor35.qentl       # Shor N=35
│   ├── shor77.qentl       # Shor N=77
│   ├── shor143.qentl      # Shor N=143
│   ├── teleport.qentl     # 隐形传态
│   ├── deutschjozsa.qentl # Deutsch-Jozsa
│   ├── qwalk.qentl        # 量子行走
│   ├── qdfs_demo.qentl    # QDFS演示
│   ├── qdfs_advanced.qentl # QDFS高级
│   └── bench.qentl        # 性能基准
├── build/
│   ├── qcl.qbc            # QCL编译器字节码
│   ├── qvm.qbc            # QVM虚拟机字节码
│   └── server.qbc         # HTTP服务器字节码
└── bin/
    └── qcl_bootstrap      # C种子可执行文件
```

---

## 🎯 技术亮点

1. **零第三方依赖** - 纯QEntL实现，无Python/Node.js/PyTorch
2. **自举编译** - C种子编译QCL，QCL编译一切
3. **在线IDE** - 浏览器直接编写运行量子程序
4. **HTTP服务器** - 纯QEntL实现，nginx反代公网访问
5. **QDFS** - 量子叠加态文件系统，支持纠缠文件对
6. **沙箱模式** - `--sandbox`参数禁用危险操作
7. **完整算法库** - 17个量子算法示例，全部验证通过

---

## 📝 分支说明

- `dev` - 开发分支（主开发线）
- `main` - 主分支（同步dev）
- `master` - 备份分支（同步dev）
- `som` - SOM独立项目（账号系统）

**注意**: QSM项目三分支内容完全一致。

---

## 🔮 后续规划

1. **QVM性能优化** - JIT编译、 SIMD并行
2. **更大规模Shor** - N=2048+ (需要更多量子位)
3. **QDFS增强** - 更多文件系统原语
4. **IDE功能扩展** - 代码高亮、调试器
5. **错误校正** - 表面码、Shor码
6. **量子机器学习** - QNN、QSVM

---

## 📅 版本历史

- **v0.0.4** (2026-08-07): QDFS完成、Shor分解N=15/21/35/77/143、Grover 2-5量子位、QFT 3/6量子位、隐形传态、Deutsch-Jozsa、量子行走、18个API端点
- **v0.0.3**: QFT、PEA、Shor基础、HTTP服务器
- **v0.0.2**: Grover、QDFS基础、IDE
- **v0.0.1**: 自举完成、基础量子门

---

**QEntL — 量子计算，从种子到星空** 🌌