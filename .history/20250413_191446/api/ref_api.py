#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ref API适配器模块 - 将请求转发到Ref模型API
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import request, jsonify

# 配置日志记录器
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/ref_api.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Ref-API-Adapter")

# 获取项目根目录
root_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 将Ref模块添加到系统路径
ref_path = os.path.join(root_dir, 'Ref')
if ref_path not in sys.path:
    sys.path.insert(0, ref_path)

# 尝试导入Ref API模块
try:
    from Ref.api.ref_api import create_Ref_namespace
    from flask_restx import Api
    
    # 创建一个临时的API实例，用于获取Ref API命名空间
    dummy_api = Api()
    ref_ns = create_ref_namespace(dummy_api)
    
    logger.info("成功导入Ref模型API")
except ImportError as e:
    logger.error(f"导入Ref模型API失败: {str(e)}")
    ref_ns = None

def get_status():
    """获取API状态
    
    Returns:
        API状态信息
    """
    return jsonify({
        'name': 'Ref API',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

def handle_request(path, request_obj):
    """处理API请求
    
    Args:
        path: 请求路径
        request_obj: Flask请求对象
        
    Returns:
        API响应
    """
    if ref_ns is None:
        return jsonify({
            'status': 'error',
            'message': 'Ref API模块未正确初始化'
        }), 500
    
    logger.info(f"处理Ref API请求: {path}")
    
    # 根据路径处理请求
    if path == 'health' or path == 'health/':
        # 健康状态检查
        if request_obj.method == 'GET':
            try:
                # 获取RefHealth资源类
                ref_health = ref_ns.resources['/health']
                
                # 创建资源实例并调用get方法
                response = ref_health().get()
                if isinstance(response, tuple):
                    return response
                else:
                    return jsonify(response)
            except Exception as e:
                logger.error(f"健康状态检查时出错: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'健康状态检查时出错: {str(e)}'
                }), 500
    
    elif path == 'status' or path == 'status/':
        # 详细状态检查
        if request_obj.method == 'GET':
            try:
                # 获取RefStatus资源类
                ref_status = ref_ns.resources['/status']
                
                # 创建资源实例并调用get方法
                response = ref_status().get()
                if isinstance(response, tuple):
                    return response
                else:
                    return jsonify(response)
            except Exception as e:
                logger.error(f"详细状态检查时出错: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'详细状态检查时出错: {str(e)}'
                }), 500
    
    elif path == 'models' or path == 'models/':
        # 获取已注册的模型列表
        if request_obj.method == 'GET':
            try:
                # 获取RefModels资源类
                ref_models = ref_ns.resources['/models']
                
                # 创建资源实例并调用get方法
                response = ref_models().get()
                if isinstance(response, tuple):
                    return response
                else:
                    return jsonify(response)
            except Exception as e:
                logger.error(f"获取模型列表时出错: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'获取模型列表时出错: {str(e)}'
                }), 500
    
    elif path.startswith('model/') and len(path.split('/')) > 1:
        # 获取特定模型的信息
        model_id = path.split('/')[1]
        if request_obj.method == 'GET':
            try:
                # 获取RefModel资源类
                ref_model = ref_ns.resources['/model/<string:model_id>']
                
                # 创建资源实例并调用get方法
                response = ref_model().get(model_id)
                if isinstance(response, tuple):
                    return response
                else:
                    return jsonify(response)
            except Exception as e:
                logger.error(f"获取模型信息时出错: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'获取模型信息时出错: {str(e)}'
                }), 500
    
    elif path.startswith('repair/') and len(path.split('/')) > 1:
        # 修复指定的模型
        model_id = path.split('/')[1]
        if request_obj.method == 'POST':
            try:
                # 获取RefRepairModel资源类
                ref_repair = ref_ns.resources['/repair/<string:model_id>']
                
                # 创建资源实例并调用post方法
                response = ref_repair().post(model_id)
                if isinstance(response, tuple):
                    return response
                else:
                    return jsonify(response)
            except Exception as e:
                logger.error(f"修复模型时出错: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'修复模型时出错: {str(e)}'
                }), 500
    
    elif path == 'optimize' or path == 'optimize/':
        # 优化系统
        if request_obj.method == 'POST':
            try:
                # 获取RefOptimize资源类
                ref_optimize = ref_ns.resources['/optimize']
                
                # 创建资源实例并调用post方法
                response = ref_optimize().post()
                if isinstance(response, tuple):
                    return response
                else:
                    return jsonify(response)
            except Exception as e:
                logger.error(f"优化系统时出错: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'优化系统时出错: {str(e)}'
                }), 500
    
    elif path == 'marker/add' or path == 'marker/add/':
        # 添加量子基因标记
        if request_obj.method == 'POST':
            try:
                # 获取RefAddMarker资源类
                ref_add_marker = ref_ns.resources['/marker/add']
                
                # 创建资源实例并调用post方法
                data = request_obj.get_json()
                response = ref_add_marker().post()
                if isinstance(response, tuple):
                    return response
                else:
                    return jsonify(response)
            except Exception as e:
                logger.error(f"添加量子基因标记时出错: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'添加量子基因标记时出错: {str(e)}'
                }), 500
    
    elif path == 'marker/update' or path == 'marker/update/':
        # 更新量子基因标记
        if request_obj.method == 'POST':
            try:
                # 获取RefUpdateMarker资源类
                ref_update_marker = ref_ns.resources['/marker/update']
                
                # 创建资源实例并调用post方法
                data = request_obj.get_json()
                response = ref_update_marker().post()
                if isinstance(response, tuple):
                    return response
                else:
                    return jsonify(response)
            except Exception as e:
                logger.error(f"更新量子基因标记时出错: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'更新量子基因标记时出错: {str(e)}'
                }), 500
    
    else:
        return jsonify({
            'status': 'error',
            'message': f'未知的API路径: {path}'
        }), 404

"""
量子基因编码: QE-API-REF-3E7D8F9A
纠缠状态: 活跃
纠缠对象: ['Ref/api/ref_api.py']
纠缠强度: 0.98
"""

# 开发团队：中华 ZhoHo，Claude 