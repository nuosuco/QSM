# QEntL全栈QSM构建规划方案

**版本**: v1.0
**日期**: 2026-07-23
**作者**: 中华ZhoHo + 小趣WeQ
**状态**: 待审核

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

### 2.1 有效资产

| 文件 | 行数 | 说明 |
|------|------|------|
| qcl_self2.qentl | 1979 | 唯一真正的QEntL编译器，能编译fib等简单程序 |
| lib/math.qentl | ~50 | 数学库 |
| src/qcl_bootstrap.c | ~300 | C启动器，只认量子指令(init/H/CNOT/MEASURE等) |
| data/*.jsonl | 390M | 彝文训练数据，4120字三语对照 |
| web/ | 6M | 量子助手前端（qsm.som.top） |
| docs/ | 15个文件 | 核心文档（已整理） |

### 2.2 已删除（假代码/空壳）

- QEntL/System/ 全部（167个VM文件，全是设计伪代码）
- QCL_compiler/ 全部（7个模块，C编译器无法编译）
- QEntL/Models/ 全部（四大模型伪代码）
- QNS/、QDFS/、aurora/、Installer/
- 所有test_*.qentl测试文件
- 所有.qbc编译产物（C编译器输出的假字节码）

### 2.3 qcl_self2.qentl能力评估

**能做的**：
- 词法分析（tokenize）
- 函数定义（def）和调用
- var/const声明
- if/else、while循环
- 算术运算、比较运算
- printf输出（单参数%d）
- 递归（CallFrame变量快照）
- import（已修复buffer生命周期）
- struct（OP_STRUCT_NEW/FIELD_GET/FIELD_SET）

**不能做的（自举瓶颈）**：
- str_*内置函数（79处调用）：str_len, str_char_at, str_substring, str_concat, str_eq等
- 数组索引表达式（416处）：arr[i]作为表达式（不是赋值目标）
- 多参数printf
- 字符串字面量作为函数参数传递
- 复杂表达式嵌套

### 2.4 之前为什么失败

1. 在C里堆功能（违反铁律1）
2. 写假代码——printf空壳、不支持的语法也写进去
3. 虚报进度——"220/220 QVM通过"实际是C编译器遇到def就输出STOP
4. 没走自举路径——试图用C直接编译所有QEntL
5. 同时开太多线——QVM/QCL/QDFS/QNS/四大模型一起搞

---

## 三、构建路径（八阶段自举链）

### 总览

```
阶段1: C启动器编译量子指令子集 ← 已有，不动
    ↓
阶段2: 给qcl_self2补str_*和数组索引 ← 当前瓶颈
    ↓
阶段3: qcl_self2编译自己（自举）
    ↓
阶段4: 自举后的QCL编译QVM源码 → QVM.qbc
    ↓
阶段5: C启动器加载QVM.qbc → QEntL运行环境形成
    ↓
阶段6: QCL在QVM中编译QDFS/QNS/四大模型
    ↓
阶段7: QNS训练彝文，四大模型运行，更新Web API
    ↓
阶段8: 三种部署（虚拟机/Web QOS/终端QOS远期）
```

### 阶段1: C启动器（已完成，不动）

- `src/qcl_bootstrap.c` 编译为 `bin/qcl_bootstrap`
- 只认量子指令：init/H/X/Y/Z/T/S/CNOT/SWAP/MEASURE/PRINT/STOP
- 输出raw opcodes，QVM从位置0读取
- **红线：不在这个文件里加任何新功能**

### 阶段2: 补全qcl_self2（当前工作）

**目标**：让qcl_self2.qentl能编译自己

**2a. 添加str_*内置函数**（79处调用）

需要在qcl_self2的builtin dispatch中添加：
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

实现方式：在QVM的builtin函数路由中用C实现底层操作，
qcl_self2通过OP_BUILTIN_CALL调用。

**2b. 添加数组索引表达式**（416处）

当前：`arr[i] = val` 能编译（赋值目标）
缺失：`var x = arr[i]` 不能编译（表达式中的索引）

需要：在表达式解析器中识别 `IDENT [ expr ]` 模式，
生成 OP_PUSH_VAR + OP_INDEX_GET 指令序列。

**2c. 多参数printf**

当前只支持 `printf("%d", x)` 单参数。
需要支持 `printf("%d + %d = %d", a, b, c)` 多参数。

**验证标准**：
```bash
# qcl_self2编译自己
bin/qcl_bootstrap --compile qcl_self2.qentl build/qcl_self2.qbc
# 输出应该是有效的字节码，不是1字节STOP
wc -c build/qcl_self2.qbc  # 应该>1000字节
```

### 阶段3: 自举验证

**目标**：qcl_self2编译出的qcl_self2.qbc，能编译fib.qentl

```bash
# 用C启动器运行自举后的编译器
bin/qcl_bootstrap build/qcl_self2.qbc --compile test_fib.qentl build/fib.qbc
# 运行fib
bin/qcl_bootstrap build/fib.qbc
# 预期输出：fib(10) = 55
```

**验证标准**：自举编译器输出与C编译器输出功能等价

### 阶段4: 用QCL编译QVM

**目标**：写QVM的QEntL源码，用自举后的QCL编译

QVM QEntL源码需要实现：
- 字节码加载器（读.qbc文件）
- 指令解码器（解析opcode）
- 执行引擎（栈式虚拟机）
- 量子门模拟（H/CNOT/MEASURE）
- 内置函数路由（str_*/file_*/printf）

