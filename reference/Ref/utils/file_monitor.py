#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Quantum File Event Monitoring System

This module provides a file monitoring system that detects file movements
and updates the quantum gene markers to maintain entanglement relationships.
"""

import os
import time
import logging
import threading
import sys
import re
import traceback
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileMovedEvent
import json
from threading import Event
from typing import Dict, List, Set, Tuple, Any, Optional, Union, Callable
import shutil

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(current_dir), "logs", "file_monitor.log"), mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QuantumFileMonitor")

# Import quantum gene marker functionality
quantum_gene_marker = None
try:
    from Ref.utils.quantum_gene_marker import RefQuantumGeneMarker
    quantum_gene_marker = RefQuantumGeneMarker()
    logger.info("Successfully imported RefQuantumGeneMarker from Ref.utils")
except ImportError as e:
    logger.warning(f"Could not import from Ref.utils.quantum_gene_marker: {e}")
    # Try direct import
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        sys.path.insert(0, parent_dir)
        from quantum_gene_marker import RefQuantumGeneMarker
        quantum_gene_marker = RefQuantumGeneMarker()
        logger.info("Successfully imported RefQuantumGeneMarker from parent directory")
    except ImportError as e:
        logger.error(f"Could not import RefQuantumGeneMarker: {e}")
        
        # Create a minimal implementation for standalone operation
        class MinimalRefQuantumGeneMarker:
            def __init__(self):
                self.logger = logging.getLogger("MinimalRefQuantumGeneMarker")
                self.logger.warning("Using minimal implementation of RefQuantumGeneMarker")
                
            def get_project_root(self):
                return project_root
                
            def has_quantum_gene_marker(self, file_path):
                return False
                
            def update_file_path(self, file_path, old_path):
                self.logger.info(f"Mock update file path: {old_path} -> {file_path}")
                return True
                
            def has_reference_to_file(self, file_path, ref_path):
                return False
                
            def update_reference_path(self, file_path, old_ref, new_ref):
                self.logger.info(f"Mock update reference in {file_path}: {old_ref} -> {new_ref}")
                return True
        
        quantum_gene_marker = MinimalRefQuantumGeneMarker()
        logger.warning("Using minimal implementation for standalone operation")

# Import supported file types
SUPPORTED_FILE_TYPES = {}
try:
    from Ref.utils.quantum_gene_marker import SUPPORTED_FILE_TYPES
    logger.info(f"Imported SUPPORTED_FILE_TYPES with {len(SUPPORTED_FILE_TYPES)} entries")
except ImportError:
    # Fallback supported file types
    SUPPORTED_FILE_TYPES = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.h': 'C Header',
        '.cs': 'C#',
        '.go': 'Go',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.ts': 'TypeScript',
        '.scala': 'Scala',
        '.rs': 'Rust',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.m': 'Objective-C',
        '.sql': 'SQL',
        '.r': 'R',
        '.sh': 'Shell',
        '.bat': 'Batch',
        '.ps1': 'PowerShell',
        '.html': 'HTML',
        '.css': 'CSS',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yml': 'YAML',
        '.yaml': 'YAML',
        '.ini': 'INI',
        '.toml': 'TOML',
        '.md': 'Markdown',
        '.txt': 'Text',
    }
    logger.warning(f"Using fallback SUPPORTED_FILE_TYPES with {len(SUPPORTED_FILE_TYPES)} entries")

# Create a global instance to be used by all handlers
quantum_gene_marker = RefQuantumGeneMarker()

# 创建全局监控器实例，用于单例模式
_file_monitor_instance = None

class QuantumFileEventHandler(FileSystemEventHandler):
    """
    Handler for file system events that involve quantum entangled objects.
    Focuses primarily on file movement events to update quantum gene markers.
    """
    
    def __init__(self):
        super().__init__()
        self.processing_lock = threading.Lock()
        self.logger = logging.getLogger("QuantumFileEventHandler")
        self.deleted_files = set()  # 用于跟踪已删除的文件
    
    def on_moved(self, event):
        """
        Handle file movement events, updating quantum gene markers accordingly.
        
        Args:
            event (FileMovedEvent): The file movement event
        """
        if not isinstance(event, FileMovedEvent):
            return
        
        # 获取文件扩展名
        from Ref.utils.quantum_gene_marker import SUPPORTED_FILE_TYPES
        
        # 标准化路径以消除不同的路径分隔符表示
        src_path = os.path.normpath(event.src_path)
        dest_path = os.path.normpath(event.dest_path)
        
        # 提取文件扩展名
        _, src_ext = os.path.splitext(src_path)
        _, dest_ext = os.path.splitext(dest_path)
        
        # 检查是否是支持的文件类型
        if src_ext.lower() not in SUPPORTED_FILE_TYPES and dest_ext.lower() not in SUPPORTED_FILE_TYPES:
            return
            
        self.logger.info(f"File moved: {src_path} -> {dest_path}")
        
        # Use a lock to prevent concurrent processing of the same file
        with self.processing_lock:
            try:
                self._process_moved_file(src_path, dest_path)
            except Exception as e:
                self.logger.error(f"Error processing moved file: {str(e)}")
    
    def _process_moved_file(self, src_path, dest_path):
        """
        Process a moved file by updating its quantum gene marker and 
        all references to it in other files.
        
        Args:
            src_path (str): The original file path
            dest_path (str): The new file path
        """
        self.logger.info(f"Processing moved file: {src_path} -> {dest_path}")
        
        # 检查是否应该跳过（如果是点开头的目录）
        def should_skip_path(path):
            parts = os.path.normpath(path).split(os.path.sep)
            for part in parts:
                if part.startswith('.') and part not in ['.', '..']:
                    return True
            return False
        
        # 如果源路径或目标路径在忽略的目录中，则跳过处理
        if should_skip_path(src_path) or should_skip_path(dest_path):
            self.logger.info(f"Skipping file in dot directory: {src_path} -> {dest_path}")
            return
        
        # 通知量子基因标记监控系统文件移动
        self.notify_marker_monitor(dest_path, 'move', src_path)
        
        # 1. Update the moved file's quantum gene marker
        try:
            # First check if the file had quantum gene markers
            if quantum_gene_marker.has_quantum_gene_marker(dest_path):
                quantum_gene_marker.update_file_path(dest_path, src_path)
                self.logger.info(f"Updated quantum gene marker in moved file: {dest_path}")
        except Exception as e:
            self.logger.error(f"Error updating quantum gene marker in moved file: {str(e)}")
        
        # 2. Update all files that reference the moved file
        try:
            # Normalize paths for comparison
            norm_src_path = os.path.normpath(src_path)
            norm_dest_path = os.path.normpath(dest_path)
            
            # Get project root from quantum gene marker
            try:
                project_root = quantum_gene_marker.get_project_root()
            except Exception as e:
                self.logger.warning(f"Failed to get project_root from quantum_gene_marker: {str(e)}")
                # Fallback to the current directory's parent
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
                self.logger.info(f"Using fallback project_root: {project_root}")
            
            self.logger.info(f"Searching for references to {norm_src_path} in {project_root}")
            
            # 获取支持的文件扩展名
            from Ref.utils.quantum_gene_marker import SUPPORTED_FILE_TYPES
            
            # Find all supported files in the project
            for root, dirs, files in os.walk(project_root):
                # 跳过以点开头的目录
                dirs[:] = [d for d in dirs if not (d.startswith('.') and d not in ['.', '..'])]
                
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in SUPPORTED_FILE_TYPES:
                    file_path = os.path.join(root, file)
                    norm_file_path = os.path.normpath(file_path)
                    
                    # Skip the moved file itself
                    if norm_file_path == norm_dest_path:
                        continue
                    
                    # Check if this file references the moved file
                    try:
                        # 使用两种方式检查引用
                        # 1. 直接使用路径字符串比较
                        if quantum_gene_marker.has_reference_to_file(file_path, norm_src_path):
                            # Update the reference
                            self.logger.info(f"Found reference to {norm_src_path} in {file_path}")
                            result = quantum_gene_marker.update_reference_path(file_path, norm_src_path, dest_path)
                            if result:
                                self.logger.info(f"Updated reference in file: {file_path}")
                            else:
                                self.logger.warning(f"Failed to update reference in file: {file_path}")
                        
                        # 2. 检查不同格式的路径表示
                        # 尝试将反斜杠转换为正斜杠
                        alt_src_path = norm_src_path.replace('\\', '/')
                        if alt_src_path != norm_src_path and quantum_gene_marker.has_reference_to_file(file_path, alt_src_path):
                            self.logger.info(f"Found reference with alternative path format to {alt_src_path} in {file_path}")
                            alt_dest_path = norm_dest_path.replace('\\', '/')
                            result = quantum_gene_marker.update_reference_path(file_path, alt_src_path, alt_dest_path)
                            if result:
                                self.logger.info(f"Updated alternative path reference in file: {file_path}")
                            else:
                                self.logger.warning(f"Failed to update alternative path reference in file: {file_path}")
                                
                    except Exception as e:
                        self.logger.error(f"Error checking/updating reference in {file_path}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error updating references to moved file: {str(e)}")

    def notify_marker_monitor(self, file_path: str, change_type: str, old_path: str = None):
        """
        通知量子基因标记监控系统文件变化
        
        Args:
            file_path: 变化的文件路径
            change_type: 变化类型，可选值：'add', 'update', 'move', 'delete'
            old_path: 如果是移动操作，原始路径
        """
        try:
            # 使用线程本地变量防止递归
            thread_id = threading.get_ident()
            if not hasattr(self, '_notifying_threads'):
                self._notifying_threads = set()
                
            # 如果当前线程已在通知中，跳过
            if thread_id in self._notifying_threads:
                logger.info(f"跳过重复通知（事件处理器）: {change_type} {file_path}")
                return True
                
            # 标记当前线程
            self._notifying_threads.add(thread_id)
            
            try:
                # 简化实现，仅记录日志
                logger.info(f"通知量子基因标记系统: {change_type} {file_path}")
                
                # 导入量子基因标记系统的通知函数
                from Ref.utils.quantum_gene_marker import notify_monitoring_systems
                notify_monitoring_systems(file_path, change_type, old_path)
                
                return True
            finally:
                # 通知完成后移除线程标记
                self._notifying_threads.remove(thread_id)
        except Exception as e:
            logger.error(f"通知量子基因标记监控系统时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return False

    def _suggest_entangled_objects(self, file_path: str, default_entangled_objects: List[str] = None) -> List[str]:
        """
        为文件推断潜在的纠缠对象
        
        Args:
            file_path: 文件路径
            default_entangled_objects: 默认的纠缠对象列表
            
        Returns:
            List[str]: 推断的纠缠对象列表
        """
        if default_entangled_objects is None:
            default_entangled_objects = []
            
        # 简化实现，直接返回默认列表
        return list(default_entangled_objects)

class QuantumFileMonitor:
    """
    Monitor for file system events related to quantum entangled objects.
    Watches project directories for file movements and updates markers accordingly.
    """
    
    def __init__(self):
        """简化版初始化"""
        self.logger = logging.getLogger("QuantumFileMonitor")
        self.event_handler = QuantumFileEventHandler()
        self.running = False
        self.paths_to_watch = ["."]
        logger.info(f"Initialized QuantumFileMonitor with paths: {self.paths_to_watch}")
    
    def start(self):
        """启动监控"""
        self.running = True
        logger.info("Quantum file monitoring started")
        return True
    
    def stop(self):
        """停止监控"""
        self.running = False
        logger.info("Quantum file monitoring stopped")
        return True
        
    def monitor_weq_directories(self, weq_output_dirs=None):
        """添加WeQ输出目录到监控"""
        logger.info(f"添加WeQ输出目录到监控: {weq_output_dirs}")
        return True
        
    def add_quantum_gene_marker(self, file_path: str, entangled_objects: List[str] = None, 
                               strength: float = 0.95, notify_others: bool = True) -> bool:
        """
        独立的标记添加功能 - 允许文件监控系统直接添加量子基因标记
        
        Args:
            file_path: 文件路径
            entangled_objects: 纠缠对象列表
            strength: 纠缠强度
            notify_others: 是否通知其他系统
            
        Returns:
            bool: 是否成功添加标记
        """
        try:
            # 先检查文件是否已有标记
            has_marker = False
            
            try:
                # 尝试读取文件内容检查是否有标记
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    # 简单检查是否包含标记关键字
                    has_marker = "量子基因编码" in content or "quantum_gene" in content or "纠缠对象" in content
            except Exception as e:
                self.logger.warning(f"检查文件标记时出错: {str(e)}")
                
            if has_marker:
                self.logger.info(f"文件已有量子基因标记: {file_path}")
                return True
                
            # 如果没有标记，添加标记
            # 生成唯一的量子基因编码
            import uuid
            import time
            import hashlib
            
            # 使用文件路径和时间生成唯一ID
            file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
            time_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:4]
            unique_id = f"QE-{file_hash}-{time_hash}"
            
            # 确定文件类型和注释标记
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            # 不同文件类型的注释格式
            comment_map = {
                '.py': ('#', '', ''),
                '.js': ('//', '', ''),
                '.ts': ('//', '', ''),
                '.java': ('//', '', ''),
                '.c': ('//', '', ''),
                '.cpp': ('//', '', ''),
                '.h': ('//', '', ''),
                '.cs': ('//', '', ''),
                '.go': ('//', '', ''),
                '.rs': ('//', '', ''),
                '.rb': ('#', '', ''),
                '.php': ('//', '', ''),
                '.html': ('<!--', '-->', ''),
                '.xml': ('<!--', '-->', ''),
                '.md': ('', '', ''),
                '.txt': ('', '', ''),
                '.json': ('// ', '', ''),
                '.yml': ('# ', '', ''),
                '.yaml': ('# ', '', '')
            }
            
            # 默认使用Python风格注释
            start_comment, end_comment, line_prefix = comment_map.get(ext, ('#', '', ''))
            
            # 格式化纠缠对象列表
            entangled_str = str(entangled_objects) if entangled_objects else "[]"
            
            # 创建量子基因标记内容
            if start_comment and end_comment:  # HTML/XML风格注释
                marker_content = f"""
{start_comment}
量子基因编码: {unique_id}
纠缠状态: 活跃
纠缠对象: {entangled_str}
纠缠强度: {strength}
{end_comment}
"""
            else:  # 单行注释风格
                marker_content = f"""
{start_comment} 量子基因编码: {unique_id}
{start_comment} 纠缠状态: 活跃
{start_comment} 纠缠对象: {entangled_str}
{start_comment} 纠缠强度: {strength}
"""
            
            # 读取原始文件内容
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception as e:
                self.logger.error(f"读取文件时出错: {file_path} - {str(e)}")
                return False
                
            # 添加标记到文件
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # 如果是Python文件，在导入语句后添加标记
                    if ext == '.py' and 'import ' in content:
                        # 找到最后一个导入语句的位置
                        import_lines = [i for i, line in enumerate(content.split('\n')) 
                                       if line.strip().startswith('import ') or line.strip().startswith('from ')]
                        
                        if import_lines:
                            last_import = max(import_lines)
                            lines = content.split('\n')
                            new_content = '\n'.join(lines[:last_import+1]) + '\n\n' + marker_content + '\n' + '\n'.join(lines[last_import+1:])
                            f.write(new_content)
                        else:
                            f.write(marker_content + '\n\n' + content)
                    else:
                        # 对于其他文件类型，在文件开头添加标记
                        f.write(marker_content + '\n\n' + content)
                
                self.logger.info(f"文件监控系统成功添加量子基因标记: {file_path}")
                
                # 通知其他系统
                if notify_others:
                    self.event_handler.notify_marker_monitor(file_path, 'update')
                
                return True
            except Exception as e:
                self.logger.error(f"写入量子基因标记时出错: {file_path} - {str(e)}")
                return False
        except Exception as e:
            self.logger.error(f"添加量子基因标记时出错: {file_path} - {str(e)}")
            return False
    
    def update_quantum_gene_marker(self, file_path: str, entangled_objects: List[str] = None, 
                                 strength: float = None, notify_others: bool = True) -> bool:
        """
        更新文件的量子基因标记
        
        Args:
            file_path: 文件路径
            entangled_objects: 新的纠缠对象列表
            strength: 新的纠缠强度
            notify_others: 是否通知其他系统
            
        Returns:
            bool: 是否成功更新标记
        """
        try:
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception as e:
                self.logger.error(f"读取文件时出错: {file_path} - {str(e)}")
                return False
                
            # 检查是否有量子基因标记
            if "量子基因编码" not in content and "quantum_gene" not in content:
                # 如果没有标记，添加新标记
                return self.add_quantum_gene_marker(file_path, entangled_objects, 
                                                 strength or 0.95, notify_others)
            
            # 解析现有的纠缠对象
            import re
            entangled_match = re.search(r'纠缠对象:\s*(\[.*?\])', content, re.DOTALL)
            
            if not entangled_match:
                # 如果找不到纠缠对象，但有基因编码，重新添加标记
                return self.add_quantum_gene_marker(file_path, entangled_objects, 
                                                 strength or 0.95, notify_others)
            
            # 获取现有纠缠对象列表
            try:
                current_entangled_str = entangled_match.group(1)
                # 将字符串转换为Python列表（简化实现）
                current_entangled = eval(current_entangled_str)
            except Exception:
                current_entangled = []
            
            # 合并纠缠对象
            if entangled_objects:
                merged_entangled = list(set(current_entangled + entangled_objects))
            else:
                merged_entangled = current_entangled
                
            # 更新纠缠对象
            new_entangled_str = str(merged_entangled)
            new_content = re.sub(r'纠缠对象:\s*(\[.*?\])', f'纠缠对象: {new_entangled_str}', content, flags=re.DOTALL)
            
            # 如果需要更新纠缠强度
            if strength is not None:
                new_content = re.sub(r'纠缠强度:\s*[\d\.]+', f'纠缠强度: {strength}', new_content)
            
            # 写回文件
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.logger.info(f"文件监控系统成功更新量子基因标记: {file_path}")
                
                # 通知其他系统
                if notify_others:
                    self.event_handler.notify_marker_monitor(file_path, 'update')
                
                return True
            except Exception as e:
                self.logger.error(f"写入更新的量子基因标记时出错: {file_path} - {str(e)}")
                return False
        except Exception as e:
            self.logger.error(f"更新量子基因标记时出错: {file_path} - {str(e)}")
            return False

def get_file_monitor():
    """获取文件监控器的全局实例"""
    global _file_monitor_instance
    if _file_monitor_instance is None:
        _file_monitor_instance = QuantumFileMonitor()
    return _file_monitor_instance

def notify_marker_monitor(file_path: str, change_type: str, old_path: str = None) -> bool:
    """
    通知量子基因标记系统文件变更（全局函数）
    
    Args:
        file_path: 文件路径
        change_type: 变更类型 ('add', 'update', 'move', 'delete')
        old_path: 如果是移动操作，原始路径
        
    Returns:
        bool: 是否成功通知
    """
    try:
        # 使用线程本地存储防止递归
        thread_id = threading.get_ident()
        global _notification_thread_ids
        if not '_notification_thread_ids' in globals():
            _notification_thread_ids = set()
            
        # 如果当前线程已在通知中，跳过
        if thread_id in _notification_thread_ids:
            logging.info(f"跳过重复通知（文件监控系统）: {change_type} {file_path}")
            return True
            
        # 标记当前线程
        _notification_thread_ids.add(thread_id)
        
        try:
            monitor = get_file_monitor()
            if not monitor:
                return False
                
            if hasattr(monitor, 'event_handler') and hasattr(monitor.event_handler, 'notify_marker_monitor'):
                return monitor.event_handler.notify_marker_monitor(file_path, change_type, old_path)
            return False
        finally:
            # 通知完成后移除标记
            _notification_thread_ids.remove(thread_id)
    except Exception as e:
        logging.error(f"通知量子基因标记系统失败: {str(e)}")
        return False

def add_quantum_gene_marker_by_monitor(file_path: str, entangled_objects: List[str] = None, 
                                  strength: float = 0.95) -> bool:
    """
    使用文件监控系统为文件添加量子基因标记（全局函数）
    
    Args:
        file_path: 文件路径
        entangled_objects: 纠缠对象列表
        strength: 纠缠强度
        
    Returns:
        bool: 是否成功添加标记
    """
    try:
        monitor = get_file_monitor()
        if not monitor:
            logger.error("无法获取文件监控器实例")
            return False
            
        return monitor.add_quantum_gene_marker(file_path, entangled_objects, strength)
    except Exception as e:
        logger.error(f"添加量子基因标记时出错: {str(e)}")
        return False
        
def update_quantum_gene_marker_by_monitor(file_path: str, entangled_objects: List[str] = None,
                                         strength: float = None) -> bool:
    """
    使用文件监控系统更新文件的量子基因标记（全局函数）
    
    Args:
        file_path: 文件路径
        entangled_objects: 新的纠缠对象列表
        strength: 新的纠缠强度
        
    Returns:
        bool: 是否成功更新标记
    """
    try:
        monitor = get_file_monitor()
        if not monitor:
            logger.error("无法获取文件监控器实例")
            return False
            
        return monitor.update_quantum_gene_marker(file_path, entangled_objects, strength)
    except Exception as e:
        logger.error(f"更新量子基因标记时出错: {str(e)}")
        return False

def main():
    """
    Main function for the quantum file monitor.
    """
    parser = argparse.ArgumentParser(description='Quantum File Monitor')
    parser.add_argument('--standalone', action='store_true', help='Run as a standalone process')
    parser.add_argument('--test', action='store_true', help='Run a test')
    parser.add_argument('--test-movement', action='store_true', help='Run file movement test')
    parser.add_argument('--test-reverse', action='store_true', help='Run reverse file movement test')
    parser.add_argument('--monitor-weq', action='store_true', help='Monitor WeQ output directories')
    parser.add_argument('--weq-dirs', nargs='+', help='Specific WeQ output directories to monitor')
    parser.add_argument('--scan-existing', action='store_true', help='Scan existing files and add markers')
    args = parser.parse_args()
    
    # 配置日志
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'file_monitor.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger("QuantumFileMonitor")
    
    if args.test:
        logger.info("Running test mode...")
        # Basic test to ensure the monitor can start and stop
        try:
            monitor = get_file_monitor()
            monitor.start()
            logger.info("Started monitor for test...")
            time.sleep(2)
            monitor.stop()
            logger.info("Test completed successfully!")
            return 0
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            return 1
    
    if args.test_movement:
        logger.info("Running file movement test...")
        monitor = get_file_monitor()
        monitor.start()
        result = monitor.test_file_movement_monitoring()
        if result:
            logger.info("文件移动测试成功!")
        else:
            logger.warning("文件移动测试失败")
        monitor.stop()
        return 0 if result else 1
    
    if args.test_reverse:
        logger.info("Running reverse file movement test...")
        monitor = get_file_monitor()
        monitor.start()
        result = monitor.test_file_movement_monitoring_reverse()
        if result:
            logger.info("反向文件移动测试成功!")
        else:
            logger.warning("反向文件移动测试失败")
        monitor.stop()
        return 0 if result else 1
    
    # 获取监控器实例
    monitor = get_file_monitor()
    
    # 启动监控
    monitor.start()
    
    # 根据参数执行相应操作
    if args.scan_existing:
        logger.info("扫描现有文件并添加标记...")
        # 对所有已知文件执行标记检查
        monitor._check_and_add_markers()
        
    if args.monitor_weq:
        logger.info("开始监控WeQ输出目录...")
        # 使用指定的WeQ目录或默认目录
        weq_dirs = args.weq_dirs if args.weq_dirs else None
        monitor.monitor_weq_directories(weq_dirs)
    
    if args.standalone or args.monitor_weq or args.scan_existing:
        logger.info("Running in standalone mode...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping monitor...")
        finally:
            monitor.stop()
            logger.info("Monitor stopped")
        
        return 0
    
    # No arguments, print help
    parser.print_help()
    return 0

# 如果作为主程序执行
if __name__ == "__main__":
    import argparse
    exit(main())

# 量子基因标记
# <QEntL:quantum_gene:af47d9c6a2e0437b8b7a19b38e5d117c:v1.0>
# </QEntL:quantum_gene>

# 量子纠缠状态
# <QEntL:entangled>
# paths: []
# related_files: []
# </QEntL:entangled>

# 量子基因编码: QE-FIL-F234C42D3A91
# 纠缠状态: 活跃
# 纠缠对象: ['Ref/ref_core.py']
# 纠缠强度: 0.98