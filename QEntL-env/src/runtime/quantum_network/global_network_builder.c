/**
 * QEntL量子网络全局构建器实现
 * 
 * 量子基因编码: QG-RUNTIME-NETBLD-SRC-G2J5-1713051200
 * 
 * @文件: global_network_builder.c
 * @描述: 实现QEntL运行时的量子网络全局构建器功能
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-18
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 网络构建器支持自动探测和连接网络节点
 * - 支持跨设备量子网络拓扑结构的构建和优化
 */

#include "global_network_builder.h"
#include "node_manager.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

/**
 * 连接结构
 */
typedef struct Connection {
    QNetworkNode* node1;              /* 第一个节点 */
    QNetworkNode* node2;              /* 第二个节点 */
    double strength;                  /* 连接强度 */
    time_t creation_time;             /* 创建时间 */
    int is_active;                    /* 是否活跃 */
} Connection;

/**
 * 网络拓扑结构
 */
struct NetworkTopology {
    NetworkTopologyType type;         /* 拓扑类型 */
    QNetworkNode** nodes;             /* 节点数组 */
    int node_count;                   /* 节点数量 */
    int node_capacity;                /* 节点容量 */
    Connection** connections;         /* 连接数组 */
    int connection_count;             /* 连接数量 */
    int connection_capacity;          /* 连接容量 */
    double reliability;               /* 可靠性指标 */
    double efficiency;                /* 效率指标 */
};

/**
 * 回调条目结构
 */
typedef struct ConfirmCallbackEntry {
    ConnectionConfirmCallback callback; /* 回调函数 */
    void* user_data;                   /* 用户数据 */
} ConfirmCallbackEntry;

typedef struct CompleteCallbackEntry {
    NetworkBuildCompleteCallback callback; /* 回调函数 */
    void* user_data;                      /* 用户数据 */
} CompleteCallbackEntry;

/**
 * 全局网络构建器内部结构
 */
struct GlobalNetworkBuilder {
    NodeActivator* node_activator;      /* 节点激活器 */
    EventSystem* event_system;          /* 事件系统 */
    EventHandler* event_handler;        /* 事件处理器 */
    
    NetworkBuilderConfig config;        /* 构建配置 */
    NetworkTopology* topology;          /* 网络拓扑 */
    
    QNetworkNode** seed_nodes;          /* 种子节点数组 */
    int seed_node_count;                /* 种子节点数量 */
    int seed_node_capacity;             /* 种子节点容量 */
    
    ConfirmCallbackEntry* confirm_callbacks;  /* 确认回调数组 */
    int confirm_callback_count;               /* 确认回调数量 */
    int confirm_callback_capacity;            /* 确认回调容量 */
    
    CompleteCallbackEntry* complete_callbacks; /* 完成回调数组 */
    int complete_callback_count;              /* 完成回调数量 */
    int complete_callback_capacity;           /* 完成回调容量 */
    
    int is_building;                    /* 是否正在构建 */
    time_t last_process_time;           /* 上次处理时间 */
    
    NetworkBuildingStats stats;         /* 构建统计 */
};

/* 内部函数声明 */
static int execute_connection_callbacks(GlobalNetworkBuilder* builder, 
                                      QNetworkNode* node1, 
                                      QNetworkNode* node2, 
                                      ConnectionPriority priority);
static int execute_build_complete_callbacks(GlobalNetworkBuilder* builder, 
                                         int success, 
                                         QNetworkNode** nodes, 
                                         int node_count);
static void update_building_stats(GlobalNetworkBuilder* builder);
static ConnectionPriority calculate_connection_priority(GlobalNetworkBuilder* builder, 
                                                     QNetworkNode* node1, 
                                                     QNetworkNode* node2);
static Connection* find_connection(NetworkTopology* topology, 
                                QNetworkNode* node1, 
                                QNetworkNode* node2);
static int is_node_in_topology(NetworkTopology* topology, QNetworkNode* node);
static int build_connection(GlobalNetworkBuilder* builder, 
                         QNetworkNode* node1, 
                         QNetworkNode* node2, 
                         double strength);
