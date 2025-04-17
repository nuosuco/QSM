/**
 * 量子场管理器实现
 * 
 * 提供量子场的创建、管理、查询和操作功能，是QEntL运行时系统中
 * 负责量子场生命周期和行为的核心组件。
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "../../quantum_field.h"
#include "../../quantum_field_generator.h"
#include "field_manager.h"

/* 内部全局变量 */
static FieldManager* global_field_manager = NULL;
static int initialized = 0;

/* 内部辅助函数声明 */
static char* generate_manager_id();
static FieldManagerError check_field_exists(FieldManager* manager, QFieldID field_id);
static void log_manager_action(FieldManager* manager, const char* action, const char* details);
static FieldReference* create_field_reference(QField* field);
static void free_field_reference(FieldReference* reference);
static QField* get_field_by_reference(FieldReference* reference);

/**
 * 初始化量子场管理器
 */
FieldManager* initialize_field_manager(FieldManagerConfig config) {
    // 如果已经初始化，则返回全局实例
    if (initialized && global_field_manager) {
        return global_field_manager;
    }
    
    // 分配内存
    FieldManager* manager = (FieldManager*)malloc(sizeof(FieldManager));
    if (!manager) {
        fprintf(stderr, "无法分配量子场管理器内存\n");
        return NULL;
    }
    
    // 设置基本属性
    manager->manager_id = generate_manager_id();
    manager->creation_time = time(NULL);
    manager->fields = NULL;
    manager->field_count = 0;
    manager->field_capacity = config.initial_capacity > 0 ? config.initial_capacity : 10;
    manager->config = config;
    
    // 分配字段数组
    manager->fields = (QField**)malloc(sizeof(QField*) * manager->field_capacity);
    if (!manager->fields) {
        fprintf(stderr, "无法分配量子场数组内存\n");
        free(manager->manager_id);
        free(manager);
        return NULL;
    }
    
    // 初始化字段引用
    manager->references = (FieldReference**)malloc(sizeof(FieldReference*) * manager->field_capacity);
    if (!manager->references) {
        fprintf(stderr, "无法分配字段引用数组内存\n");
        free(manager->fields);
        free(manager->manager_id);
        free(manager);
        return NULL;
    }
    
    // 初始化引用数组
    for (int i = 0; i < manager->field_capacity; i++) {
        manager->fields[i] = NULL;
        manager->references[i] = NULL;
    }
    
    // 初始化场生成器
    manager->field_generator = create_quantum_field_generator("FieldManager生成器");
    if (!manager->field_generator) {
        fprintf(stderr, "无法创建量子场生成器\n");
        free(manager->references);
        free(manager->fields);
        free(manager->manager_id);
        free(manager);
        return NULL;
    }
    
    // 设置全局实例
    global_field_manager = manager;
    initialized = 1;
    
    // 记录初始化成功
    log_manager_action(manager, "初始化", "量子场管理器初始化成功");
    
    printf("量子场管理器初始化成功 (ID: %s)\n", manager->manager_id);
    return manager;
}

/**
 * 关闭量子场管理器并释放资源
 */
void shutdown_field_manager(FieldManager* manager) {
    if (!manager) return;
    
    // 记录关闭操作
    log_manager_action(manager, "关闭", "释放量子场管理器资源");
    
    // 释放所有字段和引用
    for (int i = 0; i < manager->field_count; i++) {
        if (manager->fields[i]) {
            free_quantum_field(manager->fields[i]);
        }
        if (manager->references[i]) {
            free_field_reference(manager->references[i]);
        }
    }
    
    // 释放场生成器
    if (manager->field_generator) {
        free_quantum_field_generator(manager->field_generator);
    }
    
    // 释放数组
    free(manager->fields);
    free(manager->references);
    
    // 释放管理器ID
    free(manager->manager_id);
    
    // 释放管理器本身
    free(manager);
    
    // 重置全局变量
    if (global_field_manager == manager) {
        global_field_manager = NULL;
        initialized = 0;
    }
    
    printf("量子场管理器已关闭\n");
}

/**
 * 创建新的量子场
 */
