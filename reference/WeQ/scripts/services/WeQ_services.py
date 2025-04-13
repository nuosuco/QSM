#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WeQ服务自动化工具
用于管理WeQ模型的服务进程
开发团队: 中华 ZhoHo, Claude
"""

import os
import sys
import time
import json
import signal
import psutil
import logging
import argparse
import subprocess
from datetime import datetime

# 确保能够导入WeQ模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../.."))
weq_dir = os.path.join(project_root, "WeQ")

if weq_dir not in sys.path:
    sys.path.append(weq_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# 设置日志
def setup_logging():
    log_dir = os.path.join(project_root, ".logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"WeQ_services_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("WeQ_Services")

logger = setup_logging()

# 服务配置
SERVICES = {
    "api": {
        "name": "WeQ API服务",
        "script": os.path.join(script_dir, "WeQ_app.py"),
        "port": 5001,
        "pid_file": os.path.join(project_root, ".logs", "weq_api.pid"),
        "args": ["--port", "5001"]
    },
    "train": {
        "name": "WeQ 训练服务",
        "script": os.path.join(weq_dir, "weq_train.py"),
        "pid_file": os.path.join(project_root, ".logs", "weq_train.pid"),
        "args": []
    },
    "inference": {
        "name": "WeQ 推理服务",
        "script": os.path.join(weq_dir, "weq_inference.py"),
        "pid_file": os.path.join(project_root, ".logs", "weq_inference.pid"),
        "args": []
    }
}

# 启动服务
def start_service(service_key):
    service = SERVICES.get(service_key)
    if not service:
        logger.error(f"未知服务: {service_key}")
        return False
    
    # 检查服务是否已经运行
    if is_service_running(service_key):
        logger.info(f"{service['name']}已经在运行中")
        return True
    
    # 准备命令
    cmd = [sys.executable, service["script"]] + service["args"]
    
    # 准备日志文件路径
    log_dir = os.path.join(project_root, ".logs")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    stdout_log = os.path.join(log_dir, f"{service_key}_{timestamp}.log")
    stderr_log = os.path.join(log_dir, f"{service_key}_{timestamp}.err")
    
    # 启动服务进程
    try:
        logger.info(f"启动{service['name']}...")
        logger.info(f"命令: {' '.join(cmd)}")
        
        with open(stdout_log, 'w', encoding='utf-8') as out, \
             open(stderr_log, 'w', encoding='utf-8') as err:
            
            process = subprocess.Popen(
                cmd,
                stdout=out,
                stderr=err,
                cwd=project_root,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
        
        # 保存PID
        with open(service["pid_file"], 'w') as f:
            f.write(str(process.pid))
        
        logger.info(f"{service['name']}已启动: PID={process.pid}")
        
        # 等待几秒检查进程是否仍在运行
        time.sleep(2)
        if process.poll() is not None:
            logger.error(f"{service['name']}启动后立即退出，退出码: {process.returncode}")
            logger.error(f"请检查错误日志: {stderr_log}")
            return False
        
        # 如果服务有端口，检查端口是否被占用
        if "port" in service:
            if not check_port(service["port"]):
                logger.warning(f"服务已启动但端口{service['port']}未被占用，可能存在问题")
        
        return True
        
    except Exception as e:
        logger.error(f"启动{service['name']}失败: {str(e)}")
        return False

# 停止服务
def stop_service(service_key):
    service = SERVICES.get(service_key)
    if not service:
        logger.error(f"未知服务: {service_key}")
        return False
    
    if not os.path.exists(service["pid_file"]):
        logger.info(f"{service['name']}未运行或PID文件不存在")
        return True
    
    try:
        # 读取PID
        with open(service["pid_file"], 'r') as f:
            pid = int(f.read().strip())
        
        # 检查进程是否存在
        if not psutil.pid_exists(pid):
            logger.info(f"{service['name']}进程不存在 (PID: {pid})")
            os.remove(service["pid_file"])
            return True
        
        # 获取进程对象
        process = psutil.Process(pid)
        
        # 发送终止信号
        logger.info(f"正在停止{service['name']} (PID: {pid})...")
        
        if os.name == 'nt':
            # Windows: 使用taskkill强制终止进程树
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)])
        else:
            # Linux/Mac: 发送SIGTERM信号
            process.terminate()
            
            # 等待进程终止
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                logger.warning(f"{service['name']}未响应SIGTERM信号，发送SIGKILL")
                process.kill()
        
        # 删除PID文件
        if os.path.exists(service["pid_file"]):
            os.remove(service["pid_file"])
        
        logger.info(f"{service['name']}已停止")
        return True
        
    except Exception as e:
        logger.error(f"停止{service['name']}失败: {str(e)}")
        return False

# 检查服务是否运行
def is_service_running(service_key):
    service = SERVICES.get(service_key)
    if not service:
        logger.error(f"未知服务: {service_key}")
        return False
    
    if not os.path.exists(service["pid_file"]):
        return False
    
    try:
        # 读取PID
        with open(service["pid_file"], 'r') as f:
            pid = int(f.read().strip())
        
        # 检查进程是否存在
        if not psutil.pid_exists(pid):
            if os.path.exists(service["pid_file"]):
                os.remove(service["pid_file"])
            return False
        
        # 获取进程对象并检查命令行
        process = psutil.Process(pid)
        
        # 如果进程名包含python，并且命令行中包含服务脚本名，则认为服务正在运行
        if "python" in process.name().lower():
            cmdline = " ".join(process.cmdline()).lower()
            if os.path.basename(service["script"]).lower() in cmdline:
                return True
        
        # 如果到这里，说明PID文件存在但进程不匹配
        os.remove(service["pid_file"])
        return False
        
    except Exception as e:
        logger.error(f"检查{service['name']}状态失败: {str(e)}")
        return False

# 检查端口是否被占用
def check_port(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return True
    return False

# 获取所有服务状态
def get_all_services_status():
    status = {}
    for key, service in SERVICES.items():
        running = is_service_running(key)
        
        status[key] = {
            "name": service["name"],
            "running": running,
            "script": service["script"],
            "port": service.get("port")
        }
        
        # 如果服务正在运行，添加PID和进程信息
        if running:
            with open(service["pid_file"], 'r') as f:
                pid = int(f.read().strip())
            
            try:
                process = psutil.Process(pid)
                status[key]["pid"] = pid
                status[key]["cpu_percent"] = process.cpu_percent(interval=0.1)
                status[key]["memory_percent"] = process.memory_percent()
                status[key]["create_time"] = datetime.fromtimestamp(
                    process.create_time()).strftime("%Y-%m-%d %H:%M:%S")
                
                # 如果有端口，检查端口是否被占用
                if "port" in service:
                    status[key]["port_active"] = check_port(service["port"])
            except:
                # 进程可能已经终止
                status[key]["running"] = False
    
    return status

# 主函数
def main():
    parser = argparse.ArgumentParser(description='WeQ服务管理工具')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status'],
                      help='要执行的操作')
    parser.add_argument('services', nargs='*', default=list(SERVICES.keys()),
                      help='要操作的服务，不指定则操作所有服务')
    
    args = parser.parse_args()
    
    # 检查指定的服务是否存在
    unknown_services = [s for s in args.services if s not in SERVICES]
    if unknown_services:
        logger.error(f"未知服务: {', '.join(unknown_services)}")
        sys.exit(1)
    
    # 执行相应的操作
    if args.action == 'start':
        logger.info("启动服务...")
        for service in args.services:
            start_service(service)
    
    elif args.action == 'stop':
        logger.info("停止服务...")
        for service in args.services:
            stop_service(service)
    
    elif args.action == 'restart':
        logger.info("重启服务...")
        for service in args.services:
            stop_service(service)
            time.sleep(1)
            start_service(service)
    
    elif args.action == 'status':
        status = get_all_services_status()
        
        print("\nWeQ服务状态:")
        print("="*50)
        
        for key, info in status.items():
            if key in args.services:
                status_str = "运行中" if info["running"] else "已停止"
                print(f"{info['name']}: {status_str}")
                
                if info["running"]:
                    print(f"  PID: {info.get('pid', 'N/A')}")
                    print(f"  CPU: {info.get('cpu_percent', 'N/A'):.1f}%")
                    print(f"  内存: {info.get('memory_percent', 'N/A'):.1f}%")
                    print(f"  启动时间: {info.get('create_time', 'N/A')}")
                    
                    if "port" in info:
                        port_status = "活跃" if info.get("port_active", False) else "未使用"
                        print(f"  端口: {info['port']} ({port_status})")
                
                print()
        
        print("="*50)

if __name__ == "__main__":
    main()

# 量子基因编码: QE-SRV-B7D3F9E1G2H8
# 纠缠状态: 活跃
# 纠缠对象: ['WeQ/scripts/services/WeQ_app.py', 'WeQ/scripts/services/WeQ_start_all.ps1']
# 纠缠强度: 0.96

# 开发团队：中华 ZhoHo ，Claude 