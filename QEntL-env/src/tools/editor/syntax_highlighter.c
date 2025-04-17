/**
 * QEntL编辑器语法高亮组件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月19日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>
#include "syntax_highlighter.h"

// ANSI颜色代码
#define COLOR_RESET     "\x1b[0m"
#define COLOR_KEYWORD   "\x1b[34m"    // 蓝色
#define COLOR_QKEYWORD  "\x1b[36m"    // 青色
#define COLOR_STRING    "\x1b[32m"    // 绿色
#define COLOR_NUMBER    "\x1b[33m"    // 黄色
#define COLOR_COMMENT   "\x1b[90m"    // 灰色
#define COLOR_OPERATOR  "\x1b[35m"    // 紫色
#define COLOR_FUNCTION  "\x1b[92m"    // 亮绿色

// QEntL关键字列表
static const char* keywords[] = {
    "if", "else", "while", "for", "function", "return", "break", 
    "continue", "var", "const", "struct", "enum", "true", "false",
    "null", "import", "export", NULL
};

// QEntL量子关键字列表
static const char* quantum_keywords[] = {
    "quantum", "qstate", "qubit", "qregister", "entangle", "apply", 
    "measure", "collapse", "superposition", "probability", "amplitude",
    "phase", "interference", "coherence", "teleport", NULL
};

// QEntL量子门列表
static const char* quantum_gates[] = {
    "H", "X", "Y", "Z", "S", "T", "CNOT", "CZ", "SWAP", "Toffoli",
    "Rx", "Ry", "Rz", "U1", "U2", "U3", NULL
};

// 检查字符串是否是关键字
static bool is_keyword(const char* word) {
    for (int i = 0; keywords[i] != NULL; i++) {
        if (strcmp(keywords[i], word) == 0) {
            return true;
        }
    }
    return false;
}

// 检查字符串是否是量子关键字
static bool is_quantum_keyword(const char* word) {
    for (int i = 0; quantum_keywords[i] != NULL; i++) {
        if (strcmp(quantum_keywords[i], word) == 0) {
            return true;
        }
    }
    return false;
}

// 检查字符串是否是量子门
static bool is_quantum_gate(const char* word) {
    for (int i = 0; quantum_gates[i] != NULL; i++) {
        if (strcmp(quantum_gates[i], word) == 0) {
            return true;
        }
    }
    return false;
}

// 检查字符是否是标识符的一部分
static bool is_identifier_char(char c) {
    return isalnum(c) || c == '_';
}

// 检查字符是否是运算符
static bool is_operator_char(char c) {
    return strchr("+-*/%=<>!&|^~?:", c) != NULL;
}

// 语法高亮器结构
struct SyntaxHighlighter {
    bool use_colors;                // 是否启用彩色输出
    char token_buffer[256];         // 标记缓冲区
    SyntaxHighlightCallback callback; // 高亮回调函数
    void* callback_data;            // 回调函数用户数据
};

// 创建语法高亮器
SyntaxHighlighter* syntax_highlighter_create(void) {
    SyntaxHighlighter* highlighter = (SyntaxHighlighter*)malloc(sizeof(SyntaxHighlighter));
    if (!highlighter) {
        return NULL;
    }
    
    highlighter->use_colors = true;
    highlighter->token_buffer[0] = '\0';
    highlighter->callback = NULL;
    highlighter->callback_data = NULL;
    
    return highlighter;
}

// 销毁语法高亮器
void syntax_highlighter_destroy(SyntaxHighlighter* highlighter) {
    if (highlighter) {
        free(highlighter);
    }
}

// 设置是否启用彩色输出
void syntax_highlighter_set_use_colors(SyntaxHighlighter* highlighter, bool use_colors) {
    if (highlighter) {
        highlighter->use_colors = use_colors;
    }
}

// 设置高亮回调函数
void syntax_highlighter_set_callback(SyntaxHighlighter* highlighter, 
                                   SyntaxHighlightCallback callback, 
                                   void* user_data) {
    if (highlighter) {
        highlighter->callback = callback;
        highlighter->callback_data = user_data;
    }
}

