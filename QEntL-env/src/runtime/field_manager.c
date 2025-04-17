/**
 * QEntL量子场管理器实现
 * 
 * 量子基因编码: QG-RUNTIME-FLDMGR-D1E9-1713051200
 * 
 * @文件: field_manager.c
 * @描述: 实现QEntL运行时的量子场管理功能
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-16
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 场管理支持多维量子场动态生成和演化
 * - 支持量子场间的相互作用和拓扑结构变换
 */

#include "field_manager.h"
#include "../quantum_field.h"
#include "../quantum_field_generator.h"
#include "state_manager.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

/* 场管理器内部结构 */
struct FieldManager {
    QField** fields;               /* 量子场数组 */
    size_t field_count;            /* 场数量 */
    size_t field_capacity;         /* 场容量 */
    
    QField** active_fields;        /* 当前活跃的量子场 */
    size_t active_count;           /* 活跃场数量 */
    
    FieldGenerator* generator;     /* 场生成器 */
    StateManager* state_manager;   /* 状态管理器引用 */
    
    FieldChangeCallback change_callback; /* 场变化回调 */
    void* callback_user_data;            /* 回调用户数据 */
    
    FieldInteractionMap* interactions;   /* 场交互图 */
    int simulation_quality;              /* 模拟质量 */
    double simulation_step;              /* 模拟步长 */
    
    FieldSimulationStats stats;          /* 模拟统计 */
};

/* 创建场管理器 */
FieldManager* field_manager_create(StateManager* state_manager) {
    if (!state_manager) {
        return NULL;
    }
    
    FieldManager* manager = (FieldManager*)malloc(sizeof(FieldManager));
    if (!manager) {
        return NULL;
    }
    
    /* 初始化场数组 */
    manager->field_capacity = 8;
    manager->fields = (QField**)malloc(manager->field_capacity * sizeof(QField*));
    if (!manager->fields) {
        free(manager);
        return NULL;
    }
    manager->field_count = 0;
    
    /* 初始化活跃场数组 */
    manager->active_fields = (QField**)malloc(manager->field_capacity * sizeof(QField*));
    if (!manager->active_fields) {
        free(manager->fields);
        free(manager);
        return NULL;
    }
    manager->active_count = 0;
    
    /* 创建场生成器 */
    manager->generator = field_generator_create();
    if (!manager->generator) {
        free(manager->active_fields);
        free(manager->fields);
        free(manager);
        return NULL;
    }
    
    /* 创建场交互图 */
    manager->interactions = field_interaction_map_create();
    if (!manager->interactions) {
        field_generator_destroy(manager->generator);
        free(manager->active_fields);
        free(manager->fields);
        free(manager);
        return NULL;
    }
    
    /* 初始化其他属性 */
    manager->state_manager = state_manager;
    manager->change_callback = NULL;
    manager->callback_user_data = NULL;
    manager->simulation_quality = SIMULATION_QUALITY_MEDIUM;
    manager->simulation_step = 0.01;
    
    /* 初始化统计 */
    memset(&manager->stats, 0, sizeof(FieldSimulationStats));
    manager->stats.start_time = time(NULL);
    
    return manager;
}

/* 销毁场管理器 */
void field_manager_destroy(FieldManager* manager) {
    if (!manager) {
        return;
    }
    
    /* 销毁所有场 */
    for (size_t i = 0; i < manager->field_count; i++) {
        quantum_field_destroy(manager->fields[i]);
    }
    
    /* 销毁资源 */
    field_interaction_map_destroy(manager->interactions);
    field_generator_destroy(manager->generator);
    free(manager->active_fields);
    free(manager->fields);
    free(manager);
}

