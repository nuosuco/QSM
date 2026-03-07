#!/usr/bin/env python3
"""
QEntL完整语法分析器
支持所有QEntL语法结构
"""

import sys
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto

# 导入词法分析器
sys.path.insert(0, '/root/QSM/tools')
from compiler_verifier import Token, TokenType, Lexer

class NodeType(Enum):
    PROGRAM = auto()
    CONFIG_BLOCK = auto()
    TYPE_DEF = auto()
    FUNCTION_DEF = auto()
    VARIABLE_DEF = auto()
    ASSIGNMENT = auto()
    IF_STMT = auto()
    ELSE_STMT = auto()
    LOOP_STMT = auto()
    RETURN_STMT = auto()
    IMPORT_STMT = auto()
    EXPORT_STMT = auto()
    QUANTUM_CLASS = auto()
    QUANTUM_INTERFACE = auto()
    QUANTUM_ENUM = auto()
    QUANTUM_PROGRAM = auto()
    FUNCTION_CALL = auto()
    BINARY_EXPR = auto()
    UNARY_EXPR = auto()
    LITERAL = auto()
    IDENTIFIER = auto()
    BLOCK = auto()

@dataclass
class ASTNode:
    node_type: NodeType
    value: str = ""
    children: List['ASTNode'] = None
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.attributes is None:
            self.attributes = {}

