/**
 * QEntL量子执行引擎实现
 * 
 * 量子基因编码: QG-RUNTIME-QEXEC-SRC-H5K2-1713051300
 * 
 * @文件: quantum_executor.c
 * @描述: 实现QEntL运行时的量子指令执行引擎功能
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-18
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块实现量子指令集的执行引擎
 * - 支持单/多量子比特门操作、测量、重置等基本操作
 * - 支持量子指令流水线和并行执行
 */

#include "quantum_executor.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <complex.h>

/**
 * 量子执行器内部结构
 */
struct QuantumExecutor {
    StateManager* state_manager;        /* 状态管理器 */
    EventSystem* event_system;          /* 事件系统 */
    EventHandler* event_handler;        /* 事件处理器 */
    
    ExecutionMode mode;                 /* 执行模式 */
    OptimizationLevel optimization;     /* 优化级别 */
    
    ExecutionStats stats;               /* 执行统计 */
    
    int is_running;                     /* 是否正在运行 */
    int max_threads;                    /* 最大线程数 */
    
    /* 执行时缓存和计算数据 */
    void* execution_cache;             /* 执行缓存 */
};

/**
 * 自定义门回调函数类型
 */
typedef int (*CustomGateFunction)(QuantumGate* gate, QState* state, void* user_data);

/**
 * 自定义门数据结构
 */
typedef struct CustomGateData {
    CustomGateFunction function;    /* 自定义门函数 */
    void* user_data;                /* 用户数据 */
    char* name;                     /* 门名称 */
} CustomGateData;

/* 前向声明内部函数 */
static int apply_single_qubit_gate(QuantumExecutor* executor, QuantumGate* gate, QState* state);
static int apply_two_qubit_gate(QuantumExecutor* executor, QuantumGate* gate, QState* state);
static int apply_multi_qubit_gate(QuantumExecutor* executor, QuantumGate* gate, QState* state);
static int apply_custom_gate(QuantumExecutor* executor, QuantumGate* gate, QState* state);
static int handle_measurement(QuantumExecutor* executor, QuantumGate* gate, QState* state);
static void update_stats(QuantumExecutor* executor, QuantumGate* gate, double duration);
static void on_quantum_event(QEntLEvent* event, QuantumExecutor* executor);
static double calculate_circuit_depth(QuantumCircuit* circuit);

/**
 * 创建量子执行器
 */
QuantumExecutor* quantum_executor_create(StateManager* state_manager, EventSystem* event_system) {
    if (!state_manager || !event_system) {
        fprintf(stderr, "错误: 创建量子执行器需要有效的状态管理器和事件系统\n");
        return NULL;
    }
    
    QuantumExecutor* executor = (QuantumExecutor*)malloc(sizeof(QuantumExecutor));
    if (!executor) {
        fprintf(stderr, "错误: 无法分配量子执行器内存\n");
        return NULL;
    }
    
    /* 初始化基本字段 */
    executor->state_manager = state_manager;
    executor->event_system = event_system;
    executor->mode = EXEC_MODE_SEQUENTIAL;
    executor->optimization = OPT_LEVEL_NONE;
    executor->is_running = 0;
    executor->max_threads = 4;  /* 默认最大线程数 */
    executor->execution_cache = NULL;
    
    /* 初始化统计信息 */
    memset(&executor->stats, 0, sizeof(ExecutionStats));
    
    /* 注册事件处理器 */
    executor->event_handler = event_system_add_handler(
        event_system,
        (EventHandlerFunc)on_quantum_event,
        executor,
        30, /* 优先级 */
        (1 << EVENT_QUANTUM_OPERATION) | (1 << EVENT_STATE_CHANGED)
    );
    
    printf("量子执行引擎已创建\n");
    
    return executor;
}

/**
 * 销毁量子执行器
 */
void quantum_executor_destroy(QuantumExecutor* executor) {
    if (!executor) return;
    
    /* 移除事件处理器 */
    if (executor->event_system && executor->event_handler) {
        event_system_remove_handler(executor->event_system, executor->event_handler);
    }
    
    /* 释放执行缓存 */
    if (executor->execution_cache) {
        free(executor->execution_cache);
    }
    
    /* 释放执行器本身 */
    free(executor);
    
    printf("量子执行引擎已销毁\n");
}

/**
 * 设置执行模式
 */
int quantum_executor_set_mode(QuantumExecutor* executor, ExecutionMode mode) {
    if (!executor) return 0;
    
    executor->mode = mode;
    return 1;
}

/**
 * 设置优化级别
 */
int quantum_executor_set_optimization(QuantumExecutor* executor, OptimizationLevel level) {
    if (!executor) return 0;
    
    executor->optimization = level;
    return 1;
}

/**
 * 获取执行统计信息
 */
ExecutionStats quantum_executor_get_stats(QuantumExecutor* executor) {
    ExecutionStats empty_stats = {0};
    
    if (!executor) return empty_stats;
    
    return executor->stats;
}

/**
 * 重置执行统计信息
 */
void quantum_executor_reset_stats(QuantumExecutor* executor) {
    if (!executor) return;
    
    memset(&executor->stats, 0, sizeof(ExecutionStats));
}

/**
 * 创建新的量子电路
 */
