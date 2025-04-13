/**
 * 量子算法库实现
 * 
 * 实现了QEntL中常用量子算法，如量子傅里叶变换、
 * Grover搜索算法、量子相位估计等。
 */

#include "quantum_algorithms.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* -------------------- 量子傅里叶变换实现 -------------------- */

void quantum_fourier_transform(QuantumRegister* reg, int start_qubit, int end_qubit) {
    if (!reg || !reg->amplitudes || start_qubit < 0 || end_qubit >= reg->num_qubits || start_qubit > end_qubit) {
        return;
    }
    
    int num_qubits = end_qubit - start_qubit + 1;
    
    // 反转比特顺序以匹配标准QFT定义
    for (int i = 0; i < num_qubits / 2; i++) {
        apply_swap(reg, start_qubit + i, end_qubit - i);
    }
    
    // 应用H门和受控旋转门
    for (int i = end_qubit; i >= start_qubit; i--) {
        // 对每个量子比特应用Hadamard门
        apply_hadamard_to_qubit(reg, i);
        
        // 应用受控旋转门
        for (int j = i - 1; j >= start_qubit; j--) {
            // 计算相位角度
            double angle = M_PI / pow(2.0, i - j);
            
            // 应用受控旋转门
            // 注意：这里使用自定义函数实现受控旋转，因为它不是标准的门
            controlled_phase_rotation(reg, j, i, angle);
        }
    }
}

void inverse_quantum_fourier_transform(QuantumRegister* reg, int start_qubit, int end_qubit) {
    if (!reg || !reg->amplitudes || start_qubit < 0 || end_qubit >= reg->num_qubits || start_qubit > end_qubit) {
        return;
    }
    
    int num_qubits = end_qubit - start_qubit + 1;
    
    // 应用逆H门和受控旋转门
    for (int i = start_qubit; i <= end_qubit; i++) {
        // 应用负相位的受控旋转门
        for (int j = start_qubit; j < i; j++) {
            // 计算相位角度
            double angle = -M_PI / pow(2.0, i - j);
            
            // 应用受控旋转门
            controlled_phase_rotation(reg, j, i, angle);
        }
        
        // 对每个量子比特应用Hadamard门
        apply_hadamard_to_qubit(reg, i);
    }
    
    // 反转比特顺序以匹配标准IQFT定义
    for (int i = 0; i < num_qubits / 2; i++) {
        apply_swap(reg, start_qubit + i, end_qubit - i);
    }
}

void controlled_phase_rotation(QuantumRegister* reg, int control_qubit, int target_qubit, double angle) {
    if (!reg || !reg->amplitudes || 
        control_qubit < 0 || control_qubit >= reg->num_qubits ||
        target_qubit < 0 || target_qubit >= reg->num_qubits ||
        control_qubit == target_qubit) {
        return;
    }
    
    int control_mask = 1 << control_qubit;
    int target_mask = 1 << target_qubit;
    
    // 应用相位旋转
    double complex phase = cos(angle) + sin(angle) * I;
    
    for (int i = 0; i < reg->size; i++) {
        // 只有在控制量子比特为1且目标量子比特为1时才应用相位
        if ((i & control_mask) && (i & target_mask)) {
            reg->amplitudes[i] *= phase;
        }
    }
}

/* -------------------- Grover搜索算法实现 -------------------- */

// 应用Grover扩散算子
void apply_grover_diffusion(QuantumRegister* reg, int start_qubit, int end_qubit) {
    if (!reg || !reg->amplitudes || start_qubit < 0 || end_qubit >= reg->num_qubits || start_qubit > end_qubit) {
        return;
    }
    
    int num_qubits = end_qubit - start_qubit + 1;
    
    // 对所有比特应用H门
    for (int i = start_qubit; i <= end_qubit; i++) {
        apply_hadamard_to_qubit(reg, i);
    }
    
    // 应用条件相位翻转（对除|0⟩以外的所有状态反转相位）
    // 首先对所有量子比特应用X门
    for (int i = start_qubit; i <= end_qubit; i++) {
        apply_pauli_x_to_qubit(reg, i);
    }
    
    // 应用多控制Z门，即相当于在|11...1⟩状态上添加负相位
    // 对于多量子比特，需要使用辅助比特，但这里简化实现
    if (num_qubits == 1) {
        // 单比特情况，直接应用Z门
        apply_pauli_z_to_qubit(reg, start_qubit);
    } else if (num_qubits == 2) {
        // 两比特情况，使用CZ门
        apply_controlled_z(reg, start_qubit, start_qubit + 1);
    } else {
        // 多比特情况，使用相位旋转
        int all_ones_state = (1 << num_qubits) - 1;
        all_ones_state <<= start_qubit;
        
        for (int i = 0; i < reg->size; i++) {
            int relevant_bits = i & ((1 << (end_qubit + 1)) - (1 << start_qubit));
            if (relevant_bits == all_ones_state) {
                reg->amplitudes[i] = -reg->amplitudes[i];
            }
        }
    }
    
    // 再次对所有量子比特应用X门
    for (int i = start_qubit; i <= end_qubit; i++) {
        apply_pauli_x_to_qubit(reg, i);
    }
    
    // 最后再次对所有比特应用H门
    for (int i = start_qubit; i <= end_qubit; i++) {
        apply_hadamard_to_qubit(reg, i);
    }
}

