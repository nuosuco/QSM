/**
 * QEntL量子网络全局构建器测试文件
 * 
 * @文件: test_global_network_builder.c
 * @描述: 测试量子网络全局构建器的功能
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-18
 * @版本: 1.0
 */

#include "global_network_builder.h"
#include "node_activator.h"
#include "node_manager.h"
#include "../event_system.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// 测试连接确认回调函数
int test_connection_confirm_callback(QNetworkNode* node1, QNetworkNode* node2, 
                                   ConnectionPriority priority, void* user_data) {
    printf("连接确认回调: 节点1=%s, 节点2=%s, 优先级=%d\n", 
           node1->id, node2->id, priority);
    
    // 模拟基于优先级的决策
    if (priority >= CONNECTION_PRIORITY_HIGH) {
        printf("  高优先级连接，自动批准\n");
        return 1;
    } else if (priority == CONNECTION_PRIORITY_NORMAL) {
        // 模拟基于节点类型的决策
        if (node1->type == NODE_TYPE_GATEWAY || node2->type == NODE_TYPE_GATEWAY) {
            printf("  包含网关节点的普通优先级连接，批准\n");
            return 1;
        } else {
            printf("  普通优先级连接，随机决策\n");
            return (rand() % 100 < 80); // 80%的概率批准
        }
    } else {
        printf("  低优先级连接，随机决策\n");
        return (rand() % 100 < 50); // 50%的概率批准
    }
}

// 测试构建完成回调函数
void test_build_complete_callback(GlobalNetworkBuilder* builder, int success,
                                QNetworkNode** nodes, int node_count, void* user_data) {
    printf("构建完成回调: 成功=%d, 节点数=%d\n", success, node_count);
    
    // 打印所有节点
    printf("  节点列表:\n");
    for (int i = 0; i < node_count; i++) {
        printf("  - 节点%d: ID=%s, 类型=%d\n", i, nodes[i]->id, nodes[i]->type);
    }
}

// 测试默认配置和自定义配置
void test_configurations(GlobalNetworkBuilder* builder) {
    printf("\n===== 测试网络构建配置 =====\n");
    
    // 获取默认配置
    NetworkBuilderConfig default_config = global_network_builder_get_config(builder);
    printf("默认配置: 构建模式=%d, 拓扑类型=%d, 自动发现=%d\n", 
           default_config.build_mode, default_config.topology_type, 
           default_config.auto_discovery_enabled);
    
    // 创建自定义配置
    NetworkBuilderConfig custom_config = default_config;
    custom_config.build_mode = NETWORK_BUILD_MODE_SEMI_AUTO;
    custom_config.topology_type = NETWORK_TOPOLOGY_STAR;
    custom_config.max_discovery_depth = 2;
    custom_config.network_stability_threshold = 0.7;
    
    // 设置自定义配置
    if (global_network_builder_set_config(builder, custom_config)) {
        printf("成功设置自定义配置\n");
    } else {
        printf("设置自定义配置失败\n");
    }
    
    // 获取更新后的配置
    NetworkBuilderConfig current_config = global_network_builder_get_config(builder);
    printf("更新后的配置: 构建模式=%d, 拓扑类型=%d, 稳定性阈值=%f\n", 
           current_config.build_mode, current_config.topology_type, 
           current_config.network_stability_threshold);
}

// 测试种子节点添加
void test_seed_nodes(GlobalNetworkBuilder* builder, NodeManager* node_manager) {
    printf("\n===== 测试种子节点添加 =====\n");
    
    // 创建测试节点
    QNetworkNode* seed1 = node_manager_create_node(node_manager, "种子节点1", NODE_TYPE_GATEWAY);
    QNetworkNode* seed2 = node_manager_create_node(node_manager, "种子节点2", NODE_TYPE_STANDARD);
    
    printf("已创建种子节点: seed1(ID=%s), seed2(ID=%s)\n", seed1->id, seed2->id);
    
    // 添加种子节点
    if (global_network_builder_add_seed_node(builder, seed1)) {
        printf("成功添加种子节点1\n");
    } else {
        printf("添加种子节点1失败\n");
    }
    
    if (global_network_builder_add_seed_node(builder, seed2)) {
        printf("成功添加种子节点2\n");
    } else {
        printf("添加种子节点2失败\n");
    }
    
    // 获取拓扑
    NetworkTopology* topology = global_network_builder_get_topology(builder);
    int node_count, connection_count;
    double avg_connections, density;
    
    network_topology_get_stats(topology, &node_count, &connection_count, 
                            &avg_connections, &density);
    
    printf("网络拓扑统计: 节点数=%d, 连接数=%d, 平均连接数=%f, 密度=%f\n",
           node_count, connection_count, avg_connections, density);
}

