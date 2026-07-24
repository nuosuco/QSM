#!/usr/bin/env python3
"""
测试淘宝联盟API - 使用升级后的正确API方法名
"""
import hashlib
import time
import json

try:
    import requests
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

APP_KEY = "34975006"
APP_SECRET = "4bbf7dda72ea0a07bbac05005b46c75f"
ADZONE_ID = "115831100360"
SITE_ID = "3155250154"
API_URL = "https://eco.taobao.com/router/rest"

def sign_request(params, secret):
    sorted_params = sorted(params.items())
    sign_str = secret + ''.join(f"{k}{v}" for k, v in sorted_params) + secret
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

def call_api(method, extra_params, desc):
    print(f"\n--- 测试: {desc} ---")
    print(f"  方法: {method}")

    params = {
        'app_key': APP_KEY,
        'method': method,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'format': 'json',
        'v': '2.0',
        'sign_method': 'md5',
    }
    params.update(extra_params)
    params['sign'] = sign_request(params, APP_SECRET)

    try:
        response = requests.get(API_URL, params=params, timeout=15)
        result = response.json()

        if 'error_response' in result:
            error = result['error_response']
            code = error.get('code')
            msg = error.get('msg')
            sub_code = error.get('sub_code', '无')
            sub_msg = error.get('sub_msg', '无')
            print(f"  ❌ 错误码: {code} | {msg}")
            print(f"  子错误: {sub_code} | {sub_msg}")
            return False
        else:
            print(f"  ✅ 成功!")
            for key in result:
                if key != 'error_response':
                    data_str = json.dumps(result[key], ensure_ascii=False)
                    print(f"  返回: {data_str[:500]}")
            return True

    except Exception as e:
        print(f"  异常: {e}")
        return False

# 淘宝联盟API升级后的正确方法名：
# 16516 物料搜索 → taobao.tbk.dg.material.optional.upgrade (工具服务商) 
#                  或 taobao.tbk.dg.material.recommend (推广者)
# 16518 物料精选 → taobao.tbk.dg.material.recommend
# 18294 官方活动转链 → taobao.tbk.activity.info.get (新)
# 12340 长链转短链 → taobao.tbk.spread.get
# 11655 淘口令生成 → taobao.tbk.tpwd.create

# ===== 测试1: 物料搜索升级版（16516）=====
call_api(
    'taobao.tbk.dg.material.optional.upgrade',
    {
        'adzone_id': ADZONE_ID,
        'site_id': SITE_ID,
        'q': '有机枸杞',
        'page_size': '1',
        'platform': '2',
    },
    '物料搜索升级版（16516）'
)

# ===== 测试2: 物料精选升级版（16518）=====
call_api(
    'taobao.tbk.dg.material.recommend',
    {
        'adzone_id': ADZONE_ID,
        'site_id': SITE_ID,
        'material_id': '2802',
        'page_size': '1',
    },
    '物料精选升级版（16518）'
)

# ===== 测试3: 官方活动转链（18294）- 新方法名 =====
call_api(
    'taobao.tbk.activity.info.get',
    {
        'adzone_id': ADZONE_ID,
        'site_id': SITE_ID,
        'activity_material_id': '2802',
    },
    '官方活动转链（18294）- 新方法名'
)

# ===== 测试4: 长链转短链（12340）- 修正参数名 =====
call_api(
    'taobao.tbk.spread.get',
    {
        'request': json.dumps([{'url': 'https://item.taobao.com/item.htm?id=601803398371'}]),
    },
    '长链转短链（12340）- 修正参数'
)

# ===== 测试5: 淘口令生成（11655）=====
call_api(
    'taobao.tbk.tpwd.create',
    {
        'text': '松麦有机枸杞',
        'url': 'https://s.click.taobao.com/t?e=test',
        'adzone_id': ADZONE_ID,
        'site_id': SITE_ID,
    },
    '淘口令生成（11655）'
)

# ===== 测试6: 物料id列表查询 =====
call_api(
    'taobao.tbk.optimus.tou.material.ids.get',
    {
        'adzone_id': ADZONE_ID,
        'site_id': SITE_ID,
    },
    '物料id列表查询'
)

print("\n" + "=" * 50)
print("淘宝联盟API测试完成")
print("=" * 50)
