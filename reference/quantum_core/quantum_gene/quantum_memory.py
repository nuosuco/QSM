"""
量子语义记忆模块 (Quantum Semantic Memory)
为量子基因神经网络提供语义知识存储与检索能力
"""

import numpy as np
import cirq
import json
import os
import logging
import time
import hashlib
from typing import List, Dict, Tuple, Any, Optional, Union
from collections import defaultdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='quantum_memory.log'
)
logger = logging.getLogger(__name__)

class MemoryItem:
    """记忆项，表示存储在量子记忆中的单个项目"""
    
    def __init__(self, item_id: str, vector: np.ndarray, content: Any, metadata: Dict = None):
        self.item_id = item_id
        self.vector = vector  # 语义向量
        self.content = content  # 存储的内容
        self.metadata = metadata or {}
        self.creation_time = time.time()
        self.access_count = 0
        self.last_access_time = self.creation_time
        
    def access(self):
        """访问记忆项，更新访问计数和时间"""
        self.access_count += 1
        self.last_access_time = time.time()
        
    def get_age(self) -> float:
        """获取记忆项的年龄（秒）"""
        return time.time() - self.creation_time
        
    def get_recency(self) -> float:
        """获取记忆项的近期访问度（0-1）"""
        time_since_access = time.time() - self.last_access_time
        # 使用衰减函数计算近期度，1天作为参考时间
        decay_factor = 24 * 60 * 60  # 1天的秒数
        return np.exp(-time_since_access / decay_factor)
        
    def get_importance(self) -> float:
        """获取记忆项的重要性（基于访问频率和元数据）"""
        # 基础重要性来自访问频率
        base_importance = np.log(self.access_count + 1)
        
        # 从元数据中提取额外重要性
        extra_importance = self.metadata.get('importance', 0.0)
        
        return base_importance + extra_importance
        
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            'item_id': self.item_id,
            'vector': self.vector.tolist(),
            'content': self.content,
            'metadata': self.metadata,
            'creation_time': self.creation_time,
            'access_count': self.access_count,
            'last_access_time': self.last_access_time
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryItem':
        """从字典创建实例"""
        item = cls(
            item_id=data['item_id'],
            vector=np.array(data['vector']),
            content=data['content'],
            metadata=data.get('metadata', {})
        )
        item.creation_time = data.get('creation_time', time.time())
        item.access_count = data.get('access_count', 0)
        item.last_access_time = data.get('last_access_time', item.creation_time)
        return item

