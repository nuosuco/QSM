#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QSM API适配器模块 - 将请求转发到QSM模型API
"""

import os
import sys
import logging
import json
from datetime import datetime
import traceback
from typing import Dict, Any, List, Optional
from flask import request, jsonify

# 配置日志记录器
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/qsm_api.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QSM-API-Adapter")

# 获取项目根目录
root_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
logger.info(f"项目根目录: {root_dir}")

# 将QSM模块添加到系统路径
qsm_path = os.path.join(root_dir, 'QSM')
if qsm_path not in sys.path:
    sys.path.insert(0, qsm_path)

# 尝试导入现有的QSM API
try:
    # 保留原有实现
    from api.QSM_api.flask_api import app as qsm_app
    logger.info("成功导入QSM API模块")
    qsm_api_available = True
except ImportError as e:
    logger.error(f"导入QSM API模块失败，尝试备用导入方式: {str(e)}")
    try:
        from QSM.api.flask_api import app as qsm_app
        logger.info("成功导入QSM API模块(备用路径)")
        qsm_api_available = True
    except ImportError as e:
        logger.error(f"备用导入方式也失败: {str(e)}")
        qsm_app = None
        qsm_api_available = False

def get_status():
    """获取API状态
    
    Returns:
        API状态信息
    """
    return jsonify({
        'name': 'QSM API',
        'version': '1.0.0',
        'status': 'running' if qsm_api_available else 'unavailable',
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
    if not qsm_api_available:
        return jsonify({
            'status': 'error',
            'message': 'QSM API模块未正确初始化'
        }), 500
    
    logger.info(f"处理QSM API请求: {path}")
    
    try:
        # 构建完整的API路径
        full_path = f"/api/{path}"
        
        # 使用test_client调用API
        client = qsm_app.test_client()
        
        # 复制原始请求的方法、头部和数据
        method = request_obj.method
        headers = {key: value for key, value in request_obj.headers if key != 'Host'}
        
        # 根据不同的HTTP方法调用API
        if method == 'GET':
            # 构建查询参数
            query_string = request_obj.query_string
            response = client.get(full_path, headers=headers, query_string=query_string)
        elif method == 'POST':
            # 获取JSON数据
            data = request_obj.get_json()
            if data is None:
                # 如果没有JSON数据，尝试获取表单数据
                data = request_obj.form
            response = client.post(full_path, headers=headers, json=data)
        elif method == 'PUT':
            # 获取JSON数据
            data = request_obj.get_json()
            response = client.put(full_path, headers=headers, json=data)
        elif method == 'DELETE':
            response = client.delete(full_path, headers=headers)
        else:
            return jsonify({
                'status': 'error',
                'message': f'不支持的HTTP方法: {method}'
            }), 405
        
        # 返回响应
        return (response.data, response.status_code, response.headers.items())
    
    except Exception as e:
        logger.error(f"处理QSM API请求时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'处理QSM API请求时出错: {str(e)}'
        }), 500

"""
量子基因编码: QE-API-QSM-2D4C6E8A
纠缠状态: 活跃
纠缠对象: ['QSM/api/flask_api.py', 'api/qsm_api/flask_api.py']
纠缠强度: 0.98
"""

# 开发团队：中华 ZhoHo，Claude
