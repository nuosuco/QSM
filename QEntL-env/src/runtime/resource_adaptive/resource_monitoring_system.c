/**
 * 资源监控系统实现 - QEntL运行时环境的组件
 * 负责监控量子计算资源的使用情况和可用性
 * 
 * 作者: QEntL核心开发团队
 * 日期: 2024-05-18
 * 版本: 1.0
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "resource_monitoring_system.h"
#include "../event_system.h"
#include "../quantum_core/quantum_executor.h"
#include "device_capability_detector.h"

// 内部结构定义

/**
 * 资源使用记录
 */
typedef struct {
    ResourceType type;         // 资源类型
    double used_amount;        // 已使用的资源量
    double peak_amount;        // 峰值使用量
    time_t timestamp;          // 记录时间戳
} ResourceUsageRecord;

/**
 * 资源阈值警报
 */
typedef struct {
    ResourceType type;                // 资源类型
    double threshold;                 // 阈值百分比(0.0-1.0)
    ThresholdSeverity severity;       // 严重程度
    ResourceThresholdCallback callback; // 回调函数
    void* user_data;                  // 用户数据
    int is_active;                    // 是否激活
} ResourceThreshold;

/**
 * 性能计数器
 */
typedef struct {
    unsigned long operations_count;   // 操作计数
    double operation_rate;            // 操作速率(每秒)
    time_t last_calculation;          // 上次计算时间
} PerformanceCounter;

/**
 * 资源监控系统内部结构
 */
struct ResourceMonitoringSystem {
    MonitoringConfig config;              // 监控配置
    ResourceUsageRecord* usage_records;   // 资源使用记录数组
    size_t records_count;                 // 记录数量
    size_t records_capacity;              // 记录容量
    
    ResourceThreshold* thresholds;        // 阈值数组
    size_t thresholds_count;              // 阈值数量
    size_t thresholds_capacity;           // 阈值容量
    
    PerformanceCounter* counters;         // 性能计数器数组
    size_t counters_count;                // 计数器数量
    
    time_t start_time;                    // 监控开始时间
    time_t last_update;                   // 上次更新时间
    
    ResourceStatsSnapshot latest_snapshot; // 最新快照
    
    EventSystem* event_system;            // 事件系统引用
    int is_active;                        // 是否激活
};

// 内部函数声明
static void update_resource_usage(ResourceMonitoringSystem* system);
static void check_thresholds(ResourceMonitoringSystem* system);
static void calculate_performance(ResourceMonitoringSystem* system);
static void emit_resource_event(ResourceMonitoringSystem* system, ResourceEventType event_type, ResourceType resource_type, double value);
static ResourceUsageRecord* find_usage_record(ResourceMonitoringSystem* system, ResourceType type);
static const char* get_resource_type_name(ResourceType type);
static void create_resource_snapshot(ResourceMonitoringSystem* system);

/**
 * 创建资源监控系统
 */
