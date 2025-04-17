/*
 * 自动网络构建模块实现
 * 负责实现节点自动激活和量子网络自动构建
 */

// 量子基因编码
// QG-SRC-AUTONET-C-A1B1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "auto_network_builder.h"

// 创建网络构建器
AutoNetworkBuilder* auto_network_builder_create(const char* id) {
    AutoNetworkBuilder* builder = (AutoNetworkBuilder*)malloc(sizeof(AutoNetworkBuilder));
    if (builder == NULL) {
        return NULL;
    }
    
    // 初始化构建器
    strncpy(builder->id, id, sizeof(builder->id) - 1);
    builder->id[sizeof(builder->id) - 1] = '\0';
    
    // 设置默认配置
    builder->config.strategy = NETWORK_STRATEGY_ADAPTIVE;
    builder->config.discovery = DISCOVERY_METHOD_QUANTUM_RESONANCE;
    builder->config.max_nodes = 1000;
    builder->config.max_connections_per_node = 10;
    builder->config.min_entanglement_strength = 0.5;
    builder->config.auto_rebuild_interval = 3600; // 1小时
    builder->config.activate_all_nodes = 1; // 默认激活所有节点
    
    // 初始化统计信息
    builder->last_build_time = 0;
    builder->total_networks_built = 0;
    builder->active_nodes_count = 0;
    builder->inactive_nodes_count = 0;
    
    return builder;
}

// 销毁网络构建器
void auto_network_builder_destroy(AutoNetworkBuilder* builder) {
    if (builder != NULL) {
        free(builder);
    }
}

// 配置网络构建器
void auto_network_builder_configure(AutoNetworkBuilder* builder, NetworkBuildConfig* config) {
    if (builder == NULL || config == NULL) {
        return;
    }
    
    // 复制配置
    builder->config = *config;
}

// 从现有节点自动构建网络
EntanglementNetwork* auto_network_builder_build_network(
    AutoNetworkBuilder* builder, 
    const char* network_id, 
    QuantumNetworkNode** nodes, 
    int node_count
) {
    if (builder == NULL || network_id == NULL || nodes == NULL || node_count <= 0) {
        return NULL;
    }
    
    // 创建纠缠网络
    EntanglementNetwork* network = entanglement_network_create(network_id);
    if (network == NULL) {
        return NULL;
    }
    
    // 根据策略构建网络
    switch (builder->config.strategy) {
        case NETWORK_STRATEGY_FULLY_CONNECTED:
            // 完全连接网络：每个节点都与其他所有节点连接
            for (int i = 0; i < node_count; i++) {
                // 将节点添加到网络
                entanglement_network_add_node(network, nodes[i]->state);
                
                // 确保节点处于激活状态
                if (builder->config.activate_all_nodes) {
                    entanglement_network_activate_node(network, nodes[i]->state);
                }
                
                // 连接到所有前面的节点
                for (int j = 0; j < i; j++) {
                    // 计算纠缠强度（可以根据需要调整）
                    double strength = builder->config.min_entanglement_strength + 
                                     (1.0 - builder->config.min_entanglement_strength) * ((double)rand() / RAND_MAX);
                    
                    // 创建连接
                    entanglement_network_connect(network, nodes[i]->state, nodes[j]->state, strength);
                }
            }
            break;
            
        case NETWORK_STRATEGY_STAR:
            // 星形网络：一个中心节点与所有其他节点连接
            if (node_count > 0) {
                // 添加所有节点到网络
                for (int i = 0; i < node_count; i++) {
                    entanglement_network_add_node(network, nodes[i]->state);
                    
                    // 确保节点处于激活状态
                    if (builder->config.activate_all_nodes) {
                        entanglement_network_activate_node(network, nodes[i]->state);
                    }
                }
                
                // 连接中心节点（第一个节点）与所有其他节点
                for (int i = 1; i < node_count; i++) {
                    double strength = builder->config.min_entanglement_strength + 
                                     (1.0 - builder->config.min_entanglement_strength) * ((double)rand() / RAND_MAX);
                    
                    entanglement_network_connect(network, nodes[0]->state, nodes[i]->state, strength);
                }
            }
            break;
            
        case NETWORK_STRATEGY_RING:
            // 环形网络：每个节点与相邻的节点连接
            if (node_count > 0) {
                // 添加所有节点到网络
                for (int i = 0; i < node_count; i++) {
                    entanglement_network_add_node(network, nodes[i]->state);
                    
                    // 确保节点处于激活状态
                    if (builder->config.activate_all_nodes) {
                        entanglement_network_activate_node(network, nodes[i]->state);
                    }
                }
                
                // 连接节点形成环
                for (int i = 0; i < node_count; i++) {
                    int next = (i + 1) % node_count;
                    double strength = builder->config.min_entanglement_strength + 
                                     (1.0 - builder->config.min_entanglement_strength) * ((double)rand() / RAND_MAX);
                    
                    entanglement_network_connect(network, nodes[i]->state, nodes[next]->state, strength);
                }
            }
            break;
            
        case NETWORK_STRATEGY_ADAPTIVE:
        default:
            // 自适应网络：根据节点特性和状态动态构建
            // 添加所有节点到网络
            for (int i = 0; i < node_count; i++) {
                entanglement_network_add_node(network, nodes[i]->state);
                
                // 确保节点处于激活状态
                if (builder->config.activate_all_nodes) {
                    entanglement_network_activate_node(network, nodes[i]->state);
                }
                
                // 为每个节点计算适合连接的其他节点
                int connections = 0;
                for (int j = 0; j < node_count && connections < builder->config.max_connections_per_node; j++) {
                    if (i == j) continue;
                    
                    // 计算两个节点之间的兼容性分数
                    double compatibility = compute_node_compatibility(nodes[i], nodes[j]);
                    
                    // 如果兼容性超过阈值，创建连接
                    if (compatibility > 0.6) {
                        double strength = builder->config.min_entanglement_strength + 
                                         (compatibility - 0.6) * (1.0 - builder->config.min_entanglement_strength) / 0.4;
                        
                        entanglement_network_connect(network, nodes[i]->state, nodes[j]->state, strength);
                        connections++;
                    }
                }
            }
            break;
    }
    
    // 更新统计信息
    builder->last_build_time = time(NULL);
    builder->total_networks_built++;
    
    // 统计活跃和非活跃节点
    builder->active_nodes_count = 0;
    builder->inactive_nodes_count = 0;
    
    for (int i = 0; i < network->node_count; i++) {
        if (network->nodes[i].active) {
            builder->active_nodes_count++;
        } else {
            builder->inactive_nodes_count++;
        }
    }
    
    return network;
}

