/**
 * @file test_resource_adaptive_engine.c
 * @brief 资源自适应引擎综合测试程序
 * @author QEntL核心开发团队
 * @date 2024-05-19
 * @version 1.0
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>

#include "../device_capability_detector.h"
#include "../quantum_bit_adjuster.h"
#include "../resource_monitoring_system.h"
#include "../../core/logger.h"
#include "../../core/config_manager.h"

/**
 * @brief 模拟量子计算任务
 */
typedef struct {
    char name[64];
    unsigned int required_qubits;
    unsigned int active_qubits;
    unsigned int gate_operations;
    unsigned int entangled_pairs;
    double error_rate;
    double execution_time_ms;
} QuantumTask;

/**
 * @brief 设备能力变化回调函数
 * @param current 当前设备能力
 * @param previous 先前设备能力
 * @param context 回调上下文
 */
static void capability_change_callback(
    const DeviceCapabilities* current,
    const DeviceCapabilities* previous,
    void* context) {
    
    printf("\n[设备能力变化通知]\n");
    printf("  CPU核心数: %d -> %d\n", 
           previous->processing_power.cpu_cores,
           current->processing_power.cpu_cores);
    printf("  可用内存: %d MB -> %d MB\n", 
           previous->memory_capacity.available_ram_mb,
           current->memory_capacity.available_ram_mb);
    printf("  量子比特数: %d -> %d\n", 
           previous->quantum_hardware.max_qubits,
           current->quantum_hardware.max_qubits);
    printf("  量子处理器错误率: %.4f -> %.4f\n", 
           previous->quantum_hardware.error_rate,
           current->quantum_hardware.error_rate);
}

/**
 * @brief 量子比特调整回调函数
 * @param old_qubits 旧的量子比特数
 * @param new_qubits 新的量子比特数
 * @param result 调整结果
 * @param context 回调上下文
 */
static void qbit_adjust_callback(
    unsigned int old_qubits,
    unsigned int new_qubits,
    QBitAdjustResult result,
    void* context) {
    
    printf("\n[量子比特调整通知]\n");
    
    if (result == QB_ADJUST_RESULT_NO_CHANGE_NEEDED) {
        printf("  无需调整，当前量子比特数 %d 已是最佳\n", old_qubits);
        return;
    }
    
    if (result == QB_ADJUST_RESULT_ERROR || result == QB_ADJUST_RESULT_INSUFFICIENT_QUBITS) {
        printf("  调整失败: %s\n", 
               result == QB_ADJUST_RESULT_ERROR ? "发生错误" : "量子比特数不足");
        return;
    }
    
    printf("  量子比特数已调整: %d -> %d\n", old_qubits, new_qubits);
    
    if (new_qubits > old_qubits) {
        printf("  扩展了 %d 个量子比特以提高性能\n", new_qubits - old_qubits);
    } else {
        printf("  减少了 %d 个量子比特以优化资源使用\n", old_qubits - new_qubits);
    }
}

/**
 * @brief 资源警报回调函数
 * @param alert 警报信息
 * @param context 回调上下文
 */
static void resource_alert_callback(
    const ResourceAlert* alert,
    void* context) {
    
    const char* level_str = "未知";
    switch (alert->level) {
        case RESOURCE_ALERT_INFO:    level_str = "信息"; break;
        case RESOURCE_ALERT_WARNING: level_str = "警告"; break;
        case RESOURCE_ALERT_ERROR:   level_str = "错误"; break;
        case RESOURCE_ALERT_CRITICAL: level_str = "严重"; break;
    }
    
    const char* resource_str = "未知";
    switch (alert->resource_type) {
        case RESOURCE_TYPE_CPU:          resource_str = "CPU"; break;
        case RESOURCE_TYPE_MEMORY:       resource_str = "内存"; break;
        case RESOURCE_TYPE_STORAGE:      resource_str = "存储"; break;
        case RESOURCE_TYPE_NETWORK:      resource_str = "网络"; break;
        case RESOURCE_TYPE_QUANTUM_BITS: resource_str = "量子比特"; break;
        case RESOURCE_TYPE_QUANTUM_GATES: resource_str = "量子门操作"; break;
        case RESOURCE_TYPE_ENTANGLEMENT: resource_str = "量子纠缠"; break;
        default: break;
    }
    
    printf("\n[资源警报] %s - %s\n", level_str, resource_str);
    printf("  消息: %s\n", alert->message);
    printf("  当前值: %.2f, 阈值: %.2f\n", alert->value, alert->threshold);
}

