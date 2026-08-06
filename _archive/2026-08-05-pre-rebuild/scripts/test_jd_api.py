#!/usr/bin/env python3
"""
测试京东联盟API连接
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

APP_KEY = "1c790ba72292dc6723a8145c3ac994f7"
APP_SECRET = "bbb6957c76224ca78db994daf03d90d5"
SITE_ID = "2035806496"
API_URL = "https://api.jd.com/routerjson"

def sign_request(params, secret):
    """京东联盟MD5签名"""
    sorted_params = sorted(params.items())
    sign_str = secret + ''.join(f"{k}{v}" for k, v in sorted_params) + secret
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

def test_jd():
    print("=" * 50)
    print("测试京东联盟API连接")
    print("=" * 50)

    params = {
        'app_key': APP_KEY,
        'method': 'jd.union.open.goods.query',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'format': 'json',
        'v': '1.0',
        'sign_method': 'md5',
        '360buy_param_json': json.dumps({
            'goodsReq': {
                'keyword': '有机枸杞',
                'pageSize': 1,
                'pageIndex': 1
            }
        })
    }

    params['sign'] = sign_request(params, APP_SECRET)

    print(f"  App Key: {APP_KEY}")
    print(f"  Site ID: {SITE_ID}")
    print(f"  请求方法: jd.union.open.goods.query")
    print(f"  搜索关键词: 有机枸杞")

    try:
        response = requests.post(API_URL, data=params, timeout=15)
        result = response.json()

        print(f"\n  响应状态码: {response.status_code}")

        if 'error_response' in result:
            error = result['error_response']
            print(f"\n  ❌ API返回错误")
            print(f"  错误码: {error.get('code')}")
            print(f"  错误信息: {error.get('msg')}")
            print(f"  子错误码: {error.get('sub_code', '无')}")
            print(f"  子错误信息: {error.get('sub_msg', '无')}")

            # 分析常见错误
            code = str(error.get('code', ''))
            if code == '25':
                print(f"\n  💡 说明: 缺少method权限，需要在京东联盟后台申请API权限")
            elif code == '26':
                print(f"\n  💡 说明: 会话过期或access_token无效")
            elif code == '27':
                print(f"\n  💡 说明: 无效签名，请检查App Secret")
            elif code == '5':
                print(f"\n  💡 说明: 无效的参数")
            return False
        else:
            print(f"\n  ✅ API调用成功!")
            # 解析京东返回的数据
            if 'jd_union_open_goods_query_response' in result:
                data = result['jd_union_open_goods_query_response']
                if 'result' in data:
                    result_data = json.loads(data['result'])
                    if 'data' in result_data:
                        goods_list = result_data['data']
                        if goods_list:
                            item = goods_list[0]
                            print(f"  示例商品: {item.get('skuName', '未知')[:50]}")
                            print(f"  价格: ¥{item.get('priceInfo', {}).get('price', '未知')}")
                            print(f"  佣金比例: {item.get('commissionInfo', {}).get('commissionShare', '未知')}%")
                        else:
                            print(f"  未找到商品")
            return True

    except requests.exceptions.Timeout:
        print(f"\n  ❌ 请求超时（15秒）")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"\n  ❌ 连接失败: {e}")
        return False
    except Exception as e:
        print(f"\n  ❌ 发生错误: {e}")
        return False

if __name__ == '__main__':
    success = test_jd()
    print("\n" + "=" * 50)
    if success:
        print("✅ 京东联盟API连接测试通过")
    else:
        print("❌ 京东联盟API连接测试失败")
    print("=" * 50)
