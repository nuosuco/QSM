/**
 * 量子模型集成框架
 * 
 * 提供QEntL环境中不同量子模型间的无缝集成机制，包括状态同步、事件传播和服务发现。
 * 支持QSM、SOM、REF和WeQ四个核心模型的互操作。
 * 
 * 该框架完全自主开发，不依赖任何第三方技术。
 */

#ifndef QUANTUM_MODEL_INTEGRATION_H
#define QUANTUM_MODEL_INTEGRATION_H

#include <stdint.h>
#include <stdlib.h>
#include "../../quantum_state.h"
#include "../../quantum_entanglement.h"
#include "../../quantum_field.h"

/**
 * 集成模型类型枚举
 */
typedef enum {
    MODEL_QSM,                 // 量子叠加模型
    MODEL_SOM,                 // 自组织模型
    MODEL_REF,                 // 反思评估模型
    MODEL_WEQ,                 // WeQ模型
    MODEL_CUSTOM,              // 自定义模型
    MODEL_COUNT                // 模型数量（用于内部计算）
} QuantumModelType;

/**
 * 集成模式枚举
 */
typedef enum {
    INTEGRATION_SYNC,          // 同步模式 - 操作会等待所有模型响应
    INTEGRATION_ASYNC,         // 异步模式 - 操作不等待响应
    INTEGRATION_SELECTIVE,     // 选择性模式 - 只与指定模型同步
    INTEGRATION_PRIORITIZED    // 优先级模式 - 按优先级顺序处理
} IntegrationMode;

/**
 * 集成事件类型枚举
 */
typedef enum {
    EVENT_STATE_CHANGED,       // 量子状态变化
    EVENT_ENTANGLEMENT_CREATED,// 创建量子纠缠
    EVENT_ENTANGLEMENT_BROKEN, // 量子纠缠断开
    EVENT_FIELD_UPDATED,       // 量子场更新
    EVENT_MODEL_REGISTERED,    // 模型注册
    EVENT_MODEL_UNREGISTERED,  // 模型注销
    EVENT_SERVICE_DISCOVERED,  // 服务发现
    EVENT_SYNC_REQUESTED,      // 同步请求
    EVENT_SYNC_COMPLETED,      // 同步完成
    EVENT_ERROR_OCCURRED,      // 错误发生
    EVENT_CUSTOM               // 自定义事件
} IntegrationEventType;

/**
 * 集成服务角色枚举
 */
typedef enum {
    ROLE_PROVIDER,             // 服务提供者
    ROLE_CONSUMER,             // 服务消费者
    ROLE_BOTH                  // 提供者和消费者
} ServiceRole;

/**
 * 服务提供者接口定义
 */
typedef struct {
    char* service_id;          // 服务ID
    char* service_name;        // 服务名称
    char* service_uri;         // 服务URI
    ServiceRole role;          // 服务角色
    QuantumModelType model_type; // 所属模型类型
    void* capabilities;        // 能力描述（自定义结构）
} ServiceProvider;

/**
 * 同步策略枚举
 */
typedef enum {
    SYNC_QUANTUM_STATE,        // 量子状态同步
    SYNC_ENTANGLEMENT,         // 量子纠缠同步
    SYNC_FIELD,                // 量子场同步
    SYNC_EVENTS,               // 事件同步
    SYNC_ALL                   // 全部同步
} SyncStrategy;

/**
 * 集成事件结构
 */
typedef struct {
    IntegrationEventType type;     // 事件类型
    char* source_id;               // 事件源ID
    QuantumModelType source_model; // 事件源模型
    void* event_data;              // 事件数据
    uint64_t timestamp;            // 事件时间戳
    uint32_t sequence;             // 事件序列号
} IntegrationEvent;

/**
 * 事件处理回调函数类型
 */
typedef void (*EventHandlerCallback)(IntegrationEvent* event, void* user_data);

/**
 * 模型适配器接口
 * 每个模型实现此接口以接入集成框架
 */
typedef struct {
    QuantumModelType model_type;      // 模型类型
    char* model_id;                   // 模型实例ID
    char* model_name;                 // 模型名称
    char* model_version;              // 模型版本
    
    // 模型生命周期管理函数
    int (*initialize)(void* config);               // 初始化函数
    int (*start)(void);                            // 启动函数
    int (*stop)(void);                             // 停止函数
    int (*cleanup)(void);                          // 清理函数
    
    // 状态管理函数
    int (*export_state)(void** state_data, size_t* data_size);  // 导出状态
    int (*import_state)(void* state_data, size_t data_size);    // 导入状态
    int (*validate_state)(void* state_data, size_t data_size);  // 验证状态
    
    // 事件处理函数
    int (*process_event)(IntegrationEvent* event);               // 处理事件
    int (*subscribe_event)(IntegrationEventType event_type);     // 订阅事件
    int (*unsubscribe_event)(IntegrationEventType event_type);   // 取消订阅事件
    
    // 服务管理函数
    int (*register_service)(ServiceProvider* provider);     // 注册服务
    int (*unregister_service)(const char* service_id);      // 注销服务
    int (*discover_services)(QuantumModelType model_type);  // 发现服务
} ModelAdapter;

