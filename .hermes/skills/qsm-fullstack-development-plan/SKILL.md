---
name: qsm-fullstack-development-plan
description: "QSM全栈开发完整方案 — 基于已读项目分析，QEntL全栈QSM能开发出来。四阶段构建方案+Skill+持续执行机制"
version: 1.0.0
author: 小趣WeQ
date: 2026-07-14
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [qentl, qsm, qvm, qdfs, qns, fullstack, development-plan, four-phases]
    related_skills: [qentl-fullstack, qsm-build]
---

# QSM 全栈开发完整方案

## 核心结论

**QEntL 全栈 QSM 能开发出来。**

理由：
1. 基础设施已完备（C启动器+QVM+QCL+341个.qentl+552个.qbc+训练数据）
2. 核心链路已打通（C启动器→QVM→QCL编译→.qbc运行）
3. 瓶颈可解决（运行时函数缺失、自举链断裂有明确修复路径）
4. 剩余工作量可控（阶段5-8主要是验证和集成）

## 四阶段构建方案

### 阶段1：修复自举链（最高优先级）

**目标**：让 QCL.qbc 在 QVM 上完整运行，编译所有 QEntL 源码

**具体任务**：
1. 修复 QVM 运行时函数缺失（print/len/read_source_file/get_directory_entries/is_directory）
   - 在 qvm_bootstrap.c 的 OP_FUNC_CALL_STMT 处理器中添加运行时函数路由
   - 对未定义的函数名检查是否为已知运行时函数名
   - 执行对应 C 逻辑

2. 修复 while 循环变量条件陷阱
   - 重构 QVM LoopFrame 添加 cond_pos 字段
   - 迭代时跳回 cond_pos 而非 body_start
   - 需要同时修改编译器（记录条件push的字节码位置）和QVM

3. 验证 QCL 引导器在 QVM 上完整运行
   - 编译 QCL_main.qentl → QCL_main.qbc
   - QVM 加载 QCL_main.qbc → 验证 exit=0
   - 验证 import 链加载所有 6 个 QCL_compiler 模块
   - 验证函数体扫描和嵌套深度正确

**验收标准**：
- QCL_main.qbc 在 QVM 上 exit=0
- import 链加载所有模块
- 114 处函数体扫描正确
- QVM 提供所有运行时函数

### 阶段2：QEntL 全量编译验证

**目标**：用 QCL.qbc 编译所有 .qentl 源码，生成 .qbc 字节码

**具体任务**：
1. 批量编译所有 .qentl 文件
   - 按 import 依赖拓扑排序
   - 先编译被导入的底层模块，再编译上层入口
   - 验证每个 .qbc 首字节 = 0x14

2. 全量 QVM 验证
   - 对所有 0x14 文件执行 bin/qvm_bootstrap
   - 统计 PASS/FAIL 比例
   - 修复失败的模块

3. 验证 DEF/END 配对
   - 用编译器输出 `函数=N` 为权威统计
   - 不能数字节码 255/254

**验收标准**：
- 所有 .qentl 编译为 .qbc
- 首字节 0x14
- QVM 全量 PASS ≥ 95%

### 阶段3：QDFS → QNS → 四大模型集成

**目标**：QDFS/QNS/四大模型在 QEntL 环境运行

**具体任务**：
1. QDFS 量子动态文件系统运行
   - 编译 QDFS 模块 → .qbc
   - QVM 加载运行
   - 验证文件 CRUD、叠加态、事务管理

2. QNS 量子神经叠加态运行
   - 编译 QNS 训练管道 → .qbc
   - QVM 加载运行
   - 验证训练周期执行

3. 四大模型协调
   - 编译 QSM/SOM/WeQ/Ref → .qbc
   - QVM 加载运行
   - 验证纠缠信道通信

**验收标准**：
- QDFS 32/32 模块 QVM PASS
- QNS 训练管道 exit=0
- 四大模型协调运行

### 阶段4：训练与部署

**目标**：QNS 训练彝文数据，三种部署验证

**具体任务**：
1. QNS 训练彝文数据
   - 加载 51,899 条彝文训练数据
   - 执行训练周期
   - 验证准确率 > 80%

2. 更新 Web 桌面量子助手 API
   - 训练成功后更新 API 配置
   - 验证三语对话（彝文/中文/英文）

3. 三种部署验证
   - 应用部署（解压即用）
   - 虚拟机部署（QVM 模拟）
   - Web QOS（浏览器访问）

**验收标准**：
- QNS 训练准确率 > 80%
- 三语对话测试通过
- 三种部署模式可用

## 持续工作机制

### 1. 后台持续编译进程

```bash
# 每 60 秒编译+测试一轮，永不停止
bash /root/QSM/run_continuous_build.sh
```

### 2. 状态跟踪

- 每次任务完成后更新 STATE.md
- 记录 round_number、status、time
- 验证结果写入 build_report/

### 3. 防欺骗机制

- 所有编译必须实际执行验证
- 不能声称完成但实际未验证
- 产物大小变化要有合理解释
- DEF/END 配对用编译器输出为准

## 风险与应对

| 风险 | 影响 | 应对方案 |
|------|------|----------|
| QVM 运行时函数修复复杂 | 高 | 分步修复，先修 print/len，再修文件操作 |
| 自举链修复时间超预期 | 中 | 先用 qcl_phase2.c 编译，不依赖 QCL.qbc |
| 训练数据格式不匹配 | 低 | 已有数据格式适配逻辑，微调即可 |
| QVM 死循环 | 高 | 已有 QVM_MAX_STEPS 上限，防止无限循环 |

## 执行顺序

1. **立即执行**：阶段1 - 修复自举链
2. **阶段1完成后**：阶段2 - 全量编译验证
3. **阶段2完成后**：阶段3 - 模块集成
4. **阶段3完成后**：阶段4 - 训练与部署

---

*方案制定于 2026-07-14，基于完整项目阅读和分析*
