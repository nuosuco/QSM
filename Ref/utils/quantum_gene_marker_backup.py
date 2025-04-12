#!/usr/bin/env python
# -*- coding: utf-8 -*-

# # 
"""
量子基因编码: QE-QUA-17C456F10733
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""

"""
量子基因标记工具

提供对文件添加、更新和管理量子基因标记的功能
"""

import os
import re
import sys
import random
import hashlib
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union

# 设置日志记录器
logger = logging.getLogger("Ref.utils.quantum_gene_marker")

class RefQuantumGeneMarker:
    """量子基因标记处理器

    提供对文件添加、更新和搜索量子基因标记的功能
    支持多种文件类型和灵活的标记格式
    """

    # 支持的文件类型和对应的注释标记
    SUPPORTED_FILE_TYPES = {
        '.py': ['#', "'''", '"""'],
        '.js': ['//', '/*'],
        '.html': ['<!--'],
        '.css': ['/*'],
        '.java': ['//', '/*'],
        '.c': ['//', '/*'],
        '.cpp': ['//', '/*'],
        '.h': ['//', '/*'],
        '.hpp': ['//', '/*'],
        '.go': ['//', '/*'],
        '.rs': ['//', '/*'],
        '.scala': ['//', '/*'],
        '.php': ['//', '/*', '#'],
        '.rb': ['#', '=begin'],
        '.pl': ['#'],
        '.sh': ['#'],
        '.bat': ['REM', '::'],
        '.ps1': ['#'],
        '.yml': ['#'],
        '.yaml': ['#'],
        '.json': [],  # JSON不支持注释，但我们可能需要特殊处理
        '.md': ['<!--'],
        '.txt': ['#'],
        '.sql': ['--', '/*'],
        '.xml': ['<!--'],
        '.swift': ['//', '/*'],
        '.kt': ['//', '/*'],
        '.ts': ['//', '/*'],
        '.dart': ['//', '/*'],
        '.r': ['#'],
        '.lua': ['--', '--[['],
        '.dockerfile': ['#']
    }

    # 注释结束标记
    COMMENT_END_MARKERS = {
        "'''": "'''",
        '"""': '"""',
        '/*': '*/',
        '<!--': '-->',
        '=begin': '=end',
        '--[[': ']]'
    }

    # 量子基因模板
    GENE_TEMPLATE = """
# 
"""
量子基因编码: QE-QUA-17C456F10733
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

    def __init__(self):
        """初始化量子基因标记处理器"""
        self.last_generated_code = None
        # 尝试导入QEntL模块，如果可用
        try:
            import QEntL
            self.qentl_available = True
            logger.info("已找到QEntL工具模块，但将优先使用内部实现")
        except ImportError:
            self.qentl_available = False
            logger.debug("未找到QEntL工具模块，使用内部实现")

    def add_quantum_gene_marker(self, file_path: str) -> bool:
        """为文件添加量子基因标记
        
        Args:
            file_path: 要添加标记的文件路径
            
        Returns:
            是否成功添加标记
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False

            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查文件是否已有量子基因标记
            if self._has_gene_marker(content):
                logger.info(f"文件已有量子基因标记: {file_path}")
                return True

            # 生成基因编码
            gene_code = self._generate_gene_code(file_path)
            
            # 创建量子基因标记
            marker = self.GENE_TEMPLATE.format(
                gene_code=gene_code,
                entanglement_state="活跃",
                entangled_objects=[],
                entanglement_strength=0.98
            )

            # 获取文件注释标记
            comment_start, comment_end = self._get_comment_markers(file_path)
            
            # 如果是支持注释的文件类型，使用注释包装
            if comment_start:
                if comment_start in ['#', '//', '--', '::', 'REM']:
                    # 单行注释类型，每行添加前缀
                    formatted_marker = "\n".join([f"{comment_start} {line.strip()}" if line.strip() else "" 
                                                for line in marker.split('\n')])
                else:
                    # 块注释类型
                    formatted_marker = f"{comment_start}{marker}{comment_end}"
            else:
                # 不支持注释的文件类型，直接添加
                formatted_marker = marker

            # 在文件顶部（保留首行shebang或编码声明）添加标记
            lines = content.split('\n')
            insert_position = 0
            
            # 检查是否有shebang或编码声明
            if lines and (lines[0].startswith('#!') or 
                         (len(lines) > 1 and lines[1].startswith('# -*- coding'))):
                if lines[0].startswith('#!'):
                    insert_position = 1
                    if len(lines) > 1 and lines[1].startswith('# -*- coding'):
                        insert_position = 2

            # 插入标记
            new_content = '\n'.join(lines[:insert_position])
            if new_content and not new_content.endswith('\n'):
                new_content += '\n'
            new_content += formatted_marker
            if insert_position < len(lines):
                remaining_content = '\n'.join(lines[insert_position:])
                if formatted_marker and not formatted_marker.endswith('\n'):
                    new_content += '\n'
                new_content += remaining_content

            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            self.last_generated_code = gene_code
            logger.info(f"已添加量子基因标记到文件: {file_path}")
            return True

        except Exception as e:
            logger.error(f"添加量子基因标记时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return False

    def update_quantum_gene_marker(self, file_path: str, 
                                  entanglement_state: str = None,
                                  entangled_objects: List[str] = None,
                                  entanglement_strength: float = None) -> bool:
        """更新文件的量子基因标记
        
        Args:
            file_path: 要更新标记的文件路径
            entanglement_state: 新的纠缠状态
            entangled_objects: 新的纠缠对象列表
            entanglement_strength: 新的纠缠强度
            
        Returns:
            是否成功更新标记
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False

            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()

            # 找到量子基因标记位置
            marker_pos = self._find_gene_marker_position(file_content)
            if marker_pos == -1:
                logger.warning(f"文件没有量子基因标记: {file_path}")
                return False

            # 提取当前的量子基因编码
            pattern = r"# 
