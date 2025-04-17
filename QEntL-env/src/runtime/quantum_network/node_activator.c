/**
 * QEntL量子网络节点自动激活系统实现
 * 
 * 量子基因编码: QG-RUNTIME-NODEACT-SRC-F8H3-1713051200
 * 
 * @文件: node_activator.c
 * @描述: 实现QEntL运行时的量子网络节点自动激活系统功能
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-18
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 节点激活系统支持节点动态自启动和自恢复
 * - 支持跨设备节点发现和激活协同
 */

#include "node_activator.h"
#include "node_manager.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/**
 * 节点管理条目结构
 */
typedef struct NodeEntry {
    QNetworkNode* node;              /* 网络节点 */
    NodeActivationState state;       /* 激活状态 */
    ActivationPolicy policy;         /* 激活策略 */
    time_t last_activation_attempt;  /* 上次激活尝试时间 */
    time_t activation_time;          /* 激活时间 */
    int retry_count;                 /* 重试计数 */
    double activation_duration;      /* 激活持续时间 */
    int is_custom_policy;            /* 是否使用自定义策略 */
} NodeEntry;

/**
 * 回调条目结构
 */
typedef struct CallbackEntry {
    NodeActivationCallback callback; /* 回调函数 */
    void* user_data;                 /* 用户数据 */
} CallbackEntry;

/**
 * 节点激活器内部结构
 */
struct NodeActivator {
    NodeEntry** nodes;               /* 节点条目数组 */
    int node_count;                  /* 节点数量 */
    int node_capacity;               /* 节点容量 */
    
    CallbackEntry* callbacks;        /* 回调条目数组 */
    int callback_count;              /* 回调数量 */
    int callback_capacity;           /* 回调容量 */
    
    ActivationPolicy default_policy; /* 默认激活策略 */
    EventSystem* event_system;       /* 事件系统 */
    EventHandler* event_handler;     /* 事件处理器 */
    
    int is_auto_activating;          /* 是否自动激活 */
    time_t last_process_time;        /* 上次处理时间 */
    
    NodeActivationStats stats;       /* 激活统计 */
};

/* 内部函数声明 */
static NodeEntry* find_node_entry(NodeActivator* activator, QNetworkNode* node);
static int execute_node_callbacks(NodeActivator* activator, QNetworkNode* node, NodeActivationState state);
static int activate_node_internal(NodeActivator* activator, NodeEntry* entry);
static int deactivate_node_internal(NodeActivator* activator, NodeEntry* entry);
static int update_node_state(NodeActivator* activator, NodeEntry* entry, NodeActivationState new_state);
static void update_activation_stats(NodeActivator* activator);
static void on_node_event(QEntLEvent* event, NodeActivator* activator);

/**
 * 创建节点激活器
 */
NodeActivator* node_activator_create(EventSystem* event_system) {
    if (!event_system) {
        fprintf(stderr, "错误: 创建节点激活器需要有效的事件系统\n");
        return NULL;
    }
    
    NodeActivator* activator = (NodeActivator*)malloc(sizeof(NodeActivator));
    if (!activator) {
        fprintf(stderr, "错误: 无法分配节点激活器内存\n");
        return NULL;
    }
    
    /* 初始化节点数组 */
    activator->node_capacity = 16;
    activator->nodes = (NodeEntry**)malloc(activator->node_capacity * sizeof(NodeEntry*));
    if (!activator->nodes) {
        free(activator);
        fprintf(stderr, "错误: 无法分配节点数组内存\n");
        return NULL;
    }
    activator->node_count = 0;
    
    /* 初始化回调数组 */
    activator->callback_capacity = 8;
    activator->callbacks = (CallbackEntry*)malloc(activator->callback_capacity * sizeof(CallbackEntry));
    if (!activator->callbacks) {
        free(activator->nodes);
        free(activator);
        fprintf(stderr, "错误: 无法分配回调数组内存\n");
        return NULL;
    }
    activator->callback_count = 0;
    
    /* 设置默认激活策略 */
    activator->default_policy.mode = ACTIVATION_MODE_AUTO_STARTUP;
    activator->default_policy.priority = ACTIVATION_PRIORITY_NORMAL;
    activator->default_policy.auto_recovery = 1;
    activator->default_policy.activation_threshold = 0;
    activator->default_policy.max_retry_count = 3;
    activator->default_policy.retry_interval = 5.0;
    activator->default_policy.schedule_info = NULL;
    
    /* 初始化事件系统 */
    activator->event_system = event_system;
    activator->event_handler = event_system_add_handler(event_system, 
                                                      node_activator_event_handler, 
                                                      activator, 
                                                      10, /* 优先级 */
                                                      (1 << EVENT_SYSTEM_STARTUP) | 
                                                      (1 << EVENT_NETWORK_CONNECTION) |
                                                      (1 << EVENT_NETWORK_DISCONNECTION));
    
    /* 初始化其他属性 */
    activator->is_auto_activating = 0;
    activator->last_process_time = time(NULL);
    
    /* 初始化统计信息 */
    memset(&activator->stats, 0, sizeof(NodeActivationStats));
    
    printf("量子网络节点自动激活系统已创建\n");
    
    return activator;
}

