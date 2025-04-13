#!/usr/bin/env python

# # """
量子基因编码: QE-FIX-B2D70C3E20CD
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""
缩进错误修复脚本

此脚本用于修复项目中的Python文件中的缩进错误，
特别是针对多行文档字符串(docstring)缩进不正确的问题。
"""

import os
import re
import sys
from pathlib import Path

# 需要检查的文件路径列表
FILES_TO_CHECK = [
    "Ref/ref_core.py",
    "Ref/utils/quantum_gene_marker.py",
    "QEntL/utils/__init__.py",
    "Ref/utils/file_monitor.py",
    "Ref/__init__.py",
    "world/tools/path_resolver.py",
    "QSM/app.py"
]

# 颜色定义
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def print_status(message):
    """打印状态消息"""
    print(f"{GREEN}[STATUS] {message}{RESET}")

def print_warning(message):
    """打印警告消息"""
    print(f"{YELLOW}[WARNING] {message}{RESET}")

def print_error(message):
    """打印错误消息"""
    print(f"{RED}[ERROR] {message}{RESET}")

def detect_docstring_indent_errors(lines):
    """
    检测并修复文档字符串中的缩进错误
    
    参数:
        lines: 文件的行列表
    
    返回:
        list: 修复后的行列表
        bool: 是否进行了修改
    """
    modified = False
    in_multiline_string = False
    string_indent = 0
    current_indent = 0
    string_start_line = 0
    
    fixed_lines = lines.copy()
    
    for i in range(len(lines)):
        line = lines[i]
        
        # 检测当前行的缩进级别
        if line.strip():
            current_indent = len(line) - len(line.lstrip())
        
        # 检测三引号开始的多行字符串
        if (re.search(r'^\s*"""', line) or re.search(r'^\s*\'\'\'', line)) and not (line.strip().endswith('"""') or line.strip().endswith("'''")):
            in_multiline_string = True
            string_indent = current_indent
            string_start_line = i
        
        # 如果在多行字符串中，并且检测到缩进错误
        if in_multiline_string and i > string_start_line:
            if current_indent != string_indent and line.strip():
                # 修复缩进
                fixed_lines[i] = ' ' * string_indent + line.lstrip()
                modified = True
        
        # 检测三引号结束的多行字符串
        if in_multiline_string and (line.strip().endswith('"""') or line.strip().endswith("'''")):
            # 确保结束引号的缩进和开始引号一致
            if len(line) - len(line.lstrip()) != string_indent:
                fixed_lines[i] = ' ' * string_indent + line.lstrip()
                modified = True
            in_multiline_string = False
    
    return fixed_lines, modified

def detect_method_indent_errors(lines):
    """
    检测并修复方法和函数定义中的缩进错误
    
    参数:
        lines: 文件的行列表
    
    返回:
        list: 修复后的行列表
        bool: 是否进行了修改
    """
    modified = False
    fixed_lines = lines.copy()
    
    # 使用正则表达式检测类定义、方法定义和函数定义
    class_pattern = re.compile(r'^\s*class\s+\w+.*:')
    func_pattern = re.compile(r'^\s*def\s+\w+\s*\(.*\):')
    indent_stack = []
    
    for i in range(len(lines)):
        line = lines[i]
        stripped_line = line.strip()
        
        # 跳过空行和注释行
        if not stripped_line or stripped_line.startswith('#'):
            continue
        
        current_indent = len(line) - len(line.lstrip())
        
        # 检测类定义
        if class_pattern.match(line):
            indent_stack.append((current_indent, 'class'))
            continue
        
        # 检测函数或方法定义
        if func_pattern.match(line):
            if indent_stack and indent_stack[-1][1] == 'class':
                # 在类内部的方法应该有额外的缩进
                expected_indent = indent_stack[-1][0] + 4
                if current_indent != expected_indent:
                    fixed_lines[i] = ' ' * expected_indent + line.lstrip()
                    modified = True
            indent_stack.append((current_indent, 'func'))
            continue
        
        # 检查函数或方法体的缩进
        if indent_stack:
            expected_indent = indent_stack[-1][0] + 4
            
            # 检查是否退出当前块
            if current_indent <= indent_stack[-1][0]:
                while indent_stack and current_indent <= indent_stack[-1][0]:
                    indent_stack.pop()
            
            # 检查当前行的缩进是否正确
            elif current_indent != expected_indent:
                # 这可能是函数体内的一行，应该有正确的缩进
                fixed_lines[i] = ' ' * expected_indent + line.lstrip()
                modified = True
    
    return fixed_lines, modified

