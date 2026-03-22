#!/usr/bin/env python3
"""
QBC字节码运行器 v0.3.1
量子基因编码: QGC-VM-BYTECODE-20260323
真正执行QBC字节码文件，支持彝文
"""

import os
import re

class BytecodeRunner:
    """字节码运行器"""
    
    def __init__(self):
        self.version = "0.3.1"
        self.stack = []
        self.variables = {}
        self.functions = {}
        self.output = []
        self.current_program = None
        print(f"🚀 QBC字节码运行器 v{self.version}")
    
    def run(self, bytecode_file: str) -> bool:
        """运行字节码文件"""
        if not os.path.exists(bytecode_file):
            print(f"❌ 文件不存在: {bytecode_file}")
            return False
        
        print(f"\n运行: {bytecode_file}")
        
        # 读取字节码（二进制模式）
        with open(bytecode_file, 'rb') as f:
            raw_data = f.read()
        
        # 跳过头部（QBC + 版本号），转换为文本
        # 找到第一个 '(' 的位置
        start_idx = raw_data.find(b'(')
        if start_idx > 0:
            bytecode = raw_data[start_idx:].decode('utf-8')
        else:
            bytecode = raw_data.decode('utf-8')
        
        # 解析TOKEN序列
        tokens = self._parse_tokens(bytecode)
        
        if not tokens:
            print("❌ 无法解析字节码")
            return False
        
        print(f"✅ 解析到 {len(tokens)} 个TOKEN")
        
        # 执行
        self._execute_tokens(tokens)
        
        return True
    
    def _parse_tokens(self, bytecode: str) -> list:
        """解析QBC字节码中的TOKEN"""
        tokens = []
        
        try:
            # 直接匹配 ('TYPE', 'VALUE') 格式
            pattern = r"\('(\w+)',\s*'([^']*)'\)"
            matches = re.findall(pattern, bytecode)
            
            for match in matches:
                token_type, token_value = match
                tokens.append({
                    'type': token_type,
                    'value': token_value
                })
        
        except Exception as e:
            print(f"解析错误: {e}")
        
        return tokens
    
    def _execute_tokens(self, tokens: list):
        """执行TOKEN序列"""
        print("\n执行字节码...")
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            token_val = token['value']
            
            # 检查日志调用 - 格式: 日志("内容")
            if '日志(' in token_val:
                # 提取日志内容
                import re
                match = re.search(r'日志\("([^"]*)"\)', token_val)
                if match:
                    log_content = match.group(1)
                    self.output.append(log_content)
                    i += 1
                    continue
            
            # KEYWORD处理
            if token['type'] == 'KEYWORD':
                keyword = token['value']
                
                if keyword == '配置':
                    i = self._parse_config(tokens, i + 1)
                    continue
                elif keyword == '类型':
                    i = self._parse_type(tokens, i + 1)
                    continue
                elif keyword == '函数':
                    i = self._parse_function(tokens, i + 1)
                    continue
                elif keyword == 'let':
                    i = self._parse_let(tokens, i + 1)
                    continue
                elif keyword == '返回':
                    i = self._parse_return(tokens, i + 1)
                    continue
                elif keyword in ['如果', '否则', '循环']:
                    i = self._skip_block(tokens, i + 1)
                    continue
            
            # quantum_program
            elif token_val == 'quantum_program':
                i = self._parse_program(tokens, i + 1)
                continue
            
            i += 1
        
        # 输出结果
        self._print_output()
    
    def _parse_config(self, tokens: list, start: int) -> int:
        """解析配置块"""
        i = start
        while i < len(tokens):
            if tokens[i]['value'] == '}':
                return i + 1
            i += 1
        return i
    
    def _parse_type(self, tokens: list, start: int) -> int:
        """解析类型定义"""
        i = start
        while i < len(tokens) and tokens[i]['value'] != '}':
            i += 1
        return i + 1
    
    def _parse_function(self, tokens: list, start: int) -> int:
        """解析函数定义"""
        i = start
        func_name = tokens[i]['value']
        i += 1
        
        # 提取函数体
        func_body = []
        brace_count = 0
        started = False
        
        while i < len(tokens):
            if tokens[i]['value'] == '{':
                brace_count += 1
                started = True
            elif tokens[i]['value'] == '}':
                brace_count -= 1
                if brace_count == 0 and started:
                    break
            elif started:
                func_body.append(tokens[i])
            i += 1
        
        self.functions[func_name] = func_body
        return i + 1
    
    def _parse_let(self, tokens: list, start: int) -> int:
        """解析变量声明"""
        i = start
        var_name = tokens[i]['value']
        i += 1
        
        # 跳过 =
        if i < len(tokens) and tokens[i]['value'] == '=':
            i += 1
        
        # 获取值
        if i < len(tokens):
            value = tokens[i]['value']
            # 去掉引号
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            
            self.variables[var_name] = value
        
        return i + 1
    
    def _parse_return(self, tokens: list, start: int) -> int:
        """解析返回语句"""
        i = start
        result = ""
        
        while i < len(tokens):
            val = tokens[i]['value']
            if val == '}':
                break
            
            # 处理字符串
            if val.startswith('"') and val.endswith('"'):
                result += val[1:-1]
            elif val.startswith('"'):
                parts = [val[1:]]
                i += 1
                while i < len(tokens) and not tokens[i]['value'].endswith('"'):
                    parts.append(tokens[i]['value'])
                    i += 1
                if i < len(tokens):
                    parts.append(tokens[i]['value'][:-1])
                result += ''.join(parts)
            # 处理变量引用
            elif val in self.variables:
                result += str(self.variables[val])
            elif val not in ['+', '返回']:
                if val in self.variables:
                    result += str(self.variables[val])
            
            i += 1
        
        self.output.append(result)
        return i
    
    def _skip_block(self, tokens: list, start: int) -> int:
        """跳过代码块"""
        i = start
        brace_count = 0
        started = False
        
        while i < len(tokens):
            if tokens[i]['value'] == '{':
                brace_count += 1
                started = True
            elif tokens[i]['value'] == '}':
                brace_count -= 1
                if brace_count == 0 and started:
                    break
            i += 1
        
        return i + 1
    
    def _parse_program(self, tokens: list, start: int) -> int:
        """解析量子程序"""
        i = start
        program_name = tokens[i]['value']
        self.current_program = program_name
        i += 1
        
        # 解析程序块
        brace_count = 0
        started = False
        setup_body = []
        run_body = []
        current_section = None
        
        while i < len(tokens):
            val = tokens[i]['value']
            
            if val == '{':
                brace_count += 1
                started = True
            elif val == '}':
                brace_count -= 1
                if brace_count == 0 and started:
                    break
            elif val == 'setup:':
                current_section = 'setup'
            elif val == 'run:':
                current_section = 'run'
            elif started:
                if current_section == 'setup':
                    setup_body.append(tokens[i])
                elif current_section == 'run':
                    run_body.append(tokens[i])
            
            i += 1
        
        # 执行setup
        if setup_body:
            self._execute_tokens(setup_body)
        
        # 执行run
        if run_body:
            self._execute_tokens(run_body)
        
        return i + 1
    
    def _print_output(self):
        """打印输出"""
        print("\n输出:")
        for line in self.output:
            print(f"  {line}")
        print("\n✅ 执行完成")


def demo():
    """运行演示"""
    runner = BytecodeRunner()
    runner.run('/tmp/test_yiwen_full.qbc')


if __name__ == "__main__":
    demo()
