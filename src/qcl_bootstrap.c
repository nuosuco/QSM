/*
 * qcl_bootstrap.c — QSM QEntL 自举启动器（全项目唯一C文件）
 *
 * 三合一职责（启动器本职工作，不是堆功能）：
 *   1) qcompile : 量子指令子集 → 量子电路字节码（v1兼容，永久保留）
 *   2) compile   : 最小QEntL编译器（刚好够编译 qcl.qentl）
 *   3) run       : QBC1 虚拟机（31条opcode + 14个builtin）
 *
 * 自举链：本文件编译 qcl.qentl → qcl.qbc → QCL接管一切编译 → 本文件的
 * compile/run 路径退役（只留量子路径）。QCL活了后C编译器永不再用。
 *
 * QBC1格式: [4B]"QBC1" [2B]code_len_LE16 [code] [2B]pool_len_LE16 [pool]
 * 代码布局: JMP main_start | FUNC_DEF块... | main_start: 语句... | HALT
 * 变量编码: operand < 0x8000 = 帧内局部slot; >= 0x8000 = 全局slot(op & 0x7FFF)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

/* ================================================================
 * 通用工具
 * ================================================================ */
static char *read_file_all(const char *path, long *out_len) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = (char *)malloc(n + 1);
    if (!buf) { fclose(f); return NULL; }
    long rd = (long)fread(buf, 1, n, f);
    fclose(f);
    buf[rd] = '\0';
    if (out_len) *out_len = rd;
    return buf;
}

static int write_file_all(const char *path, const char *data, long len) {
    FILE *f = fopen(path, "wb");
    if (!f) return -1;
    long w = (long)fwrite(data, 1, len, f);
    fclose(f);
    return (w == len) ? 0 : -1;
}

/* ================================================================
 * VM 值类型
 * ================================================================ */
enum { V_INT = 0, V_STR = 1, V_ARR = 2 };

typedef struct Value {
    int type;
    long long i;             /* V_INT */
    char *s;                 /* V_STR: 数据(可含\0) */
    long long len;           /* V_STR: 字节长度 */
    struct Value *arr;       /* V_ARR: 元素数组 */
    long long asize;         /* V_ARR: 元素个数 */
} Value;

static Value mk_int(long long v) {
    Value r; r.type = V_INT; r.i = v; r.s = NULL; r.len = 0; r.arr = NULL; r.asize = 0;
    return r;
}
static Value mk_str_copy(const char *data, long long n) {
    Value r; r.type = V_STR; r.i = 0; r.arr = NULL; r.asize = 0;
    r.s = (char *)malloc(n + 1);
    if (n > 0) memcpy(r.s, data, n);
    r.s[n] = '\0';
    r.len = n;
    return r;
}
static Value mk_arr(long long n) {
    Value r; r.type = V_ARR; r.i = 0; r.s = NULL; r.len = 0;
    r.arr = (Value *)calloc(n > 0 ? n : 1, sizeof(Value));
    r.asize = n;
    for (long long k = 0; k < n; k++) r.arr[k] = mk_int(0);
    return r;
}
static int truthy(Value v) {
    if (v.type == V_INT) return v.i != 0;
    if (v.type == V_STR) return v.len > 0;
    return v.asize > 0;
}

/* ================================================================
 * QBC1 VM
 * ================================================================ */
#define VM_STACK_MAX  65536
#define VM_FRAMES_MAX 1024
#define VM_LOCALS_MAX 512
#define VM_GLOBALS_MAX 8192

typedef struct {
    long long ret_pc;
    Value locals[VM_LOCALS_MAX];
} Frame;

typedef struct {
    int name_off;            /* pool偏移 */
    int nparams;
    long long body_pc;
} FuncInfo;

typedef struct {
    unsigned char *code;
    long code_len;
    char *pool;
    long pool_len;
    Value stack[VM_STACK_MAX];
    long sp;
    Frame *frames;           /* 堆分配(避免C栈溢出) */
    int fp;                  /* 当前帧数 */
    Value globals[VM_GLOBALS_MAX];
    FuncInfo funcs[2048];
    int nfuncs;
    long long cycles;
} VM;

static const char *pool_cstr(VM *vm, int off) {
    if (off < 0 || off >= vm->pool_len) return "";
    return vm->pool + off;
}
/* 读pool字符串为Value(长度取到\0或pool尾) */
static Value pool_str(VM *vm, int off) {
    if (off < 0 || off >= vm->pool_len) return mk_str_copy("", 0);
    const char *p = vm->pool + off;
    long n = strnlen(p, vm->pool_len - off);
    return mk_str_copy(p, n);
}

static void vm_push(VM *vm, Value v) {
    if (vm->sp >= VM_STACK_MAX) { fprintf(stderr, "[QVM] 栈溢出\n"); exit(1); }
    vm->stack[vm->sp++] = v;
}
static Value vm_pop(VM *vm) {
    if (vm->sp <= 0) { fprintf(stderr, "[QVM] 栈下溢 pc=%lld\n", vm->cycles); exit(1); }
    return vm->stack[--vm->sp];
}

static int read_u16_code(VM *vm, long long p) {
    if (p + 1 >= vm->code_len) return 0;
    return vm->code[p] | (vm->code[p + 1] << 8);
}

/* 变量存取：operand高位区分全局/局部 */
static Value *var_slot(VM *vm, int operand, const char *what) {
    if (operand & 0x8000) {
        int g = operand & 0x7FFF;
        if (g >= VM_GLOBALS_MAX) { fprintf(stderr, "[QVM] 全局slot越界 %d (%s)\n", g, what); exit(1); }
        return &vm->globals[g];
    }
    if (vm->fp <= 0) { fprintf(stderr, "[QVM] 主代码访问局部slot %d (%s)\n", operand, what); exit(1); }
    if (operand >= VM_LOCALS_MAX) { fprintf(stderr, "[QVM] 局部slot越界 %d (%s)\n", operand, what); exit(1); }
    return &vm->frames[vm->fp - 1].locals[operand];
}

static int cmp_values(Value a, Value b) {
    if (a.type == V_INT && b.type == V_INT) {
        return (a.i < b.i) ? -1 : (a.i > b.i) ? 1 : 0;
    }
    if (a.type == V_STR && b.type == V_STR) {
        long long n = a.len < b.len ? a.len : b.len;
        int c = (n > 0) ? memcmp(a.s, b.s, n) : 0;
        if (c != 0) return c < 0 ? -1 : 1;
        return (a.len < b.len) ? -1 : (a.len > b.len) ? 1 : 0;
    }
    return (a.type < b.type) ? -1 : (a.type > b.type) ? 1 : 0;
}

static Value do_add(Value a, Value b) {
    if (a.type == V_STR || b.type == V_STR) {
        /* 字符串拼接(另一方若int则先转字符串) */
        char ta[32], tb[32];
        const char *pa; long long la;
        const char *pb; long long lb;
        if (a.type == V_STR) { pa = a.s; la = a.len; }
        else { snprintf(ta, sizeof(ta), "%lld", a.i); pa = ta; la = (long long)strlen(ta); }
        if (b.type == V_STR) { pb = b.s; lb = b.len; }
        else { snprintf(tb, sizeof(tb), "%lld", b.i); pb = tb; lb = (long long)strlen(tb); }
        char *buf = (char *)malloc(la + lb + 1);
        if (la > 0) memcpy(buf, pa, la);
        if (lb > 0) memcpy(buf + la, pb, lb);
        buf[la + lb] = '\0';
        Value r; r.type = V_STR; r.i = 0; r.s = buf; r.len = la + lb; r.arr = NULL; r.asize = 0;
        return r;
    }
    return mk_int(a.i + b.i);
}

/* ---------------- 内置函数 ---------------- */
static void bi_printf(Value *args, int nargs) {
    /* 单一参数游标：按格式串顺序消费 %d/%s（修复static计数器跨调用污染） */
    if (nargs < 1) return;
    Value fmt = args[0];
    int ai = 1;
    for (long long k = 0; k < fmt.len; k++) {
        char c = fmt.s[k];
        if (c == '%' && k + 1 < fmt.len) {
            char nx = fmt.s[k + 1];
            if (nx == 'd') {
                long long v = (ai < nargs && args[ai].type == V_INT) ? args[ai].i : 0;
                printf("%lld", v);
                ai++; k++;
                continue;
            } else if (nx == 's') {
                if (ai < nargs) {
                    Value sv = args[ai];
                    if (sv.type == V_INT) {
                        char tmp[32];
                        snprintf(tmp, sizeof(tmp), "%lld", sv.i);
                        fwrite(tmp, 1, strlen(tmp), stdout);
                    } else if (sv.type == V_STR) {
                        fwrite(sv.s, 1, sv.len, stdout);
                    }
                }
                ai++; k++;
                continue;
            } else if (nx == '%') {
                putchar('%');
                k++;
                continue;
            }
        }
        putchar(c);
    }
    fflush(stdout);
}

