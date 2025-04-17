/**
 * QEntL标准库网络函数头文件
 * 
 * 量子基因编码: QG-STDLIB-NET-HEADER-A1B5
 * 
 * @文件: quantum_network_lib.h
 * @描述: 定义QEntL标准库中的网络功能接口，包括量子节点管理和纠缠通信
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-15
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 网络节点和通信信道自动包含量子基因编码和量子纠缠信道
 * - 能根据运行环境自适应调整量子比特处理能力
 */

#ifndef QENTL_QUANTUM_NETWORK_LIB_H
#define QENTL_QUANTUM_NETWORK_LIB_H

#include <stdlib.h>
#include "../../quantum_state.h"

/**
 * 量子网络节点不透明结构
 */
typedef struct QNetworkNode QNetworkNode;

/**
 * 量子通信信道不透明结构
 */
typedef struct QNetworkChannel QNetworkChannel;

/**
 * 初始化标准库网络组件
 * 
 * @return 成功返回1，失败返回0
 */
int qentl_stdlib_network_initialize(void);

/**
 * 清理标准库网络组件
 */
void qentl_stdlib_network_cleanup(void);

/**
 * 创建量子网络节点
 * 
 * 创建一个新的量子网络节点，节点默认处于激活状态，
 * 自动包含量子基因编码和量子纠缠信道，可立即参与
 * 全局量子纠缠网络的构建。
 * 
 * @param name 节点名称
 * @param type 节点类型 (可选，NULL为"default")
 * @return 节点指针，失败返回NULL
 */
QNetworkNode* qentl_create_network_node(const char* name, const char* type);

/**
 * 销毁量子网络节点
 * 
 * @param node 网络节点指针
 */
void qentl_destroy_network_node(QNetworkNode* node);

/**
 * 设置节点活跃状态
 * 
 * 节点默认处于激活状态(active=1)，能自动参与量子纠缠网络构建。
 * 
 * @param node 网络节点指针
 * @param active 活跃状态 (1为活跃，0为非活跃)
 */
void qentl_set_node_active(QNetworkNode* node, int active);

/**
 * 检查节点是否活跃
 * 
 * @param node 网络节点指针
 * @return 活跃返回1，非活跃返回0
 */
int qentl_is_node_active(QNetworkNode* node);

/**
 * 设置节点用户数据和清理回调
 * 
 * @param node 网络节点指针
 * @param user_data 用户数据指针
 * @param cleanup_callback 用户数据清理回调函数
 */
void qentl_set_node_user_data(QNetworkNode* node, void* user_data, 
                            void (*cleanup_callback)(void*));

/**
 * 获取节点用户数据
 * 
 * @param node 网络节点指针
 * @return 用户数据指针，失败返回NULL
 */
void* qentl_get_node_user_data(QNetworkNode* node);

/**
 * 获取节点ID
 * 
 * @param node 网络节点指针
 * @return 节点ID字符串，失败返回NULL
 */
const char* qentl_get_node_id(QNetworkNode* node);

/**
 * 获取节点名称
 * 
 * @param node 网络节点指针
 * @return 节点名称字符串，失败返回NULL
 */
const char* qentl_get_node_name(QNetworkNode* node);

/**
 * 获取节点量子态
 * 
 * @param node 网络节点指针
 * @return 节点量子态指针，失败返回NULL
 */
QState* qentl_get_node_state(QNetworkNode* node);

/**
 * 连接两个节点
 * 
 * 创建两个节点间的量子纠缠通信信道。通信信道默认处于激活状态，
 * 自动包含量子基因编码和量子纠缠信道。
 * 
 * @param source 源节点
 * @param target 目标节点
 * @param strength 纠缠强度 (0.0-1.0，默认为0.75)
 * @return 通信信道指针，失败返回NULL
 */
QNetworkChannel* qentl_connect_nodes(QNetworkNode* source, QNetworkNode* target, 
                                  double strength);

/**
 * 销毁量子通信信道
 * 
 * @param channel 通信信道指针
 */
void qentl_destroy_channel(QNetworkChannel* channel);

