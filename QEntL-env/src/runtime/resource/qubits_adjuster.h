/**
 * QEntL量子比特调整器头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月25日
 * 
 * 量子比特调整器负责根据当前资源状况和应用需求，
 * 动态调整可用量子比特数量和分配策略，是资源自适应引擎的核心组件。
 */

#ifndef QENTL_QUBITS_ADJUSTER_H
#define QENTL_QUBITS_ADJUSTER_H

#include <stdbool.h>
#include <stdint.h>
#include "resource_monitor.h"
#include "../../quantum/quantum_circuit.h"

// 前向声明
typedef struct QubitsAdjuster QubitsAdjuster;

/**
 * 量子比特分配策略枚举
 */
typedef enum {
    QUBIT_ALLOCATION_BALANCED,    // 平衡策略 - 资源与性能平衡
    QUBIT_ALLOCATION_PERFORMANCE, // 性能优先 - 优先考虑计算性能
    QUBIT_ALLOCATION_RESOURCE,    // 资源优先 - 最小化资源使用
    QUBIT_ALLOCATION_FIDELITY,    // 保真度优先 - 优先考虑结果准确性
    QUBIT_ALLOCATION_ADAPTIVE     // 自适应策略 - 根据任务特性动态调整
} QubitAllocationStrategy;

/**
 * 量子比特调整模式枚举
 */
typedef enum {
    QUBIT_ADJUST_MODE_STATIC,      // 静态模式 - 初始化时设置一次
    QUBIT_ADJUST_MODE_PERIODIC,    // 周期性模式 - 定期调整
    QUBIT_ADJUST_MODE_DYNAMIC,     // 动态模式 - 根据资源变化调整
    QUBIT_ADJUST_MODE_PREDICTIVE,  // 预测模式 - 预测资源需求并提前调整
    QUBIT_ADJUST_MODE_REACTIVE     // 反应式模式 - 根据性能指标调整
} QubitAdjustMode;

/**
 * 量子比特类型枚举
 */
typedef enum {
    QUBIT_TYPE_PHYSICAL,           // 物理量子位
    QUBIT_TYPE_LOGICAL,            // 逻辑量子位
    QUBIT_TYPE_SIMULATED           // 模拟量子位
} QubitType;

/**
 * 量子比特配置结构体
 */
typedef struct {
    int physical_qubits;           // 物理量子比特数量
    int logical_qubits;            // 逻辑量子比特数量
    int total_available_qubits;    // 总可用量子比特数
    double error_rate;             // 错误率
    double coherence_time_us;      // 相干时间（微秒）
    int max_circuit_depth;         // 最大电路深度
    bool ecc_enabled;              // 是否启用纠错码
    int ecc_overhead;              // 纠错码开销（每个逻辑比特需要的物理比特数）
} QubitConfiguration;

/**
 * 量子比特调整器配置结构体
 */
typedef struct {
    QubitAllocationStrategy strategy;     // 分配策略
    QubitAdjustMode adjust_mode;          // 调整模式
    QubitType preferred_qubit_type;       // 首选量子比特类型
    
    int min_qubits;                       // 最小量子比特数
    int max_qubits;                       // 最大量子比特数
    int target_qubits;                    // 目标量子比特数（如果可能）
    
    int adjust_interval_ms;               // 调整间隔（毫秒，用于周期性模式）
    double resource_threshold;            // 资源阈值（触发调整的资源变化百分比）
    
    double performance_weight;            // 性能权重（在平衡模式下）
    double resource_weight;               // 资源权重（在平衡模式下）
    double fidelity_weight;               // 保真度权重（在平衡模式下）
    
    bool enable_ecc;                      // 是否启用量子纠错
    int ecc_level;                        // 纠错级别（0-5，0表示禁用）
    
    bool verbose;                         // 是否输出详细信息
} QubitsAdjusterConfig;

/**
 * 量子比特调整统计信息结构体
 */
typedef struct {
    int initial_qubit_count;              // 初始量子比特数
    int current_qubit_count;              // 当前量子比特数
    int adjustment_count;                 // 调整次数
    
    int max_allocated_qubits;             // 最大分配的量子比特数
    int min_allocated_qubits;             // 最小分配的量子比特数
    
    double average_qubits;                // 平均量子比特数
    double qubit_utilization;             // 量子比特利用率
    
    int64_t last_adjustment_time;         // 上次调整时间（毫秒时间戳）
    QubitConfiguration last_configuration; // 上次量子比特配置
} QubitsAdjusterStats;

/**
 * 创建量子比特调整器
 * @param config 调整器配置
 * @param resource_monitor 资源监控器实例
 * @return 调整器实例
 */
QubitsAdjuster* qubits_adjuster_create(
    const QubitsAdjusterConfig* config,
    ResourceMonitor* resource_monitor);