/**
 * 销毁节点激活器
 */
void node_activator_destroy(NodeActivator* activator) {
    if (!activator) return;
    
    /* 停止自动激活 */
    if (activator->is_auto_activating) {
        node_activator_stop_auto_activation(activator);
    }
    
    /* 移除事件处理器 */
    if (activator->event_system && activator->event_handler) {
        event_system_remove_handler(activator->event_system, activator->event_handler);
    }
    
    /* 释放节点条目 */
    for (int i = 0; i < activator->node_count; i++) {
        free(activator->nodes[i]);
    }
    free(activator->nodes);
    
    /* 释放回调数组 */
    free(activator->callbacks);
    
    /* 释放激活器本身 */
    free(activator);
    
    printf("量子网络节点自动激活系统已销毁\n");
}

/**
 * 设置默认激活策略
 */
int node_activator_set_default_policy(NodeActivator* activator, ActivationPolicy policy) {
    if (!activator) return 0;
    
    activator->default_policy = policy;
    return 1;
}

/**
 * 获取默认激活策略
 */
ActivationPolicy node_activator_get_default_policy(NodeActivator* activator) {
    static ActivationPolicy empty_policy = {0};
    
    if (!activator) return empty_policy;
    
    return activator->default_policy;
}

/**
 * 添加网络节点
 */
int node_activator_add_node(NodeActivator* activator, QNetworkNode* node, ActivationPolicy* policy) {
    if (!activator || !node) return 0;
    
    /* 检查节点是否已存在 */
    if (find_node_entry(activator, node)) {
        return 0;  /* 节点已存在 */
    }
    
    /* 检查是否需要扩展节点数组 */
    if (activator->node_count >= activator->node_capacity) {
        int new_capacity = activator->node_capacity * 2;
        NodeEntry** new_nodes = (NodeEntry**)realloc(activator->nodes, 
                                                   new_capacity * sizeof(NodeEntry*));
        if (!new_nodes) {
            fprintf(stderr, "错误: 无法扩展节点数组\n");
            return 0;
        }
        
        activator->nodes = new_nodes;
        activator->node_capacity = new_capacity;
    }
    
    /* 创建新节点条目 */
    NodeEntry* entry = (NodeEntry*)malloc(sizeof(NodeEntry));
    if (!entry) {
        fprintf(stderr, "错误: 无法分配节点条目内存\n");
        return 0;
    }
    
    /* 初始化条目 */
    entry->node = node;
    entry->state = NODE_STATE_INACTIVE;
    entry->last_activation_attempt = 0;
    entry->activation_time = 0;
    entry->retry_count = 0;
    entry->activation_duration = 0.0;
    
    /* 设置策略 */
    if (policy) {
        entry->policy = *policy;
        entry->is_custom_policy = 1;
    } else {
        entry->policy = activator->default_policy;
        entry->is_custom_policy = 0;
    }
    
    /* 添加到数组 */
    activator->nodes[activator->node_count++] = entry;
    
    /* 更新统计信息 */
    activator->stats.total_nodes++;
    activator->stats.inactive_nodes++;
    
    /* 如果策略是自动启动激活，立即激活节点 */
    if (entry->policy.mode == ACTIVATION_MODE_AUTO_STARTUP || entry->policy.mode == ACTIVATION_MODE_AUTO_DISCOVERY) {
        activate_node_internal(activator, entry);
    }
    
    return 1;
}

/**
 * 移除网络节点
 */
