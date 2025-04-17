/**
 * QEntL量子网络全局构建器头文件
 * 
 * 量子基因编码: QG-RUNTIME-NETBLD-HDR-G2H4-1713051200
 * 
 * @文件: global_network_builder.h
 * @描述: 定义QEntL运行时的量子网络全局构建器API
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-18
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 网络构建器支持自动探测和连接网络节点
 * - 支持跨设备量子网络拓扑结构的构建和优化
 */

#ifndef QENTL_GLOBAL_NETWORK_BUILDER_H
#define QENTL_GLOBAL_NETWORK_BUILDER_H

#include "../../quantum_network.h"
#include "node_activator.h"
#include "../event_system.h"

/**
 * 前向声明
 */
typedef struct GlobalNetworkBuilder GlobalNetworkBuilder;
typedef struct NetworkTopology NetworkTopology;
typedef struct NetworkBuilderConfig NetworkBuilderConfig;
typedef struct NetworkBuildingStats NetworkBuildingStats;

/**
 * 网络构建模式枚举
 */
typedef enum {
    NETWORK_BUILD_MODE_AUTOMATIC,   /* 完全自动模式 */
    NETWORK_BUILD_MODE_SEMI_AUTO,   /* 半自动模式(需要确认关键连接) */
    NETWORK_BUILD_MODE_MANUAL,      /* 手动模式(需要确认所有连接) */
    NETWORK_BUILD_MODE_SCHEDULED    /* 定时构建模式 */
} NetworkBuildMode;

/**
 * 网络拓扑类型枚举
 */
typedef enum {
    NETWORK_TOPOLOGY_MESH,          /* 网状拓扑 */
    NETWORK_TOPOLOGY_STAR,          /* 星型拓扑 */
    NETWORK_TOPOLOGY_RING,          /* 环形拓扑 */
    NETWORK_TOPOLOGY_TREE,          /* 树形拓扑 */
    NETWORK_TOPOLOGY_BUS,           /* 总线拓扑 */
    NETWORK_TOPOLOGY_HYBRID,        /* 混合拓扑 */
    NETWORK_TOPOLOGY_DYNAMIC        /* 动态自适应拓扑 */
} NetworkTopologyType;

/**
 * 连接优先级枚举
 */
typedef enum {
    CONNECTION_PRIORITY_LOW,         /* 低优先级 */
    CONNECTION_PRIORITY_NORMAL,      /* 普通优先级 */
    CONNECTION_PRIORITY_HIGH,        /* 高优先级 */
    CONNECTION_PRIORITY_CRITICAL     /* 关键优先级 */
} ConnectionPriority;

/**
 * 网络构建配置结构
 */
typedef struct NetworkBuilderConfig {
    NetworkBuildMode build_mode;                /* 构建模式 */
    NetworkTopologyType topology_type;          /* 拓扑类型 */
    int auto_discovery_enabled;                 /* 是否启用自动发现 */
    int max_discovery_depth;                    /* 最大发现深度 */
    int max_connections_per_node;               /* 每个节点的最大连接数 */
    double min_connection_strength;             /* 最小连接强度 */
    int enable_connection_optimization;         /* 是否启用连接优化 */
    int enable_fault_tolerance;                 /* 是否启用容错 */
    int connection_retry_count;                 /* 连接重试次数 */
    double connection_timeout;                  /* 连接超时(秒) */
    double network_stability_threshold;         /* 网络稳定性阈值 */
    void* custom_config;                        /* 自定义配置 */
} NetworkBuilderConfig;

/**
 * 网络构建统计结构
 */
typedef struct NetworkBuildingStats {
    time_t build_start_time;                    /* 构建开始时间 */
    time_t last_build_time;                     /* 上次构建时间 */
    int total_build_attempts;                   /* 总构建尝试次数 */
    int successful_builds;                      /* 成功构建次数 */
    int failed_builds;                          /* 失败构建次数 */
    int nodes_discovered;                       /* 发现的节点数 */
    int connections_established;                /* 建立的连接数 */
    int connections_failed;                     /* 失败的连接数 */
    int topology_changes;                       /* 拓扑变化次数 */
    double average_build_time;                  /* 平均构建时间 */
    double network_stability;                   /* 网络稳定性(0-1) */
    int active_nodes;                           /* 活跃节点数 */
} NetworkBuildingStats;

