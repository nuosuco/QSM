/**
 * 节点恢复测试程序
 * 
 * 本程序演示如何使用resume_node函数恢复暂停状态的节点
 */

#include <stdio.h>
#include <stdlib.h>
#include "node_manager.h"

int main() {
    printf("节点恢复测试程序开始运行...\n\n");
    
    // 初始化节点管理器
    NodeManagerConfig config = get_default_node_manager_config();
    config.enable_logging = 1;
    config.log_file_path = "node_recovery_test.log";
    
    NodeManager* manager = initialize_node_manager(config, NULL);
    if (!manager) {
        printf("节点管理器初始化失败!\n");
        return 1;
    }
    
    printf("节点管理器初始化成功\n");
    
    // 创建测试节点
    unsigned int node_id = create_network_node(manager, NODE_TYPE_NORMAL, "测试节点", NODE_CAPABILITY_PROCESSING);
    if (node_id == 0) {
        printf("节点创建失败!\n");
        shutdown_node_manager(manager);
        return 1;
    }
    
    printf("创建测试节点，ID: %u\n", node_id);
    
    // 激活节点
    NodeManagerError result = update_node_state(manager, node_id, NODE_STATE_ACTIVE);
    if (result != NODE_MANAGER_ERROR_NONE) {
        printf("节点激活失败，错误码: %d\n", result);
        shutdown_node_manager(manager);
        return 1;
    }
    
    printf("节点已激活\n");
    
    // 暂停节点
    result = suspend_node(manager, node_id);
    if (result != NODE_MANAGER_ERROR_NONE) {
        printf("节点暂停失败，错误码: %d\n", result);
        shutdown_node_manager(manager);
        return 1;
    }
    
    printf("节点已暂停\n");
    
    // 获取并显示节点状态
    QuantumNetworkNode* node = get_node(manager, node_id);
    if (node) {
        printf("节点当前状态: %d (%s)\n", 
               node->state, 
               node->state == NODE_STATE_SUSPENDED ? "已暂停" : "未知状态");
    }
    
    // 恢复节点
    printf("\n准备恢复节点...\n");
    result = resume_node(manager, node_id);
    if (result != NODE_MANAGER_ERROR_NONE) {
        printf("节点恢复失败，错误码: %d\n", result);
    } else {
        printf("节点恢复成功!\n");
    }
    
    // 再次获取并显示节点状态
    node = get_node(manager, node_id);
    if (node) {
        printf("节点当前状态: %d (%s)\n", 
               node->state, 
               node->state == NODE_STATE_ACTIVE ? "已激活" : "未知状态");
    }
    
    // 尝试恢复已经处于活动状态的节点(应该成功，不做任何修改)
    printf("\n尝试恢复已经是活动状态的节点...\n");
    result = resume_node(manager, node_id);
    if (result != NODE_MANAGER_ERROR_NONE) {
        printf("操作失败，错误码: %d\n", result);
    } else {
        printf("操作成功(节点保持活动状态)\n");
    }
    
    // 清理资源
    shutdown_node_manager(manager);
    printf("\n测试完成，节点管理器已关闭\n");
    
    return 0;
} 