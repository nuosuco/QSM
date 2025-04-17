/**
 * 量子状态管理器实现
 * 
 * 该文件实现了量子状态管理器的功能，负责量子状态的生命周期管理，
 * 包括创建、存储、检索、更新和删除等操作。
 *
 * @file state_manager.c
 * @version 1.0
 * @date 2024-05-15
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include "state_manager.h"

/* 内部辅助函数声明 */
static char* generate_manager_id();
static char* generate_reference_id();
static StateReference* create_state_reference(QuantumState* state);
static void free_state_reference(StateReference* reference);
static QuantumState* get_state_by_reference(StateReference* reference);
static StateManagerError check_state_exists(StateManager* manager, QuantumStateID state_id);
static void log_manager_action(StateManager* manager, const char* action, const char* details);
static char* get_current_timestamp();
static int match_state_criteria(QuantumState* state, StateQueryCriteria criteria);
static int compare_states_for_sort(QuantumState* state1, QuantumState* state2, const char* sort_by, int ascending);

/**
 * 初始化状态管理器
 */
StateManager* initialize_state_manager(StateManagerConfig config) {
    // 分配状态管理器内存
    StateManager* manager = (StateManager*)malloc(sizeof(StateManager));
    if (!manager) {
        fprintf(stderr, "无法分配状态管理器内存\n");
        return NULL;
    }
    
    // 设置初始容量
    int capacity = config.initial_capacity > 0 ? config.initial_capacity : 10;
    manager->states = (QuantumState**)malloc(sizeof(QuantumState*) * capacity);
    manager->references = (StateReference**)malloc(sizeof(StateReference*) * capacity);
    
    if (!manager->states || !manager->references) {
        free(manager->states);
        free(manager->references);
        free(manager);
        fprintf(stderr, "无法分配状态数组内存\n");
        return NULL;
    }
    
    // 初始化数组
    for (int i = 0; i < capacity; i++) {
        manager->states[i] = NULL;
        manager->references[i] = NULL;
    }
    
    // 初始化管理器属性
    manager->state_count = 0;
    manager->capacity = capacity;
    manager->config = config;
    manager->manager_id = generate_manager_id();
    manager->log_file = NULL;
    manager->cache = NULL;
    manager->persistence_manager = NULL;
    manager->mutex = NULL;
    
    // 打开日志文件(如果启用)
    if (config.enable_logging && config.log_file_path) {
        manager->log_file = fopen(config.log_file_path, "a");
        if (!manager->log_file) {
            fprintf(stderr, "警告: 无法打开日志文件 %s\n", config.log_file_path);
        }
    }
    
    // TODO: 初始化缓存、持久化管理器和互斥锁(如果启用)
    
    // 记录初始化成功
    log_manager_action(manager, "初始化", "状态管理器初始化成功");
    
    printf("量子状态管理器初始化成功 (ID: %s)\n", manager->manager_id);
    
    return manager;
}

/**
 * 获取默认状态管理器配置
 */
StateManagerConfig get_default_state_manager_config() {
    StateManagerConfig config;
    
    config.initial_capacity = 20;
    config.max_capacity = 1000;
    config.auto_resize = 1;
    config.enable_logging = 1;
    config.log_file_path = "state_manager.log";
    config.cache_size_mb = 16.0;
    config.enable_persistence = 0;
    config.persistence_dir = "states";
    config.persistence_interval = 300;
    config.thread_safe = 0;
    
    return config;
}

/**
 * 关闭状态管理器
 */
void shutdown_state_manager(StateManager* manager) {
    if (!manager) return;
    
    // 记录关闭操作
    log_manager_action(manager, "关闭", "正在关闭状态管理器");
    
    // 释放所有状态和引用
    for (int i = 0; i < manager->state_count; i++) {
        // 此处假设量子状态和引用应该被释放
        // 实际应用中可能需要更复杂的引用计数处理
        free_state_reference(manager->references[i]);
        
        // TODO: 添加释放量子状态的函数调用
        // free_quantum_state(manager->states[i]);
    }
    
    // 释放数组
    free(manager->states);
    free(manager->references);
    
    // 关闭日志文件
    if (manager->log_file) {
        fclose(manager->log_file);
    }
    
    // TODO: 释放缓存、持久化管理器和互斥锁
    
    // 释放管理器ID
    free(manager->manager_id);
    
    // 释放管理器本身
    free(manager);
    
    printf("量子状态管理器已关闭\n");
}