/**
 * @brief 优化建议回调函数
 * @param suggestion 优化建议
 * @param context 回调上下文
 */
static void optimization_suggestion_callback(
    const OptimizationSuggestion* suggestion,
    void* context) {
    
    const char* type_str = "未知";
    switch (suggestion->type) {
        case OPTIMIZE_REDUCE_QUBITS:       type_str = "减少量子比特"; break;
        case OPTIMIZE_INCREASE_QUBITS:     type_str = "增加量子比特"; break;
        case OPTIMIZE_REDUCE_GATES:        type_str = "减少量子门操作"; break;
        case OPTIMIZE_OPTIMIZE_CIRCUIT:    type_str = "优化量子电路"; break;
        case OPTIMIZE_CHANGE_ALGORITHM:    type_str = "更改算法"; break;
        case OPTIMIZE_DISTRIBUTE_WORKLOAD: type_str = "分布式工作负载"; break;
        case OPTIMIZE_ADJUST_MEMORY:       type_str = "调整内存使用"; break;
        case OPTIMIZE_ADJUST_ERROR_CORRECTION: type_str = "调整错误修正"; break;
    }
    
    const char* resource_str = "未知";
    switch (suggestion->resource_type) {
        case RESOURCE_TYPE_CPU:          resource_str = "CPU"; break;
        case RESOURCE_TYPE_MEMORY:       resource_str = "内存"; break;
        case RESOURCE_TYPE_STORAGE:      resource_str = "存储"; break;
        case RESOURCE_TYPE_NETWORK:      resource_str = "网络"; break;
        case RESOURCE_TYPE_QUANTUM_BITS: resource_str = "量子比特"; break;
        case RESOURCE_TYPE_QUANTUM_GATES: resource_str = "量子门操作"; break;
        case RESOURCE_TYPE_ENTANGLEMENT: resource_str = "量子纠缠"; break;
        default: break;
    }
    
    printf("\n[优化建议] %s - %s\n", type_str, resource_str);
    printf("  描述: %s\n", suggestion->description);
    printf("  当前利用率: %.2f, 目标利用率: %.2f\n", 
           suggestion->current_utilization, 
           suggestion->target_utilization);
    printf("  预计改进: %.1f%%\n", suggestion->estimated_improvement * 100.0);
}

/**
 * @brief 模拟量子应用程序
 * @param detector 设备能力检测器
 * @param adjuster 量子比特调整器
 * @param monitor 资源监控系统
 */
