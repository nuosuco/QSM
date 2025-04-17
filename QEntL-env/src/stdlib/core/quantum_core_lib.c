/**
 * QEntL标准库核心函数实现
 * 
 * 量子基因编码: QG-STDLIB-CORE-A1B4
 * 
 * @文件: quantum_core_lib.c
 * @描述: 提供QEntL标准库中的核心函数实现，包括基础量子操作和工具函数
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-15
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 函数的输出自动包含量子基因编码和量子纠缠信道
 * - 能根据运行环境自适应调整量子比特处理能力
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "../../quantum_state.h"
#include "../../quantum_gene.h"
#include "../../quantum_entanglement.h"
#include "../../runtime/quantum_runtime.h"
#include "quantum_core_lib.h"

/* 量子纠缠激活 */
#define QUANTUM_ENTANGLEMENT_ACTIVE 1

/* 内部量子基因 */
static QGene* stdlib_core_gene = NULL;

/**
 * 初始化标准库核心组件
 */
int qentl_stdlib_core_initialize(void) {
    /* 如果已经初始化，返回成功 */
    if (stdlib_core_gene) {
        return 1;
    }
    
    /* 创建标准库核心量子基因 */
    stdlib_core_gene = quantum_gene_create("STDLIB-CORE", "A1B4");
    if (!stdlib_core_gene) {
        return 0;
    }
    
    /* 设置量子基因属性 */
    quantum_gene_add_metadata(stdlib_core_gene, "STDLIB_VERSION", "1.0");
    quantum_gene_add_metadata(stdlib_core_gene, "CREATION_TIME", 
                             (const char*)(size_t)time(NULL));
    quantum_gene_set_strength(stdlib_core_gene, 0.85);
    
    /* 创建量子纠缠 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        /* 创建与运行时核心的纠缠 */
        QEntanglement* ent_runtime = quantum_entanglement_create();
        if (ent_runtime) {
            quantum_entanglement_set_source(ent_runtime, "STDLIB-CORE");
            quantum_entanglement_set_target(ent_runtime, "RUNTIME-CORE");
            quantum_entanglement_set_strength(ent_runtime, 0.9);
            quantum_gene_add_entanglement(stdlib_core_gene, ent_runtime);
            quantum_entanglement_destroy(ent_runtime);
        }
        
        /* 创建与语言核心的纠缠 */
        QEntanglement* ent_lang = quantum_entanglement_create();
        if (ent_lang) {
            quantum_entanglement_set_source(ent_lang, "STDLIB-CORE");
            quantum_entanglement_set_target(ent_lang, "LANG-CORE");
            quantum_entanglement_set_strength(ent_lang, 0.85);
            quantum_gene_add_entanglement(stdlib_core_gene, ent_lang);
            quantum_entanglement_destroy(ent_lang);
        }
    }
    
    return 1;
}

/**
 * 清理标准库核心组件
 */
void qentl_stdlib_core_cleanup(void) {
    if (stdlib_core_gene) {
        quantum_gene_destroy(stdlib_core_gene);
        stdlib_core_gene = NULL;
    }
}

/**
 * 标准库核心版本信息
 */
const char* qentl_stdlib_core_version(void) {
    return "QEntL Standard Library Core 1.0";
}

/**
 * 获取当前可用量子比特数量
 */
int qentl_stdlib_get_qubit_count(void) {
    return quantum_runtime_get_qubit_count();
}

/**
 * 创建量子叠加态
 * 
 * @param basis_states 基态名称数组
 * @param amplitudes 对应的振幅数组
 * @param count 状态数量
 * @return 叠加态状态指针，失败返回NULL
 */
