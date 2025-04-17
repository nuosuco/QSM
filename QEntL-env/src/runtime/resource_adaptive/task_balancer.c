/**
 * 任务平衡器实现 - QEntL资源自适应引擎组件
 * 负责在可用资源之间智能分配计算任务，优化量子计算性能
 * 
 * 作者: QEntL核心开发团队
 * 日期: 2024-05-18
 * 版本: 1.0
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include "task_balancer.h"
#include "../event_system.h"

/**
 * 任务队列节点
 */
typedef struct TaskQueueNode {
    QuantumTask task;                // 任务
    struct TaskQueueNode* next;      // 下一个节点
    struct TaskQueueNode* prev;      // 上一个节点
    TaskCompletionCallback callback; // 完成回调
    void* user_data;                 // 用户数据
} TaskQueueNode;

/**
 * 任务队列
 */
typedef struct {
    TaskQueueNode* head;      // 队列头
    TaskQueueNode* tail;      // 队列尾
    unsigned int count;       // 任务数量
    unsigned int max_size;    // 最大大小
} TaskQueue;

/**
 * 回调条目
 */
typedef struct {
    unsigned int task_id;           // 任务ID
    TaskCompletionCallback callback; // 回调函数
    void* user_data;                // 用户数据
} CallbackEntry;

/**
 * 资源单元列表
 */
typedef struct {
    ResourceUnit* units;         // 资源单元数组
    unsigned int count;          // 单元数量
    unsigned int capacity;       // 数组容量
    unsigned int next_id;        // 下一个ID
} ResourceUnitList;

/**
 * 任务平衡器内部结构
 */
struct TaskBalancer {
    TaskQueue pending_queue;         // 等待队列
    TaskQueue running_queue;         // 运行队列
    TaskQueue completed_queue;       // 完成队列
    
    ResourceUnitList resources;      // 资源单元列表
    
    TaskBalancerConfig config;       // 配置
    TaskBalancerStats stats;         // 统计
    
    ResourceMonitoringSystem* monitor;  // 资源监控系统
    DeviceCapabilityDetector* detector; // 设备能力检测器
    QuantumBitAdjuster* adjuster;       // 量子比特调整器
    
    unsigned int next_task_id;       // 下一个任务ID
    time_t last_rebalance;          // 上次重新平衡时间
    
    int is_active;                   // 是否激活
};

// 内部函数声明
static int initialize_task_queue(TaskQueue* queue, unsigned int max_size);
static void free_task_queue(TaskQueue* queue);
static int enqueue_task(TaskQueue* queue, const QuantumTask* task, TaskCompletionCallback callback, void* user_data);
static int dequeue_task(TaskQueue* queue, QuantumTask* out_task, TaskCompletionCallback* out_callback, void** out_user_data);
static TaskQueueNode* find_task_node(TaskQueue* queue, unsigned int task_id);
static int remove_task_node(TaskQueue* queue, TaskQueueNode* node);
static int initialize_resource_list(ResourceUnitList* list, unsigned int initial_capacity);
static void free_resource_list(ResourceUnitList* list);
static ResourceUnit* find_resource_unit(ResourceUnitList* list, unsigned int unit_id);
static int allocate_resources(TaskBalancer* balancer, QuantumTask* task);
static int release_resources(TaskBalancer* balancer, const QuantumTask* task);
static int rebalance_tasks(TaskBalancer* balancer);
static unsigned int calculate_task_score(const TaskBalancer* balancer, const QuantumTask* task);
static unsigned int calculate_resource_score(const TaskBalancer* balancer, const ResourceUnit* unit, const QuantumTask* task);
static const char* get_task_type_name(TaskType type);
static const char* get_task_priority_name(TaskPriority priority);
static const char* get_task_status_name(TaskStatus status);
static const char* get_allocation_strategy_name(AllocationStrategy strategy);

/**
 * 创建任务平衡器
 */
