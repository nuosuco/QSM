#!/usr/bin/env python3
"""
文件自动监视服务

使用watchdog库监听文件变化并自动调用Ref文件完整性检查功能
"""
import os
import sys
import time
import logging
import threading
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
except ImportError:
    print("请先安装watchdog: pip install watchdog")
    print("watchdog是一个用于监视文件系统事件的第三方库")
    sys.exit(1)

from Ref.utils.file_integrity_monitor import get_monitor
from Ref.utils.file_organization_guardian import get_guardian

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Ref/logs/auto_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('AutoMonitor')

# 全局变量，追踪服务状态
_monitor_service = None
_monitor_status = {
    "running": False,
    "start_time": None,
    "watched_paths": [],
    "event_stats": {
        "created": 0,
        "modified": 0,
        "deleted": 0,
        "moved": 0
    },
    "last_event_time": None
}

# 默认配置
DEFAULT_CONFIG = {
    "watched_paths": ["."],            # 监控的路径列表
    "ignore_patterns": [               # 忽略的文件模式
        "*.pyc", "*.pyo", "__pycache__", 
        ".git", ".idea", ".vscode", 
        "*.log", "*.tmp", "*.bak"
    ],
    "ignore_directories": [".git", ".idea", ".vscode", "__pycache__"],  # 忽略的目录
    "check_interval": 2.0,             # 监控检查间隔（秒）
    "auto_register": True,             # 是否自动注册新文件
    "auto_backup": True,               # 是否自动备份修改的文件
    "notify_conflicts": True,          # 是否通知冲突
    "registry_path": "Ref/data/file_registry.json",  # 注册表路径
    "backup_dir": "Ref/backup/files",  # 备份目录
    "throttle_seconds": 1.0            # 事件节流时间（秒）
}


