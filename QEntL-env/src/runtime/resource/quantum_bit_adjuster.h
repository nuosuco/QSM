/**
 * @file quantum_bit_adjuster.h
 * @brief 量子比特调整器 - 管理和优化量子比特资源分配
 * @author QEntL开发团队
 * @version 1.1
 * @date 2024-06-05
 *
 * 量子比特调整器负责动态调整可用量子比特数量和分配策略，
 * 基于系统资源条件、应用需求和执行环境。
 * 它可以根据当前系统状态和算法复杂度优化量子计算资源利用。
 * 此文件包含了从两个原始实现整合而来的功能。
 */

#ifndef QUANTUM_BIT_ADJUSTER_H
#define QUANTUM_BIT_ADJUSTER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* 调整策略枚举 */
typedef enum {
    ADJUSTMENT_STRATEGY_CONSERVATIVE,    /* 保守策略：优先考虑稳定性，缓慢调整 */
    ADJUSTMENT_STRATEGY_AGGRESSIVE,      /* 激进策略：快速调整以获得最佳性能 */
    ADJUSTMENT_STRATEGY_BALANCED,        /* 平衡策略：在性能与稳定性间取平衡 */
    ADJUSTMENT_STRATEGY_LEARNING,        /* 学习策略：根据历史数据学习最佳配置 */
    ADJUSTMENT_STRATEGY_ERROR_MINIMIZING /* 错误最小化：优先考虑降低错误率 */
} AdjustmentStrategy;

/* 量子执行模式 */
typedef enum {
    QUANTUM_EXECUTION_MODE_SIMULATION,   /* 模拟模式：在经典计算机上模拟量子计算 */
    QUANTUM_EXECUTION_MODE_HARDWARE,     /* 硬件模式：在实际量子处理器上执行 */
    QUANTUM_EXECUTION_MODE_HYBRID        /* 混合模式：部分在模拟器上，部分在硬件上 */
} QuantumExecutionMode;

/* 量子比特分配策略 */
typedef enum {
    QUBIT_ALLOCATION_STATIC,             /* 静态分配：一次性分配固定数量 */
    QUBIT_ALLOCATION_DYNAMIC,            /* 动态分配：根据需要增减 */
    QUBIT_ALLOCATION_POOLED,             /* 池化分配：使用预分配的池 */
    QUBIT_ALLOCATION_PRIORITIZED,        /* 优先级分配：基于任务重要性 */
    QUBIT_ALLOCATION_ADAPTIVE            /* 自适应分配：根据算法特性动态调整 */
} QubitAllocationStrategy;

/* 量子比特调整模式 */
typedef enum {
    QUBIT_ADJUST_MODE_REALTIME,          /* 实时模式：持续监控和调整 */
    QUBIT_ADJUST_MODE_SCHEDULED,         /* 计划模式：按计划间隔调整 */
    QUBIT_ADJUST_MODE_TRIGGER,           /* 触发模式：在特定事件时调整 */
    QUBIT_ADJUST_MODE_MANUAL             /* 手动模式：用户手动触发调整 */
} QubitAdjustMode;

/* 量子比特类型 */
typedef enum {
    QUBIT_TYPE_PHYSICAL,                 /* 物理量子比特：直接对应硬件 */
    QUBIT_TYPE_LOGICAL,                  /* 逻辑量子比特：包含错误校正 */
    QUBIT_TYPE_VIRTUAL                   /* 虚拟量子比特：模拟或抽象表示 */
} QubitType;

/**
 * @brief 量子比特调整器配置结构
 */
typedef struct {
    uint32_t min_qubits;               /* 最小量子比特数量 */
    uint32_t max_qubits;               /* 最大量子比特数量 */
    double target_fidelity;            /* 目标保真度 (0.0-1.0) */
    uint64_t memory_limit_kb;          /* 内存限制 (KB) */
    double error_threshold;            /* 错误率阈值 */
    unsigned int adjustment_interval_ms;/* 调整间隔 (毫秒) */
    AdjustmentStrategy strategy;       /* 调整策略 */
    QuantumExecutionMode execution_mode;/* 执行模式 */
    float performance_weight;          /* 性能权重因子 */
    float stability_weight;            /* 稳定性权重因子 */
    QubitAllocationStrategy allocation_strategy; /* 量子比特分配策略 */
    QubitAdjustMode adjust_mode;       /* 调整模式 */
    QubitType qubit_type;              /* 量子比特类型 */
    bool use_error_correction;         /* 是否使用错误校正 */
    uint32_t error_correction_overhead; /* 错误校正开销 */
    bool dynamic_routing;              /* 是否使用动态路由 */
    double connectivity_factor;        /* 连接因子 (影响拓扑限制) */
} QuantumBitAdjusterConfig;

/**
 * @brief 量子比特配置结构
 */
typedef struct {
    uint32_t physical_qubits;          /* 物理量子比特数量 */
    uint32_t logical_qubits;           /* 逻辑量子比特数量 */
    double coherence_time_us;          /* 相干时间 (微秒) */
    double gate_fidelity;              /* 门操作保真度 */
    double readout_fidelity;           /* 读取保真度 */
    uint32_t max_circuit_depth;        /* 最大电路深度 */
    bool supports_mid_circuit_measurement; /* 是否支持电路中途测量 */
    char topology_description[256];    /* 拓扑结构描述 */
} QubitConfiguration;

