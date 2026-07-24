"""
SOM 松麦 - 商品服务
对接淘宝联盟 + 京东联盟API
只推荐有机认证、药食同源、健康环保认证产品
"""
import hashlib
import json
import os
import time
from typing import List, Optional

import requests

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

# 有机认证关键词（搜索时自动追加，确保只返回有机产品）
ORGANIC_KEYWORDS = ['有机', '有机认证', '有机食品']

# 分类目录：药食同源 + 有机食品分类
# 每个分类对应淘宝/京东搜索关键词
CATEGORY_MAP = {
    '全部': {
        'keyword': '有机食品 养生 滋补 食材 药食同源',
        'icon': '🌿',
        'desc': '所有有机认证食品与药食同源产品',
    },
    '谷物杂粮': {
        'keyword': '有机 五谷杂粮 大米 小米 燕麦',
        'icon': '🌾',
        'desc': '有机大米、小米、燕麦、藜麦等',
    },
    '滋补养生': {
        'keyword': '有机 滋补 枸杞 红枣 黄芪 党参',
        'icon': '🫖',
        'desc': '枸杞、红枣、黄芪、党参等',
    },
    '茶饮花茶': {
        'keyword': '有机茶 养生茶 花茶 红茶 绿茶',
        'icon': '🍵',
        'desc': '有机绿茶、红茶、花草茶',
    },
    '坚果干果': {
        'keyword': '有机坚果 核桃 杏仁 腰果 干果',
        'icon': '🥜',
        'desc': '有机核桃、杏仁、腰果等',
    },
    '菌菇干货': {
        'keyword': '有机菌菇 香菇 木耳 银耳 干货',
        'icon': '🍄',
        'desc': '有机香菇、木耳、银耳等',
    },
    '调味佐料': {
        'keyword': '有机调味品 酱油 醋 橄榄油 调料',
        'icon': '🧂',
        'desc': '有机酱油、醋、橄榄油等调味品',
    },
    '药食同源': {
        'keyword': '有机药食同源 黄芪 党参 山药 莲子',
        'icon': '🌱',
        'desc': '国家药食同源目录食材',
    },
    '新鲜果蔬': {
        'keyword': '有机蔬菜 有机水果 新鲜',
        'icon': '🥬',
        'desc': '有机认证新鲜蔬果',
    },
    '母婴有机': {
        'keyword': '有机母婴 婴儿食品 有机奶粉',
        'icon': '🍼',
        'desc': '有机婴幼儿食品',
    },
}


