/**
 * QEntL量子比特调整器实现
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月25日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include "qubits_adjuster.h"
#include "../../common/logger.h"
#include "../../common/timer.h"

#define MAX_CALLBACKS 10
#define MAX_HISTORY_SIZE 100
#define MAX_REASON_LENGTH 128

/**
 * 调整历史记录项
 */
typedef struct {
    int old_qubits;
    int new_qubits;
    time_t timestamp;
    char reason[MAX_REASON_LENGTH];
    AdjustTrigger trigger;
} AdjustmentHistoryItem;

/**
 * 量子比特调整器结构体
 */
struct QubitsAdjuster {
    QubitsAdjusterConfig config;              // 调整器配置
    QubitsAdjusterState state;                // 当前状态
    
    DeviceCapabilityDetector* detector;       // 设备能力检测器
    ResourceMonitor* monitor;                 // 资源监控器
    
    int current_qubits;                       // 当前量子比特数
    char last_adjustment_reason[MAX_REASON_LENGTH]; // 最后一次调整原因
    
    // 性能历史记录
    PerformanceMetrics recent_metrics;        // 最近的性能指标
    PerformanceMetrics avg_metrics;           // 平均性能指标
    
    // 调整统计
    int adjustment_count;                     // 总调整次数
    int upward_adjustments;                   // 向上调整次数
    int downward_adjustments;                 // 向下调整次数
    
    // 历史记录
    AdjustmentHistoryItem history[MAX_HISTORY_SIZE]; // 调整历史
    int history_count;                        // 历史记录数量
    
    // 回调
    QubitsAdjustmentCallback callbacks[MAX_CALLBACKS]; // 回调函数数组
    void* callback_user_data[MAX_CALLBACKS];  // 回调用户数据
    int callback_count;                       // 回调数量
    
    // 定时器ID
    int timer_id;                             // 定期调整的定时器ID
    
    // 日志
    int log_level;                            // 日志级别
    
    // 锁定期
    time_t last_adjustment_time;              // 上次调整时间
    bool in_stability_period;                 // 是否在稳定期内
    
    // 分析数据
    double avg_circuit_complexity;            // 平均电路复杂度
    double avg_execution_time;                // 平均执行时间
    double error_rate_trend;                  // 错误率趋势
};

// 前向声明私有函数
static void qubits_adjuster_timer_callback(void* user_data);
static bool perform_adjustment(QubitsAdjuster* adjuster, int new_qubits, AdjustTrigger trigger, const char* reason);
static int calculate_optimal_qubits(QubitsAdjuster* adjuster);
static void add_history_item(QubitsAdjuster* adjuster, int old_qubits, int new_qubits, AdjustTrigger trigger, const char* reason);
static void notify_callbacks(QubitsAdjuster* adjuster, int old_qubits, int new_qubits);
static double calculate_resource_pressure(QubitsAdjuster* adjuster);
static int get_step_size(QubitsAdjuster* adjuster, bool increase);
static bool is_stability_period_active(QubitsAdjuster* adjuster);
static void update_performance_metrics(QubitsAdjuster* adjuster, const PerformanceMetrics* metrics);
static bool can_device_handle_qubits(QubitsAdjuster* adjuster, int qubits);

/**
 * 创建量子比特调整器
 */
QubitsAdjuster* qubits_adjuster_create(const QubitsAdjusterConfig* config) {
    if (config == NULL) {
        LOG_ERROR("无法创建量子比特调整器: 配置为空");
        return NULL;
    }
    
    QubitsAdjuster* adjuster = (QubitsAdjuster*)malloc(sizeof(QubitsAdjuster));
    if (adjuster == NULL) {
        LOG_ERROR("无法分配量子比特调整器内存");
        return NULL;
    }
    
    // 初始化结构体
    memset(adjuster, 0, sizeof(QubitsAdjuster));
    
    // 复制配置
    memcpy(&adjuster->config, config, sizeof(QubitsAdjusterConfig));
    
    // 设置初始状态
    adjuster->state = ADJUSTER_STATE_INACTIVE;
    adjuster->current_qubits = config->initial_qubits;
    adjuster->log_level = 1; // 默认日志级别
    
    LOG_INFO("量子比特调整器创建成功，初始量子比特数: %d", adjuster->current_qubits);
    
    return adjuster;
}

/**
 * 销毁量子比特调整器
 */
void qubits_adjuster_destroy(QubitsAdjuster* adjuster) {
    if (adjuster == NULL) {
        return;
    }
    
    // 停止定时器
    if (adjuster->timer_id != 0) {
        timer_stop(adjuster->timer_id);
    }
    
    // 释放资源
    LOG_INFO("量子比特调整器销毁，总调整次数: %d", adjuster->adjustment_count);
    free(adjuster);
}

/**
 * 初始化量子比特调整器
 */