static void on_network_event(QEntLEvent* event, GlobalNetworkBuilder* builder);
static double calculate_connection_strength(QNetworkNode* node1, QNetworkNode* node2);
static double calculate_network_stability(NetworkTopology* topology);

/**
 * 创建默认配置
 */
static NetworkBuilderConfig create_default_config() {
    NetworkBuilderConfig config;
    
    config.build_mode = NETWORK_BUILD_MODE_AUTOMATIC;
    config.topology_type = NETWORK_TOPOLOGY_MESH;
    config.auto_discovery_enabled = 1;
    config.max_discovery_depth = 3;
    config.max_connections_per_node = 10;
    config.min_connection_strength = 0.3;
    config.enable_connection_optimization = 1;
    config.enable_fault_tolerance = 1;
    config.connection_retry_count = 3;
    config.connection_timeout = 10.0;
    config.network_stability_threshold = 0.6;
    config.custom_config = NULL;
    
    return config;
}

/**
 * 创建全局网络构建器
 */
GlobalNetworkBuilder* global_network_builder_create(NodeActivator* node_activator, 
                                                  EventSystem* event_system) {
    if (!node_activator || !event_system) {
        fprintf(stderr, "错误: 创建网络构建器需要有效的节点激活器和事件系统\n");
        return NULL;
    }
    
    GlobalNetworkBuilder* builder = (GlobalNetworkBuilder*)malloc(sizeof(GlobalNetworkBuilder));
    if (!builder) {
        fprintf(stderr, "错误: 无法分配网络构建器内存\n");
        return NULL;
    }
    
    /* 初始化基本字段 */
    builder->node_activator = node_activator;
    builder->event_system = event_system;
    builder->is_building = 0;
    builder->last_process_time = time(NULL);
    
    /* 创建网络拓扑 */
    builder->topology = network_topology_create(NETWORK_TOPOLOGY_MESH);
    if (!builder->topology) {
        free(builder);
        fprintf(stderr, "错误: 无法创建网络拓扑\n");
        return NULL;
    }
    
    /* 初始化种子节点数组 */
    builder->seed_node_capacity = 8;
    builder->seed_nodes = (QNetworkNode**)malloc(builder->seed_node_capacity * sizeof(QNetworkNode*));
    if (!builder->seed_nodes) {
        network_topology_destroy(builder->topology);
        free(builder);
        fprintf(stderr, "错误: 无法分配种子节点数组内存\n");
        return NULL;
    }
    builder->seed_node_count = 0;
    
    /* 初始化回调数组 */
    builder->confirm_callback_capacity = 4;
    builder->confirm_callbacks = (ConfirmCallbackEntry*)malloc(
        builder->confirm_callback_capacity * sizeof(ConfirmCallbackEntry));
    if (!builder->confirm_callbacks) {
        free(builder->seed_nodes);
        network_topology_destroy(builder->topology);
        free(builder);
        fprintf(stderr, "错误: 无法分配确认回调数组内存\n");
        return NULL;
    }
    builder->confirm_callback_count = 0;
    
    builder->complete_callback_capacity = 4;
    builder->complete_callbacks = (CompleteCallbackEntry*)malloc(
        builder->complete_callback_capacity * sizeof(CompleteCallbackEntry));
    if (!builder->complete_callbacks) {
        free(builder->confirm_callbacks);
        free(builder->seed_nodes);
        network_topology_destroy(builder->topology);
        free(builder);
        fprintf(stderr, "错误: 无法分配完成回调数组内存\n");
        return NULL;
    }
    builder->complete_callback_count = 0;
    
    /* 设置默认配置 */
    builder->config = create_default_config();
    
    /* 注册事件处理器 */
    builder->event_handler = event_system_add_handler(event_system, 
                                                   global_network_builder_event_handler, 
                                                   builder, 
                                                   20, /* 优先级 */
                                                   (1 << EVENT_SYSTEM_STARTUP) | 
                                                   (1 << EVENT_NETWORK_CONNECTION) |
                                                   (1 << EVENT_NETWORK_DISCONNECTION) |
                                                   (1 << EVENT_NODE_DISCOVERED));
    
    /* 初始化统计信息 */
    memset(&builder->stats, 0, sizeof(NetworkBuildingStats));
    builder->stats.build_start_time = time(NULL);
    builder->stats.network_stability = 1.0; /* 初始假设网络很稳定 */
    
    printf("量子网络全局构建器已创建\n");
    
    return builder;
}

