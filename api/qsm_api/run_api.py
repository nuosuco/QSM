#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QSM API 启动脚本

此脚本用于启动QSM API服务以及各子系统API服务
"""

import os
import sys
import subprocess
import logging
import time
import signal
import argparse
from concurrent.futures import ThreadPoolExecutor

# 添加项目根目录到系统路径
sys.path.append('.')

# 导入配置
from api.qsm_api.qsm_api_config import (
    QSM_API_PORT, 
    WEQ_API_PORT,
    SOM_API_PORT,
    REF_API_PORT,
    INTEGRATE_WEQ,
    INTEGRATE_SOM,
    INTEGRATE_REF
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('run_api.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("QSM-API-Runner")

# 存储所有子进程
processes = []

def signal_handler(sig, frame):
    """处理终止信号，确保所有子进程都被关闭"""
    logger.info("接收到终止信号，正在关闭所有API服务...")
    for process in processes:
        if process.poll() is None:  # 如果进程仍在运行
            process.terminate()
    logger.info("所有API服务已关闭")
    sys.exit(0)

def run_api_service(command, name, log_file):
    """运行API服务并重定向输出到日志文件"""
    logger.info(f"启动 {name} 服务: {command}")
    log_f = open(log_file, 'w')
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        text=True
    )
    processes.append(process)
    return process

def check_service_status(process, name, port):
    """检查服务是否成功启动"""
    time.sleep(2)  # 给服务一些启动时间
    
    # 检查进程是否仍在运行
    if process.poll() is not None:
        logger.error(f"{name} 服务启动失败，退出码: {process.returncode}")
        return False
    
    # 如果进程仍在运行，检查端口是否被占用（简单验证服务是否正常启动）
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            logger.info(f"{name} 服务成功启动在端口 {port}")
            return True
        else:
            logger.warning(f"{name} 服务可能未成功绑定到端口 {port}")
            return False
    except Exception as e:
        logger.error(f"检查 {name} 服务状态时出错: {str(e)}")
        return False

def main():
    """启动QSM API及其子系统API服务"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='启动QSM API服务')
    parser.add_argument('--qsm-only', action='store_true', help='仅启动QSM API服务，不启动子系统API')
    parser.add_argument('--with-weq', action='store_true', help='启动WeQ API服务')
    parser.add_argument('--with-som', action='store_true', help='启动SOM API服务')
    parser.add_argument('--with-ref', action='store_true', help='启动Ref API服务')
    parser.add_argument('--all', action='store_true', help='启动所有API服务')
    args = parser.parse_args()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建日志目录
    os.makedirs('logs', exist_ok=True)
    
    # 根据参数决定启动哪些服务
    services_to_start = []
    
    # 如果指定了--all，则启动所有服务
    if args.all:
        services_to_start = ['qsm', 'weq', 'som', 'ref']
    else:
        # 始终启动QSM服务
        services_to_start.append('qsm')
        
        # 如果不是--qsm-only，则按照配置或命令行参数启动子系统
        if not args.qsm_only:
            if args.with_weq or INTEGRATE_WEQ:
                services_to_start.append('weq')
            if args.with_som or INTEGRATE_SOM:
                services_to_start.append('som')
            if args.with_ref or INTEGRATE_REF:
                services_to_start.append('ref')
    
    # 准备服务启动命令
    service_configs = {
        'qsm': {
            'command': 'python -m api.qsm_api.qsm_api',
            'name': 'QSM API',
            'log_file': 'logs/qsm_api.log',
            'port': QSM_API_PORT
        },
        'weq': {
            'command': 'python -m WeQ.api.weq_api',
            'name': 'WeQ API',
            'log_file': 'logs/weq_api.log',
            'port': WEQ_API_PORT
        },
        'som': {
            'command': 'python -m SOM.api.som_api',
            'name': 'SOM API',
            'log_file': 'logs/som_api.log',
            'port': SOM_API_PORT
        },
        'ref': {
            'command': 'python -m Ref.api.ref_api',
            'name': 'Ref API',
            'log_file': 'logs/ref_api.log',
            'port': REF_API_PORT
        }
    }
    
    # 启动选定的服务
    with ThreadPoolExecutor(max_workers=len(services_to_start)) as executor:
        for service_name in services_to_start:
            if service_name in service_configs:
                config = service_configs[service_name]
                process = run_api_service(config['command'], config['name'], config['log_file'])
                
                # 在后台检查服务状态
                executor.submit(check_service_status, process, config['name'], config['port'])
    
    logger.info(f"已启动以下服务: {', '.join(services_to_start)}")
    logger.info("按Ctrl+C终止所有服务")
    
    # 保持主进程运行，直到收到终止信号
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main() 

"""
"""
量子基因编码: QE-RUN-2689E5F8CD7F
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
