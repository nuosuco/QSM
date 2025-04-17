/**
 * QEntL编辑器代码补全实现
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月19日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>
#include "code_completion.h"

#define MAX_COMPLETIONS 100
#define MAX_LINE_LENGTH 1024

// 补全项结构
typedef struct {
    char* text;               // 补全文本
    char* display_text;       // 显示文本
    CompletionType type;      // 补全类型
    char* description;        // 描述
} CompletionItem;

// 代码补全结构
struct CodeCompletion {
    CompletionItem* items;    // 补全项数组
    int item_count;           // 补全项数量
    int capacity;             // 数组容量
    
    // QEntL语言的内置项
    CompletionItem* builtin_items;   // 内置补全项
    int builtin_count;               // 内置项数量
    
    CompletionCallback callback;     // 回调函数
    void* callback_data;             // 回调函数用户数据
};

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

// QEntL标准函数列表
static const char* std_functions[] = {
    "create_state", "create_qregister", "apply_gate", "measure_qubit",
    "get_probability", "get_amplitude", "set_phase", "entangle_qubits",
    "teleport_qubit", "create_bell_pair", "create_ghz_state", "quantum_fourier_transform",
    "print", "println", "read_line", "parse_int", "parse_float", "to_string",
    "array_length", "array_push", "array_pop", NULL
};

// QEntL标准函数描述
static const char* std_function_descriptions[] = {
    "创建一个新的量子态",
    "创建一个量子寄存器",
    "应用量子门到量子比特",
    "测量量子比特",
    "获取特定状态的概率",
    "获取特定状态的振幅",
    "设置量子态的相位",
    "纠缠多个量子比特",
    "量子隐形传态",
    "创建一个贝尔对",
    "创建一个GHZ态",
    "执行量子傅里叶变换",
    "打印内容",
    "打印内容并换行",
    "从标准输入读取一行文本",
    "将字符串解析为整数",
    "将字符串解析为浮点数",
    "将值转换为字符串",
    "获取数组长度",
    "向数组末尾添加元素",
    "移除并返回数组末尾元素",
    NULL
};

// 初始化内置补全项
static void init_builtin_completions(CodeCompletion* comp) {
    // 计算内置项总数
    int count = 0;
    
    // 计算关键字数量
    for (int i = 0; keywords[i] != NULL; i++) count++;
    
    // 计算量子关键字数量
    for (int i = 0; quantum_keywords[i] != NULL; i++) count++;
    
    // 计算量子门数量
    for (int i = 0; quantum_gates[i] != NULL; i++) count++;
    
    // 计算标准函数数量
    for (int i = 0; std_functions[i] != NULL; i++) count++;
    
    // 分配内置项数组
    comp->builtin_items = (CompletionItem*)malloc(count * sizeof(CompletionItem));
    if (!comp->builtin_items) return;
    
    comp->builtin_count = count;
    int index = 0;
    
    // 添加关键字
    for (int i = 0; keywords[i] != NULL; i++) {
        comp->builtin_items[index].text = strdup(keywords[i]);
        comp->builtin_items[index].display_text = strdup(keywords[i]);
        comp->builtin_items[index].type = COMPLETION_KEYWORD;
        comp->builtin_items[index].description = strdup("关键字");
        index++;
    }
    
    // 添加量子关键字
    for (int i = 0; quantum_keywords[i] != NULL; i++) {
        comp->builtin_items[index].text = strdup(quantum_keywords[i]);
        comp->builtin_items[index].display_text = strdup(quantum_keywords[i]);
        comp->builtin_items[index].type = COMPLETION_QUANTUM_KEYWORD;
        comp->builtin_items[index].description = strdup("量子关键字");
        index++;
    }
    
    // 添加量子门
    for (int i = 0; quantum_gates[i] != NULL; i++) {
        comp->builtin_items[index].text = strdup(quantum_gates[i]);
        comp->builtin_items[index].display_text = strdup(quantum_gates[i]);
        comp->builtin_items[index].type = COMPLETION_QUANTUM_GATE;
        comp->builtin_items[index].description = strdup("量子门");
        index++;
    }
    
    // 添加标准函数
    for (int i = 0; std_functions[i] != NULL; i++) {
        comp->builtin_items[index].text = strdup(std_functions[i]);
        char display[256];
        snprintf(display, sizeof(display), "%s()", std_functions[i]);
        comp->builtin_items[index].display_text = strdup(display);
        comp->builtin_items[index].type = COMPLETION_FUNCTION;
        comp->builtin_items[index].description = 
            std_function_descriptions[i] ? strdup(std_function_descriptions[i]) : strdup("标准函数");
        index++;
    }
}

// 释放内置补全项
static void free_builtin_completions(CodeCompletion* comp) {
    if (!comp || !comp->builtin_items) return;
    
    for (int i = 0; i < comp->builtin_count; i++) {
        free(comp->builtin_items[i].text);
        free(comp->builtin_items[i].display_text);
        free(comp->builtin_items[i].description);
    }
    
    free(comp->builtin_items);
    comp->builtin_items = NULL;
    comp->builtin_count = 0;
}

// 创建代码补全
CodeCompletion* code_completion_create(void) {
    CodeCompletion* comp = (CodeCompletion*)malloc(sizeof(CodeCompletion));
    if (!comp) return NULL;
    
    // 初始化补全项数组
    comp->capacity = MAX_COMPLETIONS;
    comp->items = (CompletionItem*)malloc(comp->capacity * sizeof(CompletionItem));
    if (!comp->items) {
        free(comp);
        return NULL;
    }
    
    comp->item_count = 0;
    comp->callback = NULL;
    comp->callback_data = NULL;
    
    // 初始化内置补全项
    init_builtin_completions(comp);
    
    return comp;
}

// 销毁代码补全
void code_completion_destroy(CodeCompletion* comp) {
    if (!comp) return;
    
    // 释放补全项
    for (int i = 0; i < comp->item_count; i++) {
        free(comp->items[i].text);
        free(comp->items[i].display_text);
        free(comp->items[i].description);
    }
    
    free(comp->items);
    
    // 释放内置补全项
    free_builtin_completions(comp);
    
    free(comp);
}

// 添加补全项
bool code_completion_add_item(CodeCompletion* comp, const char* text, 
                            const char* display_text, CompletionType type,
                            const char* description) {
    if (!comp || !text) return false;
    
    // 检查是否需要扩展数组
    if (comp->item_count >= comp->capacity) {
        int new_capacity = comp->capacity * 2;
        CompletionItem* new_items = (CompletionItem*)realloc(
            comp->items, new_capacity * sizeof(CompletionItem)
        );
        
        if (!new_items) return false;
        
        comp->items = new_items;
        comp->capacity = new_capacity;
    }
    
    // 添加新项
    comp->items[comp->item_count].text = strdup(text);
    comp->items[comp->item_count].display_text = 
        display_text ? strdup(display_text) : strdup(text);
    comp->items[comp->item_count].type = type;
    comp->items[comp->item_count].description = 
        description ? strdup(description) : strdup("");
    
    comp->item_count++;
    
    return true;
}

// 清除所有补全项
void code_completion_clear(CodeCompletion* comp) {
    if (!comp) return;
    
    // 释放所有项
    for (int i = 0; i < comp->item_count; i++) {
        free(comp->items[i].text);
        free(comp->items[i].display_text);
        free(comp->items[i].description);
    }
    
    comp->item_count = 0;
}

// 设置补全回调函数
void code_completion_set_callback(CodeCompletion* comp, 
                                CompletionCallback callback, 
                                void* user_data) {
    if (!comp) return;
    
    comp->callback = callback;
    comp->callback_data = user_data;
}

// 调用补全回调函数
static void trigger_completion(CodeCompletion* comp, 
                              CompletionItem* items, int count) {
    if (!comp || !comp->callback) return;
    
    // 创建结果数组
    CompletionResult* results = (CompletionResult*)malloc(count * sizeof(CompletionResult));
    if (!results) return;
    
    // 填充结果
    for (int i = 0; i < count; i++) {
        results[i].text = items[i].text;
        results[i].display_text = items[i].display_text;
        results[i].type = items[i].type;
        results[i].description = items[i].description;
    }
    
    // 调用回调函数
    comp->callback(results, count, comp->callback_data);
    
    // 释放结果数组（但不释放字符串，因为它们仍由补全项拥有）
    free(results);
}

// 字符串前缀匹配
static bool starts_with(const char* str, const char* prefix) {
    if (!str || !prefix) return false;
    
    size_t str_len = strlen(str);
    size_t prefix_len = strlen(prefix);
    
    if (prefix_len > str_len) return false;
    
    return strncmp(str, prefix, prefix_len) == 0;
}

// 获取当前行光标前的单词
static char* get_word_before_cursor(const char* line, int cursor_pos) {
    if (!line || cursor_pos <= 0) return strdup("");
    
    // 确保光标位置不超过行长度
    int line_len = strlen(line);
    if (cursor_pos > line_len) cursor_pos = line_len;
    
    // 找到光标前的单词起始位置
    int word_start = cursor_pos - 1;
    while (word_start >= 0 && (isalnum(line[word_start]) || line[word_start] == '_')) {
        word_start--;
    }
    word_start++; // 移动到实际单词开始
    
    // 提取单词
    int word_len = cursor_pos - word_start;
    char* word = (char*)malloc(word_len + 1);
    if (!word) return strdup("");
    
    strncpy(word, line + word_start, word_len);
    word[word_len] = '\0';
    
    return word;
}

// 计算上下文
static void analyze_context(const char* line, int cursor_pos, bool* in_quantum_block,
                           bool* after_apply, bool* after_dot) {
    if (!line || !in_quantum_block || !after_apply || !after_dot) return;
    
    *in_quantum_block = false;
    *after_apply = false;
    *after_dot = false;
    
    // 检查是否在量子块中
    const char* quantum_start = strstr(line, "quantum");
    if (quantum_start && (quantum_start - line) < cursor_pos) {
        const char* block_start = strchr(quantum_start, '{');
        if (block_start && (block_start - line) < cursor_pos) {
            const char* block_end = strchr(block_start, '}');
            if (!block_end || (block_end - line) > cursor_pos) {
                *in_quantum_block = true;
            }
        }
    }
    
    // 检查是否在apply之后
    const char* apply = strstr(line, "apply");
    if (apply && (apply - line) < cursor_pos) {
        const char* apply_end = apply + 5; // strlen("apply")
        if (*apply_end == '(' || isspace(*apply_end)) {
            *after_apply = true;
        }
    }
    
    // 检查是否在点操作符之后
    for (int i = 0; i < cursor_pos - 1; i++) {
        if (line[i] == '.' && isspace(line[i+1])) {
            *after_dot = true;
            break;
        }
    }
}

// 根据上下文过滤补全项
static CompletionItem* filter_items_by_context(CodeCompletion* comp, 
                                             const char* prefix,
                                             bool in_quantum_block,
                                             bool after_apply,
                                             bool after_dot,
                                             int* count) {
    if (!comp || !count) return NULL;
    
    // 分配结果数组
    CompletionItem* results = (CompletionItem*)malloc(
        (comp->item_count + comp->builtin_count) * sizeof(CompletionItem)
    );
    if (!results) return NULL;
    
    *count = 0;
    
    // 首先添加用户定义的项
    for (int i = 0; i < comp->item_count; i++) {
        if (prefix && prefix[0] != '\0') {
            if (!starts_with(comp->items[i].text, prefix)) continue;
        }
        
        results[*count] = comp->items[i];
        (*count)++;
    }
    
    // 然后添加内置项
    for (int i = 0; i < comp->builtin_count; i++) {
        // 根据上下文过滤
        CompletionType type = comp->builtin_items[i].type;
        
        // 在量子块外不显示量子关键字和量子门
        if (!in_quantum_block && 
            (type == COMPLETION_QUANTUM_KEYWORD || type == COMPLETION_QUANTUM_GATE)) {
            continue;
        }
        
        // 在apply之后只显示量子门
        if (after_apply && type != COMPLETION_QUANTUM_GATE) {
            continue;
        }
        
        // 前缀匹配
        if (prefix && prefix[0] != '\0') {
            if (!starts_with(comp->builtin_items[i].text, prefix)) continue;
        }
        
        // 复制项目
        results[*count].text = comp->builtin_items[i].text;
        results[*count].display_text = comp->builtin_items[i].display_text;
        results[*count].type = comp->builtin_items[i].type;
        results[*count].description = comp->builtin_items[i].description;
        (*count)++;
    }
    
    return results;
}

// 执行代码补全
void code_completion_complete(CodeCompletion* comp, const char* line, int cursor_pos) {
    if (!comp || !line) return;
    
    // 获取光标前的单词
    char* prefix = get_word_before_cursor(line, cursor_pos);
    
    // 分析上下文
    bool in_quantum_block = false;
    bool after_apply = false;
    bool after_dot = false;
    analyze_context(line, cursor_pos, &in_quantum_block, &after_apply, &after_dot);
    
    // 根据上下文过滤补全项
    int count = 0;
    CompletionItem* filtered = filter_items_by_context(
        comp, prefix, in_quantum_block, after_apply, after_dot, &count
    );
    
    // 触发补全回调
    if (filtered && count > 0) {
        trigger_completion(comp, filtered, count);
    }
    
    // 清理
    free(prefix);
    free(filtered);
} 