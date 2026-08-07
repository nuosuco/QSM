# QEntL 全栈量子计算平台 v0.0.5

> 纯QEntL实现，零第三方依赖，自举编译器，在线IDE，HTTP服务器全栈完成。
> 运行于 https://qsm.som.top (QOS平台)

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
- ✅ 22个量子算法示例，全部验证通过

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

### 4. 编译HTTP服务器
```bash
bin/qcl_bootstrap compile server_qentl.qentl build/server.qbc
bin/qcl_bootstrap run build/server.qbc
# 访问: https://qsm.som.top
```

### 5. 运行算法示例
```bash
bin/qcl_bootstrap run build/grover4.qbc
bin/qcl_bootstrap run build/shor15.qbc
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

## 🧪 算法示例 (22个)

### 量子搜索
| 文件 | 说明 | 验证 |
|------|------|------|
| `grover.qentl` | Grover 2量子位 | ✅ 20/20 |
| `grover3.qentl` | Grover 3量子位 | ✅ 20/20 |
| `grover4.qentl` | Grover 4量子位 | ✅ 20/20 |
| `grover5.qentl` | Grover 5量子位 (CCCCZ) | ✅ 20/20 |
| `grover_opt.qentl` | Grover 3次最优迭代 | ✅ 20/20 |

### 量子傅里叶变换
| 文件 | 说明 | 验证 |
|------|------|------|
| `qft.qentl` | QFT 3量子位往返 | ✅ 5/5 |
| `qft6.qentl` | QFT 6量子位往返 | ✅ 5/5 |

### 量子估计
| 文件 | 说明 | 验证 |
|------|------|------|
| `pea.qentl` | 相位估计(T门) | ✅ 5/5 |

### Shor因子分解
| 文件 | 说明 | 验证 |
|------|------|------|
| `shor.qentl` | Shor周期查找 | ✅ 5/5 |
| `shor15.qentl` | N=15=3×5 | ✅ 5/5 |
| `shor21.qentl` | N=21=3×7 | ✅ 5/5 |
| `shor35.qentl` | N=35=5×7 | ✅ 5/5 |
| `shor77.qentl` | N=77=7×11 | ✅ 5/5 |
| `shor143.qentl` | N=143=11×13 | ✅ 5/5 |
| `shor_qft.qentl` | QFT周期查找版 | ✅ 5/5 |

### 量子协议
| 文件 | 说明 | 验证 |
|------|------|------|
| `teleport.qentl` | 量子隐形传态 | ✅ 10/10 |
| `bb84.qentl` | BB84量子密钥分发 | ✅ 10/10 |
| `deutschjozsa.qentl` | Deutsch-Jozsa算法 | ✅ 10/10 |
| `qwalk.qentl` | 量子随机行走K3 | ✅ 通过 |

### 量子演示
| 文件 | 说明 | 验证 |
|------|------|------|
| `superposition.qentl` | 叠加态测量 | ✅ 通过 |
| `ghz.qentl` | GHZ纠缠态 | ✅ 通过 |
| `bell_pair.qentl` | 双Bell态对 | ✅ 通过 |
| `qclustering.qentl` | 量子聚类 | ✅ 通过 |
| `qoptimization.qentl` | 量子优化 | ✅ 20/20 |
| `qnn_demo.qentl` | 量子神经网络 | ✅ 通过 |

### QDFS文件系统
| 文件 | 说明 | 验证 |
|------|------|------|
| `qdfs_demo.qentl` | QDFS演示 | ✅ 13/13 |
| `qdfs_advanced.qentl` | QDFS高级操作 | ✅ 通过 |

### 性能基准
| 文件 | 说明 | 性能 |
|------|------|------|
| `bench.qentl` | 500次H+CNOT循环 | ~6ms |

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
| `/api/grover_opt` | GET | Grover优化版 |
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
| QVM基准 (500次H+CNOT) | ~6ms |
| 初始QVM (10M迭代) | 1.77s → 优化后 0.92s (48%提升) |
| 编译器自举时间 | <1s |
| 算法验证通过率 | 100% (25/25) |

---

## 🔧 项目结构

```
/root/QSM/
├── src/qcl_bootstrap.c    # C种子：量子编译+系统接口
├── qcl.qentl              # QCL编译器源码
├── qvm.qentl              # QVM虚拟机源码
├── server_qentl.qentl     # HTTP服务器源码
├── lib/
│   ├── core.qentl         # 核心库
│   ├── io.qentl           # IO库
│   ├── qdfs.qentl         # 量子文件系统
│   └── qnn.qentl          # 量子神经网络
├── examples/              # 22个算法示例
├── build/                 # 编译产物
├── bin/qcl_bootstrap      # C种子可执行文件
└── docs/                  # 开发文档
```

---

## 🎯 技术亮点

1. **零第三方依赖** - 纯QEntL实现，无Python/Node.js/PyTorch
2. **自举编译** - C种子编译QCL，QCL编译一切
3. **在线IDE** - 浏览器直接编写运行量子程序
4. **HTTP服务器** - 纯QEntL实现，nginx反代公网访问
5. **QDFS** - 量子叠加态文件系统，支持纠缠文件对
6. **沙箱模式** - `--sandbox`参数禁用危险操作
7. **完整算法库** - 22个量子算法示例，全部验证通过

---

## 📝 分支说明

- `dev` - 开发分支（主开发线）
- `main` - 主分支（同步dev）
- `master` - 备份分支（同步dev）
- `som` - SOM独立项目（账号系统）

---

## 🔮 后续规划

1. **QNS量子神经网络** - 彝文4120字三语训练框架
2. **四大模型** - QSM(主)/SOM(经济)/WeQ(社交)/Ref(自反省)
3. **三种部署** - 终端QOS / 虚拟机 / Web QOS (qsm.som.top)
4. **QVM性能优化** - JIT编译、SIMD并行
5. **IDE功能扩展** - 代码高亮、调试器
6. **量子机器学习** - QNN、QSVM、Q聚类

---

## 📅 版本历史

- **v0.0.5** (2026-08-07): QNN/QSV/量子聚类/量子优化、BB84、GHZ、Bell态对、22个算法示例、25/25验证通过
- **v0.0.4** (2026-08-07): QDFS完成、Shor分解N=15/21/35/77/143、Grover 2-5量子位、QFT 3/6量子位、隐形传态、Deutsch-Jozsa、量子行走、18个API端点
- **v0.0.3**: QFT、PEA、Shor基础、HTTP服务器
- **v0.0.2**: Grover、QDFS基础、IDE
- **v0.0.1**: 自举完成、基础量子门

---

**QEntL — 量子计算，从种子到星空** 🌌