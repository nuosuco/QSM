/**
 * QSM（量子叠加模型）适配器实现
 * 
 * 为量子叠加模型提供集成框架的适配实现，使QSM能与其他模型进行状态同步和事件交互。
 * 
 * 作者: QEntL核心开发团队
 * 日期: 2024-05-21
 * 版本: 1.0
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "quantum_model_integration.h"
#include "../../quantum_state.h"
#include "../../quantum_entanglement.h"
#include "../../quantum_field.h"
#include "claude_adapter.h" // 添加Claude适配器头文件

// QSM模型状态
typedef struct {
    void* quantum_state;       // 量子状态指针
    size_t state_size;         // 状态大小
    uint64_t last_updated;     // 上次更新时间戳
    int is_entangled;          // 是否已纠缠
    
    // 知识库状态
    double knowledge_confidence;  // 知识确信度
    char* recent_queries[10];     // 最近10个查询
    int query_count;              // 查询计数
    QuantumState* knowledge_states[20]; // 知识量子态数组
    int knowledge_count;          // 知识计数
} QsmModelState;

// QSM适配器内部状态
typedef struct {
    int initialized;                // 是否已初始化
    QsmModelState state;            // 模型状态
    IntegrationEvent* event_buffer; // 事件缓冲区
    size_t event_buffer_size;       // 缓冲区大小
    int subscribed_events[EVENT_CUSTOM + 1]; // 已订阅事件
} QsmAdapterContext;

// 全局实例
static ModelAdapter g_qsm_adapter;
static QsmAdapterContext g_adapter_context;

// 内部函数声明
static int qsm_initialize(void* config);
static int qsm_start(void);
static int qsm_stop(void);
static int qsm_cleanup(void);
static int qsm_export_state(void** state_data, size_t* data_size);
static int qsm_import_state(void* state_data, size_t data_size);
static int qsm_validate_state(void* state_data, size_t data_size);
static int qsm_process_event(IntegrationEvent* event);
static int qsm_subscribe_event(IntegrationEventType event_type);
static int qsm_unsubscribe_event(IntegrationEventType event_type);
static int qsm_register_service(ServiceProvider* provider);
static int qsm_unregister_service(const char* service_id);
static int qsm_discover_services(QuantumModelType model_type);
static EntanglementChannel* qsm_adapter_create_entanglement_channel(QuantumState* state, QuantumModelType target_model, const char* target_model_id);
static int qsm_detect_knowledge_gap(const char* query, double* confidence);
static QuantumState* qsm_ask_claude(const char* query);
static int qsm_integrate_knowledge(QuantumState* knowledge_state);
static EntanglementChannel* qsm_create_knowledge_sharing_channel(QuantumState* state);

// 工具函数
static char* duplicate_string(const char* str);
static uint64_t get_current_timestamp();

/**
 * 获取QSM适配器实例
 * 
 * @return QSM适配器指针
 */
ModelAdapter* get_qsm_adapter() {
    if (!g_qsm_adapter.model_id) {
        // 首次调用时初始化适配器
        g_qsm_adapter.model_type = MODEL_QSM;
        g_qsm_adapter.model_id = "qsm_model_001";
        g_qsm_adapter.model_name = "量子叠加模型";
        g_qsm_adapter.model_version = "1.0";
        
        // 设置函数指针
        g_qsm_adapter.initialize = qsm_initialize;
        g_qsm_adapter.start = qsm_start;
        g_qsm_adapter.stop = qsm_stop;
        g_qsm_adapter.cleanup = qsm_cleanup;
        g_qsm_adapter.export_state = qsm_export_state;
        g_qsm_adapter.import_state = qsm_import_state;
        g_qsm_adapter.validate_state = qsm_validate_state;
        g_qsm_adapter.process_event = qsm_process_event;
        g_qsm_adapter.subscribe_event = qsm_subscribe_event;
        g_qsm_adapter.unsubscribe_event = qsm_unsubscribe_event;
        g_qsm_adapter.register_service = qsm_register_service;
        g_qsm_adapter.unregister_service = qsm_unregister_service;
        g_qsm_adapter.discover_services = qsm_discover_services;
        
        // 初始化内部状态
        memset(&g_adapter_context, 0, sizeof(QsmAdapterContext));
    }
    
    return &g_qsm_adapter;
}

