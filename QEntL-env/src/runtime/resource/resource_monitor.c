/**
 * QEntL资源监控器实现
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月25日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "resource_monitor.h"
#include "../../common/logger.h"
#include "../../common/timer.h"

#ifdef _WIN32
#include <windows.h>
#include <psapi.h>
#elif defined(__unix__) || defined(__linux__) || defined(__APPLE__)
#include <sys/sysinfo.h>
#include <sys/statvfs.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

#define MAX_CALLBACKS 10
#define MAX_HISTORY_SIZE 1000

/**
 * 回调注册项结构体
 */
typedef struct {
    bool in_use;
    ResourceChangeCallback callback;
    ResourceType resource_type;
    ResourceAlertLevel alert_level_filter;
    void* user_data;
} CallbackRegistration;

/**
 * 资源监控器结构体
 */
struct ResourceMonitor {
    ResourceMonitorConfig config;       // 监控配置
    bool active;                        // 是否处于活跃状态
    bool paused;                        // 是否暂停
    
    ResourceStatus current_status;      // 当前资源状态
    ResourceStatus* history;            // 历史状态记录
    int history_size;                   // 历史记录大小
    int history_capacity;               // 历史记录容量
    int history_index;                  // 当前历史记录索引
    
    CallbackRegistration callbacks[MAX_CALLBACKS]; // 回调函数注册表
    int callback_count;                 // 已注册回调数量
    
    int timer_id;                       // 定时器ID
    time_t last_update_time;            // 上次更新时间
    
    // 内部计数器
    uint64_t update_count;              // 更新计数
    uint64_t alert_count;               // 警报计数
    
    // 网络统计
    uint64_t last_network_in;           // 上次入站流量
    uint64_t last_network_out;          // 上次出站流量
    
    // 文件句柄
    FILE* log_file;                     // 日志文件
};

// 前向声明内部函数
static void resource_monitor_timer_callback(void* user_data);
static bool update_resource_status(ResourceMonitor* monitor);
static void check_alerts(ResourceMonitor* monitor, const ResourceStatus* old_status);
static void notify_callbacks(ResourceMonitor* monitor, ResourceType type, ResourceAlertLevel level);
static void add_to_history(ResourceMonitor* monitor, const ResourceStatus* status);
static void log_status(ResourceMonitor* monitor, const ResourceStatus* status);
static int get_timer_interval(MonitorFrequency frequency);
static ResourceAlertLevel check_resource_alert_level(double usage, double warning_threshold, double critical_threshold);
static bool detect_cpu_status(ResourceStatus* status);
static bool detect_memory_status(ResourceStatus* status);
static bool detect_storage_status(ResourceStatus* status);
static bool detect_network_status(ResourceStatus* status);
static bool detect_gpu_status(ResourceStatus* status);
static bool detect_quantum_status(ResourceStatus* status);

/**
 * 创建资源监控器
 */
ResourceMonitor* resource_monitor_create(const ResourceMonitorConfig* config) {
    ResourceMonitor* monitor = (ResourceMonitor*)malloc(sizeof(ResourceMonitor));
    if (monitor == NULL) {
        LOG_ERROR("无法分配资源监控器内存");
        return NULL;
    }
    
    // 初始化结构体
    memset(monitor, 0, sizeof(ResourceMonitor));
    
    // 如果提供了配置，则使用它
    if (config != NULL) {
        memcpy(&monitor->config, config, sizeof(ResourceMonitorConfig));
    } else {
        // 默认配置
        monitor->config.frequency = MONITOR_FREQUENCY_MEDIUM;
        monitor->config.monitor_cpu = true;
        monitor->config.monitor_memory = true;
        monitor->config.monitor_storage = true;
        monitor->config.monitor_network = true;
        monitor->config.monitor_gpu = false;  // 默认不监控GPU
        monitor->config.monitor_quantum = false; // 默认不监控量子资源
        
        // 默认警报阈值
        monitor->config.cpu_warning_threshold = 70.0;     // 70%
        monitor->config.cpu_critical_threshold = 90.0;    // 90%
        monitor->config.memory_warning_threshold = 80.0;
        monitor->config.memory_critical_threshold = 95.0;
        monitor->config.storage_warning_threshold = 85.0;
        monitor->config.storage_critical_threshold = 95.0;
        monitor->config.network_warning_threshold = 70.0;
        monitor->config.network_critical_threshold = 90.0;
        monitor->config.gpu_warning_threshold = 80.0;
        monitor->config.gpu_critical_threshold = 95.0;
        monitor->config.quantum_warning_threshold = 80.0;
        monitor->config.quantum_critical_threshold = 95.0;
        
        // 默认历史记录大小
        monitor->config.history_size = 100;
        monitor->config.enable_logging = false;
    }
    
    // 分配历史记录空间
    monitor->history_capacity = (monitor->config.history_size > 0) ? 
                               monitor->config.history_size : 
                               100; // 默认保存100条记录
    
    monitor->history = (ResourceStatus*)malloc(sizeof(ResourceStatus) * monitor->history_capacity);
    if (monitor->history == NULL) {
        LOG_ERROR("无法分配历史记录内存");
        free(monitor);
        return NULL;
    }
    
    // 初始化历史记录
    memset(monitor->history, 0, sizeof(ResourceStatus) * monitor->history_capacity);
    
    // 初始化当前状态
    memset(&monitor->current_status, 0, sizeof(ResourceStatus));
    monitor->current_status.timestamp = time(NULL);
    
    // 打开日志文件（如果需要）
    if (monitor->config.enable_logging && monitor->config.log_file[0] != '\0') {
        monitor->log_file = fopen(monitor->config.log_file, "a");
        if (monitor->log_file == NULL) {
            LOG_WARNING("无法打开资源监控日志文件: %s", monitor->config.log_file);
        } else {
            fprintf(monitor->log_file, "\n--- 资源监控开始于 %s ---\n", __DATE__ " " __TIME__);
        }
    }
    
    LOG_INFO("资源监控器创建成功");
    return monitor;
}

