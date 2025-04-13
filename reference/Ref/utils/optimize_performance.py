#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ref系统性能优化工具
用于优化Ref模型的性能和Cursor编辑器的响应速度
"""

import os
import sys
import logging
import time
import json
import shutil
import psutil
import threading
from datetime import datetime, timedelta

# 添加项目根目录到sys.path
parent_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(parent_dir, '..')))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ref_optimize.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Ref-Optimizer")

# 配置
CONFIG = {
    "cache_retention_days": 7,        # 缓存保留天数
    "memory_threshold": 80,           # 内存占用阈值(%)
    "cleanup_interval": 3600,         # 自动清理间隔(秒)
    "watch_memory": True,             # 是否监控内存使用
    "optimize_file_system": True,     # 是否优化文件系统
    "optimize_cursor": True,          # 是否优化Cursor性能
}

IGNORED_DIRS = [
    'node_modules',
    '.git',
    '__pycache__',
    '.venv',
    '.cursor',
    '.idea',
]


def get_memory_usage():
    """获取当前内存使用情况"""
    return psutil.virtual_memory().percent


def optimize_file_system():
    """优化文件系统，清理临时文件和缓存"""
    logger.info("开始优化文件系统...")
    
    # 项目根目录
    project_root = os.path.abspath(os.path.join(parent_dir, '..'))
    
    # 清理的文件类型和目录
    patterns_to_clean = [
        '**/__pycache__',
        '**/*.pyc',
        '**/*.pyo',
        '**/*.log',
        '**/node_modules',
        '**/.pytest_cache',
        '**/.coverage',
        '**/htmlcov',
        '**/build',
        '**/dist',
        '**/*.egg-info',
    ]
    
    # 不清理的目录
    exclude_dirs = [
        '.git',
        '.venv',
        '.cursor',
        'env',
    ]
    
    # 获取截止日期
    cutoff_date = datetime.now() - timedelta(days=CONFIG["cache_retention_days"])
    total_cleaned = 0
    
    for root, dirs, files in os.walk(project_root, topdown=True):
        # 跳过排除的目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # 清理符合模式的文件
        for file in files:
            file_path = os.path.join(root, file)
            
            # 检查是否是缓存文件
            is_cache_file = any(
                file.endswith(ext) for ext in ['.pyc', '.pyo', '.log', '.tmp', '.cache']
            )
            
            if is_cache_file:
                try:
                    # 检查文件修改时间
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mod_time < cutoff_date:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        total_cleaned += file_size
                        logger.debug(f"已删除: {file_path}")
                except Exception as e:
                    logger.warning(f"清理文件时出错: {file_path} - {str(e)}")
        
        # 清理空的__pycache__目录
        for dir_name in dirs:
            if dir_name == "__pycache__":
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        logger.debug(f"已删除空目录: {dir_path}")
                except Exception as e:
                    logger.warning(f"删除目录时出错: {dir_path} - {str(e)}")
    
    logger.info(f"文件系统优化完成，共清理: {total_cleaned/1024/1024:.2f} MB")
    return total_cleaned


def optimize_cursor_performance():
    """优化Cursor编辑器性能"""
    logger.info("开始优化Cursor性能...")
    
    # 项目根目录
    project_root = os.path.abspath(os.path.join(parent_dir, '..'))
    
    # Cursor配置文件路径
    cursor_settings_path = os.path.join(project_root, '.cursor', 'settings.json')
    
    # 优化设置
    optimized_settings = {
        "editor.minimap.enabled": False,
        "editor.scrollBeyondLastLine": False,
        "editor.renderWhitespace": "none",
        "editor.renderControlCharacters": False,
        "editor.folding": True,
        "editor.foldingStrategy": "indentation",
        "editor.wordWrap": "off",
        "editor.suggest.shareSuggestSelections": True,
        "editor.acceptSuggestionOnEnter": "smart",
        "editor.smoothScrolling": False,
        "editor.cursorBlinking": "solid",
        "editor.cursorSmoothCaretAnimation": "off",
        "editor.mouseWheelScrollSensitivity": 1,
        "workbench.list.smoothScrolling": False,
        "workbench.editor.enablePreview": False,
        "workbench.editor.enablePreviewFromQuickOpen": False,
        "workbench.startupEditor": "none",
        "workbench.enableExperiments": False,
        "workbench.tree.indent": 8,
        "files.exclude": {
            "**/.git": True,
            "**/.svn": True,
            "**/.hg": True,
            "**/CVS": True,
            "**/.DS_Store": True,
            "**/__pycache__": True,
            "**/*.pyc": True
        },
        "search.exclude": {
            "**/node_modules": True,
            "**/bower_components": True,
            "**/*.code-search": True,
            "**/__pycache__": True,
            "**/*.pyc": True
        },
        "files.watcherExclude": {
            "**/.git/objects/**": True,
            "**/.git/subtree-cache/**": True,
            "**/node_modules/**": True,
            "**/__pycache__/**": True
        }
    }
    
    # 创建.cursor目录（如果不存在）
    cursor_dir = os.path.dirname(cursor_settings_path)
    if not os.path.exists(cursor_dir):
        os.makedirs(cursor_dir)
    
    # 更新或创建设置文件
    if os.path.exists(cursor_settings_path):
        try:
            with open(cursor_settings_path, 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
            
            # 合并设置
            existing_settings.update(optimized_settings)
            
            with open(cursor_settings_path, 'w', encoding='utf-8') as f:
                json.dump(existing_settings, f, indent=2)
            
            logger.info("Cursor设置已更新")
        except Exception as e:
            logger.error(f"更新Cursor设置时出错: {str(e)}")
    else:
        try:
            with open(cursor_settings_path, 'w', encoding='utf-8') as f:
                json.dump(optimized_settings, f, indent=2)
            
            logger.info("Cursor设置已创建")
        except Exception as e:
            logger.error(f"创建Cursor设置时出错: {str(e)}")
    
    logger.info("Cursor性能优化完成")


def memory_monitor_thread():
    """内存监控线程"""
    logger.info("启动内存监控...")
    
    while CONFIG["watch_memory"]:
        mem_usage = get_memory_usage()
        
        if mem_usage > CONFIG["memory_threshold"]:
            logger.warning(f"内存使用率高: {mem_usage}% > 阈值 {CONFIG['memory_threshold']}%")
            logger.info("开始执行紧急清理...")
            
            # 执行紧急优化
            optimize_file_system()
            
            # 建议进行垃圾回收
            import gc
            gc.collect()
            
            # 记录优化后的内存使用情况
            new_mem_usage = get_memory_usage()
            logger.info(f"清理后内存使用率: {new_mem_usage}%")
        
        # 休眠一段时间
        time.sleep(60)  # 每分钟检查一次


def start_memory_monitor():
    """启动内存监控线程"""
    if CONFIG["watch_memory"]:
        thread = threading.Thread(target=memory_monitor_thread, daemon=True)
        thread.start()
        return thread
    return None


def optimize_ref_system():
    """优化Ref系统性能"""
    logger.info("开始Ref系统性能优化...")
    
    # 加载系统优化插件
    try:
        from Ref.repair import repair_utils
        repair_utils.optimize_quantum_memory()
        logger.info("量子内存优化完成")
    except ImportError:
        logger.warning("无法导入量子内存优化模块")
    
    # 优化量子通信系统
    try:
        from Ref.quantum_entanglement_comm import optimize_entanglement
        optimize_entanglement()
        logger.info("量子纠缠通信优化完成")
    except ImportError:
        logger.warning("无法导入量子纠缠通信优化模块")
    
    logger.info("Ref系统性能优化完成")


def main():
    """主函数"""
    logger.info("===== Ref系统性能优化工具启动 =====")
    
    try:
        # 监控内存使用
        monitor_thread = start_memory_monitor()
        
        # 优化文件系统
        if CONFIG["optimize_file_system"]:
            optimize_file_system()
        
        # 优化Cursor性能
        if CONFIG["optimize_cursor"]:
            optimize_cursor_performance()
        
        # 优化Ref系统
        optimize_ref_system()
        
        logger.info("===== 所有优化任务完成 =====")
        
        # 启动定期优化
        while True:
            logger.info(f"等待 {CONFIG['cleanup_interval']} 秒后再次执行优化...")
            time.sleep(CONFIG["cleanup_interval"])
            
            logger.info("开始定期优化...")
            if CONFIG["optimize_file_system"]:
                optimize_file_system()
            
            if CONFIG["optimize_cursor"]:
                optimize_cursor_performance()
    
    except KeyboardInterrupt:
        logger.info("收到中断信号，优化工具退出")
    except Exception as e:
        logger.error(f"优化过程中出错: {str(e)}")
    finally:
        # 设置监控标志为False，结束监控线程
        CONFIG["watch_memory"] = False
        if monitor_thread:
            monitor_thread.join(timeout=1.0)
        
        logger.info("优化工具已退出")


if __name__ == "__main__":
    # 解析命令行参数
    if len(sys.argv) > 1:
        # 如果有参数，则执行单次优化
        logger.info("执行单次优化...")
        if CONFIG["optimize_file_system"]:
            optimize_file_system()
        
        if CONFIG["optimize_cursor"]:
            optimize_cursor_performance()
        
        optimize_ref_system()
    else:
        # 否则作为服务运行
        main() 

# 量子基因编码: QE-OPT-404CABF8E80C
# 纠缠状态: 活跃
# 纠缠对象: ["Ref/ref_core.py", "Ref/utils/file_monitor.py"]
# 纠缠强度: 0.98

# 开发团队：中华 ZhoHo ，Claude 