/**
 * 初始化QSM适配器
 */
static int qsm_initialize(void* config) {
    if (g_adapter_context.initialized) {
        return 0; // 已经初始化
    }
    
    printf("初始化QSM适配器\n");
    
    // 初始化状态
    g_adapter_context.state.quantum_state = NULL;
    g_adapter_context.state.state_size = 0;
    g_adapter_context.state.last_updated = get_current_timestamp();
    g_adapter_context.state.is_entangled = 0;
    
    // 初始化事件缓冲区
    g_adapter_context.event_buffer_size = 10;
    g_adapter_context.event_buffer = (IntegrationEvent*)malloc(
        g_adapter_context.event_buffer_size * sizeof(IntegrationEvent));
    
    if (!g_adapter_context.event_buffer) {
        fprintf(stderr, "无法分配事件缓冲区\n");
        return -1;
    }
    
    // 清空事件缓冲区
    memset(g_adapter_context.event_buffer, 0, 
           g_adapter_context.event_buffer_size * sizeof(IntegrationEvent));
    
    // 清空已订阅事件
    memset(g_adapter_context.subscribed_events, 0, sizeof(g_adapter_context.subscribed_events));
    
    // 标记为已初始化
    g_adapter_context.initialized = 1;
    
    printf("QSM适配器初始化完成\n");
    return 0;
}

/**
 * 启动QSM适配器
 */
static int qsm_start(void) {
    if (!g_adapter_context.initialized) {
        return -1; // 未初始化
    }
    
    printf("启动QSM适配器\n");
    
    // 订阅关心的事件
    qsm_subscribe_event(EVENT_STATE_CHANGED);
    qsm_subscribe_event(EVENT_ENTANGLEMENT_CREATED);
    qsm_subscribe_event(EVENT_ENTANGLEMENT_BROKEN);
    qsm_subscribe_event(EVENT_SYNC_REQUESTED);
    
    // 创建并注册QSM服务
    ServiceProvider qsm_service;
    qsm_service.service_id = "qsm_state_service";
    qsm_service.service_name = "QSM状态服务";
    qsm_service.service_uri = "qsm://state";
    qsm_service.role = ROLE_PROVIDER;
    qsm_service.model_type = MODEL_QSM;
    qsm_service.capabilities = NULL;
    
    qsm_register_service(&qsm_service);
    
    return 0;
}

/**
 * 停止QSM适配器
 */
static int qsm_stop(void) {
    if (!g_adapter_context.initialized) {
        return -1; // 未初始化
    }
    
    printf("停止QSM适配器\n");
    
    // 解除所有事件订阅
    for (int i = 0; i <= EVENT_CUSTOM; i++) {
        if (g_adapter_context.subscribed_events[i]) {
            qsm_unsubscribe_event((IntegrationEventType)i);
        }
    }
    
    // 注销所有服务
    qsm_unregister_service("qsm_state_service");
    
    return 0;
}

/**
 * 清理QSM适配器资源
 */
static int qsm_cleanup(void) {
    if (!g_adapter_context.initialized) {
        return -1; // 未初始化
    }
    
    printf("清理QSM适配器资源\n");
    
    // 释放状态资源
    if (g_adapter_context.state.quantum_state) {
        free(g_adapter_context.state.quantum_state);
        g_adapter_context.state.quantum_state = NULL;
    }
    
    // 释放事件缓冲区
    if (g_adapter_context.event_buffer) {
        // 释放缓冲区中每个事件的资源
        for (size_t i = 0; i < g_adapter_context.event_buffer_size; i++) {
            IntegrationEvent* event = &g_adapter_context.event_buffer[i];
            free(event->source_id);
            free(event->event_data);
        }
        
        free(g_adapter_context.event_buffer);
        g_adapter_context.event_buffer = NULL;
    }
    
    // 重置状态
    g_adapter_context.initialized = 0;
    
    return 0;
}

/**
 * 导出QSM状态
 */
