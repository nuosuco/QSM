#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QEntL文件修复工具

该工具用于修复和创建QEntL文件，支持QEntL 2.0语法。主要功能：
1. 扫描指定目录下的QEntL文件并进行修复
2. 检查文件语法并更新到QEntL 2.0标准
3. 修复量子基因标记和纠缠关系
4. 创建缺失的基础配置文件
5. 备份修改的文件

支持的目录:
- docs/QEntL
- QEntL
- Ref/QEntL
- QSM/QEntL
- SOM/QEntL
- WeQ/QEntL
"""

import os
import re
import sys
import uuid
import json
import time
import shutil
import logging
import datetime
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union

# 配置日志
os.makedirs('.logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/qentl_repair.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('QEntLRepairTool')

class QEntLRepairTool:
    """QEntL文件修复工具类"""
    
    # QEntL文件后缀
    QENTL_EXTENSIONS = ['.qent', '.qentl']
    
    # QEntL文件类型
    QENTL_FILE_TYPES = {
        'network': r'network\s+\w+\s*{',
        'channel': r'channel\s*{',
        'gene': r'QuantumGene:'
    }
    
    def __init__(self, project_root: Optional[str] = None, backup_dir: Optional[str] = None):
        """
        初始化QEntL文件修复工具
        
        参数:
            project_root: 项目根目录，默认会自动查找
            backup_dir: 备份目录，默认为项目根目录下的.qentl_backup
        """
        self.project_root = project_root or self._find_project_root()
        self.backup_dir = backup_dir or os.path.join(self.project_root, '.qentl_backup')
        
        # 确保备份目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # QEntL目录列表
        self.qentl_dirs = [
            os.path.join(self.project_root, 'docs', 'QEntL'),
            os.path.join(self.project_root, 'QEntL'),
            os.path.join(self.project_root, 'Ref', 'QEntL'),
            os.path.join(self.project_root, 'QSM', 'QEntL'),
            os.path.join(self.project_root, 'SOM', 'QEntL'),
            os.path.join(self.project_root, 'WeQ', 'QEntL')
        ]
        
        # 确保QEntL目录存在
        for qentl_dir in self.qentl_dirs:
            os.makedirs(qentl_dir, exist_ok=True)
        
        logger.info(f"QEntL文件修复工具初始化完成，项目根目录：{self.project_root}")
        logger.info(f"备份目录：{self.backup_dir}")
    
    def _find_project_root(self) -> str:
        """
        查找项目根目录，通过向上查找.git目录确定
        
        返回:
            str: 项目根目录的绝对路径
        """
        current_dir = os.path.abspath(os.path.dirname(__file__))
        
        # 向上查找.git目录
        while current_dir != os.path.dirname(current_dir):  # 防止到达文件系统根目录
            if os.path.exists(os.path.join(current_dir, '.git')):
                logger.debug(f"找到项目根目录: {current_dir}")
                return current_dir
            current_dir = os.path.dirname(current_dir)
        
        # 如果找不到.git目录，使用当前目录
        logger.warning("未找到.git目录，使用当前目录作为项目根目录")
        return os.path.abspath(os.path.dirname(__file__))
    
    def backup_file(self, file_path: str) -> str:
        """
        备份文件
        
        参数:
            file_path: 要备份的文件路径
            
        返回:
            str: 备份文件的路径
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.warning(f"要备份的文件不存在: {file_path}")
                return ""
            
            # 创建备份子目录
            rel_path = os.path.relpath(file_path, self.project_root)
            backup_subdir = os.path.dirname(os.path.join(self.backup_dir, rel_path))
            os.makedirs(backup_subdir, exist_ok=True)
            
            # 生成备份文件名（添加时间戳）
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            file_name, file_ext = os.path.splitext(os.path.basename(file_path))
            backup_file_name = f"{file_name}_{timestamp}{file_ext}"
            backup_path = os.path.join(backup_subdir, backup_file_name)
            
            # 复制文件
            shutil.copy2(file_path, backup_path)
            logger.info(f"已备份文件: {file_path} -> {backup_path}")
            
            return backup_path
        
        except Exception as e:
            logger.error(f"备份文件失败 {file_path}: {str(e)}")
            return ""
    
    def is_qentl_file(self, file_path: str) -> bool:
        """
        检查文件是否为QEntL文件
        
        参数:
            file_path: 文件路径
            
        返回:
            bool: 是否为QEntL文件
        """
        # 检查文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in self.QENTL_EXTENSIONS:
            return True
        
        # 检查文件内容是否包含QEntL关键字
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)  # 只读取前1KB判断
                if 'QEntL:' in content or 'QuantumGene:' in content or 'network ' in content or 'channel {' in content:
                    return True
        except Exception:
            pass
        
        return False
    
    def repair_file(self, file_path: str) -> bool:
        """
        修复QEntL文件
        
        参数:
            file_path: 文件路径
            
        返回:
            bool: 修复是否成功
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.warning(f"要修复的文件不存在: {file_path}")
                return False
            
            # 检查是否为QEntL文件
            if not self.is_qentl_file(file_path):
                logger.warning(f"文件不是QEntL文件: {file_path}")
                return False
            
            logger.info(f"开始修复文件: {file_path}")
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 备份原文件
            self.backup_file(file_path)
            
            # 根据文件类型进行修复
            if re.search(self.QENTL_FILE_TYPES['network'], content):
                new_content = self._repair_qentl_definition(content, 'network')
            elif re.search(self.QENTL_FILE_TYPES['channel'], content):
                new_content = self._repair_channel_definition(content)
            elif re.search(self.QENTL_FILE_TYPES['gene'], content):
                new_content = self._repair_gene_definition(content)
            else:
                # 无法识别的QEntL文件类型
                logger.warning(f"无法识别的QEntL文件类型: {file_path}")
                return False
            
            # 写入修复后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"文件修复成功: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"修复文件失败 {file_path}: {str(e)}")
            return False
    
    def _repair_qentl_definition(self, content: str, definition_type: str) -> str:
        """
        修复QEntL网络定义
        
        参数:
            content: 文件内容
            definition_type: 定义类型
            
        返回:
            str: 修复后的内容
        """
        # 更新版本信息
        content = re.sub(r'# Version:.*', '# Version: 2.0', content)
        
        # 更新生成时间
        timestamp = datetime.datetime.now().isoformat()
        content = re.sub(r'# Generated:.*', f'# Generated: {timestamp}', content)
        
        # 修复网络定义格式
        if definition_type == 'network':
            # 检查网络ID是否存在，如果不存在则添加
            if not re.search(r'id:\s*"[^"]*"', content):
                network_name = re.search(r'network\s+(\w+)', content).group(1)
                network_id = f"{network_name}_{int(time.time())}"
                content = re.sub(r'network\s+\w+\s*{', f'network {network_name} {{\n  id: "{network_id}",', content)
            
            # 检查网络类型是否存在，如果不存在则添加
            if not re.search(r'type:\s*"[^"]*"', content):
                content = re.sub(r'id:\s*"[^"]*"', 'id: "\\g<0>",\n  type: "mesh"', content)
            
            # 检查版本是否存在，如果不存在则添加
            if not re.search(r'version:\s*"[^"]*"', content):
                content = re.sub(r'type:\s*"[^"]*"', 'type: "\\g<0>",\n  version: "2.0"', content)
        
        return content
    
    def _repair_channel_definition(self, content: str) -> str:
        """
        修复QEntL信道定义
        
        参数:
            content: 文件内容
            
        返回:
            str: 修复后的内容
        """
        # 更新版本信息
        content = re.sub(r'# Version:.*', '# Version: 2.0', content)
        if not '# Version:' in content:
            content = content.replace('# Generated:', '# Version: 2.0\n# Generated:')
        
        # 更新生成时间
        timestamp = datetime.datetime.now().isoformat()
        content = re.sub(r'# Generated:.*', f'# Generated: {timestamp}', content)
        
        # 检查信道ID是否存在
        if not re.search(r'id:\s*"[^"]*"', content):
            channel_id = f"channel_{int(time.time())}"
            content = re.sub(r'channel\s*{', f'channel {{\n  id: "{channel_id}",', content)
        
        # 检查信道类型是否存在
        if not re.search(r'type:\s*"[^"]*"', content):
            content = re.sub(r'id:\s*"[^"]*"', 'id: "\\g<0>",\n  type: "standard"', content)
        
        # 检查优先级是否存在
        if not re.search(r'priority:\s*\d+', content):
            content = re.sub(r'type:\s*"[^"]*"', 'type: "\\g<0>",\n  priority: 5', content)
        
        return content
    
    def _repair_gene_definition(self, content: str) -> str:
        """
        修复QEntL基因定义
        
        参数:
            content: 文件内容
            
        返回:
            str: 修复后的内容
        """
        # 获取量子基因编码
        gene_match = re.search(r'QuantumGene:\s*([^\n]+)', content)
        quantum_gene = gene_match.group(1).strip() if gene_match else f"QE-AUTO-{str(uuid.uuid4())[:8]}-{int(time.time())}"
        
        # 检查QEntL标头
        if not re.search(r'QEntL:', content):
            content = f"QEntL: QEntL 2.0 Annotation\n{content}"
        else:
            content = re.sub(r'QEntL:.*', 'QEntL: QEntL 2.0 Annotation', content)
        
        # 检查创建时间
        if not re.search(r'CreatedAt:', content):
            timestamp = datetime.datetime.now().isoformat()
            content = re.sub(r'QuantumGene:.*', f'QuantumGene: {quantum_gene}\nCreatedAt: {timestamp}', content)
        
        # 检查纠缠强度
        if not re.search(r'EntanglementStrength:', content):
            content += f"\nEntanglementStrength: 0.95\n"
        
        return content
    
    def create_base_files(self, directory: str) -> bool:
        """
        创建基础配置文件
        
        参数:
            directory: 目录路径
            
        返回:
            bool: 创建是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(directory, exist_ok=True)
            
            # 创建README文件
            readme_path = os.path.join(directory, 'README.md')
            if not os.path.exists(readme_path):
                dir_name = os.path.basename(directory)
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(f"""# {dir_name} 目录

此目录包含QEntL（量子纠缠语言）定义文件，用于描述量子纠缠关系和网络拓扑。

## 文件类型

- `.qent`/`.qentl`: QEntL定义文件
- `networks/`: 包含量子网络定义
- `channels/`: 包含量子信道定义

## QEntL 2.0语法

QEntL 2.0语法支持更灵活的网络和信道定义，以及量子基因标记。详细语法请参考`docs/QEntL/syntax.qentl`文件。
""")
                logger.info(f"已创建README文件: {readme_path}")
            
            # 创建配置文件
            config_path = os.path.join(directory, 'qentl.config')
            if not os.path.exists(config_path):
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write("""# QEntL配置文件
version: "2.0"
auto_repair: true
syntax_validation: true
entanglement_threshold: 0.85
default_network_type: "mesh"
default_channel_type: "standard"
""")
                logger.info(f"已创建配置文件: {config_path}")
            
            # 创建子目录
            for subdir in ['networks', 'channels']:
                subdir_path = os.path.join(directory, subdir)
                os.makedirs(subdir_path, exist_ok=True)
            
            return True
        
        except Exception as e:
            logger.error(f"创建基础配置文件失败 {directory}: {str(e)}")
            return False
    
    def scan_and_repair(self, directory: str) -> Tuple[int, int]:
        """
        扫描目录并修复QEntL文件
        
        参数:
            directory: 要扫描的目录
            
        返回:
            Tuple[int, int]: (扫描文件数, 修复文件数)
        """
        # 创建基础配置文件
        self.create_base_files(directory)
        
        scanned_files = 0
        repaired_files = 0
        
        # 扫描目录
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                # 检查是否为QEntL文件
                if self.is_qentl_file(file_path):
                    scanned_files += 1
                    
                    # 修复文件
                    if self.repair_file(file_path):
                        repaired_files += 1
        
        logger.info(f"目录扫描完成: {directory}, 共扫描 {scanned_files} 个QEntL文件, 修复 {repaired_files} 个文件")
        return (scanned_files, repaired_files)
    
    def repair_all(self) -> Dict[str, Tuple[int, int]]:
        """
        修复所有QEntL目录
        
        返回:
            Dict[str, Tuple[int, int]]: 目录路径到(扫描文件数, 修复文件数)的映射
        """
        results = {}
        
        # 遍历所有QEntL目录
        for qentl_dir in self.qentl_dirs:
            if os.path.exists(qentl_dir):
                logger.info(f"开始修复目录: {qentl_dir}")
                results[qentl_dir] = self.scan_and_repair(qentl_dir)
        
        # 打印汇总信息
        total_scanned = sum(r[0] for r in results.values())
        total_repaired = sum(r[1] for r in results.values())
        logger.info(f"QEntL文件修复完成，共扫描 {total_scanned} 个文件，修复 {total_repaired} 个文件")
        
        return results

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='QEntL文件修复工具')
    parser.add_argument('--root', type=str, help='项目根目录')
    parser.add_argument('--backup', type=str, help='备份目录')
    args = parser.parse_args()
    
    # 创建修复工具
    repair_tool = QEntLRepairTool(project_root=args.root, backup_dir=args.backup)
    
    # 修复所有QEntL文件
    results = repair_tool.repair_all()
    
    # 打印结果
    print("\n修复结果汇总:")
    for directory, (scanned, repaired) in results.items():
        print(f"{directory}: 扫描 {scanned} 个文件，修复 {repaired} 个文件")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
"""
量子基因编码: QE-QEN-9B4791F6B67F
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
"""