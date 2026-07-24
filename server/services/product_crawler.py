"""
SOM 松麦 - 商品详情爬虫+数据库缓存模块
淘宝/京东商品详情爬取，存入SQLite数据库，支持缓存查询
"""

import json
import time
import hashlib
import requests
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from bs4 import BeautifulSoup

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'product_cache.db')

# 从config.json读取配置
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

TB_CONFIG = CONFIG['taobao']
JD_CONFIG = CONFIG['jd']


def init_db():
    """初始化数据库，创建表"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 商品详情缓存表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_cache (
            item_id TEXT PRIMARY KEY,
            platform TEXT NOT NULL,
            title TEXT,
            price TEXT,
            main_image TEXT,
            images TEXT,  -- JSON数组，多张图片
            shop_name TEXT,
            brand TEXT,
            category TEXT,
            commission_rate TEXT,
            click_url TEXT,
            desc_text TEXT,  -- 商品描述文本
            params TEXT,  -- JSON，规格参数
            detail_images TEXT,  -- JSON数组，详情描述图
            sales TEXT,  -- 销量
            raw_data TEXT,  -- 原始API返回数据
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 爬虫状态表
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
    print(f"数据库初始化完成: {DB_PATH}")


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _sign_tb(params: dict) -> str:
    """淘宝联盟MD5签名"""
    sorted_params = sorted(params.items())
    sign_str = TB_CONFIG["app_secret"] + ''.join(f"{k}{v}" for k, v in sorted_params) + TB_CONFIG["app_secret"]
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()


def search_taobao(keyword: str, page: int = 1, page_size: int = 40) -> List[dict]:
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
            print(f"淘宝API错误: {result['error_response']}")
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
                        
                        click_url = publish.get('click_url', '')
                        if click_url.startswith('//'):
                            click_url = 'https:' + click_url
                        
                        # 获取多张图片
                        images = []
                        small_images = basic.get('small_images', {})
                        if small_images and 'string' in small_images:
                            images = small_images['string']
                        if not images and basic.get('pict_url'):
                            images = [basic.get('pict_url', '')]
                        
                        items.append({
                            'item_id': item.get('item_id', ''),
                            'title': basic.get('short_title', '') or basic.get('title', ''),
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
        print(f"淘宝搜索失败: {e}")
        return []


def get_taobao_item_detail(item_id: str) -> Optional[dict]:
    """通过淘宝移动端API获取商品详情"""
    try:
        # 淘宝移动端API
        url = f"https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/"
        params = {
            'data': json.dumps({
                'id': item_id,
                'itemNumId': item_id,
                'exParams': '{"id": "%s"}' % item_id,
            })
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
            'Referer': 'https://item.taobao.com/',
        }
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        
        if data.get('ret') and 'SUCCESS' in str(data['ret']):
            item_data = data.get('data', {})
            # 提取详情图片
            detail_images = []
            desc_info = item_data.get('descInfo', {})
            if desc_info.get('descUrl'):
                # 详情页URL，需要进一步获取
                pass
            
            # 提取规格参数
            props = item_data.get('props', [])
            
            # 提取多张商品图片
            images = []
            item_info = item_data.get('itemInfo', {})
            if item_info.get('images'):
                images = item_info['images']
            
            return {
                'images': json.dumps(images[:10]),  # 最多10张
                'detail_images': json.dumps(detail_images),
                'params': json.dumps(props[:50]),  # 最多50个参数
                'desc_text': item_data.get('descInfo', {}).get('desc', ''),
            }
    except Exception as e:
        print(f"获取淘宝详情失败: {e}")
    
    return None


def save_product(items: List[dict], platform: str = 'taobao'):
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
            print(f"保存商品失败 {item.get('item_id')}: {e}")
    
    conn.commit()
    conn.close()
    return saved


def get_cached_product(item_id: str) -> Optional[dict]:
    """从缓存获取商品详情"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM product_cache WHERE item_id = ?', (item_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def crawl_category(keywords: List[str], platform: str = 'taobao', max_pages: int = 3):
    """爬取一个分类的所有商品"""
    all_items = []
    seen_ids = set()
    
    for keyword in keywords:
        search_kw = f"有机 {keyword}"
        print(f"  搜索: {search_kw}")
        
        for page in range(1, max_pages + 1):
            items = search_taobao(search_kw, page)
            if not items:
                break
            
            for item in items:
                if item['item_id'] not in seen_ids:
                    seen_ids.add(item['item_id'])
                    all_items.append(item)
            
            print(f"    第{page}页: 找到{len(items)}个商品")
            time.sleep(1)  # 每秒1个，避免被封
    
    # 保存到数据库
    saved = save_product(all_items, platform)
    print(f"  共保存{saved}个商品")
    return all_items