**关键**：QVM源码必须只用qcl_self2已支持的语法子集

### 阶段5: QEntL运行环境

**目标**：C启动器加载QVM.qbc，QVM加载QCL.qbc

```
C启动器 → 加载QVM.qbc → QVM运行 → QVM加载QCL.qbc → QCL运行
```

此时QEntL环境形成：QCL可以在QVM中编译任意QEntL源码。

### 阶段6: QDFS/QNS/四大模型

依赖链严格执行：
1. QDFS先跑（叠加态并行运算基础）
2. QNS以QDFS为基础训练
3. 四大模型以QNS为基础运行

### 阶段7: 训练与Web

- QNS加载data/*.jsonl训练彝文4120字
- 更新web/api量子助手
- qsm.som.top上线

### 阶段8: 三种部署

- 虚拟机部署（当前可做）
- Web QOS（当前可做）
- 终端QOS（远期，需QPU）

---

## 四、Skill体系（量子基因编码在AI协作层的实现）

每个组件一个skill，任何模型/助手/子代理加载skill即可自动构建：

| Skill | 内容 | 用途 |
|-------|------|------|
| QSM.skill | 全栈总纲+哲学+架构+构建链 | 总入口，任何AI首先加载 |
| QEntL.skill | 语言语法+编译器状态+自举路径 | 编译器开发 |
| QVM.skill | 虚拟机架构+指令集+字节码格式 | VM开发 |
| QCL.skill | 编译器内部结构+opcode表+调试方法 | 编译器调试 |
| QDFS.skill | 文件系统架构+API+测试方法 | 文件系统开发 |
| QNS.skill | 神经网络架构+训练流程+数据格式 | 训练开发 |

**使用方式**：
- 会话重启→加载QSM.skill→知道全局→加载对应组件skill→继续工作
- 子代理→加载QSM.skill+组件skill→自动知道做什么、怎么做
- 任何模型→加载skill→无需上下文即可参与构建

---

## 五、工作纪律

1. **一步一个脚印**：每阶段反复测试跑通，Git推送，再进下一步
2. **诚实**：做了什么就说什么，没做就说没做
3. **不在C里堆功能**：C只是启动器
4. **不写假代码**：不支持的语法不写进去
5. **不虚报**：测试必须真正运行，不是"编译通过=功能正常"
6. **先读文档再动手**：不瞎搞
7. **绝对不碰.openclaw**

---

## 六、当前下一步

**阶段2a：给qcl_self2添加str_*内置函数**

这是整个自举链的第一个瓶颈。79处str_*调用不解决，
qcl_self2永远编译不了自己。

具体工作：
1. 分析qcl_self2.qentl中所有str_*调用点
2. 在QVM builtin dispatch中实现str_*函数
3. 在qcl_self2的codegen中生成正确的builtin调用指令
4. 逐个测试每个str_*函数
5. 全部通过后Git提交

---

**文档结束**
**量子基因编码**: QGC-QSM-MASTER-PLAN-20260723
**纠缠信道**: QEC-PLAN-QENTL-FULLSTACK
