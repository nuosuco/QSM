# QEntL 全栈构建与跑通方案

> 版本: 3.0.0
> 日期: 2026-07-11
> 状态: Phase1完成

---

## 核心认知（必须首先理解！）

### 命名纠正

- **qcl_bootstrap.c** = **引导器**（不是解释器）
  - 一个C文件就能完成 `--compile` 编译QEntL源码为QBC
  - 模式1：`./bin/qcl_bootstrap QCL_main.qentl` → 解释执行QEntL源码
  - 模式2：`./bin/qcl_bootstrap --compile input.qentl output.qbc` → **直接编译为字节码**
  - 不需要加载任何QEntL模块就能编译
- **QCL** = **编译器**（不是引导器）
  - 源码是 `QCL_main.qentl` + `QCL_compiler/*.qentl`（共7个文件）
  - QCL源码保留不删，但不再作为运行组件加载
- **qvm_bootstrap.c** = **C语言启动器**（加载器）
  - 加载 `.qbc` 字节码文件运行

### 所有系统文件必须通过 import 链链接成系统

单个 `.qentl` 或 `.qbc` 文件独立运行没用。系统必须通过 import 链链接：
- **QCL系统**：QCL_main.qentl(入口) import 6个QCL_compiler模块 → 链接成系统
- **QVM系统**：QVM_entry_full.qentl(入口) import QVM_entry.qentl import QVM.qentl → 链接成系统
- **编译出的 .qbc 也要保持链接结构**
- **QVM 必须能实际加载被 import 的 .qbc 文件**

### QDFS是整个QSM的基础

QDFS不只是文件系统——它是**量子叠加态并行运算与运行的基础**：
- 装文件、加载数据
- 所有系统叠加态并行运算的底层支撑
- 没有QDFS，QNS没有数据可训练，四大模型没有数据可运行

**依赖链不能乱：QDFS → QNS → 四大模型**

---

## 一、自举链（八阶段）

### 阶段流程总览

```
阶段1: C语言引导器(qcl_bootstrap.c) 编译量子指令子集
    ↓
阶段2: 引导器启动 QCL编译器(QEntL源码，7个.qentl文件)
    ↓
阶段3: QCL编译器编译 QCL与QVM的QEntL源码 → 生成各数个.qbc文件
    ↓
阶段4: C语言启动器(qvm_bootstrap.c) 加载QVM(数个.qbc文件) 运行 → QEntL环境形成
    ↓
阶段5: QCL编译器(数个.qbc文件) 在QEntL环境中运行 → 编译所有QEntL源码
    ↓
阶段6: QDFS/QNS/四大模型(各数个.qbc文件) 在QEntL环境中运行
         QNS以QDFS为基础，四大模型以QNS为基础
    ↓
阶段7: QNS训练彝文等数据，模型测试成功，更新web桌面量子助手API
    ↓
阶段8: QEntL三种部署
```

### 各阶段详细说明

#### 阶段1: C语言引导器编译量子指令子集

**组件**: `src/qcl_bootstrap.c`（编译为 `bin/qcl_bootstrap`）

**职责**: 单个C文件，编译QEntL源码为QBC字节码

**支持指令**: init / H / X / Y / Z / T / S / CNOT / MEASURE / PRINT / STOP / EXIT / JUMP 等量子指令集 + import / def / if / while / var / 类型定义 等高级语法

**编译模式**:
```bash
# 单文件编译
cd /root/QSM && bin/qcl_bootstrap --compile QCL_main.qentl build/compiled_qcl/QCL_main.qbc

# 批量编译
cd /root/QSM/QCL_compiler && for f in *.qentl; do
  ../bin/qcl_bootstrap --compile $f ../build/compiled_qcl/${f%.qentl}.qbc
done
```

**编译产物**: 无头raw opcodes格式，QVM从位置0读取

---

#### 阶段2: 引导器启动 QCL编译器

**组件**: QCL编译器源码（7个QEntL文件）

**QCL编译器包含**（6个模块 + 1个入口）:
| 文件 | 行数 | 功能 |
|------|------|------|
| QCL_main.qentl | ~457 | 入口、量子电路执行、编译器新建/扫描/编译 |
| QCL_compiler/qcl_opcodes.qentl | 240 | 68个操作码常量表 |
| QCL_compiler/qcl_lexer.qentl | 730 | 70个token类型，词法分析 |
| QCL_compiler/qcl_parser.qentl | 618 | 15个函数，量子指令解析 |
| QCL_compiler/qcl_parser_high.qentl | 1,258 | 39个函数，高级语法解析 |
| QCL_compiler/qcl_bootstrap_phase2.qentl | 735 | 阶段2引导（def函数定义编译） |
| QCL_compiler/qcl_compiler_phase2.qentl | 24 | 阶段2编译器入口 |

**import链**: QCL_main.qentl → import 6个QCL_compiler模块 → 链接成完整QCL编译器系统

**核心逻辑**: QCL编译器 = QCL本身。第一次没有.qbc，所以用C引导器启动QCL源码运行。

