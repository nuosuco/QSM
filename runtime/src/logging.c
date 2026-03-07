// QEntL运行时 - 日志系统实现
// 版本: 1.0.0

#include "qentl_runtime.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdarg.h>
#include <time.h>

// ============================================================================
// 日志级别定义（与头文件一致）
// ============================================================================

// 使用头文件中的QentlLogLevel，这里定义匹配的常量
#define LOG_LEVEL_DEBUG    QENTL_LOG_DEBUG
#define LOG_LEVEL_INFO     QENTL_LOG_INFO
#define LOG_LEVEL_WARN     QENTL_LOG_WARNING
#define LOG_LEVEL_ERROR    QENTL_LOG_ERROR
#define LOG_LEVEL_FATAL    QENTL_LOG_FATAL
#define LOG_LEVEL_NONE     QENTL_LOG_NONE

// 日志级别名称
static const char* LOG_LEVEL_NAMES[] = {
    "DEBUG",
    "INFO",
    "WARN",
    "ERROR",
    "FATAL",
    "NONE"
};

// 日志级别颜色（ANSI转义码）
static const char* LOG_LEVEL_COLORS[] = {
    "\033[36m",  // DEBUG: 青色
    "\033[32m",  // INFO:  绿色
    "\033[33m",  // WARN:  黄色
    "\033[31m",  // ERROR: 红色
    "\033[35m",  // FATAL: 洋红色
    "\033[0m"    // NONE:  默认
};

// ============================================================================
// 日志系统状态
// ============================================================================

typedef struct {
    QentlLogLevel current_level;
    bool use_colors;
    bool output_to_file;
    char* log_file_path;
    FILE* log_file;
    bool initialized;
} LogSystemState;

static LogSystemState g_log_state = {
    .current_level = LOG_LEVEL_INFO,
    .use_colors = true,
    .output_to_file = false,
    .log_file_path = NULL,
    .log_file = NULL,
    .initialized = false
};

// ============================================================================
// 内部工具函数
// ============================================================================

static const char* get_current_time_string(void) {
    static char time_buffer[64];
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    
    strftime(time_buffer, sizeof(time_buffer), "%Y-%m-%d %H:%M:%S", tm_info);
    return time_buffer;
}

static void log_output(const char* level_name, const char* color_code, 
                      const char* file, int line, const char* format, va_list args) {
    // 获取当前时间
    const char* timestamp = get_current_time_string();
    
    // 格式化消息
    char message_buffer[1024];
    vsnprintf(message_buffer, sizeof(message_buffer), format, args);
    
    // 输出到控制台
    if (g_log_state.use_colors) {
        fprintf(stderr, "%s[%s] %s%-5s\033[0m %s:%d: %s\n",
                color_code, timestamp, color_code, level_name, file, line, message_buffer);
    } else {
        fprintf(stderr, "[%s] %-5s %s:%d: %s\n",
                timestamp, level_name, file, line, message_buffer);
    }
    
    // 输出到文件（如果启用）
    if (g_log_state.output_to_file && g_log_state.log_file != NULL) {
        fprintf(g_log_state.log_file, "[%s] %-5s %s:%d: %s\n",
                timestamp, level_name, file, line, message_buffer);
        fflush(g_log_state.log_file);
    }
}

// ============================================================================
// 公共API实现
// ============================================================================

void qentl_log_init(QentlLogLevel level, bool use_colors) {
    if (g_log_state.initialized) {
        return;
    }
    
    g_log_state.current_level = level;
    g_log_state.use_colors = use_colors;
    g_log_state.initialized = true;
    
    qentl_log_debug(__FILE__, __LINE__, "日志系统初始化完成，级别: %s", 
                    LOG_LEVEL_NAMES[level]);
}

void qentl_log_set_level(QentlLogLevel level) {
    g_log_state.current_level = level;
}

void qentl_log_set_file(const char* file_path) {
    // 关闭现有日志文件
    if (g_log_state.log_file != NULL) {
        fclose(g_log_state.log_file);
        g_log_state.log_file = NULL;
    }
    
    // 释放现有文件路径
    if (g_log_state.log_file_path != NULL) {
        qentl_free(g_log_state.log_file_path);
        g_log_state.log_file_path = NULL;
    }
    
    // 设置新文件路径
    if (file_path != NULL && file_path[0] != '\0') {
        g_log_state.log_file_path = qentl_string_create(file_path);
        g_log_state.output_to_file = true;
        
        // 打开日志文件（追加模式）
        g_log_state.log_file = fopen(file_path, "a");
        if (g_log_state.log_file == NULL) {
            fprintf(stderr, "❌ 无法打开日志文件: %s\n", file_path);
            g_log_state.output_to_file = false;
        } else {
            qentl_log_info(__FILE__, __LINE__, "日志输出到文件: %s", file_path);
        }
    } else {
        g_log_state.output_to_file = false;
    }
}

