/**
 * QEntL量子网络节点自动激活系统测试文件
 * 
 * @文件: test_node_activator.c
 * @描述: 测试节点自动激活系统的功能
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-18
 * @版本: 1.0
 */

#include "node_activator.h"
#include "node_manager.h"
#include "../event_system.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// 测试回调函数
int test_activation_callback(QNetworkNode* node, NodeActivationState state, void* user_data) {
    printf("节点激活回调: ID=%s, 状态=%d\n", node->id, state);
    return 1;
}

// 测试默认策略设置
void test_default_policy(NodeActivator* activator) {
    printf("\n===== 测试默认策略设置 =====\n");
    
    // 获取默认策略
    ActivationPolicy default_policy = node_activator_get_default_policy(activator);
    printf("默认策略: 模式=%d, 优先级=%d, 自动恢复=%d\n", 
           default_policy.mode, default_policy.priority, default_policy.auto_recovery);
    
    // 修改默认策略
    ActivationPolicy new_policy = default_policy;
    new_policy.mode = ACTIVATION_MODE_AUTO_DISCOVERY;
    new_policy.priority = ACTIVATION_PRIORITY_HIGH;
    new_policy.max_retry_count = 5;
    
    if (node_activator_set_default_policy(activator, new_policy)) {
        printf("成功设置新的默认策略\n");
    } else {
        printf("设置默认策略失败\n");
    }
    
    // 再次获取默认策略确认更改
    default_policy = node_activator_get_default_policy(activator);
    printf("修改后的默认策略: 模式=%d, 优先级=%d, 最大重试=%d\n", 
           default_policy.mode, default_policy.priority, default_policy.max_retry_count);
}

// 测试节点添加和移除
void test_node_management(NodeActivator* activator, NodeManager* node_manager) {
    printf("\n===== 测试节点添加和移除 =====\n");
    
    // 创建测试节点
    QNetworkNode* node1 = node_manager_create_node(node_manager, "测试节点1", NODE_TYPE_STANDARD);
    QNetworkNode* node2 = node_manager_create_node(node_manager, "测试节点2", NODE_TYPE_GATEWAY);
    QNetworkNode* node3 = node_manager_create_node(node_manager, "测试节点3", NODE_TYPE_BRIDGE);
    
    printf("已创建测试节点: node1(ID=%s), node2(ID=%s), node3(ID=%s)\n",
           node1->id, node2->id, node3->id);
    
    // 添加节点到激活器
    if (node_activator_add_node(activator, node1, NULL)) {
        printf("成功添加节点1(使用默认策略)\n");
    } else {
        printf("添加节点1失败\n");
    }
    
    // 为节点2创建自定义策略
    ActivationPolicy custom_policy = {0};
    custom_policy.mode = ACTIVATION_MODE_MANUAL;
    custom_policy.priority = ACTIVATION_PRIORITY_LOW;
    custom_policy.auto_recovery = 0;
    custom_policy.max_retry_count = 1;
    
    if (node_activator_add_node(activator, node2, &custom_policy)) {
        printf("成功添加节点2(使用自定义策略)\n");
    } else {
        printf("添加节点2失败\n");
    }
    
    if (node_activator_add_node(activator, node3, NULL)) {
        printf("成功添加节点3(使用默认策略)\n");
    } else {
        printf("添加节点3失败\n");
    }
    
    // 获取节点状态
    NodeActivationState state1 = node_activator_get_node_state(activator, node1);
    NodeActivationState state2 = node_activator_get_node_state(activator, node2);
    NodeActivationState state3 = node_activator_get_node_state(activator, node3);
    
    printf("节点1状态: %d\n", state1);
    printf("节点2状态: %d\n", state2);
    printf("节点3状态: %d\n", state3);
    
    // 尝试移除一个节点
    if (node_activator_remove_node(activator, node3)) {
        printf("成功移除节点3\n");
    } else {
        printf("移除节点3失败\n");
    }
    
    // 获取激活统计
    NodeActivationStats stats = node_activator_get_stats(activator);
    printf("激活统计: 总节点=%d, 活跃节点=%d, 非活跃节点=%d\n",
           stats.total_nodes, stats.active_nodes, stats.inactive_nodes);
}

