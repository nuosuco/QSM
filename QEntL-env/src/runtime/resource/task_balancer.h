/**
 * QEntL任务平衡器头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月25日
 * 
 * 任务平衡器负责根据当前资源状态和任务优先级，
 * 在量子计算资源上平衡分配计算任务，是资源自适应引擎的重要组件。
 */

#ifndef QENTL_TASK_BALANCER_H
#define QENTL_TASK_BALANCER_H

#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include "resource_monitor.h"
#include "resource_allocation_manager.h"
#include "../../quantum/quantum_circuit.h"

// 前向声明
typedef struct TaskBalancer TaskBalancer;

/**
 * 任务优先级枚举
 */
typedef enum {
    TASK_PRIORITY_LOW,          // 低优先级
    TASK_PRIORITY_NORMAL,       // 标准优先级
    TASK_PRIORITY_HIGH,         // 高优先级
    TASK_PRIORITY_CRITICAL      // 关键优先级
} TaskPriority;

/**
 * 任务状态枚举
 */
typedef enum {
    TASK_STATUS_PENDING,        // 等待中
    TASK_STATUS_SCHEDULED,      // 已调度
    TASK_STATUS_RUNNING,        // 运行中
    TASK_STATUS_PAUSED,         // 已暂停
    TASK_STATUS_COMPLETED,      // 已完成
    TASK_STATUS_FAILED,         // 已失败
    TASK_STATUS_CANCELLED       // 已取消
} TaskStatus;

/**
 * 调度策略枚举
 */
typedef enum {
    SCHEDULE_STRATEGY_FIFO,           // 先进先出
    SCHEDULE_STRATEGY_PRIORITY,       // 优先级优先
    SCHEDULE_STRATEGY_DEADLINE,       // 截止时间优先
    SCHEDULE_STRATEGY_RESOURCE,       // 资源效率优先
    SCHEDULE_STRATEGY_DYNAMIC,        // 动态策略
    SCHEDULE_STRATEGY_FAIR            // 公平策略
} ScheduleStrategy;

/**
 * 负载均衡模式枚举
 */
typedef enum {
    BALANCE_MODE_STATIC,         // 静态负载均衡
    BALANCE_MODE_DYNAMIC,        // 动态负载均衡
    BALANCE_MODE_ADAPTIVE,       // 自适应负载均衡
    BALANCE_MODE_PREDICTIVE      // 预测性负载均衡
} BalanceMode;

/**
 * 量子任务结构体
 */
typedef struct {
    char task_id[64];                  // 任务ID
    char task_name[128];               // 任务名称
    QuantumCircuit* circuit;           // 量子电路
    
    TaskPriority priority;             // 任务优先级
    TaskStatus status;                 // 任务状态
    
    int required_qubits;               // 所需量子比特数
    uint64_t required_memory_bytes;    // 所需内存（字节）
    int estimated_runtime_ms;          // 估计运行时间（毫秒）
    
    time_t submission_time;            // 提交时间
    time_t start_time;                 // 开始执行时间
    time_t completion_time;            // 完成时间
    time_t deadline;                   // 截止时间
    
    bool preemptible;                  // 是否可被抢占
    int retry_count;                   // 重试次数
    int max_retries;                   // 最大重试次数
    
    char allocation_id[64];            // 资源分配ID
    char error_message[256];           // 错误信息
} QuantumTask;

/**
 * 任务平衡器配置结构体
 */
typedef struct {
    ScheduleStrategy schedule_strategy;   // 调度策略
    BalanceMode balance_mode;             // 负载均衡模式
    
    int max_concurrent_tasks;             // 最大并发任务数
    int max_queue_size;                   // 最大队列大小
    int rebalance_interval_ms;            // 重新平衡间隔（毫秒）
    
    bool enable_task_preemption;          // 是否启用任务抢占
    bool enable_dynamic_priorities;       // 是否启用动态优先级
    bool enable_deadline_scheduling;      // 是否启用截止时间调度
    
    double priority_weight;               // 优先级权重
    double deadline_weight;               // 截止时间权重
    double resource_weight;               // 资源利用权重
    double waiting_time_weight;           // 等待时间权重
    
    int max_task_age_ms;                  // 最大任务年龄（毫秒）
    int min_execution_time_ms;            // 最小执行时间（毫秒）
    
    bool verbose;                         // 是否输出详细信息
} TaskBalancerConfig;