"""
量子基因编码: QE-QUA-17C456F10733
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
            
            current_state = state_match.group(1) if state_match else "活跃"
            current_strength = float(strength_match.group(1)) if strength_match else 0.98
            
            # 使用传入的新值或保留原值
            new_state = entanglement_state if entanglement_state is not None else current_state
            new_objects = entangled_objects if entangled_objects is not None else current_entangled_objects
            new_strength = entanglement_strength if entanglement_strength is not None else current_strength
            
            # 创建新的标记
            new_marker = self.GENE_TEMPLATE.format(
                gene_code=gene_code,
                entanglement_state=new_state,
                entangled_objects=new_objects,
                entanglement_strength=new_strength
            )
            
            # 获取注释标记
            comment_start, comment_end = self._get_comment_markers(file_path)
            
            # 根据文件类型格式化标记
            if comment_start in ['#', '//', '--', '::', 'REM']:
                # 单行注释类型
                formatted_new_marker = "\n".join([f"{comment_start} {line.strip()}" if line.strip() else "" 
                                               for line in new_marker.split('\n')])
            else:
                # 块注释类型
                formatted_new_marker = f"{comment_start}{new_marker}{comment_end}"
            
            # 查找整个标记块并替换
            # 尝试多种可能的模式来匹配整个标记块
            patterns = [
                r"# 
"""
量子基因编码: QE-QUA-17C456F10733
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
                r"/\*\s*# 
"""
量子基因编码: QE-QUA-17C456F10733
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
                r"<!--\s*# 
"""
量子基因编码: QE-QUA-17C456F10733
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
                r"'''\s*# 
"""
量子基因编码: QE-QUA-17C456F10733
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
                r"\"\"\"\s*# 
"""
量子基因编码: QE-QUA-17C456F10733
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
            ]
            
            # 尝试使用每种模式进行替换
            pattern = r"# 