static Value call_builtin(VM *vm, const char *name, Value *args, int nargs) {
    if (strcmp(name, "printf") == 0) { bi_printf(args, nargs); return mk_int(0); }
    if (strcmp(name, "str_len") == 0) {
        return mk_int(nargs >= 1 && args[0].type == V_STR ? args[0].len : 0);
    }
    if (strcmp(name, "str_char_at") == 0) {
        if (nargs >= 2 && args[0].type == V_STR) {
            long long idx = args[1].i;
            if (idx >= 0 && idx < args[0].len) return mk_str_copy(args[0].s + idx, 1);
        }
        return mk_str_copy("", 0);
    }
    if (strcmp(name, "str_substring") == 0) {
        if (nargs >= 3 && args[0].type == V_STR) {
            long long st = args[1].i, ln = args[2].i;
            if (st < 0) st = 0;
            if (st > args[0].len) st = args[0].len;
            if (ln < 0) ln = 0;
            if (st + ln > args[0].len) ln = args[0].len - st;
            return mk_str_copy(args[0].s + st, ln);
        }
        return mk_str_copy("", 0);
    }
    if (strcmp(name, "str_concat") == 0) {
        Value a = nargs >= 1 ? args[0] : mk_str_copy("", 0);
        Value b = nargs >= 2 ? args[1] : mk_str_copy("", 0);
        return do_add(a, b);
    }
    if (strcmp(name, "str_eq") == 0) {
        if (nargs >= 2 && args[0].type == V_STR && args[1].type == V_STR)
            return mk_int(args[0].len == args[1].len &&
                          (args[0].len == 0 || memcmp(args[0].s, args[1].s, args[0].len) == 0));
        return mk_int(0);
    }
    if (strcmp(name, "str_index_of") == 0) {
        if (nargs >= 2 && args[0].type == V_STR && args[1].type == V_STR) {
            long long n = args[0].len, m = args[1].len;
            if (m == 0) return mk_int(0);
            for (long long k = 0; k + m <= n; k++)
                if (memcmp(args[0].s + k, args[1].s, m) == 0) return mk_int(k);
        }
        return mk_int(-1);
    }
    if (strcmp(name, "str_from_char") == 0) {
        char c = (char)(nargs >= 1 ? (args[0].i & 0xFF) : 0);
        return mk_str_copy(&c, 1);
    }
    if (strcmp(name, "str_to_int") == 0) {
        long long v = 0;
        int neg = 0;
        if (nargs >= 1 && args[0].type == V_STR) {
            long long k = 0;
            if (k < args[0].len && args[0].s[k] == '-') { neg = 1; k++; }
            for (; k < args[0].len && args[0].s[k] >= '0' && args[0].s[k] <= '9'; k++)
                v = v * 10 + (args[0].s[k] - '0');
        }
        return mk_int(neg ? -v : v);
    }
    if (strcmp(name, "int_to_str") == 0) {
        char tmp[32];
        snprintf(tmp, sizeof(tmp), "%lld", nargs >= 1 ? args[0].i : 0);
        return mk_str_copy(tmp, (long long)strlen(tmp));
    }
    if (strcmp(name, "len") == 0) {
        if (nargs >= 1) {
            if (args[0].type == V_ARR) return mk_int(args[0].asize);
            if (args[0].type == V_STR) return mk_int(args[0].len);
        }
        return mk_int(0);
    }
    if (strcmp(name, "ord") == 0) {
        if (nargs >= 1 && args[0].type == V_STR && args[0].len > 0)
            return mk_int((unsigned char)args[0].s[0]);
        return mk_int(0);
    }
    if (strcmp(name, "chr") == 0) {
        char c = (char)(nargs >= 1 ? args[0].i : 0);
        return mk_str_copy(&c, 1);
    }
    if (strcmp(name, "file_read") == 0) {
        if (nargs >= 1 && args[0].type == V_STR) {
            char path[4096];
            long long n = args[0].len < 4095 ? args[0].len : 4095;
            memcpy(path, args[0].s, n);
            path[n] = '\0';
            long flen = 0;
            char *data = read_file_all(path, &flen);
            if (data) {
                Value r = mk_str_copy(data, flen);
                free(data);
                return r;
            }
        }
        return mk_str_copy("", 0);
    }
    if (strcmp(name, "file_write_bytes") == 0) {
        if (nargs >= 2 && args[0].type == V_STR && args[1].type == V_STR) {
            char path[4096];
            long long n = args[0].len < 4095 ? args[0].len : 4095;
            memcpy(path, args[0].s, n);
            path[n] = '\0';
            if (write_file_all(path, args[1].s, args[1].len) == 0) return mk_int(args[1].len);
        }
        return mk_int(-1);
    }
    if (strcmp(name, "file_exists") == 0) {
        if (nargs >= 1 && args[0].type == V_STR) {
            char path[4096];
            long long n = args[0].len < 4095 ? args[0].len : 4095;
            memcpy(path, args[0].s, n);
            path[n] = '\0';
            FILE *f = fopen(path, "rb");
            if (f) { fclose(f); return mk_int(1); }
        }
        return mk_int(0);
    }
    fprintf(stderr, "[QVM] 未知内置函数: %s\n", name);
    exit(1);
}

/* 扫描函数区[3, main_start)建立函数表 —— 线性反汇编行走 */
static void build_func_table(VM *vm, long long main_start) {
    long long p = 3;
    vm->nfuncs = 0;
    while (p < main_start && p < vm->code_len) {
        unsigned char op = vm->code[p];
        if (op == 0x1E) { /* FUNC_DEF */
            int name_off = read_u16_code(vm, p + 1);
            int np = vm->code[p + 3];
            if (vm->nfuncs < 2048) {
                vm->funcs[vm->nfuncs].name_off = name_off;
                vm->funcs[vm->nfuncs].nparams = np;
                vm->funcs[vm->nfuncs].body_pc = p + 4 + 2 * np;
                vm->nfuncs++;
            }
            p += 4 + 2 * np;
        } else if (op == 0x12 || op == 0x15) { /* CALL/BUILTIN: u16+u8 */
            p += 4;
        } else if (op == 0x01 || op == 0x02 || op == 0x03 || op == 0x04 ||
                   op == 0x10 || op == 0x11 || op == 0x16 || op == 0x17 || op == 0x18) {
            p += 3;
        } else {
            p += 1;
        }
    }
}

static FuncInfo *find_func(VM *vm, const char *name) {
    for (int k = 0; k < vm->nfuncs; k++) {
        if (strcmp(pool_cstr(vm, vm->funcs[k].name_off), name) == 0) return &vm->funcs[k];
    }
    return NULL;
}

