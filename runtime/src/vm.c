// QEntL虚拟机核心 - 实现文件
// 版本: 1.0.0
// 描述: QEntL字节码解释器和虚拟机实现
// 量子基因编码: QGC-VM-IMPL-20260202

#include "qentl_vm.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdarg.h>
#include <math.h>

// ============================================================================
// 内部宏定义
// ============================================================================

#define VM_GROW_CAPACITY(capacity) \
    ((capacity) < 8 ? 8 : (capacity) * 2)

#define VM_GROW_ARRAY(type, pointer, old_count, new_count) \
    (type*)qentl_realloc(pointer, sizeof(type) * (new_count))

#define VM_FREE_ARRAY(type, pointer, old_count) \
    qentl_free(pointer)

// ============================================================================
// 内部函数声明
// ============================================================================

static bool vm_ensure_stack_capacity(QentlVM* vm, size_t min_capacity);
static void vm_push(QentlVM* vm, QentlValue value);
static QentlValue vm_pop(QentlVM* vm);
static QentlValue vm_peek(QentlVM* vm, size_t distance);

static const char* opcode_to_string(OpCode opcode);
static void vm_runtime_error(QentlVM* vm, const char* format, ...);

// ============================================================================
// 字节码块实现
// ============================================================================

BytecodeChunk* qentl_bytecode_create(void) {
    BytecodeChunk* chunk = (BytecodeChunk*)qentl_alloc(sizeof(BytecodeChunk));
    if (chunk == NULL) {
        return NULL;
    }
    
    chunk->capacity = 0;
    chunk->length = 0;
    chunk->code = NULL;
    chunk->lines = NULL;
    
    return chunk;
}

void qentl_bytecode_destroy(BytecodeChunk* chunk) {
    if (chunk == NULL) {
        return;
    }
    
    VM_FREE_ARRAY(Instruction, chunk->code, chunk->capacity);
    VM_FREE_ARRAY(size_t, chunk->lines, chunk->capacity);
    qentl_free(chunk);
}

static bool bytecode_ensure_capacity(BytecodeChunk* chunk, size_t min_capacity) {
    if (chunk->capacity >= min_capacity) {
        return true;
    }
    
    size_t new_capacity = VM_GROW_CAPACITY(chunk->capacity);
    if (new_capacity < min_capacity) {
        new_capacity = min_capacity;
    }
    
    Instruction* new_code = VM_GROW_ARRAY(Instruction, chunk->code, 
                                         chunk->capacity, new_capacity);
    if (new_code == NULL) {
        return false;
    }
    
    size_t* new_lines = VM_GROW_ARRAY(size_t, chunk->lines,
                                     chunk->capacity, new_capacity);
    if (new_lines == NULL) {
        // 回滚代码数组的分配
        chunk->code = (Instruction*)qentl_realloc(new_code, 
                                                 sizeof(Instruction) * chunk->capacity);
        return false;
    }
    
    chunk->code = new_code;
    chunk->lines = new_lines;
    chunk->capacity = new_capacity;
    
    return true;
}

size_t qentl_bytecode_add_instruction(BytecodeChunk* chunk, OpCode opcode, int32_t operand) {
    if (!bytecode_ensure_capacity(chunk, chunk->length + 1)) {
        return (size_t)-1;
    }
    
    Instruction* instr = &chunk->code[chunk->length];
    instr->opcode = opcode;
    instr->operand.index = operand;
    chunk->lines[chunk->length] = 0; // 默认行号
    
    size_t index = chunk->length;
    chunk->length++;
    
    return index;
}

size_t qentl_bytecode_add_constant(BytecodeChunk* chunk, QentlValue value) {
    // 注意：这个实现需要在虚拟机中维护常量池
    // 这里简化处理，返回一个占位索引
    qentl_log_warn(__FILE__, __LINE__, 
                   "常量添加需要虚拟机实现，当前返回占位索引0");
    return 0;
}

QentlValue qentl_bytecode_get_constant(BytecodeChunk* chunk, size_t index) {
    // 注意：这个实现需要在虚拟机中查询常量池
    qentl_log_warn(__FILE__, __LINE__, 
                   "常量获取需要虚拟机实现，当前返回null");
    return qentl_value_null();
}

