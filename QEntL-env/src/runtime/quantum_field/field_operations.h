/**
 * 量子场操作接口头文件
 * 
 * 定义了量子场的高级操作函数，包括交互、演化、分析和可视化等功能。
 * 这些接口在量子场管理器的基础上提供更高级的功能。
 */

#ifndef QENTL_FIELD_OPERATIONS_H
#define QENTL_FIELD_OPERATIONS_H

#include "field_manager.h"

/**
 * 场操作类型枚举
 */
typedef enum {
    FIELD_OP_AMPLIFY,           // 振幅放大
    FIELD_OP_ATTENUATE,         // 振幅衰减
    FIELD_OP_PHASE_SHIFT,       // 相位偏移
    FIELD_OP_SUPERPOSE,         // 叠加
    FIELD_OP_ENTANGLE,          // 纠缠
    FIELD_OP_DECOHERE,          // 退相干
    FIELD_OP_TRANSFORM,         // 转换
    FIELD_OP_ANALYZE,           // 分析
    FIELD_OP_VISUALIZE,         // 可视化
    FIELD_OP_CUSTOM             // 自定义操作
} FieldOperationType;

/**
 * 场操作参数结构
 */
typedef struct {
    FieldOperationType type;    // 操作类型
    double param1;              // 参数1（针对不同操作类型有不同含义）
    double param2;              // 参数2
    double param3;              // 参数3
    void* custom_params;        // 自定义参数
} FieldOperationParams;

/**
 * 场交互结果
 */
typedef struct {
    int success;                     // 操作是否成功
    char* operation_description;     // 操作描述
    double effect_magnitude;         // 效果幅度
    double energy_before;            // 操作前能量
    double energy_after;             // 操作后能量
    double entropy_before;           // 操作前熵
    double entropy_after;            // 操作后熵
    char* timestamp;                 // 操作时间戳
    FieldManagerError error;         // 错误代码
} FieldOperationResult;

/**
 * 场演化配置
 */
typedef struct {
    double time_step;               // 时间步长
    int steps;                      // 步数
    double stability_threshold;     // 稳定性阈值
    int record_trajectory;          // 是否记录轨迹
    int adaptive_step;              // 是否自适应步长
    void* custom_evolution_params;  // 自定义演化参数
} FieldEvolutionConfig;

/**
 * 场演化轨迹
 */
typedef struct {
    int step_count;                 // 步数
    double* time_points;            // 时间点数组
    double* energy_trajectory;      // 能量轨迹
    double* entropy_trajectory;     // 熵轨迹
    double* coherence_trajectory;   // 相干性轨迹
    char* evolution_id;             // 演化ID
    char* start_timestamp;          // 开始时间戳
    char* end_timestamp;            // 结束时间戳
} FieldEvolutionTrajectory;

/**
 * 场分析结果
 */
typedef struct {
    char* analysis_type;            // 分析类型
    double* metric_values;          // 指标值数组
    char** metric_names;            // 指标名称数组
    int metric_count;               // 指标数量
    void* custom_analysis_result;   // 自定义分析结果
    char* analysis_timestamp;       // 分析时间戳
} FieldAnalysisResult;

/**
 * 场可视化选项
 */
typedef struct {
    char* visualization_type;       // 可视化类型
    int resolution_x;               // X轴分辨率
    int resolution_y;               // Y轴分辨率
    int resolution_z;               // Z轴分辨率
    int color_map;                  // 色彩映射
    int show_nodes;                 // 是否显示节点
    int show_boundaries;            // 是否显示边界
    int show_vectors;               // 是否显示向量
    void* custom_vis_params;        // 自定义可视化参数
} FieldVisualizationOptions;

/**
 * 场可视化结果
 */
typedef struct {
    void* visualization_data;       // 可视化数据
    size_t data_size;               // 数据大小
    char* format;                   // 格式（如"png"、"svg"等）
    int width;                      // 宽度
    int height;                     // 高度
    char* title;                    // 标题
    char* description;              // 描述
    char* generation_timestamp;     // 生成时间戳
} FieldVisualizationResult;

/**
 * 应用操作到量子场
 * 
 * @param manager 管理器
 * @param reference 量子场引用
 * @param operation 操作类型
 * @param params 操作参数
 * @return 操作结果
 */
FieldOperationResult apply_field_operation(FieldManager* manager, 
                                          FieldReference* reference,
                                          FieldOperationType operation,
                                          FieldOperationParams params);

/**
 * 叠加两个量子场
 * 
 * @param manager 管理器
 * @param reference1 第一个量子场引用
 * @param reference2 第二个量子场引用
 * @param weight1 第一个场的权重
 * @param weight2 第二个场的权重
 * @param result_options 结果场的创建选项
 * @return 叠加后的新量子场引用
 */
