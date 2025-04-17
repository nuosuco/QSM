/**
 * 量子网络节点管理器实现文件
 * 
 * 该文件实现了量子网络节点管理器的功能，负责管理量子网络中的节点及其连接。
 *
 * @file node_manager.c
 * @version 1.0
 * @date 2024-05-15
 */

#include "node_manager.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <math.h>

#define DEFAULT_EVENT_QUEUE_SIZE 100
#define DEFAULT_MAX_PATH_LENGTH 16

/* 内部辅助函数声明 */
static char* generate_manager_id();
static void log_manager_action(NodeManager* manager, const char* action, const char* details);
static int find_node_index(NodeManager* manager, unsigned int node_id);
static NetworkConnection* find_connection(NodeManager* manager, unsigned int connection_id);
static int find_connection_index(QuantumNetworkNode* node, unsigned int connection_id);
static void free_node_resources(QuantumNetworkNode* node);
static void free_connection_resources(NetworkConnection* connection);
static int validate_node_state_transition(NodeState current_state, NodeState new_state);
static int validate_connection_state_transition(ConnectionState current_state, ConnectionState new_state);
static void queue_network_event(NodeManager* manager, NetworkEventType type, unsigned int node_id, unsigned int connection_id, void* event_data, const char* description);
static NodeManagerError resize_node_array(NodeManager* manager);
static char* get_current_timestamp();
static unsigned int generate_unique_id();
static void update_node_energy(QuantumNetworkNode* node);
static void update_connection_stability(NetworkConnection* connection);
static void cleanup_events(NodeManager* manager);

/**
 * 初始化节点管理器
 */
NodeManager* initialize_node_manager(NodeManagerConfig config, EntanglementProcessor* entanglement_processor) {
    // 分配节点管理器内存
    NodeManager* manager = (NodeManager*)malloc(sizeof(NodeManager));
    if (!manager) {
        fprintf(stderr, "无法分配节点管理器内存\n");
        return NULL;
    }
    
    // 设置初始容量
    int capacity = config.initial_capacity > 0 ? config.initial_capacity : 10;
    manager->nodes = (QuantumNetworkNode**)malloc(sizeof(QuantumNetworkNode*) * capacity);
    
    if (!manager->nodes) {
        free(manager);
        fprintf(stderr, "无法分配节点数组内存\n");
        return NULL;
    }
    
    // 初始化节点数组
    for (int i = 0; i < capacity; i++) {
        manager->nodes[i] = NULL;
    }
    
    // 分配事件队列
    manager->event_queue = (NetworkEvent*)malloc(sizeof(NetworkEvent) * DEFAULT_EVENT_QUEUE_SIZE);
    if (!manager->event_queue) {
        free(manager->nodes);
        free(manager);
        fprintf(stderr, "无法分配事件队列内存\n");
        return NULL;
    }
    
    // 初始化管理器属性
    manager->node_count = 0;
    manager->capacity = capacity;
    manager->config = config;
    manager->manager_id = generate_manager_id();
    manager->log_file = NULL;
    manager->event_queue_size = DEFAULT_EVENT_QUEUE_SIZE;
    manager->event_count = 0;
    manager->last_topology_update = time(NULL);
    manager->topology = NULL;
    manager->entanglement_processor = entanglement_processor;
    manager->routing_table = NULL;
    manager->mutex = NULL;
    
    // 打开日志文件(如果启用)
    if (config.enable_logging && config.log_file_path) {
        manager->log_file = fopen(config.log_file_path, "a");
        if (!manager->log_file) {
            fprintf(stderr, "警告: 无法打开日志文件 %s\n", config.log_file_path);
        }
    }
    
    // TODO: 初始化路由表和互斥锁(如果需要)
    
    // 记录初始化成功
    log_manager_action(manager, "初始化", "节点管理器初始化成功");
    
    printf("量子网络节点管理器初始化成功 (ID: %s)\n", manager->manager_id);
    
    return manager;
}

