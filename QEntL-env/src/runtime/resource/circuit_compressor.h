/**
 * QEntL量子电路压缩器头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月25日
 * 
 * 量子电路压缩器负责优化量子电路以减少量子比特数量和门复杂度，
 * 从而提高量子计算的效率和质量。它是资源自适应引擎的关键组件。
 */

#ifndef QENTL_CIRCUIT_COMPRESSOR_H
#define QENTL_CIRCUIT_COMPRESSOR_H

#include <stdbool.h>
#include <stdint.h>
#include "../../quantum/quantum_circuit.h"

// 前向声明
typedef struct CircuitCompressor CircuitCompressor;

/**
 * 压缩策略枚举
 */
typedef enum {
    COMPRESS_STRATEGY_SPEED,       // 速度优先，快速但压缩率较低
    COMPRESS_STRATEGY_BALANCED,    // 平衡模式，速度和压缩率的平衡
    COMPRESS_STRATEGY_AGGRESSIVE,  // 激进模式，最大程度压缩，但速度较慢
    COMPRESS_STRATEGY_LOSSLESS,    // 无损模式，只进行不影响精度的优化
    COMPRESS_STRATEGY_LOSSY        // 有损模式，允许一定程度的精度损失以获得更高压缩率
} CompressionStrategy;

/**
 * 压缩技术枚举
 */
typedef enum {
    COMPRESS_TECH_GATE_CANCELLATION   = 0x0001,  // 门取消/合并技术
    COMPRESS_TECH_QUBIT_REDUCTION     = 0x0002,  // 量子比特减少技术
    COMPRESS_TECH_CIRCUIT_SYNTHESIS   = 0x0004,  // 电路重新合成
    COMPRESS_TECH_TEMPLATE_MATCHING   = 0x0008,  // 模板匹配优化
    COMPRESS_TECH_COMMUTATION_ANALYSIS = 0x0010, // 交换分析
    COMPRESS_TECH_PEEPHOLE_OPTIMIZATION = 0x0020, // 窥孔优化
    COMPRESS_TECH_PHASE_FOLDING       = 0x0040,  // 相位折叠
    COMPRESS_TECH_ZX_CALCULUS         = 0x0080,  // ZX演算优化
    COMPRESS_TECH_ALL                 = 0xFFFF   // 使用所有技术
} CompressionTechnique;

/**
 * 压缩统计信息结构体
 */
typedef struct {
    int original_qubit_count;         // 原始量子比特数
    int compressed_qubit_count;       // 压缩后量子比特数
    int original_gate_count;          // 原始门数量
    int compressed_gate_count;        // 压缩后门数量
    int original_depth;               // 原始电路深度
    int compressed_depth;             // 压缩后电路深度
    double compression_ratio;         // 压缩比率
    double estimated_fidelity;        // 估计保真度
    double compression_time_ms;       // 压缩耗时（毫秒）
    int optimization_iterations;      // 优化迭代次数
} CompressionStats;

/**
 * 压缩器配置结构体
 */
typedef struct {
    CompressionStrategy strategy;     // 压缩策略
    uint32_t techniques;              // 启用的压缩技术（位掩码）
    
    int max_iterations;               // 最大优化迭代次数
    double fidelity_threshold;        // 保真度阈值（针对有损压缩）
    double time_limit_ms;             // 时间限制（毫秒）
    
    bool preserve_entanglement;       // 是否保留纠缠结构
    bool optimize_for_hardware;       // 是否针对特定硬件优化
    char target_hardware[64];         // 目标硬件名称
    
    int min_qubit_count;              // 最小量子比特数量
    bool enable_verification;         // 是否启用压缩后验证
    bool verbose_output;              // 是否输出详细信息
} CircuitCompressorConfig;

/**
 * 创建量子电路压缩器
 * @param config 压缩器配置
 * @return 压缩器实例
 */
CircuitCompressor* circuit_compressor_create(const CircuitCompressorConfig* config);

/**
 * 销毁量子电路压缩器
 * @param compressor 压缩器实例
 */
void circuit_compressor_destroy(CircuitCompressor* compressor);

/**
 * 压缩量子电路
 * @param compressor 压缩器实例
 * @param circuit 要压缩的量子电路
 * @param stats 输出压缩统计信息（可为NULL）
 * @return 压缩后的新量子电路，如果压缩失败则返回NULL
 */
