#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SOM API服务 - 自组织映射模型API服务
此脚本提供SOM模型的Web API功能
"""

import os
import sys
import json
import time
import logging
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

# 导入Flask相关库
try:
    from flask import Flask, request, jsonify, send_file
    from flask_cors import CORS
except ImportError as e:
    print(f"错误: 无法导入Flask相关模块 - {e}")
    print("请安装所需依赖: pip install flask flask-cors")
    sys.exit(1)

# 导入SOM模型相关模块
try:
    from SOM.scripts.services.SOM_inference import SOMInferenceService
    from SOM.som_utils import load_data, preprocess_data
except ImportError as e:
    print(f"错误: 无法导入SOM模块 - {e}")
    sys.exit(1)

# 创建日志目录
log_dir = os.path.join(project_root, ".logs")
os.makedirs(log_dir, exist_ok=True)

# 配置日志
def setup_logging(log_level=logging.INFO):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"som_api_{timestamp}.log")
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("SOM_API")

logger = setup_logging()

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 初始化推理服务
inference_service = SOMInferenceService()

# API版本
API_VERSION = "1.0.0"

# 端口
PORT = 5002

# 健康检查
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "ok",
        "service": "SOM API",
        "version": API_VERSION,
        "timestamp": datetime.datetime.now().isoformat()
    })

# API根路径
@app.route('/', methods=['GET'])
def api_root():
    """API根路径接口"""
    return jsonify({
        "service": "SOM API服务",
        "version": API_VERSION,
        "description": "自组织映射模型API服务",
        "endpoints": {
            "/health": "健康检查",
            "/api/v1/model/info": "获取模型信息",
            "/api/v1/model/load": "加载模型",
            "/api/v1/predict": "单样本预测",
            "/api/v1/batch_predict": "批量预测",
            "/api/v1/cluster": "数据聚类",
            "/api/v1/visualize": "模型可视化"
        }
    })

# 获取模型信息
@app.route('/api/v1/model/info', methods=['GET'])
def get_model_info():
    """获取模型信息接口"""
    try:
        # 检查模型是否已加载
        if inference_service.model is None:
            return jsonify({
                "status": "error",
                "message": "模型未加载",
                "code": 400
            }), 400
        
        # 获取模型信息
        info = inference_service.get_model_info()
        if info:
            return jsonify({
                "status": "success",
                "data": info
            })
        else:
            return jsonify({
                "status": "error",
                "message": "获取模型信息失败",
                "code": 500
            }), 500
    
    except Exception as e:
        logger.error(f"获取模型信息时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"服务器内部错误: {str(e)}",
            "code": 500
        }), 500

# 加载模型
@app.route('/api/v1/model/load', methods=['POST'])
def load_model():
    """加载模型接口"""
    try:
        # 获取请求数据
        data = request.get_json() or {}
        model_path = data.get('model_path')
        
        # 加载模型
        if inference_service.load_model(model_path):
            return jsonify({
                "status": "success",
                "message": f"模型加载成功: {model_path if model_path else '最新模型'}"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "模型加载失败",
                "code": 500
            }), 500
    
    except Exception as e:
        logger.error(f"加载模型时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"服务器内部错误: {str(e)}",
            "code": 500
        }), 500

# 单样本预测
@app.route('/api/v1/predict', methods=['POST'])
def predict():
    """单样本预测接口"""
    try:
        # 获取请求数据
        data = request.get_json() or {}
        sample = data.get('sample')
        
        if not sample:
            return jsonify({
                "status": "error",
                "message": "未提供有效的样本数据",
                "code": 400
            }), 400
        
        # 检查模型是否已加载
        if inference_service.model is None:
            # 尝试加载模型
            if not inference_service.load_model():
                return jsonify({
                    "status": "error",
                    "message": "模型未加载且无法自动加载",
                    "code": 400
                }), 400
        
        # 进行预测
        result = inference_service.predict(sample)
        if result:
            return jsonify({
                "status": "success",
                "data": result
            })
        else:
            return jsonify({
                "status": "error",
                "message": "预测失败",
                "code": 500
            }), 500
    
    except Exception as e:
        logger.error(f"预测时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"服务器内部错误: {str(e)}",
            "code": 500
        }), 500

# 批量预测
@app.route('/api/v1/batch_predict', methods=['POST'])
def batch_predict():
    """批量预测接口"""
    try:
        # 获取请求数据
        if request.is_json:
            data = request.get_json() or {}
            samples = data.get('samples')
        else:
            # 处理文件上传
            if 'file' not in request.files:
                return jsonify({
                    "status": "error",
                    "message": "未提供数据文件",
                    "code": 400
                }), 400
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    "status": "error",
                    "message": "未选择数据文件",
                    "code": 400
                }), 400
                
            # 保存上传的文件
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            tmp_file = os.path.join(log_dir, f"upload_{timestamp}.json")
            file.save(tmp_file)
            
            # 加载文件内容
            try:
                samples = load_data(tmp_file)
                # 删除临时文件
                os.remove(tmp_file)
            except:
                # 删除临时文件
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
                return jsonify({
                    "status": "error",
                    "message": "无法解析上传的数据文件",
                    "code": 400
                }), 400
        
        if not samples or not isinstance(samples, list):
            return jsonify({
                "status": "error",
                "message": "未提供有效的样本数据列表",
                "code": 400
            }), 400
        
        # 检查模型是否已加载
        if inference_service.model is None:
            # 尝试加载模型
            if not inference_service.load_model():
                return jsonify({
                    "status": "error",
                    "message": "模型未加载且无法自动加载",
                    "code": 400
                }), 400
        
        # 进行批量预测
        results = inference_service.batch_predict(samples)
        if results:
            return jsonify({
                "status": "success",
                "data": results
            })
        else:
            return jsonify({
                "status": "error",
                "message": "批量预测失败",
                "code": 500
            }), 500
    
    except Exception as e:
        logger.error(f"批量预测时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"服务器内部错误: {str(e)}",
            "code": 500
        }), 500

# 数据聚类
@app.route('/api/v1/cluster', methods=['POST'])
def cluster():
    """数据聚类接口"""
    try:
        # 获取请求数据
        if request.is_json:
            data = request.get_json() or {}
            samples = data.get('samples')
            normalize = data.get('normalize', True)
        else:
            # 处理文件上传
            if 'file' not in request.files:
                return jsonify({
                    "status": "error",
                    "message": "未提供数据文件",
                    "code": 400
                }), 400
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    "status": "error",
                    "message": "未选择数据文件",
                    "code": 400
                }), 400
                
            # 保存上传的文件
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            tmp_file = os.path.join(log_dir, f"upload_{timestamp}.json")
            file.save(tmp_file)
            
            # 加载文件内容
            try:
                samples = load_data(tmp_file)
                # 删除临时文件
                os.remove(tmp_file)
            except:
                # 删除临时文件
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
                return jsonify({
                    "status": "error",
                    "message": "无法解析上传的数据文件",
                    "code": 400
                }), 400
                
            normalize = request.form.get('normalize', 'true').lower() in ['true', '1', 't', 'y', 'yes']
        
        if not samples or not isinstance(samples, list):
            return jsonify({
                "status": "error",
                "message": "未提供有效的样本数据列表",
                "code": 400
            }), 400
        
        # 检查模型是否已加载
        if inference_service.model is None:
            # 尝试加载模型
            if not inference_service.load_model():
                return jsonify({
                    "status": "error",
                    "message": "模型未加载且无法自动加载",
                    "code": 400
                }), 400
        
        # 进行聚类
        results = inference_service.cluster(samples, normalize=normalize)
        if results:
            return jsonify({
                "status": "success",
                "data": results
            })
        else:
            return jsonify({
                "status": "error",
                "message": "聚类失败",
                "code": 500
            }), 500
    
    except Exception as e:
        logger.error(f"聚类时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"服务器内部错误: {str(e)}",
            "code": 500
        }), 500

# 模型可视化
@app.route('/api/v1/visualize', methods=['GET', 'POST'])
def visualize():
    """模型可视化接口"""
    try:
        # 获取请求参数
        if request.method == 'POST':
            data = request.get_json() or {}
            include_umatrix = data.get('include_umatrix', True)
            include_component_planes = data.get('include_component_planes', True)
        else:
            include_umatrix = request.args.get('include_umatrix', 'true').lower() in ['true', '1', 't', 'y', 'yes']
            include_component_planes = request.args.get('include_component_planes', 'true').lower() in ['true', '1', 't', 'y', 'yes']
        
        # 检查模型是否已加载
        if inference_service.model is None:
            # 尝试加载模型
            if not inference_service.load_model():
                return jsonify({
                    "status": "error",
                    "message": "模型未加载且无法自动加载",
                    "code": 400
                }), 400
        
        # 生成可视化输出路径
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(inference_service.output_dir, f"som_visualization_{timestamp}")
        
        # 进行可视化
        results = inference_service.visualize(
            output_path=output_path,
            include_umatrix=include_umatrix,
            include_component_planes=include_component_planes
        )
        
        if results:
            return jsonify({
                "status": "success",
                "data": results
            })
        else:
            return jsonify({
                "status": "error",
                "message": "可视化失败",
                "code": 500
            }), 500
    
    except Exception as e:
        logger.error(f"可视化时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"服务器内部错误: {str(e)}",
            "code": 500
        }), 500

# 获取可视化图片
@app.route('/api/v1/visualization/<path:filename>', methods=['GET'])
def get_visualization(filename):
    """获取可视化图片接口"""
    try:
        # 检查文件路径安全性
        if '..' in filename or filename.startswith('/'):
            return jsonify({
                "status": "error",
                "message": "非法的文件路径",
                "code": 400
            }), 400
        
        # 构建文件路径
        file_path = os.path.join(inference_service.output_dir, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({
                "status": "error",
                "message": "文件不存在",
                "code": 404
            }), 404
        
        # 返回文件
        return send_file(file_path)
    
    except Exception as e:
        logger.error(f"获取可视化图片时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"服务器内部错误: {str(e)}",
            "code": 500
        }), 500

def start_server(host='0.0.0.0', port=PORT, debug=False):
    """启动API服务器"""
    # 预加载模型
    inference_service.load_model()
    
    # 启动Flask应用
    logger.info(f"SOM API服务正在启动，监听地址: {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="SOM API服务")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=PORT, help="监听端口")
    parser.add_argument("--model", type=str, help="模型路径")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # 如果指定了模型路径，则加载模型
    if args.model:
        inference_service.load_model(args.model)
    
    logger.info("==== SOM API服务启动 ====")
    logger.info(f"项目根目录: {project_root}")
    logger.info(f"监听地址: {args.host}:{args.port}")
    
    # 启动服务器
    start_server(host=args.host, port=args.port, debug=args.debug)

# 量子基因编码: QE-API-S0O4M2
# 纠缠状态: 活跃
# 纠缠对象: ['SOM/scripts/services/SOM_inference.py', 'SOM/som_core.py']
# 纠缠强度: 0.98

# 开发团队：中华 ZhoHo ，Claude 