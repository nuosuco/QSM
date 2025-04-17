/**
 * QEntL调试器核心头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月19日
 */

#ifndef QENTL_DEBUGGER_CORE_H
#define QENTL_DEBUGGER_CORE_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <stdarg.h>

// 最大限制常量
#define MAX_BREAKPOINTS        100    // 最大断点数
#define MAX_LOCALS             200    // 最大局部变量数
#define MAX_GLOBALS            300    // 最大全局变量数
#define MAX_CALLSTACK          50     // 最大调用栈深度
#define MAX_EVENT_CALLBACKS    20     // 最大事件回调数
#define MAX_EVENT_HISTORY      100    // 最大事件历史记录数
#define MAX_LOG_HISTORY        200    // 最大日志历史记录数
#define MAX_VAR_NAME_LENGTH    64     // 最大变量名长度
#define MAX_EXPR_LENGTH        256    // 最大表达式长度
#define MAX_PATH_LENGTH        512    // 最大路径长度

// 断点类型
typedef enum {
    BP_LINE,         // 行断点
    BP_FUNCTION,     // 函数断点
    BP_CONDITION,    // 条件断点
    BP_QUANTUM_STATE,// 量子状态断点
    BP_ENTANGLEMENT  // 纠缠断点
} BreakpointType;

// 调试状态
typedef enum {
    DEBUG_NONE,      // 未启动
    DEBUG_RUNNING,   // 运行中
    DEBUG_PAUSED,    // 已暂停
    DEBUG_STEPPED,   // 单步执行
    DEBUG_ERROR,     // 错误状态
    DEBUG_FINISHED   // 执行完成
} DebuggerState;

// 执行模式
typedef enum {
    EXEC_CONTINUE,   // 继续执行
    EXEC_STEP_OVER,  // 单步执行（跳过函数）
    EXEC_STEP_INTO,  // 单步执行（进入函数）
    EXEC_STEP_OUT,   // 单步执行（跳出函数）
    EXEC_RUN_TO      // 运行到指定位置
} ExecutionMode;

// 前置声明
typedef struct Debugger Debugger;
typedef struct BreakpointManager BreakpointManager;
typedef struct StateInspector StateInspector;

// 调试事件类型
typedef enum {
    DEBUG_EVENT_START,            // 调试会话开始
    DEBUG_EVENT_TERMINATE,        // 调试会话终止
    DEBUG_EVENT_PAUSE,            // 调试暂停
    DEBUG_EVENT_RESUME,           // 调试恢复
    DEBUG_EVENT_STEP,             // 单步执行
    DEBUG_EVENT_BREAKPOINT_HIT,   // 断点命中
    DEBUG_EVENT_BREAKPOINT_ADD,   // 断点添加
    DEBUG_EVENT_BREAKPOINT_REMOVE,// 断点移除
    DEBUG_EVENT_EXCEPTION,        // 异常发生
    DEBUG_EVENT_OUTPUT,           // 程序输出
    DEBUG_EVENT_PROCESS_EXIT,     // 进程退出
    DEBUG_EVENT_PROCESS_SIGNAL,   // 进程信号
    DEBUG_EVENT_VARIABLE_CHANGE,  // 变量变更
    DEBUG_EVENT_STACK_CHANGE,     // 栈帧变更
    DEBUG_EVENT_ALL,              // 所有事件（用于注册通用处理程序）
    DEBUG_EVENT_MAX               // 标记最大事件类型（内部使用）
} DebugEventType;

// 日志级别
typedef enum {
    DEBUG_LOG_DEBUG,      // 调试级别（最详细）
    DEBUG_LOG_INFO,       // 信息级别
    DEBUG_LOG_WARNING,    // 警告级别
    DEBUG_LOG_ERROR       // 错误级别（最严重）
} DebugLogLevel;

// 调试事件结构体
typedef struct {
    DebugEventType type;     // 事件类型
    void* data;              // 事件数据（根据事件类型不同而不同）
    time_t timestamp;        // 事件发生时间戳
    Debugger* debugger;      // 相关联的调试器实例
} DebugEvent;

// 事件回调函数类型
typedef void (*DebugEventCallback)(DebugEvent* event, void* user_data);

// 日志回调函数类型
typedef void (*DebugLogCallback)(DebugLogLevel level, const char* message, void* user_data);

// 事件回调条目
typedef struct {
    DebugEventType event_type;      // 事件类型
    DebugEventCallback callback;    // 回调函数
    void* user_data;                // 用户数据
} EventCallbackEntry;

// 变量类型
typedef enum {
    VAR_TYPE_UNKNOWN,
    VAR_TYPE_INT,
    VAR_TYPE_FLOAT,
    VAR_TYPE_DOUBLE,
    VAR_TYPE_BOOL,
    VAR_TYPE_STRING,
    VAR_TYPE_ARRAY,
    VAR_TYPE_OBJECT,
    VAR_TYPE_POINTER,
    VAR_TYPE_FUNCTION,
    VAR_TYPE_QUANTUM     // 量子类型
} VariableType;