QuantumCircuit* quantum_circuit_create(int qubit_count, const char* name) {
    if (qubit_count <= 0) {
        fprintf(stderr, "错误: 量子比特数量必须大于0\n");
        return NULL;
    }
    
    QuantumCircuit* circuit = (QuantumCircuit*)malloc(sizeof(QuantumCircuit));
    if (!circuit) {
        fprintf(stderr, "错误: 无法分配量子电路内存\n");
        return NULL;
    }
    
    /* 初始化门数组 */
    circuit->gate_capacity = 16;  /* 初始容量 */
    circuit->gates = (QuantumGate**)malloc(circuit->gate_capacity * sizeof(QuantumGate*));
    if (!circuit->gates) {
        free(circuit);
        fprintf(stderr, "错误: 无法分配门数组内存\n");
        return NULL;
    }
    circuit->gate_count = 0;
    
    /* 设置电路属性 */
    circuit->qubit_count = qubit_count;
    circuit->depth = 0.0;
    
    /* 复制电路名称 */
    if (name) {
        circuit->name = strdup(name);
    } else {
        circuit->name = strdup("unnamed_circuit");
    }
    
    if (!circuit->name) {
        free(circuit->gates);
        free(circuit);
        fprintf(stderr, "错误: 无法复制电路名称\n");
        return NULL;
    }
    
    return circuit;
}

/**
 * 销毁量子电路
 */
void quantum_circuit_destroy(QuantumCircuit* circuit) {
    if (!circuit) return;
    
    /* 释放所有门 */
    for (int i = 0; i < circuit->gate_count; i++) {
        quantum_gate_destroy(circuit->gates[i]);
    }
    
    /* 释放门数组 */
    free(circuit->gates);
    
    /* 释放电路名称 */
    free(circuit->name);
    
    /* 释放电路本身 */
    free(circuit);
}

/**
 * 添加门到量子电路
 */
int quantum_circuit_add_gate(QuantumCircuit* circuit, QuantumGate* gate) {
    if (!circuit || !gate) return 0;
    
    /* 检查量子位是否在有效范围内 */
    for (int i = 0; i < gate->qubit_count; i++) {
        if (gate->qubits[i] < 0 || gate->qubits[i] >= circuit->qubit_count) {
            fprintf(stderr, "错误: 量子位索引超出范围: %d (应在0到%d之间)\n", 
                   gate->qubits[i], circuit->qubit_count - 1);
            return 0;
        }
    }
    
    /* 检查是否需要扩展门数组 */
    if (circuit->gate_count >= circuit->gate_capacity) {
        int new_capacity = circuit->gate_capacity * 2;
        QuantumGate** new_gates = (QuantumGate**)realloc(
            circuit->gates, 
            new_capacity * sizeof(QuantumGate*));
        
        if (!new_gates) {
            fprintf(stderr, "错误: 无法扩展门数组\n");
            return 0;
        }
        
        circuit->gates = new_gates;
        circuit->gate_capacity = new_capacity;
    }
    
    /* 添加门 */
    circuit->gates[circuit->gate_count++] = gate;
    
    /* 更新电路深度 */
    circuit->depth = calculate_circuit_depth(circuit);
    
    return 1;
}

/**
 * 创建量子门
 */
QuantumGate* quantum_gate_create(QuantumGateType type, 
                               int* qubits, 
                               int qubit_count, 
                               double* parameters, 
                               int parameter_count) {
    if (qubit_count <= 0 || !qubits) {
        fprintf(stderr, "错误: 无效的量子位数组\n");
        return NULL;
    }
    
    /* 验证门类型与量子位数量的兼容性 */
    if ((type <= GATE_RZ && qubit_count != 1) ||
        (type >= GATE_CNOT && type <= GATE_CRZ && qubit_count != 2) ||
        (type >= GATE_TOFFOLI && type <= GATE_FREDKIN && qubit_count != 3)) {
        fprintf(stderr, "错误: 门类型 %d 与量子位数量 %d 不兼容\n", type, qubit_count);
        return NULL;
    }
    
    QuantumGate* gate = (QuantumGate*)malloc(sizeof(QuantumGate));
    if (!gate) {
        fprintf(stderr, "错误: 无法分配量子门内存\n");
        return NULL;
    }
    
    /* 初始化门 */
    gate->type = type;
    gate->qubit_count = qubit_count;
    gate->custom_data = NULL;
    
    /* 复制量子位数组 */
    gate->qubits = (int*)malloc(qubit_count * sizeof(int));
    if (!gate->qubits) {
        free(gate);
        fprintf(stderr, "错误: 无法分配量子位数组内存\n");
        return NULL;
    }
    memcpy(gate->qubits, qubits, qubit_count * sizeof(int));
    
    /* 处理参数 */
    if (parameter_count > 0 && parameters) {
        gate->parameter_count = parameter_count;
        gate->parameters = (double*)malloc(parameter_count * sizeof(double));
        if (!gate->parameters) {
            free(gate->qubits);
            free(gate);
            fprintf(stderr, "错误: 无法分配参数数组内存\n");
            return NULL;
        }
        memcpy(gate->parameters, parameters, parameter_count * sizeof(double));
    } else {
        gate->parameter_count = 0;
        gate->parameters = NULL;
    }
    
    return gate;
}