/* 添加量子场 */
int field_manager_add_field(FieldManager* manager, QField* field) {
    if (!manager || !field) {
        return 0;
    }
    
    /* 检查容量并扩展 */
    if (manager->field_count >= manager->field_capacity) {
        size_t new_capacity = manager->field_capacity * 2;
        QField** new_fields = (QField**)realloc(manager->fields, new_capacity * sizeof(QField*));
        if (!new_fields) {
            return 0;
        }
        manager->fields = new_fields;
        
        QField** new_active = (QField**)realloc(manager->active_fields, new_capacity * sizeof(QField*));
        if (!new_active) {
            return 0;
        }
        manager->active_fields = new_active;
        
        manager->field_capacity = new_capacity;
    }
    
    /* 添加场 */
    manager->fields[manager->field_count++] = field;
    
    /* 通知场变化 */
    if (manager->change_callback) {
        manager->change_callback(field, FIELD_ADDED, manager->callback_user_data);
    }
    
    return 1;
}

/* 查找量子场 */
QField* field_manager_find_field(FieldManager* manager, const char* name) {
    if (!manager || !name) {
        return NULL;
    }
    
    for (size_t i = 0; i < manager->field_count; i++) {
        if (strcmp(manager->fields[i]->name, name) == 0) {
            return manager->fields[i];
        }
    }
    
    return NULL;
}

/* 激活量子场 */
int field_manager_activate_field(FieldManager* manager, QField* field) {
    if (!manager || !field) {
        return 0;
    }
    
    /* 检查场是否已经激活 */
    for (size_t i = 0; i < manager->active_count; i++) {
        if (manager->active_fields[i] == field) {
            return 1; /* 已经激活 */
        }
    }
    
    /* 添加到活跃场列表 */
    manager->active_fields[manager->active_count++] = field;
    
    /* 通知场变化 */
    if (manager->change_callback) {
        manager->change_callback(field, FIELD_ACTIVATED, manager->callback_user_data);
    }
    
    return 1;
}

/* 停用量子场 */
int field_manager_deactivate_field(FieldManager* manager, QField* field) {
    if (!manager || !field) {
        return 0;
    }
    
    /* 查找并移除活跃场 */
    size_t pos = manager->active_count;
    for (size_t i = 0; i < manager->active_count; i++) {
        if (manager->active_fields[i] == field) {
            pos = i;
            break;
        }
    }
    
    if (pos >= manager->active_count) {
        return 0; /* 未找到 */
    }
    
    /* 移动最后一个元素到当前位置 */
    manager->active_fields[pos] = manager->active_fields[--manager->active_count];
    
    /* 通知场变化 */
    if (manager->change_callback) {
        manager->change_callback(field, FIELD_DEACTIVATED, manager->callback_user_data);
    }
    
    return 1;
}

/* 删除量子场 */
int field_manager_remove_field(FieldManager* manager, QField* field) {
    if (!manager || !field) {
        return 0;
    }
    
    /* 先停用场 */
    field_manager_deactivate_field(manager, field);
    
    /* 查找并删除场 */
    size_t pos = manager->field_count;
    for (size_t i = 0; i < manager->field_count; i++) {
        if (manager->fields[i] == field) {
            pos = i;
            break;
        }
    }
    
    if (pos >= manager->field_count) {
        return 0; /* 未找到 */
    }
    
    /* 通知场变化 */
    if (manager->change_callback) {
        manager->change_callback(field, FIELD_REMOVED, manager->callback_user_data);
    }
    
    /* 从交互图中移除 */
    field_interaction_map_remove_field(manager->interactions, field);
    
    /* 销毁场 */
    quantum_field_destroy(field);
    
    /* 移动最后一个元素到当前位置 */
    manager->fields[pos] = manager->fields[--manager->field_count];
    
    return 1;
}

/* 创建量子场 */
QField* field_manager_create_field(FieldManager* manager, const char* name, FieldType type, int dimensions) {
    if (!manager || !name || dimensions < 1 || dimensions > MAX_FIELD_DIMENSIONS) {
        return NULL;
    }
    
    /* 创建量子场 */
    QField* field = quantum_field_create(name, type, dimensions);
    if (!field) {
        return NULL;
    }
    
    /* 添加到管理器 */
    if (!field_manager_add_field(manager, field)) {
        quantum_field_destroy(field);
        return NULL;
    }
    
    return field;
}

