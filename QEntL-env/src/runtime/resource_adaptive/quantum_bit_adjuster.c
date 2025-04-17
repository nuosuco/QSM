/**
 * @file quantum_bit_adjuster.c
 * @brief 量子比特调整器实现 - QEntL资源自适应引擎的组件
 * @author QEntL核心开发团队
 * @date 2024-05-19
 * @version 1.0
 *
 * 该文件实现了量子比特调整器，负责根据设备能力和资源使用情况自动调整量子比特的分配。
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <math.h>

#include "quantum_bit_adjuster.h"
#include "../core/logger.h"
#include "../core/config_manager.h"

/**
 * @brief 量子比特调整器结构体
 */
struct QuantumBitAdjuster {
    /* 关联的设备能力检测器 */
    DeviceCapabilityDetector* detector;
    
    /* 配置 */
    QBitAllocConfig config;
    
    /* 统计数据 */
    QBitUsageStats stats;
    
    /* 自动调整相关 */
    bool auto_adjust_enabled;
    time_t last_adjust_time;
    
    /* 自定义调整函数 */
    CustomQBitAdjustFunc custom_adjust_func;
    void* custom_adjust_context;
    
    /* 调整通知回调 */
    QBitAdjustNotifyCallback notify_callback;
    void* notify_context;
};

/**
 * @brief 使用保守策略计算推荐的量子比特数
 * @param adjuster 量子比特调整器
 * @param capabilities 设备能力
 * @return 推荐的量子比特数
 */
static unsigned int calculate_conservative_qubits(
    QuantumBitAdjuster* adjuster,
    const DeviceCapabilities* capabilities) {
    
    // 保守策略下，我们使用能可靠支持的最小量子比特数
    unsigned int max_supported = capabilities->quantum_hardware.max_qubits;
    unsigned int min_required = adjuster->config.min_qubits;
    
    // 如果设备支持的比特数少于最小要求，则使用设备支持的最大值
    if (max_supported < min_required) {
        return max_supported;
    }
    
    // 计算保守值（设备最大值的70%，但不低于最小要求）
    unsigned int conservative = (unsigned int)(max_supported * 0.7);
    return (conservative > min_required) ? conservative : min_required;
}

/**
 * @brief 使用平衡策略计算推荐的量子比特数
 * @param adjuster 量子比特调整器
 * @param capabilities 设备能力
 * @return 推荐的量子比特数
 */
static unsigned int calculate_balanced_qubits(
    QuantumBitAdjuster* adjuster,
    const DeviceCapabilities* capabilities) {
    
    // 平衡策略下，我们在性能和稳定性之间取得平衡
    unsigned int max_supported = capabilities->quantum_hardware.max_qubits;
    unsigned int min_required = adjuster->config.min_qubits;
    unsigned int optimal = adjuster->config.optimal_qubits;
    
    // 如果设备支持的比特数少于最小要求，则使用设备支持的最大值
    if (max_supported < min_required) {
        return max_supported;
    }
    
    // 如果最佳值已设置，则使用最佳值（但不超过设备支持的最大值）
    if (optimal > 0) {
        return (optimal <= max_supported) ? optimal : max_supported;
    }
    
    // 否则使用设备最大值的85%
    unsigned int balanced = (unsigned int)(max_supported * 0.85);
    return (balanced > min_required) ? balanced : min_required;
}

/**
 * @brief 使用激进策略计算推荐的量子比特数
 * @param adjuster 量子比特调整器
 * @param capabilities 设备能力
 * @return 推荐的量子比特数
 */
static unsigned int calculate_aggressive_qubits(
    QuantumBitAdjuster* adjuster,
    const DeviceCapabilities* capabilities) {
    
    // 激进策略下，我们优先考虑性能，使用接近设备最大能力的量子比特数
    unsigned int max_supported = capabilities->quantum_hardware.max_qubits;
    unsigned int min_required = adjuster->config.min_qubits;
    
    // 如果设备支持的比特数少于最小要求，则使用设备支持的最大值
    if (max_supported < min_required) {
        return max_supported;
    }
    
    // 使用设备最大值的95%
    unsigned int aggressive = (unsigned int)(max_supported * 0.95);
    return (aggressive > min_required) ? aggressive : min_required;
}

/**
 * @brief 使用自适应策略计算推荐的量子比特数
 * @param adjuster 量子比特调整器
 * @param capabilities 设备能力
 * @return 推荐的量子比特数
 */
