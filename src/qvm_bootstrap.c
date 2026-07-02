/*
 * qvm_bootstrap.c — QVM量子虚拟机 C语言启动器
 * ⚠️ 只作为启动器，真正计算由QEntL全栈执行
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define MAX_QUBITS 64
#define MAX_REGISTERS 64
#define MAX_MEM 256 * 1024 * 1024  /* 256MB for up to 22 qubits */
#define MAX_CYCLES 10000

/* 操作码 */
enum {
    OP_INIT = 0x14,
    OP_H = 0x00, OP_X = 0x01, OP_Y = 0x02, OP_Z = 0x03,
    OP_CNOT = 0x04, OP_S = 0x05, OP_T = 0x06, OP_SWAP = 0x07,
    OP_RESET = 0x08, OP_MEASURE = 0x09, OP_BARRIER = 0x0A,
    OP_PRINT = 0x0B, OP_STOP = 0x0C, OP_LOAD = 0x0D,
    OP_STORE = 0x0E, OP_ADD = 0x0F, OP_MUL = 0x10,
    OP_CALL = 0x11, OP_RET = 0x12
};

typedef struct {
    double real;
    double imag;
} complex_t;

typedef struct {
    int num_qubits;
    int qubits;
    complex_t *state;
    int registers[MAX_REGISTERS];
    int amplitudes[MAX_QUBITS];
    int cycles;
    int ops;
} QVM;

static void qvm_reset(QVM *vm, int n) {
    vm->qubits = n;
    vm->num_qubits = n;
    int size = 1 << n;
    if (vm->state) free(vm->state);
    // 内存安全检查: >20 qubits (2^20 * 16 = 16MB) 用简化模式
    if (n > 20 || size * sizeof(complex_t) > MAX_MEM * 2) {
        vm->state = NULL;
        printf("[QVM] 量子比特数=%d，使用简化模拟模式（不展开完整态矢量）\\n", n);
    } else {
        vm->state = (complex_t *)calloc(size, sizeof(complex_t));
        if (vm->state) {
            vm->state[0].real = 1.0;
            vm->state[0].imag = 0.0;
        } else {
            printf("[QVM] 警告: 内存不足，使用简化模拟模式\\n");
        }
    }
    memset(vm->registers, 0, sizeof(vm->registers));
    memset(vm->amplitudes, 0, sizeof(vm->amplitudes));
    vm->cycles = 0;
    vm->ops = 0;
}

static complex_t c_mul(complex_t a, complex_t b) {
    return (complex_t){a.real * b.real - a.imag * b.imag,
                       a.real * b.imag + a.imag * b.real};
}

