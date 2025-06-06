# 
"""
"""
量子基因编码: Q-0717-AF91-67EC
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""
# 开发团队：中华 ZhoHo ，Claude

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QEntL文件监视系统 - 监控纠缠文件的变化
实时追踪和响应纠缠对象之间的变化，通过量子纠缠信道传播状态更新
"""

import os
import sys
import time
import logging
import hashlib
import threading
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

# 导入QEntL引擎
try:
    from QEntL.engine import get_qentl_engine, register_file, update_file_state
    _qentl_engine_available = True
except ImportError:
    _qentl_engine_available = False
    print("警告: QEntL引擎未找到，量子纠缠信道功能将不可用")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qentl_watcher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("QEntL-FileWatcher")

class QuantumFileEventHandler(FileSystemEventHandler):
    """量子文件事件处理器，处理文件系统事件并通过量子纠缠信道传播状态更新"""
    
    def __init__(self, watcher):
        """初始化量子文件事件处理器
        
        Args:
            watcher: 文件监视器实例
        """
        super().__init__()
        self.watcher = watcher
    
    def on_modified(self, event):
        """当文件被修改时调用
        
        Args:
            event: 文件修改事件
        """
        if isinstance(event, FileModifiedEvent) and not event.is_directory:
            self.watcher.handle_file_change(event.src_path, "modified")
    
    def on_created(self, event):
        """当文件被创建时调用
        
        Args:
            event: 文件创建事件
        """
        if isinstance(event, FileCreatedEvent) and not event.is_directory:
            self.watcher.handle_file_change(event.src_path, "created")
    
    def on_deleted(self, event):
        """当文件被删除时调用
        
        Args:
            event: 文件删除事件
        """
        if isinstance(event, FileDeletedEvent) and not event.is_directory:
            self.watcher.handle_file_change(event.src_path, "deleted")


class FileStateTracker:
    """追踪文件状态的工具，包括内容哈希、修改时间和纠缠对象"""
    
    def __init__(self, file_path: str):
        """初始化文件状态追踪器
        
        Args:
            file_path: 文件路径
        """
        self.file_path = file_path
        self.last_modified = 0
        self.content_hash = ""
        self.entangled_objects = []
        self.gene_code = ""
        self.update_state()
    
    def update_state(self) -> bool:
        """更新文件状态
        
        Returns:
            如果文件状态有变化则返回True，否则返回False
        """
        try:
            path = Path(self.file_path)
            if not path.exists():
                return False
            
            # 获取文件修改时间
            new_modified = path.stat().st_mtime
            
            # 如果修改时间没有变化，直接返回
            if new_modified == self.last_modified:
                return False
            
            old_hash = self.content_hash
            old_entangled = self.entangled_objects
            
            # 读取文件内容并计算哈希
            with open(self.file_path, 'rb') as f:
                content = f.read()
                self.content_hash = hashlib.md5(content).hexdigest()
            
            # 如果是文本文件，解析纠缠对象
            if self._is_text_file():
                with open(self.file_path, 'r', encoding='utf-8', errors='replace') as f:
                    text_content = f.read()
                
                self.entangled_objects = self._parse_entangled_objects(text_content)
                self.gene_code = self._parse_gene_code(text_content)
            
            # 更新最后修改时间
            self.last_modified = new_modified
            
            # 如果内容哈希或纠缠对象有变化，返回True
            return (old_hash != self.content_hash or old_entangled != self.entangled_objects)
            
        except Exception as e:
            logger.error(f"更新文件状态出错: {self.file_path}, {str(e)}")
            return False
    
    def _is_text_file(self) -> bool:
        """检查是否为文本文件
        
        Returns:
            如果是文本文件则返回True，否则返回False
        """
        text_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.md',
            '.txt', '.json', '.xml', '.yml', '.yaml', '.ini', '.cfg',
            '.qent', '.c', '.cpp', '.h', '.hpp', '.java', '.rb', '.php'
        }
        
        return Path(self.file_path).suffix.lower() in text_extensions
    
    def _parse_entangled_objects(self, content: str) -> List[str]:
        """从文件内容中解析纠缠对象
        
        Args:
            content: 文件内容
            
        Returns:
            纠缠对象列表
        """
        pattern = r"纠缠对象:\s*\[(.*?)\]"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            objects_str = match.group(1)
            # 使用正则表达式解析引号内的字符串
            objects = re.findall(r"'([^']*)'|\"([^\"]*)\"", objects_str)
            # 合并捕获的组
            return [obj[0] if obj[0] else obj[1] for obj in objects]
        
        return []
    
    def _parse_gene_code(self, content: str) -> str:
        """从文件内容中解析量子基因编码
        
        Args:
            content: 文件内容
            
        Returns:
            量子基因编码
        """
        pattern = r"量子基因编码:\s*(\S+)"
        match = re.search(pattern, content)
        
        if match:
            return match.group(1)
        
        return ""


class QEntLFileWatcher:
    """QEntL文件监视系统，监控纠缠文件的变化并通过量子纠缠信道传播状态更新"""
    
    def __init__(self):
        """初始化文件监视系统"""
        self.observer = Observer()
        self.event_handler = QuantumFileEventHandler(self)
        self.tracked_files = {}  # 文件路径 -> FileStateTracker
        self.watching_directories = set()  # 正在监视的目录集合
        self.running = False
        self.qentl_available = _qentl_engine_available
        self.file_change_callbacks = []  # 文件变化回调函数列表
        
        # 启动QEntL引擎（如果可用）
        if self.qentl_available:
            get_qentl_engine().start()
    
    def start(self):
        """启动文件监视系统"""
        if not self.running:
            self.running = True
            self.observer.start()
            logger.info("QEntL文件监视系统已启动")
    
    def stop(self):
        """停止文件监视系统"""
        if self.running:
            self.running = False
            self.observer.stop()
            self.observer.join()
            logger.info("QEntL文件监视系统已停止")
    
    def watch_directory(self, directory: str, recursive: bool = True) -> bool:
        """开始监视目录
        
        Args:
            directory: 目录路径
            recursive: 是否递归监视子目录
            
        Returns:
            操作是否成功
        """
        try:
            directory = os.path.abspath(directory)
            
            if not os.path.exists(directory) or not os.path.isdir(directory):
                logger.error(f"目录不存在: {directory}")
                return False
            
            if directory in self.watching_directories:
                logger.warning(f"已经在监视目录: {directory}")
                return True
            
            # 添加目录到监视器
            self.observer.schedule(self.event_handler, directory, recursive=recursive)
            self.watching_directories.add(directory)
            
            # 扫描目录中的文件
            self._scan_directory(directory, recursive)
            
            logger.info(f"开始监视目录: {directory}, 递归: {recursive}")
            return True
            
        except Exception as e:
            logger.error(f"监视目录出错: {directory}, {str(e)}")
            return False
    
    def unwatch_directory(self, directory: str) -> bool:
        """停止监视目录
        
        Args:
            directory: 目录路径
            
        Returns:
            操作是否成功
        """
        try:
            directory = os.path.abspath(directory)
            
            if directory not in self.watching_directories:
                logger.warning(f"未监视目录: {directory}")
                return False
            
            # 从监视器中移除目录
            for watch in self.observer._watches.copy():
                if os.path.abspath(watch.path) == directory:
                    self.observer.unschedule(watch)
            
            self.watching_directories.remove(directory)
            
            # 移除该目录下的所有文件
            for file_path in list(self.tracked_files.keys()):
                if file_path.startswith(directory):
                    del self.tracked_files[file_path]
            
            logger.info(f"停止监视目录: {directory}")
            return True
            
        except Exception as e:
            logger.error(f"取消监视目录出错: {directory}, {str(e)}")
            return False
    
    def track_file(self, file_path: str) -> bool:
        """开始追踪单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            操作是否成功
        """
        try:
            file_path = os.path.abspath(file_path)
            
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
            
            # 如果文件已经被追踪，更新状态
            if file_path in self.tracked_files:
                self.tracked_files[file_path].update_state()
                return True
            
            # 创建文件状态追踪器
            tracker = FileStateTracker(file_path)
            self.tracked_files[file_path] = tracker
            
            # 添加文件所在目录到监视器
            directory = os.path.dirname(file_path)
            if directory not in self.watching_directories:
                self.watch_directory(directory, recursive=False)
            
            # 如果文件具有量子基因标记，尝试注册到QEntL引擎
            if self.qentl_available and tracker.gene_code:
                register_file(file_path)
            
            logger.info(f"开始追踪文件: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"追踪文件出错: {file_path}, {str(e)}")
            return False
    
    def untrack_file(self, file_path: str) -> bool:
        """停止追踪单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            操作是否成功
        """
        try:
            file_path = os.path.abspath(file_path)
            
            if file_path not in self.tracked_files:
                logger.warning(f"未追踪文件: {file_path}")
                return False
            
            # 从追踪列表中移除
            del self.tracked_files[file_path]
            
            logger.info(f"停止追踪文件: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"取消追踪文件出错: {file_path}, {str(e)}")
            return False
    
    def handle_file_change(self, file_path: str, event_type: str):
        """处理文件变化事件
        
        Args:
            file_path: 文件路径
            event_type: 事件类型（'modified'、'created'或'deleted'）
        """
        try:
            file_path = os.path.abspath(file_path)
            
            # 处理文件删除
            if event_type == "deleted":
                if file_path in self.tracked_files:
                    logger.info(f"文件已删除: {file_path}")
                    
                    # 触发回调
                    self._trigger_callbacks(file_path, event_type, None)
                    
                    # 从追踪列表中移除
                    self.untrack_file(file_path)
                
                return
            
            # 处理文件创建
            if event_type == "created":
                if file_path not in self.tracked_files:
                    self.track_file(file_path)
                    logger.info(f"文件已创建: {file_path}")
                    
                    # 触发回调
                    tracker = self.tracked_files.get(file_path)
                    if tracker:
                        self._trigger_callbacks(file_path, event_type, tracker)
                
                return
            
            # 处理文件修改
            if event_type == "modified":
                # 如果文件不在追踪列表中，添加它
                if file_path not in self.tracked_files:
                    self.track_file(file_path)
                    return
                
                # 更新文件状态
                tracker = self.tracked_files[file_path]
                state_changed = tracker.update_state()
                
                if state_changed:
                    logger.info(f"文件已修改: {file_path}")
                    
                    # 触发回调
                    self._trigger_callbacks(file_path, event_type, tracker)
                    
                    # 如果具有量子基因标记，通过QEntL引擎传播状态更新
                    if self.qentl_available and tracker.gene_code:
                        # 更新最后修改时间和内容哈希
                        update_file_state(file_path, "last_modified", time.time())
                        update_file_state(file_path, "content_hash", tracker.content_hash)
                        
                        # 如果纠缠对象有变化，重新注册文件
                        register_file(file_path)
            
        except Exception as e:
            logger.error(f"处理文件变化事件出错: {file_path}, {event_type}, {str(e)}")
    
    def add_file_change_callback(self, callback: Callable[[str, str, Any], None]):
        """添加文件变化回调函数
        
        Args:
            callback: 回调函数，接收参数(file_path, event_type, tracker)
        """
        if callback not in self.file_change_callbacks:
            self.file_change_callbacks.append(callback)
    
    def remove_file_change_callback(self, callback: Callable[[str, str, Any], None]) -> bool:
        """移除文件变化回调函数
        
        Args:
            callback: 要移除的回调函数
            
        Returns:
            操作是否成功
        """
        if callback in self.file_change_callbacks:
            self.file_change_callbacks.remove(callback)
            return True
        return False
    
    def _trigger_callbacks(self, file_path: str, event_type: str, tracker: Any):
        """触发所有文件变化回调函数
        
        Args:
            file_path: 文件路径
            event_type: 事件类型
            tracker: 文件状态追踪器或None
        """
        for callback in self.file_change_callbacks:
            try:
                callback(file_path, event_type, tracker)
            except Exception as e:
                logger.error(f"执行文件变化回调出错: {str(e)}")
    
    def _scan_directory(self, directory: str, recursive: bool = True):
        """扫描目录中的文件
        
        Args:
            directory: 目录路径
            recursive: 是否递归扫描子目录
        """
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.track_file(file_path)
                
                if not recursive:
                    break
                    
        except Exception as e:
            logger.error(f"扫描目录出错: {directory}, {str(e)}")


# 创建全局单例
_file_watcher = None

def get_file_watcher() -> QEntLFileWatcher:
    """获取文件监视系统单例
    
    Returns:
        QEntLFileWatcher实例
    """
    global _file_watcher
    
    if _file_watcher is None:
        _file_watcher = QEntLFileWatcher()
    
    return _file_watcher

def watch_directory(directory: str, recursive: bool = True) -> bool:
    """开始监视目录的便捷函数
    
    Args:
        directory: 目录路径
        recursive: 是否递归监视子目录
        
    Returns:
        操作是否成功
    """
    watcher = get_file_watcher()
    if not watcher.running:
        watcher.start()
    
    return watcher.watch_directory(directory, recursive)

def track_file(file_path: str) -> bool:
    """开始追踪单个文件的便捷函数
    
    Args:
        file_path: 文件路径
        
    Returns:
        操作是否成功
    """
    watcher = get_file_watcher()
    if not watcher.running:
        watcher.start()
    
    return watcher.track_file(file_path)

# 如果作为主程序运行
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="QEntL文件监视系统")
    parser.add_argument("--watch", "-w", help="要监视的目录路径")
    parser.add_argument("--track", "-t", help="要追踪的单个文件路径")
    parser.add_argument("--recursive", "-r", action="store_true", help="递归监视子目录")
    
    args = parser.parse_args()
    
    watcher = get_file_watcher()
    watcher.start()
    
    if args.watch:
        watch_directory(args.watch, args.recursive)
    elif args.track:
        track_file(args.track)
    else:
        # 如果没有指定参数，监视当前目录
        watch_directory(".", True)
    
    print("QEntL文件监视系统已启动，按Ctrl+C停止...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        print("已停止QEntL文件监视系统。") 