static unsigned int calculate_adaptive_qubits(
    QuantumBitAdjuster* adjuster,
    const DeviceCapabilities* capabilities) {
    
    // 自适应策略下，我们根据历史使用情况和当前错误率动态调整
    unsigned int max_supported = capabilities->quantum_hardware.max_qubits;
    unsigned int min_required = adjuster->config.min_qubits;
    unsigned int current = adjuster->config.current_qubits;
    
    // 如果设备支持的比特数少于最小要求，则使用设备支持的最大值
    if (max_supported < min_required) {
        return max_supported;
    }
    
    // 如果还没有当前值，从平衡策略开始
    if (current == 0) {
        return calculate_balanced_qubits(adjuster, capabilities);
    }
    
    // 根据使用情况和错误率调整
    float usage_ratio = (float)adjuster->stats.active_qubits / (float)current;
    float error_ratio = adjuster->stats.avg_error_rate / adjuster->config.error_tolerance;
    
    // 如果使用率高，错误率低，增加量子比特
    if (usage_ratio > 0.85 && error_ratio < 0.8) {
        unsigned int new_qubits = (unsigned int)(current * 1.15);
        return (new_qubits <= max_supported) ? new_qubits : max_supported;
    }
    
    // 如果使用率低，减少量子比特
    if (usage_ratio < 0.5) {
        unsigned int new_qubits = (unsigned int)(current * 0.85);
        return (new_qubits >= min_required) ? new_qubits : min_required;
    }
    
    // 如果错误率高，减少量子比特
    if (error_ratio > 1.2) {
        unsigned int new_qubits = (unsigned int)(current * 0.9);
        return (new_qubits >= min_required) ? new_qubits : min_required;
    }
    
    // 如果一切正常，保持当前值
    return current;
}

/**
 * @brief 计算推荐的量子比特数
 * @param adjuster 量子比特调整器
 * @return 推荐的量子比特数
 */
static unsigned int calculate_recommended_qubits(QuantumBitAdjuster* adjuster) {
    DeviceCapabilities capabilities;
    
    // 获取设备能力
    if (!device_capability_detector_get_capabilities(adjuster->detector, &capabilities)) {
        log_error("计算推荐量子比特数失败: 无法获取设备能力");
        return 0;
    }
    
    unsigned int recommended_qubits = 0;
    
    // 根据策略计算推荐值
    switch (adjuster->config.strategy) {
        case QB_ADJUST_STRATEGY_CONSERVATIVE:
            recommended_qubits = calculate_conservative_qubits(adjuster, &capabilities);
            break;
            
        case QB_ADJUST_STRATEGY_BALANCED:
            recommended_qubits = calculate_balanced_qubits(adjuster, &capabilities);
            break;
            
        case QB_ADJUST_STRATEGY_AGGRESSIVE:
            recommended_qubits = calculate_aggressive_qubits(adjuster, &capabilities);
            break;
            
        case QB_ADJUST_STRATEGY_ADAPTIVE:
            recommended_qubits = calculate_adaptive_qubits(adjuster, &capabilities);
            break;
            
        case QB_ADJUST_STRATEGY_CUSTOM:
            if (adjuster->custom_adjust_func) {
                recommended_qubits = adjuster->custom_adjust_func(
                    adjuster->config.current_qubits,
                    &capabilities,
                    &adjuster->stats,
                    adjuster->custom_adjust_context);
            } else {
                // 如果没有自定义函数，回退到平衡策略
                recommended_qubits = calculate_balanced_qubits(adjuster, &capabilities);
            }
            break;
            
        default:
            // 未知策略，使用平衡策略
            recommended_qubits = calculate_balanced_qubits(adjuster, &capabilities);
    }
    
    // 确保推荐值在合理范围内
    if (recommended_qubits < adjuster->config.min_qubits) {
        recommended_qubits = adjuster->config.min_qubits;
    }
    
    if (adjuster->config.max_qubits > 0 && recommended_qubits > adjuster->config.max_qubits) {
        recommended_qubits = adjuster->config.max_qubits;
    }
    
    return recommended_qubits;
}

/**
 * @brief 创建量子比特调整器
 * @param detector 设备能力检测器
 * @param config 量子比特分配配置
 * @return 成功返回调整器指针，失败返回NULL
 */
