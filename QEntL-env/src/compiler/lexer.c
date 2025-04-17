/**
 * QEntL词法分析器实现
 * 
 * 量子基因编码: QG-COMP-LEXER-A1B2
 * 
 * @文件: lexer.c
 * @描述: 将QEntL源代码文本分解为词法单元(tokens)，是编译过程的第一阶段
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
#include <ctype.h>
#include "../quantum_gene.h"
#include "../quantum_entanglement.h"
#include "lexer.h"

/* 量子纠缠激活 */
#define QUANTUM_ENTANGLEMENT_ACTIVE 1

/* 词法分析器状态 */
typedef struct {
    const char* source;       /* 输入源代码 */
    size_t source_length;     /* 源代码长度 */
    size_t current_pos;       /* 当前位置 */
    size_t line;              /* 当前行号 */
    size_t column;            /* 当前列号 */
    char current_char;        /* 当前字符 */
    QGene* quantum_gene;      /* 量子基因标记 */
} LexerState;

/* 创建新的词法分析器状态 */
static LexerState* lexer_state_create(const char* source) {
    if (!source) return NULL;
    
    LexerState* state = (LexerState*)malloc(sizeof(LexerState));
    if (!state) return NULL;
    
    state->source = source;
    state->source_length = strlen(source);
    state->current_pos = 0;
    state->line = 1;
    state->column = 1;
    state->current_char = (state->source_length > 0) ? state->source[0] : '\0';
    
    /* 创建量子基因标记 */
    state->quantum_gene = quantum_gene_create("LEXER-MODULE", "A1B2");
    
    return state;
}

/* 释放词法分析器状态 */
static void lexer_state_destroy(LexerState* state) {
    if (!state) return;
    
    if (state->quantum_gene) {
        quantum_gene_destroy(state->quantum_gene);
    }
    
    free(state);
}

/* 前进到下一个字符 */
static void lexer_advance(LexerState* state) {
    if (!state || state->current_pos >= state->source_length) return;
    
    if (state->current_char == '\n') {
        state->line++;
        state->column = 1;
    } else {
        state->column++;
    }
    
    state->current_pos++;
    state->current_char = (state->current_pos < state->source_length) 
                         ? state->source[state->current_pos] 
                         : '\0';
}

/* 查看下一个字符，但不前进 */
static char lexer_peek(LexerState* state) {
    if (!state || state->current_pos + 1 >= state->source_length) return '\0';
    return state->source[state->current_pos + 1];
}

/* 跳过空白字符 */
static void lexer_skip_whitespace(LexerState* state) {
    if (!state) return;
    
    while (state->current_char != '\0' && isspace(state->current_char)) {
        lexer_advance(state);
    }
}

/* 跳过注释 */
static void lexer_skip_comment(LexerState* state) {
    if (!state) return;
    
    // 跳过单行注释 "//"
    if (state->current_char == '/' && lexer_peek(state) == '/') {
        while (state->current_char != '\0' && state->current_char != '\n') {
            lexer_advance(state);
        }
    }
    // 跳过多行注释 "/* ... */"
    else if (state->current_char == '/' && lexer_peek(state) == '*') {
        lexer_advance(state); // 跳过 '/'
        lexer_advance(state); // 跳过 '*'
        
        while (state->current_char != '\0') {
            if (state->current_char == '*' && lexer_peek(state) == '/') {
                lexer_advance(state); // 跳过 '*'
                lexer_advance(state); // 跳过 '/'
                break;
            }
            lexer_advance(state);
        }
    }
}

/* 解析标识符或关键字 */
static Token* lexer_parse_identifier(LexerState* state) {
    if (!state) return NULL;
    
    size_t start_pos = state->current_pos;
    size_t start_line = state->line;
    size_t start_column = state->column;
    
    // 读取标识符
    while (state->current_char != '\0' && 
           (isalnum(state->current_char) || state->current_char == '_')) {
        lexer_advance(state);
    }
    
    // 提取标识符文本
    size_t length = state->current_pos - start_pos;
    char* text = (char*)malloc(length + 1);
    if (!text) return NULL;
    
    strncpy(text, state->source + start_pos, length);
    text[length] = '\0';
    
    // 判断是否为关键字
    TokenType type = TOKEN_IDENTIFIER;
    if (strcmp(text, "quantum") == 0) type = TOKEN_QUANTUM;
    else if (strcmp(text, "entangle") == 0) type = TOKEN_ENTANGLE;
    else if (strcmp(text, "superposition") == 0) type = TOKEN_SUPERPOSITION;
    else if (strcmp(text, "function") == 0) type = TOKEN_FUNCTION;
    else if (strcmp(text, "let") == 0) type = TOKEN_LET;
    else if (strcmp(text, "if") == 0) type = TOKEN_IF;
    else if (strcmp(text, "else") == 0) type = TOKEN_ELSE;
    else if (strcmp(text, "while") == 0) type = TOKEN_WHILE;
    else if (strcmp(text, "for") == 0) type = TOKEN_FOR;
    else if (strcmp(text, "return") == 0) type = TOKEN_RETURN;
    else if (strcmp(text, "true") == 0) type = TOKEN_TRUE;
    else if (strcmp(text, "false") == 0) type = TOKEN_FALSE;
    else if (strcmp(text, "null") == 0) type = TOKEN_NULL;
    else if (strcmp(text, "import") == 0) type = TOKEN_IMPORT;
    else if (strcmp(text, "export") == 0) type = TOKEN_EXPORT;
    
    // 创建词法单元并应用量子基因编码
    Token* token = token_create(type, text, start_line, start_column);
    free(text); // token_create已复制文本
    
    // 应用量子基因
    if (token && QUANTUM_ENTANGLEMENT_ACTIVE) {
        token_apply_quantum_gene(token, state->quantum_gene);
    }
    
    return token;
}

