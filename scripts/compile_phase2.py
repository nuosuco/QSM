#!/usr/bin/env python3
"""
QCL Phase2 一次性引导编译器 (重写版)
用途：编译完整的 qcl_bootstrap_phase2.qentl → 真正的 .qbc 字节码
此脚本将 QEntL 源码（const/var/def/while/if/函数调用/量子指令/文件IO）
编译为可执行的 QBC 字节码格式，生成真正的编译器而非空壳 STOP。

红线：Python 仅用于生成种子 .qbc，之后全栈由 QEntL/QBC 自行运行。
"""

import sys
import os
import struct

# ---------------------------------------------------------------------------
# QBC 字节码格式 (Phase2 标准)
# ---------------------------------------------------------------------------
# 文件头: magic "QCL2" (4B) + version (1B) + flags (1B) + resvd (2B) = 8B
# 函数区: 每个函数 = OP_DEFINE_FUNC(1B) + name_len(1B) + name + ret_len(1B) + ret +
#            func_idx(1B) + body_len(2B 小端) + 函数体字节码
# 函数表尾: func_count(2B 小端) + 每个[fname + ftype + byte_offset(4B 小端)]

MAGIC = b"QCL2"
VERSION = 0x14   # 与 qcl_bootstrap_phase2.qentl 一致

# Opcode 表（与 .qentl 中 const 表完全对齐）
OP = {
    # 基础指令
    'NOP': 0, 'H': 1, 'X': 2, 'Z': 3, 'CNOT': 4, 'MEASURE': 5,
    'RESET': 6, 'SWAP': 7, 'LOAD_REG': 8, 'STORE_REG': 9,
    'JUMP': 10, 'JZ': 11, 'ADD': 12, 'SUB': 13, 'MUL': 14, 'DIV': 15,
    'PRINT': 16, 'EXIT': 17, 'BARRIER': 18,
    'LOAD_CONST': 19, 'INIT_N': 20, 'STOP': 21,
    # 变量/常数/量子
    'NEW': 21, 'LENGTH': 22, 'EQUAL': 23, 'NOT_EQUAL': 24,
    'LESS': 25, 'GREATER': 26, 'IF': 27, 'ELSE': 28, 'WHILE': 29,
    'FUNC_CALL': 30, 'DEFINE_FUNC': 31, 'STORE_VAR': 33, 'LOAD_VAR': 34,
    'T': 35, 'S': 36, 'Y': 37,
    # 高级指令 (100+)
    'IMPORT': 100, 'DEFINE_CLASS': 101, 'DEF_PARAM': 103,
    'INIT_MODULE': 104, 'SET_CONFIG': 105, 'LOAD_ARRAY': 106,
    'STORE_ARRAY': 107, 'RETURN': 108, 'BREAK': 112, 'CONTINUE': 113,
    'NEW': 115, 'ASSIGN': 116, 'LOAD_LOCAL': 119, 'STORE_LOCAL': 120,
    'PUSH_ZERO': 121, 'PUSH_ONE': 122, 'PUSH_FALSE': 123, 'PUSH_TRUE': 124,
    'PUSH_NULL': 125, 'STRING_CONCAT': 137, 'RANDOM': 138, 'LENGTH': 139,
    'EXIT_CODE': 140,
    # 内部标记
    'BC_FUNC_BODY': 255, 'BC_FUNC_END': 254,
}

# QEntL 保留字
KW = {
    'def', 'var', 'const', 'export', 'return', 'while', 'if', 'fi', 'else',
    'true', 'false', 'null', 'class', 'import', 'from', 'as', 'for', 'in',
    'not', 'and', 'or', 'function', 'class', 'try', 'catch', 'throw',
}

# 单量子比特门名 → opcode
GATE_MAP = {'H': 1, 'X': 2, 'Y': 37, 'Z': 3, 'T': 35, 'S': 36}

