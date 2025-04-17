/**
 * QEntL量子网络节点状态监控系统实现
 * 
 * 量子基因编码: QG-RUNTIME-NODEMON-SRC-G4M7-1713051600
 * 
 * @文件: node_status_monitor.c
 * @描述: 实现QEntL运行时的量子网络节点状态监控系统
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-18
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，负责监控量子网络中节点的状态
 * - 支持节点健康监测、异常预警、性能分析和状态报告
 * - 能够与网络连接管理器协同工作，实现网络自愈和优化
 */

#include "node_status_monitor.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

/**
 * 节点监控条目结构
 */
typedef struct MonitoredNode {
    QNetworkNode* node;                /* 节点指针 */
    NodeHealthStatus current_status;   /* 当前状态 */
    NodeHealthStatus previous_status;  /* 上一个状态 */
    NodeHealthMetrics metrics;         /* 健康指标 */
    time_t last_check_time;            /* 上次检查时间 */
    time_t last_status_change;         /* 上次状态改变时间 */
    int alert_count;                   /* 警报计数 */
    int recovery_attempts;             /* 恢复尝试次数 */
    void* node_data;                   /* 节点数据 */
} MonitoredNode;

/**
 * 节点状态警报结构
 */
typedef struct StatusAlert {
    QNetworkNode* node;                /* 节点指针 */
    NodeHealthStatus status;           /* 触发状态 */
    char* message;                     /* 警报消息 */
    time_t timestamp;                  /* 时间戳 */
    int severity;                      /* 严重程度 */
} StatusAlert;

/**
 * 回调条目结构
 */
typedef struct CallbackEntry {
    NodeStatusCallback callback;       /* 回调函数 */
    void* user_data;                   /* 用户数据 */
} CallbackEntry;

/**
 * 节点状态监控系统内部结构
 */
struct NodeStatusMonitor {
    NetworkConnectionManager* connection_manager;  /* 连接管理器 */
    EventSystem* event_system;                    /* 事件系统 */
    EventHandler* event_handler;                  /* 事件处理器 */
    
    NodeStatusConfig config;                      /* 监控配置 */
    
    MonitoredNode** monitored_nodes;              /* 监控节点数组 */
    int node_count;                               /* 节点数量 */
    int node_capacity;                            /* 节点容量 */
    
    StatusAlert** alerts;                         /* 警报数组 */
    int alert_count;                              /* 警报数量 */
    int alert_capacity;                           /* 警报容量 */
    
    CallbackEntry* callbacks;                     /* 回调数组 */
    int callback_count;                           /* 回调数量 */
    int callback_capacity;                        /* 回调容量 */
    
    int is_monitoring;                            /* 是否正在监控 */
    time_t last_monitor_time;                     /* 上次监控时间 */
    time_t last_report_time;                      /* 上次报告时间 */
    
    /* 健康统计 */
    int total_nodes;                              /* 总节点数 */
    int normal_nodes;                             /* 正常节点数 */
    int warning_nodes;                            /* 警告节点数 */
    int critical_nodes;                           /* 危急节点数 */
    int offline_nodes;                            /* 离线节点数 */
};

/* 内部函数声明 */
static NodeStatusConfig create_default_config(void);
static MonitoredNode* find_monitored_node(NodeStatusMonitor* monitor, QNetworkNode* node);
static NodeHealthMetrics calculate_node_metrics(NodeStatusMonitor* monitor, QNetworkNode* node);
static NodeHealthStatus determine_node_health(NodeStatusMonitor* monitor, NodeHealthMetrics metrics);
static void update_node_status(NodeStatusMonitor* monitor, MonitoredNode* monitored);
static void execute_callbacks(NodeStatusMonitor* monitor, QNetworkNode* node, NodeHealthStatus status, NodeStatusReport* report);
static void on_node_event(QEntLEvent* event, NodeStatusMonitor* monitor);
static void update_health_stats(NodeStatusMonitor* monitor);
static void add_status_alert(NodeStatusMonitor* monitor, QNetworkNode* node, NodeHealthStatus status, const char* message, int severity);
static StatusAlert* create_status_alert(QNetworkNode* node, NodeHealthStatus status, const char* message, int severity);
static void free_status_alert(StatusAlert* alert);

/**
 * 创建默认配置
 */
static NodeStatusConfig create_default_config(void) {
    NodeStatusConfig config;
    
    config.auto_monitor = 1;
    config.monitor_interval = 30;  /* 30秒 */
    config.level = MONITOR_LEVEL_STANDARD;
    
    config.warning_threshold = 0.7;
    config.critical_threshold = 0.4;
    
    config.enable_alerts = 1;
    config.alert_history_size = 100;
    
    config.enable_auto_recovery = 1;
    config.enable_logging = 1;
    
    config.enable_periodic_report = 1;
    config.report_interval = 300;  /* 5分钟 */
    
    config.custom_config = NULL;
    
    return config;
}

