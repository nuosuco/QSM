/**
 * @file quantum_visualizer.c
 * @brief 量子状态可视化工具库实现
 * @author Claude
 * @version 1.0
 * @date 2024-05-31
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "../../include/quantum_state.h"
#include "../../include/quantum_visualizer.h"

/**
 * @brief 量子可视化器结构体
 */
struct QuantumVisualizer {
    unsigned int width;                /* 可视化画布宽度 */
    unsigned int height;               /* 可视化画布高度 */
    char *canvas;                      /* 字符画布 */
    VisualizationMode mode;            /* 可视化模式 */
    ColorScheme colorScheme;           /* 颜色方案 */
    bool showProbability;              /* 是否显示概率 */
    bool showPhase;                    /* 是否显示相位 */
    void *rendererData;                /* 渲染器特定数据 */
};

/**
 * @brief 创建量子可视化器
 * 
 * @param width 可视化画布宽度
 * @param height 可视化画布高度
 * @param mode 可视化模式
 * @return QuantumVisualizer* 创建的可视化器指针
 */
QuantumVisualizer* visualizer_create(unsigned int width, unsigned int height, VisualizationMode mode) {
    QuantumVisualizer *vis = (QuantumVisualizer*)malloc(sizeof(QuantumVisualizer));
    if (!vis) {
        fprintf(stderr, "无法分配可视化器内存\n");
        return NULL;
    }
    
    vis->width = width;
    vis->height = height;
    vis->mode = mode;
    vis->colorScheme = COLOR_SCHEME_DEFAULT;
    vis->showProbability = true;
    vis->showPhase = true;
    vis->rendererData = NULL;
    
    size_t canvasSize = width * height;
    vis->canvas = (char*)malloc(canvasSize * sizeof(char));
    if (!vis->canvas) {
        fprintf(stderr, "无法分配画布内存\n");
        free(vis);
        return NULL;
    }
    
    // 初始化画布
    memset(vis->canvas, ' ', canvasSize);
    
    printf("量子可视化器已创建，模式：%d，尺寸：%d x %d\n", mode, width, height);
    return vis;
}

/**
 * @brief 销毁量子可视化器
 * 
 * @param vis 可视化器指针
 */
void visualizer_destroy(QuantumVisualizer *vis) {
    if (!vis) return;
    
    if (vis->canvas) {
        free(vis->canvas);
    }
    
    if (vis->rendererData) {
        free(vis->rendererData);
    }
    
    free(vis);
    printf("量子可视化器已销毁\n");
}

/**
 * @brief 设置可视化模式
 * 
 * @param vis 可视化器指针
 * @param mode 可视化模式
 * @return int 成功返回0，失败返回-1
 */
int visualizer_set_mode(QuantumVisualizer *vis, VisualizationMode mode) {
    if (!vis) return -1;
    
    vis->mode = mode;
    printf("可视化模式已设置为: %d\n", mode);
    return 0;
}

/**
 * @brief 设置颜色方案
 * 
 * @param vis 可视化器指针
 * @param scheme 颜色方案
 * @return int 成功返回0，失败返回-1
 */
int visualizer_set_color_scheme(QuantumVisualizer *vis, ColorScheme scheme) {
    if (!vis) return -1;
    
    vis->colorScheme = scheme;
    printf("颜色方案已设置为: %d\n", scheme);
    return 0;
}

/**
 * @brief 设置是否显示概率
 * 
 * @param vis 可视化器指针
 * @param show 是否显示
 * @return int 成功返回0，失败返回-1
 */
int visualizer_show_probability(QuantumVisualizer *vis, bool show) {
    if (!vis) return -1;
    
    vis->showProbability = show;
    return 0;
}

/**
 * @brief 设置是否显示相位
 * 
 * @param vis 可视化器指针
 * @param show 是否显示
 * @return int 成功返回0，失败返回-1
 */
int visualizer_show_phase(QuantumVisualizer *vis, bool show) {
    if (!vis) return -1;
    
    vis->showPhase = show;
    return 0;
}

/**
 * @brief 清空画布
 * 
 * @param vis 可视化器指针
 * @return int 成功返回0，失败返回-1
 */
