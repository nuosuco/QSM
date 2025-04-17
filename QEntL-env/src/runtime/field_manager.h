/**
 * QEntL量子场管理器头文件
 * 
 * 量子基因编码: QG-RUNTIME-FLDMGR-HDR-D7E3-1713051200
 * 
 * @文件: field_manager.h
 * @描述: 定义QEntL运行时的量子场管理API
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-16
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 场管理支持多维量子场动态生成和演化
 * - 支持量子场间的相互作用和拓扑结构变换
 */

#ifndef QENTL_FIELD_MANAGER_H
#define QENTL_FIELD_MANAGER_H

#include "../quantum_field.h"
#include "../quantum_field_generator.h"
#include "state_manager.h"
#include <time.h>

/* 常量定义 */
#define MAX_FIELD_DIMENSIONS 11       /* 最大场维度 */
#define MAX_STATES_PER_EXCHANGE 32    /* 每次交换的最大状态数 */

/**
 * 前向声明
 */
typedef struct FieldManager FieldManager;
typedef struct FieldInteraction FieldInteraction;
typedef struct FieldInteractionMap FieldInteractionMap;
typedef struct FieldGenerator FieldGenerator;

/**
 * 场变化类型枚举
 */
typedef enum {
    FIELD_ADDED,               /* 场被添加 */
    FIELD_REMOVED,             /* 场被移除 */
    FIELD_ACTIVATED,           /* 场被激活 */
    FIELD_DEACTIVATED,         /* 场被停用 */
    FIELD_MODIFIED,            /* 场被修改 */
    FIELD_EVOLVED,             /* 场演化了 */
    FIELD_INTERACTION_CHANGED  /* 场交互发生变化 */
} FieldChangeType;

/**
 * 交互类型枚举
 */
typedef enum {
    INTERACTION_NONE,              /* 无交互 */
    INTERACTION_ENERGY_TRANSFER,   /* 能量传递 */
    INTERACTION_INFORMATION_EXCHANGE, /* 信息交换 */
    INTERACTION_SPATIAL_DISTORTION /* 空间扭曲 */
} InteractionType;

/**
 * 预定义场类型枚举
 */
typedef enum {
    PRESET_FIELD_UNIFORM,          /* 均匀场 */
    PRESET_FIELD_GRADIENT,         /* 梯度场 */
    PRESET_FIELD_RADIAL,           /* 径向场 */
    PRESET_FIELD_WAVE,             /* 波动场 */
    PRESET_FIELD_VORTEX,           /* 涡旋场 */
    PRESET_FIELD_CHAOTIC           /* 混沌场 */
} PredefinedFieldType;

/**
 * 模拟质量枚举
 */
typedef enum {
    SIMULATION_QUALITY_LOW,        /* 低质量模拟 */
    SIMULATION_QUALITY_MEDIUM,     /* 中质量模拟 */
    SIMULATION_QUALITY_HIGH,       /* 高质量模拟 */
    SIMULATION_QUALITY_ULTRA       /* 超高质量模拟 */
} SimulationQuality;

/**
 * 场交互结构
 */
typedef struct FieldInteraction {
    QField* field1;             /* 第一个场 */
    QField* field2;             /* 第二个场 */
    InteractionType type;       /* 交互类型 */
    double strength;            /* 交互强度 */
} FieldInteraction;

/**
 * 场交互图结构
 */
typedef struct FieldInteractionMap {
    FieldInteraction** interactions; /* 交互数组 */
    int interaction_count;           /* 交互数量 */
    int interaction_capacity;        /* 交互容量 */
} FieldInteractionMap;

/**
 * 模拟统计数据结构
 */
typedef struct {
    time_t start_time;             /* 开始时间 */
    time_t last_simulation_time;   /* 上次模拟时间 */
    double total_simulation_time;  /* 总模拟耗时 */
    int simulation_steps;          /* 模拟步数 */
    double total_energy;           /* 总能量 */
    double total_entropy;          /* 总熵 */
} FieldSimulationStats;

/**
 * 场变化回调函数类型
 * 
 * @param field 发生变化的量子场
 * @param change_type 变化类型
 * @param user_data 用户数据
 */
typedef void (*FieldChangeCallback)(QField* field, FieldChangeType change_type, void* user_data);

/**
 * 创建场管理器
 * 
 * @param state_manager 状态管理器
 * @return 新创建的场管理器
 */
FieldManager* field_manager_create(StateManager* state_manager);

/**
 * 销毁场管理器
 * 
 * @param manager 要销毁的场管理器
 */
void field_manager_destroy(FieldManager* manager);

/**
 * 添加量子场
 * 
 * @param manager 场管理器
 * @param field 要添加的量子场
 * @return 成功返回1，失败返回0
 */
int field_manager_add_field(FieldManager* manager, QField* field);

/**
 * 查找量子场
 * 
 * @param manager 场管理器
 * @param name 场名称
 * @return 找到的量子场，未找到返回NULL
 */
QField* field_manager_find_field(FieldManager* manager, const char* name);