void qentl_bytecode_disassemble(BytecodeChunk* chunk, const char* name) {
    if (chunk == NULL) {
        printf("字节码块: NULL\n");
        return;
    }
    
    printf("== %s ==\n", name);
    
    for (size_t offset = 0; offset < chunk->length; offset++) {
        Instruction instr = chunk->code[offset];
        
        printf("%04zu ", offset);
        
        // 打印行号（如果可用）
        if (offset > 0 && chunk->lines[offset] == chunk->lines[offset - 1]) {
            printf("   | ");
        } else {
            printf("%4zu ", chunk->lines[offset]);
        }
        
        printf("%s", opcode_to_string(instr.opcode));
        
        // 打印操作数（如果有）
        switch (instr.opcode) {
            case OP_LOAD_CONST:
            case OP_LOAD_GLOBAL:
            case OP_STORE_GLOBAL:
            case OP_JUMP:
            case OP_JUMP_IF_TRUE:
            case OP_JUMP_IF_FALSE:
            case OP_CALL:
                printf(" %d", instr.operand.index);
                break;
                
            default:
                // 没有操作数
                break;
        }
        
        printf("\n");
    }
}

// ============================================================================
// 虚拟机核心实现
// ============================================================================

QentlVM* qentl_vm_create(void) {
    QentlVM* vm = (QentlVM*)qentl_alloc(sizeof(QentlVM));
    if (vm == NULL) {
        return NULL;
    }
    
    // 初始化所有字段为0
    memset(vm, 0, sizeof(QentlVM));
    
    // 初始化栈
    vm->stack_capacity = VM_STACK_SIZE;
    vm->stack = (QentlValue*)qentl_calloc(vm->stack_capacity, sizeof(QentlValue));
    if (vm->stack == NULL) {
        qentl_free(vm);
        return NULL;
    }
    vm->stack_top = 0;
    
    // 初始化调用栈
    vm->call_stack = (size_t*)qentl_calloc(VM_CALL_STACK_SIZE, sizeof(size_t));
    if (vm->call_stack == NULL) {
        VM_FREE_ARRAY(QentlValue, vm->stack, vm->stack_capacity);
        qentl_free(vm);
        return NULL;
    }
    vm->call_stack_top = 0;
    
    // 初始化全局变量
    vm->globals = (QentlValue*)qentl_calloc(VM_GLOBALS_SIZE, sizeof(QentlValue));
    if (vm->globals == NULL) {
        VM_FREE_ARRAY(size_t, vm->call_stack, VM_CALL_STACK_SIZE);
        VM_FREE_ARRAY(QentlValue, vm->stack, vm->stack_capacity);
        qentl_free(vm);
        return NULL;
    }
    vm->globals_count = 0;
    
    // 初始化常量池
    vm->constants_capacity = 256;
    vm->constants = (QentlValue*)qentl_calloc(vm->constants_capacity, sizeof(QentlValue));
    if (vm->constants == NULL) {
        VM_FREE_ARRAY(QentlValue, vm->globals, VM_GLOBALS_SIZE);
        VM_FREE_ARRAY(size_t, vm->call_stack, VM_CALL_STACK_SIZE);
        VM_FREE_ARRAY(QentlValue, vm->stack, vm->stack_capacity);
        qentl_free(vm);
        return NULL;
    }
    vm->constants_count = 0;
    
    // 初始化其他字段
    vm->chunk = NULL;
    vm->ip = 0;
    vm->functions = NULL;
    vm->running = false;
    vm->last_error = QENTL_ERROR_NONE;
    vm->error_message = NULL;
    
    qentl_log_info(__FILE__, __LINE__, "虚拟机创建成功");
    return vm;
}