static void simulate_quantum_application(
    DeviceCapabilityDetector* detector,
    QuantumBitAdjuster* adjuster,
    ResourceMonitoringSystem* monitor) {
    
    printf("\n======== 模拟量子应用程序 ========\n");
    
    // 定义一系列量子计算任务
    QuantumTask tasks[] = {
        {"量子傅里叶变换", 8, 8, 120, 4, 0.01, 150.0},
        {"Grover搜索算法", 12, 12, 240, 6, 0.02, 300.0},
        {"量子相位估计", 10, 10, 180, 5, 0.015, 220.0},
        {"Shor分解算法", 20, 20, 1200, 10, 0.03, 1500.0},
        {"变分量子特征求解器", 16, 16, 800, 8, 0.025, 800.0},
        {"量子机器学习", 24, 24, 2400, 12, 0.04, 3000.0},
    };
    
    int num_tasks = sizeof(tasks) / sizeof(QuantumTask);
    
    // 初始化量子比特分配
    quantum_bit_adjuster_adjust_now(adjuster);
    
    // 为每个任务执行资源自适应过程
    for (int i = 0; i < num_tasks; i++) {
        QuantumTask* task = &tasks[i];
        
        printf("\n[执行任务] %s\n", task->name);
        printf("  要求量子比特数: %d\n", task->required_qubits);
        printf("  量子门操作数: %d\n", task->gate_operations);
        printf("  量子纠缠对数: %d\n", task->entangled_pairs);
        
        // 获取当前分配的量子比特数
        QBitAllocConfig qbit_config;
        quantum_bit_adjuster_get_config(adjuster, &qbit_config);
        
        if (qbit_config.current_qubits < task->required_qubits) {
            printf("  警告: 当前分配的量子比特数(%d)小于任务要求(%d)\n", 
                  qbit_config.current_qubits, task->required_qubits);
            
            // 临时调整量子比特配置
            qbit_config.min_qubits = task->required_qubits;
            quantum_bit_adjuster_set_config(adjuster, &qbit_config);
            
            // 再次调整量子比特
            quantum_bit_adjuster_adjust_now(adjuster);
            
            // 获取调整后的配置
            quantum_bit_adjuster_get_config(adjuster, &qbit_config);
        }
        
        // 报告量子资源指标
        QuantumResourceMetrics metrics;
        metrics.active_qubits = task->active_qubits;
        metrics.max_qubits = qbit_config.current_qubits;
        metrics.gate_operations = task->gate_operations;
        metrics.entangled_pairs = task->entangled_pairs;
        metrics.measurement_operations = task->gate_operations / 10; // 假设10%的操作是测量
        metrics.error_rate = task->error_rate;
        metrics.coherence_time_us = 100.0; // 假设相干时间为100微秒
        metrics.fidelity = 1.0 - task->error_rate;
        
        resource_monitoring_system_report_quantum_metrics(monitor, &metrics);
        
        // 模拟任务执行
        printf("  正在执行任务...\n");
        
        // 模拟每个时间步的资源使用报告
        int num_steps = 10;
        for (int step = 1; step <= num_steps; step++) {
            // 报告量子比特使用情况
            unsigned int active_qubits = task->active_qubits * step / num_steps;
            float current_error_rate = task->error_rate * (1.0 + 0.5 * step / num_steps);
            
            quantum_bit_adjuster_report_usage(
                adjuster, 
                active_qubits, 
                current_error_rate);
            
            // 更新指标
            metrics.active_qubits = active_qubits;
            metrics.error_rate = current_error_rate;
            metrics.gate_operations = task->gate_operations * step / num_steps;
            metrics.entangled_pairs = task->entangled_pairs * step / num_steps;
            
            resource_monitoring_system_report_quantum_metrics(monitor, &metrics);
            
            // 睡眠一小段时间，模拟计算过程
#if defined(_WIN32)
            Sleep(100); // Windows
#else
            usleep(100 * 1000); // Unix
#endif
        }
        
        printf("  任务完成，执行时间: %.1f ms\n", task->execution_time_ms);
        
        // 获取资源使用情况
        ResourceUsage qbit_usage;
        resource_monitoring_system_get_usage(monitor, RESOURCE_TYPE_QUANTUM_BITS, &qbit_usage);
        
        printf("  量子比特使用情况: %.1f%% (%d/%d)\n", 
               qbit_usage.utilization * 100.0,
               qbit_usage.total - qbit_usage.available,
               qbit_usage.total);
        
        ResourceUsage gate_usage;
        resource_monitoring_system_get_usage(monitor, RESOURCE_TYPE_QUANTUM_GATES, &gate_usage);
        
        printf("  量子门操作使用情况: %.1f%%\n", gate_usage.utilization * 100.0);
        
        // 获取优化建议
        OptimizationSuggestion suggestion;
        if (resource_monitoring_system_get_suggestion(monitor, RESOURCE_TYPE_QUANTUM_BITS, &suggestion)) {
            printf("  优化建议: %s\n", suggestion.description);
        }
        
        // 根据任务执行结果调整资源
        quantum_bit_adjuster_adjust_now(adjuster);
        
        // 打印分隔线
        printf("\n----------------------------------------\n");
    }
}

