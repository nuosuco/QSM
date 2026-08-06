# QVML 字节码直接写入方案
## 发现：QVM (/root/bin/qvm_bootstrap) 就是QEntL运行时

### 字节码格式 (QVML)
```
[0x14 0x00 0x00 0x00]  — QVML头 (4B)
[code_len LE16]          — 代码长度 (2B)
[code (code_len bytes)]  — 字节码指令
[sp_len LE16]            — 字符串池长度 (2B)
[string_pool]            — 字符串池数据
```

### 已验证的QVM操作码
| 操作码 | 名称 | 说明 |
|--------|------|------|
| 0x00 | OP_NOP | 空操作 |
| 0x01 | OP_H | Hadamard门 |
| 0x02 | OP_X | Pauli-X门 |
| 0x03 | OP_Z | Pauli-Z门 |
| 0x06 | OP_RESET | 重置量子比特 |
| 0x08 | OP_LOAD_REG | 寄存器→栈 |
| 0x09 | OP_STORE_REG | 栈→寄存器 |
| 0x0B | OP_PRINT | 打印寄存器 |
| 0x0C | OP_STOP | 停止 |
| 0x0D | OP_SUB | 减法 |
| 0x0E | OP_DIV | 除法 |
| 0x0F | OP_MUL | 乘法 |
| 0x11 | OP_EXIT | 退出 |
| 0x12 | OP_BARRIER | 量子屏障 |
| 0x23 | OP_T | T门 |
| 0x24 | OP_S | S门 |
| 0x25 | OP_Y | Pauli-Y门 |
| 0x66 | OP_FUNC_DEF | 函数定义 |
| 0x67 | OP_FUNC_END | 函数结束 |
| 0x69 | OP_TYPE_END | 类型结束 |
| 0x6B | OP_RETURN_STMT | 返回语句 |
| 0x6C | OP_IF_STMT | If语句 |
| 0x6D | OP_ELSE_STMT | Else语句 |
| 0x6E | OP_WHILE_STMT | While循环 |
| 0x70 | OP_FUNC_CALL_STMT | 函数调用 |
| 0x71 | OP_BREAK_STMT | Break |
| 0x72 | OP_CONTINUE_STMT | Continue |
| 0x78 | OP_PUSH_CONST_INT | 压入整数常量(2B LE) |
| 0x79 | OP_PUSH_CONST_STR | 压入字符串常量 |
| 0x82 | OP_APPEND_BYTE | 追加字节 |
| 0x83 | OP_BYTECODE_LEN | 字节码长度 |
| 0xC8 | OP_LINUX | Linux平台 |
| 0xC9 | OP_WINDOWS | Windows平台 |
| 0xCA | OP_IOS | iOS平台 |
| 0xCB | OP_ANDROID | Android平台 |
| 0xCC | OP_HARMONY | 鸿蒙平台 |
| 0xFE | BC_FUNC_END | 函数体结束 |
| 0xFF | BC_FUNC_BODY | 函数体开始 |

### 核心原理
- QVM自动扫描函数定义，然后执行主代码
- 如果没执行主代码，自动调用 `main()` 或 `主程序()` 函数
- 字节码可以直接用 printf 写入，无需编译器
- 无需gcc，无需第三方语言

### 已验证
- `printf '\x14\x00\x00\x00\x08\x00\x78\x2a\x00\x09\x00\x0b\x00\x0c\x00\x00' > /tmp/test.qvml`
- 运行: `/root/bin/qvm_bootstrap /tmp/test.qvml`
- 输出: `print(r0) = 42`