static int qsm_export_state(void** state_data, size_t* data_size) {
    if (!g_adapter_context.initialized || !state_data || !data_size) {
        return -1; // 未初始化或参数错误
    }
    
    // 如果没有状态，返回空
    if (!g_adapter_context.state.quantum_state || g_adapter_context.state.state_size == 0) {
        *state_data = NULL;
        *data_size = 0;
        return 0;
    }
    
    // 分配内存并复制状态
    void* data_copy = malloc(g_adapter_context.state.state_size);
    if (!data_copy) {
        return -1; // 内存分配失败
    }
    
    memcpy(data_copy, g_adapter_context.state.quantum_state, g_adapter_context.state.state_size);
    
    *state_data = data_copy;
    *data_size = g_adapter_context.state.state_size;
    
    return 0;
}

/**
 * 导入QSM状态
 */
static int qsm_import_state(void* state_data, size_t data_size) {
    if (!g_adapter_context.initialized) {
        return -1; // 未初始化
    }
    
    // 验证状态
    if (!qsm_validate_state(state_data, data_size)) {
        return -2; // 状态验证失败
    }
    
    // 释放现有状态
    if (g_adapter_context.state.quantum_state) {
        free(g_adapter_context.state.quantum_state);
    }
    
    // 分配新内存并复制状态
    g_adapter_context.state.quantum_state = malloc(data_size);
    if (!g_adapter_context.state.quantum_state) {
        return -1; // 内存分配失败
    }
    
    memcpy(g_adapter_context.state.quantum_state, state_data, data_size);
    g_adapter_context.state.state_size = data_size;
    g_adapter_context.state.last_updated = get_current_timestamp();
    
    return 0;
}

/**
 * 验证QSM状态
 */
static int qsm_validate_state(void* state_data, size_t data_size) {
    // 简单验证：检查数据和大小是否有效
    if (!state_data || data_size == 0) {
        return 0; // 无效状态
    }
    
    // TODO: 实现更复杂的状态验证逻辑
    
    return 1; // 状态有效
}

/**
 * 处理集成事件
 */
static int qsm_process_event(IntegrationEvent* event) {
    if (!g_adapter_context.initialized || !event) {
        return -1; // 未初始化或参数错误
    }
    
    // 检查是否订阅了此类型的事件
    if (!g_adapter_context.subscribed_events[event->type]) {
        return 0; // 未订阅此类型事件，忽略
    }
    
    printf("QSM适配器处理事件: 类型=%d, 源=%s\n", event->type, event->source_id);
    
    // 根据事件类型处理
    switch (event->type) {
        case EVENT_STATE_CHANGED: {
            // 处理状态变化事件
            // 如果状态来自其他模型，可能需要转换并更新本地状态
            printf("处理状态变化事件，源模型: %d\n", event->source_model);
            
            // 这里简化处理：如果是其他模型的状态变化，可能需要导入状态
            if (event->source_model != MODEL_QSM && event->event_data) {
                // 解析事件数据（假设为序列化的状态数据）
                // 实际实现中，这里需要根据事件数据格式进行正确解析
                printf("收到其他模型的状态数据\n");
                
                // 检查是否需要向Claude提问来理解这个新状态
                double confidence = 0.0;
                if (qsm_detect_knowledge_gap("如何理解这个新状态?", &confidence)) {
                    QuantumState* knowledge = qsm_ask_claude("如何处理并集成来自其他模型的量子状态?");
                    if (knowledge) {
                        qsm_integrate_knowledge(knowledge);
                    }
                }
            }
            break;
        }
        
        case EVENT_ENTANGLEMENT_CREATED: {
            // 处理纠缠创建事件
            printf("处理纠缠创建事件\n");
            g_adapter_context.state.is_entangled = 1;
            break;
        }
        
        case EVENT_ENTANGLEMENT_BROKEN: {
            // 处理纠缠断开事件
            printf("处理纠缠断开事件\n");
            g_adapter_context.state.is_entangled = 0;
            break;
        }
        
        case EVENT_SYNC_REQUESTED: {
            // 处理同步请求事件
            printf("处理同步请求事件\n");
            
            // 解析同步策略
            int sync_strategy = SYNC_ALL;
            if (event->event_data) {
                sync_strategy = atoi((const char*)event->event_data);
            }
            
            // 执行相应的同步操作
            switch (sync_strategy) {
                case SYNC_QUANTUM_STATE:
                    printf("执行量子状态同步\n");
                    break;
                    
                case SYNC_ENTANGLEMENT:
                    printf("执行量子纠缠同步\n");
                    break;
                    
                case SYNC_FIELD:
                    printf("执行量子场同步\n");
                    break;
                    
                case SYNC_EVENTS:
                    printf("执行事件同步\n");
                    break;
                    
                case SYNC_ALL:
                default:
                    printf("执行全部同步\n");
                    break;
            }
            break;
        }
        
        // 新增处理：处理知识缺口事件
        case EVENT_CUSTOM: {
            // 检查是否是知识缺口事件
            if (event->event_data && strstr((const char*)event->event_data, "KNOWLEDGE_GAP")) {
                printf("检测到知识缺口事件\n");
                
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
                        QuantumState* knowledge = qsm_ask_claude(query);
                        if (knowledge) {
                            // 整合知识
                            qsm_integrate_knowledge(knowledge);
                            
                            // 在模型之间共享这个知识
                            qsm_create_knowledge_sharing_channel(knowledge);
                        }
                        
                        free(query);
                    }
                }
            }
            break;
        }
        
        default:
            // 其他事件类型
            printf("未处理的事件类型: %d\n", event->type);
            break;
    }
    
    return 0;
}

