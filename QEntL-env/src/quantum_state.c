/**
 * 量子状态管理实现
 * 
 * 实现了QEntL中的量子状态和相关操作。
 * 包含量子比特、量子寄存器和量子纠缠的核心操作。
 */

#include "quantum_state.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

/* -------------------- 工具函数 -------------------- */

// 复数平方幅度
static double complex_abs_squared(double complex z) {
    return creal(z) * creal(z) + cimag(z) * cimag(z);
}

// 生成[0,1)之间的随机数
static double rand_double() {
    static int seeded = 0;
    if (!seeded) {
        srand((unsigned int)time(NULL));
        seeded = 1;
    }
    return (double)rand() / RAND_MAX;
}

// 检查量子比特的归一化条件
static int is_normalized(QubitState qubit, double epsilon) {
    double sum = complex_abs_squared(qubit.alpha) + complex_abs_squared(qubit.beta);
    return fabs(sum - 1.0) < epsilon;
}

// 归一化量子比特状态
static QubitState normalize_qubit(QubitState qubit) {
    double norm = sqrt(complex_abs_squared(qubit.alpha) + complex_abs_squared(qubit.beta));
    
    if (norm < 1e-10) {
        // 如果振幅几乎为零，设为|0⟩状态
        qubit.alpha = 1.0;
        qubit.beta = 0.0;
        return qubit;
    }
    
    qubit.alpha /= norm;
    qubit.beta /= norm;
    return qubit;
}

/* -------------------- 量子比特函数实现 -------------------- */

QubitState create_qubit() {
    QubitState qubit;
    qubit.alpha = 1.0 + 0.0 * I;  // |0⟩ 状态
    qubit.beta = 0.0 + 0.0 * I;
    return qubit;
}

QubitState create_qubit_state(double complex alpha, double complex beta) {
    QubitState qubit;
    qubit.alpha = alpha;
    qubit.beta = beta;
    return normalize_qubit(qubit);
}

QubitState apply_hadamard(QubitState qubit) {
    QubitState result;
    double sqrt2_inv = 1.0 / sqrt(2.0);
    
    result.alpha = sqrt2_inv * (qubit.alpha + qubit.beta);
    result.beta = sqrt2_inv * (qubit.alpha - qubit.beta);
    
    return result;
}

QubitState apply_pauli_x(QubitState qubit) {
    QubitState result;
    result.alpha = qubit.beta;
    result.beta = qubit.alpha;
    return result;
}

QubitState apply_pauli_y(QubitState qubit) {
    QubitState result;
    result.alpha = -I * qubit.beta;
    result.beta = I * qubit.alpha;
    return result;
}

QubitState apply_pauli_z(QubitState qubit) {
    QubitState result;
    result.alpha = qubit.alpha;
    result.beta = -qubit.beta;
    return result;
}

QubitState apply_rotation_x(QubitState qubit, double angle) {
    QubitState result;
    double cos_half = cos(angle / 2.0);
    double sin_half = sin(angle / 2.0);
    
    result.alpha = cos_half * qubit.alpha - I * sin_half * qubit.beta;
    result.beta = -I * sin_half * qubit.alpha + cos_half * qubit.beta;
    
    return result;
}

QubitState apply_rotation_y(QubitState qubit, double angle) {
    QubitState result;
    double cos_half = cos(angle / 2.0);
    double sin_half = sin(angle / 2.0);
    
    result.alpha = cos_half * qubit.alpha - sin_half * qubit.beta;
    result.beta = sin_half * qubit.alpha + cos_half * qubit.beta;
    
    return result;
}

QubitState apply_rotation_z(QubitState qubit, double angle) {
    QubitState result;
    double complex phase = cos(angle / 2.0) - I * sin(angle / 2.0);
    double complex phase_conj = cos(angle / 2.0) + I * sin(angle / 2.0);
    
    result.alpha = phase_conj * qubit.alpha;
    result.beta = phase * qubit.beta;
    
    return result;
}

QubitState apply_phase(QubitState qubit, double angle) {
    QubitState result;
    double complex phase = cos(angle) + I * sin(angle);
    
    result.alpha = qubit.alpha;
    result.beta = phase * qubit.beta;
    
    return result;
}

QubitState apply_t_gate(QubitState qubit) {
    // T门是Z旋转π/4
    return apply_phase(qubit, M_PI / 4.0);
}

