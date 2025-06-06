#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QEntL格式化工具

该模块提供用于生成QEntL 2.0语法的功能，包括：
1. 量子基因编码生成
2. QEntL注释生成
3. QEntL信道文件生成
4. QEntL网络定义生成

支持将QEntL注释添加到多种文件类型，并可自动处理注释格式。
"""

import os
import re
import uuid
import json
import time
import hashlib
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Any, Union

# 配置日志
os.makedirs('.logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/qentl_formatter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('QEntLFormatter')

class QEntLFormatter:
    """QEntL格式化工具，支持QEntL 2.0语法"""
    
    # 文件类型与注释格式映射
    FILE_COMMENT_FORMATS = {
        '.py': {'block_start': '"""', 'block_end': '"""', 'line': '#'},
        '.js': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.ts': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.tsx': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.jsx': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.java': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.c': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.cpp': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.h': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.go': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.rs': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.php': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.rb': {'block_start': '=begin', 'block_end': '=end', 'line': '#'},
        '.swift': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.kt': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.scala': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.html': {'block_start': '<!--', 'block_end': '-->', 'line': '<!--'},
        '.xml': {'block_start': '<!--', 'block_end': '-->', 'line': '<!--'},
        '.css': {'block_start': '/*', 'block_end': '*/', 'line': '/*'},
        '.scss': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.less': {'block_start': '/*', 'block_end': '*/', 'line': '//'},
        '.md': {'block_start': '<!---', 'block_end': '-->', 'line': '<!--'},
        '.sh': {'block_start': ': <<\'EOC\'', 'block_end': 'EOC', 'line': '#'},
        '.bat': {'block_start': '@echo off\nREM', 'block_end': '@echo on', 'line': 'REM'},
        '.ps1': {'block_start': '<#', 'block_end': '#>', 'line': '#'},
        '.sql': {'block_start': '/*', 'block_end': '*/', 'line': '--'},
        '.r': {'block_start': '#\'', 'block_end': '#\'', 'line': '#'},
        '.json': {'block_start': '', 'block_end': '', 'line': '//'},
        '.yaml': {'block_start': '', 'block_end': '', 'line': '#'},
        '.yml': {'block_start': '', 'block_end': '', 'line': '#'},
        '.toml': {'block_start': '', 'block_end': '', 'line': '#'},
        '.ini': {'block_start': '', 'block_end': '', 'line': ';'},
        '.conf': {'block_start': '', 'block_end': '', 'line': '#'},
        '.default': {'block_start': '', 'block_end': '', 'line': '#'}
    }
    
    def __init__(self, project_root: Optional[str] = None, output_dir: Optional[str] = None):
        """
        初始化QEntL格式化工具
        
        参数:
            project_root: 项目根目录，默认会自动查找
            output_dir: 输出目录，默认为./WeQ/output/qentl
        """
        self.project_root = project_root or self._find_project_root()
        self.output_dir = output_dir or os.path.join(self.project_root, 'WeQ', 'output', 'qentl')
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 创建QEntL子目录
        for subdir in ['networks', 'channels', 'annotations']:
            os.makedirs(os.path.join(self.output_dir, subdir), exist_ok=True)
        
        logger.info(f"QEntL格式化工具初始化完成，项目根目录：{self.project_root}")
        logger.info(f"QEntL输出目录：{self.output_dir}")
    
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
    
    def generate_quantum_gene(self, module_name: str, content: Optional[str] = None) -> str:
        """
        生成量子基因编码
        
        参数:
            module_name: 模块名称，用于生成前缀
            content: 可选的内容，用于生成唯一性哈希
            
        返回:
            str: 量子基因编码，格式为 QE-{PREFIX}-{UUID}
        """
        # 生成前缀
        prefix = module_name.upper()[:4]
        
        # 生成时间戳
        timestamp = int(time.time() * 1000)
        
        # 生成UUID
        random_uuid = str(uuid.uuid4()).replace('-', '')[:8]
        
        # 如果提供了内容，则生成内容哈希
        if content:
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        else:
            content_hash = random_uuid
        
        # 组合量子基因编码
        quantum_gene = f"QE-{prefix}-{content_hash}-{timestamp}"
        
        logger.debug(f"生成量子基因编码: {quantum_gene}")
        return quantum_gene
    
    def create_qentl_annotation(self, 
                              quantum_gene: str, 
                              entangled_objects: Optional[List[str]] = None,
                              entanglement_strength: float = 0.95,
                              created_at: Optional[str] = None) -> str:
        """
        创建QEntL注释
        
        参数:
            quantum_gene: 量子基因编码
            entangled_objects: 纠缠对象列表
            entanglement_strength: 纠缠强度，0.0-1.0之间的浮点数
            created_at: 创建时间，ISO格式的字符串，默认为当前时间
            
        返回:
            str: QEntL注释文本
        """
        if created_at is None:
            created_at = datetime.datetime.now().isoformat()
        
        # 创建注释基本内容
        annotation = "QEntL: QEntL 2.0 Annotation\n"
        annotation += f"QuantumGene: {quantum_gene}\n"
        annotation += f"CreatedAt: {created_at}\n"
        
        # 添加纠缠对象
        if entangled_objects and len(entangled_objects) > 0:
            annotation += "EntangledObjects:\n"
            for obj in entangled_objects:
                annotation += f"  - {obj}\n"
        
        # 添加纠缠强度
        annotation += f"EntanglementStrength: {entanglement_strength:.2f}\n"
        
        return annotation
    
    def format_annotation_for_file_type(self, annotation: str, file_ext: str) -> str:
        """
        根据文件类型格式化注释
        
        参数:
            annotation: 注释内容
            file_ext: 文件扩展名，包含点，如 .py
            
        返回:
            str: 格式化后的注释
        """
        # 获取文件类型的注释格式
        format_info = self.FILE_COMMENT_FORMATS.get(
            file_ext.lower(), 
            self.FILE_COMMENT_FORMATS['.default']
        )
        
        # 格式化注释
        if format_info['block_start'] and format_info['block_end']:
            # 块注释格式
            formatted = f"{format_info['block_start']}\n{annotation}{format_info['block_end']}\n"
        else:
            # 行注释格式
            lines = annotation.split('\n')
            formatted = ''
            for line in lines:
                if line.strip():
                    formatted += f"{format_info['line']} {line}\n"
                else:
                    formatted += '\n'
        
        return formatted
    
    def process_file(self, file_path: str, force: bool = False) -> Tuple[bool, Optional[str]]:
        """
        处理文件，添加量子基因编码和注释
        
        参数:
            file_path: 文件路径
            force: 是否强制重新生成量子基因编码，即使文件中已存在
            
        返回:
            Tuple[bool, Optional[str]]: (成功标志, 量子基因编码)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                logger.warning(f"文件不存在或不是文件: {file_path}")
                return False, None
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 检查是否已经有量子基因编码
            gene_match = re.search(r'QuantumGene:\s*([^\n]+)', content)
            if gene_match and not force:
                logger.info(f"文件已有量子基因编码: {gene_match.group(1).strip()}")
                return True, gene_match.group(1).strip()
            
            # 获取文件扩展名
            file_ext = os.path.splitext(file_path)[1]
            
            # 获取相对于项目根目录的路径，用作模块名
            rel_path = os.path.relpath(file_path, self.project_root)
            module_name = os.path.dirname(rel_path).replace(os.path.sep, '_') or os.path.basename(file_path)
            
            # 生成量子基因编码
            quantum_gene = self.generate_quantum_gene(module_name, content)
            
            # 创建QEntL注释
            annotation = self.create_qentl_annotation(quantum_gene)
            
            # 格式化注释
            formatted_annotation = self.format_annotation_for_file_type(annotation, file_ext)
            
            # 添加到文件开头
            with open(file_path, 'w', encoding='utf-8') as f:
                # 如果文件是Python文件并且有shebang，保留在第一行
                if file_ext == '.py' and content.startswith('#!'):
                    shebang_end = content.find('\n') + 1
                    f.write(content[:shebang_end])
                    f.write('\n')
                    f.write(formatted_annotation)
                    f.write('\n')
                    f.write(content[shebang_end:])
                else:
                    f.write(formatted_annotation)
                    f.write('\n')
                    f.write(content)
            
            logger.info(f"已处理文件: {file_path}, 量子基因编码: {quantum_gene}")
            return True, quantum_gene
            
        except Exception as e:
            logger.error(f"处理文件失败 {file_path}: {str(e)}")
            return False, None
    
    def scan_directory(self, directory: str, file_types: Optional[List[str]] = None, recursive: bool = True) -> Dict[str, str]:
        """
        扫描目录，处理符合条件的文件
        
        参数:
            directory: 要扫描的目录
            file_types: 要处理的文件扩展名列表，例如 ['.py', '.js']
            recursive: 是否递归扫描子目录
            
        返回:
            Dict[str, str]: 文件路径到量子基因编码的映射
        """
        results = {}
        
        # 默认文件类型
        if file_types is None:
            file_types = list(self.FILE_COMMENT_FORMATS.keys())
        
        # 规范化文件类型
        file_types = [ft.lower() if ft.startswith('.') else f'.{ft.lower()}' for ft in file_types]
        
        logger.info(f"开始扫描目录: {directory}, 文件类型: {file_types}")
        
        # 扫描目录
        if recursive:
            for root, dirs, files in os.walk(directory):
                # 跳过.git、node_modules等目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
                
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in file_types:
                        file_path = os.path.join(root, file)
                        success, quantum_gene = self.process_file(file_path)
                        if success and quantum_gene:
                            results[file_path] = quantum_gene
        else:
            # 只扫描当前目录
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in file_types:
                        success, quantum_gene = self.process_file(file_path)
                        if success and quantum_gene:
                            results[file_path] = quantum_gene
        
        logger.info(f"目录扫描完成: {directory}, 处理了 {len(results)} 个文件")
        return results
    
    def create_qentl_channel_file(self, quantum_gene: str, target_entities: List[str], 
                                 channel_type: str = 'standard', priority: int = 5) -> str:
        """
        创建QEntL信道文件
        
        参数:
            quantum_gene: 量子基因编码
            target_entities: 目标实体列表
            channel_type: 信道类型
            priority: 优先级
            
        返回:
            str: 信道文件的路径
        """
        # 生成信道ID
        channel_id = f"channel_{quantum_gene.replace('QE-', '')}"
        
        # 确保输出目录存在
        channel_dir = os.path.join(self.output_dir, 'channels')
        os.makedirs(channel_dir, exist_ok=True)
        
        # 创建信道文件路径
        channel_file = os.path.join(channel_dir, f"{channel_id}.qent")
        
        # 生成信道文件内容
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = f"""# QEntL Channel Definition - {timestamp}
# Channel: {channel_id}
# Type: {channel_type}
# Version: 2.0
# Generated: {datetime.datetime.now().isoformat()}

channel {{
  id: "{channel_id}",
  type: "{channel_type}",
  quantum_gene: "{quantum_gene}",
  priority: {priority},
  targets: {json.dumps(target_entities)}
}}
"""
        # 写入文件
        with open(channel_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"已创建QEntL信道文件: {channel_file}")
        return channel_file