/**
 * 销毁全局网络构建器
 */
void global_network_builder_destroy(GlobalNetworkBuilder* builder) {
    if (!builder) return;
    
    /* 停止网络构建 */
    if (builder->is_building) {
        global_network_builder_stop(builder);
    }
    
    /* 移除事件处理器 */
    if (builder->event_system && builder->event_handler) {
        event_system_remove_handler(builder->event_system, builder->event_handler);
    }
    
    /* 释放网络拓扑 */
    if (builder->topology) {
        network_topology_destroy(builder->topology);
    }
    
    /* 释放种子节点数组 */
    free(builder->seed_nodes);
    
    /* 释放回调数组 */
    free(builder->confirm_callbacks);
    free(builder->complete_callbacks);
    
    /* 释放构建器本身 */
    free(builder);
    
    printf("量子网络全局构建器已销毁\n");
}

/**
 * 设置网络构建配置
 */
int global_network_builder_set_config(GlobalNetworkBuilder* builder, NetworkBuilderConfig config) {
    if (!builder) return 0;
    
    builder->config = config;
    return 1;
}

/**
 * 获取网络构建配置
 */
NetworkBuilderConfig global_network_builder_get_config(GlobalNetworkBuilder* builder) {
    NetworkBuilderConfig empty_config = {0};
    
    if (!builder) return empty_config;
    
    return builder->config;
}

/**
 * 注册连接确认回调
 */
int global_network_builder_register_confirm_callback(GlobalNetworkBuilder* builder, 
                                                  ConnectionConfirmCallback callback, 
                                                  void* user_data) {
    if (!builder || !callback) return 0;
    
    /* 检查是否需要扩展回调数组 */
    if (builder->confirm_callback_count >= builder->confirm_callback_capacity) {
        int new_capacity = builder->confirm_callback_capacity * 2;
        ConfirmCallbackEntry* new_callbacks = (ConfirmCallbackEntry*)realloc(
            builder->confirm_callbacks, 
            new_capacity * sizeof(ConfirmCallbackEntry));
        
        if (!new_callbacks) {
            fprintf(stderr, "错误: 无法扩展确认回调数组\n");
            return 0;
        }
        
        builder->confirm_callbacks = new_callbacks;
        builder->confirm_callback_capacity = new_capacity;
    }
    
    /* 添加回调 */
    builder->confirm_callbacks[builder->confirm_callback_count].callback = callback;
    builder->confirm_callbacks[builder->confirm_callback_count].user_data = user_data;
    builder->confirm_callback_count++;
    
    return 1;
}

/**
 * 注册构建完成回调
 */
int global_network_builder_register_complete_callback(GlobalNetworkBuilder* builder, 
                                                   NetworkBuildCompleteCallback callback, 
                                                   void* user_data) {
    if (!builder || !callback) return 0;
    
    /* 检查是否需要扩展回调数组 */
    if (builder->complete_callback_count >= builder->complete_callback_capacity) {
        int new_capacity = builder->complete_callback_capacity * 2;
        CompleteCallbackEntry* new_callbacks = (CompleteCallbackEntry*)realloc(
            builder->complete_callbacks, 
            new_capacity * sizeof(CompleteCallbackEntry));
        
        if (!new_callbacks) {
            fprintf(stderr, "错误: 无法扩展完成回调数组\n");
            return 0;
        }
        
        builder->complete_callbacks = new_callbacks;
        builder->complete_callback_capacity = new_capacity;
    }
    
    /* 添加回调 */
    builder->complete_callbacks[builder->complete_callback_count].callback = callback;
    builder->complete_callbacks[builder->complete_callback_count].user_data = user_data;
    builder->complete_callback_count++;
    
    return 1;
}

