#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ref API模块
提供Ref系统的API接口
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, Any, List
from flask_restx import Resource, fields, Namespace, Api  # 直接导入所有需要的类
from flask import request, jsonify, Flask  # 导入Flask的request对象

# 配置日志记录器
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/ref_api.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Ref-API")

# 将Ref核心添加到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
ref_root = os.path.abspath(os.path.join(current_dir, ".."))
if ref_root not in sys.path:
    sys.path.append(ref_root)

# 获取项目根目录
root_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 导入Ref核心
try:
    from Ref.ref_core import get_Ref_core
    from Ref.utils.quantum_gene_marker import get_gene_marker
    
    ref_core_available = True
except ImportError as e:
    logger.error(f"导入Ref核心模块时出错: {str(e)}")
    ref_core_available = False

def create_ref_namespace(api=None):
    """创建Ref API命名空间
    
    Args:
        api: Flask-RESTX API实例
        
    Returns:
        Ref API命名空间
    """
    logger.info("创建Ref API命名空间")
    
    # 如果未提供API实例，创建一个新的
    if api is None:
        app = Flask(__name__)
        api = Api(app)
    
    # 处理不同类型的API实例
    try:
        # 如果api是Flask应用，尝试获取保存的api实例
        if hasattr(api, 'api'):
            api = api.api
        
        # 确保api具有namespace方法
        if not hasattr(api, 'namespace'):
            logger.error("API实例不支持namespace方法")
            return None
        
        # 创建命名空间
        ref_ns = api.namespace('ref', description='Ref系统API')
        
        # 创建模型定义
        add_marker_model = ref_ns.model('AddMarker', {
            'file_path': fields.String(required=True, description='文件路径'),
            'entangled_objects': fields.List(fields.String, description='纠缠对象列表'),
            'strength': fields.Float(description='纠缠强度')
        })
        
        update_marker_model = ref_ns.model('UpdateMarker', {
            'file_path': fields.String(required=True, description='文件路径'),
            'entangled_objects': fields.List(fields.String, description='纠缠对象列表'),
            'strength': fields.Float(description='纠缠强度')
        })
        
        @ref_ns.route('/health')
        class RefHealth(Resource):
            def get(self):
                """获取Ref系统健康状态"""
                if not ref_core_available:
                    return {"status": "unavailable", "error": "Ref核心模块不可用"}, 503
                
                try:
                    ref_core = get_ref_core()
                    health_status = ref_core.get_health_status()
                
                return {
                        "status": "healthy",
                        "version": ref_core.version,
                        "quantum_gene": ref_core.quantum_gene,
                        "system_status": health_status,
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.error(f"获取Ref健康状态时出错: {str(e)}")
                    return {"status": "error", "error": str(e)}, 500
        
        @ref_ns.route('/status')
        class RefStatus(Resource):
            def get(self):
                """获取Ref系统详细状态"""
                if not ref_core_available:
                    return {"status": "unavailable", "error": "Ref核心模块不可用"}, 503
                
                try:
                    ref_core = get_ref_core()
                    detailed_status = ref_core.get_detailed_status()
                
                return {
                        "status": "success",
                        "version": ref_core.version,
                        "quantum_gene": ref_core.quantum_gene,
                        "system_status": detailed_status,
                        "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
                    logger.error(f"获取Ref详细状态时出错: {str(e)}")
                    return {"status": "error", "error": str(e)}, 500
        
        @ref_ns.route('/models')
        class RefModels(Resource):
            def get(self):
                """获取已注册的模型列表"""
                if not ref_core_available:
                    return {"status": "unavailable", "error": "Ref核心模块不可用"}, 503
                
                try:
                    ref_core = get_ref_core()
                
                return {
                        "status": "success",
                        "models": ref_core.registered_models,
                        "count": len(ref_core.registered_models),
                        "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                    logger.error(f"获取已注册模型列表时出错: {str(e)}")
                    return {"status": "error", "error": str(e)}, 500
        
        @ref_ns.route('/model/<string:model_id>')
        class RefModel(Resource):
            def get(self, model_id):
                """获取特定模型的信息"""
                if not ref_core_available:
                    return {"status": "unavailable", "error": "Ref核心模块不可用"}, 503
                
                try:
                    ref_core = get_ref_core()
                    
                    if model_id not in ref_core.registered_models:
                        return {"status": "error", "error": f"模型 {model_id} 未注册"}, 404
                    
                    return {
                        "status": "success",
                        "model_id": model_id,
                        "model_info": ref_core.registered_models[model_id],
                        "timestamp": datetime.now().isoformat()
                    }
            except Exception as e:
                    logger.error(f"获取模型 {model_id} 信息时出错: {str(e)}")
                    return {"status": "error", "error": str(e)}, 500
        
        @ref_ns.route('/repair/<string:model_id>')
        class RefRepairModel(Resource):
            def post(self, model_id):
                """修复指定的模型"""
                if not ref_core_available:
                    return {"status": "unavailable", "error": "Ref核心模块不可用"}, 503
                
                try:
                    ref_core = get_ref_core()
                    
                    if model_id not in ref_core.registered_models:
                        return {"status": "error", "error": f"模型 {model_id} 未注册"}, 404
                    
                    success = ref_core.repair_model(model_id)
                    
                    if success:
                        return {
                            "status": "success",
                            "message": f"模型 {model_id} 修复成功",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"模型 {model_id} 修复失败",
                            "timestamp": datetime.now().isoformat()
                        }, 500
                    
            except Exception as e:
                    logger.error(f"修复模型 {model_id} 时出错: {str(e)}")
                    return {"status": "error", "error": str(e)}, 500
        
        @ref_ns.route('/optimize')
        class RefOptimize(Resource):
        def post(self):
                """优化Ref系统"""
                if not ref_core_available:
                    return {"status": "unavailable", "error": "Ref核心模块不可用"}, 503
                
                try:
                    ref_core = get_ref_core()
                    success = ref_core.optimize_system()
                    
                    if success:
                    return {
                        "status": "success",
                            "message": "系统优化成功",
                        "timestamp": datetime.now().isoformat()
                    }
                    else:
                        return {
                            "status": "error",
                            "error": "系统优化失败",
                            "timestamp": datetime.now().isoformat()
                        }, 500
                    
                except Exception as e:
                    logger.error(f"优化系统时出错: {str(e)}")
                    return {"status": "error", "error": str(e)}, 500
        
        @ref_ns.route('/marker/add')
        class RefAddMarker(Resource):
            @ref_ns.expect(add_marker_model)
            def post(self):
                """添加量子基因标记"""
                if not ref_core_available:
                    return {"status": "unavailable", "error": "Ref核心模块不可用"}, 503
                
                try:
                    data = request.get_json()
                    
                    # 验证必要参数
                    if 'file_path' not in data:
                        return {"status": "error", "error": "缺少必要参数: file_path"}, 400
                    
                    file_path = data['file_path']
                    entangled_objects = data.get('entangled_objects', [])
                    strength = data.get('strength', 0.5)
                    
                    marker = get_gene_marker()
                    success = marker.add_marker(file_path, entangled_objects, strength)
                    
                    if success:
                        return {
                            "status": "success",
                            "message": f"量子基因标记添加成功: {file_path}",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"量子基因标记添加失败: {file_path}",
                            "timestamp": datetime.now().isoformat()
                        }, 500
                    
            except Exception as e:
                    logger.error(f"添加量子基因标记时出错: {str(e)}")
                    return {"status": "error", "error": str(e)}, 500
        
        @ref_ns.route('/marker/update')
        class RefUpdateMarker(Resource):
            @ref_ns.expect(update_marker_model)
            def post(self):
                """更新量子基因标记"""
                if not ref_core_available:
                    return {"status": "unavailable", "error": "Ref核心模块不可用"}, 503
                
                try:
                    data = request.get_json()
                    
                    # 验证必要参数
                    if 'file_path' not in data:
                        return {"status": "error", "error": "缺少必要参数: file_path"}, 400
                    
                    file_path = data['file_path']
                    entangled_objects = data.get('entangled_objects', [])
                    strength = data.get('strength', 0.5)
                    
                    marker = get_gene_marker()
                    success = marker.update_marker(file_path, entangled_objects, strength)
                    
                    if success:
                return {
                            "status": "success",
                            "message": f"量子基因标记更新成功: {file_path}",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"量子基因标记更新失败: {file_path}",
                            "timestamp": datetime.now().isoformat()
                        }, 500
                    
            except Exception as e:
                    logger.error(f"更新量子基因标记时出错: {str(e)}")
                    return {"status": "error", "error": str(e)}, 500
    
    return ref_ns
    
    except Exception as e:
        logger.error(f"创建Ref API命名空间时出错: {str(e)}")
        return None

# 创建API接口
app = Flask(__name__)
api = Api(app, 
    version='1.0', 
    title='Ref API',
    description='量子自反省系统API',
    doc='/swagger/'
)
ref_ns = create_ref_namespace(api)

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
    logger.info(f"处理Ref API请求: {path}")
    
    # 确保命名空间已创建
    if ref_ns is None:
        return jsonify({
            'status': 'error',
            'message': 'Ref API模块未正确初始化'
        }), 500
    
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

if __name__ == '__main__':
    # 启动独立服务
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=True, host='0.0.0.0', port=port)

"""
量子基因编码: QE-API-REF-3E7D8F9A
纠缠状态: 活跃
纠缠对象: ['api/ref_api/ref_api.py']
纠缠强度: 0.98
"""

# 开发团队：中华 ZhoHo，Claude
