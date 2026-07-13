/*
 * qcl_full_compiler.c — 完整QCL→QBC编译器（C语言）
 * 使用当前QVM opcode值，输出内联格式QBC
 * 编译：gcc -O2 -o bin/qcl_full_compiler src/qcl_full_compiler.c -lm
 * 用法：./bin/qcl_full_compiler <输入.qentl> <输出.qbc>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>

/* ========== QVM opcode值 ========== */
#define OP_NOP       0
#define OP_H         1
#define OP_X         2
#define OP_Z         3
#define OP_CNOT      4
#define OP_MEASURE   5
#define OP_RESET     6
#define OP_SWAP      7
#define OP_LOAD_REG  8
#define OP_STORE_REG 9
#define OP_JUMP     10
#define OP_PRINT    11
#define OP_STOP     12
#define OP_SUB      13
#define OP_DIV      14
#define OP_MUL      15
#define OP_ADD      16
#define OP_EXIT     17
#define OP_BARRIER  18
#define OP_INIT_N   20
#define OP_T        35
#define OP_S        36
#define OP_Y        37
#define OP_LOAD_VAR   34
#define OP_STORE_VAR  33
#define OP_IMPORT         100
#define OP_CONST_DEF      101
#define OP_FUNC_DEF       102
#define OP_FUNC_END       103
#define OP_TYPE_DEF       104
#define OP_TYPE_END       105
#define OP_VAR_DECL       106
#define OP_RETURN_STMT    107
#define OP_IF_STMT        108
#define OP_ELSE_STMT      109
#define OP_WHILE_STMT     110
#define OP_ASSIGN_STMT    111
#define OP_FUNC_CALL_STMT 112
#define OP_BREAK_STMT     113
#define OP_CONTINUE_STMT  114
#define OP_PUSH_CONST_INT 120
#define OP_PUSH_CONST_STR 121
#define OP_EQUAL        163
#define OP_NOT_EQUAL    164
#define OP_LESS         165
#define OP_GREATER      166
#define OP_LESS_EQ      167
#define OP_GREATER_EQ   168
#define OP_LENGTH       169
#define OP_LOAD_ARRAY   170
#define OP_STORE_ARRAY  171
#define OP_LOAD_MEMBER  172
#define OP_STORE_MEMBER 173
#define OP_STRING_CONCAT 174
#define OP_ARRAY_LITERAL 135
#define OP_PUSH_TRUE    175
#define OP_PUSH_FALSE   176
#define OP_FILE_READ    160
#define OP_FILE_WRITE   161
#define BC_FUNC_END     254

/* ========== 字节码缓冲区 ========== */
#define BUF_INIT 65536
static uint8_t *bc = NULL;
static int bc_cap = 0, bc_pos = 0;

static void bc_init(void) {
    bc_cap = BUF_INIT;
    bc = (uint8_t*)malloc(bc_cap);
    bc_pos = 0;
}

static void bc_grow(int n) {
    if (bc_pos + n > bc_cap) {
        while (bc_pos + n > bc_cap) bc_cap += BUF_INIT;
        bc = (uint8_t*)realloc(bc, bc_cap);
    }
}

static void bc_b(uint8_t b) { bc_grow(1); bc[bc_pos++] = b; }
static void bc_u16(uint16_t v) { bc_grow(2); bc[bc_pos++] = v & 0xFF; bc[bc_pos++] = (v>>8) & 0xFF; }

/* 写入内联字符串: off(0)+len+data */
static void bc_str(const char *s, int len) {
    if (len < 0) len = (int)strlen(s);
    bc_u16(0); /* off=0 内联模式 */
    bc_u16((uint16_t)len);
    bc_grow(len);
    memcpy(bc + bc_pos, s, len);
    bc_pos += len;
}

static void bc_strz(const char *s) { bc_str(s, (int)strlen(s)); }

