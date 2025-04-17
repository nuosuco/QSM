/**
 * QEntL资源分配策略管理器头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月25日
 * 
 * 资源分配策略管理器负责管理和优化量子计算资源的分配策略，
 * 根据应用需求和系统资源状况选择最佳的资源分配方案。
 */

#ifndef QENTL_RESOURCE_ALLOCATION_MANAGER_H
#define QENTL_RESOURCE_ALLOCATION_MANAGER_H

#include <stdbool.h>
#include <stdint.h>
#include "resource_monitor.h"
#include "device_capability_detector.h"
#include "../../quantum/quantum_circuit.h"

// 前向声明
typedef struct ResourceAllocationManager ResourceAllocationManager;

/**
 * 资源分配策略枚举
 */
typedef enum {
    ALLOCATION_STRATEGY_BALANCED,    // 平衡策略 - 平衡资源使用和性能
    ALLOCATION_STRATEGY_PERFORMANCE, // 性能优先 - 最大化计算性能
    ALLOCATION_STRATEGY_EFFICIENCY,  // 效率优先 - 最小化资源使用
    ALLOCATION_STRATEGY_FIDELITY,    // 保真度优先 - 最大化结果准确性
    ALLOCATION_STRATEGY_SPEED,       // 速度优先 - 最小化执行时间
    ALLOCATION_STRATEGY_CUSTOM       // 自定义策略
} AllocationStrategy;

/**
 * 资源类型枚举
 */
typedef enum {
    RESOURCE_TYPE_QUBITS,            // 量子比特资源
    RESOURCE_TYPE_MEMORY,            // 内存资源
    RESOURCE_TYPE_COMPUTATION,       // 计算资源
    RESOURCE_TYPE_BANDWIDTH,         // 带宽资源
    RESOURCE_TYPE_STORAGE            // 存储资源
} ResourceType;

/**
 * 资源优先级枚举
 */
typedef enum {
    RESOURCE_PRIORITY_LOW,           // 低优先级
    RESOURCE_PRIORITY_NORMAL,        // 普通优先级
    RESOURCE_PRIORITY_HIGH,          // 高优先级
    RESOURCE_PRIORITY_CRITICAL       // 关键优先级
} ResourcePriority;

/**
 * 资源分配配置结构体
 */
typedef struct {
    AllocationStrategy strategy;           // 分配策略
    bool dynamic_adjustment;               // 是否启用动态调整
    int update_interval_ms;                // 更新间隔（毫秒）
    
    double qubit_weight;                   // 量子比特资源权重
    double memory_weight;                  // 内存资源权重
    double computation_weight;             // 计算资源权重
    double bandwidth_weight;               // 带宽资源权重
    
    int min_qubits;                        // 最小量子比特数
    int max_qubits;                        // 最大量子比特数
    
    uint64_t min_memory_bytes;             // 最小内存（字节）
    uint64_t max_memory_bytes;             // 最大内存（字节）
    
    int max_circuit_depth;                 // 最大电路深度
    double target_success_probability;     // 目标成功概率
    
    bool enable_resource_sharing;          // 是否启用资源共享
    bool enable_resource_reservation;      // 是否启用资源预留
    
    bool verbose;                          // 是否输出详细信息
} ResourceAllocationConfig;

/**
 * 资源分配请求结构体
 */
typedef struct {
    int requested_qubits;                  // 请求的量子比特数
    uint64_t requested_memory_bytes;       // 请求的内存（字节）
    int circuit_depth;                     // 电路深度
    double required_fidelity;              // 所需保真度
    
    ResourcePriority priority;             // 请求优先级
    char request_id[64];                   // 请求ID
    char application_name[128];            // 应用名称
    
    bool flexible_allocation;              // 是否允许灵活分配
    int min_acceptable_qubits;             // 最小可接受量子比特数
    
    int64_t deadline_ms;                   // 截止时间（毫秒）
    bool can_be_preempted;                 // 是否可被抢占
} ResourceAllocationRequest;

/**
 * 资源分配结果结构体
 */
typedef struct {
    bool success;                          // 分配是否成功
    
    int allocated_qubits;                  // 已分配的量子比特数
    uint64_t allocated_memory_bytes;       // 已分配的内存
    
    double estimated_success_probability;  // 估计成功概率
    double estimated_runtime_ms;           // 估计运行时间
    
    char allocation_id[64];                // 分配ID
    int64_t valid_until_ms;                // 有效期（毫秒时间戳）
    
    char error_message[256];               // 错误信息（如果失败）
} ResourceAllocationResult;

/**
 * 资源分配统计信息结构体
 */
typedef struct {
    int total_requests;                    // 总请求数
    int successful_allocations;            // 成功分配数
    int failed_allocations;                // 失败分配数
    
    int current_allocations;               // 当前分配数
    int qubits_in_use;                     // 使用中的量子比特数
    uint64_t memory_in_use_bytes;          // 使用中的内存
    
    double average_allocation_time_ms;     // 平均分配时间
    double resource_utilization;           // 资源利用率
    
    int preemptions;                       // 抢占次数
    int reservations;                      // 预留次数
} ResourceAllocationStats;

/**
 * 创建资源分配策略管理器
 * @param config 分配配置
 * @param resource_monitor 资源监控器实例
 * @param device_detector 设备检测器实例
 * @return 管理器实例
 */
