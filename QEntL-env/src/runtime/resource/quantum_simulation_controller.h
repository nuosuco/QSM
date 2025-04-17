/**
 * QEntL量子模拟控制器头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月25日
 * 
 * 量子模拟控制器负责管理量子模拟过程，根据可用资源动态选择
 * 最合适的模拟方法和参数，确保模拟的效率和精度。
 */

#ifndef QENTL_QUANTUM_SIMULATION_CONTROLLER_H
#define QENTL_QUANTUM_SIMULATION_CONTROLLER_H

#include <stdbool.h>
#include <stdint.h>
#include "../../quantum/quantum_circuit.h"
#include "../../quantum/quantum_state.h"

// 前向声明
typedef struct QuantumSimulationController QuantumSimulationController;

/**
 * 模拟方法枚举
 */
typedef enum {
    SIMULATION_METHOD_STATEVECTOR,    // 状态向量模拟（精确但资源消耗大）
    SIMULATION_METHOD_DENSITY_MATRIX, // 密度矩阵模拟（支持混合态）
    SIMULATION_METHOD_TENSOR_NETWORK, // 张量网络模拟（适合特定结构电路）
    SIMULATION_METHOD_STABILIZER,     // 稳定器模拟（适合Clifford门）
    SIMULATION_METHOD_MPS,            // 矩阵乘积状态模拟
    SIMULATION_METHOD_ADAPTIVE,       // 自适应模拟（自动选择）
    SIMULATION_METHOD_DISTRIBUTED     // 分布式模拟
} SimulationMethod;

/**
 * 模拟精度枚举
 */
typedef enum {
    SIMULATION_PRECISION_SINGLE,      // 单精度浮点
    SIMULATION_PRECISION_DOUBLE,      // 双精度浮点
    SIMULATION_PRECISION_EXTENDED,    // 扩展精度
    SIMULATION_PRECISION_ADAPTIVE     // 自适应精度
} SimulationPrecision;

/**
 * 模拟模式枚举
 */
typedef enum {
    SIMULATION_MODE_FULL,             // 完整模拟
    SIMULATION_MODE_SAMPLING,         // 采样模式
    SIMULATION_MODE_EXPECTATION,      // 期望值计算
    SIMULATION_MODE_TRAJECTORY        // 轨迹模拟
} SimulationMode;

/**
 * 硬件加速类型枚举
 */
typedef enum {
    ACCELERATION_NONE,                // 无加速
    ACCELERATION_GPU,                 // GPU加速
    ACCELERATION_MPI,                 // MPI分布式加速
    ACCELERATION_HYBRID               // 混合加速
} AccelerationType;

/**
 * 模拟统计信息结构体
 */
typedef struct {
    int qubit_count;                   // 模拟的量子比特数
    uint64_t state_dimension;          // 状态空间维度 (2^n)
    SimulationMethod method_used;      // 使用的模拟方法
    SimulationPrecision precision_used; // 使用的精度
    AccelerationType acceleration_used; // 使用的加速类型
    
    double setup_time_ms;              // 设置时间（毫秒）
    double simulation_time_ms;         // 模拟时间（毫秒）
    double memory_used_mb;             // 使用的内存（MB）
    
    uint64_t operations_count;         // 操作计数
    int max_entanglement_width;        // 最大纠缠宽度
    double estimated_fidelity;         // 估计保真度
    
    bool success;                      // 模拟是否成功
    char error_message[256];           // 错误信息（如果有）
} SimulationStats;

/**
 * 模拟控制器配置结构体
 */
typedef struct {
    SimulationMethod preferred_method;   // 首选模拟方法
    SimulationPrecision precision;       // 模拟精度
    SimulationMode mode;                 // 模拟模式
    AccelerationType acceleration;       // 硬件加速类型
    
    int max_qubit_count;                 // 最大量子比特数限制
    uint64_t max_memory_mb;              // 最大内存使用限制（MB）
    double time_limit_sec;               // 时间限制（秒）
    
    bool enable_optimization;            // 是否启用优化
    bool enable_noise_simulation;        // 是否启用噪声模拟
    bool enable_checkpointing;           // 是否启用检查点
    
    double target_fidelity;              // 目标保真度
    int random_seed;                     // 随机数种子（-1表示使用时间种子）
    
    char device_profile[64];             // 设备配置文件名（针对真实设备模拟）
    bool verbose;                        // 是否输出详细信息
} SimulationControllerConfig;

/**
 * 创建量子模拟控制器
 * @param config 控制器配置
 * @return 控制器实例
 */
QuantumSimulationController* quantum_simulation_controller_create(
    const SimulationControllerConfig* config);

/**
 * 销毁量子模拟控制器
 * @param controller 控制器实例
 */
void quantum_simulation_controller_destroy(QuantumSimulationController* controller);

/**
 * 设置模拟控制器配置
 * @param controller 控制器实例
 * @param config 新配置
 * @return 是否成功设置
 */
bool quantum_simulation_controller_set_config(
    QuantumSimulationController* controller,
    const SimulationControllerConfig* config);

/**
 * 获取模拟控制器配置
 * @param controller 控制器实例
 * @param config 输出配置
 * @return 是否成功获取
 */
bool quantum_simulation_controller_get_config(
    QuantumSimulationController* controller,
    SimulationControllerConfig* config);

/**
 * 执行量子电路模拟
 * @param controller 控制器实例
 * @param circuit 要模拟的量子电路
 * @param input_state 输入量子态（可为NULL，默认为|0...0>）
 * @param stats 输出模拟统计信息（可为NULL）
 * @return 模拟后的量子态，如果模拟失败则返回NULL
 */
