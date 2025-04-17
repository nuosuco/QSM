/**
 * @file quantum_bit_adjuster.h
 * @brief 量子比特调整器头文件 - QEntL资源自适应引擎的组件
 * @author QEntL核心开发团队
 * @date 2024-05-19
 * @version 1.0
 *
 * 该文件定义了量子比特调整器的API和数据结构，用于根据设备能力自动调整量子比特的分配和使用策略。
 */

#ifndef QENTL_QUANTUM_BIT_ADJUSTER_H
#define QENTL_QUANTUM_BIT_ADJUSTER_H

#include <stdbool.h>
#include "device_capability_detector.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief 调整策略类型
 */
typedef enum {
    QB_ADJUST_STRATEGY_CONSERVATIVE,    /**< 保守策略 - 优先保证稳定性 */
    QB_ADJUST_STRATEGY_BALANCED,        /**< 平衡策略 - 在性能和稳定性之间平衡 */
    QB_ADJUST_STRATEGY_AGGRESSIVE,      /**< 激进策略 - 优先考虑性能 */
    QB_ADJUST_STRATEGY_ADAPTIVE,        /**< 自适应策略 - 根据运行情况动态调整 */
    QB_ADJUST_STRATEGY_CUSTOM           /**< 自定义策略 - 使用用户提供的调整函数 */
} QBitAdjustStrategy;

/**
 * @brief 调整模式
 */
typedef enum {
    QB_ADJUST_MODE_MANUAL,              /**< 手动模式 - 仅在明确请求时调整 */
    QB_ADJUST_MODE_ONDEMAND,            /**< 按需模式 - 在资源压力高时调整 */
    QB_ADJUST_MODE_PERIODIC,            /**< 周期模式 - 定期调整 */
    QB_ADJUST_MODE_CONTINUOUS           /**< 连续模式 - 持续监控并调整 */
} QBitAdjustMode;

/**
 * @brief 调整结果
 */
typedef enum {
    QB_ADJUST_RESULT_SUCCESS,            /**< 调整成功 */
    QB_ADJUST_RESULT_NO_CHANGE_NEEDED,   /**< 无需调整 */
    QB_ADJUST_RESULT_INSUFFICIENT_QUBITS,/**< 量子比特不足 */
    QB_ADJUST_RESULT_ERROR,              /**< 调整出错 */
    QB_ADJUST_RESULT_NOT_SUPPORTED       /**< 不支持的调整 */
} QBitAdjustResult;

/**
 * @brief 量子比特分配配置
 */
typedef struct {
    unsigned int min_qubits;             /**< 最小量子比特数 */
    unsigned int max_qubits;             /**< 最大量子比特数 */
    unsigned int optimal_qubits;         /**< 最佳量子比特数 */
    unsigned int current_qubits;         /**< 当前量子比特数 */
    float error_tolerance;               /**< 错误容忍度 */
    QBitAdjustStrategy strategy;         /**< 调整策略 */
    QBitAdjustMode mode;                 /**< 调整模式 */
    unsigned int adjust_interval_ms;     /**< 调整间隔(毫秒) */
} QBitAllocConfig;

/**
 * @brief 量子比特使用统计
 */
typedef struct {
    unsigned int allocated_qubits;       /**< 已分配的量子比特数 */
    unsigned int active_qubits;          /**< 活跃的量子比特数 */
    unsigned int peak_qubits;            /**< 峰值量子比特数 */
    unsigned int total_adjustments;      /**< 总调整次数 */
    unsigned int failed_adjustments;     /**< 失败的调整次数 */
    float avg_error_rate;                /**< 平均错误率 */
} QBitUsageStats;

/**
 * @brief 自定义量子比特调整函数类型
 * @param current_qubits 当前量子比特数
 * @param capabilities 设备能力
 * @param stats 使用统计
 * @param context 回调上下文
 * @return 推荐的量子比特数
 */
typedef unsigned int (*CustomQBitAdjustFunc)(
    unsigned int current_qubits,
    const DeviceCapabilities* capabilities,
    const QBitUsageStats* stats,
    void* context);

