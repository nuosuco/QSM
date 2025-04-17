/**
 * 任务平衡器测试 - QEntL资源自适应引擎
 * 测试任务平衡器的功能和性能
 * 
 * 作者: QEntL核心开发团队
 * 日期: 2024-05-18
 * 版本: 1.0
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../task_balancer.h"
#include "../device_capability_detector.h"
#include "../resource_monitoring_system.h"
#include "../quantum_bit_adjuster.h"
#include "../../event_system.h"

// 回调函数计数器
static int callback_count = 0;

/**
 * 任务完成回调函数
 */
void task_completion_callback(QuantumTask* task, void* user_data) {
    printf("任务完成回调: ID=%u, 类型=%d, 状态=%d\n", task->id, task->type, task->status);
    callback_count++;
}

/**
 * 测试基本功能
 */
int test_basic_functionality() {
    printf("\n==== 测试基本功能 ====\n");
    
    // 创建必要的组件
    EventSystem* event_system = event_system_create();
    ResourceMonitoringSystem* monitor = resource_monitoring_system_create(event_system);
    DeviceCapabilityDetector* detector = device_capability_detector_create();
    QuantumBitAdjuster* adjuster = quantum_bit_adjuster_create(detector);
    
    if (!event_system || !monitor || !detector || !adjuster) {
        fprintf(stderr, "错误: 无法创建必要的组件\n");
        if (event_system) event_system_destroy(event_system);
        if (monitor) resource_monitoring_system_destroy(monitor);
        if (detector) device_capability_detector_destroy(detector);
        if (adjuster) quantum_bit_adjuster_destroy(adjuster);
        return 0;
    }
    
    // 启动监控系统
    resource_monitoring_system_start(monitor);
    
    // 创建任务平衡器
    TaskBalancer* balancer = task_balancer_create(monitor, detector, adjuster);
    if (!balancer) {
        fprintf(stderr, "错误: 无法创建任务平衡器\n");
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    // 测试配置功能
    TaskBalancerConfig config;
    config.strategy = ALLOCATION_STRATEGY_PERFORMANCE;
    config.max_queue_size = 200;
    config.thread_count = 4;
    config.rebalance_interval_ms = 2000;
    config.enable_preemption = 1;
    config.auto_adjust_resources = 1;
    config.priority_weight = 1.2;
    config.performance_weight = 1.5;
    config.efficiency_weight = 0.8;
    
    if (!task_balancer_set_config(balancer, &config)) {
        fprintf(stderr, "错误: 无法设置任务平衡器配置\n");
        task_balancer_destroy(balancer);
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    // 验证配置
    TaskBalancerConfig retrieved_config;
    if (!task_balancer_get_config(balancer, &retrieved_config)) {
        fprintf(stderr, "错误: 无法获取任务平衡器配置\n");
        task_balancer_destroy(balancer);
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    if (retrieved_config.strategy != config.strategy ||
        retrieved_config.max_queue_size != config.max_queue_size ||
        retrieved_config.thread_count != config.thread_count) {
        fprintf(stderr, "错误: 配置不匹配\n");
        task_balancer_destroy(balancer);
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    printf("配置功能测试通过\n");
    
    // 测试资源单元管理
    unsigned int cpu_unit = task_balancer_add_resource_unit(balancer, RESOURCE_TYPE_CPU, 100, 0.9, 0.8);
    unsigned int memory_unit = task_balancer_add_resource_unit(balancer, RESOURCE_TYPE_MEMORY, 200, 0.8, 0.9);
    unsigned int qbit_unit = task_balancer_add_resource_unit(balancer, RESOURCE_TYPE_QUANTUM_BITS, 50, 1.0, 0.7);
    
    if (cpu_unit == 0 || memory_unit == 0 || qbit_unit == 0) {
        fprintf(stderr, "错误: 无法添加资源单元\n");
        task_balancer_destroy(balancer);
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    // 更新资源单元
    if (!task_balancer_update_resource_unit(balancer, cpu_unit, 80, 0.95, 0.85)) {
        fprintf(stderr, "错误: 无法更新资源单元\n");
        task_balancer_destroy(balancer);
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    // 移除资源单元
    if (!task_balancer_remove_resource_unit(balancer, memory_unit)) {
        fprintf(stderr, "错误: 无法移除资源单元\n");
        task_balancer_destroy(balancer);
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    printf("资源单元管理测试通过\n");
    
    // 启动任务平衡器
    if (!task_balancer_start(balancer)) {
        fprintf(stderr, "错误: 无法启动任务平衡器\n");
        task_balancer_destroy(balancer);
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    // 测试任务创建
    unsigned int task1_id = task_balancer_create_task(balancer, TASK_TYPE_COMPUTATION, TASK_PRIORITY_HIGH, 20, 500.0, NULL, 0);
    unsigned int task2_id = task_balancer_create_task(balancer, TASK_TYPE_MEASUREMENT, TASK_PRIORITY_NORMAL, 10, 200.0, NULL, 0);
    
    if (task1_id == 0 || task2_id == 0) {
        fprintf(stderr, "错误: 无法创建任务\n");
        task_balancer_destroy(balancer);
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    // 注册回调
    if (!task_balancer_register_completion_callback(balancer, task1_id, task_completion_callback, NULL)) {
        fprintf(stderr, "错误: 无法注册任务完成回调\n");
        task_balancer_destroy(balancer);
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    // 检查任务状态
    QuantumTask task_info;
    if (!task_balancer_get_task_status(balancer, task1_id, &task_info)) {
        fprintf(stderr, "错误: 无法获取任务状态\n");
        task_balancer_destroy(balancer);
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    printf("任务创建和管理测试通过\n");
    
    // 打印状态
    task_balancer_print_status(balancer);
    
    // 停止任务平衡器
    if (!task_balancer_stop(balancer)) {
        fprintf(stderr, "错误: 无法停止任务平衡器\n");
        task_balancer_destroy(balancer);
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    // 清理资源
    task_balancer_destroy(balancer);
    resource_monitoring_system_destroy(monitor);
    device_capability_detector_destroy(detector);
    quantum_bit_adjuster_destroy(adjuster);
    event_system_destroy(event_system);
    
    printf("基本功能测试通过\n");
    return 1;
}

/**
 * 测试任务处理
 */
int test_task_processing() {
    printf("\n==== 测试任务处理 ====\n");
    
    // 创建必要的组件
    EventSystem* event_system = event_system_create();
    ResourceMonitoringSystem* monitor = resource_monitoring_system_create(event_system);
    DeviceCapabilityDetector* detector = device_capability_detector_create();
    QuantumBitAdjuster* adjuster = quantum_bit_adjuster_create(detector);
    
    if (!event_system || !monitor || !detector || !adjuster) {
        fprintf(stderr, "错误: 无法创建必要的组件\n");
        if (event_system) event_system_destroy(event_system);
        if (monitor) resource_monitoring_system_destroy(monitor);
        if (detector) device_capability_detector_destroy(detector);
        if (adjuster) quantum_bit_adjuster_destroy(adjuster);
        return 0;
    }
    
    // 启动监控系统
    resource_monitoring_system_start(monitor);
    
    // 创建任务平衡器
    TaskBalancer* balancer = task_balancer_create(monitor, detector, adjuster);
    if (!balancer) {
        fprintf(stderr, "错误: 无法创建任务平衡器\n");
        resource_monitoring_system_destroy(monitor);
        device_capability_detector_destroy(detector);
        quantum_bit_adjuster_destroy(adjuster);
        event_system_destroy(event_system);
        return 0;
    }
    
    // 添加资源单元
    task_balancer_add_resource_unit(balancer, RESOURCE_TYPE_CPU, 100, 0.9, 0.8);
    task_balancer_add_resource_unit(balancer, RESOURCE_TYPE_MEMORY, 200, 0.8, 0.9);
    task_balancer_add_resource_unit(balancer, RESOURCE_TYPE_QUANTUM_BITS, 50, 1.0, 0.7);
    
    // 启动任务平衡器
    task_balancer_start(balancer);
    
    // 重置回调计数器
    callback_count = 0;
    
    // 创建多个任务
    const int task_count = 10;
    unsigned int task_ids[task_count];
    
    for (int i = 0; i < task_count; i++) {
        TaskType type = i % TASK_TYPE_MAX;
        TaskPriority priority = i % 4;
        unsigned int resource_demand = (i % 5) * 10 + 10;
        double duration = (i % 3) * 100.0 + 100.0;
        
        task_ids[i] = task_balancer_create_task(balancer, type, priority, resource_demand, duration, NULL, 0);
        if (task_ids[i] == 0) {
            fprintf(stderr, "错误: 无法创建任务 %d\n", i);
            task_balancer_destroy(balancer);
            resource_monitoring_system_destroy(monitor);
            device_capability_detector_destroy(detector);
            quantum_bit_adjuster_destroy(adjuster);
            event_system_destroy(event_system);
            return 0;
        }
        
        // 注册回调
        task_balancer_register_completion_callback(balancer, task_ids[i], task_completion_callback, NULL);
    }
    
    printf("已创建 %d 个任务\n", task_count);
    
    // 检查任务状态
    for (int i = 0; i < task_count; i++) {
        QuantumTask task_info;
        if (task_balancer_get_task_status(balancer, task_ids[i], &task_info)) {
            printf("任务 ID=%u: 类型=%d, 优先级=%d, 状态=%d\n", 
                   task_info.id, task_info.type, task_info.priority, task_info.status);
        }
    }
    
    // 打印状态
    task_balancer_print_status(balancer);
    
    // 模拟任务处理
    printf("模拟任务处理...\n");
    
    // 等待一段时间处理任务
    // 在实际测试中，可以添加更复杂的逻辑来模拟任务处理
    #ifdef _WIN32
    Sleep(3000);  // Windows
    #else
    sleep(3);     // UNIX
    #endif
    
    // 打印状态
    task_balancer_print_status(balancer);
    
    // 强制重新平衡任务
    printf("强制重新平衡任务...\n");
    task_balancer_force_rebalance(balancer);
    
    // 等待重新平衡完成
    #ifdef _WIN32
    Sleep(1000);  // Windows
    #else
    sleep(1);     // UNIX
    #endif
    
    // 打印状态
    task_balancer_print_status(balancer);
    
    // 获取统计信息
    TaskBalancerStats stats;
    task_balancer_get_stats(balancer, &stats);
    
    printf("任务处理统计:\n");
    printf("处理任务数: %u\n", stats.tasks_processed);
    printf("成功任务数: %u\n", stats.tasks_succeeded);
    printf("失败任务数: %u\n", stats.tasks_failed);
    printf("平均等待时间: %.2f ms\n", stats.avg_waiting_time);
    printf("平均处理时间: %.2f ms\n", stats.avg_processing_time);
    printf("资源利用率: %u%%\n", stats.resource_utilization);
    
    // 停止任务平衡器
    task_balancer_stop(balancer);
    
    // 清理资源
    task_balancer_destroy(balancer);
    resource_monitoring_system_destroy(monitor);
    device_capability_detector_destroy(detector);
    quantum_bit_adjuster_destroy(adjuster);
    event_system_destroy(event_system);
    
    printf("任务处理测试完成\n");
    return 1;
}

/**
 * 主函数
 */
int main() {
    printf("任务平衡器测试开始\n");
    
    // 初始化随机数生成器
    srand((unsigned int)time(NULL));
    
    // 运行测试
    int basic_test_passed = test_basic_functionality();
    int processing_test_passed = test_task_processing();
    
    printf("\n==== 测试总结 ====\n");
    printf("基本功能测试: %s\n", basic_test_passed ? "通过" : "失败");
    printf("任务处理测试: %s\n", processing_test_passed ? "通过" : "失败");
    
    // 如果所有测试都通过，则调用内置的任务平衡器测试
    if (basic_test_passed && processing_test_passed) {
        printf("\n==== 运行内置测试 ====\n");
        task_balancer_run_test();
    }
    
    printf("\n任务平衡器测试结束\n");
    
    return basic_test_passed && processing_test_passed ? 0 : 1;
} 