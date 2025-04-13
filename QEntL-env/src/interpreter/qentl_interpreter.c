/**
 * QEntL解释器主实现
 * 
 * 这是QEntL语言解释器的核心实现，负责解析和执行QEntL代码。
 * 不依赖任何第三方库，纯C实现以保证最大兼容性和性能。
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* 版本信息 */
#define QENTL_VERSION_MAJOR 0
#define QENTL_VERSION_MINOR 1
#define QENTL_VERSION_PATCH 0

/* 词法标记类型 */
typedef enum {
    TOKEN_EOF = 0,
    TOKEN_IDENTIFIER,
    TOKEN_NUMBER,
    TOKEN_STRING,
    TOKEN_QUANTUM,
    TOKEN_ENTANGLE,
    TOKEN_FUNCTION,
    TOKEN_ROUTE,
    TOKEN_IMPORTS,
    TOKEN_CONSTANTS,
    TOKEN_INITIALIZATION,
    TOKEN_ENTRYPOINT,
    TOKEN_LPAREN,
    TOKEN_RPAREN,
    TOKEN_LBRACE,
    TOKEN_RBRACE,
    TOKEN_LBRACKET,
    TOKEN_RBRACKET,
    TOKEN_COMMA,
    TOKEN_COLON,
    TOKEN_SEMICOLON,
    TOKEN_DOT,
    TOKEN_ARROW,
    TOKEN_PLUS,
    TOKEN_MINUS,
    TOKEN_STAR,
    TOKEN_SLASH,
    TOKEN_PERCENT,
    TOKEN_EQUAL,
    TOKEN_EQUAL_EQUAL,
    TOKEN_BANG,
    TOKEN_BANG_EQUAL,
    TOKEN_LESS,
    TOKEN_LESS_EQUAL,
    TOKEN_GREATER,
    TOKEN_GREATER_EQUAL,
    TOKEN_AND,
    TOKEN_OR,
    TOKEN_IF,
    TOKEN_ELSE,
    TOKEN_FOR,
    TOKEN_WHILE,
    TOKEN_RETURN,
    TOKEN_TRUE,
    TOKEN_FALSE,
    TOKEN_NIL
} TokenType;

/* 词法标记结构 */
typedef struct {
    TokenType type;
    const char* start;
    int length;
    int line;
} Token;

/* 解析器状态 */
typedef struct {
    const char* source;
    const char* current;
    int line;
    Token current_token;
    Token previous_token;
    int had_error;
    int panic_mode;
} Parser;

/* 初始化解析器 */
void init_parser(Parser* parser, const char* source) {
    parser->source = source;
    parser->current = source;
    parser->line = 1;
    parser->had_error = 0;
    parser->panic_mode = 0;
}

/* 检查当前字符 */
static int is_at_end(Parser* parser) {
    return *parser->current == '\0';
}

/* 获取当前字符并前进 */
static char advance(Parser* parser) {
    return *parser->current++;
}

/* 查看当前字符但不前进 */
static char peek(Parser* parser) {
    return *parser->current;
}

/* 查看下一个字符 */
static char peek_next(Parser* parser) {
    if (is_at_end(parser)) return '\0';
    return parser->current[1];
}

/* 检查并匹配字符 */
static int match(Parser* parser, char expected) {
    if (is_at_end(parser)) return 0;
    if (*parser->current != expected) return 0;
    parser->current++;
    return 1;
}

/* 创建一个标记 */
static Token make_token(Parser* parser, TokenType type) {
    Token token;
    token.type = type;
    token.start = parser->current;
    token.length = (int)(parser->current - token.start);
    token.line = parser->line;
    return token;
}

/* 创建一个错误标记 */
static Token error_token(Parser* parser, const char* message) {
    Token token;
    token.type = TOKEN_EOF;
    token.start = message;
    token.length = (int)strlen(message);
    token.line = parser->line;
    return token;
}

/* 跳过空白字符和注释 */
static void skip_whitespace(Parser* parser) {
    for (;;) {
        char c = peek(parser);
        switch (c) {
            case ' ':
            case '\r':
            case '\t':
                advance(parser);
                break;
            case '\n':
                parser->line++;
                advance(parser);
                break;
            case '/':
                if (peek_next(parser) == '/') {
                    // 单行注释
                    while (peek(parser) != '\n' && !is_at_end(parser))
                        advance(parser);
                } else if (peek_next(parser) == '*') {
                    // 多行注释
                    advance(parser); // 跳过 '/'
                    advance(parser); // 跳过 '*'
                    
                    while (!(peek(parser) == '*' && peek_next(parser) == '/') && !is_at_end(parser)) {
                        if (peek(parser) == '\n') parser->line++;
                        advance(parser);
                    }
                    
                    if (!is_at_end(parser)) {
                        advance(parser); // 跳过 '*'
                        advance(parser); // 跳过 '/'
                    }
                } else {
                    return;
                }
                break;
            default:
                return;
        }
    }
}

