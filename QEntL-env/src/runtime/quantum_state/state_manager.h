/**
 * 量子状态管理器头文件
 * 
 * 该文件定义了量子状态管理器的数据结构和函数接口，用于管理量子状态的创建、存储、
 * 检索、更新和删除等操作。状态管理器是QEntL运行时的核心组件之一。
 *
 * @file state_manager.h
 * @version 1.0
 * @date 2024-05-15
 */

#ifndef QENTL_STATE_MANAGER_H
#define QENTL_STATE_MANAGER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../../quantum_state.h"

/**
 * 状态管理器错误码
 */
typedef enum {
    STATE_MANAGER_ERROR_NONE = 0,                 // 无错误
    STATE_MANAGER_ERROR_INVALID_ARGUMENT = 1,     // 无效参数
    STATE_MANAGER_ERROR_MEMORY_ALLOCATION = 2,    // 内存分配错误
    STATE_MANAGER_ERROR_STATE_NOT_FOUND = 3,      // 状态未找到
    STATE_MANAGER_ERROR_STATE_ALREADY_EXISTS = 4, // 状态已经存在
    STATE_MANAGER_ERROR_OPERATION_FAILED = 5,     // 操作失败
    STATE_MANAGER_ERROR_INVALID_STATE = 6,        // 无效的状态
    STATE_MANAGER_ERROR_MANAGER_FULL = 7,         // 管理器已满
    STATE_MANAGER_ERROR_INVALID_QUERY = 8,        // 无效的查询条件
    STATE_MANAGER_ERROR_INTERNAL = 9              // 内部错误
} StateManagerError;

/**
 * 状态引用结构体
 * 用于引用一个量子状态，而不直接操作状态本身
 */
typedef struct {
    char* reference_id;             // 引用ID
    QuantumStateID state_id;        // 状态ID
    void* state_ptr;                // 指向状态的指针
    unsigned int reference_count;   // 引用计数
} StateReference;

/**
 * 状态查询条件
 */
typedef struct {
    char* name_pattern;             // 名称模式（支持通配符）
    char* tags;                     // 标签过滤
    double min_fidelity;            // 最小保真度
    double max_fidelity;            // 最大保真度
    int min_dimensions;             // 最小维度
    int max_dimensions;             // 最大维度
    time_t created_after;           // 创建时间过滤（之后）
    time_t created_before;          // 创建时间过滤（之前）
    time_t updated_after;           // 更新时间过滤（之后）
    time_t updated_before;          // 更新时间过滤（之前）
    int max_results;                // 最大结果数
    char* sort_by;                  // 排序字段
    int sort_ascending;             // 排序方向(1=升序，0=降序)
} StateQueryCriteria;

/**
 * 状态查询结果
 */
typedef struct {
    StateReference** results;       // 引用数组
    int count;                      // 引用数量
    int total_matches;              // 匹配的总数（可能大于count）
    StateManagerError error;        // 错误码
} StateQueryResult;

/**
 * 状态管理器配置
 */
typedef struct {
    int initial_capacity;           // 初始容量
    int max_capacity;               // 最大容量
    int auto_resize;                // 是否自动调整大小
    int enable_logging;             // 是否启用日志记录
    char* log_file_path;            // 日志文件路径
    double cache_size_mb;           // 缓存大小(MB)
    int enable_persistence;         // 是否启用持久化
    char* persistence_dir;          // 持久化目录
    int persistence_interval;       // 持久化间隔(秒)
    int thread_safe;                // 是否线程安全
} StateManagerConfig;

/**
 * 状态信息结构体
 * 用于返回状态的元数据信息
 */
typedef struct {
    QuantumStateID id;              // 状态ID
    char* name;                     // 名称
    char* description;              // 描述
    int dimensions;                 // 维度
    double fidelity;                // 保真度
    char* creation_time;            // 创建时间
    char* last_update_time;         // 最后更新时间
    int property_count;             // 属性数量
    char** property_names;          // 属性名称数组
    int reference_count;            // 引用计数
    StateManagerError error;        // 错误码
} StateInfo;

/**
 * 状态更新选项
 */
typedef struct {
    char* name;                     // 更新名称
    char* description;              // 更新描述
    double fidelity;                // 更新保真度
    QuantumStateProperty* properties_to_add;    // 要添加的属性
    int properties_add_count;                   // 要添加的属性数量
    char** properties_to_remove;    // 要移除的属性名
    int properties_remove_count;    // 要移除的属性数量
} StateUpdateOptions;

/**
 * 状态管理器结构体
 */
