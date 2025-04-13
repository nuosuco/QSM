"""
WeQ量子基因神经网络训练器
使用Claude API提供的知识数据训练28量子比特的WeQ模型
"""

import os
import sys
import json
import numpy as np
import logging
import time
import argparse
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 引入量子适配器和桥接模块
from quantum_gene_network.quantum_adapter import QuantumKnowledgeAdapter, prepare_knowledge_for_weq
from quantum_gene_network.claude_quantum_bridge import ClaudeQuantumBridge, create_quantum_teaching_session

# 引入训练用的WeQ模型
from train_quantum_gene_network import QubitNeuralNetwork28

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='weq_trainer.log'
)
logger = logging.getLogger(__name__)

class WeQTrainer:
    """WeQ量子基因神经网络训练器"""
    
    def __init__(self, model_config=None, model_path=None):
        """
        初始化WeQ训练器
        
        Args:
            model_config: 模型配置字典
            model_path: 模型文件路径
        """
        self.model = None
        self.adapter = None
        self.bridge = None
        self.training_history = []
        self.current_topics = []
        
        # 加载或创建模型
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        elif model_config:
            self.create_model(model_config)
        else:
            # 使用默认配置
            self.create_model({
                "input_dim": 64,
                "hidden_dim": 32,
                "output_dim": 3,
                "qubit_count": 28,
                "batch_size": 16
            })
        
        # 初始化适配器
        self.adapter = QuantumKnowledgeAdapter(
            input_dim=self.model.input_dim,
            qubit_dim=self.model.qubit_count
        )
        
        logger.info("WeQ训练器初始化完成")
    
    def create_model(self, config):
        """
        创建WeQ模型
        
        Args:
            config: 模型配置字典
        """
        self.model = QubitNeuralNetwork28(
            input_dim=config.get("input_dim", 64),
            hidden_dim=config.get("hidden_dim", 32),
            output_dim=config.get("output_dim", 3),
            qubit_count=config.get("qubit_count", 28),
            batch_size=config.get("batch_size", 16)
        )
        logger.info(f"创建WeQ模型: {config}")
    
    def load_model(self, model_path):
        """
        加载WeQ模型
        
        Args:
            model_path: 模型文件路径
        """
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.create_model(config)
            logger.info(f"加载WeQ模型: {model_path}")
            return True
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            return False
    
    def connect_to_claude(self, weq_model_path=None):
        """
        连接到Claude API
        
        Args:
            weq_model_path: WeQ模型路径
            
        Returns:
            是否成功连接
        """
        try:
            # 创建桥接
            self.bridge = ClaudeQuantumBridge(
                weq_model_path=weq_model_path or "models/weq_model_28qubit.json",
                vector_dim=self.model.input_dim,
                quantum_dim=self.model.qubit_count
            )
            
            # 启动查询处理线程
            self.bridge.start_query_handler()
            logger.info("已连接到Claude API")
            return True
        except Exception as e:
            logger.error(f"连接Claude API失败: {str(e)}")
            return False
    
    def train_from_claude_knowledge(self, topics, samples_per_topic=5, epochs=10):
        """
        从Claude获取知识并训练
        
        Args:
            topics: 训练主题列表
            samples_per_topic: 每个主题的样本数
            epochs: 训练轮次
            
        Returns:
            训练结果
        """
        if not self.bridge:
            logger.error("尚未连接到Claude API")
            return False
        
        self.current_topics = topics
        topic_vectors = {}
        all_responses = []
        
        # 从Claude获取各主题知识
        for topic in topics:
            topic_samples = []
            for i in range(samples_per_topic):
                # 构造一个更具体的查询
                query = self._generate_topic_query(topic, i)
                
                # 获取知识
                response = self.bridge.ask_knowledge(
                    query=query,
                    topic=topic,
                    wait_response=True
                )
                
                if response:
                    topic_samples.append(response)
                    all_responses.append(response)
                    
                    # 如果是第一个样本，记录该主题的向量
                    if i == 0:
                        topic_vectors[topic] = response["response_vector"]
            
            logger.info(f"获取主题'{topic}'的知识样本: {len(topic_samples)}")
        
        # 如果没有获取到知识，退出
        if not all_responses:
            logger.error("未能从Claude获取任何知识")
            return False
        
        # 准备训练数据
        X = []
        y = []
        
        # 为每个主题创建标签的one-hot编码
        topic_to_id = {topic: i for i, topic in enumerate(topics)}
        
        for response in all_responses:
            vector = response["response_vector"]
            topic = response["topic"]
            
            X.append(vector)
            
            # 创建one-hot编码标签
            label = np.zeros(len(topics))
            label[topic_to_id[topic]] = 1
            y.append(label)
        
        X = np.array(X)
        y = np.array(y)
        
        # 训练模型
        return self.train(X, y, epochs=epochs)
    
    def _generate_topic_query(self, topic, index):
        """根据主题和索引生成查询"""
        query_templates = [
            f"请详细解释{topic}的基本概念和原理",
            f"请描述{topic}的核心特点和重要性",
            f"请提供关于{topic}的最新研究进展",
            f"请分析{topic}在实际应用中的挑战和解决方案",
            f"请总结{topic}的历史发展和未来趋势"
        ]
        
        # 如果模板不够，使用通用模板
        if index >= len(query_templates):
            return f"请提供关于{topic}的第{index+1}个知识点"
        
        return query_templates[index]
    
    def train(self, X, y, epochs=10, learning_rate=0.01, batch_size=None):
        """
        训练WeQ模型
        
        Args:
            X: 输入数据
            y: 标签
            epochs: 训练轮次
            learning_rate: 学习率
            batch_size: 批次大小
            
        Returns:
            训练历史
        """
        if batch_size is None:
            batch_size = self.model.batch_size
        
        start_time = time.time()
        
        # 记录训练前的性能
        initial_predictions = self.model.predict(X)
        initial_accuracy = np.mean(np.argmax(initial_predictions, axis=1) == np.argmax(y, axis=1))
        
        # 训练模型
        self.model.train(X, y, learning_rate=learning_rate, epochs=epochs, batch_size=batch_size)
        
        # 评估模型
        predictions = self.model.predict(X)
        accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
        
        # 记录训练历史
        training_record = {
            "timestamp": time.time(),
            "epochs": epochs,
            "samples": len(X),
            "topics": self.current_topics,
            "initial_accuracy": float(initial_accuracy),
            "final_accuracy": float(accuracy),
            "learning_rate": learning_rate,
            "training_time": time.time() - start_time
        }
        self.training_history.append(training_record)
        
        logger.info(f"训练完成: {len(X)}个样本, {epochs}轮, 准确率: {accuracy:.4f} (提升: {accuracy-initial_accuracy:.4f})")
        return training_record
    
    def save_model(self, output_dir="models", model_name=None):
        """
        保存WeQ模型
        
        Args:
            output_dir: 输出目录
            model_name: 模型名称
            
        Returns:
            保存的文件路径
        """
        os.makedirs(output_dir, exist_ok=True)
        
        if model_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = f"weq_model_{self.model.qubit_count}qubit_{timestamp}.json"
        
        model_path = os.path.join(output_dir, model_name)
        
        # 保存模型配置
        model_config = {
            "input_dim": self.model.input_dim,
            "hidden_dim": self.model.hidden_dim,
            "output_dim": self.model.output_dim,
            "qubit_count": self.model.qubit_count,
            "qubit_system": f"{self.model.qubit_count}-qubit",
            "training_history": self.training_history,
            "topics": self.current_topics,
            "timestamp": time.time()
        }
        
        with open(model_path, 'w', encoding='utf-8') as f:
            json.dump(model_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"模型已保存: {model_path}")
        return model_path
    
    def knowledge_guided_training(self, initial_topics=None, iterations=3, 
                                epochs_per_iteration=5, samples_per_topic=3,
                                learning_rate=0.005):
        """
        知识引导训练 - 循环从Claude获取知识并训练
        
        Args:
            initial_topics: 初始训练主题列表
            iterations: 迭代次数
            epochs_per_iteration: 每次迭代的训练轮次
            samples_per_topic: 每个主题的样本数
            learning_rate: 学习率
            
        Returns:
            训练历史记录
        """
        if not self.bridge:
            success = self.connect_to_claude()
            if not success:
                logger.error("无法连接到Claude API")
                return False
        
        # 使用默认主题或用户提供的主题
        topics = initial_topics or [
            "量子计算", "神经网络", "机器学习", "自然语言处理", "计算机视觉"
        ]
        
        all_training_records = []
        
        for iteration in range(iterations):
            logger.info(f"开始第{iteration+1}/{iterations}次知识引导训练")
            print(f"\n===== 第{iteration+1}/{iterations}次知识引导训练 =====")
            print(f"当前主题: {', '.join(topics)}")
            
            # 从Claude获取知识并训练
            training_record = self.train_from_claude_knowledge(
                topics=topics,
                samples_per_topic=samples_per_topic,
                epochs=epochs_per_iteration
            )
            
            if training_record:
                all_training_records.append(training_record)
                print(f"训练完成: {training_record['samples']}个样本, 准确率: {training_record['final_accuracy']:.4f}")
                
                # 保存中间模型
                self.save_model(model_name=f"weq_model_{self.model.qubit_count}qubit_iter{iteration+1}.json")
                
                # 收集反馈，以便Claude调整知识提供方式
                if self.bridge:
                    self.bridge.provide_feedback(
                        response_id=iteration,
                        metrics={
                            "relevance": min(0.5 + training_record['final_accuracy']/2, 0.95),
                            "comprehension": training_record['final_accuracy'],
                            "integration": training_record['final_accuracy'] - training_record['initial_accuracy']
                        }
                    )
                
                # 演化主题 - 根据当前主题生成相关主题
                if iteration < iterations - 1:
                    topics = self._evolve_topics(topics)
            else:
                logger.warning(f"第{iteration+1}次训练失败")
        
        # 保存最终模型
        self.save_model(model_name=f"weq_model_{self.model.qubit_count}qubit_final.json")
        
        return all_training_records
    
    def _evolve_topics(self, current_topics):
        """演化主题，生成新的相关主题"""
        if not self.bridge:
            return current_topics
        
        # 请求Claude为当前主题推荐相关主题
        topic_list = ", ".join(current_topics)
        query = f"我正在学习以下主题: {topic_list}。请推荐5个相关但更深入的主题，仅列出主题名称，用逗号分隔。"
        
        response = self.bridge.ask_claude(query)
        
        # 解析响应中的主题
        try:
            # 简单解析，假设Claude返回的是逗号分隔的主题列表
            topics_text = response.split(":")[-1].strip()
            new_topics = [t.strip() for t in topics_text.split(",")]
            
            # 过滤掉空主题
            new_topics = [t for t in new_topics if t]
            
            # 限制主题数量
            new_topics = new_topics[:5]
            
            if new_topics:
                logger.info(f"主题演化: {current_topics} -> {new_topics}")
                return new_topics
        except Exception as e:
            logger.error(f"解析主题失败: {str(e)}")
        
        return current_topics