/* 创建预定义的量子场 */
QField* field_manager_create_predefined_field(FieldManager* manager, const char* name, PredefinedFieldType preset) {
    if (!manager || !name) {
        return NULL;
    }
    
    /* 通过场生成器创建预定义场 */
    QField* field = field_generator_create_preset(manager->generator, name, preset);
    if (!field) {
        return NULL;
    }
    
    /* 添加到管理器 */
    if (!field_manager_add_field(manager, field)) {
        quantum_field_destroy(field);
        return NULL;
    }
    
    return field;
}

/* 添加量子状态到场 */
int field_manager_add_state_to_field(FieldManager* manager, QField* field, QState* state, 
                                   double coordinates[MAX_FIELD_DIMENSIONS]) {
    if (!manager || !field || !state || !coordinates) {
        return 0;
    }
    
    /* 添加状态到场 */
    if (!quantum_field_add_state(field, state, coordinates)) {
        return 0;
    }
    
    /* 通知场变化 */
    if (manager->change_callback) {
        manager->change_callback(field, FIELD_MODIFIED, manager->callback_user_data);
    }
    
    return 1;
}

/* 设置场变化回调 */
void field_manager_set_change_callback(FieldManager* manager, FieldChangeCallback callback, void* user_data) {
    if (!manager) {
        return;
    }
    
    manager->change_callback = callback;
    manager->callback_user_data = user_data;
}

/* 定义场之间的交互 */
int field_manager_define_interaction(FieldManager* manager, QField* field1, QField* field2, 
                                   InteractionType type, double strength) {
    if (!manager || !field1 || !field2 || strength < 0.0) {
        return 0;
    }
    
    /* 添加到交互图 */
    if (!field_interaction_map_add(manager->interactions, field1, field2, type, strength)) {
        return 0;
    }
    
    /* 通知场变化 */
    if (manager->change_callback) {
        manager->change_callback(field1, FIELD_INTERACTION_CHANGED, manager->callback_user_data);
        manager->change_callback(field2, FIELD_INTERACTION_CHANGED, manager->callback_user_data);
    }
    
    return 1;
}

/* 模拟场的演化 */
int field_manager_simulate_evolution(FieldManager* manager, double time_span) {
    if (!manager || time_span <= 0.0) {
        return 0;
    }
    
    double time_step = manager->simulation_step;
    int steps = (int)(time_span / time_step);
    
    if (steps <= 0) {
        steps = 1;
    }
    
    /* 记录开始时间 */
    time_t sim_start = time(NULL);
    
    /* 逐步模拟 */
    for (int step = 0; step < steps; step++) {
        /* 首先，演化每个活跃场 */
        for (size_t i = 0; i < manager->active_count; i++) {
            QField* field = manager->active_fields[i];
            quantum_field_evolve(field, time_step);
        }
        
        /* 然后，处理场之间的相互作用 */
        process_field_interactions(manager, time_step);
        
        /* 更新统计 */
        manager->stats.simulation_steps++;
    }
    
    /* 记录结束时间和耗时 */
    time_t sim_end = time(NULL);
    manager->stats.total_simulation_time += difftime(sim_end, sim_start);
    
    /* 通知场变化 */
    for (size_t i = 0; i < manager->active_count; i++) {
        if (manager->change_callback) {
            manager->change_callback(manager->active_fields[i], FIELD_EVOLVED, manager->callback_user_data);
        }
    }
    
    return 1;
}

/* 获取模拟统计 */
FieldSimulationStats field_manager_get_stats(FieldManager* manager) {
    FieldSimulationStats empty_stats;
    memset(&empty_stats, 0, sizeof(FieldSimulationStats));
    
    if (!manager) {
        return empty_stats;
    }
    
    return manager->stats;
}

/* 设置模拟参数 */
void field_manager_set_simulation_parameters(FieldManager* manager, int quality, double step) {
    if (!manager) {
        return;
    }
    
    /* 设置模拟质量 */
    if (quality >= SIMULATION_QUALITY_LOW && quality <= SIMULATION_QUALITY_ULTRA) {
        manager->simulation_quality = quality;
    }
    
    /* 设置模拟步长 */
    if (step > 0.0) {
        manager->simulation_step = step;
    }
}