TaskBalancer* task_balancer_create(ResourceMonitoringSystem* monitor, 
                                  DeviceCapabilityDetector* detector,
                                  QuantumBitAdjuster* adjuster) {
    if (!monitor || !detector || !adjuster) {
        fprintf(stderr, "错误: 创建任务平衡器时需要有效的系统引用\n");
        return NULL;
    }
    
    TaskBalancer* balancer = (TaskBalancer*)malloc(sizeof(TaskBalancer));
    if (!balancer) {
        fprintf(stderr, "错误: 无法为任务平衡器分配内存\n");
        return NULL;
    }
    
    // 初始化任务队列
    if (!initialize_task_queue(&balancer->pending_queue, 100) ||
        !initialize_task_queue(&balancer->running_queue, 100) ||
        !initialize_task_queue(&balancer->completed_queue, 100)) {
        
        free_task_queue(&balancer->pending_queue);
        free_task_queue(&balancer->running_queue);
        free_task_queue(&balancer->completed_queue);
        free(balancer);
        return NULL;
    }
    
    // 初始化资源列表
    if (!initialize_resource_list(&balancer->resources, 10)) {
        free_task_queue(&balancer->pending_queue);
        free_task_queue(&balancer->running_queue);
        free_task_queue(&balancer->completed_queue);
        free(balancer);
        return NULL;
    }
    
    // 设置默认配置
    balancer->config.strategy = ALLOCATION_STRATEGY_BALANCED;
    balancer->config.max_queue_size = 1000;
    balancer->config.thread_count = 4;
    balancer->config.rebalance_interval_ms = 5000; // 5秒
    balancer->config.enable_preemption = 0;
    balancer->config.auto_adjust_resources = 1;
    balancer->config.priority_weight = 1.0;
    balancer->config.performance_weight = 1.0;
    balancer->config.efficiency_weight = 1.0;
    
    // 初始化统计
    memset(&balancer->stats, 0, sizeof(TaskBalancerStats));
    
    // 设置系统引用
    balancer->monitor = monitor;
    balancer->detector = detector;
    balancer->adjuster = adjuster;
    
    // 初始化其他字段
    balancer->next_task_id = 1;
    balancer->last_rebalance = time(NULL);
    balancer->is_active = 0;
    
    return balancer;
}

/**
 * 销毁任务平衡器
 */
void task_balancer_destroy(TaskBalancer* balancer) {
    if (!balancer) return;
    
    // 停止任务平衡器
    task_balancer_stop(balancer);
    
    // 释放资源
    free_task_queue(&balancer->pending_queue);
    free_task_queue(&balancer->running_queue);
    free_task_queue(&balancer->completed_queue);
    free_resource_list(&balancer->resources);
    
    free(balancer);
}

/**
 * 启动任务平衡器
 */
int task_balancer_start(TaskBalancer* balancer) {
    if (!balancer) return 0;
    
    if (balancer->is_active) {
        return 1; // 已经在运行
    }
    
    balancer->is_active = 1;
    balancer->last_rebalance = time(NULL);
    
    printf("任务平衡器启动\n");
    return 1;
}

/**
 * 停止任务平衡器
 */
int task_balancer_stop(TaskBalancer* balancer) {
    if (!balancer || !balancer->is_active) return 0;
    
    balancer->is_active = 0;
    
    printf("任务平衡器停止\n");
    return 1;
}

/**
 * 设置任务平衡器配置
 */
int task_balancer_set_config(TaskBalancer* balancer, const TaskBalancerConfig* config) {
    if (!balancer || !config) return 0;
    
    balancer->config = *config;
    
    // 更新队列大小
    balancer->pending_queue.max_size = config->max_queue_size;
    balancer->running_queue.max_size = config->max_queue_size;
    balancer->completed_queue.max_size = config->max_queue_size;
    
    return 1;
}

/**
 * 获取任务平衡器配置
 */
int task_balancer_get_config(TaskBalancer* balancer, TaskBalancerConfig* out_config) {
    if (!balancer || !out_config) return 0;
    
    *out_config = balancer->config;
    return 1;
}

/**
 * 添加资源单元
 */
unsigned int task_balancer_add_resource_unit(TaskBalancer* balancer, 
                                           ResourceType type, 
                                           unsigned int capacity,
                                           double performance,
                                           double efficiency) {
    if (!balancer) return 0;
    
    // 检查是否需要扩容
    if (balancer->resources.count >= balancer->resources.capacity) {
        unsigned int new_capacity = balancer->resources.capacity * 2;
        ResourceUnit* new_units = (ResourceUnit*)realloc(
            balancer->resources.units, new_capacity * sizeof(ResourceUnit));
        
        if (!new_units) {
            fprintf(stderr, "错误: 无法扩展资源单元数组\n");
            return 0;
        }
        
        balancer->resources.units = new_units;
        balancer->resources.capacity = new_capacity;
    }
    
    // 创建新资源单元
    unsigned int unit_id = balancer->resources.next_id++;
    ResourceUnit unit;
    unit.id = unit_id;
    unit.resource_type = type;
    unit.total_capacity = capacity;
    unit.available_capacity = capacity;
    unit.performance_rating = performance;
    unit.energy_efficiency = efficiency;
    unit.is_active = 1;
    unit.last_update = time(NULL);
    
    // 添加到列表
    balancer->resources.units[balancer->resources.count++] = unit;
    
    printf("添加资源单元: ID=%u, 类型=%d, 容量=%u\n", unit_id, type, capacity);
    return unit_id;
}

