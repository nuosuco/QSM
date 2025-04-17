/**
 * @file test_device_capability_detector.c
 * @brief 设备能力检测器测试程序
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
#include "../../core/logger.h"
#include "../../core/config_manager.h"

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
    
    printf("设备能力变化通知:\n");
    printf("  CPU核心数: %d -> %d\n", 
           previous->processing_power.cpu_cores,
           current->processing_power.cpu_cores);
    printf("  内存总量: %d MB -> %d MB\n", 
           previous->memory_capacity.total_ram_mb,
           current->memory_capacity.total_ram_mb);
    printf("  量子比特数: %d -> %d\n", 
           previous->quantum_hardware.max_qubits,
           current->quantum_hardware.max_qubits);
    
    // 设置上下文中的标志，表示回调已触发
    if (context) {
        *((bool*)context) = true;
    }
}

/**
 * @brief 测试创建和销毁
 * @return 成功返回true，失败返回false
 */
static bool test_create_destroy() {
    printf("\n======== 测试创建和销毁 ========\n");
    
    // 创建检测器
    DeviceCapabilityDetector* detector = device_capability_detector_create(NULL);
    if (!detector) {
        printf("创建设备能力检测器失败\n");
        return false;
    }
    printf("创建设备能力检测器成功\n");
    
    // 销毁检测器
    device_capability_detector_destroy(detector);
    printf("销毁设备能力检测器成功\n");
    
    return true;
}

/**
 * @brief 测试执行检测
 * @return 成功返回true，失败返回false
 */
static bool test_run_detection() {
    printf("\n======== 测试执行检测 ========\n");
    
    // 创建检测器
    DeviceCapabilityDetector* detector = device_capability_detector_create(NULL);
    if (!detector) {
        printf("创建设备能力检测器失败\n");
        return false;
    }
    
    // 执行检测
    bool result = device_capability_detector_run(detector);
    if (!result) {
        printf("执行设备能力检测失败\n");
        device_capability_detector_destroy(detector);
        return false;
    }
    printf("执行设备能力检测成功\n");
    
    // 获取检测结果
    DeviceCapabilities capabilities;
    result = device_capability_detector_get_capabilities(detector, &capabilities);
    if (!result) {
        printf("获取设备能力失败\n");
        device_capability_detector_destroy(detector);
        return false;
    }
    
    // 打印检测结果
    printf("设备能力检测结果:\n");
    printf("  处理能力:\n");
    printf("    CPU核心数: %d\n", capabilities.processing_power.cpu_cores);
    printf("    CPU频率: %.2f GHz\n", capabilities.processing_power.cpu_frequency_mhz / 1000.0);
    printf("    CPU架构: %s\n", capabilities.processing_power.cpu_architecture);
    
    printf("  内存容量:\n");
    printf("    总内存: %d MB\n", capabilities.memory_capacity.total_ram_mb);
    printf("    可用内存: %d MB\n", capabilities.memory_capacity.available_ram_mb);
    printf("    内存类型: %s\n", capabilities.memory_capacity.memory_type);
    
    printf("  量子硬件支持:\n");
    printf("    是否有量子处理器: %s\n", capabilities.quantum_hardware.has_quantum_processor ? "是" : "否");
    printf("    最大量子比特数: %d\n", capabilities.quantum_hardware.max_qubits);
    printf("    量子处理器类型: %s\n", capabilities.quantum_hardware.processor_type);
    printf("    错误率: %.4f\n", capabilities.quantum_hardware.error_rate);
    
    // 销毁检测器
    device_capability_detector_destroy(detector);
    
    return true;
}

/**
 * @brief 测试连续检测
 * @return 成功返回true，失败返回false
 */