**验证命令**:
```bash
cd /root/QSM && bin/qcl_bootstrap build/compiled_qcl/QCL_main.qbc
# 预期：exit_code=0，18门量子操作，import链加载所有模块
```

---

#### 阶段3: QCL编译器编译 QCL与QVM的QEntL源码 → 各数个.qbc文件

**这是自举的关键步骤**

QCL编译器源码运行成功后，编译：
1. **编译自己**（QCL源码）→ QCL.qbc（数个文件）
   - QCL_main.qentl → QCL_main.qbc
   - 6个QCL_compiler模块 → 各.qbc文件
2. **编译QVM源码** → QVM.qbc（数个文件）
   - QVM_entry_full.qentl → QVM_entry_full.qbc
   - QVM_entry.qentl → QVM_entry.qbc
   - QVM.qentl → QVM.qbc

**输出**: QCL和QVM的 .qbc 字节码集合，通过import链链接

**关键**: 这是自举的核心。有了.qbc，以后全部用qbc编译，不再需要C引导器编译模式。

---

#### 阶段4: C语言启动器加载QVM运行 → QEntL环境形成

**组件**: `src/qvm_bootstrap.c`（编译为 `bin/qvm_bootstrap`）

**职责**: 加载QVM.qbc（数个文件），启动量子虚拟机，形成QEntL运行环境

**import链加载**: QVM_entry_full.qbc → import QVM_entry.qbc → import QVM.qbc
- 3比特电路执行 → 模块结束返回父模块
- 8比特电路执行 → 模块结束返回父模块
- 12比特电路执行 → 程序退出

**编译命令**:
```bash
cd /root/QSM && gcc -std=gnu99 -O2 -o bin/qvm_bootstrap src/qvm_bootstrap.c -lm -mcmodel=medium
```

**执行**:
```bash
cd /root/QSM && bin/qvm_bootstrap build/compiled_qvm/QVM_entry_full.qbc
```

**结果**: QEntL环境形成。从此以后全部用qbc，不再需要C引导器。

**Phase1验证目标（2026-07-11达成）**:
- ✅ QVM退出0，18门量子操作全部正确执行
- ✅ import链加载所有模块（114处跳过函数体）
- ✅ 2126个高级opcode处理完成
- ✅ 调试输出已全部移除

---

#### 阶段5: QCL编译器在QEntL环境中运行

**组件**: QCL编译器（数个.qbc文件，即自举阶段生成的QCL.qbc）

**职责**: 在QEntL环境中运行，编译所有QEntL源码

**输入**: 所有 .qentl 源文件

**输出**: 完整的 .qbc 字节码集合

**关键**: 从此阶段开始，全部用qbc。C引导器使命完成，不再需要。

---

#### 阶段6: QDFS/QNS/四大模型在QEntL环境中运行

**组件及依赖关系**:
```
QDFS(数个.qbc文件) → QNS(数个.qbc文件) → 四大模型(数个.qbc文件)
```

| 系统 | 目录 | 说明 |
|------|------|------|
| QDFS（量子动态文件系统） | QEntL/System/Kernel/filesystem/ | 量子叠加态并行运算与运行的基础 |
| QNS（量子神经网络系统） | QEntL/System/Kernel/neural/ | 以QDFS为基础，加载数据训练 |
| 四大模型 | QEntL/Models/ | 以QNS为基础 |
| └ QSM | QEntL/Models/QSM/ | 量子叠加态模型 |
| └ SOM | QEntL/Models/SOM/ | 自组织映射模型 |
| └ WeQ | QEntL/Models/WeQ/ | 社交通信模型 |
| └ Ref | QEntL/Models/Ref/ | 自省参考模型 |

**依赖链不能乱**: QDFS → QNS → 四大模型

---

#### 阶段7: QNS训练彝文等数据

**组件**: QNS（数个.qbc文件）

**任务**: 训练彝文等数据，模型测试成功

**输出**: 更新web桌面的量子助手API

**训练数据**: `data/` 目录下51,899条彝文数据

---

#### 阶段8: QEntL三种部署

**三种部署模式**:

| 部署方式 | 说明 | 适用场景 |
|---------|------|---------|
| **应用部署** | QEntL应用程序解压即用 | 主要方式，绿色软件，无需安装 |
| **操作系统部署** | QEntL操作系统ISO镜像 | 需要引导程序/分区管理/驱动安装 |
| **跨平台部署** | 支持5大经典+3种量子 | 运行时根据平台自动适配 |

**经典5大平台**:
| 平台 | 架构 | 格式 |
|------|------|------|
| Windows | x86_64/ARM64 | PE |
| iOS | ARM64 | Mach-O |
| Android | ARM64 | ELF |
| 鸿蒙 | ARM64 | ELF |
| Linux | x86_64/ARM64 | ELF |

**量子3种部署方式**:
| 方式 | 实现 | 说明 |
|------|------|------|
| 开发部署 | QVM软件模拟 | 本地CPU模拟量子运算 |
| 生产部署 | 云端QPU API | 网络调用QPU服务 |
| 专用部署 | 量子协处理器 | 直接调用硬件量子设备 |

---

## 二、文件结构

