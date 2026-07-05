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
#define MAX_FUNCS 256
#define MAX_VARIABLES 512
#define CALL_STACK_MAX 128
#define LOOP_STACK_MAX 64

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

/* ========== 高级语法执行引擎数据结构 ========== */

/* 函数表：存储已解析的函数定义（名称、起始pos、参数数） */
typedef struct {
    char name[128];
    int start_pos;
    int end_pos;      /* OP_FUNC_END 的 pos */
    int nargs;
} FuncDef;
static FuncDef func_table[MAX_FUNCS];
static int func_count = 0;

/* 变量表：变量名 -> 整数值 */
typedef struct {
    char name[128];
    int value;
} Variable;
static Variable var_table[MAX_VARIABLES];
static int var_count = 0;

/* 函数调用栈：每层保存返回地址 */
typedef struct {
    int return_pos;       /* 函数返回后继续执行的位置 */
    int nargs;            /* 本次调用实参个数（可选） */
    int ret_addr_value;   /* 函数返回值 */
} CallFrame;
static CallFrame call_stack[CALL_STACK_MAX];
static int call_depth = 0;
static int return_value = 0;   /* 最近一次 return 的值 */
static int in_return = 0;      /* 刚执行 return，需要弹出调用帧 */

/* 循环栈：每层 while 循环保存循环体起始位置和条件值 */
typedef struct {
    int body_start;       /* while 循环体第一条指令的 pos */
    int body_end;         /* while 循环体结束位置（下一指令） */
    int condition;        /* 循环条件值（简化：非0继续） */
} LoopFrame;
static LoopFrame loop_stack[LOOP_STACK_MAX];
static int loop_depth = 0;

/* 字符串常量暂存区 */
static char str_const_buf[4096];
static int str_const_count = 0;

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

/* 安全读取string_pool中的字符串，避免越界 */
static char *read_string(char *buf, int bufsize, uint8_t *sp_data, int sp_len, int off, int len) {
    if (!buf || bufsize <= 0 || !sp_data || sp_len <= 0) return NULL;
    if (off < 0 || len <= 0 || off + len > sp_len) return NULL;
    int safe = (len < bufsize - 1) ? len : (bufsize - 1);
    memcpy(buf, sp_data + off, safe);
    buf[safe] = '\0';
    return buf;
}

/* ========== 高级语法辅助函数 ========== */

/* 查找变量，不存在返回 -1 */
static int var_find(const char *name) {
    for (int i = 0; i < var_count; i++) {
        if (strcmp(var_table[i].name, name) == 0) return i;
    }
    return -1;
}

/* 获取/创建变量的值 */
static int var_get(const char *name) {
    int idx = var_find(name);
    if (idx >= 0) return var_table[idx].value;
    return 0;
}

/* 设置变量值 */
static void var_set(const char *name, int value) {
    int idx = var_find(name);
    if (idx >= 0) {
        var_table[idx].value = value;
        return;
    }
    /* 新建变量 */
    if (var_count >= MAX_VARIABLES) return;
    strncpy(var_table[var_count].name, name, sizeof(var_table[var_count].name) - 1);
    var_table[var_count].name[sizeof(var_table[var_count].name) - 1] = '\0';
    var_table[var_count].value = value;
    var_count++;
}

/* 查找函数定义，不存在返回 -1 */
static int func_find(const char *name) {
    for (int i = 0; i < func_count; i++) {
        if (strcmp(func_table[i].name, name) == 0) return i;
    }
    return -1;
}