MeasurementResult measure_qubit(QubitState* qubit) {
    MeasurementResult result;
    double prob_0 = complex_abs_squared(qubit->alpha);
    double rand_val = rand_double();
    
    if (rand_val < prob_0) {
        // 坍缩到|0⟩
        result.result = 0;
        result.probability = prob_0;
        qubit->alpha = 1.0 + 0.0 * I;
        qubit->beta = 0.0 + 0.0 * I;
    } else {
        // 坍缩到|1⟩
        result.result = 1;
        result.probability = 1.0 - prob_0;
        qubit->alpha = 0.0 + 0.0 * I;
        qubit->beta = 1.0 + 0.0 * I;
    }
    
    return result;
}

/* -------------------- 量子寄存器函数实现 -------------------- */

QuantumRegister* create_quantum_register(int num_qubits) {
    if (num_qubits <= 0) {
        return NULL;
    }
    
    QuantumRegister* reg = (QuantumRegister*)malloc(sizeof(QuantumRegister));
    if (!reg) {
        return NULL;
    }
    
    reg->num_qubits = num_qubits;
    reg->size = 1 << num_qubits; // 2^num_qubits
    
    reg->amplitudes = (double complex*)malloc(reg->size * sizeof(double complex));
    if (!reg->amplitudes) {
        free(reg);
        return NULL;
    }
    
    // 初始化为|0...0⟩态
    memset(reg->amplitudes, 0, reg->size * sizeof(double complex));
    reg->amplitudes[0] = 1.0 + 0.0 * I;
    
    return reg;
}

void free_quantum_register(QuantumRegister* reg) {
    if (reg) {
        if (reg->amplitudes) {
            free(reg->amplitudes);
        }
        free(reg);
    }
}

void reset_quantum_register(QuantumRegister* reg) {
    if (!reg || !reg->amplitudes) {
        return;
    }
    
    // 重置为|0...0⟩态
    memset(reg->amplitudes, 0, reg->size * sizeof(double complex));
    reg->amplitudes[0] = 1.0 + 0.0 * I;
}

void apply_hadamard_to_qubit(QuantumRegister* reg, int qubit_index) {
    if (!reg || !reg->amplitudes || qubit_index < 0 || qubit_index >= reg->num_qubits) {
        return;
    }
    
    int mask = 1 << qubit_index;
    double sqrt2_inv = 1.0 / sqrt(2.0);
    
    // 为每个可能的计算基态应用Hadamard变换
    for (int basis = 0; basis < reg->size; basis += (2 * mask)) {
        for (int offset = 0; offset < mask; offset++) {
            int i0 = basis + offset;             // 该比特为0的状态
            int i1 = basis + offset + mask;      // 该比特为1的状态
            
            double complex a0 = reg->amplitudes[i0];
            double complex a1 = reg->amplitudes[i1];
            
            reg->amplitudes[i0] = sqrt2_inv * (a0 + a1);
            reg->amplitudes[i1] = sqrt2_inv * (a0 - a1);
        }
    }
}

void apply_pauli_x_to_qubit(QuantumRegister* reg, int qubit_index) {
    if (!reg || !reg->amplitudes || qubit_index < 0 || qubit_index >= reg->num_qubits) {
        return;
    }
    
    int mask = 1 << qubit_index;
    
    // 为每个可能的计算基态应用X门（比特翻转）
    for (int basis = 0; basis < reg->size; basis += (2 * mask)) {
        for (int offset = 0; offset < mask; offset++) {
            int i0 = basis + offset;             // 该比特为0的状态
            int i1 = basis + offset + mask;      // 该比特为1的状态
            
            // 交换振幅
            double complex temp = reg->amplitudes[i0];
            reg->amplitudes[i0] = reg->amplitudes[i1];
            reg->amplitudes[i1] = temp;
        }
    }
}

void apply_cnot(QuantumRegister* reg, int control_qubit, int target_qubit) {
    if (!reg || !reg->amplitudes || 
        control_qubit < 0 || control_qubit >= reg->num_qubits ||
        target_qubit < 0 || target_qubit >= reg->num_qubits ||
        control_qubit == target_qubit) {
        return;
    }
    
    int control_mask = 1 << control_qubit;
    int target_mask = 1 << target_qubit;
    
    // 为每个可能的计算基态应用CNOT门
    for (int i = 0; i < reg->size; i++) {
        // 只有当控制比特为1时才翻转目标比特
        if (i & control_mask) {
            int j = i ^ target_mask;  // 翻转目标比特
            
            // 交换振幅
            double complex temp = reg->amplitudes[i];
            reg->amplitudes[i] = reg->amplitudes[j];
            reg->amplitudes[j] = temp;
        }
    }
}

