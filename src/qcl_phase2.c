/*
 * qcl_phase2.c — QCL引导器 Stage 2 编译器
 *
 * 架构定位：
 *   qcl_bootstrap.c (C解释器) — 阶段1，只编译量子指令子集
 *   qcl_phase2.c  (Stage 2)  — 扩展解析 import/const/def/类型/函数体
 *   QCL引导器.qentl           — 阶段3，QCL编译器(QEntL全栈)
 *
 * 输出字节码格式：
 *   首字节 0x14 (QEntL字节码魔数)
 *   后接量子指令 + 高级语法操作码 + OP_STOP
 *
 * 红线：不修改 qcl_bootstrap.c，不向主编译循环注入parse_import调用
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <ctype.h>

#define MAX_LINE_LEN 4096
#define MAX_OPS      262144
#define MAX_TOKENS   65536
#define MAX_FUNC_BODY 65536
#define MAX_STRING   1024
#define MAX_IDENT    256

typedef enum {
    BC_MAGIC     = 0x14,
    OP_NOP       = 0,
    OP_H         = 1,
    OP_X         = 2,
    OP_Z         = 3,
    OP_CNOT      = 4,
    OP_MEASURE   = 5,
    OP_RESET     = 6,
    OP_SWAP      = 7,
    OP_LOAD_REG  = 8,
    OP_STORE_REG = 9,
    OP_JUMP      = 10,
    OP_PRINT     = 11,
    OP_ADD       = 16,
    OP_SUB       = 13,
    OP_MUL       = 15,
    OP_DIV       = 14,
    OP_EXIT      = 17,
    OP_BARRIER   = 18,
    OP_INIT_N    = 20,
    OP_STOP      = 12,
    OP_T         = 35,
    OP_S         = 36,
    OP_Y         = 37,
    OP_LINUX     = 200,
    OP_WINDOWS   = 201,
    OP_IOS       = 202,
    OP_ANDROID   = 203,
    OP_HARMONY   = 204,
    OP_IMPORT          = 100,
    OP_CONST_DEF       = 101,
    OP_FUNC_DEF        = 102,
    OP_FUNC_END        = 103,
    OP_TYPE_DEF        = 104,
    OP_TYPE_END        = 105,
    OP_VAR_DECL        = 106,
    OP_RETURN_STMT     = 107,
    OP_IF_STMT         = 108,
    OP_ELSE_STMT       = 109,
    OP_WHILE_STMT      = 110,
    OP_ASSIGN_STMT     = 111,
    OP_FUNC_CALL_STMT  = 112,
    OP_BREAK_STMT      = 113,
    OP_CONTINUE_STMT   = 114,
    OP_PUSH_CONST_INT  = 120,
    OP_PUSH_CONST_STR  = 121,
    OP_APPEND_BYTE     = 130,
    OP_BYTECODE_LEN    = 131,
    OP_EXPORT_SYM      = 140,
    BC_FUNC_BODY       = 255,
    BC_FUNC_END        = 254,
} Opcode;

typedef struct {
    const char *name;
    Opcode     op;
} GateMapEntry;

static const GateMapEntry GATE_MAP[] = {
    {"H", OP_H}, {"X", OP_X}, {"Y", OP_Y},
    {"Z", OP_Z}, {"T", OP_T}, {"S", OP_S},
    {NULL, OP_NOP}
};

/* ==================== 全局缓冲区 ==================== */
static unsigned char g_bytecode[MAX_OPS];
static int           g_bc_pos = 0;
static unsigned char g_highbuf[MAX_FUNC_BODY];
static int           g_highbuf_pos = 0;
static char g_strpool[MAX_FUNC_BODY];
static int  g_strpool_pos = 0;

/* ==================== 字节码写入函数 ==================== */
static void write_byte(unsigned char b) {
    if (g_bc_pos < MAX_OPS) g_bytecode[g_bc_pos++] = b;
}
static void write_opcode(Opcode op)    { write_byte((unsigned char)op); }
static void write_u8(unsigned char v)  { write_byte(v); }
static void write_u16(unsigned short v) {
    write_byte(v & 0xFF);
    write_byte((v >> 8) & 0xFF);
}
static void write_string_ref(const char *s) {
    int len = (int)strlen(s);
    if (len == 0) return;
    /* 为每个字符串分配新的string pool偏移 */
    int off = g_strpool_pos;
    if (off + len > MAX_FUNC_BODY) return;
    memcpy(g_strpool + off, s, len);
    g_strpool_pos += len;
    write_u16((unsigned short)off);  /* string_pool_offset */
    write_u16((unsigned short)len);   /* length */
}
static void flush_highbuf(void) {
    if (g_highbuf_pos > 0 && g_bc_pos + g_highbuf_pos <= MAX_OPS) {
        memcpy(g_bytecode + g_bc_pos, g_highbuf, g_highbuf_pos);
        g_bc_pos += g_highbuf_pos;
    }
    g_highbuf_pos = 0;
}
static void write_high_byte(unsigned char b) {
    if (g_highbuf_pos < MAX_FUNC_BODY) g_highbuf[g_highbuf_pos++] = b;
}
static void write_high_opcode(Opcode op) { write_high_byte((unsigned char)op); }

/* ==================== 词法分析器 ==================== */
typedef enum {
    TOK_EOF = 0,
    TOK_IDENT  = 1,
    TOK_NUMBER = 2,
    TOK_STRING = 3,
    TOK_CHAR   = 4,
    TOK_PLUS   = 5,
    TOK_MINUS  = 6,
    TOK_STAR   = 7,
    TOK_SLASH  = 8,
    TOK_PERC   = 9,
    TOK_EQ     = 10,
    TOK_NEQ    = 11,
    TOK_LTE    = 12,
    TOK_GTE    = 13,
    TOK_LT     = 14,
    TOK_GT     = 15,
    TOK_LPAR   = 16,
    TOK_RPAR   = 17,
    TOK_LBRACE = 18,
    TOK_RBRACE = 19,
    TOK_LBRK   = 20,
    TOK_RBRK   = 21,
    TOK_COMMA  = 22,
    TOK_DOT    = 23,
    TOK_SEMI   = 24,
    TOK_COLON  = 25,
    TOK_ANDAND = 26,
    TOK_OROR   = 27,
    TOK_ARROW  = 28,
    TOK_SHEQ   = 29,
    TOK_SHE    = 30,
    TOK_SHL    = 31,
    TOK_SHLEQ  = 32,
    TOK_HASH   = 33,
    TOK_DSLASH = 34,
    TOK_ERR    = 99,
} TokenKind;

typedef struct {
    TokenKind kind;
    int line, col;
    char text[MAX_STRING];
} Token;

typedef struct {
    const char *src;
    int len, pos, line, col;
    Token cur;
} Lexer;

static void lexer_skip_ws(Lexer *L) {
    while (L->pos < L->len) {
        int ch = (unsigned char)L->src[L->pos];
        if (ch == ' ' || ch == '\t' || ch == '\r' || ch == '\n' || ch == '\f' || ch == '\v') {
            if (ch == '\n') { L->line++; L->col = 1; }
            L->pos++; L->col++;
        }
        else break;
    }
}

