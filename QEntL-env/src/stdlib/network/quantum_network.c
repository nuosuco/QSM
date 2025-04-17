/**
 * 量子网络库 - 实现量子节点间的通信和分布式量子计算功能
 * 
 * 该模块提供基于量子纠缠的网络传输、远程量子状态准备和分布式量子算法
 * 
 * @作者：QEntL开发团队
 * @版本：1.0.0
 * @日期：2023-06-22
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../../quantum_state.h"
#include "../../quantum_entanglement.h"
#include "../core/math_library.h"

// 量子网络节点结构
typedef struct quantum_node {
    char node_id[64];                  // 节点ID
    char node_address[128];            // 节点网络地址
    quantum_state_t* local_state;      // 本地量子状态
    quantum_entanglement_t** entanglements; // 与其他节点的量子纠缠
    int entanglement_count;            // 纠缠数量
    int active;                        // 节点是否活跃
    int qubit_capacity;                // 节点的量子比特容量
    struct quantum_node** neighbors;   // 邻居节点
    int neighbor_count;                // 邻居数量
} quantum_node_t;

// 量子网络结构
typedef struct {
    quantum_node_t** nodes;            // 网络节点列表
    int node_count;                    // 节点数量
    char network_id[64];               // 网络ID
    int is_fully_connected;            // 是否为全连接网络
    time_t creation_time;              // 创建时间
    double entanglement_fidelity;      // 网络纠缠保真度
} quantum_network_t;

// 量子通信协议
typedef enum {
    QCP_TELEPORTATION,                 // 量子隐形传态
    QCP_DENSE_CODING,                  // 超密编码
    QCP_ENTANGLEMENT_SWAPPING,         // 纠缠交换
    QCP_QUANTUM_KEY_DISTRIBUTION       // 量子密钥分发
} quantum_comm_protocol_t;

// 量子通信消息结构
typedef struct {
    char message_id[64];               // 消息ID
    char sender_id[64];                // 发送者ID
    char receiver_id[64];              // 接收者ID
    quantum_comm_protocol_t protocol;  // 使用的通信协议
    quantum_state_t* payload;          // 量子荷载
    int classical_bits[2];             // 经典辅助比特
    time_t timestamp;                  // 时间戳
} quantum_message_t;

// ==== 量子节点函数 ====

// 创建量子网络节点
quantum_node_t* quantum_node_create(const char* node_id, const char* address, int qubit_capacity) {
    quantum_node_t* node = (quantum_node_t*)malloc(sizeof(quantum_node_t));
    if (!node) return NULL;
    
    strncpy(node->node_id, node_id, 63);
    node->node_id[63] = '\0';
    
    strncpy(node->node_address, address, 127);
    node->node_address[127] = '\0';
    
    node->qubit_capacity = qubit_capacity;
    node->local_state = quantum_state_create(qubit_capacity);
    node->entanglements = NULL;
    node->entanglement_count = 0;
    node->active = 1;
    node->neighbors = NULL;
    node->neighbor_count = 0;
    
    return node;
}

// 销毁量子网络节点
void quantum_node_destroy(quantum_node_t* node) {
    if (!node) return;
    
    quantum_state_destroy(node->local_state);
    
    // 释放纠缠
    if (node->entanglements) {
        for (int i = 0; i < node->entanglement_count; i++) {
            quantum_entanglement_destroy(node->entanglements[i]);
        }
        free(node->entanglements);
    }
    
    // 注意：不释放邻居指针，因为它们是对其他节点的引用
    if (node->neighbors) {
        free(node->neighbors);
    }
    
    free(node);
}

// 添加节点邻居
int quantum_node_add_neighbor(quantum_node_t* node, quantum_node_t* neighbor) {
    if (!node || !neighbor) return 0;
    
    // 检查是否已经是邻居
    for (int i = 0; i < node->neighbor_count; i++) {
        if (node->neighbors[i] == neighbor) return 1; // 已经是邻居
    }
    
    // 扩展邻居数组
    quantum_node_t** new_neighbors = (quantum_node_t**)realloc(
        node->neighbors, sizeof(quantum_node_t*) * (node->neighbor_count + 1));
    
    if (!new_neighbors) return 0;
    
    node->neighbors = new_neighbors;
    node->neighbors[node->neighbor_count] = neighbor;
    node->neighbor_count++;
    
    return 1;
}

// 创建与另一个节点的量子纠缠
int quantum_node_create_entanglement(quantum_node_t* node, quantum_node_t* other_node) {
    if (!node || !other_node) return 0;
    
    // 创建纠缠
    quantum_entanglement_t* entanglement = quantum_entangle(
        node->local_state, other_node->local_state);
    
    if (!entanglement) return 0;
    
    // 为当前节点添加纠缠
    quantum_entanglement_t** new_entanglements = (quantum_entanglement_t**)realloc(
        node->entanglements, sizeof(quantum_entanglement_t*) * (node->entanglement_count + 1));
    
    if (!new_entanglements) {
        quantum_entanglement_destroy(entanglement);
        return 0;
    }
    
    node->entanglements = new_entanglements;
    node->entanglements[node->entanglement_count] = entanglement;
    node->entanglement_count++;
    
    // 确保节点互为邻居
    quantum_node_add_neighbor(node, other_node);
    quantum_node_add_neighbor(other_node, node);
    
    return 1;
}

// 检查两个节点是否有纠缠
int quantum_node_has_entanglement(quantum_node_t* node1, quantum_node_t* node2) {
    if (!node1 || !node2) return 0;
    
    // 检查是否是邻居
    int is_neighbor = 0;
    for (int i = 0; i < node1->neighbor_count; i++) {
        if (node1->neighbors[i] == node2) {
            is_neighbor = 1;
            break;
        }
    }
    
    if (!is_neighbor) return 0;
    
    // 检查量子态是否纠缠
    for (int i = 0; i < node1->entanglement_count; i++) {
        if (quantum_entanglement_involves(node1->entanglements[i], node2->local_state)) {
            return 1;
        }
    }
    
    return 0;
}

// 测量节点的本地量子状态
int quantum_node_measure(quantum_node_t* node) {
    if (!node) return -1;
    
    return quantum_state_measure(node->local_state);
}

// ==== 量子网络函数 ====

// 创建量子网络
quantum_network_t* quantum_network_create(const char* network_id) {
    quantum_network_t* network = (quantum_network_t*)malloc(sizeof(quantum_network_t));
    if (!network) return NULL;
    
    strncpy(network->network_id, network_id, 63);
    network->network_id[63] = '\0';
    
    network->nodes = NULL;
    network->node_count = 0;
    network->is_fully_connected = 0;
    network->creation_time = time(NULL);
    network->entanglement_fidelity = 1.0;
    
    return network;
}

// 销毁量子网络
void quantum_network_destroy(quantum_network_t* network) {
    if (!network) return;
    
    // 销毁所有节点
    if (network->nodes) {
        for (int i = 0; i < network->node_count; i++) {
            quantum_node_destroy(network->nodes[i]);
        }
        free(network->nodes);
    }
    
    free(network);
}

// 添加节点到网络
int quantum_network_add_node(quantum_network_t* network, quantum_node_t* node) {
    if (!network || !node) return 0;
    
    // 检查是否已经在网络中
    for (int i = 0; i < network->node_count; i++) {
        if (strcmp(network->nodes[i]->node_id, node->node_id) == 0) {
            return 0; // 已经存在
        }
    }
    
    // 扩展节点数组
    quantum_node_t** new_nodes = (quantum_node_t**)realloc(
        network->nodes, sizeof(quantum_node_t*) * (network->node_count + 1));
    
    if (!new_nodes) return 0;
    
    network->nodes = new_nodes;
    network->nodes[network->node_count] = node;
    network->node_count++;
    
    // 添加后不再是全连接
    network->is_fully_connected = 0;
    
    return 1;
}

// 查找网络中的节点
quantum_node_t* quantum_network_find_node(quantum_network_t* network, const char* node_id) {
    if (!network || !node_id) return NULL;
    
    for (int i = 0; i < network->node_count; i++) {
        if (strcmp(network->nodes[i]->node_id, node_id) == 0) {
            return network->nodes[i];
        }
    }
    
    return NULL;
}

// 在网络中创建全连接拓扑
int quantum_network_create_fully_connected(quantum_network_t* network) {
    if (!network || network->node_count <= 1) return 0;
    
    for (int i = 0; i < network->node_count; i++) {
        for (int j = i + 1; j < network->node_count; j++) {
            // 如果尚未纠缠，则创建纠缠
            if (!quantum_node_has_entanglement(network->nodes[i], network->nodes[j])) {
                if (!quantum_node_create_entanglement(network->nodes[i], network->nodes[j])) {
                    return 0;
                }
            }
        }
    }
    
    network->is_fully_connected = 1;
    return 1;
}

// 计算网络量子比特总容量
int quantum_network_total_capacity(quantum_network_t* network) {
    if (!network) return 0;
    
    int total = 0;
    for (int i = 0; i < network->node_count; i++) {
        total += network->nodes[i]->qubit_capacity;
    }
    
    return total;
}

// 计算网络的纠缠连接性
double quantum_network_entanglement_connectivity(quantum_network_t* network) {
    if (!network || network->node_count <= 1) return 0.0;
    
    int total_possible_connections = network->node_count * (network->node_count - 1) / 2;
    int actual_connections = 0;
    
    for (int i = 0; i < network->node_count; i++) {
        for (int j = i + 1; j < network->node_count; j++) {
            if (quantum_node_has_entanglement(network->nodes[i], network->nodes[j])) {
                actual_connections++;
            }
        }
    }
    
    return (double)actual_connections / total_possible_connections;
}

// ==== 量子通信函数 ====

// 创建量子通信消息
quantum_message_t* quantum_message_create(const char* sender_id, const char* receiver_id, 
                                         quantum_comm_protocol_t protocol, quantum_state_t* payload) {
    quantum_message_t* message = (quantum_message_t*)malloc(sizeof(quantum_message_t));
    if (!message) return NULL;
    
    // 生成唯一消息ID
    sprintf(message->message_id, "QM%ld", (long)time(NULL));
    
    strncpy(message->sender_id, sender_id, 63);
    message->sender_id[63] = '\0';
    
    strncpy(message->receiver_id, receiver_id, 63);
    message->receiver_id[63] = '\0';
    
    message->protocol = protocol;
    message->payload = quantum_state_copy(payload);
    message->classical_bits[0] = 0;
    message->classical_bits[1] = 0;
    message->timestamp = time(NULL);
    
    return message;
}

// 销毁量子通信消息
void quantum_message_destroy(quantum_message_t* message) {
    if (!message) return;
    
    quantum_state_destroy(message->payload);
    free(message);
}

// 执行量子隐形传态
int quantum_teleport(quantum_node_t* sender, quantum_node_t* receiver, quantum_state_t* state_to_send, 
                     int* measurement_results) {
    if (!sender || !receiver || !state_to_send || !measurement_results) return 0;
    
    // 检查是否有纠缠
    if (!quantum_node_has_entanglement(sender, receiver)) return 0;
    
    // 简化版：直接设置接收者的量子态
    quantum_state_copy_to(state_to_send, receiver->local_state);
    
    // 设置经典测量结果（在实际实现中，这应该由隐形传态协议决定）
    measurement_results[0] = rand() % 2;
    measurement_results[1] = rand() % 2;
    
    return 1;
}

// 执行超密编码
int quantum_dense_coding(quantum_node_t* sender, quantum_node_t* receiver, int bit1, int bit2, 
                         int* decoded_bits) {
    if (!sender || !receiver || !decoded_bits) return 0;
    
    // 检查是否有纠缠
    if (!quantum_node_has_entanglement(sender, receiver)) return 0;
    
    // 简化版：直接返回编码的比特
    decoded_bits[0] = bit1;
    decoded_bits[1] = bit2;
    
    return 1;
}

// 执行纠缠交换
int quantum_entanglement_swapping(quantum_node_t* node1, quantum_node_t* node2, quantum_node_t* intermediary) {
    if (!node1 || !node2 || !intermediary) return 0;
    
    // 检查所需的纠缠
    if (!quantum_node_has_entanglement(node1, intermediary) || 
        !quantum_node_has_entanglement(intermediary, node2)) return 0;
    
    // 简化版：直接在node1和node2之间创建纠缠
    return quantum_node_create_entanglement(node1, node2);
}

// 执行量子密钥分发
int quantum_key_distribution(quantum_node_t* sender, quantum_node_t* receiver, int* key, int key_length) {
    if (!sender || !receiver || !key || key_length <= 0) return 0;
    
    // 生成随机密钥
    for (int i = 0; i < key_length; i++) {
        key[i] = rand() % 2;
    }
    
    return 1;
}

// ==== 分布式量子计算函数 ====

// 分布式量子傅里叶变换
int distributed_quantum_fourier_transform(quantum_network_t* network, quantum_node_t** participating_nodes, 
                                         int node_count) {
    if (!network || !participating_nodes || node_count <= 0) return 0;
    
    // 检查所有参与节点是否都在网络中
    for (int i = 0; i < node_count; i++) {
        int found = 0;
        for (int j = 0; j < network->node_count; j++) {
            if (participating_nodes[i] == network->nodes[j]) {
                found = 1;
                break;
            }
        }
        
        if (!found) return 0;
    }
    
    // 检查节点之间是否有足够的纠缠连接
    for (int i = 0; i < node_count; i++) {
        for (int j = i + 1; j < node_count; j++) {
            if (!quantum_node_has_entanglement(participating_nodes[i], participating_nodes[j])) {
                // 尝试创建纠缠
                if (!quantum_node_create_entanglement(participating_nodes[i], participating_nodes[j])) {
                    return 0;
                }
            }
        }
    }
    
    // 简化版：对每个节点的本地状态应用量子傅里叶变换
    for (int i = 0; i < node_count; i++) {
        quantum_state_apply_qft(participating_nodes[i]->local_state);
    }
    
    return 1;
}

// 分布式量子搜索
int distributed_quantum_search(quantum_network_t* network, quantum_node_t** participating_nodes, 
                              int node_count, int* result) {
    if (!network || !participating_nodes || node_count <= 0 || !result) return 0;
    
    // 检查参与节点
    for (int i = 0; i < node_count; i++) {
        int found = 0;
        for (int j = 0; j < network->node_count; j++) {
            if (participating_nodes[i] == network->nodes[j]) {
                found = 1;
                break;
            }
        }
        
        if (!found) return 0;
    }
    
    // 简化版：随机选择一个结果
    *result = rand() % (1 << quantum_network_total_capacity(network));
    
    return 1;
}

// 分布式量子纠错
int distributed_quantum_error_correction(quantum_network_t* network, quantum_node_t* target_node) {
    if (!network || !target_node) return 0;
    
    // 检查目标节点是否在网络中
    int found = 0;
    for (int i = 0; i < network->node_count; i++) {
        if (target_node == network->nodes[i]) {
            found = 1;
            break;
        }
    }
    
    if (!found) return 0;
    
    // 简化版：恢复纠缠保真度
    network->entanglement_fidelity = 1.0;
    
    return 1;
}

// ==== 调试和信息函数 ====

// 打印量子网络信息
void quantum_network_print(quantum_network_t* network) {
    if (!network) {
        printf("NULL quantum network\n");
        return;
    }
    
    printf("===== 量子网络信息 =====\n");
    printf("网络ID: %s\n", network->network_id);
    printf("创建时间: %ld\n", (long)network->creation_time);
    printf("节点数量: %d\n", network->node_count);
    printf("全连接: %s\n", network->is_fully_connected ? "是" : "否");
    printf("纠缠保真度: %.4f\n", network->entanglement_fidelity);
    printf("连接性: %.4f\n", quantum_network_entanglement_connectivity(network));
    printf("总量子比特容量: %d\n", quantum_network_total_capacity(network));
    
    printf("\n节点列表:\n");
    for (int i = 0; i < network->node_count; i++) {
        quantum_node_t* node = network->nodes[i];
        printf("  节点 #%d:\n", i + 1);
        printf("    ID: %s\n", node->node_id);
        printf("    地址: %s\n", node->node_address);
        printf("    量子比特容量: %d\n", node->qubit_capacity);
        printf("    活跃状态: %s\n", node->active ? "在线" : "离线");
        printf("    纠缠连接数: %d\n", node->entanglement_count);
        printf("    邻居数: %d\n", node->neighbor_count);
        
        if (node->neighbor_count > 0) {
            printf("    邻居节点: ");
            for (int j = 0; j < node->neighbor_count; j++) {
                printf("%s", node->neighbors[j]->node_id);
                if (j < node->neighbor_count - 1) {
                    printf(", ");
                }
            }
            printf("\n");
        }
    }
    
    printf("========================\n");
} 