static int bc_tell(void) { return bc_pos; }
static void bc_free(void) { free(bc); bc = NULL; bc_cap = 0; bc_pos = 0; }
/* 在指定位置写入16位值 */
static void bc_patch16(int pos, uint16_t v) {
    if (pos >= 0 && pos + 2 <= bc_pos) { bc[pos] = v & 0xFF; bc[pos+1] = (v>>8) & 0xFF; }
}

static int bc_save(const char *path) {
    FILE *f = fopen(path, "wb");
    if (!f) { fprintf(stderr, "无法写入 %s\n", path); return -1; }
    fwrite(bc, 1, bc_pos, f);
    fclose(f);
    return 0;
}

/* ========== 源文件 ========== */
typedef struct { char **l; int n, cap; } Src;
static Src *src_load(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) return NULL;
    Src *s = calloc(1, sizeof(Src));
    s->cap = 4096; s->l = malloc(s->cap * sizeof(char*));
    char buf[8192];
    while (fgets(buf, sizeof(buf), f)) {
        int len = strlen(buf);
        while (len > 0 && (buf[len-1]=='\n'||buf[len-1]=='\r')) buf[--len]=0;
        if (s->n >= s->cap) { s->cap *= 2; s->l = realloc(s->l, s->cap*sizeof(char*)); }
        s->l[s->n++] = strdup(buf);
    }
    fclose(f);
    printf("[加载] %s (%d 行)\n", path, s->n);
    return s;
}
static void src_free(Src *s) {
    if (!s) return;
    for (int i=0;i<s->n;i++) free(s->l[i]);
    free(s->l); free(s);
}

/* ========== 工具 ========== */
static int skip_sp(const char *s, int p) { while (s[p]==' '||s[p]=='\t') p++; return p; }
static int is_idch(unsigned char c) { return isalnum(c) || c=='_' || c=='.' || c>=0x80; }
static int get_indent(const char *s) { int n=0; while(s[n]==' '||s[n]=='\t') n++; return n; }

/* 提取标识符 */
static char *extract_id(const char *s, int p, int *ep) {
    p = skip_sp(s, p);
    int st = p;
    while (s[p] && is_idch((unsigned char)s[p])) {
        if ((s[p] & 0xC0) == 0xC0) { /* UTF-8 lead byte */
            int extra = 0;
            if ((s[p] & 0xF0) == 0xF0) extra = 3;
            else if ((s[p] & 0xE0) == 0xE0) extra = 2;
            else extra = 1;
            p++; while (extra-- && s[p]) p++;
        } else p++;
    }
    if (p == st) { *ep = skip_sp(s, p); return NULL; }
    char *r = malloc(p - st + 1);
    memcpy(r, s+st, p-st); r[p-st] = 0;
    *ep = p;
    return r;
}

/* 提取整数 */
static int extract_int(const char *s, int p, int *ep, int *v) {
    p = skip_sp(s, p);
    int st = p, val = 0;
    while (s[p] >= '0' && s[p] <= '9') { val = val*10 + (s[p]-'0'); p++; }
    if (p == st) { *ep = p; return -1; }
    *v = val; *ep = p; return 0;
}

/* 提取引号字符串 */
static char *extract_str(const char *s, int p, int *ep) {
    p = skip_sp(s, p);
    if (s[p] != '"') { *ep = p; return NULL; }
    p++;
    int st = p;
    while (s[p] && s[p] != '"') { if (s[p]=='\\' && s[p+1]) p++; p++; }
    int len = p - st;
    char *r = malloc(len + 1);
    int ri = 0;
    for (int i = st; i < st + len; i++) {
        if (s[i] == '\\' && i+1 < st+len) {
            i++;
            if (s[i] == 'n') r[ri++] = '\n';
            else if (s[i] == 't') r[ri++] = '\t';
            else if (s[i] == '"') r[ri++] = '"';
            else if (s[i] == '\\') r[ri++] = '\\';
            else r[ri++] = s[i];
        } else r[ri++] = s[i];
    }
    r[ri] = 0;
    if (s[p] == '"') p++;
    *ep = p;
    return r;
}