QState* qentl_create_superposition(const char** basis_states, 
                                  double* amplitudes, 
                                  size_t count) {
    if (!basis_states || !amplitudes || count == 0) {
        return NULL;
    }
    
    /* 标准化振幅 - 计算总振幅平方和 */
    double sum_sqr = 0.0;
    for (size_t i = 0; i < count; i++) {
        sum_sqr += amplitudes[i] * amplitudes[i];
    }
    
    /* 如果振幅平方和不接近1.0，则归一化 */
    if (fabs(sum_sqr - 1.0) > 0.00001) {
        double norm = sqrt(sum_sqr);
        for (size_t i = 0; i < count; i++) {
            amplitudes[i] /= norm;
        }
    }
    
    /* 创建各基态 */
    QState** states = (QState**)malloc(sizeof(QState*) * count);
    if (!states) {
        return NULL;
    }
    
    for (size_t i = 0; i < count; i++) {
        states[i] = quantum_runtime_create_state(basis_states[i]);
        if (!states[i]) {
            /* 清理已创建的状态 */
            for (size_t j = 0; j < i; j++) {
                quantum_runtime_destroy_state(states[j]);
            }
            free(states);
            return NULL;
        }
    }
    
    /* 将振幅转换为概率 */
    double* probabilities = (double*)malloc(sizeof(double) * count);
    if (!probabilities) {
        /* 清理已创建的状态 */
        for (size_t i = 0; i < count; i++) {
            quantum_runtime_destroy_state(states[i]);
        }
        free(states);
        return NULL;
    }
    
    for (size_t i = 0; i < count; i++) {
        probabilities[i] = amplitudes[i] * amplitudes[i]; /* 概率 = |振幅|^2 */
    }
    
    /* 创建叠加态 */
    QState* superposition = quantum_runtime_create_superposition(states, probabilities, count);
    
    /* 清理资源 */
    for (size_t i = 0; i < count; i++) {
        quantum_runtime_destroy_state(states[i]);
    }
    free(states);
    free(probabilities);
    
    /* 应用标准库的量子基因 */
    if (superposition && stdlib_core_gene) {
        QGene* gene = quantum_gene_clone(stdlib_core_gene);
        if (gene) {
            /* 添加叠加态特定元数据 */
            quantum_gene_add_metadata(gene, "FUNCTION", "qentl_create_superposition");
            quantum_gene_add_metadata(gene, "STATE_COUNT", (const char*)(size_t)count);
            
            /* 应用基因 */
            quantum_state_apply_gene(superposition, gene);
            quantum_gene_destroy(gene);
        }
    }
    
    return superposition;
}

/**
 * 测量量子叠加态
 * 
 * @param state 叠加态
 * @return 测量结果索引，-1表示错误
 */
int qentl_measure_state(QState* state) {
    if (!state) {
        return -1;
    }
    
    /* 检查状态类型 */
    const char* type = quantum_state_get_type(state);
    if (!type || strcmp(type, "superposition") != 0) {
        return -1; /* 不是叠加态 */
    }
    
    /* 获取叠加分量数量 */
    size_t component_count = quantum_state_get_component_count(state);
    if (component_count == 0) {
        return -1;
    }
    
    /* 获取所有分量概率 */
    double* probabilities = (double*)malloc(sizeof(double) * component_count);
    if (!probabilities) {
        return -1;
    }
    
    /* 填充概率数组 */
    for (size_t i = 0; i < component_count; i++) {
        probabilities[i] = quantum_state_get_component_probability(state, i);
    }
    
    /* 生成0-1之间的随机数 */
    double random_value = (double)rand() / RAND_MAX;
    
    /* 根据概率选择结果 */
    double cumulative_prob = 0.0;
    int result = -1;
    
    for (size_t i = 0; i < component_count; i++) {
        cumulative_prob += probabilities[i];
        if (random_value <= cumulative_prob) {
            result = (int)i;
            break;
        }
    }
    
    /* 释放资源 */
    free(probabilities);
    
    return result;
}

/**
 * 创建Bell态（最大纠缠态）
 * 
 * @return Bell态指针，失败返回NULL
 */
QState* qentl_create_bell_state(void) {
    /* 创建Bell态的两个基本状态 */
    QState* state_0 = quantum_runtime_create_state("bell_0");
    QState* state_1 = quantum_runtime_create_state("bell_1");
    
    if (!state_0 || !state_1) {
        if (state_0) quantum_runtime_destroy_state(state_0);
        if (state_1) quantum_runtime_destroy_state(state_1);
        return NULL;
    }
    
    /* 设置基态属性 */
    quantum_state_set_property(state_0, "basis", "0");
    quantum_state_set_property(state_1, "basis", "1");
    
    /* 创建Bell态的叠加 */
    QState* states[2] = {state_0, state_1};
    double probabilities[2] = {0.5, 0.5}; /* 等概率叠加 */
    
    QState* bell_state = quantum_runtime_create_superposition(states, probabilities, 2);
    
    /* 设置Bell态特殊属性 */
    if (bell_state) {
        quantum_state_set_property(bell_state, "entanglement_type", "Bell");
        quantum_state_set_property(bell_state, "max_entangled", "true");
        
        /* 应用标准库的量子基因 */
        if (stdlib_core_gene) {
            QGene* gene = quantum_gene_clone(stdlib_core_gene);
            if (gene) {
                /* 添加Bell态特定元数据 */
                quantum_gene_add_metadata(gene, "FUNCTION", "qentl_create_bell_state");
                quantum_gene_add_metadata(gene, "ENTANGLEMENT_TYPE", "Bell");
                quantum_gene_set_strength(gene, 0.95); /* Bell态具有更高的纠缠强度 */
                
                /* 应用基因 */
                quantum_state_apply_gene(bell_state, gene);
                quantum_gene_destroy(gene);
            }
        }
    }
    
    /* 释放基态 */
    quantum_runtime_destroy_state(state_0);
    quantum_runtime_destroy_state(state_1);
    
    return bell_state;
}

