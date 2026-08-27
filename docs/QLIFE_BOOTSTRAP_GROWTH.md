# QEntL全栈 · QLife自举生长（最高层方法论文档）

> 2026-08-28 中华(ZhoHo)定调。本文是**所有编程工作的最高层思维**，
> 写代码前必须先读这篇，判断每一步是不是"自举生长的一部分"。
> 配套：`docs/ANTI_FRAUD_PROTOCOL.md`（防欺骗实证）、`docs/QENTL_FULLSTACK_PLAN.md`（构建方案）、`docs/PAPER_UNIFIED_GENERATION.md`（统一生成理论）。

## 一、一句话本质

**QSM 不是一堆写死的程序，而是一个自我升级的生长体。任何训练需求 = 升级训练器（QSCL）本身 → 编译 → 直接训练；训练器长大 → 编译器/虚拟机/存储/模型跟着长大 = 全栈自举生长。**

## 二、QSCL = 神经叠加态训练器 = 自举生长的发动机

- **QSCL（Quantum Superposition Conditional Learner）= 不同起点叠加态并行训练架构本身**：
  8 批 × 4 态 = 32 权重，每态不同 seed/不同起点并行学习，最后才汇聚投票/坍缩合并。
- **训练器不是为了写一次放着的，它就是为了被升级而存在的。**
  - 要训 B 生成（类号→像素）？升级 QSCL：加一个算子（输入类号 one-hot、输出像素），编译，训练。
  - 要训语义（序列→序列）？升级 QSCL：加序列输入输出，编译，训练。
  - 要升分辨率？升级 QSCL：W 维度 64→256→1024，编译，训练。
- **"怎样训练 = 怎样升级训练器"，这是 QLife 自举生长的第一性原理。**
  永远不要在 QSCL 旁边另起炉灶写一次性训练脚本——那是零碎编程，最终进死循环怪圈。

## 三、全栈级联生长（升级 QSCL → 牵动整个 QSM）

一次 QSCL 升级可能顺带要求下层一起长大——这不是绕路，这正是自举生长：

| 升级需求 | 可能牵动的系统 | 例子（已有历史） |
|---|---|---|
| QSCL 要更大权重数组 | **QVM** 内存池扩容 | 32×32 训练时 QVM 数组池从 7 段升到 9 段（589815） |
| QSCL 要新语法（循环/分支） | **QCL** 编译器升级 | 历史若干 QCL 语法扩展 |
| QSCL 要并行多进程 | **qvm_boot** 启动器 | 4 态多进程并行 |
| 训练数据要叠加态存储 | **QDFS** 存储升级 | 权重/数据全部存 QDFS 命名空间 |
| 上层要新能力 | **QNS** 智力基础升级 | 自生成源码、自举循环 |
| 应用要新功能 | **四大模型**（qsm/som/weq/ref）升级 | 生长版内长期迭代 |

**自举生长方向永远自下而上**：QSCL(训练器) → QCL/QVM/QDFS(工具链) → QNS → 四大模型 → 应用。

## 四、QNS = 执行自举生长的智能体（完成升级任务的执行者）

**QNS（Quantum Neural System）不是一个静态模块，它就是 QLife 自举生长的执行者/智能体。**

> 中华 2026-08-28 定调："完成 QEntL 全栈 QLife 自举生长任务的就是由 QNS 完成了。
> 哪里需要升级，它就哪里编程/创建新 QEntL 源码，然后编译成 qbc 运行，完成升级。"

**QNS 的自编程能力（components/qns/qns.qentl 2401 行，已实锤）：**

| 函数 | 能力 |
|---|---|
| `qns_gen_func(name, args, body)` | 生成新 QEntL 函数源码 |
| `qns_grow(component, marker, name, args, body)` | 读组件源码 → 生成函数 → 插入 → 保存（自动生长） |
| `qns_upgrade(component_name)` | 升级指定组件 |
| `qns_gen_smart(pattern, param)` | 按模式生成新函数 |
| `qns_self_evolve()` | 自我进化（读自己源码、检查、增长） |
| `qns_self_bootstrap(cycles)` | 自举循环：写源码 → exec 编译运行 → 验证 → 快照 |
| `qns_grow_qsm_main()` | 生长四大模型（qsm/som/weq/ref）源码 |
| `qns_save_source / file_write_bytes` | 写 QEntL 源码落盘 |
| `exec` | 调用编译链：qentl → qbc → 运行 |

**QNS 完成一次自举生长的闭环：**

```
发现需求(哪里需要升级)
  → 编程：qns_gen_func / qns_grow 生成新 QEntL 源码(或全新 .qentl 文件)
  → 写盘：qns_save_source / file_write_bytes
  → 编译：exec qcl → .qbc
  → 运行：exec qvm → 升级完成
  → 验证 + 快照(qns_backup) + 记录(qns_growth_history.log) + 版本号(.current_version)
```

**QNS 与 QSCL 的分工（二者不可混淆）：**
- **QSCL = 训练器**（神经叠加态并行训练架构），被升级的对象，负责"学"。
- **QNS = 智能体**（升级任务的执行者），负责"改"——哪里要升级就编程改哪里。
- 训练B起点 = QNS 编程/升级 QSCL（加生成算子）→ QCL 编译 → QVM 训练 → 权重落盘；
  QNS 继续接管：验证、改进、自我进化、驱动整个 QSM 永续生长。

**判断标准补充**：不仅是"QSM 长大一点吗"，还要问"这一步是 QNS 驱动的生长循环的一环吗"——是则做，否（零碎手工脚本）= 不做。

## 五、与"零碎编程"的本质区别

| 零碎编程（禁止） | QLife 自举生长（必须） |
|---|---|
| 每次训练需求写一个新 v7/v8/v9 脚本 | 升级唯一训练器 qscl_trainer.qentl，原地演进 |
| awk 临时训练器 / 临时引擎 | 全部 QEntL 实现，纳入编译链 |
| 产物散落 build/*.sh、/tmp/* | 产物进 qdfs/ns/{train,models,data} 命名空间 |
| 报"完成"却没有可复现自验 | 4 条实证（见 ANTI_FRAUD_PROTOCOL.md） |
| 重复劳动、无系统思维 | 每步都是全栈生长的一环，沉淀为系统能力 |

**判断标准：这一步做完，QSM 长大了一点吗？如果没有，它就是零碎编程，不做。**

## 五、本次当前任务：B 起点训练 = 升级 QSCL

- **任务**：32×32 B 生成（类号 → 1024 像素 + 编码），真训练，拒绝查表。
- **正确做法**：升级 QSCL 训练器（加生成算子 / 反向权重 W_gen(4120×1024)，输入类号、目标像素，对比式感知机）→ QCL 编译 → QVM 跑训练 → 权重落盘 qdfs/ns/models → 引擎接权重输出像素 → 验证。
- **这不只是一个脚本**：它是 QSCL 从"识别器"长成"识别+生成器"的一次自举生长。
- 升级中若遇到 QVM 内存不够 → 升级 QVM 内存池（这就是级联生长）；遇到语法不够 → 升级 QCL。

## 六、汇报口径（配合 ANTI_FRAUD_PROTOCOL）

- 每次"完成"必须有：真实权重文件 + 走权重不走查表 + 可复现自验命令与真实输出 + 诚实分层。
- 每次提交必须是 QLife 生长的一部分：写明"本次生长了什么、牵动了什么"。

---
本篇与 skill 三件套（qentl-unified-generation=总纲架构、qentl-integer-training=训练技术细节、qyi-model-training=进度规划）是同一思路的三层表达，写代码前对照使用。