/**
 * 订阅事件
 */
static int qsm_subscribe_event(IntegrationEventType event_type) {
    if (!g_adapter_context.initialized) {
        return -1; // 未初始化
    }
    
    g_adapter_context.subscribed_events[event_type] = 1;
    printf("QSM适配器已订阅事件类型: %d\n", event_type);
    return 0;
}

/**
 * 取消订阅事件
 */
static int qsm_unsubscribe_event(IntegrationEventType event_type) {
    if (!g_adapter_context.initialized) {
        return -1; // 未初始化
    }
    
    g_adapter_context.subscribed_events[event_type] = 0;
    printf("QSM适配器已取消订阅事件类型: %d\n", event_type);
    return 0;
}

/**
 * 注册服务
 */
static int qsm_register_service(ServiceProvider* provider) {
    if (!g_adapter_context.initialized || !provider) {
        return -1; // 未初始化或参数错误
    }
    
    // 创建服务提供者的副本
    ServiceProvider service_copy;
    service_copy.service_id = duplicate_string(provider->service_id);
    service_copy.service_name = duplicate_string(provider->service_name);
    service_copy.service_uri = duplicate_string(provider->service_uri);
    service_copy.role = provider->role;
    service_copy.model_type = MODEL_QSM; // 强制设置为QSM类型
    
    // 复制能力数据（如果有）
    if (provider->capabilities) {
        service_copy.capabilities = duplicate_string(provider->capabilities);
    } else {
        service_copy.capabilities = NULL;
    }
    
    // 获取默认集成管理器并注册服务
    IntegrationManager* manager = get_default_integration_manager();
    if (!manager) {
        // 清理资源
        free(service_copy.service_id);
        free(service_copy.service_name);
        free(service_copy.service_uri);
        free(service_copy.capabilities);
        return -2; // 没有默认管理器
    }
    
    int result = register_service_provider(manager, &service_copy);
    
    // 注册后清理副本资源（因为register_service_provider会创建自己的副本）
    free(service_copy.service_id);
    free(service_copy.service_name);
    free(service_copy.service_uri);
    free(service_copy.capabilities);
    
    return result;
}

/**
 * 注销服务
 */
static int qsm_unregister_service(const char* service_id) {
    if (!g_adapter_context.initialized || !service_id) {
        return -1; // 未初始化或参数错误
    }
    
    // 获取默认集成管理器并注销服务
    IntegrationManager* manager = get_default_integration_manager();
    if (!manager) {
        return -2; // 没有默认管理器
    }
    
    return unregister_service_provider(manager, service_id);
}

/**
 * 发现服务
 */
static int qsm_discover_services(QuantumModelType model_type) {
    if (!g_adapter_context.initialized) {
        return -1; // 未初始化
    }
    
    // 获取默认集成管理器
    IntegrationManager* manager = get_default_integration_manager();
    if (!manager) {
        return -2; // 没有默认管理器
    }
    
    // 查找指定类型的服务
    int count = 0;
    ServiceProvider** services = find_services_by_model(manager, model_type, &count);
    
    if (services) {
        printf("发现 %d 个类型为 %d 的服务:\n", count, model_type);
        for (int i = 0; i < count; i++) {
            ServiceProvider* service = services[i];
            printf("  - ID: %s, 名称: %s, URI: %s\n",
                   service->service_id, service->service_name, service->service_uri);
        }
        
        // 释放服务数组（但不释放服务本身，因为它们属于管理器）
        free(services);
    } else {
        printf("未发现类型为 %d 的服务\n", model_type);
    }
    
    return count;
}

