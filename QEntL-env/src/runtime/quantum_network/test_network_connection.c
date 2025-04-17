/**
 * 量子网络连接管理器测试程序
 * 
 * 本程序测试QEntL网络连接管理器的基本功能：
 * - 创建和配置连接管理器
 * - 建立节点连接
 * - 获取和修改连接状态
 * - 优化连接
 * - 连接事件回调
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "network_connection_manager.h"
#include "node_activator.h"
#include "global_network_builder.h"
#include "../event_system.h"

/* 测试用节点结构 */
typedef struct TestNode {
    char id[32];
    int active;
    double quantum_capacity;
    int connected_nodes;
} TestNode;

/* 创建测试节点 */
QNetworkNode* create_test_node(const char* id) {
    QNetworkNode* node = (QNetworkNode*)malloc(sizeof(QNetworkNode));
    if (!node) {
        fprintf(stderr, "无法分配节点内存\n");
        return NULL;
    }
    
    /* 设置ID */
    node->id = strdup(id);
    
    /* 设置基本属性 */
    node->type = QNETWORK_NODE_COMPUTATIONAL;
    node->status = NODE_STATUS_ACTIVE;
    
    /* 在这里可以设置更多节点属性 */
    
    return node;
}

/* 销毁测试节点 */
void destroy_test_node(QNetworkNode* node) {
    if (!node) return;
    
    /* 释放资源 */
    if (node->id) free(node->id);
    
    /* 释放节点本身 */
    free(node);
}

/* 连接事件回调函数 */
void connection_event_callback(QNetworkNode* source, 
                             QNetworkNode* target, 
                             ConnectionState state,
                             void* user_data) {
    printf("连接事件: 源=%s, 目标=%s, 状态=%d\n", 
           source->id, target->id, state);
    
    /* 可以根据状态执行不同操作 */
    switch (state) {
        case CONNECTION_STATE_CONNECTING:
            printf("  连接建立中...\n");
            break;
        case CONNECTION_STATE_ACTIVE:
            printf("  连接已激活\n");
            break;
        case CONNECTION_STATE_DEGRADED:
            printf("  连接性能下降\n");
            break;
        case CONNECTION_STATE_FAILED:
            printf("  连接失败\n");
            break;
        case CONNECTION_STATE_CLOSING:
            printf("  连接关闭中\n");
            break;
        default:
            printf("  未知连接状态\n");
            break;
    }
}

/* 测试配置功能 */
void test_configuration(NetworkConnectionManager* manager) {
    printf("\n===== 测试配置功能 =====\n");
    
    /* 获取默认配置 */
    ConnectionConfig default_config = network_connection_manager_get_config(manager);
    printf("默认配置:\n");
    printf("  自动连接: %d\n", default_config.auto_connect);
    printf("  最大连接数: %d\n", default_config.max_connections);
    printf("  优化策略: %d\n", default_config.opt_strategy);
    printf("  优化间隔: %d 秒\n", default_config.optimization_interval);
    printf("  连接强度阈值: %.2f\n", default_config.strength_threshold);
    
    /* 设置新配置 */
    ConnectionConfig new_config = default_config;
    new_config.auto_connect = 0;
    new_config.max_connections = 500;
    new_config.opt_strategy = CONN_OPT_STRENGTH;
    new_config.optimization_interval = 30;
    new_config.strength_threshold = 0.7;
    
    int result = network_connection_manager_set_config(manager, new_config);
    printf("设置新配置 %s\n", result ? "成功" : "失败");
    
    /* 获取并验证新配置 */
    ConnectionConfig updated_config = network_connection_manager_get_config(manager);
    printf("更新后的配置:\n");
    printf("  自动连接: %d\n", updated_config.auto_connect);
    printf("  最大连接数: %d\n", updated_config.max_connections);
    printf("  优化策略: %d\n", updated_config.opt_strategy);
    printf("  优化间隔: %d 秒\n", updated_config.optimization_interval);
    printf("  连接强度阈值: %.2f\n", updated_config.strength_threshold);
}

