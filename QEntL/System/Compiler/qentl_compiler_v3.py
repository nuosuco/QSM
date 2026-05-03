#!/usr/bin/env python3
"""
QEntL量子编译器 V3 - 将 .qentl 源码编译为 .qbc 字节码
支持:类型定义、函数声明、量子程序、控制流
"""

import re
import json
import sys
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

# === QBC字节码指令集 ===
class OpCode(Enum):
    # 基础操作
    NOP = 0x00
    HALT = 0x01
    LOAD_CONST = 0x10      # 加载常量
    LOAD_VAR = 0x11        # 加载变量
    STORE_VAR = 0x12       # 存储变量
    LOAD_FIELD = 0x13; GLOBAL_DECL = 0x25      # 加载字段
    STORE_FIELD = 0x14     # 存储字段

    # 算术运算 (QBC: 升)
    ADD = 0x20
    SUB = 0x21
    MUL = 0x22
    DIV = 0x23
    MOD = 0x24

    # 比较运算
    EQ = 0x30
    NEQ = 0x31
    LT = 0x32
    GT = 0x33
    LTE = 0x34
    GTE = 0x35

    # 控制流 (QBC: 逃)
    JUMP = 0x40
    JUMP_IF_FALSE = 0x41
    JUMP_IF_TRUE = 0x42
    CALL = 0x43
    RETURN = 0x44
    LOOP_START = 0x45
    LOOP_END = 0x46

    # 量子操作 (QBC: 爬/凑)
    QUANTUM_INIT = 0x50    # 初始化量子态
    QUANTUM_GATE = 0x51    # 应用量子门
    QUANTUM_MEASURE = 0x52 # 量子测量
    QUANTUM_ENTANGLE = 0x53 # 量子纠缠

    # I/O
    LOG = 0x60
    INPUT = 0x61

    # 类型操作
    TYPE_DEF = 0x70
    IMPORT = 0xF1
    EXPORT = 0xF2
    CLASS_DEF = 0xF3
    INTERFACE_DEF = 0xF4
    TYPE_CAST = 0x71

    # 对象操作
    OBJ_CREATE = 0x80
    OBJ_GET = 0x81
    OBJ_SET = 0x82
    BUILTIN_CALL = 0x95  # 内置函数调用
    # 数组操作
    BUILD_LIST = 0x90
    BUILD_DICT = 0x93
    INDEX_ACCESS = 0x91
    INDEX_ASSIGN = 0x92
    SLICE_ACCESS = 0x94
    # 扩展操作
    DOT_ACCESS = 0xF5
    METHOD_CALL = 0xF6
    UNARY_NOT = 0xF7
    LOGICAL_AND = 0xCE
    LOGICAL_OR = 0xCF
    BOOL_LOAD = 0xF8
    PUSH_TRY = 0xF9
    POP_TRY = 0xFA
    THROW = 0xFB
    LABEL = 0xFC
    ASSERT = 0xCD

# === 词法分析 ===
class TokenType(Enum):
    # 关键字
    CONFIG = '配置'
    TYPE = '类型'
    FUNC = '函数'
    QUANTUM_PROGRAM = 'quantum_program'
    QUANTUM_ENUM = 'quantum_enum'
    QUANTUM_CLASS = 'quantum_class'
    QUANTUM_INTERFACE = 'quantum_interface'
    IMPORT = 'import'
    EXPORT = 'export'
    IF = '如果'
    ELSE = '否则'
    ELIF = '否则如果'
    MATCH = '匹配'
    CASE = '情况'
    DEFAULT = '默认'
    RETURN = '返回'
    LET = '让'
    FOR = '循环'
    IN = '在'
    TO = '到'
    WHILE = '当'
    GLOBAL = '全局'
    LOG = 'LOG'  # Use English keyword 'LOG' (was '日志')
    SETUP = 'setup'
    RUN = 'run'

    # 类型关键字
    STRING = '字符串'
    INT = '整数'
    FLOAT = '浮点数'
    BOOL = '布尔'
    QUANTUM = '量子'
    QUANTUM_GATE_KW = '量子门'
    MEASURE_KW = '测量'
    ENTANGLE_KW = '纠缠'
    QUANTUM_INIT_KW = '量子初始化'
    STEP_KW = '步长'

    # 符号
    LBRACE = '{'
    RBRACE = '}'
    LPAREN = '('
    RPAREN = ')'
    LBRACKET = '['
    RBRACKET = ']'
    ARROW = '->'
    DOT = '.'
    COMMA = ','
    COLON = ':'
    SEMICOLON = ';'
    ASSIGN = '='
    PLUS_ASSIGN = '+='
    MINUS_ASSIGN = '-='
    MUL_ASSIGN = '*='
    DIV_ASSIGN = '/='

    # 运算符
    PLUS = '+'
    MINUS = '-'
    STAR = '*'
    SLASH = '/'
    EQEQ = '=='
    NEQ = '!='
    LT = '<'
    GT = '>'
    LTE = '<='
    GTE = '>='
    PERCENT = '%'
    AND = '且'
    OR = '或'
    QUESTION = '?'
    NOT = '非'
    BOOL_TRUE = 'true'
    BOOL_FALSE = 'false'
    NULL = '空'
    BREAK = 'break'
    CONTINUE = 'continue'
    THROW = '抛出'
    ASSERT = '断言'
    TRY = '尝试'
    CATCH = '捕获'

    # 字面量
    IDENTIFIER = 'IDENTIFIER'
    STRING_LIT = 'STRING_LIT'
    NUMBER_LIT = 'NUMBER_LIT'

    # 特殊
    EOF = 'EOF'
    COMMENT = 'COMMENT'

@dataclass
class Token:
    type: TokenType
    value: str
    line: int = 0
    col: int = 0