// 变量值联合体
typedef union {
    int int_val;
    float float_val;
    double double_val;
    bool bool_val;
    char* string_val;
    void* array_val;
    void* object_val;
    void* pointer_val;
    void* function_val;
    void* quantum_val;
} VariableValue;

// 变量结构
typedef struct {
    char name[MAX_VAR_NAME_LENGTH];
    VariableType type;
    VariableValue value;
    int scope_level;         // 作用域级别
    int scope_id;            // 作用域ID
    bool is_modified;        // 是否最近被修改
    bool is_expandable;      // 是否可以展开（如数组、对象）
    int children_count;      // 子变量数量（如果是可展开类型）
} Variable;

// 断点信息
typedef struct {
    int id;                  // 断点ID
    BreakpointType type;     // 断点类型
    char* file;              // 文件名
    int line;                // 行号
    char* function;          // 函数名
    char* condition;         // 条件表达式
    bool enabled;            // 是否启用
    int hit_count;           // 命中次数
} BreakpointInfo;

// 调用栈帧
typedef struct {
    char function_name[MAX_VAR_NAME_LENGTH];
    char file_path[MAX_PATH_LENGTH];
    int line_number;
    int column;
    int level;               // 栈帧级别（0是最上层）
    int locals_count;        // 局部变量数量
    Variable* locals;        // 局部变量列表
} StackFrame;

// 断点结构
typedef struct {
    int id;                   // 断点ID
    BreakpointType type;      // 断点类型
    char file_path[MAX_PATH_LENGTH];
    int line;                 // 行号（对于行断点）
    char function[MAX_VAR_NAME_LENGTH]; // 函数名（对于函数断点）
    char condition[MAX_EXPR_LENGTH];    // 条件表达式（对于条件断点）
    char data_expr[MAX_EXPR_LENGTH];    // 数据表达式（对于数据变更断点）
    bool enabled;             // 是否启用
    int hit_count;            // 命中次数
    int ignore_count;         // 忽略计数
    bool temp;                // 是否为临时断点
} Breakpoint;

// 断点检查状态
typedef struct {
    bool hit;                 // 是否命中断点
    int breakpoint_id;        // 命中的断点ID（如果hit为true）
    char message[256];        // 断点消息
} BreakpointCheckResult;

// 检查类型
typedef enum {
    INSPECTOR_NONE,
    INSPECTOR_VARIABLES,
    INSPECTOR_STACK,
    INSPECTOR_MEMORY,
    INSPECTOR_QUANTUM_STATE
} InspectorType;

// 检查器结构
typedef struct {
    InspectorType type;
    Variable* locals;
    int locals_count;
    Variable* globals;
    int globals_count;
    StackFrame* stack;
    int stack_count;
    void* memory_data;
    int memory_size;
    void* quantum_state;
} Inspector;

// 调试器统计信息
typedef struct {
    int breakpoints_count;
    int breakpoints_hit_count;
    int step_count;
    int continue_count;
    int exception_count;
    int variables_inspected;
    int expression_evaluated;
    long long start_time;
    long long total_run_time;
    long long total_pause_time;
} DebuggerStats;

// 调试器配置
typedef struct {
    bool break_on_exception;
    bool break_on_throw;
    bool break_on_error;
    bool async_mode;
    bool allow_remote;
    char remote_host[64];
    int remote_port;
    bool verbose_logging;
    bool trace_calls;
    bool quantum_inspection;
} DebuggerConfig;

// 主调试器结构
struct Debugger {
    // 基本状态
    DebuggerState state;
    Inspector* inspector;
    FILE* input_stream;
    FILE* output_stream;
    FILE* error_stream;
    
    // 断点和程序位置
    Breakpoint breakpoints[MAX_BREAKPOINTS];
    int breakpoint_count;
    int next_breakpoint_id;
    char current_file[MAX_PATH_LENGTH];
    int current_line;
    int current_column;
    
    // 进程和程序控制
    void* process_handle;
    int process_id;
    char program_path[MAX_PATH_LENGTH];
    char** program_args;
    int program_args_count;
    
    // 事件和回调
    EventCallbackEntry event_callbacks[MAX_EVENT_CALLBACKS];
    int event_count;
    DebugEvent event_history[MAX_EVENT_HISTORY];
    int event_history_count;
    int event_history_index;
    
    // 日志
    DebugLogLevel log_level;
    DebugLogCallback log_callback;
    void* log_user_data;
    char* log_history[MAX_LOG_HISTORY];
    int log_history_count;
    int log_history_index;
    FILE* log_file;
    
    // 配置和统计
    DebuggerConfig config;
    DebuggerStats stats;
    
    // 自定义用户数据
    void* user_data;
};

// 创建调试器
Debugger* debugger_create(void);

// 销毁调试器
void debugger_destroy(Debugger* debugger);

