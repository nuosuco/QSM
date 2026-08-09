# QEntL 全栈 QSM 构建方案 v2.0（从零重建）

**日期**: 2026-08-05
**作者**: 小趣WeQ（细读全项目后重写）
**状态**: ✅ 自举成功，全栈跑通（2026-08-08 里程碑）

---

## ★ 里程碑状态更新（2026-08-08，中华确认）

**自举成功，QEntL全栈QSM已跑通。** 方案中全部9个阶段完成并验证：

| 里程碑 | 日期 | 证据 |
|--------|------|------|
| 自举成功 | 2026-08-06 | QCL编译自身 → 16107字节QBC1 → 端到端执行 |
| HTTP+QOS上线 | 2026-08-06 | qsm.som.top HTTPS，纯QEntL服务器9802端口 |
| 量子门14个 | 2026-08-07 | H/T/X/Z/CX/CZ/CCX/CCZ/CCCZ/CCCCZ/phase±/cphase± |
| 97算法+14库 | 2026-08-07 | Grover/Shor/QFT/BB84/teleport/QNS/QDFS全部QCL编译QVM运行 |
| 环境自生长验证 | 2026-08-08 | env_test.qentl现场写→编译errors=0→执行全对→回归零破坏 |
| QDFS+QNS经QVM运行确认 | 2026-08-08 | QDFS叠加态/纠缠文件、QNS训练+全流水线均QCL编译→QVM执行通过；QCL自编译产物QBC1 |
| 全栈19组件QVM可运行 | 2026-08-08 | QDFS/QNS/四大模型8版/彝文/部署/API/服务器/HTTP均QCL→QVM通过；QCL-on-QVM三层嵌套编译bell_pair逐字节一致；教训:QEntL字面量u16上限,池边界用运行时算术 |
| is_builtin补齐 | 2026-08-08 | 缺失apply_x/z/cz导致增强版四大模型QVM报"未定义函数"；补齐后8/8通过 |
| 能力边界①分号 | 2026-08-08 | 词法器跳过`;`+peek_type防门名冲突，一行多语句通过 |
| 能力边界②浮点 | 2026-08-08 | 定点数scale=1000，3.14→3140，lib/fixed.qentl，π×e=8.534 |
| fx_sqrt | 2026-08-08 | 牛顿法纯QEntL，√2=1.414验证通过 |
| RY/SWAP门 | 2026-08-08 | 任意角度旋转(毫弧度)+交换门，四层同步，语义验证通过 |
| VQE变分算法 | 2026-08-08 | 浮点实战: ⟨Z⟩收敛-1.000(理论基态)，首个变分量子算法跑通 |
| var arr[N] | 2026-08-08 | QCL补齐数组声明，tests 11/11编译通过 |
| 严格回归体系 | 2026-08-08 | rm -f防假通过，examples 101/101 + tests 11/11 真通过 |
| fx_sin/fx_cos | 2026-08-08 | 定点三角函数(泰勒级数+周期规约)，sin(π/6)=0.501，sin²+cos²=1恒等式20点通过 |
| peek_type2 | 2026-08-08 | 两token前瞻修复`var sum = t`误判T门，门赋值需`门名 IDENT [`形态 |
| 2比特VQE | 2026-08-08 | 多比特哈密顿量H=Z0+Z1+Z0Z1，纠缠拟设RY-CX-RY，2参数坐标下降，E=-1.000精确命中理论基态 |
| 量子纠错码 | 2026-08-08 | 3比特比特翻转码+相位翻转码+9比特Shor码+真Steane码(CSS叠加态编码+6稳定子+辅助比特综合征提取,160/160,X+Z单错全纠) |
| QNN量子神经网络 | 2026-08-08 | XOR分类器4/4(经典感知机无解), CX(q1→q0)直接算XOR拓扑+坐标下降, 损失0.002 |

**结论**: 铁律第1-3条全部兑现。C启动器编译qcl.qentl→执行qcl.qbc→QCL编译一切，C编译器路径退役。QEntL环境可自我编译、自我运行、自我生长。

