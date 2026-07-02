# QEntL 全栈跑通流程

> **版本**: v2.0 R9  
> **日期**: 2026-07-02  
> **项目**: QSM (Quantum Superposition Model)  
> **核心语言**: QEntL (量子编程语言)  
> **约束**: 完全使用QEntL全栈方案，禁止使用第三方库、经典语言实现  
> **当前验证**: 270 QEntL源文件 → 270编译成功 → 974 QBC → 974 QVM通过 (100%)

---

## 核心原则

- **绝对禁止休眠**: 助手与子代理必须持续并行工作
- **绝对禁止欺骗**: 有工作就做，没工作就如实汇报
- **QEntL全栈强制**: 所有代码必须使用QEntL语言实现，禁止使用.py/.js等第三方语言
- **禁止第三方库**: 禁止使用numpy/pytorch/OpenSSL等第三方库，全部自研
- **量子神经叠加态**: 量子神经网络统一更名为"量子神经叠加态"(QNS)

---

## 项目架构总览

```
QSM/
├── bin/                    # 编译产物 (二进制可执行文件)
│   ├── qvm_boot            # QVM量子虚拟机
│   ├── qentl_compiler      # QCL编译器 (v3.x, CNOT tgt修复)
│   ├── qdfs_driver         # QDFS量子动态文件系统
│   ├── qnn_runner          # QNS推理引擎
│   ├── yi_pipeline         # 彝文数据管道
│   ├── qns/                # QNS字节码 (14个)
│   ├── qdfs/               # QDFS字节码 (32个)
│   └── models/             # 四大模型字节码
├── QEntL/                  # QEntL全栈源代码 (270个.qentl文件)
│   ├── System/
│   │   ├── VM/             # QVM量子虚拟机 (167个源文件)
│   │   ├── Compiler/       # QCL编译器
│   │   └── Kernel/         # 内核组件
│   │       ├── filesystem/ # 文件系统
│   │       ├── neural/     # QNS量子神经叠加态
│   │       ├── gui/        # 图形界面
│   │       └── services/   # 服务组件
│   └── Models/             # 四大应用模型 (23个源文件)
│       ├── QSM/            # 量子叠加态模型
│       ├── SOM/            # 自组织映射模型
│       ├── WeQ/            # 量子纠缠社交模型
│       └── Ref/            # 参考监控模型
├── src/                    # C引导代码 (自研，无第三方依赖)
├── data/                   # 训练数据 (JSONL格式)
├── docs/                   # 文档
│   ├── workflow/           # 工作流文档
│   ├── examples/           # 示例代码
│   └── architecture/       # 架构文档
├── tests/                  # 测试套件
├── web/                    # Web界面
├── aurora/                 # Aurora引擎
└── Installer/              # 安装脚本
```

---

## 构建顺序 (严格依赖关系)

### Phase 1: QVM 量子虚拟机
**功能**: 量子比特管理、量子门操作、叠加态/纠缠态模拟、测量、字节码执行引擎  
**源码**: `src/qvm_boot.c` → `bin/qvm_boot`  
**QEntL文件**: `QEntL/System/VM/` 目录下所有.qentl文件  
**操作码**: 19种 (OP_NOP ~ OP_BARRIER)  
**能力**: 64量子比特、16经典寄存器、1024KB量子内存

```bash
# 编译QVM
make qvm_boot
# 测试QVM
bin/qvm_boot test
# 运行示例
bin/qvm_boot docs/examples/bell.qbc
```

### Phase 2: QEntL 编译器
**功能**: 词法分析、语法解析、语义分析、字节码生成、优化、链接  
**源码**: `QEntL/System/Compiler/` 目录下所有.qentl文件 + `src/qentl_compiler.c` → `bin/qentl_compiler`  
**QEntL文件**: 167个系统级.qentl文件

```bash
# 编译QCL编译器
make qentl_compiler
# 编译单个QEntL文件
bin/qentl_compiler docs/examples/hello.qentl bin/hello.qbc
# 运行编译产物
bin/qvm_boot bin/hello.qbc
```

### Phase 3: QDFS 量子动态文件系统
**功能**: 量子加密存储、叠加态文件、事务管理、多维搜索、元数据管理  
**源码**: `src/qdfs.c` + `src/qdfs_driver.c` → `bin/qdfs_driver`  
**QEntL文件**: `QEntL/System/Kernel/filesystem/` 目录下所有.qentl文件

