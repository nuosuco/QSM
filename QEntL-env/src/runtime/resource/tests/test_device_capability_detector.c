/**
 * QEntL设备能力检测器测试程序
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月20日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../device_capability_detector.h"

// 测试设备能力检测器的基本功能（创建、扫描、销毁）
void test_basic_functionality(void) {
    printf("\n===== 测试设备能力检测器基本功能 =====\n");
    
    // 创建设备能力检测器
    DeviceCapabilityDetector* detector = device_capability_detector_create();
    if (!detector) {
        printf("创建设备能力检测器失败\n");
        return;
    }
    
    printf("设备能力检测器创建成功\n");
    
    // 执行快速扫描
    bool scan_result = device_capability_detector_scan(detector, false);
    if (!scan_result) {
        printf("设备能力检测失败\n");
        device_capability_detector_destroy(detector);
        return;
    }
    
    printf("快速扫描完成\n");
    
    // 销毁设备能力检测器
    device_capability_detector_destroy(detector);
    printf("设备能力检测器销毁成功\n");
}

// 测试详细扫描并获取能力信息
void test_detailed_scan(void) {
    printf("\n===== 测试详细扫描并获取能力信息 =====\n");
    
    // 创建设备能力检测器
    DeviceCapabilityDetector* detector = device_capability_detector_create();
    if (!detector) {
        printf("创建设备能力检测器失败\n");
        return;
    }
    
    // 执行详细扫描
    bool scan_result = device_capability_detector_scan(detector, true);
    if (!scan_result) {
        printf("详细扫描失败\n");
        device_capability_detector_destroy(detector);
        return;
    }
    
    // 获取设备能力
    const DeviceCapability* capability = device_capability_detector_get_capability(detector);
    if (!capability) {
        printf("获取设备能力失败\n");
        device_capability_detector_destroy(detector);
        return;
    }
    
    // 打印设备基本信息
    printf("设备基本信息:\n");
    printf("  设备名称: %s\n", capability->device_name);
    printf("  设备类型: %s\n", device_capability_detector_get_device_type_string(capability->device_type));
    printf("  操作系统: %s %s\n", device_capability_detector_get_os_type_string(capability->os_type), capability->os_version);
    printf("  逻辑处理器: %d\n", capability->logical_processors);
    printf("  综合性能得分: %.2f/100.0\n", capability->composite_score);
    printf("  推荐量子比特数: %d\n", capability->recommended_qubits);
    
    // 打印CPU信息
    printf("\nCPU信息:\n");
    printf("  型号: %s\n", capability->cpu.model_name);
    printf("  核心数: %d\n", capability->cpu.cores);
    printf("  线程数: %d\n", capability->cpu.threads);
    printf("  基础频率: %.2f GHz\n", capability->cpu.frequency_ghz);
    printf("  最大频率: %.2f GHz\n", capability->cpu.max_frequency_ghz);
    printf("  基准测试得分: %.2f\n", capability->cpu.benchmark_score);
    
    // 打印内存信息
    printf("\n内存信息:\n");
    printf("  物理内存: %.2f GB\n", capability->memory.total_physical_memory / (1024.0 * 1024 * 1024));
    printf("  可用内存: %.2f GB\n", capability->memory.available_memory / (1024.0 * 1024 * 1024));
    printf("  内存带宽: %.2f MB/s\n", capability->memory.memory_bandwidth);
    
    // 打印GPU信息
    printf("\nGPU信息:\n");
    if (capability->gpu.available) {
        printf("  型号: %s\n", capability->gpu.model_name);
        printf("  显存: %.2f GB\n", capability->gpu.memory_size / (1024.0 * 1024 * 1024));
        printf("  CUDA核心数: %d\n", capability->gpu.cuda_cores);
        printf("  FP32性能: %.2f TFLOPS\n", capability->gpu.fp32_performance_tflops);
    } else {
        printf("  未检测到可用的GPU\n");
    }
    
    // 打印量子处理能力信息
    printf("\n量子处理能力信息:\n");
    if (capability->quantum.available) {
        printf("  量子比特数: %d\n", capability->quantum.qubits);
        printf("  最大纠缠量子比特数: %d\n", capability->quantum.max_entangled_qubits);
        printf("  门保真度: %.4f\n", capability->quantum.gate_fidelity);
        printf("  读取保真度: %.4f\n", capability->quantum.readout_fidelity);
    } else {
        printf("  未检测到量子处理能力\n");
    }
    
    // 销毁设备能力检测器
    device_capability_detector_destroy(detector);
}

// 测试报告生成
void test_report_generation(void) {
    printf("\n===== 测试设备能力报告生成 =====\n");
    
    // 创建设备能力检测器
    DeviceCapabilityDetector* detector = device_capability_detector_create();
    if (!detector) {
        printf("创建设备能力检测器失败\n");
        return;
    }
    
    // 执行详细扫描
    bool scan_result = device_capability_detector_scan(detector, true);
    if (!scan_result) {
        printf("设备能力检测失败\n");
        device_capability_detector_destroy(detector);
        return;
    }
    
    // 生成报告
    const char* report_file = "device_capability_report.txt";
    bool report_result = device_capability_detector_save_report(detector, report_file);
    
    if (report_result) {
        printf("设备能力报告已保存到: %s\n", report_file);
    } else {
        printf("生成设备能力报告失败\n");
    }
    
    // 销毁设备能力检测器
    device_capability_detector_destroy(detector);
}

// 测试推荐的量子比特数获取
void test_recommended_qubits(void) {
    printf("\n===== 测试推荐的量子比特数获取 =====\n");
    
    // 创建设备能力检测器
    DeviceCapabilityDetector* detector = device_capability_detector_create();
    if (!detector) {
        printf("创建设备能力检测器失败\n");
        return;
    }
    
    // 执行快速扫描
    device_capability_detector_scan(detector, false);
    
    // 获取推荐的量子比特数
    int recommended_qubits = device_capability_detector_get_recommended_qubits(detector);
    printf("推荐的量子比特数: %d\n", recommended_qubits);
    
    // 销毁设备能力检测器
    device_capability_detector_destroy(detector);
}

// 测试量子功能支持检查
void test_quantum_feature_support(void) {
    printf("\n===== 测试量子功能支持检查 =====\n");
    
    // 创建设备能力检测器
    DeviceCapabilityDetector* detector = device_capability_detector_create();
    if (!detector) {
        printf("创建设备能力检测器失败\n");
        return;
    }
    
    // 执行详细扫描
    device_capability_detector_scan(detector, true);
    
    // 检查各种量子功能支持
    printf("错误纠正功能支持: %s\n", 
           device_capability_detector_supports_quantum_feature(detector, "error_correction") ? "是" : "否");
    
    printf("纠缠功能支持: %s\n", 
           device_capability_detector_supports_quantum_feature(detector, "entanglement") ? "是" : "否");
    
    printf("高保真度功能支持: %s\n", 
           device_capability_detector_supports_quantum_feature(detector, "high_fidelity") ? "是" : "否");
    
    printf("全连接功能支持: %s\n", 
           device_capability_detector_supports_quantum_feature(detector, "full_connectivity") ? "是" : "否");
    
    printf("高相干时间功能支持: %s\n", 
           device_capability_detector_supports_quantum_feature(detector, "high_coherence") ? "是" : "否");
    
    // 销毁设备能力检测器
    device_capability_detector_destroy(detector);
}

// 测试设备兼容性和性能比较
void test_compatibility_and_performance(void) {
    printf("\n===== 测试设备兼容性和性能比较 =====\n");
    
    // 创建一个设备能力检测器
    DeviceCapabilityDetector* detector = device_capability_detector_create();
    if (!detector) {
        printf("创建设备能力检测器失败\n");
        return;
    }
    
    // 执行扫描以获取当前设备能力
    device_capability_detector_scan(detector, true);
    const DeviceCapability* capability = device_capability_detector_get_capability(detector);
    
    if (!capability) {
        printf("获取设备能力失败\n");
        device_capability_detector_destroy(detector);
        return;
    }
    
    // 创建一个模拟的设备能力（与当前设备类似，但有所不同）
    DeviceCapability sim_capability = *capability;
    
    // 修改一些属性
    sim_capability.cpu.cores = capability->cpu.cores / 2;
    sim_capability.cpu.benchmark_score = capability->cpu.benchmark_score * 0.7;
    sim_capability.memory.total_physical_memory = capability->memory.total_physical_memory / 2;
    strcpy(sim_capability.device_name, "模拟设备");
    
    // 检查兼容性
    int compatibility = device_capability_detector_check_compatibility(capability, &sim_capability);
    printf("与模拟设备的兼容性: %d%%\n", compatibility);
    
    // 比较性能
    int performance_comparison = device_capability_detector_compare_performance(capability, &sim_capability);
    printf("性能比较结果: ");
    
    switch (performance_comparison) {
        case -1:
            printf("当前设备性能较弱\n");
            break;
        case 0:
            printf("性能相当\n");
            break;
        case 1:
            printf("当前设备性能较强\n");
            break;
    }
    
    // 销毁设备能力检测器
    device_capability_detector_destroy(detector);
}

// 主函数
int main(int argc, char* argv[]) {
    printf("QEntL设备能力检测器测试程序\n");
    printf("===========================\n");
    
    // 运行所有测试
    test_basic_functionality();
    test_detailed_scan();
    test_report_generation();
    test_recommended_qubits();
    test_quantum_feature_support();
    test_compatibility_and_performance();
    
    printf("\n所有测试完成\n");
    return 0;
} 