#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WeQ输出模块 - 使用QEntL 2.0语法生成量子基因编码和量子纠缠关系
"""

import os
import sys
import json
import uuid
import time
import logging
import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from Ref.utils.quantum_gene_marker import RefQuantumGeneMarker
    from Ref.utils.log_config import get_logger
except ImportError:
    print("无法导入Ref模块，请确保安装了所有依赖")
    sys.exit(1)

# 配置日志
logger = get_logger('weq_output', log_file='weq_output.log', level='INFO')

class WeQOutput:
    """WeQ输出模块类，负责生成QEntL格式的输出文件和建立量子纠缠关系"""
    
    def __init__(self, output_dir=None):
        """
        初始化输出模块
        
        Args:
            output_dir: 输出目录，默认为WeQ/output
        """
        self.output_dir = output_dir or os.path.join(
            Path(__file__).parent.parent, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.qgm = RefQuantumGeneMarker()
        self.networks = {}
        self.channels = {}
        self.entanglement_pairs = []
        
        logger.info(f"WeQ输出模块初始化完成，输出目录: {self.output_dir}")
    
    def create_qentl_file(self, file_name, content, metadata=None):
        """
        创建QEntL文件
        
        Args:
            file_name: 文件名
            content: 文件内容
            metadata: 元数据字典
        
        Returns:
            file_path: 创建的文件路径
        """
        if not file_name.endswith('.qentl'):
            file_name += '.qentl'
        
        file_path = os.path.join(self.output_dir, file_name)
        
        # 生成量子基因ID
        gene_id = f"QE-WeQ-{str(uuid.uuid4())[:8]}-{int(time.time())}"
        created_at = datetime.datetime.now().isoformat()
        
        # 组装QEntL头部
        header = [
            f"QEntL: QEntL 2.0 Output File",
            f"QuantumGene: {gene_id}",
            f"CreatedAt: {created_at}",
            f"EntanglementStrength: 1.0"
        ]
        
        # 添加元数据
        if metadata:
            for key, value in metadata.items():
                header.append(f"{key}: {value}")
        
        # 组装完整内容
        full_content = "\n".join(header) + "\n\n" + content
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        logger.info(f"已创建QEntL文件: {file_path}")
        
        # 为文件添加量子基因标记
        self.qgm.add_quantum_gene_marker(file_path, gene_id)
        
        return file_path
    
    def create_network_definition(self, network_id, network_type, description, nodes, connections):
        """
        创建量子网络定义
        
        Args:
            network_id: 网络ID
            network_type: 网络类型
            description: 网络描述
            nodes: 节点列表
            connections: 连接列表
        
        Returns:
            network_content: 网络定义内容
        """
        network = {
            'id': network_id,
            'type': network_type,
            'version': '2.0',
            'description': description,
            'nodes': nodes,
            'connections': connections,
            'properties': {
                'maxEntanglementDistance': 1000,
                'purificationThreshold': 0.9,
                'errorCorrectionEnabled': True
            }
        }
        
        # 保存网络定义
        self.networks[network_id] = network
        
        # 格式化网络定义为QEntL语法
        network_lines = [
            f"network {network_type.capitalize()}Network {{",
            f"  id: \"{network_id}\",",
            f"  type: \"{network_type}\",",
            f"  version: \"2.0\",",
            f"  description: \"{description}\",",
            "  ",
            "  nodes: ["
        ]
        
        # 添加节点
        for node in nodes:
            node_line = f"    {{ id: \"{node['id']}\", type: \"{node['type']}\", address: \"{node['address']}\" }}"
            if node != nodes[-1]:
                node_line += ","
            network_lines.append(node_line)
        
        network_lines.append("  ],")
        network_lines.append("  ")
        network_lines.append("  connections: [")
        
        # 添加连接
        for conn in connections:
            conn_line = f"    {{ from: \"{conn['from']}\", to: \"{conn['to']}\", channel: \"{conn['channel']}\" }}"
            if conn != connections[-1]:
                conn_line += ","
            network_lines.append(conn_line)
        
        network_lines.extend([
            "  ],",
            "  ",
            "  properties: {",
            "    maxEntanglementDistance: 1000,",
            "    purificationThreshold: 0.9,",
            "    errorCorrectionEnabled: true",
            "  }",
            "}"
        ])
        
        return "\n".join(network_lines)
    
    def create_channel_definition(self, channel_id, channel_type, endpoints, properties=None):
        """
        创建量子信道定义
        
        Args:
            channel_id: 信道ID
            channel_type: 信道类型
            endpoints: 端点列表
            properties: 信道属性
        
        Returns:
            channel_content: 信道定义内容
        """
        if properties is None:
            properties = {
                'bandwidth': '100 qubit/s',
                'latency': '5 ms',
                'errorRate': 0.01,
                'securityLevel': 'quantum_key'
            }
        
        channel = {
            'id': channel_id,
            'type': channel_type,
            'priority': 5,
            'properties': properties,
            'endpoints': endpoints
        }
        
        # 保存信道定义
        self.channels[channel_id] = channel
        
        # 格式化信道定义为QEntL语法
        channel_lines = [
            "channel {",
            f"  id: \"{channel_id}\",",
            f"  type: \"{channel_type}\",",
            "  priority: 5,",
            "  ",
            "  properties: {"
        ]
        
        # 添加属性
        for key, value in properties.items():
            prop_line = f"    {key}: "
            if isinstance(value, str):
                prop_line += f"\"{value}\""
            else:
                prop_line += f"{str(value).lower()}"
            if key != list(properties.keys())[-1]:
                prop_line += ","
            channel_lines.append(prop_line)
        
        channel_lines.append("  },")
        channel_lines.append("  ")
        channel_lines.append("  endpoints: [")
        
        # 添加端点
        for ep in endpoints:
            ep_line = f"    {{ node: \"{ep['node']}\", port: {ep['port']} }}"
            if ep != endpoints[-1]:
                ep_line += ","
            channel_lines.append(ep_line)
        
        channel_lines.extend([
            "  ]",
            "}"
        ])
        
        return "\n".join(channel_lines)
    
    def create_entanglement_pair(self, source_file, target_file, strength=0.95, properties=None):
        """
        创建量子纠缠对
        
        Args:
            source_file: 源文件路径
            target_file: 目标文件路径
            strength: 纠缠强度
            properties: 纠缠属性
        
        Returns:
            entanglement_content: 纠缠对定义内容
        """
        if properties is None:
            properties = {
                'lifetime': '1 hour',
                'purificationLevel': 3,
                'errorCorrectionScheme': 'surface_code'
            }
        
        # 检查文件是否已有量子基因标记
        source_gene = self.qgm.find_quantum_gene_marker(source_file)
        target_gene = self.qgm.find_quantum_gene_marker(target_file)
        
        if not source_gene:
            source_gene = f"QE-SRC-{str(uuid.uuid4())[:8]}-{int(time.time())}"
            self.qgm.add_quantum_gene_marker(source_file, source_gene)
        
        if not target_gene:
            target_gene = f"QE-TGT-{str(uuid.uuid4())[:8]}-{int(time.time())}"
            self.qgm.add_quantum_gene_marker(target_file, target_gene)
        
        pair_id = f"ep_{str(uuid.uuid4())[:8]}"
        
        entanglement_pair = {
            'id': pair_id,
            'source': source_gene,
            'target': target_gene,
            'strength': strength,
            'properties': properties
        }
        
        # 保存纠缠对定义
        self.entanglement_pairs.append(entanglement_pair)
        
        # 格式化纠缠对定义为QEntL语法
        pair_lines = [
            "entanglement_pair {",
            f"  id: \"{pair_id}\",",
            f"  source: \"{source_gene}\",",
            f"  target: \"{target_gene}\",",
            f"  strength: {strength},",
            "  ",
            "  properties: {"
        ]
        
        # 添加属性
        for key, value in properties.items():
            prop_line = f"    {key}: "
            if isinstance(value, str):
                prop_line += f"\"{value}\""
            else:
                prop_line += f"{value}"
            if key != list(properties.keys())[-1]:
                prop_line += ","
            pair_lines.append(prop_line)
        
        pair_lines.extend([
            "  }",
            "}"
        ])
        
        # 创建纠缠关系文件
        entanglement_content = "\n".join(pair_lines)
        file_name = f"entanglement_{pair_id}.qentl"
        entanglement_file = self.create_qentl_file(
            file_name, 
            entanglement_content,
            {
                'SourceFile': os.path.basename(source_file),
                'TargetFile': os.path.basename(target_file)
            }
        )
        
        logger.info(f"已创建量子纠缠对: {pair_id} 连接 {source_gene} 和 {target_gene}")
        
        return entanglement_content
    
    def create_event_handler(self, handler_id, event_type, trigger_condition, nodes, action_type, action_params):
        """
        创建事件处理器
        
        Args:
            handler_id: 处理器ID
            event_type: 事件类型
            trigger_condition: 触发条件
            nodes: 节点列表
            action_type: 动作类型
            action_params: 动作参数
        
        Returns:
            handler_content: 处理器定义内容
        """
        handler_lines = [
            "event_handler {",
            f"  id: \"{handler_id}\",",
            f"  type: \"{event_type}\",",
            "  ",
            "  trigger: {",
            f"    condition: \"{trigger_condition}\",",
            "    nodes: ["
        ]
        
        # 添加节点
        for node in nodes:
            node_line = f"      \"{node}\""
            if node != nodes[-1]:
                node_line += ","
            handler_lines.append(node_line)
        
        handler_lines.extend([
            "    ]",
            "  },",
            "  ",
            "  action: {",
            f"    type: \"{action_type}\",",
            "    parameters: {"
        ])
        
        # 添加动作参数
        for key, value in action_params.items():
            param_line = f"      {key}: "
            if isinstance(value, str):
                param_line += f"\"{value}\""
            else:
                param_line += f"{str(value).lower()}"
            if key != list(action_params.keys())[-1]:
                param_line += ","
            handler_lines.append(param_line)
        
        handler_lines.extend([
            "    }",
            "  }",
            "}"
        ])
        
        return "\n".join(handler_lines)
    
    def generate_config_file(self, auto_repair=True, entanglement_threshold=0.85, log_level="info"):
        """
        生成QEntL配置文件
        
        Args:
            auto_repair: 是否自动修复
            entanglement_threshold: 纠缠阈值
            log_level: 日志级别
        
        Returns:
            config_file: 配置文件路径
        """
        config = {
            'version': '2.0',
            'auto_repair': auto_repair,
            'syntax_validation': True,
            'entanglement_threshold': entanglement_threshold,
            'default_network_type': 'mesh',
            'default_channel_type': 'standard',
            'logging': {
                'level': log_level,
                'file': 'qentl_operations.log'
            },
            'paths': {
                'networks': './networks',
                'channels': './channels',
                'templates': './templates'
            }
        }
        
        # 转换为QEntL配置语法
        config_lines = [
            "version: \"2.0\"",
            f"auto_repair: {str(auto_repair).lower()}",
            "syntax_validation: true",
            f"entanglement_threshold: {entanglement_threshold}",
            "default_network_type: \"mesh\"",
            "default_channel_type: \"standard\"",
            "logging: {",
            f"  level: \"{log_level}\",",
            "  file: \"qentl_operations.log\"",
            "}",
            "paths: {",
<<<<<<< HEAD
            "  networks: \"./networks/",",
            "  channels: \"./channels/",",
            "  templates: \"./templates/"",
=======
            "  networks: \"./networks\",",
            "  channels: \"./channels\",",
            "  templates: \"./templates\"",
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
            "}"
        ]
        
        config_content = "\n".join(config_lines)
        file_path = self.create_qentl_file(
            "qentl.config", 
            config_content,
            {
                'ConfigType': 'QEntL System Configuration',
                'ConfigFormat': 'QEntL 2.0'
            }
        )
        
        logger.info(f"已生成QEntL配置文件: {file_path}")
        
        return file_path
    
    def export_to_json(self, output_file="weq_output.json"):
        """
        将当前所有网络、信道和纠缠对导出为JSON
        
        Args:
            output_file: 输出JSON文件名
        
        Returns:
            json_file: JSON文件路径
        """
        data = {
            'networks': self.networks,
            'channels': self.channels,
            'entanglement_pairs': self.entanglement_pairs,
            'generated_at': datetime.datetime.now().isoformat(),
            'version': '2.0'
        }
        
        json_file = os.path.join(self.output_dir, output_file)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"已导出QEntL数据到JSON: {json_file}")
        
        return json_file


# 如果直接运行此模块，创建示例输出
if __name__ == "__main__":
    print("WeQ输出模块 - 使用QEntL 2.0语法")
    
    # 示例：创建输出模块实例
    output = WeQOutput()
    
    # 示例：创建网络定义
    nodes = [
        {'id': 'node1', 'type': 'quantum_processor', 'address': 'qp://node1.local'},
        {'id': 'node2', 'type': 'quantum_memory', 'address': 'qm://node2.local'},
        {'id': 'node3', 'type': 'quantum_router', 'address': 'qr://node3.local'}
    ]
    
    connections = [
        {'from': 'node1', 'to': 'node2', 'channel': 'channel1'},
        {'from': 'node2', 'to': 'node3', 'channel': 'channel2'},
        {'from': 'node3', 'to': 'node1', 'channel': 'channel3'}
    ]
    
    network_content = output.create_network_definition(
        'weq_network_001', 
        'mesh', 
        '示例网格型量子网络', 
        nodes, 
        connections
    )
    
    # 创建网络定义文件
    network_file = output.create_qentl_file(
        'example_network.qentl', 
        network_content,
        {
            'NetworkType': 'Mesh',
            'NodeCount': '3'
        }
    )
    
    # 生成配置文件
    config_file = output.generate_config_file()
    
    print(f"示例文件已创建:")
    print(f"- 网络定义: {network_file}")
    print(f"- 配置文件: {config_file}")
    print(f"输出目录: {output.output_dir}") 
"""
量子基因编码: QE-OUT-9852B2DE530F
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
"""