QuantumState* quantum_simulation_controller_run(
    QuantumSimulationController* controller,
    const QuantumCircuit* circuit,
    const QuantumState* input_state,
    SimulationStats* stats);

/**
 * 执行电路的采样模拟
 * @param controller 控制器实例
 * @param circuit 要模拟的量子电路
 * @param shots 采样次数
 * @param qubits_to_measure 要测量的量子比特索引数组
 * @param qubit_count 要测量的量子比特数量
 * @param results 输出结果数组（大小应为shots）
 * @param stats 输出模拟统计信息（可为NULL）
 * @return 是否成功执行采样
 */
bool quantum_simulation_controller_sample(
    QuantumSimulationController* controller,
    const QuantumCircuit* circuit,
    int shots,
    const int* qubits_to_measure,
    int qubit_count,
    uint64_t* results,
    SimulationStats* stats);

/**
 * 计算期望值
 * @param controller 控制器实例
 * @param circuit 要模拟的量子电路
 * @param observable 可观测量
 * @param expectation_value 输出期望值
 * @param stats 输出模拟统计信息（可为NULL）
 * @return 是否成功计算
 */
bool quantum_simulation_controller_expectation(
    QuantumSimulationController* controller,
    const QuantumCircuit* circuit,
    const void* observable,
    double* expectation_value,
    SimulationStats* stats);

/**
 * 中断正在进行的模拟
 * @param controller 控制器实例
 * @return 是否成功中断
 */
bool quantum_simulation_controller_interrupt(QuantumSimulationController* controller);

/**
 * 分析电路并自动选择模拟方法
 * @param controller 控制器实例
 * @param circuit 要分析的量子电路
 * @param recommended_method 输出推荐的模拟方法
 * @param estimated_resources 输出估计资源需求（MB）
 * @return 是否成功分析
 */
bool quantum_simulation_controller_analyze_circuit(
    QuantumSimulationController* controller,
    const QuantumCircuit* circuit,
    SimulationMethod* recommended_method,
    double* estimated_resources);

/**
 * 检查电路是否可模拟
 * @param controller 控制器实例
 * @param circuit 要检查的量子电路
 * @param reason 输出不可模拟的原因（若无法模拟）
 * @param buffer_size 缓冲区大小
 * @return 是否可模拟
 */
bool quantum_simulation_controller_can_simulate(
    QuantumSimulationController* controller,
    const QuantumCircuit* circuit,
    char* reason,
    size_t buffer_size);

/**
 * 进行分布式模拟设置
 * @param controller 控制器实例
 * @param node_count 节点数
 * @param nodes_info 节点信息数组
 * @return 是否成功设置
 */
bool quantum_simulation_controller_setup_distributed(
    QuantumSimulationController* controller,
    int node_count,
    const char** nodes_info);

/**
 * 获取上次模拟的统计信息
 * @param controller 控制器实例
 * @param stats 输出统计信息
 * @return 是否成功获取
 */
bool quantum_simulation_controller_get_last_stats(
    QuantumSimulationController* controller,
    SimulationStats* stats);

/**
 * 生成模拟报告
 * @param controller 控制器实例
 * @param filename 报告文件名
 * @return 是否成功生成
 */
bool quantum_simulation_controller_generate_report(
    QuantumSimulationController* controller,
    const char* filename);

/**
 * 设置模拟噪声模型
 * @param controller 控制器实例
 * @param noise_model 噪声模型数据
 * @return 是否成功设置
 */
bool quantum_simulation_controller_set_noise_model(
    QuantumSimulationController* controller,
    const void* noise_model);

/**
 * 获取可用模拟方法
 * @param controller 控制器实例
 * @param methods 输出方法数组
 * @param max_methods 最大方法数
 * @param actual_methods 实际方法数
 * @return 是否成功获取
 */
bool quantum_simulation_controller_get_available_methods(
    QuantumSimulationController* controller,
    SimulationMethod* methods,
    int max_methods,
    int* actual_methods);

/**
 * 设置模拟方法
 * @param controller 控制器实例
 * @param method 模拟方法
 * @return 是否成功设置
 */
bool quantum_simulation_controller_set_method(
    QuantumSimulationController* controller,
    SimulationMethod method);

/**
 * 设置硬件加速类型
 * @param controller 控制器实例
 * @param acceleration 加速类型
 * @return 是否成功设置
 */
bool quantum_simulation_controller_set_acceleration(
    QuantumSimulationController* controller,
    AccelerationType acceleration);

/**
 * 保存模拟状态到文件
 * @param controller 控制器实例
 * @param filename 文件名
 * @return 是否成功保存
 */
bool quantum_simulation_controller_save_state(
    QuantumSimulationController* controller,
    const char* filename);

/**
 * 从文件加载模拟状态
 * @param controller 控制器实例
 * @param filename 文件名
 * @return 是否成功加载
 */
bool quantum_simulation_controller_load_state(
    QuantumSimulationController* controller,
    const char* filename);

/**
 * 获取模拟方法名称
 * @param method 模拟方法
 * @return 方法名称字符串
 */
const char* quantum_simulation_controller_get_method_name(SimulationMethod method);

/**
 * 获取加速类型名称
 * @param acceleration 加速类型
 * @return 加速类型名称字符串
 */
const char* quantum_simulation_controller_get_acceleration_name(AccelerationType acceleration);

#endif /* QENTL_QUANTUM_SIMULATION_CONTROLLER_H */ 