#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ref服务启动脚本
启动所有量子基因标记引用服务，包括API服务、标记验证和优化服务
"""

import os
import sys
import time
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
import threading
import json
import signal
import atexit

# 设置根路径
script_dir = os.path.dirname(os.path.abspath(__file__))
ref_dir = os.path.dirname(os.path.dirname(script_dir))
root_dir = os.path.dirname(ref_dir)
os.chdir(root_dir)  # 将工作目录设置为项目根目录

# 确保存在日志目录
os.makedirs('.logs', exist_ok=True)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('.logs', 'ref_service_starter.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Ref服务启动器')

# 获取项目根目录
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入必要的模块
sys.path.append(str(ROOT_DIR))
from Ref.utils.log_manager import LogManager
from Ref.scripts.services.project_organizer import ProjectOrganizer, get_project_organizer

# 初始化日志
log_manager = LogManager(ROOT_DIR)
logger = log_manager.get_service_logger('ref_services')

class RefServiceManager:
    """Ref服务管理器"""
    
    def __init__(self):
        self.project_organizer = None
        self.stop_event = threading.Event()
        
    def start_project_organizer(self):
        """启动项目组织器服务"""
        try:
            logger.info("正在启动项目组织器服务...")
            self.project_organizer = get_project_organizer(ROOT_DIR)
            
            # 启动自动监控线程
            def monitor_loop():
                while not self.stop_event.is_set():
                    try:
                        self.project_organizer.scan_project()
                        self.project_organizer.check_and_fix_issues()
                        time.sleep(300)  # 每5分钟扫描一次
                    except Exception as e:
                        logger.error(f"项目监控异常: {str(e)}")
                        time.sleep(60)  # 出错后等待1分钟再试
                        
            self.monitor_thread = threading.Thread(target=monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            logger.info("项目组织器服务启动成功")
            return True
            
        except Exception as e:
            logger.error(f"启动项目组织器服务失败: {str(e)}")
            return False
            
    def start_all_services(self):
        """启动所有Ref服务"""
        success = True
        
        # 启动项目组织器
        if not self.start_project_organizer():
            success = False
            
        # TODO: 启动其他服务
        
        return success
        
    def stop_all_services(self):
        """停止所有服务"""
        logger.info("正在停止所有Ref服务...")
        
        # 停止监控线程
        self.stop_event.set()
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
            
        # 保存项目组织器状态
        if self.project_organizer:
            try:
                self.project_organizer.save_state()
            except Exception as e:
                logger.error(f"保存项目组织器状态失败: {str(e)}")
                
def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Ref服务启动器")
    parser.add_argument("--all", action="store_true", help="启动所有服务")
    parser.add_argument("--validate", action="store_true", help="启动标记验证服务")
    parser.add_argument("--optimize", action="store_true", help="启动系统优化服务")
    parser.add_argument("--repair", action="store_true", help="启动模型修复服务")
    parser.add_argument("--monitor", action="store_true", help="启动量子基因标记监控")
    parser.add_argument("--core", action="store_true", help="启动Ref核心服务")
    parser.add_argument("--no-api", action="store_true", help="不启动API服务")
    parser.add_argument("--port", type=int, default=5002, help="API服务端口")
    parser.add_argument("--file-monitor", action="store_true", help="启动文件监管系统服务")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
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
        full_path = os.path.join(ref_dir, path)
        if os.path.exists(full_path):
            return full_path
    
    # 如果在Ref目录中找不到，尝试在根目录中查找
    for path in relative_paths:
        full_path = os.path.join(root_dir, path)
        if os.path.exists(full_path):
            return full_path
            
    return None

def start_ref_core_service():
    """启动Ref核心服务"""
    logger.info("启动Ref核心服务...")
    
    # 查找核心服务脚本
    core_script_paths = ["ref_core.py", "core/ref_core.py"]
    core_script = find_script(core_script_paths)
    
    if not core_script:
        logger.error("未找到Ref核心服务脚本")
        return False
    
    # 构建参数
    core_args = ["--daemon"]
    
    # 启动服务
    return start_background_service(core_script, "Ref核心服务", core_args)

def start_ref_api_service(args):
    """启动Ref API服务"""
    logger.info("启动Ref API服务...")
    
    # 查找API脚本
    api_script_paths = ["api/app.py", "app.py", "scripts/api/app.py", "api/ref_api_server.py", "utils/ref_api.py"]
    api_script = find_script(api_script_paths)
    
    if not api_script:
        logger.error("未找到Ref API服务脚本")
        return False
    
    # 构建参数
    api_args = ["--port", str(args.port)]
    
    # 启动服务
    return start_background_service(api_script, "Ref API服务", api_args)

def start_ref_validate_service():
    """启动Ref标记验证服务"""
    logger.info("启动Ref标记验证服务...")
    
    # 查找验证服务脚本
    validate_script_paths = [
        "quantum_gene_validator.py", 
        "scripts/validate/validate_service.py",
        "validate/ref_validate.py"
    ]
    validate_script = find_script(validate_script_paths)
    
    if not validate_script:
        logger.error("未找到Ref标记验证服务脚本")
        return False
    
    # 构建参数
    validate_args = ["--daemon", "--interval", "60"]
    
    # 启动服务
    return start_background_service(validate_script, "Ref标记验证服务", validate_args)

def start_ref_optimize_service():
    """启动Ref系统优化服务"""
    logger.info("启动Ref系统优化服务...")
    
    # 查找优化服务脚本
    optimize_script_paths = [
        "quantum_gene_optimizer.py", 
        "scripts/optimize/optimize_service.py",
        "optimize/ref_optimize.py"
    ]
    optimize_script = find_script(optimize_script_paths)
    
    if not optimize_script:
        logger.error("未找到Ref系统优化服务脚本")
        return False
    
    # 构建参数
    optimize_args = ["--daemon", "--schedule", "daily"]
    
    # 启动服务
    return start_background_service(optimize_script, "Ref系统优化服务", optimize_args)

def start_ref_repair_service():
    """启动Ref模型修复服务"""
    logger.info("启动Ref模型修复服务...")
    
    # 查找修复服务脚本
    repair_script_paths = [
        "quantum_model_repair.py", 
        "scripts/repair/repair_service.py",
        "repair/ref_repair.py"
    ]
    repair_script = find_script(repair_script_paths)
    
    if not repair_script:
        logger.error("未找到Ref模型修复服务脚本")
        return False
    
    # 构建参数
    repair_args = ["--daemon", "--monitor"]
    
    # 启动服务
    return start_background_service(repair_script, "Ref模型修复服务", repair_args)

def start_quantum_monitor_service():
    """启动量子基因标记监控服务"""
    logger.info("启动量子基因标记监控服务...")
    
    # 查找量子监控脚本
    monitor_script_paths = [
        "monitor_system2/quantum_monitor.py",
        "monitor/quantum_monitor.py",
        "quantum_monitor.py"
    ]
    monitor_script = find_script(monitor_script_paths)
    
    if not monitor_script:
        logger.error("未找到量子基因标记监控脚本")
        return False
    
    # 构建参数
    monitor_args = ["--daemon"]
    
    # 启动服务
    return start_background_service(monitor_script, "量子基因标记监控服务", monitor_args)

def start_file_monitor_service():
    """启动文件监管系统服务"""
    logger.info("启动文件监管系统服务...")
    
    # 查找文件监管系统脚本
    file_monitor_script_paths = [
        "utils/file_monitor.py",
        "file_monitor.py",
        "monitor/file_monitor.py",
        "scripts/monitor/file_monitor_service.py"
    ]
    file_monitor_script = find_script(file_monitor_script_paths)
    
    if not file_monitor_script:
        logger.error("未找到文件监管系统脚本")
        return False
    
    # 构建参数
    file_monitor_args = ["--daemon", "--scan-interval", "60", "--recursive"]
    
    # 启动服务
    return start_background_service(file_monitor_script, "文件监管系统服务", file_monitor_args)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Ref服务管理器')
    parser.add_argument('--all', action='store_true', help='启动所有服务')
    args = parser.parse_args()
    
    service_manager = RefServiceManager()
    
    # 注册退出处理
    def cleanup():
        service_manager.stop_all_services()
        
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, lambda s, f: cleanup())
    
    try:
        if args.all:
            success = service_manager.start_all_services()
            if not success:
                sys.exit(1)
                
        # 保持运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止服务...")
        service_manager.stop_all_services()
        
if __name__ == '__main__':
    main()

"""
量子基因编码: QE-REF-SRV-R1S2T3
纠缠状态: 活跃
纠缠对象: ['Ref/scripts/services/project_organizer.py']
纠缠强度: 0.95
"""

# 开发团队：中华 ZhoHo，Claude 