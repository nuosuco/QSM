#!/usr/bin/env python3
import sys
import os
import time
import logging
import argparse
import random
from typing import Dict, List, Any

# 添加父目录到路径以导入QEntL模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.quantum_network import (
    QuantumNetwork, 
    ChannelType,
    ChannelState
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("QEntL.Demo")

class QuantumNetworkDemo:
    """量子网络功能演示"""
    
    def __init__(self):
        self.network = QuantumNetwork()
        self.demo_nodes: Dict[str, str] = {}  # name -> node_id
    
    def setup_demo_network(self):
        """设置演示网络，包含多个节点"""
        logger.info("正在设置演示量子网络...")
        
        # 创建节点
        self.demo_nodes["quantum_lab"] = self.network.create_node(name="量子实验室")
        self.demo_nodes["satellite"] = self.network.create_node(name="量子卫星")
        self.demo_nodes["data_center"] = self.network.create_node(name="安全数据中心")
        self.demo_nodes["relay"] = self.network.create_node(name="量子中继")
        self.demo_nodes["end_user"] = self.network.create_node(name="终端用户")
        
        # 按网络拓扑连接节点
        self._connect_nodes("quantum_lab", "satellite", ChannelType.QUANTUM)
        self._connect_nodes("satellite", "data_center", ChannelType.QUANTUM)
        self._connect_nodes("satellite", "relay", ChannelType.QUANTUM)
        self._connect_nodes("relay", "end_user", ChannelType.QUANTUM)
        self._connect_nodes("quantum_lab", "data_center", ChannelType.CLASSICAL)
        
        # 打开连接
        self._open_connection("quantum_lab", "satellite")
        self._open_connection("satellite", "data_center")
        self._open_connection("satellite", "relay")
        self._open_connection("relay", "end_user")
        self._open_connection("quantum_lab", "data_center")
        
        logger.info("演示网络设置完成！")
    
    def _connect_nodes(self, node1_name: str, node2_name: str, channel_type: ChannelType):
        """按名称连接节点的辅助函数"""
        if node1_name not in self.demo_nodes or node2_name not in self.demo_nodes:
            logger.error(f"无法连接 - 未找到一个或两个节点: {node1_name}, {node2_name}")
            return False
        
        node1_id = self.demo_nodes[node1_name]
        node2_id = self.demo_nodes[node2_name]
        
        success, _ = self.network.connect_nodes(node1_id, node2_id, channel_type)
        if success:
            logger.info(f"已连接 {node1_name} 到 {node2_name}，使用{channel_type.value}通道")
        return success
    
    def _open_connection(self, node1_name: str, node2_name: str):
        """按名称打开节点间连接的辅助函数"""
        if node1_name not in self.demo_nodes or node2_name not in self.demo_nodes:
            return False
        
        node1_id = self.demo_nodes[node1_name]
        node2_id = self.demo_nodes[node2_name]
        
        success = self.network.open_connection(node1_id, node2_id)
        if success:
            logger.info(f"已打开 {node1_name} 和 {node2_name} 之间的连接")
        return success
    
    def run_qkd_demo(self):
        """量子密钥分发演示"""
        logger.info("\n===== 量子密钥分发演示 =====")
        
        lab_id = self.demo_nodes["quantum_lab"]
        data_center_id = self.demo_nodes["data_center"]
        
        result = self.network.run_protocol("quantum_key_distribution", {
            "source_id": lab_id,
            "target_id": data_center_id,
            "key_length": 16
        })
        
        if result["success"]:
            data = result["data"]
            logger.info(f"量子密钥分发成功生成 {data['key_length']} 位安全密钥")
            logger.info(f"匹配基底数: {data['matching_bases_count']} (共16个)")
            logger.info(f"筛选后密钥: {data['sifted_key']}")
            
            # 转换为字符串表示
            key_string = ''.join(str(bit) for bit in data['sifted_key'])
            logger.info(f"密钥(二进制): {key_string}")
            
            # 模拟使用密钥进行加密
            message = "量子安全传输"
            logger.info(f"使用密钥加密消息: '{message}'")
            
            # 模拟简化的一次性密码本加密(仅用于演示)
            binary_message = ''.join(format(ord(char), '08b') for char in message)
            logger.info(f"二进制消息: {binary_message[:20]}...")
            
            # 扩展密钥(在真实量子密钥分发中，我们会生成更长的密钥)
            extended_key = data['sifted_key'] * (len(binary_message) // len(data['sifted_key']) + 1)
            extended_key = extended_key[:len(binary_message)]
            
            # XOR加密(模拟)
            logger.info("加密完成 - 安全通道已建立！")
        else:
            logger.error(f"量子密钥分发失败: {result.get('error', '未知错误')}")
    
    def run_teleportation_demo(self):
        """量子隐形传态演示"""
        logger.info("\n===== 量子隐形传态演示 =====")
        
        lab_id = self.demo_nodes["quantum_lab"]
        end_user_id = self.demo_nodes["end_user"]
        
        # 传送叠加态
        state_to_teleport = [0.7071, 0.7071]  # |+⟩ 态
        logger.info(f"准备从量子实验室传送 |+⟩ 态到终端用户")
        
        # 通过量子网络运行隐形传态
        result = self.network.run_protocol("teleportation", {
            "source_id": lab_id,
            "target_id": end_user_id,
            "state": state_to_teleport
        })
        
        if result["success"]:
            logger.info("隐形传态成功！")
            logger.info(f"原始状态: |+⟩")
            logger.info(f"传送量子比特的测量结果: {result['data']['teleported_result']}")
            logger.info("注意: 在实际量子系统中，除非需要使用信息，否则我们不会测量状态")
            logger.info("      因为测量会导致量子态坍缩。")
        else:
            logger.error(f"隐形传态失败: {result.get('error', '未知错误')}")
    
    def run_entanglement_swapping_demo(self):
        """演示纠缠交换以连接远距离节点"""
        logger.info("\n===== 纠缠交换演示 =====")
        
        lab_id = self.demo_nodes["quantum_lab"]
        relay_id = self.demo_nodes["relay"]
        end_user_id = self.demo_nodes["end_user"]
        
        logger.info("尝试通过中继在量子实验室和终端用户之间建立纠缠...")
        
        result = self.network.run_protocol("entanglement_swapping", {
            "node_a": lab_id,
            "node_b": end_user_id,
            "node_c": relay_id
        })
        
        if result["success"]:
            logger.info("纠缠交换成功！")
            logger.info("量子实验室和终端用户现在共享纠缠量子比特")
            logger.info("这允许在没有直接量子通道的情况下进行量子隐形传态")
            
            # 演示使用纠缠
            logger.info("使用已建立的纠缠传送量子态...")
            time.sleep(1)
            
            # 创建新的传送状态
            lab_node = self.network.nodes[lab_id]
            qubit_idx = lab_node.create_qubit()
            lab_node.apply_gate(qubit_idx, "h")  # 应用Hadamard门创建叠加态
            
            # 使用纠缠进行隐形传态
            state_teleported = self.network.teleport_state(lab_id, end_user_id, qubit_idx)
            logger.info(f"通过纠缠交换的状态传送: {'成功' if state_teleported else '失败'}")
        else:
            logger.error(f"纠缠交换失败: {result.get('error', '未知错误')}")
    
    def run_full_demo(self):
        """运行完整的量子网络演示"""
        self.setup_demo_network()
        time.sleep(1)
        
        self.run_qkd_demo()
        time.sleep(2)
        
        self.run_teleportation_demo()
        time.sleep(2)
        
        self.run_entanglement_swapping_demo()
        
        logger.info("\n===== 量子网络演示完成 =====")
        logger.info("感谢您使用QEntL探索量子网络！")

def main():
    parser = argparse.ArgumentParser(description="QEntL量子网络演示")
    parser.add_argument("--demo", choices=["full", "qkd", "teleport", "entanglement"],
                        default="full", help="选择要运行的特定演示")
    
    args = parser.parse_args()
    
    demo = QuantumNetworkDemo()
    
    if args.demo == "full":
        demo.run_full_demo()
    else:
        demo.setup_demo_network()
        
        if args.demo == "qkd":
            demo.run_qkd_demo()
        elif args.demo == "teleport":
            demo.run_teleportation_demo()
        elif args.demo == "entanglement":
            demo.run_entanglement_swapping_demo()

if __name__ == "__main__":
    main() 

"""
"""
量子基因编码: QE-QUA-80BDE338DA15
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
