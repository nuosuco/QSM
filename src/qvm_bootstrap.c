/*
 * qvm_bootstrap.c — QVM量子虚拟机 C语言启动器
 * ⚠️ 只作为启动器，真正计算由QEntL全栈执行
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <dirent.h>
#include <sys/stat.h>

#define MAX_QUBITS 64
#define MAX_REGISTERS 64
#define MAX_MEM 256 * 1024 * 1024  /* 256MB for up to 22 qubits */
#define MAX_CYCLES 10000
#define MAX_PATH 1024
#define MAX_FILE_SIZE 1024 * 1024  // 1MB max file read

/* 操作码 — 与qcl_bootstrap.c编译器严格对齐 */
enum {
    OP_NOP = 0,
    OP_H = 1,
    OP_X = 2,
    OP_Y = 37,   // 编译器OP_Y=37
    OP_Z = 3,
    OP_CNOT = 4,
    OP_MEASURE = 5,
    OP_RESET = 6,
    OP_SWAP = 7,
    OP_LOAD = 8,
    OP_STORE = 9,
    OP_JUMP = 10,
    OP_PRINT = 11,
    OP_STOP = 12,
    OP_ADD = 13,
    OP_MUL = 15,
    OP_EXIT = 17,
    OP_T = 35,
    OP_S = 36,
    OP_BARRIER = 18,
    OP_INIT = 20,   // 编译器OP_INIT_N=20, 0x14=20
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

// ============================================================
// QEntL文件操作函数（供QCL引导器调用）
// ============================================================

// 文件读取 — 读取完整文件内容到字符串
char *qentl_read_file(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) {
        printf("[QVM] 文件读取失败: %s\n", path);
        return NULL;
    }
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (size > MAX_FILE_SIZE) {
        printf("[QVM] 文件过大: %s (%ld bytes)\n", path, size);
        fclose(f);
        return NULL;
    }
    char *content = (char *)malloc(size + 1);
    if (!content) {
        fclose(f);
        return NULL;
    }
    fread(content, 1, size, f);
    content[size] = '\0';
    fclose(f);
    printf("[QVM] 文件读取成功: %s (%ld bytes)\n", path, size);
    return content;
}

// 文件写入 — 将字符串写入文件
int qentl_write_file(const char *path, const char *content, int length) {
    FILE *f = fopen(path, "wb");
    if (!f) {
        printf("[QVM] 文件写入失败: %s\n", path);
        return -1;
    }
    fwrite(content, 1, length, f);
    fclose(f);
    printf("[QVM] 文件写入成功: %s (%d bytes)\n", path, length);
    return 0;
}

// 目录扫描 — 列出目录下的所有文件/目录
int qentl_list_dir(const char *path, char **entries, int max_entries) {
    DIR *dir = opendir(path);
    if (!dir) {
        printf("[QVM] 目录扫描失败: %s\n", path);
        return -1;
    }
    int count = 0;
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL && count < max_entries) {
        if (entry->d_name[0] == '.' && (entry->d_name[1] == '\0' || 
            (entry->d_name[1] == '.' && entry->d_name[2] == '\0'))) {
            continue; // 跳过.和..
        }
        strncpy(entries[count], entry->d_name, MAX_PATH - 1);
        entries[count][MAX_PATH - 1] = '\0';
        count++;
    }
    closedir(dir);
    printf("[QVM] 目录扫描完成: %s (%d entries)\n", path, count);
    return count;
}

// 路径连接 — 连接两个路径
void qentl_path_join(char *dest, const char *dir, const char *file) {
    strncpy(dest, dir, MAX_PATH - 1);
    dest[MAX_PATH - 1] = '\0';
    int len = strlen(dest);
    if (len > 0 && dest[len - 1] != '/') {
        dest[len] = '/';
        dest[len + 1] = '\0';
    }
    strncat(dest, file, MAX_PATH - strlen(dest) - 1);
}

// 判断路径是否是目录
int qentl_is_dir(const char *path) {
    struct stat st;
    if (stat(path, &st) != 0) return 0;
    return S_ISDIR(st.st_mode);
}

// 判断字符串是否以后缀结尾
int qentl_ends_with(const char *str, const char *suffix) {
    int str_len = strlen(str);
    int suffix_len = strlen(suffix);
    if (suffix_len > str_len) return 0;
    return strcmp(str + str_len - suffix_len, suffix) == 0;
}

// ============================================================
// QEntL源码编译器（供QCL引导器调用）
// ============================================================

// 行缓冲区结构
typedef struct {
    char *buffer;
    int size;
} LineBuf;

static void linebuf_init(LineBuf *lb) {
    lb->size = 1024;
    lb->buffer = (char *)malloc(lb->size);
    lb->buffer[0] = '\0';
}

static void linebuf_append(LineBuf *lb, const char *s) {
    int need = strlen(s) + 1;
    if (strlen(lb->buffer) + need >= lb->size) {
        lb->size *= 2;
        lb->buffer = (char *)realloc(lb->buffer, lb->size);
    }
    strcat(lb->buffer, s);
}

