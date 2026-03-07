#!/usr/bin/env python3
"""
QEntL编译器命令行入口
"""

import sys
import json
sys.path.insert(0, '/root/QSM/tools')

from compiler_verifier import Lexer
from qentl_parser import Parser
from qentl_codegen import CodeGenerator

def compile_file(filepath):
    """编译QEntL文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    # 词法分析
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    # 语法分析
    parser = Parser(tokens)
    ast = parser.parse()
    
    # 代码生成
    codegen = CodeGenerator()
    bytecode = codegen.generate(ast)
    
    # 输出结果
    print(json.dumps(bytecode, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: qentl_compile.py <file.qentl>")
        sys.exit(1)
    
    compile_file(sys.argv[1])