/* 提取字符 */
static int extract_ch(const char *s, int p, int *ep) {
    p = skip_sp(s, p);
    if (s[p] != '\'') { *ep = p; return -1; }
    p++;
    int ch = (unsigned char)s[p];
    if (s[p] == '\\' && s[p+1]) { p++; ch = s[p]; }
    if (s[p]) p++;
    if (s[p] == '\'') p++;
    *ep = p;
    return ch;
}

/* ========== 表达式生成器 ========== */
static void emit_push_int(int v) { bc_b(OP_PUSH_CONST_INT); bc_u16((uint16_t)(v & 0xFFFF)); }
static void emit_push_str(const char *s, int len) { bc_b(OP_PUSH_CONST_STR); bc_str(s, len); }
static void emit_load_var(const char *name) { bc_b(OP_LOAD_VAR); bc_strz(name); }

/* ========== 表达式解析（简化递归下降） ========== */
typedef struct { const char *s; int p, len; } ExprCtx;

/* 前向声明 */
static void parse_expr(ExprCtx *ec);

/* 解析primary */
static void parse_primary(ExprCtx *ec) {
    int p = skip_sp(ec->s, ec->p);
    if (p >= ec->len) return;

    /* 字符串 */
    if (ec->s[p] == '"') { int ep; char *s = extract_str(ec->s, p, &ep); if (s) { emit_push_str(s, strlen(s)); free(s); } ec->p = ep; return; }
    /* 字符 */
    if (ec->s[p] == '\'') { int ep, ch = extract_ch(ec->s, p, &ep); emit_push_int(ch >= 0 ? ch : 0); ec->p = ep; return; }
    /* 数字 */
    if (ec->s[p] >= '0' && ec->s[p] <= '9') { int ep, v; if (extract_int(ec->s, p, &ep, &v) == 0) emit_push_int(v); ec->p = ep; return; }
    /* true/false/null */
    if (strncmp(ec->s+p, "true", 4)==0 && !is_idch(ec->s[p+4])) { bc_b(OP_PUSH_TRUE); ec->p = p+4; return; }
    if (strncmp(ec->s+p, "false", 5)==0 && !is_idch(ec->s[p+5])) { bc_b(OP_PUSH_FALSE); ec->p = p+5; return; }
    if (strncmp(ec->s+p, "null", 4)==0 && !is_idch(ec->s[p+4])) { emit_push_int(0); ec->p = p+4; return; }
    /* 括号 */
    if (ec->s[p] == '(') { ec->p = p+1; parse_expr(ec); p = skip_sp(ec->s, ec->p); if (ec->s[p]==')') ec->p = p+1; return; }
    /* len(...) */
    if (strncmp(ec->s+p, "len(", 4)==0) { ec->p = p+4; parse_expr(ec); p = skip_sp(ec->s, ec->p); if (ec->s[p]==')') ec->p = p+1; bc_b(OP_LENGTH); return; }
    /* ord(...) */
    if (strncmp(ec->s+p, "ord(", 4)==0) { ec->p = p+4; parse_expr(ec); p = skip_sp(ec->s, ec->p); if (ec->s[p]==')') ec->p = p+1; return; }
    /* 数组 [...] */
    if (ec->s[p] == '[') {
        ec->p = p+1;
        bc_b(OP_ARRAY_LITERAL);
        while (1) {
            p = skip_sp(ec->s, ec->p);
            if (ec->s[p]==']') { ec->p = p+1; break; }
            if (ec->s[p]==',') ec->p = p+1;
            parse_expr(ec);
            p = skip_sp(ec->s, ec->p);
            if (ec->s[p]==']') { ec->p = p+1; break; }
        }
        return;
    }
    /* 对象 {...} */
    if (ec->s[p] == '{') { emit_push_int(0); int d = 1; ec->p = p+1; while (ec->p < ec->len && d > 0) { if (ec->s[ec->p]=='{') d++; else if (ec->s[ec->p]=='}') d--; ec->p++; } return; }
    /* 一元 ! 和 - */
    if (ec->s[p] == '!') { ec->p = p+1; parse_expr(ec); emit_push_int(0); bc_b(OP_EQUAL); return; }
    if (ec->s[p] == '-') { ec->p = p+1; parse_expr(ec); emit_push_int(0); bc_b(OP_SUB); return; }
    /* 标识符 */
    { int ep; char *id = extract_id(ec->s, p, &ep);
        if (id) {
            ec->p = ep;
            int p2 = skip_sp(ec->s, ec->p);
            /* 函数调用 id(...) */
            if (ec->s[p2] == '(') {
                ec->p = p2 + 1;
                int nargs = 0;
                while (1) {
                    p2 = skip_sp(ec->s, ec->p);
                    if (ec->s[p2] == ')') { ec->p = p2 + 1; break; }
                    if (nargs > 0) { if (ec->s[p2] == ',') ec->p = p2 + 1; }
                    parse_expr(ec);
                    nargs++;
                    p2 = skip_sp(ec->s, ec->p);
                    if (ec->s[p2] == ')') { ec->p = p2 + 1; break; }
                }
                bc_b(OP_FUNC_CALL_STMT); bc_strz(id); bc_b((uint8_t)nargs);
                free(id);
                return;
            }
            /* 数组索引 id[...] */
            if (ec->s[p2] == '[') {
                ec->p = p2 + 1;
                parse_expr(ec);
                p2 = skip_sp(ec->s, ec->p);
                if (ec->s[p2] == ']') ec->p = p2 + 1;
                bc_b(OP_LOAD_ARRAY); bc_strz(id);
                free(id);
                return;
            }
            /* 成员访问 id.member */
            if (ec->s[p2] == '.') {
                ec->p = p2 + 1;
                int ep2; char *m = extract_id(ec->s, ec->p, &ep2);
                if (m) {
                    ec->p = ep2;
                    bc_b(OP_LOAD_MEMBER); bc_strz(m); free(m);
                }
                free(id); return;
            }
            emit_load_var(id);
            free(id);
            return;
        }
    }
    ec->p = p + 1;
}

