// QEntL最小化运行时 - 核心头文件
// 版本: 1.0.0
// 描述: QEntL运行时的最小化实现，支持运行QEntL编译器
// 量子基因编码: QGC-RUNTIME-CORE-20260202

#ifndef QENTL_RUNTIME_H
#define QENTL_RUNTIME_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

// ============================================================================
// 基本类型定义
// ============================================================================

// 错误类型
typedef enum {
    QENTL_ERROR_NONE = 0,
    QENTL_ERROR_SYNTAX,
    QENTL_ERROR_TYPE,
    QENTL_ERROR_RUNTIME,
    QENTL_ERROR_MEMORY,
    QENTL_ERROR_IO,
    QENTL_ERROR_NOT_IMPLEMENTED
} QentlErrorType;

// 基础值类型
typedef enum {
    QENTL_TYPE_NULL,
    QENTL_TYPE_BOOLEAN,
    QENTL_TYPE_INTEGER,
    QENTL_TYPE_FLOAT,
    QENTL_TYPE_STRING,
    QENTL_TYPE_ARRAY,
    QENTL_TYPE_OBJECT,
    QENTL_TYPE_FUNCTION
} QentlType;

// 值联合体
typedef union {
    bool boolean;
    int64_t integer;
    double floating;
    void* pointer;
} QentlValueData;

// 值结构体
typedef struct {
    QentlType type;
    QentlValueData data;
} QentlValue;

// ============================================================================
// 内存管理API
// ============================================================================

// 初始化内存系统
void qentl_memory_init(void);

// 清理内存系统
void qentl_memory_cleanup(void);

// 分配内存
void* qentl_alloc(size_t size);

// 分配并清零内存
void* qentl_calloc(size_t count, size_t size);

// 重新分配内存
void* qentl_realloc(void* ptr, size_t size);

// 释放内存
void qentl_free(void* ptr);

// 获取已使用内存量
size_t qentl_memory_used(void);

// ============================================================================
// 字符串API (必须支持)
// ============================================================================

// 创建字符串（复制输入字符串）
char* qentl_string_create(const char* value);

// 创建字符串（不复制，直接使用输入字符串，调用者不能释放）
char* qentl_string_create_const(const char* value);

// 连接两个字符串
char* qentl_string_concat(const char* str1, const char* str2);

// 格式化字符串（类似printf）
char* qentl_string_format(const char* format, ...);

// 获取字符串长度
size_t qentl_string_length(const char* str);

// 释放字符串
void qentl_string_free(char* str);

// ============================================================================
// 数组API (必须支持)
// ============================================================================

// 数组结构体
typedef struct {
    size_t capacity;
    size_t length;
    QentlValue* elements;
} QentlArray;

// 创建数组
QentlArray* qentl_array_create(size_t initial_capacity);

// 销毁数组
void qentl_array_destroy(QentlArray* array);

// 向数组添加元素
void qentl_array_push(QentlArray* array, QentlValue value);

// 从数组获取元素
QentlValue qentl_array_get(QentlArray* array, size_t index);

// 设置数组元素
void qentl_array_set(QentlArray* array, size_t index, QentlValue value);

// 获取数组长度
size_t qentl_array_length(QentlArray* array);

// 获取数组容量
size_t qentl_array_capacity(QentlArray* array);

// 清空数组
void qentl_array_clear(QentlArray* array);

// ============================================================================
// 值操作API
// ============================================================================

// 创建各种类型的值
QentlValue qentl_value_null(void);
QentlValue qentl_value_boolean(bool value);
QentlValue qentl_value_integer(int64_t value);
QentlValue qentl_value_float(double value);
QentlValue qentl_value_string(const char* value);
QentlValue qentl_value_array(QentlArray* array);

// 获取值的类型
QentlType qentl_value_get_type(QentlValue value);

// 检查值是否为真（truthy）
bool qentl_value_is_truthy(QentlValue value);

// 克隆值（深拷贝）
QentlValue qentl_value_clone(QentlValue value);

// 释放值占用的资源
void qentl_value_free(QentlValue value);

// 值转换为字符串表示（用于调试）
char* qentl_value_to_string(QentlValue value);

// ============================================================================
// 错误处理API
// ============================================================================

// 设置错误
void qentl_error_set(QentlErrorType type, const char* message, int line, int column);

