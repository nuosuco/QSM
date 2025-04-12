#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子系统主API服务
集成模式下的请求分发器，将请求路由到各个子模型API
"""

import os
import sys
import logging
import re
from datetime import datetime
from flask import Flask, request, render_template, jsonify, send_from_directory, redirect, url_for
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/quantum_api_server.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Quantum-API-Dispatcher")

# 获取绝对路径
root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config.update(
    DEBUG=True,
    SECRET_KEY=os.urandom(24)
)

# 添加模块路径
sys.path.insert(0, root_dir)
logger.info(f"Python路径: {sys.path}")

# 检查独立服务模式
def is_standalone_mode():
    """检查是否使用独立服务模式"""
    return os.environ.get('STANDALONE_SERVICES', 'false').lower() == 'true'

# API状态检查
@app.route('/api/status')
def api_status():
    """API状态检查"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'mode': 'standalone' if is_standalone_mode() else 'integrated'
    })

# QSM API路由
@app.route('/api/qsm/', defaults={'path': ''})
@app.route('/api/qsm/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def qsm_api_proxy(path):
    """QSM模型API请求代理"""
    try:
        # 检查是否使用独立服务模式
        if is_standalone_mode():
            qsm_url = f"http://localhost:5000/api/{path}"
            return redirect(qsm_url)
            
        # 集成模式下的请求处理
        if not path:
            # API根路径，返回状态信息
            try:
                from QSM.api.qsm_api import get_status
                return get_status()
            except ImportError:
                # 如果模块未找到
                logger.warning("QSM API模块未找到，尝试从根目录API目录加载")
                try:
                    from api.QSM_api.QSM_api import get_status
                    return get_status()
                except ImportError:
                    logger.error("未能找到QSM API模块")
                    return jsonify({
                        'status': 'error',
                        'message': 'QSM API模块未找到'
                    }), 404
        else:
            # 将请求转发给QSM API模块
            try:
                # 尝试从QSM模块导入
                from QSM.api.qsm_api import handle_request
                return handle_request(path, request)
            except ImportError:
                # 如果模块未找到，尝试从根目录API目录加载
                try:
                    from api.QSM_api.QSM_api import handle_request
                    return handle_request(path, request)
                except ImportError:
                    logger.error("未能找到QSM API模块")
                    return jsonify({
                        'status': 'error',
                        'message': 'QSM API模块未找到'
                    }), 404
            except Exception as e:
                logger.error(f"QSM API请求处理出错: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({
                    'status': 'error',
                    'message': 'QSM API请求处理出错',
                    'error': str(e)
                }), 500
    except Exception as e:
        logger.error(f"QSM API代理出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': 'QSM API代理出错',
            'error': str(e)
        }), 500

# WeQ API路由
@app.route('/api/weq/', defaults={'path': ''})
@app.route('/api/weq/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def weq_api_proxy(path):
    """WeQ模型API请求代理"""
    try:
        # 检查是否使用独立服务模式
        if is_standalone_mode():
            weq_url = f"http://localhost:5003/api/{path}"
            return redirect(weq_url)
            
        # 集成模式下的请求处理
        if not path:
            # API根路径，返回状态信息
            try:
                from WeQ.api.weq_api import get_status
                return get_status()
            except ImportError:
                # 如果模块未找到
                logger.warning("WeQ API模块未找到，尝试从根目录API目录加载")
                try:
                    from api.WeQ_api.WeQ_api import get_status
                    return get_status()
                except ImportError:
                    logger.error("未能找到WeQ API模块")
                    return jsonify({
                        'status': 'error',
                        'message': 'WeQ API模块未找到'
                    }), 404
        else:
            # 将请求转发给WeQ API模块
            try:
                # 尝试从WeQ模块导入
                from WeQ.api.weq_api import handle_request
                return handle_request(path, request)
            except ImportError:
                # 如果模块未找到，尝试从根目录API目录加载
                try:
                    from api.WeQ_api.WeQ_api import handle_request
                    return handle_request(path, request)
                except ImportError:
                    logger.error("未能找到WeQ API模块")
                    return jsonify({
                        'status': 'error',
                        'message': 'WeQ API模块未找到'
                    }), 404
            except Exception as e:
                logger.error(f"WeQ API请求处理出错: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({
                    'status': 'error',
                    'message': 'WeQ API请求处理出错',
                    'error': str(e)
                }), 500
    except Exception as e:
        logger.error(f"WeQ API代理出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': 'WeQ API代理出错',
            'error': str(e)
        }), 500

