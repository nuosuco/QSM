// QEntL运行时 - 内存管理实现
// 版本: 1.0.0

#include "qentl_runtime.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// ============================================================================
// 内存调试配置
// ============================================================================

// 启用内存调试（开发阶段启用，生产阶段禁用）
#define MEMORY_DEBUG 1

// 内存块头部（用于调试）
typedef struct MemoryBlockHeader {
    size_t size;
    const char* file;
    int line;
    struct MemoryBlockHeader* next;
    struct MemoryBlockHeader* prev;
} MemoryBlockHeader;

// 内存统计
typedef struct {
    size_t total_allocated;
    size_t total_freed;
    size_t current_used;
    size_t peak_used;
    size_t allocation_count;
    size_t free_count;
} MemoryStats;

// 全局内存状态
static struct {
    MemoryBlockHeader* head;
    MemoryBlockHeader* tail;
    MemoryStats stats;
    bool initialized;
} g_memory_state = {0};

// ============================================================================
// 内部工具函数
// ============================================================================

static void memory_stats_init(void) {
    memset(&g_memory_state.stats, 0, sizeof(MemoryStats));
    g_memory_state.head = NULL;
    g_memory_state.tail = NULL;
    g_memory_state.initialized = true;
}

static void memory_stats_update_allocation(size_t size) {
    g_memory_state.stats.total_allocated += size;
    g_memory_state.stats.current_used += size;
    g_memory_state.stats.allocation_count++;
    
    if (g_memory_state.stats.current_used > g_memory_state.stats.peak_used) {
        g_memory_state.stats.peak_used = g_memory_state.stats.current_used;
    }
}

static void memory_stats_update_free(size_t size) {
    g_memory_state.stats.total_freed += size;
    g_memory_state.stats.current_used -= size;
    g_memory_state.stats.free_count++;
}

#if MEMORY_DEBUG
static void memory_block_link(MemoryBlockHeader* header) {
    header->next = NULL;
    header->prev = g_memory_state.tail;
    
    if (g_memory_state.tail) {
        g_memory_state.tail->next = header;
    }
    g_memory_state.tail = header;
    
    if (!g_memory_state.head) {
        g_memory_state.head = header;
    }
}

static void memory_block_unlink(MemoryBlockHeader* header) {
    if (header->prev) {
        header->prev->next = header->next;
    } else {
        g_memory_state.head = header->next;
    }
    
    if (header->next) {
        header->next->prev = header->prev;
    } else {
        g_memory_state.tail = header->prev;
    }
}

static void memory_debug_print_block(MemoryBlockHeader* header) {
    printf("  [%p] size=%zu, file=%s, line=%d\n",
           (void*)(header + 1),
           header->size,
           header->file ? header->file : "(unknown)",
           header->line);
}
#endif

// ============================================================================
// 公共API实现
// ============================================================================

void qentl_memory_init(void) {
    if (!g_memory_state.initialized) {
        memory_stats_init();
        printf("[内存] 内存系统初始化完成\n");
    }
}

void qentl_memory_cleanup(void) {
    if (!g_memory_state.initialized) {
        return;
    }
    
#if MEMORY_DEBUG
    // 检查内存泄漏
    if (g_memory_state.head != NULL) {
        printf("\n⚠️  [内存] 检测到内存泄漏！\n");
        printf("  未释放的内存块：\n");
        
        MemoryBlockHeader* current = g_memory_state.head;
        size_t leak_count = 0;
        size_t leak_size = 0;
        
        while (current != NULL) {
            memory_debug_print_block(current);
            leak_count++;
            leak_size += current->size;
            current = current->next;
        }
        
        printf("  总计: %zu 个块, %zu 字节\n", leak_count, leak_size);
    }
    
    // 打印内存统计
    printf("\n[内存] 内存使用统计:\n");
    printf("  总分配: %zu 字节\n", g_memory_state.stats.total_allocated);
    printf("  总释放: %zu 字节\n", g_memory_state.stats.total_freed);
    printf("  当前使用: %zu 字节\n", g_memory_state.stats.current_used);
    printf("  峰值使用: %zu 字节\n", g_memory_state.stats.peak_used);
    printf("  分配次数: %zu\n", g_memory_state.stats.allocation_count);
    printf("  释放次数: %zu\n", g_memory_state.stats.free_count);
#endif
    
    g_memory_state.initialized = false;
    printf("[内存] 内存系统清理完成\n");
}