int visualizer_clear(QuantumVisualizer *vis) {
    if (!vis || !vis->canvas) return -1;
    
    memset(vis->canvas, ' ', vis->width * vis->height);
    return 0;
}

/**
 * @brief 渲染单量子比特状态
 * 
 * @param vis 可视化器指针
 * @param state 量子状态
 * @return int 成功返回0，失败返回-1
 */
int visualizer_render_qubit(QuantumVisualizer *vis, QuantumState *state) {
    if (!vis || !state) return -1;
    
    visualizer_clear(vis);
    
    // 根据不同的可视化模式渲染
    switch (vis->mode) {
        case MODE_BLOCH_SPHERE:
            return _render_bloch_sphere(vis, state);
        case MODE_PROBABILITY_BAR:
            return _render_probability_bar(vis, state);
        case MODE_STATE_VECTOR:
            return _render_state_vector(vis, state);
        default:
            fprintf(stderr, "不支持的可视化模式\n");
            return -1;
    }
}

/**
 * @brief 渲染多量子比特系统
 * 
 * @param vis 可视化器指针
 * @param state 量子状态
 * @return int 成功返回0，失败返回-1
 */
int visualizer_render_multi_qubit(QuantumVisualizer *vis, QuantumState *state) {
    if (!vis || !state) return -1;
    
    visualizer_clear(vis);
    
    // 根据不同的可视化模式渲染
    switch (vis->mode) {
        case MODE_PROBABILITY_BAR:
            return _render_probability_bar(vis, state);
        case MODE_STATE_VECTOR:
            return _render_state_vector(vis, state);
        case MODE_DENSITY_MATRIX:
            return _render_density_matrix(vis, state);
        default:
            fprintf(stderr, "不支持的可视化模式\n");
            return -1;
    }
}

/**
 * @brief 渲染量子纠缠
 * 
 * @param vis 可视化器指针
 * @param state 量子状态
 * @return int 成功返回0，失败返回-1
 */
int visualizer_render_entanglement(QuantumVisualizer *vis, QuantumState *state) {
    if (!vis || !state) return -1;
    
    visualizer_clear(vis);
    
    // 计算并显示纠缠度
    double entanglement = _calculate_entanglement(state);
    
    // 使用ASCII艺术呈现纠缠关系
    int centerX = vis->width / 2;
    int centerY = vis->height / 2;
    
    // 画两个量子比特
    _draw_circle(vis, centerX - 10, centerY, 5);
    _draw_circle(vis, centerX + 10, centerY, 5);
    
    // 画连接线，线的密度代表纠缠度
    int connections = (int)(entanglement * 10);
    for (int i = 0; i < connections; i++) {
        _draw_line(vis, centerX - 5, centerY, centerX + 5, centerY);
    }
    
    return 0;
}

/**
 * @brief 渲染量子场
 * 
 * @param vis 可视化器指针
 * @param field 量子场
 * @return int 成功返回0，失败返回-1
 */
int visualizer_render_quantum_field(QuantumVisualizer *vis, void *field) {
    if (!vis || !field) return -1;
    
    visualizer_clear(vis);
    
    // 量子场的可视化逻辑
    // 此处为示例，实际实现需要根据量子场的具体结构
    
    return 0;
}

/**
 * @brief 显示可视化结果
 * 
 * @param vis 可视化器指针
 * @return int 成功返回0，失败返回-1
 */
int visualizer_display(QuantumVisualizer *vis) {
    if (!vis || !vis->canvas) return -1;
    
    // 输出画布内容到控制台
    for (unsigned int y = 0; y < vis->height; y++) {
        for (unsigned int x = 0; x < vis->width; x++) {
            putchar(vis->canvas[y * vis->width + x]);
        }
        putchar('\n');
    }
    
    return 0;
}

/**
 * @brief 导出可视化结果到文件
 * 
 * @param vis 可视化器指针
 * @param filename 文件名
 * @return int 成功返回0，失败返回-1
 */
int visualizer_export(QuantumVisualizer *vis, const char *filename) {
    if (!vis || !vis->canvas || !filename) return -1;
    
    FILE *file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "无法打开文件 %s 进行写入\n", filename);
        return -1;
    }
    
    // 写入画布内容到文件
    for (unsigned int y = 0; y < vis->height; y++) {
        for (unsigned int x = 0; x < vis->width; x++) {
            fputc(vis->canvas[y * vis->width + x], file);
        }
        fputc('\n', file);
    }
    
    fclose(file);
    printf("可视化结果已导出到文件: %s\n", filename);
    return 0;
}