/* 判断是否为数字 */
static int is_digit(char c) {
    return c >= '0' && c <= '9';
}

/* 判断是否为字母或下划线 */
static int is_alpha(char c) {
    return (c >= 'a' && c <= 'z') ||
           (c >= 'A' && c <= 'Z') ||
           c == '_';
}

/* 判断是否为字母数字或下划线 */
static int is_alphanumeric(char c) {
    return is_alpha(c) || is_digit(c);
}

/* 检查关键字 */
static TokenType check_keyword(Parser* parser, int start, int length, const char* rest, TokenType type) {
    if (parser->current - parser->previous_token.start == start + length &&
        memcmp(parser->previous_token.start + start, rest, length) == 0) {
        return type;
    }
    
    return TOKEN_IDENTIFIER;
}

/* 标识符类型判定 */
static TokenType identifier_type(Parser* parser) {
    switch (parser->previous_token.start[0]) {
        case 'a': return check_keyword(parser, 1, 2, "nd", TOKEN_AND);
        case 'e': 
            if (parser->current - parser->previous_token.start > 1) {
                switch (parser->previous_token.start[1]) {
                    case 'l': return check_keyword(parser, 2, 2, "se", TOKEN_ELSE);
                    case 'n': 
                        if (parser->current - parser->previous_token.start > 7) {
                            return check_keyword(parser, 2, 9, "trypoint", TOKEN_ENTRYPOINT);
                        }
                        if (parser->current - parser->previous_token.start > 6) {
                            return check_keyword(parser, 2, 6, "tangle", TOKEN_ENTANGLE);
                        }
                }
            }
            break;
        case 'f': 
            if (parser->current - parser->previous_token.start > 1) {
                switch (parser->previous_token.start[1]) {
                    case 'a': return check_keyword(parser, 2, 3, "lse", TOKEN_FALSE);
                    case 'o': return check_keyword(parser, 2, 1, "r", TOKEN_FOR);
                    case 'u': return check_keyword(parser, 2, 6, "nction", TOKEN_FUNCTION);
                }
            }
            break;
        case 'i': 
            if (parser->current - parser->previous_token.start > 1) {
                switch (parser->previous_token.start[1]) {
                    case 'f': return check_keyword(parser, 2, 0, "", TOKEN_IF);
                    case 'm': return check_keyword(parser, 2, 5, "ports", TOKEN_IMPORTS);
                    case 'n': return check_keyword(parser, 2, 10, "itialization", TOKEN_INITIALIZATION);
                }
            }
            break;
        case 'n': return check_keyword(parser, 1, 2, "il", TOKEN_NIL);
        case 'o': return check_keyword(parser, 1, 1, "r", TOKEN_OR);
        case 'q': return check_keyword(parser, 1, 6, "uantum", TOKEN_QUANTUM);
        case 'r': 
            if (parser->current - parser->previous_token.start > 1) {
                switch (parser->previous_token.start[1]) {
                    case 'e': return check_keyword(parser, 2, 4, "turn", TOKEN_RETURN);
                    case 'o': return check_keyword(parser, 2, 3, "ute", TOKEN_ROUTE);
                }
            }
            break;
        case 't': return check_keyword(parser, 1, 3, "rue", TOKEN_TRUE);
        case 'w': return check_keyword(parser, 1, 4, "hile", TOKEN_WHILE);
    }
    
    return TOKEN_IDENTIFIER;
}