```
/root/QSM/
├── src/
│   ├── qcl_bootstrap.c      # C语言引导器（阶段1-3）
│   └── qvm_bootstrap.c      # C语言启动器（阶段4）
├── bin/
│   ├── qcl_bootstrap        # 编译后的引导器
│   └── qvm_bootstrap        # 编译后的启动器
├── QCL_main.qentl          # QCL编译器入口
├── QCL_compiler/            # QCL编译器模块（6个.qentl）
│   ├── qcl_opcodes.qentl
│   ├── qcl_lexer.qentl
│   ├── qcl_parser.qentl
│   ├── qcl_parser_high.qentl
│   ├── qcl_bootstrap_phase2.qentl
│   └── qcl_compiler_phase2.qentl
├── QVM.qentl               # QVM源码（3个文件）
├── QVM_entry.qentl
├── QVM_entry_full.qentl
├── QEntL/                    # QEntL全栈源码
│   ├── System/
│   │   ├── Kernel/
│   │   │   ├── filesystem/  # QDFS（阶段6）
│   │   │   └── neural/      # QNS（阶段6/7）
│   │   ├── Platform/        # 经典5平台（8个文件）
│   │   └── Deployment/      # 量子3部署（5个文件）
│   ├── Models/               # 四大模型（阶段6）
│   │   ├── QSM/
│   │   ├── SOM/
│   │   ├── WeQ/
│   │   └── Ref/
│   └── ...248个.qentl文件
├── build/
│   ├── compiled_qcl/        # QCL编译输出（7个.qbc）
│   ├── compiled_qvm/        # QVM编译输出（3个.qbc）
│   └── ...完整编译产物
└── data/                     # 训练数据
```

---

## 三、核心原则

1. **所有系统文件必须通过import链链接成系统**
   - QCL系统：1+6文件链接
   - QVM系统：1+2文件链接
   - 编译出的.qbc也要保持链接结构

2. **C语言只是引导/启动**
   - `src/qcl_bootstrap.c` — 引导器（编译QEntL源码为QBC）
   - `src/qvm_bootstrap.c` — 启动器（加载QBC，执行）
   - 自举完成后C引导器退场，全部用qbc

3. **QCL = 编译器（不是引导器）**
   - 源码是QCL_main.qentl + 6个模块文件
   - 文件名"qcl_bootstrap"仅代表这是C文件版的自举工具

4. **QDFS是QSM整个系统的基础**
   - 所有量子叠加态运算的底层支撑
   - 没有QDFS，QNS没有数据可训练

5. **依赖链不可逆**
   - QDFS → QNS → 四大模型
   - 必须按顺序构建验证

6. **分配置编译**
   - MAX_LINE_LEN=8192（回退值，防止BSS溢出）
   - `-mcmodel=medium`（地址空间大模型）
   - 编译产物：无头raw opcodes，QVM从位置0读取

---

## 四、Phase1验证结果（2026-07-11）

| 验证项 | 状态 | 说明 |
|-------|------|------|
| 引导器编译QCL源码 | ✅ | 7个文件全部编译成功，3217+KB |
| 引导器编译QVM源码 | ✅ | 3个文件全部编译成功 |
| QVM加载QCL_main.qbc | ✅ | exit=0，18门量子操作正确 |
| import链加载所有模块 | ✅ | 6个QCL_compiler模块全部链接 |
| 函数体扫描 | ✅ | 114处跳过函数体完全正确 |
| 跨模块func_nest_depth | ✅ | 保存/恢复机制验证通过 |
| OP_PUSH_CONST_STR格式 | ✅ | 4B(off+len)格式统一 |
| 调试输出移除 | ✅ | 天量printf已全部清理 |
| OP_TYPE_DEF跳转 | ✅ | 加入skip列表避免失步 |
| OP_FUNC_CALL_STMT跳过 | ✅ | import时跳过函数调用 |
| OP_LOAD_VAR对齐 | ✅ | 33号操作码统一 |

### 已知遗留问题

- qcl_parser_high.qbc 中字符串含字节103('g')被误识别为OP_FUNC_END，导致少数函数depth为负
- QCL编译器（7个.qbc文件）在QVM上完整运行尚未验证（需进入阶段5）

---

## 五、里程碑跟踪

| 阶段 | 状态 | 说明 |
|------|------|------|
| ✅ 阶段1 | 完成 | qcl_bootstrap.c 编译模式，43个OP_定义 |
| ✅ 阶段2 | 完成 | 7个QEntL源码通过import链链接成系统 |
| ✅ 阶段3 | Phase1完成 | QCL+QVM全部编译为QBC，QVM运行exit=0 |
| ⏳ 阶段4 | 验证中 | QVM加载QCL_main.qbc成功，需完整验证 |
| ⬜ 阶段5 | 待实现 | QCL.qbc在QVM上运行 |
| ⬜ 阶段6 | 待实现 | QDFS → QNS → 四大模型 |
| ⬜ 阶段7 | 待实现 | QNS训练彝文数据 |
| ⬜ 阶段8 | 待实现 | 三种部署 |

---

*文档结束 — 2026-07-11 更新 v3.0.0*