ResourceMonitoringSystem* resource_monitoring_system_create(EventSystem* event_system) {
    if (!event_system) {
        fprintf(stderr, "错误: 创建资源监控系统时需要有效的事件系统\n");
        return NULL;
    }
    
    ResourceMonitoringSystem* system = (ResourceMonitoringSystem*)malloc(sizeof(ResourceMonitoringSystem));
    if (!system) {
        fprintf(stderr, "错误: 无法为资源监控系统分配内存\n");
        return NULL;
    }
    
    // 初始化默认配置
    system->config.update_interval_ms = 1000;  // 默认1秒
    system->config.monitoring_level = MONITORING_LEVEL_NORMAL;
    system->config.auto_snapshot = 1;
    system->config.emit_events = 1;
    
    // 初始化记录数组
    system->records_capacity = 10;  // 初始容量
    system->records_count = 0;
    system->usage_records = (ResourceUsageRecord*)malloc(
        system->records_capacity * sizeof(ResourceUsageRecord));
    if (!system->usage_records) {
        fprintf(stderr, "错误: 无法为资源使用记录分配内存\n");
        free(system);
        return NULL;
    }
    
    // 初始化阈值数组
    system->thresholds_capacity = 10;  // 初始容量
    system->thresholds_count = 0;
    system->thresholds = (ResourceThreshold*)malloc(
        system->thresholds_capacity * sizeof(ResourceThreshold));
    if (!system->thresholds) {
        fprintf(stderr, "错误: 无法为资源阈值分配内存\n");
        free(system->usage_records);
        free(system);
        return NULL;
    }
    
    // 初始化性能计数器
    system->counters_count = RESOURCE_TYPE_MAX;
    system->counters = (PerformanceCounter*)calloc(
        system->counters_count, sizeof(PerformanceCounter));
    if (!system->counters) {
        fprintf(stderr, "错误: 无法为性能计数器分配内存\n");
        free(system->thresholds);
        free(system->usage_records);
        free(system);
        return NULL;
    }
    
    // 初始化时间和状态
    system->start_time = time(NULL);
    system->last_update = system->start_time;
    system->is_active = 0;  // 默认不激活
    
    // 设置事件系统
    system->event_system = event_system;
    
    // 初始化资源类型
    for (int i = 0; i < RESOURCE_TYPE_MAX; i++) {
        ResourceUsageRecord record;
        record.type = (ResourceType)i;
        record.used_amount = 0.0;
        record.peak_amount = 0.0;
        record.timestamp = system->start_time;
        
        if (system->records_count >= system->records_capacity) {
            // 扩容
            size_t new_capacity = system->records_capacity * 2;
            ResourceUsageRecord* new_records = (ResourceUsageRecord*)realloc(
                system->usage_records, new_capacity * sizeof(ResourceUsageRecord));
            if (!new_records) {
                fprintf(stderr, "警告: 无法扩展资源记录数组\n");
                continue;
            }
            system->usage_records = new_records;
            system->records_capacity = new_capacity;
        }
        
        system->usage_records[system->records_count++] = record;
    }
    
    // 初始化最新快照
    memset(&system->latest_snapshot, 0, sizeof(ResourceStatsSnapshot));
    
    return system;
}

/**
 * 销毁资源监控系统
 */
void resource_monitoring_system_destroy(ResourceMonitoringSystem* system) {
    if (!system) return;
    
    // 停止监控
    resource_monitoring_system_stop(system);
    
    // 释放内存
    free(system->usage_records);
    free(system->thresholds);
    free(system->counters);
    free(system);
}

/**
 * 启动资源监控系统
 */
int resource_monitoring_system_start(ResourceMonitoringSystem* system) {
    if (!system) return 0;
    
    if (system->is_active) {
        return 1;  // 已经在运行中
    }
    
    system->is_active = 1;
    system->start_time = time(NULL);
    system->last_update = system->start_time;
    
    // 创建初始快照
    create_resource_snapshot(system);
    
    // 发送启动事件
    emit_resource_event(system, RESOURCE_EVENT_MONITORING_STARTED, RESOURCE_TYPE_SYSTEM, 0.0);
    
    return 1;
}

/**
 * 停止资源监控系统
 */
int resource_monitoring_system_stop(ResourceMonitoringSystem* system) {
    if (!system || !system->is_active) return 0;
    
    system->is_active = 0;
    
    // 发送停止事件
    emit_resource_event(system, RESOURCE_EVENT_MONITORING_STOPPED, RESOURCE_TYPE_SYSTEM, 0.0);
    
    return 1;
}

/**
 * 设置监控配置
 */
int resource_monitoring_system_set_config(ResourceMonitoringSystem* system, const MonitoringConfig* config) {
    if (!system || !config) return 0;
    
    system->config = *config;
    return 1;
}

/**
 * 获取监控配置
 */
int resource_monitoring_system_get_config(ResourceMonitoringSystem* system, MonitoringConfig* out_config) {
    if (!system || !out_config) return 0;
    
    *out_config = system->config;
    return 1;
}

/**
 * 更新资源使用情况
 */
int resource_monitoring_system_update(ResourceMonitoringSystem* system) {
    if (!system || !system->is_active) return 0;
    
    // 检查是否需要更新
    time_t current_time = time(NULL);
    double elapsed_ms = difftime(current_time, system->last_update) * 1000.0;
    
    if (elapsed_ms < system->config.update_interval_ms) {
        return 1;  // 还不需要更新
    }
    
    // 更新资源使用情况
    update_resource_usage(system);
    
    // 检查阈值
    check_thresholds(system);
    
    // 计算性能
    calculate_performance(system);
    
    // 更新时间戳
    system->last_update = current_time;
    
    // 自动创建快照
    if (system->config.auto_snapshot) {
        create_resource_snapshot(system);
    }
    
    return 1;
}

/**
 * 添加资源阈值
 */
