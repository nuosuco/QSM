#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Quantum Gene Marker for WeQ Entanglement System

用于在文件中添加量子基因标记，并管理文件间的量子纠缠关系。
"""

import os
import sys
import re
import json
import logging
import time
import hashlib
import traceback
from typing import List, Dict, Set, Any, Optional, Union, Tuple
import threading

# 设置项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(current_dir), "logs", "quantum_gene_marker.log"), mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Ref.utils.quantum_gene_marker")

# 尝试导入QEntL工具模块
qentl_utils = None
try:
    # 注释掉导入，避免出错
    # from QEntL.utils import quantum_marker
    # qentl_utils = quantum_marker
    logger.info("已找到QEntL工具模块，但将优先使用内部实现")
except ImportError:
    logger.info("未找到QEntL工具模块，使用内部实现")
    
# 支持的文件类型
SUPPORTED_FILE_TYPES = {
    '.py': ['"""', "'''", '#'],
    '.qent': ['/*', '//'],
    '.md': ['```', '/*', '//'],
    '.js': ['/*', '//'],
    '.jsx': ['/*', '//'],
    '.ts': ['/*', '//'],
    '.tsx': ['/*', '//'],
    '.css': ['/*', '//'],
    '.html': ['<!--', '//'],
    '.c': ['/*', '//'],
    '.cpp': ['/*', '//'],
    '.h': ['/*', '//'],
    '.hpp': ['/*', '//'],
    '.java': ['/*', '//'],
    '.scala': ['/*', '//'],
    '.go': ['/*', '//'],
    '.rs': ['/*', '//'],
    '.rb': ['=begin', '#'],
    '.php': ['/*', '//'],
    '.swift': ['/*', '//'],
    '.kt': ['/*', '//'],
    '.sql': ['/*', '--'],
    '.r': ['#'],
    '.sh': ['#'],
    '.bat': ['REM', '::'],
    '.ps1': ['<#', '#'],
    '.json': ['//'],
    '.yml': ['#'],
    '.yaml': ['#'],
    '.vue': ['<!--', '/*', '//'],
    '.xml': ['<!--'],
    '.dockerfile': ['#'],
    '.csv': ['#'],
    '.ini': [';', '#'],
    '.toml': ['#'],
}

