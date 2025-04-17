/**
 * QEntL事件系统头文件
 * 
 * 量子基因编码: QG-RUNTIME-EVTSYS-HDR-E9F1-1713051200
 * 
 * @文件: event_system.h
 * @描述: 定义QEntL运行时的事件处理系统API
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-16
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 事件系统支持量子事件发布和订阅机制
 * - 支持量子纠缠触发的事件传播和叠加
 */

#ifndef QENTL_EVENT_SYSTEM_H
#define QENTL_EVENT_SYSTEM_H

#include <time.h>

/**
 * 前向声明
 */
typedef struct EventSystem EventSystem;
typedef struct EventHandler EventHandler;
typedef struct QEntLEvent QEntLEvent;

/**
 * 事件类型枚举
 */
typedef enum {
    EVENT_SYSTEM_STARTUP,          /* 系统启动 */
    EVENT_SYSTEM_SHUTDOWN,         /* 系统关闭 */
    EVENT_STATE_CREATED,           /* 状态被创建 */
    EVENT_STATE_DESTROYED,         /* 状态被销毁 */
    EVENT_STATE_CHANGED,           /* 状态改变 */
    EVENT_STATE_MEASURED,          /* 状态被测量 */
    EVENT_FIELD_CREATED,           /* 场被创建 */
    EVENT_FIELD_DESTROYED,         /* 场被销毁 */
    EVENT_FIELD_CHANGED,           /* 场改变 */
    EVENT_ENTANGLEMENT_CREATED,    /* 纠缠被创建 */
    EVENT_ENTANGLEMENT_DESTROYED,  /* 纠缠被销毁 */
    EVENT_ENTANGLEMENT_CHANGED,    /* 纠缠改变 */
    EVENT_NETWORK_CONNECTION,      /* 网络连接 */
    EVENT_NETWORK_DISCONNECTION,   /* 网络断开 */
    EVENT_USER_DEFINED,            /* 用户定义事件基础值 */
    EVENT_MAX_PREDEFINED = EVENT_USER_DEFINED /* 预定义事件最大值 */
} EventType;

/**
 * 事件标志
 */
typedef enum {
    EVENT_FLAG_NONE = 0,           /* 无标志 */
    EVENT_FLAG_CONSUMED = 1,       /* 事件已消费 */
    EVENT_FLAG_DEFERRED = 2,       /* 延迟处理事件 */
    EVENT_FLAG_PRIORITY = 4,       /* 优先处理事件 */
    EVENT_FLAG_QUANTUM = 8,        /* 量子事件 */
    EVENT_FLAG_PROPAGATE = 16      /* 事件需要传播 */
} EventFlags;

/**
 * 事件掩码
 */
typedef unsigned int EventMask;

/**
 * 量子事件数据结构
 */
typedef struct {
    double coherence;               /* 相干性 */
    double probability;             /* 概率 */
    int is_entangled;               /* 是否纠缠 */
    void* entanglement_source;      /* 纠缠源 */
    double entanglement_strength;   /* 纠缠强度 */
} QuantumEventData;

/**
 * 事件结构
 */
typedef struct QEntLEvent {
    EventType type;                 /* 事件类型 */
    void* source;                   /* 事件源 */
    void* data;                     /* 事件数据 */
    time_t timestamp;               /* 时间戳 */
    int flags;                      /* 事件标志 */
    int processed;                  /* 是否已处理 */
    QuantumEventData quantum_data;  /* 量子事件数据 */
} QEntLEvent;

/**
 * 事件统计数据结构
 */
typedef struct {
    time_t system_start_time;        /* 系统启动时间 */
    unsigned long total_events;       /* 总事件数 */
    unsigned long processed_events;   /* 已处理事件数 */
    unsigned long dropped_events;     /* 丢弃的事件数 */
    double total_processing_time;     /* 总处理时间 */
    int max_queue_length;             /* 最大队列长度 */
} EventStats;

/**
 * 事件回调函数类型
 * 
 * @param event 事件
 * @param user_data 用户数据
 */
typedef void (*EventCallback)(QEntLEvent* event, void* user_data);

