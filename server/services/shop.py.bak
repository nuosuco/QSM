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

# 排除关键词：搜索结果中出现这些词的商品将被过滤掉
# 排除顺序：书籍 > 化工 > 玩具 > 电子 > 其他
EXCLUDE_KEYWORDS = [
    # 书籍文具
    '书', '书籍', '教材', '课本', '图书', '文具', '笔记本', '笔', '本子',
    # 化工化学
    '化工', '化学', '试剂', '肥料', '农药', '化肥', '工业', '原料',
    # 玩具娱乐
    '玩具', '模型', '手办', '乐高', '积木', '游戏', '桌游', '卡牌',
    # 电子产品
    '手机', '电脑', '平板', '耳机', '充电器', '数据线', '电子', '数码', '电器',
    # 汽车配件
    '汽车', '轮胎', '机油', '车', '配件', '改装',
    # 宠物用品
    '猫粮', '狗粮', '宠物', '猫砂',
    # 其他无关
    '塑料', '包装', '纸箱', '胶带',
]

# 分类目录：全品类有机认证 + 环保认证产品
# 每个分类对应淘宝/京东搜索关键词
# 搜索时自动追加'有机 原生态 野生'前缀
CATEGORY_MAP = {
    '全部': {
        'keyword': '食品 养生 食材 滋补品 药膳 母婴 原生态 野生 日用品 家居 绿植 健身 保健 棉品 美妆',
        'icon': '🌿',
        'desc': '所有有机认证、环保认证产品',
    },
    # ====== 食品粮油 ======
    '谷物杂粮': {
        'keyword': '五谷杂粮 大米 小米 燕麦 藜麦 原生态 野生',
        'icon': '🌾',
        'desc': '有机五谷杂粮、米面粮油',
    },
    '滋补养生': {
        'keyword': '滋补 枸杞 红枣 黄芪 党参 人参 原生态 野生',
        'icon': '🫖',
        'desc': '枸杞、红枣、黄芪、党参等滋补品',
    },
    '药膳食材': {
        'keyword': '药膳 药食同源 黄芪 党参 山药 莲子 茯苓 原生态 野生',
        'icon': '🍲',
        'desc': '药膳食材、药食同源目录食材',
    },
    '茶饮酒水': {
        'keyword': '茶 养生茶 花茶 红茶 绿茶 药酒 果酒 原生态 野生',
        'icon': '🍵',
        'desc': '有机茶、养生茶、药酒、果酒',
    },
    '坚果干果': {
        'keyword': '坚果 核桃 杏仁 腰果 干果 果脯 原生态 野生',
        'icon': '🥜',
        'desc': '有机坚果、干果、果脯',
    },
    '菌菇干货': {
        'keyword': '菌菇 香菇 木耳 银耳 干货 山珍 原生态 野生',
        'icon': '🍄',
        'desc': '有机菌菇、木耳、银耳等山珍干货',
    },
    '调味佐料': {
        'keyword': '调味品 酱油 醋 橄榄油 调料 蜂蜜 原生态 野生',
        'icon': '🧂',
        'desc': '有机调味品、蜂蜜、橄榄油等',
    },
    '新鲜果蔬': {
        'keyword': '蔬菜 水果 新鲜 时令 原生态 野生',
        'icon': '🥬',
        'desc': '有机认证新鲜蔬果',
    },
    '母婴食品': {
        'keyword': '母婴 婴儿食品 奶粉 辅食 原生态 野生',
        'icon': '🍼',
        'desc': '有机婴幼儿食品、奶粉',
    },
    # ====== 日用品 ======
    '棉品面料': {
        'keyword': '棉 丝 麻 竹纤维 面料 衣服 内衣 毛巾 床品',
        'icon': '👕',
        'desc': '有机棉、丝、麻等天然面料服装家纺',
    },
    '日化洗护': {
        'keyword': '洗发水 沐浴露 护肤品 化妆品 手工皂 环保 原生态 野生',
        'icon': '🧴',
        'desc': '有机/环保认证日化洗护用品',
    },
    '美妆护肤': {
        'keyword': '护肤品 化妆品 面膜 精油 纯露 口红 原生态 野生',
        'icon': '💄',
        'desc': '有机/天然成分美妆护肤品',
    },
    # ====== 家居生活 ======
    '家居日用': {
        'keyword': '家居 日用 收纳 竹制品 藤编 环保 原生态 野生',
        'icon': '🏠',
        'desc': '环保家居用品、竹木藤编制品',
    },
    '绿植盆栽': {
        'keyword': '绿植 盆栽 花卉 多肉 盆景 园艺 原生态 野生',
        'icon': '🪴',
        'desc': '绿植盆栽、花卉园艺、盆景',
    },
    '环保餐具': {
        'keyword': '餐具 厨具 水杯 竹纤维 麦秸秆 环保 原生态',
        'icon': '🍽️',
        'desc': '环保餐具、竹纤维/麦秸秆制品',
    },
    # ====== 健康养生 ======
    '保健器械': {
        'keyword': '保健品 艾灸 刮痧 拔罐 按摩 理疗 原生态 野生',
        'icon': '💊',
        'desc': '有机保健品、艾灸刮痧等中医器具',
    },
    '健身运动': {
        'keyword': '健身 瑜伽 太极 运动 器材 跳绳 原生态',
        'icon': '🏋️',
        'desc': '环保健身器材、瑜伽用品、太极用品',
    },
    '户外出行': {
        'keyword': '户外 露营 徒步 登山 环保 水杯 原生态 野生',
        'icon': '🥾',
        'desc': '环保户外用品、露营装备',
    },
    # ====== 医疗健康 ======
    '医用环保': {
        'keyword': '医用 棉签 口罩 纱布 消毒 环保 原生态',
        'icon': '🏥',
        'desc': '有机棉医用耗材、环保医疗用品',
    },
    '中医养生': {
        'keyword': '艾草 足浴 泡脚 养生壶 经络 穴位 原生态 野生',
        'icon': '🧘',
        'desc': '中医养生用品、艾草足浴、经络调理',
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
            # 把长关键词拆成2-3个词的短组合，分别搜索再合并
            sub_keywords = self._split_keywords(search_keyword)
            seen_ids = set()
            for sub_kw in sub_keywords:
                # 每个子关键词搜3页，覆盖更多商品
                for page_num in range(1, 4):
                    sub_items = self._search_taobao(sub_kw, page_num, page_size, sort)
                    if not sub_items:
                        break  # 这一页没结果了，跳过
                    for item in sub_items:
                        item_id = item.get('item_id', '') or item.get('title', '')
                        if item_id not in seen_ids and not self._is_excluded(item):
                            seen_ids.add(item_id)
                            items.append(item)
                # 如果已经收集够多了，就不再继续
                if len(items) >= page_size * 10:
                    break
        if platform in ("jd", "all"):
            for page_num in range(1, 4):
                for item in self._search_jd(search_keyword, page_num, page_size):
                    if not self._is_excluded(item):
                        items.append(item)
        return items

    def _is_excluded(self, item: dict) -> bool:
        """检查商品是否应该被排除（书籍、化工、玩具等无关品类）"""
        title = (item.get('title', '') or '').lower()
        for ex in EXCLUDE_KEYWORDS:
            if ex in title:
                return True
        return False

    def _split_keywords(self, keyword: str) -> list:
        """将长关键词拆分成2-3个词的短组合，确保淘宝能搜到"""
        words = keyword.split()
        if len(words) <= 3:
            return [keyword]
        # 取前2个词作为基础，然后依次追加
        result = []
        base = ' '.join(words[:2])
        result.append(base)
        for i in range(2, len(words)):
            result.append(f"{words[0]} {words[i]}")
        return result

    def _ensure_organic(self, keyword: str) -> str:
        """确保搜索词包含有机认证关键词"""
        # 强制在开头加'有机'，确保搜索结果是有机认证产品
        return f"有机 {keyword}"

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