class Lexer:
    KEYWORDS = {t.value: t for t in TokenType if t.value and t.value not in ['IDENTIFIER', 'STRING_LIT', 'NUMBER_LIT', 'EOF', 'COMMENT']}
    # Chinese aliases
    KEYWORDS['量子程序'] = TokenType.QUANTUM_PROGRAM
    KEYWORDS['量子初始化'] = TokenType.QUANTUM_INIT_KW
    KEYWORDS['量子类'] = TokenType.QUANTUM_CLASS
    KEYWORDS['量子枚举'] = TokenType.QUANTUM_ENUM
    KEYWORDS['量子接口'] = TokenType.QUANTUM_INTERFACE
    KEYWORDS['循环当'] = TokenType.WHILE
    KEYWORDS['每个'] = TokenType.FOR
    KEYWORDS['全局'] = TokenType.GLOBAL
    KEYWORDS['否则如果'] = TokenType.ELIF
    KEYWORDS['跳出'] = TokenType.BREAK
    KEYWORDS['继续'] = TokenType.CONTINUE
    KEYWORDS['抛出'] = TokenType.THROW
    KEYWORDS['throw'] = TokenType.THROW

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            ch = self.source[self.pos]

            # Skip whitespace
            if ch in ' \t\r':
                self._advance()
                continue

            if ch == '\n':
                self.line += 1
                self.col = 1
                self.pos += 1
                continue

            # Comments (// or #)
            if ch == '/' and self.pos + 1 < len(self.source) and self.source[self.pos+1] == '/':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self._advance()
                continue
            if ch == '#':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self._advance()
                continue

            # String literals
            if ch == '"':
                self._read_string()
                continue

            # Numbers
            if ch.isdigit():
                self._read_number()
                continue

            # Two-character operators
            if self.pos + 1 < len(self.source):
                two = self.source[self.pos:self.pos+2]
                if two == '->':
                    self._add_token(TokenType.ARROW, '->')
                    self._advance(); self._advance()
                    continue
                if two == '==':
                    self._add_token(TokenType.EQEQ, '==')
                    self._advance(); self._advance()
                    continue
                if two == '!=':
                    self._add_token(TokenType.NEQ, '!=')
                    self._advance(); self._advance()
                    continue
                if two == '+=':
                    self._add_token(TokenType.PLUS_ASSIGN, '+=')
                    self._advance(); self._advance()
                    continue
                if two == '-=':
                    self._add_token(TokenType.MINUS_ASSIGN, '-=')
                    self._advance(); self._advance()
                    continue
                if two == '*=':
                    self._add_token(TokenType.MUL_ASSIGN, '*=')
                    self._advance(); self._advance()
                    continue
                if two == '/=':
                    self._add_token(TokenType.DIV_ASSIGN, '/=')
                    self._advance(); self._advance()
                    continue
            if two == '<=':
                self._add_token(TokenType.LTE, '<=')
                self._advance(); self._advance()
                continue
            if two == '>=':
                self._add_token(TokenType.GTE, '>=')
                self._advance(); self._advance()
                continue
            if ch == "!" and (self.pos >= len(self.source) or self.source[self.pos] != "="):
                self._add_token(TokenType.NOT, "!")
                self._advance()
                continue
            # Single character operators/symbols
            symbol_map = {
                '{': TokenType.LBRACE, '}': TokenType.RBRACE,
                '(': TokenType.LPAREN, ')': TokenType.RPAREN,
                '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
                '.': TokenType.DOT, ',': TokenType.COMMA,
    '?': TokenType.QUESTION,
    ':': TokenType.COLON, ';': TokenType.SEMICOLON,
                '=': TokenType.ASSIGN,
        '+=': TokenType.PLUS_ASSIGN,
        '-=': TokenType.MINUS_ASSIGN,
        '*=': TokenType.MUL_ASSIGN,
        '/=': TokenType.DIV_ASSIGN, '+': TokenType.PLUS,
                '-': TokenType.MINUS, '*': TokenType.STAR,
                '/': TokenType.SLASH,
    '%': TokenType.PERCENT, '<': TokenType.LT,
                '>': TokenType.GT,
            }
            if ch in symbol_map:
                self._add_token(symbol_map[ch], ch)
                self._advance()
                continue

            # Identifiers and keywords (supports Chinese)
            if ch.isalpha() or '\u4e00' <= ch <= '\u9fff' or ch == '_':
                self._read_identifier()
                continue

            # Skip unknown
            self._advance()

        self.tokens.append(Token(TokenType.EOF, '', self.line, self.col))
        return self.tokens

    def _advance(self):
        self.pos += 1
        self.col += 1

    def _add_token(self, type: TokenType, value: str):
        self.tokens.append(Token(type, value, self.line, self.col))

    def _read_string(self):
        self._advance()  # skip opening "
        chars = []
        while self.pos < len(self.source) and self.source[self.pos] != '"':
            if self.source[self.pos] == '\\':
                self._advance()  # skip backslash
                if self.pos < len(self.source):
                    esc = self.source[self.pos]
                    esc_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', '0': '\0'}
                    chars.append(esc_map.get(esc, '\\' + esc))
                    self._advance()
                continue
            if self.source[self.pos] == '\n':
                self.line += 1
            chars.append(self.source[self.pos])
            self._advance()
        value = ''.join(chars)
        self._add_token(TokenType.STRING_LIT, value)
        self._advance()  # skip closing "

    def _read_number(self):
        start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
            self._advance()
        self._add_token(TokenType.NUMBER_LIT, self.source[start:self.pos])

    def _read_identifier(self):
        start = self.pos
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch.isalnum() or '\u4e00' <= ch <= '\u9fff' or ch == '_' or ch == '·':
                self._advance()
            else:
                break
        value = self.source[start:self.pos]
        ttype = self.KEYWORDS.get(value, TokenType.IDENTIFIER)
        self._add_token(ttype, value)

