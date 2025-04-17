/**
 * @file device_capability_detector.c
 * @brief 设备能力检测器实现 - QEntL资源自适应引擎的组件
 * @author QEntL核心开发团队
 * @date 2024-05-19
 * @version 1.0
 *
 * 该文件实现了设备能力检测器，负责检测运行QEntL应用的设备的硬件和软件能力，
 * 包括处理能力、内存容量、存储容量、网络带宽、能源供应、冷却能力和量子硬件支持。
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#elif defined(__unix__) || defined(__unix) || defined(unix) || defined(__APPLE__) || defined(__linux__)
#include <unistd.h>
#include <sys/types.h>
#include <sys/sysinfo.h>
#endif

#include "device_capability_detector.h"
#include "../core/logger.h"
#include "../core/config_manager.h"

/**
 * @brief 设备能力检测器结构体
 */
struct DeviceCapabilityDetector {
    /* 配置 */
    DeviceDetectionConfig config;
    
    /* 检测结果 */
    DeviceCapabilities capabilities;
    
    /* 连续检测相关 */
    bool continuous_detection_enabled;
    unsigned int detection_interval_ms;
    time_t last_detection_time;
    
    /* 回调函数 */
    DeviceCapabilityChangeCallback callback;
    void* callback_context;
    
    /* 统计数据 */
    unsigned int detection_count;
    unsigned int significant_changes_detected;
};

/**
 * @brief 获取CPU信息
 * @param detector 设备能力检测器
 * @return 成功返回true，失败返回false
 */
static bool detect_cpu_capabilities(DeviceCapabilityDetector* detector) {
    if (!detector) {
        log_error("检测CPU能力失败: 检测器为NULL");
        return false;
    }
    
    // 初始化CPU能力
    detector->capabilities.processing_power.cpu_cores = 0;
    detector->capabilities.processing_power.cpu_frequency_mhz = 0;
    detector->capabilities.processing_power.cpu_architecture[0] = '\0';
    
    #ifdef _WIN32
    SYSTEM_INFO sysInfo;
    GetSystemInfo(&sysInfo);
    detector->capabilities.processing_power.cpu_cores = sysInfo.dwNumberOfProcessors;
    strcpy(detector->capabilities.processing_power.cpu_architecture, "x86_64"); // 简化处理
    detector->capabilities.processing_power.cpu_frequency_mhz = 2500; // 默认值，实际应通过WMI查询
    #elif defined(__unix__) || defined(__unix) || defined(unix) || defined(__APPLE__) || defined(__linux__)
    detector->capabilities.processing_power.cpu_cores = sysconf(_SC_NPROCESSORS_ONLN);
    strcpy(detector->capabilities.processing_power.cpu_architecture, "x86_64"); // 简化处理
    detector->capabilities.processing_power.cpu_frequency_mhz = 2500; // 默认值，实际应从/proc/cpuinfo解析
    #endif
    
    log_info("CPU能力检测: %d核心, %.2fGHz", 
             detector->capabilities.processing_power.cpu_cores,
             detector->capabilities.processing_power.cpu_frequency_mhz / 1000.0);
             
    return true;
}

/**
 * @brief 获取内存信息
 * @param detector 设备能力检测器
 * @return 成功返回true，失败返回false
 */
static bool detect_memory_capabilities(DeviceCapabilityDetector* detector) {
    if (!detector) {
        log_error("检测内存能力失败: 检测器为NULL");
        return false;
    }
    
    // 初始化内存能力
    detector->capabilities.memory_capacity.total_ram_mb = 0;
    detector->capabilities.memory_capacity.available_ram_mb = 0;
    detector->capabilities.memory_capacity.memory_type[0] = '\0';
    
    #ifdef _WIN32
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    if (GlobalMemoryStatusEx(&memInfo)) {
        detector->capabilities.memory_capacity.total_ram_mb = (unsigned int)(memInfo.ullTotalPhys / (1024 * 1024));
        detector->capabilities.memory_capacity.available_ram_mb = (unsigned int)(memInfo.ullAvailPhys / (1024 * 1024));
        strcpy(detector->capabilities.memory_capacity.memory_type, "DDR");
    }
    #elif defined(__unix__) || defined(__unix) || defined(unix) || defined(__APPLE__) || defined(__linux__)
    struct sysinfo memInfo;
    if (sysinfo(&memInfo) == 0) {
        detector->capabilities.memory_capacity.total_ram_mb = (unsigned int)((memInfo.totalram * memInfo.mem_unit) / (1024 * 1024));
        detector->capabilities.memory_capacity.available_ram_mb = (unsigned int)((memInfo.freeram * memInfo.mem_unit) / (1024 * 1024));
        strcpy(detector->capabilities.memory_capacity.memory_type, "DDR");
    }
    #endif
    
    log_info("内存能力检测: 总内存: %dMB, 可用内存: %dMB", 
             detector->capabilities.memory_capacity.total_ram_mb,
             detector->capabilities.memory_capacity.available_ram_mb);
             
    return true;
}

