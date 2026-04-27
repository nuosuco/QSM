#!/usr/bin/env python3
"""
QEntL量子编译器 V3 - 将 .qentl 源码编译为 .qbc 字节码
支持：类型定义、函数声明、量子程序、控制流
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
    LOAD_FIELD = 0x13      # 加载字段
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
    TYPE_CAST = 0x71
    
    # 对象操作
    OBJ_CREATE = 0x80
    OBJ_GET = 0x81
    OBJ_SET = 0x82

# === 词法分析 ===
class TokenType(Enum):
    # 关键字
    CONFIG = '配置'
    TYPE = '类型'
    FUNC = '函数'
    QUANTUM_PROGRAM = 'quantum_program'
    IF = '如果'
    ELSE = '否则'
    ELIF = '否则如果'
    RETURN = '返回'
    LET = 'let'
    FOR = '循环'
    IN = '在'
    WHILE = '当'
    LOG = '日志'
    SETUP = 'setup'
    RUN = 'run'
    
    # 类型关键字
    STRING = '字符串'
    INT = '整数'
    FLOAT = '浮点数'
    BOOL = '布尔'
    QUANTUM = '量子'
    
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
    AND = '且'
    OR = '或'
    NOT = '非'
    
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
            
            # Comments
            if ch == '/' and self.pos + 1 < len(self.source) and self.source[self.pos+1] == '/':
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
                if two == '<=':
                    self._add_token(TokenType.LTE, '<=')
                    self._advance(); self._advance()
                    continue
                if two == '>=':
                    self._add_token(TokenType.GTE, '>=')
                    self._advance(); self._advance()
                    continue
            
            # Single character operators/symbols
            symbol_map = {
                '{': TokenType.LBRACE, '}': TokenType.RBRACE,
                '(': TokenType.LPAREN, ')': TokenType.RPAREN,
                '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
                '.': TokenType.DOT, ',': TokenType.COMMA,
                ':': TokenType.COLON, ';': TokenType.SEMICOLON,
                '=': TokenType.ASSIGN, '+': TokenType.PLUS,
                '-': TokenType.MINUS, '*': TokenType.STAR,
                '/': TokenType.SLASH, '<': TokenType.LT,
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
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos] != '"':
            if self.source[self.pos] == '\n':
                self.line += 1
            self._advance()
        value = self.source[start:self.pos]
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
    
    def _at_end(self) -> bool:
        return self._current().type == TokenType.EOF
    
    def _expect(self, ttype: TokenType) -> Token:
        if self._current().type == ttype:
            return self._advance()
        raise SyntaxError(f"Expected {ttype}, got {self._current().type} ({self._current().value}) at line {self._current().line}")
    
    def _parse_top_level(self):
        t = self._current()
        if t.type == TokenType.CONFIG:
            return self._parse_config()
        elif t.type == TokenType.TYPE:
            return self._parse_type_def()
        elif t.type == TokenType.FUNC:
            return self._parse_function()
        elif t.type == TokenType.QUANTUM_PROGRAM:
            return self._parse_quantum_program()
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
    
    def _parse_function(self):
        node = ASTNode('Function', line=self._current().line)
        self._expect(TokenType.FUNC)
        node.value = self._advance().value  # function name
        self._expect(TokenType.LPAREN)
        # Parameters
        while self._current().type != TokenType.RPAREN:
            pname = self._advance().value
            self._expect(TokenType.COLON)
            ptype = self._advance().value
            node.children.append(ASTNode('Param', value=f"{pname}:{ptype}"))
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
        node.value = self._advance().value  # program name
        self._expect(TokenType.LBRACE)
        # Parse setup/run sections - they use inline function-like syntax
        while self._current().type != TokenType.RBRACE:
            section = self._advance().value  # setup/run
            self._expect(TokenType.COLON)
            # The body can be a function definition or an inline anonymous function
            if self._current().type == TokenType.FUNC:
                # Anonymous function: 函数() { ... } - parse function name as empty, skip parens
                self._advance()  # skip 函数
                self._expect(TokenType.LPAREN)
                self._expect(TokenType.RPAREN)
                body = self._parse_block()
                body.type = 'Function'
                body.value = section  # use section name as function name
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
        elif t.type == TokenType.RETURN:
            return self._parse_return()
        elif t.type == TokenType.LET:
            return self._parse_let()
        elif t.type == TokenType.FOR:
            return self._parse_for()
        elif t.type == TokenType.LOG:
            return self._parse_log()
        elif t.type == TokenType.WHILE:
            return self._parse_while()
        else:
            # Expression statement
            expr = self._parse_expression()
            if self._current().type == TokenType.SEMICOLON:
                self._advance()
            return expr
    
    def _parse_if(self):
        node = ASTNode('If', line=self._current().line)
        self._expect(TokenType.IF)
        node.children.append(self._parse_expression())
        node.children.append(self._parse_block())
        if self._current().type in (TokenType.ELSE, TokenType.ELIF):
            self._advance()
            if self._current().type == TokenType.IF:
                node.children.append(self._parse_if())
            else:
                node.children.append(self._parse_block())
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
        self._expect(TokenType.ASSIGN)
        node.children.append(self._parse_expression())
        return node
    
    def _parse_for(self):
        node = ASTNode('For', line=self._current().line)
        self._expect(TokenType.FOR)
        node.value = self._advance().value  # loop variable
        self._expect(TokenType.IN)
        node.children.append(self._parse_expression())  # range
        node.children.append(self._parse_block())
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
        return self._parse_comparison()
    
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
        left = self._parse_primary()
        while self._current().type in (TokenType.STAR, TokenType.SLASH):
            op = self._advance().value
            right = self._parse_primary()
            left = ASTNode('BinaryOp', value=op, children=[left, right])
        return left
    
    def _parse_primary(self):
        t = self._current()
        if t.type == TokenType.NUMBER_LIT:
            self._advance()
            return ASTNode('NumberLit', value=t.value, line=t.line)
        elif t.type == TokenType.STRING_LIT:
            self._advance()
            return ASTNode('StringLit', value=t.value, line=t.line)
        elif t.type == TokenType.IDENTIFIER:
            self._advance()
            node = ASTNode('Identifier', value=t.value, line=t.line)
            # Check for function call or field access
            if self._current().type == TokenType.LPAREN:
                self._advance()  # (
                args = []
                while self._current().type != TokenType.RPAREN:
                    args.append(self._parse_expression())
                    if self._current().type == TokenType.COMMA:
                        self._advance()
                self._expect(TokenType.RPAREN)
                node = ASTNode('Call', value=t.value, children=args, line=t.line)
            elif self._current().type == TokenType.DOT:
                self._advance()
                field = self._advance().value
                node = ASTNode('FieldAccess', value=field, children=[node], line=t.line)
            return node
        elif t.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr
        elif t.type == TokenType.LBRACKET:
            return self._parse_list()
        elif t.type == TokenType.LBRACE:
            return self._parse_object_literal()
        else:
            self._advance()
            return ASTNode('Unknown', value=t.value, line=t.line)
    
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
    
    def _parse_list(self):
        node = ASTNode('List', line=self._current().line)
        self._expect(TokenType.LBRACKET)
        while self._current().type != TokenType.RBRACKET:
            node.children.append(self._parse_expression())
            if self._current().type == TokenType.COMMA:
                self._advance()
        self._expect(TokenType.RBRACKET)
        return node

# === 代码生成器 (.qentl -> .qbc) ===
class CodeGenerator:
    def __init__(self):
        self.instructions = []
        self.constants = []
        self.variables = {}
        self.functions = {}
        self.label_counter = 0
        self.current_line = 0
    
    def generate(self, ast: ASTNode) -> Dict:
        self._gen_node(ast)
        return {
            'version': '3.0',
            'qbc_version': '1.0',
            'constants': self.constants,
            'variables': list(self.variables.keys()),
            'functions': self.functions,
            'instructions': self.instructions
        }
    
    def _new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"
    
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
            for child in node.children:
                if child.type == 'Param':
                    self.variables[child.value.split(':')[0]] = len(self.variables)
                elif child.type == 'Block':
                    self._gen_node(child)
                elif child.type != 'ReturnType':
                    self._gen_node(child)
            self._emit(OpCode.RETURN)
        
        elif node.type == 'Block':
            for child in node.children:
                self._gen_node(child)
        
        elif node.type == 'Let':
            self.variables[node.value] = len(self.variables)
            self._gen_node(node.children[0])
            self._emit(OpCode.STORE_VAR, node.value, node.line)
        
        elif node.type == 'Return':
            self._gen_node(node.children[0])
            self._emit(OpCode.RETURN, line=node.line)
        
        elif node.type == 'Log':
            self._gen_node(node.children[0])
            self._emit(OpCode.LOG, line=node.line)
        
        elif node.type == 'If':
            else_label = self._new_label()
            end_label = self._new_label()
            self._gen_node(node.children[0])  # condition
            self._emit(OpCode.JUMP_IF_FALSE, else_label, node.line)
            self._gen_node(node.children[1])  # if body
            self._emit(OpCode.JUMP, end_label, node.line)
            # Else label
            self.instructions.append({'op': 'LABEL', 'name': else_label})
            if len(node.children) > 2:  # else body
                self._gen_node(node.children[2])
            # End label
            self.instructions.append({'op': 'LABEL', 'name': end_label})
        
        elif node.type == 'For':
            start_label = self._new_label()
            end_label = self._new_label()
            self._gen_node(node.children[0])  # range
            self._emit(OpCode.LOOP_START, node.value, node.line)
            self.instructions.append({'op': 'LABEL', 'name': start_label})
            self._gen_node(node.children[1])  # body
            self._emit(OpCode.LOOP_END, start_label, node.line)
            self.instructions.append({'op': 'LABEL', 'name': end_label})
        
        elif node.type == 'BinaryOp':
            self._gen_node(node.children[0])
            self._gen_node(node.children[1])
            op_map = {
                '+': OpCode.ADD, '-': OpCode.SUB,
                '*': OpCode.MUL, '/': OpCode.DIV,
                '==': OpCode.EQ, '!=': OpCode.NEQ,
                '<': OpCode.LT, '>': OpCode.GT,
                '<=': OpCode.LTE, '>=': OpCode.GTE,
            }
            self._emit(op_map.get(node.value, OpCode.NOP), line=node.line)
        
        elif node.type == 'NumberLit':
            idx = self._add_const(float(node.value) if '.' in node.value else int(node.value))
            self._emit(OpCode.LOAD_CONST, idx, node.line)
        
        elif node.type == 'StringLit':
            idx = self._add_const(node.value)
            self._emit(OpCode.LOAD_CONST, idx, node.line)
        
        elif node.type == 'Identifier':
            self._emit(OpCode.LOAD_VAR, node.value, node.line)
        
        elif node.type == 'Call':
            for arg in node.children:
                self._gen_node(arg)
            self._emit(OpCode.CALL, node.value, node.line)
        
        elif node.type == 'FieldAccess':
            self._gen_node(node.children[0])
            self._emit(OpCode.LOAD_FIELD, node.value, node.line)
        
        elif node.type == 'List':
            for child in node.children:
                self._gen_node(child)
            self._emit(OpCode.QUANTUM_INIT, len(node.children), node.line)
        
        elif node.type == 'QuantumProgram':
            self._emit(OpCode.QUANTUM_INIT, line=node.line)
            for child in node.children:
                self._gen_node(child)
                # For sections (setup/run), emit the block code directly
                if child.type == 'Section':
                    # The section's child is the function/block
                    for section_child in child.children:
                        self._gen_node(section_child)

# === 编译主流程 ===
def compile_qentl(source: str) -> Dict:
    """编译 QEntL 源码为 QBC 字节码"""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    codegen = CodeGenerator()
    qbc = codegen.generate(ast)
    
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
    return qbc

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 qentl_compiler_v3.py <input.qentl> [output.qbc]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    compile_file(input_file, output_file)
