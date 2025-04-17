/**
 * QEntL量子网络节点状态监控系统头文件
 * 
 * 量子基因编码: QG-RUNTIME-NODEMON-HDR-G4M7-1713051600
 * 
 * @文件: node_status_monitor.h
 * @描述: 定义QEntL运行时的量子网络节点状态监控系统API
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-18
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，负责监控量子网络中节点的状态
 * - 支持节点健康监测、异常预警、性能分析和状态报告
 * - 能够与网络连接管理器协同工作，实现网络自愈和优化
 */

#ifndef QENTL_NODE_STATUS_MONITOR_H
#define QENTL_NODE_STATUS_MONITOR_H

#include "../../quantum_network.h"
#include "network_connection_manager.h"
#include "../event_system.h"

/**
 * 前向声明
 */
typedef struct NodeStatusMonitor NodeStatusMonitor;
typedef struct NodeStatusConfig NodeStatusConfig;
typedef struct NodeStatusReport NodeStatusReport;
typedef struct NodeHealthMetrics NodeHealthMetrics;

/**
 * 节点状态枚举
 */
typedef enum {
    NODE_HEALTH_UNKNOWN = 0,     /* 未知状态 */
    NODE_HEALTH_NORMAL = 1,      /* 正常状态 */
    NODE_HEALTH_WARNING = 2,     /* 警告状态 */
    NODE_HEALTH_CRITICAL = 3,    /* 危急状态 */
    NODE_HEALTH_OFFLINE = 4      /* 离线状态 */
} NodeHealthStatus;

/**
 * 节点监控级别枚举
 */
typedef enum {
    MONITOR_LEVEL_OFF = 0,       /* 关闭监控 */
    MONITOR_LEVEL_MINIMAL = 1,   /* 最小监控 */
    MONITOR_LEVEL_STANDARD = 2,  /* 标准监控 */
    MONITOR_LEVEL_INTENSIVE = 3, /* 密集监控 */
    MONITOR_LEVEL_DEBUG = 4      /* 调试监控 */
} MonitoringLevel;

/**
 * 节点健康指标
 */
typedef struct NodeHealthMetrics {
    double uptime_ratio;          /* 正常运行时间比例 */
    double stability;             /* 稳定性指标 */
    double entanglement_quality;  /* 纠缠质量 */
    double connection_quality;    /* 连接质量 */
    double error_rate;            /* 错误率 */
    double resource_usage;        /* 资源使用率 */
    double response_time;         /* 响应时间 */
    double overall_health;        /* 总体健康度 */
} NodeHealthMetrics;

/**
 * 节点状态报告
 */
typedef struct NodeStatusReport {
    QNetworkNode* node;           /* 节点指针 */
    NodeHealthStatus status;      /* 健康状态 */
    NodeHealthMetrics metrics;    /* 健康指标 */
    time_t timestamp;             /* 时间戳 */
    char* description;            /* 描述信息 */
    int alert_level;              /* 警报级别 */
    int connection_count;         /* 连接数量 */
    int active_connections;       /* 活跃连接数 */
    NodeHealthStatus* connected_nodes_health; /* 连接节点健康状态 */
} NodeStatusReport;

/**
 * 监控配置
 */
typedef struct NodeStatusConfig {
    int auto_monitor;             /* 是否自动监控 */
    int monitor_interval;         /* 监控间隔(秒) */
    MonitoringLevel level;        /* 监控级别 */
    
    double warning_threshold;     /* 警告阈值 */
    double critical_threshold;    /* 危急阈值 */
    
    int enable_alerts;            /* 是否启用警报 */
    int alert_history_size;       /* 警报历史大小 */
    
    int enable_auto_recovery;     /* 是否启用自动恢复 */
    int enable_logging;           /* 是否启用日志 */
    
    int enable_periodic_report;   /* 是否启用定期报告 */
    int report_interval;          /* 报告间隔(秒) */
    
    void* custom_config;          /* 自定义配置 */
} NodeStatusConfig;

/**
 * 节点状态更新回调函数
 * 
 * @param node 节点指针
 * @param status 健康状态
 * @param report 状态报告
 * @param user_data 用户数据
 */
typedef void (*NodeStatusCallback)(QNetworkNode* node, 
                                 NodeHealthStatus status, 
                                 NodeStatusReport* report, 
                                 void* user_data);

/**
 * 创建节点状态监控系统
 * 
 * @param connection_manager 连接管理器
 * @param event_system 事件系统
 * @return 新创建的状态监控系统
 */
NodeStatusMonitor* node_status_monitor_create(
    NetworkConnectionManager* connection_manager, 
    EventSystem* event_system);