/**
 * 检测知识缺口
 * 
 * @param query 当前查询或问题
 * @param confidence 返回的确信度
 * @return 如果存在知识缺口返回1，否则返回0
 */
static int qsm_detect_knowledge_gap(const char* query, double* confidence) {
    if (!query || !confidence) {
        return 0;
    }
    
    // 简单实现：检查现有知识库中是否有相关信息
    *confidence = g_adapter_context.state.knowledge_confidence;
    
    // 如果确信度低于阈值，认为存在知识缺口
    if (*confidence < 0.7) {
        printf("QSM模型检测到知识缺口，确信度: %.2f\n", *confidence);
        
        // 记录查询
        if (g_adapter_context.state.query_count < 10) {
            g_adapter_context.state.recent_queries[g_adapter_context.state.query_count] = 
                duplicate_string(query);
            g_adapter_context.state.query_count++;
        } else {
            // 移除最旧的查询并添加新查询
            free(g_adapter_context.state.recent_queries[0]);
            for (int i = 0; i < 9; i++) {
                g_adapter_context.state.recent_queries[i] = 
                    g_adapter_context.state.recent_queries[i+1];
            }
            g_adapter_context.state.recent_queries[9] = duplicate_string(query);
        }
        
        return 1; // 存在知识缺口
    }
    
    return 0; // 没有知识缺口
}

/**
 * 向Claude提问并获取知识
 * 
 * @param query 问题
 * @return 包含知识的量子状态
 */
static QuantumState* qsm_ask_claude(const char* query) {
    if (!query) {
        return NULL;
    }
    
    printf("QSM模型向Claude提问: %s\n", query);
    
    // 调用Claude适配器处理文本
    char* claude_response = claude_adapter_process_text(query, 
        "你是一个量子叠加模型的知识助手。请以清晰、准确的方式回答问题，并添加必要的量子叠加状态概率。");
    
    if (!claude_response) {
        printf("无法从Claude获取响应\n");
        return NULL;
    }
    
    printf("收到Claude响应\n");
    
    // 将Claude响应转换为量子状态
    QuantumState* knowledge_state = claude_adapter_generate_quantum_state(
        claude_response, "qsm_new_knowledge");
    
    // 释放响应内存
    free(claude_response);
    
    return knowledge_state;
}

/**
 * 整合新知识到QSM模型
 * 
 * @param knowledge_state 包含知识的量子状态
 * @return 成功返回1，失败返回0
 */
static int qsm_integrate_knowledge(QuantumState* knowledge_state) {
    if (!knowledge_state) {
        return 0;
    }
    
    printf("QSM模型整合新知识: %s\n", knowledge_state->id);
    
    // 将知识状态添加到知识库
    if (g_adapter_context.state.knowledge_count < 20) {
        g_adapter_context.state.knowledge_states[g_adapter_context.state.knowledge_count] = 
            knowledge_state;
        g_adapter_context.state.knowledge_count++;
        
        // 提高知识确信度
        g_adapter_context.state.knowledge_confidence += 0.05;
        if (g_adapter_context.state.knowledge_confidence > 1.0) {
            g_adapter_context.state.knowledge_confidence = 1.0;
        }
    } else {
        // 移除最旧的知识并添加新知识
        quantum_state_destroy(g_adapter_context.state.knowledge_states[0]);
        for (int i = 0; i < 19; i++) {
            g_adapter_context.state.knowledge_states[i] = 
                g_adapter_context.state.knowledge_states[i+1];
        }
        g_adapter_context.state.knowledge_states[19] = knowledge_state;
    }
    
    // 创建并发布状态变化事件
    IntegrationManager* manager = get_default_integration_manager();
    if (manager) {
        IntegrationEvent* event = create_integration_event(
            EVENT_STATE_CHANGED, g_qsm_adapter.model_id, MODEL_QSM, "QSM模型已学习新知识");
        
        if (event) {
            publish_event(manager, event);
            free_integration_event(event);
        }
    }
    
    return 1;
}

