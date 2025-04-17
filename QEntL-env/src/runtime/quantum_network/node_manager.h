/**
 * 量子网络节点管理器头文件
 * 
 * 该文件定义了量子网络节点管理器的数据结构和函数接口，用于管理量子网络中的节点。
 * 节点管理器负责网络拓扑结构的维护、节点生命周期管理和节点间通信路由。
 *
 * @file node_manager.h
 * @version 1.0
 * @date 2024-05-15
 */

#ifndef QENTL_NODE_MANAGER_H
#define QENTL_NODE_MANAGER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../../quantum_network.h"
#include "../entanglement/entanglement_processor.h"

/**
 * 节点管理器错误码
 */
typedef enum {
    NODE_MANAGER_ERROR_NONE = 0,               // 无错误
    NODE_MANAGER_ERROR_INVALID_ARGUMENT = 1,   // 无效参数
    NODE_MANAGER_ERROR_MEMORY_ALLOCATION = 2,  // 内存分配错误
    NODE_MANAGER_ERROR_NODE_NOT_FOUND = 3,     // 节点未找到
    NODE_MANAGER_ERROR_NODE_EXISTS = 4,        // 节点已存在
    NODE_MANAGER_ERROR_NODE_INACTIVE = 5,      // 节点未激活
    NODE_MANAGER_ERROR_NODE_FULL = 6,          // 节点连接已满
    NODE_MANAGER_ERROR_NETWORK_FULL = 7,       // 网络节点已满
    NODE_MANAGER_ERROR_CONNECTION_EXISTS = 8,  // 连接已存在
    NODE_MANAGER_ERROR_CONNECTION_FAILED = 9,  // 连接失败
    NODE_MANAGER_ERROR_INTERNAL = 10           // 内部错误
} NodeManagerError;

/**
 * 节点类型
 */
typedef enum {
    NODE_TYPE_NORMAL = 0,              // 普通节点
    NODE_TYPE_GATEWAY = 1,             // 网关节点
    NODE_TYPE_ROUTER = 2,              // 路由节点
    NODE_TYPE_BRIDGE = 3,              // 桥接节点
    NODE_TYPE_ANCHOR = 4,              // 锚点节点
    NODE_TYPE_SENSOR = 5,              // 感知节点
    NODE_TYPE_PROCESSOR = 6,           // 处理节点
    NODE_TYPE_STORAGE = 7,             // 存储节点
    NODE_TYPE_AUTHORITY = 8,           // 权威节点
    NODE_TYPE_CUSTOM = 9               // 自定义节点
} NodeType;

/**
 * 节点状态
 */
typedef enum {
    NODE_STATE_INACTIVE = 0,           // 未激活
    NODE_STATE_ACTIVE = 1,             // 激活
    NODE_STATE_SUSPENDED = 2,          // 暂停
    NODE_STATE_ERROR = 3,              // 错误
    NODE_STATE_OVERLOADED = 4,         // 过载
    NODE_STATE_MAINTENANCE = 5,        // 维护
    NODE_STATE_UPGRADING = 6,          // 升级中
    NODE_STATE_PROTECTED = 7,          // 受保护
    NODE_STATE_ISOLATED = 8            // 隔离
} NodeState;

/**
 * 连接类型
 */
typedef enum {
    CONNECTION_TYPE_DIRECT = 0,        // 直接连接
    CONNECTION_TYPE_ROUTED = 1,        // 路由连接
    CONNECTION_TYPE_ENTANGLED = 2,     // 量子纠缠连接
    CONNECTION_TYPE_SECURE = 3,        // 安全连接
    CONNECTION_TYPE_TEMPORAL = 4,      // 临时连接
    CONNECTION_TYPE_PERSISTENT = 5,    // 持久连接
    CONNECTION_TYPE_MONITORED = 6,     // 监控连接
    CONNECTION_TYPE_PRIORITY = 7,      // 优先级连接
    CONNECTION_TYPE_CUSTOM = 8         // 自定义连接
} ConnectionType;

