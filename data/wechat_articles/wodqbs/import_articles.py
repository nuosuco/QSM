#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆承载公众号文章批量导入器
将GitHub仓库中的md文件导入SQLite数据库
"""

import sqlite3
import os
import re
import json
from datetime import datetime
from pathlib import Path

DB_PATH = '/root/SOM/data/wechat_articles/wodqbs/trading.db'
ARTICLES_DIR = '/root/SOM/data/wechat_articles/wodqbs/BiShuXiFengArticle'

def init_db():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建文章表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT UNIQUE,
            title TEXT,
            author TEXT DEFAULT '碧树西风',
            publish_date TEXT,
            year TEXT,
            content TEXT,
            summary TEXT,
            source TEXT DEFAULT 'github',
            url TEXT,
            keywords TEXT,
            sentiment TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(publish_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_year ON articles(year)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)')
    
    conn.commit()
    return conn

def extract_date_from_title(title):
    """从标题提取日期信息"""
    date_match = re.search(r'(\d{4})[年\-](\d{1,2})[月\-](\d{1,2})', title)
    if date_match:
        return f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
    return ""

def extract_keywords(content):
    """提取关键词"""
    finance_keywords = [
        '股票', '基金', '投资', '市场', '货币', '汇率', '黄金', '比特币', 
        '加密货币', '经济', '政策', '财富', '钱', '赚钱', '亏损', '收益',
        '牛市', '熊市', '涨', '跌', '机会', '风险', '恐慌', '贪婪',
        '金融', '银行', '保险', '证券', '期货', '期权', '外汇',
        '创业', '商业', '公司', '企业', '老板', '员工', '工资'
    ]
    
    keywords = []
    for kw in finance_keywords:
        if kw in content:
            keywords.append(kw)
    return keywords[:10]

def analyze_sentiment(content):
    """分析情感倾向"""
    positive_words = ['涨', '牛', '机会', '希望', '成功', '盈利', '收益']
    negative_words = ['跌', '熊', '风险', '恐慌', '亏损', '倒闭', '危机']
    
    pos_count = sum(1 for w in positive_words if w in content)
    neg_count = sum(1 for w in negative_words if w in content)
    
    if pos_count > neg_count:
        return 'bullish'
    elif neg_count > pos_count:
        return 'bearish'
    return 'neutral'

def import_article(file_path, year):
    """导入单篇文章"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题（文件名去掉.md）
        title = os.path.basename(file_path).replace('.md', '')
        
        # 提取日期
        publish_date = extract_date_from_title(title)
        
        # 提取关键词
        keywords = extract_keywords(content)
        
        # 分析情感
        sentiment = analyze_sentiment(content)
        
        # 生成摘要（前200字）
        summary = content[:200] if len(content) > 200 else content
        
        # 生成唯一ID
        article_id = f"{year}-{title[:30]}"
        
        return {
            'article_id': article_id,
            'title': title,
            'publish_date': publish_date,
            'year': year,
            'content': content[:50000],  # 限制5万字
            'summary': summary,
            'source': 'github',
            'keywords': json.dumps(keywords, ensure_ascii=False),
            'sentiment': sentiment
        }
    except Exception as e:
        print(f"❌ 导入失败 {file_path}: {e}")
        return None

def main():
    print("=" * 50)
    print("记忆承载文章批量导入器")
    print("=" * 50)
    
    # 初始化数据库
    conn = init_db()
    cursor = conn.cursor()
    
    # 统计现有文章数
    cursor.execute("SELECT COUNT(*) FROM articles")
    existing_count = cursor.fetchone()[0]
    print(f"📊 现有文章: {existing_count} 篇")
    
    # 遍历所有年份目录
    imported = 0
    skipped = 0
    errors = 0
    
    for year_dir in sorted(Path(ARTICLES_DIR).iterdir()):
        if not year_dir.is_dir():
            continue
        
        year = year_dir.name
        print(f"\n📁 处理 {year}...")
        
        md_files = list(year_dir.glob("*.md"))
        print(f"   找到 {len(md_files)} 个md文件")
        
        for md_file in md_files:
            try:
                article_data = import_article(str(md_file), year)
                if article_data:
                    # 插入数据库
                    cursor.execute('''
                        INSERT OR IGNORE INTO articles 
                        (article_id, title, publish_date, year, content, summary, 
                         source, keywords, sentiment)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        article_data['article_id'],
                        article_data['title'],
                        article_data['publish_date'],
                        article_data['year'],
                        article_data['content'],
                        article_data['summary'],
                        article_data['source'],
                        article_data['keywords'],
                        article_data['sentiment']
                    ))
                    imported += 1
                    if imported % 100 == 0:
                        print(f"   已导入 {imported} 篇...")
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                print(f"   ❌ 错误: {e}")
    
    # 提交并关闭
    conn.commit()
    conn.close()
    
    # 显示结果
    print("\n" + "=" * 50)
    print("✅ 导入完成!")
    print(f"   新增: {imported} 篇")
    print(f"   跳过: {skipped} 篇")
    print(f"   错误: {errors} 篇")
    print(f"   总计: {existing_count + imported} 篇")
    print("=" * 50)

if __name__ == '__main__':
    main()