int resource_monitoring_system_add_threshold(ResourceMonitoringSystem* system, ResourceType type, 
                                           double threshold, ThresholdSeverity severity,
                                           ResourceThresholdCallback callback, void* user_data) {
    if (!system) return 0;
    if (threshold < 0.0 || threshold > 1.0) {
        fprintf(stderr, "错误: 资源阈值必须在0.0到1.0之间\n");
        return 0;
    }
    
    // 检查是否需要扩容
    if (system->thresholds_count >= system->thresholds_capacity) {
        size_t new_capacity = system->thresholds_capacity * 2;
        ResourceThreshold* new_thresholds = (ResourceThreshold*)realloc(
            system->thresholds, new_capacity * sizeof(ResourceThreshold));
        if (!new_thresholds) {
            fprintf(stderr, "错误: 无法扩展阈值数组\n");
            return 0;
        }
        system->thresholds = new_thresholds;
        system->thresholds_capacity = new_capacity;
    }
    
    // 添加新阈值
    ResourceThreshold threshold_item;
    threshold_item.type = type;
    threshold_item.threshold = threshold;
    threshold_item.severity = severity;
    threshold_item.callback = callback;
    threshold_item.user_data = user_data;
    threshold_item.is_active = 1;
    
    system->thresholds[system->thresholds_count++] = threshold_item;
    
    return 1;
}

/**
 * 移除资源阈值
 */
int resource_monitoring_system_remove_threshold(ResourceMonitoringSystem* system, ResourceType type, double threshold) {
    if (!system) return 0;
    
    for (size_t i = 0; i < system->thresholds_count; i++) {
        if (system->thresholds[i].type == type && 
            fabs(system->thresholds[i].threshold - threshold) < 0.0001) {
            
            // 移除阈值（通过将最后一个移动到当前位置）
            if (i < system->thresholds_count - 1) {
                system->thresholds[i] = system->thresholds[system->thresholds_count - 1];
            }
            system->thresholds_count--;
            
            return 1;
        }
    }
    
    return 0;  // 未找到匹配的阈值
}

/**
 * 记录资源操作
 */
int resource_monitoring_system_record_operation(ResourceMonitoringSystem* system, ResourceType type, double amount) {
    if (!system || !system->is_active) return 0;
    
    // 查找资源类型对应的性能计数器
    if (type < RESOURCE_TYPE_MAX) {
        system->counters[type].operations_count++;
    }
    
    // 记录资源使用量
    ResourceUsageRecord* record = find_usage_record(system, type);
    if (record) {
        record->used_amount += amount;
        record->timestamp = time(NULL);
        
        // 更新峰值
        if (record->used_amount > record->peak_amount) {
            record->peak_amount = record->used_amount;
        }
    }
    
    return 1;
}

/**
 * 创建资源统计快照
 */
int resource_monitoring_system_create_snapshot(ResourceMonitoringSystem* system, ResourceStatsSnapshot* out_snapshot) {
    if (!system || !out_snapshot) return 0;
    
    // 更新使用情况
    update_resource_usage(system);
    
    // 填充快照
    out_snapshot->timestamp = time(NULL);
    out_snapshot->uptime_seconds = difftime(out_snapshot->timestamp, system->start_time);
    
    // 复制资源使用情况
    for (size_t i = 0; i < system->records_count && i < MAX_RESOURCE_TYPES; i++) {
        ResourceUsageRecord* record = &system->usage_records[i];
        out_snapshot->resources[i].type = record->type;
        out_snapshot->resources[i].usage_percentage = record->used_amount;
        out_snapshot->resources[i].peak_usage_percentage = record->peak_amount;
    }
    out_snapshot->resources_count = system->records_count > MAX_RESOURCE_TYPES ? 
                                   MAX_RESOURCE_TYPES : system->records_count;
    
    // 复制性能计数器
    for (size_t i = 0; i < system->counters_count && i < MAX_RESOURCE_TYPES; i++) {
        out_snapshot->performance[i].type = (ResourceType)i;
        out_snapshot->performance[i].operations_count = system->counters[i].operations_count;
        out_snapshot->performance[i].operations_per_second = system->counters[i].operation_rate;
    }
    out_snapshot->performance_count = system->counters_count > MAX_RESOURCE_TYPES ? 
                                     MAX_RESOURCE_TYPES : system->counters_count;
    
    return 1;
}

/**
 * 获取最新的资源统计快照
 */
const ResourceStatsSnapshot* resource_monitoring_system_get_latest_snapshot(ResourceMonitoringSystem* system) {
    if (!system) return NULL;
    
    // 如果自动快照关闭，手动创建快照
    if (!system->config.auto_snapshot) {
        create_resource_snapshot(system);
    }
    
    return &system->latest_snapshot;
}