/**
 * @brief 初始化资源自适应引擎
 * @param p_detector 用于存储检测器指针的指针
 * @param p_adjuster 用于存储调整器指针的指针
 * @param p_monitor 用于存储监控系统指针的指针
 * @return 成功返回true，失败返回false
 */
static bool initialize_resource_adaptive_engine(
    DeviceCapabilityDetector** p_detector,
    QuantumBitAdjuster** p_adjuster,
    ResourceMonitoringSystem** p_monitor) {
    
    printf("\n======== 初始化资源自适应引擎 ========\n");
    
    // 创建设备能力检测器
    DeviceCapabilityDetector* detector = device_capability_detector_create(NULL);
    if (!detector) {
        printf("创建设备能力检测器失败\n");
        return false;
    }
    printf("创建设备能力检测器成功\n");
    
    // 设置回调
    device_capability_detector_set_callback(detector, capability_change_callback, NULL);
    
    // 执行初始检测
    bool result = device_capability_detector_run(detector);
    if (!result) {
        printf("执行设备能力检测失败\n");
        device_capability_detector_destroy(detector);
        return false;
    }
    
    // 获取设备能力
    DeviceCapabilities capabilities;
    result = device_capability_detector_get_capabilities(detector, &capabilities);
    if (!result) {
        printf("获取设备能力失败\n");
        device_capability_detector_destroy(detector);
        return false;
    }
    
    printf("设备能力检测结果:\n");
    printf("  CPU: %d核心, %.2f GHz\n", 
           capabilities.processing_power.cpu_cores,
           capabilities.processing_power.cpu_frequency_mhz / 1000.0);
    printf("  内存: 总共 %d MB, 可用 %d MB\n",
           capabilities.memory_capacity.total_ram_mb,
           capabilities.memory_capacity.available_ram_mb);
    printf("  量子硬件: %s, %d量子比特\n",
           capabilities.quantum_hardware.has_quantum_processor ? 
               capabilities.quantum_hardware.processor_type : "模拟器",
           capabilities.quantum_hardware.max_qubits);
    
    // 创建量子比特调整器
    QBitAllocConfig qbit_config;
    memset(&qbit_config, 0, sizeof(QBitAllocConfig));
    
    qbit_config.min_qubits = 5;
    qbit_config.max_qubits = capabilities.quantum_hardware.max_qubits;
    qbit_config.optimal_qubits = 0; // 让调整器自动决定
    qbit_config.current_qubits = 0; // 尚未分配
    qbit_config.error_tolerance = 0.05f; // 5%错误容忍度
    qbit_config.strategy = QB_ADJUST_STRATEGY_ADAPTIVE; // 自适应策略
    qbit_config.mode = QB_ADJUST_MODE_ONDEMAND; // 按需调整
    qbit_config.adjust_interval_ms = 1000; // 每秒调整一次
    
    QuantumBitAdjuster* adjuster = quantum_bit_adjuster_create(detector, &qbit_config);
    if (!adjuster) {
        printf("创建量子比特调整器失败\n");
        device_capability_detector_destroy(detector);
        return false;
    }
    printf("创建量子比特调整器成功\n");
    
    // 设置回调
    quantum_bit_adjuster_set_notify_callback(adjuster, qbit_adjust_callback, NULL);
    
    // 启动自动调整
    result = quantum_bit_adjuster_start_auto(adjuster);
    if (!result) {
        printf("启动自动调整失败\n");
        quantum_bit_adjuster_destroy(adjuster);
        device_capability_detector_destroy(detector);
        return false;
    }
    
    // 创建资源监控系统
    ResourceMonitoringConfig monitor_config;
    memset(&monitor_config, 0, sizeof(ResourceMonitoringConfig));
    
    monitor_config.sampling_interval_ms = 1000; // 每秒采样一次
    monitor_config.history_size = 100; // 保存最近100次采样结果
    monitor_config.alert_on_high = true; // 高使用率时发出警报
    monitor_config.alert_on_critical = true; // 临界使用率时发出警报
    monitor_config.auto_optimize = true; // 自动优化
    
    // 设置各资源类型的阈值
    for (int i = 0; i < 7; i++) {
        monitor_config.thresholds[i].low_threshold = 0.3f;
        monitor_config.thresholds[i].normal_threshold = 0.6f;
        monitor_config.thresholds[i].high_threshold = 0.8f;
        monitor_config.thresholds[i].critical_threshold = 0.95f;
    }
    
    ResourceMonitoringSystem* monitor = resource_monitoring_system_create(detector, &monitor_config);
    if (!monitor) {
        printf("创建资源监控系统失败\n");
        quantum_bit_adjuster_destroy(adjuster);
        device_capability_detector_destroy(detector);
        return false;
    }
    printf("创建资源监控系统成功\n");
    
    // 设置回调
    resource_monitoring_system_set_alert_callback(monitor, resource_alert_callback, NULL);
    resource_monitoring_system_set_suggestion_callback(monitor, optimization_suggestion_callback, NULL);
    
    // 启动监控
    result = resource_monitoring_system_start(monitor);
    if (!result) {
        printf("启动资源监控失败\n");
        resource_monitoring_system_destroy(monitor);
        quantum_bit_adjuster_destroy(adjuster);
        device_capability_detector_destroy(detector);
        return false;
    }
    
    // 返回创建的组件
    *p_detector = detector;
    *p_adjuster = adjuster;
    *p_monitor = monitor;
    
    return true;
}

