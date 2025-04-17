/**
 * 量子模型集成框架实现
 * 
 * 提供QEntL环境中不同量子模型间的无缝集成机制，包括状态同步、事件传播和服务发现。
 * 支持QSM、SOM、REF和WeQ四个核心模型的互操作。
 * 
 * 作者: QEntL核心开发团队
 * 日期: 2024-05-21
 * 版本: 1.0
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "quantum_model_integration.h"
#include "../../quantum_state.h"
#include "../../quantum_entanglement.h"
#include "../../quantum_field.h"

/**
 * 内部结构定义
 */

// 事件队列节点
typedef struct EventQueueNode {
    IntegrationEvent event;
    struct EventQueueNode* next;
} EventQueueNode;

// 事件队列
typedef struct {
    EventQueueNode* head;
    EventQueueNode* tail;
    int size;
    int capacity;
} EventQueue;

// 事件处理器
typedef struct {
    IntegrationEventType event_type;
    EventHandlerCallback callback;
    void* user_data;
    int is_active;
} EventHandler;

// 模型注册详情
typedef struct {
    ModelAdapter* adapter;
    int is_active;
    uint64_t last_heartbeat;
    int subscribed_events[EVENT_CUSTOM + 1];
} RegisteredModel;

// 服务提供者详情
typedef struct {
    ServiceProvider provider;
    uint64_t registration_time;
    int is_active;
    int reference_count;
} RegisteredServiceProvider;

/**
 * 集成管理器完整定义
 */
struct IntegrationManager {
    IntegrationManagerConfig config;              // 配置
    
    RegisteredModel** registered_models;          // 已注册模型数组
    int model_count;                              // 模型数量
    int model_capacity;                           // 模型容量
    
    RegisteredServiceProvider** service_providers; // 服务提供者数组
    int provider_count;                           // 提供者数量
    int provider_capacity;                        // 提供者容量
    
    EventQueue* event_queue;                      // 事件队列
    
    EventHandler* event_handlers;                 // 事件处理器数组
    int handler_count;                            // 处理器数量
    int handler_capacity;                         // 处理器容量
    
    uint64_t last_sync_time;                      // 上次同步时间
    int is_processing_events;                     // 是否正在处理事件
    
    int error_code;                               // 最近错误代码
    char error_message[256];                      // 错误消息
};

/**
 * 内部全局变量
 */
static IntegrationManager* g_default_manager = NULL;

/**
 * 内部函数声明
 */
static EventQueue* create_event_queue(int capacity);
static void free_event_queue(EventQueue* queue);
static int push_event(EventQueue* queue, IntegrationEvent* event);
static int pop_event(EventQueue* queue, IntegrationEvent* event);

static RegisteredModel* find_registered_model(IntegrationManager* manager, QuantumModelType type, const char* model_id);
static RegisteredServiceProvider* find_service_provider(IntegrationManager* manager, const char* service_id);

static int process_event_queue(IntegrationManager* manager);
static uint64_t get_current_timestamp();
static char* duplicate_string(const char* str);
static void free_integration_event(IntegrationEvent* event);
static int validate_model_adapter(ModelAdapter* adapter);

/* ===== 集成管理器API实现 ===== */

/**
 * 创建量子模型集成管理器
 * 
 * @param config 集成管理器配置
 * @return 新创建的集成管理器指针，失败返回NULL
 */