// 输出高亮标记
static void emit_token(SyntaxHighlighter* highlighter, const char* token, 
                       SyntaxTokenType type) {
    if (!highlighter || !token || token[0] == '\0') {
        return;
    }
    
    if (highlighter->callback) {
        // 使用回调函数
        highlighter->callback(token, type, highlighter->callback_data);
    } else {
        // 直接输出到控制台
        if (highlighter->use_colors) {
            switch (type) {
                case TOKEN_KEYWORD:
                    printf("%s%s%s", COLOR_KEYWORD, token, COLOR_RESET);
                    break;
                case TOKEN_QUANTUM_KEYWORD:
                    printf("%s%s%s", COLOR_QKEYWORD, token, COLOR_RESET);
                    break;
                case TOKEN_STRING:
                    printf("%s%s%s", COLOR_STRING, token, COLOR_RESET);
                    break;
                case TOKEN_NUMBER:
                    printf("%s%s%s", COLOR_NUMBER, token, COLOR_RESET);
                    break;
                case TOKEN_COMMENT:
                    printf("%s%s%s", COLOR_COMMENT, token, COLOR_RESET);
                    break;
                case TOKEN_OPERATOR:
                    printf("%s%s%s", COLOR_OPERATOR, token, COLOR_RESET);
                    break;
                case TOKEN_FUNCTION:
                    printf("%s%s%s", COLOR_FUNCTION, token, COLOR_RESET);
                    break;
                default:
                    printf("%s", token);
                    break;
            }
        } else {
            printf("%s", token);
        }
    }
}

// 处理标识符
static void process_identifier(SyntaxHighlighter* highlighter, const char* identifier) {
    if (is_keyword(identifier)) {
        emit_token(highlighter, identifier, TOKEN_KEYWORD);
    } else if (is_quantum_keyword(identifier)) {
        emit_token(highlighter, identifier, TOKEN_QUANTUM_KEYWORD);
    } else if (is_quantum_gate(identifier)) {
        emit_token(highlighter, identifier, TOKEN_QUANTUM_KEYWORD);
    } else {
        // 检查是否是函数调用
        bool is_function = false;
        const char* p = identifier;
        while (*p) p++; // 移动到字符串末尾
        if (p > identifier) {
            p--; // 回退一个字符
            is_function = (*p == '(');
        }
        
        if (is_function) {
            emit_token(highlighter, identifier, TOKEN_FUNCTION);
        } else {
            emit_token(highlighter, identifier, TOKEN_IDENTIFIER);
        }
    }
}