/**
 * 应用Hadamard门
 * 
 * 将|0>变为(|0>+|1>)/√2，将|1>变为(|0>-|1>)/√2
 * 
 * @param state 输入量子态
 * @return 应用Hadamard门后的量子态，失败返回NULL
 */
QState* qentl_apply_hadamard(QState* state) {
    if (!state) {
        return NULL;
    }
    
    /* 获取状态类型 */
    const char* type = quantum_state_get_type(state);
    
    /* 检查是否为基态 */
    if (type && strcmp(type, "basis") == 0) {
        /* 获取基态值 */
        const char* basis = quantum_state_get_property(state, "basis");
        if (!basis) {
            return NULL;
        }
        
        /* 创建新的叠加态 */
        if (strcmp(basis, "0") == 0) {
            /* |0> -> (|0>+|1>)/√2 */
            const char* basis_states[2] = {"hadamard_0", "hadamard_1"};
            double amplitudes[2] = {1.0/sqrt(2), 1.0/sqrt(2)};
            
            QState* result = qentl_create_superposition(basis_states, amplitudes, 2);
            if (result) {
                quantum_state_set_property(result, "hadamard_input", "0");
            }
            return result;
        }
        else if (strcmp(basis, "1") == 0) {
            /* |1> -> (|0>-|1>)/√2 */
            const char* basis_states[2] = {"hadamard_0", "hadamard_1"};
            double amplitudes[2] = {1.0/sqrt(2), -1.0/sqrt(2)};
            
            QState* result = qentl_create_superposition(basis_states, amplitudes, 2);
            if (result) {
                quantum_state_set_property(result, "hadamard_input", "1");
            }
            return result;
        }
    }
    
    /* 如果不是基态，返回NULL */
    return NULL;
}

/**
 * 检查两个量子态是否相等
 * 
 * @param state1 第一个量子态
 * @param state2 第二个量子态
 * @return 相等返回1，不相等返回0
 */
int qentl_states_equal(QState* state1, QState* state2) {
    if (!state1 || !state2) {
        return 0;
    }
    
    /* 检查类型 */
    const char* type1 = quantum_state_get_type(state1);
    const char* type2 = quantum_state_get_type(state2);
    
    if (!type1 || !type2 || strcmp(type1, type2) != 0) {
        return 0; /* 类型不同 */
    }
    
    /* 检查是否为基态 */
    if (strcmp(type1, "basis") == 0) {
        /* 比较基态值 */
        const char* basis1 = quantum_state_get_property(state1, "basis");
        const char* basis2 = quantum_state_get_property(state2, "basis");
        
        if (!basis1 || !basis2) {
            return 0;
        }
        
        return strcmp(basis1, basis2) == 0;
    }
    
    /* 检查是否为叠加态 */
    if (strcmp(type1, "superposition") == 0) {
        /* 比较分量数量 */
        size_t count1 = quantum_state_get_component_count(state1);
        size_t count2 = quantum_state_get_component_count(state2);
        
        if (count1 != count2) {
            return 0; /* 分量数量不同 */
        }
        
        /* 比较每个分量和概率 */
        for (size_t i = 0; i < count1; i++) {
            double prob1 = quantum_state_get_component_probability(state1, i);
            
            /* 在state2中查找匹配分量 */
            int found = 0;
            for (size_t j = 0; j < count2; j++) {
                double prob2 = quantum_state_get_component_probability(state2, j);
                
                /* 检查概率是否接近 */
                if (fabs(prob1 - prob2) < 0.00001) {
                    found = 1;
                    break;
                }
            }
            
            if (!found) {
                return 0; /* 没有找到匹配分量 */
            }
        }
        
        return 1; /* 所有分量都匹配 */
    }
    
    /* 对于其他类型的状态，简单比较名称 */
    const char* name1 = quantum_state_get_name(state1);
    const char* name2 = quantum_state_get_name(state2);
    
    if (!name1 || !name2) {
        return 0;
    }
    
    return strcmp(name1, name2) == 0;
}