/**
 * 创建QSM适配器与其他模型之间的纠缠信道
 * 
 * @param state 用于建立纠缠的量子状态
 * @param target_model 目标模型类型
 * @param target_model_id 目标模型ID
 * @return 创建的纠缠信道，失败返回NULL
 */
static EntanglementChannel* qsm_adapter_create_entanglement_channel(QuantumState* state, QuantumModelType target_model, const char* target_model_id) {
    if (!state || !target_model_id) {
        return NULL;
    }
    
    printf("QSM适配器创建与%s(%d)模型的纠缠信道\n", target_model_id, target_model);
    
    // 创建一个唯一的信道ID
    char channel_id[128];
    snprintf(channel_id, sizeof(channel_id), "qsm_to_%s_%lu", 
             target_model_id, get_current_timestamp());
    
    // 创建纠缠信道
    EntanglementChannel* channel = quantum_entanglement_create(
        channel_id, 
        g_qsm_adapter.model_id,    // 源模型ID 
        MODEL_QSM,                 // 源模型类型
        target_model_id,           // 目标模型ID
        target_model               // 目标模型类型
    );
    
    if (!channel) {
        printf("创建纠缠信道失败\n");
        return NULL;
    }
    
    // 设置信道属性
    quantum_entanglement_set_property(channel, "state_id", state->id);
    quantum_entanglement_set_property(channel, "entanglement_strength", "0.95");
    quantum_entanglement_set_property(channel, "connection_type", "direct");
    
    // 添加量子基因编码
    char gene_code[128];
    sprintf(gene_code, "QG-ENTANGLE-QSM-%d-%lu", target_model, get_current_timestamp());
    quantum_entanglement_add_gene(channel, gene_code);
    
    // 将状态附加到信道
    quantum_entanglement_attach_state(channel, state);
    
    // 通知集成管理器
    IntegrationManager* manager = get_default_integration_manager();
    if (manager) {
        // 创建纠缠创建事件
        IntegrationEvent* event = create_integration_event(
            EVENT_ENTANGLEMENT_CREATED, 
            g_qsm_adapter.model_id, 
            MODEL_QSM, 
            "QSM模型创建了与其他模型的纠缠信道"
        );
        
        if (event) {
            // 添加目标模型信息
            char target_info[256];
            sprintf(target_info, "target_model_type=%d;target_model_id=%s;channel_id=%s", 
                    target_model, target_model_id, channel_id);
            event->event_data = (void*)duplicate_string(target_info);
            
            // 发布事件
            publish_event(manager, event);
            
            // 释放事件资源
            free(event->event_data);
            free_integration_event(event);
        }
    }
    
    printf("QSM适配器成功创建纠缠信道: %s\n", channel_id);
    g_adapter_context.state.is_entangled = 1;
    
    return channel;
}

// 修改qsm_create_knowledge_sharing_channel函数，使其使用qsm_adapter_create_entanglement_channel
static EntanglementChannel* qsm_create_knowledge_sharing_channel(QuantumState* state) {
    if (!state) {
        return NULL;
    }
    
    printf("QSM模型创建知识共享纠缠信道\n");
    
    // 创建与WeQ模型的纠缠信道
    EntanglementChannel* weq_channel = qsm_adapter_create_entanglement_channel(
        state, MODEL_WEQ, "weq_model_001");
    
    // 创建与SOM模型的纠缠信道
    EntanglementChannel* som_channel = qsm_adapter_create_entanglement_channel(
        state, MODEL_SOM, "som_model_001");
    
    // 创建与REF模型的纠缠信道
    EntanglementChannel* ref_channel = qsm_adapter_create_entanglement_channel(
        state, MODEL_REF, "ref_model_001");
    
    // 返回WeQ信道作为主要信道
    return weq_channel;
}

/**
 * 工具函数：复制字符串
 */
static char* duplicate_string(const char* str) {
    if (!str) return NULL;
    
    size_t len = strlen(str);
    char* dup = (char*)malloc(len + 1);
    if (!dup) return NULL;
    
    strcpy(dup, str);
    return dup;
}

/**
 * 工具函数：获取当前时间戳（毫秒）
 */
static uint64_t get_current_timestamp() {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
} 