/**
 * 发送状态通过信道
 * 
 * 通过量子纠缠信道传输量子状态。传输的状态自动包含量子基因编码
 * 和量子纠缠信道，保持与源状态的纠缠关系。
 * 
 * @param channel 通信信道
 * @param state 量子状态
 * @return 传输后的状态副本，失败返回NULL
 */
QState* qentl_transmit_through_channel(QNetworkChannel* channel, QState* state);

/**
 * 广播状态到所有连接的节点
 * 
 * 将量子态广播到所有与源节点连接的节点。
 * 
 * @param source 源节点
 * @param state 量子状态
 * @return 成功发送的节点数量
 */
int qentl_broadcast_state(QNetworkNode* source, QState* state);

/**
 * 查找节点
 * 
 * 通过节点ID查找全局节点
 * 
 * @param node_id 节点ID
 * @return 节点指针，未找到返回NULL
 */
QNetworkNode* qentl_find_node_by_id(const char* node_id);

/**
 * 通过名称查找节点
 * 
 * @param node_name 节点名称
 * @return 节点指针，未找到返回NULL
 */
QNetworkNode* qentl_find_node_by_name(const char* node_name);

/**
 * 获取所有节点
 * 
 * 返回全局节点列表的副本
 * 
 * @param count 输出节点数量
 * @return 节点指针数组，失败返回NULL，使用完毕需调用free释放
 */
QNetworkNode** qentl_get_all_nodes(size_t* count);

/**
 * 获取连接到节点的所有信道
 * 
 * @param node 节点指针
 * @param count 输出信道数量
 * @return 信道指针数组，失败返回NULL，使用完毕需调用qentl_free_channels释放
 */
QNetworkChannel** qentl_get_node_channels(QNetworkNode* node, size_t* count);

/**
 * 释放信道数组
 * 
 * @param channels 信道指针数组
 * @param count 信道数量
 */
void qentl_free_channels(QNetworkChannel** channels, size_t count);

/**
 * 创建量子网络集群
 * 
 * 创建一个具有中心节点和多个子节点的网络集群，
 * 所有节点默认处于激活状态，自动参与量子纠缠网络构建。
 * 
 * @param name 集群名称
 * @param node_count 子节点数量
 * @return 中心节点指针，失败返回NULL
 */
QNetworkNode* qentl_create_network_cluster(const char* name, int node_count);

/**
 * 发现网络中的节点
 * 
 * 扫描网络并发现活跃的量子节点
 * 
 * @param max_nodes 最大返回节点数量
 * @param timeout_ms 超时时间(毫秒)
 * @param count 输出发现的节点数量
 * @return 节点指针数组，失败返回NULL，使用完毕需调用free释放
 */
QNetworkNode** qentl_discover_nodes(int max_nodes, int timeout_ms, size_t* count);

/**
 * 创建量子路由表
 * 
 * 为网络中的节点创建路由表，以优化量子通信路径
 * 
 * @param nodes 节点数组
 * @param node_count 节点数量
 * @return 路由表指针，失败返回NULL
 */
void* qentl_create_routing_table(QNetworkNode** nodes, size_t node_count);

/**
 * 优化网络拓扑
 * 
 * 分析网络结构并优化纠缠连接，提高整体网络效率
 * 
 * @param nodes 节点数组
 * @param node_count 节点数量
 * @return 成功返回优化的连接数量，失败返回负值
 */
int qentl_optimize_network_topology(QNetworkNode** nodes, size_t node_count);

/**
 * 检测节点健康状态
 * 
 * @param node 节点指针
 * @return 健康值(0-100)，0表示不可用
 */
int qentl_check_node_health(QNetworkNode* node);

/**
 * 自动修复网络连接
 * 
 * 检测并尝试修复网络中断开的连接
 * 
 * @param nodes 节点数组
 * @param node_count 节点数量
 * @return 修复的连接数量
 */
int qentl_repair_network_connections(QNetworkNode** nodes, size_t node_count);

#endif /* QENTL_QUANTUM_NETWORK_LIB_H */ 