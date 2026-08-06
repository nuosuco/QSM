#!/usr/bin/env python3
"""
详细调试京东联盟API连接 - 尝试多个方法
"""
import hashlib
import time
import json
import requests
from datetime import datetime, timezone, timedelta

APP_KEY = "1c790ba72292dc6723a8145c3ac994f7"
APP_SECRET = "bbb6957c76224ca78db994daf03d90d5"
API_URL = "https://api.jd.com/routerjson"

def sign_request(params, secret):
    sorted_params = sorted(params.items())
    sign_str = secret + ''.join(f"{k}{v}" for k, v in sorted_params) + secret
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

def get_beijing_time():
    """获取北京时间（UTC+8）"""
    utc_now = datetime.now(timezone.utc)
    beijing_tz = timezone(timedelta(hours=8))
    beijing_now = utc_now.astimezone(beijing_tz)
    return beijing_now.strftime('%Y-%m-%d %H:%M:%S')

def call_jd_api(method, param_json, desc):
    print(f"\n--- 测试: {desc} ---")
    print(f"  方法: {method}")

    params = {
        'app_key': APP_KEY,
        'method': method,
        'timestamp': get_beijing_time(),  # 使用北京时间
        'format': 'json',
        'v': '1.0',
        'sign_method': 'md5',
        '360buy_param_json': json.dumps(param_json)
    }
    params['sign'] = sign_request(params, APP_SECRET)
    
    print(f"  时间戳: {params['timestamp']}")

    try:
        response = requests.post(API_URL, data=params, timeout=15)
        result = response.json()
        print(f"  完整响应: {json.dumps(result, ensure_ascii=False, indent=4)}")
        return result
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return None

# 测试1: 基础商品查询（新版接口）
call_jd_api(
    'jd.union.open.goods.query',
    {'goodsReq': {'keyword': '有机枸杞', 'pageSize': 1, 'pageIndex': 1}},
    '商品查询（新版）'
)

# 测试2: 大字段商品查询
call_jd_api(
    'jd.union.open.goods.bigfield.query',
    {'goodsReq': {'skuIds': [1]}},
    '大字段查询'
)

# 测试3: 获取推广链接
call_jd_api(
    'jd.union.open.promotion.common.get',
    {'promotionCodeReq': {'materialId': 'https://item.jd.com/1.html', 'siteId': '2035806496'}},
    '获取推广链接'
)

# 测试4: 订单查询
call_jd_api(
    'jd.union.open.order.row.query',
    {'orderReq': {'pageIndex': 1, 'pageSize': 1, 'type': 1, 'startTime': '2026-07-01 00:00:00', 'endTime': '2026-07-21 23:59:59'}},
    '订单查询'
)

# 测试5: 尝试旧版接口
call_jd_api(
    'jd.union.open.goods.jingfen.query',
    {'goodsReq': {'eliteId': 1, 'pageIndex': 1, 'pageSize': 1}},
    '京粉精选商品'
)

print("\n" + "=" * 50)
print("测试完成，请查看上面的响应结果")
print("=" * 50)