void apply_controlled_z(QuantumRegister* reg, int control_qubit, int target_qubit) {
    if (!reg || !reg->amplitudes || 
        control_qubit < 0 || control_qubit >= reg->num_qubits ||
        target_qubit < 0 || target_qubit >= reg->num_qubits ||
        control_qubit == target_qubit) {
        return;
    }
    
    int control_mask = 1 << control_qubit;
    int target_mask = 1 << target_qubit;
    
    // 为每个可能的计算基态应用CZ门
    for (int i = 0; i < reg->size; i++) {
        // 只有当控制比特和目标比特都为1时才施加相位
        if ((i & control_mask) && (i & target_mask)) {
            reg->amplitudes[i] = -reg->amplitudes[i];
        }
    }
}

void apply_toffoli(QuantumRegister* reg, int control1, int control2, int target) {
    if (!reg || !reg->amplitudes || 
        control1 < 0 || control1 >= reg->num_qubits ||
        control2 < 0 || control2 >= reg->num_qubits ||
        target < 0 || target >= reg->num_qubits ||
        control1 == control2 || control1 == target || control2 == target) {
        return;
    }
    
    int control1_mask = 1 << control1;
    int control2_mask = 1 << control2;
    int target_mask = 1 << target;
    
    // 为每个可能的计算基态应用Toffoli门
    for (int i = 0; i < reg->size; i++) {
        // 只有当两个控制比特都为1时才翻转目标比特
        if ((i & control1_mask) && (i & control2_mask)) {
            int j = i ^ target_mask;  // 翻转目标比特
            
            // 交换振幅
            double complex temp = reg->amplitudes[i];
            reg->amplitudes[i] = reg->amplitudes[j];
            reg->amplitudes[j] = temp;
        }
    }
}

void apply_swap(QuantumRegister* reg, int qubit_a, int qubit_b) {
    if (!reg || !reg->amplitudes || 
        qubit_a < 0 || qubit_a >= reg->num_qubits ||
        qubit_b < 0 || qubit_b >= reg->num_qubits ||
        qubit_a == qubit_b) {
        return;
    }
    
    int mask_a = 1 << qubit_a;
    int mask_b = 1 << qubit_b;
    
    // 为每个不一致的基态交换振幅
    for (int i = 0; i < reg->size; i++) {
        int bit_a = (i & mask_a) ? 1 : 0;
        int bit_b = (i & mask_b) ? 1 : 0;
        
        if (bit_a != bit_b) {
            int j = i ^ mask_a ^ mask_b;  // 交换两个比特
            
            // 确保只处理每对状态一次
            if (i < j) {
                double complex temp = reg->amplitudes[i];
                reg->amplitudes[i] = reg->amplitudes[j];
                reg->amplitudes[j] = temp;
            }
        }
    }
}

MeasurementResult measure_qubit_in_register(QuantumRegister* reg, int qubit_index) {
    if (!reg || !reg->amplitudes || qubit_index < 0 || qubit_index >= reg->num_qubits) {
        MeasurementResult error = {-1, 0.0};
        return error;
    }
    
    int mask = 1 << qubit_index;
    double prob_0 = 0.0;
    
    // 计算测量结果为0的概率
    for (int i = 0; i < reg->size; i++) {
        if (!(i & mask)) {  // 如果测量的比特为0
            prob_0 += complex_abs_squared(reg->amplitudes[i]);
        }
    }
    
    // 生成随机数决定测量结果
    double rand_val = rand_double();
    int result;
    double probability;
    
    if (rand_val < prob_0) {
        // 坍缩到该比特为0的状态
        result = 0;
        probability = prob_0;
        
        // 将所有该比特为1的态的振幅置为0，并重新归一化
        double norm_factor = 1.0 / sqrt(prob_0);
        for (int i = 0; i < reg->size; i++) {
            if (i & mask) {  // 如果测量的比特为1
                reg->amplitudes[i] = 0.0 + 0.0 * I;
            } else {
                reg->amplitudes[i] *= norm_factor;
            }
        }
    } else {
        // 坍缩到该比特为1的状态
        result = 1;
        probability = 1.0 - prob_0;
        
        // 将所有该比特为0的态的振幅置为0，并重新归一化
        double norm_factor = 1.0 / sqrt(probability);
        for (int i = 0; i < reg->size; i++) {
            if (!(i & mask)) {  // 如果测量的比特为0
                reg->amplitudes[i] = 0.0 + 0.0 * I;
            } else {
                reg->amplitudes[i] *= norm_factor;
            }
        }
    }
    
    MeasurementResult measurement = {result, probability};
    return measurement;
}

