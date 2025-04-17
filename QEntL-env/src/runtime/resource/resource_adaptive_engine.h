/**
 * QEntL资源自适应引擎头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月25日
 * 
 * 资源自适应引擎是QEntL运行时的核心组件，负责协调各子模块，
 * 根据系统资源状况和应用需求动态调整量子计算资源分配与使用策略。
 */

#ifndef QENTL_RESOURCE_ADAPTIVE_ENGINE_H
#define QENTL_RESOURCE_ADAPTIVE_ENGINE_H

#include <stdbool.h>
#include <stdint.h>
#include "resource_monitor.h"
#include "qubits_adjuster.h"
#include "circuit_compressor.h"
#include "error_mitigation_module.h"
#include "quantum_simulation_controller.h"
#include "device_capability_detector.h"
#include "../../quantum/quantum_circuit.h"

// 前向声明
typedef struct ResourceAdaptiveEngine ResourceAdaptiveEngine;

/**
 * 自适应引擎状态枚举
 */
typedef enum {
    ADAPTIVE_ENGINE_STATE_INACTIVE,     // 未激活
    ADAPTIVE_ENGINE_STATE_INITIALIZING, // 初始化中
    ADAPTIVE_ENGINE_STATE_ACTIVE,       // 活跃状态
    ADAPTIVE_ENGINE_STATE_PAUSED,       // 暂停状态
    ADAPTIVE_ENGINE_STATE_ERROR         // 错误状态
} AdaptiveEngineState;

/**
 * 自适应优化级别枚举
 */
typedef enum {
    ADAPTIVE_LEVEL_NONE,       // 不进行自适应
    ADAPTIVE_LEVEL_MINIMAL,    // 最小化自适应（仅基本资源监控）
    ADAPTIVE_LEVEL_STANDARD,   // 标准自适应（平衡性能和资源）
    ADAPTIVE_LEVEL_AGGRESSIVE, // 激进自适应（最大化性能优化）
    ADAPTIVE_LEVEL_CUSTOM      // 自定义自适应级别
} AdaptiveOptimizationLevel;

/**
 * 自适应策略枚举
 */
typedef enum {
    ADAPTIVE_STRATEGY_BALANCED,          // 平衡策略
    ADAPTIVE_STRATEGY_PERFORMANCE,       // 性能优先
    ADAPTIVE_STRATEGY_RESOURCE_SAVING,   // 资源节约
    ADAPTIVE_STRATEGY_ACCURACY,          // 精度优先
    ADAPTIVE_STRATEGY_SPEED,             // 速度优先
    ADAPTIVE_STRATEGY_CUSTOM             // 自定义策略
} AdaptiveStrategy;

/**
 * 资源自适应引擎配置结构体
 */
typedef struct {
    AdaptiveOptimizationLevel level;     // 优化级别
    AdaptiveStrategy strategy;           // 自适应策略
    
    bool enable_device_detection;        // 启用设备检测
    bool enable_resource_monitoring;     // 启用资源监控
    bool enable_qubits_adjustment;       // 启用量子比特调整
    bool enable_circuit_compression;     // 启用电路压缩
    bool enable_error_mitigation;        // 启用错误缓解
    bool enable_quantum_simulation;      // 启用量子模拟控制
    
    int update_interval_ms;              // 更新间隔（毫秒）
    
    // 子模块配置（可选，NULL表示使用默认配置）
    ResourceMonitorConfig* monitor_config;                  // 资源监控器配置
    QubitsAdjusterConfig* adjuster_config;                  // 量子比特调整器配置
    CircuitCompressorConfig* compressor_config;             // 电路压缩器配置
    ErrorMitigationConfig* error_mitigation_config;         // 错误缓解模块配置
    SimulationControllerConfig* simulation_controller_config; // 模拟控制器配置
    
    char config_file[256];               // 配置文件路径（用于保存/加载配置）
    bool verbose;                        // 是否输出详细信息
} ResourceAdaptiveEngineConfig;