/**
 * 获取默认节点管理器配置
 */
NodeManagerConfig get_default_node_manager_config() {
    NodeManagerConfig config;
    
    config.initial_capacity = 20;
    config.max_capacity = 1000;
    config.auto_resize = 1;
    config.enable_logging = 1;
    config.log_file_path = "node_manager.log";
    config.enable_auto_routing = 1;
    config.enable_self_healing = 1;
    config.topology_update_interval = 300;
    config.connection_timeout = 30;
    config.max_retry_count = 3;
    config.default_max_connections = 10;
    config.default_connection_strength = 0.8;
    config.stability_threshold = 0.6;
    
    return config;
}

/**
 * 关闭节点管理器
 */
void shutdown_node_manager(NodeManager* manager) {
    if (!manager) return;
    
    // 记录关闭操作
    log_manager_action(manager, "关闭", "正在关闭节点管理器");
    
    // 释放所有节点和连接资源
    for (int i = 0; i < manager->node_count; i++) {
        if (manager->nodes[i]) {
            free_node_resources(manager->nodes[i]);
            free(manager->nodes[i]);
        }
    }
    
    // 释放拓扑分析结果
    if (manager->topology) {
        free_topology_analysis(manager->topology);
    }
    
    // 释放事件队列
    if (manager->event_queue) {
        cleanup_events(manager);
        free(manager->event_queue);
    }
    
    // 关闭日志文件
    if (manager->log_file) {
        fclose(manager->log_file);
    }
    
    // TODO: 释放路由表和互斥锁
    
    // 释放节点数组
    free(manager->nodes);
    
    // 释放管理器ID
    free(manager->manager_id);
    
    // 释放管理器本身
    free(manager);
    
    printf("量子网络节点管理器已关闭\n");
}

/**
 * 创建网络节点
 */
unsigned int create_network_node(NodeManager* manager, NodeType type, const char* name, unsigned int capabilities) {
    if (!manager || !name) {
        return 0;
    }
    
    // 检查容量
    if (manager->node_count >= manager->capacity) {
        if (manager->config.auto_resize && 
            (manager->config.max_capacity == 0 || manager->capacity < manager->config.max_capacity)) {
            
            // 尝试调整大小
            NodeManagerError resize_result = resize_node_array(manager);
            if (resize_result != NODE_MANAGER_ERROR_NONE) {
                log_manager_action(manager, "错误", "无法扩展节点数组容量");
                return 0;
            }
        } else {
            log_manager_action(manager, "错误", "网络节点已满");
            return 0;
        }
    }
    
    // 分配新节点
    QuantumNetworkNode* node = (QuantumNetworkNode*)malloc(sizeof(QuantumNetworkNode));
    if (!node) {
        log_manager_action(manager, "错误", "无法分配节点内存");
        return 0;
    }
    
    // 分配连接数组
    int max_connections = manager->config.default_max_connections;
    node->connections = (NetworkConnection**)malloc(sizeof(NetworkConnection*) * max_connections);
    if (!node->connections) {
        free(node);
        log_manager_action(manager, "错误", "无法分配连接数组内存");
        return 0;
    }
    
    // 初始化连接数组
    for (int i = 0; i < max_connections; i++) {
        node->connections[i] = NULL;
    }
    
    // 生成唯一ID
    unsigned int node_id = generate_unique_id();
    
    // 初始化节点属性
    node->id = node_id;
    // 重要：节点默认为激活状态，确保网络中节点自动参与量子纠缠网络构建
    // 这允许系统根据可用计算资源自动扩展量子比特计算能力
    node->state = NODE_STATE_ACTIVE;
    node->connection_count = 0;
    node->max_connections = max_connections;
    node->energy_level = 1.0;
    node->stability = 1.0;
    node->creation_time = time(NULL);
    node->last_update_time = node->creation_time;
    node->last_activity_time = node->creation_time;
    node->node_state = NULL;
    node->custom_data = NULL;
    
    // 初始化元数据
    node->metadata.name = strdup(name);
    node->metadata.description = NULL;
    node->metadata.type = type;
    node->metadata.capabilities = capabilities;
    node->metadata.owner = NULL;
    node->metadata.location = NULL;
    node->metadata.priority = 0.5;
    node->metadata.creation_time = get_current_timestamp();
    node->metadata.last_update_time = strdup(node->metadata.creation_time);
    node->metadata.tags = NULL;
    node->metadata.custom_data = NULL;
    
    // 添加到管理器
    manager->nodes[manager->node_count++] = node;
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "创建节点: ID=%u, 名称=%s, 类型=%d", 
             node_id, name, type);
    log_manager_action(manager, "创建节点", details);
    
    // 触发事件
    queue_network_event(manager, NETWORK_EVENT_NODE_ADDED, node_id, 0, NULL, "节点已添加");
    
    return node_id;
}

