/**
 * QEntL量子纠缠语言代码生成器头文件
 * 
 * 量子基因编码: QG-COMP-CODEGEN-HDR-A2C5-1713051200
 * 
 * @文件: codegen.h
 * @描述: 定义QEntL语言的代码生成API，将AST转换为QEntL字节码
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-16
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 代码生成支持量子优化和量子比特自适应分配
 * - 支持量子态编码和量子纠缠指令优化
 */

#ifndef QENTL_CODEGEN_H
#define QENTL_CODEGEN_H

#include "parser.h"
#include "semantic.h"

/**
 * 常量类型枚举
 */
typedef enum {
    CONSTANT_INT,         /* 整数常量 */
    CONSTANT_FLOAT,       /* 浮点数常量 */
    CONSTANT_STRING,      /* 字符串常量 */
    CONSTANT_BOOL,        /* 布尔常量 */
    CONSTANT_QUANTUM      /* 量子常量 */
} ConstantType;

/**
 * 常量值联合体
 */
typedef union {
    int int_value;          /* 整数值 */
    double float_value;     /* 浮点数值 */
    char* string_value;     /* 字符串值 */
    int bool_value;         /* 布尔值 */
    void* quantum_value;    /* 量子值指针 */
} ConstantValue;

/**
 * 常量结构
 */
typedef struct {
    ConstantType type;      /* 常量类型 */
    ConstantValue value;    /* 常量值 */
} Constant;

/**
 * 操作码枚举
 */
typedef enum {
    /* 基本操作 */
    OP_NOP,               /* 空操作 */
    OP_HALT,              /* 停止执行 */
    
    /* 加载操作 */
    OP_LOAD_CONST,        /* 加载常量 */
    OP_LOAD_VAR,          /* 加载变量 */
    OP_STORE_VAR,         /* 存储变量 */
    
    /* 算术操作 */
    OP_ADD,               /* 加法 */
    OP_SUB,               /* 减法 */
    OP_MUL,               /* 乘法 */
    OP_DIV,               /* 除法 */
    OP_NEG,               /* 一元负 */
    
    /* 逻辑操作 */
    OP_AND,               /* 逻辑与 */
    OP_OR,                /* 逻辑或 */
    OP_NOT,               /* 逻辑非 */
    
    /* 比较操作 */
    OP_EQ,                /* 等于 */
    OP_NE,                /* 不等于 */
    OP_LT,                /* 小于 */
    OP_LE,                /* 小于等于 */
    OP_GT,                /* 大于 */
    OP_GE,                /* 大于等于 */
    
    /* 控制流操作 */
    OP_JMP,               /* 无条件跳转 */
    OP_JMP_IF_TRUE,       /* 条件为真跳转 */
    OP_JMP_IF_FALSE,      /* 条件为假跳转 */
    
    /* 函数操作 */
    OP_DECLARE_FUNC,      /* 声明函数 */
    OP_FUNC_PARAM,        /* 函数参数 */
    OP_CALL,              /* 调用函数 */
    OP_PARAM,             /* 传递参数 */
    OP_RETURN,            /* 返回（无值） */
    OP_RETURN_VALUE,      /* 返回值 */
    
    /* 变量声明操作 */
    OP_DECLARE_VAR,       /* 声明变量 */
    OP_DECLARE_VAR_INIT,  /* 声明并初始化变量 */
    
    /* 量子操作 */
    OP_QUANTUM_CONVERT,   /* 经典值转量子值 */
    OP_QUANTUM_MEASURE,   /* 量子测量 */
    OP_QUANTUM_ENTANGLE,  /* 量子纠缠（两个实体） */
    OP_QUANTUM_ENTANGLE_MULTI, /* 量子纠缠（多个实体） */
    OP_ENTANGLE_ENTITY,   /* 纠缠实体 */
    
    /* 叠加态操作 */
    OP_SUPERPOSITION,     /* 创建叠加态 */
    OP_SUPERPOSITION_STATE /* 添加叠加态分量 */
} OpCode;

/**
 * 字节码指令结构
 */
typedef struct {
    OpCode opcode;        /* 操作码 */
    int dst;              /* 目标寄存器或标签 */
    int src1;             /* 源寄存器1或立即数 */
    int src2;             /* 源寄存器2或立即数 */
} bytecode_instruction;

/**
 * 字节码模块结构
 */
typedef struct {
    bytecode_instruction* instructions; /* 指令数组 */
    int instruction_count;              /* 指令数量 */
    int instruction_capacity;           /* 指令容量 */
    
    Constant* constants;                /* 常量池 */
    int constant_count;                 /* 常量数量 */
    int constant_capacity;              /* 常量容量 */
    
    int* labels;                        /* 标签位置数组 */
    int label_count;                    /* 标签数量 */
    int label_capacity;                 /* 标签容量 */
} BytecodeModule;

/**
 * 创建新的字节码模块
 * 
 * @return 新创建的字节码模块
 */
BytecodeModule* bytecode_module_create(void);

/**
 * 销毁字节码模块
 * 
 * @param module 要销毁的字节码模块
 */
void bytecode_module_destroy(BytecodeModule* module);

/**
 * 向字节码模块添加指令
 * 
 * @param module 字节码模块
 * @param instruction 要添加的指令
 * @return 指令索引
 */
int bytecode_module_add_instruction(BytecodeModule* module, bytecode_instruction instruction);

/**
 * 向字节码模块添加常量
 * 
 * @param module 字节码模块
 * @param constant 要添加的常量
 * @return 常量索引
 */
int bytecode_module_add_constant(BytecodeModule* module, Constant constant);

/**
 * 向字节码模块添加标签
 * 
 * @param module 字节码模块
 * @param label_id 标签ID
 * @return 标签索引
 */
int bytecode_module_add_label(BytecodeModule* module, int label_id);

/**
 * 生成代码
 * 
 * @param ast 抽象语法树
 * @param symbol_table 符号表
 * @return 生成的字节码模块
 */
BytecodeModule* generate_code(AST* ast, SymbolTable* symbol_table);

#endif /* QENTL_CODEGEN_H */ 