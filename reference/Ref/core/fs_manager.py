#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ref文件系统管理服务
提供统一的文件和目录管理功能，整合现有的目录结构优化器、文件组织监护器等组件
"""

import os
import sys
import shutil
import logging
import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Set, Any, Optional, Union
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.append(project_root)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(current_dir), "logs", "fs_manager.log"), mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("FSManager")

# 导入目录结构优化器
try:
    from Ref.utils.directory_structure_optimizer import get_directory_optimizer
    directory_optimizer_available = True
except ImportError as e:
    logger.warning(f"无法导入目录结构优化器: {str(e)}")
    directory_optimizer_available = False

# 导入文件组织监护器
try:
    from Ref.utils.file_organization_guardian import get_guardian
    file_guardian_available = True
except ImportError as e:
    logger.warning(f"无法导入文件组织监护器: {str(e)}")
    file_guardian_available = False

# 导入文件监控器
try:
    from Ref.utils.file_monitor import get_file_monitor
    file_monitor_available = True
except ImportError as e:
    logger.warning(f"无法导入文件监控器: {str(e)}")
    file_monitor_available = False

# 导入量子基因标记工具
try:
    from Ref.utils.quantum_gene_marker import RefQuantumGeneMarker
    quantum_gene_marker_available = True
except ImportError as e:
    logger.warning(f"无法导入量子基因标记工具: {str(e)}")
    quantum_gene_marker_available = False

# 全局实例
_fs_manager_instance = None


class FileSystemManager:
    """统一的文件系统管理服务，整合文件和目录管理功能"""
    
    def __init__(self, project_root: str = None):
        """
        初始化文件系统管理服务
        
        Args:
            project_root: 项目根目录，如果为None，则自动检测
        """
        if project_root is None:
            self.project_root = os.path.abspath(os.path.dirname(os.path.dirname(current_dir)))
        else:
            self.project_root = os.path.abspath(project_root)
            
        self.logger = logger
        
        # 初始化备份目录
        self.backup_dir = os.path.join(self.project_root, "Ref", "backup", "fs_manager")
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 尝试初始化组件
        if directory_optimizer_available:
            self.directory_optimizer = get_directory_optimizer(self.project_root)
        else:
            self.directory_optimizer = None
            
        if file_guardian_available:
            self.file_guardian = get_guardian(self.project_root)
        else:
            self.file_guardian = None
            
        if file_monitor_available:
            self.file_monitor = get_file_monitor()
        else:
            self.file_monitor = None
            
        if quantum_gene_marker_available:
            self.quantum_gene_marker = RefQuantumGeneMarker()
        else:
            self.quantum_gene_marker = None
            
        # 主要模块列表
        self.main_modules = ['QSM', 'WeQ', 'SOM', 'Ref', 'QEntL']
        
        # 标准子目录结构
        self.standard_subdirs = [
            'core', 'api', 'tools', 'data', 'models', 'tests', 
            'docs', 'utils', 'examples', 'QEntL'
        ]
        
        # 文件类型映射到目标目录
        self.file_type_mapping = {
            # Python文件
            r'_api\.py$': 'api',           # API相关文件
            r'_test\.py$': 'tests',        # 测试文件
            r'test_.*\.py$': 'tests',      # 测试文件
            r'utils?[/_].*/.py$': 'utils', # 工具文件
            r'data[/_].*/.py$': 'data',    # 数据处理文件
            r'model.*\.py$': 'models',     # 模型文件
            r'train.*\.py$': 'train',      # 训练文件
            r'_core\.py$': 'core',         # 核心文件
            r'_monitor\.py$': 'utils',     # 监控工具
            
            # 量子纠缠模板文件
            r'\.qent$': 'QEntL/qent',      # .qent文件
            r'\.qentl$': 'QEntL/qentl',    # .qentl模板文件
            
            # 文档文件
            r'\.md$': 'docs',              # Markdown文档
            r'\.rst$': 'docs',             # RST文档
            r'\.txt$': 'docs',             # 文本文档
            
            # 示例文件
            r'example.*\.py$': 'examples', # 示例代码
            r'demo.*\.py$': 'examples',    # 示例代码
        }
        
        # 特殊文件不移动
        self.special_files = {
            '__init__.py',
            'README.md',
            'setup.py',
            'requirements.txt',
            '.gitignore'
        }
        
        # 模块特殊目录映射
        self.module_special_mappings = {
            'WeQ': {
                r'helper.*\.py$': 'train/helpers',
                r'model.*\.py$': 'train/models',
                r'data.*\.py$': 'train/data',
            }
        }
        
        self.logger.info(f"文件系统管理服务初始化完成，项目根目录: {self.project_root}")
        
    # 目录管理功能 -------------------------------------------------------
    
    def create_directory(self, path: str, exist_ok: bool = True) -> bool:
        """
        创建目录
        
        Args:
            path: 目录路径
            exist_ok: 如果目录已存在是否忽略
            
        Returns:
            是否成功创建目录
        """
        try:
            os.makedirs(path, exist_ok=exist_ok)
            self.logger.info(f"创建目录: {path}")
            return True
        except Exception as e:
            self.logger.error(f"创建目录失败 {path}: {str(e)}")
            return False
            
    def delete_empty_directory(self, path: str, recursive: bool = True) -> bool:
        """
        删除空目录
        
        Args:
            path: 目录路径
            recursive: 是否递归删除子目录
            
        Returns:
            是否成功删除目录
        """
        if not os.path.isdir(path):
            return False
            
        try:
            # 检查目录是否为空
            contents = os.listdir(path)
            if contents:
                if recursive:
                    # 递归处理子目录
                    for item in contents:
                        item_path = os.path.join(path, item)
                        if os.path.isdir(item_path):
                            self.delete_empty_directory(item_path, recursive)
                    
                    # 再次检查目录是否为空
                    contents = os.listdir(path)
                    
                if contents:  # 仍然有内容，不删除
                    return False
                    
            # 删除空目录
            os.rmdir(path)
            self.logger.info(f"删除空目录: {path}")
            return True
        except Exception as e:
            self.logger.error(f"删除空目录失败 {path}: {str(e)}")
            return False
            
    def merge_directories(self, source_dir: str, target_dir: str, move_files: bool = True) -> bool:
        """
        合并目录
        
        Args:
            source_dir: 源目录
            target_dir: 目标目录
            move_files: 是否移动文件而不是复制
            
        Returns:
            是否成功合并目录
        """
        if not os.path.isdir(source_dir) or not os.path.isdir(target_dir):
            return False
            
        try:
            # 复制或移动源目录中的文件到目标目录
            for item in os.listdir(source_dir):
                source_path = os.path.join(source_dir, item)
                target_path = os.path.join(target_dir, item)
                
                if os.path.exists(target_path):
                    # 文件或目录已存在，需要决定如何处理
                    if os.path.isdir(source_path) and os.path.isdir(target_path):
                        # 递归合并子目录
                        self.merge_directories(source_path, target_path, move_files)
                    else:
                        # 文件已存在，备份后覆盖
                        self._backup_file(target_path)
                        if move_files:
                            shutil.move(source_path, target_path)
                        else:
                            shutil.copy2(source_path, target_path)
                else:
                    # 目标不存在，直接复制或移动
                    if move_files:
                        shutil.move(source_path, target_path)
                    else:
                        if os.path.isdir(source_path):
                            shutil.copytree(source_path, target_path)
                        else:
                            shutil.copy2(source_path, target_path)
                            
            # 如果是移动模式，检查源目录是否已空并删除
            if move_files:
                self.delete_empty_directory(source_dir, recursive=False)
                
            self.logger.info(f"成功{'移动' if move_files else '复制'}合并目录: {source_dir} -> {target_dir}")
            return True
        except Exception as e:
            self.logger.error(f"合并目录失败 {source_dir} -> {target_dir}: {str(e)}")
            return False
    
    # 文件管理功能 -------------------------------------------------------
    
    def create_file(self, filepath: str, content: str, allow_overwrite: bool = False) -> bool:
        """
        创建文件
        
        Args:
            filepath: 文件路径
            content: 文件内容
            allow_overwrite: 是否允许覆盖现有文件
            
        Returns:
            是否成功创建文件
        """
        # 使用文件组织监护器（如果可用）
        if self.file_guardian is not None:
            success, message = self.file_guardian.safe_create_file(
                filepath, 
                content, 
                purpose=f"由FSManager创建于 {datetime.now().isoformat()}", 
                allow_overwrite=allow_overwrite
            )
            return success
            
        # 简单版本
        try:
            if os.path.exists(filepath) and not allow_overwrite:
                self.logger.warning(f"文件已存在且不允许覆盖: {filepath}")
                return False
                
            # 如果文件已存在且允许覆盖，先备份
            if os.path.exists(filepath):
                self._backup_file(filepath)
                
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.logger.info(f"创建文件: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"创建文件失败 {filepath}: {str(e)}")
            return False
    
    def move_file(self, source_path: str, target_path: str, update_imports: bool = True) -> bool:
        """
        移动文件并更新导入路径
        
        Args:
            source_path: 源文件路径
            target_path: 目标文件路径
            update_imports: 是否更新导入路径
            
        Returns:
            是否成功移动文件
        """
        if not os.path.exists(source_path):
            self.logger.error(f"源文件不存在: {source_path}")
            return False
            
        try:
            # 读取文件内容
            with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # 如果需要更新导入路径
            if update_imports and source_path.endswith('.py'):
                content = self._update_import_paths(content, source_path, target_path)
                
            # 确保目标目录存在
            os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
            
            # 备份目标文件（如果存在）
            if os.path.exists(target_path):
                self._backup_file(target_path)
                
            # 写入目标文件
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # 删除源文件
            os.remove(source_path)
            
            self.logger.info(f"移动文件: {source_path} -> {target_path}")
            return True
        except Exception as e:
            self.logger.error(f"移动文件失败 {source_path} -> {target_path}: {str(e)}")
            return False
            
    def delete_file(self, filepath: str, force: bool = False) -> bool:
        """
        删除文件
        
        Args:
            filepath: 文件路径
            force: 是否强制删除
            
        Returns:
            是否成功删除文件
        """
        # 使用文件组织监护器（如果可用）
        if self.file_guardian is not None and not force:
            success, message = self.file_guardian.safe_delete_file(filepath, force)
            return success
            
        # 简单版本
        try:
            if not os.path.exists(filepath):
                self.logger.warning(f"文件不存在，无需删除: {filepath}")
                return True
                
            # 备份文件
            self._backup_file(filepath)
            
            # 删除文件
            os.remove(filepath)
            
            self.logger.info(f"删除文件: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"删除文件失败 {filepath}: {str(e)}")
            return False
    
    # 项目结构优化功能 ---------------------------------------------------
    
    def create_standard_structure(self) -> Dict[str, Any]:
        """
        创建标准目录结构
        
        Returns:
            包含创建结果的字典
        """
        if self.directory_optimizer is not None:
            return self.directory_optimizer.create_standard_directory_structure()
            
        results = {
            'created_dirs': [],
            'existing_dirs': [],
            'errors': []
        }
        
        # 为每个主要模块创建标准子目录
        for module in self.main_modules:
            module_path = os.path.join(self.project_root, module)
            
            if not os.path.exists(module_path):
                self.logger.warning(f"模块目录不存在: {module}")
                results['errors'].append(f"模块目录不存在: {module}")
                continue
                
            # 创建标准子目录
            for subdir in self.standard_subdirs:
                subdir_path = os.path.join(module_path, subdir)
                
                if os.path.exists(subdir_path):
                    results['existing_dirs'].append(subdir_path)
                else:
                    try:
                        os.makedirs(subdir_path, exist_ok=True)
                        # 创建空的__init__.py文件
                        init_file = os.path.join(subdir_path, '__init__.py')
                        if not os.path.exists(init_file):
                            with open(init_file, 'w', encoding='utf-8') as f:
                                f.write(f'"""\n{subdir} 包\n"""\n')
                        
                        results['created_dirs'].append(subdir_path)
                        self.logger.info(f"创建目录: {subdir_path}")
                    except Exception as e:
                        error_msg = f"创建目录失败 {subdir_path}: {str(e)}"
                        results['errors'].append(error_msg)
                        self.logger.error(error_msg)
        
        return results
    
    def organize_module_files(self, module: str, apply: bool = False) -> Dict[str, Any]:
        """
        组织模块文件
        
        Args:
            module: 模块名称
            apply: 是否真正执行，False表示只模拟
            
        Returns:
            包含组织结果的字典
        """
        if self.directory_optimizer is not None:
            return self.directory_optimizer.organize_files(module, dry_run=not apply)
            
        # 简单实现
        module_path = os.path.join(self.project_root, module)
        if not os.path.exists(module_path):
            return {'error': f"模块不存在: {module}"}
            
        results = {
            'moved_files': [],
            'unchanged_files': [],
            'errors': []
        }
        
        # 扫描模块根目录文件
        self.logger.info(f"{'模拟' if not apply else ''}组织 {module} 模块文件")
        
        for item in os.listdir(module_path):
            item_path = os.path.join(module_path, item)
            
            # 跳过目录和特殊文件
            if os.path.isdir(item_path) or item.startswith('.') or item == '__init__.py':
                continue
                
            # 简单的文件类型识别
            target_dir = self._determine_file_target_directory(item)
            
            if target_dir:
                target_path = os.path.join(module_path, target_dir, item)
                
                if not apply:
                    # 只模拟
                    results['moved_files'].append({
                        'from': item_path,
                        'to': target_path,
                        'status': 'simulated'
                    })
                    self.logger.info(f"[模拟] 将移动: {item_path} -> {target_path}")
                else:
                    # 实际移动
                    try:
                        if self.move_file(item_path, target_path):
                            results['moved_files'].append({
                                'from': item_path,
                                'to': target_path,
                                'status': 'moved'
                            })
                    except Exception as e:
                        error_msg = f"移动文件失败 {item_path} -> {target_path}: {str(e)}"
                        results['errors'].append(error_msg)
                        self.logger.error(error_msg)
            else:
                results['unchanged_files'].append(item_path)
        
        self.logger.info(f"{'模拟' if not apply else ''}组织完成: "
                       f"移动 {len(results['moved_files'])} 个文件, "
                       f"保持不变 {len(results['unchanged_files'])} 个文件, "
                       f"发生 {len(results['errors'])} 个错误")
        
        return results
    
    def organize_all_modules(self, apply: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        组织所有模块文件
        
        Args:
            apply: 是否真正执行，False表示只模拟
            
        Returns:
            包含每个模块组织结果的字典
        """
        results = {}
        
        for module in self.main_modules:
            module_path = os.path.join(self.project_root, module)
            if os.path.exists(module_path):
                results[module] = self.organize_module_files(module, apply)
                
        return results
    
    def clean_empty_directories(self) -> Dict[str, List[str]]:
        """
        清理项目中的空目录
        
        Returns:
            包含清理结果的字典
        """
        results = {
            'deleted': [],
            'errors': []
        }
        
        for module in self.main_modules:
            module_path = os.path.join(self.project_root, module)
            if not os.path.exists(module_path):
                continue
                
            # 遍历模块目录
            for root, dirs, files in os.walk(module_path, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if self.delete_empty_directory(dir_path, recursive=False):
                        results['deleted'].append(dir_path)
        
        return results
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """
        分析项目结构
        
        Returns:
            包含项目结构分析的字典
        """
        if self.directory_optimizer is not None:
            return self.directory_optimizer.analyze_project_structure()
            
        # 简单实现
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': self.project_root,
            'modules': {},
            'file_counts': {
                'total': 0,
                'by_type': {}
            },
            'directory_counts': {
                'total': 0,
                'by_module': {}
            },
            'recommendations': []
        }
        
        for module in self.main_modules:
            module_path = os.path.join(self.project_root, module)
            if not os.path.exists(module_path):
                continue
                
            # 分析模块
            module_info = {
                'path': module_path,
                'directory_count': 0,
                'file_count': 0,
                'files_by_type': {},
                'files_in_root': [],
                'subdirectories': [],
                'missing_standard_dirs': []
            }
            
            # 检查标准子目录
            for subdir in self.standard_subdirs:
                if not os.path.exists(os.path.join(module_path, subdir)):
                    module_info['missing_standard_dirs'].append(subdir)
            
            # 遍历模块目录
            for root, dirs, files in os.walk(module_path):
                # 更新目录计数
                module_info['directory_count'] += len(dirs)
                
                # 相对于模块根目录的路径
                rel_path = os.path.relpath(root, module_path)
                
                # 添加子目录
                if rel_path != '.' and os.path.dirname(rel_path) == '.':
                    module_info['subdirectories'].append(rel_path)
                
                # 处理文件
                for file in files:
                    module_info['file_count'] += 1
                    
                    # 获取文件扩展名
                    _, ext = os.path.splitext(file)
                    ext = ext.lower()
                    
                    # 更新按类型的文件计数
                    if ext not in module_info['files_by_type']:
                        module_info['files_by_type'][ext] = 0
                    module_info['files_by_type'][ext] += 1
                    
                    # 检查是否为根目录中的文件
                    if rel_path == '.':
                        module_info['files_in_root'].append(file)
            
            # 添加到报告
            report['modules'][module] = module_info
            
            # 更新总计数
            report['file_counts']['total'] += module_info['file_count']
            report['directory_counts']['total'] += module_info['directory_count']
            report['directory_counts']['by_module'][module] = module_info['directory_count']
            
            for ext, count in module_info['files_by_type'].items():
                if ext not in report['file_counts']['by_type']:
                    report['file_counts']['by_type'][ext] = 0
                report['file_counts']['by_type'][ext] += count
            
            # 生成建议
            if module_info['missing_standard_dirs']:
                missing_dirs_str = ', '.join(module_info['missing_standard_dirs'])
                report['recommendations'].append(
                    f"在 {module} 模块中创建缺失的标准目录: {missing_dirs_str}"
                )
            
            # 检查根目录中的Python文件
            py_files_in_root = [f for f in module_info['files_in_root'] 
                              if f.endswith('.py') and f != '__init__.py']
            if py_files_in_root:
                report['recommendations'].append(
                    f"将 {module} 模块根目录中的 {len(py_files_in_root)} 个Python文件移动到适当的子目录"
                )
        
        return report
    
    # 辅助方法 -----------------------------------------------------------
    
    def _backup_file(self, filepath: str) -> Optional[str]:
        """备份文件并返回备份路径"""
        if not os.path.exists(filepath):
            return None
            
        try:
            # 创建备份文件名
            filename = os.path.basename(filepath)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{filename}.{timestamp}.bak"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # 确保备份目录存在
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # 复制文件
            shutil.copy2(filepath, backup_path)
            self.logger.info(f"文件已备份: {filepath} -> {backup_path}")
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"备份文件失败 {filepath}: {str(e)}")
            return None
            
    def _determine_file_target_directory(self, filename: str) -> Optional[str]:
        """根据文件名确定目标目录"""
        # 去掉路径部分，只保留文件名
        filename = os.path.basename(filename)
        
        # 特殊文件不移动
        if filename in ['__init__.py', 'README.md', 'setup.py', 'requirements.txt', '.gitignore']:
            return None
            
        # 根据文件名模式确定目标目录
        if filename.endswith('_test.py') or filename.startswith('test_'):
            return 'tests'
        elif filename.endswith('_api.py') or 'api' in filename.lower():
            return 'api'
        elif 'util' in filename.lower() or 'helper' in filename.lower():
            return 'utils'
        elif 'model' in filename.lower():
            return 'models'
        elif 'example' in filename.lower() or 'demo' in filename.lower():
            return 'examples'
        elif '_core' in filename.lower():
            return 'core'
        elif filename.endswith('.md') or filename.endswith('.rst') or filename.endswith('.txt'):
            return 'docs'
            
        # 默认情况：Python文件放在core
        if filename.endswith('.py'):
            return 'core'
            
        return None
            
    def _update_import_paths(self, content: str, source_path: str, target_path: str) -> str:
        """更新Python文件中的导入路径"""
        # 获取源文件和目标文件的相对路径
        rel_source = os.path.relpath(source_path, self.project_root)
        rel_target = os.path.relpath(target_path, self.project_root)
        
        # 如果源文件和目标文件在同一目录，则不需要调整
        if os.path.dirname(rel_source) == os.path.dirname(rel_target):
            return content
            
        # 获取源文件和目标文件的包路径
        source_package = rel_source.replace(os.path.sep, '.').rsplit('.', 1)[0]
        target_package = rel_target.replace(os.path.sep, '.').rsplit('.', 1)[0]
        
        # 调整导入语句
        lines = content.splitlines()
        new_lines = []
        
        for line in lines:
            # 查找from ... import ...语句
            from_import_match = re.match(r'from\s+(\.+)?([\w.]+)\s+import\s+', line)
            if from_import_match:
                dots = from_import_match.group(1) or ''
                package = from_import_match.group(2)
                
                # 如果是相对导入
                if dots:
                    # 计算新的相对路径
                    if dots == '.':  # 从当前包导入
                        # 如果源文件和目标文件的包路径相同，则不用调整
                        if os.path.dirname(source_package) == os.path.dirname(target_package):
                            new_lines.append(line)
                        else:
                            # 需要调整相对导入
                            new_package = os.path.relpath(
                                os.path.dirname(source_package),
                                os.path.dirname(target_package)
                            ).replace(os.path.sep, '.')
                            if new_package == '.':
                                new_line = f'from . import {package}'
                            else:
                                new_line = f'from .{new_package} import {package}'
                            new_lines.append(new_line)
                    else:  # 从父包导入
                        # 计算新的相对深度
                        source_depth = len(dots) - 1
                        target_depth = len(target_package.split('.')) - len(source_package.split('.')) + source_depth
                        new_dots = '.' * (target_depth + 1)
                        new_line = line.replace(dots, new_dots, 1)
                        new_lines.append(new_line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)

    def is_special_file(self, filename: str) -> bool:
        """
        判断是否为特殊文件（不应移动）
        
        Args:
            filename: 文件名
            
        Returns:
            是否为特殊文件
        """
        return filename in self.special_files
    
    def determine_target_directory(self, filepath: str, module_name: str) -> Optional[str]:
        """
        确定文件应该移动到的目标目录
        
        Args:
            filepath: 文件路径
            module_name: 模块名称
            
        Returns:
            目标目录或None（如果不应移动）
        """
        filename = os.path.basename(filepath)
        
        # 特殊文件不移动
        if self.is_special_file(filename):
            return None
        
        # 使用文件类型映射
        for pattern, target_dir in self.file_type_mapping.items():
            if re.search(pattern, filename, re.IGNORECASE):
                return target_dir
        
        # 模块特殊处理
        if module_name in self.module_special_mappings:
            for pattern, target_dir in self.module_special_mappings[module_name].items():
                if re.search(pattern, filename, re.IGNORECASE):
                    return target_dir
        
        # 默认情况：Python文件放在core，其他文件不移动
        if filename.endswith('.py'):
            return 'core'
        
        return None
    
    def update_import_paths(self, file_content: str, old_path: Path, new_path: Path) -> str:
        """
        更新文件中的导入路径
        
        Args:
            file_content: 文件内容
            old_path: 旧路径
            new_path: 新路径
            
        Returns:
            更新后的文件内容
        """
        # 获取相对路径信息
        old_parts = old_path.parts
        new_parts = new_path.parts
        
        # 找到模块名索引（QSM, WeQ, SOM, Ref, QEntL）
        module_idx = -1
        for idx, part in enumerate(old_parts):
            if part in self.main_modules:
                module_idx = idx
                break
        
        if module_idx == -1:
            return file_content  # 找不到模块名，不修改
        
        # 计算相对路径差异
        old_rel_path = '.'.join(old_parts[module_idx:])
        new_rel_path = '.'.join(new_parts[module_idx:])
        
        # 不包含文件扩展名
        old_rel_path = old_rel_path.replace('.py', '')
        new_rel_path = new_rel_path.replace('.py', '')
        
        # 替换导入语句
        import_patterns = [
            r'from\s+{0}\s+import'.format(re.escape(old_rel_path)),
            r'import\s+{0}'.format(re.escape(old_rel_path)),
            r'from\s+{0}'.format(re.escape(old_rel_path))
        ]
        
        updated_content = file_content
        for pattern in import_patterns:
            replacement = pattern.replace(old_rel_path, new_rel_path)
            updated_content = re.sub(pattern, replacement, updated_content)
        
        return updated_content
    
    def fix_triple_quotes(self, file_content: str) -> str:
        """
        修复未闭合的三引号问题
        
        Args:
            file_content: 文件内容
            
        Returns:
            修复后的文件内容
        """
        # 检查三引号数量
        quotes_count = file_content.count('"""')
        
        # 如果三引号数量为奇数，且包含量子纠缠相关标记，移除末尾的三引号
        if quotes_count % 2 != 0 and re.search(r'量子基因编码|纠缠状态|纠缠对象|纠缠强度', file_content):
            if file_content.rstrip().endswith('"""'):
                return file_content.rstrip()[:-3]
        
        return file_content
    
    def organize_file(self, filepath: str, apply: bool = False) -> Dict[str, Any]:
        """
        组织单个文件（确定目标位置并移动）
        
        Args:
            filepath: 文件路径
            apply: 是否应用更改
            
        Returns:
            包含操作结果的字典
        """
        result = {"from": filepath, "status": "unchanged", "message": ""}
        
        try:
            # 检查文件存在
            if not os.path.isfile(filepath):
                result["status"] = "error"
                result["message"] = "文件不存在"
                return result
            
            # 确定所属模块
            for module in self.main_modules:
                if module in filepath.split(os.sep):
                    module_name = module
                    break
            else:
                result["status"] = "unchanged"
                result["message"] = "不属于已知模块"
                return result
            
            # 确定目标目录
            target_subdir = self.determine_target_directory(filepath, module_name)
            if target_subdir is None:
                result["status"] = "unchanged"
                result["message"] = "特殊文件或无法确定目标目录"
                return result
            
            # 构建目标路径
            module_root = os.path.join(self.project_root, module_name)
            target_dir = os.path.join(module_root, target_subdir)
            target_path = os.path.join(target_dir, os.path.basename(filepath))
            
            # 目标文件已存在，不移动
            if os.path.samefile(filepath, target_path):
                result["status"] = "unchanged"
                result["message"] = "文件已在正确位置"
                return result
            
            if os.path.exists(target_path):
                result["status"] = "unchanged"
                result["message"] = "目标文件已存在"
                return result
            
            result["to"] = target_path
            result["status"] = "will_move"
            
            # 如果是模拟运行，到此为止
            if not apply:
                return result
            
            # 创建目标目录
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # 读取文件
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 修复三引号问题
            content = self.fix_triple_quotes(content)
            
            # 更新导入路径
            content = self.update_import_paths(content, Path(filepath), Path(target_path))
            
            # 写入新文件
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 删除原文件
            os.remove(filepath)
            
            result["status"] = "moved"
            
            # 如果启用了量子基因标记，记录文件移动
            if self.quantum_gene_marker:
                self.quantum_gene_marker.mark_file_movement(filepath, target_path)
            
            return result
            
        except Exception as e:
            result["status"] = "error"
            result["message"] = str(e)
            self.logger.error(f"组织文件失败 {filepath}: {str(e)}")
            return result
    
    def organize_module_files(self, module_name: str, apply: bool = False) -> Dict[str, Any]:
        """
        组织指定模块的文件
        
        Args:
            module_name: 模块名称
            apply: 是否应用更改
            
        Returns:
            包含操作结果的字典
        """
        results = {
            "module": module_name,
            "moved_files": [],
            "unchanged_files": [],
            "errors": []
        }
        
        if module_name not in self.main_modules:
            results["errors"].append(f"未知模块: {module_name}")
            return results
        
        module_dir = os.path.join(self.project_root, module_name)
        if not os.path.isdir(module_dir):
            results["errors"].append(f"模块目录不存在: {module_dir}")
            return results
        
        # 收集模块中的所有Python文件
        python_files = []
        for root, _, files in os.walk(module_dir):
            for file in files:
                if file.endswith('.py') or file.endswith('.qent') or file.endswith('.qentl'):
                    filepath = os.path.join(root, file)
                    python_files.append(filepath)
        
        for filepath in python_files:
            result = self.organize_file(filepath, apply)
            
            if result["status"] == "moved":
                results["moved_files"].append({
                    "from": result["from"],
                    "to": result["to"]
                })
            elif result["status"] == "will_move":
                results["moved_files"].append({
                    "from": result["from"],
                    "to": result["to"],
                    "note": "模拟运行，未实际移动"
                })
            elif result["status"] == "error":
                results["errors"].append(f"{filepath}: {result['message']}")
            else:
                results["unchanged_files"].append(filepath)
        
        return results
    
    def organize_all_modules(self, apply: bool = False) -> Dict[str, Any]:
        """
        组织所有模块的文件
        
        Args:
            apply: 是否应用更改
            
        Returns:
            包含操作结果的字典
        """
        results = {
            "modules": [],
            "total_moved": 0,
            "total_unchanged": 0,
            "total_errors": 0
        }
        
        for module in self.main_modules:
            module_result = self.organize_module_files(module, apply)
            
            results["modules"].append({
                "name": module,
                "moved": len(module_result["moved_files"]),
                "unchanged": len(module_result["unchanged_files"]),
                "errors": len(module_result["errors"])
            })
            
            results["total_moved"] += len(module_result["moved_files"])
            results["total_unchanged"] += len(module_result["unchanged_files"])
            results["total_errors"] += len(module_result["errors"])
        
        return results
    
    def process_powershell_cleanup(self, max_depth: int = 3) -> Dict[str, Any]:
        """
        进行PowerShell脚本中的清理任务（修复引号、检查语法）
        
        Args:
            max_depth: 最大处理深度
            
        Returns:
            包含操作结果的字典
        """
        results = {
            "processed_files": 0,
            "fixed_files": 0,
            "errors": []
        }
        
        def process_directory(dir_path, current_depth=1):
            if current_depth > max_depth:
                return
                
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                
                # 处理目录
                if os.path.isdir(item_path):
                    if item in self.standard_subdirs or current_depth == 1:
                        process_directory(item_path, current_depth + 1)
                    continue
                
                # 处理Python文件
                if item.endswith('.py'):
                    try:
                        # 创建备份
                        backup_path = os.path.join(
                            self.backup_dir, 
                            datetime.now().strftime('%Y%m%d_%H%M%S'),
                            os.path.relpath(item_path, self.project_root)
                        )
                        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                        shutil.copy2(item_path, backup_path)
                        
                        # 读取文件
                        with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # 修复三引号
                        fixed_content = self.fix_triple_quotes(content)
                        
                        results["processed_files"] += 1
                        
                        # 如果内容有变化，写回文件
                        if fixed_content != content:
                            with open(item_path, 'w', encoding='utf-8') as f:
                                f.write(fixed_content)
                            results["fixed_files"] += 1
                            
                    except Exception as e:
                        results["errors"].append(f"{item_path}: {str(e)}")
        
        # 处理各模块目录
        for module in self.main_modules:
            module_dir = os.path.join(self.project_root, module)
            if os.path.isdir(module_dir):
                process_directory(module_dir)
        
        return results