/**
 * 销毁资源监控器
 */
void resource_monitor_destroy(ResourceMonitor* monitor) {
    if (monitor == NULL) {
        return;
    }
    
    // 停止资源监控
    resource_monitor_stop(monitor);
    
    // 关闭日志文件
    if (monitor->log_file != NULL) {
        fprintf(monitor->log_file, "--- 资源监控结束于 %s ---\n", __DATE__ " " __TIME__);
        fclose(monitor->log_file);
        monitor->log_file = NULL;
    }
    
    // 释放历史记录
    if (monitor->history != NULL) {
        free(monitor->history);
        monitor->history = NULL;
    }
    
    // 释放结构体
    free(monitor);
    
    LOG_INFO("资源监控器已销毁");
}

/**
 * 启动资源监控
 */
bool resource_monitor_start(ResourceMonitor* monitor) {
    if (monitor == NULL) {
        LOG_ERROR("无法启动资源监控: 监控器为空");
        return false;
    }
    
    if (monitor->active) {
        LOG_WARNING("资源监控器已经启动");
        return true;
    }
    
    // 获取初始资源状态
    if (!update_resource_status(monitor)) {
        LOG_ERROR("无法获取初始资源状态");
        return false;
    }
    
    // 开始定时器
    int interval = get_timer_interval(monitor->config.frequency);
    monitor->timer_id = timer_start(interval, resource_monitor_timer_callback, monitor);
    if (monitor->timer_id == 0) {
        LOG_ERROR("无法启动资源监控定时器");
        return false;
    }
    
    monitor->active = true;
    monitor->paused = false;
    LOG_INFO("资源监控已启动，更新间隔: %d 毫秒", interval);
    
    return true;
}

/**
 * 停止资源监控
 */
void resource_monitor_stop(ResourceMonitor* monitor) {
    if (monitor == NULL || !monitor->active) {
        return;
    }
    
    // 停止定时器
    if (monitor->timer_id != 0) {
        timer_stop(monitor->timer_id);
        monitor->timer_id = 0;
    }
    
    monitor->active = false;
    monitor->paused = false;
    LOG_INFO("资源监控已停止，总更新次数: %llu", monitor->update_count);
}

/**
 * 暂停资源监控
 */
void resource_monitor_pause(ResourceMonitor* monitor) {
    if (monitor == NULL || !monitor->active || monitor->paused) {
        return;
    }
    
    // 暂停定时器
    if (monitor->timer_id != 0) {
        timer_pause(monitor->timer_id);
    }
    
    monitor->paused = true;
    LOG_INFO("资源监控已暂停");
}

/**
 * 恢复资源监控
 */
void resource_monitor_resume(ResourceMonitor* monitor) {
    if (monitor == NULL || !monitor->active || !monitor->paused) {
        return;
    }
    
    // 恢复定时器
    if (monitor->timer_id != 0) {
        timer_resume(monitor->timer_id);
    }
    
    monitor->paused = false;
    LOG_INFO("资源监控已恢复");
}

/**
 * 获取当前资源状态
 */
bool resource_monitor_get_status(ResourceMonitor* monitor, ResourceStatus* status) {
    if (monitor == NULL || status == NULL) {
        LOG_ERROR("无法获取资源状态: 参数为空");
        return false;
    }
    
    // 如果监控器处于非活跃状态，尝试更新一次
    if (!monitor->active || difftime(time(NULL), monitor->last_update_time) > 5) {
        if (!update_resource_status(monitor)) {
            LOG_ERROR("无法更新资源状态");
            return false;
        }
    }
    
    // 复制当前状态
    memcpy(status, &monitor->current_status, sizeof(ResourceStatus));
    return true;
}

/**
 * 手动触发一次资源状态更新
 */
bool resource_monitor_update_status(ResourceMonitor* monitor) {
    if (monitor == NULL) {
        LOG_ERROR("无法更新资源状态: 监控器为空");
        return false;
    }
    
    return update_resource_status(monitor);
}

/**
 * 注册资源变化回调
 */
int resource_monitor_register_callback(ResourceMonitor* monitor,
                                      ResourceChangeCallback callback,
                                      ResourceType resource_type,
                                      ResourceAlertLevel alert_level_filter,
                                      void* user_data) {
    if (monitor == NULL || callback == NULL) {
        LOG_ERROR("无法注册回调: 参数为空");
        return -1;
    }
    
    // 查找空闲位置
    int slot = -1;
    for (int i = 0; i < MAX_CALLBACKS; i++) {
        if (!monitor->callbacks[i].in_use) {
            slot = i;
            break;
        }
    }
    
    if (slot == -1) {
        LOG_ERROR("无法注册回调: 回调列表已满");
        return -1;
    }
    
    // 注册回调
    monitor->callbacks[slot].in_use = true;
    monitor->callbacks[slot].callback = callback;
    monitor->callbacks[slot].resource_type = resource_type;
    monitor->callbacks[slot].alert_level_filter = alert_level_filter;
    monitor->callbacks[slot].user_data = user_data;
    
    monitor->callback_count++;
    
    LOG_INFO("已注册资源回调，类型: %d，级别过滤: %d，总回调数: %d", 
           resource_type, alert_level_filter, monitor->callback_count);
    
    return slot;
}

