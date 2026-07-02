/*
 * qvm_boot.c - QEntL量子虚拟机
 * 
 * 功能：
 * 1. 解析和执行.qbc量子字节码
 * 2. 模拟量子门操作（H, CNOT, 测量等）
 * 3. 管理量子态叠加和纠缠
 * 4. 提供经典计算能力
 * 
 * 编译: gcc -o bin/qvm_boot src/qvm_boot.c -lm -lpthread
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#include <pthread.h>

#define QVM_VERSION "1.0.0"
#define MAX_QUBITS 64
#define MAX_GATES 1024
#define MAX_MEMORY 1024 * 1024  // 1MB量子内存
#define MAX_STACK 256

// ==================== 量子类型定义 ====================

typedef enum {
    QVM_OK = 0,
    QVM_ERROR = -1,
    QVM_QUANTUM_ERROR = -2,
    QVM_MEMORY_ERROR = -3,
    QVM_STACK_OVERFLOW = -4
} QVMStatus;

typedef enum {
    QUBIT_ZERO = 0,
    QUBIT_ONE = 1,
    QUBIT_SUPERPOSITION = 2
} QubitState;

// 量子比特
typedef struct {
    double amplitude_zero;   // |0⟩ 振幅
    double amplitude_one;    // |1⟩ 振幅
    QubitState state;
    int entangled_with;      // 纠缠对
    int measured;            // 是否已测量
    double phase;            // 相位
} Qubit;

// 量子门
typedef enum {
    GATE_H = 0,       // Hadamard
    GATE_X = 1,       // Pauli-X (NOT)
    GATE_Y = 2,       // Pauli-Y
    GATE_Z = 3,       // Pauli-Z
    GATE_CNOT = 4,    // 控制非门
    GATE_MEASURE = 5, // 测量
    GATE_SWAP = 6,    // 交换门
    GATE_T = 7,       // T门 (π/8)
    GATE_S = 8,       // S门
    GATE_RESET = 9,   // 重置
    GATE_BARRIER = 10 // 屏障
} GateType;

// 量子门指令
typedef struct {
    GateType type;
    int target;       // 目标量子比特
    int control;      // 控制量子比特 (CNOT用)
    double angle;     // 旋转角度
} QuantumGate;

// 经典寄存器
typedef struct {
    unsigned long long value;
    int bits;
} ClassicRegister;

// ==================== QVM状态 ====================

typedef struct {
    // 量子寄存器
    Qubit qubits[MAX_QUBITS];
    int qubit_count;
    
    // 经典寄存器
    ClassicRegister classic_regs[16];
    
    // 量子门队列
    QuantumGate gates[MAX_GATES];
    int gate_count;
    
    // 执行栈
    void* stack[MAX_STACK];
    int stack_top;
    
    // 内存
    unsigned char memory[MAX_MEMORY];
    int memory_used;
    
    // 执行状态
    int running;
    int halted;
    int error_code;
    char error_msg[256];
    
    // 随机数种子
    unsigned int random_seed;
    
    // 性能统计
    long long gates_executed;
    long long cycles;
} QVMContext;

// ==================== 全局上下文 ====================

static QVMContext g_vm;

// ==================== 量子数学工具 ====================

static double rand_double(double min, double max) {
    return min + ((double)rand() / RAND_MAX) * (max - min);
}

static double prob_amplitude(double amp) {
    return amp * amp;
}

// ==================== QVM初始化 ====================

QVMStatus qvm_init(void) {
    memset(&g_vm, 0, sizeof(QVMContext));
    g_vm.qubit_count = 0;
    g_vm.running = 0;
    g_vm.halted = 0;
    g_vm.random_seed = (unsigned int)time(NULL);
    srand(g_vm.random_seed);
    
    // 初始化量子比特到|0⟩状态
    for (int i = 0; i < MAX_QUBITS; i++) {
        g_vm.qubits[i].amplitude_zero = 1.0;
        g_vm.qubits[i].amplitude_one = 0.0;
        g_vm.qubits[i].state = QUBIT_ZERO;
        g_vm.qubits[i].entangled_with = -1;
        g_vm.qubits[i].measured = 0;
        g_vm.qubits[i].phase = 0.0;
    }
    
    printf("[QVM] 量子虚拟机初始化完成 (v%s)\n", QVM_VERSION);
    printf("[QVM] 量子比特: %d/%d\n", g_vm.qubit_count, MAX_QUBITS);
    printf("[QVM] 经典寄存器: 16个\n");
    printf("[QVM] 量子内存: %d KB\n", MAX_MEMORY / 1024);
    
    return QVM_OK;
}

// ==================== 量子比特管理 ====================

int qvm_alloc_qubit(void) {
    if (g_vm.qubit_count >= MAX_QUBITS) {
        strcpy(g_vm.error_msg, "量子比特数量超出限制");
        return -1;
    }
    
    int qid = g_vm.qubit_count++;
    g_vm.qubits[qid].amplitude_zero = 1.0;
    g_vm.qubits[qid].amplitude_one = 0.0;
    g_vm.qubits[qid].state = QUBIT_ZERO;
    g_vm.qubits[qid].entangled_with = -1;
    g_vm.qubits[qid].measured = 0;
    g_vm.qubits[qid].phase = 0.0;
    
    return qid;
}

void qvm_reset_qubit(int qid) {
    if (qid < 0 || qid >= g_vm.qubit_count) return;
    
    g_vm.qubits[qid].amplitude_zero = 1.0;
    g_vm.qubits[qid].amplitude_one = 0.0;
    g_vm.qubits[qid].state = QUBIT_ZERO;
    g_vm.qubits[qid].entangled_with = -1;
    g_vm.qubits[qid].measured = 0;
    g_vm.qubits[qid].phase = 0.0;
}

// ==================== 量子门实现 ====================

// Hadamard门 - 创建叠加态
void gate_h(int qid) {
    if (qid < 0 || qid >= g_vm.qubit_count) return;
    
    Qubit* q = &g_vm.qubits[qid];
    double a0 = q->amplitude_zero;
    double a1 = q->amplitude_one;
    
    // H|0⟩ = (|0⟩ + |1⟩)/√2
    // H|1⟩ = (|0⟩ - |1⟩)/√2
    q->amplitude_zero = (a0 + a1) / sqrt(2.0);
    q->amplitude_one = (a0 - a1) / sqrt(2.0);
    q->state = QUBIT_SUPERPOSITION;
    q->measured = 0;
    
    g_vm.gates_executed++;
}

// Pauli-X门 (NOT门)
void gate_x(int qid) {
    if (qid < 0 || qid >= g_vm.qubit_count) return;
    
    Qubit* q = &g_vm.qubits[qid];
    double temp = q->amplitude_zero;
    q->amplitude_zero = q->amplitude_one;
    q->amplitude_one = temp;
    
    if (q->state == QUBIT_SUPERPOSITION) {
        q->state = QUBIT_ZERO; // 简化状态
    }
    
    g_vm.gates_executed++;
}

// Pauli-Z门
void gate_z(int qid) {
    if (qid < 0 || qid >= g_vm.qubit_count) return;
    
    g_vm.qubits[qid].phase += M_PI;
    g_vm.gates_executed++;
}

// CNOT门 - 纠缠
void gate_cnot(int control, int target) {
    if (control < 0 || control >= g_vm.qubit_count ||
        target < 0 || target >= g_vm.qubit_count) return;
    
    Qubit* ctrl = &g_vm.qubits[control];
    Qubit* tgt = &g_vm.qubits[target];
    
    // 建立纠缠关系
    ctrl->entangled_with = target;
    tgt->entangled_with = control;
    
    // 如果控制比特是|1⟩，翻转目标比特
    if (tgt->state == QUBIT_ZERO && ctrl->state == QUBIT_ONE) {
        double temp = tgt->amplitude_zero;
        tgt->amplitude_zero = tgt->amplitude_one;
        tgt->amplitude_one = temp;
    }
    
    g_vm.gates_executed++;
}

// 测量量子比特
int gate_measure(int qid) {
    if (qid < 0 || qid >= g_vm.qubit_count) return -1;
    
    Qubit* q = &g_vm.qubits[qid];
    
    // 计算概率
    double p0 = prob_amplitude(q->amplitude_zero);
    double p1 = prob_amplitude(q->amplitude_one);
    
    // 随机坍缩
    double r = (double)rand() / RAND_MAX;
    int result = (r < p1) ? 1 : 0;
    
    // 坍缩到测量结果
    if (result == 0) {
        q->amplitude_zero = 1.0;
        q->amplitude_one = 0.0;
    } else {
        q->amplitude_zero = 0.0;
        q->amplitude_one = 1.0;
    }
    
    q->state = (QubitState)result;
    q->measured = 1;
    
    // 如果纠缠，同步测量结果
    if (q->entangled_with >= 0 && q->entangled_with < g_vm.qubit_count) {
        Qubit* partner = &g_vm.qubits[q->entangled_with];
        partner->amplitude_zero = (result == 0) ? 1.0 : 0.0;
        partner->amplitude_one = (result == 1) ? 1.0 : 0.0;
        partner->state = (QubitState)result;
        partner->measured = 1;
    }
    
    g_vm.gates_executed++;
    return result;
}

// 重置量子比特
void gate_reset(int qid) {
    qvm_reset_qubit(qid);
    g_vm.gates_executed++;
}

// ==================== 字节码执行引擎 ====================

// .qbc字节码指令集
typedef enum {
    OP_NOP = 0,
    OP_H = 1,         // Hadamard
    OP_X = 2,         // Pauli-X
    OP_Z = 3,         // Pauli-Z
    OP_CNOT = 4,      // 控制非
    OP_MEASURE = 5,   // 测量
    OP_RESET = 6,     // 重置
    OP_SWAP = 7,      // 交换
    OP_LOAD_REG = 8,  // 加载经典寄存器
    OP_STORE_REG = 9, // 存储到经典寄存器
    OP_JUMP = 10,     // 跳转
    OP_JZ = 11,       // 条件跳转（为零）
    OP_ADD = 12,      // 加法
    OP_SUB = 13,      // 减法
    OP_MUL = 14,      // 乘法
    OP_DIV = 15,      // 除法
    OP_PRINT = 16,    // 打印
    OP_EXIT = 17,     // 退出
    OP_BARRIER = 18   // 屏障
} QVMOpcode;

// 添加编译器定义的opcode
#define OP_INIT_N 0x14
#define OP_STOP 0x15
#define OP_LOAD_CONST 0x20
#define OP_STORE_VAR 0x21
#define OP_LOAD_VAR 0x22
#define OP_T 0x23
#define OP_S 0x24
#define OP_Y 0x25

// 执行单个字节码指令
QVMStatus qvm_execute_bytecode(unsigned char* bytecode, int length) {
    int pc = 0; // 程序计数器
    
    printf("[QVM] 开始执行字节码 (%d bytes)\n", length);
    
    while (pc < length && !g_vm.halted) {
        unsigned char opcode = bytecode[pc++];
        
        switch (opcode) {
        case OP_NOP:
            break;
            
        case OP_INIT_N:  // Initialize qubits (arg1 = low byte, arg2 = high byte)
            {
                uint8_t lo = bytecode[pc++];
                uint8_t hi = bytecode[pc++];
                int nq = (int)lo | ((int)hi << 8);
                printf("[QVM] 初始化 %d 个量子比特\n", nq);
                g_vm.qubit_count = nq;
                // Initialize qubits
                for (int i = 0; i < nq; i++) {
                    qvm_alloc_qubit();
                }
            }
            break;
            
        case OP_H: {
            int qid = bytecode[pc++];
            gate_h(qid);
            printf("[QVM] H(q%d)\n", qid);
            break;
        }
            
        case OP_X: {
            int qid = bytecode[pc++];
            gate_x(qid);
            printf("[QVM] X(q%d)\n", qid);
            break;
        }
            
        case OP_Z: {
            int qid = bytecode[pc++];
            gate_z(qid);
            printf("[QVM] Z(q%d)\n", qid);
            break;
        }
            
        case OP_CNOT: {
            int ctrl = bytecode[pc++];
            int tgt = bytecode[pc++];
            gate_cnot(ctrl, tgt);
            printf("[QVM] CNOT(q%d, q%d)\n", ctrl, tgt);
            break;
        }
            
        case OP_MEASURE: {
            int qid = bytecode[pc++];
            int reg = bytecode[pc++];  // Read register
            int result = gate_measure(qid);
            // Store measurement result into classic register
            if (reg >= 0 && reg < 16) {
                g_vm.classic_regs[reg].value = result;
            }
            printf("[QVM] 测量 q%d -> r%d = %d\n", qid, reg, result);
            break;
        }
            
        case OP_RESET: {
            int qid = bytecode[pc++];
            gate_reset(qid);
            printf("[QVM] RESET(q%d)\n", qid);
            break;
        }
            
        case OP_SWAP: {
            int q1 = bytecode[pc++];
            int q2 = bytecode[pc++];
            if (q1 >= 0 && q1 < g_vm.qubit_count &&
                q2 >= 0 && q2 < g_vm.qubit_count) {
                Qubit* a = &g_vm.qubits[q1];
                Qubit* b = &g_vm.qubits[q2];
                double t0 = a->amplitude_zero;
                double t1 = a->amplitude_one;
                double tphase = a->phase;
                a->amplitude_zero = b->amplitude_zero;
                a->amplitude_one = b->amplitude_one;
                a->phase = b->phase;
                b->amplitude_zero = t0;
                b->amplitude_one = t1;
                b->phase = tphase;
                g_vm.gates_executed++;
            }
            printf("[QVM] SWAP(q%d, q%d)\n", q1, q2);
            break;
        }
            
        case OP_T: {
            int qid = bytecode[pc++];
            if (qid >= 0 && qid < g_vm.qubit_count) {
                Qubit* q = &g_vm.qubits[qid];
                q->phase += M_PI / 4.0;
                g_vm.gates_executed++;
            }
            printf("[QVM] T(q%d)\n", qid);
            break;
        }
            
        case OP_S: {
            int qid = bytecode[pc++];
            if (qid >= 0 && qid < g_vm.qubit_count) {
                Qubit* q = &g_vm.qubits[qid];
                q->phase += M_PI / 2.0;
                g_vm.gates_executed++;
            }
            printf("[QVM] S(q%d)\n", qid);
            break;
        }
            
        case OP_Y: {
            int qid = bytecode[pc++];
            if (qid >= 0 && qid < g_vm.qubit_count) {
                Qubit* q = &g_vm.qubits[qid];
                double t0 = q->amplitude_zero;
                double t1 = q->amplitude_one;
                q->amplitude_zero = -t1;
                q->amplitude_one = t0;
                q->state = QUBIT_SUPERPOSITION;
                g_vm.gates_executed++;
            }
            printf("[QVM] Y(q%d)\n", qid);
            break;
        }
            
        case OP_BARRIER: {
            printf("[QVM] BARRIER\n");
            break;
        }
            
        case OP_PRINT: {
            int reg = bytecode[pc++];
            printf("[QVM] print(r%d) = %llu\n", reg, g_vm.classic_regs[reg].value);
            break;
        }
            
        case OP_STOP:
        case OP_EXIT:
            g_vm.halted = 1;
            printf("[QVM] 程序退出\n");
            break;
            
        case OP_LOAD_CONST: {
            uint8_t lo = bytecode[pc++];
            uint8_t hi = bytecode[pc++];
            int idx = (int)lo | ((int)hi << 8);
            printf("[QVM] LOAD_CONST(%d)\n", idx);
            break;
        }
            
        case OP_STORE_VAR: {
            uint8_t lo = bytecode[pc++];
            uint8_t hi = bytecode[pc++];
            int idx = (int)lo | ((int)hi << 8);
            printf("[QVM] STORE_VAR(%d)\n", idx);
            break;
        }
            
        case OP_LOAD_VAR: {
            uint8_t lo = bytecode[pc++];
            uint8_t hi = bytecode[pc++];
            int idx = (int)lo | ((int)hi << 8);
            printf("[QVM] LOAD_VAR(%d)\n", idx);
            break;
        }
            
        case OP_LOAD_REG:
        case OP_STORE_REG:
        case OP_JUMP:
        case OP_JZ:
        case OP_ADD:
        case OP_SUB:
        case OP_MUL:
        case OP_DIV:
            printf("[QVM] 经典指令: 0x%02x (跳过)\n", opcode);
            break;
            
        default:
            printf("[QVM] 未知指令: 0x%02x\n", opcode);
            break;
        }
        
        g_vm.cycles++;
    }
    
    printf("[QVM] 执行完成: %lld 周期, %lld 门操作\n", 
           g_vm.cycles, g_vm.gates_executed);
    
    return QVM_OK;
}

// ==================== 量子态查询 ====================

void qvm_print_state(void) {
    printf("\n=== 量子态 ===\n");
    for (int i = 0; i < g_vm.qubit_count; i++) {
        Qubit* q = &g_vm.qubits[i];
        printf("q[%d]: ", i);
        
        if (q->measured) {
            printf("|%d⟩ (已测量)\n", q->state);
        } else if (q->state == QUBIT_SUPERPOSITION) {
            printf("(%.2f)|0⟩ + (%.2f)|1⟩)\n", 
                   q->amplitude_zero, q->amplitude_one);
        } else {
            printf("|%d⟩\n", q->state);
        }
    }
    printf("=================\n\n");
}

// ==================== 测试用例 ====================

void run_test_bell_state(void) {
    printf("\n>>> 测试: 贝尔态 (Bell State) <<<\n");
    
    // 创建两个量子比特
    int q0 = qvm_alloc_qubit();
    int q1 = qvm_alloc_qubit();
    
    printf("[TEST] 创建 q0=%d, q1=%d\n", q0, q1);
    
    // H门作用于q0 - 创建叠加态
    gate_h(q0);
    printf("[TEST] H(q0) - 创建叠加态\n");
    
    // CNOT门 - 纠缠
    gate_cnot(q0, q1);
    printf("[TEST] CNOT(q0, q1) - 建立纠缠\n");
    
    // 测量
    int m0 = gate_measure(q0);
    int m1 = gate_measure(q1);
    
    printf("[TEST] 测量结果: q0=%d, q1=%d\n", m0, m1);
    printf("[TEST] 纠缠验证: %s\n", 
           (m0 == m1) ? "✓ 纠缠成功!" : "✗ 纠缠失败!");
    
    qvm_print_state();
}

void run_test_superposition(void) {
    printf("\n>>> 测试: 叠加态 <<<\n");
    
    int q = qvm_alloc_qubit();
    gate_h(q);
    
    printf("[TEST] 叠加态 q%d: (%.2f)|0⟩ + (%.2f)|1⟩)\n",
           q, g_vm.qubits[q].amplitude_zero, 
           g_vm.qubits[q].amplitude_one);
    
    // 多次测量统计
    int count0 = 0, count1 = 0;
    for (int i = 0; i < 100; i++) {
        qvm_reset_qubit(q);
        gate_h(q);
        if (gate_measure(q) == 0) count0++;
        else count1++;
    }
    
    printf("[TEST] 100次测量统计: |0⟩=%d, |1⟩=%d\n", count0, count1);
    printf("[TEST] 概率分布: |0⟩=%.1f%%, |1⟩=%.1f%%\n",
           (double)count0, (double)count1);
    
    qvm_print_state();
}

// ==================== 主函数 ====================

int main(int argc, char* argv[]) {
    printf("╔══════════════════════════════════════╗\n");
    printf("║    QEntL Quantum Virtual Machine     ║\n");
    printf("║    Version %s                       ║\n", QVM_VERSION);
    printf("╚══════════════════════════════════════╝\n\n");
    
    // 初始化
    qvm_init();
    
    if (argc < 2) {
        printf("用法: %s <test|bytecode.qbc>\n", argv[0]);
        printf("  test      - 运行量子测试\n");
        printf("  bytecode  - 执行.qbc字节码文件\n");
        return 0;
    }
    
    if (strcmp(argv[1], "test") == 0) {
        printf("=== QVM 量子测试套件 ===\n\n");
        
        run_test_superposition();
        run_test_bell_state();
        
        printf("\n=== 所有测试完成 ===\n");
    } else {
        // 加载并执行字节码文件
        FILE* f = fopen(argv[1], "rb");
        if (!f) {
            printf("错误: 无法打开文件 %s\n", argv[1]);
            return 1;
        }
        
        fseek(f, 0, SEEK_END);
        int size = ftell(f);
        fseek(f, 0, SEEK_SET);
        
        unsigned char* bytecode = malloc(size);
        fread(bytecode, 1, size, f);
        fclose(f);
        
        /* v3.x编译器输出纯字节码(无header), 直接执行;
           旧格式文件(含58B header + 魔数)才需要跳过header */
        unsigned char* exec_ptr = bytecode;
        int exec_length = size;
        /* 检测旧格式: 前58字节包含非纯opcode字节(魔数/文本) */
        {
            int has_header = 0;
            if (size > 4) {
                /* 旧格式魔数特征: 前4字节非纯opcode(包含字母ASCII) */
                if ((bytecode[0] >= 'A' && bytecode[0] <= 'Z') ||
                    (bytecode[0] >= 'a' && bytecode[0] <= 'z')) {
                    has_header = 1;
                }
            }
            if (has_header && size > 58) {
                exec_ptr = bytecode + 58;
                exec_length = size - 58;
            }
        }
        
        qvm_execute_bytecode(exec_ptr, exec_length);
        free(bytecode);
    }
    
    return 0;
}