bool qubits_adjuster_initialize(QubitsAdjuster* adjuster, 
                               DeviceCapabilityDetector* detector,
                               ResourceMonitor* monitor) {
    if (adjuster == NULL || detector == NULL || monitor == NULL) {
        LOG_ERROR("量子比特调整器初始化失败: 参数为空");
        return false;
    }
    
    adjuster->state = ADJUSTER_STATE_INITIALIZING;
    adjuster->detector = detector;
    adjuster->monitor = monitor;
    
    // 根据设备能力进行初始调整
    DeviceCapability* capability = device_capability_detector_get_capability(detector);
    if (capability == NULL) {
        LOG_ERROR("无法获取设备能力信息");
        adjuster->state = ADJUSTER_STATE_ERROR;
        return false;
    }
    
    // 根据设备量子能力调整初始量子比特数
    if (capability->quantum_capability.supported) {
        int device_max_qubits = capability->quantum_capability.max_qubits;
        if (device_max_qubits < adjuster->config.initial_qubits) {
            LOG_WARNING("设备支持的最大量子比特数(%d)小于配置的初始值(%d)，自动调整",
                      device_max_qubits, adjuster->config.initial_qubits);
            adjuster->current_qubits = device_max_qubits;
        }
    } else {
        // 设备不支持量子处理，尝试使用模拟
        if (adjuster->config.use_quantum_simulation) {
            LOG_WARNING("设备不支持量子处理，使用量子模拟模式");
            // 限制模拟模式下的量子比特数
            if (adjuster->current_qubits > 24) {
                LOG_WARNING("模拟模式下限制量子比特数为24");
                adjuster->current_qubits = 24;
            }
        } else {
            LOG_ERROR("设备不支持量子处理，且未启用模拟模式");
            adjuster->state = ADJUSTER_STATE_ERROR;
            return false;
        }
    }
    
    // 记录初始化调整
    sprintf(adjuster->last_adjustment_reason, "初始化根据设备能力调整");
    add_history_item(adjuster, adjuster->config.initial_qubits, adjuster->current_qubits, 
                    ADJUST_TRIGGER_MANUAL, "初始化调整");
    
    adjuster->state = ADJUSTER_STATE_ACTIVE;
    LOG_INFO("量子比特调整器初始化成功，当前量子比特数: %d", adjuster->current_qubits);
    
    return true;
}

/**
 * 启动量子比特调整器
 */
bool qubits_adjuster_start(QubitsAdjuster* adjuster) {
    if (adjuster == NULL) {
        LOG_ERROR("量子比特调整器启动失败: 调整器为空");
        return false;
    }
    
    if (adjuster->state == ADJUSTER_STATE_ACTIVE) {
        LOG_WARNING("量子比特调整器已经处于活跃状态");
        return true;
    }
    
    if (adjuster->state == ADJUSTER_STATE_ERROR) {
        LOG_ERROR("量子比特调整器处于错误状态，无法启动");
        return false;
    }
    
    // 如果是定时触发模式，设置定时器
    if (adjuster->config.trigger == ADJUST_TRIGGER_TIME &&
        adjuster->config.mode != ADJUST_MODE_STATIC) {
        adjuster->timer_id = timer_start(adjuster->config.adjust_interval_ms, 
                                       qubits_adjuster_timer_callback, 
                                       adjuster);
        if (adjuster->timer_id == 0) {
            LOG_ERROR("无法启动调整定时器");
            return false;
        }
    }
    
    adjuster->state = ADJUSTER_STATE_ACTIVE;
    LOG_INFO("量子比特调整器启动成功");
    
    return true;
}

/**
 * 暂停量子比特调整器
 */
void qubits_adjuster_pause(QubitsAdjuster* adjuster) {
    if (adjuster == NULL) {
        return;
    }
    
    if (adjuster->state != ADJUSTER_STATE_ACTIVE) {
        LOG_WARNING("量子比特调整器不处于活跃状态，无法暂停");
        return;
    }
    
    // 暂停定时器
    if (adjuster->timer_id != 0) {
        timer_pause(adjuster->timer_id);
    }
    
    adjuster->state = ADJUSTER_STATE_PAUSED;
    LOG_INFO("量子比特调整器已暂停");
}

/**
 * 恢复量子比特调整器
 */
void qubits_adjuster_resume(QubitsAdjuster* adjuster) {
    if (adjuster == NULL) {
        return;
    }
    
    if (adjuster->state != ADJUSTER_STATE_PAUSED) {
        LOG_WARNING("量子比特调整器不处于暂停状态，无法恢复");
        return;
    }
    
    // 恢复定时器
    if (adjuster->timer_id != 0) {
        timer_resume(adjuster->timer_id);
    }
    
    adjuster->state = ADJUSTER_STATE_ACTIVE;
    LOG_INFO("量子比特调整器已恢复");
}

/**
 * 停止量子比特调整器
 */
void qubits_adjuster_stop(QubitsAdjuster* adjuster) {
    if (adjuster == NULL) {
        return;
    }
    
    // 停止定时器
    if (adjuster->timer_id != 0) {
        timer_stop(adjuster->timer_id);
        adjuster->timer_id = 0;
    }
    
    adjuster->state = ADJUSTER_STATE_INACTIVE;
    LOG_INFO("量子比特调整器已停止");
}

/**
 * 获取当前推荐的量子比特数
 */
int qubits_adjuster_get_current_qubits(QubitsAdjuster* adjuster) {
    if (adjuster == NULL) {
        LOG_ERROR("无法获取量子比特数: 调整器为空");
        return 0;
    }
    
    return adjuster->current_qubits;
}

/**
 * 手动设置量子比特数
 */
bool qubits_adjuster_set_qubits(QubitsAdjuster* adjuster, int qubits) {
    if (adjuster == NULL) {
        LOG_ERROR("无法设置量子比特数: 调整器为空");
        return false;
    }
    
    // 检查范围
    if (qubits < adjuster->config.min_qubits || qubits > adjuster->config.max_qubits) {
        LOG_ERROR("量子比特数 %d 超出允许范围 [%d, %d]", 
                qubits, adjuster->config.min_qubits, adjuster->config.max_qubits);
        return false;
    }
    
    // 检查设备能力
    if (!can_device_handle_qubits(adjuster, qubits)) {
        LOG_ERROR("当前设备无法处理 %d 个量子比特", qubits);
        return false;
    }
    
    return perform_adjustment(adjuster, qubits, ADJUST_TRIGGER_MANUAL, "手动设置");
}

/**
 * 获取量子比特调整器状态
 */
QubitsAdjusterState qubits_adjuster_get_state(QubitsAdjuster* adjuster) {
    if (adjuster == NULL) {
        LOG_ERROR("无法获取状态: 调整器为空");
        return ADJUSTER_STATE_ERROR;
    }
    
    return adjuster->state;
}