/**
 * 取消注册资源变化回调
 */
bool resource_monitor_unregister_callback(ResourceMonitor* monitor, int callback_id) {
    if (monitor == NULL) {
        LOG_ERROR("无法取消注册回调: 监控器为空");
        return false;
    }
    
    if (callback_id < 0 || callback_id >= MAX_CALLBACKS || !monitor->callbacks[callback_id].in_use) {
        LOG_ERROR("无法取消注册回调: 无效的回调ID");
        return false;
    }
    
    // 清除回调注册
    monitor->callbacks[callback_id].in_use = false;
    monitor->callbacks[callback_id].callback = NULL;
    monitor->callback_count--;
    
    LOG_INFO("已取消注册资源回调，ID: %d，剩余回调数: %d", 
           callback_id, monitor->callback_count);
    
    return true;
}

/**
 * 设置监控频率
 */
void resource_monitor_set_frequency(ResourceMonitor* monitor, MonitorFrequency frequency) {
    if (monitor == NULL) {
        return;
    }
    
    if (monitor->config.frequency == frequency) {
        return; // 频率没变，不需要更新
    }
    
    monitor->config.frequency = frequency;
    
    // 如果监控器处于活跃状态，更新定时器
    if (monitor->active && monitor->timer_id != 0) {
        // 停止当前定时器
        timer_stop(monitor->timer_id);
        
        // 启动新定时器
        int interval = get_timer_interval(frequency);
        monitor->timer_id = timer_start(interval, resource_monitor_timer_callback, monitor);
        
        LOG_INFO("已更新资源监控频率: %d，新间隔: %d 毫秒", 
               frequency, interval);
    }
}

/**
 * 获取监控频率的毫秒间隔
 */
static int get_timer_interval(MonitorFrequency frequency) {
    switch (frequency) {
        case MONITOR_FREQUENCY_LOW:
            return 10000;  // 10秒
        case MONITOR_FREQUENCY_MEDIUM:
            return 3000;   // 3秒
        case MONITOR_FREQUENCY_HIGH:
            return 1000;   // 1秒
        case MONITOR_FREQUENCY_REALTIME:
            return 500;    // 0.5秒
        default:
            return 3000;   // 默认3秒
    }
}

/**
 * 定时器回调函数
 */
static void resource_monitor_timer_callback(void* user_data) {
    ResourceMonitor* monitor = (ResourceMonitor*)user_data;
    if (monitor == NULL || !monitor->active || monitor->paused) {
        return;
    }
    
    update_resource_status(monitor);
}

/**
 * 获取历史资源状态
 */
bool resource_monitor_get_history(ResourceMonitor* monitor,
                                 ResourceStatus* history,
                                 int max_items,
                                 int* actual_items) {
    if (monitor == NULL || history == NULL || max_items <= 0) {
        LOG_ERROR("无法获取历史记录: 参数无效");
        return false;
    }
    
    // 确定实际要返回的记录数
    int count = (monitor->history_size < max_items) ? monitor->history_size : max_items;
    
    // 如果历史记录是空的
    if (count == 0) {
        if (actual_items != NULL) {
            *actual_items = 0;
        }
        return true;
    }
    
    // 从最近的记录开始复制
    int start_index = (monitor->history_index - 1 + monitor->history_capacity) % monitor->history_capacity;
    
    for (int i = 0; i < count; i++) {
        int src_index = (start_index - i + monitor->history_capacity) % monitor->history_capacity;
        memcpy(&history[i], &monitor->history[src_index], sizeof(ResourceStatus));
    }
    
    if (actual_items != NULL) {
        *actual_items = count;
    }
    
    return true;
}

/**
 * 清除历史记录
 */
void resource_monitor_clear_history(ResourceMonitor* monitor) {
    if (monitor == NULL) {
        return;
    }
    
    // 清空历史记录内容
    memset(monitor->history, 0, sizeof(ResourceStatus) * monitor->history_capacity);
    monitor->history_size = 0;
    monitor->history_index = 0;
    
    LOG_INFO("资源监控历史记录已清空");
}

/**
 * 更新资源状态
 */
