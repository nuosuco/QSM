#!/usr/bin/env python
# -*- coding: utf-8 -*-

# # 
"""
量子基因编码: QE-FIX-FC4F06043D16
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""

"""
修复Python文件中的docstring缩进问题
特别是针对monitor/system_monitor_enhancer.py文件
"""

import os
import re
import sys
from pathlib import Path

# 设置颜色
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

def fix_docstring_indentation(file_path):
    """修复文件中方法的docstring缩进问题"""
    print_info(f"开始修复 {file_path} 中的docstring缩进问题...")
    
    if not os.path.exists(file_path):
        print_error(f"文件不存在: {file_path}")
        return False
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 备份文件
        backup_path = f"{file_path}.docstring_bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print_info(f"已创建备份文件: {backup_path}")
        
        # 使用正则表达式修复方法定义后的docstring缩进
        pattern = r'(def\s+\w+\([^)]*\)[^:]*:)\s*\n\s*"""([^"]*?)"""'
        fixed_content = re.sub(pattern, r'\1\n        """\2"""', content)
        
        # 修复特定的docstring缩进问题 - get_trend方法
        pattern = r'(def\s+get_trend\([^)]*\)[^:]*:)\s*\n"""([^"]*?)"""'
        fixed_content = re.sub(pattern, r'\1\n        """\2"""', fixed_content)
        
        # 修复特定的docstring缩进问题 - scan_project方法
        pattern = r'(def\s+scan_project\([^)]*\)[^:]*:)\s*\n"""([^"]*?)"""'
        fixed_content = re.sub(pattern, r'\1\n        """\2"""', fixed_content)
        
        # 修复特定的docstring缩进问题 - analyze_file_health方法
        pattern = r'(def\s+analyze_file_health\([^)]*\)[^:]*:)\s*\n"""([^"]*?)"""'
        fixed_content = re.sub(pattern, r'\1\n        """\2"""', fixed_content)
        
        # 保存修复后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print_info(f"已修复文件: {file_path}")
        return True
    
    except Exception as e:
        print_error(f"修复过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 默认修复system_monitor_enhancer.py文件
    default_file = os.path.join("Ref", "monitor", "system_monitor_enhancer.py")
    
    if len(sys.argv) > 1:
        # 如果提供了文件路径，修复指定的文件
        target_file = sys.argv[1]
    else:
        target_file = default_file
    
    success = fix_docstring_indentation(target_file)
    
    if success:
        print_info("修复完成")
    else:
        print_error("修复失败") 