/**
 * 销毁量子比特调整器
 * @param adjuster 调整器实例
 */
void qubits_adjuster_destroy(QubitsAdjuster* adjuster);

/**
 * 设置调整器配置
 * @param adjuster 调整器实例
 * @param config 新配置
 * @return 是否成功设置
 */
bool qubits_adjuster_set_config(
    QubitsAdjuster* adjuster,
    const QubitsAdjusterConfig* config);

/**
 * 获取调整器配置
 * @param adjuster 调整器实例
 * @param config 输出配置
 * @return 是否成功获取
 */
bool qubits_adjuster_get_config(
    QubitsAdjuster* adjuster,
    QubitsAdjusterConfig* config);

/**
 * 启动调整器
 * @param adjuster 调整器实例
 * @return 是否成功启动
 */
bool qubits_adjuster_start(QubitsAdjuster* adjuster);

/**
 * 停止调整器
 * @param adjuster 调整器实例
 */
void qubits_adjuster_stop(QubitsAdjuster* adjuster);

/**
 * 获取当前量子比特配置
 * @param adjuster 调整器实例
 * @param config 输出量子比特配置
 * @return 是否成功获取
 */
bool qubits_adjuster_get_current_config(
    QubitsAdjuster* adjuster,
    QubitConfiguration* config);

/**
 * 手动触发一次量子比特调整
 * @param adjuster 调整器实例
 * @return 是否成功调整
 */
bool qubits_adjuster_adjust(QubitsAdjuster* adjuster);

/**
 * 为特定任务估计所需量子比特数
 * @param adjuster 调整器实例
 * @param circuit 量子电路
 * @param available_resources 可用资源（百分比，0-100）
 * @param estimated_qubits 输出估计的量子比特数
 * @return 是否成功估计
 */
bool qubits_adjuster_estimate_qubits(
    QubitsAdjuster* adjuster,
    const QuantumCircuit* circuit,
    double available_resources,
    int* estimated_qubits);

/**
 * 为电路分配量子比特
 * @param adjuster 调整器实例
 * @param circuit 量子电路
 * @param allocated_qubits 输出分配的量子比特数
 * @return 是否成功分配
 */
bool qubits_adjuster_allocate_for_circuit(
    QubitsAdjuster* adjuster,
    const QuantumCircuit* circuit,
    int* allocated_qubits);

/**
 * 设置分配策略
 * @param adjuster 调整器实例
 * @param strategy 分配策略
 * @return 是否成功设置
 */
bool qubits_adjuster_set_strategy(
    QubitsAdjuster* adjuster,
    QubitAllocationStrategy strategy);

/**
 * 设置调整模式
 * @param adjuster 调整器实例
 * @param mode 调整模式
 * @return 是否成功设置
 */
bool qubits_adjuster_set_mode(
    QubitsAdjuster* adjuster,
    QubitAdjustMode mode);

/**
 * 获取调整器统计信息
 * @param adjuster 调整器实例
 * @param stats 输出统计信息
 * @return 是否成功获取
 */
bool qubits_adjuster_get_stats(
    QubitsAdjuster* adjuster,
    QubitsAdjusterStats* stats);

/**
 * 生成量子比特调整报告
 * @param adjuster 调整器实例
 * @param filename 报告文件名
 * @return 是否成功生成
 */
bool qubits_adjuster_generate_report(
    QubitsAdjuster* adjuster,
    const char* filename);

/**
 * 重置调整器统计信息
 * @param adjuster 调整器实例
 * @return 是否成功重置
 */
bool qubits_adjuster_reset_stats(QubitsAdjuster* adjuster);

/**
 * 获取可用量子比特数
 * @param adjuster 调整器实例
 * @return 可用量子比特数，失败时返回-1
 */
int qubits_adjuster_get_available_qubits(QubitsAdjuster* adjuster);

/**
 * 获取推荐的量子比特数
 * @param adjuster 调整器实例
 * @param performance_level 性能级别（0-100）
 * @return 推荐的量子比特数，失败时返回-1
 */
int qubits_adjuster_get_recommended_qubits(
    QubitsAdjuster* adjuster,
    int performance_level);

/**
 * 获取分配策略名称
 * @param strategy 分配策略
 * @return 策略名称字符串
 */
const char* qubits_adjuster_get_strategy_name(QubitAllocationStrategy strategy);

/**
 * 获取调整模式名称
 * @param mode 调整模式
 * @return 模式名称字符串
 */
const char* qubits_adjuster_get_mode_name(QubitAdjustMode mode);

/**
 * 获取量子比特类型名称
 * @param type 量子比特类型
 * @return 类型名称字符串
 */
const char* qubits_adjuster_get_qubit_type_name(QubitType type);

#endif /* QENTL_QUBITS_ADJUSTER_H */ 