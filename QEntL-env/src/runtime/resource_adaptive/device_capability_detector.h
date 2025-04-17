/**
 * @file device_capability_detector.h
 * @brief 设备能力检测器头文件 - QEntL资源自适应引擎的组件
 * @author QEntL核心开发团队
 * @date 2024-05-19
 * @version 1.0
 *
 * 该文件定义了设备能力检测器的API和数据结构，用于检测运行QEntL应用的设备的硬件和软件能力。
 */

#ifndef QENTL_DEVICE_CAPABILITY_DETECTOR_H
#define QENTL_DEVICE_CAPABILITY_DETECTOR_H

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief 处理能力信息
 */
typedef struct {
    unsigned int cpu_cores;             /**< CPU核心数 */
    unsigned int cpu_frequency_mhz;     /**< CPU频率(MHz) */
    char cpu_architecture[32];          /**< CPU架构 */
    unsigned int gpu_cores;             /**< GPU核心数 */
    unsigned int gpu_memory_mb;         /**< GPU内存(MB) */
    float computing_power_tflops;       /**< 计算能力(TFLOPS) */
} ProcessingPower;

/**
 * @brief 内存容量信息
 */
typedef struct {
    unsigned int total_ram_mb;          /**< 总RAM(MB) */
    unsigned int available_ram_mb;      /**< 可用RAM(MB) */
    char memory_type[16];               /**< 内存类型 */
    unsigned int memory_speed_mhz;      /**< 内存速度(MHz) */
} MemoryCapacity;

/**
 * @brief 存储容量信息
 */
typedef struct {
    unsigned long long total_storage_mb;        /**< 总存储容量(MB) */
    unsigned long long available_storage_mb;    /**< 可用存储容量(MB) */
    char storage_type[16];                      /**< 存储类型 */
    unsigned int read_speed_mbps;               /**< 读取速度(MB/s) */
    unsigned int write_speed_mbps;              /**< 写入速度(MB/s) */
} StorageCapacity;

/**
 * @brief 网络带宽信息
 */
typedef struct {
    unsigned int bandwidth_mbps;         /**< 带宽(Mbps) */
    unsigned int latency_ms;             /**< 延迟(ms) */
    char network_type[16];               /**< 网络类型 */
    bool quantum_network_support;        /**< 量子网络支持 */
} NetworkBandwidth;

/**
 * @brief
 * 能源供应信息
 */
typedef struct {
    bool battery_powered;                /**< 是否使用电池供电 */
    unsigned int battery_level_percent;  /**< 电池电量百分比 */
    unsigned int power_supply_watts;     /**< 电源功率(W) */
    float energy_efficiency;             /**< 能源效率 */
} EnergySupply;

/**
 * @brief 冷却能力信息
 */
typedef struct {
    char cooling_type[32];               /**< 冷却类型 */
    float max_cooling_capacity_watts;    /**< 最大冷却能力(W) */
    float current_temperature_celsius;   /**< 当前温度(°C) */
    float max_safe_temperature_celsius;  /**< 最大安全温度(°C) */
} CoolingCapability;

/**
 * @brief 量子硬件支持信息
 */
typedef struct {
    bool has_quantum_processor;          /**< 是否有量子处理器 */
    unsigned int max_qubits;             /**< 最大量子位数 */
    double error_rate;                   /**< 错误率 */
    unsigned int coherence_time_us;      /**< 相干时间(微秒) */
    char processor_type[32];             /**< 处理器类型 */
} QuantumHardwareSupport;

/**
 * @brief 设备能力
 */
typedef struct {
    ProcessingPower processing_power;            /**< 处理能力 */
    MemoryCapacity memory_capacity;              /**< 内存容量 */
    StorageCapacity storage_capacity;            /**< 存储容量 */
    NetworkBandwidth network_bandwidth;          /**< 网络带宽 */
    EnergySupply energy_supply;                  /**< 能源供应 */
    CoolingCapability cooling_capability;        /**< 冷却能力 */
    QuantumHardwareSupport quantum_hardware;     /**< 量子硬件支持 */
} DeviceCapabilities;

/**
 * @brief 设备检测配置
 */
typedef struct {
    bool detect_processing;              /**< 是否检测处理能力 */
    bool detect_memory;                  /**< 是否检测内存容量 */
    bool detect_storage;                 /**< 是否检测存储容量 */
    bool detect_network;                 /**< 是否检测网络带宽 */
    bool detect_energy;                  /**< 是否检测能源供应 */
    bool detect_cooling;                 /**< 是否检测冷却能力 */
    bool detect_quantum_hardware;        /**< 是否检测量子硬件支持 */
} DeviceDetectionConfig;

/**
 * @brief 设备能力检测器
 */
typedef struct DeviceCapabilityDetector DeviceCapabilityDetector;

/**
 * @brief 设备能力变化回调函数类型
 * @param current 当前设备能力
 * @param previous 先前设备能力
 * @param context 回调上下文
 */
typedef void (*DeviceCapabilityChangeCallback)(
    const DeviceCapabilities* current,
    const DeviceCapabilities* previous,
    void* context);

/**
 * @brief 创建设备能力检测器
 * @param config 检测配置，如果为NULL则使用默认配置
 * @return 成功返回检测器指针，失败返回NULL
 */
DeviceCapabilityDetector* device_capability_detector_create(
    const DeviceDetectionConfig* config);

/**
 * @brief 销毁设备能力检测器
 * @param detector 要销毁的检测器
 */
void device_capability_detector_destroy(DeviceCapabilityDetector* detector);

/**
 * @brief 执行设备能力检测
 * @param detector 设备能力检测器
 * @return 成功返回true，失败返回false
 */
bool device_capability_detector_run(DeviceCapabilityDetector* detector);

/**
 * @brief 获取最近一次检测的设备能力
 * @param detector 设备能力检测器
 * @param capabilities 用于存储设备能力的指针
 * @return 成功返回true，失败返回false
 */
bool device_capability_detector_get_capabilities(
    DeviceCapabilityDetector* detector,
    DeviceCapabilities* capabilities);

/**
 * @brief 设置设备能力变化回调
 * @param detector 设备能力检测器
 * @param callback 回调函数
 * @param context 回调上下文
 */
void device_capability_detector_set_callback(
    DeviceCapabilityDetector* detector,
    DeviceCapabilityChangeCallback callback,
    void* context);

/**
 * @brief 启动连续检测
 * @param detector 设备能力检测器
 * @param interval_ms 检测间隔(毫秒)
 * @return 成功返回true，失败返回false
 */
bool device_capability_detector_start_continuous(
    DeviceCapabilityDetector* detector,
    unsigned int interval_ms);

/**
 * @brief 停止连续检测
 * @param detector 设备能力检测器
 */
void device_capability_detector_stop_continuous(
    DeviceCapabilityDetector* detector);

#ifdef __cplusplus
}
#endif

#endif /* QENTL_DEVICE_CAPABILITY_DETECTOR_H */ 