/* 扫描并定位 compound block 的结束位置
   在 pos 处开始，遇到与当前深度匹配的 OP_IF_STMT/OP_WHILE_STMT/OP_FUNC_DEF 时 depth++，
   遇到对应的 END 时 depth--。
   对于 IF_STMT：block 在遇到 OP_ELSE_STMT 或外层指令时结束
   对于 WHILE_STMT：block 在遇到同深度下一条指令时结束（通常由编译器确保边界）
   对于 FUNC_BODY：block 在遇到 BC_FUNC_END 时结束
*/
static int find_block_end(const uint8_t *code, int code_end, int pos, int mode) {
    /* mode: 1=if_body, 2=while_body, 3=func_body */
    int depth = 0;
    while (pos < code_end) {
        uint8_t op = code[pos];
        if (op == OP_IF_STMT || op == OP_WHILE_STMT || op == OP_FUNC_DEF) {
            depth++;
            pos++;
        } else if (op == OP_ELSE_STMT && mode == 1 && depth == 0) {
            return pos;  /* IF body 结束于 ELSE */
        } else if (op == OP_FUNC_END && mode == 3 && depth == 0) {
            return pos;  /* 函数体结束于 FUNC_END（由FUNC_DEF解析处理） */
        } else if (op == BC_FUNC_END && mode == 3 && depth == 0) {
            return pos;  /* func body 结束于 BC_FUNC_END */
        } else if (op == OP_FUNC_END && depth > 0) {
            depth--;
            pos++;
        } else {
            pos++;
        }
    }
    return pos;  /* 扫描到末尾 */
}

/* 前向扫描：定位 IF body 结束位置（OP_ELSE_STMT 或下一条同层级指令） */
static int find_if_else_end(const uint8_t *code, int code_end, int pos) {
    int depth = 0;
    while (pos < code_end) {
        uint8_t op = code[pos];
        if (op == OP_IF_STMT || op == OP_WHILE_STMT || op == OP_FUNC_DEF || op == OP_FUNC_END) {
            depth++;
            pos++;
        } else if (op == OP_ELSE_STMT && depth == 0) {
            return pos;  /* 遇到 ELSE */
        } else if ((op == OP_RETURN_STMT || op == OP_IF_STMT || op == OP_WHILE_STMT ||
                    op == OP_FUNC_DEF || op == OP_FUNC_CALL_STMT || op == OP_ASSIGN_STMT ||
                    op == OP_VAR_DECL || op == OP_STOP || op == OP_EXIT) && depth == 0) {
            /* 同层级的下一条语句 — IF body 结束（无 else） */
            return pos;
        } else if (op == OP_FUNC_END && depth > 0) {
            depth--;
            pos++;
        } else {
            pos++;
        }
    }
    return pos;
}

/* 前向扫描：定位 WHILE body 结束位置（下一条同层级指令） */
static int find_while_body_end(const uint8_t *code, int code_end, int pos) {
    int depth = 0;
    while (pos < code_end) {
        uint8_t op = code[pos];
        if (op == OP_IF_STMT || op == OP_WHILE_STMT || op == OP_FUNC_DEF || op == OP_FUNC_END) {
            depth++;
            pos++;
        } else if (op == OP_BREAK_STMT && depth == 0) {
            /* break 是 body 内的一部分，跳过 */
            pos++;
        } else if ((op == OP_RETURN_STMT || op == OP_IF_STMT || op == OP_WHILE_STMT ||
                    op == OP_FUNC_DEF || op == OP_FUNC_CALL_STMT || op == OP_ASSIGN_STMT ||
                    op == OP_VAR_DECL || op == OP_STOP || op == OP_EXIT || op == OP_ELSE_STMT) && depth == 0) {
            /* 同层级的下一条语句 — while body 结束 */
            return pos;
        } else if (op == OP_FUNC_END && depth > 0) {
            depth--;
            pos++;
        } else {
            pos++;
        }
    }
    return pos;
}

/* 调用函数：在函数表中找到函数并跳转到其 start_pos 执行 */
static int call_function(uint8_t *code, int code_end, const char *name, int nargs, int *sp_data_ptr, int sp_len) {
    int fidx = func_find(name);
    if (fidx < 0) {
        printf("[QVM] 警告: 未找到函数 '%s'，跳过调用\n", name);
        return -1;
    }
    if (call_depth >= CALL_STACK_MAX) {
        printf("[QVM] 错误: 调用栈溢出 (depth=%d)\n", call_depth);
        return -1;
    }
    return func_table[fidx].start_pos;
}

