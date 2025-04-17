/**
 * @file profiler_core.h
 * @brief 量子性能分析器头文件
 * @author QEntL开发团队
 * @version 1.0
 * @date 2024-06-10
 *
 * 量子性能分析器用于监测和分析量子程序的执行性能，
 * 包括执行时间、资源使用情况、量子门操作统计等，
 * 以帮助开发者优化量子算法和应用。
 */

#ifndef QENTL_PROFILER_CORE_H
#define QENTL_PROFILER_CORE_H

#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * 分析级别枚举
 */
typedef enum {
    PROFILE_LEVEL_BASIC,      /* 基本级别：只收集总体执行时间和资源使用 */
    PROFILE_LEVEL_STANDARD,   /* 标准级别：增加门操作统计和基本量子指标 */
    PROFILE_LEVEL_DETAILED,   /* 详细级别：增加每个操作的具体时间和细节 */
    PROFILE_LEVEL_QUANTUM     /* 量子级别：包含量子特有指标如纠缠度、保真度等 */
} ProfileLevel;

/**
 * 性能标记类型
 */
typedef enum {
    MARK_CIRCUIT_START,       /* 电路开始执行 */
    MARK_CIRCUIT_END,         /* 电路结束执行 */
    MARK_GATE_START,          /* 门操作开始 */
    MARK_GATE_END,            /* 门操作结束 */
    MARK_MEASUREMENT,         /* 测量操作 */
    MARK_ENTANGLEMENT,        /* 纠缠操作 */
    MARK_MEMORY_ALLOCATE,     /* 内存分配 */
    MARK_MEMORY_FREE,         /* 内存释放 */
    MARK_CUSTOM               /* 自定义标记 */
} MarkType;

/**
 * 统计指标类型
 */
typedef enum {
    METRIC_TIME,              /* 时间指标 */
    METRIC_MEMORY,            /* 内存指标 */
    METRIC_GATE_COUNT,        /* 门计数指标 */
    METRIC_CIRCUIT_DEPTH,     /* 电路深度指标 */
    METRIC_ENTANGLEMENT,      /* 纠缠度指标 */
    METRIC_FIDELITY,          /* 保真度指标 */
    METRIC_ERROR_RATE,        /* 错误率指标 */
    METRIC_CUSTOM             /* 自定义指标 */
} MetricType;

/**
 * 性能标记结构
 */
typedef struct {
    MarkType type;            /* 标记类型 */
    const char* label;        /* 标记标签 */
    struct timespec time;     /* 时间戳 */
    uint64_t memory_usage;    /* 内存使用量 */
    int gate_type;            /* 门类型(如适用) */
    int qubit_count;          /* 涉及的量子比特数(如适用) */
    double value;             /* 附加值(如适用) */
    void* custom_data;        /* 自定义数据 */
} PerformanceMark;

/**
 * 性能计数结构
 */
typedef struct {
    uint64_t total_gates;     /* 总门操作数 */
    uint64_t h_gates;         /* Hadamard门数 */
    uint64_t x_gates;         /* X门数 */
    uint64_t y_gates;         /* Y门数 */
    uint64_t z_gates;         /* Z门数 */
    uint64_t cnot_gates;      /* CNOT门数 */
    uint64_t swap_gates;      /* SWAP门数 */
    uint64_t t_gates;         /* T门数 */
    uint64_t tdg_gates;       /* T†门数 */
    uint64_t s_gates;         /* S门数 */
    uint64_t sdg_gates;       /* S†门数 */
    uint64_t rx_gates;        /* RX门数 */
    uint64_t ry_gates;        /* RY门数 */
    uint64_t rz_gates;        /* RZ门数 */
    uint64_t cx_gates;        /* CX门数 */
    uint64_t cy_gates;        /* CY门数 */
    uint64_t cz_gates;        /* CZ门数 */
    uint64_t measurements;    /* 测量操作数 */
    uint64_t custom_gates;    /* 自定义门数 */
} GateCounter;

/**
 * 性能分析会话结构
 */