IntegrationManager* create_integration_manager(IntegrationManagerConfig config) {
    IntegrationManager* manager = (IntegrationManager*)malloc(sizeof(IntegrationManager));
    if (!manager) {
        fprintf(stderr, "无法分配集成管理器内存\n");
        return NULL;
    }
    
    // 初始化配置
    manager->config = config;
    
    // 设置默认值
    if (manager->config.event_queue_size <= 0) {
        manager->config.event_queue_size = 100; // 默认队列大小
    }
    
    if (manager->config.max_service_providers <= 0) {
        manager->config.max_service_providers = 50; // 默认最大服务提供者数量
    }
    
    if (manager->config.sync_interval_ms <= 0) {
        manager->config.sync_interval_ms = 1000; // 默认同步间隔1秒
    }
    
    // 创建事件队列
    manager->event_queue = create_event_queue(manager->config.event_queue_size);
    if (!manager->event_queue) {
        fprintf(stderr, "无法创建事件队列\n");
        free(manager);
        return NULL;
    }
    
    // 初始化模型数组
    manager->model_capacity = 10; // 初始容量
    manager->model_count = 0;
    manager->registered_models = (RegisteredModel**)malloc(
        manager->model_capacity * sizeof(RegisteredModel*));
    if (!manager->registered_models) {
        fprintf(stderr, "无法分配模型数组内存\n");
        free_event_queue(manager->event_queue);
        free(manager);
        return NULL;
    }
    
    // 初始化服务提供者数组
    manager->provider_capacity = manager->config.max_service_providers;
    manager->provider_count = 0;
    manager->service_providers = (RegisteredServiceProvider**)malloc(
        manager->provider_capacity * sizeof(RegisteredServiceProvider*));
    if (!manager->service_providers) {
        fprintf(stderr, "无法分配服务提供者数组内存\n");
        free(manager->registered_models);
        free_event_queue(manager->event_queue);
        free(manager);
        return NULL;
    }
    
    // 初始化事件处理器数组
    manager->handler_capacity = 20; // 初始容量
    manager->handler_count = 0;
    manager->event_handlers = (EventHandler*)malloc(
        manager->handler_capacity * sizeof(EventHandler));
    if (!manager->event_handlers) {
        fprintf(stderr, "无法分配事件处理器数组内存\n");
        free(manager->service_providers);
        free(manager->registered_models);
        free_event_queue(manager->event_queue);
        free(manager);
        return NULL;
    }
    
    // 初始化其他字段
    manager->last_sync_time = get_current_timestamp();
    manager->is_processing_events = 0;
    manager->error_code = 0;
    memset(manager->error_message, 0, sizeof(manager->error_message));
    
    // 设置默认管理器（如果尚未设置）
    if (g_default_manager == NULL) {
        g_default_manager = manager;
    }
    
    printf("量子模型集成管理器已创建，当前共有 %d 个已注册模型\n", manager->model_count);
    return manager;
}

/**
 * 释放量子模型集成管理器资源
 * 
 * @param manager 集成管理器指针
 */
void free_integration_manager(IntegrationManager* manager) {
    if (!manager) return;
    
    // 清理已注册的模型
    for (int i = 0; i < manager->model_count; i++) {
        RegisteredModel* reg_model = manager->registered_models[i];
        if (reg_model) {
            // 不释放适配器，因为这是外部提供的
            free(reg_model);
        }
    }
    free(manager->registered_models);
    
    // 清理服务提供者
    for (int i = 0; i < manager->provider_count; i++) {
        RegisteredServiceProvider* provider = manager->service_providers[i];
        if (provider) {
            // 释放服务提供者字符串资源
            free(provider->provider.service_id);
            free(provider->provider.service_name);
            free(provider->provider.service_uri);
            free(provider->provider.capabilities);
            free(provider);
        }
    }
    free(manager->service_providers);
    
    // 释放事件队列
    free_event_queue(manager->event_queue);
    
    // 释放事件处理器数组
    free(manager->event_handlers);
    
    // 如果是默认管理器，清除引用
    if (g_default_manager == manager) {
        g_default_manager = NULL;
    }
    
    // 释放管理器本身
    free(manager);
    
    printf("量子模型集成管理器已释放\n");
}

static EventQueue* create_event_queue(int capacity) {
    EventQueue* queue = (EventQueue*)malloc(sizeof(EventQueue));
    if (!queue) return NULL;
    
    queue->head = queue->tail = NULL;
    queue->size = 0;
    queue->capacity = capacity;
    
    return queue;
}

static void free_event_queue(EventQueue* queue) {
    if (!queue) return;
    
    EventQueueNode* current = queue->head;
    EventQueueNode* next;
    
    while (current) {
        next = current->next;
        free_integration_event(&current->event);
        free(current);
        current = next;
    }
    
    queue->head = queue->tail = NULL;
    queue->size = 0;
}

static int push_event(EventQueue* queue, IntegrationEvent* event) {
    if (!queue || !event) return 0;
    
    EventQueueNode* new_node = (EventQueueNode*)malloc(sizeof(EventQueueNode));
    if (!new_node) return 0;
    
    new_node->event = *event;
    new_node->next = NULL;
    
    if (queue->tail) {
        queue->tail->next = new_node;
    } else {
        queue->head = new_node;
    }
    
    queue->tail = new_node;
    queue->size++;
    
    return 1;
}

static int pop_event(EventQueue* queue, IntegrationEvent* event) {
    if (!queue || !event) return 0;
    
    if (queue->head == NULL) return 0;
    
    EventQueueNode* node = queue->head;
    *event = node->event;
    
    queue->head = node->next;
    if (queue->head == NULL) {
        queue->tail = NULL;
    }
    
    free(node);
    queue->size--;
    
    return 1;
}

