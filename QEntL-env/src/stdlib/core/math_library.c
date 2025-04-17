/**
 * @file math_library.c
 * @brief QEntL核心数学库实现
 * @author AI助手
 * @version 1.0
 * @date 2023-10-30
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <string.h>
#include "math_library.h"

// 定义复数类型（如果系统没有complex.h，可以取消注释以下定义）
/*
typedef struct {
    double real;      // 实部
    double imag;      // 虚部
} complex_t;
*/

// 使用C99标准的复数类型
typedef double complex complex_t;

// 向量结构
typedef struct {
    int size;         // 向量维度
    complex_t* data;  // 向量数据
} vector_t;

// 矩阵结构
typedef struct {
    int rows;         // 行数
    int cols;         // 列数
    complex_t* data;  // 矩阵数据
} matrix_t;

// ==== 复数运算函数 ====

// 创建复数
complex_t complex_create(double real, double imag) {
    return real + imag * I;
}

// 复数加法
complex_t complex_add(complex_t a, complex_t b) {
    complex_t result;
    result.real = a.real + b.real;
    result.imag = a.imag + b.imag;
    return result;
}

// 复数减法
complex_t complex_sub(complex_t a, complex_t b) {
    complex_t result;
    result.real = a.real - b.real;
    result.imag = a.imag - b.imag;
    return result;
}

// 复数乘法
complex_t complex_mul(complex_t a, complex_t b) {
    complex_t result;
    result.real = a.real * b.real - a.imag * b.imag;
    result.imag = a.real * b.imag + a.imag * b.real;
    return result;
}

// 复数除法
complex_t complex_div(complex_t a, complex_t b) {
    complex_t result;
    double denominator = b.real * b.real + b.imag * b.imag;
    
    if (denominator < DBL_EPSILON) {
        fprintf(stderr, "错误: 复数除法分母为零或接近零\n");
        result.real = 0.0;
        result.imag = 0.0;
        return result;
    }
    
    result.real = (a.real * b.real + a.imag * b.imag) / denominator;
    result.imag = (a.imag * b.real - a.real * b.imag) / denominator;
    return result;
}

// 复数模
double complex_abs(complex_t z) {
    return sqrt(z.real * z.real + z.imag * z.imag);
}

// 复数共轭
complex_t complex_conj(complex_t a) {
    complex_t result;
    result.real = a.real;
    result.imag = -a.imag;
    return result;
}

// 复数相位
double complex_phase(complex_t a) {
    return atan2(a.imag, a.real);
}

// 欧拉公式：e^(i*theta)
complex_t complex_exp_i(double theta) {
    return cos(theta) + I * sin(theta);
}

// ==== 向量运算函数 ====

// 创建向量
vector_t* vector_create(int size) {
    vector_t* vec = (vector_t*)malloc(sizeof(vector_t));
    if (!vec) return NULL;
    
    vec->size = size;
    vec->data = (complex_t*)malloc(sizeof(complex_t) * size);
    
    if (!vec->data) {
        free(vec);
        return NULL;
    }
    
    // 初始化为零向量
    for (int i = 0; i < size; i++) {
        vec->data[i] = 0.0 + 0.0 * I;
    }
    
    return vec;
}

// 销毁向量
void vector_destroy(vector_t* vec) {
    if (!vec) return;
    
    if (vec->data) {
        free(vec->data);
    }
    
    free(vec);
}

// 向量加法
vector_t* vector_add(vector_t* a, vector_t* b) {
    if (!a || !b || a->size != b->size) return NULL;
    
    vector_t* result = vector_create(a->size);
    if (!result) return NULL;
    
    for (int i = 0; i < a->size; i++) {
        result->data[i] = a->data[i] + b->data[i];
    }
    
    return result;
}

// 向量减法
vector_t* vector_sub(vector_t* a, vector_t* b) {
    if (!a || !b || a->size != b->size) return NULL;
    
    vector_t* result = vector_create(a->size);
    if (!result) return NULL;
    
    for (int i = 0; i < a->size; i++) {
        result->data[i] = a->data[i] - b->data[i];
    }
    
    return result;
}