FieldReference* create_field(FieldManager* manager, QFieldType type, FieldCreationOptions options) {
    if (!manager) return NULL;
    
    // 检查容量
    if (manager->field_count >= manager->field_capacity) {
        // 扩展容量
        int new_capacity = manager->field_capacity * 2;
        QField** new_fields = (QField**)realloc(manager->fields, 
                                                         sizeof(QField*) * new_capacity);
        FieldReference** new_references = (FieldReference**)realloc(manager->references, 
                                                                 sizeof(FieldReference*) * new_capacity);
        
        if (!new_fields || !new_references) {
            fprintf(stderr, "无法扩展量子场管理器容量\n");
            return NULL;
        }
        
        manager->fields = new_fields;
        manager->references = new_references;
        
        // 初始化新分配的空间
        for (int i = manager->field_capacity; i < new_capacity; i++) {
            manager->fields[i] = NULL;
            manager->references[i] = NULL;
        }
        
        manager->field_capacity = new_capacity;
    }
    
    // 创建边界条件
    FieldBoundaryCondition boundary;
    boundary.type = options.boundary_type;
    boundary.x_min = options.x_min;
    boundary.x_max = options.x_max;
    boundary.y_min = options.y_min;
    boundary.y_max = options.y_max;
    boundary.z_min = options.z_min;
    boundary.z_max = options.z_max;
    boundary.custom_boundary_data = NULL;
    
    // 创建量子场
    QField* field = create_field_of_type(type, boundary);
    if (!field) {
        fprintf(stderr, "无法创建量子场\n");
        return NULL;
    }
    
    // 设置元数据
    QFieldMetadata metadata;
    metadata.name = strdup(options.name ? options.name : "未命名量子场");
    metadata.description = strdup(options.description ? options.description : "");
    
    // 获取当前时间戳
    time_t now = time(NULL);
    char timestamp[64];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(&now));
    
    metadata.creation_timestamp = strdup(timestamp);
    metadata.last_update_timestamp = strdup(timestamp);
    metadata.creator_id = strdup(manager->manager_id);
    metadata.version = 1;
    metadata.tags = strdup(options.tags ? options.tags : "");
    
    set_field_metadata(field, metadata);
    
    // 添加到管理器
    manager->fields[manager->field_count] = field;
    
    // 创建引用
    FieldReference* reference = create_field_reference(field);
    manager->references[manager->field_count] = reference;
    
    // 增加计数
    manager->field_count++;
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "创建类型为 %d 的量子场，名称: %s", 
             type, metadata.name);
    log_manager_action(manager, "创建量子场", details);
    
    printf("已创建量子场: %s (ID: %s)\n", metadata.name, field->id.readable_id);
    return reference;
}

/**
 * 删除量子场
 */
FieldManagerError delete_field(FieldManager* manager, FieldReference* reference) {
    if (!manager || !reference) return FIELD_MANAGER_ERROR_INVALID_ARGUMENT;
    
    QField* field = get_field_by_reference(reference);
    if (!field) return FIELD_MANAGER_ERROR_INVALID_REFERENCE;
    
    // 查找字段索引
    int field_index = -1;
    for (int i = 0; i < manager->field_count; i++) {
        if (compare_field_ids(manager->fields[i]->id, field->id) == 0) {
            field_index = i;
            break;
        }
    }
    
    if (field_index == -1) {
        return FIELD_MANAGER_ERROR_FIELD_NOT_FOUND;
    }
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "删除量子场 (ID: %s)", 
             field->id.readable_id);
    log_manager_action(manager, "删除量子场", details);
    
    // 释放字段和引用
    free_quantum_field(manager->fields[field_index]);
    free_field_reference(manager->references[field_index]);
    
    // 调整数组
    for (int i = field_index; i < manager->field_count - 1; i++) {
        manager->fields[i] = manager->fields[i + 1];
        manager->references[i] = manager->references[i + 1];
    }
    
    // 减少计数
    manager->field_count--;
    
    // 清空最后一个元素
    manager->fields[manager->field_count] = NULL;
    manager->references[manager->field_count] = NULL;
    
    printf("已删除量子场 (ID: %s)\n", field->id.readable_id);
    return FIELD_MANAGER_ERROR_NONE;
}

/**
 * 获取量子场信息
 */
FieldInfo get_field_info(FieldManager* manager, FieldReference* reference) {
    FieldInfo info;
    memset(&info, 0, sizeof(FieldInfo));
    
    if (!manager || !reference) {
        info.error = FIELD_MANAGER_ERROR_INVALID_ARGUMENT;
        return info;
    }
    
    QField* field = get_field_by_reference(reference);
    if (!field) {
        info.error = FIELD_MANAGER_ERROR_INVALID_REFERENCE;
        return info;
    }
    
    // 复制ID
    memcpy(&info.id, &field->id, sizeof(QFieldID));
    
    // 获取元数据
    QFieldMetadata metadata = get_field_metadata(field);
    info.name = strdup(metadata.name);
    info.description = strdup(metadata.description);
    info.creation_time = strdup(metadata.creation_timestamp);
    info.last_update_time = strdup(metadata.last_update_timestamp);
    info.version = metadata.version;
    
    // 设置字段特性
    info.type = field->type;
    info.node_count = field->node_count;
    info.energy = calculate_field_energy(field);
    info.entropy = calculate_field_entropy(field);
    
    // 设置边界信息
    info.boundary_type = field->boundary.type;
    info.x_min = field->boundary.x_min;
    info.x_max = field->boundary.x_max;
    info.y_min = field->boundary.y_min;
    info.y_max = field->boundary.y_max;
    info.z_min = field->boundary.z_min;
    info.z_max = field->boundary.z_max;
    
    info.error = FIELD_MANAGER_ERROR_NONE;
    return info;
}

/**
 * 更新量子场
 */
