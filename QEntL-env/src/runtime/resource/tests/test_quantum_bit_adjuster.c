/**
 * QEntL量子比特调整器测试程序
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月20日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../quantum_bit_adjuster.h"
#include "../device_capability_detector.h"

// 事件回调函数
void adjuster_event_callback(AdjusterEventType event_type, const AdjusterStatus* status, void* user_data) {
    const char* event_name = "";
    
    switch (event_type) {
        case EVENT_ADJUSTMENT_STARTED:
            event_name = "调整开始";
            break;
        case EVENT_ADJUSTMENT_COMPLETED:
            event_name = "调整完成";
            break;
        case EVENT_RESOURCE_LIMITATION:
            event_name = "资源限制";
            break;
        case EVENT_ERROR_THRESHOLD_EXCEEDED:
            event_name = "误差超阈值";
            break;
        case EVENT_MODE_CHANGED:
            event_name = "模式变更";
            break;
        case EVENT_FIDELITY_CHANGED:
            event_name = "保真度变更";
            break;
    }
    
    printf("[量子比特调整器事件] %s - 当前量子比特数: %d, 推荐量子比特数: %d\n", 
           event_name, status->current_qubits, status->recommended_qubits);
}

// 测试基本创建和销毁功能
void test_create_destroy(DeviceCapabilityDetector* detector) {
    printf("\n===== 测试量子比特调整器创建和销毁 =====\n");
    
    QuantumBitAdjuster* adjuster = quantum_bit_adjuster_create(detector);
    if (!adjuster) {
        printf("创建量子比特调整器失败\n");
        return;
    }
    
    // 获取初始状态
    AdjusterStatus status;
    if (quantum_bit_adjuster_get_status(adjuster, &status)) {
        printf("初始状态:\n");
        printf("  推荐量子比特数: %d\n", status.recommended_qubits);
        printf("  估计保真度: %.4f\n", status.estimated_fidelity);
        printf("  内存使用: %.2f GB\n", status.memory_usage_gb);
    }
    
    // 销毁量子比特调整器
    quantum_bit_adjuster_destroy(adjuster);
}

// 测试配置设置和获取
void test_configuration(DeviceCapabilityDetector* detector) {
    printf("\n===== 测试量子比特调整器配置设置和获取 =====\n");
    
    QuantumBitAdjuster* adjuster = quantum_bit_adjuster_create(detector);
    if (!adjuster) {
        printf("创建量子比特调整器失败\n");
        return;
    }
    
    // 获取当前配置
    QuantumBitAdjusterConfig original_config;
    quantum_bit_adjuster_get_config(adjuster, &original_config);
    
    printf("原始配置:\n");
    printf("  最小量子比特数: %d\n", original_config.min_qubits);
    printf("  最大量子比特数: %d\n", original_config.max_qubits);
    printf("  调整策略: %s\n", quantum_bit_adjuster_strategy_to_string(original_config.strategy));
    printf("  执行模式: %s\n", quantum_bit_adjuster_mode_to_string(original_config.mode));
    printf("  目标保真度: %.4f\n", original_config.target_fidelity);
    
    // 修改配置
    QuantumBitAdjusterConfig new_config = original_config;
    new_config.min_qubits = 4;
    new_config.max_qubits = 24;
    new_config.strategy = STRATEGY_AGGRESSIVE;
    new_config.target_fidelity = 0.95;
    new_config.memory_limit_gb = 8.0;
    
    printf("\n设置新配置...\n");
    if (quantum_bit_adjuster_set_config(adjuster, &new_config)) {
        // 获取更新后的配置
        QuantumBitAdjusterConfig updated_config;
        quantum_bit_adjuster_get_config(adjuster, &updated_config);
        
        printf("更新后的配置:\n");
        printf("  最小量子比特数: %d\n", updated_config.min_qubits);
        printf("  最大量子比特数: %d\n", updated_config.max_qubits);
        printf("  调整策略: %s\n", quantum_bit_adjuster_strategy_to_string(updated_config.strategy));
        printf("  执行模式: %s\n", quantum_bit_adjuster_mode_to_string(updated_config.mode));
        printf("  目标保真度: %.4f\n", updated_config.target_fidelity);
        printf("  内存限制: %.2f GB\n", updated_config.memory_limit_gb);
    } else {
        printf("配置更新失败\n");
    }
    
    // 测试设置无效配置
    new_config.min_qubits = 0;  // 无效值
    printf("\n尝试设置无效配置（最小量子比特数为0）...\n");
    if (!quantum_bit_adjuster_set_config(adjuster, &new_config)) {
        printf("成功拒绝了无效配置\n");
    }
    
    // 测试设置无效配置
    new_config.min_qubits = 30;
    new_config.max_qubits = 20;  // 最大值小于最小值
    printf("\n尝试设置无效配置（最大值小于最小值）...\n");
    if (!quantum_bit_adjuster_set_config(adjuster, &new_config)) {
        printf("成功拒绝了无效配置\n");
    }
    
    quantum_bit_adjuster_destroy(adjuster);
}

// 测试不同调整策略
void test_adjustment_strategies(DeviceCapabilityDetector* detector) {
    printf("\n===== 测试不同的量子比特调整策略 =====\n");
    
    QuantumBitAdjuster* adjuster = quantum_bit_adjuster_create(detector);
    if (!adjuster) {
        printf("创建量子比特调整器失败\n");
        return;
    }
    
    // 注册事件回调
    quantum_bit_adjuster_register_callback(adjuster, adjuster_event_callback, NULL);
    
    // 测试各种策略
    AdjustmentStrategy strategies[] = {
        STRATEGY_CONSERVATIVE,
        STRATEGY_BALANCED,
        STRATEGY_AGGRESSIVE,
        STRATEGY_ADAPTIVE
    };
    
    const char* strategy_names[] = {
        "保守策略",
        "平衡策略",
        "激进策略",
        "自适应策略"
    };
    
    for (int i = 0; i < 4; i++) {
        printf("\n测试 %s:\n", strategy_names[i]);
        
        quantum_bit_adjuster_set_strategy(adjuster, strategies[i]);
        
        // 获取推荐的量子比特数
        int qubits = quantum_bit_adjuster_get_recommended_qubits(adjuster);
        
        // 获取状态
        AdjusterStatus status;
        quantum_bit_adjuster_get_status(adjuster, &status);
        
        printf("  推荐量子比特数: %d\n", qubits);
        printf("  估计保真度: %.4f\n", status.estimated_fidelity);
        printf("  内存使用: %.2f GB\n", status.memory_usage_gb);
    }
    
    // 取消注册事件回调
    quantum_bit_adjuster_unregister_callback(adjuster);
    
    quantum_bit_adjuster_destroy(adjuster);
}

// 测试执行模式
void test_execution_modes(DeviceCapabilityDetector* detector) {
    printf("\n===== 测试不同的量子执行模式 =====\n");
    
    QuantumBitAdjuster* adjuster = quantum_bit_adjuster_create(detector);
    if (!adjuster) {
        printf("创建量子比特调整器失败\n");
        return;
    }
    
    // 注册事件回调
    quantum_bit_adjuster_register_callback(adjuster, adjuster_event_callback, NULL);
    
    // 测试模拟模式
    printf("\n测试模拟模式:\n");
    quantum_bit_adjuster_set_mode(adjuster, MODE_SIMULATION);
    
    AdjusterStatus status;
    quantum_bit_adjuster_get_status(adjuster, &status);
    printf("  推荐量子比特数: %d\n", status.recommended_qubits);
    printf("  估计保真度: %.4f\n", status.estimated_fidelity);
    printf("  内存使用: %.2f GB\n", status.memory_usage_gb);
    
    // 测试混合模式
    printf("\n测试混合模式:\n");
    quantum_bit_adjuster_set_mode(adjuster, MODE_HYBRID);
    
    quantum_bit_adjuster_get_status(adjuster, &status);
    printf("  推荐量子比特数: %d\n", status.recommended_qubits);
    printf("  估计保真度: %.4f\n", status.estimated_fidelity);
    printf("  内存使用: %.2f GB\n", status.memory_usage_gb);
    
    // 测试硬件模式（可能失败，取决于是否检测到量子处理器）
    printf("\n测试硬件模式:\n");
    if (quantum_bit_adjuster_set_mode(adjuster, MODE_HARDWARE)) {
        quantum_bit_adjuster_get_status(adjuster, &status);
        printf("  推荐量子比特数: %d\n", status.recommended_qubits);
        printf("  估计保真度: %.4f\n", status.estimated_fidelity);
        printf("  内存使用: %.2f GB\n", status.memory_usage_gb);
    } else {
        printf("  设置硬件模式失败，可能因为未检测到量子处理器\n");
    }
    
    // 取消注册事件回调
    quantum_bit_adjuster_unregister_callback(adjuster);
    
    quantum_bit_adjuster_destroy(adjuster);
}

// 测试性能预测
void test_performance_prediction(DeviceCapabilityDetector* detector) {
    printf("\n===== 测试量子电路性能预测 =====\n");
    
    QuantumBitAdjuster* adjuster = quantum_bit_adjuster_create(detector);
    if (!adjuster) {
        printf("创建量子比特调整器失败\n");
        return;
    }
    
    // 设置为模拟模式
    quantum_bit_adjuster_set_mode(adjuster, MODE_SIMULATION);
    
    // 预测不同规模电路的性能
    printf("量子比特数\t电路深度\t估计保真度\t估计内存(GB)\t估计时间(ms)\n");
    printf("---------------------------------------------------------------\n");
    
    for (int qubits = 4; qubits <= 20; qubits += 4) {
        for (int depth = 10; depth <= 100; depth += 45) {
            double fidelity, memory_gb, time_ms;
            
            if (quantum_bit_adjuster_predict_performance(adjuster, qubits, depth, &fidelity, &memory_gb, &time_ms)) {
                printf("%d\t\t%d\t\t%.4f\t\t%.2f\t\t%.2f\n", 
                       qubits, depth, fidelity, memory_gb, time_ms);
            }
        }
    }
    
    quantum_bit_adjuster_destroy(adjuster);
}

// 测试算法验证
void test_algorithm_validation(DeviceCapabilityDetector* detector) {
    printf("\n===== 测试量子算法验证 =====\n");
    
    QuantumBitAdjuster* adjuster = quantum_bit_adjuster_create(detector);
    if (!adjuster) {
        printf("创建量子比特调整器失败\n");
        return;
    }
    
    // 获取当前推荐的量子比特数
    int max_qubits = quantum_bit_adjuster_get_recommended_qubits(adjuster);
    printf("当前推荐的量子比特数: %d\n", max_qubits);
    
    // 测试有效算法
    int valid_qubits = max_qubits - 2;
    int valid_depth = 50;
    double required_fidelity = 0.9;
    
    printf("\n验证有效算法 (量子比特: %d, 深度: %d, 保真度: %.2f)...\n", 
           valid_qubits, valid_depth, required_fidelity);
    
    if (quantum_bit_adjuster_validate_algorithm(adjuster, valid_qubits, valid_depth, required_fidelity)) {
        printf("  算法验证通过\n");
    } else {
        printf("  算法验证失败\n");
        
        // 获取状态以查看错误信息
        AdjusterStatus status;
        quantum_bit_adjuster_get_status(adjuster, &status);
        printf("  错误信息: %s\n", status.last_error);
    }
    
    // 测试无效算法（量子比特数太多）
    int invalid_qubits = max_qubits + 5;
    
    printf("\n验证无效算法 (量子比特: %d, 深度: %d, 保真度: %.2f)...\n", 
           invalid_qubits, valid_depth, required_fidelity);
    
    if (!quantum_bit_adjuster_validate_algorithm(adjuster, invalid_qubits, valid_depth, required_fidelity)) {
        printf("  成功拒绝了无效算法\n");
        
        // 获取状态以查看错误信息
        AdjusterStatus status;
        quantum_bit_adjuster_get_status(adjuster, &status);
        printf("  错误信息: %s\n", status.last_error);
    } else {
        printf("  验证意外通过\n");
    }
    
    // 测试无效算法（要求保真度太高）
    double high_fidelity = 0.9999;
    
    printf("\n验证无效算法 (量子比特: %d, 深度: %d, 保真度: %.4f)...\n", 
           valid_qubits, valid_depth, high_fidelity);
    
    if (!quantum_bit_adjuster_validate_algorithm(adjuster, valid_qubits, valid_depth, high_fidelity)) {
        printf("  成功拒绝了无效算法\n");
        
        // 获取状态以查看错误信息
        AdjusterStatus status;
        quantum_bit_adjuster_get_status(adjuster, &status);
        printf("  错误信息: %s\n", status.last_error);
    } else {
        printf("  验证意外通过\n");
    }
    
    quantum_bit_adjuster_destroy(adjuster);
}

// 测试状态报告生成
void test_report_generation(DeviceCapabilityDetector* detector) {
    printf("\n===== 测试状态报告生成 =====\n");
    
    QuantumBitAdjuster* adjuster = quantum_bit_adjuster_create(detector);
    if (!adjuster) {
        printf("创建量子比特调整器失败\n");
        return;
    }
    
    // 设置不同的配置进行测试
    quantum_bit_adjuster_set_strategy(adjuster, STRATEGY_AGGRESSIVE);
    quantum_bit_adjuster_set_mode(adjuster, MODE_SIMULATION);
    
    // 调整量子比特数
    quantum_bit_adjuster_adjust(adjuster);
    
    // 生成报告
    const char* report_file = "quantum_bit_adjuster_report.txt";
    if (quantum_bit_adjuster_save_report(adjuster, report_file)) {
        printf("状态报告已保存到: %s\n", report_file);
    } else {
        printf("保存状态报告失败\n");
    }
    
    quantum_bit_adjuster_destroy(adjuster);
}

// 主函数
int main(int argc, char* argv[]) {
    printf("QEntL量子比特调整器测试程序\n");
    printf("============================\n");
    
    // 创建设备能力检测器
    DeviceCapabilityDetector* detector = device_capability_detector_create();
    if (!detector) {
        printf("创建设备能力检测器失败\n");
        return 1;
    }
    
    // 执行设备能力检测
    if (!device_capability_detector_scan(detector, true)) {
        printf("设备能力检测失败\n");
        device_capability_detector_destroy(detector);
        return 1;
    }
    
    // 运行各项测试
    test_create_destroy(detector);
    test_configuration(detector);
    test_adjustment_strategies(detector);
    test_execution_modes(detector);
    test_performance_prediction(detector);
    test_algorithm_validation(detector);
    test_report_generation(detector);
    
    // 销毁设备能力检测器
    device_capability_detector_destroy(detector);
    
    printf("\n测试完成\n");
    return 0;
} 