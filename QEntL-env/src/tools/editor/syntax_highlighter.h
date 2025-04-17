/**
 * QEntL编辑器语法高亮器头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月19日
 */

#ifndef QENTL_SYNTAX_HIGHLIGHTER_H
#define QENTL_SYNTAX_HIGHLIGHTER_H

#include <stdio.h>
#include <stdbool.h>

// 语法标记类型
typedef enum {
    TOKEN_IDENTIFIER,     // 标识符
    TOKEN_KEYWORD,        // 关键字
    TOKEN_QUANTUM_KEYWORD,// 量子关键字
    TOKEN_STRING,         // 字符串
    TOKEN_NUMBER,         // 数字
    TOKEN_COMMENT,        // 注释
    TOKEN_OPERATOR,       // 运算符
    TOKEN_FUNCTION,       // 函数
    TOKEN_WHITESPACE,     // 空白
    TOKEN_OTHER           // 其他
} SyntaxTokenType;

// 前置声明
typedef struct SyntaxHighlighter SyntaxHighlighter;

// 语法高亮回调函数类型
typedef void (*SyntaxHighlightCallback)(const char* token, SyntaxTokenType type, void* user_data);

// 创建语法高亮器
SyntaxHighlighter* syntax_highlighter_create(void);

// 销毁语法高亮器
void syntax_highlighter_destroy(SyntaxHighlighter* highlighter);

// 设置是否启用彩色输出
void syntax_highlighter_set_use_colors(SyntaxHighlighter* highlighter, bool use_colors);

// 设置高亮回调函数
void syntax_highlighter_set_callback(SyntaxHighlighter* highlighter, 
                                   SyntaxHighlightCallback callback, 
                                   void* user_data);

// 高亮单行文本
void syntax_highlighter_highlight_line(SyntaxHighlighter* highlighter, const char* line);

// 高亮整个文件
void syntax_highlighter_highlight_file(SyntaxHighlighter* highlighter, FILE* file);

// 高亮字符串
void syntax_highlighter_highlight_string(SyntaxHighlighter* highlighter, const char* text);

#endif /* QENTL_SYNTAX_HIGHLIGHTER_H */ 