/**
 * 销毁节点状态监控系统
 * 
 * @param monitor 要销毁的状态监控系统
 */
void node_status_monitor_destroy(NodeStatusMonitor* monitor);

/**
 * 设置监控配置
 * 
 * @param monitor 状态监控系统
 * @param config 监控配置
 * @return 成功返回1，失败返回0
 */
int node_status_monitor_set_config(NodeStatusMonitor* monitor, 
                                 NodeStatusConfig config);

/**
 * 获取监控配置
 * 
 * @param monitor 状态监控系统
 * @return 监控配置
 */
NodeStatusConfig node_status_monitor_get_config(NodeStatusMonitor* monitor);

/**
 * 添加节点到监控列表
 * 
 * @param monitor 状态监控系统
 * @param node 要监控的节点
 * @return 成功返回1，失败返回0
 */
int node_status_monitor_add_node(NodeStatusMonitor* monitor, 
                               QNetworkNode* node);

/**
 * 从监控列表移除节点
 * 
 * @param monitor 状态监控系统
 * @param node 要移除的节点
 * @return 成功返回1，失败返回0
 */
int node_status_monitor_remove_node(NodeStatusMonitor* monitor, 
                                  QNetworkNode* node);

/**
 * 查询节点健康状态
 * 
 * @param monitor 状态监控系统
 * @param node 要查询的节点
 * @return 节点健康状态
 */
NodeHealthStatus node_status_monitor_get_node_status(NodeStatusMonitor* monitor, 
                                                   QNetworkNode* node);

/**
 * 获取节点健康指标
 * 
 * @param monitor 状态监控系统
 * @param node 要查询的节点
 * @return 节点健康指标
 */
NodeHealthMetrics node_status_monitor_get_node_metrics(NodeStatusMonitor* monitor, 
                                                     QNetworkNode* node);

/**
 * 获取节点状态报告
 * 
 * @param monitor 状态监控系统
 * @param node 要查询的节点
 * @return 节点状态报告
 */
NodeStatusReport* node_status_monitor_get_node_report(NodeStatusMonitor* monitor, 
                                                    QNetworkNode* node);

/**
 * 释放节点状态报告
 * 
 * @param report 状态报告
 */
void node_status_monitor_free_report(NodeStatusReport* report);

/**
 * 注册状态更新回调
 * 
 * @param monitor 状态监控系统
 * @param callback 回调函数
 * @param user_data 用户数据
 * @return 成功返回1，失败返回0
 */
int node_status_monitor_register_callback(NodeStatusMonitor* monitor, 
                                        NodeStatusCallback callback, 
                                        void* user_data);

/**
 * 启动节点监控
 * 
 * @param monitor 状态监控系统
 * @return 成功返回1，失败返回0
 */
int node_status_monitor_start(NodeStatusMonitor* monitor);

/**
 * 停止节点监控
 * 
 * @param monitor 状态监控系统
 * @return 成功返回1，失败返回0
 */
int node_status_monitor_stop(NodeStatusMonitor* monitor);

/**
 * 请求立即执行监控检查
 * 
 * @param monitor 状态监控系统
 * @return 成功返回1，失败返回0
 */
int node_status_monitor_check_now(NodeStatusMonitor* monitor);

/**
 * 获取所有节点健康统计
 * 
 * @param monitor 状态监控系统
 * @param total 节点总数
 * @param normal 正常节点数
 * @param warning 警告节点数
 * @param critical 危急节点数
 * @param offline 离线节点数
 */
void node_status_monitor_get_health_stats(NodeStatusMonitor* monitor, 
                                        int* total, 
                                        int* normal, 
                                        int* warning, 
                                        int* critical, 
                                        int* offline);

/**
 * 保存监控状态到文件
 * 
 * @param monitor 状态监控系统
 * @param filename 文件名
 * @return 成功返回1，失败返回0
 */
int node_status_monitor_save_state(NodeStatusMonitor* monitor, 
                                 const char* filename);

/**
 * 从文件加载监控状态
 * 
 * @param monitor 状态监控系统
 * @param filename 文件名
 * @return 成功返回1，失败返回0
 */
int node_status_monitor_load_state(NodeStatusMonitor* monitor, 
                                 const char* filename);

/**
 * 尝试恢复问题节点
 * 
 * @param monitor 状态监控系统
 * @param node 要恢复的节点
 * @return 成功返回1，失败返回0
 */
int node_status_monitor_recover_node(NodeStatusMonitor* monitor, 
                                   QNetworkNode* node);

/**
 * 事件处理函数
 */
void node_status_monitor_event_handler(QEntLEvent* event, void* user_data);

#endif /* QENTL_NODE_STATUS_MONITOR_H */ 