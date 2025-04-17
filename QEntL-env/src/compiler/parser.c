/**
 * QEntL语法分析器实现
 * 
 * 量子基因编码: QG-COMP-PARSER-A1B2
 * 
 * @文件: parser.c
 * @描述: 实现QEntL语法分析功能，将词法单元流转换为抽象语法树(AST)
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-15
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 输出的AST节点自动包含量子基因编码和量子纠缠信道
 * - 能根据运行环境自适应调整量子比特处理能力
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../quantum_gene.h"
#include "../quantum_entanglement.h"
#include "lexer.h"
#include "parser.h"

/* 量子纠缠激活 */
#define QUANTUM_ENTANGLEMENT_ACTIVE 1

/* 语法分析器状态 */
typedef struct Parser {
    Lexer* lexer;          /* 词法分析器 */
    Token* current_token;  /* 当前Token */
    Token* peek_token;     /* 下一个Token */
    QGene* quantum_gene;   /* 量子基因标记 */
} Parser;

/* 前置声明 */
static ASTNode* parse_statement(Parser* parser);
static ASTNode* parse_expression(Parser* parser, int precedence);

/* 运算符优先级 */
typedef enum {
    PREC_LOWEST = 0,
    PREC_ASSIGN,      /* = */
    PREC_OR,          /* || */
    PREC_AND,         /* && */
    PREC_EQUALITY,    /* == != */
    PREC_RELATIONAL,  /* < > <= >= */
    PREC_ADDITIVE,    /* + - */
    PREC_MULTIPLICATIVE, /* * / */
    PREC_PREFIX,      /* -x !x */
    PREC_CALL,        /* func() */
    PREC_MEMBER       /* obj.prop */
} Precedence;

/* 获取运算符优先级 */
static Precedence get_token_precedence(TokenType type) {
    switch (type) {
        case TOKEN_EQUAL:
            return PREC_ASSIGN;
        case TOKEN_OR:
            return PREC_OR;
        case TOKEN_AND:
            return PREC_AND;
        case TOKEN_EQUAL_EQUAL:
        case TOKEN_NOT_EQUAL:
            return PREC_EQUALITY;
        case TOKEN_LESS:
        case TOKEN_LESS_EQUAL:
        case TOKEN_GREATER:
        case TOKEN_GREATER_EQUAL:
            return PREC_RELATIONAL;
        case TOKEN_PLUS:
        case TOKEN_MINUS:
            return PREC_ADDITIVE;
        case TOKEN_MULTIPLY:
        case TOKEN_DIVIDE:
            return PREC_MULTIPLICATIVE;
        case TOKEN_LPAREN:
            return PREC_CALL;
        case TOKEN_DOT:
            return PREC_MEMBER;
        default:
            return PREC_LOWEST;
    }
}

/* 前进到下一个Token */
static void parser_advance_token(Parser* parser) {
    parser->current_token = parser->peek_token;
    parser->peek_token = lexer_get_next_token(parser->lexer);
}

/* 检查当前Token类型 */
static int parser_current_token_is(Parser* parser, TokenType type) {
    return parser->current_token->type == type;
}

/* 检查下一个Token类型 */
static int parser_peek_token_is(Parser* parser, TokenType type) {
    return parser->peek_token->type == type;
}

/* 期望下一个Token为指定类型，如果是则前进并返回1，否则返回0 */
static int parser_expect_peek(Parser* parser, TokenType type) {
    if (parser_peek_token_is(parser, type)) {
        parser_advance_token(parser);
        return 1;
    }
    
    fprintf(stderr, "Error: Expected next token to be %s, got %s instead at line %zu, column %zu\n",
            token_type_name(type),
            token_type_name(parser->peek_token->type),
            parser->peek_token->line,
            parser->peek_token->column);
    return 0;
}

/* 创建AST节点的基础信息 */
static void init_ast_node(ASTNode* node, ASTNodeType type, size_t line, size_t column) {
    node->type = type;
    node->line = line;
    node->column = column;
    node->quantum_gene = NULL;
    node->parent = NULL;
}