/**
 * 连接状态
 */
typedef enum {
    CONNECTION_STATE_INACTIVE = 0,     // 未激活
    CONNECTION_STATE_ACTIVE = 1,       // 激活
    CONNECTION_STATE_DEGRADED = 2,     // 质量下降
    CONNECTION_STATE_UNSTABLE = 3,     // 不稳定
    CONNECTION_STATE_ERROR = 4,        // 错误
    CONNECTION_STATE_CONGESTED = 5,    // 拥塞
    CONNECTION_STATE_CLOSING = 6,      // 关闭中
    CONNECTION_STATE_SECURED = 7,      // 安全状态
    CONNECTION_STATE_THROTTLED = 8     // 限流
} ConnectionState;

/**
 * 节点能力标志
 */
typedef enum {
    NODE_CAPABILITY_ROUTING = (1 << 0),           // 路由能力
    NODE_CAPABILITY_ENTANGLEMENT = (1 << 1),      // 纠缠能力
    NODE_CAPABILITY_HIGH_BANDWIDTH = (1 << 2),    // 高带宽
    NODE_CAPABILITY_ENCRYPTION = (1 << 3),        // 加密能力
    NODE_CAPABILITY_STORAGE = (1 << 4),           // 存储能力
    NODE_CAPABILITY_PROCESSING = (1 << 5),        // 处理能力
    NODE_CAPABILITY_SELF_HEALING = (1 << 6),      // 自修复能力
    NODE_CAPABILITY_MONITORING = (1 << 7),        // 监控能力
    NODE_CAPABILITY_CLUSTERING = (1 << 8),        // 集群能力
    NODE_CAPABILITY_DISCOVERY = (1 << 9)          // 发现能力
} NodeCapability;

/**
 * 网络事件类型
 */
typedef enum {
    NETWORK_EVENT_NODE_ADDED = 0,           // 节点添加
    NETWORK_EVENT_NODE_REMOVED = 1,         // 节点移除
    NETWORK_EVENT_NODE_STATE_CHANGED = 2,   // 节点状态改变
    NETWORK_EVENT_CONNECTION_ADDED = 3,     // 连接添加
    NETWORK_EVENT_CONNECTION_REMOVED = 4,   // 连接移除
    NETWORK_EVENT_CONNECTION_CHANGED = 5,   // 连接状态改变
    NETWORK_EVENT_TOPOLOGY_CHANGED = 6,     // 拓扑结构改变
    NETWORK_EVENT_NETWORK_SPLIT = 7,        // 网络分裂
    NETWORK_EVENT_NETWORK_MERGED = 8,       // 网络合并
    NETWORK_EVENT_ERROR = 9                 // 错误事件
} NetworkEventType;

/**
 * 节点元数据
 */
typedef struct {
    char* name;                        // 节点名称
    char* description;                 // 节点描述
    NodeType type;                     // 节点类型
    unsigned int capabilities;         // 节点能力标志
    char* owner;                       // 节点所有者
    char* location;                    // 节点位置
    double priority;                   // 节点优先级 (0-1)
    char* creation_time;               // 创建时间
    char* last_update_time;            // 最后更新时间
    char* tags;                        // 标签
    void* custom_data;                 // 自定义数据
} NodeMetadata;

/**
 * 网络连接
 */
typedef struct {
    unsigned int id;                   // 连接ID
    unsigned int source_node_id;       // 源节点ID
    unsigned int target_node_id;       // 目标节点ID
    ConnectionType type;               // 连接类型
    ConnectionState state;             // 连接状态
    double strength;                   // 连接强度 (0-1)
    double bandwidth;                  // 带宽
    double latency;                    // 延迟
    double stability;                  // 稳定性 (0-1)
    time_t creation_time;              // 创建时间
    time_t last_update_time;           // 最后更新时间
    ChannelReference entanglement_channel; // 关联的纠缠通道(如果有)
    void* custom_data;                 // 自定义数据
} NetworkConnection;

/**
 * 量子网络节点
 */
