"""
松麦币(SOM)API接口

提供松麦币相关的API接口，用于与前端交互，包括查询币值、发行统计、用户余额等功能。
"""

import json
import logging
from decimal import Decimal
from flask import Blueprint, jsonify, request, current_app
from functools import wraps
import datetime

# 导入松麦币发行系统
from quantum_economy.ref.coin.ref_coin import SomCoinEmission, SomCoinRewardDistributor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ref_coin_api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SomCoinAPI")

# 创建蓝图
ref_coin_api = Blueprint('ref_coin_api', __name__)

# 辅助函数：需要验证的API
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        
        token = auth_header.split(' ')[1]
        
        # 在实际应用中，这里应该验证token
        # 此处简化处理
        try:
            # 验证token
            if not token:
                return jsonify({'error': 'Invalid token'}), 401
                
            # 将token存储在g对象上，以便在路由中使用
            # g.user_id = user_id
            pass
                
        except Exception as e:
            logger.error(f"Token验证失败: {e}")
            return jsonify({'error': 'Token authentication failed'}), 401
            
        return f(*args, **kwargs)
    return decorated

# 获取应用上下文中的松麦币发行系统
def get_emission_system():
    # 这里假设在应用上下文中已经初始化了松麦币发行系统
    # 在实际应用中，您可能需要根据应用的结构进行调整
    if hasattr(current_app, 'ref_coin_emission'):
        return current_app.ref_coin_emission
    
    # 如果还没有初始化，则创建一个新的实例
    # 注意：这是一个简化的处理方式，实际应用中应确保只有一个实例
    logger.warning("松麦币发行系统未在应用上下文中初始化，创建新实例")
    emission_system = SomCoinEmission()
    current_app.ref_coin_emission = emission_system
    return emission_system

# 获取应用上下文中的松麦币奖励分配器
def get_reward_distributor():
    if hasattr(current_app, 'ref_coin_reward_distributor'):
        return current_app.ref_coin_reward_distributor
    
    emission_system = get_emission_system()
    reward_distributor = SomCoinRewardDistributor(emission_system)
    current_app.ref_coin_reward_distributor = reward_distributor
    return reward_distributor

# API路由：获取松麦币信息
@ref_coin_api.route('/info', methods=['GET'])
def get_coin_info():
    """获取松麦币基本信息"""
    try:
        emission_system = get_emission_system()
        stats = emission_system.get_supply_stats()
        
        # 添加一些额外信息
        info = {
            "name": "松麦币",
            "symbol": "SOM",
            "decimals": 8,
            "logo": "/static/images/ref-coin-logo.png",
            "description": "松麦生态系统的核心通证，基于量子区块链技术",
            "website": "https://ref.example.org",
            "current_value": "1.0",  # 示例值，实际应用中可能需要从市场获取
            "stats": stats
        }
        
        return jsonify(info), 200
    except Exception as e:
        logger.error(f"获取松麦币信息失败: {e}")
        return jsonify({"error": "Internal server error"}), 500

# API路由：获取松麦币经济参数
@ref_coin_api.route('/parameters', methods=['GET'])
def get_coin_parameters():
    """获取松麦币经济参数"""
    try:
        emission_system = get_emission_system()
        params = emission_system.params
        
        parameters = {
            "block_time": str(params.BLOCK_TIME),
            "max_supply": str(params.MAX_SUPPLY),
            "initial_supply": str(params.INITIAL_SUPPLY),
            "alpha": str(params.ALPHA),
            "beta": str(params.BETA),
            "gamma": str(params.GAMMA),
            "inflation_rate": str(params.INFLATION_RATE),
            "lambda": str(params.LAMBDA),
            "k": str(params.K),
            "kappa": str(params.KAPPA)
        }
        
        return jsonify(parameters), 200
    except Exception as e:
        logger.error(f"获取松麦币参数失败: {e}")
        return jsonify({"error": "Internal server error"}), 500

