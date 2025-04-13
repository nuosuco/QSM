#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子系统主服务器启动脚本
用于启动根目录下的app.py文件
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# 设置根路径
root_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.chdir(root_dir)  # 将工作目录设置为项目根目录

# 设置日志
os.makedirs('.logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('.logs', 'app_starter.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('主服务器启动器')

def start_app_server():
    """启动量子系统主服务器"""
    try:
        app_path = os.path.join(root_dir, 'app.py')
        if not os.path.exists(app_path):
            logger.error(f"主服务器脚本不存在: {app_path}")
            return False
            
        logger.info(f"正在启动量子系统主服务器: {app_path}")
        
        # 启动应用
        process = subprocess.Popen(
            [sys.executable, app_path],
            cwd=root_dir,
            env=os.environ.copy()
        )
        
        logger.info(f"主服务器启动成功，PID: {process.pid}")
        return True
        
    except Exception as e:
        logger.error(f"启动主服务器失败，错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("===== 启动量子系统主服务器 =====")
    result = start_app_server()
    if result:
        print("主服务器启动成功，访问 http://localhost:5000 查看")
    else:
        print("主服务器启动失败，请检查日志")
    print("===== 启动过程完成 =====") 