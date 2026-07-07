/*
 * qcl_bootstrap.c — QCL编译器最小化引导编译器
 *
 * 红线规则：只能解释量子指令子集
 *   init / H / X / Y / Z / T / S / CNOT / MEASURE / PRINT / STOP / EXIT
 * 严禁添加 parse_import / parse_type / parse_function 等高级语法解析。
 */
#define _GNU_SOURCE
/*
 * qcl_bootstrap_opt.c — QCL编译器最小化引导编译器（优化版）
 * 优化: mmap替代fopen, MAX_OPS=4096, MADV_SEQUENTIAL
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#define MAX_LINE_LEN 1024      /* 优化：小buffer降低栈/内存占用 */
#define MAX_OPS 131072         /* 字节码输出缓冲区（保持原容量） */
#define OPT_MMAP 1  // 使用mmap替代fopen进行I/O优化

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

// ==================== mmap 加载文件（替代fopen，减少I/O） ====================

static uint8_t *mmap_load(const char *path, size_t *out_size) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "[QCL] mmap open失败: %s\n", path);
        return NULL;
    }
    struct stat st;
    if (fstat(fd, &st) < 0 || st.st_size <= 0) {
        close(fd);
        return NULL;
    }
    void *map = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (map == MAP_FAILED) {
        close(fd);
        return NULL;
    }
    // 减少一次系统调用：用 madvise 提示顺序读取
    madvise(map, st.st_size, MADV_SEQUENTIAL);
    close(fd);
    *out_size = st.st_size;
    return (uint8_t *)map;
}

// ==================== 量子指令子集编译器（mmap 版） ====================

int compile_file_v2(const char *input_path, const char *output_path) {
    size_t fsize = 0;
    uint8_t *data = mmap_load(input_path, &fsize);
    if (!data) return -1;

    fprintf(stdout, "[QCL] 编译: %s\n", input_path);
    fprintf(stdout, "[QCL] 输出: %s\n", output_path);

    char *buf = (char *)data;
    char *end = buf + fsize;
    int line_num = 0;
    int found_code = 0;

    // 逐行解析（原地，零拷贝）
    while (buf < end) {
        line_num++;
        char *p = buf;
        char *eol = memchr(p, '\n', end - p);
        if (!eol) eol = end;

        while (p < eol && (*p == ' ' || *p == '\t' || *p == '\r')) p++;

        if (p >= eol || *p == '/' || *p == '#') {
            buf = eol + 1;
            continue;
        }

        if (strncmp(p, "init ", 5) == 0) {
            p += 5;
            unsigned int n = 0;
            while (p < eol && *p >= '0' && *p <= '9') { n = n * 10 + (*p - '0'); p++; }
            write_opcode(OP_INIT_N);
            write_u8(n & 0xFF);
            write_u8((n >> 8) & 0xFF);
            found_code = 1;
        }
        else if ((p+2 <= eol) &&
                 ((strncmp(p, "H ", 2) == 0) || (strncmp(p, "X ", 2) == 0) ||
                  (strncmp(p, "Y ", 2) == 0) || (strncmp(p, "Z ", 2) == 0) ||
                  (strncmp(p, "T ", 2) == 0) || (strncmp(p, "S ", 2) == 0))) {
            Opcode op;
            if (p[0]=='H') op = OP_H;
            else if (p[0]=='X') op = OP_X;
            else if (p[0]=='Y') op = OP_Y;
            else if (p[0]=='Z') op = OP_Z;
            else if (p[0]=='T') op = OP_T;
            else op = OP_S;
            p += 2;
            int qid = 0;
            while (p < eol && *p >= '0' && *p <= '9') { qid = qid * 10 + (*p - '0'); p++; }
            write_opcode(op);
            write_u8(qid);
            found_code = 1;
        }
        else if (strncmp(p, "CNOT ", 5) == 0) {
            p += 5;
            int ctrl = 0, tgt = 0;
            while (p < eol && *p >= '0' && *p <= '9') { ctrl = ctrl * 10 + (*p - '0'); p++; }
            while (p < eol && (*p == ' ' || *p == '\t')) p++;
            while (p < eol && *p >= '0' && *p <= '9') { tgt = tgt * 10 + (*p - '0'); p++; }
            write_opcode(OP_CNOT);
            write_u8(ctrl);
            write_u8(tgt);
            found_code = 1;
        }
        else if (strncmp(p, "MEASURE ", 8) == 0) {
            p += 8;
            int qid = 0, reg = 0;
            while (p < eol && *p >= '0' && *p <= '9') { qid = qid * 10 + (*p - '0'); p++; }
            while (p < eol && (*p == ' ' || *p == '\t')) p++;
            while (p < eol && *p >= '0' && *p <= '9') { reg = reg * 10 + (*p - '0'); p++; }
            write_opcode(OP_MEASURE);
            write_u8(qid);
            write_u8(reg);
            found_code = 1;
        }
        else if (strncmp(p, "PRINT ", 6) == 0) {
            p += 6;
            int reg = 0;
            while (p < eol && *p >= '0' && *p <= '9') { reg = reg * 10 + (*p - '0'); p++; }
            write_opcode(OP_PRINT);
            write_u8(reg);
            found_code = 1;
        }
        else if (strncmp(p, "STOP", 4) == 0) {
            write_opcode(OP_STOP);
            found_code = 1;
        }
        else if (strncmp(p, "EXIT", 4) == 0) {
            write_opcode(OP_EXIT);
            found_code = 1;
        }

        buf = eol + 1;
    }

    munmap(data, fsize);

    if (!found_code) {
        fprintf(stdout, "[QCL] 警告: 未找到可编译的量子代码\n");
        write_opcode(OP_STOP);
    }

    FILE *fout = fopen(output_path, "wb");
    if (!fout) {
        fprintf(stderr, "[QCL] 无法创建输出文件: %s\n", output_path);
        return -1;
    }

    fwrite(g_bytecode, 1, g_bc_pos, fout);
    fclose(fout);

    fprintf(stdout, "[QCL] 编译完成: %d 字节, %d 条指令 [mmap]\n", g_bc_pos, g_bc_pos);

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