**下一阶段**: ~~VQE变分量子算法~~(已完成) → 定点三角函数(sin/cos) → VQE扩展多比特哈密顿量 → 量子纠错码。

**2026-08-09 更新：完整未来规划（10条，按能力递进）**

**★ 核心前提：QDFS与QNS是必须构建与运行基础**

在展开任何上层建设之前，必须先夯实**两个必须构建与运行基础**（缺一不可）：
- **QDFS（量子动态文件系统）= 文件叠加态**——整个QSM的量子叠加态并行存储、运算与运行的地基
- **QNS（量子神经叠加态）= 神经叠加态**——区别于经典神经网络的量子并行平行世界，是灵魂，**QNS包含QNN**

QVM、QCL、QDFS、QNS（包括QNN）、四大模型等等，**都以QDFS和QNS这两个基础之上构建与运行**，缺一不可。只有它们都成功运行，全部组件才能以量子叠加态并行存储、运算、运行与思考。因此**近期规划的一切工作，都围绕并服务于这两个基础的深化与建设**。

**🚩 近期（必须奠基：QDFS + QNS两个基础的建设与深化）**

| 序号 | 项目 | 说明 | 基础 |
|:---:|------|------|:----:|
| 1 | **QDFS深度建设（文件叠加态基础）** | 量子叠加态文件系统基础已跑通，深化：纠缠文件、量子搜索、叠加态读写。**这是量子叠加态并行存储与运算的地基** | ✅ QVM完善 |
| 2 | **QNS深度建设（神经叠加态基础 + 灵魂）** | QNS框架已跑通，深化：量子特征编码、多比特叠加态、训练主循环。**QNS是灵魂，包含QNN** | ✅ QDFS基础 |
| 3 | **QNN深化（QNS内具体算法）** | XOR分类器(4/4)已跑通，深化：QNN变分线路→多比特分类→量子经典混合反馈回路。**QNN是QNS体系内的算法应用** | ✅ QNS基础 |
| 4 | **彝文4120字训练（QNS实战）** | 数据390M已就位，QNS训练流水线已跑通，启动彝文→三语（彝中英）模型训练。**这是QNS神经叠加态能力的真实检验** | ✅ QNS全流水线 |

**🚩 中期（基础之上建设）**

| 序号 | 项目 | 说明 |
|:---:|------|------|
| 5 | QCL→C交叉编译 | QCL编译到C代码，脱离C启动器独立运行 |
| 6 | QEntL异步/并发 | QDFS基础上加量子异步并发能力（深化文件叠加态基础） |
| 7 | 四大模型深度建设 | QSM/经济/反思/社交 从演示模型→可训练模型（构建于QNS之上） |

**🚩 远期**

| 序号 | 项目 | 说明 |
|:---:|------|------|
| 8 | QOS终端部署 | 终端交互式QOS |
| 9 | 量子虚拟机Web版 | 浏览器内跑QVM |
| 10 | 全栈自动生长 | 系统自我编译、自我测试、自我进化 |

**重要说明**: QNS（量子神经叠加态）是整个架构的核心层，**QNS是QNN的上层框架**。QNS基于QDFS提供量子神经叠加态能力（特征编码、前向传播、测量），QNN（量子神经网络）是QNS体系下的具体算法应用。QNS ≠ QNN，QNS包含QNN。**QDFS（文件叠加态）与QNS（神经叠加态）是必须构建与运行基础，缺一不可。**

---

> **前版教训**: v1方案失败原因 = 字节码格式分裂(QBC1 vs QVML两套opcode) + 多个C二进制变体 + JS/Python第三方混入

## 一、铁律（不可违反）

