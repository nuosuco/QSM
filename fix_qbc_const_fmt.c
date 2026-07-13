/*
 * fix_qbc_const_fmt.c — 修复QBC文件的OP_CONST_DEF格式
 * 旧格式: OP_CONST_DEF | off(2B) | len(2B) | name(len) | [no value]
 * 新格式: OP_CONST_DEF | off(2B) | len(2B) | value(2B) | name(len)
 * 编译: gcc -O2 -o bin/fix_qbc_const_fmt fix_qbc_const_fmt.c
 * 用法: ./bin/fix_qbc_const_fmt <输入.qbc> <输出.qbc>
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define OP_CONST_DEF 101
#define OP_VAR_DECL 106
#define OP_FUNC_DEF 102
#define OP_IMPORT 100
#define OP_FUNC_END 103
#define OP_TYPE_DEF 104
#define OP_TYPE_END 105
#define OP_RETURN_STMT 107
#define OP_IF_STMT 108
#define OP_ELSE_STMT 109
#define OP_WHILE_STMT 110
#define OP_ASSIGN_STMT 111
#define OP_FUNC_CALL_STMT 112
#define OP_BREAK_STMT 113
#define OP_CONTINUE_STMT 114
#define OP_PUSH_CONST_INT 120
#define OP_PUSH_CONST_STR 121
#define OP_EQUAL 163
#define OP_NOT_EQUAL 164
#define OP_LESS 165
#define OP_GREATER 166
#define OP_LESS_EQ 167
#define OP_GREATER_EQ 168
#define OP_LENGTH 169
#define OP_LOAD_ARRAY 170
#define OP_STORE_ARRAY 171
#define OP_LOAD_MEMBER 172
#define OP_STORE_MEMBER 173
#define OP_STRING_CONCAT 174
#define OP_PUSH_TRUE 175
#define OP_PUSH_FALSE 176
#define BC_FUNC_END 254

/* 判断opcode是否有字符串参数 */
static int has_string_opcode(int op) {
    return op == OP_CONST_DEF || op == OP_VAR_DECL || op == OP_FUNC_DEF ||
           op == OP_IMPORT || op == OP_TYPE_DEF || op == OP_RETURN_STMT ||
           op == OP_IF_STMT || op == OP_ELSE_STMT || op == OP_WHILE_STMT ||
           op == OP_ASSIGN_STMT || op == OP_FUNC_CALL_STMT || op == OP_BREAK_STMT ||
           op == OP_CONTINUE_STMT || op == OP_PUSH_CONST_STR || op == OP_LOAD_ARRAY ||
           op == OP_STORE_ARRAY || op == OP_LOAD_MEMBER || op == OP_STORE_MEMBER ||
           op == OP_PUSH_CONST_INT || op == OP_LENGTH || op == OP_EQUAL ||
           op == OP_NOT_EQUAL || op == OP_LESS || op == OP_GREATER ||
           op == OP_LESS_EQ || op == OP_GREATER_EQ || op == OP_STRING_CONCAT ||
           op == OP_PUSH_TRUE || op == OP_PUSH_FALSE || op == BC_FUNC_END;
}

static int skip_string_opcode(int op) {
    (void)op;
    return 4; /* off(2B) + len(2B) = 4 bytes header */
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "用法: %s <输入.qbc> <输出.qbc>\n", argv[0]); return 1; }
    
    FILE *f = fopen(argv[1], "rb");
    if (!f) { fprintf(stderr, "无法打开 %s\n", argv[1]); return 1; }
    fseek(f, 0, SEEK_END);
    int fsize = (int)ftell(f);
    fseek(f, 0, SEEK_SET);
    uint8_t *buf = (uint8_t*)malloc(fsize + 16);
    fread(buf, 1, fsize, f);
    fclose(f);
    
    int out_size = fsize * 2;
    uint8_t *out = (uint8_t*)calloc(out_size, 1);
    int out_pos = 0;
    
    int pos = 0;
    int fixed_count = 0;
    
    while (pos < fsize) {
        int op = buf[pos++];
        
        if (op == OP_CONST_DEF) {
            /* 旧格式: OP_CONST_DEF | off(2B) | len(2B) | name(len) [| OP_PUSH_CONST_INT | value(2B)]
               新格式: OP_CONST_DEF | off(2B) | len(2B) | value(2B) | name(len) */
            if (pos + 4 > fsize) break;
            int off = buf[pos] | (buf[pos+1] << 8);
            int len = buf[pos+2] | (buf[pos+3] << 8);
            pos += 4;
            
            /* 旧格式中，name字符串直接跟在len后面 */
            int name_start = pos;
            if (pos + len > fsize) len = fsize - pos;
            pos += len;
            
            /* 检查后面是否有OP_PUSH_CONST_INT + 值 */
            int val = 0;
            if (pos < fsize && buf[pos] == OP_PUSH_CONST_INT && pos + 3 <= fsize) {
                val = buf[pos+1] | (buf[pos+2] << 8);
                pos += 3;
            }
            
            /* 写入新格式: OP_CONST_DEF | off | len | value | name */
            out[out_pos++] = OP_CONST_DEF;
            out[out_pos++] = off & 0xFF; out[out_pos++] = (off >> 8) & 0xFF;
            out[out_pos++] = len & 0xFF; out[out_pos++] = (len >> 8) & 0xFF;
            out[out_pos++] = val & 0xFF; out[out_pos++] = (val >> 8) & 0xFF;
            memcpy(out + out_pos, buf + name_start, len);
            /* pos已经指向name之后（如果后面有OP_PUSH_CONST_INT，已跳过），不要重置 */
            out_pos += len;
            fixed_count++;
            continue;
        }
        
        /* 其他操作码，原样复制 */
        if (out_pos + 4 >= out_size) {
            out_size *= 2;
            out = (uint8_t*)realloc(out, out_size);
        }
        out[out_pos++] = (uint8_t)op;
        
        if (has_string_opcode(op)) {
            /* 跳过字符串参数 */
            int skip = skip_string_opcode(op);
            if (pos + skip > fsize) break;
            int off = buf[pos] | (buf[pos+1] << 8);
            int slen = buf[pos+2] | (buf[pos+3] << 8);
            
            memcpy(out + out_pos, buf + pos, skip);
            pos += skip;
            out_pos += skip;
            
            if (pos + slen > fsize) slen = fsize - pos;
            if (out_pos + slen >= out_size) {
                out_size = out_size + slen + 16;
                out = (uint8_t*)realloc(out, out_size);
            }
            memcpy(out + out_pos, buf + pos, slen);
            pos += slen;
            out_pos += slen;
            
            /* 如果OP_FUNC_DEF，还有nargs */
            if (op == OP_FUNC_DEF && pos < fsize) {
                out[out_pos++] = buf[pos++];
            }
        } else if (op == OP_PUSH_CONST_INT) {
            if (pos + 2 <= fsize) {
                out[out_pos++] = buf[pos++];
                out[out_pos++] = buf[pos++];
            }
        }
    }
    
    f = fopen(argv[2], "wb");
    if (!f) { fprintf(stderr, "无法写入 %s\n", argv[2]); return 1; }
    fwrite(out, 1, out_pos, f);
    fclose(f);
    
    printf("修复完成: %d 个OP_CONST_DEF被修复, 输出 %d 字节 (原 %d 字节)\n", fixed_count, out_pos, fsize);
    free(buf); free(out);
    return 0;
}