/**
 * 注册调整事件回调
 */
bool qubits_adjuster_register_callback(QubitsAdjuster* adjuster, 
                                      QubitsAdjustmentCallback callback,
                                      void* user_data) {
    if (adjuster == NULL || callback == NULL) {
        LOG_ERROR("无法注册回调: 参数为空");
        return false;
    }
    
    if (adjuster->callback_count >= MAX_CALLBACKS) {
        LOG_ERROR("无法注册更多回调: 已达到最大数量");
        return false;
    }
    
    // 检查是否已经注册
    for (int i = 0; i < adjuster->callback_count; i++) {
        if (adjuster->callbacks[i] == callback) {
            LOG_WARNING("回调已经注册");
            return true;
        }
    }
    
    // 添加回调
    adjuster->callbacks[adjuster->callback_count] = callback;
    adjuster->callback_user_data[adjuster->callback_count] = user_data;
    adjuster->callback_count++;
    
    LOG_INFO("已注册量子比特调整回调，当前回调数: %d", adjuster->callback_count);
    
    return true;
}

/**
 * 取消注册调整事件回调
 */
bool qubits_adjuster_unregister_callback(QubitsAdjuster* adjuster, 
                                        QubitsAdjustmentCallback callback) {
    if (adjuster == NULL || callback == NULL) {
        LOG_ERROR("无法取消注册回调: 参数为空");
        return false;
    }
    
    // 查找回调
    int index = -1;
    for (int i = 0; i < adjuster->callback_count; i++) {
        if (adjuster->callbacks[i] == callback) {
            index = i;
            break;
        }
    }
    
    if (index == -1) {
        LOG_WARNING("回调未注册，无法取消");
        return false;
    }
    
    // 移除回调（通过移动后面的元素）
    for (int i = index; i < adjuster->callback_count - 1; i++) {
        adjuster->callbacks[i] = adjuster->callbacks[i + 1];
        adjuster->callback_user_data[i] = adjuster->callback_user_data[i + 1];
    }
    
    adjuster->callback_count--;
    LOG_INFO("已取消注册量子比特调整回调，当前回调数: %d", adjuster->callback_count);
    
    return true;
}

/**
 * 提供性能指标进行调整
 */
void qubits_adjuster_provide_metrics(QubitsAdjuster* adjuster, 
                                   const PerformanceMetrics* metrics) {
    if (adjuster == NULL || metrics == NULL) {
        LOG_ERROR("无法提供性能指标: 参数为空");
        return;
    }
    
    if (adjuster->state != ADJUSTER_STATE_ACTIVE) {
        return; // 非活跃状态不处理
    }
    
    // 更新性能指标
    update_performance_metrics(adjuster, metrics);
    
    // 如果在静态模式或稳定期内，不进行调整
    if (adjuster->config.mode == ADJUST_MODE_STATIC || is_stability_period_active(adjuster)) {
        return;
    }
    
    // 根据性能指标决定是否需要调整
    if (adjuster->config.trigger == ADJUST_TRIGGER_PERFORMANCE) {
        // 检查性能是否低于阈值
        if (metrics->execution_time > adjuster->avg_metrics.execution_time * (1.0 + adjuster->config.performance_threshold)) {
            // 性能下降，考虑减少量子比特
            int new_qubits = adjuster->current_qubits - get_step_size(adjuster, false);
            if (new_qubits >= adjuster->config.min_qubits) {
                perform_adjustment(adjuster, new_qubits, ADJUST_TRIGGER_PERFORMANCE, "性能下降");
            }
        }
        // 检查是否可以增加量子比特以提高精度
        else if (metrics->success_probability > 0.9 && 
                 metrics->error_rate < adjuster->config.error_threshold) {
            int new_qubits = adjuster->current_qubits + get_step_size(adjuster, true);
            if (new_qubits <= adjuster->config.max_qubits && can_device_handle_qubits(adjuster, new_qubits)) {
                perform_adjustment(adjuster, new_qubits, ADJUST_TRIGGER_PERFORMANCE, "性能良好，提高精度");
            }
        }
    }
    else if (adjuster->config.trigger == ADJUST_TRIGGER_ERROR) {
        // 检查错误率是否超过阈值
        if (metrics->error_rate > adjuster->config.error_threshold) {
            // 错误率高，考虑减少量子比特
            int new_qubits = adjuster->current_qubits - get_step_size(adjuster, false);
            if (new_qubits >= adjuster->config.min_qubits) {
                perform_adjustment(adjuster, new_qubits, ADJUST_TRIGGER_ERROR, "错误率过高");
            }
        }
    }
    
    // 适应模式下的额外检查
    if (adjuster->config.mode == ADJUST_MODE_ADAPTIVE) {
        // 检查电路复杂度与纠缠水平的匹配度
        double complexity_factor = (metrics->circuit_depth * metrics->gate_complexity) / 
                                  adjuster->avg_circuit_complexity;
        double entanglement_factor = metrics->entanglement_level / 0.5; // 以0.5作为基准
        
        if (complexity_factor > 1.5 && entanglement_factor > 1.2) {
            // 复杂度和纠缠度都高，考虑增加量子比特
            int new_qubits = adjuster->current_qubits + get_step_size(adjuster, true);
            if (new_qubits <= adjuster->config.max_qubits && can_device_handle_qubits(adjuster, new_qubits)) {
                perform_adjustment(adjuster, new_qubits, ADJUST_TRIGGER_PERFORMANCE, 
                                 "电路复杂度和纠缠度高，增加量子比特");
            }
        }
    }
    
    // 预测模式下的分析
    if (adjuster->config.mode == ADJUST_MODE_PREDICTIVE) {
        // 基于历史趋势预测未来需求
        // 此处简化实现，实际应用可使用更复杂的预测算法
        if (adjuster->error_rate_trend > 0.1) { // 错误率呈上升趋势
            int new_qubits = adjuster->current_qubits - get_step_size(adjuster, false);
            if (new_qubits >= adjuster->config.min_qubits) {
                perform_adjustment(adjuster, new_qubits, ADJUST_TRIGGER_PERFORMANCE, 
                                 "预测错误率将上升，提前调整");
            }
        }
    }
}

