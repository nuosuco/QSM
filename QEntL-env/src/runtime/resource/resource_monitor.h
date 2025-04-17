/**
 * QEntL资源监控器头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月25日
 * 
 * 资源监控器负责实时监控系统资源使用情况，提供资源状态数据
 * 供量子比特调整器等组件进行资源自适应决策。
 */

#ifndef QENTL_RESOURCE_MONITOR_H
#define QENTL_RESOURCE_MONITOR_H

#include <stdbool.h>
#include <stdint.h>
#include <time.h>

// 前向声明
typedef struct ResourceMonitor ResourceMonitor;

/**
 * 监控频率级别枚举
 */
typedef enum {
    MONITOR_FREQUENCY_LOW,      // 低频率监控（约每10秒）
    MONITOR_FREQUENCY_MEDIUM,   // 中频率监控（约每3秒）
    MONITOR_FREQUENCY_HIGH,     // 高频率监控（约每1秒）
    MONITOR_FREQUENCY_REALTIME  // 实时监控（尽可能频繁）
} MonitorFrequency;

/**
 * 资源警报级别枚举
 */
typedef enum {
    RESOURCE_ALERT_NONE,        // 无警报
    RESOURCE_ALERT_WARNING,     // 警告级别
    RESOURCE_ALERT_CRITICAL     // 严重级别
} ResourceAlertLevel;

/**
 * 资源类型枚举
 */
typedef enum {
    RESOURCE_TYPE_CPU,          // CPU资源
    RESOURCE_TYPE_MEMORY,       // 内存资源 
    RESOURCE_TYPE_STORAGE,      // 存储资源
    RESOURCE_TYPE_NETWORK,      // 网络资源
    RESOURCE_TYPE_GPU,          // GPU资源
    RESOURCE_TYPE_QUANTUM       // 量子资源
} ResourceType;

/**
 * 资源状态结构体
 */
typedef struct {
    // 基础资源状态
    double cpu_usage;           // CPU使用率（百分比）
    double memory_usage;        // 内存使用率（百分比）
    double storage_usage;       // 存储使用率（百分比）
    double network_usage;       // 网络带宽使用率（百分比）
    
    // 额外资源详情
    int cpu_temperature;        // CPU温度（摄氏度）
    uint64_t memory_available;  // 可用内存（字节）
    uint64_t memory_total;      // 总内存（字节）
    uint64_t storage_available; // 可用存储（字节）
    uint64_t storage_total;     // 总存储（字节）
    double network_in_rate;     // 网络入站速率（字节/秒）
    double network_out_rate;    // 网络出站速率（字节/秒）
    
    // GPU资源状态（如果有）
    bool has_gpu;               // 是否有GPU
    double gpu_usage;           // GPU使用率（百分比）
    int gpu_temperature;        // GPU温度（摄氏度）
    uint64_t gpu_memory_used;   // GPU已用内存（字节）
    uint64_t gpu_memory_total;  // GPU总内存（字节）
    
    // 量子资源状态（如果有）
    bool has_quantum_status;               // 是否有量子资源状态
    double quantum_resource_usage;         // 量子资源使用率（百分比）
    double quantum_error_rate;             // 量子错误率
    double quantum_decoherence_rate;       // 量子退相干率
    int active_qubits;                     // 活跃量子比特数
    int quantum_circuit_depth;             // 当前量子电路深度
    
    // 警报状态
    ResourceAlertLevel cpu_alert;          // CPU警报级别
    ResourceAlertLevel memory_alert;       // 内存警报级别
    ResourceAlertLevel storage_alert;      // 存储警报级别
    ResourceAlertLevel network_alert;      // 网络警报级别
    ResourceAlertLevel gpu_alert;          // GPU警报级别
    ResourceAlertLevel quantum_alert;      // 量子资源警报级别
    
    // 时间戳
    time_t timestamp;                      // 状态采集时间戳
} ResourceStatus;

/**
 * 资源监控器配置结构体
 */
typedef struct {
    MonitorFrequency frequency;            // 监控频率
    bool monitor_cpu;                      // 是否监控CPU
    bool monitor_memory;                   // 是否监控内存
    bool monitor_storage;                  // 是否监控存储
    bool monitor_network;                  // 是否监控网络
    bool monitor_gpu;                      // 是否监控GPU
    bool monitor_quantum;                  // 是否监控量子资源
    
    // 警报阈值（百分比）
    double cpu_warning_threshold;          // CPU警告阈值
    double cpu_critical_threshold;         // CPU严重阈值
    double memory_warning_threshold;       // 内存警告阈值
    double memory_critical_threshold;      // 内存严重阈值
    double storage_warning_threshold;      // 存储警告阈值
    double storage_critical_threshold;     // 存储严重阈值
    double network_warning_threshold;      // 网络警告阈值
    double network_critical_threshold;     // 网络严重阈值
    double gpu_warning_threshold;          // GPU警告阈值
    double gpu_critical_threshold;         // GPU严重阈值
    double quantum_warning_threshold;      // 量子资源警告阈值
    double quantum_critical_threshold;     // 量子资源严重阈值
    
    // 历史记录配置
    int history_size;                      // 历史记录保存条数
    bool enable_logging;                   // 是否启用日志记录
    char log_file[256];                    // 日志文件路径
} ResourceMonitorConfig;

