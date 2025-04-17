/**
 * QEntL量子网络连接管理器头文件
 * 
 * 量子基因编码: QG-RUNTIME-NETCON-HDR-G3K5-1713051400
 * 
 * @文件: network_connection_manager.h
 * @描述: 定义QEntL运行时的量子网络连接管理器API
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-18
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，负责管理量子网络中节点之间的连接
 * - 支持自动连接优化、负载均衡和故障恢复
 * - 能够动态调整连接强度和带宽分配
 */

#ifndef QENTL_NETWORK_CONNECTION_MANAGER_H
#define QENTL_NETWORK_CONNECTION_MANAGER_H

#include "../../quantum_network.h"
#include "global_network_builder.h"
#include "../event_system.h"

/**
 * 前向声明
 */
typedef struct NetworkConnectionManager NetworkConnectionManager;
typedef struct ConnectionStats ConnectionStats;
typedef struct ConnectionConfig ConnectionConfig;

/**
 * 连接状态枚举
 */
typedef enum {
    CONNECTION_STATE_INACTIVE = 0,    /* 未激活 */
    CONNECTION_STATE_CONNECTING = 1,  /* 连接中 */
    CONNECTION_STATE_ACTIVE = 2,      /* 已激活 */
    CONNECTION_STATE_DEGRADED = 3,    /* 性能下降 */
    CONNECTION_STATE_FAILED = 4,      /* 连接失败 */
    CONNECTION_STATE_CLOSING = 5      /* 正在关闭 */
} ConnectionState;

/**
 * 连接类型枚举
 */
typedef enum {
    CONNECTION_TYPE_DIRECT = 0,       /* 直接连接 */
    CONNECTION_TYPE_RELAY = 1,        /* 中继连接 */
    CONNECTION_TYPE_TUNNEL = 2,       /* 隧道连接 */
    CONNECTION_TYPE_BROADCAST = 3,    /* 广播连接 */
    CONNECTION_TYPE_MULTICAST = 4     /* 多播连接 */
} ConnectionType;

/**
 * 连接优化策略枚举
 */
typedef enum {
    CONN_OPT_NONE = 0,                /* 不优化 */
    CONN_OPT_STRENGTH = 1,            /* 优化连接强度 */
    CONN_OPT_LATENCY = 2,             /* 优化延迟 */
    CONN_OPT_BANDWIDTH = 3,           /* 优化带宽 */
    CONN_OPT_RELIABILITY = 4,         /* 优化可靠性 */
    CONN_OPT_BALANCED = 5             /* 平衡优化 */
} ConnectionOptStrategy;

/**
 * 连接统计结构
 */
typedef struct ConnectionStats {
    int total_connections;             /* 总连接数 */
    int active_connections;            /* 活跃连接数 */
    int degraded_connections;          /* 性能下降的连接数 */
    int failed_connections;            /* 失败的连接数 */
    
    double average_strength;           /* 平均连接强度 */
    double average_bandwidth;          /* 平均带宽 */
    double average_latency;            /* 平均延迟 */
    
    int connection_attempts;           /* 连接尝试次数 */
    int successful_connections;        /* 成功的连接次数 */
    int connection_failures;           /* 连接失败次数 */
    
    int reconnection_attempts;         /* 重连尝试次数 */
    int successful_reconnections;      /* 成功的重连次数 */
    
    time_t last_connection_time;       /* 最后连接时间 */
    time_t last_optimization_time;     /* 最后优化时间 */
} ConnectionStats;

/**
 * 连接配置结构
 */
typedef struct ConnectionConfig {
    int auto_connect;                   /* 是否自动连接 */
    int max_connections;                /* 最大连接数 */
    int max_retries;                    /* 最大重试次数 */
    double connection_timeout;          /* 连接超时时间(秒) */
    
    ConnectionOptStrategy opt_strategy; /* 连接优化策略 */
    int optimization_interval;          /* 优化间隔(秒) */
    
    double min_connection_strength;     /* 最小连接强度 */
    double strength_threshold;          /* 连接强度阈值 */
    
    int enable_load_balancing;          /* 是否启用负载均衡 */
    int enable_fault_tolerance;         /* 是否启用故障容错 */
    
    int persistent_connections;         /* 是否保持持久连接 */
    void* custom_config;                /* 自定义配置 */
} ConnectionConfig;

/**
 * 连接事件回调函数
 * 
 * @param source 源节点
 * @param target 目标节点
 * @param state 连接状态
 * @param user_data 用户数据
 */
typedef void (*ConnectionEventCallback)(QNetworkNode* source, 
                                      QNetworkNode* target, 
                                      ConnectionState state,
                                      void* user_data);