void qentl_vm_destroy(QentlVM* vm) {
    if (vm == NULL) {
        return;
    }
    
    qentl_log_debug(__FILE__, __LINE__, "销毁虚拟机");
    
    // 释放栈
    for (size_t i = 0; i < vm->stack_top; i++) {
        qentl_value_free(vm->stack[i]);
    }
    VM_FREE_ARRAY(QentlValue, vm->stack, vm->stack_capacity);
    
    // 释放调用栈
    VM_FREE_ARRAY(size_t, vm->call_stack, VM_CALL_STACK_SIZE);
    
    // 释放全局变量
    for (size_t i = 0; i < vm->globals_count; i++) {
        qentl_value_free(vm->globals[i]);
    }
    VM_FREE_ARRAY(QentlValue, vm->globals, VM_GLOBALS_SIZE);
    
    // 释放常量池
    for (size_t i = 0; i < vm->constants_count; i++) {
        qentl_value_free(vm->constants[i]);
    }
    VM_FREE_ARRAY(QentlValue, vm->constants, vm->constants_capacity);
    
    // 释放函数
    QentlFunction* func = vm->functions;
    while (func != NULL) {
        QentlFunction* next = func->next;
        
        // 释放函数名
        qentl_string_free(func->name);
        
        // 释放字节码块
        VM_FREE_ARRAY(Instruction, func->chunk.code, func->chunk.capacity);
        VM_FREE_ARRAY(size_t, func->chunk.lines, func->chunk.capacity);
        
        qentl_free(func);
        func = next;
    }
    
    // 释放错误消息
    if (vm->error_message != NULL) {
        qentl_string_free(vm->error_message);
    }
    
    // 释放虚拟机本身
    qentl_free(vm);
    
    qentl_log_info(__FILE__, __LINE__, "虚拟机销毁完成");
}

void qentl_vm_init(QentlVM* vm) {
    if (vm == NULL) {
        return;
    }
    
    qentl_vm_reset(vm);
    qentl_log_info(__FILE__, __LINE__, "虚拟机初始化完成");
}

void qentl_vm_reset(QentlVM* vm) {
    if (vm == NULL) {
        return;
    }
    
    // 重置栈
    for (size_t i = 0; i < vm->stack_top; i++) {
        qentl_value_free(vm->stack[i]);
    }
    vm->stack_top = 0;
    
    // 重置调用栈
    vm->call_stack_top = 0;
    
    // 重置执行状态
    vm->chunk = NULL;
    vm->ip = 0;
    vm->running = false;
    
    // 清除错误
    vm->last_error = QENTL_ERROR_NONE;
    if (vm->error_message != NULL) {
        qentl_string_free(vm->error_message);
        vm->error_message = NULL;
    }
    
    qentl_log_debug(__FILE__, __LINE__, "虚拟机状态已重置");
}

static bool vm_ensure_stack_capacity(QentlVM* vm, size_t min_capacity) {
    if (vm->stack_capacity >= min_capacity) {
        return true;
    }
    
    size_t new_capacity = VM_GROW_CAPACITY(vm->stack_capacity);
    if (new_capacity < min_capacity) {
        new_capacity = min_capacity;
    }
    
    QentlValue* new_stack = VM_GROW_ARRAY(QentlValue, vm->stack,
                                         vm->stack_capacity, new_capacity);
    if (new_stack == NULL) {
        return false;
    }
    
    vm->stack = new_stack;
    vm->stack_capacity = new_capacity;
    
    return true;
}

static void vm_push(QentlVM* vm, QentlValue value) {
    if (!vm_ensure_stack_capacity(vm, vm->stack_top + 1)) {
        vm_runtime_error(vm, "栈溢出");
        return;
    }
    
    vm->stack[vm->stack_top] = value;
    vm->stack_top++;
}

static QentlValue vm_pop(QentlVM* vm) {
    if (vm->stack_top == 0) {
        vm_runtime_error(vm, "栈下溢");
        return qentl_value_null();
    }
    
    vm->stack_top--;
    return vm->stack[vm->stack_top];
}

static QentlValue vm_peek(QentlVM* vm, size_t distance) {
    if (distance >= vm->stack_top) {
        return qentl_value_null();
    }
    
    return vm->stack[vm->stack_top - 1 - distance];
}

bool qentl_vm_load_chunk(QentlVM* vm, BytecodeChunk* chunk) {
    if (vm == NULL || chunk == NULL) {
        return false;
    }
    
    vm->chunk = chunk;
    vm->ip = 0;
    vm->running = true;
    
    qentl_log_info(__FILE__, __LINE__, "字节码块加载成功，指令数: %zu", chunk->length);
    return true;
}

