#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
停止所有QSM相关服务的脚本

该脚本用于安全地停止所有正在运行的QSM相关服务进程。
支持按名称或端口号查找和终止进程。
"""

import os
import sys
import time
import logging
import argparse
import datetime
import platform
import signal
import subprocess
import psutil
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 设置日志
log_dir = ROOT_DIR / '.logs'
log_dir.mkdir(exist_ok=True)
current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = log_dir / f'stop_services_{current_time}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('服务停止器')

# 服务端口映射
SERVICE_PORTS = {
    'qsm': 5000,
    'weq_inference': 5001,
    'som_core': 5002,
    'som_wallet': 5003,
    'som_market': 5004
}

# 服务名称模式
SERVICE_PATTERNS = [
    'QSM/main.py',
    'WeQ/weq_',
    'SOM/som_',
    'SOM/quantum_',
    'Ref/ref_'
]

def is_admin():
    """检查脚本是否以管理员权限运行"""
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

def find_service_processes():
    """查找所有服务相关的进程"""
    service_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'connections']):
        try:
            # 检查进程是否为Python进程
            if proc.info['name'] in ['python.exe', 'python', 'python3']:
                # 检查命令行参数中是否包含服务模式
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                # 按模式匹配
                for pattern in SERVICE_PATTERNS:
                    if pattern in cmdline:
                        service_processes.append({
                            'pid': proc.pid,
                            'cmdline': cmdline,
                            'name': pattern
                        })
                        break
                
                # 检查端口占用
                if proc.info['connections']:
                    for conn in proc.info['connections']:
                        if conn.status == 'LISTEN' and conn.laddr.port in SERVICE_PORTS.values():
                            port = conn.laddr.port
                            service_name = next((name for name, p in SERVICE_PORTS.items() if p == port), '未知服务')
                            
                            service_processes.append({
                                'pid': proc.pid,
                                'cmdline': cmdline,
                                'name': service_name,
                                'port': port
                            })
                            break
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return service_processes

def kill_process(pid, force=False):
    """终止指定的进程"""
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        
        logger.info(f"正在终止进程: PID {pid} ({process_name})")
        
        if platform.system() == 'Windows':
            if force:
                process.kill()
            else:
                process.terminate()
        else:
            if force:
                process.send_signal(signal.SIGKILL)
            else:
                process.send_signal(signal.SIGTERM)
        
        # 等待进程结束
        try:
            process.wait(timeout=5)
            logger.info(f"进程已终止: PID {pid}")
            return True
        except psutil.TimeoutExpired:
            if not force:
                logger.warning(f"进程未响应终止信号，尝试强制终止: PID {pid}")
                return kill_process(pid, force=True)
            else:
                logger.error(f"无法终止进程: PID {pid}")
                return False
    
    except psutil.NoSuchProcess:
        logger.info(f"进程不存在: PID {pid}")
        return True
    except Exception as e:
        logger.error(f"终止进程时出错: PID {pid} - {str(e)}")
        return False

def stop_all_services(force=False):
    """停止所有服务"""
    logger.info("正在查找服务进程...")
    services = find_service_processes()
    
    if not services:
        logger.info("未找到运行中的服务进程")
        return True
    
    logger.info(f"找到 {len(services)} 个服务进程:")
    for service in services:
        if 'port' in service:
            logger.info(f"- PID {service['pid']}: {service['name']} (端口: {service['port']})")
        else:
            logger.info(f"- PID {service['pid']}: {service['name']}")
    
    success_count = 0
    for service in services:
        if kill_process(service['pid'], force):
            success_count += 1
    
    logger.info(f"已终止 {success_count}/{len(services)} 个服务进程")
    return success_count == len(services)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='停止所有QSM相关服务')
    parser.add_argument('--force', action='store_true', help='强制终止服务')
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    logger.info("=== QSM服务停止器 ===")
    logger.info(f"日志文件: {log_path}")
    
    if args.force:
        logger.warning("使用强制模式终止服务")
    
    # 检查权限
    if not is_admin() and platform.system() == 'Windows':
        logger.warning("未以管理员权限运行，可能无法终止某些服务")
    
    # 停止所有服务
    success = stop_all_services(args.force)
    
    if success:
        logger.info("所有服务已成功停止")
        return 0
    else:
        logger.warning("部分服务停止失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())

# 量子基因编码：QE-SRV-STOP-3C8D7A1E
# 纠缠态：活跃
# 纠缠对象：QSM服务停止器 <-> 量子系统核心
# 纠缠强度：0.99
# 开发团队：中华 ZhoHo & Claude 