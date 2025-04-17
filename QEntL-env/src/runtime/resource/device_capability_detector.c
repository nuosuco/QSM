/**
 * QEntL设备能力检测器实现
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月25日
 * 
 * 设备能力检测器负责检测当前设备的计算能力和支持的量子功能，
 * 为资源自适应引擎提供设备能力信息。
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "device_capability_detector.h"

// 定义最大处理器数量
#define MAX_PROCESSORS 256

// 设备能力检测器结构体实现
struct DeviceCapabilityDetector {
    DeviceCapability current_capability;   // 当前检测到的设备能力
    bool has_cached_results;               // 是否有缓存的检测结果
    bool is_scanning;                      // 是否正在扫描
    time_t last_scan_time;                 // 上次扫描时间
    int scan_count;                        // 扫描计数
    char device_id[64];                    // 设备唯一ID
    
    // 操作系统特定参数
    bool is_windows;                       // 是否Windows系统
    bool is_linux;                         // 是否Linux系统
    bool is_macos;                         // 是否macOS系统
    
    // 缓存数据
    CPUCapability cached_cpu;              // 缓存的CPU能力
    MemoryCapability cached_memory;        // 缓存的内存能力
    StorageCapability cached_storage;      // 缓存的存储能力
    NetworkCapability cached_network;      // 缓存的网络能力
    GPUCapability cached_gpu;              // 缓存的GPU能力
    QuantumCapability cached_quantum;      // 缓存的量子能力
};

// 静态函数声明
static bool detect_cpu_capability(DeviceCapabilityDetector* detector, CPUCapability* cpu);
static bool detect_memory_capability(DeviceCapabilityDetector* detector, MemoryCapability* memory);
static bool detect_storage_capability(DeviceCapabilityDetector* detector, StorageCapability* storage);
static bool detect_network_capability(DeviceCapabilityDetector* detector, NetworkCapability* network);
static bool detect_gpu_capability(DeviceCapabilityDetector* detector, GPUCapability* gpu);
static bool detect_quantum_capability(DeviceCapabilityDetector* detector, QuantumCapability* quantum);
static bool generate_device_id(DeviceCapabilityDetector* detector);
static double calculate_device_performance_score(const DeviceCapability* capability);
static OSType detect_os_type();

// 创建设备能力检测器
DeviceCapabilityDetector* device_capability_detector_create() {
    DeviceCapabilityDetector* detector = (DeviceCapabilityDetector*)malloc(sizeof(DeviceCapabilityDetector));
    if (!detector) {
        return NULL;
    }
    
    // 初始化结构体
    memset(detector, 0, sizeof(DeviceCapabilityDetector));
    detector->has_cached_results = false;
    detector->is_scanning = false;
    detector->last_scan_time = 0;
    detector->scan_count = 0;
    
    // 检测操作系统类型
    OSType os_type = detect_os_type();
    detector->is_windows = (os_type == OS_TYPE_WINDOWS);
    detector->is_linux = (os_type == OS_TYPE_LINUX);
    detector->is_macos = (os_type == OS_TYPE_MACOS);
    detector->current_capability.os_type = os_type;
    
    // 生成设备ID
    generate_device_id(detector);
    
    return detector;
}

// 销毁设备能力检测器
void device_capability_detector_destroy(DeviceCapabilityDetector* detector) {
    if (detector) {
        free(detector);
    }
}

// 扫描设备能力
bool device_capability_detector_scan(DeviceCapabilityDetector* detector) {
    if (!detector) {
        return false;
    }
    
    // 标记正在扫描
    detector->is_scanning = true;
    
    // 扫描各种能力
    bool cpu_success = detect_cpu_capability(detector, &detector->current_capability.cpu);
    bool memory_success = detect_memory_capability(detector, &detector->current_capability.memory);
    bool storage_success = detect_storage_capability(detector, &detector->current_capability.storage);
    bool network_success = detect_network_capability(detector, &detector->current_capability.network);
    bool gpu_success = detect_gpu_capability(detector, &detector->current_capability.gpu);
    bool quantum_success = detect_quantum_capability(detector, &detector->current_capability.quantum);
    
    // 更新缓存
    if (cpu_success) {
        memcpy(&detector->cached_cpu, &detector->current_capability.cpu, sizeof(CPUCapability));
    }
    if (memory_success) {
        memcpy(&detector->cached_memory, &detector->current_capability.memory, sizeof(MemoryCapability));
    }
    if (storage_success) {
        memcpy(&detector->cached_storage, &detector->current_capability.storage, sizeof(StorageCapability));
    }
    if (network_success) {
        memcpy(&detector->cached_network, &detector->current_capability.network, sizeof(NetworkCapability));
    }
    if (gpu_success) {
        memcpy(&detector->cached_gpu, &detector->current_capability.gpu, sizeof(GPUCapability));
    }
    if (quantum_success) {
        memcpy(&detector->cached_quantum, &detector->current_capability.quantum, sizeof(QuantumCapability));
    }
    
    // 计算综合性能分数
    detector->current_capability.composite_score = calculate_device_performance_score(&detector->current_capability);
    
    // 标记为有缓存结果
    detector->has_cached_results = true;
    detector->last_scan_time = time(NULL);
    detector->scan_count++;
    
    // 扫描完成
    detector->is_scanning = false;
    
    // 检查是否所有检测都成功
    return cpu_success && memory_success && storage_success && 
           network_success && gpu_success && quantum_success;
}

// 获取设备能力
bool device_capability_detector_get_capability(DeviceCapabilityDetector* detector, DeviceCapability* capability) {
    if (!detector || !capability) {
        return false;
    }
    
    // 如果没有缓存结果，执行扫描
    if (!detector->has_cached_results) {
        if (!device_capability_detector_scan(detector)) {
            return false;
        }
    }
    
    // 复制结果
    memcpy(capability, &detector->current_capability, sizeof(DeviceCapability));
    return true;
}

// 保存设备能力报告
bool device_capability_detector_save_report(DeviceCapabilityDetector* detector, const char* filename) {
    if (!detector || !filename) {
        return false;
    }
    
    // 如果没有缓存结果，执行扫描
    if (!detector->has_cached_results) {
        if (!device_capability_detector_scan(detector)) {
            return false;
        }
    }
    
    // 打开文件
    FILE* file = fopen(filename, "w");
    if (!file) {
        return false;
    }
    
    // 写入报告标题
    fprintf(file, "# QEntL 设备能力报告\n");
    fprintf(file, "设备ID: %s\n", detector->device_id);
    fprintf(file, "扫描时间: %s", ctime(&detector->last_scan_time));
    fprintf(file, "扫描次数: %d\n\n", detector->scan_count);
    
    // 写入操作系统信息
    fprintf(file, "## 操作系统信息\n");
    const char* os_type_str = "未知";
    switch (detector->current_capability.os_type) {
        case OS_TYPE_WINDOWS: os_type_str = "Windows"; break;
        case OS_TYPE_LINUX: os_type_str = "Linux"; break;
        case OS_TYPE_MACOS: os_type_str = "macOS"; break;
        case OS_TYPE_ANDROID: os_type_str = "Android"; break;
        case OS_TYPE_IOS: os_type_str = "iOS"; break;
        case OS_TYPE_OTHER: os_type_str = "其他"; break;
    }
    fprintf(file, "操作系统类型: %s\n\n", os_type_str);
    
    // 写入CPU信息
    fprintf(file, "## CPU 能力\n");
    fprintf(file, "CPU名称: %s\n", detector->current_capability.cpu.cpu_name);
    fprintf(file, "核心数: %d\n", detector->current_capability.cpu.core_count);
    fprintf(file, "线程数: %d\n", detector->current_capability.cpu.thread_count);
    fprintf(file, "基准频率: %.2f GHz\n", detector->current_capability.cpu.base_clock_speed);
    fprintf(file, "最大频率: %.2f GHz\n", detector->current_capability.cpu.max_clock_speed);
    fprintf(file, "支持SIMD: %s\n", detector->current_capability.cpu.has_simd ? "是" : "否");
    fprintf(file, "支持AVX: %s\n", detector->current_capability.cpu.has_avx ? "是" : "否");
    fprintf(file, "支持AVX2: %s\n", detector->current_capability.cpu.has_avx2 ? "是" : "否");
    fprintf(file, "支持AVX512: %s\n", detector->current_capability.cpu.has_avx512 ? "是" : "否");
    fprintf(file, "L1缓存: %d KB\n", detector->current_capability.cpu.l1_cache_size_kb);
    fprintf(file, "L2缓存: %d KB\n", detector->current_capability.cpu.l2_cache_size_kb);
    fprintf(file, "L3缓存: %d KB\n\n", detector->current_capability.cpu.l3_cache_size_kb);
    
    // 写入内存信息
    fprintf(file, "## 内存能力\n");
    fprintf(file, "总内存: %.2f GB\n", detector->current_capability.memory.total_memory_bytes / (1024.0 * 1024.0 * 1024.0));
    fprintf(file, "可用内存: %.2f GB\n", detector->current_capability.memory.available_memory_bytes / (1024.0 * 1024.0 * 1024.0));
    fprintf(file, "内存速度: %d MHz\n", detector->current_capability.memory.memory_speed_mhz);
    fprintf(file, "内存类型: %s\n\n", detector->current_capability.memory.memory_type);
    
    // 写入存储信息
    fprintf(file, "## 存储能力\n");
    fprintf(file, "总存储: %.2f GB\n", detector->current_capability.storage.total_storage_bytes / (1024.0 * 1024.0 * 1024.0));
    fprintf(file, "可用存储: %.2f GB\n", detector->current_capability.storage.available_storage_bytes / (1024.0 * 1024.0 * 1024.0));
    fprintf(file, "存储类型: %s\n", detector->current_capability.storage.storage_type);
    fprintf(file, "读取速度: %.2f MB/s\n", detector->current_capability.storage.read_speed_mbps);
    fprintf(file, "写入速度: %.2f MB/s\n\n", detector->current_capability.storage.write_speed_mbps);
    
    // 写入网络信息
    fprintf(file, "## 网络能力\n");
    fprintf(file, "网络类型: %s\n", detector->current_capability.network.network_type);
    fprintf(file, "下载速度: %.2f Mbps\n", detector->current_capability.network.download_speed_mbps);
    fprintf(file, "上传速度: %.2f Mbps\n", detector->current_capability.network.upload_speed_mbps);
    fprintf(file, "延迟: %d ms\n\n", detector->current_capability.network.latency_ms);
    
    // 写入GPU信息
    fprintf(file, "## GPU 能力\n");
    if (detector->current_capability.gpu.has_gpu) {
        fprintf(file, "GPU名称: %s\n", detector->current_capability.gpu.gpu_name);
        fprintf(file, "GPU内存: %.2f GB\n", detector->current_capability.gpu.gpu_memory_bytes / (1024.0 * 1024.0 * 1024.0));
        fprintf(file, "CUDA核心: %d\n", detector->current_capability.gpu.cuda_cores);
        fprintf(file, "计算能力: %.1f\n", detector->current_capability.gpu.compute_capability);
        fprintf(file, "支持CUDA: %s\n", detector->current_capability.gpu.supports_cuda ? "是" : "否");
        fprintf(file, "支持OpenCL: %s\n", detector->current_capability.gpu.supports_opencl ? "是" : "否");
    } else {
        fprintf(file, "无GPU设备\n");
    }
    fprintf(file, "\n");
    
    // 写入量子能力信息
    fprintf(file, "## 量子计算能力\n");
    if (detector->current_capability.quantum.has_quantum_capability) {
        fprintf(file, "量子模拟器: %s\n", detector->current_capability.quantum.quantum_simulator ? "是" : "否");
        fprintf(file, "量子硬件: %s\n", detector->current_capability.quantum.quantum_hardware ? "是" : "否");
        fprintf(file, "可模拟量子比特数: %d\n", detector->current_capability.quantum.max_simulatable_qubits);
        fprintf(file, "物理量子比特数: %d\n", detector->current_capability.quantum.physical_qubits);
        fprintf(file, "逻辑量子比特数: %d\n", detector->current_capability.quantum.logical_qubits);
        fprintf(file, "量子门错误率: %.6f\n", detector->current_capability.quantum.gate_error_rate);
        fprintf(file, "量子测量错误率: %.6f\n", detector->current_capability.quantum.measurement_error_rate);
    } else {
        fprintf(file, "无量子计算能力\n");
    }
    fprintf(file, "\n");
    
    // 写入综合分数
    fprintf(file, "## 综合性能评分\n");
    fprintf(file, "综合性能分数: %.2f / 100\n", detector->current_capability.composite_score);
    
    // 关闭文件
    fclose(file);
    return true;
}

// 检查两个设备是否兼容
bool device_capability_detector_is_compatible(DeviceCapabilityDetector* detector1, DeviceCapabilityDetector* detector2) {
    if (!detector1 || !detector2) {
        return false;
    }
    
    // 确保两个检测器都有缓存的结果
    if (!detector1->has_cached_results) {
        if (!device_capability_detector_scan(detector1)) {
            return false;
        }
    }
    
    if (!detector2->has_cached_results) {
        if (!device_capability_detector_scan(detector2)) {
            return false;
        }
    }
    
    // 在这里添加兼容性检查逻辑
    // 这里简单地检查量子能力是否兼容
    if (detector1->current_capability.quantum.has_quantum_capability && detector2->current_capability.quantum.has_quantum_capability) {
        // 如果两者都有量子能力，检查它们是否可以协同工作
        return true;
    }
    
    // 如果一方有量子能力，而另一方没有，检查是否可以通过模拟器协同工作
    if (detector1->current_capability.quantum.has_quantum_capability && detector1->current_capability.quantum.quantum_simulator) {
        return true;
    }
    
    if (detector2->current_capability.quantum.has_quantum_capability && detector2->current_capability.quantum.quantum_simulator) {
        return true;
    }
    
    // 如果两者都没有量子能力，检查常规计算能力
    return (detector1->current_capability.composite_score > 20.0) && (detector2->current_capability.composite_score > 20.0);
}

// 比较两个设备的性能
int device_capability_detector_compare_performance(DeviceCapabilityDetector* detector1, DeviceCapabilityDetector* detector2) {
    if (!detector1 || !detector2) {
        return 0;
    }
    
    // 确保两个检测器都有缓存的结果
    if (!detector1->has_cached_results) {
        if (!device_capability_detector_scan(detector1)) {
            return 0;
        }
    }
    
    if (!detector2->has_cached_results) {
        if (!device_capability_detector_scan(detector2)) {
            return 0;
        }
    }
    
    // 比较综合性能分数
    if (detector1->current_capability.composite_score > detector2->current_capability.composite_score) {
        return 1;  // 第一个设备性能更好
    } else if (detector1->current_capability.composite_score < detector2->current_capability.composite_score) {
        return -1; // 第二个设备性能更好
    } else {
        return 0;  // 两个设备性能相当
    }
}

// 估计可用量子比特数
int device_capability_detector_estimate_available_qubits(DeviceCapabilityDetector* detector) {
    if (!detector) {
        return 0;
    }
    
    // 如果没有缓存结果，执行扫描
    if (!detector->has_cached_results) {
        if (!device_capability_detector_scan(detector)) {
            return 0;
        }
    }
    
    // 如果有量子硬件，返回物理量子比特数
    if (detector->current_capability.quantum.has_quantum_capability && detector->current_capability.quantum.quantum_hardware) {
        return detector->current_capability.quantum.physical_qubits;
    }
    
    // 如果有量子模拟器，返回可模拟的量子比特数
    if (detector->current_capability.quantum.has_quantum_capability && detector->current_capability.quantum.quantum_simulator) {
        return detector->current_capability.quantum.max_simulatable_qubits;
    }
    
    // 否则，根据CPU和内存估计可模拟的量子比特数
    // 对于一个经典模拟器，通常每个量子比特需要2^n个复数，每个复数需要16字节
    // 考虑到内存限制和CPU性能，我们进行一个粗略的估计
    
    int estimated_qubits = 2; // 默认至少能模拟2个量子比特
    
    // 根据可用内存估计
    uint64_t available_memory = detector->current_capability.memory.available_memory_bytes;
    int memory_based_estimate = (int)(log2(available_memory / 16.0) / 2.0);
    
    // 根据CPU核心数和性能估计
    int cpu_cores = detector->current_capability.cpu.core_count;
    double cpu_speed = detector->current_capability.cpu.max_clock_speed;
    int cpu_based_estimate = (int)(log2(cpu_cores * cpu_speed));
    
    // 取较小的估计值
    estimated_qubits = (memory_based_estimate < cpu_based_estimate) ? memory_based_estimate : cpu_based_estimate;
    
    // 考虑一些实际限制
    if (estimated_qubits > 32) {
        estimated_qubits = 32; // 实际上，完全模拟超过32个量子比特对于大多数设备来说是不现实的
    }
    
    return (estimated_qubits > 2) ? estimated_qubits : 2;
}

// 获取操作系统类型名称
const char* device_capability_detector_get_os_type_name(OSType os_type) {
    switch (os_type) {
        case OS_TYPE_WINDOWS: return "Windows";
        case OS_TYPE_LINUX: return "Linux";
        case OS_TYPE_MACOS: return "macOS";
        case OS_TYPE_ANDROID: return "Android";
        case OS_TYPE_IOS: return "iOS";
        case OS_TYPE_OTHER: return "Other";
        default: return "Unknown";
    }
}

// 静态函数实现

// 检测CPU能力
static bool detect_cpu_capability(DeviceCapabilityDetector* detector, CPUCapability* cpu) {
    if (!detector || !cpu) {
        return false;
    }
    
    // 这里简化实现，实际应该根据不同平台使用不同的检测方法
    
    // 基本信息
    strcpy(cpu->cpu_name, "Generic CPU");
    cpu->core_count = 4;
    cpu->thread_count = 8;
    cpu->base_clock_speed = 2.5;
    cpu->max_clock_speed = 3.5;
    
    // 高级特性
    cpu->has_simd = true;
    cpu->has_avx = true;
    cpu->has_avx2 = true;
    cpu->has_avx512 = false;
    
    // 缓存信息
    cpu->l1_cache_size_kb = 256;
    cpu->l2_cache_size_kb = 1024;
    cpu->l3_cache_size_kb = 8192;
    
    return true;
}

// 检测内存能力
static bool detect_memory_capability(DeviceCapabilityDetector* detector, MemoryCapability* memory) {
    if (!detector || !memory) {
        return false;
    }
    
    // 这里简化实现，实际应该根据不同平台使用不同的检测方法
    
    memory->total_memory_bytes = 16ULL * 1024 * 1024 * 1024;  // 16 GB
    memory->available_memory_bytes = 8ULL * 1024 * 1024 * 1024;  // 8 GB
    memory->memory_speed_mhz = 3200;
    strcpy(memory->memory_type, "DDR4");
    
    return true;
}

// 检测存储能力
static bool detect_storage_capability(DeviceCapabilityDetector* detector, StorageCapability* storage) {
    if (!detector || !storage) {
        return false;
    }
    
    // 这里简化实现，实际应该根据不同平台使用不同的检测方法
    
    storage->total_storage_bytes = 512ULL * 1024 * 1024 * 1024;  // 512 GB
    storage->available_storage_bytes = 256ULL * 1024 * 1024 * 1024;  // 256 GB
    strcpy(storage->storage_type, "SSD");
    storage->read_speed_mbps = 2500.0;  // 2500 MB/s
    storage->write_speed_mbps = 1800.0;  // 1800 MB/s
    
    return true;
}

// 检测网络能力
static bool detect_network_capability(DeviceCapabilityDetector* detector, NetworkCapability* network) {
    if (!detector || !network) {
        return false;
    }
    
    // 这里简化实现，实际应该根据不同平台使用不同的检测方法
    
    strcpy(network->network_type, "Ethernet");
    network->download_speed_mbps = 100.0;  // 100 Mbps
    network->upload_speed_mbps = 50.0;  // 50 Mbps
    network->latency_ms = 20;  // 20 ms
    
    return true;
}

// 检测GPU能力
static bool detect_gpu_capability(DeviceCapabilityDetector* detector, GPUCapability* gpu) {
    if (!detector || !gpu) {
        return false;
    }
    
    // 这里简化实现，实际应该根据不同平台使用不同的检测方法
    
    gpu->has_gpu = true;
    strcpy(gpu->gpu_name, "Generic GPU");
    gpu->gpu_memory_bytes = 4ULL * 1024 * 1024 * 1024;  // 4 GB
    gpu->cuda_cores = 2048;
    gpu->compute_capability = 7.5;
    gpu->supports_cuda = true;
    gpu->supports_opencl = true;
    
    return true;
}

// 检测量子能力
static bool detect_quantum_capability(DeviceCapabilityDetector* detector, QuantumCapability* quantum) {
    if (!detector || !quantum) {
        return false;
    }
    
    // 这里简化实现，假设大多数设备只有量子模拟能力，没有物理量子硬件
    
    quantum->has_quantum_capability = true;
    quantum->quantum_simulator = true;
    quantum->quantum_hardware = false;
    quantum->max_simulatable_qubits = 28;  // 假设可以模拟28个量子比特
    quantum->physical_qubits = 0;          // 没有物理量子比特
    quantum->logical_qubits = 0;           // 没有逻辑量子比特
    quantum->gate_error_rate = 0.0001;     // 模拟的门错误率
    quantum->measurement_error_rate = 0.001; // 模拟的测量错误率
    
    return true;
}

// 生成设备唯一ID
static bool generate_device_id(DeviceCapabilityDetector* detector) {
    if (!detector) {
        return false;
    }
    
    // 简单实现：使用时间戳和随机数生成一个ID
    srand((unsigned int)time(NULL));
    sprintf(detector->device_id, "QEntL-Device-%08x-%04x-%04x", 
            (unsigned int)time(NULL), 
            rand() % 65536, 
            rand() % 65536);
    
    return true;
}

// 计算设备性能分数
static double calculate_device_performance_score(const DeviceCapability* capability) {
    if (!capability) {
        return 0.0;
    }
    
    double score = 0.0;
    
    // CPU评分（最高30分）
    double cpu_score = 0.0;
    cpu_score += capability->cpu.core_count * 1.5;  // 每个核心1.5分
    cpu_score += capability->cpu.max_clock_speed * 2.0;  // 每GHz 2分
    if (capability->cpu.has_avx) cpu_score += 2.0;
    if (capability->cpu.has_avx2) cpu_score += 3.0;
    if (capability->cpu.has_avx512) cpu_score += 5.0;
    cpu_score = (cpu_score > 30.0) ? 30.0 : cpu_score;  // 最高30分
    
    // 内存评分（最高20分）
    double memory_score = 0.0;
    memory_score += (capability->memory.total_memory_bytes / (1024.0 * 1024.0 * 1024.0)) * 1.5;  // 每GB 1.5分
    memory_score += (capability->memory.memory_speed_mhz / 1000.0) * 5.0;  // 每1000MHz 5分
    memory_score = (memory_score > 20.0) ? 20.0 : memory_score;  // 最高20分
    
    // GPU评分（最高25分）
    double gpu_score = 0.0;
    if (capability->gpu.has_gpu) {
        gpu_score += (capability->gpu.gpu_memory_bytes / (1024.0 * 1024.0 * 1024.0)) * 2.0;  // 每GB 2分
        gpu_score += (capability->gpu.cuda_cores / 1000.0) * 5.0;  // 每1000CUDA核心 5分
        gpu_score += capability->gpu.compute_capability * 2.0;  // 每计算能力1.0 2分
        if (capability->gpu.supports_cuda) gpu_score += 3.0;
        if (capability->gpu.supports_opencl) gpu_score += 2.0;
    }
    gpu_score = (gpu_score > 25.0) ? 25.0 : gpu_score;  // 最高25分
    
    // 量子能力评分（最高25分）
    double quantum_score = 0.0;
    if (capability->quantum.has_quantum_capability) {
        if (capability->quantum.quantum_hardware) {
            quantum_score += capability->quantum.physical_qubits * 2.0;  // 每个物理量子比特 2分
            quantum_score += capability->quantum.logical_qubits * 5.0;  // 每个逻辑量子比特 5分
        } else if (capability->quantum.quantum_simulator) {
            quantum_score += capability->quantum.max_simulatable_qubits * 1.0;  // 每个可模拟量子比特 1分
        }
    }
    quantum_score = (quantum_score > 25.0) ? 25.0 : quantum_score;  // 最高25分
    
    // 综合评分
    score = cpu_score + memory_score + gpu_score + quantum_score;
    
    // 确保分数在0-100范围内
    score = (score > 100.0) ? 100.0 : score;
    score = (score < 0.0) ? 0.0 : score;
    
    return score;
}

// 检测操作系统类型
static OSType detect_os_type() {
#ifdef _WIN32
    return OS_TYPE_WINDOWS;
#elif defined(__APPLE__)
    return OS_TYPE_MACOS;
#elif defined(__linux__)
    return OS_TYPE_LINUX;
#elif defined(__ANDROID__)
    return OS_TYPE_ANDROID;
#else
    return OS_TYPE_OTHER;
#endif
} 