/**
 * 启动网络构建
 */
int global_network_builder_start(GlobalNetworkBuilder* builder) {
    if (!builder) return 0;
    
    if (builder->is_building) return 1;  /* 已经在构建 */
    
    builder->is_building = 1;
    builder->stats.build_start_time = time(NULL);
    builder->stats.total_build_attempts++;
    
    printf("量子网络构建已启动\n");
    
    return 1;
}

/**
 * 停止网络构建
 */
int global_network_builder_stop(GlobalNetworkBuilder* builder) {
    if (!builder) return 0;
    
    if (!builder->is_building) return 1;  /* 已经停止 */
    
    builder->is_building = 0;
    
    printf("量子网络构建已停止\n");
    
    return 1;
}

/**
 * 获取网络构建统计
 */
NetworkBuildingStats global_network_builder_get_stats(GlobalNetworkBuilder* builder) {
    NetworkBuildingStats empty_stats = {0};
    
    if (!builder) return empty_stats;
    
    /* 更新统计信息 */
    update_building_stats(builder);
    
    return builder->stats;
}

/**
 * 添加种子节点
 */
int global_network_builder_add_seed_node(GlobalNetworkBuilder* builder, QNetworkNode* node) {
    if (!builder || !node) return 0;
    
    /* 检查节点是否已经存在 */
    for (int i = 0; i < builder->seed_node_count; i++) {
        if (builder->seed_nodes[i] == node) {
            return 1;  /* 节点已存在 */
        }
    }
    
    /* 检查是否需要扩展种子节点数组 */
    if (builder->seed_node_count >= builder->seed_node_capacity) {
        int new_capacity = builder->seed_node_capacity * 2;
        QNetworkNode** new_nodes = (QNetworkNode**)realloc(
            builder->seed_nodes, 
            new_capacity * sizeof(QNetworkNode*));
        
        if (!new_nodes) {
            fprintf(stderr, "错误: 无法扩展种子节点数组\n");
            return 0;
        }
        
        builder->seed_nodes = new_nodes;
        builder->seed_node_capacity = new_capacity;
    }
    
    /* 添加种子节点 */
    builder->seed_nodes[builder->seed_node_count++] = node;
    
    /* 同时添加到网络拓扑 */
    network_topology_add_node(builder->topology, node);
    
    /* 更新统计 */
    builder->stats.nodes_discovered++;
    
    return 1;
}

/**
 * 获取当前网络拓扑
 */
NetworkTopology* global_network_builder_get_topology(GlobalNetworkBuilder* builder) {
    if (!builder) return NULL;
    
    return builder->topology;
}

/**
 * 设置网络拓扑类型
 */
int global_network_builder_set_topology_type(GlobalNetworkBuilder* builder, NetworkTopologyType type) {
    if (!builder || !builder->topology) return 0;
    
    /* 更新配置 */
    builder->config.topology_type = type;
    
    /* 更新拓扑类型 */
    builder->topology->type = type;
    
    /* 如果已经有节点，可能需要重新组织网络 */
    if (builder->topology->node_count > 0) {
        /* TODO: 实现根据新拓扑类型重新组织网络的逻辑 */
        builder->stats.topology_changes++;
    }
    
    return 1;
}

/**
 * 优化网络拓扑
 */
int global_network_builder_optimize_topology(GlobalNetworkBuilder* builder, int optimization_level) {
    if (!builder || !builder->topology) return 0;
    if (optimization_level < 0 || optimization_level > 3) return 0;
    
    printf("正在优化网络拓扑 (级别 %d)...\n", optimization_level);
    
    /* 根据优化级别执行不同程度的优化 */
    switch (optimization_level) {
        case 0:
            /* 最小优化 - 仅移除重复连接 */
            /* TODO: 实现移除重复连接的逻辑 */
            break;
            
        case 1:
            /* 基本优化 - 移除重复连接，调整弱连接 */
            /* TODO: 实现基本优化逻辑 */
            break;
            
        case 2:
            /* 标准优化 - 重新平衡网络，优化路径 */
            /* TODO: 实现标准优化逻辑 */
            break;
            
        case 3:
            /* 完全优化 - 重构网络以获得最佳性能 */
            /* TODO: 实现完全优化逻辑 */
            break;
    }
    
    /* 更新网络稳定性 */
    builder->stats.network_stability = calculate_network_stability(builder->topology);
    
    return 1;
}

