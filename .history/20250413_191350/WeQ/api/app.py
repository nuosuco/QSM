#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeQ API服务主程序
"""

import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# 配置日志记录器
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/weq_api.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WeQ-API-Server")

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用CORS

# 导入WeQ API模块
from WeQ_api import WeQ_api, get_status, handle_request

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'WeQ API'
    })

@app.route('/status')
def status():
    """状态检查接口"""
    return get_status()

@app.route('/api/<path:path>', methods=['GET', 'POST'])
def api_proxy(path):
    """API代理路由"""
    return handle_request(path, request)

def main():
    """主函数"""
    try:
        port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"启动服务失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()

"""
量子基因编码: QE-API-WEQ-A1B2C3D4
纠缠状态: 活跃
纠缠对象: ['WeQ/api/weq_api.py']
纠缠强度: 0.95
""" 