/**
 * 创建节点状态监控系统
 */
NodeStatusMonitor* node_status_monitor_create(
    NetworkConnectionManager* connection_manager, 
    EventSystem* event_system) {
    
    if (!connection_manager || !event_system) {
        fprintf(stderr, "错误: 创建节点状态监控系统需要有效的连接管理器和事件系统\n");
        return NULL;
    }
    
    NodeStatusMonitor* monitor = (NodeStatusMonitor*)malloc(sizeof(NodeStatusMonitor));
    if (!monitor) {
        fprintf(stderr, "错误: 无法分配节点状态监控系统内存\n");
        return NULL;
    }
    
    /* 初始化基本字段 */
    monitor->connection_manager = connection_manager;
    monitor->event_system = event_system;
    monitor->is_monitoring = 0;
    monitor->last_monitor_time = time(NULL);
    monitor->last_report_time = time(NULL);
    
    /* 初始化监控节点数组 */
    monitor->node_capacity = 16;
    monitor->monitored_nodes = (MonitoredNode**)malloc(
        monitor->node_capacity * sizeof(MonitoredNode*));
    if (!monitor->monitored_nodes) {
        free(monitor);
        fprintf(stderr, "错误: 无法分配监控节点数组内存\n");
        return NULL;
    }
    monitor->node_count = 0;
    
    /* 初始化警报数组 */
    monitor->alert_capacity = 16;
    monitor->alerts = (StatusAlert**)malloc(
        monitor->alert_capacity * sizeof(StatusAlert*));
    if (!monitor->alerts) {
        free(monitor->monitored_nodes);
        free(monitor);
        fprintf(stderr, "错误: 无法分配警报数组内存\n");
        return NULL;
    }
    monitor->alert_count = 0;
    
    /* 初始化回调数组 */
    monitor->callback_capacity = 4;
    monitor->callbacks = (CallbackEntry*)malloc(
        monitor->callback_capacity * sizeof(CallbackEntry));
    if (!monitor->callbacks) {
        free(monitor->alerts);
        free(monitor->monitored_nodes);
        free(monitor);
        fprintf(stderr, "错误: 无法分配回调数组内存\n");
        return NULL;
    }
    monitor->callback_count = 0;
    
    /* 设置默认配置 */
    monitor->config = create_default_config();
    
    /* 初始化健康统计 */
    monitor->total_nodes = 0;
    monitor->normal_nodes = 0;
    monitor->warning_nodes = 0;
    monitor->critical_nodes = 0;
    monitor->offline_nodes = 0;
    
    /* 注册事件处理器 */
    monitor->event_handler = event_system_add_handler(event_system, 
                                                   node_status_monitor_event_handler, 
                                                   monitor, 
                                                   10, /* 优先级 */
                                                   (1 << EVENT_NODE_ACTIVATED) |
                                                   (1 << EVENT_NODE_DEACTIVATED) |
                                                   (1 << EVENT_NODE_DEGRADED) |
                                                   (1 << EVENT_NODE_RECOVERED));
    
    printf("量子网络节点状态监控系统已创建\n");
    
    /* 如果配置为自动监控，立即启动 */
    if (monitor->config.auto_monitor) {
        node_status_monitor_start(monitor);
    }
    
    return monitor;
}

/**
 * 销毁节点状态监控系统
 */
void node_status_monitor_destroy(NodeStatusMonitor* monitor) {
    if (!monitor) return;
    
    /* 停止监控 */
    if (monitor->is_monitoring) {
        node_status_monitor_stop(monitor);
    }
    
    /* 移除事件处理器 */
    if (monitor->event_system && monitor->event_handler) {
        event_system_remove_handler(monitor->event_system, monitor->event_handler);
    }
    
    /* 释放所有警报 */
    for (int i = 0; i < monitor->alert_count; i++) {
        free_status_alert(monitor->alerts[i]);
    }
    
    /* 释放所有监控节点 */
    for (int i = 0; i < monitor->node_count; i++) {
        free(monitor->monitored_nodes[i]);
    }
    
    /* 释放数组 */
    free(monitor->callbacks);
    free(monitor->alerts);
    free(monitor->monitored_nodes);
    
    /* 释放监控系统本身 */
    free(monitor);
    
    printf("量子网络节点状态监控系统已销毁\n");
}

/**
 * 设置监控配置
 */
int node_status_monitor_set_config(NodeStatusMonitor* monitor, 
                                 NodeStatusConfig config) {
    if (!monitor) return 0;
    
    monitor->config = config;
    return 1;
}

/**
 * 获取监控配置
 */
