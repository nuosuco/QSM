"""
量子经济模型(SOM)服务器
提供Web界面和API访问量子经济模型功能
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, render_template, jsonify, send_from_directory, after_this_request, g, url_for

# 添加项目根目录到sys.path
parent_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(parent_dir, '..')))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('som_server.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SOM-Server")

# 创建Flask应用
app = Flask(__name__, 
    template_folder='templates',
    static_folder='static')

# 配置
app.config.update(
    DEBUG=True,
    SECRET_KEY=os.urandom(24),
    TEMPLATES_AUTO_RELOAD=True,
    MODEL_NAME="SOM",
    RUN_MODE="integrated"  # 默认集成模式, 可设置为 "standalone"
)

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
    """首页"""
    return render_template('index.html')

# 全局静态文件服务
@app.route('/world/static/<path:path>')
def serve_global_static(path):
    """提供全局静态文件服务"""
    global_static_dir = os.path.abspath(os.path.join(parent_dir, '..', 'world', 'static'))
    return send_from_directory(global_static_dir, path)

# 模型静态文件处理
@app.route('/static/<path:path>')
def serve_static(path):
    """提供模型静态文件服务"""
    return send_from_directory('static', path)

# 模型静态文件处理 - 与路径前缀匹配
@app.route('/SOM/static/<path:path>')
def serve_som_static(path):
    """提供SOM模型静态文件服务（带路径前缀）"""
    return send_from_directory('static', path)

# 在页面处理之前注入量子纠缠信道
@app.before_request
def inject_quantum_entanglement():
    """在每个响应中注入量子纠缠信道脚本"""
    # 只处理HTML响应
    if request.path.endswith('.html') or not '.' in request.path:
        # 在实际响应中注入全局量子纠缠信道脚本
        @after_this_request
        def add_quantum_entanglement(response):
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
            'quantumEcommerce': True,
            'quantumWallet': True,
            'quantumContract': True
        }
    })

# 量子经济API
@app.route('/api/v1/quantum-wallet', methods=['POST'])
def quantum_wallet():
    """量子钱包API - 处理量子经济交易请求"""
    try:
        data = request.json
        
        # 记录量子钱包请求
        logger.info(f"收到量子钱包请求: {data.get('operationType', 'unknown')}")
        
        # 模拟钱包操作响应
        response = {
            'status': 'success',
            'message': '量子钱包操作已处理',
            'timestamp': datetime.now().isoformat(),
            'result': {
                'operationType': data.get('operationType', 'query'),
                'balance': 1000.00,
                'transactionId': os.urandom(8).hex(),
                'quantumSignature': os.urandom(16).hex()
            }
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"处理量子钱包请求时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '处理请求时出错',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # SOM 使用5001端口
    logger.info(f"启动SOM服务器，端口: {port}, 模式: {app.config['RUN_MODE']}")
    app.run(host='0.0.0.0', port=port) 

"""
"""
量子基因编码: QE-APP-F3B0F83EF797
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