/**
 * 创建量子状态
 */
StateReference* create_state(StateManager* manager, QuantumState* state) {
    if (!manager || !state) return NULL;
    
    // 检查容量
    if (manager->state_count >= manager->capacity) {
        // 如果已达到容量上限且允许自动调整大小
        if (manager->config.auto_resize && 
            (manager->config.max_capacity == 0 || manager->capacity < manager->config.max_capacity)) {
            
            int new_capacity = manager->capacity * 2;
            if (manager->config.max_capacity > 0 && new_capacity > manager->config.max_capacity) {
                new_capacity = manager->config.max_capacity;
            }
            
            QuantumState** new_states = (QuantumState**)realloc(
                manager->states, 
                sizeof(QuantumState*) * new_capacity);
                
            StateReference** new_references = (StateReference**)realloc(
                manager->references, 
                sizeof(StateReference*) * new_capacity);
            
            if (!new_states || !new_references) {
                free(new_states);
                free(new_references);
                log_manager_action(manager, "错误", "无法扩展管理器容量");
                return NULL;
            }
            
            // 初始化新分配的内存
            for (int i = manager->capacity; i < new_capacity; i++) {
                new_states[i] = NULL;
                new_references[i] = NULL;
            }
            
            manager->states = new_states;
            manager->references = new_references;
            manager->capacity = new_capacity;
            
            log_manager_action(manager, "扩容", "管理器容量已扩展到 %d", new_capacity);
        } else {
            log_manager_action(manager, "错误", "管理器已满，无法创建更多状态");
            return NULL;
        }
    }
    
    // 检查状态是否已存在
    for (int i = 0; i < manager->state_count; i++) {
        if (compare_state_ids(manager->states[i]->id, state->id) == 0) {
            log_manager_action(manager, "错误", "状态已存在 (ID: %s)", state->id.id_string);
            return NULL;
        }
    }
    
    // 在当前时间戳设置创建和更新时间(如果未设置)
    if (!state->metadata.creation_timestamp) {
        state->metadata.creation_timestamp = get_current_timestamp();
    }
    if (!state->metadata.last_update_timestamp) {
        state->metadata.last_update_timestamp = strdup(state->metadata.creation_timestamp);
    }
    
    // 创建状态引用
    StateReference* reference = create_state_reference(state);
    if (!reference) {
        log_manager_action(manager, "错误", "无法创建状态引用");
        return NULL;
    }
    
    // 添加状态和引用到管理器
    manager->states[manager->state_count] = state;
    manager->references[manager->state_count] = reference;
    manager->state_count++;
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "创建状态 (ID: %s, 名称: %s)", 
             state->id.id_string, state->metadata.name);
    log_manager_action(manager, "创建状态", details);
    
    return reference;
}

/**
 * 获取状态引用
 */
StateReference* get_state_reference(StateManager* manager, QuantumStateID state_id) {
    if (!manager) return NULL;
    
    // 查找状态
    for (int i = 0; i < manager->state_count; i++) {
        if (compare_state_ids(manager->states[i]->id, state_id) == 0) {
            return manager->references[i];
        }
    }
    
    return NULL;
}

/**
 * 获取状态引用(通过引用ID)
 */
StateReference* get_state_reference_by_id(StateManager* manager, const char* reference_id) {
    if (!manager || !reference_id) return NULL;
    
    // 查找引用
    for (int i = 0; i < manager->state_count; i++) {
        if (manager->references[i] && 
            strcmp(manager->references[i]->reference_id, reference_id) == 0) {
            return manager->references[i];
        }
    }
    
    return NULL;
}

/**
 * 更新量子状态
 */