/**
 * 连接确认回调函数
 * 
 * @param node1 第一个节点
 * @param node2 第二个节点
 * @param priority 连接优先级
 * @param user_data 用户数据
 * @return 允许连接返回1，拒绝连接返回0
 */
typedef int (*ConnectionConfirmCallback)(QNetworkNode* node1, QNetworkNode* node2, 
                                       ConnectionPriority priority, void* user_data);

/**
 * 网络构建完成回调函数
 * 
 * @param builder 网络构建器
 * @param success 构建是否成功
 * @param nodes 节点数组
 * @param node_count 节点数量
 * @param user_data 用户数据
 */
typedef void (*NetworkBuildCompleteCallback)(GlobalNetworkBuilder* builder, int success,
                                          QNetworkNode** nodes, int node_count, void* user_data);

/**
 * 创建全局网络构建器
 * 
 * @param node_activator 节点激活器
 * @param event_system 事件系统
 * @return 新创建的网络构建器
 */
GlobalNetworkBuilder* global_network_builder_create(NodeActivator* node_activator, 
                                                  EventSystem* event_system);

/**
 * 销毁全局网络构建器
 * 
 * @param builder 要销毁的网络构建器
 */
void global_network_builder_destroy(GlobalNetworkBuilder* builder);

/**
 * 设置网络构建配置
 * 
 * @param builder 网络构建器
 * @param config 构建配置
 * @return 成功返回1，失败返回0
 */
int global_network_builder_set_config(GlobalNetworkBuilder* builder, NetworkBuilderConfig config);

/**
 * 获取网络构建配置
 * 
 * @param builder 网络构建器
 * @return 构建配置
 */
NetworkBuilderConfig global_network_builder_get_config(GlobalNetworkBuilder* builder);

/**
 * 注册连接确认回调
 * 
 * @param builder 网络构建器
 * @param callback 回调函数
 * @param user_data 用户数据
 * @return 成功返回1，失败返回0
 */
int global_network_builder_register_confirm_callback(GlobalNetworkBuilder* builder, 
                                                  ConnectionConfirmCallback callback, 
                                                  void* user_data);

/**
 * 注册构建完成回调
 * 
 * @param builder 网络构建器
 * @param callback 回调函数
 * @param user_data 用户数据
 * @return 成功返回1，失败返回0
 */
int global_network_builder_register_complete_callback(GlobalNetworkBuilder* builder, 
                                                   NetworkBuildCompleteCallback callback, 
                                                   void* user_data);

/**
 * 启动网络构建
 * 
 * @param builder 网络构建器
 * @return 成功返回1，失败返回0
 */
int global_network_builder_start(GlobalNetworkBuilder* builder);

/**
 * 停止网络构建
 * 
 * @param builder 网络构建器
 * @return 成功返回1，失败返回0
 */
int global_network_builder_stop(GlobalNetworkBuilder* builder);

/**
 * 获取网络构建统计
 * 
 * @param builder 网络构建器
 * @return 构建统计
 */
NetworkBuildingStats global_network_builder_get_stats(GlobalNetworkBuilder* builder);

/**
 * 添加种子节点
 * 
 * @param builder 网络构建器
 * @param node 要添加的节点
 * @return 成功返回1，失败返回0
 */
int global_network_builder_add_seed_node(GlobalNetworkBuilder* builder, QNetworkNode* node);

/**
 * 获取当前网络拓扑
 * 
 * @param builder 网络构建器
 * @return 网络拓扑
 */
NetworkTopology* global_network_builder_get_topology(GlobalNetworkBuilder* builder);

/**
 * 设置网络拓扑类型
 * 
 * @param builder 网络构建器
 * @param type 拓扑类型
 * @return 成功返回1，失败返回0
 */
int global_network_builder_set_topology_type(GlobalNetworkBuilder* builder, NetworkTopologyType type);

/**
 * 优化网络拓扑
 * 
 * @param builder 网络构建器
 * @param optimization_level 优化级别(0-3)
 * @return 成功返回1，失败返回0
 */
int global_network_builder_optimize_topology(GlobalNetworkBuilder* builder, int optimization_level);