// 内部辅助函数
// -----------------------------------

/**
 * @brief 在布洛赫球上渲染量子比特状态
 */
static int _render_bloch_sphere(QuantumVisualizer *vis, QuantumState *state) {
    // 获取量子比特的布洛赫球坐标
    double x, y, z;
    _get_bloch_coordinates(state, &x, &y, &z);
    
    // 渲染布洛赫球和状态点
    _draw_sphere(vis, vis->width / 2, vis->height / 2, vis->height / 3);
    _draw_point(vis, 
                (int)(vis->width / 2 + x * vis->height / 3), 
                (int)(vis->height / 2 + y * vis->height / 3),
                '*');
    
    return 0;
}

/**
 * @brief 渲染概率条形图
 */
static int _render_probability_bar(QuantumVisualizer *vis, QuantumState *state) {
    // 获取量子态的概率分布
    int numStates = 1 << _get_num_qubits(state);
    double *probabilities = (double*)malloc(numStates * sizeof(double));
    _get_probabilities(state, probabilities, numStates);
    
    // 渲染概率条形图
    int barWidth = vis->width / numStates;
    for (int i = 0; i < numStates; i++) {
        int barHeight = (int)(probabilities[i] * vis->height);
        for (int h = 0; h < barHeight; h++) {
            for (int w = 0; w < barWidth; w++) {
                int x = i * barWidth + w;
                int y = vis->height - h - 1;
                if (x < vis->width && y < vis->height) {
                    vis->canvas[y * vis->width + x] = '#';
                }
            }
        }
    }
    
    free(probabilities);
    return 0;
}

/**
 * @brief 渲染状态向量
 */
static int _render_state_vector(QuantumVisualizer *vis, QuantumState *state) {
    // 获取状态向量
    int numStates = 1 << _get_num_qubits(state);
    complex_t *amplitudes = (complex_t*)malloc(numStates * sizeof(complex_t));
    _get_amplitudes(state, amplitudes, numStates);
    
    // 示例实现：在控制台显示状态向量的振幅和相位
    int centerY = vis->height / 2;
    for (int i = 0; i < numStates; i++) {
        char stateLabel[20];
        sprintf(stateLabel, "|%d⟩", i);
        
        // 写入态标签
        int labelPos = i * (vis->width / numStates);
        for (int j = 0; j < strlen(stateLabel); j++) {
            if (labelPos + j < vis->width) {
                vis->canvas[centerY * vis->width + labelPos + j] = stateLabel[j];
            }
        }
        
        // 计算振幅
        double amplitude = sqrt(amplitudes[i].real * amplitudes[i].real + 
                              amplitudes[i].imag * amplitudes[i].imag);
        
        // 显示振幅为线条长度
        int ampLength = (int)(amplitude * 10);
        for (int j = 0; j < ampLength; j++) {
            if (labelPos + j < vis->width) {
                vis->canvas[(centerY - 2) * vis->width + labelPos + j] = '|';
            }
        }
    }
    
    free(amplitudes);
    return 0;
}

/**
 * @brief 渲染密度矩阵
 */
static int _render_density_matrix(QuantumVisualizer *vis, QuantumState *state) {
    // 此处为示例，实际实现需要计算密度矩阵并渲染
    // ...
    
    return 0;
}

/**
 * @brief 在画布上画一个圆
 */
static void _draw_circle(QuantumVisualizer *vis, int centerX, int centerY, int radius) {
    for (int y = -radius; y <= radius; y++) {
        for (int x = -radius; x <= radius; x++) {
            if (x*x + y*y <= radius*radius + radius && 
                x*x + y*y >= radius*radius - radius) {
                
                int drawX = centerX + x;
                int drawY = centerY + y;
                
                if (drawX >= 0 && drawX < vis->width && 
                    drawY >= 0 && drawY < vis->height) {
                    vis->canvas[drawY * vis->width + drawX] = 'o';
                }
            }
        }
    }
}

/**
 * @brief 在画布上画一条线
 */