static RegisteredModel* find_registered_model(IntegrationManager* manager, QuantumModelType type, const char* model_id) {
    if (!manager || !model_id) return NULL;
    
    for (int i = 0; i < manager->model_count; i++) {
        RegisteredModel* reg_model = manager->registered_models[i];
        if (reg_model && reg_model->adapter && reg_model->adapter->type == type && strcmp(reg_model->adapter->model_id, model_id) == 0) {
            return reg_model;
        }
    }
    return NULL;
}

static RegisteredServiceProvider* find_service_provider(IntegrationManager* manager, const char* service_id) {
    if (!manager || !service_id) return NULL;
    
    for (int i = 0; i < manager->provider_count; i++) {
        RegisteredServiceProvider* provider = manager->service_providers[i];
        if (provider && strcmp(provider->provider.service_id, service_id) == 0) {
            return provider;
        }
    }
    return NULL;
}

static int process_event_queue(IntegrationManager* manager) {
    if (!manager) return 0;
    
    // Implementation of process_event_queue function
    return 1; // Placeholder return, actual implementation needed
}

static uint64_t get_current_timestamp() {
    return (uint64_t)time(NULL);
}

static char* duplicate_string(const char* str) {
    if (!str) return NULL;
    
    char* dup = (char*)malloc(strlen(str) + 1);
    if (!dup) return NULL;
    
    strcpy(dup, str);
    return dup;
}

static void free_integration_event(IntegrationEvent* event) {
    if (!event) return;
    
    // Implementation of free_integration_event function
}

static int validate_model_adapter(ModelAdapter* adapter) {
    if (!adapter) return 0;
    
    // Implementation of validate_model_adapter function
    return 1; // Placeholder return, actual implementation needed
}

/**
 * 注册模型适配器
 * 
 * @param manager 集成管理器指针
 * @param adapter 模型适配器指针
 * @return 成功返回0，失败返回错误码
 */
int register_model_adapter(IntegrationManager* manager, ModelAdapter* adapter) {
    if (!manager || !adapter) {
        return -1; // 参数错误
    }
    
    // 验证适配器
    if (!validate_model_adapter(adapter)) {
        sprintf(manager->error_message, "模型适配器验证失败，缺少必要的接口实现");
        manager->error_code = -2;
        return -2; // 适配器验证失败
    }
    
    // 检查是否已存在
    RegisteredModel* existing = find_registered_model(manager, adapter->model_type, adapter->model_id);
    if (existing) {
        sprintf(manager->error_message, "模型已注册: %s (类型: %d)", adapter->model_id, adapter->model_type);
        manager->error_code = -3;
        return -3; // 模型已注册
    }
    
    // 检查容量，必要时扩容
    if (manager->model_count >= manager->model_capacity) {
        int new_capacity = manager->model_capacity * 2;
        RegisteredModel** new_models = (RegisteredModel**)realloc(
            manager->registered_models, 
            new_capacity * sizeof(RegisteredModel*));
        
        if (!new_models) {
            sprintf(manager->error_message, "内存分配失败，无法扩展模型数组");
            manager->error_code = -4;
            return -4; // 内存分配失败
        }
        
        manager->registered_models = new_models;
        manager->model_capacity = new_capacity;
    }
    
    // 创建并初始化注册模型
    RegisteredModel* reg_model = (RegisteredModel*)malloc(sizeof(RegisteredModel));
    if (!reg_model) {
        sprintf(manager->error_message, "内存分配失败，无法创建注册模型");
        manager->error_code = -4;
        return -4; // 内存分配失败
    }
    
    reg_model->adapter = adapter;
    reg_model->is_active = 1;
    reg_model->last_heartbeat = get_current_timestamp();
    memset(reg_model->subscribed_events, 0, sizeof(reg_model->subscribed_events));
    
    // 添加到注册模型数组
    manager->registered_models[manager->model_count++] = reg_model;
    
    // 创建模型注册事件
    IntegrationEvent event;
    event.type = EVENT_MODEL_REGISTERED;
    event.source_id = duplicate_string(adapter->model_id);
    event.source_model = adapter->model_type;
    event.event_data = NULL; // 不需要额外数据
    event.timestamp = get_current_timestamp();
    event.sequence = 0; // 序列号将在push_event中分配
    
    // 发送事件
    push_event(manager->event_queue, &event);
    
    // 初始化适配器（如果提供了初始化函数）
    if (adapter->initialize) {
        adapter->initialize(NULL); // 默认无配置
    }
    
    printf("模型已注册: %s (类型: %d)\n", adapter->model_id, adapter->model_type);
    return 0; // 成功
}

