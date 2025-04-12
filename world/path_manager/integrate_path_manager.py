#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件路径管理器集成脚本
用于将文件路径管理器集成到QEntL、QSM、WeQ、SOM和Ref模块中
"""

import os
import sys
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 文件路径管理器模块路径
file_path_manager_py = os.path.join(project_root, 'world', 'path_manager', 'file_path_manager.py')
file_path_helpers_py = os.path.join(project_root, 'world', 'path_manager', 'file_path_helpers.py')

# 确保文件路径管理器模块存在
if not os.path.exists(file_path_manager_py) or not os.path.exists(file_path_helpers_py):
    raise FileNotFoundError(f"文件路径管理器模块不存在: {file_path_manager_py} 或 {file_path_helpers_py}")

# 需要集成的模块列表
modules = ['QEntL', 'QSM', 'WeQ', 'SOM', 'Ref']

def create_path_module(module_dir):
    """在指定模块目录中创建路径管理模块"""
    if not os.path.exists(module_dir) or not os.path.isdir(module_dir):
        return False
        
    # 创建path_utils.py文件
    path_utils_py = os.path.join(module_dir, 'path_utils.py')
    
    with open(path_utils_py, 'w', encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-

\"\"\"
路径管理工具
提供文件路径解析和管理功能
\"\"\"

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # 优先使用全局文件路径管理器
    from world.path_manager import resolve_path, get_all_files, move_file
    
    # 导入成功的信息
    print(f"在{os.path.basename(os.path.dirname(__file__))}模块中成功集成文件路径管理器")
    
    # 创建模块特定的文件类型
    MODULE_FILE_TYPES = {
        'qentl': ['.qent', '.qentl'],
        'python': ['.py', '.pyw'],
        'data': ['.json', '.yaml', '.yml'],
    }
    
    def get_module_files(file_types=None, recursive=True):
        \"\"\"获取当前模块的所有文件\"\"\"
        module_dir = os.path.dirname(__file__)
        return get_all_files(module_dir, file_types, recursive)
        
    def resolve_module_path(relative_path):
        \"\"\"解析相对于当前模块的路径\"\"\"
        module_dir = os.path.dirname(__file__)
        return resolve_path(relative_path, module_dir)
    
except ImportError:
    # 如果导入失败，提供基本的替代函数
    print(f"在{os.path.basename(os.path.dirname(__file__))}模块中无法导入全局文件路径管理器，使用基本功能")
    
    # 基本的路径解析函数
    def resolve_path(path, base_dir=None):
        \"\"\"基本的路径解析函数\"\"\"
        if base_dir:
            return Path(base_dir) / path
        return Path(path)
    
    # 模块特定的文件类型
    MODULE_FILE_TYPES = {
        'qentl': ['.qent', '.qentl'],
        'python': ['.py', '.pyw'],
        'data': ['.json', '.yaml', '.yml'],
    }
    
    def get_all_files(directory=None, file_types=None, recursive=True):
        \"\"\"基本的文件获取函数\"\"\"
        if directory is None:
            directory = os.getcwd()
        
        extensions = []
        if file_types:
            for file_type in file_types:
                if file_type in MODULE_FILE_TYPES:
                    extensions.extend(MODULE_FILE_TYPES[file_type])
        
        files = []
        if recursive:
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    if not extensions or os.path.splitext(filename)[1] in extensions:
                        files.append(os.path.join(root, filename))
        else:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                if os.path.isfile(full_path) and (not extensions or os.path.splitext(item)[1] in extensions):
                    files.append(full_path)
        return files
        
    def move_file(source_path, target_path, update_references=True):
        \"\"\"基本的文件移动函数\"\"\"
        import shutil
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.move(source_path, target_path)
            return True
        except Exception:
            return False
            
    def get_module_files(file_types=None, recursive=True):
        \"\"\"获取当前模块的所有文件\"\"\"
        module_dir = os.path.dirname(__file__)
        return get_all_files(module_dir, file_types, recursive)
        
    def resolve_module_path(relative_path):
        \"\"\"解析相对于当前模块的路径\"\"\"
        module_dir = os.path.dirname(__file__)
        return resolve_path(relative_path, module_dir)

# 公共API
__all__ = [
    'resolve_path',
    'get_all_files',
    'move_file',
    'get_module_files',
    'resolve_module_path',
    'MODULE_FILE_TYPES'
]
""")

    return os.path.exists(path_utils_py)

# 为每个模块创建路径管理模块
success_count = 0
for module in modules:
    module_dir = os.path.join(project_root, module)
    if create_path_module(module_dir):
        success_count += 1
        print(f"在{module}模块中成功创建路径管理模块")
    else:
        print(f"在{module}模块中创建路径管理模块失败")

print(f"共在{success_count}/{len(modules)}个模块中创建了路径管理模块")

if __name__ == "__main__":
    print("文件路径管理器集成完成") 