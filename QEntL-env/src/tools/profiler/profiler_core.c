/**
 * @file profiler_core.c
 * @brief 量子性能分析器实现
 * @author QEntL开发团队
 * @version 1.0
 * @date 2024-06-10
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include "profiler_core.h"

#define MAX_SESSIONS 10
#define MAX_MARKS 1000
#define MAX_METRICS 50
#define MAX_SESSION_NAME 64

/**
 * 指标数据结构
 */
typedef struct {
    MetricType type;
    char name[64];
    double value;
} Metric;

/**
 * 会话实例结构
 */
typedef struct {
    char name[MAX_SESSION_NAME];
    ProfileSession data;
    PerformanceMark* marks;
    size_t mark_count;
    size_t mark_capacity;
    Metric* metrics;
    size_t metric_count;
    bool active;
} SessionInstance;

/**
 * 性能分析器完整结构
 */
struct QuantumProfiler {
    ProfileLevel level;
    SessionInstance* sessions;
    size_t session_count;
    size_t active_session;
    bool is_collecting;
};

/**
 * 获取当前时间
 */
static void get_current_time(struct timespec* time) {
#ifdef _WIN32
    timespec_get(time, TIME_UTC);
#else
    clock_gettime(CLOCK_MONOTONIC, time);
#endif
}

/**
 * 计算两个时间点的差值(毫秒)
 */
static double calculate_time_diff_ms(const struct timespec* start, const struct timespec* end) {
    return (end->tv_sec - start->tv_sec) * 1000.0 + 
           (end->tv_nsec - start->tv_nsec) / 1000000.0;
}

/**
 * 创建量子性能分析器
 */
QuantumProfiler* quantum_profiler_create(ProfileLevel level) {
    QuantumProfiler* profiler = (QuantumProfiler*)malloc(sizeof(QuantumProfiler));
    if (!profiler) {
        fprintf(stderr, "错误: 无法为性能分析器分配内存\n");
        return NULL;
    }
    
    profiler->level = level;
    profiler->is_collecting = false;
    profiler->active_session = (size_t)-1;
    
    // 分配会话数组
    profiler->sessions = (SessionInstance*)malloc(MAX_SESSIONS * sizeof(SessionInstance));
    if (!profiler->sessions) {
        fprintf(stderr, "错误: 无法为会话数组分配内存\n");
        free(profiler);
        return NULL;
    }
    
    profiler->session_count = 0;
    
    printf("量子性能分析器已创建，分析级别: %d\n", level);
    return profiler;
}

/**
 * 销毁量子性能分析器
 */
void quantum_profiler_destroy(QuantumProfiler* profiler) {
    if (!profiler) return;
    
    // 释放每个会话的资源
    for (size_t i = 0; i < profiler->session_count; i++) {
        SessionInstance* session = &profiler->sessions[i];
        if (session->marks) free(session->marks);
        if (session->metrics) free(session->metrics);
    }
    
    // 释放会话数组
    free(profiler->sessions);
    
    // 释放分析器本身
    free(profiler);
    
    printf("量子性能分析器已销毁\n");
}

/**
 * 开始性能分析会话
 */
