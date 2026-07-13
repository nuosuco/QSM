---
name: qentl-fullstack
description: "QEntL全栈跑通流程Skill — 八阶段自举流程、并行协作、训练测试迭代、防欺骗防休眠、汇报机制。所有子代理必须加载本Skill才能工作。详细构建流程见 /root/QSM/QEntL全栈构建与跑通方案.md"
version: 6.28.0
author: QSM Team
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [qentl, qsm, qvm, qdfs, qns, quantum, fullstack, workflow, eight-stage, anti-cheat, anti-sleep, cross-platform, qcl-phase2]
    related_skills: ["qsm-build"]
---

# QEntL 全栈跑通流程 Skill

> **强制加载规则**: 所有子代理启动后必须加载本Skill。未加载本Skill的子代理禁止执行任何开发/训练/测试任务。

> **⚠️ 必须最先执行**: 任何新会话、Cron唤醒、子代理启动，第一件事就是读取本Skill。不读Skill = 乱工作。**Cron唤醒后必须立即先读本Skill，然后立即并行启动多个子代理，绝不等用户响应！**

> **⚠️ 2026-07-09更新 - 大项目理解工作流**：详见 `references/massive-project-comprehension-workflow-2026-07-09.md`。分层阅读策略（结构扫描→文档→C源码→QEntL源码→扫描链接），5层共18-31次调用即理解663文件7.8MB规模的项目。**绝不让低智能模型做多文件系统构建**——商汤/Agnes等模型能跑单文件但不能做多文件系统链接、自举链理解、架构决策。

## ⚠️ 重要须知

**SKILL.md正文在2026-07-09因edit操作被截断**。详细方法论已转移至reference文件。要查看完整方法论，加载reference文件：

| 主题 | Reference文件 |
|------|--------------|
| 自举链架构 | `/root/QSM/QEntL全栈构建与跑通方案.md` |
| 阶段完成度 | `references/eight_stage_milestone_tracking_v30_2026_07_08.md` |
| 基线方法论 | `references/fullstack_baseline_v30_2026_07_08.md` |
| 反休眠规则 | `references/user-corrections-2026-07-06.md` |
| 大项目理解 | `references/massive-project-comprehension-workflow-2026-07-09.md` |
| 红线检测 | `references/fullstack_redline_verification_2026_07_08.md` |
| 集成测试 | `references/fullstack_integration_test_binary_output_trap_2026_07_07.md` |
| **纯QEntL项目清理** | `references/pure-qentl-project-cleanup-2026-07-09.md` |

## ⚠️ 大项目理解工作流（2026-07-09 新增）

> 详见 `references/massive-project-comprehension-workflow-2026-07-09.md`

**分层阅读顺序**：
1. 第一层：项目结构扫描（terminal：find + wc -l + 目录树）→ 2-3次调用
2. 第二层：核心文档优先（read_file：READEME/BUILD_ROADMAP/架构文档/项目状态）→ 5-8次调用
3. 第三层：C/核心源码（read_file限500行/次：编译器+启动器+运行时关键文件）→ 5-10次调用
4. 第四层：QEntL核心源码（read_file入口模块 + skill_view加载对应skill）→ 3-5次调用
5. 第五层：剩余文件结构扫描（search_files看import链接/def函数分布）→ 3-5次调用

**QSM项目实测**（2026-07-09）：663个需理解文件，7.8MB，用此策略约420K tokens进入context，18-31次调用。

**⚠️ 关键原则**：绝不让低智能模型做多文件系统构建。文件数统计用find实测不记旧值。分层顺序不可逆。

## ⚠️ 纯QEntL项目清理规则（2026-07-09 确立）

> **用户2026-07-09明确指令**：QSM项目只保留纯QEntL组件（.qentl/.qbc/.md）和两个C文件（qcl_bootstrap.c + qvm_bootstrap.c）。所有第三方依赖、Python脚本、shell脚本、备份文件、日志、模型权重全部删除。详见 `references/pure-qentl-project-cleanup-2026-07-09.md`。

### 必须保留的

| 类别 | 说明 |
|------|------|
| `src/qcl_bootstrap.c` | C解释器（唯一C文件1） |
| `src/qvm_bootstrap.c` | C启动器（唯一C文件2） |
| `bin/qcl_bootstrap` + `bin/qvm_bootstrap` | 编译好二进制 |
| 所有 `.qentl` 文件 | QEntL源码（387个） |
| 所有 `.qbc` 文件 | 字节码（954个） |
| 所有 `.md` 文件 | 文档（208个） |
| `web/` 前端 | Web UI |
| `data/` 训练数据 | QSM彝文数据集 |

### 必须删除的（一次性全部清空）

