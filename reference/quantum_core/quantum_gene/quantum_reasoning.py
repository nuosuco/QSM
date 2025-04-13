"""
量子语义推理模块 (Quantum Semantic Reasoning)
为量子基因神经网络提供基于量子行走算法的推理能力
"""

import numpy as np
import cirq
import networkx as nx
import json
import os
import logging
import time
import hashlib
from typing import List, Dict, Tuple, Any, Optional, Union, Set
from collections import defaultdict, Counter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='quantum_reasoning.log'
)
logger = logging.getLogger(__name__)

class KnowledgeNode:
    """知识图谱节点，表示概念或实体"""
    
    def __init__(self, node_id: str, vector: np.ndarray, metadata: Dict = None):
        self.node_id = node_id
        self.vector = vector  # 语义向量
        self.metadata = metadata or {}
        self.creation_time = time.time()
        
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            'node_id': self.node_id,
            'vector': self.vector.tolist(),
            'metadata': self.metadata,
            'creation_time': self.creation_time
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'KnowledgeNode':
        """从字典创建实例"""
        node = cls(
            node_id=data['node_id'],
            vector=np.array(data['vector']),
            metadata=data.get('metadata', {})
        )
        node.creation_time = data.get('creation_time', time.time())
        return node

class KnowledgeRelation:
    """知识图谱关系，表示节点间的连接"""
    
    def __init__(self, relation_id: str, source_id: str, target_id: str, 
                relation_type: str, weight: float = 1.0, metadata: Dict = None):
        self.relation_id = relation_id
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.weight = weight
        self.metadata = metadata or {}
        self.creation_time = time.time()
        
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            'relation_id': self.relation_id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relation_type': self.relation_type,
            'weight': self.weight,
            'metadata': self.metadata,
            'creation_time': self.creation_time
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'KnowledgeRelation':
        """从字典创建实例"""
        relation = cls(
            relation_id=data['relation_id'],
            source_id=data['source_id'],
            target_id=data['target_id'],
            relation_type=data['relation_type'],
            weight=data.get('weight', 1.0),
            metadata=data.get('metadata', {})
        )
        relation.creation_time = data.get('creation_time', time.time())
        return relation