static void lexer_next(Lexer *L) {
    /* 跳过前导空白（含换行） */
    lexer_skip_ws(L);
    Token *t = &L->cur;
    t->kind = TOK_EOF;
    t->text[0] = '\0';
    if (L->pos >= L->len) return;
    int ch = (unsigned char)L->src[L->pos];

    if (ch == '/' && L->pos+1 < L->len && L->src[L->pos+1] == '/') {
        while (L->pos < L->len && L->src[L->pos] != '\n') L->pos++;
        lexer_next(L); return;
    }
    if (ch == '#') {
        while (L->pos < L->len && L->src[L->pos] != '\n') L->pos++;
        lexer_next(L); return;
    }
    if (ch == '/' && L->pos+1 < L->len && L->src[L->pos+1] == '*') {
        L->pos += 2; L->col += 2;
        while (L->pos+1 < L->len && !(L->src[L->pos]=='*' && L->src[L->pos+1]=='/')) {
            if (L->src[L->pos] == '\n') { L->line++; L->col = 1; }
            else L->col++;
            L->pos++;
        }
        if (L->pos < L->len) { L->pos += 2; L->col += 2; }
        lexer_next(L); return;
    }

    t->line = L->line; t->col = L->col;

    if (ch == '"') {
        int i = 0;
        L->pos++; L->col++;
        while (L->pos < L->len && L->src[L->pos] != '"' && L->src[L->pos] != '\n') {
            if (i < MAX_STRING-1) t->text[i++] = L->src[L->pos];
            L->pos++; L->col++;
        }
        t->text[i] = '\0';
        if (L->pos < L->len) { L->pos++; L->col++; }
        t->kind = TOK_STRING; return;
    }
    if (ch == '\'') {
        L->pos++; L->col++;
        if (L->pos < L->len) { t->text[0] = L->src[L->pos]; t->text[1] = '\0'; L->pos++; L->col++; }
        if (L->pos < L->len && L->src[L->pos] == '\'') { L->pos++; L->col++; }
        t->kind = TOK_CHAR; return;
    }
    if (ch >= '0' && ch <= '9') {
        int i = 0, dot = 0;
        while (L->pos < L->len) {
            int c = (unsigned char)L->src[L->pos];
            if (c >= '0' && c <= '9') {
                if (i < MAX_STRING-1) t->text[i++] = L->src[L->pos];
                L->pos++; L->col++;
            } else if (c == '.' && !dot) {
                dot = 1;
                if (i < MAX_STRING-1) t->text[i++] = L->src[L->pos];
                L->pos++; L->col++;
            } else break;
        }
        t->text[i] = '\0';
        t->kind = TOK_NUMBER; return;
    }
    if (ch == '_' || ch == '$' || ch == '@' || isalpha(ch) || ch >= 0x80) {
        int i = 0;
        while (L->pos < L->len) {
            int c = (unsigned char)L->src[L->pos];
            if (c == '_' || c == '$' || isalnum(c) || c >= 0x80) {
                if (i < MAX_STRING-1) t->text[i++] = L->src[L->pos];
                L->pos++; L->col++;
            } else break;
        }
        t->text[i] = '\0';
        t->kind = TOK_IDENT; return;
    }
    if (L->pos + 1 < L->len) {
        int c1 = (unsigned char)L->src[L->pos];
        int c2 = (unsigned char)L->src[L->pos+1];
        if (c1=='=' && c2=='=') { t->kind=TOK_EQ;     L->pos+=2; L->col+=2; return; }
        if (c1=='!' && c2=='=') { t->kind=TOK_NEQ;    L->pos+=2; L->col+=2; return; }
        if (c1=='<' && c2=='=') { t->kind=TOK_LTE;    L->pos+=2; L->col+=2; return; }
        if (c1=='>' && c2=='=') { t->kind=TOK_GTE;    L->pos+=2; L->col+=2; return; }
        if (c1=='&' && c2=='&') { t->kind=TOK_ANDAND; L->pos+=2; L->col+=2; return; }
        if (c1=='|' && c2=='|') { t->kind=TOK_OROR;   L->pos+=2; L->col+=2; return; }
        if (c1=='>' && c2=='>') {
            if (L->pos+2 < L->len && L->src[L->pos+2]=='=') { t->kind=TOK_SHEQ; L->pos+=3; L->col+=3; return; }
            t->kind=TOK_SHE; L->pos+=2; L->col+=2; return;
        }
        if (c1=='<' && c2=='<') {
            if (L->pos+2 < L->len && L->src[L->pos+2]=='=') { t->kind=TOK_SHLEQ; L->pos+=3; L->col+=3; return; }
            t->kind=TOK_SHL; L->pos+=2; L->col+=2; return;
        }
        if (c1=='-' && c2=='>') { t->kind=TOK_ARROW; L->pos+=2; L->col+=2; return; }
    }
    switch (ch) {
        case '+': t->kind=TOK_PLUS;   break;
        case '-': t->kind=TOK_MINUS;  break;
        case '*': t->kind=TOK_STAR;   break;
        case '/': t->kind=TOK_SLASH;  break;
        case '%': t->kind=TOK_PERC;   break;
        case '=': t->kind=TOK_EQ;     break;
        case '<': t->kind=TOK_LT;     break;
        case '>': t->kind=TOK_GT;     break;
        case '(': t->kind=TOK_LPAR;   break;
        case ')': t->kind=TOK_RPAR;   break;
        case '{': t->kind=TOK_LBRACE; break;
        case '}': t->kind=TOK_RBRACE; break;
        case '[': t->kind=TOK_LBRK;   break;
        case ']': t->kind=TOK_RBRK;   break;
        case ',': t->kind=TOK_COMMA;  break;
        case '.': t->kind=TOK_DOT;    break;
        case ';': t->kind=TOK_SEMI;   break;
        case ':': t->kind=TOK_COLON;  break;
        case '#': t->kind=TOK_HASH;   break;
        default:  t->kind=TOK_ERR;    break;
    }
    t->text[0] = (char)ch; t->text[1] = '\0';
    L->pos++; L->col++;
}

static int kw(const Token *t, const char *s) {
    return t->kind == TOK_IDENT && strcmp(t->text, s) == 0;
}

/* ==================== 解析器 ==================== */
typedef struct {
    Lexer  lexer;
    int func_depth;
    int type_depth;
    int brace_depth;
    int compiled;
    int high_level;
} Parser;