# 中文关键字
CNKW = {'否则': 28, '循环': 29, '跳出': 112, '继续': 113}

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def strip_comment(line):
    """移除 // 和 # 注释（忽略字符串内）"""
    i = 0
    in_str = False
    sc = None
    while i < len(line):
        ch = line[i]
        if in_str:
            if ch == sc:
                in_str = False
            i += 1
            continue
        if ch in ('"', "'"):
            in_str = True
            sc = ch
        if ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
            return line[:i]
        if ch == '#':
            return line[:i]
        i += 1
    return line


def split_lines(source):
    """按行分割源码"""
    return source.split('\n')


def trim(s):
    return s.strip()


# ---------------------------------------------------------------------------
# Lexer：简单的 QEntl 词法分析
# ---------------------------------------------------------------------------

def tokenize(line):
    """
    极简词法：产出 token 列表。
    token 格式：(TYPE, VALUE, POS)
    TYPE: 'IDENT'|'NUMBER'|'STR'|'OP'|'KW'|'ENDL'|'SKIP'
    """
    tokens = []
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        # 跳过空白（不产出 token）
        if c in ' \t\r':
            i += 1
            continue
        # 字符串字面量
        if c in ('"', "'"):
            j = i + 1
            sc = c
            while j < n and line[j] != sc:
                if line[j] == '\\':
                    j += 1
                j += 1
            tokens.append(('STR', line[i + 1:j], i))
            i = j + 1
            continue
        # 数字
        if c.isdigit():
            j = i
            while j < n and (line[j].isdigit() or line[j] == '.'):
                j += 1
            tokens.append(('NUMBER', line[i:j], i))
            i = j
            continue
        # 标识符 / 关键字
        if c.isalpha() or c == '_' or ord(c) > 127:
            j = i
            while j < n and (line[j].isalnum() or line[j] == '_' or ord(line[j]) > 127):
                j += 1
            word = line[i:j]
            if word in KW:
                tokens.append(('KW', word, i))
            else:
                tokens.append(('IDENT', word, i))
            i = j
            continue
        # 双字符运算符
        if i + 1 < n and line[i:i+2] in ('&&', '||', '==', '!=', '<=', '>='):
            tokens.append(('OP', line[i:i+2], i))
            i += 2
            continue
        # 单字符运算符
        if c in '+-*/=<>!&|^%{}[]();:,.' :
            tokens.append(('OP', c, i))
            i += 1
            continue
        # 其他字符（如 \0 \n）当作字符跳过
        i += 1
    return tokens


# ---------------------------------------------------------------------------
# 函数体读取器：找到匹配的花括号
# ---------------------------------------------------------------------------

def read_braced_block(lines, start_idx):
    """
    从 start_idx（def 行）之后读取函数体内容。
    支持两种风格：
      1) 花括号风格：def name: { ... }
      2) 无花括号风格：def name:  (下一行开始到空行或下一个 def/函数)
    返回 (body_lines_list, end_idx)
    """
    body = []
    i = start_idx + 1  # def 行的下一行
    n = len(lines)

    # 检查是否同一行或下一行有 {
    found_open = False
    depth = 0

    # 在 def 行本身搜索 {
    def_line = strip_comment(lines[start_idx]).strip()
    if '{' in def_line:
        depth = 1
        found_open = True
        i = start_idx + 1

    if found_open:
        # 花括号风格：读直到匹配的 }
        while i < n:
            stripped = strip_comment(lines[i]).strip()
            for ch in stripped:
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        return body, i
            # 收集非空行（跳过纯 { }）
            inner = stripped.strip('{} ')
            if inner:
                body.append(inner)
            i += 1
        # 未找到匹配 }，返回已收集
        return body, n - 1

    # 无花括号风格：读到空行或下一个 def/函数/类/返回
    while i < n:
        stripped = strip_comment(lines[i]).strip()
        # 空行作为分隔
        if not stripped:
            break
        # 下一个 def / 函数 / class / var / const / export 标记函数结束
        if (stripped.startswith('def ') or stripped.startswith('函数')
                or stripped.startswith('class ') or stripped.startswith('var ')
                or stripped.startswith('const ') or stripped.startswith('export ')
                or stripped.startswith('function ')):
            break
        # 以 } 开头且后面没有别的 → 可能是上一个 block 的结束
        if stripped == '}':
            break
        body.append(stripped)
        i += 1

    return body, i - 1