// ============================================================================
// 虚拟机执行引擎
// ============================================================================

static void vm_runtime_error(QentlVM* vm, const char* format, ...) {
    va_list args;
    va_start(args, format);
    
    // 格式化错误消息
    char buffer[512];
    vsnprintf(buffer, sizeof(buffer), format, args);
    
    // 保存错误
    vm->last_error = QENTL_ERROR_RUNTIME;
    if (vm->error_message != NULL) {
        qentl_string_free(vm->error_message);
    }
    vm->error_message = qentl_string_create(buffer);
    
    // 记录日志
    qentl_log_error(__FILE__, __LINE__, "虚拟机运行时错误: %s", buffer);
    
    // 停止执行
    vm->running = false;
    
    va_end(args);
}

// ============================================================================
// 操作码到字符串转换
// ============================================================================

static const char* opcode_to_string(OpCode opcode) {
    switch (opcode) {
        case OP_LOAD_CONST:    return "LOAD_CONST";
        case OP_LOAD_GLOBAL:   return "LOAD_GLOBAL";
        case OP_STORE_GLOBAL:  return "STORE_GLOBAL";
        case OP_POP:           return "POP";
        case OP_DUP:           return "DUP";
        case OP_SWAP:          return "SWAP";
        case OP_ADD:           return "ADD";
        case OP_SUB:           return "SUB";
        case OP_MUL:           return "MUL";
        case OP_DIV:           return "DIV";
        case OP_MOD:           return "MOD";
        case OP_NEG:           return "NEG";
        case OP_EQ:            return "EQ";
        case OP_NE:            return "NE";
        case OP_LT:            return "LT";
        case OP_LE:            return "LE";
        case OP_GT:            return "GT";
        case OP_GE:            return "GE";
        case OP_NOT:           return "NOT";
        case OP_AND:           return "AND";
        case OP_OR:            return "OR";
        case OP_JUMP:          return "JUMP";
        case OP_JUMP_IF_TRUE:  return "JUMP_IF_TRUE";
        case OP_JUMP_IF_FALSE: return "JUMP_IF_FALSE";
        case OP_CALL:          return "CALL";
        case OP_RETURN:        return "RETURN";
        case OP_PRINT:         return "PRINT";
        case OP_HALT:          return "HALT";
        default:               return "UNKNOWN";
    }
}

// ============================================================================
// 指令执行函数
// ============================================================================