/**
 * 手动连接两个节点
 */
int global_network_builder_connect_nodes(GlobalNetworkBuilder* builder, 
                                      QNetworkNode* node1, 
                                      QNetworkNode* node2, 
                                      double strength) {
    if (!builder || !node1 || !node2) return 0;
    if (node1 == node2) return 0;  /* 不能自连接 */
    
    /* 检查连接强度范围 */
    if (strength < 0.0) strength = 0.0;
    if (strength > 1.0) strength = 1.0;
    
    /* 确保两个节点都在拓扑中 */
    if (!is_node_in_topology(builder->topology, node1)) {
        network_topology_add_node(builder->topology, node1);
    }
    
    if (!is_node_in_topology(builder->topology, node2)) {
        network_topology_add_node(builder->topology, node2);
    }
    
    /* 检查是否已经存在连接 */
    Connection* existing = find_connection(builder->topology, node1, node2);
    if (existing) {
        /* 更新连接强度 */
        existing->strength = strength;
        return 1;
    }
    
    /* 执行连接确认回调 */
    ConnectionPriority priority = calculate_connection_priority(builder, node1, node2);
    if (builder->config.build_mode != NETWORK_BUILD_MODE_AUTOMATIC) {
        /* 对于非自动模式，需要确认连接 */
        if (!execute_connection_callbacks(builder, node1, node2, priority)) {
            return 0;  /* 连接被拒绝 */
        }
    }
    
    /* 建立连接 */
    return build_connection(builder, node1, node2, strength);
}

/**
 * 断开节点连接
 */
int global_network_builder_disconnect_nodes(GlobalNetworkBuilder* builder, 
                                         QNetworkNode* node1, 
                                         QNetworkNode* node2) {
    if (!builder || !builder->topology || !node1 || !node2) return 0;
    
    /* 查找连接 */
    Connection* connection = find_connection(builder->topology, node1, node2);
    if (!connection) return 0;  /* 连接不存在 */
    
    /* 在连接数组中找到索引 */
    int index = -1;
    for (int i = 0; i < builder->topology->connection_count; i++) {
        if (builder->topology->connections[i] == connection) {
            index = i;
            break;
        }
    }
    
    if (index == -1) return 0;  /* 连接不在数组中 */
    
    /* 释放连接 */
    free(connection);
    
    /* 移除连接并重整数组 */
    for (int i = index; i < builder->topology->connection_count - 1; i++) {
        builder->topology->connections[i] = builder->topology->connections[i + 1];
    }
    builder->topology->connection_count--;
    
    /* 更新统计 */
    builder->stats.network_stability = calculate_network_stability(builder->topology);
    
    return 1;
}

/**
 * 探测网络中的所有节点
 */
int global_network_builder_discover_nodes(GlobalNetworkBuilder* builder, 
                                       int max_depth, 
                                       QNetworkNode*** nodes, 
                                       int* node_count) {
    if (!builder || !nodes || !node_count) return 0;
    
    /* 设置最大深度 */
    if (max_depth <= 0) {
        max_depth = builder->config.max_discovery_depth;
    }
    
    /* 从种子节点开始探索网络 */
    /* 这里实现简化版本，实际应该进行广度优先或深度优先搜索 */
    *node_count = builder->topology->node_count;
    *nodes = (QNetworkNode**)malloc(*node_count * sizeof(QNetworkNode*));
    
    if (!*nodes) {
        fprintf(stderr, "错误: 无法分配节点数组内存\n");
        return 0;
    }
    
    /* 复制节点列表 */
    for (int i = 0; i < *node_count; i++) {
        (*nodes)[i] = builder->topology->nodes[i];
    }
    
    /* 更新统计 */
    builder->stats.nodes_discovered = *node_count;
    
    return 1;
}