/**
 * 移除资源单元
 */
int task_balancer_remove_resource_unit(TaskBalancer* balancer, unsigned int unit_id) {
    if (!balancer) return 0;
    
    // 查找资源单元
    for (unsigned int i = 0; i < balancer->resources.count; i++) {
        if (balancer->resources.units[i].id == unit_id) {
            // 将最后一个单元移动到当前位置
            if (i < balancer->resources.count - 1) {
                balancer->resources.units[i] = balancer->resources.units[balancer->resources.count - 1];
            }
            
            balancer->resources.count--;
            printf("移除资源单元: ID=%u\n", unit_id);
            return 1;
        }
    }
    
    fprintf(stderr, "错误: 未找到资源单元 ID=%u\n", unit_id);
    return 0;
}

/**
 * 更新资源单元
 */
int task_balancer_update_resource_unit(TaskBalancer* balancer, 
                                     unsigned int unit_id,
                                     unsigned int available_capacity,
                                     double performance,
                                     double efficiency) {
    if (!balancer) return 0;
    
    // 查找资源单元
    ResourceUnit* unit = find_resource_unit(&balancer->resources, unit_id);
    if (!unit) {
        fprintf(stderr, "错误: 未找到资源单元 ID=%u\n", unit_id);
        return 0;
    }
    
    // 更新资源单元
    unit->available_capacity = available_capacity;
    unit->performance_rating = performance;
    unit->energy_efficiency = efficiency;
    unit->last_update = time(NULL);
    
    return 1;
}

/**
 * 创建量子任务
 */
unsigned int task_balancer_create_task(TaskBalancer* balancer,
                                     TaskType type,
                                     TaskPriority priority,
                                     unsigned int resource_demand,
                                     double expected_duration,
                                     void* task_data,
                                     size_t data_size) {
    if (!balancer) return 0;
    
    // 检查队列是否已满
    if (balancer->pending_queue.count >= balancer->pending_queue.max_size) {
        fprintf(stderr, "错误: 任务队列已满\n");
        return 0;
    }
    
    // 创建任务
    QuantumTask task;
    task.id = balancer->next_task_id++;
    task.type = type;
    task.priority = priority;
    task.status = TASK_STATUS_PENDING;
    task.resource_demand = resource_demand;
    task.expected_duration = expected_duration;
    task.actual_duration = 0.0;
    task.creation_time = time(NULL);
    task.start_time = 0;
    task.completion_time = 0;
    task.assigned_unit_id = 0;
    
    // 复制任务数据
    if (task_data && data_size > 0) {
        task.task_data = malloc(data_size);
        if (!task.task_data) {
            fprintf(stderr, "错误: 无法为任务数据分配内存\n");
            return 0;
        }
        
        memcpy(task.task_data, task_data, data_size);
        task.data_size = data_size;
    } else {
        task.task_data = NULL;
        task.data_size = 0;
    }
    
    // 添加到等待队列
    if (!enqueue_task(&balancer->pending_queue, &task, NULL, NULL)) {
        if (task.task_data) {
            free(task.task_data);
        }
        return 0;
    }
    
    printf("创建任务: ID=%u, 类型=%s, 优先级=%s\n", 
           task.id, get_task_type_name(type), get_task_priority_name(priority));
    
    // 如果平衡器处于活动状态，尝试立即分配资源
    if (balancer->is_active) {
        TaskQueueNode* node = find_task_node(&balancer->pending_queue, task.id);
        if (node) {
            allocate_resources(balancer, &node->task);
        }
    }
    
    return task.id;
}

/**
 * 注册任务完成回调
 */