typedef struct {
    QuantumState** states;          // 状态数组
    StateReference** references;    // 引用数组
    int state_count;                // 当前状态数量
    int capacity;                   // 当前容量
    StateManagerConfig config;      // 配置
    char* manager_id;               // 管理器ID
    FILE* log_file;                 // 日志文件
    void* cache;                    // 缓存(内部实现)
    void* persistence_manager;      // 持久化管理器(内部实现)
    void* mutex;                    // 互斥锁(内部实现，线程安全时使用)
} StateManager;

/* 函数声明 */

/**
 * 初始化状态管理器
 * 
 * @param config 管理器配置
 * @return 状态管理器指针，失败时返回NULL
 */
StateManager* initialize_state_manager(StateManagerConfig config);

/**
 * 获取默认状态管理器配置
 * 
 * @return 默认配置
 */
StateManagerConfig get_default_state_manager_config();

/**
 * 关闭状态管理器
 * 
 * @param manager 状态管理器
 */
void shutdown_state_manager(StateManager* manager);

/**
 * 创建量子状态
 * 
 * @param manager 状态管理器
 * @param state 量子状态
 * @return 状态引用，失败时返回NULL
 */
StateReference* create_state(StateManager* manager, QuantumState* state);

/**
 * 获取状态引用
 * 
 * @param manager 状态管理器
 * @param state_id 状态ID
 * @return 状态引用，失败时返回NULL
 */
StateReference* get_state_reference(StateManager* manager, QuantumStateID state_id);

/**
 * 获取状态引用(通过引用ID)
 * 
 * @param manager 状态管理器
 * @param reference_id 引用ID
 * @return 状态引用，失败时返回NULL
 */
StateReference* get_state_reference_by_id(StateManager* manager, const char* reference_id);

/**
 * 更新量子状态
 * 
 * @param manager 状态管理器
 * @param reference 状态引用
 * @param options 更新选项
 * @return 错误码
 */
StateManagerError update_state(StateManager* manager, StateReference* reference, StateUpdateOptions options);

/**
 * 删除量子状态
 * 
 * @param manager 状态管理器
 * @param reference 状态引用
 * @return 错误码
 */
StateManagerError delete_state(StateManager* manager, StateReference* reference);

/**
 * 查询量子状态
 * 
 * @param manager 状态管理器
 * @param criteria 查询条件
 * @return 查询结果
 */
StateQueryResult query_states(StateManager* manager, StateQueryCriteria criteria);

/**
 * 获取状态信息
 * 
 * @param manager 状态管理器
 * @param reference 状态引用
 * @return 状态信息
 */
StateInfo get_state_info(StateManager* manager, StateReference* reference);

/**
 * 比较两个量子状态
 * 
 * @param manager 状态管理器
 * @param ref1 状态引用1
 * @param ref2 状态引用2
 * @return 相似度(0-1)，-1表示错误
 */
double compare_states(StateManager* manager, StateReference* ref1, StateReference* ref2);

/**
 * 克隆量子状态
 * 
 * @param manager 状态管理器
 * @param reference 原始状态引用
 * @param new_name 新状态名称
 * @return 新状态引用，失败时返回NULL
 */
StateReference* clone_state(StateManager* manager, StateReference* reference, const char* new_name);

/**
 * 导出量子状态
 * 
 * @param manager 状态管理器
 * @param reference 状态引用
 * @param format 导出格式
 * @param file_path 文件路径
 * @return 错误码
 */
StateManagerError export_state(StateManager* manager, StateReference* reference, const char* format, const char* file_path);

/**
 * 导入量子状态
 * 
 * @param manager 状态管理器
 * @param format 导入格式
 * @param file_path 文件路径
 * @return 状态引用，失败时返回NULL
 */
StateReference* import_state(StateManager* manager, const char* format, const char* file_path);

/**
 * 释放状态查询结果
 * 
 * @param result 查询结果
 */
void free_state_query_result(StateQueryResult* result);

/**
 * 释放状态信息
 * 
 * @param info 状态信息
 */
void free_state_info(StateInfo* info);

/**
 * 获取状态管理器统计信息
 * 
 * @param manager 状态管理器
 * @param stats 输出统计信息
 * @return 错误码
 */
StateManagerError get_state_manager_stats(StateManager* manager, void* stats);

/**
 * 强制持久化状态
 * 
 * @param manager 状态管理器
 * @return 错误码
 */
StateManagerError force_persistence(StateManager* manager);

#endif /* QENTL_STATE_MANAGER_H */ 