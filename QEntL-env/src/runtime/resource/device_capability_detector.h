/**
 * QEntL设备能力检测器头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月20日
 */

#ifndef QENTL_DEVICE_CAPABILITY_DETECTOR_H
#define QENTL_DEVICE_CAPABILITY_DETECTOR_H

#include <stdbool.h>
#include <stdint.h>

// CPU能力数据结构
typedef struct {
    int cores;                  // CPU核心数
    int threads;                // 线程数
    double frequency_ghz;       // 频率（GHz）
    double max_frequency_ghz;   // 最大频率（GHz）
    char model_name[256];       // CPU型号名称
    int64_t cache_size_kb;      // 缓存大小（KB）
    bool has_avx;               // 是否支持AVX指令集
    bool has_avx2;              // 是否支持AVX2指令集
    bool has_sse4;              // 是否支持SSE4指令集
    bool has_aes;               // 是否支持AES指令
    double benchmark_score;     // 基准测试得分
} CPUCapability;

// 内存能力数据结构
typedef struct {
    int64_t total_physical_memory;  // 总物理内存（字节）
    int64_t available_memory;       // 可用内存（字节）
    int64_t virtual_memory;         // 虚拟内存大小（字节）
    int64_t page_size;              // 内存页大小（字节）
    double memory_bandwidth;        // 内存带宽（MB/s）
    int memory_channels;            // 内存通道数
    double benchmark_read_speed;    // 读取速度基准（MB/s）
    double benchmark_write_speed;   // 写入速度基准（MB/s）
} MemoryCapability;

// 存储能力数据结构
typedef struct {
    int64_t total_capacity;         // 总容量（字节）
    int64_t available_capacity;     // 可用容量（字节）
    bool is_ssd;                    // 是否为SSD
    double read_speed;              // 读取速度（MB/s）
    double write_speed;             // 写入速度（MB/s）
    double iops;                    // IOPS（每秒I/O操作数）
    char file_system[64];           // 文件系统类型
    double access_time_ms;          // 平均访问时间（毫秒）
} StorageCapability;

// 网络能力数据结构
typedef struct {
    double bandwidth_mbps;          // 带宽（Mbps）
    double latency_ms;              // 延迟（毫秒）
    double packet_loss;             // 丢包率
    double jitter_ms;               // 抖动（毫秒）
    bool has_ipv6;                  // 是否支持IPv6
    bool has_wifi;                  // 是否有WiFi
    bool has_ethernet;              // 是否有以太网
    bool has_cellular;              // 是否有蜂窝网络
    char adapter_name[64];          // 网络适配器名称
    char ip_address[64];            // IP地址
} NetworkCapability;

// GPU能力数据结构
typedef struct {
    bool available;                 // 是否可用
    char model_name[256];           // GPU型号名称
    int64_t memory_size;            // 显存大小（字节）
    int cuda_cores;                 // CUDA核心数
    double clock_rate_mhz;          // 时钟频率（MHz）
    double memory_bandwidth;        // 显存带宽（GB/s）
    int compute_capability_major;   // 计算能力主版本
    int compute_capability_minor;   // 计算能力次版本
    bool supports_tensor_cores;     // 是否支持Tensor核心
    double fp32_performance_tflops; // FP32性能（TFLOPS）
    double fp16_performance_tflops; // FP16性能（TFLOPS）
} GPUCapability;

// 量子处理能力数据结构
typedef struct {
    bool available;                 // 是否可用
    int qubits;                     // 量子比特数
    double coherence_time_us;       // 相干时间（微秒）
    double gate_fidelity;           // 门保真度
    double readout_fidelity;        // 读取保真度
    int max_entangled_qubits;       // 最大纠缠量子比特数
    int qubit_topology;             // 量子比特拓扑结构（0=线性，1=网格，2=全连接）
    double t1_time_us;              // T1时间（微秒）
    double t2_time_us;              // T2时间（微秒）
    bool supports_error_correction; // 是否支持错误纠正
} QuantumCapability;

// 设备类型枚举
typedef enum {
    DEVICE_DESKTOP,       // 桌面电脑
    DEVICE_LAPTOP,        // 笔记本
    DEVICE_SERVER,        // 服务器
    DEVICE_MOBILE,        // 移动设备
    DEVICE_EMBEDDED,      // 嵌入式设备
    DEVICE_QUANTUM,       // 量子计算设备
    DEVICE_CLOUD,         // 云实例
    DEVICE_UNKNOWN        // 未知设备
} DeviceType;

// 操作系统类型枚举
typedef enum {
    OS_WINDOWS,           // Windows
    OS_LINUX,             // Linux
    OS_MACOS,             // macOS
    OS_ANDROID,           // Android
    OS_IOS,               // iOS
    OS_RTOS,              // 实时操作系统
    OS_OTHER,             // 其他操作系统
    OS_UNKNOWN            // 未知操作系统
} OSType;

// 综合设备能力数据结构
typedef struct {
    DeviceType device_type;         // 设备类型
    OSType os_type;                 // 操作系统类型
    char device_name[256];          // 设备名称
    char os_version[64];            // 操作系统版本
    int logical_processors;         // 逻辑处理器数量
    
    CPUCapability cpu;              // CPU能力
    MemoryCapability memory;        // 内存能力
    StorageCapability storage;      // 存储能力
    NetworkCapability network;      // 网络能力
    GPUCapability gpu;              // GPU能力
    QuantumCapability quantum;      // 量子处理能力
    
    double composite_score;         // 综合性能得分
    int recommended_qubits;         // 推荐量子比特数
    
    bool detection_complete;        // 检测是否完成
    bool detailed_scan;             // 是否进行了详细扫描
} DeviceCapability;

// 设备能力检测器前置声明
typedef struct DeviceCapabilityDetector DeviceCapabilityDetector;

// 创建设备能力检测器
DeviceCapabilityDetector* device_capability_detector_create(void);

// 销毁设备能力检测器
void device_capability_detector_destroy(DeviceCapabilityDetector* detector);

// 执行设备能力检测
bool device_capability_detector_scan(DeviceCapabilityDetector* detector, bool detailed_scan);

// 获取设备能力
const DeviceCapability* device_capability_detector_get_capability(DeviceCapabilityDetector* detector);

// 保存设备能力报告到文件
bool device_capability_detector_save_report(DeviceCapabilityDetector* detector, const char* filename);

// 获取设备类型字符串
const char* device_capability_detector_get_device_type_string(DeviceType type);

// 获取操作系统类型字符串
const char* device_capability_detector_get_os_type_string(OSType type);

// 获取推荐的最大量子比特数
int device_capability_detector_get_recommended_qubits(DeviceCapabilityDetector* detector);

// 检查设备是否支持特定的量子功能
bool device_capability_detector_supports_quantum_feature(DeviceCapabilityDetector* detector, const char* feature);

// 获取设备性能评分
double device_capability_detector_get_performance_score(DeviceCapabilityDetector* detector);

// 更新设备能力信息（手动强制更新）
bool device_capability_detector_update(DeviceCapabilityDetector* detector);

// 检查两个设备的兼容性级别（0-100）
int device_capability_detector_check_compatibility(const DeviceCapability* dev1, const DeviceCapability* dev2);

// 比较两个设备的性能（返回值: -1:dev1较弱, 0:相当, 1:dev1较强）
int device_capability_detector_compare_performance(const DeviceCapability* dev1, const DeviceCapability* dev2);

#endif /* QENTL_DEVICE_CAPABILITY_DETECTOR_H */ 