typedef struct {
    unsigned int id;                   // 节点ID
    NodeState state;                   // 节点状态
    NodeMetadata metadata;             // 节点元数据
    NetworkConnection** connections;   // 连接数组
    int connection_count;              // 连接数量
    int max_connections;               // 最大连接数
    double energy_level;               // 能量水平 (0-1)
    double stability;                  // 稳定性 (0-1)
    time_t creation_time;              // 创建时间
    time_t last_update_time;           // 最后更新时间
    time_t last_activity_time;         // 最后活动时间
    QuantumStateReference* node_state; // 关联的量子状态
    void* custom_data;                 // 自定义数据
} QuantumNetworkNode;

/**
 * 网络事件
 */
typedef struct {
    NetworkEventType type;             // 事件类型
    unsigned int node_id;              // 相关节点ID
    unsigned int connection_id;        // 相关连接ID
    time_t timestamp;                  // 事件时间戳
    void* event_data;                  // 事件数据
    char* description;                 // 事件描述
} NetworkEvent;

/**
 * 网络拓扑分析结果
 */
typedef struct {
    int node_count;                    // 节点总数
    int active_node_count;             // 活动节点数
    int connection_count;              // 连接总数
    int active_connection_count;       // 活动连接数
    double average_connectivity;       // 平均连接度
    double network_density;            // 网络密度
    double average_path_length;        // 平均路径长度
    int diameter;                      // 网络直径
    int cluster_count;                 // 集群数量
    double clustering_coefficient;     // 集群系数
    double network_efficiency;         // 网络效率
    double entanglement_level;         // 纠缠水平
    double* centrality_measures;       // 中心性度量
    int* node_degrees;                 // 节点度数组
    char* analysis_timestamp;          // 分析时间戳
} NetworkTopologyAnalysis;

/**
 * 节点查询条件
 */
typedef struct {
    NodeType type;                     // 节点类型
    NodeState state;                   // 节点状态
    unsigned int capabilities;         // 能力要求
    double min_energy;                 // 最低能量水平
    double min_stability;              // 最低稳定性
    char* name_pattern;                // 名称模式(支持通配符)
    char* tag_pattern;                 // 标签模式
    int max_results;                   // 最大结果数
    char* sort_by;                     // 排序字段
    int sort_ascending;                // 排序方向(1=升序，0=降序)
} NodeQueryCriteria;

/**
 * 节点查询结果
 */
typedef struct {
    QuantumNetworkNode** nodes;        // 节点数组
    int count;                         // 节点数量
    int total_matches;                 // 匹配的总数(可能大于count)
    NodeManagerError error;            // 错误码
} NodeQueryResult;

/**
 * 路由信息
 */
typedef struct {
    unsigned int source_node_id;       // 源节点ID
    unsigned int target_node_id;       // 目标节点ID
    unsigned int* path;                // 路径节点ID数组
    int path_length;                   // 路径长度
    double total_latency;              // 总延迟
    double min_bandwidth;              // 最小带宽
    double reliability;                // 可靠性
    NodeManagerError error;            // 错误码
} RouteInfo;

/**
 * 节点管理器配置
 */
typedef struct {
    int initial_capacity;              // 初始容量
    int max_capacity;                  // 最大容量
    int auto_resize;                   // 是否自动调整大小
    int enable_logging;                // 是否启用日志
    char* log_file_path;               // 日志文件路径
    int enable_auto_routing;           // 是否启用自动路由
    int enable_self_healing;           // 是否启用自修复
    int topology_update_interval;      // 拓扑更新间隔(秒)
    int connection_timeout;            // 连接超时(秒)
    int max_retry_count;               // 最大重试次数
    int default_max_connections;       // 默认最大连接数
    double default_connection_strength;// 默认连接强度
    double stability_threshold;        // 稳定性阈值
} NodeManagerConfig;

/**
 * 节点管理器
 */
