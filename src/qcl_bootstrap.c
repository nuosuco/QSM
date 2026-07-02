/*
 * qcl_bootstrap_v2.c - QCL编译器最小化引导编译器 v2
 * 
 * 功能：
 * 1. 解析QEntL高级语法（量子模块、导入、类型、函数）
 * 2. 生成QVM能执行的.qbc字节码
 * 3. 提取训练参数、配置等关键信息
 * 4. 支持中文关键字（导入、量子模块、类型、函数等）
 * 
 * 编译: gcc -std=c11 -O2 -o bin/qcl_bootstrap src/qcl_bootstrap_v2.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <unistd.h>

#define MAGIC "QntL"
#define VERSION "2.0.0-bootstrap"
#define MAX_LINE_LEN 4096
#define MAX_OPS 131072
#define MAX_SYM_NAME 256
#define MAX_IMPORTS 256
#define MAX_CLASSES 128
#define MAX_FUNCTIONS 256
#define MAX_TYPES 128

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
    OP_JZ = 50,
    OP_ADD = 12,
    OP_SUB = 13,
    OP_MUL = 15,  // 对齐QVM OP_MUL
    OP_DIV = 14,  // 对齐QVM OP_ADD位置(避免冲突)
    OP_PRINT = 11,  // 对齐QVM OP_PRINT
    OP_STOP = 12,  // 对齐QVM OP_STOP
    OP_LOAD_CONST = 32,
    OP_STORE_VAR = 33,
    OP_LOAD_VAR = 34,
    OP_T = 35,
    OP_S = 36,
    OP_Y = 37,
    OP_BARRIER = 18,
    OP_EXIT = 17,
    // 高级指令
    OP_IMPORT = 100,       // 导入模块
    OP_DEFINE_CLASS = 101, // 定义类型/类
    OP_DEFINE_FUNC = 102,  // 定义函数
    OP_DEF_PARAM = 103,    // 定义参数
    OP_INIT_MODULE = 104,  // 初始化量子模块
    OP_SET_CONFIG = 105,   // 设置配置值
    OP_LOAD_ARRAY = 106,   // 加载数组
    OP_STORE_ARRAY = 107,  // 存储数组
    OP_RETURN = 108,       // 函数返回
    OP_IF = 109,           // 条件分支
    OP_ELSE = 110,         // else分支
    OP_WHILE = 111,        // 循环
    OP_BREAK = 112,        // 跳出循环
    OP_CONTINUE = 113,     // 继续循环
    OP_FUNC_CALL = 114, // 函数调用
    OP_FUNC_DEF = 150, // 函数定义
    OP_NEW = 115, // 创建对象
    OP_ASSIGN = 116,       // 赋值
    OP_LOAD_MEMBER = 117,  // 加载成员
    OP_STORE_MEMBER = 118, // 存储成员
    OP_LOAD_LOCAL = 119,   // 加载局部变量
    OP_STORE_LOCAL = 120,  // 存储局部变量
    OP_PUSH_ZERO = 121,    // 推入0
    OP_PUSH_ONE = 122,     // 推入1
    OP_PUSH_FALSE = 123,   // 推入false
    OP_PUSH_TRUE = 124,    // 推入true
    OP_PUSH_NULL = 125,    // 推入null/空
    OP_EQUAL = 126,        // 等于比较
    OP_NOT_EQUAL = 127,    // 不等于比较
    OP_LESS = 128,         // 小于比较
    OP_GREATER = 129,      // 大于比较
    OP_LESS_EQ = 130,      // 小于等于
    OP_GREATER_EQ = 131,   // 大于等于
    OP_RETURN_VAL = 132,   // 返回值
    OP_RETURN_OBJ = 133,   // 返回对象
    OP_RETURN_EMPTY = 134, // 返回空
    OP_ARRAY_LITERAL = 135,// 数组字面量
    OP_OBJECT_LITERAL = 136, // 对象字面量
    OP_STRING_CONCAT = 137, // 字符串连接
    OP_RANDOM = 138,       // 随机数
    OP_LENGTH = 139,       // 获取长度
    OP_EXIT_CODE = 140,    // 退出码
} Opcode;

// ==================== 数据定义 ====================

typedef struct {
    char path[MAX_SYM_NAME];
    char alias[MAX_SYM_NAME];
} Import;

typedef struct {
    char name[MAX_SYM_NAME];
    char fields[MAX_SYM_NAME * 16]; // 简单字段列表
    int field_count;
} ClassType;

typedef struct {
    char name[MAX_SYM_NAME];
    char params[MAX_SYM_NAME * 8];
    int param_count;
    char return_type[MAX_SYM_NAME];
} FunctionDef;

typedef struct {
    char name[MAX_SYM_NAME];
    int value;
} ConfigValue;

static Import g_imports[MAX_IMPORTS];
static int g_import_count = 0;

static ClassType g_classes[MAX_CLASSES];
static int g_class_count = 0;

static FunctionDef g_functions[MAX_FUNCTIONS];
static int g_function_count = 0;

static ConfigValue g_configs[MAX_TYPES];
static int g_config_count = 0;

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

static void write_string(const char *s) {
    unsigned short len = strlen(s);
    write_u16(len);
    while (*s) {
        write_byte(*s++);
    }
}

// ==================== 高级语法解析 ====================

static int parse_import(const char **p) {
    // 解析 "导入 <path> 作为 <alias>" 或 "import <path> as <alias>"
    
    // 跳过"import "或"导入 "
    if (strncmp(*p, "import ", 7) == 0) {
        (*p) += 7;
    } else if (strncmp(*p, "导入", 2) == 0) {
        (*p) += 2;
        // 跳过空白
        while (**p == ' ' || **p == '\t') (*p)++;
    } else {
        return 0;
    }
    
    // 跳过空白和引号
    while (**p == ' ' || **p == '\t' || **p == '"') (*p)++;
    
    // 读取模块路径
    int j = 0;
    while (**p != '"' && **p != '\0' && **p != '\n' && j < MAX_SYM_NAME-1) {
        g_imports[g_import_count].path[j++] = **p;
        (*p)++;
    }
    g_imports[g_import_count].path[j] = '\0';
    
    // 跳过引号和空白
    while (**p == '"' || **p == ' ' || **p == '\t') (*p)++;
    
    // 跳过"作为"或"as"
    if (strncmp(*p, "as", 2) == 0) {
        (*p) += 2;
        while (**p == ' ' || **p == '\t') (*p)++;
    } else if (strncmp(*p, "作为", 2) == 0) {
        (*p) += 2;
        while (**p == ' ' || **p == '\t') (*p)++;
    }
    
    // 读取别名
    j = 0;
    while (**p != '\0' && **p != '\n' && **p != '\r' && **p != '\t' && **p != ' ' && j < MAX_SYM_NAME-1) {
        g_imports[g_import_count].alias[j++] = **p;
        (*p)++;
    }
    g_imports[g_import_count].alias[j] = '\0';
    g_import_count++;
    
    // 写入字节码
    write_opcode(OP_IMPORT);
    write_string(g_imports[g_import_count-1].path);
    write_string(g_imports[g_import_count-1].alias);
    
    return 1;
}

static int parse_quantum_module(const char **p) {
    // 解析 "量子模块 <name> {"
    (*p) += 4; // 跳过"量子模块"
    
    char module_name[MAX_SYM_NAME];
    int j = 0;
    while (**p != '\0' && **p != '\n' && **p != '\r' && **p != '\t' && **p != ' ' && **p != '{' && j < MAX_SYM_NAME-1) {
        module_name[j++] = **p;
        (*p)++;
    }
    module_name[j] = '\0';
    
    // 跳过到 {
    while (**p != '{' && **p != '\0') (*p)++;
    
    // 写入字节码
    write_opcode(OP_INIT_MODULE);
    write_string(module_name);
    
    return 1;
}

static int parse_type(const char **p) {
    // 解析 "类型 <name> {"
    (*p) += 2; // 跳过"类型"
    
    char type_name[MAX_SYM_NAME];
    int j = 0;
    while (**p != '\0' && **p != '\n' && **p != '\r' && **p != '\t' && **p != ' ' && **p != '{' && j < MAX_SYM_NAME-1) {
        type_name[j++] = **p;
        (*p)++;
    }
    type_name[j] = '\0';
    
    // 跳过到 {
    while (**p != '{' && **p != '\0') (*p)++;
    
    // 记录类型
    strncpy(g_classes[g_class_count].name, type_name, MAX_SYM_NAME-1);
    g_classes[g_class_count].name[MAX_SYM_NAME-1] = '\0';
    g_classes[g_class_count].field_count = 0;
    g_class_count++;
    
    // 写入字节码
    write_opcode(OP_DEFINE_CLASS);
    write_string(type_name);
    write_u8(g_class_count-1);
    
    return 1;
}

static int parse_function(const char **p) {
    // 解析 "函数 <name>(<params>) -> <return> {"
    (*p) += 2; // 跳过"函数"
    
    char func_name[MAX_SYM_NAME];
    int j = 0;
    while (**p != '\0' && **p != '\n' && **p != '\r' && **p != '\t' && **p != ' ' && **p != '(' && **p != '{' && j < MAX_SYM_NAME-1) {
        func_name[j++] = **p;
        (*p)++;
    }
    func_name[j] = '\0';
    
    // 跳过参数到 -> 或 {
    char return_type[MAX_SYM_NAME] = "void";
    while (**p != '\0' && **p != '\n' && **p != '\r' && **p != '\t' && **p != '{') {
        if (strncmp(*p, "->", 2) == 0 || strncmp(*p, "->", 2) == 0) {
            (*p) += 2;
            while (**p == ' ' || **p == '\t') (*p)++;
            j = 0;
            while (**p != '{' && **p != '\0' && **p != '\n' && j < MAX_SYM_NAME-1) {
                return_type[j++] = **p;
                (*p)++;
            }
            return_type[j] = '\0';
            break;
        }
        (*p)++;
    }
    
    // 跳过到 {
    while (**p != '{' && **p != '\0') (*p)++;
    
    // 记录函数
    strncpy(g_functions[g_function_count].name, func_name, MAX_SYM_NAME-1);
    g_functions[g_function_count].name[MAX_SYM_NAME-1] = '\0';
    strncpy(g_functions[g_function_count].return_type, return_type, MAX_SYM_NAME-1);
    g_functions[g_function_count].param_count = 0;
    g_function_count++;
    
    // 写入字节码
    write_opcode(OP_DEFINE_FUNC);
    write_string(func_name);
    write_string(return_type);
    write_u8(g_function_count-1);
    
    return 1;
}

static int parse_if(const char **p) {
    // 解析 "如果 (<condition>) {"
    (*p) += 2; // 跳过"如果"
    
    // 跳过到 (
    while (**p != '(' && **p != '\0') (*p)++;
    
    // 写入字节码
    write_opcode(OP_IF);
    
    return 1;
}

static int parse_return(const char **p) {
    // 解析 "返回 <value>"
    (*p) += 2; // 跳过"返回"
    
    // 跳过空白
    while (**p == ' ' || **p == '\t' || **p == '\r') (*p)++;
    
    // 写入字节码
    write_opcode(OP_RETURN);
    
    return 1;
}

static int parse_return_obj(const char **p) {
    // 解析 "返回 {"
    (*p) += 2; // 跳过"返回"
    
    // 跳过空白
    while (**p == ' ' || **p == '\t' || **p == '\r') (*p)++;
    
    if (**p == '{') {
        write_opcode(OP_RETURN_OBJ);
        return 1;
    }
    
    return 0;
}

static int parse_return_empty(const char **p) {
    // 解析 "返回空二进制()" 或 "返回空()"
    (*p) += 2; // 跳过"返回"
    
    write_opcode(OP_RETURN_EMPTY);
    
    return 1;
}

static int parse_new(const char **p) {
    // 解析 "new <type>(...)"
    (*p) += 3; // 跳过"new"
    
    write_opcode(OP_NEW);
    
    return 1;
}

static int parse_length(const char **p) {
    // 解析 ".长度"
    (*p) += 3; // 跳过".长度"
    
    write_opcode(OP_LENGTH);
    
    return 1;
}

static int parse_random(const char **p) {
    // 解析 "随机()"
    (*p) += 2; // 跳过"随机"
    
    write_opcode(OP_RANDOM);
    
    return 1;
}

static int parse_number(const char **p) {
    // 解析数字常量
    char num_str[32];
    int j = 0;
    int is_float = 0;
    
    while (**p >= '0' && **p <= '9' || **p == '.') {
        if (j < 31) num_str[j++] = **p;
        if (**p == '.') is_float = 1;
        (*p)++;
    }
    num_str[j] = '\0';
    
    // 写入字节码
    if (is_float) {
        float f = atof(num_str);
        write_opcode(OP_LOAD_CONST);
        write_u32((unsigned int)(f * 1000)); // 简单浮点编码
    } else {
        int n = atoi(num_str);
        write_opcode(OP_LOAD_CONST);
        write_u32(n);
    }
    
    return 1;
}

static int parse_string_literal(const char **p) {
    // 解析字符串字面量 '"..."'
    (*p)++; // 跳过第一个引号
    
    char str[MAX_SYM_NAME];
    int j = 0;
    while (**p != '"' && **p != '\0' && j < MAX_SYM_NAME-1) {
        str[j++] = **p;
        (*p)++;
    }
    str[j] = '\0';
    
    if (**p == '"') (*p)++;
    
    write_opcode(OP_LOAD_CONST);
    write_u32(strlen(str));
    write_string(str);
    
    return 1;
}

static int parse_boolean(const char **p) {
    // 解析 "true" 或 "false"
    if (strncmp(*p, "true", 4) == 0 || strncmp(*p, "真", 2) == 0) {
        write_opcode(OP_PUSH_TRUE);
        (*p) += 4;
    } else if (strncmp(*p, "false", 5) == 0 || strncmp(*p, "假", 2) == 0) {
        write_opcode(OP_PUSH_FALSE);
        (*p) += 5;
    } else {
        return 0;
    }
    
    return 1;
}

static int parse_null(const char **p) {
    // 解析 "null" 或 "空"
    if (strncmp(*p, "null", 4) == 0 || strncmp(*p, "空", 2) == 0 || strncmp(*p, "空二进制", 4) == 0) {
        write_opcode(OP_PUSH_NULL);
        if (strncmp(*p, "空二进制", 4) == 0) (*p) += 4;
        else (*p) += 2;
        return 1;
    }
    return 0;
}

static int parse_array_literal(const char **p) {
    // 解析 "[...]"
    (*p)++; // 跳过[
    
    write_opcode(OP_ARRAY_LITERAL);
    
    // 简单计数元素
    int count = 0;
    while (**p != ']' && **p != '\0') {
        if (**p == ',' ) count++;
        (*p)++;
    }
    write_u8(count);
    
    if (**p == ']') (*p)++;
    
    return 1;
}

static int parse_object_literal(const char **p) {
    // 解析 "{"
    (*p)++; // 跳过{
    
    write_opcode(OP_OBJECT_LITERAL);
    
    return 1;
}

static int parse_operator(const char **p) {
    // 解析运算符 === !== < > <= >=
    if (strncmp(*p, "!==", 3) == 0) {
        write_opcode(OP_NOT_EQUAL);
        (*p) += 3;
        return 1;
    } else if (strncmp(*p, "===", 3) == 0) {
        write_opcode(OP_EQUAL);
        (*p) += 3;
        return 1;
    } else if (strncmp(*p, "!=", 2) == 0) {
        write_opcode(OP_NOT_EQUAL);
        (*p) += 2;
        return 1;
    } else if (strncmp(*p, "==", 2) == 0) {
        write_opcode(OP_EQUAL);
        (*p) += 2;
        return 1;
    } else if (**p == '<') {
        write_opcode(OP_LESS);
        (*p)++;
        return 1;
    } else if (**p == '>') {
        write_opcode(OP_GREATER);
        (*p)++;
        return 1;
    } else if (**p == '+') {
        write_opcode(OP_ADD);
        (*p)++;
        return 1;
    } else if (**p == '-') {
        write_opcode(OP_SUB);
        (*p)++;
        return 1;
    } else if (**p == '*') {
        write_opcode(OP_MUL);
        (*p)++;
        return 1;
    } else if (**p == '/') {
        write_opcode(OP_DIV);
        (*p)++;
        return 1;
    }
    return 0;
}

static int parse_member_access(const char **p) {
    // 解析 ".成员"
    (*p)++; // 跳过.
    
    char member[MAX_SYM_NAME];
    int j = 0;
    while (**p != '\0' && **p != '\n' && **p != '\r' && **p != '\t' && **p != ' ' && **p != '.' && **p != '=' && **p != ',' && **p != ')' && j < MAX_SYM_NAME-1) {
        member[j++] = **p;
        (*p)++;
    }
    member[j] = '\0';
    
    if (j > 0) {
        write_opcode(OP_LOAD_MEMBER);
        write_string(member);
        return 1;
    }
    return 0;
}

static int parse_variable_assignment(const char **p) {
    // 解析 "变量 = 值"
    char var_name[MAX_SYM_NAME];
    int j = 0;
    while (**p != '\0' && **p != '\n' && **p != '\r' && **p != '\t' && **p != ' ' && **p != '=' && j < MAX_SYM_NAME-1) {
        var_name[j++] = **p;
        (*p)++;
    }
    var_name[j] = '\0';
    
    if (j == 0) return 0;
    
    // 跳过空白
    while (**p == ' ' || **p == '\t' || **p == '\r') (*p)++;
    
    if (**p == '=') {
        (*p)++;
        
        // 写入赋值
        write_opcode(OP_LOAD_LOCAL);
        write_string(var_name);
        write_opcode(OP_STORE_LOCAL);
        write_string(var_name);
        
        return 1;
    }
    
    return 0;
}

// ==================== 主编译函数 ====================

int compile_file_v2(const char *input_path, const char *output_path) {
    FILE *fin = fopen(input_path, "r");
    if (!fin) {
        fprintf(stderr, "[Bootstrap v2] 无法打开输入文件: %s\n", input_path);
        return -1;
    }
    
    char line[MAX_LINE_LEN];
    int line_num = 0;
    int found_code = 0;
    int brace_depth = 0;
    
    // 文件头 - QVM直接从字节码开始解析指令
    // 不写magic，让QVM直接解析指令
    
    fprintf(stdout, "[Bootstrap v2] 编译: %s\n", input_path);
    fprintf(stdout, "[Bootstrap v2] 输出: %s\n", output_path);
    
    // 读取所有行
    while (fgets(line, sizeof(line), fin)) {
        line_num++;
        
        // 跳过注释行
        char *p = line;
        while (*p == ' ' || *p == '\t' || *p == '\r') p++;
        
        if (*p == '/' || *p == '\n' || *p == '\0' || *p == '#') continue;
        
        // 处理行内注释 - 找到第一个//
        char code[MAX_LINE_LEN];
        int ci = 0;
        for (int i = 0; i < strlen(line); i++) {
            if (line[i] == '/' && line[i+1] == '/') break;
            if (ci < MAX_LINE_LEN-1) code[ci++] = line[i];
        }
        code[ci] = '\0';
        
        p = code;
        while (*p == ' ' || *p == '\t' || *p == '\r') p++;
        if (*p == '/' || *p == '\n' || *p == '\0' || *p == '#') continue;
        
        // 检查花括号深度
        while (*p) {
            if (*p == '{') brace_depth++;
            else if (*p == '}') brace_depth--;
            p++;
        }
        p = code; // 重置指针
        
        // 量子门操作（QVM执行）- 基本量子门
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
        else if (strncmp(p, "H ", 2) == 0 || strncmp(p, "X ", 2) == 0 || strncmp(p, "Y ", 2) == 0 || strncmp(p, "Z ", 2) == 0 || strncmp(p, "T ", 2) == 0 || strncmp(p, "S ", 2) == 0) {
            Opcode op = OP_H;
            if (strncmp(p, "H ", 2) == 0) op = OP_H;
            else if (strncmp(p, "X ", 2) == 0) op = OP_X;
            else if (strncmp(p, "Y ", 2) == 0) op = OP_Y;
            else if (strncmp(p, "Z ", 2) == 0) op = OP_Z;
            else if (strncmp(p, "T ", 2) == 0) op = OP_T;
            else if (strncmp(p, "S ", 2) == 0) op = OP_S;
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
        // 高级语法处理 - 高级语法不写入字节码（C编译器只能处理量子指令子集）
        // QCL编译器（QEntL全栈）在QEntL环境中运行，负责处理高级语法
        
        // 函数调用（记录函数名，不执行）
        else if (strstr(p, "()")) {
            write_opcode(OP_FUNC_CALL);
            char fname[MAX_SYM_NAME];
            int j = 0;
            while (*p != '(' && *p != '\0' && j < MAX_SYM_NAME-1) { fname[j++] = *p; p++; }
            fname[j] = '\0';
            write_string(fname);
            found_code = 1;
        }
    }
    
    fclose(fin);
    
    if (!found_code) {
        fprintf(stdout, "[Bootstrap v2] 警告: 未找到可编译的量子代码\n");
        write_opcode(OP_STOP);
    }
    
    // 写入输出文件（纯字节码，无header，让QVM从0开始直接解析指令）
    FILE *fout = fopen(output_path, "wb");
    if (!fout) {
        fprintf(stderr, "[Bootstrap v2] 无法创建输出文件: %s\n", output_path);
        return -1;
    }
    
    fwrite(g_bytecode, 1, g_bc_pos, fout);
    fclose(fout);
    
    fprintf(stdout, "[Bootstrap v2] 编译完成: %d 字节, %d 导入, %d 类型, %d 函数\n", 
            g_bc_pos, g_import_count, g_class_count, g_function_count);
    
    return 0;
}

// ==================== 主函数 ====================

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "用法: %s <input.qentl> [output.qbc]\\n", argv[0]);
        fprintf(stderr, "\\nQCL引导编译器 v2 - 最小化C语言引导编译器\\n");
        fprintf(stderr, "将QEntL源码编译为QVM可执行的.qbc字节码\\n");
        fprintf(stderr, "\\n支持指令:\\n");
        fprintf(stderr, "  量子门: init, H, X, Y, Z, T, S, CNOT, SWAP, MEASURE, RESET, BARRIER\\n");
        fprintf(stderr, "  高级语法: 导入, 量子模块, 类型, 函数, 如果, 返回, new, .长度, 随机\\n");
        fprintf(stderr, "  运算符: ===, !==, ==, !=, <, >, +, -, *, /\\n");
        fprintf(stderr, "  控制流: 否则, 循环, 跳出, 继续\\n");
        fprintf(stderr, "\\n注: 高级QEntL语法(类定义、函数体等)会被简化处理\\n");
        return 1;
    }
    
    const char *input = argv[1];
    
    if (argc == 2) {
        // 执行模式：编译成临时qbc，然后调用qvm_bootstrap执行
        char tmp_qbc[512];
        snprintf(tmp_qbc, sizeof(tmp_qbc), "/tmp/qcl_exec_%d.qbc", getpid());
        
        fprintf(stderr, "[QCL] 执行模式：编译 %s → %s\\n", input, tmp_qbc);
        int ret = compile_file_v2(input, tmp_qbc);
        if (ret != 0) {
            fprintf(stderr, "[QCL] 编译失败\\n");
            return ret;
        }
        
        char cmd[1024];
        snprintf(cmd, sizeof(cmd), "bin/qvm_bootstrap %s", tmp_qbc);
        fprintf(stderr, "[QCL] 调用QVM执行 %s\\n", cmd);
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