import os
import sys
import json
import logging
import datetime
import hashlib
import uuid
import numpy as np
from typing import List, Dict, Any, Optional

# 导入量子区块链模块
from quantum_economy.blockchain.quantum_chain import QuantumChain, QuantumTransaction
from quantum_economy.blockchain.quantum_asset import QuantumAsset

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ref_economy.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SomEconomy")

class SomEconomyModel:
    """松麦经济模型，实现量子区块链经济系统"""
    
    def __init__(self, model_id: str = None):
        """初始化松麦经济模型
        
        Args:
            model_id: 模型唯一标识，如果为None则自动生成
        """
        self.model_id = model_id or self._generate_model_id()
        self.cycle_controller = CycleController()
        self.value_distributor = ValueDistributor()
        self.ecosystem_developer = EcosystemDeveloper()
        self.market_regulator = MarketRegulator()
        self.creation_time = datetime.datetime.now()
        self.chain = None  # 松麦量子链
        self.config = {
            "block_time": 3.14,  # 出块时间(秒)
            "max_supply": 314159265,  # 最大发行量
            "reward_curve": "cos(x) + log(1+x)",  # 奖励曲线
            "initial_value": 1.0,  # 初始价值
            "ecosystem_params": {
                "growth_rate": 0.05,  # 生态增长率
                "balance_factor": 0.8,  # 平衡因子
                "contribution_weight": {
                    "time": 0.3,  # 时间维度权重
                    "technical": 0.4,  # 技术维度权重
                    "social": 0.3  # 社会维度权重
                }
            }
        }
        logger.info(f"初始化松麦经济模型: {self.model_id}")
    
    def _generate_model_id(self) -> str:
        """生成模型唯一标识"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = str(uuid.uuid4())[:8]
        return f"SOM-{timestamp}-{random_str}"
    
    def initialize_chain(self, chain_type: str = "sub") -> QuantumChain:
        """初始化松麦量子链
        
        Args:
            chain_type: 链类型，"main"表示主链，"sub"表示子链
            
        Returns:
            量子链对象
        """
        self.chain = QuantumChain(chain_id=f"SOM-CHAIN-{self.model_id}", chain_type=chain_type)
        logger.info(f"初始化松麦量子链: {self.chain.chain_id}")
        return self.chain
    
    def control_cycle(self) -> bool:
        """控制经济循环
        
        控制松麦经济系统的循环运行
        
        Returns:
            是否成功控制循环
        """
        return self.cycle_controller.control_cycle(self)
    
    def distribute_value(self, distribution_data: Dict) -> bool:
        """分配价值
        
        根据分配数据分配松麦价值
        
        Args:
            distribution_data: 分配数据
            
        Returns:
            是否成功分配
        """
        return self.value_distributor.distribute_value(self, distribution_data)
    
    def develop_ecosystem(self) -> bool:
        """发展生态
        
        发展松麦生态系统
        
        Returns:
            是否成功发展生态
        """
        return self.ecosystem_developer.develop_ecosystem(self)
    
    def regulate_market(self, market_data: Dict) -> bool:
        """调节市场
        
        根据市场数据调节松麦市场
        
        Args:
            market_data: 市场数据
            
        Returns:
            是否成功调节市场
        """
        return self.market_regulator.regulate_market(self, market_data)
    
    def create_ref_coin(self, amount: float, recipient_id: str) -> Optional[QuantumAsset]:
        """创建松麦币
        
        创建指定数量的松麦币并分配给接收者
        
        Args:
            amount: 松麦币数量
            recipient_id: 接收者ID
            
        Returns:
            量子资产对象或None
        """
        # 检查是否超过最大发行量
        current_supply = self.value_distributor.get_total_supply()
        if current_supply + amount > self.config["max_supply"]:
            logger.warning(f"创建松麦币失败: 超过最大发行量 {self.config['max_supply']}")
            return None
        
        # 创建松麦币资产
        ref_coin = QuantumAsset(
            asset_type="SOM_COIN",
            value=amount,
            metadata={
                "recipient_id": recipient_id,
                "creation_time": datetime.datetime.now().isoformat(),
                "model_id": self.model_id,
                "description": "松麦币 - 量子区块链平权经济货币"
            }
        )
        
        # 分配给松麦链
        if self.chain:
            ref_coin.assign_to_chain(self.chain.chain_id)
        
        # 更新总发行量
        self.value_distributor.update_total_supply(amount)
        
        logger.info(f"创建松麦币: {ref_coin.asset_id}, 数量: {amount}, 接收者: {recipient_id}")
        return ref_coin
    
    def calculate_user_reward(self, user_id: str, purchase_amount: float) -> float:
        """计算用户奖励
        
        根据用户购买金额计算松麦币奖励
        
        Args:
            user_id: 用户ID
            purchase_amount: 购买金额
            
        Returns:
            松麦币奖励数量
        """
        # 基础奖励为等值松麦币
        base_reward = purchase_amount
        
        # 获取用户贡献度
        user_contribution = self.value_distributor.get_user_contribution(user_id)
        
        # 根据贡献度调整奖励
        contribution_factor = 1.0 + (user_contribution * 0.1)  # 每10%贡献增加1%奖励
        
        # 计算最终奖励
        final_reward = base_reward * contribution_factor
        
        logger.info(f"计算用户 {user_id} 的奖励: 购买金额={purchase_amount}, 基础奖励={base_reward}, 贡献度={user_contribution}, 最终奖励={final_reward}")
        return final_reward
    
    def process_organic_purchase(self, user_id: str, product_id: str, purchase_amount: float) -> Dict:
        """处理有机产品购买
        
        处理用户购买有机产品的交易，并发放松麦币奖励
        
        Args:
            user_id: 用户ID
            product_id: 产品ID
            purchase_amount: 购买金额
            
        Returns:
            处理结果
        """
        # 计算奖励
        reward_amount = self.calculate_user_reward(user_id, purchase_amount)
        
        # 创建松麦币
        ref_coin = self.create_ref_coin(reward_amount, user_id)
        
        if not ref_coin:
            logger.warning(f"处理购买失败: 无法创建松麦币")
            return {
                "success": False,
                "message": "无法创建松麦币奖励",
                "user_id": user_id,
                "product_id": product_id,
                "purchase_amount": purchase_amount
            }
        
        # 创建购买交易
        purchase_tx_data = {
            "type": "organic_purchase",
            "user_id": user_id,
            "product_id": product_id,
            "purchase_amount": purchase_amount,
            "reward_amount": reward_amount,
            "reward_asset_id": ref_coin.asset_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 创建交易
        if self.chain:
            purchase_tx = QuantumTransaction(tx_data=purchase_tx_data, chain_ids=[self.chain.chain_id])
            self.chain.add_transaction(purchase_tx)
        
        # 更新用户贡献度
        self.value_distributor.update_user_contribution(user_id, purchase_amount * 0.01)  # 每购买100元增加1%贡献度
        
        # 记录购买活动
        self.ecosystem_developer.record_activity({
            "type": "purchase",
            "user_id": user_id,
            "product_id": product_id,
            "amount": purchase_amount,
            "reward": reward_amount,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        logger.info(f"处理用户 {user_id} 购买产品 {product_id}: 金额={purchase_amount}, 奖励={reward_amount}")
        return {
            "success": True,
            "message": "购买处理成功，已发放松麦币奖励",
            "user_id": user_id,
            "product_id": product_id,
            "purchase_amount": purchase_amount,
            "reward_amount": reward_amount,
            "reward_asset_id": ref_coin.asset_id
        }
    
    def register_new_user(self, user_id: str, user_data: Dict) -> Dict:
        """注册新用户
        
        注册新用户并发放初始松麦币
        
        Args:
            user_id: 用户ID
            user_data: 用户数据
            
        Returns:
            注册结果
        """
        # 初始奖励金额
        initial_reward = 100.0  # 每个新用户获得100松麦币
        
        # 创建松麦币
        ref_coin = self.create_ref_coin(initial_reward, user_id)
        
        if not ref_coin:
            logger.warning(f"注册用户失败: 无法创建初始松麦币")
            return {
                "success": False,
                "message": "无法创建初始松麦币奖励",
                "user_id": user_id
            }
        
        # 创建注册交易
        register_tx_data = {
            "type": "user_register",
            "user_id": user_id,
            "user_data": user_data,
            "reward_amount": initial_reward,
            "reward_asset_id": ref_coin.asset_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 创建交易
        if self.chain:
            register_tx = QuantumTransaction(tx_data=register_tx_data, chain_ids=[self.chain.chain_id])
            self.chain.add_transaction(register_tx)
        
        # 初始化用户贡献度
        self.value_distributor.initialize_user_contribution(user_id)
        
        # 记录注册活动
        self.ecosystem_developer.record_activity({
            "type": "register",
            "user_id": user_id,
            "reward": initial_reward,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        logger.info(f"注册新用户 {user_id}: 初始奖励={initial_reward}")
        return {
            "success": True,
            "message": "用户注册成功，已发放初始松麦币",
            "user_id": user_id,
            "reward_amount": initial_reward,
            "reward_asset_id": ref_coin.asset_id
        }
    
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "model_id": self.model_id,
            "creation_time": self.creation_time.isoformat(),
            "config": self.config,
            "chain_id": self.chain.chain_id if self.chain else None,
            "cycle_controller": self.cycle_controller.to_dict(),
            "value_distributor": self.value_distributor.to_dict(),
            "ecosystem_developer": self.ecosystem_developer.to_dict(),
            "market_regulator": self.market_regulator.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SomEconomyModel':
        """从字典恢复模型"""
        model = cls(data["model_id"])
        model.creation_time = datetime.datetime.fromisoformat(data["creation_time"])
        model.config = data["config"]
        
        model.cycle_controller = CycleController.from_dict(data["cycle_controller"])
        model.value_distributor = ValueDistributor.from_dict(data["value_distributor"])
        model.ecosystem_developer = EcosystemDeveloper.from_dict(data["ecosystem_developer"])
        model.market_regulator = MarketRegulator.from_dict(data["market_regulator"])
        
        return model
    
    def save_to_file(self, filepath: str) -> bool:
        """保存模型状态到文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            是否成功保存
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
            logger.info(f"成功保存经济模型状态到 {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存经济模型状态失败: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'SomEconomyModel':
        """从文件加载模型状态
        
        Args:
            filepath: 文件路径
            
        Returns:
            松麦经济模型对象
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.info(f"成功从 {filepath} 加载经济模型状态")
            return cls.from_dict(data)
        except Exception as e:
            logger.error(f"加载经济模型状态失败: {e}")
            return None


class CycleController:
    """循环控制器，负责控制经济循环"""
    
    def __init__(self):
        """初始化循环控制器"""
        self.cycles = []
        self.current_cycle = {
            "cycle_id": self._generate_cycle_id(),
            "start_time": datetime.datetime.now().isoformat(),
            "status": "active",
            "metrics": {}
        }
        logger.info("初始化循环控制器")
    
    def _generate_cycle_id(self) -> str:
        """生成循环唯一标识"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = str(uuid.uuid4())[:4]
        return f"CYCLE-{timestamp}-{random_str}"
    
    def control_cycle(self, economy_model: SomEconomyModel) -> bool:
        """控制循环
        
        Args:
            economy_model: 经济模型
            
        Returns:
            是否成功控制循环
        """
        # 更新当前循环指标
        self.current_cycle["metrics"] = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_supply": economy_model.value_distributor.get_total_supply(),
            "active_users": economy_model.ecosystem_developer.get_active_users_count(),
            "total_transactions": len(economy_model.chain.blocks) if economy_model.chain else 0,
            "market_value": economy_model.market_regulator.get_current_value()
        }
        
        # 检查是否需要结束当前循环
        cycle_start = datetime.datetime.fromisoformat(self.current_cycle["start_time"])
        current_time = datetime.datetime.now()
        
        # 每天一个循环
        if (current_time - cycle_start).days >= 1:
            # 结束当前循环
            self.current_cycle["end_time"] = current_time.isoformat()
            self.current_cycle["status"] = "completed"
            
            # 保存当前循环
            self.cycles.append(self.current_cycle)
            
            # 创建新循环
            self.current_cycle = {
                "cycle_id": self._generate_cycle_id(),
                "start_time": current_time.isoformat(),
                "status": "active",
                "metrics": {}
            }
            
            logger.info(f"结束循环 {self.cycles[-1]['cycle_id']} 并开始新循环 {self.current_cycle['cycle_id']}")
        
        logger.info(f"控制循环 {self.current_cycle['cycle_id']}")
        return True
    
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "cycles": self.cycles,
            "current_cycle": self.current_cycle
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CycleController':
        """从字典恢复控制器"""
        controller = cls()
        controller.cycles = data["cycles"]
        controller.current_cycle = data["current_cycle"]
        return controller