/**
 * 资源变化回调函数类型
 * @param status 资源状态
 * @param resource_type 发生变化的资源类型
 * @param alert_level 警报级别
 * @param user_data 用户数据
 */
typedef void (*ResourceChangeCallback)(const ResourceStatus* status, 
                                      ResourceType resource_type,
                                      ResourceAlertLevel alert_level,
                                      void* user_data);

/**
 * 创建资源监控器
 * @param config 监控器配置
 * @return 资源监控器实例
 */
ResourceMonitor* resource_monitor_create(const ResourceMonitorConfig* config);

/**
 * 销毁资源监控器
 * @param monitor 资源监控器实例
 */
void resource_monitor_destroy(ResourceMonitor* monitor);

/**
 * 启动资源监控
 * @param monitor 资源监控器实例
 * @return 是否成功启动
 */
bool resource_monitor_start(ResourceMonitor* monitor);

/**
 * 停止资源监控
 * @param monitor 资源监控器实例
 */
void resource_monitor_stop(ResourceMonitor* monitor);

/**
 * 暂停资源监控
 * @param monitor 资源监控器实例
 */
void resource_monitor_pause(ResourceMonitor* monitor);

/**
 * 恢复资源监控
 * @param monitor 资源监控器实例
 */
void resource_monitor_resume(ResourceMonitor* monitor);

/**
 * 获取当前资源状态
 * @param monitor 资源监控器实例
 * @param status 输出资源状态
 * @return 是否成功获取状态
 */
bool resource_monitor_get_status(ResourceMonitor* monitor, ResourceStatus* status);

/**
 * 手动触发一次资源状态更新
 * @param monitor 资源监控器实例
 * @return 是否成功更新状态
 */
bool resource_monitor_update_status(ResourceMonitor* monitor);

/**
 * 注册资源变化回调
 * @param monitor 资源监控器实例
 * @param callback 回调函数
 * @param resource_type 感兴趣的资源类型
 * @param alert_level_filter 感兴趣的警报级别（更高级别也会触发）
 * @param user_data 用户数据
 * @return 注册的回调ID，用于取消注册
 */
int resource_monitor_register_callback(ResourceMonitor* monitor,
                                      ResourceChangeCallback callback,
                                      ResourceType resource_type,
                                      ResourceAlertLevel alert_level_filter,
                                      void* user_data);

/**
 * 取消注册资源变化回调
 * @param monitor 资源监控器实例
 * @param callback_id 注册时返回的回调ID
 * @return 是否成功取消注册
 */
bool resource_monitor_unregister_callback(ResourceMonitor* monitor, int callback_id);

/**
 * 设置监控频率
 * @param monitor 资源监控器实例
 * @param frequency 新的监控频率
 */
void resource_monitor_set_frequency(ResourceMonitor* monitor, MonitorFrequency frequency);

/**
 * 获取历史资源状态
 * @param monitor 资源监控器实例
 * @param history 输出历史状态数组
 * @param max_items 最大返回条数
 * @param actual_items 实际返回条数
 * @return 是否成功获取历史
 */
bool resource_monitor_get_history(ResourceMonitor* monitor,
                                 ResourceStatus* history,
                                 int max_items,
                                 int* actual_items);

/**
 * 清除历史记录
 * @param monitor 资源监控器实例
 */
void resource_monitor_clear_history(ResourceMonitor* monitor);

/**
 * 生成资源使用报告
 * @param monitor 资源监控器实例
 * @param filename 保存文件名
 * @param include_history 是否包含历史数据
 * @return 是否成功生成报告
 */
bool resource_monitor_generate_report(ResourceMonitor* monitor,
                                     const char* filename,
                                     bool include_history);

/**
 * 设置警报阈值
 * @param monitor 资源监控器实例
 * @param resource_type 资源类型
 * @param warning_threshold 警告阈值
 * @param critical_threshold 严重阈值
 */
void resource_monitor_set_alert_threshold(ResourceMonitor* monitor,
                                         ResourceType resource_type,
                                         double warning_threshold,
                                         double critical_threshold);

/**
 * 获取量子特定资源状态
 * @param monitor 资源监控器实例
 * @param active_qubits 活跃量子比特数输出
 * @param error_rate 错误率输出
 * @param decoherence_rate 退相干率输出
 * @return 是否成功获取状态
 */
bool resource_monitor_get_quantum_status(ResourceMonitor* monitor,
                                        int* active_qubits,
                                        double* error_rate,
                                        double* decoherence_rate);

/**
 * 获取监控器是否处于活跃状态
 * @param monitor 资源监控器实例
 * @return 是否处于活跃状态
 */
bool resource_monitor_is_active(ResourceMonitor* monitor);

/**
 * 获取最后一次更新时间
 * @param monitor 资源监控器实例
 * @return 上次更新的时间戳
 */
time_t resource_monitor_get_last_update_time(ResourceMonitor* monitor);

#endif /* QENTL_RESOURCE_MONITOR_H */ 