/**
 * 量子纠缠处理器头文件
 * 
 * 该文件定义了量子纠缠处理器的数据结构和函数接口，用于管理量子纠缠通道的创建、
 * 维护、操作和销毁。纠缠处理器是QEntL运行时的核心组件之一。
 *
 * @file entanglement_processor.h
 * @version 1.0
 * @date 2024-05-15
 */

#ifndef QENTL_ENTANGLEMENT_PROCESSOR_H
#define QENTL_ENTANGLEMENT_PROCESSOR_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../../quantum_entanglement.h"
#include "../quantum_state/state_manager.h"

/**
 * 纠缠处理器错误码
 */
typedef enum {
    ENTANGLEMENT_PROCESSOR_ERROR_NONE = 0,                 // 无错误
    ENTANGLEMENT_PROCESSOR_ERROR_INVALID_ARGUMENT = 1,     // 无效参数
    ENTANGLEMENT_PROCESSOR_ERROR_MEMORY_ALLOCATION = 2,    // 内存分配错误
    ENTANGLEMENT_PROCESSOR_ERROR_CHANNEL_NOT_FOUND = 3,    // 通道未找到
    ENTANGLEMENT_PROCESSOR_ERROR_CHANNEL_EXISTS = 4,       // 通道已存在
    ENTANGLEMENT_PROCESSOR_ERROR_OPERATION_FAILED = 5,     // 操作失败
    ENTANGLEMENT_PROCESSOR_ERROR_INVALID_CHANNEL = 6,      // 无效的通道
    ENTANGLEMENT_PROCESSOR_ERROR_PROCESSOR_FULL = 7,       // 处理器已满
    ENTANGLEMENT_PROCESSOR_ERROR_INVALID_QUERY = 8,        // 无效的查询条件
    ENTANGLEMENT_PROCESSOR_ERROR_INVALID_STATE = 9,        // 无效状态
    ENTANGLEMENT_PROCESSOR_ERROR_STATES_NOT_COMPATIBLE = 10, // 状态不兼容
    ENTANGLEMENT_PROCESSOR_ERROR_ENTANGLEMENT_FAILED = 11, // 纠缠操作失败
    ENTANGLEMENT_PROCESSOR_ERROR_INTERNAL = 12             // 内部错误
} EntanglementProcessorError;

/**
 * 纠缠通道引用结构体
 * 用于引用一个纠缠通道，而不直接操作通道本身
 */
typedef struct {
    char* reference_id;                   // 引用ID
    EntanglementChannelID channel_id;     // 通道ID
    void* channel_ptr;                    // 指向通道的指针
    unsigned int reference_count;         // 引用计数
} ChannelReference;

/**
 * 通道查询条件
 */
typedef struct {
    char* name_pattern;                   // 名称模式（支持通配符）
    EntanglementType type;                // 纠缠类型
    double min_strength;                  // 最小强度
    double max_strength;                  // 最大强度
    time_t created_after;                 // 创建时间过滤（之后）
    time_t created_before;                // 创建时间过滤（之前）
    time_t updated_after;                 // 更新时间过滤（之后）
    time_t updated_before;                // 更新时间过滤（之前）
    char* source_state_id;                // 源状态ID
    char* target_state_id;                // 目标状态ID
    int max_results;                      // 最大结果数
    char* sort_by;                        // 排序字段
    int sort_ascending;                   // 排序方向(1=升序，0=降序)
} ChannelQueryCriteria;

/**
 * 通道查询结果
 */
typedef struct {
    ChannelReference** results;           // 引用数组
    int count;                            // 引用数量
    int total_matches;                    // 匹配的总数（可能大于count）
    EntanglementProcessorError error;     // 错误码
} ChannelQueryResult;

/**
 * 纠缠处理器配置
 */
typedef struct {
    int initial_capacity;                 // 初始容量
    int max_capacity;                     // 最大容量
    int auto_resize;                      // 是否自动调整大小
    int enable_logging;                   // 是否启用日志记录
    char* log_file_path;                  // 日志文件路径
    double cache_size_mb;                 // 缓存大小(MB)
    int enable_persistence;               // 是否启用持久化
    char* persistence_dir;                // 持久化目录
    int persistence_interval;             // 持久化间隔(秒)
    int thread_safe;                      // 是否线程安全
    int auto_refresh;                     // 是否自动刷新纠缠通道
    int refresh_interval;                 // 刷新间隔(秒)
} EntanglementProcessorConfig;