/* 解析数字（整数或浮点数） */
static Token* lexer_parse_number(LexerState* state) {
    if (!state) return NULL;
    
    size_t start_pos = state->current_pos;
    size_t start_line = state->line;
    size_t start_column = state->column;
    int is_float = 0;
    
    // 读取数字
    while (state->current_char != '\0' && isdigit(state->current_char)) {
        lexer_advance(state);
    }
    
    // 检查小数点
    if (state->current_char == '.') {
        is_float = 1;
        lexer_advance(state);
        
        // 读取小数部分
        while (state->current_char != '\0' && isdigit(state->current_char)) {
            lexer_advance(state);
        }
    }
    
    // 提取数字文本
    size_t length = state->current_pos - start_pos;
    char* text = (char*)malloc(length + 1);
    if (!text) return NULL;
    
    strncpy(text, state->source + start_pos, length);
    text[length] = '\0';
    
    // 创建词法单元
    TokenType type = is_float ? TOKEN_FLOAT : TOKEN_INTEGER;
    Token* token = token_create(type, text, start_line, start_column);
    free(text); // token_create已复制文本
    
    // 应用量子基因
    if (token && QUANTUM_ENTANGLEMENT_ACTIVE) {
        token_apply_quantum_gene(token, state->quantum_gene);
    }
    
    return token;
}

/* 解析字符串 */
static Token* lexer_parse_string(LexerState* state) {
    if (!state) return NULL;
    
    size_t start_line = state->line;
    size_t start_column = state->column;
    
    // 跳过开始的引号
    lexer_advance(state);
    
    size_t start_pos = state->current_pos;
    
    // 读取字符串内容
    while (state->current_char != '\0' && state->current_char != '"') {
        // 处理转义字符
        if (state->current_char == '\\') {
            lexer_advance(state);
        }
        lexer_advance(state);
    }
    
    // 提取字符串文本
    size_t length = state->current_pos - start_pos;
    char* text = (char*)malloc(length + 1);
    if (!text) return NULL;
    
    strncpy(text, state->source + start_pos, length);
    text[length] = '\0';
    
    // 跳过结束的引号
    if (state->current_char == '"') {
        lexer_advance(state);
    } else {
        // 未闭合的字符串
        fprintf(stderr, "Error: Unterminated string at line %zu, column %zu\n", 
                start_line, start_column);
    }
    
    // 创建词法单元
    Token* token = token_create(TOKEN_STRING, text, start_line, start_column);
    free(text); // token_create已复制文本
    
    // 应用量子基因
    if (token && QUANTUM_ENTANGLEMENT_ACTIVE) {
        token_apply_quantum_gene(token, state->quantum_gene);
    }
    
    return token;
}

