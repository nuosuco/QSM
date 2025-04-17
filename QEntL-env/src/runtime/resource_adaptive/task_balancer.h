/**
 * 任务平衡器头文件 - QEntL资源自适应引擎组件
 * 负责在可用资源之间智能分配计算任务，优化量子计算性能
 * 
 * 作者: QEntL核心开发团队
 * 日期: 2024-05-18
 * 版本: 1.0
 */

#ifndef QENTL_TASK_BALANCER_H
#define QENTL_TASK_BALANCER_H

#include <time.h>
#include "resource_monitoring_system.h"
#include "device_capability_detector.h"
#include "quantum_bit_adjuster.h"

/**
 * 任务优先级
 */
typedef enum {
    TASK_PRIORITY_LOW,     // 低优先级任务
    TASK_PRIORITY_NORMAL,  // 正常优先级任务
    TASK_PRIORITY_HIGH,    // 高优先级任务
    TASK_PRIORITY_CRITICAL // 关键优先级任务
} TaskPriority;

/**
 * 任务类型
 */
typedef enum {
    TASK_TYPE_COMPUTATION,    // 计算任务
    TASK_TYPE_MEASUREMENT,    // 测量任务
    TASK_TYPE_ENTANGLEMENT,   // 纠缠操作任务
    TASK_TYPE_FIELD_UPDATE,   // 量子场更新任务
    TASK_TYPE_IO,             // IO操作任务
    TASK_TYPE_NETWORK,        // 网络操作任务
    TASK_TYPE_MAX             // 任务类型数量
} TaskType;

/**
 * 分配策略
 */
typedef enum {
    ALLOCATION_STRATEGY_PERFORMANCE,  // 偏向性能的分配策略
    ALLOCATION_STRATEGY_EFFICIENCY,   // 偏向效率的分配策略
    ALLOCATION_STRATEGY_BALANCED,     // 平衡的分配策略
    ALLOCATION_STRATEGY_ENERGY_SAVING // 节能的分配策略
} AllocationStrategy;

/**
 * 任务状态
 */
typedef enum {
    TASK_STATUS_PENDING,    // 等待分配
    TASK_STATUS_ASSIGNED,   // 已分配
    TASK_STATUS_RUNNING,    // 运行中
    TASK_STATUS_COMPLETED,  // 已完成
    TASK_STATUS_FAILED      // 失败
} TaskStatus;

/**
 * 资源单元
 */
typedef struct {
    unsigned int id;                // 资源单元ID
    unsigned int total_capacity;    // 总容量
    unsigned int available_capacity;// 可用容量
    double performance_rating;      // 性能评分
    double energy_efficiency;       // 能效比
    ResourceType resource_type;     // 资源类型
    int is_active;                  // 是否激活
    time_t last_update;            // 上次更新时间
} ResourceUnit;

/**
 * 量子任务
 */
typedef struct {
    unsigned int id;               // 任务ID
    TaskType type;                 // 任务类型
    TaskPriority priority;         // 任务优先级
    TaskStatus status;             // 任务状态
    unsigned int resource_demand;  // 资源需求量
    double expected_duration;      // 预期持续时间(毫秒)
    double actual_duration;        // 实际持续时间(毫秒)
    time_t creation_time;         // 创建时间
    time_t start_time;            // 开始时间
    time_t completion_time;       // 完成时间
    unsigned int assigned_unit_id; // 分配的资源单元ID
    void* task_data;              // 任务数据
    size_t data_size;             // 数据大小
} QuantumTask;

/**
 * 任务完成回调函数类型
 */
typedef void (*TaskCompletionCallback)(QuantumTask* task, void* user_data);

/**
 * 任务调度器配置
 */
typedef struct {
    AllocationStrategy strategy;        // 分配策略
    unsigned int max_queue_size;        // 最大队列大小
    unsigned int thread_count;          // 线程数
    unsigned int rebalance_interval_ms; // 重新平衡间隔(毫秒)
    int enable_preemption;              // 是否启用任务抢占
    int auto_adjust_resources;          // 是否自动调整资源
    double priority_weight;             // 优先级权重
    double performance_weight;          // 性能权重
    double efficiency_weight;           // 效率权重
} TaskBalancerConfig;

/**
 * 任务平衡统计
 */
typedef struct {
    unsigned int tasks_processed;       // 已处理任务数
    unsigned int tasks_succeeded;       // 成功任务数
    unsigned int tasks_failed;          // 失败任务数
    double avg_waiting_time;            // 平均等待时间(毫秒)
    double avg_processing_time;         // 平均处理时间(毫秒)
    unsigned int resource_utilization;  // 资源利用率(百分比)
    unsigned int load_distribution[TASK_TYPE_MAX]; // 各类型任务负载分布
    time_t last_rebalance;             // 上次重新平衡时间
} TaskBalancerStats;

/**
 * 任务平衡器
 */
typedef struct TaskBalancer TaskBalancer;

/**
 * 创建任务平衡器
 * 
 * @param monitor 资源监控系统
 * @param detector 设备能力检测器
 * @param adjuster 量子比特调整器
 * @return 新创建的任务平衡器，失败时返回NULL
 */
