# QEntL 全栈构建与跑通方案

> 版本: 1.0.0
> 日期: 2026-07-03
> 状态: 执行中

---

## 一、八阶段自举流程（总体架构）

```
阶段1: C语言解释器（qcl_bootstrap.c）解释量子指令子集
     ↓
阶段2: 解释器启动QCL引导器（QEntL源码，数个.qentl文件）
     ↓
阶段3: QCL引导器编译QCL与QVM的QEntL源码（各数个.qentl文件）
       → 生成 QCL 和 QVM 的 QBC（各数个.qbc文件）
     ↓
阶段4: C语言启动器（qvm_bootstrap.c）加载QVM（数个.qbc文件）运行
       → QEntL环境形成
     ↓
阶段5: QCL编译器（数个.qbc文件）在QEntL环境中运行
       → 编译所有QEntL源码
     ↓
阶段6: QDFS/QNS/四大模型（各数个.qbc文件）等全部在QEntL环境中运行
       其中 QNS 以 QDFS 为基础，四大模型以 QNS 为基础
     ↓
阶段7: QNS（各数个.qbc文件）训练彝文等数据，模型测试成功
       → 更新 web 桌面的量子助手的 API
     ↓
阶段8: QEntL 三种部署
```

---

## 二、阶段详情

### 阶段1: C语言解释器启动

**组件**: `src/qcl_bootstrap.c`（编译为 `bin/qcl_bootstrap`）

**职责**: 解释执行 `.qentl` 量子电路文件，输出 `.qbc` 字节码

**支持指令**: init / H / X / Y / Z / T / S / CNOT / MEASURE / PRINT / STOP 等量子指令子集

**不支持**: def 函数定义、类型定义、模块定义、函数体等高级语法

**编译命令**:
```bash
cd /root/QSM && gcc -std=c11 -O2 -o bin/qcl_bootstrap src/qcl_bootstrap.c -lm
```

---

### 阶段2: 解释器启动 QCL引导器

**组件**: `QCL引导器.qentl`（QEntL源码）

**QCL引导器包含**:
- 量子电路执行体（qcl_bootstrap 可编译部分）
- 模块导入（import QCL模块/qcl_opcodes.qentl 等）
- 三个核心函数：新建编译器 / 扫描QEntL目录 / 编译器.编译

**QCL模块依赖**（6个文件，3,605行）:
- `QCL模块/qcl_opcodes.qentl` — 操作码定义（240行）
- `QCL模块/qcl_lexer.qentl` — 词法分析器（730行）
- `QCL模块/qcl_parser.qentl` — 语法解析器（618行）
- `QCL模块/qcl_parser_high.qentl` — 高级语法解析器（1,258行）
- `QCL模块/qcl_bootstrap_phase2.qentl` — 阶段2引导（735行）
- `QCL模块/qcl_compiler_phase2.qentl` — 阶段2编译器（24行）

**编译命令**:
```bash
cd /root/QSM && bin/qcl_bootstrap QCL引导器.qentl QCL引导器.qbc
```

---

### 阶段3: QCL引导器编译 QCL 与 QVM

**组件**: QCL引导器在 QEntL 环境中运行

**输入**: QCL 与 QVM 的 QEntL 源码（各数个 .qentl 文件）
- QCL 源码: `QEntL/System/Compiler/` 目录
- QVM 源码: `QEntL/System/VM/` 目录

**输出**: QCL 和 QVM 的 .qbc 字节码（各数个 .qbc 文件）

---

### 阶段4: C语言启动器加载 QVM 运行

**组件**: `src/qvm_bootstrap.c`（编译为 `bin/qvm_bootstrap`）

**职责**: 加载 QVM.qbc 字节码，启动 QEntL 虚拟机，形成 QEntL 运行环境

**编译命令**:
```bash
cd /root/QSM && gcc -std=c11 -O2 -o bin/qvm_bootstrap src/qvm_bootstrap.c -lm
```

**执行**:
```bash
bin/qvm_bootstrap QVM.qbc
```

**结果**: QEntL 环境形成

---

### 阶段5: QCL编译器在QEntL环境中运行

**组件**: QCL 编译器（数个 .qbc 文件）

**职责**: 在 QEntL 环境中运行，编译所有 QEntL 源码

**输入**: 所有 .qentl 源文件（235个，QEntL/ 目录）

