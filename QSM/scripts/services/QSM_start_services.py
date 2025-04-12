#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QSM服务启动脚本
启动QSM模型相关的服务，支持后台运行和进程管理
"""

import os
import sys
import time
import signal
import logging
import argparse
import subprocess
import threading
import psutil
from pathlib import Path
from logging.handlers import RotatingFileHandler

# 设置项目根目录
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(ROOT_DIR)

# 创建日志目录
LOG_DIR = ROOT_DIR / '.logs'
LOG_DIR.mkdir(exist_ok=True)
PID_DIR = ROOT_DIR / '.pids'
PID_DIR.mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        RotatingFileHandler(
            LOG_DIR / 'qsm_services.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('QSM-Services')

class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.services = {}
        self.stop_event = threading.Event()
        
    def save_pid(self, service_name, pid):
        """保存进程ID"""
        pid_file = PID_DIR / f"{service_name}.pid"
        with open(pid_file, 'w') as f:
            f.write(str(pid))
            
    def load_pid(self, service_name):
        """加载进程ID"""
        pid_file = PID_DIR / f"{service_name}.pid"
        if pid_file.exists():
            with open(pid_file) as f:
                return int(f.read().strip())
        return None
        
    def is_service_running(self, service_name):
        """检查服务是否在运行"""
        pid = self.load_pid(service_name)
        if pid is None:
            return False
            
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            return False
            
    def start_service(self, cmd, service_name, cwd=None):
        """启动服务"""
        try:
            # 检查服务是否已在运行
            if self.is_service_running(service_name):
                logger.info(f"{service_name}已在运行")
                return True
                
            # 启动进程
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # 保存进程信息
            self.services[service_name] = process
            self.save_pid(service_name, process.pid)
            
            # 启动日志监控线程
            threading.Thread(
                target=self._monitor_logs,
                args=(process, service_name),
                daemon=True
            ).start()
            
            logger.info(f"{service_name}启动成功 - PID: {process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"启动{service_name}失败: {str(e)}")
            return False
            
    def _monitor_logs(self, process, service_name):
        """监控服务日志"""
        while not self.stop_event.is_set() and process.poll() is None:
            output = process.stdout.readline()
            if output:
                logger.info(f"[{service_name}] {output.strip()}")
            error = process.stderr.readline()
            if error:
                logger.error(f"[{service_name}] {error.strip()}")
                
    def stop_service(self, service_name):
        """停止服务"""
        try:
            pid = self.load_pid(service_name)
            if pid is None:
                return True
                
            process = psutil.Process(pid)
            children = process.children(recursive=True)
            
            # 发送终止信号
            process.terminate()
            
            # 等待进程结束
            gone, alive = psutil.wait_procs([process] + children, timeout=3)
            
            # 强制结束未响应的进程
            for p in alive:
                p.kill()
                
            # 删除PID文件
            (PID_DIR / f"{service_name}.pid").unlink(missing_ok=True)
            
            logger.info(f"{service_name}已停止")
            return True
            
        except psutil.NoSuchProcess:
            logger.warning(f"{service_name}进程不存在")
            return True
        except Exception as e:
            logger.error(f"停止{service_name}失败: {str(e)}")
            return False

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='QSM服务启动器')
    parser.add_argument('--port', type=int, default=5000, help='API服务端口')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='API服务地址')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    parser.add_argument('--stop', action='store_true', help='停止所有服务')
    parser.add_argument('--all', action='store_true', help='启动所有服务')
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    service_mgr = ServiceManager()
    
    try:
        if args.stop:
            # 停止所有服务
            service_mgr.stop_service('qsm-api')
            logger.info("所有服务已停止")
            return
            
        # 启动API服务
        api_script = ROOT_DIR / 'api' / 'qsm_api.py'
        if not api_script.exists():
            logger.error(f"API服务脚本不存在: {api_script}")
            sys.exit(1)
            
        cmd = [
            sys.executable,
            str(api_script),
            '--port', str(args.port),
            '--host', args.host
        ]
        
        if args.debug:
            cmd.append('--debug')
            
        if not service_mgr.start_service(cmd, 'qsm-api', cwd=str(ROOT_DIR)):
            logger.error("启动API服务失败")
            sys.exit(1)
            
        # 注册信号处理
        def signal_handler(signum, frame):
            logger.info("接收到停止信号，正在关闭服务...")
            service_mgr.stop_event.set()
            service_mgr.stop_service('qsm-api')
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 保持主进程运行
        while not service_mgr.stop_event.is_set():
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"服务异常: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()

"""
量子基因编码: QE-SRV-QSM-S5E2R7V1
纠缠状态: 活跃
纠缠对象: ['api/qsm_api.py', 'core/qsm_core.py']
纠缠强度: 0.99
"""

# 开发团队：中华 ZhoHo，Claude 