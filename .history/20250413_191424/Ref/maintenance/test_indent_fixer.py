#!/usr/bin/env python
# -*- coding: utf-8 -*-

# # 
"""
量子基因编码: QE-TES-9C0CAA6A27CA
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""
测试缩进修复工具的功能

这个模块包含一组测试用例，用于验证缩进修复工具的各种功能，包括：
1. 方法缩进修复
2. 文档字符串缩进修复
3. 条件语句缩进修复
4. 量子基因标记特殊修复
"""

import os
import sys
import unittest
import tempfile
import textwrap
from pathlib import Path

# 导入要测试的模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from maintenance.fix_indent_errors import (
    detect_indentation,
    fix_method_indentation,
    fix_docstring_indentation,
    fix_conditional_indentation,
    fix_quantum_gene_marker,
    fix_elif_indentation,
    fix_indentation_errors
)

class TestIndentationDetection(unittest.TestCase):
    """测试缩进检测功能"""
    
    def test_detect_spaces(self):
        """测试检测空格缩进"""
        content = textwrap.dedent("""\
        def test_function():
            print("Hello")
                print("World")
        """)
        
        char, size = detect_indentation(content)
        self.assertEqual(char, ' ')
        self.assertEqual(size, 4)
    
    def test_detect_tabs(self):
        """测试检测制表符缩进"""
        content = "def test_function():\n\tprint('Hello')\n\t\tprint('World')"
        
        char, size = detect_indentation(content)
        self.assertEqual(char, '\t')
        self.assertEqual(size, 1)
    
    def test_detect_mixed(self):
        """测试混合缩进时返回最常用的缩进类型"""
        content = textwrap.dedent("""\
        def test_function():
            print("Hello")
            print("World")
        class TestClass:
        \tdef method(self):
        \t\tpass
        """)
        
        char, size = detect_indentation(content)
        self.assertEqual(char, ' ')
        self.assertEqual(size, 4)

class TestMethodIndentation(unittest.TestCase):
    """测试方法缩进修复功能"""
    
    def test_fix_method_indentation(self):
        """测试修复类方法缩进"""
        # 错误的缩进
        before = textwrap.dedent("""\
        class TestClass:
          def method1(self):
              print("Hello")
          
          def method2(self):
              print("World")
        """)
        
        # 预期的正确缩进
        expected = textwrap.dedent("""\
        class TestClass:
            def method1(self):
                print("Hello")
            
            def method2(self):
                print("World")
        """)
        
        after = fix_method_indentation(before)
        self.assertEqual(after, expected)
    
    def test_preserve_method_body_indent(self):
        """测试保留方法体相对缩进"""
        # 错误的缩进，但方法体有相对缩进
        before = textwrap.dedent("""\
        class TestClass:
          def method(self):
              print("Line 1")
                  print("Indented line")
              print("Line 3")
        """)
        
        # 预期的正确缩进，保留方法体的相对缩进
        expected = textwrap.dedent("""\
        class TestClass:
            def method(self):
                print("Line 1")
                    print("Indented line")
                print("Line 3")
        """)
        
        after = fix_method_indentation(before)
        self.assertEqual(after, expected)

class TestDocstringIndentation(unittest.TestCase):
    """测试文档字符串缩进修复功能"""
    
    def test_fix_multiline_docstring(self):
        """测试修复多行文档字符串缩进"""
        # 错误的文档字符串缩进
        before = textwrap.dedent('''\
        def test_function():
            """
        This is a docstring with
        incorrect indentation.
            """
            pass
        ''')
        
        # 预期的正确缩进
        expected = textwrap.dedent('''\
        def test_function():
            """
                This is a docstring with
                incorrect indentation.
            """
            pass
        ''')
        
        after = fix_docstring_indentation(before)
        self.assertEqual(after, expected)
    
    def test_preserve_single_line_docstring(self):
        """测试单行文档字符串不会被修改"""
        content = 'def test_function():\n    """This is a single line docstring."""\n    pass'
        
        after = fix_docstring_indentation(content)
        self.assertEqual(after, content)

class TestConditionalIndentation(unittest.TestCase):
    """测试条件语句缩进修复功能"""
    
    def test_fix_if_statement(self):
        """测试修复 if 语句块缩进"""
        # 错误的 if 语句缩进
        before = textwrap.dedent("""\
        def test_function():
            if condition:
            print("Inside if")
                print("Indented inside if")
        """)
        
        # 预期的正确缩进
        expected = textwrap.dedent("""\
        def test_function():
            if condition:
                print("Inside if")
                    print("Indented inside if")
        """)
        
        after = fix_conditional_indentation(before)
        self.assertEqual(after, expected)
    
    def test_fix_for_statement(self):
        """测试修复 for 循环缩进"""
        # 错误的 for 循环缩进
        before = textwrap.dedent("""\
        def test_function():
            for item in items:
            print(item)
        """)
        
        # 预期的正确缩进
        expected = textwrap.dedent("""\
        def test_function():
            for item in items:
                print(item)
        """)
        
        after = fix_conditional_indentation(before)
        self.assertEqual(after, expected)

