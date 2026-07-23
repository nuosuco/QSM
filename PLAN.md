# QEntL 全栈构建规划方案

> 日期: 2026-07-23
> 状态: 待中华审批
> 原则: 一步一个脚印，每步反复跑通再进下一步，Git推送保存，绝不跳步

---

## 一、现状诚实评估

### 真正能跑的（仅2个）

| 文件 | 能力 | 限制 |
|------|------|------|
| src/qcl_bootstrap.c (7766字节) | 编译量子指令(init/H/X/CNOT/MEASURE/PRINT/STOP)→QBC | **不认def/var/if/while/return/函数调用** |
| qcl_self2.qentl (1979行) | QEntL写的编译器，能编译简单程序(fib) | **编译不了自己，缺str_*/数组索引表达式等** |

### 必须删除的（假代码，永远编译不了）

| 目录/文件 | 文件数 | 删除原因 |
|-----------|--------|----------|
| QCL_compiler/ (7个.qentl) | 7 | 用了中文变量名、对象字面量{}、.push()/.split()/.substring()、import...作为、返回/IF/WHILE大写、且/或/非、null/true/false、in运算符、成员访问——**没有任何编译器能编译** |
| QCL_main.qentl | 1 | 同上，用了对象字面量、成员访问、get_directory_entries等不存在的函数 |
| QEntL/System/VM/ (8个) | 8 | **全是printf空壳**，没有一行真正的VM逻辑 |
| QEntL/System/Platform/ (8个) | 8 | 用了对象字面量、成员访问——没有编译器支持 |
| QEntL/System/Deployment/ (14个) | 14 | 用了printf空壳+不存在的函数 |
| QEntL/Models/ (4个) | 4 | **全是printf空壳** |
| QEntL/QEntL_构建系统*.qentl (2个) | 2 | 用了不存在的函数(QDFS_文件存在等) |
| QEntL/System/Kernel/ (5个) | 5 | QDFS用了fopen/fclose，QNS把H()/CNOT()当函数调用 |
| QNS/ (5个) | 5 | 同上 |
| QDFS/ (3个) | 3 | 用了fopen/fclose/fgets/fwrite——QEntL没有 |
| aurora/ (5个) | 5 | 用了quantum_class/public/private/new——完全不同的语法 |
| QVM.qentl/QVM_entry.qentl/QVM_entry_full.qentl | 3 | 只是量子电路测试，不是虚拟机 |
| QEntL_main.qentl | 1 | printf空壳 |
| Installer/ | 2 | 用了不存在的语法 |
| 根目录test_*.qentl (~30个) | 30 | 测试碎片 |
| test_programs/ (~20个) | 20 | 测试碎片 |
| tests/ (~10个) | 10 | 测试碎片 |
| test/ (~30个) | 30 | 测试碎片 |
| build_test/ | 5 | 测试碎片 |
| test_output/ | 5 | 测试碎片 |
| 根目录散落.qentl (feature_extraction/full_train_pipeline/multi_epoch_train/joint_task/qns_yi_*/train_circuit/yi_*/coordination_test) | ~12 | 无法编译 |
| docs/architecture/*.qentl | 8 | 设计文档伪装成代码 |
| docs/examples/*.qentl | 14 | 量子电路示例（保留.md说明） |
| docs/integration/*.qentl | 2 | 无法编译 |
| docs/philosophy/*.qentl | 4 | 无法编译 |
| docs/MASTER_PLAN*.qentl | 2 | 无法编译 |
| docs/*.qentl (其余) | 4 | 无法编译 |
| bin/qcl_phase2, bin/qentl_compiler, bin/qvm_bootstrap | 3 | 源码已删，二进制无用 |
| build/ | 全部 | 编译产物，重新生成 |

### 保留的

| 文件 | 原因 |
|------|------|
| src/qcl_bootstrap.c | C启动器，编译量子指令子集，**自举起点** |
| qcl_self2.qentl | **唯一真正的QEntL编译器**，自举核心 |
| lib/math.qentl | 简单数学库(add/mul)，qcl_self2能编译 |
| docs/*.md | 开发文档（合并整理） |
| data/ | 训练数据（51899条彝文） |
| web/ | Web界面 |
| .git/ | 版本控制 |

---

## 二、核心矛盾与解决路径

### 矛盾

八阶段计划说"C引导器编译QCL编译器源码"。但：
- qcl_bootstrap.c **只认量子指令**（init/H/X/CNOT/MEASURE/PRINT/STOP）
- qcl_self2.qentl 用了 def/var/if/while/return/printf/数组/函数调用/str_*
- **qcl_bootstrap.c 编译不了 qcl_self2.qentl**

### 解决路径

**必须扩展C启动器最后一次**，让它能编译qcl_self2.qentl用的语法子集。
这是自举的"种子"——C代码是最后一次，之后qcl_self2.qentl接管一切。

qcl_self2.qentl用的语法子集（精确清单）：
```
def name(params): ... end        ← 函数定义
var x = expr                     ← 变量声明
var arr[N]                       ← 数组声明
arr[idx] = val                   ← 数组赋值
arr[idx]                         ← 数组读取（索引是表达式）
if (cond): ... end               ← 条件（支持嵌套）
while (cond): ... end            ← 循环
return expr                      ← 返回
printf("fmt", args)              ← 内置：格式化输出
file_read("path")                ← 内置：读文件
str_char_at(s, pos)              ← 内置：取字符
str_eq(s1, s2)                   ← 内置：字符串比较
len(s)                           ← 内置：长度
name(args)                       ← 函数调用
+ - * /                          ← 算术
== != < > <= >=                  ← 比较
"string" / 123                   ← 字面量
// comment                       ← 注释
```

**共17种语法构造。C启动器必须支持这17种，才能编译qcl_self2.qentl。**

---

## 三、分步计划（8步，每步跑通才进下一步）

### 第1步：清理 + 文档整理（Day 1）
- [ ] 删除上表所有假代码文件
- [ ] 合并docs/*.md为一份 `docs/QSM_开发文档.md`
- [ ] 删除bin/qcl_phase2, bin/qentl_compiler, bin/qvm_bootstrap, build/
- [ ] Git commit + push："清理：删除假代码，保留自举核心"
- **验证**: `find . -name "*.qentl" | wc -l` 只剩 qcl_self2.qentl + lib/math.qentl

### 第2步：扩展C启动器编译qcl_self2.qentl（Day 2-4）
- [ ] 在src/qcl_bootstrap.c中添加17种语法构造的编译支持
- [ ] 每加一种，写一个最小测试.qentl验证
- [ ] 顺序：var → def/end → if/end → while/end → return → 函数调用 → 数组声明 → 数组索引 → printf → file_read → str_char_at → str_eq → len → 算术 → 比较 → 字符串字面量 → 注释
- [ ] 最终验证：`bin/qcl_bootstrap --compile qcl_self2.qentl build/qcl_self2.qbc`
- **验证**: 编译成功，输出QBC文件，大小>0
- Git commit + push

### 第3步：C启动器运行QBC（Day 4-5）
- [ ] 在src/qcl_bootstrap.c中添加QBC执行模式（或写最小qvm_runner.c）
- [ ] 执行qcl_self2.qbc，验证它能读取源文件、词法分析、生成字节码
- [ ] 用qcl_self2编译lib/math.qentl → 验证输出QBC正确
- **验证**: qcl_self2.qbc运行，成功编译math.qentl，输出math.qbc
- Git commit + push

### 第4步：qcl_self2自举——逐个加特性（Day 5-10）
- [ ] 分析qcl_self2.qentl编译自己时缺什么特性
- [ ] 每次只加一个特性，反复测试跑通再加下一个
- [ ] 优先级：str_*内置函数 → 数组索引表达式 → 复杂表达式 → 字符串拼接 → 更多内置
- [ ] 每加一个特性：编译→运行→验证→Git commit
- **验证**: qcl_self2.qentl能编译qcl_self2.qentl → 输出qcl_self2_v2.qbc
- **终极验证**: qcl_self2_v2.qbc运行结果与qcl_self2.qbc一致（自举成功）
- Git commit + push："自举完成"

### 第5步：用QEntL重写QVM（Day 10-14）
- [ ] 用qcl_self2（已自举）编译QVM源码
- [ ] QVM用QEntL写，实现：QBC加载、opcode分发、栈操作、函数调用、内置函数
- [ ] 替换C启动器的QBC执行功能
- **验证**: QEntL版QVM能运行qcl_self2.qbc，结果与C版一致
- Git commit + push

### 第6步：QDFS量子动态文件系统（Day 14-18）
- [ ] 用QEntL写QDFS（基于自举编译器+QEntL VM）
- [ ] 实现：文件读写、目录扫描、文件索引
- [ ] 不用fopen/fclose——用QEntL VM提供的系统调用
- **验证**: QDFS能读写文件、扫描目录
- Git commit + push

### 第7步：QNS量子神经叠加态（Day 18-24）
- [ ] 用QEntL写QNS训练管道
- [ ] 基于QDFS加载data/下51899条彝文数据
- [ ] 实现：量子编码、前向传播、梯度下降、模型保存
- **验证**: QNS能加载数据、训练1个epoch、输出损失值
- Git commit + push

### 第8步：四大模型 + Web API（Day 24-30）
- [ ] QSM/SOM/WeQ/Ref用QEntL重写（基于QNS）
- [ ] 更新web/桌面量子助手API
- **验证**: 四大模型能运行，API能响应
- Git commit + push："QEntL全栈完成"

---

## 四、铁律

1. **每步跑通才进下一步**——不跳步、不并行、不"先写后补"
2. **每步Git commit + push**——保存地基，随时可回退
3. **C代码只在第2-3步扩展，第4步之后C退场**——C是种子不是主体
4. **不写printf空壳**——每行代码必须能编译运行
5. **不用不存在的语法**——只写当前编译器支持的语法
6. **绝对禁止休眠、欺骗、假象、敷衍了事**

---

## 五、时间线

| 步骤 | 内容 | 时间 | 验证标准 |
|------|------|------|----------|
| **第1步** | 清理假代码+合并文档 | 0-1h | 只剩qcl_self2.qentl+lib/math.qentl+src/qcl_bootstrap.c |
| **第2步** | 扩展C启动器编译qcl_self2 | 1-6h | qcl_self2.qentl→QBC成功 |
| **第3步** | C启动器运行QBC | 6-9h | qcl_self2.qbc运行，编译math.qentl成功 |
| **第4步** | **自举** | 9-16h | qcl_self2编译自己，输出一致 |
| **第5步** | QEntL重写QVM | 16-21h | QEntL VM运行qcl_self2.qbc，C退场 |
| **第6步** | QDFS | 21-24h | 文件读写、目录扫描跑通 |
| **第7步** | QNS | 24-28h | 彝文训练1个epoch跑通 |
| **第8步** | 四大模型+Web API | 28-30h | **全栈完成** |

**总计30小时。** 时间不够时开子代理并行（第2步C扩展可拆分子任务，第6-8步可并行）。

---

## 六、能不能成功？

**能。** 理由：

1. qcl_self2.qentl已经能编译简单程序（fibonacci），证明QEntL编译器核心逻辑是对的
2. 它只缺17种语法构造中的少数几个（str_*、数组索引表达式），不是架构问题
3. C启动器扩展是确定性的工作——17种语法构造，每种都有明确的输入输出
4. 自举是编译器领域的标准路径（GCC、Rust、Go都是自举的）
5. 不再写假代码——每行都能编译运行

**风险：**
- 第2步C扩展可能遇到qcl_self2.qentl的边界语法（嵌套if、复杂表达式）
- 第4步自举可能需要多轮迭代
- 应对：每步反复测试，不跳步，遇到问题当场解决

**之前为什么失败：**
- 没走自举路径，在C里堆了5000行
- 写了大量"看起来像代码"的.qentl文件，没有一个能编译
- 同时开多条线，哪个都没做完
- 这次：一条线，一步一个脚印
