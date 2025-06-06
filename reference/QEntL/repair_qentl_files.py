#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QEntL 文件修复工具

该工具用于修复以下目录中的QEntL文件：
- docs/QEntL
- QEntL
- Ref/QEntL
- QSM/QEntL
- SOM/QEntL
- WeQ/QEntL

修复内容包括:
1. 更新文件语法至最新的QEntL 2.0标准
2. 修复量子基因标记和纠缠关系
3. 创建缺失的基础配置文件
4. 备份所有修改过的文件
"""

import os
import re
import sys
import json
import shutil
import logging
import argparse
import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set, Any

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
    
    def __init__(self, project_root: str, backup_dir: Optional[str] = None):
        """
        初始化修复工具
        
        参数:
            project_root: 项目根目录
            backup_dir: 备份目录，默认为项目根目录下的.qentl_backup
        """
        self.project_root = os.path.abspath(project_root)
        self.backup_dir = backup_dir or os.path.join(self.project_root, '.qentl_backup')
        
        # QEntL目录列表
        self.qentl_dirs = [
            os.path.join(self.project_root, 'docs', 'QEntL'),
            os.path.join(self.project_root, 'QEntL'),
            os.path.join(self.project_root, 'Ref', 'QEntL'),
            os.path.join(self.project_root, 'QSM', 'QEntL'),
            os.path.join(self.project_root, 'SOM', 'QEntL'),
            os.path.join(self.project_root, 'WeQ', 'QEntL')
        ]
        
        # QEntL文件扩展名
        self.qentl_extensions = ['.qent', '.qentl']
        
        # 确保目标目录存在
        for qentl_dir in self.qentl_dirs:
            os.makedirs(qentl_dir, exist_ok=True)
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        logger.info(f"备份目录创建成功: {self.backup_dir}")
        
        # 时间戳，用于备份文件夹命名
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        
        logger.info(f"QEntL修复工具初始化完成")
    
    def backup_file(self, file_path: str) -> str:
        """
        备份文件
        
        参数:
            file_path: 需要备份的文件路径
            
        返回:
            str: 备份后的文件路径
        """
        # 获取文件相对于项目根目录的路径
        rel_path = os.path.relpath(file_path, self.project_root)
        
        # 构建备份文件路径
        backup_path = os.path.join(self.backup_dir, self.timestamp, rel_path)
        
        # 确保备份目录存在
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # 复制文件
        shutil.copy2(file_path, backup_path)
        logger.debug(f"文件已备份: {file_path} -> {backup_path}")
        
        return backup_path
    
    def is_qentl_file(self, file_path: str) -> bool:
        """
        检查文件是否为QEntL文件
        
        参数:
            file_path: 文件路径
            
        返回:
            bool: 是否为QEntL文件
        """
        # 检查文件扩展名
        ext = os.path.splitext(file_path)[1].lower()
        if ext in self.qentl_extensions:
            return True
        
        # 检查文件内容是否包含QEntL标记
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # 只读取前1000个字符
                return 'QEntL' in content or 'quantum_gene' in content or 'QuantumGene' in content
        except:
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
                logger.warning(f"文件不存在: {file_path}")
                return False
            
            # 检查是否为QEntL文件
            if not self.is_qentl_file(file_path):
                logger.debug(f"非QEntL文件，跳过: {file_path}")
                return False
            
            # 备份文件
            self.backup_file(file_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 获取文件扩展名
            ext = os.path.splitext(file_path)[1].lower()
            
            # 根据文件类型选择修复方法
            if ext == '.qent' or ext == '.qentl':
                repaired_content = self._repair_qentl_definition(content)
            else:
                repaired_content = self._repair_qentl_annotation(content)
            
            # 写入修复后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(repaired_content)
            
            logger.info(f"文件修复成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"修复文件失败 {file_path}: {str(e)}")
            return False
    
    def _repair_qentl_definition(self, content: str) -> str:
        """
        修复QEntL定义文件内容
        
        参数:
            content: 文件内容
            
        返回:
            str: 修复后的内容
        """
        # 检查文件类型
        if 'network {' in content or 'network{' in content:
            return self._repair_network_definition(content)
        elif 'channel {' in content or 'channel{' in content:
            return self._repair_channel_definition(content)
        elif 'quantum_gene' in content or 'QuantumGene' in content:
            return self._repair_gene_definition(content)
        else:
            # 基础配置文件
            return self._repair_config_definition(content)
    
    def _repair_network_definition(self, content: str) -> str:
        """修复网络定义文件"""
        # 检查是否是JSON格式
        if content.strip().startswith('{') and 'network' in content and '"id"' in content:
            # 尝试将JSON格式转换为QEntL 2.0语法
            try:
                data = json.loads(content)
                network_data = data.get('network', {})
                network_name = network_data.get('id', 'network_' + self.timestamp[:8])
                
                # 创建新的网络定义
                new_content = f"""# QEntL Network Definition - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Network: {network_name}
