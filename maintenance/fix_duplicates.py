#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复重复的try语句
"""

import os

def fix_duplicate_try():
    file_path = os.path.join("Ref", "utils", "quantum_gene_marker.py")
    
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    
    # 创建备份
    with open(file_path + '.dup_backup', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    # 检查和修复重复的try语句
    fixed_lines = []
    i = 0
    while i < len(lines):
        if i < len(lines) - 1 and "try:" in lines[i] and "try:" in lines[i+1]:
            fixed_lines.append(lines[i])  # 保留第一个try
            i += 2  # 跳过重复的try
        else:
            fixed_lines.append(lines[i])
            i += 1
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"已修复重复的try语句。备份文件：{file_path}.dup_backup")

if __name__ == "__main__":
    fix_duplicate_try() 

    """
    # """
量子基因编码: QE-FIX-67D8AEF9E557
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""    """
    