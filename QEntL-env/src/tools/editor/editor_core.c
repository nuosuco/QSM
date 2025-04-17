/**
 * QEntL编辑器核心实现
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月19日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include "editor_core.h"

#define MAX_LINE_LENGTH 1024
#define DEFAULT_BUFFER_SIZE 1024

// 编辑器缓冲区结构
typedef struct {
    char** lines;         // 文件内容行
    int line_count;       // 总行数
    int capacity;         // 缓冲区容量
    char* file_path;      // 当前文件路径
    bool is_modified;     // 是否已修改
} EditorBuffer;

// 光标位置结构
typedef struct {
    int line;             // 当前行
    int column;           // 当前列
} CursorPosition;

// 编辑器状态结构
struct EditorState {
    EditorBuffer buffer;          // 编辑缓冲区
    CursorPosition cursor;        // 光标位置
    int scroll_offset;            // 滚动偏移
    EditorConfig config;          // 编辑器配置
    EditorEventHandler* event_handlers; // 事件处理器
    int event_handler_count;      // 事件处理器数量
};

// 创建编辑器状态
EditorState* editor_create(void) {
    printf("创建QEntL编辑器...\n");
    
    EditorState* state = (EditorState*)malloc(sizeof(EditorState));
    if (!state) {
        fprintf(stderr, "错误：无法分配编辑器状态内存\n");
        return NULL;
    }
    
    // 初始化缓冲区
    state->buffer.lines = (char**)malloc(DEFAULT_BUFFER_SIZE * sizeof(char*));
    if (!state->buffer.lines) {
        fprintf(stderr, "错误：无法分配缓冲区内存\n");
        free(state);
        return NULL;
    }
    
    state->buffer.line_count = 0;
    state->buffer.capacity = DEFAULT_BUFFER_SIZE;
    state->buffer.file_path = NULL;
    state->buffer.is_modified = false;
    
    // 初始化光标位置
    state->cursor.line = 0;
    state->cursor.column = 0;
    
    // 初始化滚动偏移
    state->scroll_offset = 0;
    
    // 初始化配置
    state->config.tab_size = 4;
    state->config.auto_indent = true;
    state->config.syntax_highlight = true;
    state->config.line_numbers = true;
    
    // 初始化事件处理器
    state->event_handlers = NULL;
    state->event_handler_count = 0;
    
    printf("编辑器创建成功\n");
    return state;
}

// 销毁编辑器状态
void editor_destroy(EditorState* state) {
    if (!state) return;
    
    // 清理缓冲区
    if (state->buffer.lines) {
        for (int i = 0; i < state->buffer.line_count; i++) {
            free(state->buffer.lines[i]);
        }
        free(state->buffer.lines);
    }
    
    // 清理文件路径
    if (state->buffer.file_path) {
        free(state->buffer.file_path);
    }
    
    // 清理事件处理器
    if (state->event_handlers) {
        free(state->event_handlers);
    }
    
    // 清理编辑器状态
    free(state);
    
    printf("编辑器已销毁\n");
}

// 打开文件
bool editor_open_file(EditorState* state, const char* file_path) {
    if (!state || !file_path) return false;
    
    FILE* file = fopen(file_path, "r");
    if (!file) {
        fprintf(stderr, "错误：无法打开文件 %s\n", file_path);
        return false;
    }
    
    // 清理当前缓冲区
    for (int i = 0; i < state->buffer.line_count; i++) {
        free(state->buffer.lines[i]);
    }
    state->buffer.line_count = 0;
    
    // 读取文件内容
    char line[MAX_LINE_LENGTH];
    while (fgets(line, MAX_LINE_LENGTH, file)) {
        // 移除换行符
        size_t len = strlen(line);
        if (len > 0 && (line[len-1] == '\n' || line[len-1] == '\r')) {
            line[len-1] = '\0';
            if (len > 1 && line[len-2] == '\r') {
                line[len-2] = '\0';
            }
        }
        
        // 检查缓冲区容量是否需要扩展
        if (state->buffer.line_count >= state->buffer.capacity) {
            int new_capacity = state->buffer.capacity * 2;
            char** new_lines = (char**)realloc(state->buffer.lines, new_capacity * sizeof(char*));
            if (!new_lines) {
                fprintf(stderr, "错误：无法扩展缓冲区容量\n");
                fclose(file);
                return false;
            }
            state->buffer.lines = new_lines;
            state->buffer.capacity = new_capacity;
        }
        
        // 添加行到缓冲区
        state->buffer.lines[state->buffer.line_count] = strdup(line);
        state->buffer.line_count++;
    }
    
    fclose(file);
    
    // 更新文件路径
    if (state->buffer.file_path) {
        free(state->buffer.file_path);
    }
    state->buffer.file_path = strdup(file_path);
    
    // 重置光标位置和修改标志
    state->cursor.line = 0;
    state->cursor.column = 0;
    state->buffer.is_modified = false;
    
    printf("文件已加载: %s (共 %d 行)\n", file_path, state->buffer.line_count);
    return true;
}

// 保存文件
bool editor_save_file(EditorState* state, const char* file_path) {
    if (!state) return false;
    
    const char* path_to_use = file_path ? file_path : state->buffer.file_path;
    if (!path_to_use) {
        fprintf(stderr, "错误：未指定保存路径\n");
        return false;
    }
    
    FILE* file = fopen(path_to_use, "w");
    if (!file) {
        fprintf(stderr, "错误：无法写入文件 %s\n", path_to_use);
        return false;
    }
    
    // 写入缓冲区内容到文件
    for (int i = 0; i < state->buffer.line_count; i++) {
        fprintf(file, "%s\n", state->buffer.lines[i]);
    }
    
    fclose(file);
    
    // 如果是新文件路径，更新当前文件路径
    if (file_path && (!state->buffer.file_path || strcmp(file_path, state->buffer.file_path) != 0)) {
        if (state->buffer.file_path) {
            free(state->buffer.file_path);
        }
        state->buffer.file_path = strdup(file_path);
    }
    
    // 重置修改标志
    state->buffer.is_modified = false;
    
    printf("文件已保存: %s\n", path_to_use);
    return true;
}

// 获取当前行内容
const char* editor_get_current_line(EditorState* state) {
    if (!state || state->cursor.line >= state->buffer.line_count) {
        return NULL;
    }
    
    return state->buffer.lines[state->cursor.line];
}

// 设置光标位置
bool editor_set_cursor(EditorState* state, int line, int column) {
    if (!state) return false;
    
    // 检查行范围
    if (line < 0) line = 0;
    if (line >= state->buffer.line_count) line = state->buffer.line_count - 1;
    
    // 检查列范围
    if (column < 0) column = 0;
    if (line >= 0 && line < state->buffer.line_count) {
        int max_column = strlen(state->buffer.lines[line]);
        if (column > max_column) column = max_column;
    }
    
    state->cursor.line = line;
    state->cursor.column = column;
    
    return true;
}

// 插入文本
bool editor_insert_text(EditorState* state, const char* text) {
    if (!state || !text) return false;
    
    // 确保有至少一行
    if (state->buffer.line_count == 0) {
        if (state->buffer.capacity == 0) {
            state->buffer.lines = (char**)malloc(DEFAULT_BUFFER_SIZE * sizeof(char*));
            if (!state->buffer.lines) return false;
            state->buffer.capacity = DEFAULT_BUFFER_SIZE;
        }
        state->buffer.lines[0] = strdup("");
        state->buffer.line_count = 1;
    }
    
    // 获取当前行
    char* current_line = state->buffer.lines[state->cursor.line];
    int cur_len = strlen(current_line);
    
    // 判断是否包含换行符
    if (strchr(text, '\n') == NULL) {
        // 简单插入文本到当前行
        char* new_line = (char*)malloc(cur_len + strlen(text) + 1);
        if (!new_line) return false;
        
        // 复制前半部分
        strncpy(new_line, current_line, state->cursor.column);
        new_line[state->cursor.column] = '\0';
        
        // 添加新文本
        strcat(new_line, text);
        
        // 添加后半部分
        strcat(new_line, current_line + state->cursor.column);
        
        // 替换当前行
        free(current_line);
        state->buffer.lines[state->cursor.line] = new_line;
        
        // 更新光标位置
        state->cursor.column += strlen(text);
    } else {
        // TODO: 处理多行插入
        fprintf(stderr, "尚未实现多行插入功能\n");
        return false;
    }
    
    state->buffer.is_modified = true;
    return true;
}

// 删除字符
bool editor_delete_char(EditorState* state, bool is_backspace) {
    if (!state || state->buffer.line_count == 0) return false;
    
    int cur_line = state->cursor.line;
    int cur_col = state->cursor.column;
    char* line = state->buffer.lines[cur_line];
    int line_len = strlen(line);
    
    if (is_backspace) {
        // 向后删除
        if (cur_col > 0) {
            // 从当前行中删除前一个字符
            memmove(line + cur_col - 1, line + cur_col, line_len - cur_col + 1);
            state->cursor.column--;
            state->buffer.is_modified = true;
            return true;
        } else if (cur_line > 0) {
            // 将当前行与前一行合并
            char* prev_line = state->buffer.lines[cur_line - 1];
            int prev_len = strlen(prev_line);
            
            // 创建合并后的新行
            char* new_line = (char*)malloc(prev_len + line_len + 1);
            if (!new_line) return false;
            
            strcpy(new_line, prev_line);
            strcat(new_line, line);
            
            // 更新前一行，删除当前行
            free(prev_line);
            free(line);
            state->buffer.lines[cur_line - 1] = new_line;
            
            // 移动后续行
            for (int i = cur_line; i < state->buffer.line_count - 1; i++) {
                state->buffer.lines[i] = state->buffer.lines[i + 1];
            }
            state->buffer.line_count--;
            
            // 更新光标位置
            state->cursor.line = cur_line - 1;
            state->cursor.column = prev_len;
            
            state->buffer.is_modified = true;
            return true;
        }
    } else {
        // 向前删除
        if (cur_col < line_len) {
            // 从当前行中删除字符
            memmove(line + cur_col, line + cur_col + 1, line_len - cur_col);
            state->buffer.is_modified = true;
            return true;
        } else if (cur_line < state->buffer.line_count - 1) {
            // 将下一行合并到当前行
            char* next_line = state->buffer.lines[cur_line + 1];
            
            // 扩展当前行
            char* new_line = (char*)realloc(line, line_len + strlen(next_line) + 1);
            if (!new_line) return false;
            
            strcat(new_line, next_line);
            state->buffer.lines[cur_line] = new_line;
            
            // 移动后续行
            free(next_line);
            for (int i = cur_line + 1; i < state->buffer.line_count - 1; i++) {
                state->buffer.lines[i] = state->buffer.lines[i + 1];
            }
            state->buffer.line_count--;
            
            state->buffer.is_modified = true;
            return true;
        }
    }
    
    return false;
}

// 获取编辑器状态信息
void editor_get_status(EditorState* state, EditorStatus* status) {
    if (!state || !status) return;
    
    status->current_line = state->cursor.line + 1; // 1-based for display
    status->current_column = state->cursor.column + 1;
    status->total_lines = state->buffer.line_count;
    status->is_modified = state->buffer.is_modified;
    status->current_file = state->buffer.file_path ? state->buffer.file_path : "[未命名]";
}

// 注册事件处理器
bool editor_register_event_handler(EditorState* state, EditorEventType event_type, 
                                  EditorEventCallback callback, void* user_data) {
    if (!state || !callback) return false;
    
    // 扩展事件处理器数组
    EditorEventHandler* new_handlers = (EditorEventHandler*)realloc(
        state->event_handlers, 
        (state->event_handler_count + 1) * sizeof(EditorEventHandler)
    );
    
    if (!new_handlers) return false;
    
    state->event_handlers = new_handlers;
    
    // 添加新的事件处理器
    state->event_handlers[state->event_handler_count].event_type = event_type;
    state->event_handlers[state->event_handler_count].callback = callback;
    state->event_handlers[state->event_handler_count].user_data = user_data;
    state->event_handler_count++;
    
    return true;
}

// 触发事件
void editor_trigger_event(EditorState* state, EditorEventType event_type, void* event_data) {
    if (!state) return;
    
    for (int i = 0; i < state->event_handler_count; i++) {
        if (state->event_handlers[i].event_type == event_type) {
            state->event_handlers[i].callback(state, event_type, event_data, 
                                              state->event_handlers[i].user_data);
        }
    }
}

// 设置编辑器配置
void editor_set_config(EditorState* state, const EditorConfig* config) {
    if (!state || !config) return;
    
    state->config = *config;
    
    // 触发配置变更事件
    editor_trigger_event(state, EDITOR_EVENT_CONFIG_CHANGED, NULL);
}

// 获取编辑器配置
void editor_get_config(EditorState* state, EditorConfig* config) {
    if (!state || !config) return;
    
    *config = state->config;
} 