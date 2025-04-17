/**
 * QEntL量子状态管理器实现
 * 
 * 量子基因编码: QG-RUNTIME-STMGR-B2C8-1713051200
 * 
 * @文件: state_manager.c
 * @描述: 实现QEntL运行时的量子状态管理功能
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-16
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 状态管理支持量子比特动态分配和自适应优化
 * - 支持跨设备量子状态同步和一致性维护
 */

#include "state_manager.h"
#include "../quantum_state.h"
#include "../quantum_entanglement.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* 状态管理器内部结构 */
struct StateManager {
    QState** states;                /* 量子状态数组 */
    size_t state_count;             /* 状态数量 */
    size_t state_capacity;          /* 状态容量 */
    
    QState** active_states;         /* 当前活跃的量子状态 */
    size_t active_count;            /* 活跃状态数量 */
    
    EntanglementRegistry* entanglement_registry; /* 纠缠注册表 */
    
    SystemResourceMonitor* resource_monitor;     /* 资源监控器 */
    
    int auto_optimization_enabled;  /* 是否启用自动优化 */
    double optimization_threshold;  /* 优化阈值 */
    
    StateChangeCallback change_callback; /* 状态变化回调 */
    void* callback_user_data;            /* 回调用户数据 */
};

/* 资源监控器内部结构 */
struct SystemResourceMonitor {
    size_t available_qubits;        /* 可用量子比特数量 */
    size_t total_qubits;            /* 总量子比特数量 */
    double cpu_usage;               /* CPU使用率 */
    double memory_usage;            /* 内存使用率 */
    time_t last_update;             /* 上次更新时间 */
};

/* 创建状态管理器 */
StateManager* state_manager_create(void) {
    StateManager* manager = (StateManager*)malloc(sizeof(StateManager));
    if (!manager) {
        return NULL;
    }
    
    /* 初始化状态数组 */
    manager->state_capacity = 16;
    manager->states = (QState**)malloc(manager->state_capacity * sizeof(QState*));
    if (!manager->states) {
        free(manager);
        return NULL;
    }
    manager->state_count = 0;
    
    /* 初始化活跃状态数组 */
    manager->active_states = (QState**)malloc(manager->state_capacity * sizeof(QState*));
    if (!manager->active_states) {
        free(manager->states);
        free(manager);
        return NULL;
    }
    manager->active_count = 0;
    
    /* 创建纠缠注册表 */
    manager->entanglement_registry = entanglement_registry_create();
    if (!manager->entanglement_registry) {
        free(manager->active_states);
        free(manager->states);
        free(manager);
        return NULL;
    }
    
    /* 创建资源监控器 */
    manager->resource_monitor = (SystemResourceMonitor*)malloc(sizeof(SystemResourceMonitor));
    if (!manager->resource_monitor) {
        entanglement_registry_destroy(manager->entanglement_registry);
        free(manager->active_states);
        free(manager->states);
        free(manager);
        return NULL;
    }
    
    /* 初始化资源监控器 */
    manager->resource_monitor->available_qubits = 128; /* 默认值 */
    manager->resource_monitor->total_qubits = 128;
    manager->resource_monitor->cpu_usage = 0.0;
    manager->resource_monitor->memory_usage = 0.0;
    manager->resource_monitor->last_update = time(NULL);
    
    /* 设置默认配置 */
    manager->auto_optimization_enabled = 1;
    manager->optimization_threshold = 0.75;
    manager->change_callback = NULL;
    manager->callback_user_data = NULL;
    
    /* 初始化随机数生成器 */
    srand((unsigned int)time(NULL));
    
    return manager;
}

/* 销毁状态管理器 */
void state_manager_destroy(StateManager* manager) {
    if (!manager) {
        return;
    }
    
    /* 释放所有状态 */
    for (size_t i = 0; i < manager->state_count; i++) {
        quantum_state_destroy(manager->states[i]);
    }
    
    /* 释放资源 */
    entanglement_registry_destroy(manager->entanglement_registry);
    free(manager->resource_monitor);
    free(manager->active_states);
    free(manager->states);
    free(manager);
}