class ShopService:
    """商品搜索与推荐服务 - 只推荐有机认证产品"""

    def __init__(self):
        self.tb_config = CONFIG["taobao"]
        self.jd_config = CONFIG["jd"]

    def get_categories(self) -> List[dict]:
        """获取分类目录"""
        return [
            {'name': name, 'keyword': info['keyword'], 'icon': info['icon'], 'desc': info['desc']}
            for name, info in CATEGORY_MAP.items()
        ]

    def search(self, keyword: str, platform: str = "taobao", page: int = 1, page_size: int = 10, sort: str = "") -> List[dict]:
        """
        搜索商品 - 自动追加"有机"关键词，只返回有机认证产品
        platform: taobao / jd / all
        sort: 空=综合, price_asc=价格最低, price_desc=价格最高, sales=销量最高, credit=评价最高
        """
        # 强制追加有机认证关键词
        search_keyword = self._ensure_organic(keyword)

        items = []
        if platform in ("taobao", "all"):
            items.extend(self._search_taobao(search_keyword, page, page_size, sort))
        if platform in ("jd", "all"):
            items.extend(self._search_jd(search_keyword, page, page_size))
        return items

    def _ensure_organic(self, keyword: str) -> str:
        """确保搜索词包含有机认证关键词"""
        has_organic = any(ok in keyword for ok in ORGANIC_KEYWORDS)
        if not has_organic:
            return f"有机 {keyword}"
        return keyword

    # ========== 淘宝联盟 ==========

    def _sign_tb(self, params: dict) -> str:
        """淘宝联盟MD5签名"""
        sorted_params = sorted(params.items())
        sign_str = self.tb_config["app_secret"] + ''.join(f"{k}{v}" for k, v in sorted_params) + self.tb_config["app_secret"]
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    def _search_taobao(self, keyword: str, page: int, page_size: int, sort: str = "") -> List[dict]:
        """淘宝联盟物料搜索（升级版API）"""
        # 淘宝API排序参数映射
        sort_map = {
            'price_asc': 'price_asc',
            'price_desc': 'price_desc',
            'sales': 'sales_desc',
            'credit': 'credit_desc',
        }
        tb_sort = sort_map.get(sort, '')
        
        params = {
            'app_key': self.tb_config["app_key"],
            'method': 'taobao.tbk.dg.material.optional.upgrade',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'format': 'json',
            'v': '2.0',
            'sign_method': 'md5',
            'adzone_id': self.tb_config["adzone_id"],
            'site_id': self.tb_config["site_id"],
            'q': keyword,
            'page_size': str(page_size),
            'page_no': str(page),
            'platform': '2',
        }
        if tb_sort:
            params['sort'] = tb_sort
        params['sign'] = self._sign_tb(params)

        try:
            resp = requests.get("https://eco.taobao.com/router/rest", params=params, timeout=10)
            result = resp.json()

            if 'error_response' in result:
                return []

            # 解析返回数据
            for key in result:
                if key != 'error_response':
                    data = result[key]
                    if isinstance(data, dict) and 'result_list' in data:
                        items_data = data['result_list'].get('map_data', [])
                        items = []
                        for item in items_data:
                            basic = item.get('item_basic_info', {})
                            price_info = item.get('price_promotion_info', {})
                            publish = item.get('publish_info', {})
                            income = publish.get('income_info', {})
                            
                            # 生成淘宝APP deeplink（优先打开APP）
                            click_url = publish.get('click_url', '')
                            # 确保click_url有协议前缀
                            if click_url.startswith('//'):
                                click_url = 'https:' + click_url
                            
                            # 基于click_url生成APP deeplink，保留佣金追踪参数
                            app_url = ''
                            if click_url:
                                # 将 https://s.click.taobao.com/... 转为 taobao:// 协议
                                app_url = click_url.replace('https://', 'taobao://', 1)
                            
                            items.append({
                                'item_id': item.get('item_id', ''),
                                'title': basic.get('short_title', '') or basic.get('title', ''),
                                'price': price_info.get('zk_final_price', '') or price_info.get('reserve_price', ''),
                                'image': basic.get('pict_url', ''),
                                'url': click_url,  # 网页版推广链接（带佣金）
                                'app_url': app_url,  # APP deeplink（优先，带佣金追踪）
                                'platform': 'taobao',
                                'commission_rate': income.get('commission_rate', ''),
                                'shop_name': basic.get('shop_title', ''),
                                'brand': basic.get('brand_name', ''),
                            })
                        return items
        except Exception as e:
            print(f"淘宝搜索异常: {e}")
        return []

    # ========== 京东联盟 ==========

    def _sign_jd(self, params: dict) -> str:
        """京东联盟MD5签名"""
        sorted_params = sorted(params.items())
        sign_str = self.jd_config["app_secret"] + ''.join(f"{k}{v}" for k, v in sorted_params) + self.jd_config["app_secret"]
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    def _get_beijing_time(self) -> str:
        """获取北京时间"""
        from datetime import datetime, timezone, timedelta
        utc_now = datetime.now(timezone.utc)
        beijing_tz = timezone(timedelta(hours=8))
        return utc_now.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')

    def _search_jd(self, keyword: str, page: int, page_size: int) -> List[dict]:
        """京东联盟商品查询"""
        params = {
            'app_key': self.jd_config["app_key"],
            'method': 'jd.union.open.goods.query',
            'timestamp': self._get_beijing_time(),
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
        params['sign'] = self._sign_jd(params)

        try:
            resp = requests.post("https://api.jd.com/routerjson", data=params, timeout=10)
            result = resp.json()

            if 'error_response' in result:
                return []

            # 解析京东返回
            resp_key = 'jd_union_open_goods_query_response'
            if resp_key in result:
                data = result[resp_key]
                if 'result' in data:
                    result_data = json.loads(data['result'])
                    goods_list = result_data.get('data', [])
                    items = []
                    for item in goods_list:
                        price_info = item.get('priceInfo', {})
                        commission_info = item.get('commissionInfo', {})
                        items.append({
                            'title': item.get('skuName', ''),
                            'price': price_info.get('price', ''),
                            'image': item.get('imageInfo', {}).get('imageList', [{}])[0].get('url', '') if item.get('imageInfo', {}).get('imageList') else '',
                            'url': item.get('materialUrl', ''),
                            'platform': 'jd',
                            'commission_rate': f"{commission_info.get('commissionShare', 0)}%",
                            'shop_name': item.get('shopInfo', {}).get('shopName', ''),
                        })
                    return items
        except Exception as e:
            print(f"京东搜索异常: {e}")
        return []
