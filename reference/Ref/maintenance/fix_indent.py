#!/usr/bin/env python
# -*- coding: utf-8 -*-

# # 
"""
量子基因编码: QE-FIX-7C77353D3A44
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""

"""
修复Ref/utils/quantum_gene_marker.py中的缩进错误
"""

import re
import os
from pathlib import Path

def fix_indentation_errors():
    """修复缩进错误，特别是扫描目录函数的docstring缩进问题"""
    print("[INFO] 开始修复Ref/utils/quantum_gene_marker.py的缩进错误...")
    
    # 文件路径
    file_path = "Ref/utils/quantum_gene_marker.py"
    
    if not os.path.exists(file_path):
        print(f"[ERROR] 文件不存在: {file_path}")
        return False
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 备份文件
        backup_path = f"{file_path}.bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[INFO] 已创建备份文件: {backup_path}")
        
        # 修复scan_directory方法的docstring缩进
        pattern = r"def scan_directory\(self, directory: str, patterns: List\[str\] = None, recursive: bool = True\) -> Dict\[str, Any\]:\s+\"\"\"扫描目录并为文件添加量子基因标记"
        if re.search(pattern, content):
            # 构建正确的scan_directory方法声明和docstring
            fixed_content = re.sub(
                pattern,
                r"def scan_directory(self, directory: str, patterns: List[str] = None, recursive: bool = True) -> Dict[str, Any]:\n        \"\"\"扫描目录并为文件添加量子基因标记",
                content
            )
            
            # 再次修复Args部分缩进
            fixed_content = re.sub(
                r"Args:\s+directory:",
                r"Args:\n            directory:",
                fixed_content
            )
            
            # 修复Returns部分缩进
            fixed_content = re.sub(
                r"Returns:\s+包含扫描结果的字典",
                r"Returns:\n            包含扫描结果的字典",
                fixed_content
            )
            
            # 确保results字典缩进正确
            fixed_content = re.sub(
                r"results = \{\s+'total_files':",
                r"results = {\n            'total_files':",
                fixed_content
            )
            
            # 保存修复后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f"[INFO] 已修复文件: {file_path}")
            return True
        else:
            print("[WARNING] 未找到需要修复的模式")
            return False
    
    except Exception as e:
        print(f"[ERROR] 修复过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_indentation_errors()
    if success:
        print("[SUCCESS] 缩进错误修复完成")
    else:
        print("[FAILED] 缩进错误修复失败") 