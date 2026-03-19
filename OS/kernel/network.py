#!/usr/bin/env python3
"""
QEntL原生操作系统 - 量子网络管理器
版本: v0.1.0
量子基因编码: QGC-OS-NETWORK-20260308

实现量子纠缠网络通信
"""

from typing import Dict, List, Optional
import time
import uuid

class QuantumNode:
    """量子网络节点"""
    
    def __init__(self, node_id: str, name: str):
        self.node_id = node_id
        self.name = name
        self.address = None
        self.entangled_nodes: List[str] = []  # 纠缠的节点
        self.state = "superposition"
        
    def __repr__(self):
        return f"QuantumNode(id='{self.node_id}', name='{self.name}')"


class QuantumMessage:
    """量子消息"""
    
    def __init__(self, sender: str, receiver: str, content: str):
        self.id = str(uuid.uuid4())[:8]
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = time.time()
        self.quantum_signature = f"QS_{self.id}"
        self.entanglement_level = 0.5


class QuantumNetworkManager:
    """量子网络管理器"""
    
    def __init__(self):
        self.nodes: Dict[str, QuantumNode] = {}
        self.local_node: Optional[QuantumNode] = None
        self.messages: List[QuantumMessage] = []
        
        print("🌐 量子网络管理器初始化完成")
    
    def create_node(self, name: str) -> QuantumNode:
        """创建节点"""
        node_id = str(uuid.uuid4())[:8]
        node = QuantumNode(node_id, name)
        self.nodes[node_id] = node
        
        print(f"✅ 创建节点: {node}")
        return node
    
    def entangle_nodes(self, node_id1: str, node_id2: str):
        """纠缠两个节点"""
        if node_id1 in self.nodes and node_id2 in self.nodes:
            node1 = self.nodes[node_id1]
            node2 = self.nodes[node_id2]
            
            node1.entangled_nodes.append(node_id2)
            node2.entangled_nodes.append(node_id1)
            
            print(f"🔗 节点 {node1.name} 和 {node2.name} 已纠缠")
    
    def send_message(self, sender_id: str, receiver_id: str, content: str) -> QuantumMessage:
        """发送量子消息"""
        if sender_id in self.nodes and receiver_id in self.nodes:
            message = QuantumMessage(sender_id, receiver_id, content)
            self.messages.append(message)
            
            print(f"📨 发送消息: {sender_id} → {receiver_id}")
            print(f"   内容: {content}")
            print(f"   量子签名: {message.quantum_signature}")
            
            return message
        return None
    
    def receive_messages(self, node_id: str) -> List[QuantumMessage]:
        """接收消息"""
        received = [m for m in self.messages if m.receiver == node_id]
        
        if received:
            print(f"\n📬 节点 {node_id} 收到 {len(received)} 条消息:")
            for msg in received:
                print(f"   来自 {msg.sender}: {msg.content}")
        
        return received
    
    def list_nodes(self):
        """列出所有节点"""
        print("\n📋 网络节点列表:")
        print("-" * 50)
        for node_id, node in self.nodes.items():
            entangled = f" → 纠缠: {node.entangled_nodes}" if node.entangled_nodes else ""
            print(f"  {node.name} ({node_id}) {entangled}")
        print("-" * 50)


def demo():
    """演示量子网络"""
    print("\n=== 量子网络演示 ===\n")
    
    nm = QuantumNetworkManager()
    
    # 创建节点
    node1 = nm.create_node("QSM主节点")
    node2 = nm.create_node("SOM经济节点")
    node3 = nm.create_node("WeQ通讯节点")
    
    # 纠缠节点
    nm.entangle_nodes(node1.node_id, node2.node_id)
    nm.entangle_nodes(node1.node_id, node3.node_id)
    
    # 列出节点
    nm.list_nodes()
    
    # 发送消息
    nm.send_message(node1.node_id, node2.node_id, "量子经济数据同步请求")
    nm.send_message(node3.node_id, node1.node_id, "通讯状态报告")
    
    # 接收消息
    nm.receive_messages(node1.node_id)
    nm.receive_messages(node2.node_id)


if __name__ == "__main__":
    demo()