def fix_special_cases(lines, file_path):
    """
    修复特定文件中的特殊缩进问题
    
    参数:
        lines: 文件的行列表
        file_path: 文件路径
    
    返回:
        list: 修复后的行列表
        bool: 是否进行了修改
    """
    modified = False
    fixed_lines = lines.copy()
    
    # 检查文件名中是否包含特定关键字，并应用针对性修复
    file_name = os.path.basename(file_path)
    
    # 例如，为path_resolver.py文件应用特殊修复
    if "path_resolver.py" in file_path:
        # 寻找特定行并修复
        for i in range(len(lines)):
            if i > 0 and "def resolve_path" in lines[i] and "参数:" in lines[i+1]:
                # 检查下面几行的缩进
                base_indent = len(lines[i]) - len(lines[i].lstrip())
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip() and "def " not in lines[j]:
                        current_indent = len(lines[j]) - len(lines[j].lstrip())
                        expected_indent = base_indent + 4
                        if current_indent != expected_indent:
                            fixed_lines[j] = ' ' * expected_indent + lines[j].lstrip()
                            modified = True
    
    # 针对ref_core.py文件的特殊处理
    if "ref_core.py" in file_path:
        for i in range(len(lines)):
            if "def start_monitoring" in lines[i]:
                base_indent = len(lines[i]) - len(lines[i].lstrip())
                in_method = True
                for j in range(i+1, len(lines)):
                    if not lines[j].strip():
                        continue
                    
                    current_indent = len(lines[j]) - len(lines[j].lstrip())
                    
                    # 检查是否已经离开了方法
                    if current_indent <= base_indent and "def " in lines[j]:
                        in_method = False
                        break
                    
                    # 检查方法内的行是否有正确的缩进
                    if in_method and current_indent != base_indent + 4 and lines[j].strip():
                        fixed_lines[j] = ' ' * (base_indent + 4) + lines[j].lstrip()
                        modified = True
    
    return fixed_lines, modified

def fix_quantum_gene_marker(lines):
    """
    特别修复quantum_gene_marker.py文件中常见的问题
    
    参数:
        lines: 文件的行列表
    
    返回:
        list: 修复后的行列表
        bool: 是否进行了修改
    """
    modified = False
    fixed_lines = lines.copy()
    
    # 查找 COMMENT_END_MARKERS 字典定义
    for i, line in enumerate(lines):
        if "COMMENT_END_MARKERS" in line and "{" in line:
            # 在字典开始后，检查其内容是否有正确的缩进
            base_indent = len(line) - len(line.lstrip())
            in_dict = True
            for j in range(i+1, len(lines)):
                if "}" in lines[j]:
                    in_dict = False
                    break
                    
                current_indent = len(lines[j]) - len(lines[j].lstrip())
                expected_indent = base_indent + 4  # 字典内容应该多缩进4个空格
                
                if lines[j].strip() and current_indent != expected_indent:
                    fixed_lines[j] = ' ' * expected_indent + lines[j].lstrip()
                    modified = True
    
    # 查找 __init__ 方法并修复其内部缩进
    for i, line in enumerate(lines):
        if "def __init__" in line:
            base_indent = len(line) - len(line.lstrip())
            in_method = True
            for j in range(i+1, len(lines)):
                if not lines[j].strip():
                    continue
                
                current_indent = len(lines[j]) - len(lines[j].lstrip())
                
                # 检查是否已经离开了方法
                if current_indent <= base_indent and "def " in lines[j]:
                    in_method = False
                    break
                
                # 检查方法内的行是否有正确的缩进
                if in_method and current_indent != base_indent + 4 and lines[j].strip() and not lines[j].strip().startswith('#'):
                    fixed_lines[j] = ' ' * (base_indent + 4) + lines[j].lstrip()
                    modified = True
    
    return fixed_lines, modified

def fix_indent_errors(file_path):
    """
    修复文件中的缩进错误，特别是多行文档字符串的缩进问题
    
    参数:
        file_path: 要修复的文件路径
    
    返回:
        bool: 是否进行了修改
    """
    try:
        # 确保文件存在
        if not os.path.exists(file_path):
            print_warning(f"文件不存在: {file_path}")
            return False
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 保存原始内容备份
        backup_path = f"{file_path}.bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # 应用多种修复算法
        modified = False
        
        # 1. 修复文档字符串缩进
        lines, doc_modified = detect_docstring_indent_errors(lines)
        modified |= doc_modified
        
        # 2. 修复方法和函数缩进
        lines, method_modified = detect_method_indent_errors(lines)
        modified |= method_modified
        
        # 3. 应用特殊情况修复
        lines, special_modified = fix_special_cases(lines, file_path)
        modified |= special_modified
        
        # 4. 针对quantum_gene_marker.py的特殊修复
        if "quantum_gene_marker.py" in file_path:
            lines, qgm_modified = fix_quantum_gene_marker(lines)
            modified |= qgm_modified
        
        # 如果进行了修改，写入文件
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print_status(f"已修复文件: {file_path}")
        else:
            print_status(f"文件没有需要修复的缩进错误: {file_path}")
            # 删除备份
            os.remove(backup_path)
        
        return modified
    
    except Exception as e:
        print_error(f"处理文件 {file_path} 时出错: {str(e)}")
        return False

def scan_all_python_files(directory="."):
    """
    扫描目录中的所有Python文件
    
    参数:
        directory: 要扫描的目录
    
    返回:
        list: 发现的所有Python文件路径
    """
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def main():
    """主函数，处理指定的文件列表"""
    # 解析命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--scan-all":
        print_status("扫描所有Python文件以查找缩进错误...")
        files_to_check = scan_all_python_files()
        print_status(f"发现 {len(files_to_check)} 个Python文件")
    else:
        print_status("使用预定义的文件列表...")
        # 获取当前工作目录
        current_dir = os.getcwd()
        files_to_check = [os.path.join(current_dir, file_path) for file_path in FILES_TO_CHECK]
    
    print_status("开始修复文件中的缩进错误...")
    
    # 处理所有指定的文件
    files_fixed = 0
    for file_path in files_to_check:
        if fix_indent_errors(file_path):
            files_fixed += 1
    
    # 打印汇总信息
    if files_fixed > 0:
        print_status(f"已修复 {files_fixed} 个文件中的缩进错误")
    else:
        print_status("没有文件需要修复缩进错误")
    
    print_status("缩进错误修复完成")

if __name__ == "__main__":
    main() 