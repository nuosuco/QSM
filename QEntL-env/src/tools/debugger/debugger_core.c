/**
 * QEntL调试器核心实现
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月19日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <stdarg.h>
#include "debugger_core.h"

#define MAX_BREAKPOINTS 100
#define MAX_VARIABLES 200
#define MAX_STACK_FRAMES 50

// 断点结构
typedef struct {
    int id;                  // 断点ID
    BreakpointType type;     // 断点类型
    char* file;              // 文件名
    int line;                // 行号
    char* function;          // 函数名
    char* condition;         // 条件表达式
    bool enabled;            // 是否启用
    int hit_count;           // 命中次数
} Breakpoint;

// 断点管理器结构
struct BreakpointManager {
    Breakpoint breakpoints[MAX_BREAKPOINTS];  // 断点数组
    int count;                               // 断点数量
    int next_id;                             // 下一个断点ID
};

// 状态检查器结构
struct StateInspector {
    VariableInfo local_variables[MAX_VARIABLES];   // 局部变量数组
    int local_count;                              // 局部变量数量
    
    VariableInfo global_variables[MAX_VARIABLES];  // 全局变量数组
    int global_count;                             // 全局变量数量
    
    StackFrame call_stack[MAX_STACK_FRAMES];       // 调用栈数组
    int stack_count;                              // 调用栈帧数量
};

// 调试器结构
struct Debugger {
    DebuggerState state;                     // 当前状态
    char* current_file;                      // 当前文件
    int current_line;                        // 当前行号
    ExecutionMode exec_mode;                 // 执行模式
    
    BreakpointManager* bp_manager;           // 断点管理器
    StateInspector* inspector;               // 状态检查器
    
    FILE* process_stdin;                     // 调试进程标准输入
    FILE* process_stdout;                    // 调试进程标准输出
    int process_id;                          // 调试进程ID
    
    char* working_dir;                       // 工作目录
    char* program_args;                      // 程序参数
    
    DebuggerEventCallback event_callback;    // 事件回调函数
    void* callback_data;                     // 回调函数用户数据
    
    DebugLogLevel log_level;                   // 日志级别
    DebugLogCallback log_callback;              // 日志回调函数
    void* log_user_data;                     // 日志回调函数用户数据
    
    char log_history[MAX_LOG_HISTORY][1024];   // 日志历史记录
    int log_history_count;                    // 日志历史记录数量
    int log_history_index;                    // 日志历史记录索引
    
    char program_path[MAX_PATH_LENGTH];        // 程序路径
    DebuggerStats stats;                        // 调试器统计信息
};

// 创建调试器
Debugger* debugger_create(void) {
    Debugger* debugger = (Debugger*)malloc(sizeof(Debugger));
    if (!debugger) {
        return NULL;
    }
    
    // 初始化基本状态
    memset(debugger, 0, sizeof(Debugger));
    debugger->state = DEBUGGER_IDLE;
    debugger->input_stream = stdin;
    debugger->output_stream = stdout;
    debugger->error_stream = stderr;
    
    // 初始化日志级别
    debugger->log_level = DEBUG_LOG_INFO;
    
    // 配置默认设置
    debugger->config.break_on_exception = true;
    debugger->config.break_on_error = true;
    debugger->config.async_mode = false;
    debugger->config.allow_remote = false;
    strcpy(debugger->config.remote_host, "localhost");
    debugger->config.remote_port = 9000;
    
    // 记录创建时间
    debugger->stats.start_time = time(NULL);
    
    return debugger;
}

// 销毁调试器
void debugger_destroy(Debugger* debugger) {
    if (!debugger) {
        return;
    }
    
    // 停止调试会话（如果正在运行）
    if (debugger->state != DEBUGGER_IDLE && debugger->state != DEBUGGER_STOPPED) {
        debugger_stop(debugger);
    }
    
    // 释放资源
    debugger_cleanup_resources(debugger);
    
    // 关闭日志文件（如果有）
    if (debugger->log_file) {
        fclose(debugger->log_file);
        debugger->log_file = NULL;
    }
    
    // 释放日志历史
    for (int i = 0; i < debugger->log_history_count; i++) {
        if (debugger->log_history[i]) {
            free(debugger->log_history[i]);
        }
    }
    
    // 释放调试器结构体
    free(debugger);
}

// 清理资源
void debugger_cleanup_resources(Debugger* debugger) {
    if (!debugger) {
        return;
    }
    
    // 释放程序参数
    if (debugger->program_args) {
        for (int i = 0; i < debugger->program_args_count; i++) {
            if (debugger->program_args[i]) {
                free(debugger->program_args[i]);
            }
        }
        free(debugger->program_args);
        debugger->program_args = NULL;
        debugger->program_args_count = 0;
    }
    
    // 释放断点
    for (int i = 0; i < debugger->breakpoint_count; i++) {
        if (debugger->breakpoints[i].condition) {
            free(debugger->breakpoints[i].condition);
        }
    }
}

// 注册事件处理函数
bool debugger_register_event_handler(Debugger* debugger, DebugEventType event_type, 
                                    DebugEventCallback callback, void* user_data) {
    if (!debugger || !callback) {
        return false;
    }
    
    // 检查是否已达到最大回调数
    if (debugger->event_count >= MAX_EVENT_CALLBACKS) {
        debugger_log(debugger, DEBUG_LOG_ERROR, "已达到最大事件处理函数数量");
        return false;
    }
    
    // 检查事件类型有效性
    if (event_type < 0 || event_type >= DEBUG_EVENT_MAX) {
        debugger_log(debugger, DEBUG_LOG_ERROR, "无效的事件类型 %d", event_type);
        return false;
    }
    
    // 检查是否已注册相同的回调函数
    for (int i = 0; i < debugger->event_count; i++) {
        if (debugger->event_callbacks[i].event_type == event_type && 
            debugger->event_callbacks[i].callback == callback) {
            // 只更新用户数据
            debugger->event_callbacks[i].user_data = user_data;
            return true;
        }
    }
    
    // 添加新的回调
    debugger->event_callbacks[debugger->event_count].event_type = event_type;
    debugger->event_callbacks[debugger->event_count].callback = callback;
    debugger->event_callbacks[debugger->event_count].user_data = user_data;
    debugger->event_count++;
    
    debugger_log(debugger, DEBUG_LOG_INFO, "已注册事件处理函数，类型: %s", 
                 debugger_get_event_name(event_type));
    
    return true;
}

// 取消注册事件处理函数
bool debugger_unregister_event_handler(Debugger* debugger, DebugEventType event_type, 
                                      DebugEventCallback callback) {
    if (!debugger || !callback) {
        return false;
    }
    
    // 查找并移除回调
    for (int i = 0; i < debugger->event_count; i++) {
        if (debugger->event_callbacks[i].event_type == event_type && 
            debugger->event_callbacks[i].callback == callback) {
            
            // 通过移动最后一个元素到当前位置来快速删除
            if (i < debugger->event_count - 1) {
                debugger->event_callbacks[i] = debugger->event_callbacks[debugger->event_count - 1];
            }
            
            // 减少计数
            debugger->event_count--;
            
            debugger_log(debugger, DEBUG_LOG_INFO, "已取消注册事件处理函数，类型: %s", 
                         debugger_get_event_name(event_type));
            return true;
        }
    }
    
    // 没有找到匹配的回调
    return false;
}

// 触发事件
void debugger_trigger_event(Debugger* debugger, DebugEventType event_type, void* event_data) {
    if (!debugger) {
        return;
    }
    
    // 创建事件结构体
    DebugEvent event;
    event.type = event_type;
    event.data = event_data;
    event.timestamp = time(NULL);
    event.debugger = debugger;
    
    // 记录事件到历史记录
    int index = debugger->event_history_index;
    debugger->event_history[index] = event;
    debugger->event_history_index = (index + 1) % MAX_EVENT_HISTORY;
    if (debugger->event_history_count < MAX_EVENT_HISTORY) {
        debugger->event_history_count++;
    }
    
    // 记录日志
    debugger_log(debugger, DEBUG_LOG_INFO, "触发事件: %s", debugger_get_event_name(event_type));
    
    // 调用所有匹配的事件处理函数
    for (int i = 0; i < debugger->event_count; i++) {
        EventCallbackEntry* entry = &debugger->event_callbacks[i];
        
        // 调用特定类型的回调或通用回调（DEBUG_EVENT_ALL）
        if (entry->event_type == event_type || entry->event_type == DEBUG_EVENT_ALL) {
            entry->callback(&event, entry->user_data);
        }
    }
}

// 获取事件类型名称
const char* debugger_get_event_name(DebugEventType event_type) {
    switch (event_type) {
        case DEBUG_EVENT_START:             return "调试开始";
        case DEBUG_EVENT_TERMINATE:         return "调试终止";
        case DEBUG_EVENT_PAUSE:             return "调试暂停";
        case DEBUG_EVENT_RESUME:            return "调试恢复";
        case DEBUG_EVENT_STEP:              return "单步执行";
        case DEBUG_EVENT_BREAKPOINT_HIT:    return "断点命中";
        case DEBUG_EVENT_BREAKPOINT_ADD:    return "断点添加";
        case DEBUG_EVENT_BREAKPOINT_REMOVE: return "断点移除";
        case DEBUG_EVENT_EXCEPTION:         return "异常";
        case DEBUG_EVENT_OUTPUT:            return "输出";
        case DEBUG_EVENT_PROCESS_EXIT:      return "进程退出";
        case DEBUG_EVENT_PROCESS_SIGNAL:    return "进程信号";
        case DEBUG_EVENT_VARIABLE_CHANGE:   return "变量改变";
        case DEBUG_EVENT_STACK_CHANGE:      return "栈帧改变";
        case DEBUG_EVENT_ALL:               return "所有事件";
        default:                            return "未知事件";
    }
}

// 设置日志级别
void debugger_set_log_level(Debugger* debugger, DebugLogLevel level) {
    if (!debugger) {
        return;
    }
    
    debugger->log_level = level;
    
    const char* level_name = "未知";
    switch (level) {
        case DEBUG_LOG_DEBUG:   level_name = "调试"; break;
        case DEBUG_LOG_INFO:    level_name = "信息"; break;
        case DEBUG_LOG_WARNING: level_name = "警告"; break;
        case DEBUG_LOG_ERROR:   level_name = "错误"; break;
    }
    
    debugger_log(debugger, DEBUG_LOG_INFO, "日志级别已设置为: %s", level_name);
}

// 设置日志回调函数
void debugger_set_log_callback(Debugger* debugger, DebugLogCallback callback, void* user_data) {
    if (!debugger) {
        return;
    }
    
    debugger->log_callback = callback;
    debugger->log_user_data = user_data;
    
    debugger_log(debugger, DEBUG_LOG_INFO, "已设置日志回调函数");
}

// 记录日志
void debugger_log(Debugger* debugger, DebugLogLevel level, const char* format, ...) {
    if (!debugger || !format) {
        return;
    }
    
    // 检查日志级别
    if (level < debugger->log_level) {
        return;
    }
    
    // 准备时间戳
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    char timestamp[20];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", tm_info);
    
    // 准备日志消息
    char message[1024];
    va_list args;
    va_start(args, format);
    vsnprintf(message, sizeof(message), format, args);
    va_end(args);
    
    // 获取级别前缀
    const char* level_prefix = "";
    FILE* output = debugger->output_stream;
    
    switch (level) {
        case DEBUG_LOG_DEBUG:
            level_prefix = "[调试] ";
            break;
        case DEBUG_LOG_INFO:
            level_prefix = "[信息] ";
            break;
        case DEBUG_LOG_WARNING:
            level_prefix = "[警告] ";
            output = debugger->error_stream;
            break;
        case DEBUG_LOG_ERROR:
            level_prefix = "[错误] ";
            output = debugger->error_stream;
            break;
    }
    
    // 输出日志
    fprintf(output, "%s %s%s\n", timestamp, level_prefix, message);
    
    // 调用日志回调
    if (debugger->log_callback) {
        debugger->log_callback(level, message, debugger->log_user_data);
    }
    
    // 记录到日志文件（如果已设置）
    if (debugger->log_file) {
        fprintf(debugger->log_file, "[%s] %s%s\n", timestamp, level_prefix, message);
        fflush(debugger->log_file);
    }
    
    // 添加到历史记录
    char* log_entry = (char*)malloc(strlen(timestamp) + strlen(message) + strlen(level_prefix) + 4);
    if (log_entry) {
        sprintf(log_entry, "[%s] %s%s", timestamp, level_prefix, message);
        
        // 释放可能被覆盖的旧日志
        if (debugger->log_history[debugger->log_history_index]) {
            free(debugger->log_history[debugger->log_history_index]);
        }
        
        // 存储新日志
        debugger->log_history[debugger->log_history_index] = log_entry;
        debugger->log_history_index = (debugger->log_history_index + 1) % MAX_LOG_HISTORY;
        if (debugger->log_history_count < MAX_LOG_HISTORY) {
            debugger->log_history_count++;
        }
    }
}

// 设置日志文件
bool debugger_set_log_file(Debugger* debugger, const char* filename) {
    if (!debugger || !filename) {
        return false;
    }
    
    // 关闭现有日志文件
    if (debugger->log_file) {
        fclose(debugger->log_file);
        debugger->log_file = NULL;
    }
    
    // 打开新日志文件
    debugger->log_file = fopen(filename, "a");
    if (!debugger->log_file) {
        debugger_log(debugger, DEBUG_LOG_ERROR, "无法打开日志文件 '%s'", filename);
        return false;
    }
    
    debugger_log(debugger, DEBUG_LOG_INFO, "日志文件已设置为: %s", filename);
    return true;
}

// 获取日志历史
const char** debugger_get_log_history(Debugger* debugger, int* count) {
    if (!debugger || !count) {
        return NULL;
    }
    
    *count = debugger->log_history_count;
    return (const char**)debugger->log_history;
}

// 清空日志历史
void debugger_clear_log_history(Debugger* debugger) {
    if (!debugger) {
        return;
    }
    
    // 释放所有日志条目
    for (int i = 0; i < debugger->log_history_count; i++) {
        if (debugger->log_history[i]) {
            free(debugger->log_history[i]);
            debugger->log_history[i] = NULL;
        }
    }
    
    // 重置计数
    debugger->log_history_count = 0;
    debugger->log_history_index = 0;
    
    debugger_log(debugger, DEBUG_LOG_INFO, "日志历史已清空");
}

// 开始调试会话
bool debugger_start(Debugger* debugger, const char* program_path) {
    if (!debugger || !program_path) {
        return false;
    }
    
    // 检查状态
    if (debugger->state != DEBUGGER_IDLE && debugger->state != DEBUGGER_STOPPED) {
        debugger_log(debugger, DEBUG_LOG_ERROR, "无法启动调试会话，当前状态不是空闲或已停止");
        return false;
    }
    
    // 记录路径
    strncpy(debugger->program_path, program_path, MAX_PATH_LENGTH - 1);
    debugger->program_path[MAX_PATH_LENGTH - 1] = '\0';
    
    // 更新状态
    debugger->state = DEBUGGER_RUNNING;
    
    // 重置统计
    debugger->stats.breakpoints_hit_count = 0;
    debugger->stats.step_count = 0;
    debugger->stats.continue_count = 0;
    debugger->stats.exception_count = 0;
    debugger->stats.start_time = time(NULL);
    
    // 记录日志
    debugger_log(debugger, DEBUG_LOG_INFO, "开始调试会话：%s", program_path);
    
    // 触发开始事件
    debugger_trigger_event(debugger, DEBUG_EVENT_START, NULL);
    
    return true;
}

// 暂停调试会话
bool debugger_pause(Debugger* debugger) {
    if (!debugger) {
        return false;
    }
    
    // 检查状态
    if (debugger->state != DEBUGGER_RUNNING) {
        debugger_log(debugger, DEBUG_LOG_ERROR, "无法暂停调试会话，当前状态不是运行中");
        return false;
    }
    
    // 更新状态
    debugger->state = DEBUGGER_PAUSED;
    
    // 记录日志
    debugger_log(debugger, DEBUG_LOG_INFO, "调试会话已暂停");
    
    // 触发暂停事件
    debugger_trigger_event(debugger, DEBUG_EVENT_PAUSE, NULL);
    
    return true;
}

// 恢复调试会话
bool debugger_resume(Debugger* debugger) {
    if (!debugger) {
        return false;
    }
    
    // 检查状态
    if (debugger->state != DEBUGGER_PAUSED && debugger->state != DEBUGGER_STEPPING) {
        debugger_log(debugger, DEBUG_LOG_ERROR, "无法恢复调试会话，当前状态不是暂停或单步");
        return false;
    }
    
    // 更新状态
    debugger->state = DEBUGGER_RUNNING;
    
    // 更新统计
    debugger->stats.continue_count++;
    
    // 记录日志
    debugger_log(debugger, DEBUG_LOG_INFO, "调试会话已恢复");
    
    // 触发恢复事件
    debugger_trigger_event(debugger, DEBUG_EVENT_RESUME, NULL);
    
    return true;
}

// 停止调试会话
bool debugger_stop(Debugger* debugger) {
    if (!debugger) {
        return false;
    }
    
    // 检查状态
    if (debugger->state == DEBUGGER_IDLE || debugger->state == DEBUGGER_STOPPED) {
        debugger_log(debugger, DEBUG_LOG_INFO, "调试会话已经停止");
        return true;
    }
    
    // 更新状态
    debugger->state = DEBUGGER_STOPPED;
    
    // 记录日志
    debugger_log(debugger, DEBUG_LOG_INFO, "调试会话已停止");
    
    // 触发终止事件
    debugger_trigger_event(debugger, DEBUG_EVENT_TERMINATE, NULL);
    
    return true;
}

// 单步执行（进入函数）
bool debugger_step_into(Debugger* debugger) {
    if (!debugger) {
        return false;
    }
    
    // 检查状态
    if (debugger->state != DEBUGGER_PAUSED && debugger->state != DEBUGGER_STEPPING) {
        debugger_log(debugger, DEBUG_LOG_ERROR, "无法执行单步调试，当前状态不是暂停或单步");
        return false;
    }
    
    // 更新状态
    debugger->state = DEBUGGER_STEPPING;
    
    // 更新统计
    debugger->stats.step_count++;
    
    // 记录日志
    debugger_log(debugger, DEBUG_LOG_INFO, "执行单步调试（进入函数）");
    
    // 触发单步事件
    debugger_trigger_event(debugger, DEBUG_EVENT_STEP, NULL);
    
    return true;
}

// 单步执行（跳过函数）
bool debugger_step_over(Debugger* debugger) {
    if (!debugger) {
        return false;
    }
    
    // 检查状态
    if (debugger->state != DEBUGGER_PAUSED && debugger->state != DEBUGGER_STEPPING) {
        debugger_log(debugger, DEBUG_LOG_ERROR, "无法执行单步调试，当前状态不是暂停或单步");
        return false;
    }
    
    // 更新状态
    debugger->state = DEBUGGER_STEPPING_OVER;
    
    // 更新统计
    debugger->stats.step_count++;
    
    // 记录日志
    debugger_log(debugger, DEBUG_LOG_INFO, "执行单步调试（跳过函数）");
    
    // 触发单步事件
    debugger_trigger_event(debugger, DEBUG_EVENT_STEP, NULL);
    
    return true;
}

// 单步执行（跳出函数）
bool debugger_step_out(Debugger* debugger) {
    if (!debugger) {
        return false;
    }
    
    // 检查状态
    if (debugger->state != DEBUGGER_PAUSED && debugger->state != DEBUGGER_STEPPING) {
        debugger_log(debugger, DEBUG_LOG_ERROR, "无法执行单步调试，当前状态不是暂停或单步");
        return false;
    }
    
    // 更新状态
    debugger->state = DEBUGGER_STEPPING_OUT;
    
    // 更新统计
    debugger->stats.step_count++;
    
    // 记录日志
    debugger_log(debugger, DEBUG_LOG_INFO, "执行单步调试（跳出函数）");
    
    // 触发单步事件
    debugger_trigger_event(debugger, DEBUG_EVENT_STEP, NULL);
    
    return true;
}

// 添加断点
int debugger_add_breakpoint(Debugger* debugger, BreakpointType type, const char* file, 
                            int line, const char* function, const char* condition) {
    if (!debugger || !debugger->bp_manager) return 0;
    
    // 检查断点数量是否超出限制
    if (debugger->bp_manager->count >= MAX_BREAKPOINTS) {
        fprintf(stderr, "错误：断点数量已达到上限\n");
        return 0;
    }
    
    // 创建新断点
    Breakpoint* bp = &debugger->bp_manager->breakpoints[debugger->bp_manager->count];
    bp->id = debugger->bp_manager->next_id++;
    bp->type = type;
    bp->file = file ? strdup(file) : NULL;
    bp->line = line;
    bp->function = function ? strdup(function) : NULL;
    bp->condition = condition ? strdup(condition) : NULL;
    bp->enabled = true;
    bp->hit_count = 0;
    
    debugger->bp_manager->count++;
    
    return bp->id;
}

// 移除断点
bool debugger_remove_breakpoint(Debugger* debugger, int breakpoint_id) {
    if (!debugger || !debugger->bp_manager) return false;
    
    // 查找断点
    for (int i = 0; i < debugger->bp_manager->count; i++) {
        if (debugger->bp_manager->breakpoints[i].id == breakpoint_id) {
            // 释放断点资源
            Breakpoint* bp = &debugger->bp_manager->breakpoints[i];
            
            if (bp->file) free(bp->file);
            if (bp->function) free(bp->function);
            if (bp->condition) free(bp->condition);
            
            // 移动后续断点
            for (int j = i; j < debugger->bp_manager->count - 1; j++) {
                debugger->bp_manager->breakpoints[j] = debugger->bp_manager->breakpoints[j + 1];
            }
            
            debugger->bp_manager->count--;
            return true;
        }
    }
    
    return false;
}

// 启用/禁用断点
bool debugger_enable_breakpoint(Debugger* debugger, int breakpoint_id, bool enable) {
    if (!debugger || !debugger->bp_manager) return false;
    
    // 查找断点
    for (int i = 0; i < debugger->bp_manager->count; i++) {
        if (debugger->bp_manager->breakpoints[i].id == breakpoint_id) {
            debugger->bp_manager->breakpoints[i].enabled = enable;
            return true;
        }
    }
    
    return false;
}

// 获取断点列表
BreakpointInfo* debugger_get_breakpoints(Debugger* debugger, int* count) {
    if (!debugger || !debugger->bp_manager || !count) return NULL;
    
    *count = debugger->bp_manager->count;
    
    if (*count == 0) return NULL;
    
    // 创建断点信息数组
    BreakpointInfo* info = (BreakpointInfo*)malloc(*count * sizeof(BreakpointInfo));
    if (!info) {
        *count = 0;
        return NULL;
    }
    
    // 复制断点信息
    for (int i = 0; i < *count; i++) {
        Breakpoint* bp = &debugger->bp_manager->breakpoints[i];
        
        info[i].id = bp->id;
        info[i].type = bp->type;
        info[i].file = bp->file ? strdup(bp->file) : NULL;
        info[i].line = bp->line;
        info[i].function = bp->function ? strdup(bp->function) : NULL;
        info[i].condition = bp->condition ? strdup(bp->condition) : NULL;
        info[i].enabled = bp->enabled;
        info[i].hit_count = bp->hit_count;
    }
    
    return info;
}

// 更新局部变量
bool debugger_update_locals(Debugger* debugger, VariableInfo* variables, int count) {
    if (!debugger || !debugger->inspector) return false;
    
    // 清理现有的局部变量
    for (int i = 0; i < debugger->inspector->local_count; i++) {
        VariableInfo* var = &debugger->inspector->local_variables[i];
        
        if (var->name) free(var->name);
        if (var->type) free(var->type);
        if (var->value) free(var->value);
    }
    
    // 检查变量数量是否超出限制
    if (count > MAX_VARIABLES) {
        fprintf(stderr, "警告：局部变量数量超出限制，只加载前%d个\n", MAX_VARIABLES);
        count = MAX_VARIABLES;
    }
    
    // 更新变量
    debugger->inspector->local_count = count;
    
    for (int i = 0; i < count; i++) {
        VariableInfo* src = &variables[i];
        VariableInfo* dst = &debugger->inspector->local_variables[i];
        
        dst->name = src->name ? strdup(src->name) : NULL;
        dst->type = src->type ? strdup(src->type) : NULL;
        dst->value = src->value ? strdup(src->value) : NULL;
        dst->flags = src->flags;
    }
    
    return true;
}

// 更新全局变量
bool debugger_update_globals(Debugger* debugger, VariableInfo* variables, int count) {
    if (!debugger || !debugger->inspector) return false;
    
    // 清理现有的全局变量
    for (int i = 0; i < debugger->inspector->global_count; i++) {
        VariableInfo* var = &debugger->inspector->global_variables[i];
        
        if (var->name) free(var->name);
        if (var->type) free(var->type);
        if (var->value) free(var->value);
    }
    
    // 检查变量数量是否超出限制
    if (count > MAX_VARIABLES) {
        fprintf(stderr, "警告：全局变量数量超出限制，只加载前%d个\n", MAX_VARIABLES);
        count = MAX_VARIABLES;
    }
    
    // 更新变量
    debugger->inspector->global_count = count;
    
    for (int i = 0; i < count; i++) {
        VariableInfo* src = &variables[i];
        VariableInfo* dst = &debugger->inspector->global_variables[i];
        
        dst->name = src->name ? strdup(src->name) : NULL;
        dst->type = src->type ? strdup(src->type) : NULL;
        dst->value = src->value ? strdup(src->value) : NULL;
        dst->flags = src->flags;
    }
    
    return true;
}

// 更新调用栈
bool debugger_update_callstack(Debugger* debugger, StackFrame* frames, int count) {
    if (!debugger || !debugger->inspector) return false;
    
    // 清理现有的调用栈
    for (int i = 0; i < debugger->inspector->stack_count; i++) {
        StackFrame* frame = &debugger->inspector->call_stack[i];
        
        if (frame->function) free(frame->function);
        if (frame->file) free(frame->file);
    }
    
    // 检查栈帧数量是否超出限制
    if (count > MAX_STACK_FRAMES) {
        fprintf(stderr, "警告：调用栈帧数量超出限制，只加载前%d个\n", MAX_STACK_FRAMES);
        count = MAX_STACK_FRAMES;
    }
    
    // 更新调用栈
    debugger->inspector->stack_count = count;
    
    for (int i = 0; i < count; i++) {
        StackFrame* src = &frames[i];
        StackFrame* dst = &debugger->inspector->call_stack[i];
        
        dst->function = src->function ? strdup(src->function) : NULL;
        dst->file = src->file ? strdup(src->file) : NULL;
        dst->line = src->line;
        dst->level = src->level;
    }
    
    return true;
}

// 获取局部变量
VariableInfo* debugger_get_locals(Debugger* debugger, int* count) {
    if (!debugger || !debugger->inspector || !count) return NULL;
    
    *count = debugger->inspector->local_count;
    
    if (*count == 0) return NULL;
    
    // 创建变量信息数组
    VariableInfo* info = (VariableInfo*)malloc(*count * sizeof(VariableInfo));
    if (!info) {
        *count = 0;
        return NULL;
    }
    
    // 复制变量信息
    for (int i = 0; i < *count; i++) {
        VariableInfo* src = &debugger->inspector->local_variables[i];
        VariableInfo* dst = &info[i];
        
        dst->name = src->name ? strdup(src->name) : NULL;
        dst->type = src->type ? strdup(src->type) : NULL;
        dst->value = src->value ? strdup(src->value) : NULL;
        dst->flags = src->flags;
    }
    
    return info;
}

// 获取全局变量
VariableInfo* debugger_get_globals(Debugger* debugger, int* count) {
    if (!debugger || !debugger->inspector || !count) return NULL;
    
    *count = debugger->inspector->global_count;
    
    if (*count == 0) return NULL;
    
    // 创建变量信息数组
    VariableInfo* info = (VariableInfo*)malloc(*count * sizeof(VariableInfo));
    if (!info) {
        *count = 0;
        return NULL;
    }
    
    // 复制变量信息
    for (int i = 0; i < *count; i++) {
        VariableInfo* src = &debugger->inspector->global_variables[i];
        VariableInfo* dst = &info[i];
        
        dst->name = src->name ? strdup(src->name) : NULL;
        dst->type = src->type ? strdup(src->type) : NULL;
        dst->value = src->value ? strdup(src->value) : NULL;
        dst->flags = src->flags;
    }
    
    return info;
}

// 获取调用栈
StackFrame* debugger_get_callstack(Debugger* debugger, int* count) {
    if (!debugger || !debugger->inspector || !count) return NULL;
    
    *count = debugger->inspector->stack_count;
    
    if (*count == 0) return NULL;
    
    // 创建栈帧信息数组
    StackFrame* info = (StackFrame*)malloc(*count * sizeof(StackFrame));
    if (!info) {
        *count = 0;
        return NULL;
    }
    
    // 复制栈帧信息
    for (int i = 0; i < *count; i++) {
        StackFrame* src = &debugger->inspector->call_stack[i];
        StackFrame* dst = &info[i];
        
        dst->function = src->function ? strdup(src->function) : NULL;
        dst->file = src->file ? strdup(src->file) : NULL;
        dst->line = src->line;
        dst->level = src->level;
    }
    
    return info;
}

// 查找变量
VariableInfo* debugger_find_variable(Debugger* debugger, const char* name, bool* is_global) {
    if (!debugger || !debugger->inspector || !name) return NULL;
    
    // 先在局部变量中查找
    for (int i = 0; i < debugger->inspector->local_count; i++) {
        VariableInfo* var = &debugger->inspector->local_variables[i];
        
        if (var->name && strcmp(var->name, name) == 0) {
            if (is_global) *is_global = false;
            
            // 创建变量副本
            VariableInfo* result = (VariableInfo*)malloc(sizeof(VariableInfo));
            if (!result) return NULL;
            
            result->name = var->name ? strdup(var->name) : NULL;
            result->type = var->type ? strdup(var->type) : NULL;
            result->value = var->value ? strdup(var->value) : NULL;
            result->flags = var->flags;
            
            return result;
        }
    }
    
    // 再在全局变量中查找
    for (int i = 0; i < debugger->inspector->global_count; i++) {
        VariableInfo* var = &debugger->inspector->global_variables[i];
        
        if (var->name && strcmp(var->name, name) == 0) {
            if (is_global) *is_global = true;
            
            // 创建变量副本
            VariableInfo* result = (VariableInfo*)malloc(sizeof(VariableInfo));
            if (!result) return NULL;
            
            result->name = var->name ? strdup(var->name) : NULL;
            result->type = var->type ? strdup(var->type) : NULL;
            result->value = var->value ? strdup(var->value) : NULL;
            result->flags = var->flags;
            
            return result;
        }
    }
    
    return NULL;
}

// 执行表达式
char* debugger_evaluate_expression(Debugger* debugger, const char* expression) {
    if (!debugger || !expression) return NULL;
    
    // 检查调试器状态
    if (debugger->state != DEBUGGER_PAUSED && debugger->state != DEBUGGER_STEPPING) {
        return strdup("错误：调试器未暂停，无法执行表达式");
    }
    
    // 模拟表达式求值
    // 注意：这里只是模拟，实际实现需要解析表达式并与调试进程交互
    
    // 示例：如果表达式是变量名，尝试查找变量值
    bool is_global;
    VariableInfo* var = debugger_find_variable(debugger, expression, &is_global);
    
    if (var) {
        char* result;
        if (var->value) {
            // 添加变量类型到结果
            if (var->type) {
                result = malloc(strlen(var->value) + strlen(var->type) + 50);
                sprintf(result, "(%s) %s [%s]", var->type, var->value, 
                       is_global ? "全局变量" : "局部变量");
            } else {
                result = malloc(strlen(var->value) + 50);
                sprintf(result, "%s [%s]", var->value, 
                       is_global ? "全局变量" : "局部变量");
            }
        } else {
            result = strdup("<无值>");
        }
        
        // 释放变量副本
        if (var->name) free(var->name);
        if (var->type) free(var->type);
        if (var->value) free(var->value);
        free(var);
        
        return result;
    }
    
    // 如果不是简单变量名，模拟表达式计算
    if (strlen(expression) < 100) {
        char* result = malloc(strlen(expression) + 50);
        sprintf(result, "表达式 '%s' 的模拟结果", expression);
        return result;
    } else {
        return strdup("表达式过长，无法计算");
    }
}

// 设置程序参数
void debugger_set_program_args(Debugger* debugger, const char* args) {
    if (!debugger) return;
    
    if (debugger->program_args) {
        free(debugger->program_args);
        debugger->program_args = NULL;
    }
    
    if (args) {
        debugger->program_args = strdup(args);
    }
}

// 发送命令到调试进程
bool debugger_send_command(Debugger* debugger, const char* command) {
    if (!debugger || !command) return false;
    
    // 检查调试器状态
    if (debugger->state == DEBUGGER_IDLE || debugger->state == DEBUGGER_STOPPED) {
        return false;
    }
    
    // 检查进程输入流
    if (!debugger->process_stdin) {
        fprintf(stderr, "错误：调试进程输入流未打开\n");
        return false;
    }
    
    // 向调试进程发送命令
    fprintf(debugger->process_stdin, "%s\n", command);
    fflush(debugger->process_stdin);
    
    return true;
}

// 中断调试进程执行
bool debugger_interrupt(Debugger* debugger) {
    if (!debugger) return false;
    
    // 检查调试器状态
    if (debugger->state != DEBUGGER_RUNNING) {
        return false;
    }
    
    // 发送中断信号到调试进程（此处模拟）
    return debugger_pause(debugger);
}

// 跳到指定位置执行
bool debugger_run_to_location(Debugger* debugger, const char* file, int line) {
    if (!debugger || !file) return false;
    
    // 检查调试器状态
    if (debugger->state != DEBUGGER_PAUSED && debugger->state != DEBUGGER_STEPPING) {
        return false;
    }
    
    // 设置临时断点
    int bp_id = debugger_add_breakpoint(debugger, BP_LINE, file, line, NULL, NULL);
    if (bp_id == 0) {
        return false;
    }
    
    // 恢复执行
    bool result = debugger_resume(debugger);
    
    // 恢复后自动移除临时断点
    debugger_remove_breakpoint(debugger, bp_id);
    
    return result;
}

// 获取调试器统计信息
void debugger_get_stats(Debugger* debugger, DebuggerStats* stats) {
    if (!debugger || !stats) {
        return;
    }
    
    // 复制统计信息
    *stats = debugger->stats;
}

// 设置调试器配置
void debugger_set_config(Debugger* debugger, DebuggerConfig* config) {
    if (!debugger || !config) return;
    
    // 复制配置
    memcpy(&debugger->config, config, sizeof(DebuggerConfig));
    
    // 记录日志
    debugger_log(debugger, DEBUG_LOG_INFO, "调试器配置已更新");
}

// 获取调试器配置
void debugger_get_config(Debugger* debugger, DebuggerConfig* config) {
    if (!debugger || !config) return;
    
    // 复制配置
    memcpy(config, &debugger->config, sizeof(DebuggerConfig));
}

// 获取调试器统计信息
void debugger_get_stats(Debugger* debugger, DebuggerStats* stats) {
    if (!debugger || !stats) {
        return;
    }
    
    // 复制统计信息
    *stats = debugger->stats;
}

// 设置调试器配置
void debugger_set_config(Debugger* debugger, DebuggerConfig* config) {
    if (!debugger || !config) return;
    
    // 复制配置
    memcpy(&debugger->config, config, sizeof(DebuggerConfig));
    
    // 记录日志
    debugger_log(debugger, DEBUG_LOG_INFO, "调试器配置已更新");
}

// 获取调试器配置
void debugger_get_config(Debugger* debugger, DebuggerConfig* config) {
    if (!debugger || !config) return;
    
    // 复制配置
    memcpy(config, &debugger->config, sizeof(DebuggerConfig));
}

// 获取调试器统计信息
void debugger_get_stats(Debugger* debugger, DebuggerStats* stats) {
    if (!debugger || !stats) {
        return;
    }
    
    // 复制统计信息
    *stats = debugger->stats;
} 