/**
 * 手动触发量子比特调整
 */
bool qubits_adjuster_trigger_adjustment(QubitsAdjuster* adjuster) {
    if (adjuster == NULL) {
        LOG_ERROR("无法触发调整: 调整器为空");
        return false;
    }
    
    if (adjuster->state != ADJUSTER_STATE_ACTIVE) {
        LOG_ERROR("调整器不处于活跃状态，无法触发调整");
        return false;
    }
    
    // 计算最佳量子比特数
    int optimal_qubits = calculate_optimal_qubits(adjuster);
    
    if (optimal_qubits == adjuster->current_qubits) {
        LOG_INFO("当前量子比特数已经是最佳值，无需调整");
        return true;
    }
    
    return perform_adjustment(adjuster, optimal_qubits, ADJUST_TRIGGER_MANUAL, "手动触发优化");
}

/**
 * 获取调整统计信息
 */
bool qubits_adjuster_get_stats(QubitsAdjuster* adjuster, 
                              int* adjustments_count,
                              int* upward_adjustments,
                              int* downward_adjustments) {
    if (adjuster == NULL) {
        LOG_ERROR("无法获取统计信息: 调整器为空");
        return false;
    }
    
    if (adjustments_count != NULL) {
        *adjustments_count = adjuster->adjustment_count;
    }
    
    if (upward_adjustments != NULL) {
        *upward_adjustments = adjuster->upward_adjustments;
    }
    
    if (downward_adjustments != NULL) {
        *downward_adjustments = adjuster->downward_adjustments;
    }
    
    return true;
}

/**
 * 更新调整器配置
 */
bool qubits_adjuster_update_config(QubitsAdjuster* adjuster, 
                                  const QubitsAdjusterConfig* config) {
    if (adjuster == NULL || config == NULL) {
        LOG_ERROR("无法更新配置: 参数为空");
        return false;
    }
    
    // 保存旧定时器设置
    int old_interval = adjuster->config.adjust_interval_ms;
    AdjustTrigger old_trigger = adjuster->config.trigger;
    AdjustMode old_mode = adjuster->config.mode;
    
    // 更新配置
    memcpy(&adjuster->config, config, sizeof(QubitsAdjusterConfig));
    
    // 如果定时器相关设置变更，需要重新配置定时器
    if (adjuster->timer_id != 0 && 
        (old_interval != config->adjust_interval_ms || 
         old_trigger != config->trigger ||
         old_mode != config->mode)) {
        
        // 停止旧定时器
        timer_stop(adjuster->timer_id);
        adjuster->timer_id = 0;
        
        // 如果仍然需要定时器，重新启动
        if (config->trigger == ADJUST_TRIGGER_TIME &&
            config->mode != ADJUST_MODE_STATIC && 
            adjuster->state == ADJUSTER_STATE_ACTIVE) {
            
            adjuster->timer_id = timer_start(config->adjust_interval_ms, 
                                          qubits_adjuster_timer_callback, 
                                          adjuster);
            if (adjuster->timer_id == 0) {
                LOG_ERROR("无法重新启动调整定时器");
                return false;
            }
        }
    }
    
    LOG_INFO("量子比特调整器配置已更新");
    return true;
}

/**
 * 获取调整器配置
 */
bool qubits_adjuster_get_config(QubitsAdjuster* adjuster, 
                               QubitsAdjusterConfig* config) {
    if (adjuster == NULL || config == NULL) {
        LOG_ERROR("无法获取配置: 参数为空");
        return false;
    }
    
    memcpy(config, &adjuster->config, sizeof(QubitsAdjusterConfig));
    return true;
}

/**
 * 获取最后一次调整的原因
 */
const char* qubits_adjuster_get_last_adjustment_reason(QubitsAdjuster* adjuster) {
    if (adjuster == NULL) {
        LOG_ERROR("无法获取调整原因: 调整器为空");
        return NULL;
    }
    
    return adjuster->last_adjustment_reason;
}

/**
 * 重置调整器状态
 */
bool qubits_adjuster_reset(QubitsAdjuster* adjuster) {
    if (adjuster == NULL) {
        LOG_ERROR("无法重置: 调整器为空");
        return false;
    }
    
    // 停止活动的定时器
    if (adjuster->timer_id != 0) {
        timer_stop(adjuster->timer_id);
        adjuster->timer_id = 0;
    }
    
    // 重置统计信息
    adjuster->adjustment_count = 0;
    adjuster->upward_adjustments = 0;
    adjuster->downward_adjustments = 0;
    
    // 重置性能指标
    memset(&adjuster->recent_metrics, 0, sizeof(PerformanceMetrics));
    memset(&adjuster->avg_metrics, 0, sizeof(PerformanceMetrics));
    
    // 重置历史记录
    adjuster->history_count = 0;
    
    // 重置状态
    adjuster->state = ADJUSTER_STATE_INACTIVE;
    
    // 恢复到初始量子比特数
    adjuster->current_qubits = adjuster->config.initial_qubits;
    
    // 清空最后调整原因
    strcpy(adjuster->last_adjustment_reason, "重置到初始状态");
    
    LOG_INFO("量子比特调整器已重置到初始状态");
    return true;
}

/**
 * 设置日志级别
 */