QuantumBitAdjuster* quantum_bit_adjuster_create(
    DeviceCapabilityDetector* detector,
    const QBitAllocConfig* config) {
    
    if (!detector) {
        log_error("创建量子比特调整器失败: 检测器为NULL");
        return NULL;
    }
    
    QuantumBitAdjuster* adjuster = (QuantumBitAdjuster*)malloc(sizeof(QuantumBitAdjuster));
    if (!adjuster) {
        log_error("创建量子比特调整器失败: 内存分配错误");
        return NULL;
    }
    
    // 初始化结构体
    memset(adjuster, 0, sizeof(QuantumBitAdjuster));
    
    // 关联设备能力检测器
    adjuster->detector = detector;
    
    // 设置配置
    if (config) {
        memcpy(&adjuster->config, config, sizeof(QBitAllocConfig));
    } else {
        // 默认配置
        adjuster->config.min_qubits = 5;
        adjuster->config.max_qubits = 0; // 不限制最大值
        adjuster->config.optimal_qubits = 0; // 未指定最佳值
        adjuster->config.current_qubits = 0; // 尚未分配
        adjuster->config.error_tolerance = 0.05f; // 5%错误容忍度
        adjuster->config.strategy = QB_ADJUST_STRATEGY_BALANCED; // 平衡策略
        adjuster->config.mode = QB_ADJUST_MODE_ONDEMAND; // 按需调整
        adjuster->config.adjust_interval_ms = 60000; // 每分钟调整一次
    }
    
    // 初始化统计数据
    adjuster->stats.allocated_qubits = 0;
    adjuster->stats.active_qubits = 0;
    adjuster->stats.peak_qubits = 0;
    adjuster->stats.total_adjustments = 0;
    adjuster->stats.failed_adjustments = 0;
    adjuster->stats.avg_error_rate = 0.0f;
    
    adjuster->auto_adjust_enabled = false;
    adjuster->last_adjust_time = 0;
    
    adjuster->custom_adjust_func = NULL;
    adjuster->custom_adjust_context = NULL;
    
    adjuster->notify_callback = NULL;
    adjuster->notify_context = NULL;
    
    log_info("量子比特调整器已创建");
    
    return adjuster;
}

/**
 * @brief 销毁量子比特调整器
 * @param adjuster 要销毁的调整器
 */
void quantum_bit_adjuster_destroy(QuantumBitAdjuster* adjuster) {
    if (!adjuster) {
        return;
    }
    
    // 停止自动调整
    quantum_bit_adjuster_stop_auto(adjuster);
    
    // 释放资源
    free(adjuster);
    
    log_info("量子比特调整器已销毁");
}

/**
 * @brief 设置量子比特分配配置
 * @param adjuster 量子比特调整器
 * @param config 量子比特分配配置
 * @return 成功返回true，失败返回false
 */
bool quantum_bit_adjuster_set_config(
    QuantumBitAdjuster* adjuster,
    const QBitAllocConfig* config) {
    
    if (!adjuster || !config) {
        log_error("设置量子比特分配配置失败: 参数无效");
        return false;
    }
    
    // 复制配置
    memcpy(&adjuster->config, config, sizeof(QBitAllocConfig));
    
    log_info("量子比特分配配置已更新: 最小值=%d, 最大值=%d, 策略=%d, 模式=%d",
             adjuster->config.min_qubits,
             adjuster->config.max_qubits,
             adjuster->config.strategy,
             adjuster->config.mode);
    
    return true;
}

/**
 * @brief 获取量子比特分配配置
 * @param adjuster 量子比特调整器
 * @param config 用于存储配置的指针
 * @return 成功返回true，失败返回false
 */
bool quantum_bit_adjuster_get_config(
    QuantumBitAdjuster* adjuster,
    QBitAllocConfig* config) {
    
    if (!adjuster || !config) {
        log_error("获取量子比特分配配置失败: 参数无效");
        return false;
    }
    
    // 复制配置
    memcpy(config, &adjuster->config, sizeof(QBitAllocConfig));
    
    return true;
}

/**
 * @brief 获取量子比特使用统计
 * @param adjuster 量子比特调整器
 * @param stats 用于存储统计的指针
 * @return 成功返回true，失败返回false
 */