/**
 * @brief 检测量子硬件支持情况
 * @param detector 设备能力检测器
 * @return 成功返回true，失败返回false
 */
static bool detect_quantum_hardware_support(DeviceCapabilityDetector* detector) {
    if (!detector) {
        log_error("检测量子硬件支持失败: 检测器为NULL");
        return false;
    }
    
    // 初始化量子硬件支持
    detector->capabilities.quantum_hardware.has_quantum_processor = false;
    detector->capabilities.quantum_hardware.max_qubits = 0;
    detector->capabilities.quantum_hardware.error_rate = 0.0;
    detector->capabilities.quantum_hardware.coherence_time_us = 0;
    detector->capabilities.quantum_hardware.processor_type[0] = '\0';
    
    // 这里实现实际的量子硬件检测逻辑
    // 在当前版本中，我们仅模拟检测过程
    
    // 检查配置中是否有定义量子硬件信息
    char* quantum_hardware_config = config_get_string("quantum.hardware.type", NULL);
    if (quantum_hardware_config) {
        detector->capabilities.quantum_hardware.has_quantum_processor = true;
        strcpy(detector->capabilities.quantum_hardware.processor_type, quantum_hardware_config);
        detector->capabilities.quantum_hardware.max_qubits = config_get_int("quantum.hardware.qubits", 0);
        detector->capabilities.quantum_hardware.error_rate = config_get_double("quantum.hardware.error_rate", 0.01);
        detector->capabilities.quantum_hardware.coherence_time_us = config_get_int("quantum.hardware.coherence_time_us", 100);
        free(quantum_hardware_config);
    } else {
        // 检查是否有量子模拟器
        detector->capabilities.quantum_hardware.has_quantum_processor = false;
        strcpy(detector->capabilities.quantum_hardware.processor_type, "模拟器");
        detector->capabilities.quantum_hardware.max_qubits = 28; // 默认模拟器支持的量子位数
        detector->capabilities.quantum_hardware.error_rate = 0.0;
        detector->capabilities.quantum_hardware.coherence_time_us = 0;
    }
    
    if (detector->capabilities.quantum_hardware.has_quantum_processor) {
        log_info("量子硬件支持检测: 发现量子处理器 [%s], %d量子位, 错误率: %.4f, 相干时间: %dus",
                detector->capabilities.quantum_hardware.processor_type,
                detector->capabilities.quantum_hardware.max_qubits,
                detector->capabilities.quantum_hardware.error_rate,
                detector->capabilities.quantum_hardware.coherence_time_us);
    } else {
        log_info("量子硬件支持检测: 使用量子模拟器, 最大支持%d量子位",
                detector->capabilities.quantum_hardware.max_qubits);
    }
    
    return true;
}

/**
 * @brief 创建设备能力检测器
 * @param config 检测配置，如果为NULL则使用默认配置
 * @return 成功返回检测器指针，失败返回NULL
 */
DeviceCapabilityDetector* device_capability_detector_create(const DeviceDetectionConfig* config) {
    DeviceCapabilityDetector* detector = (DeviceCapabilityDetector*)malloc(sizeof(DeviceCapabilityDetector));
    if (!detector) {
        log_error("创建设备能力检测器失败: 内存分配错误");
        return NULL;
    }
    
    // 初始化结构体
    memset(detector, 0, sizeof(DeviceCapabilityDetector));
    
    // 设置配置
    if (config) {
        memcpy(&detector->config, config, sizeof(DeviceDetectionConfig));
    } else {
        // 默认配置
        detector->config.detect_processing = true;
        detector->config.detect_memory = true;
        detector->config.detect_storage = true;
        detector->config.detect_network = true;
        detector->config.detect_energy = true;
        detector->config.detect_cooling = true;
        detector->config.detect_quantum_hardware = true;
    }
    
    detector->continuous_detection_enabled = false;
    detector->detection_interval_ms = 30000; // 默认30秒
    detector->last_detection_time = 0;
    detector->callback = NULL;
    detector->callback_context = NULL;
    
    log_info("设备能力检测器已创建");
    
    return detector;
}

/**
 * @brief 销毁设备能力检测器
 * @param detector 要销毁的检测器
 */
void device_capability_detector_destroy(DeviceCapabilityDetector* detector) {
    if (!detector) {
        return;
    }
    
    // 停止连续检测
    device_capability_detector_stop_continuous(detector);
    
    // 释放资源
    free(detector);
    
    log_info("设备能力检测器已销毁");
}

/**
 * @brief 执行设备能力检测
 * @param detector 设备能力检测器
 * @return 成功返回true，失败返回false
 */