/**
 * 资源自适应引擎状态统计结构体
 */
typedef struct {
    AdaptiveEngineState state;               // 当前状态
    uint64_t uptime_ms;                      // 运行时间（毫秒）
    
    int total_circuits_processed;            // 处理的总电路数
    int total_optimizations_applied;         // 应用的总优化数
    
    int64_t total_resources_saved;           // 节省的总资源（字节）
    double average_compression_ratio;        // 平均压缩比
    double average_error_reduction;          // 平均错误减少率
    
    int64_t last_update_time;                // 上次更新时间
    char last_error_message[256];            // 上次错误信息
    
    // 子模块统计
    ResourceStatus resource_status;          // 资源状态
    QubitConfiguration qubit_config;         // 量子比特配置
    CompressionStats compression_stats;      // 压缩统计
    
    char device_name[64];                    // 设备名称
    int device_qubits;                       // 设备量子比特数
} ResourceAdaptiveEngineStats;

/**
 * 创建资源自适应引擎
 * @param config 引擎配置
 * @return 引擎实例
 */
ResourceAdaptiveEngine* resource_adaptive_engine_create(const ResourceAdaptiveEngineConfig* config);

/**
 * 销毁资源自适应引擎
 * @param engine 引擎实例
 */
void resource_adaptive_engine_destroy(ResourceAdaptiveEngine* engine);

/**
 * 初始化资源自适应引擎
 * @param engine 引擎实例
 * @return 是否成功初始化
 */
bool resource_adaptive_engine_initialize(ResourceAdaptiveEngine* engine);

/**
 * 启动资源自适应引擎
 * @param engine 引擎实例
 * @return 是否成功启动
 */
bool resource_adaptive_engine_start(ResourceAdaptiveEngine* engine);

/**
 * 停止资源自适应引擎
 * @param engine 引擎实例
 */
void resource_adaptive_engine_stop(ResourceAdaptiveEngine* engine);

/**
 * 暂停资源自适应引擎
 * @param engine 引擎实例
 */
void resource_adaptive_engine_pause(ResourceAdaptiveEngine* engine);

/**
 * 恢复资源自适应引擎
 * @param engine 引擎实例
 */
void resource_adaptive_engine_resume(ResourceAdaptiveEngine* engine);

/**
 * 获取引擎状态
 * @param engine 引擎实例
 * @return 引擎状态
 */
AdaptiveEngineState resource_adaptive_engine_get_state(ResourceAdaptiveEngine* engine);

/**
 * 优化量子电路
 * @param engine 引擎实例
 * @param circuit 输入电路
 * @param optimized_circuit 输出优化后的电路
 * @return 是否成功优化
 */
bool resource_adaptive_engine_optimize_circuit(
    ResourceAdaptiveEngine* engine,
    const QuantumCircuit* circuit,
    QuantumCircuit** optimized_circuit);

/**
 * 更新引擎配置
 * @param engine 引擎实例
 * @param config 新配置
 * @return 是否成功更新
 */
bool resource_adaptive_engine_update_config(
    ResourceAdaptiveEngine* engine,
    const ResourceAdaptiveEngineConfig* config);

/**
 * 获取引擎配置
 * @param engine 引擎实例
 * @param config 输出配置
 * @return 是否成功获取
 */
bool resource_adaptive_engine_get_config(
    ResourceAdaptiveEngine* engine,
    ResourceAdaptiveEngineConfig* config);

/**
 * 获取引擎统计信息
 * @param engine 引擎实例
 * @param stats 输出统计信息
 * @return 是否成功获取
 */
bool resource_adaptive_engine_get_stats(
    ResourceAdaptiveEngine* engine,
    ResourceAdaptiveEngineStats* stats);

/**
 * 设置自适应策略
 * @param engine 引擎实例
 * @param strategy 自适应策略
 * @return 是否成功设置
 */
bool resource_adaptive_engine_set_strategy(
    ResourceAdaptiveEngine* engine,
    AdaptiveStrategy strategy);