typedef struct {
    ProfileLevel level;       /* 分析级别 */
    GateCounter gate_counts;  /* 门计数器 */
    struct timespec start_time; /* 开始时间 */
    struct timespec end_time;   /* 结束时间 */
    double total_duration_ms; /* 总持续时间(毫秒) */
    double max_memory_kb;     /* 最大内存使用(KB) */
    double avg_memory_kb;     /* 平均内存使用(KB) */
    uint32_t sample_count;    /* 样本数量 */
    double circuit_depth;     /* 电路深度 */
    double avg_gate_time_ms;  /* 平均门执行时间(毫秒) */
    double entanglement_degree; /* 纠缠度 */
    double fidelity;          /* 保真度 */
    double error_rate;        /* 错误率 */
} ProfileSession;

/**
 * 性能分析器结构(不透明指针)
 */
typedef struct QuantumProfiler QuantumProfiler;

/**
 * 创建量子性能分析器
 * 
 * @param level 分析级别
 * @return 新创建的性能分析器，失败返回NULL
 */
QuantumProfiler* quantum_profiler_create(ProfileLevel level);

/**
 * 销毁量子性能分析器
 * 
 * @param profiler 性能分析器
 */
void quantum_profiler_destroy(QuantumProfiler* profiler);

/**
 * 开始性能分析会话
 * 
 * @param profiler 性能分析器
 * @param session_name 会话名称
 * @return 成功返回true，失败返回false
 */
bool quantum_profiler_start_session(QuantumProfiler* profiler, const char* session_name);

/**
 * 结束性能分析会话
 * 
 * @param profiler 性能分析器
 * @return 成功返回true，失败返回false
 */
bool quantum_profiler_end_session(QuantumProfiler* profiler);

/**
 * 添加性能标记
 * 
 * @param profiler 性能分析器
 * @param type 标记类型
 * @param label 标记标签
 * @return 成功返回true，失败返回false
 */
bool quantum_profiler_mark(QuantumProfiler* profiler, MarkType type, const char* label);

/**
 * 添加门操作标记
 * 
 * @param profiler 性能分析器
 * @param gate_type 门类型
 * @param qubit_indices 量子比特索引数组
 * @param qubit_count 量子比特数量
 * @return 成功返回true，失败返回false
 */
bool quantum_profiler_mark_gate(QuantumProfiler* profiler, int gate_type, 
                              const int* qubit_indices, int qubit_count);

/**
 * 设置自定义指标
 * 
 * @param profiler 性能分析器
 * @param metric_type 指标类型
 * @param metric_name 指标名称
 * @param value 指标值
 * @return 成功返回true，失败返回false
 */
bool quantum_profiler_set_metric(QuantumProfiler* profiler, MetricType metric_type, 
                               const char* metric_name, double value);

/**
 * 获取当前会话
 * 
 * @param profiler 性能分析器
 * @param session 输出会话信息
 * @return 成功返回true，失败返回false
 */
bool quantum_profiler_get_session(QuantumProfiler* profiler, ProfileSession* session);

/**
 * 生成性能报告
 * 
 * @param profiler 性能分析器
 * @param filename 报告文件名
 * @return 成功返回true，失败返回false
 */
bool quantum_profiler_generate_report(QuantumProfiler* profiler, const char* filename);

/**
 * 打印性能摘要
 * 
 * @param profiler 性能分析器
 */
void quantum_profiler_print_summary(QuantumProfiler* profiler);

/**
 * 比较两个会话的性能差异
 * 
 * @param profiler 性能分析器
 * @param session1_name 第一个会话名称
 * @param session2_name 第二个会话名称
 * @param output_file 输出文件名
 * @return 成功返回true，失败返回false
 */
bool quantum_profiler_compare_sessions(QuantumProfiler* profiler,
                                     const char* session1_name,
                                     const char* session2_name,
                                     const char* output_file);

/**
 * 运行性能分析器测试
 * 
 * @return 成功返回true，失败返回false
 */
bool quantum_profiler_run_test(void);

#ifdef __cplusplus
}
#endif

#endif /* QENTL_PROFILER_CORE_H */ 