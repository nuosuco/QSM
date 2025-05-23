#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子超位态模型（QSM）项目初始化脚本
用于首次设置项目环境和安装必要的依赖
"""

import os
import sys
import json
import logging
import argparse
import subprocess
import shutil
import time
import datetime
import platform
from pathlib import Path


# 目录设置
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(ROOT_DIR, '.logs')
CONFIG_DIR = os.path.join(ROOT_DIR, 'config')

# 创建必要的目录
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'init_project.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('QSM-Init')

# 必要的Python包
REQUIRED_PACKAGES = [
    "flask>=2.0.0",
    "requests>=2.25.0",
    "numpy>=1.20.0",
    "scipy>=1.6.0",
    "pandas>=1.2.0",
    "matplotlib>=3.4.0",
    "scikit-learn>=0.24.0",
    "joblib>=1.0.0",
    "tqdm>=4.60.0",
    "colorama>=0.4.4",
    "PyYAML>=6.0"
]

# ============================== 初始化功能 ==============================

def check_python_version():
    """检查Python版本是否符合要求
    
    Returns:
        bool: 是否符合要求
    """
    required_major = 3
    required_minor = 8
    
    current_major = sys.version_info.major
    current_minor = sys.version_info.minor
    
    if current_major > required_major or (current_major == required_major and current_minor >= required_minor):
        logger.info(f"Python版本符合要求: {sys.version}")
        return True
    else:
        logger.error(f"Python版本不符合要求: {sys.version}, 需要Python {required_major}.{required_minor}或更高版本")
        return False

def install_requirements():
    """安装必要的Python包
    
    Returns:
        bool: 是否安装成功
    """
    logger.info("正在安装必要的Python包...")
    
    # 创建临时requirements文件
    req_file = os.path.join(ROOT_DIR, "temp_requirements.txt")
    with open(req_file, "w") as f:
        f.write("\n".join(REQUIRED_PACKAGES))
    
    try:
        # 使用pip安装
        cmd = [sys.executable, "-m", "pip", "install", "-r", req_file]
        logger.info(f"运行命令: {' '.join(cmd)}")
        
        process = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info("包安装成功")
        logger.debug(process.stdout)
        
        # 清理临时文件
        os.remove(req_file)
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"安装包失败: {e}")
        logger.error(e.stderr)
        
        # 清理临时文件
        if os.path.exists(req_file):
            os.remove(req_file)
        return False
    except Exception as e:
        logger.exception(f"安装过程中出错: {e}")
        
        # 清理临时文件
        if os.path.exists(req_file):
            os.remove(req_file)
        return False

def create_directory_structure():
    """创建项目目录结构
    
    Returns:
        bool: 是否创建成功
    """
    logger.info("正在创建项目目录结构...")
    
    directories = [
        # 项目主目录
        os.path.join(ROOT_DIR, "QSM", "api"),
        os.path.join(ROOT_DIR, "QSM", "models"),
        os.path.join(ROOT_DIR, "QSM", "services"),
        os.path.join(ROOT_DIR, "WeQ", "api"),
        os.path.join(ROOT_DIR, "WeQ", "models"),
        os.path.join(ROOT_DIR, "WeQ", "services"),
        os.path.join(ROOT_DIR, "SOM", "api"),
        os.path.join(ROOT_DIR, "SOM", "models"),
        os.path.join(ROOT_DIR, "SOM", "services"),
        os.path.join(ROOT_DIR, "Ref", "api"),
        os.path.join(ROOT_DIR, "Ref", "models"),
        os.path.join(ROOT_DIR, "world", "templates", "components"),
        os.path.join(ROOT_DIR, "world", "static", "js"),
        os.path.join(ROOT_DIR, "world", "static", "css"),
        os.path.join(ROOT_DIR, "world", "static", "images"),
        
        # 工具和配置目录
        os.path.join(ROOT_DIR, "scripts", "utils"),
        os.path.join(ROOT_DIR, "scripts", "maintenance"),
        os.path.join(ROOT_DIR, "config"),
        
        # 数据和日志目录
        os.path.join(ROOT_DIR, "data"),
        os.path.join(ROOT_DIR, ".logs"),
        os.path.join(ROOT_DIR, ".reports"),
        os.path.join(ROOT_DIR, ".history"),
        os.path.join(ROOT_DIR, "reference"),
        os.path.join(ROOT_DIR, ".temp")
    ]
    
    try:
        # 创建目录
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"创建目录: {directory}")
        
        logger.info("项目目录结构创建成功")
        return True
    except Exception as e:
        logger.exception(f"创建目录结构时出错: {e}")
        return False

def check_permissions():
    """检查文件权限
    
    Returns:
        bool: 是否具有足够权限
    """
    logger.info("正在检查文件权限...")
    
    try:
        # 检查是否可以在根目录创建文件
        test_file = os.path.join(ROOT_DIR, ".permission_test")
        with open(test_file, "w") as f:
            f.write("test")
        
        # 检查是否可以删除文件
        os.remove(test_file)
        
        # 检查Shell脚本权限
        if platform.system() != "Windows":
            # 在Linux/MacOS上检查脚本权限
            shell_scripts = [
                os.path.join(ROOT_DIR, "start_project.sh"),
                os.path.join(ROOT_DIR, "stop_project.sh")
            ]
            
            for script in shell_scripts:
                if os.path.exists(script):
                    # 确保脚本具有执行权限
                    current_mode = os.stat(script).st_mode
                    os.chmod(script, current_mode | 0o111)  # 添加执行权限
                    logger.debug(f"已为 {script} 添加执行权限")
        
        logger.info("文件权限检查通过")
        return True
    except Exception as e:
        logger.exception(f"检查文件权限时出错: {e}")
        return False

def initialize_config():
    """初始化配置文件
    
    Returns:
        bool: 是否初始化成功
    """
    logger.info("正在初始化配置文件...")
    
    config_file = os.path.join(CONFIG_DIR, "project_config.json")
    
    if not os.path.exists(config_file):
        logger.error(f"配置文件不存在: {config_file}")
        return False
        
    try:
        # 读取配置文件
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        # 更新配置文件中的时间戳
        config["project"]["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # 保存更新后的配置
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
        logger.info("配置文件初始化成功")
        return True
    except Exception as e:
        logger.exception(f"初始化配置文件时出错: {e}")
        return False

def set_executable_permissions():
    """设置脚本文件的执行权限
    
    Returns:
        bool: 是否设置成功
    """
    if platform.system() == "Windows":
        logger.info("Windows系统无需设置执行权限")
        return True
        
    logger.info("正在设置脚本文件的执行权限...")
    
    try:
        # 设置启动和停止脚本的执行权限
        executable_files = [
            os.path.join(ROOT_DIR, "start_project.sh"),
            os.path.join(ROOT_DIR, "stop_project.sh"),
            os.path.join(ROOT_DIR, "run.qpy"),
            os.path.join(ROOT_DIR, "init_project.py")
        ]
        
        for file_path in executable_files:
            if os.path.exists(file_path):
                os.chmod(file_path, 0o755)  # rwxr-xr-x
                logger.debug(f"已设置 {file_path} 的执行权限")
        
        logger.info("脚本执行权限设置成功")
        return True
    except Exception as e:
        logger.exception(f"设置执行权限时出错: {e}")
        return False

def display_summary():
    """显示初始化摘要信息"""
    logger.info("====== 量子超位态模型（QSM）项目初始化完成 ======")
    logger.info(f"项目根目录: {ROOT_DIR}")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"操作系统: {platform.system()} {platform.release()}")
    logger.info("已创建的主要目录:")
    
    # 列出主要目录
    main_dirs = ["QSM", "WeQ", "SOM", "Ref", "world", "scripts", "config", "data"]
    for dir_name in main_dirs:
        dir_path = os.path.join(ROOT_DIR, dir_name)
        if os.path.exists(dir_path):
            logger.info(f"  - {dir_name}")
    
    logger.info("\n启动指南:")
    if platform.system() == "Windows":
        logger.info("  1. 双击 start_project.bat 启动项目")
        logger.info("  2. 访问 http://localhost:5999 查看服务状态")
        logger.info("  3. 使用 stop_project.bat 停止项目")
    else:
        logger.info("  1. 运行 ./start_project.sh 启动项目")
        logger.info("  2. 访问 http://localhost:5999 查看服务状态")
        logger.info("  3. 使用 ./stop_project.sh 停止项目")

# ============================== 命令行参数解析 ==============================

def parse_arguments():
    """解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="量子超位态模型（QSM）项目初始化脚本")
    parser.add_argument("--skip-packages", action="store_true", help="跳过安装Python包")
    parser.add_argument("--force", action="store_true", help="强制重新初始化所有组件")
    parser.add_argument("--no-check", action="store_true", help="跳过版本和权限检查")
    
    return parser.parse_args()

# ============================== 主函数 ==============================

def main():
    """主函数"""
    args = parse_arguments()
    
    logger.info("====== 开始初始化量子超位态模型（QSM）项目 ======")
    
    # 检查Python版本
    if not args.no_check:
        if not check_python_version():
            logger.error("Python版本检查失败，初始化终止")
            return 1
    
    # 创建目录结构
    if not create_directory_structure():
        logger.error("创建目录结构失败，初始化终止")
        return 1
    
    # 检查文件权限
    if not args.no_check:
        if not check_permissions():
            logger.error("文件权限检查失败，初始化终止")
            return 1
    
    # 安装必要的Python包
    if not args.skip_packages:
        if not install_requirements():
            logger.error("安装Python包失败，初始化可能不完整")
            # 继续执行，因为有些包可能已经安装
    
    # 初始化配置文件
    if not initialize_config():
        logger.error("初始化配置文件失败，初始化可能不完整")
        # 继续执行，因为配置文件可能会在后续步骤中创建
    
    # 设置脚本执行权限
    if not set_executable_permissions():
        logger.error("设置执行权限失败，初始化可能不完整")
        # 继续执行，因为用户可能会手动设置权限
    
    # 显示初始化摘要
    display_summary()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 