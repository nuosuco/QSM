# QSM量子叠加态模型 — 构建顺序指南

## 核心原则（铁律）

### 1. 全栈QEntL构建 — 禁止使用第三方库

- **所有代码必须使用QEntL语言实现**，或使用C语言（仅用于启动引导）
- **禁止使用** Python(.py)、Node.js(.js)、Java、Go、Rust等第三方语言
- **禁止使用** numpy、pytorch、tensorflow等第三方库
- **禁止使用** OpenSSL、libcurl等第三方C库
- **唯一允许的依赖**: 标准C库（libc, libm, libpthread）

### 2. 构建顺序 — 六层架构（严格依赖顺序）

```
第1层: C语言启动器 (启动引导) - C语言
   ↓ 依赖
第2层: QVM量子虚拟机 (环境基础) - QEntL全栈
   ↓ 依赖
第3层: QCL编译器 (编译工具) - QEntL全栈
   ↓ 依赖
第4层: QDFS量子动态文件系统 (叠加态并行运算基础) - QEntL全栈
   ↓ 依赖
第5层: QNS量子神经叠加态 (训练与推理) - QEntL全栈
   ↓ 依赖
第6层: 四大模型应用层 (QSM/SOM/WeQ/Ref) - QEntL全栈
```

### 3. 命名规范

- **"量子神经网络" → "量子神经叠加态"** (QNS)
- 缩写: QNN → QNS (Quantum Neural Superposition)
- 理由: 网络是线性的，叠加态是并行的平行宇宙

### 4. 子代理沟通规范

- 子代理必须加载此技能才能工作
- 子代理任务描述中必须明确标注"QEntL全栈方案"
- 子代理产出必须符合上述四项铁律
- **禁止闭门造车！** 所有子代理必须参与整个QEntL全栈跑通流程

### 5. 训练→测试→迭代循环

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  训练   │ -> │  测试   │ -> │ 评估    │ -> │ 改进    │ -> │ 更新API │
│  Train  │    │  Test   │    │ Evaluate│    │ Improve │    │ Update  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     ^                                                                    │
     │                                                                    │
     └────────────────── 循环（直到测试成功）──────────────────────────────┘