void qubits_adjuster_set_log_level(QubitsAdjuster* adjuster, int log_level) {
    if (adjuster == NULL) {
        return;
    }
    
    adjuster->log_level = log_level;
}

/**
 * 分析电路复杂度并建议合适的量子比特数
 */
int qubits_adjuster_analyze_circuit(QubitsAdjuster* adjuster,
                                  int circuit_size,
                                  int circuit_depth,
                                  double entanglement_degree) {
    if (adjuster == NULL) {
        LOG_ERROR("无法分析电路: 调整器为空");
        return 0;
    }
    
    // 简单分析逻辑
    // 1. 基准: 从当前量子比特数开始
    int suggested_qubits = adjuster->current_qubits;
    
    // 2. 根据电路大小调整
    double size_factor = (double)circuit_size / 100.0;  // 基准: 100个门
    suggested_qubits = (int)(suggested_qubits * (0.8 + 0.4 * size_factor));
    
    // 3. 根据电路深度调整
    double depth_factor = (double)circuit_depth / 20.0;  // 基准: 深度20
    suggested_qubits = (int)(suggested_qubits * (0.9 + 0.2 * depth_factor));
    
    // 4. 根据纠缠度调整
    suggested_qubits = (int)(suggested_qubits * (0.8 + 0.4 * entanglement_degree));
    
    // 5. 确保在界限内
    if (suggested_qubits < adjuster->config.min_qubits) {
        suggested_qubits = adjuster->config.min_qubits;
    }
    if (suggested_qubits > adjuster->config.max_qubits) {
        suggested_qubits = adjuster->config.max_qubits;
    }
    
    // 6. 检查设备能力
    DeviceCapability* capability = device_capability_detector_get_capability(adjuster->detector);
    if (capability != NULL && capability->quantum_capability.supported) {
        int device_max_qubits = capability->quantum_capability.max_qubits;
        if (suggested_qubits > device_max_qubits) {
            suggested_qubits = device_max_qubits;
        }
    }
    
    LOG_INFO("电路分析建议量子比特数: %d (电路大小: %d, 深度: %d, 纠缠度: %.2f)",
           suggested_qubits, circuit_size, circuit_depth, entanglement_degree);
    
    return suggested_qubits;
}

/**
 * 检查当前设备是否可以处理指定数量的量子比特
 */
bool qubits_adjuster_can_handle(QubitsAdjuster* adjuster, int qubits) {
    if (adjuster == NULL) {
        LOG_ERROR("无法检查设备能力: 调整器为空");
        return false;
    }
    
    return can_device_handle_qubits(adjuster, qubits);
}

/**
 * 获取当前设备的量子比特容量范围
 */
bool qubits_adjuster_get_capacity_range(QubitsAdjuster* adjuster,
                                       int* min_qubits,
                                       int* max_qubits,
                                       int* optimal_qubits) {
    if (adjuster == NULL) {
        LOG_ERROR("无法获取容量范围: 调整器为空");
        return false;
    }
    
    DeviceCapability* capability = device_capability_detector_get_capability(adjuster->detector);
    if (capability == NULL) {
        LOG_ERROR("无法获取设备能力信息");
        return false;
    }
    
    // 获取设备支持的最大量子比特数
    int device_max = adjuster->config.max_qubits;
    if (capability->quantum_capability.supported) {
        device_max = capability->quantum_capability.max_qubits;
    } else if (adjuster->config.use_quantum_simulation) {
        // 模拟模式下的限制
        device_max = 24;
    } else {
        LOG_ERROR("设备不支持量子处理，且未启用模拟模式");
        return false;
    }
    
    // 设置返回值
    if (min_qubits != NULL) {
        *min_qubits = adjuster->config.min_qubits;
    }
    
    if (max_qubits != NULL) {
        *max_qubits = (device_max < adjuster->config.max_qubits) ? 
                      device_max : adjuster->config.max_qubits;
    }
    
    if (optimal_qubits != NULL) {
        // 计算当前最佳量子比特数
        *optimal_qubits = calculate_optimal_qubits(adjuster);
    }
    
    return true;
}

/**
 * 生成量子比特调整报告
 */