/**
 * 注销模型适配器
 * 
 * @param manager 集成管理器指针
 * @param model_type 模型类型
 * @param model_id 模型ID
 * @return 成功返回0，失败返回错误码
 */
int unregister_model_adapter(IntegrationManager* manager, QuantumModelType model_type, const char* model_id) {
    if (!manager || !model_id) {
        return -1; // 参数错误
    }
    
    // 查找模型
    RegisteredModel* model = NULL;
    int model_index = -1;
    
    for (int i = 0; i < manager->model_count; i++) {
        RegisteredModel* curr = manager->registered_models[i];
        if (curr && curr->adapter && 
            curr->adapter->model_type == model_type && 
            strcmp(curr->adapter->model_id, model_id) == 0) {
            model = curr;
            model_index = i;
            break;
        }
    }
    
    if (!model) {
        sprintf(manager->error_message, "模型未注册: %s (类型: %d)", model_id, model_type);
        manager->error_code = -5;
        return -5; // 模型未注册
    }
    
    // 停止和清理适配器
    if (model->adapter->stop) {
        model->adapter->stop();
    }
    
    if (model->adapter->cleanup) {
        model->adapter->cleanup();
    }
    
    // 创建模型注销事件
    IntegrationEvent event;
    event.type = EVENT_MODEL_UNREGISTERED;
    event.source_id = duplicate_string(model_id);
    event.source_model = model_type;
    event.event_data = NULL; // 不需要额外数据
    event.timestamp = get_current_timestamp();
    event.sequence = 0; // 序列号将在push_event中分配
    
    // 发送事件
    push_event(manager->event_queue, &event);
    
    // 从数组中移除 (通过与最后一个交换位置)
    free(model);
    if (model_index < manager->model_count - 1) {
        manager->registered_models[model_index] = manager->registered_models[manager->model_count - 1];
    }
    manager->model_count--;
    
    printf("模型已注销: %s (类型: %d)\n", model_id, model_type);
    return 0; // 成功
}

/**
 * 注册服务提供者
 * 
 * @param manager 集成管理器指针
 * @param provider 服务提供者
 * @return 成功返回0，失败返回错误码
 */
int register_service_provider(IntegrationManager* manager, ServiceProvider* provider) {
    if (!manager || !provider || !provider->service_id) {
        return -1; // 参数错误
    }
    
    // 检查是否已存在
    RegisteredServiceProvider* existing = find_service_provider(manager, provider->service_id);
    if (existing) {
        // 更新现有提供者信息
        free(existing->provider.service_name);
        free(existing->provider.service_uri);
        free(existing->provider.capabilities);
        
        existing->provider.service_name = duplicate_string(provider->service_name);
        existing->provider.service_uri = duplicate_string(provider->service_uri);
        existing->provider.role = provider->role;
        existing->provider.model_type = provider->model_type;
        
        // 复制能力数据（如果有）
        if (provider->capabilities) {
            // 假设capabilities是一个可以深复制的结构
            // 实际实现中可能需要根据具体类型进行处理
            existing->provider.capabilities = duplicate_string(provider->capabilities);
        } else {
            existing->provider.capabilities = NULL;
        }
        
        existing->is_active = 1;
        
        printf("服务提供者已更新: %s\n", provider->service_id);
        return 0;
    }
    
    // 检查是否超过最大服务提供者数量
    if (manager->provider_count >= manager->provider_capacity) {
        sprintf(manager->error_message, "服务提供者数量已达到上限: %d", manager->provider_capacity);
        manager->error_code = -6;
        return -6; // 超过最大数量
    }
    
    // 创建新的服务提供者
    RegisteredServiceProvider* new_provider = (RegisteredServiceProvider*)malloc(sizeof(RegisteredServiceProvider));
    if (!new_provider) {
        sprintf(manager->error_message, "内存分配失败，无法创建服务提供者");
        manager->error_code = -4;
        return -4; // 内存分配失败
    }
    
    // 复制服务提供者信息
    new_provider->provider.service_id = duplicate_string(provider->service_id);
    new_provider->provider.service_name = duplicate_string(provider->service_name);
    new_provider->provider.service_uri = duplicate_string(provider->service_uri);
    new_provider->provider.role = provider->role;
    new_provider->provider.model_type = provider->model_type;
    
    // 复制能力数据（如果有）
    if (provider->capabilities) {
        new_provider->provider.capabilities = duplicate_string(provider->capabilities);
    } else {
        new_provider->provider.capabilities = NULL;
    }
    
    new_provider->registration_time = get_current_timestamp();
    new_provider->is_active = 1;
    new_provider->reference_count = 0;
    
    // 添加到服务提供者数组
    manager->service_providers[manager->provider_count++] = new_provider;
    
    // 创建服务发现事件
    IntegrationEvent event;
    event.type = EVENT_SERVICE_DISCOVERED;
    event.source_id = duplicate_string(provider->service_id);
    event.source_model = provider->model_type;
    event.event_data = NULL; // 不需要额外数据
    event.timestamp = get_current_timestamp();
    event.sequence = 0; // 序列号将在push_event中分配
    
    // 发送事件
    push_event(manager->event_queue, &event);
    
    printf("服务提供者已注册: %s\n", provider->service_id);
    return 0; // 成功
}