# API路由：获取松麦币发行统计
@ref_coin_api.route('/emission-stats', methods=['GET'])
def get_emission_stats():
    """获取松麦币发行统计"""
    try:
        emission_system = get_emission_system()
        
        # 从系统状态获取总供应量和发行历史
        total_supply = str(emission_system.total_supply)
        start_time = emission_system.start_time.isoformat()
        
        # 提取最近的贡献数据
        recent_contributions = {}
        for dim in emission_system.contribution_metrics:
            metrics = emission_system.contribution_metrics[dim]
            if metrics:
                recent_contributions[dim] = metrics[-10:]  # 最近10条记录
            else:
                recent_contributions[dim] = []
        
        # 计算日供应增长
        now = datetime.datetime.now()
        days = (now - emission_system.start_time).days or 1  # 避免除以零
        daily_growth = str(Decimal(total_supply) / Decimal(str(days)))
        
        stats = {
            "total_supply": total_supply,
            "start_time": start_time,
            "days_running": days,
            "daily_average_growth": daily_growth,
            "max_allowed_supply": str(emission_system.max_allowed_supply()),
            "recent_contributions": recent_contributions,
            "percent_of_max": str(Decimal(total_supply) / Decimal(str(emission_system.params.MAX_SUPPLY)) * 100) + "%"
        }
        
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"获取松麦币发行统计失败: {e}")
        return jsonify({"error": "Internal server error"}), 500

# API路由：获取用户余额
@ref_coin_api.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    """获取特定地址的松麦币余额"""
    try:
        emission_system = get_emission_system()
        
        # 在实际应用中，这里应该从区块链或数据库查询余额
        # 这里简化处理，假设有一个接口
        if emission_system.economy_chain:
            balance = emission_system.economy_chain.get_balance(address, 'SOM')
        else:
            # 模拟数据，仅用于开发阶段
            import random
            balance = random.uniform(10, 1000)
        
        # 获取交易历史（模拟数据）
        transactions = _get_mock_transactions(address)
        
        response = {
            "address": address,
            "balance": str(balance),
            "last_updated": datetime.datetime.now().isoformat(),
            "transactions": transactions[:5]  # 最近5笔交易
        }
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"获取余额失败: {e}")
        return jsonify({"error": "Internal server error"}), 500

# API路由：获取用户交易历史
@ref_coin_api.route('/transactions/<address>', methods=['GET'])
def get_transactions(address):
    """获取特定地址的交易历史"""
    try:
        # 分页参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # 在实际应用中，这里应该从区块链或数据库查询交易历史
        # 这里简化处理，使用模拟数据
        transactions = _get_mock_transactions(address)
        
        # 分页处理
        start = (page - 1) * limit
        end = start + limit
        paginated_txs = transactions[start:end]
        
        response = {
            "address": address,
            "transactions": paginated_txs,
            "total": len(transactions),
            "page": page,
            "limit": limit,
            "pages": (len(transactions) + limit - 1) // limit
        }
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"获取交易历史失败: {e}")
        return jsonify({"error": "Internal server error"}), 500

# API路由：创建转账交易
@ref_coin_api.route('/transfer', methods=['POST'])
@require_auth
def create_transfer():
    """创建松麦币转账交易"""
    try:
        data = request.json
        
        if not data or not all(k in data for k in ['from_address', 'to_address', 'amount']):
            return jsonify({"error": "Missing required parameters"}), 400
        
        from_address = data['from_address']
        to_address = data['to_address']
        amount = Decimal(str(data['amount']))
        memo = data.get('memo', '')
        
        # 在实际应用中，这里应该调用区块链进行转账
        # 这里简化处理
        emission_system = get_emission_system()
        
        if emission_system.economy_chain:
            # 使用经济链进行转账
            try:
                tx_id = emission_system.economy_chain.transfer_ref_coin(
                    from_address, to_address, float(amount), memo
                )
                
                if tx_id:
                    return jsonify({
                        "success": True,
                        "tx_id": tx_id,
                        "from": from_address,
                        "to": to_address,
                        "amount": str(amount),
                        "timestamp": datetime.datetime.now().isoformat()
                    }), 200
                else:
                    return jsonify({"error": "Transaction failed"}), 400
            
            except Exception as e:
                logger.error(f"转账失败: {e}")
                return jsonify({"error": str(e)}), 400
        else:
            # 无链模式，返回模拟数据
            import uuid
            tx_id = str(uuid.uuid4())
            
            return jsonify({
                "success": True,
                "tx_id": tx_id,
                "from": from_address,
                "to": to_address,
                "amount": str(amount),
                "timestamp": datetime.datetime.now().isoformat(),
                "note": "This is a simulated transaction (no blockchain)"
            }), 200
            
    except Exception as e:
        logger.error(f"创建转账失败: {e}")
        return jsonify({"error": "Internal server error"}), 500