QuantumCircuit* circuit_compressor_compress(CircuitCompressor* compressor, 
                                          const QuantumCircuit* circuit,
                                          CompressionStats* stats);

/**
 * 估计压缩后的量子比特数量
 * @param compressor 压缩器实例
 * @param circuit 要分析的量子电路
 * @return 估计的压缩后量子比特数量
 */
int circuit_compressor_estimate_qubit_count(CircuitCompressor* compressor,
                                          const QuantumCircuit* circuit);

/**
 * 更新压缩器配置
 * @param compressor 压缩器实例
 * @param config 新配置
 * @return 是否成功更新配置
 */
bool circuit_compressor_update_config(CircuitCompressor* compressor,
                                     const CircuitCompressorConfig* config);

/**
 * 获取压缩器配置
 * @param compressor 压缩器实例
 * @param config 输出配置
 * @return 是否成功获取配置
 */
bool circuit_compressor_get_config(CircuitCompressor* compressor,
                                  CircuitCompressorConfig* config);

/**
 * 设置压缩策略
 * @param compressor 压缩器实例
 * @param strategy 压缩策略
 */
void circuit_compressor_set_strategy(CircuitCompressor* compressor,
                                    CompressionStrategy strategy);

/**
 * 启用指定压缩技术
 * @param compressor 压缩器实例
 * @param technique 要启用的压缩技术
 */
void circuit_compressor_enable_technique(CircuitCompressor* compressor,
                                        CompressionTechnique technique);

/**
 * 禁用指定压缩技术
 * @param compressor 压缩器实例
 * @param technique 要禁用的压缩技术
 */
void circuit_compressor_disable_technique(CircuitCompressor* compressor,
                                         CompressionTechnique technique);

/**
 * 检查指定压缩技术是否已启用
 * @param compressor 压缩器实例
 * @param technique 要检查的压缩技术
 * @return 是否已启用
 */
bool circuit_compressor_is_technique_enabled(CircuitCompressor* compressor,
                                           CompressionTechnique technique);

/**
 * 分析电路并生成优化建议
 * @param compressor 压缩器实例
 * @param circuit 要分析的量子电路
 * @param recommendations 输出建议（字符串缓冲区）
 * @param buffer_size 缓冲区大小
 * @return 是否成功生成建议
 */
bool circuit_compressor_analyze(CircuitCompressor* compressor,
                              const QuantumCircuit* circuit,
                              char* recommendations,
                              size_t buffer_size);

/**
 * 获取上次压缩的统计信息
 * @param compressor 压缩器实例
 * @param stats 输出统计信息
 * @return 是否成功获取统计信息
 */
bool circuit_compressor_get_last_stats(CircuitCompressor* compressor,
                                      CompressionStats* stats);

/**
 * 生成压缩报告
 * @param compressor 压缩器实例
 * @param filename 报告文件名
 * @param include_visualization 是否包含电路可视化
 * @return 是否成功生成报告
 */
bool circuit_compressor_generate_report(CircuitCompressor* compressor,
                                       const char* filename,
                                       bool include_visualization);

/**
 * 验证压缩是否保持电路功能等价
 * @param compressor 压缩器实例
 * @param original 原始电路
 * @param compressed 压缩后电路
 * @param fidelity 输出保真度
 * @return 是否功能等价
 */
bool circuit_compressor_verify(CircuitCompressor* compressor,
                             const QuantumCircuit* original,
                             const QuantumCircuit* compressed,
                             double* fidelity);

/**
 * 获取支持的压缩技术列表
 * @param compressor 压缩器实例
 * @param techniques 输出技术列表
 * @param max_techniques 最大返回技术数
 * @param actual_techniques 实际返回技术数
 * @return 是否成功获取列表
 */
bool circuit_compressor_get_supported_techniques(CircuitCompressor* compressor,
                                               CompressionTechnique* techniques,
                                               int max_techniques,
                                               int* actual_techniques);

/**
 * 获取压缩技术名称
 * @param technique 压缩技术
 * @return 技术名称字符串
 */
const char* circuit_compressor_get_technique_name(CompressionTechnique technique);

/**
 * 获取压缩策略名称
 * @param strategy 压缩策略
 * @return 策略名称字符串
 */
const char* circuit_compressor_get_strategy_name(CompressionStrategy strategy);

#endif /* QENTL_CIRCUIT_COMPRESSOR_H */ 