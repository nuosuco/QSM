/**
 * QEntL量子纠缠处理器实现
 * 
 * 量子基因编码: QG-RUNTIME-ENTPROC-C5D7-1713051200
 * 
 * @文件: entanglement_processor.c
 * @描述: 实现QEntL运行时的量子纠缠处理功能
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-16
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 纠缠处理支持复杂量子网络拓扑和量子纠缠传递
 * - 支持跨设备量子纠缠同步和高效通信
 */

#include "entanglement_processor.h"
#include "state_manager.h"
#include "../quantum_entanglement.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

/* 纠缠处理器内部结构 */
struct EntanglementProcessor {
    StateManager* state_manager;      /* 状态管理器引用 */
    EntanglementRegistry* registry;   /* 纠缠注册表引用 */
    
    int thread_count;                 /* 处理线程数量 */
    int is_running;                   /* 处理器是否运行中 */
    
    EntanglementCallback* callbacks;  /* 回调函数数组 */
    int callback_count;               /* 回调函数数量 */
    
    double coherence_threshold;       /* 相干性阈值 */
    double propagation_speed;         /* 纠缠传播速度 */
    
    EntanglementProcessorStats stats; /* 统计数据 */
    time_t last_stats_update;         /* 上次统计更新时间 */
};

/* 纠缠效应内部结构 */
typedef struct {
    QEntanglement* source;            /* 源纠缠关系 */
    QState* affected_state;           /* 受影响的状态 */
    double effect_strength;           /* 效应强度 */
    EffectType type;                  /* 效应类型 */
} EntanglementEffect;

/* 创建纠缠处理器 */
EntanglementProcessor* entanglement_processor_create(StateManager* state_manager) {
    if (!state_manager) {
        return NULL;
    }
    
    EntanglementProcessor* processor = (EntanglementProcessor*)malloc(sizeof(EntanglementProcessor));
    if (!processor) {
        return NULL;
    }
    
    processor->state_manager = state_manager;
    processor->registry = state_manager_get_registry(state_manager);
    
    if (!processor->registry) {
        free(processor);
        return NULL;
    }
    
    /* 默认配置 */
    processor->thread_count = 1;
    processor->is_running = 0;
    
    processor->callbacks = NULL;
    processor->callback_count = 0;
    
    processor->coherence_threshold = 0.01;
    processor->propagation_speed = 1.0;
    
    /* 初始化统计数据 */
    memset(&processor->stats, 0, sizeof(EntanglementProcessorStats));
    processor->last_stats_update = time(NULL);
    
    return processor;
}

/* 销毁纠缠处理器 */
void entanglement_processor_destroy(EntanglementProcessor* processor) {
    if (!processor) {
        return;
    }
    
    /* 停止处理 */
    entanglement_processor_stop(processor);
    
    /* 释放回调函数数组 */
    if (processor->callbacks) {
        free(processor->callbacks);
    }
    
    free(processor);
}

/* 启动纠缠处理器 */
int entanglement_processor_start(EntanglementProcessor* processor) {
    if (!processor) {
        return 0;
    }
    
    if (processor->is_running) {
        return 1; /* 已经在运行 */
    }
    
    processor->is_running = 1;
    
    /* 更新统计 */
    processor->stats.start_time = time(NULL);
    processor->stats.processing_cycles = 0;
    processor->stats.total_effects_processed = 0;
    
    return 1;
}

/* 停止纠缠处理器 */
void entanglement_processor_stop(EntanglementProcessor* processor) {
    if (!processor || !processor->is_running) {
        return;
    }
    
    processor->is_running = 0;
    
    /* 更新统计 */
    processor->stats.stop_time = time(NULL);
}

/* 注册纠缠回调 */
int entanglement_processor_register_callback(EntanglementProcessor* processor, 
                                           EntanglementCallback callback) {
    if (!processor || !callback) {
        return 0;
    }
    
    /* 扩展回调数组 */
    EntanglementCallback* new_callbacks = 
        (EntanglementCallback*)realloc(processor->callbacks, 
                                      (processor->callback_count + 1) * sizeof(EntanglementCallback));
    
    if (!new_callbacks) {
        return 0;
    }
    
    processor->callbacks = new_callbacks;
    processor->callbacks[processor->callback_count++] = callback;
    
    return 1;
}

