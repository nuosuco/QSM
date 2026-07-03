#!/usr/bin/env python3
"""
QCL Phase2 一次性引导编译器
用途：用Python编译 qcl_bootstrap_phase2.qentl → qcl_bootstrap_phase2.qbc
这是Bootstrap编译器的标准做法——种子编译器。

红线说明：Python只用于生成种子.qbc，之后QEntL全栈自行运行。
"""

import sys
import os

# Opcode 常量表（与 qcl_bootstrap_phase2.qentl 一致）
OPC = {
    'NOP': 0, 'H': 1, 'X': 2, 'Y': 37, 'Z': 3,
    'T': 35, 'S': 36, 'CNOT': 4, 'SWAP': 7,
    'MEASURE': 5, 'RESET': 6, 'LOAD_REG': 8, 'STORE_REG': 9,
    'JUMP': 10, 'JZ': 11, 'ADD': 12, 'SUB': 13, 'MUL': 15,
    'DIV': 14, 'PRINT': 11, 'EXIT': 17, 'BARRIER': 18,
    'INIT_N': 20, 'STOP': 12, 'FUNC_CALL': 30,
    'DEFINE_FUNC': 31, 'LOAD_CONST': 19,
    'NEW': 21, 'LENGTH': 22, 'EQUAL': 23,
    'NOT_EQUAL': 24, 'LESS': 25, 'GREATER': 26,
    'IF': 27, 'ELSE': 28, 'WHILE': 29,
}

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def write_bytecode(path, bc):
    with open(path, 'wb') as f:
        f.write(bc)

def parse_const(line):
    """解析 const NAME = VALUE;"""
    parts = line.replace(';', '').split('=')
    if len(parts) == 2:
        name = parts[0].strip().replace('const ', '')
        try:
            value = int(parts[1].strip())
            return name, value
        except:
            pass
    return None, None

def compile_phase2(src_path, out_path):
    """编译 qcl_bootstrap_phase2.qentl 为 .qbc"""
    source = read_file(src_path)
    lines = source.split('\n')
    
    # 收集常量表
    const_table = {}
    for line in lines:
        name, value = parse_const(line)
        if name:
            const_table[name] = value
    
    bytecode = bytearray()
    
    # 写入魔数头
    bytecode.extend(b'QCL2')
    bytecode.append(0x14)  # 版本标识
    
    # 遍历所有函数，提取量子指令
    in_function = False
    function_name = None
    brace_depth = 0
    
    for line in lines:
        line = line.strip()
        
        # 跳过注释和空行
        if not line or line.startswith('//') or line.startswith('/*'):
            continue
        
        # 检测函数定义
        if line.startswith('def ') and ':' in line:
            in_function = True
            brace_depth = 0
            function_name = line
            # 写入函数定义opcode
            bytecode.append(OPC['DEFINE_FUNC'])
            # 写入函数名字符串长度和内容
            name = function_name.split('(')[0].replace('def ', '').strip()
            name_bytes = name.encode('utf-8')
            bytecode.append(len(name_bytes))
            bytecode.extend(name_bytes)
            continue
        
        # 计算花括号深度
        brace_depth += line.count('{') - line.count('}')
        if brace_depth <= 0 and in_function:
            in_function = False
            continue
        
        # 只编译函数体内的量子指令
        if not in_function:
            continue
        
        # 解析量子指令
        parts = line.split()
        if not parts:
            continue
        
        opcode = parts[0]
        
        # 编译init N
        if opcode == 'init':
            bytecode.append(OPC['INIT_N'])
            if len(parts) > 1:
                bytecode.append(int(parts[1]))
        # 编译H X Y Z T S
        elif opcode in ['H', 'X', 'Y', 'Z', 'T', 'S']:
            bytecode.append(OPC[opcode])
            if len(parts) > 1:
                bytecode.append(int(parts[1]))
        # 编译CNOT
        elif opcode == 'CNOT':
            bytecode.append(OPC['CNOT'])
            if len(parts) > 1:
                bytecode.append(int(parts[1]))
            if len(parts) > 2:
                bytecode.append(int(parts[2]))
        # 编译MEASURE
        elif opcode == 'MEASURE':
            bytecode.append(OPC['MEASURE'])
            if len(parts) > 1:
                bytecode.append(int(parts[1]))
            if len(parts) > 2:
                bytecode.append(int(parts[2]))
        # 编译PRINT
        elif opcode == 'PRINT':
            bytecode.append(OPC['PRINT'])
            if len(parts) > 1:
                bytecode.append(int(parts[1]))
        # 编译STOP/EXIT
        elif opcode in ['STOP', 'EXIT']:
            bytecode.append(OPC[opcode])
        # 编译SWAP
        elif opcode == 'SWAP':
            bytecode.append(OPC['SWAP'])
            if len(parts) > 1:
                bytecode.append(int(parts[1]))
            if len(parts) > 2:
                bytecode.append(int(parts[2]))
        # 编译BARRIER
        elif opcode == 'BARRIER':
            bytecode.append(OPC['BARRIER'])
        # 编译FUNC_CALL
        elif opcode == 'FUNC_CALL':
            bytecode.append(OPC['FUNC_CALL'])
            if len(parts) > 1:
                fname = parts[1]
                fbytes = fname.encode('utf-8')
                bytecode.append(len(fbytes))
                bytecode.extend(fbytes)
        # 编译LOAD_CONST
        elif opcode == 'LOAD_CONST':
            bytecode.append(OPC['LOAD_CONST'])
            if len(parts) > 1:
                try:
                    bytecode.append(int(parts[1]))
                except:
                    pass
    
    write_bytecode(out_path, bytecode)
    print(f"[Phase2 Compiler] 编译: {src_path}")
    print(f"[Phase2 Compiler] 输出: {out_path} ({len(bytecode)} 字节)")
    print(f"[Phase2 Compiler] 函数数: {bytecode.count(OPC['DEFINE_FUNC'])}")
    return len(bytecode)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <输入.qentl> <输出.qbc>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not os.path.exists(input_path):
        print(f"[错误] 找不到文件: {input_path}")
        sys.exit(1)
    
    size = compile_phase2(input_path, output_path)
    print(f"[Phase2 Compiler] 编译成功: {size} 字节")