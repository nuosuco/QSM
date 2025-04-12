"""
松麦币发行系统核心实现

本模块实现松麦币(SOM)的发行控制及分配算法，包括：
1. 基于三维贡献度量的发行机制
2. 通货膨胀控制逻辑
3. 奖励分配系统
"""

import os
import math
import json
import logging
import datetime
from decimal import Decimal, getcontext
from typing import Dict, List, Tuple, Any, Optional, Union
import numpy as np

# 设置高精度计算
getcontext().prec = 28

# 导入松麦币核心
from quantum_economy.QSM.coin.QSM_coin import SomCoin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("qsm_coin_emission.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SomCoinEmission")

class EmissionParameters:
    """松麦币发行参数"""
    
    def __init__(self, config_path: str = None):
        """初始化发行参数
        
        Args:
            config_path: 配置文件路径
        """
        # 默认参数
        self.BLOCK_TIME = Decimal('3.14')  # 出块时间(秒)
        self.MAX_SUPPLY = Decimal('314159265')  # 最大发行量
        self.INITIAL_SUPPLY = Decimal('31415926')  # 初始发行量
        self.HALVING_PERIOD = Decimal('3141592')  # 减半周期(区块数)
        self.INFLATION_RATE = Decimal('0.005')  # 年通胀率
        
        # 三维贡献权重
        self.ALPHA = Decimal('0.3')  # 时间维度权重
        self.BETA = Decimal('0.4')  # 技术维度权重
        self.GAMMA = Decimal('0.3')  # 社会维度权重
        
        # 通胀控制参数
        self.K = Decimal('1.05')  # 通胀基数
        self.LAMBDA = Decimal('0.005')  # 指数因子
        
        # 时间贡献常数
        self.KAPPA = Decimal('2592000')  # 30天的秒数
        
        # 从配置文件加载
        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)
    
    def _load_from_file(self, config_path: str):
        """从配置文件加载参数
        
        Args:
            config_path: 配置文件路径
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # 更新参数
            for key, value in config.items():
                key_upper = key.upper()
                if hasattr(self, key_upper):
                    setattr(self, key_upper, Decimal(str(value)))
            
            logger.info(f"从{config_path}加载发行参数")
        except Exception as e:
            logger.error(f"加载发行参数失败: {e}")
    
    def to_dict(self) -> Dict:
        """将参数转换为字典
        
        Returns:
            参数字典
        """
        return {
            "block_time": str(self.BLOCK_TIME),
            "max_supply": str(self.MAX_SUPPLY),
            "initial_supply": str(self.INITIAL_SUPPLY),
            "halving_period": str(self.HALVING_PERIOD),
            "inflation_rate": str(self.INFLATION_RATE),
            "alpha": str(self.ALPHA),
            "beta": str(self.BETA),
            "gamma": str(self.GAMMA),
            "k": str(self.K),
            "lambda": str(self.LAMBDA),
            "kappa": str(self.KAPPA)
        }


class SomCoinEmission:
    """松麦币发行系统"""
    
    def __init__(self, config_path: str = None, economy_chain = None):
        """初始化松麦币发行系统
        
        Args:
            config_path: 配置文件路径
            economy_chain: 经济链接口
        """
        self.params = EmissionParameters(config_path)
        self.economy_chain = economy_chain
        
        # 系统状态
        self.start_time = datetime.datetime.now()
        self.total_supply = self.params.INITIAL_SUPPLY
        self.current_block_height = 0
        
        # 贡献记录
        self.contribution_metrics = {
            "time": [],
            "technical": [],
            "social": []
        }
        
        # 人口统计
        self.demographics = {
            "active_users": 0,
            "contributors": 0,
            "technical_contributors": 0,
            "social_contributors": 0
        }
        
        logger.info(f"松麦币发行系统初始化完成，初始供应量: {self.total_supply}")
    
    def max_allowed_supply(self, timestamp: datetime.datetime = None) -> Decimal:
        """计算当前时间点的最大允许供应量
        
        基于通胀控制公式: S_total ≤ K·e^(λt)
        
        Args:
            timestamp: 时间点，默认为当前时间
            
        Returns:
            最大允许供应量
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()
        
        # 计算经过的年数
        years = (timestamp - self.start_time).total_seconds() / (365 * 24 * 3600)
        years_decimal = Decimal(str(years))
        
        # 计算通胀上限
        inflation_cap = self.params.INITIAL_SUPPLY * self.params.K * (
            Decimal(str(math.exp(1))) ** (self.params.LAMBDA * years_decimal)
        )
        
        # 确保不超过最大供应量
        return min(inflation_cap, self.params.MAX_SUPPLY)
    
    def mint_coins(self, block_height: int, contributions: Dict[str, Dict]) -> Dict:
        """铸造新松麦币
        
        基于区块高度和贡献记录铸造新的松麦币
        
        Args:
            block_height: 区块高度
            contributions: 用户贡献记录，格式为 {user_id: {贡献数据}}
            
        Returns:
            铸造结果
        """
        # 计算当前允许的最大供应量
        max_allowed = self.max_allowed_supply()
        
        # 检查是否已达到最大供应量
        if self.total_supply >= self.params.MAX_SUPPLY:
            logger.info("已达到最大供应量上限，停止铸造")
            return {
                "success": False,
                "reason": "max_supply_reached",
                "minted": "0",
                "total_supply": str(self.total_supply)
            }
        
        # 检查通胀控制
        if self.total_supply >= max_allowed:
            logger.info(f"当前供应量{self.total_supply}已达到通胀控制上限{max_allowed}，停止铸造")
            return {
                "success": False,
                "reason": "inflation_cap_reached",
                "minted": "0",
                "total_supply": str(self.total_supply),
                "max_allowed": str(max_allowed)
            }
        
        # 计算本区块基础奖励
        base_reward = self._calculate_block_reward(block_height)
        
        # 计算可铸造上限
        mint_cap = min(
            base_reward,
            self.params.MAX_SUPPLY - self.total_supply,
            max_allowed - self.total_supply
        )
        
        # 如果没有足够空间铸造
        if mint_cap <= Decimal('0'):
            return {
                "success": False,
                "reason": "no_room_for_minting",
                "minted": "0",
                "total_supply": str(self.total_supply),
                "max_allowed": str(max_allowed)
            }
        
        # 分析用户贡献
        users_contributions = {}
        total_contribution = Decimal('0')
        
        for user_id, contrib_data in contributions.items():
            # 计算三维贡献
            time_contrib = self._calculate_time_contribution(
                contrib_data.get("participation_time", 0)
            )
            
            technical_contrib = self._calculate_technical_contribution(
                contrib_data.get("technical_metrics", {})
            )
            
            social_contrib = self._calculate_social_contribution(
                contrib_data.get("social_metrics", {})
            )
            
            # 计算加权总贡献
            weighted_contrib = (
                self.params.ALPHA * time_contrib +
                self.params.BETA * technical_contrib +
                self.params.GAMMA * social_contrib
            )
            
            # 记录用户贡献
            users_contributions[user_id] = {
                "time": str(time_contrib),
                "technical": str(technical_contrib),
                "social": str(social_contrib),
                "weighted": str(weighted_contrib)
            }
            
            # 累加总贡献
            total_contribution += weighted_contrib
            
            # 记录贡献指标
            self._record_contribution_metrics(user_id, time_contrib, technical_contrib, social_contrib)
        
        # 防止除以零
        if total_contribution <= Decimal('0'):
            total_contribution = Decimal('1')
        
        # 根据贡献分配币
        rewards = {}
        total_minted = Decimal('0')
        
        for user_id, contrib in users_contributions.items():
            weighted_contrib = Decimal(contrib["weighted"])
            user_reward = (weighted_contrib / total_contribution) * mint_cap
            
            # 四舍五入到8位小数
            user_reward = user_reward.quantize(Decimal('0.00000001'))
            
            if user_reward > Decimal('0'):
                rewards[user_id] = str(user_reward)
                total_minted += user_reward
        
        # 更新总供应量
        self.total_supply += total_minted
        self.current_block_height = block_height
        
        # 处理区块链交易
        if self.economy_chain:
            for user_id, reward in rewards.items():
                try:
                    self.economy_chain.mint_to_address(
                        user_id, 
                        float(reward), 
                        {
                            "block_height": block_height,
                            "contribution": users_contributions[user_id]
                        }
                    )
                except Exception as e:
                    logger.error(f"铸币交易失败: {e}")
        
        return {
            "success": True,
            "block_height": block_height,
            "base_reward": str(base_reward),
            "minted": str(total_minted),
            "total_supply": str(self.total_supply),
            "max_allowed": str(max_allowed),
            "rewards": rewards,
            "contributions": users_contributions
        }
    
    def _calculate_block_reward(self, block_height: int) -> Decimal:
        """计算区块基础奖励
        
        使用奖励曲线：cos(x) + log(1+x)
        
        Args:
            block_height: 区块高度
            
        Returns:
            区块基础奖励
        """
        # 计算当前所处减半周期
        halvings = block_height // int(self.params.HALVING_PERIOD)
        
        # 归一化区块高度到[0, 1]区间
        normalized_height = (block_height % int(self.params.HALVING_PERIOD)) / int(self.params.HALVING_PERIOD)
        
        # 映射到[0, 2π]区间用于余弦函数
        x = normalized_height * 2 * math.pi
        
        # 计算奖励：cos(x) + log(1+x)
        reward = math.cos(x) + math.log(1 + x)
        
        # 确保奖励为正数
        reward = max(0.1, reward)
        
        # 应用减半
        if halvings > 0:
            reward = reward / (2 ** halvings)
        
        # 转换为Decimal并返回
        return Decimal(str(reward))
    
    def _calculate_time_contribution(self, participation_time: Union[int, float]) -> Decimal:
        """计算时间维度贡献
        
        使用公式：τ = 1 - e^(-t/κ)
        
        Args:
            participation_time: 参与时间(秒)
            
        Returns:
            时间维度贡献
        """
        # 转换为Decimal
        t = Decimal(str(participation_time))
        
        # 计算贡献: τ = 1 - e^(-t/κ)
        tau = Decimal('1') - Decimal(str(math.exp(-float(t / self.params.KAPPA))))
        
        # 确保贡献度在[0, 1]范围内
        tau = max(Decimal('0'), min(Decimal('1'), tau))
        
        return tau
    
    def _calculate_technical_contribution(self, metrics: Dict) -> Decimal:
        """计算技术维度贡献
        
        使用公式：Γ = Σ(w_i·impact_i)，并归一化
        
        Args:
            metrics: 技术贡献指标
            
        Returns:
            技术维度贡献
        """
        if not metrics:
            return Decimal('0')
        
        # 贡献类型权重
        weights = {
            "code": Decimal('1.0'),  # 代码贡献
            "review": Decimal('0.5'),  # 代码审查
            "document": Decimal('0.5'),  # 文档
            "test": Decimal('0.7'),  # 测试
            "issue": Decimal('0.3'),  # 问题报告
            "other": Decimal('0.1')  # 其他
        }
        
        # 计算加权贡献总和
        weighted_sum = Decimal('0')
        
        for contrib_type, impact in metrics.items():
            weight = weights.get(contrib_type, weights["other"])
            weighted_sum += weight * Decimal(str(impact))
        
        # 使用Sigmoid函数归一化到[0, 1]范围
        # Sigmoid: 1 / (1 + e^(-(x-threshold)/scale))
        threshold = Decimal('100')  # 贡献阈值
        scale = Decimal('50')  # 缩放因子
        
        normalized = Decimal('1') / (Decimal('1') + Decimal(
            str(math.exp(-float((weighted_sum - threshold) / scale)))
        ))
        
        return normalized
    
    def _calculate_social_contribution(self, metrics: Dict) -> Decimal:
        """计算社会维度贡献
        
        使用简化的加权平均代替MLP
        
        Args:
            metrics: 社会贡献指标
            
        Returns:
            社会维度贡献
        """
        if not metrics:
            return Decimal('0')
        
        # 社会贡献维度权重
        weights = {
            "community_help": Decimal('0.3'),  # 社区互助
            "knowledge_share": Decimal('0.3'),  # 知识分享
            "event_organization": Decimal('0.2'),  # 活动组织
            "emergency_response": Decimal('0.2')  # 紧急响应
        }
        
        # 归一化各指标到[0, 1]
        normalized_metrics = {}
        
        for metric, value in metrics.items():
            if metric == "community_help":
                normalized_metrics[metric] = min(Decimal('1'), Decimal(str(value)) / Decimal('100'))
            elif metric == "knowledge_share":
                normalized_metrics[metric] = min(Decimal('1'), Decimal(str(value)) / Decimal('100'))
            elif metric == "event_organization":
                normalized_metrics[metric] = min(Decimal('1'), Decimal(str(value)) / Decimal('50'))
            elif metric == "emergency_response":
                normalized_metrics[metric] = min(Decimal('1'), Decimal(str(value)) * Decimal('2'))
            else:
                normalized_metrics[metric] = min(Decimal('1'), Decimal(str(value)) / Decimal('100'))
        
        # 计算加权平均
        weighted_sum = Decimal('0')
        total_weight = Decimal('0')
        
        for metric, weight in weights.items():
            if metric in normalized_metrics:
                weighted_sum += weight * normalized_metrics[metric]
                total_weight += weight
        
        # 防止除以零
        if total_weight <= Decimal('0'):
            return Decimal('0')
        
        # 计算贡献度
        contribution = weighted_sum / total_weight
        
        # 确保贡献度在[0, 1]范围内
        contribution = max(Decimal('0'), min(Decimal('1'), contribution))
        
        return contribution
    
    def _record_contribution_metrics(self, 
                                    user_id: str, 
                                    time_contrib: Decimal, 
                                    technical_contrib: Decimal, 
                                    social_contrib: Decimal):
        """记录用户贡献指标
        
        Args:
            user_id: 用户ID
            time_contrib: 时间贡献
            technical_contrib: 技术贡献
            social_contrib: 社会贡献
        """
        timestamp = datetime.datetime.now().isoformat()
        
        self.contribution_metrics["time"].append({
            "user_id": user_id,
            "value": str(time_contrib),
            "timestamp": timestamp
        })
        
        self.contribution_metrics["technical"].append({
            "user_id": user_id,
            "value": str(technical_contrib),
            "timestamp": timestamp
        })
        
        self.contribution_metrics["social"].append({
            "user_id": user_id,
            "value": str(social_contrib),
            "timestamp": timestamp
        })
        
        # 限制记录数量
        for dim in self.contribution_metrics:
            if len(self.contribution_metrics[dim]) > 1000:
                self.contribution_metrics[dim] = self.contribution_metrics[dim][-1000:]
    
    def get_supply_stats(self) -> Dict:
        """获取供应统计信息
        
        Returns:
            供应统计信息
        """
        current_max_allowed = self.max_allowed_supply()
        
        return {
            "total_supply": str(self.total_supply),
            "max_supply": str(self.params.MAX_SUPPLY),
            "initial_supply": str(self.params.INITIAL_SUPPLY),
            "current_inflation_cap": str(current_max_allowed),
            "percent_issued": str((self.total_supply / self.params.MAX_SUPPLY) * 100) + "%",
            "current_block_height": self.current_block_height,
            "start_time": self.start_time.isoformat(),
            "running_days": (datetime.datetime.now() - self.start_time).days
        }
    
    def reset_system(self):
        """重置发行系统（仅用于测试）"""
        logger.warning("重置松麦币发行系统")
        
        self.start_time = datetime.datetime.now()
        self.total_supply = self.params.INITIAL_SUPPLY
        self.current_block_height = 0
        
        for dim in self.contribution_metrics:
            self.contribution_metrics[dim] = []
        
        for key in self.demographics:
            self.demographics[key] = 0