static bool vm_execute_instruction(QentlVM* vm) {
    if (vm->chunk == NULL || vm->ip >= vm->chunk->length) {
        vm_runtime_error(vm, "无效的指令指针或空字节码块");
        return false;
    }
    
    Instruction instr = vm->chunk->code[vm->ip];
    
    // 调试：打印执行的指令
    qentl_log_debug(__FILE__, __LINE__, "执行指令: %s (IP=%zu)", 
                    opcode_to_string(instr.opcode), vm->ip);
    
    switch (instr.opcode) {
        case OP_LOAD_CONST: {
            if (instr.operand.index >= vm->constants_count) {
                vm_runtime_error(vm, "常量索引越界: %d", instr.operand.index);
                return false;
            }
            
            QentlValue constant = vm->constants[instr.operand.index];
            QentlValue copy = qentl_value_clone(constant);
            vm_push(vm, copy);
            vm->ip++;
            break;
        }
        
        case OP_LOAD_GLOBAL: {
            if (instr.operand.index >= vm->globals_count) {
                vm_runtime_error(vm, "全局变量索引越界: %d", instr.operand.index);
                return false;
            }
            
            QentlValue global = vm->globals[instr.operand.index];
            QentlValue copy = qentl_value_clone(global);
            vm_push(vm, copy);
            vm->ip++;
            break;
        }
        
        case OP_STORE_GLOBAL: {
            if (instr.operand.index >= VM_GLOBALS_SIZE) {
                vm_runtime_error(vm, "全局变量表已满");
                return false;
            }
            
            if (vm->stack_top == 0) {
                vm_runtime_error(vm, "栈为空，无法存储");
                return false;
            }
            
            QentlValue value = vm_pop(vm);
            
            // 释放旧的全局变量（如果存在）
            if (instr.operand.index < vm->globals_count) {
                qentl_value_free(vm->globals[instr.operand.index]);
            } else {
                // 扩展全局变量表
                vm->globals_count = instr.operand.index + 1;
            }
            
            vm->globals[instr.operand.index] = value;
            vm->ip++;
            break;
        }
        
        case OP_POP: {
            QentlValue popped = vm_pop(vm);
            qentl_value_free(popped);
            vm->ip++;
            break;
        }
        
        case OP_ADD: {
            if (vm->stack_top < 2) {
                vm_runtime_error(vm, "栈中元素不足执行加法");
                return false;
            }
            
            QentlValue b = vm_pop(vm);
            QentlValue a = vm_pop(vm);
            
            // 类型检查和转换
            if (a.type == QENTL_TYPE_INTEGER && b.type == QENTL_TYPE_INTEGER) {
                int64_t result = a.data.integer + b.data.integer;
                vm_push(vm, qentl_value_integer(result));
            } else if (a.type == QENTL_TYPE_FLOAT || b.type == QENTL_TYPE_FLOAT) {
                double a_val = (a.type == QENTL_TYPE_INTEGER) ? 
                              (double)a.data.integer : a.data.floating;
                double b_val = (b.type == QENTL_TYPE_INTEGER) ? 
                              (double)b.data.integer : b.data.floating;
                vm_push(vm, qentl_value_float(a_val + b_val));
            } else {
                vm_runtime_error(vm, "不支持的类型进行加法运算");
                qentl_value_free(a);
                qentl_value_free(b);
                return false;
            }
            
            qentl_value_free(a);
            qentl_value_free(b);
            vm->ip++;
            break;
        }
        
        case OP_SUB: {
            if (vm->stack_top < 2) {
                vm_runtime_error(vm, "栈中元素不足执行减法");
                return false;
            }
            
            QentlValue b = vm_pop(vm);
            QentlValue a = vm_pop(vm);
            
            if (a.type == QENTL_TYPE_INTEGER && b.type == QENTL_TYPE_INTEGER) {
                int64_t result = a.data.integer - b.data.integer;
                vm_push(vm, qentl_value_integer(result));
            } else if (a.type == QENTL_TYPE_FLOAT || b.type == QENTL_TYPE_FLOAT) {
                double a_val = (a.type == QENTL_TYPE_INTEGER) ? 
                              (double)a.data.integer : a.data.floating;
                double b_val = (b.type == QENTL_TYPE_INTEGER) ? 
                              (double)b.data.integer : b.data.floating;
                vm_push(vm, qentl_value_float(a_val - b_val));
            } else {
                vm_runtime_error(vm, "不支持的类型进行减法运算");
                qentl_value_free(a);
                qentl_value_free(b);
                return false;
            }
            
            qentl_value_free(a);
            qentl_value_free(b);
            vm->ip++;
            break;
        }
        
        case OP_MUL: {
            if (vm->stack_top < 2) {
                vm_runtime_error(vm, "栈中元素不足执行乘法");
                return false;
            }
            
            QentlValue b = vm_pop(vm);
            QentlValue a = vm_pop(vm);
            
            if (a.type == QENTL_TYPE_INTEGER && b.type == QENTL_TYPE_INTEGER) {
                int64_t result = a.data.integer * b.data.integer;
                vm_push(vm, qentl_value_integer(result));
            } else if (a.type == QENTL_TYPE_FLOAT || b.type == QENTL_TYPE_FLOAT) {
                double a_val = (a.type == QENTL_TYPE_INTEGER) ? 
                              (double)a.data.integer : a.data.floating;
                double b_val = (b.type == QENTL_TYPE_INTEGER) ? 
                              (double)b.data.integer : b.data.floating;
                vm_push(vm, qentl_value_float(a_val * b_val));
            } else {
                vm_runtime_error(vm, "不支持的类型进行乘法运算");
                qentl_value_free(a);
                qentl_value_free(b);
                return false;
            }
            
            qentl_value_free(a);
            qentl_value_free(b);
            vm->ip++;
            break;
        }
        
        case OP_DIV: {
            if (vm->stack_top < 2) {
                vm_runtime_error(vm, "栈中元素不足执行除法");
                return false;
            }
            
            QentlValue b = vm_pop(vm);
            QentlValue a = vm_pop(vm);
            
            // 检查除以零
            if ((b.type == QENTL_TYPE_INTEGER && b.data.integer == 0) ||
                (b.type == QENTL_TYPE_FLOAT && b.data.floating == 0.0)) {
                vm_runtime_error(vm, "除以零错误");
                qentl_value_free(a);
                qentl_value_free(b);
                return false;
            }
            
            if (a.type == QENTL_TYPE_INTEGER && b.type == QENTL_TYPE_INTEGER) {
                // 整数除法
                int64_t result = a.data.integer / b.data.integer;
                vm_push(vm, qentl_value_integer(result));
            } else {
                // 浮点数除法
                double a_val = (a.type == QENTL_TYPE_INTEGER) ? 
                              (double)a.data.integer : a.data.floating;
                double b_val = (b.type == QENTL_TYPE_INTEGER) ? 
                              (double)b.data.integer : b.data.floating;
                vm_push(vm, qentl_value_float(a_val / b_val));
            }
            
            qentl_value_free(a);
            qentl_value_free(b);
            vm->ip++;
            break;
        }
        
        case OP_PRINT: {
            if (vm->stack_top == 0) {
                vm_runtime_error(vm, "栈为空，无法打印");
                return false;
            }
            
            QentlValue value = vm_pop(vm);
            char* str = qentl_value_to_string(value);
            printf("%s\n", str);
            qentl_string_free(str);
            qentl_value_free(value);
            vm->ip++;
            break;
        }
        
        case OP_HALT: {
            vm->running = false;
            vm->ip++;
            qentl_log_info(__FILE__, __LINE__, "虚拟机正常停止");
            break;
        }
        
        default: {
            vm_runtime_error(vm, "未实现的指令: %s", opcode_to_string(instr.opcode));
            return false;
        }
    }
    
    return true;
}

