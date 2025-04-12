"""
SOM Coin System
松麦币系统 - 实现量子纠缠网络中的价值交换和激励机制
"""

import numpy as np
import time
import uuid
import hashlib
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入量子区块链相关模块
from quantum_core.quantum_blockchain.quantum_blockchain_core import MainQuantumBlockchain

# 尝试导入SOM量子区块链
try:
    from SOM.quantum_blockchain.som_blockchain import SomQuantumChain, get_som_chain
    _som_blockchain_available = True
    logging.info("使用SOM量子区块链")
except ImportError:
    _som_blockchain_available = False
    logging.warning("无法导入SOM量子区块链，将尝试使用其他实现")

# 尝试导入现有的松麦币和钱包系统
try:
<<<<<<< HEAD
    from quantum_economy.SOM.blockchain.SOM_chain import SomEconomyChain
    from quantum_economy.SOM.wallet.wallet_core import SomWallet
=======
    from quantum_economy.som.blockchain.som_chain import SomEconomyChain
    from quantum_economy.som.wallet.wallet_core import SomWallet
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
    _existing_implementation = True
    
    logging.info("使用现有松麦币和钱包系统")
except ImportError:
    _existing_implementation = False
    logging.info("使用新松麦币和钱包系统")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='som_coin.log'
)
logger = logging.getLogger(__name__)

@dataclass
class SomCoinTransaction:
    """松麦币交易记录"""
    transaction_id: str
    from_wallet: str
    to_wallet: str
    amount: float
    timestamp: float
    transaction_type: str
    data: Dict
    signature: str = ""
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "transaction_id": self.transaction_id,
            "from_wallet": self.from_wallet,
            "to_wallet": self.to_wallet,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "transaction_type": self.transaction_type,
            "data": self.data,
            "signature": self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SomCoinTransaction':
        """从字典创建交易记录"""
        return cls(
            transaction_id=data["transaction_id"],
            from_wallet=data["from_wallet"],
            to_wallet=data["to_wallet"],
            amount=data["amount"],
            timestamp=data["timestamp"],
            transaction_type=data["transaction_type"],
            data=data["data"],
            signature=data["signature"]
        )

@dataclass
class SomWalletInfo:
    """松麦钱包信息"""
    wallet_id: str
    node_id: str
    creation_time: float
    balance: float
    last_active: float
    reputation_score: float
    transaction_count: int
    wallet_type: str
    features: List[str]
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "wallet_id": self.wallet_id,
            "node_id": self.node_id,
            "creation_time": self.creation_time,
            "balance": self.balance,
            "last_active": self.last_active,
            "reputation_score": self.reputation_score,
            "transaction_count": self.transaction_count,
            "wallet_type": self.wallet_type,
            "features": self.features
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SomWalletInfo':
        """从字典创建钱包信息"""
        return cls(
            wallet_id=data["wallet_id"],
            node_id=data["node_id"],
            creation_time=data["creation_time"],
            balance=data["balance"],
            last_active=data["last_active"],
            reputation_score=data["reputation_score"],
            transaction_count=data["transaction_count"],
            wallet_type=data["wallet_type"],
            features=data["features"]
        )

