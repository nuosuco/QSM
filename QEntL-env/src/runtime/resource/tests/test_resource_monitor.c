/**
 * QEntL资源监控系统测试程序
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月20日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../resource_monitor.h"

// 警报回调函数
void alert_callback(ResourceType resource, AlertType alert_type, const char* message, void* user_data) {
    const char* alert_type_str = "";
    switch (alert_type) {
        case ALERT_INFO:
            alert_type_str = "信息";
            break;
        case ALERT_WARNING:
            alert_type_str = "警告";
            break;
        case ALERT_CRITICAL:
            alert_type_str = "严重";
            break;
    }
    
    printf("[%s警报] %s\n", alert_type_str, message);
}

// 测试资源阈值设置与获取
void test_resource_thresholds(ResourceMonitor* monitor) {
    printf("\n===== 测试资源阈值设置与获取 =====\n");
    
    // 设置自定义阈值
    ResourceThresholds thresholds;
    thresholds.low_threshold = 0.2;
    thresholds.moderate_threshold = 0.5;
    thresholds.high_threshold = 0.7;
    thresholds.critical_threshold = 0.9;
    
    // 为CPU资源设置阈值
    resource_monitor_set_thresholds(monitor, RESOURCE_CPU, &thresholds);
    
    // 读取并验证阈值
    ResourceThresholds retrieved;
    resource_monitor_get_thresholds(monitor, RESOURCE_CPU, &retrieved);
    
    printf("CPU资源阈值设置：\n");
    printf("  低使用率阈值: %.2f (应为 %.2f)\n", retrieved.low_threshold, thresholds.low_threshold);
    printf("  中等阈值:     %.2f (应为 %.2f)\n", retrieved.moderate_threshold, thresholds.moderate_threshold);
    printf("  高使用率阈值: %.2f (应为 %.2f)\n", retrieved.high_threshold, thresholds.high_threshold);
    printf("  临界阈值:     %.2f (应为 %.2f)\n", retrieved.critical_threshold, thresholds.critical_threshold);
}

// 测试资源使用情况获取
void test_resource_usage(ResourceMonitor* monitor) {
    printf("\n===== 测试资源使用情况获取 =====\n");
    
    // 刷新资源使用情况
    resource_monitor_refresh(monitor);
    
    // 获取并打印各资源使用情况
    const char* resource_names[] = {
        "CPU", "内存", "存储", "网络", "GPU", "量子处理单元", "能源", "冷却"
    };
    
    for (int i = 0; i < 8; i++) {
        ResourceUsage usage;
        if (resource_monitor_get_usage(monitor, i, &usage)) {
            printf("%s资源使用情况：\n", resource_names[i]);
            printf("  当前使用率: %.2f%%\n", usage.current_usage * 100);
            printf("  平均使用率: %.2f%%\n", usage.average_usage * 100);
            printf("  峰值使用率: %.2f%%\n", usage.peak_usage * 100);
            printf("  总容量:     %llu\n", (unsigned long long)usage.total_capacity);
            printf("  已用容量:   %llu\n", (unsigned long long)usage.used_capacity);
            printf("  使用状态:   %s\n", resource_monitor_get_state_description(usage.state));
            printf("\n");
        }
    }
}

// 测试网络性能获取
void test_network_performance(ResourceMonitor* monitor) {
    printf("\n===== 测试网络性能获取 =====\n");
    
    // 刷新资源使用情况
    resource_monitor_refresh(monitor);
    
    // 获取并打印网络性能
    NetworkPerformance performance;
    if (resource_monitor_get_network_performance(monitor, &performance)) {
        printf("网络性能指标：\n");
        printf("  带宽使用率: %.2f%%\n", performance.bandwidth_usage * 100);
        printf("  延迟:       %.2f毫秒\n", performance.latency_ms);
        printf("  丢包率:     %.2f%%\n", performance.packet_loss * 100);
        printf("  抖动:       %.2f毫秒\n", performance.jitter_ms);
        printf("  总发送数据: %llu字节\n", (unsigned long long)performance.total_sent);
        printf("  总接收数据: %llu字节\n", (unsigned long long)performance.total_received);
    }
}

// 测试量子资源获取
void test_quantum_resources(ResourceMonitor* monitor) {
    printf("\n===== 测试量子资源获取 =====\n");
    
    // 刷新资源使用情况
    resource_monitor_refresh(monitor);
    
    // 获取并打印量子资源
    QuantumResources resources;
    if (resource_monitor_get_quantum_resources(monitor, &resources)) {
        printf("量子资源指标：\n");
        printf("  可用量子比特数: %d\n", resources.available_qubits);
        printf("  最大量子比特数: %d\n", resources.max_qubits);
        printf("  相干时间:       %.2f微秒\n", resources.coherence_time_us);
        printf("  门保真度:       %.2f%%\n", resources.gate_fidelity * 100);
        printf("  读取保真度:     %.2f%%\n", resources.readout_fidelity * 100);
        printf("  纠缠容量:       %d\n", resources.entanglement_capacity);
    }
}

// 测试警报系统
void test_alert_system(ResourceMonitor* monitor) {
    printf("\n===== 测试警报系统 =====\n");
    
    // 设置警报回调
    resource_monitor_set_alert_callback(monitor, alert_callback, NULL);
    
    // 设置一个较低的阈值，以触发警报
    ResourceThresholds low_thresholds;
    low_thresholds.low_threshold = 0.05;
    low_thresholds.moderate_threshold = 0.1;
    low_thresholds.high_threshold = 0.15;
    low_thresholds.critical_threshold = 0.2;
    
    resource_monitor_set_thresholds(monitor, RESOURCE_CPU, &low_thresholds);
    
    printf("已设置较低的阈值，刷新资源使用情况以触发警报...\n");
    
    // 刷新资源使用情况，这应该会触发警报
    resource_monitor_refresh(monitor);
    
    // 恢复默认阈值
    ResourceThresholds default_thresholds;
    default_thresholds.low_threshold = 0.3;
    default_thresholds.moderate_threshold = 0.6;
    default_thresholds.high_threshold = 0.8;
    default_thresholds.critical_threshold = 0.95;
    
    resource_monitor_set_thresholds(monitor, RESOURCE_CPU, &default_thresholds);
    
    // 禁用警报
    resource_monitor_set_alert_callback(monitor, NULL, NULL);
}

// 测试资源历史保存
void test_save_history(ResourceMonitor* monitor) {
    printf("\n===== 测试资源历史保存 =====\n");
    
    // 生成一些历史数据
    for (int i = 0; i < 5; i++) {
        resource_monitor_refresh(monitor);
        
        // 模拟时间流逝
        printf("刷新资源使用情况 #%d\n", i + 1);
        
        // 在实际环境中应该使用sleep，这里只是简单循环等待一下
        for (volatile int j = 0; j < 100000000; j++) {}
    }
    
    // 保存历史数据
    const char* filename = "resource_history.csv";
    if (resource_monitor_save_history(monitor, filename)) {
        printf("资源历史数据已保存到 %s\n", filename);
    } else {
        printf("保存资源历史数据失败\n");
    }
}

// 测试负载摘要获取
void test_load_summary(ResourceMonitor* monitor) {
    printf("\n===== 测试系统负载摘要 =====\n");
    
    // 刷新资源使用情况
    resource_monitor_refresh(monitor);
    
    // 获取负载摘要
    char summary[1024];
    if (resource_monitor_get_load_summary(monitor, summary, sizeof(summary))) {
        printf("%s\n", summary);
    } else {
        printf("获取负载摘要失败\n");
    }
}

// 测试资源分配建议
void test_allocation_advice(ResourceMonitor* monitor) {
    printf("\n===== 测试资源分配建议 =====\n");
    
    // 刷新资源使用情况
    resource_monitor_refresh(monitor);
    
    // 获取资源分配建议
    char advice[1024];
    if (resource_monitor_get_allocation_advice(monitor, advice, sizeof(advice))) {
        printf("%s\n", advice);
    } else {
        printf("获取资源分配建议失败\n");
    }
}

int main(int argc, char* argv[]) {
    printf("QEntL资源监控系统测试程序\n");
    printf("===========================\n\n");
    
    // 初始化随机数生成器
    srand((unsigned int)time(NULL));
    
    // 创建资源监控系统
    ResourceMonitor* monitor = resource_monitor_create();
    if (!monitor) {
        printf("创建资源监控系统失败\n");
        return 1;
    }
    
    // 启动资源监控
    if (!resource_monitor_start(monitor, 500)) {
        printf("启动资源监控失败\n");
        resource_monitor_destroy(monitor);
        return 1;
    }
    
    // 运行各项测试
    test_resource_thresholds(monitor);
    test_resource_usage(monitor);
    test_network_performance(monitor);
    test_quantum_resources(monitor);
    test_alert_system(monitor);
    test_save_history(monitor);
    test_load_summary(monitor);
    test_allocation_advice(monitor);
    
    // 停止资源监控
    resource_monitor_stop(monitor);
    
    // 销毁资源监控系统
    resource_monitor_destroy(monitor);
    
    printf("\n===== 测试完成 =====\n");
    return 0;
} 