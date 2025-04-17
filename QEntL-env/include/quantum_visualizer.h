/**
 * @file quantum_visualizer.h
 * @brief 量子状态可视化工具库
 * @author Claude
 * @version 1.0
 * @date 2024-05-31
 */

#ifndef QUANTUM_VISUALIZER_H
#define QUANTUM_VISUALIZER_H

#include <stdbool.h>
#include "quantum_state.h"

/**
 * @brief 可视化模式枚举
 */
typedef enum {
    MODE_BLOCH_SPHERE,    /* 布洛赫球表示 */
    MODE_PROBABILITY_BAR,  /* 概率柱状图 */
    MODE_STATE_VECTOR,     /* 状态向量 */
    MODE_DENSITY_MATRIX,   /* 密度矩阵 */
    MODE_CIRCUIT          /* 量子电路 */
} VisualizationMode;

/**
 * @brief 颜色方案枚举
 */
typedef enum {
    COLOR_SCHEME_DEFAULT,  /* 默认配色方案 */
    COLOR_SCHEME_HEATMAP,  /* 热图颜色方案 */
    COLOR_SCHEME_RAINBOW,  /* 彩虹颜色方案 */
    COLOR_SCHEME_GRAYSCALE /* 灰度色方案 */
} ColorScheme;

/**
 * @brief 量子可视化器前向声明
 */
typedef struct QuantumVisualizer QuantumVisualizer;

/**
 * @brief 创建量子可视化器
 * 
 * @param width 可视化画布宽度
 * @param height 可视化画布高度
 * @param mode 可视化模式
 * @return QuantumVisualizer* 创建的可视化器指针
 */
QuantumVisualizer* visualizer_create(unsigned int width, unsigned int height, VisualizationMode mode);

/**
 * @brief 销毁量子可视化器
 * 
 * @param vis 可视化器指针
 */
void visualizer_destroy(QuantumVisualizer *vis);

/**
 * @brief 设置可视化模式
 * 
 * @param vis 可视化器指针
 * @param mode 可视化模式
 * @return int 成功返回0，失败返回-1
 */
int visualizer_set_mode(QuantumVisualizer *vis, VisualizationMode mode);

/**
 * @brief 设置颜色方案
 * 
 * @param vis 可视化器指针
 * @param scheme 颜色方案
 * @return int 成功返回0，失败返回-1
 */
int visualizer_set_color_scheme(QuantumVisualizer *vis, ColorScheme scheme);

/**
 * @brief 设置是否显示概率
 * 
 * @param vis 可视化器指针
 * @param show 是否显示
 * @return int 成功返回0，失败返回-1
 */
int visualizer_show_probability(QuantumVisualizer *vis, bool show);

/**
 * @brief 设置是否显示相位
 * 
 * @param vis 可视化器指针
 * @param show 是否显示
 * @return int 成功返回0，失败返回-1
 */
int visualizer_show_phase(QuantumVisualizer *vis, bool show);

/**
 * @brief 清空画布
 * 
 * @param vis 可视化器指针
 * @return int 成功返回0，失败返回-1
 */
int visualizer_clear(QuantumVisualizer *vis);

/**
 * @brief 渲染单量子比特状态
 * 
 * @param vis 可视化器指针
 * @param state 量子状态
 * @return int 成功返回0，失败返回-1
 */
int visualizer_render_qubit(QuantumVisualizer *vis, QuantumState *state);

/**
 * @brief 渲染多量子比特系统
 * 
 * @param vis 可视化器指针
 * @param state 量子状态
 * @return int 成功返回0，失败返回-1
 */
int visualizer_render_multi_qubit(QuantumVisualizer *vis, QuantumState *state);

/**
 * @brief 渲染量子纠缠
 * 
 * @param vis 可视化器指针
 * @param state 量子状态
 * @return int 成功返回0，失败返回-1
 */
int visualizer_render_entanglement(QuantumVisualizer *vis, QuantumState *state);

/**
 * @brief 渲染量子场
 * 
 * @param vis 可视化器指针
 * @param field 量子场
 * @return int 成功返回0，失败返回-1
 */
int visualizer_render_quantum_field(QuantumVisualizer *vis, void *field);

/**
 * @brief 显示可视化结果
 * 
 * @param vis 可视化器指针
 * @return int 成功返回0，失败返回-1
 */
int visualizer_display(QuantumVisualizer *vis);

/**
 * @brief 导出可视化结果到文件
 * 
 * @param vis 可视化器指针
 * @param filename 文件名
 * @return int 成功返回0，失败返回-1
 */
int visualizer_export(QuantumVisualizer *vis, const char *filename);

#endif /* QUANTUM_VISUALIZER_H */ 