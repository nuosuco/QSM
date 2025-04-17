/**
 * QEntL事件系统实现
 * 
 * 量子基因编码: QG-RUNTIME-EVTSYS-E5F9-1713051200
 * 
 * @文件: event_system.c
 * @描述: 实现QEntL运行时的事件处理系统
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-16
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 事件系统支持量子事件发布和订阅机制
 * - 支持量子纠缠触发的事件传播和叠加
 */

#include "event_system.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* 事件处理器内部结构 */
struct EventHandler {
    EventCallback callback;           /* 回调函数 */
    void* user_data;                  /* 用户数据 */
    int priority;                     /* 优先级 */
    EventMask event_mask;             /* 事件掩码 */
    int is_active;                    /* 是否激活 */
};

/* 事件系统内部结构 */
struct EventSystem {
    EventHandler** handlers;          /* 处理器数组 */
    int handler_count;                /* 处理器数量 */
    int handler_capacity;             /* 处理器容量 */
    
    QEntLEvent* event_queue;          /* 事件队列 */
    int queue_head;                   /* 队列头 */
    int queue_tail;                   /* 队列尾 */
    int queue_capacity;               /* 队列容量 */
    int events_in_queue;              /* 队列中的事件数量 */
    
    int is_processing;                /* 是否正在处理事件 */
    int deferred_count;               /* 延迟处理的事件数量 */
    
    EventStats stats;                 /* 统计数据 */
};

/* 创建事件系统 */
EventSystem* event_system_create(void) {
    EventSystem* system = (EventSystem*)malloc(sizeof(EventSystem));
    if (!system) {
        return NULL;
    }
    
    /* 初始化处理器数组 */
    system->handler_capacity = 16;
    system->handlers = (EventHandler**)malloc(system->handler_capacity * sizeof(EventHandler*));
    if (!system->handlers) {
        free(system);
        return NULL;
    }
    system->handler_count = 0;
    
    /* 初始化事件队列 */
    system->queue_capacity = 64;
    system->event_queue = (QEntLEvent*)malloc(system->queue_capacity * sizeof(QEntLEvent));
    if (!system->event_queue) {
        free(system->handlers);
        free(system);
        return NULL;
    }
    system->queue_head = 0;
    system->queue_tail = 0;
    system->events_in_queue = 0;
    
    /* 初始化其他属性 */
    system->is_processing = 0;
    system->deferred_count = 0;
    
    /* 初始化统计数据 */
    memset(&system->stats, 0, sizeof(EventStats));
    system->stats.system_start_time = time(NULL);
    
    return system;
}

/* 销毁事件系统 */
void event_system_destroy(EventSystem* system) {
    if (!system) {
        return;
    }
    
    /* 释放所有处理器 */
    for (int i = 0; i < system->handler_count; i++) {
        free(system->handlers[i]);
    }
    
    /* 释放资源 */
    free(system->event_queue);
    free(system->handlers);
    free(system);
}

/* 添加事件处理器 */
EventHandler* event_system_add_handler(EventSystem* system, EventCallback callback, 
                                    void* user_data, int priority, EventMask event_mask) {
    if (!system || !callback) {
        return NULL;
    }
    
    /* 检查容量并扩展 */
    if (system->handler_count >= system->handler_capacity) {
        int new_capacity = system->handler_capacity * 2;
        EventHandler** new_handlers = (EventHandler**)realloc(
            system->handlers, new_capacity * sizeof(EventHandler*));
        
        if (!new_handlers) {
            return NULL;
        }
        
        system->handlers = new_handlers;
        system->handler_capacity = new_capacity;
    }
    
    /* 创建新处理器 */
    EventHandler* handler = (EventHandler*)malloc(sizeof(EventHandler));
    if (!handler) {
        return NULL;
    }
    
    handler->callback = callback;
    handler->user_data = user_data;
    handler->priority = priority;
    handler->event_mask = event_mask;
    handler->is_active = 1;
    
    /* 添加到数组 */
    system->handlers[system->handler_count++] = handler;
    
    /* 按优先级排序处理器数组 */
    sort_handlers_by_priority(system);
    
    return handler;
}

/* 移除事件处理器 */
int event_system_remove_handler(EventSystem* system, EventHandler* handler) {
    if (!system || !handler) {
        return 0;
    }
    
    /* 查找处理器 */
    int pos = -1;
    for (int i = 0; i < system->handler_count; i++) {
        if (system->handlers[i] == handler) {
            pos = i;
            break;
        }
    }
    
    if (pos < 0) {
        return 0; /* 未找到 */
    }
    
    /* 释放处理器 */
    free(handler);
    
    /* 移动数组元素 */
    for (int i = pos; i < system->handler_count - 1; i++) {
        system->handlers[i] = system->handlers[i + 1];
    }
    
    system->handler_count--;
    return 1;
}