/**
 * 注销服务提供者
 * 
 * @param manager 集成管理器指针
 * @param service_id 服务ID
 * @return 成功返回0，失败返回错误码
 */
int unregister_service_provider(IntegrationManager* manager, const char* service_id) {
    if (!manager || !service_id) {
        return -1; // 参数错误
    }
    
    // 查找服务提供者
    RegisteredServiceProvider* provider = NULL;
    int provider_index = -1;
    
    for (int i = 0; i < manager->provider_count; i++) {
        RegisteredServiceProvider* curr = manager->service_providers[i];
        if (curr && strcmp(curr->provider.service_id, service_id) == 0) {
            provider = curr;
            provider_index = i;
            break;
        }
    }
    
    if (!provider) {
        sprintf(manager->error_message, "服务提供者未注册: %s", service_id);
        manager->error_code = -7;
        return -7; // 服务提供者未注册
    }
    
    // 如果有引用，则只标记为非活动
    if (provider->reference_count > 0) {
        provider->is_active = 0;
        printf("服务提供者已标记为非活动: %s (引用计数: %d)\n", 
               service_id, provider->reference_count);
        return 0;
    }
    
    // 否则，从数组中移除并释放资源
    free(provider->provider.service_id);
    free(provider->provider.service_name);
    free(provider->provider.service_uri);
    free(provider->provider.capabilities);
    free(provider);
    
    // 移动最后一个元素到当前位置
    if (provider_index < manager->provider_count - 1) {
        manager->service_providers[provider_index] = manager->service_providers[manager->provider_count - 1];
    }
    manager->provider_count--;
    
    printf("服务提供者已注销: %s\n", service_id);
    return 0; // 成功
}

/**
 * 发布集成事件
 * 
 * @param manager 集成管理器指针
 * @param event 事件指针
 * @return 成功返回0，失败返回错误码
 */
int publish_event(IntegrationManager* manager, IntegrationEvent* event) {
    if (!manager || !event) {
        return -1; // 参数错误
    }
    
    // 复制事件数据
    IntegrationEvent event_copy;
    event_copy.type = event->type;
    event_copy.source_id = duplicate_string(event->source_id);
    event_copy.source_model = event->source_model;
    
    // 复制事件数据（如果有）
    if (event->event_data) {
        // 假设event_data是一个可以深复制的字符串
        // 实际实现中可能需要根据具体类型进行处理
        event_copy.event_data = duplicate_string(event->event_data);
    } else {
        event_copy.event_data = NULL;
    }
    
    event_copy.timestamp = get_current_timestamp();
    event_copy.sequence = 0; // 序列号将在push_event中分配
    
    // 发送事件
    int result = push_event(manager->event_queue, &event_copy);
    if (result != 0) {
        // 推送失败，释放资源
        free(event_copy.source_id);
        free(event_copy.event_data);
    }
    
    return result;
}

/**
 * 注册事件处理器
 * 
 * @param manager 集成管理器指针
 * @param event_type 事件类型
 * @param callback 回调函数
 * @param user_data 用户数据
 * @return 成功返回0，失败返回错误码
 */
