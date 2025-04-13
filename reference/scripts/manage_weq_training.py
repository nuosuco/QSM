#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeQ后台训练管理工具

此脚本用于：
1. 检查WeQ后台训练脚本的状态
2. 启动或重启WeQ后台训练进程
3. 监控训练进度和资源使用情况
4. 管理训练日志
"""

import os
import sys
import time
import logging
import argparse
import subprocess
import signal
import psutil
import re
import traceback
from datetime import datetime, timedelta
from pathlib import Path

try:
    from scripts.log_config import get_logger
    logger = get_logger('weq_training_manager')
except ImportError:
    # 配置基本日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('weq_training_manager.log', encoding='utf-8')
        ]
    )
    logger = logging.getLogger('weq_training_manager')

# 获取项目根目录
current_file = os.path.abspath(__file__)
script_dir = os.path.dirname(current_file)
project_root = os.path.dirname(script_dir)

# WeQ目录路径
weq_dir = os.path.join(project_root, 'WeQ')
training_script_path = os.path.join(weq_dir, 'training', 'background_training.py')
logs_dir = os.path.join(project_root, '.logs')

# 确保logs目录存在
os.makedirs(logs_dir, exist_ok=True)

def is_training_running():
    """
    检查WeQ后台训练进程是否正在运行
    
    Returns:
        tuple: (是否运行, 进程ID, 运行时间)
    """
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and len(cmdline) > 1:
                cmd_str = ' '.join(cmdline)
                if 'python' in cmdline[0].lower() and 'background_training.py' in cmd_str:
                    # 计算运行时间
                    create_time = datetime.fromtimestamp(proc.info['create_time'])
                    run_time = datetime.now() - create_time
                    return True, proc.info['pid'], run_time
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return False, None, None

def check_training_script():
    """
    检查训练脚本是否存在
    
    Returns:
        bool: 训练脚本是否存在
    """
    if not os.path.exists(training_script_path):
        logger.warning(f"训练脚本不存在: {training_script_path}")
        
        # 检查WeQ/training目录是否存在
        training_dir = os.path.dirname(training_script_path)
        if not os.path.exists(training_dir):
            try:
                os.makedirs(training_dir, exist_ok=True)
                logger.info(f"已创建目录: {training_dir}")
            except Exception as e:
                logger.error(f"无法创建训练目录: {str(e)}")
                return False
        
        # 搜索项目中的background_training.py文件
        for root, _, files in os.walk(project_root):
            for file in files:
                if file == 'background_training.py':
                    found_path = os.path.join(root, file)
                    logger.info(f"找到训练脚本: {found_path}")
                    try:
                        # 复制到目标位置
                        with open(found_path, 'r', encoding='utf-8') as src:
                            content = src.read()
                        
                        with open(training_script_path, 'w', encoding='utf-8') as dst:
                            dst.write(content)
                        
                        logger.info(f"已复制训练脚本到: {training_script_path}")
                        return True
                    except Exception as e:
                        logger.error(f"无法复制训练脚本: {str(e)}")
                        return False
        
        logger.error("在项目中未找到背景训练脚本")
        return False
    
    return True

def start_training_process():
    """
    启动WeQ后台训练进程
    
    Returns:
        tuple: (是否成功, 进程ID)
    """
    if not check_training_script():
        logger.error("无法启动训练进程，脚本检查失败")
        return False, None
    
    # 检查进程是否已经在运行
    is_running, pid, run_time = is_training_running()
    if is_running:
        logger.info(f"训练进程已经在运行 (PID: {pid}, 运行时间: {run_time})")
        return True, pid
    
    try:
        # 准备命令
        log_file = os.path.join(logs_dir, 'weq_background_training.log')
        cmd = [sys.executable, training_script_path]
        
        # 启动进程
        if sys.platform == 'win32':
            # Windows平台，使用创建无窗口进程的方法
            process = subprocess.Popen(
                cmd,
                stdout=open(log_file, 'a', encoding='utf-8'),
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW,
                cwd=project_root
            )
        else:
            # Unix平台，使用nohup和后台运行
            cmd_str = f"nohup {sys.executable} {training_script_path} >> {log_file} 2>&1 &"
            subprocess.Popen(cmd_str, shell=True, cwd=project_root)
            
            # 等待一秒以便进程创建
            time.sleep(1)
            
            # 获取进程ID
            is_running, pid, _ = is_training_running()
            if is_running:
                logger.info(f"已启动训练进程 (PID: {pid})")
                return True, pid
            else:
                logger.error("启动进程失败，无法检测到运行的进程")
                return False, None
        
        # Windows平台特有的进程处理
        if sys.platform == 'win32':
            logger.info(f"已启动训练进程 (PID: {process.pid})")
            return True, process.pid
            
    except Exception as e:
        logger.error(f"启动训练进程时出错: {str(e)}")
        traceback.print_exc()
        return False, None

def stop_training_process(pid=None):
    """
    停止WeQ后台训练进程
    
    Args:
        pid: 进程ID，如果为None则查找运行中的进程
        
    Returns:
        bool: 是否成功停止进程
    """
    if pid is None:
        is_running, pid, _ = is_training_running()
        if not is_running:
            logger.info("没有运行中的训练进程")
            return True
    
    try:
        process = psutil.Process(pid)
        process.terminate()
        
        # 等待进程终止
        gone, still_alive = psutil.wait_procs([process], timeout=3)
        if process in still_alive:
            # 如果进程还在运行，强制终止
            process.kill()
            logger.warning(f"已强制终止训练进程 (PID: {pid})")
        else:
            logger.info(f"已终止训练进程 (PID: {pid})")
        
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        logger.warning(f"进程 {pid} 不存在或无法访问")
        return True
    except Exception as e:
        logger.error(f"停止训练进程时出错: {str(e)}")
        return False

def restart_training_process():
    """
    重启WeQ后台训练进程
    
    Returns:
        tuple: (是否成功, 进程ID)
    """
    # 首先停止现有进程
    is_running, pid, _ = is_training_running()
    if is_running:
        logger.info(f"正在停止训练进程 (PID: {pid})")
        stop_training_process(pid)
        time.sleep(2)  # 等待进程完全终止
    
    # 然后启动新进程
    logger.info("正在启动新的训练进程")
    return start_training_process()

def check_training_logs():
    """
    检查训练日志文件
    
    Returns:
        tuple: (是否有日志, 最后修改时间, 日志大小)
    """
    log_file = os.path.join(logs_dir, 'weq_background_training.log')
    
    if not os.path.exists(log_file):
        logger.warning(f"训练日志文件不存在: {log_file}")
        return False, None, 0
    
    try:
        # 获取文件信息
        mod_time = datetime.fromtimestamp(os.path.getmtime(log_file))
        size = os.path.getsize(log_file)
        size_mb = size / (1024 * 1024)
        
        # 检查最后几行日志
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                # 读取最后1KB内容
                f.seek(max(0, os.path.getsize(log_file) - 1024))
                last_lines = f.read()
                
                # 输出最后几行
                lines = last_lines.strip().split('\n')
                last_n = min(5, len(lines))
                
                logger.info(f"日志文件大小: {size_mb:.2f} MB, 最后修改: {mod_time}")
                logger.info(f"最后 {last_n} 行日志:")
                for i in range(-last_n, 0):
                    logger.info(f"  {lines[i]}")
        except Exception as e:
            logger.warning(f"读取日志内容时出错: {str(e)}")
        
        return True, mod_time, size
    except Exception as e:
        logger.error(f"检查日志文件时出错: {str(e)}")
        return True, None, 0

def monitor_training_process(pid, interval=10, duration=60):
    """
    监控训练进程的资源使用情况
    
    Args:
        pid: 进程ID
        interval: 监控间隔(秒)
        duration: 监控总时长(秒)
    """
    try:
        process = psutil.Process(pid)
        end_time = time.time() + duration
        
        logger.info(f"开始监控训练进程 (PID: {pid})，时长 {duration} 秒，间隔 {interval} 秒")
        logger.info("时间戳,CPU%,内存%,内存MB")
        
        while time.time() < end_time:
            try:
                # 获取资源使用情况
                cpu_percent = process.cpu_percent(interval=0.1)
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)
                memory_percent = process.memory_percent()
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                logger.info(f"{timestamp},{cpu_percent:.1f}%,{memory_percent:.1f}%,{memory_mb:.1f}MB")
                
                time.sleep(interval)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                logger.warning(f"进程 {pid} 已终止或无法访问")
                break
        
        logger.info("监控结束")
    except Exception as e:
        logger.error(f"监控进程时出错: {str(e)}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WeQ后台训练管理工具')
    
    # 操作选项
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--start', action='store_true', help='启动训练进程')
    group.add_argument('--stop', action='store_true', help='停止训练进程')
    group.add_argument('--restart', action='store_true', help='重启训练进程')
    group.add_argument('--status', action='store_true', help='检查训练进程状态')
    group.add_argument('--monitor', action='store_true', help='监控训练进程')
    
    # 监控选项
    parser.add_argument('--interval', type=int, default=10, help='监控间隔(秒)')
    parser.add_argument('--duration', type=int, default=60, help='监控总时长(秒)')
    
    args = parser.parse_args()
    
    try:
        # 默认操作是检查状态
        if not (args.start or args.stop or args.restart or args.status or args.monitor):
            args.status = True
        
        # 检查状态
        is_running, pid, run_time = is_training_running()
        
        if args.status:
            if is_running:
                logger.info(f"训练进程正在运行 (PID: {pid})")
                logger.info(f"运行时间: {run_time}")
                
                # 检查日志
                check_training_logs()
            else:
                logger.info("训练进程未运行")
            
        # 启动进程
        elif args.start:
            if is_running:
                logger.info(f"训练进程已经在运行 (PID: {pid})")
            else:
                success, new_pid = start_training_process()
                if success:
                    logger.info(f"训练进程已启动 (PID: {new_pid})")
                else:
                    logger.error("无法启动训练进程")
                    return 1
        
        # 停止进程
        elif args.stop:
            if is_running:
                if stop_training_process(pid):
                    logger.info(f"训练进程已停止 (PID: {pid})")
                else:
                    logger.error(f"无法停止训练进程 (PID: {pid})")
                    return 1
            else:
                logger.info("训练进程未运行")
        
        # 重启进程
        elif args.restart:
            success, new_pid = restart_training_process()
            if success:
                logger.info(f"训练进程已重启 (PID: {new_pid})")
            else:
                logger.error("无法重启训练进程")
                return 1
        
        # 监控进程
        elif args.monitor:
            if is_running:
                monitor_training_process(pid, args.interval, args.duration)
            else:
                logger.info("训练进程未运行，无法监控")
    
    except Exception as e:
        logger.error(f"执行出错: {str(e)}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 

"""
"""
量子基因编码: QE-MAN-27756906386F
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