NodeStatusConfig node_status_monitor_get_config(NodeStatusMonitor* monitor) {
    NodeStatusConfig empty_config = {0};
    
    if (!monitor) return empty_config;
    
    return monitor->config;
}

/**
 * 添加节点到监控列表
 */
int node_status_monitor_add_node(NodeStatusMonitor* monitor, 
                               QNetworkNode* node) {
    if (!monitor || !node) {
        fprintf(stderr, "错误: 无效的参数\n");
        return 0;
    }
    
    /* 检查节点是否已存在 */
    if (find_monitored_node(monitor, node)) {
        printf("警告: 节点已在监控列表中\n");
        return 1;  /* 节点已存在视为成功 */
    }
    
    /* 检查是否需要扩展节点数组 */
    if (monitor->node_count >= monitor->node_capacity) {
        int new_capacity = monitor->node_capacity * 2;
        MonitoredNode** new_nodes = (MonitoredNode**)realloc(
            monitor->monitored_nodes, 
            new_capacity * sizeof(MonitoredNode*));
        
        if (!new_nodes) {
            fprintf(stderr, "错误: 无法扩展节点数组\n");
            return 0;
        }
        
        monitor->monitored_nodes = new_nodes;
        monitor->node_capacity = new_capacity;
    }
    
    /* 创建新监控节点 */
    MonitoredNode* monitored = (MonitoredNode*)malloc(sizeof(MonitoredNode));
    if (!monitored) {
        fprintf(stderr, "错误: 无法分配监控节点内存\n");
        return 0;
    }
    
    /* 初始化监控节点 */
    monitored->node = node;
    monitored->current_status = NODE_HEALTH_UNKNOWN;
    monitored->previous_status = NODE_HEALTH_UNKNOWN;
    memset(&monitored->metrics, 0, sizeof(NodeHealthMetrics));
    monitored->last_check_time = time(NULL);
    monitored->last_status_change = monitored->last_check_time;
    monitored->alert_count = 0;
    monitored->recovery_attempts = 0;
    monitored->node_data = NULL;
    
    /* 添加到监控节点数组 */
    monitor->monitored_nodes[monitor->node_count++] = monitored;
    
    /* 初始化节点指标和状态 */
    monitored->metrics = calculate_node_metrics(monitor, node);
    monitored->current_status = determine_node_health(monitor, monitored->metrics);
    
    /* 更新健康统计 */
    monitor->total_nodes++;
    update_health_stats(monitor);
    
    printf("节点已添加到监控列表: %p\n", (void*)node);
    
    return 1;
}

/**
 * 从监控列表移除节点
 */
int node_status_monitor_remove_node(NodeStatusMonitor* monitor, 
                                  QNetworkNode* node) {
    if (!monitor || !node) {
        return 0;
    }
    
    /* 查找监控节点 */
    MonitoredNode* monitored = NULL;
    int found_index = -1;
    
    for (int i = 0; i < monitor->node_count; i++) {
        if (monitor->monitored_nodes[i]->node == node) {
            monitored = monitor->monitored_nodes[i];
            found_index = i;
            break;
        }
    }
    
    if (!monitored || found_index < 0) {
        fprintf(stderr, "错误: 节点不在监控列表中\n");
        return 0;
    }
    
    /* 移除并释放监控节点 */
    free(monitored);
    
    /* 移动数组中的元素以填补空缺 */
    for (int i = found_index; i < monitor->node_count - 1; i++) {
        monitor->monitored_nodes[i] = monitor->monitored_nodes[i + 1];
    }
    
    monitor->node_count--;
    
    /* 更新健康统计 */
    monitor->total_nodes--;
    update_health_stats(monitor);
    
    printf("节点已从监控列表移除: %p\n", (void*)node);
    
    return 1;
}

/**
 * 查找监控节点
 */
static MonitoredNode* find_monitored_node(NodeStatusMonitor* monitor, QNetworkNode* node) {
    if (!monitor || !node) {
        return NULL;
    }
    
    for (int i = 0; i < monitor->node_count; i++) {
        if (monitor->monitored_nodes[i]->node == node) {
            return monitor->monitored_nodes[i];
        }
    }
    
    return NULL;
}

/**
 * 释放状态警报
 */
static void free_status_alert(StatusAlert* alert) {
    if (!alert) return;
    
    if (alert->message) {
        free(alert->message);
    }
    
    free(alert);
}

/**
 * 启动监控
 */
int node_status_monitor_start(NodeStatusMonitor* monitor) {
    if (!monitor) return 0;
    
    if (monitor->is_monitoring) {
        printf("警告: 节点状态监控系统已在运行\n");
        return 1;
    }
    
    monitor->is_monitoring = 1;
    monitor->last_monitor_time = time(NULL);
    
    printf("节点状态监控系统已启动\n");
    
    /* 启动后立即执行一次状态更新 */
    node_status_monitor_update(monitor);
    
    return 1;
}

