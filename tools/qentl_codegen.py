#!/usr/bin/env python3
"""
QEntL代码生成器
生成QBC量子字节码
"""

import sys
import json
from typing import List, Dict, Any
sys.path.insert(0, '/root/QSM/tools')
from qentl_parser import Parser, ASTNode, NodeType

class CodeGenerator:
    """代码生成器 - 生成QBC字节码"""
    
    def __init__(self):
        self.instructions = []
        self.constants = []
        self.functions = {}
        self.current_function = None
    
    def generate(self, ast: ASTNode) -> Dict[str, Any]:
        """生成完整字节码"""
        self.instructions = []
        self.constants = []
        
        # 生成头部
        self.emit_header()
        
        # 生成各节点
        for child in ast.children:
            self.generate_node(child)
        
        # 生成尾部
        self.emit_footer()
        
        return {
            "magic": "QBC1",
            "version": "1.0.0",
            "quantum_gene": "QG-COMPILED-20260305",
            "instructions": self.instructions,
            "constants": self.constants,
            "functions": self.functions
        }
    
    def emit_header(self):
        """生成字节码头"""
        self.instructions.append("INIT_QUANTUM")
        self.instructions.append("SET_QUBITS 8")
    
    def emit_footer(self):
        """生成字节码尾"""
        self.instructions.append("HALT")
    
    def emit(self, instruction: str):
        """发射指令"""
        self.instructions.append(instruction)
    
    def generate_node(self, node: ASTNode):
        """生成节点代码"""
        if node.node_type == NodeType.CONFIG_BLOCK:
            self.generate_config(node)
        elif node.node_type == NodeType.TYPE_DEF:
            self.generate_type_def(node)
        elif node.node_type == NodeType.FUNCTION_DEF:
            self.generate_function_def(node)
        elif node.node_type == NodeType.QUANTUM_CLASS:
            self.generate_quantum_class(node)
        elif node.node_type == NodeType.IMPORT_STMT:
            self.generate_import(node)
        elif node.node_type == NodeType.EXPORT_STMT:
            self.generate_export(node)
        elif node.node_type == NodeType.VARIABLE_DEF:
            self.generate_variable_def(node)
        elif node.node_type == NodeType.IF_STMT:
            self.generate_if(node)
        elif node.node_type == NodeType.LOOP_STMT:
            self.generate_loop(node)
        elif node.node_type == NodeType.RETURN_STMT:
            self.generate_return(node)
    
    def generate_config(self, node: ASTNode):
        """生成配置代码"""
        self.emit(f"# Config block")
        for key, value in node.attributes.items():
            if isinstance(value, str):
                self.emit(f"CONFIG_STR {key} \"{value}\"")
            elif isinstance(value, bool):
                self.emit(f"CONFIG_BOOL {key} {str(value).lower()}")
            else:
                self.emit(f"CONFIG {key} {value}")
    
    def generate_type_def(self, node: ASTNode):
        """生成类型定义"""
        self.emit(f"# Type: {node.value}")
        self.emit(f"TYPE_DEF {node.value}")
        for field_name, field_type in node.attributes.items():
            self.emit(f"TYPE_FIELD {field_name} {field_type}")
        self.emit("TYPE_END")
    
    def generate_function_def(self, node: ASTNode):
        """生成函数定义"""
        func_name = node.value
        self.current_function = func_name
        
        self.emit(f"# Function: {func_name}")
        self.emit(f"FUNC_DEF {func_name}")
        
        # 参数
        params = node.attributes.get("params", [])
        for param_name, param_type in params:
            self.emit(f"PARAM {param_name} {param_type}")
        
        # 返回类型
        return_type = node.attributes.get("return_type")
        if return_type:
            self.emit(f"RETURN_TYPE {return_type}")
        
        # 函数体
        for stmt in node.children:
            self.generate_node(stmt)
        
        self.emit("FUNC_END")
        
        # 记录函数
        self.functions[func_name] = {
            "params": params,
            "return_type": return_type,
            "instruction_count": len(self.instructions)
        }
        self.current_function = None
    
    def generate_quantum_class(self, node: ASTNode):
        """生成量子类"""
        self.emit(f"# Quantum Class: {node.value}")
        self.emit(f"QUANTUM_CLASS {node.value}")
        
        for child in node.children:
            self.generate_node(child)
        
        self.emit("QUANTUM_CLASS_END")
    
    def generate_import(self, node: ASTNode):
        """生成导入"""
        self.emit(f"IMPORT {node.value}")
    
    def generate_export(self, node: ASTNode):
        """生成导出"""
        self.emit(f"EXPORT {node.value}")
    
    def generate_variable_def(self, node: ASTNode):
        """生成变量定义"""
        var_name = node.value
        self.emit(f"LET {var_name}")
        if node.children:
            self.generate_expression(node.children[0])
            self.emit(f"STORE {var_name}")
    
    def generate_if(self, node: ASTNode):
        """生成if语句"""
        # 条件
        self.generate_expression(node.children[0])
        
        label_else = f"ELSE_{len(self.instructions)}"
        label_end = f"ENDIF_{len(self.instructions)}"
        
        self.emit(f"JUMP_FALSE {label_else}")
        
        # then块
        for stmt in node.attributes.get("then", []):
            self.generate_node(stmt)
        
        self.emit(f"JUMP {label_end}")
        self.emit(f"{label_else}:")
        
        # else块
        for stmt in node.attributes.get("else", []):
            self.generate_node(stmt)
        
        self.emit(f"{label_end}:")
    
    def generate_loop(self, node: ASTNode):
        """生成循环"""
        var = node.value
        collection = node.attributes.get("collection", "")
        
        label_start = f"LOOP_{len(self.instructions)}"
        label_end = f"ENDLOOP_{len(self.instructions)}"
        
        self.emit(f"LOAD {collection}")
        self.emit(f"ITER_START {var}")
        
        self.emit(f"{label_start}:")
        self.emit(f"ITER_HAS_NEXT {var}")
        self.emit(f"JUMP_FALSE {label_end}")
        self.emit(f"ITER_NEXT {var}")
        
        # 循环体
        for stmt in node.children:
            self.generate_node(stmt)
        
        self.emit(f"JUMP {label_start}")
        self.emit(f"{label_end}:")
        self.emit("ITER_END")
    
    def generate_return(self, node: ASTNode):
        """生成返回"""
        if node.children:
            self.generate_expression(node.children[0])
            self.emit("RETURN_VALUE")
        else:
            self.emit("RETURN")
    
    def generate_expression(self, node: ASTNode):
        """生成表达式"""
        if node.node_type == NodeType.LITERAL:
            value = node.value.strip('"')
            const_idx = len(self.constants)
            self.constants.append(value)
            self.emit(f"PUSH_CONST {const_idx}")
        
        elif node.node_type == NodeType.IDENTIFIER:
            self.emit(f"LOAD {node.value}")
        
        elif node.node_type == NodeType.BINARY_EXPR:
            self.generate_expression(node.children[0])
            self.generate_expression(node.children[1])
            op = node.value
            self.emit(f"BINARY_OP {op}")
        
        elif node.node_type == NodeType.FUNCTION_CALL:
            # 参数
            for arg in node.children:
                self.generate_expression(arg)
            self.emit(f"CALL {node.value} {len(node.children)}")


def test_codegen():
    """测试代码生成器"""
    test_code = '''
配置 {
    版本: "1.0.0"
}

函数 加法(a: 整数, b: 整数) -> 整数 {
    let 结果 = a + b
    返回 结果
}

quantum_class 量子计算 {
    函数 运行() {
        返回 "量子计算完成"
    }
}
'''
    
    from compiler_verifier import Lexer
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    codegen = CodeGenerator()
    bytecode = codegen.generate(ast)
    
    print("代码生成成功！")
    print(f"指令数: {len(bytecode['instructions'])}")
    print(f"函数数: {len(bytecode['functions'])}")
    print(f"\n指令列表:")
    for i, inst in enumerate(bytecode['instructions'][:20]):
        print(f"  {i:3}: {inst}")
    if len(bytecode['instructions']) > 20:
        print(f"  ... ({len(bytecode['instructions']) - 20} more)")
    
    return bytecode is not None


if __name__ == "__main__":
    success = test_codegen()
    sys.exit(0 if success else 1)
