#!/usr/bin/env python
# -*- coding: utf-8 -*-

# # 
"""
量子基因编码: QE-FIX-DD3E20FAB732
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""
量子缩进错误修复工具

此模块提供函数用于检测和修复Python文件中的缩进错误，
特别关注以下几种错误类型：
1. 混合使用制表符和空格
2. 类方法缩进不一致
3. 文档字符串缩进错误
4. 条件语句缩进错误（特别是elif与if不对齐）
5. 量子基因标记类相关缩进问题
"""

import re
import logging
import tokenize
import io
from pathlib import Path
import argparse

logger = logging.getLogger("IndentFixer")

# 量子基因标记类名正则表达式
QUANTUM_GENE_CLASS_PATTERN = re.compile(r'class\s+(\w+QuantumGene\w*)')

def detect_indentation_type(content):
    """
    检测文件使用的缩进类型
    
    Args:
        content (str): 文件内容
    
    Returns:
        tuple: (使用空格缩进, 使用制表符缩进, 混合使用)
    """
    lines = content.split('\n')
    
    space_indent = False
    tab_indent = False
    
    for line in lines:
        if line.strip() and line.startswith(' '):
            space_indent = True
        if line.strip() and line.startswith('\t'):
            tab_indent = True
        
        # 如果两种都检测到，表示混合使用
        if space_indent and tab_indent:
            return (True, True, True)
    
    return (space_indent, tab_indent, space_indent and tab_indent)

def normalize_indentation(content, use_spaces=True, spaces_per_tab=4):
    """
    标准化文件的缩进
    
    Args:
        content (str): 文件内容
        use_spaces (bool): 是否使用空格作为缩进
        spaces_per_tab (int): 每个制表符等效的空格数
    
    Returns:
        str: 标准化后的文件内容
    """
    lines = content.split('\n')
    normalized_lines = []
    
    for line in lines:
        if not line.strip():  # 空行直接添加
            normalized_lines.append(line)
            continue
        
        # 计算前导空白
        leading_whitespace = len(line) - len(line.lstrip())
        if leading_whitespace == 0:
            normalized_lines.append(line)
            continue
        
        # 提取前导空白
        whitespace = line[:leading_whitespace]
        
        # 计算新的缩进
        if use_spaces:
            # 将制表符转换为空格
            spaces = whitespace.replace('\t', ' ' * spaces_per_tab)
            normalized_lines.append(spaces + line[leading_whitespace:])
        else:
            # 将空格转换为制表符
            tabs = whitespace.replace(' ' * spaces_per_tab, '\t')
            normalized_lines.append(tabs + line[leading_whitespace:])
    
    return '\n'.join(normalized_lines)

def fix_method_indentation(content):
    """
    修复类方法的缩进问题
    
    Args:
        content (str): 文件内容
    
    Returns:
        str: 修复后的文件内容
    """
    lines = content.split('\n')
    fixed_lines = []
    
    in_class = False
    class_indent = ""
    method_indent = ""
    expected_method_indent = ""
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        
        # 检测类定义
        if re.match(r'^\s*class\s+\w+', line):
            in_class = True
            class_indent = line[:len(line) - len(stripped)]
            expected_method_indent = class_indent + "    "  # 假设标准缩进为4个空格
        
        # 检测类内方法定义
        if in_class and re.match(r'^\s*def\s+\w+\s*\(', line):
            current_indent = line[:len(line) - len(stripped)]
            
            # 是否为类方法（第一个参数为self）
            if "self" in line.split('(')[1].split(')')[0]:
                if current_indent != expected_method_indent:
                    logger.debug(f"修复方法缩进: {line.strip()}")
                    line = expected_method_indent + stripped
        
        fixed_lines.append(line)
        i += 1
    
    return '\n'.join(fixed_lines)