int task_balancer_register_completion_callback(TaskBalancer* balancer,
                                             unsigned int task_id,
                                             TaskCompletionCallback callback,
                                             void* user_data) {
    if (!balancer || !callback) return 0;
    
    // 查找任务
    TaskQueueNode* node = find_task_node(&balancer->pending_queue, task_id);
    if (node) {
        node->callback = callback;
        node->user_data = user_data;
        return 1;
    }
    
    node = find_task_node(&balancer->running_queue, task_id);
    if (node) {
        node->callback = callback;
        node->user_data = user_data;
        return 1;
    }
    
    fprintf(stderr, "错误: 未找到任务 ID=%u\n", task_id);
    return 0;
}

/**
 * 获取任务状态
 */
int task_balancer_get_task_status(TaskBalancer* balancer, 
                                unsigned int task_id,
                                QuantumTask* out_task) {
    if (!balancer || !out_task) return 0;
    
    // 检查各队列
    TaskQueueNode* node = find_task_node(&balancer->pending_queue, task_id);
    if (node) {
        *out_task = node->task;
        return 1;
    }
    
    node = find_task_node(&balancer->running_queue, task_id);
    if (node) {
        *out_task = node->task;
        return 1;
    }
    
    node = find_task_node(&balancer->completed_queue, task_id);
    if (node) {
        *out_task = node->task;
        return 1;
    }
    
    fprintf(stderr, "错误: 未找到任务 ID=%u\n", task_id);
    return 0;
}

/**
 * 打印任务平衡器状态
 */
void task_balancer_print_status(TaskBalancer* balancer) {
    if (!balancer) return;
    
    printf("\n========== 任务平衡器状态 ==========\n");
    printf("状态: %s\n", balancer->is_active ? "运行中" : "已停止");
    printf("分配策略: %s\n", get_allocation_strategy_name(balancer->config.strategy));
    
    printf("\n--- 队列状态 ---\n");
    printf("等待队列: %u/%u\n", balancer->pending_queue.count, balancer->pending_queue.max_size);
    printf("运行队列: %u/%u\n", balancer->running_queue.count, balancer->running_queue.max_size);
    printf("完成队列: %u/%u\n", balancer->completed_queue.count, balancer->completed_queue.max_size);
    
    printf("\n--- 资源状态 ---\n");
    printf("资源单元数量: %u\n", balancer->resources.count);
    for (unsigned int i = 0; i < balancer->resources.count; i++) {
        ResourceUnit* unit = &balancer->resources.units[i];
        printf("单元 ID=%u: 类型=%d, 可用=%u/%u, 性能=%.2f, 能效=%.2f\n",
               unit->id, unit->resource_type, unit->available_capacity, 
               unit->total_capacity, unit->performance_rating, unit->energy_efficiency);
    }
    
    printf("\n--- 统计信息 ---\n");
    printf("已处理任务: %u (成功:%u, 失败:%u)\n", 
           balancer->stats.tasks_processed,
           balancer->stats.tasks_succeeded,
           balancer->stats.tasks_failed);
    printf("平均等待时间: %.2f ms\n", balancer->stats.avg_waiting_time);
    printf("平均处理时间: %.2f ms\n", balancer->stats.avg_processing_time);
    printf("资源利用率: %u%%\n", balancer->stats.resource_utilization);
    
    printf("任务类型分布:\n");
    for (int i = 0; i < TASK_TYPE_MAX; i++) {
        printf("  %s: %u\n", get_task_type_name(i), balancer->stats.load_distribution[i]);
    }
    
    printf("======================================\n\n");
}

/**
 * 运行任务平衡器测试
 */
