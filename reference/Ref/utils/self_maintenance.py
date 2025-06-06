#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ref 系统自维护模块

本模块为 Ref 系统提供自我修复和维护功能，集成了量子标记修复、环境文件修复
和量子基因统计分析功能。

通过 QEntL 量子纠缠语言实现自动化修复和维护，确保系统整体稳定性。
"""

import os
import sys
import re
import logging
import importlib.util
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Union, Optional, Tuple
import threading
import time
import shutil

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(PROJECT_ROOT, ".logs", "ref_maintenance.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RefMaintenance")

# 量子标记模式
QUANTUM_MARKER_PATTERNS = [
    r'量子基因编码',  # Quantum Gene Encoding
    r'量子纠缠',      # Quantum Entanglement
    r'量子通信',      # Quantum Communication
    r'量子标记',      # Quantum Marker
]

# 确保日志目录存在
def ensure_logs_dir():
    """确保日志目录存在"""
    logs_dir = PROJECT_ROOT / ".logs"
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
        logger.info(f"创建日志目录: {logs_dir}")


class RefSelfMaintenance:
    """Ref系统自维护类，集成各种维护功能"""
    
    def __init__(self, project_root: Union[str, Path] = None):
        """
        初始化自维护系统
        
        Args:
            project_root: 项目根目录路径
"""
        self.project_root = Path(project_root) if project_root else PROJECT_ROOT
        self.maintenance_dir = self.project_root / "maintenance"
        self.ref_dir = self.project_root / "Ref"
        self.qentl_dir = self.project_root / "QEntL"
        
        # 确保日志目录存在
        ensure_logs_dir()
        
        # 维护工具路径
        self.quantum_fixer_path = self.maintenance_dir / "fix_quantum_markers.py"
        self.comment_fixer_path = self.maintenance_dir / "fix_comments.py"
        
        logger.info(f"初始化Ref自维护系统，项目根目录: {self.project_root}")
        
        # 检查维护工具是否存在
        self._check_maintenance_tools()
    
    def _check_maintenance_tools(self):
        """检查必要的维护工具是否存在"""
        if not self.maintenance_dir.exists():
            logger.warning(f"维护工具目录不存在: {self.maintenance_dir}")
            return False
        
        missing_tools = []
        
        if not self.quantum_fixer_path.exists():
            missing_tools.append(str(self.quantum_fixer_path))
        
        if not self.comment_fixer_path.exists():
            missing_tools.append(str(self.comment_fixer_path))
        
        if missing_tools:
            logger.warning(f"缺少维护工具: {', '.join(missing_tools)}")
            return False
        
        logger.info("所有维护工具已找到")
        return True
    
    def fix_quantum_markers_in_file(self, file_path: Union[str, Path]) -> bool:
"""
        修复文件中的量子标记
        
        Args:
            file_path: 需要修复的文件路径
            
        Returns:
            bool: 修复是否成功
"""
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return False
        
        try:
            # 使用QEntL语言的特性处理量子标记
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # 检查是否包含量子标记
            has_marker = False
            for pattern in QUANTUM_MARKER_PATTERNS:
                if re.search(pattern, content):
                    has_marker = True
                    break
            
            if not has_marker:
                logger.debug(f"文件中没有量子标记: {file_path}")
                return False
            
            # 修复量子标记
            fixed_content = self._fix_quantum_markers(content)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            logger.info(f"成功修复文件中的量子标记: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"修复文件时出错 {file_path}: {str(e)}")
            return False
    
    def _fix_quantum_markers(self, content: str) -> str:
"""
        修复内容中的量子标记
        
        Args:
            content: 包含量子标记的内容
            
        Returns:
            str: 修复后的内容
"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 检查行是否包含量子标记
            has_marker = False
            for pattern in QUANTUM_MARKER_PATTERNS:
                if pattern in line:
                    has_marker = True
                    break
            
            if has_marker:
                # 如果已经是注释，保持原样
                if line.strip().startswith('#'):
                    fixed_lines.append(line)
                else:
                    # 提取代码和标记部分
                    code_part = ''
                    marker_part = ''
                    
                    # 简单情况：标记在开头或结尾
                    for pattern in QUANTUM_MARKER_PATTERNS:
                        if line.startswith(pattern):
                            marker_part = pattern
                            code_part = line[len(pattern):].strip()
                            break
                        elif line.endswith(pattern):
                            marker_part = pattern
                            code_part = line[:-len(pattern)].strip()
                            break
                    
                    # 更复杂的情况：标记在中间
                    if not marker_part:
                        for pattern in QUANTUM_MARKER_PATTERNS:
                            if pattern in line:
                                parts = line.split(pattern)
                                code_part = parts[0].strip()
                                marker_part = pattern
                                # 包含标记后的任何内容作为注释
                                if len(parts) > 1 and parts[1].strip():
                                    marker_part += ' ' + parts[1].strip()
                    
                    # 创建修复后的行
                    if code_part:
                        # 代码存在，将标记添加为注释
                        fixed_lines.append(f"{code_part}  # {marker_part}")
                    else:
                        # 只有标记存在，将其变为注释
                        fixed_lines.append(f"# {marker_part}")
            else:
                # 没有量子标记，保持原样
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_all_python_files(self, directory: Union[str, Path] = None) -> Tuple[int, int]:
"""
        修复目录中所有Python文件的量子标记
        
        Args:
            directory: 要处理的目录，默认为项目根目录
            
        Returns:
            Tuple[int, int]: (处理的文件数，修复的文件数)
"""
        if directory is None:
            directory = self.project_root
        
        directory = Path(directory)
        if not directory.exists():
            logger.error(f"目录不存在: {directory}")
            return 0, 0
        
        processed_files = 0
        fixed_files = 0
        
        logger.info(f"开始处理目录中的所有Python文件: {directory}")
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(('.py', '.pyw', '.pyi')):
                    file_path = Path(root) / file
                    processed_files += 1
                    
                    if self.fix_quantum_markers_in_file(file_path):
                        fixed_files += 1
        
        logger.info(f"处理了 {processed_files} 个Python文件，修复了 {fixed_files} 个文件")
        return processed_files, fixed_files
    
    def fix_virtual_env_files(self) -> int:
