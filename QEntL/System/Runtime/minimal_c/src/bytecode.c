// QEntL最小化运行时 - 字节码模块
// 实现字节码指令集和反汇编器

#include "runtime.h"
#include "bytecode.h"
#include <stdio.h>
#include <string.h>

// ==================== 指令信息表 ====================

static const OpCodeInfo opcode_info[OP_COUNT] = {
    // 空操作和控制流
    [OP_NOP]        = {"NOP",        "空操作", 0},
    [OP_HALT]       = {"HALT",       "停止执行", 0},
    
    // 栈操作
    [OP_PUSH_NIL]   = {"PUSH_NIL",   "压入空值", 0},
    [OP_PUSH_TRUE]  = {"PUSH_TRUE",  "压入真", 0},
    [OP_PUSH_FALSE] = {"PUSH_FALSE", "压入假", 0},
    [OP_PUSH_INT]   = {"PUSH_INT",   "压入整数", 4}, // 32位常量索引
    [OP_PUSH_FLOAT] = {"PUSH_FLOAT", "压入浮点数", 4},
    [OP_PUSH_STRING] = {"PUSH_STRING", "压入字符串", 4},
    [OP_POP]        = {"POP",        "弹出栈顶", 0},
    
    // 算术运算
    [OP_ADD]        = {"ADD",        "加法", 0},
    [OP_SUB]        = {"SUB",        "减法", 0},
    [OP_MUL]        = {"MUL",        "乘法", 0},
    [OP_DIV]        = {"DIV",        "除法", 0},
    [OP_MOD]        = {"MOD",        "取模", 0},
    [OP_NEG]        = {"NEG",        "取负", 0},
    
    // 比较运算
    [OP_EQ]         = {"EQ",         "等于", 0},
    [OP_NEQ]        = {"NEQ",        "不等于", 0},
    [OP_LT]         = {"LT",         "小于", 0},
    [OP_LE]         = {"LE",         "小于等于", 0},
    [OP_GT]         = {"GT",         "大于", 0},
    [OP_GE]         = {"GE",         "大于等于", 0},
    
    // 逻辑运算
    [OP_NOT]        = {"NOT",        "逻辑非", 0},
    [OP_AND]        = {"AND",        "逻辑与", 0},
    [OP_OR]         = {"OR",         "逻辑或", 0},
    
    // 变量操作
    [OP_GET_LOCAL]  = {"GET_LOCAL",  "获取局部变量", 1}, // 8位局部索引
    [OP_SET_LOCAL]  = {"SET_LOCAL",  "设置局部变量", 1},
    [OP_GET_GLOBAL] = {"GET_GLOBAL", "获取全局变量", 4}, // 32位名称索引
    [OP_SET_GLOBAL] = {"SET_GLOBAL", "设置全局变量", 4},
    
    // 跳转
    [OP_JUMP]       = {"JUMP",       "无条件跳转", 4}, // 32位跳转偏移
    [OP_JUMP_IF_TRUE] = {"JUMP_IF_TRUE", "如果为真跳转", 4},
    [OP_JUMP_IF_FALSE] = {"JUMP_IF_FALSE", "如果为假跳转", 4},
    
    // 函数调用
    [OP_CALL]       = {"CALL",       "调用函数", 1}, // 8位参数数量
    [OP_RETURN]     = {"RETURN",     "从函数返回", 0},
    
    // 数组操作
    [OP_NEW_ARRAY]  = {"NEW_ARRAY",  "创建新数组", 4}, // 32位元素数量
    [OP_GET_INDEX]  = {"GET_INDEX",  "获取数组元素", 0},
    [OP_SET_INDEX]  = {"SET_INDEX",  "设置数组元素", 0},
    
    // 对象操作
    [OP_GET_FIELD]  = {"GET_FIELD",  "获取对象字段", 4}, // 32位字段名索引
    [OP_SET_FIELD]  = {"SET_FIELD",  "设置对象字段", 4},
    
    // 量子操作
    [OP_QUANTUM_SUPERPOSITION] = {"QUANTUM_SUPERPOSITION", "创建叠加态", 0},
    [OP_QUANTUM_MEASURE]      = {"QUANTUM_MEASURE",      "测量量子态", 0},
    [OP_QUANTUM_ENTANGLE]     = {"QUANTUM_ENTANGLE",     "创建纠缠", 0},
    
    // 调试
    [OP_PRINT]      = {"PRINT",      "打印栈顶值", 0},
    [OP_DUMP_STACK] = {"DUMP_STACK", "转储整个栈", 0},
};

// ==================== 指令信息API ====================

const char* bytecode_opcode_name(uint8_t opcode) {
    if (opcode >= OP_COUNT) {
        return "UNKNOWN";
    }
    return opcode_info[opcode].name;
}

const char* bytecode_opcode_description(uint8_t opcode) {
    if (opcode >= OP_COUNT) {
        return "未知指令";
    }
    return opcode_info[opcode].description;
}

size_t bytecode_opcode_operand_size(uint8_t opcode) {
    if (opcode >= OP_COUNT) {
        return 0;
    }
    return opcode_info[opcode].operand_size;
}

// ==================== 反汇编器 ====================