/**
 * 获取节点
 */
QuantumNetworkNode* get_node(NodeManager* manager, unsigned int node_id) {
    if (!manager) {
        return NULL;
    }
    
    // 查找节点
    int index = find_node_index(manager, node_id);
    if (index < 0) {
        return NULL;
    }
    
    return manager->nodes[index];
}

/**
 * 更新节点状态
 */
NodeManagerError update_node_state(NodeManager* manager, unsigned int node_id, NodeState state) {
    if (!manager) {
        return NODE_MANAGER_ERROR_INVALID_ARGUMENT;
    }
    
    // 查找节点
    int index = find_node_index(manager, node_id);
    if (index < 0) {
        return NODE_MANAGER_ERROR_NODE_NOT_FOUND;
    }
    
    QuantumNetworkNode* node = manager->nodes[index];
    
    // 验证状态转换的有效性
    if (!validate_node_state_transition(node->state, state)) {
        char details[256];
        snprintf(details, sizeof(details), "无效的状态转换: 节点ID=%u, 当前状态=%d, 新状态=%d", 
                 node_id, node->state, state);
        log_manager_action(manager, "错误", details);
        return NODE_MANAGER_ERROR_INVALID_ARGUMENT;
    }
    
    // 更新状态
    NodeState old_state = node->state;
    node->state = state;
    node->last_update_time = time(NULL);
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "更新节点状态: ID=%u, 旧状态=%d, 新状态=%d", 
             node_id, old_state, state);
    log_manager_action(manager, "更新节点", details);
    
    // 触发事件
    queue_network_event(manager, NETWORK_EVENT_NODE_STATE_CHANGED, node_id, 0, NULL, details);
    
    return NODE_MANAGER_ERROR_NONE;
}

/**
 * 更新节点元数据
 */
NodeManagerError update_node_metadata(NodeManager* manager, unsigned int node_id, NodeMetadata metadata) {
    if (!manager) {
        return NODE_MANAGER_ERROR_INVALID_ARGUMENT;
    }
    
    // 查找节点
    int index = find_node_index(manager, node_id);
    if (index < 0) {
        return NODE_MANAGER_ERROR_NODE_NOT_FOUND;
    }
    
    QuantumNetworkNode* node = manager->nodes[index];
    
    // 备份旧名称以便记录
    char* old_name = strdup(node->metadata.name);
    
    // 释放旧元数据
    free(node->metadata.name);
    free(node->metadata.description);
    free(node->metadata.owner);
    free(node->metadata.location);
    free(node->metadata.creation_time);
    free(node->metadata.last_update_time);
    free(node->metadata.tags);
    // 注意：不释放custom_data，假设调用者负责管理它
    
    // 复制新元数据
    node->metadata.name = metadata.name ? strdup(metadata.name) : NULL;
    node->metadata.description = metadata.description ? strdup(metadata.description) : NULL;
    node->metadata.type = metadata.type;
    node->metadata.capabilities = metadata.capabilities;
    node->metadata.owner = metadata.owner ? strdup(metadata.owner) : NULL;
    node->metadata.location = metadata.location ? strdup(metadata.location) : NULL;
    node->metadata.priority = metadata.priority;
    
    // 保留创建时间，但更新last_update_time
    free(node->metadata.last_update_time);
    node->metadata.last_update_time = get_current_timestamp();
    
    node->metadata.tags = metadata.tags ? strdup(metadata.tags) : NULL;
    node->metadata.custom_data = metadata.custom_data;
    
    // 更新节点的时间戳
    node->last_update_time = time(NULL);
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "更新节点元数据: ID=%u, 名称从'%s'变为'%s'", 
             node_id, old_name, node->metadata.name);
    log_manager_action(manager, "更新节点", details);
    
    free(old_name);
    
    return NODE_MANAGER_ERROR_NONE;
}

