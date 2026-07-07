/*
 * test_yi_algo_map.c — 验证 YI_GATE_MAP 算法映射覆盖全部 4120 个彝文字符
 * 范围: U+F2700..U+F370F
 * 策略: U+F2700..U+F270F(算法) + U+F2710..U+F2721(静态) + U+F2722..U+F370F(算法)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define YI_BASE   0xF2700
#define YI_END    0xF370F
#define YI_IS(cp) ((cp) >= YI_BASE && (cp) <= YI_END)

#define OP_NOP       0
#define OP_H         1
#define OP_X         2
#define OP_Z         3
#define OP_Y         37
#define OP_T         35
#define OP_S         36
#define OP_CNOT      4
#define OP_MEASURE   5
#define OP_RESET     6
#define OP_SWAP      7
#define OP_EXIT      17
#define OP_BARRIER   18
#define OP_INIT_N    20
#define OP_STOP      12
#define OP_PRINT     11

typedef struct { unsigned int token_code; int op; int gate_class; } YiGateEntry;

static const YiGateEntry YI_GATE_MAP[] = {
    {0xF2710, OP_H,     0},
    {0xF2711, OP_X,     0},
    {0xF2712, OP_Z,     0},
    {0xF2713, OP_Y,     0},
    {0xF2714, OP_T,     0},
    {0xF2715, OP_S,     0},
    {0xF2716, OP_RESET, 0},
    {0xF2717, OP_NOP,   0},
    {0xF2718, OP_BARRIER,0},
    {0xF2719, OP_STOP,  0},
    {0xF271A, OP_EXIT,  0},
    {0xF271B, OP_INIT_N,0},
    {0xF271C, OP_PRINT, 0},
    {0xF271D, OP_MEASURE,0},
    {0xF271E, OP_SWAP,  0},
    {0xF2720, OP_CNOT,  1},
    {0xF2721, OP_SWAP,  1},
    {0, OP_NOP, 0}
};

static unsigned int yi_gate_opcode(unsigned int cp) {
    static const unsigned char ops[18] = {
        OP_H, OP_X, OP_Z, OP_Y, OP_T, OP_S,
        OP_RESET, OP_NOP, OP_BARRIER, OP_STOP, OP_EXIT,
        OP_INIT_N, OP_PRINT, OP_MEASURE, OP_CNOT, OP_SWAP,
        OP_SWAP, OP_INIT_N
    };
    return ops[(cp - YI_BASE) % 18];
}

static int yi_gate_is_twoqubit(unsigned int cp) {
    unsigned int op = yi_gate_opcode(cp);
    return (op == OP_CNOT || op == OP_SWAP);
}

#define MAX_EMIT 64
static unsigned char emitted[MAX_EMIT];
static int emit_pos = 0;
void reset_emit(void) { emit_pos = 0; }
void write_opcode(unsigned int op) { if (emit_pos < MAX_EMIT) emitted[emit_pos++] = op; }
void write_u8(unsigned int v)      { if (emit_pos < MAX_EMIT) emitted[emit_pos++] = v; }

static int emit_yi_gate(unsigned int cp, int qubit_id) {
    if (!YI_IS(cp)) return 0;
    for (int i = 0; YI_GATE_MAP[i].token_code != 0; i++) {
        if (YI_GATE_MAP[i].token_code == cp) {
            write_opcode(YI_GATE_MAP[i].op);
            if (YI_GATE_MAP[i].gate_class == 1) {
                write_u8(qubit_id & 0xFF);
                write_u8((qubit_id + 1) & 0xFF);
            } else {
                write_u8(qubit_id & 0xFF);
            }
            return 1;
        }
    }
    write_opcode(yi_gate_opcode(cp));
    if (yi_gate_is_twoqubit(cp)) {
        write_u8(qubit_id & 0xFF);
        write_u8((qubit_id + 1) & 0xFF);
    } else {
        write_u8(qubit_id & 0xFF);
    }
    return 1;
}

static const char *gate_name(int n) {
    if (n == OP_H) return "H"; if (n == OP_X) return "X"; if (n == OP_Z) return "Z";
    if (n == OP_Y) return "Y"; if (n == OP_T) return "T"; if (n == OP_S) return "S";
    if (n == OP_RESET) return "RESET"; if (n == OP_NOP) return "NOP";
    if (n == OP_BARRIER) return "BARRIER"; if (n == OP_STOP) return "STOP";
    if (n == OP_EXIT) return "EXIT"; if (n == OP_INIT_N) return "INIT_N";
    if (n == OP_PRINT) return "PRINT"; if (n == OP_MEASURE) return "MEASURE";
    if (n == OP_SWAP) return "SWAP"; if (n == OP_CNOT) return "CNOT";
    return "??";
}

int passed = 0, failed = 0;
static void check(int cond, const char *desc) {
    if (cond) { passed++; } else { failed++; fprintf(stderr, "FAIL: %s\n", desc); }
}

/* 测试 1: U+F2700..U+F270F 走算法映射 */
void test_pre_table_algo(void) {
    fprintf(stderr, "\n[TEST 1] U+F2700..U+F270F 算法映射:\n");
    for (int cp = 0xF2700; cp <= 0xF270F; cp++) {
        reset_emit();
        int r = emit_yi_gate(cp, 3);
        char buf[128];
        snprintf(buf, sizeof(buf), "0x%05X accepted (r=%d)", cp, r);
        check(r == 1, buf);
        int mod = (cp - YI_BASE) % 18;
        int exp_op = yi_gate_opcode(cp);
        snprintf(buf, sizeof(buf), "0x%05X (mod=%d) expected %s got %s", cp, mod, gate_name(exp_op), gate_name(emitted[0]));
        check(emitted[0] == exp_op, buf);
        snprintf(buf, sizeof(buf), "0x%05X qubit_id=3 got %d", cp, emitted[1]);
        check(emitted[1] == 3, buf);
    }
    fprintf(stderr, "  passed %d, failed %d\n", passed, failed);
}