/**
 * @brief 量子比特调整器统计信息
 */
typedef struct {
    uint32_t current_qubits;           /* 当前量子比特数量 */
    uint32_t max_qubits_used;          /* 历史最大使用量 */
    uint32_t adjustments_count;        /* 调整次数 */
    double average_fidelity;           /* 平均保真度 */
    double lowest_fidelity;            /* 最低保真度 */
    uint64_t memory_usage_kb;          /* 内存使用量 (KB) */
    uint64_t max_memory_usage_kb;      /* 最大内存使用量 (KB) */
    double average_error_rate;         /* 平均错误率 */
    uint32_t error_correction_count;   /* 错误校正次数 */
    char last_adjustment_reason[256];  /* 最近一次调整原因 */
    uint64_t total_execution_time_ms;  /* 总执行时间 (毫秒) */
    uint32_t successful_circuits;      /* 成功执行的电路数 */
    uint32_t failed_circuits;          /* 失败的电路数 */
} QubitsAdjusterStats;

/**
 * @brief 调整器状态结构
 */
typedef struct {
    uint32_t current_qubits;           /* 当前量子比特数量 */
    uint32_t recommended_qubits;       /* 推荐量子比特数量 */
    double estimated_fidelity;         /* 估计保真度 */
    bool resource_limited;             /* 是否受资源限制 */
    bool error_condition;              /* 是否有错误状态 */
    char error_message[256];           /* 错误消息 */
    unsigned long last_adjustment_time_ms; /* 上次调整时间 (毫秒) */
    QuantumExecutionMode current_mode; /* 当前执行模式 */
    double current_error_rate;         /* 当前错误率 */
    bool is_stable;                    /* 是否稳定 */
    double memory_usage_ratio;         /* 内存使用比例 */
    uint32_t available_physical_qubits; /* 可用物理量子比特 */
    uint32_t available_logical_qubits;  /* 可用逻辑量子比特 */
} AdjusterStatus;

/**
 * @brief 事件回调函数类型
 */
typedef enum {
    EVENT_ADJUSTMENT_STARTED,           /* 调整开始 */
    EVENT_ADJUSTMENT_COMPLETED,         /* 调整完成 */
    EVENT_ERROR_DETECTED,               /* 检测到错误 */
    EVENT_RESOURCE_LIMIT_REACHED,       /* 达到资源限制 */
    EVENT_FIDELITY_CHANGE,              /* 保真度变化 */
    EVENT_MODE_CHANGE                   /* 模式变化 */
} AdjustmentEventType;

/**
 * @brief 事件回调函数类型定义
 */
typedef void (*EventCallbackFn)(AdjustmentEventType event_type, void* data, void* user_data);

/**
 * @brief 性能预测结果结构
 */
typedef struct {
    double estimated_runtime_ms;        /* 估计运行时间 (毫秒) */
    double estimated_fidelity;          /* 估计保真度 */
    uint64_t estimated_memory_kb;       /* 估计内存使用 (KB) */
    bool feasible;                      /* 是否可行 */
    char limitations[256];              /* 限制因素描述 */
} PerformancePrediction;

/**
 * @brief 电路复杂度结构
 */
typedef struct {
    uint32_t qubit_count;               /* 量子比特数量 */
    uint32_t gate_count;                /* 门操作数量 */
    uint32_t depth;                     /* 电路深度 */
    uint32_t measurement_count;         /* 测量操作数量 */
    double entanglement_degree;         /* 纠缠程度 */
    bool has_mid_circuit_measurement;   /* 是否有中途测量 */
} CircuitComplexity;

/**
 * @brief 创建量子比特调整器
 * 
 * @param device_capability_detector 设备能力检测器 (可以为NULL)
 * @return 成功返回调整器指针，失败返回NULL
 */
void* quantum_bit_adjuster_create(void* device_capability_detector);

/**
 * @brief 销毁量子比特调整器
 * 
 * @param adjuster 调整器指针
 */
void quantum_bit_adjuster_destroy(void* adjuster);

