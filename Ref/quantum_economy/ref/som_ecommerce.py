import os
import sys
import json
import logging
import datetime
import hashlib
import uuid
import random
from typing import List, Dict, Any, Optional

# 导入松麦经济模型模块
<<<<<<< HEAD
from quantum_economy.Ref.Ref_economy import SomEconomyModel
=======
from quantum_economy.ref.ref_economy import SomEconomyModel
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ref_ecommerce.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SomEcommerce")

class SomEcommerce:
    """松麦电商平台，实现有机食品电商系统"""
    
    def __init__(self, platform_id: str = None):
        """初始化松麦电商平台
        
        Args:
            platform_id: 平台唯一标识，如果为None则自动生成
        """
        self.platform_id = platform_id or self._generate_platform_id()
        self.creation_time = datetime.datetime.now()
        self.economy_model = None  # 松麦经济模型
        self.products = {}  # 存储产品信息
        self.merchants = {}  # 存储商户信息
        self.users = {}  # 存储用户信息
        self.orders = {}  # 存储订单信息
        self.alliance_accounts = {}  # 存储联盟账户
        self.traceability_records = {}  # 存储溯源记录
        self.config = {
            "platform_name": "松麦生态电商平台",
            "platform_url": "https://ref.top",
            "platform_description": "为每个人的健康服务",
            "commission_rate": 0.05,  # 平台佣金率
            "reward_rate": 1.0,  # 松麦币奖励率（购买金额的倍数）
            "registration_reward": 100.0  # 注册奖励松麦币数量
        }
        logger.info(f"初始化松麦电商平台: {self.platform_id}")
    
    def _generate_platform_id(self) -> str:
        """生成平台唯一标识"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = str(uuid.uuid4())[:8]
        return f"SOM-ECOM-{timestamp}-{random_str}"
    
    def set_economy_model(self, economy_model: SomEconomyModel):
        """设置松麦经济模型
        
        Args:
            economy_model: 松麦经济模型
        """
        self.economy_model = economy_model
        logger.info(f"设置松麦经济模型: {economy_model.model_id}")
    
    def register_alliance_account(self, platform: str, account_data: Dict) -> Dict:
        """注册联盟账户
        
        Args:
            platform: 平台名称（如"淘宝"、"京东"等）
            account_data: 账户数据
            
        Returns:
            注册结果
        """
        account_id = f"{platform.upper()}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.alliance_accounts[account_id] = {
            "account_id": account_id,
            "platform": platform,
            "account_data": account_data,
            "registration_time": datetime.datetime.now().isoformat(),
            "status": "active",
            "last_sync_time": None,
            "product_count": 0
        }
        
        logger.info(f"注册联盟账户: {account_id}, 平台: {platform}")
        return {
            "success": True,
            "message": f"成功注册{platform}联盟账户",
            "account_id": account_id
        }
    
    def sync_alliance_products(self, account_id: str, filter_organic: bool = True) -> Dict:
        """同步联盟账户产品
        
        从联盟平台同步产品信息，可以选择只同步有机食品
        
        Args:
            account_id: 联盟账户ID
            filter_organic: 是否只同步有机食品
            
        Returns:
            同步结果
        """
        if account_id not in self.alliance_accounts:
            logger.warning(f"联盟账户不存在: {account_id}")
            return {
                "success": False,
                "message": "联盟账户不存在"
            }
        
        # 模拟从联盟平台同步产品
        # 在实际应用中，这里会调用各平台的API
        
        # 生成模拟产品数据
        sync_time = datetime.datetime.now()
        synced_products = []
        
        # 根据平台生成不同的产品数据
        platform = self.alliance_accounts[account_id]["platform"]
        product_count = random.randint(10, 30)  # 模拟10-30个产品
        
        for i in range(product_count):
            # 随机决定是否为有机产品
            is_organic = random.random() > 0.3  # 70%是有机产品
            
            if filter_organic and not is_organic:
                continue
            
            # 生成产品ID
            product_id = f"{platform}-{str(uuid.uuid4())[:8]}"
            
            # 生成产品价格
            price = round(random.uniform(10, 500), 2)
            
            # 生成产品数据
            product_data = {
                "product_id": product_id,
                "alliance_account_id": account_id,
                "platform": platform,
                "name": f"有机{'蔬菜' if random.random() > 0.5 else '水果'}{i+1}",
                "price": price,
                "description": f"来自{platform}的优质有机{'蔬菜' if random.random() > 0.5 else '水果'}，健康美味。",
                "is_organic": is_organic,
                "category": "有机食品",
                "stock": random.randint(10, 100),
                "images": [f"https://example.com/products/{product_id}/image{j+1}.jpg" for j in range(3)],
                "source": platform,
                "source_url": f"https://example.com/{platform}/products/{product_id}",
                "sync_time": sync_time.isoformat()
            }
            
            # 添加产品
            self.products[product_id] = product_data
            synced_products.append(product_id)
        
        # 更新联盟账户信息
        self.alliance_accounts[account_id]["last_sync_time"] = sync_time.isoformat()
        self.alliance_accounts[account_id]["product_count"] = len(synced_products)
        
        logger.info(f"同步联盟账户产品: 账户={account_id}, 平台={platform}, 同步产品数={len(synced_products)}")
        return {
            "success": True,
            "message": f"成功从{platform}同步{len(synced_products)}个产品",
            "account_id": account_id,
            "synced_products": synced_products,
            "sync_time": sync_time.isoformat()
        }
    
    def register_merchant(self, merchant_data: Dict) -> Dict:
        """注册商户
        
        Args:
            merchant_data: 商户数据
            
        Returns:
            注册结果
        """
        # 生成商户ID
        merchant_id = f"MERCH-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4]}"
        
        # 创建商户信息
        self.merchants[merchant_id] = {
            "merchant_id": merchant_id,
            "registration_time": datetime.datetime.now().isoformat(),
            "status": "active",
            "product_count": 0,
            "total_sales": 0.0,
            "rating": 5.0,
            **merchant_data
        }
        
        logger.info(f"注册商户: {merchant_id}, 名称: {merchant_data.get('name')}")
        return {
            "success": True,
            "message": "商户注册成功",
            "merchant_id": merchant_id
        }
    
    def register_user(self, user_data: Dict) -> Dict:
        """注册用户
        
        Args:
            user_data: 用户数据
            
        Returns:
            注册结果
        """
        # 生成用户ID
        user_id = f"USER-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4]}"
        
        # 创建用户信息
        self.users[user_id] = {
            "user_id": user_id,
            "registration_time": datetime.datetime.now().isoformat(),
            "status": "active",
            "ref_balance": 0.0,
            "order_count": 0,
            "total_spend": 0.0,
            "preferences": [],
            "address_book": [],
            **user_data
        }
        
        # 发放注册奖励
        if self.economy_model:
            reward_result = self.economy_model.register_new_user(user_id, user_data)
            if reward_result["success"]:
                self.users[user_id]["ref_balance"] += reward_result["reward_amount"]
        
        logger.info(f"注册用户: {user_id}, 名称: {user_data.get('name')}")
        return {
            "success": True,
            "message": "用户注册成功，已发放松麦币奖励",
            "user_id": user_id,
            "ref_balance": self.users[user_id]["ref_balance"]
        }
    
    def add_merchant_product(self, merchant_id: str, product_data: Dict) -> Dict:
        """添加商户产品
        
        Args:
            merchant_id: 商户ID
            product_data: 产品数据
            
        Returns:
            添加结果
        """
        if merchant_id not in self.merchants:
            logger.warning(f"商户不存在: {merchant_id}")
            return {
                "success": False,
                "message": "商户不存在"
            }
        
        # 生成产品ID
        product_id = f"PROD-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4]}"
        
        # 创建产品信息
        self.products[product_id] = {
            "product_id": product_id,
            "merchant_id": merchant_id,
            "creation_time": datetime.datetime.now().isoformat(),
            "status": "active",
            "platform": "ref",
            "source": "direct",
            "sales_count": 0,
            "rating": 5.0,
            "reviews": [],
            **product_data
        }
        
        # 更新商户产品数量
        self.merchants[merchant_id]["product_count"] += 1
        
        # 创建溯源记录
        if product_data.get("is_organic", False):
            self.create_traceability_record(product_id, {
                "farm_name": product_data.get("farm_name", "未知农场"),
                "production_date": product_data.get("production_date", datetime.datetime.now().isoformat()),
                "certification": product_data.get("certification", "有机认证"),
                "location": product_data.get("farm_location", "未知位置"),
                "farming_method": product_data.get("farming_method", "有机种植")
            })
        
        logger.info(f"添加商户产品: 商户={merchant_id}, 产品={product_id}, 名称={product_data.get('name')}")
        return {
            "success": True,
            "message": "产品添加成功",
            "product_id": product_id
        }
    
    def create_traceability_record(self, product_id: str, traceability_data: Dict) -> Dict:
        """创建溯源记录
        
        Args:
            product_id: 产品ID
            traceability_data: 溯源数据
            
        Returns:
            创建结果
        """
        if product_id not in self.products:
            logger.warning(f"产品不存在: {product_id}")
            return {
                "success": False,
                "message": "产品不存在"
            }
        
        # 生成溯源ID
        trace_id = f"TRACE-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4]}"
        
        # 创建溯源记录
        self.traceability_records[trace_id] = {
            "trace_id": trace_id,
            "product_id": product_id,
            "creation_time": datetime.datetime.now().isoformat(),
            "trace_hash": hashlib.sha256(f"{product_id}:{datetime.datetime.now().isoformat()}".encode()).hexdigest(),
            "trace_chain": [],
            **traceability_data
        }
        
        # 更新产品溯源ID
        self.products[product_id]["trace_id"] = trace_id
        
        logger.info(f"创建溯源记录: 产品={product_id}, 溯源ID={trace_id}")
        return {
            "success": True,
            "message": "溯源记录创建成功",
            "trace_id": trace_id
        }
    
    def get_traceability_info(self, product_id: str) -> Dict:
        """获取产品溯源信息
        
        Args:
            product_id: 产品ID
            
        Returns:
            溯源信息
        """
        if product_id not in self.products:
            logger.warning(f"产品不存在: {product_id}")
            return {
                "success": False,
                "message": "产品不存在"
            }
        
        product = self.products[product_id]
        
        if "trace_id" not in product:
            logger.warning(f"产品没有溯源记录: {product_id}")
            return {
                "success": False,
                "message": "产品没有溯源记录"
            }
        
        trace_id = product["trace_id"]
        
        if trace_id not in self.traceability_records:
            logger.warning(f"溯源记录不存在: {trace_id}")
            return {
                "success": False,
                "message": "溯源记录不存在"
            }
        
        trace_record = self.traceability_records[trace_id]
        
        logger.info(f"获取产品溯源信息: 产品={product_id}, 溯源ID={trace_id}")
        return {
            "success": True,
            "product_id": product_id,
            "product_name": product.get("name", "未知产品"),
            "trace_id": trace_id,
            "trace_data": trace_record
        }
    
    def create_order(self, user_id: str, order_data: Dict) -> Dict:
        """创建订单
        
        Args:
            user_id: 用户ID
            order_data: 订单数据
            
        Returns:
            创建结果
        """
        if user_id not in self.users:
            logger.warning(f"用户不存在: {user_id}")
            return {
                "success": False,
                "message": "用户不存在"
            }
        
        # 验证产品
        items = order_data.get("items", [])
        if not items:
            logger.warning(f"订单没有商品: 用户={user_id}")
            return {
                "success": False,
                "message": "订单没有商品"
            }
        
        valid_items = []
        total_amount = 0.0
        
        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            
            if product_id not in self.products:
                logger.warning(f"产品不存在: {product_id}")
                continue
            
            product = self.products[product_id]
            
            if product.get("status") != "active":
                logger.warning(f"产品不可用: {product_id}")
                continue
            
            if product.get("stock", 0) < quantity:
                logger.warning(f"产品库存不足: {product_id}, 需要={quantity}, 库存={product.get('stock', 0)}")
                continue
            
            # 计算商品总价
            price = product.get("price", 0.0)
            item_total = price * quantity
            
            valid_items.append({
                "product_id": product_id,
                "product_name": product.get("name", "未知产品"),
                "quantity": quantity,
                "price": price,
                "item_total": item_total
            })
            
            total_amount += item_total
        
        if not valid_items:
            logger.warning(f"没有有效商品: 用户={user_id}")
            return {
                "success": False,
                "message": "没有有效商品"
            }
        
        # 生成订单ID
        order_id = f"ORDER-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4]}"
        
        # 计算佣金
        commission = total_amount * self.config["commission_rate"]
        
        # 创建订单
        order = {
            "order_id": order_id,
            "user_id": user_id,
            "creation_time": datetime.datetime.now().isoformat(),
            "status": "created",
            "items": valid_items,
            "total_amount": total_amount,
            "commission": commission,
            "payment_status": "pending",
            "shipping_address": order_data.get("shipping_address", {}),
            "payment_method": order_data.get("payment_method", "online")
        }
        
        self.orders[order_id] = order
        
        # 更新用户订单数量
        self.users[user_id]["order_count"] += 1
        
        logger.info(f"创建订单: 用户={user_id}, 订单={order_id}, 金额={total_amount}")
        return {
            "success": True,
            "message": "订单创建成功",
            "order_id": order_id,
            "total_amount": total_amount
        }
    
    def pay_order(self, order_id: str, payment_data: Dict) -> Dict:
        """支付订单
        
        Args:
            order_id: 订单ID
            payment_data: 支付数据
            
        Returns:
            支付结果
        """
        if order_id not in self.orders:
            logger.warning(f"订单不存在: {order_id}")
            return {
                "success": False,
                "message": "订单不存在"
            }
        
        order = self.orders[order_id]
        
        if order["status"] != "created" or order["payment_status"] != "pending":
            logger.warning(f"订单状态不正确: {order_id}, 状态={order['status']}, 支付状态={order['payment_status']}")
            return {
                "success": False,
                "message": "订单状态不正确"
            }
        
        # 模拟支付处理
        # 在实际应用中，这里会调用支付接口
        
        # 更新订单状态
        order["status"] = "paid"
        order["payment_status"] = "completed"
        order["payment_time"] = datetime.datetime.now().isoformat()
        order["payment_data"] = payment_data
        
        # 更新产品库存和销量
        for item in order["items"]:
            product_id = item["product_id"]
            quantity = item["quantity"]
            
            if product_id in self.products:
                product = self.products[product_id]
                product["stock"] = max(0, product.get("stock", 0) - quantity)
                product["sales_count"] = product.get("sales_count", 0) + quantity
                
                # 更新商户销量
                if "merchant_id" in product:
                    merchant_id = product["merchant_id"]
                    if merchant_id in self.merchants:
                        self.merchants[merchant_id]["total_sales"] += item["item_total"]
        
        # A）发放松麦币奖励
        user_id = order["user_id"]
        reward_amount = 0.0
        
        if self.economy_model and user_id:
            # 为每个有机产品发放奖励
            for item in order["items"]:
                product_id = item["product_id"]
                if product_id in self.products and self.products[product_id].get("is_organic", False):
                    purchase_amount = item["item_total"]
                    
                    # 处理购买
                    purchase_result = self.economy_model.process_organic_purchase(
                        user_id=user_id,
                        product_id=product_id,
                        purchase_amount=purchase_amount
                    )
                    
                    if purchase_result["success"]:
                        reward_amount += purchase_result["reward_amount"]
            
            # 更新用户松麦币余额
            if user_id in self.users:
                self.users[user_id]["ref_balance"] += reward_amount
                self.users[user_id]["total_spend"] += order["total_amount"]
        
        # 记录奖励信息
        order["ref_reward"] = reward_amount
        
        logger.info(f"支付订单: 订单={order_id}, 用户={user_id}, 金额={order['total_amount']}, 奖励={reward_amount}")
        return {
            "success": True,
            "message": "订单支付成功，已发放松麦币奖励",
            "order_id": order_id,
            "ref_reward": reward_amount
        }
    
    def search_products(self, query: str, filters: Dict = None) -> List[Dict]:
        """搜索产品
        
        Args:
            query: 搜索关键词
            filters: 过滤条件
            
        Returns:
            产品列表
        """
        filters = filters or {}
        results = []
        
        for product_id, product in self.products.items():
            # 检查产品状态
            if product.get("status") != "active":
                continue
            
            # 检查关键词
            name = product.get("name", "").lower()
            description = product.get("description", "").lower()
            query_lower = query.lower()
            
            if query_lower not in name and query_lower not in description:
                continue
            
            # 应用过滤条件
            if filters.get("is_organic") is not None and product.get("is_organic") != filters["is_organic"]:
                continue
            
            if filters.get("min_price") is not None and product.get("price", 0) < filters["min_price"]:
                continue
            
            if filters.get("max_price") is not None and product.get("price", 0) > filters["max_price"]:
                continue
            
            if filters.get("platform") and product.get("platform") != filters["platform"]:
                continue
            
            # 添加到结果
            results.append(product)
        
        # 排序
        sort_by = filters.get("sort_by", "relevance")
        if sort_by == "price_asc":
            results.sort(key=lambda p: p.get("price", 0))
        elif sort_by == "price_desc":
            results.sort(key=lambda p: p.get("price", 0), reverse=True)
        elif sort_by == "sales":
            results.sort(key=lambda p: p.get("sales_count", 0), reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda p: p.get("rating", 0), reverse=True)
        
        logger.info(f"搜索产品: 关键词={query}, 过滤条件={filters}, 结果数={len(results)}")
        return results
    
    def recommend_products(self, user_id: str, count: int = 10) -> List[Dict]:
        """推荐产品
        
        基于用户偏好推荐产品
        
        Args:
            user_id: 用户ID
            count: 推荐数量
            
        Returns:
            产品列表
        """
        # 获取用户偏好
        preferences = []
        if user_id in self.users:
            preferences = self.users[user_id].get("preferences", [])
        
        # 找出所有有机产品
        organic_products = [p for p in self.products.values() if p.get("is_organic", False) and p.get("status") == "active"]
        
        if not organic_products:
            logger.warning("没有可推荐的有机产品")
            return []
        
        # 如果用户有偏好，按偏好推荐
        if preferences:
            # 对产品进行评分
            scored_products = []
            for product in organic_products:
                score = 0
                for pref in preferences:
                    # 检查产品类别
                    if pref.get("category") and pref["category"] == product.get("category", ""):
                        score += 3
                    
                    # 检查产品标签
                    if pref.get("tags"):
                        for tag in pref["tags"]:
                            if tag in product.get("tags", []):
                                score += 1
                
                # 增加销量和评分因素
                score += min(5, product.get("sales_count", 0) / 10)
                score += product.get("rating", 0)
                
                scored_products.append((product, score))
            
            # 排序并返回推荐
            scored_products.sort(key=lambda x: x[1], reverse=True)
            recommendations = [p[0] for p in scored_products[:count]]
        else:
            # 没有偏好，推荐销量最高的产品
            recommendations = sorted(organic_products, key=lambda p: p.get("sales_count", 0), reverse=True)[:count]
        
        logger.info(f"推荐产品: 用户={user_id}, 推荐数={len(recommendations)}")
        return recommendations
    
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "platform_id": self.platform_id,
            "creation_time": self.creation_time.isoformat(),
            "config": self.config,
            "products_count": len(self.products),
            "merchants_count": len(self.merchants),
            "users_count": len(self.users),
            "orders_count": len(self.orders),
            "alliance_accounts_count": len(self.alliance_accounts),
            "traceability_records_count": len(self.traceability_records)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SomEcommerce':
        """从字典恢复平台"""
        platform = cls(data["platform_id"])
        platform.creation_time = datetime.datetime.fromisoformat(data["creation_time"])
        platform.config = data["config"]
        return platform
    
    def save_to_file(self, filepath: str) -> bool:
        """保存平台状态到文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            是否成功保存
        """
        try:
            data = {
                "platform": self.to_dict(),
                "products": self.products,
                "merchants": self.merchants,
                "users": self.users,
                "orders": self.orders,
                "alliance_accounts": self.alliance_accounts,
                "traceability_records": self.traceability_records
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"成功保存电商平台状态到 {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存电商平台状态失败: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'SomEcommerce':
        """从文件加载平台状态
        
        Args:
            filepath: 文件路径
            
        Returns:
            松麦电商平台对象
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            platform_data = data["platform"]
            platform = cls.from_dict(platform_data)
            
            platform.products = data["products"]
            platform.merchants = data["merchants"]
            platform.users = data["users"]
            platform.orders = data["orders"]
            platform.alliance_accounts = data["alliance_accounts"]
            platform.traceability_records = data["traceability_records"]
            
            logger.info(f"成功从 {filepath} 加载电商平台状态")
            return platform
        except Exception as e:
            logger.error(f"加载电商平台状态失败: {e}")
            return None 

"""

"""
量子基因编码: QE-SOM-1E297E2B8988
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
