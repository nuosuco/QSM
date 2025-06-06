#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
项目QEntl转换脚本

此脚本用于逐步将整个项目转换为QEntl格式，
转换完成后将原始文件移动到参考目录。
"""

import os
import sys
import time
import logging
import argparse
import subprocess
from pathlib import Path

# 目录设置
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT_DIR, '.logs')

# 创建日志目录
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    logging.FileHandler(os.path.join(LOG_DIR, 'convert_project.log')),
    logging.StreamHandler()
  ]
)
logger = logging.getLogger('Convert-Project')

# 项目模块和优先级
PROJECT_MODULES = [
  "QSM",      # 主服务，最先转换
  "WeQ",      # 量子社交服务
  "SOM",      # 量子经济服务
  "Ref",      # 量子自反省服务
  "world",    # 世界服务
  "quantum_core",  # 量子核心
  "quantum_ui",    # 量子UI
  "quantum_data",  # 量子数据
  "quantum_shared",  # 量子共享
  "quantum_economy", # 量子经济
  "scripts",  # 脚本工具
  "api",      # API服务
  "core",     # 核心组件
  "tests",    # 测试文件
]

# 模块内部优先级（目录）
DIRECTORY_PRIORITY = [
  "models",    # 模型定义最先转换
  "api",       # API接口
  "services",  # 服务实现
  "utils",     # 工具函数
  "controllers", # 控制器
  "templates", # 模板文件
  "static",    # 静态资源
]

# 文件类型优先级
FILE_TYPE_PRIORITY = [
  ".py",       # Python文件最先转换
  ".js",       # JavaScript文件
  ".css",      # CSS文件
  ".html",     # HTML文件
  ".md",       # Markdown文件
]

def run_command(command, dry_run=False):
    """运行命令
    
    Args:
        command: 要运行的命令
        dry_run: 如果为True，则不实际运行，只输出日志
        
    Returns:
        int: 命令退出码
    """
    if dry_run:
        logger.info(f"[DRY RUN] 将运行命令: {command}")
        return 0
    
    try:
        logger.info(f"运行命令: {command}")
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f"命令执行成功，退出码: {result.returncode}")
        if result.stdout:
            logger.debug(f"标准输出:\n{result.stdout}")
        if result.stderr:
            logger.debug(f"标准错误:\n{result.stderr}")
        return result.returncode
    except subprocess.CalledProcessError as e:
        logger.error(f"命令执行失败，退出码: {e.returncode}")
        if e.stdout:
            logger.error(f"标准输出:\n{e.stdout}")
        if e.stderr:
            logger.error(f"标准错误:\n{e.stderr}")
        return e.returncode

def get_module_files(module_path, priority_dirs=None, priority_exts=None):
    """获取模块内的文件，按优先级排序
    
    Args:
        module_path: 模块路径
        priority_dirs: 优先级目录列表
        priority_exts: 优先级文件类型列表
        
    Returns:
        list: 排序后的文件路径列表
    """
    if not os.path.exists(module_path):
        logger.warning(f"模块路径不存在: {module_path}")
        return []
    
    if priority_dirs is None:
        priority_dirs = DIRECTORY_PRIORITY
    
    if priority_exts is None:
        priority_exts = FILE_TYPE_PRIORITY
    
    # 收集所有文件
    all_files = []
    
    for root, dirs, files in os.walk(module_path):
        # 排除参考目录、日志目录等
        if any(exclude in root for exclude in ['reference', '.git', '.venv', '__pycache__', 'node_modules']):
            continue
        
        for file in files:
            # 排除已经转换过的文件
            if any(file.endswith(ext) for ext in ['.qentl', '.qpy', '.qjs', '.qcss']):
                continue
            
            # 排除二进制文件、临时文件等
            if any(file.endswith(ext) for ext in ['.pyc', '.pyo', '.so', '.dll', '.exe', '.bin', '.dat', '.db']):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, module_path)
            _, ext = os.path.splitext(file)
            
            # 计算优先级
            dir_priority = float('inf')
            for i, dir_name in enumerate(priority_dirs):
                if f"/{dir_name}/" in f"/{rel_path}/":
                    dir_priority = i
                    break
            
            ext_priority = float('inf')
            for i, ext_type in enumerate(priority_exts):
                if file.endswith(ext_type):
                    ext_priority = i
                    break
            
            all_files.append((file_path, dir_priority, ext_priority))
    
    # 按优先级排序
    all_files.sort(key=lambda x: (x[1], x[2]))
    
    return [file_path for file_path, _, _ in all_files]

def convert_module(module_name, dry_run=False):
    """转换单个模块
    
    Args:
        module_name: 模块名称
        dry_run: 如果为True，则不实际运行，只输出日志
        
    Returns:
        bool: 是否成功
    """
    module_path = os.path.join(ROOT_DIR, module_name)
    
    if not os.path.exists(module_path):
        logger.warning(f"模块不存在: {module_path}")
        return False
    
    logger.info(f"开始转换模块: {module_name}")
    
    # 获取按优先级排序的文件
    module_files = get_module_files(module_path)
    
    if not module_files:
        logger.info(f"模块 {module_name} 中没有找到需要转换的文件")
        return True
    
    logger.info(f"模块 {module_name} 中找到 {len(module_files)} 个文件需要转换")
    
    success_count = 0
    error_count = 0
    
    for file_path in module_files:
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        logger.info(f"转换文件: {rel_path}")
        
        # 确定文件类型
        _, ext = os.path.splitext(file_path)
        
        # 构建转换命令
        convert_script = os.path.join(ROOT_DIR, 'scripts', 'utils', 'convert_to_qentl.py')
        cmd = f"python {convert_script} \"{file_path}\""
        
        # 运行转换命令
        exit_code = run_command(cmd, dry_run)
        
        if exit_code == 0:
            success_count += 1
        else:
            error_count += 1
            logger.error(f"转换文件失败: {rel_path}")
    
    success_rate = success_count / (success_count + error_count) * 100 if (success_count + error_count) > 0 else 0
    logger.info(f"模块 {module_name} 转换完成。成功: {success_count}, 失败: {error_count}, 成功率: {success_rate:.2f}%")
    
    return error_count == 0

def parse_arguments():
    """解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description='逐步将整个项目转换为QEntl格式'
    )
    
    parser.add_argument(
        '--modules', '-m',
        type=str,
        nargs='+',
        default=PROJECT_MODULES,
        help='要转换的模块列表（默认为全部）'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='不实际运行，只输出日志'
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    modules = args.modules
    dry_run = args.dry_run
    
    logger.info("===== 项目QEntl转换脚本 =====")
    logger.info(f"将转换的模块: {', '.join(modules)}")
    logger.info(f"干运行模式: {'是' if dry_run else '否'}")
    
    start_time = time.time()
    
    # 确保参考目录存在
    reference_dir = os.path.join(ROOT_DIR, 'reference')
    os.makedirs(reference_dir, exist_ok=True)
    
    # 转换选定的模块
    success_modules = []
    error_modules = []
    
    for module_name in modules:
        logger.info(f"\n{'='*50}\n开始处理模块: {module_name}\n{'='*50}")
        
        if convert_module(module_name, dry_run):
            success_modules.append(module_name)
        else:
            error_modules.append(module_name)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    logger.info("\n\n")
    logger.info(f"{'='*50}")
    logger.info(f"转换完成，耗时: {elapsed_time:.2f} 秒")
    logger.info(f"成功模块: {len(success_modules)}/{len(modules)}")
    
    if success_modules:
        logger.info(f"成功模块列表: {', '.join(success_modules)}")
    
    if error_modules:
        logger.info(f"失败模块列表: {', '.join(error_modules)}")
    
    return 0 if not error_modules else 1

# 主入口
if __name__ == "__main__":
    sys.exit(main()) 