typedef struct {
    QuantumNetworkNode** nodes;        // 节点数组
    int node_count;                    // 当前节点数量
    int capacity;                      // 当前容量
    NodeManagerConfig config;          // 配置
    char* manager_id;                  // 管理器ID
    FILE* log_file;                    // 日志文件
    NetworkEvent* event_queue;         // 事件队列
    int event_queue_size;              // 事件队列大小
    int event_count;                   // 事件数量
    time_t last_topology_update;       // 最后拓扑更新时间
    NetworkTopologyAnalysis* topology; // 拓扑分析结果
    EntanglementProcessor* entanglement_processor; // 纠缠处理器
    void* routing_table;               // 路由表(内部实现)
    void* mutex;                       // 互斥锁(内部实现)
} NodeManager;

/* 函数声明 */

/**
 * 初始化节点管理器
 * 
 * @param config 管理器配置
 * @param entanglement_processor 纠缠处理器
 * @return 节点管理器指针，失败时返回NULL
 */
NodeManager* initialize_node_manager(NodeManagerConfig config, EntanglementProcessor* entanglement_processor);

/**
 * 获取默认节点管理器配置
 * 
 * @return 默认配置
 */
NodeManagerConfig get_default_node_manager_config();

/**
 * 关闭节点管理器
 * 
 * @param manager 节点管理器
 */
void shutdown_node_manager(NodeManager* manager);

/**
 * 创建网络节点
 * 
 * @param manager 节点管理器
 * @param type 节点类型
 * @param name 节点名称
 * @param capabilities 节点能力
 * @return 节点ID，失败时返回0
 */
unsigned int create_network_node(NodeManager* manager, NodeType type, const char* name, unsigned int capabilities);

/**
 * 获取节点
 * 
 * @param manager 节点管理器
 * @param node_id 节点ID
 * @return 节点指针，失败时返回NULL
 */
QuantumNetworkNode* get_node(NodeManager* manager, unsigned int node_id);

/**
 * 更新节点状态
 * 
 * @param manager 节点管理器
 * @param node_id 节点ID
 * @param state 新状态
 * @return 错误码
 */
NodeManagerError update_node_state(NodeManager* manager, unsigned int node_id, NodeState state);

/**
 * 更新节点元数据
 * 
 * @param manager 节点管理器
 * @param node_id 节点ID
 * @param metadata 新元数据
 * @return 错误码
 */
NodeManagerError update_node_metadata(NodeManager* manager, unsigned int node_id, NodeMetadata metadata);

/**
 * 删除网络节点
 * 
 * @param manager 节点管理器
 * @param node_id 节点ID
 * @return 错误码
 */
NodeManagerError delete_network_node(NodeManager* manager, unsigned int node_id);

/**
 * 创建网络连接
 * 
 * @param manager 节点管理器
 * @param source_node_id 源节点ID
 * @param target_node_id 目标节点ID
 * @param type 连接类型
 * @param strength 连接强度
 * @return 连接ID，失败时返回0
 */
unsigned int create_network_connection(NodeManager* manager, unsigned int source_node_id, unsigned int target_node_id, ConnectionType type, double strength);

/**
 * 获取连接
 * 
 * @param manager 节点管理器
 * @param connection_id 连接ID
 * @return 连接指针，失败时返回NULL
 */
NetworkConnection* get_connection(NodeManager* manager, unsigned int connection_id);

/**
 * 更新连接状态
 * 
 * @param manager 节点管理器
 * @param connection_id 连接ID
 * @param state 新状态
 * @return 错误码
 */
NodeManagerError update_connection_state(NodeManager* manager, unsigned int connection_id, ConnectionState state);

/**
 * 更新连接属性
 * 
 * @param manager 节点管理器
 * @param connection_id 连接ID
 * @param strength 新强度
 * @param bandwidth 新带宽
 * @param latency 新延迟
 * @return 错误码
 */
NodeManagerError update_connection_properties(NodeManager* manager, unsigned int connection_id, double strength, double bandwidth, double latency);

/**
 * 删除网络连接
 * 
 * @param manager 节点管理器
 * @param connection_id 连接ID
 * @return 错误码
 */