/* 测试 2: U+F2710..U+F2721 静态表精确匹配 */
void test_static_table(void) {
    fprintf(stderr, "\n[TEST 2] U+F2710..U+F2721 静态表:\n");
    struct { unsigned int cp; int expected_op; int twoq; } expected[] = {
        {0xF2710, OP_H, 0}, {0xF2711, OP_X, 0}, {0xF2712, OP_Z, 0},
        {0xF2713, OP_Y, 0}, {0xF2714, OP_T, 0}, {0xF2715, OP_S, 0},
        {0xF2716, OP_RESET, 0}, {0xF2717, OP_NOP, 0}, {0xF2718, OP_BARRIER, 0},
        {0xF2719, OP_STOP, 0}, {0xF271A, OP_EXIT, 0}, {0xF271B, OP_INIT_N, 0},
        {0xF271C, OP_PRINT, 0}, {0xF271D, OP_MEASURE, 0}, {0xF271E, OP_SWAP, 0},
        {0xF2720, OP_CNOT, 1}, {0xF2721, OP_SWAP, 1},
    };
    char buf[128];
    for (int i = 0; i < sizeof(expected)/sizeof(expected[0]); i++) {
        reset_emit();
        emit_yi_gate(expected[i].cp, 0);
        snprintf(buf, sizeof(buf), "static 0x%05X expected %s got %s", expected[i].cp, gate_name(expected[i].expected_op), gate_name(emitted[0]));
        check(emitted[0] == expected[i].expected_op, buf);
        snprintf(buf, sizeof(buf), "static 0x%05X operands expected %d got %d", expected[i].cp, expected[i].twoq ? 3 : 2, emit_pos);
        check(emit_pos == (expected[i].twoq ? 3 : 2), buf);
    }
    fprintf(stderr, "  passed %d, failed %d\n", passed, failed);
}

/* 测试 3: 全 4120 字符可发射 */
void test_full_range(void) {
    fprintf(stderr, "\n[TEST 3] 全 4120 字符可发射 (U+F2700..U+F370F):\n");
    int count_ok = 0, count_fail = 0;
    for (unsigned int cp = YI_BASE; cp <= YI_END; cp++) {
        reset_emit();
        if (emit_yi_gate(cp, 0)) count_ok++; else count_fail++;
    }
    char buf[128];
    snprintf(buf, sizeof(buf), "%d chars failed (total %d)", count_fail, count_ok+count_fail);
    check(count_fail == 0, buf);
    snprintf(buf, sizeof(buf), "expected 4112 emitted, got %d", count_ok);
    check(count_ok == 4112, buf);
    fprintf(stderr, "  emitted %d / 4112, passed %d, failed %d\n", count_ok, passed, failed);
}

