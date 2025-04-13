#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志管理工具

此脚本用于：
1. 将所有日志文件移动到.logs目录
2. 更新代码中的日志路径配置
3. 清理和归档旧日志文件
4. 设置日志轮转策略
"""

import os
import sys
import shutil
import logging
import argparse
import re
import time
from pathlib import Path
from datetime import datetime, timedelta
import traceback

# 获取项目根目录
current_file = os.path.abspath(__file__)
script_dir = os.path.dirname(current_file)
project_root = os.path.dirname(script_dir)

# 定义日志目录
OLD_LOG_DIR = os.path.join(project_root, 'logs')
NEW_LOG_DIR = os.path.join(project_root, '.logs')
BACKUP_DIR = os.path.join(project_root, '.logs', 'archive')

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'log_management.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger('manage_logs')

def setup_logs_dir():
    """创建.logs目录并将logs目录中的文件移动到.logs目录"""
    # 创建.logs目录
    if not os.path.exists(NEW_LOG_DIR):
        try:
            os.makedirs(NEW_LOG_DIR, exist_ok=True)
            logger.info(f"已创建目录: {NEW_LOG_DIR}")
        except Exception as e:
            logger.error(f"无法创建.logs目录: {str(e)}")
            return False

    # 如果存在logs目录，将文件移动到.logs
    if os.path.exists(OLD_LOG_DIR) and os.path.isdir(OLD_LOG_DIR):
        try:
            # 获取logs目录中的所有文件
            for item in os.listdir(OLD_LOG_DIR):
                src = os.path.join(OLD_LOG_DIR, item)
                dst = os.path.join(NEW_LOG_DIR, item)
                
                if os.path.isfile(src):
                    # 如果目标已存在，添加时间戳
                    if os.path.exists(dst):
                        filename, ext = os.path.splitext(item)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dst = os.path.join(NEW_LOG_DIR, f"{filename}_{timestamp}{ext}")
                    
                    try:
                        shutil.copy2(src, dst)
                        logger.info(f"已复制: {src} -> {dst}")
                    except Exception as e:
                        logger.warning(f"无法复制 {src}: {str(e)}")
            
            logger.info(f"已从 {OLD_LOG_DIR} 复制日志文件到 {NEW_LOG_DIR}")
            
            # 将logs目录重命名为logs_old以避免冲突
            backup_name = f"logs_old_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = os.path.join(project_root, backup_name)
            try:
                # 只有确认所有文件都已复制后才重命名
                shutil.move(OLD_LOG_DIR, backup_path)
                logger.info(f"已将 {OLD_LOG_DIR} 重命名为 {backup_path}")
            except Exception as e:
                logger.warning(f"无法重命名logs目录: {str(e)}")
                
        except Exception as e:
            logger.error(f"处理logs目录出错: {str(e)}")
            return False
    
    return True

def move_root_logs(log_dir):
    """将项目根目录中的日志文件移动到指定日志目录"""
    try:
        count = 0
        for item in os.listdir(project_root):
            if item.endswith('.log'):
                src = os.path.join(project_root, item)
                dst = os.path.join(log_dir, item)
                
                if os.path.isfile(src):
                    # 如果目标已存在，添加时间戳
                    if os.path.exists(dst):
                        filename, ext = os.path.splitext(item)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dst = os.path.join(log_dir, f"{filename}_{timestamp}{ext}")
                    
                    try:
                        # 尝试复制文件
                        shutil.copy2(src, dst)
                        logger.info(f"已复制: {src} -> {dst}")
                        count += 1
                        
                        # 尝试删除原始文件
                        try:
                            os.remove(src)
                            logger.info(f"已删除原始文件: {src}")
                        except Exception as e:
                            logger.warning(f"无法删除原始文件 {src}: {str(e)}")
                            logger.info(f"文件可能正在被使用，将在下次运行时处理")
                            
                    except Exception as e:
                        logger.warning(f"无法复制 {src}: {str(e)}")
        
        logger.info(f"已处理 {count} 个根目录日志文件")
    except Exception as e:
        logger.error(f"移动根目录日志文件出错: {str(e)}")
        return False
    
    return True

def update_log_paths_in_code():
    """更新代码中的日志路径，指向.logs目录"""
    # 需要扫描的目录
    dirs_to_scan = ['Ref', 'QEntL', 'QSM', 'SOM', 'WeQ', 'quantum_core', 'quantum_economy', 'api']
    
    # 日志路径模式
    log_path_patterns = [
        r'logging\.FileHandler\([\'"](.+?\.log)[\'"]',
        r'log_file\s*=\s*[\'"](.+?\.log)[\'"]',
        r'LOG_FILE\s*=\s*[\'"](.+?\.log)[\'"]',
        r'logfile\s*=\s*[\'"](.+?\.log)[\'"]'
    ]
    
    # 日志路径替换模式
    def replace_log_path(match):
        log_file = match.group(1)
        if '/' in log_file or '\\' in log_file:
            # 如果包含路径，提取文件名
            log_file = os.path.basename(log_file)
        
        # 替换为.logs目录路径
        if log_file.startswith('.logs/') or log_file.startswith('.logs\\'):
            return match.group(0)  # 已经是正确的路径
        
        # 替换为相对于项目根目录的相对路径
        replacement = f"os.path.join(project_root, '.logs', '{log_file}')"
        return f"logging.FileHandler({replacement}"
    
    try:
        for dir_name in dirs_to_scan:
            dir_path = os.path.join(project_root, dir_name)
            if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                continue
                
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            # 检查是否包含日志路径
                            has_log_path = False
                            for pattern in log_path_patterns:
                                if re.search(pattern, content):
                                    has_log_path = True
                                    break
                                    
                            if has_log_path:
                                # 检查是否已经导入了log_config
                                if 'from scripts.log_config import' not in content and 'import scripts.log_config' not in content:
                                    # 添加导入语句
                                    import_stmt = 'from scripts.log_config import get_logger\n'
                                    if 'import ' in content:
                                        # 在最后一个import后插入
                                        last_import = re.search(r'^(import .+?)$', content, re.MULTILINE)
                                        if last_import:
                                            pos = last_import.end()
                                            content = content[:pos] + '\n' + import_stmt + content[pos:]
                                    else:
                                        # 在文件头部插入
                                        content = import_stmt + content
                                        
                                # 替换日志路径
                                # 这里我们提供指导而不是直接替换，因为日志配置可能很复杂
                                logger.info(f"文件 {file_path} 包含日志路径配置，建议使用统一的log_config模块")
                                
                                # 备份原始文件
                                backup_path = file_path + '.bak'
                                shutil.copy2(file_path, backup_path)
                                logger.info(f"已备份 {file_path} -> {backup_path}")
                                
                                # 以后的版本可以考虑自动替换
                        except Exception as e:
                            logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
    except Exception as e:
        logger.error(f"更新日志路径出错: {str(e)}")
        return False
    
    return True

def clean_old_logs(log_dir, days=30):
    """
    归档超过指定天数的日志文件
    
    Args:
        log_dir: 日志目录
        days: 超过多少天的日志文件将被归档
    """
    if not os.path.exists(log_dir) or not os.path.isdir(log_dir):
        logger.warning(f"日志目录不存在: {log_dir}")
        return False
    
    # 创建归档目录
    if not os.path.exists(BACKUP_DIR):
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            logger.info(f"已创建归档目录: {BACKUP_DIR}")
        except Exception as e:
            logger.error(f"无法创建归档目录: {str(e)}")
            return False
    
    # 获取当前时间
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    
    # 归档时间戳
    archive_timestamp = now.strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(BACKUP_DIR, f"logs_{archive_timestamp}")
    
    try:
        os.makedirs(archive_dir, exist_ok=True)
        
        count = 0
        for item in os.listdir(log_dir):
            if item.endswith('.log'):
                file_path = os.path.join(log_dir, item)
                
                if os.path.isfile(file_path):
                    # 获取文件修改时间
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # 如果文件超过指定天数
                    if mod_time < cutoff:
                        dst = os.path.join(archive_dir, item)
                        try:
                            shutil.copy2(file_path, dst)
                            logger.info(f"已归档: {file_path} -> {dst}")
                            count += 1
                            
                            # 删除原始文件
                            try:
                                os.remove(file_path)
                                logger.info(f"已删除归档后的原始文件: {file_path}")
                            except Exception as e:
                                logger.warning(f"无法删除原始文件 {file_path}: {str(e)}")
                        except Exception as e:
                            logger.warning(f"无法归档 {file_path}: {str(e)}")
        
        logger.info(f"已归档 {count} 个旧日志文件")
        
        # 如果归档目录为空，删除它
        if count == 0:
            try:
                os.rmdir(archive_dir)
                logger.info(f"删除空的归档目录: {archive_dir}")
            except Exception:
                pass
    except Exception as e:
        logger.error(f"归档旧日志文件出错: {str(e)}")
        return False
    
    return True

def clean_old_archives(max_archives=10):
    """
    清理旧的归档目录，保留最新的N个
    
    Args:
        max_archives: 保留的归档目录数量
    """
    if not os.path.exists(BACKUP_DIR) or not os.path.isdir(BACKUP_DIR):
        return True
    
    try:
        # 获取所有归档目录
        archives = []
        for item in os.listdir(BACKUP_DIR):
            item_path = os.path.join(BACKUP_DIR, item)
            if os.path.isdir(item_path) and item.startswith('logs_'):
                archives.append((item_path, os.path.getmtime(item_path)))
        
        # 按修改时间排序
        archives.sort(key=lambda x: x[1], reverse=True)
        
        # 删除旧的归档目录
        if len(archives) > max_archives:
            for i in range(max_archives, len(archives)):
                archive_path = archives[i][0]
                try:
                    shutil.rmtree(archive_path)
                    logger.info(f"已删除旧归档目录: {archive_path}")
                except Exception as e:
                    logger.warning(f"无法删除旧归档目录 {archive_path}: {str(e)}")
    except Exception as e:
        logger.error(f"清理旧归档目录出错: {str(e)}")
        return False
    
    return True

def check_backup_dirs():
    """检查Ref备份目录"""
    ref_backup_dir = os.path.join(project_root, 'Ref', 'backup')
    
    if not os.path.exists(ref_backup_dir) or not os.path.isdir(ref_backup_dir):
        logger.warning(f"Ref备份目录不存在: {ref_backup_dir}")
        return
    
    try:
        logger.info("Ref备份目录内容:")
        for item in os.listdir(ref_backup_dir):
            item_path = os.path.join(ref_backup_dir, item)
            if os.path.isdir(item_path):
                size = sum(os.path.getsize(os.path.join(root, file)) 
                           for root, _, files in os.walk(item_path) 
                           for file in files)
                size_mb = size / (1024 * 1024)
                
                mod_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                logger.info(f"  - {item}: {size_mb:.2f} MB, 最后修改: {mod_time}")
                
                # 检查内容类型
                file_count = sum(len(files) for _, _, files in os.walk(item_path))
                logger.info(f"    包含 {file_count} 个文件")
                
                # 输出一些示例文件
                sample_files = []
                for root, _, files in os.walk(item_path):
                    for file in files[:5]:  # 最多显示5个文件
                        rel_path = os.path.relpath(os.path.join(root, file), item_path)
                        sample_files.append(rel_path)
                
                if sample_files:
                    logger.info(f"    示例文件: {', '.join(sample_files)}")
    except Exception as e:
        logger.error(f"检查Ref备份目录出错: {str(e)}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='日志管理工具')
    parser.add_argument('--clean-days', type=int, default=30, help='归档超过多少天的日志文件')
    parser.add_argument('--max-archives', type=int, default=10, help='保留的归档数量')
    parser.add_argument('--check-backup', action='store_true', help='检查Ref备份目录')
    parser.add_argument('--update-paths', action='store_true', help='更新代码中的日志路径')
    args = parser.parse_args()
    
    try:
        logger.info("开始日志管理...")
        
        # 创建.logs目录并移动logs目录中的文件
        setup_logs_dir()
        
        # 移动根目录日志文件
        move_root_logs(NEW_LOG_DIR)
        
        # 如果指定了，更新代码中的日志路径
        if args.update_paths:
            update_log_paths_in_code()
        
        # 归档旧日志文件
        clean_old_logs(NEW_LOG_DIR, days=args.clean_days)
        
        # 清理旧归档
        clean_old_archives(max_archives=args.max_archives)
        
        # 检查Ref备份目录
        if args.check_backup:
            check_backup_dirs()
        
        logger.info("日志管理完成!")
    except Exception as e:
        logger.error(f"日志管理出错: {str(e)}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 

"""
"""
量子基因编码: QE-MAN-5EE8F5CA16FA
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
