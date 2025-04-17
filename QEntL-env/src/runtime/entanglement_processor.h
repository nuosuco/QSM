/**
 * QEntL量子纠缠处理器头文件
 * 
 * 量子基因编码: QG-RUNTIME-ENTPROC-HDR-C3D1-1713051200
 * 
 * @文件: entanglement_processor.h
 * @描述: 定义QEntL运行时的量子纠缠处理API
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-16
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 纠缠处理支持复杂量子网络拓扑和量子纠缠传递
 * - 支持跨设备量子纠缠同步和高效通信
 */

#ifndef QENTL_ENTANGLEMENT_PROCESSOR_H
#define QENTL_ENTANGLEMENT_PROCESSOR_H

#include "../quantum_state.h"
#include "../quantum_entanglement.h"
#include "state_manager.h"

/* 常量定义 */
#define MAX_PATH_LENGTH 16          /* 最大路径长度 */
#define MAX_INFLUENCE_STATES 64     /* 最大影响状态数 */

/**
 * 前向声明
 */
typedef struct EntanglementProcessor EntanglementProcessor;

/**
 * 效应类型枚举
 */
typedef enum {
    EFFECT_STATE_CHANGE,           /* 状态变化效应 */
    EFFECT_SUPERPOSITION_TRANSFER, /* 叠加态传递效应 */
    EFFECT_ENTANGLEMENT_TRANSFER   /* 纠缠传递效应 */
} EffectType;

/**
 * 纠缠路径结构
 */
typedef struct {
    QState* states[MAX_PATH_LENGTH];        /* 路径上的状态 */
    QEntanglement* entanglements[MAX_PATH_LENGTH - 1]; /* 路径上的纠缠关系 */
    int state_count;                        /* 状态数量 */
    int entanglement_count;                 /* 纠缠关系数量 */
    double total_strength;                  /* 总纠缠强度 */
} EntanglementPath;

/**
 * 影响图结构
 */
typedef struct {
    QState* center_state;                      /* 中心状态 */
    QState* states[MAX_INFLUENCE_STATES];      /* 受影响状态 */
    double strengths[MAX_INFLUENCE_STATES];    /* 影响强度 */
    int state_count;                           /* 状态数量 */
} InfluenceMap;

/**
 * 处理器统计数据结构
 */
typedef struct {
    time_t start_time;               /* 开始时间 */
    time_t stop_time;                /* 停止时间 */
    int processing_cycles;           /* 处理周期数 */
    int total_effects_processed;     /* 处理的总效应数 */
    double avg_effect_strength;      /* 平均效应强度 */
} EntanglementProcessorStats;

/**
 * 纠缠回调函数类型
 * 
 * @param entanglement 纠缠关系
 * @param source_state 源状态
 * @param target_state 目标状态
 * @param effect_type 效应类型
 * @param effect_strength 效应强度
 */
typedef void (*EntanglementCallback)(QEntanglement* entanglement, 
                                    QState* source_state, 
                                    QState* target_state,
                                    EffectType effect_type,
                                    double effect_strength);

/**
 * 创建纠缠处理器
 * 
 * @param state_manager 状态管理器
 * @return 新创建的纠缠处理器
 */
EntanglementProcessor* entanglement_processor_create(StateManager* state_manager);

/**
 * 销毁纠缠处理器
 * 
 * @param processor 要销毁的纠缠处理器
 */
void entanglement_processor_destroy(EntanglementProcessor* processor);

/**
 * 启动纠缠处理器
 * 
 * @param processor 纠缠处理器
 * @return 成功返回1，失败返回0
 */
int entanglement_processor_start(EntanglementProcessor* processor);

/**
 * 停止纠缠处理器
 * 
 * @param processor 纠缠处理器
 */
void entanglement_processor_stop(EntanglementProcessor* processor);

/**
 * 注册纠缠回调
 * 
 * @param processor 纠缠处理器
 * @param callback 回调函数
 * @return 成功返回1，失败返回0
 */
int entanglement_processor_register_callback(EntanglementProcessor* processor, 
                                          EntanglementCallback callback);

/**
 * 设置纠缠处理参数
 * 
 * @param processor 纠缠处理器
 * @param coherence_threshold 相干性阈值
 * @param propagation_speed 传播速度
 */
void entanglement_processor_set_parameters(EntanglementProcessor* processor, 
                                         double coherence_threshold,
                                         double propagation_speed);

/**
 * 处理单个纠缠效应
 * 
 * @param processor 纠缠处理器
 * @param entanglement 纠缠关系
 * @param source_state 源状态
 * @param target_state 目标状态
 * @return 成功返回1，失败返回0
 */
int entanglement_processor_process_effect(EntanglementProcessor* processor, 
                                        QEntanglement* entanglement,
                                        QState* source_state,
                                        QState* target_state);

/**
 * 处理一个周期的纠缠效应
 * 
 * @param processor 纠缠处理器
 * @return 处理的效应数量
 */
int entanglement_processor_process_cycle(EntanglementProcessor* processor);

/**
 * 获取处理器统计数据
 * 
 * @param processor 纠缠处理器
 * @return 处理器统计数据
 */
EntanglementProcessorStats entanglement_processor_get_stats(EntanglementProcessor* processor);

/**
 * 检测纠缠路径
 * 
 * @param processor 纠缠处理器
 * @param source 源状态
 * @param target 目标状态
 * @param path 输出路径
 * @return 成功返回1，失败返回0
 */
int entanglement_processor_detect_path(EntanglementProcessor* processor, 
                                     QState* source, 
                                     QState* target,
                                     EntanglementPath* path);

/**
 * 计算纠缠影响范围
 * 
 * @param processor 纠缠处理器
 * @param source 源状态
 * @param map 输出影响图
 * @return 受影响状态的数量
 */
int entanglement_processor_calculate_influence(EntanglementProcessor* processor,
                                             QState* source,
                                             InfluenceMap* map);

/**
 * 内部函数：应用纠缠效应
 */
static int apply_entanglement_effect(EntanglementProcessor* processor, 
                                   EntanglementEffect* effect);

/**
 * 纠缠注册表API - 在entanglement_registry.c中实现
 */

/**
 * 获取所有纠缠关系
 * 
 * @param registry 纠缠注册表
 * @param entanglements 输出纠缠数组
 * @param count 输出纠缠数量
 * @return 成功返回1，失败返回0
 */
int entanglement_registry_get_all(EntanglementRegistry* registry, 
                                QEntanglement*** entanglements, 
                                int* count);

/**
 * 查找两个状态之间的纠缠关系
 * 
 * @param registry 纠缠注册表
 * @param state1 第一个状态
 * @param state2 第二个状态
 * @return 找到的纠缠关系，未找到返回NULL
 */
QEntanglement* entanglement_registry_find(EntanglementRegistry* registry, 
                                        QState* state1, 
                                        QState* state2);

/**
 * 获取与状态相关的所有纠缠关系
 * 
 * @param registry 纠缠注册表
 * @param state 量子状态
 * @param entanglements 输出纠缠数组
 * @param count 输出纠缠数量
 * @return 成功返回1，失败返回0
 */
int entanglement_registry_get_for_state(EntanglementRegistry* registry, 
                                      QState* state, 
                                      QEntanglement*** entanglements, 
                                      int* count);

#endif /* QENTL_ENTANGLEMENT_PROCESSOR_H */ 