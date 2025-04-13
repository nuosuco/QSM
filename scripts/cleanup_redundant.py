#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
冗余文件和空目录清理脚本

该脚本用于清理项目中的冗余文件和空目录，提高代码组织结构的清晰度
"""

import os
import sys
import shutil
import logging
from pathlib import Path
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QSM-Cleanup")

def find_empty_dirs(root_dir):
    """查找空目录"""
    empty_dirs = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # 跳过.git目录
        if '.git' in dirpath:
            continue
            
        if not dirnames and not filenames:
            empty_dirs.append(dirpath)
    
    return empty_dirs

def remove_empty_dirs(empty_dirs, dry_run=True):
    """删除空目录"""
    removed = 0
    
    for dir_path in empty_dirs:
        if dry_run:
            logger.info(f"将删除空目录: {dir_path}")
        else:
            try:
                os.rmdir(dir_path)
                logger.info(f"已删除空目录: {dir_path}")
                removed += 1
            except Exception as e:
                logger.error(f"删除目录 {dir_path} 时出错: {str(e)}")
    
    return removed

def find_redundant_files(root_dir, extensions=None):
    """查找冗余文件
    
    查找策略:
    1. 找到同一目录下的.py和.qpy文件对
    2. 查找reference目录中已经备份的文件
    """
    redundant_files = []
    
    if extensions is None:
        extensions = ['.py']
    
    for dirpath, _, filenames in os.walk(root_dir):
        # 跳过.git目录
        if '.git' in dirpath:
            continue
            
        # 收集该目录下所有文件
        files_by_stem = {}
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            stem, ext = os.path.splitext(filename)
            
            if stem not in files_by_stem:
                files_by_stem[stem] = []
            
            files_by_stem[stem].append((file_path, ext))
        
        # 查找冗余文件
        for stem, files in files_by_stem.items():
            if len(files) > 1:
                # 如果有.qpy文件和.py文件，则.py文件被视为冗余
                extensions_present = [ext for _, ext in files]
                
                if '.qpy' in extensions_present:
                    for file_path, ext in files:
                        if ext in extensions:
                            redundant_files.append(file_path)
    
    return redundant_files

def move_to_reference(files, reference_dir, dry_run=True):
    """将冗余文件移动到reference目录"""
    moved = 0
    
    for file_path in files:
        # 计算在reference目录中的相对路径
        rel_path = os.path.relpath(file_path, os.getcwd())
        target_path = os.path.join(reference_dir, rel_path)
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        if dry_run:
            logger.info(f"将移动冗余文件: {file_path} 到 {target_path}")
        else:
            try:
                # 如果目标文件已存在，则附加时间戳
                if os.path.exists(target_path):
                    import time
                    timestamp = time.strftime("%Y%m%d%H%M%S")
                    base, ext = os.path.splitext(target_path)
                    target_path = f"{base}_{timestamp}{ext}"
                
                # 移动文件
                shutil.move(file_path, target_path)
                logger.info(f"已移动冗余文件: {file_path} 到 {target_path}")
                moved += 1
            except Exception as e:
                logger.error(f"移动文件 {file_path} 时出错: {str(e)}")
    
    return moved

def main():
    parser = argparse.ArgumentParser(description="清理项目中的冗余文件和空目录")
    parser.add_argument("--root-dir", default=".", help="项目根目录")
    parser.add_argument("--reference-dir", default="reference", help="参考目录，用于存放冗余文件")
    parser.add_argument("--dry-run", action="store_true", help="仅显示将要执行的操作，不实际执行")
    parser.add_argument("--empty-dirs-only", action="store_true", help="仅清理空目录")
    parser.add_argument("--redundant-files-only", action="store_true", help="仅清理冗余文件")
    
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.root_dir)
    reference_dir = os.path.abspath(args.reference_dir)
    
    logger.info(f"开始清理项目: {root_dir}")
    logger.info(f"{'模拟运行模式' if args.dry_run else '实际运行模式'}")
    
    # 确保参考目录存在
    os.makedirs(reference_dir, exist_ok=True)
    
    # 清理冗余文件
    if not args.empty_dirs_only:
        redundant_files = find_redundant_files(root_dir)
        logger.info(f"找到 {len(redundant_files)} 个冗余文件")
        
        moved = move_to_reference(redundant_files, reference_dir, args.dry_run)
        logger.info(f"{'将移动' if args.dry_run else '已移动'} {moved} 个冗余文件到参考目录")
    
    # 清理空目录
    if not args.redundant_files_only:
        empty_dirs = find_empty_dirs(root_dir)
        logger.info(f"找到 {len(empty_dirs)} 个空目录")
        
        removed = remove_empty_dirs(empty_dirs, args.dry_run)
        logger.info(f"{'将删除' if args.dry_run else '已删除'} {removed} 个空目录")
    
    logger.info("清理完成")

if __name__ == "__main__":
    main() 