/* 算符优先级 */
static int op_prec(const char *s, int p) {
    if (s[p]=='|' && s[p+1]=='|') return 1;
    if (s[p]=='&' && s[p+1]=='&') return 2;
    if ((s[p]=='=' && s[p+1]=='=') || (s[p]=='!' && s[p+1]=='=')) return 3;
    if (s[p]=='<' || s[p]=='>') {
        if (s[p+1]=='=') return 4; else return 4;
    }
    if (s[p]=='+' || s[p]=='-') return 5;
    if (s[p]=='*' || s[p]=='/') return 6;
    return 0;
}
static int op_len2(const char *s, int p) {
    if ((s[p]=='|'&&s[p+1]=='|')||(s[p]=='&'&&s[p+1]=='&')||
        (s[p]=='='&&s[p+1]=='=')||(s[p]=='!'&&s[p+1]=='=')||
        (s[p]=='<'&&s[p+1]=='=')||(s[p]=='>'&&s[p+1]=='=')) return 2;
    return 1;
}

/* 普拉特解析 */
static void parse_expr_pratt(ExprCtx *ec, int minp) {
    parse_primary(ec);
    while (1) {
        int p = skip_sp(ec->s, ec->p);
        if (p >= ec->len) break;
        int prec = op_prec(ec->s, p);
        if (prec == 0 || prec < minp) break;
        int olen = op_len2(ec->s, p);
        
        if (prec <= 2) { /* || && */
            ec->p = p + olen; parse_expr_pratt(ec, prec + 1);
            if (ec->s[p] == '|') { bc_b(OP_ADD); emit_push_int(0); bc_b(OP_GREATER); }
            else { bc_b(OP_MUL); emit_push_int(0); bc_b(OP_GREATER); }
            continue;
        }
        if (prec == 3 || prec == 4) { /* == != < > <= >= */
            ec->p = p + olen; parse_expr_pratt(ec, prec + 1);
            int op = -1;
            if (ec->s[p]=='=' && ec->s[p+1]=='=') op = OP_EQUAL;
            else if (ec->s[p]=='!' && ec->s[p+1]=='=') op = OP_NOT_EQUAL;
            else if (ec->s[p]=='<' && ec->s[p+1]=='=') op = OP_LESS_EQ;
            else if (ec->s[p]=='>' && ec->s[p+1]=='=') op = OP_GREATER_EQ;
            else if (ec->s[p]=='<') op = OP_LESS;
            else if (ec->s[p]=='>') op = OP_GREATER;
            if (op > 0) bc_b((uint8_t)op);
            continue;
        }
        if (prec == 5 || prec == 6) { /* + - * / */
            ec->p = p + olen; parse_expr_pratt(ec, prec + 1);
            int op = -1;
            if (ec->s[p]=='+') op = OP_ADD;
            else if (ec->s[p]=='-') op = OP_SUB;
            else if (ec->s[p]=='*') op = OP_MUL;
            else if (ec->s[p]=='/') op = OP_DIV;
            if (op > 0) bc_b((uint8_t)op);
            continue;
        }
        break;
    }
}

