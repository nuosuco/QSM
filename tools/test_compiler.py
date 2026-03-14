#!/usr/bin/env python3
"""
QEntL编译器单元测试
"""

import sys
import unittest
sys.path.insert(0, '/root/QSM/tools')

from compiler_verifier import Lexer, Token, TokenType
from qentl_parser import Parser, NodeType

class TestLexer(unittest.TestCase):
    """词法分析器测试"""
    
    def test_keywords(self):
        """测试关键字识别"""
        code = "配置 类型 函数 返回 如果 否则 循环"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 8)  # 7个关键字 + EOF
        for t in tokens[:-1]:
            self.assertEqual(t.type, TokenType.KEYWORD)
    
    def test_identifiers(self):
        """测试标识符识别"""
        code = "用户名 名称 年龄"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 4)  # 3个标识符 + EOF
        
    def test_operators(self):
        """测试操作符识别"""
        code = "+ - * / == !="
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 7)  # 6个操作符 + EOF
        for t in tokens[:-1]:
            self.assertEqual(t.type, TokenType.OPERATOR)
    
    def test_literals(self):
        """测试字面量识别"""
        code = '"测试" 123 true false'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 5)  # 4个字面量 + EOF

class TestParser(unittest.TestCase):
    """语法分析器测试"""
    
    def test_config_block(self):
        """测试配置块解析"""
        code = '配置 { 版本: "1.0.0" }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].node_type, NodeType.CONFIG_BLOCK)
    
    def test_function_def(self):
        """测试函数定义解析"""
        code = '函数 测试() { 返回 1 }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertGreater(len(ast.children), 0)
    
    def test_type_def(self):
        """测试类型定义解析"""
        code = '类型 用户 { 名称: 字符串 }'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertEqual(len(ast.children), 1)
        self.assertEqual(ast.children[0].node_type, NodeType.TYPE_DEF)

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_compile(self):
        """测试完整编译流程"""
        code = '''
配置 {
    版本: "1.0.0"
}

函数 加法(a: 整数, b: 整数) {
    返回 a + b
}
'''
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        self.assertGreater(len(tokens), 0)
        
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertIsNotNone(ast)

if __name__ == '__main__':
    # 运行测试
    print("=" * 50)
    print("QEntL编译器单元测试")
    print("=" * 50)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestLexer))
    suite.addTests(loader.loadTestsFromTestCase(TestParser))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print(f"测试结果: {result.testsRun}个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 50)