def main():
    parser = argparse.ArgumentParser(description="WeQ量子基因神经网络训练器")
    parser.add_argument("--model", type=str, default=None, help="模型文件路径")
    parser.add_argument("--topics", type=str, default=None, help="训练主题，逗号分隔")
    parser.add_argument("--iterations", type=int, default=3, help="知识引导训练迭代次数")
    parser.add_argument("--epochs", type=int, default=5, help="每次迭代的训练轮次")
    parser.add_argument("--samples", type=int, default=3, help="每个主题的样本数")
    parser.add_argument("--learning_rate", type=float, default=0.005, help="学习率")
    args = parser.parse_args()
    
    # 初始化训练器
    trainer = WeQTrainer(model_path=args.model)
    
    # 连接到Claude
    trainer.connect_to_claude()
    
    # 处理训练主题
    topics = None
    if args.topics:
        topics = [t.strip() for t in args.topics.split(",")]
    
    # 开始知识引导训练
    training_records = trainer.knowledge_guided_training(
        initial_topics=topics,
        iterations=args.iterations,
        epochs_per_iteration=args.epochs,
        samples_per_topic=args.samples,
        learning_rate=args.learning_rate
    )
    
    if training_records:
        print("\n===== 训练完成 =====")
        for i, record in enumerate(training_records):
            print(f"迭代 {i+1}: {record['samples']}个样本, 准确率: {record['final_accuracy']:.4f}, 时间: {record['training_time']:.2f}秒")
    else:
        print("训练失败")

if __name__ == "__main__":
    main() 

"""
"""
量子基因编码: QE-WEQ-9BE8313D6C01
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