bool quantum_bit_adjuster_get_stats(
    QuantumBitAdjuster* adjuster,
    QBitUsageStats* stats) {
    
    if (!adjuster || !stats) {
        log_error("获取量子比特使用统计失败: 参数无效");
        return false;
    }
    
    // 复制统计数据
    memcpy(stats, &adjuster->stats, sizeof(QBitUsageStats));
    
    return true;
}

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
    void* context) {
    
    if (!adjuster) {
        log_error("设置自定义调整函数失败: 调整器为NULL");
        return false;
    }
    
    adjuster->custom_adjust_func = adjust_func;
    adjuster->custom_adjust_context = context;
    
    // 如果设置了自定义函数，自动切换到自定义策略
    if (adjust_func) {
        adjuster->config.strategy = QB_ADJUST_STRATEGY_CUSTOM;
        log_info("已设置自定义调整函数并切换到自定义调整策略");
    } else {
        // 如果取消自定义函数，切换回平衡策略
        adjuster->config.strategy = QB_ADJUST_STRATEGY_BALANCED;
        log_info("已取消自定义调整函数并切换到平衡调整策略");
    }
    
    return true;
}

/**
 * @brief 设置调整通知回调
 * @param adjuster 量子比特调整器
 * @param callback 回调函数
 * @param context 回调上下文
 */
void quantum_bit_adjuster_set_notify_callback(
    QuantumBitAdjuster* adjuster,
    QBitAdjustNotifyCallback callback,
    void* context) {
    
    if (!adjuster) {
        log_error("设置调整通知回调失败: 调整器为NULL");
        return;
    }
    
    adjuster->notify_callback = callback;
    adjuster->notify_context = context;
    
    log_info("已%s量子比特调整通知回调", callback ? "设置" : "取消");
}

/**
 * @brief 手动触发量子比特调整
 * @param adjuster 量子比特调整器
 * @return 调整结果
 */
QBitAdjustResult quantum_bit_adjuster_adjust_now(QuantumBitAdjuster* adjuster) {
    if (!adjuster) {
        log_error("手动触发量子比特调整失败: 调整器为NULL");
        return QB_ADJUST_RESULT_ERROR;
    }
    
    // 计算推荐的量子比特数
    unsigned int recommended_qubits = calculate_recommended_qubits(adjuster);
    if (recommended_qubits == 0) {
        adjuster->stats.failed_adjustments++;
        log_error("量子比特调整失败: 无法计算推荐值");
        return QB_ADJUST_RESULT_ERROR;
    }
    
    // 如果与当前值相同，无需调整
    if (adjuster->config.current_qubits > 0 && recommended_qubits == adjuster->config.current_qubits) {
        log_info("量子比特无需调整: 当前值=%d已是最佳", adjuster->config.current_qubits);
        return QB_ADJUST_RESULT_NO_CHANGE_NEEDED;
    }
    
    // 获取设备能力
    DeviceCapabilities capabilities;
    if (!device_capability_detector_get_capabilities(adjuster->detector, &capabilities)) {
        adjuster->stats.failed_adjustments++;
        log_error("量子比特调整失败: 无法获取设备能力");
        return QB_ADJUST_RESULT_ERROR;
    }
    
    // 检查设备是否支持推荐的量子比特数
    if (recommended_qubits > capabilities.quantum_hardware.max_qubits) {
        // 如果推荐值超过了设备能力，调整为设备支持的最大值
        recommended_qubits = capabilities.quantum_hardware.max_qubits;
        
        if (recommended_qubits < adjuster->config.min_qubits) {
            // 如果设备支持的最大值低于最小要求，报告错误
            adjuster->stats.failed_adjustments++;
            log_error("量子比特调整失败: 设备支持的最大量子比特数(%d)低于最小要求(%d)",
                    capabilities.quantum_hardware.max_qubits,
                    adjuster->config.min_qubits);
            
            // 调用通知回调
            if (adjuster->notify_callback) {
                adjuster->notify_callback(
                    adjuster->config.current_qubits,
                    0,
                    QB_ADJUST_RESULT_INSUFFICIENT_QUBITS,
                    adjuster->notify_context);
            }
            
            return QB_ADJUST_RESULT_INSUFFICIENT_QUBITS;
        }
    }
    
    // 保存旧值用于通知
    unsigned int old_qubits = adjuster->config.current_qubits;
    
    // 更新当前值
    adjuster->config.current_qubits = recommended_qubits;
    
    // 更新统计数据
    adjuster->stats.allocated_qubits = recommended_qubits;
    adjuster->stats.total_adjustments++;
    
    if (recommended_qubits > adjuster->stats.peak_qubits) {
        adjuster->stats.peak_qubits = recommended_qubits;
    }
    
    adjuster->last_adjust_time = time(NULL);
    
    log_info("量子比特已调整: %d -> %d", old_qubits, recommended_qubits);
    
    // 调用通知回调
    if (adjuster->notify_callback) {
        adjuster->notify_callback(
            old_qubits,
            recommended_qubits,
            QB_ADJUST_RESULT_SUCCESS,
            adjuster->notify_context);
    }
    
    return QB_ADJUST_RESULT_SUCCESS;
}