// 测试节点激活和停用
void test_node_activation(NodeActivator* activator, NodeManager* node_manager) {
    printf("\n===== 测试节点激活和停用 =====\n");
    
    // 创建测试节点
    QNetworkNode* node4 = node_manager_create_node(node_manager, "测试节点4", NODE_TYPE_STANDARD);
    printf("已创建测试节点4(ID=%s)\n", node4->id);
    
    // 添加节点到激活器
    node_activator_add_node(activator, node4, NULL);
    
    // 检查初始状态
    NodeActivationState state = node_activator_get_node_state(activator, node4);
    printf("节点4初始状态: %d\n", state);
    
    // 手动激活节点
    printf("尝试激活节点4...\n");
    if (node_activator_activate_node(activator, node4)) {
        printf("成功激活节点4\n");
    } else {
        printf("激活节点4失败\n");
    }
    
    // 检查激活后状态
    state = node_activator_get_node_state(activator, node4);
    printf("节点4激活后状态: %d\n", state);
    
    // 尝试停用节点
    printf("尝试停用节点4...\n");
    if (node_activator_deactivate_node(activator, node4)) {
        printf("成功停用节点4\n");
    } else {
        printf("停用节点4失败\n");
    }
    
    // 检查停用后状态
    state = node_activator_get_node_state(activator, node4);
    printf("节点4停用后状态: %d\n", state);
    
    // 获取激活统计
    NodeActivationStats stats = node_activator_get_stats(activator);
    printf("激活统计: 总节点=%d, 激活尝试=%d, 激活成功=%d, 激活失败=%d\n",
           stats.total_nodes, stats.activation_attempts, 
           stats.activation_successes, stats.activation_failures);
}

// 测试自动激活
void test_auto_activation(NodeActivator* activator, NodeManager* node_manager) {
    printf("\n===== 测试自动激活 =====\n");
    
    // 启动自动激活
    printf("启动自动激活...\n");
    if (node_activator_start_auto_activation(activator)) {
        printf("成功启动自动激活\n");
    } else {
        printf("启动自动激活失败\n");
    }
    
    // 创建一些使用不同激活模式的节点
    QNetworkNode* auto_node = node_manager_create_node(node_manager, "自动激活节点", NODE_TYPE_STANDARD);
    QNetworkNode* manual_node = node_manager_create_node(node_manager, "手动激活节点", NODE_TYPE_STANDARD);
    
    ActivationPolicy auto_policy = {0};
    auto_policy.mode = ACTIVATION_MODE_AUTO_STARTUP;
    auto_policy.priority = ACTIVATION_PRIORITY_NORMAL;
    
    ActivationPolicy manual_policy = {0};
    manual_policy.mode = ACTIVATION_MODE_MANUAL;
    manual_policy.priority = ACTIVATION_PRIORITY_NORMAL;
    
    // 添加节点
    node_activator_add_node(activator, auto_node, &auto_policy);
    node_activator_add_node(activator, manual_node, &manual_policy);
    
    printf("添加了自动激活节点和手动激活节点\n");
    
    // 处理一个激活周期
    int processed = node_activator_process_cycle(activator);
    printf("处理了 %d 个节点的激活周期\n", processed);
    
    // 检查节点状态
    printf("自动激活节点状态: %d\n", node_activator_get_node_state(activator, auto_node));
    printf("手动激活节点状态: %d\n", node_activator_get_node_state(activator, manual_node));
    
    // 停止自动激活
    node_activator_stop_auto_activation(activator);
    printf("已停止自动激活\n");
}

// 测试强制激活所有节点
void test_activate_all(NodeActivator* activator) {
    printf("\n===== 测试强制激活所有节点 =====\n");
    
    // 获取初始激活统计
    NodeActivationStats stats_before = node_activator_get_stats(activator);
    printf("强制激活前: 总节点=%d, 活跃节点=%d, 非活跃节点=%d\n",
           stats_before.total_nodes, stats_before.active_nodes, stats_before.inactive_nodes);
    
    // 强制激活所有节点
    int activated = node_activator_activate_all_nodes(activator);
    printf("强制激活了 %d 个节点\n", activated);
    
    // 获取激活后统计
    NodeActivationStats stats_after = node_activator_get_stats(activator);
    printf("强制激活后: 总节点=%d, 活跃节点=%d, 非活跃节点=%d\n",
           stats_after.total_nodes, stats_after.active_nodes, stats_after.inactive_nodes);
}

// 主函数
int main(int argc, char* argv[]) {
    printf("=== QEntL量子网络节点自动激活系统测试 ===\n\n");
    
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
    NodeActivator* activator = node_activator_create(event_system);
    if (!activator) {
        fprintf(stderr, "无法创建节点激活器\n");
        node_manager_destroy(node_manager);
        event_system_destroy(event_system);
        return 1;
    }
    
    // 注册测试回调
    node_activator_register_callback(activator, test_activation_callback, NULL);
    
    // 运行测试
    test_default_policy(activator);
    test_node_management(activator, node_manager);
    test_node_activation(activator, node_manager);
    test_auto_activation(activator, node_manager);
    test_activate_all(activator);
    
    // 清理资源
    node_activator_destroy(activator);
    node_manager_destroy(node_manager);
    event_system_destroy(event_system);
    
    printf("\n=== 测试完成 ===\n");
    return 0;
} 