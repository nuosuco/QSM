#!/usr/bin/env python3
"""
QEntL编译器接口
版本: v0.2.0
量子基因编码: QGC-VM-COMPILER-20260308

包装QEntL编译器功能
"""

import os
import sys

class QEntLCompiler:
    """QEntL编译器接口"""
    
    def __init__(self):
        self.version = "0.2.0"
        self.source_extensions = ['.qentl', '.qsm', '.som', '.weq', '.ref']
        
        print(f"🔧 QEntL编译器 v{self.version}")
    
    def compile(self, source_file: str, output_file: str = None) -> bool:
        """
        编译QEntL源文件
        
        Args:
            source_file: 源文件路径
            output_file: 输出文件路径（可选）
        
        Returns:
            是否成功
        """
        if not os.path.exists(source_file):
            print(f"❌ 文件不存在: {source_file}")
            return False
        
        # 检查扩展名
        ext = os.path.splitext(source_file)[1]
        if ext not in self.source_extensions:
            print(f"❌ 不支持的文件类型: {ext}")
            return False
        
        # 生成输出文件名
        if output_file is None:
            output_file = os.path.splitext(source_file)[0] + '.qbc'
        
        print(f"\n编译: {source_file}")
        print(f"输出: {output_file}")
        
        # 读取源代码
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 词法分析
        tokens = self._lexer(source_code)
        
        # 语法分析
        ast = self._parser(tokens)
        
        # 代码生成
        bytecode = self._generate(ast)
        
        # 写入字节码
        self._write_bytecode(output_file, bytecode)
        
        print(f"✅ 编译成功！")
        return True
    
    def _lexer(self, source: str) -> list:
        """词法分析"""
        # 简化的词法分析
        tokens = []
        keywords = ['配置', '类型', '函数', '返回', '如果', '否则', '循环', 'let', 'quantum_class', 'import']
        
        # 这里简化处理，实际编译器有完整实现
        for word in source.split():
            if word in keywords:
                tokens.append(('KEYWORD', word))
            else:
                tokens.append(('TOKEN', word))
        
        return tokens
    
    def _parser(self, tokens: list) -> dict:
        """语法分析"""
        # 简化的AST
        ast = {
            'type': 'Program',
            'body': []
        }
        
        for token in tokens:
            ast['body'].append(token)
        
        return ast
    
    def _generate(self, ast: dict) -> bytes:
        """字节码生成"""
        # 简化的字节码
        bytecode = b'QBC\x01\x00\x00'
        
        # 这里应该是实际的字节码生成
        for item in ast.get('body', []):
            bytecode += str(item).encode('utf-8')
        
        return bytecode
    
    def _write_bytecode(self, filename: str, bytecode: bytes):
        """写入字节码文件"""
        with open(filename, 'wb') as f:
            f.write(bytecode)


def demo():
    """编译演示"""
    # 创建测试源文件
    test_source = """
配置 {
    版本: "1.0.0"
}

函数 主函数() {
    let 消息 = "你好，量子世界！"
    返回 消息
}
"""
    
    # 写入测试文件
    with open('/tmp/test.qentl', 'w', encoding='utf-8') as f:
        f.write(test_source)
    
    # 编译
    compiler = QEntLCompiler()
    compiler.compile('/tmp/test.qentl', '/tmp/test.qbc')


if __name__ == "__main__":
    demo()
