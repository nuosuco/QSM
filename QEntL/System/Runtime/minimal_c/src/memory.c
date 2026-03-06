// QEntL最小化运行时 - 内存管理模块
// 实现完全自主的内存管理，支持垃圾收集

#include "runtime.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// ==================== 全局内存统计 ====================

static size_t total_allocated = 0;
static size_t peak_allocated = 0;
static size_t gc_threshold = 1024 * 1024; // 1MB默认阈值

// ==================== 基础内存分配 ====================

void* runtime_alloc(size_t size) {
    if (size == 0) return NULL;
    
    void* ptr = malloc(size);
    if (ptr == NULL) {
        fprintf(stderr, "内存分配失败: 请求 %zu 字节\n", size);
        return NULL;
    }
    
    total_allocated += size;
    if (total_allocated > peak_allocated) {
        peak_allocated = total_allocated;
    }
    
    // 检查是否需要垃圾收集
    if (total_allocated > gc_threshold) {
        // 这里将来会触发垃圾收集
        // runtime_gc_collect();
    }
    
    return ptr;
}

void* runtime_realloc(void* ptr, size_t new_size) {
    if (ptr == NULL) {
        return runtime_alloc(new_size);
    }
    
    // 获取旧大小（简化处理，实际需要跟踪分配大小）
    // 这里简化：假设每次重新分配都调整统计
    // 实际实现应该跟踪每个分配的大小
    
    void* new_ptr = realloc(ptr, new_size);
    if (new_ptr == NULL) {
        fprintf(stderr, "内存重新分配失败: 请求 %zu 字节\n", new_size);
        return NULL;
    }
    
    // 简化统计：无法准确知道旧大小，所以不调整total_allocated
    // 实际实现需要更精确的跟踪
    
    return new_ptr;
}

void runtime_free(void* ptr) {
    if (ptr == NULL) return;
    
    free(ptr);
    // 简化：不减少total_allocated，因为不知道大小
    // 实际实现需要跟踪分配大小
}

size_t runtime_get_allocated(void) {
    return total_allocated;
}

// ==================== 垃圾收集器（简化版） ====================

// 垃圾收集器状态
typedef struct {
    size_t collected_bytes;
    size_t collection_count;
    bool tracing;  // 是否正在跟踪
} GCState;

static GCState gc_state = {0, 0, false};

void runtime_gc_collect(void) {
    if (gc_state.tracing) {
        return; // 防止递归
    }
    
    gc_state.tracing = true;
    gc_state.collection_count++;
    
    // 标记阶段：标记所有可达对象
    // 简化实现：暂时只打印信息
    printf("[GC] 开始垃圾收集 (已分配: %zu bytes)\n", total_allocated);
    
    // 清除阶段：释放未标记对象
    // 简化实现：暂时不实际释放
    
    gc_state.tracing = false;
    
    // 调整下一次收集阈值
    gc_threshold = total_allocated * 2;
    printf("[GC] 收集完成，新阈值: %zu bytes\n", gc_threshold);
}

// ==================== 专用分配器 ====================

// 字符串分配器（带长度前缀）
char* runtime_alloc_string(size_t length) {
    // 分配：长度前缀 + 字符 + 空终止符
    char* str = (char*)runtime_alloc(length + sizeof(size_t) + 1);
    if (str == NULL) return NULL;
    
    // 在字符串前存储长度
    size_t* len_ptr = (size_t*)str;
    *len_ptr = length;
    
    // 返回字符部分指针
    char* chars = str + sizeof(size_t);
    chars[length] = '\0'; // 确保空终止
    
    return chars;
}

// 获取字符串长度（从长度前缀）
size_t runtime_string_length(const char* str) {
    if (str == NULL) return 0;
    size_t* len_ptr = (size_t*)(str - sizeof(size_t));
    return *len_ptr;
}

// 释放字符串
void runtime_free_string(char* str) {
    if (str == NULL) {
        printf("[runtime_free_string] 字符串指针为NULL\n");
        return;
    }
    printf("[runtime_free_string] 释放字符串内存: %p (完整指针: %p)\n", 
           str, str - sizeof(size_t));
    runtime_free(str - sizeof(size_t));
}

// ==================== 数组分配器 ====================

// 分配值数组
Value* runtime_alloc_value_array(size_t count) {
    return (Value*)runtime_alloc(sizeof(Value) * count);
}

// 重新分配值数组
Value* runtime_realloc_value_array(Value* array, size_t new_count) {
    return (Value*)runtime_realloc(array, sizeof(Value) * new_count);
}

// ==================== 内存调试 ====================

void runtime_print_memory_stats(void) {
    printf("=== 内存统计 ===\n");
    printf("当前分配: %zu bytes\n", total_allocated);
    printf("峰值分配: %zu bytes\n", peak_allocated);
    printf("GC阈值:   %zu bytes\n", gc_threshold);
    printf("GC收集次数: %zu\n", gc_state.collection_count);
    printf("GC回收字节: %zu\n", gc_state.collected_bytes);
    printf("================\n");
}