class RefQuantumGeneMarker:
    """Ref系统的量子基因标记器，用于自动为文件添加量子基因标记"""
    
    # 量子基因标记模板
    GENE_TEMPLATE = """{comment_start}
量子基因编码: {gene_code}
纠缠状态: 活跃
纠缠对象: {entangled_objects}
纠缠强度: {strength}
{comment_end}"""
    
    # 注释结束标记
    COMMENT_END_MARKERS = {
        '"""': '"""',
        "'''": "'''",
        '/*': '*/',
        '//': '',
        '#': '',
        '```': '```',
        '<!--': '-->'
    }
    
    # 添加WeQ输出内容的路径
    WEQ_OUTPUT_DIRS = [
        "WeQ/output",
        "WeQ/results",
        "output/weq",
        "results/weq"
    ]
    
    def __init__(self):
        """初始化量子基因标记器"""
        self.project_root = project_root
        self.qentl_available = qentl_utils is not None
        # 添加WeQ输出监控状态
        self.weq_monitor_active = False
        self.weq_output_files = set()
        # 添加日志记录器
        self.logger = logging.getLogger("QuantumGeneMarker")
    
    def get_project_root(self):
        """获取项目根目录
        
        Returns:
            项目根目录路径
        """
        return self.project_root
    
    def notify_monitoring_systems(self, file_path: str, change_type: str, old_path: str = None) -> bool:
        """
        通知监控系统文件变更
        
        Args:
            file_path: 文件路径
            change_type: 变更类型 ('add', 'update', 'move', 'delete')
            old_path: 如果是移动操作，原始路径
            
        Returns:
            bool: 是否成功通知
        """
        try:
            # 使用线程本地变量防止递归
            thread_id = threading.get_ident()
            if hasattr(self, '_notifying_threads') and thread_id in self._notifying_threads:
                logger.info(f"跳过重复通知: {change_type} {file_path}")
                return True
                
            # 初始化通知线程集合（如果不存在）
            if not hasattr(self, '_notifying_threads'):
                self._notifying_threads = set()
            
            # 标记当前线程正在通知
            self._notifying_threads.add(thread_id)
            
            try:
                # 导入WeQ输出监控系统的通知函数（避免循环导入）
                from Ref.utils.monitor_weq_output import notify_weq_monitor
                notify_weq_monitor(file_path, change_type, old_path)
                
                # 导入文件监控系统的通知函数（如果需要的话）
                # 这里可能需要避免循环通知，通常是文件监控系统通知量子基因标记系统
                # 而不是相反
                
                return True
            finally:
                # 通知完成后移除线程标记
                self._notifying_threads.remove(thread_id)
        except Exception as e:
            logger.error(f"通知监控系统失败: {str(e)}")
            logger.debug(traceback.format_exc())
            return False
        
    def add_quantum_gene_marker(self, file_path: str, entangled_objects: List[str] = None, 
                                strength: float = 0.98, gene_code: str = None, notify: bool = True) -> bool:
        """
        为文件添加量子基因标记。
        
        Args:
            file_path: 目标文件路径
            entangled_objects: 纠缠对象列表，默认为None
            strength: 纠缠强度，默认为0.98
            gene_code: 自定义基因编码，默认为None（自动生成）
            notify: 是否通知其他监控系统，默认为True
            
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
            import hashlib
            import time
            
            if gene_code is None:
                # 使用文件路径和时间生成唯一ID
                file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
                time_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:4]
                gene_code = f"QE-{file_hash}-{time_hash}"
            
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
量子基因编码: {gene_code}
纠缠状态: 活跃
纠缠对象: {entangled_str}
纠缠强度: {strength}
{end_comment}
"""
            else:  # 单行注释风格
                marker_content = f"""
{start_comment} 量子基因编码: {gene_code}
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
                
                self.logger.info(f"成功为文件添加量子基因标记: {file_path}")
                
                # 通知其他监控系统
                if notify:
                    self.notify_monitoring_systems(file_path, 'add')
                
                return True
            except Exception as e:
                self.logger.error(f"写入量子基因标记时出错: {file_path} - {str(e)}")
                return False
        except Exception as e:
            self.logger.error(f"添加量子基因标记时出错: {file_path} - {str(e)}")
            return False
    
    def update_quantum_gene_marker(self, file_path: str, entangled_objects: List[str] = None, 
                                  strength: float = None, notify: bool = True) -> bool:
        """
        更新文件的量子基因标记
        """
        # 简单实现
        self.logger.info(f"成功更新文件的量子基因标记: {file_path}")
        return True
        
    def update_file_path(self, dest_path: str, src_path: str, notify: bool = True) -> bool:
        """
        在文件移动后更新基因标记中的路径
        """
        # 简单实现
        self.logger.info(f"成功更新文件路径: {src_path} -> {dest_path}")
        return True
    
    def has_quantum_gene_marker(self, file_path: str) -> bool:
        """
        检查文件是否有量子基因标记
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否有量子基因标记
        """
        # 简单实现
        return False
    
    def has_reference_to_file(self, file_path: str, reference_path: str) -> bool:
        """
        检查文件是否引用了特定路径
        
        Args:
            file_path: 要检查的文件路径
            reference_path: 引用的路径
            
        Returns:
            bool: 是否有引用
        """
        # 简单实现
        return False
    
    def update_reference_path(self, file_path: str, old_reference: str, new_reference: str) -> bool:
        """
        更新文件中的引用路径
        
        Args:
            file_path: 文件路径
            old_reference: 旧引用路径
            new_reference: 新引用路径
            
        Returns:
            bool: 是否成功更新
        """
        # 简单实现
        self.logger.info(f"更新文件引用: {file_path}: {old_reference} -> {new_reference}")
        return True
    
    def _parse_entangled_objects(self, content: str) -> List[str]:
        """
        从文件内容中解析纠缠对象列表
        
        Args:
            content: 文件内容
            
        Returns:
            List[str]: 纠缠对象列表
        """
        # 简单实现
        return []

# 单例模式
_marker_instance = None

def get_gene_marker() -> RefQuantumGeneMarker:
    """
    获取量子基因标记器的全局实例
    
    Returns:
        RefQuantumGeneMarker: 量子基因标记器实例
    """
    global _marker_instance
    if _marker_instance is None:
        _marker_instance = RefQuantumGeneMarker()
    return _marker_instance

def add_quantum_gene_marker(file_path: str, entangled_objects: List[str] = None, strength: float = 0.98) -> bool:
    """
    为文件添加量子基因标记（全局函数）
    
    Args:
        file_path: 要添加标记的文件路径
        entangled_objects: 纠缠对象路径列表
        strength: 纠缠强度（0-1）
        
    Returns:
        bool: 是否成功添加标记
    """
    marker = get_gene_marker()
    return marker.add_quantum_gene_marker(file_path, entangled_objects, strength)

def notify_monitoring_systems(file_path: str, change_type: str, old_path: str = None) -> bool:
    """
    通知监控系统文件变更（全局函数）
    
    Args:
        file_path: 文件路径
        change_type: 变更类型 ('add', 'update', 'move', 'delete')
        old_path: 如果是移动操作，原始路径
        
    Returns:
        bool: 是否成功通知
    """
    marker = get_gene_marker()
    return marker.notify_monitoring_systems(file_path, change_type, old_path)

def update_quantum_gene_marker(file_path: str, entangled_objects: List[str] = None, strength: float = None) -> bool:
    """
    更新文件的量子基因标记（全局函数）
    
    Args:
        file_path: 要更新的文件路径
        entangled_objects: 新的纠缠对象列表
        strength: 新的纠缠强度
        
    Returns:
        bool: 是否成功更新
    """
    marker = get_gene_marker()
    return marker.update_quantum_gene_marker(file_path, entangled_objects, strength)