# 如果SOM量子区块链可用，则优先使用它
if _som_blockchain_available:
    class SomCoinEconomy:
        """松麦币经济系统 - 使用SOM量子区块链"""
        
        def __init__(self):
            # 获取SOM量子区块链实例
            self.som_chain = get_som_chain()
            self.wallets = {}  # 本地钱包缓存
            self.reward_rates = {
                "SOFTWARE_NODE": 1.0,     # 软件安装节点奖励率
                "BROWSER_PERSISTENT": 0.5,  # 浏览器持久节点奖励率
                "BROWSER_TEMPORARY": 0.2,   # 浏览器临时节点奖励率
                "PHYSICAL_MEDIA": 0.3     # 物理介质节点奖励率
            }
            self.system_wallet = self.som_chain.system_wallet_id
            
            logger.info("松麦币经济系统初始化完成 (使用SOM量子区块链)")
        
        def create_wallet(self, node_id: str, wallet_type: str = "STANDARD") -> str:
            """创建新钱包"""
            wallet_id = self.som_chain.create_wallet(node_id, wallet_type)
            logger.info(f"创建新钱包: {wallet_id} 节点类型: {wallet_type} (使用SOM量子区块链)")
            return wallet_id
        
        def reward_node(self, wallet_id: str, contribution_type: str, 
                       contribution_amount: float, 
                       data: Dict = None) -> Optional[SomCoinTransaction]:
            """奖励节点贡献"""
            # 计算奖励金额
            reward_amount = self._calculate_reward(
                contribution_type, 
                contribution_amount, 
                "STANDARD",  # 默认钱包类型
                0.5  # 默认声誉分数
            )
            
            # 使用SOM量子区块链奖励钱包
            tx_id = self.som_chain.reward_wallet(wallet_id, contribution_type, reward_amount)
            
            # 创建交易记录
            transaction = SomCoinTransaction(
                transaction_id=tx_id or str(uuid.uuid4()),
                from_wallet=self.system_wallet,
                to_wallet=wallet_id,
                amount=reward_amount,
                timestamp=time.time(),
                transaction_type="REWARD",
                data=data or {
                    "contribution_type": contribution_type,
                    "contribution_amount": contribution_amount
                },
                signature=""
            )
            
            logger.info(f"奖励节点 {wallet_id}: {reward_amount} SOM币 类型: {contribution_type} (使用SOM量子区块链)")
            return transaction
        
        def _calculate_reward(self, contribution_type: str, contribution_amount: float, 
                             wallet_type: str, reputation_score: float) -> float:
            """计算奖励金额"""
            # 使用与新实现相同的奖励计算逻辑
            base_rate = 0.0
            
            # 根据贡献类型确定基础奖励率
            if contribution_type == "COMPUTE":
                base_rate = 0.01  # 每单位计算贡献的基础奖励
            elif contribution_type == "STORAGE":
                base_rate = 0.05  # 每单位存储贡献的基础奖励
            elif contribution_type == "BANDWIDTH":
                base_rate = 0.02  # 每单位带宽贡献的基础奖励
            elif contribution_type == "CONTENT_CREATION":
                base_rate = 0.1   # 每单位内容创作贡献的基础奖励
            elif contribution_type == "WALLET_CREATION":
                return 10.0       # 钱包创建固定奖励
            elif contribution_type == "PLATFORM_SUPPORT":
                base_rate = 0.5   # 平台支持奖励
            else:
                base_rate = 0.01  # 默认奖励率
            
            # 应用钱包类型乘数
            wallet_type_multiplier = self.reward_rates.get(wallet_type, 0.2)
            
            # 应用声誉分数乘数 (0.5 到 1.5 之间)
            reputation_multiplier = 0.5 + reputation_score
            
            # 最终奖励计算
            reward = contribution_amount * base_rate * wallet_type_multiplier * reputation_multiplier
            
            # 确保最低奖励
            return max(reward, 0.1)
        
        def get_wallet_info(self, wallet_id: str) -> Optional[SomWalletInfo]:
            """获取钱包信息"""
            # 这里可以添加从SOM量子区块链获取钱包信息的逻辑
            balance = self.som_chain.get_wallet_balance(wallet_id)
            
            wallet_info = SomWalletInfo(
                wallet_id=wallet_id,
                node_id="unknown",  # 目前SOM区块链API不返回node_id
                creation_time=time.time(),  # 默认为当前时间
                balance=balance,
                last_active=time.time(),
                reputation_score=0.5,  # 默认声誉分数
                transaction_count=0,   # 默认交易数
                wallet_type="STANDARD",  # 默认钱包类型
                features=[]  # 默认特性
            )
            
            return wallet_info
        
        def get_wallet_balance(self, wallet_id: str) -> float:
            """获取钱包余额"""
            return self.som_chain.get_wallet_balance(wallet_id)
        
        def transfer(self, from_wallet: str, to_wallet: str, amount: float, 
                    data: Dict = None) -> Optional[SomCoinTransaction]:
            """转账"""
            tx_id = self.som_chain.transfer(from_wallet, to_wallet, amount, data.get("memo", "") if data else "")
            
            if not tx_id:
                logger.error(f"转账失败: {from_wallet} -> {to_wallet}, 金额: {amount}")
                return None
            
            # 创建交易记录
            transaction = SomCoinTransaction(
                transaction_id=tx_id,
                from_wallet=from_wallet,
                to_wallet=to_wallet,
                amount=amount,
                timestamp=time.time(),
                transaction_type="TRANSFER",
                data=data or {},
                signature=""
            )
            
            logger.info(f"转账成功: {from_wallet} -> {to_wallet}, 金额: {amount}, 交易ID: {tx_id}")
            return transaction

    class SomWalletAPI:
        """松麦钱包API - 使用SOM量子区块链"""
        
        def __init__(self, economy: SomCoinEconomy):
            self.economy = economy
            self.som_chain = get_som_chain()
            
            logger.info("松麦钱包API初始化完成 (使用SOM量子区块链)")
        
        def create_wallet(self, node_id: str, wallet_type: str = "STANDARD") -> str:
            """创建新钱包"""
            return self.economy.create_wallet(node_id, wallet_type)
        
        def get_balance(self, wallet_id: str) -> float:
            """获取钱包余额"""
            return self.economy.get_wallet_balance(wallet_id)
        
        def transfer(self, from_wallet: str, to_wallet: str, amount: float, 
                    memo: str = "") -> Optional[str]:
            """转账"""
            tx = self.economy.transfer(from_wallet, to_wallet, amount, {"memo": memo})
            return tx.transaction_id if tx else None
        
        def get_economic_status(self) -> Dict:
            """获取经济状态"""
            return self.som_chain.get_economic_status()
            
