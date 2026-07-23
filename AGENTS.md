# QSM - QEntL全栈量子叠加态模型

## 项目定位
QSM（Quantum Superposition Model）— 基于 QEntL（Quantum Entanglement Language）的全栈量子计算语言系统。纯 C + QEntL，禁止 Python/第三方。

## 构建命令
```bash
cd /root/QSM
make qcl_phase2          # 编译 QCL 编译器
make qvm_bootstrap       # 编译 QVM 虚拟机
./bin/qcl_phase2 QCL_main.qentl   # 编译 QEntL → QBC
./bin/qvm_bootstrap QCL_main.qbc  # 执行 QBC
```

## 技术栈
- C (gnu99): qcl_phase2.c(2319行) + qvm_bootstrap.c(1749行) + qcl_bootstrap.c(247行) + qcl_full_compiler.c(716行) = 5031行
- QEntL: 184个.qentl文件, 12个.qbc文件
- 6层架构: C启动器 → QVM → QCL → QDFS → QNS → 四大模型

## 目录与约定
- `src/` — C 源码（编译器+虚拟机）
- `bin/` — 编译产物
- `QEntL/` — QEntL 语言源码（System/Kernel, System/VM, System/Compiler, Models/）
- `QCL_compiler/` — QCL 编译器 QEntL 模块
- `test_programs/` — 测试用例
- `docs/` — 设计文档
- 命名: .qentl=源码, .qbc=字节码(magic=0x14)

## 当前状态（2026-07-20 实测）
- ✅ qcl_phase2 编译通过，QCL_main.qentl → 3673字节 QBC
- ✅ qvm_bootstrap 执行 QCL_main.qbc exit=0（15函数注册）
- ✅ QVM.qbc / QVM_entry.qbc / QVM_entry_full.qbc 全部 exit=0
- ✅ QDFS 32/32, QNS 15/15, Platform 8/8, Deployment 5/5
- ❌ lexer 字符字面量 '\n' 拆分 bug（parse_int 相关）
- ❌ 自举（QVM 内运行 QCL 编译器）未完成

## 下一步
1. 修复 lexer '\n' 字符字面量 bug
2. 完成 import 链完整加载
3. 推进自举（QEntL 环境内编译 QEntL）