# SOM API路由
@app.route('/api/som/', defaults={'path': ''})
@app.route('/api/som/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def som_api_proxy(path):
    """SOM模型API请求代理"""
    try:
        # 检查是否使用独立服务模式
        if is_standalone_mode():
            som_url = f"http://localhost:5001/api/{path}"
            return redirect(som_url)
            
        # 集成模式下的请求处理
        if not path:
            # API根路径，返回状态信息
            try:
                from SOM.api.som_api import get_status
                return get_status()
            except ImportError:
                # 如果模块未找到
                logger.warning("SOM API模块未找到，尝试从根目录API目录加载")
                try:
                    from api.SOM_api.SOM_api import get_status
                    return get_status()
                except ImportError:
                    logger.error("未能找到SOM API模块")
                    return jsonify({
                        'status': 'error',
                        'message': 'SOM API模块未找到'
                    }), 404
        else:
            # 将请求转发给SOM API模块
            try:
                # 尝试从SOM模块导入
                from SOM.api.som_api import handle_request
                return handle_request(path, request)
            except ImportError:
                # 如果模块未找到，尝试从根目录API目录加载
                try:
                    from api.SOM_api.SOM_api import handle_request
                    return handle_request(path, request)
                except ImportError:
                    logger.error("未能找到SOM API模块")
                    return jsonify({
                        'status': 'error',
                        'message': 'SOM API模块未找到'
                    }), 404
            except Exception as e:
                logger.error(f"SOM API请求处理出错: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({
                    'status': 'error',
                    'message': 'SOM API请求处理出错',
                    'error': str(e)
                }), 500
    except Exception as e:
        logger.error(f"SOM API代理出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': 'SOM API代理出错',
            'error': str(e)
        }), 500

# Ref API路由
@app.route('/api/ref/', defaults={'path': ''})
@app.route('/api/ref/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def ref_api_proxy(path):
    """Ref模型API请求代理"""
    try:
        # 检查是否使用独立服务模式
        if is_standalone_mode():
            ref_url = f"http://localhost:5002/api/{path}"
            return redirect(ref_url)
            
        # 集成模式下的请求处理
        if not path:
            # API根路径，返回状态信息
            try:
                from Ref.api.ref_api import get_status
                return get_status()
            except ImportError:
                # 如果模块未找到
                logger.warning("Ref API模块未找到，尝试从根目录API目录加载")
                try:
                    from api.Ref_api.Ref_api import get_status
                    return get_status()
                except ImportError:
                    logger.error("未能找到Ref API模块")
                    return jsonify({
                        'status': 'error',
                        'message': 'Ref API模块未找到'
                    }), 404
        else:
            # 将请求转发给Ref API模块
            try:
                # 尝试从Ref模块导入
                from Ref.api.ref_api import handle_request
                return handle_request(path, request)
            except ImportError:
                # 如果模块未找到，尝试从根目录API目录加载
                try:
                    from api.Ref_api.Ref_api import handle_request
                    return handle_request(path, request)
                except ImportError:
                    logger.error("未能找到Ref API模块")
                    return jsonify({
                        'status': 'error',
                        'message': 'Ref API模块未找到'
                    }), 404
            except Exception as e:
                logger.error(f"Ref API请求处理出错: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({
                    'status': 'error',
                    'message': 'Ref API请求处理出错',
                    'error': str(e)
                }), 500
    except Exception as e:
        logger.error(f"Ref API代理出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': 'Ref API代理出错',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('API_PORT', 5050))  # API服务器默认使用5050端口
    logger.info(f"启动量子系统主API服务器，端口: {port}")
    app.run(debug=True, host='0.0.0.0', port=port)

"""
量子基因编码: QE-API-F54A935C7B3D
纠缠状态: 活跃
纠缠对象: ['api/qsm_api/qsm_api.py', 'api/weq_api/weq_api.py', 'api/som_api/som_api.py', 'api/ref_api/ref_api.py']
纠缠强度: 0.98
"""

# 开发团队：中华 ZhoHo，Claude 