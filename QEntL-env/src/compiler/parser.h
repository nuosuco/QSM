/**
 * QEntL语法分析器头文件
 * 
 * 量子基因编码: QG-COMP-PARSER-HEADER-A1B2
 * 
 * @文件: parser.h
 * @描述: 语法分析器接口定义，包括AST节点结构和解析器函数
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-15
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 输出的AST节点自动包含量子基因编码和量子纠缠信道
 * - 能根据运行环境自适应调整量子比特处理能力
 */

#ifndef QENTL_PARSER_H
#define QENTL_PARSER_H

#include "lexer.h"
#include "../quantum_gene.h"

/**
 * AST节点类型
 */
typedef enum {
    /* 表达式节点 */
    NODE_LITERAL,         /* 字面量 */
    NODE_IDENTIFIER,      /* 标识符 */
    NODE_BINARY_EXPR,     /* 二元表达式 */
    NODE_UNARY_EXPR,      /* 一元表达式 */
    NODE_CALL_EXPR,       /* 函数调用 */
    NODE_MEMBER_EXPR,     /* 成员访问 */
    NODE_ARRAY_EXPR,      /* 数组字面量 */
    NODE_OBJECT_EXPR,     /* 对象字面量 */
    NODE_QUANTUM_EXPR,    /* 量子表达式 */
    NODE_SUPERPOSITION,   /* 量子叠加态 */
    
    /* 语句节点 */
    NODE_EXPR_STMT,       /* 表达式语句 */
    NODE_VAR_DECL,        /* 变量声明 */
    NODE_BLOCK,           /* 块语句 */
    NODE_IF_STMT,         /* if语句 */
    NODE_WHILE_STMT,      /* while语句 */
    NODE_FOR_STMT,        /* for语句 */
    NODE_RETURN_STMT,     /* return语句 */
    NODE_FUNCTION_DECL,   /* 函数声明 */
    NODE_IMPORT_STMT,     /* import语句 */
    NODE_EXPORT_STMT,     /* export语句 */
    NODE_ENTANGLE_STMT,   /* entangle语句 */
    
    /* 顶层节点 */
    NODE_PROGRAM          /* 程序节点 */
} ASTNodeType;

/**
 * AST节点基本结构
 */
typedef struct ASTNode {
    ASTNodeType type;         /* 节点类型 */
    size_t line;              /* 源代码行号 */
    size_t column;            /* 源代码列号 */
    QGene* quantum_gene;      /* 量子基因标记 */
    struct ASTNode* parent;   /* 父节点 */
} ASTNode;

/**
 * 字面量节点
 */
typedef struct {
    ASTNode base;             /* 基本节点信息 */
    TokenType literal_type;   /* 字面量类型 */
    union {
        int int_value;        /* 整数值 */
        double float_value;   /* 浮点数值 */
        char* string_value;   /* 字符串值 */
        int bool_value;       /* 布尔值 */
    } value;                  /* 字面量值 */
} LiteralNode;

/**
 * 标识符节点
 */
typedef struct {
    ASTNode base;             /* 基本节点信息 */
    char* name;               /* 标识符名称 */
} IdentifierNode;

/**
 * 二元表达式节点
 */
typedef struct {
    ASTNode base;             /* 基本节点信息 */
    TokenType operator;       /* 运算符 */
    struct ASTNode* left;     /* 左操作数 */
    struct ASTNode* right;    /* 右操作数 */
} BinaryExprNode;

/**
 * 一元表达式节点
 */
typedef struct {
    ASTNode base;             /* 基本节点信息 */
    TokenType operator;       /* 运算符 */
    int prefix;               /* 是否为前缀运算符 */
    struct ASTNode* operand;  /* 操作数 */
} UnaryExprNode;

/**
 * 函数调用节点
 */
typedef struct {
    ASTNode base;             /* 基本节点信息 */
    struct ASTNode* callee;   /* 被调用对象 */
    struct ASTNode** args;    /* 参数列表 */
    size_t arg_count;         /* 参数数量 */
} CallExprNode;

/**
 * 块语句节点
 */
typedef struct {
    ASTNode base;             /* 基本节点信息 */
    struct ASTNode** statements; /* 语句列表 */
    size_t stmt_count;        /* 语句数量 */
} BlockNode;

/**
 * 量子叠加态节点
 */
typedef struct {
    ASTNode base;                 /* 基本节点信息 */
    struct ASTNode** states;      /* 状态列表 */
    double* probabilities;        /* 概率列表 */
    size_t state_count;           /* 状态数量 */
} SuperpositionNode;

/**
 * 量子纠缠声明节点
 */
typedef struct {
    ASTNode base;                 /* 基本节点信息 */
    struct ASTNode* source;       /* 源节点 */
    struct ASTNode* target;       /* 目标节点 */
    struct ASTNode* properties;   /* 纠缠属性 */
} EntangleStmtNode;

/**
 * 语法分析器不透明结构
 */
typedef struct Parser Parser;

/**
 * 创建语法分析器
 * 
 * @param lexer 词法分析器指针
 * @return 语法分析器指针，失败返回NULL
 */
Parser* parser_create(Lexer* lexer);

/**
 * 解析完整程序
 * 
 * @param parser 语法分析器指针
 * @return 程序AST根节点，失败返回NULL
 */
ASTNode* parser_parse_program(Parser* parser);

/**
 * 释放AST节点及其子节点
 * 
 * @param node AST节点指针
 */
void ast_node_destroy(ASTNode* node);

/**
 * 释放语法分析器
 * 
 * @param parser 语法分析器指针
 */
void parser_destroy(Parser* parser);

/**
 * 为AST节点应用量子基因
 * 
 * @param node AST节点指针
 * @param gene 量子基因指针
 * @return 成功返回1，失败返回0
 */
int ast_node_apply_quantum_gene(ASTNode* node, QGene* gene);

/**
 * 打印AST节点信息（用于调试）
 * 
 * @param node AST节点指针
 * @param indent 缩进级别
 */
void ast_node_print(ASTNode* node, int indent);

#endif /* QENTL_PARSER_H */ 