/**
 * QEntL错误缓解模块头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月25日
 * 
 * 错误缓解模块负责识别、特征化和减轻量子计算中的各种错误，
 * 提供多种错误缓解策略，并根据资源状况和应用需求动态调整策略。
 */

#ifndef QENTL_ERROR_MITIGATION_MODULE_H
#define QENTL_ERROR_MITIGATION_MODULE_H

#include <stdbool.h>
#include <stdint.h>
#include "../../quantum/quantum_circuit.h"
#include "../../quantum/quantum_state.h"

// 前向声明
typedef struct ErrorMitigationModule ErrorMitigationModule;

/**
 * 错误缓解方法枚举
 */
typedef enum {
    ERROR_MITIGATION_NONE,                 // 无错误缓解
    ERROR_MITIGATION_ZNE,                  // 零噪声外推
    ERROR_MITIGATION_RICHARDSON,           // Richardson外推
    ERROR_MITIGATION_PROBABILISTIC_ERROR,  // 概率错误消除
    ERROR_MITIGATION_READOUT,              // 读出错误校正
    ERROR_MITIGATION_SYMMETRY_VERIFICATION,// 对称性验证
    ERROR_MITIGATION_CLIFFORD_DATA,        // Clifford数据回归
    ERROR_MITIGATION_PAULI_FRAME,          // Pauli帧随机化
    ERROR_MITIGATION_ADAPTIVE,             // 自适应错误缓解
    ERROR_MITIGATION_MACHINE_LEARNING      // 机器学习辅助错误缓解
} ErrorMitigationMethod;

/**
 * 错误类型枚举
 */
typedef enum {
    ERROR_TYPE_READOUT,            // 读出错误
    ERROR_TYPE_GATE,               // 门操作错误
    ERROR_TYPE_DECOHERENCE,        // 退相干错误
    ERROR_TYPE_CROSSTALK,          // 串扰错误
    ERROR_TYPE_THERMAL,            // 热噪声错误
    ERROR_TYPE_LEAKAGE,            // 泄漏错误
    ERROR_TYPE_CALIBRATION,        // 校准错误
    ERROR_TYPE_OTHER               // 其他错误
} ErrorType;

/**
 * 错误缓解配置结构体
 */
typedef struct {
    ErrorMitigationMethod method;          // 缓解方法
    bool autoselect_method;                // 是否自动选择方法
    
    // ZNE 配置
    int zne_extrapolation_points;          // 零噪声外推点数
    double zne_scale_factors[5];           // 缩放因子（最多5个）
    
    // 读出错误校正配置
    bool calibrate_readout;                // 是否校准读出错误
    int readout_calibration_shots;         // 读出校准采样数
    
    // 对称性验证配置
    bool use_symmetry_verification;        // 是否使用对称性验证
    int symmetry_verification_shots;       // 对称性验证采样数
    
    // Pauli帧随机化配置
    int pauli_twirling_samples;            // Pauli随机化样本数
    
    // 通用配置
    int max_iterations;                    // 最大迭代次数
    double convergence_threshold;          // 收敛阈值
    double confidence_level;               // 置信水平
    bool store_intermediate_results;       // 是否存储中间结果
    
    int random_seed;                       // 随机数种子（-1表示随机）
    bool verbose;                          // 是否输出详细信息
} ErrorMitigationConfig;

/**
 * 错误缓解结果结构体
 */
typedef struct {
    bool success;                          // 是否成功
    ErrorMitigationMethod method_used;     // 使用的方法
    
    double raw_expectation_value;          // 原始期望值
    double mitigated_expectation_value;    // 缓解后期望值
    double confidence_interval;            // 置信区间
    
    int iterations_used;                   // 使用的迭代次数
    double convergence_metric;             // 收敛指标
    
    double time_taken_ms;                  // 花费时间（毫秒）
    double estimated_error_reduction;      // 估计错误减少比例
    
    char error_message[256];               // 错误信息（如果有）
} ErrorMitigationResult;

/**
 * 错误描述结构体
 */
typedef struct {
    ErrorType type;                        // 错误类型
    int qubit_indices[8];                  // 受影响的量子比特索引（最多8个）
    int qubit_count;                       // 受影响的量子比特数量
    
    double error_rate;                     // 错误率
    double error_variance;                 // 错误方差
    
    char error_model[64];                  // 错误模型描述
    void* additional_data;                 // 附加数据（特定于错误类型）
} ErrorDescription;

/**
 * 创建错误缓解模块
 * @param config 错误缓解配置
 * @return 错误缓解模块实例
 */
ErrorMitigationModule* error_mitigation_module_create(
    const ErrorMitigationConfig* config);

/**
 * 销毁错误缓解模块
 * @param module 错误缓解模块实例
 */
void error_mitigation_module_destroy(ErrorMitigationModule* module);

/**
 * 设置错误缓解配置
 * @param module 错误缓解模块实例
 * @param config 新配置
 * @return 是否成功设置
 */
bool error_mitigation_module_set_config(
    ErrorMitigationModule* module,
    const ErrorMitigationConfig* config);