double complex* get_state_vector(QuantumRegister* reg) {
    if (!reg || !reg->amplitudes) {
        return NULL;
    }
    
    double complex* state_vector = (double complex*)malloc(reg->size * sizeof(double complex));
    if (!state_vector) {
        return NULL;
    }
    
    memcpy(state_vector, reg->amplitudes, reg->size * sizeof(double complex));
    return state_vector;
}

double calculate_entanglement(QuantumRegister* reg, int qubit_a, int qubit_b) {
    if (!reg || !reg->amplitudes || 
        qubit_a < 0 || qubit_a >= reg->num_qubits ||
        qubit_b < 0 || qubit_b >= reg->num_qubits ||
        qubit_a == qubit_b) {
        return 0.0;
    }
    
    // 计算约化密度矩阵
    double rho[4] = {0.0, 0.0, 0.0, 0.0};  // 约化密度矩阵元素: rho_00, rho_01, rho_10, rho_11
    int mask_a = 1 << qubit_a;
    int mask_b = 1 << qubit_b;
    
    for (int i = 0; i < reg->size; i++) {
        int bit_a = (i & mask_a) ? 1 : 0;
        int bit_b = (i & mask_b) ? 1 : 0;
        int idx = bit_a * 2 + bit_b;
        
        for (int j = 0; j < reg->size; j++) {
            int bit_a_j = (j & mask_a) ? 1 : 0;
            int bit_b_j = (j & mask_b) ? 1 : 0;
            int idx_j = bit_a_j * 2 + bit_b_j;
            
            double complex product = conj(reg->amplitudes[i]) * reg->amplitudes[j];
            
            // 只有当两个态在其他比特上相同时才贡献
            int other_bits_same = 1;
            for (int k = 0; k < reg->num_qubits; k++) {
                if (k != qubit_a && k != qubit_b) {
                    int mask_k = 1 << k;
                    if ((i & mask_k) != (j & mask_k)) {
                        other_bits_same = 0;
                        break;
                    }
                }
            }
            
            if (other_bits_same) {
                int matrix_idx = idx * 2 + idx_j;
                if (matrix_idx < 4) {
                    rho[matrix_idx] += creal(product);
                }
            }
        }
    }
    
    // 计算冯·诺依曼熵作为纠缠度量
    double eigenvalues[2] = {0.0, 0.0};
    double trace = rho[0] + rho[3];
    double det = rho[0] * rho[3] - rho[1] * rho[2];
    
    // 计算特征值
    double discriminant = sqrt(trace * trace - 4 * det);
    eigenvalues[0] = (trace + discriminant) / 2.0;
    eigenvalues[1] = (trace - discriminant) / 2.0;
    
    // 计算冯·诺依曼熵
    double entropy = 0.0;
    for (int i = 0; i < 2; i++) {
        if (eigenvalues[i] > 1e-10) {
            entropy -= eigenvalues[i] * log2(eigenvalues[i]);
        }
    }
    
    // 归一化到[0,1]范围
    return entropy / log2(2.0);
}

/* -------------------- 量子纠缠图函数实现 -------------------- */

EntanglementGraph* create_entanglement_graph() {
    EntanglementGraph* graph = (EntanglementGraph*)malloc(sizeof(EntanglementGraph));
    if (graph) {
        graph->head = NULL;
        graph->count = 0;
    }
    return graph;
}

void free_entanglement_graph(EntanglementGraph* graph) {
    if (!graph) {
        return;
    }
    
    EntanglementNode* current = graph->head;
    while (current) {
        EntanglementNode* next = current->next;
        free(current);
        current = next;
    }
    
    free(graph);
}

