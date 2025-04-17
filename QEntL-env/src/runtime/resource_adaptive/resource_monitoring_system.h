/**
 * @file resource_monitoring_system.h
 * @brief 资源监控系统头文件 - QEntL资源自适应引擎的组件
 * @author QEntL核心开发团队
 * @date 2024-05-19
 * @version 1.0
 *
 * 该文件定义了资源监控系统的API和数据结构，用于监控量子应用程序的资源使用情况并提供优化建议。
 */

#ifndef QENTL_RESOURCE_MONITORING_SYSTEM_H
#define QENTL_RESOURCE_MONITORING_SYSTEM_H

#include <stdbool.h>
#include <time.h>
#include "device_capability_detector.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief 资源类型
 */
typedef enum {
    RESOURCE_TYPE_CPU,            /**< CPU资源 */
    RESOURCE_TYPE_MEMORY,         /**< 内存资源 */
    RESOURCE_TYPE_STORAGE,        /**< 存储资源 */
    RESOURCE_TYPE_NETWORK,        /**< 网络资源 */
    RESOURCE_TYPE_QUANTUM_BITS,   /**< 量子比特资源 */
    RESOURCE_TYPE_QUANTUM_GATES,  /**< 量子门操作 */
    RESOURCE_TYPE_ENTANGLEMENT,   /**< 量子纠缠资源 */
    RESOURCE_TYPE_ALL             /**< 所有资源类型 */
} ResourceType;

/**
 * @brief 资源使用水平
 */
typedef enum {
    RESOURCE_LEVEL_LOW,           /**< 低使用率 */
    RESOURCE_LEVEL_NORMAL,        /**< 正常使用率 */
    RESOURCE_LEVEL_HIGH,          /**< 高使用率 */
    RESOURCE_LEVEL_CRITICAL       /**< 临界使用率 */
} ResourceLevel;

/**
 * @brief 资源利用率阈值
 */
typedef struct {
    float low_threshold;          /**< 低利用率阈值 */
    float normal_threshold;       /**< 正常利用率阈值 */
    float high_threshold;         /**< 高利用率阈值 */
    float critical_threshold;     /**< 临界利用率阈值 */
} ResourceThresholds;

/**
 * @brief 资源使用情况
 */
typedef struct {
    ResourceType type;            /**< 资源类型 */
    float utilization;            /**< 利用率(0.0-1.0) */
    ResourceLevel level;          /**< 使用水平 */
    unsigned int available;       /**< 可用资源数量 */
    unsigned int total;           /**< 总资源数量 */
    float efficiency;             /**< 效率指标(0.0-1.0) */
    time_t timestamp;             /**< 时间戳 */
} ResourceUsage;

/**
 * @brief 资源使用历史记录条目
 */
typedef struct {
    ResourceUsage usage;          /**< 资源使用情况 */
    time_t timestamp;             /**< 记录时间戳 */
} ResourceHistoryEntry;

/**
 * @brief 资源监控配置
 */
typedef struct {
    unsigned int sampling_interval_ms;   /**< 采样间隔(毫秒) */
    unsigned int history_size;           /**< 历史记录大小 */
    ResourceThresholds thresholds[7];    /**< 各资源类型的阈值配置 */
    bool alert_on_high;                  /**< 高使用率时是否发出警报 */
    bool alert_on_critical;              /**< 临界使用率时是否发出警报 */
    bool auto_optimize;                  /**< 是否自动优化 */
} ResourceMonitoringConfig;

/**
 * @brief 量子资源指标
 */
typedef struct {
    unsigned int active_qubits;          /**< 活跃量子比特数 */
    unsigned int max_qubits;             /**< 最大量子比特数 */
    unsigned int gate_operations;        /**< 量子门操作次数 */
    unsigned int entangled_pairs;        /**< 量子纠缠对数 */
    unsigned int measurement_operations; /**< 测量操作次数 */
    double error_rate;                   /**< 错误率 */
    double coherence_time_us;            /**< 相干时间(微秒) */
    double fidelity;                     /**< 保真度 */
} QuantumResourceMetrics;

/**
 * @brief 优化建议类型
 */
typedef enum {
    OPTIMIZE_REDUCE_QUBITS,              /**< 减少量子比特使用 */
    OPTIMIZE_INCREASE_QUBITS,            /**< 增加量子比特使用 */
    OPTIMIZE_REDUCE_GATES,               /**< 减少量子门操作 */
    OPTIMIZE_OPTIMIZE_CIRCUIT,           /**< 优化量子电路 */
    OPTIMIZE_CHANGE_ALGORITHM,           /**< 更改算法 */
    OPTIMIZE_DISTRIBUTE_WORKLOAD,        /**< 分布式工作负载 */
    OPTIMIZE_ADJUST_MEMORY,              /**< 调整内存使用 */
    OPTIMIZE_ADJUST_ERROR_CORRECTION     /**< 调整错误修正 */
} OptimizationType;

/**
 * @brief 优化建议
 */
typedef struct {
    OptimizationType type;               /**< 优化类型 */
    ResourceType resource_type;          /**< 相关资源类型 */
    float current_utilization;           /**< 当前利用率 */
    float target_utilization;            /**< 目标利用率 */
    float estimated_improvement;         /**< 估计改进百分比 */
    char description[256];               /**< 建议描述 */
    time_t timestamp;                    /**< 建议生成时间 */
} OptimizationSuggestion;

/**
 * @brief 资源警报级别
 */
typedef enum {
    RESOURCE_ALERT_INFO,                 /**< 信息级别警报 */
    RESOURCE_ALERT_WARNING,              /**< 警告级别警报 */
    RESOURCE_ALERT_ERROR,                /**< 错误级别警报 */
    RESOURCE_ALERT_CRITICAL              /**< 严重级别警报 */
} ResourceAlertLevel;

