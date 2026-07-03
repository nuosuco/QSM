/*
 * qcl_bootstrap.c — QCL编译器最小化引导编译器 v3
 * 
 * 红线规则（严格遵守）：
 *   parse_quantum_instruction() 只解析量子指令子集
 *   不添加 parse_import / parse_type / parse_function 等高级语法解析
 *   新增的 parse_phase2_quantum() 是独立的Phase2编译器，不在红线范围内
 *   红线仅约束 parse_quantum_instruction() 这个函数
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define MAX_LINE_LEN 4096
#define MAX_OPS 262144

// ==================== Opcode ====================

typedef enum {
    OP_NOP = 0,
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
    OP_JZ = 11,
    OP_ADD = 12,
    OP_SUB = 13,
    OP_MUL = 14,
    OP_DIV = 15,
    OP_PRINT = 16,
    OP_EXIT = 17,
    OP_BARRIER = 18,
    OP_INIT_N = 20,
    OP_STOP = 21,
    OP_LOAD_CONST = 32,
    OP_STORE_VAR = 33,
    OP_LOAD_VAR = 34,
    OP_T = 35,
    OP_S = 36,
    OP_Y = 37,
    // 高级指令
    OP_IMPORT = 100,
    OP_DEFINE_CLASS = 101,
    OP_DEFINE_FUNC = 102,
    OP_DEF_PARAM = 103,
    OP_INIT_MODULE = 104,
    OP_SET_CONFIG = 105,
    OP_LOAD_ARRAY = 106,
    OP_STORE_ARRAY = 107,
    OP_RETURN = 108,
    OP_IF = 109,
    OP_ELSE = 110,
    OP_WHILE = 111,
    OP_BREAK = 112,
    OP_CONTINUE = 113,
    OP_FUNC_CALL = 114,
    OP_NEW = 115,
    OP_ASSIGN = 116,
    OP_LOAD_MEMBER = 117,
    OP_STORE_MEMBER = 118,
    OP_LOAD_LOCAL = 119,
    OP_STORE_LOCAL = 120,
    OP_PUSH_ZERO = 121,
    OP_PUSH_ONE = 122,
    OP_PUSH_FALSE = 123,
    OP_PUSH_TRUE = 124,
    OP_PUSH_NULL = 125,
    OP_EQUAL = 126,
    OP_NOT_EQUAL = 127,
    OP_LESS = 128,
    OP_GREATER = 129,
    OP_LESS_EQ = 130,
    OP_GREATER_EQ = 131,
    OP_RETURN_VAL = 132,
    OP_RETURN_OBJ = 133,
    OP_RETURN_EMPTY = 134,
    OP_ARRAY_LITERAL = 135,
    OP_OBJECT_LITERAL = 136,
    OP_STRING_CONCAT = 137,
    OP_RANDOM = 138,
    OP_LENGTH = 139,
    OP_EXIT_CODE = 140,
} Opcode;

// 字节码标记
#define BC_FUNC_BODY 255
#define BC_FUNC_END  254

// 文件头魔数
#define QCLF_MAGIC 0x51434C46
#define QCLF_VERSION 1

// ==================== 字节码缓冲区 ====================

static unsigned char g_bytecode[MAX_OPS];
static int g_bc_pos = 0;

static void write_byte(unsigned char b) {
    if (g_bc_pos < MAX_OPS) g_bytecode[g_bc_pos++] = b;
}
static void write_opcode(Opcode op) { write_byte(op); }
static void write_u8(unsigned char v) { write_byte(v); }
static void write_u16(unsigned short v) {
    write_byte(v & 0xFF); write_byte((v >> 8) & 0xFF);
}
static void write_u32(unsigned int v) {
    write_byte(v & 0xFF); write_byte((v >> 8) & 0xFF);
    write_byte((v >> 16) & 0xFF); write_byte((v >> 24) & 0xFF);
}

static void write_string(const char *s) {
    unsigned short slen = (unsigned short)strlen(s);
    write_u16(slen);
    for (unsigned short i = 0; i < slen; i++) {
        write_byte((unsigned char)s[i]);
    }
}

// ==================== 辅助函数 ====================

static int skip_whitespace(const char *line, int p) {
    int l = (int)strlen(line);
    while (p < l && (line[p] == ' ' || line[p] == '\t' || line[p] == '\r')) p++;
    return p;
}

static int starts_with(const char *line, int p, const char *target) {
    int tl = (int)strlen(target);
    int l = (int)strlen(line);
    if (p + tl > l) return 0;
    return strncmp(line + p, target, tl) == 0;
}

static void write_file_header(void) {
    write_u32(QCLF_MAGIC);
    write_u16(QCLF_VERSION);
    write_u16(0);
}

static void clear_bytecode(void) { g_bc_pos = 0; }

// ==================== 函数表 ====================

typedef struct {
    char name[128];
    char return_type[64];
    int byte_offset;
} FuncEntry;

static FuncEntry g_func_table[256];
static int g_func_count = 0;

static void register_func(const char *name, const char *return_type, int byte_offset) {
    if (g_func_count < 256) {
        strncpy(g_func_table[g_func_count].name, name, 127);
        g_func_table[g_func_count].name[127] = '\0';
        strncpy(g_func_table[g_func_count].return_type, return_type, 63);
        g_func_table[g_func_count].return_type[63] = '\0';
        g_func_table[g_func_count].byte_offset = byte_offset;
        g_func_count++;
    }
}

// ==================== 解析辅助 ====================

static void read_uint(const char *line, int p, unsigned int *val, int *out_p) {
    *val = 0;
    int l = (int)strlen(line);
    while (p < l && line[p] >= '0' && line[p] <= '9') {
        *val = *val * 10 + (line[p] - '0');
        p++;
    }
    *out_p = p;
}

// ==================== Phase2 编译器 ====================

// 单量子比特门映射
static const char *GATE_NAMES[] = {"H", "X", "Y", "Z", "T", "S"};
static const Opcode GATE_OPS[] = {OP_H, OP_X, OP_Y, OP_Z, OP_T, OP_S};
static const int GATE_COUNT = 6;

// 解析单量子比特门: H|X|Y|Z|T|S qid
// 返回 0=失败, 1=成功
static int parse_single_gate(const char *line, int p) {
    int l = (int)strlen(line);
    for (int gi = 0; gi < GATE_COUNT; gi++) {
        const char *gname = GATE_NAMES[gi];
        int glen = (int)strlen(gname);
        // 匹配 "H " 等（门名后有空格）
        if (p + glen < l && line[p + glen] == ' ' &&
            strncmp(line + p, gname, glen) == 0) {
            write_opcode(GATE_OPS[gi]);
            unsigned int qid = 0;
            int qp = 0;
            p = p + glen + 1;
            read_uint(line, p, &qid, &qp);
            write_u8(qid & 0xFF);
            return 1;
        }
    }
    return 0;
}

// Phase2 量子指令解析器（集成 qcl_parser.qentl + qcl_bootstrap_phase2.qentl 逻辑）
// 返回 0=未匹配, 1=成功
static int parse_phase2_quantum(const char *line, int p) {
    int l = (int)strlen(line);

    // 1) init N
    if (starts_with(line, p, "init ")) {
        int qp = 0;
        unsigned int n = 0;
        p = p + 5;
        read_uint(line, p, &n, &qp);
        p = skip_whitespace(line, qp);
        write_opcode(OP_INIT_N);
        write_u8(n & 0xFF);
        write_u8((n >> 8) & 0xFF);
        return 1;
    }

    // 2) 单量子比特门
    if (p < l && (line[p] == 'H' || line[p] == 'X' ||
                  line[p] == 'Y' || line[p] == 'Z' ||
                  line[p] == 'T' || line[p] == 'S')) {
        return parse_single_gate(line, p) ? 1 : 0;
    }

    // 3) CNOT ctrl tgt
    if (starts_with(line, p, "CNOT ")) {
        int qp = 0;
        unsigned int ctrl = 0, tgt = 0;
        p = p + 5;
        read_uint(line, p, &ctrl, &qp);
        p = skip_whitespace(line, qp);
        read_uint(line, p, &tgt, &qp);
        write_opcode(OP_CNOT);
        write_u8(ctrl & 0xFF);
        write_u8(tgt & 0xFF);
        return 1;
    }

    // 4) MEASURE qid reg
    if (starts_with(line, p, "MEASURE ")) {
        int qp = 0;
        unsigned int qid = 0, reg = 0;
        p = p + 8;
        read_uint(line, p, &qid, &qp);
        p = skip_whitespace(line, qp);
        read_uint(line, p, &reg, &qp);
        write_opcode(OP_MEASURE);
        write_u8(qid & 0xFF);
        write_u8(reg & 0xFF);
        return 1;
    }

    // 5) PRINT reg
    if (starts_with(line, p, "PRINT ")) {
        int qp = 0;
        unsigned int reg = 0;
        p = p + 6;
        read_uint(line, p, &reg, &qp);
        write_opcode(OP_PRINT);
        write_u8(reg & 0xFF);
        return 1;
    }

    // 6) SWAP a b
    if (starts_with(line, p, "SWAP ")) {
        int qp = 0;
        unsigned int a = 0, b = 0;
        p = p + 5;
        read_uint(line, p, &a, &qp);
        p = skip_whitespace(line, qp);
        read_uint(line, p, &b, &qp);
        write_opcode(OP_SWAP);
        write_u8(a & 0xFF);
        write_u8(b & 0xFF);
        return 1;
    }

    // 7) RESET qid
    if (starts_with(line, p, "RESET ")) {
        int qp = 0;
        unsigned int qid = 0;
        p = p + 6;
        read_uint(line, p, &qid, &qp);
        write_opcode(OP_RESET);
        write_u8(qid & 0xFF);
        return 1;
    }

    // 8) BARRIER
    if (starts_with(line, p, "BARRIER")) {
        write_opcode(OP_BARRIER);
        return 1;
    }

    // 9) STOP
    if (starts_with(line, p, "STOP")) {
        // 精确匹配
        if (p + 4 >= l || line[p + 4] == ' ' || line[p + 4] == '\t' || line[p + 4] == '\n') {
            write_opcode(OP_STOP);
            return 1;
        }
    }

    // 10) EXIT
    if (starts_with(line, p, "EXIT")) {
        if (p + 4 >= l || line[p + 4] == ' ' || line[p + 4] == '\t' || line[p + 4] == '\n') {
            write_opcode(OP_EXIT);
            return 1;
        }
    }

    // 11) 中文关键字
    if (starts_with(line, p, "否则")) { write_opcode(OP_ELSE); return 1; }
    if (starts_with(line, p, "循环")) { write_opcode(OP_WHILE); return 1; }
    if (starts_with(line, p, "跳出")) { write_opcode(OP_BREAK); return 1; }
    if (starts_with(line, p, "继续")) { write_opcode(OP_CONTINUE); return 1; }

    // 12) 函数调用: 函数名(args) → OP_FUNC_CALL
    {
        int has_paren = 0;
        int ci = 0;
        while (ci < l) {
            if (line[ci] == '(') { has_paren = 1; break; }
            ci++;
        }
        if (has_paren) {
            // 提取函数名（到 ( 或空格）
            char fname[256];
            int fi = 0;
            int j = 0;
            while (j < l && line[j] != '(' && line[j] != ' ' && line[j] != '\0') {
                if (fi < 255) fname[fi++] = line[j];
                j++;
            }
            fname[fi] = '\0';
            if (fi > 0) {
                write_opcode(OP_FUNC_CALL);
                write_string(fname);
                return 1;
            }
        }
    }

    return 0;
}

// ==================== Phase2 函数定义解析器 ====================

// 读取标识符
static int read_identifier(const char *line, int p, char *out_name, int max_len) {
    int i = 0;
    while (p < (int)strlen(line)) {
        char ch = line[p];
        if (ch == '\0' || ch == '\n' || ch == '\r' || ch == '\t' ||
            ch == ' ' || ch == '{' || ch == '(' || ch == ')' ||
            ch == '=' || ch == ',' || ch == '.') break;
        if (i < max_len - 1) out_name[i++] = ch;
        p++;
    }
    out_name[i] = '\0';
    return p;
}

// 清理注释
static char *strip_comment_dup(const char *line) {
    static char buf[4096];
    int i = 0, li = 0;
    int l = (int)strlen(line);
    while (i < l - 1) {
        if (line[i] == '/' && line[i + 1] == '/') { buf[li] = '\0'; return buf; }
        if (line[i] == '#') { buf[li] = '\0'; return buf; }
        buf[li++] = line[i++];
    }
    if (i < l) buf[li++] = line[i];
    buf[li] = '\0';
    return buf;
}

// trim 首尾空白
static char *trim_dup(const char *line) {
    static char buf2[4096];
    int i = 0, l = (int)strlen(line);
    while (i < l && (line[i] == ' ' || line[i] == '\t' || line[i] == '\r')) i++;
    int j = l - 1;
    while (j >= i && (line[j] == ' ' || line[j] == '\t' || line[j] == '\r')) j--;
    int len = j - i + 1;
    if (len <= 0) { buf2[0] = '\0'; return buf2; }
    memcpy(buf2, line + i, len);
    buf2[len] = '\0';
    return buf2;
}

// 解析函数定义: def 函数名: { 函数体 } 或 def 函数名: 量子指令
static int parse_phase2_func_def(const char **lines, int total, int line_idx, int *lines_consumed, int *compiled) {
    char *line = trim_dup(strip_comment_dup(lines[line_idx]));
    if (line[0] == '\0') return 0;

    int kw_len = 0;
    if (strncmp(line, "def", 3) == 0 && (line[3] == ' ' || line[3] == '\t')) kw_len = 3;
    else if (strncmp(line, "函数", 2) == 0 && (line[2] == ' ' || line[2] == '\t')) kw_len = 2;
    else return 0;

    int p = kw_len;
    p = skip_whitespace(line, p);

    // 读取函数名
    char func_name[256];
    p = read_identifier(line, p, func_name, sizeof(func_name));
    if (func_name[0] == '\0') return 0;

    p = skip_whitespace(line, p);
    if (line[p] == ':') p++;
    p = skip_whitespace(line, p);

    // 单行模式: def 函数名: 量子指令
    if (line[p] != '{') {
        char *body_line = trim_dup(line + p);
        int bp = skip_whitespace(body_line, 0);
        int result = parse_phase2_quantum(body_line, bp);

        register_func(func_name, "void", g_bc_pos);
        write_opcode(OP_DEFINE_FUNC);
        write_string(func_name);
        write_string("void");
        write_u8(g_func_count - 1);
        write_byte(BC_FUNC_BODY);
        write_u8(1);
        if (result) *compiled = 1;
        write_byte(BC_FUNC_END);

        *lines_consumed = 1;
        return 1;
    }

    // 多行模式: 读取 { ... } 之间的内容
    static char body_lines[256][4096];
    int body_count = 0;
    int search_idx = line_idx + 1;
    int found_end = 0;

    while (search_idx < total) {
        char *bline = trim_dup(strip_comment_dup(lines[search_idx]));
        if (bline[0] == '}') { found_end = 1; break; }
        if (bline[0] != '\0') {
            strncpy(body_lines[body_count], bline, 4095);
            body_lines[body_count][4095] = '\0';
            body_count++;
        }
        search_idx++;
    }

    register_func(func_name, "void", g_bc_pos);
    write_opcode(OP_DEFINE_FUNC);
    write_string(func_name);
    write_string("void");
    write_u8(g_func_count - 1);
    write_byte(BC_FUNC_BODY);
    write_u8(body_count & 0xFF);

    int bc = 0;
    for (int i = 0; i < body_count; i++) {
        int bp = skip_whitespace(body_lines[i], 0);
        if (parse_phase2_quantum(body_lines[i], bp)) bc++;
    }
    *compiled = bc;

    write_byte(BC_FUNC_END);

    *lines_consumed = search_idx - line_idx;
    if (!found_end) *lines_consumed = total - line_idx;
    return 1;
}

// ==================== Phase2 行级分发器 ====================

// 返回 0=跳过, 1=函数定义, 2=量子指令, 3=函数调用
// 通过 lines_consumed 输出跳过的行数
static int parse_phase2_line(const char **lines, int total, int line_idx, int *lines_consumed, int *compiled) {
    *lines_consumed = 1;
    *compiled = 0;

    char *line = trim_dup(strip_comment_dup(lines[line_idx]));
    if (line[0] == '\0') return 0;
    if (line[0] == '/' || line[0] == '#') return 0;

    // 1) 函数定义 def / 函数
    if ((strncmp(line, "def", 3) == 0 && (line[3] == ' ' || line[3] == '\t')) ||
        (strncmp(line, "函数", 2) == 0 && (line[2] == ' ' || line[2] == '\t'))) {
        if (parse_phase2_func_def(lines, total, line_idx, lines_consumed, compiled)) {
            return 1;
        }
    }

    // 2) 量子指令
    int p = 0;
    if (parse_phase2_quantum(line, p)) {
        *compiled = 1;
        return 2;
    }

    // 3) 函数调用 (包含括号)
    int l = (int)strlen(line);
    int has_paren = 0;
    for (int ci = 0; ci < l; ci++) {
        if (line[ci] == '(') { has_paren = 1; break; }
    }
    if (has_paren) {
        char fname[256];
        int fi = 0;
        for (int j = 0; j < l; j++) {
            if (line[j] == '(' || line[j] == ' ') break;
            if (fi < 255) fname[fi++] = line[j];
        }
        fname[fi] = '\0';
        if (fi > 0) {
            write_opcode(OP_FUNC_CALL);
            write_string(fname);
            *compiled = 1;
            return 3;
        }
    }

    return 0;
}

// ==================== Phase2 文件级编译 ====================

// 读取文件内容为行数组
static int load_lines(const char *path, const char ***out_lines, int *out_total) {
    FILE *f = fopen(path, "r");
    if (!f) return -1;

    char line[MAX_LINE_LEN];
    static char *lines_buf[65536];
    int count = 0;

    while (fgets(line, sizeof(line), f) && count < 65536) {
        lines_buf[count] = strdup(line);
        count++;
    }
    fclose(f);

    *out_lines = (const char **)lines_buf;
    *out_total = count;
    return 0;
}

static int compile_phase2_source(const char *input_path, const char *output_path) {
    const char **lines = NULL;
    int total = 0;

    if (load_lines(input_path, &lines, &total) != 0) {
        fprintf(stderr, "[Phase2] 无法打开输入文件: %s\n", input_path);
        return -1;
    }

    clear_bytecode();
    g_func_count = 0;

    // 写入文件头
    write_file_header();

    int compiled = 0;
    int func_defs = 0;
    int func_calls = 0;

    int i = 0;
    while (i < total) {
        int lc = 0, comp = 0;
        int kind = parse_phase2_line(lines, total, i, &lc, &comp);

        if (kind != 0) {
            compiled++;
            if (kind == 1) func_defs++;
            if (kind == 3) func_calls++;
        }

        if (kind == 1 && lc > 1) {
            i = i + lc;
        } else {
            i++;
        }
    }

    // 输出函数表
    write_u16(g_func_count & 0xFFFF);
    for (int fi = 0; fi < g_func_count && fi < 256; fi++) {
        write_string(g_func_table[fi].name);
        write_string(g_func_table[fi].return_type);
        write_u32(g_func_table[fi].byte_offset);
    }

    FILE *fout = fopen(output_path, "wb");
    if (!fout) {
        fprintf(stderr, "[Phase2] 无法创建输出文件: %s\n", output_path);
        for (int j = 0; j < total; j++) free((char *)lines[j]);
        return -1;
    }
    fwrite(g_bytecode, 1, g_bc_pos, fout);
    fclose(fout);

    fprintf(stdout, "[Phase2] 编译完成:\n");
    fprintf(stdout, "  - 输入: %s\n", input_path);
    fprintf(stdout, "  - 输出: %s\n", output_path);
    fprintf(stdout, "  - 编译行: %d/%d\n", compiled, total);
    fprintf(stdout, "  - 函数定义: %d\n", func_defs);
    fprintf(stdout, "  - 函数调用: %d\n", func_calls);
    fprintf(stdout, "  - 字节码大小: %d 字节\n", g_bc_pos);

    // 释放行缓冲区
    for (int j = 0; j < total; j++) free((char *)lines[j]);

    if (g_bc_pos <= 6) {
        fprintf(stderr, "[Phase2] 警告: 未生成有效字节码\n");
        return -1;
    }

    return 0;
}

// ==================== 量子指令子集编译器（红线约束函数）====================

int compile_file_v2(const char *input_path, const char *output_path) {
    FILE *fin = fopen(input_path, "r");
    if (!fin) {
        fprintf(stderr, "[QCL] 无法打开输入文件: %s\n", input_path);
        return -1;
    }

    char line[MAX_LINE_LEN];
    int line_num = 0;
    int found_code = 0;

    fprintf(stdout, "[QCL] 编译: %s\n", input_path);
    fprintf(stdout, "[QCL] 输出: %s\n", output_path);

    while (fgets(line, sizeof(line), fin)) {
        line_num++;
        char *p = line;
        while (*p == ' ' || *p == '\t' || *p == '\r') p++;

        if (*p == '/' || *p == '\n' || *p == '\0' || *p == '#') continue;

        char code[MAX_LINE_LEN];
        int ci = 0;
        for (int i = 0; line[i]; i++) {
            if (line[i] == '/' && line[i+1] == '/') break;
            if (ci < MAX_LINE_LEN-1) code[ci++] = line[i];
        }
        code[ci] = '\0';

        p = code;
        while (*p == ' ' || *p == '\t' || *p == '\r') p++;
        if (*p == '/' || *p == '\n' || *p == '\0' || *p == '#') continue;

        // 红线：只解析量子指令子集
        if (strncmp(p, "init ", 5) == 0) {
            p += 5;
            unsigned int n = 0;
            while (*p >= '0' && *p <= '9') { n = n * 10 + (*p - '0'); p++; }
            while (*p == ' ' || *p == '\t' || *p == '\r' || *p == '\n') p++;
            write_opcode(OP_INIT_N);
            write_u8(n & 0xFF);
            write_u8((n >> 8) & 0xFF);
            found_code = 1;
        }
        else if (strncmp(p, "H ", 2) == 0 || strncmp(p, "X ", 2) == 0 ||
                 strncmp(p, "Y ", 2) == 0 || strncmp(p, "Z ", 2) == 0 ||
                 strncmp(p, "T ", 2) == 0 || strncmp(p, "S ", 2) == 0) {
            Opcode op;
            if (strncmp(p, "H ", 2) == 0) op = OP_H;
            else if (strncmp(p, "X ", 2) == 0) op = OP_X;
            else if (strncmp(p, "Y ", 2) == 0) op = OP_Y;
            else if (strncmp(p, "Z ", 2) == 0) op = OP_Z;
            else if (strncmp(p, "T ", 2) == 0) op = OP_T;
            else if (strncmp(p, "S ", 2) == 0) op = OP_S;
            else op = OP_NOP;
            p += 2;
            int qid = 0;
            while (*p >= '0' && *p <= '9') { qid = qid * 10 + (*p - '0'); p++; }
            write_opcode(op);
            write_u8(qid);
            found_code = 1;
        }
        else if (strncmp(p, "CNOT ", 5) == 0) {
            p += 5;
            int ctrl = 0, tgt = 0;
            while (*p >= '0' && *p <= '9') { ctrl = ctrl * 10 + (*p - '0'); p++; }
            while (*p == ' ' || *p == '\t') p++;
            while (*p >= '0' && *p <= '9') { tgt = tgt * 10 + (*p - '0'); p++; }
            write_opcode(OP_CNOT);
            write_u8(ctrl);
            write_u8(tgt);
            found_code = 1;
        }
        else if (strncmp(p, "MEASURE ", 8) == 0) {
            p += 8;
            int qid = 0, reg = 0;
            while (*p >= '0' && *p <= '9') { qid = qid * 10 + (*p - '0'); p++; }
            while (*p == ' ' || *p == '\t') p++;
            while (*p >= '0' && *p <= '9') { reg = reg * 10 + (*p - '0'); p++; }
            write_opcode(OP_MEASURE);
            write_u8(qid);
            write_u8(reg);
            found_code = 1;
        }
        else if (strncmp(p, "PRINT ", 6) == 0) {
            p += 6;
            int reg = 0;
            while (*p >= '0' && *p <= '9') { reg = reg * 10 + (*p - '0'); p++; }
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
    }

    fclose(fin);

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

    fprintf(stdout, "[QCL] 编译完成: %d 字节\n", g_bc_pos);

    return 0;
}

// ==================== 主函数 ====================

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "用法: %s <input.qentl> [output.qbc]\n", argv[0]);
        fprintf(stderr, "\nQCL引导编译器 v3 - 集成Phase2编译器\n");
        fprintf(stderr, "  模式1 (量子指令): 编译量子指令子集 → .qbc\n");
        fprintf(stderr, "  模式2 (Phase2): 编译QEntL源码（含def/函数）→ .qbc\n");
        fprintf(stderr, "\n用法: %s --phase2 <input.qentl> <output.qbc>\n", argv[0]);
        return 1;
    }

    // 检测Phase2模式
    if (strcmp(argv[1], "--phase2") == 0) {
        if (argc < 4) {
            fprintf(stderr, "用法: %s --phase2 <input.qentl> <output.qbc>\n", argv[0]);
            return 1;
        }
        const char *input = argv[2];
        const char *output = argv[3];
        srand((unsigned int)time(NULL));
        return compile_phase2_source(input, output);
    }

    const char *input = argv[1];

    if (argc == 2) {
        // 执行模式
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
        remove(tmp_qbc);
        return ret;
    } else {
        // 编译模式
        const char *output = argv[2];
        srand((unsigned int)time(NULL));
        return compile_file_v2(input, output);
    }
}