static int run_qbc(const char *path) {
    long flen = 0;
    char *raw = read_file_all(path, &flen);
    if (!raw) { fprintf(stderr, "[QVM] 无法读取: %s\n", path); return 1; }
    if (flen < 8 || memcmp(raw, "QBC1", 4) != 0) {
        fprintf(stderr, "[QVM] 不是QBC1格式: %s\n", path);
        free(raw);
        return 1;
    }
    VM *vm = (VM *)calloc(1, sizeof(VM));   /* 堆分配(红线:大结构不上C栈) */
    vm->code_len = (unsigned char)raw[4] | ((unsigned char)raw[5] << 8);
    if (6 + vm->code_len + 2 > flen) {
        fprintf(stderr, "[QVM] QBC截断\n");
        free(raw); free(vm);
        return 1;
    }
    vm->code = (unsigned char *)malloc(vm->code_len);
    memcpy(vm->code, raw + 6, vm->code_len);
    long pp = 6 + vm->code_len;
    vm->pool_len = (unsigned char)raw[pp] | ((unsigned char)raw[pp + 1] << 8);
    vm->pool = (char *)malloc(vm->pool_len + 1);
    if (vm->pool_len > 0) memcpy(vm->pool, raw + pp + 2, vm->pool_len);
    vm->pool[vm->pool_len] = '\0';
    free(raw);

    if (vm->code_len < 3 || vm->code[0] != 0x10) {
        fprintf(stderr, "[QVM] 代码布局错误(缺JMP头)\n");
        return 1;
    }
    long long main_start = vm->code[1] | (vm->code[2] << 8);
    build_func_table(vm, main_start);
    vm->frames = (Frame *)calloc(VM_FRAMES_MAX, sizeof(Frame));

    long long pc = main_start;
    vm->fp = 0;
    vm->sp = 0;
    while (pc < vm->code_len) {
        unsigned char op = vm->code[pc];
        vm->cycles++;
        switch (op) {
        case 0x01: /* PUSH_INT */
            vm_push(vm, mk_int(read_u16_code(vm, pc + 1)));
            pc += 3; break;
        case 0x02: /* PUSH_STR */
            vm_push(vm, pool_str(vm, read_u16_code(vm, pc + 1)));
            pc += 3; break;
        case 0x03: { /* LOAD_VAR */
            Value *slot = var_slot(vm, read_u16_code(vm, pc + 1), "LOAD_VAR");
            vm_push(vm, *slot);
            pc += 3; break;
        }
        case 0x04: { /* STORE_VAR */
            Value v = vm_pop(vm);
            *var_slot(vm, read_u16_code(vm, pc + 1), "STORE_VAR") = v;
            pc += 3; break;
        }
        case 0x05: case 0x06: case 0x07: case 0x08: case 0x09: { /* ADD..MOD */
            Value b = vm_pop(vm), a = vm_pop(vm);
            if (op == 0x05) vm_push(vm, do_add(a, b));
            else if (a.type != V_INT || b.type != V_INT) { fprintf(stderr, "[QVM] 算术需整数 pc=%lld\n", pc); exit(1); }
            else if (op == 0x06) vm_push(vm, mk_int(a.i - b.i));
            else if (op == 0x07) vm_push(vm, mk_int(a.i * b.i));
            else if (op == 0x08) {
                if (b.i == 0) { fprintf(stderr, "[QVM] 除零 pc=%lld\n", pc); exit(1); }
                vm_push(vm, mk_int(a.i / b.i));
            } else {
                if (b.i == 0) { fprintf(stderr, "[QVM] 模零 pc=%lld\n", pc); exit(1); }
                vm_push(vm, mk_int(a.i % b.i));
            }
            pc += 1; break;
        }
        case 0x0A: case 0x0B: case 0x0C: case 0x0D: case 0x0E: case 0x0F: { /* 比较 */
            Value b = vm_pop(vm), a = vm_pop(vm);
            int c = cmp_values(a, b);
            int r = 0;
            if (op == 0x0A) r = (c == 0);
            else if (op == 0x0B) r = (c != 0);
            else if (op == 0x0C) r = (c < 0);
            else if (op == 0x0D) r = (c > 0);
            else if (op == 0x0E) r = (c <= 0);
            else r = (c >= 0);
            vm_push(vm, mk_int(r));
            pc += 1; break;
        }
        case 0x10: /* JMP */
            pc = read_u16_code(vm, pc + 1); break;
        case 0x11: { /* JMP_FALSE */
            Value v = vm_pop(vm);
            int t = read_u16_code(vm, pc + 1);
            pc = truthy(v) ? pc + 3 : t;
            break;
        }
        case 0x12: { /* CALL */
            int name_off = read_u16_code(vm, pc + 1);
            int nargs = vm->code[pc + 3];
            const char *fname = pool_cstr(vm, name_off);
            FuncInfo *fi = find_func(vm, fname);
            if (!fi) { fprintf(stderr, "[QVM] 未定义函数: %s\n", fname); exit(1); }
            if (vm->fp >= VM_FRAMES_MAX) { fprintf(stderr, "[QVM] 调用栈溢出\n"); exit(1); }
            Value argv_tmp[256];
            if (nargs > 256) nargs = 256;
            for (int k = nargs - 1; k >= 0; k--) argv_tmp[k] = vm_pop(vm);
            Frame *fr = &vm->frames[vm->fp];
            memset(fr->locals, 0, sizeof(fr->locals));
            for (int k = 0; k < nargs && k < VM_LOCALS_MAX; k++) fr->locals[k] = argv_tmp[k];
            fr->ret_pc = pc + 4;
            vm->fp++;
            pc = fi->body_pc;
            break;
        }
        case 0x13: { /* RET */
            Value rv = vm_pop(vm);
            if (vm->fp <= 0) { fprintf(stderr, "[QVM] 无帧可返回\n"); exit(1); }
            vm->fp--;
            pc = vm->frames[vm->fp].ret_pc;
            vm_push(vm, rv);
            break;
        }
        case 0x14: /* HALT */
            goto vm_done;
        case 0x15: { /* BUILTIN */
            int name_off = read_u16_code(vm, pc + 1);
            int nargs = vm->code[pc + 3];
            Value argv_tmp[64];
            if (nargs > 64) nargs = 64;
            for (int k = nargs - 1; k >= 0; k--) argv_tmp[k] = vm_pop(vm);
            Value r = call_builtin(vm, pool_cstr(vm, name_off), argv_tmp, nargs);
            vm_push(vm, r);
            pc += 4; break;
        }
        case 0x16: { /* ARRAY_NEW */
            int operand = read_u16_code(vm, pc + 1);
            long long sz = operand > 0 ? operand : vm_pop(vm).i;
            if (sz < 0) sz = 0;
            vm_push(vm, mk_arr(sz));
            pc += 3; break;
        }
        case 0x17: { /* ARRAY_GET */
            int operand = read_u16_code(vm, pc + 1);
            Value idx = vm_pop(vm);
            Value *av = var_slot(vm, operand, "ARRAY_GET");
            if (av->type != V_ARR) { fprintf(stderr, "[QVM] ARRAY_GET非数组 pc=%lld\n", pc); exit(1); }
            if (idx.i < 0 || idx.i >= av->asize) {
                fprintf(stderr, "[QVM] 数组越界 idx=%lld size=%lld pc=%lld\n", idx.i, av->asize, pc);
                exit(1);
            }
            vm_push(vm, av->arr[idx.i]);
            pc += 3; break;
        }
        case 0x18: { /* ARRAY_SET */
            int operand = read_u16_code(vm, pc + 1);
            Value val = vm_pop(vm);
            Value idx = vm_pop(vm);
            Value *av = var_slot(vm, operand, "ARRAY_SET");
            if (av->type != V_ARR) { fprintf(stderr, "[QVM] ARRAY_SET非数组 pc=%lld\n", pc); exit(1); }
            if (idx.i < 0 || idx.i >= av->asize) {
                fprintf(stderr, "[QVM] 数组越界 idx=%lld size=%lld pc=%lld\n", idx.i, av->asize, pc);
                exit(1);
            }
            av->arr[idx.i] = val;
            pc += 3; break;
        }
        case 0x19: /* POP */
            vm_pop(vm);
            pc += 1; break;
        case 0x1A: { /* NEG */
            Value v = vm_pop(vm);
            vm_push(vm, mk_int(-v.i));
            pc += 1; break;
        }
        case 0x1B: { /* NOT */
            Value v = vm_pop(vm);
            vm_push(vm, mk_int(!truthy(v)));
            pc += 1; break;
        }
        case 0x1C: { /* AND */
            Value b = vm_pop(vm), a = vm_pop(vm);
            vm_push(vm, mk_int(truthy(a) && truthy(b)));
            pc += 1; break;
        }
        case 0x1D: { /* OR */
            Value b = vm_pop(vm), a = vm_pop(vm);
            vm_push(vm, mk_int(truthy(a) || truthy(b)));
            pc += 1; break;
        }
        case 0x1E: { /* FUNC_DEF(执行期遇到=跳过整个函数体) */
            int np = vm->code[pc + 3];
            long long p = pc + 4 + 2 * np;
            /* 走到对应FUNC_END */
            int depth = 1;
            while (p < vm->code_len && depth > 0) {
                unsigned char o2 = vm->code[p];
                if (o2 == 0x1E) depth++;
                else if (o2 == 0x1F) depth--;
                if (depth > 0) {
                    if (o2 == 0x12 || o2 == 0x15) p += 4;
                    else if (o2 == 0x01 || o2 == 0x02 || o2 == 0x03 || o2 == 0x04 ||
                             o2 == 0x10 || o2 == 0x11 || o2 == 0x16 || o2 == 0x17 || o2 == 0x18) p += 3;
                    else p += 1;
                }
            }
            pc = p + 1;
            break;
        }
        case 0x1F: /* FUNC_END */
            pc += 1; break;
        default:
            fprintf(stderr, "[QVM] 非法opcode 0x%02X pc=%lld\n", op, pc);
            exit(1);
        }
    }
vm_done:
    return 0;
}