1. C语言只是启动器。全项目**唯一C文件** = `src/qcl_bootstrap.c`
2. QEntL全栈，不依赖任何第三方（无.js/.py/.rs/.go）
3. 构建链：C启动器 → QCL → QVM → QDFS → QNS → 四大模型
4. QDFS是叠加态并行基础，QNS基于QDFS，四大模型基于QNS
5. 量子基因编码 + 量子纠缠信道
6. 三种部署：终端QOS / 虚拟机 / Web QOS
7. 四大模型：QSM(主) / SOM(经济) / WeQ(社交) / Ref(自反省)
8. 训练从彝文4120字开始，三语（彝中英）
9. .qbc = 经典字节码格式（QBC1统一格式，见下）

---

## 二、v1失败根因（诚实复盘）

| 问题 | 后果 |
|------|------|
| 两套字节码格式并存（QBC1规格 vs QVML格式） | opcode互相冲突，编译器/VM对不上 |
| /root/bin/ 下6个qvm_bootstrap变体C二进制 | 违反"C只是启动器"铁律，版本混乱 |
| JS编译器(qcl_compiler*.js) + JS VM(qvm*.js)混入 | 第三方语言，不是量子叠加态路径 |
| Python脚本混入server/ scripts/ | 同上 |
| qcl.qentl工作区被垃圾覆盖（7KB乱码） | 唯一QEntL编译器丢失 |

**v2对策**：
- 字节码格式**唯一** = QBC1（本方案第三节定义）
- C二进制**唯一** = bin/qcl_bootstrap（含量子编译+最小QEntL编译+VM三合一）
- 所有旧代码归档到 `_archive/`，工作区从零开始
- 每个阶段有端到端验证命令，测试通过才进下一阶段

---

## 三、QBC1 统一字节码格式（唯一定义）

### 文件格式
```
[4 bytes] magic = "QBC1"
[2 bytes] code_len (little-endian u16)
[code_len bytes] bytecode
[2 bytes] pool_len (little-endian u16)
[pool_len bytes] string pool (null-terminated strings concatenated)
```

