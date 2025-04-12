"""
量子语义记忆模块 (Quantum Semantic Memory)
提供语义知识的存储和检索功能
"""

import numpy as np
import cirq
import json
import hashlib
import os
import time
from typing import List, Dict, Tuple, Any, Optional, Set
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='quantum_memory.log'
)
logger = logging.getLogger(__name__)

class MemoryItem:
    """存储在量子记忆中的记忆项"""
    
    def __init__(self, item_id: str, content: Dict[str, Any], vector: np.ndarray, 
                 metadata: Dict = None, timestamp: float = None):
        self.item_id = item_id
        self.content = content
        self.vector = vector
        self.metadata = metadata or {}
        self.timestamp = timestamp or time.time()
        self.access_count = 0
        self.last_access = self.timestamp
        self.importance = 1.0  # 初始重要性
        
    def access(self):
        """访问记忆项，更新访问统计"""
        self.access_count += 1
        self.last_access = time.time()
        
    def get_age(self) -> float:
        """获取记忆项年龄（秒）"""
        return time.time() - self.timestamp
        
    def get_recency(self) -> float:
        """获取最近访问时间（秒）"""
        return time.time() - self.last_access
        
    def calculate_importance(self) -> float:
        """计算记忆项的重要性
        
        基于访问频率、年龄和元数据中的显式重要性
        """
        # 归一化的访问频率因子
        frequency_factor = min(1.0, self.access_count / 10.0)
        
        # 随时间衰减的时间因子
        age_hours = self.get_age() / 3600.0
        time_factor = 1.0 / (1.0 + 0.1 * age_hours)
        
        # 从元数据获取显式重要性（如果存在）
        explicit_importance = self.metadata.get('importance', 1.0)
        
        # 组合因子
        self.importance = 0.3 * frequency_factor + 0.3 * time_factor + 0.4 * explicit_importance
        
        return self.importance
        
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            'item_id': self.item_id,
            'content': self.content,
            'vector': self.vector.tolist(),
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'access_count': self.access_count,
            'last_access': self.last_access,
            'importance': self.importance
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryItem':
        """从字典创建实例"""
        item = cls(
            item_id=data['item_id'],
            content=data['content'],
            vector=np.array(data['vector']),
            metadata=data.get('metadata', {}),
            timestamp=data.get('timestamp', time.time())
        )
        item.access_count = data.get('access_count', 0)
        item.last_access = data.get('last_access', item.timestamp)
        item.importance = data.get('importance', 1.0)
        return item