static Token consume(Parser *P) {
    Token t = P->lexer.cur;
    lexer_next(&P->lexer);
    return t;
}
static int expect_tok(Parser *P, TokenKind k) {
    if (P->lexer.cur.kind == k) { consume(P); return 1; }
    return 0;
}
static void skip_to_semi(Parser *P) {
    while (P->lexer.cur.kind != TOK_EOF && P->lexer.cur.kind != TOK_SEMI)
        consume(P);
    if (P->lexer.cur.kind == TOK_SEMI) consume(P);
}
static void skip_brace_block(Parser *P) {
    int d = 1;
    consume(P);
    while (d > 0 && P->lexer.cur.kind != TOK_EOF) {
        if (P->lexer.cur.kind == TOK_LBRACE) d++;
        else if (P->lexer.cur.kind == TOK_RBRACE) d--;
        consume(P);
    }
}
/* 向前声明：parse_compound_block 内部调用的后续定义的函数 */
static int  parse_const_int(const char *s);
static void skip_brace_block_alt(Parser *P, TokenKind open, TokenKind close);
static void skip_to_semi_or_rpar(Parser *P);
static int  parse_quantum_instruction(Parser *P);
static int  parse_import(Parser *P);
static int  parse_const(Parser *P);
static void parse_func_body(Parser *P);
/* 递归解析 if/while/else 大括号内的语句块（var/return/if/while/assign/func_call/def 等） */
static void parse_compound_block(Parser *P) {
    if (P->lexer.cur.kind != TOK_LBRACE) return;
    consume(P); /* 消耗 '{' */
    int d = 1;
    while (d > 0 && P->lexer.cur.kind != TOK_EOF) {
        Token t = P->lexer.cur;
        if (t.kind == TOK_LBRACE) { d++; consume(P); continue; }
        if (t.kind == TOK_RBRACE) { d--; consume(P); continue; }

        if (kw(&t, "def")) {
            consume(P);
            if (P->lexer.cur.kind == TOK_IDENT) {
                write_high_opcode(OP_FUNC_DEF);
                write_string_ref(P->lexer.cur.text);
                consume(P);
            }
            if (P->lexer.cur.kind == TOK_LPAR) {
                int pd = 1; consume(P);
                while (pd > 0 && P->lexer.cur.kind != TOK_EOF) {
                    if (P->lexer.cur.kind == TOK_LPAR) pd++;
                    else if (P->lexer.cur.kind == TOK_RPAR) pd--;
                    consume(P);
                }
            }
            if (expect_tok(P, TOK_COLON)) {}
            if (P->lexer.cur.kind == TOK_LBRACE) parse_func_body(P);
            else skip_to_semi(P);
            continue;
        }
        if (kw(&t, "import")) { if (parse_import(P)) continue; }
        if (kw(&t, "const"))  { if (parse_const(P))  continue; }
        if (kw(&t, "var")) {
            consume(P);
            if (P->lexer.cur.kind == TOK_IDENT) {
                write_high_opcode(OP_VAR_DECL);
                write_string_ref(P->lexer.cur.text);
                consume(P);
            }
            if (expect_tok(P, TOK_EQ)) {
                if (P->lexer.cur.kind == TOK_NUMBER) {
                    write_high_opcode(OP_PUSH_CONST_INT);
                    write_u16((unsigned short)parse_const_int(P->lexer.cur.text));
                    consume(P);
                } else if (P->lexer.cur.kind == TOK_STRING) {
                    write_high_opcode(OP_PUSH_CONST_STR);
                    write_string_ref(P->lexer.cur.text);
                    consume(P);
                } else if (P->lexer.cur.kind == TOK_LBRK) {
                    write_high_opcode(OP_PUSH_CONST_INT); write_u16(0);
                    skip_brace_block_alt(P, TOK_LBRK, TOK_RBRK);
                } else if (P->lexer.cur.kind == TOK_LBRACE) {
                    write_high_opcode(OP_PUSH_CONST_INT); write_u16(0);
                    parse_compound_block(P);
                } else if (P->lexer.cur.kind == TOK_IDENT) {
                    write_high_opcode(OP_PUSH_CONST_STR);
                    write_string_ref(P->lexer.cur.text);
                    consume(P);
                } else if (kw(&P->lexer.cur, "null")) {
                    write_high_opcode(OP_PUSH_CONST_INT); write_u16(0);
                    consume(P);
                }
            }
            expect_tok(P, TOK_SEMI); P->high_level++; continue;
        }
        if (kw(&t, "返回") || kw(&t, "return")) {
            consume(P);
            if (P->lexer.cur.kind == TOK_SEMI) {
                write_high_opcode(OP_RETURN_STMT); write_byte(0);
                consume(P);
            } else if (P->lexer.cur.kind == TOK_IDENT) {
                write_high_opcode(OP_RETURN_STMT); write_byte(1);
                write_string_ref(P->lexer.cur.text);
                consume(P); expect_tok(P, TOK_SEMI);
            } else if (P->lexer.cur.kind == TOK_NUMBER) {
                write_high_opcode(OP_RETURN_STMT); write_byte(2);
                write_u16((unsigned short)parse_const_int(P->lexer.cur.text));
                consume(P); expect_tok(P, TOK_SEMI);
            } else if (P->lexer.cur.kind == TOK_STRING) {
                write_high_opcode(OP_RETURN_STMT); write_byte(3);
                write_string_ref(P->lexer.cur.text);
                consume(P); expect_tok(P, TOK_SEMI);
            }
            P->high_level++; continue;
        }
        if (kw(&t, "如果") || kw(&t, "if")) {
            consume(P);
            if (expect_tok(P, TOK_LPAR)) { skip_to_semi_or_rpar(P); if (expect_tok(P, TOK_RPAR)) {} }
            if (P->lexer.cur.kind == TOK_LBRACE) { write_high_opcode(OP_IF_STMT); parse_compound_block(P); }
            if (kw(&P->lexer.cur, "否则") || kw(&P->lexer.cur, "else")) {
                consume(P);
                if (P->lexer.cur.kind == TOK_LBRACE) { write_high_opcode(OP_ELSE_STMT); parse_compound_block(P); }
            }
            P->high_level++; continue;
        }
        if (kw(&t, "循环") || kw(&t, "while") || kw(&t, "当")) {
            consume(P);
            if (expect_tok(P, TOK_LPAR)) { skip_to_semi_or_rpar(P); if (expect_tok(P, TOK_RPAR)) {} }
            if (P->lexer.cur.kind == TOK_LBRACE) { write_high_opcode(OP_WHILE_STMT); parse_compound_block(P); }
            P->high_level++; continue;
        }
        if (kw(&t, "跳出") || kw(&t, "break")) {
            consume(P); expect_tok(P, TOK_SEMI);
            write_high_opcode(OP_BREAK_STMT); P->high_level++; continue;
        }
        if (kw(&t, "继续") || kw(&t, "continue")) {
            consume(P); expect_tok(P, TOK_SEMI);
            write_high_opcode(OP_CONTINUE_STMT); P->high_level++; continue;
        }
        /* 顶层赋值 / 函数调用（标识符开头） */
        if (t.kind == TOK_IDENT) {
            const char *nm = t.text;
            consume(P);
            if (P->lexer.cur.kind == TOK_LPAR) { /* func_call */
                write_high_opcode(OP_FUNC_CALL_STMT);
                write_string_ref(nm);
                int pd = 1; consume(P);
                while (pd > 0 && P->lexer.cur.kind != TOK_EOF) {
                    if (P->lexer.cur.kind == TOK_LPAR) pd++;
                    else if (P->lexer.cur.kind == TOK_RPAR) pd--;
                    consume(P);
                }
                expect_tok(P, TOK_SEMI); P->high_level++; continue;
            }
            if (P->lexer.cur.kind == TOK_EQ) { /* assign */
                write_high_opcode(OP_ASSIGN_STMT);
                write_string_ref(nm);
                consume(P); /* '=' */
                if (P->lexer.cur.kind == TOK_NUMBER) {
                    write_high_opcode(OP_PUSH_CONST_INT);
                    write_u16((unsigned short)parse_const_int(P->lexer.cur.text));
                    consume(P);
                } else if (P->lexer.cur.kind == TOK_STRING) {
                    write_high_opcode(OP_PUSH_CONST_STR);
                    write_string_ref(P->lexer.cur.text);
                    consume(P);
                } else if (P->lexer.cur.kind == TOK_IDENT) {
                    write_high_opcode(OP_PUSH_CONST_STR);
                    write_string_ref(P->lexer.cur.text);
                    consume(P);
                } else if (kw(&P->lexer.cur, "null")) {
                    write_high_opcode(OP_PUSH_CONST_INT); write_u16(0);
                    consume(P);
                }
                expect_tok(P, TOK_SEMI); P->high_level++; continue;
            }
            expect_tok(P, TOK_SEMI); continue;
        }
        /* 量子指令（STOP/H/X/CNOT 等） */
        if (parse_quantum_instruction(P)) continue;
        /* 兜底：跳过无法识别的单条语句 */
        skip_to_semi(P);
    }
}
static int parse_const_int(const char *s) {
    int v = 0;
    while (*s) { if (*s >= '0' && *s <= '9') v = v * 10 + (*s - '0'); s++; }
    return v;
}
static int is_opcode_name_unused(const char *s) { (void)s; return 0; }

/* 向前声明 */
static int  L_peek_next_is_colon(Parser *P);
static void skip_brace_block(Parser *P);
static void parse_compound_block(Parser *P);
static int  parse_const_int(const char *s);
static void skip_brace_block_alt(Parser *P, TokenKind open, TokenKind close);
static void skip_to_semi_or_rpar(Parser *P);
static int  parse_quantum_instruction(Parser *P);
static int  parse_import(Parser *P);
static int  parse_const(Parser *P);
static int  parse_type_def(Parser *P);
static int  parse_def(Parser *P);
static int  parse_export(Parser *P);
static void parse_func_body(Parser *P);
static int  parse_top_statement(Parser *P);
static void parse_class_body(Parser *P);