/**
 * 处理网络构建周期
 */
int global_network_builder_process_cycle(GlobalNetworkBuilder* builder) {
    if (!builder || !builder->is_building) return 0;
    
    int connections_built = 0;
    
    /* 处理自动发现 */
    if (builder->config.auto_discovery_enabled) {
        /* TODO: 实现自动发现逻辑 */
    }
    
    /* 对于网状拓扑，尝试在所有节点之间建立连接 */
    if (builder->topology->type == NETWORK_TOPOLOGY_MESH) {
        for (int i = 0; i < builder->topology->node_count; i++) {
            for (int j = i + 1; j < builder->topology->node_count; j++) {
                QNetworkNode* node1 = builder->topology->nodes[i];
                QNetworkNode* node2 = builder->topology->nodes[j];
                
                /* 检查连接是否已存在 */
                if (find_connection(builder->topology, node1, node2)) {
                    continue;
                }
                
                /* 计算连接强度 */
                double strength = calculate_connection_strength(node1, node2);
                
                /* 检查是否满足最小强度要求 */
                if (strength < builder->config.min_connection_strength) {
                    continue;
                }
                
                /* 执行连接确认回调 */
                ConnectionPriority priority = calculate_connection_priority(builder, node1, node2);
                if (builder->config.build_mode != NETWORK_BUILD_MODE_AUTOMATIC) {
                    /* 对于非自动模式，需要确认连接 */
                    if (!execute_connection_callbacks(builder, node1, node2, priority)) {
                        continue;  /* 连接被拒绝 */
                    }
                }
                
                /* 建立连接 */
                if (build_connection(builder, node1, node2, strength)) {
                    connections_built++;
                }
            }
        }
    } else if (builder->topology->type == NETWORK_TOPOLOGY_STAR) {
        /* 星型拓扑逻辑 */
        /* TODO: 实现星型拓扑构建逻辑 */
    } else if (builder->topology->type == NETWORK_TOPOLOGY_RING) {
        /* 环形拓扑逻辑 */
        /* TODO: 实现环形拓扑构建逻辑 */
    } else {
        /* 其他拓扑类型 */
        /* TODO: 实现其他拓扑类型的构建逻辑 */
    }
    
    /* 更新统计信息 */
    builder->stats.last_build_time = time(NULL);
    builder->stats.connections_established += connections_built;
    builder->stats.network_stability = calculate_network_stability(builder->topology);
    
    /* 检查是否构建完成 */
    if (connections_built == 0) {
        /* 无新连接建立，可能构建已完成 */
        execute_build_complete_callbacks(builder, 1, builder->topology->nodes, builder->topology->node_count);
        builder->stats.successful_builds++;
    }
    
    return connections_built;
}

/**
 * 检测和修复网络问题
 */
int global_network_builder_repair_network(GlobalNetworkBuilder* builder) {
    if (!builder || !builder->topology) return 0;
    
    int repaired_issues = 0;
    
    /* 检查和修复断开的连接 */
    for (int i = 0; i < builder->topology->connection_count; i++) {
        Connection* conn = builder->topology->connections[i];
        
        /* 检查连接状态 */
        if (!conn->is_active) {
            /* 尝试重新激活连接 */
            conn->is_active = 1;
            repaired_issues++;
        }
    }
    
    /* 检查孤立节点 */
    for (int i = 0; i < builder->topology->node_count; i++) {
        QNetworkNode* node = builder->topology->nodes[i];
        int has_connections = 0;
        
        /* 检查节点是否有连接 */
        for (int j = 0; j < builder->topology->connection_count; j++) {
            Connection* conn = builder->topology->connections[j];
            if (conn->node1 == node || conn->node2 == node) {
                has_connections = 1;
                break;
            }
        }
        
        if (!has_connections) {
            /* 孤立节点，尝试连接到最近的节点 */
            double best_strength = 0.0;
            QNetworkNode* best_node = NULL;
            
            for (int j = 0; j < builder->topology->node_count; j++) {
                if (i == j) continue;
                
                QNetworkNode* other = builder->topology->nodes[j];
                double strength = calculate_connection_strength(node, other);
                
                if (strength > best_strength) {
                    best_strength = strength;
                    best_node = other;
                }
            }
            
            if (best_node && best_strength >= builder->config.min_connection_strength) {
                if (build_connection(builder, node, best_node, best_strength)) {
                    repaired_issues++;
                }
            }
        }
    }
    
    /* 更新统计 */
    if (repaired_issues > 0) {
        builder->stats.network_stability = calculate_network_stability(builder->topology);
    }
    
    return repaired_issues;
}

