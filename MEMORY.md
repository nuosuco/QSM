# QSM 项目记忆

> 最后更新：2026-07-05 23:30（基线审计v9：qcl_compiler_phase2 退化壳修复 14B→202B/函数0→12/导入0→5，qcl_phase2.c 959→958行修正，引导器 IMPORT 新opcode=100下实测4，整体完成度修正42-45%非100%）

---

## 项目信息

- **仓库路径**：`/root/QSM`
- **核心文件**：`src/qcl_bootstrap.c`（C解释器）、`src/qvm_bootstrap.c`（C启动器）、`QCL引导器.qentl`
- **阶段**：8阶段全栈构建（详见 `QEntL全栈构建与跑通方案.md`）

---

## 基线数据（2026-07-05）

### 核心文件行数
| 文件 | 行数 |
|------|------|
| `src/qcl_bootstrap.c` | **247** |
| `src/qvm_bootstrap.c` | **244** |
| `QCL引导器.qentl` | **472** |
| `src/qcl_phase2.c` | **958** |

### 红线检测
| 指标 | 值 | 说明 |
|------|-----|------|
| `grep -cE 'parse_import\|parse_type\|parse_function' src/qcl_bootstrap.c` | **0** | ✅ 安全 |

### .qbc 字节码统计
| 类型 | 数量 |
|------|------|
| .qbc 总数 | **354** |
| 有效量子字节码（首字节0x14） | **297** |
| QCLF_MAGIC文本（0x46） | 52 |
| 空壳（0x0c/OP_STOP） | 4 |
| 其他（0x0b/0x01） | 1 |

### .qentl 源码统计
| 类型 | 数量 |
|------|------|
| .qentl 总数 | **341** |
| QCL模块 | 7 |
| 四大模型（QSM/Ref/SOM/WeQ） | 40 |
| 边界测试 .qbc | 16（在 `tests/qcl_phase2_boundary/`） |

### 四大模型
| 模型 | 文件数 |
|------|--------|
| QSM | 14 |
| Ref | 9 |
| SOM | 8 |
| WeQ | 8 |
| 集成测试 | 1 |

### 经典5平台
- ✅ `pe_format.qentl`（Windows PE）
- ✅ `macho_format.qentl`（iOS Mach-O）
- ✅ `elf_format.qentl`（Android/Linux ELF）
- ✅ `harmony_format.qentl`（鸿蒙 ELF/ARM）
- ✅ `platform_registry.qentl` + `platform_entry.qentl`（注册/入口）

### 量子3部署
- ✅ `development_mode.qentl`（开发/QVM本地模拟）
- ✅ `production_mode.qentl`（生产/云端QPU API）
- ✅ `specialized_mode.qentl`（专用/硬件QPU）

---

## 关键里程碑

### qcl_phase2 修复（2026-07-05）
- `src/qcl_phase2.c` 修复合并冲突（OP_SUB/OP_STOP/OP_PRINT去重）
- 与 `qcl_bootstrap.c` 同步操作码定义
- 重新编译 `bin/qcl_phase2`（ELF 64-bit LSB executable）
- **有效0x14从30暴增至297** — qcl_phase2批量重新编译成功
- 新增 `tests/qcl_phase2_boundary/` 边界测试（16个测试）
- `src/qcl_phase2.c` 当前有未提交修改（OP_STOP=12, OP_ADD=16等）
- CNOT回归通过：`bin/qcl_bootstrap test/cnot_r.qentl` → 27字节27条指令
- **v6更新**：parse_type_def emit修复 + 三件套误用修复 + OP_FUNC_END闭合修复 → qcl_phase2.c 928→959行，引导器产物319→335字节
- **⚠️ opcode重新映射**：`OP_IMPORT` 96→100，统计导入数时需用新值（导入仍为3，未退化）
- **v9更新**：`qcl_compiler_phase2.qentl` 退化壳修复 — 24行占位符(14字节/函数=0) → 204行编译器(202字节/函数=12/导入=5)，阶段5核心编译器不再阻塞

### 红线规则
- `qcl_bootstrap.c` 只能解释量子指令子集（init/H/X/Y/Z/T/S/CNOT/MEASURE/PRINT/STOP）
- **严禁**添加 `parse_import`/`parse_type`/`parse_function` 等高级语法解析
- 检测命令：`grep -cE 'parse_import\|parse_type\|parse_function' src/qcl_bootstrap.c` 必须 = 0

### 有效量子字节码（0x14）
- 首字节 0x14 = 有效量子字节码（QVM可执行）
- 首字节 0x72 = 无效文本（高级语法，C解释器跳过）
- 首字节 0x0c = 空壳STOP占位（C解释器跳过）
- 首字节 0x46 = QCLF_MAGIC文本头

### 八阶段状态（2026-07-05 23:30 审计v9，整体完成度 42-45%）

> ⚠️ 此前记忆将阶段3-8误标为全部 ✅ 完成，与实时状态严重不符（曾被误刷）。以下为实测修正值，以 qentl-fullstack skill v6.13.0 审计 v8 为准。