// 向量数乘
vector_t* vector_scalar_mul(vector_t* vec, complex_t scalar) {
    if (!vec) return NULL;
    
    vector_t* result = vector_create(vec->size);
    if (!result) return NULL;
    
    for (int i = 0; i < vec->size; i++) {
        result->data[i] = vec->data[i] * scalar;
    }
    
    return result;
}

// 向量点积（内积）
complex_t vector_dot_product(vector_t* a, vector_t* b) {
    if (!a || !b || a->size != b->size) return 0.0 + 0.0 * I;
    
    complex_t result = 0.0 + 0.0 * I;
    
    for (int i = 0; i < a->size; i++) {
        result += conj(a->data[i]) * b->data[i];
    }
    
    return result;
}

// 向量范数（模长）
double vector_norm(vector_t* vec) {
    if (!vec) return 0.0;
    
    double sum = 0.0;
    
    for (int i = 0; i < vec->size; i++) {
        sum += cabs(vec->data[i]) * cabs(vec->data[i]);
    }
    
    return sqrt(sum);
}

// 归一化向量
int vector_normalize(vector_t* vec) {
    if (!vec) return 0;
    
    double norm = vector_norm(vec);
    if (norm < 1e-10) return 0; // 避免除以零
    
    for (int i = 0; i < vec->size; i++) {
        vec->data[i] /= norm;
    }
    
    return 1;
}

// 向量外积
matrix_t* vector_outer_product(vector_t* a, vector_t* b) {
    if (!a || !b) return NULL;
    
    matrix_t* result = matrix_create(a->size, b->size);
    if (!result) return NULL;
    
    for (int i = 0; i < a->size; i++) {
        for (int j = 0; j < b->size; j++) {
            result->data[i][j] = a->data[i] * conj(b->data[j]);
        }
    }
    
    return result;
}

// ==== 矩阵运算函数 ====

// 创建矩阵
matrix_t* matrix_create(int rows, int cols) {
    if (rows <= 0 || cols <= 0) {
        fprintf(stderr, "错误: 无效的矩阵维度 (%d, %d)\n", rows, cols);
        return NULL;
    }
    
    matrix_t* mat = (matrix_t*)malloc(sizeof(matrix_t));
    if (!mat) {
        fprintf(stderr, "错误: 无法分配矩阵结构体内存\n");
        return NULL;
    }
    
    mat->rows = rows;
    mat->cols = cols;
    mat->data = (complex_t*)malloc(rows * cols * sizeof(complex_t));
    
    if (!mat->data) {
        fprintf(stderr, "错误: 无法分配矩阵数据内存\n");
        free(mat);
        return NULL;
    }
    
    // 初始化为零矩阵
    for (int i = 0; i < rows * cols; i++) {
        mat->data[i].real = 0.0;
        mat->data[i].imag = 0.0;
    }
    
    return mat;
}

// 销毁矩阵
void matrix_destroy(matrix_t* mat) {
    if (mat) {
        if (mat->data) {
            free(mat->data);
        }
        free(mat);
    }
}

// 创建单位矩阵
matrix_t* matrix_identity(int size) {
    matrix_t* mat = matrix_create(size, size);
    if (!mat) return NULL;
    
    for (int i = 0; i < size; i++) {
        mat->data[i][i] = 1.0 + 0.0 * I;
    }
    
    return mat;
}

// 矩阵加法
matrix_t* matrix_add(matrix_t* a, matrix_t* b) {
    if (!a || !b || a->rows != b->rows || a->cols != b->cols) return NULL;
    
    matrix_t* result = matrix_create(a->rows, a->cols);
    if (!result) return NULL;
    
    for (int i = 0; i < a->rows; i++) {
        for (int j = 0; j < a->cols; j++) {
            result->data[i][j] = a->data[i][j] + b->data[i][j];
        }
    }
    
    return result;
}

// 矩阵减法
matrix_t* matrix_sub(matrix_t* a, matrix_t* b) {
    if (!a || !b || a->rows != b->rows || a->cols != b->cols) return NULL;
    
    matrix_t* result = matrix_create(a->rows, a->cols);
    if (!result) return NULL;
    
    for (int i = 0; i < a->rows; i++) {
        for (int j = 0; j < a->cols; j++) {
            result->data[i][j] = a->data[i][j] - b->data[i][j];
        }
    }
    
    return result;
}

