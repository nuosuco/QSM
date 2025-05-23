#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SOM推理服务 - 自组织映射模型推理服务
此脚本提供SOM模型的推理功能
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
som_dir = os.path.dirname(scripts_dir)
project_root = os.path.dirname(som_dir)
sys.path.insert(0, project_root)

# 导入SOM模型相关模块
try:
    from SOM.som_core import SOMModel
    from SOM.som_utils import load_data, preprocess_data, visualize_som
except ImportError as e:
    print(f"错误: 无法导入SOM模块 - {e}")
    sys.exit(1)

# 创建日志目录
log_dir = os.path.join(project_root, ".logs")
os.makedirs(log_dir, exist_ok=True)

# 配置日志
def setup_logging(log_level=logging.INFO):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"som_inference_{timestamp}.log")
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("SOM_INFERENCE")

logger = setup_logging()

class SOMInferenceService:
    """SOM模型推理服务类"""
    
    def __init__(self):
        self.model = None
        self.model_dir = os.path.join(som_dir, "models")
        self.output_dir = os.path.join(som_dir, "outputs")
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("SOM推理服务初始化完成")
        
    def load_model(self, model_path=None):
        """加载模型"""
        if model_path is None:
            # 使用最新的模型
            model_files = [f for f in os.listdir(self.model_dir) if f.endswith('.som')]
            if not model_files:
                logger.error("没有找到可用的模型文件")
                return False
            
            # 按时间排序，选择最新的模型
            model_path = os.path.join(self.model_dir, sorted(model_files)[-1])
        
        try:
            logger.info(f"从 {model_path} 加载模型...")
            self.model = SOMModel.load(model_path)
            logger.info(f"模型加载成功: {model_path}")
            return True
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def predict(self, data, raw_output=False):
        """单一数据推理"""
        if self.model is None:
            logger.error("模型未加载，无法进行推理")
            return None
        
        try:
            # 预处理数据
            processed_data = preprocess_data([data])[0]
            
            # 进行推理
            start_time = time.time()
            bmu, distances = self.model.predict(processed_data)
            inference_time = time.time() - start_time
            
            logger.info(f"推理完成: BMU={bmu}, 耗时={inference_time:.4f}秒")
            
            if raw_output:
                return bmu, distances
            
            # 构建结果
            result = {
                "bmu": bmu,
                "distances": distances.tolist() if hasattr(distances, "tolist") else distances,
                "inference_time": inference_time
            }
            
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
        
        results = []
        try:
            # 预处理数据
            processed_data = preprocess_data(data_list)
            
            # 批量推理
            start_time = time.time()
            bmus = []
            for i, data in enumerate(processed_data):
                bmu, distances = self.model.predict(data)
                bmus.append(bmu)
                
                if i % 100 == 0 and i > 0:
                    logger.info(f"已完成 {i}/{len(processed_data)} 个样本的推理")
            
            batch_time = time.time() - start_time
            
            # 构建结果
            results = {
                "bmus": bmus,
                "count": len(bmus),
                "batch_time": batch_time,
                "avg_time_per_sample": batch_time / len(processed_data) if processed_data else 0
            }
            
            logger.info(f"批量推理完成: {len(bmus)}个样本, 总耗时={batch_time:.4f}秒, "
                       f"平均每样本耗时={results['avg_time_per_sample']:.4f}秒")
            
            return results
            
        except Exception as e:
            logger.error(f"批量推理过程中出错: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def cluster(self, data_list, normalize=True):
        """对数据进行聚类"""
        if self.model is None:
            logger.error("模型未加载，无法进行聚类")
            return None
        
        try:
            # 预处理数据
            processed_data = preprocess_data(data_list)
            
            # 使用SOM进行聚类
            start_time = time.time()
            cluster_results = self.model.cluster(processed_data, normalize=normalize)
            cluster_time = time.time() - start_time
            
            # 构建结果
            num_clusters = len(set(cluster_results))
            results = {
                "clusters": cluster_results,
                "num_clusters": num_clusters,
                "cluster_sizes": {i: cluster_results.count(i) for i in set(cluster_results)},
                "cluster_time": cluster_time
            }
            
            logger.info(f"聚类完成: 识别出{num_clusters}个聚类, 耗时={cluster_time:.4f}秒")
            
            return results
            
        except Exception as e:
            logger.error(f"聚类过程中出错: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def visualize(self, output_path=None, include_umatrix=True, include_component_planes=True):
        """可视化SOM模型"""
        if self.model is None:
            logger.error("模型未加载，无法进行可视化")
            return None
        
        if output_path is None:
            # 生成默认输出路径
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"som_visualization_{timestamp}")
        
        try:
            # 可视化SOM
            start_time = time.time()
            vis_result = visualize_som(
                self.model, 
                output_path, 
                include_umatrix=include_umatrix, 
                include_component_planes=include_component_planes
            )
            vis_time = time.time() - start_time
            
            # 构建结果
            results = {
                "visualization_path": output_path,
                "visualization_time": vis_time,
                "visualization_details": vis_result
            }
            
            logger.info(f"可视化完成: 输出路径={output_path}, 耗时={vis_time:.4f}秒")
            
            return results
            
        except Exception as e:
            logger.error(f"可视化过程中出错: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def get_model_info(self):
        """获取模型信息"""
        if self.model is None:
            logger.error("模型未加载，无法获取信息")
            return None
        
        try:
            # 获取模型信息
            info = self.model.get_info()
            
            logger.info(f"获取模型信息成功: 地图大小={info.get('map_size', 'unknown')}")
            
            return info
            
        except Exception as e:
            logger.error(f"获取模型信息时出错: {str(e)}")
            logger.error(traceback.format_exc())
            return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="SOM模型推理服务")
    parser.add_argument("--model", type=str, help="模型路径")
    parser.add_argument("--input", type=str, help="输入数据文件路径")
    parser.add_argument("--output", type=str, help="输出结果路径")
    parser.add_argument("--mode", type=str, choices=["predict", "cluster", "visualize", "info"],
                        default="info", help="推理模式")
    parser.add_argument("--debug", action="store_true", help="启用调试日志")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    logger.info("==== SOM模型推理服务启动 ====")
    logger.info(f"项目根目录: {project_root}")
    logger.info(f"推理模式: {args.mode}")
    
    # 初始化推理服务
    inference_service = SOMInferenceService()
    
    # 加载模型
    if not inference_service.load_model(args.model):
        sys.exit(1)
    
    # 执行对应操作
    if args.mode == "info":
        # 获取模型信息
        info = inference_service.get_model_info()
        if info:
            print(json.dumps(info, indent=2))
            logger.info("模型信息获取成功")
        else:
            logger.error("获取模型信息失败")
            sys.exit(1)
    
    elif args.mode == "predict":
        if not args.input:
            logger.error("预测模式需要提供输入数据文件路径")
            sys.exit(1)
        
        # 加载输入数据
        try:
            data = load_data(args.input)
            logger.info(f"加载数据成功: {len(data)}个样本")
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            sys.exit(1)
        
        # 进行批量预测
        results = inference_service.batch_predict(data)
        if results:
            # 保存结果
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
                logger.info(f"预测结果已保存到: {args.output}")
            else:
                print(json.dumps(results, indent=2))
        else:
            logger.error("预测失败")
            sys.exit(1)
    
    elif args.mode == "cluster":
        if not args.input:
            logger.error("聚类模式需要提供输入数据文件路径")
            sys.exit(1)
        
        # 加载输入数据
        try:
            data = load_data(args.input)
            logger.info(f"加载数据成功: {len(data)}个样本")
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            sys.exit(1)
        
        # 进行聚类
        results = inference_service.cluster(data)
        if results:
            # 保存结果
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
                logger.info(f"聚类结果已保存到: {args.output}")
            else:
                print(json.dumps(results, indent=2))
        else:
            logger.error("聚类失败")
            sys.exit(1)
    
    elif args.mode == "visualize":
        # 可视化模型
        results = inference_service.visualize(args.output)
        if results:
            logger.info(f"可视化成功: {results['visualization_path']}")
        else:
            logger.error("可视化失败")
            sys.exit(1)
    
    logger.info("==== SOM模型推理服务结束 ====")
    return 0

if __name__ == "__main__":
    sys.exit(main())

"""
量子基因编码: QE-INF-S0O4M2
纠缠状态: 活跃
纠缠对象: ['SOM/som_core.py', 'SOM/models/']
纠缠强度: 0.97

# 开发团队：中华 ZhoHo ，Claude 
""" 