/* 添加量子状态 */
int state_manager_add_state(StateManager* manager, QState* state) {
    if (!manager || !state) {
        return 0;
    }
    
    /* 检查容量并扩展 */
    if (manager->state_count >= manager->state_capacity) {
        size_t new_capacity = manager->state_capacity * 2;
        QState** new_states = (QState**)realloc(manager->states, new_capacity * sizeof(QState*));
        if (!new_states) {
            return 0;
        }
        manager->states = new_states;
        
        QState** new_active = (QState**)realloc(manager->active_states, new_capacity * sizeof(QState*));
        if (!new_active) {
            return 0;
        }
        manager->active_states = new_active;
        
        manager->state_capacity = new_capacity;
    }
    
    /* 添加状态 */
    manager->states[manager->state_count++] = state;
    
    /* 更新资源使用情况 */
    update_resource_usage(manager);
    
    /* 通知状态变化 */
    if (manager->change_callback) {
        manager->change_callback(state, STATE_ADDED, manager->callback_user_data);
    }
    
    return 1;
}

/* 查找量子状态 */
QState* state_manager_find_state(StateManager* manager, const char* name) {
    if (!manager || !name) {
        return NULL;
    }
    
    for (size_t i = 0; i < manager->state_count; i++) {
        if (strcmp(manager->states[i]->name, name) == 0) {
            return manager->states[i];
        }
    }
    
    return NULL;
}

/* 激活量子状态 */
int state_manager_activate_state(StateManager* manager, QState* state) {
    if (!manager || !state) {
        return 0;
    }
    
    /* 检查状态是否已经激活 */
    for (size_t i = 0; i < manager->active_count; i++) {
        if (manager->active_states[i] == state) {
            return 1; /* 已经激活 */
        }
    }
    
    /* 添加到活跃状态列表 */
    manager->active_states[manager->active_count++] = state;
    
    /* 通知状态变化 */
    if (manager->change_callback) {
        manager->change_callback(state, STATE_ACTIVATED, manager->callback_user_data);
    }
    
    return 1;
}

/* 停用量子状态 */
int state_manager_deactivate_state(StateManager* manager, QState* state) {
    if (!manager || !state) {
        return 0;
    }
    
    /* 查找并移除活跃状态 */
    size_t pos = manager->active_count;
    for (size_t i = 0; i < manager->active_count; i++) {
        if (manager->active_states[i] == state) {
            pos = i;
            break;
        }
    }
    
    if (pos >= manager->active_count) {
        return 0; /* 未找到 */
    }
    
    /* 移动最后一个元素到当前位置 */
    manager->active_states[pos] = manager->active_states[--manager->active_count];
    
    /* 通知状态变化 */
    if (manager->change_callback) {
        manager->change_callback(state, STATE_DEACTIVATED, manager->callback_user_data);
    }
    
    return 1;
}

/* 删除量子状态 */
int state_manager_remove_state(StateManager* manager, QState* state) {
    if (!manager || !state) {
        return 0;
    }
    
    /* 先停用状态 */
    state_manager_deactivate_state(manager, state);
    
    /* 查找并删除状态 */
    size_t pos = manager->state_count;
    for (size_t i = 0; i < manager->state_count; i++) {
        if (manager->states[i] == state) {
            pos = i;
            break;
        }
    }
    
    if (pos >= manager->state_count) {
        return 0; /* 未找到 */
    }
    
    /* 通知状态变化 */
    if (manager->change_callback) {
        manager->change_callback(state, STATE_REMOVED, manager->callback_user_data);
    }
    
    /* 从纠缠注册表中移除 */
    entanglement_registry_remove_state(manager->entanglement_registry, state);
    
    /* 销毁状态 */
    quantum_state_destroy(state);
    
    /* 移动最后一个元素到当前位置 */
    manager->states[pos] = manager->states[--manager->state_count];
    
    /* 更新资源使用情况 */
    update_resource_usage(manager);
    
    return 1;
}

/* 创建量子状态 */
QState* state_manager_create_state(StateManager* manager, const char* name) {
    if (!manager || !name) {
        return NULL;
    }
    
    /* 检查资源是否足够 */
    if (manager->resource_monitor->available_qubits < 1) {
        /* 尝试优化资源 */
        if (!optimize_resource_usage(manager)) {
            return NULL;
        }
    }
    
    /* 创建量子状态 */
    QState* state = quantum_state_create(name);
    if (!state) {
        return NULL;
    }
    
    /* 添加到管理器 */
    if (!state_manager_add_state(manager, state)) {
        quantum_state_destroy(state);
        return NULL;
    }
    
    return state;
}