/**
 * 打印资源使用情况
 */
void resource_monitoring_system_print_stats(ResourceMonitoringSystem* system) {
    if (!system) return;
    
    ResourceStatsSnapshot snapshot;
    if (!resource_monitoring_system_create_snapshot(system, &snapshot)) {
        printf("无法创建资源统计快照\n");
        return;
    }
    
    printf("\n========== QEntL资源监控统计 ==========\n");
    printf("监控开始时间: %s", ctime(&system->start_time));
    printf("运行时间: %.2f秒\n", snapshot.uptime_seconds);
    printf("\n--- 资源使用情况 ---\n");
    
    for (size_t i = 0; i < snapshot.resources_count; i++) {
        ResourceStats* stats = &snapshot.resources[i];
        printf("%-20s: 当前: %.2f%%, 峰值: %.2f%%\n", 
               get_resource_type_name(stats->type),
               stats->usage_percentage * 100.0,
               stats->peak_usage_percentage * 100.0);
    }
    
    printf("\n--- 性能统计 ---\n");
    for (size_t i = 0; i < snapshot.performance_count; i++) {
        PerformanceStats* perf = &snapshot.performance[i];
        if (perf->operations_count > 0) {
            printf("%-20s: 总操作数: %lu, 速率: %.2f ops/sec\n", 
                   get_resource_type_name(perf->type),
                   perf->operations_count,
                   perf->operations_per_second);
        }
    }
    
    printf("=======================================\n\n");
}

// --- 内部函数实现 ---

/**
 * 更新资源使用情况
 */
static void update_resource_usage(ResourceMonitoringSystem* system) {
    if (!system) return;
    
    // 这里应该调用设备能力检测器获取当前资源使用情况
    // 以下是模拟实现，实际应用中需要根据实际设备状态来更新
    
    // 更新CPU使用率
    ResourceUsageRecord* cpu_record = find_usage_record(system, RESOURCE_TYPE_CPU);
    if (cpu_record) {
        // 模拟CPU使用率波动
        double current_cpu = cpu_record->used_amount;
        double random_change = ((double)rand() / RAND_MAX - 0.5) * 0.1; // -5% 到 +5%
        current_cpu += random_change;
        
        // 限制在合理范围内
        if (current_cpu < 0.05) current_cpu = 0.05;
        if (current_cpu > 0.95) current_cpu = 0.95;
        
        cpu_record->used_amount = current_cpu;
        cpu_record->timestamp = time(NULL);
        
        // 更新峰值
        if (current_cpu > cpu_record->peak_amount) {
            cpu_record->peak_amount = current_cpu;
        }
        
        // 如果配置为高级监控，发送资源变化事件
        if (system->config.monitoring_level >= MONITORING_LEVEL_DETAILED && system->config.emit_events) {
            emit_resource_event(system, RESOURCE_EVENT_USAGE_CHANGED, RESOURCE_TYPE_CPU, current_cpu);
        }
    }
    
    // 更新内存使用率
    ResourceUsageRecord* memory_record = find_usage_record(system, RESOURCE_TYPE_MEMORY);
    if (memory_record) {
        // 模拟内存使用率变化
        double current_memory = memory_record->used_amount;
        double random_change = ((double)rand() / RAND_MAX - 0.5) * 0.05; // -2.5% 到 +2.5%
        current_memory += random_change;
        
        // 限制在合理范围内
        if (current_memory < 0.1) current_memory = 0.1;
        if (current_memory > 0.9) current_memory = 0.9;
        
        memory_record->used_amount = current_memory;
        memory_record->timestamp = time(NULL);
        
        // 更新峰值
        if (current_memory > memory_record->peak_amount) {
            memory_record->peak_amount = current_memory;
        }
        
        // 如果配置为高级监控，发送资源变化事件
        if (system->config.monitoring_level >= MONITORING_LEVEL_DETAILED && system->config.emit_events) {
            emit_resource_event(system, RESOURCE_EVENT_USAGE_CHANGED, RESOURCE_TYPE_MEMORY, current_memory);
        }
    }
    
    // 更新量子比特使用率
    ResourceUsageRecord* qbit_record = find_usage_record(system, RESOURCE_TYPE_QUANTUM_BITS);
    if (qbit_record) {
        // 模拟量子比特使用率变化
        double current_qbits = qbit_record->used_amount;
        double random_change = ((double)rand() / RAND_MAX - 0.5) * 0.08; // -4% 到 +4%
        current_qbits += random_change;
        
        // 限制在合理范围内
        if (current_qbits < 0.0) current_qbits = 0.0;
        if (current_qbits > 0.8) current_qbits = 0.8;
        
        qbit_record->used_amount = current_qbits;
        qbit_record->timestamp = time(NULL);
        
        // 更新峰值
        if (current_qbits > qbit_record->peak_amount) {
            qbit_record->peak_amount = current_qbits;
        }
        
        // 如果配置为高级监控，发送资源变化事件
        if (system->config.monitoring_level >= MONITORING_LEVEL_DETAILED && system->config.emit_events) {
            emit_resource_event(system, RESOURCE_EVENT_USAGE_CHANGED, RESOURCE_TYPE_QUANTUM_BITS, current_qbits);
        }
    }
    
    // 其他资源类型的更新可以按照类似方式实现
}

