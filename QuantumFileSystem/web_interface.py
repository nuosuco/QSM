#!/usr/bin/env python3
"""
量子动态文件系统 - Web界面
版本: 0.1.0
描述: 基于Flask的Web管理界面

核心功能：
1. 文件浏览
2. 语义搜索
3. 知识图谱可视化
4. 系统状态监控
"""

import os
import json
from flask import Flask, render_template, request, jsonify
from pathlib import Path

# 创建Flask应用
app = Flask(__name__)

# 导入量子文件系统
try:
    from main_system import QuantumDynamicFileSystem
    qfs = QuantumDynamicFileSystem("./qfs_web")
    QFS_AVAILABLE = True
except ImportError:
    QFS_AVAILABLE = False
    print("⚠️ 量子文件系统模块未找到，运行在演示模式")

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/files')
def list_files():
    """列出所有文件"""
    if not QFS_AVAILABLE:
        return jsonify({"files": [], "message": "演示模式"})
    
    files = qfs.list_all_files()
    return jsonify({
        "files": files,
        "total": len(files)
    })

@app.route('/api/search')
def search():
    """搜索文件"""
    query = request.args.get('q', '')
    
    if not QFS_AVAILABLE:
        return jsonify({"results": [], "query": query})
    
    results = qfs.smart_search(query)
    return jsonify({
        "results": results,
        "query": query,
        "total": len(results)
    })

@app.route('/api/stats')
def stats():
    """系统统计"""
    if not QFS_AVAILABLE:
        return jsonify({
            "files": 0,
            "search_index": 0,
            "knowledge_nodes": 0
        })
    
    stats = qfs.get_system_stats()
    return jsonify({
        "files": stats['file_system'].get('total_files', 0),
        "search_index": stats['search_engine'].get('index_size', 0),
        "knowledge_nodes": stats['knowledge_network'].get('total_nodes', 0),
        "cache_hit_rate": stats['file_system'].get('cache_hit_rate', 0)
    })

@app.route('/api/file/<file_id>')
def file_detail(file_id):
    """文件详情"""
    if not QFS_AVAILABLE:
        return jsonify({"error": "演示模式"})
    
    knowledge = qfs.get_file_knowledge(file_id)
    return jsonify(knowledge)

# 创建HTML模板目录
templates_dir = Path(__file__).parent / 'templates'
templates_dir.mkdir(exist_ok=True)

# 写入HTML模板
INDEX_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>量子动态文件系统</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 30px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .header h1 {
            font-size: 2em;
            background: linear-gradient(90deg, #f2737, #f27ad);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: rgba(255,255,255,0.08);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #f27b0;
        }
        .search-box {
            margin-bottom: 20px;
        }
        .search-box input {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            background: rgba(255,255,255,0.1);
            color: #fff;
        }
        .search-box input:focus {
            outline: none;
            background: rgba(255,255,255,0.15);
        }
        .files-list {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            overflow: hidden;
        }
        .file-item {
            padding: 15px 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            cursor: pointer;
            transition: background 0.2s;
        }
        .file-item:hover {
            background: rgba(255,255,255,0.08);
        }
        .file-path {
            font-weight: 500;
            margin-bottom: 5px;
        }
        .file-meta {
            font-size: 0.85em;
            color: #888;
        }
        .quantum-badge {
            display: inline-block;
            padding: 2px 8px;
            background: linear-gradient(90deg, #f2737, #f27b0);
            border-radius: 10px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌟 量子动态文件系统</h1>
        <p style="margin-top:10px;opacity:0.7">v0.2.0 | 基于量子叠加态的新一代文件管理</p>
    </div>

    <div class="stats" id="stats">
        <div class="stat-card">
            <div class="stat-value" id="file-count">-</div>
            <div>文件总数</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="index-size">-</div>
            <div>搜索索引</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="node-count">-</div>
            <div>知识节点</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="cache-rate">-</div>
            <div>缓存命中率</div>
        </div>
    </div>

    <div class="search-box">
        <input type="text" id="search" placeholder="🔍 输入搜索内容（支持自然语言）..." onkeyup="handleSearch(event)">
    </div>

    <div class="files-list" id="files">
        <div class="file-item">加载中...</div>
    </div>

    <div class="footer">
        <p>量子动态文件系统 | 中华Zhoho | 小趣WeQ</p>
    </div>

    <script>
        // 加载统计数据
        function loadStats() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('file-count').textContent = data.files || 0;
                    document.getElementById('index-size').textContent = data.search_index || 0;
                    document.getElementById('node-count').textContent = data.knowledge_nodes || 0;
                    document.getElementById('cache-rate').textContent = 
                        (data.cache_hit_rate * 100).toFixed(0) + '%';
                });
        }

        // 加载文件列表
        function loadFiles() {
            fetch('/api/files')
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('files');
                    if (data.files.length === 0) {
                        container.innerHTML = '<div class="file-item">暂无文件</div>';
                        return;
                    }
                    container.innerHTML = data.files.map(f => `
                        <div class="file-item" onclick="showDetail('${f.file_id}')">
                            <div class="file-path">
                                📄 ${f.path}
                                <span class="quantum-badge">${f.quantum_state || '普通'}</span>
                            </div>
                            <div class="file-meta">
                                大小: ${f.size} bytes | 推荐: ${f.predicted_count} 个相关文件
                            </div>
                        </div>
                    `).join('');
                });
        }

        // 搜索处理
        function handleSearch(event) {
            if (event.key === 'Enter') {
                const query = document.getElementById('search').value;
                if (!query) {
                    loadFiles();
                    return;
                }
                fetch('/api/search?q=' + encodeURIComponent(query))
                    .then(r => r.json())
                    .then(data => {
                        const container = document.getElementById('files');
                        if (data.results.length === 0) {
                            container.innerHTML = '<div class="file-item">未找到匹配文件</div>';
                            return;
                        }
                        container.innerHTML = data.results.map(r => `
                            <div class="file-item">
                                <div class="file-path">📄 ${r.path}</div>
                                <div class="file-meta">
                                    相关度: ${(r.relevance * 100).toFixed(0)}% | 
                                    关键词: ${r.matched_keywords.join(', ')}
                                </div>
                            </div>
                        `).join('');
                    });
            }
        }

        // 显示文件详情
        function showDetail(fileId) {
            fetch('/api/file/' + fileId)
                .then(r => r.json())
                .then(data => {
                    alert(JSON.stringify(data, null, 2));
                });
        }

        // 初始化
        loadStats();
        loadFiles();
    </script>
</body>
</html>'''

# 写入模板文件
with open(templates_dir / 'index.html', 'w', encoding='utf-8') as f:
    f.write(INDEX_HTML)

def main():
    """启动Web服务器"""
    print("=" * 60)
    print("🌐 量子动态文件系统 - Web界面 v0.1.0")
    print("=" * 60)
    print("\n启动Web服务器...")
    print("访问地址: http://localhost:5000")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