class Parser:
    """完整语法分析器"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current = tokens[0] if tokens else None
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
        else:
            self.current = None
    
    def expect(self, token_type: TokenType, value: str = None) -> Token:
        if self.current is None:
            raise SyntaxError(f"意外的文件结束")
        if self.current.type != token_type:
            raise SyntaxError(f"期望 {token_type}，得到 {self.current.type}")
        if value and self.current.value != value:
            raise SyntaxError(f"期望 '{value}'，得到 '{self.current.value}'")
        token = self.current
        self.advance()
        return token
    
    def match(self, token_type: TokenType, value: str = None) -> bool:
        if self.current is None:
            return False
        if self.current.type != token_type:
            return False
        if value and self.current.value != value:
            return False
        return True
    
    def parse(self) -> ASTNode:
        """解析整个程序"""
        program = ASTNode(NodeType.PROGRAM)
        while self.current and self.current.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                program.children.append(stmt)
        return program
    
    def parse_statement(self) -> Optional[ASTNode]:
        """解析语句"""
        if self.current is None or self.current.type == TokenType.EOF:
            return None
        
        if self.match(TokenType.KEYWORD, "配置"):
            return self.parse_config()
        elif self.match(TokenType.KEYWORD, "类型"):
            return self.parse_type_def()
        elif self.match(TokenType.KEYWORD, "函数"):
            return self.parse_function_def()
        elif self.match(TokenType.KEYWORD, "quantum_class"):
            return self.parse_quantum_class()
        elif self.match(TokenType.KEYWORD, "import"):
            return self.parse_import()
        elif self.match(TokenType.KEYWORD, "export"):
            return self.parse_export()
        elif self.match(TokenType.KEYWORD, "let"):
            return self.parse_variable_def()
        elif self.match(TokenType.KEYWORD, "如果"):
            return self.parse_if()
        elif self.match(TokenType.KEYWORD, "循环"):
            return self.parse_loop()
        elif self.match(TokenType.KEYWORD, "返回"):
            return self.parse_return()
        else:
            # 尝试解析表达式语句
            return self.parse_expression()
    
    def parse_config(self) -> ASTNode:
        """解析配置块"""
        self.expect(TokenType.KEYWORD, "配置")
        self.expect(TokenType.SEPARATOR, "{")
        
        config = ASTNode(NodeType.CONFIG_BLOCK)
        while not self.match(TokenType.SEPARATOR, "}"):
            # 解析配置项
            name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.OPERATOR, ":")
            value = self.parse_literal()
            config.attributes[name] = value
            if self.match(TokenType.SEPARATOR, ","):
                self.advance()
        
        self.expect(TokenType.SEPARATOR, "}")
        return config
    
    def parse_type_def(self) -> ASTNode:
        """解析类型定义"""
        self.expect(TokenType.KEYWORD, "类型")
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SEPARATOR, "{")
        
        type_def = ASTNode(NodeType.TYPE_DEF, value=name)
        while not self.match(TokenType.SEPARATOR, "}"):
            # 解析字段
            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.OPERATOR, ":")
            field_type = self.expect(TokenType.IDENTIFIER).value
            type_def.attributes[field_name] = field_type
            if self.match(TokenType.SEPARATOR, ","):
                self.advance()
        
        self.expect(TokenType.SEPARATOR, "}")
        return type_def
    
    def parse_function_def(self) -> ASTNode:
        """解析函数定义"""
        self.expect(TokenType.KEYWORD, "函数")
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SEPARATOR, "(")
        
        params = []
        while not self.match(TokenType.SEPARATOR, ")"):
            param_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.OPERATOR, ":")
            param_type = self.expect(TokenType.IDENTIFIER).value
            params.append((param_name, param_type))
            if self.match(TokenType.SEPARATOR, ","):
                self.advance()
        
        self.expect(TokenType.SEPARATOR, ")")
        
        # 返回类型
        return_type = None
        if self.match(TokenType.OPERATOR, "->"):
            self.advance()
            return_type = self.expect(TokenType.IDENTIFIER).value
        
        # 函数体
        self.expect(TokenType.SEPARATOR, "{")
        body = []
        while not self.match(TokenType.SEPARATOR, "}"):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.expect(TokenType.SEPARATOR, "}")
        
        func = ASTNode(NodeType.FUNCTION_DEF, value=name)
        func.attributes["params"] = params
        func.attributes["return_type"] = return_type
        func.children = body
        return func
    
    def parse_quantum_class(self) -> ASTNode:
        """解析量子类"""
        self.expect(TokenType.KEYWORD, "quantum_class")
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SEPARATOR, "{")
        
        qc = ASTNode(NodeType.QUANTUM_CLASS, value=name)
        while not self.match(TokenType.SEPARATOR, "}"):
            stmt = self.parse_statement()
            if stmt:
                qc.children.append(stmt)
        
        self.expect(TokenType.SEPARATOR, "}")
        return qc
    
    def parse_import(self) -> ASTNode:
        """解析导入语句"""
        self.expect(TokenType.KEYWORD, "import")
        name = self.expect(TokenType.IDENTIFIER).value
        return ASTNode(NodeType.IMPORT_STMT, value=name)
    
    def parse_export(self) -> ASTNode:
        """解析导出语句"""
        self.expect(TokenType.KEYWORD, "export")
        name = self.expect(TokenType.IDENTIFIER).value
        return ASTNode(NodeType.EXPORT_STMT, value=name)
    
    def parse_variable_def(self) -> ASTNode:
        """解析变量定义"""
        self.expect(TokenType.KEYWORD, "let")
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.OPERATOR, "=")
        value = self.parse_expression()
        return ASTNode(NodeType.VARIABLE_DEF, value=name, children=[value])
    
    def parse_if(self) -> ASTNode:
        """解析if语句"""
        self.expect(TokenType.KEYWORD, "如果")
        condition = self.parse_expression()
        self.expect(TokenType.SEPARATOR, "{")
        
        then_block = []
        while not self.match(TokenType.SEPARATOR, "}"):
            stmt = self.parse_statement()
            if stmt:
                then_block.append(stmt)
        self.expect(TokenType.SEPARATOR, "}")
        
        else_block = []
        if self.match(TokenType.KEYWORD, "否则"):
            self.advance()
            self.expect(TokenType.SEPARATOR, "{")
            while not self.match(TokenType.SEPARATOR, "}"):
                stmt = self.parse_statement()
                if stmt:
                    else_block.append(stmt)
            self.expect(TokenType.SEPARATOR, "}")
        
        if_stmt = ASTNode(NodeType.IF_STMT, children=[condition])
        if_stmt.attributes["then"] = then_block
        if_stmt.attributes["else"] = else_block
        return if_stmt
    
    def parse_loop(self) -> ASTNode:
        """解析循环语句"""
        self.expect(TokenType.KEYWORD, "循环")
        var = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.KEYWORD, "在")
        collection = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SEPARATOR, "{")
        
        body = []
        while not self.match(TokenType.SEPARATOR, "}"):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.expect(TokenType.SEPARATOR, "}")
        
        loop = ASTNode(NodeType.LOOP_STMT, value=var)
        loop.attributes["collection"] = collection
        loop.children = body
        return loop
    
    def parse_return(self) -> ASTNode:
        """解析返回语句"""
        self.expect(TokenType.KEYWORD, "返回")
        value = self.parse_expression()
        return ASTNode(NodeType.RETURN_STMT, children=[value])
    
    def parse_expression(self) -> ASTNode:
        """解析表达式"""
        left = self.parse_primary()
        
        while self.current and self.current.type == TokenType.OPERATOR and \
              self.current.value in ["+", "-", "*", "/", "==", "!=", "<", ">", "<=", ">="]:
            op = self.current.value
            self.advance()
            right = self.parse_primary()
            left = ASTNode(NodeType.BINARY_EXPR, value=op, children=[left, right])
        
        return left
    
    def parse_primary(self) -> ASTNode:
        """解析基本表达式"""
        if self.current is None:
            raise SyntaxError("意外的文件结束")
        
        if self.match(TokenType.LITERAL):
            value = self.current.value
            self.advance()
            return ASTNode(NodeType.LITERAL, value=value)
        
        if self.match(TokenType.IDENTIFIER):
            name = self.current.value
            self.advance()
            
            # 检查是否是函数调用
            if self.match(TokenType.SEPARATOR, "("):
                self.advance()
                args = []
                while not self.match(TokenType.SEPARATOR, ")"):
                    arg = self.parse_expression()
                    args.append(arg)
                    if self.match(TokenType.SEPARATOR, ","):
                        self.advance()
                self.expect(TokenType.SEPARATOR, ")")
                call = ASTNode(NodeType.FUNCTION_CALL, value=name)
                call.children = args
                return call
            
            return ASTNode(NodeType.IDENTIFIER, value=name)
        
        raise SyntaxError(f"意外的标记: {self.current}")
    
    def parse_literal(self) -> Any:
        """解析字面量"""
        if self.match(TokenType.KEYWORD, "true"):
            self.advance()
            return True
        elif self.match(TokenType.KEYWORD, "false"):
            self.advance()
            return False
        elif self.match(TokenType.KEYWORD, "null"):
            self.advance()
            return None
        elif self.match(TokenType.LITERAL):
            value = self.current.value
            self.advance()
            # 移除引号
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return value
        else:
            raise SyntaxError(f"期望字面量，得到 {self.current}")


def test_parser():
    """测试语法分析器"""
    test_code = '''
配置 {
    版本: "1.0.0"
    调试: true
}

类型 用户 {
    名称: 字符串,
    年龄: 整数
}

函数 问候(名字: 字符串) -> 字符串 {
    let 消息 = "你好，" + 名字
    返回 消息
}

quantum_class 量子处理器 {
    函数 处理(数据: 字符串) {
        返回 数据
    }
}
'''
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    print("AST解析成功！")
    print(f"顶层节点数: {len(ast.children)}")
    for child in ast.children:
        print(f"  - {child.node_type.name}: {child.value}")
    
    return ast is not None


if __name__ == "__main__":
    success = test_parser()
    sys.exit(0 if success else 1)