// 高亮单行文本
void syntax_highlighter_highlight_line(SyntaxHighlighter* highlighter, const char* line) {
    if (!highlighter || !line) {
        return;
    }
    
    const char* p = line;
    int token_len = 0;
    
    while (*p) {
        // 跳过空白字符
        if (isspace(*p)) {
            highlighter->token_buffer[0] = *p;
            highlighter->token_buffer[1] = '\0';
            emit_token(highlighter, highlighter->token_buffer, TOKEN_WHITESPACE);
            p++;
            continue;
        }
        
        // 处理注释
        if (*p == '/' && *(p+1) == '/') {
            // 单行注释
            const char* comment_start = p;
            while (*p) p++; // 移动到行尾
            
            int comment_len = p - comment_start;
            if (comment_len < sizeof(highlighter->token_buffer)) {
                strncpy(highlighter->token_buffer, comment_start, comment_len);
                highlighter->token_buffer[comment_len] = '\0';
                emit_token(highlighter, highlighter->token_buffer, TOKEN_COMMENT);
            }
            continue;
        }
        
        if (*p == '/' && *(p+1) == '*') {
            // 多行注释开始
            const char* comment_start = p;
            p += 2;
            
            // 找到注释结束或行尾
            while (*p && !(*p == '*' && *(p+1) == '/')) p++;
            
            if (*p) {
                p += 2; // 跳过 */
            }
            
            int comment_len = p - comment_start;
            if (comment_len < sizeof(highlighter->token_buffer)) {
                strncpy(highlighter->token_buffer, comment_start, comment_len);
                highlighter->token_buffer[comment_len] = '\0';
                emit_token(highlighter, highlighter->token_buffer, TOKEN_COMMENT);
            }
            continue;
        }
        
        // 处理字符串
        if (*p == '"') {
            const char* str_start = p;
            p++; // 跳过开始引号
            
            // 找到字符串结束或行尾
            while (*p && *p != '"') {
                if (*p == '\\' && *(p+1)) {
                    p += 2; // 跳过转义序列
                } else {
                    p++;
                }
            }
            
            if (*p == '"') {
                p++; // 跳过结束引号
            }
            
            int str_len = p - str_start;
            if (str_len < sizeof(highlighter->token_buffer)) {
                strncpy(highlighter->token_buffer, str_start, str_len);
                highlighter->token_buffer[str_len] = '\0';
                emit_token(highlighter, highlighter->token_buffer, TOKEN_STRING);
            }
            continue;
        }
        
        // 处理字符
        if (*p == '\'') {
            const char* char_start = p;
            p++; // 跳过开始引号
            
            // 处理可能的转义字符
            if (*p == '\\' && *(p+1)) {
                p += 2;
            } else if (*p) {
                p++;
            }
            
            // 查找结束引号
            if (*p == '\'') {
                p++;
            }
            
            int char_len = p - char_start;
            if (char_len < sizeof(highlighter->token_buffer)) {
                strncpy(highlighter->token_buffer, char_start, char_len);
                highlighter->token_buffer[char_len] = '\0';
                emit_token(highlighter, highlighter->token_buffer, TOKEN_STRING);
            }
            continue;
        }
        
        // 处理数字
        if (isdigit(*p) || (*p == '.' && isdigit(*(p+1)))) {
            const char* num_start = p;
            
            // 整数部分
            while (isdigit(*p)) p++;
            
            // 小数部分
            if (*p == '.') {
                p++;
                while (isdigit(*p)) p++;
            }
            
            // 指数部分
            if (*p == 'e' || *p == 'E') {
                p++;
                if (*p == '+' || *p == '-') p++;
                while (isdigit(*p)) p++;
            }
            
            int num_len = p - num_start;
            if (num_len < sizeof(highlighter->token_buffer)) {
                strncpy(highlighter->token_buffer, num_start, num_len);
                highlighter->token_buffer[num_len] = '\0';
                emit_token(highlighter, highlighter->token_buffer, TOKEN_NUMBER);
            }
            continue;
        }
        
        // 处理标识符
        if (isalpha(*p) || *p == '_') {
            const char* id_start = p;
            
            while (is_identifier_char(*p)) p++;
            
            int id_len = p - id_start;
            if (id_len < sizeof(highlighter->token_buffer)) {
                strncpy(highlighter->token_buffer, id_start, id_len);
                highlighter->token_buffer[id_len] = '\0';
                process_identifier(highlighter, highlighter->token_buffer);
            }
            continue;
        }
        
        // 处理运算符
        if (is_operator_char(*p)) {
            const char* op_start = p;
            
            while (is_operator_char(*p)) p++;
            
            int op_len = p - op_start;
            if (op_len < sizeof(highlighter->token_buffer)) {
                strncpy(highlighter->token_buffer, op_start, op_len);
                highlighter->token_buffer[op_len] = '\0';
                emit_token(highlighter, highlighter->token_buffer, TOKEN_OPERATOR);
            }
            continue;
        }
        
        // 处理其他字符
        highlighter->token_buffer[0] = *p;
        highlighter->token_buffer[1] = '\0';
        emit_token(highlighter, highlighter->token_buffer, TOKEN_OTHER);
        p++;
    }
    
    // 添加换行符
    if (highlighter->callback) {
        highlighter->callback("\n", TOKEN_WHITESPACE, highlighter->callback_data);
    } else {
        printf("\n");
    }
}

// 高亮整个文件
void syntax_highlighter_highlight_file(SyntaxHighlighter* highlighter, FILE* file) {
    if (!highlighter || !file) {
        return;
    }
    
    char line[1024];
    while (fgets(line, sizeof(line), file)) {
        // 去掉行尾换行符
        size_t len = strlen(line);
        if (len > 0 && (line[len-1] == '\n' || line[len-1] == '\r')) {
            line[len-1] = '\0';
            if (len > 1 && line[len-2] == '\r') {
                line[len-2] = '\0';
            }
        }
        
        // 高亮该行
        syntax_highlighter_highlight_line(highlighter, line);
    }
}

// 高亮字符串
void syntax_highlighter_highlight_string(SyntaxHighlighter* highlighter, const char* text) {
    if (!highlighter || !text) {
        return;
    }
    
    const char* start = text;
    const char* end = text;
    
    // 逐行处理文本
    while (*end) {
        if (*end == '\n') {
            // 找到行尾，处理这一行
            int line_len = end - start;
            char* line = (char*)malloc(line_len + 1);
            if (line) {
                strncpy(line, start, line_len);
                line[line_len] = '\0';
                syntax_highlighter_highlight_line(highlighter, line);
                free(line);
            }
            
            start = end + 1;
        }
        end++;
    }
    
    // 处理最后一行
    if (start < end) {
        int line_len = end - start;
        char* line = (char*)malloc(line_len + 1);
        if (line) {
            strncpy(line, start, line_len);
            line[line_len] = '\0';
            syntax_highlighter_highlight_line(highlighter, line);
            free(line);
        }
    }
} 