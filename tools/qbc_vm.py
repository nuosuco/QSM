#!/usr/bin/env python3
"""
QBC量子字节码虚拟机
执行QEntL编译器生成的字节码
"""

import sys
import json
from typing import List, Dict, Any, Optional

class QBCVirtualMachine:
    """QBC虚拟机"""
    
    def __init__(self):
        self.stack = []
        self.variables = {}
        self.functions = {}
        self.quantum_state = [0] * 8  # 8个量子比特
        self.running = True
    
    def load(self, bytecode: Dict[str, Any]):
        """加载字节码"""
        self.instructions = bytecode.get("instructions", [])
        self.constants = bytecode.get("constants", [])
        self.functions = bytecode.get("functions", {})
        self.pc = 0  # 程序计数器
    
    def run(self):
        """执行字节码"""
        while self.running and self.pc < len(self.instructions):
            inst = self.instructions[self.pc]
            self.execute(inst)
            self.pc += 1
    
    def execute(self, instruction: str):
        """执行单条指令"""
        # 跳过注释
        if instruction.startswith("#"):
            return
        
        parts = instruction.split()
        if not parts:
            return
        
        op = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # 量子初始化
        if op == "INIT_QUANTUM":
            self.quantum_state = [0] * 8
            print("[VM] 量子虚拟机初始化完成")
        
        elif op == "SET_QUBITS":
            n = int(args[0]) if args else 8
            self.quantum_state = [0] * n
            print(f"[VM] 设置 {n} 个量子比特")
        
        # 配置
        elif op == "CONFIG_STR":
            key = args[0]
            value = " ".join(args[1:]).strip('"')
            print(f"[Config] {key} = {value}")
        
        elif op == "CONFIG_BOOL":
            key = args[0]
            value = args[1].lower() == "true"
            print(f"[Config] {key} = {value}")
        
        # 类型定义
        elif op == "TYPE_DEF":
            name = args[0]
            print(f"[Type] 定义类型: {name}")
        
        elif op == "TYPE_FIELD":
            field_name = args[0]
            field_type = args[1] if len(args) > 1 else "any"
            print(f"  - {field_name}: {field_type}")
        
        elif op == "TYPE_END":
            pass
        
        # 函数定义
        elif op == "FUNC_DEF":
            name = args[0]
            print(f"[Function] 定义函数: {name}")
        
        elif op == "PARAM":
            name = args[0]
            ptype = args[1] if len(args) > 1 else "any"
            print(f"  - 参数: {name} ({ptype})")
        
        elif op == "RETURN_TYPE":
            rtype = args[0]
            print(f"  - 返回类型: {rtype}")
        
        elif op == "FUNC_END":
            pass
        
        # 量子类
        elif op == "QUANTUM_CLASS":
            name = args[0]
            print(f"[Quantum] 定义量子类: {name}")
        
        elif op == "QUANTUM_CLASS_END":
            pass
        
        # 变量
        elif op == "LET":
            name = args[0]
            self.variables[name] = None
            print(f"[Var] 声明变量: {name}")
        
        elif op == "STORE":
            name = args[0]
            if self.stack:
                self.variables[name] = self.stack.pop()
                print(f"[Var] 存储 {name} = {self.variables[name]}")
        
        elif op == "LOAD":
            name = args[0]
            if name in self.variables:
                self.stack.append(self.variables[name])
            else:
                self.stack.append(name)  # 作为字符串
                print(f"[Var] 加载: {name}")
        
        # 常量
        elif op == "PUSH_CONST":
            idx = int(args[0])
            if idx < len(self.constants):
                self.stack.append(self.constants[idx])
                print(f"[Const] 压入: {self.constants[idx]}")
        
        # 运算
        elif op == "BINARY_OP":
            op_type = args[0]
            if len(self.stack) >= 2:
                b = self.stack.pop()
                a = self.stack.pop()
                result = self.compute(a, b, op_type)
                self.stack.append(result)
                print(f"[Op] {a} {op_type} {b} = {result}")
        
        # 函数调用
        elif op == "CALL":
            func_name = args[0]
            num_args = int(args[1]) if len(args) > 1 else 0
            print(f"[Call] 调用函数: {func_name}({num_args} args)")
            # 简化：直接返回
            self.stack.append(f"<{func_name} result>")
        
        # 返回
        elif op == "RETURN_VALUE":
            if self.stack:
                value = self.stack[-1]
                print(f"[Return] 返回值: {value}")
        
        elif op == "RETURN":
            print("[Return] 返回")
        
        # 导入导出
        elif op == "IMPORT":
            name = args[0]
            print(f"[Import] 导入: {name}")
        
        elif op == "EXPORT":
            name = args[0]
            print(f"[Export] 导出: {name}")
        
        # 停止
        elif op == "HALT":
            self.running = False
            print("[VM] 执行完成")
        
        else:
            print(f"[VM] 未知指令: {op}")
    
    def compute(self, a, b, op):
        """计算二元运算"""
        try:
            if op == "+":
                return a + b if isinstance(a, (int, float)) and isinstance(b, (int, float)) else str(a) + str(b)
            elif op == "-":
                return a - b
            elif op == "*":
                return a * b
            elif op == "/":
                return a / b if b != 0 else 0
            elif op == "==":
                return a == b
            elif op == "!=":
                return a != b
            elif op == "<":
                return a < b
            elif op == ">":
                return a > b
            else:
                return None
        except:
            return None


def test_vm():
    """测试虚拟机"""
    # 使用代码生成器生成字节码
    sys.path.insert(0, '/root/QSM/tools')
    from qentl_codegen import CodeGenerator
    from qentl_parser import Parser
    from compiler_verifier import Lexer
    
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
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    codegen = CodeGenerator()
    bytecode = codegen.generate(ast)
    
    print("=" * 50)
    print("QBC虚拟机测试")
    print("=" * 50)
    
    vm = QBCVirtualMachine()
    vm.load(bytecode)
    vm.run()
    
    print("=" * 50)
    print("✅ 虚拟机执行成功！")
    return True


if __name__ == "__main__":
    success = test_vm()
    sys.exit(0 if success else 1)