bool qubits_adjuster_generate_report(QubitsAdjuster* adjuster, const char* filename) {
    if (adjuster == NULL || filename == NULL) {
        LOG_ERROR("无法生成报告: 参数为空");
        return false;
    }
    
    FILE* file = fopen(filename, "w");
    if (file == NULL) {
        LOG_ERROR("无法打开文件 %s 用于写入报告", filename);
        return false;
    }
    
    // 写入报告头
    fprintf(file, "量子比特调整器报告\n");
    fprintf(file, "生成时间: %s\n", __DATE__ " " __TIME__);
    fprintf(file, "-------------------------------------------\n\n");
    
    // 写入当前配置
    fprintf(file, "当前配置:\n");
    fprintf(file, "  初始量子比特数: %d\n", adjuster->config.initial_qubits);
    fprintf(file, "  最小量子比特数: %d\n", adjuster->config.min_qubits);
    fprintf(file, "  最大量子比特数: %d\n", adjuster->config.max_qubits);
    fprintf(file, "  调整策略: %d\n", adjuster->config.strategy);
    fprintf(file, "  调整模式: %d\n", adjuster->config.mode);
    fprintf(file, "  触发条件: %d\n", adjuster->config.trigger);
    fprintf(file, "  启用压缩: %s\n", adjuster->config.enable_compression ? "是" : "否");
    fprintf(file, "  使用模拟: %s\n", adjuster->config.use_quantum_simulation ? "是" : "否");
    fprintf(file, "  启用错误缓解: %s\n", adjuster->config.enable_error_mitigation ? "是" : "否");
    fprintf(file, "\n");
    
    // 写入当前状态
    fprintf(file, "当前状态:\n");
    fprintf(file, "  状态: %d\n", adjuster->state);
    fprintf(file, "  当前量子比特数: %d\n", adjuster->current_qubits);
    fprintf(file, "  最后调整原因: %s\n", adjuster->last_adjustment_reason);
    fprintf(file, "\n");
    
    // 写入统计信息
    fprintf(file, "调整统计:\n");
    fprintf(file, "  总调整次数: %d\n", adjuster->adjustment_count);
    fprintf(file, "  向上调整次数: %d\n", adjuster->upward_adjustments);
    fprintf(file, "  向下调整次数: %d\n", adjuster->downward_adjustments);
    fprintf(file, "\n");
    
    // 写入当前性能指标
    fprintf(file, "当前性能指标:\n");
    fprintf(file, "  电路深度: %.2f\n", adjuster->recent_metrics.circuit_depth);
    fprintf(file, "  门复杂度: %.2f\n", adjuster->recent_metrics.gate_complexity);
    fprintf(file, "  纠缠水平: %.2f\n", adjuster->recent_metrics.entanglement_level);
    fprintf(file, "  执行时间: %.2f ms\n", adjuster->recent_metrics.execution_time);
    fprintf(file, "  错误率: %.2f\n", adjuster->recent_metrics.error_rate);
    fprintf(file, "  成功概率: %.2f\n", adjuster->recent_metrics.success_probability);
    fprintf(file, "\n");
    
    // 写入历史记录
    fprintf(file, "调整历史记录:\n");
    for (int i = 0; i < adjuster->history_count; i++) {
        AdjustmentHistoryItem* item = &adjuster->history[i];
        char time_str[30];
        struct tm* tm_info = localtime(&item->timestamp);
        strftime(time_str, 30, "%Y-%m-%d %H:%M:%S", tm_info);
        
        fprintf(file, "  [%s] %d -> %d 原因: %s\n",
               time_str, item->old_qubits, item->new_qubits, item->reason);
    }
    
    fclose(file);
    LOG_INFO("量子比特调整报告已生成: %s", filename);
    
    return true;
}

/**
 * 定时器回调函数
 */
static void qubits_adjuster_timer_callback(void* user_data) {
    QubitsAdjuster* adjuster = (QubitsAdjuster*)user_data;
    if (adjuster == NULL || adjuster->state != ADJUSTER_STATE_ACTIVE) {
        return;
    }
    
    // 如果在稳定期内，不进行调整
    if (is_stability_period_active(adjuster)) {
        return;
    }
    
    // 计算当前资源压力
    double resource_pressure = calculate_resource_pressure(adjuster);
    
    // 根据资源压力判断是否需要调整
    if (resource_pressure > adjuster->config.resource_threshold) {
        // 资源压力高，考虑减少量子比特
        int step = get_step_size(adjuster, false);
        int new_qubits = adjuster->current_qubits - step;
        
        if (new_qubits >= adjuster->config.min_qubits) {
            char reason[MAX_REASON_LENGTH];
            sprintf(reason, "资源压力高 (%.2f)，减少量子比特", resource_pressure);
            perform_adjustment(adjuster, new_qubits, ADJUST_TRIGGER_RESOURCE, reason);
        }
    }
    else if (resource_pressure < 0.5 * adjuster->config.resource_threshold) {
        // 资源充裕，考虑增加量子比特
        int step = get_step_size(adjuster, true);
        int new_qubits = adjuster->current_qubits + step;
        
        if (new_qubits <= adjuster->config.max_qubits && can_device_handle_qubits(adjuster, new_qubits)) {
            char reason[MAX_REASON_LENGTH];
            sprintf(reason, "资源充足 (%.2f)，增加量子比特", resource_pressure);
            perform_adjustment(adjuster, new_qubits, ADJUST_TRIGGER_RESOURCE, reason);
        }
    }
    else {
        // 资源压力适中，考虑优化当前配置
        int optimal_qubits = calculate_optimal_qubits(adjuster);
        
        if (optimal_qubits != adjuster->current_qubits) {
            char reason[MAX_REASON_LENGTH];
            sprintf(reason, "优化量子比特配置 (资源压力: %.2f)", resource_pressure);
            perform_adjustment(adjuster, optimal_qubits, ADJUST_TRIGGER_TIME, reason);
        }
    }
}

/**
 * 执行调整
 */
static bool perform_adjustment(QubitsAdjuster* adjuster, int new_qubits, AdjustTrigger trigger, const char* reason) {
    if (adjuster->state != ADJUSTER_STATE_ACTIVE && adjuster->state != ADJUSTER_STATE_INITIALIZING) {
        LOG_ERROR("调整器不处于活跃或初始化状态，无法执行调整");
        return false;
    }
    
    if (new_qubits < adjuster->config.min_qubits || new_qubits > adjuster->config.max_qubits) {
        LOG_ERROR("新量子比特数 %d 超出允许范围 [%d, %d]", 
                new_qubits, adjuster->config.min_qubits, adjuster->config.max_qubits);
        return false;
    }
    
    // 如果量子比特数没有变化，不执行调整
    if (new_qubits == adjuster->current_qubits) {
        return true;
    }
    
    // 变更状态为调整中
    QubitsAdjusterState previous_state = adjuster->state;
    adjuster->state = ADJUSTER_STATE_ADJUSTING;
    
    // 记录旧的值和调整信息
    int old_qubits = adjuster->current_qubits;
    time_t now = time(NULL);
    adjuster->last_adjustment_time = now;
    
    // 调整量子比特数
    adjuster->current_qubits = new_qubits;
    
    // 更新调整计数
    adjuster->adjustment_count++;
    if (new_qubits > old_qubits) {
        adjuster->upward_adjustments++;
    } else {
        adjuster->downward_adjustments++;
    }
    
    // 更新调整原因
    strncpy(adjuster->last_adjustment_reason, reason, MAX_REASON_LENGTH - 1);
    adjuster->last_adjustment_reason[MAX_REASON_LENGTH - 1] = '\0';
    
    // 添加历史记录
    add_history_item(adjuster, old_qubits, new_qubits, trigger, reason);
    
    // 通知回调
    notify_callbacks(adjuster, old_qubits, new_qubits);
    
    // 如果调整为增加比特，且启用了错误缓解，进行校准
    if (new_qubits > old_qubits && adjuster->config.enable_error_mitigation) {
        adjuster->state = ADJUSTER_STATE_CALIBRATING;
        // 在这里执行校准逻辑
        // ...
    }
    
    // 恢复之前的状态（一般是活跃状态）
    adjuster->state = previous_state;
    
    LOG_INFO("量子比特已调整: %d -> %d 原因: %s", old_qubits, new_qubits, reason);
    
    return true;
}

