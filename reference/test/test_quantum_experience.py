#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子叠加体验模式功能测试脚本
此脚本验证量子体验相关的HTML、CSS和JavaScript功能是否正常运行
"""

import os
import time
import webbrowser
import http.server
import socketserver
import threading
from pathlib import Path
import sys

# 全局变量
BASE_URL = "http://localhost"
PORT = 5000
SERVER_THREAD = None
SERVER = None

def check_files_exist():
    """检查必要的文件是否存在"""
    required_files = [
        'QSM/templates/quantum_experience.html',
        'QSM/templates/js/quantum_experience.js',
        'QSM/templates/js/quantum_ui.js',
        'QSM/templates/css/quantum_experience.css'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return missing_files

def start_server():
    """启动一个简单的HTTP服务器来提供静态文件"""
    global SERVER, SERVER_THREAD
    
    # 定义处理程序
    handler = http.server.SimpleHTTPRequestHandler
    
    # 创建服务器
    SERVER = socketserver.TCPServer(("", PORT), handler)
    
    # 在单独的线程中启动服务器
    SERVER_THREAD = threading.Thread(target=SERVER.serve_forever)
    SERVER_THREAD.daemon = True
    SERVER_THREAD.start()
    
    print(f"服务器启动在 {BASE_URL}:{PORT}")
    return True

def stop_server():
    """停止HTTP服务器"""
    global SERVER
    if SERVER:
        SERVER.shutdown()
        SERVER.server_close()
        print("服务器已停止")

def open_experience_page():
    """打开量子体验页面"""
    url = f"{BASE_URL}/QSM/templates/quantum_experience.html"
    
    # 尝试打开浏览器
    if webbrowser.open(url):
        print(f"已在浏览器中打开: {url}")
        return True
    else:
        print(f"无法打开浏览器, 请手动访问: {url}")
        return False

def run_tests():
    """运行测试流程"""
    # 1. 检查文件是否存在
    missing_files = check_files_exist()
    if missing_files:
        print("错误: 以下文件不存在:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("所有必要文件已找到✓")
    
    # 2. 启动服务器
    if not start_server():
        print("错误: 无法启动服务器")
        return False
    
    # 3. 打开体验页面
    if not open_experience_page():
        print("警告: 无法自动打开浏览器")
    
    print("\n测试说明:")
    print("=================================")
    print("1. 验证界面是否正确加载")
    print("2. 测试环境状态区域的实时更新")
    print("3. 点击以下功能按钮测试交互:")
    print("   - 体验导航栏变化")
    print("   - 执行健康检查") 
    print("   - 启动并行处理")
    print("   - 量子可视化")
    print("   - 存储和检索量子状态")
    print("   - 创建量子纠缠信道")
    print("   - 启动量子爬虫")
    print("   - 重排量子面板")
    print("4. 在控制台执行 testQuantumExperience() 测试环境模拟")
    print("=================================")
    
    # 等待用户手动测试
    try:
        input("\n按下回车键停止服务器...")
    except KeyboardInterrupt:
        pass
    
    # 停止服务器
    stop_server()
    
    return True

def verify_javascript_syntax():
    """验证JavaScript文件的语法"""
    try:
        import subprocess
        
        js_files = [
            'QSM/templates/js/quantum_experience.js',
            'QSM/templates/js/quantum_ui.js'
        ]
        
        for js_file in js_files:
            if os.path.exists(js_file):
                print(f"验证 {js_file} 的语法...")
                
                # 使用Node.js来检查语法
                result = subprocess.run(
                    ['node', '--check', js_file], 
                    capture_output=True, 
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"✓ {js_file} 语法正确")
                else:
                    print(f"✗ {js_file} 语法错误:")
                    print(result.stderr)
                    return False
            else:
                print(f"✗ {js_file} 不存在")
                return False
                
        return True
    except Exception as e:
        print(f"验证过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    print("===== 量子体验功能测试 =====")
    
    # 切换到项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 验证JavaScript语法
    if verify_javascript_syntax():
        print("JavaScript语法验证通过✓")
    else:
        print("JavaScript语法验证失败✗")
        sys.exit(1)
    
    # 运行测试
    if run_tests():
        print("\n测试完成!")
    else:
        print("\n测试失败!")
        sys.exit(1) 

"""
"""
量子基因编码: QE-TES-4A0E6AB3A8C9
纠缠状态: 活跃
纠缠对象: ['test/test_common.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