/**
 * 集成管理器配置
 */
typedef struct {
    IntegrationMode default_mode;           // 默认集成模式
    int event_queue_size;                   // 事件队列大小
    int max_service_providers;              // 最大服务提供者数量
    int sync_interval_ms;                   // 同步间隔（毫秒）
    SyncStrategy default_sync_strategy;     // 默认同步策略
    char* workspace_path;                   // 工作空间路径
    int log_level;                          // 日志级别
} IntegrationManagerConfig;

/**
 * 量子模型集成管理器
 * 核心集成组件，管理模型之间的集成
 */
typedef struct {
    IntegrationManagerConfig config;              // 配置
    ModelAdapter** registered_adapters;           // 已注册适配器数组
    int adapter_count;                            // 适配器数量
    ServiceProvider** service_providers;          // 服务提供者数组
    int provider_count;                           // 提供者数量
    IntegrationEvent** event_queue;               // 事件队列
    int event_queue_head;                         // 队列头索引
    int event_queue_tail;                         // 队列尾索引
    EventHandlerCallback* event_handlers;         // 事件处理器数组
    void** event_handler_user_data;               // 事件处理器用户数据
    int handler_count;                            // 处理器数量
} IntegrationManager;

/* ===== 量子模型集成管理器API ===== */

/**
 * 创建量子模型集成管理器
 * 
 * @param config 集成管理器配置
 * @return 新创建的集成管理器指针，失败返回NULL
 */
IntegrationManager* create_integration_manager(IntegrationManagerConfig config);

/**
 * 释放量子模型集成管理器资源
 * 
 * @param manager 集成管理器指针
 */
void free_integration_manager(IntegrationManager* manager);

/**
 * 注册模型适配器
 * 
 * @param manager 集成管理器指针
 * @param adapter 模型适配器指针
 * @return 成功返回0，失败返回错误码
 */
int register_model_adapter(IntegrationManager* manager, ModelAdapter* adapter);

/**
 * 注销模型适配器
 * 
 * @param manager 集成管理器指针
 * @param model_type 模型类型
 * @param model_id 模型实例ID
 * @return 成功返回0，失败返回错误码
 */
int unregister_model_adapter(IntegrationManager* manager, QuantumModelType model_type, const char* model_id);

/**
 * 添加事件处理器
 * 
 * @param manager 集成管理器指针
 * @param callback 事件处理回调函数
 * @param user_data 用户数据指针
 * @return 成功返回处理器ID，失败返回-1
 */
int add_event_handler(IntegrationManager* manager, EventHandlerCallback callback, void* user_data);

/**
 * 移除事件处理器
 * 
 * @param manager 集成管理器指针
 * @param handler_id 处理器ID
 * @return 成功返回0，失败返回错误码
 */
int remove_event_handler(IntegrationManager* manager, int handler_id);

/**
 * 发布集成事件
 * 
 * @param manager 集成管理器指针
 * @param event 事件指针
 * @return 成功返回0，失败返回错误码
 */
int publish_event(IntegrationManager* manager, IntegrationEvent* event);

/**
 * 处理集成事件队列
 * 
 * @param manager 集成管理器指针
 * @return 处理的事件数量
 */
int process_event_queue(IntegrationManager* manager);

/**
 * 注册服务提供者
 * 
 * @param manager 集成管理器指针
 * @param provider 服务提供者指针
 * @return 成功返回0，失败返回错误码
 */
int register_service_provider(IntegrationManager* manager, ServiceProvider* provider);

/**
 * 发现服务提供者
 * 
 * @param manager 集成管理器指针
 * @param model_type 模型类型（可选）
 * @param service_name 服务名称（可选）
 * @param results 结果数组指针的地址
 * @param result_count 结果数量指针
 * @return 成功返回0，失败返回错误码
 */
int discover_service_providers(IntegrationManager* manager, QuantumModelType model_type, 
                             const char* service_name, ServiceProvider*** results, int* result_count);

/**
 * 同步特定类型的状态到所有注册的模型
 * 
 * @param manager 集成管理器指针
 * @param strategy 同步策略
 * @param source_model 源模型类型
 * @param source_id 源模型ID
 * @param mode 集成模式
 * @return 成功返回0，失败返回错误码
 */