elif _existing_implementation:
    class SomCoinEconomy:
        """松麦币经济系统 - 封装现有实现"""
        
        def __init__(self):
            # 初始化现有的松麦币子链实现
            self.economy_chain = SomEconomyChain()
            self.wallets = {}  # 本地钱包缓存
            self.reward_rates = {
                "SOFTWARE_NODE": 1.0,     # 软件安装节点奖励率
                "BROWSER_PERSISTENT": 0.5,  # 浏览器持久节点奖励率
                "BROWSER_TEMPORARY": 0.2,   # 浏览器临时节点奖励率
                "PHYSICAL_MEDIA": 0.3     # 物理介质节点奖励率
            }
            self.system_wallet = self._create_system_wallet()
            self.blockchain = MainQuantumBlockchain(difficulty=4)
            
            logger.info("松麦币经济系统初始化完成 (封装现有实现)")
        
        def _create_system_wallet(self) -> str:
            """创建系统钱包"""
            system_wallet_id = "SOM_SYSTEM_WALLET"
            # 使用现有钱包系统创建钱包
            wallet = SomWallet(user_id="SYSTEM")
            self.wallets[system_wallet_id] = SomWalletInfo(
                wallet_id=system_wallet_id,
                node_id="SYSTEM",
                creation_time=time.time(),
                balance=1000000000.0,  # 系统初始供应量
                last_active=time.time(),
                reputation_score=1.0,
                transaction_count=0,
                wallet_type="SYSTEM",
                features=["UNLIMITED_TRANSACTIONS", "SYSTEM_OPERATIONS"]
            )
            
            # 在现有子链中创建初始货币
            self.economy_chain.create_som_coin(1000000000.0, "SYSTEM")
            
            return system_wallet_id
        
        def create_wallet(self, node_id: str, wallet_type: str = "STANDARD") -> str:
            """创建新钱包"""
            # 使用现有钱包系统创建钱包
            wallet = SomWallet(user_id=node_id)
            wallet_id = wallet.wallet_address
            
            # 存储到本地缓存
            self.wallets[wallet_id] = SomWalletInfo(
                wallet_id=wallet_id,
                node_id=node_id,
                creation_time=time.time(),
                balance=0.0,
                last_active=time.time(),
                reputation_score=0.5,  # 初始声誉分数
                transaction_count=0,
                wallet_type=wallet_type,
                features=self._get_wallet_features(wallet_type)
            )
            
            # 发放初始奖励
            self.reward_node(wallet_id, "WALLET_CREATION", 1.0)
            
            logger.info(f"创建新钱包: {wallet_id} 节点类型: {wallet_type} (封装现有实现)")
            return wallet_id
        
        def _get_wallet_features(self, wallet_type: str) -> List[str]:
            """获取钱包特性"""
            features = ["STANDARD_TRANSACTIONS"]
            if wallet_type == "SOFTWARE_NODE":
                features.extend(["HIGH_PRIORITY", "UNLIMITED_STORAGE"])
            elif wallet_type == "BROWSER_PERSISTENT":
                features.extend(["MEDIUM_PRIORITY", "EXTENDED_STORAGE"])
            return features
        
        def reward_node(self, wallet_id: str, contribution_type: str, 
                       contribution_amount: float, 
                       data: Dict = None) -> Optional[SomCoinTransaction]:
            """奖励节点贡献"""
            wallet = self.get_wallet_info(wallet_id)
            if not wallet:
                logger.error(f"钱包不存在: {wallet_id}")
                return None
            
            # 计算奖励金额
            reward_amount = self._calculate_reward(
                contribution_type, 
                contribution_amount, 
                wallet.wallet_type, 
                wallet.reputation_score
            )
            
            # 通过现有系统创建松麦币
            tx_id = self.economy_chain.create_som_coin(reward_amount, wallet.node_id)
            
            # 创建交易记录
            transaction = SomCoinTransaction(
                transaction_id=tx_id or str(uuid.uuid4()),
                from_wallet=self.system_wallet,
                to_wallet=wallet_id,
                amount=reward_amount,
                timestamp=time.time(),
                transaction_type="REWARD",
                data=data or {
                    "contribution_type": contribution_type,
                    "contribution_amount": contribution_amount
                },
                signature=""
            )
            
            # 更新本地钱包缓存
            self._update_wallet(wallet_id, reward_amount, "REWARD")
            
            logger.info(f"奖励节点 {wallet_id}: {reward_amount} SOM币 类型: {contribution_type} (封装现有实现)")
            return transaction
        
        def _calculate_reward(self, contribution_type: str, contribution_amount: float, 
                             wallet_type: str, reputation_score: float) -> float:
            """计算奖励金额"""
            # 使用与新实现相同的奖励计算逻辑
            base_rate = 0.0
            
            # 根据贡献类型确定基础奖励率
            if contribution_type == "COMPUTE":
                base_rate = 0.01  # 每单位计算贡献的基础奖励
            elif contribution_type == "STORAGE":
                base_rate = 0.005  # 每单位存储贡献的基础奖励
            elif contribution_type == "KNOWLEDGE":
                base_rate = 0.1  # 每单位知识贡献的基础奖励
            elif contribution_type == "PHYSICAL_MEDIA":
                base_rate = 0.02  # 每单位物理媒介贡献的基础奖励
            elif contribution_type == "ENTANGLEMENT_EXPANSION":
                base_rate = 0.5  # 每次纠缠扩展的基础奖励
            elif contribution_type == "WALLET_CREATION":
                base_rate = 10.0  # 钱包创建奖励
            
            # 应用节点类型系数
            type_multiplier = self.reward_rates.get(wallet_type, 0.1)
            
            # 应用声誉分数调整
            reputation_multiplier = 0.5 + (reputation_score * 0.5)  # 0.5 到 1.0 之间
            
            # 计算最终奖励
            reward = base_rate * contribution_amount * type_multiplier * reputation_multiplier
            
            # 应用系统奖励衰减
            current_supply = self.economy_chain.get_som_coin_info()["circulating_supply"]
            if current_supply > 0:
                decay_factor = np.exp(-current_supply / 1000000000.0)  # 供应量增加时奖励减少
                reward *= decay_factor
            
            return max(0.001, reward)  # 最小奖励0.001
        
        def _update_wallet(self, wallet_id: str, amount_change: float, update_type: str) -> None:
            """更新钱包信息（本地缓存）"""
            if wallet_id not in self.wallets:
                return
                
            wallet = self.wallets[wallet_id]
            
            # 更新余额
            wallet.balance += amount_change
            wallet.last_active = time.time()
            wallet.transaction_count += 1
            
            # 更新声誉分数（根据交易类型）
            if update_type == "REWARD":
                # 获得奖励略微提高声誉
                wallet.reputation_score = min(1.0, wallet.reputation_score + 0.001)
            elif update_type == "TRANSFER_OUT":
                # 正常转出不影响声誉
                pass
            elif update_type == "TRANSFER_IN":
                # 收到转账略微提高声誉
                wallet.reputation_score = min(1.0, wallet.reputation_score + 0.0005)
        
        def get_wallet_info(self, wallet_id: str) -> Optional[SomWalletInfo]:
            """获取钱包信息"""
            return self.wallets.get(wallet_id)
        
        def get_wallet_balance(self, wallet_id: str) -> float:
            """获取钱包余额"""
            wallet = self.get_wallet_info(wallet_id)
            if wallet:
                return wallet.balance
            return 0.0
        
        def transfer(self, from_wallet: str, to_wallet: str, amount: float, 
                    data: Dict = None) -> Optional[SomCoinTransaction]:
            """转账"""
            # 使用现有系统进行转账
            # 在实际实现中，应找到现有系统中对应的钱包ID
            from_node_id = self.wallets.get(from_wallet, SomWalletInfo("", "unknown", 0, 0, 0, 0, 0, "", [])).node_id
            to_node_id = self.wallets.get(to_wallet, SomWalletInfo("", "unknown", 0, 0, 0, 0, 0, "", [])).node_id
            
            tx_id = self.economy_chain.transfer_som_coin(from_node_id, to_node_id, amount, memo=data.get("memo", "") if data else "")
            
            if not tx_id:
                logger.error(f"转账失败: {from_wallet} -> {to_wallet}")
                return None
            
            # 创建交易记录
            transaction = SomCoinTransaction(
                transaction_id=tx_id,
                from_wallet=from_wallet,
                to_wallet=to_wallet,
                amount=amount,
                timestamp=time.time(),
                transaction_type="TRANSFER",
                data=data or {"memo": "用户转账"},
                signature=""
            )
            
            # 更新本地钱包缓存
            self._update_wallet(from_wallet, -amount, "TRANSFER_OUT")
            self._update_wallet(to_wallet, amount, "TRANSFER_IN")
            
            logger.info(f"转账完成: {from_wallet} -> {to_wallet} 金额: {amount} SOM币 (封装现有实现)")
            return transaction
        
        # 其他必要方法的封装...
    
    class SomWalletAPI:
        """松麦钱包API - 封装现有实现"""
        
        def __init__(self, economy: SomCoinEconomy):
            self.economy = economy
        
        # 其他API方法的封装...

else:
    class SomCoinEconomy:
        """松麦币经济系统 - 新实现"""
        # 原有的新实现代码...
        
    class SomWalletAPI:
        """松麦钱包API - 新实现"""
        # 原有的新实现代码...

# 全局单例
_economy_instance = None
_wallet_api = None

def get_economy_instance() -> SomCoinEconomy:
    """获取经济系统单例实例"""
    global _economy_instance
    if _economy_instance is None:
        _economy_instance = SomCoinEconomy()
    return _economy_instance

def get_wallet_api() -> SomWalletAPI:
    """获取钱包API单例实例"""
    global _wallet_api, _economy_instance
    if _wallet_api is None:
        _wallet_api = SomWalletAPI(get_economy_instance())
    return _wallet_api 

"""
"""
量子基因编码: QE-SOM-137875E185E1
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
