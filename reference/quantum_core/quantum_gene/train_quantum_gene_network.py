"""
量子基因神经网络（QGNN，小趣）训练脚本
实现数据爬取、量子编码和模型训练的完整流程
"""

import os
import time
import logging
import json
import numpy as np
import cirq
from typing import List, Dict, Any
import threading
from queue import Queue
import argparse

# 导入自定义模块
from quantum_gene_network.quantum_crawler import CrawlerManager
from quantum_gene_network.quantum_encoder import MultimodalQuantumEncoder
from quantum_gene_network.quantum_gene_neural_implementation import QuantumGeneNeuralNetwork
from quantum_distributed import DistributedQuantumEngine, QuantumShard

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='qgnn_training.log'
)
logger = logging.getLogger(__name__)

class QGNNTrainer:
    """量子基因神经网络训练器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.crawler_manager = CrawlerManager()
        self.encoder = MultimodalQuantumEncoder()
        self.distributed_db = DistributedQuantumEngine()
        
        # 创建QGNN模型
        self.qgnn = QuantumGeneNeuralNetwork(
            input_dim=config.get('input_dim', 16),
            hidden_dims=config.get('hidden_dims', [32, 16]),
            output_dim=config.get('output_dim', 8),
            num_genes=config.get('num_genes', 100),
            gene_dimension=config.get('gene_dimension', 8),
            mutation_rate=config.get('mutation_rate', 0.01)
        )
        
        # 数据流水线
        self.data_queue = Queue(maxsize=100)
        self.encoded_queue = Queue(maxsize=100)
        self.is_running = False
        
        # 数据输出目录
        self.output_db_dir = "quantum_data/quantum_distributed_db"
        os.makedirs(self.output_db_dir, exist_ok=True)
        
    def setup_crawlers(self):
        """设置数据爬虫"""
        # 创建不同语言和领域的爬虫
        self.crawler_manager.create_crawler('chinese_general', 'chinese', ['news', 'social', 'technology'])
        self.crawler_manager.create_crawler('english_academic', 'english', ['academic', 'technology'])
        self.crawler_manager.create_crawler('yiwen_culture', 'yiwen', ['culture', 'yiwen'])
        
        # 准备种子URL
        self.seed_urls = {
            'chinese_general': [
                'https://www.sina.com.cn/',
                'https://www.sohu.com/',
                'https://www.163.com/'
            ],
            'english_academic': [
                'https://www.sciencedaily.com/',
                'https://www.nature.com/',
                'https://www.science.org/'
            ],
            'yiwen_culture': [
                'https://en.wikipedia.org/wiki/Yi_script',
                'https://zh.wikipedia.org/wiki/彝文',
                'https://baike.baidu.com/item/彝文/737'
            ]
        }
        
        logger.info("爬虫设置完成")
        
    def start_crawling(self):
        """启动爬虫"""
        self.crawler_manager.start_all(self.seed_urls, max_pages=self.config.get('max_pages_per_crawler', 50))
        self.crawler_manager.start_data_processor()
        logger.info("爬虫已启动")
        
    def start_pipeline(self):
        """启动数据流水线"""
        self.is_running = True
        
        # 启动爬虫收集线程
        crawler_thread = threading.Thread(target=self._collect_crawler_data)
        crawler_thread.daemon = True
        crawler_thread.start()
        
        # 启动编码线程
        encoder_thread = threading.Thread(target=self._encode_data)
        encoder_thread.daemon = True
        encoder_thread.start()
        
        # 启动存储线程
        storage_thread = threading.Thread(target=self._store_encoded_data)
        storage_thread.daemon = True
        storage_thread.start()
        
        logger.info("数据流水线已启动")
        
    def _collect_crawler_data(self):
        """收集爬虫数据"""
        while self.is_running:
            try:
                # 检查爬虫管理器中的数据
                processed_dir = 'processed_data'
                if os.path.exists(processed_dir):
                    for filename in os.listdir(processed_dir):
                        if filename.endswith('.jsonl'):
                            file_path = os.path.join(processed_dir, filename)
                            
                            # 读取文件并提取数据
                            with open(file_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    try:
                                        data_item = json.loads(line.strip())
                                        self.data_queue.put(data_item, timeout=1)
                                    except json.JSONDecodeError:
                                        continue
                            
                            # 处理完后移动文件
                            processed_path = os.path.join(processed_dir, 'processed', filename)
                            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
                            os.rename(file_path, processed_path)
                
                # 等待新数据
                time.sleep(5)
            except Exception as e:
                logger.error(f"收集爬虫数据出错: {str(e)}")
                time.sleep(5)
                
    def _encode_data(self):
        """编码数据为量子态"""
        while self.is_running:
            try:
                # 从数据队列获取数据
                data_item = self.data_queue.get(timeout=5)
                
                # 检测语言类型
                content = data_item.get('content', '')
                language = data_item.get('language', 'english')
                
                # 编码文本
                quantum_state = self.encoder.encode_text(content, language)
                
                # 将编码结果放入编码队列
                encoded_data = {
                    'original': data_item,
                    'quantum_state': quantum_state,
                    'language': language,
                    'timestamp': time.time()
                }
                
                self.encoded_queue.put(encoded_data, timeout=5)
                logger.info(f"已编码数据: 语言={language}, 哈希={data_item.get('hash', '')[:8]}")
                
                # 标记任务完成
                self.data_queue.task_done()
                
            except Queue.Empty:
                time.sleep(1)
            except Exception as e:
                logger.error(f"编码数据出错: {str(e)}")
                time.sleep(1)
                
    def _store_encoded_data(self):
        """存储编码后的数据"""
        while self.is_running:
            try:
                # 从编码队列获取数据
                encoded_data = self.encoded_queue.get(timeout=5)
                
                # 存储到分布式量子数据库
                quantum_state = encoded_data['quantum_state']
                language = encoded_data['language']
                original_data = encoded_data['original']
                
                # 使用量子分布式引擎存储
                shard_id = self.distributed_db.store_data(original_data)
                
                if shard_id:
                    # 同时保存到本地文件
                    self._save_to_local_db(shard_id, encoded_data)
                    logger.info(f"已存储量子数据: 分片ID={shard_id}, 语言={language}")
                    
                # 标记任务完成
                self.encoded_queue.task_done()
                
            except Queue.Empty:
                time.sleep(1)
            except Exception as e:
                logger.error(f"存储编码数据出错: {str(e)}")
                time.sleep(1)
                
    def _save_to_local_db(self, shard_id: str, encoded_data: Dict):
        """将数据保存到本地量子分布式数据库"""
        language = encoded_data['language']
        timestamp = encoded_data['timestamp']
        
        # 创建语言对应的目录
        lang_dir = os.path.join(self.output_db_dir, language)
        os.makedirs(lang_dir, exist_ok=True)
        
        # 保存元数据
        metadata = {
            'shard_id': shard_id,
            'language': language,
            'timestamp': timestamp,
            'content_hash': encoded_data['original'].get('hash', ''),
            'url': encoded_data['original'].get('url', ''),
        }
        
        # 保存到文件
        file_path = os.path.join(lang_dir, f"{shard_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
    def prepare_training_data(self):
        """准备训练数据"""
        # 从量子分布式数据库加载数据
        training_data = []
        
        # 遍历本地数据库文件
        for lang_dir in os.listdir(self.output_db_dir):
            lang_path = os.path.join(self.output_db_dir, lang_dir)
            if os.path.isdir(lang_path):
                for filename in os.listdir(lang_path):
                    if filename.endswith('.json'):
                        file_path = os.path.join(lang_path, filename)
                        
                        # 读取元数据
                        with open(file_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            
                        # 从分布式数据库检索完整数据
                        shard_id = metadata.get('shard_id')
                        if shard_id:
                            data = self.distributed_db.retrieve_data(shard_id)
                            if data:
                                # 重新编码为适合训练的格式
                                content = data.get('content', '')
                                language = data.get('language', 'english')
                                
                                # 编码为向量
                                encoded_vector = self._prepare_training_vector(content, language)
                                if encoded_vector is not None:
                                    training_data.append(encoded_vector)
        
        # 转换为numpy数组
        if training_data:
            X = np.array([item['features'] for item in training_data])
            y = np.array([item['label'] for item in training_data])
            return X, y
        else:
            logger.warning("没有找到训练数据")
            return None, None
            
    def _prepare_training_vector(self, content: str, language: str):
        """将内容准备为训练向量"""
        try:
            # 将量子态转换为适合训练的特征向量
            quantum_state = self.encoder.encode_text(content, language)
            
            # 简化：使用量子态的绝对值平方作为特征
            features = np.abs(quantum_state)**2
            
            # 降维到固定大小
            if len(features) > self.config.get('input_dim', 16):
                features = features[:self.config.get('input_dim', 16)]
            else:
                features = np.pad(features, (0, self.config.get('input_dim', 16) - len(features)))
                
            # 简化：根据语言创建标签
            if language == 'chinese':
                label = np.array([1, 0, 0])
            elif language == 'english':
                label = np.array([0, 1, 0])
            elif language == 'yiwen':
                label = np.array([0, 0, 1])
            else:
                label = np.array([0.33, 0.33, 0.33])
                
            return {
                'features': features,
                'label': label
            }
        except Exception as e:
            logger.error(f"准备训练向量失败: {str(e)}")
            return None
            
    def train_model(self, X=None, y=None, epochs=100):
        """训练量子基因神经网络模型"""
        if X is None or y is None:
            # 如果没有提供数据，尝试准备
            X, y = self.prepare_training_data()
            
        if X is None or y is None or len(X) == 0:
            logger.error("没有可用的训练数据")
            return False
            
        logger.info(f"开始训练模型，数据量: {len(X)}")
        
        # 启动量子基因进化
        self.qgnn.start_evolution()
        
        # 训练模型
        self.qgnn.train(X, y, learning_rate=self.config.get('learning_rate', 0.01), epochs=epochs)
        
        logger.info("模型训练完成")
        return True
        
    def save_model(self, filepath='models/qgnn_model.json'):
        """保存模型"""
        # 创建目录
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 简化：保存模型配置
        model_config = {
            'input_dim': self.qgnn.input_dim,
            'hidden_dims': self.qgnn.hidden_dims,
            'output_dim': self.qgnn.output_dim,
            'num_genes': self.qgnn.gene_layer.num_genes,
            'gene_dimension': self.qgnn.gene_layer.gene_dimension,
            'timestamp': time.time()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(model_config, f, ensure_ascii=False, indent=2)
            
        logger.info(f"模型已保存到: {filepath}")
        
    def stop(self):
        """停止训练器"""
        self.is_running = False
        self.crawler_manager.stop_all()
        self.distributed_db.stop()
        logger.info("训练器已停止")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='量子基因神经网络训练器')
    parser.add_argument('--input_dim', type=int, default=16, help='输入维度')
    parser.add_argument('--max_pages', type=int, default=20, help='每个爬虫的最大页面数')
    parser.add_argument('--epochs', type=int, default=50, help='训练轮次')
    parser.add_argument('--crawl_only', action='store_true', help='仅执行爬虫')
    args = parser.parse_args()
    
    # 准备配置
    config = {
        'input_dim': args.input_dim,
        'hidden_dims': [32, 16],
        'output_dim': 3,  # 三种语言
        'num_genes': 100,
        'gene_dimension': 8,
        'mutation_rate': 0.01,
        'max_pages_per_crawler': args.max_pages,
        'learning_rate': 0.01
    }
    
    # 创建训练器
    trainer = QGNNTrainer(config)
    
    try:
        # 设置爬虫
        trainer.setup_crawlers()
        
        # 启动爬虫和数据流水线
        trainer.start_crawling()
        trainer.start_pipeline()
        
        if not args.crawl_only:
            # 等待数据收集
            print("正在收集和处理数据，请等待...")
            time.sleep(30)  # 给爬虫一些时间收集数据
            
            # 训练模型
            print("开始训练模型...")
            trainer.train_model(epochs=args.epochs)
            
            # 保存模型
            trainer.save_model()
        else:
            print("仅执行爬虫模式，按Ctrl+C停止...")
            while True:
                time.sleep(10)
                
    except KeyboardInterrupt:
        print("收到中断信号，正在停止...")
    finally:
        # 停止训练器
        trainer.stop()
        print("训练器已停止")

if __name__ == "__main__":
    main() 

"""
"""
量子基因编码: QE-TRA-F07B1C4CC5CA
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