/* 测试连接创建功能 */
void test_connection_creation(NetworkConnectionManager* manager, 
                            QNetworkNode** nodes, 
                            int node_count) {
    printf("\n===== 测试连接创建功能 =====\n");
    
    /* 创建几个连接 */
    for (int i = 0; i < node_count - 1; i++) {
        for (int j = i + 1; j < node_count; j++) {
            if (rand() % 2 == 0) {  /* 50%概率创建连接 */
                double strength = 0.5 + ((double)rand() / RAND_MAX) * 0.5;  /* 0.5-1.0范围 */
                int result = network_connection_manager_create_connection(manager, 
                                                                      nodes[i], 
                                                                      nodes[j], 
                                                                      CONNECTION_TYPE_DIRECT, 
                                                                      strength);
                
                printf("创建连接: %s -> %s, 强度=%.2f, %s\n", 
                       nodes[i]->id, nodes[j]->id, strength, 
                       result ? "成功" : "失败");
            }
        }
    }
    
    /* 测试获取连接状态 */
    printf("\n连接状态检查:\n");
    for (int i = 0; i < node_count - 1; i++) {
        for (int j = i + 1; j < node_count; j++) {
            ConnectionState state = network_connection_manager_get_connection_state(manager, 
                                                                                nodes[i], 
                                                                                nodes[j]);
            
            if (state != CONNECTION_STATE_INACTIVE) {
                double strength = network_connection_manager_get_connection_strength(manager, 
                                                                                 nodes[i], 
                                                                                 nodes[j]);
                
                printf("  连接 %s -> %s: 状态=%d, 强度=%.2f\n", 
                       nodes[i]->id, nodes[j]->id, state, strength);
            }
        }
    }
}

/* 测试连接强度调整功能 */
void test_strength_adjustment(NetworkConnectionManager* manager, 
                            QNetworkNode** nodes, 
                            int node_count) {
    printf("\n===== 测试连接强度调整功能 =====\n");
    
    /* 随机选择一些连接调整强度 */
    for (int i = 0; i < node_count - 1; i++) {
        for (int j = i + 1; j < node_count; j++) {
            ConnectionState state = network_connection_manager_get_connection_state(manager, 
                                                                                nodes[i], 
                                                                                nodes[j]);
            
            if (state == CONNECTION_STATE_ACTIVE) {
                /* 获取当前强度 */
                double current_strength = network_connection_manager_get_connection_strength(manager, 
                                                                                        nodes[i], 
                                                                                        nodes[j]);
                
                /* 随机调整强度 */
                double adjustment = ((double)rand() / RAND_MAX) * 0.4 - 0.2;  /* -0.2到0.2范围 */
                double new_strength = current_strength + adjustment;
                
                /* 确保在有效范围内 */
                if (new_strength < 0.1) new_strength = 0.1;
                if (new_strength > 1.0) new_strength = 1.0;
                
                /* 设置新强度 */
                int result = network_connection_manager_set_connection_strength(manager, 
                                                                            nodes[i], 
                                                                            nodes[j], 
                                                                            new_strength);
                
                printf("调整连接强度: %s -> %s, %.2f -> %.2f, %s\n", 
                       nodes[i]->id, nodes[j]->id, 
                       current_strength, new_strength, 
                       result ? "成功" : "失败");
                
                /* 获取调整后的状态 */
                ConnectionState new_state = network_connection_manager_get_connection_state(manager, 
                                                                                        nodes[i], 
                                                                                        nodes[j]);
                
                printf("  调整后状态: %d\n", new_state);
            }
        }
    }
    
    /* 打印统计信息 */
    ConnectionStats stats = network_connection_manager_get_stats(manager);
    printf("\n连接统计:\n");
    printf("  总连接数: %d\n", stats.total_connections);
    printf("  活跃连接数: %d\n", stats.active_connections);
    printf("  性能下降连接数: %d\n", stats.degraded_connections);
    printf("  平均连接强度: %.2f\n", stats.average_strength);
}

/* 测试连接优化功能 */
void test_connection_optimization(NetworkConnectionManager* manager) {
    printf("\n===== 测试连接优化功能 =====\n");
    
    /* 获取优化前的统计 */
    ConnectionStats before_stats = network_connection_manager_get_stats(manager);
    printf("优化前统计:\n");
    printf("  总连接数: %d\n", before_stats.total_connections);
    printf("  活跃连接数: %d\n", before_stats.active_connections);
    printf("  性能下降连接数: %d\n", before_stats.degraded_connections);
    printf("  平均连接强度: %.2f\n", before_stats.average_strength);
    
    /* 尝试不同的优化策略 */
    ConnectionOptStrategy strategies[] = {
        CONN_OPT_STRENGTH,
        CONN_OPT_RELIABILITY,
        CONN_OPT_BALANCED
    };
    
    for (int i = 0; i < 3; i++) {
        printf("\n尝试优化策略: %d\n", strategies[i]);
        int result = network_connection_manager_optimize_connections(manager, strategies[i]);
        printf("优化结果: %s\n", result ? "成功" : "失败");
        
        /* 获取优化后的统计 */
        ConnectionStats after_stats = network_connection_manager_get_stats(manager);
        printf("优化后统计:\n");
        printf("  总连接数: %d\n", after_stats.total_connections);
        printf("  活跃连接数: %d\n", after_stats.active_connections);
        printf("  性能下降连接数: %d\n", after_stats.degraded_connections);
        printf("  平均连接强度: %.2f\n", after_stats.average_strength);
    }
}