void add_entanglement(EntanglementGraph* graph, int qubit_a, int qubit_b, double strength) {
    if (!graph || qubit_a == qubit_b || strength < 0.0 || strength > 1.0) {
        return;
    }
    
    // 确保qubit_a < qubit_b以保持一致性
    if (qubit_a > qubit_b) {
        int temp = qubit_a;
        qubit_a = qubit_b;
        qubit_b = temp;
    }
    
    // 检查是否已存在此纠缠
    EntanglementNode* existing = find_entanglement(graph, qubit_a, qubit_b);
    if (existing) {
        existing->strength = strength;
        return;
    }
    
    // 创建新节点
    EntanglementNode* node = (EntanglementNode*)malloc(sizeof(EntanglementNode));
    if (!node) {
        return;
    }
    
    node->qubit_a = qubit_a;
    node->qubit_b = qubit_b;
    node->strength = strength;
    
    // 添加到链表头部
    node->next = graph->head;
    graph->head = node;
    graph->count++;
}

void remove_entanglement(EntanglementGraph* graph, int qubit_a, int qubit_b) {
    if (!graph || !graph->head) {
        return;
    }
    
    // 确保qubit_a < qubit_b以保持一致性
    if (qubit_a > qubit_b) {
        int temp = qubit_a;
        qubit_a = qubit_b;
        qubit_b = temp;
    }
    
    // 特殊处理头节点
    if (graph->head->qubit_a == qubit_a && graph->head->qubit_b == qubit_b) {
        EntanglementNode* temp = graph->head;
        graph->head = graph->head->next;
        free(temp);
        graph->count--;
        return;
    }
    
    // 遍历链表
    EntanglementNode* current = graph->head;
    while (current->next) {
        if (current->next->qubit_a == qubit_a && current->next->qubit_b == qubit_b) {
            EntanglementNode* temp = current->next;
            current->next = current->next->next;
            free(temp);
            graph->count--;
            return;
        }
        current = current->next;
    }
}

EntanglementNode* find_entanglement(EntanglementGraph* graph, int qubit_a, int qubit_b) {
    if (!graph || !graph->head) {
        return NULL;
    }
    
    // 确保qubit_a < qubit_b以保持一致性
    if (qubit_a > qubit_b) {
        int temp = qubit_a;
        qubit_a = qubit_b;
        qubit_b = temp;
    }
    
    // 遍历链表
    EntanglementNode* current = graph->head;
    while (current) {
        if (current->qubit_a == qubit_a && current->qubit_b == qubit_b) {
            return current;
        }
        current = current->next;
    }
    
    return NULL;
}

void update_entanglement_strength(EntanglementGraph* graph, int qubit_a, int qubit_b, double strength) {
    if (!graph || strength < 0.0 || strength > 1.0) {
        return;
    }
    
    EntanglementNode* node = find_entanglement(graph, qubit_a, qubit_b);
    if (node) {
        node->strength = strength;
    } else {
        add_entanglement(graph, qubit_a, qubit_b, strength);
    }
}

void propagate_entanglement_effects(EntanglementGraph* graph, QuantumRegister* reg, int changed_qubit) {
    if (!graph || !graph->head || !reg || changed_qubit < 0 || changed_qubit >= reg->num_qubits) {
        return;
    }
    
    // 找到与changed_qubit相关的所有纠缠
    EntanglementNode* current = graph->head;
    while (current) {
        if (current->qubit_a == changed_qubit || current->qubit_b == changed_qubit) {
            int other_qubit = (current->qubit_a == changed_qubit) ? current->qubit_b : current->qubit_a;
            
            // 根据纠缠强度计算效应
            double strength = current->strength;
            
            // 如果纠缠很强，应用CNOT来传播效应
            if (strength > 0.8) {
                apply_cnot(reg, changed_qubit, other_qubit);
            }
            // 如果纠缠中等，应用受控Z门
            else if (strength > 0.5) {
                apply_controlled_z(reg, changed_qubit, other_qubit);
            }
            // 如果纠缠较弱，只应用部分相位
            else if (strength > 0.2) {
                // 对纠缠的比特应用部分相位旋转
                int mask = 1 << other_qubit;
                double phase_angle = strength * M_PI;
                
                for (int i = 0; i < reg->size; i++) {
                    if ((i & mask) && (i & (1 << changed_qubit))) {
                        double complex phase = cos(phase_angle) + I * sin(phase_angle);
                        reg->amplitudes[i] *= phase;
                    }
                }
            }
        }
        current = current->next;
    }
} 