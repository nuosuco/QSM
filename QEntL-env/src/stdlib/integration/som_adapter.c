/**
 * SOM适配器实现文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月22日
 * 
 * 描述：自组织映射(Self-Organizing Map)模型适配器
 *      将SOM模型集成到QEntL量子环境中，实现神经网络与量子计算的结合
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "quantum_model_integration.h"
#include "../core/math_library.h"
#include "../../quantum_state.h"
#include "../../quantum_entanglement.h"
#include "claude_adapter.h" // 添加Claude适配器头文件

// SOM模型状态
typedef struct {
    // 网格尺寸
    int grid_width;
    int grid_height;
    
    // 神经元权重
    double*** weights;        // [y][x][dimension]
    
    // 输入维度
    int input_dimension;
    
    // 学习率和邻域参数
    double initial_learning_rate;
    double current_learning_rate;
    double initial_radius;
    double current_radius;
    
    // 训练进度
    int current_iteration;
    int max_iterations;
    
    // 量子增强参数
    bool quantum_enhanced;
    int qubits_per_neuron;
    
    // 纠缠网络
    EntanglementNetwork* entanglement_network;
    
    // 活跃节点量子状态
    QuantumState* active_neuron_state;

    // 知识管理 - 新增
    double knowledge_confidence;
    char* recent_queries[10];
    int query_count;
    QuantumState* knowledge_states[20];
    int knowledge_count;
} SOMModelState;

// 前向声明
static SOMModelState* som_model_create(int width, int height, int dimension, 
                                     double learning_rate, double radius, int max_iter,
                                     bool quantum_enhanced, int qubits_per_neuron);
static void som_model_destroy(SOMModelState* model);
static double calculate_distance(double* vector1, double* vector2, int dimension);
static void find_best_matching_unit(SOMModelState* model, double* input, int* bmu_x, int* bmu_y);
static void update_weights(SOMModelState* model, double* input, int bmu_x, int bmu_y);
static int som_detect_knowledge_gap(SOMModelState* model, const char* query, double* confidence);
static QuantumState* som_ask_claude(const char* query);
static int som_integrate_knowledge(SOMModelState* model, QuantumState* knowledge_state);
static EntanglementChannel* som_adapter_create_entanglement_channel(SOMModelState* model, QuantumState* state, QuantumModelType target_model, const char* target_model_id);
static EntanglementChannel* som_create_knowledge_sharing_channel(QuantumState* state);
static bool som_process_integration_event(SOMModelState* model, IntegrationEvent* event);
static bool som_model_train(SOMModelState* model, double** training_data, int data_count);
static bool som_model_map(SOMModelState* model, double* input, int* mapped_x, int* mapped_y);
static bool som_model_save(SOMModelState* model, const char* filename);
static SOMModelState* som_model_load(const char* filename, bool quantum_enhanced, int qubits_per_neuron);

// 初始化SOM模型
static SOMModelState* som_model_create(int width, int height, int dimension, 
                                      double learning_rate, double radius, int max_iter,
                                      bool quantum_enhanced, int qubits_per_neuron) {
    SOMModelState* model = (SOMModelState*)malloc(sizeof(SOMModelState));
    if (!model) {
        printf("内存分配失败: 无法创建SOM模型状态\n");
        return NULL;
    }
    
    // 初始化基本参数
    model->grid_width = width;
    model->grid_height = height;
    model->input_dimension = dimension;
    model->initial_learning_rate = learning_rate;
    model->current_learning_rate = learning_rate;
    model->initial_radius = radius;
    model->current_radius = radius;
    model->current_iteration = 0;
    model->max_iterations = max_iter;
    model->quantum_enhanced = quantum_enhanced;
    model->qubits_per_neuron = qubits_per_neuron;
    
    // 初始化知识管理系统
    model->knowledge_confidence = 0.5; // 初始确信度
    model->query_count = 0;
    model->knowledge_count = 0;
    for (int i = 0; i < 10; i++) {
        model->recent_queries[i] = NULL;
    }
    for (int i = 0; i < 20; i++) {
        model->knowledge_states[i] = NULL;
    }
    
    // 分配权重内存空间
    model->weights = (double***)malloc(height * sizeof(double**));
    if (!model->weights) {
        printf("内存分配失败: 无法为权重分配内存\n");
        free(model);
        return NULL;
    }
    
    for (int y = 0; y < height; y++) {
        model->weights[y] = (double**)malloc(width * sizeof(double*));
        if (!model->weights[y]) {
            printf("内存分配失败: 无法为权重分配内存\n");
            // 清理已分配的内存
            for (int i = 0; i < y; i++) {
                free(model->weights[i]);
            }
            free(model->weights);
            free(model);
            return NULL;
        }
        
        for (int x = 0; x < width; x++) {
            model->weights[y][x] = (double*)malloc(dimension * sizeof(double));
            if (!model->weights[y][x]) {
                printf("内存分配失败: 无法为权重分配内存\n");
                // 清理已分配的内存
                for (int i = 0; i < y; i++) {
                    for (int j = 0; j < width; j++) {
                        free(model->weights[i][j]);
                    }
                    free(model->weights[i]);
                }
                free(model->weights);
                free(model);
                return NULL;
            }
            
            // 初始化权重为随机值 (0-1)
            for (int d = 0; d < dimension; d++) {
                model->weights[y][x][d] = (double)rand() / RAND_MAX;
            }
        }
    }
    
    // 如果是量子增强模式，创建量子状态
    if (quantum_enhanced) {
        // 创建纠缠网络
        int total_qubits = width * height * qubits_per_neuron;
        model->entanglement_network = create_entanglement_network(total_qubits);
        if (!model->entanglement_network) {
            printf("无法创建纠缠网络\n");
            model->quantum_enhanced = false; // 降级为经典模式
        }
        
        // 创建活跃神经元的量子状态
        model->active_neuron_state = create_quantum_state(qubits_per_neuron);
        if (!model->active_neuron_state) {
            printf("无法创建量子状态\n");
            destroy_entanglement_network(model->entanglement_network);
            model->quantum_enhanced = false; // 降级为经典模式
        }
    } else {
        model->entanglement_network = NULL;
        model->active_neuron_state = NULL;
    }
    
    printf("SOM模型已创建: %dx%d 网格, %d 维输入\n", width, height, dimension);
    return model;
}

// 销毁SOM模型
static void som_model_destroy(SOMModelState* model) {
    if (!model) return;
    
    // 释放权重内存
    for (int y = 0; y < model->grid_height; y++) {
        for (int x = 0; x < model->grid_width; x++) {
            free(model->weights[y][x]);
        }
        free(model->weights[y]);
    }
    free(model->weights);
    
    // 释放量子资源
    if (model->quantum_enhanced) {
        if (model->entanglement_network) {
            destroy_entanglement_network(model->entanglement_network);
        }
        if (model->active_neuron_state) {
            destroy_quantum_state(model->active_neuron_state);
        }
    }
    
    // 释放知识管理资源
    for (int i = 0; i < model->query_count; i++) {
        if (model->recent_queries[i]) {
            free(model->recent_queries[i]);
        }
    }
    
    for (int i = 0; i < model->knowledge_count; i++) {
        if (model->knowledge_states[i]) {
            quantum_state_destroy(model->knowledge_states[i]);
        }
    }
    
    free(model);
    printf("SOM模型已销毁\n");
}

// 计算两个向量之间的欧氏距离
static double calculate_distance(double* vector1, double* vector2, int dimension) {
    double sum = 0.0;
    for (int i = 0; i < dimension; i++) {
        double diff = vector1[i] - vector2[i];
        sum += diff * diff;
    }
    return sqrt(sum);
}

// 找到最佳匹配单元(BMU)
static void find_best_matching_unit(SOMModelState* model, double* input, int* bmu_x, int* bmu_y) {
    double min_distance = INFINITY;
    
    for (int y = 0; y < model->grid_height; y++) {
        for (int x = 0; x < model->grid_width; x++) {
            double distance = calculate_distance(input, model->weights[y][x], model->input_dimension);
            
            if (distance < min_distance) {
                min_distance = distance;
                *bmu_x = x;
                *bmu_y = y;
            }
        }
    }
    
    // 如果是量子增强模式，更新活跃神经元的量子状态
    if (model->quantum_enhanced && model->active_neuron_state) {
        // 将BMU位置编码到量子状态
        int bmu_index = (*bmu_y) * model->grid_width + (*bmu_x);
        
        // 重置量子态
        reset_quantum_state(model->active_neuron_state);
        
        // 应用量子门来编码BMU位置
        // 这里我们使用一个简单的编码方案，可以根据需要扩展
        for (int i = 0; i < model->qubits_per_neuron; i++) {
            if (bmu_index & (1 << i)) {
                apply_x_gate(model->active_neuron_state, i);
            }
        }
    }
}

// 更新网络
static void update_weights(SOMModelState* model, double* input, int bmu_x, int bmu_y) {
    for (int y = 0; y < model->grid_height; y++) {
        for (int x = 0; x < model->grid_width; x++) {
            // 计算距BMU的距离
            double distance_to_bmu = sqrt((x - bmu_x) * (x - bmu_x) + (y - bmu_y) * (y - bmu_y));
            
            // 如果在当前半径内
            if (distance_to_bmu <= model->current_radius) {
                // 计算影响（邻域函数）
                double influence = exp(-distance_to_bmu * distance_to_bmu / (2 * model->current_radius * model->current_radius));
                
                // 更新权重
                for (int d = 0; d < model->input_dimension; d++) {
                    model->weights[y][x][d] += model->current_learning_rate * influence * (input[d] - model->weights[y][x][d]);
                }
                
                // 如果是量子增强模式，更新量子纠缠
                if (model->quantum_enhanced && model->entanglement_network) {
                    int neuron_index = y * model->grid_width + x;
                    int bmu_index = bmu_y * model->grid_width + bmu_x;
                    
                    // 基于距离和影响调整纠缠
                    int target_qubit = neuron_index * model->qubits_per_neuron;
                    int control_qubit = bmu_index * model->qubits_per_neuron;
                    
                    // 应用受控操作来增强纠缠
                    if (influence > 0.5) {
                        apply_controlled_entanglement(model->entanglement_network, 
                                                   control_qubit, 
                                                   target_qubit,
                                                   influence);
                    }
                }
            }
        }
    }
}

// 新增: 知识缺口检测
static int som_detect_knowledge_gap(SOMModelState* model, const char* query, double* confidence) {
    if (!model || !query || !confidence) {
        return 0;
    }
    
    // 设置当前确信度
    *confidence = model->knowledge_confidence;
    
    // 如果确信度低于阈值，认为存在知识缺口
    if (*confidence < 0.7) {
        printf("SOM模型检测到知识缺口，确信度: %.2f\n", *confidence);
        
        // 记录查询
        if (model->query_count < 10) {
            model->recent_queries[model->query_count] = strdup(query);
            model->query_count++;
        } else {
            // 移除最旧的查询并添加新查询
            free(model->recent_queries[0]);
            for (int i = 0; i < 9; i++) {
                model->recent_queries[i] = model->recent_queries[i+1];
            }
            model->recent_queries[9] = strdup(query);
        }
        
        return 1; // 存在知识缺口
    }
    
    return 0; // 没有知识缺口
}

// 新增: 向Claude提问
static QuantumState* som_ask_claude(const char* query) {
    if (!query) {
        return NULL;
    }
    
    printf("SOM模型向Claude提问: %s\n", query);
    
    // 调用Claude适配器处理文本
    char* claude_response = claude_adapter_process_text(query, 
        "你是一个自组织映射模型的知识助手。请以清晰、准确的方式回答问题，侧重于神经网络和拓扑映射的见解。");
    
    if (!claude_response) {
        printf("无法从Claude获取响应\n");
        return NULL;
    }
    
    printf("收到Claude响应\n");
    
    // 将Claude响应转换为量子状态
    QuantumState* knowledge_state = claude_adapter_generate_quantum_state(
        claude_response, "som_new_knowledge");
    
    // 释放响应内存
    free(claude_response);
    
    return knowledge_state;
}

// 新增: 整合知识
static int som_integrate_knowledge(SOMModelState* model, QuantumState* knowledge_state) {
    if (!model || !knowledge_state) {
        return 0;
    }
    
    printf("SOM模型整合新知识: %s\n", knowledge_state->id);
    
    // 将知识状态添加到知识库
    if (model->knowledge_count < 20) {
        model->knowledge_states[model->knowledge_count] = knowledge_state;
        model->knowledge_count++;
        
        // 提高知识确信度
        model->knowledge_confidence += 0.05;
        if (model->knowledge_confidence > 1.0) {
            model->knowledge_confidence = 1.0;
        }
    } else {
        // 移除最旧的知识并添加新知识
        quantum_state_destroy(model->knowledge_states[0]);
        for (int i = 0; i < 19; i++) {
            model->knowledge_states[i] = model->knowledge_states[i+1];
        }
        model->knowledge_states[19] = knowledge_state;
    }
    
    // 根据知识更新网络权重
    // 这里是一个简化版实现，实际中可能需要更复杂的整合逻辑
    if (model->quantum_enhanced && model->active_neuron_state) {
        // 尝试将知识量子态与活跃神经元状态纠缠
        entangle_quantum_states(model->active_neuron_state, knowledge_state);
    }
    
    return 1;
}

// 新增: 创建SOM适配器与其他模型之间的纠缠信道
static EntanglementChannel* som_adapter_create_entanglement_channel(SOMModelState* model, QuantumState* state, QuantumModelType target_model, const char* target_model_id) {
    if (!model || !state || !target_model_id) {
        return NULL;
    }
    
    printf("SOM适配器创建与%s(%d)模型的纠缠信道\n", target_model_id, target_model);
    
    // 创建一个唯一的信道ID
    char channel_id[128];
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    uint64_t timestamp = (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
    
    snprintf(channel_id, sizeof(channel_id), "som_to_%s_%lu", 
             target_model_id, timestamp);
    
    // 创建纠缠信道
    EntanglementChannel* channel = quantum_entanglement_create(
        channel_id, 
        "som_model_001",        // 源模型ID 
        MODEL_SOM,              // 源模型类型
        target_model_id,        // 目标模型ID
        target_model            // 目标模型类型
    );
    
    if (!channel) {
        printf("创建纠缠信道失败\n");
        return NULL;
    }
    
    // 设置信道属性
    quantum_entanglement_set_property(channel, "state_id", state->id);
    quantum_entanglement_set_property(channel, "entanglement_strength", "0.95");
    quantum_entanglement_set_property(channel, "connection_type", "direct");
    quantum_entanglement_set_property(channel, "grid_dimensions", 
                                     (char*)model->grid_width); // 添加SOM特有属性
    
    // 添加量子基因编码
    char gene_code[128];
    sprintf(gene_code, "QG-ENTANGLE-SOM-%d-%lu", target_model, timestamp);
    quantum_entanglement_add_gene(channel, gene_code);
    
    // 将状态附加到信道
    quantum_entanglement_attach_state(channel, state);
    
    // 通知集成管理器
    IntegrationManager* manager = get_default_integration_manager();
    if (manager) {
        // 创建纠缠创建事件
        IntegrationEvent* event = create_integration_event(
            EVENT_ENTANGLEMENT_CREATED, 
            "som_model_001", 
            MODEL_SOM, 
            "SOM模型创建了与其他模型的纠缠信道"
        );
        
        if (event) {
            // 添加目标模型信息
            char target_info[256];
            sprintf(target_info, "target_model_type=%d;target_model_id=%s;channel_id=%s", 
                    target_model, target_model_id, channel_id);
            event->event_data = strdup(target_info);
            
            // 发布事件
            publish_event(manager, event);
            
            // 释放事件资源
            free(event->event_data);
            free_integration_event(event);
        }
    }
    
    printf("SOM适配器成功创建纠缠信道: %s\n", channel_id);
    
    return channel;
}

// 修改: 使用新的som_adapter_create_entanglement_channel函数创建知识共享信道
static EntanglementChannel* som_create_knowledge_sharing_channel(QuantumState* state) {
    if (!state) {
        return NULL;
    }
    
    printf("SOM模型创建知识共享纠缠信道\n");
    
    // 获取当前SOM模型状态 - 此处应该从适配器获取，简化实现
    SOMModelState* current_model = NULL; // 此处简化，实际应从全局适配器获取
    // 假设从全局适配器获取模型状态的函数
    // current_model = get_current_som_model_state();
    
    if (!current_model) {
        // 如果无法获取当前模型，退回到使用Claude适配器
        return claude_adapter_create_entanglement_channel(state);
    }
    
    // 创建与QSM模型的纠缠信道
    EntanglementChannel* qsm_channel = som_adapter_create_entanglement_channel(
        current_model, state, MODEL_QSM, "qsm_model_001");
    
    // 创建与WeQ模型的纠缠信道
    EntanglementChannel* weq_channel = som_adapter_create_entanglement_channel(
        current_model, state, MODEL_WEQ, "weq_model_001");
    
    // 创建与REF模型的纠缠信道
    EntanglementChannel* ref_channel = som_adapter_create_entanglement_channel(
        current_model, state, MODEL_REF, "ref_model_001");
    
    // 打印成功信息
    printf("已创建知识共享纠缠信道，强度: %.2f\n", qsm_channel ? qsm_channel->strength : 0.0);
    
    // 返回QSM信道作为主要信道
    return qsm_channel;
}

// 新增: 集成进SOM模型训练过程 - 处理相关事件
static bool som_process_integration_event(SOMModelState* model, IntegrationEvent* event) {
    if (!model || !event) {
        return false;
    }
    
    printf("SOM模型处理集成事件: 类型=%d\n", event->type);
    
    switch (event->type) {
        case EVENT_STATE_CHANGED: {
            // 处理状态变化事件，可能需要调整网络
            if (event->source_model != MODEL_SOM) {
                // 其他模型的状态变化，可能需要学习适应
                double confidence = 0.0;
                if (som_detect_knowledge_gap(model, "如何调整SOM拓扑以适应新状态?", &confidence)) {
                    QuantumState* knowledge = som_ask_claude("如何在SOM网络中整合来自其他模型的量子状态变化?");
                    if (knowledge) {
                        som_integrate_knowledge(model, knowledge);
                        som_create_knowledge_sharing_channel(knowledge);
                    }
                }
            }
            break;
        }
        
        case EVENT_ENTANGLEMENT_CREATED: {
            // 新的纠缠关系建立，可能影响网络拓扑
            if (model->quantum_enhanced) {
                printf("检测到新的纠缠关系，调整SOM量子增强参数\n");
                // 实际调整逻辑
            }
            break;
        }
        
        case EVENT_CUSTOM: {
            // 检查是否是知识缺口事件
            if (event->event_data && strstr((const char*)event->event_data, "KNOWLEDGE_GAP")) {
                printf("SOM检测到知识缺口事件\n");
                
                // 提取查询
                char* query_start = strstr((const char*)event->event_data, "QUERY:");
                if (query_start) {
                    query_start += 6; // 跳过"QUERY:"
                    
                    // 寻找查询结束位置
                    char* query_end = strstr(query_start, "\n");
                    if (!query_end) query_end = query_start + strlen(query_start);
                    
                    // 复制查询内容
                    size_t query_len = query_end - query_start;
                    char* query = (char*)malloc(query_len + 1);
                    if (query) {
                        strncpy(query, query_start, query_len);
                        query[query_len] = '\0';
                        
                        // 向Claude提问
                        QuantumState* knowledge = som_ask_claude(query);
                        if (knowledge) {
                            // 整合知识
                            som_integrate_knowledge(model, knowledge);
                            
                            // 在模型之间共享这个知识
                            som_create_knowledge_sharing_channel(knowledge);
                        }
                        
                        free(query);
                    }
                }
            }
            break;
        }
        
        default:
            break;
    }
    
    return true;
}

// 修改: 在SOM模型训练过程中添加知识缺口检测和处理
static bool som_model_train(SOMModelState* model, double** training_data, int data_count) {
    if (!model || !training_data || data_count <= 0) {
        printf("无效的训练参数\n");
        return false;
    }
    
    printf("开始训练SOM模型...\n");
    
    // 主训练循环
    for (int iter = 0; iter < model->max_iterations; iter++) {
        model->current_iteration = iter;
        
        // 随机选择训练样本
        int sample_index = rand() % data_count;
        double* input = training_data[sample_index];
        
        // 找到最佳匹配单元
        int bmu_x = 0, bmu_y = 0;
        find_best_matching_unit(model, input, &bmu_x, &bmu_y);
        
        // 更新权重
        update_weights(model, input, bmu_x, bmu_y);
        
        // 更新学习率和半径
        model->current_learning_rate = model->initial_learning_rate * exp(-iter / (double)model->max_iterations);
        model->current_radius = model->initial_radius * exp(-iter / (double)model->max_iterations);
        
        // 每隔一段迭代打印进度
        if (iter % (model->max_iterations / 10) == 0 || iter == model->max_iterations - 1) {
            printf("训练进度: %.1f%% (迭代 %d/%d)\n", 
                   100.0 * iter / model->max_iterations, 
                   iter + 1, model->max_iterations);
        }
        
        // 如果找到难以匹配的数据点，可能需要额外知识
        if (iter % 100 == 0) { // 定期检查训练进度
            double progress = (double)iter / model->max_iterations;
            // 如果进度不理想，寻求Claude的帮助
            if (progress > 0.5 && model->current_learning_rate > 0.7 * model->initial_learning_rate) {
                double confidence = 0.0;
                if (som_detect_knowledge_gap(model, "如何优化SOM训练过程以提高收敛速度?", &confidence)) {
                    QuantumState* knowledge = som_ask_claude("请提供优化自组织映射训练过程的高级技巧，特别是调整学习率和邻域函数的策略。");
                    if (knowledge) {
                        som_integrate_knowledge(model, knowledge);
                    }
                }
            }
        }
    }
    
    printf("SOM模型训练完成\n");
    return true;
}

// 使用SOM模型进行映射
static bool som_model_map(SOMModelState* model, double* input, int* mapped_x, int* mapped_y) {
    if (!model || !input || !mapped_x || !mapped_y) {
        printf("无效的映射参数\n");
        return false;
    }
    
    // 找到最佳匹配单元
    find_best_matching_unit(model, input, mapped_x, mapped_y);
    return true;
}

// 保存SOM模型到文件
static bool som_model_save(SOMModelState* model, const char* filename) {
    if (!model || !filename) {
        printf("无效的保存参数\n");
        return false;
    }
    
    FILE* file = fopen(filename, "wb");
    if (!file) {
        printf("无法打开文件进行写入: %s\n", filename);
        return false;
    }
    
    // 写入网格尺寸和维度
    fwrite(&model->grid_width, sizeof(int), 1, file);
    fwrite(&model->grid_height, sizeof(int), 1, file);
    fwrite(&model->input_dimension, sizeof(int), 1, file);
    
    // 写入学习参数
    fwrite(&model->initial_learning_rate, sizeof(double), 1, file);
    fwrite(&model->initial_radius, sizeof(double), 1, file);
    fwrite(&model->max_iterations, sizeof(int), 1, file);
    
    // 写入权重
    for (int y = 0; y < model->grid_height; y++) {
        for (int x = 0; x < model->grid_width; x++) {
            fwrite(model->weights[y][x], sizeof(double), model->input_dimension, file);
        }
    }
    
    fclose(file);
    printf("SOM模型已保存到文件: %s\n", filename);
    return true;
}

// 从文件加载SOM模型
static SOMModelState* som_model_load(const char* filename, bool quantum_enhanced, int qubits_per_neuron) {
    if (!filename) {
        printf("无效的文件名\n");
        return NULL;
    }
    
    FILE* file = fopen(filename, "rb");
    if (!file) {
        printf("无法打开文件进行读取: %s\n", filename);
        return NULL;
    }
    
    // 读取网格尺寸和维度
    int grid_width, grid_height, input_dimension;
    fread(&grid_width, sizeof(int), 1, file);
    fread(&grid_height, sizeof(int), 1, file);
    fread(&input_dimension, sizeof(int), 1, file);
    
    // 读取学习参数
    double initial_learning_rate, initial_radius;
    int max_iterations;
    fread(&initial_learning_rate, sizeof(double), 1, file);
    fread(&initial_radius, sizeof(double), 1, file);
    fread(&max_iterations, sizeof(int), 1, file);
    
    // 创建模型
    SOMModelState* model = som_model_create(grid_width, grid_height, input_dimension,
                                           initial_learning_rate, initial_radius, max_iterations,
                                           quantum_enhanced, qubits_per_neuron);
    
    if (!model) {
        printf("无法创建SOM模型\n");
        fclose(file);
        return NULL;
    }
    
    // 读取权重
    for (int y = 0; y < grid_height; y++) {
        for (int x = 0; x < grid_width; x++) {
            fread(model->weights[y][x], sizeof(double), input_dimension, file);
        }
    }
    
    fclose(file);
    printf("SOM模型已从文件加载: %s\n", filename);
    return model;
}

// ----- QEntL模型适配器接口实现 -----

static void* som_adapter_create_model(ModelParameters* params) {
    if (!params) {
        printf("无效的模型参数\n");
        return NULL;
    }
    
    // 从参数中提取SOM特定的配置
    int grid_width = 10;  // 默认值
    int grid_height = 10;  // 默认值
    int input_dimension = 3;  // 默认值
    double learning_rate = 0.1;  // 默认值
    double radius = 5.0;  // 默认值
    int max_iterations = 1000;  // 默认值
    bool quantum_enhanced = true;  // 默认值
    int qubits_per_neuron = 2;  // 默认值
    
    // 解析参数
    for (int i = 0; i < params->count; i++) {
        if (strcmp(params->keys[i], "grid_width") == 0) {
            grid_width = atoi(params->values[i]);
        } else if (strcmp(params->keys[i], "grid_height") == 0) {
            grid_height = atoi(params->values[i]);
        } else if (strcmp(params->keys[i], "input_dimension") == 0) {
            input_dimension = atoi(params->values[i]);
        } else if (strcmp(params->keys[i], "learning_rate") == 0) {
            learning_rate = atof(params->values[i]);
        } else if (strcmp(params->keys[i], "radius") == 0) {
            radius = atof(params->values[i]);
        } else if (strcmp(params->keys[i], "max_iterations") == 0) {
            max_iterations = atoi(params->values[i]);
        } else if (strcmp(params->keys[i], "quantum_enhanced") == 0) {
            quantum_enhanced = (strcmp(params->values[i], "true") == 0 || strcmp(params->values[i], "1") == 0);
        } else if (strcmp(params->keys[i], "qubits_per_neuron") == 0) {
            qubits_per_neuron = atoi(params->values[i]);
        }
    }
    
    // 创建SOM模型
    return som_model_create(grid_width, grid_height, input_dimension, learning_rate, radius, max_iterations, quantum_enhanced, qubits_per_neuron);
}

static void som_adapter_destroy_model(void* model) {
    som_model_destroy((SOMModelState*)model);
}

static bool som_adapter_train(void* model, TrainingData* data) {
    if (!model || !data) {
        printf("无效的训练参数\n");
        return false;
    }
    
    SOMModelState* som_model = (SOMModelState*)model;
    
    // 转换训练数据格式
    if (data->type != TRAINING_DATA_NUMERIC) {
        printf("SOM仅支持数值型训练数据\n");
        return false;
    }
    
    // 检查维度匹配
    if (data->features_per_sample != som_model->input_dimension) {
        printf("训练数据维度(%d)与模型输入维度(%d)不匹配\n", 
               data->features_per_sample, som_model->input_dimension);
        return false;
    }
    
    // 如果数据格式不是double**，需要转换
    double** training_data = NULL;
    bool need_conversion = (data->format != TRAINING_DATA_FORMAT_DOUBLE_ARRAY);
    
    if (need_conversion) {
        // 分配并转换数据
        training_data = (double**)malloc(data->sample_count * sizeof(double*));
        if (!training_data) {
            printf("内存分配失败\n");
            return false;
        }
        
        for (int i = 0; i < data->sample_count; i++) {
            training_data[i] = (double*)malloc(data->features_per_sample * sizeof(double));
            if (!training_data[i]) {
                // 清理已分配的内存
                for (int j = 0; j < i; j++) {
                    free(training_data[j]);
                }
                free(training_data);
                printf("内存分配失败\n");
                return false;
            }
            
            // 根据数据格式进行转换
            switch (data->format) {
                case TRAINING_DATA_FORMAT_FLOAT_ARRAY:
                    {
                        float** float_data = (float**)data->data;
                        for (int j = 0; j < data->features_per_sample; j++) {
                            training_data[i][j] = (double)float_data[i][j];
                        }
                    }
                    break;
                    
                case TRAINING_DATA_FORMAT_INT_ARRAY:
                    {
                        int** int_data = (int**)data->data;
                        for (int j = 0; j < data->features_per_sample; j++) {
                            training_data[i][j] = (double)int_data[i][j];
                        }
                    }
                    break;
                    
                default:
                    // 不支持的格式
                    for (int j = 0; j <= i; j++) {
                        free(training_data[j]);
                    }
                    free(training_data);
                    printf("不支持的训练数据格式\n");
                    return false;
            }
        }
    } else {
        // 可以直接使用数据
        training_data = (double**)data->data;
    }
    
    // 训练模型
    bool success = som_model_train(som_model, training_data, data->sample_count);
    
    // 清理临时分配的内存
    if (need_conversion) {
        for (int i = 0; i < data->sample_count; i++) {
            free(training_data[i]);
        }
        free(training_data);
    }
    
    return success;
}

static bool som_adapter_predict(void* model, PredictionInput* input, PredictionResult* result) {
    if (!model || !input || !result) {
        printf("无效的预测参数\n");
        return false;
    }
    
    SOMModelState* som_model = (SOMModelState*)model;
    
    // 检查输入维度
    if (input->feature_count != som_model->input_dimension) {
        printf("输入维度(%d)与模型输入维度(%d)不匹配\n", 
               input->feature_count, som_model->input_dimension);
        return false;
    }
    
    // 转换输入数据
    double* input_data = (double*)malloc(input->feature_count * sizeof(double));
    if (!input_data) {
        printf("内存分配失败\n");
        return false;
    }
    
    for (int i = 0; i < input->feature_count; i++) {
        switch (input->type) {
            case PREDICTION_INPUT_DOUBLE:
                input_data[i] = ((double*)input->data)[i];
                break;
                
            case PREDICTION_INPUT_FLOAT:
                input_data[i] = (double)((float*)input->data)[i];
                break;
                
            case PREDICTION_INPUT_INT:
                input_data[i] = (double)((int*)input->data)[i];
                break;
                
            default:
                free(input_data);
                printf("不支持的输入数据类型\n");
                return false;
        }
    }
    
    // 使用SOM模型进行映射
    int mapped_x = 0, mapped_y = 0;
    bool success = som_model_map(som_model, input_data, &mapped_x, &mapped_y);
    
    free(input_data);
    
    if (!success) {
        return false;
    }
    
    // 设置预测结果
    result->type = PREDICTION_RESULT_VECTOR;
    result->vector_size = 2;  // x, y 坐标
    
    // 分配结果数组
    result->data = malloc(2 * sizeof(double));
    if (!result->data) {
        printf("内存分配失败\n");
        return false;
    }
    
    // 存储映射结果
    ((double*)result->data)[0] = (double)mapped_x;
    ((double*)result->data)[1] = (double)mapped_y;
    
    return true;
}

static bool som_adapter_save(void* model, const char* path) {
    return som_model_save((SOMModelState*)model, path);
}

static void* som_adapter_load(const char* path, ModelParameters* params) {
    // 从参数中提取是否启用量子增强
    bool quantum_enhanced = true;  // 默认值
    int qubits_per_neuron = 2;  // 默认值
    
    if (params) {
        for (int i = 0; i < params->count; i++) {
            if (strcmp(params->keys[i], "quantum_enhanced") == 0) {
                quantum_enhanced = (strcmp(params->values[i], "true") == 0 || strcmp(params->values[i], "1") == 0);
            } else if (strcmp(params->keys[i], "qubits_per_neuron") == 0) {
                qubits_per_neuron = atoi(params->values[i]);
            }
        }
    }
    
    return som_model_load(path, quantum_enhanced, qubits_per_neuron);
}

// 替换或添加: 适配器的处理事件函数，将调用som_process_integration_event
static int som_adapter_process_event(void* model_handle, IntegrationEvent* event) {
    if (!model_handle || !event) {
        return -1;
    }
    
    SOMModelState* model = (SOMModelState*)model_handle;
    return som_process_integration_event(model, event) ? 0 : -1;
}

// 确保在模型注册过程中，事件处理函数被正确链接
void initialize_som_adapter(ModelAdapter* adapter) {
    if (!adapter) return;
    
    // 设置适配器基本信息
    adapter->model_type = MODEL_SOM;
    adapter->model_id = "som_model_001";
    adapter->model_name = "自组织映射模型";
    adapter->model_version = "1.0";
    
    // 设置适配器函数
    adapter->create_model = som_adapter_create_model;
    adapter->destroy_model = som_adapter_destroy_model;
    adapter->train = som_adapter_train;
    adapter->predict = som_adapter_predict;
    adapter->save = som_adapter_save;
    adapter->load = som_adapter_load;
    
    // 确保事件处理函数被正确设置
    adapter->process_event = som_adapter_process_event;
    
    printf("SOM适配器已初始化，支持知识缺口检测和Claude交互\n");
} 