/**
 * 任务平衡器统计信息结构体
 */
typedef struct {
    int tasks_total;                      // 总任务数
    int tasks_completed;                  // 已完成任务数
    int tasks_failed;                     // 失败任务数
    int tasks_pending;                    // 等待中任务数
    int tasks_running;                    // 运行中任务数
    
    double average_waiting_time_ms;       // 平均等待时间（毫秒）
    double average_execution_time_ms;     // 平均执行时间（毫秒）
    double average_turnaround_time_ms;    // 平均周转时间（毫秒）
    
    int preemptions;                      // 抢占次数
    int rebalances;                       // 重新平衡次数
    
    double current_load;                  // 当前负载（0.0-1.0）
    double peak_load;                     // 峰值负载
    
    int missed_deadlines;                 // 错过的截止时间数
    double scheduling_efficiency;         // 调度效率（0.0-1.0）
} TaskBalancerStats;

/**
 * 任务事件回调函数类型
 * @param task 量子任务
 * @param previous_status 之前的状态
 * @param new_status 新状态
 * @param user_data 用户数据
 */
typedef void (*TaskEventCallback)(
    const QuantumTask* task,
    TaskStatus previous_status,
    TaskStatus new_status,
    void* user_data);

/**
 * 创建任务平衡器
 * @param config 平衡器配置
 * @param resource_monitor 资源监控器实例
 * @param allocation_manager 资源分配管理器实例
 * @return 平衡器实例
 */
TaskBalancer* task_balancer_create(
    const TaskBalancerConfig* config,
    ResourceMonitor* resource_monitor,
    ResourceAllocationManager* allocation_manager);

/**
 * 销毁任务平衡器
 * @param balancer 平衡器实例
 */
void task_balancer_destroy(TaskBalancer* balancer);

/**
 * 设置平衡器配置
 * @param balancer 平衡器实例
 * @param config 配置
 * @return 是否成功设置
 */
bool task_balancer_set_config(
    TaskBalancer* balancer,
    const TaskBalancerConfig* config);

/**
 * 获取平衡器配置
 * @param balancer 平衡器实例
 * @param config 输出配置
 * @return 是否成功获取
 */
bool task_balancer_get_config(
    TaskBalancer* balancer,
    TaskBalancerConfig* config);

/**
 * 启动任务平衡器
 * @param balancer 平衡器实例
 * @return 是否成功启动
 */
bool task_balancer_start(TaskBalancer* balancer);

/**
 * 停止任务平衡器
 * @param balancer 平衡器实例
 */
void task_balancer_stop(TaskBalancer* balancer);

/**
 * 提交量子任务
 * @param balancer 平衡器实例
 * @param circuit 量子电路
 * @param priority 任务优先级
 * @param task_name 任务名称
 * @param task_id 输出任务ID
 * @return 是否成功提交
 */
bool task_balancer_submit_task(
    TaskBalancer* balancer,
    const QuantumCircuit* circuit,
    TaskPriority priority,
    const char* task_name,
    char* task_id);

/**
 * 提交高级量子任务
 * @param balancer 平衡器实例
 * @param task 量子任务
 * @return 是否成功提交
 */
bool task_balancer_submit_advanced_task(
    TaskBalancer* balancer,
    const QuantumTask* task);

/**
 * 取消任务
 * @param balancer 平衡器实例
 * @param task_id 任务ID
 * @return 是否成功取消
 */
bool task_balancer_cancel_task(
    TaskBalancer* balancer,
    const char* task_id);

/**
 * 获取任务状态
 * @param balancer 平衡器实例
 * @param task_id 任务ID
 * @param task 输出任务信息
 * @return 是否成功获取
 */
bool task_balancer_get_task(
    TaskBalancer* balancer,
    const char* task_id,
    QuantumTask* task);

/**
 * 暂停任务
 * @param balancer 平衡器实例
 * @param task_id 任务ID
 * @return 是否成功暂停
 */
bool task_balancer_pause_task(
    TaskBalancer* balancer,
    const char* task_id);

/**
 * 恢复任务
 * @param balancer 平衡器实例
 * @param task_id 任务ID
 * @return 是否成功恢复
 */
bool task_balancer_resume_task(
    TaskBalancer* balancer,
    const char* task_id);

/**
 * 更新任务优先级
 * @param balancer 平衡器实例
 * @param task_id 任务ID
 * @param priority 新优先级
 * @return 是否成功更新
 */