class QuantumMemoryRegion:
    """量子记忆区域，管理特定类型的记忆"""
    
    def __init__(self, region_id: str, vector_dim: int, capacity: int = 1000):
        self.region_id = region_id
        self.vector_dim = vector_dim
        self.capacity = capacity
        self.items = {}  # ID到记忆项的映射
        
        # 初始化量子比特
        self.item_qubits = [cirq.GridQubit(0, i) for i in range(vector_dim)]
        self.query_qubits = [cirq.GridQubit(1, i) for i in range(vector_dim)]
        self.similarity_qubit = cirq.GridQubit(2, 0)
        
        # 初始化模拟器
        self.simulator = cirq.Simulator()
        
    def store_item(self, content: Dict[str, Any], vector: np.ndarray, 
                  metadata: Dict = None) -> Optional[str]:
        """存储记忆项"""
        # 验证向量维度
        if len(vector) != self.vector_dim:
            logger.error(f"向量维度 {len(vector)} 与记忆区域维度 {self.vector_dim} 不匹配")
            return None
            
        # 生成唯一ID
        content_str = json.dumps(content, sort_keys=True)
        vector_str = str(vector.tolist())
        unique_str = content_str + vector_str
        item_id = hashlib.md5(unique_str.encode()).hexdigest()
        
        # 检查是否已存在相同项
        if item_id in self.items:
            # 更新现有项的访问
            self.items[item_id].access()
            logger.info(f"记忆项已存在，已更新访问: {item_id}")
            return item_id
            
        # 创建新的记忆项
        item = MemoryItem(item_id, content, vector, metadata)
        
        # 检查容量
        if len(self.items) >= self.capacity:
            # 移除最不重要的项
            self._evict_least_important()
            
        # 存储新项
        self.items[item_id] = item
        logger.info(f"已存储新记忆项: {item_id}")
        return item_id
        
    def _evict_least_important(self):
        """移除最不重要的记忆项"""
        # 计算所有项的重要性
        for item in self.items.values():
            item.calculate_importance()
            
        # 按重要性排序并移除最不重要的项
        items_by_importance = sorted(
            self.items.items(), 
            key=lambda x: x[1].importance
        )
        
        if items_by_importance:
            least_important_id = items_by_importance[0][0]
            del self.items[least_important_id]
            logger.info(f"由于容量限制，移除记忆项: {least_important_id}")
            
    def retrieve_item(self, item_id: str) -> Optional[MemoryItem]:
        """按ID检索记忆项"""
        item = self.items.get(item_id)
        
        if item:
            item.access()  # 更新访问统计
            
        return item
        
    def search_similar(self, query_vector: np.ndarray, 
                      top_k: int = 5, threshold: float = 0.6) -> List[Tuple[str, float]]:
        """搜索与查询向量相似的记忆项"""
        # 验证向量维度
        if len(query_vector) != self.vector_dim:
            logger.error(f"查询向量维度 {len(query_vector)} 与记忆区域维度 {self.vector_dim} 不匹配")
            return []
            
        similarities = []
        
        for item_id, item in self.items.items():
            # 计算相似度
            # 这里使用量子电路计算相似度，对于每个项单独计算
            similarity = self._quantum_similarity(query_vector, item.vector)
            
            if similarity >= threshold:
                similarities.append((item_id, similarity))
                
        # 对结果按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 访问返回的项
        for item_id, _ in similarities[:top_k]:
            self.items[item_id].access()
            
        return similarities[:top_k]
        
    def _quantum_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """使用量子电路计算两个向量的相似度"""
        # 构建量子电路
        circuit = cirq.Circuit()
        
        # 归一化向量
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)
        
        # 编码第一个向量到查询量子比特
        for i, val in enumerate(vec1_norm):
            if i < self.vector_dim:
                # 归一化到[-1, 1]范围
                norm_value = max(min(val, 1.0), -1.0)
                circuit.append(cirq.Ry(np.pi * norm_value)(self.query_qubits[i]))
                
        # 编码第二个向量到项量子比特
        for i, val in enumerate(vec2_norm):
            if i < self.vector_dim:
                norm_value = max(min(val, 1.0), -1.0)
                circuit.append(cirq.Ry(np.pi * norm_value)(self.item_qubits[i]))
                
        # 将相似度量子比特初始化为|0⟩
        circuit.append(cirq.X(self.similarity_qubit))
        circuit.append(cirq.H(self.similarity_qubit))
        
        # 应用受控旋转门，基于两个向量之间的相似度
        for i in range(self.vector_dim):
            # 使用受控操作将向量相似度编码到相似度比特
            circuit.append(cirq.CNOT(self.query_qubits[i], self.item_qubits[i]))
            circuit.append(
                cirq.ControlledGate(cirq.Ry(np.pi/self.vector_dim))(
                    self.item_qubits[i], self.similarity_qubit
                )
            )
            
        # 测量相似度比特
        circuit.append(cirq.measure(self.similarity_qubit, key='similarity'))
        
        # 执行多次测量
        repetitions = 1000
        results = self.simulator.run(circuit, repetitions=repetitions)
        
        # 从测量结果中提取相似度
        # 计算测量到1的概率作为相似度指标
        similarity_count = sum(results.measurements['similarity'][:, 0])
        similarity = similarity_count / repetitions
        
        # 因为量子计算的概率性，我们可能需要进一步映射这个值
        # 这里简单映射到[0, 1]范围
        
        return similarity
        
    def associate_items(self, item_id1: str, item_id2: str, strength: float = 1.0) -> bool:
        """在两个记忆项之间创建关联"""
        if item_id1 not in self.items or item_id2 not in self.items:
            logger.warning(f"记忆项不存在: {item_id1} 或 {item_id2}")
            return False
            
        # 在元数据中记录关联
        item1 = self.items[item_id1]
        item2 = self.items[item_id2]
        
        # 获取或初始化关联列表
        associations1 = item1.metadata.get('associations', {})
        associations2 = item2.metadata.get('associations', {})
        
        # 添加或更新关联
        associations1[item_id2] = strength
        associations2[item_id1] = strength
        
        # 更新元数据
        item1.metadata['associations'] = associations1
        item2.metadata['associations'] = associations2
        
        return True
        
    def get_associated_items(self, item_id: str, min_strength: float = 0.5) -> List[Tuple[str, float]]:
        """获取与指定项关联的记忆项"""
        if item_id not in self.items:
            logger.warning(f"记忆项不存在: {item_id}")
            return []
            
        item = self.items[item_id]
        associations = item.metadata.get('associations', {})
        
        # 过滤并排序关联
        associated_items = [
            (assoc_id, strength) 
            for assoc_id, strength in associations.items() 
            if strength >= min_strength and assoc_id in self.items
        ]
        
        # 按关联强度排序
        associated_items.sort(key=lambda x: x[1], reverse=True)
        
        return associated_items
        
    def save_to_file(self, file_path: str = None):
        """保存记忆区域到文件"""
        if file_path is None:
            file_path = f"memory_region_{self.region_id}.json"
            
        data = {
            'region_id': self.region_id,
            'vector_dim': self.vector_dim,
            'capacity': self.capacity,
            'items': {item_id: item.to_dict() for item_id, item in self.items.items()}
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"已保存记忆区域到文件: {file_path}")
        
    @classmethod
    def load_from_file(cls, file_path: str) -> 'QuantumMemoryRegion':
        """从文件加载记忆区域"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        region = cls(
            region_id=data['region_id'],
            vector_dim=data['vector_dim'],
            capacity=data['capacity']
        )
        
        # 加载记忆项
        for item_id, item_data in data.get('items', {}).items():
            region.items[item_id] = MemoryItem.from_dict(item_data)
            
        logger.info(f"已从文件加载记忆区域: {file_path}")
        return region

class QuantumSemanticMemory:
    """量子语义记忆，管理多个记忆区域"""
    
    def __init__(self, base_path: str = "quantum_memory"):
        self.regions = {}  # 区域ID到区域对象的映射
        self.base_path = base_path
        
        # 确保存储目录存在
        os.makedirs(base_path, exist_ok=True)
        
    def add_region(self, region_id: str, vector_dim: int, capacity: int = 1000) -> QuantumMemoryRegion:
        """添加记忆区域"""
        if region_id in self.regions:
            logger.warning(f"记忆区域已存在: {region_id}")
            return self.regions[region_id]
            
        region = QuantumMemoryRegion(region_id, vector_dim, capacity)
        self.regions[region_id] = region
        
        return region
        
    def get_region(self, region_id: str) -> Optional[QuantumMemoryRegion]:
        """获取记忆区域"""
        return self.regions.get(region_id)
        
    def store_item(self, region_id: str, content: Dict[str, Any], 
                  vector: np.ndarray, metadata: Dict = None) -> Optional[str]:
        """在指定区域存储记忆项"""
        region = self.get_region(region_id)
        
        if not region:
            logger.warning(f"记忆区域不存在: {region_id}")
            return None
            
        return region.store_item(content, vector, metadata)
        
    def retrieve_item(self, region_id: str, item_id: str) -> Optional[MemoryItem]:
        """从指定区域检索记忆项"""
        region = self.get_region(region_id)
        
        if not region:
            logger.warning(f"记忆区域不存在: {region_id}")
            return None
            
        return region.retrieve_item(item_id)
        
    def search_similar(self, region_id: str, query_vector: np.ndarray, 
                      top_k: int = 5, threshold: float = 0.6) -> List[Tuple[str, float]]:
        """在指定区域搜索相似记忆项"""
        region = self.get_region(region_id)
        
        if not region:
            logger.warning(f"记忆区域不存在: {region_id}")
            return []
            
        return region.search_similar(query_vector, top_k, threshold)
        
    def associate_items(self, region_id: str, item_id1: str, item_id2: str, 
                       strength: float = 1.0) -> bool:
        """在指定区域中关联两个记忆项"""
        region = self.get_region(region_id)
        
        if not region:
            logger.warning(f"记忆区域不存在: {region_id}")
            return False
            
        return region.associate_items(item_id1, item_id2, strength)
        
    def associative_recall(self, region_id: str, item_ids: List[str], 
                         threshold: float = 0.5) -> List[Tuple[str, float]]:
        """关联性回忆，基于多个线索查找相关记忆"""
        region = self.get_region(region_id)
        
        if not region:
            logger.warning(f"记忆区域不存在: {region_id}")
            return []
            
        # 收集所有关联项
        all_associations = {}
        
        for item_id in item_ids:
            associations = region.get_associated_items(item_id)
            
            for assoc_id, strength in associations:
                if assoc_id in all_associations:
                    all_associations[assoc_id] += strength
                else:
                    all_associations[assoc_id] = strength
                    
        # 归一化并过滤
        if all_associations:
            max_strength = max(all_associations.values())
            
            normalized_associations = [
                (assoc_id, strength / max_strength)
                for assoc_id, strength in all_associations.items()
                if strength / max_strength >= threshold
            ]
            
            # 按强度排序
            normalized_associations.sort(key=lambda x: x[1], reverse=True)
            return normalized_associations
            
        return []
        
    def save_all_regions(self):
        """保存所有记忆区域"""
        for region_id, region in self.regions.items():
            file_path = os.path.join(self.base_path, f"{region_id}.json")
            region.save_to_file(file_path)
            
    def load_region(self, region_id: str) -> bool:
        """加载指定记忆区域"""
        file_path = os.path.join(self.base_path, f"{region_id}.json")
        
        if not os.path.exists(file_path):
            logger.warning(f"记忆区域文件不存在: {file_path}")
            return False
            
        try:
            region = QuantumMemoryRegion.load_from_file(file_path)
            self.regions[region_id] = region
            return True
        except Exception as e:
            logger.error(f"加载记忆区域失败: {str(e)}")
            return False
            
    def list_available_regions(self) -> List[str]:
        """列出可用的记忆区域"""
        available_regions = []
        
        for filename in os.listdir(self.base_path):
            if filename.endswith('.json'):
                region_id = filename[:-5]  # 移除.json后缀
                available_regions.append(region_id)
                
        return available_regions 

"""
"""
量子基因编码: QE-MEM-61EE99169B9C
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