// 设置事件回调
void debugger_set_event_callback(Debugger* debugger, DebugEventCallback callback, void* user_data);

// 启动调试会话
bool debugger_start(Debugger* debugger, const char* file, const char* working_dir);

// 终止调试会话
void debugger_terminate(Debugger* debugger);

// 暂停执行
bool debugger_pause(Debugger* debugger);

// 恢复执行
bool debugger_resume(Debugger* debugger, ExecutionMode mode);

// 获取当前状态
DebuggerState debugger_get_state(Debugger* debugger);

// 获取当前行号
int debugger_get_current_line(Debugger* debugger);

// 获取当前文件
const char* debugger_get_current_file(Debugger* debugger);

// 添加断点
int debugger_add_breakpoint(Debugger* debugger, BreakpointType type, const char* file, 
                           int line, const char* function, const char* condition);

// 移除断点
bool debugger_remove_breakpoint(Debugger* debugger, int breakpoint_id);

// 启用/禁用断点
bool debugger_enable_breakpoint(Debugger* debugger, int breakpoint_id, bool enable);

// 获取断点列表
BreakpointInfo* debugger_get_breakpoints(Debugger* debugger, int* count);

// 获取当前局部变量
VariableInfo* debugger_get_local_variables(Debugger* debugger, int* count);

// 获取全局变量
VariableInfo* debugger_get_global_variables(Debugger* debugger, int* count);

// 获取调用栈
StackFrame* debugger_get_call_stack(Debugger* debugger, int* count);

// 计算表达式
char* debugger_evaluate_expression(Debugger* debugger, const char* expression);

// 获取量子状态
bool debugger_get_quantum_state(Debugger* debugger, const char* variable_name, 
                               void* state_data, int* qubit_count);

// 获取纠缠信息
bool debugger_get_entanglement_info(Debugger* debugger, const char* variable_name1, 
                                   const char* variable_name2, double* entanglement);

// 程序控制
bool debugger_start(Debugger* debugger, const char* program_path);
bool debugger_pause(Debugger* debugger);
bool debugger_resume(Debugger* debugger);
bool debugger_stop(Debugger* debugger);
bool debugger_step_into(Debugger* debugger);
bool debugger_step_over(Debugger* debugger);
bool debugger_step_out(Debugger* debugger);
bool debugger_run_to_location(Debugger* debugger, const char* file, int line);

// 断点管理
int debugger_add_breakpoint(Debugger* debugger, const char* file, int line);
int debugger_add_function_breakpoint(Debugger* debugger, const char* function_name);
int debugger_add_condition_breakpoint(Debugger* debugger, const char* file, int line, const char* condition);
bool debugger_remove_breakpoint(Debugger* debugger, int breakpoint_id);
bool debugger_enable_breakpoint(Debugger* debugger, int breakpoint_id, bool enable);
BreakpointCheckResult debugger_check_breakpoint(Debugger* debugger, const char* file, int line);
void debugger_clear_all_breakpoints(Debugger* debugger);

// 变量和表达式
Variable* debugger_find_variable(Debugger* debugger, const char* name);
bool debugger_evaluate_expression(Debugger* debugger, const char* expression, Variable* result);
void debugger_update_locals(Debugger* debugger, Variable* locals, int count);
void debugger_update_globals(Debugger* debugger, Variable* globals, int count);
Variable* debugger_get_locals(Debugger* debugger, int* count);
Variable* debugger_get_globals(Debugger* debugger, int* count);

// 调用栈管理
void debugger_update_callstack(Debugger* debugger, StackFrame* stack_frames, int count);
StackFrame* debugger_get_callstack(Debugger* debugger, int* count);

// 命令和控制
bool debugger_send_command(Debugger* debugger, const char* command);
bool debugger_set_program_args(Debugger* debugger, char** args, int count);
bool debugger_interrupt(Debugger* debugger);

// 事件处理
bool debugger_register_event_handler(Debugger* debugger, DebugEventType event_type, DebugEventCallback callback, void* user_data);
bool debugger_unregister_event_handler(Debugger* debugger, DebugEventType event_type, DebugEventCallback callback);
void debugger_trigger_event(Debugger* debugger, DebugEventType event_type, void* event_data);
const char* debugger_get_event_name(DebugEventType event_type);

// 日志管理
void debugger_set_log_level(Debugger* debugger, DebugLogLevel level);
void debugger_set_log_callback(Debugger* debugger, DebugLogCallback callback, void* user_data);
void debugger_log(Debugger* debugger, const char* format, ...);
char** debugger_get_log_history(Debugger* debugger, int* count);
void debugger_clear_log_history(Debugger* debugger);
bool debugger_set_log_file(Debugger* debugger, const char* filename);
void debugger_default_log_callback(DebugLogLevel level, const char* message, void* user_data);

// 资源和清理
void debugger_cleanup_resources(Debugger* debugger);
void debugger_get_stats(Debugger* debugger, DebuggerStats* stats);

#endif /* QENTL_DEBUGGER_CORE_H */ 