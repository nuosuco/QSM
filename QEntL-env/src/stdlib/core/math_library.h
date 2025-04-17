/**
 * @file math_library.h
 * @brief QEntL核心数学库头文件
 * @author AI助手
 * @version 1.0
 * @date 2023-10-30
 */

#ifndef QENTL_MATH_LIBRARY_H
#define QENTL_MATH_LIBRARY_H

#include <stdlib.h>
#include <math.h>

/**
 * 复数结构体
 */
typedef struct {
    double real;  // 实部
    double imag;  // 虚部
} complex_t;

/**
 * 矩阵结构体
 */
typedef struct {
    int rows;         // 行数
    int cols;         // 列数
    complex_t* data;  // 矩阵数据
} matrix_t;

// 复数运算函数
complex_t complex_add(complex_t a, complex_t b);
complex_t complex_sub(complex_t a, complex_t b);
complex_t complex_mul(complex_t a, complex_t b);
complex_t complex_div(complex_t a, complex_t b);
complex_t complex_conjugate(complex_t z);
double complex_abs(complex_t z);
double complex_arg(complex_t z);
complex_t complex_from_polar(double r, double theta);

// 矩阵操作函数
matrix_t* matrix_create(int rows, int cols);
void matrix_destroy(matrix_t* mat);
matrix_t* matrix_copy(const matrix_t* src);
complex_t matrix_get(const matrix_t* mat, int row, int col);
void matrix_set(matrix_t* mat, int row, int col, complex_t value);
matrix_t* matrix_add(const matrix_t* a, const matrix_t* b);
matrix_t* matrix_subtract(const matrix_t* a, const matrix_t* b);
matrix_t* matrix_multiply(const matrix_t* a, const matrix_t* b);
matrix_t* matrix_tensor_product(const matrix_t* a, const matrix_t* b);
matrix_t* matrix_transpose(const matrix_t* mat);
matrix_t* matrix_conjugate_transpose(const matrix_t* mat);

// 量子计算专用函数
matrix_t* create_identity_matrix(int size);
matrix_t* create_pauli_x();
matrix_t* create_pauli_y();
matrix_t* create_pauli_z();
matrix_t* create_hadamard();
matrix_t* create_rotation_x(double theta);
matrix_t* create_rotation_y(double theta);
matrix_t* create_rotation_z(double theta);

// 量子位操作函数
matrix_t* apply_gate_to_qubit(const matrix_t* state_vector, const matrix_t* gate, int target_qubit, int num_qubits);
matrix_t* apply_controlled_gate(const matrix_t* state_vector, const matrix_t* gate, int control_qubit, int target_qubit, int num_qubits);
int measure_qubit(matrix_t** state_vector, int qubit_index, int num_qubits);

// 量子傅里叶变换
matrix_t* quantum_fourier_transform(int num_qubits);

// 统计函数
double calculate_entropy(const matrix_t* state_vector);
double calculate_fidelity(const matrix_t* state1, const matrix_t* state2);

#endif /* QENTL_MATH_LIBRARY_H */ 