/* ================================================================
 * QEntL 最小编译器（够编译 qcl.qentl）
 * ================================================================ */
enum {
    TK_EOF = 0, TK_IDENT, TK_NUMBER, TK_STRING,
    TK_DEF, TK_VAR, TK_IF, TK_ELSE, TK_WHILE, TK_RETURN, TK_END,
    TK_AND, TK_OR, TK_BREAK,
    TK_PLUS, TK_MINUS, TK_MUL, TK_DIV, TK_MOD,
    TK_EQ, TK_NEQ, TK_LT, TK_GT, TK_LE, TK_GE, TK_NOT, TK_ASSIGN,
    TK_LPAREN, TK_RPAREN, TK_LBRACKET, TK_RBRACKET, TK_COLON, TK_COMMA
};

typedef struct { int type; long start; long len; } Tok;

typedef struct {
    const char *src;
    long src_len;
    Tok *toks;
    int ntoks, tokcap;
    int pos;
    /* 代码缓冲：funcs区 + main区 */
    unsigned char *fbuf; long flen, fcap;
    unsigned char *mbuf; long mlen, mcap;
    /* 字符串池 */
    char *pool; long pool_len, pool_cap;
    /* 符号表：局部(当前函数) + 全局 */
    struct { long start, len; int slot; } locals[1024];
    int nlocals, next_local;
    struct { long start, len; int slot; } globals[4096];
    int nglobals, next_global;
    int in_func;
    int errors;
    /* 跳转操作数修正表：组装时加基址(fbuf+3, mbuf+3+flen) */
    long fjumps[8192]; int nfj;
    long mjumps[8192]; int nmj;
    /* break支持：未解析的break JMP位置栈 */
    long breaks[4096]; int nbreaks;
    int loop_depth;
} Comp;

static void comp_error(Comp *c, const char *msg) {
    const Tok *t = &c->toks[c->pos < c->ntoks ? c->pos : c->ntoks - 1];
    long line = 1;
    for (long k = 0; k < t->start && k < c->src_len; k++) if (c->src[k] == '\n') line++;
    fprintf(stderr, "[QCL-C] 错误(行%d tok%d): %s\n", (int)line, c->pos, msg);
    c->errors++;
    if (c->errors > 10) { fprintf(stderr, "[QCL-C] 错误过多，中止\n"); exit(1); }
}

/* ---- 缓冲区emit ---- */
static void buf_ensure(unsigned char **buf, long *cap, long need) {
    if (need <= *cap) return;
    long nc = *cap < 4096 ? 4096 : *cap;
    while (nc < need) nc *= 2;
    *buf = (unsigned char *)realloc(*buf, nc);
    *cap = nc;
}
static void f_emit_b(Comp *c, unsigned char b) { buf_ensure(&c->fbuf, &c->fcap, c->flen + 1); c->fbuf[c->flen++] = b; }
static void f_emit_u16(Comp *c, int v) { f_emit_b(c, v & 0xFF); f_emit_b(c, (v >> 8) & 0xFF); }
static void f_patch_u16(Comp *c, long at, int v) { c->fbuf[at] = v & 0xFF; c->fbuf[at + 1] = (v >> 8) & 0xFF; }
static void m_emit_b(Comp *c, unsigned char b) { buf_ensure(&c->mbuf, &c->mcap, c->mlen + 1); c->mbuf[c->mlen++] = b; }
static void m_emit_u16(Comp *c, int v) { m_emit_b(c, v & 0xFF); m_emit_b(c, (v >> 8) & 0xFF); }
static void m_patch_u16(Comp *c, long at, int v) { c->mbuf[at] = v & 0xFF; c->mbuf[at + 1] = (v >> 8) & 0xFF; }

/* ---- 字符串池 ---- */
static void pool_reserve(Comp *c, long need) {
    if (need <= c->pool_cap) return;
    long nc = c->pool_cap < 4096 ? 4096 : c->pool_cap;
    while (nc < need) nc *= 2;
    c->pool = (char *)realloc(c->pool, nc);
    c->pool_cap = nc;
}
static int pool_add(Comp *c, const char *data, long n) {
    if (c->pool_len > 0) { pool_reserve(c, c->pool_len + 1); c->pool[c->pool_len++] = '\0'; }
    int off = (int)c->pool_len;   /* 偏移=分隔符之后 */
    pool_reserve(c, c->pool_len + n);
    if (n > 0) memcpy(c->pool + c->pool_len, data, n);
    c->pool_len += n;
    return off;
}

/* ---- 词法 ---- */
static int is_delim(char ch) {
    switch (ch) {
    case ' ': case '\t': case '\n': case '\r':
    case '(': case ')': case '[': case ']': case ':': case ',':
    case '+': case '-': case '*': case '/': case '%':
    case '=': case '!': case '<': case '>': case '&': case '|':
    case '"': case '#': case '\'': case ';': case '.':
        return 1;
    }
    return 0;
}
static void add_tok(Comp *c, int type, long start, long len) {
    if (c->ntoks >= c->tokcap) {
        c->tokcap = c->tokcap < 4096 ? 4096 : c->tokcap * 2;
        c->toks = (Tok *)realloc(c->toks, c->tokcap * sizeof(Tok));
    }
    c->toks[c->ntoks].type = type;
    c->toks[c->ntoks].start = start;
    c->toks[c->ntoks].len = len;
    c->ntoks++;
}
static int kw_match(const char *s, long n, const char *kw) {
    return (long)strlen(kw) == n && memcmp(s, kw, n) == 0;
}
static void lex_run(Comp *c) {
    long pos = 0, n = c->src_len;
    while (pos < n) {
        char ch = c->src[pos];
        if (ch == ' ' || ch == '\t' || ch == '\n' || ch == '\r') { pos++; continue; }
        if (ch == '#') { while (pos < n && c->src[pos] != '\n') pos++; continue; }
        if (ch == '"') {
            long s = pos; pos++;
            while (pos < n) {
                if (c->src[pos] == '\\') pos += 2;
                else if (c->src[pos] == '"') { pos++; break; }
                else pos++;
            }
            add_tok(c, TK_STRING, s, pos - s);
            continue;
        }
        if (ch >= '0' && ch <= '9') {
            long s = pos;
            while (pos < n && c->src[pos] >= '0' && c->src[pos] <= '9') pos++;
            add_tok(c, TK_NUMBER, s, pos - s);
            continue;
        }
        if (!is_delim(ch)) {
            long s = pos;
            while (pos < n && !is_delim(c->src[pos])) pos++;
            long L = pos - s;
            const char *w = c->src + s;
            int t = TK_IDENT;
            if (kw_match(w, L, "def")) t = TK_DEF;
            else if (kw_match(w, L, "var")) t = TK_VAR;
            else if (kw_match(w, L, "if")) t = TK_IF;
            else if (kw_match(w, L, "else")) t = TK_ELSE;
            else if (kw_match(w, L, "while")) t = TK_WHILE;
            else if (kw_match(w, L, "return")) t = TK_RETURN;
            else if (kw_match(w, L, "end")) t = TK_END;
            else if (kw_match(w, L, "and")) t = TK_AND;
            else if (kw_match(w, L, "or")) t = TK_OR;
            else if (kw_match(w, L, "break")) t = TK_BREAK;
            add_tok(c, t, s, L);
            continue;
        }
        /* 双字符运算符 */
        if (ch == '=' && pos + 1 < n && c->src[pos + 1] == '=') { add_tok(c, TK_EQ, pos, 2); pos += 2; continue; }
        if (ch == '=') { add_tok(c, TK_ASSIGN, pos, 1); pos++; continue; }
        if (ch == '!' && pos + 1 < n && c->src[pos + 1] == '=') { add_tok(c, TK_NEQ, pos, 2); pos += 2; continue; }
        if (ch == '!') { add_tok(c, TK_NOT, pos, 1); pos++; continue; }
        if (ch == '<' && pos + 1 < n && c->src[pos + 1] == '=') { add_tok(c, TK_LE, pos, 2); pos += 2; continue; }
        if (ch == '<') { add_tok(c, TK_LT, pos, 1); pos++; continue; }
        if (ch == '>' && pos + 1 < n && c->src[pos + 1] == '=') { add_tok(c, TK_GE, pos, 2); pos += 2; continue; }
        if (ch == '>') { add_tok(c, TK_GT, pos, 1); pos++; continue; }
        if (ch == '&' && pos + 1 < n && c->src[pos + 1] == '&') { add_tok(c, TK_AND, pos, 2); pos += 2; continue; }
        if (ch == '&') { pos++; continue; }
        if (ch == '|' && pos + 1 < n && c->src[pos + 1] == '|') { add_tok(c, TK_OR, pos, 2); pos += 2; continue; }
        if (ch == '|') { pos++; continue; }
        if (ch == '+') { add_tok(c, TK_PLUS, pos, 1); pos++; continue; }
        if (ch == '-') { add_tok(c, TK_MINUS, pos, 1); pos++; continue; }
        if (ch == '*') { add_tok(c, TK_MUL, pos, 1); pos++; continue; }
        if (ch == '/') { add_tok(c, TK_DIV, pos, 1); pos++; continue; }
        if (ch == '%') { add_tok(c, TK_MOD, pos, 1); pos++; continue; }
        if (ch == '(') { add_tok(c, TK_LPAREN, pos, 1); pos++; continue; }
        if (ch == ')') { add_tok(c, TK_RPAREN, pos, 1); pos++; continue; }
        if (ch == '[') { add_tok(c, TK_LBRACKET, pos, 1); pos++; continue; }
        if (ch == ']') { add_tok(c, TK_RBRACKET, pos, 1); pos++; continue; }
        if (ch == ':') { add_tok(c, TK_COLON, pos, 1); pos++; continue; }
        if (ch == ',') { add_tok(c, TK_COMMA, pos, 1); pos++; continue; }
        fprintf(stderr, "[QCL-C] 词法错误: 未识别字符 0x%02X 位于字节 %ld\n", (unsigned char)ch, pos);
        pos++;
    }
    add_tok(c, TK_EOF, n, 0);
}