/**
 * 创建量子门操作
 * 
 * @param gate_type 门类型
 * @param params 门参数
 * @return 门操作指针，失败返回NULL
 */
void* qentl_create_gate(const char* gate_type, double* params) {
    if (!gate_type) {
        return NULL;
    }
    
    /* 此处实现门创建逻辑 */
    /* 简化版本，实际实现应更复杂 */
    
    /* 创建门结构 */
    struct QGate* gate = (struct QGate*)malloc(sizeof(struct QGate));
    if (!gate) {
        return NULL;
    }
    
    /* 设置门类型 */
    gate->type = strdup(gate_type);
    if (!gate->type) {
        free(gate);
        return NULL;
    }
    
    /* 复制参数 */
    if (params) {
        /* 计算参数数量 */
        int param_count = 0;
        if (strcmp(gate_type, "X") == 0 || 
            strcmp(gate_type, "Y") == 0 || 
            strcmp(gate_type, "Z") == 0 || 
            strcmp(gate_type, "H") == 0) {
            param_count = 0;
        } else if (strcmp(gate_type, "Rx") == 0 || 
                  strcmp(gate_type, "Ry") == 0 || 
                  strcmp(gate_type, "Rz") == 0 || 
                  strcmp(gate_type, "Phase") == 0) {
            param_count = 1;
        } else if (strcmp(gate_type, "CNOT") == 0 || 
                  strcmp(gate_type, "CZ") == 0) {
            param_count = 2;
        } else {
            /* 未知门类型 */
            free(gate->type);
            free(gate);
            return NULL;
        }
        
        /* 分配参数数组 */
        gate->params = (double*)malloc(sizeof(double) * param_count);
        if (!gate->params && param_count > 0) {
            free(gate->type);
            free(gate);
            return NULL;
        }
        
        /* 复制参数 */
        for (int i = 0; i < param_count; i++) {
            gate->params[i] = params[i];
        }
        
        gate->param_count = param_count;
    } else {
        gate->params = NULL;
        gate->param_count = 0;
    }
    
    /* 应用量子基因 */
    if (stdlib_core_gene) {
        gate->gene = quantum_gene_clone(stdlib_core_gene);
        if (gate->gene) {
            /* 添加门特定元数据 */
            quantum_gene_add_metadata(gate->gene, "GATE_TYPE", gate_type);
            quantum_gene_add_metadata(gate->gene, "PARAM_COUNT", 
                                     (const char*)(size_t)gate->param_count);
            
            /* 设置基因强度 */
            if (strcmp(gate_type, "CNOT") == 0 || strcmp(gate_type, "CZ") == 0) {
                /* 纠缠门有更高强度 */
                quantum_gene_set_strength(gate->gene, 0.9);
            } else {
                quantum_gene_set_strength(gate->gene, 0.85);
            }
        }
    } else {
        gate->gene = NULL;
    }
    
    return gate;
}

/**
 * 应用量子门到状态
 * 
 * @param state 量子态
 * @param gate 量子门
 * @return 应用门后的新状态，失败返回NULL
 */
QState* qentl_apply_gate_to_state(QState* state, void* gate) {
    if (!state || !gate) {
        return NULL;
    }
    
    struct QGate* qgate = (struct QGate*)gate;
    
    /* 根据门类型应用到状态 */
    if (strcmp(qgate->type, "H") == 0) {
        /* Hadamard门 */
        return qentl_apply_hadamard(state);
    }
    /* 这里应实现其他量子门的应用逻辑 */
    /* 简化版本，实际实现应更复杂 */
    
    /* 未知门类型 */
    return NULL;
}

/**
 * 释放量子门
 * 
 * @param gate 量子门指针
 */
void qentl_destroy_gate(void* gate) {
    if (!gate) {
        return;
    }
    
    struct QGate* qgate = (struct QGate*)gate;
    
    /* 释放资源 */
    if (qgate->type) {
        free(qgate->type);
    }
    
    if (qgate->params) {
        free(qgate->params);
    }
    
    if (qgate->gene) {
        quantum_gene_destroy(qgate->gene);
    }
    
    free(qgate);
} 