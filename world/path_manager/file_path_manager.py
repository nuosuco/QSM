#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
全局文件路径管理器
为整个项目提供统一的文件路径解析和管理功能
可以处理文件移动、重命名等操作，而不需要修改依赖文件中的引用
"""

import os
import re
import sys
import logging
from pathlib import Path

logger = logging.getLogger("文件路径管理器")

class FilePathManager:
    """全局文件路径管理器"""
    
    def __init__(self, project_root=None):
        """初始化文件路径管理器
        
        Args:
            project_root: 项目根目录路径，默认为当前工作目录
        """
        self.project_root = Path(project_root) if project_root else Path(os.getcwd())
        self.path_mappings = {}
        self.file_extensions = {
            'qentl': ['.qent', '.qentl'],
            'python': ['.py', '.pyw'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'data': ['.json', '.yaml', '.yml', '.xml'],
            'document': ['.md', '.txt', '.rst'],
            'config': ['.cfg', '.conf', '.ini'],
        }
        
        # 默认路径映射规则
        self._add_default_mappings()
        
    def _add_default_mappings(self):
        """添加默认的路径映射规则"""
        # QEntL文件的映射规则
        self.add_mapping(
            r'(.*?)/core/.qent$', 
            r'/1/qent/core.qent', 
            file_types=['qentl']
        )
        self.add_mapping(
            r'(.*?)/quantum_network/.qent$', 
            r'/1/qent/quantum_network.qent', 
            file_types=['qentl']
        )
        self.add_mapping(
            r'(.*?)/templates/(.*?)/.qentl$', 
            r'/1/qentl//2.qentl', 
            file_types=['qentl']
        )
        
        # 各模块QEntL文件的映射规则
        for module in ['QSM', 'WeQ', 'SOM', 'Ref']:
            self.add_mapping(
                f'{module}/QEntL/(.+?)_module/.qent$',
                f'{module}/QEntL/qent///1_module.qent',
                file_types=['qentl']
            )
        
    def add_mapping(self, pattern, replacement, file_types=None):
        """添加路径映射规则
        
        Args:
            pattern: 正则表达式模式，用于匹配原始路径
            replacement: 替换模式，用于生成新路径
            file_types: 适用的文件类型列表，如['qentl', 'python']
        """
        if not file_types:
            file_types = list(self.file_extensions.keys())
            
        extensions = []
        for file_type in file_types:
            if file_type in self.file_extensions:
                extensions.extend(self.file_extensions[file_type])
        
        self.path_mappings[pattern] = {
            'replacement': replacement,
            'extensions': extensions
        }
        
    def resolve_path(self, path, base_dir=None, create_if_missing=False):
        """解析文件路径，尝试多种可能的路径组合
        
        Args:
            path: 原始文件路径（可以是相对路径或绝对路径）
            base_dir: 基准目录，用于解析相对路径
            create_if_missing: 如果文件不存在，是否创建目录结构
            
        Returns:
            解析后的文件路径（Path对象）
        """
        # 标准化路径
        if base_dir:
            base_path = Path(base_dir)
        else:
            base_path = self.project_root
            
        # 处理相对路径
        if not os.path.isabs(path):
            path = base_path / path
        else:
            path = Path(path)
            
        # 尝试原始路径
        if path.exists():
            return path
            
        # 获取文件扩展名
        _, ext = os.path.splitext(path)
        
        # 尝试路径映射规则
        rel_path = path.relative_to(self.project_root) if self.project_root in path.parents else path
        rel_path_str = str(rel_path).replace('\\', '/')
        
        for pattern, mapping in self.path_mappings.items():
            if ext in mapping['extensions'] and re.match(pattern, rel_path_str):
                new_rel_path = re.sub(pattern, mapping['replacement'], rel_path_str)
                new_path = self.project_root / new_rel_path
                
                if new_path.exists():
                    logger.debug(f"已重新映射路径: {path} -> {new_path}")
                    return new_path
                    
        # 如需创建目录结构
        if create_if_missing:
            os.makedirs(path.parent, exist_ok=True)
            return path
            
        logger.warning(f"无法解析文件路径: {path}")
        return path
        
    def get_all_files(self, directory=None, file_types=None, recursive=True):
        """获取指定目录下的所有文件
        
        Args:
            directory: 要搜索的目录，默认为项目根目录
            file_types: 要包含的文件类型列表，如['qentl', 'python']
            recursive: 是否递归搜索子目录
            
        Returns:
            文件路径列表
        """
        if directory is None:
            directory = self.project_root
        else:
            directory = Path(directory)
            
        # 确定要包含的文件扩展名
        extensions = []
        if file_types:
            for file_type in file_types:
                if file_type in self.file_extensions:
                    extensions.extend(self.file_extensions[file_type])
        
        # 搜索文件
        files = []
        if recursive:
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    if not extensions or os.path.splitext(filename)[1] in extensions:
                        files.append(Path(root) / filename)
        else:
            for item in directory.iterdir():
                if item.is_file() and (not extensions or item.suffix in extensions):
                    files.append(item)
                    
        return files
        
    def move_file(self, source_path, target_path, update_references=True):
        """移动文件并更新引用
        
        Args:
            source_path: 源文件路径
            target_path: 目标文件路径
            update_references: 是否更新引用该文件的其他文件
            
        Returns:
            是否成功移动文件
        """
        source_path = Path(source_path)
        target_path = Path(target_path)
        
        # 确保源文件存在
        if not source_path.exists():
            logger.error(f"源文件不存在: {source_path}")
            return False
            
        # 确保目标目录存在
        os.makedirs(target_path.parent, exist_ok=True)
        
        try:
            # 移动文件
            target_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.rename(target_path)
            
            # 添加映射规则，使原始路径可以解析到新路径
            rel_source = source_path.relative_to(self.project_root) if self.project_root in source_path.parents else source_path
            rel_target = target_path.relative_to(self.project_root) if self.project_root in target_path.parents else target_path
            
            pattern = str(rel_source).replace('\\', '/').replace('.', r'\.')
            replacement = str(rel_target).replace('\\', '/')
            
            self.add_mapping(pattern, replacement)
            
            logger.info(f"已成功移动文件: {source_path} -> {target_path}")
            
            # 如果需要更新引用
            if update_references:
                self._update_references(source_path, target_path)
                
            return True
            
        except Exception as e:
            logger.error(f"移动文件失败: {e}")
            return False
            
    def _update_references(self, old_path, new_path):
        """更新对指定文件的引用
        
        Args:
            old_path: 原文件路径
            new_path: 新文件路径
        """
        # 这里实现引用更新逻辑
        # 需要搜索项目中的所有文件，查找对old_path的引用并更新为new_path
        # 这个功能比较复杂，可能需要针对不同类型的文件使用不同的解析方法
        pass

# 创建全局实例
path_manager = FilePathManager()

def resolve_path(path, base_dir=None):
    """解析文件路径的便捷函数"""
    return path_manager.resolve_path(path, base_dir)
    
def get_all_files(directory=None, file_types=None, recursive=True):
    """获取所有文件的便捷函数"""
    return path_manager.get_all_files(directory, file_types, recursive)
    
def move_file(source_path, target_path, update_references=True):
    """移动文件的便捷函数"""
    return path_manager.move_file(source_path, target_path, update_references) 