static void apply_gate(QVM *vm, int opcode, int op1, int op2) {
    int n = vm->qubits;
    int size = 1 << n;

    vm->cycles++;
    vm->ops++;

    // 简化模式: 量子比特>20时只记录门操作和测量，不展开态矢量
    if (vm->state == NULL) {
        if (opcode == OP_MEASURE) {
            int result = (rand() % 2);
            if (op2 < MAX_REGISTERS) vm->registers[op2] = result;
            printf("[QVM] 测量 q%d -> r%d = %d [简化模式]\n", op1, op2, result);
        } else if (opcode == OP_PRINT) {
            int val = (op1 < MAX_REGISTERS) ? vm->registers[op1] : 0;
            printf("[QVM] print(r%d) = %d [简化模式]\n", op1, val);
        }
        return;
    }

    complex_t *tmp = (complex_t *)calloc(size, sizeof(complex_t));
    if (!tmp) return;

    if (opcode == OP_H) {
        double s2 = 1.0 / sqrt(2.0);
        if (op1 >= n) goto end_gate;  /* qubit超出范围，跳过避免越界 */
        memcpy(tmp, vm->state, sizeof(complex_t) * size);
        for (int s = 0; s < size; s++) {
            if (((s >> op1) & 1) == 1) {
                int pair = s ^ (1 << op1);
                double r0 = tmp[pair].real, i0 = tmp[pair].imag;
                double r1 = tmp[s].real, i1 = tmp[s].imag;
                tmp[pair] = (complex_t){(r0 + r1) * s2, (i0 + i1) * s2};
                tmp[s]    = (complex_t){(r0 - r1) * s2, (i0 - i1) * s2};
            }
        }
        memcpy(vm->state, tmp, sizeof(complex_t) * size);
    } else if (opcode == OP_X) {
        if (op1 >= n) goto end_gate;
        memcpy(tmp, vm->state, sizeof(complex_t) * size);
        for (int s = 0; s < size; s++) {
            int pair = s ^ (1 << op1);
            if (pair > s) {
                vm->state[s] = tmp[pair];
                vm->state[pair] = tmp[s];
            } else if (pair == s) {
                vm->state[s] = tmp[s];
            }
        }
    } else if (opcode == OP_CNOT) {
        if (op1 >= n || op2 >= n) goto end_gate;
        memcpy(tmp, vm->state, sizeof(complex_t) * size);
        for (int s = 0; s < size; s++) {
            if (((s >> op1) & 1) == 1) {
                int tgt = s ^ (1 << op2);
                vm->state[s] = tmp[tgt];
                vm->state[tgt] = tmp[s];
            }
        }
    } else if (opcode == OP_MEASURE) {
        int result = (rand() % 2);
        if (op2 < MAX_REGISTERS) vm->registers[op2] = result;
        printf("[QVM] 测量 q%d -> r%d = %d\n", op1, op2, result);
    } else if (opcode == OP_PRINT) {
        int val = (op1 < MAX_REGISTERS) ? vm->registers[op1] : 0;
        printf("[QVM] print(r%d) = %d\n", op1, val);
    } else if (opcode == OP_STOP) {
        /* STOP handled by main loop */
    } else {
        /* 兼容QCL编译器字节码：Z/S/T/SWAP/RESET/BARRIER等做no-op */
    }
end_gate:
    free(tmp);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("[QVM] 用法: %s <字节码文件>\n", argv[0]);
        return 1;
    }

    FILE *f = fopen(argv[1], "rb");
    if (!f) {
        fprintf(stderr, "[QVM] 错误: 无法打开 %s\n", argv[1]);
        return 1;
    }

    fseek(f, 0, SEEK_END);
    long fsize = ftell(f);
    fseek(f, 0, SEEK_SET);
    uint8_t *code = (uint8_t *)malloc(fsize);
    fread(code, 1, fsize, f);
    fclose(f);

    QVM vm;
    vm.state = NULL;
    int pos = 0;
    printf("[QVM] 初始化量子虚拟机\n");
    while (pos < fsize) {
        uint8_t op = code[pos++];
        if (op == OP_INIT) {
            int n = code[pos++];
            qvm_reset(&vm, n);
            printf("[QVM] 初始化 %d 个量子比特\n", n);
            continue;
        }
        if (op == OP_STOP) {
            printf("[QVM] 程序退出\n");
            printf("[QVM] 执行完成: %d 周期, %d 门操作\n", vm.cycles, vm.ops);
            free(code);
            free(vm.state);
            return 0;
        }
        switch (op) {
        case OP_INIT: {
            int n = code[pos++];
            qvm_reset(&vm, n);
            printf("[QVM] 初始化 %d 个量子比特\n", n);
            continue;
        }
        case OP_STOP: {
            printf("[QVM] 程序退出\n");
            printf("[QVM] 执行完成: %d 周期, %d 门操作\n", vm.cycles, vm.ops);
            free(code);
            free(vm.state);
            return 0;
        }
        case 0x15: { // QCL编译器STOP操作码(兼容QCL输出)
            printf("[QVM] 程序退出\n");
            printf("[QVM] 执行完成: %d 周期, %d 门操作\n", vm.cycles, vm.ops);
            free(code);
            if (vm.state) free(vm.state);
            return 0;
        }
        case OP_H:  { int q = code[pos++]; apply_gate(&vm, OP_H, q, 0);
                      printf("[QVM] H(q%d)\n", q); break; }
        case OP_X:  { int q = code[pos++]; apply_gate(&vm, OP_X, q, 0);
                      printf("[QVM] X(q%d)\n", q); break; }
        case OP_CNOT: { int c = code[pos++], t = code[pos++];
                        apply_gate(&vm, OP_CNOT, c, t);
                        printf("[QVM] CNOT(q%d, q%d)\n", c, t); break; }
        case OP_MEASURE: { int q = code[pos++], r = code[pos++];
                           apply_gate(&vm, OP_MEASURE, q, r); break; }
        case OP_PRINT: { int r = code[pos++];
                         apply_gate(&vm, OP_PRINT, r, 0); break; }
        case 0x05: { // QCL编译器MEASURE操作码(2参数: qubit, register)
                     int q = code[pos++], r = code[pos++];
                     apply_gate(&vm, OP_MEASURE, q, r); break; }
        case 0x10: { // QCL编译器PRINT操作码(1参数: register)
                     int r = code[pos++];
                     apply_gate(&vm, OP_PRINT, r, 0); break; }
        case 0x07: { // QCL/SWAP等: 读取后续参数再跳过（避免对齐偏移）
                     /* no-op 单比特门，但跳过1个参数字节保持对齐 */
                     int _arg = code[pos++]; (void)_arg; break; }
        case 0x06: { /* QCL T gate: no-op 单比特 */ int _a = code[pos++]; (void)_a; break; }
        case 0x03: { /* QCL Z gate: no-op 单比特 */ int _a = code[pos++]; (void)_a; break; }
        case 0x02: { /* QCL Y gate: no-op 单比特 */ int _a = code[pos++]; (void)_a; break; }
        default: break;
        }
    }

    printf("[QVM] 执行完成: %d 周期, %d 门操作\n", vm.cycles, vm.ops);
    free(code);
    return 0;
}
