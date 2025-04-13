"""
松麦生态商城核心实现

本模块实现松麦生态商城的核心功能，包括：
1. 外部联盟账号绑定与数据同步
2. 有机食品筛选与导入
3. 产品推荐算法
"""

import os
import sys
import json
import logging
import requests
import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

# 导入追溯系统
try:
    from quantum_economy.qsm.traceability.traceability_system import SomTraceabilitySystem
except ImportError:
    # 开发环境Mock
    class SomTraceabilitySystem:
        def __init__(self): pass
        
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("qsm_marketplace.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SomMarketplace")

class ProductCategory(Enum):
    """产品类别枚举"""
    VEGETABLES = "蔬菜水果"
    GRAINS = "粮油米面"
    DAIRY = "奶制品"
    MEAT = "肉禽蛋品"
    SEAFOOD = "海鲜水产"
    SNACKS = "零食坚果"
    DRINKS = "饮品茶酒"
    HEALTH = "保健营养"
    OTHER = "其他食品"

@dataclass
class AllianceAccount:
    """联盟账号信息"""
    alliance_id: str
    alliance_name: str
    api_key: str
    account_id: str
    status: str
    binding_time: datetime.datetime
    last_sync_time: Optional[datetime.datetime] = None

@dataclass
class OrganicProduct:
    """有机产品信息"""
    product_id: str
    alliance_id: str
    name: str
    category: ProductCategory
    price: float
    unit: str
    stock: int
    organic_cert: List[str]
    producer: Dict[str, Any]
    description: str
    images: List[str]
    ratings: float = 5.0
    created_at: datetime.datetime = datetime.datetime.now()
    last_updated: datetime.datetime = datetime.datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "product_id": self.product_id,
            "alliance_id": self.alliance_id,
            "name": self.name,
            "category": self.category.value,
            "price": self.price,
            "unit": self.unit,
            "stock": self.stock,
            "organic_cert": self.organic_cert,
            "producer": self.producer,
            "description": self.description,
            "images": self.images,
            "ratings": self.ratings,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrganicProduct':
        """从字典创建实例"""
        category = ProductCategory(data["category"]) if isinstance(data["category"], str) else data["category"]
        created_at = datetime.datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"]
        last_updated = datetime.datetime.fromisoformat(data["last_updated"]) if isinstance(data["last_updated"], str) else data["last_updated"]
        
        return cls(
            product_id=data["product_id"],
            alliance_id=data["alliance_id"],
            name=data["name"],
            category=category,
            price=data["price"],
            unit=data["unit"],
            stock=data["stock"],
            organic_cert=data["organic_cert"],
            producer=data["producer"],
            description=data["description"],
            images=data["images"],
            ratings=data["ratings"],
            created_at=created_at,
            last_updated=last_updated
        )

