/**
 * QEntL量子模拟控制器实现
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月22日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "quantum_simulation_controller.h"
#include "device_capability_detector.h"
#include "quantum_bit_adjuster.h"

// 默认配置值
#define DEFAULT_PRECISION PRECISION_DOUBLE
#define DEFAULT_METHOD METHOD_STATE_VECTOR
#define DEFAULT_MODE MODE_STANDARD
#define DEFAULT_MAX_RUNTIME_MS 60000 // 1分钟
#define DEFAULT_MAX_MEMORY_GB 16.0
#define DEFAULT_CHECKPOINTING_INTERVAL 1000 // 1000步

// 最大回调函数数量
#define MAX_CALLBACKS 5

// 控制器内部状态
typedef enum {
    CONTROLLER_IDLE,
    CONTROLLER_RUNNING,
    CONTROLLER_PAUSED,
    CONTROLLER_ERROR
} ControllerState;

// 量子模拟控制器结构
struct QuantumSimulationController {
    // 设备能力检测器
    DeviceCapabilityDetector* detector;
    
    // 量子比特调整器
    QuantumBitAdjuster* adjuster;
    
    // 配置
    SimulationConfig config;
    
    // 内部状态
    ControllerState state;
    SimulationStatistics stats;
    
    // 事件回调
    SimulationEventCallback callbacks[MAX_CALLBACKS];
    void* callback_user_data[MAX_CALLBACKS];
    int callback_count;
    
    // 加速设备信息
    struct {
        bool gpu_available;
        bool quantum_processor_available;
        int gpu_memory_mb;
        int quantum_qubits;
    } acceleration_info;
    
    // 错误信息
    char last_error[256];
    
    // 模拟运行时参数
    int64_t simulation_start_time;
    int64_t simulation_end_time;
    bool abort_requested;
    
    // 检查点数据
    char checkpoint_file[256];
    bool checkpointing_enabled;
    
    // 是否已初始化
    bool initialized;
};

// 获取当前时间戳（毫秒）
static int64_t get_current_time_ms(void) {
    struct timespec ts;
    timespec_get(&ts, TIME_UTC);
    return (int64_t)ts.tv_sec * 1000 + (int64_t)ts.tv_nsec / 1000000;
}

// 设置错误信息
static void set_error(QuantumSimulationController* controller, const char* format, ...) {
    va_list args;
    va_start(args, format);
    vsnprintf(controller->last_error, sizeof(controller->last_error), format, args);
    va_end(args);
    
    controller->state = CONTROLLER_ERROR;
    printf("量子模拟控制器错误: %s\n", controller->last_error);
}

// 触发模拟事件
static void trigger_event(QuantumSimulationController* controller, SimulationEventType event_type) {
    for (int i = 0; i < controller->callback_count; i++) {
        if (controller->callbacks[i]) {
            controller->callbacks[i](event_type, &controller->stats, controller->callback_user_data[i]);
        }
    }
}

// 估算内存需求(GB)
static double estimate_memory_requirement(SimulationMethod method, SimulationPrecision precision, int qubits, int circuit_depth) {
    double base_size = 0.0;
    
    // 根据方法估算基础内存需求
    switch (method) {
        case METHOD_STATE_VECTOR:
            // 状态向量大小: 2^n * 复数大小
            base_size = pow(2, qubits);
            break;
            
        case METHOD_DENSITY_MATRIX:
            // 密度矩阵大小: 2^n * 2^n * 复数大小
            base_size = pow(2, 2 * qubits);
            break;
            
        case METHOD_MPS:
            // 矩阵乘积状态通常需要更少的内存
            base_size = qubits * pow(2, 4) * circuit_depth;
            break;
            
        case METHOD_STABILIZER:
            // 稳定器模拟对特定电路内存需求较小
            base_size = qubits * qubits;
            break;
            
        default:
            base_size = pow(2, qubits);
    }
    
    // 根据精度调整内存大小
    double precision_factor = (precision == PRECISION_SINGLE) ? 1.0 : 2.0;
    
    // 复数包含实部和虚部
    double complex_factor = 2.0;
    
    // 将字节转换为GB
    double memory_gb = (base_size * precision_factor * complex_factor) / (1024 * 1024 * 1024);
    
    // 额外的开销(工作内存等)
    double overhead_factor = 1.2;
    
    return memory_gb * overhead_factor;
}

// 创建量子模拟控制器
QuantumSimulationController* quantum_simulation_controller_create(DeviceCapabilityDetector* detector, QuantumBitAdjuster* adjuster) {
    if (!detector || !adjuster) {
        printf("无法创建量子模拟控制器: 设备能力检测器或量子比特调整器为空\n");
        return NULL;
    }
    
    QuantumSimulationController* controller = (QuantumSimulationController*)malloc(sizeof(QuantumSimulationController));
    if (!controller) {
        printf("无法创建量子模拟控制器: 内存分配失败\n");
        return NULL;
    }
    
    // 初始化结构
    memset(controller, 0, sizeof(QuantumSimulationController));
    controller->detector = detector;
    controller->adjuster = adjuster;
    
    // 设置默认配置
    controller->config.method = DEFAULT_METHOD;
    controller->config.precision = DEFAULT_PRECISION;
    controller->config.mode = DEFAULT_MODE;
    controller->config.acceleration = ACCEL_AUTO;
    controller->config.max_runtime_ms = DEFAULT_MAX_RUNTIME_MS;
    controller->config.max_memory_gb = DEFAULT_MAX_MEMORY_GB;
    controller->config.enable_checkpointing = true;
    controller->config.checkpointing_interval = DEFAULT_CHECKPOINTING_INTERVAL;
    
    // 初始化状态
    controller->state = CONTROLLER_IDLE;
    memset(&controller->stats, 0, sizeof(SimulationStatistics));
    controller->callback_count = 0;
    controller->abort_requested = false;
    controller->checkpointing_enabled = true;
    strcpy(controller->checkpoint_file, "quantum_sim_checkpoint.dat");
    
    // 检测加速设备
    const DeviceCapability* capability = device_capability_detector_get_capability(detector);
    if (capability) {
        controller->acceleration_info.gpu_available = capability->gpu.available;
        controller->acceleration_info.gpu_memory_mb = capability->gpu.memory_mb;
        controller->acceleration_info.quantum_processor_available = capability->quantum.available;
        controller->acceleration_info.quantum_qubits = capability->quantum.physical_qubits;
    }
    
    controller->initialized = true;
    printf("量子模拟控制器已创建\n");
    return controller;
}

// 销毁量子模拟控制器
void quantum_simulation_controller_destroy(QuantumSimulationController* controller) {
    if (controller) {
        // 确保模拟已停止
        if (controller->state == CONTROLLER_RUNNING) {
            quantum_simulation_controller_stop(controller);
        }
        
        // 清理资源
        controller->callback_count = 0;
        
        free(controller);
        printf("量子模拟控制器已销毁\n");
    }
}

// 设置模拟配置
bool quantum_simulation_controller_set_config(QuantumSimulationController* controller, const SimulationConfig* config) {
    if (!controller || !config) {
        return false;
    }
    
    if (controller->state == CONTROLLER_RUNNING) {
        set_error(controller, "无法在模拟运行时更改配置");
        return false;
    }
    
    controller->config = *config;
    printf("量子模拟控制器配置已更新\n");
    return true;
}

// 获取当前配置
bool quantum_simulation_controller_get_config(QuantumSimulationController* controller, SimulationConfig* config) {
    if (!controller || !config) {
        return false;
    }
    
    *config = controller->config;
    return true;
}

// 注册事件回调
bool quantum_simulation_controller_register_callback(QuantumSimulationController* controller, SimulationEventCallback callback, void* user_data) {
    if (!controller || !callback) {
        return false;
    }
    
    if (controller->callback_count >= MAX_CALLBACKS) {
        set_error(controller, "已达到最大回调函数数量");
        return false;
    }
    
    controller->callbacks[controller->callback_count] = callback;
    controller->callback_user_data[controller->callback_count] = user_data;
    controller->callback_count++;
    
    return true;
}

// 取消注册事件回调
bool quantum_simulation_controller_unregister_callback(QuantumSimulationController* controller, SimulationEventCallback callback) {
    if (!controller || !callback) {
        return false;
    }
    
    for (int i = 0; i < controller->callback_count; i++) {
        if (controller->callbacks[i] == callback) {
            // 移除该回调
            for (int j = i; j < controller->callback_count - 1; j++) {
                controller->callbacks[j] = controller->callbacks[j + 1];
                controller->callback_user_data[j] = controller->callback_user_data[j + 1];
            }
            
            controller->callback_count--;
            return true;
        }
    }
    
    return false;  // 未找到该回调
}

// 准备模拟
static bool prepare_simulation(QuantumSimulationController* controller, int num_qubits, int circuit_depth) {
    // 检查参数
    if (num_qubits <= 0 || circuit_depth <= 0) {
        set_error(controller, "无效的量子比特数或电路深度");
        return false;
    }
    
    // 估算内存需求
    double estimated_memory = estimate_memory_requirement(
        controller->config.method, 
        controller->config.precision,
        num_qubits,
        circuit_depth
    );
    
    // 检查内存限制
    if (estimated_memory > controller->config.max_memory_gb) {
        set_error(controller, "模拟内存需求(%.2f GB)超过限制(%.2f GB)", 
                 estimated_memory, controller->config.max_memory_gb);
        return false;
    }
    
    // 根据设备能力选择适当的加速方式
    if (controller->config.acceleration == ACCEL_AUTO) {
        // 自动选择加速方式
        if (controller->acceleration_info.quantum_processor_available && 
            num_qubits <= controller->acceleration_info.quantum_qubits) {
            controller->stats.selected_acceleration = ACCEL_QUANTUM;
        } else if (controller->acceleration_info.gpu_available && 
                  estimated_memory * 1024 <= controller->acceleration_info.gpu_memory_mb) {
            controller->stats.selected_acceleration = ACCEL_GPU;
        } else {
            controller->stats.selected_acceleration = ACCEL_CPU;
        }
    } else {
        controller->stats.selected_acceleration = controller->config.acceleration;
    }
    
    // 更新统计信息
    controller->stats.num_qubits = num_qubits;
    controller->stats.circuit_depth = circuit_depth;
    controller->stats.estimated_memory_gb = estimated_memory;
    controller->stats.method = controller->config.method;
    controller->stats.precision = controller->config.precision;
    controller->stats.mode = controller->config.mode;
    
    return true;
}

// 运行模拟
bool quantum_simulation_controller_run(QuantumSimulationController* controller, int num_qubits, int circuit_depth) {
    if (!controller) {
        return false;
    }
    
    if (controller->state == CONTROLLER_RUNNING) {
        set_error(controller, "模拟已在运行中");
        return false;
    }
    
    // 准备模拟
    if (!prepare_simulation(controller, num_qubits, circuit_depth)) {
        return false;
    }
    
    // 重置状态
    controller->stats.progress = 0.0;
    controller->stats.elapsed_time_ms = 0;
    controller->stats.gates_processed = 0;
    controller->stats.checkpoint_count = 0;
    controller->abort_requested = false;
    
    // 更新状态
    controller->state = CONTROLLER_RUNNING;
    controller->simulation_start_time = get_current_time_ms();
    
    // 触发开始事件
    trigger_event(controller, EVENT_SIMULATION_STARTED);
    
    // 在实际实现中，这里会启动模拟线程或过程
    // 为了示例，我们假设模拟立即完成

    // 模拟进度更新 (在实际实现中，这个会在单独的线程中周期性更新)
    controller->stats.progress = 100.0;
    controller->simulation_end_time = get_current_time_ms();
    controller->stats.elapsed_time_ms = controller->simulation_end_time - controller->simulation_start_time;
    controller->stats.gates_processed = circuit_depth * num_qubits;
    
    // 更新状态
    controller->state = CONTROLLER_IDLE;
    
    // 触发完成事件
    trigger_event(controller, EVENT_SIMULATION_COMPLETED);
    
    printf("量子模拟已完成，用时: %d 毫秒\n", (int)controller->stats.elapsed_time_ms);
    return true;
}

// 停止模拟
bool quantum_simulation_controller_stop(QuantumSimulationController* controller) {
    if (!controller) {
        return false;
    }
    
    if (controller->state != CONTROLLER_RUNNING && controller->state != CONTROLLER_PAUSED) {
        // 不在运行，无需停止
        return true;
    }
    
    // 请求中止
    controller->abort_requested = true;
    
    // 在实际实现中，这里会等待模拟线程结束
    
    // 更新状态
    controller->state = CONTROLLER_IDLE;
    controller->simulation_end_time = get_current_time_ms();
    controller->stats.elapsed_time_ms = controller->simulation_end_time - controller->simulation_start_time;
    
    // 触发停止事件
    trigger_event(controller, EVENT_SIMULATION_STOPPED);
    
    printf("量子模拟已停止\n");
    return true;
}

// 暂停模拟
bool quantum_simulation_controller_pause(QuantumSimulationController* controller) {
    if (!controller) {
        return false;
    }
    
    if (controller->state != CONTROLLER_RUNNING) {
        set_error(controller, "模拟未在运行，无法暂停");
        return false;
    }
    
    // 更新状态
    controller->state = CONTROLLER_PAUSED;
    
    // 触发暂停事件
    trigger_event(controller, EVENT_SIMULATION_PAUSED);
    
    printf("量子模拟已暂停\n");
    return true;
}

// 恢复模拟
bool quantum_simulation_controller_resume(QuantumSimulationController* controller) {
    if (!controller) {
        return false;
    }
    
    if (controller->state != CONTROLLER_PAUSED) {
        set_error(controller, "模拟未处于暂停状态，无法恢复");
        return false;
    }
    
    // 更新状态
    controller->state = CONTROLLER_RUNNING;
    
    // 触发恢复事件
    trigger_event(controller, EVENT_SIMULATION_RESUMED);
    
    printf("量子模拟已恢复\n");
    return true;
}

// 获取模拟统计信息
bool quantum_simulation_controller_get_statistics(QuantumSimulationController* controller, SimulationStatistics* stats) {
    if (!controller || !stats) {
        return false;
    }
    
    *stats = controller->stats;
    return true;
}

// 启用或禁用检查点
bool quantum_simulation_controller_set_checkpointing(QuantumSimulationController* controller, bool enable, const char* checkpoint_file) {
    if (!controller) {
        return false;
    }
    
    if (controller->state == CONTROLLER_RUNNING) {
        set_error(controller, "无法在模拟运行时更改检查点设置");
        return false;
    }
    
    controller->checkpointing_enabled = enable;
    
    if (checkpoint_file) {
        strncpy(controller->checkpoint_file, checkpoint_file, sizeof(controller->checkpoint_file) - 1);
        controller->checkpoint_file[sizeof(controller->checkpoint_file) - 1] = '\0';
    }
    
    return true;
}

// 从检查点加载模拟状态
bool quantum_simulation_controller_load_checkpoint(QuantumSimulationController* controller, const char* checkpoint_file) {
    if (!controller) {
        return false;
    }
    
    if (controller->state == CONTROLLER_RUNNING) {
        set_error(controller, "无法在模拟运行时加载检查点");
        return false;
    }
    
    // 在实际实现中，这里会从文件加载模拟状态
    // 为示例，我们假装成功了
    
    printf("从检查点 %s 加载模拟状态\n", checkpoint_file ? checkpoint_file : controller->checkpoint_file);
    return true;
}

// 保存模拟状态到检查点
bool quantum_simulation_controller_save_checkpoint(QuantumSimulationController* controller, const char* checkpoint_file) {
    if (!controller) {
        return false;
    }
    
    // 在实际实现中，这里会保存模拟状态到文件
    // 为示例，我们假装成功了
    
    printf("保存模拟状态到检查点 %s\n", checkpoint_file ? checkpoint_file : controller->checkpoint_file);
    controller->stats.checkpoint_count++;
    
    // 触发检查点事件
    trigger_event(controller, EVENT_CHECKPOINT_CREATED);
    
    return true;
}

// 生成性能报告
bool quantum_simulation_controller_generate_report(QuantumSimulationController* controller, const char* report_file) {
    if (!controller) {
        return false;
    }
    
    FILE* file = fopen(report_file, "w");
    if (!file) {
        set_error(controller, "无法创建报告文件 %s", report_file);
        return false;
    }
    
    // 写入报告内容
    fprintf(file, "===== 量子模拟性能报告 =====\n");
    fprintf(file, "时间戳: %lld\n\n", (long long)get_current_time_ms());
    
    fprintf(file, "---- 配置信息 ----\n");
    fprintf(file, "模拟方法: %d\n", controller->config.method);
    fprintf(file, "精度: %d\n", controller->config.precision);
    fprintf(file, "模式: %d\n", controller->config.mode);
    fprintf(file, "加速类型: %d\n", controller->config.acceleration);
    fprintf(file, "最大运行时间: %d ms\n", controller->config.max_runtime_ms);
    fprintf(file, "最大内存: %.2f GB\n", controller->config.max_memory_gb);
    fprintf(file, "检查点启用: %s\n", controller->config.enable_checkpointing ? "是" : "否");
    fprintf(file, "检查点间隔: %d\n\n", controller->config.checkpointing_interval);
    
    fprintf(file, "---- 统计信息 ----\n");
    fprintf(file, "量子比特数: %d\n", controller->stats.num_qubits);
    fprintf(file, "电路深度: %d\n", controller->stats.circuit_depth);
    fprintf(file, "已处理门: %lld\n", (long long)controller->stats.gates_processed);
    fprintf(file, "已用时间: %d ms\n", (int)controller->stats.elapsed_time_ms);
    fprintf(file, "估计内存使用: %.2f GB\n", controller->stats.estimated_memory_gb);
    fprintf(file, "实际内存使用: %.2f GB\n", controller->stats.actual_memory_gb);
    fprintf(file, "进度: %.1f%%\n", controller->stats.progress);
    fprintf(file, "检查点数: %d\n\n", controller->stats.checkpoint_count);
    
    fprintf(file, "---- 设备信息 ----\n");
    fprintf(file, "选择的加速方式: %d\n", controller->stats.selected_acceleration);
    fprintf(file, "GPU可用: %s\n", controller->acceleration_info.gpu_available ? "是" : "否");
    fprintf(file, "GPU内存: %d MB\n", controller->acceleration_info.gpu_memory_mb);
    fprintf(file, "量子处理器可用: %s\n", controller->acceleration_info.quantum_processor_available ? "是" : "否");
    fprintf(file, "量子处理器量子比特数: %d\n", controller->acceleration_info.quantum_qubits);
    
    fclose(file);
    printf("性能报告已保存到 %s\n", report_file);
    return true;
}

// 获取最后的错误信息
const char* quantum_simulation_controller_get_last_error(QuantumSimulationController* controller) {
    if (!controller) {
        return "无效的控制器";
    }
    
    return controller->last_error;
}

// 检查控制器是否在运行
bool quantum_simulation_controller_is_running(QuantumSimulationController* controller) {
    if (!controller) {
        return false;
    }
    
    return controller->state == CONTROLLER_RUNNING;
}

// 估算给定配置的性能
bool quantum_simulation_controller_estimate_performance(QuantumSimulationController* controller, 
                                                       int num_qubits, 
                                                       int circuit_depth,
                                                       SimulationMethod method,
                                                       SimulationPerformanceEstimate* estimate) {
    if (!controller || !estimate || num_qubits <= 0 || circuit_depth <= 0) {
        return false;
    }
    
    // 初始化性能估计结构
    memset(estimate, 0, sizeof(SimulationPerformanceEstimate));
    
    // 设置基本参数
    estimate->num_qubits = num_qubits;
    estimate->circuit_depth = circuit_depth;
    estimate->method = method;
    
    // 获取设备信息
    const DeviceCapability* capability = device_capability_detector_get_capability(controller->detector);
    if (!capability) {
        set_error(controller, "无法获取设备能力信息");
        return false;
    }
    
    // 估算内存需求
    estimate->memory_required_gb = estimate_memory_requirement(
        method, 
        controller->config.precision,
        num_qubits,
        circuit_depth
    );
    
    // 估算运行时间（毫秒）
    double base_time = 0.0;
    
    switch (method) {
        case METHOD_STATE_VECTOR:
            // 状态向量模拟时间复杂度约为O(2^n * d)，其中n是量子比特数，d是电路深度
            base_time = 0.001 * pow(2, num_qubits) * circuit_depth;
            break;
            
        case METHOD_DENSITY_MATRIX:
            // 密度矩阵模拟时间复杂度更高，约为O(4^n * d)
            base_time = 0.002 * pow(2, 2 * num_qubits) * circuit_depth;
            break;
            
        case METHOD_MPS:
            // 矩阵乘积状态通常更快，但具体取决于纠缠度
            base_time = 0.05 * pow(2, 4) * num_qubits * circuit_depth;
            break;
            
        case METHOD_STABILIZER:
            // 稳定器模拟对特定类型的电路很快
            base_time = 0.01 * num_qubits * num_qubits * circuit_depth;
            break;
            
        default:
            base_time = 0.001 * pow(2, num_qubits) * circuit_depth;
    }
    
    // 根据CPU性能调整时间
    double cpu_factor = 1000.0 / (capability->cpu.clock_speed_mhz * capability->cpu.cores);
    estimate->estimated_runtime_ms = base_time * cpu_factor;
    
    // 计算GPU加速因子（如果可用）
    if (capability->gpu.available) {
        double gpu_factor = 0.1; // GPU通常可以加速10倍左右
        estimate->gpu_accelerated_runtime_ms = estimate->estimated_runtime_ms * gpu_factor;
    } else {
        estimate->gpu_accelerated_runtime_ms = estimate->estimated_runtime_ms;
    }
    
    // 检查是否可以在量子处理器上运行
    if (capability->quantum.available && num_qubits <= capability->quantum.physical_qubits) {
        // 量子处理器执行时间主要取决于电路深度
        estimate->quantum_accelerated_runtime_ms = 10.0 * circuit_depth;
        estimate->can_run_on_quantum_processor = true;
    } else {
        estimate->quantum_accelerated_runtime_ms = estimate->estimated_runtime_ms;
        estimate->can_run_on_quantum_processor = false;
    }
    
    // 确定最佳加速方式
    AccelerationType best_accel = ACCEL_CPU;
    double best_time = estimate->estimated_runtime_ms;
    
    if (capability->gpu.available && 
        estimate->gpu_accelerated_runtime_ms < best_time && 
        estimate->memory_required_gb * 1024 <= capability->gpu.memory_mb) {
        best_accel = ACCEL_GPU;
        best_time = estimate->gpu_accelerated_runtime_ms;
    }
    
    if (capability->quantum.available && 
        estimate->quantum_accelerated_runtime_ms < best_time && 
        num_qubits <= capability->quantum.physical_qubits) {
        best_accel = ACCEL_QUANTUM;
        best_time = estimate->quantum_accelerated_runtime_ms;
    }
    
    estimate->recommended_acceleration = best_accel;
    estimate->is_feasible = (estimate->memory_required_gb <= controller->config.max_memory_gb);
    
    return true;
} 