int register_event_handler(IntegrationManager* manager, IntegrationEventType event_type, 
                           EventHandlerCallback callback, void* user_data) {
    if (!manager || !callback) {
        return -1; // 参数错误
    }
    
    // 检查是否需要扩容
    if (manager->handler_count >= manager->handler_capacity) {
        int new_capacity = manager->handler_capacity * 2;
        EventHandler* new_handlers = (EventHandler*)realloc(
            manager->event_handlers, 
            new_capacity * sizeof(EventHandler));
        
        if (!new_handlers) {
            sprintf(manager->error_message, "内存分配失败，无法扩展事件处理器数组");
            manager->error_code = -4;
            return -4; // 内存分配失败
        }
        
        manager->event_handlers = new_handlers;
        manager->handler_capacity = new_capacity;
    }
    
    // 添加事件处理器
    EventHandler handler;
    handler.event_type = event_type;
    handler.callback = callback;
    handler.user_data = user_data;
    handler.is_active = 1;
    
    manager->event_handlers[manager->handler_count++] = handler;
    
    printf("事件处理器已注册: 类型=%d\n", event_type);
    return 0; // 成功
}

/**
 * 注销事件处理器
 * 
 * @param manager 集成管理器指针
 * @param event_type 事件类型
 * @param callback 回调函数
 * @return 成功返回0，失败返回错误码
 */
int unregister_event_handler(IntegrationManager* manager, IntegrationEventType event_type, 
                             EventHandlerCallback callback) {
    if (!manager || !callback) {
        return -1; // 参数错误
    }
    
    int found = 0;
    
    // 查找并移除事件处理器
    for (int i = 0; i < manager->handler_count; i++) {
        if (manager->event_handlers[i].event_type == event_type && 
            manager->event_handlers[i].callback == callback) {
            
            // 移除事件处理器（通过与最后一个交换位置）
            if (i < manager->handler_count - 1) {
                manager->event_handlers[i] = manager->event_handlers[manager->handler_count - 1];
            }
            manager->handler_count--;
            found = 1;
            break;
        }
    }
    
    if (!found) {
        sprintf(manager->error_message, "事件处理器未找到: 类型=%d", event_type);
        manager->error_code = -8;
        return -8; // 事件处理器未找到
    }
    
    printf("事件处理器已注销: 类型=%d\n", event_type);
    return 0; // 成功
}

/**
 * 处理集成管理器事件
 * 
 * @param manager 集成管理器指针
 * @return 处理的事件数量，失败返回负值
 */
int process_integration_events(IntegrationManager* manager) {
    if (!manager) {
        return -1; // 参数错误
    }
    
    // 防止递归调用
    if (manager->is_processing_events) {
        return 0;
    }
    
    manager->is_processing_events = 1;
    int processed_count = 0;
    
    // 处理队列中的事件
    IntegrationEvent event;
    while (pop_event(manager->event_queue, &event) == 0) {
        // 通知所有订阅该类型事件的模型
        for (int i = 0; i < manager->model_count; i++) {
            RegisteredModel* model = manager->registered_models[i];
            if (model && model->is_active && 
                model->subscribed_events[event.type] && 
                model->adapter && model->adapter->process_event) {
                
                model->adapter->process_event(&event);
            }
        }
        
        // 调用注册的事件处理器
        for (int i = 0; i < manager->handler_count; i++) {
            EventHandler* handler = &manager->event_handlers[i];
            if (handler->is_active && 
                (handler->event_type == event.type || handler->event_type == EVENT_CUSTOM)) {
                
                handler->callback(&event, handler->user_data);
            }
        }
        
        // 释放事件资源
        free_integration_event(&event);
        processed_count++;
    }
    
    manager->is_processing_events = 0;
    return processed_count;
}

/**
 * 同步模型状态
 * 
 * @param manager 集成管理器指针
 * @param strategy 同步策略
 * @return 成功返回0，失败返回错误码
 */