class QuantumKnowledgeGraph:
    """量子知识图谱，存储和管理知识节点和关系"""
    
    def __init__(self):
        self.nodes = {}  # 节点ID到节点的映射
        self.relations = {}  # 关系ID到关系的映射
        self.outgoing_relations = defaultdict(list)  # 节点ID到出边的映射
        self.incoming_relations = defaultdict(list)  # 节点ID到入边的映射
        
        # 创建NetworkX图用于算法
        self.graph = nx.DiGraph()
        
        # 量子比特分配
        self.node_to_qubit = {}  # 节点ID到量子比特的映射
        self.qubit_to_node = {}  # 量子比特到节点ID的映射
        
        logger.info("初始化量子知识图谱")
        
    def add_node(self, node_id: str, vector: np.ndarray, metadata: Dict = None) -> bool:
        """
        添加知识节点
        
        参数:
            node_id: 节点ID
            vector: 语义向量
            metadata: 节点元数据
            
        返回:
            bool: 是否成功添加
        """
        if node_id in self.nodes:
            logger.warning(f"节点已存在: {node_id}")
            return False
            
        # 创建节点
        node = KnowledgeNode(node_id, vector, metadata)
        self.nodes[node_id] = node
        
        # 更新NetworkX图
        self.graph.add_node(node_id, vector=vector, metadata=metadata)
        
        logger.info(f"添加知识节点: {node_id}")
        return True
        
    def add_relation(self, source_id: str, target_id: str, relation_type: str, 
                    weight: float = 1.0, metadata: Dict = None) -> Optional[str]:
        """
        添加知识关系
        
        参数:
            source_id: 源节点ID
            target_id: 目标节点ID
            relation_type: 关系类型
            weight: 关系权重
            metadata: 关系元数据
            
        返回:
            Optional[str]: 关系ID或None（失败时）
        """
        # 确保节点存在
        if source_id not in self.nodes or target_id not in self.nodes:
            logger.warning(f"节点不存在: {source_id} 或 {target_id}")
            return None
            
        # 生成关系ID
        relation_id = self._generate_relation_id(source_id, target_id, relation_type)
        
        # 检查关系是否已存在
        if relation_id in self.relations:
            logger.warning(f"关系已存在: {relation_id}")
            return relation_id
            
        # 创建关系
        relation = KnowledgeRelation(
            relation_id=relation_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
            metadata=metadata
        )
        
        # 存储关系
        self.relations[relation_id] = relation
        self.outgoing_relations[source_id].append(relation_id)
        self.incoming_relations[target_id].append(relation_id)
        
        # 更新NetworkX图
        self.graph.add_edge(source_id, target_id, 
                          relation_type=relation_type, 
                          weight=weight,
                          metadata=metadata)
        
        logger.info(f"添加知识关系: {source_id} --[{relation_type}]--> {target_id}")
        return relation_id
        
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """获取节点"""
        return self.nodes.get(node_id)
        
    def get_relation(self, relation_id: str) -> Optional[KnowledgeRelation]:
        """获取关系"""
        return self.relations.get(relation_id)
        
    def get_outgoing_relations(self, node_id: str) -> List[KnowledgeRelation]:
        """获取节点的出边关系"""
        relation_ids = self.outgoing_relations.get(node_id, [])
        return [self.relations[rel_id] for rel_id in relation_ids if rel_id in self.relations]
        
    def get_incoming_relations(self, node_id: str) -> List[KnowledgeRelation]:
        """获取节点的入边关系"""
        relation_ids = self.incoming_relations.get(node_id, [])
        return [self.relations[rel_id] for rel_id in relation_ids if rel_id in self.relations]
        
    def find_similar_nodes(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """查找与查询向量最相似的节点"""
        similarities = []
        
        for node_id, node in self.nodes.items():
            # 计算向量相似度（余弦相似度）
            similarity = self._vector_similarity(query_vector, node.vector)
            similarities.append((node_id, similarity))
            
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
        
    def find_path(self, source_id: str, target_id: str, max_length: int = 3) -> List[List[Tuple[str, str, str]]]:
        """
        查找从源节点到目标节点的路径
        
        参数:
            source_id: 源节点ID
            target_id: 目标节点ID
            max_length: 最大路径长度
            
        返回:
            List[List[Tuple[str, str, str]]]: 路径列表，每条路径是(源节点,关系类型,目标节点)的元组列表
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            return []
            
        # 使用NetworkX查找路径
        paths = []
        
        for path in nx.all_simple_paths(self.graph, source=source_id, target=target_id, cutoff=max_length):
            if len(path) <= 1:
                continue
                
            # 构建路径表示
            path_with_relations = []
            for i in range(len(path) - 1):
                source = path[i]
                target = path[i + 1]
                edge_data = self.graph.get_edge_data(source, target)
                relation_type = edge_data.get('relation_type', 'unknown')
                path_with_relations.append((source, relation_type, target))
                
            paths.append(path_with_relations)
            
        return paths
        
    def run_quantum_walk(self, start_nodes: List[str], steps: int = 3, 
                        relation_types: List[str] = None) -> List[Tuple[str, float]]:
        """
        执行量子行走算法，从起始节点开始探索图
        
        参数:
            start_nodes: 起始节点ID列表
            steps: 行走步数
            relation_types: 要考虑的关系类型列表，None表示所有类型
            
        返回:
            List[Tuple[str, float]]: (节点ID, 概率)的列表，按概率排序
        """
        # 验证起始节点
        valid_start_nodes = [node_id for node_id in start_nodes if node_id in self.nodes]
        if not valid_start_nodes:
            return []
            
        # 分配量子比特
        self._assign_qubits()
        
        if not self.node_to_qubit:
            return []
            
        # 创建量子电路
        circuit = self._create_walk_circuit(valid_start_nodes, steps, relation_types)
        
        # 执行量子模拟
        simulator = cirq.Simulator()
        result = simulator.simulate(circuit)
        
        # 分析结果
        node_probabilities = self._analyze_quantum_state(result.final_state)
        
        # 按概率排序
        node_probabilities.sort(key=lambda x: x[1], reverse=True)
        
        return node_probabilities
        
    def _assign_qubits(self):
        """为图中的节点分配量子比特"""
        self.node_to_qubit.clear()
        self.qubit_to_node.clear()
        
        # 为每个节点分配一个量子比特
        for i, node_id in enumerate(self.nodes.keys()):
            qubit = cirq.GridQubit(0, i)
            self.node_to_qubit[node_id] = qubit
            self.qubit_to_node[qubit] = node_id
            
    def _create_walk_circuit(self, start_nodes: List[str], steps: int, 
                           relation_types: List[str]) -> cirq.Circuit:
        """创建量子行走电路"""
        circuit = cirq.Circuit()
        
        # 初始化起始节点
        for node_id in start_nodes:
            if node_id in self.node_to_qubit:
                circuit.append(cirq.X(self.node_to_qubit[node_id]))
                
        # 应用Hadamard门创建叠加态
        for qubit in self.node_to_qubit.values():
            circuit.append(cirq.H(qubit))
            
        # 执行多步量子行走
        for step in range(steps):
            # 添加节点间的条件转移
            for relation_id, relation in self.relations.items():
                # 检查关系类型
                if relation_types and relation.relation_type not in relation_types:
                    continue
                    
                source_id = relation.source_id
                target_id = relation.target_id
                
                if source_id in self.node_to_qubit and target_id in self.node_to_qubit:
                    source_qubit = self.node_to_qubit[source_id]
                    target_qubit = self.node_to_qubit[target_id]
                    
                    # 应用CNOT门，条件传播
                    circuit.append(cirq.CNOT(source_qubit, target_qubit))
                    
                    # 根据关系权重应用旋转
                    angle = relation.weight * np.pi / 2  # 将权重映射到旋转角度
                    circuit.append(cirq.Rz(angle)(target_qubit))
            
            # 应用扩散算子（Hadamard+反射+Hadamard）
            for qubit in self.node_to_qubit.values():
                circuit.append(cirq.H(qubit))
                
            # 实现反射算子（近似）
            for qubit in self.node_to_qubit.values():
                circuit.append(cirq.Z(qubit))
                
            for qubit in self.node_to_qubit.values():
                circuit.append(cirq.H(qubit))
                
        return circuit
        
    def _analyze_quantum_state(self, state_vector: np.ndarray) -> List[Tuple[str, float]]:
        """分析量子态，提取节点概率"""
        node_probabilities = []
        
        # 计算每个节点的概率
        for node_id, qubit in self.node_to_qubit.items():
            # 找到与该节点对应的量子比特
            qubit_index = self._qubit_to_index(qubit)
            
            # 计算该节点被访问的概率
            probability = 0
            for i in range(len(state_vector)):
                # 检查第qubit_index位是否为1
                if (i >> qubit_index) & 1:
                    probability += abs(state_vector[i]) ** 2
                    
            node_probabilities.append((node_id, probability))
            
        return node_probabilities
        
    def _qubit_to_index(self, qubit: cirq.Qid) -> int:
        """将量子比特映射到索引"""
        qubits = list(self.node_to_qubit.values())
        return qubits.index(qubit)
        
    def _generate_relation_id(self, source_id: str, target_id: str, relation_type: str) -> str:
        """生成关系ID"""
        relation_str = f"{source_id}_{relation_type}_{target_id}"
        return hashlib.md5(relation_str.encode()).hexdigest()
        
    def _vector_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """计算向量相似度（余弦相似度）"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
        
    def save(self, filepath: str):
        """保存知识图谱到文件"""
        # 创建目录
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 转换为可序列化格式
        data = {
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            'relations': {rel_id: relation.to_dict() for rel_id, relation in self.relations.items()}
        }
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"保存知识图谱到文件: {filepath}")
        
    @classmethod
    def load(cls, filepath: str) -> 'QuantumKnowledgeGraph':
        """从文件加载知识图谱"""
        # 创建图谱
        graph = cls()
        
        # 加载数据
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 加载节点
        for node_id, node_data in data.get('nodes', {}).items():
            node = KnowledgeNode.from_dict(node_data)
            graph.nodes[node_id] = node
            graph.graph.add_node(node_id, 
                               vector=node.vector, 
                               metadata=node.metadata)
            
        # 加载关系
        for rel_id, rel_data in data.get('relations', {}).items():
            relation = KnowledgeRelation.from_dict(rel_data)
            graph.relations[rel_id] = relation
            
            # 更新关系映射
            graph.outgoing_relations[relation.source_id].append(rel_id)
            graph.incoming_relations[relation.target_id].append(rel_id)
            
            # 更新NetworkX图
            graph.graph.add_edge(relation.source_id, 
                               relation.target_id, 
                               relation_type=relation.relation_type, 
                               weight=relation.weight,
                               metadata=relation.metadata)
            
        logger.info(f"从文件加载知识图谱: {filepath}, 节点数量: {len(graph.nodes)}, 关系数量: {len(graph.relations)}")
        
        return graph