/* 发送事件 */
int event_system_emit(EventSystem* system, EventType type, void* source, void* data, int flags) {
    if (!system) {
        return 0;
    }
    
    /* 创建事件 */
    QEntLEvent event;
    event.type = type;
    event.source = source;
    event.data = data;
    event.timestamp = time(NULL);
    event.flags = flags;
    event.processed = 0;
    
    /* 检查队列是否已满 */
    if (system->events_in_queue >= system->queue_capacity) {
        /* 尝试扩展队列 */
        if (!expand_event_queue(system)) {
            /* 队列已满且无法扩展 */
            system->stats.dropped_events++;
            return 0;
        }
    }
    
    /* 添加到队列尾部 */
    system->event_queue[system->queue_tail] = event;
    system->queue_tail = (system->queue_tail + 1) % system->queue_capacity;
    system->events_in_queue++;
    
    /* 更新统计 */
    system->stats.total_events++;
    
    /* 如果未在处理且事件需要立即处理 */
    if (!system->is_processing && !(flags & EVENT_FLAG_DEFERRED)) {
        return event_system_process_events(system);
    }
    
    return 1;
}

/* 处理队列中的事件 */
int event_system_process_events(EventSystem* system) {
    if (!system || system->is_processing) {
        return 0;
    }
    
    system->is_processing = 1;
    int processed = 0;
    
    /* 记录处理开始时间 */
    time_t start_time = time(NULL);
    
    /* 处理队列中的所有事件 */
    while (system->events_in_queue > 0) {
        /* 获取队列头部的事件 */
        QEntLEvent event = system->event_queue[system->queue_head];
        system->queue_head = (system->queue_head + 1) % system->queue_capacity;
        system->events_in_queue--;
        
        /* 如果是延迟事件且当前已启动延迟处理 */
        if ((event.flags & EVENT_FLAG_DEFERRED) && system->deferred_count == 0) {
            /* 跳过此事件 */
            continue;
        }
        
        /* 分发事件到处理器 */
        int handler_count = dispatch_event(system, &event);
        
        if (handler_count > 0) {
            processed++;
            
            /* 更新统计 */
            system->stats.processed_events++;
        }
    }
    
    /* 更新处理时间统计 */
    system->stats.total_processing_time += difftime(time(NULL), start_time);
    
    system->is_processing = 0;
    return processed;
}

/* 处理延迟事件 */
int event_system_process_deferred(EventSystem* system) {
    if (!system) {
        return 0;
    }
    
    /* 标记正在处理延迟事件 */
    system->deferred_count++;
    
    /* 处理所有事件（包括延迟事件） */
    int result = event_system_process_events(system);
    
    /* 结束延迟事件处理 */
    system->deferred_count--;
    
    return result;
}

/* 激活处理器 */
void event_system_activate_handler(EventSystem* system, EventHandler* handler) {
    if (!system || !handler) {
        return;
    }
    
    handler->is_active = 1;
}

/* 停用处理器 */
void event_system_deactivate_handler(EventSystem* system, EventHandler* handler) {
    if (!system || !handler) {
        return;
    }
    
    handler->is_active = 0;
}

/* 获取统计数据 */
EventStats event_system_get_stats(EventSystem* system) {
    EventStats empty_stats;
    memset(&empty_stats, 0, sizeof(EventStats));
    
    if (!system) {
        return empty_stats;
    }
    
    return system->stats;
}

/* 清除事件队列 */
void event_system_clear_queue(EventSystem* system) {
    if (!system) {
        return;
    }
    
    system->queue_head = 0;
    system->queue_tail = 0;
    system->events_in_queue = 0;
}

/* 内部函数：按优先级排序处理器 */
static void sort_handlers_by_priority(EventSystem* system) {
    if (!system || system->handler_count <= 1) {
        return;
    }
    
    /* 简单的插入排序 */
    for (int i = 1; i < system->handler_count; i++) {
        EventHandler* key = system->handlers[i];
        int j = i - 1;
        
        while (j >= 0 && system->handlers[j]->priority < key->priority) {
            system->handlers[j + 1] = system->handlers[j];
            j--;
        }
        
        system->handlers[j + 1] = key;
    }
}

/* 内部函数：扩展事件队列 */
static int expand_event_queue(EventSystem* system) {
    if (!system) {
        return 0;
    }
    
    /* 计算新容量 */
    int new_capacity = system->queue_capacity * 2;
    
    /* 分配新队列 */
    QEntLEvent* new_queue = (QEntLEvent*)malloc(new_capacity * sizeof(QEntLEvent));
    if (!new_queue) {
        return 0;
    }
    
    /* 复制旧队列中的事件到新队列 */
    int index = 0;
    int count = system->events_in_queue;
    int head = system->queue_head;
    
    for (int i = 0; i < count; i++) {
        new_queue[i] = system->event_queue[head];
        head = (head + 1) % system->queue_capacity;
    }
    
    /* 释放旧队列 */
    free(system->event_queue);
    
    /* 更新队列信息 */
    system->event_queue = new_queue;
    system->queue_capacity = new_capacity;
    system->queue_head = 0;
    system->queue_tail = count;
    
    return 1;
}