int synchronize_models(IntegrationManager* manager, SyncStrategy strategy) {
    if (!manager) {
        return -1; // 参数错误
    }
    
    uint64_t current_time = get_current_timestamp();
    int elapsed_ms = (int)(current_time - manager->last_sync_time);
    
    // 检查同步间隔
    if (elapsed_ms < manager->config.sync_interval_ms) {
        return 0; // 尚未到达同步时间
    }
    
    // 更新上次同步时间
    manager->last_sync_time = current_time;
    
    // 创建同步请求事件
    IntegrationEvent sync_event;
    sync_event.type = EVENT_SYNC_REQUESTED;
    sync_event.source_id = duplicate_string("integration_manager");
    sync_event.source_model = MODEL_CUSTOM;
    
    // 设置同步策略作为事件数据
    char sync_data[32];
    sprintf(sync_data, "%d", strategy);
    sync_event.event_data = duplicate_string(sync_data);
    
    sync_event.timestamp = current_time;
    sync_event.sequence = 0; // 序列号将在push_event中分配
    
    // 发送同步请求事件
    int result = push_event(manager->event_queue, &sync_event);
    if (result != 0) {
        free(sync_event.source_id);
        free(sync_event.event_data);
        return result;
    }
    
    // 处理事件（包括刚发送的同步请求）
    process_integration_events(manager);
    
    // 同步完成
    IntegrationEvent sync_complete_event;
    sync_complete_event.type = EVENT_SYNC_COMPLETED;
    sync_complete_event.source_id = duplicate_string("integration_manager");
    sync_complete_event.source_model = MODEL_CUSTOM;
    sync_complete_event.event_data = NULL;
    sync_complete_event.timestamp = get_current_timestamp();
    sync_complete_event.sequence = 0; // 序列号将在push_event中分配
    
    // 发送同步完成事件
    result = push_event(manager->event_queue, &sync_complete_event);
    if (result != 0) {
        free(sync_complete_event.source_id);
        return result;
    }
    
    // 再次处理事件，确保同步完成事件被处理
    process_integration_events(manager);
    
    return 0; // 成功
}

/**
 * 查找服务提供者
 * 
 * @param manager 集成管理器指针
 * @param model_type 模型类型
 * @return 服务提供者数组，调用者需要释放
 */
ServiceProvider** find_services_by_model(IntegrationManager* manager, QuantumModelType model_type, int* count) {
    if (!manager || !count) {
        return NULL; // 参数错误
    }
    
    // 首先计算匹配的服务提供者数量
    int matching_count = 0;
    for (int i = 0; i < manager->provider_count; i++) {
        RegisteredServiceProvider* provider = manager->service_providers[i];
        if (provider && provider->is_active && provider->provider.model_type == model_type) {
            matching_count++;
        }
    }
    
    *count = matching_count;
    
    if (matching_count == 0) {
        return NULL; // 没有匹配的服务提供者
    }
    
    // 分配结果数组
    ServiceProvider** result = (ServiceProvider**)malloc(matching_count * sizeof(ServiceProvider*));
    if (!result) {
        sprintf(manager->error_message, "内存分配失败，无法创建服务提供者数组");
        manager->error_code = -4;
        return NULL; // 内存分配失败
    }
    
    // 填充结果数组
    int result_index = 0;
    for (int i = 0; i < manager->provider_count; i++) {
        RegisteredServiceProvider* provider = manager->service_providers[i];
        if (provider && provider->is_active && provider->provider.model_type == model_type) {
            result[result_index++] = &(provider->provider);
        }
    }
    
    return result;
}

/**
 * 获取服务提供者
 * 
 * @param manager 集成管理器指针
 * @param service_id 服务ID
 * @return 服务提供者指针，如果未找到则返回NULL
 */
ServiceProvider* get_service_provider(IntegrationManager* manager, const char* service_id) {
    if (!manager || !service_id) {
        return NULL; // 参数错误
    }
    
    RegisteredServiceProvider* provider = find_service_provider(manager, service_id);
    if (!provider || !provider->is_active) {
        return NULL; // 未找到活动的服务提供者
    }
    
    return &(provider->provider);
}

/**
 * 获取默认集成管理器
 * 
 * @return 默认集成管理器指针，如果未创建则返回NULL
 */
IntegrationManager* get_default_integration_manager() {
    return g_default_manager;
}

/**
 * 获取最后一个错误信息
 * 
 * @param manager 集成管理器指针
 * @param error_code 错误代码输出
 * @return 错误消息字符串
 */
const char* get_last_error(IntegrationManager* manager, int* error_code) {
    if (!manager) {
        if (error_code) *error_code = -1;
        return "无效的集成管理器";
    }
    
    if (error_code) *error_code = manager->error_code;
    return manager->error_message;
}

/* ===== 内部函数实现 ===== */

/**
 * 创建事件队列
 */
static EventQueue* create_event_queue(int capacity) {
    EventQueue* queue = (EventQueue*)malloc(sizeof(EventQueue));
    if (!queue) {
        return NULL;
    }
    
    queue->head = NULL;
    queue->tail = NULL;
    queue->size = 0;
    queue->capacity = capacity > 0 ? capacity : 100; // 默认容量
    
    return queue;
}

/**
 * 释放事件队列
 */
static void free_event_queue(EventQueue* queue) {
    if (!queue) return;
    
    // 释放所有队列节点
    EventQueueNode* current = queue->head;
    while (current) {
        EventQueueNode* next = current->next;
        
        // 释放事件资源
        free_integration_event(&(current->event));
        
        // 释放节点
        free(current);
        current = next;
    }
    
    // 释放队列本身
    free(queue);
}