static void parse_expr(ExprCtx *ec) { parse_expr_pratt(ec, 0); }

/* ========== 编译 ========== */
/* 编译import */
static void comp_import(const char *line, int p) {
    p = skip_sp(line, p+6); int ep;
    char *path = extract_str(line, p, &ep);
    if (!path) { fprintf(stderr, "import语法错误\n"); return; }
    bc_b(OP_IMPORT); bc_strz(path);
    printf("  import \"%s\"\n", path);
    free(path);
}

/* 编译量子门 */
static int comp_gate(const char *line, int p) {
    int ep; char *g = extract_id(line, p, &ep);
    if (!g) return -1;
    int op = -1;
    if (!strcmp(g,"H")) op=OP_H; else if (!strcmp(g,"X")) op=OP_X;
    else if (!strcmp(g,"Y")) op=OP_Y; else if (!strcmp(g,"Z")) op=OP_Z;
    else if (!strcmp(g,"T")) op=OP_T; else if (!strcmp(g,"S")) op=OP_S;
    else if (!strcmp(g,"CNOT")) op=OP_CNOT; else if (!strcmp(g,"MEASURE")) op=OP_MEASURE;
    else if (!strcmp(g,"RESET")) op=OP_RESET; else if (!strcmp(g,"SWAP")) op=OP_SWAP;
    else if (!strcmp(g,"PRINT")) op=OP_PRINT; else if (!strcmp(g,"STOP")) op=OP_STOP;
    else if (!strcmp(g,"BARRIER")) op=OP_BARRIER; else if (!strcmp(g,"NOP")) op=OP_NOP;
    else if (!strcmp(g,"init")) op=OP_INIT_N;
    if (op < 0) { free(g); return -1; }
    bc_b((uint8_t)op);
    p = ep;
    while (1) { int v, ev; p = skip_sp(line, p); if (line[p]==';'||line[p]=='\0'||line[p]=='/'||extract_int(line,p,&ev,&v)!=0) break; bc_b((uint8_t)v); p = ev; }
    printf("   %s\n", g);
    free(g); return 0;
}

/* 连接跨行括号内容：从line_idx开始，如果当前行有未闭合的[]或{}，
   继续读取后续行直到括号闭合。返回分配的字符串（调用者free）*/