/* ==================== 量子指令解析 ==================== */
static int parse_quantum_instruction(Parser *P) {
    Token t = P->lexer.cur;
    if (kw(&t, "init")) {
        consume(P); lexer_skip_ws(&P->lexer); lexer_next(&P->lexer);
        int n = 0;
        if (P->lexer.cur.kind == TOK_NUMBER) { n = parse_const_int(P->lexer.cur.text); consume(P); }
        write_opcode(OP_INIT_N); write_u8(n & 0xFF); write_u8((n >> 8) & 0xFF);
        P->compiled++; return 1;
    }
    for (int i = 0; GATE_MAP[i].name; i++) {
        if (kw(&t, GATE_MAP[i].name)) {
            consume(P); lexer_skip_ws(&P->lexer); lexer_next(&P->lexer);
            int qid = 0;
            if (P->lexer.cur.kind == TOK_NUMBER) { qid = parse_const_int(P->lexer.cur.text); consume(P); }
            write_opcode(GATE_MAP[i].op); write_u8(qid);
            P->compiled++; return 1;
        }
    }
    if (kw(&t, "CNOT")) {
        consume(P); lexer_skip_ws(&P->lexer); lexer_next(&P->lexer);
        int ctrl = 0, tgt = 0;
        if (P->lexer.cur.kind == TOK_NUMBER) { ctrl = parse_const_int(P->lexer.cur.text); consume(P); }
        lexer_skip_ws(&P->lexer); lexer_next(&P->lexer);
        if (P->lexer.cur.kind == TOK_NUMBER) { tgt = parse_const_int(P->lexer.cur.text); consume(P); }
        write_opcode(OP_CNOT); write_u8(ctrl); write_u8(tgt);
        P->compiled++; return 1;
    }
    if (kw(&t, "MEASURE")) {
        consume(P); lexer_skip_ws(&P->lexer); lexer_next(&P->lexer);
        int qid = 0, reg = 0;
        if (P->lexer.cur.kind == TOK_NUMBER) { qid = parse_const_int(P->lexer.cur.text); consume(P); }
        lexer_skip_ws(&P->lexer); lexer_next(&P->lexer);
        if (P->lexer.cur.kind == TOK_NUMBER) { reg = parse_const_int(P->lexer.cur.text); consume(P); }
        write_opcode(OP_MEASURE); write_u8(qid); write_u8(reg);
        P->compiled++; return 1;
    }
    if (kw(&t, "PRINT")) {
        consume(P); lexer_skip_ws(&P->lexer); lexer_next(&P->lexer);
        int reg = 0;
        if (P->lexer.cur.kind == TOK_NUMBER) { reg = parse_const_int(P->lexer.cur.text); consume(P); }
        write_opcode(OP_PRINT); write_u8(reg);
        P->compiled++; return 1;
    }
    if (kw(&t, "STOP")) { consume(P); write_opcode(OP_STOP); P->compiled++; return 1; }
    if (kw(&t, "EXIT")) { consume(P); write_opcode(OP_EXIT); P->compiled++; return 1; }
    if (kw(&t, "SWAP")) {
        consume(P); lexer_skip_ws(&P->lexer); lexer_next(&P->lexer);
        int a = 0, b = 0;
        if (P->lexer.cur.kind == TOK_NUMBER) { a = parse_const_int(P->lexer.cur.text); consume(P); }
        lexer_skip_ws(&P->lexer); lexer_next(&P->lexer);
        if (P->lexer.cur.kind == TOK_NUMBER) { b = parse_const_int(P->lexer.cur.text); consume(P); }
        write_opcode(OP_SWAP); write_u8(a); write_u8(b);
        P->compiled++; return 1;
    }
    if (kw(&t, "RESET")) {
        consume(P); lexer_skip_ws(&P->lexer); lexer_next(&P->lexer);
        int qid = 0;
        if (P->lexer.cur.kind == TOK_NUMBER) { qid = parse_const_int(P->lexer.cur.text); consume(P); }
        write_opcode(OP_RESET); write_u8(qid);
        P->compiled++; return 1;
    }
    if (kw(&t, "BARRIER")) { consume(P); write_opcode(OP_BARRIER); P->compiled++; return 1; }
    return 0;
}

/* ==================== import / const / 类型 / def 解析 ==================== */
static int parse_import(Parser *P) {
    consume(P); /* import */
    /* 接受 import "模块名" 和 import <ident>（如 import stdlib） */
    const char *mod = NULL;
    if (P->lexer.cur.kind == TOK_STRING) {
        mod = P->lexer.cur.text;
        consume(P);
    } else if (P->lexer.cur.kind == TOK_IDENT) {
        mod = P->lexer.cur.text;
        consume(P);
    } else {
        return 0;
    }
    expect_tok(P, TOK_SEMI);
    write_opcode(OP_IMPORT); write_string_ref(mod);
    P->high_level++; return 1;
}

static int parse_const(Parser *P) {
    consume(P); /* const */
    if (P->lexer.cur.kind != TOK_IDENT) return 0;
    const char *name = P->lexer.cur.text;
    consume(P); /* 名字 */
    if (P->lexer.cur.kind != TOK_EQ) return 0;
    consume(P); /* = */
    int value = 0;
    if (P->lexer.cur.kind == TOK_NUMBER) { value = parse_const_int(P->lexer.cur.text); consume(P); }
    else if (P->lexer.cur.kind == TOK_IDENT) {
        value = parse_const_int(P->lexer.cur.text);
        consume(P);
    }
    /* 跳到行尾（可能有行内注释） */
    while (P->lexer.cur.kind != TOK_EOF && P->lexer.cur.kind != TOK_SEMI &&
           P->lexer.cur.kind != TOK_HASH)
        consume(P);
    if (P->lexer.cur.kind == TOK_SEMI) consume(P);

    write_opcode(OP_CONST_DEF); write_string_ref(name); write_u16((unsigned short)value);
    P->high_level++; return 1;
}

static int parse_type_def(Parser *P) {
    consume(P); /* 类型 */
    lexer_skip_ws(&P->lexer);
    if (P->lexer.cur.kind != TOK_IDENT) return 0;
    const char *name = P->lexer.cur.text;
    consume(P);
    /* 接受 类型 Name = { ... } 或 类型 Name { ... }（无 =） */
    lexer_skip_ws(&P->lexer);
    expect_tok(P, TOK_EQ);
    lexer_skip_ws(&P->lexer);
    if (!expect_tok(P, TOK_LBRACE)) return 0;

    write_opcode(OP_TYPE_DEF);
    write_string_ref(name);
    int field_count = 0;
    /* expect_tok(LBRACE) 已消费 {，lexer.cur 现在在第一个字段 */
    while (P->lexer.cur.kind != TOK_EOF && P->lexer.cur.kind != TOK_RBRACE) {
        if (P->lexer.cur.kind == TOK_HASH) {
            /* 跳过 # 注释，前进到下一 token */
            consume(P); continue;
        }
        if (P->lexer.cur.kind == TOK_IDENT) {
            const char *fname = P->lexer.cur.text;
            consume(P); /* 字段名 → cur 现在指向 = 或 : */
            lexer_skip_ws(&P->lexer);
            if (P->lexer.cur.kind == TOK_HASH) continue;
            if (P->lexer.cur.kind == TOK_EQ) {
                /* Name = value 枚举风格字段 */
                consume(P); /* 消费 "="，cur 现在指向值 */
                int value = 0;
                if (P->lexer.cur.kind == TOK_NUMBER) {
                    value = parse_const_int(P->lexer.cur.text);
                    consume(P);
                } else if (P->lexer.cur.kind == TOK_IDENT) {
                    value = parse_const_int(P->lexer.cur.text);
                    consume(P);
                }
                /* emit 字节码: OP_PUSH_CONST_INT + 值 + OP_EXPORT_SYM + 字段名字符串 */
                write_opcode(OP_PUSH_CONST_INT);
                write_u16((unsigned short)value);
                write_opcode(OP_EXPORT_SYM);
                write_string_ref(fname);
                field_count++;
            } else if (P->lexer.cur.kind == TOK_COLON) {
                consume(P); /* 消费 ":"，cur 现在指向类型名 */
                if (P->lexer.cur.kind == TOK_IDENT) {
                    const char *ftype = P->lexer.cur.text;
                    write_high_byte(field_count);
                    write_string_ref(fname);
                    write_string_ref(ftype);
                    field_count++;
                    consume(P);
                }
            }
            expect_tok(P, TOK_COMMA);
        } else if (P->lexer.cur.kind == TOK_IDENT && kw(&P->lexer.cur, "var")) {
            /* var 在类型体中出现时跳过 */
            consume(P);
        } else {
            /* 无法识别的 token，向前推进避免死循环 */
            consume(P);
        }
    }
    write_u16((unsigned short)field_count);
    flush_highbuf();
    expect_tok(P, TOK_RBRACE); expect_tok(P, TOK_SEMI);
    P->high_level++; return 1;
}

static int L_peek_next_is_colon(Parser *P) {
    int saved_pos = P->lexer.pos;
    int saved_col = P->lexer.col;
    lexer_next(&P->lexer);
    int is_colon = (P->lexer.cur.kind == TOK_COLON);
    P->lexer.pos = saved_pos; P->lexer.col = saved_col;
    return is_colon;
}

