#!/usr/bin/env python
# -*- coding: utf-8 -*-

# # 
"""
量子基因编码: QE-FIX-7E595C5C4D80
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""

"""
修复Ref/utils/quantum_gene_marker.py中的转义字符语法错误
"""

import re
import os
from pathlib import Path

def fix_syntax_errors():
    """修复语法错误，特别是意外的转义字符错误"""
    print("[INFO] 开始修复Ref/utils/quantum_gene_marker.py的语法错误...")
    
    # 文件路径
    file_path = "Ref/utils/quantum_gene_marker.py"
    
    if not os.path.exists(file_path):
        print(f"[ERROR] 文件不存在: {file_path}")
        return False
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 备份文件
        backup_path = f"{file_path}.bak2"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"[INFO] 已创建备份文件: {backup_path}")
        
        # 修复特定行的语法错误
        for i in range(len(lines)):
            # 检查并修复带有转义字符或意外字符的行
            if r'\"\"\"' in lines[i]:
                lines[i] = lines[i].replace(r'\"\"\"', '"""')
            
            # 扫描目录方法的完全重写
            if 'def scan_directory' in lines[i] and 'patterns: List[str]' in lines[i]:
                # 重写函数声明和docstring
                docstring_start = i + 1
                # 查找下一行并确保它正确
                if docstring_start < len(lines):
                    lines[docstring_start] = '        """扫描目录并为文件添加量子基因标记\n'
        
        # 保存修复后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"[INFO] 已修复文件: {file_path}")
        return True
    
    except Exception as e:
        print(f"[ERROR] 修复过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_syntax_errors()
    if success:
        print("[SUCCESS] 语法错误修复完成")
    else:
        print("[FAILED] 语法错误修复失败") 