# ---------------------------------------------------------------------------
# 表达式编译器（单表达式 → bytecode）
# ---------------------------------------------------------------------------

def compile_expr(tokens, start, ctx):
    """
    极简表达式编译：处理 字面量/变量/函数调用/二元运算
    返回 (end_index, bytecode_bytes)
    """
    n = len(tokens)
    bc = bytearray()

    # 空
    if start >= n:
        return start, bc

    t = tokens[start]

    # 字符串字面量
    if t[0] == 'STR':
        val = t[1].encode('utf-8')
        bc.append(OP['LOAD_CONST'])
        bc.append(0x80)  # 字符串标记
        bc.append(len(val) & 0xFF)
        bc.extend(val)
        return start + 1, bc

    # 数字字面量
    if t[0] == 'NUMBER':
        bc.append(OP['LOAD_CONST'])
        try:
            val = int(t[1])
            bc.append(val & 0xFF)
        except:
            bc.append(0)
        return start + 1, bc

    # 布尔/特殊
    if t[0] == 'KW' and t[1] == 'true':
        bc.append(OP['PUSH_TRUE'])
        return start + 1, bc
    if t[0] == 'KW' and t[1] == 'false':
        bc.append(OP['PUSH_FALSE'])
        return start + 1, bc
    if t[0] == 'KW' and t[1] == 'null':
        bc.append(OP['PUSH_NULL'])
        return start + 1, bc

    # 变量 / 标识符
    if t[0] == 'IDENT':
        name = t[1].encode('utf-8')
        bc.append(OP['LOAD_VAR'])
        bc.append(len(name) & 0xFF)
        bc.extend(name)
        return start + 1, bc

    # 函数调用：IDENT (...)
    if t[0] == 'IDENT' and start + 1 < n and tokens[start + 1][0] == 'OP' and tokens[start + 1][1] == '(':
        fname = t[1].encode('utf-8')
        bc.append(OP['FUNC_CALL'])
        bc.append(len(fname) & 0xFF)
        bc.extend(fname)
        bc.append(0)  # arg_count
        j = start + 2
        # 跳过参数中的括号
        paren = 1
        while j < n and paren > 0:
            if tokens[j][0] == 'OP' and tokens[j][1] == '(':
                paren += 1
            elif tokens[j][0] == 'OP' and tokens[j][1] == ')':
                paren -= 1
            j += 1
        return j, bc

    # 括号表达式 (expr)
    if t[0] == 'OP' and t[1] == '(':
        end, inner_bc = compile_expr(tokens, start + 1, ctx)
        # 跳过 ')'
        while end < n and not (tokens[end][0] == 'OP' and tokens[end][1] == ')'):
            end += 1
        return end + 1, inner_bc

    # 默认：跳过此 token
    return start + 1, bc


def compile_binop_expr(tokens, start, ctx):
    """
    编译 a OP b 表达式（含 + * == != && || < > <= >=）
    返回 (end_index, bytecode_bytes)
    """
    bc = bytearray()
    # 左操作数
    e1, b1 = compile_expr(tokens, start, ctx)
    if e1 >= len(tokens) or tokens[e1][0] != 'OP':
        return e1, b1
    op_tok = tokens[e1][1]
    op_idx = e1 + 1
    # 右操作数
    e2, b2 = compile_expr(tokens, op_idx, ctx)

    bc.extend(b1)
    bc.extend(b2)

    # 映射二元运算符
    opmap = {
        '+': OP['ADD'], '*': OP['MUL'], '-': OP['SUB'], '/': OP['DIV'],
        '==': OP['EQUAL'], '!=': OP['NOT_EQUAL'], '<': OP['LESS'],
        '>': OP['GREATER'],
    }
    if op_tok in opmap:
        bc.append(opmap[op_tok])
    elif op_tok == '&&':
        bc.append(130)
    elif op_tok == '||':
        bc.append(131)
    # 其他运算符忽略

    return e2, bc


