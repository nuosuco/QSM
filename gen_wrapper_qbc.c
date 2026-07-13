/*
 * gen_wrapper_qbc.c — 生成QBC包装器（内联模式）
 * 
 * QVM的import只在g_is_inline=1模式下工作。
 * 内联模式: 无QVM头，字符串直接嵌入字节码流。
 * 字符串引用: off=字符串在文件中的位置, len=字符串长度
 *
 * 编译: gcc -O2 -o bin/gen_wrapper_qbc gen_wrapper_qbc.c
 * 用法: ./bin/gen_wrapper_qbc <output.qbc> <import_path> <func_name> [nargs]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* Opcodes (与qvm_bootstrap.c严格对齐) */
#define OP_IMPORT           100
#define OP_FUNC_CALL_STMT   112
#define OP_PUSH_CONST_INT   120
#define OP_PUSH_CONST_STR   121
#define OP_STOP              12

/* 字节码缓冲区 */
static uint8_t bc[131072];
static int bc_pos = 0;

static void wb(uint8_t b) { bc[bc_pos++] = b; }
static void wu16(uint16_t v) { wb(v & 0xFF); wb((v >> 8) & 0xFF); }
static void wstr(const char *s) {
    while (*s) wb((uint8_t)*s++);
}

/* 写入一个字符串引用（内联模式）
 * 格式: [off(2B) | len(2B) | string_bytes(len)]
 * 返回: off的值（字符串字节在文件中的位置）
 */
static int wstr_ref_inline(const char *s) {
    int slen = strlen(s);
    int off = bc_pos + 4;  // 字符串字节在off+len之后开始
    wu16(off);
    wu16(slen);
    wstr(s);
    return off;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "用法: %s <output.qbc> <import_path> <func_name> [nargs]\n", argv[0]);
        fprintf(stderr, "示例: %s /tmp/wrapper.qbc \"QCL引导器/QCL_main.qbc\" \"优化字节码\" 0\n", argv[0]);
        return 1;
    }
    
    const char *output = argv[1];
    const char *import_path = argv[2];
    const char *func_name = argv[3];
    int nargs = argc > 4 ? atoi(argv[4]) : 0;

    // 1. import语句 (内联模式)
    wb(OP_IMPORT);
    wstr_ref_inline(import_path);

    // 2. 如果要传递参数，先推入参数（目前推入0个参数）
    // 对于无参函数，直接调用
    
    // 3. 函数调用
    wb(OP_FUNC_CALL_STMT);
    wstr_ref_inline(func_name);
    wb(nargs);

    // 4. STOP
    wb(OP_STOP);

    int total = bc_pos;

    // 写入文件
    FILE *f = fopen(output, "wb");
    if (!f) {
        fprintf(stderr, "错误: 无法创建 %s\n", output);
        return 1;
    }
    fwrite(bc, 1, total, f);
    fclose(f);

    printf("[GEN] 生成(内联模式): %s\n", output);
    printf("[GEN] 总大小: %d 字节\n", total);
    printf("[GEN] import: '%s'\n", import_path);
    printf("[GEN] call: '%s' (nargs=%d)\n", func_name, nargs);
    
    // 十六进制转储
    printf("[GEN] 字节码: ");
    for (int i = 0; i < total; i++) printf("%02x ", bc[i]);
    printf("\n");
    
    return 0;
}