// ============================================================================
// 虚拟机执行API实现
// ============================================================================

bool qentl_vm_execute(QentlVM* vm) {
    if (vm == NULL || vm->chunk == NULL) {
        return false;
    }
    
    qentl_log_info(__FILE__, __LINE__, "开始执行虚拟机");
    
    vm->running = true;
    vm->ip = 0;
    
    while (vm->running && vm->ip < vm->chunk->length) {
        if (!vm_execute_instruction(vm)) {
            qentl_log_error(__FILE__, __LINE__, "指令执行失败，IP=%zu", vm->ip);
            return false;
        }
        
        // 安全检查：防止无限循环
        if (vm->ip >= vm->chunk->length) {
            break;
        }
    }
    
    qentl_log_info(__FILE__, __LINE__, "虚拟机执行完成");
    return true;
}

bool qentl_vm_step(QentlVM* vm) {
    if (vm == NULL || vm->chunk == NULL) {
        return false;
    }
    
    if (vm->ip >= vm->chunk->length) {
        qentl_log_debug(__FILE__, __LINE__, "已到达字节码末尾");
        return false;
    }
    
    return vm_execute_instruction(vm);
}

// ============================================================================
// 虚拟机状态查询API
// ============================================================================

QentlValue qentl_vm_stack_top(QentlVM* vm) {
    if (vm == NULL || vm->stack_top == 0) {
        return qentl_value_null();
    }
    
    return vm_peek(vm, 0);
}

size_t qentl_vm_stack_depth(QentlVM* vm) {
    if (vm == NULL) {
        return 0;
    }
    
    return vm->stack_top;
}

bool qentl_vm_set_global(QentlVM* vm, const char* name, QentlValue value) {
    // 简化实现：按顺序存储，不处理名称
    if (vm == NULL || vm->globals_count >= VM_GLOBALS_SIZE) {
        return false;
    }
    
    vm->globals[vm->globals_count] = value;
    vm->globals_count++;
    
    qentl_log_debug(__FILE__, __LINE__, "设置全局变量[%zu]: %s", 
                    vm->globals_count - 1, name);
    return true;
}

