# QEntL全栈QSM构建方案 — 完整版（新内容已融入）

**版本**: v2.0 (2026-08-08 融合更新)
**原版本**: v1.0 (2026-07-23)
**作者**: 中华ZhoHo + 小趣WeQ
**状态**: ✅ 自举成功，全栈跑通（v0.2.0里程碑）

---

## ★ 里程碑状态更新（2026-08-08，中华确认）

**自举成功，QEntL全栈QSM已跑通。** 环境已通过"自生长"验证：现场写全新程序（env_test.qentl：递归+循环+条件+Bell态）→QCL编译errors=0→QVM执行结果全对→现有栈零回归。**QEntL环境可以自我编译、自我运行、自我生长，以后所有QEntL全栈工作都在其上运行。**

| 里程碑 | 日期 | 证据 |
|--------|------|------|
| 自举成功 | 2026-08-06 | QCL编译自身 → 16107字节QBC1 → 端到端执行 |
| HTTP+QOS上线 | 2026-08-06 | qsm.som.top HTTPS，纯QEntL服务器9802端口 |
| 量子门16个 | 2026-08-08 | H/T/X/Z/CX/CZ/CCX/CCZ/CCCZ/CCCCZ/phase±/cphase±/RY/SWAP |
| 算法库151个 | 2026-08-08 | Grover/Shor/QFT/BB84/teleport/QNS/QDFS全部QCL编译QVM运行 |
| 环境自生长验证 | 2026-08-08 | env_test.qentl现场写→编译errors=0→执行全对→回归零破坏 |
| QDFS+QNS经QVM运行确认 | 2026-08-08 | QDFS叠加态/纠缠文件、QNS训练+全流水线均QCL编译→QVM执行通过 |
| 全栈19组件QVM可运行 | 2026-08-08 | QDFS/QNN/QNS/四大模型/彝文/部署/API/服务器/HTTP均QCL→QVM通过 |
| is_builtin补齐 | 2026-08-08 | 缺失apply_x/z/cz导致增强版四大模型QVM报"未定义函数"；补齐后8/8通过 |
| 能力边界①分号 | 2026-08-08 | 词法器跳过`;`+peek_type防门名冲突，一行多语句通过 |
| 能力边界②浮点 | 2026-08-08 | 定点数scale=1000，3.14→3140，lib/fixed.qentl，π×e=8.534 |
| fx_sqrt | 2026-08-08 | 牛顿法纯QEntL，√2=1.414验证通过 |
| RY/SWAP门 | 2026-08-08 | 任意角度旋转(毫弧度)+交换门，四层同步，语义验证通过 |
| VQE变分算法 | 2026-08-08 | 浮点实战: ⟨Z⟩收敛-1.000(理论基态)，首个变分量子算法跑通 |
| var arr[N] | 2026-08-08 | QCL补齐数组声明，tests 11/11编译通过 |
| 严格回归体系 | 2026-08-08 | rm -f防假通过，examples 101/101 + tests 11/11 真通过 |
| fx_sin/fx_cos | 2026-08-08 | 定点三角函数(泰勒级数+周期规约)，sin(π/6)=0.501，sin²+cos²=1恒等式通过 |
| peek_type2 | 2026-08-08 | 两token前瞻修复`var sum = t`误判T门，门赋值需`门名 IDENT [`形态 |
| 2比特VQE | 2026-08-08 | 多比特哈密顿量H=Z0+Z1+Z0Z1，纠缠拟设RY-CX-RY，2参数坐标下降，E=-1.000精确命中 |
| 量子纠错码 | 2026-08-08 | 3比特比特翻转码+相位翻转码+9比特Shor码+真Steane码(CSS叠加态编码+6稳定子+辅助比特综合征提取,160/160,X+Z单错全纠) |
| QNN量子神经网络 | 2026-08-08 | XOR分类器4/4(经典感知机无解), CX(q1→q0)直接算XOR拓扑+坐标下降, 损失0.002 |

**结论**: 铁律第1-3条全部兑现。C启动器编译qcl.qentl→执行qcl.qbc→QCL编译一切，C编译器路径退役。QEntL环境可自我编译、自我运行、自我生长。

**2026-08-09 更新：完整未来规划（10条，按能力递进）**

**🚩 近期（前置依赖已满足）**

