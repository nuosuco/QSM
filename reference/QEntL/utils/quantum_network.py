#!/usr/bin/env python3
import os
import sys
import time
import json
import enum
import uuid
import logging
import threading
from typing import Dict, List, Set, Any, Optional, Tuple

# 配置日志
logging.basicConfig(
    filename='qentl_network.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("QEntL.Network")

class ChannelType(enum.Enum):
    """量子通信通道类型"""
    QUANTUM = "QUANTUM"        # 用于量子态传输
    CLASSICAL = "CLASSICAL"    # 用于经典信息
    HYBRID = "HYBRID"          # 支持量子和经典

class ChannelState(enum.Enum):
    """通信通道状态"""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    ERROR = "ERROR"
    ENTANGLED = "ENTANGLED"

class QuantumChannel:
    """表示节点间的量子通信通道"""
    
    def __init__(self, 
                 channel_id: str,
                 source_node_id: str, 
                 target_node_id: str,
                 channel_type: ChannelType = ChannelType.QUANTUM):
        self.channel_id = channel_id
        self.source_node_id = source_node_id
        self.target_node_id = target_node_id
        self.channel_type = channel_type
        self.state = ChannelState.CLOSED
        self.creation_time = time.time()
        self.last_activity = self.creation_time
        self.quantum_state = None
        self.entanglement_fidelity = 0.0
        self.metrics = {
            "qubits_sent": 0,
            "qubits_received": 0,
            "classical_bits_sent": 0,
            "classical_bits_received": 0,
            "errors": 0,
            "entanglements_created": 0
        }
    
    def open(self) -> bool:
        """打开通信通道"""
        if self.state == ChannelState.CLOSED:
            self.state = ChannelState.OPEN
            self.last_activity = time.time()
            logger.info(f"通道 {self.channel_id} 在 {self.source_node_id} 和 {self.target_node_id} 之间已打开")
            return True
        return False
    
    def close(self) -> bool:
        """关闭通道"""
        if self.state != ChannelState.CLOSED:
            self.state = ChannelState.CLOSED
            self.last_activity = time.time()
            logger.info(f"通道 {self.channel_id} 在 {self.source_node_id} 和 {self.target_node_id} 之间已关闭")
            return True
        return False
    
    def entangle(self, fidelity: float = 0.95) -> bool:
        """在节点间创建量子纠缠"""
        if self.state == ChannelState.OPEN and self.channel_type != ChannelType.CLASSICAL:
            self.state = ChannelState.ENTANGLED
            self.entanglement_fidelity = fidelity
            self.quantum_state = "bell_state"  # 简化表示
            self.last_activity = time.time()
            self.metrics["entanglements_created"] += 1
            logger.info(f"在通道 {self.channel_id} 上创建了纠缠，保真度为 {fidelity}")
            return True
        return False
    
    def send_qubit(self, qubit_data: Any) -> bool:
        """通过通道发送量子比特"""
        if self.state == ChannelState.OPEN and self.channel_type != ChannelType.CLASSICAL:
            # 模拟量子比特传输
            self.last_activity = time.time()
            self.metrics["qubits_sent"] += 1
            logger.info(f"在通道 {self.channel_id} 上发送了量子比特")
            return True
        return False
    
    def receive_qubit(self) -> Optional[Any]:
        """从通道接收量子比特"""
        if self.state == ChannelState.OPEN and self.channel_type != ChannelType.CLASSICAL:
            # 模拟量子比特接收
            self.last_activity = time.time()
            self.metrics["qubits_received"] += 1
            logger.info(f"在通道 {self.channel_id} 上接收了量子比特")
            return {"state": "random_state"}  # 简化
        return None
    
    def send_classical(self, data: Any) -> bool:
        """通过通道发送经典信息"""
        if self.state == ChannelState.OPEN and self.channel_type != ChannelType.QUANTUM:
            # 模拟经典传输
            self.last_activity = time.time()
            self.metrics["classical_bits_sent"] += len(str(data))
            logger.info(f"在通道 {self.channel_id} 上发送了经典数据")
            return True
        return False
    
    def measure_entanglement(self) -> Tuple[Any, Any]:
        """测量纠缠态，导致纠缠坍缩"""
        if self.state == ChannelState.ENTANGLED:
            # 模拟测量
            result_a = 0 if time.time() % 2 == 0 else 1  # 随机结果
            result_b = result_a  # 简化为完美相关
            
            self.state = ChannelState.OPEN
            self.quantum_state = None
            self.entanglement_fidelity = 0.0
            self.last_activity = time.time()
            
            logger.info(f"在通道 {self.channel_id} 上测量了纠缠: {result_a}, {result_b}")
            return (result_a, result_b)
        
        return (None, None)
    
    def to_dict(self) -> Dict[str, Any]:
        """将通道转换为字典表示"""
        return {
            "channel_id": self.channel_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "channel_type": self.channel_type.value,
            "state": self.state.value,
            "creation_time": self.creation_time,
            "last_activity": self.last_activity,
            "entanglement_fidelity": self.entanglement_fidelity,
            "metrics": self.metrics
        }

class QuantumNode:
    """表示量子网络中的节点"""
    
    def __init__(self, node_id: str, name: str = ""):
        self.node_id = node_id
        self.name = name or f"节点-{node_id}"
        self.channels: Dict[str, QuantumChannel] = {}
        self.creation_time = time.time()
        self.last_activity = self.creation_time
        self.qubits_available = 10  # 简化表示
        self.is_active = True
        self.capabilities = []
    
    def add_channel(self, channel: QuantumChannel) -> bool:
        """向节点添加通道"""
        if channel.channel_id not in self.channels:
            self.channels[channel.channel_id] = channel
            self.last_activity = time.time()
            logger.info(f"通道 {channel.channel_id} 已添加到节点 {self.node_id}")
            return True
        return False
    
    def remove_channel(self, channel_id: str) -> bool:
        """从节点移除通道"""
        if channel_id in self.channels:
            del self.channels[channel_id]
            self.last_activity = time.time()
            logger.info(f"通道 {channel_id} 已从节点 {self.node_id} 移除")
            return True
        return False
    
    def get_connected_nodes(self) -> Set[str]:
        """获取此节点连接的节点ID集合"""
        connected = set()
        for channel_id, channel in self.channels.items():
            if channel.source_node_id == self.node_id:
                connected.add(channel.target_node_id)
            else:
                connected.add(channel.source_node_id)
        return connected
    
    def get_channel_to_node(self, target_node_id: str) -> Optional[QuantumChannel]:
        """获取连接到指定节点的通道"""
        for channel_id, channel in self.channels.items():
            if (channel.source_node_id == self.node_id and channel.target_node_id == target_node_id) or \
               (channel.source_node_id == target_node_id and channel.target_node_id == self.node_id):
                return channel
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """将节点转换为字典表示"""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "creation_time": self.creation_time,
            "last_activity": self.last_activity,
            "qubits_available": self.qubits_available,
            "is_active": self.is_active,
            "capabilities": self.capabilities,
            "channels": [c.to_dict() for c in self.channels.values()]
        }