static bool update_resource_status(ResourceMonitor* monitor) {
    if (monitor == NULL) {
        return false;
    }
    
    // 保存旧状态用于比较
    ResourceStatus old_status;
    memcpy(&old_status, &monitor->current_status, sizeof(ResourceStatus));
    
    // 更新时间戳
    monitor->current_status.timestamp = time(NULL);
    monitor->last_update_time = monitor->current_status.timestamp;
    
    bool success = true;
    
    // 根据配置检测各类资源
    if (monitor->config.monitor_cpu) {
        success &= detect_cpu_status(&monitor->current_status);
    }
    
    if (monitor->config.monitor_memory) {
        success &= detect_memory_status(&monitor->current_status);
    }
    
    if (monitor->config.monitor_storage) {
        success &= detect_storage_status(&monitor->current_status);
    }
    
    if (monitor->config.monitor_network) {
        success &= detect_network_status(&monitor->current_status);
    }
    
    if (monitor->config.monitor_gpu) {
        success &= detect_gpu_status(&monitor->current_status);
    }
    
    if (monitor->config.monitor_quantum) {
        success &= detect_quantum_status(&monitor->current_status);
    }
    
    // 检查各资源警报级别
    monitor->current_status.cpu_alert = check_resource_alert_level(
        monitor->current_status.cpu_usage,
        monitor->config.cpu_warning_threshold,
        monitor->config.cpu_critical_threshold
    );
    
    monitor->current_status.memory_alert = check_resource_alert_level(
        monitor->current_status.memory_usage,
        monitor->config.memory_warning_threshold,
        monitor->config.memory_critical_threshold
    );
    
    monitor->current_status.storage_alert = check_resource_alert_level(
        monitor->current_status.storage_usage,
        monitor->config.storage_warning_threshold,
        monitor->config.storage_critical_threshold
    );
    
    monitor->current_status.network_alert = check_resource_alert_level(
        monitor->current_status.network_usage,
        monitor->config.network_warning_threshold,
        monitor->config.network_critical_threshold
    );
    
    if (monitor->current_status.has_gpu) {
        monitor->current_status.gpu_alert = check_resource_alert_level(
            monitor->current_status.gpu_usage,
            monitor->config.gpu_warning_threshold,
            monitor->config.gpu_critical_threshold
        );
    }
    
    if (monitor->current_status.has_quantum_status) {
        monitor->current_status.quantum_alert = check_resource_alert_level(
            monitor->current_status.quantum_resource_usage,
            monitor->config.quantum_warning_threshold,
            monitor->config.quantum_critical_threshold
        );
    }
    
    // 更新计数器
    monitor->update_count++;
    
    // 写入历史记录
    add_to_history(monitor, &monitor->current_status);
    
    // 写入日志（如果启用）
    if (monitor->config.enable_logging && monitor->log_file != NULL) {
        log_status(monitor, &monitor->current_status);
    }
    
    // 检查警报并通知回调
    check_alerts(monitor, &old_status);
    
    return success;
}

/**
 * 检查资源警报级别
 */
static ResourceAlertLevel check_resource_alert_level(double usage, double warning_threshold, double critical_threshold) {
    if (usage >= critical_threshold) {
        return RESOURCE_ALERT_CRITICAL;
    } else if (usage >= warning_threshold) {
        return RESOURCE_ALERT_WARNING;
    } else {
        return RESOURCE_ALERT_NONE;
    }
}

/**
 * 检查警报并通知回调
 */
static void check_alerts(ResourceMonitor* monitor, const ResourceStatus* old_status) {
    // 检查CPU警报
    if (monitor->current_status.cpu_alert != old_status->cpu_alert) {
        notify_callbacks(monitor, RESOURCE_TYPE_CPU, monitor->current_status.cpu_alert);
    }
    
    // 检查内存警报
    if (monitor->current_status.memory_alert != old_status->memory_alert) {
        notify_callbacks(monitor, RESOURCE_TYPE_MEMORY, monitor->current_status.memory_alert);
    }
    
    // 检查存储警报
    if (monitor->current_status.storage_alert != old_status->storage_alert) {
        notify_callbacks(monitor, RESOURCE_TYPE_STORAGE, monitor->current_status.storage_alert);
    }
    
    // 检查网络警报
    if (monitor->current_status.network_alert != old_status->network_alert) {
        notify_callbacks(monitor, RESOURCE_TYPE_NETWORK, monitor->current_status.network_alert);
    }
    
    // 检查GPU警报
    if (monitor->current_status.has_gpu && 
        monitor->current_status.gpu_alert != old_status->gpu_alert) {
        notify_callbacks(monitor, RESOURCE_TYPE_GPU, monitor->current_status.gpu_alert);
    }
    
    // 检查量子资源警报
    if (monitor->current_status.has_quantum_status && 
        monitor->current_status.quantum_alert != old_status->quantum_alert) {
        notify_callbacks(monitor, RESOURCE_TYPE_QUANTUM, monitor->current_status.quantum_alert);
    }
}

/**
 * 通知回调
 */
static void notify_callbacks(ResourceMonitor* monitor, ResourceType type, ResourceAlertLevel level) {
    if (level == RESOURCE_ALERT_NONE) {
        return; // 不需要通知无警报状态
    }
    
    for (int i = 0; i < MAX_CALLBACKS; i++) {
        if (monitor->callbacks[i].in_use && 
            (monitor->callbacks[i].resource_type == type || monitor->callbacks[i].resource_type == (ResourceType)-1) && 
            monitor->callbacks[i].alert_level_filter <= level) {
            
            monitor->callbacks[i].callback(&monitor->current_status, type, level, monitor->callbacks[i].user_data);
            monitor->alert_count++;
        }
    }
}

/**
 * 添加到历史记录
 */
static void add_to_history(ResourceMonitor* monitor, const ResourceStatus* status) {
    if (monitor->history == NULL) {
        return;
    }
    
    // 复制状态到当前位置
    memcpy(&monitor->history[monitor->history_index], status, sizeof(ResourceStatus));
    
    // 更新索引
    monitor->history_index = (monitor->history_index + 1) % monitor->history_capacity;
    
    // 更新历史大小
    if (monitor->history_size < monitor->history_capacity) {
        monitor->history_size++;
    }
}