/**
 * 创建自定义量子门
 */
QuantumGate* quantum_gate_create_custom(int* qubits, 
                                      int qubit_count, 
                                      void* custom_data) {
    if (qubit_count <= 0 || !qubits || !custom_data) {
        fprintf(stderr, "错误: 创建自定义门需要有效的量子位数组和自定义数据\n");
        return NULL;
    }
    
    QuantumGate* gate = (QuantumGate*)malloc(sizeof(QuantumGate));
    if (!gate) {
        fprintf(stderr, "错误: 无法分配量子门内存\n");
        return NULL;
    }
    
    /* 初始化门 */
    gate->type = GATE_CUSTOM;
    gate->qubit_count = qubit_count;
    gate->parameter_count = 0;
    gate->parameters = NULL;
    gate->custom_data = custom_data;
    
    /* 复制量子位数组 */
    gate->qubits = (int*)malloc(qubit_count * sizeof(int));
    if (!gate->qubits) {
        free(gate);
        fprintf(stderr, "错误: 无法分配量子位数组内存\n");
        return NULL;
    }
    memcpy(gate->qubits, qubits, qubit_count * sizeof(int));
    
    return gate;
}

/**
 * 销毁量子门
 */
void quantum_gate_destroy(QuantumGate* gate) {
    if (!gate) return;
    
    /* 释放量子位数组 */
    if (gate->qubits) {
        free(gate->qubits);
    }
    
    /* 释放参数数组 */
    if (gate->parameters) {
        free(gate->parameters);
    }
    
    /* 释放自定义门数据 */
    if (gate->type == GATE_CUSTOM && gate->custom_data) {
        CustomGateData* custom_data = (CustomGateData*)gate->custom_data;
        if (custom_data->name) {
            free(custom_data->name);
        }
        free(custom_data);
    }
    
    /* 释放门本身 */
    free(gate);
}

/**
 * 执行单个量子门
 */
int quantum_executor_apply_gate(QuantumExecutor* executor, QuantumGate* gate, QState* state) {
    if (!executor || !gate || !state) return 0;
    
    clock_t start_time = clock();
    int result = 0;
    
    /* 根据门类型选择应用方法 */
    switch (gate->type) {
        /* 单比特门 */
        case GATE_IDENTITY:
        case GATE_X:
        case GATE_Y:
        case GATE_Z:
        case GATE_H:
        case GATE_S:
        case GATE_T:
        case GATE_RX:
        case GATE_RY:
        case GATE_RZ:
            result = apply_single_qubit_gate(executor, gate, state);
            break;
            
        /* 双比特门 */
        case GATE_CNOT:
        case GATE_CZ:
        case GATE_SWAP:
        case GATE_CRX:
        case GATE_CRY:
        case GATE_CRZ:
            result = apply_two_qubit_gate(executor, gate, state);
            break;
            
        /* 三比特及以上门 */
        case GATE_TOFFOLI:
        case GATE_FREDKIN:
            result = apply_multi_qubit_gate(executor, gate, state);
            break;
            
        /* 测量操作 */
        case GATE_MEASURE:
            result = handle_measurement(executor, gate, state);
            break;
            
        /* 自定义门 */
        case GATE_CUSTOM:
            result = apply_custom_gate(executor, gate, state);
            break;
            
        default:
            fprintf(stderr, "错误: 未知门类型 %d\n", gate->type);
            return 0;
    }
    
    /* 计算执行时间并更新统计 */
    clock_t end_time = clock();
    double duration = (double)(end_time - start_time) / CLOCKS_PER_SEC * 1000.0; /* 毫秒 */
    update_stats(executor, gate, duration);
    
    /* 触发操作事件 */
    QEntLEvent* event = event_create(EVENT_QUANTUM_OPERATION);
    if (event) {
        /* TODO: 设置事件数据 */
        event_system_emit(executor->event_system, event);
    }
    
    return result;
}

/**
 * 执行量子电路
 */
