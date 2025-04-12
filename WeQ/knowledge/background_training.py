#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WeQ(小趣)后台持续训练系统
实现Claude知识教学和爬虫数据训练的后台自动化
支持24小时不间断运行
"""

import os
import sys
import time
import json
import random
import threading
import logging
import numpy as np
import schedule
import requests
from datetime import datetime, timedelta
from pathlib import Path

# 确保日志目录存在
os.makedirs('logs', exist_ok=True)
os.makedirs('models/checkpoints', exist_ok=True)
os.makedirs('training_data', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('background_training.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("WeQ-后台训练")

# 添加项目根目录到路径
sys.path.append('.')

# 添加量子区块链学习引用
try:
    from WeQ.knowledge.training_data.quantum_blockchain_learning import get_blockchain_knowledge
    _has_blockchain_knowledge = True
    logger.info("成功导入量子区块链学习模块")
except ImportError as e:
    _has_blockchain_knowledge = False
    logger.warning(f"无法导入量子区块链学习模块: {str(e)}")

# 尝试导入量子叠加态模型知识库
try:
    from quantum_core.quantum_blockchain.QSM_knowledge import get_QSM_knowledge
    _has_qsm_knowledge = True
    logger.info("成功导入量子叠加态模型知识库")
except ImportError as e:
    _has_qsm_knowledge = False
    logger.warning(f"无法导入量子叠加态模型知识库: {str(e)}")

# SimpleQuantumNetwork类和必要函数的内部实现
class SimpleQuantumNetwork:
    """简化版28量子比特神经网络模拟"""
    
    def __init__(self, input_dim=64, hidden_dim=32, output_dim=5, qubit_count=28):
        """初始化简化版量子网络"""
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.qubit_count = qubit_count
        self.weights = np.random.randn(input_dim, hidden_dim) * 0.1
        self.output_weights = np.random.randn(hidden_dim, output_dim) * 0.1
        
        logging.getLogger("WeQ-后台训练").info(f"初始化简化版量子网络: {qubit_count}比特, 输入维度: {input_dim}")
    
    def quantum_simulate(self, input_vector):
        """模拟量子处理"""
        # 添加量子噪声
        quantum_noise = np.random.normal(0, 0.01, input_vector.shape)
        quantum_vector = input_vector + quantum_noise
        # 确保归一化
        return quantum_vector / np.linalg.norm(quantum_vector) if np.linalg.norm(quantum_vector) > 0 else quantum_vector
    
    def forward(self, X):
        """前向传播"""
        # 量子模拟
        X_quantum = np.array([self.quantum_simulate(x) for x in X])
        
        # 隐藏层
        hidden = np.tanh(X_quantum.dot(self.weights))
        
        # 输出层
        output = hidden.dot(self.output_weights)
        
        # Softmax激活
        exp_scores = np.exp(output)
        probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)
        
        return probs
    
    def predict(self, X):
        """预测"""
        return self.forward(X)
    
    def train(self, X, y, learning_rate=0.01, epochs=10, batch_size=16):
        """训练模型"""
        n_samples = X.shape[0]
        
        for epoch in range(epochs):
            # 随机打乱数据
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]
            
            # 批次训练
            for i in range(0, n_samples, batch_size):
                end = min(i + batch_size, n_samples)
                X_batch = X_shuffled[i:end]
                y_batch = y_shuffled[i:end]
                
                # 前向传播
                probs = self.forward(X_batch)
                
                # 反向传播
                delta_output = probs - y_batch
                delta_hidden = delta_output.dot(self.output_weights.T) * (1 - np.tanh(X_batch.dot(self.weights))**2)
                
                # 更新权重
                self.output_weights -= learning_rate * np.dot(np.tanh(X_batch.dot(self.weights)).T, delta_output)
                self.weights -= learning_rate * np.dot(X_batch.T, delta_hidden)
            
            # 评估进度
            if (epoch + 1) % 5 == 0 or epoch == 0 or epoch == epochs - 1:
                probs = self.forward(X)
                accuracy = np.mean(np.argmax(probs, axis=1) == np.argmax(y, axis=1))
                logging.getLogger("WeQ-后台训练").info(f"轮次 {epoch+1}/{epochs}, 准确率: {accuracy:.4f}")

def generate_knowledge_for_topic(topic, count=3):
    """为指定主题生成模拟知识向量"""
    knowledge_vectors = []
    knowledge_texts = []
    
    # 尝试使用量子区块链知识库
    if _has_blockchain_knowledge and topic.startswith("量子区块链") or "区块链" in topic or "松麦币" in topic:
        blockchain_knowledge = get_blockchain_knowledge()
        
        # 查找最匹配的主题
        best_match = None
        best_score = 0
        for blockchain_topic in blockchain_knowledge.knowledge_topics:
            # 简单字符串匹配评分
            score = sum(1 for a, b in zip(topic.lower(), blockchain_topic.lower()) if a == b)
            if score > best_score:
                best_score = score
                best_match = blockchain_topic
        
        # 如果找到匹配的主题，使用区块链知识点
        if best_match and best_score > len(topic) * 0.5:
            knowledge_points = blockchain_knowledge.get_knowledge_for_topic(best_match)
            
            # 限制数量
            points_to_use = knowledge_points[:min(count, len(knowledge_points))]
            
            for point in points_to_use:
                # 生成文本
                knowledge_text = f"关于'{best_match}'的知识点: {point['title']} - {point['content']}"
                knowledge_texts.append(knowledge_text)
                
                # 使用知识向量或生成新向量
                if best_match in blockchain_knowledge.knowledge_vectors and len(blockchain_knowledge.knowledge_vectors[best_match]) > 0:
                    # 获取预先生成的向量
                    idx = knowledge_points.index(point) % len(blockchain_knowledge.knowledge_vectors[best_match])
                    vector = blockchain_knowledge.knowledge_vectors[best_match][idx]
                else:
                    # 生成新向量
                    seed = hash(best_match + point["title"]) % 10000
                    np.random.seed(seed)
                    vector = np.random.randn(64)
                    vector = vector / np.linalg.norm(vector)  # 归一化
                
                knowledge_vectors.append(vector)
            
            # 如果数量不足，补充
            while len(knowledge_vectors) < count:
                idx = len(knowledge_vectors) % len(points_to_use)
                knowledge_texts.append(knowledge_texts[idx])
                knowledge_vectors.append(knowledge_vectors[idx])
                
            return knowledge_vectors, knowledge_texts
    
    # 如果不使用量子区块链知识库，使用原始实现
    for i in range(count):
        # 生成模拟知识文本
        knowledge_text = f"关于'{topic}'的知识点{i+1}: 这是模拟的知识内容。"
        knowledge_texts.append(knowledge_text)
        
        # 生成与主题相关的向量
        # 使用随机种子基于主题名称，使得同一主题生成类似的向量
        seed = hash(topic) % 10000
        np.random.seed(seed + i)
        
        # 生成随机向量
        vector = np.random.randn(64)
        
        # 添加与主题相关的特征
        topic_feature = np.zeros(64)
        topic_feature[hash(topic) % 64] = 1.0
        topic_feature[(hash(topic) + 1) % 64] = 0.8
        topic_feature[(hash(topic) + 2) % 64] = 0.6
        
        # 组合随机向量和主题特征
        vector = vector * 0.2 + topic_feature * 0.8
        
        # 归一化
        vector = vector / np.linalg.norm(vector)
        
        knowledge_vectors.append(vector)
    
    return knowledge_vectors, knowledge_texts

def evolve_topics(current_topics):
    """演化主题，生成相关但更深入的主题"""
    evolved_topics = []
    
    # 添加量子区块链主题
    blockchain_topics = [
        "量子区块链基础", "QSM主链架构", "WeQ子链特性", "Ref子链自修复", 
        "松麦币经济系统", "量子纠缠通信", "跨链交互", "量子区块共识"
    ]
    
    # 检查当前主题是否与区块链相关
    has_blockchain_topic = any("区块链" in topic or "松麦币" in topic or "量子纠缠" in topic for topic in current_topics)
    
    topic_extensions = {
        "量子计算基础": ["量子门操作", "量子纠缠应用", "量子算法设计", "量子区块链基础"],
        "神经网络原理": ["深度学习架构", "卷积神经网络", "循环神经网络"],
        "机器学习算法": ["强化学习技术", "无监督学习方法", "半监督学习"],
        "自然语言处理": ["语义分析技术", "情感分析方法", "文本生成模型"],
        "量子纠缠现象": ["量子态传送", "量子密钥分发", "量子信息论", "量子纠缠通信"],
        # 量子区块链相关主题扩展
        "量子区块链基础": ["QSM主链架构", "WeQ子链特性", "松麦币经济系统"],
        "QSM主链架构": ["跨链交互", "量子区块共识", "量子纠缠通信"],
        "WeQ子链特性": ["量子钱包技术", "量子区块共识", "松麦币经济系统"],
        "松麦币经济系统": ["量子钱包技术", "区块链数据结构", "Ref子链自修复"],
        # 第二层主题的扩展
        "量子门操作": ["多量子比特门", "量子电路优化", "量子纠错码"],
        "深度学习架构": ["残差网络结构", "注意力机制", "图神经网络"],
        "强化学习技术": ["策略梯度方法", "Q学习进阶", "多智能体系统"],
        "语义分析技术": ["上下文理解模型", "知识图谱构建", "实体关系抽取"],
        "量子态传送": ["远程纠缠", "量子通信协议", "量子网络架构"]
    }
    
    # 如果有区块链相关主题，增加区块链主题出现的概率
    if has_blockchain_topic and random.random() < 0.7:
        # 从现有主题演化
        for topic in current_topics:
            if topic in topic_extensions:
                # 从扩展中选择1-2个主题
                selections = np.random.choice(topic_extensions[topic], 
                                            size=min(2, len(topic_extensions[topic])), 
                                            replace=False)
                evolved_topics.extend(selections)
            else:
                # 如果没有预定义的扩展，添加一个区块链主题
                evolved_topics.append(random.choice(blockchain_topics))
    else:
        # 有一定概率引入区块链主题
        if random.random() < 0.3:
            evolved_topics.append(random.choice(blockchain_topics))
            
        # 从现有主题演化
        for topic in current_topics:
            if topic in topic_extensions:
                # 从扩展中选择1-2个主题
                selections = np.random.choice(topic_extensions[topic], 
                                            size=min(2, len(topic_extensions[topic])), 
                                            replace=False)
                evolved_topics.extend(selections)
            else:
                # 如果没有预定义的扩展，生成一个通用扩展
                evolved_topics.append(f"{topic}的高级应用")
    
    # 保持主题数量合理
    if len(evolved_topics) > 5:
        evolved_topics = evolved_topics[:5]
    
    return evolved_topics

# 导入必要的模块
try:
    # 可选地使用外部模块，如果导入失败则使用上面定义的内部实现
    from start_knowledge_training_simple import SimpleQuantumNetwork as ExternalSimpleQuantumNetwork
    from start_knowledge_training_simple import generate_knowledge_for_topic as external_generate_knowledge_for_topic
    from start_knowledge_training_simple import evolve_topics as external_evolve_topics
    # 如果成功导入，可以选择是否替换当前实现
    # SimpleQuantumNetwork = ExternalSimpleQuantumNetwork
    # generate_knowledge_for_topic = external_generate_knowledge_for_topic
    # evolve_topics = external_evolve_topics
    logging.info("成功导入外部训练模块，但使用内部实现")
except ImportError as e:
    logging.info(f"使用内部训练模块实现: {str(e)}")

# 创建必要的目录
os.makedirs('training_data', exist_ok=True)
os.makedirs('crawler_data', exist_ok=True)
os.makedirs('models/checkpoints', exist_ok=True)
os.makedirs('logs', exist_ok=True)

class BackgroundTrainer:
    """WeQ后台训练系统"""
    
    def __init__(self, model_path="models/weq_model_28qubit_trained_simple.json"):
        """初始化后台训练系统"""
        self.model_path = model_path
        self.model = SimpleQuantumNetwork()
        self.current_topics = [
            "量子计算基础",
            "神经网络原理",
            "机器学习算法"
        ]
        
        # 训练状态
        self.is_running = False
        self.claude_training_interval = 30  # 分钟
        self.crawler_training_interval = 120  # 分钟
        self.qsm_training_interval = 60  # 分钟
        self.training_cycles = 0
        
        # 学习开关，确保学习功能启用
        self.enable_claude_training = True
        self.enable_crawler_training = True
        self.enable_qsm_training = True
        
        # 训练线程
        self.claude_thread = None
        self.crawler_thread = None
        self.qsm_thread = None
        
        # 训练历史
        self.training_history = {
            "claude_cycles": 0,
            "crawler_cycles": 0,
            "qsm_cycles": 0,
            "topics_trained": set(),
            "last_claude_training": 0,
            "last_crawler_training": 0,
            "last_qsm_training": 0
        }
        
        # 数据缓存
        self.knowledge_cache = {}
        
        # 爬虫数据源
        self.crawler_sources = [
            {"name": "量子计算论文", "url_template": "https://arxiv.org/search/?query=quantum+computing"},
            {"name": "IBM量子博客", "url_template": "https://www.ibm.com/blogs/research/category/quantum-computing/"},
            {"name": "API设计指南", "url_template": "https://cloud.google.com/apis/design"},
            {"name": "REST API教程", "url_template": "https://restfulapi.net/"}
        ]
        
        # 链接量子区块链知识库
        if _has_blockchain_knowledge:
            self.blockchain_knowledge = get_blockchain_knowledge()
            self.blockchain_knowledge.connect_qsm_network(self.model)
            logger.info("已连接到量子区块链知识库")
        else:
            self.blockchain_knowledge = None
            
        # 链接量子叠加态模型知识库
        if _has_qsm_knowledge:
            self.qsm_knowledge = get_qsm_knowledge()
            logger.info("已连接到量子叠加态模型知识库")
        else:
            self.qsm_knowledge = None
        
        # 尝试加载现有模型
        try:
            self.load_model()
        except Exception as e:
            logger.warning(f"加载模型失败，使用新模型: {str(e)}")
            # 创建初始配置
            self.config = {
                'input_dim': 64,
                'hidden_dim': 32,
                'output_dim': 5,
                'qubit_count': 28,
                'training_records': [],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_topics_trained': 0,
                'learning_modes': {
                    'claude_training': True,
                    'crawler_training': True,
                    'qsm_training': True
                }
            }
            # 保存初始模型
            self.save_model()
        
        logger.info("WeQ后台训练系统初始化完成")
    
    def load_model(self):
        """加载WeQ模型"""
        try:
            # 尝试加载主配置文件
            model_path = self.model_path
            
            # 如果主配置文件不存在，尝试加载备用配置文件
            if not os.path.exists(model_path):
                backup_path = "models/weq_model_28qubit_config.json"
                if os.path.exists(backup_path):
                    model_path = backup_path
                    logger.info(f"主配置文件不存在，使用备用配置文件: {backup_path}")
                else:
                    logger.warning("主配置文件和备用配置文件都不存在，将创建新配置")
                    raise FileNotFoundError("配置文件不存在")
            
            # 加载模型配置
            with open(model_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # 创建模型实例
            self.model = SimpleQuantumNetwork(
                input_dim=self.config.get('input_dim', 64),
                hidden_dim=self.config.get('hidden_dim', 32),
                output_dim=self.config.get('output_dim', 5),
                qubit_count=self.config.get('qubit_count', 28)
            )
            
            # 设置学习开关
            learning_modes = self.config.get('learning_modes', {})
            self.enable_claude_training = learning_modes.get('claude_training', True)
            self.enable_crawler_training = learning_modes.get('crawler_training', True)
            self.enable_qsm_training = learning_modes.get('qsm_training', True)
            
            # 初始化主题
            if self.config.get('training_records') and len(self.config['training_records']) > 0:
                # 使用最后一次训练的主题
                last_record = self.config['training_records'][-1]
                self.current_topics = last_record.get('topics', [])
                # 记录所有训练过的主题
                for record in self.config['training_records']:
                    for topic in record.get('topics', []):
                        self.training_history["topics_trained"].add(topic)
                        
                # 设置训练迭代次数
                self.training_cycles = max([r.get('iteration', 0) for r in self.config['training_records']])
            
            logger.info(f"成功加载WeQ模型, 当前主题: {', '.join(self.current_topics)}")
            return True
        except Exception as e:
            logger.error(f"加载WeQ模型失败: {str(e)}", exc_info=True)
            return False
    
    def save_model(self, checkpoint=False):
        """保存模型配置和训练历史"""
        try:
            # 更新配置
            self.config['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.config['total_topics_trained'] = len(self.training_history["topics_trained"])
            
            # 保存路径
            if checkpoint:
                save_path = f"models/checkpoints/weq_model_28qubit_iter{self.training_cycles}.json"
            else:
                save_path = self.model_path
            
            # 保存配置
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"模型配置已保存: {save_path}")
            return save_path
        except Exception as e:
            logger.error(f"保存模型失败: {str(e)}", exc_info=True)
            return None
    
    def select_next_topics(self):
        """选择下一批训练主题"""
        # 已训练的主题
        trained_topics = self.training_history["topics_trained"]
        
        # 选择策略:
        # 1. 优先选择QSM相关主题中未训练的主题
        # 2. 如果QSM主题都训练过了，选择高级主题
        # 3. 如果上述都训练过了，使用主题演化
        
        # 从QSM主题中选择
        available_qsm_topics = [t for t in self.current_topics if t not in trained_topics]
        
        if available_qsm_topics:
            # 优先选择QSM主题
            selected_topics = random.sample(
                available_qsm_topics,
                min(5, len(available_qsm_topics))
            )
            logger.info(f"从QSM主题库中选择了新主题: {', '.join(selected_topics)}")
            return selected_topics
            
        # 从高级主题中选择
        available_advanced_topics = [t for t in self.current_topics if t not in trained_topics]
        
        if available_advanced_topics:
            # 选择高级主题
            selected_topics = random.sample(
                available_advanced_topics,
                min(5, len(available_advanced_topics))
            )
            logger.info(f"从高级主题库中选择了新主题: {', '.join(selected_topics)}")
            return selected_topics
        
        # 使用主题演化
        evolved_topics = evolve_topics(self.current_topics)
        logger.info(f"使用主题演化生成了新主题: {', '.join(evolved_topics)}")
        return evolved_topics
    
    def generate_training_data(self, topics, samples_per_topic=3):
        """为主题生成训练数据"""
        all_vectors = []
        all_labels = []
        
        # 为每个主题创建标签的one-hot编码
        topic_to_id = {topic: i for i, topic in enumerate(topics)}
        
        for topic in topics:
            # 为每个主题生成知识向量
            vectors, _ = generate_knowledge_for_topic(topic, count=samples_per_topic)
            
            for vector in vectors:
                all_vectors.append(vector)
                
                # 创建one-hot标签
                label = np.zeros(len(topics))
                label[topic_to_id[topic]] = 1
                all_labels.append(label)
                
            # 记录已训练主题
            self.training_history["topics_trained"].add(topic)
        
        return np.array(all_vectors), np.array(all_labels)
    
    def qsm_training_cycle(self):
        """执行一次量子叠加态模型知识学习训练循环"""
        if self.is_running or not self.enable_qsm_training:
            logger.warning("量子叠加态模型知识学习训练已禁用或上一次训练尚未完成，跳过本次训练")
            return False
        
        try:
            self.is_running = True
            self.training_cycles += 1
            logger.info(f"开始第{self.training_cycles}次量子叠加态模型知识学习训练")
            
            # 获取量子叠加态模型知识主题
            qsm_topics = [
                "量子叠加态理论",
                "QSM主量子链",
                "子量子链交互",
                "量子纠缠通信",
                "松麦币统一标准"
            ]
            
            # 如果有量子叠加态模型知识库，使用其主题
            if self.qsm_knowledge:
                try:
                    qsm_topics = self.qsm_knowledge.get_all_topics()
                    logger.info(f"从量子叠加态模型知识库获取主题: {len(qsm_topics)}个")
                except:
                    logger.warning("使用默认量子叠加态模型主题")
            
            # 随机选择2-3个主题进行学习
            selected_topics = random.sample(
                qsm_topics,
                min(random.randint(2, 3), len(qsm_topics))
            )
            
            logger.info(f"选择量子叠加态模型主题: {', '.join(selected_topics)}")
            
            # 生成训练数据
            X, y = self.generate_training_data(selected_topics, samples_per_topic=5)
            
            # 训练前评估
            initial_predictions = self.model.predict(X)
            initial_accuracy = np.mean(np.argmax(initial_predictions, axis=1) == np.argmax(y, axis=1))
            logger.info(f"量子叠加态模型训练前准确率: {initial_accuracy:.4f}")
            
            # 训练模型
            epochs = 15
            self.model.train(X, y, learning_rate=0.005, epochs=epochs, batch_size=4)
            
            # 评估训练后的性能
            predictions = self.model.predict(X)
            final_accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
            logger.info(f"量子叠加态模型训练后准确率: {final_accuracy:.4f}")
            
            # 记录训练结果
            training_record = {
                "iteration": self.training_cycles,
                "topics": selected_topics,
                "samples": len(X),
                "initial_accuracy": float(initial_accuracy),
                "final_accuracy": float(final_accuracy),
                "improvement": float(final_accuracy - initial_accuracy),
                "training_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "training_type": "qsm_knowledge"
            }
            
            # 更新配置
            if 'training_records' not in self.config:
                self.config['training_records'] = []
            self.config['training_records'].append(training_record)
            
            # 保存模型
            self.save_model()
            
            self.training_history["last_qsm_training"] = datetime.now()
            self.training_history["qsm_cycles"] += 1
            logger.info(f"完成量子叠加态模型知识学习训练，已学习主题: {', '.join(selected_topics)}")
            
            self.is_running = False
            return True
        except Exception as e:
            logger.error(f"量子叠加态模型知识学习训练失败: {str(e)}", exc_info=True)
            self.is_running = False
            return False
    
    def claude_training_cycle(self):
        """执行一次Claude知识教学训练循环"""
        if self.is_running or not self.enable_claude_training:
            logger.warning("Claude知识教学训练已禁用或上一次训练尚未完成，跳过本次训练")
            return False
        
        try:
            self.is_running = True
            self.training_cycles += 1
            logger.info(f"开始第{self.training_cycles}次Claude知识教学训练")
            
            # 选择训练主题
            self.current_topics = self.select_next_topics()
            logger.info(f"当前训练主题: {', '.join(self.current_topics)}")
            
            # 生成训练数据
            X, y = self.generate_training_data(self.current_topics, samples_per_topic=5)
            
            # 训练前评估
            initial_predictions = self.model.predict(X)
            initial_accuracy = np.mean(np.argmax(initial_predictions, axis=1) == np.argmax(y, axis=1))
            logger.info(f"训练前准确率: {initial_accuracy:.4f}")
            
            # 训练模型
            epochs = 20  # 更多轮次以提高准确率
            self.model.train(X, y, learning_rate=0.005, epochs=epochs, batch_size=4)
            
            # 评估训练后的性能
            predictions = self.model.predict(X)
            final_accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
            logger.info(f"训练后准确率: {final_accuracy:.4f}")
            
            # 记录训练结果
            training_record = {
                "iteration": self.training_cycles,
                "topics": self.current_topics,
                "samples": len(X),
                "initial_accuracy": float(initial_accuracy),
                "final_accuracy": float(final_accuracy),
                "improvement": float(final_accuracy - initial_accuracy),
                "training_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "training_type": "claude_knowledge"
            }
            
            # 更新配置
            if 'training_records' not in self.config:
                self.config['training_records'] = []
            self.config['training_records'].append(training_record)
            
            # 保存模型
            self.save_model()
            # 每5次训练保存一个检查点
            if self.training_cycles % 5 == 0:
                self.save_model(checkpoint=True)
                
            self.training_history["last_claude_training"] = datetime.now()
            self.training_history["claude_cycles"] += 1
            logger.info(f"完成Claude知识教学训练，下一次主题: {', '.join(self.current_topics)}")
            
            self.is_running = False
            return True
        except Exception as e:
            logger.error(f"Claude知识教学训练失败: {str(e)}", exc_info=True)
            self.is_running = False
            return False
    
    def crawler_training_cycle(self):
        """执行一次爬虫数据训练循环"""
        if self.is_running or not self.enable_crawler_training:
            logger.warning("爬虫数据训练已禁用或上一次训练尚未完成，跳过本次爬虫训练")
            return False
            
        try:
            self.is_running = True
            logger.info("开始爬虫数据训练")
            
            # 模拟爬虫收集数据
            # 注意：在实际实现中，这里应该调用真实的爬虫模块
            collected_data = self.simulate_crawler_data_collection()
            
            if not collected_data or len(collected_data) == 0:
                logger.warning("未收集到爬虫数据，跳过训练")
                self.is_running = False
                return False
            
            # 处理爬虫数据
            X, y, topics = self.process_crawler_data(collected_data)
            
            if len(X) == 0:
                logger.warning("爬虫数据处理后为空，跳过训练")
                self.is_running = False
                return False
            
            # 训练前评估
            initial_predictions = self.model.predict(X)
            initial_accuracy = np.mean(np.argmax(initial_predictions, axis=1) == np.argmax(y, axis=1))
            logger.info(f"爬虫训练前准确率: {initial_accuracy:.4f}")
            
            # 训练模型
            epochs = 15
            self.model.train(X, y, learning_rate=0.005, epochs=epochs, batch_size=4)
            
            # 评估训练后的性能
            predictions = self.model.predict(X)
            final_accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
            logger.info(f"爬虫训练后准确率: {final_accuracy:.4f}")
            
            # 记录训练结果
            self.training_cycles += 1
            training_record = {
                "iteration": self.training_cycles,
                "topics": topics,
                "samples": len(X),
                "initial_accuracy": float(initial_accuracy),
                "final_accuracy": float(final_accuracy),
                "improvement": float(final_accuracy - initial_accuracy),
                "training_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "training_type": "crawler_data"
            }
            
            # 更新配置
            if 'training_records' not in self.config:
                self.config['training_records'] = []
            self.config['training_records'].append(training_record)
            
            # 保存模型
            self.save_model()
            
            self.training_history["last_crawler_training"] = datetime.now()
            self.training_history["crawler_cycles"] += 1
            logger.info(f"完成爬虫数据训练，主题: {', '.join(topics)}")
            
            self.is_running = False
            return True
        except Exception as e:
            logger.error(f"爬虫数据训练失败: {str(e)}", exc_info=True)
            self.is_running = False
            return False
    
    def simulate_crawler_data_collection(self):
        """模拟爬虫数据收集
        
        注意：这只是一个模拟实现，实际系统应该实现真正的网页爬取
        """
        try:
            # 模拟收集到的数据
            collected_data = []
            
            # 随机选择1-3个数据源
            selected_sources = random.sample(
                self.crawler_sources,
                min(random.randint(1, 3), len(self.crawler_sources))
            )
            
            for source in selected_sources:
                # 模拟从该数据源收集3-5篇文档
                for _ in range(random.randint(3, 5)):
                    # 生成模拟数据
                    doc = {
                        "source": source["name"],
                        "title": f"{source['name']}样本文档 #{random.randint(1, 100)}",
                        "content": f"这是从{source['name']}收集的模拟内容样本。包含了相关的技术信息和知识。",
                        "url": source.get("url_template", "https://example.com"),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    collected_data.append(doc)
            
            logger.info(f"模拟爬虫收集了{len(collected_data)}篇文档")
            
            # 保存收集的数据
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crawler_data/crawled_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(collected_data, f, ensure_ascii=False, indent=2)
            
            return collected_data
        except Exception as e:
            logger.error(f"爬虫数据收集失败: {str(e)}", exc_info=True)
            return []
    
    def process_crawler_data(self, collected_data):
        """处理爬虫收集的数据，转换为训练格式"""
        try:
            # 根据数据源分配主题
            source_to_topic = {
                "量子计算论文": "量子计算研究",
                "IBM量子博客": "量子计算应用",
                "API设计指南": "API设计模式",
                "REST API教程": "REST API开发"
            }
            
            # 收集文档主题
            doc_topics = []
            for doc in collected_data:
                source = doc.get("source", "")
                if source in source_to_topic:
                    topic = source_to_topic[source]
                    if topic not in doc_topics:
                        doc_topics.append(topic)
            
            # 如果没有识别出主题，使用默认主题
            if not doc_topics:
                doc_topics = ["未分类文档", "网络数据", "爬虫样本"]
            
            # 为新主题创建向量和标签
            topic_to_id = {topic: i for i, topic in enumerate(doc_topics)}
            
            X = []
            y = []
            
            for doc in collected_data:
                # 确定文档主题
                source = doc.get("source", "")
                if source in source_to_topic:
                    topic = source_to_topic[source]
                else:
                    topic = "未分类文档"
                
                # 如果识别出的主题不在主题列表中，使用第一个主题
                if topic not in doc_topics:
                    topic = doc_topics[0]
                
                # 提取文档内容
                text = f"{doc.get('title', '')} {doc.get('content', '')}"
                
                # 模拟文本向量化
                # 在实际实现中，应该使用更复杂的向量化方法
                vector = self.text_to_vector(text)
                X.append(vector)
                
                # 创建标签
                label = np.zeros(len(doc_topics))
                label[topic_to_id[topic]] = 1
                y.append(label)
                
                # 记录已训练主题
                self.training_history["topics_trained"].add(topic)
            
            return np.array(X), np.array(y), doc_topics
        except Exception as e:
            logger.error(f"处理爬虫数据失败: {str(e)}", exc_info=True)
            return np.array([]), np.array([]), []
    
    def text_to_vector(self, text, dim=64):
        """将文本转换为固定维度的向量"""
        # 简化版文本向量化
        if not text:
            return np.zeros(dim)
        
        # 1. 计算词频特征
        words = text.lower().split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 2. 生成向量
        vector = np.zeros(dim)
        for i, word in enumerate(word_freq):
            if i >= dim:
                break
            vector[i % dim] += word_freq[word]
        
        # 3. 归一化
        if np.linalg.norm(vector) > 0:
            vector = vector / np.linalg.norm(vector)
        
        return vector
    
    def start_background_training(self):
        """启动后台训练线程"""
        self.is_running = False
        
        # 创建并启动Claude训练线程
        if self.enable_claude_training:
            self.claude_thread = threading.Thread(
            target=self._claude_training_loop,
            name="Claude训练线程"
        )
            self.claude_thread.daemon = True
            self.claude_thread.start()
            logger.info("Claude知识教学训练线程已启动")
        else:
            logger.warning("Claude知识教学训练已禁用")
        
        # 创建并启动爬虫训练线程
        if self.enable_crawler_training:
            self.crawler_thread = threading.Thread(
            target=self._crawler_training_loop,
            name="爬虫训练线程"
        )
            self.crawler_thread.daemon = True
            self.crawler_thread.start()
            logger.info("爬虫数据训练线程已启动")
        else:
            logger.warning("爬虫数据训练已禁用")
            
        # 创建并启动量子叠加态模型知识学习线程
        if self.enable_qsm_training:
            self.qsm_thread = threading.Thread(
                target=self._qsm_training_loop,
                name="量子叠加态模型训练线程"
            )
            self.qsm_thread.daemon = True
            self.qsm_thread.start()
            logger.info("量子叠加态模型知识学习线程已启动")
        else:
            logger.warning("量子叠加态模型知识学习已禁用")
        
        # 创建并启动监控线程，确保训练不中断
        self.monitor_thread = threading.Thread(
            target=self._monitor_training_threads,
            name="训练监控线程"
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("训练监控线程已启动")
        
        # 创建并启动日志备份线程
        self.log_backup_thread = threading.Thread(
            target=self._log_backup_loop,
            name="日志备份线程"
        )
        self.log_backup_thread.daemon = True
        self.log_backup_thread.start()
        logger.info("日志备份线程已启动")
        
        logger.info("所有后台训练线程已启动，系统将24小时不间断运行")
        return (self.claude_thread, self.crawler_thread, self.qsm_thread, self.monitor_thread, self.log_backup_thread)
    
    def _monitor_training_threads(self):
        """监控训练线程，确保它们正常运行"""
        logger.info("开始监控训练线程")
        
        while True:
            try:
                # 检查Claude训练线程
                if self.enable_claude_training and (not self.claude_thread or not self.claude_thread.is_alive()):
                    logger.warning("检测到Claude训练线程已停止，正在重启...")
                    self.claude_thread = threading.Thread(
                        target=self._claude_training_loop,
                        name="Claude训练线程"
                    )
                    self.claude_thread.daemon = True
                    self.claude_thread.start()
                    logger.info("Claude训练线程已重启")
                
                # 检查爬虫训练线程
                if self.enable_crawler_training and (not self.crawler_thread or not self.crawler_thread.is_alive()):
                    logger.warning("检测到爬虫训练线程已停止，正在重启...")
                    self.crawler_thread = threading.Thread(
                        target=self._crawler_training_loop,
                        name="爬虫训练线程"
                    )
                    self.crawler_thread.daemon = True
                    self.crawler_thread.start()
                    logger.info("爬虫训练线程已重启")
                
                # 检查量子叠加态模型训练线程
                if self.enable_qsm_training and (not self.qsm_thread or not self.qsm_thread.is_alive()):
                    logger.warning("检测到量子叠加态模型训练线程已停止，正在重启...")
                    self.qsm_thread = threading.Thread(
                        target=self._qsm_training_loop,
                        name="量子叠加态模型训练线程"
                    )
                    self.qsm_thread.daemon = True
                    self.qsm_thread.start()
                    logger.info("量子叠加态模型训练线程已重启")
                
                # 保存模型状态，确保数据不丢失
                self.save_model()
                
                # 每10分钟检查一次
                time.sleep(600)
            except Exception as e:
                logger.error(f"监控线程出错: {str(e)}", exc_info=True)
                time.sleep(300)  # 出错后等待5分钟再继续
    
    def _log_backup_loop(self):
        """定期备份日志文件"""
        logger.info("开始日志备份循环")
        
        while True:
            try:
                # 每天凌晨2点备份日志
                now = datetime.now()
                # 计算下一个凌晨2点
                next_backup = datetime(now.year, now.month, now.day, 2, 0, 0)
                if now.hour >= 2:
                    next_backup = next_backup + timedelta(days=1)
                
                # 计算等待时间
                wait_seconds = (next_backup - now).total_seconds()
                if wait_seconds > 0:
                    time.sleep(wait_seconds)
                
                # 备份日志文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_src = "background_training.log"
                log_dst = f"logs/background_training_{timestamp}.log"
                
                if os.path.exists(log_src) and os.path.getsize(log_src) > 0:
                    os.makedirs("logs", exist_ok=True)
                    # 复制而非移动，保持原日志文件可用
                    with open(log_src, 'r', encoding='utf-8') as src_file:
                        with open(log_dst, 'w', encoding='utf-8') as dst_file:
                            dst_file.write(src_file.read())
                    
                    logger.info(f"日志已备份至 {log_dst}")
                    
                    # 判断是否需要清空原日志文件
                    if os.path.getsize(log_src) > 10 * 1024 * 1024:  # 10MB
                        with open(log_src, 'w', encoding='utf-8') as f:
                            f.write(f"# 日志文件已于 {timestamp} 清空并备份至 {log_dst}\n")
                        logger.info("由于日志文件过大，已清空原日志文件")
                
                # 清理过期日志（保留30天）
                self._clean_old_logs(30)
                
                time.sleep(3600)  # 每小时检查一次
            except Exception as e:
                logger.error(f"日志备份出错: {str(e)}", exc_info=True)
                time.sleep(3600)  # 出错后等待1小时再继续
    
    def _clean_old_logs(self, days_to_keep=30):
        """清理超过指定天数的旧日志"""
        try:
            logs_dir = "logs"
            if not os.path.exists(logs_dir):
                return
                
            now = datetime.now()
            cutoff_date = now - timedelta(days=days_to_keep)
            
            for filename in os.listdir(logs_dir):
                if filename.startswith("background_training_") and filename.endswith(".log"):
                    try:
                        # 从文件名中提取日期 (格式: background_training_YYYYMMDD_HHMMSS.log)
                        date_str = filename.split("_")[2]  # 获取YYYYMMDD部分
                        file_date = datetime.strptime(date_str, "%Y%m%d")
                        
                        if file_date < cutoff_date:
                            file_path = os.path.join(logs_dir, filename)
                            os.remove(file_path)
                            logger.info(f"已删除过期日志: {filename}")
                    except Exception as e:
                        logger.warning(f"处理日志文件 {filename} 时出错: {str(e)}")
        except Exception as e:
            logger.error(f"清理旧日志出错: {str(e)}", exc_info=True)
    
    def _claude_training_loop(self):
        """Claude训练循环"""
        logger.info("Claude训练循环已启动")
        
        # 设置训练计划 - 每小时执行一次
        schedule.every(1).hours.do(self.claude_training_cycle)
        
        # 立即执行一次训练
        try:
            self.claude_training_cycle()
        except Exception as e:
            logger.error(f"Claude训练首次执行失败: {str(e)}", exc_info=True)
        
        while True:
            try:
                if self.is_running:
                    time.sleep(60)
                    continue
                
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次计划
            except Exception as e:
                logger.error(f"Claude训练循环出错: {str(e)}", exc_info=True)
                time.sleep(300)  # 发生错误后等待5分钟再继续
    
    def _crawler_training_loop(self):
        """爬虫训练循环"""
        logger.info("爬虫训练循环已启动")
        
        # 设置训练计划 - 每3小时执行一次
        schedule.every(3).hours.do(self.crawler_training_cycle)
        
        # 等待30分钟后执行第一次训练
        time.sleep(1800)
        try:
            self.crawler_training_cycle()
        except Exception as e:
            logger.error(f"爬虫训练首次执行失败: {str(e)}", exc_info=True)
        
        while True:
            try:
                if self.is_running:
                    time.sleep(60)
                    continue
                
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次计划
            except Exception as e:
                logger.error(f"爬虫训练循环出错: {str(e)}", exc_info=True)
                time.sleep(300)  # 发生错误后等待5分钟再继续
    
    def _qsm_training_loop(self):
        """量子叠加态模型知识学习循环"""
        logger.info("量子叠加态模型知识学习循环已启动")
        
        # 设置训练计划 - 每2小时执行一次
        schedule.every(2).hours.do(self.qsm_training_cycle)
        
        # 立即执行一次训练
        time.sleep(1200)  # 等待20分钟后执行第一次训练
        try:
            self.qsm_training_cycle()
        except Exception as e:
            logger.error(f"量子叠加态模型训练首次执行失败: {str(e)}", exc_info=True)
        
        while True:
            try:
                if self.is_running:
                    time.sleep(60)
                    continue
                
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次计划
            except Exception as e:
                logger.error(f"量子叠加态模型训练循环出错: {str(e)}", exc_info=True)
                time.sleep(300)  # 发生错误后等待5分钟再继续
    
    def stop_background_training(self):
        """停止后台训练"""
        self.is_running = True
        logger.info("已发送停止信号，后台训练将在当前任务完成后停止")
        
        # 保存最终模型
        self.save_model()
        self.save_model(checkpoint=True)
        
        return True
    
    def get_training_status(self):
        """获取训练状态"""
        return {
            "is_running": self.is_running,
            "claude_training_enabled": self.enable_claude_training,
            "crawler_training_enabled": self.enable_crawler_training,
            "qsm_training_enabled": self.enable_qsm_training,
            "training_cycles": self.training_cycles,
            "claude_cycles": self.training_history["claude_cycles"],
            "crawler_cycles": self.training_history["crawler_cycles"],
            "qsm_cycles": self.training_history["qsm_cycles"],
            "topics_trained": len(self.training_history["topics_trained"]),
            "current_topics": self.current_topics,
            "last_claude_training": self.training_history["last_claude_training"],
            "last_crawler_training": self.training_history["last_crawler_training"],
            "last_qsm_training": self.training_history["last_qsm_training"]
        }

def main():
    """主函数"""
    try:
        # 检查是否已经有实例在运行
        if _check_already_running():
            logger.warning("检测到WeQ后台训练系统已经在运行，退出当前实例")
            return 0
        
        # 创建后台训练器
        trainer = BackgroundTrainer()
        
        # 确保所有学习功能开启
        trainer.enable_claude_training = True
        trainer.enable_crawler_training = True
        trainer.enable_qsm_training = True
        
        # 启动后台训练
        threads = trainer.start_background_training()
        
        logger.info("后台训练系统已启动")
        logger.info("系统将在后台24小时不间断运行")
        logger.info("输入'q'或'quit'退出训练")
        logger.info("输入'status'查看训练状态")
        
        # 创建看门狗线程，确保系统不会因主线程退出而停止
        watchdog_thread = threading.Thread(
            target=_watchdog_function,
            args=(trainer,),
            name="看门狗线程"
        )
        watchdog_thread.daemon = False  # 非守护线程，确保程序不会立即退出
        watchdog_thread.start()
        
        # 等待用户输入退出命令
        while True:
            try:
                cmd = input()
                if cmd.lower() in ['q', 'quit', 'exit']:
                    break
                elif cmd.lower() == 'status':
                    status = trainer.get_training_status()
                    print("\n===== WeQ后台训练状态 =====")
                    print(f"当前训练迭代: {status['training_cycles']}")
                    print(f"正在训练中: {'是' if status['is_running'] else '否'}")
                    print(f"\nClaude教学训练: {'启用' if status['claude_training_enabled'] else '禁用'}")
                    print(f"Claude教学循环次数: {status['claude_cycles']}")
                    print(f"上次Claude教学时间: {status['last_claude_training']}")
                    print(f"\n爬虫数据训练: {'启用' if status['crawler_training_enabled'] else '禁用'}")
                    print(f"爬虫训练循环次数: {status['crawler_cycles']}")
                    print(f"上次爬虫训练时间: {status['last_crawler_training']}")
                    print(f"\n量子叠加态模型训练: {'启用' if status['qsm_training_enabled'] else '禁用'}")
                    print(f"量子模型训练循环次数: {status['qsm_cycles']}")
                    print(f"上次量子模型训练时间: {status['last_qsm_training']}")
                    print(f"\n当前训练主题: {', '.join(status['current_topics'])}")
                    print(f"已训练主题总数: {status['topics_trained']}")
                    print("===========================\n")
                elif cmd.lower() == 'restart':
                    print("正在重启训练系统...")
                    trainer.stop_background_training()
                    time.sleep(3)
                    trainer = BackgroundTrainer()
                    threads = trainer.start_background_training()
                    print("训练系统已重启")
                elif cmd.lower() == 'help':
                    print("\n可用命令:")
                    print("status - 显示训练状态")
                    print("restart - 重启训练系统")
                    print("q/quit/exit - 退出程序")
                    print("help - 显示帮助信息\n")
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"处理用户输入时出错: {str(e)}", exc_info=True)
                time.sleep(1)
        
        # 停止训练
        trainer.stop_background_training()
        logger.info("后台训练系统已停止")
        
    except Exception as e:
        logger.error(f"后台训练系统发生错误: {str(e)}", exc_info=True)
        return 1
    
    return 0

def _check_already_running():
    """检查是否已经有训练系统在运行"""
    pid_file = "weq_training.pid"
    
    # 检查PID文件是否存在
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # 在Windows上检查进程是否存在
            if sys.platform == "win32":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                SYNCHRONIZE = 0x00100000
                process = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
                if process:
                    kernel32.CloseHandle(process)
                    return True
                return False
            
            # 在Unix系统上检查进程是否存在
            else:
                try:
                    os.kill(pid, 0)
                    return True
                except OSError:
                    # 进程不存在，可以创建新实例
                    pass
        except:
            # PID文件存在但无法读取或格式不正确
            pass
    
    # 创建新的PID文件
    try:
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
    except:
        logger.error("无法创建PID文件")
    
    return False

def _watchdog_function(trainer):
    """看门狗函数，确保所有线程正常运行并定期保存状态"""
    logger.info("看门狗线程已启动")
    
    while True:
        try:
            # 保存模型状态
            trainer.save_model()
            
            # 日志健康状态
            logger.info("看门狗检查: 训练系统正常运行中")
            
            # 每小时检查一次
            time.sleep(3600)
        except Exception as e:
            logger.error(f"看门狗线程出错: {str(e)}", exc_info=True)
            time.sleep(300)  # 5分钟后重试

def run_as_service():
    """以服务方式运行训练系统"""
    logger.info("以服务方式启动WeQ后台训练系统")
    
    # 创建后台训练器
    trainer = BackgroundTrainer()
    
    # 确保所有学习功能开启
    trainer.enable_claude_training = True
    trainer.enable_crawler_training = True
    trainer.enable_qsm_training = True
    
    # 启动后台训练
    threads = trainer.start_background_training()
    
    # 创建看门狗线程
    watchdog_thread = threading.Thread(
        target=_watchdog_function,
        args=(trainer,),
        name="看门狗线程"
    )
    watchdog_thread.daemon = False
    watchdog_thread.start()
    
    # 主线程等待，保持程序运行
    try:
        while True:
            time.sleep(3600)  # 每小时检查一次
    except KeyboardInterrupt:
        logger.info("接收到停止信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"服务运行出错: {str(e)}", exc_info=True)
    finally:
        trainer.stop_background_training()
        logger.info("服务已停止")

if __name__ == "__main__":
    # 解析命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--service':
        run_as_service()
    else:
        sys.exit(main()) 

"""
"""
量子基因编码: QE-BAC-D5E9162D9C86
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
