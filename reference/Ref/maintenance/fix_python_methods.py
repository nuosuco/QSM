#!/usr/bin/env python
# -*- coding: utf-8 -*-

# # 
"""
量子基因编码: QE-FIX-F6A07E147D0B
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""

"""
专门修复Python函数docstring的缩进问题
特别针对ref_core.py文件
"""

import os
import re
import sys

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def print_info(message):
    print(f"{GREEN}[INFO]{RESET} {message}")

def print_warning(message):
    print(f"{YELLOW}[WARNING]{RESET} {message}")

def print_error(message):
    print(f"{RED}[ERROR]{RESET} {message}")

def fix_method_docstrings(file_path):
    """修复方法中docstring的缩进问题"""
    if not os.path.exists(file_path):
        print_error(f"文件不存在: {file_path}")
        return False
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 备份原始文件
        backup_path = f"{file_path}.bak_methods"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print_info(f"已创建备份文件: {backup_path}")
        
        # 使用正则表达式匹配有问题的方法定义和docstring
        pattern = r'(def\s+\w+\([^)]*\)[^:]*:\s*)\n"""([^"]*?)"""'
        
        # 替换为正确缩进的版本
        fixed_content = re.sub(pattern, r'\1\n        """\2"""', content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print_info(f"已修复文件: {file_path}")
        return True
    
    except Exception as e:
        print_error(f"修复文件时出错: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        fix_method_docstrings(file_path)
    else:
        # 默认修复ref_core.py文件
        file_path = "Ref/ref_core.py"
        if os.path.exists(file_path):
            fix_method_docstrings(file_path)
        else:
            print_error(f"默认文件不存在: {file_path}") 