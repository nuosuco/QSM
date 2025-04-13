#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
项目组织监控器

该模块提供项目结构监控和维护功能，确保项目目录结构符合标准，
并自动修复文件位置和路径引用问题。
"""

import os
import sys
import re
import shutil
import logging
import json
from pathlib import Path
from datetime import datetime
import difflib
from typing import Dict, List, Set, Tuple, Any, Optional, Union

# 设置路径
current_dir = os.path.dirname(os.path.abspath(__file__))
ref_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(ref_dir)
os.chdir(root_dir)  # 将工作目录设置为项目根目录

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(root_dir, '.logs', 'project_organizer.log'), 'a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('项目组织监控器')

# 尝试导入量子基因标记功能
try:
    from Ref.utils.quantum_gene_marker import RefQuantumGeneMarker
    quantum_marker = RefQuantumGeneMarker()
    logger.info("成功导入量子基因标记模块")
except ImportError:
    logger.warning("无法导入量子基因标记模块，部分功能将不可用")
    quantum_marker = None

class ProjectStructure:
    """项目结构定义类"""
    
    # 标准目录结构
    STANDARD_DIRECTORIES = {
        'QSM': [
            'api', 'core', 'models', 'scripts/services', 
            'tests', 'utils', 'docs'
        ],
        'WeQ': [
            'api', 'core', 'models', 'scripts/services', 
            'train', 'inference', 'tests', 'utils', 'docs'
        ],
        'SOM': [
            'api', 'core', 'models', 'scripts/services',
            'market', 'wallet', 'tests', 'utils', 'docs'
        ],
        'Ref': [
            'api', 'core', 'models', 'scripts/services', 
            'monitor', 'utils', 'repair', 'tests', 'docs'
        ],
        'scripts': ['services'],
        'docs': [
            'QSM', 'WeQ', 'SOM', 'Ref', 'scripts',
            'architecture', 'api', 'deployment'
        ]
    }
    
    # 应该移动到特定目录的文件模式
    FILE_PATTERNS = {
        r'.*_start_services\.py$': 'scripts/services',
        r'.*_stop_services\.py$': 'scripts/services',
        r'.*_api\.py$': 'api',
        r'.*_core\.py$': 'core',
        r'.*_train\.py$': '{module}/train',
        r'.*_inference\.py$': '{module}/inference',
        r'.*_monitor\.py$': '{module}/monitor',
        r'.*_repair\.py$': '{module}/repair',
        r'.*_test\.py$': 'tests',
        r'.*_utils\.py$': 'utils'
    }
    
    @staticmethod
    def get_expected_doc_path(code_file: str) -> str:
        """根据代码文件路径获取对应的文档文件路径"""
        code_path = Path(code_file)
        
        # 如果是模块内的文件
        for module in ['QSM', 'WeQ', 'SOM', 'Ref']:
            if module in code_path.parts:
                # 找到模块在路径中的位置
                module_index = code_path.parts.index(module)
                # 构建文档路径 - 将模块作为docs下的子目录
                doc_parts = ['docs'] + list(code_path.parts[module_index:])
                doc_path = Path(*doc_parts).with_suffix('.md')
                return str(doc_path)
        
        # 如果是scripts目录下的文件
        if 'scripts' in code_path.parts:
            scripts_index = code_path.parts.index('scripts')
            doc_parts = ['docs', 'scripts'] + list(code_path.parts[scripts_index+1:])
            doc_path = Path(*doc_parts).with_suffix('.md')
            return str(doc_path)
        
        # 如果是其他目录的文件，直接放在docs下对应路径
        doc_path = Path('docs', *code_path.parts).with_suffix('.md')
        return str(doc_path)
    
    @staticmethod
    def get_expected_code_path(doc_file: str) -> str:
        """根据文档文件路径获取对应的代码文件路径"""
        doc_path = Path(doc_file)
        
        # 确保文档文件在docs目录下
        if 'docs' not in doc_path.parts:
            logger.warning(f"文档文件不在docs目录下: {doc_file}")
            return None
        
        # 找到docs在路径中的位置
        docs_index = doc_path.parts.index('docs')
        
        # 构建代码文件路径 - 移除docs部分
        code_parts = list(doc_path.parts[:docs_index]) + list(doc_path.parts[docs_index+1:])
        code_path = Path(*code_parts).with_suffix('.py')
        
        return str(code_path)

class ProjectOrganizer:
    """项目组织监控器类"""
    
    def __init__(self, root_dir=None):
        """初始化项目组织监控器"""
        self.root_dir = Path(root_dir) if root_dir else Path(os.getcwd())
        self.structure = ProjectStructure()
        self.logger = logging.getLogger('项目组织监控器')
        
        # 初始化量子基因标记处理器
        self.quantum_marker = quantum_marker
        
        # 创建必要的目录
        os.makedirs(os.path.join(self.root_dir, '.logs'), exist_ok=True)
        
        self.logger.info(f"项目组织监控器已初始化，根目录: {self.root_dir}")
    
    def scan_project(self) -> Dict:
        """扫描项目结构，返回当前状态报告"""
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'root_dir': str(self.root_dir),
            'missing_directories': [],
            'misplaced_files': [],
            'unsynced_docs': [],
            'missing_markers': [],
            'path_reference_issues': []
        }
        
        # 检查缺失的标准目录
        for module, subdirs in self.structure.STANDARD_DIRECTORIES.items():
            module_dir = self.root_dir / module
            if not module_dir.exists():
                report['missing_directories'].append(str(module_dir))
                continue
                
            for subdir in subdirs:
                subdir_path = module_dir / subdir
                if not subdir_path.exists():
                    report['missing_directories'].append(str(subdir_path))
        
        # 扫描文件位置问题
        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)
            
            # 跳过隐藏目录和虚拟环境
            if any(part.startswith('.') for part in root_path.parts) or '.venv' in root_path.parts:
                continue
            
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                file_path = root_path / file
                rel_path = file_path.relative_to(self.root_dir)
                
                # 检查文件是否应该位于其他位置
                expected_location = self._get_expected_location(str(rel_path))
                if expected_location and str(rel_path) != expected_location:
                    report['misplaced_files'].append({
                        'current_path': str(rel_path),
                        'expected_path': expected_location
                    })
                
                # 检查是否有对应的文档文件
                doc_path = self.structure.get_expected_doc_path(str(rel_path))
                if doc_path and not (self.root_dir / doc_path).exists():
                    report['unsynced_docs'].append({
                        'code_file': str(rel_path),
                        'missing_doc': doc_path
                    })
                
                # 检查量子基因标记
                if self.quantum_marker and self._should_have_marker(str(rel_path)):
                    has_marker = self.quantum_marker.has_quantum_gene_marker(str(file_path))
                    if not has_marker:
                        report['missing_markers'].append(str(rel_path))
                
                # 检查路径引用问题
                if file.endswith('.py'):
                    path_issues = self._check_path_references(file_path)
                    if path_issues:
                        report['path_reference_issues'].extend(path_issues)
        
        return report
    
    def fix_project_structure(self, auto_fix=False) -> Dict:
        """修复项目结构问题，返回修复结果"""
        report = self.scan_project()
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'created_directories': [],
            'moved_files': [],
            'synced_docs': [],
            'added_markers': [],
            'fixed_references': []
        }
        
        # 创建缺失的目录
        for dir_path in report['missing_directories']:
            try:
                if auto_fix:
                    os.makedirs(dir_path, exist_ok=True)
                    results['created_directories'].append(dir_path)
                    self.logger.info(f"已创建目录: {dir_path}")
                else:
                    self.logger.info(f"需要创建目录: {dir_path}")
            except Exception as e:
                self.logger.error(f"创建目录失败: {dir_path} - {str(e)}")
        
        # 移动位置不正确的文件
        for file_info in report['misplaced_files']:
            try:
                current_path = self.root_dir / file_info['current_path']
                expected_path = self.root_dir / file_info['expected_path']
                
                if auto_fix:
                    # 确保目标目录存在
                    os.makedirs(expected_path.parent, exist_ok=True)
                    
                    # 如果目标文件已存在，检查内容差异
                    if expected_path.exists():
                        # 比较两个文件的内容
                        with open(current_path, 'r', encoding='utf-8') as f1:
                            current_content = f1.readlines()
                        with open(expected_path, 'r', encoding='utf-8') as f2:
                            expected_content = f2.readlines()
                            
                        # 如果内容不同，备份现有文件
                        if current_content != expected_content:
                            backup_path = expected_path.with_suffix(f'.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}')
                            shutil.copy2(expected_path, backup_path)
                            self.logger.info(f"已备份现有文件: {expected_path} -> {backup_path}")
                    
                    # 移动文件
                    shutil.move(current_path, expected_path)
                    results['moved_files'].append({
                        'from': str(file_info['current_path']),
                        'to': str(file_info['expected_path'])
                    })
                    self.logger.info(f"已移动文件: {current_path} -> {expected_path}")
                    
                    # 如果有量子基因标记，更新它
                    if self.quantum_marker and self.quantum_marker.has_quantum_gene_marker(expected_path):
                        self.quantum_marker.update_file_path(expected_path, current_path)
                else:
                    self.logger.info(f"需要移动文件: {current_path} -> {expected_path}")
            except Exception as e:
                self.logger.error(f"移动文件失败: {current_path} -> {expected_path} - {str(e)}")
        
        # 同步文档文件
        for doc_info in report['unsynced_docs']:
            try:
                code_path = self.root_dir / doc_info['code_file']
                doc_path = self.root_dir / doc_info['missing_doc']
                
                if auto_fix:
                    # 确保文档目录存在
                    os.makedirs(doc_path.parent, exist_ok=True)
                    
                    # 创建对应的文档文件
                    self._create_doc_from_code(code_path, doc_path)
                    results['synced_docs'].append({
                        'code_file': doc_info['code_file'],
                        'doc_file': doc_info['missing_doc']
                    })
                    self.logger.info(f"已创建文档文件: {doc_path}")
                else:
                    self.logger.info(f"需要创建文档文件: {doc_path}")
            except Exception as e:
                self.logger.error(f"创建文档文件失败: {doc_path} - {str(e)}")
        
        # 添加缺少的量子基因标记
        if self.quantum_marker:
            for file_path in report['missing_markers']:
                try:
                    full_path = self.root_dir / file_path
                    
                    if auto_fix:
                        # 获取对应的文档文件路径
                        doc_path = self.structure.get_expected_doc_path(str(file_path))
                        entangled_objects = [doc_path] if doc_path and (self.root_dir / doc_path).exists() else []
                        
                        # 添加量子基因标记
                        success = self.quantum_marker.add_quantum_gene_marker(
                            full_path, 
                            entangled_objects=entangled_objects,
                            strength=0.95
                        )
                        
                        if success:
                            results['added_markers'].append(str(file_path))
                            self.logger.info(f"已添加量子基因标记: {file_path}")
                    else:
                        self.logger.info(f"需要添加量子基因标记: {file_path}")
                except Exception as e:
                    self.logger.error(f"添加量子基因标记失败: {file_path} - {str(e)}")
        
        # 修复路径引用问题
        for issue in report['path_reference_issues']:
            try:
                file_path = self.root_dir / issue['file']
                
                if auto_fix:
                    self._fix_path_reference(file_path, issue['line'], issue['current'], issue['expected'])
                    results['fixed_references'].append({
                        'file': issue['file'],
                        'line': issue['line'],
                        'from': issue['current'],
                        'to': issue['expected']
                    })
                    self.logger.info(f"已修复路径引用: {file_path}:{issue['line']} - {issue['current']} -> {issue['expected']}")
                else:
                    self.logger.info(f"需要修复路径引用: {file_path}:{issue['line']} - {issue['current']} -> {issue['expected']}")
            except Exception as e:
                self.logger.error(f"修复路径引用失败: {file_path}:{issue['line']} - {str(e)}")
        
        return results
    
    def create_docs_structure(self, auto_create=False) -> Dict:
        """创建与代码结构对应的文档结构"""
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'created_directories': [],
            'created_files': []
        }
        
        # 确保docs目录存在
        docs_dir = self.root_dir / 'docs'
        if not docs_dir.exists():
            if auto_create:
                os.makedirs(docs_dir, exist_ok=True)
                results['created_directories'].append(str(docs_dir))
                self.logger.info(f"已创建docs目录: {docs_dir}")
            else:
                self.logger.info(f"需要创建docs目录: {docs_dir}")
        
        # 创建各个模块的文档目录
        for module, subdirs in self.structure.STANDARD_DIRECTORIES.items():
            if module == 'docs':
                continue
                
            module_doc_dir = docs_dir / module
            if not module_doc_dir.exists():
                if auto_create:
                    os.makedirs(module_doc_dir, exist_ok=True)
                    results['created_directories'].append(str(module_doc_dir))
                    self.logger.info(f"已创建模块文档目录: {module_doc_dir}")
                else:
                    self.logger.info(f"需要创建模块文档目录: {module_doc_dir}")
        
        # 扫描代码文件，创建对应的文档文件
        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)
            
            # 跳过隐藏目录、虚拟环境和docs目录
            if any(part.startswith('.') for part in root_path.parts) or '.venv' in root_path.parts or 'docs' in root_path.parts:
                continue
            
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                file_path = root_path / file
                rel_path = file_path.relative_to(self.root_dir)
                
                # 获取对应的文档路径
                doc_path = self.structure.get_expected_doc_path(str(rel_path))
                if not doc_path:
                    continue
                    
                full_doc_path = self.root_dir / doc_path
                
                if not full_doc_path.exists():
                    if auto_create:
                        # 确保文档目录存在
                        os.makedirs(full_doc_path.parent, exist_ok=True)
                        
                        # 创建文档文件
                        self._create_doc_from_code(file_path, full_doc_path)
                        results['created_files'].append(str(doc_path))
                        self.logger.info(f"已创建文档文件: {full_doc_path}")
                    else:
                        self.logger.info(f"需要创建文档文件: {full_doc_path}")
        
        return results
    
    def _get_expected_location(self, file_path: str) -> Optional[str]:
        """根据文件名模式获取文件的预期位置"""
        file_path = Path(file_path)
        file_name = file_path.name
        
        # 检查文件是否已经在正确位置
        current_module = None
        for module in ['QSM', 'WeQ', 'SOM', 'Ref']:
            if module in file_path.parts:
                current_module = module
                break
        
        # 检查是否匹配任何模式
        for pattern, target_dir in self.structure.FILE_PATTERNS.items():
            if re.match(pattern, file_name):
                # 替换{module}占位符
                if '{module}' in target_dir:
                    if current_module:
                        target_dir = target_dir.replace('{module}', current_module)
                    else:
                        # 尝试从文件名推断模块
                        if file_name.startswith('qsm_'):
                            target_dir = target_dir.replace('{module}', 'QSM')
                        elif file_name.startswith('weq_'):
                            target_dir = target_dir.replace('{module}', 'WeQ')
                        elif file_name.startswith('som_'):
                            target_dir = target_dir.replace('{module}', 'SOM')
                        elif file_name.startswith('ref_'):
                            target_dir = target_dir.replace('{module}', 'Ref')
                        else:
                            continue  # 无法推断模块，跳过
                
                # 构建预期路径
                if current_module:
                    expected_path = Path(current_module) / target_dir / file_name
                else:
                    expected_path = Path(target_dir) / file_name
                
                # 如果期望路径与当前路径不同，返回期望路径
                if str(expected_path) != str(file_path):
                    return str(expected_path)
        
        return None
    
    def _should_have_marker(self, file_path: str) -> bool:
        """判断文件是否应该有量子基因标记"""
        # 检查是否是重要的Python文件
        if not file_path.endswith('.py'):
            return False
            
        # 跳过测试文件
        if 'test' in file_path.lower():
            return False
            
        # 跳过__init__.py文件
        if '__init__.py' in file_path:
            return False
        
        # 以下目录中的文件应该有量子基因标记
        important_dirs = ['api/', 'core/', 'services/', 'utils/']
        return any(d in file_path for d in important_dirs)
    
    def _check_path_references(self, file_path: Path) -> List[Dict]:
        """检查文件中的路径引用问题"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines):
                # 检查导入语句
                import_matches = re.finditer(r'(?:from|import)\s+([\w.]+)', line)
                for match in import_matches:
                    module_path = match.group(1)
                    
                    # 检查是否是相对导入
                    if module_path.startswith('.'):
                        continue
                    
                    # 检查是否是标准库
                    if self._is_standard_module(module_path.split('.')[0]):
                        continue
                    
                    # 检查项目模块引用
                    for module in ['QSM', 'WeQ', 'SOM', 'Ref']:
                        if module.lower() in module_path.lower() and not module_path.startswith(module):
                            # 可能需要更正为绝对导入
                            expected_path = module_path.replace(module.lower(), module)
                            issues.append({
                                'file': str(file_path.relative_to(self.root_dir)),
                                'line': i + 1,
                                'current': module_path,
                                'expected': expected_path,
                                'type': 'import'
                            })
                
                # 检查文件路径字符串
                path_matches = re.finditer(r'[\'"]([^\'"/\s]+/[^/\'"\\s]+)[\'"]', line)
                for match in path_matches:
                    path_str = match.group(1)
                    
                    # 检查是否包含反斜杠
                    if '\\' in path_str:
                        expected_path = path_str.replace('\\', '/')
                        issues.append({
                            'file': str(file_path.relative_to(self.root_dir)),
                            'line': i + 1,
                            'current': path_str,
                            'expected': expected_path,
                            'type': 'path'
                        })
        except Exception as e:
            self.logger.error(f"检查路径引用时出错: {file_path} - {str(e)}")
        
        return issues
    
    def _fix_path_reference(self, file_path: Path, line_num: int, current: str, expected: str) -> bool:
        """修复文件中的路径引用"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 行号从1开始，但列表索引从0开始
            line_idx = line_num - 1
            if line_idx < 0 or line_idx >= len(lines):
                self.logger.error(f"行号超出范围: {file_path}, 行 {line_num}")
                return False
            
            # 替换该行中的路径引用
            lines[line_idx] = lines[line_idx].replace(current, expected)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
        except Exception as e:
            self.logger.error(f"修复路径引用时出错: {file_path}, 行 {line_num} - {str(e)}")
            return False
    
    def _create_doc_from_code(self, code_path: Path, doc_path: Path) -> bool:
        """从代码文件创建或更新文档"""
        try:
            # 确保文档目录存在
            os.makedirs(doc_path.parent, exist_ok=True)
            
            # 读取代码文件
            with open(code_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # 提取文档内容
            doc_content = self._generate_doc_content(code_path, code_content)
            
            # 写入文档文件
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            self.logger.info(f"已创建/更新文档: {doc_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建文档失败: {doc_path} - {str(e)}")
            return False

    def _generate_doc_content(self, code_path: Path, code_content: str) -> str:
        """生成文档内容"""
        # 提取模块文档字符串
        doc_string = ""
        if '"""' in code_content:
            doc_parts = code_content.split('"""')
            if len(doc_parts) > 1:
                doc_string = doc_parts[1].strip()
        
        # 提取函数和类定义
        functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):', code_content)
        classes = re.findall(r'class\s+(\w+)[^\n]*:', code_content)
        
        # 生成文档内容
        content = [
            f"# {code_path.stem}",
            "",
            "## 模块说明",
            doc_string if doc_string else "暂无模块说明",
            "",
            "## 功能概述",
            "",
            "### 类",
            ""]
        
        for class_name in classes:
            content.append(f"- `{class_name}`")
        
        content.extend([
            "",
            "### 函数",
            ""])
        
        for func_name in functions:
            content.append(f"- `{func_name}`")
        
        content.extend([
            "",
            "## 依赖关系",
            "",
            "## 使用示例",
            "",
            "## 注意事项",
            "",
            f"*文档最后更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        return '\n'.join(content)

    @staticmethod
    def _is_standard_module(module_name: str) -> bool:
        """检查是否是Python标准库模块"""
        standard_modules = [
            'os', 'sys', 'time', 'datetime', 'math', 're', 'json', 'logging',
            'argparse', 'collections', 'copy', 'functools', 'itertools',
            'pathlib', 'random', 'shutil', 'subprocess', 'tempfile',
            'threading', 'traceback', 'unittest', 'warnings', 'io',
            'contextlib', 'string', 'types', 'typing', 'uuid', 'importlib',
            'queue', 'signal', 'socket', 'ssl', 'email', 'http', 'urllib',
            'tkinter', 'platform', 'configparser', 'inspect'
        ]
        return module_name in standard_modules

    def auto_fix_structure(self) -> Dict:
        """自动修复项目结构问题"""
        # 运行所有修复功能
        structure_report = self.fix_project_structure(auto_fix=True)
        docs_report = self.create_docs_structure(auto_create=True)
        
        # 同步所有文档
        self.sync_docs()
        
        # 合并报告
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'structure_fixes': structure_report,
            'docs_fixes': docs_report
        }
        
        return report

    def sync_docs(self):
        """同步所有代码文件的文档"""
        synced_files = []
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py'):
                    code_path = Path(root) / file
                    doc_path = self.structure.get_expected_doc_path(str(code_path))
                    if doc_path:
                        if self._create_doc_from_code(code_path, Path(doc_path)):
                            synced_files.append(str(doc_path))
        
        return synced_files

# 创建单例实例
_project_organizer = None

def get_project_organizer(root_dir=None):
    """获取项目组织监控器实例（单例模式）"""
    global _project_organizer
    if _project_organizer is None:
        _project_organizer = ProjectOrganizer(root_dir)
    return _project_organizer

def scan_project():
    """扫描项目结构，返回当前状态报告"""
    organizer = get_project_organizer()
    return organizer.scan_project()

def fix_project_structure(auto_fix=False):
    """修复项目结构问题，返回修复结果"""
    organizer = get_project_organizer()
    return organizer.fix_project_structure(auto_fix)

def create_docs_structure(auto_create=False):
    """创建与代码结构对应的文档结构"""
    organizer = get_project_organizer()
    return organizer.create_docs_structure(auto_create)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="项目组织监控器")
    parser.add_argument('--scan', action='store_true', help='扫描项目结构')
    parser.add_argument('--fix', action='store_true', help='修复项目结构问题')
    parser.add_argument('--sync-docs', action='store_true', help='同步项目文档')
    parser.add_argument('--check-deps', action='store_true', help='检查项目依赖')
    parser.add_argument('--report', type=str, help='生成报告文件')
    args = parser.parse_args()
    
    organizer = ProjectOrganizer()
    
    if args.fix:
        report = organizer.auto_fix_structure()
    elif args.scan:
        report = organizer.scan_project()
    elif args.sync_docs:
        report = {'synced_files': organizer.sync_docs()}
    elif args.check_deps:
        report = organizer.check_dependencies()
    else:
        parser.print_help()
        return
    
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

"""
量子基因编码: QE-ORG-REF-O7M2P9V2
纠缠状态: 活跃
纠缠对象: ['QSM/scripts/services/QSM_start_services.py', 'WeQ/scripts/services/WeQ_start_services.py', 
          'SOM/scripts/services/SOM_start_services.py', 'Ref/scripts/services/Ref_start_services.py']
纠缠强度: 0.95
""" 