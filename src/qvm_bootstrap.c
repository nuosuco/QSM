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
#define FUNC_DEF_NEST_MAX 16

/* 高级语法操作码 — 与qcl_phase2.c对齐（100+） */
#define OP_IMPORT          100
#define OP_CONST_DEF       101
#define OP_FUNC_DEF        102
#define OP_FUNC_END        103
#define OP_TYPE_DEF        104
#define OP_VAR_DECL        105
#define OP_RETURN_STMT     106
#define OP_IF_STMT         108
#define OP_WHILE_STMT      109
#define OP_ELSE_STMT       110
#define OP_BREAK_STMT      111
#define OP_CONTINUE_STMT   112
#define OP_ASSIGN          113
#define OP_FUNC_CALL       114
#define OP_PUSH_CONST_INT  120
#define OP_PUSH_CONST_STR  121
#define OP_NEW_OBJECT      122
#define OP_LENGTH          123
#define OP_RANDOM          124
#define OP_EXPORT_SYM      140
#define BC_FUNC_BODY       255
#define BC_FUNC_END        254

/* 操作码 — 与qcl_bootstrap.c编译器严格对齐 */
enum {
    OP_NOP = 0,
    OP_H = 1,
    OP_X = 2,
    OP_Z = 3,
    OP_CNOT = 4,
    OP_MEASURE = 5,
    OP_RESET = 6,
    OP_SWAP = 7,
    OP_LOAD_REG = 8,    // 编译器OP_LOAD_REG=8
    OP_STORE_REG = 9,   // 编译器OP_STORE_REG=9
    OP_JUMP = 10,
    OP_PRINT = 11,
    OP_STOP = 12,
    OP_SUB = 13,
    OP_DIV = 14,
    OP_MUL = 15,
    OP_ADD = 16,
    OP_EXIT = 17,
    OP_BARRIER = 18,
    OP_INIT_N = 20,     // 编译器OP_INIT_N=20
    OP_T = 35,
    OP_S = 36,
    OP_Y = 37,
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
        printf("[QVM] 量子比特数=%d，使用简化模拟模式（不展开完整态矢量）\n", n);
    } else {
        vm->state = (complex_t *)calloc(size, sizeof(complex_t));
        if (vm->state) {
            vm->state[0].real = 1.0;
            vm->state[0].imag = 0.0;
        } else {
            printf("[QVM] 警告: 内存不足，使用简化模拟模式\n");
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

    /* 解析QEntL字节码头: [0]=0x14魔数, [1:3]=代码长度(le16), [3:3+code_len]=代码区, [3+code_len:3+code_len+2]=string_pool长度(声明值), [3+code_len+2:]=string_pool */
    int sp_len = 0;
    uint8_t *sp_data = NULL;
    int code_len = 0;
    if (fsize > 3 && code[0] == 0x14) {
        code_len = code[1] | (code[2] << 8);
        if (3 + code_len + 2 <= fsize) {
            unsigned short spl = code[3 + code_len] | (code[3 + code_len + 1] << 8);
            sp_data = code + 3 + code_len + 2;
            /* 声明的spl可能因编译器g_strpool_pos溢出而错误，用实际可用空间 */
            int actual = fsize - (3 + code_len + 2);
            sp_len = (spl < actual) ? spl : actual;
        }
    }

    QVM vm;
    vm.state = NULL;
    int pos = 3;       /* 代码区始终从偏移3开始（跳过头部魔数+长度） */
    int func_nest_depth = 0;   /* OP_FUNC_DEF/END 嵌套计数器 */
    char last_func_name[128] = {0};
    int high_count = 0;        /* 高级opcode处理计数 */
    printf("[QVM] 初始化量子虚拟机\n");
    int code_end;          /* 代码区结束位置 */
    if (sp_data) {
        code_end = 3 + code_len;
        printf("[QVM] 加载QEntL字节码: code_len=%d, sp_len=%d, 代码区起始=3, string_pool起始=%d\n", code_len, sp_len, 3+code_len+2);
    } else {
        code_end = fsize;          /* 无头部时执行整个文件 */
        pos = 0;
    }
    while (pos < code_end) {
        uint8_t op = code[pos++];
        if (op == OP_INIT_N) {
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
        case OP_INIT_N: {
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
        case 0x15: { // QCL编译器STOP兼容
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
        case OP_Z:  { int q = code[pos++]; (void)q; break; }
        case OP_T:  { int q = code[pos++]; (void)q; break; }
        case OP_S:  { int q = code[pos++]; (void)q; break; }
        case OP_RESET: { int q = code[pos++]; (void)q; break; }
        case OP_SWAP: { int a = code[pos++], b = code[pos++]; (void)a; (void)b; break; }
        /* ---------- 高级语法opcode（100+）: 为QEntL环境铺垫 ---------- */
        case OP_IMPORT: {
            /* 格式: u16(string_pool_offset) + u16(length) */
            if (pos + 3 <= fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int len = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                if (sp_data && off + len <= sp_len && off + len <= fsize - (3 + code_len + 2)) {
                    char name[256] = {0};
                    int safe_len = (len < 255) ? len : 255;
                    memcpy(name, sp_data + off, safe_len);
                    printf("[QVM] 高级opcode: OP_IMPORT(name=\"%s\")\n", name);
                } else {
                    printf("[QVM] 高级opcode: OP_IMPORT (off=%d, len=%d) [string_pool不可用]\n", off, len);
                }
                high_count++;
            }
            break;
        }
        case OP_CONST_DEF: {
            /* 格式: u16(string_pool_offset) + u16(length) + u16(value) */
            if (pos + 4 <= fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int len = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                int sval = 0;
                if (pos + 1 < fsize) { sval = code[pos] | (code[pos+1] << 8); pos += 2; }
                char name[128] = {0};
                if (sp_data && off + len <= sp_len && len < 127) {
                    memcpy(name, sp_data + off, len); name[len] = 0;
                    printf("[QVM] 高级opcode: OP_CONST_DEF(name=\"%s\", value=%d)\n", name, sval);
                } else {
                    printf("[QVM] 高级opcode: OP_CONST_DEF (off=%d, len=%d, value=%d)\n", off, len, sval);
                }
                high_count++;
            }
            break;
        }
        case OP_FUNC_DEF: {
            int nest = func_nest_depth;
            char fn[128] = {0};
            int off = 0, flen = 0, nargs = 0;
            /* 字节码格式: u16(string_pool_offset) + u16(flen) + u8(nargs) */
            if (pos + 4 <= fsize) {
                off = code[pos] | (code[pos+1] << 8);
                flen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
            }
            if (pos < fsize) nargs = code[pos++];
            /* 读取 string pool 中的函数名 */
            if (sp_data && off + flen <= sp_len && flen > 0 && flen < 128) {
                memcpy(fn, sp_data + off, flen); fn[flen] = 0;
            }
            printf("[QVM] 高级opcode: OP_FUNC_DEF(%s, nargs=%d) depth=%d\n",
                   fn[0] ? fn : "(unknown)", nargs, nest);
            func_nest_depth++;
            strncpy(last_func_name, fn, sizeof(last_func_name) - 1);
            high_count++;
            break;
        }
        case OP_FUNC_END: {
            func_nest_depth--;
            printf("[QVM] 高级opcode: OP_FUNC_END(%s) depth=%d %s\n",
                   last_func_name[0] ? last_func_name : "(unknown)",
                   func_nest_depth < 0 ? -1 : func_nest_depth,
                   func_nest_depth < 0 ? "!!! 不匹配: FUNC_END 多余" : "");
            high_count++;
            break;
        }
        case OP_TYPE_DEF: {
            if (pos + 3 <= fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int tlen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                char name[128] = {0};
                if (sp_data && off + tlen <= sp_len && tlen < 127) {
                    memcpy(name, sp_data + off, tlen); name[tlen] = 0;
                    printf("[QVM] 高级opcode: OP_TYPE_DEF(name=\"%s\")\n", name);
                } else {
                    printf("[QVM] 高级opcode: OP_TYPE_DEF (off=%d, len=%d)\n", off, tlen);
                }
                high_count++;
            }
            break;
        }
        case OP_VAR_DECL: {
            if (pos + 3 <= fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int vlen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                char name[128] = {0};
                if (sp_data && off + vlen <= sp_len && vlen < 127) {
                    memcpy(name, sp_data + off, vlen); name[vlen] = 0;
                    printf("[QVM] 高级opcode: OP_VAR_DECL(var=\"%s\")\n", name);
                } else {
                    printf("[QVM] 高级opcode: OP_VAR_DECL (off=%d, len=%d)\n", off, vlen);
                }
                high_count++;
            }
            break;
        }
        case OP_RETURN_STMT: {
            if (pos < fsize) { int rt = code[pos++];
                printf("[QVM] 高级opcode: OP_RETURN_STMT(kind=%d)\n", rt);
                high_count++;
            }
            break;
        }
        case OP_IF_STMT: {
            printf("[QVM] 高级opcode: OP_IF_STMT (skip body)\n");
            high_count++;
            break;
        }
        case OP_WHILE_STMT: {
            printf("[QVM] 高级opcode: OP_WHILE_STMT (skip body)\n");
            high_count++;
            break;
        }
        case OP_ELSE_STMT: {
            printf("[QVM] 高级opcode: OP_ELSE_STMT (skip body)\n");
            high_count++;
            break;
        }
        case OP_BREAK_STMT: {
            printf("[QVM] 高级opcode: OP_BREAK_STMT\n");
            high_count++;
            break;
        }
        case OP_CONTINUE_STMT: {
            printf("[QVM] 高级opcode: OP_CONTINUE_STMT\n");
            high_count++;
            break;
        }
        case OP_ASSIGN: {
            if (pos + 3 <= fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int vlen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                char name[128] = {0};
                if (sp_data && off + vlen <= sp_len && vlen < 127) {
                    memcpy(name, sp_data + off, vlen); name[vlen] = 0;
                    printf("[QVM] 高级opcode: OP_ASSIGN(var=\"%s\")\n", name);
                } else {
                    printf("[QVM] 高级opcode: OP_ASSIGN (off=%d, len=%d)\n", off, vlen);
                }
                high_count++;
            }
            break;
        }
        case OP_FUNC_CALL: {
            int off = 0, flen = 0, nargs = 0;
            if (pos + 4 <= fsize) {
                off = code[pos] | (code[pos+1] << 8);
                flen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
            }
            if (pos < fsize) nargs = code[pos++];
            char fn[128] = {0};
            if (sp_data && off + flen <= sp_len && flen > 0 && flen < 128) {
                memcpy(fn, sp_data + off, flen); fn[flen] = 0;
            }
            printf("[QVM] 高级opcode: OP_FUNC_CALL(%s, nargs=%d)\n", fn[0] ? fn : "(unknown)", nargs);
            high_count++;
            break;
        }
        case OP_PUSH_CONST_INT: {
            int v = 0;
            if (pos < fsize) v = code[pos++];
            if (pos < fsize) v |= code[pos++] << 8;
            printf("[QVM] 高级opcode: OP_PUSH_CONST_INT(%d)\n", v);
            high_count++;
            break;
        }
        case OP_PUSH_CONST_STR: {
            if (pos < fsize) { int s1 = code[pos++];
                if (pos < fsize) { int slen = code[pos++] | ((s1 & 0xFF) << 8);
                    printf("[QVM] 高级opcode: OP_PUSH_CONST_STR(skip %d B)\n", slen + 2);
                    high_count++;
                }}
            break;
        }
        case OP_NEW_OBJECT: {
            printf("[QVM] 高级opcode: OP_NEW_OBJECT (skip)\n");
            high_count++;
            break;
        }
        case OP_LENGTH: {
            printf("[QVM] 高级opcode: OP_LENGTH (skip)\n");
            high_count++;
            break;
        }
        case OP_RANDOM: {
            printf("[QVM] 高级opcode: OP_RANDOM (skip)\n");
            high_count++;
            break;
        }
        case OP_EXPORT_SYM: {
            if (pos + 3 <= fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int slen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                char name[128] = {0};
                if (sp_data && off + slen <= sp_len && slen < 127) {
                    memcpy(name, sp_data + off, slen); name[slen] = 0;
                    printf("[QVM] 高级opcode: OP_EXPORT_SYM(name=\"%s\")\n", name);
                } else {
                    printf("[QVM] 高级opcode: OP_EXPORT_SYM (off=%d, len=%d)\n", off, slen);
                }
                high_count++;
            }
            break;
        }
        case BC_FUNC_BODY: {
            printf("[QVM] 高级opcode: BC_FUNC_BODY (函数体开始)\n");
            high_count++;
            break;
        }
        case BC_FUNC_END: {
            printf("[QVM] 高级opcode: BC_FUNC_END (函数体结束)\n");
            high_count++;
            break;
        }
        default: break;
        }
    }

    if (func_nest_depth != 0) {
        printf("[QVM] 警告: FUNC_DEF/END 不匹配 (depth=%d, 应有0)\n", func_nest_depth);
    }
    printf("[QVM] 高级opcode处理总数: %d\n", high_count);

    printf("[QVM] 执行完成: %d 周期, %d 门操作\n", vm.cycles, vm.ops);
    free(code);
    return 0;
}