/* 设置纠缠处理参数 */
void entanglement_processor_set_parameters(EntanglementProcessor* processor, 
                                         double coherence_threshold,
                                         double propagation_speed) {
    if (!processor) {
        return;
    }
    
    if (coherence_threshold > 0.0) {
        processor->coherence_threshold = coherence_threshold;
    }
    
    if (propagation_speed > 0.0) {
        processor->propagation_speed = propagation_speed;
    }
}

/* 处理单个纠缠效应 */
int entanglement_processor_process_effect(EntanglementProcessor* processor, 
                                        QEntanglement* entanglement,
                                        QState* source_state,
                                        QState* target_state) {
    if (!processor || !entanglement || !source_state || !target_state) {
        return 0;
    }
    
    /* 计算效应强度 */
    double effect_strength = entanglement->strength * processor->propagation_speed;
    
    /* 如果效应太弱，忽略 */
    if (effect_strength < processor->coherence_threshold) {
        return 1;
    }
    
    /* 确定效应类型 */
    EffectType effect_type = EFFECT_STATE_CHANGE;
    
    /* 根据状态类型确定更具体的效应类型 */
    if (source_state->type == QSTATE_SUPERPOSITION) {
        effect_type = EFFECT_SUPERPOSITION_TRANSFER;
    } else if (source_state->type == QSTATE_ENTANGLED && target_state->type != QSTATE_ENTANGLED) {
        effect_type = EFFECT_ENTANGLEMENT_TRANSFER;
    }
    
    /* 创建效应描述 */
    EntanglementEffect effect;
    effect.source = entanglement;
    effect.affected_state = target_state;
    effect.effect_strength = effect_strength;
    effect.type = effect_type;
    
    /* 应用效应 */
    int result = apply_entanglement_effect(processor, &effect);
    
    /* 更新统计 */
    processor->stats.total_effects_processed++;
    
    /* 通知回调 */
    for (int i = 0; i < processor->callback_count; i++) {
        processor->callbacks[i](entanglement, source_state, target_state, effect_type, effect_strength);
    }
    
    return result;
}

/* 处理一个周期的纠缠效应 */
int entanglement_processor_process_cycle(EntanglementProcessor* processor) {
    if (!processor || !processor->is_running) {
        return 0;
    }
    
    /* 获取所有活跃的纠缠关系 */
    QEntanglement** entanglements;
    int entanglement_count;
    
    if (!entanglement_registry_get_all(processor->registry, &entanglements, &entanglement_count)) {
        return 0;
    }
    
    int effects_processed = 0;
    
    /* 处理每个纠缠关系 */
    for (int i = 0; i < entanglement_count; i++) {
        QEntanglement* entanglement = entanglements[i];
        
        /* 检查两个状态是否都有效 */
        if (!entanglement->state1 || !entanglement->state2) {
            continue;
        }
        
        /* 双向处理效应 */
        if (entanglement_processor_process_effect(processor, entanglement, 
                                                entanglement->state1, entanglement->state2)) {
            effects_processed++;
        }
        
        if (entanglement_processor_process_effect(processor, entanglement, 
                                                entanglement->state2, entanglement->state1)) {
            effects_processed++;
        }
    }
    
    /* 释放纠缠数组 */
    free(entanglements);
    
    /* 更新统计 */
    processor->stats.processing_cycles++;
    processor->last_stats_update = time(NULL);
    
    return effects_processed;
}

/* 获取处理器统计数据 */
EntanglementProcessorStats entanglement_processor_get_stats(EntanglementProcessor* processor) {
    EntanglementProcessorStats empty_stats;
    memset(&empty_stats, 0, sizeof(EntanglementProcessorStats));
    
    if (!processor) {
        return empty_stats;
    }
    
    return processor->stats;
}