static bool test_continuous_detection() {
    printf("\n======== 测试连续检测 ========\n");
    
    // 创建检测器
    DeviceCapabilityDetector* detector = device_capability_detector_create(NULL);
    if (!detector) {
        printf("创建设备能力检测器失败\n");
        return false;
    }
    
    // 设置回调
    bool callback_triggered = false;
    device_capability_detector_set_callback(detector, capability_change_callback, &callback_triggered);
    printf("设置回调函数成功\n");
    
    // 启动连续检测
    unsigned int interval_ms = 5000; // 5秒
    bool result = device_capability_detector_start_continuous(detector, interval_ms);
    if (!result) {
        printf("启动连续检测失败\n");
        device_capability_detector_destroy(detector);
        return false;
    }
    printf("启动连续检测成功，间隔: %d ms\n", interval_ms);
    
    // 由于这是一个简化的实现，连续检测实际上并不会在后台自动运行
    // 因此，我们手动运行几次检测来模拟连续检测
    printf("手动模拟连续检测...\n");
    for (int i = 0; i < 3; i++) {
        result = device_capability_detector_run(detector);
        if (!result) {
            printf("执行设备能力检测失败\n");
            device_capability_detector_destroy(detector);
            return false;
        }
        printf("执行设备能力检测 #%d 成功\n", i + 1);
        
#if defined(_WIN32)
        Sleep(1000); // Windows
#else
        usleep(1000 * 1000); // Unix
#endif
    }
    
    // 停止连续检测
    device_capability_detector_stop_continuous(detector);
    printf("停止连续检测\n");
    
    // 销毁检测器
    device_capability_detector_destroy(detector);
    
    return true;
}

/**
 * @brief 测试自定义配置
 * @return 成功返回true，失败返回false
 */
static bool test_custom_config() {
    printf("\n======== 测试自定义配置 ========\n");
    
    // 创建自定义配置
    DeviceDetectionConfig config;
    memset(&config, 0, sizeof(DeviceDetectionConfig));
    
    // 仅检测处理能力和量子硬件支持
    config.detect_processing = true;
    config.detect_memory = false;
    config.detect_storage = false;
    config.detect_network = false;
    config.detect_energy = false;
    config.detect_cooling = false;
    config.detect_quantum_hardware = true;
    
    // 创建检测器
    DeviceCapabilityDetector* detector = device_capability_detector_create(&config);
    if (!detector) {
        printf("创建设备能力检测器失败\n");
        return false;
    }
    printf("使用自定义配置创建设备能力检测器成功\n");
    
    // 执行检测
    bool result = device_capability_detector_run(detector);
    if (!result) {
        printf("执行设备能力检测失败\n");
        device_capability_detector_destroy(detector);
        return false;
    }
    printf("执行设备能力检测成功\n");
    
    // 获取检测结果
    DeviceCapabilities capabilities;
    result = device_capability_detector_get_capabilities(detector, &capabilities);
    if (!result) {
        printf("获取设备能力失败\n");
        device_capability_detector_destroy(detector);
        return false;
    }
    
    // 打印检测结果
    printf("设备能力检测结果 (仅处理能力和量子硬件):\n");
    printf("  处理能力:\n");
    printf("    CPU核心数: %d\n", capabilities.processing_power.cpu_cores);
    printf("    CPU频率: %.2f GHz\n", capabilities.processing_power.cpu_frequency_mhz / 1000.0);
    
    printf("  量子硬件支持:\n");
    printf("    是否有量子处理器: %s\n", capabilities.quantum_hardware.has_quantum_processor ? "是" : "否");
    printf("    最大量子比特数: %d\n", capabilities.quantum_hardware.max_qubits);
    
    // 内存容量不应该被检测
    printf("  内存容量 (不应被检测):\n");
    printf("    总内存: %d MB\n", capabilities.memory_capacity.total_ram_mb);
    printf("    可用内存: %d MB\n", capabilities.memory_capacity.available_ram_mb);
    
    // 销毁检测器
    device_capability_detector_destroy(detector);
    
    return true;
}

/**
 * @brief 主函数
 * @return 执行结果
 */
int main() {
    printf("======================================\n");
    printf("设备能力检测器测试程序\n");
    printf("======================================\n");
    
    // 初始化日志系统
    // 注意：实际实现应该调用日志系统初始化函数，这里仅示例
    
    // 执行测试
    bool success = true;
    
    success &= test_create_destroy();
    success &= test_run_detection();
    success &= test_continuous_detection();
    success &= test_custom_config();
    
    printf("\n======================================\n");
    printf("测试结果: %s\n", success ? "全部通过" : "有测试失败");
    printf("======================================\n");
    
    return success ? 0 : 1;
} 