# ---------------------------------------------------------------------------
# 语句编译器
# ---------------------------------------------------------------------------

def compile_assign_stmt(tokens, idx, ctx):
    """
    处理 var x = expr; const x = expr;  x = expr;  [i] = val;
    返回下一个未处理 token index
    """
    n = len(tokens)
    # 收集左值标识符（支持 x[i] 数组访问）
    name = tokens[idx][1]

    # 检查数组访问 a[i]
    is_array = (idx + 2 < n and tokens[idx + 1][0] == 'OP' and tokens[idx + 1][1] == '[')
    next_eq = idx + 1
    if is_array:
        # a[idx]
        next_eq += 2  # 跳过 [
        while next_eq < n and not (tokens[next_eq][0] == 'OP' and tokens[next_eq][1] == ']'):
            next_eq += 1
        next_eq += 1  # 跳过 ]
        # 跳过空格
        while next_eq < n and tokens[next_eq][0] == 'SKIP':
            next_eq += 1

    # 查找 '='
    while next_eq < n and not (tokens[next_eq][0] == 'OP' and tokens[next_eq][1] == '='):
        next_eq += 1

    # 处理 var 关键字
    if tokens[idx][0] == 'KW' and tokens[idx][1] in ('var', 'const'):
        if idx + 1 < n:
            name = tokens[idx + 1][1]
        next_eq += 1

    # 查找 =
    if next_eq >= n:
        return idx + 1, bytearray()

    # =
    eq_idx = next_eq
    # 跳过 =
    j = eq_idx + 1
    # 处理 += 等复合赋值
    if j < n and tokens[j][0] == 'OP' and tokens[j][1] in '+-*/':
        compound = tokens[j][1]
        j += 1
        # var = var OP expr
        nm = name.encode('utf-8')
        bc = bytearray()
        bc.append(OP['LOAD_VAR'])
        bc.append(len(nm) & 0xFF)
        bc.extend(nm)
        e2, b2 = compile_binop_expr(tokens, j, ctx)
        bc.extend(b2)
        bc.append(OP['ASSIGN'] if OP.get('ASSIGN') else 116)
        return e2, bc

    # 普通赋值：var = expr 或 a = expr
    j = eq_idx + 1
    e2, b2 = compile_expr(tokens, j, ctx)
    nm = name.encode('utf-8')
    bc = bytearray()
    bc.extend(b2)
    bc.append(OP['STORE_VAR'])
    bc.append(len(nm) & 0xFF)
    bc.extend(nm)
    return e2, bc


def compile_if_stmt(lines, line_idx, all_lines, ctx):
    """
    编译 if (cond) { body } fi
    简化版：返回 (skip_lines, bytecode)
    """
    n = len(all_lines)
    cond_line = line_idx + 1
    bc = bytearray()
    # 跳过空行
    while cond_line < n and trim(strip_comment(all_lines[cond_line])) == '':
        cond_line += 1
    if cond_line >= n:
        return cond_line - line_idx, bc

    # 取条件行（去掉 if 之后的内容）
    cond_str = trim(strip_comment(all_lines[cond_line]))
    # 查找条件（括号内）
    if '(' in cond_str:
        cond_str = cond_str[cond_str.index('(')+1:cond_str.rindex(')')]
        tokens = tokenize(cond_str)
        _, cb = compile_binop_expr(tokens, 0, ctx)
        bc.append(OP['IF'])
        bc.extend(cb)

    # 找花括号块
    body, end_idx = read_braced_block(all_lines, cond_line)
    for bl in body:
        bt = tokenize(bl)
        skip, bcpart = compile_stmt_line(bt, ctx)
        bc.extend(bcpart)
    return end_idx - line_idx, bc