/* ---- token访问 ---- */
static int cur(Comp *c) { return c->toks[c->pos].type; }
static void advance(Comp *c) { if (cur(c) != TK_EOF) c->pos++; }
static void expect(Comp *c, int t, const char *what) {
    if (cur(c) != t) {
        comp_error(c, what);
        exit(1);
    }
    advance(c);
}
static char *tok_text(Comp *c, int idx, long *outlen) {
    const Tok *t = &c->toks[idx];
    if (outlen) *outlen = t->len;
    char *s = (char *)malloc(t->len + 1);
    memcpy(s, c->src + t->start, t->len);
    s[t->len] = '\0';
    return s;
}

/* ---- 符号表 ---- */
static int sym_eq(Comp *c, long start, long len, long s2, long l2) {
    return len == l2 && memcmp(c->src + start, c->src + s2, len) == 0;
}
/* 返回编码后的operand(全局带0x8000)；未找到返回-1 */
static int sym_resolve(Comp *c, long start, long len) {
    for (int k = c->nlocals - 1; k >= 0; k--)
        if (sym_eq(c, start, len, c->locals[k].start, c->locals[k].len))
            return c->locals[k].slot;
    for (int k = c->nglobals - 1; k >= 0; k--)
        if (sym_eq(c, start, len, c->globals[k].start, c->globals[k].len))
            return 0x8000 | c->globals[k].slot;
    return -1;
}
static int sym_add_local(Comp *c, long start, long len) {
    if (c->next_local >= VM_LOCALS_MAX) { comp_error(c, "局部变量过多"); exit(1); }
    int slot = c->next_local++;
    c->locals[c->nlocals].start = start;
    c->locals[c->nlocals].len = len;
    c->locals[c->nlocals].slot = slot;
    c->nlocals++;
    return slot;
}
static int sym_add_global(Comp *c, long start, long len) {
    if (c->next_global >= VM_GLOBALS_MAX) { comp_error(c, "全局变量过多"); exit(1); }
    int slot = c->next_global++;
    c->globals[c->nglobals].start = start;
    c->globals[c->nglobals].len = len;
    c->globals[c->nglobals].slot = slot;
    c->nglobals++;
    return 0x8000 | slot;
}

static int is_builtin_name(Comp *c, long start, long len) {
    static const char *names[] = {
        "printf", "str_len", "str_char_at", "str_substring", "str_concat",
        "str_eq", "str_index_of", "str_from_char", "str_to_int", "int_to_str",
        "len", "file_read", "file_write_bytes", "file_exists", "ord", "chr"
    };
    for (int k = 0; k < 16; k++)
        if (kw_match(c->src + start, len, names[k])) return 1;
    return 0;
}

/* ---- 字符串字面量处理(转义) ---- */
static int process_string_lit(Comp *c, int tokidx) {
    const Tok *t = &c->toks[tokidx];
    long raw_start = t->start + 1;
    long raw_len = t->len - 2;
    char *tmp = (char *)malloc(raw_len + 1);
    long o = 0;
    for (long k = 0; k < raw_len; k++) {
        char ch = c->src[raw_start + k];
        if (ch == '\\' && k + 1 < raw_len) {
            k++;
            char e = c->src[raw_start + k];
            if (e == 'n') tmp[o++] = '\n';
            else if (e == 't') tmp[o++] = '\t';
            else if (e == '\\') tmp[o++] = '\\';
            else if (e == '"') tmp[o++] = '"';
            else { tmp[o++] = '\\'; tmp[o++] = e; }
        } else {
            tmp[o++] = ch;
        }
    }
    int off = pool_add(c, tmp, o);
    free(tmp);
    return off;
}

/* ---- emit目标由c->in_func决定; 跳转操作数记入修正表 ---- */
static void emit_b(Comp *c, unsigned char b) { if (c->in_func) f_emit_b(c, b); else m_emit_b(c, b); }
static void emit_u16(Comp *c, int v) {
    if (c->in_func) {
        long pos = c->flen;
        f_emit_u16(c, v);
        if (pos > 0 && (c->fbuf[pos - 1] == 0x10 || c->fbuf[pos - 1] == 0x11)) {
            if (c->nfj < 8192) c->fjumps[c->nfj++] = pos;
        }
    } else {
        long pos = c->mlen;
        m_emit_u16(c, v);
        if (pos > 0 && (c->mbuf[pos - 1] == 0x10 || c->mbuf[pos - 1] == 0x11)) {
            if (c->nmj < 8192) c->mjumps[c->nmj++] = pos;
        }
    }
}
static long emit_pos(Comp *c) { return c->in_func ? c->flen : c->mlen; }
static void patch_u16(Comp *c, long at, int v) {
    if (c->in_func) f_patch_u16(c, at, v); else m_patch_u16(c, at, v);
}

static void parse_expr(Comp *c);

static void parse_call(Comp *c, long ns, long nl) {
    /* 当前token是'(' */
    advance(c);
    int nargs = 0;
    if (cur(c) != TK_RPAREN) {
        parse_expr(c);
        nargs = 1;
        while (cur(c) == TK_COMMA) {
            advance(c);
            parse_expr(c);
            nargs++;
        }
    }
    expect(c, TK_RPAREN, "调用缺')'");
    int pid = pool_add(c, c->src + ns, nl);
    if (is_builtin_name(c, ns, nl)) {
        emit_b(c, 0x15); emit_u16(c, pid); emit_b(c, nargs);
    } else {
        emit_b(c, 0x12); emit_u16(c, pid); emit_b(c, nargs);
    }
}