FieldManagerError update_field(FieldManager* manager, FieldReference* reference, 
                              FieldUpdateOptions options) {
    if (!manager || !reference) return FIELD_MANAGER_ERROR_INVALID_ARGUMENT;
    
    QField* field = get_field_by_reference(reference);
    if (!field) return FIELD_MANAGER_ERROR_INVALID_REFERENCE;
    
    // 获取当前元数据
    QFieldMetadata metadata = get_field_metadata(field);
    
    // 更新元数据
    if (options.update_name && options.name) {
        free(metadata.name);
        metadata.name = strdup(options.name);
    }
    
    if (options.update_description && options.description) {
        free(metadata.description);
        metadata.description = strdup(options.description);
    }
    
    if (options.update_tags && options.tags) {
        free(metadata.tags);
        metadata.tags = strdup(options.tags);
    }
    
    // 获取当前时间戳
    time_t now = time(NULL);
    char timestamp[64];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(&now));
    
    free(metadata.last_update_timestamp);
    metadata.last_update_timestamp = strdup(timestamp);
    
    // 增加版本号
    metadata.version++;
    
    // 更新元数据
    set_field_metadata(field, metadata);
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "更新量子场 (ID: %s), 版本: %d", 
             field->id.readable_id, metadata.version);
    log_manager_action(manager, "更新量子场", details);
    
    printf("已更新量子场: %s (ID: %s), 版本: %d\n", 
           metadata.name, field->id.readable_id, metadata.version);
    return FIELD_MANAGER_ERROR_NONE;
}

/**
 * 查找量子场
 */
FieldReference* find_field(FieldManager* manager, const char* field_id_str) {
    if (!manager || !field_id_str) return NULL;
    
    QFieldID search_id = create_field_id_from_string(field_id_str);
    
    // 查找匹配的字段
    for (int i = 0; i < manager->field_count; i++) {
        if (compare_field_ids(manager->fields[i]->id, search_id) == 0) {
            return manager->references[i];
        }
    }
    
    return NULL;
}

/**
 * 获取所有量子场引用
 */
FieldReferenceList get_all_fields(FieldManager* manager) {
    FieldReferenceList list;
    list.count = 0;
    list.references = NULL;
    list.error = FIELD_MANAGER_ERROR_NONE;
    
    if (!manager) {
        list.error = FIELD_MANAGER_ERROR_INVALID_ARGUMENT;
        return list;
    }
    
    if (manager->field_count == 0) {
        return list;
    }
    
    // 分配引用数组
    list.references = (FieldReference**)malloc(sizeof(FieldReference*) * manager->field_count);
    if (!list.references) {
        list.error = FIELD_MANAGER_ERROR_MEMORY_ALLOCATION;
        return list;
    }
    
    // 复制引用
    for (int i = 0; i < manager->field_count; i++) {
        list.references[i] = manager->references[i];
    }
    
    list.count = manager->field_count;
    return list;
}

/**
 * 释放字段引用列表
 */
void free_field_reference_list(FieldReferenceList* list) {
    if (!list) return;
    
    // 仅释放数组，不释放引用本身（因为它们仍由管理器管理）
    if (list->references) {
        free(list->references);
        list->references = NULL;
    }
    
    list->count = 0;
}

/* -------------------- 内部辅助函数实现 -------------------- */

/**
 * 生成唯一的管理器ID
 */
static char* generate_manager_id() {
    // 简单实现：时间戳+随机数
    time_t now = time(NULL);
    int random_part = rand() % 10000;
    
    char* id = (char*)malloc(32);
    if (!id) return NULL;
    
    snprintf(id, 32, "FM_%lld_%04d", (long long)now, random_part);
    return id;
}

/**
 * 检查字段是否存在
 */
static FieldManagerError check_field_exists(FieldManager* manager, QFieldID field_id) {
    if (!manager) return FIELD_MANAGER_ERROR_INVALID_ARGUMENT;
    
    for (int i = 0; i < manager->field_count; i++) {
        if (compare_field_ids(manager->fields[i]->id, field_id) == 0) {
            return FIELD_MANAGER_ERROR_NONE;
        }
    }
    
    return FIELD_MANAGER_ERROR_FIELD_NOT_FOUND;
}

/**
 * 记录管理器操作
 */
static void log_manager_action(FieldManager* manager, const char* action, const char* details) {
    if (!manager || !action) return;
    
    // 获取当前时间
    time_t now = time(NULL);
    char timestamp[64];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(&now));
    
    // 简单日志记录
    if (manager->config.enable_logging) {
        printf("[%s] %s: %s - %s\n", timestamp, manager->manager_id, action, 
               details ? details : "无详情");
    }
}

/**
 * 创建字段引用
 */
static FieldReference* create_field_reference(QField* field) {
    if (!field) return NULL;
    
    FieldReference* reference = (FieldReference*)malloc(sizeof(FieldReference));
    if (!reference) return NULL;
    
    // 设置引用ID与字段相同
    memcpy(&reference->id, &field->id, sizeof(QFieldID));
    reference->field_ptr = field;
    reference->reference_count = 1;
    
    return reference;
}

/**
 * 释放字段引用
 */
static void free_field_reference(FieldReference* reference) {
    if (!reference) return;
    
    // 仅释放引用本身，不释放其指向的字段（由管理器负责）
    free(reference);
}

/**
 * 通过引用获取字段
 */
static QField* get_field_by_reference(FieldReference* reference) {
    if (!reference) return NULL;
    return reference->field_ptr;
} 