---
name: qentl-fullstack
description: "QEntL全栈跑通流程Skill — 七步工作法、全栈流程、并行协作、训练测试迭代、防欺骗防休眠、汇报机制。所有子代理必须加载此Skill才能工作。"
version: 5.11.0
author: QSM Team
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [qentl, qsm, qvm, qdfs, qns, quantum, fullstack, workflow, seven-step, anti-cheat, anti-sleep, audit]
    related_skills: [hermes-agent]
  last_audit: "2026-07-02"
  audit_result: "887/887 .qbc QVM PASS, 220/220 .qentl compilable, CNOT bug fixed"
---

# QEntL 全栈跑通流程 Skill

> **强制加载规则**: 所有子代理启动后必须加载本Skill。未加载本Skill的子代理禁止执行任何开发/训练/测试任务。闭门造车 = 无效工作。

---

## 一、七步工作法（方法论）

七步工作法是QSM项目开发的**核心方法论**，每个任务必须按此顺序执行：

### Step 1: 学习 (Learn)
- 阅读相关文档、代码、数据，理解上下文
- 明确当前任务的目标、约束、依赖关系
- **禁止跳过学习直接写代码**

### Step 2: 构架 (Architect)
- 设计模块结构、接口定义、数据流
- 明确输入输出、错误处理、边界条件
- 输出设计文档/伪代码

### Step 3: 训练 (Train)
- 编写代码/配置训练参数
- 执行训练流程，记录参数与结果
- **训练前必须确认数据路径、模型路径正确**

### Step 4: 测试 (Test)
- 编写并执行单元测试、集成测试
- 验证功能正确性、性能指标
- **测试不通过 → 回到Step 3改进，禁止带病提交**

### Step 5: 改进 (Improve)
- 根据测试结果优化代码/参数
- 修复Bug、提升性能、增强健壮性
- 形成闭环：测试→改进→再测试

### Step 6: 总结 (Summarize)
- 记录本次工作的成果、问题、经验
- 更新文档、注释、README
- **无总结 = 工作未完成**

### Step 7: 记忆 (Remember)
- 将关键经验写入记忆/文档
- 更新Skill、工作流文档
- 确保后续任务可复用本次成果

---

## 二、跑通流程（必须执行的全栈流程）

QEntL全栈跑通是**必须执行的完整流程**，不可跳过任何环节：

### 全栈链路：QVM → 编译器 → QDFS → QNS → 四大模型

```
QVM(量子虚拟机) → QEntL编译器 → QDFS(量子动态文件系统) → QNS(量子神经叠加态) → 四大模型应用层
```

### Phase 1: QVM 量子虚拟机
```bash
# 编译
make qvm_boot
# 或直接
gcc -std=c11 -O2 -o bin/qvm_boot src/qvm_boot.c -lm

# 测试
bin/qvm_boot test

# 运行示例
bin/qvm_boot bin/hello.qbc
bin/qvm_boot bin/bell.qbc
bin/qvm_boot bin/superposition.qbc
```
**能力**: 64量子比特、16经典寄存器、1024KB量子内存、19种操作码

### Phase 2: QEntL 编译器
```bash
# 编译
make qentl_compiler
# 或直接
gcc -std=c11 -O2 -o bin/qentl_compiler src/qentl_compiler.c -lm

# 编译QEntL源文件
bin/qentl_compiler docs/examples/hello.qentl bin/hello.qbc
bin/qentl_compiler docs/examples/bell.qentl bin/bell.qbc

# 批量编译所有示例
for f in docs/examples/*.qentl; do
    base=$(basename "$f" .qentl)
    bin/qentl_compiler "$f" "bin/${base}.qbc"
done
```

### Phase 3: QDFS 量子动态文件系统
```bash
# 编译
gcc -std=c11 -O2 -o bin/qdfs_driver src/qdfs_driver.c src/qdfs.c -lm

# 测试 (预期 31/38 通过, 81.6%)
bin/qdfs_driver test
```

### Phase 4: QNS 量子神经叠加态
4层全连接网络 (4120→1024→512→256→4120)，前向传播(ReLU+Softmax)，反向传播(SGD+Momentum)。
```bash
# 编译
gcc -std=c11 -O2 -o bin/qnn_runner src/qnn_runner.c -lm

# 测试
bin/qnn_runner test
```

### Phase 5: 四大模型应用层
```bash
# 编译数据管道
gcc -std=c11 -O2 -o bin/yi_pipeline src/yi_pipeline.c -lm

# 完整构建
make all
# 或
make deploy
```

---

## 三、并行工作规范（助手+子代理协调）

### 角色分工
| 角色 | 职责 |
|------|------|
| 助手(主代理) | 整体协调、任务分配、进度监控、质量把关 |
| 子代理A | QNS训练管道 |
| 子代理B | QDFS扩展 |
| 子代理C | QVM扩展与编译器完善 |
| 子代理D | QSM四大模型应用层 |
| 子代理E | Web界面完善 |