static void parse_primary(Comp *c) {
    int t = cur(c);
    if (t == TK_NUMBER) {
        long L; char *txt = tok_text(c, c->pos, &L);
        long long v = atoll(txt);
        free(txt);
        if (v < 0 || v > 65535) { comp_error(c, "整数字面量超出u16范围"); }
        emit_b(c, 0x01); emit_u16(c, (int)v);
        advance(c);
    } else if (t == TK_STRING) {
        int pid = process_string_lit(c, c->pos);
        emit_b(c, 0x02); emit_u16(c, pid);
        advance(c);
    } else if (t == TK_IDENT) {
        long ns = c->toks[c->pos].start, nl = c->toks[c->pos].len;
        advance(c);
        if (cur(c) == TK_LPAREN) {
            parse_call(c, ns, nl);
        } else if (cur(c) == TK_LBRACKET) {
            advance(c);
            parse_expr(c);
            expect(c, TK_RBRACKET, "数组读缺']'");
            int slot = sym_resolve(c, ns, nl);
            if (slot < 0) { comp_error(c, "未定义数组变量"); slot = 0; }
            emit_b(c, 0x17); emit_u16(c, slot);
        } else {
            int slot = sym_resolve(c, ns, nl);
            if (slot < 0) { comp_error(c, "未定义变量"); slot = 0; }
            emit_b(c, 0x03); emit_u16(c, slot);
        }
    } else if (t == TK_LPAREN) {
        advance(c);
        parse_expr(c);
        expect(c, TK_RPAREN, "缺')'");
    } else {
        comp_error(c, "表达式中意外的token");
        advance(c);
    }
}

static void parse_unary(Comp *c) {
    if (cur(c) == TK_MINUS) { advance(c); parse_unary(c); emit_b(c, 0x1A); }
    else if (cur(c) == TK_NOT) { advance(c); parse_unary(c); emit_b(c, 0x1B); }
    else parse_primary(c);
}
static void parse_mul_expr(Comp *c) {
    parse_unary(c);
    for (;;) {
        if (cur(c) == TK_MUL) { advance(c); parse_unary(c); emit_b(c, 0x07); }
        else if (cur(c) == TK_DIV) { advance(c); parse_unary(c); emit_b(c, 0x08); }
        else if (cur(c) == TK_MOD) { advance(c); parse_unary(c); emit_b(c, 0x09); }
        else break;
    }
}
static void parse_add_expr(Comp *c) {
    parse_mul_expr(c);
    for (;;) {
        if (cur(c) == TK_PLUS) { advance(c); parse_mul_expr(c); emit_b(c, 0x05); }
        else if (cur(c) == TK_MINUS) { advance(c); parse_mul_expr(c); emit_b(c, 0x06); }
        else break;
    }
}
static void parse_cmp_expr(Comp *c) {
    parse_add_expr(c);
    for (;;) {
        if (cur(c) == TK_LT) { advance(c); parse_add_expr(c); emit_b(c, 0x0C); }
        else if (cur(c) == TK_GT) { advance(c); parse_add_expr(c); emit_b(c, 0x0D); }
        else if (cur(c) == TK_LE) { advance(c); parse_add_expr(c); emit_b(c, 0x0E); }
        else if (cur(c) == TK_GE) { advance(c); parse_add_expr(c); emit_b(c, 0x0F); }
        else break;
    }
}
static void parse_eq_expr(Comp *c) {
    parse_cmp_expr(c);
    for (;;) {
        if (cur(c) == TK_EQ) { advance(c); parse_cmp_expr(c); emit_b(c, 0x0A); }
        else if (cur(c) == TK_NEQ) { advance(c); parse_cmp_expr(c); emit_b(c, 0x0B); }
        else break;
    }
}
static void parse_and_expr(Comp *c) {
    parse_eq_expr(c);
    while (cur(c) == TK_AND) { advance(c); parse_eq_expr(c); emit_b(c, 0x1C); }
}
static void parse_or_expr(Comp *c) {
    parse_and_expr(c);
    while (cur(c) == TK_OR) { advance(c); parse_and_expr(c); emit_b(c, 0x1D); }
}
static void parse_expr(Comp *c) { parse_or_expr(c); }

/* ---- 语句 ---- */
static void parse_statement(Comp *c);

static void parse_block(Comp *c) {
    while (cur(c) != TK_END && cur(c) != TK_ELSE && cur(c) != TK_EOF)
        parse_statement(c);
}

static void parse_var_decl(Comp *c) {
    advance(c); /* skip var */
    long ns = c->toks[c->pos].start, nl = c->toks[c->pos].len;
    advance(c);
    if (cur(c) == TK_LBRACKET) {
        advance(c);
        parse_expr(c);
        expect(c, TK_RBRACKET, "数组声明缺']'");
        int slot = c->in_func ? sym_add_local(c, ns, nl) : sym_add_global(c, ns, nl);
        emit_b(c, 0x16); emit_u16(c, 0);   /* size从栈弹出 */
        emit_b(c, 0x04); emit_u16(c, slot);
    } else {
        expect(c, TK_ASSIGN, "var声明缺'='");
        parse_expr(c);
        int slot = c->in_func ? sym_add_local(c, ns, nl) : sym_add_global(c, ns, nl);
        emit_b(c, 0x04); emit_u16(c, slot);
    }
}

static void parse_if(Comp *c) {
    advance(c);
    expect(c, TK_LPAREN, "if缺'('");
    parse_expr(c);
    expect(c, TK_RPAREN, "if缺')'");
    expect(c, TK_COLON, "if缺':'");
    emit_b(c, 0x11);
    long else_patch = emit_pos(c);
    emit_u16(c, 0);
    parse_block(c);
    if (cur(c) == TK_ELSE) {
        advance(c);
        expect(c, TK_COLON, "else缺':'");
        emit_b(c, 0x10);
        long end_patch = emit_pos(c);
        emit_u16(c, 0);
        patch_u16(c, else_patch, (int)emit_pos(c));
        parse_block(c);
        patch_u16(c, end_patch, (int)emit_pos(c));
    } else {
        patch_u16(c, else_patch, (int)emit_pos(c));
    }
    expect(c, TK_END, "if缺end");
}

static void parse_while(Comp *c) {
    advance(c);
    expect(c, TK_LPAREN, "while缺'('");
    long loop_top = emit_pos(c);
    parse_expr(c);
    expect(c, TK_RPAREN, "while缺')'");
    expect(c, TK_COLON, "while缺':'");
    emit_b(c, 0x11);
    long end_patch = emit_pos(c);
    emit_u16(c, 0);
    int break_start = c->nbreaks;   /* break哨兵 */
    c->loop_depth++;
    parse_block(c);
    c->loop_depth--;
    emit_b(c, 0x10); emit_u16(c, (int)loop_top);
    long after = emit_pos(c);
    patch_u16(c, end_patch, (int)after);
    for (int k = break_start; k < c->nbreaks; k++)
        patch_u16(c, c->breaks[k], (int)after);
    c->nbreaks = break_start;
    expect(c, TK_END, "while缺end");
}

static void parse_break(Comp *c) {
    advance(c);
    if (c->loop_depth <= 0) { comp_error(c, "break在循环外"); return; }
    emit_b(c, 0x10);
    long p = emit_pos(c);
    emit_u16(c, 0);
    if (c->nbreaks < 4096) c->breaks[c->nbreaks++] = p;
}

static void parse_return(Comp *c) {
    advance(c);
    int t = cur(c);
    if (t == TK_END || t == TK_ELSE || t == TK_EOF) {
        emit_b(c, 0x01); emit_u16(c, 0);
    } else {
        parse_expr(c);
    }
    emit_b(c, 0x13);
}

static void parse_ident_stmt(Comp *c) {
    long ns = c->toks[c->pos].start, nl = c->toks[c->pos].len;
    advance(c);
    if (cur(c) == TK_ASSIGN) {
        advance(c);
        parse_expr(c);
        int slot = sym_resolve(c, ns, nl);
        if (slot < 0) slot = c->in_func ? sym_add_local(c, ns, nl) : sym_add_global(c, ns, nl);
        emit_b(c, 0x04); emit_u16(c, slot);
    } else if (cur(c) == TK_LBRACKET) {
        advance(c);
        parse_expr(c);
        expect(c, TK_RBRACKET, "数组写缺']'");
        if (cur(c) == TK_ASSIGN) {
            advance(c);
            parse_expr(c);
            int slot = sym_resolve(c, ns, nl);
            if (slot < 0) { comp_error(c, "数组赋值:未定义数组"); slot = 0; }
            emit_b(c, 0x18); emit_u16(c, slot);
        } else {
            int slot = sym_resolve(c, ns, nl);
            if (slot < 0) { comp_error(c, "未定义数组"); slot = 0; }
            emit_b(c, 0x17); emit_u16(c, slot);
            emit_b(c, 0x19);
        }
    } else if (cur(c) == TK_LPAREN) {
        parse_call(c, ns, nl);
        emit_b(c, 0x19);
    } else {
        int slot = sym_resolve(c, ns, nl);
        if (slot < 0) slot = c->in_func ? sym_add_local(c, ns, nl) : sym_add_global(c, ns, nl);
        emit_b(c, 0x03); emit_u16(c, slot);
        emit_b(c, 0x19);
    }
}

