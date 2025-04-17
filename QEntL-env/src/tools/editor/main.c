/**
 * QEntL编辑器主程序
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月19日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "editor_core.h"

#define VERSION "1.0"

// 显示帮助信息
void show_help(void) {
    printf("QEntL编辑器 v%s\n", VERSION);
    printf("用法: qentl_editor [选项] [文件...]\n");
    printf("\n");
    printf("选项:\n");
    printf("  -h, --help       显示帮助信息\n");
    printf("  -v, --version    显示版本信息\n");
    printf("\n");
    printf("键盘快捷键:\n");
    printf("  Ctrl+O           打开文件\n");
    printf("  Ctrl+S           保存文件\n");
    printf("  Ctrl+Q           退出程序\n");
    printf("  F1               显示帮助\n");
}

// 显示版本信息
void show_version(void) {
    printf("QEntL编辑器 v%s\n", VERSION);
    printf("版权所有 (C) 2024 QEntL开发团队\n");
}

// 处理命令行参数
int process_arguments(int argc, char** argv, EditorState* state) {
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            show_help();
            return 0;
        } else if (strcmp(argv[i], "-v") == 0 || strcmp(argv[i], "--version") == 0) {
            show_version();
            return 0;
        } else {
            // 假设是文件路径
            if (!editor_open_file(state, argv[i])) {
                fprintf(stderr, "错误：无法打开文件 '%s'\n", argv[i]);
                return 1;
            }
        }
    }
    
    return -1; // 继续执行
}

// 显示编辑器状态信息
void display_status_bar(EditorState* state) {
    EditorStatus status;
    editor_get_status(state, &status);
    
    printf("\x1b[7m"); // 反显
    printf(" %s %s | 行: %d, 列: %d | 总行数: %d ",
           status.current_file,
           status.is_modified ? "[已修改]" : "",
           status.current_line,
           status.current_column,
           status.total_lines);
    printf("\x1b[0m"); // 恢复
    printf("\n");
}

// 处理按键回调函数
void key_press_callback(EditorState* state, EditorEventType event_type, 
                        void* event_data, void* user_data) {
    if (event_type != EDITOR_EVENT_KEY_PRESS) return;
    
    // 在实际程序中，这里会处理各种按键事件
    printf("按键事件处理\n");
}

// 运行编辑器
void run_editor(EditorState* state) {
    // 注册事件处理器
    editor_register_event_handler(state, EDITOR_EVENT_KEY_PRESS, key_press_callback, NULL);
    
    // 这是一个简化的演示，实际编辑器会有更复杂的UI和事件循环
    printf("QEntL编辑器已启动\n");
    
    // 显示状态栏
    display_status_bar(state);
    
    printf("编辑器正在运行的模拟...\n");
    printf("实际实现中，这里会有完整的终端UI和事件循环\n");
    
    // 模拟一些编辑操作
    editor_insert_text(state, "// 这是QEntL程序的示例\n");
    editor_insert_text(state, "quantum {\n");
    editor_insert_text(state, "    qstate s = create_state(2);\n");
    editor_insert_text(state, "    apply(s, H, 0);\n");
    editor_insert_text(state, "    apply(s, CNOT, 0, 1);\n");
    editor_insert_text(state, "    measure(s);\n");
    editor_insert_text(state, "}\n");
    
    // 重新显示状态栏
    display_status_bar(state);
}

// 主函数
int main(int argc, char** argv) {
    // 创建编辑器状态
    EditorState* state = editor_create();
    if (!state) {
        fprintf(stderr, "错误：无法创建编辑器状态\n");
        return 1;
    }
    
    // 处理命令行参数
    int result = process_arguments(argc, argv, state);
    if (result >= 0) {
        editor_destroy(state);
        return result;
    }
    
    // 如果没有打开文件，创建一个新文件
    EditorStatus status;
    editor_get_status(state, &status);
    if (status.total_lines == 0) {
        editor_insert_text(state, "");
    }
    
    // 运行编辑器
    run_editor(state);
    
    // 清理资源
    editor_destroy(state);
    
    return 0;
} 