/* 测试 4: 双量子比特门 operand 数 */
void test_operand_count(void) {
    fprintf(stderr, "\n[TEST 4] 双量子比特门 operand 数 (CNOT/SWAP → 2 operand):\n");
    char buf[128];
    int twoq_count = 0;
    for (unsigned int cp = YI_BASE; cp <= YI_END; cp++) {
        reset_emit();
        emit_yi_gate(cp, 10);
        /* 检查实际发射字节数: 双量子比特门=3, 单量子比特门=2 */
        int is_static_twoq = 0;
        for (int i = 0; YI_GATE_MAP[i].token_code != 0; i++) {
            if (YI_GATE_MAP[i].token_code == cp) { is_static_twoq = (YI_GATE_MAP[i].gate_class == 1); break; }
        }
        /* 静态表优先; 不在静态表的走算法映射 */
        int is_in_static = 0;
        for (int i = 0; YI_GATE_MAP[i].token_code != 0; i++) {
            if (YI_GATE_MAP[i].token_code == cp) { is_in_static = 1; break; }
        }
        int expect_three = is_static_twoq || (!is_in_static && yi_gate_is_twoqubit(cp));
        int actual_three = (emit_pos == 3);
        if (expect_three) {
            twoq_count++;
            snprintf(buf, sizeof(buf), "twoqubit 0x%05X should emit 3 bytes got %d", cp, emit_pos);
            check(actual_three, buf);
            if (actual_three) {
                snprintf(buf, sizeof(buf), "twoqubit 0x%05X operands (10,11) got (%d,%d)", cp, emitted[1], emitted[2]);
                check(emitted[1] == 10 && emitted[2] == 11, buf);
            }
        } else {
            snprintf(buf, sizeof(buf), "single 0x%05X should emit 2 bytes got %d", cp, emit_pos);
            check(emit_pos == 2, buf);
        }
    }
    fprintf(stderr, "  two-qubit gates: %d, passed %d, failed %d\n", twoq_count, passed, failed);
}

/* 测试 5: 非彝文不被误判 */
void test_non_yi(void) {
    fprintf(stderr, "\n[TEST 5] 非彝文字符不被误判:\n");
    struct { unsigned int cp; const char *desc; } samples[] = {
        {0x4E00, "CJK"}, {0x0041, "ASCII"}, {0x0000, "NUL"},
        {0xF26FF, "below"}, {0xF3710, "above"},
    };
    char buf[128];
    for (int i = 0; i < sizeof(samples)/sizeof(samples[0]); i++) {
        reset_emit();
        int r = emit_yi_gate(samples[i].cp, 0);
        snprintf(buf, sizeof(buf), "non-yi 0x%05X (%s) should return 0 got %d", samples[i].cp, samples[i].desc, r);
        check(r == 0, buf);
    }
    fprintf(stderr, "  passed %d, failed %d\n", passed, failed);
}

/* 测试 6: 18 种门分布 */
void test_distribution(void) {
    fprintf(stderr, "\n[TEST 6] 18 种门分布:\n");
    int mod_hist[18] = {0};
    for (unsigned int cp = YI_BASE; cp <= YI_END; cp++)
        mod_hist[(cp - YI_BASE) % 18]++;
    int ok = 1;
    /* 4112/18=228 rem 8, 前 8 个 mod 出现 229 次 */
    for (int i = 0; i < 18; i++) {
        int exp = (i < 8) ? 229 : 228;
        if (mod_hist[i] != exp) ok = 0;
    }
    char buf[128];
    snprintf(buf, sizeof(buf), "mod-18 distribution correct");
    check(ok, buf);
    static const unsigned char exp_ops[18] = {
        OP_H, OP_X, OP_Z, OP_Y, OP_T, OP_S,
        OP_RESET, OP_NOP, OP_BARRIER, OP_STOP, OP_EXIT,
        OP_INIT_N, OP_PRINT, OP_MEASURE, OP_CNOT, OP_SWAP,
        OP_SWAP, OP_INIT_N
    };
    int op_ok = 1;
    for (int m = 0; m < 18; m++)
        if (yi_gate_opcode(YI_BASE + m) != exp_ops[m]) op_ok = 0;
    snprintf(buf, sizeof(buf), "18-gate mapping table correct");
    check(op_ok, buf);
    fprintf(stderr, "  passed %d, failed %d\n", passed, failed);
}

int main(void) {
    fprintf(stderr, "=============================================\n");
    fprintf(stderr, " YI_GATE_MAP 算法映射全覆盖验证 (4112 字符)\n");
    fprintf(stderr, " 范围: U+F2700 .. U+F370F\n");
    fprintf(stderr, "=============================================\n");
    test_pre_table_algo();
    test_static_table();
    test_full_range();
    test_operand_count();
    test_non_yi();
    test_distribution();
    fprintf(stderr, "\n=============================================\n");
    fprintf(stderr, " 总计: 通过 %d, 失败 %d\n", passed, failed);
    fprintf(stderr, "=============================================\n");
    return failed > 0 ? 1 : 0;
}