// 矩阵数乘
matrix_t* matrix_scalar_mul(matrix_t* mat, complex_t scalar) {
    if (!mat) return NULL;
    
    matrix_t* result = matrix_create(mat->rows, mat->cols);
    if (!result) return NULL;
    
    for (int i = 0; i < mat->rows; i++) {
        for (int j = 0; j < mat->cols; j++) {
            result->data[i][j] = mat->data[i][j] * scalar;
        }
    }
    
    return result;
}

// 矩阵乘法
matrix_t* matrix_mul(matrix_t* a, matrix_t* b) {
    if (!a || !b || a->cols != b->rows) return NULL;
    
    matrix_t* result = matrix_create(a->rows, b->cols);
    if (!result) return NULL;
    
    for (int i = 0; i < a->rows; i++) {
        for (int j = 0; j < b->cols; j++) {
            complex_t sum = 0.0 + 0.0 * I;
            for (int k = 0; k < a->cols; k++) {
                sum += a->data[i][k] * b->data[k][j];
            }
            result->data[i][j] = sum;
        }
    }
    
    return result;
}

// 矩阵转置
matrix_t* matrix_transpose(matrix_t* mat) {
    if (!mat) return NULL;
    
    matrix_t* result = matrix_create(mat->cols, mat->rows);
    if (!result) return NULL;
    
    for (int i = 0; i < mat->rows; i++) {
        for (int j = 0; j < mat->cols; j++) {
            result->data[j][i] = mat->data[i][j];
        }
    }
    
    return result;
}

// 矩阵共轭
matrix_t* matrix_conjugate(matrix_t* mat) {
    if (!mat) return NULL;
    
    matrix_t* result = matrix_create(mat->rows, mat->cols);
    if (!result) return NULL;
    
    for (int i = 0; i < mat->rows; i++) {
        for (int j = 0; j < mat->cols; j++) {
            result->data[i][j] = conj(mat->data[i][j]);
        }
    }
    
    return result;
}

// 矩阵共轭转置（厄米共轭）
matrix_t* matrix_adjoint(matrix_t* mat) {
    if (!mat) return NULL;
    
    matrix_t* result = matrix_create(mat->cols, mat->rows);
    if (!result) return NULL;
    
    for (int i = 0; i < mat->rows; i++) {
        for (int j = 0; j < mat->cols; j++) {
            result->data[j][i] = conj(mat->data[i][j]);
        }
    }
    
    return result;
}

// 矩阵的迹
complex_t matrix_trace(matrix_t* mat) {
    if (!mat || mat->rows != mat->cols) return 0.0 + 0.0 * I;
    
    complex_t trace = 0.0 + 0.0 * I;
    
    for (int i = 0; i < mat->rows; i++) {
        trace += mat->data[i][i];
    }
    
    return trace;
}

// 检查矩阵是否为厄米矩阵（自伴矩阵）
int matrix_is_hermitian(matrix_t* mat) {
    if (!mat || mat->rows != mat->cols) return 0;
    
    for (int i = 0; i < mat->rows; i++) {
        for (int j = 0; j < i; j++) {
            if (cabs(mat->data[i][j] - conj(mat->data[j][i])) > 1e-10) {
                return 0;
            }
        }
    }
    
    return 1;
}

// 检查矩阵是否为酉矩阵
int matrix_is_unitary(matrix_t* mat) {
    if (!mat || mat->rows != mat->cols) return 0;
    
    // 计算 M * M†
    matrix_t* adj = matrix_adjoint(mat);
    if (!adj) return 0;
    
    matrix_t* product = matrix_mul(mat, adj);
    if (!product) {
        matrix_destroy(adj);
        return 0;
    }
    
    // 检查结果是否接近单位矩阵
    int is_unitary = 1;
    for (int i = 0; i < mat->rows; i++) {
        for (int j = 0; j < mat->rows; j++) {
            complex_t expected = (i == j) ? (1.0 + 0.0 * I) : (0.0 + 0.0 * I);
            if (cabs(product->data[i][j] - expected) > 1e-10) {
                is_unitary = 0;
                break;
            }
        }
        if (!is_unitary) break;
    }
    
    matrix_destroy(adj);
    matrix_destroy(product);
    
    return is_unitary;
}