// 应用Oracle函数
void apply_oracle(QuantumRegister* reg, OracleFunction oracle, void* params) {
    if (!reg || !reg->amplitudes || !oracle) {
        return;
    }
    
    // 调用提供的oracle函数
    oracle(reg, params);
}

// Grover搜索算法实现
int grover_search(QuantumRegister* reg, int start_qubit, int end_qubit, 
                OracleFunction oracle, void* oracle_params, int* result) {
    if (!reg || !reg->amplitudes || !oracle || !result || 
        start_qubit < 0 || end_qubit >= reg->num_qubits || start_qubit > end_qubit) {
        return 0;
    }
    
    int num_qubits = end_qubit - start_qubit + 1;
    int n = 1 << num_qubits; // 搜索空间大小
    
    // 初始化：将所有量子比特置于叠加态
    reset_quantum_register(reg);
    for (int i = start_qubit; i <= end_qubit; i++) {
        apply_hadamard_to_qubit(reg, i);
    }
    
    // 计算最优迭代次数：π/4 * sqrt(n)
    int iterations = (int)(M_PI / 4.0 * sqrt(n));
    
    // Grover迭代
    for (int i = 0; i < iterations; i++) {
        // 应用oracle函数
        apply_oracle(reg, oracle, oracle_params);
        
        // 应用Grover扩散算子
        apply_grover_diffusion(reg, start_qubit, end_qubit);
    }
    
    // 测量结果
    *result = 0;
    for (int i = start_qubit; i <= end_qubit; i++) {
        MeasurementResult m = measure_qubit_in_register(reg, i);
        if (m.result == 1) {
            *result |= (1 << (i - start_qubit));
        }
    }
    
    return 1;
}

/* -------------------- 量子相位估计实现 -------------------- */

void quantum_phase_estimation(QuantumRegister* reg, int precision_qubits, 
                           int target_start_qubit, int target_size,
                           ControlledUnitaryFunction unitary, void* params,
                           double* estimated_phase) {
    if (!reg || !reg->amplitudes || !unitary || !estimated_phase ||
        precision_qubits <= 0 || precision_qubits + target_start_qubit + target_size > reg->num_qubits) {
        return;
    }
    
    int precision_start = 0;
    int precision_end = precision_qubits - 1;
    int target_end = target_start_qubit + target_size - 1;
    
    // 初始化相位寄存器为叠加态
    for (int i = precision_start; i <= precision_end; i++) {
        apply_hadamard_to_qubit(reg, i);
    }
    
    // 应用受控酉变换
    for (int i = 0; i <= precision_end; i++) {
        int power = 1 << (precision_end - i);
        
        // 应用U^(2^j)
        for (int j = 0; j < power; j++) {
            unitary(reg, i, target_start_qubit, target_end, params);
        }
    }
    
    // 应用逆量子傅里叶变换到精度寄存器
    inverse_quantum_fourier_transform(reg, precision_start, precision_end);
    
    // 测量精度寄存器
    int phase_int = 0;
    for (int i = precision_start; i <= precision_end; i++) {
        MeasurementResult m = measure_qubit_in_register(reg, i);
        if (m.result == 1) {
            phase_int |= (1 << (i - precision_start));
        }
    }
    
    // 计算估计的相位
    *estimated_phase = (double)phase_int / (1 << precision_qubits);
}

/* -------------------- 量子傅里叶采样实现 -------------------- */

