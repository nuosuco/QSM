#!/usr/bin/env python3
import sqlite3
import json
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

DB_PATH = '/root/SOM/data/wechat_articles/wodqbs/trading.db'
COLLECTION_DIR = '/root/SOM/data/wechat_articles/wodqbs/collection'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def collect_from_csdn():
    """从CSDN采集文章列表"""
    print("📚 尝试从CSDN采集...")
    # CSDN博客文章列表
    urls = [
        "https://blog.csdn.net/mysusheng/article/details/161973711",
        "https://blog.csdn.net/goodluck_2025/article/details/145529841"
    ]
    return urls

def collect_from_douban():
    """从豆瓣采集"""
    print("📚 尝试从豆瓣采集...")
    urls = [
        "https://www.douban.com/note/873628170/",
        "https://www.douban.com/note/847228049/"
    ]
    return urls

def main():
    print("=" * 50)
    print("记忆承载文章自动采集器")
    print("=" * 50)
    
    os.makedirs(COLLECTION_DIR, exist_ok=True)
    
    # 收集所有URL
    all_urls = collect_from_csdn() + collect_from_douban()
    print(f"\n找到 {len(all_urls)} 个数据源")
    
    for url in all_urls:
        print(f"\n🌐 访问: {url}")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)
                time.sleep(3)
                
                # 保存页面
                filename = url.replace("https://", "").replace("/", "_").replace(":", "_") + ".html"
                page.save_source(os.path.join(COLLECTION_DIR, filename))
                print(f"   ✅ 已保存: {filename}")
                
                browser.close()
        except Exception as e:
            print(f"   ❌ 失败: {e}")

if __name__ == "__main__":
    main()