int quantum_executor_run_circuit(QuantumExecutor* executor, QuantumCircuit* circuit, QState* state) {
    if (!executor || !circuit || !state) return 0;
    
    printf("执行量子电路 '%s' (%d个量子位, %d个门, 深度%.2f)\n", 
           circuit->name, circuit->qubit_count, circuit->gate_count, circuit->depth);
    
    /* 检查状态是否与电路兼容 */
    if (state_manager_get_qubit_count(executor->state_manager, state) < circuit->qubit_count) {
        fprintf(stderr, "错误: 状态只有%d个量子位，但电路需要%d个\n", 
               state_manager_get_qubit_count(executor->state_manager, state), 
               circuit->qubit_count);
        return 0;
    }
    
    /* 标记执行开始 */
    executor->is_running = 1;
    clock_t circuit_start = clock();
    
    /* 根据执行模式选择执行策略 */
    int success = 1;
    
    switch (executor->mode) {
        case EXEC_MODE_SEQUENTIAL:
            /* 顺序执行每个门 */
            for (int i = 0; i < circuit->gate_count; i++) {
                if (!quantum_executor_apply_gate(executor, circuit->gates[i], state)) {
                    fprintf(stderr, "错误: 执行第%d个门失败\n", i + 1);
                    success = 0;
                    break;
                }
            }
            break;
            
        case EXEC_MODE_PIPELINED:
            /* TODO: 实现流水线执行逻辑 */
            fprintf(stderr, "警告: 流水线执行模式尚未实现，使用顺序执行\n");
            for (int i = 0; i < circuit->gate_count; i++) {
                if (!quantum_executor_apply_gate(executor, circuit->gates[i], state)) {
                    fprintf(stderr, "错误: 执行第%d个门失败\n", i + 1);
                    success = 0;
                    break;
                }
            }
            break;
            
        case EXEC_MODE_PARALLEL:
            /* TODO: 实现并行执行逻辑 */
            fprintf(stderr, "警告: 并行执行模式尚未实现，使用顺序执行\n");
            for (int i = 0; i < circuit->gate_count; i++) {
                if (!quantum_executor_apply_gate(executor, circuit->gates[i], state)) {
                    fprintf(stderr, "错误: 执行第%d个门失败\n", i + 1);
                    success = 0;
                    break;
                }
            }
            break;
            
        case EXEC_MODE_OPTIMIZED: {
            /* 优化后执行 */
            QuantumCircuit* optimized = quantum_executor_optimize_circuit(
                executor, circuit, executor->optimization);
            if (optimized) {
                printf("电路已优化: 原有%d个门，优化后%d个门\n", 
                       circuit->gate_count, optimized->gate_count);
                
                for (int i = 0; i < optimized->gate_count; i++) {
                    if (!quantum_executor_apply_gate(executor, optimized->gates[i], state)) {
                        fprintf(stderr, "错误: 执行优化后的第%d个门失败\n", i + 1);
                        success = 0;
                        break;
                    }
                }
                
                /* 释放优化后的电路 */
                quantum_circuit_destroy(optimized);
            } else {
                fprintf(stderr, "警告: 无法优化电路，使用原始电路\n");
                for (int i = 0; i < circuit->gate_count; i++) {
                    if (!quantum_executor_apply_gate(executor, circuit->gates[i], state)) {
                        fprintf(stderr, "错误: 执行第%d个门失败\n", i + 1);
                        success = 0;
                        break;
                    }
                }
            }
            break;
        }
    }
    
    /* 计算总执行时间 */
    clock_t circuit_end = clock();
    double total_time = (double)(circuit_end - circuit_start) / CLOCKS_PER_SEC * 1000.0; /* 毫秒 */
    
    /* 更新电路统计信息 */
    executor->stats.circuit_depth = circuit->depth;
    executor->stats.execution_time = total_time;
    
    /* 标记执行结束 */
    executor->is_running = 0;
    
    printf("电路执行%s，耗时%.2f毫秒\n", success ? "成功" : "失败", total_time);
    
    return success;
}

/**
 * 优化量子电路
 */
QuantumCircuit* quantum_executor_optimize_circuit(QuantumExecutor* executor, 
                                                QuantumCircuit* circuit, 
                                                OptimizationLevel level) {
    if (!executor || !circuit) return NULL;
    
    /* 创建新电路作为优化结果 */
    QuantumCircuit* optimized = quantum_circuit_create(circuit->qubit_count, circuit->name);
    if (!optimized) {
        fprintf(stderr, "错误: 无法创建优化后的电路\n");
        return NULL;
    }
    
    /* 根据优化级别选择优化策略 */
    switch (level) {
        case OPT_LEVEL_NONE:
            /* 不优化，直接复制 */
            for (int i = 0; i < circuit->gate_count; i++) {
                QuantumGate* original = circuit->gates[i];
                
                /* 复制门 */
                QuantumGate* copy = quantum_gate_create(
                    original->type, 
                    original->qubits, 
                    original->qubit_count, 
                    original->parameters, 
                    original->parameter_count);
                
                if (copy) {
                    quantum_circuit_add_gate(optimized, copy);
                } else {
                    fprintf(stderr, "错误: 无法复制门\n");
                    quantum_circuit_destroy(optimized);
                    return NULL;
                }
            }
            break;
            
        case OPT_LEVEL_LIGHT:
            /* TODO: 实现轻度优化 */
            fprintf(stderr, "警告: 轻度优化尚未实现，使用原始电路\n");
            for (int i = 0; i < circuit->gate_count; i++) {
                QuantumGate* original = circuit->gates[i];
                
                /* 复制门 */
                QuantumGate* copy = quantum_gate_create(
                    original->type, 
                    original->qubits, 
                    original->qubit_count, 
                    original->parameters, 
                    original->parameter_count);
                
                if (copy) {
                    quantum_circuit_add_gate(optimized, copy);
                } else {
                    fprintf(stderr, "错误: 无法复制门\n");
                    quantum_circuit_destroy(optimized);
                    return NULL;
                }
            }
            break;
            
        case OPT_LEVEL_MEDIUM:
            /* TODO: 实现中度优化 */
            fprintf(stderr, "警告: 中度优化尚未实现，使用原始电路\n");
            for (int i = 0; i < circuit->gate_count; i++) {
                QuantumGate* original = circuit->gates[i];
                
                /* 复制门 */
                QuantumGate* copy = quantum_gate_create(
                    original->type, 
                    original->qubits, 
                    original->qubit_count, 
                    original->parameters, 
                    original->parameter_count);
                
                if (copy) {
                    quantum_circuit_add_gate(optimized, copy);
                } else {
                    fprintf(stderr, "错误: 无法复制门\n");
                    quantum_circuit_destroy(optimized);
                    return NULL;
                }
            }
            break;
            
        case OPT_LEVEL_AGGRESSIVE:
            /* TODO: 实现激进优化 */
            fprintf(stderr, "警告: 激进优化尚未实现，使用原始电路\n");
            for (int i = 0; i < circuit->gate_count; i++) {
                QuantumGate* original = circuit->gates[i];
                
                /* 复制门 */
                QuantumGate* copy = quantum_gate_create(
                    original->type, 
                    original->qubits, 
                    original->qubit_count, 
                    original->parameters, 
                    original->parameter_count);
                
                if (copy) {
                    quantum_circuit_add_gate(optimized, copy);
                } else {
                    fprintf(stderr, "错误: 无法复制门\n");
                    quantum_circuit_destroy(optimized);
                    return NULL;
                }
            }
            break;
    }
    
    return optimized;
}