/* 测试连接关闭功能 */
void test_connection_closing(NetworkConnectionManager* manager, 
                           QNetworkNode** nodes, 
                           int node_count) {
    printf("\n===== 测试连接关闭功能 =====\n");
    
    /* 随机关闭一些连接 */
    int closed_count = 0;
    for (int i = 0; i < node_count - 1; i++) {
        for (int j = i + 1; j < node_count; j++) {
            ConnectionState state = network_connection_manager_get_connection_state(manager, 
                                                                                nodes[i], 
                                                                                nodes[j]);
            
            if (state != CONNECTION_STATE_INACTIVE && rand() % 3 == 0) {  /* 1/3概率关闭 */
                int result = network_connection_manager_close_connection(manager, 
                                                                      nodes[i], 
                                                                      nodes[j]);
                
                printf("关闭连接: %s -> %s, %s\n", 
                       nodes[i]->id, nodes[j]->id, 
                       result ? "成功" : "失败");
                
                if (result) closed_count++;
            }
        }
    }
    
    printf("共关闭了 %d 个连接\n", closed_count);
    
    /* 获取关闭后的统计 */
    ConnectionStats stats = network_connection_manager_get_stats(manager);
    printf("\n关闭后统计:\n");
    printf("  总连接数: %d\n", stats.total_connections);
    printf("  活跃连接数: %d\n", stats.active_connections);
    printf("  性能下降连接数: %d\n", stats.degraded_connections);
}

/* 测试状态保存功能 */
void test_state_saving(NetworkConnectionManager* manager) {
    printf("\n===== 测试状态保存功能 =====\n");
    
    /* 保存状态到文件 */
    const char* filename = "connection_state.txt";
    int result = network_connection_manager_save_state(manager, filename);
    
    printf("保存状态到文件 %s: %s\n", filename, result ? "成功" : "失败");
}

int main(int argc, char* argv[]) {
    printf("=== QEntL量子网络连接管理器测试 ===\n\n");
    
    /* 初始化随机数生成器 */
    srand((unsigned int)time(NULL));
    
    /* 创建事件系统 */
    EventSystem* event_system = event_system_create();
    if (!event_system) {
        fprintf(stderr, "无法创建事件系统\n");
        return 1;
    }
    
    /* 创建节点激活器 */
    NodeActivator* node_activator = node_activator_create(event_system);
    if (!node_activator) {
        fprintf(stderr, "无法创建节点激活器\n");
        event_system_destroy(event_system);
        return 1;
    }
    
    /* 创建全局网络构建器 */
    GlobalNetworkBuilder* network_builder = global_network_builder_create(node_activator, event_system);
    if (!network_builder) {
        fprintf(stderr, "无法创建全局网络构建器\n");
        node_activator_destroy(node_activator);
        event_system_destroy(event_system);
        return 1;
    }
    
    /* 创建连接管理器 */
    NetworkConnectionManager* manager = network_connection_manager_create(network_builder, event_system);
    if (!manager) {
        fprintf(stderr, "无法创建连接管理器\n");
        global_network_builder_destroy(network_builder);
        node_activator_destroy(node_activator);
        event_system_destroy(event_system);
        return 1;
    }
    
    /* 注册连接事件回调 */
    network_connection_manager_register_callback(manager, connection_event_callback, NULL);
    
    /* 创建测试节点 */
    const int NODE_COUNT = 5;
    QNetworkNode* nodes[NODE_COUNT];
    
    for (int i = 0; i < NODE_COUNT; i++) {
        char node_id[32];
        sprintf(node_id, "TestNode%d", i + 1);
        nodes[i] = create_test_node(node_id);
        
        if (!nodes[i]) {
            fprintf(stderr, "无法创建测试节点 %d\n", i + 1);
            for (int j = 0; j < i; j++) {
                destroy_test_node(nodes[j]);
            }
            network_connection_manager_destroy(manager);
            global_network_builder_destroy(network_builder);
            node_activator_destroy(node_activator);
            event_system_destroy(event_system);
            return 1;
        }
    }
    
    /* 运行测试 */
    test_configuration(manager);
    test_connection_creation(manager, nodes, NODE_COUNT);
    test_strength_adjustment(manager, nodes, NODE_COUNT);
    test_connection_optimization(manager);
    test_connection_closing(manager, nodes, NODE_COUNT);
    test_state_saving(manager);
    
    /* 清理资源 */
    for (int i = 0; i < NODE_COUNT; i++) {
        destroy_test_node(nodes[i]);
    }
    
    network_connection_manager_destroy(manager);
    global_network_builder_destroy(network_builder);
    node_activator_destroy(node_activator);
    event_system_destroy(event_system);
    
    printf("\n测试完成!\n");
    
    return 0;
} 