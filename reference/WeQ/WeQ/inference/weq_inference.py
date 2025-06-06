#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WeQ推理服务 - 量子神经网络推理服务
此脚本提供WeQ量子神经网络模型的推理功能
"""

import os
import sys
import json
import time
import logging
import argparse
import datetime
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# 添加项目根目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.dirname(script_dir)
scripts_dir = os.path.dirname(services_dir)
weq_dir = os.path.dirname(scripts_dir)
project_root = os.path.dirname(weq_dir)
sys.path.insert(0, project_root)

# 导入WeQ模型相关模块
try:
    from WeQ.weq_core import WeQModel
    from WeQ.weq_utils import load_data, preprocess_data, visualize_circuit
except ImportError as e:
    print(f"错误: 无法导入WeQ模块 - {e}")
    sys.exit(1)

# 创建日志目录
log_dir = os.path.join(project_root, ".logs")
os.makedirs(log_dir, exist_ok=True)

# 配置日志
def setup_logging(log_level=logging.INFO):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"weq_inference_{timestamp}.log")
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("WeQ_INFERENCE")

logger = setup_logging()

try:
    # 导入NumPy和科学计算库
    import numpy as np
    from sklearn.preprocessing import StandardScaler
    import matplotlib.pyplot as plt
except ImportError as e:
    logger.error(f"无法导入必要的科学计算库: {e}")
    logger.error("请安装必要的依赖: pip install numpy scikit-learn matplotlib")
    sys.exit(1)

try:
    # 导入量子计算库
    import cirq
except ImportError as e:
    logger.error(f"无法导入量子计算库Cirq: {e}")
    logger.error("请安装量子计算依赖: pip install cirq")
    sys.exit(1)

class WeQInferenceService:
    """WeQ量子神经网络模型推理服务类"""
    
    def __init__(self):
        self.model = None
        self.model_dir = os.path.join(weq_dir, "models")
        self.output_dir = os.path.join(weq_dir, "outputs")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 标准化处理器
        self.scaler = StandardScaler()
        self.is_scaler_fitted = False
        
        logger.info("WeQ推理服务初始化完成")
        
    def load_model(self, model_path=None):
        """加载模型"""
        if model_path is None:
            # 使用最新的模型
            model_files = [f for f in os.listdir(self.model_dir) if f.endswith('.weq')]
            if not model_files:
                logger.error("没有找到可用的模型文件")
                return False
            
            # 按时间排序，选择最新的模型
            model_path = os.path.join(self.model_dir, sorted(model_files)[-1])
        
        try:
            logger.info(f"从 {model_path} 加载模型...")
            self.model = WeQModel.load(model_path)
            logger.info(f"模型加载成功: {model_path}")
            return True
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def preprocess_input(self, data):
        """预处理输入数据"""
        try:
            # 转换为NumPy数组
            if not isinstance(data, np.ndarray):
                data = np.array(data).reshape(1, -1) if np.isscalar(data) else np.array(data)
            
            # 应用预处理
            processed_data = preprocess_data(data)
            
            # 如果标准化器尚未拟合，且模型有预训练的标准化器，则使用模型的标准化器
            if hasattr(self.model, 'scaler') and self.model.scaler is not None:
                normalized_data = self.model.scaler.transform(processed_data)
                logger.debug("使用模型预训练的标准化器")
            else:
                # 否则使用服务自带的标准化器
                if not self.is_scaler_fitted:
                    normalized_data = self.scaler.fit_transform(processed_data)
                    self.is_scaler_fitted = True
                    logger.debug("标准化器已拟合")
                else:
                    normalized_data = self.scaler.transform(processed_data)
            
            return normalized_data
        except Exception as e:
            logger.error(f"数据预处理失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def predict(self, data, raw_output=False):
        """单一数据推理"""
        if self.model is None:
            logger.error("模型未加载，无法进行推理")
            return None
        
        try:
            # 预处理数据
            processed_data = self.preprocess_input([data])[0]
            
            # 进行推理
            start_time = time.time()
            prediction = self.model.predict(processed_data)
            inference_time = time.time() - start_time
            
            logger.info(f"推理完成: 预测结果={prediction}, 耗时={inference_time:.4f}秒")
            
            if raw_output:
                return prediction
            
            # 构建结果
            result = {
                "prediction": prediction.tolist() if hasattr(prediction, "tolist") else prediction,
                "inference_time": inference_time
            }
            
            # 如果模型输出分类结果，添加类别信息
            if hasattr(self.model, 'get_class_names') and callable(getattr(self.model, 'get_class_names')):
                class_names = self.model.get_class_names()
                if class_names:
                    # 获取最可能的类别
                    if isinstance(prediction, np.ndarray) and prediction.size > 1:
                        class_idx = np.argmax(prediction)
                        class_name = class_names[class_idx] if class_idx < len(class_names) else "未知"
                        confidence = prediction[class_idx]
                        result["class"] = class_name
                        result["confidence"] = float(confidence) if hasattr(confidence, "item") else confidence
                    else:
                        # 二分类情况
                        class_idx = 1 if prediction > 0.5 else 0
                        class_name = class_names[class_idx] if class_idx < len(class_names) else "未知"
                        result["class"] = class_name
                        result["confidence"] = float(prediction) if prediction > 0.5 else float(1 - prediction)
            
            return result
            
        except Exception as e:
            logger.error(f"推理过程中出错: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def batch_predict(self, data_list):
        """批量数据推理"""
        if self.model is None:
            logger.error("模型未加载，无法进行推理")
            return None
        
        try:
            # 预处理数据
            processed_data = self.preprocess_input(data_list)
            
            # 批量推理
            start_time = time.time()
            predictions = []
            
            # 根据模型的批处理能力选择处理方式
            if hasattr(self.model, 'batch_predict') and callable(getattr(self.model, 'batch_predict')):
                # 如果模型支持批处理
                predictions = self.model.batch_predict(processed_data)
                logger.info("使用模型的批处理功能")
            else:
                # 否则逐条处理
                for i, data in enumerate(processed_data):
                    prediction = self.model.predict(data)
                    predictions.append(prediction)
                    
                    if i % 100 == 0 and i > 0:
                        logger.info(f"已完成 {i}/{len(processed_data)} 个样本的推理")
            
            batch_time = time.time() - start_time
            
            # 转换结果为列表
            if isinstance(predictions, np.ndarray):
                predictions_list = predictions.tolist()
            else:
                predictions_list = [p.tolist() if hasattr(p, "tolist") else p for p in predictions]
            
            # 构建结果
            results = {
                "predictions": predictions_list,
                "count": len(predictions),
                "batch_time": batch_time,
                "avg_time_per_sample": batch_time / len(processed_data) if processed_data.size else 0
            }
            
            logger.info(f"批量推理完成: {len(predictions)}个样本, 总耗时={batch_time:.4f}秒, "
                      f"平均每样本耗时={results['avg_time_per_sample']:.4f}秒")
            
            return results
            
        except Exception as e:
            logger.error(f"批量推理过程中出错: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def get_quantum_state(self, data):
        """获取输入数据对应的量子态"""
        if self.model is None:
            logger.error("模型未加载，无法获取量子态")
            return None
        
        try:
            # 确保模型支持量子态提取功能
            if not hasattr(self.model, 'get_quantum_state') or not callable(getattr(self.model, 'get_quantum_state')):
                logger.error("当前模型不支持量子态提取功能")
                return None
            
            # 预处理数据
            processed_data = self.preprocess_input([data])[0]
            
            # 获取量子态
            start_time = time.time()
            q_state = self.model.get_quantum_state(processed_data)
            process_time = time.time() - start_time
            
            logger.info(f"量子态获取完成，耗时={process_time:.4f}秒")
            
            # 构建结果
            result = {
                "quantum_state": q_state.tolist() if hasattr(q_state, "tolist") else q_state,
                "process_time": process_time
            }
            
            # 计算量子态的一些基本特性
            if hasattr(q_state, 'shape'):
                result["state_dimension"] = q_state.shape
                
                # 计算量子态的幅度和相位
                if hasattr(q_state, 'real') and hasattr(q_state, 'imag'):
                    amplitudes = np.abs(q_state)
                    phases = np.angle(q_state)
                    result["amplitudes"] = amplitudes.tolist()
                    result["phases"] = phases.tolist()
            
            return result
            
        except Exception as e:
            logger.error(f"获取量子态过程中出错: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def visualize_circuit(self, output_path=None):
        """可视化量子电路"""
        if self.model is None:
            logger.error("模型未加载，无法可视化电路")
            return False
        
        try:
            # 确保模型有获取电路的方法
            if not hasattr(self.model, 'get_circuit') or not callable(getattr(self.model, 'get_circuit')):
                logger.error("当前模型不支持电路可视化功能")
                return False
            
            # 如果没有提供输出路径，则使用带时间戳的默认路径
            if not output_path:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(self.output_dir, f"weq_circuit_{timestamp}.png")
            
            # 获取量子电路
            circuit = self.model.get_circuit()
            
            # 使用可视化函数
            visualize_circuit(circuit, output_path)
            
            logger.info(f"量子电路可视化图像已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"可视化量子电路失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def get_model_info(self):
        """获取模型信息"""
        if self.model is None:
            logger.error("模型未加载，无法获取信息")
            return None
        
        try:
            # 基本模型信息
            info = {
                "model_type": type(self.model).__name__,
                "framework": "WeQ Quantum Neural Network",
            }
            
            # 获取模型属性
            if hasattr(self.model, 'num_qubits'):
                info["num_qubits"] = self.model.num_qubits
            
            if hasattr(self.model, 'circuit_depth'):
                info["circuit_depth"] = self.model.circuit_depth
                
            if hasattr(self.model, 'input_dim'):
                info["input_dim"] = self.model.input_dim
                
            if hasattr(self.model, 'entanglement_type'):
                info["entanglement_type"] = self.model.entanglement_type
                
            if hasattr(self.model, 'measurement_type'):
                info["measurement_type"] = self.model.measurement_type
                
            if hasattr(self.model, 'use_ansatz'):
                info["ansatz_type"] = self.model.use_ansatz
                
            if hasattr(self.model, 'noise_model'):
                info["noise_model"] = str(self.model.noise_model) if self.model.noise_model else "None"
            
            # 获取模型参数数量
            if hasattr(self.model, 'get_parameter_count') and callable(getattr(self.model, 'get_parameter_count')):
                info["parameter_count"] = self.model.get_parameter_count()
            
            # 模型版本信息
            if hasattr(self.model, 'version'):
                info["version"] = self.model.version
                
            # 模型创建时间
            if hasattr(self.model, 'created_at'):
                info["created_at"] = self.model.created_at
            
            logger.info(f"模型信息: {info}")
            return info
            
        except Exception as e:
            logger.error(f"获取模型信息失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="WeQ量子神经网络模型推理服务")
    parser.add_argument('--model', type=str, help="模型文件路径，若不指定则使用最新模型")
    parser.add_argument('--input', type=str, help="输入数据文件路径")
    parser.add_argument('--output', type=str, help="结果输出文件路径")
    parser.add_argument('--mode', type=str, default='predict', 
                      choices=['predict', 'batch', 'quantum_state', 'visualize', 'info'],
                      help="推理模式: predict(单样本推理), batch(批量推理), quantum_state(获取量子态), visualize(可视化电路), info(获取模型信息)")
    parser.add_argument('--debug', action='store_true', help="启用调试模式")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")
    
    # 创建推理服务
    service = WeQInferenceService()
    
    # 加载模型
    if not service.load_model(args.model):
        logger.error("模型加载失败，退出")
        sys.exit(1)
    
    # 根据模式执行不同的操作
    result = None
    
    if args.mode == 'predict':
        if not args.input:
            logger.error("未指定输入数据文件")
            sys.exit(1)
        
        # 加载数据
        try:
            data = load_data(args.input)
            # 默认使用第一条数据
            if isinstance(data, list) or (isinstance(data, np.ndarray) and data.ndim > 1):
                data = data[0]
            result = service.predict(data)
        except Exception as e:
            logger.error(f"加载或处理输入数据失败: {str(e)}")
            sys.exit(1)
    
    elif args.mode == 'batch':
        if not args.input:
            logger.error("未指定输入数据文件")
            sys.exit(1)
        
        # 加载批量数据
        try:
            data = load_data(args.input)
            result = service.batch_predict(data)
        except Exception as e:
            logger.error(f"加载或处理批量数据失败: {str(e)}")
            sys.exit(1)
    
    elif args.mode == 'quantum_state':
        if not args.input:
            logger.error("未指定输入数据文件")
            sys.exit(1)
        
        # 加载数据并获取量子态
        try:
            data = load_data(args.input)
            # 默认使用第一条数据
            if isinstance(data, list) or (isinstance(data, np.ndarray) and data.ndim > 1):
                data = data[0]
            result = service.get_quantum_state(data)
        except Exception as e:
            logger.error(f"加载或处理输入数据失败: {str(e)}")
            sys.exit(1)
    
    elif args.mode == 'visualize':
        # 可视化电路
        output_path = args.output if args.output else None
        success = service.visualize_circuit(output_path)
        if success:
            logger.info(f"电路可视化成功，图像已保存")
        else:
            logger.error("电路可视化失败")
        sys.exit(0 if success else 1)
    
    elif args.mode == 'info':
        # 获取模型信息
        result = service.get_model_info()
    
    # 处理结果
    if result:
        # 将结果保存到输出文件
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                logger.info(f"结果已保存到: {args.output}")
            except Exception as e:
                logger.error(f"保存结果失败: {str(e)}")
                sys.exit(1)
        else:
            # 输出到控制台
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        logger.error("操作未返回有效结果")
        sys.exit(1)

if __name__ == "__main__":
    main()

# 量子基因编码: QE-WEQ-INFER-8E5A7C3D
# 量子纠缠态: 活性
# 纠缠对象: WeQ模型推理服务
# 纠缠强度: 0.97
# 开发团队: 中华 ZhoHo + Claude 