/**
 * 将当前网络拓扑保存到文件
 */
int global_network_builder_save_topology(GlobalNetworkBuilder* builder, const char* filename) {
    if (!builder || !builder->topology || !filename) return 0;
    
    FILE* file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "错误: 无法打开文件 %s 进行写入\n", filename);
        return 0;
    }
    
    /* 写入拓扑元数据 */
    fprintf(file, "QEntL-Network-Topology-v1.0\n");
    fprintf(file, "Type: %d\n", builder->topology->type);
    fprintf(file, "NodeCount: %d\n", builder->topology->node_count);
    fprintf(file, "ConnectionCount: %d\n", builder->topology->connection_count);
    fprintf(file, "Reliability: %f\n", builder->topology->reliability);
    fprintf(file, "Efficiency: %f\n", builder->topology->efficiency);
    fprintf(file, "\n");
    
    /* 写入节点信息 */
    fprintf(file, "[Nodes]\n");
    for (int i = 0; i < builder->topology->node_count; i++) {
        QNetworkNode* node = builder->topology->nodes[i];
        fprintf(file, "Node %d: ID=%s, Type=%d\n", i, node->id, node->type);
    }
    fprintf(file, "\n");
    
    /* 写入连接信息 */
    fprintf(file, "[Connections]\n");
    for (int i = 0; i < builder->topology->connection_count; i++) {
        Connection* conn = builder->topology->connections[i];
        int index1 = -1, index2 = -1;
        
        /* 查找节点索引 */
        for (int j = 0; j < builder->topology->node_count; j++) {
            if (builder->topology->nodes[j] == conn->node1) index1 = j;
            if (builder->topology->nodes[j] == conn->node2) index2 = j;
        }
        
        fprintf(file, "Connection %d: Node1=%d, Node2=%d, Strength=%f, Active=%d\n",
                i, index1, index2, conn->strength, conn->is_active);
    }
    
    fclose(file);
    printf("网络拓扑已保存到文件 %s\n", filename);
    
    return 1;
}

/**
 * 从文件加载网络拓扑
 */
int global_network_builder_load_topology(GlobalNetworkBuilder* builder, const char* filename) {
    if (!builder || !filename) return 0;
    
    /* TODO: 实现从文件加载拓扑的逻辑 */
    /* 这是一个复杂的操作，需要解析文件，构建节点和连接 */
    
    printf("警告: 从文件加载网络拓扑功能尚未实现\n");
    
    return 0;
}

/**
 * 网络构建器事件处理函数
 */
void global_network_builder_event_handler(QEntLEvent* event, void* user_data) {
    GlobalNetworkBuilder* builder = (GlobalNetworkBuilder*)user_data;
    if (!builder || !event) return;
    
    /* 处理事件 */
    on_network_event(event, builder);
}

/**
 * 网络拓扑API实现
 */

/**
 * 创建网络拓扑
 */