/**
 * 获取错误缓解配置
 * @param module 错误缓解模块实例
 * @param config 输出配置
 * @return 是否成功获取
 */
bool error_mitigation_module_get_config(
    ErrorMitigationModule* module,
    ErrorMitigationConfig* config);

/**
 * 应用错误缓解于电路
 * @param module 错误缓解模块实例
 * @param circuit 输入电路
 * @param result 错误缓解结果
 * @return 缓解后的电路
 */
QuantumCircuit* error_mitigation_module_apply_to_circuit(
    ErrorMitigationModule* module,
    const QuantumCircuit* circuit,
    ErrorMitigationResult* result);

/**
 * 应用错误缓解于期望值
 * @param module 错误缓解模块实例
 * @param circuit 电路
 * @param raw_expectation_values 原始期望值数组
 * @param observable_count 可观测量数量
 * @param mitigated_expectation_values 输出缓解后期望值数组
 * @param result 错误缓解结果
 * @return 是否成功应用
 */
bool error_mitigation_module_apply_to_expectation(
    ErrorMitigationModule* module,
    const QuantumCircuit* circuit,
    const double* raw_expectation_values,
    int observable_count,
    double* mitigated_expectation_values,
    ErrorMitigationResult* result);

/**
 * 应用错误缓解于测量结果
 * @param module 错误缓解模块实例
 * @param circuit 电路
 * @param raw_counts 原始计数（位串 -> 计数）
 * @param count_size 计数数组大小
 * @param mitigated_counts 输出缓解后计数
 * @param result 错误缓解结果
 * @return 是否成功应用
 */
bool error_mitigation_module_apply_to_counts(
    ErrorMitigationModule* module,
    const QuantumCircuit* circuit,
    const uint64_t* raw_bitstrings,
    const int* raw_counts,
    int count_size,
    uint64_t* mitigated_bitstrings,
    int* mitigated_counts,
    int* mitigated_count_size,
    ErrorMitigationResult* result);

/**
 * 校准错误缓解模块
 * @param module 错误缓解模块实例
 * @param calibration_circuits 校准电路数组
 * @param circuit_count 电路数量
 * @param shots_per_circuit 每个电路的采样数
 * @return 是否成功校准
 */
bool error_mitigation_module_calibrate(
    ErrorMitigationModule* module,
    const QuantumCircuit** calibration_circuits,
    int circuit_count,
    int shots_per_circuit);

/**
 * 分析错误特征
 * @param module 错误缓解模块实例
 * @param circuit 要分析的电路
 * @param descriptions 输出错误描述数组
 * @param max_descriptions 最大描述数
 * @param actual_descriptions 实际描述数
 * @return 是否成功分析
 */
bool error_mitigation_module_analyze_errors(
    ErrorMitigationModule* module,
    const QuantumCircuit* circuit,
    ErrorDescription* descriptions,
    int max_descriptions,
    int* actual_descriptions);

/**
 * 生成错误缓解报告
 * @param module 错误缓解模块实例
 * @param filename 报告文件名
 * @return 是否成功生成
 */
bool error_mitigation_module_generate_report(
    ErrorMitigationModule* module,
    const char* filename);

/**
 * 设置错误模型
 * @param module 错误缓解模块实例
 * @param error_model 错误模型数据
 * @return 是否成功设置
 */
bool error_mitigation_module_set_error_model(
    ErrorMitigationModule* module,
    const void* error_model);

/**
 * 获取推荐的错误缓解方法
 * @param module 错误缓解模块实例
 * @param circuit 电路
 * @param recommended_method 输出推荐方法
 * @return 是否成功获取
 */
bool error_mitigation_module_get_recommended_method(
    ErrorMitigationModule* module,
    const QuantumCircuit* circuit,
    ErrorMitigationMethod* recommended_method);

/**
 * 估计错误缓解后的保真度
 * @param module 错误缓解模块实例
 * @param circuit 电路
 * @param raw_fidelity 原始保真度
 * @param estimated_fidelity 输出估计保真度
 * @return 是否成功估计
 */
bool error_mitigation_module_estimate_fidelity(
    ErrorMitigationModule* module,
    const QuantumCircuit* circuit,
    double raw_fidelity,
    double* estimated_fidelity);

/**
 * 获取错误缓解方法名称
 * @param method 错误缓解方法
 * @return 方法名称字符串
 */
const char* error_mitigation_module_get_method_name(ErrorMitigationMethod method);

/**
 * 清除缓存数据
 * @param module 错误缓解模块实例
 * @return 是否成功清除
 */
bool error_mitigation_module_clear_cache(ErrorMitigationModule* module);

/**
 * 保存错误缓解模块状态
 * @param module 错误缓解模块实例
 * @param filename 文件名
 * @return 是否成功保存
 */
bool error_mitigation_module_save_state(
    ErrorMitigationModule* module,
    const char* filename);

/**
 * 加载错误缓解模块状态
 * @param module 错误缓解模块实例
 * @param filename 文件名
 * @return 是否成功加载
 */
bool error_mitigation_module_load_state(
    ErrorMitigationModule* module,
    const char* filename);

#endif /* QENTL_ERROR_MITIGATION_MODULE_H */ 