bool quantum_profiler_start_session(QuantumProfiler* profiler, const char* session_name) {
    if (!profiler || !session_name) return false;
    
    // 检查是否已达到最大会话数
    if (profiler->session_count >= MAX_SESSIONS) {
        fprintf(stderr, "错误: 已达到最大会话数量 %d\n", MAX_SESSIONS);
        return false;
    }
    
    // 检查是否已有同名会话
    for (size_t i = 0; i < profiler->session_count; i++) {
        if (strcmp(profiler->sessions[i].name, session_name) == 0) {
            fprintf(stderr, "错误: 会话名称 '%s' 已存在\n", session_name);
            return false;
        }
    }
    
    // 创建新会话
    SessionInstance* session = &profiler->sessions[profiler->session_count];
    strncpy(session->name, session_name, MAX_SESSION_NAME - 1);
    session->name[MAX_SESSION_NAME - 1] = '\0';
    
    // 初始化会话数据
    memset(&session->data, 0, sizeof(ProfileSession));
    session->data.level = profiler->level;
    
    // 分配标记数组
    session->mark_capacity = (profiler->level >= PROFILE_LEVEL_DETAILED) ? MAX_MARKS : 10;
    session->marks = (PerformanceMark*)malloc(session->mark_capacity * sizeof(PerformanceMark));
    if (!session->marks) {
        fprintf(stderr, "错误: 无法为性能标记分配内存\n");
        return false;
    }
    session->mark_count = 0;
    
    // 分配指标数组
    session->metrics = (Metric*)malloc(MAX_METRICS * sizeof(Metric));
    if (!session->metrics) {
        fprintf(stderr, "错误: 无法为性能指标分配内存\n");
        free(session->marks);
        return false;
    }
    session->metric_count = 0;
    
    // 记录开始时间
    get_current_time(&session->data.start_time);
    
    // 设置会话为活跃状态
    session->active = true;
    profiler->active_session = profiler->session_count;
    profiler->session_count++;
    profiler->is_collecting = true;
    
    printf("性能分析会话 '%s' 已开始\n", session_name);
    return true;
}

/**
 * 结束性能分析会话
 */
bool quantum_profiler_end_session(QuantumProfiler* profiler) {
    if (!profiler || profiler->active_session >= profiler->session_count) return false;
    
    SessionInstance* session = &profiler->sessions[profiler->active_session];
    
    // 记录结束时间
    get_current_time(&session->data.end_time);
    
    // 计算持续时间
    session->data.total_duration_ms = calculate_time_diff_ms(
        &session->data.start_time, &session->data.end_time);
    
    // 计算平均门执行时间
    if (session->data.gate_counts.total_gates > 0) {
        session->data.avg_gate_time_ms = session->data.total_duration_ms / 
                                       session->data.gate_counts.total_gates;
    }
    
    // 设置会话为非活跃状态
    session->active = false;
    profiler->is_collecting = false;
    profiler->active_session = (size_t)-1;
    
    printf("性能分析会话 '%s' 已结束，总时间: %.2f ms\n", 
           session->name, session->data.total_duration_ms);
    return true;
}

/**
 * 添加性能标记
 */
bool quantum_profiler_mark(QuantumProfiler* profiler, MarkType type, const char* label) {
    if (!profiler || !label || !profiler->is_collecting || 
        profiler->active_session >= profiler->session_count) {
        return false;
    }
    
    // 如果分析级别不够，则忽略详细标记
    if (profiler->level < PROFILE_LEVEL_DETAILED && 
        type != MARK_CIRCUIT_START && type != MARK_CIRCUIT_END) {
        return true;  // 成功但不执行任何操作
    }
    
    SessionInstance* session = &profiler->sessions[profiler->active_session];
    
    // 检查是否已达到标记容量上限
    if (session->mark_count >= session->mark_capacity) {
        size_t new_capacity = session->mark_capacity * 2;
        PerformanceMark* new_marks = (PerformanceMark*)realloc(
            session->marks, new_capacity * sizeof(PerformanceMark));
        
        if (!new_marks) {
            fprintf(stderr, "错误: 无法扩展性能标记数组\n");
            return false;
        }
        
        session->marks = new_marks;
        session->mark_capacity = new_capacity;
    }
    
    // 创建新标记
    PerformanceMark* mark = &session->marks[session->mark_count];
    mark->type = type;
    mark->label = strdup(label);  // 注意：这里需要在销毁时释放
    get_current_time(&mark->time);
    mark->memory_usage = 0;  // TODO: 添加内存使用量检测
    mark->gate_type = -1;
    mark->qubit_count = 0;
    mark->value = 0.0;
    mark->custom_data = NULL;
    
    session->mark_count++;
    
    return true;
}

/**
 * 添加门操作标记
 */