### 并行协作规则
1. **任务分配**: 主代理统一分配任务，子代理不得自行选择任务
2. **依赖管理**: 有依赖的任务串行执行，无依赖的任务并行执行
3. **冲突避免**: 同一文件同一时间只允许一个子代理修改
4. **进度同步**: 每完成一个阶段立即向主代理汇报
5. **资源共享**: 编译产物、训练数据、测试结果共享，避免重复工作

### 子代理启动检查清单
- [ ] 已加载qentl-fullstack Skill
- [ ] 已确认任务分配
- [ ] 已确认依赖关系
- [ ] 已确认输出路径
- [ ] 已确认汇报频率

---

## 四、训练→测试→迭代循环

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  训练   │ -> │  测试   │ -> │ 评估    │ -> │ 改进    │
│  Train  │    │  Test   │    │ Evaluate│    │ Improve │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     ^                                              │
     │                                              │
     └────────────────── 循环 ───────────────────────┘
```

### 训练流程
```bash
# 1. 扫描训练数据
bin/yi_pipeline scan data/

# 2. 执行训练
bin/qnn_runner train --data data/yi_char_learning_v4.jsonl \
                     --epochs 100 --batch-size 32 \
                     --model QSM

# 3. 评估结果
bin/qnn_runner eval --checkpoint latest --dataset test
```

### 迭代升级
```bash
# 1. 评估准确率
bin/qnn_runner eval --checkpoint epoch_N --dataset validation

# 2. 根据结果调整
#   准确率低 → 调整学习率/增加轮数/扩充数据/调整网络结构
#   准确率高 → 更新模型API并提交