// 测试节点连接
void test_node_connections(GlobalNetworkBuilder* builder, NodeManager* node_manager) {
    printf("\n===== 测试节点连接 =====\n");
    
    // 创建更多测试节点
    QNetworkNode* node3 = node_manager_create_node(node_manager, "测试节点3", NODE_TYPE_STANDARD);
    QNetworkNode* node4 = node_manager_create_node(node_manager, "测试节点4", NODE_TYPE_BRIDGE);
    QNetworkNode* node5 = node_manager_create_node(node_manager, "测试节点5", NODE_TYPE_STANDARD);
    
    printf("已创建额外节点: node3(ID=%s), node4(ID=%s), node5(ID=%s)\n",
           node3->id, node4->id, node5->id);
    
    // 将节点添加到网络
    global_network_builder_add_seed_node(builder, node3);
    global_network_builder_add_seed_node(builder, node4);
    global_network_builder_add_seed_node(builder, node5);
    
    // 手动连接一些节点
    if (global_network_builder_connect_nodes(builder, node3, node4, 0.8)) {
        printf("成功连接 node3 和 node4 (强度=0.8)\n");
    } else {
        printf("连接 node3 和 node4 失败\n");
    }
    
    if (global_network_builder_connect_nodes(builder, node4, node5, 0.6)) {
        printf("成功连接 node4 和 node5 (强度=0.6)\n");
    } else {
        printf("连接 node4 和 node5 失败\n");
    }
    
    // 尝试连接已连接的节点
    if (global_network_builder_connect_nodes(builder, node3, node4, 0.9)) {
        printf("成功更新 node3 和 node4 的连接 (强度=0.9)\n");
    } else {
        printf("更新 node3 和 node4 的连接失败\n");
    }
    
    // 断开连接
    if (global_network_builder_disconnect_nodes(builder, node4, node5)) {
        printf("成功断开 node4 和 node5 的连接\n");
    } else {
        printf("断开 node4 和 node5 的连接失败\n");
    }
    
    // 获取拓扑统计
    NetworkTopology* topology = global_network_builder_get_topology(builder);
    int node_count, connection_count;
    double avg_connections, density;
    
    network_topology_get_stats(topology, &node_count, &connection_count, 
                            &avg_connections, &density);
    
    printf("操作后的网络拓扑统计: 节点数=%d, 连接数=%d\n",
           node_count, connection_count);
    
    // 计算网络指标
    double reliability = network_topology_calculate_reliability(topology);
    double efficiency = network_topology_calculate_efficiency(topology);
    
    printf("网络指标: 可靠性=%f, 效率=%f\n", reliability, efficiency);
}

// 测试网络构建过程
void test_network_building(GlobalNetworkBuilder* builder) {
    printf("\n===== 测试网络构建过程 =====\n");
    
    // 启动网络构建
    if (global_network_builder_start(builder)) {
        printf("成功启动网络构建\n");
    } else {
        printf("启动网络构建失败\n");
    }
    
    // 处理几个构建周期
    printf("处理构建周期...\n");
    int cycle1 = global_network_builder_process_cycle(builder);
    printf("第1个周期: 建立了 %d 个连接\n", cycle1);
    
    int cycle2 = global_network_builder_process_cycle(builder);
    printf("第2个周期: 建立了 %d 个连接\n", cycle2);
    
    int cycle3 = global_network_builder_process_cycle(builder);
    printf("第3个周期: 建立了 %d 个连接\n", cycle3);
    
    // 获取构建统计
    NetworkBuildingStats stats = global_network_builder_get_stats(builder);
    printf("构建统计: 构建尝试=%d, 成功构建=%d, 失败构建=%d\n",
           stats.total_build_attempts, stats.successful_builds, stats.failed_builds);
    printf("           发现节点=%d, 建立连接=%d, 网络稳定性=%f\n",
           stats.nodes_discovered, stats.connections_established, stats.network_stability);
    
    // 停止网络构建
    if (global_network_builder_stop(builder)) {
        printf("成功停止网络构建\n");
    } else {
        printf("停止网络构建失败\n");
    }
}

