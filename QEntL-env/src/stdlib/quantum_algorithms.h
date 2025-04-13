/**
 * 量子算法库头文件
 * 
 * 提供QEntL中常用量子算法的声明，包括量子傅里叶变换、
 * Grover搜索算法、量子相位估计等。
 */

#ifndef QUANTUM_ALGORITHMS_H
#define QUANTUM_ALGORITHMS_H

#include "../quantum_state.h"
#include <complex.h>

/* -------------------- 函数类型定义 -------------------- */

// Oracle函数类型，用于Grover算法和其他量子算法
typedef void (*OracleFunction)(QuantumRegister* reg, void* params);

// 受控酉变换函数类型，用于量子相位估计
typedef void (*ControlledUnitaryFunction)(QuantumRegister* reg, int control, 
                                       int target_start, int target_end, 
                                       void* params);

// Oracle参数结构，用于量子计数算法
typedef struct {
    int (*is_marked)(int state, void* context);  // 判断状态是否被标记的函数
    void* context;                              // 传递给回调函数的上下文
} OracleParams;

/* -------------------- 量子傅里叶变换函数 -------------------- */

/**
 * 对量子寄存器应用量子傅里叶变换
 * 
 * @param reg 量子寄存器
 * @param start_qubit 起始比特索引
 * @param end_qubit 结束比特索引
 */
void quantum_fourier_transform(QuantumRegister* reg, int start_qubit, int end_qubit);

/**
 * 对量子寄存器应用逆量子傅里叶变换
 * 
 * @param reg 量子寄存器
 * @param start_qubit 起始比特索引
 * @param end_qubit 结束比特索引
 */
void inverse_quantum_fourier_transform(QuantumRegister* reg, int start_qubit, int end_qubit);

/**
 * 对量子寄存器应用受控相位旋转门
 * 
 * @param reg 量子寄存器
 * @param control_qubit 控制比特索引
 * @param target_qubit 目标比特索引
 * @param angle 旋转角度（弧度）
 */
void controlled_phase_rotation(QuantumRegister* reg, int control_qubit, int target_qubit, double angle);

/* -------------------- Grover搜索算法函数 -------------------- */

/**
 * 对量子寄存器应用Grover扩散算子
 * 
 * @param reg 量子寄存器
 * @param start_qubit 起始比特索引
 * @param end_qubit 结束比特索引
 */
void apply_grover_diffusion(QuantumRegister* reg, int start_qubit, int end_qubit);

/**
 * 应用Oracle函数
 * 
 * @param reg 量子寄存器
 * @param oracle Oracle函数
 * @param params Oracle函数参数
 */
void apply_oracle(QuantumRegister* reg, OracleFunction oracle, void* params);

/**
 * 执行Grover搜索算法
 * 
 * @param reg 量子寄存器
 * @param start_qubit 起始比特索引
 * @param end_qubit 结束比特索引
 * @param oracle Oracle函数
 * @param oracle_params Oracle函数参数
 * @param result 搜索结果的指针
 * @return 搜索是否成功
 */
int grover_search(QuantumRegister* reg, int start_qubit, int end_qubit, 
                OracleFunction oracle, void* oracle_params, int* result);

/* -------------------- 量子相位估计函数 -------------------- */

/**
 * 执行量子相位估计算法
 * 
 * @param reg 量子寄存器
 * @param precision_qubits 精度量子比特数
 * @param target_start_qubit 目标起始比特索引
 * @param target_size 目标比特数量
 * @param unitary 酉变换函数
 * @param params 酉变换函数参数
 * @param estimated_phase 估计相位的指针
 */
void quantum_phase_estimation(QuantumRegister* reg, int precision_qubits, 
                           int target_start_qubit, int target_size,
                           ControlledUnitaryFunction unitary, void* params,
                           double* estimated_phase);

/* -------------------- 量子傅里叶采样函数 -------------------- */

/**
 * 执行量子傅里叶采样
 * 
 * @param reg 量子寄存器
 * @param start_qubit 起始比特索引
 * @param end_qubit 结束比特索引
 * @param samples 采样次数
 * @param frequencies 频率数组
 * @param frequencies_size 频率数组大小
 */
void quantum_fourier_sampling(QuantumRegister* reg, int start_qubit, int end_qubit, 
                           int samples, int* frequencies, int frequencies_size);

/* -------------------- Shor算法相关函数 -------------------- */

/**
 * 计算模幂运算: (base^exponent) % modulus
 * 
 * @param base 底数
 * @param exponent 指数
 * @param modulus 模数
 * @return 模幂结果
 */
int mod_exp(int base, int exponent, int modulus);

/**
 * 执行量子模幂运算
 * 
 * @param reg 量子寄存器
 * @param control_qubit 控制比特索引
 * @param target_start 目标起始比特索引
 * @param target_end 目标结束比特索引
 * @param base 底数
 * @param modulus 模数
 */
void quantum_modular_exponentiation(QuantumRegister* reg, int control_qubit, 
                                 int target_start, int target_end, 
                                 int base, int modulus);

/**
 * 计算最大公约数
 * 
 * @param a 第一个数
 * @param b 第二个数
 * @return 最大公约数
 */
int gcd(int a, int b);

/**
 * 使用连分数展开找到有理逼近
 * 
 * @param x 需要逼近的实数
 * @param max_denominator 最大分母
 * @param numerator 分子指针
 * @param denominator 分母指针
 */
void continued_fraction_expansion(double x, int max_denominator, int* numerator, int* denominator);

/**
 * 执行Shor算法分解大整数
 * 
 * @param N 需要分解的数
 * @param factor1 第一个因子的指针
 * @param factor2 第二个因子的指针
 * @return 是否成功分解
 */
int shor_algorithm(int N, int* factor1, int* factor2);

/* -------------------- 量子隐函数变换函数 -------------------- */

/**
 * 执行量子隐函数变换算法
 * 
 * @param reg 量子寄存器
 * @param start_qubit 起始比特索引
 * @param end_qubit 结束比特索引
 * @param oracle_f 函数f的Oracle
 * @param oracle_g 函数g的Oracle
 * @param params Oracle参数
 * @param shift 位移结果的指针
 */
void quantum_hidden_shift(QuantumRegister* reg, int start_qubit, int end_qubit, 
                       OracleFunction oracle_f, OracleFunction oracle_g, 
                       void* params, int* shift);

/* -------------------- 量子计数算法函数 -------------------- */

/**
 * 执行量子计数算法
 * 
 * @param reg 量子寄存器
 * @param counting_qubits 计数比特数量
 * @param search_start 搜索起始比特索引
 * @param search_end 搜索结束比特索引
 * @param oracle Oracle函数
 * @param oracle_params Oracle参数
 * @return 被标记状态的估计比例
 */
double quantum_counting(QuantumRegister* reg, int counting_qubits, int search_start, int search_end, 
                     OracleFunction oracle, void* oracle_params);

#endif /* QUANTUM_ALGORITHMS_H */ 