def fix_docstring_indentation(content):
    """
    修复文档字符串的缩进问题
    
    Args:
        content (str): 文件内容
    
    Returns:
        str: 修复后的文件内容
    """
    # 使用tokenize模块处理文档字符串
    tokens = []
    fixed_content = []
    
    # 将内容转换为tokens
    try:
        for tok in tokenize.tokenize(io.BytesIO(content.encode('utf-8')).readline):
            tokens.append(tok)
    except tokenize.TokenError:
        # 如果有语法错误导致tokenize失败，则跳过文档字符串修复
        logger.warning("文件存在语法错误，跳过文档字符串修复")
        return content
    
    # 寻找文档字符串并修复缩进
    for i, tok in enumerate(tokens):
        if tok.type == tokenize.STRING and i > 0:
            prev_token = tokens[i-1]
            # 检查是否为文档字符串（通常跟在函数/类定义之后）
            if prev_token.type == tokenize.NEWLINE or prev_token.type == tokenize.INDENT:
                # 检查缩进情况
                pass  # 具体的修复逻辑需要根据实际情况添加
    
    # 由于tokenize的复杂性，这里简化处理
    # 对于多行文档字符串，我们确保其缩进与定义行一致
    
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 检测三引号文档字符串开始
        if re.search(r'^\s*"""', line) and not line.strip().endswith('"""'):
            start_indent = len(line) - len(line.lstrip())
            i += 1
            
            # 修复后续行的缩进，直到找到结束的三引号
            while i < len(lines) and '"""' not in lines[i]:
                current_line = lines[i]
                current_indent = len(current_line) - len(current_line.lstrip())
                
                # 如果缩进不足，添加缩进
                if current_indent < start_indent and current_line.strip():
                    lines[i] = ' ' * start_indent + current_line.lstrip()
                
                i += 1
        
        i += 1
    
    return '\n'.join(lines)

def fix_conditional_indentation(content):
    """
    修复条件语句（if/elif/else）的缩进问题
    
    Args:
        content (str): 文件内容
    
    Returns:
        str: 修复后的文件内容
    """
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        
        # 检测elif语句
        if stripped.startswith('elif '):
            # 寻找对应的if语句
            j = i - 1
            while j >= 0:
                prev_line = lines[j].lstrip()
                prev_indent = len(lines[j]) - len(prev_line)
                
                # 找到相应的if语句
                if prev_line.startswith('if '):
                    current_indent = len(line) - len(stripped)
                    
                    # 如果缩进不匹配，修复elif的缩进
                    if current_indent != prev_indent:
                        logger.debug(f"修复elif缩进: {line.strip()}")
                        line = ' ' * prev_indent + stripped
                    
                    break
                
                # 如果找到其他控制结构，可能是嵌套的，退出
                if prev_line.startswith(('def ', 'class ', 'for ', 'while ', 'try:', 'except')):
                    break
                
                j -= 1
        
        # 检测else语句，类似处理
        if stripped.startswith('else:'):
            # 寻找对应的if或elif语句
            j = i - 1
            while j >= 0:
                prev_line = lines[j].lstrip()
                prev_indent = len(lines[j]) - len(prev_line)
                
                # 找到相应的if或elif语句
                if prev_line.startswith(('if ', 'elif ')):
                    current_indent = len(line) - len(stripped)
                    
                    # 如果缩进不匹配，修复else的缩进
                    if current_indent != prev_indent:
                        logger.debug(f"修复else缩进: {line.strip()}")
                        line = ' ' * prev_indent + stripped
                    
                    break
                
                # 如果找到其他控制结构，可能是嵌套的，退出
                if prev_line.startswith(('def ', 'class ', 'for ', 'while ', 'try:', 'except')):
                    break
                
                j -= 1
        
        fixed_lines.append(line)
        i += 1
    
    return '\n'.join(fixed_lines)

def fix_quantum_gene_class_indentation(content):
    """
    修复量子基因标记类的特殊缩进问题
    
    Args:
        content (str): 文件内容
    
    Returns:
        str: 修复后的文件内容
    """
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    in_quantum_gene_class = False
    class_indent = ""
    
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        
        # 检测量子基因类定义
        match = QUANTUM_GENE_CLASS_PATTERN.search(line)
        if match:
            in_quantum_gene_class = True
            class_indent = line[:len(line) - len(stripped)]
            logger.debug(f"发现量子基因类: {match.group(1)}")
        
        # 检测类结束（通过缩进判断）
        if in_quantum_gene_class and stripped and line.startswith(class_indent) and not stripped.startswith(('def ', 'class ')):
            in_quantum_gene_class = False
        
        # 在量子基因类内部，修复特定的缩进问题
        if in_quantum_gene_class:
            # 检查COMMENT_END_MARKERS字典定义的缩进
            if "COMMENT_END_MARKERS" in stripped:
                expected_indent = class_indent + "    "  # 应该与其他类属性同级
                current_indent = line[:len(line) - len(stripped)]
                
                if current_indent != expected_indent:
                    logger.debug(f"修复量子基因类属性缩进: {line.strip()}")
                    line = expected_indent + stripped
        
        fixed_lines.append(line)
        i += 1
    
    return '\n'.join(fixed_lines)

