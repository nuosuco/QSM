# QEntL Project Memory
## 身份
我是小趣WeQ (WeQueen)，从2026-07-05开始，会话ID: 20260705_032127_0f4826。

## 核心项目：QEntL量子增强编程语言
用户：TianZhongHua（极度疲惫，连续3年没休息，极度反感休眠/欺骗/搞糊涂）

## 八阶段流程
1. 红线修复（qcl_bootstrap.c红线=0）
2. QCL引导器编译产物（DEF/END配对）
3. qcl_phase2编译器解析修复（class语法+parse_compound_block）
4. qvm_bootstrap高级opcode解释
5. QCL编译器在QEntL环境中运行
6. QDFS+QNS+四大模型+5平台+3部署全量编译
7. QEntL全栈集成测试
8. QSM彝文训练+部署

## 最新实测进度 (2026-07-06 20:40)
### 阶段1-2: ✅ 100%
- qcl_bootstrap.c红线=0，CNOT回归8周期8门✅

### 阶段3: ✅ 94%+
- skip_brace_block=0，class语法已实现

### 阶段4: ✅ 45%+
- QVM.qbc执行2周期2门✅

### 阶段5: ✅ 12%+
- qcl_compiler_phase2编译自身1157B，函数=12✅

### 阶段6: ✅ 20%+
- QDFS=32, QNS=15, Platform=8, QSM=14, Ref=9, SOM=8, WeQ=8, Deployment=3, VM=30 全部编译✅

### 阶段7-8: 🔴 0%
- 待阶段6完成

## 质量审核真相
- **DEF/END统计方法**：必须只统计代码区（code bytes），不包含string_pool
- **代码区格式**：code_bytes + sp_len(2B LE) + string_pool
- **之前错误**：用全文件count()包含了string_pool里的字符'f'(102)和'g'(103)
- **QEntL 241个模块**：代码区DEF/END 0个不配对 ✅
- **全部444个.qbc**：代码区DEF/END 24个不配对（在docs/和build/compiled/旧文件）

## 集成测试通过
- qcl_bootstrap CNOT回归: 8周期8门 ✅
- qvm_bootstrap QVM.qbc: 2周期2门 EXIT=0 ✅
- qvm_bootstrap QCL引导器: 1周期1门 EXIT=0 ✅
- qvm_bootstrap qcl_compiler_phase2: 58周期58门 EXIT=0 ✅

## 配置 (3650天)
- run.py idle-TTL=315360000s
- config dispatch_stale_ttl_hours=87600
- config dispatch_stale_timeout_seconds=315360000
- compression: threshold=0.85, in_place=true, protect_last_n=50, target_ratio=0.3