// 发现网络中的节点
int auto_network_builder_discover_nodes(
    AutoNetworkBuilder* builder,
    QuantumNetworkNode** nodes_buffer,
    int buffer_size
) {
    if (builder == NULL || nodes_buffer == NULL || buffer_size <= 0) {
        return -1;
    }
    
    // 实现节点发现逻辑，根据发现方法
    int discovered_count = 0;
    
    switch (builder->config.discovery) {
        case DISCOVERY_METHOD_BROADCAST:
            // 广播发现实现
            discovered_count = discover_nodes_broadcast(nodes_buffer, buffer_size);
            break;
            
        case DISCOVERY_METHOD_QUANTUM_RESONANCE:
            // 量子共振发现实现
            discovered_count = discover_nodes_quantum_resonance(nodes_buffer, buffer_size);
            break;
            
        default:
            // 默认发现方法
            discovered_count = discover_nodes_default(nodes_buffer, buffer_size);
            break;
    }
    
    return discovered_count;
}

// 激活所有发现的节点
int auto_network_builder_activate_all_nodes(
    AutoNetworkBuilder* builder,
    QuantumNetworkNode** nodes,
    int node_count
) {
    if (builder == NULL || nodes == NULL || node_count <= 0) {
        return -1;
    }
    
    int activated_count = 0;
    
    for (int i = 0; i < node_count; i++) {
        if (nodes[i] != NULL) {
            // 激活节点
            nodes[i]->active = 1;
            activated_count++;
            
            // 进行量子纠缠激活过程
            quantum_network_node_activate(nodes[i]);
        }
    }
    
    return activated_count;
}

// 将量子状态添加到自动构建的网络
int auto_network_builder_add_state_to_network(
    AutoNetworkBuilder* builder,
    EntanglementNetwork* network,
    QuantumState* state
) {
    if (builder == NULL || network == NULL || state == NULL) {
        return -1;
    }
    
    // 添加状态到网络
    int result = entanglement_network_add_node(network, state);
    
    // 如果配置为激活所有节点，则激活新添加的状态
    if (result == 0 && builder->config.activate_all_nodes) {
        entanglement_network_activate_node(network, state);
    }
    
    // 自动与网络中的其他节点建立连接
    if (result == 0) {
        int connected_count = 0;
        
        for (int i = 0; i < network->node_count - 1; i++) { // 减1是因为最后一个节点是刚添加的
            // 计算兼容性
            double compatibility = compute_state_compatibility(state, network->nodes[i].state);
            
            // 如果兼容性好，建立连接
            if (compatibility > 0.6) {
                double strength = builder->config.min_entanglement_strength + 
                                 (compatibility - 0.6) * (1.0 - builder->config.min_entanglement_strength) / 0.4;
                
                entanglement_network_connect(network, state, network->nodes[i].state, strength);
                connected_count++;
                
                // 如果已达到最大连接数，停止连接
                if (connected_count >= builder->config.max_connections_per_node) {
                    break;
                }
            }
        }
    }
    
    return result;
}

