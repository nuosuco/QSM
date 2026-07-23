# QEntL 自举计划 — 让 QCL引导器(QEntL)编译自己

## 现状分析

| 层面 | 当前状态 | 需要 |
|------|---------|------|
| 字节码格式 | QCLF (0x51434C46) | QVML (0x14 00 00 00) |
| 支持 const | ✗ | 需要添加 |
| 支持 var | ✗ | 需要添加 |
| 支持 import | ✗ | 需要添加 |
| 支持 if/else | 仅 { } 体 | 缩进体+花括号体 |
| 支持 while | 仅 { } 体 | 缩进体+花括号体 |
| 字符串操作 | 无 | len/substring/ord |
| 数组操作 | 无 | push/索引访问 |
| 字节码输出 | 直接写 opcode | 需要高字节码格式 |

## 阶段计划

### Phase A: 格式对齐 — 让 QCL引导器输出 QVML 格式
1. 修改 write_file_header → QVML 头
2. 添加字符串池支持
3. 添加 code_len/sp_len 输出

### Phase B: 功能扩展 — 逐步添加缺失语法
1. const 声明支持
2. var 声明支持
3. if/else 控制流
4. while 循环
5. 字符串操作 (len/substring/ord)
6. 数组操作 (push/索引访问)

### Phase C: 自举验证
1. 编译 qcl_opcodes.qentl → 验证字节码
2. 编译所有 5 个 QCL引导器模块
3. 验证自举输出在 QVM 上运行