FieldReference* superpose_fields(FieldManager* manager,
                               FieldReference* reference1,
                               FieldReference* reference2,
                               double weight1,
                               double weight2,
                               FieldCreationOptions result_options);

/**
 * 在量子场中创建波
 * 
 * @param manager 管理器
 * @param reference 量子场引用
 * @param center_x 中心X坐标
 * @param center_y 中心Y坐标
 * @param center_z 中心Z坐标
 * @param amplitude 振幅
 * @param frequency 频率
 * @param phase 相位
 * @return 操作结果
 */
FieldOperationResult create_wave_in_field(FieldManager* manager,
                                         FieldReference* reference,
                                         double center_x,
                                         double center_y,
                                         double center_z,
                                         double amplitude,
                                         double frequency,
                                         double phase);

/**
 * 演化量子场
 * 
 * @param manager 管理器
 * @param reference 量子场引用
 * @param config 演化配置
 * @return 演化轨迹
 */
FieldEvolutionTrajectory evolve_field_with_trajectory(FieldManager* manager,
                                                    FieldReference* reference,
                                                    FieldEvolutionConfig config);

/**
 * 释放演化轨迹资源
 * 
 * @param trajectory 要释放的轨迹
 */
void free_evolution_trajectory(FieldEvolutionTrajectory* trajectory);

/**
 * 分析量子场
 * 
 * @param manager 管理器
 * @param reference 量子场引用
 * @param analysis_type 分析类型
 * @param custom_params 自定义参数
 * @return 分析结果
 */
FieldAnalysisResult analyze_field(FieldManager* manager,
                                 FieldReference* reference,
                                 const char* analysis_type,
                                 void* custom_params);

/**
 * 释放分析结果资源
 * 
 * @param result 要释放的结果
 */
void free_analysis_result(FieldAnalysisResult* result);

/**
 * 可视化量子场
 * 
 * @param manager 管理器
 * @param reference 量子场引用
 * @param options 可视化选项
 * @return 可视化结果
 */
FieldVisualizationResult visualize_field(FieldManager* manager,
                                        FieldReference* reference,
                                        FieldVisualizationOptions options);

/**
 * 释放可视化结果资源
 * 
 * @param result 要释放的结果
 */
void free_visualization_result(FieldVisualizationResult* result);

/**
 * 在两个量子场之间创建隧道
 * 
 * @param manager 管理器
 * @param reference1 第一个量子场引用
 * @param x1 第一个场中的X坐标
 * @param y1 第一个场中的Y坐标
 * @param z1 第一个场中的Z坐标
 * @param reference2 第二个量子场引用
 * @param x2 第二个场中的X坐标
 * @param y2 第二个场中的Y坐标
 * @param z2 第二个场中的Z坐标
 * @param strength 隧道强度
 * @return 操作结果
 */
FieldOperationResult create_field_tunnel(FieldManager* manager,
                                        FieldReference* reference1,
                                        double x1, double y1, double z1,
                                        FieldReference* reference2,
                                        double x2, double y2, double z2,
                                        double strength);

/**
 * 检测量子场的异常
 * 
 * @param manager 管理器
 * @param reference 量子场引用
 * @param threshold 异常阈值
 * @param custom_params 自定义参数
 * @return 分析结果
 */
FieldAnalysisResult detect_field_anomalies(FieldManager* manager,
                                          FieldReference* reference,
                                          double threshold,
                                          void* custom_params);

/**
 * 优化量子场
 * 
 * @param manager 管理器
 * @param reference 量子场引用
 * @param target_property 目标属性
 * @param optimize_value 优化目标值
 * @return 操作结果
 */
FieldOperationResult optimize_field(FieldManager* manager,
                                   FieldReference* reference,
                                   const char* target_property,
                                   double optimize_value);

/**
 * 合并多个量子场
 * 
 * @param manager 管理器
 * @param references 量子场引用数组
 * @param weights 权重数组
 * @param count 场数量
 * @param result_options 结果场的创建选项
 * @return 合并后的新量子场引用
 */
FieldReference* merge_fields(FieldManager* manager,
                           FieldReference** references,
                           double* weights,
                           int count,
                           FieldCreationOptions result_options);

/**
 * 提取量子场的特征
 * 
 * @param manager 管理器
 * @param reference 量子场引用
 * @param feature_type 特征类型
 * @param custom_params 自定义参数
 * @return 分析结果
 */
FieldAnalysisResult extract_field_features(FieldManager* manager,
                                          FieldReference* reference,
                                          const char* feature_type,
                                          void* custom_params);

#endif /* QENTL_FIELD_OPERATIONS_H */ 