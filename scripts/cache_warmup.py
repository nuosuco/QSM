#!/usr/bin/env python3
"""
SOM 松麦 - 商品缓存预热脚本
按分类自动爬取淘宝商品，写入SQLite缓存，提高搜索响应速度
计划任务：每30分钟执行一次，爬取1-2个分类
"""

import json
import time
import hashlib
import requests
import sqlite3
import os
import sys
from datetime import datetime, timezone, timedelta

# 项目根目录
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_DIR = os.path.join(PROJECT_DIR, 'server')
sys.path.insert(0, SERVER_DIR)

DB_PATH = os.path.join(SERVER_DIR, 'data', 'product_cache.db')
CONFIG_PATH = os.path.join(SERVER_DIR, 'config.json')

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

TB_CONFIG = CONFIG['taobao']

# 排除关键词
EXCLUDE_KEYWORDS = [
    '书', '书籍', '教材', '课本', '图书', '文具', '笔记本', '笔', '本子',
    '化工', '化学', '试剂', '肥料', '农药', '化肥', '工业', '原料',
    '玩具', '模型', '手办', '乐高', '积木', '游戏', '桌游', '卡牌',
    '手机', '电脑', '平板', '耳机', '充电器', '数据线', '电子', '数码', '电器',
    '汽车', '轮胎', '机油', '车', '配件', '改装',
    '猫粮', '狗粮', '宠物', '猫砂',
    '塑料', '包装', '纸箱', '胶带',
]

