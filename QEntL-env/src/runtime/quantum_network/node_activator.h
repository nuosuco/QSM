/**
 * QEntL量子网络节点自动激活系统头文件
 * 
 * 量子基因编码: QG-RUNTIME-NODEACT-HDR-F8G2-1713051200
 * 
 * @文件: node_activator.h
 * @描述: 定义QEntL运行时的量子网络节点自动激活系统API
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-18
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 节点激活系统支持节点动态自启动和自恢复
 * - 支持跨设备节点发现和激活协同
 */

#ifndef QENTL_NODE_ACTIVATOR_H
#define QENTL_NODE_ACTIVATOR_H

#include "../../quantum_network.h"
#include "../event_system.h"

/**
 * 前向声明
 */
typedef struct NodeActivator NodeActivator;
typedef struct ActivationPolicy ActivationPolicy;
typedef struct NodeActivationStats NodeActivationStats;

/**
 * 节点激活状态枚举
 */
typedef enum {
    NODE_STATE_INACTIVE,      /* 节点未激活 */
    NODE_STATE_ACTIVATING,    /* 节点正在激活 */
    NODE_STATE_ACTIVE,        /* 节点已激活 */
    NODE_STATE_DEACTIVATING,  /* 节点正在停用 */
    NODE_STATE_ERROR,         /* 节点激活错误 */
    NODE_STATE_RECOVERING     /* 节点正在恢复 */
} NodeActivationState;

/**
 * 激活模式枚举
 */
typedef enum {
    ACTIVATION_MODE_MANUAL,          /* 手动激活 */
    ACTIVATION_MODE_AUTO_STARTUP,    /* 启动时自动激活 */
    ACTIVATION_MODE_AUTO_DISCOVERY,  /* 发现时自动激活 */
    ACTIVATION_MODE_SCHEDULED,       /* 定时激活 */
    ACTIVATION_MODE_EVENT_DRIVEN,    /* 事件驱动激活 */
    ACTIVATION_MODE_NETWORK_SYNC     /* 网络同步激活 */
} ActivationMode;

/**
 * 激活优先级枚举
 */
typedef enum {
    ACTIVATION_PRIORITY_LOW,      /* 低优先级 */
    ACTIVATION_PRIORITY_NORMAL,   /* 普通优先级 */
    ACTIVATION_PRIORITY_HIGH,     /* 高优先级 */
    ACTIVATION_PRIORITY_CRITICAL  /* 关键优先级 */
} ActivationPriority;

/**
 * 激活策略结构
 */
typedef struct ActivationPolicy {
    ActivationMode mode;               /* 激活模式 */
    ActivationPriority priority;       /* 激活优先级 */
    int auto_recovery;                 /* 自动恢复标志 */
    int activation_threshold;          /* 激活阈值 */
    int max_retry_count;               /* 最大重试次数 */
    double retry_interval;             /* 重试间隔(秒) */
    void* schedule_info;               /* 定时信息(仅用于定时激活) */
} ActivationPolicy;

/**
 * 节点激活统计数据
 */
typedef struct NodeActivationStats {
    int total_nodes;                   /* 总节点数 */
    int active_nodes;                  /* 活跃节点数 */
    int inactive_nodes;                /* 非活跃节点数 */
    int activation_attempts;           /* 激活尝试次数 */
    int activation_successes;          /* 激活成功次数 */
    int activation_failures;           /* 激活失败次数 */
    int recovery_attempts;             /* 恢复尝试次数 */
    int recovery_successes;            /* 恢复成功次数 */
    double average_activation_time;    /* 平均激活时间 */
    time_t last_activation_time;       /* 最后激活时间 */
} NodeActivationStats;

/**
 * 节点激活回调函数
 * @param node 节点
 * @param state 激活状态
 * @param user_data 用户数据
 * @return 成功返回1，失败返回0
 */
typedef int (*NodeActivationCallback)(QNetworkNode* node, NodeActivationState state, void* user_data);

/**
 * 创建节点激活器
 * 
 * @param event_system 事件系统
 * @return 新创建的节点激活器
 */
NodeActivator* node_activator_create(EventSystem* event_system);

/**
 * 销毁节点激活器
 * 
 * @param activator 要销毁的节点激活器
 */
void node_activator_destroy(NodeActivator* activator);

/**
 * 设置默认激活策略
 * 
 * @param activator 节点激活器
 * @param policy 激活策略
 * @return 成功返回1，失败返回0
 */
int node_activator_set_default_policy(NodeActivator* activator, ActivationPolicy policy);

/**
 * 获取默认激活策略
 * 
 * @param activator 节点激活器
 * @return 默认激活策略
 */
ActivationPolicy node_activator_get_default_policy(NodeActivator* activator);

/**
 * 添加网络节点
 * 
 * @param activator 节点激活器
 * @param node 要添加的节点
 * @param policy 节点特定的激活策略，NULL表示使用默认策略
 * @return 成功返回1，失败返回0
 */
int node_activator_add_node(NodeActivator* activator, QNetworkNode* node, ActivationPolicy* policy);

/**
 * 移除网络节点
 * 
 * @param activator 节点激活器
 * @param node 要移除的节点
 * @return 成功返回1，失败返回0
 */
int node_activator_remove_node(NodeActivator* activator, QNetworkNode* node);

/**
 * 激活网络节点
 * 
 * @param activator 节点激活器
 * @param node 要激活的节点
 * @return 成功返回1，失败返回0
 */
int node_activator_activate_node(NodeActivator* activator, QNetworkNode* node);

/**
 * 停用网络节点
 * 
 * @param activator 节点激活器
 * @param node 要停用的节点
 * @return 成功返回1，失败返回0
 */
int node_activator_deactivate_node(NodeActivator* activator, QNetworkNode* node);

/**
 * 获取节点激活状态
 * 
 * @param activator 节点激活器
 * @param node 节点
 * @return 激活状态
 */
NodeActivationState node_activator_get_node_state(NodeActivator* activator, QNetworkNode* node);

/**
 * 注册激活回调
 * 
 * @param activator 节点激活器
 * @param callback 回调函数
 * @param user_data 用户数据
 * @return 成功返回1，失败返回0
 */
int node_activator_register_callback(NodeActivator* activator, NodeActivationCallback callback, void* user_data);

/**
 * 获取激活统计
 * 
 * @param activator 节点激活器
 * @return 激活统计数据
 */
NodeActivationStats node_activator_get_stats(NodeActivator* activator);

/**
 * 启动自动激活
 * 
 * @param activator 节点激活器
 * @return 成功返回1，失败返回0
 */
int node_activator_start_auto_activation(NodeActivator* activator);

/**
 * 停止自动激活
 * 
 * @param activator 节点激活器
 * @return 成功返回1，失败返回0
 */
int node_activator_stop_auto_activation(NodeActivator* activator);

/**
 * 处理一个激活周期
 * 
 * @param activator 节点激活器
 * @return 处理的节点数量
 */
int node_activator_process_cycle(NodeActivator* activator);

/**
 * 强制激活所有节点
 * 
 * @param activator 节点激活器
 * @return 成功激活的节点数量
 */
int node_activator_activate_all_nodes(NodeActivator* activator);

/**
 * 节点激活器处理事件
 * 
 * @param event 事件
 * @param user_data 用户数据(节点激活器)
 */
void node_activator_event_handler(QEntLEvent* event, void* user_data);

/**
 * 尝试恢复失败的节点
 * 
 * @param activator 节点激活器
 * @return 成功恢复的节点数量
 */
int node_activator_recover_failed_nodes(NodeActivator* activator);

#endif /* QENTL_NODE_ACTIVATOR_H */ 