/* 内部函数：分发事件到处理器 */
static int dispatch_event(EventSystem* system, QEntLEvent* event) {
    if (!system || !event) {
        return 0;
    }
    
    int handler_count = 0;
    
    /* 遍历所有处理器 */
    for (int i = 0; i < system->handler_count; i++) {
        EventHandler* handler = system->handlers[i];
        
        /* 检查处理器是否激活且事件类型匹配 */
        if (handler->is_active && (handler->event_mask & (1 << event->type))) {
            /* 调用处理器回调 */
            handler->callback(event, handler->user_data);
            handler_count++;
            
            /* 标记事件已处理 */
            event->processed = 1;
            
            /* 如果事件标记为已消费，停止进一步处理 */
            if (event->flags & EVENT_FLAG_CONSUMED) {
                break;
            }
        }
    }
    
    return handler_count;
}

/* 创建量子事件（通过量子纠缠传播的事件） */
QEntLEvent* create_quantum_event(EventType type, void* source, void* data, 
                               double coherence, double probability) {
    QEntLEvent* event = (QEntLEvent*)malloc(sizeof(QEntLEvent));
    if (!event) {
        return NULL;
    }
    
    /* 初始化基本事件字段 */
    event->type = type;
    event->source = source;
    event->data = data;
    event->timestamp = time(NULL);
    event->flags = EVENT_FLAG_QUANTUM;
    event->processed = 0;
    
    /* 初始化量子特定字段 */
    event->quantum_data.coherence = coherence;
    event->quantum_data.probability = probability;
    event->quantum_data.is_entangled = 0;
    event->quantum_data.entanglement_source = NULL;
    
    return event;
}

/* 发送量子事件 */
int event_system_emit_quantum(EventSystem* system, QEntLEvent* quantum_event) {
    if (!system || !quantum_event) {
        return 0;
    }
    
    /* 检查是否为量子事件 */
    if (!(quantum_event->flags & EVENT_FLAG_QUANTUM)) {
        return 0;
    }
    
    /* 创建队列中的事件副本 */
    int result = event_system_emit(system, quantum_event->type, quantum_event->source, 
                                 quantum_event->data, quantum_event->flags);
    
    /* 不需要释放原始事件，由调用者负责 */
    
    return result;
}

/* 创建纠缠事件对 */
int create_entangled_event_pair(QEntLEvent** event1, QEntLEvent** event2, 
                             EventType type1, EventType type2,
                             void* source1, void* source2,
                             void* data1, void* data2,
                             double entanglement_strength) {
    if (!event1 || !event2) {
        return 0;
    }
    
    /* 创建两个量子事件 */
    *event1 = create_quantum_event(type1, source1, data1, 1.0, 0.5);
    *event2 = create_quantum_event(type2, source2, data2, 1.0, 0.5);
    
    if (!*event1 || !*event2) {
        if (*event1) free(*event1);
        if (*event2) free(*event2);
        *event1 = NULL;
        *event2 = NULL;
        return 0;
    }
    
    /* 设置纠缠关系 */
    (*event1)->quantum_data.is_entangled = 1;
    (*event2)->quantum_data.is_entangled = 1;
    
    (*event1)->quantum_data.entanglement_source = *event2;
    (*event2)->quantum_data.entanglement_source = *event1;
    
    (*event1)->quantum_data.entanglement_strength = entanglement_strength;
    (*event2)->quantum_data.entanglement_strength = entanglement_strength;
    
    return 1;
}

/* 处理纠缠事件的量子折叠 */
int event_system_handle_collapse(EventSystem* system, QEntLEvent* event) {
    if (!system || !event || !(event->flags & EVENT_FLAG_QUANTUM) || 
        !event->quantum_data.is_entangled || !event->quantum_data.entanglement_source) {
        return 0;
    }
    
    /* 获取纠缠的事件 */
    QEntLEvent* entangled_event = (QEntLEvent*)event->quantum_data.entanglement_source;
    
    /* 检查事件是否已处理 */
    if (event->processed) {
        /* 如果主事件已处理，纠缠事件自动被观测 */
        entangled_event->quantum_data.probability = 1.0;
        
        /* 触发纠缠事件 */
        event_system_emit(system, entangled_event->type, entangled_event->source, 
                        entangled_event->data, entangled_event->flags);
    }
    
    return 1;
} 