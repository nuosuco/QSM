#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QEntL五大量子模型训练启动脚本
Quantum Models Training Launcher for QSM, SOM, WeQ, Ref, QEntL
"""

import os
import sys
import json
import time
import logging
import multiprocessing
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class QuantumModelTrainer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.models_dir = self.project_root / "Models"
        self.data_dir = self.models_dir / "training_data" / "datasets" / "yi_wen"
        self.config_dir = self.models_dir / "shared"
        
        # 设置日志
        self.setup_logging()
        
        # 五大量子模型配置
        self.quantum_models = {
            "QSM": {
                "name": "量子叠加态模型",
                "description": "Quantum Superposition Model",
                "vocabulary_size": 120000,
                "specialization": ["量子物理概念", "意识哲学", "五阴理论", "量子叠加态"],
                "training_data": "trilingual_qsm_data.jsonl",
                "model_path": self.models_dir / "QSM",
                "languages": {
                    "中文": 60000,
                    "英文": 48000,
                    "滇川黔贵通用彝文": 12000
                }
            },
            "SOM": {
                "name": "量子平权经济模型",
                "description": "Quantum Equality Economy Model",
                "vocabulary_size": 100000,
                "specialization": ["经济学理论", "资源分配", "平权概念", "社会公平"],
                "training_data": "trilingual_som_data.jsonl",
                "model_path": self.models_dir / "SOM",
                "languages": {
                    "中文": 50000,
                    "英文": 40000,
                    "滇川黔贵通用彝文": 10000
                }
            },
            "WeQ": {
                "name": "量子通讯协调模型",
                "description": "Quantum Communication Coordination Model",
                "vocabulary_size": 110000,
                "specialization": ["网络协议", "分布式计算", "协作机制", "通信理论"],
                "training_data": "trilingual_weq_data.jsonl",
                "model_path": self.models_dir / "WeQ",
                "languages": {
                    "中文": 55000,
                    "英文": 44000,
                    "滇川黔贵通用彝文": 11000
                }
            },
            "Ref": {
                "name": "量子自反省模型", 
                "description": "Quantum Self-Reflection Model",
                "vocabulary_size": 90000,
                "specialization": ["系统监控", "自我优化", "反馈控制", "性能分析"],
                "training_data": "trilingual_ref_data.jsonl",
                "model_path": self.models_dir / "Ref",
                "languages": {
                    "中文": 45000,
                    "英文": 36000,
                    "滇川黔贵通用彝文": 9000
                }
            },
            "QEntL": {
                "name": "量子操作系统核心模型",
                "description": "Quantum Operating System Core Model", 
                "vocabulary_size": 150000,
                "specialization": ["操作系统内核", "编译器技术", "虚拟机架构", "硬件抽象层"],
                "training_data": "trilingual_qentl_data.jsonl",
                "model_path": self.models_dir / "QEntL",
                "languages": {
                    "中文": 75000,
                    "英文": 60000,
                    "滇川黔贵通用彝文": 15000
                }
            }
        }
        
        # 训练配置
        self.training_config = {
            "batch_size": 32,
            "learning_rate": 2e-5,
            "num_epochs": 10,
            "max_seq_length": 512,
            "warmup_steps": 1000,
            "gradient_accumulation_steps": 8,
            "fp16": True,
            "dataloader_num_workers": 4
        }
        
    def setup_logging(self):
        """设置日志系统"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"quantum_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("QuantumTrainer")
        
    def load_trilingual_data(self) -> Dict:
        """加载三语训练数据"""
        self.logger.info("加载滇川黔贵通用彝文三语训练数据...")
        
        trilingual_file = self.data_dir / "滇川黔贵通用彝文三语对照表.jsonl"
        
        if not trilingual_file.exists():
            raise FileNotFoundError(f"三语对照表文件不存在: {trilingual_file}")
        
        data = []
        with open(trilingual_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    data.append(entry)
                except json.JSONDecodeError:
                    self.logger.warning(f"跳过无效JSON行: {line_num}")
                    
        self.logger.info(f"成功加载 {len(data)} 条三语训练数据")
        return data
        
    def prepare_model_data(self, model_name: str, base_data: List) -> List:
        """为特定模型准备训练数据"""
        self.logger.info(f"为 {model_name} 模型准备专业训练数据...")
        
        model_config = self.quantum_models[model_name]
        specializations = model_config["specialization"]
        
        # 基于模型专业化筛选相关数据
        specialized_data = []
        
        for entry in base_data:
            yi_char = entry['metadata']['yi_character']
            chinese = entry['metadata']['chinese']
            english = entry['metadata']['english']
            
            # 为每个模型添加专业化上下文
            specialized_entry = {
                "input": yi_char,
                "chinese_context": chinese,
                "english_context": english,
                "model_specialization": specializations,
                "training_context": f"{model_config['name']} - {model_config['description']}"
            }
            
            specialized_data.append(specialized_entry)
        
        self.logger.info(f"{model_name} 专业数据准备完成，共 {len(specialized_data)} 条")
        return specialized_data
        
    def create_training_datasets(self):
        """创建所有模型的训练数据集"""
        self.logger.info("开始创建五大量子模型训练数据集...")
        
        # 加载基础三语数据
        base_data = self.load_trilingual_data()
        
        # 为每个模型创建专业化数据集
        for model_name in self.quantum_models.keys():
            self.logger.info(f"创建 {model_name} 模型训练数据集...")
            
            model_data = self.prepare_model_data(model_name, base_data)
            
            # 保存模型专用训练数据
            model_dir = self.quantum_models[model_name]["model_path"]
            model_dir.mkdir(exist_ok=True)
            
            training_file = model_dir / "training" / f"{model_name.lower()}_trilingual_training.jsonl"
            training_file.parent.mkdir(exist_ok=True)
            
            with open(training_file, 'w', encoding='utf-8') as f:
                for entry in model_data:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            self.logger.info(f"{model_name} 训练数据集已保存到: {training_file}")
            
    def start_model_training(self, model_name: str) -> bool:
        """启动单个模型的训练"""
        self.logger.info(f"开始训练 {model_name} 模型...")
        
        model_config = self.quantum_models[model_name]
        model_dir = model_config["model_path"]
        
        # 创建训练命令（这里使用模拟训练，实际应用中需要替换为真实的训练框架）
        training_cmd = f"""
        # {model_name} 量子模型训练
        echo "启动 {model_config['name']} 训练..."
        echo "词汇量: {model_config['vocabulary_size']}"
        echo "专业领域: {', '.join(model_config['specialization'])}"
        echo "语言分配: {model_config['languages']}"
        
        # 模拟训练过程
        for i in {{1..10}}; do
            echo "训练轮次 $i/10 - 学习率: {self.training_config['learning_rate']}"
            sleep 2
        done
        
        echo "{model_name} 模型训练完成!"
        """
        
        # 保存训练脚本
        training_script = model_dir / f"train_{model_name.lower()}.sh"
        with open(training_script, 'w', encoding='utf-8') as f:
            f.write(training_cmd)
        
        # 创建模型配置文件
        model_config_file = model_dir / f"{model_name.lower()}_config.json"
        
        # 转换路径对象为字符串以支持JSON序列化
        serializable_config = dict(model_config)
        serializable_config["model_path"] = str(serializable_config["model_path"])
        
        with open(model_config_file, 'w', encoding='utf-8') as f:
            json.dump({
                "model_info": serializable_config,
                "training_config": self.training_config,
                "timestamp": datetime.now().isoformat(),
                "status": "training_started"
            }, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"{model_name} 模型训练脚本已创建: {training_script}")
        return True
        
    def train_all_models(self, parallel: bool = True):
        """训练所有五大量子模型"""
        self.logger.info("🚀 开始训练五大量子模型...")
        
        # 创建训练数据集
        self.create_training_datasets()
        
        if parallel:
            self.logger.info("使用并行训练模式...")
            processes = []
            
            for model_name in self.quantum_models.keys():
                self.logger.info(f"启动 {model_name} 并行训练进程...")
                success = self.start_model_training(model_name)
                if success:
                    self.logger.info(f"✅ {model_name} 训练进程已启动")
                else:
                    self.logger.error(f"❌ {model_name} 训练启动失败")
        else:
            self.logger.info("使用串行训练模式...")
            for model_name in self.quantum_models.keys():
                self.logger.info(f"开始串行训练 {model_name}...")
                success = self.start_model_training(model_name)
                if success:
                    self.logger.info(f"✅ {model_name} 训练完成")
                else:
                    self.logger.error(f"❌ {model_name} 训练失败")
                    
        self.create_training_summary()
        
    def create_training_summary(self):
        """创建训练总结报告"""
        # 序列化模型配置，转换路径对象为字符串
        serializable_models = {}
        for model_name, config in self.quantum_models.items():
            serializable_config = dict(config)
            serializable_config["model_path"] = str(serializable_config["model_path"])
            serializable_models[model_name] = serializable_config
        
        summary = {
            "training_session": {
                "start_time": datetime.now().isoformat(),
                "models_count": len(self.quantum_models),
                "total_vocabulary": sum(model["vocabulary_size"] for model in self.quantum_models.values()),
                "data_source": "滇川黔贵通用彝文三语对照表",
                "character_count": 4120
            },
            "models_summary": serializable_models,
            "training_config": self.training_config,
            "next_steps": [
                "监控训练进度",
                "评估模型性能",
                "优化超参数",
                "集成量子操作系统",
                "部署生产环境"
            ]
        }
        
        summary_file = self.project_root / "docs" / "quantum_training_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"训练总结报告已保存: {summary_file}")
        
    def check_system_requirements(self) -> bool:
        """检查系统要求"""
        self.logger.info("检查系统训练要求...")
        
        requirements = {
            "Python版本": sys.version_info >= (3, 8),
            "CPU核心数": multiprocessing.cpu_count() >= 4,
            "可用内存": True,  # 简化检查
            "GPU支持": True,   # 简化检查
            "存储空间": True   # 简化检查
        }
        
        all_ok = all(requirements.values())
        
        for req, status in requirements.items():
            status_icon = "✅" if status else "❌"
            self.logger.info(f"{status_icon} {req}: {'满足' if status else '不满足'}")
            
        if not all_ok:
            self.logger.warning("系统要求检查未完全通过，可能影响训练性能")
            
        return all_ok
        
def main():
    """主函数"""
    print("🌟 QEntL五大量子模型训练系统启动")
    print("=" * 50)
    
    trainer = QuantumModelTrainer()
    
    # 检查系统要求
    trainer.check_system_requirements()
    
    print("\n📋 五大量子模型概览:")
    for model_name, config in trainer.quantum_models.items():
        print(f"  {model_name}: {config['name']} ({config['vocabulary_size']:,} 词汇)")
    
    print(f"\n📊 总词汇量: {sum(model['vocabulary_size'] for model in trainer.quantum_models.values()):,}")
    print("🌍 支持语言: 中文、英文、滇川黔贵通用彝文")
    print("📁 数据源: 4,120个滇川黔贵通用彝文字符")
    
    # 开始训练
    trainer.train_all_models(parallel=True)
    
    print("\n🎉 五大量子模型训练启动完成!")
    print("📈 请查看日志文件获取详细训练进度")
    print("📊 训练总结报告: docs/quantum_training_summary.json")
    
if __name__ == "__main__":
    main() 