/* 内部函数：处理场之间的相互作用 */
static void process_field_interactions(FieldManager* manager, double time_step) {
    if (!manager) {
        return;
    }
    
    /* 获取所有活跃场的相互作用 */
    FieldInteraction** interactions;
    int interaction_count;
    
    if (!field_interaction_map_get_active(manager->interactions, 
                                         manager->active_fields, 
                                         manager->active_count,
                                         &interactions, 
                                         &interaction_count)) {
        return;
    }
    
    /* 处理每个相互作用 */
    for (int i = 0; i < interaction_count; i++) {
        FieldInteraction* interaction = interactions[i];
        
        /* 根据相互作用类型应用效应 */
        switch (interaction->type) {
            case INTERACTION_ENERGY_TRANSFER:
                apply_energy_transfer(interaction->field1, interaction->field2, 
                                    interaction->strength, time_step);
                break;
                
            case INTERACTION_INFORMATION_EXCHANGE:
                apply_information_exchange(interaction->field1, interaction->field2, 
                                         interaction->strength, time_step);
                break;
                
            case INTERACTION_SPATIAL_DISTORTION:
                apply_spatial_distortion(interaction->field1, interaction->field2, 
                                       interaction->strength, time_step);
                break;
                
            default:
                /* 未知的相互作用类型 */
                break;
        }
    }
    
    /* 释放相互作用数组 */
    free(interactions);
}

/* 内部函数：应用能量传递相互作用 */
static void apply_energy_transfer(QField* field1, QField* field2, double strength, double time_step) {
    /* 获取场的能量 */
    double energy1 = quantum_field_get_energy(field1);
    double energy2 = quantum_field_get_energy(field2);
    
    /* 计算传递的能量 */
    double transfer = strength * time_step * (energy1 - energy2) * 0.5;
    
    /* 传递能量 */
    quantum_field_add_energy(field1, -transfer);
    quantum_field_add_energy(field2, transfer);
}

/* 内部函数：应用信息交换相互作用 */
static void apply_information_exchange(QField* field1, QField* field2, double strength, double time_step) {
    /* 计算信息交换量 */
    double exchange_amount = strength * time_step;
    
    /* 遍历场中的每个状态 */
    for (int i = 0; i < field1->state_count && i < MAX_STATES_PER_EXCHANGE; i++) {
        QState* state1 = field1->states[i];
        
        /* 查找最近的状态在场2中 */
        QState* nearest_state = find_nearest_state(field2, state1);
        
        if (nearest_state) {
            /* 交换信息（这里简化为添加一个属性） */
            char key[64];
            char value[64];
            
            snprintf(key, sizeof(key), "info_exchange_from_%s", field1->name);
            snprintf(value, sizeof(value), "%f", exchange_amount);
            quantum_state_set_property(nearest_state, key, value);
            
            snprintf(key, sizeof(key), "info_exchange_from_%s", field2->name);
            quantum_state_set_property(state1, key, value);
        }
    }
}

/* 内部函数：应用空间扭曲相互作用 */
static void apply_spatial_distortion(QField* field1, QField* field2, double strength, double time_step) {
    /* 计算扭曲因子 */
    double distortion_factor = strength * time_step;
    
    /* 应用扭曲到场的指标张量 */
    quantum_field_distort_metric(field1, distortion_factor);
    quantum_field_distort_metric(field2, -distortion_factor);
}

/* 内部函数：找到场中最近的状态 */
static QState* find_nearest_state(QField* field, QState* target_state) {
    if (!field || !target_state || field->state_count == 0) {
        return NULL;
    }
    
    /* 简单实现：返回第一个状态 */
    /* 实际实现应该计算空间距离并找到最近的状态 */
    return field->states[0];
}

/* 场交互图函数 */

/* 创建场交互图 */
FieldInteractionMap* field_interaction_map_create(void) {
    FieldInteractionMap* map = (FieldInteractionMap*)malloc(sizeof(FieldInteractionMap));
    if (!map) {
        return NULL;
    }
    
    map->interaction_capacity = 16;
    map->interactions = (FieldInteraction**)malloc(map->interaction_capacity * sizeof(FieldInteraction*));
    if (!map->interactions) {
        free(map);
        return NULL;
    }
    map->interaction_count = 0;
    
    return map;
}

