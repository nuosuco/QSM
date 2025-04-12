#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SOM训练服务 - 自组织映射模型训练服务
此脚本提供SOM模型的训练功能，包括参数配置、模型训练、保存和评估
"""

import os
import sys
import json
import time
import logging
import datetime
import traceback
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# 添加项目根目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.dirname(script_dir)
scripts_dir = os.path.dirname(services_dir)
som_dir = os.path.dirname(scripts_dir)
project_root = os.path.dirname(som_dir)
sys.path.insert(0, project_root)

# 创建日志目录
log_dir = os.path.join(project_root, ".logs")
os.makedirs(log_dir, exist_ok=True)

# 配置日志
def setup_logging(log_level=logging.INFO):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"som_train_{timestamp}.log")
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("SOM_Train")

logger = setup_logging()

try:
    # 导入NumPy和科学计算库
    import numpy as np
    from sklearn.preprocessing import MinMaxScaler
    import matplotlib.pyplot as plt
    import pandas as pd
except ImportError as e:
    logger.error(f"无法导入必要的科学计算库: {e}")
    logger.error("请安装必要的依赖: pip install numpy scikit-learn matplotlib pandas")
    sys.exit(1)

try:
    # 导入SOM模型相关模块
    from SOM.som_core import SOMModel
    from SOM.som_utils import load_data, preprocess_data, evaluate_model
except ImportError as e:
    logger.error(f"无法导入SOM模块: {e}")
    sys.exit(1)

class SOMTrainingService:
    """SOM训练服务类，提供SOM模型的训练、评估和保存功能"""
    
    def __init__(self):
        """初始化SOM训练服务"""
        # 设置模型目录
        self.model_dir = os.path.join(som_dir, "models")
        os.makedirs(self.model_dir, exist_ok=True)
        
        # 设置数据目录
        self.data_dir = os.path.join(som_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 设置输出目录
        self.output_dir = os.path.join(som_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 默认训练配置
        self.default_config = {
            "map_size": (10, 10),           # SOM网格大小
            "input_dim": None,              # 输入维度，将根据数据自动设置
            "learning_rate": 0.1,           # 学习率
            "sigma": None,                  # 邻域半径，None表示自动计算
            "decay_function": "exponential", # 衰减函数: exponential或linear
            "neighborhood_function": "gaussian", # 邻域函数: gaussian或bubble
            "random_seed": 42,              # 随机种子
            "n_iterations": 1000,           # 迭代次数 
            "n_jobs": 1                     # 并行作业数
        }
        
        # SOM模型实例
        self.model = None
        
        # 预处理器
        self.scaler = MinMaxScaler()
        
        logger.info("SOM训练服务初始化完成")
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载训练配置"""
        # 如果没有提供配置文件路径，使用默认配置
        if not config_path:
            logger.info("使用默认训练配置")
            return self.default_config.copy()
        
        # 加载自定义配置
        logger.info(f"从文件加载训练配置: {config_path}")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 合并默认配置和自定义配置
            merged_config = self.default_config.copy()
            merged_config.update(config)
            logger.info(f"成功加载配置: {merged_config}")
            return merged_config
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            logger.warning("使用默认配置")
            return self.default_config.copy()
    
    def load_data(self, data_path: str) -> np.ndarray:
        """加载并预处理训练数据"""
        logger.info(f"加载训练数据: {data_path}")
        
        try:
            data = load_data(data_path)
            logger.info(f"成功加载数据，形状: {data.shape if hasattr(data, 'shape') else '未知'}")
            return data
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def preprocess_data(self, data: np.ndarray) -> np.ndarray:
        """对数据进行预处理"""
        logger.info("对数据进行预处理")
        
        try:
            # 将数据转换为NumPy数组
            if not isinstance(data, np.ndarray):
                data = np.array(data)
            
            # 应用预处理
            processed_data = preprocess_data(data)
            
            # 应用归一化处理
            normalized_data = self.scaler.fit_transform(processed_data)
            
            logger.info(f"预处理完成，数据形状: {normalized_data.shape}")
            return normalized_data
        except Exception as e:
            logger.error(f"数据预处理失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def initialize_model(self, config: Dict[str, Any], input_dim: int) -> bool:
        """初始化SOM模型"""
        logger.info("初始化SOM模型")
        
        try:
            # 更新输入维度
            config['input_dim'] = input_dim
            
            # 创建模型
            self.model = SOMModel(
                map_size=config['map_size'],
                input_dim=config['input_dim'],
                learning_rate=config['learning_rate'],
                sigma=config['sigma'],
                decay_function=config['decay_function'],
                neighborhood_function=config['neighborhood_function'],
                random_seed=config['random_seed']
            )
            
            logger.info(f"SOM模型初始化成功，配置: {config}")
            return True
        except Exception as e:
            logger.error(f"SOM模型初始化失败: {str(e)}")
            logger.error(traceback.format_exc())
            self.model = None
            return False
    
    def train_model(self, data: np.ndarray, config: Dict[str, Any]) -> Dict[str, Any]:
        """训练SOM模型"""
        if self.model is None:
            logger.error("模型尚未初始化，无法进行训练")
            return None
        
        try:
            # 开始计时
            start_time = time.time()
            logger.info(f"开始训练SOM模型，迭代次数: {config['n_iterations']}")
            
            # 记录训练开始时间
            training_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 训练模型
            train_result = self.model.train(
                data,
                n_iterations=config['n_iterations'],
                n_jobs=config['n_jobs']
            )
            
            # 计算训练时间
            training_time = time.time() - start_time
            
            # 构建训练结果
            result = {
                "train_result": train_result,
                "training_time": training_time,
                "training_start": training_start,
                "training_end": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "config": config
            }
            
            logger.info(f"SOM模型训练完成，用时: {training_time:.2f}秒")
            return result
        except Exception as e:
            logger.error(f"SOM模型训练失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def evaluate_model(self, data: np.ndarray) -> Dict[str, Any]:
        """评估模型性能"""
        if self.model is None:
            logger.error("模型尚未初始化，无法进行评估")
            return None
        
        try:
            logger.info("开始评估SOM模型")
            
            # 计算定量评估指标
            evaluation_results = evaluate_model(self.model, data)
            
            logger.info("SOM模型评估完成")
            return evaluation_results
        except Exception as e:
            logger.error(f"SOM模型评估失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def save_model(self, output_path: Optional[str] = None) -> str:
        """保存训练好的模型"""
        if self.model is None:
            logger.error("模型尚未初始化，无法保存")
            return None
        
        try:
            # 如果未指定输出路径，则生成带时间戳的文件名
            if not output_path:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(self.model_dir, f"som_model_{timestamp}.pkl")
            
            # 保存模型
            logger.info(f"保存SOM模型到: {output_path}")
            self.model.save(output_path)
            
            # 保存缩放器
            scaler_path = output_path.replace('.pkl', '_scaler.pkl')
            self.model.save_scaler(self.scaler, scaler_path)
            
            logger.info(f"SOM模型保存成功")
            return output_path
        except Exception as e:
            logger.error(f"SOM模型保存失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def visualize_model(self, data: Optional[np.ndarray] = None, output_path: Optional[str] = None) -> bool:
        """可视化模型"""
        if self.model is None:
            logger.error("模型尚未初始化，无法可视化")
            return False
        
        try:
            # 如果未指定输出路径，则生成带时间戳的文件名
            if not output_path:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = os.path.join(self.output_dir, f"visualization_{timestamp}")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "som")
            
            # 创建可视化输出目录
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 可视化U-matrix
            logger.info("生成U-matrix可视化")
            u_matrix_path = f"{output_path}_u_matrix.png"
            self.model.plot_u_matrix(filename=u_matrix_path)
            
            # 可视化组件平面
            logger.info("生成组件平面可视化")
            component_planes_path = f"{output_path}_component_planes.png"
            self.model.plot_component_planes(filename=component_planes_path)
            
            # 如果提供了数据，可视化数据在SOM上的映射
            if data is not None:
                logger.info("生成数据映射可视化")
                data_map_path = f"{output_path}_data_map.png"
                self.model.plot_data_map(data, filename=data_map_path)
            
            logger.info(f"SOM模型可视化完成，输出保存到: {os.path.dirname(output_path)}")
            return True
        except Exception as e:
            logger.error(f"SOM模型可视化失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def run_training_pipeline(self, data_path: str, config_path: Optional[str] = None, 
                             output_path: Optional[str] = None, visualize: bool = True) -> Dict[str, Any]:
        """运行完整的训练流程"""
        logger.info("开始SOM模型训练流程")
        result = {
            "success": False,
            "model_path": None,
            "evaluation": None,
            "visualizations": [],
            "error": None
        }
        
        try:
            # 加载配置
            config = self.load_config(config_path)
            if not config:
                result["error"] = "配置加载失败"
                return result
            
            # 加载数据
            raw_data = self.load_data(data_path)
            if raw_data is None:
                result["error"] = "数据加载失败"
                return result
            
            # 预处理数据
            processed_data = self.preprocess_data(raw_data)
            if processed_data is None:
                result["error"] = "数据预处理失败"
                return result
            
            # 初始化模型
            if not self.initialize_model(config, processed_data.shape[1]):
                result["error"] = "模型初始化失败"
                return result
            
            # 训练模型
            training_result = self.train_model(processed_data, config)
            if training_result is None:
                result["error"] = "模型训练失败"
                return result
            
            # 评估模型
            evaluation = self.evaluate_model(processed_data)
            result["evaluation"] = evaluation
            
            # 保存模型
            model_path = self.save_model(output_path)
            if model_path:
                result["model_path"] = model_path
            else:
                result["error"] = "模型保存失败"
                return result
            
            # 可视化模型
            if visualize:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                vis_output_path = os.path.join(self.output_dir, f"visualization_{timestamp}/som")
                if self.visualize_model(processed_data, vis_output_path):
                    result["visualizations"] = [
                        f"{vis_output_path}_u_matrix.png",
                        f"{vis_output_path}_component_planes.png",
                        f"{vis_output_path}_data_map.png"
                    ]
            
            # 标记成功
            result["success"] = True
            logger.info("SOM模型训练流程完成")
            
        except Exception as e:
            error_msg = f"训练流程出错: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            result["error"] = error_msg
        
        return result

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="SOM模型训练服务")
    parser.add_argument("--data", type=str, required=True, help="训练数据文件路径")
    parser.add_argument("--config", type=str, help="训练配置文件路径")
    parser.add_argument("--output", type=str, help="模型输出路径")
    parser.add_argument("--no-visualize", action="store_true", help="不生成可视化")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # 创建训练服务
    training_service = SOMTrainingService()
    
    # 运行训练流程
    result = training_service.run_training_pipeline(
        data_path=args.data,
        config_path=args.config,
        output_path=args.output,
        visualize=not args.no_visualize
    )
    
    # 输出结果
    if result["success"]:
        logger.info(f"训练成功！模型保存在: {result['model_path']}")
        if result["evaluation"]:
            logger.info(f"模型评估结果: {result['evaluation']}")
        if result["visualizations"]:
            logger.info(f"模型可视化已保存到: {', '.join(result['visualizations'])}")
    else:
        logger.error(f"训练失败: {result['error']}")

if __name__ == "__main__":
    logger.info("==== SOM训练服务启动 ====")
    main()
    logger.info("==== SOM训练服务结束 ====")

# 量子基因编码: QE-TRN-S0O4M2
# 纠缠状态: 活跃
# 纠缠对象: ['SOM/som_core.py', 'SOM/som_utils.py', 'SOM/scripts/services/SOM_inference.py']
# 纠缠强度: 0.98

# 开发团队：中华 ZhoHo ，Claude 