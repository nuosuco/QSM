#!/usr/bin/env python3
"""
QEntL编译器优化器
优化AST以提高执行效率
"""

import sys
sys.path.insert(0, '/root/QSM/tools')
from qentl_parser import ASTNode, NodeType

class Optimizer:
    """AST优化器"""
    
    def __init__(self):
        self.optimizations = 0
    
    def optimize(self, ast: ASTNode) -> ASTNode:
        """优化AST"""
        self.optimizations = 0
        return self.optimize_node(ast)
    
    def optimize_node(self, node: ASTNode) -> ASTNode:
        """优化单个节点"""
        if node is None:
            return None
        
        # 优化子节点
        optimized_children = []
        for child in node.children:
            opt_child = self.optimize_node(child)
            if opt_child is not None:
                optimized_children.append(opt_child)
        node.children = optimized_children
        
        # 应用优化规则
        node = self.fold_constants(node)
        node = self.eliminate_dead_code(node)
        
        return node
    
    def fold_constants(self, node: ASTNode) -> ASTNode:
        """常量折叠"""
        if node.node_type == NodeType.BINARY_EXPR:
            if len(node.children) == 2:
                left, right = node.children
                if (left.node_type == NodeType.LITERAL and 
                    right.node_type == NodeType.LITERAL):
                    # 尝试计算常量表达式
                    try:
                        a = self.get_value(left)
                        b = self.get_value(right)
                        result = self.compute(a, b, node.value)
                        if result is not None:
                            self.optimizations += 1
                            return ASTNode(NodeType.LITERAL, value=str(result))
                    except:
                        pass
        return node
    
    def eliminate_dead_code(self, node: ASTNode) -> ASTNode:
        """消除死代码"""
        # 如果if条件是常量true/false，简化
        if node.node_type == NodeType.IF_STMT:
            if node.children and node.children[0].node_type == NodeType.LITERAL:
                cond = node.children[0].value
                if cond == "true":
                    # 只保留then块
                    self.optimizations += 1
                    then_block = node.attributes.get("then", [])
                    if then_block:
                        return then_block[0] if len(then_block) == 1 else node
                elif cond == "false":
                    # 只保留else块
                    self.optimizations += 1
                    else_block = node.attributes.get("else", [])
                    if else_block:
                        return else_block[0] if len(else_block) == 1 else node
        return node
    
    def get_value(self, node: ASTNode):
        """获取节点值"""
        val = node.value
        if val == "true":
            return True
        elif val == "false":
            return False
        elif val.startswith('"') and val.endswith('"'):
            return val[1:-1]
        else:
            try:
                return int(val)
            except:
                try:
                    return float(val)
                except:
                    return val
    
    def compute(self, a, b, op):
        """计算表达式"""
        try:
            if op == "+":
                return a + b
            elif op == "-":
                return a - b
            elif op == "*":
                return a * b
            elif op == "/":
                return a / b
            elif op == "==":
                return a == b
            elif op == "!=":
                return a != b
        except:
            return None
        return None
    
    def get_stats(self):
        """获取优化统计"""
        return {"optimizations": self.optimizations}


def test_optimizer():
    """测试优化器"""
    from qentl_parser import Parser
    from compiler_verifier import Lexer
    
    code = '''
配置 { 版本: "1.0.0" }

函数 计算() {
    let x = 1 + 2
    返回 x
}
'''
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    optimizer = Optimizer()
    optimized_ast = optimizer.optimize(ast)
    
    stats = optimizer.get_stats()
    print(f"优化完成")
    print(f"应用优化: {stats['optimizations']}次")
    
    return optimized_ast is not None


if __name__ == "__main__":
    test_optimizer()
