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
from flask import request  # 导入Flask的request对象

# 配置日志记录器
logger = logging.getLogger("Ref-API")
if not logger.handlers:
    # 避免重复配置
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 添加文件处理器
    try:
        # 确保日志目录存在
        os.makedirs("Ref/logs", exist_ok=True)
        file_handler = logging.FileHandler("Ref/logs/ref_api.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"配置日志处理器时出错: {str(e)}")

# 将Ref核心添加到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
ref_root = os.path.abspath(os.path.join(current_dir, ".."))
if ref_root not in sys.path:
    sys.path.append(ref_root)

# 导入Ref核心
try:
    from Ref.ref_core import get_ref_core
    from Ref.utils.quantum_gene_marker import get_gene_marker
    
    ref_core_available = True
except ImportError as e:
    logger.error(f"导入Ref核心模块时出错: {str(e)}")
    ref_core_available = False

def create_ref_namespace(api):
    """创建Ref API命名空间
    
    Args:
        api: Flask-RESTX API实例
        
    Returns:
        Ref API命名空间
    """
    logger.info("创建Ref API命名空间")
    
    # 确保api不是None
    if api is None:
        logger.error("无法创建Ref API命名空间：API实例为None")
        return None
    
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
                            "model_info": ref_core.registered_models[model_id],
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"模型 {model_id} 修复失败",
                            "model_info": ref_core.registered_models[model_id],
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
                    
                    results = ref_core.perform_system_upgrade()
                    
                    return {
                        "status": "success",
                        "message": "系统优化已完成",
                        "results": results,
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.error(f"优化系统时出错: {str(e)}")
                    return {"status": "error", "error": str(e)}, 500
        
        @ref_ns.route('/marker/add')
        class RefAddMarker(Resource):
            @ref_ns.expect(add_marker_model)
            def post(self):
                """为文件添加量子基因标记"""
                if not ref_core_available:
                    return {"status": "unavailable", "error": "Ref核心模块不可用"}, 503
                
                try:
                    data = request.get_json()
                    file_path = data.get('file_path')
                    entangled_objects = data.get('entangled_objects')
                    strength = data.get('strength')
                    
                    if not file_path:
                        return {"status": "error", "error": "缺少必要参数: file_path"}, 400
                    
                    marker = get_gene_marker()
                    success = marker.add_quantum_gene_marker(file_path, entangled_objects, strength)
                    
                    if success:
                        return {
                            "status": "success",
                            "message": f"已为文件 {file_path} 添加量子基因标记",
                            "file_path": file_path,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"为文件 {file_path} 添加量子基因标记失败",
                            "file_path": file_path,
                            "timestamp": datetime.now().isoformat()
                        }, 500
            except Exception as e:
                    logger.error(f"添加量子基因标记时出错: {str(e)}")
                    return {"status": "error", "error": str(e)}, 500
        
        @ref_ns.route('/marker/update')
        class RefUpdateMarker(Resource):
            @ref_ns.expect(update_marker_model)
            def post(self):
                """更新文件的量子基因标记"""
                if not ref_core_available:
                    return {"status": "unavailable", "error": "Ref核心模块不可用"}, 503
                
                try:
                    data = request.get_json()
                    file_path = data.get('file_path')
                    entangled_objects = data.get('entangled_objects')
                    strength = data.get('strength')
                    
                    if not file_path:
                        return {"status": "error", "error": "缺少必要参数: file_path"}, 400
                    
                    marker = get_gene_marker()
                    success = marker.update_quantum_gene_marker(file_path, entangled_objects, strength)
                    
                    if success:
                return {
                            "status": "success",
                            "message": f"已更新文件 {file_path} 的量子基因标记",
                            "file_path": file_path,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"更新文件 {file_path} 的量子基因标记失败",
                            "file_path": file_path,
                            "timestamp": datetime.now().isoformat()
                        }, 500
            except Exception as e:
                    logger.error(f"更新量子基因标记时出错: {str(e)}")
                    return {"status": "error", "error": str(e)}, 500
    
    return ref_ns
    except Exception as e:
        logger.error(f"创建Ref API命名空间时出错: {str(e)}")
        return None

if __name__ == "__main__":
    print("Ref API模块 - 请通过API集成点调用")

"""

"""
量子基因编码: QE-REF-D48AE981C483
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