/**
 * 停止监控
 */
int node_status_monitor_stop(NodeStatusMonitor* monitor) {
    if (!monitor) return 0;
    
    if (!monitor->is_monitoring) {
        printf("警告: 节点状态监控系统已停止\n");
        return 1;
    }
    
    monitor->is_monitoring = 0;
    
    printf("节点状态监控系统已停止\n");
    
    return 1;
}

/**
 * 更新所有节点状态
 */
int node_status_monitor_update(NodeStatusMonitor* monitor) {
    if (!monitor) return 0;
    
    if (!monitor->is_monitoring) {
        printf("警告: 监控未启动，无法更新节点状态\n");
        return 0;
    }
    
    time_t current_time = time(NULL);
    
    /* 检查是否需要更新 */
    if (difftime(current_time, monitor->last_monitor_time) < monitor->config.monitor_interval) {
        return 1;  /* 还未到更新时间 */
    }
    
    printf("更新节点状态 (总计 %d 个节点)...\n", monitor->node_count);
    
    /* 遍历所有监控节点并更新状态 */
    for (int i = 0; i < monitor->node_count; i++) {
        MonitoredNode* monitored = monitor->monitored_nodes[i];
        
        /* 保存上一个状态 */
        monitored->previous_status = monitored->current_status;
        
        /* 计算新指标 */
        monitored->metrics = calculate_node_metrics(monitor, monitored->node);
        
        /* 基于新指标确定健康状态 */
        NodeHealthStatus new_status = determine_node_health(monitor, monitored->metrics);
        
        /* 如果状态改变，更新状态和时间戳 */
        if (new_status != monitored->current_status) {
            monitored->current_status = new_status;
            monitored->last_status_change = current_time;
            
            /* 处理状态变化逻辑 */
            update_node_status(monitor, monitored);
        }
        
        monitored->last_check_time = current_time;
    }
    
    /* 更新健康统计 */
    update_health_stats(monitor);
    
    /* 更新监控时间 */
    monitor->last_monitor_time = current_time;
    
    /* 检查是否需要生成周期性报告 */
    if (monitor->config.enable_periodic_report &&
        difftime(current_time, monitor->last_report_time) >= monitor->config.report_interval) {
        
        /* 生成并发送报告 */
        NodeStatusReport* report = node_status_monitor_generate_report(monitor);
        if (report) {
            /* 执行所有回调 */
            for (int i = 0; i < monitor->callback_count; i++) {
                if (monitor->callbacks[i].callback) {
                    monitor->callbacks[i].callback(NULL, NODE_HEALTH_UNKNOWN, report, monitor->callbacks[i].user_data);
                }
            }
            
            /* 发送报告事件 */
            if (monitor->event_system) {
                QEntLEvent* event = event_system_create_event(monitor->event_system, 
                                                         EVENT_NETWORK_REPORT, 
                                                         report, 
                                                         sizeof(NodeStatusReport));
                if (event) {
                    event_system_emit_event(monitor->event_system, event);
                }
            }
            
            /* 释放报告 */
            free(report);
        }
        
        monitor->last_report_time = current_time;
    }
    
    return 1;
}

/**
 * 计算节点健康指标
 */
static NodeHealthMetrics calculate_node_metrics(NodeStatusMonitor* monitor, QNetworkNode* node) {
    NodeHealthMetrics metrics = {0};
    
    /* 初始化默认值 */
    metrics.health_score = 1.0;  /* 默认为满分 */
    metrics.availability = 1.0;
    metrics.response_time = 0.0;  /* 默认响应时间为0 */
    metrics.error_rate = 0.0;     /* 默认无错误 */
    metrics.connection_stability = 1.0;
    metrics.quantum_coherence = 1.0;
    metrics.entanglement_fidelity = 1.0;
    
    /* 如果节点为NULL，返回离线指标 */
    if (!node) {
        metrics.health_score = 0.0;
        metrics.availability = 0.0;
        metrics.connection_stability = 0.0;
        return metrics;
    }
    
    /* 使用连接管理器检查节点连接状态 */
    if (monitor->connection_manager) {
        /* 检查节点是否有活跃连接 */
        int is_connected = network_connection_manager_is_node_connected(
            monitor->connection_manager, node);
        
        if (!is_connected) {
            metrics.availability = 0.0;
            metrics.health_score *= 0.5;  /* 降低健康分数 */
        }
        
        /* 获取连接稳定性评分 */
        metrics.connection_stability = network_connection_manager_get_connection_stability(
            monitor->connection_manager, node);
        
        /* 获取错误率 */
        metrics.error_rate = network_connection_manager_get_error_rate(
            monitor->connection_manager, node);
    }
    
    /* 尝试从节点获取量子相干性和纠缠保真度 */
    if (node->get_quantum_metrics) {
        double coherence = 0.0, fidelity = 0.0;
        if (node->get_quantum_metrics(node, &coherence, &fidelity) == 1) {
            metrics.quantum_coherence = coherence;
            metrics.entanglement_fidelity = fidelity;
        }
    }
    
    /* 检查响应时间 */
    if (node->ping) {
        metrics.response_time = node->ping(node);
    }
    
    /* 根据配置的监控级别调整计算深度 */
    if (monitor->config.level >= MONITOR_LEVEL_COMPREHENSIVE) {
        /* 更复杂的评估逻辑，包括资源使用率、吞吐量等 */
        if (node->get_load) {
            double load = node->get_load(node);
            if (load > 0.9) {  /* 负载过高 */
                metrics.health_score *= 0.8;
            }
        }
    }
    
    /* 计算最终健康分数 */
    metrics.health_score = metrics.availability * 0.3 +
                          (1.0 - metrics.error_rate) * 0.2 +
                          metrics.connection_stability * 0.2 +
                          metrics.quantum_coherence * 0.15 +
                          metrics.entanglement_fidelity * 0.15;
    
    /* 确保健康分数在0-1范围内 */
    if (metrics.health_score < 0.0) metrics.health_score = 0.0;
    if (metrics.health_score > 1.0) metrics.health_score = 1.0;
    
    return metrics;
}