class TestElifIndentation(unittest.TestCase):
    """测试 elif 语句缩进修复功能"""
    
    def test_fix_elif_indentation(self):
        """测试修复 elif 语句缩进与 if 语句对齐"""
        # 错误的 elif 缩进
        before = textwrap.dedent("""\
        if condition1:
            print("Condition 1")
          elif condition2:
            print("Condition 2")
            print("More in condition 2")
        else:
            print("Default")
        """)
        
        # 预期的正确缩进
        expected = textwrap.dedent("""\
        if condition1:
            print("Condition 1")
        elif condition2:
            print("Condition 2")
            print("More in condition 2")
        else:
            print("Default")
        """)
        
        after = fix_elif_indentation(before)
        self.assertEqual(after, expected)
    
    def test_nested_if_elif(self):
        """测试嵌套的 if-elif 结构"""
        # 嵌套的 if-elif 结构
        before = textwrap.dedent("""\
        if condition1:
            print("Condition 1")
            if nested_condition:
                print("Nested condition")
              elif nested_condition2:
                print("Nested condition 2")
          elif condition2:
            print("Condition 2")
        """)
        
        # 预期的正确缩进
        expected = textwrap.dedent("""\
        if condition1:
            print("Condition 1")
            if nested_condition:
                print("Nested condition")
            elif nested_condition2:
                print("Nested condition 2")
        elif condition2:
            print("Condition 2")
        """)
        
        after = fix_elif_indentation(before)
        self.assertEqual(after, expected)

class TestQuantumGeneMarker(unittest.TestCase):
    """测试量子基因标记特殊修复功能"""
    
    def test_fix_quantum_gene_marker(self):
        """测试修复量子基因标记类中的特殊缩进"""
        # 模拟量子基因标记类的错误缩进
        before = textwrap.dedent("""\
        class RefQuantumGeneMarker:
          def __init__(self, args):
              \"\"\"
              初始化量子基因标记系统
              \"\"\"
              self.args = args
              
              # 定义注释结尾标记
            self.COMMENT_END_MARKERS = {
                'py': ['"""', "'''"],
                'js': ['*/'],
                'html': ['-->'],
                'css': ['*/']
            }
        """)
        
        # 预期的正确缩进
        expected = textwrap.dedent("""\
        class RefQuantumGeneMarker:
            def __init__(self, args):
                \"\"\"
                初始化量子基因标记系统
                \"\"\"
                self.args = args
                
                # 定义注释结尾标记
                self.COMMENT_END_MARKERS = {
                    'py': ['"""', "'''"],
                    'js': ['*/'],
                    'html': ['-->'],
                    'css': ['*/']
                }
        """)
        
        after = fix_quantum_gene_marker(before)
        self.assertEqual(after, expected)

class TestFileOperations(unittest.TestCase):
    """测试文件操作功能"""
    
    def test_fix_file(self):
        """测试修复文件中的缩进错误"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp:
            # 写入错误缩进的内容
            temp.write(textwrap.dedent("""\
            class TestClass:
              def method(self):
                  \"\"\"
                  测试方法
                  \"\"\"
                  print("Hello")
            """).encode('utf-8'))
        
        try:
            # 调用文件修复函数
            result = fix_indentation_errors(temp.name)
            
            # 检查是否成功修复
            self.assertTrue(result)
            
            # 读取修复后的文件
            with open(temp.name, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 验证修复是否正确
            expected = textwrap.dedent("""\
            class TestClass:
                def method(self):
                    \"\"\"
                        测试方法
                    \"\"\"
                    print("Hello")
            """)
            self.assertEqual(content, expected)
        
        finally:
            # 清理临时文件
            os.unlink(temp.name)

def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTest(loader.loadTestsFromTestCase(TestIndentationDetection))
    suite.addTest(loader.loadTestsFromTestCase(TestMethodIndentation))
    suite.addTest(loader.loadTestsFromTestCase(TestDocstringIndentation))
    suite.addTest(loader.loadTestsFromTestCase(TestConditionalIndentation))
    suite.addTest(loader.loadTestsFromTestCase(TestElifIndentation))
    suite.addTest(loader.loadTestsFromTestCase(TestQuantumGeneMarker))
    suite.addTest(loader.loadTestsFromTestCase(TestFileOperations))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 如果有测试失败，返回非零退出码
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests()) 