# Type: {network_data.get('type', 'mesh')}
# Version: 2.0
# Repaired: {datetime.datetime.now().isoformat()}

network {network_name} {{
  id: "{network_data.get('id', network_name)}",
  type: "{network_data.get('type', 'mesh')}",
  version: "2.0",
"""
                # 添加节点
                nodes = network_data.get('nodes', [])
                if nodes:
                    new_content += "\n  nodes: [\n"
                    for node in nodes:
                        new_content += f"    {{\n"
                        for key, value in node.items():
                            if isinstance(value, str):
                                new_content += f'      {key}: "{value}",\n'
                            elif isinstance(value, list):
                                values_str = ', '.join([f'"{v}"' for v in value])
                                new_content += f"      {key}: [{values_str}],\n"
                            else:
                                new_content += f"      {key}: {value},\n"
                        new_content += "    },\n"
                    new_content += "  ],\n"
                
                # 添加处理器
                processors = network_data.get('processors', [])
                if processors:
                    new_content += "\n  processors: [\n"
                    for processor in processors:
                        new_content += f"    {{\n"
                        for key, value in processor.items():
                            if isinstance(value, str):
                                new_content += f'      {key}: "{value}",\n'
                            elif isinstance(value, list):
                                values_str = ', '.join([f'"{v}"' for v in value])
                                new_content += f"      {key}: [{values_str}],\n"
                            else:
                                new_content += f"      {key}: {value},\n"
                        new_content += "    },\n"
                    new_content += "  ],\n"
                
                # 添加纠缠管理器
                entanglement_manager = network_data.get('entanglementManager', {})
                if entanglement_manager:
                    new_content += "\n  entanglementManager: {\n"
                    for key, value in entanglement_manager.items():
                        if isinstance(value, str):
                            new_content += f'    {key}: "{value}",\n'
                        elif isinstance(value, list):
                            values_str = ', '.join([f'"{v}"' for v in value])
                            new_content += f"    {key}: [{values_str}],\n"
                        else:
                            new_content += f"    {key}: {value},\n"
                    new_content += "  }\n"
                
                new_content += "}\n"
                return new_content
                
            except json.JSONDecodeError:
                # 如果不是有效的JSON，尝试其他方法修复
                pass
        
        # 已经是QEntL 2.0语法或其他格式，进行基本清理
        # 添加/更新头部注释
        header_lines = []
        content_lines = content.split('\n')
        
        # 过滤掉旧的头部注释
        for i, line in enumerate(content_lines):
            if line.strip().startswith('#'):
                header_lines.append(line)
            else:
                content_lines = content_lines[i:]
                break
        
        # 如果没有足够的头部注释，添加新的
        if len(header_lines) < 3:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            header_lines = [
                f"# QEntL Network Definition - {timestamp}",
                "# Type: mesh",
                "# Version: 2.0",
                f"# Repaired: {datetime.datetime.now().isoformat()}"
            ]
        
        # 提取网络名称
        network_name = "network"
        for line in content_lines:
            match = re.search(r'network\s+(\w+)\s*{', line)
            if match:
                network_name = match.group(1)
                break
        
        # 添加版本号（如果没有）
        version_added = False
        for i, line in enumerate(content_lines):
            if 'version' in line and ':' in line:
                content_lines[i] = re.sub(r'version\s*:\s*"[^"]*"', 'version: "2.0"', line)
                version_added = True
                break
        
        if not version_added:
            # 寻找添加版本号的位置
            for i, line in enumerate(content_lines):
                if '{' in line and (i == 0 or '}' not in content_lines[i-1]):
                    indent = line.index('{') + 1
                    content_lines.insert(i + 1, ' ' * indent + 'version: "2.0",')
                    break
        
        # 组合头部和内容
        return '\n'.join(header_lines + content_lines)
    
    def _repair_channel_definition(self, content: str) -> str:
        """修复信道定义文件"""
        # 检查是否是JSON格式
        if content.strip().startswith('{') and 'channel' in content and '"id"' in content:
            # 尝试将JSON格式转换为QEntL 2.0语法
            try:
                data = json.loads(content)
                channel_data = data.get('channel', {})
                channel_id = channel_data.get('id', 'channel_' + self.timestamp[:8])
                
                # 创建新的信道定义
                new_content = f"""# QEntL Channel Definition - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Channel: {channel_id}
# Type: {channel_data.get('type', 'standard')}
# Version: 2.0
# Repaired: {datetime.datetime.now().isoformat()}

channel {{
  id: "{channel_id}",
  type: "{channel_data.get('type', 'standard')}",
  quantum_gene: "{channel_data.get('quantum_gene', '')}",
  priority: {channel_data.get('priority', 5)},
"""
                # 添加源
                source = channel_data.get('source', '')
                if source:
                    new_content += f'  source: "{source}",\n'
                
                # 添加目标
                targets = channel_data.get('targets', [])
                if targets:
                    if isinstance(targets, list):
                        targets_str = json.dumps(targets)
                        new_content += f"  targets: {targets_str}\n"
                    else:
                        new_content += f'  targets: ["{targets}"]\n'
                else:
                    new_content += "  targets: []\n"
                
                new_content += "}\n"
                return new_content
                
            except json.JSONDecodeError:
                # 如果不是有效的JSON，尝试其他方法修复
                pass
        
        # 已经是QEntL 2.0语法或其他格式，进行基本清理
        # 添加/更新头部注释
        header_lines = []
        content_lines = content.split('\n')
        
        # 过滤掉旧的头部注释
        for i, line in enumerate(content_lines):
            if line.strip().startswith('#'):
                header_lines.append(line)
            else:
                content_lines = content_lines[i:]
                break
        
        # 如果没有足够的头部注释，添加新的
        if len(header_lines) < 3:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            channel_id = "channel_" + self.timestamp[:8]
            for line in content_lines:
                match = re.search(r'id\s*:\s*"([^"]*)"', line)
                if match:
                    channel_id = match.group(1)
                    break
            
            header_lines = [
                f"# QEntL Channel Definition - {timestamp}",
                f"# Channel: {channel_id}",
                "# Type: standard",
                "# Version: 2.0",
                f"# Repaired: {datetime.datetime.now().isoformat()}"
            ]
        
        # 组合头部和内容
        return '\n'.join(header_lines + content_lines)
    
    def _repair_gene_definition(self, content: str) -> str:
        """修复基因定义文件"""
        # 如果是JSON格式，转换为QEntL 2.0语法
        if content.strip().startswith('{') and ('QuantumGene' in content or 'quantum_gene' in content):
            try:
                data = json.loads(content)
                gene_id = data.get('id', data.get('QuantumGene', data.get('quantum_gene', 'QE-' + self.timestamp[:8])))
                
                # 创建新的基因定义
                new_content = f"""# QEntL Quantum Gene Definition - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Gene: {gene_id}
# Version: 2.0
# Repaired: {datetime.datetime.now().isoformat()}

quantum_gene {{
  id: "{gene_id}",
  version: "2.0",
  created_at: "{data.get('created_at', data.get('CreatedAt', datetime.datetime.now().isoformat()))}",
"""
                # 添加其他属性
                for key, value in data.items():
                    if key not in ['id', 'QuantumGene', 'quantum_gene', 'created_at', 'CreatedAt', 'version']:
                        if isinstance(value, str):
                            new_content += f'  {key}: "{value}",\n'
                        elif isinstance(value, list):
                            values_str = json.dumps(value)
                            new_content += f"  {key}: {values_str},\n"
                        else:
                            new_content += f"  {key}: {value},\n"
                
                # 移除最后一个逗号并关闭定义
                new_content = new_content.rstrip(',\n') + '\n}\n'
                return new_content
                
            except json.JSONDecodeError:
                # 如果不是有效的JSON，尝试其他方法修复
                pass
        
        # 已经是QEntL 2.0语法或其他格式，进行基本清理
        # 将关键字从 QuantumGene 统一为 quantum_gene
        content = re.sub(r'QuantumGene\s*{', 'quantum_gene {', content)
        content = re.sub(r'QuantumGene\s*:', 'quantum_gene:', content)
        
        # 添加版本号（如果没有）
        if 'version' not in content:
            content = re.sub(r'quantum_gene\s*{', 'quantum_gene {\n  version: "2.0",', content)
        
        # 添加/更新头部注释
        header_lines = []
        content_lines = content.split('\n')
        
        # 过滤掉旧的头部注释
        for i, line in enumerate(content_lines):
            if line.strip().startswith('#'):
                header_lines.append(line)
            else:
                content_lines = content_lines[i:]
                break
        
        # 如果没有足够的头部注释，添加新的
        if len(header_lines) < 3:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            gene_id = "QE-" + self.timestamp[:8]
            for line in content_lines:
                match = re.search(r'id\s*:\s*"([^"]*)"', line)
                if match:
                    gene_id = match.group(1)
                    break
            
            header_lines = [
                f"# QEntL Quantum Gene Definition - {timestamp}",
                f"# Gene: {gene_id}",
                "# Version: 2.0",
                f"# Repaired: {datetime.datetime.now().isoformat()}"
            ]
        
        # 组合头部和内容
        return '\n'.join(header_lines + content_lines)
    
    def _repair_config_definition(self, content: str) -> str:
        """修复配置定义文件"""
        # 如果文件为空或几乎为空，创建一个新的配置文件
        if len(content.strip()) < 10:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return f"""# QEntL Configuration - {timestamp}
# Version: 2.0
# Generated: {datetime.datetime.now().isoformat()}

config {{
  version: "2.0",
  default_network: "main_network",
  log_level: "info",
  auto_repair: true,
  paths: {{
    networks: "./networks",
    channels: "./channels",
    templates: "./templates"
  }},
  plugins: [
    "quantum_error_correction",
    "entanglement_purification"
  ]
}}
"""
        
        # 已经有内容，进行基本清理
        # 添加/更新头部注释
        header_lines = []
        content_lines = content.split('\n')
        
        # 过滤掉旧的头部注释
        for i, line in enumerate(content_lines):
            if line.strip().startswith('#'):
                header_lines.append(line)
            else:
                content_lines = content_lines[i:]
                break
        
        # 如果没有足够的头部注释，添加新的
        if len(header_lines) < 3:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            header_lines = [
                f"# QEntL Configuration - {timestamp}",
                "# Version: 2.0",
                f"# Repaired: {datetime.datetime.now().isoformat()}"
            ]
        
        # 添加版本号（如果没有）
        version_added = False
        for i, line in enumerate(content_lines):
            if 'version' in line and ':' in line:
                content_lines[i] = re.sub(r'version\s*:\s*"[^"]*"', 'version: "2.0"', line)
                version_added = True
                break
        
        if not version_added:
            # 寻找添加版本号的位置
            for i, line in enumerate(content_lines):
                if '{' in line and (i == 0 or '}' not in content_lines[i-1]):
                    indent = line.index('{') + 1
                    content_lines.insert(i + 1, ' ' * indent + 'version: "2.0",')
                    break
        
        # 组合头部和内容
        return '\n'.join(header_lines + content_lines)
    
    def _repair_qentl_annotation(self, content: str) -> str:
        """
        修复QEntL注释
        
        参数:
            content: 文件内容
            
        返回:
            str: 修复后的内容
        """
        # 查找QEntL注释块
        qentl_block_pattern = r'(QEntL:.*?)(?=\n\s*\n|\Z)'
        qentl_blocks = re.findall(qentl_block_pattern, content, re.DOTALL)
        
        if not qentl_blocks:
            return content
        
        # 修复每个QEntL注释块
        for block in qentl_blocks:
            # 提取量子基因编码
            gene_match = re.search(r'QuantumGene:\s*(.+)', block)
            if not gene_match:
                continue
            
            quantum_gene = gene_match.group(1).strip()
            
            # 创建新的注释块
            new_block = f"QEntL: QEntL 2.0 Annotation\n"
            new_block += f"QuantumGene: {quantum_gene}\n"
            
            # 添加创建时间（如果没有）
            if 'CreatedAt:' not in block:
                new_block += f"CreatedAt: {datetime.datetime.now().isoformat()}\n"
            else:
                # 提取已有的创建时间
                created_match = re.search(r'CreatedAt:\s*(.+)', block)
                if created_match:
                    new_block += f"CreatedAt: {created_match.group(1).strip()}\n"
            
            # 添加纠缠对象（如果有）
            entangled_match = re.search(r'EntangledObjects:(.*?)(?=\n\w|$)', block, re.DOTALL)
            if entangled_match:
                objects_text = entangled_match.group(1).strip()
                if objects_text:
                    new_block += "EntangledObjects:\n"
                    for line in objects_text.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if not line.startswith('-'):
                                line = f"  - {line}"
                            else:
                                line = f"  {line}"
                            new_block += f"{line}\n"
            
            # 添加纠缠强度（如果有）
            strength_match = re.search(r'EntanglementStrength:\s*(.+)', block)
            if strength_match:
                strength = strength_match.group(1).strip()
                new_block += f"EntanglementStrength: {strength}\n"
            else:
                new_block += "EntanglementStrength: 0.95\n"
            
            # 替换原始块
            content = content.replace(block, new_block)
        
        return content
    
    def create_base_files(self, directory: str) -> int:
        """
        创建基础文件
        
        参数:
            directory: 目录路径
            
        返回:
            int: 创建的文件数量
        """
        try:
            # 确保目录存在
            os.makedirs(directory, exist_ok=True)
            
            created_count = 0
            
            # 创建README.md（如果不存在）
            readme_path = os.path.join(directory, 'README.md')
            if not os.path.exists(readme_path):
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(f"""# QEntL 定义文件目录

此目录包含用于定义量子纠缠关系和网络的QEntL文件。

## 目录结构

- `networks/`: 包含QEntL网络定义
- `channels/`: 包含QEntL信道定义
- `templates/`: 包含可重用的QEntL模板

## 文件格式

所有QEntL文件使用QEntL 2.0语法标准。

生成时间: {datetime.datetime.now().isoformat()}
""")
                created_count += 1
                logger.info(f"创建README.md文件: {readme_path}")
            
            # 创建配置文件（如果不存在）
            config_path = os.path.join(directory, 'qentl_config.qent')
            if not os.path.exists(config_path):
                with open(config_path, 'w', encoding='utf-8') as f:
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"""# QEntL Configuration - {timestamp}
# Version: 2.0
# Generated: {datetime.datetime.now().isoformat()}

config {{
  version: "2.0",
  default_network: "main_network",
  log_level: "info",
  auto_repair: true,
  paths: {{
    networks: "./networks",
    channels: "./channels",
    templates: "./templates"
  }},
  plugins: [
    "quantum_error_correction",
    "entanglement_purification"
  ]
}}
""")
                created_count += 1
                logger.info(f"创建配置文件: {config_path}")
            
            # 创建目录结构
            for subdir in ['networks', 'channels', 'templates']:
                subdir_path = os.path.join(directory, subdir)
                os.makedirs(subdir_path, exist_ok=True)
                
                # 创建示例网络文件
                if subdir == 'networks' and not os.listdir(subdir_path):
                    example_path = os.path.join(subdir_path, 'example_network.qent')
                    with open(example_path, 'w', encoding='utf-8') as f:
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        dir_name = os.path.basename(directory)
                        f.write(f"""# QEntL Network Definition - {timestamp}
# Network: {dir_name}_network
# Type: mesh
# Version: 2.0
# Generated: {datetime.datetime.now().isoformat()}

network {dir_name}_network {{
  id: "{dir_name}_network_{self.timestamp}",
  type: "mesh",
  version: "2.0",
  
  nodes: [
    # 核心节点
    {{
      id: "core_node_1",
      type: "core",
      connections: ["compute_node_1", "storage_node_1"],
      state_management: true
    }},
    
    # 计算节点
    {{
      id: "compute_node_1",
      type: "compute",
      connections: ["core_node_1", "storage_node_1"],
      qubits: 128
    }},
    
    # 存储节点
    {{
      id: "storage_node_1",
      type: "storage",
      connections: ["core_node_1", "compute_node_1"],
      capacity: "1024 qubits"
    }}
  ],
  
  processors: [
    {{
      id: "main_processor",
      type: "quantum",
      qubits: 512,
      error_correction: "surface_code",
      nodes: ["core_node_1"]
    }},
    {{
      id: "auxiliary_processor",
      type: "quantum",
      qubits: 256,
      error_correction: "surface_code",
      nodes: ["compute_node_1"]
    }}
  ],
  
  entanglementManager: {{
    id: "{dir_name}_entanglement_manager",
    type: "priority_based",
    purification_threshold: 0.95,
    refresh_rate: "100ms",
    priority_levels: 10
  }}
}}
""")
                    created_count += 1
                    logger.info(f"创建示例网络文件: {example_path}")
            
            logger.info(f"目录 {directory} 中创建了 {created_count} 个基础文件")
            return created_count
            
        except Exception as e:
            logger.error(f"创建基础文件失败 {directory}: {str(e)}")
            return 0
    
    def repair_qentl_files(self) -> Dict[str, int]:
        """
        修复所有QEntL文件
        
        返回:
            Dict[str, int]: 每个目录的修复文件数量
        """
        results = {}
        
        for qentl_dir in self.qentl_dirs:
            # 确保目录存在
            os.makedirs(qentl_dir, exist_ok=True)
            
            # 创建基础文件
            self.create_base_files(qentl_dir)
            
            # 修复目录中的文件
            repaired_count = 0
            
            # 递归遍历目录
            for root, dirs, files in os.walk(qentl_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.repair_file(file_path):
                        repaired_count += 1
            
            # 记录结果
            rel_dir = os.path.relpath(qentl_dir, self.project_root)
            results[rel_dir] = repaired_count
            logger.info(f"目录 {rel_dir} 中修复了 {repaired_count} 个文件")
        
        return results

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='QEntL文件修复工具')
    parser.add_argument('--project-root', '-p', type=str, default=os.getcwd(),
                      help='项目根目录路径')
    parser.add_argument('--backup-dir', '-b', type=str, default=None,
                      help='备份目录路径')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='显示详细日志')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger('QEntLRepairTool').setLevel(logging.DEBUG)
    
    # 初始化修复工具
    tool = QEntLRepairTool(args.project_root, args.backup_dir)
    
    # 执行修复
    start_time = datetime.datetime.now()
    results = tool.repair_qentl_files()
    end_time = datetime.datetime.now()
    
    # 输出结果
    print("\nQEntL文件修复完成!")
    print("-" * 50)
    total_repaired = sum(results.values())
    print(f"总共修复: {total_repaired} 个文件")
    print(f"耗时: {(end_time - start_time).total_seconds():.2f} 秒")
    print("-" * 50)
    
    for directory, count in results.items():
        print(f"{directory}: {count} 个文件")
    
    print("\n备份存储在: " + tool.backup_dir)
    print("修复日志保存在: .logs/qentl_repair.log")

if __name__ == "__main__":
    main() 
"""
量子基因编码: QE-REP-13FB3D827DB9
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""