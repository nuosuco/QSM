#!/usr/bin/env python3
"""
记忆承载文章自动导入脚本
支持: rsmap.top API + GitHub仓库
"""
import sqlite3
import re
import os
import json
import requests
from datetime import datetime

DB_PATH = '/root/SOM/data/wechat_articles/wodqbs/trading.db'
DATA_DIR = '/root/SOM/data/wechat_articles/wodqbs'
LOG_FILE = f'{DATA_DIR}/import_log.json'

def init_db():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查并添加缺失列
    cursor.execute("PRAGMA table_info(articles)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'year' not in columns:
        cursor.execute("ALTER TABLE articles ADD COLUMN year TEXT")
    if 'date' not in columns:
        cursor.execute("ALTER TABLE articles ADD COLUMN date TEXT")
    if 'tags' not in columns:
        cursor.execute("ALTER TABLE articles ADD COLUMN tags TEXT")
    if 'status' not in columns:
        cursor.execute("ALTER TABLE articles ADD COLUMN status TEXT DEFAULT 'pending'")
    
    conn.commit()
    return conn

def log_import(source, count, status='success'):
    """记录导入日志"""
    log = {
        'timestamp': datetime.now().isoformat(),
        'source': source,
        'count': count,
        'status': status
    }
    
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            pass
    
    logs.append(log)
    
    if len(logs) > 100:
        logs = logs[-100:]
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    print(f"📝 日志已保存: {source} - {count}篇")

def import_rsmap_api():
    """从rsmap.top API导入文章"""
    conn = init_db()
    cursor = conn.cursor()
    
    print("\n===== 开始导入 rsmap.top API =====")
    
    try:
        resp = requests.get('https://rsmap.top/api/articles?limit=5', timeout=10)
        data = resp.json()
        print(f"✓ API正常，返回{len(data)}条")
    except Exception as e:
        print(f"✗ API访问失败: {e}")
        log_import('rsmap_top', 0, 'failed')
        conn.close()
        return
    
    all_articles = []
    for page in range(1, 50):
        try:
            resp = requests.get(f'https://rsmap.top/api/articles?limit=100&page={page}', timeout=10)
            data = resp.json()
            if not data:
                break
            for item in data:
                date = item.get('date', '')
                year = int(date[:4]) if date else 2026
                all_articles.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'date': date,
                    'year': str(year),
                    'source': 'rsmap_top',
                    'content': '',
                    'tags': item.get('tag', ''),
                    'article_id': item.get('id', '')
                })
            print(f"  第{page}页: {len(data)}条")
        except:
            print(f"  第{page}页失败")
            break
    
    if not all_articles:
        print("✗ 没有获取到数据")
        log_import('rsmap_top', 0, 'failed')
        conn.close()
        return
    
    # 去重
    seen = set(a['article_id'] for a in all_articles if a['article_id'])
    unique_articles = [a for a in all_articles if a['article_id'] in seen or not a['article_id']]
    unique_articles = all_articles[:len(seen)] if seen else all_articles
    print(f"去重后: {len(unique_articles)}篇")
    
    # 插入数据库
    batch_size = 500
    for i in range(0, len(unique_articles), batch_size):
        batch = unique_articles[i:i+batch_size]
        cursor.executemany('''
            INSERT OR IGNORE INTO articles (title, url, publish_date, year, source, content, keywords, article_id)
            VALUES (:title, :url, :date, :year, :source, :content, :tags, :article_id)
        ''', batch)
        print(f"导入批次 {i//batch_size + 1}: {len(batch)}篇")
    
    conn.commit()
    
    count = cursor.execute("SELECT COUNT(*) FROM articles WHERE source='rsmap_top'").fetchone()[0]
    print(f"✅ rsmap_top导入完成! 共{count}篇")
    log_import('rsmap_top', count)
    conn.close()

def import_github_wechat():
    """从GitHub wechat目录导入文章"""
    conn = init_db()
    cursor = conn.cursor()
    
    print("\n===== 开始导入 GitHub wechat 目录 =====")
    
    wechat_dir = f'{DATA_DIR}/sushengbuhuo_blog/docs/wechat/'
    if not os.path.exists(wechat_dir):
        print("✗ GitHub仓库未克隆")
        log_import('github_wechat', 0, 'failed')
        conn.close()
        return
    
    articles = []
    
    for filename in ['记忆承载公众号历史文章列表.md', '公众号记忆承载3历史文章.md']:
        filepath = os.path.join(wechat_dir, filename)
        if not os.path.exists(filepath):
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = r'\[(\d{4}-\d{2}-\d{2})_(.+?)\]\((http[^)]+)\)'
        matches = re.findall(pattern, content)
        
        for date, title, url in matches:
            year = int(date[:4])
            articles.append({
                'title': title.strip(),
                'url': url,
                'date': date,
                'year': str(year),
                'source': 'github_wechat',
                'content': '',
                'tags': filename,
                'article_id': ''
            })
        
        print(f"✓ {filename}: {len(matches)}篇")
    
    # 去重
    seen = set()
    unique_articles = []
    for art in articles:
        key = art['url']
        if key not in seen:
            seen.add(key)
            unique_articles.append(art)
    
    print(f"去重后: {len(unique_articles)}篇")
    
    # 检查已导入
    cursor.execute("SELECT COUNT(*) FROM articles WHERE source='github_wechat'")
    existing = cursor.fetchone()[0]
    
    if existing >= len(unique_articles):
        print("数据已是最新，跳过导入")
        conn.close()
        return
    
    # 插入数据库
    batch_size = 500
    for i in range(0, len(unique_articles), batch_size):
        batch = unique_articles[i:i+batch_size]
        cursor.executemany('''
            INSERT OR IGNORE INTO articles (title, url, publish_date, year, source, content, keywords, article_id)
            VALUES (:title, :url, :date, :year, :source, :content, :tags, :article_id)
        ''', batch)
        print(f"导入批次 {i//batch_size + 1}: {len(batch)}篇")
    
    conn.commit()
    
    count = cursor.execute("SELECT COUNT(*) FROM articles WHERE source='github_wechat'").fetchone()[0]
    print(f"✅ github_wechat导入完成! 共{count}篇")
    log_import('github_wechat', count)
    conn.close()

def get_stats():
    """打印数据库统计"""
    conn = init_db()
    cursor = conn.cursor()
    
    print("\n===== 📊 数据库统计 =====")
    print(f"总文章数: {cursor.execute('SELECT COUNT(*) FROM articles').fetchone()[0]}")
    print(f"\n【按年份分布】")
    cursor.execute("SELECT year, COUNT(*) as cnt FROM articles WHERE year IS NOT NULL AND year != 'unknown' GROUP BY year ORDER BY year")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}篇")
    print(f"\n【按来源分布】")
    cursor.execute("SELECT source, COUNT(*) as cnt FROM articles GROUP BY source ORDER BY cnt DESC")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}篇")
    
    conn.close()

if __name__ == '__main__':
    import_rsmap_api()
    import_github_wechat()
    get_stats()
