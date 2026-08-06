# SOM松麦 - 淘宝联盟与京东联盟API调用技术说明

## 一、项目背景

SOM松麦是一个中医辨证+有机食品推荐平台，通过淘宝联盟和京东联盟API获取商品数据，用户通过推荐链接购买后，平台获得佣金。

## 二、淘宝联盟API调用

### 2.1 API信息

- **接口地址**: `https://eco.taobao.com/router/rest`
- **请求方式**: GET
- **API方法名**: `taobao.tbk.dg.material.optional.upgrade`（升级版物料搜索）
- **权限包ID**: 16516（物料搜索权限）

### 2.2 必需参数

```python
params = {
    'app_key': '34975006',              # 应用key
    'method': 'taobao.tbk.dg.material.optional.upgrade',  # 必须是这个升级版方法名
    'timestamp': '2026-07-22 10:30:00',  # 格式: YYYY-MM-DD HH:MM:SS
    'format': 'json',
    'v': '2.0',
    'sign_method': 'md5',
    'adzone_id': '115831100360',        # 推广位ID
    'site_id': '3155250154',            # 媒体ID
    'q': '枸杞',                        # 搜索关键词
    'page_size': '20',                  # 每页数量
    'page_no': '1',                     # 页码
    'platform': '2',                    # 平台类型: 1=PC, 2=移动端
}
```

### 2.3 签名算法（关键）

淘宝联盟使用MD5签名，算法如下：

```python
import hashlib

def sign_taobao(params, app_secret):
    """
    签名步骤：
    1. 将所有参数按字母顺序排序（不包括sign参数）
    2. 拼接成: app_secret + key1value1key2value2... + app_secret
    3. 对整个字符串做MD5加密，转大写
    """
    # 按key排序
    sorted_params = sorted(params.items())
    
    # 拼接签名字符串
    sign_str = app_secret + ''.join(f"{k}{v}" for k, v in sorted_params) + app_secret
    
    # MD5加密并转大写
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

# 使用示例
app_secret = '4bbf7dda72ea0a07bbac05005b46c75f'
params['sign'] = sign_taobao(params, app_secret)
```

### 2.4 完整调用示例

```python
import requests
import hashlib
import time

def search_taobao(keyword, page=1, page_size=20):
    app_key = '34975006'
    app_secret = '4bbf7dda72ea0a07bbac05005b46c75f'
    adzone_id = '115831100360'
    site_id = '3155250154'
    
    params = {
        'app_key': app_key,
        'method': 'taobao.tbk.dg.material.optional.upgrade',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'format': 'json',
        'v': '2.0',
        'sign_method': 'md5',
        'adzone_id': adzone_id,
        'site_id': site_id,
        'q': keyword,
        'page_size': str(page_size),
        'page_no': str(page),
        'platform': '2',
    }
    
    # 生成签名
    sorted_params = sorted(params.items())
    sign_str = app_secret + ''.join(f"{k}{v}" for k, v in sorted_params) + app_secret
    params['sign'] = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
    
    # 发送请求
    resp = requests.get("https://eco.taobao.com/router/rest", params=params, timeout=10)
    result = resp.json()
    
    # 检查错误
    if 'error_response' in result:
        print(f"淘宝API错误: {result['error_response']}")
        return []
    
    # 解析返回数据
    # 返回结构: { "tbk_dg_material_optional_upgrade_response": { "result_list": { "map_data": [...] } } }
    for key in result:
        if key != 'error_response':
            data = result[key]
            if isinstance(data, dict) and 'result_list' in data:
                items_data = data['result_list'].get('map_data', [])
                items = []
                for item in items_data:
                    basic = item.get('item_basic_info', {})
                    promo = item.get('item_promotion_info', {})
                    items.append({
                        'title': basic.get('short_title', '') or basic.get('title', ''),
                        'price': promo.get('final_price', '') or basic.get('reserve_price', ''),
                        'image': basic.get('pict_url', ''),
                        'url': promo.get('click_url', ''),  # 这是带佣金的推广链接
                        'platform': 'taobao',
                        'commission_rate': promo.get('commission_rate', ''),
                        'shop_name': basic.get('shop_title', ''),
                    })
                return items
    return []

# 测试
items = search_taobao('有机枸杞')
print(f"找到 {len(items)} 个商品")
```

