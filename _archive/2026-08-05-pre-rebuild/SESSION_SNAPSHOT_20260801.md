# 会话快照 2026-08-01

## 核心哲学教训（中华教导）
1. **用了第三方就不是量子叠加态** — JS/Python等第三方语言使项目变成经典串行，不能并行工作
2. **QVM直接运行QEntl源码** — 跳过字节码中间层，才是正确的量子路径
3. **C二进制是最小程序启动器** — 只做编译量子电路子集，不作为完整解释器
4. **最终目标** — QEntL源码直接编译为机器二进制

## 项目路径
- QSM项目: /root/QSM/ (从备份恢复)
- QEntL项目: /root/QEntL/ (41个.qentl源文件)
- 编译器源码: /root/restored_sources/Compiler_QCL/qcl_full_compiler.c (716行)
- 完整编译器: /root/restored_sources/Compiler_QCL/qcl_phase2.c (2320行)
- QVM源码(完整版): /root/restored_sources/Compiler_QCL/qvm_bootstrap.c (1707行)
- QVM源码(精简版): /root/src/qvm_bootstrap.c (834行, 已编译为/root/qvm_boot)
- C启动器v2: /root/src/qcl_bootstrap.c (824行, 已编译为/root/bin/qcl_bootstrap)
- QVM二进制: /root/qvm_boot (支持量子指令+基本控制流)
- 备份: /root/backups/QSM-20260725-v1.0.1.tar.gz

## 可用二进制
- /root/qcl_bootstrap — v1编译器 (编译量子电路, 18字节输出)
- /root/bin/qcl_bootstrap — v2编译器 (中文关键字, 3354字节垃圾输出)
- /root/qvm_boot — QVM运行时 (Version 1.0.0, 16寄存器, 64量子比特)
- /root/qvm_bootstrap_v3 — QVM v3
- /root/qsm_qcl_bootstrap — QSM版编译器

## 当前状态
- 启动器(fopen/fgets)可以编译简单量子电路
- 不支持函数定义(def/var/if/while/return)
- 下一个任务: 让QVM直接运行QEntl源码，跳过字节码