void quantum_fourier_sampling(QuantumRegister* reg, int start_qubit, int end_qubit, 
                           int samples, int* frequencies, int frequencies_size) {
    if (!reg || !reg->amplitudes || !frequencies || 
        start_qubit < 0 || end_qubit >= reg->num_qubits || start_qubit > end_qubit ||
        frequencies_size < (1 << (end_qubit - start_qubit + 1))) {
        return;
    }
    
    int num_qubits = end_qubit - start_qubit + 1;
    int states = 1 << num_qubits;
    
    // 清零频率数组
    memset(frequencies, 0, sizeof(int) * frequencies_size);
    
    // 应用量子傅里叶变换
    quantum_fourier_transform(reg, start_qubit, end_qubit);
    
    // 多次采样
    for (int s = 0; s < samples; s++) {
        // 创建量子寄存器的副本
        QuantumRegister* tmp_reg = create_quantum_register(reg->num_qubits);
        if (!tmp_reg) {
            continue;
        }
        
        // 复制量子态
        memcpy(tmp_reg->amplitudes, reg->amplitudes, sizeof(double complex) * reg->size);
        
        // 测量指定的量子比特
        int result = 0;
        for (int i = start_qubit; i <= end_qubit; i++) {
            MeasurementResult m = measure_qubit_in_register(tmp_reg, i);
            if (m.result == 1) {
                result |= (1 << (i - start_qubit));
            }
        }
        
        // 更新频率
        if (result < frequencies_size) {
            frequencies[result]++;
        }
        
        // 释放临时寄存器
        free_quantum_register(tmp_reg);
    }
}

/* -------------------- Shor算法相关实现 -------------------- */

// 模幂运算
int mod_exp(int base, int exponent, int modulus) {
    if (modulus == 1) return 0;
    
    long result = 1;
    long b = base % modulus;
    
    while (exponent > 0) {
        if (exponent % 2 == 1) {
            result = (result * b) % modulus;
        }
        exponent = exponent >> 1;
        b = (b * b) % modulus;
    }
    
    return (int)result;
}

// 对Shor算法的量子部分进行模拟
// 实现简化版本的量子模幂
void quantum_modular_exponentiation(QuantumRegister* reg, int control_qubit, 
                                 int target_start, int target_end, 
                                 int base, int modulus) {
    if (!reg || !reg->amplitudes || 
        control_qubit < 0 || control_qubit >= reg->num_qubits ||
        target_start < 0 || target_end >= reg->num_qubits ||
        target_start > target_end) {
        return;
    }
    
    int control_mask = 1 << control_qubit;
    int target_size = target_end - target_start + 1;
    int target_states = 1 << target_size;
    
    // 遍历所有可能的计算基态
    for (int i = 0; i < reg->size; i++) {
        // 只处理控制比特为1的情况
        if (i & control_mask) {
            // 提取目标寄存器状态
            int target_value = (i >> target_start) & (target_states - 1);
            
            // 计算模幂
            int result = mod_exp(base, 1 << control_qubit, modulus);
            
            // 计算新的目标寄存器状态
            int new_target = (target_value * result) % modulus;
            
            // 如果新状态与旧状态不同，则交换振幅
            if (new_target != target_value && new_target < target_states) {
                // 计算新状态的索引
                int target_mask = ((target_states - 1) << target_start);
                int new_i = (i & ~target_mask) | (new_target << target_start);
                
                // 交换振幅
                double complex temp = reg->amplitudes[i];
                reg->amplitudes[i] = reg->amplitudes[new_i];
                reg->amplitudes[new_i] = temp;
            }
        }
    }
}

// 使用辗转相除法计算最大公约数
int gcd(int a, int b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}

// 使用连分数展开找到有理逼近
void continued_fraction_expansion(double x, int max_denominator, int* numerator, int* denominator) {
    if (!numerator || !denominator) return;
    
    // 初始化分母序列
    int d0 = 1, d1 = 0;
    // 初始化分子序列
    int n0 = 0, n1 = 1;
    // 初始化商和余数
    double a = x;
    int a_int;
    
    while (d1 <= max_denominator) {
        a_int = (int)a;
        
        // 更新分子
        int n2 = a_int * n1 + n0;
        n0 = n1;
        n1 = n2;
        
        // 更新分母
        int d2 = a_int * d1 + d0;
        d0 = d1;
        d1 = d2;
        
        // 判断是否找到足够精确的逼近
        double approx = (double)n1 / d1;
        if (fabs(approx - x) < 1.0 / (2.0 * d1 * d1)) {
            *numerator = n1;
            *denominator = d1;
            return;
        }
        
        // 计算下一个余数
        double f = a - a_int;
        if (f < 1e-10) break;
        a = 1.0 / f;
    }
    
    *numerator = n1;
    *denominator = d1;
}