/**
 * 通道信息结构体
 * 用于返回通道的元数据信息
 */
typedef struct {
    EntanglementChannelID id;             // 通道ID
    char* name;                           // 名称
    char* description;                    // 描述
    EntanglementType type;                // 纠缠类型
    double strength;                      // 纠缠强度
    char* creation_time;                  // 创建时间
    char* last_update_time;               // 最后更新时间
    QuantumStateID source_state_id;       // 源状态ID
    QuantumStateID target_state_id;       // 目标状态ID
    int reference_count;                  // 引用计数
    EntanglementProcessorError error;     // 错误码
} ChannelInfo;

/**
 * 通道更新选项
 */
typedef struct {
    char* name;                           // 更新名称
    char* description;                    // 更新描述
    double strength;                      // 更新强度
    EntanglementType type;                // 更新类型
} ChannelUpdateOptions;

/**
 * 纠缠操作结果
 */
typedef struct {
    double initial_fidelity;              // 初始保真度
    double final_fidelity;                // 最终保真度
    double strength_change;               // 强度变化
    double energy_consumption;            // 能量消耗
    double coherence_time;                // 相干时间
    int success;                          // 操作是否成功
    EntanglementProcessorError error;     // 错误码
} EntanglementOperationResult;

/**
 * 纠缠处理器结构体
 */
typedef struct {
    EntanglementChannel** channels;       // 通道数组
    ChannelReference** references;        // 引用数组
    int channel_count;                    // 当前通道数量
    int capacity;                         // 当前容量
    EntanglementProcessorConfig config;   // 配置
    char* processor_id;                   // 处理器ID
    FILE* log_file;                       // 日志文件
    void* cache;                          // 缓存(内部实现)
    void* persistence_manager;            // 持久化管理器(内部实现)
    void* mutex;                          // 互斥锁(内部实现，线程安全时使用)
    StateManager* state_manager;          // 状态管理器引用
    time_t last_refresh_time;             // 最后刷新时间
    void* refresh_thread;                 // 刷新线程(内部实现)
} EntanglementProcessor;

/* 函数声明 */

/**
 * 初始化纠缠处理器
 * 
 * @param config 处理器配置
 * @param state_manager 状态管理器
 * @return 纠缠处理器指针，失败时返回NULL
 */
EntanglementProcessor* initialize_entanglement_processor(EntanglementProcessorConfig config, StateManager* state_manager);

/**
 * 获取默认纠缠处理器配置
 * 
 * @return 默认配置
 */
EntanglementProcessorConfig get_default_entanglement_processor_config();

/**
 * 关闭纠缠处理器
 * 
 * @param processor 纠缠处理器
 */
void shutdown_entanglement_processor(EntanglementProcessor* processor);

/**
 * 创建纠缠通道
 * 
 * @param processor 纠缠处理器
 * @param channel 纠缠通道
 * @return 通道引用，失败时返回NULL
 */
ChannelReference* create_channel(EntanglementProcessor* processor, EntanglementChannel* channel);

/**
 * 创建两个状态之间的纠缠通道
 * 
 * @param processor 纠缠处理器
 * @param source_ref 源状态引用
 * @param target_ref 目标状态引用
 * @param type 纠缠类型
 * @param initial_strength 初始强度
 * @param name 通道名称
 * @param description 通道描述
 * @return 通道引用，失败时返回NULL
 */
ChannelReference* create_entanglement(EntanglementProcessor* processor, 
                                   StateReference* source_ref, 
                                   StateReference* target_ref,
                                   EntanglementType type,
                                   double initial_strength,
                                   const char* name,
                                   const char* description);

/**
 * 获取通道引用
 * 
 * @param processor 纠缠处理器
 * @param channel_id 通道ID
 * @return 通道引用，失败时返回NULL
 */
ChannelReference* get_channel_reference(EntanglementProcessor* processor, EntanglementChannelID channel_id);

/**
 * 获取通道引用(通过引用ID)
 * 
 * @param processor 纠缠处理器
 * @param reference_id 引用ID
 * @return 通道引用，失败时返回NULL
 */
ChannelReference* get_channel_reference_by_id(EntanglementProcessor* processor, const char* reference_id);