/* 纠缠两个量子状态 */
int state_manager_entangle_states(StateManager* manager, QState* state1, QState* state2, double strength) {
    if (!manager || !state1 || !state2 || strength < 0.0 || strength > 1.0) {
        return 0;
    }
    
    /* 创建纠缠关系 */
    QEntanglement* entanglement = quantum_entanglement_create(state1, state2, strength);
    if (!entanglement) {
        return 0;
    }
    
    /* 将纠缠添加到状态 */
    if (!quantum_state_add_entanglement(state1, entanglement) ||
        !quantum_state_add_entanglement(state2, entanglement)) {
        quantum_entanglement_destroy(entanglement);
        return 0;
    }
    
    /* 注册纠缠关系 */
    entanglement_registry_add(manager->entanglement_registry, entanglement);
    
    /* 通知状态变化 */
    if (manager->change_callback) {
        manager->change_callback(state1, STATE_ENTANGLED, manager->callback_user_data);
        manager->change_callback(state2, STATE_ENTANGLED, manager->callback_user_data);
    }
    
    return 1;
}

/* 设置状态变化回调 */
void state_manager_set_change_callback(StateManager* manager, StateChangeCallback callback, void* user_data) {
    if (!manager) {
        return;
    }
    
    manager->change_callback = callback;
    manager->callback_user_data = user_data;
}

/* 获取纠缠注册表 */
EntanglementRegistry* state_manager_get_registry(StateManager* manager) {
    if (!manager) {
        return NULL;
    }
    
    return manager->entanglement_registry;
}

/* 获取资源监控器 */
SystemResourceMonitor* state_manager_get_resource_monitor(StateManager* manager) {
    if (!manager) {
        return NULL;
    }
    
    return manager->resource_monitor;
}

/* 设置自动优化配置 */
void state_manager_set_auto_optimization(StateManager* manager, int enabled, double threshold) {
    if (!manager) {
        return;
    }
    
    manager->auto_optimization_enabled = enabled;
    if (threshold > 0.0 && threshold <= 1.0) {
        manager->optimization_threshold = threshold;
    }
}

/* 内部函数：更新资源使用情况 */
static void update_resource_usage(StateManager* manager) {
    if (!manager) {
        return;
    }
    
    /* 更新时间 */
    manager->resource_monitor->last_update = time(NULL);
    
    /* 计算量子比特使用情况 */
    size_t used_qubits = 0;
    for (size_t i = 0; i < manager->state_count; i++) {
        QState* state = manager->states[i];
        
        /* 根据状态类型估算量子比特使用量 */
        switch (state->type) {
            case QSTATE_BASIC:
                used_qubits += 1;
                break;
                
            case QSTATE_SUPERPOSITION:
                used_qubits += 2;
                break;
                
            case QSTATE_ENTANGLED:
                used_qubits += 2;
                break;
                
            case QSTATE_MEASURED:
                used_qubits += 1;
                break;
        }
    }
    
    /* 更新可用量子比特 */
    if (used_qubits < manager->resource_monitor->total_qubits) {
        manager->resource_monitor->available_qubits = 
            manager->resource_monitor->total_qubits - used_qubits;
    } else {
        manager->resource_monitor->available_qubits = 0;
    }
    
    /* 计算CPU和内存使用率（这里是模拟值） */
    manager->resource_monitor->cpu_usage = (double)manager->active_count / 
                                          (double)manager->state_capacity;
    
    manager->resource_monitor->memory_usage = (double)manager->state_count / 
                                             (double)manager->state_capacity;
    
    /* 自动优化检查 */
    if (manager->auto_optimization_enabled && 
        manager->resource_monitor->available_qubits < 
        manager->resource_monitor->total_qubits * (1.0 - manager->optimization_threshold)) {
        optimize_resource_usage(manager);
    }
}

/* 内部函数：优化资源使用 */
static int optimize_resource_usage(StateManager* manager) {
    if (!manager) {
        return 0;
    }
    
    /* 找出非活跃状态并可能测量它们 */
    for (size_t i = 0; i < manager->state_count; i++) {
        QState* state = manager->states[i];
        int is_active = 0;
        
        /* 检查状态是否在活跃列表中 */
        for (size_t j = 0; j < manager->active_count; j++) {
            if (manager->active_states[j] == state) {
                is_active = 1;
                break;
            }
        }
        
        /* 对非活跃的叠加态或纠缠态进行测量，释放资源 */
        if (!is_active && (state->type == QSTATE_SUPERPOSITION || state->type == QSTATE_ENTANGLED)) {
            QState* measured_state = quantum_state_measure(state);
            
            /* 用测量结果替换原状态 */
            if (measured_state) {
                /* 更新纠缠关系 */
                entanglement_registry_update_state(manager->entanglement_registry, state, measured_state);
                
                /* 替换状态 */
                quantum_state_destroy(state);
                manager->states[i] = measured_state;
            }
        }
    }
    
    /* 更新资源使用情况 */
    update_resource_usage(manager);
    
    return manager->resource_monitor->available_qubits > 0;
} 