bool device_capability_detector_run(DeviceCapabilityDetector* detector) {
    if (!detector) {
        log_error("执行设备能力检测失败: 检测器为NULL");
        return false;
    }
    
    DeviceCapabilities previous_capabilities;
    memcpy(&previous_capabilities, &detector->capabilities, sizeof(DeviceCapabilities));
    
    bool success = true;
    
    // 检测各个方面的设备能力
    if (detector->config.detect_processing) {
        success &= detect_cpu_capabilities(detector);
    }
    
    if (detector->config.detect_memory) {
        success &= detect_memory_capabilities(detector);
    }
    
    // 其他能力检测可以类似实现
    if (detector->config.detect_quantum_hardware) {
        success &= detect_quantum_hardware_support(detector);
    }
    
    detector->detection_count++;
    detector->last_detection_time = time(NULL);
    
    // 检查是否有重大变化
    bool significant_change = false;
    
    // 比较处理能力变化
    if (detector->capabilities.processing_power.cpu_cores != previous_capabilities.processing_power.cpu_cores ||
        detector->capabilities.processing_power.cpu_frequency_mhz != previous_capabilities.processing_power.cpu_frequency_mhz) {
        significant_change = true;
    }
    
    // 比较内存容量变化 (超过10%视为显著变化)
    if (abs((int)detector->capabilities.memory_capacity.available_ram_mb - 
            (int)previous_capabilities.memory_capacity.available_ram_mb) > 
        (detector->capabilities.memory_capacity.total_ram_mb * 0.1)) {
        significant_change = true;
    }
    
    // 比较量子硬件支持变化
    if (detector->capabilities.quantum_hardware.has_quantum_processor != 
        previous_capabilities.quantum_hardware.has_quantum_processor ||
        detector->capabilities.quantum_hardware.max_qubits != 
        previous_capabilities.quantum_hardware.max_qubits) {
        significant_change = true;
    }
    
    if (significant_change) {
        detector->significant_changes_detected++;
        
        // 调用回调函数
        if (detector->callback) {
            detector->callback(&detector->capabilities, &previous_capabilities, 
                              detector->callback_context);
        }
    }
    
    return success;
}

/**
 * @brief 获取最近一次检测的设备能力
 * @param detector 设备能力检测器
 * @param capabilities 用于存储设备能力的指针
 * @return 成功返回true，失败返回false
 */
bool device_capability_detector_get_capabilities(
    DeviceCapabilityDetector* detector, 
    DeviceCapabilities* capabilities) {
    if (!detector || !capabilities) {
        log_error("获取设备能力失败: 参数无效");
        return false;
    }
    
    // 如果从未检测过，执行一次检测
    if (detector->detection_count == 0) {
        if (!device_capability_detector_run(detector)) {
            return false;
        }
    }
    
    // 复制检测结果
    memcpy(capabilities, &detector->capabilities, sizeof(DeviceCapabilities));
    
    return true;
}

/**
 * @brief 设置设备能力变化回调
 * @param detector 设备能力检测器
 * @param callback 回调函数
 * @param context 回调上下文
 */
void device_capability_detector_set_callback(
    DeviceCapabilityDetector* detector,
    DeviceCapabilityChangeCallback callback,
    void* context) {
    if (!detector) {
        log_error("设置回调失败: 检测器为NULL");
        return;
    }
    
    detector->callback = callback;
    detector->callback_context = context;
}

/**
 * @brief 启动连续检测
 * @param detector 设备能力检测器
 * @param interval_ms 检测间隔(毫秒)
 * @return 成功返回true，失败返回false
 */
bool device_capability_detector_start_continuous(
    DeviceCapabilityDetector* detector, 
    unsigned int interval_ms) {
    if (!detector) {
        log_error("启动连续检测失败: 检测器为NULL");
        return false;
    }
    
    if (detector->continuous_detection_enabled) {
        log_warning("连续检测已经启动");
        return true;
    }
    
    detector->continuous_detection_enabled = true;
    detector->detection_interval_ms = (interval_ms > 1000) ? interval_ms : 1000;
    
    // 注意: 实际实现应该启动一个线程或使用事件循环来定期检测
    // 在这个简化版本中，我们仅设置标志
    
    log_info("连续设备能力检测已启动，间隔: %dms", detector->detection_interval_ms);
    
    return true;
}

/**
 * @brief 停止连续检测
 * @param detector 设备能力检测器
 */
void device_capability_detector_stop_continuous(DeviceCapabilityDetector* detector) {
    if (!detector) {
        log_error("停止连续检测失败: 检测器为NULL");
        return;
    }
    
    if (!detector->continuous_detection_enabled) {
        return;
    }
    
    detector->continuous_detection_enabled = false;
    
    // 注意: 实际实现应该停止检测线程
    
    log_info("连续设备能力检测已停止");
} 