static char *join_brackets(Src *sf, int *line_idx) {
    int bufsz = 4096;
    char *buf = (char*)malloc(bufsz);
    int bufpos = 0;
    int depth = 0;
    int in_str = 0;
    
    for (int i = *line_idx; i < sf->n; i++) {
        const char *line = sf->l[i];
        /* 扩展缓冲区 */
        int need = bufpos + strlen(line) + 2;
        if (need > bufsz) { while (need > bufsz) bufsz *= 2; buf = (char*)realloc(buf, bufsz); }
        
        /* 复制行内容，跟踪括号深度 */
        for (int j = 0; line[j]; j++) {
            char c = line[j];
            if (in_str) {
                if (c == '"' && (j == 0 || line[j-1] != '\\')) in_str = 0;
                buf[bufpos++] = c;
            } else if (c == '"') {
                in_str = 1;
                buf[bufpos++] = c;
            } else if (c == '/' && line[j+1] == '/') {
                /* 行注释，跳过剩余部分 */
                break;
            } else {
                if (c == '[' || c == '{') depth++;
                else if (c == ']' || c == '}') depth--;
                buf[bufpos++] = c;
            }
        }
        buf[bufpos] = '\0';
        
        *line_idx = i;
        
        /* 如果括号已闭合，且不在字符串中，返回 */
        if (depth <= 0 && !in_str) {
            return buf;
        }
        
        /* 添加换行符（替换源文件中的换行） */
        if (bufpos + 1 < bufsz) { buf[bufpos++] = ' '; buf[bufpos] = '\0'; }
    }
    
    buf[bufpos] = '\0';
    return buf;
}
static int compile_file(const char *ipath, const char *opath) {
    Src *sf = src_load(ipath);
    if (!sf) { fprintf(stderr, "无法打开 %s\n", ipath); return -1; }
    bc_init();
    
    int ind_stk[512], ind_top = 0; ind_stk[0] = 0;
    int func_stk[512], func_top = 0;
    
    printf("\n===== 编译 %s =====\n", ipath);
    
    for (int i = 0; i < sf->n; i++) {
        const char *line = sf->l[i];
        int indent = get_indent(line);
        int p = skip_sp(line, 0);
        
        /* 空行/注释跳过 */
        if (line[p] == '\0' || (line[p]=='/' && line[p+1]=='/')) continue;
        
        /* 缩进变化：结束之前打开的块 */
        while (ind_top > 0 && indent <= ind_stk[ind_top]) {
            /* 如果当前在函数体中，发出BC_FUNC_END */
            if (func_top > 0 && func_stk[func_top-1] == ind_top) {
                bc_b(BC_FUNC_END);
                printf("  [函数结束]\n");
                func_top--;
            }
            ind_top--;
        }
        
        printf("[%4d|i=%d] %s\n", i+1, indent, line);
        
        /* ==== 判断语句类型 ==== */
        
        /* import */
        if (strncmp(line+p, "import", 6) == 0 && (line[p+6]==' '||line[p+6]=='\t'||line[p+6]=='"')) {
            comp_import(line, p);
            goto next_line;
        }
        
        /* const/var */
        if ((strncmp(line+p, "const",5)==0 || strncmp(line+p, "var",3)==0) &&
            (line[p+ (line[p]=='v'?3:5)] == ' ' || line[p+ (line[p]=='v'?3:5)] == '\t')) {
            int is_const = (line[p] == 'c');
            int kwlen = is_const ? 5 : 3;
            int ep; char *name = extract_id(line, p+kwlen, &ep);
            if (!name) { fprintf(stderr, "   var/const错误\n"); continue; }
            printf("  %s %s\n", is_const ? "const" : "var", name);
            
            if (is_const) {
                /* const: QVM格式是 OP_CONST_DEF | off(2B) | len(2B) | value(2B) | name(len) */
                bc_b(OP_CONST_DEF);
                int hdr_pos = bc_tell();
                bc_u16(0); /* off（内联模式） */
                bc_u16(0); /* len（占位） */
                int val = 0; /* 默认值 */
                int p2 = skip_sp(line, ep);
                if (line[p2] == '=') {
                    int p3 = skip_sp(line, p2 + 1);
                    int ep2, v;
                    if (extract_int(line, p3, &ep2, &v) == 0) val = v;
                }
                bc_u16((uint16_t)(val & 0xFFFF));
                int str_pos = bc_tell();
                for (const char *cp = name; *cp; cp++) bc_b(*cp);
                /* 回填len */
                bc_patch16(hdr_pos + 2, (uint16_t)(bc_tell() - str_pos));
            } else {
                /* var: OP_VAR_DECL | name | [expr] | [OP_ASSIGN_STMT | name] */
                bc_b(OP_VAR_DECL);
                bc_strz(name);
                /* 检查 = 赋值 */
                int p2 = skip_sp(line, ep);
                if (line[p2] == '=') {
                    int p3 = skip_sp(line, p2 + 1);
                    if (line[p3] == '[' || line[p3] == '{') {
                        /* 先检查是否同行闭合 */
                        int depth = 1, in_str = 0;
                        for (int cp = p3 + 1; line[cp] && depth > 0; cp++) {
                            if (in_str) { if (line[cp] == '\"') in_str = 0; }
                            else if (line[cp] == '\"') in_str = 1;
                            else if (line[cp] == '[' || line[cp] == '{') depth++;
                            else if (line[cp] == ']' || line[cp] == '}') depth--;
                        }
                        if (depth == 0) {
                            /* 同行闭合，直接用原行 */
                            ExprCtx ec; ec.s = line; ec.p = p3; ec.len = strlen(line);
                            parse_expr(&ec);
                        } else {
                            /* 多行：用join_brackets */
                            char *joined = join_brackets(sf, &i);
                            if (joined) {
                                ExprCtx ec; ec.s = joined; ec.p = 0; ec.len = strlen(joined);
                                parse_expr(&ec);
                                free(joined);
                            }
                        }
                    } else {
                        ExprCtx ec; ec.s = line; ec.p = p3; ec.len = strlen(line);
                        parse_expr(&ec);
                    }
                    bc_b(OP_ASSIGN_STMT); bc_strz(name);
                }
            }
            free(name);
            goto next_line;
        }
        
        /* def */
        if (strncmp(line+p, "def", 3) == 0 && (line[p+3]==' '||line[p+3]=='\t')) {
            int ep; char *name = extract_id(line, p+3, &ep);
            if (!name) continue;
            int nargs = 0;
            int p2 = skip_sp(line, ep);
            if (line[p2] == '(') {
                p2++;
                while (1) {
                    p2 = skip_sp(line, p2);
                    if (line[p2] == ')') break;
                    int pep; char *par = extract_id(line, p2, &pep);
                    if (par) { nargs++; free(par); p2 = pep; }
                    p2 = skip_sp(line, p2);
                    if (line[p2] == ',') p2++;
                    else if (line[p2] == ')') break;
                }
            }
            bc_b(OP_FUNC_DEF); bc_strz(name); bc_b((uint8_t)nargs);
            printf("  def %s(%d)\n", name, nargs);
            free(name);
            /* 记录函数体开始 */
            if (func_top < 256) func_stk[func_top++] = ind_top + 1;
            goto next_line;
        }
        
        /* return */
        if (strncmp(line+p, "return", 6) == 0) {
            int p2 = skip_sp(line, p+6);
            if (line[p2] != ';' && line[p2] != '\0' && line[p2] != '/') {
                ExprCtx ec; ec.s = line; ec.p = p2; ec.len = strlen(line);
                parse_expr(&ec);
            }
            bc_b(OP_RETURN_STMT);
            printf("  return\n");
            goto next_line;
        }
        
        /* if */
        if (strncmp(line+p, "if", 2) == 0 && (line[p+2]==' '||line[p+2]=='\t')) {
            ExprCtx ec; ec.s = line; ec.p = skip_sp(line, p+2); ec.len = strlen(line);
            parse_expr(&ec);
            bc_b(OP_IF_STMT);
            printf("  if\n");
            goto next_line;
        }
        
        /* else */
        if (strncmp(line+p, "else", 4) == 0) {
            bc_b(OP_ELSE_STMT);
            printf("  else\n");
            goto next_line;
        }
        
        /* while */
        if (strncmp(line+p, "while", 5) == 0 && (line[p+5]==' '||line[p+5]=='\t')) {
            ExprCtx ec; ec.s = line; ec.p = skip_sp(line, p+5); ec.len = strlen(line);
            parse_expr(&ec);
            bc_b(OP_WHILE_STMT);
            printf("  while\n");
            goto next_line;
        }
        
        /* break */
        if (strncmp(line+p, "break", 5) == 0) { bc_b(OP_BREAK_STMT); printf("  break\n"); goto next_line; }
        /* continue */
        if (strncmp(line+p, "continue", 8) == 0) { bc_b(OP_CONTINUE_STMT); printf("  continue\n"); goto next_line; }
        
        /* 量子门 */
        if (comp_gate(line, p) == 0) goto next_line;
        
        /* 函数调用 / 赋值 / 表达式 */
        {
            int ep; char *name = extract_id(line, p, &ep);
            if (name) {
                int p2 = skip_sp(line, ep);
                /* name = expr; 赋值 */
                if (line[p2] == '=') {
                    ExprCtx ec; ec.s = line; ec.p = skip_sp(line, p2+1); ec.len = strlen(line);
                    parse_expr(&ec);
                    bc_b(OP_ASSIGN_STMT); bc_strz(name);
                    printf("   %s = expr\n", name);
                    free(name);
                    goto next_line;
                }
                /* name(...) 函数调用 */
                if (line[p2] == '(') {
                    p2++;
                    int nargs = 0;
                    while (1) {
                        p2 = skip_sp(line, p2);
                        if (line[p2] == ')') break;
                        if (nargs > 0) { if (line[p2]==',') p2++; }
                        ExprCtx ec; ec.s = line; ec.p = p2; ec.len = strlen(line);
                        parse_expr(&ec);
                        nargs++;
                        p2 = skip_sp(line, bc_tell()?bc_tell():0); // can't get pos from expr
                        p2 = skip_sp(line, ec.p);
                        if (line[p2] == ',') p2++;
                        else if (line[p2] == ')') { p2++; break; }
                        else break;
                    }
                    bc_b(OP_FUNC_CALL_STMT); bc_strz(name); bc_b((uint8_t)nargs);
                    free(name);
                    printf("   call\n");
                    goto next_line;
                }
                /* 其他表达式 */
                ExprCtx ec; ec.s = line; ec.p = p; ec.len = strlen(line);
                parse_expr(&ec);
                free(name);
                goto next_line;
            }
        }
        
        /* 未知语句 */
        fprintf(stderr, "   无法编译\n");
        
next_line:
        /* 记录缩进 */
        if (ind_top < 256) { ind_top++; ind_stk[ind_top] = indent; }
    }
    
    /* 关闭所有打开的函数 */
    while (func_top > 0) {
        bc_b(BC_FUNC_END);
        printf("  [关闭函数]\n");
        func_top--;
    }
    
    printf("===== 编译完成: %d 字节 =====\n", bc_pos);
    
    if (bc_save(opath) < 0) { bc_free(); src_free(sf); return -1; }
    printf("[输出] %s (%d 字节)\n", opath, bc_pos);
    bc_free(); src_free(sf);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "用法: %s <输入.qentl> <输出.qbc>\n", argv[0]);
        return 1;
    }
    return compile_file(argv[1], argv[2]);
}