void qentl_log_cleanup(void) {
    if (!g_log_state.initialized) {
        return;
    }
    
    qentl_log_debug(__FILE__, __LINE__, "日志系统清理中...");
    
    // 关闭日志文件
    if (g_log_state.log_file != NULL) {
        fclose(g_log_state.log_file);
        g_log_state.log_file = NULL;
    }
    
    // 释放文件路径
    if (g_log_state.log_file_path != NULL) {
        qentl_free(g_log_state.log_file_path);
        g_log_state.log_file_path = NULL;
    }
    
    g_log_state.initialized = false;
    printf("[日志] 日志系统清理完成\n");
}

// ============================================================================
// 日志记录函数
// ============================================================================

void qentl_log_debug(const char* file, int line, const char* format, ...) {
    if (g_log_state.current_level > LOG_LEVEL_DEBUG) {
        return;
    }
    
    va_list args;
    va_start(args, format);
    log_output("DEBUG", LOG_LEVEL_COLORS[LOG_LEVEL_DEBUG], file, line, format, args);
    va_end(args);
}

void qentl_log_info(const char* file, int line, const char* format, ...) {
    if (g_log_state.current_level > LOG_LEVEL_INFO) {
        return;
    }
    
    va_list args;
    va_start(args, format);
    log_output("INFO", LOG_LEVEL_COLORS[LOG_LEVEL_INFO], file, line, format, args);
    va_end(args);
}

void qentl_log_warn(const char* file, int line, const char* format, ...) {
    if (g_log_state.current_level > LOG_LEVEL_WARN) {
        return;
    }
    
    va_list args;
    va_start(args, format);
    log_output("WARN", LOG_LEVEL_COLORS[LOG_LEVEL_WARN], file, line, format, args);
    va_end(args);
}

void qentl_log_error(const char* file, int line, const char* format, ...) {
    if (g_log_state.current_level > LOG_LEVEL_ERROR) {
        return;
    }
    
    va_list args;
    va_start(args, format);
    log_output("ERROR", LOG_LEVEL_COLORS[LOG_LEVEL_ERROR], file, line, format, args);
    va_end(args);
}

void qentl_log_fatal(const char* file, int line, const char* format, ...) {
    // FATAL总是记录，无论当前日志级别
    va_list args;
    va_start(args, format);
    log_output("FATAL", LOG_LEVEL_COLORS[LOG_LEVEL_FATAL], file, line, format, args);
    va_end(args);
    
    // FATAL日志通常意味着程序应该终止
    exit(EXIT_FAILURE);
}

// ============================================================================
// 辅助函数
// ============================================================================

void qentl_log_dump_memory_stats(void) {
    size_t used = qentl_memory_used();
    qentl_log_info(__FILE__, __LINE__, "内存使用统计: %zu 字节", used);
}

void qentl_log_dump_value(QentlValue value) {
    char* str = qentl_value_to_string(value);
    qentl_log_debug(__FILE__, __LINE__, "值转储: %s", str);
    qentl_string_free(str);
}

void qentl_log_dump_array(QentlArray* array) {
    if (array == NULL) {
        qentl_log_debug(__FILE__, __LINE__, "数组转储: NULL");
        return;
    }
    
    size_t length = qentl_array_length(array);
    qentl_log_debug(__FILE__, __LINE__, "数组转储: length=%zu, capacity=%zu", 
                    length, qentl_array_capacity(array));
    
    for (size_t i = 0; i < length && i < 10; i++) {
        QentlValue value = qentl_array_get(array, i);
        char* str = qentl_value_to_string(value);
        qentl_log_debug(__FILE__, __LINE__, "  [%zu]: %s", i, str);
        qentl_string_free(str);
    }
    
    if (length > 10) {
        qentl_log_debug(__FILE__, __LINE__, "  ... 还有 %zu 个元素", length - 10);
    }
}