TaskBalancer* task_balancer_create(ResourceMonitoringSystem* monitor, 
                                  DeviceCapabilityDetector* detector,
                                  QuantumBitAdjuster* adjuster);

/**
 * 销毁任务平衡器
 * 
 * @param balancer 要销毁的任务平衡器
 */
void task_balancer_destroy(TaskBalancer* balancer);

/**
 * 启动任务平衡器
 * 
 * @param balancer 任务平衡器
 * @return 成功时返回1，失败时返回0
 */
int task_balancer_start(TaskBalancer* balancer);

/**
 * 停止任务平衡器
 * 
 * @param balancer 任务平衡器
 * @return 成功时返回1，失败时返回0
 */
int task_balancer_stop(TaskBalancer* balancer);

/**
 * 设置任务平衡器配置
 * 
 * @param balancer 任务平衡器
 * @param config 配置
 * @return 成功时返回1，失败时返回0
 */
int task_balancer_set_config(TaskBalancer* balancer, const TaskBalancerConfig* config);

/**
 * 获取任务平衡器配置
 * 
 * @param balancer 任务平衡器
 * @param out_config 输出配置
 * @return 成功时返回1，失败时返回0
 */
int task_balancer_get_config(TaskBalancer* balancer, TaskBalancerConfig* out_config);

/**
 * 添加资源单元
 * 
 * @param balancer 任务平衡器
 * @param type 资源类型
 * @param capacity 容量
 * @param performance 性能评分
 * @param efficiency 能效比
 * @return 成功时返回资源单元ID，失败时返回0
 */
unsigned int task_balancer_add_resource_unit(TaskBalancer* balancer, 
                                           ResourceType type, 
                                           unsigned int capacity,
                                           double performance,
                                           double efficiency);

/**
 * 移除资源单元
 * 
 * @param balancer 任务平衡器
 * @param unit_id 资源单元ID
 * @return 成功时返回1，失败时返回0
 */
int task_balancer_remove_resource_unit(TaskBalancer* balancer, unsigned int unit_id);

/**
 * 更新资源单元
 * 
 * @param balancer 任务平衡器
 * @param unit_id 资源单元ID
 * @param available_capacity 可用容量
 * @param performance 性能评分
 * @param efficiency 能效比
 * @return 成功时返回1，失败时返回0
 */
int task_balancer_update_resource_unit(TaskBalancer* balancer, 
                                     unsigned int unit_id,
                                     unsigned int available_capacity,
                                     double performance,
                                     double efficiency);

/**
 * 创建量子任务
 * 
 * @param balancer 任务平衡器
 * @param type 任务类型
 * @param priority 任务优先级
 * @param resource_demand 资源需求量
 * @param expected_duration 预期持续时间(毫秒)
 * @param task_data 任务数据
 * @param data_size 数据大小
 * @return 成功时返回任务ID，失败时返回0
 */
unsigned int task_balancer_create_task(TaskBalancer* balancer,
                                     TaskType type,
                                     TaskPriority priority,
                                     unsigned int resource_demand,
                                     double expected_duration,
                                     void* task_data,
                                     size_t data_size);

/**
 * 注册任务完成回调
 * 
 * @param balancer 任务平衡器
 * @param task_id 任务ID
 * @param callback 回调函数
 * @param user_data 用户数据
 * @return 成功时返回1，失败时返回0
 */
int task_balancer_register_completion_callback(TaskBalancer* balancer,
                                             unsigned int task_id,
                                             TaskCompletionCallback callback,
                                             void* user_data);

/**
 * 取消任务
 * 
 * @param balancer 任务平衡器
 * @param task_id 任务ID
 * @return 成功时返回1，失败时返回0
 */
int task_balancer_cancel_task(TaskBalancer* balancer, unsigned int task_id);

/**
 * 获取任务状态
 * 
 * @param balancer 任务平衡器
 * @param task_id 任务ID
 * @param out_task 输出任务信息
 * @return 成功时返回1，失败时返回0
 */
int task_balancer_get_task_status(TaskBalancer* balancer, 
                                unsigned int task_id,
                                QuantumTask* out_task);

/**
 * 强制重新平衡任务
 * 
 * @param balancer 任务平衡器
 * @return 成功时返回1，失败时返回0
 */
int task_balancer_force_rebalance(TaskBalancer* balancer);

/**
 * 获取任务平衡器统计信息
 * 
 * @param balancer 任务平衡器
 * @param out_stats 输出统计信息
 * @return 成功时返回1，失败时返回0
 */
int task_balancer_get_stats(TaskBalancer* balancer, TaskBalancerStats* out_stats);

/**
 * 打印任务平衡器状态
 * 
 * @param balancer 任务平衡器
 */
void task_balancer_print_status(TaskBalancer* balancer);

/**
 * 运行任务平衡器测试
 * 
 * @return 成功时返回1，失败时返回0
 */
int task_balancer_run_test(void);

#endif /* QENTL_TASK_BALANCER_H */ 