**输出**: 完整的 .qbc 字节码集合

---

### 阶段6: QDFS/QNS/四大模型在QEntL环境中运行

**组件及依赖关系**:
```
QDFS（数个.qbc文件）→ QNS（数个.qbc文件）→ 四大模型（数个.qbc文件）
```

**QDFS（量子分布式文件系统）**: `QEntL/System/Kernel/filesystem/`
**QNS（量子神经网络系统）**: `QEntL/System/Kernel/neural/`
**四大模型**: `QEntL/Models/`
- QSM (Quantum Superposition Model)
- SOM (Self-Organizing Map)
- WeQ (Web Assistant)
- Ref (Reference Model)

---

### 阶段7: 训练与测试

**组件**: QNS（数个 .qbc 文件）

**任务**: 训练彝文等数据，模型测试成功

**输出**: 更新 web 桌面的量子助手的 API

---

### 阶段8: QEntL 三种部署

见下方"八、三种部署模式"。

---

## 三、核心原则

1. **C语言只能是启动器或解释器，不是编译器**
2. **只有两个C语言组件**:
   - `src/qcl_bootstrap.c` — 解释器（量子指令子集）
   - `src/qvm_bootstrap.c` — 启动器（加载器）
3. **所有QEntL编译都通过 qcl_bootstrap 完成**
4. **QCL引导器 = QEntL构建的QCL编译器**（真正的编译器）
5. **QEntL环境形成后才能运行QCL编译器编译所有源码**
6. **分阶段自举，每一阶段依赖前一阶段**

---

## 四、文件结构

```
/root/QSM/
├── src/
│   ├── qcl_bootstrap.c      # C语言解释器（阶段1）
│   └── qvm_bootstrap.c      # C语言启动器（阶段4）
├── bin/
│   ├── qcl_bootstrap        # 编译后的解释器
│   └── qvm_bootstrap        # 编译后的启动器
├── QCL引导器.qentl          # QCL引导器源码（阶段2）
├── QCL引导器.qbc            # QCL引导器字节码
├── QCL模块/                  # QCL编译器组件（6个文件）
│   ├── qcl_opcodes.qentl
│   ├── qcl_lexer.qentl
│   ├── qcl_parser.qentl
│   ├── qcl_parser_high.qentl
│   ├── qcl_bootstrap_phase2.qentl
│   └── qcl_compiler_phase2.qentl
├── QEntL/                    # QEntL全栈源码
│   ├── System/
│   │   ├── Compiler/         # QCL编译器（阶段5）
│   │   ├── VM/              # QVM（阶段4）
│   │   └── Kernel/
│   │       ├── filesystem/  # QDFS（阶段6）
│   │       └── neural/      # QNS（阶段6/7）
│   ├── Models/               # 四大模型（阶段6/7）
│   │   ├── QSM/
│   │   ├── SOM/
│   │   ├── WeQ/
│   │   └── Ref/
│   └── 235个.qentl源码文件
└── data/                     # 训练数据（51,899条）
```

---

## 五、.qbc文件格式（经典+量子双格式）

**统一文件格式，包含5个经典平台的机器二进制 + 量子字节码：**

```
.qbc文件结构:
┌─────────────────────────────────────────┐
│ 文件头（统一标识，0x14）                 │
├─────────────────────────────────────────┤
│ 经典逻辑部分（机器二进制）                │
│ - Windows (PE)                          │
│ - iOS (Mach-O)                          │
│ - Android (ELF)                         │
│ - 鸿蒙 (ELF/ARM)                        │
│ - Linux (ELF)                           │
│ → CPU直接执行                            │
├─────────────────────────────────────────┤
│ 量子逻辑部分（量子字节码）                │
│ - 叠加态指令                             │
│ - 纠缠指令                               │
│ - 测量指令                               │
│ → QPU直接执行                            │
└─────────────────────────────────────────┘
```

### 经典5平台架构

| 平台 | 架构 | 机器二进制格式 | 说明 |
|------|------|---------------|------|
| Windows | x86_64/ARM64 | PE（Portable Executable） | 可移植可执行文件 |
| iOS | ARM64 | Mach-O | Apple移动操作系统 |
| Android | ARM64 | ELF（Linux格式） | Linux衍生系统 |
| 鸿蒙 | ARM64 | ELF（Linux格式） | 华为操作系统 |
| Linux | x86_64/ARM64 | ELF | 标准Linux |

