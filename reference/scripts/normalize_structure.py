#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目结构规范化工具

该脚本用于规范化项目结构，确保所有模块和服务遵循一致的目录结构。
主要功能：
1. 检查各个模块的目录结构
2. 将不符合规范的文件移动到正确位置
3. 合并重复的功能模块
4. 删除冗余文件
"""

import os
import shutil
import logging
import sys
import re
import datetime
from pathlib import Path
import argparse

# 设置日志
log_dir = Path('.logs')
log_dir.mkdir(exist_ok=True)
log_filename = f'normalize_structure_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
log_path = log_dir / log_filename

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 主要模块名称
MODULES = ['QSM', 'WeQ', 'SOM', 'Ref']

# 标准目录结构
STANDARD_STRUCTURE = {
    'api': {
        'description': '模块API接口目录',
        'subdirs': ['templates', 'static']
    },
    'core': {
        'description': '核心功能实现',
        'subdirs': []
    },
    'utils': {
        'description': '工具函数',
        'subdirs': []
    },
    'models': {
        'description': '模型定义和存储',
        'subdirs': ['pretrained', 'saved']
    },
    'scripts': {
        'description': '运行脚本',
        'subdirs': ['services', 'tools']
    },
    'tests': {
        'description': '测试代码',
        'subdirs': ['unit', 'integration']
    },
    'docs': {
        'description': '文档',
        'subdirs': ['api', 'examples']
    }
}

# 不应该被移动的文件模式
EXCLUDED_PATTERNS = [
    r'__pycache__',
    r'\.git',
    r'\.vscode',
    r'\.idea',
    r'\.logs',
    r'\.venv',
    r'\.env',
    r'\.bak$',
    r'.*\.pyc$',
    r'^normalize_structure\.py$'
]

def should_exclude(path):
    """判断路径是否应该被排除"""
    for pattern in EXCLUDED_PATTERNS:
        if re.search(pattern, str(path)):
            return True
    return False

def ensure_standard_structure(module_path):
    """确保模块目录符合标准结构"""
    module_path = Path(module_path)
    if not module_path.exists():
        logger.info(f"创建模块目录: {module_path}")
        module_path.mkdir(parents=True, exist_ok=True)
    
    # 创建标准目录结构
    for dir_name, dir_info in STANDARD_STRUCTURE.items():
        dir_path = module_path / dir_name
        if not dir_path.exists():
            logger.info(f"创建目录: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        for subdir in dir_info['subdirs']:
            subdir_path = dir_path / subdir
            if not subdir_path.exists():
                logger.info(f"创建子目录: {subdir_path}")
                subdir_path.mkdir(parents=True, exist_ok=True)

def identify_misplaced_files(root_dir):
    """识别不符合规范的文件"""
    misplaced_files = []
    root_path = Path(root_dir)
    
    for module in MODULES:
        module_path = root_path / module
        if not module_path.exists():
            continue
        
        for item in module_path.glob('**/*'):
            if item.is_file() and not should_exclude(item):
                relative_path = item.relative_to(module_path)
                parts = relative_path.parts
                
                # 检查文件是否在标准目录结构中
                if len(parts) > 0 and parts[0] not in STANDARD_STRUCTURE:
                    target_dir = determine_target_dir(item, module_path)
                    if target_dir:
                        misplaced_files.append((item, target_dir))
    
    return misplaced_files

def determine_target_dir(file_path, module_path):
    """根据文件类型确定目标目录"""
    file_name = file_path.name
    file_content = ''
    try:
        if file_path.suffix.lower() in ['.py', '.md', '.txt', '.json', '.yml', '.yaml']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read(4096)  # 只读取前4096字节
    except Exception as e:
        logger.warning(f"无法读取文件 {file_path}: {e}")
    
    # 基于文件名和内容的简单分类规则
    if re.search(r'api|flask|http|rest|route', file_name.lower() + '\n' + file_content.lower()):
        return module_path / 'api'
    elif re.search(r'test|spec', file_name.lower()):
        return module_path / 'tests'
    elif re.search(r'model|train|predict|inference', file_name.lower() + '\n' + file_content.lower()):
        return module_path / 'models'
    elif re.search(r'script|run|start|stop|service', file_name.lower()):
        return module_path / 'scripts'
    elif re.search(r'util|helper|tool', file_name.lower() + '\n' + file_content.lower()):
        return module_path / 'utils'
    elif re.search(r'doc|readme|guide|tutorial', file_name.lower()):
        return module_path / 'docs'
    else:
        return module_path / 'core'

def move_files(files_to_move, dry_run=True):
    """移动文件到正确位置"""
    for source, target_dir in files_to_move:
        target = target_dir / source.name
        target_dir.mkdir(parents=True, exist_ok=True)
        
        if dry_run:
            logger.info(f"将移动: {source} -> {target}")
        else:
            try:
                if target.exists():
                    logger.warning(f"目标文件已存在，跳过: {target}")
                    continue
                
                logger.info(f"移动: {source} -> {target}")
                shutil.copy2(source, target)
                os.remove(source)
            except Exception as e:
                logger.error(f"移动文件时出错 {source} -> {target}: {e}")

def unify_services_directory(root_dir, dry_run=True):
    """统一服务脚本目录"""
    root_path = Path(root_dir)
    services_dir = root_path / 'scripts' / 'services'
    services_dir.mkdir(parents=True, exist_ok=True)
    
    for module in MODULES:
        module_services = root_path / module / 'scripts' / 'services'
        if not module_services.exists():
            continue
        
        for service_file in module_services.glob('*'):
            if service_file.is_file() and not should_exclude(service_file):
                target = services_dir / service_file.name
                
                if dry_run:
                    logger.info(f"将统一服务脚本: {service_file} -> {target}")
                else:
                    try:
                        if target.exists():
                            logger.warning(f"目标服务脚本已存在，跳过: {target}")
                            continue
                        
                        logger.info(f"统一服务脚本: {service_file} -> {target}")
                        shutil.copy2(service_file, target)
                    except Exception as e:
                        logger.error(f"统一服务脚本时出错 {service_file} -> {target}: {e}")

def main():
    parser = argparse.ArgumentParser(description='项目结构规范化工具')
    parser.add_argument('--dry-run', action='store_true', help='仅显示将要执行的操作，不实际修改文件')
    parser.add_argument('--modules', nargs='+', default=MODULES, help='要处理的模块列表')
    args = parser.parse_args()
    
    logger.info(f"开始规范化项目结构{'（试运行模式）' if args.dry_run else ''}")
    logger.info(f"要处理的模块: {', '.join(args.modules)}")
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logger.info(f"项目根目录: {root_dir}")
    
    # 确保每个模块有标准目录结构
    for module in args.modules:
        module_path = os.path.join(root_dir, module)
        logger.info(f"处理模块: {module}")
        ensure_standard_structure(module_path)
    
    # 处理不符合规范的文件
    logger.info("识别不符合规范的文件...")
    misplaced_files = identify_misplaced_files(root_dir)
    logger.info(f"找到 {len(misplaced_files)} 个不符合规范的文件")
    
    if misplaced_files:
        move_files(misplaced_files, args.dry_run)
    
    # 统一服务脚本目录
    logger.info("统一服务脚本目录...")
    unify_services_directory(root_dir, args.dry_run)
    
    logger.info(f"项目结构规范化{'试运行' if args.dry_run else '执行'}完成！")
    logger.info(f"详细日志已保存至: {log_path}")

if __name__ == "__main__":
    main() 