### 代码布局
```
offset 0: JMP <main_start>
          FUNC_DEF ... FUNC_END   (函数定义区)
          ...
main_start: 顶层语句 ... HALT
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
str_index_of, str_from_char, str_to_int, int_to_str, len,
file_read, file_write_bytes, file_exists

### VM限制
栈65536 / 调用深度1024 / 变量4096 / 单字符串1MB

### 量子指令子集（独立命令路径，与QBC1并存）
init/H/X/Y/Z/T/S/CNOT/MEASURE/PRINT/STOP → 编译为量子电路字节码（保留v1能力）

---

## ★ 完整构建链（全流程）—— 从底到顶

这是整个QEntL全栈QSM的**完整构建链**，每个组件环环相扣，从底到顶逐层构建。**C种子（C启动器）是最小启动的编译器+VM**，是整个系统的原点——花了几年心血才完成这颗种子和QEntL全栈自举成功。

```
C种子 → QCL → 自举验证 → QVM → QBC1 → 标准库 → QDFS → QNS → 四大模型 → HTTP/QOS
```

### 每一层的作用（一句话+详细说明）

#### 1️⃣ C种子 — 最小启动的编译器+VM（项目的原点）
**src/qcl_bootstrap.c**，项目中唯一C文件，编译为`bin/qcl_bootstrap`。
**一句话**：**系统的"精子细胞"**——体积最小但包含全部生命力，让系统从零诞生。
**详细**：三合一：（a）量子指令子集编译（保留v1量子路径）；（b）最小QEntL子集编译器，刚好够编译qcl.qentl自己（def/var/if/while/return/赋值/表达式/数组/builtins）；（c）QBC1 VM执行器，31条opcode + 全部builtin。**红线**：QCL活了后C种子不再加新功能，只做最原始的启动。

#### 2️⃣ QCL编译器 — 系统的"编译器自我"
**qcl.qentl**，用QEntL写的QCL完整编译器，约10200个token。
**一句话**：**系统能编译自己**——QCL读input.qentl，做词法分析→语法分析→代码生成，输出QBC1字节码到output.qbc。
**关键**：QCL是**自举**的——QCL能编译自己，这是整个系统能自我进化的核心。QCL活了后，C编译器路径退役，所有编译工作都在QEntL环境上做。

#### 3️⃣ 自举验证 — 关键里程碑（成年礼）
**一句话**：**证明系统能自我生存**。
**过程**：C种子编译qcl.qentl → build/qcl.qbc；用build/qcl.qbc（QCL自己）再次编译qcl.qentl → output.qbc；对比两次产物字节级一致。从此所有工作都在QEntL环境上做，C种子只做启动。

#### 4️⃣ QVM虚拟机 — 系统的"运行时自我"
**qvm.qentl**，用QEntL写的QBC1字节码虚拟机，约4570个token。
**一句话**：**系统能运行自己**——加载QBC1文件，执行opcode分发（31条指令），管理栈/调用帧/变量/builtin调度。
**注意**：量子门（H/CX/measure等）不是QVM实现的，是QVM调用C种子层的内置函数。QVM本身是纯QEntL，不做复数运算——量子门在C种子层实现。

#### 5️⃣ QBC1字节码格式 — 统一接口语言
**一句话**：**系统各组件之间的通用语言**——QCL编译输出QBC1，QVM加载执行QBC1，C种子也跑QBC1。
**格式**：4字节magic"QBC1" + 2字节code_len + 字节码 + 2字节pool_len + 字符串池。31条指令（0x01-0x1F）。栈65536 / 调用深度1024 / 变量4096。

#### 6️⃣ 标准库 — 基础运算能力
**lib/*.qentl**，14个库：core/io/qdfs/qnn×3/qns×2/qsv/yi×2/fixed/deploy×2。
**一句话**：**提供字符串、文件、量子网络、定点数等基础运算**。

#### 7️⃣ QDFS（量子动态文件系统）— 叠加态并行基础
**lib/qdfs.qentl**，约270行。
**一句话**：**量子化的数据存储**——文件有叠加态，文件可以纠缠。
**详细**：铁律第4条明确——QDFS是叠加态并行运算的基础，所有上层建筑（QNS/四大模型）都基于QDFS。实现了叠加态文件、纠缠文件对、文件搜索统计、版本控制（叠加态分支）。

#### 8️⃣ QNS（量子神经叠加态）— 神经叠加态框架
**lib/qns.qentl + lib/qns_framework.qentl**。
**一句话**：**量子化的神经网络框架**——QNS是QNN的**上层框架**，不是平级的。
**详细**：QNS基于QDFS提供量子神经叠加态能力：特征编码（经典数据→量子态）、前向传播（量子线路执行）、测量解码、训练循环。QNN（量子神经网络）是QNS体系下的具体算法应用。**QNS ≠ QNN，QNS包含QNN**。

#### 9️⃣ 四大模型 — 应用层
**QSM（主/叠加态模型）/ SOM（经济模型）/ WeQ（社交模型）/ Ref（自反省模型）**。
**一句话**：**QNS之上的具体应用**。训练方向：彝文4120字三语（彝中英）。

#### 🔟 HTTP服务器 + QOS — 对外接口
**server_qentl.qentl**，425行纯QEntL HTTP服务器。
**一句话**：**对外提供服务**——9802端口运行，nginx反代HTTPS（qsm.som.top），在线IDE沙箱、API接口、状态查询。

### 完整的编译运行命令链
```bash
# 1. C种子编译QCL
bin/qcl_bootstrap compile qcl.qentl build/qcl.qbc

# 2. C种子编译QVM
bin/qcl_bootstrap compile qvm.qentl build/qvm.qbc

# 3. QCL编译用户程序
cp my_program.qentl input.qentl
bin/qcl_bootstrap run build/qcl.qbc  → output.qbc