// 检查和重建网络（如有必要）
int auto_network_builder_check_and_rebuild(
    AutoNetworkBuilder* builder,
    EntanglementNetwork* network
) {
    if (builder == NULL || network == NULL) {
        return -1;
    }
    
    // 检查是否需要重建
    time_t now = time(NULL);
    if (now - builder->last_build_time < builder->config.auto_rebuild_interval) {
        // 未到重建时间
        return 0;
    }
    
    // 检查网络健康状况
    int inactive_nodes = 0;
    for (int i = 0; i < network->node_count; i++) {
        if (!network->nodes[i].active) {
            inactive_nodes++;
        }
    }
    
    // 如果非活跃节点过多，重新激活它们
    if (inactive_nodes > 0 && builder->config.activate_all_nodes) {
        for (int i = 0; i < network->node_count; i++) {
            if (!network->nodes[i].active) {
                entanglement_network_activate_node(network, network->nodes[i].state);
            }
        }
    }
    
    // 检查纠缠连接
    int weak_connections = 0;
    for (int i = 0; i < network->connection_count; i++) {
        if (network->connections[i].strength < builder->config.min_entanglement_strength) {
            weak_connections++;
        }
    }
    
    // 如果弱连接过多，重建网络
    if (weak_connections > network->connection_count / 3) { // 超过1/3的连接较弱
        // 提取所有节点状态
        QuantumState** states = (QuantumState**)malloc(network->node_count * sizeof(QuantumState*));
        if (states == NULL) {
            return -1;
        }
        
        for (int i = 0; i < network->node_count; i++) {
            states[i] = network->nodes[i].state;
        }
        
        // 重建网络连接
        rebuild_network_connections(builder, network, states, network->node_count);
        
        free(states);
        return 1; // 返回1表示重建了网络
    }
    
    // 更新最后构建时间
    builder->last_build_time = now;
    
    return 0;
}

// 获取网络统计信息
void auto_network_builder_get_stats(
    AutoNetworkBuilder* builder,
    int* active_nodes,
    int* inactive_nodes,
    int* total_networks
) {
    if (builder == NULL) {
        return;
    }
    
    if (active_nodes != NULL) {
        *active_nodes = builder->active_nodes_count;
    }
    
    if (inactive_nodes != NULL) {
        *inactive_nodes = builder->inactive_nodes_count;
    }
    
    if (total_networks != NULL) {
        *total_networks = builder->total_networks_built;
    }
}

//----------- 内部辅助函数 ---------------

// 计算两个节点之间的兼容性分数
static double compute_node_compatibility(QuantumNetworkNode* node1, QuantumNetworkNode* node2) {
    if (node1 == NULL || node2 == NULL) {
        return 0.0;
    }
    
    // 计算状态兼容性
    return compute_state_compatibility(node1->state, node2->state);
}

// 计算两个状态之间的兼容性分数
static double compute_state_compatibility(QuantumState* state1, QuantumState* state2) {
    if (state1 == NULL || state2 == NULL) {
        return 0.0;
    }
    
    // 基本类型兼容性
    double type_compatibility = 0.5;
    if (strcmp(state1->type, state2->type) == 0) {
        type_compatibility = 1.0;
    }
    
    // 叠加态兼容性
    double superposition_compatibility = 0.0;
    
    // 计算共同叠加态的数量
    int common_states = 0;
    for (int i = 0; i < state1->superposition_count; i++) {
        for (int j = 0; j < state2->superposition_count; j++) {
            if (strcmp(state1->superpositions[i].state, state2->superpositions[j].state) == 0) {
                common_states++;
                break;
            }
        }
    }
    
    if (state1->superposition_count > 0 && state2->superposition_count > 0) {
        superposition_compatibility = (double)common_states / 
            ((state1->superposition_count + state2->superposition_count) / 2.0);
    }
    
    // 加权计算总兼容性
    return 0.4 * type_compatibility + 0.6 * superposition_compatibility;
}