int task_balancer_run_test(void) {
    printf("开始任务平衡器测试...\n");
    
    // 创建必要的组件
    ResourceMonitoringSystem* monitor = resource_monitoring_system_create(NULL);
    DeviceCapabilityDetector* detector = device_capability_detector_create();
    QuantumBitAdjuster* adjuster = quantum_bit_adjuster_create(detector);
    
    if (!monitor || !detector || !adjuster) {
        fprintf(stderr, "错误: 无法创建必要的组件\n");
        if (monitor) resource_monitoring_system_destroy(monitor);
        if (detector) device_capability_detector_destroy(detector);
        if (adjuster) quantum_bit_adjuster_destroy(adjuster);
        return 0;
    }
    
    // 创建任务平衡器
    TaskBalancer* balancer = task_balancer_create(monitor, detector, adjuster);
    if (!balancer) {
        fprintf(stderr, "错误: 无法创建任务平衡器\n");
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        return 0;
    }
    
    // 配置任务平衡器
    TaskBalancerConfig config;
    config.strategy = ALLOCATION_STRATEGY_BALANCED;
    config.max_queue_size = 100;
    config.thread_count = 2;
    config.rebalance_interval_ms = 1000;
    config.enable_preemption = 0;
    config.auto_adjust_resources = 1;
    config.priority_weight = 1.0;
    config.performance_weight = 1.0;
    config.efficiency_weight = 0.8;
    task_balancer_set_config(balancer, &config);
    
    // 添加资源单元
    unsigned int cpu_unit = task_balancer_add_resource_unit(balancer, RESOURCE_TYPE_CPU, 100, 0.9, 0.8);
    unsigned int memory_unit = task_balancer_add_resource_unit(balancer, RESOURCE_TYPE_MEMORY, 200, 0.8, 0.9);
    unsigned int qbit_unit = task_balancer_add_resource_unit(balancer, RESOURCE_TYPE_QUANTUM_BITS, 50, 1.0, 0.7);
    
    // 启动任务平衡器
    task_balancer_start(balancer);
    
    // 创建任务
    task_balancer_create_task(balancer, TASK_TYPE_COMPUTATION, TASK_PRIORITY_HIGH, 20, 500.0, NULL, 0);
    task_balancer_create_task(balancer, TASK_TYPE_MEASUREMENT, TASK_PRIORITY_NORMAL, 10, 200.0, NULL, 0);
    task_balancer_create_task(balancer, TASK_TYPE_ENTANGLEMENT, TASK_PRIORITY_CRITICAL, 30, 1000.0, NULL, 0);
    
    // 打印状态
    task_balancer_print_status(balancer);
    
    // 更新资源单元
    task_balancer_update_resource_unit(balancer, cpu_unit, 70, 0.95, 0.85);
    task_balancer_update_resource_unit(balancer, memory_unit, 150, 0.85, 0.9);
    
    // 再次打印状态
    task_balancer_print_status(balancer);
    
    // 停止任务平衡器
    task_balancer_stop(balancer);
    
    // 销毁资源
    task_balancer_destroy(balancer);
    resource_monitoring_system_destroy(monitor);
    device_capability_detector_destroy(detector);
    quantum_bit_adjuster_destroy(adjuster);
    
    printf("任务平衡器测试完成\n");
    return 1;
}

// --- 内部函数实现 ---

/**
 * 初始化任务队列
 */
static int initialize_task_queue(TaskQueue* queue, unsigned int max_size) {
    if (!queue) return 0;
    
    queue->head = NULL;
    queue->tail = NULL;
    queue->count = 0;
    queue->max_size = max_size;
    
    return 1;
}

/**
 * 释放任务队列
 */
static void free_task_queue(TaskQueue* queue) {
    if (!queue) return;
    
    // 释放所有节点
    TaskQueueNode* current = queue->head;
    while (current) {
        TaskQueueNode* next = current->next;
        
        // 释放任务数据
        if (current->task.task_data) {
            free(current->task.task_data);
        }
        
        free(current);
        current = next;
    }
    
    queue->head = NULL;
    queue->tail = NULL;
    queue->count = 0;
}

/**
 * 将任务添加到队列
 */
static int enqueue_task(TaskQueue* queue, const QuantumTask* task, TaskCompletionCallback callback, void* user_data) {
    if (!queue || !task) return 0;
    
    // 检查队列是否已满
    if (queue->count >= queue->max_size) {
        fprintf(stderr, "错误: 任务队列已满\n");
        return 0;
    }
    
    // 创建新节点
    TaskQueueNode* node = (TaskQueueNode*)malloc(sizeof(TaskQueueNode));
    if (!node) {
        fprintf(stderr, "错误: 无法为任务队列节点分配内存\n");
        return 0;
    }
    
    // 初始化节点
    node->task = *task;
    node->next = NULL;
    node->prev = NULL;
    node->callback = callback;
    node->user_data = user_data;
    
    // 添加到队列尾部
    if (queue->tail) {
        queue->tail->next = node;
        node->prev = queue->tail;
        queue->tail = node;
    } else {
        queue->head = node;
        queue->tail = node;
    }
    
    queue->count++;
    return 1;
}

/**
 * 从队列中移除任务
 */