/**
 * 计算最佳量子比特数
 */
static int calculate_optimal_qubits(QubitsAdjuster* adjuster) {
    // 获取设备能力
    DeviceCapability* capability = device_capability_detector_get_capability(adjuster->detector);
    if (capability == NULL) {
        // 无法获取能力信息，返回当前值
        return adjuster->current_qubits;
    }
    
    // 获取资源使用情况
    ResourceStatus status;
    if (!resource_monitor_get_status(adjuster->monitor, &status)) {
        // 无法获取资源状态，返回当前值
        return adjuster->current_qubits;
    }
    
    // 基于设备量子能力和资源使用情况计算最佳量子比特数
    int optimal_qubits = adjuster->config.optimal_qubits;
    
    // 如果设备支持量子处理
    if (capability->quantum_capability.supported) {
        int device_max_qubits = capability->quantum_capability.max_qubits;
        // 调整最佳值，不超过设备最大支持
        if (optimal_qubits > device_max_qubits) {
            optimal_qubits = device_max_qubits;
        }
        
        // 根据量子处理器性能调整
        double processor_factor = capability->quantum_capability.processor_performance / 100.0;
        optimal_qubits = (int)(optimal_qubits * (0.7 + 0.3 * processor_factor));
    } else if (adjuster->config.use_quantum_simulation) {
        // 使用模拟模式
        // 根据CPU和内存资源调整
        double cpu_usage = status.cpu_usage / 100.0;
        double memory_usage = status.memory_usage / 100.0;
        
        // 资源使用率高时减少量子比特
        if (cpu_usage > 0.8 || memory_usage > 0.8) {
            optimal_qubits = (int)(optimal_qubits * 0.7);
        }
        
        // 模拟模式下的上限
        if (optimal_qubits > 24) {
            optimal_qubits = 24;
        }
    } else {
        // 不支持量子处理且不使用模拟，返回最小值
        optimal_qubits = adjuster->config.min_qubits;
    }
    
    // 确保在配置的范围内
    if (optimal_qubits < adjuster->config.min_qubits) {
        optimal_qubits = adjuster->config.min_qubits;
    }
    if (optimal_qubits > adjuster->config.max_qubits) {
        optimal_qubits = adjuster->config.max_qubits;
    }
    
    return optimal_qubits;
}

/**
 * 添加历史记录项
 */
static void add_history_item(QubitsAdjuster* adjuster, int old_qubits, int new_qubits, 
                            AdjustTrigger trigger, const char* reason) {
    // 如果历史记录已满，移除最旧的记录
    if (adjuster->history_count >= MAX_HISTORY_SIZE) {
        // 移动所有元素，覆盖第一个
        for (int i = 0; i < MAX_HISTORY_SIZE - 1; i++) {
            adjuster->history[i] = adjuster->history[i + 1];
        }
        adjuster->history_count = MAX_HISTORY_SIZE - 1;
    }
    
    // 添加新记录
    AdjustmentHistoryItem* item = &adjuster->history[adjuster->history_count];
    item->old_qubits = old_qubits;
    item->new_qubits = new_qubits;
    item->timestamp = time(NULL);
    item->trigger = trigger;
    strncpy(item->reason, reason, MAX_REASON_LENGTH - 1);
    item->reason[MAX_REASON_LENGTH - 1] = '\0';
    
    adjuster->history_count++;
}

/**
 * 通知所有回调
 */
static void notify_callbacks(QubitsAdjuster* adjuster, int old_qubits, int new_qubits) {
    for (int i = 0; i < adjuster->callback_count; i++) {
        if (adjuster->callbacks[i] != NULL) {
            adjuster->callbacks[i](old_qubits, new_qubits, adjuster->callback_user_data[i]);
        }
    }
}

/**
 * 计算资源压力
 */
static double calculate_resource_pressure(QubitsAdjuster* adjuster) {
    // 获取资源使用情况
    ResourceStatus status;
    if (!resource_monitor_get_status(adjuster->monitor, &status)) {
        // 无法获取资源状态，返回中等压力
        return 0.5;
    }
    
    // 计算综合资源压力
    double cpu_pressure = status.cpu_usage / 100.0;
    double memory_pressure = status.memory_usage / 100.0;
    double storage_pressure = status.storage_usage / 100.0;
    
    // 不同资源的权重
    double cpu_weight = 0.5;
    double memory_weight = 0.3;
    double storage_weight = 0.2;
    
    // 量子特定资源（如有）
    if (status.has_quantum_status) {
        double quantum_pressure = status.quantum_resource_usage / 100.0;
        // 重新分配权重
        cpu_weight = 0.3;
        memory_weight = 0.2;
        storage_weight = 0.1;
        // 加入量子资源权重
        return cpu_weight * cpu_pressure + 
               memory_weight * memory_pressure + 
               storage_weight * storage_pressure + 
               0.4 * quantum_pressure;
    }
    
    // 常规资源压力计算
    return cpu_weight * cpu_pressure + 
           memory_weight * memory_pressure + 
           storage_weight * storage_pressure;
}