int shor_algorithm(int N, int* factor1, int* factor2) {
    if (!factor1 || !factor2 || N <= 1) {
        return 0;
    }
    
    // 检查N是否为偶数
    if (N % 2 == 0) {
        *factor1 = 2;
        *factor2 = N / 2;
        return 1;
    }
    
    // 尝试使用简单算法找出因子
    for (int i = 3; i * i <= N; i += 2) {
        if (N % i == 0) {
            *factor1 = i;
            *factor2 = N / i;
            return 1;
        }
    }
    
    // Shor算法部分
    // 随机选择一个整数a，使得1 < a < N
    int a;
    int attempts = 0;
    const int MAX_ATTEMPTS = 10;
    
    while (attempts < MAX_ATTEMPTS) {
        // 选择随机数a
        a = 2 + rand() % (N - 2);
        
        // 计算a与N的最大公约数
        int g = gcd(a, N);
        
        // 如果g > 1，则g是N的一个因子
        if (g > 1) {
            *factor1 = g;
            *factor2 = N / g;
            return 1;
        }
        
        // 否则，需要找到a^r ≡ 1 (mod N)的r
        // 这实际上需要量子计算来有效实现
        // 在这里模拟量子部分的结果
        
        // 所需的比特数量
        int n = (int)ceil(log2(N));
        int precision_qubits = 2 * n + 3;
        
        // 创建量子寄存器，这里只是概念演示
        QuantumRegister* reg = create_quantum_register(precision_qubits + n);
        if (!reg) {
            attempts++;
            continue;
        }
        
        // 应用量子相位估计
        double phase;
        void* params = malloc(sizeof(int) * 2);
        if (!params) {
            free_quantum_register(reg);
            attempts++;
            continue;
        }
        
        int* p = (int*)params;
        p[0] = a;
        p[1] = N;
        
        // 量子相位估计，使用量子模幂作为酉算子
        // 这部分在真实量子计算机上执行
        quantum_phase_estimation(reg, precision_qubits, precision_qubits, n, 
                              (ControlledUnitaryFunction)quantum_modular_exponentiation, params, &phase);
        
        free(params);
        free_quantum_register(reg);
        
        // 从相位中提取周期
        if (phase < 1e-10) {
            attempts++;
            continue;
        }
        
        // 将相位转换为分数形式
        int numerator, denominator;
        continued_fraction_expansion(phase, N, &numerator, &denominator);
        
        // 检查是否找到有效周期
        if (denominator % 2 == 0) {
            int r = denominator;
            int x = mod_exp(a, r / 2, N);
            
            if ((x + 1) % N != 0) {
                int factor = gcd(x + 1, N);
                if (factor > 1 && factor < N) {
                    *factor1 = factor;
                    *factor2 = N / factor;
                    return 1;
                }
                
                factor = gcd(x - 1, N);
                if (factor > 1 && factor < N) {
                    *factor1 = factor;
                    *factor2 = N / factor;
                    return 1;
                }
            }
        }
        
        attempts++;
    }
    
    // 如果找不到因子，返回失败
    return 0;
}

/* -------------------- 量子隐函数变换实现 -------------------- */

void quantum_hidden_shift(QuantumRegister* reg, int start_qubit, int end_qubit, 
                       OracleFunction oracle_f, OracleFunction oracle_g, 
                       void* params, int* shift) {
    if (!reg || !reg->amplitudes || !oracle_f || !oracle_g || !shift ||
        start_qubit < 0 || end_qubit >= reg->num_qubits || start_qubit > end_qubit) {
        return;
    }
    
    int num_qubits = end_qubit - start_qubit + 1;
    
    // 初始化：将所有量子比特置于|0⟩态
    reset_quantum_register(reg);
    
    // 应用Hadamard门
    for (int i = start_qubit; i <= end_qubit; i++) {
        apply_hadamard_to_qubit(reg, i);
    }
    
    // 应用g的Oracle
    apply_oracle(reg, oracle_g, params);
    
    // 再次应用Hadamard门
    for (int i = start_qubit; i <= end_qubit; i++) {
        apply_hadamard_to_qubit(reg, i);
    }
    
    // 应用f的Oracle
    apply_oracle(reg, oracle_f, params);
    
    // 最后应用Hadamard门
    for (int i = start_qubit; i <= end_qubit; i++) {
        apply_hadamard_to_qubit(reg, i);
    }
    
    // 测量结果，得到位移s
    *shift = 0;
    for (int i = start_qubit; i <= end_qubit; i++) {
        MeasurementResult m = measure_qubit_in_register(reg, i);
        if (m.result == 1) {
            *shift |= (1 << (i - start_qubit));
        }
    }
}