static void parse_statement(Comp *c) {
    int t = cur(c);
    if (t == TK_VAR) parse_var_decl(c);
    else if (t == TK_IF) parse_if(c);
    else if (t == TK_WHILE) parse_while(c);
    else if (t == TK_BREAK) parse_break(c);
    else if (t == TK_RETURN) parse_return(c);
    else if (t == TK_IDENT) parse_ident_stmt(c);
    else if (t == TK_END || t == TK_ELSE) { comp_error(c, "多余的end/else"); advance(c); }
    else { parse_expr(c); emit_b(c, 0x19); }
}

static void parse_func_def(Comp *c) {
    advance(c); /* skip def */
    long fs = c->toks[c->pos].start, fl = c->toks[c->pos].len;
    advance(c);
    expect(c, TK_LPAREN, "def缺'('");
    long p_s[128], p_l[128];
    int np = 0;
    if (cur(c) != TK_RPAREN) {
        p_s[0] = c->toks[c->pos].start; p_l[0] = c->toks[c->pos].len; np = 1;
        advance(c);
        while (cur(c) == TK_COMMA) {
            advance(c);
            if (np >= 128) { comp_error(c, "参数过多"); break; }
            p_s[np] = c->toks[c->pos].start; p_l[np] = c->toks[c->pos].len; np++;
            advance(c);
        }
    }
    expect(c, TK_RPAREN, "def缺')'");
    expect(c, TK_COLON, "def缺':'");

    /* FUNC_DEF头 */
    int fpid = pool_add(c, c->src + fs, fl);
    f_emit_b(c, 0x1E);
    f_emit_u16(c, fpid);
    f_emit_b(c, np);
    for (int k = 0; k < np; k++) {
        int pid = pool_add(c, c->src + p_s[k], p_l[k]);
        f_emit_u16(c, pid);
    }

    /* 新局部作用域，参数占slot 0..np-1 */
    c->nlocals = 0;
    c->next_local = 0;
    for (int k = 0; k < np; k++) sym_add_local(c, p_s[k], p_l[k]);
    c->in_func = 1;

    parse_block(c);

    /* 隐式return 0 */
    f_emit_b(c, 0x01); f_emit_u16(c, 0);
    f_emit_b(c, 0x13);
    f_emit_b(c, 0x1F);

    expect(c, TK_END, "def缺end");
    c->in_func = 0;
    c->nlocals = 0; c->next_local = 0;  /* 函数局部作用域不泄漏到主代码 */
}

static int compile_qentl(const char *in_path, const char *out_path) {
    long slen = 0;
    char *src = read_file_all(in_path, &slen);
    if (!src) { fprintf(stderr, "[QCL-C] 无法读取: %s\n", in_path); return 1; }

    Comp *c = (Comp *)calloc(1, sizeof(Comp));
    c->src = src;
    c->src_len = slen;
    lex_run(c);

    c->pos = 0;
    c->in_func = 0;
    /* 顶层：var/def/语句 按源码顺序处理 */
    while (cur(c) != TK_EOF) {
        if (cur(c) == TK_DEF) {
            parse_func_def(c);
        } else {
            parse_statement(c);   /* var声明→全局; 其他→main代码 */
        }
    }

    if (c->errors > 0) {
        fprintf(stderr, "[QCL-C] %d个错误，放弃输出\n", c->errors);
        return 1;
    }

    /* 组装: JMP main_start | funcs | main | HALT */
    long main_start = 3 + c->flen;
    long total = main_start + c->mlen + 1;
    unsigned char *out = (unsigned char *)malloc(total);
    out[0] = 0x10;
    out[1] = main_start & 0xFF;
    out[2] = (main_start >> 8) & 0xFF;
    if (c->flen > 0) memcpy(out + 3, c->fbuf, c->flen);
    if (c->mlen > 0) memcpy(out + main_start, c->mbuf, c->mlen);
    out[total - 1] = 0x14; /* HALT */

    /* 修正跳转目标：fbuf基址=3, mbuf基址=3+flen */
    for (int k = 0; k < c->nfj; k++) {
        long p = c->fjumps[k];            /* fbuf内偏移 */
        int rel = c->fbuf[p] | (c->fbuf[p + 1] << 8);
        int abs = (int)(3 + rel);
        out[3 + p] = abs & 0xFF;
        out[3 + p + 1] = (abs >> 8) & 0xFF;
    }
    for (int k = 0; k < c->nmj; k++) {
        long p = c->mjumps[k];            /* mbuf内偏移 */
        int rel = c->mbuf[p] | (c->mbuf[p + 1] << 8);
        int abs = (int)(main_start + rel);
        out[main_start + p] = abs & 0xFF;
        out[main_start + p + 1] = (abs >> 8) & 0xFF;
    }

    /* 写QBC1 */
    FILE *f = fopen(out_path, "wb");
    if (!f) { fprintf(stderr, "[QCL-C] 无法写: %s\n", out_path); return 1; }
    fwrite("QBC1", 1, 4, f);
    unsigned char h[2];
    h[0] = total & 0xFF; h[1] = (total >> 8) & 0xFF;
    fwrite(h, 1, 2, f);
    fwrite(out, 1, total, f);
    h[0] = c->pool_len & 0xFF; h[1] = (c->pool_len >> 8) & 0xFF;
    fwrite(h, 1, 2, f);
    if (c->pool_len > 0) fwrite(c->pool, 1, c->pool_len, f);
    fclose(f);

    fprintf(stdout, "[QCL-C] %s -> %s  tokens=%d code=%ld pool=%ld 全局=%d 函数区=%ld\n",
            in_path, out_path, c->ntoks, total, c->pool_len, c->next_global, c->flen);
    free(out);
    return 0;
}

/* ================================================================
 * 量子指令子集编译器（v1兼容，永久保留）
 * ================================================================ */
#define QOP_INIT_N 20
#define QOP_H 1
#define QOP_X 2
#define QOP_Z 3
#define QOP_CNOT 4
#define QOP_MEASURE 5
#define QOP_PRINT 11
#define QOP_STOP 12
#define QOP_T 35
#define QOP_S 36
#define QOP_Y 37
#define QOP_EXIT 17

