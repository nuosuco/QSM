"""
量子语义推理模块 (Quantum Semantic Reasoning)
基于量子行走算法的知识图谱推理能力
"""

import numpy as np
import cirq
import json
import networkx as nx
import os
from typing import List, Dict, Tuple, Any, Optional, Set
import logging
import random
import pickle
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='quantum_reasoning.log'
)
logger = logging.getLogger(__name__)

class KnowledgeNode:
    """知识图谱节点"""
    
    def __init__(self, node_id: str, vector: np.ndarray, attributes: Dict = None):
        self.node_id = node_id
        self.vector = vector  # 节点的向量表示
        self.attributes = attributes or {}
        
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            'node_id': self.node_id,
            'vector': self.vector.tolist(),
            'attributes': self.attributes
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'KnowledgeNode':
        """从字典创建实例"""
        return cls(
            node_id=data['node_id'],
            vector=np.array(data['vector']),
            attributes=data.get('attributes', {})
        )

class KnowledgeRelation:
    """知识图谱关系"""
    
    def __init__(self, relation_id: str, source_id: str, target_id: str, 
                 relation_type: str, weight: float = 1.0, attributes: Dict = None):
        self.relation_id = relation_id
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.weight = weight
        self.attributes = attributes or {}
        
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            'relation_id': self.relation_id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relation_type': self.relation_type,
            'weight': self.weight,
            'attributes': self.attributes
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'KnowledgeRelation':
        """从字典创建实例"""
        return cls(
            relation_id=data['relation_id'],
            source_id=data['source_id'],
            target_id=data['target_id'],
            relation_type=data['relation_type'],
            weight=data.get('weight', 1.0),
            attributes=data.get('attributes', {})
        )