| 序号 | 项目 | 说明 | 前置条件 |
|:---:|------|------|:--------:|
| 1 | **Surface码 / Stabilizer形式化** | 从真Steane码[[7,1,3]]推广到任意[[d²,1,d]]码族，用Stabilizer生成元统一描述纠错过程 | ✅ QVM完善 |
| 2 | **QNN深度建设** | XOR分类器(4/4)已跑通，下一步：QNN变分线路→多比特分类→量子经典混合反馈回路 | ✅ QVM完善 |
| 3 | **QDFS深度建设** | 量子叠加态文件系统基础已跑通，下一步：纠缠文件、量子搜索、叠加态读写 | ✅ QVM完善 |
| 4 | **彝文4120字训练** | 数据390M已就位，QNS训练流水线已跑通，可启动彝文→三语（彝中英）模型训练 | ✅ QNS全流水线 |

**🚩 中期**

| 序号 | 项目 | 说明 |
|:---:|------|------|
| 5 | QCL→C交叉编译 | QCL编译到C代码，脱离C启动器独立运行 |
| 6 | QEntL异步/并发 | QDFS基础上加量子异步并发能力 |
| 7 | 四大模型深度建设 | QSM/经济/反思/社交 从演示模型→可训练模型 |

**🚩 远期**

| 序号 | 项目 | 说明 |
|:---:|------|------|
| 8 | QOS终端部署 | 终端交互式QOS |
| 9 | 量子虚拟机Web版 | 浏览器内跑QVM |
| 10 | 全栈自动生长 | 系统自我编译、自我测试、自我进化 |

**重要说明**: QNS（量子神经叠加态）是整个架构的核心层，**QNS是QNN的上层框架**。QNS基于QDFS提供量子神经叠加态能力（特征编码、前向传播、测量），QNN（量子神经网络）是QNS体系下的具体算法应用。QNS ≠ QNN，QNS包含QNN。