/**
 * 确定节点健康状态
 */
static NodeHealthStatus determine_node_health(NodeStatusMonitor* monitor, NodeHealthMetrics metrics) {
    /* 如果可用性为0，节点离线 */
    if (metrics.availability <= 0.001) {
        return NODE_HEALTH_OFFLINE;
    }
    
    /* 根据健康分数确定状态 */
    if (metrics.health_score >= monitor->config.warning_threshold) {
        return NODE_HEALTH_NORMAL;
    } else if (metrics.health_score >= monitor->config.critical_threshold) {
        return NODE_HEALTH_WARNING;
    } else {
        return NODE_HEALTH_CRITICAL;
    }
}

/**
 * 处理节点状态更新
 */
static void update_node_status(NodeStatusMonitor* monitor, MonitoredNode* monitored) {
    if (!monitor || !monitored) return;
    
    QNetworkNode* node = monitored->node;
    NodeHealthStatus old_status = monitored->previous_status;
    NodeHealthStatus new_status = monitored->current_status;
    
    /* 如果状态相同，不需要处理 */
    if (old_status == new_status) return;
    
    printf("节点 %p 状态变化: %d -> %d\n", (void*)node, old_status, new_status);
    
    /* 生成节点状态报告 */
    NodeStatusReport report;
    memset(&report, 0, sizeof(NodeStatusReport));
    
    report.node = node;
    report.timestamp = time(NULL);
    report.previous_status = old_status;
    report.current_status = new_status;
    report.metrics = monitored->metrics;
    report.since_last_change = difftime(report.timestamp, monitored->last_status_change);
    
    /* 如果状态恶化，增加警报计数并可能触发警报 */
    if (new_status > old_status) {  /* 数值更大表示状态更差 */
        monitored->alert_count++;
        
        /* 根据配置决定是否触发警报 */
        if (monitor->config.enable_alerts) {
            char message[256];
            int severity = 0;
            
            switch (new_status) {
                case NODE_HEALTH_WARNING:
                    snprintf(message, sizeof(message), 
                            "节点进入警告状态，健康分数: %.2f", monitored->metrics.health_score);
                    severity = 1;
                    break;
                    
                case NODE_HEALTH_CRITICAL:
                    snprintf(message, sizeof(message), 
                            "节点进入危急状态，健康分数: %.2f", monitored->metrics.health_score);
                    severity = 2;
                    break;
                    
                case NODE_HEALTH_OFFLINE:
                    snprintf(message, sizeof(message), 
                            "节点离线");
                    severity = 3;
                    break;
                    
                default:
                    break;
            }
            
            /* 添加警报 */
            add_status_alert(monitor, node, new_status, message, severity);
            
            /* 如果配置自动恢复并且节点处于严重状态，尝试恢复 */
            if (monitor->config.enable_auto_recovery && 
                (new_status == NODE_HEALTH_CRITICAL || new_status == NODE_HEALTH_OFFLINE)) {
                
                monitored->recovery_attempts++;
                
                /* 尝试恢复节点 */
                if (node->recover && monitored->recovery_attempts <= 3) {
                    printf("尝试恢复节点 %p (尝试 #%d)\n", (void*)node, monitored->recovery_attempts);
                    node->recover(node);
                }
            }
        }
    } 
    /* 如果状态改善，重置警报计数和恢复尝试次数 */
    else if (new_status < old_status) {
        monitored->alert_count = 0;
        monitored->recovery_attempts = 0;
        
        /* 如果节点恢复正常，记录一条消息 */
        if (new_status == NODE_HEALTH_NORMAL && 
            (old_status == NODE_HEALTH_WARNING || 
             old_status == NODE_HEALTH_CRITICAL || 
             old_status == NODE_HEALTH_OFFLINE)) {
            
            char message[256];
            snprintf(message, sizeof(message), 
                    "节点已恢复正常状态，健康分数: %.2f", monitored->metrics.health_score);
            
            /* 添加恢复警报 */
            add_status_alert(monitor, node, new_status, message, 0);
        }
    }
    
    /* 触发事件 */
    if (monitor->event_system) {
        int event_type = EVENT_NODE_STATUS_CHANGED;
        
        /* 根据状态变化选择更具体的事件类型 */
        if (old_status == NODE_HEALTH_OFFLINE && new_status != NODE_HEALTH_OFFLINE) {
            event_type = EVENT_NODE_ACTIVATED;
        } else if (old_status != NODE_HEALTH_OFFLINE && new_status == NODE_HEALTH_OFFLINE) {
            event_type = EVENT_NODE_DEACTIVATED;
        } else if (new_status > old_status && new_status != NODE_HEALTH_OFFLINE) {
            event_type = EVENT_NODE_DEGRADED;
        } else if (new_status < old_status) {
            event_type = EVENT_NODE_RECOVERED;
        }
        
        /* 创建并发射事件 */
        QEntLEvent* event = event_system_create_event(monitor->event_system, 
                                                 event_type, 
                                                 &report, 
                                                 sizeof(NodeStatusReport));
        if (event) {
            event_system_emit_event(monitor->event_system, event);
        }
    }
    
    /* 执行回调 */
    execute_callbacks(monitor, node, new_status, &report);
}