# API路由：提交贡献数据
@ref_coin_api.route('/contribute', methods=['POST'])
@require_auth
def submit_contribution():
    """提交贡献数据，用于松麦币发行计算"""
    try:
        data = request.json
        
        if not data or 'contribution_data' not in data:
            return jsonify({"error": "Missing contribution data"}), 400
        
        contribution_data = data['contribution_data']
        address = data.get('address', 'community_pool')
        
        # 处理贡献数据
        emission_system = get_emission_system()
        
        # 处理一个区块，使用提交的贡献数据
        emission_amount = emission_system.process_block(contribution_data)
        
        response = {
            "success": True,
            "emission_amount": str(emission_amount),
            "timestamp": datetime.datetime.now().isoformat(),
            "contribution_data": contribution_data
        }
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"提交贡献数据失败: {e}")
        return jsonify({"error": "Internal server error"}), 500

# API路由：请求特定贡献的奖励
@ref_coin_api.route('/reward', methods=['POST'])
@require_auth
def request_reward():
    """为特定贡献请求松麦币奖励"""
    try:
        data = request.json
        
        if not data or not all(k in data for k in ['address', 'contribution_type', 'value']):
            return jsonify({"error": "Missing required parameters"}), 400
        
        address = data['address']
        contribution_type = data['contribution_type']
        value = Decimal(str(data['value']))
        
        # 验证贡献类型
        valid_types = ['tech', 'social', 'governance']
        if contribution_type not in valid_types:
            return jsonify({"error": f"Invalid contribution type. Must be one of: {valid_types}"}), 400
        
        # 处理奖励请求
        reward_distributor = get_reward_distributor()
        result = reward_distributor.reward_for_contribution(address, contribution_type, value)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"请求奖励失败: {e}")
        return jsonify({"error": "Internal server error"}), 500

# API路由：分配团队奖励
@ref_coin_api.route('/distribute-rewards', methods=['POST'])
@require_auth
def distribute_team_rewards():
    """向团队成员分配松麦币奖励"""
    try:
        data = request.json
        
        if not data or 'contributors' not in data or 'total_reward' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
        
        contributors = data['contributors']
        total_reward = Decimal(str(data['total_reward']))
        
        # 验证贡献者数据
        if not isinstance(contributors, list) or not contributors:
            return jsonify({"error": "Contributors must be a non-empty list"}), 400
        
        for c in contributors:
            if not isinstance(c, dict) or 'address' not in c or 'weight' not in c:
                return jsonify({"error": "Each contributor must have address and weight"}), 400
        
        # 分配奖励
        reward_distributor = get_reward_distributor()
        result = reward_distributor.distribute_rewards(contributors, total_reward)
        
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"分配团队奖励失败: {e}")
        return jsonify({"error": "Internal server error"}), 500

# 辅助函数：生成模拟交易数据（仅用于开发阶段）
def _get_mock_transactions(address):
    """生成模拟交易数据"""
    import random
    
    tx_types = ['transfer', 'reward', 'mint', 'burn']
    
    transactions = []
    
    # 生成一些随机交易
    for i in range(30):
        tx_type = random.choice(tx_types)
        
        # 基本交易数据
        tx = {
            "tx_id": f"tx_{address[:5]}_{i}",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(days=i, hours=random.randint(0, 23))).isoformat(),
            "type": tx_type,
        }
        
        # 根据交易类型添加不同字段
        if tx_type == 'transfer':
            tx.update({
                "from": address if random.random() > 0.5 else f"other_address_{i}",
                "to": f"other_address_{i}" if tx["from"] == address else address,
                "amount": str(random.uniform(1, 100)),
                "fee": str(random.uniform(0.001, 0.01))
            })
        elif tx_type == 'reward':
            tx.update({
                "to": address,
                "amount": str(random.uniform(0.1, 10)),
                "source": random.choice(['tech', 'social', 'governance']),
                "contribution_value": str(random.uniform(1, 5))
            })
        elif tx_type == 'mint':
            tx.update({
                "to": address,
                "amount": str(random.uniform(10, 1000)),
                "reason": "Block emission"
            })
        elif tx_type == 'burn':
            tx.update({
                "from": address,
                "amount": str(random.uniform(1, 50)),
                "reason": random.choice(["Fee", "Voluntary burn", "Expired tokens"])
            })
        
        transactions.append(tx)
    
    # 按时间排序，最新的在前
    transactions.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return transactions 

"""

"""
量子基因编码: QE-SOM-C58FE36EBEBB
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