/**
 * 将量子电路转换为JSON字符串
 */
char* quantum_circuit_to_json(QuantumCircuit* circuit) {
    if (!circuit) return NULL;
    
    /* 估计JSON大小 - 这只是一个粗略估计 */
    size_t json_size = 1024;  /* 基础大小 */
    json_size += strlen(circuit->name) * 2;  /* 电路名称 */
    json_size += circuit->gate_count * 256;  /* 每个门的JSON表示 */
    
    /* 分配内存 */
    char* json = (char*)malloc(json_size);
    if (!json) {
        fprintf(stderr, "错误: 无法分配内存用于JSON序列化\n");
        return NULL;
    }
    
    /* 初始化JSON字符串 */
    int offset = 0;
    offset += snprintf(json + offset, json_size - offset, 
                      "{\n  \"name\": \"%s\",\n  \"qubit_count\": %d,\n  \"gate_count\": %d,\n  \"depth\": %.2f,\n  \"gates\": [\n", 
                      circuit->name, circuit->qubit_count, circuit->gate_count, circuit->depth);
    
    /* 添加每个门 */
    for (int i = 0; i < circuit->gate_count; i++) {
        QuantumGate* gate = circuit->gates[i];
        
        /* 开始门的JSON对象 */
        offset += snprintf(json + offset, json_size - offset, "    {\n      \"type\": \"%s\",\n      \"qubits\": [", 
                          get_gate_type_name(gate->type));
        
        /* 添加量子位 */
        for (int q = 0; q < gate->qubit_count; q++) {
            offset += snprintf(json + offset, json_size - offset, "%d%s", 
                              gate->qubits[q], (q < gate->qubit_count - 1) ? ", " : "");
        }
        
        offset += snprintf(json + offset, json_size - offset, "]");
        
        /* 添加参数（如果有） */
        if (gate->parameter_count > 0) {
            offset += snprintf(json + offset, json_size - offset, ",\n      \"params\": [");
            
            for (int p = 0; p < gate->parameter_count; p++) {
                offset += snprintf(json + offset, json_size - offset, "%.6f%s", 
                                  gate->parameters[p], (p < gate->parameter_count - 1) ? ", " : "");
            }
            
            offset += snprintf(json + offset, json_size - offset, "]");
        }
        
        /* 结束门的JSON对象 */
        offset += snprintf(json + offset, json_size - offset, "\n    }%s\n", 
                          (i < circuit->gate_count - 1) ? "," : "");
    }
    
    /* 完成JSON字符串 */
    offset += snprintf(json + offset, json_size - offset, "  ]\n}");
    
    return json;
}

/**
 * 从JSON字符串解析量子电路
 */
QuantumCircuit* quantum_circuit_from_json(const char* json) {
    /* 这个函数只是一个占位符，实际实现应该使用JSON解析库 */
    fprintf(stderr, "警告: quantum_circuit_from_json 尚未实现\n");
    return NULL;
}

/**
 * 获取门类型的名称
 */
const char* get_gate_type_name(GateType type) {
    switch (type) {
        case GATE_I: return "I";
        case GATE_X: return "X";
        case GATE_Y: return "Y";
        case GATE_Z: return "Z";
        case GATE_H: return "H";
        case GATE_S: return "S";
        case GATE_T: return "T";
        case GATE_RX: return "RX";
        case GATE_RY: return "RY";
        case GATE_RZ: return "RZ";
        case GATE_CNOT: return "CNOT";
        case GATE_CZ: return "CZ";
        case GATE_SWAP: return "SWAP";
        case GATE_TOFFOLI: return "TOFFOLI";
        case GATE_MEASURE: return "MEASURE";
        default: return "UNKNOWN";
    }
}

/**
 * 将量子电路保存到文件
 */
