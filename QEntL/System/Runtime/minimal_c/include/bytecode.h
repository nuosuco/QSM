// QEntL最小化运行时 - 字节码指令集
// 定义虚拟机执行的字节码指令

#ifndef BYTECODE_H
#define BYTECODE_H

#include <stdint.h>

// ==================== 字节码指令枚举 ====================

typedef enum {
    // 空操作和控制流
    OP_NOP,         // 空操作
    OP_HALT,        // 停止执行
    
    // 栈操作
    OP_PUSH_NIL,    // 压入空值
    OP_PUSH_TRUE,   // 压入真
    OP_PUSH_FALSE,  // 压入假
    OP_PUSH_INT,    // 压入整数 (操作数: 常量索引)
    OP_PUSH_FLOAT,  // 压入浮点数 (操作数: 常量索引)
    OP_PUSH_STRING, // 压入字符串 (操作数: 常量索引)
    OP_POP,         // 弹出栈顶
    
    // 算术运算
    OP_ADD,         // 加法
    OP_SUB,         // 减法
    OP_MUL,         // 乘法
    OP_DIV,         // 除法
    OP_MOD,         // 取模
    OP_NEG,         // 取负
    
    // 比较运算
    OP_EQ,          // 等于
    OP_NEQ,         // 不等于
    OP_LT,          // 小于
    OP_LE,          // 小于等于
    OP_GT,          // 大于
    OP_GE,          // 大于等于
    
    // 逻辑运算
    OP_NOT,         // 逻辑非
    OP_AND,         // 逻辑与
    OP_OR,          // 逻辑或
    
    // 变量操作
    OP_GET_LOCAL,   // 获取局部变量 (操作数: 局部变量索引)
    OP_SET_LOCAL,   // 设置局部变量 (操作数: 局部变量索引)
    OP_GET_GLOBAL,  // 获取全局变量 (操作数: 常量索引-名称)
    OP_SET_GLOBAL,  // 设置全局变量 (操作数: 常量索引-名称)
    
    // 跳转
    OP_JUMP,        // 无条件跳转 (操作数: 跳转偏移)
    OP_JUMP_IF_TRUE, // 如果为真跳转
    OP_JUMP_IF_FALSE, // 如果为假跳转
    
    // 函数调用
    OP_CALL,        // 调用函数 (操作数: 参数数量)
    OP_RETURN,      // 从函数返回
    
    // 数组操作
    OP_NEW_ARRAY,   // 创建新数组 (操作数: 元素数量)
    OP_GET_INDEX,   // 获取数组元素
    OP_SET_INDEX,   // 设置数组元素
    
    // 对象操作
    OP_GET_FIELD,   // 获取对象字段 (操作数: 常量索引-字段名)
    OP_SET_FIELD,   // 设置对象字段 (操作数: 常量索引-字段名)
    
    // 量子操作（简化）
    OP_QUANTUM_SUPERPOSITION, // 创建叠加态
    OP_QUANTUM_MEASURE,      // 测量量子态
    OP_QUANTUM_ENTANGLE,     // 创建纠缠
    
    // 调试
    OP_PRINT,       // 打印栈顶值
    OP_DUMP_STACK,  // 转储整个栈
    
    // 指令总数
    OP_COUNT
} OpCode;

// ==================== 指令编码辅助 ====================

// 指令格式：操作码(1字节) + 操作数(可变)
#define OPCODE_SIZE 1

// 操作数类型
typedef union {
    uint8_t u8;
    uint16_t u16;
    uint32_t u32;
    uint64_t u64;
    int8_t i8;
    int16_t i16;
    int32_t i32;
    int64_t i64;
    float f32;
    double f64;
} Operand;

// 指令描述
typedef struct {
    const char* name;        // 指令名称
    const char* description; // 指令描述
    size_t operand_size;     // 操作数字节数 (0表示无操作数)
} OpCodeInfo;

// ==================== 公共API ====================

// 获取指令信息
const char* bytecode_opcode_name(uint8_t opcode);
const char* bytecode_opcode_description(uint8_t opcode);
size_t bytecode_opcode_operand_size(uint8_t opcode);

// 反汇编
void bytecode_disassemble(const uint8_t* code, size_t size);
void bytecode_disassemble_instruction(const uint8_t* ip);

#endif // BYTECODE_H