```bash
# 编译QDFS
gcc -std=c11 -O2 -o bin/qdfs_driver src/qdfs_driver.c src/qdfs.c -lm
# 运行测试
bin/qdfs_driver test
# 预期: 160/160 通过 (100%)
```

### Phase 4: QNS 量子神经叠加态
**功能**: 4层全连接网络、前向传播(ReLU+Softmax)、反向传播(SGD+Momentum)、交叉熵损失  
**源码**: `src/qnn_runner.c` → `bin/qnn_runner`  
**QEntL文件**: `QEntL/System/Kernel/neural/` 目录下所有.qentl文件
- `qns_model_params.qentl` — 模型参数定义
- `qns_training_pipeline.qentl` — 训练管道
- `qns_attention.qentl` — 注意力机制
- `qns_dataset.qentl` — 数据集管理
- `qns_embedding.qentl` — 嵌入层
- `qns_evaluation.qentl` — 评估模块
- `qns_optimizer.qentl` — 优化器
- `qns_test.qentl` — 测试套件

```bash
# 编译QNS推理引擎
gcc -std=c11 -O2 -o bin/qnn_runner src/qnn_runner.c -lm
# 运行推理
bin/qnn_runner test
```

### Phase 5: 四大模型应用层
**功能**: 基于QVM+QCL编译器+QDFS+QNS构建的应用模型

| 模型 | 目录 | 说明 |
|------|------|------|
| QSM | `QEntL/Models/QSM/` | 量子叠加态模型 (核心) |
| SOM | `QEntL/Models/SOM/` | 自组织映射模型 |
| WeQ | `QEntL/Models/WeQ/` | 量子纠缠社交模型 |
| Ref | `QEntL/Models/Ref/` | 参考监控模型 |

```bash
# 完整构建
make all
# 或
make deploy
```

---

## 完整跑通流程

### 1. 环境准备

```bash
cd /root/QSM
# 确认项目结构
find . -name "*.qentl" | wc -l    # 应有270个QEntL文件
find . -name "*.qbc" -not -name "libqdfs.a" | wc -l  # 约974个QBC字节码
du -sh . --exclude=.git            # 当前磁盘使用
git status                           # 确认工作区状态
```

### 2. 编译构建

```bash
# 方式A: 使用Makefile (推荐)
make all

# 方式B: 手动分步编译
make qvm_boot        # Phase 1: QVM
make qentl_compiler  # Phase 3: 编译器
# Phase 2: QBC Tools 使用bootstrap替代

# 方式C: 完整部署
make deploy          # 编译+测试+流水线+训练
```

### 3. 编译测试

```bash
# 3.1 编译示例QEntL文件
bin/qentl_compiler docs/examples/hello.qentl bin/hello.qbc
bin/qentl_compiler docs/examples/bell.qentl bin/bell.qbc
bin/qentl_compiler docs/examples/superposition.qentl bin/superposition.qbc
bin/qentl_compiler docs/examples/teleportation.qentl bin/teleportation.qbc

# 3.2 使用QVM运行字节码
bin/qvm_boot bin/hello.qbc
bin/qvm_boot bin/bell.qbc
bin/qvm_boot bin/superposition.qbc
bin/qvm_boot bin/teleportation.qbc

# 3.3 运行所有示例
for f in docs/examples/*.qentl; do
    base=$(basename "$f" .qentl)
    bin/qentl_compiler "$f" "bin/${base}.qbc"
    bin/qvm_boot "bin/${base}.qbc"
done
```

### 4. QDFS测试

```bash
# 运行QDFS核心功能测试
bin/qdfs_driver test
# 预期结果: 160/160 通过 (100%)
# 通过项: 初始化、文件创建、目录操作、写入、量子加密、
#         叠加态文件、事务管理、多维索引、文件删除、统计
```

### 5. QNS训练测试

```bash
# 运行QNS推理引擎测试
bin/qnn_runner test
# 测试项: 前向传播、反向传播、训练循环、推理

# 运行彝文数据管道
bin/yi_pipeline --help
# 功能: JSONL解析、Unicode解码、彝文字符检测、字符→ID映射
#       训练样本生成、批量采样、二进制输出
```

### 6. 训练流程