"""
        修复虚拟环境中的量子标记问题
        
        Returns:
            int: 修复的文件数
"""
        logger.info("开始修复虚拟环境中的文件")
        
        # 检查虚拟环境
        venv_path = None
        if (self.project_root / ".venv").exists():
            venv_path = self.project_root / ".venv"
        elif (self.project_root / "venv").exists():
            venv_path = self.project_root / "venv"
        
        if venv_path is None:
            logger.error("找不到虚拟环境目录")
            return 0
        
        # 获取site-packages目录
        site_packages = None
        if sys.platform.startswith('win'):
            site_packages = venv_path / "Lib" / "site-packages"
        else:
            # 查找Python版本目录
            lib_dir = venv_path / "lib"
            if lib_dir.exists():
                python_dirs = [d for d in lib_dir.iterdir() if d.name.startswith("python")]
                if python_dirs:
                    site_packages = python_dirs[0] / "site-packages"
        
        if not site_packages or not site_packages.exists():
            logger.error(f"找不到site-packages目录: {site_packages}")
            return 0
        
        # 修复已知问题包
        fixed_files = 0
        problem_packages = ["pip", "setuptools"]
        
        for package in problem_packages:
            package_dir = site_packages / package
            if package_dir.exists():
                logger.info(f"修复包 {package}")
                _, fixed = self.fix_all_python_files(package_dir)
                fixed_files += fixed
        
        # 特别处理pip/_vendor/rich目录
        rich_dir = site_packages / "pip" / "_vendor" / "rich"
        if rich_dir.exists():
            logger.info(f"修复 pip/_vendor/rich 目录")
            _, fixed = self.fix_all_python_files(rich_dir)
            fixed_files += fixed
        
        # 修复pywin32_bootstrap.py
        if sys.platform.startswith('win'):
            bootstrap_file = site_packages / "pywin32_bootstrap.py"
            if bootstrap_file.exists():
                logger.info(f"修复 pywin32_bootstrap.py")
                if self.fix_quantum_markers_in_file(bootstrap_file):
                    fixed_files += 1
        
        logger.info(f"虚拟环境文件修复完成，共修复 {fixed_files} 个文件")
        return fixed_files
    
    def fix_file_with_python(self, file_path: Union[str, Path]) -> bool:
"""
        使用Python脚本修复文件
        
        Args:
            file_path: 要修复的文件路径
            
        Returns:
            bool: 修复是否成功
"""
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return False
        
        try:
            # 使用fix_quantum_markers.py脚本修复文件
            result = subprocess.run(
                [sys.executable, str(self.quantum_fixer_path), str(file_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"修复文件失败: {file_path}")
                logger.error(f"错误: {result.stderr}")
                return False
            
            logger.info(f"成功使用Python脚本修复文件: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"修复文件时出错 {file_path}: {str(e)}")
            return False
    
    def run_maintenance_cycle(self):
        """运行一个完整的维护周期"""
        logger.info("开始Ref系统维护周期")
        
        # 修复虚拟环境文件
        self.fix_virtual_env_files()
        
        # 修复Ref目录中的文件
        _, fixed_ref = self.fix_all_python_files(self.ref_dir)
        logger.info(f"修复了 {fixed_ref} 个Ref目录中的文件")
        
        # 修复QEntL目录中的文件
        _, fixed_qentl = self.fix_all_python_files(self.qentl_dir)
        logger.info(f"修复了 {fixed_qentl} 个QEntL目录中的文件")
        
        logger.info("Ref系统维护周期完成")
    
    def start_maintenance_thread(self, interval_hours: float = 6):
        """
        启动维护线程，定期运行维护周期
        
        Args:
            interval_hours: 维护周期间隔（小时）
"""
        def maintenance_loop():
            while True:
                try:
                    self.run_maintenance_cycle()
                except Exception as e:
                    logger.error(f"维护周期出错: {str(e)}")
                
                # 等待下一个维护周期
                logger.info(f"下一个维护周期将在 {interval_hours} 小时后运行")
                time.sleep(interval_hours * 3600)
        
        thread = threading.Thread(target=maintenance_loop, daemon=True)
        thread.start()
        logger.info(f"维护线程已启动，间隔时间: {interval_hours} 小时")
        return thread


def main():
    """主函数，用于直接执行时"""
    maintenance = RefSelfMaintenance()
    maintenance.run_maintenance_cycle()


if __name__ == "__main__":
    main() 

"""
    # 
"""
量子基因编码: QE-SEL-18814D11EC3B
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""
    