#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子纠缠网络演示程序
此程序展示如何使用QEntL量子纠缠信道进行节点间的量子态传输
"""

import os
import sys
import time
import json
import random
import logging
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent.parent))

# 导入QEntL模块
from QEntL.core import QEntLEngine
from QEntL.parser import QEntLParser
from QEntL.executor import QEntLExecutor
from QEntL.network import QuantumNetworkAdapter
from QEntL.utils.quantum_state import QuantumState, Qubit

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("qentl_demo.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("QEntL-Demo")

class QuantumEntanglementDemo:
    """量子纠缠网络演示类"""
    
    def __init__(self):
        """初始化量子纠缠网络演示环境"""
        self.engine = QEntLEngine()
        self.parser = QEntLParser()
        self.executor = QEntLExecutor()
        self.network = QuantumNetworkAdapter()
        
        # 加载量子网络定义
        self.qent_file_path = Path(__file__).parent.parent / "qent" / "quantum_network.qent"
        self.load_quantum_network()
        
        # 初始化本地节点
        self.local_node = None
        self.nodes = {}
        self.entangled_pairs = {}
        
    def load_quantum_network(self):
        """加载量子网络定义文件"""
        if not self.qent_file_path.exists():
            logger.error(f"量子网络定义文件不存在: {self.qent_file_path}")
            raise FileNotFoundError(f"量子网络定义文件不存在: {self.qent_file_path}")
        
        logger.info(f"加载量子网络定义文件: {self.qent_file_path}")
        with open(self.qent_file_path, 'r', encoding='utf-8') as f:
            qent_code = f.read()
        
        # 解析QEntL代码
        self.network_def = self.parser.parse(qent_code)
        logger.info("量子网络定义加载完成")
        
    def initialize_local_node(self, node_type="internet"):
        """初始化本地节点
        
        Args:
            node_type: 节点类型，可选值: "internet", "offline", "physical"
        """
        logger.info(f"初始化本地节点，类型: {node_type}")
        
        if node_type == "internet":
            self.local_node = self.create_internet_node("local_internet_node")
        elif node_type == "offline":
            self.local_node = self.create_offline_node("local_offline_node")
        elif node_type == "physical":
            self.local_node = self.create_physical_node("local_physical_node")
        else:
            raise ValueError(f"不支持的节点类型: {node_type}")
        
        self.nodes[self.local_node.id] = self.local_node
        logger.info(f"本地节点初始化完成: {self.local_node.id}")
        
    def create_internet_node(self, node_id):
        """创建互联网连接节点"""
        # 执行QEntL中的InternetNode创建
        node_config = self.network_def.get("InternetNode", {})
        node = self.executor.create_node(
            node_id=node_id,
            node_type="InternetNode",
            config=node_config
        )
        return node
    
    def create_offline_node(self, node_id):
        """创建离线电子节点"""
        # 执行QEntL中的OfflineNode创建
        node_config = self.network_def.get("OfflineNode", {})
        node = self.executor.create_node(
            node_id=node_id,
            node_type="OfflineNode",
            config=node_config
        )
        return node
    
    def create_physical_node(self, node_id):
        """创建物理媒介节点"""
        # 执行QEntL中的PhysicalNode创建
        node_config = self.network_def.get("PhysicalNode", {})
        node = self.executor.create_node(
            node_id=node_id,
            node_type="PhysicalNode",
            config=node_config
        )
        return node
    
    def simulate_network(self, num_nodes=5):
        """模拟网络环境，创建多个不同类型的节点
        
        Args:
            num_nodes: 要创建的节点数量
        """
        logger.info(f"模拟网络环境，创建{num_nodes}个节点")
        
        # 创建不同类型的节点
        for i in range(num_nodes):
            node_type = random.choice(["internet", "offline", "physical"])
            node_id = f"simulated_node_{i}_{node_type}"
            
            if node_type == "internet":
                node = self.create_internet_node(node_id)
            elif node_type == "offline":
                node = self.create_offline_node(node_id)
            else:
                node = self.create_physical_node(node_id)
            
            self.nodes[node_id] = node
            logger.info(f"创建模拟节点: {node_id}，类型: {node_type}")
        
        logger.info(f"网络模拟完成，共有{len(self.nodes)}个节点")
        
    def establish_entanglement(self, node_a_id, node_b_id, strength=0.9):
        """在两个节点之间建立量子纠缠
        
        Args:
            node_a_id: 第一个节点ID
            node_b_id: 第二个节点ID
            strength: 纠缠强度，0.0-1.0之间
        
        Returns:
            bool: 是否成功建立纠缠
        """
        if node_a_id not in self.nodes or node_b_id not in self.nodes:
            logger.error(f"节点不存在: {node_a_id} 或 {node_b_id}")
            return False
        
        node_a = self.nodes[node_a_id]
        node_b = self.nodes[node_b_id]
        
        # 检查节点类型兼容性
        if not self._check_compatibility(node_a, node_b):
            logger.warning(f"节点类型不兼容: {node_a.type} 和 {node_b.type}")
            return False
        
        # 使用QEntL中定义的establish_entanglement函数
        channel_type = self._determine_channel_type(node_a, node_b)
        result = self.executor.execute_function(
            "establish_entanglement",
            [node_a, node_b, strength, channel_type]
        )
        
        if result:
            pair_id = f"{node_a_id}_{node_b_id}"
            self.entangled_pairs[pair_id] = {
                "node_a": node_a,
                "node_b": node_b,
                "strength": strength,
                "created_at": time.time(),
                "channel_type": channel_type
            }
            logger.info(f"成功建立量子纠缠: {node_a_id} <-> {node_b_id}，强度: {strength}")
        else:
            logger.error(f"建立量子纠缠失败: {node_a_id} <-> {node_b_id}")
        
        return result
    
    def transmit_data(self, source_id, target_id, data):
        """通过量子纠缠信道传输数据
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            data: 要传输的数据，可以是字符串或字典
        
        Returns:
            bool: 是否成功传输数据
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            logger.error(f"节点不存在: {source_id} 或 {target_id}")
            return False
        
        # 检查是否存在纠缠
        pair_id = f"{source_id}_{target_id}"
        reverse_pair_id = f"{target_id}_{source_id}"
        
        if pair_id not in self.entangled_pairs and reverse_pair_id not in self.entangled_pairs:
            logger.error(f"节点间不存在量子纠缠: {source_id} <-> {target_id}")
            return False
        
        source_node = self.nodes[source_id]
        target_node = self.nodes[target_id]
        
        # 将数据转换为量子态
        if isinstance(data, dict):
            data_str = json.dumps(data)
        else:
            data_str = str(data)
        
        quantum_state = self._encode_data_to_quantum_state(data_str)
        
        # 使用QEntL中定义的transmit_quantum_state函数
        result = self.executor.execute_function(
            "transmit_quantum_state",
            [source_node, target_node, quantum_state]
        )
        
        if result:
            logger.info(f"成功通过量子纠缠信道传输数据: {source_id} -> {target_id}")
            
            # 更新纠缠强度（每次传输后略有衰减）
            if pair_id in self.entangled_pairs:
                self.entangled_pairs[pair_id]["strength"] *= 0.99
            else:
                self.entangled_pairs[reverse_pair_id]["strength"] *= 0.99
        else:
            logger.error(f"通过量子纠缠信道传输数据失败: {source_id} -> {target_id}")
        
        return result
    
    def detect_quantum_markers(self, scan_area="local", pattern=None):
        """检测量子基因标记
        
        Args:
            scan_area: 扫描区域，可以是"local"或特定路径
            pattern: 要匹配的模式，如果为None则匹配所有
        
        Returns:
            list: 检测到的量子基因标记列表
        """
        if pattern is None:
            pattern = {"type": "any"}
        
        # 使用QEntL中定义的detect_quantum_markers函数
        matches = self.executor.execute_function(
            "detect_quantum_markers",
            [scan_area, pattern]
        )
        
        if matches:
            logger.info(f"检测到{len(matches)}个量子基因标记")
            for i, match in enumerate(matches):
                logger.debug(f"标记 {i+1}: {match}")
        else:
            logger.info("未检测到量子基因标记")
        
        return matches
    
    def monitor_network(self, duration=60, interval=5):
        """监控量子纠缠网络状态
        
        Args:
            duration: 监控持续时间（秒）
            interval: 监控间隔（秒）
        """
        logger.info(f"开始监控量子纠缠网络，持续{duration}秒，间隔{interval}秒")
        
        end_time = time.time() + duration
        while time.time() < end_time:
            # 收集网络状态
            network_stats = self._collect_network_stats()
            
            # 显示网络状态
            logger.info(f"网络状态: 节点数 {network_stats['node_count']}, "
                       f"纠缠对数 {network_stats['entanglement_count']}, "
                       f"平均纠缠强度 {network_stats['avg_entanglement_strength']:.4f}")
            
            # 检查是否需要维护
            if network_stats['avg_entanglement_strength'] < 0.7:
                self._perform_network_maintenance()
            
            # 等待下一个监控周期
            time.sleep(interval)
        
        logger.info("量子纠缠网络监控结束")
    
    def run_demo(self):
        """运行完整演示"""
        try:
            # 初始化本地节点
            self.initialize_local_node("internet")
            
            # 模拟网络环境
            self.simulate_network(5)
            
            # 列出所有节点
            logger.info("网络中的所有节点:")
            for node_id, node in self.nodes.items():
                logger.info(f"- {node_id} ({node.type})")
            
            # 建立量子纠缠
            node_ids = list(self.nodes.keys())
            for i in range(3):  # 建立几对纠缠关系
                if len(node_ids) >= 2:
                    node_a, node_b = random.sample(node_ids, 2)
                    self.establish_entanglement(node_a, node_b)
            
            # 传输数据
            if self.entangled_pairs:
                pair = list(self.entangled_pairs.values())[0]
                source_id = pair["node_a"].id
                target_id = pair["node_b"].id
                
                test_data = {
                    "message": "通过量子纠缠传输的测试数据",
                    "timestamp": time.time(),
                    "source": source_id
                }
                
                self.transmit_data(source_id, target_id, test_data)
            
            # 检测量子基因标记
            self.detect_quantum_markers()
            
            # 监控网络（短时间）
            self.monitor_network(20, 2)
            
            logger.info("量子纠缠网络演示完成")
            
        except Exception as e:
            logger.exception(f"演示过程中发生错误: {str(e)}")
    
    # 辅助方法
    def _check_compatibility(self, node_a, node_b):
        """检查两个节点是否兼容"""
        # 检查节点类型兼容性
        connection_rules = self.network_def.get("EntanglementChannel", {}).get("connection_rules", {})
        
        # 构建规则键
        rule_key = f"{node_a.type.lower()}_to_{node_b.type.lower()}"
        reverse_rule_key = f"{node_b.type.lower()}_to_{node_a.type.lower()}"
        
        # 检查是否存在兼容规则
        return rule_key in connection_rules or reverse_rule_key in connection_rules
    
    def _determine_channel_type(self, node_a, node_b):
        """确定两个节点之间应使用的信道类型"""
        if node_a.type == "InternetNode" and node_b.type == "InternetNode":
            return "tcp_quantum"
        elif "PhysicalNode" in (node_a.type, node_b.type):
            return "field_resonance"
        else:
            return "hybrid_channel"
    
    def _encode_data_to_quantum_state(self, data_str):
        """将数据编码为量子态"""
        # 创建量子态对象
        qstate = QuantumState()
        
        # 将字符串转换为比特，然后编码为量子比特
        for char in data_str:
            # 获取字符的ASCII码，并转换为8位二进制
            bits = format(ord(char), '08b')
            for bit in bits:
                # 创建量子比特并初始化为|0⟩或|1⟩
                qubit = Qubit()
                if bit == '1':
                    qubit.flip()  # 如果是1，翻转到|1⟩态
                qstate.add_qubit(qubit)
        
        return qstate
    
    def _collect_network_stats(self):
        """收集网络统计信息"""
        stats = {
            "node_count": len(self.nodes),
            "entanglement_count": len(self.entangled_pairs),
            "avg_entanglement_strength": 0.0
        }
        
        if self.entangled_pairs:
            total_strength = sum(pair["strength"] for pair in self.entangled_pairs.values())
            stats["avg_entanglement_strength"] = total_strength / len(self.entangled_pairs)
        
        return stats
    
    def _perform_network_maintenance(self):
        """执行网络维护，刷新弱纠缠"""
        logger.info("执行网络维护，刷新弱纠缠...")
        
        for pair_id, pair_info in list(self.entangled_pairs.items()):
            if pair_info["strength"] < 0.7:
                # 刷新纠缠
                node_a = pair_info["node_a"]
                node_b = pair_info["node_b"]
                
                logger.info(f"刷新纠缠: {node_a.id} <-> {node_b.id}，当前强度: {pair_info['strength']:.4f}")
                
                # 重新建立纠缠
                self.establish_entanglement(node_a.id, node_b.id, 0.9)


if __name__ == "__main__":
    print("启动量子纠缠网络演示程序...")
    demo = QuantumEntanglementDemo()
    demo.run_demo() 

"""
"""
量子基因编码: QE-QUA-79A7A15418F0
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