/* 销毁场交互图 */
void field_interaction_map_destroy(FieldInteractionMap* map) {
    if (!map) {
        return;
    }
    
    /* 释放所有交互 */
    for (int i = 0; i < map->interaction_count; i++) {
        free(map->interactions[i]);
    }
    
    free(map->interactions);
    free(map);
}

/* 添加场交互 */
int field_interaction_map_add(FieldInteractionMap* map, QField* field1, QField* field2, 
                            InteractionType type, double strength) {
    if (!map || !field1 || !field2) {
        return 0;
    }
    
    /* 检查是否已存在 */
    for (int i = 0; i < map->interaction_count; i++) {
        FieldInteraction* interaction = map->interactions[i];
        if ((interaction->field1 == field1 && interaction->field2 == field2) ||
            (interaction->field1 == field2 && interaction->field2 == field1)) {
            
            /* 更新现有交互 */
            interaction->type = type;
            interaction->strength = strength;
            return 1;
        }
    }
    
    /* 检查容量并扩展 */
    if (map->interaction_count >= map->interaction_capacity) {
        int new_capacity = map->interaction_capacity * 2;
        FieldInteraction** new_interactions = (FieldInteraction**)realloc(
            map->interactions, new_capacity * sizeof(FieldInteraction*));
        
        if (!new_interactions) {
            return 0;
        }
        
        map->interactions = new_interactions;
        map->interaction_capacity = new_capacity;
    }
    
    /* 创建新交互 */
    FieldInteraction* interaction = (FieldInteraction*)malloc(sizeof(FieldInteraction));
    if (!interaction) {
        return 0;
    }
    
    interaction->field1 = field1;
    interaction->field2 = field2;
    interaction->type = type;
    interaction->strength = strength;
    
    /* 添加到图 */
    map->interactions[map->interaction_count++] = interaction;
    
    return 1;
}

/* 移除场的所有交互 */
int field_interaction_map_remove_field(FieldInteractionMap* map, QField* field) {
    if (!map || !field) {
        return 0;
    }
    
    int removed = 0;
    
    /* 查找并移除与该场相关的所有交互 */
    for (int i = 0; i < map->interaction_count; ) {
        FieldInteraction* interaction = map->interactions[i];
        
        if (interaction->field1 == field || interaction->field2 == field) {
            /* 找到相关交互，移除它 */
            free(interaction);
            
            /* 移动最后一个元素到当前位置 */
            map->interactions[i] = map->interactions[--map->interaction_count];
            removed++;
        } else {
            /* 当前交互与目标场无关，继续下一个 */
            i++;
        }
    }
    
    return removed;
}

/* 获取活跃场的交互 */
int field_interaction_map_get_active(FieldInteractionMap* map, 
                                   QField** active_fields, 
                                   int active_count,
                                   FieldInteraction*** result, 
                                   int* result_count) {
    if (!map || !active_fields || active_count <= 0 || !result || !result_count) {
        return 0;
    }
    
    /* 分配结果数组 */
    *result_count = 0;
    *result = (FieldInteraction**)malloc(map->interaction_count * sizeof(FieldInteraction*));
    
    if (!*result) {
        return 0;
    }
    
    /* 查找涉及活跃场的交互 */
    for (int i = 0; i < map->interaction_count; i++) {
        FieldInteraction* interaction = map->interactions[i];
        int field1_active = 0;
        int field2_active = 0;
        
        /* 检查场是否活跃 */
        for (int j = 0; j < active_count; j++) {
            if (active_fields[j] == interaction->field1) {
                field1_active = 1;
            }
            if (active_fields[j] == interaction->field2) {
                field2_active = 1;
            }
        }
        
        /* 如果两个场都是活跃的，添加到结果 */
        if (field1_active && field2_active) {
            (*result)[(*result_count)++] = interaction;
        }
    }
    
    /* 如果没有找到交互，释放结果数组 */
    if (*result_count == 0) {
        free(*result);
        *result = NULL;
        return 0;
    }
    
    return 1;
} 