/* -------------------- 量子计数算法实现 -------------------- */

double quantum_counting(QuantumRegister* reg, int counting_qubits, int search_start, int search_end, 
                     OracleFunction oracle, void* oracle_params) {
    if (!reg || !reg->amplitudes || !oracle || 
        counting_qubits <= 0 || counting_qubits >= reg->num_qubits ||
        search_start < 0 || search_end >= reg->num_qubits || search_start > search_end) {
        return -1.0;
    }
    
    int search_qubits = search_end - search_start + 1;
    int counting_start = 0;
    int counting_end = counting_qubits - 1;
    int search_space_size = 1 << search_qubits;
    
    // 初始化量子寄存器
    reset_quantum_register(reg);
    
    // 在计数寄存器上应用Hadamard门
    for (int i = counting_start; i <= counting_end; i++) {
        apply_hadamard_to_qubit(reg, i);
    }
    
    // 在搜索寄存器上应用Hadamard门
    for (int i = search_start; i <= search_end; i++) {
        apply_hadamard_to_qubit(reg, i);
    }
    
    // 应用受控Grover迭代
    for (int i = 0; i < counting_qubits; i++) {
        int power = 1 << i;
        
        // 为控制量子比特i执行power次Grover迭代
        for (int j = 0; j < power; j++) {
            // 使控制比特i作为条件
            int control_mask = 1 << i;
            
            // 仅当控制比特为1时，应用Oracle和扩散算子
            // 应用Oracle
            for (int state = 0; state < reg->size; state++) {
                if (state & control_mask) {
                    // 创建一个临时寄存器仅包含搜索比特
                    int search_state = (state >> search_start) & ((1 << search_qubits) - 1);
                    double phase = 1.0;
                    
                    // 调用Oracle决定相位
                    void* temp_params = malloc(sizeof(int) * 2);
                    if (temp_params) {
                        int* p = (int*)temp_params;
                        p[0] = search_state;
                        p[1] = search_qubits;
                        
                        // 模拟Oracle将标记状态的相位反转
                        OracleParams* op = (OracleParams*)oracle_params;
                        if (op && op->is_marked && op->is_marked(search_state, op->context)) {
                            phase = -1.0;
                        }
                        
                        free(temp_params);
                    }
                    
                    // 应用相位
                    reg->amplitudes[state] *= phase;
                }
            }
            
            // 受控扩散算子（同样仅当控制比特为1时应用）
            for (int state = 0; state < reg->size; state++) {
                if (state & control_mask) {
                    int search_mask = ((1 << search_qubits) - 1) << search_start;
                    int search_state = (state & search_mask) >> search_start;
                    
                    // 计算平均振幅
                    double complex avg_amp = 0.0;
                    for (int k = 0; k < search_space_size; k++) {
                        int full_state = (state & ~search_mask) | (k << search_start);
                        avg_amp += reg->amplitudes[full_state];
                    }
                    avg_amp /= search_space_size;
                    
                    // 应用2|ψ⟩⟨ψ| - I操作
                    for (int k = 0; k < search_space_size; k++) {
                        int full_state = (state & ~search_mask) | (k << search_start);
                        reg->amplitudes[full_state] = 2.0 * avg_amp - reg->amplitudes[full_state];
                    }
                }
            }
        }
    }
    
    // 在计数寄存器上应用逆QFT
    inverse_quantum_fourier_transform(reg, counting_start, counting_end);
    
    // 测量计数寄存器
    int result = 0;
    for (int i = counting_start; i <= counting_end; i++) {
        MeasurementResult m = measure_qubit_in_register(reg, i);
        if (m.result == 1) {
            result |= (1 << (i - counting_start));
        }
    }
    
    // 从测量结果计算被标记状态的比例
    double theta = (double)result / (1 << counting_qubits) * 2.0 * M_PI;
    double ratio = sin(theta / 2.0) * sin(theta / 2.0) * search_space_size;
    
    return ratio;
} 