/**
 * 激活量子场
 * 
 * @param manager 场管理器
 * @param field 要激活的量子场
 * @return 成功返回1，失败返回0
 */
int field_manager_activate_field(FieldManager* manager, QField* field);

/**
 * 停用量子场
 * 
 * @param manager 场管理器
 * @param field 要停用的量子场
 * @return 成功返回1，失败返回0
 */
int field_manager_deactivate_field(FieldManager* manager, QField* field);

/**
 * 删除量子场
 * 
 * @param manager 场管理器
 * @param field 要删除的量子场
 * @return 成功返回1，失败返回0
 */
int field_manager_remove_field(FieldManager* manager, QField* field);

/**
 * 创建量子场
 * 
 * @param manager 场管理器
 * @param name 场名称
 * @param type 场类型
 * @param dimensions 场维度
 * @return 创建的量子场，失败返回NULL
 */
QField* field_manager_create_field(FieldManager* manager, const char* name, FieldType type, int dimensions);

/**
 * 创建预定义的量子场
 * 
 * @param manager 场管理器
 * @param name 场名称
 * @param preset 预定义场类型
 * @return 创建的量子场，失败返回NULL
 */
QField* field_manager_create_predefined_field(FieldManager* manager, const char* name, PredefinedFieldType preset);

/**
 * 添加量子状态到场
 * 
 * @param manager 场管理器
 * @param field 目标量子场
 * @param state 要添加的量子状态
 * @param coordinates 状态在场中的坐标
 * @return 成功返回1，失败返回0
 */
int field_manager_add_state_to_field(FieldManager* manager, QField* field, QState* state, 
                                   double coordinates[MAX_FIELD_DIMENSIONS]);

/**
 * 设置场变化回调
 * 
 * @param manager 场管理器
 * @param callback 回调函数
 * @param user_data 用户数据
 */
void field_manager_set_change_callback(FieldManager* manager, FieldChangeCallback callback, void* user_data);

/**
 * 定义场之间的交互
 * 
 * @param manager 场管理器
 * @param field1 第一个场
 * @param field2 第二个场
 * @param type 交互类型
 * @param strength 交互强度
 * @return 成功返回1，失败返回0
 */
int field_manager_define_interaction(FieldManager* manager, QField* field1, QField* field2, 
                                   InteractionType type, double strength);

/**
 * 模拟场的演化
 * 
 * @param manager 场管理器
 * @param time_span 模拟时间跨度
 * @return 成功返回1，失败返回0
 */
int field_manager_simulate_evolution(FieldManager* manager, double time_span);

/**
 * 获取模拟统计
 * 
 * @param manager 场管理器
 * @return 模拟统计数据
 */
FieldSimulationStats field_manager_get_stats(FieldManager* manager);

/**
 * 设置模拟参数
 * 
 * @param manager 场管理器
 * @param quality 模拟质量
 * @param step 模拟步长
 */
void field_manager_set_simulation_parameters(FieldManager* manager, int quality, double step);

/**
 * 内部函数：处理场之间的相互作用
 */
static void process_field_interactions(FieldManager* manager, double time_step);

/**
 * 内部函数：应用能量传递相互作用
 */
static void apply_energy_transfer(QField* field1, QField* field2, double strength, double time_step);

/**
 * 内部函数：应用信息交换相互作用
 */
static void apply_information_exchange(QField* field1, QField* field2, double strength, double time_step);

/**
 * 内部函数：应用空间扭曲相互作用
 */
static void apply_spatial_distortion(QField* field1, QField* field2, double strength, double time_step);

/**
 * 内部函数：找到场中最近的状态
 */
static QState* find_nearest_state(QField* field, QState* target_state);

/**
 * 场交互图API
 */

/**
 * 创建场交互图
 * 
 * @return 新创建的场交互图
 */
FieldInteractionMap* field_interaction_map_create(void);

/**
 * 销毁场交互图
 * 
 * @param map 要销毁的场交互图
 */
void field_interaction_map_destroy(FieldInteractionMap* map);

/**
 * 添加场交互
 * 
 * @param map 场交互图
 * @param field1 第一个场
 * @param field2 第二个场
 * @param type 交互类型
 * @param strength 交互强度
 * @return 成功返回1，失败返回0
 */
int field_interaction_map_add(FieldInteractionMap* map, QField* field1, QField* field2, 
                            InteractionType type, double strength);

/**
 * 移除场的所有交互
 * 
 * @param map 场交互图
 * @param field 要移除的场
 * @return 移除的交互数量
 */
int field_interaction_map_remove_field(FieldInteractionMap* map, QField* field);

/**
 * 获取活跃场的交互
 * 
 * @param map 场交互图
 * @param active_fields 活跃场数组
 * @param active_count 活跃场数量
 * @param result 输出交互数组
 * @param result_count 输出交互数量
 * @return 成功返回1，失败返回0
 */
int field_interaction_map_get_active(FieldInteractionMap* map, 
                                   QField** active_fields, 
                                   int active_count,
                                   FieldInteraction*** result, 
                                   int* result_count);

#endif /* QENTL_FIELD_MANAGER_H */ 