/**
 * @brief 启动自动调整
 * @param adjuster 量子比特调整器
 * @return 成功返回true，失败返回false
 */
bool quantum_bit_adjuster_start_auto(QuantumBitAdjuster* adjuster) {
    if (!adjuster) {
        log_error("启动自动调整失败: 调整器为NULL");
        return false;
    }
    
    if (adjuster->auto_adjust_enabled) {
        log_warning("自动调整已经启动");
        return true;
    }
    
    adjuster->auto_adjust_enabled = true;
    
    // 注意: 实际实现应该启动一个线程或使用事件循环来定期调整
    // 在这个简化版本中，我们仅设置标志
    
    log_info("自动量子比特调整已启动，模式: %d, 间隔: %dms",
             adjuster->config.mode,
             adjuster->config.adjust_interval_ms);
    
    return true;
}

/**
 * @brief 停止自动调整
 * @param adjuster 量子比特调整器
 */
void quantum_bit_adjuster_stop_auto(QuantumBitAdjuster* adjuster) {
    if (!adjuster) {
        log_error("停止自动调整失败: 调整器为NULL");
        return;
    }
    
    if (!adjuster->auto_adjust_enabled) {
        return;
    }
    
    adjuster->auto_adjust_enabled = false;
    
    // 注意: 实际实现应该停止调整线程
    
    log_info("自动量子比特调整已停止");
}

/**
 * @brief 获取当前推荐的量子比特数
 * @param adjuster 量子比特调整器
 * @return 推荐的量子比特数，失败返回0
 */
unsigned int quantum_bit_adjuster_get_recommended_qubits(QuantumBitAdjuster* adjuster) {
    if (!adjuster) {
        log_error("获取推荐量子比特数失败: 调整器为NULL");
        return 0;
    }
    
    // 计算推荐的量子比特数
    return calculate_recommended_qubits(adjuster);
}

/**
 * @brief 报告量子比特使用情况
 * @param adjuster 量子比特调整器
 * @param active_qubits 活跃的量子比特数
 * @param error_rate 当前错误率
 */
void quantum_bit_adjuster_report_usage(
    QuantumBitAdjuster* adjuster,
    unsigned int active_qubits,
    float error_rate) {
    
    if (!adjuster) {
        log_error("报告量子比特使用情况失败: 调整器为NULL");
        return;
    }
    
    // 更新统计数据
    adjuster->stats.active_qubits = active_qubits;
    
    // 更新平均错误率（简单移动平均）
    if (adjuster->stats.avg_error_rate == 0.0f) {
        adjuster->stats.avg_error_rate = error_rate;
    } else {
        adjuster->stats.avg_error_rate = adjuster->stats.avg_error_rate * 0.7f + error_rate * 0.3f;
    }
    
    // 根据模式决定是否需要调整
    if (adjuster->auto_adjust_enabled) {
        time_t now = time(NULL);
        bool should_adjust = false;
        
        switch (adjuster->config.mode) {
            case QB_ADJUST_MODE_ONDEMAND:
                // 按需模式：如果资源压力高或错误率超出容忍度，则调整
                if (active_qubits > (adjuster->config.current_qubits * 0.9) ||
                    error_rate > adjuster->config.error_tolerance) {
                    should_adjust = true;
                }
                break;
                
            case QB_ADJUST_MODE_PERIODIC:
                // 周期模式：根据设定的间隔定期调整
                if (difftime(now, adjuster->last_adjust_time) * 1000 >= adjuster->config.adjust_interval_ms) {
                    should_adjust = true;
                }
                break;
                
            case QB_ADJUST_MODE_CONTINUOUS:
                // 连续模式：总是尝试调整
                should_adjust = true;
                break;
                
            case QB_ADJUST_MODE_MANUAL:
            default:
                // 手动模式：不自动调整
                should_adjust = false;
        }
        
        // 如果需要调整，执行调整
        if (should_adjust) {
            quantum_bit_adjuster_adjust_now(adjuster);
        }
    }
}