/**
 * 记录状态到日志
 */
static void log_status(ResourceMonitor* monitor, const ResourceStatus* status) {
    if (monitor->log_file == NULL) {
        return;
    }
    
    time_t now = time(NULL);
    struct tm* time_info = localtime(&now);
    char time_str[20];
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", time_info);
    
    fprintf(monitor->log_file, "[%s] CPU: %.1f%%, MEM: %.1f%%, STORAGE: %.1f%%, NET: %.1f%%",
           time_str, status->cpu_usage, status->memory_usage, 
           status->storage_usage, status->network_usage);
    
    if (status->has_gpu) {
        fprintf(monitor->log_file, ", GPU: %.1f%%", status->gpu_usage);
    }
    
    if (status->has_quantum_status) {
        fprintf(monitor->log_file, ", QUANTUM: %.1f%%, Error: %.3f%%", 
               status->quantum_resource_usage, status->quantum_error_rate);
    }
    
    fprintf(monitor->log_file, "\n");
}

/**
 * 检测CPU状态
 */
static bool detect_cpu_status(ResourceStatus* status) {
#ifdef _WIN32
    // Windows实现
    FILETIME idle_time, kernel_time, user_time;
    if (!GetSystemTimes(&idle_time, &kernel_time, &user_time)) {
        LOG_ERROR("GetSystemTimes失败");
        return false;
    }
    
    static ULARGE_INTEGER last_idle = {0}, last_kernel = {0}, last_user = {0};
    ULARGE_INTEGER current_idle, current_kernel, current_user;
    
    current_idle.LowPart = idle_time.dwLowDateTime;
    current_idle.HighPart = idle_time.dwHighDateTime;
    current_kernel.LowPart = kernel_time.dwLowDateTime;
    current_kernel.HighPart = kernel_time.dwHighDateTime;
    current_user.LowPart = user_time.dwLowDateTime;
    current_user.HighPart = user_time.dwHighDateTime;
    
    if (last_idle.QuadPart != 0) {
        ULONGLONG idle_diff = current_idle.QuadPart - last_idle.QuadPart;
        ULONGLONG kernel_diff = current_kernel.QuadPart - last_kernel.QuadPart;
        ULONGLONG user_diff = current_user.QuadPart - last_user.QuadPart;
        ULONGLONG system_diff = kernel_diff + user_diff;
        
        if (system_diff > 0) {
            status->cpu_usage = 100.0 - ((double)idle_diff * 100.0 / (double)system_diff);
        }
    }
    
    last_idle = current_idle;
    last_kernel = current_kernel;
    last_user = current_user;
    
    // 获取CPU温度 - Windows未实现
    status->cpu_temperature = 0;
    
#elif defined(__unix__) || defined(__linux__)
    // Linux实现
    FILE* file = fopen("/proc/stat", "r");
    if (file == NULL) {
        LOG_ERROR("无法打开/proc/stat");
        return false;
    }
    
    static unsigned long long last_user = 0, last_nice = 0, last_system = 0, last_idle = 0;
    unsigned long long user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice;
    
    fscanf(file, "cpu %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu",
          &user, &nice, &system, &idle, &iowait, &irq, &softirq, &steal, &guest, &guest_nice);
    
    fclose(file);
    
    unsigned long long idle_all = idle + iowait;
    unsigned long long system_all = system + irq + softirq;
    unsigned long long total = user + nice + system_all + idle_all + steal + guest + guest_nice;
    
    if (last_user > 0) {
        unsigned long long idle_diff = idle_all - last_idle;
        unsigned long long total_diff = total - (last_user + last_nice + last_system + last_idle);
        
        if (total_diff > 0) {
            status->cpu_usage = 100.0 * (1.0 - (double)idle_diff / (double)total_diff);
        }
    }
    
    last_user = user;
    last_nice = nice;
    last_system = system;
    last_idle = idle_all;
    
    // 尝试获取CPU温度
    file = fopen("/sys/class/thermal/thermal_zone0/temp", "r");
    if (file != NULL) {
        int temp;
        if (fscanf(file, "%d", &temp) == 1) {
            status->cpu_temperature = temp / 1000; // 转换为摄氏度
        }
        fclose(file);
    }
#else
    // 其他平台简化实现
    status->cpu_usage = 50.0; // 默认值
    status->cpu_temperature = 0;
#endif

    return true;
}

/**
 * 检测内存状态
 */
static bool detect_memory_status(ResourceStatus* status) {
#ifdef _WIN32
    // Windows实现
    MEMORYSTATUSEX memory_status;
    memory_status.dwLength = sizeof(memory_status);
    if (!GlobalMemoryStatusEx(&memory_status)) {
        LOG_ERROR("GlobalMemoryStatusEx失败");
        return false;
    }
    
    status->memory_usage = (double)memory_status.dwMemoryLoad;
    status->memory_available = memory_status.ullAvailPhys;
    status->memory_total = memory_status.ullTotalPhys;
    
#elif defined(__unix__) || defined(__linux__)
    // Linux实现
    struct sysinfo info;
    if (sysinfo(&info) != 0) {
        LOG_ERROR("sysinfo调用失败");
        return false;
    }
    
    status->memory_total = info.totalram * info.mem_unit;
    status->memory_available = info.freeram * info.mem_unit;
    status->memory_usage = 100.0 * (1.0 - (double)info.freeram / (double)info.totalram);
    
#else
    // 其他平台简化实现
    status->memory_usage = 60.0; // 默认值
    status->memory_available = 1024 * 1024 * 1024; // 1GB
    status->memory_total = 4 * 1024 * 1024 * 1024; // 4GB
#endif

    return true;
}

