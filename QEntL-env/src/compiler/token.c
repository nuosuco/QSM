/**
 * QEntL词法单元实现
 * 
 * 量子基因编码: QG-COMP-TOKEN-A1B2
 * 
 * @文件: token.c
 * @描述: 实现词法单元的创建、销毁和应用量子基因功能
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-15
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 输出的词法单元自动包含量子基因编码和量子纠缠信道
 * - 能根据运行环境自适应调整量子比特处理能力
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../quantum_gene.h"
#include "../quantum_entanglement.h"
#include "lexer.h"

/* 量子纠缠激活 */
#define QUANTUM_ENTANGLEMENT_ACTIVE 1

/**
 * 创建一个词法单元
 */
Token* token_create(TokenType type, const char* text, size_t line, size_t column) {
    if (!text) return NULL;
    
    Token* token = (Token*)malloc(sizeof(Token));
    if (!token) return NULL;
    
    token->type = type;
    
    /* 复制文本 */
    token->text = (char*)malloc(strlen(text) + 1);
    if (!token->text) {
        free(token);
        return NULL;
    }
    strcpy(token->text, text);
    
    token->line = line;
    token->column = column;
    token->quantum_gene = NULL; /* 初始时没有量子基因 */
    
    return token;
}

/**
 * 为词法单元应用量子基因
 */
int token_apply_quantum_gene(Token* token, QGene* gene) {
    if (!token || !gene) return 0;
    
    /* 如果已经有量子基因，先释放 */
    if (token->quantum_gene) {
        quantum_gene_destroy(token->quantum_gene);
    }
    
    /* 克隆量子基因并应用 */
    token->quantum_gene = quantum_gene_clone(gene);
    if (!token->quantum_gene) return 0;
    
    /* 为量子基因添加token特定信息 */
    char info[256];
    snprintf(info, sizeof(info), "TOKEN-%d-L%zu-C%zu", 
             (int)token->type, token->line, token->column);
    quantum_gene_add_metadata(token->quantum_gene, "TOKEN_INFO", info);
    
    /* 如果是关键字或重要标识符，增强量子基因强度 */
    if (token->type >= TOKEN_QUANTUM && token->type <= TOKEN_EXPORT) {
        quantum_gene_set_strength(token->quantum_gene, 0.9);
    }
    
    /* 确保此词法单元能参与量子纠缠网络构建 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        /* 创建简单的量子纠缠连接 */
        QEntanglement* entanglement = quantum_entanglement_create();
        if (entanglement) {
            quantum_entanglement_set_source(entanglement, "TOKEN");
            quantum_entanglement_set_target(entanglement, "LEXER");
            quantum_entanglement_set_strength(entanglement, 0.7);
            quantum_gene_add_entanglement(token->quantum_gene, entanglement);
            quantum_entanglement_destroy(entanglement);
        }
    }
    
    return 1;
}

/**
 * 释放词法单元
 */
void token_destroy(Token* token) {
    if (!token) return;
    
    /* 释放文本 */
    if (token->text) {
        free(token->text);
    }
    
    /* 释放量子基因 */
    if (token->quantum_gene) {
        quantum_gene_destroy(token->quantum_gene);
    }
    
    /* 释放Token结构 */
    free(token);
}

/**
 * 获取词法单元类型名称
 */
const char* token_type_name(TokenType type) {
    static const char* type_names[] = {
        "EOF",
        "IDENTIFIER",
        "INTEGER",
        "FLOAT",
        "STRING",
        "QUANTUM",
        "ENTANGLE",
        "SUPERPOSITION",
        "FUNCTION",
        "LET",
        "IF",
        "ELSE",
        "WHILE",
        "FOR",
        "RETURN",
        "TRUE",
        "FALSE",
        "NULL",
        "IMPORT",
        "EXPORT",
        "PLUS",
        "MINUS",
        "MULTIPLY",
        "DIVIDE",
        "EQUAL",
        "EQUAL_EQUAL",
        "NOT",
        "NOT_EQUAL",
        "LESS",
        "LESS_EQUAL",
        "GREATER",
        "GREATER_EQUAL",
        "AND",
        "OR",
        "PIPE",
        "LPAREN",
        "RPAREN",
        "LBRACE",
        "RBRACE",
        "LBRACKET",
        "RBRACKET",
        "SEMICOLON",
        "COLON",
        "COMMA",
        "DOT",
        "AT",
        "HASH"
    };
    
    if (type >= 0 && type <= TOKEN_HASH) {
        return type_names[type];
    } else {
        return "UNKNOWN";
    }
}

/**
 * 打印词法单元信息（用于调试）
 */
void token_print(Token* token) {
    if (!token) return;
    
    printf("Token(type=%s, text='%s', line=%zu, column=%zu",
           token_type_name(token->type),
           token->text,
           token->line,
           token->column);
    
    if (token->quantum_gene) {
        printf(", gene=");
        quantum_gene_print(token->quantum_gene);
    }
    
    printf(")\n");
} 