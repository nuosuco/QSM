#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子系统主服务器
集成模式下的请求分发器，将请求路由到各个子模型
"""

import os
import sys
import logging
import re
from datetime import datetime
from flask import Flask, request, render_template, jsonify, send_from_directory, redirect, url_for
from jinja2 import FileSystemLoader, Environment, TemplateNotFound
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quantum_server.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Quantum-Dispatcher")

# 获取绝对路径
root_dir = os.path.abspath(os.path.dirname(__file__))

# 创建Flask应用
app = Flask(__name__, 
    template_folder=root_dir,  # 使用项目根目录作为模板文件夹
    static_folder=os.path.join(root_dir, 'static'))

# 配置Jinja2模板环境
template_dirs = [
    os.path.join(root_dir, 'world', 'templates'),
    os.path.join(root_dir, 'QSM', 'templates'),
    os.path.join(root_dir, 'WeQ', 'templates'),
    os.path.join(root_dir, 'SOM', 'templates'),
    os.path.join(root_dir, 'Ref', 'templates'),
    root_dir  # 添加根目录以支持直接引用模块模板
]
app.jinja_env.loader = FileSystemLoader(template_dirs)

# 配置
app.config.update(
    DEBUG=True,
    SECRET_KEY=os.urandom(24),
    TEMPLATES_AUTO_RELOAD=True
)

# 导入子模型应用
sys.path.insert(0, root_dir)

# 确保quantum_economy可以被所有模型找到
logger.info(f"Python路径: {sys.path}")

# 全局静态文件服务
@app.route('/world/static/<path:path>')
def serve_global_static(path):
    """提供全局静态文件服务"""
    global_static_dir = os.path.join(root_dir, 'world', 'static')
    return send_from_directory(global_static_dir, path)

# QSM 静态文件
@app.route('/QSM/static/<path:path>')
def qsm_static(path):
    """提供QSM模型静态文件"""
    return send_from_directory(os.path.join(root_dir, 'QSM', 'static'), path)

# WeQ 静态文件
@app.route('/WeQ/static/<path:path>')
def weq_static(path):
    """提供WeQ模型静态文件"""
    return send_from_directory(os.path.join(root_dir, 'WeQ', 'static'), path)

# SOM 静态文件
@app.route('/SOM/static/<path:path>')
def som_static(path):
    """提供SOM模型静态文件"""
    return send_from_directory(os.path.join(root_dir, 'SOM', 'static'), path)

# Ref 静态文件
@app.route('/Ref/static/<path:path>')
def ref_static(path):
    """提供Ref模型静态文件"""
    return send_from_directory(os.path.join(root_dir, 'Ref', 'static'), path)

# 主页
@app.route('/')
def index():
    """主页"""
    try:
        return render_template('world/home.html')
    except Exception as e:
        logger.error(f"首页加载错误: {str(e)}")
        # 尝试备用模板
        try:
            return render_template('home.html')
        except Exception as e2:
            logger.error(f"备用首页加载错误: {str(e2)}")
            return "量子系统正在加载中...", 200

# QSM 路由代理
@app.route('/QSM/', defaults={'path': ''})
@app.route('/QSM/<path:path>')
def qsm_proxy(path):
    """QSM模型请求代理"""
    try:
        # 检查是否使用独立服务模式
        use_standalone = os.environ.get('STANDALONE_SERVICES', 'false').lower() == 'true'
        
        # 如果使用独立服务模式，则重定向
        if use_standalone:
            qsm_url = f"http://localhost:5000/{path}"
            return redirect(qsm_url)
            
        # 根据路径处理请求
        if not path:
            # 主页
            return render_template('QSM/templates/index.html')
        elif path == 'quantum_test':
            # 量子测试页面
            return render_template('QSM/templates/quantum_test.html')
        elif path == 'quantum_experience':
            # 量子体验页面
            return render_template('QSM/templates/quantum_experience.html')
        elif path == 'api_client':
            # API客户端页面
            return render_template('QSM/templates/api_client.html')
        elif path.startswith('api/'):
            # API请求
            from QSM.app import api_status
            return api_status()
        else:
            # 尝试渲染对应模板
            try:
                return render_template(f'QSM/templates/{path}.html')
            except Exception as e:
                logger.error(f"Template not found: {str(e)}")
                # 当模板不存在时返回404错误
                return jsonify({
                    'status': 'error',
                    'message': f'无法找到QSM页面: {path}'
                }), 404
    except Exception as e:
        logger.error(f"QSM请求处理出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'QSM模型请求处理出错',
            'error': str(e)
        }), 500

# WeQ 路由代理
@app.route('/WeQ/', defaults={'path': ''})
@app.route('/WeQ/<path:path>')
def weq_proxy(path):
    """WeQ模型请求代理"""
    try:
        # 检查是否使用独立服务模式
        use_standalone = os.environ.get('STANDALONE_SERVICES', 'false').lower() == 'true'
        
        # 如果使用独立服务模式，则重定向
        if use_standalone:
            weq_url = f"http://localhost:5003/{path}"
            return redirect(weq_url)
        
        # 根据路径处理请求
        if not path:
            # 主页
            return render_template('WeQ/templates/index.html')
        elif path == 'multimodal':
            # 多模态交互页面
            return render_template('WeQ/templates/weq_multimodal_demo.html')
        elif path.startswith('api/'):
            # API请求
            from WeQ.app import api_status
            return api_status()
        else:
            # 尝试渲染对应模板
            try:
                return render_template(f'WeQ/templates/{path}.html')
            except Exception as e:
                logger.error(f"Template not found: {str(e)}")
                # 当模板不存在时返回404错误
                return jsonify({
                    'status': 'error',
                    'message': f'无法找到WeQ页面: {path}'
                }), 404
    except Exception as e:
        logger.error(f"WeQ请求处理出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'WeQ模型请求处理出错',
            'error': str(e)
        }), 500

# SOM 路由代理
@app.route('/SOM/', defaults={'path': ''})
@app.route('/SOM/<path:path>')
def som_proxy(path):
    """SOM模型请求代理"""
    try:
        # 检查是否使用独立服务模式
        use_standalone = os.environ.get('STANDALONE_SERVICES', 'false').lower() == 'true'
        
        # 如果使用独立服务模式，则重定向
        if use_standalone:
            som_url = f"http://localhost:5001/{path}"
            return redirect(som_url)
        
        # 根据路径处理请求
        if not path:
            # 主页
            return render_template('SOM/templates/index.html')
        elif path == 'wallet' or path == 'quantum_wallet':
            # 钱包页面
            try:
                return render_template('SOM/templates/wallet.html')
            except Exception as e:
                logger.error(f"Wallet template not found: {str(e)}")
                # 如果页面不存在，返回开发中提示
                return '量子钱包页面正在开发中', 200
        elif path == 'market' or path == 'quantum_markets':
            # 市场页面
            try:
                return render_template('SOM/templates/market.html')
            except Exception as e:
                logger.error(f"Market template not found: {str(e)}")
                # 如果页面不存在，返回开发中提示
                return '量子市场页面正在开发中', 200
        elif path == 'contracts' or path == 'quantum_contracts':
            # 合约页面
            try:
                return render_template('SOM/templates/contracts.html')
            except Exception as e:
                logger.error(f"Contracts template not found: {str(e)}")
                # 如果页面不存在，返回开发中提示
                return '量子合约页面正在开发中', 200
        elif path.startswith('api/'):
            # API请求
            from SOM.app import api_status
            return api_status()
        else:
            # 尝试渲染对应模板
            try:
                return render_template(f'SOM/templates/{path}.html')
            except Exception as e:
                logger.error(f"Template not found: {str(e)}")
                # 当模板不存在时返回404错误
                return jsonify({
                    'status': 'error',
                    'message': f'无法找到SOM页面: {path}'
                }), 404
    except Exception as e:
        logger.error(f"SOM请求处理出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'SOM模型请求处理出错',
            'error': str(e)
        }), 500

# Ref 路由代理
@app.route('/Ref/', defaults={'path': ''})
@app.route('/Ref/<path:path>')
def ref_proxy(path):
    """Ref模型请求代理"""
    try:
        # 检查是否使用独立服务模式
        use_standalone = os.environ.get('STANDALONE_SERVICES', 'false').lower() == 'true'
        
        # 如果使用独立服务模式，则重定向
        if use_standalone:
            ref_url = f"http://localhost:5002/{path}"
            return redirect(ref_url)
        
        # 根据路径处理请求
        if not path:
            # 主页
            return render_template('Ref/templates/index.html')
        elif path == 'quantum_entanglement_comm':
            # 量子纠缠通信页面
            return render_template('Ref/templates/quantum_entanglement_comm.html')
        elif path == 'dashboard' or path == 'monitoring':
            # 系统监测页面
            try:
                return render_template('Ref/templates/monitoring.html')
    except Exception as e:
                logger.error(f"Monitoring template not found: {str(e)}")
                # 如果页面不存在，返回开发中提示
                return '系统监测页面正在开发中', 200
        elif path == 'self_reflection':
            # 自我反省页面
            try:
                return render_template('Ref/templates/self_reflection.html')
    except Exception as e:
                logger.error(f"Self reflection template not found: {str(e)}")
                # 如果页面不存在，返回开发中提示
                return '自我反省页面正在开发中', 200
        elif path.startswith('api/'):
            # API请求
            from Ref.app import api_status
            return api_status()
        else:
            # 尝试渲染对应模板
            try:
                return render_template(f'Ref/templates/{path}.html')
    except Exception as e:
                logger.error(f"Template not found: {str(e)}")
                # 当模板不存在时返回404错误
        return jsonify({
            'status': 'error',
                    'message': f'无法找到量子自反省模型页面: {path}'
                }), 404
    except Exception as e:
        logger.error(f"Ref请求处理出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '量子自反省模型请求处理出错',
            'error': str(e)
        }), 500

# 添加全局钩子，确保响应中包含量子纠缠脚本
@app.after_request
def add_quantum_entanglement_script(response):
    """在响应中添加量子纠缠脚本"""
    if response.content_type and response.content_type.startswith('text/html'):
        # 添加量子纠缠脚本到所有HTML响应
        quantum_script = '<script src="/world/static/js/quantum_entanglement.js"></script>'
        
        # 检查响应是否已经有该脚本
        if quantum_script.encode() not in response.data:
            response.data = response.data.replace(b'</head>', f'{quantum_script}</head>'.encode())
    
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # 主服务器使用5000端口
    logger.info(f"启动量子系统主服务器，端口: {port}")
    app.run(debug=True, host='0.0.0.0', port=port) 

"""
"""
量子基因编码: QE-APP-464C68B1FB1F
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