class AllianceConnector:
    """外部联盟连接器"""
    
    # 已知的有机食品联盟API配置
    ALLIANCE_CONFIGS = {
        "organic_china": {
            "name": "中国有机食品联盟",
            "base_url": "https://api.organic-china.org/v1",
            "products_endpoint": "/products",
            "auth_endpoint": "/auth",
            "verification_endpoint": "/verify"
        },
        "global_organic": {
            "name": "全球有机农业联盟",
            "base_url": "https://api.global-organic.com/v2",
            "products_endpoint": "/catalog/organic",
            "auth_endpoint": "/connect/token",
            "verification_endpoint": "/certification/check"
        },
        "eco_farmers": {
            "name": "生态农业协会",
            "base_url": "https://ecofarmer-api.cn/api",
            "products_endpoint": "/eco-products",
            "auth_endpoint": "/login",
            "verification_endpoint": "/cert-verify"
        }
    }
    
    def __init__(self, alliance_id: str, api_key: str, account_id: str = None):
        """初始化联盟连接器
        
        Args:
            alliance_id: 联盟ID
            api_key: API密钥
            account_id: 账号ID
        """
        if alliance_id not in self.ALLIANCE_CONFIGS:
            raise ValueError(f"不支持的联盟ID: {alliance_id}")
        
        self.alliance_id = alliance_id
        self.api_key = api_key
        self.account_id = account_id
        self.config = self.ALLIANCE_CONFIGS[alliance_id]
        self.session = requests.Session()
        self.token = None
        self.token_expires = None
        
        logger.info(f"初始化联盟连接器: {self.config['name']}")
    
    def authenticate(self) -> bool:
        """认证并获取访问令牌
        
        Returns:
            认证是否成功
        """
        try:
            # 为了开发环境模拟，实际实现应当使用真实API
            logger.info(f"模拟认证: {self.config['name']}")
            self.token = f"mock_token_{self.alliance_id}_{datetime.datetime.now().timestamp()}"
            self.token_expires = datetime.datetime.now() + datetime.timedelta(hours=1)
            return True
            
            # 实际实现可能类似如下：
            # url = f"{self.config['base_url']}{self.config['auth_endpoint']}"
            # response = self.session.post(url, json={
            #     "api_key": self.api_key,
            #     "account_id": self.account_id
            # })
            # if response.status_code == 200:
            #     data = response.json()
            #     self.token = data.get("access_token")
            #     expires_in = data.get("expires_in", 3600)
            #     self.token_expires = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
            #     return True
            # return False
        except Exception as e:
            logger.error(f"联盟认证失败: {e}")
            return False
    
    def get_organic_products(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取有机产品列表
        
        Args:
            filters: 筛选条件
            
        Returns:
            有机产品列表
        """
        # 检查并更新令牌
        if not self.token or (self.token_expires and self.token_expires < datetime.datetime.now()):
            if not self.authenticate():
                logger.error("无法获取有效令牌，无法获取产品数据")
                return []
        
        # 模拟从API获取数据
        # 实际实现应连接真实API
        mock_products = self._get_mock_products(filters)
        logger.info(f"从{self.config['name']}获取了{len(mock_products)}个有机产品")
        return mock_products
    
    def verify_product(self, product_id: str) -> Dict[str, Any]:
        """验证产品有机认证
        
        Args:
            product_id: 产品ID
            
        Returns:
            验证结果
        """
        # 模拟验证
        return {
            "product_id": product_id,
            "verified": True,
            "certification": ["有机认证", "绿色食品", "无公害"],
            "valid_until": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
        }
    
    def _get_mock_products(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取模拟产品数据（仅开发环境使用）
        
        Args:
            filters: 筛选条件
            
        Returns:
            模拟产品列表
        """
        # 模拟数据
        mock_data = []
        categories = [cat for cat in ProductCategory]
        
        # 根据联盟生成不同风格的产品
        if self.alliance_id == "organic_china":
            products = [
                {"name": "有机菠菜", "category": ProductCategory.VEGETABLES, "price": 12.5},
                {"name": "有机红薯", "category": ProductCategory.VEGETABLES, "price": 8.8},
                {"name": "有机糙米", "category": ProductCategory.GRAINS, "price": 25.0},
                {"name": "有机鸡蛋", "category": ProductCategory.MEAT, "price": 28.0},
                {"name": "有机酸奶", "category": ProductCategory.DAIRY, "price": 15.0}
            ]
        elif self.alliance_id == "global_organic":
            products = [
                {"name": "进口有机蓝莓", "category": ProductCategory.VEGETABLES, "price": 45.0},
                {"name": "进口有机牛肉", "category": ProductCategory.MEAT, "price": 120.0},
                {"name": "进口有机蜂蜜", "category": ProductCategory.HEALTH, "price": 88.0},
                {"name": "进口有机麦片", "category": ProductCategory.GRAINS, "price": 35.0},
                {"name": "进口有机葡萄酒", "category": ProductCategory.DRINKS, "price": 198.0}
            ]
        else:  # eco_farmers
            products = [
                {"name": "生态有机青菜", "category": ProductCategory.VEGETABLES, "price": 9.9},
                {"name": "生态有机鲜奶", "category": ProductCategory.DAIRY, "price": 18.0},
                {"name": "生态有机小麦粉", "category": ProductCategory.GRAINS, "price": 22.0},
                {"name": "生态有机鸡肉", "category": ProductCategory.MEAT, "price": 45.0},
                {"name": "生态有机坚果", "category": ProductCategory.SNACKS, "price": 32.0}
            ]
        
        # 生成完整产品数据
        for i, p in enumerate(products):
            product_id = f"{self.alliance_id}_p{i+1}"
            product = {
                "product_id": product_id,
                "alliance_id": self.alliance_id,
                "name": p["name"],
                "category": p["category"].value,
                "price": p["price"],
                "unit": "500g" if "菜" in p["name"] else "袋" if "米" in p["name"] else "盒",
                "stock": 100 + i * 10,
                "organic_cert": ["有机认证", "绿色食品"],
                "producer": {
                    "name": f"{self.config['name']}认证生产商{i+1}",
                    "location": "北京" if i % 3 == 0 else "上海" if i % 3 == 1 else "广州",
                    "id": f"prod_{self.alliance_id}_{i+1}"
                },
                "description": f"优质{p['name']}，采用纯天然种植方式，无农药、无化肥、无添加剂。",
                "images": [f"/SOM/templates/images/products/{product_id}_{j}.jpg" for j in range(1, 4)],
                "ratings": 4.5 + (i % 10) / 20,
                "created_at": datetime.datetime.now().isoformat(),
                "last_updated": datetime.datetime.now().isoformat()
            }
            mock_data.append(product)
        
        # 应用筛选条件
        if filters:
            filtered_data = []
            for product in mock_data:
                match = True
                
                for key, value in filters.items():
                    if key == "category" and value:
                        if isinstance(value, list):
                            if product["category"] not in [cat.value for cat in value]:
                                match = False
                                break
                        elif product["category"] != value.value:
                            match = False
                            break
                    elif key == "min_price" and value:
                        if product["price"] < value:
                            match = False
                            break
                    elif key == "max_price" and value:
                        if product["price"] > value:
                            match = False
                            break
                    elif key == "keyword" and value:
                        if value.lower() not in product["name"].lower() and value.lower() not in product["description"].lower():
                            match = False
                            break
                
                if match:
                    filtered_data.append(product)
            
            return filtered_data
        
        return mock_data


class SomMarketplace:
    """松麦生态商城核心实现"""
    
    def __init__(self, db_path: str = None, traceability_system: SomTraceabilitySystem = None):
        """初始化松麦生态商城
        
        Args:
            db_path: 数据存储路径
            traceability_system: 追溯系统实例
        """
        self.db_path = db_path or "marketplace_data.json"
        self.traceability_system = traceability_system
        
        # 账号绑定信息
        self.alliance_accounts = {}
        
        # 产品数据库
        self.products = {}
        
        # 用户推荐历史
        self.user_recommendations = {}
        
        # 加载数据
        self._load_data()
        
        logger.info("松麦生态商城初始化完成")
    
    def _load_data(self):
        """从文件加载数据"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 加载联盟账号
                for account_id, account_data in data.get("alliance_accounts", {}).items():
                    self.alliance_accounts[account_id] = AllianceAccount(
                        alliance_id=account_data["alliance_id"],
                        alliance_name=account_data["alliance_name"],
                        api_key=account_data["api_key"],
                        account_id=account_data["account_id"],
                        status=account_data["status"],
                        binding_time=datetime.datetime.fromisoformat(account_data["binding_time"]),
                        last_sync_time=datetime.datetime.fromisoformat(account_data["last_sync_time"]) 
                            if account_data.get("last_sync_time") else None
                    )
                
                # 加载产品
                for product_id, product_data in data.get("products", {}).items():
                    self.products[product_id] = OrganicProduct.from_dict(product_data)
                
                # 加载用户推荐历史
                self.user_recommendations = data.get("user_recommendations", {})
                
                logger.info(f"从{self.db_path}加载了{len(self.alliance_accounts)}个联盟账号和{len(self.products)}个产品")
            except Exception as e:
                logger.error(f"加载数据失败: {e}")
    
    def _save_data(self):
        """保存数据到文件"""
        try:
            data = {
                "alliance_accounts": {},
                "products": {},
                "user_recommendations": self.user_recommendations
            }
            
            # 保存联盟账号
            for account_id, account in self.alliance_accounts.items():
                data["alliance_accounts"][account_id] = {
                    "alliance_id": account.alliance_id,
                    "alliance_name": account.alliance_name,
                    "api_key": account.api_key,
                    "account_id": account.account_id,
                    "status": account.status,
                    "binding_time": account.binding_time.isoformat(),
                    "last_sync_time": account.last_sync_time.isoformat() if account.last_sync_time else None
                }
            
            # 保存产品
            for product_id, product in self.products.items():
                data["products"][product_id] = product.to_dict()
            
            # 保存到文件
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存到{self.db_path}")
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
    
    def bind_alliance_account(self, alliance_id: str, api_key: str, account_id: str) -> Dict[str, Any]:
        """绑定联盟账号
        
        Args:
            alliance_id: 联盟ID
            api_key: API密钥
            account_id: 账号ID
            
        Returns:
            绑定结果
        """
        # 验证联盟ID是否有效
        if alliance_id not in AllianceConnector.ALLIANCE_CONFIGS:
            return {
                "success": False,
                "message": f"不支持的联盟ID: {alliance_id}"
            }
        
        # 创建连接器并验证
        try:
            connector = AllianceConnector(alliance_id, api_key, account_id)
            if not connector.authenticate():
                return {
                    "success": False,
                    "message": "认证失败，请检查API密钥和账号ID"
                }
            
            # 生成唯一标识
            binding_id = f"{alliance_id}_{account_id}"
            
            # 保存账号信息
            self.alliance_accounts[binding_id] = AllianceAccount(
                alliance_id=alliance_id,
                alliance_name=connector.config["name"],
                api_key=api_key,
                account_id=account_id,
                status="active",
                binding_time=datetime.datetime.now()
            )
            
            # 保存数据
            self._save_data()
            
            return {
                "success": True,
                "binding_id": binding_id,
                "message": f"成功绑定{connector.config['name']}账号",
                "alliance_name": connector.config["name"]
            }
        except Exception as e:
            logger.error(f"绑定联盟账号失败: {e}")
            return {
                "success": False,
                "message": f"绑定失败: {str(e)}"
            }
    
    def sync_organic_products(self, binding_id: str = None, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """同步有机产品数据
        
        Args:
            binding_id: 绑定标识，不提供则同步所有绑定账号
            filters: 筛选条件
            
        Returns:
            同步结果
        """
        sync_results = {}
        binding_ids = [binding_id] if binding_id else list(self.alliance_accounts.keys())
        
        for b_id in binding_ids:
            if b_id not in self.alliance_accounts:
                sync_results[b_id] = {
                    "success": False,
                    "message": f"未找到绑定账号: {b_id}"
                }
                continue
            
            account = self.alliance_accounts[b_id]
            
            try:
                # 创建连接器
                connector = AllianceConnector(
                    account.alliance_id, 
                    account.api_key, 
                    account.account_id
                )
                
                # 获取产品数据
                products_data = connector.get_organic_products(filters)
                
                # 转换并存储产品
                imported_count = 0
                for product_data in products_data:
                    product = OrganicProduct.from_dict(product_data)
                    self.products[product.product_id] = product
                    imported_count += 1
                
                # 更新同步时间
                account.last_sync_time = datetime.datetime.now()
                
                sync_results[b_id] = {
                    "success": True,
                    "message": f"从{account.alliance_name}导入了{imported_count}个有机产品",
                    "imported_count": imported_count
                }
                
                # 如果有追溯系统，同步产品信息到追溯系统
                if self.traceability_system:
                    for product_data in products_data:
                        try:
                            # 使用追溯系统注册产品和生产者
                            producer_id = self.traceability_system.register_producer(
                                product_data["producer"]["name"],
                                product_data["producer"]
                            )
                            
                            product_id = self.traceability_system.register_product(
                                producer_id,
                                product_data["name"],
                                product_data
                            )
                            
                            # 添加认证信息
                            for cert in product_data["organic_cert"]:
                                self.traceability_system.add_certification(
                                    product_id,
                                    cert,
                                    {
                                        "issued_by": account.alliance_name,
                                        "issue_date": datetime.datetime.now().isoformat(),
                                        "valid_until": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
                                    }
                                )
                        except Exception as e:
                            logger.error(f"同步产品到追溯系统失败: {e}")
                
            except Exception as e:
                logger.error(f"同步{account.alliance_name}产品失败: {e}")
                sync_results[b_id] = {
                    "success": False,
                    "message": f"同步失败: {str(e)}"
                }
        
        # 保存数据
        self._save_data()
        
        return {
            "overall_success": all(result["success"] for result in sync_results.values()),
            "results": sync_results,
            "total_products": len(self.products)
        }
    
    def get_products(self, filters: Dict[str, Any] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取产品列表
        
        Args:
            filters: 筛选条件
            page: 页码
            page_size: 每页数量
            
        Returns:
            产品列表
        """
        # 应用筛选
        filtered_products = list(self.products.values())
        if filters:
            for key, value in filters.items():
                if value is None:
                    continue
                
                if key == "category":
                    if isinstance(value, list):
                        filtered_products = [p for p in filtered_products if p.category in value]
                    else:
                        filtered_products = [p for p in filtered_products if p.category == value]
                elif key == "min_price":
                    filtered_products = [p for p in filtered_products if p.price >= value]
                elif key == "max_price":
                    filtered_products = [p for p in filtered_products if p.price <= value]
                elif key == "alliance_id":
                    filtered_products = [p for p in filtered_products if p.alliance_id == value]
                elif key == "keyword":
                    filtered_products = [p for p in filtered_products if 
                                        value.lower() in p.name.lower() or 
                                        value.lower() in p.description.lower()]
        
        # 计算分页
        total = len(filtered_products)
        total_pages = (total + page_size - 1) // page_size
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        end = min(start + page_size, total)
        
        # 提取当前页数据
        page_data = [p.to_dict() for p in filtered_products[start:end]]
        
        return {
            "products": page_data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages
            }
        }
    
    def get_product_detail(self, product_id: str) -> Dict[str, Any]:
        """获取产品详情
        
        Args:
            product_id: 产品ID
            
        Returns:
            产品详情
        """
        if product_id not in self.products:
            return {
                "success": False,
                "message": f"未找到产品: {product_id}"
            }
        
        product = self.products[product_id]
        result = product.to_dict()
        
        # 如果有追溯系统，获取追溯信息
        if self.traceability_system:
            try:
                trace_info = self.traceability_system.trace_product(product_id)
                result["traceability"] = trace_info
            except Exception as e:
                logger.error(f"获取产品追溯信息失败: {e}")
                result["traceability"] = {"error": "无法获取追溯信息"}
        
        return {
            "success": True,
            "product": result
        }
    
    def get_recommendations(self, user_id: str, count: int = 5) -> Dict[str, Any]:
        """获取推荐产品
        
        Args:
            user_id: 用户ID
            count: 推荐数量
            
        Returns:
            推荐产品列表
        """
        if not self.products:
            return {
                "success": False,
                "message": "没有可推荐的产品"
            }
        
        # 获取用户历史
        user_history = self.user_recommendations.get(user_id, {})
        viewed_products = user_history.get("viewed", [])
        purchased_products = user_history.get("purchased", [])
        
        # 简单推荐算法：基于用户历史记录和产品评分
        all_products = list(self.products.values())
        
        # 计算每个产品的推荐分数
        scored_products = []
        for product in all_products:
            # 已购买的不再推荐
            if product.product_id in purchased_products:
                continue
                
            # 基础分数为产品评分
            score = product.ratings
            
            # 如果用户浏览过，略微降低分数避免重复推荐
            if product.product_id in viewed_products:
                score *= 0.8
            
            # 有机认证数量加分
            score += len(product.organic_cert) * 0.3
            
            scored_products.append((product, score))
        
        # 排序并选择前N个
        scored_products.sort(key=lambda x: x[1], reverse=True)
        recommended_products = [p[0].to_dict() for p in scored_products[:count]]
        
        # 记录推荐历史
        if not user_id in self.user_recommendations:
            self.user_recommendations[user_id] = {"viewed": [], "purchased": []}
        
        self.user_recommendations[user_id]["recommended"] = [p["product_id"] for p in recommended_products]
        self._save_data()
        
        return {
            "success": True,
            "recommendations": recommended_products
        }
    
    def record_user_action(self, user_id: str, action: str, product_id: str) -> Dict[str, Any]:
        """记录用户行为
        
        Args:
            user_id: 用户ID
            action: 行为（viewed/purchased）
            product_id: 产品ID
            
        Returns:
            操作结果
        """
        if product_id not in self.products:
            return {
                "success": False,
                "message": f"未找到产品: {product_id}"
            }
        
        if action not in ["viewed", "purchased"]:
            return {
                "success": False,
                "message": f"不支持的行为: {action}"
            }
        
        # 初始化用户历史
        if user_id not in self.user_recommendations:
            self.user_recommendations[user_id] = {"viewed": [], "purchased": []}
        
        # 记录行为
        action_list = self.user_recommendations[user_id].get(action, [])
        if product_id not in action_list:
            action_list.append(product_id)
        self.user_recommendations[user_id][action] = action_list
        
        # 保存数据
        self._save_data()
        
        return {
            "success": True,
            "message": f"已记录用户{user_id}的{action}行为"
        }
    
    def get_alliance_accounts(self) -> Dict[str, Any]:
        """获取已绑定的联盟账号列表
        
        Returns:
            账号列表
        """
        accounts = []
        for binding_id, account in self.alliance_accounts.items():
            accounts.append({
                "binding_id": binding_id,
                "alliance_id": account.alliance_id,
                "alliance_name": account.alliance_name,
                "account_id": account.account_id,
                "status": account.status,
                "binding_time": account.binding_time.isoformat(),
                "last_sync_time": account.last_sync_time.isoformat() if account.last_sync_time else None
            })
        
        return {
            "success": True,
            "accounts": accounts
        }
    
    def unbind_alliance_account(self, binding_id: str) -> Dict[str, Any]:
        """解绑联盟账号
        
        Args:
            binding_id: 绑定标识
            
        Returns:
            解绑结果
        """
        if binding_id not in self.alliance_accounts:
            return {
                "success": False,
                "message": f"未找到绑定账号: {binding_id}"
            }
        
        # 删除该账号关联的产品
        account = self.alliance_accounts[binding_id]
        alliance_id = account.alliance_id
        
        products_to_remove = []
        for product_id, product in self.products.items():
            if product.alliance_id == alliance_id:
                products_to_remove.append(product_id)
        
        for product_id in products_to_remove:
            del self.products[product_id]
        
        # 解绑账号
        del self.alliance_accounts[binding_id]
        
        # 保存数据
        self._save_data()
        
        return {
            "success": True,
            "message": f"已解绑{account.alliance_name}账号并删除关联产品",
            "removed_products_count": len(products_to_remove)
        }
    
    def get_all_products(self):
        """获取所有产品"""
        return self.products
    
    def get_products_by_filter(self, category=None, alliance=None):
        """根据分类或联盟获取产品"""
        if not category and not alliance:
            return self.get_all_products()
        
        filtered_products = []
        for product_id, product in self.products.items():
            if category and (
                (isinstance(product.category, ProductCategory) and product.category.value == category) or
                (isinstance(product.category, str) and product.category == category)
            ):
                filtered_products.append(product.to_dict())
            elif alliance and product.alliance_id == alliance:
                filtered_products.append(product.to_dict())
                
        return filtered_products