int node_activator_remove_node(NodeActivator* activator, QNetworkNode* node) {
    if (!activator || !node) return 0;
    
    int index = -1;
    NodeEntry* entry = NULL;
    
    /* 查找节点索引 */
    for (int i = 0; i < activator->node_count; i++) {
        if (activator->nodes[i]->node == node) {
            index = i;
            entry = activator->nodes[i];
            break;
        }
    }
    
    if (index == -1) return 0;  /* 节点未找到 */
    
    /* 如果节点处于激活状态，先停用它 */
    if (entry->state == NODE_STATE_ACTIVE || entry->state == NODE_STATE_ACTIVATING) {
        deactivate_node_internal(activator, entry);
    }
    
    /* 更新统计 */
    activator->stats.total_nodes--;
    if (entry->state == NODE_STATE_ACTIVE) {
        activator->stats.active_nodes--;
    } else if (entry->state == NODE_STATE_INACTIVE) {
        activator->stats.inactive_nodes--;
    }
    
    /* 释放节点条目 */
    free(entry);
    
    /* 移除节点并重新整理数组 */
    for (int i = index; i < activator->node_count - 1; i++) {
        activator->nodes[i] = activator->nodes[i + 1];
    }
    activator->node_count--;
    
    return 1;
}

/**
 * 激活网络节点
 */
int node_activator_activate_node(NodeActivator* activator, QNetworkNode* node) {
    if (!activator || !node) return 0;
    
    NodeEntry* entry = find_node_entry(activator, node);
    if (!entry) return 0;  /* 节点未找到 */
    
    return activate_node_internal(activator, entry);
}

/**
 * 停用网络节点
 */
int node_activator_deactivate_node(NodeActivator* activator, QNetworkNode* node) {
    if (!activator || !node) return 0;
    
    NodeEntry* entry = find_node_entry(activator, node);
    if (!entry) return 0;  /* 节点未找到 */
    
    return deactivate_node_internal(activator, entry);
}

/**
 * 获取节点激活状态
 */
NodeActivationState node_activator_get_node_state(NodeActivator* activator, QNetworkNode* node) {
    if (!activator || !node) return NODE_STATE_INACTIVE;
    
    NodeEntry* entry = find_node_entry(activator, node);
    if (!entry) return NODE_STATE_INACTIVE;  /* 节点未找到 */
    
    return entry->state;
}

/**
 * 注册激活回调
 */
int node_activator_register_callback(NodeActivator* activator, NodeActivationCallback callback, void* user_data) {
    if (!activator || !callback) return 0;
    
    /* 检查是否需要扩展回调数组 */
    if (activator->callback_count >= activator->callback_capacity) {
        int new_capacity = activator->callback_capacity * 2;
        CallbackEntry* new_callbacks = (CallbackEntry*)realloc(activator->callbacks, 
                                                             new_capacity * sizeof(CallbackEntry));
        if (!new_callbacks) {
            fprintf(stderr, "错误: 无法扩展回调数组\n");
            return 0;
        }
        
        activator->callbacks = new_callbacks;
        activator->callback_capacity = new_capacity;
    }
    
    /* 添加回调 */
    activator->callbacks[activator->callback_count].callback = callback;
    activator->callbacks[activator->callback_count].user_data = user_data;
    activator->callback_count++;
    
    return 1;
}

/**
 * 获取激活统计
 */
NodeActivationStats node_activator_get_stats(NodeActivator* activator) {
    NodeActivationStats empty_stats = {0};
    
    if (!activator) return empty_stats;
    
    /* 更新统计信息 */
    update_activation_stats(activator);
    
    return activator->stats;
}

/**
 * 启动自动激活
 */
int node_activator_start_auto_activation(NodeActivator* activator) {
    if (!activator) return 0;
    
    if (activator->is_auto_activating) return 1;  /* 已经在运行 */
    
    activator->is_auto_activating = 1;
    activator->last_process_time = time(NULL);
    
    /* 激活处于AUTO模式的所有节点 */
    for (int i = 0; i < activator->node_count; i++) {
        NodeEntry* entry = activator->nodes[i];
        if (entry->state == NODE_STATE_INACTIVE && 
            (entry->policy.mode == ACTIVATION_MODE_AUTO_STARTUP || 
             entry->policy.mode == ACTIVATION_MODE_AUTO_DISCOVERY)) {
            activate_node_internal(activator, entry);
        }
    }
    
    printf("量子网络节点自动激活系统已启动\n");
    
    return 1;
}

/**
 * 停止自动激活
 */
int node_activator_stop_auto_activation(NodeActivator* activator) {
    if (!activator) return 0;
    
    if (!activator->is_auto_activating) return 1;  /* 已经停止 */
    
    activator->is_auto_activating = 0;
    
    printf("量子网络节点自动激活系统已停止\n");
    
    return 1;
}

/**
 * 处理一个激活周期
 */