static char *linebuf_get(LineBuf *lb) {
    return lb->buffer;
}

// 写入字节码
static void write_opcode(uint8_t **out, int *pos, uint8_t op, ...) {
    va_list args;
    va_start(args, op);
    (*out)[(*pos)++] = op;
    int num = op;
    switch(num) {
        case OP_H: case OP_X: case OP_Y: case OP_Z:
        case OP_T: case OP_S: case OP_RESET: {
            int q = va_arg(args, int);
            (*out)[(*pos)++] = q;
            break;
        }
        case OP_CNOT: case OP_SWAP: case OP_MEASURE: {
            int a = va_arg(args, int);
            int b = va_arg(args, int);
            (*out)[(*pos)++] = a;
            (*out)[(*pos)++] = b;
            break;
        }
        case OP_LOAD: case OP_STORE: {
            int r = va_arg(args, int);
            (*out)[(*pos)++] = r;
            break;
        }
        case OP_JUMP: case OP_JZ: {
            int target = va_arg(args, int);
            (*out)[(*pos)++] = target;
            break;
        }
        default:
            // NOP, STOP, PRINT, EXIT, INIT, BARRIER - 可能需要参数
            break;
    }
    va_end(args);
}

// 编译QEntL源码文件为.qbc字节码
int compile_qentl_to_qbc(const char *input_path, const char *output_path) {
    char *src = qentl_read_file(input_path);
    if (!src) {
        printf("[QVM] 编译失败: 无法读取 %s\n", input_path);
        return -1;
    }
    
    printf("[QVM] 编译QEntL源码: %s -> %s\n", input_path, output_path);
    
    // 分配字节码缓冲区
    int buf_size = strlen(src) * 4;
    uint8_t *code = (uint8_t *)calloc(buf_size, 1);
    int pos = 0;
    int line_num = 0;
    
    // 逐行编译
    char *line_start = src;
    char *p = src;
    char temp[MAX_FILE_SIZE];
    
    while (*p) {
        if (*p == '\n') {
            *p = '\0';
            char *line = line_start;
            line_num++;
            
            // 跳过空行和注释
            while (*line && (*line == ' ' || *line == '\t')) line++;
            if (*line == '/' && *(line+1) == '/') {
                // 单行注释
                line_start = p + 1;
                p++;
                continue;
            }
            if (*line == '/' && *(line+1) == '*') {
                // 多行注释开始
                char *end = strstr(p, "*/");
                if (end) {
                    line_start = end + 2;
                    p = end + 2;
                    continue;
                }
            }
            
            // 编译量子指令
            char trimmed[MAX_FILE_SIZE];
            strncpy(trimmed, line, MAX_FILE_SIZE - 1);
            trimmed[MAX_FILE_SIZE - 1] = '\0';
            
            // 去除首尾空格
            char *t = trimmed;
            while (*t && (*t == ' ' || *t == '\t')) t++;
            char *end2 = t + strlen(t) - 1;
            while (end2 > t && (*end2 == ' ' || *end2 == '\t')) {
                *end2 = '\0';
                end2--;
            }
            
            // 跳过空行
            if (*t == '\0') {
                line_start = p + 1;
                p++;
                continue;
            }
            
            // 跳过高级语法（def/import/var/class等）
            if (strncmp(t, "def ", 4) == 0 || strncmp(t, "import ", 7) == 0 ||
                strncmp(t, "var ", 4) == 0 || strncmp(t, "class ", 6) == 0 ||
                strncmp(t, "const ", 6) == 0 || strncmp(t, "while ", 6) == 0 ||
                strncmp(t, "if ", 3) == 0 || strncmp(t, "else", 4) == 0 ||
                strncmp(t, "return ", 7) == 0 || strncmp(t, "break", 5) == 0 ||
                strncmp(t, "continue", 8) == 0 || strncmp(t, "for ", 4) == 0 ||
                t[0] == '/' || t[0] == '}') {
                line_start = p + 1;
                p++;
                continue;
            }
            
            // 编译量子指令
            int parsed = 0;
            
            // init N
            if (strncmp(t, "init ", 5) == 0) {
                int n = atoi(t + 5);
                write_opcode(&code, &pos, OP_INIT, n);
                parsed = 1;
            }
            // H q
            else if (strncmp(t, "H ", 2) == 0) {
                int q = atoi(t + 2);
                write_opcode(&code, &pos, OP_H, q);
                parsed = 1;
            }
            // X q
            else if (strncmp(t, "X ", 2) == 0) {
                int q = atoi(t + 2);
                write_opcode(&code, &pos, OP_X, q);
                parsed = 1;
            }
            // Y q
            else if (strncmp(t, "Y ", 2) == 0) {
                int q = atoi(t + 2);
                write_opcode(&code, &pos, OP_Y, q);
                parsed = 1;
            }
            // Z q
            else if (strncmp(t, "Z ", 2) == 0) {
                int q = atoi(t + 2);
                write_opcode(&code, &pos, OP_Z, q);
                parsed = 1;
            }
            // T q
            else if (strncmp(t, "T ", 2) == 0) {
                int q = atoi(t + 2);
                write_opcode(&code, &pos, OP_T, q);
                parsed = 1;
            }
            // S q
            else if (strncmp(t, "S ", 2) == 0) {
                int q = atoi(t + 2);
                write_opcode(&code, &pos, OP_S, q);
                parsed = 1;
            }
            // CNOT c t
            else if (strncmp(t, "CNOT ", 5) == 0) {
                char *s = t + 5;
                while (*s && (*s == ' ' || *s == '\t')) s++;
                int c = atoi(s);
                while (*s && (*s == ' ' || *s == '\t')) s++;
                int t2 = atoi(s);
                write_opcode(&code, &pos, OP_CNOT, c, t2);
                parsed = 1;
            }
            // SWAP a b
            else if (strncmp(t, "SWAP ", 5) == 0) {
                char *s = t + 5;
                while (*s && (*s == ' ' || *s == '\t')) s++;
                int a = atoi(s);
                while (*s && (*s == ' ' || *s == '\t')) s++;
                int b = atoi(s);
                write_opcode(&code, &pos, OP_SWAP, a, b);
                parsed = 1;
            }
            // MEASURE q r
            else if (strncmp(t, "MEASURE ", 8) == 0) {
                char *s = t + 8;
                while (*s && (*s == ' ' || *s == '\t')) s++;
                int q = atoi(s);
                while (*s && (*s == ' ' || *s == '\t')) s++;
                int r = atoi(s);
                write_opcode(&code, &pos, OP_MEASURE, q, r);
                parsed = 1;
            }
            // PRINT r
            else if (strncmp(t, "PRINT ", 6) == 0) {
                char *s = t + 6;
                while (*s && (*s == ' ' || *s == '\t')) s++;
                int r = atoi(s);
                write_opcode(&code, &pos, OP_PRINT, r);
                parsed = 1;
            }
            // RESET q
            else if (strncmp(t, "RESET ", 6) == 0) {
                int q = atoi(t + 6);
                write_opcode(&code, &pos, OP_RESET, q);
                parsed = 1;
            }
            // BARRIER
            else if (strncmp(t, "BARRIER", 7) == 0) {
                write_opcode(&code, &pos, OP_BARRIER);
                parsed = 1;
            }
            // STOP
            else if (strncmp(t, "STOP", 4) == 0) {
                write_opcode(&code, &pos, OP_STOP);
                parsed = 1;
            }
            // EXIT
            else if (strncmp(t, "EXIT", 4) == 0) {
                write_opcode(&code, &pos, OP_EXIT);
                parsed = 1;
            }
            
            if (!parsed) {
                printf("[QVM] 跳过无法编译的行: %s\n", t);
            }
            
            line_start = p + 1;
            p++;
        } else {
            p++;
        }
    }
    
    if (pos == 0) {
        printf("[QVM] 编译失败: %s 无有效量子指令\n", input_path);
        free(src);
        free(code);
        return -1;
    }
    
    // 写入.qbc文件
    FILE *out = fopen(output_path, "wb");
    if (!out) {
        printf("[QVM] 编译失败: 无法写入 %s\n", output_path);
        free(src);
        free(code);
        return -1;
    }
    fwrite(code, 1, pos, out);
    fclose(out);
    
    printf("[QVM] 编译成功: %s (%d bytes, %d instructions)\n", output_path, pos, line_num);
    free(src);
    free(code);
    return 0;
}