### 2.5 常见错误

1. **错误码22: Invalid method** - 方法名错误，必须用 `taobao.tbk.dg.material.optional.upgrade`，不是旧版的 `taobao.tbk.item.get`
2. **错误码11: Insufficient isv permissions** - 权限不足，需要在淘宝联盟后台申请权限包16516
3. **签名错误** - 检查签名算法，确保参数排序正确，app_secret在前后都有

## 三、京东联盟API调用

### 3.1 API信息

- **接口地址**: `https://api.jd.com/routerjson`
- **请求方式**: POST
- **API方法名**: `jd.union.open.goods.query`（商品查询）

### 3.2 必需参数

```python
import json
from datetime import datetime, timezone, timedelta

def get_beijing_time():
    """获取北京时间（UTC+8）"""
    utc_now = datetime.now(timezone.utc)
    beijing_tz = timezone(timedelta(hours=8))
    return utc_now.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')

params = {
    'app_key': '1c790ba72292dc6723a8145c3ac994f7',
    'method': 'jd.union.open.goods.query',
    'timestamp': get_beijing_time(),  # 必须是北京时间！
    'format': 'json',
    'v': '1.0',
    'sign_method': 'md5',
    '360buy_param_json': json.dumps({
        'goodsReq': {
            'keyword': '枸杞',
            'pageSize': 20,
            'pageIndex': 1,
        }
    })
}
```

### 3.3 签名算法

京东联盟也使用MD5签名，算法与淘宝相同：

```python
def sign_jd(params, app_secret):
    """京东联盟签名"""
    sorted_params = sorted(params.items())
    sign_str = app_secret + ''.join(f"{k}{v}" for k, v in sorted_params) + app_secret
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

app_secret = 'bbb6957c76224ca78db994daf03d90d5'
params['sign'] = sign_jd(params, app_secret)
```

### 3.4 完整调用示例

```python
import requests
import hashlib
import json
from datetime import datetime, timezone, timedelta

def search_jd(keyword, page=1, page_size=20):
    app_key = '1c790ba72292dc6723a8145c3ac994f7'
    app_secret = 'bbb6957c76224ca78db994daf03d90d5'
    
    # 获取北京时间
    utc_now = datetime.now(timezone.utc)
    beijing_tz = timezone(timedelta(hours=8))
    timestamp = utc_now.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    params = {
        'app_key': app_key,
        'method': 'jd.union.open.goods.query',
        'timestamp': timestamp,
        'format': 'json',
        'v': '1.0',
        'sign_method': 'md5',
        '360buy_param_json': json.dumps({
            'goodsReq': {
                'keyword': keyword,
                'pageSize': page_size,
                'pageIndex': page,
            }
        })
    }
    
    # 生成签名
    sorted_params = sorted(params.items())
    sign_str = app_secret + ''.join(f"{k}{v}" for k, v in sorted_params) + app_secret
    params['sign'] = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
    
    # 发送请求（注意是POST）
    resp = requests.post("https://api.jd.com/routerjson", data=params, timeout=10)
    result = resp.json()
    
    # 检查错误
    if 'error_response' in result:
        print(f"京东API错误: {result['error_response']}")
        return []
    
    # 解析返回数据
    # 返回结构: { "jd_union_open_goods_query_response": { "result": "{...json string...}" } }
    resp_key = 'jd_union_open_goods_query_response'
    if resp_key in result:
        data = result[resp_key]
        if 'result' in data:
            # result字段是JSON字符串，需要再次解析
            result_data = json.loads(data['result'])
            goods_list = result_data.get('data', [])
            items = []
            for item in goods_list:
                price_info = item.get('priceInfo', {})
                commission_info = item.get('commissionInfo', {})
                image_info = item.get('imageInfo', {})
                
                # 获取第一张图片
                image_url = ''
                if image_info.get('imageList'):
                    image_url = image_info['imageList'][0].get('url', '')
                
                items.append({
                    'title': item.get('skuName', ''),
                    'price': price_info.get('price', ''),
                    'image': image_url,
                    'url': item.get('materialUrl', ''),  # 推广链接
                    'platform': 'jd',
                    'commission_rate': f"{commission_info.get('commissionShare', 0)}%",
                    'shop_name': item.get('shopInfo', {}).get('shopName', ''),
                })
            return items
    return []

# 测试
items = search_jd('有机枸杞')
print(f"找到 {len(items)} 个商品")
```

