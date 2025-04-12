#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建路径管理模块
为QEntL、QSM、WeQ、SOM和Ref模块创建路径管理模块
"""

import os
import sys

# 项目根目录
project_root = os.path.abspath(os.path.dirname(__file__))
print(f"项目根目录: {project_root}")

# 需要创建路径管理模块的目录
modules = ['QEntL', 'QSM', 'WeQ', 'SOM', 'Ref']

# 路径管理模块的内容
path_utils_content = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

\"\"\"
路径管理工具
为模块提供文件路径解析和管理功能
\"\"\"

import os
import sys
import re
from pathlib import Path

class PathUtils:
    \"\"\"路径管理工具类\"\"\"
    
    def __init__(self, module_root=None):
        \"\"\"初始化路径管理工具
        
        Args:
            module_root: 模块根目录，默认为当前文件所在目录
        \"\"\"
        self.module_root = module_root or os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.module_root)
        
        # 路径映射规则
        self.path_mappings = {
            # QEntL路径映射
            r'(.+?)/core\.qent$': r'\\1/qent/core.qent',
            r'(.+?)/quantum_network\.qent$': r'\\1/qent/quantum_network.qent',
            r'(.+?)/templates/(.+?)\.qentl$': r'\\1/qentl/\\2.qentl',
            
            # 模块QEntL路径映射
            r'(.+?)/QEntL/(.+?)_module\.qent$': r'\\1/QEntL/qent/\\2_module.qent'
        }
        
    def resolve_path(self, path, base_dir=None):
        \"\"\"解析文件路径，尝试多种可能的路径组合
        
        Args:
            path: 原始文件路径（相对或绝对路径）
            base_dir: 基准目录，用于解析相对路径
            
        Returns:
            解析后的文件路径（Path对象）
        \"\"\"
        # 标准化路径
        if base_dir:
            base_path = Path(base_dir)
        else:
            base_path = Path(self.module_root)
            
        # 处理相对路径
        if not os.path.isabs(path):
            path = base_path / path
        else:
            path = Path(path)
            
        # 尝试原始路径
        if path.exists():
            return path
            
        # 路径映射
        path_str = str(path).replace('\\\\', '/')
        for pattern, replacement in self.path_mappings.items():
            if re.search(pattern, path_str):
                new_path_str = re.sub(pattern, replacement, path_str)
                new_path = Path(new_path_str)
                if new_path.exists():
                    return new_path
        
        # 如果是QEntL文件，尝试特殊处理
        if path_str.endswith('.qent') or path_str.endswith('.qentl'):
            # 尝试在qent或qentl子目录中查找
            if path_str.endswith('.qent'):
                parent_dir = path.parent
                file_name = path.name
                qent_dir = parent_dir / 'qent'
                if qent_dir.exists():
                    qent_path = qent_dir / file_name
                    if qent_path.exists():
                        return qent_path
            elif path_str.endswith('.qentl'):
                parent_dir = path.parent
                file_name = path.name
                qentl_dir = parent_dir / 'qentl'
                if qentl_dir.exists():
                    qentl_path = qentl_dir / file_name
                    if qentl_path.exists():
                        return qentl_path
        
        # 返回原始路径
        return path
        
    def get_module_files(self, pattern=None, recursive=True):
        \"\"\"获取模块中的文件
        
        Args:
            pattern: 文件名模式，如'*.qent'
            recursive: 是否递归查找子目录
            
        Returns:
            文件路径列表
        \"\"\"
        files = []
        
        if recursive:
            for root, _, filenames in os.walk(self.module_root):
                for filename in filenames:
                    if pattern is None or self._match_pattern(filename, pattern):
                        files.append(os.path.join(root, filename))
        else:
            for item in os.listdir(self.module_root):
                file_path = os.path.join(self.module_root, item)
                if os.path.isfile(file_path) and (pattern is None or self._match_pattern(item, pattern)):
                    files.append(file_path)
                    
        return files
        
    def _match_pattern(self, filename, pattern):
        \"\"\"检查文件名是否匹配模式
        
        Args:
            filename: 文件名
            pattern: 模式，支持'*'通配符
            
        Returns:
            是否匹配
        \"\"\"
        if pattern.startswith('*'):
            return filename.endswith(pattern[1:])
        elif pattern.endswith('*'):
            return filename.startswith(pattern[:-1])
        else:
            return filename == pattern

# 创建单例实例
path_utils = PathUtils()

# 便捷函数
def resolve_path(path, base_dir=None):
    \"\"\"解析文件路径\"\"\"
    return path_utils.resolve_path(path, base_dir)
    
def get_module_files(pattern=None, recursive=True):
    \"\"\"获取模块文件\"\"\"
    return path_utils.get_module_files(pattern, recursive)
"""

# 为每个模块创建路径管理模块
for module in modules:
    module_dir = os.path.join(project_root, module)
    if os.path.exists(module_dir) and os.path.isdir(module_dir):
        path_utils_file = os.path.join(module_dir, 'path_utils.py')
        with open(path_utils_file, 'w', encoding='utf-8') as f:
            f.write(path_utils_content)
        print(f"已在 {module} 模块中创建路径管理模块")
    else:
        print(f"模块目录不存在: {module_dir}")

print("路径管理模块创建完成") 