static void skip_brace_block_alt(Parser *P, TokenKind open, TokenKind close) {
    int d = 1;
    consume(P);
    while (d > 0 && P->lexer.cur.kind != TOK_EOF) {
        if (P->lexer.cur.kind == open) d++;
        else if (P->lexer.cur.kind == close) d--;
        consume(P);
    }
}
static void skip_to_semi_or_rpar(Parser *P) {
    while (P->lexer.cur.kind != TOK_EOF &&
           P->lexer.cur.kind != TOK_SEMI &&
           P->lexer.cur.kind != TOK_RPAR)
        consume(P);
}
static int L_is_double_slash(Parser *P) {
    int sp = P->lexer.pos;
    return (sp + 1 < P->lexer.len && P->lexer.src[sp] == '/' && P->lexer.src[sp+1] == '/');
}

/* ==================== class 体解析（递归解析方法） ==================== */
static void parse_class_body(Parser *P) {
    int d = 1;
    while (d > 0 && P->lexer.cur.kind != TOK_EOF) {
        Token t = P->lexer.cur;
        if (t.kind == TOK_LBRACE) { d++; consume(P); continue; }
        if (t.kind == TOK_RBRACE) { d--; consume(P); continue; }

        /* 跳过修饰符：private / public / protected / static / virtual / override */
        if (kw(&t, "private") || kw(&t, "public") || kw(&t, "protected") ||
            kw(&t, "static") || kw(&t, "virtual") || kw(&t, "override")) {
            consume(P); continue;
        }
        /* 跳过 this. 调用开头的 this */
        if (kw(&t, "this")) { consume(P); continue; }
        /* 跳过 super( ... ) 调用 */
        if (kw(&t, "super")) { consume(P);
            if (P->lexer.cur.kind == TOK_LPAR) {
                int pd = 1; consume(P);
                while (pd > 0 && P->lexer.cur.kind != TOK_EOF) {
                    if (P->lexer.cur.kind == TOK_LPAR) pd++;
                    else if (P->lexer.cur.kind == TOK_RPAR) pd--;
                    consume(P);
                }
            }
            skip_to_semi(P); continue;
        }
        /* 方法定义：def / 函数 / constructor */
        if (kw(&t, "def") || kw(&t, "函数") || kw(&t, "constructor")) {
            consume(P); /* def/函数/constructor → cur 已推进到函数名 */
            if (P->lexer.cur.kind == TOK_IDENT) {
                write_high_opcode(OP_FUNC_DEF);
                write_string_ref(P->lexer.cur.text);
                consume(P); /* 函数名 */
            } else {
                /* constructor() 或 constructor(...) 紧跟 (，无名字 */
                write_high_opcode(OP_FUNC_DEF);
                write_string_ref("_constructor");
            }
            /* 跳过参数列表 ( ...) */
            if (P->lexer.cur.kind == TOK_LPAR) {
                int pd = 1; consume(P);
                while (pd > 0 && P->lexer.cur.kind != TOK_EOF) {
                    if (P->lexer.cur.kind == TOK_LPAR) pd++;
                    else if (P->lexer.cur.kind == TOK_RPAR) pd--;
                    consume(P);
                }
            }
            if (expect_tok(P, TOK_COLON)) {}
            if (P->lexer.cur.kind == TOK_LBRACE) parse_class_body(P);
            else skip_to_semi(P);
            continue;
        }
        /* var 字段声明 */
        if (kw(&t, "var")) {
            consume(P);
            if (P->lexer.cur.kind == TOK_IDENT) {
                write_high_opcode(OP_VAR_DECL);
                write_string_ref(P->lexer.cur.text);
                consume(P);
            }
            if (expect_tok(P, TOK_EQ)) {
                if (P->lexer.cur.kind == TOK_NUMBER) {
                    write_high_opcode(OP_PUSH_CONST_INT);
                    write_u16((unsigned short)parse_const_int(P->lexer.cur.text));
                    consume(P);
                } else if (P->lexer.cur.kind == TOK_IDENT) {
                    write_high_opcode(OP_PUSH_CONST_STR);
                    write_string_ref(P->lexer.cur.text);
                    consume(P);
                }
            }
            skip_to_semi(P); continue;
        }
        /* import / const / 类型 / export 等顶层语法 */
        if (kw(&t, "import")) { if (parse_import(P)) continue; }
        if (kw(&t, "const"))  { if (parse_const(P))  continue; }
        if (kw(&t, "类型"))   { if (parse_type_def(P)) continue; }
        if (kw(&t, "export")) { if (parse_export(P)) continue; }

        /* 控制流：if / return / while / break / continue */
        if (kw(&t, "如果") || kw(&t, "if")) {
            consume(P);
            if (P->lexer.cur.kind == TOK_LPAR) {
                int pd = 1; consume(P);
                while (pd > 0 && P->lexer.cur.kind != TOK_EOF) {
                    if (P->lexer.cur.kind == TOK_LPAR) pd++;
                    else if (P->lexer.cur.kind == TOK_RPAR) pd--;
                    consume(P);
                }
            }
            write_high_opcode(OP_IF_STMT);
            if (P->lexer.cur.kind == TOK_COLON) consume(P);
            if (P->lexer.cur.kind == TOK_LBRACE) parse_class_body(P);
            else skip_to_semi(P);
            continue;
        }
        if (kw(&t, "返回") || kw(&t, "return")) {
            consume(P);
            if (P->lexer.cur.kind == TOK_SEMI) {
                write_high_opcode(OP_RETURN_STMT); write_byte(0); consume(P);
            } else if (P->lexer.cur.kind == TOK_IDENT) {
                write_high_opcode(OP_RETURN_STMT); write_byte(1);
                write_string_ref(P->lexer.cur.text); consume(P); skip_to_semi(P);
            } else if (P->lexer.cur.kind == TOK_NUMBER) {
                write_high_opcode(OP_RETURN_STMT); write_byte(2);
                write_u16((unsigned short)parse_const_int(P->lexer.cur.text));
                consume(P); skip_to_semi(P);
            } else if (P->lexer.cur.kind == TOK_STRING) {
                write_high_opcode(OP_RETURN_STMT); write_byte(3);
                write_string_ref(P->lexer.cur.text); consume(P); skip_to_semi(P);
            } else skip_to_semi(P);
            continue;
        }
        if (kw(&t, "循环") || kw(&t, "while")) {
            consume(P);
            if (P->lexer.cur.kind == TOK_LPAR) {
                int pd = 1; consume(P);
                while (pd > 0 && P->lexer.cur.kind != TOK_EOF) {
                    if (P->lexer.cur.kind == TOK_LPAR) pd++;
                    else if (P->lexer.cur.kind == TOK_RPAR) pd--;
                    consume(P);
                }
            }
            write_high_opcode(OP_WHILE_STMT);
            if (P->lexer.cur.kind == TOK_COLON) consume(P);
            if (P->lexer.cur.kind == TOK_LBRACE) parse_class_body(P);
            else skip_to_semi(P);
            continue;
        }
        if (kw(&t, "跳出") || kw(&t, "break") || kw(&t, "继续") || kw(&t, "continue")) {
            consume(P); skip_to_semi(P); continue;
        }
        /* 注释 */
        if (t.kind == TOK_HASH || (t.kind == TOK_SLASH && L_is_double_slash(P))) {
            skip_to_semi(P); continue;
        }
        /* 普通标识符：可能是赋值、函数调用、或裸语句 */
        if (t.kind == TOK_IDENT) {
            const char *nm = P->lexer.cur.text;
            consume(P);
            if (P->lexer.cur.kind == TOK_LPAR) { /* 函数调用 */
                int pd = 1; consume(P);
                while (pd > 0 && P->lexer.cur.kind != TOK_EOF) {
                    if (P->lexer.cur.kind == TOK_LPAR) pd++;
                    else if (P->lexer.cur.kind == TOK_RPAR) pd--;
                    consume(P);
                }
                write_high_opcode(OP_FUNC_CALL_STMT); write_string_ref(nm);
                skip_to_semi(P); continue;
            }
            if (P->lexer.cur.kind == TOK_EQ) { /* 赋值 */
                write_high_opcode(OP_ASSIGN_STMT); write_string_ref(nm);
                consume(P);
                if (P->lexer.cur.kind == TOK_NUMBER) {
                    write_high_opcode(OP_PUSH_CONST_INT);
                    write_u16((unsigned short)parse_const_int(P->lexer.cur.text));
                    consume(P);
                } else if (P->lexer.cur.kind == TOK_IDENT) {
                    write_high_opcode(OP_PUSH_CONST_STR);
                    write_string_ref(P->lexer.cur.text); consume(P);
                }
                skip_to_semi(P); continue;
            }
            skip_to_semi(P); continue;
        }
        /* 其他 token：分号、逗号、括号直接推进 */
        if (t.kind == TOK_SEMI || t.kind == TOK_COMMA ||
            t.kind == TOK_COLON || t.kind == TOK_LPAR || t.kind == TOK_RPAR) {
            consume(P); continue;
        }
        /* 无法识别的 token：推进 */
        consume(P);
    }
    flush_highbuf();
}

