#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆承载公众号文章采集器
作者：小蕊
日期：2026-08-13
"""

import sqlite3
import json
import time
import re
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

DB_PATH = '/root/SOM/data/wechat_articles/wodqbs/trading.db'
COLLECTION_DIR = '/root/SOM/data/wechat_articles/wodqbs'

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_existing(article_id):
    """检查文章是否已存在"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM articles WHERE article_id = ?", (article_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_article(article_data):
    """保存文章到数据库"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO articles 
            (article_id, title, author, publish_date, content, summary, 
             read_count, like_count, source, url, keywords, sentiment, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_data.get('article_id'),
            article_data.get('title', ''),
            article_data.get('author', '碧树西风'),
            article_data.get('publish_date', ''),
            article_data.get('content', ''),
            article_data.get('summary', ''),
            article_data.get('read_count', 0),
            article_data.get('like_count', 0),
            article_data.get('source', 'wechat'),
            article_data.get('url', ''),
            json.dumps(article_data.get('keywords', []), ensure_ascii=False),
            article_data.get('sentiment', ''),
            datetime.now().isoformat()
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def extract_keywords(text):
    """提取关键词"""
    keywords = []
    # 财经相关关键词
    finance_keywords = ['股票', '基金', '投资', '市场', '货币', '汇率', '黄金', '比特币', '加密货币']
    # 情绪相关关键词
    emotion_keywords = ['涨', '跌', '牛市', '熊市', '机会', '风险', '恐慌', '贪婪']
    
    for kw in finance_keywords + emotion_keywords:
        if kw in text:
            keywords.append(kw)
    return keywords[:10]  # 最多10个关键词

def scrape_article(url):
    """使用Playwright采集文章内容"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print(f"📄 正在访问: {url}")
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(3)
            
            # 提取内容
            title = page.title()
            content = page.inner_text('article') or page.inner_text('#js_content') or page.inner_text('body')
            
            # 提取日期
            date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', content)
            publish_date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}" if date_match else ""
            
            # 提取摘要
            summary_match = re.search(r'摘要[：:]\s*(.+)', content)
            summary = summary_match.group(1) if summary_match else content[:200]
            
            # 提取关键词
            keywords = extract_keywords(content)
            
            browser.close()
            
            return {
                'title': title,
                'content': content[:50000],  # 限制5万字
                'summary': summary[:500],
                'publish_date': publish_date,
                'keywords': keywords,
                'url': url
            }
        except Exception as e:
            print(f"❌ 采集失败: {e}")
            browser.close()
            return None

def collect_from_jintiankansha():
    """从今天看啥网站采集"""
    articles = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("🌐 访问今天看啥...")
            page.goto("http://www.jintiankansha.com/column/4k0SK6QY1U", wait_until="networkidle", timeout=30000)
            time.sleep(5)
            
            # 提取文章链接
            links = page.evaluate("""() => {
                const items = [];
                document.querySelectorAll('a').forEach(a => {
                    const href = a.href;
                    if (href && href.includes('mp.weixin.qq.com/s')) {
                        items.push(href);
                    }
                });
                return items;
            }""")
            
            print(f"✅ 找到 {len(links)} 篇文章链接")
            
            for link in links[:50]:  # 先采50篇测试
                if not check_existing(link):
                    print(f"📥 采集: {link}")
                    article_data = scrape_article(link)
                    if article_data:
                        article_data['article_id'] = link
                        save_article(article_data)
                        print(f"✅ 保存成功")
                    time.sleep(1)  # 避免请求过快
            
            browser.close()
            return len(links)
        except Exception as e:
            print(f"❌ 采集失败: {e}")
            browser.close()
            return 0

def collect_from_blog():
    """从jiyichengzai.com博客采集"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("🌐 访问个人博客...")
            page.goto("https://jiyichengzai.com/", wait_until="networkidle", timeout=30000)
            time.sleep(3)
            
            content = page.inner_text('body')[:10000]
            print(f"✅ 获取博客内容: {len(content)}字")
            
            # 保存为初始数据
            article_data = {
                'article_id': 'blog_intro',
                'title': '记忆承载·开号声明',
                'author': '碧树西风',
                'content': content,
                'source': 'blog',
                'url': 'https://jiyichengzai.com/'
            }
            save_article(article_data)
            
            browser.close()
            return True
        except Exception as e:
            print(f"❌ 博客采集失败: {e}")
            browser.close()
            return False

def get_stats():
    """获取采集统计"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM articles")
    total = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(DISTINCT source) as sources FROM articles")
    sources = cursor.fetchone()['sources']
    conn.close()
    return total, sources

def main():
    """主函数"""
    print("=" * 50)
    print("记忆承载公众号文章采集器")
    print("目标：采集4300+篇文章")
    print("=" * 50)
    
    # 1. 先采集博客
    print("\n📌 步骤1: 采集个人博客...")
    collect_from_blog()
    
    # 2. 从今天看啥采集
    print("\n📌 步骤2: 采集今天看啥...")
    count = collect_from_jintiankansha()
    
    # 3. 显示统计
    total, sources = get_stats()
    print(f"\n{'=' * 50}")
    print(f"✅ 当前已采集: {total} 篇文章")
    print(f"📊 数据来源: {sources} 个")
    print(f"🎯 目标总数: 4300+ 篇")
    print(f"📈 完成度: {total/4300*100:.1f}%")
    print(f"{'=' * 50}")
    
    # 4. 保存配置
    config = {
        'target_count': 4300,
        'current_count': total,
        'status': 'collecting',
        'last_update': datetime.now().isoformat()
    }
    with open(os.path.join(COLLECTION_DIR, 'config.json'), 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
