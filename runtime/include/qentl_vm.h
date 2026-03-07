// QEntL虚拟机核心 - 头文件
// 版本: 1.0.0
// 描述: QEntL字节码解释器和虚拟机实现
// 量子基因编码: QGC-VM-CORE-20260202

#ifndef QENTL_VM_H
#define QENTL_VM_H

#include "qentl_runtime.h"
#include <stdint.h>

// ============================================================================
// 虚拟机常量定义
// ============================================================================

// 虚拟机栈大小（默认）
#define VM_STACK_SIZE 1024

// 虚拟机调用栈大小
#define VM_CALL_STACK_SIZE 256

// 全局变量表大小
#define VM_GLOBALS_SIZE 256

// 最大函数参数数量
#define VM_MAX_ARGS 16

// ============================================================================
// 字节码指令定义
// ============================================================================

typedef enum {
    // 加载和存储指令
    OP_LOAD_CONST,      // 加载常量到栈
    OP_LOAD_GLOBAL,     // 加载全局变量
    OP_STORE_GLOBAL,    // 存储到全局变量
    
    // 栈操作指令
    OP_POP,             // 弹出栈顶
    OP_DUP,             // 复制栈顶
    OP_SWAP,            // 交换栈顶两个元素
    
    // 算术运算指令
    OP_ADD,             // 加法
    OP_SUB,             // 减法
    OP_MUL,             // 乘法
    OP_DIV,             // 除法
    OP_MOD,             // 取模
    OP_NEG,             // 取负
    
    // 比较指令
    OP_EQ,              // 相等
    OP_NE,              // 不相等
    OP_LT,              // 小于
    OP_LE,              // 小于等于
    OP_GT,              // 大于
    OP_GE,              // 大于等于
    
    // 逻辑运算指令
    OP_NOT,             // 逻辑非
    OP_AND,             // 逻辑与
    OP_OR,              // 逻辑或
    
    // 控制流指令
    OP_JUMP,            // 无条件跳转
    OP_JUMP_IF_TRUE,    // 条件为真跳转
    OP_JUMP_IF_FALSE,   // 条件为假跳转
    OP_CALL,            // 调用函数
    OP_RETURN,          // 从函数返回
    
    // 内置函数调用
    OP_PRINT,           // 打印栈顶值
    
    // 特殊指令
    OP_HALT             // 停止虚拟机
} OpCode;

// ============================================================================
// 字节码指令结构
// ============================================================================

typedef struct {
    OpCode opcode;      // 操作码
    union {
        int32_t index;  // 常量表索引或跳转偏移
        int64_t value;  // 立即数值
        double fvalue;  // 浮点立即数值
    } operand;
} Instruction;

// ============================================================================
// 字节码块结构
// ============================================================================

typedef struct {
    size_t capacity;    // 容量
    size_t length;      // 当前长度
    Instruction* code;  // 指令数组
    size_t* lines;      // 源代码行号映射
} BytecodeChunk;

// ============================================================================
// 函数对象结构
// ============================================================================

typedef struct QentlFunction {
    char* name;                 // 函数名
    BytecodeChunk chunk;        // 字节码块
    size_t arity;               // 参数数量
    size_t locals_count;        // 局部变量数量
    struct QentlFunction* next; // 链表下一个
} QentlFunction;

// ============================================================================
// 虚拟机状态结构
// ============================================================================

typedef struct {
    // 执行状态
    QentlValue* stack;          // 值栈
    size_t stack_top;           // 栈顶指针
    size_t stack_capacity;      // 栈容量
    
    // 调用栈
    size_t* call_stack;         // 返回地址栈
    size_t call_stack_top;      // 调用栈顶指针
    
    // 字节码执行
    BytecodeChunk* chunk;       // 当前执行的字节码块
    size_t ip;                  // 指令指针
    
    // 常量池
    QentlValue* constants;      // 常量池
    size_t constants_count;     // 常量数量
    size_t constants_capacity;  // 常量池容量
    
    // 全局变量
    QentlValue* globals;        // 全局变量表
    size_t globals_count;       // 全局变量数量
    
    // 函数表
    QentlFunction* functions;   // 函数链表
    
    // 运行时状态
    bool running;               // 是否正在运行
    QentlErrorType last_error;  // 最后错误类型
    char* error_message;        // 错误消息
} QentlVM;

// ============================================================================
// 字节码块API
// ============================================================================

// 创建字节码块
BytecodeChunk* qentl_bytecode_create(void);

// 销毁字节码块
void qentl_bytecode_destroy(BytecodeChunk* chunk);

// 向字节码块添加指令
size_t qentl_bytecode_add_instruction(BytecodeChunk* chunk, OpCode opcode, int32_t operand);

// 向字节码块添加常量
size_t qentl_bytecode_add_constant(BytecodeChunk* chunk, QentlValue value);

// 获取字节码块中的常量
QentlValue qentl_bytecode_get_constant(BytecodeChunk* chunk, size_t index);

// 反汇编字节码块（调试用）
void qentl_bytecode_disassemble(BytecodeChunk* chunk, const char* name);

// ============================================================================
// 虚拟机API
// ============================================================================

// 创建虚拟机实例
QentlVM* qentl_vm_create(void);

// 销毁虚拟机实例
void qentl_vm_destroy(QentlVM* vm);

// 初始化虚拟机
void qentl_vm_init(QentlVM* vm);

// 重置虚拟机状态
void qentl_vm_reset(QentlVM* vm);

// 加载字节码块到虚拟机
bool qentl_vm_load_chunk(QentlVM* vm, BytecodeChunk* chunk);

// 执行虚拟机
bool qentl_vm_execute(QentlVM* vm);

// 执行单步调试
bool qentl_vm_step(QentlVM* vm);

// 获取虚拟机栈顶值
QentlValue qentl_vm_stack_top(QentlVM* vm);

// 获取虚拟机栈深度
size_t qentl_vm_stack_depth(QentlVM* vm);

// 设置全局变量
bool qentl_vm_set_global(QentlVM* vm, const char* name, QentlValue value);

// 获取全局变量
QentlValue qentl_vm_get_global(QentlVM* vm, const char* name);

// ============================================================================
// 运行时支持函数
// ============================================================================

// 定义内置函数
typedef QentlValue (*QentlNativeFn)(QentlVM* vm, size_t arg_count, QentlValue* args);

// 注册内置函数
bool qentl_vm_register_native(QentlVM* vm, const char* name, QentlNativeFn function);

// ============================================================================
// 虚拟机调试API
// ============================================================================

// 打印虚拟机状态
void qentl_vm_dump_state(QentlVM* vm);

// 打印虚拟机栈
void qentl_vm_dump_stack(QentlVM* vm);

// 设置跟踪模式
void qentl_vm_set_trace(QentlVM* vm, bool enabled);

// ============================================================================
// 简单执行API（高级封装）
// ============================================================================

// 编译并执行QEntL源代码
bool qentl_execute_source(const char* source);

// 编译并执行QEntL文件
bool qentl_execute_file(const char* filename);

// 执行字节码
bool qentl_execute_bytecode(BytecodeChunk* chunk);

#endif // QENTL_VM_H