/* ==================== 函数体解析 ==================== */
static void parse_func_body(Parser *P) {
    P->func_depth++;
    int d = 1;
    while (d > 0 && P->lexer.cur.kind != TOK_EOF) {
        Token t = P->lexer.cur;
        if (t.kind == TOK_LBRACE) { d++; consume(P); continue; }
        if (t.kind == TOK_RBRACE) { d--; consume(P); continue; }

        if (kw(&t, "def")) {
            consume(P); /* "def" → cur 已推进到函数名 */
            if (P->lexer.cur.kind == TOK_IDENT) {
                write_high_opcode(OP_FUNC_DEF);
                write_string_ref(P->lexer.cur.text);
                consume(P); /* 函数名 → cur 已推进到 "(" */
            }
            /* consume 后直接读 cur，不额外 lexer_next（三件套误用修复） */
            if (P->lexer.cur.kind == TOK_LPAR) {
                int pd = 1; consume(P);
                while (pd > 0 && P->lexer.cur.kind != TOK_EOF) {
                    if (P->lexer.cur.kind == TOK_LPAR) pd++;
                    else if (P->lexer.cur.kind == TOK_RPAR) pd--;
                    consume(P);
                }
            }
            if (expect_tok(P, TOK_COLON)) {}
            if (P->lexer.cur.kind == TOK_LBRACE) parse_func_body(P);
            else skip_to_semi(P);
            write_high_opcode(OP_FUNC_END); /* 嵌套 def 必须闭合 OP_FUNC_END */
            continue;
        }
        if (kw(&t, "import")) { if (parse_import(P)) continue; }
        if (kw(&t, "const"))  { if (parse_const(P))  continue; }
        if (kw(&t, "var")) {
            consume(P); /* "var" → cur 已推进到标识符 */
            /* consume 后直接读 cur，不额外 lexer_next（三件套误用修复） */
            if (P->lexer.cur.kind == TOK_IDENT) {
                write_high_opcode(OP_VAR_DECL);
                write_string_ref(P->lexer.cur.text);
                consume(P); /* 标识符 → cur 已推进到 "=" 或 ";" */
            }
            if (expect_tok(P, TOK_EQ)) {
                /* consume(=) 后直接读 cur */
                if (P->lexer.cur.kind == TOK_NUMBER) {
                    write_high_opcode(OP_PUSH_CONST_INT);
                    write_u16((unsigned short)parse_const_int(P->lexer.cur.text));
                    consume(P);
                } else if (P->lexer.cur.kind == TOK_STRING) {
                    write_high_opcode(OP_PUSH_CONST_STR);
                    write_string_ref(P->lexer.cur.text);
                    consume(P);
                } else if (P->lexer.cur.kind == TOK_LBRK) {
                    write_high_opcode(OP_PUSH_CONST_INT); write_u16(0);
                    skip_brace_block_alt(P, TOK_LBRK, TOK_RBRK);
                } else if (P->lexer.cur.kind == TOK_LBRACE) {
                    write_high_opcode(OP_PUSH_CONST_INT); write_u16(0);
                    skip_brace_block(P);
                } else if (P->lexer.cur.kind == TOK_IDENT) {
                    write_high_opcode(OP_PUSH_CONST_STR);
                    write_string_ref(P->lexer.cur.text);
                    consume(P);
                }
            }
            expect_tok(P, TOK_SEMI); P->high_level++; continue;
        }
        if (kw(&t, "返回") || kw(&t, "return")) {
            consume(P); /* "return" → cur 已推进到值/分号 */
            /* consume 后直接读 cur，不额外 lexer_next（三件套误用修复） */
            if (P->lexer.cur.kind == TOK_SEMI) {
                write_high_opcode(OP_RETURN_STMT); write_byte(0);
                consume(P);
            } else if (P->lexer.cur.kind == TOK_IDENT) {
                write_high_opcode(OP_RETURN_STMT); write_byte(1);
                write_string_ref(P->lexer.cur.text);
                consume(P); expect_tok(P, TOK_SEMI);
            } else if (P->lexer.cur.kind == TOK_NUMBER) {
                write_high_opcode(OP_RETURN_STMT); write_byte(2);
                write_u16((unsigned short)parse_const_int(P->lexer.cur.text));
                consume(P); expect_tok(P, TOK_SEMI);
            } else if (P->lexer.cur.kind == TOK_STRING) {
                write_high_opcode(OP_RETURN_STMT); write_byte(3);
                write_string_ref(P->lexer.cur.text);
                consume(P); expect_tok(P, TOK_SEMI);
            }
            P->high_level++; continue;
        }
        if (kw(&t, "如果") || kw(&t, "if")) {
            consume(P); /* "if" → cur 已推进到 "(" */
            /* consume 后直接读 cur，不额外 lexer_next（三件套误用修复） */
            if (expect_tok(P, TOK_LPAR)) { skip_to_semi_or_rpar(P); if (expect_tok(P, TOK_RPAR)) {} }
            if (P->lexer.cur.kind == TOK_LBRACE) { write_high_opcode(OP_IF_STMT); parse_compound_block(P); }
            if (kw(&P->lexer.cur, "否则") || kw(&P->lexer.cur, "else")) {
                consume(P);
                if (P->lexer.cur.kind == TOK_LBRACE) { write_high_opcode(OP_ELSE_STMT); parse_compound_block(P); }
            }
            P->high_level++; continue;
        }
        if (kw(&t, "循环") || kw(&t, "while") || kw(&t, "当")) {
            consume(P);
            if (expect_tok(P, TOK_LPAR)) { skip_to_semi_or_rpar(P); if (expect_tok(P, TOK_RPAR)) {} }
            if (P->lexer.cur.kind == TOK_LBRACE) { write_high_opcode(OP_WHILE_STMT); parse_compound_block(P); }
            P->high_level++; continue;
        }
        if (kw(&t, "跳出") || kw(&t, "break")) {
            consume(P); expect_tok(P, TOK_SEMI);
            write_high_opcode(OP_BREAK_STMT); P->high_level++; continue;
        }
        if (kw(&t, "继续") || kw(&t, "continue")) {
            consume(P); expect_tok(P, TOK_SEMI);
            write_high_opcode(OP_CONTINUE_STMT); P->high_level++; continue;
        }
        if (t.kind == TOK_IDENT) {
            const char *nm = t.text;
            consume(P); /* 标识符 → cur 已推进到 "(" 或 "=" 或 ";" */
            /* consume 后直接读 cur，不额外 lexer_next（三件套误用修复） */
            if (P->lexer.cur.kind == TOK_LPAR) {
                write_high_opcode(OP_FUNC_CALL_STMT);
                write_string_ref(nm);
                int pd = 1, argc = 0;
                consume(P);
                while (pd > 0 && P->lexer.cur.kind != TOK_EOF) {
                    if (P->lexer.cur.kind == TOK_LPAR) pd++;
                    else if (P->lexer.cur.kind == TOK_RPAR) pd--;
                    else if (P->lexer.cur.kind == TOK_COMMA) argc++;
                    consume(P);
                }
                write_u16((unsigned short)argc);
                expect_tok(P, TOK_SEMI); P->high_level++; continue;
            }
            if (P->lexer.cur.kind == TOK_EQ) {
                write_high_opcode(OP_ASSIGN_STMT);
                write_string_ref(nm);
                consume(P); /* = → cur 已推进到值 */
                if (P->lexer.cur.kind == TOK_NUMBER) {
                    write_high_opcode(OP_PUSH_CONST_INT);
                    write_u16((unsigned short)parse_const_int(P->lexer.cur.text));
                    consume(P);
                } else if (P->lexer.cur.kind == TOK_IDENT) {
                    write_high_opcode(OP_PUSH_CONST_STR);
                    write_string_ref(P->lexer.cur.text);
                    consume(P);
                }
                expect_tok(P, TOK_SEMI); P->high_level++; continue;
            }
            expect_tok(P, TOK_SEMI); continue;
        }
        skip_to_semi(P); continue;
    }
    flush_highbuf();
    P->func_depth--;
}

