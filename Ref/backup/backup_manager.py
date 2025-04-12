#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ref系统备份管理工具

此脚本用于管理Ref系统的备份，包括：
1. 列出所有备份
2. 查看备份信息
3. 检查备份完整性
4. 清理过期备份
5. 生成备份报告
6. 比较备份差异
"""

import os
import sys
import json
import time
import shutil
import logging
import argparse
import datetime
import re
from pathlib import Path
import difflib
from collections import defaultdict

# 获取项目根目录
current_file = os.path.abspath(__file__)
backup_dir = os.path.dirname(current_file)
ref_dir = os.path.dirname(backup_dir)
project_root = os.path.dirname(ref_dir)

# 导入日志配置
sys.path.append(project_root)
try:
    from scripts.log_config import get_logger
except ImportError:
    # 简易日志配置作为备份
    def get_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        return logger

# 获取日志记录器
logger = get_logger('backup_manager')

# 备份目录
BACKUP_DIR = backup_dir
SYSTEM_BACKUP_DIR = os.path.join(BACKUP_DIR, 'system')

def get_backup_dirs():
    """
    获取所有备份目录
    
    Returns:
        list: 按时间戳排序的备份目录列表
    """
    backup_dirs = []
    pattern = r'system_backup_(\d{8})_(\d{6})'
    
    for item in os.listdir(BACKUP_DIR):
        item_path = os.path.join(BACKUP_DIR, item)
        if os.path.isdir(item_path) and re.match(pattern, item):
            backup_dirs.append(item_path)
    
    # 按创建时间排序
    return sorted(backup_dirs, key=lambda x: os.path.getctime(x), reverse=True)

def get_backup_info(backup_path):
    """
    获取备份信息
    
    Args:
        backup_path: 备份目录路径
        
    Returns:
        dict: 备份信息字典
    """
    info = {
        'path': backup_path,
        'name': os.path.basename(backup_path),
        'created': datetime.datetime.fromtimestamp(os.path.getctime(backup_path)).strftime('%Y-%m-%d %H:%M:%S'),
        'modified': datetime.datetime.fromtimestamp(os.path.getmtime(backup_path)).strftime('%Y-%m-%d %H:%M:%S'),
        'size': 0,
        'files': 0,
        'config': {}
    }
    
    # 计算总大小和文件数
    for root, dirs, files in os.walk(backup_path):
        info['files'] += len(files)
        for file in files:
            file_path = os.path.join(root, file)
            try:
                info['size'] += os.path.getsize(file_path)
            except (OSError, FileNotFoundError):
                continue
                
    # 格式化大小
    size_bytes = info['size']
    if size_bytes < 1024:
        info['size_formatted'] = f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        info['size_formatted'] = f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        info['size_formatted'] = f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        info['size_formatted'] = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
    # 读取配置信息
    config_path = os.path.join(backup_path, 'backup_config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                info['config'] = json.load(f)
        except Exception as e:
            logger.error(f"读取备份配置失败: {str(e)}")
    
    return info

def list_backups(verbose=False):
    """
    列出所有备份
    
    Args:
        verbose: 是否显示详细信息
        
    Returns:
        list: 备份信息列表
    """
    backup_dirs = get_backup_dirs()
    
    if not backup_dirs:
        logger.info("未找到任何备份")
        return []
    
    backups = []
    for backup_dir in backup_dirs:
        info = get_backup_info(backup_dir)
        backups.append(info)
        
        if verbose:
            print(f"备份: {info['name']}")
            print(f"  路径: {info['path']}")
            print(f"  创建时间: {info['created']}")
            print(f"  修改时间: {info['modified']}")
            print(f"  大小: {info['size_formatted']} ({info['size']} 字节)")
            print(f"  文件数: {info['files']}")
            if info['config']:
                print("  配置信息:")
                for key, value in info['config'].items():
                    print(f"    {key}: {value}")
            print()
        else:
            print(f"{info['name']} - {info['created']} - {info['size_formatted']}")
    
    return backups

def check_backup_integrity(backup_path):
    """
    检查备份完整性
    
    Args:
        backup_path: 备份目录路径
        
    Returns:
        tuple: (完整性状态, 问题列表)
    """
    if not os.path.exists(backup_path):
        return False, ["备份目录不存在"]
    
    problems = []
    required_dirs = ['code', 'config', 'data']
    required_files = ['backup_config.json', 'backup_metadata.json']
    
    for dir_name in required_dirs:
        dir_path = os.path.join(backup_path, dir_name)
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            problems.append(f"缺少必要目录: {dir_name}")
    
    for file_name in required_files:
        file_path = os.path.join(backup_path, file_name)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            problems.append(f"缺少必要文件: {file_name}")
            continue
            
        # 检查配置文件是否为有效的JSON
        if file_name.endswith('.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError:
                problems.append(f"文件格式无效: {file_name}")
    
    is_valid = len(problems) == 0
    return is_valid, problems

def clean_old_backups(days=30, max_backups=10, dry_run=False):
    """
    清理过期备份
    
    Args:
        days: 保留最近多少天的备份
        max_backups: 最多保留的备份数量
        dry_run: 是否只模拟操作
        
    Returns:
        tuple: (删除的备份数量, 删除的字节数)
    """
    backup_dirs = get_backup_dirs()
    
    if not backup_dirs:
        logger.info("未找到任何备份")
        return 0, 0
    
    # 计算截止日期
    cutoff_date = time.time() - (days * 24 * 60 * 60)
    
    # 保留的备份
    kept_backups = []
    
    # 首先保留最近的max_backups个备份
    kept_backups.extend(backup_dirs[:max_backups])
    
    # 然后保留最近days天内的备份
    for backup_dir in backup_dirs[max_backups:]:
        if os.path.getctime(backup_dir) >= cutoff_date:
            kept_backups.append(backup_dir)
    
    # 需要删除的备份
    to_delete = [d for d in backup_dirs if d not in kept_backups]
    
    if not to_delete:
        logger.info("没有需要清理的备份")
        return 0, 0
    
    deleted_count = 0
    deleted_bytes = 0
    
    for backup_dir in to_delete:
        # 计算大小
        size = 0
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size += os.path.getsize(file_path)
                except (OSError, FileNotFoundError):
                    continue
        
        # 删除备份
        if dry_run:
            logger.info(f"[模拟] 将删除备份: {os.path.basename(backup_dir)} ({size} 字节)")
        else:
            try:
                shutil.rmtree(backup_dir)
                logger.info(f"已删除备份: {os.path.basename(backup_dir)} ({size} 字节)")
                deleted_count += 1
                deleted_bytes += size
            except Exception as e:
                logger.error(f"删除备份失败: {str(e)}")
    
    mode = "[模拟] " if dry_run else ""
    logger.info(f"{mode}清理完成，{deleted_count} 个备份被删除, 释放空间 {deleted_bytes/(1024*1024):.2f} MB")
    
    return deleted_count, deleted_bytes

def create_backup_report(output=None):
    """
    生成备份报告
    
    Args:
        output: 输出文件路径，None表示输出到stdout
        
    Returns:
        str: 报告内容
    """
    backups = list_backups(verbose=False)
    
    if not backups:
        report = "未找到任何备份"
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(report)
        else:
            print(report)
        return report
    
    total_size = sum(b['size'] for b in backups)
    total_files = sum(b['files'] for b in backups)
    
    # 格式化总大小
    if total_size < 1024:
        total_size_fmt = f"{total_size} B"
    elif total_size < 1024 * 1024:
        total_size_fmt = f"{total_size / 1024:.2f} KB"
    elif total_size < 1024 * 1024 * 1024:
        total_size_fmt = f"{total_size / (1024 * 1024):.2f} MB"
    else:
        total_size_fmt = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
    
    # 生成报告
    report = "# Ref 系统备份报告\n\n"
    report += f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report += f"备份总数: {len(backups)}\n"
    report += f"总大小: {total_size_fmt} ({total_size} 字节)\n"
    report += f"总文件数: {total_files}\n\n"
    
    # 备份列表
    report += "## 备份列表\n\n"
    report += "| 备份名称 | 创建时间 | 大小 | 文件数 |\n"
    report += "|---------|----------|------|--------|\n"
    
    for backup in backups:
        report += f"| {backup['name']} | {backup['created']} | {backup['size_formatted']} | {backup['files']} |\n"
    
    # 完整性检查
    report += "\n## 完整性检查\n\n"
    for backup in backups:
        is_valid, problems = check_backup_integrity(backup['path'])
        status = "✅ 正常" if is_valid else "❌ 异常"
        report += f"### {backup['name']} - {status}\n\n"
        
        if not is_valid:
            report += "问题：\n"
            for problem in problems:
                report += f"- {problem}\n"
            report += "\n"
    
    # 输出报告
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"报告已保存到: {output}")
    else:
        print(report)
    
    return report

def compare_backups(backup1, backup2):
    """
    比较两个备份的差异
        
        Args:
        backup1: 第一个备份路径
        backup2: 第二个备份路径
        
    Returns:
        dict: 差异信息
    """
    if not os.path.exists(backup1):
        raise FileNotFoundError(f"备份不存在: {backup1}")
    if not os.path.exists(backup2):
        raise FileNotFoundError(f"备份不存在: {backup2}")
    
    # 获取备份信息
    info1 = get_backup_info(backup1)
    info2 = get_backup_info(backup2)
    
    # 收集两个备份中的所有文件
    files1 = {}
    files2 = {}
    
    for root, dirs, files in os.walk(backup1):
        rel_path = os.path.relpath(root, backup1)
        for file in files:
            file_path = os.path.join(root, file)
            rel_file_path = os.path.join(rel_path, file).replace('\\', '/')
            if rel_file_path.startswith('./'):
                rel_file_path = rel_file_path[2:]
            
            try:
                mtime = os.path.getmtime(file_path)
                size = os.path.getsize(file_path)
                files1[rel_file_path] = {
                    'mtime': mtime,
                    'size': size,
                    'path': file_path
                }
            except (OSError, FileNotFoundError):
                continue
    
    for root, dirs, files in os.walk(backup2):
        rel_path = os.path.relpath(root, backup2)
        for file in files:
            file_path = os.path.join(root, file)
            rel_file_path = os.path.join(rel_path, file).replace('\\', '/')
            if rel_file_path.startswith('./'):
                rel_file_path = rel_file_path[2:]
            
            try:
                mtime = os.path.getmtime(file_path)
                size = os.path.getsize(file_path)
                files2[rel_file_path] = {
                    'mtime': mtime,
                    'size': size,
                    'path': file_path
                }
            except (OSError, FileNotFoundError):
                continue
    
    # 比较文件
    all_files = sorted(set(list(files1.keys()) + list(files2.keys())))
    
    diff = {
        'backup1': info1['name'],
        'backup2': info2['name'],
        'only_in_1': [],
        'only_in_2': [],
        'modified': [],
        'same': [],
        'summary': {
            'total_files': len(all_files),
            'only_in_1': 0,
            'only_in_2': 0,
            'modified': 0,
            'same': 0
        }
    }
    
    for file in all_files:
        if file in files1 and file not in files2:
            diff['only_in_1'].append(file)
            diff['summary']['only_in_1'] += 1
        elif file not in files1 and file in files2:
            diff['only_in_2'].append(file)
            diff['summary']['only_in_2'] += 1
        elif file in files1 and file in files2:
            # 比较文件大小和修改时间
            if abs(files1[file]['size'] - files2[file]['size']) > 0:
                diff['modified'].append(file)
                diff['summary']['modified'] += 1
            elif abs(files1[file]['mtime'] - files2[file]['mtime']) > 1:  # 允许1秒的差异
                # 对于时间不同但大小相同的文件，比较内容
                try:
                    with open(files1[file]['path'], 'rb') as f1, open(files2[file]['path'], 'rb') as f2:
                        if f1.read() == f2.read():
                            diff['same'].append(file)
                            diff['summary']['same'] += 1
                        else:
                            diff['modified'].append(file)
                            diff['summary']['modified'] += 1
                except Exception:
                    # 如果无法比较，认为已修改
                    diff['modified'].append(file)
                    diff['summary']['modified'] += 1
            else:
                diff['same'].append(file)
                diff['summary']['same'] += 1
    
    # 打印差异摘要
    print(f"比较 {info1['name']} 和 {info2['name']} 的差异")
    print(f"总文件数: {diff['summary']['total_files']}")
    print(f"仅在 {info1['name']} 中存在: {diff['summary']['only_in_1']}")
    print(f"仅在 {info2['name']} 中存在: {diff['summary']['only_in_2']}")
    print(f"已修改: {diff['summary']['modified']}")
    print(f"相同: {diff['summary']['same']}")
    
    return diff

def create_metadata_for_system_backup():
    """
    为system_backup创建元数据文件
    """
    system_backup_files = {
        'backup_config.json': {
            'description': '备份配置文件',
            'version': '1.0.0',
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'backup_type': 'system',
            'retention_days': 30,
            'max_backups': 10
        },
        'backup_metadata.json': {
            'description': '系统备份元数据',
            'version': '1.0.0',
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'files': [],
            'directories': ['code', 'config', 'data']
        }
    }
    
    # system目录
    os.makedirs(SYSTEM_BACKUP_DIR, exist_ok=True)
    for subdir in ['code', 'config', 'data']:
        os.makedirs(os.path.join(SYSTEM_BACKUP_DIR, subdir), exist_ok=True)
    
    # 创建配置文件
    for filename, content in system_backup_files.items():
        file_path = os.path.join(SYSTEM_BACKUP_DIR, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    
    logger.info(f"系统备份元数据已创建: {SYSTEM_BACKUP_DIR}")
    
    return SYSTEM_BACKUP_DIR

def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='Ref系统备份管理工具')
    
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # list命令
    list_parser = subparsers.add_parser('list', help='列出所有备份')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    
    # info命令
    info_parser = subparsers.add_parser('info', help='查看备份信息')
    info_parser.add_argument('backup', help='备份名称或路径')
    
    # check命令
    check_parser = subparsers.add_parser('check', help='检查备份完整性')
    check_parser.add_argument('backup', help='备份名称或路径')
    
    # clean命令
    clean_parser = subparsers.add_parser('clean', help='清理过期备份')
    clean_parser.add_argument('--days', type=int, default=30, help='保留最近多少天的备份')
    clean_parser.add_argument('--max', type=int, default=10, help='最多保留的备份数量')
    clean_parser.add_argument('--dry-run', action='store_true', help='只模拟操作，不实际删除')
    
    # report命令
    report_parser = subparsers.add_parser('report', help='生成备份报告')
    report_parser.add_argument('--output', help='输出文件路径')
    
    # compare命令
    compare_parser = subparsers.add_parser('compare', help='比较备份差异')
    compare_parser.add_argument('backup1', help='第一个备份名称或路径')
    compare_parser.add_argument('backup2', help='第二个备份名称或路径')
    
    # init-metadata命令
    init_metadata_parser = subparsers.add_parser('init-metadata', help='初始化system_backup元数据')
    
    args = parser.parse_args()
    
    # 如果没有命令，显示帮助
    if args.command is None:
        parser.print_help()
        return
    
    try:
        # 执行对应命令
        if args.command == 'list':
            list_backups(args.verbose)
        
        elif args.command == 'info':
            backup_path = args.backup
            if not os.path.isabs(backup_path):
                backup_path = os.path.join(BACKUP_DIR, backup_path)
            
            if not os.path.exists(backup_path):
                logger.error(f"备份不存在: {backup_path}")
                return
            
            info = get_backup_info(backup_path)
            print(f"备份: {info['name']}")
            print(f"  路径: {info['path']}")
            print(f"  创建时间: {info['created']}")
            print(f"  修改时间: {info['modified']}")
            print(f"  大小: {info['size_formatted']} ({info['size']} 字节)")
            print(f"  文件数: {info['files']}")
            if info['config']:
                print("  配置信息:")
                for key, value in info['config'].items():
                    print(f"    {key}: {value}")
        
        elif args.command == 'check':
            backup_path = args.backup
            if not os.path.isabs(backup_path):
                backup_path = os.path.join(BACKUP_DIR, backup_path)
            
            if not os.path.exists(backup_path):
                logger.error(f"备份不存在: {backup_path}")
                return
            
            is_valid, problems = check_backup_integrity(backup_path)
            
            if is_valid:
                print(f"备份 {os.path.basename(backup_path)} 完整性检查通过")
            else:
                print(f"备份 {os.path.basename(backup_path)} 完整性检查失败")
                print("问题:")
                for problem in problems:
                    print(f"  - {problem}")
        
        elif args.command == 'clean':
            clean_old_backups(args.days, args.max, args.dry_run)
        
        elif args.command == 'report':
            create_backup_report(args.output)
        
        elif args.command == 'compare':
            backup1 = args.backup1
            backup2 = args.backup2
            
            if not os.path.isabs(backup1):
                backup1 = os.path.join(BACKUP_DIR, backup1)
            if not os.path.isabs(backup2):
                backup2 = os.path.join(BACKUP_DIR, backup2)
            
            if not os.path.exists(backup1):
                logger.error(f"备份不存在: {backup1}")
                return
            if not os.path.exists(backup2):
                logger.error(f"备份不存在: {backup2}")
                return
            
            compare_backups(backup1, backup2)
        
        elif args.command == 'init-metadata':
            create_metadata_for_system_backup()
    
    except Exception as e:
        logger.error(f"执行命令 {args.command} 失败: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    main()

"""

"""
量子基因编码: QE-BAC-D096B08AEFAB
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
