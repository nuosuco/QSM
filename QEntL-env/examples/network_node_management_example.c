/**
 * 量子网络节点管理示例程序
 * 
 * 本示例演示了QEntL环境中量子网络节点管理器的各种功能，包括：
 * - 创建和初始化节点管理器
 * - 创建不同类型的量子节点（状态节点、纠缠节点、场节点）
 * - 连接节点形成网络
 * - 管理节点状态（激活、停用、暂停、恢复）
 * - 检测和恢复故障节点
 * - 自动优化网络拓扑
 * - 分析网络结构
 * 
 * 编译命令：gcc -o node_management_example network_node_management_example.c -lqentl_runtime -lm
 * 运行命令：./node_management_example
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../runtime/quantum_network/node_manager.h"
#include "../quantum_state.h"
#include "../quantum_field.h"
#include "../entanglement_channel.h"

// 辅助函数：创建样例量子状态
QuantumState* create_sample_quantum_state(const char* name) {
    // 此处简化实现，实际应用中应使用QEntL量子状态创建API
    QuantumState* state = (QuantumState*)malloc(sizeof(QuantumState));
    if (!state) return NULL;
    
    state->id.id_string = strdup("state_id");
    state->id.readable_id = strdup(name);
    state->dimensions = 2; // 量子比特
    state->properties = NULL;
    state->property_count = 0;
    
    return state;
}

// 辅助函数：创建样例纠缠通道
EntanglementChannel* create_sample_entanglement_channel(const char* name) {
    // 此处简化实现，实际应用中应使用QEntL纠缠通道创建API
    EntanglementChannel* channel = (EntanglementChannel*)malloc(sizeof(EntanglementChannel));
    if (!channel) return NULL;
    
    channel->id.id_string = strdup("channel_id");
    channel->id.readable_id = strdup(name);
    channel->entanglement_strength = 0.8;
    channel->entanglement_type = ENTANGLEMENT_TYPE_QUANTUM;
    channel->last_refresh_time = time(NULL);
    
    return channel;
}

// 辅助函数：创建样例量子场
QuantumField* create_sample_quantum_field(const char* name) {
    // 此处简化实现，实际应用中应使用QEntL量子场创建API
    QuantumField* field = (QuantumField*)malloc(sizeof(QuantumField));
    if (!field) return NULL;
    
    field->id.id_string = strdup("field_id");
    field->id.readable_id = strdup(name);
    field->field_type = QUANTUM_FIELD_TYPE_DETERMINISTIC;
    field->dimensions = 3;
    field->node_count = 0;
    field->nodes = NULL;
    
    return field;
}

// 辅助函数：打印节点信息
void print_node_info(NodeInfo info) {
    printf("-------------------------------------\n");
    printf("节点ID: %s\n", info.id.readable_id);
    printf("名称: %s\n", info.name);
    printf("描述: %s\n", info.description);
    printf("创建时间: %s\n", info.creation_time);
    printf("最后更新: %s\n", info.last_update_time);
    printf("版本: %d\n", info.version);
    
    // 打印节点类型
    printf("类型: ");
    switch (info.type) {
        case NETWORK_NODE_TYPE_STATE:
            printf("量子状态节点\n");
            break;
        case NETWORK_NODE_TYPE_ENTANGLEMENT:
            printf("量子纠缠节点\n");
            break;
        case NETWORK_NODE_TYPE_FIELD:
            printf("量子场节点\n");
            break;
        default:
            printf("其他类型节点\n");
    }
    
    // 打印节点状态
    printf("状态: ");
    switch (info.status) {
        case QUANTUM_NETWORK_NODE_STATUS_ACTIVE:
            printf("活跃\n");
            break;
        case QUANTUM_NETWORK_NODE_STATUS_INACTIVE:
            printf("非活跃\n");
            break;
        case QUANTUM_NETWORK_NODE_STATUS_SUSPENDED:
            printf("已暂停\n");
            break;
        case QUANTUM_NETWORK_NODE_STATUS_ERROR:
            printf("错误\n");
            break;
        default:
            printf("未知\n");
    }
    
    printf("连接数: %d\n", info.connection_count);
    printf("处理能力: %.2f\n", info.processing_capacity);
    printf("存储容量: %.2f\n", info.storage_capacity);
    printf("相干时间: %.2f\n", info.coherence_time);
    printf("错误率: %.2f%%\n", info.error_rate * 100.0);
    printf("-------------------------------------\n");
}

// 辅助函数：模拟节点错误
void simulate_node_error(QuantumNetworkNode* node, int error_code) {
    node->status = QUANTUM_NETWORK_NODE_STATUS_ERROR;
    node->last_error_code = error_code;
    node->last_error_time = time(NULL);
    node->error_count++;
    
    printf("模拟节点 %s 发生错误, 错误代码: %d\n", node->id.readable_id, error_code);
}

int main() {
    printf("量子网络节点管理示例程序\n");
    printf("==================================\n\n");
    
    // 初始化随机数生成器
    srand(time(NULL));
    
    // 1. 初始化节点管理器
    printf("初始化量子网络节点管理器...\n");
    NodeManagerConfig config = get_default_node_manager_config();
    config.initial_capacity = 20;  // 设置初始容量
    
    NodeManager* manager = initialize_node_manager(config, NULL);
    if (!manager) {
        printf("初始化节点管理器失败，程序退出\n");
        return 1;
    }
    printf("节点管理器初始化成功 (ID: %s)\n\n", manager->manager_id);
    
    // 2. 创建不同类型的节点
    printf("创建量子网络节点...\n");
    
    // 创建量子状态节点
    NodeCreationOptions state_options = get_default_node_creation_options();
    state_options.name = "量子态节点A";
    state_options.description = "存储量子比特状态的节点";
    state_options.tags = "quantum,state,qubit";
    
    QuantumState* state_a = create_sample_quantum_state("状态A");
    NodeReference* state_node_a = create_state_node(manager, state_a, state_options);
    
    // 再创建一个量子状态节点
    state_options.name = "量子态节点B";
    QuantumState* state_b = create_sample_quantum_state("状态B");
    NodeReference* state_node_b = create_state_node(manager, state_b, state_options);
    
    // 创建纠缠节点
    NodeCreationOptions entanglement_options = get_default_node_creation_options();
    entanglement_options.name = "纠缠通道节点";
    entanglement_options.description = "连接两个量子状态的纠缠通道";
    entanglement_options.tags = "entanglement,channel,quantum";
    entanglement_options.coherence_time = 1500.0; // 更长的相干时间
    
    EntanglementChannel* channel = create_sample_entanglement_channel("主纠缠通道");
    NodeReference* entanglement_node = create_entanglement_node_with_options(manager, channel, entanglement_options);
    
    // 创建量子场节点
    NodeCreationOptions field_options = get_default_node_creation_options();
    field_options.name = "量子场节点";
    field_options.description = "表示量子场的节点";
    field_options.tags = "field,quantum,space";
    field_options.processing_capacity = 1.5; // 更高的处理能力
    
    QuantumField* field = create_sample_quantum_field("主量子场");
    NodeReference* field_node = create_field_node(manager, field, field_options);
    
    printf("成功创建4个节点\n\n");
    
    // 3. 连接节点形成网络
    printf("连接节点形成网络...\n");
    
    // 连接量子态节点A到纠缠节点
    connect_nodes(manager, state_node_a, entanglement_node, 0.8);
    
    // 连接量子态节点B到纠缠节点
    connect_nodes(manager, state_node_b, entanglement_node, 0.8);
    
    // 连接纠缠节点到场节点
    connect_nodes(manager, entanglement_node, field_node, 0.7);
    
    // 连接量子态节点A到场节点
    connect_nodes(manager, state_node_a, field_node, 0.6);
    
    printf("节点连接成功，形成简单网络\n\n");
    
    // 4. 激活所有节点
    printf("激活所有节点...\n");
    activate_node(manager, state_node_a);
    activate_node(manager, state_node_b);
    activate_node(manager, entanglement_node);
    activate_node(manager, field_node);
    printf("所有节点已激活\n\n");
    
    // 5. 查看节点信息
    printf("查看状态节点A信息:\n");
    NodeInfo info_a = get_node_info(manager, state_node_a);
    print_node_info(info_a);
    
    printf("查看纠缠节点信息:\n");
    NodeInfo info_e = get_node_info(manager, entanglement_node);
    print_node_info(info_e);
    
    // 6. 模拟暂停节点
    printf("暂停状态节点B 10秒...\n");
    suspend_node(manager, state_node_b, 10); // 暂停10秒
    
    // 查看暂停后节点状态
    NodeInfo info_b = get_node_info(manager, state_node_b);
    printf("暂停后状态节点B信息:\n");
    print_node_info(info_b);
    
    // 7. 尝试恢复暂停节点
    printf("尝试恢复状态节点B...\n");
    
    // 如果您在真实环境中运行，可以等待暂停时间结束
    // 此处为了演示，我们直接调用detect_and_recover_node
    NodeManagerError recovery_result = detect_and_recover_node(manager, state_node_b);
    
    if (recovery_result == NODE_MANAGER_ERROR_NODE_SUSPENDED) {
        printf("节点仍处于暂停状态，无法恢复\n");
        
        // 在实际应用中，您可以使用以下代码等待暂停结束
        // printf("等待暂停时间结束...\n");
        // sleep(10);
        
        // 为了演示，我们手动重置节点状态
        QuantumNetworkNode* node_b = (QuantumNetworkNode*)state_node_b->node_ptr;
        node_b->status = QUANTUM_NETWORK_NODE_STATUS_INACTIVE;
        node_b->suspension_end_time = 0;
        
        printf("手动重置节点状态后尝试恢复...\n");
        recovery_result = activate_node(manager, state_node_b);
        
        if (recovery_result == NODE_MANAGER_ERROR_NONE) {
            printf("节点成功恢复\n");
        } else {
            printf("节点恢复失败，错误码: %d\n", recovery_result);
        }
    } else if (recovery_result == NODE_MANAGER_ERROR_NONE) {
        printf("节点成功恢复\n");
    } else {
        printf("节点恢复失败，错误码: %d\n", recovery_result);
    }
    
    // 8. 模拟节点故障和恢复
    printf("\n模拟纠缠节点故障...\n");
    QuantumNetworkNode* entanglement_node_ptr = (QuantumNetworkNode*)entanglement_node->node_ptr;
    simulate_node_error(entanglement_node_ptr, QUANTUM_NODE_ERROR_ENTANGLEMENT_BREAK);
    
    // 查看故障节点状态
    info_e = get_node_info(manager, entanglement_node);
    printf("故障后纠缠节点信息:\n");
    print_node_info(info_e);
    
    // 恢复故障节点
    printf("尝试恢复纠缠节点...\n");
    recovery_result = detect_and_recover_node(manager, entanglement_node);
    
    if (recovery_result == NODE_MANAGER_ERROR_NONE) {
        printf("纠缠节点成功恢复\n");
        
        // 查看恢复后状态
        info_e = get_node_info(manager, entanglement_node);
        printf("恢复后纠缠节点信息:\n");
        print_node_info(info_e);
    } else {
        printf("纠缠节点恢复失败，错误码: %d\n", recovery_result);
    }
    
    // 9. 分析网络拓扑
    printf("\n分析网络拓扑...\n");
    NetworkTopologyAnalysis* analysis = analyze_network_topology(manager);
    
    if (analysis) {
        printf("网络拓扑分析结果:\n");
        printf("总节点数: %d\n", analysis->total_nodes);
        printf("活跃节点数: %d\n", analysis->active_nodes);
        printf("非活跃节点数: %d\n", analysis->inactive_nodes);
        printf("暂停节点数: %d\n", analysis->suspended_nodes);
        printf("错误节点数: %d\n", analysis->error_nodes);
        printf("总连接数: %d\n", analysis->total_connections);
        printf("最大连接数: %d (节点: %s)\n", analysis->max_connections, analysis->most_connected_node);
        printf("平均连接数: %.2f\n", analysis->avg_connections);
        printf("平均能量水平: %.2f\n", analysis->avg_energy_level);
        printf("平均稳定性: %.2f\n", analysis->avg_stability);
        printf("网络集群数: %d\n", analysis->clusters);
        printf("网络纠缠度: %.2f\n", analysis->network_entanglement);
        printf("网络健康度: %.2f\n", analysis->network_health);
        
        free_network_topology_analysis(analysis);
    } else {
        printf("网络拓扑分析失败\n");
    }
    
    // 10. 自动优化网络拓扑
    printf("\n自动优化网络拓扑...\n");
    NodeManagerError optimize_result = optimize_network_topology(manager);
    
    if (optimize_result == NODE_MANAGER_ERROR_NONE) {
        printf("网络拓扑优化成功\n");
        
        // 再次分析优化后的网络
        analysis = analyze_network_topology(manager);
        if (analysis) {
            printf("优化后网络健康度: %.2f\n", analysis->network_health);
            free_network_topology_analysis(analysis);
        }
    } else {
        printf("网络拓扑优化失败，错误码: %d\n", optimize_result);
    }
    
    // 11. 清理资源
    printf("\n清理资源...\n");
    shutdown_node_manager(manager);
    printf("节点管理器已关闭\n");
    
    printf("\n示例程序完成\n");
    return 0;
} 