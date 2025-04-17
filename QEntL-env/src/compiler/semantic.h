/**
 * QEntL量子纠缠语言语义分析器头文件
 * 
 * 量子基因编码: QG-COMP-SEM-HDR-A1C3-1713051200
 * 
 * @文件: semantic.h
 * @描述: 定义QEntL语言的语义分析API
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-16
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 语义分析支持量子叠加分析和量子基因表达式验证
 * - 能分析量子纠缠链接的合法性和资源消耗
 */

#ifndef QENTL_SEMANTIC_H
#define QENTL_SEMANTIC_H

#include "parser.h"

/**
 * 错误列表结构
 */
typedef struct {
    char** messages;         /* 错误消息数组 */
    int count;               /* 错误数量 */
    int capacity;            /* 容量 */
} ErrorList;

/**
 * 创建错误列表
 * 
 * @return 新创建的错误列表
 */
ErrorList* error_list_create(void);

/**
 * 向错误列表添加错误
 * 
 * @param list 错误列表
 * @param message 错误消息
 */
void error_list_add(ErrorList* list, const char* message);

/**
 * 销毁错误列表
 * 
 * @param list 要销毁的错误列表
 */
void error_list_destroy(ErrorList* list);

/**
 * 克隆错误列表
 * 
 * @param list 源错误列表
 * @return 克隆的错误列表
 */
ErrorList* error_list_clone(ErrorList* list);

/**
 * 符号类型枚举
 */
typedef enum {
    SYMBOL_VARIABLE,     /* 变量符号 */
    SYMBOL_FUNCTION,     /* 函数符号 */
    SYMBOL_TYPE,         /* 类型符号 */
    SYMBOL_NAMESPACE     /* 命名空间符号 */
} SymbolType;

/**
 * 数据类型枚举
 */
typedef enum {
    TYPE_UNKNOWN,        /* 未知类型 */
    TYPE_VOID,           /* 空类型 */
    TYPE_INT,            /* 整数类型 */
    TYPE_FLOAT,          /* 浮点数类型 */
    TYPE_BOOL,           /* 布尔类型 */
    TYPE_STRING,         /* 字符串类型 */
    TYPE_QUANTUM_INT,    /* 量子整数类型 */
    TYPE_QUANTUM_FLOAT,  /* 量子浮点数类型 */
    TYPE_QUANTUM_BOOL,   /* 量子布尔类型 */
    TYPE_QUANTUM_STRING, /* 量子字符串类型 */
    TYPE_SUPERPOSITION,  /* 量子叠加态 */
    TYPE_ENTANGLEMENT    /* 量子纠缠类型 */
} DataType;

/**
 * 函数类型数据
 */
typedef struct {
    DataType return_type;    /* 返回类型 */
    DataType* param_types;   /* 参数类型数组 */
    int param_count;         /* 参数数量 */
} FunctionTypeData;

/**
 * 符号结构
 */
typedef struct Symbol {
    char* name;              /* 符号名称 */
    SymbolType symbol_type;  /* 符号类型 */
    DataType data_type;      /* 数据类型（对于变量） */
    union {
        FunctionTypeData function; /* 函数类型数据（对于函数） */
        struct Symbol** members;   /* 成员符号（对于命名空间） */
        int member_count;          /* 成员数量 */
    } data;
} Symbol;

/**
 * 符号表结构
 */
typedef struct SymbolTable {
    Symbol** symbols;        /* 符号数组 */
    int count;               /* 符号数量 */
    int capacity;            /* 容量 */
    struct SymbolTable* parent; /* 父符号表 */
} SymbolTable;

/**
 * 创建符号表
 * 
 * @param parent 父符号表（可为NULL）
 * @return 新创建的符号表
 */
SymbolTable* symbol_table_create(SymbolTable* parent);

/**
 * 销毁符号表
 * 
 * @param table 要销毁的符号表
 */
void symbol_table_destroy(SymbolTable* table);

/**
 * 在符号表中查找符号
 * 
 * @param table 符号表
 * @param name 符号名称
 * @return 找到的符号，未找到返回NULL
 */
Symbol* symbol_table_lookup(SymbolTable* table, const char* name);

/**
 * 向符号表中插入符号
 * 
 * @param table 符号表
 * @param symbol 要插入的符号
 * @return 成功返回1，失败返回0
 */
int symbol_table_insert(SymbolTable* table, Symbol* symbol);

/**
 * 创建变量符号
 * 
 * @param name 变量名
 * @param type 变量类型
 * @return 新创建的符号
 */
Symbol* symbol_create_variable(const char* name, DataType type);

/**
 * 创建函数符号
 * 
 * @param name 函数名
 * @param return_type 返回类型
 * @return 新创建的符号
 */
Symbol* symbol_create_function(const char* name, DataType return_type);

/**
 * 向函数符号添加参数类型
 * 
 * @param symbol 函数符号
 * @param param_type 参数类型
 * @return 成功返回1，失败返回0
 */
int symbol_function_add_parameter(Symbol* symbol, DataType param_type);

/**
 * 进行语义分析
 * 
 * @param ast 语法分析树
 * @return 错误列表，无错误时列表为空
 */
ErrorList* semantic_analyze(AST* ast);

#endif /* QENTL_SEMANTIC_H */ 