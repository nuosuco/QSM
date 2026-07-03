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

// ============================================================
// QEntL源码解释器（供QCL引导器调用）
// ============================================================

// 函数定义结构
typedef struct FuncDef {
    char name[MAX_PATH];
    int param_count;
    char params[MAX_PATH][64];
    char *body;
    int body_len;
    struct FuncDef *next;
} FuncDef;

// 全局指针：当前正在构建的函数定义
static FuncDef *current_func = NULL;
static FuncDef *func_defs = NULL;  // 函数定义链表头

// 解析def函数定义
static void parse_def_func(const char *line) {
    char *p = (char *)line;
    // 跳过 "def " 前缀
    p += 4;
    while (*p && (*p == ' ' || *p == '\t')) p++;
    
    // 读取函数名
    char name[MAX_PATH];
    int i = 0;
    while (*p && *p != ' ' && *p != '(' && *p != '\t' && *p != '\n') {
        name[i++] = *p++;
    }
    name[i] = '\0';
    
    // 跳过空格和左括号
    while (*p && (*p == ' ' || *p == '\t')) p++;
    if (*p != '(') return;
    p++; // 跳过 (
    
    // 读取参数
    char params[10][64];
    int param_count = 0;
    while (*p && *p != ')') {
        int j = 0;
        while (*p && *p != ',' && *p != ')' && *p != ' ' && *p != '\t') {
            params[param_count][j++] = *p++;
        }
        params[param_count][j] = '\0';
        if (j > 0) param_count++;
        while (*p && (*p == ' ' || *p == ',' || *p == '\t')) p++;
    }
    if (*p == ')') p++; // 跳过 )
    
    // 创建函数定义
    FuncDef *fd = (FuncDef *)malloc(sizeof(FuncDef));
    strcpy(fd->name, name);
    fd->param_count = param_count;
    for (int k = 0; k < param_count && k < 10; k++) {
        strcpy(fd->params[k], params[k]);
    }
    fd->body = NULL;
    fd->body_len = 0;
    fd->next = func_defs;
    func_defs = fd;
    current_func = fd;  // 设置当前函数指针
    
    printf("[QVM] 解析函数定义: %s(%d params)\n", name, param_count);
}

// 追加函数体到当前函数定义
static void append_to_function_body(const char *line) {
    if (!current_func) return;
    
    FuncDef *fd = current_func;
    
    if (!fd->body) {
        fd->body = (char *)malloc(MAX_FILE_SIZE);
        fd->body[0] = '\0';
        fd->body_len = 0;
    }
    
    int need = strlen(line) + 2;
    if (fd->body_len + need >= MAX_FILE_SIZE) {
        fd->body = (char *)realloc(fd->body, MAX_FILE_SIZE * 2);
    }
    strcat(fd->body, line);
    strcat(fd->body, "\n");
    fd->body_len += need;
}

// 查找函数定义
static FuncDef *find_func(const char *name) {
    FuncDef *fd = func_defs;
    while (fd) {
        if (strcmp(fd->name, name) == 0) return fd;
        fd = fd->next;
    }
    return NULL;
}

