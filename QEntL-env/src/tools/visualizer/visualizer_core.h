/**
 * QEntL量子状态可视化工具头文件
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月19日
 */

#ifndef QENTL_VISUALIZER_CORE_H
#define QENTL_VISUALIZER_CORE_H

#include <stdio.h>
#include <stdbool.h>
#include <complex.h>

// 颜色方案
typedef enum {
    SCHEME_DEFAULT,    // 默认方案
    SCHEME_DARK,       // 暗色方案
    SCHEME_LIGHT,      // 亮色方案
    SCHEME_VIBRANT,    // 鲜艳方案
    SCHEME_PASTEL      // 柔和方案
} ColorScheme;

// 向量表示方式
typedef enum {
    VECTOR_ARROWS,     // 箭头表示
    VECTOR_BARS,       // 条形图表示
    VECTOR_CIRCLES,    // 圆形表示
    VECTOR_SPHERES     // 球形表示
} VectorRepresentation;

// 输出模式
typedef enum {
    OUTPUT_CONSOLE,    // 控制台输出
    OUTPUT_FILE,       // 文件输出
    OUTPUT_CALLBACK    // 回调函数输出
} VisualizerOutputMode;

// 可视化器配置
typedef struct {
    ColorScheme color_scheme;              // 颜色方案
    bool bloch_sphere;                     // 是否显示布洛赫球
    bool show_phase;                       // 是否显示相位
    bool show_probabilities;               // 是否显示概率
    bool animation;                        // 是否启用动画
    VectorRepresentation vector_representation; // 向量表示方式
} VisualizerConfig;

// 可视化数据
typedef struct {
    int qubit_count;                       // 量子比特数
    complex double* amplitudes;            // 状态振幅
    const double** entanglement_matrix;    // 纠缠矩阵
    int* measurement_counts;               // 测量结果计数
    int total_measurements;                // 总测量次数
    double* field_strength;                // 场强度
    int field_dimensions[3];               // 场维度
} VisualizerData;

// 前置声明
typedef struct Visualizer Visualizer;

// 可视化回调函数类型
typedef void (*VisualizerCallback)(const VisualizerData* data, void* user_data);

// 创建可视化器
Visualizer* visualizer_create(void);

// 销毁可视化器
void visualizer_destroy(Visualizer* vis);

// 设置可视化器配置
void visualizer_set_config(Visualizer* vis, const VisualizerConfig* config);

// 获取可视化器配置
void visualizer_get_config(Visualizer* vis, VisualizerConfig* config);

// 设置输出模式
bool visualizer_set_output_mode(Visualizer* vis, VisualizerOutputMode mode, const char* filename);

// 设置回调函数
void visualizer_set_callback(Visualizer* vis, VisualizerCallback callback, void* user_data);

// 设置量子态
bool visualizer_set_quantum_state(Visualizer* vis, int qubit_count, const complex double* amplitudes);

// 设置纠缠矩阵
bool visualizer_set_entanglement_matrix(Visualizer* vis, int qubit_count, const double** matrix);

// 设置量子场数据
bool visualizer_set_quantum_field(Visualizer* vis, int x_dim, int y_dim, int z_dim, const double* strength);

// 添加测量结果
void visualizer_add_measurement(Visualizer* vis, int state);

// 可视化量子态
void visualizer_visualize(Visualizer* vis);

#endif /* QENTL_VISUALIZER_CORE_H */ 