class FileChangeHandler(FileSystemEventHandler):
    """处理文件系统变化事件的处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化处理器
        
        Args:
            config: 监控配置
        """
        self.config = config
        self.guardian = get_guardian(
            workspace_root=os.path.abspath(os.getcwd()),
            registry_path=self.config["registry_path"],
            backup_dir=self.config["backup_dir"]
        )
        self.monitor = get_monitor(
            registry_path=os.path.join(
                os.path.abspath(os.getcwd()),
                self.config["registry_path"]
            )
        )
        
        # 事件节流机制
        self.last_events = {}
        self.throttle_seconds = self.config["throttle_seconds"]
        
        logger.info("文件变化处理器初始化完成")
    
    def dispatch(self, event):
        """
        调度事件处理
        
        Args:
            event: 文件系统事件
        """
        # 实现事件节流，避免短时间内多次处理同一个文件
        current_time = time.time()
        path = event.src_path
        
        # 如果最近处理过该文件的同类事件，并且在节流时间内，则跳过
        if path in self.last_events:
            last_time, last_event_type = self.last_events[path]
            if (current_time - last_time < self.throttle_seconds and 
                last_event_type == event.event_type):
                return
        
        # 更新最后处理时间和事件类型
        self.last_events[path] = (current_time, event.event_type)
        
        # 处理事件
        super().dispatch(event)
    
    def on_created(self, event):
        """
        处理文件创建事件
        
        Args:
            event: 文件创建事件
        """
        # 更新统计信息
        _monitor_status["event_stats"]["created"] += 1
        _monitor_status["last_event_time"] = datetime.now().isoformat()
        
        if event.is_directory:
            return
        
        # 忽略指定类型的文件
        if self._should_ignore(event.src_path):
            return
        
        logger.info(f"检测到文件创建: {event.src_path}")
        
        if self.config["auto_register"]:
            try:
                # 读取文件内容
                with open(event.src_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 注册新文件
                purpose = f"通过自动监控注册的文件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                success = self.monitor.register_file(
                    event.src_path,
                    content,
                    purpose
                )
                
                if success:
                    logger.info(f"自动注册文件成功: {event.src_path}")
                else:
                    logger.warning(f"自动注册文件失败: {event.src_path}")
            except Exception as e:
                logger.error(f"处理文件创建事件时发生异常: {str(e)}")
    
    def on_modified(self, event):
        """
        处理文件修改事件
        
        Args:
            event: 文件修改事件
        """
        # 更新统计信息
        _monitor_status["event_stats"]["modified"] += 1
        _monitor_status["last_event_time"] = datetime.now().isoformat()
        
        if event.is_directory:
            return
        
        # 忽略指定类型的文件
        if self._should_ignore(event.src_path):
            return
        
        logger.info(f"检测到文件修改: {event.src_path}")
        
        try:
            # 读取文件内容
            with open(event.src_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 检查文件是否已注册
            if event.src_path in self.monitor.file_registry:
                # 检查冲突
                conflict = self.monitor.check_conflicts(event.src_path, content)
                
                if conflict is True:
                    logger.warning(f"检测到文件冲突: {event.src_path}")
                    
                    # 自动备份
                    if self.config["auto_backup"]:
                        backup_path = self.guardian._backup_file(event.src_path)
                        if backup_path:
                            logger.info(f"已自动备份文件: {backup_path}")
                
                # 更新注册表
                self.monitor.register_file(
                    event.src_path,
                    content,
                    self.monitor.file_registry[event.src_path].get("purpose", ""),
                    self.monitor.file_registry[event.src_path].get("dependencies", [])
                )
                logger.info(f"已更新文件注册信息: {event.src_path}")
            
            elif self.config["auto_register"]:
                # 自动注册新文件
                purpose = f"通过自动监控注册的修改文件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.monitor.register_file(
                    event.src_path,
                    content,
                    purpose
                )
                logger.info(f"自动注册修改的新文件: {event.src_path}")
        
        except Exception as e:
            logger.error(f"处理文件修改事件时发生异常: {str(e)}")
    
    def on_deleted(self, event):
        """
        处理文件删除事件
        
        Args:
            event: 文件删除事件
        """
        # 更新统计信息
        _monitor_status["event_stats"]["deleted"] += 1
        _monitor_status["last_event_time"] = datetime.now().isoformat()
        
        if event.is_directory:
            return
        
        # 忽略指定类型的文件
        if self._should_ignore(event.src_path):
            return
        
        logger.info(f"检测到文件删除: {event.src_path}")
        
        # 如果文件已注册，从注册表中移除
        if event.src_path in self.monitor.file_registry:
            # 从注册表中删除
            if hasattr(self.monitor, 'file_registry') and event.src_path in self.monitor.file_registry:
                del self.monitor.file_registry[event.src_path]
                self.monitor._save_registry()
                logger.info(f"已从注册表中移除删除的文件: {event.src_path}")
    
    def on_moved(self, event):
        """
        处理文件移动事件
        
        Args:
            event: 文件移动事件
        """
        # 更新统计信息
        _monitor_status["event_stats"]["moved"] += 1
        _monitor_status["last_event_time"] = datetime.now().isoformat()
        
        if event.is_directory:
            return
        
        # 忽略指定类型的文件
        if self._should_ignore(event.src_path) or self._should_ignore(event.dest_path):
            return
        
        logger.info(f"检测到文件移动: {event.src_path} -> {event.dest_path}")
        
        # 如果源文件已注册，更新注册表
        if event.src_path in self.monitor.file_registry:
            try:
                # 读取目标文件内容
                with open(event.dest_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 复制源文件的注册信息
                purpose = self.monitor.file_registry[event.src_path].get("purpose", "")
                dependencies = self.monitor.file_registry[event.src_path].get("dependencies", [])
                
                # 从注册表中移除源文件
                del self.monitor.file_registry[event.src_path]
                
                # 注册目标文件
                self.monitor.register_file(
                    event.dest_path,
                    content,
                    purpose,
                    dependencies
                )
                
                logger.info(f"已更新移动文件的注册信息: {event.dest_path}")
            
            except Exception as e:
                logger.error(f"处理文件移动事件时发生异常: {str(e)}")
    
    def _should_ignore(self, path: str) -> bool:
        """
        判断是否应该忽略文件
        
        Args:
            path: 文件路径
            
        Returns:
            是否应该忽略
        """
        # 检查是否是目录
        if os.path.isdir(path):
            dirname = os.path.basename(path)
            if dirname in self.config["ignore_directories"]:
                return True
        
        # 检查文件名模式
        filename = os.path.basename(path)
        for pattern in self.config["ignore_patterns"]:
            if pattern.startswith("*"):
                if filename.endswith(pattern[1:]):
                    return True
            elif pattern.endswith("*"):
                if filename.startswith(pattern[:-1]):
                    return True
            elif pattern == filename:
                return True
        
        return False


class FileWatcherService:
    """文件监视服务，在后台运行监视文件变化"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化服务
        
        Args:
            config: 服务配置
        """
        self.config = config or DEFAULT_CONFIG.copy()
        self.observer = Observer()
        self.handler = FileChangeHandler(self.config)
        self.is_running = False
        self.start_time = None
        
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.join(
            os.getcwd(), self.config["registry_path"])), exist_ok=True)
        os.makedirs(os.path.join(
            os.getcwd(), self.config["backup_dir"]), exist_ok=True)
        
        # 初始化监控状态
        global _monitor_status
        _monitor_status["watched_paths"] = self.config["watched_paths"]
    
    def start(self):
        """启动监视服务"""
        if self.is_running:
            logger.warning("监视服务已经在运行中")
            return
        
        # 添加要监视的路径
        for path in self.config["watched_paths"]:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                self.observer.schedule(
                    self.handler, 
                    abs_path, 
                    recursive=True
                )
                logger.info(f"添加监视路径: {abs_path}")
            else:
                logger.warning(f"路径不存在，跳过: {abs_path}")
        
        # 启动观察者
        self.observer.start()
        self.is_running = True
        self.start_time = datetime.now()
        
        # 更新状态
        global _monitor_status
        _monitor_status["running"] = True
        _monitor_status["start_time"] = self.start_time.isoformat()
        
        logger.info(f"文件监视服务已启动，监控 {len(self.config['watched_paths'])} 个路径")
    
    def stop(self):
        """停止监视服务"""
        if not self.is_running:
            logger.warning("监视服务未运行")
            return
        
        self.observer.stop()
        self.observer.join()
        self.is_running = False
        
        # 更新状态
        global _monitor_status
        _monitor_status["running"] = False
        
        logger.info("文件监视服务已停止")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取监视服务状态
        
        Returns:
            服务状态信息
        """
        return {
            "running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "config": self.config,
            "event_stats": _monitor_status["event_stats"],
            "last_event_time": _monitor_status["last_event_time"]
        }


def load_config(config_file: str = "Ref/data/auto_monitor_config.json") -> Dict[str, Any]:
    """
    加载监控配置
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置字典
    """
    config = DEFAULT_CONFIG.copy()
    
    # 如果配置文件存在，加载它
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # 更新默认配置
            config.update(user_config)
            logger.info(f"已加载配置文件: {config_file}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}，将使用默认配置")
    else:
        logger.info(f"配置文件不存在: {config_file}，将使用默认配置")
        
        # 创建默认配置文件
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
            logger.info(f"已创建默认配置文件: {config_file}")
        except Exception as e:
            logger.error(f"创建默认配置文件失败: {str(e)}")
    
    return config


def start_monitor_service(config_file: str = None) -> bool:
    """
    启动监视服务
    
    Args:
        config_file: 配置文件路径，如不指定则使用默认路径
        
    Returns:
        是否成功启动
    """
    global _monitor_service
    
    # 如果服务已经运行，直接返回
    if _monitor_service is not None and _monitor_service.is_running:
        logger.warning("监视服务已经在运行中")
        return True
    
    # 加载配置
    config_path = config_file or "Ref/data/auto_monitor_config.json"
    config = load_config(config_path)
    
    try:
        # 创建并启动服务
        _monitor_service = FileWatcherService(config)
        _monitor_service.start()
        
        logger.info("监视服务已成功启动")
        return True
    except Exception as e:
        logger.error(f"启动监视服务失败: {str(e)}")
        return False


def stop_monitor_service() -> bool:
    """
    停止监视服务
    
    Returns:
        是否成功停止
    """
    global _monitor_service
    
    if _monitor_service is None or not _monitor_service.is_running:
        logger.warning("监视服务未运行")
        return False
    
    try:
        _monitor_service.stop()
        logger.info("监视服务已停止")
        return True
    except Exception as e:
        logger.error(f"停止监视服务失败: {str(e)}")
        return False


def is_monitor_running() -> bool:
    """
    检查监视服务是否正在运行
    
    Returns:
        是否正在运行
    """
    global _monitor_service
    return _monitor_service is not None and _monitor_service.is_running


def get_monitor_status() -> Dict[str, Any]:
    """
    获取监视服务状态
    
    Returns:
        服务状态信息
    """
    global _monitor_service, _monitor_status
    
    if _monitor_service is not None:
        return _monitor_service.get_status()
    
    return _monitor_status


if __name__ == "__main__":
    # 命令行界面
    import argparse
    
    parser = argparse.ArgumentParser(description="Ref自动文件监视服务")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 启动命令
    start_parser = subparsers.add_parser("start", help="启动监视服务")
    start_parser.add_argument(
        "--config", "-c",
        dest="config_file",
        help="配置文件路径"
    )
    
    # 停止命令
    stop_parser = subparsers.add_parser("stop", help="停止监视服务")
    
    # 状态命令
    status_parser = subparsers.add_parser("status", help="查看服务状态")
    
    args = parser.parse_args()
    
    if args.command == "start":
        success = start_monitor_service(args.config_file)
        if success:
            print("监视服务已启动")
            
            # 保持运行，直到用户按Ctrl+C
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n正在停止服务...")
                stop_monitor_service()
                print("服务已停止")
        else:
            print("启动监视服务失败")
            sys.exit(1)
    
    elif args.command == "stop":
        success = stop_monitor_service()
        if success:
            print("监视服务已停止")
        else:
            print("停止监视服务失败")
            sys.exit(1)
    
    elif args.command == "status":
        if is_monitor_running():
            status = get_monitor_status()
            print("监视服务状态:")
            print(f"  运行中: {status['running']}")
            print(f"  启动时间: {status['start_time']}")
            print(f"  监视路径: {', '.join(status['config']['watched_paths'])}")
            print(f"  事件统计:")
            for event_type, count in status['event_stats'].items():
                print(f"    - {event_type}: {count}")
            print(f"  最后事件时间: {status['last_event_time'] or '无'}")
        else:
            print("监视服务未运行")
    
    else:
        parser.print_help() 

"""

"""
量子基因编码: QE-FIL-79A6F2B15757
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