class ValueDistributor:
    """价值分配器，负责分配经济价值"""
    
    def __init__(self):
        """初始化价值分配器"""
        self.total_supply = 0.0
        self.user_contributions = {}
        self.distribution_history = []
        self.time_dimension_formula = "∫(1-e^(-t/κ))dt"
        self.technical_dimension_formula = "Σ(w_i·git_impact)"
        self.social_dimension_formula = "MLP(f(贡献度, 紧急度))"
        self.dynamic_issuance_formula = "dS/dt = α·τ + β·Γ + γ·Ψ"
        logger.info("初始化价值分配器")
    
    def distribute_value(self, economy_model: SomEconomyModel, distribution_data: Dict) -> bool:
        """分配价值
        
        Args:
            economy_model: 经济模型
            distribution_data: 分配数据
            
        Returns:
            是否成功分配
        """
        # 处理分配请求
        distribution_id = f"DIST-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4]}"
        
        # 解析分配数据
        if "type" not in distribution_data or "recipients" not in distribution_data:
            logger.warning("分配数据无效")
            return False
        
        # 计算总分配量
        total_amount = sum(recipient["amount"] for recipient in distribution_data["recipients"])
        
        # 检查是否超过最大发行量
        if self.total_supply + total_amount > economy_model.config["max_supply"]:
            logger.warning(f"分配失败: 超过最大发行量 {economy_model.config['max_supply']}")
            return False
        
        # 进行分配
        successful_recipients = []
        for recipient in distribution_data["recipients"]:
            user_id = recipient["user_id"]
            amount = recipient["amount"]
            
            # 创建松麦币
            ref_coin = economy_model.create_ref_coin(amount, user_id)
            
            if ref_coin:
                # 更新用户贡献度
                self.update_user_contribution(user_id, amount * 0.005)  # 每获得200松麦币增加1%贡献度
                
                successful_recipients.append({
                    "user_id": user_id,
                    "amount": amount,
                    "asset_id": ref_coin.asset_id
                })
        
        # 记录分配历史
        distribution_record = {
            "distribution_id": distribution_id,
            "type": distribution_data["type"],
            "timestamp": datetime.datetime.now().isoformat(),
            "total_amount": total_amount,
            "successful_recipients": successful_recipients
        }
        
        self.distribution_history.append(distribution_record)
        
        # 更新总发行量
        self.update_total_supply(total_amount)
        
        logger.info(f"分配价值: ID={distribution_id}, 类型={distribution_data['type']}, 总量={total_amount}")
        return True
    
    def update_total_supply(self, amount: float):
        """更新总发行量
        
        Args:
            amount: 增加的发行量
        """
        self.total_supply += amount
        logger.debug(f"更新总发行量: +{amount} = {self.total_supply}")
    
    def get_total_supply(self) -> float:
        """获取总发行量
        
        Returns:
            总发行量
        """
        return self.total_supply
    
    def initialize_user_contribution(self, user_id: str):
        """初始化用户贡献度
        
        Args:
            user_id: 用户ID
        """
        self.user_contributions[user_id] = {
            "time": 0.0,  # 时间维度贡献度
            "technical": 0.0,  # 技术维度贡献度
            "social": 0.0,  # 社会维度贡献度
            "total": 0.0,  # 总贡献度
            "last_update": datetime.datetime.now().isoformat()
        }
        logger.debug(f"初始化用户 {user_id} 的贡献度")
    
    def update_user_contribution(self, user_id: str, contribution_delta: float):
        """更新用户贡献度
        
        Args:
            user_id: 用户ID
            contribution_delta: 贡献度增量
        """
        if user_id not in self.user_contributions:
            self.initialize_user_contribution(user_id)
        
        # 更新贡献度
        self.user_contributions[user_id]["total"] += contribution_delta
        self.user_contributions[user_id]["last_update"] = datetime.datetime.now().isoformat()
        
        # 简化版本中，平均分配到三个维度
        dim_delta = contribution_delta / 3
        self.user_contributions[user_id]["time"] += dim_delta
        self.user_contributions[user_id]["technical"] += dim_delta
        self.user_contributions[user_id]["social"] += dim_delta
        
        logger.debug(f"更新用户 {user_id} 的贡献度: +{contribution_delta} = {self.user_contributions[user_id]['total']}")
    
    def get_user_contribution(self, user_id: str) -> float:
        """获取用户贡献度
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户总贡献度
        """
        if user_id not in self.user_contributions:
            return 0.0
        
        return self.user_contributions[user_id]["total"]
    
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "total_supply": self.total_supply,
            "user_contributions": self.user_contributions,
            "distribution_history": self.distribution_history,
            "formulas": {
                "time_dimension": self.time_dimension_formula,
                "technical_dimension": self.technical_dimension_formula,
                "social_dimension": self.social_dimension_formula,
                "dynamic_issuance": self.dynamic_issuance_formula
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ValueDistributor':
        """从字典恢复分配器"""
        distributor = cls()
        distributor.total_supply = data["total_supply"]
        distributor.user_contributions = data["user_contributions"]
        distributor.distribution_history = data["distribution_history"]
        
        formulas = data.get("formulas", {})
        if formulas:
            distributor.time_dimension_formula = formulas.get("time_dimension", distributor.time_dimension_formula)
            distributor.technical_dimension_formula = formulas.get("technical_dimension", distributor.technical_dimension_formula)
            distributor.social_dimension_formula = formulas.get("social_dimension", distributor.social_dimension_formula)
            distributor.dynamic_issuance_formula = formulas.get("dynamic_issuance", distributor.dynamic_issuance_formula)
        
        return distributor


class EcosystemDeveloper:
    """生态发展器，负责发展经济生态"""
    
    def __init__(self):
        """初始化生态发展器"""
        self.activities = []
        self.development_metrics = {
            "user_growth": [],
            "transaction_growth": [],
            "value_growth": []
        }
        self.active_users = set()
        logger.info("初始化生态发展器")
    
    def develop_ecosystem(self, economy_model: SomEconomyModel) -> bool:
        """发展生态
        
        Args:
            economy_model: 经济模型
            
        Returns:
            是否成功发展生态
        """
        current_time = datetime.datetime.now()
        
        # 更新发展指标
        self.development_metrics["user_growth"].append({
            "timestamp": current_time.isoformat(),
            "active_users": len(self.active_users),
            "growth_rate": self._calculate_growth_rate(self.development_metrics["user_growth"], "active_users")
        })
        
        self.development_metrics["transaction_growth"].append({
            "timestamp": current_time.isoformat(),
            "transactions": len(economy_model.chain.blocks) if economy_model.chain else 0,
            "growth_rate": self._calculate_growth_rate(self.development_metrics["transaction_growth"], "transactions")
        })
        
        self.development_metrics["value_growth"].append({
            "timestamp": current_time.isoformat(),
            "total_value": economy_model.value_distributor.get_total_supply(),
            "growth_rate": self._calculate_growth_rate(self.development_metrics["value_growth"], "total_value")
        })
        
        logger.info("发展生态: 更新发展指标")
        return True
    
    def _calculate_growth_rate(self, metrics: List[Dict], key: str) -> float:
        """计算增长率
        
        Args:
            metrics: 指标列表
            key: 指标键
            
        Returns:
            增长率
        """
        if len(metrics) < 2:
            return 0.0
        
        prev_value = metrics[-2][key] if len(metrics) >= 2 else 0
        current_value = metrics[-1][key] if metrics else 0
        
        if prev_value == 0:
            return 1.0 if current_value > 0 else 0.0
        
        return (current_value - prev_value) / prev_value
    
    def record_activity(self, activity: Dict):
        """记录活动
        
        Args:
            activity: 活动数据
        """
        # 添加活动ID
        activity_id = f"ACT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4]}"
        activity["activity_id"] = activity_id
        
        # 记录活动
        self.activities.append(activity)
        
        # 更新活跃用户
        if "user_id" in activity:
            self.active_users.add(activity["user_id"])
        
        logger.debug(f"记录活动: ID={activity_id}, 类型={activity.get('type')}")
    
    def get_active_users_count(self) -> int:
        """获取活跃用户数量
        
        Returns:
            活跃用户数量
        """
        return len(self.active_users)
    
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "activities": self.activities,
            "development_metrics": self.development_metrics,
            "active_users": list(self.active_users)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EcosystemDeveloper':
        """从字典恢复发展器"""
        developer = cls()
        developer.activities = data["activities"]
        developer.development_metrics = data["development_metrics"]
        developer.active_users = set(data["active_users"])
        return developer


class MarketRegulator:
    """市场调节器，负责调节经济市场"""
    
    def __init__(self):
        """初始化市场调节器"""
        self.market_metrics = {
            "price_history": [],
            "volume_history": [],
            "volatility_history": []
        }
        self.current_value = 1.0  # 初始价值
        self.inflation_control = "S_total ≤ K·e^(λt)"  # 通货膨胀控制公式
        logger.info("初始化市场调节器")
    
    def regulate_market(self, economy_model: SomEconomyModel, market_data: Dict) -> bool:
        """调节市场
        
        Args:
            economy_model: 经济模型
            market_data: 市场数据
            
        Returns:
            是否成功调节市场
        """
        current_time = datetime.datetime.now()
        
        # 解析市场数据
        if "price" in market_data:
            self.current_value = market_data["price"]
        
        # 更新市场指标
        self.market_metrics["price_history"].append({
            "timestamp": current_time.isoformat(),
            "price": self.current_value
        })
        
        if "volume" in market_data:
            self.market_metrics["volume_history"].append({
                "timestamp": current_time.isoformat(),
                "volume": market_data["volume"]
            })
        
        # 计算波动率
        volatility = self._calculate_volatility(self.market_metrics["price_history"])
        self.market_metrics["volatility_history"].append({
            "timestamp": current_time.isoformat(),
            "volatility": volatility
        })
        
        logger.info(f"调节市场: 当前价值={self.current_value}, 波动率={volatility}")
        return True
    
    def _calculate_volatility(self, price_history: List[Dict]) -> float:
        """计算波动率
        
        Args:
            price_history: 价格历史
            
        Returns:
            波动率
        """
        if len(price_history) < 2:
            return 0.0
        
        # 获取最近10个价格
        recent_prices = [item["price"] for item in price_history[-10:]]
        
        if not recent_prices:
            return 0.0
        
        # 计算标准差
        mean_price = sum(recent_prices) / len(recent_prices)
        variance = sum((price - mean_price) ** 2 for price in recent_prices) / len(recent_prices)
        return (variance ** 0.5) / mean_price  # 标准差除以均值作为波动率
    
    def get_current_value(self) -> float:
        """获取当前价值
        
        Returns:
            当前价值
        """
        return self.current_value
    
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "market_metrics": self.market_metrics,
            "current_value": self.current_value,
            "inflation_control": self.inflation_control
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MarketRegulator':
        """从字典恢复调节器"""
        regulator = cls()
        regulator.market_metrics = data["market_metrics"]
        regulator.current_value = data["current_value"]
        regulator.inflation_control = data["inflation_control"]
        return regulator 

"""

"""
量子基因编码: QE-SOM-AFF686F1D444
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