/**
 * 检查阈值
 */
static void check_thresholds(ResourceMonitoringSystem* system) {
    if (!system) return;
    
    for (size_t i = 0; i < system->thresholds_count; i++) {
        ResourceThreshold* threshold = &system->thresholds[i];
        
        if (!threshold->is_active) continue;
        
        ResourceUsageRecord* record = find_usage_record(system, threshold->type);
        if (!record) continue;
        
        double usage = record->used_amount;
        
        // 检查是否超过阈值
        if (usage >= threshold->threshold) {
            // 发送阈值事件
            if (system->config.emit_events) {
                emit_resource_event(system, RESOURCE_EVENT_THRESHOLD_EXCEEDED, 
                                   threshold->type, usage);
            }
            
            // 调用回调函数
            if (threshold->callback) {
                threshold->callback(system, threshold->type, usage, 
                                   threshold->threshold, threshold->severity,
                                   threshold->user_data);
            }
        }
    }
}

/**
 * 计算性能
 */
static void calculate_performance(ResourceMonitoringSystem* system) {
    if (!system) return;
    
    time_t current_time = time(NULL);
    double elapsed_seconds = difftime(current_time, system->last_update);
    
    if (elapsed_seconds <= 0.0) return;
    
    // 计算每种资源的操作速率
    for (size_t i = 0; i < system->counters_count; i++) {
        PerformanceCounter* counter = &system->counters[i];
        
        // 计算速率 (每秒操作数)
        counter->operation_rate = counter->operations_count / elapsed_seconds;
        
        // 如果监控级别为详细，则发送性能事件
        if (system->config.monitoring_level >= MONITORING_LEVEL_DETAILED && 
            system->config.emit_events && counter->operations_count > 0) {
            
            emit_resource_event(system, RESOURCE_EVENT_PERFORMANCE_MEASURED, 
                               (ResourceType)i, counter->operation_rate);
        }
    }
}

/**
 * 发送资源事件
 */
static void emit_resource_event(ResourceMonitoringSystem* system, ResourceEventType event_type, 
                               ResourceType resource_type, double value) {
    if (!system || !system->event_system || !system->config.emit_events) return;
    
    // 创建事件数据
    ResourceEventData event_data;
    event_data.event_type = event_type;
    event_data.resource_type = resource_type;
    event_data.value = value;
    event_data.timestamp = time(NULL);
    
    // 获取资源类型名称
    const char* resource_name = get_resource_type_name(resource_type);
    
    // 创建事件
    QEntLEvent* event = event_create(EVENT_TYPE_RESOURCE, EVENT_FLAG_NONE);
    if (!event) {
        fprintf(stderr, "错误: 无法创建资源事件\n");
        return;
    }
    
    // 设置事件数据
    event->data = malloc(sizeof(ResourceEventData));
    if (!event->data) {
        fprintf(stderr, "错误: 无法为事件数据分配内存\n");
        event_destroy(event);
        return;
    }
    
    memcpy(event->data, &event_data, sizeof(ResourceEventData));
    
    // 设置事件描述
    char description[256];
    switch (event_type) {
        case RESOURCE_EVENT_MONITORING_STARTED:
            snprintf(description, sizeof(description), "资源监控已启动");
            break;
        case RESOURCE_EVENT_MONITORING_STOPPED:
            snprintf(description, sizeof(description), "资源监控已停止");
            break;
        case RESOURCE_EVENT_USAGE_CHANGED:
            snprintf(description, sizeof(description), "%s使用率变为%.2f%%", 
                    resource_name, value * 100.0);
            break;
        case RESOURCE_EVENT_THRESHOLD_EXCEEDED:
            snprintf(description, sizeof(description), "%s超过阈值: %.2f%%", 
                    resource_name, value * 100.0);
            break;
        case RESOURCE_EVENT_PERFORMANCE_MEASURED:
            snprintf(description, sizeof(description), "%s性能: %.2f ops/sec", 
                    resource_name, value);
            break;
        default:
            snprintf(description, sizeof(description), "资源事件: %s, 值: %.2f", 
                    resource_name, value);
            break;
    }
    
    event->description = strdup(description);
    
    // 发送事件
    event_emit(system->event_system, event);
}