// 测试拓扑类型变更
void test_topology_change(GlobalNetworkBuilder* builder) {
    printf("\n===== 测试拓扑类型变更 =====\n");
    
    // 获取当前拓扑类型
    NetworkTopology* topology = global_network_builder_get_topology(builder);
    printf("当前拓扑类型: %d\n", topology->type);
    
    // 更改拓扑类型
    if (global_network_builder_set_topology_type(builder, NETWORK_TOPOLOGY_RING)) {
        printf("成功将拓扑类型更改为环形(RING)\n");
    } else {
        printf("更改拓扑类型失败\n");
    }
    
    // 处理一个构建周期，应用新拓扑
    global_network_builder_start(builder);
    int connections = global_network_builder_process_cycle(builder);
    printf("使用新拓扑处理了构建周期，建立了 %d 个连接\n", connections);
    global_network_builder_stop(builder);
    
    // 获取更新后的拓扑类型
    printf("更新后的拓扑类型: %d\n", topology->type);
}

// 测试网络修复
void test_network_repair(GlobalNetworkBuilder* builder) {
    printf("\n===== 测试网络修复 =====\n");
    
    // 模拟网络问题
    NetworkTopology* topology = global_network_builder_get_topology(builder);
    printf("修复前的网络稳定性: %f\n", topology->reliability);
    
    // 模拟连接失活
    if (topology->connection_count > 0) {
        printf("模拟网络问题: 正在使一个连接失活\n");
        topology->connections[0]->is_active = 0;
    }
    
    // 运行网络修复
    int repaired = global_network_builder_repair_network(builder);
    printf("修复了 %d 个网络问题\n", repaired);
    
    // 检查修复后的状态
    double reliability = network_topology_calculate_reliability(topology);
    printf("修复后的网络稳定性: %f\n", reliability);
}

// 测试保存和加载拓扑
void test_topology_save_load(GlobalNetworkBuilder* builder) {
    printf("\n===== 测试拓扑保存和加载 =====\n");
    
    // 保存拓扑到文件
    const char* filename = "test_topology.dat";
    if (global_network_builder_save_topology(builder, filename)) {
        printf("成功将拓扑保存到文件 %s\n", filename);
    } else {
        printf("保存拓扑失败\n");
    }
    
    // 尝试加载拓扑
    if (global_network_builder_load_topology(builder, filename)) {
        printf("成功从文件 %s 加载拓扑\n", filename);
    } else {
        printf("加载拓扑失败或功能未实现\n");
    }
}

// 主函数
int main(int argc, char* argv[]) {
    printf("=== QEntL量子网络全局构建器测试 ===\n\n");
    
    // 初始化随机数生成器
    srand((unsigned int)time(NULL));
    
    // 创建事件系统
    EventSystem* event_system = event_system_create();
    if (!event_system) {
        fprintf(stderr, "无法创建事件系统\n");
        return 1;
    }
    
    // 创建节点管理器
    NodeManager* node_manager = node_manager_create();
    if (!node_manager) {
        fprintf(stderr, "无法创建节点管理器\n");
        event_system_destroy(event_system);
        return 1;
    }
    
    // 创建节点激活器
    NodeActivator* node_activator = node_activator_create(event_system);
    if (!node_activator) {
        fprintf(stderr, "无法创建节点激活器\n");
        node_manager_destroy(node_manager);
        event_system_destroy(event_system);
        return 1;
    }
    
    // 创建全局网络构建器
    GlobalNetworkBuilder* builder = global_network_builder_create(node_activator, event_system);
    if (!builder) {
        fprintf(stderr, "无法创建全局网络构建器\n");
        node_activator_destroy(node_activator);
        node_manager_destroy(node_manager);
        event_system_destroy(event_system);
        return 1;
    }
    
    // 注册测试回调
    global_network_builder_register_confirm_callback(builder, test_connection_confirm_callback, NULL);
    global_network_builder_register_complete_callback(builder, test_build_complete_callback, NULL);
    
    // 运行测试
    test_configurations(builder);
    test_seed_nodes(builder, node_manager);
    test_node_connections(builder, node_manager);
    test_network_building(builder);
    test_topology_change(builder);
    test_network_repair(builder);
    test_topology_save_load(builder);
    
    // 清理资源
    global_network_builder_destroy(builder);
    node_activator_destroy(node_activator);
    node_manager_destroy(node_manager);
    event_system_destroy(event_system);
    
    printf("\n=== 测试完成 ===\n");
    return 0;
} 