/**
 * 删除网络节点
 */
NodeManagerError delete_network_node(NodeManager* manager, unsigned int node_id) {
    if (!manager) {
        return NODE_MANAGER_ERROR_INVALID_ARGUMENT;
    }
    
    // 查找节点
    int index = find_node_index(manager, node_id);
    if (index < 0) {
        return NODE_MANAGER_ERROR_NODE_NOT_FOUND;
    }
    
    QuantumNetworkNode* node = manager->nodes[index];
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "删除节点: ID=%u, 名称=%s", 
             node_id, node->metadata.name);
    log_manager_action(manager, "删除节点", details);
    
    // 释放节点资源
    free_node_resources(node);
    free(node);
    
    // 从数组中移除节点（通过将最后一个节点移到被删除的位置）
    if (index < manager->node_count - 1) {
        manager->nodes[index] = manager->nodes[manager->node_count - 1];
    }
    manager->nodes[manager->node_count - 1] = NULL;
    manager->node_count--;
    
    // 触发事件
    queue_network_event(manager, NETWORK_EVENT_NODE_REMOVED, node_id, 0, NULL, "节点已移除");
    
    return NODE_MANAGER_ERROR_NONE;
}

/**
 * 创建网络连接
 */
unsigned int create_network_connection(NodeManager* manager, unsigned int source_node_id, unsigned int target_node_id, ConnectionType type, double strength) {
    if (!manager || source_node_id == 0 || target_node_id == 0 || source_node_id == target_node_id) {
        return 0;
    }
    
    // 查找源节点和目标节点
    int source_index = find_node_index(manager, source_node_id);
    int target_index = find_node_index(manager, target_node_id);
    
    if (source_index < 0 || target_index < 0) {
        log_manager_action(manager, "错误", "创建连接失败: 节点不存在");
        return 0;
    }
    
    QuantumNetworkNode* source_node = manager->nodes[source_index];
    QuantumNetworkNode* target_node = manager->nodes[target_index];
    
    // 检查节点状态
    if (source_node->state != NODE_STATE_ACTIVE || target_node->state != NODE_STATE_ACTIVE) {
        log_manager_action(manager, "错误", "创建连接失败: 节点未激活");
        return 0;
    }
    
    // 检查连接容量
    if (source_node->connection_count >= source_node->max_connections) {
        log_manager_action(manager, "错误", "创建连接失败: 源节点连接已满");
        return 0;
    }
    
    if (target_node->connection_count >= target_node->max_connections) {
        log_manager_action(manager, "错误", "创建连接失败: 目标节点连接已满");
        return 0;
    }
    
    // 检查是否已存在连接
    for (int i = 0; i < source_node->connection_count; i++) {
        NetworkConnection* conn = source_node->connections[i];
        if ((conn->source_node_id == source_node_id && conn->target_node_id == target_node_id) ||
            (conn->source_node_id == target_node_id && conn->target_node_id == source_node_id)) {
            log_manager_action(manager, "错误", "创建连接失败: 连接已存在");
            return 0;
        }
    }
    
    // 创建新连接
    NetworkConnection* connection = (NetworkConnection*)malloc(sizeof(NetworkConnection));
    if (!connection) {
        log_manager_action(manager, "错误", "无法分配连接内存");
        return 0;
    }
    
    // 生成唯一ID
    unsigned int connection_id = generate_unique_id();
    
    // 初始化连接属性
    connection->id = connection_id;
    connection->source_node_id = source_node_id;
    connection->target_node_id = target_node_id;
    connection->type = type;
    connection->state = CONNECTION_STATE_ACTIVE;
    connection->strength = strength > 0 ? (strength <= 1.0 ? strength : 1.0) : manager->config.default_connection_strength;
    connection->bandwidth = 1.0; // 默认带宽
    connection->latency = 0.01; // 默认延迟
    connection->stability = 1.0; // 默认稳定性
    connection->creation_time = time(NULL);
    connection->last_update_time = connection->creation_time;
    connection->entanglement_channel = NULL;
    connection->custom_data = NULL;
    
    // 添加到源节点和目标节点
    source_node->connections[source_node->connection_count++] = connection;
    
    // 对于目标节点，创建一个相同连接的指针
    if (target_node->connection_count < target_node->max_connections) {
        target_node->connections[target_node->connection_count++] = connection;
    }
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "创建连接: ID=%u, 源节点=%u, 目标节点=%u, 类型=%d, 强度=%.2f", 
             connection_id, source_node_id, target_node_id, type, connection->strength);
    log_manager_action(manager, "创建连接", details);
    
    // 触发事件
    queue_network_event(manager, NETWORK_EVENT_CONNECTION_ADDED, 0, connection_id, NULL, "连接已添加");
    
    // 如果是纠缠类型连接，创建纠缠通道
    if (type == CONNECTION_TYPE_ENTANGLED && manager->entanglement_processor) {
        // TODO: 创建实际的纠缠通道
    }
    
    return connection_id;
}