static int compile_quantum(const char *input_path, const char *output_path) {
    FILE *fin = fopen(input_path, "r");
    if (!fin) { fprintf(stderr, "[QCL] 无法打开输入文件: %s\n", input_path); return -1; }
    unsigned char bc[131072];
    int bp = 0;
    char line[4096];
    int found = 0;
    fprintf(stdout, "[QCL] 量子编译: %s -> %s\n", input_path, output_path);
    while (fgets(line, sizeof(line), fin)) {
        char *p = line;
        while (*p == ' ' || *p == '\t' || *p == '\r') p++;
        if (*p == '/' || *p == '\n' || *p == '\0' || *p == '#') continue;
        char code[4096];
        int ci = 0;
        for (int k = 0; line[k]; k++) {
            if (line[k] == '/' && line[k + 1] == '/') break;
            if (ci < 4095) code[ci++] = line[k];
        }
        code[ci] = '\0';
        p = code;
        while (*p == ' ' || *p == '\t' || *p == '\r') p++;
        if (*p == '/' || *p == '\n' || *p == '\0' || *p == '#') continue;

        if (bp > 131000) break;
        if (strncmp(p, "init ", 5) == 0) {
            p += 5;
            unsigned int qn = 0;
            while (*p >= '0' && *p <= '9') { qn = qn * 10 + (*p - '0'); p++; }
            bc[bp++] = QOP_INIT_N; bc[bp++] = qn & 0xFF; bc[bp++] = (qn >> 8) & 0xFF;
            found = 1;
        } else if (strncmp(p, "H ", 2) == 0 || strncmp(p, "X ", 2) == 0 ||
                   strncmp(p, "Y ", 2) == 0 || strncmp(p, "Z ", 2) == 0 ||
                   strncmp(p, "T ", 2) == 0 || strncmp(p, "S ", 2) == 0) {
            unsigned char op;
            if (strncmp(p, "H ", 2) == 0) op = QOP_H;
            else if (strncmp(p, "X ", 2) == 0) op = QOP_X;
            else if (strncmp(p, "Y ", 2) == 0) op = QOP_Y;
            else if (strncmp(p, "Z ", 2) == 0) op = QOP_Z;
            else if (strncmp(p, "T ", 2) == 0) op = QOP_T;
            else op = QOP_S;
            p += 2;
            int qid = 0;
            while (*p >= '0' && *p <= '9') { qid = qid * 10 + (*p - '0'); p++; }
            bc[bp++] = op; bc[bp++] = qid;
            found = 1;
        } else if (strncmp(p, "CNOT ", 5) == 0) {
            p += 5;
            int ctrl = 0, tgt = 0;
            while (*p >= '0' && *p <= '9') { ctrl = ctrl * 10 + (*p - '0'); p++; }
            while (*p == ' ' || *p == '\t') p++;
            while (*p >= '0' && *p <= '9') { tgt = tgt * 10 + (*p - '0'); p++; }
            bc[bp++] = QOP_CNOT; bc[bp++] = ctrl; bc[bp++] = tgt;
            found = 1;
        } else if (strncmp(p, "MEASURE ", 8) == 0) {
            p += 8;
            int qid = 0, reg = 0;
            while (*p >= '0' && *p <= '9') { qid = qid * 10 + (*p - '0'); p++; }
            while (*p == ' ' || *p == '\t') p++;
            while (*p >= '0' && *p <= '9') { reg = reg * 10 + (*p - '0'); p++; }
            bc[bp++] = QOP_MEASURE; bc[bp++] = qid; bc[bp++] = reg;
            found = 1;
        } else if (strncmp(p, "PRINT ", 6) == 0) {
            p += 6;
            int reg = 0;
            while (*p >= '0' && *p <= '9') { reg = reg * 10 + (*p - '0'); p++; }
            bc[bp++] = QOP_PRINT; bc[bp++] = reg;
            found = 1;
        } else if (strncmp(p, "STOP", 4) == 0) {
            bc[bp++] = QOP_STOP; found = 1;
        } else if (strncmp(p, "EXIT", 4) == 0) {
            bc[bp++] = QOP_EXIT; found = 1;
        }
    }
    fclose(fin);
    if (!found) { fprintf(stdout, "[QCL] 警告: 未找到量子代码\n"); bc[bp++] = QOP_STOP; }
    FILE *fout = fopen(output_path, "wb");
    if (!fout) { fprintf(stderr, "[QCL] 无法创建输出: %s\n", output_path); return -1; }
    fwrite(bc, 1, bp, fout);
    fclose(fout);
    fprintf(stdout, "[QCL] 量子编译完成: %d 字节\n", bp);
    return 0;
}

/* ================================================================
 * 反汇编（调试用）
 * ================================================================ */
static int disasm_qbc(const char *path) {
    long flen = 0;
    char *raw = read_file_all(path, &flen);
    if (!raw || flen < 8 || memcmp(raw, "QBC1", 4) != 0) {
        fprintf(stderr, "不是QBC1: %s\n", path);
        return 1;
    }
    long clen = (unsigned char)raw[4] | ((unsigned char)raw[5] << 8);
    unsigned char *code = (unsigned char *)raw + 6;
    long pp = 6 + clen;
    long plen = (unsigned char)raw[pp] | ((unsigned char)raw[pp + 1] << 8);
    char *pool = raw + pp + 2;
    printf("code=%ld pool=%ld\n", clen, plen);
    long p = 0;
    while (p < clen) {
        unsigned char op = code[p];
        printf("%5ld: %02X ", p, op);
        switch (op) {
        case 0x01: printf("PUSH_INT %d", code[p+1] | (code[p+2]<<8)); p += 3; break;
        case 0x02: printf("PUSH_STR %d \"%s\"", code[p+1] | (code[p+2]<<8),
                           (code[p+1] | (code[p+2]<<8)) < plen ? pool + (code[p+1] | (code[p+2]<<8)) : "?"); p += 3; break;
        case 0x03: printf("LOAD_VAR %d%s", code[p+1] | (code[p+2]<<8), (code[p+2]&0x80) ? "(g)" : ""); p += 3; break;
        case 0x04: printf("STORE_VAR %d%s", code[p+1] | (code[p+2]<<8), (code[p+2]&0x80) ? "(g)" : ""); p += 3; break;
        case 0x05: printf("ADD"); p++; break;
        case 0x06: printf("SUB"); p++; break;
        case 0x07: printf("MUL"); p++; break;
        case 0x08: printf("DIV"); p++; break;
        case 0x09: printf("MOD"); p++; break;
        case 0x0A: printf("EQ"); p++; break;
        case 0x0B: printf("NEQ"); p++; break;
        case 0x0C: printf("LT"); p++; break;
        case 0x0D: printf("GT"); p++; break;
        case 0x0E: printf("LE"); p++; break;
        case 0x0F: printf("GE"); p++; break;
        case 0x10: printf("JMP %d", code[p+1] | (code[p+2]<<8)); p += 3; break;
        case 0x11: printf("JMP_FALSE %d", code[p+1] | (code[p+2]<<8)); p += 3; break;
        case 0x12: printf("CALL %s nargs=%d", pool + (code[p+1] | (code[p+2]<<8)), code[p+3]); p += 4; break;
        case 0x13: printf("RET"); p++; break;
        case 0x14: printf("HALT"); p++; break;
        case 0x15: printf("BUILTIN %s nargs=%d", pool + (code[p+1] | (code[p+2]<<8)), code[p+3]); p += 4; break;
        case 0x16: printf("ARRAY_NEW %d", code[p+1] | (code[p+2]<<8)); p += 3; break;
        case 0x17: printf("ARRAY_GET %d", code[p+1] | (code[p+2]<<8)); p += 3; break;
        case 0x18: printf("ARRAY_SET %d", code[p+1] | (code[p+2]<<8)); p += 3; break;
        case 0x19: printf("POP"); p++; break;
        case 0x1A: printf("NEG"); p++; break;
        case 0x1B: printf("NOT"); p++; break;
        case 0x1C: printf("AND"); p++; break;
        case 0x1D: printf("OR"); p++; break;
        case 0x1E: {
            int np2 = code[p+3];
            printf("FUNC_DEF %s nparams=%d", pool + (code[p+1] | (code[p+2]<<8)), np2);
            p += 4 + 2 * np2;
            break;
        }
        case 0x1F: printf("FUNC_END"); p++; break;
        default: printf("???"); p++; break;
        }
        printf("\n");
    }
    free(raw);
    return 0;
}

/* ================================================================
 * main
 * ================================================================ */
static void usage(const char *prog) {
    fprintf(stderr, "QSM QEntL 自举启动器 (唯一C文件)\n");
    fprintf(stderr, "用法:\n");
    fprintf(stderr, "  %s compile <in.qentl> <out.qbc>   编译QEntL\n", prog);
    fprintf(stderr, "  %s run <file.qbc>                 执行QBC1\n", prog);
    fprintf(stderr, "  %s qcompile <in.qasm> <out.qbc>   编译量子指令\n", prog);
    fprintf(stderr, "  %s disasm <file.qbc>              反汇编\n", prog);
    fprintf(stderr, "  %s <in.qentl> [out.qbc]           兼容模式(无out则编译并执行)\n", prog);
}

int main(int argc, char *argv[]) {
    srand((unsigned int)time(NULL));
    if (argc < 2) { usage(argv[0]); return 1; }

    if (strcmp(argv[1], "compile") == 0) {
        if (argc < 4) { usage(argv[0]); return 1; }
        return compile_qentl(argv[2], argv[3]);
    }
    if (strcmp(argv[1], "run") == 0) {
        if (argc < 3) { usage(argv[0]); return 1; }
        return run_qbc(argv[2]);
    }
    if (strcmp(argv[1], "qcompile") == 0) {
        if (argc < 4) { usage(argv[0]); return 1; }
        return compile_quantum(argv[2], argv[3]);
    }
    if (strcmp(argv[1], "disasm") == 0) {
        if (argc < 3) { usage(argv[0]); return 1; }
        return disasm_qbc(argv[2]);
    }

    /* 兼容模式 */
    const char *input = argv[1];
    if (argc >= 3) return compile_qentl(input, argv[2]);

    char tmp[512];
    snprintf(tmp, sizeof(tmp), "/tmp/qcl_exec_%d.qbc", getpid());
    int ret = compile_qentl(input, tmp);
    if (ret != 0) return ret;
    ret = run_qbc(tmp);
    remove(tmp);
    return ret;
}
