#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件整理工具

此脚本用于识别并整理项目中的文件，包括：
- 识别并移动损坏的文件（.broken后缀）到参考目录
- 识别并清理重复或过时的文件
- 将不再需要但有参考价值的文件移动到参考目录
- 合并相似功能的文件减少冗余
"""

import os
import sys
import re
import shutil
import logging
import argparse
import time
import hashlib
import fnmatch
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set, Any
from datetime import datetime

# 目录设置
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REFERENCE_DIR = os.path.join(ROOT_DIR, 'reference')
LOG_DIR = os.path.join(ROOT_DIR, '.logs')

# 创建必要的目录
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REFERENCE_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'file_organizer.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('File-Organizer')

# 需要排除的目录和文件
EXCLUDE_PATTERNS = [
    '.git', '.vscode', '.cursor', '.venv', '.history', 'reference', 
    '.logs', '.reports', '.pids', '.temp', '__pycache__',
    '*.pyc', '*.pyo', '*.so', '*.dll', '*.exe', '*.bin', '*.dat', '*.db'
]

# 不需要的文件模式（将移动到参考目录）
UNWANTED_PATTERNS = [
    '*.broken', '*.bak', '*.backup', '*.old', '*.tmp', '*.temp',
    '*.log', '*.log.*', 'temp_*', '*.swp', '*.swo',
    'test_*', '*.test.*', '*_test.*', '*_test_*',
    '*_old.*', '*_old_*', '*_backup.*', '*_backup_*',
    'unused_*', '*_unused.*', '*_unused_*',
    'draft_*', '*_draft.*', '*_draft_*',
    'obsolete_*', '*_obsolete.*', '*_obsolete_*'
]

# 文件内容标记，表示文件已弃用或已移动
OBSOLETE_MARKERS = [
    "# OBSOLETE", "# DEPRECATED", "# MOVED TO", 
    "// OBSOLETE", "// DEPRECATED", "// MOVED TO",
    "/* OBSOLETE", "/* DEPRECATED", "/* MOVED TO",
    "<!-- OBSOLETE", "<!-- DEPRECATED", "<!-- MOVED TO",
    "''' OBSOLETE", "''' DEPRECATED", "''' MOVED TO",
    '""" OBSOLETE', '""" DEPRECATED', '""" MOVED TO'
]

# 已知的代码重复和冗余模式
REDUNDANCY_PATTERNS = {
    # 量子基因相关文件整合到一个目录
    'quantum_gene': ['*quantum_gene*.py', '*quantum_gene*.qpy', '*qgene*.py', '*qgene*.qpy'],
    # 自组织市场文件整合
    'som': ['*som_*.py', '*som_*.qpy', '*market*.py', '*market*.qpy'],
    # 量子社交引擎文件整合
    'weq': ['*weq_*.py', '*weq_*.qpy', '*social*.py', '*social*.qpy'],
    # 反射系统文件整合
    'ref': ['*ref_*.py', '*ref_*.qpy', '*reflect*.py', '*reflect*.qpy'],
}