/* 读取一个 uint16 值 */
static uint16_t read_u16(const uint8_t *code, int pos) {
    return (uint16_t)(code[pos] | (code[pos + 1] << 8));
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
        /* 真实 RESET：等同于测量+强制置|0> */
        if (op1 >= n) goto end_gate;
        double p = vm->state[0].real * vm->state[0].real + vm->state[0].imag * vm->state[0].imag;
        if (p > 0.0) {
            double inv = 1.0 / sqrt(p);
            for (int s = 0; s < size; s++) {
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
    /* D-001 修复：显式文件头标记，替代脆弱的等式反推搜索
       新格式: [0x14 | 0x00 | 0x00 | 0x00 | code_len(LE16) | CODE(code_len bytes) | sp_len(LE16) | string_pool]
       标记 = "QVML"(0x14 0x00 0x00 0x00)，搜索范围覆盖整个 code 区(最多 fsize-4)，
       并校验 code_len + header_size + sp_len == fsize，防止误判。 */
    if (fsize >= 6) {
        int found = 0;
        /* 在整个 code 区内搜索显式标记头 */
        int max_search = (int)fsize - 4;  /* 需要至少 code_len(2B)+sp_len(2B) */
        if (max_search < 4) max_search = (int)fsize;
        for (int i = 0; i < max_search - 3; i++) {
            /* 检测标记: 0x14 0x00 0x00 0x00 */
            if (code[i] == 0x14 && code[i + 1] == 0x00 &&
                code[i + 2] == 0x00 && code[i + 3] == 0x00) {
                int hdr = i + 4;            /* code_len 字段起始 */
                if (hdr + 2 > (int)fsize) break;
                int c_len = code[hdr] | (code[hdr + 1] << 8);
                int sp_hdr = hdr + 2 + c_len;  /* sp_len 字段起始 */
                if (sp_hdr + 2 > (int)fsize) break;
                int s_len = code[sp_hdr] | (code[sp_hdr + 1] << 8);
                int sp_start = sp_hdr + 2;
                /* 额外校验: code_len + header(6B) + sp_len == fsize */
                if (sp_start + s_len == (int)fsize && c_len >= 0 && s_len >= 0) {
                    code_len = c_len;
                    sp_data = code + sp_start;
                    sp_len = s_len;
                    found = 1;
                    break;
                }
            }
        }
        if (!found) {
            /* 无显式标记：退化为纯字节码（无 string_pool） */
            code_len = fsize;
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
        /* 循环重入检查：如果 pos 进入活跃循环的 body_end 区域，重新评估条件 */
        if (loop_depth > 0) {
            LoopFrame *lf = &loop_stack[loop_depth - 1];
            if (pos >= lf->body_end && pos <= lf->body_end + 1) {
                printf("[QVM] WHILE 循环到达 body_end=%d, 重新评估条件\n", lf->body_end);
                int cond = lf->condition;  /* 使用 WHILE_STMT 时设置的条件 */
                if (stack_top > 0) cond = stack_pop();  /* 优先用栈顶 */
                printf("[QVM] WHILE 循环条件: cond=%d\n", cond);
                if (cond != 0) {
                    printf("[QVM] 条件为真，跳回循环体开始 pos=%d\n", lf->body_start);
                    pos = lf->body_start;
                } else {
                    printf("[QVM] 条件为假，退出循环\n");
                    loop_depth--;
                }
            }
        }
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
            /* 只在顶层（depth==0）注册函数，嵌套 def 只是语法标记 */
            if (nest == 0) {
                if (func_count < MAX_FUNCS) {
                    strncpy(func_table[func_count].name, name, sizeof(func_table[func_count].name) - 1);
                    func_table[func_count].name[sizeof(func_table[func_count].name) - 1] = '\0';
                    func_table[func_count].start_pos = pos;  /* 函数体从下一条指令开始 */
                    func_table[func_count].nargs = nargs;
                    func_count++;
                }
            }
            func_nest_depth++;
            strncpy(last_func_name, name, sizeof(last_func_name) - 1);
            last_func_name[sizeof(last_func_name) - 1] = '\0';
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
                /* 初始化变量为 0（如果不存在则创建） */
                if (n) var_set(n, 0);
                printf("[QVM] OP_VAR_DECL(%s)\n", n ? n : "(invalid)");
                high_count++;
            }
            break;
        }
        case OP_RETURN_STMT: {
            int rt = 0;
            int save_ret = 0;
            if (pos < fsize) rt = code[pos++];
            printf("[QVM] OP_RETURN_STMT(kind=%d)\n", rt);
            /* 从函数返回：弹出调用帧，跳到返回地址 */
            if (rt == 0 && call_depth > 0) {
                /* return; 无返回值 */
                CallFrame *cf = &call_stack[--call_depth];
                int ret = cf->ret_addr_value;
                return_value = ret;
                printf("[QVM] return; -> 返回地址=%d, return_value=%d\n", cf->return_pos, ret);
                pos = cf->return_pos;
                continue;
            } else if (rt == 1 && call_depth > 0) {
                /* return var; 返回变量值 */
                int off = 0, vlen = 0;
                if (pos + 3 < fsize) {
                    off = code[pos] | (code[pos+1] << 8);
                    vlen = code[pos+2] | (code[pos+3] << 8);
                    pos += 4;
                }
                char *vn = read_string(name, sizeof(name), sp_data, sp_len, off, vlen);
                int v = vn ? var_get(vn) : 0;
                CallFrame *cf = &call_stack[--call_depth];
                return_value = v;
                printf("[QVM] return %s = %d -> 返回地址=%d\n", vn ? vn : "(null)", v, cf->return_pos);
                pos = cf->return_pos;
                continue;
            } else if (rt == 2 && call_depth > 0) {
                /* return number; 返回整数值 */
                int val = 0;
                if (pos + 1 < fsize) { val = read_u16(code, pos); pos += 2; }
                CallFrame *cf = &call_stack[--call_depth];
                return_value = val;
                printf("[QVM] return %d -> 返回地址=%d\n", val, cf->return_pos);
                pos = cf->return_pos;
                continue;
            } else if (rt == 3 && call_depth > 0) {
                /* return string; 跳过字符串，返回空 */
                int off = 0, vlen = 0;
                if (pos + 3 < fsize) {
                    off = code[pos] | (code[pos+1] << 8);
                    vlen = code[pos+2] | (code[pos+3] << 8);
                    pos += 4;
                }
                char *vn = read_string(name, sizeof(name), sp_data, sp_len, off, vlen);
                CallFrame *cf = &call_stack[--call_depth];
                return_value = 0;
                printf("[QVM] return \"%s\" -> 返回地址=%d\n", vn ? vn : "(null)", cf->return_pos);
                pos = cf->return_pos;
                continue;
            } else if (call_depth <= 0) {
                /* 在顶层 return = 退出程序 */
                printf("[QVM] 顶层 return，退出程序\n");
                free(code); if (vm.state) free(vm.state); return 0;
            }
            break;
        }
        case OP_IF_STMT: {
            int cond = 0;
            if (stack_top > 0) cond = stack_pop();
            int if_end = find_if_else_end(code, code_end, pos);
            int has_else = (if_end < code_end && code[if_end] == OP_ELSE_STMT);
            int else_end = has_else ? find_if_else_end(code, code_end, if_end + 1) : if_end;
            printf("[QVM] OP_IF_STMT cond=%d if_body=[%d,%d) else=%d else_end=%d\n",
                   cond, pos, if_end, has_else, else_end);
            if (cond != 0) {
                printf("[QVM] IF 真，执行 IF body [%d -> %d)\n", pos, if_end);
                if (if_end < code_end) {
                    while (pos < if_end) {
                        uint8_t bip = code[pos++];
                        if (bip == OP_PUSH_CONST_INT) {
                            if (pos + 1 < code_end) { int v = read_u16(code, pos); pos += 2;
                                stack_push(v); }
                        } else if (bip == OP_PUSH_CONST_STR) {
                            if (pos + 3 < code_end) { int o = read_u16(code, pos); int l = read_u16(code, pos+2); pos += 4;
                                char *s = read_string(str_const_buf, sizeof(str_const_buf), sp_data, sp_len, o, l);
                                (void)s;
                            }
                        } else if (bip == OP_VAR_DECL) {
                            if (pos + 3 < code_end) { int o = read_u16(code, pos); int vl = read_u16(code, pos+2); pos += 4;
                                char *vname = read_string(name, sizeof(name), sp_data, sp_len, o, vl);
                                if (vname) var_set(vname, 0);
                            }
                        } else if (bip == OP_ASSIGN_STMT) {
                            if (pos + 3 < code_end) { int o = read_u16(code, pos); int vl = read_u16(code, pos+2); pos += 4;
                                char *vname = read_string(name, sizeof(name), sp_data, sp_len, o, vl);
                                int v = stack_top > 0 ? stack_pop() : 0;
                                if (vname) var_set(vname, v);
                            }
                        } else if (bip == OP_FUNC_CALL_STMT) {
                            /* 内联执行函数调用 */
                            if (pos + 3 < code_end) { int o = read_u16(code, pos); int fl = read_u16(code, pos+2); pos += 4;
                                int nargs = (pos < code_end) ? code[pos++] : 0;
                                char *fn = read_string(name, sizeof(name), sp_data, sp_len, o, fl);
                                if (fn && func_find(fn) >= 0) {
                                    if (call_depth < CALL_STACK_MAX) {
                                        CallFrame *cf = &call_stack[call_depth++];
                                        cf->return_pos = pos; cf->nargs = nargs; cf->return_value = 0;
                                        pos = func_table[func_find(fn)].start_pos;
                                        /* 在 IF body 内继续循环执行 */
                                        continue;
                                    }
                                }
                            }
                        } else if (bip == OP_RETURN_STMT) {
                            /* 内联处理 return */
                            if (pos < code_end) { uint8_t rt = code[pos++]; (void)rt; }
                            pos--; /* 回溯给主循环继续处理（主循环会跳回调用者） */
                            break;
                        } else if (bip == OP_IF_STMT || bip == OP_WHILE_STMT) {
                            pos--; /* 回溯给主循环处理嵌套控制流 */
                            break;
                        } else if (bip == OP_STOP || bip == OP_EXIT) {
                            pos--; break;
                        } else if (bip == OP_PRINT) {
                            int r = (pos < code_end) ? code[pos++] : 0;
                            int val = (r < MAX_REGISTERS) ? vm.registers[r] : 0;
                            printf("[QVM] IF-body print(r%d) = %d\n", r, val);
                        } else if (bip == OP_LOAD_REG) {
                            int r = (pos < code_end) ? code[pos++] : 0;
                            int val = (r < MAX_REGISTERS) ? vm.registers[r] : 0;
                            stack_push(val);
                        } else if (bip == OP_STORE_REG) {
                            int r = (pos < code_end) ? code[pos++] : 0;
                            if (r < MAX_REGISTERS) vm.registers[r] = stack_pop();
                        } else if (bip == OP_ADD) {
                            int b = stack_pop(), a = stack_pop(); stack_push(a + b);
                        } else if (bip == OP_SUB) {
                            int b = stack_pop(), a = stack_pop(); stack_push(a - b);
                        } else if (bip == OP_MUL) {
                            int b = stack_pop(), a = stack_pop(); stack_push(a * b);
                        } else if (bip == OP_DIV) {
                            int b = stack_pop(), a = stack_pop(); stack_push(b != 0 ? a / b : 0);
                        } else if (bip == OP_JUMP) {
                            if (pos + 1 < code_end) { int tgt = read_u16(code, pos); pos += 2; pos = tgt; }
                        } else {
                            printf("[QVM] IF-body 未知 opcode 0x%02x pos=%d\n", bip, pos-1);
                        }
                    }
                    pos = else_end;
                }
            } else {
                printf("[QVM] IF 假，跳过 IF body [%d -> %d)\n", pos, if_end);
                if (has_else) {
                    printf("[QVM] 执行 ELSE body [%d -> %d)\n", if_end+1, else_end);
                    pos = if_end + 1;
                    while (pos < else_end) {
                        uint8_t bip = code[pos++];
                        if (bip == OP_PUSH_CONST_INT) {
                            if (pos + 1 < code_end) { int v = read_u16(code, pos); pos += 2; stack_push(v); }
                        } else if (bip == OP_PUSH_CONST_STR) {
                            if (pos + 3 < code_end) { int o = read_u16(code, pos); int l = read_u16(code, pos+2); pos += 4; (void)read_string(str_const_buf, sizeof(str_const_buf), sp_data, sp_len, o, l); }
                        } else if (bip == OP_VAR_DECL) {
                            if (pos + 3 < code_end) { int o = read_u16(code, pos); int vl = read_u16(code, pos+2); pos += 4; char *vname = read_string(name, sizeof(name), sp_data, sp_len, o, vl); if (vname) var_set(vname, 0); }
                        } else if (bip == OP_ASSIGN_STMT) {
                            if (pos + 3 < code_end) { int o = read_u16(code, pos); int vl = read_u16(code, pos+2); pos += 4; char *vname = read_string(name, sizeof(name), sp_data, sp_len, o, vl); int v = stack_top > 0 ? stack_pop() : 0; if (vname) var_set(vname, v); }
                        } else if (bip == OP_FUNC_CALL_STMT) {
                            if (pos + 3 < code_end) { int o = read_u16(code, pos); int fl = read_u16(code, pos+2); pos += 4; int nargs = (pos < code_end) ? code[pos++] : 0;
                                char *fn = read_string(name, sizeof(name), sp_data, sp_len, o, fl);
                                if (fn && func_find(fn) >= 0) {
                                    if (call_depth < CALL_STACK_MAX) {
                                        CallFrame *cf = &call_stack[call_depth++];
                                        cf->return_pos = pos; cf->nargs = nargs; cf->return_value = 0;
                                        pos = func_table[func_find(fn)].start_pos;
                                        continue;
                                    }
                                }
                            }
                        } else if (bip == OP_RETURN_STMT) {
                            if (pos < code_end) { uint8_t rt = code[pos++]; (void)rt; }
                            pos--; break;
                        } else if (bip == OP_IF_STMT || bip == OP_WHILE_STMT) {
                            pos--; break;
                        } else if (bip == OP_PRINT) {
                            int r = (pos < code_end) ? code[pos++] : 0;
                            int val = (r < MAX_REGISTERS) ? vm.registers[r] : 0;
                            printf("[QVM] ELSE-body print(r%d) = %d\n", r, val);
                        } else if (bip == OP_LOAD_REG) {
                            int r = (pos < code_end) ? code[pos++] : 0; stack_push((r < MAX_REGISTERS) ? vm.registers[r] : 0);
                        } else if (bip == OP_STORE_REG) {
                            int r = (pos < code_end) ? code[pos++] : 0;
                            if (r < MAX_REGISTERS) vm.registers[r] = stack_pop();
                        } else if (bip == OP_ADD) { int b = stack_pop(), a = stack_pop(); stack_push(a + b); }
                        else if (bip == OP_SUB) { int b = stack_pop(), a = stack_pop(); stack_push(a - b); }
                        else if (bip == OP_MUL) { int b = stack_pop(), a = stack_pop(); stack_push(a * b); }
                        else if (bip == OP_DIV) { int b = stack_pop(), a = stack_pop(); stack_push(b != 0 ? a / b : 0); }
                        else if (bip == OP_JUMP) {
                            if (pos + 1 < code_end) { int tgt = read_u16(code, pos); pos += 2; pos = tgt; }
                        } else if (bip == OP_STOP || bip == OP_EXIT) { pos--; break; }
                        else { printf("[QVM] ELSE-body 未知 opcode 0x%02x pos=%d\n", bip, pos-1); }
                    }
                    pos = else_end;
                } else {
                    pos = if_end;
                }
            }
            high_count++;
            break;
        }
        case OP_ELSE_STMT: {
            printf("[QVM] OP_ELSE_STMT (由 IF_STMT 处理跳过)\n");
            high_count++;
            break;
        }
        case OP_WHILE_STMT: {
            printf("[QVM] OP_WHILE_STMT (循环)\n");
            /* 取条件值 */
            int cond = 0;
            if (stack_top > 0) cond = stack_pop();
            /* 扫描 while body 结束位置 */
            int body_end = find_while_body_end(code, code_end, pos);
            /* 入循环栈 */
            if (loop_depth >= LOOP_STACK_MAX) {
                printf("[QVM] 错误: 循环嵌套过深\n"); break;
            }
            LoopFrame *lf = &loop_stack[loop_depth++];
            lf->body_start = pos;
            lf->body_end = body_end;
            lf->condition = cond;
            printf("[QVM] WHILE body_start=%d, body_end=%d, cond=%d\n", pos, body_end, cond);
            if (cond == 0) {
                printf("[QVM] WHILE 条件为假，跳过循环体\n");
                loop_depth--;
                pos = body_end;
            } else {
                /* 条件为真：循环栈已入，pos 指向 body_start，主循环从 pos 执行 body */
            }
            high_count++;
            break;
        }
        case OP_ASSIGN_STMT: {
            if (pos + 3 < fsize) {
                int off = code[pos] | (code[pos+1] << 8);
                int vlen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
                char *n = read_string(name, sizeof(name), sp_data, sp_len, off, vlen);
                /* 取栈顶值赋给变量 */
                int val = stack_top > 0 ? stack_pop() : 0;
                if (n) var_set(n, val);
                printf("[QVM] OP_ASSIGN_STMT(%s = %d)\n", n ? n : "(invalid)", val);
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
            /* 函数调用：保存返回地址，跳转到函数体 */
            if (n && func_find(n) >= 0) {
                if (call_depth >= CALL_STACK_MAX) {
                    printf("[QVM] 错误: 调用栈溢出\n");
                    high_count++; break;
                }
                CallFrame *cf = &call_stack[call_depth++];
                cf->return_pos = pos;  /* 函数返回后继续执行的位置 */
                cf->nargs = nargs;
                cf->ret_addr_value = 0;
                int fidx = func_find(n);
                int target = func_table[fidx].start_pos;
                printf("[QVM] 跳转调用函数 '%s' (返回地址=%d, 目标=%d)\n", n, pos, target);
                pos = target;
                high_count++;
                continue;  /* 立即从目标位置继续执行 */
            } else {
                printf("[QVM] 警告: 函数 '%s' 未定义，跳过调用\n", n ? n : "(null)");
                high_count++;
            }
            break;
        }
        case OP_BREAK_STMT: {
            printf("[QVM] OP_BREAK_STMT\n");
            /* 跳出当前循环：弹出循环栈，跳到 body_end */
            if (loop_depth > 0) {
                LoopFrame *lf = &loop_stack[--loop_depth];
                printf("[QVM] BREAK: 跳出循环 body_end=%d\n", lf->body_end);
                pos = lf->body_end;
                high_count++;
                continue;
            }
            printf("[QVM] 警告: BREAK 在循环外\n");
            high_count++;
            break;
        }
        case OP_CONTINUE_STMT: {
            printf("[QVM] OP_CONTINUE_STMT\n");
            /* 跳到循环体开始，重新执行 */
            if (loop_depth > 0) {
                LoopFrame *lf = &loop_stack[loop_depth - 1];
                printf("[QVM] CONTINUE: 跳回 body_start=%d\n", lf->body_start);
                pos = lf->body_start;
                high_count++;
                continue;
            }
            printf("[QVM] 警告: CONTINUE 在循环外\n");
            high_count++;
            break;
        }
        case OP_PUSH_CONST_INT: {
            int v = 0;
            if (pos < fsize) v = code[pos++];
            if (pos < fsize) v |= code[pos++] << 8;
            stack_push(v);
            /* 同时存入全局变量供后续条件判断使用 */
            var_set("__last_const", v);
            printf("[QVM] OP_PUSH_CONST_INT(%d) stack_top=%d\n", v, stack_top);
            high_count++;
            break;
        }
        case OP_PUSH_CONST_STR: {
            int off = 0, slen = 0;
            if (pos + 3 < fsize) {
                off = code[pos] | (code[pos+1] << 8);
                slen = code[pos+2] | (code[pos+3] << 8);
                pos += 4;
            }
            char *s = read_string(str_const_buf, sizeof(str_const_buf), sp_data, sp_len, off, slen);
            printf("[QVM] OP_PUSH_CONST_STR(%s)\n", s ? s : "(null)");
            high_count++;
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
            if (pos + 1 < fsize) bclen = read_u16(code, pos);
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