class QuantumMemoryRegion:
    """量子记忆区域，管理特定类型的记忆"""
    
    def __init__(self, region_id: str, capacity: int = 1000, qubit_count: int = 8):
        self.region_id = region_id
        self.capacity = capacity
        self.qubit_count = qubit_count
        self.items = {}  # 项目ID到记忆项的映射
        
        # 初始化量子比特
        self.qubits = [cirq.GridQubit(0, i) for i in range(qubit_count)]
        
        # 量子模拟器
        self.simulator = cirq.Simulator()
        
        logger.info(f"初始化量子记忆区域: ID={region_id}, 容量={capacity}, 量子比特数={qubit_count}")
        
    def store(self, vector: np.ndarray, content: Any, metadata: Dict = None) -> str:
        """
        存储新的记忆项
        
        参数:
            vector: 语义向量
            content: 要存储的内容
            metadata: 记忆项元数据
            
        返回:
            str: 新创建的记忆项ID
        """
        # 生成唯一ID
        item_id = self._generate_id(vector, content)
        
        # 检查是否已存在
        if item_id in self.items:
            logger.info(f"记忆项已存在: {item_id}")
            self.items[item_id].access()
            return item_id
            
        # 检查容量
        if len(self.items) >= self.capacity:
            self._evict_items()
            
        # 创建新记忆项
        memory_item = MemoryItem(
            item_id=item_id,
            vector=vector,
            content=content,
            metadata=metadata
        )
        
        # 存储记忆项
        self.items[item_id] = memory_item
        
        logger.info(f"存储记忆项: {item_id}")
        return item_id
        
    def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """
        通过ID检索记忆项
        
        参数:
            item_id: 记忆项ID
            
        返回:
            Optional[MemoryItem]: 检索到的记忆项或None
        """
        if item_id not in self.items:
            return None
            
        # 更新访问信息
        self.items[item_id].access()
        
        return self.items[item_id]
        
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        通过向量相似度搜索记忆项
        
        参数:
            query_vector: 查询向量
            top_k: 返回的最相似项目数量
            
        返回:
            List[Tuple[str, float]]: (项目ID, 相似度)的列表
        """
        if not self.items:
            return []
            
        # 计算量子相似度
        similarities = self._compute_quantum_similarities(query_vector)
        
        # 排序并返回结果
        sorted_items = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        
        # 更新访问信息
        for item_id, _ in sorted_items[:top_k]:
            self.items[item_id].access()
            
        return sorted_items[:top_k]
        
    def _compute_quantum_similarities(self, query_vector: np.ndarray) -> Dict[str, float]:
        """使用量子电路计算查询向量与所有记忆项的相似度"""
        similarities = {}
        
        # 为每个记忆项计算相似度
        for item_id, item in self.items.items():
            similarity = self._quantum_similarity(query_vector, item.vector)
            similarities[item_id] = similarity
            
        return similarities
        
    def _quantum_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        使用量子电路计算两个向量的相似度
        
        参数:
            vec1, vec2: 要比较的向量
            
        返回:
            float: 相似度 (0-1)
        """
        # 创建量子电路
        circuit = cirq.Circuit()
        
        # 1. 初始化第一个向量
        for i, value in enumerate(vec1[:self.qubit_count]):
            # 归一化到[-1, 1]
            norm_value = max(min(value, 1.0), -1.0)
            # 使用Ry旋转编码
            circuit.append(cirq.Ry(np.pi * norm_value)(self.qubits[i]))
            
        # 2. 应用Hadamard门
        for i in range(self.qubit_count):
            circuit.append(cirq.H(self.qubits[i]))
            
        # 3. 编码第二个向量
        for i, value in enumerate(vec2[:self.qubit_count]):
            # 归一化到[-1, 1]
            norm_value = max(min(value, 1.0), -1.0)
            # 使用Rz旋转编码
            circuit.append(cirq.Rz(np.pi * norm_value)(self.qubits[i]))
            
        # 4. 再次应用Hadamard门
        for i in range(self.qubit_count):
            circuit.append(cirq.H(self.qubits[i]))
            
        # 5. 测量
        for i in range(self.qubit_count):
            circuit.append(cirq.measure(self.qubits[i], key=f'q{i}'))
            
        # 运行电路多次
        repetitions = 100
        results = self.simulator.run(circuit, repetitions=repetitions)
        
        # 统计所有量子比特测量到0的比例
        zeros_count = 0
        total_bits = self.qubit_count * repetitions
        
        for i in range(self.qubit_count):
            zeros_count += np.sum(results.measurements[f'q{i}'] == 0)
            
        # 相似度为测量到0的比例（相似向量会导致更多的0）
        similarity = zeros_count / total_bits
        
        return similarity
        
    def _generate_id(self, vector: np.ndarray, content: Any) -> str:
        """为记忆项生成唯一ID"""
        # 组合向量和内容创建哈希
        hash_input = f"{vector.tobytes()}_{str(content)}_{time.time()}"
        return hashlib.md5(hash_input.encode()).hexdigest()
        
    def _evict_items(self):
        """
        当记忆区域达到容量上限时淘汰记忆项
        使用重要性、近期度和年龄的加权评分
        """
        if len(self.items) <= self.capacity * 0.9:  # 只有超过90%容量才清理
            return
            
        # 计算每个项目的评分
        scores = {}
        for item_id, item in self.items.items():
            importance = item.get_importance()
            recency = item.get_recency()
            age = item.get_age()
            
            # 评分公式: 重要性 + 近期度 - 标准化年龄
            # 高分的项目被保留，低分的被淘汰
            age_factor = age / (24 * 60 * 60)  # 转换为天数
            scores[item_id] = importance + recency - 0.1 * age_factor
            
        # 排序并保留顶部项目
        keep_count = int(self.capacity * 0.8)  # 保留80%的容量
        items_to_keep = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:keep_count]
        
        # 创建新的项目字典
        new_items = {}
        for item_id, _ in items_to_keep:
            new_items[item_id] = self.items[item_id]
            
        # 更新项目字典
        removed_count = len(self.items) - len(new_items)
        self.items = new_items
        
        logger.info(f"淘汰了{removed_count}个记忆项，当前记忆项数量: {len(self.items)}")
        
    def clear(self):
        """清空记忆区域"""
        self.items.clear()
        logger.info(f"清空记忆区域: {self.region_id}")
        
    def save_to_file(self, filepath: str):
        """将记忆区域保存到文件"""
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 将记忆项转换为字典
        items_dict = {item_id: item.to_dict() for item_id, item in self.items.items()}
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'region_id': self.region_id,
                'capacity': self.capacity,
                'qubit_count': self.qubit_count,
                'items': items_dict
            }, f, ensure_ascii=False, indent=2)
            
        logger.info(f"记忆区域保存到文件: {filepath}")
        
    @classmethod
    def load_from_file(cls, filepath: str) -> 'QuantumMemoryRegion':
        """从文件加载记忆区域"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 创建记忆区域
        region = cls(
            region_id=data['region_id'],
            capacity=data['capacity'],
            qubit_count=data['qubit_count']
        )
        
        # 加载记忆项
        for item_id, item_data in data['items'].items():
            region.items[item_id] = MemoryItem.from_dict(item_data)
            
        logger.info(f"从文件加载记忆区域: {filepath}, 记忆项数量: {len(region.items)}")
        
        return region

class QuantumSemanticMemory:
    """量子语义记忆，管理多个记忆区域"""
    
    def __init__(self, memory_size: int = 64, qubit_count: int = 16):
        self.memory_size = memory_size
        self.qubit_count = qubit_count
        self.regions = {}  # 区域ID到记忆区域的映射
        self.default_region = "general"
        
        # 创建默认记忆区域
        self.regions[self.default_region] = QuantumMemoryRegion(
            region_id=self.default_region,
            capacity=memory_size,
            qubit_count=qubit_count
        )
        
        # 全局查询量子比特
        self.query_qubits = [cirq.GridQubit(1, i) for i in range(qubit_count)]
        
        # 关联矩阵，用于记忆项之间的关联
        self.associations = defaultdict(dict)
        
        logger.info(f"初始化量子语义记忆: 记忆大小={memory_size}, 量子比特数={qubit_count}")
        
    def add_region(self, region_id: str, capacity: int = None, qubit_count: int = None) -> bool:
        """
        添加新的记忆区域
        
        参数:
            region_id: 区域ID
            capacity: 区域容量，默认使用全局设置
            qubit_count: 量子比特数，默认使用全局设置
            
        返回:
            bool: 是否成功添加
        """
        if region_id in self.regions:
            logger.warning(f"记忆区域已存在: {region_id}")
            return False
            
        # 使用默认值或指定值
        capacity = capacity or self.memory_size
        qubit_count = qubit_count or self.qubit_count
        
        # 创建新记忆区域
        self.regions[region_id] = QuantumMemoryRegion(
            region_id=region_id,
            capacity=capacity,
            qubit_count=qubit_count
        )
        
        logger.info(f"添加记忆区域: {region_id}, 容量={capacity}, 量子比特数={qubit_count}")
        return True
        
    def store(self, vector: np.ndarray, content: Any, region_id: str = None, metadata: Dict = None) -> str:
        """
        存储记忆项
        
        参数:
            vector: 语义向量
            content: 要存储的内容
            region_id: 记忆区域ID，默认使用默认区域
            metadata: 元数据
            
        返回:
            str: 记忆项ID
        """
        # 使用指定区域或默认区域
        region_id = region_id or self.default_region
        
        # 确保区域存在
        if region_id not in self.regions:
            self.add_region(region_id)
            
        # 存储记忆项
        return self.regions[region_id].store(vector, content, metadata)
        
    def retrieve(self, item_id: str, region_id: str = None) -> Optional[Any]:
        """
        检索记忆项
        
        参数:
            item_id: 记忆项ID
            region_id: 记忆区域ID，默认在所有区域中搜索
            
        返回:
            Optional[Any]: 检索到的内容或None
        """
        # 在指定区域搜索
        if region_id is not None:
            if region_id not in self.regions:
                return None
                
            memory_item = self.regions[region_id].retrieve(item_id)
            return memory_item.content if memory_item else None
            
        # 在所有区域搜索
        for region in self.regions.values():
            memory_item = region.retrieve(item_id)
            if memory_item:
                return memory_item.content
                
        return None
        
    def search(self, query_vector: np.ndarray, region_id: str = None, top_k: int = 5) -> List[Tuple[str, float, Any]]:
        """
        搜索记忆项
        
        参数:
            query_vector: 查询向量
            region_id: 记忆区域ID，默认在所有区域中搜索
            top_k: 返回的最相似项目数量
            
        返回:
            List[Tuple[str, float, Any]]: (项目ID, 相似度, 内容)的列表
        """
        results = []
        
        # 在指定区域搜索
        if region_id is not None:
            if region_id not in self.regions:
                return []
                
            region_results = self.regions[region_id].search(query_vector, top_k)
            for item_id, similarity in region_results:
                memory_item = self.regions[region_id].items[item_id]
                results.append((item_id, similarity, memory_item.content))
                
            return results
            
        # 在所有区域搜索
        all_results = []
        
        for region_id, region in self.regions.items():
            region_results = region.search(query_vector, top_k)
            for item_id, similarity in region_results:
                memory_item = region.items[item_id]
                all_results.append((region_id, item_id, similarity, memory_item.content))
                
        # 按相似度排序
        all_results.sort(key=lambda x: x[2], reverse=True)
        
        # 返回前top_k个结果
        return [(item_id, similarity, content) for _, item_id, similarity, content in all_results[:top_k]]
        
    def create_association(self, item_id1: str, item_id2: str, strength: float = 1.0) -> bool:
        """
        创建两个记忆项之间的关联
        
        参数:
            item_id1, item_id2: 要关联的记忆项ID
            strength: 关联强度 (0-1)
            
        返回:
            bool: 是否成功创建关联
        """
        # 查找记忆项
        item1 = self._find_item(item_id1)
        item2 = self._find_item(item_id2)
        
        if not item1 or not item2:
            return False
            
        # 创建双向关联
        self.associations[item_id1][item_id2] = strength
        self.associations[item_id2][item_id1] = strength
        
        logger.info(f"创建记忆项关联: {item_id1} <-> {item_id2}, 强度={strength}")
        return True
        
    def get_associated_items(self, item_id: str, min_strength: float = 0.5) -> List[Tuple[str, float, Any]]:
        """
        获取与指定记忆项关联的记忆项
        
        参数:
            item_id: 记忆项ID
            min_strength: 最小关联强度
            
        返回:
            List[Tuple[str, float, Any]]: (项目ID, 关联强度, 内容)的列表
        """
        if item_id not in self.associations:
            return []
            
        results = []
        
        # 获取关联项
        for associated_id, strength in self.associations[item_id].items():
            if strength >= min_strength:
                item = self._find_item(associated_id)
                if item:
                    results.append((associated_id, strength, item.content))
                    
        # 按关联强度排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
        
    def associative_recall(self, query_vector: np.ndarray, depth: int = 2, top_k: int = 5) -> List[Tuple[str, float, Any]]:
        """
        关联回忆，通过查询向量找到相似项，然后查找与这些项关联的项
        
        参数:
            query_vector: 查询向量
            depth: 关联深度
            top_k: 返回的最相似项目数量
            
        返回:
            List[Tuple[str, float, Any]]: (项目ID, 相似度, 内容)的列表
        """
        # 获取初始相似项
        initial_results = self.search(query_vector, region_id=None, top_k=3)
        
        if not initial_results:
            return []
            
        # 获取关联项
        associated_items = set()
        current_items = {item_id for item_id, _, _ in initial_results}
        
        # 遍历关联深度
        for _ in range(depth):
            next_items = set()
            
            for item_id in current_items:
                if item_id in self.associations:
                    # 添加关联项
                    for associated_id, strength in self.associations[item_id].items():
                        if strength >= 0.5 and associated_id not in associated_items and associated_id not in current_items:
                            next_items.add(associated_id)
                            
            # 更新集合
            associated_items.update(current_items)
            current_items = next_items
            
            if not current_items:
                break
                
        # 收集所有关联项的内容
        results = []
        
        for item_id in associated_items:
            item = self._find_item(item_id)
            if item:
                # 计算与查询向量的相似度
                for region in self.regions.values():
                    if item_id in region.items:
                        similarity = region._quantum_similarity(query_vector, item.vector)
                        results.append((item_id, similarity, item.content))
                        break
                        
        # 按相似度排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
        
    def _find_item(self, item_id: str) -> Optional[MemoryItem]:
        """在所有记忆区域中查找记忆项"""
        for region in self.regions.values():
            if item_id in region.items:
                return region.items[item_id]
                
        return None
        
    def save(self, directory: str = "quantum_memory"):
        """
        保存记忆系统
        
        参数:
            directory: 保存目录
        """
        # 确保目录存在
        os.makedirs(directory, exist_ok=True)
        
        # 保存各个记忆区域
        for region_id, region in self.regions.items():
            filepath = os.path.join(directory, f"{region_id}.json")
            region.save_to_file(filepath)
            
        # 保存关联矩阵
        associations_filepath = os.path.join(directory, "associations.json")
        with open(associations_filepath, 'w', encoding='utf-8') as f:
            json.dump(dict(self.associations), f, ensure_ascii=False, indent=2)
            
        logger.info(f"保存量子语义记忆到目录: {directory}")
        
    @classmethod
    def load(cls, directory: str = "quantum_memory") -> 'QuantumSemanticMemory':
        """
        加载记忆系统
        
        参数:
            directory: 加载目录
            
        返回:
            QuantumSemanticMemory: 加载的记忆系统
        """
        # 确保目录存在
        if not os.path.exists(directory):
            logger.warning(f"记忆目录不存在: {directory}")
            return cls()
            
        # 创建记忆系统
        memory = cls()
        
        # 加载记忆区域
        for filename in os.listdir(directory):
            if filename.endswith('.json') and filename != "associations.json":
                filepath = os.path.join(directory, filename)
                region_id = filename[:-5]  # 移除.json后缀
                
                try:
                    region = QuantumMemoryRegion.load_from_file(filepath)
                    memory.regions[region_id] = region
                except Exception as e:
                    logger.error(f"加载记忆区域失败: {filepath}, 错误: {str(e)}")
                    
        # 加载关联矩阵
        associations_filepath = os.path.join(directory, "associations.json")
        if os.path.exists(associations_filepath):
            try:
                with open(associations_filepath, 'r', encoding='utf-8') as f:
                    memory.associations = defaultdict(dict, json.load(f))
            except Exception as e:
                logger.error(f"加载关联矩阵失败: {associations_filepath}, 错误: {str(e)}")
                
        logger.info(f"从目录加载量子语义记忆: {directory}, 区域数量: {len(memory.regions)}")
        
        return memory

# 测试代码
if __name__ == "__main__":
    # 创建量子语义记忆
    memory = QuantumSemanticMemory(memory_size=10, qubit_count=4)
    
    # 添加记忆区域
    memory.add_region("concepts", capacity=5)
    memory.add_region("facts", capacity=5)
    
    # 存储一些记忆
    # 概念记忆
    concept_vectors = {
        "tree": np.array([0.5, 0.2, 0.1, -0.3]),
        "car": np.array([0.1, 0.8, 0.3, 0.2]),
        "house": np.array([-0.2, 0.4, 0.7, 0.1])
    }
    
    concept_ids = {}
    for concept, vector in concept_vectors.items():
        concept_ids[concept] = memory.store(
            vector=vector,
            content=f"Concept: {concept}",
            region_id="concepts",
            metadata={"type": "concept"}
        )
        
    # 事实记忆
    fact_vectors = {
        "trees are green": np.array([0.6, 0.3, 0.0, -0.4]),
        "cars have wheels": np.array([0.2, 0.7, 0.4, 0.1]),
        "houses have rooms": np.array([-0.1, 0.5, 0.6, 0.2])
    }
    
    fact_ids = {}
    for fact, vector in fact_vectors.items():
        fact_ids[fact] = memory.store(
            vector=vector,
            content=f"Fact: {fact}",
            region_id="facts",
            metadata={"type": "fact"}
        )
        
    # 创建关联
    memory.create_association(concept_ids["tree"], fact_ids["trees are green"], 0.9)
    memory.create_association(concept_ids["car"], fact_ids["cars have wheels"], 0.8)
    memory.create_association(concept_ids["house"], fact_ids["houses have rooms"], 0.7)
    
    # 测试检索
    print("\n直接检索:")
    tree_content = memory.retrieve(concept_ids["tree"])
    print(f"树的概念内容: {tree_content}")
    
    # 测试搜索
    print("\n向量搜索:")
    query_vector = np.array([0.5, 0.3, 0.1, -0.3])  # 类似"tree"的向量
    search_results = memory.search(query_vector, top_k=2)
    for item_id, similarity, content in search_results:
        print(f"ID: {item_id}, 相似度: {similarity:.4f}, 内容: {content}")
        
    # 测试关联检索
    print("\n关联检索:")
    associated_items = memory.get_associated_items(concept_ids["tree"])
    for item_id, strength, content in associated_items:
        print(f"ID: {item_id}, 关联强度: {strength:.4f}, 内容: {content}")
        
    # 测试关联回忆
    print("\n关联回忆:")
    recall_results = memory.associative_recall(query_vector, depth=2, top_k=3)
    for item_id, similarity, content in recall_results:
        print(f"ID: {item_id}, 相似度: {similarity:.4f}, 内容: {content}")
        
    # 保存记忆
    memory.save("test_memory")
    
    # 加载记忆
    loaded_memory = QuantumSemanticMemory.load("test_memory")
    print("\n加载后的记忆区域:")
    for region_id, region in loaded_memory.regions.items():
        print(f"区域: {region_id}, 记忆项数量: {len(region.items)}") 

"""
"""
量子基因编码: QE-QUA-A6E1FA26F5A3
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