class QuantumReasoner:
    """量子推理器，使用量子行走算法进行推理"""
    
    def __init__(self, knowledge_graph: QuantumKnowledgeGraph):
        self.knowledge_graph = knowledge_graph
        self.simulator = cirq.Simulator()
        
        # 创建量子比特
        self.concept_qubits = []
        self.auxiliary_qubits = []
        
        logger.info("初始化量子推理器")
        
    def prepare_qubits(self, num_concepts: int = 0, num_auxiliary: int = 2):
        """准备量子比特"""
        # 为概念准备量子比特
        if num_concepts <= 0:
            num_concepts = len(self.knowledge_graph.nodes)
            
        self.concept_qubits = [cirq.GridQubit(0, i) for i in range(num_concepts)]
        
        # 准备辅助量子比特
        self.auxiliary_qubits = [cirq.GridQubit(1, i) for i in range(num_auxiliary)]
        
        logger.info(f"准备量子比特: 概念比特数={num_concepts}, 辅助比特数={num_auxiliary}")
        
    def encode_knowledge_graph(self) -> cirq.Circuit:
        """将知识图谱编码为量子电路"""
        # 创建量子电路
        circuit = cirq.Circuit()
        
        # 确保有足够的量子比特
        if len(self.concept_qubits) < len(self.knowledge_graph.nodes):
            self.prepare_qubits(len(self.knowledge_graph.nodes))
            
        # 创建节点到量子比特的映射
        node_to_qubit = {}
        for i, node_id in enumerate(self.knowledge_graph.nodes.keys()):
            if i < len(self.concept_qubits):
                node_to_qubit[node_id] = self.concept_qubits[i]
                
        # 编码节点（应用Hadamard门创建叠加态）
        for qubit in self.concept_qubits:
            circuit.append(cirq.H(qubit))
            
        # 编码边（使用CNOT门表示节点间的关系）
        for relation_id, relation in self.knowledge_graph.relations.items():
            source_id = relation.source_id
            target_id = relation.target_id
            
            if source_id in node_to_qubit and target_id in node_to_qubit:
                source_qubit = node_to_qubit[source_id]
                target_qubit = node_to_qubit[target_id]
                
                # 应用CNOT门
                circuit.append(cirq.CNOT(source_qubit, target_qubit))
                
                # 根据关系权重应用旋转
                angle = relation.weight * np.pi / 2
                circuit.append(cirq.Rz(angle)(target_qubit))
                
        return circuit
        
    def infer(self, query_concepts: List[str], steps: int = 3) -> List[Tuple[str, float]]:
        """
        执行推理，从起始概念出发探索相关概念
        
        参数:
            query_concepts: 起始概念列表
            steps: 推理步数
            
        返回:
            List[Tuple[str, float]]: (概念ID, 概率)的列表，按概率排序
        """
        # 确保概念存在
        valid_concepts = [concept for concept in query_concepts if concept in self.knowledge_graph.nodes]
        if not valid_concepts:
            return []
            
        # 准备量子比特
        self.prepare_qubits()
        
        # 使用知识图谱的量子行走功能
        return self.knowledge_graph.run_quantum_walk(valid_concepts, steps)
        
    def find_relations(self, concept1: str, concept2: str) -> List[Dict]:
        """
        查找两个概念之间的关系
        
        参数:
            concept1, concept2: 概念ID
            
        返回:
            List[Dict]: 关系描述字典列表
        """
        paths = self.knowledge_graph.find_path(concept1, concept2)
        
        if not paths:
            return []
            
        relations = []
        
        for path in paths:
            relation_desc = {
                'path': path,
                'length': len(path),
                'description': self._path_to_description(path)
            }
            relations.append(relation_desc)
            
        return relations
        
    def answer_query(self, query: str, context_concepts: List[str] = None) -> Dict:
        """
        回答查询，基于知识图谱和量子推理
        
        参数:
            query: 查询文本
            context_concepts: 上下文概念列表
            
        返回:
            Dict: 回答信息
        """
        # 查找与查询最相似的节点
        query_embedding = self._embed_text(query)
        similar_nodes = self.knowledge_graph.find_similar_nodes(query_embedding, top_k=3)
        
        # 获取起始概念
        start_concepts = [node_id for node_id, _ in similar_nodes]
        if context_concepts:
            # 添加上下文概念
            valid_context = [c for c in context_concepts if c in self.knowledge_graph.nodes]
            start_concepts.extend(valid_context)
            
        # 执行推理
        inferred_concepts = self.infer(start_concepts)
        
        # 提取答案
        answer = {
            'query': query,
            'similar_concepts': similar_nodes,
            'inferred_concepts': inferred_concepts[:5],
            'confidence': self._calculate_confidence(similar_nodes, inferred_concepts)
        }
        
        # 尝试提取关系路径
        if len(similar_nodes) >= 2:
            relation_paths = self.find_relations(similar_nodes[0][0], similar_nodes[1][0])
            if relation_paths:
                answer['relation_paths'] = relation_paths
                
        return answer
        
    def analogical_reasoning(self, a: str, b: str, c: str) -> List[Tuple[str, float]]:
        """
        类比推理: 如果a与b有关系，c与什么有同样关系？
        
        参数:
            a, b, c: 概念ID
            
        返回:
            List[Tuple[str, float]]: (概念ID, 相似度)的列表
        """
        if a not in self.knowledge_graph.nodes or b not in self.knowledge_graph.nodes or c not in self.knowledge_graph.nodes:
            return []
            
        # 获取a和b之间的关系
        ab_paths = self.knowledge_graph.find_path(a, b)
        if not ab_paths:
            return []
            
        # 提取关系类型
        relation_types = set()
        for path in ab_paths:
            for _, relation_type, _ in path:
                relation_types.add(relation_type)
                
        # 使用量子行走在相同关系类型的边上寻找c可能连接的节点
        return self.knowledge_graph.run_quantum_walk([c], steps=2, relation_types=list(relation_types))
        
    def _embed_text(self, text: str) -> np.ndarray:
        """
        为文本创建语义向量（简化版本）
        实际应用中应该使用预训练的语言模型
        """
        # 简化的字符哈希嵌入
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # 创建固定维度的向量
        vec_dim = len(list(self.knowledge_graph.nodes.values())[0].vector) if self.knowledge_graph.nodes else 8
        vector = np.zeros(vec_dim)
        
        for i in range(min(len(hash_bytes), vec_dim)):
            vector[i] = (hash_bytes[i] / 255.0) * 2 - 1
            
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
        
    def _path_to_description(self, path: List[Tuple[str, str, str]]) -> str:
        """将路径转换为可读描述"""
        if not path:
            return ""
            
        description = []
        for source, relation_type, target in path:
            description.append(f"{source} --[{relation_type}]--> {target}")
            
        return " | ".join(description)
        
    def _calculate_confidence(self, similar_nodes: List[Tuple[str, float]], 
                           inferred_concepts: List[Tuple[str, float]]) -> float:
        """计算推理结果的置信度"""
        # 基于相似节点的相似度和推理概率计算置信度
        if not similar_nodes or not inferred_concepts:
            return 0.0
            
        # 相似度平均值
        avg_similarity = sum(sim for _, sim in similar_nodes) / len(similar_nodes)
        
        # 推理概率平均值
        avg_probability = sum(prob for _, prob in inferred_concepts[:3]) / min(3, len(inferred_concepts))
        
        # 综合置信度
        return (avg_similarity + avg_probability) / 2
        
    def explain_reasoning(self, query_concepts: List[str], result_concepts: List[str]) -> List[Dict]:
        """
        解释推理过程
        
        参数:
            query_concepts: 查询概念列表
            result_concepts: 结果概念列表
            
        返回:
            List[Dict]: 推理路径解释列表
        """
        explanations = []
        
        for source in query_concepts:
            for target in result_concepts:
                paths = self.knowledge_graph.find_path(source, target)
                
                for path in paths:
                    explanation = {
                        'source': source,
                        'target': target,
                        'path': path,
                        'description': self._path_to_description(path)
                    }
                    explanations.append(explanation)
                    
        return explanations

