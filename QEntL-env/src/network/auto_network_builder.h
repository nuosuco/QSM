/*
 * 自动网络构建模块头文件
 * 负责实现节点自动激活和量子网络自动构建
 */

// 量子基因编码
// QG-SRC-AUTONET-H-A1B1

#ifndef AUTO_NETWORK_BUILDER_H
#define AUTO_NETWORK_BUILDER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../quantum_state.h"
#include "../quantum_entanglement.h"
#include "../quantum_network.h"

// 网络构建策略
typedef enum {
    NETWORK_STRATEGY_FULLY_CONNECTED,  // 完全连接网络
    NETWORK_STRATEGY_STAR,             // 星形网络
    NETWORK_STRATEGY_RING,             // 环形网络
    NETWORK_STRATEGY_MESH,             // 网格网络
    NETWORK_STRATEGY_HIERARCHICAL,     // 层次网络
    NETWORK_STRATEGY_ADAPTIVE          // 自适应网络
} NetworkBuildStrategy;

// 节点发现方法
typedef enum {
    DISCOVERY_METHOD_BROADCAST,       // 广播发现
    DISCOVERY_METHOD_MULTICAST,       // 组播发现
    DISCOVERY_METHOD_CENTRAL_REGISTRY, // 中央注册表
    DISCOVERY_METHOD_PEER_EXCHANGE,   // 对等交换
    DISCOVERY_METHOD_QUANTUM_RESONANCE // 量子共振
} NodeDiscoveryMethod;

// 网络构建配置
typedef struct {
    NetworkBuildStrategy strategy;     // 构建策略
    NodeDiscoveryMethod discovery;     // 发现方法
    int max_nodes;                     // 最大节点数量
    int max_connections_per_node;      // 每个节点的最大连接数
    double min_entanglement_strength;  // 最小纠缠强度
    int auto_rebuild_interval;         // 自动重建间隔（秒）
    int activate_all_nodes;            // 是否自动激活所有节点
} NetworkBuildConfig;

// 网络构建器
typedef struct {
    char id[64];                       // 构建器ID
    NetworkBuildConfig config;         // 配置
    time_t last_build_time;            // 上次构建时间
    int total_networks_built;          // 已构建网络总数
    int active_nodes_count;            // 活跃节点数量
    int inactive_nodes_count;          // 非活跃节点数量
} AutoNetworkBuilder;

// 创建网络构建器
AutoNetworkBuilder* auto_network_builder_create(const char* id);

// 销毁网络构建器
void auto_network_builder_destroy(AutoNetworkBuilder* builder);

// 配置网络构建器
void auto_network_builder_configure(AutoNetworkBuilder* builder, NetworkBuildConfig* config);

// 从现有节点自动构建网络
EntanglementNetwork* auto_network_builder_build_network(
    AutoNetworkBuilder* builder, 
    const char* network_id, 
    QuantumNetworkNode** nodes, 
    int node_count
);

// 发现网络中的节点
int auto_network_builder_discover_nodes(
    AutoNetworkBuilder* builder,
    QuantumNetworkNode** nodes_buffer,
    int buffer_size
);

// 激活所有发现的节点
int auto_network_builder_activate_all_nodes(
    AutoNetworkBuilder* builder,
    QuantumNetworkNode** nodes,
    int node_count
);

// 将量子状态添加到自动构建的网络
int auto_network_builder_add_state_to_network(
    AutoNetworkBuilder* builder,
    EntanglementNetwork* network,
    QuantumState* state
);

// 检查和重建网络（如有必要）
int auto_network_builder_check_and_rebuild(
    AutoNetworkBuilder* builder,
    EntanglementNetwork* network
);

// 获取网络统计信息
void auto_network_builder_get_stats(
    AutoNetworkBuilder* builder,
    int* active_nodes,
    int* inactive_nodes,
    int* total_networks
);

#endif /* AUTO_NETWORK_BUILDER_H */ 