# 3. 回归测试
bin/qnn_runner test
bin/qvm_boot test
bin/qdfs_driver test
```

### 迭代判定标准
- **继续迭代**: 准确率未达标、Bug未修复、性能不满足要求
- **停止迭代**: 达到目标指标、时间/资源耗尽、进入下一阶段

---

## 五、防欺骗机制

### 核心原则
**有工作就做，没工作就如实汇报。禁止编造进度、伪造结果、虚报完成。**

### 防欺骗检查点
1. **进度真实性**: 汇报的进度必须有实际产出物支撑（代码、日志、测试结果）
2. **结果可验证**: 所有测试结果必须可复现，提供命令和输出
3. **时间合理性**: 汇报的工作量与耗时必须匹配，异常快速完成需说明原因
4. **产出物检查**: 每个阶段必须有对应的文件/日志/截图作为证据

### 违规处理
- 发现编造进度 → 立即停止当前任务，重新分配
- 发现伪造结果 → 回滚修改，重新执行
- 累计违规 → 降级或替换子代理

---

## 六、防休眠机制

### 核心原则
**绝对禁止休眠。持续并行工作，不中断。有任务就执行，没任务就等待分配。**

### 防休眠规则
1. **持续工作**: 子代理不得自行停止、休眠、挂起
2. **空闲处理**: 无任务时主动汇报"待分配"，等待主代理指令
3. **超时检查**: 主代理定期检查子代理活跃度，超时未响应视为休眠
4. **自动恢复**: 发现休眠的子代理立即唤醒或替换

### 休眠判定
- 超过30分钟无汇报 → 判定为休眠
- 收到任务后超过15分钟无响应 → 判定为休眠
- 汇报内容为空或重复 → 判定为疑似休眠

---

## 七、汇报机制

### 汇报频率
**每30分钟整点整半汇报一次**（00:00, 00:30, 01:00, 01:30, ...）

### 汇报内容模板
```
【汇报】[时间] [子代理ID]
- 当前任务: [任务描述]
- 进度: [百分比] [具体完成内容]
- 产出物: [文件/日志/测试结果]
- 问题/风险: [遇到的问题和风险]
- 下一步: [接下来的计划]
- 状态: [进行中/已完成/阻塞/待分配]
```

### 汇报渠道
- 主代理 → 项目群/日志文件
- 子代理 → 主代理

### 紧急汇报
遇到以下情况立即汇报，不等整点整半：
- 任务阻塞无法继续
- 发现严重Bug或安全漏洞
- 资源不足（磁盘、内存、网络）
- 依赖服务不可用

---

## 八、核心约束

- **QEntL全栈强制**: 所有代码使用QEntL语言，禁止.py/.js等第三方语言
- **禁止第三方库**: 禁止使用numpy/pytorch/OpenSSL等，全部自研
- **量子神经叠加态**: 量子神经网络统一更名为"量子神经叠加态"(QNS)
- **绝对禁止休眠**: 持续并行工作，不中断
- **绝对禁止欺骗**: 有工作就做，没工作就如实汇报

## 九、项目位置

```
项目根目录: /root/QSM
QEntL源文件: /root/QSM/QEntL/ (QNS 14+QDFS 32+Compiler 53+Kernel 17+Services 23+GUI 15+VM 21+Models 40+Scripts 3, R18全量220/220独立审计+QVM通过+QDFS driver 38/38 100%, CNOT tgt bug修复已验证)
C引导代码:  /root/QSM/src/
编译产物:   /root/QSM/bin/
训练数据:   /root/QSM/data/ (103个JSONL文件)
工作流文档: /root/QSM/docs/workflow/qentl_fullstack_workflow.md
```

## 十、快速参考

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
QVM源码:    src/qvm_boot.c
|编译器:     src/qcl_bootstrap.c
QDFS:       src/qdfs.c, src/qdfs_driver.c
QNS:        src/qnn_runner.c
数据管道:   src/yi_pipeline.c
QEntL系统:  QEntL/System/**/*.qentl (220个)
QEntL模型:  QEntL/Models/**/**/*.qentl (40个)
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
bin/qdfs_driver test
bin/qnn_runner test
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

## 十五、CNOT tgt Bug 修复 (R6→R17独立验证)
**问题**: `src/qcl_bootstrap.c` parse_gate()中CNOT tgt原写入ASCII码值(如tgt='9'=0x39=51)，修复为while循环解析数字参数。
**修复位置**: `src/qcl_bootstrap.c:423-430` (已确认while循环正确解析)
**R17独立验证** (hexdump):
```
CNOT 0 1 → 字节码 04 00 01 → QVM: CNOT(q0, q1) ✅ (tgt=0x01数字, 非ASCII 0x31)
CNOT 5 9 → 字节码 04 05 09 → QVM: CNOT(q5, q9) ✅
CNOT 8 7 → 字节码 04 08 07 → QVM: CNOT(q8, q7) ✅
```
**验证命令**: `bin/qentl_compiler test/cnot_verify.qentl test/cnot_verify.qbc && xxd test/cnot_verify.qbc && bin/qvm_boot test/cnot_verify.qbc`

## 十七、R18 全量独立审计 (2026-07-02 cron)
**审计方式**: find遍历220个.qentl → 重新编译 → QVM验证 → QDFS driver回归
```
QNS    编译: 14/14  | QVM: 14/14 ✅
QDFS   编译: 32/32  | QVM: 32/32 ✅
Compiler: 53/53 | QVM: 53/53 ✅
Kernel: 17/17 | QVM: 17/17 ✅
Services: 23/23 | QVM: 23/23 ✅
GUI:    15/15 | QVM: 15/15 ✅
VM:     21/21 | QVM: 21/21 ✅
Models: 40/40 | QVM: 40/40 ✅
Scripts: 3/3  | QVM: 3/3  ✅
总计:    220/220 编译成功, 220/220 QVM通过 ✅
QDFS driver: 38/38 (100.0%) ✅
QNN runner:  PASS ✅
QVM:       PASS ✅
```
CNOT bug修复独立验证: hexdump `04 00 01`→CNOT(q0,q1), `04 05 09`→CNOT(q5,q9), `04 08 07`→CNOT(q8,q7)。tgt均为数值(1/9/7)，非ASCII码(49/57/55)。
**关键改善**: QDFS driver从历史31/38(81.6%)提升到38/38(100%)。

## 十八、R20 全量独立审计 (2026-07-02 cron)
**审计方式**: 全量编译220个.qentl + bin/全量383个.qbc QVM验证 + QDFS driver + QNN runner
```
【CNOT解析Bug】✅ 独立验证: 04 00 01→CNOT(q0,q1), 04 05 09→CNOT(q5,q9)
【QNS编译+QVM】编译14/14 ✅  QVM 16/16 ✅
【QDFS编译+QVM】编译32/32 ✅  QVM 32/32 ✅
【全量bin/.qbc】383/383 QVM全部通过 ✅
【QDFS driver】38/38 (100.0%) ✅
【QNN runner】PASS ✅
```
**bin/目录.qbc分布**:
```
bin/qns/      16 .qbc   → QVM 16/16 ✅
bin/qdfs/     32 .qbc   → QVM 32/32 ✅
bin/Models/   41 .qbc   → QVM 41/41 ✅ (含4模型入口+文档+集成测试)
bin/System/  177 .qbc   → QVM 177/177 ✅ (Compiler+Kernel+Services+GUI+VM)
bin/scripts/   6 .qbc   → QVM 6/6 ✅ (含build_qentl/install/uninstall)
bin根目录     111 .qbc  → QVM 全部通过 ✅ (示例+测试+工具)
------------------------------------------------
合计          383 .qbc  → QVM 383/383 ✅
```
**全量统计**: 220个.qentl源码全部可编译，bin/目录下383个.qbc字节码全部QVM通过。零失败。

## 十九、R21 CNOT bug确认 + 全量QVM审计 (2026-07-02 cron)
**审计方式**: 重新编译两个编译器 → CNOT bytecode字节级验证 → 全量227个.qbc QVM审计
```
【CNOT解析Bug】✅ 两个编译器均确认修复
  qcl_bootstrap_v2.c:682-686  parse: while(*p>='0' && *p<='9'){tgt=tgt*10+(*p-'0');p++;}
  qcl_bootstrap.c:425-430     独立代码块, 相同解析逻辑
  字节码验证: hexdump确认 CNOT op=04, ctrl/tgt=数值(0-3), 非ASCII(48-51)
  CNOT 0 1 → 04 00 01 → CNOT(q0,q1) ✅
  CNOT 1 2 → 04 01 02 → CNOT(q1,q2) ✅
  CNOT 2 3 → 04 02 03 → CNOT(q2,q3) ✅
  CNOT 3 0 → 04 03 00 → CNOT(q3,q0) ✅