| 类别 | 删除命令 |
|------|---------|
| Python `.py` | `find . -name "*.py" -exec trash {} +` |
| Python `.pyc` + `__pycache__` | `find . -name "*.pyc" -exec trash {} +`; `find . -type d -name "__pycache__" -exec trash -r {} +` |
| 多余C文件 | 只保留 `qcl_bootstrap.c` + `qvm_bootstrap.c`，删除 `*_opt.c` `*_optimized.c` `test_*.c` |
| Shell `.sh` | `find . -name "*.sh" -exec trash {} +` |
| 备份 `.bak` | `find . -name "*.bak" -exec trash {} +` |
| 日志 `.log` | `find . -name "*.log" -exec trash {} +` |
| 模型 `.dat` `.epoch*` | `find . \( -name "*.dat" -o -name "*.epoch*" \) -exec trash {} +` |
| 损坏 `.corrupt*` | `find . -name "*.corrupt*" -exec trash {} +` |
| bin/多余二进制 | 只保留 `qcl_bootstrap` + `qvm_bootstrap`，删除 `*_opt` `*_stripped` `*_test` `*_old` `.new` 等 |
| src/二进制残渣 | 删除编译中间产物（.o文件、无扩展名二进制） |

### 注意事项

- 必须用 `trash`（trash-cli）而非 `rm`，确保可恢复
- 删除后必须验证：`find . -name "*.py" | wc -l` → 0；`find . -name "*.c" | sort` → 仅2个
- 清理后总文件数约1900+（含.qentl/.qbc/.md/web/data）
- 此规则适用于任何后续session重启后——项目已经是纯QEntL，**禁止重新引入Python/第三方依赖**

## 自举链（2026-07-09最终版，必须牢记！）

### 核心认知：QCL引导器 = QCL本身

**QCL引导器和QCL是同一套源码。** "引导器"只是因为第一次还没有.qbc，必须靠C解释器启动源码运行。一旦自举成功，它就是QCL编译器本身。引导器不是独立组件。

### 自举的本质

第一次（没有.qbc，只能用源码）:
1. C解释器 → 启动QCL源码运行成功
2. QCL编译自己 → QCL.qbc（数个文件）
3. QCL同时编译QVM源码 → QVM.qbc（数个文件）
4. C启动器 → 加载QVM.qbc → QVM运行成功 → **QEntL环境形成**

以后（有.qbc了，全部用qbc）:
1. QCL.qbc在QVM上运行 → 编译所有QEntL源码
2. QDFS.qbc构建出来 → 量子叠加态并行运算与运行的基础
3. QNS以QDFS为基础 → 四大模型以QNS为基础

### QDFS是整个QSM的基础

QDFS不只是文件系统——它是**量子叠加态并行运算与运行的基础**：装文件、加载数据，所有系统叠加态并行运算的底层支撑。没有QDFS，QNS没有数据可训练，四大模型没有数据可运行。**QDFS → QNS → 四大模型，依赖链不能乱。**

**核心原则**：
- C语言只能是启动器或解释器，不是编译器
- 只有两个C语言组件：`qcl_bootstrap.c`（解释器）和 `qvm_bootstrap.c`（启动器）
- QCL引导器 = QCL本身（同一套源码，"引导器"只是第一次以源码运行时的名字）
- 所有QEntL编译都通过QCL完成（第一次由C解释器启动QCL源码运行，以后由qbc版QCL编译）
- QEntL环境形成后全部用qbc，不再需要C解释器
- QDFS是整个QSM的基础 — 量子叠加态并行运算与运行的基础

**红线检测**：
```bash
grep -cP 'parse_(import|type|function|if|return|new|length|random)\\(&' src/qcl_bootstrap.c
# 必须返回0
```

## 相关Reference文件（80+个）

SKILL.md的reference文件目录下有80+个文件涵盖详细的编译调试方法、陷阱分析、修复记录。按需加载：

- `references/qcl_compilation_debugging.md` — QCL编译调试方法论
- `references/qcl-compilation-workflow.md` — 批量编译标准工作流
- `references/qvm_qbc_generation_workflow_2026_07_07.md` — QVM.qbc生成七步法
- `references/qcl_phase2_parse_def_fix_2026_07_05.md` — parse_def修复记录
- `references/qcl_phase2_compound_block_impl_2026_07_06.md` — parse_compound_block实现
- `references/qcl_phase2_class_method_body_wrap_2026_07_07.md` — class方法体修复
- `references/qcl_phase2_quantum_gate_opcode_mapping.md` — opcode映射表
- `references/user-corrections-2026-07-06.md` — 用户偏好和反休眠强制规则
- `references/main-agent-parallel-division-principle-2026-07-08.md` — 主代理/子代理分工
- `references/massive-project-comprehension-workflow-2026-07-09.md` — 大项目理解工作流

## 用户铁律

- **"绝对禁止休眠"** — 每次响应必须包含实际进展和下一步行动
- **"想尽一切办法解决休眠/欺骗问题"** — 不能只依赖Cron
- **"绝对禁止欺骗"** — 有工作就做，没工作就如实汇报
- **Git推送规则**：允许force push远程（远程老文件错误多）；禁止拉取远程覆盖本地