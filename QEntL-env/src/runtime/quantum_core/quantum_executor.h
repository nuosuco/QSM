/**
 * QEntL量子执行引擎头文件
 * 
 * 量子基因编码: QG-RUNTIME-QEXEC-HDR-H5J9-1713051300
 * 
 * @文件: quantum_executor.h
 * @描述: 定义QEntL运行时的量子指令执行引擎核心API
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-18
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块实现量子指令集的执行引擎
 * - 支持单/多量子比特门操作、测量、重置等基本操作
 * - 支持量子指令流水线和并行执行
 */

#ifndef QENTL_QUANTUM_EXECUTOR_H
#define QENTL_QUANTUM_EXECUTOR_H

#include "../state_manager.h"
#include "../event_system.h"
#include <stdio.h>
#include <stdlib.h>

/**
 * 前向声明
 */
typedef struct QuantumExecutor QuantumExecutor;
typedef struct QuantumCircuit QuantumCircuit;
typedef struct QuantumGate QuantumGate;
typedef struct ExecutionStats ExecutionStats;

/**
 * 量子门类型枚举
 */
typedef enum {
    /* 单比特门 */
    GATE_IDENTITY,  /* 单位门 I */
    GATE_X,         /* 泡利-X门 (NOT) */
    GATE_Y,         /* 泡利-Y门 */
    GATE_Z,         /* 泡利-Z门 */
    GATE_H,         /* 阿达马门 */
    GATE_S,         /* S门 (相位门) */
    GATE_T,         /* T门 (π/8门) */
    GATE_RX,        /* 绕X轴旋转门 */
    GATE_RY,        /* 绕Y轴旋转门 */
    GATE_RZ,        /* 绕Z轴旋转门 */
    
    /* 双比特门 */
    GATE_CNOT,      /* 受控非门 */
    GATE_CZ,        /* 受控Z门 */
    GATE_SWAP,      /* 交换门 */
    GATE_CRX,       /* 受控RX门 */
    GATE_CRY,       /* 受控RY门 */
    GATE_CRZ,       /* 受控RZ门 */
    
    /* 三比特门 */
    GATE_TOFFOLI,   /* 托福利门 (CCNOT) */
    GATE_FREDKIN,   /* 弗雷德金门 (CSWAP) */
    
    /* 测量操作 */
    GATE_MEASURE,   /* 量子测量 */
    
    /* 自定义门 */
    GATE_CUSTOM     /* 自定义量子门 */
} QuantumGateType;

/**
 * 执行模式枚举
 */
typedef enum {
    EXEC_MODE_SEQUENTIAL,  /* 顺序执行 */
    EXEC_MODE_PIPELINED,   /* 流水线执行 */
    EXEC_MODE_PARALLEL,    /* 并行执行 */
    EXEC_MODE_OPTIMIZED    /* 优化执行 */
} ExecutionMode;

/**
 * 优化级别枚举
 */
typedef enum {
    OPT_LEVEL_NONE,        /* 不优化 */
    OPT_LEVEL_LIGHT,       /* 轻度优化 */
    OPT_LEVEL_MEDIUM,      /* 中度优化 */
    OPT_LEVEL_AGGRESSIVE   /* 激进优化 */
} OptimizationLevel;

/**
 * 执行统计结构
 */
typedef struct ExecutionStats {
    int total_gates;           /* 执行的总门数 */
    int single_qubit_gates;    /* 单比特门数量 */
    int two_qubit_gates;       /* 双比特门数量 */
    int multi_qubit_gates;     /* 多比特门数量 */
    int measurements;          /* 测量操作数量 */
    double circuit_depth;      /* 电路深度 */
    double execution_time;     /* 执行时间(ms) */
    int errors;                /* 错误数量 */
    double fidelity;           /* 保真度估计 */
} ExecutionStats;

/**
 * 量子门结构
 */
typedef struct QuantumGate {
    QuantumGateType type;      /* 门类型 */
    int* qubits;               /* 作用的量子位数组 */
    int qubit_count;           /* 量子位数量 */
    double* parameters;        /* 参数数组(用于旋转门等) */
    int parameter_count;       /* 参数数量 */
    void* custom_data;         /* 自定义门数据 */
} QuantumGate;

/**
 * 量子电路结构
 */
typedef struct QuantumCircuit {
    QuantumGate** gates;       /* 门数组 */
    int gate_count;            /* 门数量 */
    int gate_capacity;         /* 门容量 */
    int qubit_count;           /* 量子位总数 */
    double depth;              /* 电路深度 */
    char* name;                /* 电路名称 */
} QuantumCircuit;