NetworkTopology* network_topology_create(NetworkTopologyType type) {
    NetworkTopology* topology = (NetworkTopology*)malloc(sizeof(NetworkTopology));
    if (!topology) {
        fprintf(stderr, "错误: 无法分配网络拓扑内存\n");
        return NULL;
    }
    
    /* 初始化节点数组 */
    topology->node_capacity = 16;
    topology->nodes = (QNetworkNode**)malloc(topology->node_capacity * sizeof(QNetworkNode*));
    if (!topology->nodes) {
        free(topology);
        fprintf(stderr, "错误: 无法分配节点数组内存\n");
        return NULL;
    }
    topology->node_count = 0;
    
    /* 初始化连接数组 */
    topology->connection_capacity = 32;
    topology->connections = (Connection**)malloc(topology->connection_capacity * sizeof(Connection*));
    if (!topology->connections) {
        free(topology->nodes);
        free(topology);
        fprintf(stderr, "错误: 无法分配连接数组内存\n");
        return NULL;
    }
    topology->connection_count = 0;
    
    /* 设置拓扑类型和初始指标 */
    topology->type = type;
    topology->reliability = 1.0;
    topology->efficiency = 1.0;
    
    return topology;
}

/**
 * 销毁网络拓扑
 */
void network_topology_destroy(NetworkTopology* topology) {
    if (!topology) return;
    
    /* 释放连接 */
    for (int i = 0; i < topology->connection_count; i++) {
        free(topology->connections[i]);
    }
    free(topology->connections);
    
    /* 释放节点数组 */
    free(topology->nodes);
    
    /* 释放拓扑本身 */
    free(topology);
}

/**
 * 添加节点到拓扑
 */
int network_topology_add_node(NetworkTopology* topology, QNetworkNode* node) {
    if (!topology || !node) return 0;
    
    /* 检查节点是否已存在 */
    if (is_node_in_topology(topology, node)) {
        return 1;  /* 节点已存在 */
    }
    
    /* 检查是否需要扩展节点数组 */
    if (topology->node_count >= topology->node_capacity) {
        int new_capacity = topology->node_capacity * 2;
        QNetworkNode** new_nodes = (QNetworkNode**)realloc(
            topology->nodes, 
            new_capacity * sizeof(QNetworkNode*));
        
        if (!new_nodes) {
            fprintf(stderr, "错误: 无法扩展节点数组\n");
            return 0;
        }
        
        topology->nodes = new_nodes;
        topology->node_capacity = new_capacity;
    }
    
    /* 添加节点 */
    topology->nodes[topology->node_count++] = node;
    
    return 1;
}

/**
 * 添加连接到拓扑
 */
int network_topology_add_connection(NetworkTopology* topology, 
                                 QNetworkNode* node1, 
                                 QNetworkNode* node2, 
                                 double strength) {
    if (!topology || !node1 || !node2) return 0;
    if (node1 == node2) return 0;  /* 不能自连接 */
    
    /* 检查连接是否已存在 */
    if (find_connection(topology, node1, node2)) {
        return 0;  /* 连接已存在 */
    }
    
    /* 确保两个节点都在拓扑中 */
    if (!is_node_in_topology(topology, node1)) {
        network_topology_add_node(topology, node1);
    }
    
    if (!is_node_in_topology(topology, node2)) {
        network_topology_add_node(topology, node2);
    }
    
    /* 检查是否需要扩展连接数组 */
    if (topology->connection_count >= topology->connection_capacity) {
        int new_capacity = topology->connection_capacity * 2;
        Connection** new_connections = (Connection**)realloc(
            topology->connections, 
            new_capacity * sizeof(Connection*));
        
        if (!new_connections) {
            fprintf(stderr, "错误: 无法扩展连接数组\n");
            return 0;
        }
        
        topology->connections = new_connections;
        topology->connection_capacity = new_capacity;
    }
    
    /* 创建新连接 */
    Connection* conn = (Connection*)malloc(sizeof(Connection));
    if (!conn) {
        fprintf(stderr, "错误: 无法分配连接内存\n");
        return 0;
    }
    
    /* 初始化连接 */
    conn->node1 = node1;
    conn->node2 = node2;
    conn->strength = strength;
    conn->creation_time = time(NULL);
    conn->is_active = 1;
    
    /* 添加连接 */
    topology->connections[topology->connection_count++] = conn;
    
    return 1;
} 