StateManagerError update_state(StateManager* manager, StateReference* reference, StateUpdateOptions options) {
    if (!manager || !reference) {
        return STATE_MANAGER_ERROR_INVALID_ARGUMENT;
    }
    
    // 获取状态
    QuantumState* state = get_state_by_reference(reference);
    if (!state) {
        return STATE_MANAGER_ERROR_INVALID_REFERENCE;
    }
    
    // 更新名称(如果提供)
    if (options.name) {
        free(state->metadata.name);
        state->metadata.name = strdup(options.name);
    }
    
    // 更新描述(如果提供)
    if (options.description) {
        free(state->metadata.description);
        state->metadata.description = strdup(options.description);
    }
    
    // 更新保真度(如果有效)
    if (options.fidelity >= 0 && options.fidelity <= 1.0) {
        state->fidelity = options.fidelity;
    }
    
    // 添加属性
    if (options.properties_to_add && options.properties_add_count > 0) {
        for (int i = 0; i < options.properties_add_count; i++) {
            // 检查属性是否已存在
            int property_exists = 0;
            for (int j = 0; j < state->property_count; j++) {
                if (strcmp(state->properties[j].name, options.properties_to_add[i].name) == 0) {
                    // 更新现有属性
                    state->properties[j].type = options.properties_to_add[i].type;
                    
                    // 释放旧值并复制新值
                    free(state->properties[j].value);
                    state->properties[j].value = strdup(options.properties_to_add[i].value);
                    
                    property_exists = 1;
                    break;
                }
            }
            
            // 如果属性不存在，添加新属性
            if (!property_exists) {
                // 重新分配属性数组
                QuantumStateProperty* new_properties = (QuantumStateProperty*)realloc(
                    state->properties, 
                    sizeof(QuantumStateProperty) * (state->property_count + 1));
                
                if (!new_properties) {
                    return STATE_MANAGER_ERROR_MEMORY_ALLOCATION;
                }
                
                state->properties = new_properties;
                
                // 添加新属性
                state->properties[state->property_count].name = strdup(options.properties_to_add[i].name);
                state->properties[state->property_count].type = options.properties_to_add[i].type;
                state->properties[state->property_count].value = strdup(options.properties_to_add[i].value);
                
                state->property_count++;
            }
        }
    }
    
    // 移除属性
    if (options.properties_to_remove && options.properties_remove_count > 0) {
        for (int i = 0; i < options.properties_remove_count; i++) {
            for (int j = 0; j < state->property_count; j++) {
                if (strcmp(state->properties[j].name, options.properties_to_remove[i]) == 0) {
                    // 释放属性资源
                    free(state->properties[j].name);
                    free(state->properties[j].value);
                    
                    // 将后面的属性前移
                    for (int k = j; k < state->property_count - 1; k++) {
                        state->properties[k] = state->properties[k + 1];
                    }
                    
                    state->property_count--;
                    
                    // 调整索引，因为删除了一个元素
                    j--;
                    break;
                }
            }
        }
    }
    
    // 更新时间戳
    free(state->metadata.last_update_timestamp);
    state->metadata.last_update_timestamp = get_current_timestamp();
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "更新状态 (ID: %s, 名称: %s)", 
             state->id.id_string, state->metadata.name);
    log_manager_action(manager, "更新状态", details);
    
    return STATE_MANAGER_ERROR_NONE;
}

/**
 * 删除量子状态
 */
StateManagerError delete_state(StateManager* manager, StateReference* reference) {
    if (!manager || !reference) {
        return STATE_MANAGER_ERROR_INVALID_ARGUMENT;
    }
    
    // 查找状态索引
    int state_index = -1;
    for (int i = 0; i < manager->state_count; i++) {
        if (manager->references[i] == reference) {
            state_index = i;
            break;
        }
    }
    
    if (state_index == -1) {
        return STATE_MANAGER_ERROR_STATE_NOT_FOUND;
    }
    
    // 获取状态
    QuantumState* state = manager->states[state_index];
    
    // 记录操作
    char details[256];
    snprintf(details, sizeof(details), "删除状态 (ID: %s, 名称: %s)", 
             state->id.id_string, state->metadata.name);
    log_manager_action(manager, "删除状态", details);
    
    // 释放引用
    free_state_reference(manager->references[state_index]);
    
    // TODO: 释放量子状态资源
    // free_quantum_state(manager->states[state_index]);
    
    // 移动数组中的元素以填补空缺
    for (int i = state_index; i < manager->state_count - 1; i++) {
        manager->states[i] = manager->states[i + 1];
        manager->references[i] = manager->references[i + 1];
    }
    
    // 减少计数并清空最后一个元素
    manager->state_count--;
    manager->states[manager->state_count] = NULL;
    manager->references[manager->state_count] = NULL;
    
    return STATE_MANAGER_ERROR_NONE;
}

/**
 * 查询量子状态
 */
