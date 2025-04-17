/**
 * QEntL编辑器代码补全头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月19日
 */

#ifndef QENTL_CODE_COMPLETION_H
#define QENTL_CODE_COMPLETION_H

#include <stdbool.h>

// 补全类型
typedef enum {
    COMPLETION_IDENTIFIER,     // 标识符
    COMPLETION_KEYWORD,        // 关键字
    COMPLETION_QUANTUM_KEYWORD,// 量子关键字
    COMPLETION_QUANTUM_GATE,   // 量子门
    COMPLETION_FUNCTION,       // 函数
    COMPLETION_VARIABLE,       // 变量
    COMPLETION_PROPERTY,       // 属性
    COMPLETION_METHOD,         // 方法
    COMPLETION_CLASS,          // 类
    COMPLETION_STRUCT,         // 结构
    COMPLETION_ENUM,           // 枚举
    COMPLETION_SNIPPET         // 代码片段
} CompletionType;

// 补全结果结构
typedef struct {
    const char* text;          // 补全文本
    const char* display_text;  // 显示文本
    CompletionType type;       // 补全类型
    const char* description;   // 描述
} CompletionResult;

// 前置声明
typedef struct CodeCompletion CodeCompletion;

// 补全回调函数类型
typedef void (*CompletionCallback)(CompletionResult* results, int count, void* user_data);

// 创建代码补全
CodeCompletion* code_completion_create(void);

// 销毁代码补全
void code_completion_destroy(CodeCompletion* comp);

// 添加补全项
bool code_completion_add_item(CodeCompletion* comp, const char* text, 
                            const char* display_text, CompletionType type,
                            const char* description);

// 清除所有补全项
void code_completion_clear(CodeCompletion* comp);

// 设置补全回调函数
void code_completion_set_callback(CodeCompletion* comp, 
                                CompletionCallback callback, 
                                void* user_data);

// 执行代码补全
void code_completion_complete(CodeCompletion* comp, const char* line, int cursor_pos);

#endif /* QENTL_CODE_COMPLETION_H */ 