int node_activator_process_cycle(NodeActivator* activator) {
    if (!activator) return 0;
    
    time_t current_time = time(NULL);
    int processed_nodes = 0;
    
    /* 处理所有节点 */
    for (int i = 0; i < activator->node_count; i++) {
        NodeEntry* entry = activator->nodes[i];
        
        /* 处理重试逻辑 */
        if (entry->state == NODE_STATE_ERROR && entry->policy.auto_recovery) {
            if (entry->retry_count < entry->policy.max_retry_count && 
                difftime(current_time, entry->last_activation_attempt) >= entry->policy.retry_interval) {
                /* 尝试恢复节点 */
                update_node_state(activator, entry, NODE_STATE_RECOVERING);
                activate_node_internal(activator, entry);
                processed_nodes++;
            }
        }
        
        /* 处理定时激活模式 */
        if (entry->state == NODE_STATE_INACTIVE && entry->policy.mode == ACTIVATION_MODE_SCHEDULED) {
            /* TODO: 实现定时激活逻辑 */
            /* 这里需要检查entry->policy.schedule_info来决定是否应该激活节点 */
        }
    }
    
    /* 更新统计信息 */
    update_activation_stats(activator);
    
    return processed_nodes;
}

/**
 * 强制激活所有节点
 */
int node_activator_activate_all_nodes(NodeActivator* activator) {
    if (!activator) return 0;
    
    int success_count = 0;
    
    for (int i = 0; i < activator->node_count; i++) {
        NodeEntry* entry = activator->nodes[i];
        
        /* 只处理非活跃状态的节点 */
        if (entry->state != NODE_STATE_ACTIVE && entry->state != NODE_STATE_ACTIVATING) {
            if (activate_node_internal(activator, entry)) {
                success_count++;
            }
        }
    }
    
    return success_count;
}

/**
 * 节点激活器处理事件
 */
void node_activator_event_handler(QEntLEvent* event, void* user_data) {
    NodeActivator* activator = (NodeActivator*)user_data;
    if (!activator || !event) return;
    
    /* 处理事件 */
    on_node_event(event, activator);
}

/**
 * 尝试恢复失败的节点
 */
int node_activator_recover_failed_nodes(NodeActivator* activator) {
    if (!activator) return 0;
    
    int recovery_count = 0;
    
    for (int i = 0; i < activator->node_count; i++) {
        NodeEntry* entry = activator->nodes[i];
        
        if (entry->state == NODE_STATE_ERROR) {
            /* 重置重试计数 */
            entry->retry_count = 0;
            
            /* 尝试恢复 */
            update_node_state(activator, entry, NODE_STATE_RECOVERING);
            if (activate_node_internal(activator, entry)) {
                recovery_count++;
            }
        }
    }
    
    /* 更新统计 */
    activator->stats.recovery_attempts += recovery_count;
    
    return recovery_count;
}

/**
 * 内部函数：查找节点条目
 */
static NodeEntry* find_node_entry(NodeActivator* activator, QNetworkNode* node) {
    if (!activator || !node) return NULL;
    
    for (int i = 0; i < activator->node_count; i++) {
        if (activator->nodes[i]->node == node) {
            return activator->nodes[i];
        }
    }
    
    return NULL;
}

/**
 * 内部函数：执行节点回调
 */
static int execute_node_callbacks(NodeActivator* activator, QNetworkNode* node, NodeActivationState state) {
    if (!activator || !node) return 0;
    
    int success_count = 0;
    
    for (int i = 0; i < activator->callback_count; i++) {
        if (activator->callbacks[i].callback(node, state, activator->callbacks[i].user_data)) {
            success_count++;
        }
    }
    
    return success_count;
}

/**
 * 内部函数：激活节点
 */
static int activate_node_internal(NodeActivator* activator, NodeEntry* entry) {
    if (!activator || !entry) return 0;
    
    /* 只有非活跃的节点可以被激活 */
    if (entry->state != NODE_STATE_INACTIVE && entry->state != NODE_STATE_ERROR && 
        entry->state != NODE_STATE_RECOVERING) {
        return 0;
    }
    
    /* 更新状态 */
    update_node_state(activator, entry, NODE_STATE_ACTIVATING);
    
    /* 记录尝试激活的时间 */
    entry->last_activation_attempt = time(NULL);
    entry->retry_count++;
    
    /* 更新统计 */
    activator->stats.activation_attempts++;
    
    /* 执行实际激活操作 */
    int success = 0;
    /* 这里调用真实的节点激活逻辑，例如：
     * success = node_manager_activate_node(entry->node); 
     */
    
    /* 模拟激活成功的逻辑 */
    success = 1;  /* 在实际实现中应该使用实际的成功/失败结果 */
    
    if (success) {
        /* 激活成功 */
        entry->activation_time = time(NULL);
        update_node_state(activator, entry, NODE_STATE_ACTIVE);
        entry->retry_count = 0;  /* 重置重试计数 */
        
        /* 更新统计 */
        activator->stats.activation_successes++;
        activator->stats.active_nodes++;
        activator->stats.inactive_nodes--;
        activator->stats.last_activation_time = entry->activation_time;
        
        if (entry->state == NODE_STATE_RECOVERING) {
            activator->stats.recovery_successes++;
        }
        
        /* 计算激活时间 */
        entry->activation_duration = difftime(entry->activation_time, entry->last_activation_attempt);
        
        /* 执行回调 */
        execute_node_callbacks(activator, entry->node, NODE_STATE_ACTIVE);
        
        return 1;
    } else {
        /* 激活失败 */
        update_node_state(activator, entry, NODE_STATE_ERROR);
        
        /* 执行回调 */
        execute_node_callbacks(activator, entry->node, NODE_STATE_ERROR);
        
        /* 更新统计 */
        activator->stats.activation_failures++;
        
        return 0;
    }
}