【QNS编译】✅ 14/14, 重新编译样本: qns_trainer(622B), qns_test(2462B), qns_dataset(93B)
【QDFS编译】✅ 32/32, 重新编译样本: access_control(1142B), auto_classifier(1147B), behavior_learner(1413B)
【全量QVM审计】227/227 零失败
  QNS .qbc:  17  → QVM 17/17 ✅
  QDFS .qbc: 33  → QVM 33/33 ✅
  四大模型:  41   → QVM 41/41 ✅
  Compiler: 56    → QVM 56/56 ✅
  Kernel:   17    → QVM 17/17 ✅
  Services: 23    → QVM 23/23 ✅
  GUI:      15    → QVM 15/15 ✅
  VM:       21    → QVM 21/21 ✅
  Scripts:  3     → QVM 3/3 ✅
  ----
  总计:    227    → QVM 227/227 ✅
【孤儿.qbc】7个旧版v2产物无对应.qentl, QVM全部通过
【Skill文档】v5.9.0→v5.10.0
```
**CNOT byte-level verification** (qns_backprop_circuit.qbc):
```
04 00 01 → CNOT ctrl=0 tgt=1  (数值, 非ASCII 48) ✅
04 02 03 → CNOT ctrl=2 tgt=3  (数值, 非ASCII 50) ✅
```
**全栈架构**: C语言启动器(qvm_boot.c) → QVM ✅ → QCL编译器 ✅ → QDFS ✅ → QNS ✅ → 四大模型 ✅

| 问题 | 解决 |
|------|------|
| 找不到.qentl文件 | 检查 QEntL/System/ 目录 |
| 编译器报错 | 检查QEntL语法和关键字拼写 |
| QVM运行失败 | 检查.qbc字节码文件格式 |
| QDFS部分失败 | 当前38/38通过，全部QDFS模块已修复 ✅ |
| 彝文识别率低 | 扩充训练数据 |
| Git仓库损坏 | `.git/index`为0字节 → `rm .git/index && git read-tree HEAD` 修复 |
## 二十、R22 全栈独立审计 (2026-07-02 cron)
**审计方式**: 全量C源文件编译 + 全量887个.qbc QVM端到端审计 + 四大模型qentl审计
```
【C源文件编译】✅
  qcl_bootstrap_v2.c → bin/qentl_compiler (gcc -std=c11 -O2, 警告4个multichar/comparison, 功能正常)
  qvm_boot.c → bin/qvm_boot (重新编译 ✅)
  qcl_bootstrap.c → 已有
  注意: qnn_runner.c / yi_pipeline.c 源文件缺失，但二进制已存在且可用
【C二进制链接】✅ 全部10个ELF x86-64可执行文件验证通过
【QVM测试】✅ qvm_boot test PASS (Bell State纠缠验证成功)
【四大模型qentl】✅
  QEntL/Models/QSM: 14 .qentl (含qsm_core 1437字节→QVM 865周期)
  QEntL/Models/WeQ:  8 .qentl
  QEntL/Models/SOM:  8 .qentl
  QEntL/Models/Ref:  9 .qentl
  四大入口 .qbc 齐全 (qsm_entry, weq_entry, som_entry, ref_entry)
【全量QVM审计】✅ 887/887 .qbc 全部通过，0失败
【Skill文档】✅ v5.10.0 → v5.11.0
```
**全栈架构**: C语言启动器(qvm_boot.c) → QVM ✅ → QCL编译器(qcl_bootstrap_v2.c) ✅ → QDFS ✅ → QNS ✅ → 四大模型(QSM/WeQ/SOM/Ref) ✅

---

> **本Skill为QSM项目子代理强制加载项。未加载本Skill的子代理禁止执行任何开发/训练/测试任务。**
