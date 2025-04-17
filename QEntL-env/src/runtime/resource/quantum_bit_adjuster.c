/**
 * QEntL量子比特调整器实现
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月20日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "quantum_bit_adjuster.h"

// 默认配置值
#define DEFAULT_MIN_QUBITS 2
#define DEFAULT_MAX_QUBITS 32
#define DEFAULT_TARGET_FIDELITY 0.99
#define DEFAULT_MEMORY_LIMIT_GB 16.0
#define DEFAULT_ERROR_THRESHOLD 0.05
#define DEFAULT_ADJUSTMENT_INTERVAL_MS 1000

// 最大回调函数数量
#define MAX_CALLBACKS 5

// 量子比特调整器结构
struct QuantumBitAdjuster {
    // 设备能力检测器
    DeviceCapabilityDetector* detector;
    
    // 配置
    QuantumBitAdjusterConfig config;
    
    // 状态
    AdjusterStatus status;
    
    // 事件回调
    AdjusterEventCallback callback;
    void* callback_user_data;
    
    // 上次调整时间
    int64_t last_check_time;
    
    // 是否已初始化
    bool initialized;
};

// 获取当前时间戳（毫秒）
static int64_t get_current_time_ms(void) {
    struct timespec ts;
    timespec_get(&ts, TIME_UTC);
    return (int64_t)ts.tv_sec * 1000 + (int64_t)ts.tv_nsec / 1000000;
}

// 触发调整器事件
static void trigger_event(QuantumBitAdjuster* adjuster, AdjusterEventType event_type) {
    if (adjuster->callback) {
        adjuster->callback(event_type, &adjuster->status, adjuster->callback_user_data);
    }
}

// 设置错误信息
static void set_error(QuantumBitAdjuster* adjuster, const char* format, ...) {
    va_list args;
    va_start(args, format);
    vsnprintf(adjuster->status.last_error, sizeof(adjuster->status.last_error), format, args);
    va_end(args);
    
    adjuster->status.failed_operations++;
    printf("量子比特调整器错误: %s\n", adjuster->status.last_error);
}

// 创建量子比特调整器
QuantumBitAdjuster* quantum_bit_adjuster_create(DeviceCapabilityDetector* detector) {
    if (!detector) {
        printf("无法创建量子比特调整器: 设备能力检测器为空\n");
        return NULL;
    }
    
    QuantumBitAdjuster* adjuster = (QuantumBitAdjuster*)malloc(sizeof(QuantumBitAdjuster));
    if (!adjuster) {
        printf("无法创建量子比特调整器: 内存分配失败\n");
        return NULL;
    }
    
    // 初始化结构
    memset(adjuster, 0, sizeof(QuantumBitAdjuster));
    adjuster->detector = detector;
    
    // 设置默认配置
    adjuster->config.min_qubits = DEFAULT_MIN_QUBITS;
    adjuster->config.max_qubits = DEFAULT_MAX_QUBITS;
    adjuster->config.strategy = STRATEGY_BALANCED;
    adjuster->config.mode = MODE_SIMULATION;
    adjuster->config.target_fidelity = DEFAULT_TARGET_FIDELITY;
    adjuster->config.memory_limit_gb = DEFAULT_MEMORY_LIMIT_GB;
    adjuster->config.allow_entanglement_reduction = true;
    adjuster->config.optimize_for_speed = false;
    adjuster->config.error_threshold = DEFAULT_ERROR_THRESHOLD;
    adjuster->config.adjustment_interval_ms = DEFAULT_ADJUSTMENT_INTERVAL_MS;
    
    // 初始化状态
    adjuster->status.current_qubits = 0;
    adjuster->status.recommended_qubits = 0;
    adjuster->status.estimated_fidelity = 1.0;
    adjuster->status.memory_usage_gb = 0.0;
    adjuster->status.cpu_usage = 0.0;
    adjuster->status.is_resource_limited = false;
    adjuster->status.last_adjustment_time = get_current_time_ms();
    adjuster->status.adjustment_count = 0;
    adjuster->status.failed_operations = 0;
    strcpy(adjuster->status.last_error, "");
    
    adjuster->last_check_time = get_current_time_ms();
    adjuster->initialized = true;
    
    // 执行初始调整
    quantum_bit_adjuster_adjust(adjuster);
    
    printf("量子比特调整器已创建\n");
    return adjuster;
}

// 销毁量子比特调整器
void quantum_bit_adjuster_destroy(QuantumBitAdjuster* adjuster) {
    if (adjuster) {
        // 清理资源
        adjuster->callback = NULL;
        adjuster->callback_user_data = NULL;
        
        free(adjuster);
        printf("量子比特调整器已销毁\n");
    }
}

// 设置调整配置
bool quantum_bit_adjuster_set_config(QuantumBitAdjuster* adjuster, const QuantumBitAdjusterConfig* config) {
    if (!adjuster || !config) {
        return false;
    }
    
    // 验证配置有效性
    if (config->min_qubits < 1) {
        set_error(adjuster, "量子比特数最小值不能小于1");
        return false;
    }
    
    if (config->max_qubits < config->min_qubits) {
        set_error(adjuster, "量子比特数最大值不能小于最小值");
        return false;
    }
    
    if (config->target_fidelity <= 0.0 || config->target_fidelity > 1.0) {
        set_error(adjuster, "目标保真度必须在(0,1]范围内");
        return false;
    }
    
    // 应用新配置
    adjuster->config = *config;
    printf("量子比特调整器配置已更新\n");
    
    // 重新调整
    return quantum_bit_adjuster_adjust(adjuster);
}

// 获取当前配置
bool quantum_bit_adjuster_get_config(QuantumBitAdjuster* adjuster, QuantumBitAdjusterConfig* config) {
    if (!adjuster || !config) {
        return false;
    }
    
    *config = adjuster->config;
    return true;
}

// 获取调整器状态
bool quantum_bit_adjuster_get_status(QuantumBitAdjuster* adjuster, AdjusterStatus* status) {
    if (!adjuster || !status) {
        return false;
    }
    
    *status = adjuster->status;
    return true;
}

// 注册事件回调
void quantum_bit_adjuster_register_callback(QuantumBitAdjuster* adjuster, AdjusterEventCallback callback, void* user_data) {
    if (!adjuster) {
        return;
    }
    
    adjuster->callback = callback;
    adjuster->callback_user_data = user_data;
}

// 取消注册事件回调
void quantum_bit_adjuster_unregister_callback(QuantumBitAdjuster* adjuster) {
    if (!adjuster) {
        return;
    }
    
    adjuster->callback = NULL;
    adjuster->callback_user_data = NULL;
}

// 计算基于策略的调整系数
static double calculate_strategy_factor(AdjustmentStrategy strategy) {
    switch (strategy) {
        case STRATEGY_CONSERVATIVE:
            return 0.7;
        case STRATEGY_BALANCED:
            return 1.0;
        case STRATEGY_AGGRESSIVE:
            return 1.3;
        case STRATEGY_ADAPTIVE:
        case STRATEGY_CUSTOM:
        default:
            return 1.0;
    }
}

// 估算量子状态向量大小（字节）
static int64_t estimate_state_vector_size(int num_qubits) {
    // 量子态需要2^n个复数（每个复数用两个双精度浮点数表示）
    return ((int64_t)1 << num_qubits) * 2 * sizeof(double);
}

// 估算量子态模拟所需内存（GB）
static double estimate_memory_usage(int num_qubits, QuantumExecutionMode mode) {
    double memory_gb = 0.0;
    
    switch (mode) {
        case MODE_SIMULATION:
            // 完全模拟需要保存整个状态向量
            memory_gb = (double)estimate_state_vector_size(num_qubits) / (1024.0 * 1024.0 * 1024.0);
            // 额外的工作内存
            memory_gb *= 1.5;
            break;
            
        case MODE_HARDWARE:
            // 硬件模式下内存需求较小（用于控制和结果读取）
            memory_gb = 0.1;
            break;
            
        case MODE_HYBRID:
            // 混合模式下，假设需要模拟部分量子比特
            int simulated_qubits = num_qubits / 2;
            memory_gb = (double)estimate_state_vector_size(simulated_qubits) / (1024.0 * 1024.0 * 1024.0);
            memory_gb *= 1.3;
            break;
    }
    
    return memory_gb;
}

// 估算在特定量子比特和策略下的保真度
static double estimate_fidelity(int num_qubits, double base_fidelity, AdjustmentStrategy strategy) {
    double strategy_factor = calculate_strategy_factor(strategy);
    
    // 随着量子比特数的增加，保真度会下降
    double qubit_penalty = 1.0 - (num_qubits * 0.005 / strategy_factor);
    
    // 确保保真度在有效范围内
    return fmax(0.5, fmin(base_fidelity * qubit_penalty, 1.0));
}

// 执行量子比特数量调整
bool quantum_bit_adjuster_adjust(QuantumBitAdjuster* adjuster) {
    if (!adjuster || !adjuster->initialized) {
        return false;
    }
    
    // 检查是否需要调整（基于时间间隔）
    int64_t current_time = get_current_time_ms();
    if (current_time - adjuster->last_check_time < adjuster->config.adjustment_interval_ms) {
        return true;
    }
    adjuster->last_check_time = current_time;
    
    // 触发开始调整事件
    trigger_event(adjuster, EVENT_ADJUSTMENT_STARTED);
    
    // 获取设备能力
    const DeviceCapability* capability = device_capability_detector_get_capability(adjuster->detector);
    if (!capability) {
        set_error(adjuster, "无法获取设备能力信息");
        return false;
    }
    
    // 从设备能力检测器获取推荐的量子比特数
    int device_recommended_qubits = capability->recommended_qubits;
    
    // 应用策略调整
    double strategy_factor = calculate_strategy_factor(adjuster->config.strategy);
    int adjusted_qubits = (int)(device_recommended_qubits * strategy_factor);
    
    // 根据执行模式调整
    switch (adjuster->config.mode) {
        case MODE_SIMULATION:
            // 检查内存限制
            double memory_usage = estimate_memory_usage(adjusted_qubits, MODE_SIMULATION);
            if (memory_usage > adjuster->config.memory_limit_gb) {
                // 如果超过内存限制，则减少量子比特数
                adjuster->status.is_resource_limited = true;
                trigger_event(adjuster, EVENT_RESOURCE_LIMITATION);
                
                // 找到符合内存限制的最大量子比特数
                while (adjusted_qubits > adjuster->config.min_qubits) {
                    adjusted_qubits--;
                    memory_usage = estimate_memory_usage(adjusted_qubits, MODE_SIMULATION);
                    if (memory_usage <= adjuster->config.memory_limit_gb) {
                        break;
                    }
                }
            } else {
                adjuster->status.is_resource_limited = false;
            }
            break;
            
        case MODE_HARDWARE:
            // 对于硬件模式，直接使用量子处理器的量子比特数
            if (capability->quantum.available) {
                adjusted_qubits = capability->quantum.qubits;
            } else {
                set_error(adjuster, "无法使用硬件模式: 未检测到量子处理器");
                return false;
            }
            break;
            
        case MODE_HYBRID:
            // 混合模式下，平衡经典和量子资源
            adjusted_qubits = (int)(device_recommended_qubits * strategy_factor * 0.8);
            break;
    }
    
    // 确保在配置的限制范围内
    if (adjusted_qubits < adjuster->config.min_qubits) {
        adjusted_qubits = adjuster->config.min_qubits;
    } else if (adjusted_qubits > adjuster->config.max_qubits) {
        adjusted_qubits = adjuster->config.max_qubits;
    }
    
    // 更新状态
    adjuster->status.recommended_qubits = adjusted_qubits;
    adjuster->status.current_qubits = adjusted_qubits;
    adjuster->status.memory_usage_gb = estimate_memory_usage(adjusted_qubits, adjuster->config.mode);
    adjuster->status.estimated_fidelity = estimate_fidelity(adjusted_qubits, 
                                                          adjuster->config.mode == MODE_HARDWARE ? 
                                                          capability->quantum.gate_fidelity : 0.999, 
                                                          adjuster->config.strategy);
    adjuster->status.last_adjustment_time = current_time;
    adjuster->status.adjustment_count++;
    
    // 触发调整完成事件
    trigger_event(adjuster, EVENT_ADJUSTMENT_COMPLETED);
    
    printf("量子比特数已调整: %d\n", adjusted_qubits);
    return true;
}

// 获取建议的量子比特数量
int quantum_bit_adjuster_get_recommended_qubits(QuantumBitAdjuster* adjuster) {
    if (!adjuster || !adjuster->initialized) {
        return 0;
    }
    
    // 检查是否需要重新调整
    int64_t current_time = get_current_time_ms();
    if (current_time - adjuster->last_check_time >= adjuster->config.adjustment_interval_ms) {
        quantum_bit_adjuster_adjust(adjuster);
    }
    
    return adjuster->status.recommended_qubits;
}

// 设置执行模式
bool quantum_bit_adjuster_set_mode(QuantumBitAdjuster* adjuster, QuantumExecutionMode mode) {
    if (!adjuster) {
        return false;
    }
    
    // 如果设置为硬件模式，检查是否有量子处理器
    if (mode == MODE_HARDWARE) {
        const DeviceCapability* capability = device_capability_detector_get_capability(adjuster->detector);
        if (!capability || !capability->quantum.available) {
            set_error(adjuster, "无法设置硬件模式: 未检测到量子处理器");
            return false;
        }
    }
    
    // 更新模式
    adjuster->config.mode = mode;
    
    // 触发模式变更事件
    trigger_event(adjuster, EVENT_MODE_CHANGED);
    
    // 重新调整量子比特数
    return quantum_bit_adjuster_adjust(adjuster);
}

// 获取执行模式
QuantumExecutionMode quantum_bit_adjuster_get_mode(QuantumBitAdjuster* adjuster) {
    if (!adjuster) {
        return MODE_SIMULATION;  // 默认为模拟模式
    }
    
    return adjuster->config.mode;
}

// 设置调整策略
bool quantum_bit_adjuster_set_strategy(QuantumBitAdjuster* adjuster, AdjustmentStrategy strategy) {
    if (!adjuster) {
        return false;
    }
    
    adjuster->config.strategy = strategy;
    
    // 重新调整量子比特数
    return quantum_bit_adjuster_adjust(adjuster);
}

// 获取调整策略
AdjustmentStrategy quantum_bit_adjuster_get_strategy(QuantumBitAdjuster* adjuster) {
    if (!adjuster) {
        return STRATEGY_BALANCED;  // 默认为平衡策略
    }
    
    return adjuster->config.strategy;
}

// 预测特定量子电路在当前设备上的性能
bool quantum_bit_adjuster_predict_performance(QuantumBitAdjuster* adjuster, 
                                            int circuit_qubits, 
                                            int circuit_depth, 
                                            double* estimated_fidelity, 
                                            double* estimated_memory_gb,
                                            double* estimated_time_ms) {
    if (!adjuster || circuit_qubits <= 0 || circuit_depth <= 0) {
        return false;
    }
    
    // 获取设备能力
    const DeviceCapability* capability = device_capability_detector_get_capability(adjuster->detector);
    if (!capability) {
        set_error(adjuster, "无法获取设备能力信息");
        return false;
    }
    
    // 估算内存使用
    if (estimated_memory_gb) {
        *estimated_memory_gb = estimate_memory_usage(circuit_qubits, adjuster->config.mode);
    }
    
    // 估算保真度
    if (estimated_fidelity) {
        // 基础保真度
        double base_fidelity = (adjuster->config.mode == MODE_HARDWARE) ? 
                             capability->quantum.gate_fidelity : 0.999;
        
        // 考虑电路深度对保真度的影响
        double depth_factor = pow(base_fidelity, circuit_depth);
        
        *estimated_fidelity = estimate_fidelity(circuit_qubits, base_fidelity, adjuster->config.strategy) * depth_factor;
    }
    
    // 估算执行时间
    if (estimated_time_ms) {
        double base_time = 0.0;
        
        switch (adjuster->config.mode) {
            case MODE_SIMULATION:
                // 模拟时间随量子比特数指数增长
                base_time = 0.1 * pow(2, circuit_qubits) * circuit_depth;
                break;
                
            case MODE_HARDWARE:
                // 硬件执行时间主要由电路深度决定
                base_time = 10.0 * circuit_depth;
                break;
                
            case MODE_HYBRID:
                // 混合模式
                base_time = 5.0 * pow(2, circuit_qubits / 2) * circuit_depth;
                break;
        }
        
        *estimated_time_ms = base_time;
    }
    
    return true;
}

// 验证量子算法是否适合当前设备
bool quantum_bit_adjuster_validate_algorithm(QuantumBitAdjuster* adjuster, 
                                           int required_qubits, 
                                           int circuit_depth,
                                           double required_fidelity) {
    if (!adjuster || required_qubits <= 0 || circuit_depth <= 0 || required_fidelity <= 0.0 || required_fidelity > 1.0) {
        return false;
    }
    
    // 预测性能
    double estimated_fidelity, estimated_memory_gb;
    if (!quantum_bit_adjuster_predict_performance(adjuster, required_qubits, circuit_depth, 
                                                &estimated_fidelity, &estimated_memory_gb, NULL)) {
        return false;
    }
    
    // 检查量子比特数是否在范围内
    bool qubits_ok = (required_qubits <= adjuster->status.recommended_qubits);
    
    // 检查保真度是否满足要求
    bool fidelity_ok = (estimated_fidelity >= required_fidelity);
    
    // 检查内存使用是否在限制内
    bool memory_ok = (estimated_memory_gb <= adjuster->config.memory_limit_gb);
    
    // 所有条件都满足才返回true
    bool result = qubits_ok && fidelity_ok && memory_ok;
    
    // 如果验证失败，设置错误消息
    if (!result) {
        char error_msg[256] = "";
        if (!qubits_ok) {
            strcat(error_msg, "量子比特数超出设备能力; ");
        }
        if (!fidelity_ok) {
            strcat(error_msg, "预计保真度无法满足要求; ");
        }
        if (!memory_ok) {
            strcat(error_msg, "内存需求超出限制; ");
        }
        
        set_error(adjuster, "算法验证失败: %s", error_msg);
    }
    
    return result;
}

// 估算给定量子状态的内存需求
int64_t quantum_bit_adjuster_estimate_memory_requirements(QuantumBitAdjuster* adjuster, 
                                                        int num_qubits, 
                                                        bool sparse_state) {
    if (!adjuster || num_qubits <= 0) {
        return 0;
    }
    
    int64_t base_size = estimate_state_vector_size(num_qubits);
    
    // 对于稀疏表示，可以显著减少内存需求（但这是一个简单的估计）
    if (sparse_state) {
        // 假设在典型情况下，稀疏表示可以节省约80-95%的内存
        // 具体节省量取决于实际量子态
        return base_size / 10;
    }
    
    return base_size;
}

// 获取设备支持的最大纠缠量子比特数
int quantum_bit_adjuster_get_max_entangled_qubits(QuantumBitAdjuster* adjuster) {
    if (!adjuster) {
        return 0;
    }
    
    const DeviceCapability* capability = device_capability_detector_get_capability(adjuster->detector);
    if (!capability) {
        set_error(adjuster, "无法获取设备能力信息");
        return 0;
    }
    
    // 如果是硬件模式且有量子处理器，返回处理器的最大纠缠量子比特数
    if (adjuster->config.mode == MODE_HARDWARE && capability->quantum.available) {
        return capability->quantum.max_entangled_qubits;
    }
    
    // 对于模拟模式，最大纠缠量子比特数取决于推荐的量子比特数
    return adjuster->status.recommended_qubits;
}

// 重置调整器状态
void quantum_bit_adjuster_reset(QuantumBitAdjuster* adjuster) {
    if (!adjuster) {
        return;
    }
    
    // 重置状态
    adjuster->status.current_qubits = 0;
    adjuster->status.memory_usage_gb = 0.0;
    adjuster->status.cpu_usage = 0.0;
    adjuster->status.is_resource_limited = false;
    adjuster->status.adjustment_count = 0;
    adjuster->status.failed_operations = 0;
    strcpy(adjuster->status.last_error, "");
    
    // 执行初始调整
    quantum_bit_adjuster_adjust(adjuster);
}

// 获取用于表示量子策略的字符串
const char* quantum_bit_adjuster_strategy_to_string(AdjustmentStrategy strategy) {
    switch (strategy) {
        case STRATEGY_CONSERVATIVE:
            return "保守策略";
        case STRATEGY_BALANCED:
            return "平衡策略";
        case STRATEGY_AGGRESSIVE:
            return "激进策略";
        case STRATEGY_ADAPTIVE:
            return "自适应策略";
        case STRATEGY_CUSTOM:
            return "自定义策略";
        default:
            return "未知策略";
    }
}

// 获取用于表示量子执行模式的字符串
const char* quantum_bit_adjuster_mode_to_string(QuantumExecutionMode mode) {
    switch (mode) {
        case MODE_SIMULATION:
            return "模拟模式";
        case MODE_HARDWARE:
            return "硬件模式";
        case MODE_HYBRID:
            return "混合模式";
        default:
            return "未知模式";
    }
}

// 保存调整器状态报告到文件
bool quantum_bit_adjuster_save_report(QuantumBitAdjuster* adjuster, const char* filename) {
    if (!adjuster || !filename) {
        return false;
    }
    
    FILE* file = fopen(filename, "w");
    if (!file) {
        set_error(adjuster, "无法创建报告文件");
        return false;
    }
    
    // 获取设备能力
    const DeviceCapability* capability = device_capability_detector_get_capability(adjuster->detector);
    
    // 写入报告头
    fprintf(file, "QEntL量子比特调整器状态报告\n");
    fprintf(file, "==========================\n\n");
    
    // 报告生成时间
    time_t now = time(NULL);
    char time_str[64];
    struct tm* tm_info = localtime(&now);
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", tm_info);
    fprintf(file, "报告生成时间: %s\n\n", time_str);
    
    // 当前配置
    fprintf(file, "当前配置:\n");
    fprintf(file, "-------------\n");
    fprintf(file, "调整策略: %s\n", quantum_bit_adjuster_strategy_to_string(adjuster->config.strategy));
    fprintf(file, "执行模式: %s\n", quantum_bit_adjuster_mode_to_string(adjuster->config.mode));
    fprintf(file, "最小量子比特数: %d\n", adjuster->config.min_qubits);
    fprintf(file, "最大量子比特数: %d\n", adjuster->config.max_qubits);
    fprintf(file, "目标保真度: %.4f\n", adjuster->config.target_fidelity);
    fprintf(file, "内存限制: %.2f GB\n", adjuster->config.memory_limit_gb);
    fprintf(file, "允许减少纠缠: %s\n", adjuster->config.allow_entanglement_reduction ? "是" : "否");
    fprintf(file, "速度优化: %s\n", adjuster->config.optimize_for_speed ? "是" : "否");
    fprintf(file, "误差阈值: %.4f\n", adjuster->config.error_threshold);
    fprintf(file, "调整间隔: %d 毫秒\n\n", adjuster->config.adjustment_interval_ms);
    
    // 当前状态
    fprintf(file, "当前状态:\n");
    fprintf(file, "-------------\n");
    fprintf(file, "当前量子比特数: %d\n", adjuster->status.current_qubits);
    fprintf(file, "推荐量子比特数: %d\n", adjuster->status.recommended_qubits);
    fprintf(file, "估计保真度: %.4f\n", adjuster->status.estimated_fidelity);
    fprintf(file, "内存使用: %.2f GB\n", adjuster->status.memory_usage_gb);
    fprintf(file, "CPU使用率: %.2f%%\n", adjuster->status.cpu_usage * 100.0);
    fprintf(file, "资源受限: %s\n", adjuster->status.is_resource_limited ? "是" : "否");
    fprintf(file, "调整次数: %d\n", adjuster->status.adjustment_count);
    fprintf(file, "失败操作数: %d\n", adjuster->status.failed_operations);
    fprintf(file, "最后错误: %s\n\n", adjuster->status.last_error);
    
    // 设备信息
    if (capability) {
        fprintf(file, "设备信息:\n");
        fprintf(file, "-------------\n");
        fprintf(file, "设备名称: %s\n", capability->device_name);
        fprintf(file, "操作系统: %s %s\n", device_capability_detector_get_os_type_string(capability->os_type), 
                capability->os_version);
        fprintf(file, "综合性能得分: %.2f/100.0\n", capability->composite_score);
        
        // 量子处理能力
        fprintf(file, "\n量子处理能力:\n");
        if (capability->quantum.available) {
            fprintf(file, "物理量子比特数: %d\n", capability->quantum.qubits);
            fprintf(file, "最大纠缠量子比特数: %d\n", capability->quantum.max_entangled_qubits);
            fprintf(file, "量子比特拓扑结构: %s\n", 
                    capability->quantum.qubit_topology == 0 ? "线性" : 
                    capability->quantum.qubit_topology == 1 ? "网格" : 
                    capability->quantum.qubit_topology == 2 ? "全连接" : "未知");
            fprintf(file, "相干时间: %.2f 微秒\n", capability->quantum.coherence_time_us);
            fprintf(file, "门保真度: %.4f\n", capability->quantum.gate_fidelity);
            fprintf(file, "读取保真度: %.4f\n", capability->quantum.readout_fidelity);
        } else {
            fprintf(file, "未检测到量子处理器\n");
        }
    }
    
    // 性能预测示例
    fprintf(file, "\n性能预测示例:\n");
    fprintf(file, "-------------\n");
    fprintf(file, "量子比特数\t电路深度\t估计保真度\t估计内存\t估计时间(ms)\n");
    
    for (int qubits = 2; qubits <= fmin(20, adjuster->config.max_qubits); qubits += 2) {
        for (int depth = 10; depth <= 100; depth += 90) {
            double estimated_fidelity, estimated_memory_gb, estimated_time_ms;
            if (quantum_bit_adjuster_predict_performance(adjuster, qubits, depth, 
                                                      &estimated_fidelity, &estimated_memory_gb, &estimated_time_ms)) {
                fprintf(file, "%d\t\t%d\t\t%.4f\t\t%.2f GB\t\t%.2f\n", 
                        qubits, depth, estimated_fidelity, estimated_memory_gb, estimated_time_ms);
            }
        }
    }
    
    fclose(file);
    printf("量子比特调整器状态报告已保存到: %s\n", filename);
    return true;
} 