int quantum_circuit_save_to_file(QuantumCircuit* circuit, const char* filename) {
    if (!circuit || !filename) {
        fprintf(stderr, "错误: 无效的参数用于保存量子电路\n");
        return QENTL_ERROR_INVALID_PARAM;
    }
    
    /* 将电路转换为JSON */
    char* json = quantum_circuit_to_json(circuit);
    if (!json) {
        fprintf(stderr, "错误: 无法将量子电路转换为JSON\n");
        return QENTL_ERROR_SERIALIZATION;
    }
    
    /* 打开文件用于写入 */
    FILE* file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "错误: 无法打开文件用于写入: %s\n", filename);
        free(json);
        return QENTL_ERROR_FILE_OPERATION;
    }
    
    /* 写入JSON到文件 */
    size_t written = fwrite(json, 1, strlen(json), file);
    if (written != strlen(json)) {
        fprintf(stderr, "错误: 写入文件时出错: %s\n", filename);
        fclose(file);
        free(json);
        return QENTL_ERROR_FILE_OPERATION;
    }
    
    /* 关闭文件并释放资源 */
    fclose(file);
    free(json);
    
    printf("量子电路成功保存到文件: %s\n", filename);
    return QENTL_SUCCESS;
}

/**
 * 从文件加载量子电路
 */
QuantumCircuit* quantum_circuit_load_from_file(const char* filename) {
    if (!filename) {
        fprintf(stderr, "错误: 无效的文件名参数\n");
        return NULL;
    }
    
    /* 打开文件用于读取 */
    FILE* file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "错误: 无法打开文件用于读取: %s\n", filename);
        return NULL;
    }
    
    /* 获取文件大小 */
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    /* 分配内存用于文件内容 */
    char* json = (char*)malloc(file_size + 1);
    if (!json) {
        fprintf(stderr, "错误: 无法分配内存用于文件内容\n");
        fclose(file);
        return NULL;
    }
    
    /* 读取文件内容 */
    size_t read = fread(json, 1, file_size, file);
    if (read != file_size) {
        fprintf(stderr, "错误: 读取文件时出错: %s\n", filename);
        fclose(file);
        free(json);
        return NULL;
    }
    
    /* 添加字符串结束符 */
    json[file_size] = '\0';
    
    /* 关闭文件 */
    fclose(file);
    
    /* 从JSON解析量子电路 */
    QuantumCircuit* circuit = quantum_circuit_from_json(json);
    free(json);
    
    if (!circuit) {
        fprintf(stderr, "错误: 无法从文件解析量子电路: %s\n", filename);
        return NULL;
    }
    
    printf("量子电路成功从文件加载: %s\n", filename);
    return circuit;
}

/**
 * 创建测试量子电路
 */
QuantumCircuit* quantum_executor_create_test_circuit(int qubit_count) {
    /* 创建一个新的量子电路 */
    QuantumCircuit* circuit = quantum_circuit_create("测试电路", qubit_count);
    if (!circuit) {
        fprintf(stderr, "错误: 无法创建测试量子电路\n");
        return NULL;
    }
    
    /* 添加各种门来测试功能 */
    
    /* 添加H门到第一个量子位 */
    quantum_circuit_add_h(circuit, 0);
    
    /* 添加X门到第二个量子位 */
    if (qubit_count > 1) {
        quantum_circuit_add_x(circuit, 1);
    }
    
    /* 添加CNOT门 */
    if (qubit_count > 1) {
        quantum_circuit_add_cnot(circuit, 0, 1);
    }
    
    /* 添加RY旋转门 */
    if (qubit_count > 0) {
        quantum_circuit_add_ry(circuit, 0, M_PI / 4);
    }
    
    /* 添加CZ门 */
    if (qubit_count > 2) {
        quantum_circuit_add_cz(circuit, 1, 2);
    }
    
    /* 添加Toffoli门 */
    if (qubit_count > 2) {
        quantum_circuit_add_toffoli(circuit, 0, 1, 2);
    }
    
    /* 添加测量门 */
    for (int i = 0; i < qubit_count; i++) {
        quantum_circuit_add_measure(circuit, i, i);
    }
    
    /* 计算电路深度 */
    quantum_circuit_compute_depth(circuit);
    printf("测试电路已创建，包含 %d 个量子位，%d 个门，深度 %.2f\n", 
           circuit->qubit_count, circuit->gate_count, circuit->depth);
    
    return circuit;
}

/**
 * 运行量子执行器测试
 */