/* ==================== def 函数解析（顶层） ==================== */
static int parse_def(Parser *P) {
    consume(P); /* def */
    lexer_skip_ws(&P->lexer);
    if (P->lexer.cur.kind != TOK_IDENT) return 0;
    const char *fname = P->lexer.cur.text;
    write_opcode(OP_FUNC_DEF);
    write_string_ref(fname);
    consume(P); /* 函数名 */
    lexer_skip_ws(&P->lexer);
    int param_count = 0;
    if (P->lexer.cur.kind == TOK_LPAR) {
        consume(P); /* ( */
        while (P->lexer.cur.kind != TOK_EOF && P->lexer.cur.kind != TOK_RPAR) {
            if (P->lexer.cur.kind == TOK_IDENT) {
                write_high_byte(param_count);
                write_string_ref(P->lexer.cur.text);
                param_count++;
                consume(P);
            } else consume(P);
            if (expect_tok(P, TOK_COLON)) { lexer_skip_ws(&P->lexer); if (P->lexer.cur.kind == TOK_IDENT) consume(P); }
            if (expect_tok(P, TOK_COMMA)) {}
        }
        expect_tok(P, TOK_RPAR); /* ) */
    }
    /* 接受 def f() { ... } 和 def f() : { ... } 两种写法 */
    lexer_skip_ws(&P->lexer);
    if (expect_tok(P, TOK_COLON)) { lexer_skip_ws(&P->lexer); }
    write_u16((unsigned short)param_count);
    flush_highbuf();
    if (P->lexer.cur.kind == TOK_LBRACE) {
        write_high_opcode(BC_FUNC_BODY);
        parse_func_body(P);
        write_high_opcode(BC_FUNC_END);
        flush_highbuf();
    } else {
        skip_to_semi(P);
        write_high_opcode(BC_FUNC_BODY); write_high_opcode(BC_FUNC_END);
        flush_highbuf();
    }
    write_opcode(OP_FUNC_END);
    P->high_level++; return 1;
}

/* ==================== export 解析 ==================== */
static int parse_export(Parser *P) {
    consume(P); /* 消耗 "export"，cur 已推进到导出标识符 */
    /* consume 后直接读 cur，不额外 lexer_next（避免跳过标识符） */
    while (P->lexer.cur.kind == TOK_IDENT) {
        const char *sname = P->lexer.cur.text;
        write_opcode(OP_EXPORT_SYM); write_string_ref(sname);
        consume(P);
        if (expect_tok(P, TOK_SEMI)) break;
        if (expect_tok(P, TOK_COMMA)) {
            /* 跳过逗号后的空白，cur 已推进到下一个标识符 */
        }
    }
    P->high_level++; return 1;
}

/* ==================== 顶层语句调度器 ==================== */
static int parse_top_statement(Parser *P) {
    Token t = P->lexer.cur;
    if (t.kind == TOK_EOF) return 0;
    if (t.kind == TOK_HASH || (t.kind == TOK_SLASH && L_is_double_slash(P))) { skip_to_semi(P); return 1; }
    if (kw(&t, "import")) return parse_import(P);
    if (kw(&t, "const"))  return parse_const(P);
    if (kw(&t, "类型"))   return parse_type_def(P);
    if (kw(&t, "def") || kw(&t, "函数")) return parse_def(P);
    if (kw(&t, "export")) return parse_export(P);
    if (parse_quantum_instruction(P)) return 1;
    if (kw(&t, "var")) {
        consume(P); /* 消耗 "var"，cur 已推进到标识符 */
        /* consume 后直接读 cur，不额外 lexer_next */
        if (P->lexer.cur.kind == TOK_IDENT) {
            write_high_opcode(OP_VAR_DECL);
            write_string_ref(P->lexer.cur.text);
            consume(P);
        }
        if (expect_tok(P, TOK_EQ)) {
            if (P->lexer.cur.kind == TOK_NUMBER) {
                write_high_opcode(OP_PUSH_CONST_INT);
                write_u16((unsigned short)parse_const_int(P->lexer.cur.text));
                consume(P);
            } else if (P->lexer.cur.kind == TOK_STRING) {
                write_high_opcode(OP_PUSH_CONST_STR);
                write_string_ref(P->lexer.cur.text);
                consume(P);
            } else if (P->lexer.cur.kind == TOK_LBRK) {
                write_high_opcode(OP_PUSH_CONST_INT); write_u16(0);
                skip_brace_block_alt(P, TOK_LBRK, TOK_RBRK);
            } else if (P->lexer.cur.kind == TOK_LBRACE) {
                write_high_opcode(OP_PUSH_CONST_INT); write_u16(0);
                skip_brace_block(P);
            } else if (P->lexer.cur.kind == TOK_IDENT) {
                write_high_opcode(OP_PUSH_CONST_STR);
                write_string_ref(P->lexer.cur.text);
                consume(P);
            } else if (kw(&P->lexer.cur, "null")) {
                write_high_opcode(OP_PUSH_CONST_INT); write_u16(0);
                consume(P);
            }
        }
        flush_highbuf(); expect_tok(P, TOK_SEMI); P->high_level++; return 1;
    }
    /* 顶层 if / return / while / break / continue 控制流 */
    if (kw(&t, "如果") || kw(&t, "if")) {
        consume(P); /* "if" → cur 已推进到 "(" */
        if (expect_tok(P, TOK_LPAR)) { skip_to_semi_or_rpar(P); if (expect_tok(P, TOK_RPAR)) {} }
        if (expect_tok(P, TOK_LBRACE)) { write_high_opcode(OP_IF_STMT); parse_compound_block(P); }
        if (kw(&P->lexer.cur, "否则") || kw(&P->lexer.cur, "else")) {
            consume(P);
            if (expect_tok(P, TOK_LBRACE)) { write_high_opcode(OP_ELSE_STMT); parse_compound_block(P); }
        }
        flush_highbuf(); P->high_level++; return 1;
    }
    if (kw(&t, "返回") || kw(&t, "return")) {
        consume(P); /* "return" → cur 已推进到值/分号 */
        if (P->lexer.cur.kind == TOK_SEMI) {
            write_high_opcode(OP_RETURN_STMT); write_byte(0);
            consume(P);
        } else if (P->lexer.cur.kind == TOK_IDENT) {
            write_high_opcode(OP_RETURN_STMT); write_byte(1);
            write_string_ref(P->lexer.cur.text);
            consume(P); expect_tok(P, TOK_SEMI);
        } else if (P->lexer.cur.kind == TOK_NUMBER) {
            write_high_opcode(OP_RETURN_STMT); write_byte(2);
            write_u16((unsigned short)parse_const_int(P->lexer.cur.text));
            consume(P); expect_tok(P, TOK_SEMI);
        } else if (P->lexer.cur.kind == TOK_STRING) {
            write_high_opcode(OP_RETURN_STMT); write_byte(3);
            write_string_ref(P->lexer.cur.text);
            consume(P); expect_tok(P, TOK_SEMI);
        }
        flush_highbuf(); P->high_level++; return 1;
    }
    if (kw(&t, "循环") || kw(&t, "while") || kw(&t, "当")) {
        consume(P);
        if (expect_tok(P, TOK_LPAR)) { skip_to_semi_or_rpar(P); if (expect_tok(P, TOK_RPAR)) {} }
        if (expect_tok(P, TOK_LBRACE)) { write_high_opcode(OP_WHILE_STMT); parse_compound_block(P); }
        flush_highbuf(); P->high_level++; return 1;
    }
    if (kw(&t, "跳出") || kw(&t, "break")) {
        consume(P); expect_tok(P, TOK_SEMI);
        write_high_opcode(OP_BREAK_STMT); P->high_level++; return 1;
    }
    if (kw(&t, "继续") || kw(&t, "continue")) {
        consume(P); expect_tok(P, TOK_SEMI);
        write_high_opcode(OP_CONTINUE_STMT); P->high_level++; return 1;
    }
    skip_to_semi(P); return 1;
}

/* ==================== 主编译函数 ==================== */
typedef struct {
    int total_lines, quantum_lines, high_level_lines;
    int functions, types, imports, const_defs, exports;
} CompileStats;