def create_qentl_file(network_name: str, output_path: Optional[str] = None) -> str:
    """
    创建QEntL网络定义文件
    
    参数:
        network_name: 网络名称
        output_path: 输出路径，如果不提供则使用当前目录
    
    返回:
        str: 创建的文件路径
    """
    # 确定输出路径
    if not output_path:
        output_path = os.path.join(os.getcwd(), f"{network_name}.qent")
    
    # 生成网络ID
    network_id = f"{network_name}_{int(time.time())}"
    
    # 生成网络定义
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    network_def = f"""# QEntL Network Definition - {timestamp}
# Network: {network_name}
# Type: mesh
# Version: 2.0
# Generated: {datetime.datetime.now().isoformat()}

network {network_name} {{
  id: "{network_id}",
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
    id: "{network_name}_entanglement_manager",
    type: "priority_based",
    purification_threshold: 0.95,
    refresh_rate: "100ms",
    priority_levels: 10
  }}
}}
"""
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(network_def)
    
    print(f"已创建QEntL网络定义文件: {output_path}")
    return output_path

# 测试代码
if __name__ == "__main__":
    formatter = QEntLFormatter()
    
    # 测试生成量子基因编码
    quantum_gene = formatter.generate_quantum_gene("test_module", "test content")
    print(f"生成的量子基因编码: {quantum_gene}")
    
    # 测试创建QEntL注释
    annotation = formatter.create_qentl_annotation(
        quantum_gene=quantum_gene,
        entangled_objects=["file1.py", "file2.js"],
        entanglement_strength=0.95
    )
    print(f"创建的QEntL注释:\n{annotation}")
    
    # 测试创建QEntL信道文件
    channel_file = formatter.create_qentl_channel_file(
        quantum_gene=quantum_gene,
        target_entities=["target1", "target2"],
        channel_type="bidirectional"
    )
    print(f"创建的QEntL信道文件: {channel_file}")
    
    # 测试创建QEntL网络定义
    network_file = create_qentl_file("test_network")
    print(f"创建的QEntL网络定义文件: {network_file}")
    
    # 测试扫描目录
    print("尝试扫描当前目录...")
    results = formatter.scan_directory(".", [".py"], recursive=False)
    print(f"扫描结果: {results}") 

'''
量子纠缠信道: ["Ref/ref_core.py"]
'''
"""
量子基因编码: QE-QEN-55C7CAD20059
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
"""