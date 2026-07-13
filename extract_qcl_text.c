/*
 * extract_qcl_text.c — 从旧格式QBC文件中重建QCL源码
 * QBC格式: [opcode | off(2B) | len(2B) | name(len)]...
 * 读取所有OP_FUNC_DEF和OP_CONST_DEF，重建可读文本
 * 编译: gcc -O2 -o bin/extract_qcl_text extract_qcl_text.c
 * 用法: ./bin/extract_qcl_text <输入.qbc> [输出.qentl]
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
#define BC_FUNC_END 254

static int has_str(int op) {
    return op == OP_CONST_DEF || op == OP_VAR_DECL || op == OP_FUNC_DEF ||
           op == OP_IMPORT || op == OP_ASSIGN_STMT || op == OP_FUNC_CALL_STMT ||
           op == OP_RETURN_STMT;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "用法: %s <输入.qbc> [输出]\n", argv[0]); return 1; }
    const char *in_path = argv[1];
    const char *out_path = argc > 2 ? argv[2] : NULL;
    
    FILE *f = fopen(in_path, "rb");
    if (!f) { fprintf(stderr, "无法打开 %s\n", in_path); return 1; }
    fseek(f, 0, SEEK_END);
    int fsize = (int)ftell(f);
    fseek(f, 0, SEEK_SET);
    uint8_t *buf = (uint8_t*)malloc(fsize + 16);
    fread(buf, 1, fsize, f);
    fclose(f);
    
    FILE *out = out_path ? fopen(out_path, "w") : stdout;
    if (!out) { fprintf(stderr, "无法写入 %s\n", out_path); return 1; }
    
    fprintf(out, "# 从QBC字节码重建的QCL源码\n");
    fprintf(out, "# 原文件: %s (%d 字节)\n\n", in_path, fsize);
    
    int pos = 0;
    while (pos < fsize) {
        int op = buf[pos++];
        
        if (op == OP_CONST_DEF) {
            int off = buf[pos] | (buf[pos+1] << 8);
            int len = buf[pos+2] | (buf[pos+3] << 8);
            pos += 4;
            /* 在新格式中，后面跟着value(2B) */
            int val = 0;
            if (pos + 2 <= fsize) {
                val = buf[pos] | (buf[pos+1] << 8);
                pos += 2;
            }
            char name[256];
            int nlen = len < 255 ? len : 255;
            memcpy(name, buf + pos, nlen);
            name[nlen] = 0;
            pos += len;
            fprintf(out, "const %s = %d;\n", name, val);
            continue;
        }
        
        if (op == OP_VAR_DECL) {
            int off = buf[pos] | (buf[pos+1] << 8);
            int len = buf[pos+2] | (buf[pos+3] << 8);
            pos += 4;
            char name[256];
            int nlen = len < 255 ? len : 255;
            memcpy(name, buf + pos, nlen);
            name[nlen] = 0;
            pos += len;
            fprintf(out, "var %s;\n", name);
            continue;
        }
        
        if (op == OP_FUNC_DEF) {
            int off = buf[pos] | (buf[pos+1] << 8);
            int len = buf[pos+2] | (buf[pos+3] << 8);
            pos += 4;
            char name[256];
            int nlen = len < 255 ? len : 255;
            memcpy(name, buf + pos, nlen);
            name[nlen] = 0;
            pos += len;
            int nargs = buf[pos++];
            fprintf(out, "def %s(%d) {\n", name, nargs);
            continue;
        }
        
        if (op == OP_IMPORT) {
            int off = buf[pos] | (buf[pos+1] << 8);
            int len = buf[pos+2] | (buf[pos+3] << 8);
            pos += 4;
            char name[256];
            int nlen = len < 255 ? len : 255;
            memcpy(name, buf + pos, nlen);
            name[nlen] = 0;
            pos += len;
            fprintf(out, "import \"%s\";\n", name);
            continue;
        }
        
        if (op == BC_FUNC_END) {
            fprintf(out, "}\n\n");
            pos += 0; /* BC_FUNC_END has no extra bytes */
            continue;
        }
        
        if (op == OP_RETURN_STMT) {
            fprintf(out, "  return;\n");
            continue;
        }
        
        if (op == OP_ASSIGN_STMT) {
            int off = buf[pos] | (buf[pos+1] << 8);
            int len = buf[pos+2] | (buf[pos+3] << 8);
            pos += 4;
            char name[256];
            int nlen = len < 255 ? len : 255;
            memcpy(name, buf + pos, nlen);
            name[nlen] = 0;
            pos += len;
            fprintf(out, "  // ASSIGN: %s\n", name);
            continue;
        }
        
        if (op == OP_FUNC_CALL_STMT) {
            int off = buf[pos] | (buf[pos+1] << 8);
            int len = buf[pos+2] | (buf[pos+3] << 8);
            pos += 4;
            char name[256];
            int nlen = len < 255 ? len : 255;
            memcpy(name, buf + pos, nlen);
            name[nlen] = 0;
            pos += len;
            fprintf(out, "  // CALL: %s\n", name);
            continue;
        }
        
        if (op == OP_IF_STMT) {
            fprintf(out, "  // IF\n");
            continue;
        }
        
        if (op == OP_ELSE_STMT) {
            fprintf(out, "  // ELSE\n");
            continue;
        }
        
        if (op == OP_WHILE_STMT) {
            fprintf(out, "  // WHILE\n");
            continue;
        }
        
        if (op == OP_PUSH_CONST_INT) {
            if (pos + 2 <= fsize) {
                int val = buf[pos] | (buf[pos+1] << 8);
                pos += 2;
                fprintf(out, "  // PUSH_INT(%d)\n", val);
            }
            continue;
        }
        
        if (op == OP_PUSH_CONST_STR) {
            int off = buf[pos] | (buf[pos+1] << 8);
            int len = buf[pos+2] | (buf[pos+3] << 8);
            pos += 4;
            char s[256];
            int slen = len < 255 ? len : 255;
            memcpy(s, buf + pos, slen);
            s[slen] = 0;
            pos += len;
            fprintf(out, "  // PUSH_STR(\"%s\")\n", s);
            continue;
        }
    }
    
    fclose(out);
    printf("提取完成: %d 字节 -> %s\n", fsize, out_path ? out_path : "stdout");
    free(buf);
    return 0;
}