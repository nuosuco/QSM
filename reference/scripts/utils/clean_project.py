#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
项目清理脚本
用于清理和整合项目中的文档、代码文件和目录
"""

import os
import time
import shutil
from pathlib import Path
import re

# 量子基因编码
QG_CODE = "QG-UTIL-CLEAN-PROJ-A1B2"

# 量子纠缠信道
QE_CHANNEL = "QE-UTIL-CLEAN-" + str(int(time.time()))

# 设置项目根目录
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 需要保留的重要文档
KEEP_DOCS = [
    "docs/architecture/template.qentl",
    "docs/architecture/architecture.qentl", 
    "docs/project_state/project_state.qentl",
    "docs/change_history/change_history.qentl"
]

# 需要保留的重要代码文件
KEEP_CODE = [
    # 核心服务文件
    "QSM/api/qsm_api.py",
    "WeQ/api/weq_api.py",
    "SOM/api/som_api.py",
    "Ref/api/ref_api.py",
    
    # 启动脚本
    "scripts/services/start_all_services.py",
    "WeQ/scripts/services/WeQ_start_services.py",
    
    # 工具脚本
    "scripts/utils/clean_project.py",
    "Ref/utils/project_organizer.py"
]

# 需要保留的目录
KEEP_DIRS = [
    "world/static/js/quantum_entanglement",
    "world/templates/components",
    "world/static/css",
    "docs"
]

def is_simple_doc(file_path):
    """判断是否为简单的文档"""
    if not file_path.is_file():
        return False
        
    # 检查文件大小
    if file_path.stat().st_size > 1024:  # 大于1KB的文件可能是重要文档
        return False
        
    # 读取文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False
        
    # 如果包含量子基因编码或量子纠缠信道,则不是简单文档
    if "QG-" in content or "QE-" in content:
        return False
        
    # 统计行数
    lines = content.split('\n')
    if len(lines) > 20:  # 超过20行的可能是重要文档
        return False
        
    return True

def is_test_or_temp_code(file_path):
    """判断是否为测试或临时代码文件"""
    # 检查文件名
    name = file_path.name.lower()
    if any(x in name for x in ['test', 'temp', 'tmp', 'bak']):
        return True
        
    # 检查内容
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'TODO' in content or 'FIXME' in content:
                return True
    except:
        pass
        
    return False

def should_keep_file(file_path):
    """判断是否需要保留文件"""
    rel_path = str(file_path.relative_to(ROOT_DIR)).replace('\\', '/')
    
    # 检查是否在保留列表中
    if rel_path in KEEP_DOCS or rel_path in KEEP_CODE:
        return True
        
    # 检查是否在保留目录中
    for keep_dir in KEEP_DIRS:
        if rel_path.startswith(keep_dir):
            return True
            
    return False

def clean_project():
    """清理项目文件"""
    print(f"开始清理项目: {ROOT_DIR}")
    
    # 遍历所有文件
    for file_path in ROOT_DIR.rglob('*'):
        if file_path.is_file():
            rel_path = str(file_path.relative_to(ROOT_DIR)).replace('\\', '/')
            
            # 跳过需要保留的文件
            if should_keep_file(file_path):
                print(f"保留文件: {rel_path}")
                continue
                
            # 删除简单文档或测试代码
            if is_simple_doc(file_path) or is_test_or_temp_code(file_path):
                print(f"删除文件: {rel_path}")
                file_path.unlink()
                
    # 清理空目录
    for dir_path in ROOT_DIR.rglob('*'):
        if dir_path.is_dir():
            rel_path = str(dir_path.relative_to(ROOT_DIR)).replace('\\', '/')
            
            # 跳过需要保留的目录
            if any(rel_path.startswith(x) for x in KEEP_DIRS):
                continue
                
            try:
                dir_path.rmdir()  # 只能删除空目录
                print(f"删除空目录: {rel_path}")
            except OSError:
                pass  # 非空目录会抛出异常,忽略即可

if __name__ == "__main__":
    clean_project() 