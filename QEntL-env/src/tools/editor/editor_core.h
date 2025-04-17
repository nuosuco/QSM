/**
 * QEntL编辑器核心头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月19日
 */

#ifndef QENTL_EDITOR_CORE_H
#define QENTL_EDITOR_CORE_H

#include <stdbool.h>

// 编辑器配置结构
typedef struct {
    int tab_size;                // Tab字符宽度
    bool auto_indent;            // 自动缩进
    bool syntax_highlight;       // 语法高亮
    bool line_numbers;           // 显示行号
} EditorConfig;

// 编辑器状态信息结构
typedef struct {
    int current_line;            // 当前行号
    int current_column;          // 当前列号
    int total_lines;             // 总行数
    bool is_modified;            // 是否已修改
    const char* current_file;    // 当前文件路径
} EditorStatus;

// 编辑器事件类型
typedef enum {
    EDITOR_EVENT_KEY_PRESS,      // 按键事件
    EDITOR_EVENT_TEXT_CHANGED,   // 文本变更事件
    EDITOR_EVENT_CURSOR_MOVED,   // 光标移动事件
    EDITOR_EVENT_FILE_OPENED,    // 文件打开事件
    EDITOR_EVENT_FILE_SAVED,     // 文件保存事件
    EDITOR_EVENT_CONFIG_CHANGED  // 配置变更事件
} EditorEventType;

// 前置声明
typedef struct EditorState EditorState;

// 编辑器事件回调函数类型
typedef void (*EditorEventCallback)(EditorState* state, EditorEventType event_type, 
                                   void* event_data, void* user_data);

// 编辑器事件处理器结构
typedef struct {
    EditorEventType event_type;    // 事件类型
    EditorEventCallback callback;  // 回调函数
    void* user_data;               // 用户数据
} EditorEventHandler;

// 创建编辑器状态
EditorState* editor_create(void);

// 销毁编辑器状态
void editor_destroy(EditorState* state);

// 打开文件
bool editor_open_file(EditorState* state, const char* file_path);

// 保存文件
bool editor_save_file(EditorState* state, const char* file_path);

// 获取当前行内容
const char* editor_get_current_line(EditorState* state);

// 设置光标位置
bool editor_set_cursor(EditorState* state, int line, int column);

// 插入文本
bool editor_insert_text(EditorState* state, const char* text);

// 删除字符
bool editor_delete_char(EditorState* state, bool is_backspace);

// 获取编辑器状态信息
void editor_get_status(EditorState* state, EditorStatus* status);

// 注册事件处理器
bool editor_register_event_handler(EditorState* state, EditorEventType event_type, 
                                  EditorEventCallback callback, void* user_data);

// 触发事件
void editor_trigger_event(EditorState* state, EditorEventType event_type, void* event_data);

// 设置编辑器配置
void editor_set_config(EditorState* state, const EditorConfig* config);

// 获取编辑器配置
void editor_get_config(EditorState* state, EditorConfig* config);

#endif /* QENTL_EDITOR_CORE_H */ 