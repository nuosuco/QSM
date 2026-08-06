#!/usr/bin/env python3
"""
测试淘宝和京东联盟API的完整功能
"""
import hashlib
import json
import time
import requests
from datetime import datetime, timezone, timedelta

# 淘宝配置
TB_APP_KEY = '34975006'
TB_APP_SECRET = '4bbf7dda72ea0a07bbac05005b46c75f'
TB_ADZONE_ID = '115831100360'
TB_SITE_ID = '3155250154'

# 京东配置
JD_APP_KEY = '1c790ba72292dc6723a8145c3ac994f7'
JD_APP_SECRET = 'bbb6957c76224ca78db994daf03d90d5'
JD_SITE_ID = '2035806496'


def tb_sign(params):
    """淘宝签名"""
    sorted_params = sorted(params.items())
    sign_str = TB_APP_SECRET + ''.join(f"{k}{v}" for k, v in sorted_params) + TB_APP_SECRET
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()


def jd_sign(params):
    """京东签名"""
    sorted_params = sorted(params.items())
    sign_str = JD_APP_SECRET + ''.join(f"{k}{v}" for k, v in sorted_params) + JD_APP_SECRET
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()


def get_beijing_time():
    """获取北京时间"""
    utc_now = datetime.now(timezone.utc)
    beijing_tz = timezone(timedelta(hours=8))
    return utc_now.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')


def test_taobao_search():
    """测试淘宝搜索"""
    print("\n=== 淘宝API测试 ===")
    print("1. 测试关键词搜索...")
    
    params = {
        'app_key': TB_APP_KEY,
        'method': 'taobao.tbk.dg.material.optional.upgrade',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'format': 'json',
        'v': '2.0',
        'sign_method': 'md5',
        'adzone_id': TB_ADZONE_ID,
        'site_id': TB_SITE_ID,
        'q': '有机枸杞',
        'page_size': '5',
        'page_no': '1',
        'platform': '2',
    }
    params['sign'] = tb_sign(params)
    
    try:
        resp = requests.get("https://eco.taobao.com/router/rest", params=params, timeout=10)
        result = resp.json()
        
        if 'error_response' in result:
            print(f"  ❌ 错误: {result['error_response'].get('sub_msg', result['error_response'].get('msg'))}")
            return None
        
        # 解析结果
        for key in result:
            if key != 'error_response':
                data = result[key]
                if isinstance(data, dict) and 'result_list' in data:
                    items = data['result_list'].get('map_data', [])
                    print(f"  ✅ 找到 {len(items)} 个商品")
                    
                    if items:
                        # 显示第一个商品的详细信息
                        item = items[0]
                        basic = item.get('item_basic_info', {})
                        promo = item.get('item_promotion_info', {})
                        
                        print(f"\n  示例商品:")
                        print(f"    标题: {basic.get('title', '')[:50]}")
                        print(f"    价格: ¥{promo.get('zk_final_price', '')}")
                        print(f"    佣金比例: {promo.get('commission_rate', '')}%")
                        print(f"    店铺: {basic.get('shop_title', '')}")
                        print(f"    商品ID: {basic.get('item_id', '')}")
                        
                        # 检查是否有推广链接
                        click_url = promo.get('click_url', '')
                        if click_url:
                            print(f"    推广链接: ✅ 有")
                        else:
                            print(f"    推广链接: ❌ 无")
                        
                        return items[0]
        return None
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return None


def test_taobao_detail():
    """测试淘宝商品详情"""
    print("\n2. 测试商品详情获取...")
    
    # 先搜索一个商品
    params = {
        'app_key': TB_APP_KEY,
        'method': 'taobao.tbk.dg.material.optional.upgrade',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'format': 'json',
        'v': '2.0',
        'sign_method': 'md5',
        'adzone_id': TB_ADZONE_ID,
        'site_id': TB_SITE_ID,
        'q': '红枣',
        'page_size': '1',
        'page_no': '1',
        'platform': '2',
    }
    params['sign'] = tb_sign(params)
    
    try:
        resp = requests.get("https://eco.taobao.com/router/rest", params=params, timeout=10)
        result = resp.json()
        
        item_id = None
        for key in result:
            if key != 'error_response':
                data = result[key]
                if isinstance(data, dict) and 'result_list' in data:
                    items = data['result_list'].get('map_data', [])
                    if items:
                        item_id = items[0].get('item_basic_info', {}).get('item_id')
        
        if not item_id:
            print("  ❌ 无法获取商品ID")
            return
        
        # 使用taobao.tbk.item.info.get获取详情
        params2 = {
            'app_key': TB_APP_KEY,
            'method': 'taobao.tbk.item.info.get',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'format': 'json',
            'v': '2.0',
            'sign_method': 'md5',
            'num_iids': str(item_id),
            'platform': '2',
        }
        params2['sign'] = tb_sign(params2)
        
        resp2 = requests.get("https://eco.taobao.com/router/rest", params=params2, timeout=10)
        result2 = resp2.json()
        
        if 'error_response' in result2:
            print(f"  ❌ 错误: {result2['error_response'].get('sub_msg', result2['error_response'].get('msg'))}")
        else:
            print(f"  ✅ 商品详情获取成功")
            # 解析详情
            for key in result2:
                if key != 'error_response':
                    data = result2[key]
                    if isinstance(data, dict) and 'results' in data:
                        items = data['results'].get('n_tbk_item', [])
                        if items:
                            item = items[0]
                            print(f"    标题: {item.get('title', '')[:50]}")
                            print(f"    价格: ¥{item.get('zk_final_price', '')}")
                            print(f"    描述: {item.get('item_description', '')[:50]}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")