bool task_balancer_update_priority(
    TaskBalancer* balancer,
    const char* task_id,
    TaskPriority priority);

/**
 * 手动触发重新平衡
 * @param balancer 平衡器实例
 * @return 是否成功触发
 */
bool task_balancer_trigger_rebalance(TaskBalancer* balancer);

/**
 * 获取所有任务
 * @param balancer 平衡器实例
 * @param tasks 输出任务数组
 * @param max_tasks 最大任务数
 * @param actual_tasks 实际任务数
 * @return 是否成功获取
 */
bool task_balancer_get_all_tasks(
    TaskBalancer* balancer,
    QuantumTask* tasks,
    int max_tasks,
    int* actual_tasks);

/**
 * 获取指定状态的任务
 * @param balancer 平衡器实例
 * @param status 任务状态
 * @param tasks 输出任务数组
 * @param max_tasks 最大任务数
 * @param actual_tasks 实际任务数
 * @return 是否成功获取
 */
bool task_balancer_get_tasks_by_status(
    TaskBalancer* balancer,
    TaskStatus status,
    QuantumTask* tasks,
    int max_tasks,
    int* actual_tasks);

/**
 * 注册任务事件回调
 * @param balancer 平衡器实例
 * @param callback 回调函数
 * @param user_data 用户数据
 * @return 是否成功注册
 */
bool task_balancer_register_callback(
    TaskBalancer* balancer,
    TaskEventCallback callback,
    void* user_data);

/**
 * 取消注册任务事件回调
 * @param balancer 平衡器实例
 * @param callback 回调函数
 * @return 是否成功取消
 */
bool task_balancer_unregister_callback(
    TaskBalancer* balancer,
    TaskEventCallback callback);

/**
 * 设置调度策略
 * @param balancer 平衡器实例
 * @param strategy 调度策略
 * @return 是否成功设置
 */
bool task_balancer_set_schedule_strategy(
    TaskBalancer* balancer,
    ScheduleStrategy strategy);

/**
 * 设置负载均衡模式
 * @param balancer 平衡器实例
 * @param mode 负载均衡模式
 * @return 是否成功设置
 */
bool task_balancer_set_balance_mode(
    TaskBalancer* balancer,
    BalanceMode mode);

/**
 * 获取平衡器统计信息
 * @param balancer 平衡器实例
 * @param stats 输出统计信息
 * @return 是否成功获取
 */
bool task_balancer_get_stats(
    TaskBalancer* balancer,
    TaskBalancerStats* stats);

/**
 * 重置统计信息
 * @param balancer 平衡器实例
 * @return 是否成功重置
 */
bool task_balancer_reset_stats(TaskBalancer* balancer);

/**
 * 生成任务平衡器报告
 * @param balancer 平衡器实例
 * @param filename 报告文件名
 * @return 是否成功生成
 */
bool task_balancer_generate_report(
    TaskBalancer* balancer,
    const char* filename);

/**
 * 估计任务完成时间
 * @param balancer 平衡器实例
 * @param task_id 任务ID
 * @param estimated_completion_time 输出估计完成时间
 * @return 是否成功估计
 */
bool task_balancer_estimate_completion_time(
    TaskBalancer* balancer,
    const char* task_id,
    time_t* estimated_completion_time);

/**
 * 获取任务排队位置
 * @param balancer 平衡器实例
 * @param task_id 任务ID
 * @param position 输出排队位置
 * @return 是否成功获取
 */
bool task_balancer_get_queue_position(
    TaskBalancer* balancer,
    const char* task_id,
    int* position);

/**
 * 获取任务优先级名称
 * @param priority 任务优先级
 * @return 优先级名称字符串
 */
const char* task_balancer_get_priority_name(TaskPriority priority);

/**
 * 获取任务状态名称
 * @param status 任务状态
 * @return 状态名称字符串
 */
const char* task_balancer_get_status_name(TaskStatus status);

/**
 * 获取调度策略名称
 * @param strategy 调度策略
 * @return 策略名称字符串
 */
const char* task_balancer_get_strategy_name(ScheduleStrategy strategy);

/**
 * 获取负载均衡模式名称
 * @param mode 负载均衡模式
 * @return 模式名称字符串
 */
const char* task_balancer_get_mode_name(BalanceMode mode);

#endif /* QENTL_TASK_BALANCER_H */ 