int synchronize_state(IntegrationManager* manager, SyncStrategy strategy, 
                    QuantumModelType source_model, const char* source_id, 
                    IntegrationMode mode);

/**
 * 创建新的集成事件
 * 
 * @param type 事件类型
 * @param source_id 事件源ID
 * @param source_model 事件源模型
 * @param event_data 事件数据
 * @return 新创建的事件指针，失败返回NULL
 */
IntegrationEvent* create_integration_event(IntegrationEventType type, const char* source_id,
                                       QuantumModelType source_model, void* event_data);

/**
 * 释放集成事件资源
 * 
 * @param event 事件指针
 */
void free_integration_event(IntegrationEvent* event);

/**
 * 创建服务提供者
 * 
 * @param service_id 服务ID
 * @param service_name 服务名称
 * @param service_uri 服务URI
 * @param role 服务角色
 * @param model_type 模型类型
 * @param capabilities 能力描述（可选）
 * @return 新创建的服务提供者指针，失败返回NULL
 */
ServiceProvider* create_service_provider(const char* service_id, const char* service_name,
                                     const char* service_uri, ServiceRole role,
                                     QuantumModelType model_type, void* capabilities);

/**
 * 释放服务提供者资源
 * 
 * @param provider 服务提供者指针
 */
void free_service_provider(ServiceProvider* provider);

/**
 * 创建默认集成管理器配置
 * 
 * @return 默认配置
 */
IntegrationManagerConfig create_default_integration_config();

/* ===== 模型适配器辅助函数 ===== */

/**
 * 创建基本模型适配器
 * 
 * @param model_type 模型类型
 * @param model_id 模型ID
 * @param model_name 模型名称
 * @param model_version 模型版本
 * @return 新创建的模型适配器指针，失败返回NULL
 */
ModelAdapter* create_basic_model_adapter(QuantumModelType model_type, const char* model_id,
                                     const char* model_name, const char* model_version);

/**
 * 释放模型适配器资源
 * 
 * @param adapter 适配器指针
 */
void free_model_adapter(ModelAdapter* adapter);

/* ===== 量子状态转换函数 ===== */

/**
 * 将量子状态转换为跨模型传输格式
 * 
 * @param state 量子状态指针
 * @param output_data 输出数据的指针地址
 * @param data_size 数据大小指针
 * @return 成功返回0，失败返回错误码
 */
int convert_quantum_state_to_transport(QuantumState* state, void** output_data, size_t* data_size);

/**
 * 从跨模型传输格式还原量子状态
 * 
 * @param data 传输数据
 * @param data_size 数据大小
 * @return 新创建的量子状态指针，失败返回NULL
 */
QuantumState* convert_transport_to_quantum_state(void* data, size_t data_size);

/**
 * 将量子纠缠转换为跨模型传输格式
 * 
 * @param entanglement 量子纠缠指针
 * @param output_data 输出数据的指针地址
 * @param data_size 数据大小指针
 * @return 成功返回0，失败返回错误码
 */
int convert_entanglement_to_transport(EntanglementChannel* entanglement, 
                                    void** output_data, size_t* data_size);

/**
 * 从跨模型传输格式还原量子纠缠
 * 
 * @param data 传输数据
 * @param data_size 数据大小
 * @return 新创建的量子纠缠指针，失败返回NULL
 */
EntanglementChannel* convert_transport_to_entanglement(void* data, size_t data_size);

/* ===== 量子场转换函数 ===== */

/**
 * 将量子场转换为跨模型传输格式
 * 
 * @param field 量子场指针
 * @param output_data 输出数据的指针地址
 * @param data_size 数据大小指针
 * @return 成功返回0，失败返回错误码
 */
int convert_quantum_field_to_transport(QField* field, void** output_data, size_t* data_size);

/**
 * 从跨模型传输格式还原量子场
 * 
 * @param data 传输数据
 * @param data_size 数据大小
 * @return 新创建的量子场指针，失败返回NULL
 */
QField* convert_transport_to_quantum_field(void* data, size_t data_size);

/* ===== 辅助函数 ===== */

/**
 * 获取模型类型名称
 * 
 * @param model_type 模型类型
 * @return 模型类型名称字符串
 */
const char* get_model_type_name(QuantumModelType model_type);

/**
 * 获取集成事件类型名称
 * 
 * @param event_type 事件类型
 * @return 事件类型名称字符串
 */
const char* get_event_type_name(IntegrationEventType event_type);

/**
 * 获取同步策略名称
 * 
 * @param strategy 同步策略
 * @return 同步策略名称字符串
 */
const char* get_sync_strategy_name(SyncStrategy strategy);

#endif /* QUANTUM_MODEL_INTEGRATION_H */ 