#!/usr/bin/env python3
"""
SOM 松麦 - 商品缓存自动清理脚本
清理规则：
1. 超过 MAX_AGE_DAYS 天的商品（淘宝可能已下架）
2. 只有单张图片的商品（图片质量不达标）
3. click_url 为空的商品（无法跳转，无佣金）

计划任务：每天凌晨 4:30 执行
"""

import json
import sqlite3
import os
from datetime import datetime, timedelta

SERVER_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'server')
DB_PATH = os.path.join(SERVER_DIR, 'data', 'product_cache.db')

# 清理配置
MAX_AGE_DAYS = 30  # 超过30天的商品清理（淘宝商品更新快，老数据大概率已下架）
MIN_IMAGES = 2     # 至少2张图片（主图+多图数组），单图不要


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def count_images(images_json, main_image):
    """计算商品图片总数"""
    count = 0
    if main_image:
        count += 1
    try:
        imgs = json.loads(images_json) if images_json else []
        count += len(imgs)
    except (json.JSONDecodeError, TypeError):
        pass
    return count


def cleanup():
    print(f"\n{'='*50}")
    print(f"SOM商品缓存清理 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    if not os.path.exists(DB_PATH):
        print("缓存数据库不存在，跳过")
        return

    conn = get_db()
    cursor = conn.cursor()

    # 清理前统计
    total_before = cursor.execute('SELECT COUNT(*) FROM product_cache').fetchone()[0]
    print(f"清理前缓存总量: {total_before}")

    # 1. 清理超龄商品
    cutoff_date = (datetime.now() - timedelta(days=MAX_AGE_DAYS)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('DELETE FROM product_cache WHERE updated_at < ?', (cutoff_date,))
    aged_deleted = cursor.rowcount
    print(f"  超龄清理(>{MAX_AGE_DAYS}天): 删除 {aged_deleted} 条")

    # 2. 清理单图商品（逐条判断图片数量）
    rows = cursor.execute('SELECT item_id, main_image, images FROM product_cache').fetchall()
    single_img_ids = []
    for r in rows:
        if count_images(r['images'], r['main_image']) < MIN_IMAGES:
            single_img_ids.append(r['item_id'])

    if single_img_ids:
        # 分批删除，避免SQL参数过多
        batch_size = 500
        for i in range(0, len(single_img_ids), batch_size):
            batch = single_img_ids[i:i+batch_size]
            placeholders = ','.join('?' * len(batch))
            cursor.execute(f'DELETE FROM product_cache WHERE item_id IN ({placeholders})', batch)
    single_deleted = len(single_img_ids)
    print(f"  单图清理(<{MIN_IMAGES}张): 删除 {single_deleted} 条")

    # 3. 清理无跳转链接的商品
    cursor.execute("DELETE FROM product_cache WHERE click_url IS NULL OR click_url = ''")
    no_url_deleted = cursor.rowcount
    print(f"  无链接清理: 删除 {no_url_deleted} 条")

    conn.commit()

    # 清理后统计
    total_after = cursor.execute('SELECT COUNT(*) FROM product_cache').fetchone()[0]
    print(f"\n清理后缓存总量: {total_after}")
    print(f"本次共清理: {total_before - total_after} 条")
    print(f"{'='*50}\n")

    conn.close()


if __name__ == '__main__':
    cleanup()