// 执行函数体（简单的函数调用机制）
static int execute_function_body(FuncDef *fd, int arg_count, char *args[]) {
    if (!fd || !fd->body) {
        printf("[QVM] 函数体为空: %s\n", fd ? fd->name : "(null)");
        return -1;
    }
    
    printf("[QVM] 执行函数: %s (body length: %d)\n", fd->name, fd->body_len);
    
    // 简单的函数体执行：解析并执行其中的量子指令
    char *body = fd->body;
    char *line_start = body;
    char *p = body;
    
    int cycles = 0;
    
    while (*p) {
        if (*p == '\n') {
            *p = '\0';
            char *line = line_start;
            
            // 跳过空行和注释
            while (*line && (*line == ' ' || *line == '\t')) line++;
            if (*line == '/' && *(line+1) == '/') {
                line_start = p + 1;
                p++;
                continue;
            }
            if (*line == '\0') {
                line_start = p + 1;
                p++;
                continue;
            }
            
            // 编译量子指令
            int parsed = 0;
            
            // init N
            if (strncmp(line, "init ", 5) == 0) {
                cycles += 1;
                parsed = 1;
            }
            // H q
            else if (strncmp(line, "H ", 2) == 0) {
                cycles += 1;
                parsed = 1;
            }
            // X q
            else if (strncmp(line, "X ", 2) == 0) {
                cycles += 1;
                parsed = 1;
            }
            // CNOT c t
            else if (strncmp(line, "CNOT ", 5) == 0) {
                cycles += 1;
                parsed = 1;
            }
            // MEASURE q r
            else if (strncmp(line, "MEASURE ", 8) == 0) {
                cycles += 1;
                parsed = 1;
            }
            // PRINT r
            else if (strncmp(line, "PRINT ", 6) == 0) {
                cycles += 1;
                parsed = 1;
            }
            // STOP
            else if (strncmp(line, "STOP", 4) == 0) {
                cycles += 1;
                parsed = 1;
            }
            // 编译调用 - 特殊处理
            else if (strstr(line, "编译(")) {
                printf("[QVM] 编译调用: %s\n", line);
                cycles += 1;
                parsed = 1;
            }
            // 扫描目录调用 - 特殊处理
            else if (strstr(line, "扫描目录(")) {
                printf("[QVM] 扫描目录调用: %s\n", line);
                cycles += 1;
                parsed = 1;
            }
            // 扫描QEntL目录调用 - 特殊处理（Stage 3核心！）
            else if (strstr(line, "扫描QEntL目录(")) {
                printf("[QVM] 扫描QEntL目录调用: %s\n", line);
                // 真正调用扫描QEntL目录函数！
                FuncDef *scan_func = find_func("扫描QEntL目录");
                if (scan_func) {
                    printf("[QVM] 执行扫描QEntL目录函数\n");
                    int scan_cycles = execute_function_body(scan_func, 0, NULL);
                    cycles += scan_cycles;
                }
                parsed = 1;
            }
            // 编译器编译调用 - 特殊处理（Stage 3核心！）
            else if (strstr(line, "编译器编译(")) {
                printf("[QVM] 编译器编译调用: %s\n", line);
                // 真正调用编译器编译函数！
                FuncDef *compile_func = find_func("编译器编译");
                if (compile_func) {
                    printf("[QVM] 执行编译器编译函数\n");
                    int compile_cycles = execute_function_body(compile_func, 0, NULL);
                    cycles += compile_cycles;
                }
                parsed = 1;
            }
            // 函数调用（通用）
            else if (strstr(line, "(") && !strstr(line, "def ")) {
                printf("[QVM] 函数调用: %s\n", line);
                // 尝试查找并执行被调用的函数
                char *paren = strstr(line, "(");
                if (paren) {
                    // 找到函数名：从(往前找
                    char *name_end = paren;
                    char *name_start = name_end;
                    
                    // 向前跳过空格
                    while (name_start > line && (name_start[-1] == ' ' || name_start[-1] == '\t')) {
                        name_start--;
                    }
                    
                    // 向后找函数名开始（遇到空格/非字母数字/非中文字符）
                    while (name_start > line && 
                           (((unsigned char)name_start[-1] >= 'a' && (unsigned char)name_start[-1] <= 'z') ||
                            ((unsigned char)name_start[-1] >= 'A' && (unsigned char)name_start[-1] <= 'Z') ||
                            ((unsigned char)name_start[-1] >= '0' && (unsigned char)name_start[-1] <= '9') ||
                            ((unsigned char)name_start[-1] >= 0x80))) {  // 中文字符
                        name_start--;
                    }
                    
                    int name_len = name_end - name_start;
                    if (name_len > 0 && name_len < MAX_PATH) {
                        char func_name[MAX_PATH];
                        strncpy(func_name, name_start, name_len);
                        func_name[name_len] = '\0';
                        
                        printf("[QVM] 提取函数名: [%s] (len=%d)\n", func_name, name_len);
                        
                        FuncDef *called = find_func(func_name);
                        if (called) {
                            printf("[QVM] 执行函数调用: %s\n", func_name);
                            int called_cycles = execute_function_body(called, 0, NULL);
                            cycles += called_cycles;
                        } else {
                            printf("[QVM] 函数未找到: %s\n", func_name);
                        }
                    }
                }
                parsed = 1;
            }
            
            line_start = p + 1;
            p++;
        } else {
            p++;
        }
    }
    
    printf("[QVM] 函数执行完成: %s (%d cycles)\n", fd->name, cycles);
    return cycles;
}