# 测试代码
if __name__ == "__main__":
    # 创建松麦生态商城实例
    marketplace = SomMarketplace()
    
    # 绑定联盟账号
    print("\n1. 绑定联盟账号")
    result1 = marketplace.bind_alliance_account("organic_china", "test_api_key", "test_account")
    print(json.dumps(result1, ensure_ascii=False, indent=2))
    
    result2 = marketplace.bind_alliance_account("global_organic", "test_api_key", "test_account")
    print(json.dumps(result2, ensure_ascii=False, indent=2))
    
    # 同步有机产品
    print("\n2. 同步有机产品")
    sync_result = marketplace.sync_organic_products()
    print(json.dumps(sync_result, ensure_ascii=False, indent=2))
    
    # 获取产品列表
    print("\n3. 获取产品列表")
    products = marketplace.get_products({"category": ProductCategory.VEGETABLES})
    print(f"找到{products['pagination']['total']}个蔬菜水果类产品")
    
    # 获取产品详情
    if products['products']:
        product_id = products['products'][0]['product_id']
        print("\n4. 获取产品详情")
        detail = marketplace.get_product_detail(product_id)
        print(json.dumps(detail, ensure_ascii=False, indent=2))
    
    # 获取推荐
    print("\n5. 获取推荐产品")
    recommendations = marketplace.get_recommendations("test_user", 3)
    print(json.dumps(recommendations, ensure_ascii=False, indent=2))
    
    # 记录用户行为
    if recommendations['success'] and recommendations['recommendations']:
        rec_product_id = recommendations['recommendations'][0]['product_id']
        print("\n6. 记录用户行为")
        action_result = marketplace.record_user_action("test_user", "viewed", rec_product_id)
        print(json.dumps(action_result, ensure_ascii=False, indent=2))
    
    # 获取账号列表
    print("\n7. 获取联盟账号列表")
    accounts = marketplace.get_alliance_accounts()
    print(json.dumps(accounts, ensure_ascii=False, indent=2)) 

"""
"""
量子基因编码: QE-MAR-9D7D2FB9BB09
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