### 3.5 常见错误

1. **错误码8: Invalid timestamp** - 时间戳错误，必须用北京时间（UTC+8），不能用UTC时间
2. **错误码2000: Rate limit exceeded** - 请求频率过高，京东有限流，测试时注意间隔
3. **签名错误** - 检查签名算法，确保 `360buy_param_json` 参数也被包含在签名中

## 四、关键注意事项

### 4.1 淘宝联盟

1. **必须用升级版API**: `taobao.tbk.dg.material.optional.upgrade`，旧版API已废弃
2. **权限包**: 需要在淘宝联盟后台申请权限包16516（物料搜索）
3. **PID格式**: 完整PID是 `mm_52057803_3155250154_115831100360`，其中：
   - 52057803 = 会员ID
   - 3155250154 = 媒体ID（site_id）
   - 115831100360 = 推广位ID（adzone_id）

### 4.2 京东联盟

1. **时间戳**: 必须是北京时间（UTC+8），用 `datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))` 获取
2. **请求方式**: 京东用POST，淘宝用GET
3. **参数格式**: `360buy_param_json` 是JSON字符串，需要 `json.dumps()` 转换
4. **返回数据**: `result` 字段是JSON字符串，需要二次解析

### 4.3 通用注意事项

1. **签名算法**: 两个平台都用MD5签名，算法相同：`app_secret + 排序后的参数 + app_secret`
2. **错误处理**: 检查返回数据中是否有 `error_response` 字段
3. **推广链接**: 淘宝的 `click_url` 和京东的 `materialUrl` 就是带佣金的推广链接，用户通过这些链接购买，平台才能获得佣金

## 五、测试验证

测试代码：

```python
# 测试淘宝
tb_items = search_taobao('有机枸杞')
print(f"淘宝找到 {len(tb_items)} 个商品")
if tb_items:
    print(f"第一个商品: {tb_items[0]['title']} - ¥{tb_items[0]['price']}")

# 测试京东
jd_items = search_jd('有机枸杞')
print(f"京东找到 {len(jd_items)} 个商品")
if jd_items:
    print(f"第一个商品: {jd_items[0]['title']} - ¥{jd_items[0]['price']}")
```

如果返回0个商品，检查：
1. API密钥是否正确
2. 权限是否已申请
3. 签名算法是否正确
4. 查看返回的完整JSON，找到具体的错误信息

## 六、完整配置

```json
{
  "taobao": {
    "app_key": "34975006",
    "app_secret": "4bbf7dda72ea0a07bbac05005b46c75f",
    "pid": "mm_52057803_3155250154_115831100360",
    "adzone_id": "115831100360",
    "site_id": "3155250154"
  },
  "jd": {
    "app_key": "1c790ba72292dc6723a8145c3ac994f7",
    "app_secret": "bbb6957c76224ca78db994daf03d90d5",
    "site_id": "2035806496"
  }
}
```

---

**文档版本**: v1.0  
**更新日期**: 2026-07-22  
**项目**: SOM松麦 - 中医辨证+有机食品推荐平台