NodeManagerError delete_network_connection(NodeManager* manager, unsigned int connection_id);

/**
 * 查询节点
 * 
 * @param manager 节点管理器
 * @param criteria 查询条件
 * @return 查询结果
 */
NodeQueryResult query_nodes(NodeManager* manager, NodeQueryCriteria criteria);

/**
 * 查找最短路径
 * 
 * @param manager 节点管理器
 * @param source_node_id 源节点ID
 * @param target_node_id 目标节点ID
 * @return 路由信息
 */
RouteInfo find_shortest_path(NodeManager* manager, unsigned int source_node_id, unsigned int target_node_id);

/**
 * 查找最可靠路径
 * 
 * @param manager 节点管理器
 * @param source_node_id 源节点ID
 * @param target_node_id 目标节点ID
 * @return 路由信息
 */
RouteInfo find_most_reliable_path(NodeManager* manager, unsigned int source_node_id, unsigned int target_node_id);

/**
 * 分析网络拓扑
 * 
 * @param manager 节点管理器
 * @return 拓扑分析结果，失败时返回NULL
 */
NetworkTopologyAnalysis* analyze_network_topology(NodeManager* manager);

/**
 * 获取网络事件
 * 
 * @param manager 节点管理器
 * @param event_buffer 事件缓冲区
 * @param max_events 最大事件数
 * @return 实际获取的事件数
 */
int get_network_events(NodeManager* manager, NetworkEvent* event_buffer, int max_events);

/**
 * 暂停节点
 * 
 * @param manager 节点管理器
 * @param node_id 节点ID
 * @return 错误码
 */
NodeManagerError suspend_node(NodeManager* manager, unsigned int node_id);

/**
 * 恢复节点
 * 
 * @param manager 节点管理器
 * @param node_id 节点ID
 * @return 错误码
 */
NodeManagerError resume_node(NodeManager* manager, unsigned int node_id);

/**
 * 检查节点连接性
 * 
 * @param manager 节点管理器
 * @param node_id 节点ID
 * @return 连接的节点数量，失败时返回负值
 */
int check_node_connectivity(NodeManager* manager, unsigned int node_id);

/**
 * 优化网络拓扑
 * 
 * @param manager 节点管理器
 * @param optimization_criteria 优化标准
 * @return 成功优化的连接数量，失败时返回负值
 */
int optimize_network_topology(NodeManager* manager, void* optimization_criteria);

/**
 * 创建纠缠连接
 * 
 * @param manager 节点管理器
 * @param source_node_id 源节点ID
 * @param target_node_id 目标节点ID
 * @param entanglement_strength 纠缠强度
 * @return 连接ID，失败时返回0
 */
unsigned int create_entanglement_connection(NodeManager* manager, unsigned int source_node_id, unsigned int target_node_id, double entanglement_strength);

/**
 * 获取节点健康状态
 * 
 * @param manager 节点管理器
 * @param node_id 节点ID
 * @return 健康度(0-1)，失败时返回负值
 */
double get_node_health(NodeManager* manager, unsigned int node_id);

/**
 * 获取网络健康状态
 * 
 * @param manager 节点管理器
 * @return 网络健康度(0-1)，失败时返回负值
 */
double get_network_health(NodeManager* manager);

/**
 * 释放查询结果资源
 * 
 * @param result 查询结果
 */
void free_node_query_result(NodeQueryResult* result);

/**
 * 释放路由信息资源
 * 
 * @param route_info 路由信息
 */
void free_route_info(RouteInfo* route_info);

/**
 * 释放拓扑分析结果资源
 * 
 * @param analysis 拓扑分析结果
 */
void free_topology_analysis(NetworkTopologyAnalysis* analysis);

/**
 * 获取节点管理器错误消息
 * 
 * @param error 错误码
 * @return 错误消息
 */
const char* get_node_manager_error_message(NodeManagerError error);

#endif /* QENTL_NODE_MANAGER_H */ 