/**
 * 执行状态回调
 */
static void execute_callbacks(NodeStatusMonitor* monitor, 
                            QNetworkNode* node, 
                            NodeHealthStatus status, 
                            NodeStatusReport* report) {
    if (!monitor) return;
    
    for (int i = 0; i < monitor->callback_count; i++) {
        if (monitor->callbacks[i].callback) {
            monitor->callbacks[i].callback(node, status, report, monitor->callbacks[i].user_data);
        }
    }
}

/**
 * 添加状态警报
 */
static void add_status_alert(NodeStatusMonitor* monitor, 
                           QNetworkNode* node, 
                           NodeHealthStatus status, 
                           const char* message, 
                           int severity) {
    if (!monitor || !node || !message) return;
    
    /* 创建警报 */
    StatusAlert* alert = create_status_alert(node, status, message, severity);
    if (!alert) return;
    
    /* 检查是否需要扩展警报数组 */
    if (monitor->alert_count >= monitor->alert_capacity) {
        int new_capacity = monitor->alert_capacity * 2;
        StatusAlert** new_alerts = (StatusAlert**)realloc(
            monitor->alerts, 
            new_capacity * sizeof(StatusAlert*));
        
        if (!new_alerts) {
            free_status_alert(alert);
            fprintf(stderr, "错误: 无法扩展警报数组\n");
            return;
        }
        
        monitor->alerts = new_alerts;
        monitor->alert_capacity = new_capacity;
    }
    
    /* 添加警报 */
    monitor->alerts[monitor->alert_count++] = alert;
    
    /* 如果超出历史记录大小限制，移除最旧的警报 */
    if (monitor->alert_count > monitor->config.alert_history_size) {
        free_status_alert(monitor->alerts[0]);
        
        /* 移动数组元素 */
        for (int i = 0; i < monitor->alert_count - 1; i++) {
            monitor->alerts[i] = monitor->alerts[i + 1];
        }
        
        monitor->alert_count--;
    }
    
    /* 根据严重程度记录警报 */
    if (monitor->config.enable_logging) {
        char severity_str[16] = "信息";
        
        if (severity == 1) strcpy(severity_str, "警告");
        else if (severity == 2) strcpy(severity_str, "危急");
        else if (severity == 3) strcpy(severity_str, "严重");
        
        printf("[%s] 节点 %p: %s\n", severity_str, (void*)node, message);
    }
}

/**
 * 创建状态警报
 */
static StatusAlert* create_status_alert(QNetworkNode* node, 
                                     NodeHealthStatus status, 
                                     const char* message, 
                                     int severity) {
    if (!node || !message) return NULL;
    
    StatusAlert* alert = (StatusAlert*)malloc(sizeof(StatusAlert));
    if (!alert) return NULL;
    
    alert->node = node;
    alert->status = status;
    alert->timestamp = time(NULL);
    alert->severity = severity;
    
    /* 复制消息 */
    alert->message = strdup(message);
    if (!alert->message) {
        free(alert);
        return NULL;
    }
    
    return alert;
}