```

---

## 详细构建步骤

### 第1步: C语言启动器 (已完成)

- 文件: `src/qvm_boot.c` → `bin/qvm_boot`
- 功能: 启动QVM（QEntL全栈）
- 已推送: ✓

### 第2步: QVM量子虚拟机 (已完成)

- QEntL实现: `QEntL/System/VM/`
- 功能: 量子比特管理、量子门操作、叠加态/纠缠态模拟、量子内存管理
- 能力: 64量子比特、16经典寄存器、1024KB量子内存、19种操作码
- **必须在C启动器上运行**
- 已推送: ✓

### 第3步: QCL编译器 (已完成)

- QEntL实现: `QEntL/System/Compiler/`
- 功能: 将.qentl源码编译为.qbc字节码
- **必须在QVM上运行**
- 已推送: ✓

### 第4步: QDFS量子动态文件系统 (已完成)

- QEntL实现: `QEntL/System/Kernel/filesystem/*.qentl`
- 功能: 叠加态文件管理、量子加密、纠缠关联、BB84密钥交换
- **必须在QVM上运行**
- 测试: **38/38 全部通过 (100%)**
- 已推送: ✓

### 第5步: QNS量子神经叠加态 (进行中)

- **必须用QEntL文件构建，不能用C语言！**
- QNS训练管道: `QEntL/System/Kernel/neural/qns_training_pipeline.qentl` (754行)
- **必须在QVM上运行**
- 功能:
  - 量子叠加态嵌入
  - 量子纠缠注意力机制
  - 量子叠加态前向传播
  - 量子梯度下降
  - 模型保存与加载（基于QDFS）
- 训练数据: `data/yi_4120_merged_for_gemma.jsonl` (彝文字符集4120个)
- 训练参数: 学习率0.01, Momentum 0.9, 嵌入维度128, 隐藏层[256, 128, 64]

#### 训练流程

```bash
# 1. 扫描训练数据
bin/qvm_boot bin/yi_pipeline.qbc scan data/

# 2. 执行QNS训练（彝文）
bin/qvm_boot bin/qns_training_pipeline.qbc data/yi_4120_merged_for_gemma.jsonl data/qns_model.dat 10

# 3. 评估结果
bin/qvm_boot bin/qns_training_pipeline.qbc test
```

#### 迭代判定标准

| 结果 | 动作 |
|------|------|
| 准确率达标（>80%） | ✅ 停止迭代，更新Web桌面量子助手API |
| 准确率未达标 | ❌ 调整参数/扩充数据/调整网络结构 → 重新训练 |
| 测试失败 | ❌ 修复Bug → 重新测试 |

#### 更新Web桌面量子助手API

当训练测试成功后，必须更新Web桌面的量子助手API：

```bash
# 1. 更新API配置
# 编辑 src/qsm_api.c，更新模型路径和参数

# 2. 重新编译API
gcc -std=c11 -O2 -o bin/qsm_api src/qsm_api.c -lm

# 3. 重启Web桌面服务

# 4. 通知用户测试
# 通过企业微信通知用户："QNS训练完成，Web桌面量子助手API已更新，请测试"
```

### 第6步: 四大模型应用层 (待实现)

- QSM量子叠加态模型
- SOM量子平权经济模型
- WeQ量子社交通信模型
- Ref量子自反省管理模型
- **必须在QVM上运行**

---

## 并行工作分工

### ⚠️ 核心原则：子代理必须参与整个流程的跑通情况

**禁止闭门造车！** 所有子代理必须参与整个QEntL全栈跑通流程，不能只做自己的一部分就脱离整体。

### 角色分工

| 角色 | 职责 | 必须参与 |
|------|------|----------|
| 助手(主代理) | 整体协调、任务分配、进度监控、质量把关 | 全流程 |
| 子代理A | QNS训练管道 | 训练→测试→迭代循环 |
| 子代理B | QDFS扩展 | 文件系统→QNS数据加载 |
| 子代理C | QVM扩展与编译器完善 | QVM环境→QEntL编译 |
| 子代理D | QSM四大模型应用层 | 模型→Web桌面API |
| 子代理E | Web界面完善 | 界面→API集成 |

### 并行协作规则

1. **任务分配**: 主代理统一分配任务，子代理不得自行选择任务
2. **依赖管理**: 有依赖的任务串行执行，无依赖的任务并行执行
3. **冲突避免**: 同一文件同一时间只允许一个子代理修改
4. **进度同步**: 每完成一个阶段立即向主代理汇报
5. **资源共享**: 编译产物、训练数据、测试结果共享，避免重复工作
6. **流程参与**: 子代理必须参与整个跑通流程，不能只做局部就脱离

---

## 子代理任务模板

```
项目位于/root/QSM，**必须完全使用QEntL全栈方案**，
不能使用任何第三方库或经典实现！

构建顺序: C启动器 → QVM → QCL编译器 → QDFS → QNS → 四大模型

重要:
- 禁止使用.py/.js等第三方语言
- 禁止使用numpy/pytorch等第三方库
- 禁止使用OpenSSL等第三方C库
- 量子神经网络改名为"量子神经叠加态"(QNS)
- **必须参与整个跑通流程，禁止闭门造车！**
- **所有组件（除C启动器外）必须在QVM上运行！**
```

## 技能加载要求

- 所有子代理任务必须附带此技能上下文
- 助手在分配任务前必须确认子代理知晓此技能

---

## 快速参考

### QEntL量子门语法

```qentl
init N              # 初始化N个量子比特
H 0                 # Hadamard门
CNOT 0 1            # 受控非门
MEASURE 0 0         # 测量
PRINT 0             # 打印
STOP                # 停止
```

### 关键路径速查

```
C启动器:    src/qvm_boot.c
QVM:        QEntL/System/VM/
编译器:     QEntL/System/Compiler/
QDFS:       QEntL/System/Kernel/filesystem/
QNS:        QEntL/System/Kernel/neural/
数据管道:   QEntL/System/Kernel/data/
QEntL系统:  QEntL/System/**/*.qentl (195个)
QEntL模型:  QEntL/Models/**/**/*.qentl (23个)
训练数据:   data/*.jsonl (103个)
示例代码:   docs/examples/*.qentl (14个)
```

### 常用命令

```bash
# 查看项目统计
find . -name "*.qentl" | wc -l
du -sh . --exclude=.git
git log --oneline -5

# 运行所有测试
bin/qvm_boot test
bin/qvm_boot bin/qdfs_driver.qbc
bin/qvm_boot bin/qns_training_pipeline.qbc test
```

### Git 提交与推送

```bash
cd /root/QSM
git add -A
git commit -m "QEntL全栈: [描述修改]"
git push origin master
git push origin main
git push origin dev
```

---

## 故障排除

| 问题 | 解决 |
|------|------|
| 找不到.qentl文件 | 检查 QEntL/System/ 目录 |
| 编译器报错 | 检查QEntL语法和关键字拼写 |
| QVM运行失败 | 检查.qbc字节码文件格式 |
| QDFS部分失败 | 当前38/38通过，读取/加密相关已修复 |
| 彝文识别率低 | 扩充训练数据 |
| Git仓库损坏 | `.git/index`为0字节 → `rm .git/index && git read-tree HEAD` 修复 |
| 编译产物为空文件 | `find bin/ -type f -empty` 检测，重新编译修复 |
| 僵尸训练进程 | `ps aux | grep train` 检查，验证数据路径是否存在 |