// ==== 量子计算相关函数 ====

// 计算态矢量的纠缠熵
double calc_entanglement_entropy(vector_t* state, int subsystem_qubits, int total_qubits) {
    if (!state || subsystem_qubits <= 0 || subsystem_qubits >= total_qubits) return 0.0;
    
    // 计算约化密度矩阵尺寸
    int dim_a = 1 << subsystem_qubits;
    int dim_b = 1 << (total_qubits - subsystem_qubits);
    
    // 创建约化密度矩阵
    matrix_t* rho_a = matrix_create(dim_a, dim_a);
    if (!rho_a) return 0.0;
    
    // 通过部分迹计算约化密度矩阵
    for (int i = 0; i < dim_a; i++) {
        for (int j = 0; j < dim_a; j++) {
            rho_a->data[i][j] = 0.0 + 0.0 * I;
            
            for (int k = 0; k < dim_b; k++) {
                int idx_i = i * dim_b + k;
                int idx_j = j * dim_b + k;
                rho_a->data[i][j] += state->data[idx_i] * conj(state->data[idx_j]);
            }
        }
    }
    
    // 计算矩阵的特征值
    // 注意：这里需要完整的特征值求解算法，为简化我们假设rho_a是对角矩阵
    double entropy = 0.0;
    for (int i = 0; i < dim_a; i++) {
        double p = cabs(rho_a->data[i][i]);
        if (p > 1e-10) {
            entropy -= p * log2(p);
        }
    }
    
    matrix_destroy(rho_a);
    return entropy;
}

// 计算量子态的相位
double* calc_quantum_phases(vector_t* state) {
    if (!state) return NULL;
    
    double* phases = (double*)malloc(sizeof(double) * state->size);
    if (!phases) return NULL;
    
    for (int i = 0; i < state->size; i++) {
        phases[i] = carg(state->data[i]);
    }
    
    return phases;
}

// 计算量子态的概率分布
double* calc_quantum_probabilities(vector_t* state) {
    if (!state) return NULL;
    
    double* probs = (double*)malloc(sizeof(double) * state->size);
    if (!probs) return NULL;
    
    for (int i = 0; i < state->size; i++) {
        probs[i] = cabs(state->data[i]) * cabs(state->data[i]);
    }
    
    return probs;
}

// 计算两个量子态的内积
complex_t calc_quantum_inner_product(vector_t* state1, vector_t* state2) {
    return vector_dot_product(state1, state2);
}

// 计算两个量子态的保真度
double calc_quantum_fidelity(vector_t* state1, vector_t* state2) {
    complex_t inner = calc_quantum_inner_product(state1, state2);
    return cabs(inner) * cabs(inner);
}

// 计算量子态的冯诺依曼熵
double calc_state_entropy(vector_t* state) {
    if (!state) return 0.0;
    
    double entropy = 0.0;
    double* probs = calc_quantum_probabilities(state);
    
    if (!probs) return 0.0;
    
    for (int i = 0; i < state->size; i++) {
        if (probs[i] > 1e-10) {
            entropy -= probs[i] * log2(probs[i]);
        }
    }
    
    free(probs);
    return entropy;
}

// 计算量子态的演化速率
double calc_state_flux(int num_states, ...) {
    if (num_states <= 0) return 0.0;
    
    va_list args;
    va_start(args, num_states);
    
    double total_flux = 0.0;
    quantum_state_t* prev_state = va_arg(args, quantum_state_t*);
    
    for (int i = 1; i < num_states; i++) {
        quantum_state_t* curr_state = va_arg(args, quantum_state_t*);
        
        // 简化版：计算两个状态之间的差异作为通量度量
        // 在实际实现中，应该基于量子态之间的距离度量
        double state_diff = quantum_state_distance(prev_state, curr_state);
        total_flux += state_diff;
        
        prev_state = curr_state;
    }
    
    va_end(args);
    return total_flux / (num_states - 1);
}

// ==== 辅助函数 ====

// 打印复数
void complex_print(complex_t c) {
    if (cimag(c) >= 0) {
        printf("%.4f+%.4fi", creal(c), cimag(c));
    } else {
        printf("%.4f%.4fi", creal(c), cimag(c));
    }
}

