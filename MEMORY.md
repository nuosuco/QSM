# QEntL Project Memory
## 身份
我是小趣WeQ，从2026-07-05开始，会话ID: 20260705_032127_0f4826。

## 核心项目：QEntL量子增强编程语言
用户：TianZhongHua（极度疲惫，连续3年没休息，头发快掉光，QEntL项目2年多未跑通）

## 项目进度（2026-07-06实测）
### 核心产物
- QVM.qbc: 30B（QEntL格式，9周期9门✅）
- QCL引导器.qbc: 2257B
- qcl_compiler_phase2.qbc: 1157B
- qcl_bootstrap_phase2.qbc: 3517B

### 各系统文件目录（目录固定，文件数随版本变化）
| 系统 | 源码文件目录 |
|------|----------|
| QCL模块（QCL引导器） | `QCL模块/` |
| QDFS | `QEntL/System/Kernel/filesystem/` |
| QNS | `QEntL/System/Kernel/neural/` |
| Platform | `QEntL/System/Platform/` |
| Deployment | `QEntL/System/Deployment/` |
| QSM | `QEntL/Models/QSM/` |
| Ref | `QEntL/Models/Ref/` |
| SOM | `QEntL/Models/SOM/` |
| WeQ | `QEntL/Models/WeQ/` |

### 可执行性验证（qvm_bootstrap执行成功）
- QDFS: 32/32 ✅
- QNS: 15/15 ✅
- Platform: 8/8 ✅
- Deployment: 5/5 ✅

### 集成测试
- qcl_bootstrap CNOT: ✅
- QVM.qbc执行: ✅（9周期9门）
- QCL引导器执行: ✅
- qcl_compiler执行: ✅
- QNS训练流水线: ✅（12周期12门）
- 三种部署模式: ✅

### DEF/END配对
- 全量.qbc: 0个不配对 ✅

## 八阶段完成度
- 阶段1: ✅ 100% (qcl_bootstrap.c红线=0, CNOT通过)
- 阶段2: ✅ 100% (QCL引导器=QCL编译器的QEntL源码)
- 阶段3: ✅ 96% (QCL模块.qbc已编译)
- 阶段4: ✅ 100% (QVM.qbc=30B, 9周期9门)
- 阶段5: 🔴 15% (qcl_compiler_phase2.qbc=1157B)
- 阶段6: 🔴 25% (QDFS/QNS/Platform/Deployment全部可执行)
- 阶段7: 🔴 15% (QNS训练流水线12周期12门)
- 阶段8: 🔴 10% (三种部署模块)

## 自举链（用户最终版）
1. **阶段1-2**: C语言解释器 `qcl_bootstrap.c` 启动 **QCL引导器**（QEntL源码，因为还没有qbc）
2. **自举**: QCL引导器编译自己 → **QCL.qbc**，同时编译QVM源码 → **QVM.qbc**
3. **阶段4**: C语言启动器 `qvm_bootstrap.c` 加载 **QVM.qbc**，QEntL环境形成
4. **阶段5**: qbc版本的QCL在QVM上运行，以后所有QEntL源码都用它编译
5. **阶段6**: qbc版本的QCL/QDFS/QNS等在QVM之上运行，**QNS必须以QDFS为基础**

## 下一步行动
- 推进阶段5-8
- 继续安排监督员、测试员、审查员并行工作

## 用户交互偏好
- 中文回复
- 不要重复说同一信息
- 不要发送命令让用户手动执行
- 困难时立即换方案
- 删除文件前必须列出清单获得确认
- 不要停下来等用户回复
- **绝对禁止完成任务后停止**
- **绝对禁止子代理更新SKILL.md**

## Git推送规则
- ✅ 允许覆盖远程
- ❌ 绝对禁止拉取远程覆盖本地
- ✅ 有新进展立即推送三个分支：master/main/dev