/* 为AST节点应用量子基因 */
int ast_node_apply_quantum_gene(ASTNode* node, QGene* gene) {
    if (!node || !gene) return 0;
    
    /* 如果已经有量子基因，先释放 */
    if (node->quantum_gene) {
        quantum_gene_destroy(node->quantum_gene);
    }
    
    /* 克隆量子基因并应用 */
    node->quantum_gene = quantum_gene_clone(gene);
    if (!node->quantum_gene) return 0;
    
    /* 为量子基因添加节点特定信息 */
    char info[256];
    snprintf(info, sizeof(info), "AST-%d-L%zu-C%zu", 
             (int)node->type, node->line, node->column);
    quantum_gene_add_metadata(node->quantum_gene, "AST_INFO", info);
    
    /* 根据节点类型调整量子基因强度 */
    switch (node->type) {
        case NODE_QUANTUM_EXPR:
        case NODE_SUPERPOSITION:
        case NODE_ENTANGLE_STMT:
            /* 量子相关节点具有更强的量子基因 */
            quantum_gene_set_strength(node->quantum_gene, 0.95);
            break;
        case NODE_FUNCTION_DECL:
        case NODE_IMPORT_STMT:
        case NODE_EXPORT_STMT:
            /* 结构相关节点也较为重要 */
            quantum_gene_set_strength(node->quantum_gene, 0.85);
            break;
        default:
            quantum_gene_set_strength(node->quantum_gene, 0.7);
            break;
    }
    
    /* 确保此AST节点能参与量子纠缠网络构建 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        /* 创建简单的量子纠缠连接 */
        QEntanglement* entanglement = quantum_entanglement_create();
        if (entanglement) {
            quantum_entanglement_set_source(entanglement, "AST_NODE");
            quantum_entanglement_set_target(entanglement, "PARSER");
            quantum_entanglement_set_strength(entanglement, 0.75);
            quantum_gene_add_entanglement(node->quantum_gene, entanglement);
            quantum_entanglement_destroy(entanglement);
        }
    }
    
    return 1;
}

