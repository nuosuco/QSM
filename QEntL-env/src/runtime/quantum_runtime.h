/**
 * QEntL量子运行时头文件
 * 
 * 量子基因编码: QG-RT-CORE-HEADER-A1B3
 * 
 * @文件: quantum_runtime.h
 * @描述: QEntL量子运行时的API接口定义
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-15
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 提供的量子状态自动包含量子基因编码和量子纠缠信道
 * - 能根据运行环境自适应调整量子比特处理能力
 */

#ifndef QENTL_QUANTUM_RUNTIME_H
#define QENTL_QUANTUM_RUNTIME_H

#include "../quantum_state.h"
#include "../quantum_gene.h"
#include "../quantum_entanglement.h"

/**
 * 初始化量子运行时
 * 
 * 此函数初始化量子运行时环境，检测可用资源，
 * 应用量子基因编码，并激活节点以参与量子纠缠网络。
 * 
 * @return 成功返回1，失败返回0
 */
int quantum_runtime_initialize(void);

/**
 * 释放量子运行时资源
 */
void quantum_runtime_cleanup(void);

/**
 * 获取可用量子比特数量
 * 
 * @return 可用量子比特数量
 */
int quantum_runtime_get_qubit_count(void);

/**
 * 扩展可用量子比特数量
 * 
 * 此函数用于当连接到高性能计算资源时，
 * 自动扩展量子比特计算能力。
 * 
 * @param additional_qubits 额外的量子比特数量
 * @return 扩展后的总量子比特数量
 */
int quantum_runtime_expand_qubits(int additional_qubits);

/**
 * 创建量子状态
 * 
 * 创建一个带有基因编码和纠缠信息的量子状态。
 * 量子状态自动支持全局纠缠网络。
 * 
 * @param name 状态名称
 * @return 量子状态指针，失败返回NULL
 */
QState* quantum_runtime_create_state(const char* name);

/**
 * 销毁量子状态
 * 
 * @param state 量子状态指针
 */
void quantum_runtime_destroy_state(QState* state);

/**
 * 在两个量子状态之间建立纠缠
 * 
 * @param source 源状态
 * @param target 目标状态
 * @param strength 纠缠强度 (0.0-1.0)
 * @return 成功返回1，失败返回0
 */
int quantum_runtime_entangle_states(QState* source, QState* target, double strength);

/**
 * 获取运行时状态信息
 * 
 * @return 运行时状态信息字符串，需要调用者释放
 */
char* quantum_runtime_get_info(void);

/**
 * 应用量子态叠加
 * 
 * 创建一个叠加态，包含多个不同状态及其概率
 * 
 * @param states 量子态数组
 * @param probabilities 对应的概率数组
 * @param count 状态数量
 * @return 新的叠加态，失败返回NULL
 */
QState* quantum_runtime_create_superposition(QState** states, double* probabilities, size_t count);

/**
 * 测量叠加态，将其坍缩到单一状态
 * 
 * @param state 叠加态指针
 * @return 坍缩后的状态索引
 */
int quantum_runtime_measure_state(QState* state);

/**
 * 应用量子门操作
 * 
 * 在指定的量子状态上应用量子门操作
 * 
 * @param state 量子状态
 * @param gate_type 量子门类型
 * @param params 门参数
 * @return 成功返回1，失败返回0
 */
int quantum_runtime_apply_gate(QState* state, const char* gate_type, double* params);

/**
 * 创建量子场
 * 
 * 创建一个具有特定特性的量子场
 * 
 * @param name 场名称
 * @param field_type 场类型
 * @param params 场参数
 * @return 量子场指针，失败返回NULL
 */
void* quantum_runtime_create_field(const char* name, const char* field_type, double* params);

/**
 * 将状态放入量子场
 * 
 * 将量子状态放入场中，使其受场影响
 * 
 * @param field 量子场
 * @param state 量子状态
 * @return 成功返回1，失败返回0
 */
int quantum_runtime_place_in_field(void* field, QState* state);

/**
 * 更新量子运行时环境状态
 * 
 * 处理外部资源变化，动态调整运行时参数
 * 
 * @return 成功返回1，失败返回0
 */
int quantum_runtime_update(void);

#endif /* QENTL_QUANTUM_RUNTIME_H */ 