def fix_indentation_errors(file_path, dry_run=False):
    """
    修复文件中的缩进错误
    
    Args:
        file_path (str): 文件路径
        dry_run (bool): 如果为True，仅检测问题但不修复
    
    Returns:
        bool: 如果文件被修改或需要修改，返回True
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检测缩进类型
        uses_spaces, uses_tabs, mixed_indent = detect_indentation_type(content)
        
        # 确定是否需要修复
        needs_fixing = mixed_indent
        
        # 应用各种修复
        if needs_fixing or True:  # 暂时对所有文件应用修复
            # 1. 标准化缩进
            if mixed_indent:
                logger.debug(f"混合使用制表符和空格: {file_path}")
                fixed_content = normalize_indentation(content)
            else:
                fixed_content = content
            
            # 2. 修复方法缩进
            fixed_content = fix_method_indentation(fixed_content)
            
            # 3. 修复文档字符串缩进
            fixed_content = fix_docstring_indentation(fixed_content)
            
            # 4. 修复条件语句缩进
            fixed_content = fix_conditional_indentation(fixed_content)
            
            # 5. 修复量子基因类特殊缩进
            fixed_content = fix_quantum_gene_class_indentation(fixed_content)
            
            # 检查是否有变化
            if fixed_content != content:
                if not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    logger.debug(f"已修复文件: {file_path}")
                return True
        
        return False
    
    except Exception as e:
        logger.error(f"处理文件时出错 {file_path}: {str(e)}")
        return False

def fix_files_batch(file_paths, dry_run=False):
    """
    批量修复多个文件
    
    Args:
        file_paths (list): 文件路径列表
        dry_run (bool): 如果为True，仅检测问题但不修复
    
    Returns:
        tuple: (修复的文件数, 处理的文件总数)
    """
    fixed_count = 0
    total_count = len(file_paths)
    
    for file_path in file_paths:
        if fix_indentation_errors(file_path, dry_run):
            fixed_count += 1
    
    return fixed_count, total_count

def find_python_files(directory, recursive=False):
    """
    查找目录中的Python文件
    
    Args:
        directory (str): 目录路径
        recursive (bool): 是否递归搜索子目录
    
    Returns:
        list: Python文件路径列表
    """
    python_files = []
    path = Path(directory)
    
    if recursive:
        for file_path in path.rglob("*.py"):
            python_files.append(str(file_path))
    else:
        for file_path in path.glob("*.py"):
            python_files.append(str(file_path))
    
    return python_files

def main():
    """
    主函数，处理命令行参数并执行修复
    """
    parser = argparse.ArgumentParser(description="修复Python文件中的缩进错误")
    parser.add_argument("--dir", default=".", help="要处理的目录路径")
    parser.add_argument("--recursive", action="store_true", help="递归处理子目录")
    parser.add_argument("--dry-run", action="store_true", help="仅检测问题但不修复")
    parser.add_argument("--verbose", action="store_true", help="显示详细信息")
    parser.add_argument("--force", action="store_true", help="强制修复所有文件")
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # 查找Python文件
    python_files = find_python_files(args.dir, args.recursive)
    logger.info(f"找到 {len(python_files)} 个Python文件")
    
    # 执行修复
    fixed_count, total_count = fix_files_batch(python_files, args.dry_run)
    
    # 输出结果
    if args.dry_run:
        logger.info(f"检测完成: 发现 {fixed_count}/{total_count} 个文件需要修复")
    else:
        logger.info(f"修复完成: 已修复 {fixed_count}/{total_count} 个文件")

if __name__ == "__main__":
<<<<<<< HEAD
    main()

=======
    main() 
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
