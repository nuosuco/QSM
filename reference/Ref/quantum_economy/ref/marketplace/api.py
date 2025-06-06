"""
松麦生态商城API接口

提供松麦生态商城的API接口，用于前端交互，包括有机食品联盟账号绑定、产品同步、筛选与推荐等功能。
"""

import json
import logging
from flask import Blueprint, jsonify, request, current_app, g
from functools import wraps
from enum import Enum

# 导入松麦生态商城核心
<<<<<<< HEAD
from quantum_economy.Ref.marketplace.marketplace_core import SomMarketplace, ProductCategory, AllianceConnector
=======
from quantum_economy.ref.marketplace.marketplace_core import SomMarketplace, ProductCategory, AllianceConnector
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("marketplace_api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MarketplaceAPI")

# 创建蓝图
marketplace_api = Blueprint('marketplace_api', __name__)

# 辅助函数：需要验证的API
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '缺少或无效的令牌'}), 401
        
        token = auth_header.split(' ')[1]
        
        # 在实际应用中，这里应该验证token
        try:
            # 简化处理：假设token验证通过
            # 实际应用中，应该验证token并获取用户ID
            g.user_id = "test_user"  # 开发环境
        except Exception as e:
            logger.error(f"Token验证失败: {e}")
            return jsonify({'error': 'Token验证失败'}), 401
            
        return f(*args, **kwargs)
    return decorated

# 获取商城实例
def get_marketplace():
    if hasattr(current_app, 'marketplace'):
        return current_app.marketplace
    
    # 如果没有初始化，则创建一个新实例
    logger.warning("松麦生态商城未在应用上下文中初始化，创建新实例")
    marketplace = SomMarketplace()
    current_app.marketplace = marketplace
    return marketplace

# API路由：绑定联盟账号
@marketplace_api.route('/alliance/bind', methods=['POST'])
@require_auth
def bind_alliance_account():
    """绑定联盟账号"""
    try:
        data = request.json
        if not data or not all(k in data for k in ['alliance_id', 'api_key', 'account_id']):
            return jsonify({"error": "缺少必要参数"}), 400
        
        marketplace = get_marketplace()
        result = marketplace.bind_alliance_account(
            data['alliance_id'],
            data['api_key'],
            data['account_id']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"绑定联盟账号失败: {e}")
        return jsonify({"error": f"绑定失败: {str(e)}"}), 500

# API路由：获取已绑定的联盟账号
@marketplace_api.route('/alliance/list', methods=['GET'])
@require_auth
def get_alliance_accounts():
    """获取已绑定的联盟账号列表"""
    try:
        marketplace = get_marketplace()
        result = marketplace.get_alliance_accounts()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"获取联盟账号列表失败: {e}")
        return jsonify({"error": f"获取失败: {str(e)}"}), 500

# API路由：解绑联盟账号
@marketplace_api.route('/alliance/unbind/<binding_id>', methods=['DELETE'])
@require_auth
def unbind_alliance_account(binding_id):
    """解绑联盟账号"""
    try:
        marketplace = get_marketplace()
        result = marketplace.unbind_alliance_account(binding_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"解绑联盟账号失败: {e}")
        return jsonify({"error": f"解绑失败: {str(e)}"}), 500

# API路由：同步有机产品
@marketplace_api.route('/products/sync', methods=['POST'])
@require_auth
def sync_organic_products():
    """同步有机产品"""
    try:
        data = request.json or {}
        binding_id = data.get('binding_id')
        filters = data.get('filters')
        
        marketplace = get_marketplace()
        result = marketplace.sync_organic_products(binding_id, filters)
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"同步有机产品失败: {e}")
        return jsonify({"error": f"同步失败: {str(e)}"}), 500

# API路由：获取产品列表
@marketplace_api.route('/products', methods=['GET'])
def get_products():
    """获取产品列表"""
    try:
        # 解析查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 筛选条件
        filters = {}
        
        # 类别筛选
        category = request.args.get('category')
        if category:
            try:
                filters['category'] = ProductCategory(category)
            except ValueError:
                pass
        
        # 价格范围
        min_price = request.args.get('min_price')
        if min_price:
            filters['min_price'] = float(min_price)
            
        max_price = request.args.get('max_price')
        if max_price:
            filters['max_price'] = float(max_price)
        
        # 联盟筛选
        alliance_id = request.args.get('alliance_id')
        if alliance_id:
            filters['alliance_id'] = alliance_id
        
        # 关键词搜索
        keyword = request.args.get('keyword')
        if keyword:
            filters['keyword'] = keyword
        
        marketplace = get_marketplace()
        result = marketplace.get_products(filters, page, page_size)
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"获取产品列表失败: {e}")
        return jsonify({"error": f"获取失败: {str(e)}"}), 500

# API路由：获取产品详情
@marketplace_api.route('/products/<product_id>', methods=['GET'])
def get_product_detail(product_id):
    """获取产品详情"""
    try:
        marketplace = get_marketplace()
        result = marketplace.get_product_detail(product_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"获取产品详情失败: {e}")
        return jsonify({"error": f"获取失败: {str(e)}"}), 500

# API路由：获取推荐产品
@marketplace_api.route('/recommendations', methods=['GET'])
@require_auth
def get_recommendations():
    """获取推荐产品"""
    try:
        user_id = g.user_id
        count = int(request.args.get('count', 5))
        
        marketplace = get_marketplace()
        result = marketplace.get_recommendations(user_id, count)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"获取推荐失败: {e}")
        return jsonify({"error": f"获取失败: {str(e)}"}), 500

# API路由：记录用户行为
@marketplace_api.route('/user/action', methods=['POST'])
@require_auth
def record_user_action():
    """记录用户行为"""
    try:
        data = request.json
        if not data or not all(k in data for k in ['action', 'product_id']):
            return jsonify({"error": "缺少必要参数"}), 400
        
        user_id = g.user_id
        action = data['action']
        product_id = data['product_id']
        
        marketplace = get_marketplace()
        result = marketplace.record_user_action(user_id, action, product_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"记录用户行为失败: {e}")
        return jsonify({"error": f"记录失败: {str(e)}"}), 500

# API路由：获取联盟列表
@marketplace_api.route('/alliance/available', methods=['GET'])
def get_available_alliances():
    """获取可用的联盟列表"""
    try:
        # 返回可用的联盟信息
        available_alliances = []
        for alliance_id, config in AllianceConnector.ALLIANCE_CONFIGS.items():
            available_alliances.append({
                "alliance_id": alliance_id,
                "name": config["name"],
                "description": f"{config['name']}是专注于有机食品认证和流通的权威机构"
            })
        
        return jsonify({
            "success": True,
            "alliances": available_alliances
        }), 200
    except Exception as e:
        logger.error(f"获取可用联盟列表失败: {e}")
        return jsonify({"error": f"获取失败: {str(e)}"}), 500

# API路由：获取有机产品类别
@marketplace_api.route('/products/categories', methods=['GET'])
def get_product_categories():
    """获取有机产品类别"""
    try:
        categories = []
        for category in ProductCategory:
            categories.append({
                "id": category.name,
                "name": category.value
            })
        
        return jsonify({
            "success": True,
            "categories": categories
        }), 200
    except Exception as e:
        logger.error(f"获取产品类别失败: {e}")
        return jsonify({"error": f"获取失败: {str(e)}"}), 500 

"""

"""
量子基因编码: QE-API-6FE9B0A9EAC6
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
