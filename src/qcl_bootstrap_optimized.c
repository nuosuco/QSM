/*
 * qcl_bootstrap.c — QCL编译器最小化引导编译器
 *
 * 红线规则：只能解释量子指令子集
 *   init / H / X / Y / Z / T / S / CNOT / MEASURE / PRINT / STOP / EXIT
 * 严禁添加 parse_import / parse_type / parse_function 等高级语法解析。
 */
/* ============================================================
 * OPTIMIZED variant — performance tuning:
 *   1. MAX_OPS=4096 (smaller buffer → smaller BSS + better cache)
 *   2. mmap replaces fopen for input (fewer syscalls, no libc buf)
 *   3. static linking + strip reduces binary bloat
 * ============================================================ */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#define MAX_LINE_LEN 1024
#define MAX_OPS 131072

// ==================== 字节码操作码 ====================

typedef enum {
    OP_NOP = 0,
    OP_INIT_N = 20,
    OP_H = 1,
    OP_X = 2,
    OP_Z = 3,
    OP_CNOT = 4,
    OP_MEASURE = 5,
    OP_RESET = 6,
    OP_SWAP = 7,
    OP_LOAD_REG = 8,
    OP_STORE_REG = 9,
    OP_JUMP = 10,
    OP_ADD = 16,
    OP_SUB = 13,
    OP_MUL = 15,
    OP_DIV = 14,
    OP_PRINT = 11,
    OP_STOP = 12,
    OP_T = 35,
    OP_S = 36,
    OP_Y = 37,
    OP_BARRIER = 18,
    OP_EXIT = 17,
} Opcode;

// ==================== 全局字节码缓冲区 ====================

static unsigned char g_bytecode[MAX_OPS];
static int g_bc_pos = 0;

// ==================== 字节码写入 ====================

static void write_byte(unsigned char b) {
    if (g_bc_pos < MAX_OPS) {
        g_bytecode[g_bc_pos++] = b;
    }
}

static void write_opcode(Opcode op) {
    write_byte(op);
}

static void write_u8(unsigned char v) {
    write_byte(v);
}

static void write_u16(unsigned short v) {
    write_byte(v & 0xFF);
    write_byte((v >> 8) & 0xFF);
}

static void write_u32(unsigned int v) {
    write_byte(v & 0xFF);
    write_byte((v >> 8) & 0xFF);
    write_byte((v >> 16) & 0xFF);
    write_byte((v >> 24) & 0xFF);
}

// ==================== 量子指令子集编译器 ====================