/**
 * 更新健康统计
 */
static void update_health_stats(NodeStatusMonitor* monitor) {
    if (!monitor) return;
    
    /* 重置计数器 */
    monitor->normal_nodes = 0;
    monitor->warning_nodes = 0;
    monitor->critical_nodes = 0;
    monitor->offline_nodes = 0;
    
    /* 遍历所有节点并计数 */
    for (int i = 0; i < monitor->node_count; i++) {
        switch (monitor->monitored_nodes[i]->current_status) {
            case NODE_HEALTH_NORMAL:
                monitor->normal_nodes++;
                break;
                
            case NODE_HEALTH_WARNING:
                monitor->warning_nodes++;
                break;
                
            case NODE_HEALTH_CRITICAL:
                monitor->critical_nodes++;
                break;
                
            case NODE_HEALTH_OFFLINE:
                monitor->offline_nodes++;
                break;
                
            default:
                break;
        }
    }
}

/**
 * 添加状态回调
 */
int node_status_monitor_add_callback(NodeStatusMonitor* monitor, 
                                   NodeStatusCallback callback, 
                                   void* user_data) {
    if (!monitor || !callback) return 0;
    
    /* 检查是否需要扩展回调数组 */
    if (monitor->callback_count >= monitor->callback_capacity) {
        int new_capacity = monitor->callback_capacity * 2;
        CallbackEntry* new_callbacks = (CallbackEntry*)realloc(
            monitor->callbacks, 
            new_capacity * sizeof(CallbackEntry));
        
        if (!new_callbacks) {
            fprintf(stderr, "错误: 无法扩展回调数组\n");
            return 0;
        }
        
        monitor->callbacks = new_callbacks;
        monitor->callback_capacity = new_capacity;
    }
    
    /* 添加回调 */
    monitor->callbacks[monitor->callback_count].callback = callback;
    monitor->callbacks[monitor->callback_count].user_data = user_data;
    monitor->callback_count++;
    
    return 1;
}

/**
 * 移除状态回调
 */
int node_status_monitor_remove_callback(NodeStatusMonitor* monitor, 
                                      NodeStatusCallback callback, 
                                      void* user_data) {
    if (!monitor || !callback) return 0;
    
    int found_index = -1;
    
    /* 查找回调 */
    for (int i = 0; i < monitor->callback_count; i++) {
        if (monitor->callbacks[i].callback == callback &&
            monitor->callbacks[i].user_data == user_data) {
            found_index = i;
            break;
        }
    }
    
    if (found_index < 0) {
        return 0;  /* 回调不存在 */
    }
    
    /* 移动数组中的元素以填补空缺 */
    for (int i = found_index; i < monitor->callback_count - 1; i++) {
        monitor->callbacks[i] = monitor->callbacks[i + 1];
    }
    
    monitor->callback_count--;
    
    return 1;
}

/**
 * 生成状态报告
 */
NodeStatusReport* node_status_monitor_generate_report(NodeStatusMonitor* monitor) {
    if (!monitor) return NULL;
    
    /* 分配报告内存 */
    NodeStatusReport* report = (NodeStatusReport*)malloc(sizeof(NodeStatusReport));
    if (!report) {
        fprintf(stderr, "错误: 无法分配报告内存\n");
        return NULL;
    }
    
    /* 填充报告字段 */
    report->timestamp = time(NULL);
    report->node = NULL;  /* 这是一个网络级别的报告 */
    report->previous_status = NODE_HEALTH_UNKNOWN;
    report->current_status = NODE_HEALTH_UNKNOWN;
    report->since_last_change = 0;
    
    /* 复制指标 */
    memset(&report->metrics, 0, sizeof(NodeHealthMetrics));
    
    /* 设置节点统计信息 */
    report->total_nodes = monitor->total_nodes;
    report->normal_nodes = monitor->normal_nodes;
    report->warning_nodes = monitor->warning_nodes;
    report->critical_nodes = monitor->critical_nodes;
    report->offline_nodes = monitor->offline_nodes;
    
    /* 计算整体网络健康分数 */
    if (monitor->total_nodes > 0) {
        double total_score = 0.0;
        int active_nodes = 0;
        
        for (int i = 0; i < monitor->node_count; i++) {
            MonitoredNode* monitored = monitor->monitored_nodes[i];
            if (monitored->current_status != NODE_HEALTH_OFFLINE) {
                total_score += monitored->metrics.health_score;
                active_nodes++;
            }
        }
        
        if (active_nodes > 0) {
            report->metrics.health_score = total_score / active_nodes;
        } else {
            report->metrics.health_score = 0.0;
        }
        
        /* 设置网络可用性 */
        report->metrics.availability = (double)(monitor->total_nodes - monitor->offline_nodes) / 
                                     monitor->total_nodes;
    }
    
    return report;
}