/**
 * 内部函数：停用节点
 */
static int deactivate_node_internal(NodeActivator* activator, NodeEntry* entry) {
    if (!activator || !entry) return 0;
    
    /* 只有活跃状态的节点可以被停用 */
    if (entry->state != NODE_STATE_ACTIVE && entry->state != NODE_STATE_ACTIVATING) {
        return 0;
    }
    
    /* 更新状态 */
    update_node_state(activator, entry, NODE_STATE_DEACTIVATING);
    
    /* 执行实际停用操作 */
    int success = 0;
    /* 这里调用真实的节点停用逻辑，例如：
     * success = node_manager_deactivate_node(entry->node); 
     */
    
    /* 模拟停用成功的逻辑 */
    success = 1;  /* 在实际实现中应该使用实际的成功/失败结果 */
    
    if (success) {
        /* 停用成功 */
        update_node_state(activator, entry, NODE_STATE_INACTIVE);
        
        /* 更新统计 */
        activator->stats.active_nodes--;
        activator->stats.inactive_nodes++;
        
        /* 执行回调 */
        execute_node_callbacks(activator, entry->node, NODE_STATE_INACTIVE);
        
        return 1;
    } else {
        /* 停用失败，恢复到活跃状态 */
        update_node_state(activator, entry, NODE_STATE_ACTIVE);
        
        return 0;
    }
}

/**
 * 内部函数：更新节点状态
 */
static int update_node_state(NodeActivator* activator, NodeEntry* entry, NodeActivationState new_state) {
    if (!activator || !entry) return 0;
    
    /* 保存旧状态 */
    NodeActivationState old_state = entry->state;
    
    /* 更新状态 */
    entry->state = new_state;
    
    /* 发出状态变化事件 */
    if (old_state != new_state && activator->event_system) {
        /* 创建事件数据 */
        /* TODO: 构建实际的事件数据并发送事件 */
    }
    
    return 1;
}

/**
 * 内部函数：更新激活统计
 */
static void update_activation_stats(NodeActivator* activator) {
    if (!activator) return;
    
    /* 重新计算活跃/非活跃节点数 */
    activator->stats.active_nodes = 0;
    activator->stats.inactive_nodes = 0;
    
    double total_duration = 0.0;
    int duration_count = 0;
    
    for (int i = 0; i < activator->node_count; i++) {
        NodeEntry* entry = activator->nodes[i];
        
        if (entry->state == NODE_STATE_ACTIVE) {
            activator->stats.active_nodes++;
        } else if (entry->state == NODE_STATE_INACTIVE) {
            activator->stats.inactive_nodes++;
        }
        
        /* 计算平均激活时间 */
        if (entry->activation_duration > 0) {
            total_duration += entry->activation_duration;
            duration_count++;
        }
    }
    
    if (duration_count > 0) {
        activator->stats.average_activation_time = total_duration / duration_count;
    }
}

/**
 * 内部函数：处理节点事件
 */
static void on_node_event(QEntLEvent* event, NodeActivator* activator) {
    if (!event || !activator) return;
    
    /* 处理系统启动事件 */
    if (event->type == EVENT_SYSTEM_STARTUP) {
        if (!activator->is_auto_activating) {
            node_activator_start_auto_activation(activator);
        }
        return;
    }
    
    /* 处理网络连接事件 */
    if (event->type == EVENT_NETWORK_CONNECTION) {
        /* TODO: 检查事件数据，找到对应的节点并激活 */
        return;
    }
    
    /* 处理网络断开事件 */
    if (event->type == EVENT_NETWORK_DISCONNECTION) {
        /* TODO: 检查事件数据，找到对应的节点并停用 */
        return;
    }
} 