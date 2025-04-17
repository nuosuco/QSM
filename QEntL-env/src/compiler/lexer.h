/**
 * QEntL词法分析器头文件
 * 
 * 量子基因编码: QG-COMP-LEXER-HEADER-A1B2
 * 
 * @文件: lexer.h
 * @描述: 词法分析器接口定义，包括Token结构和词法分析器函数
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-15
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 输出的词法单元自动包含量子基因编码和量子纠缠信道
 * - 能根据运行环境自适应调整量子比特处理能力
 */

#ifndef QENTL_LEXER_H
#define QENTL_LEXER_H

#include <stdlib.h>
#include "../quantum_gene.h"

/**
 * 词法单元类型
 */
typedef enum {
    /* 终结符 */
    TOKEN_EOF,        /* 文件结束 */
    
    /* 标识符与字面量 */
    TOKEN_IDENTIFIER, /* 标识符 */
    TOKEN_INTEGER,    /* 整数字面量 */
    TOKEN_FLOAT,      /* 浮点数字面量 */
    TOKEN_STRING,     /* 字符串字面量 */
    
    /* 关键字 */
    TOKEN_QUANTUM,       /* quantum */
    TOKEN_ENTANGLE,      /* entangle */
    TOKEN_SUPERPOSITION, /* superposition */
    TOKEN_FUNCTION,      /* function */
    TOKEN_LET,           /* let */
    TOKEN_IF,            /* if */
    TOKEN_ELSE,          /* else */
    TOKEN_WHILE,         /* while */
    TOKEN_FOR,           /* for */
    TOKEN_RETURN,        /* return */
    TOKEN_TRUE,          /* true */
    TOKEN_FALSE,         /* false */
    TOKEN_NULL,          /* null */
    TOKEN_IMPORT,        /* import */
    TOKEN_EXPORT,        /* export */
    
    /* 运算符 */
    TOKEN_PLUS,          /* + */
    TOKEN_MINUS,         /* - */
    TOKEN_MULTIPLY,      /* * */
    TOKEN_DIVIDE,        /* / */
    TOKEN_EQUAL,         /* = */
    TOKEN_EQUAL_EQUAL,   /* == */
    TOKEN_NOT,           /* ! */
    TOKEN_NOT_EQUAL,     /* != */
    TOKEN_LESS,          /* < */
    TOKEN_LESS_EQUAL,    /* <= */
    TOKEN_GREATER,       /* > */
    TOKEN_GREATER_EQUAL, /* >= */
    TOKEN_AND,           /* && */
    TOKEN_OR,            /* || */
    TOKEN_PIPE,          /* | */
    
    /* 分隔符 */
    TOKEN_LPAREN,        /* ( */
    TOKEN_RPAREN,        /* ) */
    TOKEN_LBRACE,        /* { */
    TOKEN_RBRACE,        /* } */
    TOKEN_LBRACKET,      /* [ */
    TOKEN_RBRACKET,      /* ] */
    TOKEN_SEMICOLON,     /* ; */
    TOKEN_COLON,         /* : */
    TOKEN_COMMA,         /* , */
    TOKEN_DOT,           /* . */
    TOKEN_AT,            /* @ */
    TOKEN_HASH           /* # */
} TokenType;

/**
 * 词法单元结构
 */
typedef struct Token {
    TokenType type;        /* 词法单元类型 */
    char* text;            /* 词法单元文本 */
    size_t line;           /* 行号 */
    size_t column;         /* 列号 */
    QGene* quantum_gene;   /* 量子基因标记 */
} Token;

/**
 * 词法分析器不透明结构
 */
typedef struct Lexer Lexer;

/**
 * 创建一个词法单元
 * 
 * @param type 词法单元类型
 * @param text 词法单元文本
 * @param line 行号
 * @param column 列号
 * @return 词法单元指针，失败返回NULL
 */
Token* token_create(TokenType type, const char* text, size_t line, size_t column);

/**
 * 释放词法单元
 * 
 * @param token 词法单元指针
 */
void token_destroy(Token* token);

/**
 * 为词法单元应用量子基因
 * 
 * @param token 词法单元指针
 * @param gene 量子基因指针
 * @return 成功返回1，失败返回0
 */
int token_apply_quantum_gene(Token* token, QGene* gene);

/**
 * 创建词法分析器
 * 
 * @param source 源代码字符串
 * @return 词法分析器指针，失败返回NULL
 */
Lexer* lexer_create(const char* source);

/**
 * 获取下一个词法单元
 * 
 * @param lexer 词法分析器指针
 * @return 词法单元指针，失败或结束返回NULL
 */
Token* lexer_get_next_token(Lexer* lexer);

/**
 * 释放词法分析器
 * 
 * @param lexer 词法分析器指针
 */
void lexer_destroy(Lexer* lexer);

#endif /* QENTL_LEXER_H */ 