/**
 * 创建网络连接管理器
 * 
 * @param network_builder 全局网络构建器
 * @param event_system 事件系统
 * @return 新创建的连接管理器
 */
NetworkConnectionManager* network_connection_manager_create(
    GlobalNetworkBuilder* network_builder, 
    EventSystem* event_system);

/**
 * 销毁网络连接管理器
 * 
 * @param manager 要销毁的连接管理器
 */
void network_connection_manager_destroy(NetworkConnectionManager* manager);

/**
 * 设置连接配置
 * 
 * @param manager 连接管理器
 * @param config 连接配置
 * @return 成功返回1，失败返回0
 */
int network_connection_manager_set_config(NetworkConnectionManager* manager, 
                                       ConnectionConfig config);

/**
 * 获取连接配置
 * 
 * @param manager 连接管理器
 * @return 连接配置
 */
ConnectionConfig network_connection_manager_get_config(NetworkConnectionManager* manager);

/**
 * 创建节点连接
 * 
 * @param manager 连接管理器
 * @param source 源节点
 * @param target 目标节点
 * @param type 连接类型
 * @param strength 连接强度(0.0-1.0)
 * @return 成功返回1，失败返回0
 */
int network_connection_manager_create_connection(NetworkConnectionManager* manager,
                                              QNetworkNode* source,
                                              QNetworkNode* target,
                                              ConnectionType type,
                                              double strength);

/**
 * 关闭节点连接
 * 
 * @param manager 连接管理器
 * @param source 源节点
 * @param target 目标节点
 * @return 成功返回1，失败返回0
 */
int network_connection_manager_close_connection(NetworkConnectionManager* manager,
                                             QNetworkNode* source,
                                             QNetworkNode* target);

/**
 * 获取连接状态
 * 
 * @param manager 连接管理器
 * @param source 源节点
 * @param target 目标节点
 * @return 连接状态
 */
ConnectionState network_connection_manager_get_connection_state(NetworkConnectionManager* manager,
                                                             QNetworkNode* source,
                                                             QNetworkNode* target);

/**
 * 获取连接强度
 * 
 * @param manager 连接管理器
 * @param source 源节点
 * @param target 目标节点
 * @return 连接强度(0.0-1.0)，失败返回-1.0
 */
double network_connection_manager_get_connection_strength(NetworkConnectionManager* manager,
                                                       QNetworkNode* source,
                                                       QNetworkNode* target);

/**
 * 设置连接强度
 * 
 * @param manager 连接管理器
 * @param source 源节点
 * @param target 目标节点
 * @param strength 连接强度(0.0-1.0)
 * @return 成功返回1，失败返回0
 */
int network_connection_manager_set_connection_strength(NetworkConnectionManager* manager,
                                                    QNetworkNode* source,
                                                    QNetworkNode* target,
                                                    double strength);

/**
 * 注册连接事件回调
 * 
 * @param manager 连接管理器
 * @param callback 回调函数
 * @param user_data 用户数据
 * @return 成功返回1，失败返回0
 */
int network_connection_manager_register_callback(NetworkConnectionManager* manager,
                                              ConnectionEventCallback callback,
                                              void* user_data);

/**
 * 优化连接
 * 
 * @param manager 连接管理器
 * @param strategy 优化策略
 * @return 成功返回1，失败返回0
 */
int network_connection_manager_optimize_connections(NetworkConnectionManager* manager,
                                                 ConnectionOptStrategy strategy);

/**
 * 获取连接统计
 * 
 * @param manager 连接管理器
 * @return 连接统计
 */
ConnectionStats network_connection_manager_get_stats(NetworkConnectionManager* manager);

/**
 * 重置连接统计
 * 
 * @param manager 连接管理器
 */
void network_connection_manager_reset_stats(NetworkConnectionManager* manager);

/**
 * 保存连接状态到文件
 * 
 * @param manager 连接管理器
 * @param filename 文件名
 * @return 成功返回1，失败返回0
 */
int network_connection_manager_save_state(NetworkConnectionManager* manager,
                                       const char* filename);

/**
 * 从文件加载连接状态
 * 
 * @param manager 连接管理器
 * @param filename 文件名
 * @return 成功返回1，失败返回0
 */
int network_connection_manager_load_state(NetworkConnectionManager* manager,
                                       const char* filename);

/**
 * 事件处理函数
 */
void network_connection_manager_event_handler(QEntLEvent* event, void* user_data);

#endif /* QENTL_NETWORK_CONNECTION_MANAGER_H */ 