/**
 * 获取调整步长
 */
static int get_step_size(QubitsAdjuster* adjuster, bool increase) {
    int base_step = 1;
    
    // 根据调整策略确定步长
    switch (adjuster->config.strategy) {
        case ADJUST_STRATEGY_CONSERVATIVE:
            // 保守策略: 小步长
            base_step = 1;
            break;
            
        case ADJUST_STRATEGY_MODERATE:
            // 适中策略
            base_step = 2;
            break;
            
        case ADJUST_STRATEGY_AGGRESSIVE:
            // 激进策略: 大步长
            base_step = 4;
            break;
            
        case ADJUST_STRATEGY_AUTO:
            // 自动策略: 根据当前量子比特数和历史调整效果动态确定
            base_step = 1 + (adjuster->current_qubits / 10);
            
            // 根据历史调整效果调整步长
            if (adjuster->history_count > 1) {
                // 检查最近两次调整是否方向一致
                AdjustmentHistoryItem* last = &adjuster->history[adjuster->history_count - 1];
                AdjustmentHistoryItem* prev = &adjuster->history[adjuster->history_count - 2];
                
                bool last_increased = (last->new_qubits > last->old_qubits);
                bool prev_increased = (prev->new_qubits > prev->old_qubits);
                
                // 如果连续两次调整方向一致，增大步长
                if ((last_increased && prev_increased && increase) || 
                    (!last_increased && !prev_increased && !increase)) {
                    base_step += 1;
                }
            }
            break;
    }
    
    // 使用配置的调整步长或计算的值
    if (adjuster->config.adjustment_step > 0) {
        base_step = adjuster->config.adjustment_step;
    }
    
    // 对于向下调整，可以使用更激进的步长
    if (!increase && adjuster->config.strategy == ADJUST_STRATEGY_AGGRESSIVE) {
        base_step = base_step * 2;
    }
    
    // 确保步长至少为1
    return (base_step > 0) ? base_step : 1;
}

/**
 * 检查是否在稳定期内
 */
static bool is_stability_period_active(QubitsAdjuster* adjuster) {
    if (adjuster->config.stability_period <= 0) {
        return false;
    }
    
    time_t now = time(NULL);
    double diff_seconds = difftime(now, adjuster->last_adjustment_time);
    
    // 转换为毫秒
    int diff_ms = (int)(diff_seconds * 1000);
    
    return diff_ms < adjuster->config.stability_period;
}

/**
 * 更新性能指标
 */
static void update_performance_metrics(QubitsAdjuster* adjuster, const PerformanceMetrics* metrics) {
    // 保存最近的指标
    memcpy(&adjuster->recent_metrics, metrics, sizeof(PerformanceMetrics));
    
    // 更新平均指标 (简单指数移动平均)
    double alpha = 0.3; // 平滑因子
    
    adjuster->avg_metrics.circuit_depth = alpha * metrics->circuit_depth + 
                                        (1 - alpha) * adjuster->avg_metrics.circuit_depth;
    
    adjuster->avg_metrics.gate_complexity = alpha * metrics->gate_complexity + 
                                          (1 - alpha) * adjuster->avg_metrics.gate_complexity;
    
    adjuster->avg_metrics.entanglement_level = alpha * metrics->entanglement_level + 
                                             (1 - alpha) * adjuster->avg_metrics.entanglement_level;
    
    adjuster->avg_metrics.execution_time = alpha * metrics->execution_time + 
                                         (1 - alpha) * adjuster->avg_metrics.execution_time;
    
    adjuster->avg_metrics.error_rate = alpha * metrics->error_rate + 
                                     (1 - alpha) * adjuster->avg_metrics.error_rate;
    
    adjuster->avg_metrics.success_probability = alpha * metrics->success_probability + 
                                              (1 - alpha) * adjuster->avg_metrics.success_probability;
    
    // 更新错误率趋势
    adjuster->error_rate_trend = metrics->error_rate - adjuster->avg_metrics.error_rate;
    
    // 更新电路复杂度
    double complexity = metrics->circuit_depth * metrics->gate_complexity;
    adjuster->avg_circuit_complexity = alpha * complexity + 
                                     (1 - alpha) * adjuster->avg_circuit_complexity;
    
    // 更新执行时间
    adjuster->avg_execution_time = alpha * metrics->execution_time + 
                                 (1 - alpha) * adjuster->avg_execution_time;
}

/**
 * 检查设备是否能处理指定数量的量子比特
 */
static bool can_device_handle_qubits(QubitsAdjuster* adjuster, int qubits) {
    DeviceCapability* capability = device_capability_detector_get_capability(adjuster->detector);
    if (capability == NULL) {
        return false;
    }
    
    // 如果设备支持量子处理
    if (capability->quantum_capability.supported) {
        return qubits <= capability->quantum_capability.max_qubits;
    }
    
    // 如果使用量子模拟
    if (adjuster->config.use_quantum_simulation) {
        // 检查CPU和内存
        double cpu_cores = capability->cpu_capability.core_count;
        double memory_gb = capability->memory_capability.total_size / (1024.0 * 1024.0 * 1024.0);
        
        // 简单估算：每个量子比特需要的资源
        double cores_needed = 0.5 * pow(2, qubits/5); // 指数级增长但较缓慢
        double memory_needed = 0.01 * pow(2, qubits); // GB, 指数级增长
        
        return (cores_needed <= cpu_cores) && (memory_needed <= memory_gb);
    }
    
    return false;
} 