/**
 * 获取连接
 */
NetworkConnection* get_connection(NodeManager* manager, unsigned int connection_id) {
    if (!manager) {
        return NULL;
    }
    
    // 查找连接
    return find_connection(manager, connection_id);
}

/**
 * 更新连接状态
 */
NodeManagerError update_connection_state(NodeManager* manager, unsigned int connection_id, ConnectionState state) {
    if (!manager) {
        return NODE_MANAGER_ERROR_INVALID_ARGUMENT;
    }
    
    // 查找连接
    NetworkConnection* connection = find_connection(manager, connection_id);
    if (!connection) {
        return NODE_MANAGER_ERROR_CONNECTION_FAILED;
    }
    
    // 验证状态转换的有效性
    if (!validate_connection_state_transition(connection->state, state)) {
        char details[256];
        snprintf(details, sizeof(details), "无效的连接状态转换: 连接ID=%u, 当前状态=%d, 新状态=%d", 
                 connection_id, connection->state, state);
        log_manager_action(manager, "错误", details);
        return NODE_MANAGER_ERROR_INVALID_ARGUMENT;
    }
    
    // 更新状态
    ConnectionState old_state = connection->state;
    connection->state = state;
    connection->last_update_time = time(NULL);
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "更新连接状态: ID=%u, 旧状态=%d, 新状态=%d", 
             connection_id, old_state, state);
    log_manager_action(manager, "更新连接", details);
    
    // 触发事件
    queue_network_event(manager, NETWORK_EVENT_CONNECTION_CHANGED, 0, connection_id, NULL, details);
    
    return NODE_MANAGER_ERROR_NONE;
}

/**
 * 暂停节点
 *
 * 将节点状态设置为暂停状态，这将暂时停止节点的活动但保留其所有连接和状态
 */