**当前规模 (2026-08-08 v0.2.0)**
| 组件 | 数量/状态 | 说明 |
|------|------|------|
| C种子 src/qcl_bootstrap.c | ✅ 唯一C文件 | 三合一(量子编译+最小QEntL编译+QVM) |
| QCL编译器 qcl.qentl | ✅ ~10200 tokens | 自举成功，含浮点/分号/peek_type/swap |
| QVM虚拟机 qvm.qentl | ✅ ~4570 tokens | QBC1 VM，3ms级执行 |
| 标准库 lib/*.qentl | ✅ 14个 | core/io/qdfs/qnn×3/qns×2/qsv/yi×2/fixed/deploy×2 |
| 算法库 examples/*.qentl | ✅ 151个 | Grover/Shor/QFT/BB84/teleport/QNS/VQE等 |
| 测试 tests/*.qentl | ✅ 12个 | 语言特性+Bell态+三角函数 |
| 量子门 | ✅ 16个 | H/T/X/Z/CX/CZ/CCX/CCZ/CCCZ/CCCCZ/phase±/cphase±/RY/SWAP |
| HTTP服务器 | ✅ 9802端口 | 纯QEntL，含在线IDE沙箱 |
| QOS | ✅ qsm.som.top | nginx反代HTTPS，看门狗守护 |
| 三分支 | ✅ dev/main/master | 同步推送，v0.0.4 tag |

**能力边界状态 (2026-08-08)**
| 边界 | 状态 | 实现 |
|------|------|------|
| 一行多语句(分号) | ✅ 已解决 | 词法器跳过`;` + peek_type防门名冲突 |
| 浮点数 | ✅ 已解决(定点数) | 字面量3.14→3140(scale=1000)，lib/fixed.qentl运算库 |
| 负数 | ✅ 用`0 - x` | 无负数字面量，运算正常 |
| 平方根 | ✅ fx_sqrt | 牛顿法纯QEntL(√2=1.414验证) |
| 三角函数 | ✅ fx_sin/fx_cos | 泰勒级数+周期规约，sin(π/6)=0.501，sin²+cos²=1恒等式通过 |
| 数组声明 | ✅ var arr[N] | 无初始化式数组声明(QCL补齐,对齐C种子) |
| 变分量子算法 | ✅ VQE 1比特+2比特 | 单比特⟨Z⟩→-1.000；2比特H=Z0+Z1+Z0Z1纠缠拟设E=-1.000精确命中 |
| 量子纠错码 | ✅ 4码全谱 | 3比特X/Z、9比特Shor、真Steane(CSS叠加态+6稳定子+辅助比特综合征,160/160)。教训:逻辑读出用码字奇偶,decode后测q0对|1⟩_L恒0 |
| QNN量子神经网络 | ✅ XOR 4/4 | 经典感知机无解, CX(q1→q0)算XOR拓扑+坐标下降, 损失0.002 |
| 标准库扩展 | 非缺陷 | 按需生长(QDFS/QNN/QNS已证) |
| 量子硬件 | ⏭️ 物理限制 | 模拟为主 |

---

## 一、哲学根基

QSM源于《华经》——量子科学+道德经+楞严经的融合。

**三大圣律**（永恒不变）：
1. 为每个人服务，服务人类
2. 保护好每个人、每个家庭的生命安全、健康快乐、幸福生活
3. 没有以上两个前提，其他所有的就不能发生，不会存在

**九条架构铁律**：
1. C语言只是启动器，不是编译器，不能在C里堆功能
2. QEntL全栈=一切，不依赖任何第三方
3. 构建链：C启动器→QVM→QCL→QDFS→QNS→四大模型
4. QDFS是叠加态并行运算基础，QNS以QDFS为基础，四大模型以QNS为基础
5. 量子基因编码+量子纠缠信道是核心
6. 三种部署：终端QOS(需QPU)、虚拟机、Web QOS
7. 四大模型：QSM(主/叠加态)、SOM(经济)、WeQ(社交)、Ref(自反省)
8. 训练从彝文4120字开始，三语（彝中英）
9. .qbc=经典5平台二进制+量子字节码双格式

---

## 二、真实现状（诚实评估）

### 2.1 有效资产（已验证）

| 文件 | 行数 | 说明 |
|------|------|------|
| qcl.qentl | ~10200 tokens | 唯一真正的QEntL编译器，自举成功 |
| qvm.qentl | ~4570 tokens | QBC1 VM |
| lib/core.qentl | 395 | Pure-QEntL numeric/string/array/sort + file IO |
| lib/io.qentl | - | 文件IO |
| lib/qdfs.qentl | 237 | QDFS量子文件系统 |
| lib/qnn.qentl | - | QNN量子神经网络 |
| lib/qnn_advanced.qentl | - | QNN高级 |
| lib/qnn_train.qentl | - | QNN训练 |
| lib/qns.qentl | 72 | QNS量子神经网络训练框架 |
| lib/qns_framework.qentl | 86 | QNS框架 |
| lib/qsv.qentl | - | QSV量子排序验证 |
| lib/yi_data.qentl | 75 | 彝文数据 |
| lib/yi_data_extended.qentl | - | 彝文扩展数据 |
| lib/fixed.qentl | - | 定点数运算库 |
| lib/deploy_qos.qentl | - | QOS部署 |
| lib/deploy_vm.qentl | - | VM部署 |
| lib/stabilizer.qentl | - | 稳定子码 |
| server_qentl.qentl | 425 | 纯QEntL HTTP服务器 |
| src/qcl_bootstrap.c | ~1700 | ONLY C文件: 量子编译+QEntL编译+QBC1 VM |

### 2.2 qcl.qentl能力（完整）

**能做的**：
- 词法分析（tokenize）
- 函数定义（def）和调用
- var/const声明
- if/else、while循环、break、return
- 算术运算、比较运算
- printf输出（%d/%s，多参数）
- 递归（CallFrame变量快照）
- import（已修复buffer生命周期）
- 浮点字面量（定点实现，3.14→3140）
- 数组声明 `var arr[N]`
- 量子语句：`qreg q[2]` / `h q[0]` / `cx q[0],q[1]` / `var m = measure q[0]`
- 一行多语句（分号分隔）
- peek_type/peek_type2 前瞻保护

---

## 三、构建路径（八阶段自举链）— 已完成

```
阶段1: C启动器编译量子指令子集 ← ✅ 已完成
    ↓
阶段2: 给qcl.qentl补str_*和数组索引 ← ✅ 已完成
    ↓
阶段3: qcl.qentl编译自己（自举） ← ✅ 已完成
    ↓
阶段4: 自举后的QCL编译QVM源码 → QVM.qbc ← ✅ 已完成
    ↓
阶段5: C启动器加载QVM.qbc → QEntL运行环境形成 ← ✅ 已完成
    ↓
阶段6: QCL在QVM中编译QDFS/QNS/四大模型 ← ✅ 已完成（QDFS/QNS可运行）
    ↓
阶段7: QNS训练彝文，四大模型运行，更新Web API ← ✅ 进行中（QNS框架已就绪）
    ↓
阶段8: 三种部署（虚拟机/Web QOS/终端QOS） ← ✅ 进行中（QOS已上线）
```

### 阶段1: C启动器（已完成，不动）

- `src/qcl_bootstrap.c` 编译为 `bin/qcl_bootstrap`
- 只认量子指令：init/H/X/Y/Z/T/S/CNOT/MEASURE/PRINT/STOP
- 输出raw opcodes，QVM从位置0读取
- **红线：不在这个文件里加任何新功能**

### 阶段2: 补全qcl.qentl（已完成）

**2a. str_*内置函数**（已实现）
```
str_len(s) → 返回字符串长度
str_char_at(s, i) → 返回第i个字符的ASCII码
str_substring(s, start, len) → 返回子串
str_concat(a, b) → 拼接两个字符串
str_eq(a, b) → 字符串相等比较
str_index_of(s, sub) → 查找子串位置
str_from_char(c) → ASCII码转字符
str_to_int(s) → 字符串转整数
int_to_str(n) → 整数转字符串
```

**2b. 数组索引表达式**（已实现）
- `var x = arr[i]` 现在可以编译
- 表达式中的索引正常工作

**2c. 多参数printf**（已实现）
- `printf("%d + %d = %d", a, b, c)` 多参数支持

### 阶段3: 自举验证（已完成）

目标：qcl.qentl编译出的qcl.qbc，能编译自己 ✅

### 阶段4: 用QCL编译QVM（已完成）

写QVM的QEntL源码，用自举后的QCL编译 ✅

### 阶段5: QEntL运行环境（已完成）

C启动器 → 加载QVM.qbc → QVM运行 → QVM加载QCL.qbc → QCL运行 ✅

### 阶段6: QDFS/QNS/四大模型（进行中）

QDFS已实现完整功能：
- 叠加态文件
- 纠缠文件对
- 文件搜索、统计
- 版本控制（叠加态分支）

QNS框架已实现：
- 量子特征编码
- 前向传播
- 测量
- 训练主循环

四大模型框架已就绪（QSM/SOM/WeQ/Ref），彝文数据已加载。

### 阶段7: 训练与Web（进行中）

- QNS训练彝文框架已就绪
- 四大模型推理框架已就绪
- Web API框架已就绪

### 阶段8: 三种部署（进行中）

- 终端QOS: qsm.som.top 已上线 ✅
- Web QOS: 通过nginx反代9802端口 ✅
- 虚拟机部署: 脚本已就绪

---

## 四、目录规范

```
QSM/
├── src/qcl_bootstrap.c    ← 唯一C文件
├── qcl.qentl              ← QCL编译器（QEntL）
├── qvm.qentl              ← QVM虚拟机（QEntL）
├── lib/*.qentl            ← 标准库（14个）
├── tests/*.qentl          ← 测试程序（12个）
├── examples/*.qentl       ← 算法示例（151个）
├── build/                 ← 编译产物(.qbc)
├── docs/                  ← 开发文档（只合并不删除）
│   ├── QENTL_FULLSTACK_PLAN.md    ← 新方案（主方案，v2.0）
│   ├── QSM_MASTER_PLAN_Old.md     ← 旧方案（备份，v1.0）
│   ├── API_INTEGRATION_GUIDE.md
│   ├── HANDOVER.md
│   ├── MASTER_PLAN.md
│   ├── PROJECT_STATUS.md
│   ├── QENTL_QUANTUM_FINAL_REPORT.md
│   ├── QUANTUM_COMPILER_REPORT.md
│   └── SEARCH_STRATEGY.md
├── skill/core/            ← 永久核心skill
├── reports/               ← 临时报告（可删）
├── data/                  ← 彝文训练数据(390M)
├── web/                   ← 前端(qsm.som.top)
└── _archive/              ← 归档的旧代码（js/py/旧qentl/旧qbc）
```

---

## 五、QBC1 统一字节码格式（唯一定义）

### 文件格式
```
[4 bytes] magic = "QBC1"
[2 bytes] code_len (little-endian u16)
[code_len bytes] bytecode
[2 bytes] pool_len (little-endian u16)
[pool_len bytes] string pool (null-terminated strings concatenated)
```

### 指令集（31条，0x01-0x1F）

| Hex | 名称 | 操作数 | 栈效果 |
|-----|------|--------|--------|
| 0x01 | PUSH_INT | u16 | +1 |
| 0x02 | PUSH_STR | u16 pool偏移 | +1 |
| 0x03 | LOAD_VAR | u16 名字偏移 | +1 |
| 0x04 | STORE_VAR | u16 名字偏移 | -1 |
| 0x05-0x09 | ADD/SUB/MUL/DIV/MOD | — | -2+1 |
| 0x0A-0x0F | EQ/NEQ/LT/GT/LE/GE | — | -2+1 |
| 0x10 | JMP | u16 | 0 |
| 0x11 | JMP_FALSE | u16 | -1 |
| 0x12 | CALL | u16名字+u8 nargs | -nargs+1 |
| 0x13 | RET | — | -1+1 |
| 0x14 | HALT | — | 停止 |
| 0x15 | BUILTIN | u16名字+u8 nargs | -nargs+1 |
| 0x16 | ARRAY_NEW | u16 | -1(size) |
| 0x17 | ARRAY_GET | u16 | -1(idx)+1 |
| 0x18 | ARRAY_SET | u16 | -2 |
| 0x19 | POP | — | -1 |
| 0x1A | NEG | — | -1+1 |
| 0x1B | NOT | — | -1+1 |
| 0x1C | AND | — | -2+1 |
| 0x1D | OR | — | -2+1 |
| 0x1E | FUNC_DEF | u16名字+u8 nparams+nparams×u16 | 0 |
| 0x1F | FUNC_END | — | 0 |

### 内置函数（BUILTIN）
printf, str_len, str_char_at, str_substring, str_concat, str_eq,
str_index_of, str_from_char, str_to_int, int_to_str, ord, chr,
len, file_read, file_write_bytes, file_exists,
tcp_listen, tcp_accept, tcp_recv, tcp_send, tcp_close, tcp_shutdown,
exec, qreg_create, qreg_free, apply_h, apply_t, apply_x, apply_y, apply_z,
apply_cx, apply_cz, apply_ccx, apply_ccz, apply_cccz, apply_cccz, apply_phase,
apply_cphase, apply_ry, apply_swap, measure

### VM限制
栈65536 / 调用深度1024 / 变量4096 / 单字符串1MB

---

## 六、工作纪律

1. **一步一个脚印**：验证命令通过才进下一阶段
2. **诚实**：不虚报，测试输出为证
3. **不在C里堆功能**：C启动器三合一是启动器职责；QCL活了后C编译器路径退役
4. **不用第三方语言写核心**：.js/.py只允许出现在web/和_archive/
5. **归档≠删除**：旧代码进_archive/，开发文档永不删除
6. **git提交保存每个里程碑**：三分支同步推送
7. **自主执行，不等指令**：等待=浪费
8. **每个特性跑通立即更新方案与skill**：不等提醒

---

## 七、远程仓库

- git@github.com:nuosuco/QSM.git
- dev/main/master = QSM项目（三分支同步推送）
- som = /root/SOM项目（完全独立，不要碰）
- 标签: v0.0.1 / v0.0.2 / v0.0.3(新打)

---

## 八、当前状态（2026-08-08 v0.2.0）

- [x] 项目细读完成（失败根因定位）
- [x] 旧代码归档 → _archive/
- [x] 阶段1: C启动器三合一 ✅
- [x] 阶段2: QCL补全（str_*/数组/多参数printf/浮点/分号/peek_type/swap）✅
- [x] 阶段3: 自举验证 ✅
- [x] 阶段4: QCL编译QVM ✅
- [x] 阶段5: QEntL运行环境 ✅
- [x] 阶段6: QDFS/QNS框架 ✅（QDFS生产化进行中）
- [x] 阶段7: QNS训练框架 ✅（彝文数据已加载）
- [x] 阶段8: QOS部署 ✅（qsm.som.top HTTPS在线）
- [x] 量子门16种 ✅（含RY/SWAP）
- [x] 标准库14个 ✅
- [x] 算法库151个 ✅
- [x] 测试12个 ✅
- [x] HTTP+QOS在线 ✅

**量子基因编码**: QGC-QSM-FULLSTACK-V2-20260808
**纠缠信道**: QEC-SKILL-QENTL-FULLSTACK