"""
量子基因编码: QE-QUA-17C456F10733
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
            new_content = re.sub(pattern, new_marker, file_content, flags=re.DOTALL)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return True
        
        except Exception as e:
            logger.error(f"更新量子基因标记时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return False

    def scan_directory(self, directory: str, patterns: List[str] = None, recursive: bool = True) -> Dict[str, Any]:
        """扫描目录并为文件添加量子基因标记
        
        Args:
            directory: 要扫描的目录
            patterns: 文件匹配模式列表
            recursive: 是否递归扫描子目录
            
        Returns:
            包含扫描结果的字典
        """
        # 使用内部实现
        results = {
            'total_files': 0,
            'marked_files': 0,
            'errors': 0,
            'files': [],
            'details': []
        }
        
        if patterns is None:
            # 默认匹配所有支持的文件类型
            patterns = []
            for ext in self.SUPPORTED_FILE_TYPES.keys():
                patterns.append(f"*{ext}")
        
        # 使用Path.glob或Path.rglob扫描文件
        try:
            path = Path(directory)
            if not path.exists():
                raise FileNotFoundError(f"目录不存在: {directory}")
            
            # 创建文件列表
            files = []
            
            def should_skip_dir(dir_path):
                """检查是否应该跳过此目录（以点开头）"""
                # 获取目录名（不含路径）
                dir_name = os.path.basename(os.path.normpath(dir_path))
                # 如果目录名以点开头，且不是当前目录 (.) 或上级目录 (..)，则跳过
                return dir_name.startswith('.') and dir_name not in ['.', '..']
            
            if recursive:
                # 手动递归遍历目录，跳过以点开头的目录
                for root, dirs, found_files in os.walk(path):
                    # 修改dirs列表，移除以点开头的目录，防止进一步遍历
                    dirs[:] = [d for d in dirs if not should_skip_dir(d)]
                    
                    for file in found_files:
                        if any(file.endswith(ext) for ext in self.SUPPORTED_FILE_TYPES.keys()):
                            file_path = os.path.join(root, file)
                            files.append(Path(file_path))
            else:
                # 非递归模式，只检查当前目录
                for pattern in patterns:
                    for file_path in path.glob(pattern):
                        if file_path.is_file():
                            files.append(file_path)
            
            # 处理文件
            for file_path in files:
                file_str = str(file_path)
                results['total_files'] += 1
                
                try:
                    # 添加量子基因标记
                    if self.add_quantum_gene_marker(file_str):
                        results['marked_files'] += 1
                        results['files'].append(file_str)
                        results['details'].append({
                            'path': file_str,
                            'status': 'marked'
                        })
                except Exception as e:
                    results['errors'] += 1
                    results['details'].append({
                        'path': file_str,
                        'status': 'error',
                        'error': str(e)
                    })
                    
            return results
        except Exception as e:
            logger.error(f"扫描目录时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            results['errors'] += 1
            results['details'].append({
                'error': str(e)
            })
            return results

    def _generate_gene_code(self, file_path: str, prefix: str = "QE") -> str:
        """为给定文件生成量子基因编码
        
        Args:
            file_path: 文件路径
            prefix: 基因前缀
            
        Returns:
            生成的量子基因编码
        """
        # 获取文件名和路径信息
        path_obj = Path(file_path)
        file_name = path_obj.name
        file_stem = path_obj.stem.upper()
        
        # 创建基础哈希
        file_content_hash = ""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                file_content_hash = hashlib.md5(content).hexdigest().upper()[:12]
            else:
                # 对于新文件，使用时间戳
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                file_content_hash = hashlib.md5(timestamp.encode()).hexdigest().upper()[:12]
        except Exception as e:
            # 如果读取失败，使用随机值
            file_content_hash = ''.join(random.choice('0123456789ABCDEF') for _ in range(12))
            
        # 将哈希分成多个部分
        hash_parts = [file_content_hash[i:i+4] for i in range(0, len(file_content_hash), 4)]
        
        # 从文件名中提取模块标识符（最多3个字符）
        if len(file_stem) > 0:
            module_id = ''.join([c for c in file_stem if c.isalpha()])[:3]
        else:
            module_id = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(3))
            
        # 构建基因代码
        gene_code = f"{prefix}-{module_id}-{''.join(hash_parts)}"
        
        return gene_code

    def _get_comment_markers(self, file_path: str) -> tuple:
        """获取文件的注释开始和结束标记
        
        Args:
            file_path: 文件路径
            
        Returns:
            注释开始和结束标记的元组 (start, end)
        """
        ext = Path(file_path).suffix
        
        if ext in self.SUPPORTED_FILE_TYPES:
            # 对于支持的文件类型，使用首选注释标记
            comment_start = self.SUPPORTED_FILE_TYPES[ext][0]
            comment_end = self.COMMENT_END_MARKERS.get(comment_start, "")
            return comment_start, comment_end
            
        # 默认使用多行注释
        return '"""', '"""'

    def _has_gene_marker(self, content: str) -> bool:
        """检查内容是否已有量子基因标记
        
        Args:
            content: 文件内容
            
        Returns:
            是否已有标记
        """
        # 使用正则表达式检查是否存在量子基因标记
        pattern = r"# 量子基因编码: QE-[A-Z0-9-]+"
        return bool(re.search(pattern, content))

    def _find_gene_marker_position(self, content: str) -> int:
        """查找量子基因标记在内容中的位置
        
        Args:
            content: 文件内容
            
        Returns:
            标记位置的索引，如果未找到则返回-1
        """
        pattern = r"# 量子基因编码: (QE-[A-Z0-9-]+)"
        match = re.search(pattern, content)
        if match:
            return match.start()
        return -1

    def _parse_entangled_objects(self, content: str) -> List[str]:
        """从文件内容中提取纠缠对象列表
        
        Args:
            content: 文件内容
            
        Returns:
            纠缠对象列表
        """
        pattern = r"# 纠缠对象: \[(.*?)\]"
        match = re.search(pattern, content)
        if match:
            objects_str = match.group(1)
            # 解析对象列表
            if not objects_str.strip():
                return []
            
            # 尝试解析为Python列表
            try:
                # 确保是有效的Python语法
                objects_str = objects_str.replace("'", '"')
                objects_list = eval(f"[{objects_str}]")
                return objects_list
            except Exception:
                # 如果解析失败，使用简单的分割
                return [obj.strip() for obj in objects_str.split(',') if obj.strip()]
        return []

    def update_file_path(self, file_path: str, new_path: str) -> bool:
        """更新文件中引用的路径
        
        Args:
            file_path: 当前文件路径
            new_path: 新的文件路径
            
        Returns:
            是否成功更新路径
        """
        # 更新文件中的路径引用
        # 这是一个简化实现，实际应用中可能需要更复杂的逻辑
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
                
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 更新所有引用旧路径的地方
            old_path = os.path.normpath(file_path)
            new_path = os.path.normpath(new_path)
            
            # 替换文件路径（考虑不同的路径分隔符和引用样式）
            # 在Windows中，路径可能使用反斜杠或正斜杠
            old_path_variants = [
                old_path,
                old_path.replace('\\', '/'),
                old_path.replace('/', '\\')
            ]
            
            new_content = content
            for variant in old_path_variants:
                new_content = new_content.replace(f'"{variant}"', f'"{new_path}"')
                new_content = new_content.replace(f"'{variant}'", f"'{new_path}'")
                
            # 如果有变化，写回文件
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logger.info(f"已更新文件中的路径引用: {file_path}")
                return True
            else:
                logger.debug(f"文件中没有找到需要更新的路径引用: {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"更新文件路径时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return False

    def update_reference_path(self, file_path: str, old_reference: str, new_reference: str) -> bool:
        """更新文件中的引用路径
        
        Args:
            file_path: 要更新的文件路径
            old_reference: 旧的引用路径
            new_reference: 新的引用路径
            
        Returns:
            是否成功更新引用
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
                
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 替换各种可能的引用形式
            replacements = [
                (f'import {old_reference}', f'import {new_reference}'),
                (f'from {old_reference}', f'from {new_reference}'),
                (f'require("{old_reference}")', f'require("{new_reference}")'),
                (f"require('{old_reference}')", f"require('{new_reference}')"),
                (f'include "{old_reference}"', f'include "{new_reference}"'),
                (f'include <{old_reference}>', f'include <{new_reference}>'),
                (f'#include "{old_reference}"', f'#include "{new_reference}"'),
                (f'#include <{old_reference}>', f'#include <{new_reference}>'),
            ]
            
            new_content = content
            for old, new in replacements:
                new_content = new_content.replace(old, new)
                
            # 如果有变化，写回文件
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logger.info(f"已更新文件中的引用: {file_path}")
                return True
            else:
                logger.debug(f"文件中没有找到需要更新的引用: {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"更新引用路径时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return False

# 全局单例实例
_marker_instance = None

def get_marker_instance():
    """获取标记器的全局单例实例"""
    global _marker_instance
    if _marker_instance is None:
        _marker_instance = RefQuantumGeneMarker()
    return _marker_instance

# 便捷函数，供外部调用
def add_quantum_gene_marker(file_path: str) -> bool:
    """添加量子基因标记到文件"""
    marker = get_marker_instance()
    return marker.add_quantum_gene_marker(file_path)

def update_quantum_gene_marker(file_path: str, 
                              entanglement_state: str = None,
                              entangled_objects: List[str] = None,
                              entanglement_strength: float = None) -> bool:
    """更新文件的量子基因标记"""
    marker = get_marker_instance()
    return marker.update_quantum_gene_marker(
        file_path, 
        entanglement_state,
        entangled_objects,
        entanglement_strength
    )

def scan_and_mark_directory(directory: str, 
                           patterns: List[str] = None, 
                           recursive: bool = True) -> Dict[str, Any]:
    """扫描目录并为文件添加量子基因标记"""
    marker = get_marker_instance()
    return marker.scan_directory(directory, patterns, recursive)

def get_gene_marker():
    """获取量子基因标记处理器实例"""
    return get_marker_instance()

# 当作为脚本运行时的主函数
if __name__ == "__main__":
    # 设置基本的日志配置
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "mark" and len(sys.argv) > 2:
            # 给文件添加标记
            file_path = sys.argv[2]
            result = add_quantum_gene_marker(file_path)
            print(f"添加标记{'成功' if result else '失败'}: {file_path}")
        elif command == "update" and len(sys.argv) > 2:
            # 更新文件标记
            file_path = sys.argv[2]
            # 解析其他可选参数
            state = None
            objects = None
            strength = None
            
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--state" and i+1 < len(sys.argv):
                    state = sys.argv[i+1]
                    i += 2
                elif sys.argv[i] == "--objects" and i+1 < len(sys.argv):
                    objects = sys.argv[i+1].split(',')
                    i += 2
                elif sys.argv[i] == "--strength" and i+1 < len(sys.argv):
                    try:
                        strength = float(sys.argv[i+1])
                    except ValueError:
                        print(f"错误：无效的强度值 {sys.argv[i+1]}")
                        sys.exit(1)
                    i += 2
                else:
                    i += 1
            
            result = update_quantum_gene_marker(file_path, state, objects, strength)
            print(f"更新标记{'成功' if result else '失败'}: {file_path}")
        elif command == "scan" and len(sys.argv) > 2:
            # 扫描目录
            directory = sys.argv[2]
            recursive = True
            patterns = None
            
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--no-recursive":
                    recursive = False
                    i += 1
                elif sys.argv[i] == "--patterns" and i+1 < len(sys.argv):
                    patterns = sys.argv[i+1].split(',')
                    i += 2
                else:
                    i += 1
            
            result = scan_and_mark_directory(directory, patterns, recursive)
            print(f"扫描目录完成: {directory}")
            print(f"总文件数: {result['total_files']}")
            print(f"标记文件数: {result['marked_files']}")
            print(f"错误数: {result['errors']}")
        else:
            print("使用方法:")
            print("  python quantum_gene_marker.py mark <file_path>")
            print("  python quantum_gene_marker.py update <file_path> [--state <state>] [--objects obj1,obj2] [--strength <value>]")
            print("  python quantum_gene_marker.py scan <directory> [--no-recursive] [--patterns *.py,*.js]")
    else:
        print("量子基因标记工具")
        print("使用方法:")
        print("  python quantum_gene_marker.py mark <file_path>")
        print("  python quantum_gene_marker.py update <file_path> [--state <state>] [--objects obj1,obj2] [--strength <value>]")
        print("  python quantum_gene_marker.py scan <directory> [--no-recursive] [--patterns *.py,*.js]")

