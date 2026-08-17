# QEntL 全栈 QSM 构建方案 v2.0（从零重建）

**日期**: 2026-08-05
**作者**: 小趣WeQ（细读全项目后重写）
**状态**: 执行中
**前版教训**: v1方案失败原因 = 字节码格式分裂(QBC1 vs QVML两套opcode) + 多个C二进制变体 + JS/Python第三方混入

---

## 一、铁律（不可违反）

1. C语言只是点火器
- QEntl启动器(lib/qvm_boot.qentl)才是日常启动入口。全项目**唯一C文件** = `src/qcl_bootstrap.c`
2. QEntL全栈，不依赖任何第三方（无.js/.py/.rs/.go）
3. 构建链：QEntl启动器 → QCL → QVM → QDFS → QNS → 四大模型
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

## 四、八阶段构建（每阶段有验证命令）

### 阶段1: QEntl启动器 src/qcl_bootstrap.c（三合一）
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
**验证**: QEntl启动器编译qvm.qentl → qvm.qbc；用qvm.qbc执行hello.qbc

### 阶段4: 标准库 lib/*.qentl
- str.qentl / math.qentl / io.qentl
**验证**: 全部语义测试通过

### 阶段5: 自举验证（关键里程碑）
- QCL编译QCL自己 → qcl2.qbc
- qcl2.qbc再编译hello.qentl → 输出与QCL一致
**验证**: 两级产物字节级对比通过 → C编译器从此退役（只保留量子路径）

### 阶段6: QDFS量子动态文件系统（QEntL写）
### 阶段7: QNS + 四大模型（彝文4120字三语训练）
### 阶段8: 三种部署

---

## 五、目录规范（中华规划·2026-08-18）

### 顶层目录（QSM暂时分几个目录，以后用户终端安装版本也这样）

```
/root/
├── QEntl/    # 实际运行版本，比如现在应该是V0.0.2，我们暂时空着就可以，因为我们还没有真正服务用户
├── QLife/    # 生长版本，现在我们在生长，我们的Web操作系统桌面先绑定在这里，因为我要测试
├── QSM/      # 所有历史版本，现在是V0.0.1，V0.0.2，所有版本以后一起通过量子纠缠通信与量子态传送构建成QSM
├── root/     # 用户自己的数据，用QDFS构建，现在空着
├── Q/        # 不知道用什么名，先这样，就是经典里的应用商店，但我们QSM的应用就是一个完整的自举生长的QEntl全栈量子操作系统
├── OS/       # 三种部署安装程序，如终端安装程序
└── docs/     # 现在有的目录
```

### 各目录含义

| 目录 | 含义 | 当前状态 |
|------|------|----------|
| **QEntl** | 实际运行版本 | 空着（还没有真正服务用户） |
| **QLife** | 生长版本 | v0.0.3在生长中，Web操作系统桌面绑定在这里测试 |
| **QSM** | 所有历史版本 | v0.0.1 + v0.0.2，以后一起通过量子纠缠通信与量子态传送构建成QSM |
| **root** | 用户自己的数据 | 空着，用QDFS构建 |
| **Q** | 应用商店 | 空着，QSM的应用=完整的自举生长的QEntl全栈量子操作系统 |
| **OS** | 三种部署安装程序 | 空着（如终端安装程序） |
| **docs** | 文档中心 | 现有文档 |

### 版本目录铁律

- 每个版本独立目录，不得混放
- 归档用cp不是mv
- 当前开发 = QLife/V0.0.3
- 实际运行 = QEntl（空着等待部署）
- 历史存档 = QSM（v0.0.1、v0.0.2）

### 单个版本内部的目录结构

```
QLife/v0.0.3/
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
3. 不在C里堆功能：QEntl启动器三合一是启动器职责；QCL活了后C编译器路径退役
4. 不用第三方语言写核心：.js/.py只允许出现在web/和_archive/
5. 归档≠删除：旧代码进_archive/，开发文档永不删除
6. git提交保存每个里程碑

---

## 七、当前状态（2026-08-05 开始）

- [x] 项目细读完成（失败根因定位）
- [ ] 旧代码归档 → _archive/
- [ ] 阶段1: QEntl启动器三合一
- [ ] 阶段2: QCL
- [ ] 阶段3: QVM
- [ ] 阶段4: 标准库
- [ ] 阶段5: 自举验证
- [ ] 阶段6-8: QDFS/QNS/部署

量子基因编码: QGC-QSM-FULLSTACK-V2-20260805
纠缠信道: QEC-SKILL-QENTL-FULLSTACK