/**
 * 节点事件处理函数
 */
int node_status_monitor_event_handler(QEntLEvent* event, void* user_data) {
    if (!event || !user_data) return 0;
    
    NodeStatusMonitor* monitor = (NodeStatusMonitor*)user_data;
    
    /* 处理各种节点相关事件 */
    switch (event->type) {
        case EVENT_NODE_ACTIVATED:
        case EVENT_NODE_DEACTIVATED:
        case EVENT_NODE_DEGRADED:
        case EVENT_NODE_RECOVERED:
            on_node_event(event, monitor);
            break;
            
        default:
            /* 忽略其他事件类型 */
            break;
    }
    
    return 1;
}

/**
 * 处理节点事件
 */
static void on_node_event(QEntLEvent* event, NodeStatusMonitor* monitor) {
    if (!event || !monitor || !event->data) return;
    
    /* 获取事件数据 */
    NodeStatusReport* report = (NodeStatusReport*)event->data;
    QNetworkNode* node = report->node;
    
    if (!node) return;
    
    /* 查找节点 */
    MonitoredNode* monitored = find_monitored_node(monitor, node);
    
    /* 如果节点不在监控列表中，且是激活事件，添加节点 */
    if (!monitored && event->type == EVENT_NODE_ACTIVATED) {
        node_status_monitor_add_node(monitor, node);
        return;
    }
    
    /* 如果节点不在监控列表中，无法处理 */
    if (!monitored) return;
    
    /* 处理事件 */
    switch (event->type) {
        case EVENT_NODE_ACTIVATED:
            /* 节点激活 */
            if (monitored->current_status == NODE_HEALTH_OFFLINE) {
                monitored->previous_status = monitored->current_status;
                monitored->current_status = NODE_HEALTH_NORMAL;
                monitored->last_status_change = time(NULL);
                
                /* 更新指标和健康统计 */
                monitored->metrics = calculate_node_metrics(monitor, node);
                update_health_stats(monitor);
            }
            break;
            
        case EVENT_NODE_DEACTIVATED:
            /* 节点停用 */
            monitored->previous_status = monitored->current_status;
            monitored->current_status = NODE_HEALTH_OFFLINE;
            monitored->last_status_change = time(NULL);
            
            /* 更新健康统计 */
            update_health_stats(monitor);
            break;
            
        case EVENT_NODE_DEGRADED:
            /* 节点性能下降 */
            if (monitored->current_status < report->current_status) {
                monitored->previous_status = monitored->current_status;
                monitored->current_status = report->current_status;
                monitored->last_status_change = time(NULL);
                
                /* 更新指标和健康统计 */
                monitored->metrics = report->metrics;
                update_health_stats(monitor);
            }
            break;
            
        case EVENT_NODE_RECOVERED:
            /* 节点恢复 */
            if (monitored->current_status > report->current_status) {
                monitored->previous_status = monitored->current_status;
                monitored->current_status = report->current_status;
                monitored->last_status_change = time(NULL);
                
                /* 更新指标和健康统计 */
                monitored->metrics = report->metrics;
                update_health_stats(monitor);
            }
            break;
            
        default:
            break;
    }
}

/**
 * 获取节点状态
 */
NodeHealthStatus node_status_monitor_get_node_status(NodeStatusMonitor* monitor, 
                                                  QNetworkNode* node) {
    if (!monitor || !node) {
        return NODE_HEALTH_UNKNOWN;
    }
    
    /* 查找节点 */
    MonitoredNode* monitored = find_monitored_node(monitor, node);
    if (!monitored) {
        return NODE_HEALTH_UNKNOWN;
    }
    
    return monitored->current_status;
}

/**
 * 获取节点健康指标
 */
NodeHealthMetrics node_status_monitor_get_node_metrics(NodeStatusMonitor* monitor, 
                                                    QNetworkNode* node) {
    NodeHealthMetrics empty_metrics = {0};
    
    if (!monitor || !node) {
        return empty_metrics;
    }
    
    /* 查找节点 */
    MonitoredNode* monitored = find_monitored_node(monitor, node);
    if (!monitored) {
        return empty_metrics;
    }
    
    return monitored->metrics;
}

/**
 * 获取网络状态统计
 */
void node_status_monitor_get_network_stats(NodeStatusMonitor* monitor, 
                                        int* total, 
                                        int* normal, 
                                        int* warning, 
                                        int* critical, 
                                        int* offline) {
    if (!monitor) return;
    
    if (total) *total = monitor->total_nodes;
    if (normal) *normal = monitor->normal_nodes;
    if (warning) *warning = monitor->warning_nodes;
    if (critical) *critical = monitor->critical_nodes;
    if (offline) *offline = monitor->offline_nodes;
} 