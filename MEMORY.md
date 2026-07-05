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

## 项目总进度统计 (2026-07-05 更新)
> 扫描全量 .qentl + .qbc（排除 .git/__pycache__/venv 等隐藏目录，排除空文件；.qbc 代码区用 sp_len(2B LE) 边界识别，DEF/END 仅统计代码区 opcode 0x66/0x67）

### 文件总数
| 指标 | 数值 |
|------|------|
| .qentl 总数 | **340** |
| .qbc 总数 | **520** |
| 文件合计 | **860** |

### .qentl 源码统计
| 指标 | 数值 |
|------|------|
| 总代码行数 | **180,965 行** |
| 总文件大小 | **5,881,888 字节 (5.6 MB)** |
| 代码区函数总数 (def) | **154** |

### .qbc 字节码统计
| 指标 | 数值 |
|------|------|
| 有效 0x14 首字节文件数 | **516** |
| 含量子指令(0x01–0x08)文件数 | **488** |
| 代码区 DEF (0x66) 数 | **1,027** |
| 代码区 END (0x67) 数 | **1,016**（配对率 98.9%） |
| 代码区 DEF+END 总数 | **2,043** |
| 量子指令总数 (0x01–0x08) | **21,257** |
| 代码字节量 | **88,348 字节** |
| 总文件大小 | **180,028 字节 (175.8 KB)** |

### 汇总
| 指标 | 数值 |
|------|------|
| 函数总数 | **1,181**（.qentl def 154 + .qbc DEF 1,027） |
| 量子指令总数 | **21,257+**（.qbc 代码区 0x01–0x08，不含 .qentl 源码关键词） |

### 阶段6分类进度（.qbc）
- QDFS=32, QNS=15, VM=30, Platform=8, QSM=14, Ref=9, SOM=8, WeQ=8, Deployment=3, 其他=342 ✅

## 最新实测进度 (2026-07-06 23:00)

### 集成测试状态
- **QEntL 241 个模块全部编译通过** ✅
- **DEF/END：0 个不配对** ✅（全部配对完整）
- **集成测试：3/4 通过** ⚠️（4 项中 3 项完全通过，1 项需关注）
  - ✅ qcl_bootstrap CNOT回归: 8周期8门
  - ✅ qvm_bootstrap QVM.qbc: 2周期2门 EXIT=0
  - ✅ qvm_bootstrap QCL引导器: 1周期1门 EXIT=0
  - ✅ qvm_bootstrap qcl_compiler_phase2: 58周期58门 EXIT=0

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