| 阶段 | 状态 | 说明 |
|------|------|------|
| Stage 1 | ✅ 完成 | qcl_bootstrap.c 247行，红线0，CNOT回归通过（27字节27条指令） |
| Stage 2 | ✅ 完成 | QCL引导器 472行，产物335字节，函数16，导入3 |
| Stage 3 | 🟡 修复中 | QCL模块7文件均成功emit；**qcl_compiler_phase2 退化壳已修复（14B→202B，函数0→12，导入0→5）**；残留：parse_var/if/return 高级控制流未验证 |
| Stage 4 | 🟡 阻塞 | qvm_bootstrap.c 244行已编译；**QVM.qbc=72字节仅为量子电路（非完整VM）→ 最大阻塞点** |
| Stage 5 | 🔴 阻塞 | 需阶段4 QEntL环境形成；qcl_compiler_phase2 退化壳已修复 |
| Stage 6 | 🔴 待开始 | 四大模型(29个)+System(197个).qentl 待编译 |
| Stage 7 | 🔴 待开始 | 需阶段6完成 |
| Stage 8 | 🔴 待开始 | 需阶段7完成 |

### QCL引导器系统结构
- **QCL引导器.qentl**：472行（L21-L54量子指令34行 + L56-L472高级语法108行）
- **QCL模块**：7个.qentl文件（3,621行）
  - `qcl_opcodes.qentl`（240行，20+函数）
  - `qcl_lexer.qentl`（730行，15+函数）
  - `qcl_parser.qentl`（618行，10+函数）
  - `qcl_parser_high.qentl`（1,258行，50+函数）
  - `qcl_bootstrap_phase2.qentl`（735行）
  - `qcl_compiler_phase2.qentl`（204行，12函数，202字节 — 2026-07-05 退化壳修复后）
  - `qcircuit`相关文件
- **编译器源码**：`QEntL/System/Compiler`（53个.qentl，28,662行）
- **QVM源码**：`QEntL/System/VM`（29个.qentl，15,110行）

### Hermes配置
- `gateway_auto_continue_freshness`: **31536000秒**（365天）
- `agent.max_turns`: 500
- WeCom企业微信连接永久保持在线
- cron定时任务已关闭

---

## 用户偏好与规则

1. **用户极度反感分析麻痹** — 接到任务立即执行，不要分析不要解释不要问
2. **用户极度反感重复执行** — 说一遍就记住，不重复执行
3. **用户极度反感"越做越把事情搞砸"** — 每次工具调用后立即启动下一个工具
4. **用户偏好先讨论再行动** — 当用户情绪激动或项目受挫时，应先汇报问题、确认理解、等用户指示
5. **用户通过WeCom企业微信连接** — 对话窗口永久保持在线，上下文持续保留
6. **关闭所有cron定时任务** — 365天会话保持已配置
7. **用户极度反感助手犯低级错误** — 严格按八阶段内容执行，不能马虎
8. **简化推进原则** — "不要乱搞，把两个C语言文件搞对，然后QCL引导器编译成QCL.qbc+QVM.qbc，QVM运行形成QEntL环境"

---

## 快速命令

```bash
# 红线检测
grep -cE 'parse_import\(|parse_type\(|parse_function\(' /root/QSM/src/qcl_bootstrap.c

# 文件行数
wc -l /root/QSM/src/qcl_bootstrap.c /root/QSM/src/qvm_bootstrap.c /root/QSM/QCL引导器.qentl

# 有效0x14统计
find /root/QSM -name '*.qbc' -not -path '*/.git/*' -type f -exec sh -c 'xxd -l1 -p "$1"' _ {} \; 2>/dev/null | grep -c "^14$"

# 全量编译+验证
cd /root/QSM && bin/qcl_phase2 QEntL/
```

---

## 历史基线对比

| 日期 | .qentl | .qbc | 有效0x14 | 红线 | 备注 |
|------|--------|------|----------|------|------|
| 2026-07-03 23:20 | 332 | 356 | 28 | 0 | 初始基线 |
| 2026-07-05 00:26 | 332 | 358 | 30 | 0 | 基线审计v3 |
| 2026-07-05 02:30 | **341** | **354** | **296** | **0** | qcl_phase2修复后重编译 |
| 2026-07-05 13:00 | **341** | **354** | **297** | **0** | 基线审计v4（qvm_bootstrap+1行, phase2+26行, 0x14+1, 边界测试8→16） |
| 2026-07-05 14:30 | **341** | **354** | **297** | **0** | 基线审计v6（qcl_phase2 928→959行：parse_type_def emit修复+三件套误用修复+OP_FUNC_END闭合修复） |
| 2026-07-05 23:30 | **341** | **354** | **297** | **0** | 基线审计v9（qcl_compiler_phase2退化壳修复14B→202B函数0→12导入0→5；qcl_phase2.c实测958行非959；引导器335B DEF=17/END=17/IMPORT=4；八阶段完成度修正42-45%非100%） |