def test_jd_search():
    """测试京东搜索"""
    print("\n=== 京东API测试 ===")
    print("1. 测试关键词搜索...")
    
    params = {
        'app_key': JD_APP_KEY,
        'method': 'jd.union.open.goods.query',
        'timestamp': get_beijing_time(),
        'format': 'json',
        'v': '1.0',
        'sign_method': 'md5',
        '360buy_param_json': json.dumps({
            'goodsReq': {
                'keyword': '有机枸杞',
                'pageSize': 5,
                'pageIndex': 1,
            }
        })
    }
    params['sign'] = jd_sign(params)
    
    try:
        resp = requests.post("https://api.jd.com/routerjson", data=params, timeout=10)
        result = resp.json()
        
        if 'error_response' in result:
            error = result['error_response']
            print(f"  ❌ 错误: {error.get('zh_desc', error.get('error_msg'))}")
            return None
        
        resp_key = 'jd_union_open_goods_query_response'
        if resp_key in result:
            data = result[resp_key]
            if 'result' in data:
                result_data = json.loads(data['result'])
                goods_list = result_data.get('data', [])
                print(f"  ✅ 找到 {len(goods_list)} 个商品")
                
                if goods_list:
                    item = goods_list[0]
                    print(f"\n  示例商品:")
                    print(f"    标题: {item.get('skuName', '')[:50]}")
                    print(f"    价格: ¥{item.get('priceInfo', {}).get('price', '')}")
                    print(f"    佣金比例: {item.get('commissionInfo', {}).get('commissionShare', 0)}%")
                    print(f"    店铺: {item.get('shopInfo', {}).get('shopName', '')}")
                    print(f"    商品ID: {item.get('skuId', '')}")
                    
                    material_url = item.get('materialUrl', '')
                    if material_url:
                        print(f"    推广链接: ✅ 有")
                    else:
                        print(f"    推广链接: ❌ 无")
                    
                    return goods_list[0]
        return None
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return None


def test_jd_detail():
    """测试京东商品详情"""
    print("\n2. 测试商品详情获取...")
    
    # 先搜索一个商品
    params = {
        'app_key': JD_APP_KEY,
        'method': 'jd.union.open.goods.query',
        'timestamp': get_beijing_time(),
        'format': 'json',
        'v': '1.0',
        'sign_method': 'md5',
        '360buy_param_json': json.dumps({
            'goodsReq': {
                'keyword': '红枣',
                'pageSize': 1,
                'pageIndex': 1,
            }
        })
    }
    params['sign'] = jd_sign(params)
    
    try:
        resp = requests.post("https://api.jd.com/routerjson", data=params, timeout=10)
        result = resp.json()
        
        sku_id = None
        resp_key = 'jd_union_open_goods_query_response'
        if resp_key in result:
            data = result[resp_key]
            if 'result' in data:
                result_data = json.loads(data['result'])
                goods_list = result_data.get('data', [])
                if goods_list:
                    sku_id = goods_list[0].get('skuId')
        
        if not sku_id:
            print("  ❌ 无法获取商品ID")
            return
        
        # 使用jd.union.open.goods.bigfield.query获取详情
        params2 = {
            'app_key': JD_APP_KEY,
            'method': 'jd.union.open.goods.bigfield.query',
            'timestamp': get_beijing_time(),
            'format': 'json',
            'v': '1.0',
            'sign_method': 'md5',
            '360buy_param_json': json.dumps({
                'goodsReq': {
                    'skuIds': [sku_id]
                }
            })
        }
        params2['sign'] = jd_sign(params2)
        
        resp2 = requests.post("https://api.jd.com/routerjson", data=params2, timeout=10)
        result2 = resp2.json()
        
        if 'error_response' in result2:
            print(f"  ❌ 错误: {result2['error_response'].get('zh_desc', result2['error_response'].get('error_msg'))}")
        else:
            print(f"  ✅ 商品详情获取成功")
            resp_key2 = 'jd_union_open_goods_bigfield_query_response'
            if resp_key2 in result2:
                data2 = result2[resp_key2]
                if 'result' in data2:
                    result_data2 = json.loads(data2['result'])
                    items = result_data2.get('data', [])
                    if items:
                        item = items[0]
                        print(f"    标题: {item.get('skuName', '')[:50]}")
                        print(f"    描述: {item.get('desc', '')[:50]}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")


if __name__ == '__main__':
    print("=" * 60)
    print("SOM松麦 - 淘宝京东联盟API完整功能测试")
    print("=" * 60)
    
    # 淘宝测试
    tb_item = test_taobao_search()
    test_taobao_detail()
    
    # 京东测试
    jd_item = test_jd_search()
    test_jd_detail()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
