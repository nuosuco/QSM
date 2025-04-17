/**
 * QEntL量子状态可视化工具核心实现
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月19日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <complex.h>
#include "visualizer_core.h"

// 常量定义
#define MAX_QUBITS 20
#define MAX_STATES (1 << MAX_QUBITS)  // 2^MAX_QUBITS

// 可视化器结构
struct Visualizer {
    VisualizerConfig config;           // 配置
    VisualizerOutputMode output_mode;  // 输出模式
    FILE* output_file;                 // 输出文件
    
    // 状态数据
    int qubit_count;                   // 量子比特数
    complex double* amplitudes;        // 状态振幅
    int* measurement_counts;           // 测量结果计数
    int total_measurements;            // 总测量次数
    
    // 纠缠数据
    double** entanglement_matrix;      // 纠缠矩阵
    
    // 场数据
    double* field_strength;            // 场强度
    int field_dimensions[3];           // 场维度
    
    // 回调函数
    VisualizerCallback callback;       // 回调函数
    void* callback_data;               // 回调函数用户数据
};

// 创建可视化器
Visualizer* visualizer_create(void) {
    Visualizer* vis = (Visualizer*)malloc(sizeof(Visualizer));
    if (!vis) {
        fprintf(stderr, "错误：无法分配可视化器内存\n");
        return NULL;
    }
    
    // 初始化配置
    vis->config.color_scheme = SCHEME_DEFAULT;
    vis->config.bloch_sphere = true;
    vis->config.show_phase = true;
    vis->config.show_probabilities = true;
    vis->config.animation = true;
    vis->config.vector_representation = VECTOR_ARROWS;
    
    // 初始化模式和输出
    vis->output_mode = OUTPUT_CONSOLE;
    vis->output_file = NULL;
    
    // 初始化状态数据
    vis->qubit_count = 0;
    vis->amplitudes = NULL;
    vis->measurement_counts = NULL;
    vis->total_measurements = 0;
    
    // 初始化纠缠数据
    vis->entanglement_matrix = NULL;
    
    // 初始化场数据
    vis->field_strength = NULL;
    vis->field_dimensions[0] = 0;
    vis->field_dimensions[1] = 0;
    vis->field_dimensions[2] = 0;
    
    // 初始化回调
    vis->callback = NULL;
    vis->callback_data = NULL;
    
    return vis;
}

// 销毁可视化器
void visualizer_destroy(Visualizer* vis) {
    if (!vis) return;
    
    // 释放状态数据
    if (vis->amplitudes) {
        free(vis->amplitudes);
    }
    
    if (vis->measurement_counts) {
        free(vis->measurement_counts);
    }
    
    // 释放纠缠矩阵
    if (vis->entanglement_matrix) {
        for (int i = 0; i < vis->qubit_count; i++) {
            if (vis->entanglement_matrix[i]) {
                free(vis->entanglement_matrix[i]);
            }
        }
        free(vis->entanglement_matrix);
    }
    
    // 释放场数据
    if (vis->field_strength) {
        free(vis->field_strength);
    }
    
    // 关闭输出文件
    if (vis->output_file && vis->output_file != stdout) {
        fclose(vis->output_file);
    }
    
    // 释放可视化器
    free(vis);
}

// 设置可视化器配置
void visualizer_set_config(Visualizer* vis, const VisualizerConfig* config) {
    if (!vis || !config) return;
    
    vis->config = *config;
}

// 获取可视化器配置
void visualizer_get_config(Visualizer* vis, VisualizerConfig* config) {
    if (!vis || !config) return;
    
    *config = vis->config;
}

// 设置输出模式
bool visualizer_set_output_mode(Visualizer* vis, VisualizerOutputMode mode, const char* filename) {
    if (!vis) return false;
    
    // 关闭之前的输出文件
    if (vis->output_file && vis->output_file != stdout) {
        fclose(vis->output_file);
        vis->output_file = NULL;
    }
    
    vis->output_mode = mode;
    
    // 处理不同的输出模式
    switch (mode) {
        case OUTPUT_CONSOLE:
            vis->output_file = stdout;
            break;
            
        case OUTPUT_FILE:
            if (!filename) {
                fprintf(stderr, "错误：需要提供文件名\n");
                return false;
            }
            
            vis->output_file = fopen(filename, "w");
            if (!vis->output_file) {
                fprintf(stderr, "错误：无法打开输出文件 %s\n", filename);
                vis->output_file = stdout;
                return false;
            }
            break;
            
        case OUTPUT_CALLBACK:
            // 回调模式不需要文件
            vis->output_file = NULL;
            break;
            
        default:
            fprintf(stderr, "错误：未知的输出模式\n");
            return false;
    }
    
    return true;
}

// 设置回调函数
void visualizer_set_callback(Visualizer* vis, VisualizerCallback callback, void* user_data) {
    if (!vis) return;
    
    vis->callback = callback;
    vis->callback_data = user_data;
}

// 设置量子态
bool visualizer_set_quantum_state(Visualizer* vis, int qubit_count, const complex double* amplitudes) {
    if (!vis || qubit_count <= 0 || qubit_count > MAX_QUBITS || !amplitudes) {
        return false;
    }
    
    // 释放旧的状态数据
    if (vis->amplitudes) {
        free(vis->amplitudes);
        vis->amplitudes = NULL;
    }
    
    if (vis->measurement_counts) {
        free(vis->measurement_counts);
        vis->measurement_counts = NULL;
    }
    
    // 分配新的状态数据
    int state_count = 1 << qubit_count;
    vis->amplitudes = (complex double*)malloc(state_count * sizeof(complex double));
    if (!vis->amplitudes) {
        fprintf(stderr, "错误：无法分配状态振幅内存\n");
        return false;
    }
    
    vis->measurement_counts = (int*)calloc(state_count, sizeof(int));
    if (!vis->measurement_counts) {
        fprintf(stderr, "错误：无法分配测量计数内存\n");
        free(vis->amplitudes);
        vis->amplitudes = NULL;
        return false;
    }
    
    // 复制状态振幅
    for (int i = 0; i < state_count; i++) {
        vis->amplitudes[i] = amplitudes[i];
    }
    
    vis->qubit_count = qubit_count;
    vis->total_measurements = 0;
    
    return true;
}

// 设置纠缠矩阵
bool visualizer_set_entanglement_matrix(Visualizer* vis, int qubit_count, const double** matrix) {
    if (!vis || qubit_count <= 0 || qubit_count > MAX_QUBITS || !matrix) {
        return false;
    }
    
    // 释放旧的纠缠矩阵
    if (vis->entanglement_matrix) {
        for (int i = 0; i < vis->qubit_count; i++) {
            if (vis->entanglement_matrix[i]) {
                free(vis->entanglement_matrix[i]);
            }
        }
        free(vis->entanglement_matrix);
        vis->entanglement_matrix = NULL;
    }
    
    // 分配新的纠缠矩阵
    vis->entanglement_matrix = (double**)malloc(qubit_count * sizeof(double*));
    if (!vis->entanglement_matrix) {
        fprintf(stderr, "错误：无法分配纠缠矩阵内存\n");
        return false;
    }
    
    for (int i = 0; i < qubit_count; i++) {
        vis->entanglement_matrix[i] = (double*)malloc(qubit_count * sizeof(double));
        if (!vis->entanglement_matrix[i]) {
            fprintf(stderr, "错误：无法分配纠缠矩阵行内存\n");
            
            // 释放已分配的行
            for (int j = 0; j < i; j++) {
                free(vis->entanglement_matrix[j]);
            }
            free(vis->entanglement_matrix);
            vis->entanglement_matrix = NULL;
            
            return false;
        }
        
        // 复制纠缠矩阵行
        for (int j = 0; j < qubit_count; j++) {
            vis->entanglement_matrix[i][j] = matrix[i][j];
        }
    }
    
    return true;
}

// 设置量子场数据
bool visualizer_set_quantum_field(Visualizer* vis, int x_dim, int y_dim, int z_dim, const double* strength) {
    if (!vis || x_dim <= 0 || y_dim <= 0 || (z_dim < 0) || !strength) {
        return false;
    }
    
    // 释放旧的场数据
    if (vis->field_strength) {
        free(vis->field_strength);
        vis->field_strength = NULL;
    }
    
    // 计算场数据大小
    int field_size = x_dim * y_dim;
    if (z_dim > 0) {
        field_size *= z_dim;
    }
    
    // 分配新的场数据
    vis->field_strength = (double*)malloc(field_size * sizeof(double));
    if (!vis->field_strength) {
        fprintf(stderr, "错误：无法分配场数据内存\n");
        return false;
    }
    
    // 复制场数据
    for (int i = 0; i < field_size; i++) {
        vis->field_strength[i] = strength[i];
    }
    
    // 设置场维度
    vis->field_dimensions[0] = x_dim;
    vis->field_dimensions[1] = y_dim;
    vis->field_dimensions[2] = z_dim;
    
    return true;
}

// 添加测量结果
void visualizer_add_measurement(Visualizer* vis, int state) {
    if (!vis || !vis->measurement_counts) return;
    
    int state_count = 1 << vis->qubit_count;
    if (state < 0 || state >= state_count) return;
    
    vis->measurement_counts[state]++;
    vis->total_measurements++;
}

// 转换为二进制字符串
static void int_to_binary_string(int value, int bit_count, char* buffer) {
    if (!buffer) return;
    
    buffer[bit_count] = '\0';
    
    for (int i = bit_count - 1; i >= 0; i--) {
        buffer[bit_count - 1 - i] = ((value >> i) & 1) ? '1' : '0';
    }
}

// 绘制概率条形图
static void draw_probability_bars(Visualizer* vis) {
    if (!vis || !vis->amplitudes || !vis->output_file) return;
    
    int state_count = 1 << vis->qubit_count;
    fprintf(vis->output_file, "量子态概率分布:\n");
    
    // 计算最大概率
    double max_prob = 0.0;
    for (int i = 0; i < state_count; i++) {
        double prob = cabs(vis->amplitudes[i]) * cabs(vis->amplitudes[i]);
        if (prob > max_prob) max_prob = prob;
    }
    
    // 绘制条形图
    char binary[MAX_QUBITS + 1];
    for (int i = 0; i < state_count; i++) {
        double prob = cabs(vis->amplitudes[i]) * cabs(vis->amplitudes[i]);
        int_to_binary_string(i, vis->qubit_count, binary);
        
        fprintf(vis->output_file, "|%s>: ", binary);
        
        // 绘制概率条
        int bar_length = (int)(40.0 * (prob / max_prob));
        for (int j = 0; j < bar_length; j++) {
            fprintf(vis->output_file, "|");
        }
        
        fprintf(vis->output_file, " %.4f", prob);
        
        // 如果启用了相位显示，显示相位信息
        if (vis->config.show_phase) {
            double phase = carg(vis->amplitudes[i]);
            fprintf(vis->output_file, " ∠%.2f°", phase * 180.0 / M_PI);
        }
        
        fprintf(vis->output_file, "\n");
    }
}

// 绘制布洛赫球
static void draw_bloch_sphere(Visualizer* vis) {
    if (!vis || !vis->amplitudes || !vis->output_file || vis->qubit_count > 1) return;
    
    fprintf(vis->output_file, "布洛赫球表示 (单量子比特):\n");
    
    // 计算布洛赫球坐标
    double alpha = cabs(vis->amplitudes[0]);
    double beta = cabs(vis->amplitudes[1]);
    double phase = carg(vis->amplitudes[1]) - carg(vis->amplitudes[0]);
    
    double theta = 2.0 * acos(alpha);
    double phi = phase;
    
    double x = sin(theta) * cos(phi);
    double y = sin(theta) * sin(phi);
    double z = cos(theta);
    
    fprintf(vis->output_file, "  量子态 = %.4f|0> + %.4fe^(i%.4f)|1>\n", alpha, beta, phase);
    fprintf(vis->output_file, "  布洛赫坐标: (%.4f, %.4f, %.4f)\n", x, y, z);
    fprintf(vis->output_file, "  θ = %.4f, φ = %.4f\n", theta, phi);
    
    // ASCII 绘制简化的布洛赫球
    fprintf(vis->output_file, "        |z\n");
    fprintf(vis->output_file, "        |\n");
    fprintf(vis->output_file, "        |   •(量子态)\n");
    fprintf(vis->output_file, "        |  /\n");
    fprintf(vis->output_file, "        | /\n");
    fprintf(vis->output_file, "  ------+------y\n");
    fprintf(vis->output_file, "       /|\n");
    fprintf(vis->output_file, "      / |\n");
    fprintf(vis->output_file, "     /  |\n");
    fprintf(vis->output_file, "    /   |\n");
    fprintf(vis->output_file, "   x    |\n");
}

// 绘制纠缠矩阵
static void draw_entanglement_matrix(Visualizer* vis) {
    if (!vis || !vis->entanglement_matrix || !vis->output_file) return;
    
    fprintf(vis->output_file, "量子比特纠缠矩阵:\n");
    
    // 打印列标题
    fprintf(vis->output_file, "     ");
    for (int i = 0; i < vis->qubit_count; i++) {
        fprintf(vis->output_file, "Q%-3d", i);
    }
    fprintf(vis->output_file, "\n");
    
    // 打印分隔线
    fprintf(vis->output_file, "    +");
    for (int i = 0; i < vis->qubit_count; i++) {
        fprintf(vis->output_file, "----");
    }
    fprintf(vis->output_file, "\n");
    
    // 打印矩阵
    for (int i = 0; i < vis->qubit_count; i++) {
        fprintf(vis->output_file, "Q%-3d|", i);
        
        for (int j = 0; j < vis->qubit_count; j++) {
            if (i == j) {
                fprintf(vis->output_file, "    ");
            } else {
                fprintf(vis->output_file, "%.2f ", vis->entanglement_matrix[i][j]);
            }
        }
        
        fprintf(vis->output_file, "\n");
    }
}

// 绘制测量结果统计
static void draw_measurement_statistics(Visualizer* vis) {
    if (!vis || !vis->measurement_counts || !vis->output_file || vis->total_measurements == 0) return;
    
    int state_count = 1 << vis->qubit_count;
    fprintf(vis->output_file, "测量结果统计 (共 %d 次):\n", vis->total_measurements);
    
    // 查找最常见的结果
    int max_count = 0;
    for (int i = 0; i < state_count; i++) {
        if (vis->measurement_counts[i] > max_count) {
            max_count = vis->measurement_counts[i];
        }
    }
    
    // 绘制统计图
    char binary[MAX_QUBITS + 1];
    for (int i = 0; i < state_count; i++) {
        if (vis->measurement_counts[i] > 0) {
            int_to_binary_string(i, vis->qubit_count, binary);
            double percentage = 100.0 * vis->measurement_counts[i] / vis->total_measurements;
            
            fprintf(vis->output_file, "|%s>: ", binary);
            
            // 绘制条形图
            int bar_length = (int)(40.0 * vis->measurement_counts[i] / max_count);
            for (int j = 0; j < bar_length; j++) {
                fprintf(vis->output_file, "|");
            }
            
            fprintf(vis->output_file, " %d (%.1f%%)\n", 
                    vis->measurement_counts[i], percentage);
        }
    }
}

// 在控制台上可视化量子态
static void visualize_state_console(Visualizer* vis) {
    if (!vis || !vis->amplitudes || !vis->output_file) return;
    
    fprintf(vis->output_file, "===== 量子态可视化 =====\n");
    fprintf(vis->output_file, "量子比特数: %d\n", vis->qubit_count);
    fprintf(vis->output_file, "\n");
    
    // 显示状态向量
    fprintf(vis->output_file, "状态向量:\n");
    int state_count = 1 << vis->qubit_count;
    char binary[MAX_QUBITS + 1];
    for (int i = 0; i < state_count; i++) {
        if (cabs(vis->amplitudes[i]) > 1e-10) {
            int_to_binary_string(i, vis->qubit_count, binary);
            double mag = cabs(vis->amplitudes[i]);
            double phase = carg(vis->amplitudes[i]) * 180.0 / M_PI;
            fprintf(vis->output_file, "  |%s> : %.4f∠%.1f° (%.4f + %.4fi)\n", 
                    binary, mag, phase, creal(vis->amplitudes[i]), cimag(vis->amplitudes[i]));
        }
    }
    fprintf(vis->output_file, "\n");
    
    // 绘制概率分布
    if (vis->config.show_probabilities) {
        draw_probability_bars(vis);
        fprintf(vis->output_file, "\n");
    }
    
    // 绘制布洛赫球
    if (vis->config.bloch_sphere && vis->qubit_count == 1) {
        draw_bloch_sphere(vis);
        fprintf(vis->output_file, "\n");
    }
    
    // 绘制测量统计
    if (vis->total_measurements > 0) {
        draw_measurement_statistics(vis);
        fprintf(vis->output_file, "\n");
    }
    
    // 绘制纠缠矩阵
    if (vis->entanglement_matrix) {
        draw_entanglement_matrix(vis);
        fprintf(vis->output_file, "\n");
    }
    
    fprintf(vis->output_file, "=========================\n");
}

// 使用回调函数可视化量子态
static void visualize_state_callback(Visualizer* vis) {
    if (!vis || !vis->callback) return;
    
    // 构建回调数据
    VisualizerData data;
    data.qubit_count = vis->qubit_count;
    data.amplitudes = vis->amplitudes;
    data.entanglement_matrix = (const double**)vis->entanglement_matrix;
    data.measurement_counts = vis->measurement_counts;
    data.total_measurements = vis->total_measurements;
    data.field_strength = vis->field_strength;
    data.field_dimensions[0] = vis->field_dimensions[0];
    data.field_dimensions[1] = vis->field_dimensions[1];
    data.field_dimensions[2] = vis->field_dimensions[2];
    
    // 调用回调函数
    vis->callback(&data, vis->callback_data);
}

// 可视化量子态
void visualizer_visualize(Visualizer* vis) {
    if (!vis) return;
    
    switch (vis->output_mode) {
        case OUTPUT_CONSOLE:
        case OUTPUT_FILE:
            visualize_state_console(vis);
            break;
            
        case OUTPUT_CALLBACK:
            visualize_state_callback(vis);
            break;
    }
} 