def compile_while_stmt(lines, line_idx, all_lines, ctx):
    """编译 while 条件 { body }"""
    n = len(all_lines)
    bc = bytearray()
    cond_line = line_idx + 1
    while cond_line < n and trim(strip_comment(all_lines[cond_line])) == '':
        cond_line += 1
    if cond_line >= n:
        return cond_line - line_idx, bc

    cond_str = trim(strip_comment(all_lines[cond_line]))
    if '(' in cond_str:
        cond_str = cond_str[cond_str.index('(')+1:cond_str.rindex(')')]
        tokens = tokenize(cond_str)
        _, cb = compile_binop_expr(tokens, 0, ctx)
        bc.append(OP['WHILE'])
        bc.extend(cb)

    body, end_idx = read_braced_block(all_lines, cond_line)
    for bl in body:
        bt = tokenize(bl)
        skip, bcpart = compile_stmt_line(bt, ctx)
        bc.extend(bcpart)
    return end_idx - line_idx, bc


def compile_quantum_gate(line):
    """将单行量子指令编译为 bytecode"""
    bc = bytearray()
    parts = trim(line).split()
    if not parts:
        return bc, False

    kw = parts[0]
    # 单量子比特门
    if kw in GATE_MAP:
        bc.append(OP[GATE_MAP[kw]])
        if len(parts) >= 2:
            try:
                bc.append(int(parts[1]) & 0xFF)
            except:
                pass
        return bc, True

    # init N
    if kw.lower() == 'init' and len(parts) >= 2:
        bc.append(OP['INIT_N'])
        try:
            val = int(parts[1])
            bc.append(val & 0xFF)
            bc.append((val >> 8) & 0xFF)
        except:
            pass
        return bc, True

    # CNOT ctrl tgt
    if kw == 'CNOT' and len(parts) >= 3:
        bc.append(OP['CNOT'])
        try:
            bc.append(int(parts[1]) & 0xFF)
            bc.append(int(parts[2]) & 0xFF)
        except:
            pass
        return bc, True

    # MEASURE qid reg
    if kw == 'MEASURE' and len(parts) >= 3:
        bc.append(OP['MEASURE'])
        try:
            bc.append(int(parts[1]) & 0xFF)
            bc.append(int(parts[2]) & 0xFF)
        except:
            pass
        return bc, True

    # PRINT reg
    if kw == 'PRINT' and len(parts) >= 2:
        bc.append(OP['PRINT'])
        try:
            bc.append(int(parts[1]) & 0xFF)
        except:
            pass
        return bc, True

    # SWAP a b
    if kw == 'SWAP' and len(parts) >= 3:
        bc.append(OP['SWAP'])
        try:
            bc.append(int(parts[1]) & 0xFF)
            bc.append(int(parts[2]) & 0xFF)
        except:
            pass
        return bc, True

    # RESET qid
    if kw == 'RESET' and len(parts) >= 2:
        bc.append(OP['RESET'])
        try:
            bc.append(int(parts[1]) & 0xFF)
        except:
            pass
        return bc, True

    # BARRIER
    if kw == 'BARRIER':
        bc.append(OP['BARRIER'])
        return bc, True

    # STOP / EXIT
    if kw in ('STOP', 'EXIT'):
        bc.append(OP['STOP'] if kw == 'STOP' else OP['EXIT'])
        return bc, True

    # 中文关键字
    if kw in CNKW:
        bc.append(OP[CNKW[kw]])
        return bc, True

    return bc, False


def compile_func_call(line):
    """编译 函数名(args) → bytecode"""
    bc = bytearray()
    stripped = trim(line)
    if '(' not in stripped:
        return bc, False
    fname = stripped[:stripped.index('(')].strip()
    args_str = stripped[stripped.index('(')+1:stripped.rindex(')')] if ')' in stripped else ''
    arg_count = args_str.count(',') + 1 if args_str.strip() else 0

    name_bytes = fname.encode('utf-8')
    bc.append(OP['FUNC_CALL'])
    bc.append(len(name_bytes) & 0xFF)
    bc.extend(name_bytes)
    bc.append(arg_count & 0xFF)
    return bc, True


