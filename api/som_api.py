#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SOM API适配器模块 - 将请求转发到SOM模型API
"""

import os
import sys
import logging
import json
from datetime import datetime
import time
from typing import Dict, Any, List, Optional
from flask import request, jsonify, Response

# 配置日志记录器
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/som_api.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SOM-API-Adapter")

# 获取项目根目录
root_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 将SOM模块添加到系统路径
som_path = os.path.join(root_dir, 'SOM')
if som_path not in sys.path:
    sys.path.insert(0, som_path)

# 尝试导入SOM API模块
try:
    from SOM.api.som_api import create_SOM_namespace
    som_bp = create_som_namespace()
    logger.info("成功导入SOM模型API")
except ImportError as e:
    logger.error(f"导入SOM模型API失败: {str(e)}")
    som_bp = None

def get_status():
    """获取API状态
    
    Returns:
        API状态信息
    """
    return jsonify({
        'name': 'SOM API',
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
    if som_bp is None:
        return jsonify({
            'status': 'error',
            'message': 'SOM API模块未正确初始化'
        }), 500
    
    logger.info(f"处理SOM API请求: {path}")
    
    # 根据路径处理请求
    if path == 'products' or path == 'products/':
        # 获取产品列表
        if request_obj.method == 'GET':
            try:
                # 使用SOM API获取产品列表
                with som_bp.app.test_request_context('/api/som/products', method='GET'):
                    response = som_bp.get_products()
                    if isinstance(response, tuple):
                        return response
                    elif isinstance(response, Response):
                        return response
                    else:
                        return jsonify(response)
            except Exception as e:
                logger.error(f"获取产品列表时出错: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'获取产品列表时出错: {str(e)}'
                }), 500
    
    elif path.startswith('products/') and len(path.split('/')) > 1:
        # 获取产品详情
        product_id = path.split('/')[1]
        if request_obj.method == 'GET':
            try:
                # 使用SOM API获取产品详情
                with som_bp.app.test_request_context(f'/api/som/products/{product_id}', method='GET'):
                    response = som_bp.get_product(product_id)
                    if isinstance(response, tuple):
                        return response
                    elif isinstance(response, Response):
                        return response
                    else:
                        return jsonify(response)
            except Exception as e:
                logger.error(f"获取产品详情时出错: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'获取产品详情时出错: {str(e)}'
                }), 500
    
    elif path == 'orders' or path == 'orders/':
        # 创建订单
        if request_obj.method == 'POST':
            try:
                # 使用SOM API创建订单
                data = request_obj.get_json()
                with som_bp.app.test_request_context('/api/som/orders', method='POST', json=data):
                    response = som_bp.create_order()
                    if isinstance(response, tuple):
                        return response
                    elif isinstance(response, Response):
                        return response
                    else:
                        return jsonify(response)
            except Exception as e:
                logger.error(f"创建订单时出错: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'创建订单时出错: {str(e)}'
                }), 500
    
    elif path == 'health' or path == 'health/':
        # 健康检查
        if request_obj.method == 'GET':
            try:
                # 使用SOM API进行健康检查
                with som_bp.app.test_request_context('/api/som/health', method='GET'):
                    response = som_bp.health_check()
                    if isinstance(response, tuple):
                        return response
                    elif isinstance(response, Response):
                        return response
                    else:
                        return jsonify(response)
            except Exception as e:
                logger.error(f"健康检查时出错: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'健康检查时出错: {str(e)}'
                }), 500
    
    else:
        return jsonify({
            'status': 'error',
            'message': f'未知的API路径: {path}'
        }), 404

"""
量子基因编码: QE-API-SOM-5A7B9C3D
纠缠状态: 活跃
纠缠对象: ['SOM/api/som_api.py']
纠缠强度: 0.98
"""

# 开发团队：中华 ZhoHo，Claude