**经典5平台支持**: 嵌入在QCL模块（opcodes/lexer/parser）中实现。编译时，QCL编译器读取源码中的平台指令，自动选择对应平台。

---

### 量子3种部署

| 部署方式 | 量子运算实现 | 说明 |
|---------|------------|------|
| **开发部署** | 软件模拟器（QVM） | 本地CPU模拟量子运算 |
| **生产部署** | 云端QPU API | 网络调用云端QPU服务 |
| **专用部署** | 量子协处理器 | 直接调用硬件量子设备 |

**量子3种部署支持**: 嵌入在 `QEntL/System/VM/src/deployment/` 模块中（8个模块，3,361行）。

---

## 六、安装方式（两种）

| 场景 | 方式 | 是否需要安装程序 |
|------|------|------------------|
| **QEntL应用程序在Windows上** | 解压即用（绿色软件） | ❌ 不需要 |
| **QEntL操作系统在笔记本上** | ISO镜像安装 | ✅ 需要（引导/分区/驱动配置） |

---

## 七、核心组件说明

### QCL引导器（QCL引导器.qentl）

QCL引导器是QCL编译器的QEntL源码版本，包含：

- **量子电路执行体**: 8量子比特H/X/CNOT纠缠+8路MEASURE/PRINT，QVM验证23周期/23门
- **模块导入**: import 4个QCL模块
- **辅助工具函数**: starts_with/skip_whitespace/parse_int/trim_str/冒泡排序/排除目录检查
- **新建编译器()**: 初始化opcode表、编译器对象
- **扫描QEntL目录()**: 递归遍历目录树、匹配*.qentl、冒泡排序
- **编译器.编译()**: 七步流程（读取→词法→语法→语义→字节码→优化→写入.qbc）
- **主程序()**: 入口函数（初始化→扫描→编译→输出）

### QCL模块（6个文件，3,605行）

| 模块 | 行数 | 功能 |
|------|------|------|
| qcl_opcodes.qentl | 240 | 68个操作码常量表 |
| qcl_lexer.qentl | 730 | 70个token类型，词法分析 |
| qcl_parser.qentl | 618 | 15个函数，量子指令解析 |
| qcl_parser_high.qentl | 1,258 | 39个函数，高级语法解析 |
| qcl_bootstrap_phase2.qentl | 735 | 阶段2引导（def函数定义编译） |
| qcl_compiler_phase2.qentl | 24 | 阶段2编译器入口（纯量子指令） |

---

## 八、三种部署模式（阶段8详情）

### 部署方式1: 应用部署

QEntL应用程序解压即用（主要方式，无需setup.exe）。

**特点**: 绿色软件，解压即用，自动检测平台，无需安装。

### 部署方式2: 操作系统部署

QEntL操作系统ISO镜像安装到硬件。

**特点**: 需要引导程序（Bootloader）、分区管理、驱动安装、系统配置。类似Ubuntu/Linux安装。

### 部署方式3: 跨平台部署

支持5大经典平台（Windows/iOS/Android/鸿蒙/Linux）+ 3种量子部署方式（开发/生产/专用）。

**特点**: .qbc文件自动包含经典5平台机器二进制+量子3部署字节码，运行时代码根据平台自动适配。

---

## 九、里程碑跟踪

| 阶段 | 状态 | 说明 |
|------|------|------|
| ✅ 阶段1 | 完成 | qcl_bootstrap.c编译为bin/qcl_bootstrap |
| ✅ 阶段2 | 完成 | QCL引导器.qentl → QCL引导器.qbc（293字节，23周期/23门通过） |
| [ ] 阶段3 | 待实现 | QCL引导器编译QCL与QVM源码 → 生成各数个.qbc |
| [ ] 阶段4 | 待实现 | qvm_bootstrap.c加载QVM.qbc → QEntL环境形成 |
| [ ] 阶段5 | 待实现 | QCL编译器编译所有QEntL源码 |
| [ ] 阶段6 | 待实现 | QDFS/QNS/四大模型在QEntL环境中运行 |
| [ ] 阶段7 | 待实现 | QNS训练彝文数据，更新API |
| [ ] 阶段8 | 待实现 | 三种部署 |

---

*文档结束*