/* 解析标识符 */
static ASTNode* parse_identifier(Parser* parser) {
    IdentifierNode* node = (IdentifierNode*)malloc(sizeof(IdentifierNode));
    if (!node) return NULL;
    
    init_ast_node((ASTNode*)node, NODE_IDENTIFIER, 
                  parser->current_token->line, 
                  parser->current_token->column);
    
    /* 复制标识符名称 */
    node->name = strdup(parser->current_token->text);
    if (!node->name) {
        free(node);
        return NULL;
    }
    
    /* 应用量子基因 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        ast_node_apply_quantum_gene((ASTNode*)node, parser->quantum_gene);
    }
    
    return (ASTNode*)node;
}

/* 解析整数字面量 */
static ASTNode* parse_integer_literal(Parser* parser) {
    LiteralNode* node = (LiteralNode*)malloc(sizeof(LiteralNode));
    if (!node) return NULL;
    
    init_ast_node((ASTNode*)node, NODE_LITERAL, 
                  parser->current_token->line, 
                  parser->current_token->column);
    
    node->literal_type = TOKEN_INTEGER;
    node->value.int_value = atoi(parser->current_token->text);
    
    /* 应用量子基因 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        ast_node_apply_quantum_gene((ASTNode*)node, parser->quantum_gene);
    }
    
    return (ASTNode*)node;
}

/* 解析浮点数字面量 */
static ASTNode* parse_float_literal(Parser* parser) {
    LiteralNode* node = (LiteralNode*)malloc(sizeof(LiteralNode));
    if (!node) return NULL;
    
    init_ast_node((ASTNode*)node, NODE_LITERAL, 
                  parser->current_token->line, 
                  parser->current_token->column);
    
    node->literal_type = TOKEN_FLOAT;
    node->value.float_value = atof(parser->current_token->text);
    
    /* 应用量子基因 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        ast_node_apply_quantum_gene((ASTNode*)node, parser->quantum_gene);
    }
    
    return (ASTNode*)node;
}

/* 解析字符串字面量 */
static ASTNode* parse_string_literal(Parser* parser) {
    LiteralNode* node = (LiteralNode*)malloc(sizeof(LiteralNode));
    if (!node) return NULL;
    
    init_ast_node((ASTNode*)node, NODE_LITERAL, 
                  parser->current_token->line, 
                  parser->current_token->column);
    
    node->literal_type = TOKEN_STRING;
    node->value.string_value = strdup(parser->current_token->text);
    if (!node->value.string_value) {
        free(node);
        return NULL;
    }
    
    /* 应用量子基因 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        ast_node_apply_quantum_gene((ASTNode*)node, parser->quantum_gene);
    }
    
    return (ASTNode*)node;
}

/* 解析布尔字面量 */
static ASTNode* parse_boolean_literal(Parser* parser) {
    LiteralNode* node = (LiteralNode*)malloc(sizeof(LiteralNode));
    if (!node) return NULL;
    
    init_ast_node((ASTNode*)node, NODE_LITERAL, 
                  parser->current_token->line, 
                  parser->current_token->column);
    
    node->literal_type = parser->current_token->type; /* TOKEN_TRUE or TOKEN_FALSE */
    node->value.bool_value = (parser->current_token->type == TOKEN_TRUE) ? 1 : 0;
    
    /* 应用量子基因 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        ast_node_apply_quantum_gene((ASTNode*)node, parser->quantum_gene);
    }
    
    return (ASTNode*)node;
}

/* 解析前缀表达式 */
static ASTNode* parse_prefix_expression(Parser* parser) {
    UnaryExprNode* node = (UnaryExprNode*)malloc(sizeof(UnaryExprNode));
    if (!node) return NULL;
    
    init_ast_node((ASTNode*)node, NODE_UNARY_EXPR, 
                  parser->current_token->line, 
                  parser->current_token->column);
    
    node->operator = parser->current_token->type;
    node->prefix = 1;
    
    /* 前进到下一个token */
    parser_advance_token(parser);
    
    /* 解析操作数 */
    node->operand = parse_expression(parser, PREC_PREFIX);
    if (!node->operand) {
        free(node);
        return NULL;
    }
    
    node->operand->parent = (ASTNode*)node;
    
    /* 应用量子基因 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        ast_node_apply_quantum_gene((ASTNode*)node, parser->quantum_gene);
    }
    
    return (ASTNode*)node;
}

/* 解析中缀表达式 */
static ASTNode* parse_infix_expression(Parser* parser, ASTNode* left) {
    BinaryExprNode* node = (BinaryExprNode*)malloc(sizeof(BinaryExprNode));
    if (!node) return NULL;
    
    init_ast_node((ASTNode*)node, NODE_BINARY_EXPR, 
                  parser->current_token->line, 
                  parser->current_token->column);
    
    node->operator = parser->current_token->type;
    node->left = left;
    left->parent = (ASTNode*)node;
    
    /* 获取当前运算符的优先级 */
    Precedence precedence = get_token_precedence(parser->current_token->type);
    
    /* 前进到下一个token */
    parser_advance_token(parser);
    
    /* 解析右操作数 */
    node->right = parse_expression(parser, precedence);
    if (!node->right) {
        ast_node_destroy((ASTNode*)node);
        return NULL;
    }
    
    node->right->parent = (ASTNode*)node;
    
    /* 应用量子基因 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        ast_node_apply_quantum_gene((ASTNode*)node, parser->quantum_gene);
    }
    
    return (ASTNode*)node;
}

/* 解析函数调用参数 */
static ASTNode** parse_call_arguments(Parser* parser, size_t* arg_count) {
    ASTNode** args = NULL;
    *arg_count = 0;
    
    /* 空参数列表 */
    if (parser_peek_token_is(parser, TOKEN_RPAREN)) {
        parser_advance_token(parser);
        return NULL;
    }
    
    /* 前进到第一个参数 */
    parser_advance_token(parser);
    
    /* 分配初始参数数组 */
    args = (ASTNode**)malloc(sizeof(ASTNode*) * 4);
    if (!args) return NULL;
    
    /* 解析第一个参数 */
    args[(*arg_count)++] = parse_expression(parser, PREC_LOWEST);
    
    /* 解析剩余参数 */
    while (parser_peek_token_is(parser, TOKEN_COMMA)) {
        parser_advance_token(parser); /* 消耗逗号 */
        parser_advance_token(parser); /* 移动到下一个参数 */
        
        /* 如果需要，扩展参数数组 */
        if (*arg_count % 4 == 0) {
            ASTNode** new_args = (ASTNode**)realloc(args, sizeof(ASTNode*) * (*arg_count + 4));
            if (!new_args) {
                /* 清理已分配的参数 */
                for (size_t i = 0; i < *arg_count; i++) {
                    ast_node_destroy(args[i]);
                }
                free(args);
                return NULL;
            }
            args = new_args;
        }
        
        /* 添加新参数 */
        args[(*arg_count)++] = parse_expression(parser, PREC_LOWEST);
    }
    
    /* 期望右括号 */
    if (!parser_expect_peek(parser, TOKEN_RPAREN)) {
        /* 清理已分配的参数 */
        for (size_t i = 0; i < *arg_count; i++) {
            ast_node_destroy(args[i]);
        }
        free(args);
        return NULL;
    }
    
    return args;
}

/* 解析函数调用表达式 */
static ASTNode* parse_call_expression(Parser* parser, ASTNode* function) {
    CallExprNode* node = (CallExprNode*)malloc(sizeof(CallExprNode));
    if (!node) return NULL;
    
    init_ast_node((ASTNode*)node, NODE_CALL_EXPR, 
                  parser->current_token->line, 
                  parser->current_token->column);
    
    node->callee = function;
    function->parent = (ASTNode*)node;
    
    /* 解析参数列表 */
    node->args = parse_call_arguments(parser, &node->arg_count);
    
    /* 设置参数父节点 */
    for (size_t i = 0; i < node->arg_count; i++) {
        if (node->args[i]) {
            node->args[i]->parent = (ASTNode*)node;
        }
    }
    
    /* 应用量子基因 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        ast_node_apply_quantum_gene((ASTNode*)node, parser->quantum_gene);
    }
    
    return (ASTNode*)node;
}

/* 解析表达式 */
static ASTNode* parse_expression(Parser* parser, int precedence) {
    /* 定义前缀解析函数指针 */
    ASTNode* (*prefix_parse_fns[TOKEN_HASH + 1])(Parser*) = {0};
    
    /* 设置前缀解析函数 */
    prefix_parse_fns[TOKEN_IDENTIFIER] = parse_identifier;
    prefix_parse_fns[TOKEN_INTEGER] = parse_integer_literal;
    prefix_parse_fns[TOKEN_FLOAT] = parse_float_literal;
    prefix_parse_fns[TOKEN_STRING] = parse_string_literal;
    prefix_parse_fns[TOKEN_TRUE] = parse_boolean_literal;
    prefix_parse_fns[TOKEN_FALSE] = parse_boolean_literal;
    prefix_parse_fns[TOKEN_MINUS] = parse_prefix_expression;
    prefix_parse_fns[TOKEN_NOT] = parse_prefix_expression;
    
    /* 获取前缀解析函数 */
    ASTNode* (*prefix_fn)(Parser*) = prefix_parse_fns[parser->current_token->type];
    if (!prefix_fn) {
        fprintf(stderr, "Error: No prefix parse function for %s at line %zu, column %zu\n",
                token_type_name(parser->current_token->type),
                parser->current_token->line,
                parser->current_token->column);
        return NULL;
    }
    
    /* 解析左操作数 */
    ASTNode* left_expr = prefix_fn(parser);
    if (!left_expr) return NULL;
    
    /* 处理中缀表达式和函数调用 */
    while (!parser_peek_token_is(parser, TOKEN_SEMICOLON) && 
           precedence < get_token_precedence(parser->peek_token->type)) {
        
        /* 前进到下一个token */
        parser_advance_token(parser);
        
        /* 处理函数调用 */
        if (parser_current_token_is(parser, TOKEN_LPAREN)) {
            left_expr = parse_call_expression(parser, left_expr);
        }
        /* 处理中缀表达式 */
        else {
            left_expr = parse_infix_expression(parser, left_expr);
        }
        
        if (!left_expr) return NULL;
    }
    
    return left_expr;
}

/* 解析表达式语句 */
static ASTNode* parse_expression_statement(Parser* parser) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    init_ast_node(node, NODE_EXPR_STMT, 
                  parser->current_token->line, 
                  parser->current_token->column);
    
    /* 解析表达式 */
    ASTNode* expr = parse_expression(parser, PREC_LOWEST);
    if (!expr) {
        free(node);
        return NULL;
    }
    
    expr->parent = node;
    
    /* 可选的分号 */
    if (parser_peek_token_is(parser, TOKEN_SEMICOLON)) {
        parser_advance_token(parser);
    }
    
    /* 应用量子基因 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        ast_node_apply_quantum_gene(node, parser->quantum_gene);
    }
    
    return node;
}

/* 解析语句 */
static ASTNode* parse_statement(Parser* parser) {
    switch (parser->current_token->type) {
        case TOKEN_LET:
            /* 这里应该解析变量声明语句 */
            return NULL; /* 暂未实现 */
        case TOKEN_FUNCTION:
            /* 这里应该解析函数声明语句 */
            return NULL; /* 暂未实现 */
        case TOKEN_IMPORT:
            /* 这里应该解析导入语句 */
            return NULL; /* 暂未实现 */
        case TOKEN_EXPORT:
            /* 这里应该解析导出语句 */
            return NULL; /* 暂未实现 */
        case TOKEN_IF:
            /* 这里应该解析if语句 */
            return NULL; /* 暂未实现 */
        case TOKEN_WHILE:
            /* 这里应该解析while语句 */
            return NULL; /* 暂未实现 */
        case TOKEN_FOR:
            /* 这里应该解析for语句 */
            return NULL; /* 暂未实现 */
        case TOKEN_RETURN:
            /* 这里应该解析return语句 */
            return NULL; /* 暂未实现 */
        case TOKEN_ENTANGLE:
            /* 这里应该解析entangle语句 */
            return NULL; /* 暂未实现 */
        default:
            /* 默认解析表达式语句 */
            return parse_expression_statement(parser);
    }
}

/* 解析程序 */
ASTNode* parser_parse_program(Parser* parser) {
    /* 分配程序节点 */
    ASTNode* program = (ASTNode*)malloc(sizeof(ASTNode));
    if (!program) return NULL;
    
    init_ast_node(program, NODE_PROGRAM, 0, 0);
    
    /* 应用量子基因 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        ast_node_apply_quantum_gene(program, parser->quantum_gene);
    }
    
    /* 解析语句直到文件结束 */
    while (parser->current_token->type != TOKEN_EOF) {
        ASTNode* stmt = parse_statement(parser);
        if (stmt) {
            stmt->parent = program;
        }
        
        /* 前进到下一个token */
        parser_advance_token(parser);
    }
    
    return program;
}

/* 创建语法分析器 */
Parser* parser_create(Lexer* lexer) {
    if (!lexer) return NULL;
    
    Parser* parser = (Parser*)malloc(sizeof(Parser));
    if (!parser) return NULL;
    
    parser->lexer = lexer;
    parser->current_token = lexer_get_next_token(lexer);
    parser->peek_token = lexer_get_next_token(lexer);
    
    /* 创建量子基因标记 */
    parser->quantum_gene = quantum_gene_create("PARSER-MODULE", "A1B2");
    
    return parser;
}

/* 释放语法分析器 */
void parser_destroy(Parser* parser) {
    if (!parser) return;
    
    /* 释放量子基因 */
    if (parser->quantum_gene) {
        quantum_gene_destroy(parser->quantum_gene);
    }
    
    /* 释放Token */
    if (parser->current_token) {
        token_destroy(parser->current_token);
    }
    
    if (parser->peek_token) {
        token_destroy(parser->peek_token);
    }
    
    /* 不需要释放lexer，由调用者负责 */
    
    /* 释放Parser结构 */
    free(parser);
}

/* 释放AST节点 */
void ast_node_destroy(ASTNode* node) {
    if (!node) return;
    
    /* 根据节点类型释放特定资源 */
    switch (node->type) {
        case NODE_LITERAL: {
            LiteralNode* literal = (LiteralNode*)node;
            if (literal->literal_type == TOKEN_STRING && literal->value.string_value) {
                free(literal->value.string_value);
            }
            break;
        }
        case NODE_IDENTIFIER: {
            IdentifierNode* identifier = (IdentifierNode*)node;
            if (identifier->name) {
                free(identifier->name);
            }
            break;
        }
        case NODE_BINARY_EXPR: {
            BinaryExprNode* binary = (BinaryExprNode*)node;
            if (binary->left) ast_node_destroy(binary->left);
            if (binary->right) ast_node_destroy(binary->right);
            break;
        }
        case NODE_UNARY_EXPR: {
            UnaryExprNode* unary = (UnaryExprNode*)node;
            if (unary->operand) ast_node_destroy(unary->operand);
            break;
        }
        case NODE_CALL_EXPR: {
            CallExprNode* call = (CallExprNode*)node;
            if (call->callee) ast_node_destroy(call->callee);
            for (size_t i = 0; i < call->arg_count; i++) {
                if (call->args[i]) ast_node_destroy(call->args[i]);
            }
            if (call->args) free(call->args);
            break;
        }
        /* 其他节点类型的释放... */
        default:
            break;
    }
    
    /* 释放量子基因 */
    if (node->quantum_gene) {
        quantum_gene_destroy(node->quantum_gene);
    }
    
    /* 释放节点本身 */
    free(node);
} 