StateQueryResult query_states(StateManager* manager, StateQueryCriteria criteria) {
    StateQueryResult result;
    result.results = NULL;
    result.count = 0;
    result.total_matches = 0;
    result.error = STATE_MANAGER_ERROR_NONE;
    
    if (!manager) {
        result.error = STATE_MANAGER_ERROR_INVALID_ARGUMENT;
        return result;
    }
    
    // 设置默认的最大结果数
    int max_results = (criteria.max_results > 0) ? criteria.max_results : manager->state_count;
    
    // 第一遍：计算匹配的状态数量
    for (int i = 0; i < manager->state_count; i++) {
        if (match_state_criteria(manager->states[i], criteria)) {
            result.total_matches++;
        }
    }
    
    // 如果没有匹配项，直接返回
    if (result.total_matches == 0) {
        return result;
    }
    
    // 分配结果数组
    int results_to_return = (result.total_matches < max_results) ? result.total_matches : max_results;
    result.results = (StateReference**)malloc(sizeof(StateReference*) * results_to_return);
    
    if (!result.results) {
        result.error = STATE_MANAGER_ERROR_MEMORY_ALLOCATION;
        return result;
    }
    
    // 第二遍：收集匹配的状态引用
    int result_index = 0;
    for (int i = 0; i < manager->state_count && result_index < results_to_return; i++) {
        if (match_state_criteria(manager->states[i], criteria)) {
            result.results[result_index++] = manager->references[i];
        }
    }
    
    result.count = result_index;
    
    // 如果需要排序
    if (criteria.sort_by) {
        // TODO: 实现排序逻辑
    }
    
    return result;
}

/**
 * 获取状态信息
 */
StateInfo get_state_info(StateManager* manager, StateReference* reference) {
    StateInfo info;
    memset(&info, 0, sizeof(StateInfo));
    
    if (!manager || !reference) {
        info.error = STATE_MANAGER_ERROR_INVALID_ARGUMENT;
        return info;
    }
    
    QuantumState* state = get_state_by_reference(reference);
    if (!state) {
        info.error = STATE_MANAGER_ERROR_INVALID_REFERENCE;
        return info;
    }
    
    // 复制基本信息
    info.id = state->id;
    info.name = strdup(state->metadata.name);
    info.description = strdup(state->metadata.description);
    info.dimensions = state->dimensions;
    info.fidelity = state->fidelity;
    info.creation_time = strdup(state->metadata.creation_timestamp);
    info.last_update_time = strdup(state->metadata.last_update_timestamp);
    info.property_count = state->property_count;
    
    // 复制属性名称
    if (state->property_count > 0) {
        info.property_names = (char**)malloc(sizeof(char*) * state->property_count);
        if (info.property_names) {
            for (int i = 0; i < state->property_count; i++) {
                info.property_names[i] = strdup(state->properties[i].name);
            }
        }
    }
    
    // 设置引用计数
    info.reference_count = reference->reference_count;
    
    info.error = STATE_MANAGER_ERROR_NONE;
    return info;
}

/* 内部辅助函数实现 */

/**
 * 生成管理器ID
 */
static char* generate_manager_id() {
    char* id = (char*)malloc(33);
    if (!id) return NULL;
    
    // 生成随机ID
    const char hex_chars[] = "0123456789ABCDEF";
    for (int i = 0; i < 32; i++) {
        id[i] = hex_chars[rand() % 16];
    }
    id[32] = '\0';
    
    return id;
}

/**
 * 生成引用ID
 */
static char* generate_reference_id() {
    char* id = (char*)malloc(17);
    if (!id) return NULL;
    
    // 生成随机ID
    const char hex_chars[] = "0123456789ABCDEF";
    for (int i = 0; i < 16; i++) {
        id[i] = hex_chars[rand() % 16];
    }
    id[16] = '\0';
    
    return id;
}

/**
 * 创建状态引用
 */
static StateReference* create_state_reference(QuantumState* state) {
    if (!state) return NULL;
    
    StateReference* reference = (StateReference*)malloc(sizeof(StateReference));
    if (!reference) return NULL;
    
    reference->reference_id = generate_reference_id();
    reference->state_id = state->id;
    reference->state_ptr = state;
    reference->reference_count = 1;
    
    return reference;
}

/**
 * 释放状态引用
 */
static void free_state_reference(StateReference* reference) {
    if (!reference) return;
    
    free(reference->reference_id);
    free(reference);
}