class QuantumNetwork:
    """管理量子节点网络及其连接"""
    
    def __init__(self):
        self.nodes: Dict[str, QuantumNode] = {}
        self.creation_time = time.time()
        self.last_activity = self.creation_time
        self.network_id = str(uuid.uuid4())
    
    def create_node(self, node_id: Optional[str] = None, name: str = "") -> str:
        """在网络中创建新节点"""
        if node_id is None:
            node_id = str(uuid.uuid4())
        
        if node_id in self.nodes:
            logger.warning(f"节点 {node_id} 已存在")
            return node_id
        
        self.nodes[node_id] = QuantumNode(node_id, name)
        self.last_activity = time.time()
        logger.info(f"节点 {node_id} 已创建")
        return node_id
    
    def remove_node(self, node_id: str) -> bool:
        """从网络中移除节点"""
        if node_id in self.nodes:
            # 首先，移除连接到此节点的所有通道
            channels_to_remove = []
            
            # 识别在其他节点中连接到此节点的通道
            for other_node_id, other_node in self.nodes.items():
                if other_node_id == node_id:
                    continue
                    
                for channel_id, channel in other_node.channels.items():
                    if channel.source_node_id == node_id or channel.target_node_id == node_id:
                        channels_to_remove.append((other_node_id, channel_id))
            
            # 移除已识别的通道
            for other_node_id, channel_id in channels_to_remove:
                self.nodes[other_node_id].remove_channel(channel_id)
            
            # 最后移除节点
            del self.nodes[node_id]
            self.last_activity = time.time()
            logger.info(f"节点 {node_id} 已从网络移除")
            return True
        
        return False
    
    def connect_nodes(self, 
                      source_node_id: str, 
                      target_node_id: str, 
                      channel_type: ChannelType = ChannelType.QUANTUM) -> Optional[str]:
        """使用量子通道连接两个节点"""
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            logger.error(f"无法连接：一个或两个节点不存在")
            return None
        
        if source_node_id == target_node_id:
            logger.error(f"无法将节点连接到自身")
            return None
        
        # 检查这些节点是否已连接
        source_node = self.nodes[source_node_id]
        if target_node_id in source_node.get_connected_nodes():
            logger.warning(f"节点 {source_node_id} 和 {target_node_id} 已经连接")
            
            # 返回现有通道
            channel = source_node.get_channel_to_node(target_node_id)
            if channel:
                return channel.channel_id
            
        # 创建新通道
        channel_id = str(uuid.uuid4())
        new_channel = QuantumChannel(channel_id, source_node_id, target_node_id, channel_type)
        
        # 将通道添加到两个节点
        self.nodes[source_node_id].add_channel(new_channel)
        self.nodes[target_node_id].add_channel(new_channel)
        
        self.last_activity = time.time()
        logger.info(f"在 {source_node_id} 和 {target_node_id} 之间创建了通道 {channel_id}")
        return channel_id
    
    def disconnect_nodes(self, source_node_id: str, target_node_id: str) -> bool:
        """通过移除共享通道断开两个节点的连接"""
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            logger.error(f"无法断开连接：一个或两个节点不存在")
            return False
        
        source_node = self.nodes[source_node_id]
        channel = source_node.get_channel_to_node(target_node_id)
        
        if not channel:
            logger.warning(f"{source_node_id} 和 {target_node_id} 之间不存在通道")
            return False
        
        # 从两个节点移除通道
        channel_id = channel.channel_id
        self.nodes[source_node_id].remove_channel(channel_id)
        self.nodes[target_node_id].remove_channel(channel_id)
        
        self.last_activity = time.time()
        logger.info(f"移除了 {source_node_id} 和 {target_node_id} 之间的通道 {channel_id}")
        return True
    
    def open_connection(self, source_node_id: str, target_node_id: str) -> bool:
        """打开两个节点间的通信通道"""
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            logger.error(f"无法打开连接：一个或两个节点不存在")
            return False
        
        source_node = self.nodes[source_node_id]
        channel = source_node.get_channel_to_node(target_node_id)
        
        if not channel:
            logger.warning(f"{source_node_id} 和 {target_node_id} 之间不存在通道")
            return False
        
        success = channel.open()
        if success:
            self.last_activity = time.time()
        
        return success
    
    def close_connection(self, source_node_id: str, target_node_id: str) -> bool:
        """关闭两个节点间的通信通道"""
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            logger.error(f"无法关闭连接：一个或两个节点不存在")
            return False
        
        source_node = self.nodes[source_node_id]
        channel = source_node.get_channel_to_node(target_node_id)
        
        if not channel:
            logger.warning(f"{source_node_id} 和 {target_node_id} 之间不存在通道")
            return False
        
        success = channel.close()
        if success:
            self.last_activity = time.time()
        
        return success
    
    def create_entanglement(self, source_node_id: str, target_node_id: str, fidelity: float = 0.95) -> bool:
        """在两个节点间创建量子纠缠"""
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            logger.error(f"无法创建纠缠：一个或两个节点不存在")
            return False
        
        source_node = self.nodes[source_node_id]
        channel = source_node.get_channel_to_node(target_node_id)
        
        if not channel:
            logger.warning(f"{source_node_id} 和 {target_node_id} 之间不存在通道")
            return False
        
        success = channel.entangle(fidelity)
        if success:
            self.last_activity = time.time()
        
        return success
    
    def measure_entanglement(self, source_node_id: str, target_node_id: str) -> Tuple[Any, Any]:
        """测量两个节点间的纠缠"""
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            logger.error(f"无法测量纠缠：一个或两个节点不存在")
            return (None, None)
        
        source_node = self.nodes[source_node_id]
        channel = source_node.get_channel_to_node(target_node_id)
        
        if not channel:
            logger.warning(f"{source_node_id} 和 {target_node_id} 之间不存在通道")
            return (None, None)
        
        results = channel.measure_entanglement()
        if results[0] is not None:
            self.last_activity = time.time()
        
        return results
    
    def send_qubit(self, source_node_id: str, target_node_id: str, qubit_data: Any) -> bool:
        """从一个节点向另一个节点发送量子比特"""
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            logger.error(f"无法发送量子比特：一个或两个节点不存在")
            return False
        
        source_node = self.nodes[source_node_id]
        channel = source_node.get_channel_to_node(target_node_id)
        
        if not channel:
            logger.warning(f"{source_node_id} 和 {target_node_id} 之间不存在通道")
            return False
        
        success = channel.send_qubit(qubit_data)
        if success:
            self.last_activity = time.time()
        
        return success
    
    def save_network_config(self, filename: str) -> bool:
        """将网络配置保存到JSON文件"""
        try:
            config = {
                "network_id": self.network_id,
                "creation_time": self.creation_time,
                "last_activity": self.last_activity,
                "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()}
            }
            
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"网络配置已保存到 {filename}")
            return True
        except Exception as e:
            logger.error(f"保存网络配置时出错：{e}")
            return False
    
    def load_network_config(self, filename: str) -> bool:
        """从JSON文件加载网络配置"""
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            
            self.network_id = config.get("network_id", str(uuid.uuid4()))
            self.creation_time = config.get("creation_time", time.time())
            self.last_activity = config.get("last_activity", time.time())
            
            # 清除现有节点
            self.nodes = {}
            
            # 首先，创建所有节点
            for node_id, node_data in config.get("nodes", {}).items():
                self.create_node(node_id, node_data.get("name", ""))
                
                # 设置节点属性
                if node_id in self.nodes:
                    node = self.nodes[node_id]
                    node.creation_time = node_data.get("creation_time", time.time())
                    node.last_activity = node_data.get("last_activity", time.time())
                    node.qubits_available = node_data.get("qubits_available", 10)
                    node.is_active = node_data.get("is_active", True)
                    node.capabilities = node_data.get("capabilities", [])
            
            # 然后在节点间创建连接
            for node_id, node_data in config.get("nodes", {}).items():
                for channel_data in node_data.get("channels", []):
                    source_id = channel_data.get("source_node_id")
                    target_id = channel_data.get("target_node_id")
                    
                    # 如果两个节点都存在且源是当前节点，则创建通道
                    if (source_id == node_id and 
                        source_id in self.nodes and 
                        target_id in self.nodes):
                        
                        # 获取通道类型
                        channel_type_str = channel_data.get("channel_type", "QUANTUM")
                        try:
                            channel_type = ChannelType[channel_type_str]
                        except (KeyError, ValueError):
                            channel_type = ChannelType.QUANTUM
                        
                        # 连接节点
                        channel_id = self.connect_nodes(source_id, target_id, channel_type)
                        
                        # 如果连接成功，设置通道状态
                        if channel_id:
                            source_node = self.nodes[source_id]
                            channel = source_node.channels.get(channel_id)
                            
                            if channel:
                                # 获取通道状态
                                state_str = channel_data.get("state", "CLOSED")
                                try:
                                    state = ChannelState[state_str]
                                except (KeyError, ValueError):
                                    state = ChannelState.CLOSED
                                
                                channel.state = state
                                channel.creation_time = channel_data.get("creation_time", time.time())
                                channel.last_activity = channel_data.get("last_activity", time.time())
                                channel.entanglement_fidelity = channel_data.get("entanglement_fidelity", 0.0)
                                channel.metrics = channel_data.get("metrics", {})
            
            logger.info(f"网络配置已从 {filename} 加载")
            return True
        except Exception as e:
            logger.error(f"加载网络配置时出错：{e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """将网络转换为字典表示"""
        return {
            "network_id": self.network_id,
            "creation_time": self.creation_time,
            "last_activity": self.last_activity,
            "node_count": len(self.nodes),
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()}
        }

def main():
    """测试量子网络实现"""
    # 创建示例网络
    network = QuantumNetwork()
    
    # 添加节点
    node1 = network.create_node(name="量子实验室")
    node2 = network.create_node(name="量子卫星")
    node3 = network.create_node(name="数据中心")
    
    # 连接节点
    channel1 = network.connect_nodes(node1, node2)
    channel2 = network.connect_nodes(node2, node3)
    channel3 = network.connect_nodes(node1, node3, ChannelType.CLASSICAL)
    
    # 打开连接
    network.open_connection(node1, node2)
    network.open_connection(node2, node3)
    
    # 创建纠缠
    network.create_entanglement(node1, node2)
    
    # 保存配置
    network.save_network_config("quantum_network_config.json")
    
    print("网络已创建并保存")
    print(f"网络ID: {network.network_id}")
    print(f"节点数量: {len(network.nodes)}")

if __name__ == "__main__":
    main() 

"""
"""
量子基因编码: QE-QUA-2E49A365D0EC
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