/* 获取下一个词法单元 */
Token* lexer_get_next_token(Lexer* lexer) {
    LexerState* state = (LexerState*)lexer;
    if (!state) return NULL;
    
    // 跳过空白字符和注释
    while (state->current_char != '\0') {
        if (isspace(state->current_char)) {
            lexer_skip_whitespace(state);
            continue;
        }
        
        if (state->current_char == '/' && 
            (lexer_peek(state) == '/' || lexer_peek(state) == '*')) {
            lexer_skip_comment(state);
            continue;
        }
        
        break;
    }
    
    // 源代码结束
    if (state->current_char == '\0') {
        Token* token = token_create(TOKEN_EOF, "", state->line, state->column);
        if (token && QUANTUM_ENTANGLEMENT_ACTIVE) {
            token_apply_quantum_gene(token, state->quantum_gene);
        }
        return token;
    }
    
    // 保存当前位置信息
    size_t current_line = state->line;
    size_t current_column = state->column;
    char current_char = state->current_char;
    
    // 解析标识符或关键字
    if (isalpha(current_char) || current_char == '_') {
        return lexer_parse_identifier(state);
    }
    
    // 解析数字
    if (isdigit(current_char)) {
        return lexer_parse_number(state);
    }
    
    // 解析字符串
    if (current_char == '"') {
        return lexer_parse_string(state);
    }
    
    // 解析运算符和其他符号
    Token* token = NULL;
    switch (current_char) {
        case '+':
            lexer_advance(state);
            token = token_create(TOKEN_PLUS, "+", current_line, current_column);
            break;
        case '-':
            lexer_advance(state);
            token = token_create(TOKEN_MINUS, "-", current_line, current_column);
            break;
        case '*':
            lexer_advance(state);
            token = token_create(TOKEN_MULTIPLY, "*", current_line, current_column);
            break;
        case '/':
            lexer_advance(state);
            token = token_create(TOKEN_DIVIDE, "/", current_line, current_column);
            break;
        case '=':
            lexer_advance(state);
            if (state->current_char == '=') {
                lexer_advance(state);
                token = token_create(TOKEN_EQUAL_EQUAL, "==", current_line, current_column);
            } else {
                token = token_create(TOKEN_EQUAL, "=", current_line, current_column);
            }
            break;
        case '!':
            lexer_advance(state);
            if (state->current_char == '=') {
                lexer_advance(state);
                token = token_create(TOKEN_NOT_EQUAL, "!=", current_line, current_column);
            } else {
                token = token_create(TOKEN_NOT, "!", current_line, current_column);
            }
            break;
        case '<':
            lexer_advance(state);
            if (state->current_char == '=') {
                lexer_advance(state);
                token = token_create(TOKEN_LESS_EQUAL, "<=", current_line, current_column);
            } else {
                token = token_create(TOKEN_LESS, "<", current_line, current_column);
            }
            break;
        case '>':
            lexer_advance(state);
            if (state->current_char == '=') {
                lexer_advance(state);
                token = token_create(TOKEN_GREATER_EQUAL, ">=", current_line, current_column);
            } else {
                token = token_create(TOKEN_GREATER, ">", current_line, current_column);
            }
            break;
        case '&':
            lexer_advance(state);
            if (state->current_char == '&') {
                lexer_advance(state);
                token = token_create(TOKEN_AND, "&&", current_line, current_column);
            }
            break;
        case '|':
            lexer_advance(state);
            if (state->current_char == '|') {
                lexer_advance(state);
                token = token_create(TOKEN_OR, "||", current_line, current_column);
            } else {
                token = token_create(TOKEN_PIPE, "|", current_line, current_column);
            }
            break;
        case '(':
            lexer_advance(state);
            token = token_create(TOKEN_LPAREN, "(", current_line, current_column);
            break;
        case ')':
            lexer_advance(state);
            token = token_create(TOKEN_RPAREN, ")", current_line, current_column);
            break;
        case '{':
            lexer_advance(state);
            token = token_create(TOKEN_LBRACE, "{", current_line, current_column);
            break;
        case '}':
            lexer_advance(state);
            token = token_create(TOKEN_RBRACE, "}", current_line, current_column);
            break;
        case '[':
            lexer_advance(state);
            token = token_create(TOKEN_LBRACKET, "[", current_line, current_column);
            break;
        case ']':
            lexer_advance(state);
            token = token_create(TOKEN_RBRACKET, "]", current_line, current_column);
            break;
        case ';':
            lexer_advance(state);
            token = token_create(TOKEN_SEMICOLON, ";", current_line, current_column);
            break;
        case ':':
            lexer_advance(state);
            token = token_create(TOKEN_COLON, ":", current_line, current_column);
            break;
        case ',':
            lexer_advance(state);
            token = token_create(TOKEN_COMMA, ",", current_line, current_column);
            break;
        case '.':
            lexer_advance(state);
            token = token_create(TOKEN_DOT, ".", current_line, current_column);
            break;
        case '@':
            lexer_advance(state);
            token = token_create(TOKEN_AT, "@", current_line, current_column);
            break;
        case '#':
            lexer_advance(state);
            token = token_create(TOKEN_HASH, "#", current_line, current_column);
            break;
        default:
            // 未知字符
            fprintf(stderr, "Error: Unknown character '%c' at line %zu, column %zu\n", 
                    current_char, current_line, current_column);
            lexer_advance(state);
            return lexer_get_next_token(lexer); // 尝试下一个字符
    }
    
    // 应用量子基因
    if (token && QUANTUM_ENTANGLEMENT_ACTIVE) {
        token_apply_quantum_gene(token, state->quantum_gene);
    }
    
    return token;
}

/* 创建词法分析器 */
Lexer* lexer_create(const char* source) {
    return (Lexer*)lexer_state_create(source);
}

/* 释放词法分析器 */
void lexer_destroy(Lexer* lexer) {
    lexer_state_destroy((LexerState*)lexer);
} 