NodeManagerError suspend_node(NodeManager* manager, unsigned int node_id) {
    if (!manager) {
        return NODE_MANAGER_ERROR_INVALID_ARGUMENT;
    }
    
    // 查找节点
    int index = find_node_index(manager, node_id);
    if (index < 0) {
        return NODE_MANAGER_ERROR_NODE_NOT_FOUND;
    }
    
    QuantumNetworkNode* node = manager->nodes[index];
    
    // 如果节点已经处于暂停状态，直接返回成功
    if (node->state == NODE_STATE_SUSPENDED) {
        return NODE_MANAGER_ERROR_NONE;
    }
    
    // 只有活动状态的节点可以被暂停
    if (node->state != NODE_STATE_ACTIVE) {
        char details[256];
        snprintf(details, sizeof(details), "无法暂停节点: ID=%u, 当前状态=%d 不是活动状态", 
                 node_id, node->state);
        log_manager_action(manager, "错误", details);
        return NODE_MANAGER_ERROR_INVALID_ARGUMENT;
    }
    
    // 更新节点状态为暂停
    NodeManagerError result = update_node_state(manager, node_id, NODE_STATE_SUSPENDED);
    
    // 记录操作
    if (result == NODE_MANAGER_ERROR_NONE) {
        char details[256];
        snprintf(details, sizeof(details), "节点已暂停: ID=%u", node_id);
        log_manager_action(manager, "暂停节点", details);
    }
    
    return result;
}

/**
 * 恢复节点
 *
 * 将暂停的节点重新恢复为活动状态，允许节点重新开始处理和参与网络活动
 */
NodeManagerError resume_node(NodeManager* manager, unsigned int node_id) {
    if (!manager) {
        return NODE_MANAGER_ERROR_INVALID_ARGUMENT;
    }
    
    // 查找节点
    int index = find_node_index(manager, node_id);
    if (index < 0) {
        return NODE_MANAGER_ERROR_NODE_NOT_FOUND;
    }
    
    QuantumNetworkNode* node = manager->nodes[index];
    
    // 如果节点已经处于活动状态，直接返回成功
    if (node->state == NODE_STATE_ACTIVE) {
        return NODE_MANAGER_ERROR_NONE;
    }
    
    // 只有暂停状态的节点可以被恢复
    if (node->state != NODE_STATE_SUSPENDED) {
        char details[256];
        snprintf(details, sizeof(details), "无法恢复节点: ID=%u, 当前状态=%d 不是暂停状态", 
                 node_id, node->state);
        log_manager_action(manager, "错误", details);
        return NODE_MANAGER_ERROR_INVALID_ARGUMENT;
    }
    
    // 更新节点状态为活动
    NodeManagerError result = update_node_state(manager, node_id, NODE_STATE_ACTIVE);
    
    // 记录操作
    if (result == NODE_MANAGER_ERROR_NONE) {
        char details[256];
        snprintf(details, sizeof(details), "节点已恢复: ID=%u", node_id);
        log_manager_action(manager, "恢复节点", details);
        
        // 更新节点的最后活动时间
        node->last_activity_time = time(NULL);
    }
    
    return result;
}

/* 内部辅助函数实现 */

/**
 * 生成管理器ID
 */
static char* generate_manager_id() {
    char* id = (char*)malloc(33);
    if (!id) return NULL;
    
    // 生成随机ID
    const char hex_chars[] = "0123456789ABCDEF";
    for (int i = 0; i < 32; i++) {
        id[i] = hex_chars[rand() % 16];
    }
    id[32] = '\0';
    
    return id;
}

/**
 * 记录管理器操作
 */