static void _draw_line(QuantumVisualizer *vis, int x1, int y1, int x2, int y2) {
    int dx = abs(x2 - x1);
    int dy = abs(y2 - y1);
    int sx = (x1 < x2) ? 1 : -1;
    int sy = (y1 < y2) ? 1 : -1;
    int err = dx - dy;
    
    while (1) {
        if (x1 >= 0 && x1 < vis->width && y1 >= 0 && y1 < vis->height) {
            vis->canvas[y1 * vis->width + x1] = '-';
        }
        
        if (x1 == x2 && y1 == y2) break;
        
        int e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            x1 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y1 += sy;
        }
    }
}

/**
 * @brief 在画布上画一个点
 */
static void _draw_point(QuantumVisualizer *vis, int x, int y, char symbol) {
    if (x >= 0 && x < vis->width && y >= 0 && y < vis->height) {
        vis->canvas[y * vis->width + x] = symbol;
    }
}

/**
 * @brief 在画布上画一个球体
 */
static void _draw_sphere(QuantumVisualizer *vis, int centerX, int centerY, int radius) {
    for (int y = -radius; y <= radius; y++) {
        for (int x = -radius; x <= radius; x++) {
            double distance = sqrt(x*x + y*y);
            if (distance < radius) {
                // 计算球面效果
                char symbol = ' ';
                if (distance > radius * 0.9) {
                    symbol = '.';
                } else if (x*x + y*y <= radius/3) {
                    symbol = 'O';
                } else {
                    double z = sqrt(radius*radius - x*x - y*y);
                    double intensity = z / radius;
                    
                    if (intensity > 0.8) symbol = '@';
                    else if (intensity > 0.6) symbol = '#';
                    else if (intensity > 0.4) symbol = '*';
                    else if (intensity > 0.2) symbol = '+';
                    else symbol = '.';
                }
                
                int drawX = centerX + x;
                int drawY = centerY + y;
                
                if (drawX >= 0 && drawX < vis->width && 
                    drawY >= 0 && drawY < vis->height) {
                    vis->canvas[drawY * vis->width + drawX] = symbol;
                }
            }
        }
    }
    
    // 画坐标轴
    for (int i = -radius; i <= radius; i++) {
        int x = centerX + i;
        int y = centerY;
        if (x >= 0 && x < vis->width && y >= 0 && y < vis->height) {
            vis->canvas[y * vis->width + x] = '-';
        }
        
        x = centerX;
        y = centerY + i;
        if (x >= 0 && x < vis->width && y >= 0 && y < vis->height) {
            vis->canvas[y * vis->width + x] = '|';
        }
    }
}

/**
 * @brief 获取量子比特的布洛赫球坐标
 */
static void _get_bloch_coordinates(QuantumState *state, double *x, double *y, double *z) {
    // 此处为示例，实际实现需要从量子态中计算布洛赫球坐标
    // 假设从状态中获取了布洛赫球坐标
    *x = 0.5;
    *y = 0.5;
    *z = 0.707;
}

/**
 * @brief 获取量子比特数量
 */
static int _get_num_qubits(QuantumState *state) {
    // 此处为示例，实际实现需要从量子态中获取比特数
    return 2; // 假设为2量子比特系统
}

/**
 * @brief 获取量子态的概率分布
 */
static void _get_probabilities(QuantumState *state, double *probabilities, int numStates) {
    // 此处为示例，实际实现需要从量子态中计算概率
    for (int i = 0; i < numStates; i++) {
        probabilities[i] = 1.0 / numStates; // 均匀分布示例
    }
}

/**
 * @brief 获取量子态的振幅
 */
static void _get_amplitudes(QuantumState *state, complex_t *amplitudes, int numStates) {
    // 此处为示例，实际实现需要从量子态中获取振幅
    for (int i = 0; i < numStates; i++) {
        amplitudes[i].real = 1.0 / sqrt(numStates);
        amplitudes[i].imag = 0.0;
    }
}

/**
 * @brief 计算量子纠缠度
 */
static double _calculate_entanglement(QuantumState *state) {
    // 此处为示例，实际实现需要计算纠缠度（例如冯诺依曼熵）
    return 0.8; // 假设纠缠度为0.8
} 