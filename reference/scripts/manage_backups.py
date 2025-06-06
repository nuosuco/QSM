#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ref备份管理工具

此脚本用于：
1. 检查Ref备份目录的状态和大小
2. 清理过期备份
3. 生成备份报告
4. 比较备份之间的差异
"""

import os
import sys
import time
import shutil
import logging
import argparse
import traceback
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

try:
    from scripts.log_config import get_logger
    logger = get_logger('ref_backup_manager')
except ImportError:
    # 配置基本日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('.logs/ref_backup_manager.log', encoding='utf-8', mode='a')
        ]
    )
    logger = logging.getLogger('ref_backup_manager')

# 获取项目根目录
current_file = os.path.abspath(__file__)
script_dir = os.path.dirname(current_file)
project_root = os.path.dirname(script_dir)

# Ref备份目录路径
ref_dir = os.path.join(project_root, 'Ref')
backup_dir = os.path.join(ref_dir, 'backup')
system_backup_dir = os.path.join(backup_dir, 'system')

# 确保日志目录存在
logs_dir = os.path.join(project_root, '.logs')
os.makedirs(logs_dir, exist_ok=True)

# 备份模式常量
BACKUP_MODE_FULL = 'full'
BACKUP_MODE_INCREMENTAL = 'incremental'
BACKUP_MODE_DIFFERENTIAL = 'differential'

def get_backup_dirs():
    """
    获取所有备份目录
    
    Returns:
        list: 备份目录列表，按照时间排序
    """
    if not os.path.exists(backup_dir):
        logger.warning(f"备份目录不存在: {backup_dir}")
        return []
    
    backup_dirs = []
    
    try:
        # 获取system目录
        if os.path.exists(system_backup_dir) and os.path.isdir(system_backup_dir):
            backup_dirs.append(('system', system_backup_dir, None))
        
        # 获取时间戳备份目录
        pattern = re.compile(r'system_backup_(\d{8})_(\d{6})')
        
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            if os.path.isdir(item_path):
                match = pattern.match(item)
                if match:
                    try:
                        date_str = match.group(1)
                        time_str = match.group(2)
                        timestamp = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                        backup_dirs.append((item, item_path, timestamp))
                    except ValueError:
                        logger.warning(f"无法解析备份目录名称: {item}")
        
        # 按时间戳排序，最新的在前面
        backup_dirs.sort(key=lambda x: x[2] if x[2] else datetime.max, reverse=True)
        
        return backup_dirs
    
    except Exception as e:
        logger.error(f"获取备份目录时出错: {str(e)}")
        return []

def get_backup_info(backup_path):
    """
    获取备份的详细信息
    
    Args:
        backup_path: 备份目录路径
        
    Returns:
        dict: 备份信息
    """
    if not os.path.exists(backup_path):
        logger.warning(f"备份路径不存在: {backup_path}")
        return {}
    
    try:
        # 基本信息
        backup_name = os.path.basename(backup_path)
        create_time = datetime.fromtimestamp(os.path.getctime(backup_path))
        modify_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
        
        # 计算大小
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(backup_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except OSError:
                    pass
        
        # 查找备份配置文件
        backup_config = {}
        config_path = os.path.join(backup_path, 'backup_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    backup_config = json.load(f)
            except Exception as e:
                logger.warning(f"无法读取备份配置文件: {str(e)}")
        
        # 返回信息
        return {
            'name': backup_name,
            'path': backup_path,
            'create_time': create_time,
            'modify_time': modify_time,
            'size': total_size,
            'size_mb': total_size / (1024 * 1024),
            'file_count': file_count,
            'config': backup_config,
            'mode': backup_config.get('mode', '未知')
        }
    
    except Exception as e:
        logger.error(f"获取备份信息时出错: {str(e)}")
        return {}

def list_backups(verbose=False):
    """
    列出所有备份
    
    Args:
        verbose: 是否显示详细信息
    """
    backup_dirs = get_backup_dirs()
    
    if not backup_dirs:
        logger.info("没有找到任何备份")
        return
    
    logger.info(f"找到 {len(backup_dirs)} 个备份:")
    
    for i, (name, path, timestamp) in enumerate(backup_dirs):
        logger.info(f"{i+1}. {name} {'(永久存储)' if timestamp is None else ''}")
        
        if verbose:
            info = get_backup_info(path)
            
            if info:
                logger.info(f"   路径: {path}")
                logger.info(f"   创建时间: {info['create_time']}")
                logger.info(f"   修改时间: {info['modify_time']}")
                logger.info(f"   大小: {info['size_mb']:.2f} MB")
                logger.info(f"   文件数: {info['file_count']}")
                logger.info(f"   备份模式: {info['mode']}")
                logger.info("")

def check_backup_integrity(backup_path):
    """
    检查备份完整性
    
    Args:
        backup_path: 备份目录路径
        
    Returns:
        bool: 是否完整
    """
    if not os.path.exists(backup_path):
        logger.warning(f"备份路径不存在: {backup_path}")
        return False
    
    try:
        # 检查必要的文件和目录
        required_dirs = ['models', 'data']
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = os.path.join(backup_path, dir_name)
            if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            logger.warning(f"备份不完整，缺少以下目录: {', '.join(missing_dirs)}")
            return False
        
        # 检查配置文件
        config_path = os.path.join(backup_path, 'backup_config.json')
        if not os.path.exists(config_path):
            logger.warning(f"备份不完整，缺少配置文件")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"检查备份完整性时出错: {str(e)}")
        return False

def clean_old_backups(days=30, max_backups=10, dry_run=False):
    """
    清理旧备份
    
    Args:
        days: 保留天数
        max_backups: 最大保留备份数
        dry_run: 是否仅模拟操作
        
    Returns:
        int: 清理的备份数量
    """
    backup_dirs = get_backup_dirs()
    
    if not backup_dirs:
        logger.info("没有找到任何备份")
        return 0
    
    # 过滤永久存储的系统备份
    backup_dirs = [(name, path, timestamp) for name, path, timestamp in backup_dirs if timestamp is not None]
    
    # 保留最新的max_backups个备份和days天内的备份
    now = datetime.now()
    cutoff_date = now - timedelta(days=days)
    
    # 保留的备份
    keep_backups = []
    
    # 首先保留最新的max_backups个备份
    keep_backups.extend(backup_dirs[:max_backups])
    
    # 然后保留days天内的备份
    for backup in backup_dirs[max_backups:]:
        name, path, timestamp = backup
        if timestamp >= cutoff_date:
            keep_backups.append(backup)
    
    # 需要删除的备份
    delete_backups = [backup for backup in backup_dirs if backup not in keep_backups]
    
    if not delete_backups:
        logger.info("没有需要清理的备份")
        return 0
    
    logger.info(f"将清理 {len(delete_backups)} 个备份:")
    
    deleted_count = 0
    
    for name, path, timestamp in delete_backups:
        if not dry_run:
            try:
                logger.info(f"正在删除: {name} ({timestamp})")
                shutil.rmtree(path)
                deleted_count += 1
            except Exception as e:
                logger.error(f"删除备份 {name} 时出错: {str(e)}")
        else:
            logger.info(f"[模拟删除]: {name} ({timestamp})")
            deleted_count += 1
    
    return deleted_count

def create_backup_report(output=None):
    """
    创建备份报告
    
    Args:
        output: 输出文件路径，None则输出到日志
    """
    backup_dirs = get_backup_dirs()
    
    if not backup_dirs:
        logger.info("没有找到任何备份")
        return
    
    # 收集报告数据
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_backups': len(backup_dirs),
        'backups': [],
        'total_size': 0,
        'avg_size': 0,
        'oldest_backup': None,
        'newest_backup': None
    }
    
    for name, path, timestamp in backup_dirs:
        info = get_backup_info(path)
        if info:
            backup_data = {
                'name': name,
                'timestamp': timestamp.isoformat() if timestamp else '永久存储',
                'size_mb': info['size_mb'],
                'file_count': info['file_count'],
                'mode': info['mode']
            }
            report['backups'].append(backup_data)
            report['total_size'] += info['size']
    
    # 计算统计数据
    if report['backups']:
        report['avg_size'] = report['total_size'] / len(report['backups']) / (1024 * 1024)
        report['total_size_mb'] = report['total_size'] / (1024 * 1024)
        
        timestamped_backups = [b for name, path, timestamp in backup_dirs if timestamp is not None]
        if timestamped_backups:
            report['oldest_backup'] = min(timestamped_backups, key=lambda x: x[2])[0]
            report['newest_backup'] = max(timestamped_backups, key=lambda x: x[2])[0]
    
    # 输出报告
    if output:
        try:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            logger.info(f"备份报告已保存到: {output}")
        except Exception as e:
            logger.error(f"保存报告时出错: {str(e)}")
    else:
        logger.info("\n备份报告:")
        logger.info(f"总备份数: {report['total_backups']}")
        logger.info(f"总备份大小: {report.get('total_size_mb', 0):.2f} MB")
        logger.info(f"平均备份大小: {report.get('avg_size', 0):.2f} MB")
        logger.info(f"最老备份: {report.get('oldest_backup', '无')}")
        logger.info(f"最新备份: {report.get('newest_backup', '无')}")
        logger.info("\n备份列表:")
        
        for backup in report['backups']:
            logger.info(f"{backup['name']} - {backup['timestamp']} - {backup['size_mb']:.2f} MB - {backup['mode']}")

def compare_backups(backup1, backup2):
    """
    比较两个备份的差异
    
    Args:
        backup1: 第一个备份路径
        backup2: 第二个备份路径
    """
    if not os.path.exists(backup1):
        logger.error(f"备份路径不存在: {backup1}")
        return
    
    if not os.path.exists(backup2):
        logger.error(f"备份路径不存在: {backup2}")
        return
    
    logger.info(f"比较备份: {os.path.basename(backup1)} 与 {os.path.basename(backup2)}")
    
    try:
        # 获取两个备份的文件集合
        files1 = set()
        files2 = set()
        
        for root, _, files in os.walk(backup1):
            rel_root = os.path.relpath(root, backup1)
            for file in files:
                rel_path = os.path.join(rel_root, file).replace('\\', '/')
                files1.add(rel_path)
        
        for root, _, files in os.walk(backup2):
            rel_root = os.path.relpath(root, backup2)
            for file in files:
                rel_path = os.path.join(rel_root, file).replace('\\', '/')
                files2.add(rel_path)
        
        # 计算差异
        only_in_1 = files1 - files2
        only_in_2 = files2 - files1
        common = files1.intersection(files2)
        
        # 检查共同文件的内容差异
        modified = []
        
        for file in common:
            path1 = os.path.join(backup1, file)
            path2 = os.path.join(backup2, file)
            
            try:
                size1 = os.path.getsize(path1)
                size2 = os.path.getsize(path2)
                
                if size1 != size2:
                    modified.append(file)
                    continue
                
                # 对于小文件，比较内容
                if size1 < 1024 * 1024:  # 小于1MB
                    with open(path1, 'rb') as f1, open(path2, 'rb') as f2:
                        if f1.read() != f2.read():
                            modified.append(file)
            except Exception:
                # 出错时假设文件不同
                modified.append(file)
        
        # 输出结果
        logger.info(f"文件总数: {len(files1)} (备份1), {len(files2)} (备份2)")
        logger.info(f"共同文件: {len(common)}")
        logger.info(f"修改的文件: {len(modified)}")
        logger.info(f"仅在备份1中存在: {len(only_in_1)}")
        logger.info(f"仅在备份2中存在: {len(only_in_2)}")
        
        # 列出差异文件
        if only_in_1:
            logger.info("\n仅在备份1中存在的文件 (前20个):")
            for file in sorted(list(only_in_1))[:20]:
                logger.info(f"  {file}")
        
        if only_in_2:
            logger.info("\n仅在备份2中存在的文件 (前20个):")
            for file in sorted(list(only_in_2))[:20]:
                logger.info(f"  {file}")
        
        if modified:
            logger.info("\n内容已修改的文件 (前20个):")
            for file in sorted(modified)[:20]:
                logger.info(f"  {file}")
    
    except Exception as e:
        logger.error(f"比较备份时出错: {str(e)}")
        traceback.print_exc()

def create_metadata_for_system_backup():
    """
    为system备份创建元数据文件
    """
    if not os.path.exists(system_backup_dir):
        logger.warning(f"system备份目录不存在: {system_backup_dir}")
        return False
    
    try:
        # 创建配置文件
        config = {
            'mode': BACKUP_MODE_FULL,
            'timestamp': datetime.now().isoformat(),
            'description': '系统永久存储备份',
            'creator': 'ref_backup_manager'
        }
        
        config_path = os.path.join(system_backup_dir, 'backup_config.json')
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"已为system备份创建元数据文件: {config_path}")
        return True
    
    except Exception as e:
        logger.error(f"创建元数据文件时出错: {str(e)}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Ref备份管理工具')
    
    # 操作选项
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list', action='store_true', help='列出所有备份')
    group.add_argument('--info', type=str, help='显示特定备份的详细信息')
    group.add_argument('--clean', action='store_true', help='清理旧备份')
    group.add_argument('--report', action='store_true', help='生成备份报告')
    group.add_argument('--compare', nargs=2, metavar=('BACKUP1', 'BACKUP2'), help='比较两个备份的差异')
    group.add_argument('--metadata', action='store_true', help='为system备份创建元数据文件')
    
    # 附加选项
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    parser.add_argument('--days', type=int, default=30, help='清理时保留多少天的备份')
    parser.add_argument('--max-backups', type=int, default=10, help='最大保留的备份数量')
    parser.add_argument('--dry-run', action='store_true', help='仅模拟操作，不实际执行')
    parser.add_argument('--output', '-o', type=str, help='报告输出文件路径')
    
    args = parser.parse_args()
    
    try:
        # 默认操作是列出备份
        if not (args.list or args.info or args.clean or args.report or args.compare or args.metadata):
            args.list = True
        
        # 列出备份
        if args.list:
            list_backups(args.verbose)
        
        # 显示备份信息
        elif args.info:
            backup_dirs = get_backup_dirs()
            
            try:
                # 尝试作为索引解析
                idx = int(args.info) - 1
                if 0 <= idx < len(backup_dirs):
                    _, path, _ = backup_dirs[idx]
                    info = get_backup_info(path)
                    
                    if info:
                        logger.info(f"备份信息: {info['name']}")
                        logger.info(f"路径: {info['path']}")
                        logger.info(f"创建时间: {info['create_time']}")
                        logger.info(f"修改时间: {info['modify_time']}")
                        logger.info(f"大小: {info['size_mb']:.2f} MB")
                        logger.info(f"文件数: {info['file_count']}")
                        logger.info(f"备份模式: {info['mode']}")
                        
                        if check_backup_integrity(path):
                            logger.info("备份完整性: 完整")
                        else:
                            logger.warning("备份完整性: 不完整")
                else:
                    logger.error(f"无效的备份索引: {args.info}")
            except ValueError:
                # 作为路径解析
                if os.path.exists(args.info):
                    info = get_backup_info(args.info)
                    
                    if info:
                        logger.info(f"备份信息: {info['name']}")
                        logger.info(f"路径: {info['path']}")
                        logger.info(f"创建时间: {info['create_time']}")
                        logger.info(f"修改时间: {info['modify_time']}")
                        logger.info(f"大小: {info['size_mb']:.2f} MB")
                        logger.info(f"文件数: {info['file_count']}")
                        logger.info(f"备份模式: {info['mode']}")
                        
                        if check_backup_integrity(args.info):
                            logger.info("备份完整性: 完整")
                        else:
                            logger.warning("备份完整性: 不完整")
                else:
                    logger.error(f"备份路径不存在: {args.info}")
        
        # 清理旧备份
        elif args.clean:
            deleted = clean_old_backups(args.days, args.max_backups, args.dry_run)
            if deleted > 0:
                if args.dry_run:
                    logger.info(f"模拟清理: 将删除 {deleted} 个备份")
                else:
                    logger.info(f"已清理 {deleted} 个备份")
        
        # 生成备份报告
        elif args.report:
            create_backup_report(args.output)
        
        # 比较备份
        elif args.compare:
            compare_backups(args.compare[0], args.compare[1])
        
        # 为system备份创建元数据文件
        elif args.metadata:
            if create_metadata_for_system_backup():
                logger.info("元数据创建成功")
            else:
                logger.error("元数据创建失败")
    
    except Exception as e:
        logger.error(f"执行出错: {str(e)}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 

"""
"""
量子基因编码: QE-MAN-8DC83A18FCB6
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