static void log_manager_action(NodeManager* manager, const char* action, const char* details) {
    if (!manager || !action || !details) return;
    
    // 如果未启用日志，则直接返回
    if (!manager->config.enable_logging) return;
    
    // 获取当前时间
    time_t now;
    time(&now);
    char timestamp[64];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(&now));
    
    // 打印到控制台
    printf("[%s] NodeManager (%s): %s - %s\n", 
           timestamp, manager->manager_id, action, details);
    
    // 写入日志文件
    if (manager->log_file) {
        fprintf(manager->log_file, "[%s] %s - %s\n", timestamp, action, details);
        fflush(manager->log_file);
    }
}

/**
 * 查找节点索引
 */
static int find_node_index(NodeManager* manager, unsigned int node_id) {
    if (!manager) return -1;
    
    for (int i = 0; i < manager->node_count; i++) {
        if (manager->nodes[i] && manager->nodes[i]->id == node_id) {
            return i;
        }
    }
    
    return -1;
}

/**
 * 查找连接
 */
static NetworkConnection* find_connection(NodeManager* manager, unsigned int connection_id) {
    if (!manager) return NULL;
    
    // 在所有节点的连接中查找
    for (int i = 0; i < manager->node_count; i++) {
        QuantumNetworkNode* node = manager->nodes[i];
        if (!node) continue;
        
        for (int j = 0; j < node->connection_count; j++) {
            if (node->connections[j] && node->connections[j]->id == connection_id) {
                return node->connections[j];
            }
        }
    }
    
    return NULL;
}

/**
 * 查找节点中的连接索引
 */
static int find_connection_index(QuantumNetworkNode* node, unsigned int connection_id) {
    if (!node) return -1;
    
    for (int i = 0; i < node->connection_count; i++) {
        if (node->connections[i] && node->connections[i]->id == connection_id) {
            return i;
        }
    }
    
    return -1;
}

/**
 * 释放节点资源
 */
static void free_node_resources(QuantumNetworkNode* node) {
    if (!node) return;
    
    // 释放元数据
    free(node->metadata.name);
    free(node->metadata.description);
    free(node->metadata.owner);
    free(node->metadata.location);
    free(node->metadata.creation_time);
    free(node->metadata.last_update_time);
    free(node->metadata.tags);
    
    // 释放连接资源
    // 注意：一个连接可能被多个节点引用，所以需要小心处理
    // 这里只释放那些以此节点为源节点的连接
    for (int i = 0; i < node->connection_count; i++) {
        if (node->connections[i] && node->connections[i]->source_node_id == node->id) {
            free_connection_resources(node->connections[i]);
            free(node->connections[i]);
        }
    }
    
    // 释放连接数组
    free(node->connections);
    
    // 注意：不释放node_state，假设它由状态管理器管理
}

/**
 * 释放连接资源
 */
static void free_connection_resources(NetworkConnection* connection) {
    if (!connection) return;
    
    // 清理任何需要释放的资源
    // 注意：entanglement_channel 由纠缠处理器管理，不在这里释放
    // 同样，custom_data 由用户管理
}

/**
 * 验证节点状态转换的有效性
 */
static int validate_node_state_transition(NodeState current_state, NodeState new_state) {
    // 允许所有状态转换，或者可以实现更严格的规则
    return 1;
}

/**
 * 验证连接状态转换的有效性
 */
static int validate_connection_state_transition(ConnectionState current_state, ConnectionState new_state) {
    // 允许所有状态转换，或者可以实现更严格的规则
    return 1;
}

/**
 * 将事件添加到队列
 */
static void queue_network_event(NodeManager* manager, NetworkEventType type, unsigned int node_id, unsigned int connection_id, void* event_data, const char* description) {
    if (!manager) return;
    
    // 如果队列已满，先清理一些旧事件
    if (manager->event_count >= manager->event_queue_size) {
        cleanup_events(manager);
    }
    
    // 如果队列仍然已满，忽略此事件
    if (manager->event_count >= manager->event_queue_size) {
        log_manager_action(manager, "警告", "事件队列已满，忽略新事件");
        return;
    }
    
    // 创建新事件
    NetworkEvent event;
    event.type = type;
    event.node_id = node_id;
    event.connection_id = connection_id;
    event.timestamp = time(NULL);
    event.event_data = event_data;
    event.description = description ? strdup(description) : NULL;
    
    // 添加到队列
    manager->event_queue[manager->event_count++] = event;
}

