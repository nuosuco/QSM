/**
 * QEntL量子状态管理器头文件
 * 
 * 量子基因编码: QG-RUNTIME-STMGR-HDR-A5B3-1713051200
 * 
 * @文件: state_manager.h
 * @描述: 定义QEntL运行时的量子状态管理API
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-16
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 状态管理支持量子比特动态分配和自适应优化
 * - 支持跨设备量子状态同步和一致性维护
 */

#ifndef QENTL_STATE_MANAGER_H
#define QENTL_STATE_MANAGER_H

#include "../quantum_state.h"
#include "../quantum_entanglement.h"

/**
 * 前向声明
 */
typedef struct StateManager StateManager;
typedef struct SystemResourceMonitor SystemResourceMonitor;
typedef struct EntanglementRegistry EntanglementRegistry;

/**
 * 状态变化类型枚举
 */
typedef enum {
    STATE_ADDED,           /* 状态被添加 */
    STATE_REMOVED,         /* 状态被移除 */
    STATE_ACTIVATED,       /* 状态被激活 */
    STATE_DEACTIVATED,     /* 状态被停用 */
    STATE_MODIFIED,        /* 状态被修改 */
    STATE_ENTANGLED,       /* 状态被纠缠 */
    STATE_MEASURED         /* 状态被测量 */
} StateChangeType;

/**
 * 状态变化回调函数类型
 * 
 * @param state 发生变化的量子状态
 * @param change_type 变化类型
 * @param user_data 用户数据
 */
typedef void (*StateChangeCallback)(QState* state, StateChangeType change_type, void* user_data);

/**
 * 创建状态管理器
 * 
 * @return 新创建的状态管理器
 */
StateManager* state_manager_create(void);

/**
 * 销毁状态管理器
 * 
 * @param manager 要销毁的状态管理器
 */
void state_manager_destroy(StateManager* manager);

/**
 * 添加量子状态
 * 
 * @param manager 状态管理器
 * @param state 要添加的量子状态
 * @return 成功返回1，失败返回0
 */
int state_manager_add_state(StateManager* manager, QState* state);

/**
 * 查找量子状态
 * 
 * @param manager 状态管理器
 * @param name 状态名称
 * @return 找到的量子状态，未找到返回NULL
 */
QState* state_manager_find_state(StateManager* manager, const char* name);

/**
 * 激活量子状态
 * 
 * @param manager 状态管理器
 * @param state 要激活的量子状态
 * @return 成功返回1，失败返回0
 */
int state_manager_activate_state(StateManager* manager, QState* state);

/**
 * 停用量子状态
 * 
 * @param manager 状态管理器
 * @param state 要停用的量子状态
 * @return 成功返回1，失败返回0
 */
int state_manager_deactivate_state(StateManager* manager, QState* state);

/**
 * 删除量子状态
 * 
 * @param manager 状态管理器
 * @param state 要删除的量子状态
 * @return 成功返回1，失败返回0
 */
int state_manager_remove_state(StateManager* manager, QState* state);

/**
 * 创建量子状态
 * 
 * @param manager 状态管理器
 * @param name 状态名称
 * @return 创建的量子状态，失败返回NULL
 */
QState* state_manager_create_state(StateManager* manager, const char* name);

/**
 * 纠缠两个量子状态
 * 
 * @param manager 状态管理器
 * @param state1 第一个量子状态
 * @param state2 第二个量子状态
 * @param strength 纠缠强度 (0.0-1.0)
 * @return 成功返回1，失败返回0
 */
int state_manager_entangle_states(StateManager* manager, QState* state1, QState* state2, double strength);

/**
 * 设置状态变化回调
 * 
 * @param manager 状态管理器
 * @param callback 回调函数
 * @param user_data 用户数据
 */
void state_manager_set_change_callback(StateManager* manager, StateChangeCallback callback, void* user_data);

/**
 * 获取纠缠注册表
 * 
 * @param manager 状态管理器
 * @return 纠缠注册表
 */
EntanglementRegistry* state_manager_get_registry(StateManager* manager);

/**
 * 获取资源监控器
 * 
 * @param manager 状态管理器
 * @return 资源监控器
 */
SystemResourceMonitor* state_manager_get_resource_monitor(StateManager* manager);

/**
 * 设置自动优化配置
 * 
 * @param manager 状态管理器
 * @param enabled 是否启用自动优化
 * @param threshold 优化阈值 (0.0-1.0)
 */
void state_manager_set_auto_optimization(StateManager* manager, int enabled, double threshold);

/**
 * 内部函数：更新资源使用情况
 */
static void update_resource_usage(StateManager* manager);

/**
 * 内部函数：优化资源使用
 */
static int optimize_resource_usage(StateManager* manager);

/**
 * 纠缠注册表函数
 */

/**
 * 创建纠缠注册表
 * 
 * @return 新创建的纠缠注册表
 */
EntanglementRegistry* entanglement_registry_create(void);

/**
 * 销毁纠缠注册表
 * 
 * @param registry 要销毁的纠缠注册表
 */
void entanglement_registry_destroy(EntanglementRegistry* registry);

/**
 * 添加纠缠关系
 * 
 * @param registry 纠缠注册表
 * @param entanglement 要添加的纠缠关系
 * @return 成功返回1，失败返回0
 */
int entanglement_registry_add(EntanglementRegistry* registry, QEntanglement* entanglement);

/**
 * 移除量子状态的所有纠缠关系
 * 
 * @param registry 纠缠注册表
 * @param state 量子状态
 * @return 成功返回1，失败返回0
 */
int entanglement_registry_remove_state(EntanglementRegistry* registry, QState* state);

/**
 * 更新量子状态引用
 * 
 * @param registry 纠缠注册表
 * @param old_state 旧状态
 * @param new_state 新状态
 * @return 成功返回1，失败返回0
 */
int entanglement_registry_update_state(EntanglementRegistry* registry, QState* old_state, QState* new_state);

#endif /* QENTL_STATE_MANAGER_H */ 