/**
 * 创建量子执行器
 * 
 * @param state_manager 状态管理器
 * @param event_system 事件系统
 * @return 新创建的量子执行器
 */
QuantumExecutor* quantum_executor_create(StateManager* state_manager, EventSystem* event_system);

/**
 * 销毁量子执行器
 * 
 * @param executor 要销毁的量子执行器
 */
void quantum_executor_destroy(QuantumExecutor* executor);

/**
 * 设置执行模式
 * 
 * @param executor 量子执行器
 * @param mode 执行模式
 * @return 成功返回1，失败返回0
 */
int quantum_executor_set_mode(QuantumExecutor* executor, ExecutionMode mode);

/**
 * 设置优化级别
 * 
 * @param executor 量子执行器
 * @param level 优化级别
 * @return 成功返回1，失败返回0
 */
int quantum_executor_set_optimization(QuantumExecutor* executor, OptimizationLevel level);

/**
 * 执行单个量子门
 * 
 * @param executor 量子执行器
 * @param gate 量子门
 * @param state 量子状态
 * @return 成功返回1，失败返回0
 */
int quantum_executor_apply_gate(QuantumExecutor* executor, QuantumGate* gate, QState* state);

/**
 * 执行量子电路
 * 
 * @param executor 量子执行器
 * @param circuit 量子电路
 * @param state 量子状态
 * @return 成功返回1，失败返回0
 */
int quantum_executor_run_circuit(QuantumExecutor* executor, QuantumCircuit* circuit, QState* state);

/**
 * 获取执行统计信息
 * 
 * @param executor 量子执行器
 * @return 执行统计结构
 */
ExecutionStats quantum_executor_get_stats(QuantumExecutor* executor);

/**
 * 重置执行统计信息
 * 
 * @param executor 量子执行器
 */
void quantum_executor_reset_stats(QuantumExecutor* executor);

/**
 * 创建新的量子电路
 * 
 * @param qubit_count 量子位数量
 * @param name 电路名称
 * @return 新创建的量子电路
 */
QuantumCircuit* quantum_circuit_create(int qubit_count, const char* name);

/**
 * 销毁量子电路
 * 
 * @param circuit 要销毁的量子电路
 */
void quantum_circuit_destroy(QuantumCircuit* circuit);

/**
 * 添加门到量子电路
 * 
 * @param circuit 量子电路
 * @param gate 要添加的量子门
 * @return 成功返回1，失败返回0
 */
int quantum_circuit_add_gate(QuantumCircuit* circuit, QuantumGate* gate);

/**
 * 创建量子门
 * 
 * @param type 门类型
 * @param qubits 作用的量子位数组
 * @param qubit_count 量子位数量
 * @param parameters 参数数组(可选)
 * @param parameter_count 参数数量
 * @return 新创建的量子门
 */
QuantumGate* quantum_gate_create(QuantumGateType type, 
                                int* qubits, 
                                int qubit_count, 
                                double* parameters, 
                                int parameter_count);

/**
 * 创建自定义量子门
 * 
 * @param qubits 作用的量子位数组
 * @param qubit_count 量子位数量
 * @param custom_data 自定义门数据
 * @return 新创建的自定义量子门
 */
QuantumGate* quantum_gate_create_custom(int* qubits, 
                                       int qubit_count, 
                                       void* custom_data);

/**
 * 销毁量子门
 * 
 * @param gate 要销毁的量子门
 */
void quantum_gate_destroy(QuantumGate* gate);

/**
 * 优化量子电路
 * 
 * @param executor 量子执行器
 * @param circuit 要优化的量子电路
 * @param level 优化级别
 * @return 优化后的量子电路
 */
QuantumCircuit* quantum_executor_optimize_circuit(QuantumExecutor* executor, 
                                                QuantumCircuit* circuit, 
                                                OptimizationLevel level);

/**
 * 将量子电路转换为JSON字符串
 * 
 * @param circuit 量子电路
 * @return JSON字符串，使用后需要手动释放
 */
char* quantum_circuit_to_json(QuantumCircuit* circuit);

/**
 * 从JSON字符串解析量子电路
 * 
 * @param json JSON字符串
 * @return 解析后的量子电路
 */
QuantumCircuit* quantum_circuit_from_json(const char* json);

#endif /* QENTL_QUANTUM_EXECUTOR_H */ 