// 读取操作数（小端字节序）
static uint32_t read_u32(const uint8_t* ptr) {
    return (uint32_t)ptr[0] | 
           ((uint32_t)ptr[1] << 8) | 
           ((uint32_t)ptr[2] << 16) | 
           ((uint32_t)ptr[3] << 24);
}

static uint16_t read_u16(const uint8_t* ptr) {
    return (uint16_t)ptr[0] | ((uint16_t)ptr[1] << 8);
}

static uint8_t read_u8(const uint8_t* ptr) {
    return ptr[0];
}

void bytecode_disassemble_instruction(const uint8_t* ip) {
    uint8_t opcode = read_u8(ip);
    
    if (opcode >= OP_COUNT) {
        printf("%04zx: %-20s ; 无效操作码: %d\n", 
               (size_t)(ip), "DB", opcode);
        return;
    }
    
    const OpCodeInfo* info = &opcode_info[opcode];
    
    // 打印地址和操作码
    printf("%04zx: %-20s", (size_t)(ip), info->name);
    
    // 打印操作数
    const uint8_t* operand_ptr = ip + 1;
    switch (info->operand_size) {
        case 0:
            printf(" ");
            break;
            
        case 1: {
            uint8_t operand = read_u8(operand_ptr);
            printf(" %-3u", operand);
            break;
        }
            
        case 2: {
            uint16_t operand = read_u16(operand_ptr);
            printf(" %-5u", operand);
            break;
        }
            
        case 4: {
            uint32_t operand = read_u32(operand_ptr);
            printf(" %-10u", operand);
            break;
        }
            
        default:
            printf(" [%zu字节操作数]", info->operand_size);
            break;
    }
    
    // 打印描述
    printf(" ; %s\n", info->description);
}

void bytecode_disassemble(const uint8_t* code, size_t size) {
    printf("=== QEntL字节码反汇编 ===\n");
    printf("大小: %zu 字节\n", size);
    printf("========================\n");
    
    size_t offset = 0;
    while (offset < size) {
        const uint8_t* ip = code + offset;
        uint8_t opcode = read_u8(ip);
        
        if (opcode >= OP_COUNT) {
            printf("%04zx: DB %-18d ; 无效操作码\n", offset, opcode);
            offset += 1;
            continue;
        }
        
        const OpCodeInfo* info = &opcode_info[opcode];
        size_t instruction_size = 1 + info->operand_size;
        
        // 确保不会读取越界
        if (offset + instruction_size > size) {
            printf("%04zx: <截断的指令>\n", offset);
            break;
        }
        
        bytecode_disassemble_instruction(ip);
        offset += instruction_size;
    }
    
    printf("========================\n");
}

// ==================== 字节码构建辅助 ====================

// 字节码构建器实现在runtime.h中定义

BytecodeBuilder* bytecode_builder_create(size_t initial_capacity) {
    BytecodeBuilder* builder = (BytecodeBuilder*)runtime_alloc(sizeof(BytecodeBuilder));
    if (builder == NULL) return NULL;
    
    builder->capacity = initial_capacity > 0 ? initial_capacity : 1024;
    builder->code = (uint8_t*)runtime_alloc(builder->capacity);
    builder->size = 0;
    
    if (builder->code == NULL) {
        runtime_free(builder);
        return NULL;
    }
    
    return builder;
}

void bytecode_builder_free(BytecodeBuilder* builder) {
    if (builder == NULL) return;
    if (builder->code != NULL) {
        runtime_free(builder->code);
    }
    runtime_free(builder);
}

void bytecode_builder_ensure_capacity(BytecodeBuilder* builder, size_t needed) {
    if (builder->size + needed <= builder->capacity) {
        return;
    }
    
    size_t new_capacity = builder->capacity * 2;
    while (builder->size + needed > new_capacity) {
        new_capacity *= 2;
    }
    
    uint8_t* new_code = (uint8_t*)runtime_realloc(builder->code, new_capacity);
    if (new_code == NULL) {
        fprintf(stderr, "字节码构建器扩容失败\n");
        return;
    }
    
    builder->code = new_code;
    builder->capacity = new_capacity;
}

void bytecode_builder_emit_u8(BytecodeBuilder* builder, uint8_t value) {
    bytecode_builder_ensure_capacity(builder, 1);
    builder->code[builder->size++] = value;
}

void bytecode_builder_emit_u16(BytecodeBuilder* builder, uint16_t value) {
    bytecode_builder_ensure_capacity(builder, 2);
    builder->code[builder->size++] = value & 0xFF;
    builder->code[builder->size++] = (value >> 8) & 0xFF;
}

void bytecode_builder_emit_u32(BytecodeBuilder* builder, uint32_t value) {
    bytecode_builder_ensure_capacity(builder, 4);
    builder->code[builder->size++] = value & 0xFF;
    builder->code[builder->size++] = (value >> 8) & 0xFF;
    builder->code[builder->size++] = (value >> 16) & 0xFF;
    builder->code[builder->size++] = (value >> 24) & 0xFF;
}

void bytecode_builder_emit_opcode(BytecodeBuilder* builder, uint8_t opcode) {
    bytecode_builder_emit_u8(builder, opcode);
}

uint8_t* bytecode_builder_get_code(BytecodeBuilder* builder, size_t* out_size) {
    if (out_size != NULL) {
        *out_size = builder->size;
    }
    return builder->code;
}