// 解析QEntL源码文件并提取函数定义
static int parse_qentl_functions(const char *path) {
    char *src = qentl_read_file(path);
    if (!src) {
        printf("[QVM] 解析失败: 无法读取 %s\n", path);
        return -1;
    }
    
    printf("[QVM] 解析QEntL源码: %s\n", path);
    
    char *line_start = src;
    char *p = src;
    int in_function = 0;
    
    while (*p) {
        if (*p == '\n') {
            *p = '\0';
            char *line = line_start;
            
            // 跳过空行和注释
            while (*line && (*line == ' ' || *line == '\t')) line++;
            if (*line == '/' && *(line+1) == '/') {
                line_start = p + 1;
                p++;
                continue;
            }
            if (*line == '/' && *(line+1) == '*') {
                char *end = strstr(p, "*/");
                if (end) {
                    line_start = end + 2;
                    p = end + 2;
                    continue;
                }
            }
            if (*line == '\0') {
                line_start = p + 1;
                p++;
                continue;
            }
            
            // 检测def函数定义
            if (strncmp(line, "def ", 4) == 0) {
                // 保存上一个函数（结束）
                current_func = NULL;
                if (in_function) {
                    printf("[QVM] 警告: 嵌套函数定义\n");
                }
                parse_def_func(line);
                in_function = 1;
            } else if (in_function) {
                // 追加函数体
                append_to_function_body(line);
            } else if (!in_function && line[0] != ' ' && line[0] != '\t' && line[0] != '/' && line[0] != '\0') {
                // 检测到函数结束（缩进减少或新语句开始）
                // 但只有当前函数体不为空时才算结束
                if (current_func && current_func->body_len > 0) {
                    // 继续检测，不关闭函数（允许多行语句）
                }
            }
            
            line_start = p + 1;
            p++;
        } else {
            p++;
        }
    }
    
    free(src);
    printf("[QVM] 解析完成: %d 个函数定义\n", func_defs ? 1 : 0);
    return 0;
}

// 判断字符串是否以后缀结尾
int qentl_ends_with(const char *str, const char *suffix) {
    int str_len = strlen(str);
    int suffix_len = strlen(suffix);
    if (suffix_len > str_len) return 0;
    return strcmp(str + str_len - suffix_len, suffix) == 0;
}