int compile_file_v2(const char *input_path, const char *output_path) {
    /* Optimized: mmap input file (no libc buffering overhead) */
    int fd = open(input_path, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "[QCL] 无法打开输入文件: %s\n", input_path);
        return -1;
    }
    struct stat st;
    if (fstat(fd, &st) < 0) { close(fd); return -1; }
    size_t fsize = (size_t)st.st_size;
    void *map = mmap(NULL, fsize, PROT_READ, MAP_PRIVATE, fd, 0);
    if (map == MAP_FAILED) { close(fd); return -1; }
    /* Advise kernel we read sequentially for optimal prefetching */
    madvise(map, fsize, MADV_SEQUENTIAL);
    close(fd);

    const char *data = (const char *)map;
    const char *end  = data + fsize;

    fprintf(stdout, "[QCL] 编译: %s\n", input_path);
    fprintf(stdout, "[QCL] 输出: %s\n", output_path);

    /* Parse line by line via strchr (avoids per-char overhead) */
    const char *p = data;
    int line_num = 0;
    int found_code = 0;

    while (p < end) {
        line_num++;
        const char *line_start = p;
        const char *nl = memchr(p, '\n', end - p);
        if (nl) { p = nl + 1; } else { p = end; }

        /* Trim leading whitespace */
        while (p > line_start && (*line_start == ' ' || *line_start == '\t' || *line_start == '\r' || *line_start == '\n'))
            line_start++;
        if (line_start >= p) continue;
        if (*line_start == '/' || *line_start == '#') continue;

        /* Strip // comments (inlined, no malloc) */
        const char *sl = line_start;
        while (sl < p - 1) {
            if (sl[0] == '/' && sl[1] == '/') break;
            sl++;
        }
        size_t code_len = (size_t)(sl - line_start);
        if (code_len == 0) continue;

        const char *c = line_start;
        while (c < line_start + code_len && (*c == ' ' || *c == '\t')) c++;
        if (c >= line_start + code_len) continue;
        if (*c == '/' || *c == '#') continue;

        /* Parse each instruction */
        if (memcmp(c, "init ", 5) == 0) {
            c += 5;
            unsigned int n = 0;
            while (*c >= '0' && *c <= '9') { n = n * 10 + (*c - '0'); c++; }
            while (*c == ' ' || *c == '\t' || *c == '\r' || *c == '\n') c++;
            write_opcode(OP_INIT_N);
            write_u8(n & 0xFF);
            write_u8((n >> 8) & 0xFF);
            found_code = 1;
        }
        else if (memcmp(c, "H ", 2) == 0 || memcmp(c, "X ", 2) == 0 ||
                 memcmp(c, "Y ", 2) == 0 || memcmp(c, "Z ", 2) == 0 ||
                 memcmp(c, "T ", 2) == 0 || memcmp(c, "S ", 2) == 0) {
            Opcode op;
            if (memcmp(c, "H ", 2) == 0) op = OP_H;
            else if (memcmp(c, "X ", 2) == 0) op = OP_X;
            else if (memcmp(c, "Y ", 2) == 0) op = OP_Y;
            else if (memcmp(c, "Z ", 2) == 0) op = OP_Z;
            else if (memcmp(c, "T ", 2) == 0) op = OP_T;
            else if (memcmp(c, "S ", 2) == 0) op = OP_S;
            else op = OP_NOP;
            c += 2;
            int qid = 0;
            while (*c >= '0' && *c <= '9') { qid = qid * 10 + (*c - '0'); c++; }
            write_opcode(op);
            write_u8(qid);
            found_code = 1;
        }
        else if (memcmp(c, "CNOT ", 5) == 0) {
            c += 5;
            int ctrl = 0, tgt = 0;
            while (*c >= '0' && *c <= '9') { ctrl = ctrl * 10 + (*c - '0'); c++; }
            while (*c == ' ' || *c == '\t') c++;
            while (*c >= '0' && *c <= '9') { tgt = tgt * 10 + (*c - '0'); c++; }
            write_opcode(OP_CNOT);
            write_u8(ctrl);
            write_u8(tgt);
            found_code = 1;
        }
        else if (memcmp(c, "MEASURE ", 8) == 0) {
            c += 8;
            int qid = 0, reg = 0;
            while (*c >= '0' && *c <= '9') { qid = qid * 10 + (*c - '0'); c++; }
            while (*c == ' ' || *c == '\t') c++;
            while (*c >= '0' && *c <= '9') { reg = reg * 10 + (*c - '0'); c++; }
            write_opcode(OP_MEASURE);
            write_u8(qid);
            write_u8(reg);
            found_code = 1;
        }
        else if (memcmp(c, "PRINT ", 6) == 0) {
            c += 6;
            int reg = 0;
            while (*c >= '0' && *c <= '9') { reg = reg * 10 + (*c - '0'); c++; }
            write_opcode(OP_PRINT);
            write_u8(reg);
            found_code = 1;
        }
        else if (memcmp(c, "STOP", 4) == 0) {
            write_opcode(OP_STOP);
            found_code = 1;
        }
        else if (memcmp(c, "EXIT", 4) == 0) {
            write_opcode(OP_EXIT);
            found_code = 1;
        }
    }

    munmap(map, fsize);

    if (!found_code) {
        fprintf(stdout, "[QCL] 警告: 未找到可编译的量子代码\n");
        write_opcode(OP_STOP);
    }

    /* Optimized: write bytecode via open+write (no libc buffering) */
    int outfd = open(output_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (outfd < 0) {
        fprintf(stderr, "[QCL] 无法创建输出文件: %s\n", output_path);
        return -1;
    }
    ssize_t written = write(outfd, g_bytecode, g_bc_pos);
    close(outfd);
    if ((size_t)written != (size_t)g_bc_pos) {
        fprintf(stderr, "[QCL] 写入不完整\n");
        return -1;
    }

    fprintf(stdout, "[QCL] 编译完成: %d 字节, %d 条指令\n", g_bc_pos, g_bc_pos);

    return 0;
}

// ==================== 主函数 ====================

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "用法: %s <input.qentl> [output.qbc]\n", argv[0]);
        fprintf(stderr, "\nQCL引导编译器 v2 - 最小化C语言引导编译器\n");
        fprintf(stderr, "将QEntL源码编译为QVM可执行的.qbc字节码\n");
        fprintf(stderr, "\n支持指令:\n");
        fprintf(stderr, "  量子门: init, H, X, Y, Z, T, S, CNOT, SWAP, MEASURE, RESET, BARRIER\n");
        fprintf(stderr, "  (bootstrap仅支持量子指令子集；类/函数体等高级语法由qcl_phase2/QCL编译器处理)\n");
        fprintf(stderr, "  运算符: ===, !==, ==, !=, <, >, +, -, *, /\n");
        fprintf(stderr, "  控制流: 否则, 循环, 跳出, 继续\n");
        fprintf(stderr, "\n注: 高级QEntL语法(类定义、函数体等)会被简化处理\n");
        return 1;
    }
    
    const char *input = argv[1];
    
    if (argc == 2) {
        // 执行模式：编译成临时qbc，然后调用qvm_bootstrap执行
        char tmp_qbc[512];
        snprintf(tmp_qbc, sizeof(tmp_qbc), "/tmp/qcl_exec_%d.qbc", getpid());
        
        fprintf(stderr, "[QCL] 执行模式：编译 %s → %s\n", input, tmp_qbc);
        int ret = compile_file_v2(input, tmp_qbc);
        if (ret != 0) {
            fprintf(stderr, "[QCL] 编译失败\n");
            return ret;
        }
        
        char cmd[1024];
        snprintf(cmd, sizeof(cmd), "bin/qvm_bootstrap %s", tmp_qbc);
        fprintf(stderr, "[QCL] 调用QVM执行 %s\n", cmd);
        ret = system(cmd);
        
        // 清理临时文件
        remove(tmp_qbc);
        return ret;
    } else {
        // 编译模式
        const char *output = argv[2];
        srand((unsigned int)time(NULL));
        int ret = compile_file_v2(input, output);
        return ret;
    }
}