static int compile_file_stage2(const char *input_path, const char *output_path) {
    FILE *fin = fopen(input_path, "r");
    if (!fin) { fprintf(stderr, "[QCL2] 无法打开: %s\n", input_path); return -1; }
    fseek(fin, 0, SEEK_END); long fsize = ftell(fin); fseek(fin, 0, SEEK_SET);
    char *src = (char *)malloc(fsize + 1);
    if (!src) { fclose(fin); return -1; }
    long nread = fread(src, 1, fsize, fin);
    src[nread] = '\0';
    fclose(fin);

    fprintf(stdout, "[QCL2] 编译: %s\n", input_path);
    fprintf(stdout, "[QCL2] 输出: %s\n", output_path);

    g_bc_pos = 0; g_highbuf_pos = 0; g_strpool_pos = 0;
    memset(g_bytecode, 0, sizeof(g_bytecode));
    memset(g_highbuf, 0, sizeof(g_highbuf));
    memset(g_strpool, 0, sizeof(g_strpool));

    CompileStats stats = {0};

    Parser P;
    memset(&P, 0, sizeof(P));
    P.lexer.src = src; P.lexer.len = (int)nread;
    P.lexer.line = 1; P.lexer.col = 1;
    lexer_next(&P.lexer);

    /* 首字节 0x14 */
    write_byte(BC_MAGIC);

    while (P.lexer.cur.kind != TOK_EOF) {
        /* 跳过空白（含换行） */
        lexer_skip_ws(&P.lexer);
        if (P.lexer.cur.kind == TOK_EOF) break;
        /* 如果跳过空白后仍是TOK_ERR（如孤立换行），再跳过 */
        while (P.lexer.cur.kind == TOK_ERR && P.lexer.pos < P.lexer.len &&
               P.lexer.src[P.lexer.pos] == '\n') {
            P.lexer.pos++; P.lexer.line++; P.lexer.col = 1;
            lexer_next(&P.lexer);
        }
        if (P.lexer.cur.kind == TOK_EOF) break;
        Token cur = P.lexer.cur;
        fprintf(stderr, "[main] cur=%s kind=%d line=%d\n", cur.text, cur.kind, P.lexer.line);
        /* 跳过 # 注释（单行）和 // 注释 */
        if (cur.kind == TOK_HASH) {
            skip_to_semi(&P); continue;
        }
        if (P.lexer.pos + 1 < P.lexer.len && P.lexer.src[P.lexer.pos] == '/' && P.lexer.src[P.lexer.pos+1] == '/') {
            /* 注：lexer_next 已处理 // 注释，此行通常不会到达 */
            consume(&P); continue;
        }
        if (parse_quantum_instruction(&P)) { stats.quantum_lines++; continue; }
        if (kw(&cur, "import")) {
            if (parse_import(&P)) { stats.imports++; stats.high_level_lines++; continue; }
        }
        if (kw(&cur, "const")) {
            if (parse_const(&P)) { stats.const_defs++; stats.high_level_lines++; continue; }
        }
        if (kw(&cur, "类型")) {
            if (parse_type_def(&P)) { stats.types++; stats.high_level_lines++; continue; }
        }
        if (kw(&cur, "def") || kw(&cur, "函数")) {
            if (parse_def(&P)) { stats.functions++; stats.high_level_lines++; continue; }
        }
        /* class / quantum_class / enum 类型定义（跳过整个体，emit OP_TYPE_DEF + 类型名 + OP_TYPE_END）
           注意：此分支在 export 之前，以处理 "export class Foo { ... }" 语法 */
        if (kw(&cur, "class") || kw(&cur, "quantum_class") || kw(&cur, "enum")) {
            consume(&P); /* 消耗 class / quantum_class，cur 推进到类名 */
            if (P.lexer.cur.kind == TOK_IDENT) {
                write_opcode(OP_TYPE_DEF); write_string_ref(P.lexer.cur.text);
                consume(&P);
            }
            if (P.lexer.cur.kind == TOK_LBRACE) {
                parse_class_body(&P); /* 递归解析 class 体内的方法 */
            } else {
                skip_to_semi(&P);
            }
            write_opcode(OP_TYPE_END);
            flush_highbuf();
            stats.types++; stats.high_level_lines++;
            continue;
        }
        if (kw(&cur, "export")) {
            if (parse_export(&P)) { stats.exports++; stats.high_level_lines++; continue; }
        }
        /* export class / export enum 的 class 关键字已消耗在 parse_export 中，
           若 parse_export 失败且下一个 token 是 class/enum，作为类型定义处理 */
        if (kw(&cur, "class") || kw(&cur, "quantum_class") || kw(&cur, "enum")) {
            consume(&P); /* 消耗 class / quantum_class，cur 推进到类名 */
            if (P.lexer.cur.kind == TOK_IDENT) {
                write_opcode(OP_TYPE_DEF); write_string_ref(P.lexer.cur.text);
                consume(&P);
            }
            if (P.lexer.cur.kind == TOK_LBRACE) {
                parse_class_body(&P); /* 递归解析 class 体内的方法 */
            } else {
                skip_to_semi(&P);
            }
            write_opcode(OP_TYPE_END);
            flush_highbuf();
            stats.types++; stats.high_level_lines++;
            continue;
        }
        if (kw(&cur, "var")) {
            parse_top_statement(&P); stats.high_level_lines++; continue;
        }
        if (parse_top_statement(&P)) continue;
        consume(&P);
    }

    if (g_bc_pos <= 1 || g_bytecode[g_bc_pos - 1] != OP_STOP)
        write_opcode(OP_STOP);

    FILE *fout = fopen(output_path, "wb");
    if (!fout) { fprintf(stderr, "[QCL2] 无法创建: %s\n", output_path); free(src); return -1; }
    fwrite(g_bytecode, 1, g_bc_pos, fout);
    /* 追加 string pool 长度（u16）+ 内容，供 qvm_bootstrap 区分代码/字符串区 */
    unsigned short sp_len = (unsigned short)g_strpool_pos;
    fwrite(&sp_len, 2, 1, fout);
    if (g_strpool_pos > 0) fwrite(g_strpool, 1, g_strpool_pos, fout);
    fclose(fout);

    stats.total_lines = stats.quantum_lines + stats.high_level_lines;
    fprintf(stdout, "[QCL2] 编译完成: %d 字节(代码 %d + sp_len 2 + string_pool %d), 首字节 0x%02X\n",
            g_bc_pos + 2 + (g_strpool_pos > 0 ? g_strpool_pos : 0), g_bc_pos, g_strpool_pos, g_bytecode[0]);
    fprintf(stdout, "[QCL2] 量子指令=%d 高级语法=%d 函数=%d 类型=%d 导入=%d 常量=%d 导出=%d\n",
            stats.quantum_lines, stats.high_level_lines, stats.functions,
            stats.types, stats.imports, stats.const_defs, stats.exports);
    free(src);
    return 0;
}

/* ==================== 主函数 ==================== */
int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "用法: %s <input.qentl> [output.qbc]\n", argv[0]);
        fprintf(stderr, "\nQCL引导器 Stage 2 编译器\n");
        fprintf(stderr, "  量子指令: init, H, X, Y, Z, T, S, CNOT, MEASURE, PRINT, STOP, EXIT\n");
        fprintf(stderr, "  高级语法: import, const, def, 类型, var, export\n");
        fprintf(stderr, "  控制流:   如果/否则, 循环, 跳出, 继续, 返回\n");
        fprintf(stderr, "  字节码首字节: 0x14\n");
        return 1;
    }
    const char *input  = argv[1];
    const char *output = (argc >= 3) ? argv[2] : NULL;
    if (!output) {
        size_t nlen = strlen(input) + 8;
        char *tmp = (char *)malloc(nlen);
        if (!tmp) { fprintf(stderr, "[QCL2] 内存不足\\n"); return -1; }
        strcpy(tmp, input);
        char *ext = strstr(tmp, ".qentl");
        if (ext) { *ext = '\0'; strcat(tmp, ".qbc"); }
        output = tmp;
        /* 输出路径是栈分配的，用完释放 */
        int rc = compile_file_stage2(input, output);
        free(tmp);
        return rc;
    }
    srand((unsigned int)time(NULL));
    return compile_file_stage2(input, output);
}
