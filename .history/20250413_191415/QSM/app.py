#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子叠加态模型(QSM)服务器
提供Web界面和API访问量子叠加态模型功能
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, render_template, jsonify, send_from_directory, after_this_request, g, url_for, redirect, Blueprint

# 添加项目根目录到sys.path
parent_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(parent_dir, '..')))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qsm_server.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QSM-Server")

# 创建Flask应用
app = Flask(__name__, 
    template_folder='templates',  # 使用相对路径
    static_folder='static')

# 注册其他模板文件夹
world_templates = Blueprint('world_templates', __name__, 
                          template_folder=os.path.abspath('../world/templates'))
app.register_blueprint(world_templates)

# 配置
app.config.update(
    DEBUG=True,
    SECRET_KEY=os.urandom(24),
    TEMPLATES_AUTO_RELOAD=True,
    SEND_FILE_MAX_AGE_DEFAULT=0,  # 禁用静态文件缓存
    MODEL_NAME="QSM",
    RUN_MODE="integrated"  # 默认集成模式, 可设置为 "standalone"
)

# 禁用Jinja2缓存
app.jinja_env.cache = {}

# 导入并初始化路径解析器
try:
    from world.tools.path_resolver import init_app as init_path_resolver
    # 初始化路径解析器
    init_path_resolver(app)
    logger.info("路径解析器初始化成功")
except ImportError as e:
    logger.warning(f"无法导入路径解析器: {e}")

# 路由
@app.route('/')
def index():
    return render_template('index.html')

# 添加模块路由
@app.route('/QSM/')
def qsm_index():
    """QSM模块首页"""
    return render_template('index.html')

@app.route('/test_buttons')
def test_buttons():
    """测试按钮页面"""
    return render_template('test_buttons.html')

@app.route('/direct_demo')
def direct_demo():
    """直接演示页面"""
    return render_template('direct_demo.html')

@app.route('/hello')
def hello():
    """简单测试页面"""
    return "Hello, World! 你好，世界！"

@app.route('/simple')
def simple():
    """极简HTML页面"""
    return render_template('simple.html')

@app.route('/SOM/')
def som_index():
    """SOM模块首页"""
    # 独立模式下直接渲染自身的模板
    if app.config['RUN_MODE'] == "standalone":
        return render_template('SOM/index.html')
    # 集成模式下，不再重定向而是返回提示信息
    return "<h1>SOM模块</h1><p>当前处于集成模式，请通过主服务器访问: <a href='/SOM/'>主服务器SOM</a></p>"

@app.route('/WeQ/')
def weq_index():
    """WeQ模块首页"""
    # 独立模式下直接渲染自身的模板
    if app.config['RUN_MODE'] == "standalone":
        return render_template('WeQ/index.html')
    # 集成模式下，不再重定向而是返回提示信息
    return "<h1>WeQ模块</h1><p>当前处于集成模式，请通过主服务器访问: <a href='/WeQ/'>主服务器WeQ</a></p>"

@app.route('/Ref/')
def ref_index():
    """Ref模块首页"""
    # 独立模式下直接渲染自身的模板
    if app.config['RUN_MODE'] == "standalone":
        return render_template('Ref/index.html')
    # 集成模式下，不再重定向而是返回提示信息
    return "<h1>Ref模块</h1><p>当前处于集成模式，请通过主服务器访问: <a href='/Ref/'>主服务器Ref</a></p>"

@app.route('/quantum_test')
def quantum_test():
    """量子测试页面"""
    return render_template('quantum_test.html')

@app.route('/quantum_experience')
def quantum_experience():
    """量子体验页面"""
    return render_template('quantum_experience.html')

@app.route('/api_client')
def api_client():
    """API客户端页面"""
    return render_template('api_client.html')

# 全局静态文件服务
@app.route('/world/static/<path:path>')
def serve_global_static(path):
    """提供全局静态文件服务"""
    global_static_dir = os.path.abspath(os.path.join(parent_dir, '..', 'world', 'static'))
    return send_from_directory(global_static_dir, path)

# 添加world目录下的js文件服务
@app.route('/Ref/world/js/<path:path>')
def serve_ref_js(path):
    """提供Ref模型JavaScript文件服务"""
    ref_js_dir = os.path.abspath(os.path.join(parent_dir, '..', 'Ref', 'world', 'js'))
    return send_from_directory(ref_js_dir, path)

# 模型静态文件处理
@app.route('/static/<path:path>')
def serve_static(path):
    """提供模型静态文件服务"""
    return send_from_directory('static', path)

# 模型静态文件处理 - 与路径前缀匹配
@app.route('/QSM/static/<path:path>')
def serve_qsm_static(path):
    """提供QSM模型静态文件服务（带路径前缀）"""
    return send_from_directory('static', path)

# 在页面处理之前注入WebQuantum客户端
@app.before_request
def inject_web_quantum():
    """在每个响应中注入WebQuantum客户端脚本"""
    # 只处理HTML响应
    if request.path.endswith('.html') or not '.' in request.path:
        # 在实际响应中注入全局模板补丁脚本
        @after_this_request
        def add_web_quantum(response):
            if response.content_type and response.content_type.startswith('text/html'):
                inject_script = '<script src="/world/static/js/quantum_entanglement.js"></script>'
                response.data = response.data.replace(b'</head>', f'{inject_script}</head>'.encode())
            return response

# API路由
@app.route('/api/v1/status')
def api_status():
    """API状态检查"""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'webQuantum': True,
            'quantumEntanglement': True
        }
    })

# WebQuantum API路由
@app.route('/api/v1/quantum-registry', methods=['POST'])
def quantum_registry():
    """量子注册API - 处理WebQuantum客户端的注册请求"""
    try:
        data = request.json
        
        # 记录量子注册请求
        logger.info(f"收到量子注册请求: {data.get('deviceQuantumGene', 'unknown')}")
        
        # 模拟注册响应
        response = {
            'status': 'success',
            'message': '量子纠缠信道已建立',
            'timestamp': datetime.now().isoformat(),
            'channels': [
                {
                    'id': 'ch-' + os.urandom(4).hex(),
                    'type': 'quantum_entanglement',
                    'strength': 0.95,
                    'established': datetime.now().isoformat(),
                    'expires': None  # 永久信道
                }
            ]
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"处理量子注册请求时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '处理请求时出错',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"启动QSM服务器，端口: {port}, 模式: {app.config['RUN_MODE']}")
    app.run(host='0.0.0.0', port=port) 

"""
"""
量子基因编码: QE-APP-51E4C56A1A5D
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