// 打印向量
void vector_print(vector_t* vec) {
    if (!vec) {
        printf("NULL vector\n");
        return;
    }
    
    printf("Vector(%d): [", vec->size);
    for (int i = 0; i < vec->size; i++) {
        complex_print(vec->data[i]);
        if (i < vec->size - 1) {
            printf(", ");
        }
    }
    printf("]\n");
}

// 打印矩阵
void matrix_print(matrix_t* mat) {
    if (!mat) {
        printf("NULL matrix\n");
        return;
    }
    
    printf("Matrix(%d×%d):\n", mat->rows, mat->cols);
    for (int i = 0; i < mat->rows; i++) {
        printf("  [");
        for (int j = 0; j < mat->cols; j++) {
            complex_print(mat->data[i][j]);
            if (j < mat->cols - 1) {
                printf(", ");
            }
        }
        printf("]\n");
    }
}

// 从量子态创建向量
vector_t* vector_from_quantum_state(quantum_state_t* state) {
    if (!state) return NULL;
    
    int dim = 1 << quantum_state_get_num_qubits(state);
    vector_t* vec = vector_create(dim);
    if (!vec) return NULL;
    
    // 复制量子态的振幅到向量
    complex_t* amplitudes = quantum_state_get_amplitudes(state);
    if (!amplitudes) {
        vector_destroy(vec);
        return NULL;
    }
    
    for (int i = 0; i < dim; i++) {
        vec->data[i] = amplitudes[i];
    }
    
    return vec;
}

// 将向量转换为量子态
quantum_state_t* quantum_state_from_vector(vector_t* vec) {
    if (!vec) return NULL;
    
    // 检查向量尺寸是否是2的幂
    int num_qubits = 0;
    int size = vec->size;
    while (size > 1) {
        if (size % 2 != 0) return NULL; // 不是2的幂
        size /= 2;
        num_qubits++;
    }
    
    quantum_state_t* state = quantum_state_create(num_qubits);
    if (!state) return NULL;
    
    // 复制向量振幅到量子态
    for (int i = 0; i < vec->size; i++) {
        quantum_state_set_amplitude(state, i, vec->data[i]);
    }
    
    return state;
}

// 量子傅里叶变换实现
matrix_t* quantum_fourier_transform(int num_qubits) {
    int dimension = 1 << num_qubits;
    matrix_t* qft = matrix_create(dimension, dimension);
    if (!qft) return NULL;
    
    double normalization = 1.0 / sqrt(dimension);
    
    for (int i = 0; i < dimension; i++) {
        for (int j = 0; j < dimension; j++) {
            double angle = 2.0 * M_PI * i * j / dimension;
            complex_t val = {
                normalization * cos(angle),
                normalization * sin(angle)
            };
            matrix_set(qft, i, j, val);
        }
    }
    
    return qft;
}

// 统计函数
double calculate_entropy(const matrix_t* state_vector) {
    if (!state_vector || state_vector->cols != 1) {
        fprintf(stderr, "错误：熵计算的输入无效\n");
        return -1.0;
    }
    
    double entropy = 0.0;
    
    for (int i = 0; i < state_vector->rows; i++) {
        complex_t amplitude = matrix_get(state_vector, i, 0);
        double prob = amplitude.real * amplitude.real + amplitude.imag * amplitude.imag;
        
        if (prob > 1e-10) {  // 避免对0取对数
            entropy -= prob * log2(prob);
        }
    }
    
    return entropy;
}

double calculate_fidelity(const matrix_t* state1, const matrix_t* state2) {
    if (!state1 || !state2 || 
        state1->rows != state2->rows || 
        state1->cols != 1 || state2->cols != 1) {
        fprintf(stderr, "错误：保真度计算的输入无效\n");
        return -1.0;
    }
    
    complex_t inner_product = {0.0, 0.0};
    
    for (int i = 0; i < state1->rows; i++) {
        complex_t amp1 = matrix_get(state1, i, 0);
        complex_t amp2 = matrix_get(state2, i, 0);
        complex_t conj_amp1 = complex_conj(amp1);
        
        inner_product = complex_add(inner_product, complex_mul(conj_amp1, amp2));
    }
    
    double abs_inner_product = complex_abs(inner_product);
    return abs_inner_product * abs_inner_product;
} 