/**
 * 更新纠缠通道
 * 
 * @param processor 纠缠处理器
 * @param reference 通道引用
 * @param options 更新选项
 * @return 错误码
 */
EntanglementProcessorError update_channel(EntanglementProcessor* processor, ChannelReference* reference, ChannelUpdateOptions options);

/**
 * 删除纠缠通道
 * 
 * @param processor 纠缠处理器
 * @param reference 通道引用
 * @return 错误码
 */
EntanglementProcessorError delete_channel(EntanglementProcessor* processor, ChannelReference* reference);

/**
 * 查询纠缠通道
 * 
 * @param processor 纠缠处理器
 * @param criteria 查询条件
 * @return 查询结果
 */
ChannelQueryResult query_channels(EntanglementProcessor* processor, ChannelQueryCriteria criteria);

/**
 * 获取通道信息
 * 
 * @param processor 纠缠处理器
 * @param reference 通道引用
 * @return 通道信息
 */
ChannelInfo get_channel_info(EntanglementProcessor* processor, ChannelReference* reference);

/**
 * 刷新纠缠通道
 * 
 * @param processor 纠缠处理器
 * @param reference 通道引用
 * @return 错误码
 */
EntanglementProcessorError refresh_channel(EntanglementProcessor* processor, ChannelReference* reference);

/**
 * 刷新所有纠缠通道
 * 
 * @param processor 纠缠处理器
 * @return 错误码
 */
EntanglementProcessorError refresh_all_channels(EntanglementProcessor* processor);

/**
 * 增强纠缠强度
 * 
 * @param processor 纠缠处理器
 * @param reference 通道引用
 * @param amount 增强量(0-1)
 * @return 操作结果
 */
EntanglementOperationResult enhance_entanglement(EntanglementProcessor* processor, ChannelReference* reference, double amount);

/**
 * 减弱纠缠强度
 * 
 * @param processor 纠缠处理器
 * @param reference 通道引用
 * @param amount 减弱量(0-1)
 * @return 操作结果
 */
EntanglementOperationResult weaken_entanglement(EntanglementProcessor* processor, ChannelReference* reference, double amount);

/**
 * 交换纠缠属性
 * 
 * @param processor 纠缠处理器
 * @param reference 通道引用
 * @param property_name 属性名称
 * @return 操作结果
 */
EntanglementOperationResult swap_entanglement_property(EntanglementProcessor* processor, ChannelReference* reference, const char* property_name);

/**
 * 测量纠缠通道
 * 
 * @param processor 纠缠处理器
 * @param reference 通道引用
 * @return 测量结果(0-1)，负值表示错误
 */
double measure_entanglement(EntanglementProcessor* processor, ChannelReference* reference);

/**
 * 纠缠两个现有状态
 * 
 * @param processor 纠缠处理器
 * @param source_ref 源状态引用
 * @param target_ref 目标状态引用
 * @param type 纠缠类型
 * @param initial_strength 初始强度
 * @return 操作结果
 */
EntanglementOperationResult entangle_states(EntanglementProcessor* processor, 
                                        StateReference* source_ref, 
                                        StateReference* target_ref,
                                        EntanglementType type,
                                        double initial_strength);

/**
 * 传输量子状态通过纠缠通道
 * 
 * @param processor 纠缠处理器
 * @param reference 通道引用
 * @param property_name 要传输的属性名称
 * @return 操作结果
 */
EntanglementOperationResult transmit_through_channel(EntanglementProcessor* processor, 
                                                ChannelReference* reference,
                                                const char* property_name);

/**
 * 释放通道查询结果
 * 
 * @param result 查询结果
 */
void free_channel_query_result(ChannelQueryResult* result);

/**
 * 释放通道信息
 * 
 * @param info 通道信息
 */
void free_channel_info(ChannelInfo* info);

/**
 * 获取纠缠处理器统计信息
 * 
 * @param processor 纠缠处理器
 * @param stats 输出统计信息
 * @return 错误码
 */
EntanglementProcessorError get_entanglement_processor_stats(EntanglementProcessor* processor, void* stats);

/**
 * 强制持久化通道
 * 
 * @param processor 纠缠处理器
 * @return 错误码
 */
EntanglementProcessorError force_persistence(EntanglementProcessor* processor);

#endif /* QENTL_ENTANGLEMENT_PROCESSOR_H */ 