def get_fs_manager(project_root: str = None) -> FileSystemManager:
    """
    获取文件系统管理器的单例实例
    
    Args:
        project_root: 项目根目录
        
    Returns:
        文件系统管理器实例
    """
    global _fs_manager_instance
    
    if _fs_manager_instance is None:
        _fs_manager_instance = FileSystemManager(project_root)
        
    return _fs_manager_instance


if __name__ == "__main__":
    import argparse
    
    # 定义命令行参数
    parser = argparse.ArgumentParser(description='QSM项目文件系统管理工具')
    parser.add_argument('--create-dirs', action='store_true', help='创建标准目录结构')
    parser.add_argument('--organize', type=str, help='组织指定模块的文件')
    parser.add_argument('--organize-all', action='store_true', help='组织所有模块的文件')
    parser.add_argument('--clean', action='store_true', help='清理空目录')
    parser.add_argument('--analyze', action='store_true', help='分析项目结构')
    parser.add_argument('--merge', type=str, help='合并目录 (源目录:目标目录)')
    parser.add_argument('--apply', action='store_true', help='应用更改（默认为模拟运行）')
    parser.add_argument('--fix-quotes', action='store_true', help='修复文件中未闭合的三引号问题')
    parser.add_argument('--port', type=int, default=0, help='启动API服务的端口（0表示不启动）')
    parser.add_argument('--gui', action='store_true', help='启动GUI界面')
    parser.add_argument('--output', type=str, help='输出文件路径')
    
    args = parser.parse_args()
    
    # 获取文件系统管理器
    fs_manager = get_fs_manager()
    
    # 执行操作
    if args.create_dirs:
        results = fs_manager.create_standard_structure()
        print(f"创建标准目录结构完成:")
        print(f"- 创建了 {len(results['created_dirs'])} 个目录")
        for dir_path in results['created_dirs']:
            print(f"  - {dir_path}")
        print(f"- 已存在 {len(results['existing_dirs'])} 个目录")
        print(f"- 发生 {len(results['errors'])} 个错误")
    
    if args.organize:
        results = fs_manager.organize_module_files(args.organize, args.apply)
        print(f"组织模块 {args.organize} 的文件完成:")
        print(f"- 移动了 {len(results['moved_files'])} 个文件")
        print(f"- 保持不变 {len(results['unchanged_files'])} 个文件")
        print(f"- 发生 {len(results['errors'])} 个错误")
        
        if not args.apply:
            print("注意: 这是模拟运行，未实际移动文件。使用 --apply 参数执行实际移动。")
    
    if args.organize_all:
        results = fs_manager.organize_all_modules(args.apply)
        print(f"组织所有模块的文件完成:")
        print(f"- 总共移动 {results['total_moved']} 个文件")
        print(f"- 总共保持不变 {results['total_unchanged']} 个文件")
        print(f"- 总共发生 {results['total_errors']} 个错误")
        
        for module in results['modules']:
            print(f"- {module['name']}: 移动 {module['moved']}, 不变 {module['unchanged']}, 错误 {module['errors']}")
        
        if not args.apply:
            print("注意: 这是模拟运行，未实际移动文件。使用 --apply 参数执行实际移动。")
    
    if args.clean:
        results = fs_manager.clean_empty_directories()
        print(f"清理空目录完成，删除了 {len(results['deleted'])} 个目录:")
        for i, dir_path in enumerate(results['deleted'], 1):
            print(f"  {i}. {dir_path}")
    
    if args.analyze:
        report = fs_manager.analyze_project_structure()
        print(f"项目结构分析完成")
        
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"分析报告已保存至: {args.output}")
            except Exception as e:
                print(f"保存报告失败: {str(e)}")
        else:
            print(f"项目根目录: {report['project_root']}")
            print(f"总文件数: {report['file_counts']['total']}")
            print(f"总目录数: {report['directory_counts']['total']}")
            
            print("\n模块概况:")
            for module, module_info in report['modules'].items():
                print(f"- {module}: {module_info['file_count']} 文件, {module_info['directory_count']} 目录")
                if 'missing_standard_dirs' in module_info and module_info['missing_standard_dirs']:
                    print(f"  缺失目录: {', '.join(module_info['missing_standard_dirs'])}")
    
    if args.merge:
        try:
            source_dir, target_dir = args.merge.split(':')
            source_dir = os.path.abspath(source_dir)
            target_dir = os.path.abspath(target_dir)
            
            success = fs_manager.merge_directories(source_dir, target_dir, move_files=True)
            
            if success:
                print(f"成功合并目录:")
                print(f"- 从: {source_dir}")
                print(f"- 到: {target_dir}")
            else:
                print(f"合并目录失败")
        except ValueError:
            print("错误: 合并参数格式应为 '源目录:目标目录'")
    
    if args.fix_quotes:
        results = fs_manager.process_powershell_cleanup()
        print(f"修复三引号问题完成:")
        print(f"- 处理了 {results['processed_files']} 个文件")
        print(f"- 修复了 {results['fixed_files']} 个文件")
        print(f"- 发生 {len(results['errors'])} 个错误")
        
        if results['errors']:
            print("\n错误:")
            for error in results['errors']:
                print(f"- {error}")
    
    # 启动API服务
    if args.port > 0:
        try:
            # 尝试导入Ref API集成模块
            from Ref.api.ref_api_integration import start_fs_manager_api
            print(f"启动文件系统管理器API服务，端口: {args.port}")
            start_fs_manager_api(fs_manager, port=args.port)
        except ImportError as e:
            print(f"启动API服务失败: {str(e)}")
    
    # 启动GUI界面
    if args.gui:
        try:
            # 尝试导入Ref GUI模块
            from Ref.QEntL.qent.fs_manager_gui import start_gui
            print("启动文件系统管理器GUI界面")
            start_gui(fs_manager)
        except ImportError as e:
            print(f"启动GUI界面失败: {str(e)}")
    
    # 如果没有指定任何操作，显示帮助信息
    if not any([args.create_dirs, args.organize, args.organize_all, args.clean, 
                args.analyze, args.merge, args.fix_quotes, args.port > 0, args.gui]):
        parser.print_help() 