#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QSM服务修复工具

此脚本用于检查和修复所有QSM相关服务
"""
import os
import sys
import time
import logging
import argparse
import subprocess
import psutil
from datetime import datetime
from pathlib import Path

# 设置日志
log_dir = Path('.logs')
log_dir.mkdir(exist_ok=True)
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = log_dir / f'service_fix_{current_time}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('QSM服务修复工具')

# 服务定义
SERVICES = {
    'qsm': {
        'name': 'QSM主服务',
        'script': 'QSM/main.py',
        'port': 5000,
        'daemon': True,
        'process_name': 'QSM主服务',
    },
    'weq_train': {
        'name': 'WeQ训练服务',
        'script': 'WeQ/train/weq_train.py',
        'port': None,
        'hours': 24,
        'process_name': 'WeQ训练服务',
    },
    'weq_inference': {
        'name': 'WeQ推理服务',
        'script': 'WeQ/weq_inference.py',
        'port': 5001,
        'daemon': True,
        'process_name': 'WeQ推理服务',
    },
    'som_core': {
        'name': 'SOM核心服务',
        'script': 'SOM/som_core.py',
        'port': 5002,
        'daemon': True,
        'process_name': 'SOM核心服务',
    },
    'som_wallet': {
        'name': 'SOM钱包服务',
        'script': 'SOM/quantum_wallet.py',
        'port': 5003,
        'daemon': True,
        'process_name': 'SOM钱包服务',
    },
    'som_market': {
        'name': 'SOM市场服务',
        'script': 'SOM/quantum_ecommerce.py',
        'port': 5004,
        'daemon': True,
        'process_name': 'SOM市场服务',
    }
}

def get_python_processes():
    """获取当前运行的Python进程"""
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'py.exe':
                python_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return python_processes

def get_running_services():
    """获取当前运行的服务列表"""
    services = {}
    python_processes = get_python_processes()
    
    for proc in python_processes:
        try:
            cmdline = proc.cmdline()
            if not cmdline:
                continue
                
            for service_id, service in SERVICES.items():
                script_name = service['script'].replace('\\', '/')
                if any(script_name in cmd for cmd in cmdline):
                    services[service_id] = {
                        'pid': proc.pid,
                        'cmdline': ' '.join(cmdline),
                        'status': 'running'
                    }
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return services

def check_port(port):
    """检查端口是否被占用"""
    for conn in psutil.net_connections(kind='tcp'):
        if conn.laddr.port == port:
            return True, conn.pid
    return False, None

def check_service_status():
    """检查所有服务的状态"""
    logger.info("检查服务状态...")
    
    running_services = get_running_services()
    service_status = {}
    
    for service_id, service in SERVICES.items():
        if service_id in running_services:
            status = 'running'
            pid = running_services[service_id]['pid']
        else:
            status = 'stopped'
            pid = None
        
        port_status = False
        port_pid = None
        if service.get('port'):
            port_status, port_pid = check_port(service['port'])
        
        service_status[service_id] = {
            'status': status,
            'pid': pid,
            'port_status': port_status,
            'port_pid': port_pid
        }
        
        logger.info(f"服务 {service['name']} 状态: {status}, PID: {pid}")
        if service.get('port'):
            port_status_text = "使用中" if port_status else "未使用"
            logger.info(f"端口 {service['port']} 状态: {port_status_text}, 占用PID: {port_pid}")
    
    return service_status

def start_service(service_id):
    """启动指定服务"""
    service = SERVICES[service_id]
    script_path = service['script']
    
    if not os.path.exists(script_path):
        logger.error(f"服务脚本不存在: {script_path}")
        return False
    
    try:
        cmd = ['py', '-u', script_path]
        
        # 添加参数
        if service.get('port'):
            cmd.extend(['--port', str(service['port'])])
        
        if service.get('daemon'):
            cmd.append('--daemon')
            
        if service.get('hours'):
            cmd.extend(['--hours', str(service['hours'])])
        
        logger.info(f"启动服务: {service['name']} (命令: {' '.join(cmd)})")
        
        if os.name == 'nt':  # Windows
            process = subprocess.Popen(
                ['start', f'"{service["process_name"]}"'] + cmd,
                shell=True
            )
        else:  # Linux/Mac
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
        
        logger.info(f"服务已启动: {service['name']}")
        return True
    
    except Exception as e:
        logger.error(f"启动服务失败: {service['name']} - {str(e)}")
        return False

def stop_service(service_id, service_status):
    """停止指定服务"""
    if service_id not in service_status or not service_status[service_id]['pid']:
        logger.warning(f"服务 {SERVICES[service_id]['name']} 未运行")
        return True
    
    pid = service_status[service_id]['pid']
    try:
        proc = psutil.Process(pid)
        logger.info(f"正在停止服务: {SERVICES[service_id]['name']} (PID: {pid})")
        proc.terminate()
        
        # 等待进程结束
        gone, alive = psutil.wait_procs([proc], timeout=5)
        if alive:
            logger.warning(f"服务没有及时响应终止信号，正在强制终止: {SERVICES[service_id]['name']}")
            for p in alive:
                p.kill()
        
        logger.info(f"服务已停止: {SERVICES[service_id]['name']}")
        return True
    except psutil.NoSuchProcess:
        logger.info(f"进程已不存在: {pid}")
        return True
    except Exception as e:
        logger.error(f"停止服务时出错: {SERVICES[service_id]['name']} - {str(e)}")
        return False

def fix_service(service_id, service_status):
    """修复指定服务"""
    service = SERVICES[service_id]
    status = service_status[service_id]
    
    logger.info(f"开始修复服务: {service['name']}")
    
    # 检查服务脚本是否存在
    if not os.path.exists(service['script']):
        logger.error(f"服务脚本不存在: {service['script']}")
        return False
    
    # 检查端口占用情况
    if service.get('port') and status['port_status'] and status['port_pid'] != status['pid']:
        logger.warning(f"端口 {service['port']} 被其他进程占用 (PID: {status['port_pid']})")
        try:
            proc = psutil.Process(status['port_pid'])
            logger.info(f"尝试终止占用端口的进程: {proc.name()} (PID: {status['port_pid']})")
            proc.terminate()
            proc.wait(5)
        except Exception as e:
            logger.error(f"终止进程失败: {str(e)}")
            return False
    
    # 如果服务已经在运行，则先停止
    if status['status'] == 'running':
        if not stop_service(service_id, service_status):
            logger.error(f"无法停止服务: {service['name']}")
            return False
        
        # 等待一段时间确保服务完全停止
        time.sleep(2)
    
    # 启动服务
    return start_service(service_id)

def fix_all_services():
    """修复所有服务"""
    logger.info("开始修复所有服务...")
    
    # 检查当前服务状态
    service_status = check_service_status()
    
    # 修复每个服务
    results = {}
    for service_id in SERVICES:
        results[service_id] = fix_service(service_id, service_status)
    
    # 汇总结果
    success_count = sum(1 for success in results.values() if success)
    logger.info(f"服务修复完成. 成功: {success_count}/{len(SERVICES)}")
    
    if success_count < len(SERVICES):
        failed_services = [SERVICES[sid]['name'] for sid, success in results.items() if not success]
        logger.error(f"以下服务修复失败: {', '.join(failed_services)}")
    
    return success_count == len(SERVICES)

def main():
    parser = argparse.ArgumentParser(description='QSM服务修复工具')
    parser.add_argument('--check', action='store_true', help='仅检查服务状态，不进行修复')
    args = parser.parse_args()
    
    try:
        logger.info("=== QSM服务修复工具 ===")
        
        if args.check:
            logger.info("仅检查服务状态")
            check_service_status()
        else:
            fix_all_services()
            
            # 再次检查服务状态
            logger.info("检查修复后的服务状态")
            check_service_status()
        
        logger.info("操作完成")
        
    except Exception as e:
        logger.error(f"执行过程中发生错误: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 