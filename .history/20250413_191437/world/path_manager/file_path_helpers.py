#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件路径辅助器
为各个模块集成文件路径管理功能
"""

import os
import sys
import importlib
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # 尝试导入文件路径管理器
    from .file_path_manager import FilePathManager, resolve_path, get_all_files, move_file
    
    path_manager_available = True
except ImportError:
    # 如果导入失败，提供基本的替代函数
    path_manager_available = False
    
    def resolve_path(path, base_dir=None):
        """基本的路径解析函数"""
        if base_dir:
            return Path(base_dir) / path
        return Path(path)
        
    def get_all_files(directory=None, file_types=None, recursive=True):
        """基本的文件获取函数"""
        if directory is None:
            directory = os.getcwd()
        
        files = []
        if recursive:
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        else:
            for item in os.listdir(directory):
                if os.path.isfile(os.path.join(directory, item)):
                    files.append(os.path.join(directory, item))
        return files
        
    def move_file(source_path, target_path, update_references=True):
        """基本的文件移动函数"""
        import shutil
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.move(source_path, target_path)
            return True
        except Exception:
            return False

def patch_import_system():
    """修补Python导入系统，使其使用文件路径管理器"""
    if not path_manager_available:
        return False
        
    # 保存原始的导入函数
    original_import = __builtins__['__import__']
    
    # 创建一个新的导入函数
    def patched_import(name, globals=None, locals=None, fromlist=(), level=0):
        # 调用原始导入函数
        module = original_import(name, globals, locals, fromlist, level)
        
        # 如果导入失败，尝试使用文件路径管理器解析模块路径
        if fromlist and not all(hasattr(module, attr) for attr in fromlist):
            # 获取模块文件路径
            if hasattr(module, '__file__'):
                module_dir = os.path.dirname(module.__file__)
                
                # 尝试解析可能移动的模块文件
                for attr in fromlist:
                    if not hasattr(module, attr):
                        # 构建可能的模块文件路径
                        possible_paths = [
                            os.path.join(module_dir, f"{attr}.py"),
                            os.path.join(module_dir, attr, "__init__.py"),
                            os.path.join(module_dir, "qent", f"{attr}.qent"),
                            os.path.join(module_dir, "qentl", f"{attr}.qentl")
                        ]
                        
                        # 使用文件路径管理器解析路径
                        for path in possible_paths:
                            resolved_path = resolve_path(path)
                            if os.path.exists(resolved_path):
                                # 如果找到文件，尝试导入它
                                try:
                                    if resolved_path.endswith('.py'):
                                        # 动态导入Python模块
                                        spec = importlib.util.spec_from_file_location(attr, resolved_path)
                                        submodule = importlib.util.module_from_spec(spec)
                                        spec.loader.exec_module(submodule)
                                        setattr(module, attr, submodule)
                                    elif resolved_path.endswith(('.qent', '.qentl')):
                                        # 对于QEntL文件，只记录路径信息
                                        setattr(module, attr, resolved_path)
                                except Exception:
                                    pass
                                    
        return module
    
    # 替换内置导入函数
    __builtins__['__import__'] = patched_import
    return True

# 尝试修补导入系统
if path_manager_available and __name__ != "__main__":
    patch_result = patch_import_system()
    if patch_result:
        print("文件路径管理器已成功集成到Python导入系统")
    else:
        print("文件路径管理器集成失败")
else:
    if __name__ != "__main__":
        print("文件路径管理器不可用，使用基本的路径处理函数") 