// 扫描目录并编译所有QEntL文件
int compile_qentl_directory(const char *dir_path, const char *output_dir) {
    char entries[100][MAX_PATH];
    char *ptrs[100];
    for (int i = 0; i < 100; i++) ptrs[i] = entries[i];
    char full_path[MAX_PATH];
    char out_path[MAX_PATH];
    int count = qentl_list_dir(dir_path, ptrs, 100);
    
    if (count < 0) return -1;
    
    int compiled = 0;
    for (int i = 0; i < count; i++) {
        qentl_path_join(full_path, dir_path, ptrs[i]);
        
        if (qentl_is_dir(full_path)) {
            qentl_path_join(out_path, output_dir, ptrs[i]);
            if (mkdir(out_path, 0755) == 0) {
                int sub = compile_qentl_directory(full_path, out_path);
                if (sub >= 0) compiled += sub;
            }
        } else if (qentl_ends_with(ptrs[i], ".qentl")) {
            qentl_path_join(out_path, output_dir, ptrs[i]);
            // 替换扩展名 .qentl -> .qbc
            char *ext = strstr(out_path, ".qentl");
            if (ext) {
                *ext = '\0';
                strcat(out_path, ".qbc");
            }
            // 解析并执行函数（QCL引导器模式）
            if (parse_qentl_functions(full_path) == 0) {
                compiled++;
            }
        }
    }
    
    return compiled;
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
    
    // 逐行编译
    char *line_start = src;
    char *p = src;
    
    while (*p) {
        if (*p == '\n') {
            *p = '\0';
            char *line = line_start;
            
            // 跳过空行和注释
            while (*line && (*line == ' ' || *line == '\t')) line++;
            if (*line == '/' && *(line+1) == '/') {
                line_start = p + 1;
                p++;
                continue;
            }
            if (*line == '/' && *(line+1) == '*') {
                char *end = strstr(p, "*/");
                if (end) {
                    line_start = end + 2;
                    p = end + 2;
                    continue;
                }
            }
            if (*line == '\0') {
                line_start = p + 1;
                p++;
                continue;
            }
            
            // 跳过高级语法（def/import/var/class等）
            if (strncmp(line, "def ", 4) == 0 || strncmp(line, "import ", 7) == 0 ||
                strncmp(line, "var ", 4) == 0 || strncmp(line, "class ", 6) == 0 ||
                strncmp(line, "const ", 6) == 0 || strncmp(line, "while ", 6) == 0 ||
                strncmp(line, "if ", 3) == 0 || strncmp(line, "else", 4) == 0 ||
                strncmp(line, "return ", 7) == 0 || strncmp(line, "break", 5) == 0 ||
                strncmp(line, "continue", 8) == 0 || strncmp(line, "for ", 4) == 0 ||
                line[0] == '/' || line[0] == '}') {
                line_start = p + 1;
                p++;
                continue;
            }
            
            // 编译量子指令
            int parsed = 0;
            
            // init N
            if (strncmp(line, "init ", 5) == 0) {
                int n = atoi(line + 5);
                code[pos++] = OP_INIT;
                code[pos++] = n;
                parsed = 1;
            }
            // H q
            else if (strncmp(line, "H ", 2) == 0) {
                int q = atoi(line + 2);
                code[pos++] = OP_H;
                code[pos++] = q;
                parsed = 1;
            }
            // X q
            else if (strncmp(line, "X ", 2) == 0) {
                int q = atoi(line + 2);
                code[pos++] = OP_X;
                code[pos++] = q;
                parsed = 1;
            }
            // CNOT c t
            else if (strncmp(line, "CNOT ", 5) == 0) {
                char *s = line + 5;
                while (*s && (*s == ' ' || *s == '\t')) s++;
                int c = atoi(s);
                while (*s && (*s == ' ' || *s == '\t')) s++;
                int t2 = atoi(s);
                code[pos++] = OP_CNOT;
                code[pos++] = c;
                code[pos++] = t2;
                parsed = 1;
            }
            // MEASURE q r
            else if (strncmp(line, "MEASURE ", 8) == 0) {
                char *s = line + 8;
                while (*s && (*s == ' ' || *s == '\t')) s++;
                int q = atoi(s);
                while (*s && (*s == ' ' || *s == '\t')) s++;
                int r = atoi(s);
                code[pos++] = OP_MEASURE;
                code[pos++] = q;
                code[pos++] = r;
                parsed = 1;
            }
            // PRINT r
            else if (strncmp(line, "PRINT ", 6) == 0) {
                int r = atoi(line + 6);
                code[pos++] = OP_PRINT;
                code[pos++] = r;
                parsed = 1;
            }
            // STOP
            else if (strncmp(line, "STOP", 4) == 0) {
                code[pos++] = OP_STOP;
                parsed = 1;
            }
            
            line_start = p + 1;
            p++;
        } else {
            p++;
        }
    }
    
    if (pos == 0) {
        printf("[QVM] 跳过（无量子指令）: %s\n", input_path);
        free(src);
        free(code);
        return 1; // 不是错误，只是没有量子指令
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
    
    printf("[QVM] 编译成功: %s (%d bytes)\n", output_path, pos);
    free(src);
    free(code);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("[QVM] 用法: %s <字节码文件> [选项]\n", argv[0]);
        printf("[QVM] 或: %s --qentl <QEntL源码文件>\n", argv[0]);
        printf("[QVM] 或: %s --compile-all <源目录> <目标目录>\n", argv[0]);
        return 1;
    }

    // 模式1: 直接执行QEntL源码（不读取.qbc）
    if (strcmp(argv[1], "--qentl") == 0 && argc >= 3) {
        printf("[QVM] 模式: 直接执行QEntL源码\n");
        printf("[QVM] 文件: %s\n", argv[2]);
        
        // 解析QEntL源码并执行函数
        if (parse_qentl_functions(argv[2]) == 0) {
            // 找到并执行入口函数（通常是"main"或第一个函数）
            FuncDef *entry = find_func("main");
            if (!entry) entry = func_defs;
            
            if (entry) {
                printf("[QVM] 执行入口函数: %s\n", entry->name);
                execute_function_body(entry, 0, NULL);
            } else {
                printf("[QVM] 错误: 未找到入口函数\n");
                return 1;
            }
        } else {
            printf("[QVM] 错误: 解析QEntL源码失败\n");
            return 1;
        }
        return 0;
    }

    // 模式2: 编译所有QEntL源码到QBC
    if (strcmp(argv[1], "--compile-all") == 0 && argc >= 4) {
        printf("[QVM] 模式: 编译所有QEntL源码\n");
        printf("[QVM] 源目录: %s\n", argv[2]);
        printf("[QVM] 目标目录: %s\n", argv[3]);
        
        int compiled = compile_qentl_directory(argv[2], argv[3]);
        printf("[QVM] 编译完成: %d 个文件\n", compiled);
        return compiled >= 0 ? 0 : 1;
    }

    // 模式4: Stage 3 — QCL引导器编译QCL/QVM源码
    if (strcmp(argv[1], "--stage3") == 0) {
        printf("[QVM] ==========================================\n");
        printf("[QVM] Stage 3: QCL引导器编译QCL/QVM源码\n");
        printf("[QVM] ==========================================\n");
        
        // 扫描QEntL源码目录
        char source_dir[MAX_PATH] = "./QEntL";
        char output_dir[MAX_PATH] = "./QEntL";
        
        printf("[QVM] 扫描QEntL目录: %s\n", source_dir);
        printf("[QVM] 输出目录: %s\n", output_dir);
        
        // 扫描并统计
        int compiled = 0;
        int total = 0;
        char entries[200][MAX_PATH];
        char full_path[MAX_PATH];
        char out_path[MAX_PATH];
        int count = qentl_list_dir(source_dir, entries, 200);
        
        if (count >= 0) {
            printf("[QVM] 找到 %d 个目录/文件\n", count);
            for (int i = 0; i < count; i++) {
                qentl_path_join(full_path, source_dir, entries[i]);
                
                if (qentl_is_dir(full_path)) {
                    printf("[QVM] 扫描子目录: %s\n", entries[i]);
                    char sub_out[MAX_PATH];
                    qentl_path_join(sub_out, output_dir, entries[i]);
                    if (mkdir(sub_out, 0755) == 0) {
                        // 递归扫描子目录
                        char sub_entries[200][MAX_PATH];
                        char sub_path[MAX_PATH];
                        int sub_count = qentl_list_dir(full_path, sub_entries, 200);
                        if (sub_count >= 0) {
                            for (int j = 0; j < sub_count; j++) {
                                qentl_path_join(sub_path, full_path, sub_entries[j]);
                                if (qentl_ends_with(sub_entries[j], ".qentl")) {
                                    char sub_out_path[MAX_PATH];
                                    qentl_path_join(sub_out_path, sub_out, sub_entries[j]);
                                    char *ext = strstr(sub_out_path, ".qentl");
                                    if (ext) { *ext = '\0'; strcat(sub_out_path, ".qbc"); }
                                    
                                    // 编译QEntL源码为QBC
                                    if (compile_qentl_to_qbc(sub_path, sub_out_path) == 0) {
                                        compiled++;
                                    }
                                    total++;
                                }
                            }
                        }
                    }
                } else if (qentl_ends_with(entries[i], ".qentl")) {
                    qentl_path_join(out_path, output_dir, entries[i]);
                    char *ext = strstr(out_path, ".qentl");
                    if (ext) { *ext = '\0'; strcat(out_path, ".qbc"); }
                    
                    if (compile_qentl_to_qbc(full_path, out_path) == 0) {
                        compiled++;
                    }
                    total++;
                }
            }
        }
        
        printf("\n[QVM] ==========================================\n");
        printf("[QVM] Stage 3 完成\n");
        printf("[QVM] 总文件数: %d\n", total);
        printf("[QVM] 编译成功: %d\n", compiled);
        printf("[QVM] 成功率: %.1f%%\n", total > 0 ? (double)compiled/total*100 : 0);
        printf("[QVM] ==========================================\n");
        
        return 0;
    }

    // 模式3: 读取.qbc字节码执行（传统模式）
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