# === 语法分析 ===
@dataclass
class ASTNode:
    type: str
    children: List[Any] = field(default_factory=list)
    value: str = ''
    line: int = 0

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> ASTNode:
        root = ASTNode('Program')
        while not self._at_end():
            node = self._parse_top_level()
            if node:
                root.children.append(node)
        return root

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _peek(self, offset=0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return Token(TokenType.EOF, '')

    def _advance(self) -> Token:
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def _peek(self, offset=1) -> Token:
        """Look ahead without consuming"""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def _at_end(self) -> bool:
        return self._current().type == TokenType.EOF

    def _expect(self, ttype: TokenType) -> Token:
        if self._current().type == ttype:
            return self._advance()
        raise SyntaxError(f"Expected {ttype}, got {self._current().type} ({self._current().value}) at line {self._current().line}")


    def _parse_import(self):
        """解析 import 语句: import 模块名 [as 别名]"""
        node = ASTNode('Import', line=self._peek().line)
        self._expect(TokenType.IMPORT)
        # Get module path (can be dotted: import A.B.C)
        module_parts = []
        module_parts.append(self._advance().value)
        while self._peek() and self._peek().type == TokenType.DOT:
            self._advance()  # consume dot
            module_parts.append(self._advance().value)
        node.value = '.'.join(module_parts)
        # Optional: as alias
        if self._peek() and self._peek().value == 'as':
            self._advance()  # consume 'as'
            node.children.append(ASTNode('Alias', value=self._advance().value, line=node.line))
        return node

    def _parse_export(self):
        """解析 export 语句: export 名称 [as 别名]"""
        node = ASTNode('Export', line=self._peek().line)
        self._expect(TokenType.EXPORT)
        node.value = self._advance().value
        # Optional: as alias
        if self._peek() and self._peek().value == 'as':
            self._advance()  # consume 'as'
            node.children.append(ASTNode('Alias', value=self._advance().value, line=node.line))
        return node


    def _parse_quantum_class(self):
        """解析 quantum_class: quantum_class 名称 { 字段+方法 }"""
        node = ASTNode('QuantumClass', line=self._peek().line)
        self._expect(TokenType.QUANTUM_CLASS)
        node.value = self._advance().value  # class name
        self._expect(TokenType.LBRACE)
        while self._current().type != TokenType.RBRACE and not self._at_end():
            # Parse field: 名称: 类型 or 名称: 类型 = 值
            # Parse method: 函数 名称(...) { ... }
            if self._current().type == TokenType.FUNC:
                method = self._parse_function()
                node.children.append(method)
            else:
                # Field definition
                field_name = self._advance().value
                if self._current().type == TokenType.COLON:
                    self._advance()  # skip :
                    field_type = self._advance().value
                    field_node = ASTNode('Field', value=field_name, line=node.line)
                    field_node.field_type = field_type
                    # Optional default value
                    if self._current().value == '=' or self._current().type == TokenType.ASSIGN:
                        self._advance()
                        field_node.children.append(ASTNode('Default', value=self._advance().value, line=node.line))
                    node.children.append(field_node)
                else:
                    # Simple field without type
                    node.children.append(ASTNode('Field', value=field_name, line=node.line))
                # Skip comma
                if self._current().type == TokenType.COMMA:
                    self._advance()
        self._expect(TokenType.RBRACE)
        return node


    def _parse_quantum_interface(self):
        """解析 quantum_interface: quantum_interface 名称 { 方法签名 }"""
        node = ASTNode('QuantumInterface', line=self._peek().line)
        self._expect(TokenType.QUANTUM_INTERFACE)
        node.value = self._advance().value
        self._expect(TokenType.LBRACE)
        while self._current().type != TokenType.RBRACE and not self._at_end():
            if self._current().type == TokenType.FUNC:
                method = self._parse_function()
                node.children.append(method)
            else:
                method_name = self._advance().value
                method_node = ASTNode('MethodSig', value=method_name, line=node.line)
                if self._current().type == TokenType.LPAREN:
                    self._advance()
                    while self._current().type != TokenType.RPAREN:
                        self._advance()
                    self._expect(TokenType.RPAREN)
                node.children.append(method_node)
            if self._current().type == TokenType.COMMA:
                self._advance()
        self._expect(TokenType.RBRACE)
        return node

    def _parse_top_level(self):
        t = self._current()
        if t.type == TokenType.CONFIG:
            return self._parse_config()
        elif t.type == TokenType.TYPE:
            return self._parse_type_def()
        elif t.type == TokenType.IDENTIFIER and self._peek().type == TokenType.COLON:
            # Labeled declaration: 函数名: 函数(args) { body }
            label = self._advance().value
            self._advance()  # skip :
            if self._current().type == TokenType.FUNC:
                node = self._parse_function(name_override=label)
                return node
            else:
                return None
        elif t.type == TokenType.FUNC:
            return self._parse_function()
        elif t.type == TokenType.QUANTUM_PROGRAM:
            return self._parse_quantum_program()
        elif t.type == TokenType.QUANTUM_ENUM:
            return self._parse_quantum_enum()
        elif t.type == TokenType.IMPORT:
            return self._parse_import()
        elif t.type == TokenType.EXPORT:
            return self._parse_export()
        elif t.type == TokenType.LET:
            return self._parse_let()
        elif t.type == TokenType.QUANTUM_CLASS:
            return self._parse_quantum_class()
        elif t.type == TokenType.QUANTUM_INTERFACE:
            return self._parse_quantum_interface()
        else:
            # Skip unknown token
            self._advance()
            return None

    def _parse_config(self):
        node = ASTNode('Config', line=self._current().line)
        self._expect(TokenType.CONFIG)
        self._expect(TokenType.LBRACE)
        while self._current().type != TokenType.RBRACE:
            key = self._advance().value
            self._expect(TokenType.COLON)
            val = self._advance().value
            node.children.append(ASTNode('ConfigEntry', value=f"{key}={val}"))
            if self._current().type == TokenType.COMMA:
                self._advance()
        self._expect(TokenType.RBRACE)
        return node

    def _parse_type_def(self):
        node = ASTNode('TypeDef', line=self._current().line)
        self._expect(TokenType.TYPE)
        node.value = self._advance().value  # type name
        self._expect(TokenType.LBRACE)
        while self._current().type != TokenType.RBRACE:
            field_name = self._advance().value
            self._expect(TokenType.COLON)
            field_type = self._advance().value
            node.children.append(ASTNode('Field', value=f"{field_name}:{field_type}"))
            if self._current().type == TokenType.COMMA:
                self._advance()
        self._expect(TokenType.RBRACE)
        return node

    def _parse_function(self, name_override=None):
        node = ASTNode('Function', line=self._current().line)
        self._expect(TokenType.FUNC)
        if name_override:
            node.value = name_override
            # Skip default name parsing - next token should be LPAREN
        else:
            node.value = self._advance().value  # function name
        self._expect(TokenType.LPAREN)
        # Parameters
        while self._current().type != TokenType.RPAREN:
            pname = self._advance().value
            if self._current().type == TokenType.COLON:
                self._advance()
                ptype = self._advance().value
                node.children.append(ASTNode('Param', value=f"{pname}:{ptype}"))
            else:
                node.children.append(ASTNode('Param', value=f"{pname}:any"))
            if self._current().type == TokenType.COMMA:
                self._advance()
        self._expect(TokenType.RPAREN)
        # Return type
        if self._current().type == TokenType.ARROW:
            self._advance()
            ret_type = self._advance().value
            node.children.append(ASTNode('ReturnType', value=ret_type))
        # Body
        body = self._parse_block()
        node.children.append(body)
        return node

    def _parse_quantum_program(self):
        node = ASTNode('QuantumProgram', line=self._current().line)
        self._expect(TokenType.QUANTUM_PROGRAM)
        # Check if next token is LBRACE (simple format) or name (full format)
        if self._current().type == TokenType.LBRACE:
            # Simple format: 量子程序 { 量子初始化 N; 量子门 H 0; ... }
            node.value = 'inline_quantum'
            self._advance()  # skip LBRACE
            # Parse quantum instructions directly
            while self._current().type != TokenType.RBRACE:
                if self._current().value in ('量子初始化', 'quantum_init'):
                    self._advance()
                    n_qubits = int(self._advance().value)
                    init_node = ASTNode('QuantumInit', value=n_qubits, line=self._current().line)
                    node.children.append(init_node)
                elif self._current().value in ('量子门', 'quantum_gate'):
                    self._advance()
                    gate_name = self._advance().value
                    target = self._advance().value
                    gate_node = ASTNode('QuantumGate', value=f'{gate_name} {target}', line=self._current().line)
                    node.children.append(gate_node)
                elif self._current().value in ('纠缠', 'entangle', 'CNOT'):
                    self._advance()
                    ctrl = self._advance().value
                    tgt = self._advance().value
                    ent_node = ASTNode('QuantumEntangle', value=f'{ctrl} {tgt}', line=self._current().line)
                    node.children.append(ent_node)
                elif self._current().type == TokenType.NEWLINE:
                    self._advance()
                else:
                    self._advance()  # skip unknown
            self._expect(TokenType.RBRACE)
            return node
        node.value = self._advance().value  # program name
        self._expect(TokenType.LBRACE)
        # Parse setup/run sections - they use inline function-like syntax
        while self._current().type != TokenType.RBRACE:
            section = self._advance().value  # setup/run
            self._expect(TokenType.COLON)
            # The body can be a function definition or an inline anonymous function
            if self._current().type == TokenType.FUNC:
                # Function with optional params
                self._advance()  # skip 函数
                self._expect(TokenType.LPAREN)
                param_names = []
                while self._current().type != TokenType.RPAREN:
                    pname = self._advance().value
                    if self._current().type == TokenType.COLON:
                        self._advance()  # skip :
                        self._advance()  # skip type
                    param_names.append(pname)
                    if self._current().type == TokenType.COMMA:
                        self._advance()
                self._expect(TokenType.RPAREN)
                body = self._parse_block()
                body.type = 'Function'
                body.value = section
                body.params = param_names
            elif self._current().type == TokenType.LBRACE:
                body = self._parse_block()
            else:
                body = self._parse_block()
            node.children.append(ASTNode('Section', value=section, children=[body]))
            # Skip comma between sections
            if self._current().type == TokenType.COMMA:
                self._advance()
        self._expect(TokenType.RBRACE)
        return node

    def _parse_quantum_enum(self):
        """Parse quantum_enum definition
        quantum_enum Name {
            VALUE1,
            VALUE2,
            ...
        }
        """
        node = ASTNode('QuantumEnum', line=self._current().line)
        self._expect(TokenType.QUANTUM_ENUM)
        node.value = self._advance().value  # enum name
        self._expect(TokenType.LBRACE)
        while self._current().type != TokenType.RBRACE:
            val = self._advance().value
            node.children.append(ASTNode('EnumValue', value=val))
            if self._current().type == TokenType.COMMA:
                self._advance()
        self._expect(TokenType.RBRACE)
        return node

    def _parse_block(self):
        node = ASTNode('Block', line=self._current().line)
        self._expect(TokenType.LBRACE)
        while self._current().type != TokenType.RBRACE:
            stmt = self._parse_statement()
            if stmt:
                node.children.append(stmt)
        self._expect(TokenType.RBRACE)
        return node

    def _parse_statement(self):
        t = self._current()
        if t.type == TokenType.IF:
            return self._parse_if()
        elif t.type == TokenType.MATCH:
            return self._parse_switch()
        elif t.type == TokenType.RETURN:
            return self._parse_return()
        elif t.type == TokenType.LET:
            return self._parse_let()
        elif t.type == TokenType.FOR:
            return self._parse_for()
        elif t.type == TokenType.ENTANGLE_KW:
            return self._parse_entangle()

        elif t.type == TokenType.MEASURE_KW:
            return self._parse_measure()

        elif t.type == TokenType.QUANTUM_GATE_KW:
            return self._parse_quantum_gate()

        elif t.type == TokenType.LOG:
            return self._parse_log()
        elif t.type == TokenType.WHILE:
            return self._parse_while()
        elif t.type == TokenType.GLOBAL:
            self._advance()
            var_name = self._advance().value
            return ASTNode('GlobalDecl', value=var_name, line=t.line)
        elif t.type == TokenType.BREAK:
            self._advance()
            return ASTNode('Break', line=t.line)
        elif t.type == TokenType.CONTINUE:
            self._advance()
            return ASTNode('Continue', line=t.line)
        elif t.type == TokenType.THROW:
            self._advance()
            expr = self._parse_expression()
            node = ASTNode('Throw', line=t.line)
            node.children.append(expr)
            return node
        elif t.type == TokenType.TRY:
            return self._parse_try()
        elif t.type == TokenType.ASSERT:
            return self._parse_assert()
        elif t.type == TokenType.QUANTUM_PROGRAM:
            return self._parse_quantum_program()
        else:
            # Check for compound assignment: x += expr
            if t.type == TokenType.IDENTIFIER and self._peek() and self._peek().type in (TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN, TokenType.MUL_ASSIGN, TokenType.DIV_ASSIGN):
                var_name = t.value
                self._advance()  # skip identifier
                op_token = self._advance()  # skip += etc
                expr = self._parse_expression()
                op_map = {TokenType.PLUS_ASSIGN: '升', TokenType.MINUS_ASSIGN: '降', TokenType.MUL_ASSIGN: '乘', TokenType.DIV_ASSIGN: '除'}
                node = ASTNode('CompoundAssign', value=var_name, line=t.line)
                node.assign_op = op_map.get(op_token.type, '升')
                node.children.append(expr)
                return node
            
        # Expression statement (may be assignment)
        expr = self._parse_expression()
        if self._current() and self._current().type == TokenType.ASSIGN:
            # Assignment without 让: x = val, d["key"] = val, arr[i] = val
            self._advance()  # skip =
            value = self._parse_expression()
            if expr.type == 'IndexAccess':
                # d["key"] = val or self.data[key] = val
                if expr.children[0].type == 'Identifier':
                    # Simple: d[key] = val
                    assign_node = ASTNode('IndexAssign', value=expr.children[0].value, line=expr.line)
                    assign_node.children.append(expr.children[1])  # key
                    assign_node.children.append(value)  # value
                else:
                    # Complex: self.data[key] = val
                    assign_node = ASTNode('IndexAssign', value=None, line=expr.line)
                    assign_node.children.append(expr.children[0])  # target expr
                    assign_node.children.append(expr.children[1])  # key
                    assign_node.children.append(value)  # value
                return assign_node
            elif expr.type == 'FieldAccess':
                # q.field = val → FieldAssign
                    assign_node = ASTNode('FieldAssign', value=expr.value, line=expr.line)
                    assign_node.children.append(expr.children[0])  # object
                    assign_node.children.append(value)  # value
                    return assign_node
            elif expr.type == 'Identifier':
                # x = val → Assign
                assign_node = ASTNode('Assign', value=expr.value, line=expr.line)
                assign_node.children.append(value)
                return assign_node
            else:
                return value
        if self._current().type == TokenType.SEMICOLON:
            self._advance()
        return expr

    def _parse_assert(self):
        """Parse assert: 断言(expr) or 断言(expr, "message")"""
        node = ASTNode('Assert', line=self._current().line)
        self._expect(TokenType.ASSERT)
        self._expect(TokenType.LPAREN)
        node.children.append(self._parse_expression())  # condition
        if self._current().type == TokenType.COMMA:
            self._advance()
            node.children.append(self._parse_expression())  # message
        self._expect(TokenType.RPAREN)
        return node

    def _parse_try(self):
        """Parse try/catch: 尝试 { ... } 捕获 (e) { ... }"""
        node = ASTNode('Try', line=self._current().line)
        self._expect(TokenType.TRY)
        node.children.append(self._parse_block())  # try body
        if self._current().type == TokenType.CATCH:
            self._advance()
            # Optional error variable: 捕获(e) or 捕获
            error_var = None
            if self._current().type == TokenType.LPAREN:
                self._advance()
                error_var = self._advance().value
                self._expect(TokenType.RPAREN)
            node.children.append(self._parse_block())  # catch body
            if error_var:
                node.value = error_var
        return node

    def _parse_if(self):
            node = ASTNode('If', line=self._current().line)
            self._expect(TokenType.IF)
            node.children.append(self._parse_expression())  # condition
            node.children.append(self._parse_block())  # if-body
            # Handle elif chain
            while self._current().type == TokenType.ELIF:
                self._advance()  # skip '否则如果'
                elif_node = ASTNode('If', line=self._current().line)
                elif_node.children.append(self._parse_expression())  # condition
                elif_node.children.append(self._parse_block())  # elif-body
                # Check for else after this elif
                if self._current().type == TokenType.ELSE:
                    self._advance()  # skip '否则'
                    elif_node.children.append(self._parse_block())  # else-body
                node.children.append(elif_node)
            # Handle final else
            if self._current().type == TokenType.ELSE:
                self._advance()  # skip '否则'
                if self._current().type == TokenType.IF:
                    node.children.append(self._parse_if())  # else if
                else:
                    node.children.append(self._parse_block())  # else-body
            return node

    def _parse_assert(self):
        """Parse assert: 断言(expr) or 断言(expr, "message")"""
        node = ASTNode('Assert', line=self._current().line)
        self._expect(TokenType.ASSERT)
        self._expect(TokenType.LPAREN)
        node.children.append(self._parse_expression())  # condition
        if self._current().type == TokenType.COMMA:
            self._advance()
            node.children.append(self._parse_expression())  # message
        self._expect(TokenType.RPAREN)
        return node

    def _parse_try(self):
        """Parse try/catch: 尝试 { ... } 捕获 (e) { ... }"""
        node = ASTNode('Try', line=self._current().line)
        self._expect(TokenType.TRY)
        node.children.append(self._parse_block())  # try body
        if self._current().type == TokenType.CATCH:
            self._advance()
            # Optional error variable: 捕获(e) or 捕获
            error_var = None
            if self._current().type == TokenType.LPAREN:
                self._advance()
                error_var = self._advance().value
                self._expect(TokenType.RPAREN)
            node.children.append(self._parse_block())  # catch body
            if error_var:
                node.value = error_var
        return node

    def _parse_if(self):
        node = ASTNode('If', line=self._current().line)
        self._expect(TokenType.IF)
        node.children.append(self._parse_expression())  # condition
        node.children.append(self._parse_block())  # if-body
        # Handle elif chain
        while self._current().type == TokenType.ELIF:
            self._advance()  # skip '否则如果'
            elif_node = ASTNode('If', line=self._current().line)
            elif_node.children.append(self._parse_expression())
            elif_node.children.append(self._parse_block())
            if self._current().type == TokenType.ELSE:
                self._advance()
                elif_node.children.append(self._parse_block())
            node.children.append(elif_node)
        # Handle final else
        if self._current().type == TokenType.ELSE:
            self._advance()
            if self._current().type == TokenType.IF:
                node.children.append(self._parse_if())
            else:
                node.children.append(self._parse_block())
        return node

    def _parse_builtin_call(self, func_name):
        node = ASTNode('BuiltinCall', line=self._current().line)
        node.value = func_name
        self._advance()  # skip function name
        self._expect(TokenType.LPAREN)
        # Parse arguments
        if self._current().type != TokenType.RPAREN:
            node.children.append(self._parse_expression())
            while self._current().type == TokenType.COMMA:
                self._advance()
                node.children.append(self._parse_expression())
        self._expect(TokenType.RPAREN)
        return node

    def _parse_switch(self):
        node = ASTNode('Switch', line=self._current().line)
        self._expect(TokenType.MATCH)
        node.children.append(self._parse_expression())  # match expr
        self._expect(TokenType.LBRACE)
        # Parse cases
        while self._current().type == TokenType.CASE:
            self._advance()  # skip '情况'
            case_node = ASTNode('Case', line=self._current().line)
            case_node.children.append(self._parse_expression())  # case value
            case_node.children.append(self._parse_block())  # case body
            node.children.append(case_node)
        # Parse default
        if self._current().type == TokenType.DEFAULT:
            self._advance()  # skip '默认'
            default_node = ASTNode('Default', line=self._current().line)
            default_node.children.append(self._parse_block())
            node.children.append(default_node)
        self._expect(TokenType.RBRACE)
        return node

    def _parse_return(self):
        node = ASTNode('Return', line=self._current().line)
        self._expect(TokenType.RETURN)
        node.children.append(self._parse_expression())
        return node

    def _parse_let(self):
        node = ASTNode('Let', line=self._current().line)
        self._expect(TokenType.LET)
        node.value = self._advance().value  # variable name
        # Check for indexed assignment
        if self._current().type == TokenType.LBRACKET:
            self._advance()  # consume [
            index = self._parse_expression()
            self._expect(TokenType.RBRACKET)
            node.type = 'IndexAssign'
            self._expect(TokenType.ASSIGN)
            node.children.append(index)
            node.children.append(self._parse_expression())
        else:
            self._expect(TokenType.ASSIGN)
            node.children.append(self._parse_expression())
        return node

    def _parse_for(self):
        node = ASTNode('For', line=self._current().line)
        self._expect(TokenType.FOR)
        node.value = self._advance().value  # loop variable
        self._expect(TokenType.IN)
        # Parse range: start 到 end
        start = self._parse_expression()
        if self._current().type == TokenType.TO:
            self._advance()  # consume 到
            end = self._parse_expression()
            # Optional step: 步长 2
            step = ASTNode('NumberLit', value='1')
            if self._current().type == TokenType.STEP_KW:
                self._advance()  # consume 步长
                step = self._parse_expression()
            node.children.append(ASTNode('Range', children=[start, end, step]))
        else:
            node.children.append(start)
        node.children.append(self._parse_block())
        return node

    def _parse_entangle(self):
        """Parse 纠缠 0 1 - create Bell state"""
        node = ASTNode('Entangle', line=self._current().line)
        self._expect(TokenType.ENTANGLE_KW)
        # Two target qubits
        node.children.append(self._parse_primary())  # control
        if self._current().type == TokenType.NUMBER_LIT:
            node.children.append(self._parse_primary())  # target
        return node

    def _parse_measure(self):
        """Parse 测量 0 or 测量 比特0"""
        node = ASTNode('Measure', line=self._current().line)
        self._expect(TokenType.MEASURE_KW)
        # Target qubit (number)
        node.children.append(self._parse_primary())
        return node

    def _parse_quantum_gate(self):
        """Parse 量子门 H 0 or 量子门 CNOT 0 1"""
        node = ASTNode('QuantumGate', line=self._current().line)
        self._expect(TokenType.QUANTUM_GATE_KW)
        # Gate name (identifier or string)
        if self._current().type == TokenType.STRING_LIT:
            node.value = self._advance().value
        else:
            node.value = self._advance().value  # gate name as identifier
        # Target qubits - only consume NUMBER_LIT tokens
        while self._current().type == TokenType.NUMBER_LIT:
            node.children.append(self._parse_primary())
        return node

    def _parse_log(self):
        node = ASTNode('Log', line=self._current().line)
        self._expect(TokenType.LOG)
        self._expect(TokenType.LPAREN)
        node.children.append(self._parse_expression())
        self._expect(TokenType.RPAREN)
        return node

    def _parse_while(self):
        node = ASTNode('While', line=self._current().line)
        self._expect(TokenType.WHILE)
        node.children.append(self._parse_expression())
        node.children.append(self._parse_block())
        return node

    def _parse_expression(self):
        return self._parse_ternary()

    def _parse_ternary(self):
        """Parse ternary: condition ? true_expr : false_expr"""
        node = self._parse_logical_or()
        if self._current().type == TokenType.QUESTION:
            self._advance()  # consume ?
            true_expr = self._parse_expression()
            self._expect(TokenType.COLON)
            false_expr = self._parse_expression()
            node = ASTNode('Ternary', children=[node, true_expr, false_expr], line=node.line)
        return node

    def _parse_logical_or(self):
        left = self._parse_logical_and()
        while self._current().type == TokenType.OR:
            self._advance()  # consume 或
            right = self._parse_logical_and()
            left = ASTNode('BinaryOp', value='或', children=[left, right])
        return left

    def _parse_logical_and(self):
        left = self._parse_comparison()
        while self._current().type == TokenType.AND:
            self._advance()  # consume 且
            right = self._parse_comparison()
            left = ASTNode('BinaryOp', value='且', children=[left, right])
        return left

    def _parse_comparison(self):
        left = self._parse_addition()
        while self._current().type in (TokenType.EQEQ, TokenType.NEQ, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            op = self._advance().value
            right = self._parse_addition()
            left = ASTNode('BinaryOp', value=op, children=[left, right])
        return left

    def _parse_addition(self):
        left = self._parse_multiplication()
        while self._current().type in (TokenType.PLUS, TokenType.MINUS):
            op = self._advance().value
            right = self._parse_multiplication()
            left = ASTNode('BinaryOp', value=op, children=[left, right])
        return left

    def _parse_multiplication(self):
        left = self._parse_factor()
        while self._current().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._advance().value
            right = self._parse_primary()
            left = ASTNode('BinaryOp', value=op, children=[left, right])
        return left

    def _parse_factor(self):
        """Parse factor - handle unary minus and NOT"""
        if self._current().type == TokenType.MINUS:
            self._advance()
            node = self._parse_primary()
            if node is None:
                return ASTNode('NumberLit', value='0', line=1)
            neg_node = ASTNode('UnaryMinus', line=node.line)
            neg_node.children.append(node)
            return neg_node
        if self._current().type == TokenType.NOT:
            self._advance()
            node = self._parse_primary()
            if node is None:
                return ASTNode('BoolLit', value='false', line=1)
            not_node = ASTNode('UnaryNot', line=node.line)
            not_node.children.append(node)
            return not_node
        return self._parse_primary()

    def _parse_primary(self):
        t = self._current()
        if t.type == TokenType.NUMBER_LIT:
            self._advance()
            return ASTNode('NumberLit', value=t.value, line=t.line)
        elif t.type == TokenType.STRING_LIT:
            self._advance()
            return ASTNode('StringLit', value=t.value, line=t.line)
        elif t.type == TokenType.BOOL_TRUE:
            self._advance()
            return ASTNode('BoolLit', value='true', line=t.line)
        elif t.type == TokenType.BOOL_FALSE:
            self._advance()
            return ASTNode('BoolLit', value='false', line=t.line)
        elif t.type == TokenType.NULL:
            self._advance()
            return ASTNode('NullLit', line=t.line)
        elif t.type == TokenType.TYPE and self._peek() and self._peek().type == TokenType.LPAREN:
            # 类型 as built-in function call
            return self._parse_builtin_call(t.value)
        elif t.type == TokenType.CONFIG and self._peek() and self._peek().type == TokenType.LPAREN:
            # 配置 as class instantiation (not config declaration)
            # Treat as identifier for expression context
            self._advance()
            node = ASTNode('Identifier', value=t.value, line=t.line)
            if self._current().type == TokenType.LPAREN:
                self._advance()
                args = []
                while self._current().type != TokenType.RPAREN:
                    args.append(self._parse_expression())
                    if self._current().type == TokenType.COMMA:
                        self._advance()
                self._expect(TokenType.RPAREN)
                node = ASTNode('Call', value=t.value, children=args, line=t.line)
            # Don't return - fall through to chained dot access below
        elif t.type == TokenType.IDENTIFIER:
            builtin_funcs = {'打印', '长度', '推入', '弹出', '类型', '绝对值', '最大值', '最小值', '字典', '翻转', '包含', '连接', '分割', '替换', '子串', '增1', '减1', '取整', '幂', '是数字', '是字母', '是空', '格式', '查找', '删除', '插入', '重复', '排序', '去重', '范围数', '随机数', '大写', '小写', '首大写', '计数', '开始以', '结束以', '键', '值', '合并'}
            if t.value in builtin_funcs and self._peek() and self._peek().type == TokenType.LPAREN:
                return self._parse_builtin_call(t.value)
            self._advance()
            node = ASTNode('Identifier', value=t.value, line=t.line)
            # Check for function call: identifier(args)
            if self._current().type == TokenType.LPAREN:
                self._advance()  # (
                args = []
                while self._current().type != TokenType.RPAREN:
                    args.append(self._parse_expression())
                    if self._current().type == TokenType.COMMA:
                        self._advance()
                self._expect(TokenType.RPAREN)
                node = ASTNode('Call', value=t.value, children=args, line=t.line)
            # Check for index/slice: identifier[expr]
            elif self._current().type == TokenType.LBRACKET:
                self._advance()  # consume [
                first = self._parse_expression()
                if self._current().type == TokenType.COLON:
                    self._advance()  # consume :
                    second = self._parse_expression()
                    self._expect(TokenType.RBRACKET)
                    node = ASTNode('SliceAccess', children=[node, first, second], line=t.line)
                else:
                    self._expect(TokenType.RBRACKET)
                    node = ASTNode('IndexAccess', children=[node, first], line=t.line)
            # Apply chained dot access (obj.field, obj.method())
            return self._apply_chained_dot(node)
        elif t.type == TokenType.CONFIG and self._peek() and self._peek().type == TokenType.LPAREN:
            # 配置 as class instantiation (not config declaration)
            self._advance()
            node = ASTNode('Identifier', value=t.value, line=t.line)
            if self._current().type == TokenType.LPAREN:
                self._advance()
                args = []
                while self._current().type != TokenType.RPAREN:
                    args.append(self._parse_expression())
                    if self._current().type == TokenType.COMMA:
                        self._advance()
                self._expect(TokenType.RPAREN)
                node = ASTNode('Call', value=t.value, children=args, line=t.line)
            return self._apply_chained_dot(node)
        elif t.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr
        elif t.type == TokenType.LBRACE:
            return self._parse_dict_literal()
        elif t.type == TokenType.LBRACKET:
            return self._parse_list()
        else:
            self._advance()
            return ASTNode('Unknown', value=t.value, line=t.line)
    def _apply_chained_dot(self, node):
        """Apply chained dot and index access (obj.field, obj[i], obj.method()) to any node."""
        while self._current() and (self._current().type == TokenType.DOT or self._current().type == TokenType.LBRACKET):
            if self._current().type == TokenType.LBRACKET:
                # Chained index: arr[0]["key"], obj[i][j]
                self._advance()  # consume [
                idx = self._parse_expression()
                self._expect(TokenType.RBRACKET)
                node = ASTNode('IndexAccess', children=[node, idx], line=node.line)
            else:
                self._advance()  # consume .
                field = self._advance().value
                if self._current().type == TokenType.LPAREN:
                    # Method call: obj.method(args)
                    self._advance()  # consume (
                    args = []
                    while self._current().type != TokenType.RPAREN:
                        args.append(self._parse_expression())
                        if self._current().type == TokenType.COMMA:
                            self._advance()
                    self._expect(TokenType.RPAREN)
                    node = ASTNode('MethodCall', value=field, children=[node] + args, line=node.line)
                else:
                    # Field access: obj.field
                    node = ASTNode('FieldAccess', value=field, children=[node], line=node.line)
        return node
    def _parse_object_literal(self):
        """Parse object literal { key: value, ... }"""
        node = ASTNode('ObjectLiteral', line=self._current().line)
        self._expect(TokenType.LBRACE)
        while self._current().type != TokenType.RBRACE:
            key = self._advance().value
            self._expect(TokenType.COLON)
            value = self._parse_expression()
            node.children.append(ASTNode('KeyValue', value=key, children=[value]))
            if self._current().type == TokenType.COMMA:
                self._advance()
        self._expect(TokenType.RBRACE)
        return node

    def _parse_dict_literal(self):
        """Parse dict literal: { "key": expr, ... } or { key: expr, ... }"""
        line = self._current().line
        self._advance()  # consume {
        pairs = []
        if self._current().type != TokenType.RBRACE:
            key = self._parse_expression()
            self._expect(TokenType.COLON)
            value = self._parse_expression()
            pairs.append((key, value))
            while self._current().type == TokenType.COMMA:
                self._advance()
                key = self._parse_expression()
                self._expect(TokenType.COLON)
                value = self._parse_expression()
                pairs.append((key, value))
        self._expect(TokenType.RBRACE)
        return ASTNode('DictLiteral', children=pairs, line=line)

    def _parse_list(self):
        node = ASTNode('List', line=self._current().line)
        self._expect(TokenType.LBRACKET)
        while self._current().type != TokenType.RBRACKET:
            node.children.append(self._parse_expression())
            if self._current().type == TokenType.COMMA:
                self._advance()
        self._expect(TokenType.RBRACKET)
        return node


class CodeGenerator:
    def __init__(self):
        self.instructions = []
        self.constants = []
        self.variables = {}
        self.functions = {}
        self.function_params = {}
        self.label_counter = 0
        self.loop_label_stack = []
        self.current_line = 0

    def generate(self, ast: ASTNode) -> Dict:
        self._gen_node(ast)
        return {
            'version': '3.0',
            'qbc_version': '1.0',
            'constants': self.constants,
            'variables': list(self.variables.keys()),
            'functions': self.functions,
            'function_params': self.function_params,
            'instructions': self.instructions
        }

    def _new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"

    def _emit_label(self, label_name):
        """Emit a label marker for jump targets"""
        self.instructions.append({'op': 'LABEL', 'name': label_name, 'code': OpCode.LABEL.value, 'operand': label_name, 'line': 0})


    def _add_const(self, value) -> int:
        if value not in self.constants:
            self.constants.append(value)
        return self.constants.index(value)

    def _emit(self, opcode: OpCode, operand=None, line=0):
        self.instructions.append({
            'op': opcode.name,
            'code': opcode.value,
            'operand': operand,
            'line': line
        })

    def _gen_node(self, node: ASTNode):
        if node is None:
            return

        self.current_line = node.line

        if node.type == 'Program':
            for child in node.children:
                self._gen_node(child)
            self._emit(OpCode.HALT)

        elif node.type == 'Config':
            self._emit(OpCode.NOP, line=node.line)

        elif node.type == 'TypeDef':
            idx = self._add_const(node.value)
            self._emit(OpCode.TYPE_DEF, idx, node.line)
            for child in node.children:
                if child.type == 'Field':
                    field_idx = self._add_const(child.value)
                    self._emit(OpCode.LOAD_CONST, field_idx, child.line)

        elif node.type == 'Function':
            self.functions[node.value] = len(self.instructions)
            param_names = []
            for child in node.children:
                if child.type == 'Param':
                    pname = child.value.split(':')[0]
                    param_names.append(pname)
                    self.variables[pname] = len(self.variables)
                elif child.type == 'Block':
                    self._gen_node(child)
                elif child.type != 'ReturnType':
                    self._gen_node(child)
            self.function_params[node.value] = param_names
            self._emit(OpCode.RETURN)

        elif node.type == 'Block':
            for child in node.children:
                self._gen_node(child)

        elif node.type == 'Let':
            self.variables[node.value] = len(self.variables)
            self._gen_node(node.children[0])
            self._emit(OpCode.STORE_VAR, node.value, node.line)

        elif node.type == 'CompoundAssign':
            self._emit(OpCode.LOAD_VAR, node.value, node.line)
            self._gen_node(node.children[0])
            op_map = {'升': OpCode.ADD, '降': OpCode.SUB, '乘': OpCode.MUL, '除': OpCode.DIV}
            self._emit(op_map.get(node.assign_op, OpCode.ADD), None, node.line)
            self._emit(OpCode.STORE_VAR, node.value, node.line)
        elif node.type == 'Return':
            self._gen_node(node.children[0])
            self._emit(OpCode.RETURN, line=node.line)

        elif node.type == 'Entangle':
            targets = []
            for child in node.children:
                if child.type == 'NumberLit':
                    targets.append(str(int(child.value)))
            entangle_str = ' '.join(targets) if targets else '0 1'
            self._emit(OpCode.QUANTUM_ENTANGLE, entangle_str, node.line)

        elif node.type == 'Measure':
            if node.children:
                child = node.children[0]
                if child.type == 'NumberLit':
                    self._emit(OpCode.QUANTUM_MEASURE, int(child.value), node.line)
                else:
                    self._emit(OpCode.QUANTUM_MEASURE, 0, node.line)
            else:
                self._emit(OpCode.QUANTUM_MEASURE, 0, node.line)

        elif node.type == 'QuantumGate':
            gate_name = node.value
            targets = []
            for child in node.children:
                if child.type == 'NumberLit':
                    targets.append(child.value)
                elif child.type == 'Identifier':
                    targets.append(child.value)
            gate_str = gate_name + ' ' + ' '.join(str(t) for t in targets)
            self._emit(OpCode.QUANTUM_GATE, gate_str.strip(), node.line)
        elif node.type == 'Log':
            self._gen_node(node.children[0])
            self._emit(OpCode.LOG, line=node.line)

        elif node.type == 'BuiltinCall':
            for child in node.children:
                self._gen_node(child)
            self._emit(OpCode.BUILTIN_CALL, node.value, node.line)
        elif node.type == 'Switch':
            # Evaluate match expression
            self._gen_node(node.children[0])
            match_var = f'_match_{node.line}'
            self._emit(OpCode.STORE_VAR, match_var, node.line)
            end_label = f'_switch_end_{node.line}'
            default_label = f'_default_{node.line}'
            for i, child in enumerate(node.children[1:]):
                if child.type == 'Case':
                    case_label = f'_case_{node.line}_{i}'
                    self.instructions.append({'op': 'LABEL', 'name': case_label})
                    self._emit(OpCode.LOAD_VAR, match_var, child.line)
                    self._gen_node(child.children[0])  # case value
                    self._emit(OpCode.EQ, None, child.line)
                    next_i = i + 1
                    # Find next case index (skip Default nodes)
                    remaining = node.children[1:][next_i:]
                    found_case = False
                    for j, nxt in enumerate(remaining):
                        if nxt.type == 'Case':
                            next_label = f'_case_{node.line}_{next_i + j}'
                            found_case = True
                            break
                    if not found_case:
                        next_label = default_label
                    self._emit(OpCode.JUMP_IF_FALSE, next_label, child.line)
                    self._gen_node(child.children[1])  # case body
                    self._emit(OpCode.JUMP, end_label, child.line)
                elif child.type == 'Default':
                    self.instructions.append({'op': 'LABEL', 'name': default_label})
                    self._gen_node(child.children[0])
            self.instructions.append({'op': 'LABEL', 'name': end_label})
        elif node.type == 'If':
            else_label = self._new_label()
            end_label = self._new_label()
            self._gen_node(node.children[0])  # condition
            self._emit(OpCode.JUMP_IF_FALSE, else_label, node.line)
            self._gen_node(node.children[1])  # if body
            self._emit(OpCode.JUMP, end_label, node.line)
            # Else label
            self.instructions.append({'op': 'LABEL', 'name': else_label})
            if len(node.children) > 2:
                # Handle elif chain
                # children[2..n] are elif If nodes or a final else Block
                # If only children[2] exists, it's a single else/elif
                if len(node.children) == 3:
                    # Single else or nested elif-with-else
                    self._gen_node(node.children[2])
                else:
                    # Multiple elif nodes without else at the end
                    # Generate each elif inline
                    for i in range(2, len(node.children)):
                        child = node.children[i]
                        child_else = self._new_label()
                        self._gen_node(child.children[0])  # elif condition
                        self._emit(OpCode.JUMP_IF_FALSE, child_else, child.line)
                        self._gen_node(child.children[1])  # elif body
                        self._emit(OpCode.JUMP, end_label, child.line)
                        self.instructions.append({'op': 'LABEL', 'name': child_else})
            # End label
            self.instructions.append({"op": "LABEL", "name": end_label})

        elif node.type == 'For':
            start_label = self._new_label()
            end_label = self._new_label()
            range_node = node.children[0] if node.children else None
            if range_node and (range_node.type == 'Range' or (range_node.type == 'Call' and range_node.value == '范围')):
                self._gen_node(range_node.children[0])
                self._emit(OpCode.STORE_VAR, node.value, node.line)
                self._gen_node(range_node.children[1])
                self._emit(OpCode.STORE_VAR, f'_for_end_{node.value}', node.line)
                self.instructions.append({'op': 'LABEL', 'name': start_label})
                self._emit(OpCode.LOAD_VAR, node.value, node.line)
                self._emit(OpCode.LOAD_VAR, f'_for_end_{node.value}', node.line)
                self._emit(OpCode.LT, None, node.line)
                self._emit(OpCode.JUMP_IF_FALSE, end_label, node.line)
                continue_label = self._new_label()
                self.loop_label_stack.append((continue_label, end_label))
                self._gen_node(node.children[1])
                self.instructions.append({'op': 'LABEL', 'name': continue_label})
                self._emit(OpCode.LOAD_VAR, node.value, node.line)
                # Use step from Range if available, else default 1
                if (range_node.type == 'Range' or range_node.type == 'Call') and len(range_node.children) > 2:
                    self._gen_node(range_node.children[2])
                else:
                    step_idx = self._add_const(1)
                    self._emit(OpCode.LOAD_CONST, step_idx, node.line)
                self._emit(OpCode.ADD, None, node.line)
                self._emit(OpCode.STORE_VAR, node.value, node.line)
                self._emit(OpCode.JUMP, start_label, node.line)
                self.instructions.append({'op': 'LABEL', 'name': end_label})
                self.loop_label_stack.pop()
            else:
                # Array iteration: 循环 x 在 arr { ... }
                iter_arr = f'_for_arr_{node.value}'
                iter_idx = f'_for_idx_{node.value}'
                self._gen_node(range_node)  # push arr
                self._emit(OpCode.STORE_VAR, iter_arr, node.line)
                zero_idx = self._add_const(0)
                self._emit(OpCode.LOAD_CONST, zero_idx, node.line)
                self._emit(OpCode.STORE_VAR, iter_idx, node.line)
                # Store arr length as end
                self._emit(OpCode.LOAD_VAR, iter_arr, node.line)
                self._emit(OpCode.BUILTIN_CALL, '长度', node.line)
                self._emit(OpCode.STORE_VAR, f'_for_end_{node.value}', node.line)
                # Init loop var to arr[0]
                self._emit(OpCode.LOAD_VAR, iter_arr, node.line)
                self._emit(OpCode.LOAD_VAR, iter_idx, node.line)
                self._emit(OpCode.INDEX_ACCESS, None, node.line)
                self._emit(OpCode.STORE_VAR, node.value, node.line)
                self.instructions.append({'op': 'LABEL', 'name': start_label})
                # Check idx < length
                self._emit(OpCode.LOAD_VAR, iter_idx, node.line)
                self._emit(OpCode.LOAD_VAR, f'_for_end_{node.value}', node.line)
                self._emit(OpCode.LT, None, node.line)
                self._emit(OpCode.JUMP_IF_FALSE, end_label, node.line)
                continue_label_fe = self._new_label()
                self.loop_label_stack.append((continue_label_fe, end_label))
                # Body
                self._gen_node(node.children[1])
                self.instructions.append({'op': 'LABEL', 'name': continue_label_fe})
                # Increment idx and update loop var
                self._emit(OpCode.LOAD_VAR, iter_idx, node.line)
                one_idx = self._add_const(1)
                self._emit(OpCode.LOAD_CONST, one_idx, node.line)
                self._emit(OpCode.ADD, None, node.line)
                self._emit(OpCode.STORE_VAR, iter_idx, node.line)
                # Update x = arr[idx]
                self._emit(OpCode.LOAD_VAR, iter_arr, node.line)
                self._emit(OpCode.LOAD_VAR, iter_idx, node.line)
                self._emit(OpCode.INDEX_ACCESS, None, node.line)
                self._emit(OpCode.STORE_VAR, node.value, node.line)
                self._emit(OpCode.JUMP, start_label, node.line)
                self.instructions.append({'op': 'LABEL', 'name': end_label})
                self.loop_label_stack.pop()
        elif node.type == 'While':
            start_label = self._new_label()
            end_label = self._new_label()
            self.loop_label_stack.append((start_label, end_label))
            self.instructions.append({'op': 'LABEL', 'name': start_label})
            # Evaluate condition
            self._gen_node(node.children[0])
            self._emit(OpCode.JUMP_IF_FALSE, end_label, node.line)
            # Body
            self._gen_node(node.children[1])
            self._emit(OpCode.JUMP, start_label, node.line)
            self.instructions.append({'op': 'LABEL', 'name': end_label})
            self.loop_label_stack.pop()
        elif node.type == 'Break':
            if self.loop_label_stack:
                _, end_label = self.loop_label_stack[-1]
                self._emit(OpCode.JUMP, end_label, node.line)
        elif node.type == 'GlobalDecl':
            self._emit(OpCode.GLOBAL_DECL, node.value, node.line)
        elif node.type == 'Continue':
            if self.loop_label_stack:
                start_label, _ = self.loop_label_stack[-1]
                self._emit(OpCode.JUMP, start_label, node.line)
        elif node.type == 'Throw':
            self._gen_node(node.children[0])  # exception value
            self._emit(OpCode.THROW, None, node.line)
        elif node.type == 'BinaryOp':
            self._gen_node(node.children[0])
            self._gen_node(node.children[1])
            op_map = {
                '+': OpCode.ADD, '-': OpCode.SUB,
                '*': OpCode.MUL, '/': OpCode.DIV, '%': OpCode.MOD,
                '==': OpCode.EQ, '!=': OpCode.NEQ,
                '<': OpCode.LT, '>': OpCode.GT,
                '<=': OpCode.LTE, '>=': OpCode.GTE,
                '且': OpCode.LOGICAL_AND, '或': OpCode.LOGICAL_OR,
            }
            self._emit(op_map.get(node.value, OpCode.NOP), line=node.line)

        elif node.type == 'UnaryMinus':
            zero_idx = self._add_const(0)
            self._emit(OpCode.LOAD_CONST, zero_idx, node.line)
            self._gen_node(node.children[0])
            self._emit(OpCode.SUB, None, node.line)
        elif node.type == 'Ternary':
            # condition ? true_expr : false_expr
            false_label = self._new_label()
            end_label = self._new_label()
            self._gen_node(node.children[0])  # condition
            self._emit(OpCode.JUMP_IF_FALSE, false_label, node.line)
            self._gen_node(node.children[1])  # true_expr
            self._emit(OpCode.JUMP, end_label, node.line)
            self._emit(OpCode.LABEL, false_label, node.line)
            self._gen_node(node.children[2])  # false_expr
            self._emit(OpCode.LABEL, end_label, node.line)
        elif node.type == 'UnaryNot':
            self._gen_node(node.children[0])
            self._emit(OpCode.UNARY_NOT, None, node.line)
        elif node.type == 'NumberLit':
            idx = self._add_const(float(node.value) if '.' in node.value else int(node.value))
            self._emit(OpCode.LOAD_CONST, idx, node.line)

        elif node.type == 'NullLit':
            none_idx = self._add_const(None)
            self._emit(OpCode.LOAD_CONST, none_idx, node.line)
        elif node.type == 'BoolLit':
            idx = self._add_const(1 if node.value == 'true' else 0)
            self._emit(OpCode.LOAD_CONST, idx, node.line)
        elif node.type == 'StringLit':
            idx = self._add_const(node.value)
            self._emit(OpCode.LOAD_CONST, idx, node.line)
        elif node.type == 'List':
            # Build list: push all elements then BUILD_LIST with count
            for child in node.children:
                self._gen_node(child)
            self._emit(OpCode.BUILD_LIST, len(node.children), node.line)
        elif node.type == 'DictLiteral':
            # Build dict: push key-value pairs then BUILD_DICT with pair count
            for key_node, val_node in node.children:
                self._gen_node(key_node)
                self._gen_node(val_node)
            self._emit(OpCode.BUILD_DICT, len(node.children), node.line)
        elif node.type == 'IndexAccess':
            # Push variable value, then push index
            self._gen_node(node.children[0])  # the array variable
            self._gen_node(node.children[1])  # the index
            self._emit(OpCode.INDEX_ACCESS, None, node.line)
        elif node.type == 'SliceAccess':
            # Push array, start, end then SLICE_ACCESS
            self._gen_node(node.children[0])  # the array/string
            self._gen_node(node.children[1])  # start
            self._gen_node(node.children[2])  # end
            self._emit(OpCode.SLICE_ACCESS, None, node.line)
        elif node.type == 'IndexAssign':
            # a[i] = expr → push array/dict, index, value, INDEX_ASSIGN
            if node.value is not None:
                # Simple: d[key] = val
                self._emit(OpCode.LOAD_VAR, node.value, node.line)
                self._gen_node(node.children[0])  # index
                self._gen_node(node.children[1])  # value
            else:
                # Complex: self.data[key] = val
                self._gen_node(node.children[0])  # target expr (pushes dict)
                self._gen_node(node.children[1])  # index
                self._gen_node(node.children[2])  # value
            self._emit(OpCode.INDEX_ASSIGN, None, node.line)
        elif node.type == 'Assign':
            # x = expr → generate value, then STORE_VAR
            self._gen_node(node.children[0])
            self._emit(OpCode.STORE_VAR, node.value, node.line)
        elif node.type == 'FieldAssign':
            # q.field = val → load obj, load value, STORE_FIELD
            self._gen_node(node.children[0])  # object (push dict)
            self._gen_node(node.children[1])  # value (push value)
            self._emit(OpCode.STORE_FIELD, node.value, node.line)  # field name
        elif node.type == 'Identifier':
            self._emit(OpCode.LOAD_VAR, node.value, node.line)

        elif node.type == 'Call':
            for arg in node.children:
                self._gen_node(arg)
            self._emit(OpCode.CALL, node.value, node.line)

        elif node.type == 'FieldAccess':
            self._gen_node(node.children[0])
            self._emit(OpCode.LOAD_FIELD, node.value, node.line)

        elif node.type == 'MethodCall':
            # obj.method(args) → LOAD obj + LOAD args + METHOD_CALL
            self._gen_node(node.children[0])  # push obj (will become self)
            for arg in node.children[1:]:
                self._gen_node(arg)  # push args
            n_args = len(node.children) - 1  # number of explicit args (not counting self)
            self._emit(OpCode.METHOD_CALL, (node.value, n_args), node.line)

        elif node.type == 'List':
            for child in node.children:
                self._gen_node(child)
            self._emit(OpCode.QUANTUM_INIT, len(node.children), node.line)

        elif node.type == 'QuantumProgram':
            # Simple format: inline quantum instructions
            if node.value == 'inline_quantum':
                for child in node.children:
                    if child.type == 'QuantumInit':
                        self._emit(OpCode.QUANTUM_INIT, child.value, child.line)
                    elif child.type == 'QuantumGate':
                        self._emit(OpCode.QUANTUM_GATE, child.value, child.line)
                    elif child.type == 'QuantumEntangle':
                        self._emit(OpCode.QUANTUM_ENTANGLE, child.value, child.line)
            else:
                # Full format: setup/run sections
                self._emit(OpCode.QUANTUM_INIT, line=node.line)
                for child in node.children:
                    self._gen_node(child)
                    if child.type == 'Section':
                        for section_child in child.children:
                            self._gen_node(section_child)
        elif node.type == 'QuantumInterface':
            name_idx = self._add_const(node.value)
            self._emit(OpCode.INTERFACE_DEF, name_idx, node.line)
            for child in node.children:
                self._gen_node(child)
        elif node.type == 'QuantumClass':
            name_idx = self._add_const(node.value)
            self._emit(OpCode.CLASS_DEF, name_idx, node.line)
            for child in node.children:
                self._gen_node(child)
        elif node.type == 'Try':
            catch_label = self._new_label()
            end_label = self._new_label()
            self._emit(OpCode.PUSH_TRY, catch_label, node.line)
            self._gen_node(node.children[0])  # try body
            self._emit(OpCode.POP_TRY, None, node.line)
            self._emit(OpCode.JUMP, end_label, node.line)
            # catch_label:
            self._emit_label(catch_label)
            # Bind exception value to catch variable
            if node.value:  # catch variable name (e.g., 'e')
                self._emit(OpCode.STORE_VAR, node.value, node.line)
            elif self.stack:  # no variable, just pop
                pass  # value stays on stack
            if len(node.children) > 1:
                self._gen_node(node.children[1])  # catch body
            # end_label:
            self._emit_label(end_label)
        elif node.type == 'Assert':
            self._gen_node(node.children[0])
            self._emit(OpCode.ASSERT, len(node.children), node.line)
        elif node.type == 'Import':
            mod_idx = self._add_const(node.value)
            self._emit(OpCode.IMPORT, mod_idx, node.line)
            for child in node.children:
                self._gen_node(child)
        elif node.type == 'Export':
            name_idx = self._add_const(node.value)
            self._emit(OpCode.EXPORT, name_idx, node.line)
            for child in node.children:
                self._gen_node(child)
        elif node.type == 'QuantumEnum':
            # quantum_enum → create dict with values mapped to indices
            enum_name = node.value
            self.variables[enum_name] = len(self.variables)
            # Build enum dict: {value_name: index, ...}
            enum_dict = {}
            for idx, child in enumerate(node.children):
                enum_dict[child.value] = idx
            dict_idx = self._add_const(enum_dict)
            self._emit(OpCode.LOAD_CONST, dict_idx, node.line)
            self._emit(OpCode.STORE_VAR, enum_name, node.line)

# === 编译主流程 ===
def compile_qentl(source: str) -> Dict:
    """编译 QEntL 源码为 QBC 字节码"""
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    codegen = CodeGenerator()
    qbc = codegen.generate(ast)

    # Auto-detect qubit count from instructions
    max_qubit = 1
    for instr in qbc.get('instructions', []):
        op = instr.get('op', '')
        operand = instr.get('operand')
        if op == 'QUANTUM_GATE' and isinstance(operand, str):
            parts = operand.split()
            for p in parts[1:]:
                try: max_qubit = max(max_qubit, int(p))
                except: pass
        elif op == 'QUANTUM_MEASURE' and isinstance(operand, int):
            max_qubit = max(max_qubit, operand)
        elif op == 'QUANTUM_ENTANGLE' and isinstance(operand, str):
            for p in operand.split():
                try: max_qubit = max(max_qubit, int(p))
                except: pass
    n_qubits = max_qubit + 1
    # Patch QUANTUM_INIT instruction
    for instr in qbc.get('instructions', []):
        if instr.get('op') == 'QUANTUM_INIT':
            instr['operand'] = n_qubits
            break
    qbc['n_qubits'] = n_qubits
    return qbc

def compile_file(input_path: str, output_path: str = None):
    """编译 .qentl 文件为 .qbc 文件"""
    with open(input_path, 'r', encoding='utf-8') as f:
        source = f.read()

    qbc = compile_qentl(source)

    if output_path is None:
        output_path = input_path.replace('.qentl', '.qbc')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qbc, f, ensure_ascii=False, indent=2)

    print(f"✅ 编译完成: {input_path} → {output_path}")
    print(f"   常量: {len(qbc['constants'])}")
    print(f"   变量: {len(qbc['variables'])}")
    print(f"   函数: {len(qbc['functions'])}")
    print(f"   指令: {len(qbc['instructions'])}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 qentl_compiler_v3.py <input.qentl> [output.qbc]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    compile_file(input_file, output_file)
