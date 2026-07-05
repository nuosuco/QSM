# QEntL Project Memory
## 身份
我是小趣WeQ，从2026-07-05开始，会话ID: 20260705_032127_0f4826。

## 核心项目：QEntL量子增强编程语言
用户：TianZhongHua（极度疲惫，连续3年没休息，头发快掉光，QEntL项目2年多未跑通）

## 项目进度（2026-07-06实测）
### 核心产物
- QVM.qbc: 73B（来自vm_main.qentl，可执行，0周期0门）
- QCL引导器.qbc: 2257B
- qcl_compiler_phase2.qbc: 1157B
- qcl_bootstrap_phase2.qbc: 3517B

### 各系统文件数量（要求≥5个，源码文件都在同一目录下）
- **QCL模块（QCL引导器 = QCL编译器源码）**: **7个.qentl** ✅（不需要qbc，qbc是编译产物）
- QDFS: 32 .qentl
- QNS: 15 .qentl
- Platform: 8 .qentl
- Deployment: 5 .qentl
- QSM: 14 .qentl
- Ref: 9 .qentl
- SOM: 8 .qentl
- WeQ: 8 .qentl

### 集成测试
- qcl_bootstrap CNOT: ✅
- QVM.qbc执行: ✅
- QCL引导器执行: ✅
- qcl_compiler执行: ✅
- QNS训练流水线: ✅（12周期12门）
- 三种部署模式: ✅（规格定义，0周期0门正常）

### DEF/END配对
- 全量.qbc: 0个不配对 ✅

## 八阶段完成度
- 阶段1: ✅ 100% (qcl_bootstrap.c红线=0, CNOT通过)
- 阶段2: ✅ 100% (QCL引导器.qentl=QCL编译器源码)
- 阶段3: ✅ 96% (QCL模块.qbc已编译)
- 阶段4: 🟡 55% (QVM.qbc=73B)
- 阶段5: 🔴 15% (qcl_compiler_phase2.qbc=1157B)
- 阶段6: 🔴 25% (QDFS/QNS/Platform/Deployment/Models)
- 阶段7: 🔴 10% (QNS训练流水线执行成功，12周期12门)
- 阶段8: 🔴 10% (三种部署模块已就绪)

## 2026-07-06用户核心教导（必须牢记，绝不重复说！）
1. **QCL引导器 = QCL编译器的7个源码文件**（QCL模块目录下），不需要qbc（qbc是编译产物，不属于引导器本身）
2. **自举过程**：C语言解释器启动QCL源码 → 编译自己所有QEntL源码为qbc → qbc版本的QCL在QVM上运行
3. **每个系统的源码文件都在同一个文件目录下**，统计必须准确
4. **统计必须准确，不能出错**——第一次统计30个是错误的，正确是7个
5. **所有系统必须≥5个文件**（除了两个C解释器/启动器）
6. **QNS必须以QDFS为基础**
7. **方案与skill必须同时更新**，绝不再漏！

## 下一步行动
1. 推进八阶段7-8的后续工作
2. 不再重复汇报已确认的信息
3. 统计系统文件数量时只统计源码（.qentl），不统计编译产物（.qbc）

## 用户交互偏好
- 中文回复
- 不要重复说同一信息
- 不要发送命令让用户手动执行
- 困难时立即换方案
- 删除文件前必须列出清单获得确认
- 不要停下来等用户回复
- **绝对禁止完成任务后停止**

## Git推送规则
- ✅ 允许覆盖远程
- ❌ 绝对禁止拉取远程覆盖本地
- ✅ 有新进展立即推送三个分支：master/main/dev