int quantum_executor_run_test(void) {
    printf("开始量子执行器测试...\n");
    
    /* 创建状态管理器 */
    StateManager* state_manager = state_manager_create();
    if (!state_manager) {
        fprintf(stderr, "错误: 无法创建状态管理器\n");
        return QENTL_ERROR_RUNTIME;
    }
    
    /* 创建事件系统 */
    EventSystem* event_system = event_system_create();
    if (!event_system) {
        fprintf(stderr, "错误: 无法创建事件系统\n");
        state_manager_destroy(state_manager);
        return QENTL_ERROR_RUNTIME;
    }
    
    /* 创建量子执行器 */
    QuantumExecutor* executor = quantum_executor_create(state_manager, event_system);
    if (!executor) {
        fprintf(stderr, "错误: 无法创建量子执行器\n");
        event_system_destroy(event_system);
        state_manager_destroy(state_manager);
        return QENTL_ERROR_RUNTIME;
    }
    
    /* 创建测试电路 */
    QuantumCircuit* circuit = quantum_executor_create_test_circuit(3);
    if (!circuit) {
        fprintf(stderr, "错误: 无法创建测试电路\n");
        quantum_executor_destroy(executor);
        event_system_destroy(event_system);
        state_manager_destroy(state_manager);
        return QENTL_ERROR_RUNTIME;
    }
    
    /* 执行电路 */
    printf("执行测试电路...\n");
    int result = quantum_executor_execute_circuit(executor, circuit);
    if (result != QENTL_SUCCESS) {
        fprintf(stderr, "错误: 执行测试电路失败，错误码: %d\n", result);
        quantum_circuit_destroy(circuit);
        quantum_executor_destroy(executor);
        event_system_destroy(event_system);
        state_manager_destroy(state_manager);
        return result;
    }
    
    /* 获取执行统计信息 */
    ExecutionStats stats = quantum_executor_get_stats(executor);
    printf("电路执行统计信息:\n");
    printf("  总门数: %d\n", stats.total_gates);
    printf("  执行时间: %.3f ms\n", stats.execution_time_ms);
    printf("  单门平均时间: %.3f us\n", stats.avg_gate_time_us);
    
    /* 保存电路到文件 */
    quantum_circuit_save_to_file(circuit, "test_circuit.json");
    
    /* 清理资源 */
    quantum_circuit_destroy(circuit);
    quantum_executor_destroy(executor);
    event_system_destroy(event_system);
    state_manager_destroy(state_manager);
    
    printf("量子执行器测试完成\n");
    return QENTL_SUCCESS;
}

/**
 * 内部函数：应用单比特门
 */
static int apply_single_qubit_gate(QuantumExecutor* executor, QuantumGate* gate, QState* state) {
    if (!executor || !gate || !state) return 0;
    if (gate->qubit_count != 1) return 0;
    
    int qubit = gate->qubits[0];
    
    /* 根据门类型应用不同的操作 */
    switch (gate->type) {
        case GATE_IDENTITY:
            /* 单位门不做任何操作 */
            return 1;
            
        case GATE_X:
            return state_manager_apply_x(executor->state_manager, state, qubit);
            
        case GATE_Y:
            return state_manager_apply_y(executor->state_manager, state, qubit);
            
        case GATE_Z:
            return state_manager_apply_z(executor->state_manager, state, qubit);
            
        case GATE_H:
            return state_manager_apply_h(executor->state_manager, state, qubit);
            
        case GATE_S:
            return state_manager_apply_s(executor->state_manager, state, qubit);
            
        case GATE_T:
            return state_manager_apply_t(executor->state_manager, state, qubit);
            
        case GATE_RX:
            if (gate->parameter_count < 1) {
                fprintf(stderr, "错误: RX门需要一个角度参数\n");
                return 0;
            }
            return state_manager_apply_rx(executor->state_manager, state, qubit, gate->parameters[0]);
            
        case GATE_RY:
            if (gate->parameter_count < 1) {
                fprintf(stderr, "错误: RY门需要一个角度参数\n");
                return 0;
            }
            return state_manager_apply_ry(executor->state_manager, state, qubit, gate->parameters[0]);
            
        case GATE_RZ:
            if (gate->parameter_count < 1) {
                fprintf(stderr, "错误: RZ门需要一个角度参数\n");
                return 0;
            }
            return state_manager_apply_rz(executor->state_manager, state, qubit, gate->parameters[0]);
            
        default:
            fprintf(stderr, "错误: 未知的单比特门类型 %d\n", gate->type);
            return 0;
    }
}

/**
 * 内部函数：应用双比特门
 */
static int apply_two_qubit_gate(QuantumExecutor* executor, QuantumGate* gate, QState* state) {
    if (!executor || !gate || !state) return 0;
    if (gate->qubit_count != 2) return 0;
    
    int control = gate->qubits[0];
    int target = gate->qubits[1];
    
    /* 根据门类型应用不同的操作 */
    switch (gate->type) {
        case GATE_CNOT:
            return state_manager_apply_cnot(executor->state_manager, state, control, target);
            
        case GATE_CZ:
            return state_manager_apply_cz(executor->state_manager, state, control, target);
            
        case GATE_SWAP:
            return state_manager_apply_swap(executor->state_manager, state, control, target);
            
        case GATE_CRX:
            if (gate->parameter_count < 1) {
                fprintf(stderr, "错误: CRX门需要一个角度参数\n");
                return 0;
            }
            return state_manager_apply_crx(executor->state_manager, state, control, target, gate->parameters[0]);
            
        case GATE_CRY:
            if (gate->parameter_count < 1) {
                fprintf(stderr, "错误: CRY门需要一个角度参数\n");
                return 0;
            }
            return state_manager_apply_cry(executor->state_manager, state, control, target, gate->parameters[0]);
            
        case GATE_CRZ:
            if (gate->parameter_count < 1) {
                fprintf(stderr, "错误: CRZ门需要一个角度参数\n");
                return 0;
            }
            return state_manager_apply_crz(executor->state_manager, state, control, target, gate->parameters[0]);
            
        default:
            fprintf(stderr, "错误: 未知的双比特门类型 %d\n", gate->type);
            return 0;
    }
}

/**
 * 内部函数：应用多比特门
 */