/**
 * 检测存储状态
 */
static bool detect_storage_status(ResourceStatus* status) {
#ifdef _WIN32
    // Windows实现 - 检测C盘
    ULARGE_INTEGER free_bytes, total_bytes, total_free_bytes;
    if (!GetDiskFreeSpaceExA("C:\\", &free_bytes, &total_bytes, &total_free_bytes)) {
        LOG_ERROR("GetDiskFreeSpaceEx失败");
        return false;
    }
    
    status->storage_available = free_bytes.QuadPart;
    status->storage_total = total_bytes.QuadPart;
    status->storage_usage = 100.0 * (1.0 - (double)free_bytes.QuadPart / (double)total_bytes.QuadPart);
    
#elif defined(__unix__) || defined(__linux__)
    // Linux实现 - 检测根目录
    struct statvfs stat;
    if (statvfs("/", &stat) != 0) {
        LOG_ERROR("statvfs调用失败");
        return false;
    }
    
    status->storage_available = stat.f_bsize * stat.f_bavail;
    status->storage_total = stat.f_blocks * stat.f_frsize;
    status->storage_usage = 100.0 * (1.0 - (double)stat.f_bavail / (double)stat.f_blocks);
    
#else
    // 其他平台简化实现
    status->storage_usage = 70.0; // 默认值
    status->storage_available = 10 * 1024 * 1024 * 1024; // 10GB
    status->storage_total = 100 * 1024 * 1024 * 1024; // 100GB
#endif

    return true;
}

/**
 * 检测网络状态
 */
static bool detect_network_status(ResourceStatus* status) {
    // 网络状态检测比较复杂且平台相关性高，此处提供简化实现
    // 实际应用中需要根据具体平台和需求实现
    
    status->network_usage = 30.0; // 默认值
    status->network_in_rate = 1024 * 1024; // 1MB/s
    status->network_out_rate = 512 * 1024; // 512KB/s
    
    return true;
}

/**
 * 检测GPU状态
 */
static bool detect_gpu_status(ResourceStatus* status) {
    // GPU状态检测需要特定的API (如NVIDIA的NVML或AMD的ADL)
    // 此处提供简化实现
    
    status->has_gpu = true; // 默认假设有GPU
    status->gpu_usage = 40.0; // 默认值
    status->gpu_temperature = 65; // 默认65°C
    status->gpu_memory_used = 1 * 1024 * 1024 * 1024; // 默认1GB
    status->gpu_memory_total = 4 * 1024 * 1024 * 1024; // 默认4GB
    
    return true;
}

/**
 * 检测量子资源状态
 */
static bool detect_quantum_status(ResourceStatus* status) {
    // 量子资源状态检测需要与量子硬件或模拟器接口
    // 此处提供模拟实现以供接口测试
    
    status->has_quantum_status = true;
    status->quantum_resource_usage = 25.0; // 默认值
    status->quantum_error_rate = 0.05; // 5%错误率
    status->quantum_decoherence_rate = 0.02; // 2%退相干率
    status->active_qubits = 16; // 16个活跃量子比特
    status->quantum_circuit_depth = 20; // 电路深度
    
    return true;
}

/**
 * 获取监控器是否处于活跃状态
 */
bool resource_monitor_is_active(ResourceMonitor* monitor) {
    if (monitor == NULL) {
        return false;
    }
    
    return monitor->active;
}

/**
 * 获取最后一次更新时间
 */
time_t resource_monitor_get_last_update_time(ResourceMonitor* monitor) {
    if (monitor == NULL) {
        return 0;
    }
    
    return monitor->last_update_time;
}

/**
 * 设置警报阈值
 */
void resource_monitor_set_alert_threshold(ResourceMonitor* monitor,
                                         ResourceType resource_type,
                                         double warning_threshold,
                                         double critical_threshold) {
    if (monitor == NULL) {
        return;
    }
    
    // 确保阈值合理
    if (warning_threshold < 0.0) warning_threshold = 0.0;
    if (warning_threshold > 100.0) warning_threshold = 100.0;
    if (critical_threshold < warning_threshold) critical_threshold = warning_threshold;
    if (critical_threshold > 100.0) critical_threshold = 100.0;
    
    // 设置对应资源的阈值
    switch (resource_type) {
        case RESOURCE_TYPE_CPU:
            monitor->config.cpu_warning_threshold = warning_threshold;
            monitor->config.cpu_critical_threshold = critical_threshold;
            break;
            
        case RESOURCE_TYPE_MEMORY:
            monitor->config.memory_warning_threshold = warning_threshold;
            monitor->config.memory_critical_threshold = critical_threshold;
            break;
            
        case RESOURCE_TYPE_STORAGE:
            monitor->config.storage_warning_threshold = warning_threshold;
            monitor->config.storage_critical_threshold = critical_threshold;
            break;
            
        case RESOURCE_TYPE_NETWORK:
            monitor->config.network_warning_threshold = warning_threshold;
            monitor->config.network_critical_threshold = critical_threshold;
            break;
            
        case RESOURCE_TYPE_GPU:
            monitor->config.gpu_warning_threshold = warning_threshold;
            monitor->config.gpu_critical_threshold = critical_threshold;
            break;
            
        case RESOURCE_TYPE_QUANTUM:
            monitor->config.quantum_warning_threshold = warning_threshold;
            monitor->config.quantum_critical_threshold = critical_threshold;
            break;
    }
    
    LOG_INFO("已更新资源警报阈值，类型: %d，警告: %.1f%%，严重: %.1f%%", 
           resource_type, warning_threshold, critical_threshold);
}