bool quantum_profiler_mark_gate(QuantumProfiler* profiler, int gate_type, 
                              const int* qubit_indices, int qubit_count) {
    if (!profiler || !profiler->is_collecting || 
        profiler->active_session >= profiler->session_count) {
        return false;
    }
    
    // 如果分析级别不足，只更新计数器
    SessionInstance* session = &profiler->sessions[profiler->active_session];
    
    // 更新门计数
    session->data.gate_counts.total_gates++;
    
    // 根据门类型更新特定计数器
    switch (gate_type) {
        case 0:  // H门
            session->data.gate_counts.h_gates++;
            break;
        case 1:  // X门
            session->data.gate_counts.x_gates++;
            break;
        case 2:  // Y门
            session->data.gate_counts.y_gates++;
            break;
        case 3:  // Z门
            session->data.gate_counts.z_gates++;
            break;
        case 4:  // CNOT门
            session->data.gate_counts.cnot_gates++;
            break;
        case 5:  // SWAP门
            session->data.gate_counts.swap_gates++;
            break;
        // ... 其他门类型
        default:
            session->data.gate_counts.custom_gates++;
            break;
    }
    
    // 如果分析级别足够高，则添加详细标记
    if (profiler->level >= PROFILE_LEVEL_DETAILED) {
        char label[128];
        snprintf(label, sizeof(label), "Gate_%d_q", gate_type);
        
        // 添加量子比特索引
        char temp[16];
        for (int i = 0; i < qubit_count && i < 5; i++) {
            snprintf(temp, sizeof(temp), "%d", qubit_indices[i]);
            strcat(label, temp);
            if (i < qubit_count - 1) strcat(label, "_");
        }
        
        // 添加标记
        if (quantum_profiler_mark(profiler, MARK_GATE_START, label)) {
            PerformanceMark* mark = &session->marks[session->mark_count - 1];
            mark->gate_type = gate_type;
            mark->qubit_count = qubit_count;
            return true;
        }
        return false;
    }
    
    return true;
}

/**
 * 设置自定义指标
 */
bool quantum_profiler_set_metric(QuantumProfiler* profiler, MetricType metric_type, 
                               const char* metric_name, double value) {
    if (!profiler || !metric_name || !profiler->is_collecting || 
        profiler->active_session >= profiler->session_count) {
        return false;
    }
    
    SessionInstance* session = &profiler->sessions[profiler->active_session];
    
    // 检查是否已达到指标上限
    if (session->metric_count >= MAX_METRICS) {
        fprintf(stderr, "错误: 已达到最大指标数量 %d\n", MAX_METRICS);
        return false;
    }
    
    // 检查是否已有同名指标，如果有则更新值
    for (size_t i = 0; i < session->metric_count; i++) {
        if (strcmp(session->metrics[i].name, metric_name) == 0) {
            session->metrics[i].value = value;
            return true;
        }
    }
    
    // 创建新指标
    Metric* metric = &session->metrics[session->metric_count];
    metric->type = metric_type;
    strncpy(metric->name, metric_name, sizeof(metric->name) - 1);
    metric->name[sizeof(metric->name) - 1] = '\0';
    metric->value = value;
    
    session->metric_count++;
    
    // 更新会话数据中的相应字段
    switch (metric_type) {
        case METRIC_CIRCUIT_DEPTH:
            session->data.circuit_depth = value;
            break;
        case METRIC_ENTANGLEMENT:
            session->data.entanglement_degree = value;
            break;
        case METRIC_FIDELITY:
            session->data.fidelity = value;
            break;
        case METRIC_ERROR_RATE:
            session->data.error_rate = value;
            break;
        default:
            break;
    }
    
    return true;
}

/**
 * 获取当前会话
 */
bool quantum_profiler_get_session(QuantumProfiler* profiler, ProfileSession* session) {
    if (!profiler || !session || profiler->active_session >= profiler->session_count) {
        return false;
    }
    
    SessionInstance* instance = &profiler->sessions[profiler->active_session];
    *session = instance->data;
    
    return true;
}

/**
 * 生成性能报告
 */
