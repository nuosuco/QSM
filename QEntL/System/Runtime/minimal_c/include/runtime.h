// QEntL最小化C运行时 - 公共头文件（修复版）
// 为QEntL量子语言提供最小化运行时支持
// 设计原则：完全自主、最小化、可被QEntL代码逐步替换

#ifndef RUNTIME_H
#define RUNTIME_H

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

// ==================== 前向声明 ====================

typedef struct Value Value;
typedef struct VM VM;
typedef struct BytecodeBuilder BytecodeBuilder;

// ==================== 基础类型定义 ====================

// QEntL类型枚举
typedef enum {
    TYPE_NIL,      // 空值
    TYPE_BOOL,     // 布尔
    TYPE_INT,      // 整数
    TYPE_FLOAT,    // 浮点数
    TYPE_STRING,   // 字符串
    TYPE_ARRAY,    // 数组
    TYPE_MAP,      // 映射
    TYPE_FUNCTION, // 函数
    TYPE_OBJECT,   // 对象
    TYPE_QUANTUM,  // 量子类型
} ValueType;

// 统一值表示
struct Value {
    ValueType type;
    union {
        bool boolean;
        int64_t integer;
        double number;
        struct {
            char* chars;
            size_t length;
        } string;
        struct {
            Value* items;       // 使用Value*而不是struct Value*
            size_t count;
            size_t capacity;
        } array;
        struct {
            Value* keys;        // 使用Value*而不是struct Value*
            Value* values;      // 使用Value*而不是struct Value*
            size_t count;
            size_t capacity;
        } map;
        struct {
            void* code;      // 函数代码指针
            size_t arity;    // 参数数量
        } function;
        void* pointer;       // 通用指针
    } as;
};

// ==================== 内存管理 ====================

// 内存分配器接口
typedef struct {
    void* (*alloc)(size_t size);
    void* (*realloc)(void* ptr, size_t new_size);
    void (*free)(void* ptr);
    size_t total_allocated;
    size_t peak_allocated;
} Allocator;

// 垃圾收集器接口
typedef struct {
    void (*collect)(void);
    size_t (*get_allocated)(void);
    size_t (*get_threshold)(void);
    void (*set_threshold)(size_t threshold);
} GarbageCollector;

// ==================== 虚拟机 ====================

// 虚拟机状态
struct VM {
    Value* stack;           // 调用栈
    size_t stack_size;      // 栈大小
    size_t stack_top;       // 栈顶指针
    
    Value* constants;       // 常量池
    size_t constant_count;  // 常量数量
    
    uint8_t* bytecode;      // 字节码
    size_t bytecode_size;   // 字节码大小
    size_t ip;              // 指令指针
    
    Allocator* allocator;   // 内存分配器
    GarbageCollector* gc;   // 垃圾收集器
    
    bool running;           // 运行标志
    int exit_code;          // 退出代码
};

// ==================== 字节码构建器 ====================

// 字节码构建器结构
struct BytecodeBuilder {
    uint8_t* code;
    size_t size;
    size_t capacity;
};

// ==================== 公共API ====================

// 内存管理API
void* runtime_alloc(size_t size);
void* runtime_realloc(void* ptr, size_t new_size);
void runtime_free(void* ptr);
size_t runtime_get_allocated(void);
void runtime_gc_collect(void);
void runtime_print_memory_stats(void);

// 字符串专用分配器
char* runtime_alloc_string(size_t length);
size_t runtime_string_length(const char* str);
void runtime_free_string(char* str);

// 值数组分配器
Value* runtime_alloc_value_array(size_t count);
Value* runtime_realloc_value_array(Value* array, size_t new_count);

// 值操作API
Value value_nil(void);
Value value_bool(bool b);
Value value_int(int64_t i);
Value value_float(double f);
Value value_string(const char* chars, size_t length);
Value value_string_copy(const char* chars);
Value value_array(size_t initial_capacity);
void value_array_push(Value* array, Value value);
Value value_array_get(Value* array, size_t index);
void value_array_set(Value* array, size_t index, Value value);
size_t value_array_length(Value* array);
bool value_is_nil(Value value);
bool value_is_bool(Value value);
bool value_is_int(Value value);
bool value_is_float(Value value);
bool value_is_string(Value value);
bool value_is_array(Value value);
bool value_is_number(Value value);
bool value_is_truthy(Value value);
const char* value_type_name(ValueType type);
const char* value_to_string(Value value);
bool value_equals(Value a, Value b);
void value_free(Value* value);
void value_print(Value value);
void value_println(Value value);

// 数值操作
double value_to_number(Value value);
int64_t value_to_int(Value value);
Value value_add(Value a, Value b);
Value value_sub(Value a, Value b);
Value value_mul(Value a, Value b);
Value value_div(Value a, Value b);
Value value_mod(Value a, Value b);
Value value_neg(Value a);
bool value_lt(Value a, Value b);
bool value_le(Value a, Value b);
bool value_gt(Value a, Value b);
bool value_ge(Value a, Value b);
Value value_not(Value a);
Value value_and(Value a, Value b);
Value value_or(Value a, Value b);
Value value_string_concat(Value a, Value b);
bool value_string_equals(Value a, Value b);
Value value_array_slice(Value* array, size_t start, size_t end);
void value_array_clear(Value* array);
Value value_copy(Value value);

// 虚拟机API
VM* vm_create(void);
void vm_free(VM* vm);
void vm_load_bytecode(VM* vm, uint8_t* bytecode, size_t size);
int vm_execute(VM* vm);
void vm_push(VM* vm, Value value);
Value vm_pop(VM* vm);
Value vm_peek(VM* vm, size_t depth);
Value vm_get_constant(VM* vm, uint32_t index);
uint32_t vm_add_constant(VM* vm, Value value);
void vm_run_test(void);

// 编译器支持API（用于运行QEntL编译器）
int runtime_execute_qentl_compiler(const char* source_code);
int runtime_execute_bytecode_file(const char* filename);
int runtime_bootstrap_qentl_compiler(void);

// 测试API
void runtime_run_tests(void);

// 字节码构建器
BytecodeBuilder* bytecode_builder_create(size_t initial_capacity);
void bytecode_builder_free(BytecodeBuilder* builder);
void bytecode_builder_emit_opcode(BytecodeBuilder* builder, uint8_t opcode);
void bytecode_builder_emit_u8(BytecodeBuilder* builder, uint8_t value);
void bytecode_builder_emit_u32(BytecodeBuilder* builder, uint32_t value);
uint8_t* bytecode_builder_get_code(BytecodeBuilder* builder, size_t* out_size);

// 字节码反汇编
void bytecode_disassemble(const uint8_t* code, size_t size);

// 文件加载
uint8_t* load_file(const char* filename, size_t* out_size);

#endif // RUNTIME_H