/**
 * 手动连接两个节点
 * 
 * @param builder 网络构建器
 * @param node1 第一个节点
 * @param node2 第二个节点
 * @param strength 连接强度(0.0-1.0)
 * @return 成功返回1，失败返回0
 */
int global_network_builder_connect_nodes(GlobalNetworkBuilder* builder, 
                                      QNetworkNode* node1, 
                                      QNetworkNode* node2, 
                                      double strength);

/**
 * 断开节点连接
 * 
 * @param builder 网络构建器
 * @param node1 第一个节点
 * @param node2 第二个节点
 * @return 成功返回1，失败返回0
 */
int global_network_builder_disconnect_nodes(GlobalNetworkBuilder* builder, 
                                         QNetworkNode* node1, 
                                         QNetworkNode* node2);

/**
 * 探测网络中的所有节点
 * 
 * @param builder 网络构建器
 * @param max_depth 最大探测深度
 * @param nodes 输出节点数组
 * @param node_count 输出节点数量
 * @return 成功返回1，失败返回0
 */
int global_network_builder_discover_nodes(GlobalNetworkBuilder* builder, 
                                       int max_depth, 
                                       QNetworkNode*** nodes, 
                                       int* node_count);

/**
 * 处理网络构建周期
 * 
 * @param builder 网络构建器
 * @return 构建的连接数量
 */
int global_network_builder_process_cycle(GlobalNetworkBuilder* builder);

/**
 * 检测和修复网络问题
 * 
 * @param builder 网络构建器
 * @return 修复的问题数量
 */
int global_network_builder_repair_network(GlobalNetworkBuilder* builder);

/**
 * 将当前网络拓扑保存到文件
 * 
 * @param builder 网络构建器
 * @param filename 文件名
 * @return 成功返回1，失败返回0
 */
int global_network_builder_save_topology(GlobalNetworkBuilder* builder, const char* filename);

/**
 * 从文件加载网络拓扑
 * 
 * @param builder 网络构建器
 * @param filename 文件名
 * @return 成功返回1，失败返回0
 */
int global_network_builder_load_topology(GlobalNetworkBuilder* builder, const char* filename);

/**
 * 网络构建器事件处理函数
 * 
 * @param event 事件
 * @param user_data 用户数据(网络构建器)
 */
void global_network_builder_event_handler(QEntLEvent* event, void* user_data);

/**
 * 网络拓扑结构API
 */

/**
 * 创建网络拓扑
 * 
 * @param type 拓扑类型
 * @return 新创建的网络拓扑
 */
NetworkTopology* network_topology_create(NetworkTopologyType type);

/**
 * 销毁网络拓扑
 * 
 * @param topology 要销毁的网络拓扑
 */
void network_topology_destroy(NetworkTopology* topology);

/**
 * 添加节点到拓扑
 * 
 * @param topology 网络拓扑
 * @param node 要添加的节点
 * @return 成功返回1，失败返回0
 */
int network_topology_add_node(NetworkTopology* topology, QNetworkNode* node);

/**
 * 添加连接到拓扑
 * 
 * @param topology 网络拓扑
 * @param node1 第一个节点
 * @param node2 第二个节点
 * @param strength 连接强度
 * @return 成功返回1，失败返回0
 */
int network_topology_add_connection(NetworkTopology* topology, 
                                 QNetworkNode* node1, 
                                 QNetworkNode* node2, 
                                 double strength);

/**
 * 计算拓扑的可靠性
 * 
 * @param topology 网络拓扑
 * @return 可靠性度量(0.0-1.0)
 */
double network_topology_calculate_reliability(NetworkTopology* topology);

/**
 * 计算拓扑的效率
 * 
 * @param topology 网络拓扑
 * @return 效率度量(0.0-1.0)
 */
double network_topology_calculate_efficiency(NetworkTopology* topology);

/**
 * 获取网络拓扑统计信息
 * 
 * @param topology 网络拓扑
 * @param node_count 输出节点数量
 * @param connection_count 输出连接数量
 * @param avg_connections 输出平均连接数
 * @param density 输出拓扑密度
 */
void network_topology_get_stats(NetworkTopology* topology, 
                             int* node_count, 
                             int* connection_count, 
                             double* avg_connections, 
                             double* density);

#endif /* QENTL_GLOBAL_NETWORK_BUILDER_H */ 