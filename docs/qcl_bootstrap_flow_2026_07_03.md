# QCL引导器自举流程（2026-07-03 最终确认）

> **核心原则**: `qcl_bootstrap.c` 是C语言**解释器**（不是编译器），只解释量子指令子集。真正编译QEntL高级语法的是**QCL引导器.qentl**（QEntL源码）。

---

## 架构理解（用户纠正，2026-07-03）

| 组件 | 说明 |
|------|------|
| `qcl_bootstrap.c` | **C语言解释器** — 解释执行QEntL量子电路，启动QCL引导器 |
| `qcl_bootstrap.c` | **不是编译器** — 只解释量子指令子集，不编译高级语法 |
| `QCL引导器.qentl` | **QEntL构建的QCL编译器** — 真正的编译器，由解释器启动 |
| QVM | **运行环境** — 构建QEntL环境 |

---

## QCL引导器自举流程（7阶段）

```
阶段1: C语言解释器（qcl_bootstrap.c）解释量子指令子集
     ↓
阶段2: 解释器启动QCL引导器.qentl（QEntL源码）
     ↓
阶段3: QCL引导器编译QEntL源码 → 生成QCL.qbc和QVM.qbc
     ↓
阶段4: C语言启动器加载QVM.qbc → QEntL环境形成
     ↓
阶段5: QCL引导器编译QCL编译器源码 → QCL.qbc
     ↓
阶段6: QCL编译器在QEntL环境中运行 → 编译所有QEntL源码
     ↓
阶段7: QDFS/QNS/四大模型全部在QEntL环境中运行
```

---

## 详细步骤

### 阶段1: C语言解释器（qcl_bootstrap.c）

```bash
# 编译C语言解释器（只作为解释器/启动器）
gcc -std=c11 -O2 -o bin/qcl_bootstrap src/qcl_bootstrap.c -lm

# 解释量子指令子集
# 支持: init/H/X/Y/Z/T/S/CNOT/MEASURE/PRINT/STOP等
# 不支持: def/类型/函数/模块/导入等高级语法
```

### 阶段2: 启动QCL引导器.qentl

```bash
# qcl_bootstrap解释并启动QCL引导器.qentl
bin/qcl_bootstrap QCL引导器.qentl
# 或
bin/qcl_bootstrap QCL引导器.qentl QCL引导器.qbc
```

**注意**: QCL引导器.qentl 当前只有39行占位代码，需要实现！

### 阶段3: QCL引导器编译QEntL源码

```bash
# QCL引导器（由qcl_bootstrap启动）编译QEntL源码
QCL引导器编译QCL编译器源码 → QCL.qbc
QCL引导器编译QVM源码 → QVM.qbc
```

### 阶段4: QVM环境形成

```bash
# C语言启动器加载QVM.qbc
gcc -std=c11 -O2 -o bin/qvm_bootstrap src/qvm_bootstrap.c -lm
bin/qvm_bootstrap QVM.qbc
# → QEntL环境形成！
```

### 阶段5: QCL编译器编译源码

```bash
# QCL编译器在QEntL环境中运行
bin/qvm_bootstrap QCL.qbc
# → QCL编译器编译所有QEntL源码
```

### 阶段6: 全量编译

```bash
# 编译QNS训练器
bin/qvm_bootstrap QCL.qbc --compile QEntL/System/Kernel/neural/qns_trainer.qentl

# 编译QDFS核心
bin/qvm_bootstrap QCL.qbc --compile QEntL/System/Kernel/filesystem/qdfs_core.qentl

# 编译四大模型
bin/qvm_bootstrap QCL.qbc --compile QEntL/Models/...
```

### 阶段7: QEntL全栈运行

```bash
# QDFS运行
bin/qvm_bootstrap QDFS.qbc

# QNS训练
bin/qvm_bootstrap QNS.qbc --train data/yi_4120_merged_for_gemma.jsonl

# 四大模型运行
bin/qvm_bootstrap QSM.qbc
bin/qvm_bootstrap SOM.qbc
bin/qvm_bootstrap WeQ.qbc
bin/qvm_bootstrap Ref.qbc
```

---

## 关键问题

**QCL引导器.qentl 当前状态**: 39行占位伪代码，未实现！

需要实现：
```
新建编译器()      ← 未实现
扫描QEntL目录()   ← 未实现
编译器.编译()     ← 未实现
```

**这是QEntL全栈的核心瓶颈！**

---

## 用户纠正记录（2026-07-03）

> "qcl_bootstrap是解释器，不是编译器。它只是用QEntl构建的Qcl引导器的解释器"
>
> "C语言启动器启动QEntl源码Qcl编译器，编译Qcl与Qvm源码。然后c语言启动器加载qbc版本的Qvm构建环境，启动qbc版本Qcl"

**这些是架构铁律，必须遵守！**

---

## 相关文件

- SKILL.md: `/root/.hermes/skills/qentl-fullstack/SKILL.md`
- QCL引导器源码: `QCL引导器.qentl`
- C语言解释器: `src/qcl_bootstrap.c`
- C语言启动器: `src/qvm_bootstrap.c`