bool quantum_profiler_generate_report(QuantumProfiler* profiler, const char* filename) {
    if (!profiler || !filename) return false;
    
    // 如果当前还有活跃的会话，先结束它
    if (profiler->is_collecting) {
        quantum_profiler_end_session(profiler);
    }
    
    // 打开文件
    FILE* file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "错误: 无法打开文件 %s\n", filename);
        return false;
    }
    
    // 写入报告头
    fprintf(file, "========================================\n");
    fprintf(file, "QEntL 量子性能分析报告\n");
    fprintf(file, "生成时间: %s", ctime(&(time_t){time(NULL)}));
    fprintf(file, "分析级别: %d\n", profiler->level);
    fprintf(file, "会话数量: %zu\n", profiler->session_count);
    fprintf(file, "========================================\n\n");
    
    // 写入每个会话的数据
    for (size_t i = 0; i < profiler->session_count; i++) {
        SessionInstance* session = &profiler->sessions[i];
        
        fprintf(file, "会话: %s\n", session->name);
        fprintf(file, "----------------------------------------\n");
        fprintf(file, "总执行时间: %.2f ms\n", session->data.total_duration_ms);
        fprintf(file, "门操作统计:\n");
        fprintf(file, "  总门数: %llu\n", (unsigned long long)session->data.gate_counts.total_gates);
        fprintf(file, "  H门: %llu\n", (unsigned long long)session->data.gate_counts.h_gates);
        fprintf(file, "  X门: %llu\n", (unsigned long long)session->data.gate_counts.x_gates);
        fprintf(file, "  Y门: %llu\n", (unsigned long long)session->data.gate_counts.y_gates);
        fprintf(file, "  Z门: %llu\n", (unsigned long long)session->data.gate_counts.z_gates);
        fprintf(file, "  CNOT门: %llu\n", (unsigned long long)session->data.gate_counts.cnot_gates);
        fprintf(file, "  SWAP门: %llu\n", (unsigned long long)session->data.gate_counts.swap_gates);
        fprintf(file, "  测量操作: %llu\n", (unsigned long long)session->data.gate_counts.measurements);
        
        if (profiler->level >= PROFILE_LEVEL_STANDARD) {
            fprintf(file, "电路深度: %.2f\n", session->data.circuit_depth);
            fprintf(file, "平均门时间: %.4f ms\n", session->data.avg_gate_time_ms);
        }
        
        if (profiler->level >= PROFILE_LEVEL_QUANTUM) {
            fprintf(file, "纠缠度: %.4f\n", session->data.entanglement_degree);
            fprintf(file, "保真度: %.4f\n", session->data.fidelity);
            fprintf(file, "错误率: %.6f\n", session->data.error_rate);
        }
        
        // 写入自定义指标
        if (session->metric_count > 0) {
            fprintf(file, "\n自定义指标:\n");
            for (size_t j = 0; j < session->metric_count; j++) {
                fprintf(file, "  %s: %.6f\n", session->metrics[j].name, session->metrics[j].value);
            }
        }
        
        // 如果是详细级别，写入所有标记
        if (profiler->level >= PROFILE_LEVEL_DETAILED && session->mark_count > 0) {
            fprintf(file, "\n标记时间线:\n");
            struct timespec* base_time = &session->data.start_time;
            
            for (size_t j = 0; j < session->mark_count; j++) {
                PerformanceMark* mark = &session->marks[j];
                double time_ms = calculate_time_diff_ms(base_time, &mark->time);
                
                fprintf(file, "  [%.4f ms] %s: %s", time_ms, 
                        mark->type == MARK_CIRCUIT_START ? "开始" :
                        mark->type == MARK_CIRCUIT_END ? "结束" :
                        mark->type == MARK_GATE_START ? "门开始" :
                        mark->type == MARK_GATE_END ? "门结束" :
                        mark->type == MARK_MEASUREMENT ? "测量" :
                        mark->type == MARK_ENTANGLEMENT ? "纠缠" :
                        mark->type == MARK_MEMORY_ALLOCATE ? "内存分配" :
                        mark->type == MARK_MEMORY_FREE ? "内存释放" : "自定义",
                        mark->label);
                
                if (mark->gate_type >= 0) {
                    fprintf(file, " (门类型: %d, 量子比特数: %d)", 
                            mark->gate_type, mark->qubit_count);
                }
                
                fprintf(file, "\n");
            }
        }
        
        fprintf(file, "\n");
    }
    
    fclose(file);
    printf("性能报告已生成: %s\n", filename);
    return true;
}

