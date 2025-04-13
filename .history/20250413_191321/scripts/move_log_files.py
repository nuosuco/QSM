#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
将项目中的.log文件移动到.logs目录
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

# 确保.logs目录存在
logs_dir = Path('.logs')
if not logs_dir.exists():
    logs_dir.mkdir()

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('.logs', 'move_logs.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('LogMover')

def find_log_files(directory):
    """
    递归查找目录中的所有.log文件
    """
    log_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.log'):
                # 排除.logs目录中的文件
                if '.logs' not in root and 'logs' not in root:
                    log_files.append(os.path.join(root, file))
    return log_files

def move_log_file(log_file, target_dir):
    """
    移动日志文件到目标目录
    如果目标文件已存在，则重命名原文件
    """
    filename = os.path.basename(log_file)
    target_path = os.path.join(target_dir, filename)
    
    try:
        # 如果目标文件已存在，则添加时间戳重命名
        if os.path.exists(target_path):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_{timestamp}{ext}"
            target_path = os.path.join(target_dir, new_filename)
        
        # 移动文件
        shutil.move(log_file, target_path)
        logger.info(f"Moved {log_file} to {target_path}")
        return True
    except Exception as e:
        logger.error(f"Error moving {log_file}: {str(e)}")
        return False

def main():
    """
    主函数
    """
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not project_root:
        project_root = '.'
    
    logger.info(f"Scanning project directory: {project_root}")
    
    # 查找所有.log文件
    log_files = find_log_files(project_root)
    logger.info(f"Found {len(log_files)} log files")
    
    # 移动文件到.logs目录
    moved_count = 0
    for log_file in log_files:
        if move_log_file(log_file, '.logs'):
            moved_count += 1
    
    logger.info(f"Successfully moved {moved_count} log files to .logs directory")

if __name__ == "__main__":
    main() 
"""
量子基因编码: QE-MOV-41DA8E371333
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""