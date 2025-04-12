#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
量子系统API管理界面
提供API管理和监控功能
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, redirect, url_for, request

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/api_ui.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("API-UI")

# 获取项目根目录
root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 创建Flask应用
app = Flask(__name__, 
    static_folder=os.path.join(root_dir, 'static'),
    template_folder=os.path.join(root_dir, 'templates'))

# 配置
app.config.update(
    DEBUG=True,
    SECRET_KEY=os.urandom(24)
)

# 添加项目根目录到系统路径
sys.path.insert(0, root_dir)

# 主页
@app.route('/')
def index():
    """API管理主页"""
    try:
        return render_template('api/index.html')
    except Exception as e:
        logger.error(f"API管理主页加载错误: {str(e)}")
        return "API管理系统正在加载中...", 200

# API状态
@app.route('/status')
def api_status():
    """获取所有API的状态"""
    try:
        # 导入主API模块的状态函数
        from api.app import api_status as main_status
        from api.QSM_api.QSM_api import get_status as qsm_status
        from api.WeQ_api.WeQ_api import get_status as weq_status  
        from api.SOM_api.SOM_api import get_status as som_status
        from api.Ref_api.Ref_api import get_status as ref_status
        
        # 构建状态信息
        status_info = {
            'main_api': main_status().get_json(),
            'qsm_api': qsm_status().get_json(),
            'weq_api': weq_status().get_json(),
            'som_api': som_status().get_json(),
            'ref_api': ref_status().get_json(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status_info)
    except Exception as e:
        logger.error(f"获取API状态时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取API状态时出错: {str(e)}'
        }), 500

# 重定向到各个API的文档页面
@app.route('/docs/<api_name>')
def api_docs(api_name):
    """重定向到各个API的文档页面"""
    if api_name == 'qsm':
        return redirect('/api/qsm/swagger/')
    elif api_name == 'weq':
        return redirect('/api/weq/docs/')
    elif api_name == 'som':
        return redirect('/api/som/docs/')
    elif api_name == 'ref':
        return redirect('/api/ref/swagger/')
    else:
        return jsonify({
            'status': 'error',
            'message': f'未知的API: {api_name}'
        }), 404

# 测试页面
@app.route('/test')
def test_page():
    """API测试页面"""
    try:
        return render_template('api/test.html')
    except Exception as e:
        logger.error(f"API测试页面加载错误: {str(e)}")
        return "API测试页面正在开发中...", 200

# 监控页面
@app.route('/monitor')
def monitor_page():
    """API监控页面"""
    try:
        return render_template('api/monitor.html')
    except Exception as e:
        logger.error(f"API监控页面加载错误: {str(e)}")
        return "API监控页面正在开发中...", 200

if __name__ == '__main__':
    port = int(os.environ.get('UI_PORT', 5060))  # API UI服务器默认使用5060端口
    logger.info(f"启动API管理界面服务器，端口: {port}")
    app.run(debug=True, host='0.0.0.0', port=port)

"""
量子基因编码: QE-API-UI-1B3D5E7F
纠缠状态: 活跃
纠缠对象: ['api/app.py']
纠缠强度: 0.98
"""

# 开发团队：中华 ZhoHo，Claude 