class FileOrganizer:
    """文件整理器，用于识别和移动文件"""
    
    def __init__(self, root_dir=None, reference_dir=None, dry_run=False):
        """初始化文件整理器
        
        Args:
            root_dir: 项目根目录
            reference_dir: 参考文件目录
            dry_run: 是否仅模拟操作而不实际修改文件
        """
        self.root_dir = root_dir or ROOT_DIR
        self.reference_dir = reference_dir or REFERENCE_DIR
        self.dry_run = dry_run
        self.stats = {
            'scanned': 0,
            'moved': 0,
            'failed': 0,
            'skipped': 0,
            'total_size_moved': 0
        }
        self.moved_files = []
        self.failed_files = []
        
    def scan_project(self, directory=None):
        """扫描项目目录
        
        Args:
            directory: 要扫描的目录，如果为None则扫描根目录
            
        Returns:
            扫描的文件列表
        """
        if directory is None:
            directory = self.root_dir
            
        logger.info(f"扫描目录: {directory}")
        
        files_to_process = []
        
        for root, dirs, files in os.walk(directory):
            # 排除指定的目录
            dirs[:] = [d for d in dirs if not self._should_exclude(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # 排除指定的文件
                if self._should_exclude(file_path):
                    continue
                
                self.stats['scanned'] += 1
                files_to_process.append(file_path)
                
        logger.info(f"找到 {len(files_to_process)} 个待处理文件")
        return files_to_process
    
    def identify_unwanted_files(self, files):
        """识别不需要的文件
        
        Args:
            files: 文件路径列表
            
        Returns:
            不需要的文件路径列表
        """
        unwanted_files = []
        
        for file_path in files:
            file_name = os.path.basename(file_path)
            
            # 检查文件名是否匹配不需要的模式
            if any(fnmatch.fnmatch(file_name, pattern) for pattern in UNWANTED_PATTERNS):
                unwanted_files.append(file_path)
                continue
            
            # 检查文件内容是否包含弃用标记
            if self._has_obsolete_marker(file_path):
                unwanted_files.append(file_path)
                continue
                
        logger.info(f"找到 {len(unwanted_files)} 个不需要的文件")
        return unwanted_files
    
    def _has_obsolete_marker(self, file_path):
        """检查文件是否包含弃用标记
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否包含弃用标记
        """
        try:
            # 只读取文件的前50行以提高效率
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = ''.join([f.readline() for _ in range(50)])
                
            for marker in OBSOLETE_MARKERS:
                if marker in content:
                    return True
                    
            return False
        except Exception as e:
            logger.warning(f"检查文件 {file_path} 内容时出错: {e}")
            return False
    
    def find_redundancies(self, files):
        """查找代码冗余
        
        Args:
            files: 文件路径列表
            
        Returns:
            冗余文件组的字典，键为组名，值为文件路径列表
        """
        redundancies = {}
        
        # 按模式分组文件
        for group_name, patterns in REDUNDANCY_PATTERNS.items():
            redundancies[group_name] = []
            for file_path in files:
                file_name = os.path.basename(file_path)
                if any(fnmatch.fnmatch(file_name, pattern) for pattern in patterns):
                    redundancies[group_name].append(file_path)
        
        # 移除只有一个文件的组
        redundancies = {k: v for k, v in redundancies.items() if len(v) > 1}
        
        return redundancies
    
    def move_file_to_reference(self, file_path):
        """将文件移动到参考目录
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功移动
        """
        try:
            # 计算相对路径
            rel_path = os.path.relpath(file_path, self.root_dir)
            ref_path = os.path.join(self.reference_dir, rel_path)
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(ref_path), exist_ok=True)
            
            # 如果已存在同名文件，添加时间戳
            if os.path.exists(ref_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base, ext = os.path.splitext(ref_path)
                ref_path = f"{base}_{timestamp}{ext}"
            
            if self.dry_run:
                logger.info(f"[DRY RUN] 移动文件: {file_path} -> {ref_path}")
                return True
            
            # 移动文件
            file_size = os.path.getsize(file_path)
            shutil.move(file_path, ref_path)
            
            # 更新统计信息
            self.stats['moved'] += 1
            self.stats['total_size_moved'] += file_size
            self.moved_files.append((file_path, ref_path))
            
            logger.info(f"已移动文件: {file_path} -> {ref_path}")
            return True
            
        except Exception as e:
            logger.error(f"移动文件 {file_path} 时出错: {e}")
            self.stats['failed'] += 1
            self.failed_files.append(file_path)
            return False
    
    def _should_exclude(self, path):
        """检查路径是否应该被排除
        
        Args:
            path: 要检查的路径
            
        Returns:
            是否应该排除
        """
        path = os.path.normpath(path)
        
        # 检查路径是否在排除模式中
        for pattern in EXCLUDE_PATTERNS:
            if fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
            if pattern in path.split(os.sep):
                return True
                
        return False
    
    def organize_project(self):
        """整理项目文件
        
        Returns:
            组织完成的统计信息
        """
        start_time = time.time()
        logger.info(f"开始整理项目: {self.root_dir}")
        
        # 扫描项目文件
        files = self.scan_project()
        
        # 识别不需要的文件
        unwanted_files = self.identify_unwanted_files(files)
        
        # 移动不需要的文件到参考目录
        for file_path in unwanted_files:
            self.move_file_to_reference(file_path)
        
        # 查找冗余
        redundancies = self.find_redundancies(files)
        
        # 处理冗余文件组
        if redundancies and not self.dry_run:
            logger.info("正在处理冗余文件组...")
            for group_name, group_files in redundancies.items():
                logger.info(f"处理组 '{group_name}' ({len(group_files)} 个文件)")
                self._consolidate_redundant_files(group_name, group_files)
        
        # 输出冗余文件信息
        if redundancies:
            logger.info("找到以下冗余文件组:")
            for group_name, group_files in redundancies.items():
                logger.info(f"  组 '{group_name}' 包含 {len(group_files)} 个相关文件")
                for file_path in group_files:
                    logger.info(f"    - {file_path}")
        
        # 生成整理报告
        elapsed_time = time.time() - start_time
        report = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': elapsed_time,
            'stats': self.stats,
            'moved_files': self.moved_files,
            'failed_files': self.failed_files,
            'redundancy_groups': {k: v for k, v in redundancies.items()}
        }
        
        # 保存报告
        report_path = os.path.join(LOG_DIR, f'organize_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 输出统计信息
        logger.info(f"项目整理完成，用时 {elapsed_time:.2f} 秒")
        logger.info(f"扫描文件: {self.stats['scanned']}")
        logger.info(f"移动文件: {self.stats['moved']}")
        logger.info(f"失败: {self.stats['failed']}")
        logger.info(f"跳过: {self.stats['skipped']}")
        logger.info(f"移动总大小: {self.stats['total_size_moved'] / 1024:.2f} KB")
        
        return report

    def _consolidate_redundant_files(self, group_name, file_paths):
        """整合冗余文件组
        
        将同一组的冗余文件整合到reference目录的对应组文件夹中
        保留主要模块中的文件，移动其他冗余副本
        
        Args:
            group_name: 冗余组名称
            file_paths: 冗余文件路径列表
        """
        if not file_paths:
            return
        
        # 创建冗余组文件夹
        redundancy_group_dir = os.path.join(self.reference_dir, 'redundant', group_name)
        os.makedirs(redundancy_group_dir, exist_ok=True)
        
        # 按模块分类文件
        files_by_module = {}
        for file_path in file_paths:
            # 获取相对路径
            rel_path = os.path.relpath(file_path, self.root_dir)
            # 获取第一级目录作为模块名
            parts = rel_path.split(os.sep)
            module = parts[0] if parts else 'unknown'
            
            if module not in files_by_module:
                files_by_module[module] = []
            files_by_module[module].append(file_path)
        
        # 确定主要模块优先级
        module_priority = {
            'QSM': 1,    # 主服务最高优先级
            'WeQ': 2,
            'SOM': 2,
            'Ref': 2,
            'api': 3,
            'models': 3,
            'core': 4,
            'quantum_core': 5,
            'quantum_shared': 6
        }
        
        # 确定保留哪些模块的文件
        modules_to_keep = []
        if group_name == 'quantum_gene':
            modules_to_keep = ['quantum_core', 'Ref']
        elif group_name == 'som':
            modules_to_keep = ['SOM', 'quantum_economy']
        elif group_name == 'weq':
            modules_to_keep = ['WeQ']
        elif group_name == 'ref':
            modules_to_keep = ['Ref']
        
        # 处理每个模块
        for module, module_files in files_by_module.items():
            # 如果是需要保留的模块，跳过
            if module in modules_to_keep:
                logger.info(f"  保留模块 '{module}' 中的文件")
                continue
            
            # 特殊处理：保留QSM/api, SOM/api和WeQ/api中的API文件
            if (module in ['QSM', 'SOM', 'WeQ']) and (any('api' in file_path for file_path in module_files)):
                api_files = [f for f in module_files if 'api' in f]
                non_api_files = [f for f in module_files if 'api' not in f]
                
                logger.info(f"  保留模块 '{module}' 中的API文件")
                
                # 移动非API文件
                for file_path in non_api_files:
                    self._move_to_redundancy_group(file_path, redundancy_group_dir, module)
                
                continue
            
            # 移动此模块的所有文件
            for file_path in module_files:
                self._move_to_redundancy_group(file_path, redundancy_group_dir, module)
    
    def _move_to_redundancy_group(self, file_path, group_dir, module):
        """移动文件到冗余组目录
        
        Args:
            file_path: 文件路径
            group_dir: 冗余组目录
            module: 模块名
        """
        try:
            # 从文件路径中提取文件名
            file_name = os.path.basename(file_path)
            
            # 创建模块子目录
            module_dir = os.path.join(group_dir, module)
            os.makedirs(module_dir, exist_ok=True)
            
            # 目标路径
            target_path = os.path.join(module_dir, file_name)
            
            # 如果文件已存在，添加时间戳
            if os.path.exists(target_path):
                base, ext = os.path.splitext(target_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                target_path = f"{base}_{timestamp}{ext}"
            
            # 移动文件
            file_size = os.path.getsize(file_path)
            shutil.move(file_path, target_path)
            
            # 更新统计信息
            self.stats['moved'] += 1
            self.stats['total_size_moved'] += file_size
            self.moved_files.append((file_path, target_path))
            
            logger.info(f"  已移动冗余文件: {file_path} -> {target_path}")
            
        except Exception as e:
            logger.error(f"移动冗余文件 {file_path} 时出错: {e}")
            self.stats['failed'] += 1
            self.failed_files.append(file_path)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="文件整理工具")
    parser.add_argument("--root", help="项目根目录", default=ROOT_DIR)
    parser.add_argument("--reference", help="参考文件目录", default=REFERENCE_DIR)
    parser.add_argument("--dry-run", action="store_true", help="仅模拟操作而不实际修改文件")
    parser.add_argument("--unwanted-only", action="store_true", help="仅处理不需要的文件")
    parser.add_argument("--redundancy-only", action="store_true", help="仅处理冗余文件")
    parser.add_argument("--skip-redundancy", action="store_true", help="跳过冗余检查")
    parser.add_argument("--print-unwanted", action="store_true", help="打印不需要的文件列表而不移动")
    parser.add_argument("--include-pattern", help="额外的不需要文件模式", action="append")
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    # 添加额外的不需要文件模式
    if args.include_pattern:
        for pattern in args.include_pattern:
            if pattern not in UNWANTED_PATTERNS:
                UNWANTED_PATTERNS.append(pattern)
    
    # 创建文件整理器
    organizer = FileOrganizer(
        root_dir=args.root, 
        reference_dir=args.reference,
        dry_run=args.dry_run
    )
    
    # 执行整理
    if args.redundancy_only:
        # 仅处理冗余文件
        files = organizer.scan_project()
        redundancies = organizer.find_redundancies(files)
        
        if redundancies and not args.dry_run:
            logger.info("正在处理冗余文件组...")
            for group_name, group_files in redundancies.items():
                logger.info(f"处理组 '{group_name}' ({len(group_files)} 个文件)")
                organizer._consolidate_redundant_files(group_name, group_files)
                
        # 输出冗余文件信息
        if redundancies:
            logger.info("找到以下冗余文件组:")
            for group_name, group_files in redundancies.items():
                logger.info(f"  组 '{group_name}' 包含 {len(group_files)} 个相关文件")
                for file_path in group_files:
                    logger.info(f"    - {file_path}")
    else:
        # 完整整理
        organizer.organize_project()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 