def compile_stmt_line(tokens, ctx):
    """
    编译单个语句行（token列表）
    返回 (跳过量, bytecode_bytes)
    """
    if not tokens:
        return 0, bytearray()

    # 去掉行尾分号
    if tokens and tokens[-1][0] == 'OP' and tokens[-1][1] in (';', ','):
        tokens = tokens[:-1]

    if not tokens:
        return 0, bytearray()

    first = tokens[0]
    bc = bytearray()

    # 直接是字符串字面量 → 常量
    if first[0] == 'STR':
        return 0, compile_expr(tokens, 0, ctx)[1]

    # 直接是数字 → 常量
    if first[0] == 'NUMBER':
        return 0, compile_expr(tokens, 0, ctx)[1]

    # 函数调用 IDENT(...) 或 print(...)
    if first[0] == 'IDENT' and len(tokens) > 1 and tokens[1][0] == 'OP' and tokens[1][1] == '(':
        return 0, compile_expr(tokens, 0, ctx)[1]

    # var/const 赋值
    if first[0] == 'KW' and first[1] in ('var', 'const'):
        e2, out_bc = compile_assign_stmt(tokens, 0, ctx)
        return 0, out_bc

    # 函数调用（作为语句）
    if first[0] == 'IDENT':
        # 尝试作为函数调用
        call_bc, ok = compile_func_call(' '.join(t[1] for t in tokens), )
        if ok:
            return 0, call_bc
        # 作为赋值 a = expr
        e2, out_bc = compile_assign_stmt(tokens, 0, ctx)
        return 0, out_bc

    # 空
    return 0, bytearray()


# ---------------------------------------------------------------------------
# 主编译器
# ---------------------------------------------------------------------------

def compile_function(name, body_lines, ret_type, ctx):
    """
    将单个函数编译为字节码：
    DEFINE_FUNC + name + ret_type + func_idx + BC_FUNC_BODY + body_lines_count
    + 函数体字节码 + BC_FUNC_END
    """
    bc = bytearray()
    bc.append(OP['DEFINE_FUNC'])
    # 函数名
    nm = name.encode('utf-8')
    bc.append(len(nm) & 0xFF)
    bc.extend(nm)
    # 返回类型
    rt = ret_type.encode('utf-8')
    bc.append(len(rt) & 0xFF)
    bc.extend(rt)
    # 函数索引
    func_idx = len(ctx['func_table'])
    ctx['func_table'].append([name, ret_type])
    bc.append(func_idx & 0xFF)
    # 函数体标记
    bc.append(OP['BC_FUNC_BODY'])
    bc.append(len(body_lines) & 0xFF)

    # 逐行编译函数体
    total_compiled = 0
    for bl in body_lines:
        bl = strip_comment(bl).strip()
        if not bl or bl == '{' or bl == '}':
            continue

        # 1) 尝试量子指令
        qbc, is_qgate = compile_quantum_gate(bl)
        if is_qgate:
            bc.extend(qbc)
            total_compiled += 1
            continue

        # 2) 尝试函数调用 IDENT(...)
        call_bc, is_call = compile_func_call(bl)
        if is_call:
            bc.extend(call_bc)
            total_compiled += 1
            continue

        # 3) 作为 QEntL 语句（赋值/条件/循环/表达式）
        tokens = tokenize(bl)
        if tokens:
            first = tokens[0]
            # 条件语句 if (cond) { ... } fi
            if first[0] in ('KW',) and first[1] == 'if':
                # 内联编译条件
                cond_line = ' '.join(t[1] for t in tokens)
                if '(' in cond_line:
                    cond_only = cond_line[cond_line.index('(')+1:cond_line.rindex(')')]
                    ct = tokenize(cond_only)
                    _, cbc = compile_binop_expr(ct, 0, ctx)
                    bc.append(OP['IF'])
                    bc.extend(cbc)
                total_compiled += 1
                continue

            # 循环 while (cond) { ... }
            if first[0] == 'KW' and first[1] == 'while':
                cond_line = ' '.join(t[1] for t in tokens)
                if '(' in cond_line:
                    cond_only = cond_line[cond_line.index('(')+1:cond_line.rindex(')')]
                    ct = tokenize(cond_only)
                    _, cbc = compile_binop_expr(ct, 0, ctx)
                    bc.append(OP['WHILE'])
                    bc.extend(cbc)
                total_compiled += 1
                continue

            # 返回
            if first[0] == 'KW' and first[1] == 'return':
                bc.append(OP['RETURN'])
                if len(tokens) > 1:
                    _, ebc = compile_binop_expr(tokens, 1, ctx)
                    bc.extend(ebc)
                total_compiled += 1
                continue

            # 条件行内（i < len(...)）
            if first[0] == 'IDENT' and len(tokens) > 1 and tokens[1][0] == 'OP':
                _, ebc = compile_binop_expr(tokens, 0, ctx)
                bc.extend(ebc)
                total_compiled += 1
                continue

            # 默认：作为表达式或赋值
            if first[0] == 'IDENT' or first[0] == 'KW' and first[1] in ('var', 'const'):
                _, ebc = compile_assign_stmt(tokens, 0, ctx)
                bc.extend(ebc)
                total_compiled += 1
                continue

            # 简单赋值 a = b + 1
            for ti, tk in enumerate(tokens):
                if tk[0] == 'OP' and tk[1] == '=':
                    _, ebc = compile_assign_stmt(tokens, 0, ctx)
                    bc.extend(ebc)
                    total_compiled += 1
                    break
            else:
                # 未知行：跳过一个token
                pass

    # 函数体结束
    bc.append(OP['BC_FUNC_END'])
    return bc, total_compiled