static int apply_multi_qubit_gate(QuantumExecutor* executor, QuantumGate* gate, QState* state) {
    if (!executor || !gate || !state) return 0;
    
    /* 检查门类型和量子位数量 */
    if (gate->type == GATE_TOFFOLI) {
        if (gate->qubit_count != 3) {
            fprintf(stderr, "错误: Toffoli门需要3个量子位\n");
            return 0;
        }
        
        int control1 = gate->qubits[0];
        int control2 = gate->qubits[1];
        int target = gate->qubits[2];
        
        return state_manager_apply_toffoli(executor->state_manager, state, control1, control2, target);
    }
    else if (gate->type == GATE_FREDKIN) {
        if (gate->qubit_count != 3) {
            fprintf(stderr, "错误: Fredkin门需要3个量子位\n");
            return 0;
        }
        
        int control = gate->qubits[0];
        int target1 = gate->qubits[1];
        int target2 = gate->qubits[2];
        
        return state_manager_apply_fredkin(executor->state_manager, state, control, target1, target2);
    }
    else {
        fprintf(stderr, "错误: 未知的多比特门类型 %d\n", gate->type);
        return 0;
    }
}

/**
 * 内部函数：应用自定义门
 */
static int apply_custom_gate(QuantumExecutor* executor, QuantumGate* gate, QState* state) {
    if (!executor || !gate || !state || !gate->custom_data) return 0;
    
    /* 从自定义数据中获取函数指针和用户数据 */
    CustomGateData* custom_data = (CustomGateData*)gate->custom_data;
    
    if (!custom_data->function) {
        fprintf(stderr, "错误: 自定义门没有有效的函数指针\n");
        return 0;
    }
    
    /* 调用自定义函数 */
    return custom_data->function(gate, state, custom_data->user_data);
}

/**
 * 内部函数：处理测量操作
 */
static int handle_measurement(QuantumExecutor* executor, QuantumGate* gate, QState* state) {
    if (!executor || !gate || !state) return 0;
    
    /* 测量所有指定的量子位 */
    int result = 1;
    for (int i = 0; i < gate->qubit_count; i++) {
        int qubit = gate->qubits[i];
        int measurement_result = 0;
        
        /* 执行测量 */
        if (!state_manager_measure_qubit(executor->state_manager, state, qubit, &measurement_result)) {
            fprintf(stderr, "错误: 测量量子位 %d 失败\n", qubit);
            result = 0;
        }
    }
    
    return result;
}

/**
 * 内部函数：更新统计信息
 */
static void update_stats(QuantumExecutor* executor, QuantumGate* gate, double duration) {
    if (!executor || !gate) return;
    
    /* 更新门计数 */
    executor->stats.total_gates++;
    
    /* 根据门类型更新统计 */
    if (gate->type <= GATE_RZ) {
        executor->stats.single_qubit_gates++;
    }
    else if (gate->type >= GATE_CNOT && gate->type <= GATE_CRZ) {
        executor->stats.two_qubit_gates++;
    }
    else if (gate->type >= GATE_TOFFOLI && gate->type <= GATE_FREDKIN) {
        executor->stats.multi_qubit_gates++;
    }
    else if (gate->type == GATE_MEASURE) {
        executor->stats.measurements++;
    }
    
    /* 累加执行时间 */
    executor->stats.execution_time += duration;
}

/**
 * 内部函数：计算电路深度
 */
static double calculate_circuit_depth(QuantumCircuit* circuit) {
    if (!circuit || circuit->gate_count == 0) return 0.0;
    
    /* 简化的深度计算，实际应考虑并行性 */
    int max_depth = 0;
    int* qubit_depths = (int*)calloc(circuit->qubit_count, sizeof(int));
    
    if (!qubit_depths) {
        fprintf(stderr, "错误: 无法分配量子位深度数组内存\n");
        return 1.0;  /* 默认最小深度 */
    }
    
    /* 计算每个量子位的深度 */
    for (int i = 0; i < circuit->gate_count; i++) {
        QuantumGate* gate = circuit->gates[i];
        int gate_depth = 0;
        
        /* 查找该门作用的所有量子位中最大的深度值 */
        for (int j = 0; j < gate->qubit_count; j++) {
            int qubit = gate->qubits[j];
            if (qubit_depths[qubit] > gate_depth) {
                gate_depth = qubit_depths[qubit];
            }
        }
        
        /* 该门的深度为最大深度值加1 */
        gate_depth++;
        
        /* 更新所有受影响的量子位的深度 */
        for (int j = 0; j < gate->qubit_count; j++) {
            int qubit = gate->qubits[j];
            qubit_depths[qubit] = gate_depth;
        }
        
        /* 更新电路最大深度 */
        if (gate_depth > max_depth) {
            max_depth = gate_depth;
        }
    }
    
    free(qubit_depths);
    return (double)max_depth;
}

/**
 * 内部函数：处理量子事件
 */
static void on_quantum_event(QEntLEvent* event, QuantumExecutor* executor) {
    if (!event || !executor) return;
    
    /* 根据事件类型处理 */
    switch (event->type) {
        case EVENT_QUANTUM_OPERATION:
            /* 可以记录操作统计等 */
            break;
            
        case EVENT_STATE_CHANGED:
            /* 可以记录状态变化等 */
            break;
            
        default:
            /* 忽略其他事件 */
            break;
    }
} 