#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子系统服务启动脚本
启动所有必要的后台服务，支持监控、优化和训练
"""

import os
import sys
import time
import logging
import argparse
import subprocess
from pathlib import Path
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
        logging.FileHandler(os.path.join('.logs', 'service_starter.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('服务启动器')

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="量子系统服务启动器")
    parser.add_argument("--all", action="store_true", help="启动所有服务")
    parser.add_argument("--ref-core", action="store_true", help="启动Ref核心服务")
    parser.add_argument("--monitor", action="store_true", help="启动量子基因标记监控")
    parser.add_argument("--file-monitor", action="store_true", help="启动文件监控系统")
    parser.add_argument("--qsm-api", action="store_true", help="启动QSM API服务")
    parser.add_argument("--qentl", action="store_true", help="启动QEntL引擎服务")
    parser.add_argument("--weq-train", action="store_true", help="启动WeQ训练服务")
    parser.add_argument("--weq-all", action="store_true", help="启动所有WeQ相关服务")
    parser.add_argument("--fix-qgm", action="store_true", help="修复量子基因标记")
    parser.add_argument("--optimize", action="store_true", help="执行系统优化")
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
            cmd.extend(args.split())
            
        # 启动进程，重定向输出到日志文件
        with open(log_file, 'w', encoding='utf-8') as out_f, open(err_file, 'w', encoding='utf-8') as err_f:
            process = subprocess.Popen(
                cmd,
                stdout=out_f,
                stderr=err_f,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
        logger.info(f"成功启动服务: {service_name}, PID: {process.pid}, 日志: {log_file}")
        return True
        
    except Exception as e:
        logger.error(f"启动服务失败: {service_name}, 错误: {str(e)}")
        return False

def run_powershell_script(script_path, args=""):
    """运行PowerShell脚本"""
    try:
        # 确保脚本路径存在
        if not os.path.exists(script_path):
            logger.error(f"PowerShell脚本不存在: {script_path}")
            return False
            
        # 创建日志文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join('.logs', f"powershell_{timestamp}.log")
        
        # 构建命令
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path]
        if args:
            cmd.extend(args.split())
            
        # 启动进程，重定向输出到日志文件
        with open(log_file, 'w', encoding='utf-8') as out_f:
            process = subprocess.Popen(
                cmd,
                stdout=out_f,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
        logger.info(f"成功运行PowerShell脚本: {script_path}, PID: {process.pid}, 日志: {log_file}")
        return True
        
    except Exception as e:
        logger.error(f"运行PowerShell脚本失败: {script_path}, 错误: {str(e)}")
        return False

def optimize_system():
    """执行系统优化"""
    logger.info("开始执行系统优化...")
    
    # 首先尝试PowerShell优化脚本
    optimize_script = os.path.join("scripts", "maintenance", "optimize_cursor.ps1")
    if os.path.exists(optimize_script):
        if run_powershell_script(optimize_script):
            logger.info("系统优化脚本已在后台启动")
            return True
    
    # 备用BAT优化脚本
    backup_script = os.path.join("Ref", "monitor", "optimize_cursor.bat")
    if os.path.exists(backup_script):
        try:
            subprocess.Popen(
                [backup_script], 
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            logger.info("备用优化脚本已在后台启动")
            return True
        except Exception as e:
            logger.error(f"运行备用优化脚本失败: {str(e)}")
    
    logger.error("未找到系统优化脚本")
    return False

def fix_quantum_gene_markers():
    """修复量子基因标记"""
    logger.info("开始修复量子基因标记...")
    
    # 使用量子监控脚本修复标记
    monitor_script = os.path.join("monitor_system2", "quantum_monitor.py")
    if os.path.exists(monitor_script):
        try:
            result = subprocess.run(
                [sys.executable, monitor_script, "--fix-markers", "--no-daemon"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("量子基因标记修复成功")
                return True
            else:
                logger.error(f"量子基因标记修复失败: {result.stderr}")
        except Exception as e:
            logger.error(f"运行量子基因标记修复失败: {str(e)}")
    else:
        logger.warning("未找到量子监控脚本，跳过修复")
    
    return False

def find_weq_train_script():
    """查找可用的WeQ训练脚本"""
    scripts = [
        os.path.join("WeQ", "weq_train.py"),
        os.path.join("WeQ", "weq_train_par.py")
    ]
    
    for script in scripts:
        if os.path.exists(script):
            return script
    
    return None

def start_weq_unified_service():
    """启动WeQ统一服务"""
    logger.info("启动WeQ统一服务...")
    
    # 查找可用的WeQ训练脚本
    weq_script = find_weq_train_script()
    if not weq_script:
        logger.error("未找到WeQ训练脚本")
        return False
    
    # 根据脚本类型选择参数
    args = "--hours 24"  # 默认参数
    if weq_script.endswith("weq_train_par.py"):
        args = "--parallel"
    
    # 启动WeQ训练服务
    return start_background_service(weq_script, "WeQ训练服务", args)

def main():
    """主函数"""
    args = parse_args()
    
    # 服务计数器
    services_started = 0
    
    # 判断是否启动所有服务
    start_all = args.all or not any([
        args.ref_core, args.monitor, args.file_monitor, 
        args.qsm_api, args.qentl, args.weq_train, args.weq_all
    ])
    
    # 系统优化
    if args.optimize:
        if optimize_system():
            services_started += 1
    
    # 修复量子基因标记
    if args.fix_qgm:
        if fix_quantum_gene_markers():
            services_started += 1
    
    # 启动WeQ服务
    if args.weq_all or args.weq_train or start_all:
        if start_weq_unified_service():
            services_started += 1
    
    # 启动Ref核心服务
    if args.ref_core or start_all:
        ref_core_path = os.path.join("Ref", "ref_core.py")
        if start_background_service(ref_core_path, "Ref核心服务"):
            services_started += 1
            time.sleep(2)  # 等待核心服务初始化
    
    # 启动量子基因标记监控
    if args.monitor or start_all:
        monitor_path = os.path.join("monitor_system2", "quantum_monitor.py")
        if start_background_service(monitor_path, "量子基因标记监控"):
            services_started += 1
    
    # 启动文件监控系统
    if args.file_monitor or start_all:
        file_monitor_path = os.path.join("Ref", "utils", "file_monitor.py")
        if start_background_service(file_monitor_path, "文件监控系统", "--standalone"):
            services_started += 1
    
    # 启动QSM API服务
    if args.qsm_api or start_all:
        qsm_api_path = os.path.join("QSM", "app.py")
        if start_background_service(qsm_api_path, "QSM API服务"):
            services_started += 1
    
    # 启动QEntL引擎服务
    if args.qentl or start_all:
        qentl_path = os.path.join("QEntL", "engine.py")
        if start_background_service(qentl_path, "QEntL引擎服务"):
            services_started += 1
    
    # 显示启动结果
    if services_started > 0:
        logger.info(f"成功启动 {services_started} 个服务")
        logger.info("所有服务已在后台启动，系统正在运行中")
        logger.info("系统将自动进行量子叠加态优化和资源管理")
    else:
        logger.error("未能启动任何服务")

if __name__ == "__main__":
    print("===== 量子系统服务启动器 =====")
    main()
    print("===== 服务启动完成，控制台可继续使用 =====") 
"""
量子基因编码: QE-STA-098EA1D5140F
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""