/**
 * 推送事件到队列
 */
static int push_event(EventQueue* queue, IntegrationEvent* event) {
    if (!queue || !event) {
        return -1; // 参数错误
    }
    
    // 检查队列是否已满
    if (queue->size >= queue->capacity) {
        return -2; // 队列已满
    }
    
    // 创建新的队列节点
    EventQueueNode* node = (EventQueueNode*)malloc(sizeof(EventQueueNode));
    if (!node) {
        return -3; // 内存分配失败
    }
    
    // 复制事件数据
    node->event = *event; // 浅复制，假设event中的指针已经是深复制的
    node->event.sequence = queue->size + 1; // 分配序列号
    node->next = NULL;
    
    // 添加到队列尾部
    if (queue->tail) {
        queue->tail->next = node;
        queue->tail = node;
    } else {
        // 空队列
        queue->head = queue->tail = node;
    }
    
    queue->size++;
    return 0; // 成功
}

/**
 * 从队列中弹出事件
 */
static int pop_event(EventQueue* queue, IntegrationEvent* event) {
    if (!queue || !event || !queue->head) {
        return -1; // 参数错误或队列为空
    }
    
    // 获取队列头部节点
    EventQueueNode* node = queue->head;
    
    // 复制事件数据
    *event = node->event; // 浅复制，caller负责释放资源
    
    // 更新队列头部
    queue->head = node->next;
    if (!queue->head) {
        queue->tail = NULL; // 队列现在为空
    }
    
    // 释放节点（但不释放事件资源，由caller负责）
    free(node);
    
    queue->size--;
    return 0; // 成功
}

/**
 * 查找注册的模型
 */
static RegisteredModel* find_registered_model(IntegrationManager* manager, QuantumModelType type, const char* model_id) {
    if (!manager || !model_id) {
        return NULL;
    }
    
    for (int i = 0; i < manager->model_count; i++) {
        RegisteredModel* model = manager->registered_models[i];
        if (model && model->adapter && 
            model->adapter->model_type == type && 
            strcmp(model->adapter->model_id, model_id) == 0) {
            return model;
        }
    }
    
    return NULL; // 未找到
}

/**
 * 查找服务提供者
 */
static RegisteredServiceProvider* find_service_provider(IntegrationManager* manager, const char* service_id) {
    if (!manager || !service_id) {
        return NULL;
    }
    
    for (int i = 0; i < manager->provider_count; i++) {
        RegisteredServiceProvider* provider = manager->service_providers[i];
        if (provider && strcmp(provider->provider.service_id, service_id) == 0) {
            return provider;
        }
    }
    
    return NULL; // 未找到
}

/**
 * 获取当前时间戳（毫秒）
 */
static uint64_t get_current_timestamp() {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
}

/**
 * 复制字符串
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
 * 释放集成事件资源
 */
static void free_integration_event(IntegrationEvent* event) {
    if (!event) return;
    
    free(event->source_id);
    free(event->event_data);
}

/**
 * 验证模型适配器
 */
static int validate_model_adapter(ModelAdapter* adapter) {
    if (!adapter) return 0;
    
    // 检查必要的字段
    if (!adapter->model_id || !adapter->model_name) {
        return 0;
    }
    
    // 检查必要的函数
    if (!adapter->process_event) {
        return 0;
    }
    
    return 1; // 有效
}

/**
 * 量子模型集成框架测试
 * 
 * @return 成功返回0，失败返回错误码
 */
int quantum_model_integration_run_test(void) {
    printf("=== 量子模型集成框架测试 ===\n");
    
    // 创建集成管理器配置
    IntegrationManagerConfig config;
    config.default_mode = INTEGRATION_SYNC;
    config.event_queue_size = 100;
    config.max_service_providers = 50;
    config.sync_interval_ms = 1000;
    config.default_sync_strategy = SYNC_ALL;
    config.workspace_path = ".";
    config.log_level = 0;
    
    // 创建集成管理器
    IntegrationManager* manager = create_integration_manager(config);
    if (!manager) {
        printf("创建集成管理器失败\n");
        return -1;
    }
    
    printf("集成管理器创建成功\n");
    
    // TODO: 添加更多的测试代码，如创建模型适配器，注册服务提供者等
    
    // 清理资源
    free_integration_manager(manager);
    
    printf("=== 量子模型集成框架测试完成 ===\n");
    return 0;
} 