/**
 * 获取引用对应的状态
 */
static QuantumState* get_state_by_reference(StateReference* reference) {
    if (!reference) return NULL;
    
    return (QuantumState*)reference->state_ptr;
}

/**
 * 检查状态是否存在
 */
static StateManagerError check_state_exists(StateManager* manager, QuantumStateID state_id) {
    if (!manager) return STATE_MANAGER_ERROR_INVALID_ARGUMENT;
    
    for (int i = 0; i < manager->state_count; i++) {
        if (compare_state_ids(manager->states[i]->id, state_id) == 0) {
            return STATE_MANAGER_ERROR_NONE;
        }
    }
    
    return STATE_MANAGER_ERROR_STATE_NOT_FOUND;
}

/**
 * 记录管理器操作
 */
static void log_manager_action(StateManager* manager, const char* action, const char* details) {
    if (!manager || !action || !details) return;
    
    // 如果未启用日志，则直接返回
    if (!manager->config.enable_logging) return;
    
    // 获取当前时间
    time_t now;
    time(&now);
    char timestamp[64];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(&now));
    
    // 打印到控制台
    printf("[%s] StateManager (%s): %s - %s\n", 
           timestamp, manager->manager_id, action, details);
    
    // 写入日志文件
    if (manager->log_file) {
        fprintf(manager->log_file, "[%s] %s - %s\n", timestamp, action, details);
        fflush(manager->log_file);
    }
}

/**
 * 获取当前时间戳
 */
static char* get_current_timestamp() {
    char* timestamp = (char*)malloc(64);
    if (!timestamp) return NULL;
    
    time_t now;
    time(&now);
    strftime(timestamp, 64, "%Y-%m-%d %H:%M:%S", localtime(&now));
    
    return timestamp;
}

/**
 * 匹配状态查询条件
 */
static int match_state_criteria(QuantumState* state, StateQueryCriteria criteria) {
    if (!state) return 0;
    
    // 名称模式匹配(简化版，只支持精确匹配)
    if (criteria.name_pattern && strlen(criteria.name_pattern) > 0) {
        if (strcmp(state->metadata.name, criteria.name_pattern) != 0) {
            return 0;
        }
    }
    
    // 标签匹配(简化版，只检查是否包含)
    if (criteria.tags && strlen(criteria.tags) > 0) {
        // TODO: 实现更复杂的标签匹配
        if (!state->metadata.tags || strstr(state->metadata.tags, criteria.tags) == NULL) {
            return 0;
        }
    }
    
    // 保真度范围匹配
    if (criteria.min_fidelity > 0 && state->fidelity < criteria.min_fidelity) {
        return 0;
    }
    if (criteria.max_fidelity > 0 && criteria.max_fidelity <= 1.0 && state->fidelity > criteria.max_fidelity) {
        return 0;
    }
    
    // 维度范围匹配
    if (criteria.min_dimensions > 0 && state->dimensions < criteria.min_dimensions) {
        return 0;
    }
    if (criteria.max_dimensions > 0 && state->dimensions > criteria.max_dimensions) {
        return 0;
    }
    
    // TODO: 实现时间过滤
    
    // 所有条件都匹配
    return 1;
}

/**
 * 比较状态ID
 * 这个函数可能在quantum_state.c中已经定义，这里是一个简单实现
 */
int compare_state_ids(QuantumStateID id1, QuantumStateID id2) {
    return strcmp(id1.id_string, id2.id_string);
}

/**
 * 比较两个状态用于排序
 */
static int compare_states_for_sort(QuantumState* state1, QuantumState* state2, const char* sort_by, int ascending) {
    if (!state1 || !state2 || !sort_by) return 0;
    
    int result = 0;
    
    // 根据不同字段排序
    if (strcmp(sort_by, "name") == 0) {
        result = strcmp(state1->metadata.name, state2->metadata.name);
    }
    else if (strcmp(sort_by, "dimensions") == 0) {
        result = state1->dimensions - state2->dimensions;
    }
    else if (strcmp(sort_by, "fidelity") == 0) {
        result = (state1->fidelity > state2->fidelity) ? 1 : ((state1->fidelity < state2->fidelity) ? -1 : 0);
    }
    // TODO: 添加更多排序字段
    
    // 如果是降序，反转结果
    return ascending ? result : -result;
} 