/**
 * @brief 关闭资源自适应引擎
 * @param detector 设备能力检测器
 * @param adjuster 量子比特调整器
 * @param monitor 资源监控系统
 */
static void shutdown_resource_adaptive_engine(
    DeviceCapabilityDetector* detector,
    QuantumBitAdjuster* adjuster,
    ResourceMonitoringSystem* monitor) {
    
    printf("\n======== 关闭资源自适应引擎 ========\n");
    
    // 停止监控
    resource_monitoring_system_stop(monitor);
    printf("停止资源监控系统\n");
    
    // 停止自动调整
    quantum_bit_adjuster_stop_auto(adjuster);
    printf("停止量子比特自动调整\n");
    
    // 销毁组件
    resource_monitoring_system_destroy(monitor);
    quantum_bit_adjuster_destroy(adjuster);
    device_capability_detector_destroy(detector);
    
    printf("资源自适应引擎已关闭\n");
}

/**
 * @brief 主函数
 * @return 执行结果
 */
int main() {
    printf("======================================\n");
    printf("资源自适应引擎综合测试程序\n");
    printf("======================================\n");
    
    // 初始化日志系统
    // 注意：实际实现应该调用日志系统初始化函数，这里仅示例
    
    // 初始化资源自适应引擎
    DeviceCapabilityDetector* detector = NULL;
    QuantumBitAdjuster* adjuster = NULL;
    ResourceMonitoringSystem* monitor = NULL;
    
    bool success = initialize_resource_adaptive_engine(&detector, &adjuster, &monitor);
    if (!success) {
        printf("初始化资源自适应引擎失败\n");
        return 1;
    }
    
    // 运行模拟任务
    simulate_quantum_application(detector, adjuster, monitor);
    
    // 关闭资源自适应引擎
    shutdown_resource_adaptive_engine(detector, adjuster, monitor);
    
    printf("\n======================================\n");
    printf("测试完成\n");
    printf("======================================\n");
    
    return 0;
} 