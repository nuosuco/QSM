#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
项目量子化转换工具
将项目中的所有文件转换为量子格式（QEntl, QPy, QJS等）
提供更灵活的转换选项和详细的进度报告
"""

import os
import sys
import time
import argparse
import subprocess
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"quantum_conversion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# 项目模块
MODULES = [
    "QSM", "WeQ", "SOM", "Ref", "world", "scripts", "tests", "docs"
]

def setup_parser():
    """设置命令行参数解析器"""
    parser = argparse.ArgumentParser(description="项目量子化转换工具")
    parser.add_argument('--modules', nargs='+', choices=MODULES + ['all'], default=['all'],
                        help='指定要转换的模块，默认为全部')
    parser.add_argument('--dry-run', action='store_true', 
                        help='干运行模式，不实际执行转换')
    parser.add_argument('--skip-errors', action='store_true',
                        help='遇到错误时继续执行')
    parser.add_argument('--verbose', action='store_true',
                        help='显示详细日志')
    parser.add_argument('--backup', action='store_true',
                        help='在转换前创建备份')
    return parser

def create_backup():
    """创建项目备份"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"正在创建项目备份到 {backup_dir}...")
    
    # 简单备份实现，实际应用中可能需要更复杂的逻辑
    try:
        import shutil
        os.makedirs(backup_dir, exist_ok=True)
        
        for module in MODULES:
            if os.path.exists(module):
                shutil.copytree(module, os.path.join(backup_dir, module))
        
        logger.info(f"备份已完成，保存在 {backup_dir}")
        return True
    except Exception as e:
        logger.error(f"备份失败: {str(e)}")
        return False

def convert_module(module, dry_run=False, verbose=False):
    """转换单个模块"""
    logger.info(f"开始转换模块: {module}")
    
    converter_path = os.path.join("scripts", "utils", "quantum_converter.qpy")
    if not os.path.exists(converter_path):
        logger.error(f"错误: 转换脚本 {converter_path} 不存在!")
        return False
    
    cmd = ["python", converter_path, "--module", module]
    if dry_run:
        cmd.append("--dry-run")
    if verbose:
        cmd.append("--verbose")
    
    try:
        logger.info(f"执行命令: {' '.join(cmd)}")
        if not dry_run:
            process = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if verbose:
                logger.info(process.stdout)
            if process.stderr:
                logger.warning(process.stderr)
        else:
            logger.info(f"[干运行] 将执行: {' '.join(cmd)}")
        
        logger.info(f"模块 {module} 转换完成")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"模块 {module} 转换失败: {str(e)}")
        if hasattr(e, 'stdout') and e.stdout:
            logger.error(f"输出: {e.stdout}")
        if hasattr(e, 'stderr') and e.stderr:
            logger.error(f"错误: {e.stderr}")
        return False

def main():
    """主函数"""
    parser = setup_parser()
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("="*50)
    logger.info("项目量子化转换工具")
    logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*50)
    
    # 创建备份
    if args.backup and not args.dry_run:
        if not create_backup():
            if not args.skip_errors:
                logger.error("备份失败，中止转换")
                return 1
    
    # 确定要转换的模块
    modules_to_convert = MODULES if 'all' in args.modules else args.modules
    logger.info(f"将要转换的模块: {', '.join(modules_to_convert)}")
    
    # 执行转换
    successful = 0
    failed = 0
    
    for i, module in enumerate(modules_to_convert, 1):
        logger.info(f"[{i}/{len(modules_to_convert)}] 处理模块: {module}")
        
        if convert_module(module, args.dry_run, args.verbose):
            successful += 1
        else:
            failed += 1
            if not args.skip_errors:
                logger.error(f"转换模块 {module} 失败，中止后续转换")
                break
    
    # 输出结果统计
    logger.info("="*50)
    logger.info("转换完成统计")
    logger.info(f"成功: {successful}")
    logger.info(f"失败: {failed}")
    logger.info(f"总计: {len(modules_to_convert)}")
    logger.info(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*50)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 