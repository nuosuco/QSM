"""
量子适配器模块 - 负责将Claude生成的知识向量转换为WeQ可训练的格式
实现Claude和WeQ神经网络之间的双向交互和知识转换
"""

import os
import numpy as np
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='quantum_adapter.log'
)
logger = logging.getLogger(__name__)

class QuantumKnowledgeAdapter:
    """
    量子知识适配器 - 将Claude知识向量转换为WeQ训练格式
    """
    
    def __init__(self, input_dim=64, qubit_dim=28):
        """
        初始化量子知识适配器
        
        Args:
            input_dim: 输入向量维度
            qubit_dim: 量子比特维度
        """
        self.input_dim = input_dim
        self.qubit_dim = qubit_dim
        self.batch_buffer = []
        self.metadata_buffer = []
        logger.info(f"量子知识适配器初始化完成, 输入维度: {input_dim}, 量子维度: {qubit_dim}")
    
    def vector_to_quantum_state(self, vector):
        """
        将知识向量转换为量子态表示
        
        Args:
            vector: 知识向量 (input_dim 维度)
            
        Returns:
            量子态表示 (qubit_dim 维度)
        """
        if vector.shape[0] != self.input_dim:
            raise ValueError(f"向量维度不匹配：预期 {self.input_dim}，实际 {vector.shape[0]}")
        
        # 1. 对向量进行降维（如果需要）或者填充（如果需要）
        if self.qubit_dim < self.input_dim:
            # 降维方法一：PCA-like，保留主要信息
            # 这里使用简化版，选择方差最大的维度
            variances = np.var(vector.reshape(-1, self.qubit_dim), axis=0)
            indices = np.argsort(variances)[-self.qubit_dim:]
            quantum_state_mag = vector[indices]
        else:
            # 填充额外维度
            quantum_state_mag = np.zeros(self.qubit_dim)
            quantum_state_mag[:self.input_dim] = vector
        
        # 2. 归一化
        magnitude = np.linalg.norm(quantum_state_mag)
        if magnitude > 0:
            quantum_state_mag = quantum_state_mag / magnitude
        
        # 3. 添加相位信息（创建复数量子态）
        phase = np.random.uniform(0, 2*np.pi, size=self.qubit_dim)
        quantum_state = quantum_state_mag * np.exp(1j * phase)
        
        return quantum_state
    
    def quantum_state_to_vector(self, quantum_state):
        """
        将量子态转换回知识向量
        
        Args:
            quantum_state: 量子态（复数向量）
            
        Returns:
            知识向量
        """
        # 提取振幅（绝对值）信息
        amplitudes = np.abs(quantum_state)
        
        # 如果量子维度小于输入维度，需要扩展
        if self.qubit_dim < self.input_dim:
            vector = np.zeros(self.input_dim)
            # 将振幅分散到输入维度
            step = self.input_dim // self.qubit_dim
            for i in range(self.qubit_dim):
                vector[i*step:(i+1)*step] = amplitudes[i] / step
        else:
            # 截取所需的维度
            vector = amplitudes[:self.input_dim]
            
        # 归一化
        magnitude = np.linalg.norm(vector)
        if magnitude > 0:
            vector = vector / magnitude
            
        return vector
    
    def add_to_batch(self, vector, metadata=None):
        """
        添加向量到批处理缓冲区
        
        Args:
            vector: 知识向量
            metadata: 相关元数据
        """
        self.batch_buffer.append(vector)
        self.metadata_buffer.append(metadata or {})
        logger.debug(f"添加向量到批处理缓冲区, 当前大小: {len(self.batch_buffer)}")
    
    def prepare_training_batch(self, clear_buffer=True):
        """
        准备训练批次
        
        Args:
            clear_buffer: 是否清空缓冲区
            
        Returns:
            训练数据和元数据
        """
        if not self.batch_buffer:
            logger.warning("批处理缓冲区为空，无法准备训练批次")
            return None, None
        
        # 准备训练数据
        X = np.array(self.batch_buffer)
        metadata = self.metadata_buffer.copy()
        
        # 清空缓冲区
        if clear_buffer:
            self.batch_buffer = []
            self.metadata_buffer = []
            
        logger.info(f"准备训练批次完成, 形状: {X.shape}")
        return X, metadata
    
    def create_training_samples(self, knowledge_cache, sample_size=None):
        """
        从知识缓存创建训练样本
        
        Args:
            knowledge_cache: 知识缓存文件路径或数据
            sample_size: 样本大小，None表示全部
            
        Returns:
            训练样本 X, y
        """
        # 加载知识缓存
        if isinstance(knowledge_cache, str):
            try:
                with open(knowledge_cache, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
            except Exception as e:
                logger.error(f"加载知识缓存失败: {str(e)}")
                return None, None
        else:
            cache_data = knowledge_cache
            
        # 提取向量数据
        vectors_data = cache_data.get("vectors", {})
        if not vectors_data:
            logger.warning("知识缓存中没有向量数据")
            return None, None
            
        # 准备训练数据
        X = []
        y = []  # 使用主题作为标签
        metadata = []
        
        # 收集所有主题
        all_topics = set()
        topic_to_id = {}
        
        for vec_data in vectors_data.values():
            topic = vec_data.get("metadata", {}).get("topic")
            if topic and topic not in all_topics:
                all_topics.add(topic)
                topic_to_id[topic] = len(topic_to_id)
        
        # 收集向量和对应的标签
        for vec_id, vec_data in vectors_data.items():
            vector = np.array(vec_data["vector"])
            topic = vec_data.get("metadata", {}).get("topic")
            
            if topic and topic in topic_to_id:
                X.append(vector)
                
                # 创建one-hot编码标签
                label = np.zeros(len(all_topics))
                label[topic_to_id[topic]] = 1
                y.append(label)
                
                metadata.append(vec_data.get("metadata", {}))
        
        # 转换为numpy数组
        X = np.array(X)
        y = np.array(y)
        
        # 随机采样
        if sample_size and sample_size < len(X):
            indices = np.random.choice(len(X), sample_size, replace=False)
            X = X[indices]
            y = y[indices]
            metadata = [metadata[i] for i in indices]
        
        logger.info(f"从知识缓存创建训练样本完成, X形状: {X.shape}, y形状: {y.shape}")
        return X, y, metadata
    
    def save_quantum_ready_data(self, X, y, metadata, output_dir="quantum_training_data"):
        """
        保存量子就绪数据
        
        Args:
            X: 输入向量
            y: 标签
            metadata: 元数据
            output_dir: 输出目录
            
        Returns:
            保存的文件路径
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"quantum_data_{timestamp}.npz")
        
        # 转换X为量子态表示
        quantum_states = []
        for vector in X:
            quantum_state = self.vector_to_quantum_state(vector)
            quantum_states.append(quantum_state)
        
        # 将复数数组转换为两个实数数组
        quantum_real = np.real(quantum_states)
        quantum_imag = np.imag(quantum_states)
        
        # 保存NumPy压缩格式
        np.savez_compressed(
            output_file,
            quantum_real=quantum_real,
            quantum_imag=quantum_imag,
            y=y,
            input_dim=self.input_dim,
            qubit_dim=self.qubit_dim
        )
        
        # 保存元数据
        metadata_file = output_file.replace(".npz", "_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": timestamp,
                "samples": len(X),
                "input_dim": self.input_dim,
                "qubit_dim": self.qubit_dim,
                "metadata": metadata
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"量子就绪数据已保存: {output_file}, 元数据: {metadata_file}")
        return output_file, metadata_file
    
    def load_quantum_ready_data(self, data_file):
        """
        加载量子就绪数据
        
        Args:
            data_file: 数据文件路径
            
        Returns:
            X, y, metadata
        """
        try:
            # 加载数据
            data = np.load(data_file)
            quantum_real = data["quantum_real"]
            quantum_imag = data["quantum_imag"]
            y = data["y"]
            
            # 重构复数量子态
            quantum_states = quantum_real + 1j * quantum_imag
            
            # 转换回向量表示
            X = []
            for quantum_state in quantum_states:
                vector = self.quantum_state_to_vector(quantum_state)
                X.append(vector)
            X = np.array(X)
            
            # 加载元数据
            metadata_file = data_file.replace(".npz", "_metadata.json")
            metadata = []
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata_data = json.load(f)
                    metadata = metadata_data.get("metadata", [])
            
            logger.info(f"已加载量子就绪数据: {data_file}, X形状: {X.shape}, y形状: {y.shape}")
            return X, y, metadata
            
        except Exception as e:
            logger.error(f"加载量子就绪数据失败: {str(e)}")
            return None, None, None

def prepare_knowledge_for_weq(knowledge_cache, output_dir="quantum_training_data",
                           input_dim=64, qubit_dim=28, sample_size=None):
    """
    准备知识数据供WeQ训练
    
    Args:
        knowledge_cache: 知识缓存文件路径
        output_dir: 输出目录
        input_dim: 输入维度
        qubit_dim: 量子比特维度
        sample_size: 采样大小
        
    Returns:
        量子训练数据文件路径
    """
    # 创建适配器
    adapter = QuantumKnowledgeAdapter(input_dim=input_dim, qubit_dim=qubit_dim)
    
    # 从缓存创建训练样本
    X, y, metadata = adapter.create_training_samples(knowledge_cache, sample_size)
    
    if X is None or y is None:
        logger.error("从知识缓存创建训练样本失败")
        return None
    
    # 保存量子就绪数据
    data_file, metadata_file = adapter.save_quantum_ready_data(X, y, metadata, output_dir)
    
    return data_file

if __name__ == "__main__":
    # 测试适配器
    adapter = QuantumKnowledgeAdapter(input_dim=64, qubit_dim=28)
    
    # 创建测试向量
    test_vector = np.random.rand(64)
    test_vector = test_vector / np.linalg.norm(test_vector)
    
    # 转换为量子态
    quantum_state = adapter.vector_to_quantum_state(test_vector)
    print(f"量子态形状: {quantum_state.shape}, 类型: {type(quantum_state[0])}")
    
    # 转换回向量
    recovered_vector = adapter.quantum_state_to_vector(quantum_state)
    print(f"恢复向量形状: {recovered_vector.shape}")
    
    # 计算恢复误差
    error = np.linalg.norm(test_vector - recovered_vector)
    print(f"恢复误差: {error:.6f}")
    
    # 测试批处理
    for i in range(5):
        vector = np.random.rand(64)
        vector = vector / np.linalg.norm(vector)
        adapter.add_to_batch(vector, {"index": i, "source": "test"})
    
    # 准备训练批次
    X, metadata = adapter.prepare_training_batch()
    print(f"训练批次形状: {X.shape}, 元数据数量: {len(metadata)}") 

"""
"""
量子基因编码: QE-QUA-5E6D98F067B5
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
