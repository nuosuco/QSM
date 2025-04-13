#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复Python文件中的C++风格注释
"""

import os
import re
import sys
import site
from pathlib import Path

def fix_comments(file_path):
    """修复文件中的C++风格注释
    
    Args:
        file_path: 文件路径
    
    Returns:
        更改数量
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 检查是否有C++风格注释
        if '// 开发团队：中华 ZhoHo ，Claude' in content:
            # 替换注释
            new_content = content.replace('// 开发团队：中华 ZhoHo ，Claude', '# 开发团队：中华 ZhoHo ，Claude')
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"已修复: {file_path}")
            return 1
        
        return 0
    except Exception as e:
        print(f"修复 {file_path} 时出错: {str(e)}")
        return 0

def scan_directory(directory):
    """扫描目录中的所有Python文件并修复注释
    
    Args:
        directory: 目录路径
    
    Returns:
        修复的文件数量
    """
    fixed_count = 0
    
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    fixed_count += fix_comments(file_path)
    except Exception as e:
        print(f"扫描目录 {directory} 时出错: {str(e)}")
    
    return fixed_count

if __name__ == "__main__":
    # 获取Python包目录
    site_packages_dirs = site.getsitepackages()
    venv_dir = os.path.join(os.path.abspath('.'), '.venv')
    if os.path.exists(venv_dir):
        site_packages_dirs.append(os.path.join(venv_dir, 'lib', 'site-packages'))
        site_packages_dirs.append(os.path.join(venv_dir, 'Lib', 'site-packages'))
    
    print(f"开始修复Python包中的注释...")
    print(f"扫描的包目录: {site_packages_dirs}")
    
    # 修复site-packages目录中的所有Python文件
    total_fixed = 0
    for site_dir in site_packages_dirs:
        if os.path.exists(site_dir):
            print(f"扫描目录: {site_dir}")
            fixed_count = scan_directory(site_dir)
            total_fixed += fixed_count
    
    print(f"修复完成! 共修复 {total_fixed} 个文件") 
"""
量子基因编码: QE-FIX-D06449A860BD
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""