/**
 * 查找资源使用记录
 */
static ResourceUsageRecord* find_usage_record(ResourceMonitoringSystem* system, ResourceType type) {
    if (!system) return NULL;
    
    for (size_t i = 0; i < system->records_count; i++) {
        if (system->usage_records[i].type == type) {
            return &system->usage_records[i];
        }
    }
    
    return NULL;
}

/**
 * 获取资源类型名称
 */
static const char* get_resource_type_name(ResourceType type) {
    switch (type) {
        case RESOURCE_TYPE_CPU: return "CPU";
        case RESOURCE_TYPE_MEMORY: return "内存";
        case RESOURCE_TYPE_STORAGE: return "存储";
        case RESOURCE_TYPE_NETWORK: return "网络";
        case RESOURCE_TYPE_QUANTUM_BITS: return "量子比特";
        case RESOURCE_TYPE_QUANTUM_GATES: return "量子门";
        case RESOURCE_TYPE_ENERGY: return "能源";
        case RESOURCE_TYPE_COOLING: return "冷却";
        case RESOURCE_TYPE_SYSTEM: return "系统";
        default: return "未知资源";
    }
}

/**
 * 创建资源快照
 */
static void create_resource_snapshot(ResourceMonitoringSystem* system) {
    if (!system) return;
    
    resource_monitoring_system_create_snapshot(system, &system->latest_snapshot);
}

/**
 * 运行资源监控系统测试
 */
int resource_monitoring_system_run_test(void) {
    printf("开始资源监控系统测试...\n");
    
    // 创建事件系统
    EventSystem* event_system = event_system_create();
    if (!event_system) {
        fprintf(stderr, "错误: 无法创建事件系统\n");
        return 0;
    }
    
    // 创建资源监控系统
    ResourceMonitoringSystem* system = resource_monitoring_system_create(event_system);
    if (!system) {
        fprintf(stderr, "错误: 无法创建资源监控系统\n");
        event_system_destroy(event_system);
        return 0;
    }
    
    // 设置配置
    MonitoringConfig config;
    config.update_interval_ms = 500;  // 0.5秒
    config.monitoring_level = MONITORING_LEVEL_DETAILED;
    config.auto_snapshot = 1;
    config.emit_events = 1;
    resource_monitoring_system_set_config(system, &config);
    
    // 添加阈值回调
    resource_monitoring_system_add_threshold(system, RESOURCE_TYPE_CPU, 0.8, THRESHOLD_SEVERITY_WARNING, 
        NULL, NULL);
    resource_monitoring_system_add_threshold(system, RESOURCE_TYPE_MEMORY, 0.9, THRESHOLD_SEVERITY_CRITICAL, 
        NULL, NULL);
    
    // 启动监控
    resource_monitoring_system_start(system);
    
    // 模拟资源操作
    for (int i = 0; i < 10; i++) {
        // 模拟CPU操作
        resource_monitoring_system_record_operation(system, RESOURCE_TYPE_CPU, 0.05);
        
        // 模拟内存操作
        resource_monitoring_system_record_operation(system, RESOURCE_TYPE_MEMORY, 0.03);
        
        // 模拟量子比特操作
        resource_monitoring_system_record_operation(system, RESOURCE_TYPE_QUANTUM_BITS, 0.1);
        
        // 更新资源使用情况
        resource_monitoring_system_update(system);
        
        // 打印统计信息
        if (i % 3 == 0) {
            resource_monitoring_system_print_stats(system);
        }
        
        // 休眠一段时间
        #ifdef _WIN32
        Sleep(1000);  // Windows
        #else
        sleep(1);     // UNIX
        #endif
    }
    
    // 停止监控
    resource_monitoring_system_stop(system);
    
    // 销毁资源
    resource_monitoring_system_destroy(system);
    event_system_destroy(event_system);
    
    printf("资源监控系统测试完成\n");
    return 1;
} 