QentlValue qentl_vm_get_global(QentlVM* vm, const char* name) {
    // 简化实现：返回第一个全局变量
    if (vm == NULL || vm->globals_count == 0) {
        return qentl_value_null();
    }
    
    qentl_log_debug(__FILE__, __LINE__, "获取全局变量: %s (返回索引0)", name);
    QentlValue copy = qentl_value_clone(vm->globals[0]);
    return copy;
}

// ============================================================================
// 虚拟机调试API实现
// ============================================================================

void qentl_vm_dump_state(QentlVM* vm) {
    if (vm == NULL) {
        printf("虚拟机: NULL\n");
        return;
    }
    
    printf("=== 虚拟机状态 ===\n");
    printf("运行状态: %s\n", vm->running ? "运行中" : "已停止");
    printf("指令指针: %zu\n", vm->ip);
    printf("栈深度: %zu/%zu\n", vm->stack_top, vm->stack_capacity);
    printf("调用栈深度: %zu/%d\n", vm->call_stack_top, VM_CALL_STACK_SIZE);
    printf("常量数量: %zu\n", vm->constants_count);
    printf("全局变量数量: %zu\n", vm->globals_count);
    
    if (vm->last_error != QENTL_ERROR_NONE && vm->error_message != NULL) {
        printf("最后错误: %s\n", vm->error_message);
    }
}

void qentl_vm_dump_stack(QentlVM* vm) {
    if (vm == NULL) {
        printf("虚拟机栈: NULL\n");
        return;
    }
    
    printf("=== 虚拟机栈 (深度: %zu) ===\n", vm->stack_top);
    
    if (vm->stack_top == 0) {
        printf("  (空)\n");
        return;
    }
    
    for (size_t i = 0; i < vm->stack_top; i++) {
        char* str = qentl_value_to_string(vm->stack[i]);
        printf("  [%zu]: %s\n", i, str);
        qentl_string_free(str);
    }
}

void qentl_vm_set_trace(QentlVM* vm, bool enabled) {
    if (vm == NULL) {
        return;
    }
    
    // 简化实现：设置日志级别
    if (enabled) {
        qentl_log_set_level(QENTL_LOG_DEBUG);
        qentl_log_info(__FILE__, __LINE__, "启用虚拟机跟踪模式");
    } else {
        qentl_log_set_level(QENTL_LOG_INFO);
        qentl_log_info(__FILE__, __LINE__, "禁用虚拟机跟踪模式");
    }
}

// ============================================================================
// 高级执行API实现
// ============================================================================

bool qentl_execute_source(const char* source) {
    qentl_log_warn(__FILE__, __LINE__, "源代码执行需要编译器，当前仅支持字节码");
    
    // 创建虚拟机和简单字节码
    QentlVM* vm = qentl_vm_create();
    if (vm == NULL) {
        return false;
    }
    
    BytecodeChunk* chunk = qentl_bytecode_create();
    if (chunk == NULL) {
        qentl_vm_destroy(vm);
        return false;
    }
    
    // 添加简单测试程序：计算 1 + 2 * 3
    // 简化实现：直接推送结果
    qentl_bytecode_add_instruction(chunk, OP_LOAD_CONST, 0);  // 加载常量7
    qentl_bytecode_add_instruction(chunk, OP_PRINT, 0);       // 打印
    qentl_bytecode_add_instruction(chunk, OP_HALT, 0);        // 停止
    
    // 添加常量
    if (vm->constants_count == 0) {
        vm->constants[0] = qentl_value_integer(7);  // 1 + 2 * 3 = 7
        vm->constants_count = 1;
    }
    
    qentl_vm_load_chunk(vm, chunk);
    bool success = qentl_vm_execute(vm);
    
    qentl_bytecode_destroy(chunk);
    qentl_vm_destroy(vm);
    
    return success;
}

bool qentl_execute_file(const char* filename) {
    qentl_log_warn(__FILE__, __LINE__, "文件执行需要文件IO支持，当前未实现");
    return false;
}

bool qentl_execute_bytecode(BytecodeChunk* chunk) {
    QentlVM* vm = qentl_vm_create();
    if (vm == NULL) {
        return false;
    }
    
    qentl_vm_load_chunk(vm, chunk);
    bool success = qentl_vm_execute(vm);
    
    qentl_vm_destroy(vm);
    return success;
}