ResourceAllocationManager* resource_allocation_manager_create(
    const ResourceAllocationConfig* config,
    ResourceMonitor* resource_monitor,
    DeviceCapabilityDetector* device_detector);

/**
 * 销毁资源分配策略管理器
 * @param manager 管理器实例
 */
void resource_allocation_manager_destroy(ResourceAllocationManager* manager);

/**
 * 设置分配配置
 * @param manager 管理器实例
 * @param config 分配配置
 * @return 是否成功设置
 */
bool resource_allocation_manager_set_config(
    ResourceAllocationManager* manager,
    const ResourceAllocationConfig* config);

/**
 * 获取分配配置
 * @param manager 管理器实例
 * @param config 输出分配配置
 * @return 是否成功获取
 */
bool resource_allocation_manager_get_config(
    ResourceAllocationManager* manager,
    ResourceAllocationConfig* config);

/**
 * 启动资源分配管理器
 * @param manager 管理器实例
 * @return 是否成功启动
 */
bool resource_allocation_manager_start(ResourceAllocationManager* manager);

/**
 * 停止资源分配管理器
 * @param manager 管理器实例
 */
void resource_allocation_manager_stop(ResourceAllocationManager* manager);

/**
 * 分配资源
 * @param manager 管理器实例
 * @param request 资源请求
 * @param result 输出分配结果
 * @return 是否成功处理请求
 */
bool resource_allocation_manager_allocate(
    ResourceAllocationManager* manager,
    const ResourceAllocationRequest* request,
    ResourceAllocationResult* result);

/**
 * 释放资源
 * @param manager 管理器实例
 * @param allocation_id 分配ID
 * @return 是否成功释放
 */
bool resource_allocation_manager_release(
    ResourceAllocationManager* manager,
    const char* allocation_id);

/**
 * 为量子电路分配资源
 * @param manager 管理器实例
 * @param circuit 量子电路
 * @param priority 优先级
 * @param result 输出分配结果
 * @return 是否成功分配
 */
bool resource_allocation_manager_allocate_for_circuit(
    ResourceAllocationManager* manager,
    const QuantumCircuit* circuit,
    ResourcePriority priority,
    ResourceAllocationResult* result);

/**
 * 预留资源
 * @param manager 管理器实例
 * @param request 资源请求
 * @param reservation_id 输出预留ID
 * @param valid_for_ms 有效期（毫秒）
 * @return 是否成功预留
 */
bool resource_allocation_manager_reserve(
    ResourceAllocationManager* manager,
    const ResourceAllocationRequest* request,
    char* reservation_id,
    int64_t valid_for_ms);

/**
 * 取消预留
 * @param manager 管理器实例
 * @param reservation_id 预留ID
 * @return 是否成功取消
 */
bool resource_allocation_manager_cancel_reservation(
    ResourceAllocationManager* manager,
    const char* reservation_id);

/**
 * 检查资源可用性
 * @param manager 管理器实例
 * @param required_qubits 所需量子比特数
 * @param required_memory_bytes 所需内存
 * @param available_qubits 输出可用量子比特数
 * @param available_memory_bytes 输出可用内存
 * @return 是否有足够资源
 */
bool resource_allocation_manager_check_availability(
    ResourceAllocationManager* manager,
    int required_qubits,
    uint64_t required_memory_bytes,
    int* available_qubits,
    uint64_t* available_memory_bytes);

/**
 * 获取分配统计信息
 * @param manager 管理器实例
 * @param stats 输出统计信息
 * @return 是否成功获取
 */
bool resource_allocation_manager_get_stats(
    ResourceAllocationManager* manager,
    ResourceAllocationStats* stats);

/**
 * 设置分配策略
 * @param manager 管理器实例
 * @param strategy 分配策略
 * @return 是否成功设置
 */
bool resource_allocation_manager_set_strategy(
    ResourceAllocationManager* manager,
    AllocationStrategy strategy);

/**
 * 生成资源分配报告
 * @param manager 管理器实例
 * @param filename 报告文件名
 * @return 是否成功生成
 */
bool resource_allocation_manager_generate_report(
    ResourceAllocationManager* manager,
    const char* filename);

/**
 * 分析资源需求
 * @param manager 管理器实例
 * @param circuit 量子电路
 * @param qubits 输出所需量子比特数
 * @param memory_bytes 输出所需内存
 * @param circuit_depth 输出电路深度
 * @return 是否成功分析
 */
bool resource_allocation_manager_analyze_requirements(
    ResourceAllocationManager* manager,
    const QuantumCircuit* circuit,
    int* qubits,
    uint64_t* memory_bytes,
    int* circuit_depth);

/**
 * 获取分配策略名称
 * @param strategy 分配策略
 * @return 策略名称字符串
 */
const char* resource_allocation_manager_get_strategy_name(AllocationStrategy strategy);

/**
 * 获取资源优先级名称
 * @param priority 资源优先级
 * @return 优先级名称字符串
 */
const char* resource_allocation_manager_get_priority_name(ResourcePriority priority);

/**
 * 获取资源类型名称
 * @param type 资源类型
 * @return 类型名称字符串
 */
const char* resource_allocation_manager_get_resource_type_name(ResourceType type);

#endif /* QENTL_RESOURCE_ALLOCATION_MANAGER_H */ 