class SomCoinRewardDistributor:
    """松麦币奖励分配器"""
    
    def __init__(self, emission_system: SomCoinEmission):
        """初始化奖励分配器
        
        Args:
            emission_system: 松麦币发行系统
        """
        self.emission = emission_system
        self.reward_pools = {
            "development": Decimal('0'),  # 开发奖励池
            "community": Decimal('0'),    # 社区奖励池
            "ecosystem": Decimal('0')     # 生态建设奖励池
        }
        
        # 分配历史
        self.distribution_history = []
        
        logger.info("松麦币奖励分配器初始化完成")
    
    def fund_pool(self, pool_name: str, amount: Union[Decimal, float, str]) -> Dict:
        """向奖励池注资
        
        Args:
            pool_name: 奖励池名称
            amount: 注资金额
            
        Returns:
            注资结果
        """
        if pool_name not in self.reward_pools:
            return {
                "success": False,
                "reason": "pool_not_found",
                "message": f"奖励池{pool_name}不存在"
            }
        
        # 转换为Decimal
        amount_decimal = Decimal(str(amount))
        
        if amount_decimal <= Decimal('0'):
            return {
                "success": False,
                "reason": "invalid_amount",
                "message": "注资金额必须大于0"
            }
        
        # 检查总供应量
        if self.emission.total_supply + amount_decimal > self.emission.params.MAX_SUPPLY:
            max_possible = self.emission.params.MAX_SUPPLY - self.emission.total_supply
            return {
                "success": False,
                "reason": "exceeds_max_supply",
                "message": f"注资金额超过最大供应量，最多可注资{max_possible}"
            }
        
        # 注资
        self.reward_pools[pool_name] += amount_decimal
        
        # 更新总供应量
        self.emission.total_supply += amount_decimal
        
        # 记录历史
        self.distribution_history.append({
            "type": "fund",
            "pool": pool_name,
            "amount": str(amount_decimal),
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        logger.info(f"向{pool_name}奖励池注资{amount_decimal}松麦币")
        
        return {
            "success": True,
            "pool": pool_name,
            "amount": str(amount_decimal),
            "new_balance": str(self.reward_pools[pool_name]),
            "total_supply": str(self.emission.total_supply)
        }
    
    def distribute_rewards(self, pool_name: str, distribution: Dict[str, Union[float, str]]) -> Dict:
        """从奖励池分配奖励
        
        Args:
            pool_name: 奖励池名称
            distribution: 分配方案，格式为 {recipient_id: amount}
            
        Returns:
            分配结果
        """
        if pool_name not in self.reward_pools:
            return {
                "success": False,
                "reason": "pool_not_found",
                "message": f"奖励池{pool_name}不存在"
            }
        
        # 计算总分配量
        total_distribution = Decimal('0')
        for recipient, amount in distribution.items():
            total_distribution += Decimal(str(amount))
        
        # 检查奖励池余额
        if total_distribution > self.reward_pools[pool_name]:
            return {
                "success": False,
                "reason": "insufficient_pool_balance",
                "message": f"奖励池余额不足，当前余额{self.reward_pools[pool_name]}，需要{total_distribution}"
            }
        
        # 执行分配
        distribution_results = {}
        
        for recipient, amount in distribution.items():
            amount_decimal = Decimal(str(amount))
            
            # 跳过零值
            if amount_decimal <= Decimal('0'):
                continue
            
            # 处理区块链交易
            if self.emission.economy_chain:
                try:
                    tx_result = self.emission.economy_chain.transfer(
                        f"pool:{pool_name}",
                        recipient,
                        float(amount_decimal),
                        {
                            "type": "reward",
                            "pool": pool_name,
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                    )
                    distribution_results[recipient] = {
                        "amount": str(amount_decimal),
                        "tx_id": tx_result.get("tx_id", "unknown")
                    }
                except Exception as e:
                    logger.error(f"奖励分配交易失败: {e}")
                    distribution_results[recipient] = {
                        "amount": str(amount_decimal),
                        "error": str(e)
                    }
            else:
                # 开发环境，记录分配结果
                distribution_results[recipient] = {
                    "amount": str(amount_decimal),
                    "simulated": True
                }
            
            # 更新奖励池余额
            self.reward_pools[pool_name] -= amount_decimal
        
        # 记录历史
        self.distribution_history.append({
            "type": "distribute",
            "pool": pool_name,
            "total_amount": str(total_distribution),
            "recipients_count": len(distribution),
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        logger.info(f"从{pool_name}奖励池分配{total_distribution}松麦币给{len(distribution)}个接收者")
        
        return {
            "success": True,
            "pool": pool_name,
            "total_distributed": str(total_distribution),
            "remaining_balance": str(self.reward_pools[pool_name]),
            "distribution_results": distribution_results
        }
    
    def get_pool_status(self) -> Dict:
        """获取奖励池状态
        
        Returns:
            奖励池状态
        """
        pools_status = {}
        total_in_pools = Decimal('0')
        
        for pool_name, balance in self.reward_pools.items():
            pools_status[pool_name] = str(balance)
            total_in_pools += balance
        
        return {
            "pools": pools_status,
            "total_in_pools": str(total_in_pools),
            "percent_of_supply": str((total_in_pools / self.emission.total_supply) * 100) + "%",
            "last_distribution": self.distribution_history[-1] if self.distribution_history else None,
            "distribution_count": len(self.distribution_history)
        }


# 测试代码
if __name__ == "__main__":
    # 创建松麦币发行系统
    emission = SomCoinEmission()
    
    # 创建奖励分配器
    distributor = SomCoinRewardDistributor(emission)
    
    # 打印初始状态
    print("初始供应状态:", emission.get_supply_stats())
    
    # 模拟用户贡献
    mock_contributions = {
        "user1": {
            "participation_time": 60 * 60 * 24 * 30,  # 30天
            "technical_metrics": {
                "code": 150,
                "review": 50,
                "document": 30
            },
            "social_metrics": {
                "community_help": 80,
                "knowledge_share": 60,
                "event_organization": 20
            }
        },
        "user2": {
            "participation_time": 60 * 60 * 24 * 10,  # 10天
            "technical_metrics": {
                "code": 50,
                "test": 40
            },
            "social_metrics": {
                "community_help": 30,
                "emergency_response": 0.5
            }
        }
    }
    
    # 模拟铸币
    mint_result = emission.mint_coins(1, mock_contributions)
    print("\n铸币结果:", json.dumps(mint_result, indent=2))
    
    # 向奖励池注资
    fund_result = distributor.fund_pool("community", 1000)
    print("\n注资结果:", json.dumps(fund_result, indent=2))
    
    # 从奖励池分配奖励
    distribution = {
        "user3": 300,
        "user4": 200,
        "user5": 100
    }
    distribute_result = distributor.distribute_rewards("community", distribution)
    print("\n分配结果:", json.dumps(distribute_result, indent=2))
    
    # 打印奖励池状态
    print("\n奖励池状态:", json.dumps(distributor.get_pool_status(), indent=2))
    
    # 打印最终供应状态
    print("\n最终供应状态:", json.dumps(emission.get_supply_stats(), indent=2)) 

"""
"""
量子基因编码: QE-SOM-31A6F704E209
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