// 获取最后一个错误
QentlErrorType qentl_error_get_last(void);

// 获取错误消息
const char* qentl_error_get_message(void);

// 清除错误
void qentl_error_clear(void);

// 检查是否有错误
bool qentl_error_has_error(void);

// ============================================================================
// 日志和输出API (必须支持)
// ============================================================================

// 日志级别
typedef enum {
    QENTL_LOG_DEBUG,
    QENTL_LOG_INFO,
    QENTL_LOG_WARNING,
    QENTL_LOG_ERROR,
    QENTL_LOG_FATAL,
    QENTL_LOG_NONE
} QentlLogLevel;

// 日志系统初始化
void qentl_log_init(QentlLogLevel level, bool use_colors);

// 设置日志级别
void qentl_log_set_level(QentlLogLevel level);

// 设置日志输出文件
void qentl_log_set_file(const char* file_path);

// 清理日志系统
void qentl_log_cleanup(void);

// 记录日志（带文件名和行号）
void qentl_log_debug(const char* file, int line, const char* format, ...);
void qentl_log_info(const char* file, int line, const char* format, ...);
void qentl_log_warn(const char* file, int line, const char* format, ...);
void qentl_log_error(const char* file, int line, const char* format, ...);
void qentl_log_fatal(const char* file, int line, const char* format, ...);

// 兼容旧API
void qentl_log(QentlLogLevel level, const char* format, ...);

// 打印值到标准输出
void qentl_print(QentlValue value);

// 打印值到标准输出并换行
void qentl_println(QentlValue value);

// 辅助调试函数
void qentl_log_dump_memory_stats(void);
void qentl_log_dump_value(QentlValue value);
void qentl_log_dump_array(QentlArray* array);

// ============================================================================
// 运行时核心API
// ============================================================================

// 运行时状态
typedef struct QentlRuntime QentlRuntime;

// 创建运行时实例
QentlRuntime* qentl_runtime_create(void);

// 销毁运行时实例
void qentl_runtime_destroy(QentlRuntime* runtime);

// 初始化运行时（全局）
void qentl_runtime_init(void);

// 清理运行时（全局）
void qentl_runtime_cleanup(void);

// 重置运行时状态
void qentl_runtime_reset(QentlRuntime* runtime);

// ============================================================================
// 编译器特定支持API
// ============================================================================

// 标记类型（用于词法分析器）
typedef enum {
    QENTL_TOKEN_KEYWORD,
    QENTL_TOKEN_IDENTIFIER,
    QENTL_TOKEN_LITERAL,
    QENTL_TOKEN_OPERATOR,
    QENTL_TOKEN_SEPARATOR,
    QENTL_TOKEN_COMMENT,
    QENTL_TOKEN_EOF
} QentlTokenType;

// 标记结构（用于词法分析器）
typedef struct {
    QentlTokenType type;
    char* value;
    int line;
    int column;
} QentlToken;

// 标记数组（用于词法分析器）
typedef struct {
    size_t capacity;
    size_t length;
    QentlToken* tokens;
} QentlTokenArray;

// 创建标记数组
QentlTokenArray* qentl_token_array_create(void);

// 销毁标记数组
void qentl_token_array_destroy(QentlTokenArray* array);

// 向标记数组添加标记
void qentl_token_array_push(QentlTokenArray* array, QentlToken token);

// 从标记数组获取标记
QentlToken qentl_token_array_get(QentlTokenArray* array, size_t index);

// ============================================================================
// 工具函数
// ============================================================================

// 检查字符串是否为空或空白
bool qentl_string_is_empty(const char* str);

// 检查字符是否是字母（支持中文）
bool qentl_char_is_letter(char c);

// 检查字符是否是数字
bool qentl_char_is_digit(char c);

// 检查字符是否是字母数字
bool qentl_char_is_alnum(char c);

// 转换为小写
char qentl_char_tolower(char c);

// 字符串比较（支持空指针）
int qentl_string_compare(const char* str1, const char* str2);

// 字符串复制
char* qentl_string_copy(const char* str);

// ============================================================================
// 虚拟机支持（包含虚拟机头文件）
// ============================================================================

#ifdef QENTL_RUNTIME_FULL
#include "qentl_vm.h"
#endif

#endif // QENTL_RUNTIME_H