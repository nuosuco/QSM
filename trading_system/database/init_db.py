"""
交易系统数据库初始化
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = '/root/SOM/data/trading_system/trading.db'

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 策略表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            source_article_id INTEGER,
            source_title TEXT,
            keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 交易关键词表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trading_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE,
            article_count INTEGER DEFAULT 0,
            category TEXT
        )
    ''')
    
    # 交易平台配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_name TEXT UNIQUE,
            api_url TEXT,
            auth_type TEXT,
            status TEXT DEFAULT 'active',
            note TEXT
        )
    ''')
    
    # 交易记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_id INTEGER,
            product TEXT,
            direction TEXT,
            entry_price REAL,
            exit_price REAL,
            quantity INTEGER,
            profit_loss REAL,
            entry_time TIMESTAMP,
            exit_time TIMESTAMP,
            status TEXT DEFAULT 'closed',
            notes TEXT,
            FOREIGN KEY (strategy_id) REFERENCES strategies(id)
        )
    ''')
    
    # 绩效统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            total_trades INTEGER,
            winning_trades INTEGER,
            losing_trades INTEGER,
            win_rate REAL,
            total_profit REAL,
            max_drawdown REAL,
            sharpe_ratio REAL,
            balance REAL
        )
    ''')
    
    # 插入交易关键词
    keywords = [
        ('期货', 123, '期货交易'),
        ('股票', 743, '股票投资'),
        ('比特币', 60, '数字货币'),
        ('加密货币', 7, '数字货币'),
        ('量化', 423, '量化策略'),
        ('策略', 900, '综合'),
        ('交易系统', 240, '综合'),
        ('K线', 15, '技术分析'),
        ('技术分析', 10, '技术分析'),
        ('基本面', 114, '基本面分析'),
        ('波段', 89, '波段交易'),
        ('趋势', 399, '趋势跟踪'),
        ('止损', 235, '风险管理'),
        ('止盈', 60, '风险管理'),
        ('仓位', 241, '资金管理'),
        ('杠杆', 566, '风险管理'),
        ('保证金', 61, '风险管理'),
        ('套利', 376, '量化策略'),
        ('对冲', 407, '风险管理'),
        ('期权', 168, '衍生品'),
        ('衍生品', 19, '衍生品'),
        ('日内交易', 54, '日内交易'),
        ('资金流向', 14, '市场分析'),
        ('主力', 88, '市场分析'),
        ('散户', 431, '市场分析'),
        ('庄家', 102, '市场分析'),
        ('逃顶', 15, '技术分析'),
        ('抄底', 96, '技术分析'),
        ('平仓', 162, '风险管理'),
        ('持仓', 174, '风险管理')
    ]
    
    for kw in keywords:
        cursor.execute('''
            INSERT OR IGNORE INTO trading_keywords (keyword, article_count, category)
            VALUES (?, ?, ?)
        ''', kw)
    
    # 插入平台配置
    platforms = [
        ('期货交易', 'CTP接口', 'token', 'active', '公开可查'),
        ('股票交易', '券商API', 'oauth', 'active', '公开可查'),
        ('数字货币', '交易所API', 'key_secret', 'hidden', '仅自用')
    ]
    
    for platform in platforms:
        cursor.execute('''
            INSERT OR IGNORE INTO platform_configs (platform_name, api_url, auth_type, status, note)
            VALUES (?, ?, ?, ?, ?)
        ''', platform)
    
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成: {DB_PATH}")

if __name__ == '__main__':
    init_database()