/**
 * @brief 设置量子比特调整器配置
 * 
 * @param adjuster 调整器指针
 * @param config 配置结构体指针
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_set_config(void* adjuster, const QuantumBitAdjusterConfig* config);

/**
 * @brief 获取量子比特调整器配置
 * 
 * @param adjuster 调整器指针
 * @param config 配置结构体指针，用于存储当前配置
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_get_config(const void* adjuster, QuantumBitAdjusterConfig* config);

/**
 * @brief 获取调整器当前状态
 * 
 * @param adjuster 调整器指针
 * @param status 状态结构体指针，用于存储当前状态
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_get_status(const void* adjuster, AdjusterStatus* status);

/**
 * @brief 注册事件回调函数
 * 
 * @param adjuster 调整器指针
 * @param event_type 事件类型
 * @param callback 回调函数
 * @param user_data 用户数据
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_register_callback(void* adjuster, AdjustmentEventType event_type, 
                                         EventCallbackFn callback, void* user_data);

/**
 * @brief 取消注册事件回调函数
 * 
 * @param adjuster 调整器指针
 * @param event_type 事件类型
 * @param callback 回调函数
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_unregister_callback(void* adjuster, AdjustmentEventType event_type, 
                                           EventCallbackFn callback);

/**
 * @brief 执行量子比特数量调整
 * 
 * @param adjuster 调整器指针
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_adjust(void* adjuster);

/**
 * @brief 预测给定电路的性能
 * 
 * @param adjuster 调整器指针
 * @param circuit_complexity 电路复杂度描述
 * @param prediction 用于存储预测结果
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_predict_performance(void* adjuster, 
                                           const CircuitComplexity* circuit_complexity,
                                           PerformancePrediction* prediction);

/**
 * @brief 估计算法所需的量子比特数量
 * 
 * @param adjuster 调整器指针
 * @param algorithm_name 算法名称
 * @param problem_size 问题规模
 * @param target_accuracy 目标精度
 * @return 估计的量子比特数量，出错返回0
 */
uint32_t quantum_bit_adjuster_estimate_qubits_for_algorithm(void* adjuster, 
                                                          const char* algorithm_name,
                                                          uint32_t problem_size,
                                                          double target_accuracy);

/**
 * @brief 估计给定电路所需的量子比特数量
 * 
 * @param adjuster 调整器指针
 * @param circuit_complexity 电路复杂度描述
 * @param target_fidelity 目标保真度
 * @return 估计的量子比特数量，出错返回0
 */
uint32_t quantum_bit_adjuster_estimate_qubits_for_circuit(void* adjuster,
                                                        const CircuitComplexity* circuit_complexity,
                                                        double target_fidelity);

/**
 * @brief 开始自动调整
 * 
 * @param adjuster 调整器指针
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_start_auto_adjustment(void* adjuster);

/**
 * @brief 停止自动调整
 * 
 * @param adjuster 调整器指针
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_stop_auto_adjustment(void* adjuster);

/**
 * @brief 验证算法配置是否可行
 * 
 * @param adjuster 调整器指针
 * @param algorithm_name 算法名称
 * @param qubits 量子比特数量
 * @param circuit_depth 电路深度
 * @return 可行返回true，不可行返回false
 */
bool quantum_bit_adjuster_validate_algorithm(void* adjuster, 
                                           const char* algorithm_name,
                                           uint32_t qubits,
                                           uint32_t circuit_depth);

/**
 * @brief 生成配置报告
 * 
 * @param adjuster 调整器指针
 * @param report_file 报告文件路径
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_generate_report(void* adjuster, const char* report_file);

/**
 * @brief 估计内存使用量
 * 
 * @param qubits 量子比特数量
 * @param circuit_depth 电路深度
 * @return 估计的内存使用量 (KB)
 */
uint64_t quantum_bit_adjuster_estimate_memory_usage(uint32_t qubits, uint32_t circuit_depth);

/**
 * @brief 估计保真度
 * 
 * @param adjuster 调整器指针
 * @param qubits 量子比特数量
 * @param circuit_depth 电路深度
 * @return 估计的保真度 (0.0-1.0)
 */
double quantum_bit_adjuster_estimate_fidelity(void* adjuster, uint32_t qubits, uint32_t circuit_depth);

/**
 * @brief 获取调整器统计信息
 * 
 * @param adjuster 调整器指针
 * @param stats 统计结构体指针，用于存储统计信息
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_get_stats(const void* adjuster, QubitsAdjusterStats* stats);

/**
 * @brief 重置调整器统计信息
 * 
 * @param adjuster 调整器指针
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_reset_stats(void* adjuster);

/**
 * @brief 申请特定数量的量子比特
 * 
 * @param adjuster 调整器指针
 * @param qubits_requested 请求的量子比特数量
 * @param qubit_type 量子比特类型
 * @return 实际分配的量子比特数量，出错返回0
 */
uint32_t quantum_bit_adjuster_request_qubits(void* adjuster, 
                                           uint32_t qubits_requested, 
                                           QubitType qubit_type);

/**
 * @brief 释放之前申请的量子比特
 * 
 * @param adjuster 调整器指针
 * @param qubits_to_release 要释放的量子比特数量
 * @param qubit_type 量子比特类型
 * @return 成功返回0，失败返回非0值
 */
int quantum_bit_adjuster_release_qubits(void* adjuster, 
                                      uint32_t qubits_to_release, 
                                      QubitType qubit_type);

/**
 * @brief 通知调整器即将执行的电路
 * 
 * @param adjuster 调整器指针
 * @param circuit_complexity 电路复杂度描述
 * @return 建议的量子比特数量，出错返回0
 */
uint32_t quantum_bit_adjuster_notify_upcoming_circuit(void* adjuster, 
                                                    const CircuitComplexity* circuit_complexity);

#ifdef __cplusplus
}
#endif

#endif /* QUANTUM_BIT_ADJUSTER_H */ 