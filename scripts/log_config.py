#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一日志配置模块

此模块提供了统一的日志配置，支持：
1. 日志输出到.logs目录
2. 支持控制台和文件双重输出
3. 可配置的日志级别
4. 日志轮转
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 获取项目根目录
current_file = os.path.abspath(__file__)
script_dir = os.path.dirname(current_file)
project_root = os.path.dirname(script_dir)

# 日志目录
LOGS_DIR = os.path.join(project_root, '.logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# 默认日志格式
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
SIMPLE_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# 默认最大日志文件大小 (10MB)
DEFAULT_MAX_LOG_SIZE = 10 * 1024 * 1024

# 默认日志文件备份数量
DEFAULT_BACKUP_COUNT = 3

def get_logger(name, 
               level=logging.INFO, 
               log_format=DEFAULT_LOG_FORMAT,
               log_to_console=True,
               log_to_file=True,
               log_file=None,
               max_size=DEFAULT_MAX_LOG_SIZE,
               backup_count=DEFAULT_BACKUP_COUNT):
    """
    获取配置好的日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别，默认INFO
        log_format: 日志格式
        log_to_console: 是否输出到控制台
        log_to_file: 是否输出到文件
        log_file: 日志文件路径，不指定则使用 {name}.log
        max_size: 最大日志文件大小
        backup_count: 日志文件备份数量
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 如果已经有处理器，说明已经配置过，直接返回
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    formatter = logging.Formatter(log_format)
    
    # 控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if log_to_file:
        if log_file is None:
            log_file = os.path.join(LOGS_DIR, f"{name}.log")
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def migrate_logs_to_central_dir():
    """
    迁移项目中的日志文件到.logs目录
    
    查找项目中的.log文件并移动到.logs目录
    """
    migrated = 0
    
    # 获取root logger
    logger = get_logger('log_migration')
    
    logger.info("开始迁移日志文件到.logs目录")
    
    try:
        # 遍历项目目录
        for root, dirs, files in os.walk(project_root):
            # 跳过.logs目录和.git目录
            if '.logs' in root or '.git' in root:
                continue
            
            for file in files:
                if file.endswith('.log'):
                    source_path = os.path.join(root, file)
                    target_path = os.path.join(LOGS_DIR, file)
                    
                    try:
                        # 如果目标已存在，追加内容
                        if os.path.exists(target_path):
                            logger.info(f"追加日志文件 {source_path} 到 {target_path}")
                            with open(source_path, 'r', encoding='utf-8', errors='ignore') as src_file:
                                with open(target_path, 'a', encoding='utf-8') as tgt_file:
                                    tgt_file.write(f"\n\n--- Appended from {source_path} ---\n\n")
                                    tgt_file.write(src_file.read())
                            os.remove(source_path)
                        else:
                            logger.info(f"移动日志文件 {source_path} 到 {target_path}")
                            os.rename(source_path, target_path)
                        
                        migrated += 1
                    except Exception as e:
                        logger.error(f"迁移日志文件 {source_path} 时出错: {str(e)}")
        
        logger.info(f"日志迁移完成，共迁移 {migrated} 个文件")
        return migrated
    
    except Exception as e:
        logger.error(f"日志迁移过程中出错: {str(e)}")
        return migrated

def setup_global_logging_config(level=logging.INFO):
    """
    设置全局日志配置
    
    Args:
        level: 日志级别
        
    Returns:
        logging.Logger: root日志记录器
    """
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    root_logger.addHandler(console_handler)
    
    # 添加文件处理器
    file_handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, 'root.log'),
        maxBytes=DEFAULT_MAX_LOG_SIZE,
        backupCount=DEFAULT_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    root_logger.addHandler(file_handler)
    
    return root_logger

if __name__ == "__main__":
    # 如果直接运行，执行日志迁移
    setup_global_logging_config()
    migrate_logs_to_central_dir() 

"""
"""
量子基因编码: QE-LOG-474617D48172
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
