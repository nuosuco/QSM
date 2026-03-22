#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子系统REST API服务
提供HTTP API接口

功能：
1. 算法执行API
2. 状态查询API
3. 测试运行API
4. 报告生成API
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# 添加模块路径
sys.path.insert(0, '/root/QSM/QEntL/System/AgentHarness')


class QuantumAPIHandler(BaseHTTPRequestHandler):
    """量子API请求处理器"""
    
    # 类变量存储状态
    server_status = {
        'start_time': None,
        'requests_count': 0,
        'last_request': None
    }
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[API] {datetime.now().isoformat()} - {args[0]}")
    
    def _send_json_response(self, data: Dict, status: int = 200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
        
        # 更新统计
        QuantumAPIHandler.server_status['requests_count'] += 1
        QuantumAPIHandler.server_status['last_request'] = datetime.now().isoformat()
    
    def _send_html_response(self, html: str, status: int = 200):
        """发送HTML响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def do_GET(self):
        """处理GET请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # 路由处理
        if path == '/' or path == '/index':
            self._handle_index()
        elif path == '/api/status':
            self._handle_status()
        elif path == '/api/algorithms':
            self._handle_algorithms_list()
        elif path == '/api/modules':
            self._handle_modules_list()
        elif path == '/api/test':
            self._handle_test(query)
        elif path == '/api/health':
            self._handle_health()
        else:
            self._send_json_response({'error': 'Not Found'}, 404)
    
    def do_POST(self):
        """处理POST请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json_response({'error': 'Invalid JSON'}, 400)
            return
        
        # 路由处理
        if path == '/api/run':
            self._handle_run(data)
        elif path == '/api/report':
            self._handle_report(data)
        else:
            self._send_json_response({'error': 'Not Found'}, 404)
    
    def _handle_index(self):
        """处理首页"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>QSM量子系统API</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #2c3e50; }
        .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        code { background: #e0e0e0; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>QSM量子系统REST API</h1>
    <p>版本: 1.0.0</p>
    
    <h2>可用端点</h2>
    
    <div class="endpoint">
        <h3>GET /api/status</h3>
        <p>获取系统状态</p>
    </div>
    
    <div class="endpoint">
        <h3>GET /api/algorithms</h3>
        <p>列出可用算法</p>
    </div>
    
    <div class="endpoint">
        <h3>GET /api/modules</h3>
        <p>列出已加载模块</p>
    </div>
    
    <div class="endpoint">
        <h3>GET /api/test</h3>
        <p>运行系统测试</p>
    </div>
    
    <div class="endpoint">
        <h3>POST /api/run</h3>
        <p>执行量子算法</p>
        <p>参数: <code>{"algorithm": "grover", "n": 15}</code></p>
    </div>
    
    <div class="endpoint">
        <h3>GET /api/health</h3>
        <p>健康检查</p>
    </div>
    
    <hr>
    <p>中华Zhoho，小趣WeQ，GLM5</p>
</body>
</html>"""
        self._send_html_response(html)
    
    def _handle_status(self):
        """处理状态查询"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'system': 'QSM Quantum System',
            'version': '1.0.0',
            'status': 'running',
            'uptime_seconds': time.time() - QuantumAPIHandler.server_status['start_time'] if QuantumAPIHandler.server_status['start_time'] else 0,
            'requests_count': QuantumAPIHandler.server_status['requests_count'],
            'modules': {
                'qiskit': self._check_module('qiskit'),
                'numpy': self._check_module('numpy'),
                'scipy': self._check_module('scipy')
            }
        }
        
        # 获取Agent Harness模块数
        harness_dir = '/root/QSM/QEntL/System/AgentHarness'
        if os.path.exists(harness_dir):
            modules = [f for f in os.listdir(harness_dir) if f.endswith('.py') and not f.startswith('__')]
            status['agent_harness_modules'] = len(modules)
        
        self._send_json_response(status)
    
    def _check_module(self, name: str) -> bool:
        """检查模块是否可用"""
        try:
            __import__(name)
            return True
        except ImportError:
            return False
    
    def _handle_algorithms_list(self):
        """列出可用算法"""
        algorithms = [
            {'name': 'Grover搜索', 'id': 'grover', 'description': '量子搜索算法'},
            {'name': 'Shor因数分解', 'id': 'shor', 'description': '量子因数分解算法'},
            {'name': 'QFT', 'id': 'qft', 'description': '量子傅里叶变换'},
            {'name': '量子随机数', 'id': 'rng', 'description': '量子随机数生成器'},
            {'name': 'BB84密钥分发', 'id': 'bb84', 'description': '量子密钥分发协议'},
            {'name': 'VQE', 'id': 'vqe', 'description': '变分量子特征求解器'},
            {'name': 'QAOA', 'id': 'qaoa', 'description': '量子近似优化算法'}
        ]
        
        self._send_json_response({
            'algorithms': algorithms,
            'count': len(algorithms)
        })
    
    def _handle_modules_list(self):
        """列出已加载模块"""
        harness_dir = '/root/QSM/QEntL/System/AgentHarness'
        modules = []
        
        if os.path.exists(harness_dir):
            modules = [f[:-3] for f in os.listdir(harness_dir) 
                      if f.endswith('.py') and not f.startswith('__')]
        
        self._send_json_response({
            'modules': sorted(modules),
            'count': len(modules)
        })
    
    def _handle_test(self, query: Dict):
        """运行测试"""
        quick = query.get('quick', ['false'])[0].lower() == 'true'
        
        try:
            import quantum_integration_test as qit
            results = qit.run_integration_tests()
            
            self._send_json_response({
                'status': 'completed',
                'passed': results['summary']['passed'],
                'failed': results['summary']['failed'],
                'total': results['summary']['total'],
                'duration_seconds': results['summary']['duration_seconds']
            })
            
        except Exception as e:
            self._send_json_response({'error': str(e)}, 500)
    
    def _handle_health(self):
        """健康检查"""
        self._send_json_response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        })
    
    def _handle_run(self, data: Dict):
        """执行算法"""
        algorithm = data.get('algorithm', '').lower()
        n = data.get('n', 15)
        shots = data.get('shots', 1024)
        
        result = {'algorithm': algorithm, 'timestamp': datetime.now().isoformat()}
        
        try:
            if algorithm == 'grover':
                import quantum_simulator_integration as qsi
                integration = qsi.QuantumSimulatorIntegration()
                integration.initialize()
                algo_result = integration.run_grover_search(n)
                result['result'] = algo_result
                
            elif algorithm == 'shor':
                import shor_algorithm as shor
                shor_instance = shor.ShorAlgorithm()
                algo_result = shor_instance.factorize(n)
                result['result'] = algo_result
                
            elif algorithm == 'rng':
                import quantum_rng as qrng
                rng = qrng.QuantumRNG()
                random_num = rng.generate_random_number(0, n)
                result['result'] = {'random_number': random_num}
                
            elif algorithm == 'qft':
                import quantum_simulator_integration as qsi
                integration = qsi.QuantumSimulatorIntegration()
                integration.initialize()
                algo_result = integration.run_qft(n_qubits=3)
                result['result'] = algo_result
                
            else:
                return self._send_json_response({'error': f'Unknown algorithm: {algorithm}'}, 400)
            
            result['status'] = 'success'
            self._send_json_response(result)
            
        except Exception as e:
            self._send_json_response({'error': str(e), 'algorithm': algorithm}, 500)
    
    def _handle_report(self, data: Dict):
        """生成报告"""
        format_type = data.get('format', 'json')
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system': 'QSM Quantum System',
            'version': '1.0.0'
        }
        
        self._send_json_response(report)


class QuantumAPIServer:
    """量子API服务器"""
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.server = None
    
    def start(self):
        """启动服务器"""
        QuantumAPIHandler.server_status['start_time'] = time.time()
        
        self.server = HTTPServer((self.host, self.port), QuantumAPIHandler)
        
        print("=" * 60)
        print("QSM量子系统REST API服务")
        print("=" * 60)
        print(f"服务地址: http://{self.host}:{self.port}")
        print(f"API文档: http://{self.host}:{self.port}/")
        print("=" * 60)
        print("按 Ctrl+C 停止服务器")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")
            self.server.shutdown()
    
    def stop(self):
        """停止服务器"""
        if self.server:
            self.server.shutdown()


def start_api_server(host: str = '0.0.0.0', port: int = 8080):
    """启动API服务器"""
    server = QuantumAPIServer(host, port)
    server.start()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='QSM量子系统REST API服务')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=8080, help='监听端口')
    
    args = parser.parse_args()
    
    start_api_server(args.host, args.port)