// 广播发现节点
static int discover_nodes_broadcast(QuantumNetworkNode** nodes_buffer, int buffer_size) {
    // 模拟广播发现过程
    int discovered = 0;
    
    // 这里应该是实际的节点发现逻辑
    // 为了模拟，我们创建一些随机节点
    
    for (int i = 0; i < buffer_size && discovered < buffer_size; i++) {
        QuantumNetworkNode* node = quantum_network_node_create();
        if (node != NULL) {
            // 创建随机状态
            char id[32];
            sprintf(id, "discovered_node_%d", discovered);
            
            QuantumState* state = quantum_state_create(id, "auto_discovered");
            
            // 设置节点状态
            node->state = state;
            node->active = 0; // 默认非激活，等待激活
            
            // 添加到缓冲区
            nodes_buffer[discovered] = node;
            discovered++;
        }
    }
    
    return discovered;
}

// 量子共振发现节点
static int discover_nodes_quantum_resonance(QuantumNetworkNode** nodes_buffer, int buffer_size) {
    // 模拟量子共振发现过程
    // 这是一个更高级的发现过程，可以发现隐藏的节点
    
    int discovered = 0;
    
    // 模拟实现
    for (int i = 0; i < buffer_size && discovered < buffer_size; i++) {
        QuantumNetworkNode* node = quantum_network_node_create();
        if (node != NULL) {
            // 创建随机状态
            char id[32];
            sprintf(id, "resonance_node_%d", discovered);
            
            QuantumState* state = quantum_state_create(id, "quantum_resonant");
            
            // 添加随机叠加态
            const char* possible_states[] = {
                "enlightened", "harmonious", "balanced", "coherent", "quantum"
            };
            int num_states = sizeof(possible_states) / sizeof(possible_states[0]);
            
            int state_count = 1 + rand() % 3; // 1到3个叠加态
            for (int j = 0; j < state_count; j++) {
                int state_idx = rand() % num_states;
                double probability = (double)(rand() % 100) / 100.0;
                quantum_state_add_superposition(state, possible_states[state_idx], probability);
            }
            
            // 设置节点状态
            node->state = state;
            node->active = 0; // 默认非激活，等待激活
            
            // 添加到缓冲区
            nodes_buffer[discovered] = node;
            discovered++;
        }
    }
    
    return discovered;
}

// 默认发现节点方法
static int discover_nodes_default(QuantumNetworkNode** nodes_buffer, int buffer_size) {
    // 最基本的发现方法
    return discover_nodes_broadcast(nodes_buffer, buffer_size / 2);
}

// 重建网络连接
static void rebuild_network_connections(
    AutoNetworkBuilder* builder,
    EntanglementNetwork* network, 
    QuantumState** states,
    int state_count
) {
    if (builder == NULL || network == NULL || states == NULL || state_count <= 0) {
        return;
    }
    
    // 清除所有现有连接
    for (int i = 0; i < network->connection_count; i++) {
        entanglement_destroy(network->connections[i].pair);
    }
    network->connection_count = 0;
    
    // 根据当前策略重新建立连接
    switch (builder->config.strategy) {
        case NETWORK_STRATEGY_FULLY_CONNECTED:
            // 完全连接
            for (int i = 0; i < state_count; i++) {
                for (int j = i + 1; j < state_count; j++) {
                    double strength = builder->config.min_entanglement_strength + 
                                     (1.0 - builder->config.min_entanglement_strength) * ((double)rand() / RAND_MAX);
                    
                    entanglement_network_connect(network, states[i], states[j], strength);
                }
            }
            break;
            
        case NETWORK_STRATEGY_ADAPTIVE:
        default:
            // 自适应连接
            for (int i = 0; i < state_count; i++) {
                int connections = 0;
                
                for (int j = 0; j < state_count && connections < builder->config.max_connections_per_node; j++) {
                    if (i == j) continue;
                    
                    // 计算兼容性
                    double compatibility = compute_state_compatibility(states[i], states[j]);
                    
                    if (compatibility > 0.6) {
                        double strength = builder->config.min_entanglement_strength + 
                                         (compatibility - 0.6) * (1.0 - builder->config.min_entanglement_strength) / 0.4;
                        
                        entanglement_network_connect(network, states[i], states[j], strength);
                        connections++;
                    }
                }
            }
            break;
    }
    
    // 更新最后构建时间
    builder->last_build_time = time(NULL);
} 