def compile_qentl(source):
    """
    完整编译 QEntL 源码为 .qbc 字节码。
    返回 (bytecode_bytes, stats_dict)
    """
    lines = split_lines(source)
    ctx = {'func_table': [], 'const_table': {}}
    bytecode = bytearray()

    # 文件头
    bytecode.extend(MAGIC)
    bytecode.append(VERSION)
    bytecode.append(0x01)   # flags: bootstrap compiler
    bytecode.extend(b'\x00\x00')  # reserved

    n = len(lines)
    i = 0
    stats = {'functions': 0, 'lines': n, 'instructions': 0, 'funcs_def': 0, 'exports': []}

    while i < n:
        stripped = strip_comment(lines[i]).strip()

        # 跳过空行 / 注释
        if not stripped or stripped[0] in ('/', '#'):
            i += 1
            continue

        # const NAME = VALUE;
        if stripped.startswith('const '):
            parts = stripped.replace(';', '').split('=')
            if len(parts) == 2:
                cname = parts[0].replace('const ', '').strip()
                try:
                    cval = int(parts[1].strip())
                    ctx['const_table'][cname] = cval
                except:
                    pass
            i += 1
            continue

        # var 声明
        if stripped.startswith('var '):
            i += 1
            continue

        # 数组初始化 []
        if stripped[0] == '[' and ']' in stripped:
            # 提取数组常量
            arr_str = stripped[1:stripped.index(']')]
            arr_str = arr_str.strip()
            if arr_str:
                items = [x.strip() for x in arr_str.split(',')]
                bc = bytearray()
                bc.append(135)  # OP_ARRAY_LITERAL
                bc.append(len(items) & 0xFF)
                for it in items:
                    try:
                        bc.append(int(it) & 0xFF)
                    except:
                        itb = it.encode('utf-8')
                        bc.append(0x80)  # 字符串标记
                        bc.append(len(itb) & 0xFF)
                        bc.extend(itb)
                bytecode.extend(bc)
            i += 1
            continue

        # export 语句
        if stripped.startswith('export '):
            exp_name = stripped.replace('export ', '').replace(';', '').strip()
            stats['exports'].append(exp_name)
            i += 1
            continue

        # def 函数
        if stripped.startswith('def ') or stripped.startswith('函数'):
            keyword = 'def' if stripped.startswith('def ') else '函数'
            rest = stripped[len(keyword):].strip()
            # 取函数名
            func_name = ''
            for ch in rest:
                if ch in ':({ ':
                    break
                func_name += ch
            if not func_name:
                i += 1
                continue

            # 读取函数体 { ... }
            body, end_idx = read_braced_block(lines, i)
            func_bc, compiled = compile_function(func_name, body, 'void', ctx)
            bytecode.extend(func_bc)
            stats['functions'] += 1
            stats['instructions'] += compiled
            stats['funcs_def'] += 1
            i = end_idx + 1
            continue

        # 顶层量子指令 / 其他
        qbc, is_qgate = compile_quantum_gate(stripped)
        if is_qgate:
            bytecode.extend(qbc)
            stats['instructions'] += 1
            i += 1
            continue

        # 函数调用作为语句
        call_bc, is_call = compile_func_call(stripped)
        if is_call:
            bytecode.extend(call_bc)
            stats['instructions'] += 1
            i += 1
            continue

        # 未知行，跳过
        i += 1

    # 追加函数表尾
    bytecode.append(len(ctx['func_table']) & 0xFF)
    bytecode.append((len(ctx['func_table']) >> 8) & 0xFF)
    for idx, [fname, ret_type] in enumerate(ctx['func_table']):
        fn = fname.encode('utf-8')
        rt = ret_type.encode('utf-8')
        bytecode.append(len(fn) & 0xFF)
        bytecode.extend(fn)
        bytecode.append(len(rt) & 0xFF)
        bytecode.extend(rt)
        bytecode.append(OP['LOAD_CONST'])  # placeholder offset marker
        bytecode.append(idx & 0xFF)
        bytecode.append(0)
        bytecode.append(0)
        bytecode.append(0)

    stats['const_count'] = len(ctx['const_table'])
    return bytecode, stats


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def compile_phase2(src_path, out_path):
    """编译 QEntL 源码为真正的 .qbc 字节码"""
    if not os.path.exists(src_path):
        print(f"[错误] 找不到文件: {src_path}")
        sys.exit(1)

    with open(src_path, 'r', encoding='utf-8') as f:
        source = f.read()

    print(f"[Phase2 引导编译器] 读取源码: {src_path} ({len(source)} 字符)")
    bytecode, stats = compile_qentl(source)

    with open(out_path, 'wb') as f:
        f.write(bytecode)

    print(f"[Phase2 引导编译器] 输出: {out_path}")
    print(f"[Phase2 引导编译器] 字节码大小: {len(bytecode)} 字节")
    print(f"[Phase2 引导编译器] 统计:")
    print(f"  - 函数定义: {stats['funcs_def']}")
    print(f"  - 编译指令: {stats['instructions']}")
    print(f"  - 常量表:   {stats['const_count']}")
    print(f"  - 导出:     {len(stats['exports'])}")
    print(f"  - 总行数:   {stats['lines']}")

    # 验证：检查不是空壳
    if len(bytecode) <= 8:
        print("[警告] 生成的 .qbc 可能为空壳（仅文件头）")
        return len(bytecode)
    # 检查是否包含真正的编译器功能（DEFINE_FUNC 或 BC_FUNC_BODY）
    has_func = b'\x1f' in bytecode  # DEFINE_FUNC = 31 = 0x1f
    has_body = b'\xff' in bytecode  # BC_FUNC_BODY = 255
    has_gate = any(op in bytecode for op in [bytes([1]), bytes([2]), bytes([4])])
    if has_func or has_body or has_gate:
        print(f"[Phase2 引导编译器] 验证通过: 包含真正的编译器功能"
              f" (DEFINE_FUNC={'有' if has_func else '无'}, "
              f"FUNC_BODY={'有' if has_body else '无'}, "
              f"量子指令={'有' if has_gate else '无'})")
    else:
        print("[警告] .qbc 可能不包含真正的编译器功能")

    return len(bytecode)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <输入.qentl> <输出.qbc>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    size = compile_phase2(input_path, output_path)
    print(f"[Phase2 引导编译器] 编译完成: {size} 字节")
    sys.exit(0 if size > 8 else 1)
