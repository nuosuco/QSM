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

/* 高级语法操作码 — 与qcl_phase2.c严格对齐（编译器最新枚举） */
#define OP_IMPORT          100
#define OP_CONST_DEF       101
#define OP_FUNC_DEF        102
#define OP_FUNC_END        103
#define OP_TYPE_DEF        104
#define OP_TYPE_END        105
#define OP_VAR_DECL        106
#define OP_RETURN_STMT     107
#define OP_IF_STMT         108
#define OP_ELSE_STMT       109
#define OP_WHILE_STMT      110
#define OP_ASSIGN_STMT     111
#define OP_FUNC_CALL_STMT  112
#define OP_BREAK_STMT      113
#define OP_CONTINUE_STMT   114
#define OP_PUSH_CONST_INT  120
#define OP_PUSH_CONST_STR  121
#define OP_APPEND_BYTE     130
#define OP_BYTECODE_LEN    131
#define OP_EXPORT_SYM      140
#define OP_MODULE_DEF      141
/* 平台选择opcode — 经典5平台 */
#define OP_LINUX           200
#define OP_WINDOWS         201
#define OP_IOS             202
#define OP_ANDROID         203
#define OP_HARMONY         204
/* BC_FUNC_BODY/END 标记函数体字节码边界 */
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

/* 算术寄存器栈 — 用于 LOAD_REG/STORE_REG + ADD/SUB/MUL/DIV */
static int arith_stack[MAX_REGISTERS] = {0};
static int stack_top = 0;
static void stack_push(int v) { if (stack_top < MAX_REGISTERS) arith_stack[stack_top++] = v; }
static int stack_pop(void) { return stack_top > 0 ? arith_stack[--stack_top] : 0; }

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