# 搜索分类（精简版，覆盖主要品类）
CATEGORY_KEYWORDS = [
    '有机 枸杞 红枣',
    '有机 五谷杂粮 小米',
    '有机 菌菇 木耳',
    '有机 蜂蜜 调味品',
    '有机 茶 养生茶',
    '有机 坚果 核桃',
    '有机 山药 茯苓',
    '有机 百合 莲子',
    '有机 薏米 赤小豆',
    '有机 银耳 桂圆',
    '有机 黑芝麻 桑葚',
    '有机 艾草 足浴',
    '有机 棉 毛巾 床品',
    '有机 护肤品 面膜',
    '有机 洗发水 沐浴露',
    '有机 黄芪 当归 党参',
    '有机 新鲜 蔬菜 水果',
    '有机 母婴 辅食 奶粉',
    '有机 橄榄油 亚麻籽油',
    '有机 花草茶 玫瑰花',
    '有机 黑米 红米 糙米',
    '有机 红枣 桂圆 阿胶',
    '有机 足浴 泡脚 艾草',
    '有机 瑜伽 健身 器材',
    '有机 餐具 厨具 环保',
    '有机 棉 睡衣 内衣',
    '有机 护肤品 面膜 精油',
    '有机 竹纤维 麦秸秆',
    '有机 绿植 盆栽 花卉',
    '有机 艾灸 刮痧 拔罐',
    '有机 户外 露营 水杯',
    '有机 豆类 黄豆 黑豆',
    '有机 养生壶 煮茶器',
    '有机 纯露 精油 手工皂',
]


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_cache (
            item_id TEXT PRIMARY KEY,
            platform TEXT NOT NULL,
            title TEXT,
            price TEXT,
            main_image TEXT,
            images TEXT,
            shop_name TEXT,
            brand TEXT,
            category TEXT,
            commission_rate TEXT,
            click_url TEXT,
            sales TEXT,
            raw_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crawl_status (
            keyword TEXT PRIMARY KEY,
            platform TEXT DEFAULT 'taobao',
            page_crawled INTEGER DEFAULT 0,
            total_pages INTEGER DEFAULT 0,
            items_found INTEGER DEFAULT 0,
            last_crawled TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _sign_tb(params):
    sorted_params = sorted(params.items())
    sign_str = TB_CONFIG["app_secret"] + ''.join(f"{k}{v}" for k, v in sorted_params) + TB_CONFIG["app_secret"]
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()


def is_excluded(title):
    title_lower = (title or '').lower()
    for ex in EXCLUDE_KEYWORDS:
        if ex in title_lower:
            return True
    return False


def search_taobao(keyword, page=1, page_size=40):
    """淘宝联盟物料搜索"""
    params = {
        'app_key': TB_CONFIG["app_key"],
        'method': 'taobao.tbk.dg.material.optional.upgrade',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'format': 'json',
        'v': '2.0',
        'sign_method': 'md5',
        'adzone_id': TB_CONFIG["adzone_id"],
        'site_id': TB_CONFIG["site_id"],
        'q': keyword,
        'page_size': str(page_size),
        'page_no': str(page),
        'platform': '2',
    }
    params['sign'] = _sign_tb(params)

    try:
        resp = requests.get("https://eco.taobao.com/router/rest", params=params, timeout=10)
        result = resp.json()

        if 'error_response' in result:
            return []

        items = []
        for key in result:
            if key != 'error_response':
                data = result[key]
                if isinstance(data, dict) and 'result_list' in data:
                    items_data = data['result_list'].get('map_data', [])
                    for item in items_data:
                        basic = item.get('item_basic_info', {})
                        price_info = item.get('price_promotion_info', {})
                        publish = item.get('publish_info', {})
                        income = publish.get('income_info', {})

                        title = basic.get('short_title', '') or basic.get('title', '')
                        if is_excluded(title):
                            continue

                        click_url = publish.get('click_url', '')
                        if click_url.startswith('//'):
                            click_url = 'https:' + click_url

                        images = []
                        small_images = basic.get('small_images', {})
                        if small_images and 'string' in small_images:
                            images = small_images['string']
                        if not images and basic.get('pict_url'):
                            images = [basic.get('pict_url', '')]

                        items.append({
                            'item_id': item.get('item_id', ''),
                            'title': title,
                            'price': price_info.get('zk_final_price', '') or price_info.get('reserve_price', ''),
                            'main_image': basic.get('pict_url', ''),
                            'images': json.dumps(images),
                            'shop_name': basic.get('shop_title', ''),
                            'brand': basic.get('brand_name', ''),
                            'commission_rate': income.get('commission_rate', ''),
                            'click_url': click_url,
                            'sales': basic.get('volume', ''),
                            'category': basic.get('category_name', ''),
                            'raw_data': json.dumps(item, ensure_ascii=False),
                        })
        return items
    except Exception as e:
        print(f"  淘宝搜索失败: {e}")
        return []


def save_products(items, platform='taobao'):
    """保存商品到数据库"""
    conn = get_db()
    cursor = conn.cursor()
    saved = 0

    for item in items:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO product_cache 
                (item_id, platform, title, price, main_image, images, shop_name, brand,
                 category, commission_rate, click_url, sales, raw_data, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                item.get('item_id', ''),
                platform,
                item.get('title', ''),
                item.get('price', ''),
                item.get('main_image', ''),
                item.get('images', '[]'),
                item.get('shop_name', ''),
                item.get('brand', ''),
                item.get('category', ''),
                item.get('commission_rate', ''),
                item.get('click_url', ''),
                item.get('sales', ''),
                item.get('raw_data', ''),
            ))
            saved += 1
        except Exception as e:
            pass

    conn.commit()
    conn.close()
    return saved


def get_warmup_queue():
    """获取需要预热的关键词队列"""
    conn = get_db()
    cursor = conn.cursor()
    queue = []

    for kw in CATEGORY_KEYWORDS:
        cursor.execute('''
            SELECT status, last_crawled FROM crawl_status WHERE keyword = ?
        ''', (kw,))
        row = cursor.fetchone()

        if row:
            # 如果已爬取，检查是否过期（超过2小时）
            if row['last_crawled']:
                try:
                    last_time = datetime.strptime(row['last_crawled'], '%Y-%m-%d %H:%M:%S')
                    hours_ago = (datetime.now() - last_time).total_seconds() / 3600
                    if hours_ago < 2:
                        continue  # 2小时内已爬取，跳过
                except:
                    pass
            if row['status'] == 'completed':
                queue.append(kw)
        else:
            queue.append(kw)

    conn.close()
    return queue


def warmup_keyword(keyword, max_pages=2):
    """预热单个关键词"""
    print(f"  搜索: {keyword}")
    all_items = []
    seen_ids = set()

    for page in range(1, max_pages + 1):
        items = search_taobao(keyword, page)
        if not items:
            break

        for item in items:
            if item['item_id'] not in seen_ids:
                seen_ids.add(item['item_id'])
                all_items.append(item)

        print(f"    第{page}页: 找到{len(items)}个商品")
        time.sleep(0.5)  # 频率控制

    if all_items:
        saved = save_products(all_items)
        print(f"  保存: {saved}个商品")
    else:
        saved = 0

    # 更新状态
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO crawl_status 
        (keyword, platform, page_crawled, total_pages, items_found, last_crawled, status)
        VALUES (?, ?, ?, ?, ?, ?, 'completed')
    ''', (keyword, 'taobao', max_pages, max_pages, len(all_items), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

    return saved


def main():
    print(f"\n{'='*50}")
    print(f"SOM商品缓存预热 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    init_db()
    queue = get_warmup_queue()

    if not queue:
        print("所有关键词缓存已是最新，无需预热")
        return

    # 每次预热1-2个关键词
    batch = queue[:2]
    total_saved = 0

    for kw in batch:
        print(f"\n预热: {kw}")
        saved = warmup_keyword(kw, max_pages=2)
        total_saved += saved
        time.sleep(1)

    # 统计缓存总量
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM product_cache')
    total_cache = cursor.fetchone()[0]
    conn.close()

    print(f"\n本次预热完成: 处理{len(batch)}个关键词, 新增{total_saved}个商品")
    print(f"缓存总量: {total_cache}个商品")
    print(f"{'='*50}\n")


if __name__ == '__main__':
    main()