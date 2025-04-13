#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WeQ服务启动脚本
启动所有量子纠缠网络服务，包括API服务、训练服务和推理服务
"""

import os
import sys
import time
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# 设置根路径
script_dir = os.path.dirname(os.path.abspath(__file__))
weq_dir = os.path.dirname(os.path.dirname(script_dir))
root_dir = os.path.dirname(weq_dir)
os.chdir(root_dir)  # 将工作目录设置为项目根目录

# 确保存在日志目录
os.makedirs('.logs', exist_ok=True)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('.logs', 'weq_service_starter.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WeQ服务启动器')

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="WeQ服务启动器")
    parser.add_argument("--all", action="store_true", help="启动所有服务")
    parser.add_argument("--api", action="store_true", help="启动WeQ API服务")
    parser.add_argument("--train", action="store_true", help="启动WeQ训练服务")
    parser.add_argument("--inference", action="store_true", help="启动WeQ推理服务")
    parser.add_argument("--port", type=int, default=5003, help="API服务端口")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="API服务监听地址")
    return parser.parse_args()

def start_background_service(script_path, service_name, args=""):
    """启动后台服务"""
    try:
        # 确保脚本路径存在
        if not os.path.exists(script_path):
            logger.error(f"服务脚本不存在: {script_path}")
            return False
            
        # 创建日志文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join('.logs', f"{service_name}_{timestamp}.log")
        err_file = os.path.join('.logs', f"{service_name}_{timestamp}.err")
        
        # 构建命令
        cmd = [sys.executable, script_path]
        if args:
            if isinstance(args, str):
                cmd.extend(args.split())
            else:
                cmd.extend(args)
            
        # 启动进程，重定向输出到日志文件
        with open(log_file, 'w', encoding='utf-8') as out_f, open(err_file, 'w', encoding='utf-8') as err_f:
            process = subprocess.Popen(
                cmd,
                stdout=out_f,
                stderr=err_f,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
        logger.info(f"成功启动服务: {service_name}, PID: {process.pid}, 日志: {log_file}")
        return True
        
    except Exception as e:
        logger.error(f"启动服务失败: {service_name}, 错误: {str(e)}")
        return False

def find_script(relative_paths):
    """查找脚本文件"""
    for path in relative_paths:
        full_path = os.path.join(weq_dir, path)
        if os.path.exists(full_path):
            return full_path
    return None

def start_weq_api_service(args):
    """启动WeQ API服务"""
    logger.info("启动WeQ API服务...")
    
    # 查找API脚本，优先使用标准路径
    api_script_paths = [
        "api/weq_api.py",  # 标准路径
        "scripts/services/WeQ_app.py",  # 服务目录
        "api/app.py",  # 备用路径
    ]
    api_script = find_script(api_script_paths)
    
    if not api_script:
        logger.error("未找到WeQ API服务脚本")
        logger.error("请确保以下路径之一存在:")
        for path in api_script_paths:
            logger.error(f"- {os.path.join(weq_dir, path)}")
        return False
    
    # 构建参数
    api_args = [
        "--port", str(args.port),
        "--host", args.host
    ]
    
    # 启动服务
    return start_background_service(api_script, "WeQ API服务", api_args)

def start_weq_train_service(args):
    """启动WeQ训练服务"""
    logger.info("启动WeQ训练服务...")
    
    # 查找训练服务脚本
    train_script_paths = ["weq_train.py", "train/weq_train.py", "scripts/train/train_service.py"]
    train_script = find_script(train_script_paths)
    
    if not train_script:
        logger.error("未找到WeQ训练服务脚本")
        return False
    
    # 构建参数
    train_args = ["--daemon", "--auto_save"]
    
    # 启动服务
    return start_background_service(train_script, "WeQ训练服务", train_args)

def start_weq_inference_service(args):
    """启动WeQ推理服务"""
    logger.info("启动WeQ推理服务...")
    
    # 查找推理服务脚本
    inference_script_paths = ["weq_inference.py", "inference/weq_inference.py", "scripts/inference/inference_service.py"]
    inference_script = find_script(inference_script_paths)
    
    if not inference_script:
        logger.error("未找到WeQ推理服务脚本")
        return False
    
    # 构建参数
    inference_args = ["--daemon", "--batch_size", "32", "--model", "latest"]
    
    # 启动服务
    return start_background_service(inference_script, "WeQ推理服务", inference_args)

def check_dependencies():
    """检查依赖项"""
    try:
        # 暂时跳过PyTorch检查
        logger.warning("跳过PyTorch检查")
        return True
    except Exception as e:
        logger.error(f"依赖检查失败: {str(e)}")
        return False

def main():
    """主函数"""
    args = parse_args()
    
    # 服务计数器
    services_started = 0
    
    # 判断是否启动所有服务
    start_all = args.all or not any([args.api, args.train, args.inference])
    
    # 启动API服务
    if args.api or start_all:
        if start_weq_api_service(args):
            services_started += 1
    
    # 启动训练服务
    if args.train or start_all:
        if start_weq_train_service(args):
            services_started += 1
    
    # 启动推理服务
    if args.inference or start_all:
        if start_weq_inference_service(args):
            services_started += 1
    
    logger.info(f"启动服务完成, 总共启动 {services_started} 个服务")
    return services_started > 0

if __name__ == "__main__":
    main()

"""
量子基因编码: QE-SRV-WEQ-F1E2D3C4
纠缠状态: 活跃
纠缠对象: ['scripts/services/start_services.py', 'WeQ/api/weq_api.py', 'WeQ/weq_train.py', 'WeQ/weq_inference.py']
纠缠强度: 0.99
"""

# 开发团队：中华 ZhoHo，Claude 