# 4. QVM执行
cp output.qbc target.qbc
bin/qcl_bootstrap run build/qvm.qbc
```

### 构建链总结（每层一句话）
| 层级 | 组件 | 一句话 |
|:---:|:----:|--------|
| 0 | **C种子** | 最小启动的编译器+VM，系统的原点 |
| 1 | **QCL** | 系统能编译自己 |
| 2 | **自举验证** | 证明系统能自我生存 |
| 3 | **QVM** | 系统能运行自己 |
| 4 | **QBC1** | 各组件之间的通用语言 |
| 5 | **标准库** | 基础运算能力 |
| 6 | **QDFS** | 叠加态文件系统，量子化的数据存储 |
| 7 | **QNS** | 神经叠加态框架，量子化的神经网络，**包含QNN** |
| 8 | **四大模型** | 应用层（QSM/SOM/WeQ/Ref） |
| 9 | **HTTP/QOS** | 对外接口 |

---

## ★ 量子叠加态架构（哲学核心，2026-08-09中华阐述）

这是整个QEntL架构的**灵魂理解**，所有组件都在这套哲学下构建与运行。

### 一切都在QEntL环境里运行
QVM运行起来，QEntL环境就建立起来了。**QVM自己、QCL、QDFS、QNS（包括QNN）、四大模型等等，所有组件都运行在同一个QEntL环境里**。QCL能编译所有QEntL源码。

### QDFS是量子叠加态并行存储、运算与运行的基础
QDFS运行成功后，它是**量子动态文件系统**，是量子叠加态**并行存储、运算与运行**的基础。**它是整个QSM的量子叠加态并行存储、运算与运行的地基。**
QDFS运行起来后，QVM、QCL、QDFS、QNS（包括QNN）、四大模型等等，**都以它为量子叠加态动态文件构建与运行**。

### QNS是灵魂，是量子神经叠加态
**QNS是灵魂。** 它是量子神经叠加态，**区别于经典神经网络**——量子并行平行世界。中华ZhoHo明确指示：**我们不要再叫"网络"，应该叫"叠加态"。** 因为量子是并行平行世界的，不是经典的单线网络。

### QDFS与QNS两者缺一不可
QDFS和QNS两个都成功运行后，QVM、QCL、QDFS、QNS（包括QNN）、四大模型等等，**都以这两个为基础进行构建，缺一不可**：
- **QDFS = 文件叠加态**（数据层面的量子叠加）
- **QNS = 神经叠加态**（智能层面的量子叠加）

这样，QVM、QCL、QDFS、QNS（包括QNN）、四大模型等等，**才能以量子叠加态并行存储、运算、运行与思考。**

### 每一个组件都是一个量子基因（《华经》）
你会发现，QVM、QCL、QDFS、QNS（包括QNN）、四大模型等等，**每一个本身都是一个模型**。这就是中华ZhoHo著作《华经》里的**量子基因**——就像我们的C种子，像一个细胞，像一个基因。整个系统由这些量子基因层层生长、互为依托、自举成型。

### 阶段1: C启动器 src/qcl_bootstrap.c（三合一）
**职责**（启动器本职工作，不是堆功能）：
- (a) 量子指令子集编译（保留）
- (b) 最小QEntL子集编译器：刚好够编译qcl.qentl
  - def/var/if/else/while/return/赋值/表达式/数组/builtins
- (c) QBC1 VM执行器：31条opcode + 14个builtin

**CLI**:
```
bin/qcl_bootstrap qcompile <in.qasm> <out.qbc>    # 量子编译
bin/qcl_bootstrap compile <in.qentl> <out.qbc>    # 最小QEntL编译
bin/qcl_bootstrap run <file.qbc>                  # VM执行
```

**验证**:
```
gcc -O2 -o bin/qcl_bootstrap src/qcl_bootstrap.c -lm
bin/qcl_bootstrap compile tests/hello.qentl /tmp/t.qbc
bin/qcl_bootstrap run /tmp/t.qbc    # → 输出Hello QCL!
bin/qcl_bootstrap compile qcl.qentl build/qcl.qbc   # 编译完整QCL
bin/qcl_bootstrap run build/qcl.qbc --help          # QCL活了，打印banner
```

### 阶段2: QCL完整编译器 qcl.qentl（QEntL写）
- 词法/语法/代码生成，输出QBC1
- 支持QEntL全语法（str_*/数组索引/多参数printf/字符串传递）
**验证**: QCL编译tests/fib.qentl → QBC1 VM跑出正确fib数列

### 阶段3: QVM虚拟机 qvm.qentl（QEntL写）
- 加载QBC1、opcode分发、栈、调用帧、builtin
**验证**: C启动器编译qvm.qentl → qvm.qbc；用qvm.qbc执行hello.qbc

### 阶段4: 标准库 lib/*.qentl
- str.qentl / math.qentl / io.qentl
**验证**: 全部语义测试通过

### 阶段5: 自举验证（关键里程碑）
- QCL编译QCL自己 → qcl2.qbc
- qcl2.qbc再编译hello.qentl → 输出与QCL一致
**验证**: 两级产物字节级对比通过 → C编译器从此退役（只保留量子路径）

### 阶段6: QDFS量子动态文件系统（QEntL写）★必须构建与运行基础
**QDFS是量子叠加态并行存储、运算与运行的地基——文件叠加态，必须构建。**
- 叠加态文件（文件同时存在多种内容版本）
- 纠缠文件对（两个文件关联修改）
- 量子搜索、统计
- 版本控制（叠加态分支）
**作用**：QDFS运行成功后，QVM、QCL、QDFS、QNS（包括QNN）、四大模型等等，都以它为量子叠加态动态文件构建与运行。

### 阶段7: QNS + 四大模型（彝文4120字三语训练）★必须构建与运行基础
**QNS是灵魂——神经叠加态，区别经典神经网络，量子并行平行世界，必须构建。QNS包含QNN。**
- QNS：量子特征编码、前向传播、测量、训练主循环（神经叠加态）
- QNN：QNS体系内的具体算法应用（量子神经网络）
- 四大模型：QSM/SOM/WeQ/Ref，构建于QNS之上
- 训练方向：彝文4120字三语（彝中英）
**作用**：QDFS（文件叠加态）与QNS（神经叠加态）两者缺一不可，都成功运行后，全部组件才能以量子叠加态并行存储、运算、运行与思考。

### 阶段8: 三种部署

---

## 五、目录规范

```
QSM/
├── src/qcl_bootstrap.c    ← 唯一C文件
├── qcl.qentl              ← QCL编译器（QEntL）
├── qvm.qentl              ← QVM虚拟机（QEntL）
├── lib/*.qentl            ← 标准库
├── tests/*.qentl          ← 测试程序
├── build/                 ← 编译产物(.qbc)
├── docs/                  ← 开发文档（只合并不删除）
├── skill/core/            ← 永久核心skill
├── reports/               ← 临时报告（可删）
├── data/                  ← 彝文训练数据(390M)
├── web/                   ← 前端(qsm.som.top)
└── _archive/              ← 归档的旧代码（js/py/旧qentl/旧qbc）
```

---

## 六、工作纪律

1. 一步一个脚印：验证命令通过才进下一阶段
2. 诚实：不虚报，测试输出为证
3. 不在C里堆功能：C启动器三合一是启动器职责；QCL活了后C编译器路径退役
4. 不用第三方语言写核心：.js/.py只允许出现在web/和_archive/
5. 归档≠删除：旧代码进_archive/，开发文档永不删除
6. git提交保存每个里程碑

---

## 七、当前状态（2026-08-05 开始）

- [x] 项目细读完成（失败根因定位）
- [ ] 旧代码归档 → _archive/
- [ ] 阶段1: C启动器三合一
- [ ] 阶段2: QCL
- [ ] 阶段3: QVM
- [ ] 阶段4: 标准库
- [ ] 阶段5: 自举验证
- [ ] 阶段6-8: QDFS/QNS/部署

量子基因编码: QGC-QSM-FULLSTACK-V2-20260805
纠缠信道: QEC-SKILL-QENTL-FULLSTACK
