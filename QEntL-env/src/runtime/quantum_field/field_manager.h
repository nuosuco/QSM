/**
 * 量子场管理器头文件
 * 
 * 定义了用于创建、管理和操作量子场的接口和数据结构。
 * 量子场管理器是QEntL运行时系统中负责量子场生命周期管理的核心组件。
 */

#ifndef QENTL_FIELD_MANAGER_H
#define QENTL_FIELD_MANAGER_H

#include "../../quantum_field.h"
#include "../../quantum_field_generator.h"

/**
 * 量子场管理器错误枚举
 */
typedef enum {
    FIELD_MANAGER_ERROR_NONE = 0,                // 无错误
    FIELD_MANAGER_ERROR_INVALID_ARGUMENT,        // 无效参数
    FIELD_MANAGER_ERROR_MEMORY_ALLOCATION,       // 内存分配失败
    FIELD_MANAGER_ERROR_FIELD_NOT_FOUND,         // 字段未找到
    FIELD_MANAGER_ERROR_FIELD_ALREADY_EXISTS,    // 字段已存在
    FIELD_MANAGER_ERROR_INVALID_REFERENCE,       // 无效引用
    FIELD_MANAGER_ERROR_OPERATION_FAILED,        // 操作失败
    FIELD_MANAGER_ERROR_NOT_IMPLEMENTED,         // 功能未实现
    FIELD_MANAGER_ERROR_PERMISSION_DENIED,       // 权限被拒绝
    FIELD_MANAGER_ERROR_UNKNOWN                  // 未知错误
} FieldManagerError;

/**
 * 量子场引用
 * 用于安全地访问量子场，避免直接操作量子场指针
 */
typedef struct {
    QFieldID id;         // 字段ID
    void* field_ptr;           // 不透明字段指针
    int reference_count;       // 引用计数
} FieldReference;

/**
 * 量子场管理器配置
 */
typedef struct {
    int initial_capacity;      // 初始容量
    int enable_logging;        // 是否启用日志
    int auto_optimize;         // 是否自动优化
    int cache_enabled;         // 是否启用缓存
    char* log_file_path;       // 日志文件路径
} FieldManagerConfig;

/**
 * 量子场创建选项
 */
typedef struct {
    const char* name;          // 字段名称
    const char* description;   // 字段描述
    const char* tags;          // 标签（逗号分隔）
    FieldBoundaryType boundary_type; // 边界类型
    double x_min, x_max;       // X轴边界
    double y_min, y_max;       // Y轴边界
    double z_min, z_max;       // Z轴边界
} FieldCreationOptions;

/**
 * 量子场更新选项
 */
typedef struct {
    const char* name;          // 新名称
    const char* description;   // 新描述
    const char* tags;          // 新标签
    int update_name;           // 是否更新名称
    int update_description;    // 是否更新描述
    int update_tags;           // 是否更新标签
} FieldUpdateOptions;

/**
 * 量子场信息
 */
typedef struct {
    QFieldID id;         // 字段ID
    char* name;                // 名称
    char* description;         // 描述
    char* creation_time;       // 创建时间
    char* last_update_time;    // 最后更新时间
    int version;               // 版本号
    QFieldType type;     // 类型
    int node_count;            // 节点数量
    double energy;             // 能量
    double entropy;            // 熵
    FieldBoundaryType boundary_type; // 边界类型
    double x_min, x_max;       // X轴边界
    double y_min, y_max;       // Y轴边界
    double z_min, z_max;       // Z轴边界
    FieldManagerError error;   // 错误代码
} FieldInfo;

/**
 * 量子场引用列表
 */
typedef struct {
    FieldReference** references; // 引用数组
    int count;                 // 引用数量
    FieldManagerError error;   // 错误代码
} FieldReferenceList;

/**
 * 量子场管理器
 */
typedef struct {
    char* manager_id;                   // 管理器ID
    time_t creation_time;               // 创建时间
    QField** fields;              // 字段数组
    FieldReference** references;        // 引用数组
    int field_count;                    // 字段数量
    int field_capacity;                 // 字段容量
    QFieldGenerator* field_generator; // 字段生成器
    FieldManagerConfig config;          // 配置
} FieldManager;

/**
 * 初始化量子场管理器
 * 
 * @param config 管理器配置
 * @return 初始化的管理器，失败时返回NULL
 */
FieldManager* initialize_field_manager(FieldManagerConfig config);

/**
 * 关闭量子场管理器并释放资源
 * 
 * @param manager 要关闭的管理器
 */
void shutdown_field_manager(FieldManager* manager);

/**
 * 创建新的量子场
 * 
 * @param manager 管理器
 * @param type 量子场类型
 * @param options 创建选项
 * @return 新创建的量子场引用，失败时返回NULL
 */
FieldReference* create_field(FieldManager* manager, QFieldType type, FieldCreationOptions options);

/**
 * 删除量子场
 * 
 * @param manager 管理器
 * @param reference 要删除的量子场引用
 * @return 错误代码
 */
FieldManagerError delete_field(FieldManager* manager, FieldReference* reference);

/**
 * 获取量子场信息
 * 
 * @param manager 管理器
 * @param reference 量子场引用
 * @return 量子场信息
 */
FieldInfo get_field_info(FieldManager* manager, FieldReference* reference);

/**
 * 更新量子场
 * 
 * @param manager 管理器
 * @param reference 量子场引用
 * @param options 更新选项
 * @return 错误代码
 */
FieldManagerError update_field(FieldManager* manager, FieldReference* reference, FieldUpdateOptions options);

/**
 * 查找量子场
 * 
 * @param manager 管理器
 * @param field_id_str 量子场ID字符串
 * @return 量子场引用，未找到时返回NULL
 */
FieldReference* find_field(FieldManager* manager, const char* field_id_str);

/**
 * 获取所有量子场引用
 * 
 * @param manager 管理器
 * @return 量子场引用列表
 */
FieldReferenceList get_all_fields(FieldManager* manager);

/**
 * 释放字段引用列表
 * 
 * @param list 要释放的列表
 */
void free_field_reference_list(FieldReferenceList* list);

/**
 * 获取默认量子场管理器配置
 * 
 * @return 默认配置
 */
static inline FieldManagerConfig get_default_manager_config() {
    FieldManagerConfig config;
    config.initial_capacity = 10;
    config.enable_logging = 1;
    config.auto_optimize = 1;
    config.cache_enabled = 1;
    config.log_file_path = NULL;
    return config;
}

/**
 * 获取默认量子场创建选项
 * 
 * @return 默认创建选项
 */
static inline FieldCreationOptions get_default_creation_options() {
    FieldCreationOptions options;
    options.name = "未命名量子场";
    options.description = "默认创建的量子场";
    options.tags = "default";
    options.boundary_type = BOUNDARY_REFLECTIVE;
    options.x_min = -10.0;
    options.x_max = 10.0;
    options.y_min = -10.0;
    options.y_max = 10.0;
    options.z_min = -10.0;
    options.z_max = 10.0;
    return options;
}

#endif /* QENTL_FIELD_MANAGER_H */ 