/* 安全读取string_pool中的字符串，避免越界 */
static char *read_string(char *buf, int bufsize, uint8_t *sp_data, int sp_len, int off, int len) {
    if (!buf || bufsize <= 0 || !sp_data || sp_len <= 0) return NULL;
    if (off < 0 || len <= 0 || off + len > sp_len) return NULL;
    int safe = (len < bufsize - 1) ? len : (bufsize - 1);
    memcpy(buf, sp_data + off, safe);
    buf[safe] = '\0';
    return buf;
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
        /* 真实测量：按幅度模平方概率采样，波函数坍缩 */
        if (op1 >= n) goto end_gate;
        double prob0 = 0.0, prob1 = 0.0;
        for (int s = 0; s < size; s++) {
            if (((s >> op1) & 1) == 0) prob0 += vm->state[s].real * vm->state[s].real + vm->state[s].imag * vm->state[s].imag;
            else                       prob1 += vm->state[s].real * vm->state[s].real + vm->state[s].imag * vm->state[s].imag;
        }
        double rnd = ((double)rand() / (double)RAND_MAX) * (prob0 + prob1 + 1e-12);
        int result = (rnd < prob0) ? 0 : 1;
        if (op2 < MAX_REGISTERS) vm->registers[op2] = result;
        /* 坍缩：把非结果态的幅度清零 */
        for (int s = 0; s < size; s++) {
            if (((s >> op1) & 1) != result) { vm->state[s].real = 0.0; vm->state[s].imag = 0.0; }
        }
        printf("[QVM] 测量 q%d -> r%d = %d [坍缩 prob0=%.4f prob1=%.4f]\n", op1, op2, result, prob0, prob1);
    } else if (opcode == OP_RESET) {
        /* 真实 RESET：等同于测量+强制置|0>（已含在measure坍缩逻辑中） */
        if (op1 >= n) goto end_gate;
        for (int s = 0; s < size; s++) {
            if (((s >> op1) & 1) != 0) { vm->state[s].real = 0.0; vm->state[s].imag = 0.0; }
        }
        /* 重归一化 |0...0> 态 */
        double p = vm->state[0].real * vm->state[0].real + vm->state[0].imag * vm->state[0].imag;
        if (p > 0.0) {
            double inv = 1.0 / sqrt(p);
            for (int s = 0; s < size; s++) {
                int pair = s ^ (1 << op1);
                if (((s >> op1) & 1) == 0) { vm->state[s].real *= inv; vm->state[s].imag *= inv; }
                else { vm->state[s].real = 0.0; vm->state[s].imag = 0.0; }
            }
        }
    } else if (opcode == OP_Z) {
        /* Z = [[1,0],[0,-1]] 相位翻转 |1> */
        if (op1 >= n) goto end_gate;
        memcpy(tmp, vm->state, sizeof(complex_t) * size);
        for (int s = 0; s < size; s++) {
            if (((s >> op1) & 1) == 1) {
                tmp[s] = (complex_t){-vm->state[s].real, -vm->state[s].imag};
            }
        }
        memcpy(vm->state, tmp, sizeof(complex_t) * size);
    } else if (opcode == OP_S) {
        /* S = [[1,0],[0,i]] 相位门，|1> 乘 i */
        if (op1 >= n) goto end_gate;
        memcpy(tmp, vm->state, sizeof(complex_t) * size);
        for (int s = 0; s < size; s++) {
            if (((s >> op1) & 1) == 1) {
                double r = vm->state[s].real, im = vm->state[s].imag;
                tmp[s] = (complex_t){-im, r};   /* (r+im*i)*i = -im + ir */
            }
        }
        memcpy(vm->state, tmp, sizeof(complex_t) * size);
    } else if (opcode == OP_T) {
        /* T = [[1,0],[0,e^(i*pi/4)]] pi/8 相位门 */
        double cp = cos(M_PI / 4.0), sp = sin(M_PI / 4.0);  /* e^(i*pi/4) = (sqrt2/2) + i*(sqrt2/2) */
        if (op1 >= n) goto end_gate;
        memcpy(tmp, vm->state, sizeof(complex_t) * size);
        for (int s = 0; s < size; s++) {
            if (((s >> op1) & 1) == 1) {
                double r = vm->state[s].real, im = vm->state[s].imag;
                tmp[s] = (complex_t){r * cp - im * sp, r * sp + im * cp};
            }
        }
        memcpy(vm->state, tmp, sizeof(complex_t) * size);
    } else if (opcode == OP_Y) {
        /* Y = [[0,-i],[i,0]] 泡利Y门 */
        if (op1 >= n) goto end_gate;
        memcpy(tmp, vm->state, sizeof(complex_t) * size);
        for (int s = 0; s < size; s++) {
            if (((s >> op1) & 1) == 1) {
                int pair = s ^ (1 << op1);
                /* |1>态 -> -i*|0>态, |0>态 -> i*|1>态 */
                double r0 = vm->state[pair].real, i0 = vm->state[pair].imag;
                tmp[s] = (complex_t){i0, -r0};  /* i*(r0+i*i0) = -i0 + i*r0 */
                tmp[pair] = (complex_t){-vm->state[s].imag, vm->state[s].real};  /* -i*(rs+i*is) = is - i*rs */
            }
        }
        memcpy(vm->state, tmp, sizeof(complex_t) * size);
    } else if (opcode == OP_SWAP) {
        /* SWAP 交换两个量子比特 */
        if (op1 >= n || op2 >= n) goto end_gate;
        if (op1 == op2) goto end_gate;
        memcpy(tmp, vm->state, sizeof(complex_t) * size);
        for (int s = 0; s < size; s++) {
            int ss = s ^ (((s >> op1) & 1) << op2) ^ (((s >> op2) & 1) << op1);
            if (ss > s) {
                vm->state[s] = tmp[ss];
                vm->state[ss] = tmp[s];
            }
        }
    } else if (opcode == OP_BARRIER) {
        /* BARRIER: 同步点，强制刷新（实际模拟中为no-op） */
        fflush(stdout);
    } else if (opcode == OP_NOP) {
        /* NOP: 无操作 */
    } else if (opcode == OP_PRINT) {
        int val = (op1 < MAX_REGISTERS) ? vm->registers[op1] : 0;
        printf("[QVM] print(r%d) = %d\n", op1, val);
    } else if (opcode == OP_STOP) {
        /* STOP handled by main loop */
    } else {
        /* 兼容QCL编译器字节码：未实现opcode做no-op */
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

    int sp_len = 0;
    uint8_t *sp_data = NULL;
    int code_len = 0;
    char name[256] = {0};       /* string_pool 安全读取缓冲区 */
    /* qcl_phase2 实际输出格式: [MAGIC(0x14) | CODE(g_bc_pos bytes) | sp_len(2B LE16) | string_pool]
       通过搜索 sp_len 字段位置来确定代码区边界（sp_len 必须满足 offset+2+sp_len==fsize） */
    if (fsize > 3 && code[0] == 0x14) {
        int found = 0;
        /* 在魔数后、文件尾部之前搜索 sp_len 字段 */
        int max_search = (fsize > 5000) ? 5000 : fsize;
        for (int i = 2; i < max_search - 1; i++) {
            unsigned short spl = code[i] | (code[i + 1] << 8);
            if (i + 2 + (int)spl == fsize && spl >= 0) {
                code_len = i - 1;            /* 代码区长度 = sp_len 字段位置 - 魔数(1字节) */
                sp_data = code + i + 2;      /* string_pool 起始 */
                sp_len = fsize - (i + 2);    /* 实际 string_pool 长度 */
                found = 1;
                break;
            }
        }
        if (!found) {
            /* 搜索失败：退化为纯字节码（无 string_pool） */
            code_len = fsize - 1;
        }
    }

    QVM vm;
    vm.state = NULL;
    int pos = 1;       /* 代码区从魔数后开始（跳过0x14魔数1字节） */
    int func_nest_depth = 0;   /* OP_FUNC_DEF/END 嵌套计数器 */
    char last_func_name[128] = {0};
    int high_count = 0;        /* 高级opcode处理计数 */
    printf("[QVM] 初始化量子虚拟机\n");
    int code_end;          /* 代码区结束位置 */
    if (sp_data) {
        code_end = 1 + code_len;   /* 代码区 = [1, 1+code_len) */
        printf("[QVM] 加载QEntL字节码: code_len=%d, sp_len=%d, 代码区起始=1, string_pool起始=%d\n",
               code_len, sp_len, 1+code_len+2);
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
        case OP_Z:  { int q = code[pos++]; apply_gate(&vm, OP_Z, q, 0);
                      printf("[QVM] Z(q%d)\n", q); break; }
        case OP_S:  { int q = code[pos++]; apply_gate(&vm, OP_S, q, 0);
                      printf("[QVM] S(q%d)\n", q); break; }
        case OP_T:  { int q = code[pos++]; apply_gate(&vm, OP_T, q, 0);
                      printf("[QVM] T(q%d)\n", q); break; }
        case OP_Y:  { int q = code[pos++]; apply_gate(&vm, OP_Y, q, 0);
                      printf("[QVM] Y(q%d)\n", q); break; }
        case OP_RESET: { int q = code[pos++]; apply_gate(&vm, OP_RESET, q, 0);
                         printf("[QVM] RESET(q%d)\n", q); break; }
        case OP_SWAP: { int a = code[pos++], b = code[pos++];
                        apply_gate(&vm, OP_SWAP, a, b);
                        printf("[QVM] SWAP(q%d, q%d)\n", a, b); break; }
        case OP_BARRIER: {
                         printf("[QVM] BARRIER\n"); break; }
        case OP_NOP: {
                      printf("[QVM] NOP\n"); break; }
        case OP_LOAD_REG: { int r = code[pos++];
                            int val = (r < MAX_REGISTERS) ? vm.registers[r] : 0;
                            stack_push(val);
                            printf("[QVM] LOAD_REG r%d -> stack=%d\n", r, val); break; }
        case OP_STORE_REG: { int r = code[pos++];
                             if (r < MAX_REGISTERS) vm.registers[r] = stack_pop();
                             printf("[QVM] STORE_REG stack -> r%d\n", r); break; }
        case OP_ADD: { int b = stack_pop(), a = stack_pop();
                       stack_push(a + b);
                       printf("[QVM] ADD(%d + %d = %d)\n", a, b, a + b); break; }
        case OP_SUB: { int b = stack_pop(), a = stack_pop();
                       stack_push(a - b);
                       printf("[QVM] SUB(%d - %d = %d)\n", a, b, a - b); break; }
        case OP_MUL: { int b = stack_pop(), a = stack_pop();
                       stack_push(a * b);
                       printf("[QVM] MUL(%d * %d = %d)\n", a, b, a * b); break; }
        case OP_DIV: { int b = stack_pop(), a = stack_pop();
                       int res = (b != 0) ? a / b : 0;
                       stack_push(res);
                       printf("[QVM] DIV(%d / %d = %d)\n", a, b, res); break; }
        case OP_JUMP: { int tgt = (int)(code[pos] | (code[pos+1] << 8)); pos += 2;
                        printf("[QVM] JUMP to %d\n", tgt); break; }
        case OP_EXIT: {
                       printf("[QVM] EXIT\n");
                       free(code); if (vm.state) free(vm.state); return 0; }
        /* ---------- 高级语法opcode（100+）: 与qcl_phase2.c严格对齐 ---------- */
        case OP_IMPORT: {
            if (pos + 3 < fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int len = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                char *n = read_string(name, sizeof(name), sp_data, sp_len, off, len);
                printf("[QVM] OP_IMPORT(%s)\n", n ? n : "(invalid)");
                high_count++;
            }
            break;
        }
        case OP_CONST_DEF: {
            if (pos + 4 < fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int len = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                int sval = 0;
                if (pos + 1 < fsize) { sval = code[pos] | (code[pos+1] << 8); pos += 2; }
                char *n = read_string(name, sizeof(name), sp_data, sp_len, off, len);
                printf("[QVM] OP_CONST_DEF(%s = %d)\n", n ? n : "(invalid)", sval);
                high_count++;
            }
            break;
        }
        case OP_FUNC_DEF: {
            int nest = func_nest_depth;
            int off = 0, flen = 0, nargs = 0;
            if (pos + 4 < fsize) {
                off = code[pos] | (code[pos+1] << 8);
                flen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
            }
            if (pos < fsize) nargs = code[pos++];
            char *n = read_string(name, sizeof(name), sp_data, sp_len, off, flen);
            printf("[QVM] OP_FUNC_DEF(%s, nargs=%d) depth=%d\n",
                   n ? n : "(unknown)", nargs, nest);
            func_nest_depth++;
            strncpy(last_func_name, name, sizeof(last_func_name) - 1);
            high_count++;
            break;
        }
        case OP_FUNC_END: {
            func_nest_depth--;
            printf("[QVM] OP_FUNC_END(%s) depth=%d %s\n",
                   last_func_name[0] ? last_func_name : "(unknown)",
                   func_nest_depth, func_nest_depth < 0 ? "!!! 不匹配" : "");
            high_count++;
            break;
        }
        case OP_TYPE_DEF: {
            if (pos + 3 < fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int tlen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                char *n = read_string(name, sizeof(name), sp_data, sp_len, off, tlen);
                printf("[QVM] OP_TYPE_DEF(%s)\n", n ? n : "(invalid)");
                high_count++;
            }
            break;
        }
        case OP_TYPE_END: {
            printf("[QVM] OP_TYPE_END\n");
            high_count++;
            break;
        }
        case OP_VAR_DECL: {
            if (pos + 3 < fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int vlen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                char *n = read_string(name, sizeof(name), sp_data, sp_len, off, vlen);
                printf("[QVM] OP_VAR_DECL(%s)\n", n ? n : "(invalid)");
                high_count++;
            }
            break;
        }
        case OP_RETURN_STMT: {
            int rt = 0;
            if (pos < fsize) rt = code[pos++];
            printf("[QVM] OP_RETURN_STMT(kind=%d)\n", rt);
            high_count++;
            break;
        }
        case OP_IF_STMT: {
            printf("[QVM] OP_IF_STMT (条件跳过后置代码)\n");
            high_count++;
            break;
        }
        case OP_ELSE_STMT: {
            printf("[QVM] OP_ELSE_STMT\n");
            high_count++;
            break;
        }
        case OP_WHILE_STMT: {
            printf("[QVM] OP_WHILE_STMT (循环体)\n");
            high_count++;
            break;
        }
        case OP_ASSIGN_STMT: {
            if (pos + 3 < fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int vlen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                char *n = read_string(name, sizeof(name), sp_data, sp_len, off, vlen);
                printf("[QVM] OP_ASSIGN_STMT(%s = ...)\n", n ? n : "(invalid)");
                high_count++;
            }
            break;
        }
        case OP_FUNC_CALL_STMT: {
            int off = 0, flen = 0, nargs = 0;
            if (pos + 4 < fsize) {
                off = code[pos] | (code[pos+1] << 8);
                flen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
            }
            if (pos < fsize) nargs = code[pos++];
            char *n = read_string(name, sizeof(name), sp_data, sp_len, off, flen);
            printf("[QVM] OP_FUNC_CALL_STMT(%s, nargs=%d)\n", n ? n : "(unknown)", nargs);
            high_count++;
            break;
        }
        case OP_BREAK_STMT: {
            printf("[QVM] OP_BREAK_STMT\n");
            high_count++;
            break;
        }
        case OP_CONTINUE_STMT: {
            printf("[QVM] OP_CONTINUE_STMT\n");
            high_count++;
            break;
        }
        case OP_PUSH_CONST_INT: {
            int v = 0;
            if (pos < fsize) v = code[pos++];
            if (pos < fsize) v |= code[pos++] << 8;
            printf("[QVM] OP_PUSH_CONST_INT(%d)\n", v);
            high_count++;
            break;
        }
        case OP_PUSH_CONST_STR: {
            if (pos < fsize) {
                uint16_t slen = 0;
                if (pos < fsize) slen = code[pos++];
                if (pos < fsize) slen |= (uint16_t)code[pos++] << 8;
                if (pos + slen <= fsize) pos += slen;
                printf("[QVM] OP_PUSH_CONST_STR(%d B)\n", slen);
                high_count++;
            }
            break;
        }
        case OP_APPEND_BYTE: {
            int b = 0;
            if (pos < fsize) b = code[pos++];
            printf("[QVM] OP_APPEND_BYTE(%d)\n", b);
            high_count++;
            break;
        }
        case OP_BYTECODE_LEN: {
            int bclen = 0;
            if (pos + 1 < fsize) bclen = code[pos] | (code[pos+1] << 8);
            if (pos + 1 < fsize) pos += 2;
            printf("[QVM] OP_BYTECODE_LEN(%d)\n", bclen);
            high_count++;
            break;
        }
        case OP_EXPORT_SYM: {
            if (pos + 3 < fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int slen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                char *n = read_string(name, sizeof(name), sp_data, sp_len, off, slen);
                printf("[QVM] OP_EXPORT_SYM(%s)\n", n ? n : "(invalid)");
                high_count++;
            }
            break;
        }
        case OP_MODULE_DEF: {
            if (pos + 3 < fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int mlen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                char *n = read_string(name, sizeof(name), sp_data, sp_len, off, mlen);
                printf("[QVM] OP_MODULE_DEF(%s)\n", n ? n : "(invalid)");
                high_count++;
            }
            break;
        }
        /* ---------- 平台选择opcode（200+） ---------- */
        case OP_LINUX: {
            printf("[QVM] OP_LINUX (平台: Linux ELF)\n");
            high_count++;
            break;
        }
        case OP_WINDOWS: {
            printf("[QVM] OP_WINDOWS (平台: Windows PE)\n");
            high_count++;
            break;
        }
        case OP_IOS: {
            printf("[QVM] OP_IOS (平台: iOS Mach-O)\n");
            high_count++;
            break;
        }
        case OP_ANDROID: {
            printf("[QVM] OP_ANDROID (平台: Android ELF)\n");
            high_count++;
            break;
        }
        case OP_HARMONY: {
            printf("[QVM] OP_HARMONY (平台: 鸿蒙 ELF/ARM)\n");
            high_count++;
            break;
        }
        case BC_FUNC_BODY: {
            printf("[QVM] BC_FUNC_BODY (函数体开始)\n");
            high_count++;
            break;
        }
        case BC_FUNC_END: {
            printf("[QVM] BC_FUNC_END (函数体结束)\n");
            high_count++;
            break;
        }
        default:
            printf("[QVM] 未知opcode: 0x%02x (pos=%d)\n", op, pos - 1);
            break;
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