class QuantumKnowledgeGraph:
    """量子知识图谱，支持量子行走推理"""
    
    def __init__(self, graph_id: str = "default"):
        self.graph_id = graph_id
        self.nodes = {}  # node_id -> KnowledgeNode
        self.relations = {}  # relation_id -> KnowledgeRelation
        self.node_relations = {}  # node_id -> set(relation_ids)
        
        # 初始化NetworkX图用于路径查找和可视化
        self.graph = nx.DiGraph()
        
        # 量子比特映射
        self.node_to_qubit = {}  # node_id -> qubit
        
        # 初始化模拟器
        self.simulator = cirq.Simulator()
        
    def add_node(self, node: KnowledgeNode) -> bool:
        """添加节点到图谱"""
        # 检查节点是否已存在
        if node.node_id in self.nodes:
            logger.warning(f"节点已存在: {node.node_id}")
            return False
            
        # 存储节点
        self.nodes[node.node_id] = node
        self.node_relations[node.node_id] = set()
        
        # 添加到NetworkX图
        self.graph.add_node(node.node_id, **node.attributes)
        
        logger.info(f"已添加节点: {node.node_id}")
        return True
        
    def add_relation(self, relation: KnowledgeRelation) -> bool:
        """添加关系到图谱"""
        # 检查源节点和目标节点是否存在
        if relation.source_id not in self.nodes or relation.target_id not in self.nodes:
            logger.warning(f"源节点或目标节点不存在: {relation.source_id} -> {relation.target_id}")
            return False
            
        # 检查关系是否已存在
        if relation.relation_id in self.relations:
            logger.warning(f"关系已存在: {relation.relation_id}")
            return False
            
        # 存储关系
        self.relations[relation.relation_id] = relation
        
        # 更新节点关系映射
        self.node_relations[relation.source_id].add(relation.relation_id)
        
        # 添加到NetworkX图
        self.graph.add_edge(
            relation.source_id, 
            relation.target_id, 
            relation_id=relation.relation_id,
            relation_type=relation.relation_type,
            weight=relation.weight,
            **relation.attributes
        )
        
        logger.info(f"已添加关系: {relation.relation_id} ({relation.source_id} -> {relation.target_id})")
        return True
        
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """获取节点"""
        return self.nodes.get(node_id)
        
    def get_relation(self, relation_id: str) -> Optional[KnowledgeRelation]:
        """获取关系"""
        return self.relations.get(relation_id)
        
    def get_node_relations(self, node_id: str) -> List[KnowledgeRelation]:
        """获取节点的出边关系"""
        if node_id not in self.node_relations:
            return []
            
        return [self.relations[r_id] for r_id in self.node_relations[node_id]]
        
    def find_similar_nodes(self, vector: np.ndarray, top_k: int = 5, 
                          threshold: float = 0.6) -> List[Tuple[str, float]]:
        """查找与向量相似的节点"""
        similarities = []
        
        for node_id, node in self.nodes.items():
            # 计算余弦相似度
            dot_product = np.dot(node.vector, vector)
            norm_a = np.linalg.norm(node.vector)
            norm_b = np.linalg.norm(vector)
            
            if norm_a == 0 or norm_b == 0:
                similarity = 0.0
            else:
                similarity = dot_product / (norm_a * norm_b)
                
            if similarity >= threshold:
                similarities.append((node_id, similarity))
                
        # 排序并返回top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
        
    def prepare_quantum_walk(self):
        """准备量子行走所需的量子比特映射"""
        # 为每个节点分配一个量子比特
        self.node_to_qubit = {
            node_id: cirq.GridQubit(0, i) 
            for i, node_id in enumerate(self.nodes.keys())
        }
        
    def run_quantum_walk(self, start_node_id: str, steps: int = 3) -> Dict[str, float]:
        """执行量子随机行走推理
        
        Args:
            start_node_id: 起始节点ID
            steps: 量子行走步数
            
        Returns:
            节点ID到概率的映射，表示推理结果
        """
        if start_node_id not in self.nodes:
            logger.error(f"起始节点不存在: {start_node_id}")
            return {}
            
        # 准备量子行走
        self.prepare_quantum_walk()
        
        # 创建量子电路
        circuit = cirq.Circuit()
        
        # 量子行走的辅助比特
        coin_qubit = cirq.GridQubit(1, 0)
        
        # 初始化：将起始节点对应的量子比特置为|1⟩
        circuit.append(cirq.X(self.node_to_qubit[start_node_id]))
        
        # 初始化硬币比特为叠加态
        circuit.append(cirq.H(coin_qubit))
        
        # 执行量子行走步骤
        for _ in range(steps):
            # 对每个节点，基于其出边执行条件转移
            for source_id, relations_ids in self.node_relations.items():
                if not relations_ids:
                    continue  # 跳过没有出边的节点
                    
                source_qubit = self.node_to_qubit[source_id]
                
                # 获取节点的所有出边关系
                out_relations = [self.relations[r_id] for r_id in relations_ids]
                
                # 基于硬币比特，条件地转移到相邻节点
                for relation in out_relations:
                    target_id = relation.target_id
                    target_qubit = self.node_to_qubit[target_id]
                    
                    # 根据关系权重调整转移概率
                    weight = relation.weight
                    theta = np.arcsin(np.sqrt(weight))  # 将权重映射到旋转角度
                    
                    # 条件旋转：如果硬币是|0⟩，源比特是|1⟩，则应用到目标
                    # 这里使用两个控制比特的门
                    controls = [source_qubit, coin_qubit]
                    target = target_qubit
                    
                    # 应用条件转移
                    # 注意：cirq不直接支持多控制门，这里是简化写法
                    # 实际实现中需要分解成基本门
                    circuit.append(
                        cirq.ControlledGate(cirq.ry(2 * theta))(source_qubit, target_qubit)
                    )
                    
            # 重新初始化硬币比特
            circuit.append(cirq.H(coin_qubit))
            
        # 测量所有节点比特
        for node_id, qubit in self.node_to_qubit.items():
            circuit.append(cirq.measure(qubit, key=node_id))
            
        # 执行量子电路
        repetitions = 1000
        results = self.simulator.run(circuit, repetitions=repetitions)
        
        # 分析结果：计算每个节点的概率
        node_probabilities = {}
        
        for node_id in self.nodes:
            # 计算节点比特为1的概率
            if node_id in results.measurements:
                count_ones = sum(results.measurements[node_id][:, 0])
                probability = count_ones / repetitions
                node_probabilities[node_id] = probability
            else:
                node_probabilities[node_id] = 0.0
                
        return node_probabilities
        
    def find_path(self, source_id: str, target_id: str, 
                 max_depth: int = 3) -> List[List[Tuple[str, str, str]]]:
        """查找从源节点到目标节点的路径
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            max_depth: 最大搜索深度
            
        Returns:
            路径列表，每个路径是(node_id, relation_type, node_id)三元组的序列
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            logger.error(f"源节点或目标节点不存在: {source_id} -> {target_id}")
            return []
            
        # 使用NetworkX查找所有简单路径
        try:
            simple_paths = list(nx.all_simple_paths(
                self.graph, source_id, target_id, cutoff=max_depth
            ))
        except (nx.NetworkXError, nx.NodeNotFound) as e:
            logger.error(f"路径查找失败: {str(e)}")
            return []
            
        # 转换为详细路径表示
        detailed_paths = []
        
        for path in simple_paths:
            detailed_path = []
            
            for i in range(len(path) - 1):
                source = path[i]
                target = path[i + 1]
                
                # 获取边属性
                edge_data = self.graph.get_edge_data(source, target)
                
                if edge_data:
                    relation_type = edge_data.get('relation_type', 'unknown')
                    detailed_path.append((source, relation_type, target))
                    
            if detailed_path:
                detailed_paths.append(detailed_path)
                
        return detailed_paths
        
    def run_inference(self, question_vector: np.ndarray, 
                     max_steps: int = 3, top_k: int = 5) -> List[Tuple[str, float]]:
        """运行推理以回答问题
        
        Args:
            question_vector: 问题的向量表示
            max_steps: 最大量子行走步数
            top_k: 返回的顶部答案数量
            
        Returns:
            可能答案的节点ID和概率
        """
        # 1. 找到与问题向量最相似的起始节点
        similar_nodes = self.find_similar_nodes(question_vector, top_k=1, threshold=0.5)
        
        if not similar_nodes:
            logger.warning("找不到与问题相似的节点")
            return []
            
        start_node_id = similar_nodes[0][0]
        
        # 2. 从起始节点执行量子行走
        node_probabilities = self.run_quantum_walk(start_node_id, steps=max_steps)
        
        # 3. 按概率排序并返回顶部结果
        results = [(node_id, prob) for node_id, prob in node_probabilities.items() 
                  if prob > 0 and node_id != start_node_id]
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
        
    def save_to_file(self, file_path: str = None):
        """保存知识图谱到文件"""
        if file_path is None:
            file_path = f"knowledge_graph_{self.graph_id}.json"
            
        data = {
            'graph_id': self.graph_id,
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            'relations': {relation_id: relation.to_dict() for relation_id, relation in self.relations.items()}
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"已保存知识图谱到文件: {file_path}")
        
        # 同时保存NetworkX图结构，用于可视化
        nx_file_path = file_path.replace('.json', '_nx.pkl')
        with open(nx_file_path, 'wb') as f:
            pickle.dump(self.graph, f)
            
        logger.info(f"已保存NetworkX图结构到文件: {nx_file_path}")
        
    @classmethod
    def load_from_file(cls, file_path: str) -> 'QuantumKnowledgeGraph':
        """从文件加载知识图谱"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        graph = cls(graph_id=data.get('graph_id', 'default'))
        
        # 加载节点
        for node_id, node_data in data.get('nodes', {}).items():
            node = KnowledgeNode.from_dict(node_data)
            graph.add_node(node)
            
        # 加载关系
        for relation_id, relation_data in data.get('relations', {}).items():
            relation = KnowledgeRelation.from_dict(relation_data)
            graph.add_relation(relation)
            
        logger.info(f"已从文件加载知识图谱: {file_path}")
        
        # 尝试加载NetworkX图结构
        nx_file_path = file_path.replace('.json', '_nx.pkl')
        if os.path.exists(nx_file_path):
            with open(nx_file_path, 'rb') as f:
                graph.graph = pickle.load(f)
                
            logger.info(f"已从文件加载NetworkX图结构: {nx_file_path}")
            
        return graph
        
    def visualize(self, output_file: str = None, format: str = 'png'):
        """可视化知识图谱
        
        需要安装额外的依赖：
        pip install matplotlib pydot
        """
        try:
            import matplotlib.pyplot as plt
            import networkx.drawing.nx_pydot as nx_pydot
            
            if output_file is None:
                output_file = f"knowledge_graph_{self.graph_id}.{format}"
                
            # 为节点和边设置标签和颜色
            node_labels = {node_id: node.attributes.get('label', node_id) for node_id, node in self.nodes.items()}
            edge_labels = {(relation.source_id, relation.target_id): relation.relation_type 
                          for relation_id, relation in self.relations.items()}
            
            # 使用pydot绘制图形
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(self.graph)
            
            nx.draw(self.graph, pos, with_labels=True, labels=node_labels, 
                   node_color='lightblue', node_size=1500, font_size=10)
            nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=8)
            
            plt.savefig(output_file, format=format, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"已保存图谱可视化到文件: {output_file}")
            return True
        except ImportError as e:
            logger.error(f"可视化失败，缺少依赖: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"可视化失败: {str(e)}")
            return False 

"""
"""
量子基因编码: QE-REA-49E5F2058151
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
