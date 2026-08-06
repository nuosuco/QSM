# QEntL 全栈构建规划方案

> 日期: 2026-07-23
> 状态: 待执行
> 原则: 一步一个脚印，每步反复跑通再进下一步，Git推送保存，绝不跳步

---

## 一、现状诚实评估

### 真正能跑的（仅2个）

| 文件 | 能力 | 限制 |
|------|------|------|
| src/qcl_bootstrap.c (247行) | 编译量子指令(init/H/X/CNOT/MEASURE/PRINT/STOP)→QBC | **不认def/var/if/while/return/函数调用** |
| qcl.qentl (1383行) | QEntL写的编译器，能编译简单程序(fib) | **编译不了自己，缺str_*/数组索引表达式等** |

### 工作目录
/root/QSM/

---

## 二、分步计划（8步，每步跑通才进下一步）

### 第1步：清理 + 文档整理（已完成）
- [x] 删除所有假代码文件
- [x] 合并docs/文档

### 第2步：检查C启动器能否编译qcl.qentl
- [ ] 编译C启动器: `gcc -O2 -o bin/qcl_bootstrap src/qcl_bootstrap.c -lm`
- [ ] 用C启动器编译qcl.qentl: `bin/qcl_bootstrap compile qcl.qentl build/qcl.qbc`
- [ ] 验证编译结果

### 第3步：C启动器运行QBC
- [ ] 执行qcl.qbc: `bin/qcl_bootstrap run build/qcl.qbc`
- [ ] 验证输出

### 第4步：qcl.qentl自举
- [ ] 分析qcl.qentl编译自己时缺什么特性
- [ ] 每次只加一个特性，反复测试跑通再加下一个
- [ ] 优先级：str_*内置函数 → 数组索引表达式 → 复杂表达式 → 字符串拼接
- [ ] 验证: qcl.qentl能编译qcl.qentl → 输出qcl_v2.qbc

### 第5步：用QEntL重写QVM
- [ ] 用qcl.qentl（已自举）编译QVM源码
- [ ] QVM用QEntL写，实现：QBC加载、opcode分发、栈操作、函数调用、内置函数

### 第6步：QDFS量子动态文件系统
- [ ] 用QEntL写QDFS

### 第7步：QNS+四大模型
- [ ] QNS训练彝文，四大模型运行

### 第8步：三种部署
- [ ] 虚拟机/Web QOS/终端QOS