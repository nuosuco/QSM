/**
 * 量子状态管理
 * 
 * 定义了QEntL中的量子状态和相关操作。
 * 这是QEntL语言环境中负责管理量子态的核心模块。
 */

#ifndef QENTL_QUANTUM_STATE_H
#define QENTL_QUANTUM_STATE_H

#include <stdint.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

/**
 * 量子比特状态
 * 表示一个量子比特的状态，包含复数振幅
 */
typedef struct {
    double complex alpha;  // |0⟩ 状态的振幅
    double complex beta;   // |1⟩ 状态的振幅
} QubitState;

/**
 * 量子寄存器
 * 表示多个量子比特的集合
 */
typedef struct {
    int num_qubits;               // 量子比特数量
    double complex* amplitudes;    // 状态振幅数组
    int size;                     // 数组大小（2^num_qubits）
} QuantumRegister;

/**
 * 量子纠缠记录
 * 记录量子比特之间的纠缠关系
 */
typedef struct EntanglementNode EntanglementNode;

struct EntanglementNode {
    int qubit_a;                 // 第一个量子比特
    int qubit_b;                 // 第二个量子比特
    double strength;             // 纠缠强度（0-1）
    EntanglementNode* next;      // 下一个纠缠节点
};

/**
 * 量子纠缠图
 * 用于跟踪系统中所有的量子纠缠
 */
typedef struct {
    EntanglementNode* head;      // 纠缠链表头
    int count;                   // 纠缠计数
} EntanglementGraph;

/**
 * 量子态测量结果
 */
typedef struct {
    int result;                  // 测量结果（0或1）
    double probability;          // 测量概率
} MeasurementResult;

/* -------------------- 量子比特函数 -------------------- */

/**
 * 创建一个新的量子比特，默认为|0⟩状态
 */
QubitState create_qubit();

/**
 * 创建自定义状态的量子比特
 */
QubitState create_qubit_state(double complex alpha, double complex beta);

/**
 * 应用Hadamard门，创建叠加态
 */
QubitState apply_hadamard(QubitState qubit);

/**
 * 应用Pauli-X门（量子NOT门）
 */
QubitState apply_pauli_x(QubitState qubit);

/**
 * 应用Pauli-Y门
 */
QubitState apply_pauli_y(QubitState qubit);

/**
 * 应用Pauli-Z门
 */
QubitState apply_pauli_z(QubitState qubit);

/**
 * 应用旋转X门
 */
QubitState apply_rotation_x(QubitState qubit, double angle);

/**
 * 应用旋转Y门
 */
QubitState apply_rotation_y(QubitState qubit, double angle);

/**
 * 应用旋转Z门（相位旋转）
 */
QubitState apply_rotation_z(QubitState qubit, double angle);

/**
 * 应用相位门
 */
QubitState apply_phase(QubitState qubit, double angle);

/**
 * 应用T门
 */
QubitState apply_t_gate(QubitState qubit);

/**
 * 测量量子比特
 * 返回测量结果（0或1）并使量子比特坍缩到相应状态
 */
MeasurementResult measure_qubit(QubitState* qubit);

/* -------------------- 量子寄存器函数 -------------------- */

/**
 * 创建一个新的量子寄存器
 */
QuantumRegister* create_quantum_register(int num_qubits);

/**
 * 释放量子寄存器资源
 */
void free_quantum_register(QuantumRegister* reg);

/**
 * 将量子寄存器重置为|0...0⟩状态
 */
void reset_quantum_register(QuantumRegister* reg);

/**
 * 应用Hadamard门到指定的量子比特
 */
void apply_hadamard_to_qubit(QuantumRegister* reg, int qubit_index);

/**
 * 应用Pauli-X门到指定的量子比特
 */
void apply_pauli_x_to_qubit(QuantumRegister* reg, int qubit_index);

/**
 * 应用受控非门(CNOT)
 */
void apply_cnot(QuantumRegister* reg, int control_qubit, int target_qubit);

/**
 * 应用受控Z门
 */
void apply_controlled_z(QuantumRegister* reg, int control_qubit, int target_qubit);

/**
 * 应用Toffoli门（受控受控非门）
 */
void apply_toffoli(QuantumRegister* reg, int control1, int control2, int target);

/**
 * 应用SWAP门
 */
void apply_swap(QuantumRegister* reg, int qubit_a, int qubit_b);

/**
 * 测量指定的量子比特
 * 返回测量结果并使量子系统坍缩
 */
MeasurementResult measure_qubit_in_register(QuantumRegister* reg, int qubit_index);

/**
 * 获取量子寄存器的状态向量表示
 */
double complex* get_state_vector(QuantumRegister* reg);

/**
 * 计算两个量子比特之间的纠缠度
 * 返回值范围0-1，0表示无纠缠，1表示最大纠缠
 */
double calculate_entanglement(QuantumRegister* reg, int qubit_a, int qubit_b);

/* -------------------- 量子纠缠函数 -------------------- */

/**
 * a创建量子纠缠图
 */
EntanglementGraph* create_entanglement_graph();

/**
 * 释放量子纠缠图资源
 */
void free_entanglement_graph(EntanglementGraph* graph);

/**
 * 添加量子纠缠关系
 */
void add_entanglement(EntanglementGraph* graph, int qubit_a, int qubit_b, double strength);

/**
 * 移除量子纠缠关系
 */
void remove_entanglement(EntanglementGraph* graph, int qubit_a, int qubit_b);

/**
 * 查找两个量子比特之间的纠缠关系
 * 如果不存在返回NULL
 */
EntanglementNode* find_entanglement(EntanglementGraph* graph, int qubit_a, int qubit_b);

/**
 * 更新量子纠缠强度
 */
void update_entanglement_strength(EntanglementGraph* graph, int qubit_a, int qubit_b, double strength);

/**
 * 传播纠缠效应
 * 当量子比特状态改变时，更新所有相关的纠缠比特
 */
void propagate_entanglement_effects(EntanglementGraph* graph, QuantumRegister* reg, int changed_qubit);

#endif /* QENTL_QUANTUM_STATE_H */ 