// 扫描目录并编译所有QEntL文件
int compile_qentl_directory(const char *dir_path, const char *output_dir) {
    char entries[100][MAX_PATH];
    char full_path[MAX_PATH];
    char out_path[MAX_PATH];
    int count = qentl_list_dir(dir_path, entries, 100);
    
    if (count < 0) return -1;
    
    int compiled = 0;
    for (int i = 0; i < count; i++) {
        qentl_path_join(full_path, dir_path, entries[i]);
        
        if (qentl_is_dir(full_path)) {
            qentl_path_join(out_path, output_dir, entries[i]);
            if (mkdir(out_path, 0755) == 0) {
                int sub = compile_qentl_directory(full_path, out_path);
                if (sub >= 0) compiled += sub;
            }
        } else if (qentl_ends_with(entries[i], ".qentl")) {
            qentl_path_join(out_path, output_dir, entries[i]);
            // 替换扩展名 .qentl -> .qbc
            char *ext = strstr(out_path, ".qentl");
            if (ext) {
                *ext = '\0';
                strcat(out_path, ".qbc");
            }
            if (compile_qentl_to_qbc(full_path, out_path) == 0) {
                compiled++;
            }
        }
    }
    
    return compiled;
}

// 包含va_list
#include <stdarg.h>

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
        default: break;
        }
    }

    printf("[QVM] 执行完成: %d 周期, %d 门操作\n", vm.cycles, vm.ops);
    free(code);
    return 0;
}