/**
 * 创建事件系统
 * 
 * @return 新创建的事件系统
 */
EventSystem* event_system_create(void);

/**
 * 销毁事件系统
 * 
 * @param system 要销毁的事件系统
 */
void event_system_destroy(EventSystem* system);

/**
 * 添加事件处理器
 * 
 * @param system 事件系统
 * @param callback 回调函数
 * @param user_data 用户数据
 * @param priority 优先级（高优先级先处理）
 * @param event_mask 事件掩码
 * @return 新创建的处理器
 */
EventHandler* event_system_add_handler(EventSystem* system, EventCallback callback, 
                                    void* user_data, int priority, EventMask event_mask);

/**
 * 移除事件处理器
 * 
 * @param system 事件系统
 * @param handler 要移除的处理器
 * @return 成功返回1，失败返回0
 */
int event_system_remove_handler(EventSystem* system, EventHandler* handler);

/**
 * 发送事件
 * 
 * @param system 事件系统
 * @param type 事件类型
 * @param source 事件源
 * @param data 事件数据
 * @param flags 事件标志
 * @return 成功返回1，失败返回0
 */
int event_system_emit(EventSystem* system, EventType type, void* source, void* data, int flags);

/**
 * 处理队列中的事件
 * 
 * @param system 事件系统
 * @return 处理的事件数量
 */
int event_system_process_events(EventSystem* system);

/**
 * 处理延迟事件
 * 
 * @param system 事件系统
 * @return 处理的事件数量
 */
int event_system_process_deferred(EventSystem* system);

/**
 * 激活处理器
 * 
 * @param system 事件系统
 * @param handler 要激活的处理器
 */
void event_system_activate_handler(EventSystem* system, EventHandler* handler);

/**
 * 停用处理器
 * 
 * @param system 事件系统
 * @param handler 要停用的处理器
 */
void event_system_deactivate_handler(EventSystem* system, EventHandler* handler);

/**
 * 获取统计数据
 * 
 * @param system 事件系统
 * @return 统计数据
 */
EventStats event_system_get_stats(EventSystem* system);

/**
 * 清除事件队列
 * 
 * @param system 事件系统
 */
void event_system_clear_queue(EventSystem* system);

/**
 * 内部函数：按优先级排序处理器
 */
static void sort_handlers_by_priority(EventSystem* system);

/**
 * 内部函数：扩展事件队列
 */
static int expand_event_queue(EventSystem* system);

/**
 * 内部函数：分发事件到处理器
 */
static int dispatch_event(EventSystem* system, QEntLEvent* event);

/**
 * 量子事件API
 */

/**
 * 创建量子事件
 * 
 * @param type 事件类型
 * @param source 事件源
 * @param data 事件数据
 * @param coherence 相干性
 * @param probability 概率
 * @return 新创建的量子事件
 */
QEntLEvent* create_quantum_event(EventType type, void* source, void* data, 
                               double coherence, double probability);

/**
 * 发送量子事件
 * 
 * @param system 事件系统
 * @param quantum_event 量子事件
 * @return 成功返回1，失败返回0
 */
int event_system_emit_quantum(EventSystem* system, QEntLEvent* quantum_event);

/**
 * 创建纠缠事件对
 * 
 * @param event1 输出第一个事件
 * @param event2 输出第二个事件
 * @param type1 第一个事件类型
 * @param type2 第二个事件类型
 * @param source1 第一个事件源
 * @param source2 第二个事件源
 * @param data1 第一个事件数据
 * @param data2 第二个事件数据
 * @param entanglement_strength 纠缠强度
 * @return 成功返回1，失败返回0
 */
int create_entangled_event_pair(QEntLEvent** event1, QEntLEvent** event2, 
                             EventType type1, EventType type2,
                             void* source1, void* source2,
                             void* data1, void* data2,
                             double entanglement_strength);

/**
 * 处理纠缠事件的量子折叠
 * 
 * @param system 事件系统
 * @param event 事件
 * @return 成功返回1，失败返回0
 */
int event_system_handle_collapse(EventSystem* system, QEntLEvent* event);

#endif /* QENTL_EVENT_SYSTEM_H */ 