/* 扫描下一个标记 */
static Token scan_token(Parser* parser) {
    skip_whitespace(parser);
    
    parser->previous_token.start = parser->current;
    
    if (is_at_end(parser)) {
        return make_token(parser, TOKEN_EOF);
    }
    
    char c = advance(parser);
    
    if (is_alpha(c)) {
        // 标识符或关键字
        while (is_alphanumeric(peek(parser))) {
            advance(parser);
        }
        
        TokenType type = identifier_type(parser);
        return make_token(parser, type);
    }
    
    if (is_digit(c)) {
        // 数字
        while (is_digit(peek(parser))) {
            advance(parser);
        }
        
        // 小数部分
        if (peek(parser) == '.' && is_digit(peek_next(parser))) {
            advance(parser); // 消费 '.'
            
            while (is_digit(peek(parser))) {
                advance(parser);
            }
        }
        
        return make_token(parser, TOKEN_NUMBER);
    }
    
    switch (c) {
        case '(': return make_token(parser, TOKEN_LPAREN);
        case ')': return make_token(parser, TOKEN_RPAREN);
        case '{': return make_token(parser, TOKEN_LBRACE);
        case '}': return make_token(parser, TOKEN_RBRACE);
        case '[': return make_token(parser, TOKEN_LBRACKET);
        case ']': return make_token(parser, TOKEN_RBRACKET);
        case ';': return make_token(parser, TOKEN_SEMICOLON);
        case ',': return make_token(parser, TOKEN_COMMA);
        case '.': return make_token(parser, TOKEN_DOT);
        case '-': 
            if (match(parser, '>')) {
                return make_token(parser, TOKEN_ARROW);
            }
            return make_token(parser, TOKEN_MINUS);
        case '+': return make_token(parser, TOKEN_PLUS);
        case '/': return make_token(parser, TOKEN_SLASH);
        case '*': return make_token(parser, TOKEN_STAR);
        case '%': return make_token(parser, TOKEN_PERCENT);
        case '!': 
            if (match(parser, '=')) {
                return make_token(parser, TOKEN_BANG_EQUAL);
            }
            return make_token(parser, TOKEN_BANG);
        case '=': 
            if (match(parser, '=')) {
                return make_token(parser, TOKEN_EQUAL_EQUAL);
            }
            return make_token(parser, TOKEN_EQUAL);
        case '<': 
            if (match(parser, '=')) {
                return make_token(parser, TOKEN_LESS_EQUAL);
            }
            return make_token(parser, TOKEN_LESS);
        case '>': 
            if (match(parser, '=')) {
                return make_token(parser, TOKEN_GREATER_EQUAL);
            }
            return make_token(parser, TOKEN_GREATER);
        case '"': {
            // 字符串
            while (peek(parser) != '"' && !is_at_end(parser)) {
                if (peek(parser) == '\n') {
                    parser->line++;
                }
                advance(parser);
            }
            
            if (is_at_end(parser)) {
                return error_token(parser, "Unterminated string.");
            }
            
            // 消费结束的引号
            advance(parser);
            return make_token(parser, TOKEN_STRING);
        }
    }
    
    return error_token(parser, "Unexpected character.");
}

/* 打印QEntL版本信息 */
void print_version() {
    printf("QEntL语言解释器 v%d.%d.%d\n", 
           QENTL_VERSION_MAJOR, 
           QENTL_VERSION_MINOR, 
           QENTL_VERSION_PATCH);
    printf("量子纠缠语言 - 完全自主实现\n");
}

/* 主解释器入口 */
int qentl_interpret(const char* source) {
    Parser parser;
    init_parser(&parser, source);
    
    int line = -1;
    for (;;) {
        Token token = scan_token(&parser);
        
        if (token.line != line) {
            printf("%4d ", token.line);
            line = token.line;
        } else {
            printf("   | ");
        }
        
        printf("%-12s '%.*s'\n", 
               token.type, 
               token.length, 
               token.start);
        
        if (token.type == TOKEN_EOF) break;
    }
    
    return parser.had_error ? -1 : 0;
}

/* 从文件读取代码进行解释 */
int interpret_file(const char* file_path) {
    FILE* file = fopen(file_path, "rb");
    if (file == NULL) {
        fprintf(stderr, "无法打开文件 \"%s\".\n", file_path);
        return -1;
    }
    
    fseek(file, 0L, SEEK_END);
    size_t file_size = ftell(file);
    rewind(file);
    
    char* buffer = (char*)malloc(file_size + 1);
    if (buffer == NULL) {
        fprintf(stderr, "内存不足.\n");
        fclose(file);
        return -1;
    }
    
    size_t bytes_read = fread(buffer, sizeof(char), file_size, file);
    if (bytes_read < file_size) {
        fprintf(stderr, "无法读取文件 \"%s\".\n", file_path);
        free(buffer);
        fclose(file);
        return -1;
    }
    
    buffer[bytes_read] = '\0';
    
    fclose(file);
    
    int result = qentl_interpret(buffer);
    
    free(buffer);
    return result;
}

/* 互动模式 */
void repl() {
    char line[1024];
    
    for (;;) {
        printf("QEntL> ");
        
        if (!fgets(line, sizeof(line), stdin)) {
            printf("\n");
            break;
        }
        
        qentl_interpret(line);
    }
}

/* 主函数 */
int main(int argc, char* argv[]) {
    print_version();
    
    if (argc == 1) {
        // 无参数，进入REPL模式
        repl();
    } else if (argc == 2) {
        // 单个参数，解释文件
        if (strcmp(argv[1], "--version") == 0 || 
            strcmp(argv[1], "-v") == 0) {
            // 已经打印过版本信息
            return 0;
        }
        
        return interpret_file(argv[1]);
    } else {
        fprintf(stderr, "用法: qentl [文件路径]\n");
        return 1;
    }
    
    return 0;
} 