static int dequeue_task(TaskQueue* queue, QuantumTask* out_task, TaskCompletionCallback* out_callback, void** out_user_data) {
    if (!queue || !out_task) return 0;
    
    // 检查队列是否为空
    if (!queue->head) {
        return 0;
    }
    
    // 获取队列头部节点
    TaskQueueNode* node = queue->head;
    
    // 更新队列
    queue->head = node->next;
    if (queue->head) {
        queue->head->prev = NULL;
    } else {
        queue->tail = NULL;
    }
    
    queue->count--;
    
    // 复制任务
    *out_task = node->task;
    
    // 复制回调和用户数据
    if (out_callback) {
        *out_callback = node->callback;
    }
    
    if (out_user_data) {
        *out_user_data = node->user_data;
    }
    
    // 释放节点
    free(node);
    
    return 1;
}

/**
 * 查找任务节点
 */
static TaskQueueNode* find_task_node(TaskQueue* queue, unsigned int task_id) {
    if (!queue) return NULL;
    
    TaskQueueNode* current = queue->head;
    while (current) {
        if (current->task.id == task_id) {
            return current;
        }
        
        current = current->next;
    }
    
    return NULL;
}

/**
 * 移除任务节点
 */
static int remove_task_node(TaskQueue* queue, TaskQueueNode* node) {
    if (!queue || !node) return 0;
    
    // 更新链接
    if (node->prev) {
        node->prev->next = node->next;
    } else {
        queue->head = node->next;
    }
    
    if (node->next) {
        node->next->prev = node->prev;
    } else {
        queue->tail = node->prev;
    }
    
    queue->count--;
    
    // 释放节点
    free(node);
    
    return 1;
}

/**
 * 初始化资源列表
 */
static int initialize_resource_list(ResourceUnitList* list, unsigned int initial_capacity) {
    if (!list) return 0;
    
    list->units = (ResourceUnit*)malloc(initial_capacity * sizeof(ResourceUnit));
    if (!list->units) {
        fprintf(stderr, "错误: 无法为资源单元列表分配内存\n");
        return 0;
    }
    
    list->capacity = initial_capacity;
    list->count = 0;
    list->next_id = 1;
    
    return 1;
}

/**
 * 释放资源列表
 */
static void free_resource_list(ResourceUnitList* list) {
    if (!list) return;
    
    if (list->units) {
        free(list->units);
        list->units = NULL;
    }
    
    list->capacity = 0;
    list->count = 0;
}

/**
 * 查找资源单元
 */
static ResourceUnit* find_resource_unit(ResourceUnitList* list, unsigned int unit_id) {
    if (!list) return NULL;
    
    for (unsigned int i = 0; i < list->count; i++) {
        if (list->units[i].id == unit_id) {
            return &list->units[i];
        }
    }
    
    return NULL;
}

/**
 * 获取任务类型名称
 */
static const char* get_task_type_name(TaskType type) {
    switch (type) {
        case TASK_TYPE_COMPUTATION: return "计算";
        case TASK_TYPE_MEASUREMENT: return "测量";
        case TASK_TYPE_ENTANGLEMENT: return "纠缠";
        case TASK_TYPE_FIELD_UPDATE: return "场更新";
        case TASK_TYPE_IO: return "IO";
        case TASK_TYPE_NETWORK: return "网络";
        default: return "未知";
    }
}

/**
 * 获取任务优先级名称
 */
static const char* get_task_priority_name(TaskPriority priority) {
    switch (priority) {
        case TASK_PRIORITY_LOW: return "低";
        case TASK_PRIORITY_NORMAL: return "普通";
        case TASK_PRIORITY_HIGH: return "高";
        case TASK_PRIORITY_CRITICAL: return "关键";
        default: return "未知";
    }
}

/**
 * 获取任务状态名称
 */
static const char* get_task_status_name(TaskStatus status) {
    switch (status) {
        case TASK_STATUS_PENDING: return "等待中";
        case TASK_STATUS_ASSIGNED: return "已分配";
        case TASK_STATUS_RUNNING: return "运行中";
        case TASK_STATUS_COMPLETED: return "已完成";
        case TASK_STATUS_FAILED: return "失败";
        default: return "未知";
    }
}

/**
 * 获取分配策略名称
 */
static const char* get_allocation_strategy_name(AllocationStrategy strategy) {
    switch (strategy) {
        case ALLOCATION_STRATEGY_PERFORMANCE: return "性能优先";
        case ALLOCATION_STRATEGY_EFFICIENCY: return "效率优先";
        case ALLOCATION_STRATEGY_BALANCED: return "平衡";
        case ALLOCATION_STRATEGY_ENERGY_SAVING: return "节能";
        default: return "未知";
    }
} 