def update_crawl_status(keyword: str, platform: str, page_crawled: int, total_pages: int, items_found: int):
    """更新爬虫状态"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO crawl_status 
        (keyword, platform, page_crawled, total_pages, items_found, last_crawled, status)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 'completed')
    ''', (keyword, platform, page_crawled, total_pages, items_found))
    conn.commit()
    conn.close()


def get_crawl_queue() -> List[dict]:
    """获取待爬取的分类队列"""
    # 从shop.py读取分类
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server'))
    from services.shop import ShopService
    
    # 获取分类列表
    shop = ShopService()
    categories = shop.get_categories()
    
    conn = get_db()
    cursor = conn.cursor()
    queue = []
    
    for cat in categories:
        cursor.execute('SELECT status FROM crawl_status WHERE keyword = ?', (cat['keyword'],))
        row = cursor.fetchone()
        if not row or row['status'] != 'completed':
            queue.append(cat)
    
    conn.close()
    return queue


def crawl_all():
    """爬取所有分类的商品（主入口）"""
    print("=" * 50)
    print(f"SOM商品爬虫 - {datetime.now()}")
    print("=" * 50)
    
    init_db()
    queue = get_crawl_queue()
    
    if not queue:
        print("所有分类已爬取完成！")
        return
    
    print(f"待爬取分类: {len(queue)}个")
    
    for i, cat in enumerate(queue):
        print(f"\n[{i+1}/{len(queue)}] 分类: {cat['name']}")
        print(f"  关键词: {cat['keyword']}")
        
        keywords = cat['keyword'].split()
        items = crawl_category(keywords, 'taobao', max_pages=3)
        
        # 更新状态
        update_crawl_status(cat['keyword'], 'taobao', 3, 3, len(items))
        
        print(f"  完成: {len(items)}个商品")
        time.sleep(2)  # 分类间间隔
    
    print("\n" + "=" * 50)
    print("爬取完成！")
    print("=" * 50)


def get_product_detail(item_id: str) -> dict:
    """获取商品详情（优先从缓存，缓存未命中则爬取）"""
    # 先从缓存查
    cached = get_cached_product(item_id)
    if cached:
        return {
            'item_id': cached['item_id'],
            'title': cached['title'],
            'price': cached['price'],
            'main_image': cached['main_image'],
            'images': json.loads(cached['images']) if cached['images'] else [],
            'shop_name': cached['shop_name'],
            'brand': cached['brand'],
            'commission_rate': cached['commission_rate'],
            'click_url': cached['click_url'],
            'sales': cached['sales'],
            'detail_images': json.loads(cached['detail_images']) if cached.get('detail_images') else [],
            'params': json.loads(cached['params']) if cached.get('params') else [],
            'desc_text': cached.get('desc_text', ''),
            'from_cache': True,
        }
    
    # 缓存未命中，尝试实时获取详情
    detail = get_taobao_item_detail(item_id)
    if detail:
        return {
            'images': json.loads(detail.get('images', '[]')),
            'detail_images': json.loads(detail.get('detail_images', '[]')),
            'params': json.loads(detail.get('params', '[]')),
            'desc_text': detail.get('desc_text', ''),
            'from_cache': False,
        }
    
    return {
        'images': [],
        'detail_images': [],
        'params': [],
        'desc_text': '',
        'from_cache': False,
    }


if __name__ == '__main__':
    crawl_all()