```bash
# 6.1 数据准备
# data/目录下已有103个JSONL训练数据文件
# 包括: 彝文学习、对话、文化、科技、日常等多领域数据

# 6.2 数据管道处理
bin/yi_pipeline scan data/
# 自动扫描JSONL文件，提取彝文字符，构建词汇表

# 6.3 训练执行
bin/qnn_runner train --data data/yi_char_learning_v4.jsonl \
                     --epochs 100 --batch-size 32 \
                     --model QSM
# 网络结构: 4120→1024→512→256→4120 (自编码器)
# 优化器: SGD with Momentum
# 激活函数: ReLU + Softmax
# 损失函数: 交叉熵

# 6.4 训练监控
bin/qnn_runner eval --checkpoint latest --dataset test
# 输出: 准确率、损失曲线、混淆矩阵
```

### 7. 迭代升级流程

```bash
# 7.1 训练完成后评估
bin/qnn_runner eval --checkpoint epoch_100 --dataset validation
# 检查彝文识别准确率

# 7.2 根据评估结果调整
# 如果准确率<目标:
#   - 调整学习率
#   - 增加训练轮数
#   - 调整网络结构
#   - 扩充训练数据

# 7.3 模型API更新
# 学会: 更新模型API → git commit
# 没学会: 返回QNS模块继续改进

# 7.4 回归测试
bin/qnn_runner test          # 确保修改未破坏已有功能
bin/qvm_boot test            # QVM回归测试
bin/qdfs_driver test         # QDFS回归测试
```

---

## 并行工作机制

| 角色 | 职责 |
|------|------|
| 助手 | 整体协调与核心模块开发 |
| 子代理A | QNS量子神经叠加态训练管道 |
| 子代理B | QDFS量子动态文件系统扩展 |
| 子代理C | QVM扩展与编译器完善 |
| 子代理D | QSM四大模型应用层 |
| 子代理E | Web界面完善 |

---

## 汇报机制

- **频率**: 每30分钟自动汇报项目状态
- **内容**:
  - `git log` — 最近提交记录
  - `find . -name "*.qentl" | wc -l` — QEntL文件数量
  - `du -sh . --exclude=.git` — 磁盘使用情况
  - 各模块测试结果汇总
  - 训练进度与准确率

---

## 故障排除

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| 找不到.qentl文件 | 确认QEntL/System/目录下存在167个源文件 |
| 编译器报错 | 检查QEntL语法，确认关键字拼写 |
| QVM运行失败 | 检查.qbc字节码文件格式 |
| QDFS读取失败 | 当前已知31/38通过，读取相关功能待修复 |
| QNS训练慢 | 减少batch size或epoch数 |
| 彝文识别率低 | 扩充yi_char_learning_v4.jsonl数据 |

### 关键文件路径速查

```
QVM源码:        src/qvm_boot.c
编译器源码:     src/qentl_compiler.c
QDFS源码:       src/qdfs.c, src/qdfs_driver.c
QNS源码:        src/qnn_runner.c
数据管道:       src/yi_pipeline.c
QEntL系统文件:  QEntL/System/**/*.qentl (167个)
QEntL模型文件:  QEntL/Models/**/**/*.qentl (23个)
训练数据:       data/*.jsonl (103个)
示例代码:       docs/examples/*.qentl (14个)
编译产物:       bin/* (20+个)
```

---

## Git工作流

```bash
# 提交到所有三个远程分支
git add -A
git commit -m "QEntL全栈跑通: [描述修改]"
git push origin master
git push origin main
git push origin dev
```

---

## 附录: QEntL语法速查

### 量子门操作
```qentl
init N              # 初始化N个量子比特
H 0                 # Hadamard门
CNOT 0 1            # 受控非门
MEASURE 0 0         # 测量量子比特0到寄存器0
PRINT 0             # 打印寄存器0的值
STOP                # 停止执行
```

### 经典操作
```qentl
let x = 42          # 变量声明
ADD r1 r2           # 加法
SUB r1 r2           # 减法
MUL r1 r2           # 乘法
DIV r1 r2           # 除法
```

### 量子计算示例 (Bell态)
```qentl
# docs/examples/bell.qentl
init 2               # 初始化2个量子比特
H 0                  # Hadamard on qubit 0
CNOT 0 1             # CNOT control=0, target=1
MEASURE 0 0          # 测量
MEASURE 1 1
PRINT 0              # 输出结果
STOP
```