void* qentl_alloc(size_t size) {
    if (size == 0) {
        return NULL;
    }
    
    if (!g_memory_state.initialized) {
        memory_stats_init();
    }
    
#if MEMORY_DEBUG
    // 调试版本：添加头部信息
    size_t total_size = sizeof(MemoryBlockHeader) + size;
    MemoryBlockHeader* header = (MemoryBlockHeader*)malloc(total_size);
    
    if (header == NULL) {
        printf("❌ [内存] 分配失败: size=%zu\n", size);
        return NULL;
    }
    
    header->size = size;
    header->file = NULL;  // 调用者可以设置
    header->line = 0;
    
    memory_block_link(header);
    memory_stats_update_allocation(size);
    
    void* ptr = (void*)(header + 1);
    // printf("[内存] 分配: %p (%zu 字节)\n", ptr, size);
    
    return ptr;
#else
    // 生产版本：直接分配
    void* ptr = malloc(size);
    
    if (ptr == NULL) {
        printf("❌ [内存] 分配失败: size=%zu\n", size);
        return NULL;
    }
    
    memory_stats_update_allocation(size);
    return ptr;
#endif
}

void* qentl_calloc(size_t count, size_t size) {
    size_t total_size = count * size;
    void* ptr = qentl_alloc(total_size);
    
    if (ptr != NULL) {
        memset(ptr, 0, total_size);
    }
    
    return ptr;
}

void* qentl_realloc(void* ptr, size_t new_size) {
    if (new_size == 0) {
        qentl_free(ptr);
        return NULL;
    }
    
    if (ptr == NULL) {
        return qentl_alloc(new_size);
    }
    
#if MEMORY_DEBUG
    // 调试版本：处理头部
    MemoryBlockHeader* old_header = ((MemoryBlockHeader*)ptr) - 1;
    size_t old_size = old_header->size;
    
    // 分配新块
    size_t total_size = sizeof(MemoryBlockHeader) + new_size;
    MemoryBlockHeader* new_header = (MemoryBlockHeader*)realloc(old_header, total_size);
    
    if (new_header == NULL) {
        printf("❌ [内存] 重新分配失败: ptr=%p, new_size=%zu\n", ptr, new_size);
        return NULL;
    }
    
    // 更新链表
    if (old_header != new_header) {
        memory_block_unlink(old_header);
        memory_block_link(new_header);
    }
    
    new_header->size = new_size;
    
    // 更新统计
    if (new_size > old_size) {
        memory_stats_update_allocation(new_size - old_size);
    } else {
        memory_stats_update_free(old_size - new_size);
    }
    
    void* new_ptr = (void*)(new_header + 1);
    // printf("[内存] 重新分配: %p -> %p (%zu -> %zu 字节)\n", ptr, new_ptr, old_size, new_size);
    
    return new_ptr;
#else
    // 生产版本：直接重新分配
    void* new_ptr = realloc(ptr, new_size);
    
    if (new_ptr == NULL) {
        printf("❌ [内存] 重新分配失败: ptr=%p, new_size=%zu\n", ptr, new_size);
        return NULL;
    }
    
    // 注意：我们不知道旧大小，所以无法准确更新统计
    // 这里简化处理：假设重新分配不影响统计
    return new_ptr;
#endif
}

void qentl_free(void* ptr) {
    if (ptr == NULL) {
        return;
    }
    
#if MEMORY_DEBUG
    MemoryBlockHeader* header = ((MemoryBlockHeader*)ptr) - 1;
    size_t size = header->size;
    
    // 从链表移除
    memory_block_unlink(header);
    memory_stats_update_free(size);
    
    // printf("[内存] 释放: %p (%zu 字节)\n", ptr, size);
    free(header);
#else
    // 生产版本：直接释放
    free(ptr);
    
    // 注意：我们不知道大小，所以无法准确更新统计
#endif
}

size_t qentl_memory_used(void) {
    return g_memory_state.stats.current_used;
}

// ============================================================================
// 调试函数
// ============================================================================

#if MEMORY_DEBUG
void qentl_memory_dump(void) {
    printf("\n[内存] 当前内存块:\n");
    
    MemoryBlockHeader* current = g_memory_state.head;
    size_t block_count = 0;
    
    while (current != NULL) {
        memory_debug_print_block(current);
        block_count++;
        current = current->next;
    }
    
    if (block_count == 0) {
        printf("  (无)\n");
    }
    
    printf("  总计: %zu 个块, %zu 字节\n", block_count, g_memory_state.stats.current_used);
}

void qentl_memory_set_debug_info(void* ptr, const char* file, int line) {
#if MEMORY_DEBUG
    if (ptr != NULL) {
        MemoryBlockHeader* header = ((MemoryBlockHeader*)ptr) - 1;
        header->file = file;
        header->line = line;
    }
#endif
}
#endif