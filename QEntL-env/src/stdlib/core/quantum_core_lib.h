/**
 * QEntL标准库核心函数头文件
 * 
 * 量子基因编码: QG-STDLIB-CORE-HEADER-A1B4
 * 
 * @文件: quantum_core_lib.h
 * @描述: 定义QEntL标准库中的核心函数接口，包括基础量子操作和工具函数
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-15
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 函数的输出自动包含量子基因编码和量子纠缠信道
 * - 能根据运行环境自适应调整量子比特处理能力
 */

#ifndef QENTL_QUANTUM_CORE_LIB_H
#define QENTL_QUANTUM_CORE_LIB_H

#include "../../quantum_state.h"

/**
 * 量子门结构
 */
struct QGate {
    char* type;         /* 门类型 */
    double* params;     /* 门参数 */
    int param_count;    /* 参数数量 */
    QGene* gene;        /* 量子基因 */
};

/**
 * 初始化标准库核心组件
 * 
 * @return 成功返回1，失败返回0
 */
int qentl_stdlib_core_initialize(void);

/**
 * 清理标准库核心组件
 */
void qentl_stdlib_core_cleanup(void);

/**
 * 标准库核心版本信息
 * 
 * @return 版本信息字符串
 */
const char* qentl_stdlib_core_version(void);

/**
 * 获取当前可用量子比特数量
 * 
 * @return 可用量子比特数量
 */
int qentl_stdlib_get_qubit_count(void);

/**
 * 创建量子叠加态
 * 
 * @param basis_states 基态名称数组
 * @param amplitudes 对应的振幅数组
 * @param count 状态数量
 * @return 叠加态状态指针，失败返回NULL
 */
QState* qentl_create_superposition(const char** basis_states, 
                                  double* amplitudes, 
                                  size_t count);

/**
 * 测量量子叠加态
 * 
 * @param state 叠加态
 * @return 测量结果索引，-1表示错误
 */
int qentl_measure_state(QState* state);

/**
 * 创建Bell态（最大纠缠态）
 * 
 * @return Bell态指针，失败返回NULL
 */
QState* qentl_create_bell_state(void);

/**
 * 应用Hadamard门
 * 
 * 将|0>变为(|0>+|1>)/√2，将|1>变为(|0>-|1>)/√2
 * 
 * @param state 输入量子态
 * @return 应用Hadamard门后的量子态，失败返回NULL
 */
QState* qentl_apply_hadamard(QState* state);

/**
 * 检查两个量子态是否相等
 * 
 * @param state1 第一个量子态
 * @param state2 第二个量子态
 * @return 相等返回1，不相等返回0
 */
int qentl_states_equal(QState* state1, QState* state2);

/**
 * 创建量子门操作
 * 
 * @param gate_type 门类型
 * @param params 门参数
 * @return 门操作指针，失败返回NULL
 */
void* qentl_create_gate(const char* gate_type, double* params);

/**
 * 应用量子门到状态
 * 
 * @param state 量子态
 * @param gate 量子门
 * @return 应用门后的新状态，失败返回NULL
 */
QState* qentl_apply_gate_to_state(QState* state, void* gate);

/**
 * 释放量子门
 * 
 * @param gate 量子门指针
 */
void qentl_destroy_gate(void* gate);

/**
 * 创建纠缠态
 * 
 * @param state1 第一个状态
 * @param state2 第二个状态
 * @param entanglement_type 纠缠类型
 * @return 纠缠态指针，失败返回NULL
 */
QState* qentl_create_entangled_state(QState* state1, QState* state2, 
                                    const char* entanglement_type);

/**
 * 检查状态是否为纠缠态
 * 
 * @param state 量子态
 * @return 是纠缠态返回1，否则返回0
 */
int qentl_is_entangled(QState* state);

/**
 * 获取叠加态振幅
 * 
 * @param state 叠加态
 * @param basis_index 基态索引
 * @param amplitude 输出振幅值
 * @return 成功返回1，失败返回0
 */
int qentl_get_amplitude(QState* state, int basis_index, double* amplitude);

/**
 * 创建量子寄存器
 * 
 * @param qubit_count 量子比特数量
 * @return 量子寄存器指针，失败返回NULL
 */
void* qentl_create_quantum_register(int qubit_count);

/**
 * 释放量子寄存器
 * 
 * @param reg 量子寄存器指针
 */
void qentl_destroy_quantum_register(void* reg);

/**
 * 应用门到量子寄存器的特定量子比特
 * 
 * @param reg 量子寄存器
 * @param gate 量子门
 * @param target_qubit 目标量子比特索引
 * @return 成功返回1，失败返回0
 */
int qentl_apply_gate_to_register(void* reg, void* gate, int target_qubit);

/**
 * 应用受控门到量子寄存器
 * 
 * @param reg 量子寄存器
 * @param gate 量子门
 * @param control_qubit 控制量子比特索引
 * @param target_qubit 目标量子比特索引
 * @return 成功返回1，失败返回0
 */
int qentl_apply_controlled_gate(void* reg, void* gate, 
                              int control_qubit, int target_qubit);

/**
 * 测量量子寄存器
 * 
 * @param reg 量子寄存器
 * @return 测量结果整数值，失败返回-1
 */
int qentl_measure_register(void* reg);

/**
 * 创建量子纠缠点
 * 
 * @param name 纠缠点名称
 * @return 纠缠点指针，失败返回NULL
 */
void* qentl_create_entanglement_point(const char* name);

/**
 * 添加状态到纠缠点
 * 
 * @param point 纠缠点
 * @param state 量子态
 * @return 成功返回1，失败返回0
 */
int qentl_add_state_to_entanglement_point(void* point, QState* state);

/**
 * 创建量子纠缠通道
 * 
 * @param source_point 源纠缠点
 * @param target_point 目标纠缠点
 * @param strength 纠缠强度 (0.0-1.0)
 * @return 纠缠通道指针，失败返回NULL
 */
void* qentl_create_entanglement_channel(void* source_point, 
                                      void* target_point, 
                                      double strength);

/**
 * 通过纠缠通道传输状态
 * 
 * @param channel 纠缠通道
 * @param state 量子态
 * @return 传输后的状态副本，失败返回NULL
 */
QState* qentl_transmit_state(void* channel, QState* state);

#endif /* QENTL_QUANTUM_CORE_LIB_H */ 