/**
 * 获取量子特定资源状态
 */
bool resource_monitor_get_quantum_status(ResourceMonitor* monitor,
                                        int* active_qubits,
                                        double* error_rate,
                                        double* decoherence_rate) {
    if (monitor == NULL) {
        return false;
    }
    
    // 如果没有量子状态信息
    if (!monitor->current_status.has_quantum_status) {
        // 如果配置了监控量子资源，尝试更新一次
        if (monitor->config.monitor_quantum) {
            if (!update_resource_status(monitor) || !monitor->current_status.has_quantum_status) {
                LOG_ERROR("无法获取量子资源状态");
                return false;
            }
        } else {
            LOG_ERROR("未配置量子资源监控");
            return false;
        }
    }
    
    // 填充返回值
    if (active_qubits != NULL) {
        *active_qubits = monitor->current_status.active_qubits;
    }
    
    if (error_rate != NULL) {
        *error_rate = monitor->current_status.quantum_error_rate;
    }
    
    if (decoherence_rate != NULL) {
        *decoherence_rate = monitor->current_status.quantum_decoherence_rate;
    }
    
    return true;
}

/**
 * 生成资源使用报告
 */
bool resource_monitor_generate_report(ResourceMonitor* monitor,
                                     const char* filename,
                                     bool include_history) {
    if (monitor == NULL || filename == NULL) {
        LOG_ERROR("无法生成报告: 参数为空");
        return false;
    }
    
    FILE* file = fopen(filename, "w");
    if (file == NULL) {
        LOG_ERROR("无法打开文件生成报告: %s", filename);
        return false;
    }
    
    // 写入报告头部
    time_t now = time(NULL);
    struct tm* time_info = localtime(&now);
    char time_str[64];
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", time_info);
    
    fprintf(file, "===========================================\n");
    fprintf(file, "   QEntL资源监控报告 - 生成于 %s\n", time_str);
    fprintf(file, "===========================================\n\n");
    
    // 写入摘要信息
    fprintf(file, "监控状态: %s\n", monitor->active ? "活跃" : "非活跃");
    fprintf(file, "更新次数: %llu\n", monitor->update_count);
    fprintf(file, "警报次数: %llu\n", monitor->alert_count);
    fprintf(file, "最后更新: %s\n", ctime(&monitor->last_update_time));
    fprintf(file, "\n");
    
    // 写入当前资源状态
    fprintf(file, "当前资源状态:\n");
    fprintf(file, "-----------------------------------------\n");
    fprintf(file, "CPU 使用率: %.1f%% (%s)\n", 
           monitor->current_status.cpu_usage,
           monitor->current_status.cpu_alert == RESOURCE_ALERT_CRITICAL ? "严重" : 
           monitor->current_status.cpu_alert == RESOURCE_ALERT_WARNING ? "警告" : "正常");
    
    if (monitor->current_status.cpu_temperature > 0) {
        fprintf(file, "CPU 温度: %d°C\n", monitor->current_status.cpu_temperature);
    }
    
    fprintf(file, "内存使用率: %.1f%% (%s)\n", 
           monitor->current_status.memory_usage,
           monitor->current_status.memory_alert == RESOURCE_ALERT_CRITICAL ? "严重" : 
           monitor->current_status.memory_alert == RESOURCE_ALERT_WARNING ? "警告" : "正常");
    
    double mem_available_gb = (double)monitor->current_status.memory_available / (1024.0 * 1024.0 * 1024.0);
    double mem_total_gb = (double)monitor->current_status.memory_total / (1024.0 * 1024.0 * 1024.0);
    fprintf(file, "可用内存: %.2f GB / %.2f GB\n", mem_available_gb, mem_total_gb);
    
    fprintf(file, "存储使用率: %.1f%% (%s)\n", 
           monitor->current_status.storage_usage,
           monitor->current_status.storage_alert == RESOURCE_ALERT_CRITICAL ? "严重" : 
           monitor->current_status.storage_alert == RESOURCE_ALERT_WARNING ? "警告" : "正常");
    
    double storage_available_gb = (double)monitor->current_status.storage_available / (1024.0 * 1024.0 * 1024.0);
    double storage_total_gb = (double)monitor->current_status.storage_total / (1024.0 * 1024.0 * 1024.0);
    fprintf(file, "可用存储: %.2f GB / %.2f GB\n", storage_available_gb, storage_total_gb);
    
    fprintf(file, "网络使用率: %.1f%% (%s)\n", 
           monitor->current_status.network_usage,
           monitor->current_status.network_alert == RESOURCE_ALERT_CRITICAL ? "严重" : 
           monitor->current_status.network_alert == RESOURCE_ALERT_WARNING ? "警告" : "正常");
    
    fprintf(file, "网络流量: 入站 %.2f MB/s, 出站 %.2f MB/s\n", 
           monitor->current_status.network_in_rate / (1024.0 * 1024.0),
           monitor->current_status.network_out_rate / (1024.0 * 1024.0));
    
    if (monitor->current_status.has_gpu) {
        fprintf(file, "\nGPU 状态:\n");
        fprintf(file, "-----------------------------------------\n");
        fprintf(file, "GPU 使用率: %.1f%% (%s)\n", 
               monitor->current_status.gpu_usage,
               monitor->current_status.gpu_alert == RESOURCE_ALERT_CRITICAL ? "严重" : 
               monitor->current_status.gpu_alert == RESOURCE_ALERT_WARNING ? "警告" : "正常");
        
        fprintf(file, "GPU 温度: %d°C\n", monitor->current_status.gpu_temperature);
        
        double gpu_mem_used_gb = (double)monitor->current_status.gpu_memory_used / (1024.0 * 1024.0 * 1024.0);
        double gpu_mem_total_gb = (double)monitor->current_status.gpu_memory_total / (1024.0 * 1024.0 * 1024.0);
        fprintf(file, "GPU 内存: %.2f GB / %.2f GB\n", gpu_mem_used_gb, gpu_mem_total_gb);
    }
    
    if (monitor->current_status.has_quantum_status) {
        fprintf(file, "\n量子资源状态:\n");
        fprintf(file, "-----------------------------------------\n");
        fprintf(file, "量子资源使用率: %.1f%% (%s)\n", 
               monitor->current_status.quantum_resource_usage,
               monitor->current_status.quantum_alert == RESOURCE_ALERT_CRITICAL ? "严重" : 
               monitor->current_status.quantum_alert == RESOURCE_ALERT_WARNING ? "警告" : "正常");
        
        fprintf(file, "活跃量子比特: %d\n", monitor->current_status.active_qubits);
        fprintf(file, "量子错误率: %.2f%%\n", monitor->current_status.quantum_error_rate * 100.0);
        fprintf(file, "退相干率: %.2f%%\n", monitor->current_status.quantum_decoherence_rate * 100.0);
        fprintf(file, "量子电路深度: %d\n", monitor->current_status.quantum_circuit_depth);
    }
    
    fprintf(file, "\n配置信息:\n");
    fprintf(file, "-----------------------------------------\n");
    fprintf(file, "监控频率: %d\n", monitor->config.frequency);
    fprintf(file, "CPU 警告阈值: %.1f%%\n", monitor->config.cpu_warning_threshold);
    fprintf(file, "CPU 严重阈值: %.1f%%\n", monitor->config.cpu_critical_threshold);
    fprintf(file, "内存警告阈值: %.1f%%\n", monitor->config.memory_warning_threshold);
    fprintf(file, "内存严重阈值: %.1f%%\n", monitor->config.memory_critical_threshold);
    fprintf(file, "存储警告阈值: %.1f%%\n", monitor->config.storage_warning_threshold);
    fprintf(file, "存储严重阈值: %.1f%%\n", monitor->config.storage_critical_threshold);
    fprintf(file, "网络警告阈值: %.1f%%\n", monitor->config.network_warning_threshold);
    fprintf(file, "网络严重阈值: %.1f%%\n", monitor->config.network_critical_threshold);
    
    if (monitor->config.monitor_gpu) {
        fprintf(file, "GPU 警告阈值: %.1f%%\n", monitor->config.gpu_warning_threshold);
        fprintf(file, "GPU 严重阈值: %.1f%%\n", monitor->config.gpu_critical_threshold);
    }
    
    if (monitor->config.monitor_quantum) {
        fprintf(file, "量子资源警告阈值: %.1f%%\n", monitor->config.quantum_warning_threshold);
        fprintf(file, "量子资源严重阈值: %.1f%%\n", monitor->config.quantum_critical_threshold);
    }
    
    // 如果请求包含历史数据且有历史记录
    if (include_history && monitor->history_size > 0) {
        fprintf(file, "\n历史记录:\n");
        fprintf(file, "-----------------------------------------\n");
        fprintf(file, "时间戳               CPU    内存    存储    网络");
        
        if (monitor->config.monitor_gpu) {
            fprintf(file, "    GPU");
        }
        
        if (monitor->config.monitor_quantum) {
            fprintf(file, "    量子");
        }
        
        fprintf(file, "\n");
        
        // 最多输出100条历史记录
        int max_entries = monitor->history_size < 100 ? monitor->history_size : 100;
        int start_index = (monitor->history_index - 1 + monitor->history_capacity) % monitor->history_capacity;
        
        for (int i = 0; i < max_entries; i++) {
            int idx = (start_index - i + monitor->history_capacity) % monitor->history_capacity;
            ResourceStatus* entry = &monitor->history[idx];
            
            // 跳过空记录
            if (entry->timestamp == 0) {
                continue;
            }
            
            struct tm* time_info = localtime(&entry->timestamp);
            char time_str[20];
            strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", time_info);
            
            fprintf(file, "%-20s %5.1f%% %5.1f%% %5.1f%% %5.1f%%",
                   time_str, entry->cpu_usage, entry->memory_usage, 
                   entry->storage_usage, entry->network_usage);
            
            if (monitor->config.monitor_gpu && entry->has_gpu) {
                fprintf(file, " %5.1f%%", entry->gpu_usage);
            }
            
            if (monitor->config.monitor_quantum && entry->has_quantum_status) {
                fprintf(file, " %5.1f%%", entry->quantum_resource_usage);
            }
            
            fprintf(file, "\n");
        }
    }
    
    fclose(file);
    LOG_INFO("资源监控报告已生成: %s", filename);
    
    return true;
}