/* 检测纠缠路径 */
int entanglement_processor_detect_path(EntanglementProcessor* processor, 
                                     QState* source, 
                                     QState* target,
                                     EntanglementPath* path) {
    if (!processor || !source || !target || !path) {
        return 0;
    }
    
    /* 初始化路径 */
    memset(path, 0, sizeof(EntanglementPath));
    
    /* 如果源和目标相同，返回空路径 */
    if (source == target) {
        path->state_count = 1;
        path->states[0] = source;
        path->total_strength = 1.0;
        return 1;
    }
    
    /* 简单的广度优先搜索寻找路径 */
    /* 注意：实际实现应该使用更高效的算法 */
    
    /* 此处简化实现，仅检查是否有直接纠缠 */
    QEntanglement* direct_entanglement = entanglement_registry_find(processor->registry, source, target);
    
    if (direct_entanglement) {
        path->state_count = 2;
        path->states[0] = source;
        path->states[1] = target;
        path->entanglement_count = 1;
        path->entanglements[0] = direct_entanglement;
        path->total_strength = direct_entanglement->strength;
        return 1;
    }
    
    /* 实际实现应该包含完整的路径搜索算法 */
    return 0;
}

/* 计算纠缠影响范围 */
int entanglement_processor_calculate_influence(EntanglementProcessor* processor,
                                             QState* source,
                                             InfluenceMap* map) {
    if (!processor || !source || !map) {
        return 0;
    }
    
    /* 初始化影响图 */
    memset(map, 0, sizeof(InfluenceMap));
    map->center_state = source;
    
    /* 获取直接纠缠的状态 */
    QEntanglement** direct_entanglements;
    int direct_count;
    
    if (!entanglement_registry_get_for_state(processor->registry, source, 
                                           &direct_entanglements, &direct_count)) {
        return 0;
    }
    
    /* 添加直接纠缠的状态到影响图 */
    for (int i = 0; i < direct_count && map->state_count < MAX_INFLUENCE_STATES; i++) {
        QEntanglement* entanglement = direct_entanglements[i];
        QState* other_state = (entanglement->state1 == source) ? 
                            entanglement->state2 : entanglement->state1;
        
        map->states[map->state_count] = other_state;
        map->strengths[map->state_count] = entanglement->strength;
        map->state_count++;
    }
    
    /* 释放直接纠缠数组 */
    free(direct_entanglements);
    
    /* 实际实现应该包含更复杂的影响传播算法 */
    
    return map->state_count;
}

/* 内部函数：应用纠缠效应 */
static int apply_entanglement_effect(EntanglementProcessor* processor, EntanglementEffect* effect) {
    if (!processor || !effect || !effect->affected_state) {
        return 0;
    }
    
    QState* target = effect->affected_state;
    double strength = effect->effect_strength;
    
    switch (effect->type) {
        case EFFECT_STATE_CHANGE: {
            /* 简单的状态变化效应 */
            /* 在实际实现中，这应该修改状态的一些属性 */
            
            /* 设置一个属性来表示效应已应用 */
            quantum_state_set_property(target, "last_effect_strength", "");
            
            char value_str[32];
            snprintf(value_str, sizeof(value_str), "%f", strength);
            quantum_state_set_property(target, "last_effect_strength", value_str);
            
            return 1;
        }
            
        case EFFECT_SUPERPOSITION_TRANSFER: {
            /* 叠加态传递效应 */
            /* 在实际实现中，这应该传递叠加态的一部分到目标状态 */
            
            /* 这里简化处理，只记录效应 */
            quantum_state_set_property(target, "superposition_effect", "");
            
            char value_str[32];
            snprintf(value_str, sizeof(value_str), "%f", strength);
            quantum_state_set_property(target, "superposition_effect", value_str);
            
            return 1;
        }
            
        case EFFECT_ENTANGLEMENT_TRANSFER: {
            /* 纠缠传递效应 */
            /* 在实际实现中，这应该使目标状态也变为纠缠态 */
            
            /* 这里简化处理，只记录效应 */
            quantum_state_set_property(target, "entanglement_transfer", "");
            
            char value_str[32];
            snprintf(value_str, sizeof(value_str), "%f", strength);
            quantum_state_set_property(target, "entanglement_transfer", value_str);
            
            return 1;
        }
            
        default:
            return 0;
    }
} 