# 测试代码
if __name__ == "__main__":
    # 创建量子知识图谱
    kg = QuantumKnowledgeGraph()
    
    # 添加一些节点
    node_vectors = {
        "animal": np.array([0.5, 0.3, 0.1, -0.2]),
        "dog": np.array([0.6, 0.2, 0.0, -0.3]),
        "cat": np.array([0.4, 0.4, 0.2, -0.1]),
        "mammal": np.array([0.7, 0.2, 0.0, -0.2]),
        "vertebrate": np.array([0.6, 0.3, -0.1, -0.2]),
        "pet": np.array([0.3, 0.6, 0.2, 0.1]),
        "human": np.array([0.2, 0.3, 0.7, 0.1]),
        "friendship": np.array([0.1, 0.5, 0.5, 0.3])
    }
    
    for node_id, vector in node_vectors.items():
        kg.add_node(node_id, vector)
        
    # 添加关系
    kg.add_relation("dog", "animal", "is_a", 1.0)
    kg.add_relation("cat", "animal", "is_a", 1.0)
    kg.add_relation("dog", "mammal", "is_a", 0.9)
    kg.add_relation("cat", "mammal", "is_a", 0.9)
    kg.add_relation("mammal", "vertebrate", "is_a", 0.8)
    kg.add_relation("dog", "pet", "can_be", 0.7)
    kg.add_relation("cat", "pet", "can_be", 0.7)
    kg.add_relation("human", "pet", "has", 0.6)
    kg.add_relation("human", "dog", "has_friendship_with", 0.8)
    kg.add_relation("dog", "human", "has_loyalty_to", 0.9)
    kg.add_relation("human", "friendship", "experiences", 0.7)
    kg.add_relation("dog", "friendship", "contributes_to", 0.6)
    
    # 创建量子推理器
    reasoner = QuantumReasoner(kg)
    
    # 执行推理
    print("\n基本推理:")
    inferred = reasoner.infer(["dog"])
    for concept, prob in inferred:
        print(f"{concept}: {prob:.4f}")
        
    # 查找关系
    print("\n关系查找:")
    relations = reasoner.find_relations("dog", "human")
    for relation in relations:
        print(f"路径: {relation['description']}")
        
    # 回答查询
    print("\n回答查询:")
    answer = reasoner.answer_query("What animals can be pets?")
    print(f"查询: {answer['query']}")
    print(f"相似概念: {answer['similar_concepts']}")
    print(f"推断概念: {answer['inferred_concepts']}")
    print(f"置信度: {answer['confidence']:.4f}")
    
    # 类比推理
    print("\n类比推理 (dog:animal :: cat:?):")
    analogies = reasoner.analogical_reasoning("dog", "animal", "cat")
    for concept, prob in analogies:
        print(f"{concept}: {prob:.4f}")
        
    # 解释推理
    print("\n推理解释:")
    explanations = reasoner.explain_reasoning(["dog"], ["human"])
    for explanation in explanations:
        print(f"从 {explanation['source']} 到 {explanation['target']}:")
        print(f"  {explanation['description']}")
        
    # 保存和加载
    kg.save("test_knowledge_graph.json")
    loaded_kg = QuantumKnowledgeGraph.load("test_knowledge_graph.json")
    print(f"\n加载的知识图谱: {len(loaded_kg.nodes)}节点, {len(loaded_kg.relations)}关系") 

"""
"""
量子基因编码: QE-QUA-2B1704A2510C
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