/**
 * @brief 资源警报
 */
typedef struct {
    ResourceType resource_type;          /**< 资源类型 */
    ResourceAlertLevel level;            /**< 警报级别 */
    char message[256];                   /**< 警报消息 */
    float value;                         /**< 触发警报的值 */
    float threshold;                     /**< 警报阈值 */
    time_t timestamp;                    /**< 警报时间 */
} ResourceAlert;

/**
 * @brief 资源警报回调函数类型
 * @param alert 警报信息
 * @param context 回调上下文
 */
typedef void (*ResourceAlertCallback)(
    const ResourceAlert* alert,
    void* context);

/**
 * @brief 优化建议回调函数类型
 * @param suggestion 优化建议
 * @param context 回调上下文
 */
typedef void (*OptimizationSuggestionCallback)(
    const OptimizationSuggestion* suggestion,
    void* context);

/**
 * @brief 资源监控系统
 */
typedef struct ResourceMonitoringSystem ResourceMonitoringSystem;

/**
 * @brief 创建资源监控系统
 * @param detector 设备能力检测器
 * @param config 监控配置
 * @return 成功返回监控系统指针，失败返回NULL
 */
ResourceMonitoringSystem* resource_monitoring_system_create(
    DeviceCapabilityDetector* detector,
    const ResourceMonitoringConfig* config);

/**
 * @brief 销毁资源监控系统
 * @param system 要销毁的监控系统
 */
void resource_monitoring_system_destroy(ResourceMonitoringSystem* system);

/**
 * @brief 启动资源监控
 * @param system 资源监控系统
 * @return 成功返回true，失败返回false
 */
bool resource_monitoring_system_start(ResourceMonitoringSystem* system);

/**
 * @brief 停止资源监控
 * @param system 资源监控系统
 */
void resource_monitoring_system_stop(ResourceMonitoringSystem* system);

/**
 * @brief 获取当前资源使用情况
 * @param system 资源监控系统
 * @param type 资源类型
 * @param usage 用于存储使用情况的指针
 * @return 成功返回true，失败返回false
 */
bool resource_monitoring_system_get_usage(
    ResourceMonitoringSystem* system,
    ResourceType type,
    ResourceUsage* usage);

/**
 * @brief 报告量子资源指标
 * @param system 资源监控系统
 * @param metrics 量子资源指标
 * @return 成功返回true，失败返回false
 */
bool resource_monitoring_system_report_quantum_metrics(
    ResourceMonitoringSystem* system,
    const QuantumResourceMetrics* metrics);

/**
 * @brief 获取资源使用历史
 * @param system 资源监控系统
 * @param type 资源类型
 * @param entries 用于存储历史记录的数组
 * @param max_entries 数组大小
 * @param actual_entries 实际返回的记录数量
 * @return 成功返回true，失败返回false
 */
bool resource_monitoring_system_get_history(
    ResourceMonitoringSystem* system,
    ResourceType type,
    ResourceHistoryEntry* entries,
    unsigned int max_entries,
    unsigned int* actual_entries);

/**
 * @brief 获取资源利用率阈值
 * @param system 资源监控系统
 * @param type 资源类型
 * @param thresholds 用于存储阈值的指针
 * @return 成功返回true，失败返回false
 */
bool resource_monitoring_system_get_thresholds(
    ResourceMonitoringSystem* system,
    ResourceType type,
    ResourceThresholds* thresholds);

/**
 * @brief 设置资源利用率阈值
 * @param system 资源监控系统
 * @param type 资源类型
 * @param thresholds 阈值
 * @return 成功返回true，失败返回false
 */
bool resource_monitoring_system_set_thresholds(
    ResourceMonitoringSystem* system,
    ResourceType type,
    const ResourceThresholds* thresholds);

/**
 * @brief 设置资源警报回调
 * @param system 资源监控系统
 * @param callback 回调函数
 * @param context 回调上下文
 */
void resource_monitoring_system_set_alert_callback(
    ResourceMonitoringSystem* system,
    ResourceAlertCallback callback,
    void* context);

/**
 * @brief 设置优化建议回调
 * @param system 资源监控系统
 * @param callback 回调函数
 * @param context 回调上下文
 */
void resource_monitoring_system_set_suggestion_callback(
    ResourceMonitoringSystem* system,
    OptimizationSuggestionCallback callback,
    void* context);

/**
 * @brief 获取优化建议
 * @param system 资源监控系统
 * @param type 资源类型
 * @param suggestion 用于存储建议的指针
 * @return 成功返回true，失败返回false
 */
bool resource_monitoring_system_get_suggestion(
    ResourceMonitoringSystem* system,
    ResourceType type,
    OptimizationSuggestion* suggestion);

/**
 * @brief 获取系统配置
 * @param system 资源监控系统
 * @param config 用于存储配置的指针
 * @return 成功返回true，失败返回false
 */
bool resource_monitoring_system_get_config(
    ResourceMonitoringSystem* system,
    ResourceMonitoringConfig* config);

/**
 * @brief 设置系统配置
 * @param system 资源监控系统
 * @param config 配置
 * @return 成功返回true，失败返回false
 */
bool resource_monitoring_system_set_config(
    ResourceMonitoringSystem* system,
    const ResourceMonitoringConfig* config);

/**
 * @brief 重置系统统计
 * @param system 资源监控系统
 * @param type 资源类型，使用RESOURCE_TYPE_ALL重置所有
 * @return 成功返回true，失败返回false
 */
bool resource_monitoring_system_reset_stats(
    ResourceMonitoringSystem* system,
    ResourceType type);

#ifdef __cplusplus
}
#endif

#endif /* QENTL_RESOURCE_MONITORING_SYSTEM_H */ 