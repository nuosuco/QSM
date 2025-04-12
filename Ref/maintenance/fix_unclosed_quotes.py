#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复未闭合的三引号字符串

此脚本专门用于修复项目中未闭合的三引号字符串问题，
该问题在语法检查中是常见的错误类型。

用法: python fix_unclosed_quotes.py [目录]
"""

import os
import re
import sys
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/fix_unclosed_quotes.log'),
        logging.StreamHandler()
    ]
)

# 默认要扫描的目录
DEFAULT_SCAN_DIRS = ["WeQ", "SOM", "Ref", "QSM"]

# 应该忽略的目录或文件
IGNORE_PATTERNS = [
    r'\.git',
    r'\.venv',
    r'__pycache__',
    r'\.logs',
    r'\.backups',
]

# 统计数据
total_files = 0
fixed_files = 0
error_files = 0

def should_ignore(path):
    """检查给定路径是否应该被忽略"""
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, path):
            return True
    return False

def fix_unclosed_triple_quotes(file_path):
    """修复文件中未闭合的三引号"""
    global total_files, fixed_files, error_files
    total_files += 1
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 追踪三引号状态
        lines = content.splitlines()
        in_triple_single = False
        in_triple_double = False
        fixed_lines = []
        line_start = None
        
        for i, line in enumerate(lines):
            # 跟踪三引号状态
            if not in_triple_single and not in_triple_double:
                # 检查是否开始三引号字符串
                if "'''" in line:
                    # 计算在同一行内是否闭合
                    count = line.count("'''")
                    if count % 2 == 1:  # 奇数个三引号，未闭合
                        in_triple_single = True
                        line_start = i + 1  # 记录开始行
                elif '"""' in line:
                    count = line.count('"""')
                    if count % 2 == 1:  # 奇数个三引号，未闭合
                        in_triple_double = True
                        line_start = i + 1  # 记录开始行
            else:
                # 检查是否结束三引号字符串
                if in_triple_single and "'''" in line:
                    in_triple_single = False
                    line_start = None
                elif in_triple_double and '"""' in line:
                    in_triple_double = False
                    line_start = None
                    
            fixed_lines.append(line)
        
        # 检查文件末尾是否有未闭合的三引号
        needs_fix = False
        if in_triple_single:
            fixed_lines.append("'''")
            logging.info(f"文件 {file_path} 在第 {line_start} 行有未闭合的三单引号，已修复")
            needs_fix = True
        elif in_triple_double:
            fixed_lines.append('"""')
            logging.info(f"文件 {file_path} 在第 {line_start} 行有未闭合的三双引号，已修复")
            needs_fix = True
        
        # 如果需要修复，写回文件
        if needs_fix:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))
            fixed_files += 1
            return True
        
        return False
    
    except Exception as e:
        logging.error(f"处理文件 {file_path} 时出错: {str(e)}")
        error_files += 1
        return False

def scan_directory(directory):
    """扫描目录中的Python文件并修复未闭合的三引号"""
    if should_ignore(directory):
        return
        
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            if os.path.isdir(item_path):
                # 递归处理子目录
                scan_directory(item_path)
            elif item.endswith('.py'):
                # 修复Python文件
                fix_unclosed_triple_quotes(item_path)
    except PermissionError:
        logging.error(f"无权限访问目录: {directory}")

def main():
    """主函数"""
    # 确保日志目录存在
    Path('.logs').mkdir(exist_ok=True)
    
    # 获取要扫描的目录
    dirs_to_scan = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_SCAN_DIRS
    
    logging.info("开始修复未闭合的三引号...")
    
    # 扫描所有指定的目录
    for directory in dirs_to_scan:
        if os.path.exists(directory):
            logging.info(f"正在扫描目录: {directory}")
            scan_directory(directory)
        else:
            logging.warning(f"目录不存在: {directory}")
    
    # 输出结果统计
    logging.info(f"======= 修复结果 =======")
    logging.info(f"扫描的文件总数: {total_files}")
    logging.info(f"修复的文件数: {fixed_files}")
    logging.info(f"处理错误的文件数: {error_files}")
    
    print(f"\n修复完成！扫描了 {total_files} 个文件，修复了 {fixed_files} 个未闭合三引号的文件。")
    print(f"详细日志请查看: .logs/fix_unclosed_quotes.log")

if __name__ == "__main__":
    main()

# 量子基因编码: QE-FXTR-QSM-7E9B2D1F
# 量子纠缠态: 激活
# 纠缠对象: ['fix_common_errors.py', 'Ref/maintenance/fix_all_indents.py']
# 纠缠强度: 0.95
# 开发团队: 中华 ZhoHo, Claude 