/**
 * 设置优化级别
 * @param engine 引擎实例
 * @param level 优化级别
 * @return 是否成功设置
 */
bool resource_adaptive_engine_set_optimization_level(
    ResourceAdaptiveEngine* engine,
    AdaptiveOptimizationLevel level);

/**
 * 手动触发资源检测和调整
 * @param engine 引擎实例
 * @return 是否成功触发
 */
bool resource_adaptive_engine_trigger_adjustment(ResourceAdaptiveEngine* engine);

/**
 * 从配置文件加载引擎配置
 * @param engine 引擎实例
 * @param config_file 配置文件路径
 * @return 是否成功加载
 */
bool resource_adaptive_engine_load_config(
    ResourceAdaptiveEngine* engine,
    const char* config_file);

/**
 * 保存引擎配置到文件
 * @param engine 引擎实例
 * @param config_file 配置文件路径
 * @return 是否成功保存
 */
bool resource_adaptive_engine_save_config(
    ResourceAdaptiveEngine* engine,
    const char* config_file);

/**
 * 生成引擎运行报告
 * @param engine 引擎实例
 * @param report_file 报告文件路径
 * @return 是否成功生成
 */
bool resource_adaptive_engine_generate_report(
    ResourceAdaptiveEngine* engine,
    const char* report_file);

/**
 * 获取优化建议
 * @param engine 引擎实例
 * @param circuit 量子电路
 * @param suggestions 输出建议（字符串缓冲区）
 * @param buffer_size 缓冲区大小
 * @return 是否成功获取
 */
bool resource_adaptive_engine_get_optimization_suggestions(
    ResourceAdaptiveEngine* engine,
    const QuantumCircuit* circuit,
    char* suggestions,
    size_t buffer_size);

/**
 * 获取设备能力检测器
 * @param engine 引擎实例
 * @return 设备能力检测器实例
 */
DeviceCapabilityDetector* resource_adaptive_engine_get_device_detector(
    ResourceAdaptiveEngine* engine);

/**
 * 获取资源监控器
 * @param engine 引擎实例
 * @return 资源监控器实例
 */
ResourceMonitor* resource_adaptive_engine_get_resource_monitor(
    ResourceAdaptiveEngine* engine);

/**
 * 获取量子比特调整器
 * @param engine 引擎实例
 * @return 量子比特调整器实例
 */
QubitsAdjuster* resource_adaptive_engine_get_qubits_adjuster(
    ResourceAdaptiveEngine* engine);

/**
 * 获取电路压缩器
 * @param engine 引擎实例
 * @return 电路压缩器实例
 */
CircuitCompressor* resource_adaptive_engine_get_circuit_compressor(
    ResourceAdaptiveEngine* engine);

/**
 * 获取错误缓解模块
 * @param engine 引擎实例
 * @return 错误缓解模块实例
 */
ErrorMitigationModule* resource_adaptive_engine_get_error_mitigation_module(
    ResourceAdaptiveEngine* engine);

/**
 * 获取量子模拟控制器
 * @param engine 引擎实例
 * @return 量子模拟控制器实例
 */
QuantumSimulationController* resource_adaptive_engine_get_simulation_controller(
    ResourceAdaptiveEngine* engine);

/**
 * 获取自适应策略名称
 * @param strategy 自适应策略
 * @return 策略名称字符串
 */
const char* resource_adaptive_engine_get_strategy_name(AdaptiveStrategy strategy);

/**
 * 获取优化级别名称
 * @param level 优化级别
 * @return 级别名称字符串
 */
const char* resource_adaptive_engine_get_level_name(AdaptiveOptimizationLevel level);

/**
 * 获取引擎状态名称
 * @param state 引擎状态
 * @return 状态名称字符串
 */
const char* resource_adaptive_engine_get_state_name(AdaptiveEngineState state);

#endif /* QENTL_RESOURCE_ADAPTIVE_ENGINE_H */ 