/**
 * @brief 量子比特调整通知回调函数类型
 * @param old_qubits 旧的量子比特数
 * @param new_qubits 新的量子比特数
 * @param result 调整结果
 * @param context 回调上下文
 */
typedef void (*QBitAdjustNotifyCallback)(
    unsigned int old_qubits,
    unsigned int new_qubits,
    QBitAdjustResult result,
    void* context);

/**
 * @brief 量子比特调整器
 */
typedef struct QuantumBitAdjuster QuantumBitAdjuster;

/**
 * @brief 创建量子比特调整器
 * @param detector 设备能力检测器
 * @param config 量子比特分配配置
 * @return 成功返回调整器指针，失败返回NULL
 */
QuantumBitAdjuster* quantum_bit_adjuster_create(
    DeviceCapabilityDetector* detector,
    const QBitAllocConfig* config);

/**
 * @brief 销毁量子比特调整器
 * @param adjuster 要销毁的调整器
 */
void quantum_bit_adjuster_destroy(QuantumBitAdjuster* adjuster);

/**
 * @brief 设置量子比特分配配置
 * @param adjuster 量子比特调整器
 * @param config 量子比特分配配置
 * @return 成功返回true，失败返回false
 */
bool quantum_bit_adjuster_set_config(
    QuantumBitAdjuster* adjuster,
    const QBitAllocConfig* config);

/**
 * @brief 获取量子比特分配配置
 * @param adjuster 量子比特调整器
 * @param config 用于存储配置的指针
 * @return 成功返回true，失败返回false
 */
bool quantum_bit_adjuster_get_config(
    QuantumBitAdjuster* adjuster,
    QBitAllocConfig* config);

/**
 * @brief 获取量子比特使用统计
 * @param adjuster 量子比特调整器
 * @param stats 用于存储统计的指针
 * @return 成功返回true，失败返回false
 */
bool quantum_bit_adjuster_get_stats(
    QuantumBitAdjuster* adjuster,
    QBitUsageStats* stats);

/**
 * @brief 设置自定义调整函数
 * @param adjuster 量子比特调整器
 * @param adjust_func 调整函数
 * @param context 回调上下文
 * @return 成功返回true，失败返回false
 */
bool quantum_bit_adjuster_set_custom_func(
    QuantumBitAdjuster* adjuster,
    CustomQBitAdjustFunc adjust_func,
    void* context);

/**
 * @brief 设置调整通知回调
 * @param adjuster 量子比特调整器
 * @param callback 回调函数
 * @param context 回调上下文
 */
void quantum_bit_adjuster_set_notify_callback(
    QuantumBitAdjuster* adjuster,
    QBitAdjustNotifyCallback callback,
    void* context);

/**
 * @brief 手动触发量子比特调整
 * @param adjuster 量子比特调整器
 * @return 调整结果
 */
QBitAdjustResult quantum_bit_adjuster_adjust_now(QuantumBitAdjuster* adjuster);

/**
 * @brief 启动自动调整
 * @param adjuster 量子比特调整器
 * @return 成功返回true，失败返回false
 */
bool quantum_bit_adjuster_start_auto(QuantumBitAdjuster* adjuster);

/**
 * @brief 停止自动调整
 * @param adjuster 量子比特调整器
 */
void quantum_bit_adjuster_stop_auto(QuantumBitAdjuster* adjuster);

/**
 * @brief 获取当前推荐的量子比特数
 * @param adjuster 量子比特调整器
 * @return 推荐的量子比特数，失败返回0
 */
unsigned int quantum_bit_adjuster_get_recommended_qubits(
    QuantumBitAdjuster* adjuster);

/**
 * @brief 报告量子比特使用情况
 * @param adjuster 量子比特调整器
 * @param active_qubits 活跃的量子比特数
 * @param error_rate 当前错误率
 */
void quantum_bit_adjuster_report_usage(
    QuantumBitAdjuster* adjuster,
    unsigned int active_qubits,
    float error_rate);

#ifdef __cplusplus
}
#endif

#endif /* QENTL_QUANTUM_BIT_ADJUSTER_H */