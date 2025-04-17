/**
 * REF适配器实现文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月22日
 * 
 * 描述：参考框架(Reference Framework)模型适配器
 *      将基于参考的模型集成到QEntL量子环境中，实现知识库与量子计算的结合
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "quantum_model_integration.h"
#include "../../quantum_state.h"
#include "../../quantum_entanglement.h"
#include "claude_adapter.h" // 添加Claude适配器头文件

// 参考条目结构
typedef struct {
    char* key;              // 唯一标识符
    char* content;          // 参考内容
    double* embedding;      // 向量嵌入表示
    int embedding_dim;      // 嵌入维度
    double* quantum_phase;  // 量子相位表示
    int quantum_bits;       // 量子比特数
} ReferenceEntry;

// REF模型状态
typedef struct {
    // 参考库
    ReferenceEntry** entries;
    int entry_count;
    int capacity;
    
    // 嵌入配置
    int embedding_dimension;
    bool quantum_enhanced;
    int quantum_bits_per_entry;
    
    // 量子增强搜索
    QuantumState* search_state;
    EntanglementNetwork* entanglement_network;
    
    // 相似度阈值
    double similarity_threshold;
    
    // 索引结构（简单实现）
    int index_type;  // 0: 线性, 1: 分层, 2: 量子

    // 知识管理 - 新增
    double knowledge_confidence;  // 知识信心度
    char* recent_queries[10];     // 最近的查询记录
    int query_count;              // 查询计数
    QuantumState* knowledge_states[20]; // 知识量子态
    int knowledge_count;          // 知识计数
    char last_query_topic[128];   // 上次查询主题
} REFModelState;

// 前向声明
static REFModelState* ref_model_create(int embedding_dim, bool quantum_enhanced, 
                                     int quantum_bits, double similarity_threshold);
static void ref_model_destroy(REFModelState* model);
static int ref_detect_knowledge_gap(REFModelState* model, const char* query, double* confidence);
static QuantumState* ref_ask_claude(const char* query);
static int ref_integrate_knowledge(REFModelState* model, QuantumState* knowledge_state);
static EntanglementChannel* ref_adapter_create_entanglement_channel(REFModelState* model, QuantumState* state, QuantumModelType target_model, const char* target_model_id);
static EntanglementChannel* ref_create_knowledge_sharing_channel(QuantumState* state);
static int ref_process_integration_event(REFModelState* model, IntegrationEvent* event);

// 初始化REF模型 - 修改以添加知识管理初始化
static REFModelState* ref_model_create(int embedding_dim, bool quantum_enhanced, 
                                     int quantum_bits, double similarity_threshold) {
    REFModelState* model = (REFModelState*)malloc(sizeof(REFModelState));
    if (!model) {
        printf("内存分配失败: 无法创建REF模型状态\n");
        return NULL;
    }
    
    // 初始化基本参数
    model->embedding_dimension = embedding_dim;
    model->quantum_enhanced = quantum_enhanced;
    model->quantum_bits_per_entry = quantum_bits;
    model->similarity_threshold = similarity_threshold;
    model->entry_count = 0;
    model->capacity = 100;  // 初始容量
    model->index_type = quantum_enhanced ? 2 : 0;  // 量子增强则使用量子索引
    
    // 初始化知识管理
    model->knowledge_confidence = 0.6; // 初始置信度
    model->query_count = 0;
    model->knowledge_count = 0;
    memset(model->last_query_topic, 0, sizeof(model->last_query_topic));
    
    for (int i = 0; i < 10; i++) {
        model->recent_queries[i] = NULL;
    }
    
    for (int i = 0; i < 20; i++) {
        model->knowledge_states[i] = NULL;
    }
    
    // 分配参考条目数组
    model->entries = (ReferenceEntry**)malloc(model->capacity * sizeof(ReferenceEntry*));
    if (!model->entries) {
        printf("内存分配失败: 无法为参考条目分配内存\n");
        free(model);
        return NULL;
    }
    
    // 如果是量子增强模式，创建量子状态
    if (quantum_enhanced) {
        // 创建搜索状态
        model->search_state = create_quantum_state(quantum_bits);
        if (!model->search_state) {
            printf("无法创建量子搜索状态\n");
            free(model->entries);
            free(model);
            return NULL;
        }
        
        // 创建纠缠网络
        model->entanglement_network = create_entanglement_network(quantum_bits);
        if (!model->entanglement_network) {
            printf("无法创建纠缠网络\n");
            destroy_quantum_state(model->search_state);
            free(model->entries);
            free(model);
            return NULL;
        }
    } else {
        model->search_state = NULL;
        model->entanglement_network = NULL;
    }
    
    printf("REF模型已创建: 嵌入维度 %d, 量子增强 %s\n", 
           embedding_dim, quantum_enhanced ? "是" : "否");
    return model;
}

// 销毁REF模型 - 修改以释放知识管理资源
static void ref_model_destroy(REFModelState* model) {
    if (!model) return;
    
    // 释放所有参考条目
    for (int i = 0; i < model->entry_count; i++) {
        destroy_reference_entry(model->entries[i]);
    }
    free(model->entries);
    
    // 释放量子资源
    if (model->quantum_enhanced) {
        if (model->search_state) {
            destroy_quantum_state(model->search_state);
        }
        if (model->entanglement_network) {
            destroy_entanglement_network(model->entanglement_network);
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
    printf("REF模型已销毁\n");
}

// ... 其它原有函数 ...

// 新增: 检测知识缺口
static int ref_detect_knowledge_gap(REFModelState* model, const char* query, double* confidence) {
    if (!model || !query || !confidence) {
        return 0;
    }
    
    // 计算对该查询的置信度
    *confidence = model->knowledge_confidence;
    
    // 检查知识库中是否已有相似查询
    for (int i = 0; i < model->query_count; i++) {
        if (model->recent_queries[i] && 
            strstr(model->recent_queries[i], query) != NULL) {
            // 找到相似查询，提高置信度
            *confidence += 0.1;
            break;
        }
    }
    
    // 如果相似度低于阈值，认为存在知识缺口
    if (*confidence < 0.75) {
        printf("REF模型检测到知识缺口，置信度: %.2f\n", *confidence);
        
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
        
        // 更新上次查询主题
        strncpy(model->last_query_topic, query, sizeof(model->last_query_topic)-1);
        model->last_query_topic[sizeof(model->last_query_topic)-1] = '\0';
        
        return 1; // 存在知识缺口
    }
    
    return 0; // 没有知识缺口
}

// 新增: 向Claude提问
static QuantumState* ref_ask_claude(const char* query) {
    if (!query) {
        return NULL;
    }
    
    printf("REF模型向Claude提问: %s\n", query);
    
    // 调用Claude适配器处理文本
    char* claude_response = claude_adapter_process_text(query, 
        "你是一个参考框架模型的知识助手。请以清晰、准确的方式回答问题，侧重于知识检索与参考的见解。");
    
    if (!claude_response) {
        printf("无法从Claude获取响应\n");
        return NULL;
    }
    
    printf("收到Claude响应\n");
    
    // 将Claude响应转换为量子状态
    QuantumState* knowledge_state = claude_adapter_generate_quantum_state(
        claude_response, "ref_new_knowledge");
    
    // 释放响应内存
    free(claude_response);
    
    return knowledge_state;
}

// 新增: 整合知识到REF模型
static int ref_integrate_knowledge(REFModelState* model, QuantumState* knowledge_state) {
    if (!model || !knowledge_state) {
        return 0;
    }
    
    printf("REF模型整合新知识: %s\n", knowledge_state->id);
    
    // 将知识状态添加到知识库
    if (model->knowledge_count < 20) {
        model->knowledge_states[model->knowledge_count] = knowledge_state;
        model->knowledge_count++;
        
        // 提高知识置信度
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
    
    // 尝试从知识中提取参考条目
    if (model->last_query_topic[0] != '\0') {
        // 从知识状态中提取概率最高的叠加态作为潜在参考条目
        QuantumSuperposition* best_superposition = NULL;
        double max_prob = 0.0;
        
        for (int i = 0; i < knowledge_state->superposition_count; i++) {
            if (knowledge_state->superpositions[i].probability > max_prob) {
                max_prob = knowledge_state->superpositions[i].probability;
                best_superposition = &knowledge_state->superpositions[i];
            }
        }
        
        if (best_superposition && max_prob > 0.5) {
            // 创建新的参考条目
            char key[128];
            sprintf(key, "claude_ref_%d", model->entry_count + 1);
            
            // 生成简单嵌入
            double* embedding = (double*)malloc(model->embedding_dimension * sizeof(double));
            if (embedding) {
                // 初始化嵌入
                for (int i = 0; i < model->embedding_dimension; i++) {
                    embedding[i] = ((double)rand() / RAND_MAX) * max_prob;
                }
                
                // 添加参考条目
                ref_model_add_entry(model, key, best_superposition->state, embedding);
                
                free(embedding);
            }
        }
    }
    
    return 1;
}

// 新增: 创建REF适配器与其他模型之间的纠缠信道
static EntanglementChannel* ref_adapter_create_entanglement_channel(REFModelState* model, QuantumState* state, QuantumModelType target_model, const char* target_model_id) {
    if (!model || !state || !target_model_id) {
        return NULL;
    }
    
    printf("REF适配器创建与%s(%d)模型的纠缠信道\n", target_model_id, target_model);
    
    // 创建一个唯一的信道ID
    char channel_id[128];
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    uint64_t timestamp = (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
    
    snprintf(channel_id, sizeof(channel_id), "ref_to_%s_%lu", 
             target_model_id, timestamp);
    
    // 创建纠缠信道
    EntanglementChannel* channel = quantum_entanglement_create(
        channel_id, 
        "ref_model_001",        // 源模型ID 
        MODEL_REF,              // 源模型类型
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
    quantum_entanglement_set_property(channel, "embedding_dimension", 
                                     (char*)model->embedding_dimension); // 添加REF特有属性
    
    // 添加量子基因编码
    char gene_code[128];
    sprintf(gene_code, "QG-ENTANGLE-REF-%d-%lu", target_model, timestamp);
    quantum_entanglement_add_gene(channel, gene_code);
    
    // 将状态附加到信道
    quantum_entanglement_attach_state(channel, state);
    
    // 通知集成管理器
    IntegrationManager* manager = get_default_integration_manager();
    if (manager) {
        // 创建纠缠创建事件
        IntegrationEvent* event = create_integration_event(
            EVENT_ENTANGLEMENT_CREATED, 
            "ref_model_001", 
            MODEL_REF, 
            "REF模型创建了与其他模型的纠缠信道"
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
    
    printf("REF适配器成功创建纠缠信道: %s\n", channel_id);
    
    return channel;
}

// 修改: 使用新的ref_adapter_create_entanglement_channel函数创建知识共享信道
static EntanglementChannel* ref_create_knowledge_sharing_channel(QuantumState* state) {
    if (!state) {
        return NULL;
    }
    
    printf("REF模型创建知识共享纠缠信道\n");
    
    // 获取当前REF模型状态 - 此处应该从适配器获取，简化实现
    REFModelState* current_model = NULL; // 此处简化，实际应从全局适配器获取
    // 假设从全局适配器获取模型状态的函数
    // current_model = get_current_ref_model_state();
    
    if (!current_model) {
        // 如果无法获取当前模型，退回到使用Claude适配器
        return claude_adapter_create_entanglement_channel(state);
    }
    
    // 创建与QSM模型的纠缠信道
    EntanglementChannel* qsm_channel = ref_adapter_create_entanglement_channel(
        current_model, state, MODEL_QSM, "qsm_model_001");
    
    // 创建与SOM模型的纠缠信道
    EntanglementChannel* som_channel = ref_adapter_create_entanglement_channel(
        current_model, state, MODEL_SOM, "som_model_001");
    
    // 创建与WeQ模型的纠缠信道
    EntanglementChannel* weq_channel = ref_adapter_create_entanglement_channel(
        current_model, state, MODEL_WEQ, "weq_model_001");
    
    // 打印成功信息
    printf("已创建知识共享纠缠信道，强度: %.2f\n", qsm_channel ? qsm_channel->strength : 0.0);
    
    // 返回QSM信道作为主要信道
    return qsm_channel;
}

// 新增: 处理集成事件
static int ref_process_integration_event(REFModelState* model, IntegrationEvent* event) {
    if (!model || !event) {
        return -1;
    }
    
    printf("REF模型处理集成事件: 类型=%d\n", event->type);
    
    switch (event->type) {
        case EVENT_STATE_CHANGED: {
            // 处理状态变化事件，可能需要扩展参考知识库
            if (event->source_model != MODEL_REF) {
                // 其他模型的状态变化，考虑将其作为新的参考
                double confidence = 0.0;
                if (ref_detect_knowledge_gap(model, "如何整合新的状态信息作为参考条目?", &confidence)) {
                    QuantumState* knowledge = ref_ask_claude("如何在参考框架中有效整合来自其他模型的新状态作为可检索的参考条目?");
                    if (knowledge) {
                        ref_integrate_knowledge(model, knowledge);
                        ref_create_knowledge_sharing_channel(knowledge);
                    }
                }
            }
            break;
        }
        
        case EVENT_ENTANGLEMENT_CREATED: {
            // 新的纠缠关系建立，可能影响参考搜索
            if (model->quantum_enhanced) {
                printf("检测到新的纠缠关系，调整REF量子搜索参数\n");
                // 实际调整逻辑
            }
            break;
        }
        
        case EVENT_CUSTOM: {
            // 检查是否是知识缺口事件
            if (event->event_data && strstr((const char*)event->event_data, "KNOWLEDGE_GAP")) {
                printf("REF检测到知识缺口事件\n");
                
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
                        QuantumState* knowledge = ref_ask_claude(query);
                        if (knowledge) {
                            // 整合知识并创建参考条目
                            ref_integrate_knowledge(model, knowledge);
                            
                            // 在模型之间共享这个知识
                            ref_create_knowledge_sharing_channel(knowledge);
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
    
    return 0;
}

// 修改: 在搜索过程中添加知识缺口检测
static int ref_model_search_linear(REFModelState* model, double* query_embedding, int max_results, 
                                  ReferenceEntry** results, double* similarities) {
    // ... 原有搜索代码前部分 ...
    
    // 如果搜索结果不理想，触发知识缺口处理
    int found_count = 0; // 假设这是原代码中计算的找到结果数量
    
    // 检查搜索结果是否满足需求
    if (found_count < max_results / 2) {
        // 搜索结果不足，可能存在知识缺口
        double confidence = 0.0;
        char query[256];
        sprintf(query, "如何优化参考框架搜索以提高结果数量和质量?");
        
        if (ref_detect_knowledge_gap(model, query, &confidence)) {
            QuantumState* knowledge = ref_ask_claude(
                "请提供优化参考框架模型搜索算法的建议，特别是在结果稀疏情况下如何扩展相关匹配。");
            
            if (knowledge) {
                ref_integrate_knowledge(model, knowledge);
                // 不需要重新搜索，但可以标记下次搜索使用新知识
            }
        }
    }
    
    return found_count;
}

// 替换: 适配器的处理事件函数
static int ref_adapter_process_event(void* model_handle, IntegrationEvent* event) {
    if (!model_handle || !event) {
        return -1;
    }
    
    REFModelState* model = (REFModelState*)model_handle;
    return ref_process_integration_event(model, event);
}

// 确保在适配器初始化过程中，事件处理函数被正确设置
void initialize_ref_adapter(ModelAdapter* adapter) {
    if (!adapter) return;
    
    // 设置适配器基本信息
    adapter->model_type = MODEL_REF;
    adapter->model_id = "ref_model_001";
    adapter->model_name = "参考框架模型";
    adapter->model_version = "1.0";
    
    // ... 其他原有代码 ...
    
    // 确保事件处理函数被正确设置
    adapter->process_event = ref_adapter_process_event;
    
    printf("REF适配器已初始化，支持知识缺口检测和Claude交互\n");
}

// 向模型添加参考条目
static bool ref_model_add_entry(REFModelState* model, const char* key, const char* content, double* embedding) {
    if (!model || !key || !content || !embedding) {
        printf("无效的参数\n");
        return false;
    }
    
    // 检查是否需要扩容
    if (model->entry_count >= model->capacity) {
        int new_capacity = model->capacity * 2;
        ReferenceEntry** new_entries = (ReferenceEntry**)realloc(model->entries, 
                                                           new_capacity * sizeof(ReferenceEntry*));
        if (!new_entries) {
            printf("内存分配失败: 无法扩展参考条目数组\n");
            return false;
        }
        
        model->entries = new_entries;
        model->capacity = new_capacity;
    }
    
    // 创建新条目
    ReferenceEntry* entry = create_reference_entry(key, content, embedding, 
                                               model->embedding_dimension,
                                               model->quantum_bits_per_entry);
    if (!entry) {
        return false;
    }
    
    // 添加到模型
    model->entries[model->entry_count++] = entry;
    
    // 如果是量子增强模式，更新纠缠网络
    if (model->quantum_enhanced && model->entanglement_network) {
        // 将新条目与现有条目建立纠缠关系
        for (int i = 0; i < model->entry_count - 1; i++) {
            ReferenceEntry* existing_entry = model->entries[i];
            
            // 计算相似度
            double similarity = 0.0;
            for (int j = 0; j < model->embedding_dimension; j++) {
                similarity += entry->embedding[j] * existing_entry->embedding[j];
            }
            
            // 相似度归一化
            similarity = (similarity + 1.0) / 2.0;  // 映射到[0,1]范围
            
            // 如果相似度较高，建立纠缠
            if (similarity > model->similarity_threshold) {
                // 基于相似度设置纠缠强度
                apply_controlled_entanglement(model->entanglement_network, 
                                           i * model->quantum_bits_per_entry, 
                                           (model->entry_count - 1) * model->quantum_bits_per_entry,
                                           similarity);
            }
        }
    }
    
    return true;
}

// 计算两个向量的余弦相似度
static double cosine_similarity(double* vec1, double* vec2, int dim) {
    double dot_product = 0.0;
    double norm1 = 0.0;
    double norm2 = 0.0;
    
    for (int i = 0; i < dim; i++) {
        dot_product += vec1[i] * vec2[i];
        norm1 += vec1[i] * vec1[i];
        norm2 += vec2[i] * vec2[i];
    }
    
    norm1 = sqrt(norm1);
    norm2 = sqrt(norm2);
    
    if (norm1 == 0.0 || norm2 == 0.0) {
        return 0.0;
    }
    
    return dot_product / (norm1 * norm2);
}

// 准备量子搜索状态
static void prepare_quantum_search_state(REFModelState* model, double* query_embedding) {
    if (!model->quantum_enhanced || !model->search_state) {
        return;
    }
    
    // 重置搜索状态
    reset_quantum_state(model->search_state);
    
    // 使用Hadamard门创建叠加态
    for (int i = 0; i < model->quantum_bits_per_entry; i++) {
        apply_hadamard_gate(model->search_state, i);
    }
    
    // 根据查询嵌入应用相位旋转
    for (int i = 0; i < model->embedding_dimension && i < model->quantum_bits_per_entry; i++) {
        // 将嵌入值映射到相位角度
        double phase = fmod(query_embedding[i] * M_PI * 2, 2 * M_PI);
        if (phase < 0) {
            phase += 2 * M_PI;
        }
        
        // 应用相位旋转
        apply_phase_shift(model->search_state, i, phase);
    }
}

// 搜索最相关的参考条目 (经典方法)
static ReferenceEntry** ref_model_search_classic(REFModelState* model, double* query_embedding, 
                                               int max_results, double* similarities) {
    ReferenceEntry** results = (ReferenceEntry**)malloc(max_results * sizeof(ReferenceEntry*));
    if (!results) {
        printf("内存分配失败: 无法分配搜索结果空间\n");
        return NULL;
    }
    
    // 初始化结果
    for (int i = 0; i < max_results; i++) {
        results[i] = NULL;
        similarities[i] = -1.0;
    }
    
    // 线性扫描所有条目，计算相似度
    for (int i = 0; i < model->entry_count; i++) {
        double similarity = cosine_similarity(query_embedding, model->entries[i]->embedding, 
                                            model->embedding_dimension);
        
        // 检查是否应该加入结果集
        for (int j = 0; j < max_results; j++) {
            if (similarity > similarities[j]) {
                // 移动后续结果
                for (int k = max_results - 1; k > j; k--) {
                    results[k] = results[k - 1];
                    similarities[k] = similarities[k - 1];
                }
                
                // 插入新结果
                results[j] = model->entries[i];
                similarities[j] = similarity;
                break;
            }
        }
    }
    
    return results;
}

// 搜索最相关的参考条目 (量子增强方法)
static ReferenceEntry** ref_model_search_quantum(REFModelState* model, double* query_embedding,
                                              int max_results, double* similarities) {
    // 准备量子搜索状态
    prepare_quantum_search_state(model, query_embedding);
    
    // 应用Grover迭代操作来放大可能的匹配结果
    // 这里是简化的示例实现，实际量子搜索算法会更复杂
    int iterations = (int)sqrt(model->entry_count);
    for (int i = 0; i < iterations; i++) {
        // 实现Grover迭代
        // 1. 应用Oracle (将与查询匹配的状态标记为负相位)
        for (int j = 0; j < model->entry_count; j++) {
            double similarity = cosine_similarity(query_embedding, model->entries[j]->embedding, 
                                                model->embedding_dimension);
            
            if (similarity > model->similarity_threshold) {
                // 标记匹配的状态
                int base_qubit = j * model->quantum_bits_per_entry;
                apply_z_gate(model->search_state, base_qubit);
            }
        }
        
        // 2. 应用扩散算子 (围绕平均值反射)
        // 先把所有量子位翻转到H基态
        for (int q = 0; q < model->quantum_bits_per_entry; q++) {
            apply_hadamard_gate(model->search_state, q);
        }
        
        // 除了|0>态，所有态的相位翻转
        apply_z_gate(model->search_state, 0);
        
        // 再转回来
        for (int q = 0; q < model->quantum_bits_per_entry; q++) {
            apply_hadamard_gate(model->search_state, q);
        }
    }
    
    // 测量量子状态，得到概率分布
    double* probabilities = measure_probabilities(model->search_state);
    if (!probabilities) {
        printf("无法获取量子状态概率分布\n");
        return ref_model_search_classic(model, query_embedding, max_results, similarities);
    }
    
    // 分配结果数组
    ReferenceEntry** results = (ReferenceEntry**)malloc(max_results * sizeof(ReferenceEntry*));
    if (!results) {
        printf("内存分配失败: 无法分配搜索结果空间\n");
        free(probabilities);
        return NULL;
    }
    
    // 初始化结果
    for (int i = 0; i < max_results; i++) {
        results[i] = NULL;
        similarities[i] = -1.0;
    }
    
    // 从概率分布中找出最可能的结果
    int states = 1 << model->quantum_bits_per_entry;
    for (int i = 0; i < model->entry_count; i++) {
        int base_state = i % states;  // 简化映射
        double probability = probabilities[base_state];
        
        // 也计算经典相似度作为参考
        double classic_similarity = cosine_similarity(query_embedding, model->entries[i]->embedding, 
                                                  model->embedding_dimension);
        
        // 组合量子概率和经典相似度
        double combined_score = 0.7 * probability + 0.3 * classic_similarity;
        
        // 检查是否应该加入结果集
        for (int j = 0; j < max_results; j++) {
            if (combined_score > similarities[j]) {
                // 移动后续结果
                for (int k = max_results - 1; k > j; k--) {
                    results[k] = results[k - 1];
                    similarities[k] = similarities[k - 1];
                }
                
                // 插入新结果
                results[j] = model->entries[i];
                similarities[j] = combined_score;
                break;
            }
        }
    }
    
    free(probabilities);
    return results;
}

// 搜索最相关的参考条目
static ReferenceEntry** ref_model_search(REFModelState* model, double* query_embedding, 
                                      int max_results, double* similarities) {
    if (!model || !query_embedding || max_results <= 0 || !similarities) {
        printf("无效的搜索参数\n");
        return NULL;
    }
    
    // 如果没有条目，直接返回空结果
    if (model->entry_count == 0) {
        ReferenceEntry** empty_results = (ReferenceEntry**)malloc(max_results * sizeof(ReferenceEntry*));
        if (empty_results) {
            for (int i = 0; i < max_results; i++) {
                empty_results[i] = NULL;
                similarities[i] = 0.0;
            }
        }
        return empty_results;
    }
    
    // 根据模型配置选择搜索方法
    if (model->quantum_enhanced && model->search_state) {
        return ref_model_search_quantum(model, query_embedding, max_results, similarities);
    } else {
        return ref_model_search_classic(model, query_embedding, max_results, similarities);
    }
}

// 保存REF模型到文件
static bool ref_model_save(REFModelState* model, const char* filename) {
    if (!model || !filename) {
        printf("无效的保存参数\n");
        return false;
    }
    
    FILE* file = fopen(filename, "wb");
    if (!file) {
        printf("无法打开文件进行写入: %s\n", filename);
        return false;
    }
    
    // 写入模型配置
    fwrite(&model->embedding_dimension, sizeof(int), 1, file);
    fwrite(&model->quantum_enhanced, sizeof(bool), 1, file);
    fwrite(&model->quantum_bits_per_entry, sizeof(int), 1, file);
    fwrite(&model->similarity_threshold, sizeof(double), 1, file);
    fwrite(&model->entry_count, sizeof(int), 1, file);
    
    // 写入所有参考条目
    for (int i = 0; i < model->entry_count; i++) {
        ReferenceEntry* entry = model->entries[i];
        
        // 写入键
        int key_length = strlen(entry->key) + 1;
        fwrite(&key_length, sizeof(int), 1, file);
        fwrite(entry->key, sizeof(char), key_length, file);
        
        // 写入内容
        int content_length = strlen(entry->content) + 1;
        fwrite(&content_length, sizeof(int), 1, file);
        fwrite(entry->content, sizeof(char), content_length, file);
        
        // 写入嵌入
        fwrite(entry->embedding, sizeof(double), model->embedding_dimension, file);
        
        // 写入量子相位
        fwrite(entry->quantum_phase, sizeof(double), model->quantum_bits_per_entry, file);
    }
    
    fclose(file);
    printf("REF模型已保存到文件: %s\n", filename);
    return true;
}

// 从文件加载REF模型
static REFModelState* ref_model_load(const char* filename, bool quantum_enhanced) {
    if (!filename) {
        printf("无效的文件名\n");
        return NULL;
    }
    
    FILE* file = fopen(filename, "rb");
    if (!file) {
        printf("无法打开文件进行读取: %s\n", filename);
        return NULL;
    }
    
    // 读取模型配置
    int embedding_dimension;
    bool original_quantum_enhanced;
    int quantum_bits;
    double similarity_threshold;
    int entry_count;
    
    fread(&embedding_dimension, sizeof(int), 1, file);
    fread(&original_quantum_enhanced, sizeof(bool), 1, file);
    fread(&quantum_bits, sizeof(int), 1, file);
    fread(&similarity_threshold, sizeof(double), 1, file);
    fread(&entry_count, sizeof(int), 1, file);
    
    // 创建模型
    REFModelState* model = ref_model_create(embedding_dimension, quantum_enhanced, 
                                          quantum_bits, similarity_threshold);
    
    if (!model) {
        printf("无法创建REF模型\n");
        fclose(file);
        return NULL;
    }
    
    // 读取所有参考条目
    for (int i = 0; i < entry_count; i++) {
        // 读取键
        int key_length;
        fread(&key_length, sizeof(int), 1, file);
        char* key = (char*)malloc(key_length);
        if (!key) {
            printf("内存分配失败: 无法分配键内存\n");
            ref_model_destroy(model);
            fclose(file);
            return NULL;
        }
        fread(key, sizeof(char), key_length, file);
        
        // 读取内容
        int content_length;
        fread(&content_length, sizeof(int), 1, file);
        char* content = (char*)malloc(content_length);
        if (!content) {
            printf("内存分配失败: 无法分配内容内存\n");
            free(key);
            ref_model_destroy(model);
            fclose(file);
            return NULL;
        }
        fread(content, sizeof(char), content_length, file);
        
        // 读取嵌入
        double* embedding = (double*)malloc(embedding_dimension * sizeof(double));
        if (!embedding) {
            printf("内存分配失败: 无法分配嵌入内存\n");
            free(content);
            free(key);
            ref_model_destroy(model);
            fclose(file);
            return NULL;
        }
        fread(embedding, sizeof(double), embedding_dimension, file);
        
        // 读取量子相位 (但不使用，重新生成)
        double* quantum_phase = (double*)malloc(quantum_bits * sizeof(double));
        if (quantum_phase) {
            fread(quantum_phase, sizeof(double), quantum_bits, file);
            free(quantum_phase);  // 不使用，重新生成
        } else {
            // 跳过相位数据
            fseek(file, quantum_bits * sizeof(double), SEEK_CUR);
        }
        
        // 添加到模型
        ref_model_add_entry(model, key, content, embedding);
        
        // 清理临时内存
        free(embedding);
        free(content);
        free(key);
    }
    
    fclose(file);
    printf("REF模型已从文件加载: %s, 条目数: %d\n", filename, model->entry_count);
    return model;
}

// ----- QEntL模型适配器接口实现 -----

static void* ref_adapter_create_model(ModelParameters* params) {
    if (!params) {
        printf("无效的模型参数\n");
        return NULL;
    }
    
    // 从参数中提取REF特定的配置
    int embedding_dim = 256;  // 默认值
    bool quantum_enhanced = true;  // 默认值
    int quantum_bits = 8;  // 默认值
    double similarity_threshold = 0.6;  // 默认值
    
    // 解析参数
    for (int i = 0; i < params->count; i++) {
        if (strcmp(params->keys[i], "embedding_dimension") == 0) {
            embedding_dim = atoi(params->values[i]);
        } else if (strcmp(params->keys[i], "quantum_enhanced") == 0) {
            quantum_enhanced = (strcmp(params->values[i], "true") == 0 || strcmp(params->values[i], "1") == 0);
        } else if (strcmp(params->keys[i], "quantum_bits") == 0) {
            quantum_bits = atoi(params->values[i]);
        } else if (strcmp(params->keys[i], "similarity_threshold") == 0) {
            similarity_threshold = atof(params->values[i]);
        }
    }
    
    // 创建REF模型
    return ref_model_create(embedding_dim, quantum_enhanced, quantum_bits, similarity_threshold);
}

static void ref_adapter_destroy_model(void* model) {
    ref_model_destroy((REFModelState*)model);
}

static bool ref_adapter_train(void* model, TrainingData* data) {
    if (!model || !data) {
        printf("无效的训练参数\n");
        return false;
    }
    
    REFModelState* ref_model = (REFModelState*)model;
    
    // 检查是否是文本和嵌入训练数据
    if (data->type != TRAINING_DATA_TEXT_WITH_EMBEDDING) {
        printf("REF仅支持带嵌入的文本训练数据\n");
        return false;
    }
    
    // 解析训练数据
    TextEmbeddingData* text_data = (TextEmbeddingData*)data->data;
    if (!text_data) {
        printf("无效的文本嵌入数据\n");
        return false;
    }
    
    // 检查嵌入维度匹配
    if (text_data->embedding_dim != ref_model->embedding_dimension) {
        printf("训练数据嵌入维度(%d)与模型嵌入维度(%d)不匹配\n", 
              text_data->embedding_dim, ref_model->embedding_dimension);
        return false;
    }
    
    // 添加所有参考条目
    bool all_success = true;
    for (int i = 0; i < text_data->entry_count; i++) {
        if (!ref_model_add_entry(ref_model, 
                              text_data->keys[i], 
                              text_data->contents[i], 
                              text_data->embeddings[i])) {
            printf("添加参考条目 '%s' 失败\n", text_data->keys[i]);
            all_success = false;
        }
    }
    
    return all_success;
}

static bool ref_adapter_predict(void* model, PredictionInput* input, PredictionResult* result) {
    if (!model || !input || !result) {
        printf("无效的预测参数\n");
        return false;
    }
    
    REFModelState* ref_model = (REFModelState*)model;
    
    // 检查输入类型
    if (input->type != PREDICTION_INPUT_DOUBLE && input->type != PREDICTION_INPUT_EMBEDDING) {
        printf("REF仅支持双精度或嵌入类型的输入\n");
        return false;
    }
    
    // 获取嵌入向量
    double* query_embedding = NULL;
    
    if (input->type == PREDICTION_INPUT_DOUBLE) {
        // 直接使用输入作为嵌入
        query_embedding = (double*)input->data;
        
        // 检查维度匹配
        if (input->feature_count != ref_model->embedding_dimension) {
            printf("输入嵌入维度(%d)与模型嵌入维度(%d)不匹配\n", 
                  input->feature_count, ref_model->embedding_dimension);
            return false;
        }
    } else if (input->type == PREDICTION_INPUT_EMBEDDING) {
        // 从嵌入输入中提取
        EmbeddingInput* embedding_input = (EmbeddingInput*)input->data;
        
        if (embedding_input->dimension != ref_model->embedding_dimension) {
            printf("输入嵌入维度(%d)与模型嵌入维度(%d)不匹配\n", 
                  embedding_input->dimension, ref_model->embedding_dimension);
            return false;
        }
        
        query_embedding = embedding_input->values;
    }
    
    if (!query_embedding) {
        printf("无法获取查询嵌入\n");
        return false;
    }
    
    // 设置默认搜索结果数
    int max_results = 5;
    if (input->param_count > 0) {
        for (int i = 0; i < input->param_count; i++) {
            if (strcmp(input->param_keys[i], "max_results") == 0) {
                max_results = atoi(input->param_values[i]);
                break;
            }
        }
    }
    
    // 分配相似度数组
    double* similarities = (double*)malloc(max_results * sizeof(double));
    if (!similarities) {
        printf("内存分配失败: 无法分配相似度数组\n");
        return false;
    }
    
    // 搜索相关条目
    ReferenceEntry** search_results = ref_model_search(ref_model, query_embedding, max_results, similarities);
    
    if (!search_results) {
        free(similarities);
        return false;
    }
    
    // 统计结果数量
    int result_count = 0;
    for (int i = 0; i < max_results; i++) {
        if (search_results[i] != NULL && similarities[i] > 0) {
            result_count++;
        } else {
            break;
        }
    }
    
    // 设置预测结果
    result->type = PREDICTION_RESULT_REFERENCE;
    
    // 创建参考结果结构
    ReferenceResult* ref_result = (ReferenceResult*)malloc(sizeof(ReferenceResult));
    if (!ref_result) {
        printf("内存分配失败: 无法创建参考结果结构\n");
        free(search_results);
        free(similarities);
        return false;
    }
    
    ref_result->entry_count = result_count;
    
    // 分配结果数组
    ref_result->keys = (char**)malloc(result_count * sizeof(char*));
    ref_result->contents = (char**)malloc(result_count * sizeof(char*));
    ref_result->scores = (double*)malloc(result_count * sizeof(double));
    
    if (!ref_result->keys || !ref_result->contents || !ref_result->scores) {
        printf("内存分配失败: 无法为结果分配内存\n");
        if (ref_result->keys) free(ref_result->keys);
        if (ref_result->contents) free(ref_result->contents);
        if (ref_result->scores) free(ref_result->scores);
        free(ref_result);
        free(search_results);
        free(similarities);
        return false;
    }
    
    // 复制结果
    for (int i = 0; i < result_count; i++) {
        ref_result->keys[i] = strdup(search_results[i]->key);
        ref_result->contents[i] = strdup(search_results[i]->content);
        ref_result->scores[i] = similarities[i];
    }
    
    result->data = ref_result;
    
    // 清理临时内存
    free(search_results);
    free(similarities);
    
    return true;
}

static bool ref_adapter_save(void* model, const char* path) {
    return ref_model_save((REFModelState*)model, path);
}

static void* ref_adapter_load(const char* path, ModelParameters* params) {
    // 从参数中提取是否启用量子增强
    bool quantum_enhanced = true;  // 默认值
    
    if (params) {
        for (int i = 0; i < params->count; i++) {
            if (strcmp(params->keys[i], "quantum_enhanced") == 0) {
                quantum_enhanced = (strcmp(params->values[i], "true") == 0 || strcmp(params->values[i], "1") == 0);
            }
        }
    }
    
    return ref_model_load(path, quantum_enhanced);
}

// 初始化REF适配器
void initialize_ref_adapter(ModelAdapter* adapter) {
    if (!adapter) return;
    
    // 设置适配器信息
    strcpy(adapter->name, "REF");
    strcpy(adapter->version, "1.0");
    strcpy(adapter->description, "参考框架(Reference Framework)模型适配器");
    
    // 设置适配器函数
    adapter->create_model = ref_adapter_create_model;
    adapter->destroy_model = ref_adapter_destroy_model;
    adapter->train = ref_adapter_train;
    adapter->predict = ref_adapter_predict;
    adapter->save = ref_adapter_save;
    adapter->load = ref_adapter_load;
    
    printf("REF适配器已初始化\n");
} 