/**
 * 调整节点数组大小
 */
static NodeManagerError resize_node_array(NodeManager* manager) {
    if (!manager) return NODE_MANAGER_ERROR_INVALID_ARGUMENT;
    
    // 计算新容量
    int new_capacity = manager->capacity * 2;
    if (manager->config.max_capacity > 0 && new_capacity > manager->config.max_capacity) {
        new_capacity = manager->config.max_capacity;
    }
    
    // 如果无法增加容量，返回错误
    if (new_capacity <= manager->capacity) {
        return NODE_MANAGER_ERROR_NETWORK_FULL;
    }
    
    // 分配新数组
    QuantumNetworkNode** new_nodes = (QuantumNetworkNode**)realloc(
        manager->nodes, 
        sizeof(QuantumNetworkNode*) * new_capacity
    );
    
    if (!new_nodes) {
        return NODE_MANAGER_ERROR_MEMORY_ALLOCATION;
    }
    
    // 初始化新分配的部分
    for (int i = manager->capacity; i < new_capacity; i++) {
        new_nodes[i] = NULL;
    }
    
    // 更新管理器
    manager->nodes = new_nodes;
    manager->capacity = new_capacity;
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "节点数组已调整大小，新容量: %d", new_capacity);
    log_manager_action(manager, "调整大小", details);
    
    return NODE_MANAGER_ERROR_NONE;
}

/**
 * 获取当前时间戳
 */
static char* get_current_timestamp() {
    char* timestamp = (char*)malloc(64);
    if (!timestamp) return NULL;
    
    time_t now;
    time(&now);
    strftime(timestamp, 64, "%Y-%m-%d %H:%M:%S", localtime(&now));
    
    return timestamp;
}

/**
 * 生成唯一ID
 */
static unsigned int generate_unique_id() {
    static unsigned int next_id = 1;
    
    // 简单实现，在实际应用中可能需要更复杂的ID生成策略
    return next_id++;
}

/**
 * 更新节点能量
 */
static void update_node_energy(QuantumNetworkNode* node) {
    if (!node) return;
    
    // 简单的能量更新逻辑，可以根据需要扩展
    
    // 能量自然衰减
    node->energy_level *= 0.999;
    
    // 确保在有效范围内
    if (node->energy_level < 0.1) node->energy_level = 0.1;
    if (node->energy_level > 1.0) node->energy_level = 1.0;
}

/**
 * 更新连接稳定性
 */
static void update_connection_stability(NetworkConnection* connection) {
    if (!connection) return;
    
    // 简单的稳定性更新逻辑，可以根据需要扩展
    
    // 随时间轻微波动
    double random_factor = 0.99 + (rand() % 3) * 0.01; // 0.99, 1.00, 或 1.01
    connection->stability *= random_factor;
    
    // 确保在有效范围内
    if (connection->stability < 0.3) connection->stability = 0.3;
    if (connection->stability > 1.0) connection->stability = 1.0;
}

/**
 * 清理事件
 */
static void cleanup_events(NodeManager* manager) {
    if (!manager) return;
    
    // 简单策略：保留最近一半的事件
    int keep_count = manager->event_count / 2;
    if (keep_count < 1) keep_count = 1;
    
    // 释放要丢弃的事件资源
    for (int i = 0; i < manager->event_count - keep_count; i++) {
        free(manager->event_queue[i].description);
    }
    
    // 移动要保留的事件
    for (int i = 0; i < keep_count; i++) {
        manager->event_queue[i] = manager->event_queue[manager->event_count - keep_count + i];
    }
    
    // 更新计数
    manager->event_count = keep_count;
}
} 
} 