/**
 * 打印性能摘要
 */
void quantum_profiler_print_summary(QuantumProfiler* profiler) {
    if (!profiler) return;
    
    printf("\n========== 量子性能分析摘要 ==========\n");
    printf("分析级别: %s\n", 
           profiler->level == PROFILE_LEVEL_BASIC ? "基本" :
           profiler->level == PROFILE_LEVEL_STANDARD ? "标准" :
           profiler->level == PROFILE_LEVEL_DETAILED ? "详细" : "量子");
    
    for (size_t i = 0; i < profiler->session_count; i++) {
        SessionInstance* session = &profiler->sessions[i];
        
        printf("\n会话: %s\n", session->name);
        printf("  总时间: %.2f ms\n", session->data.total_duration_ms);
        printf("  总门数: %llu\n", (unsigned long long)session->data.gate_counts.total_gates);
        
        if (profiler->level >= PROFILE_LEVEL_STANDARD) {
            printf("  电路深度: %.2f\n", session->data.circuit_depth);
            printf("  平均门时间: %.4f ms\n", session->data.avg_gate_time_ms);
        }
        
        if (profiler->level >= PROFILE_LEVEL_QUANTUM) {
            printf("  保真度: %.4f\n", session->data.fidelity);
            printf("  错误率: %.6f\n", session->data.error_rate);
        }
    }
    
    printf("========================================\n");
}

/**
 * 比较两个会话的性能差异
 */
bool quantum_profiler_compare_sessions(QuantumProfiler* profiler,
                                     const char* session1_name,
                                     const char* session2_name,
                                     const char* output_file) {
    // 功能实现将在未来版本中添加
    printf("会话比较功能将在未来版本中提供\n");
    return false;
}

/**
 * 运行性能分析器测试
 */
bool quantum_profiler_run_test(void) {
    printf("开始量子性能分析器测试...\n");
    
    // 创建性能分析器
    QuantumProfiler* profiler = quantum_profiler_create(PROFILE_LEVEL_DETAILED);
    if (!profiler) {
        fprintf(stderr, "错误: 无法创建性能分析器\n");
        return false;
    }
    
    // 开始会话
    if (!quantum_profiler_start_session(profiler, "TestSession")) {
        quantum_profiler_destroy(profiler);
        return false;
    }
    
    // 添加电路开始标记
    quantum_profiler_mark(profiler, MARK_CIRCUIT_START, "TestCircuit");
    
    // 模拟一些门操作
    int qubits1[] = {0};
    int qubits2[] = {0, 1};
    
    for (int i = 0; i < 100; i++) {
        // H门
        quantum_profiler_mark_gate(profiler, 0, qubits1, 1);
        
        // 模拟执行时间
        struct timespec sleep_time = {0, 1000000}; // 1ms
        nanosleep(&sleep_time, NULL);
        
        // CNOT门
        quantum_profiler_mark_gate(profiler, 4, qubits2, 2);
        
        // 模拟执行时间
        nanosleep(&sleep_time, NULL);
    }
    
    // 设置一些指标
    quantum_profiler_set_metric(profiler, METRIC_CIRCUIT_DEPTH, "CircuitDepth", 42.0);
    quantum_profiler_set_metric(profiler, METRIC_ENTANGLEMENT, "MaxEntanglement", 0.95);
    quantum_profiler_set_metric(profiler, METRIC_FIDELITY, "SimulatedFidelity", 0.9987);
    quantum_profiler_set_metric(profiler, METRIC_ERROR_RATE, "EstimatedError", 0.0013);
    
    // 添加电路结束标记
    quantum_profiler_mark(profiler, MARK_CIRCUIT_END, "TestCircuit");
    
    // 结束会话
    quantum_profiler_end_session(profiler);
    
    // 生成报告
    quantum_profiler_generate_report(profiler, "quantum_profiler_test_report.txt");
    
    // 打印摘要
    quantum_profiler_print_summary(profiler);
    
    // 销毁分析器
    quantum_profiler_destroy(profiler);
    
    printf("量子性能分析器测试完成\n");
    return true;
} 