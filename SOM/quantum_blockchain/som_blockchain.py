"""
SOM Quantum Blockchain
SOM量子区块链 - 实现松麦子模型的子链区块链，专注于经济交易和价值流通
"""

import os
import sys
import json
import logging
import hashlib
import time
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass
import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入量子区块链核心
try:
    from quantum_core.quantum_blockchain.quantum_blockchain_core import (
        SubQuantumBlockchain, 
        QuantumBlock,
        _existing_implementation
    )
<<<<<<< HEAD
    from quantum_core.quantum_blockchain.QSM_main_chain import get_QSM_main_chain
=======
    from quantum_core.quantum_blockchain.qsm_main_chain import get_qsm_main_chain
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
    if _existing_implementation:
        from quantum_economy.blockchain.quantum_chain import (
            QuantumChain,
            QuantumTransaction,
            QuantumState
        )
<<<<<<< HEAD
        from quantum_economy.SOM.blockchain.SOM_chain import SomEconomyChain
=======
        from quantum_economy.som.blockchain.som_chain import SomEconomyChain
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
except ImportError:
    print("无法导入量子区块链核心，请确保已安装相关依赖")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("som_blockchain.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SOM区块链")

class SomTransactionTypes(Enum):
    """松麦交易类型"""
    COIN_CREATION = "coin_creation"            # 松麦币创建
    COIN_TRANSFER = "coin_transfer"            # 松麦币转账
    MERCHANT_REGISTRATION = "merchant_reg"      # 商家注册
    PRODUCT_LISTING = "product_listing"        # 产品上架
    PURCHASE = "purchase"                      # 购买交易
    REWARD = "reward"                          # 奖励
    VALUE_EXCHANGE = "value_exchange"          # 价值交换
    SYSTEM_EVENT = "system_event"              # 系统事件

@dataclass
class SomEconomicData:
    """松麦经济数据"""
    total_supply: float = 0.0
    circulating_supply: float = 0.0
    current_value: float = 1.0
    transaction_count: int = 0
    active_wallets: int = 0
    merchant_count: int = 0
    product_count: int = 0
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "total_supply": self.total_supply,
            "circulating_supply": self.circulating_supply,
            "current_value": self.current_value,
            "transaction_count": self.transaction_count,
            "active_wallets": self.active_wallets,
            "merchant_count": self.merchant_count,
            "product_count": self.product_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SomEconomicData':
        """从字典创建经济数据"""
        return cls(
            total_supply=data.get("total_supply", 0.0),
            circulating_supply=data.get("circulating_supply", 0.0),
            current_value=data.get("current_value", 1.0),
            transaction_count=data.get("transaction_count", 0),
            active_wallets=data.get("active_wallets", 0),
            merchant_count=data.get("merchant_count", 0),
            product_count=data.get("product_count", 0)
        )

class SomQuantumChain:
    """SOM量子链实现"""
    
    def __init__(self, chain_id: str = None):
        """初始化SOM量子链
        
        Args:
            chain_id: 链唯一标识，如不提供则自动生成
        """
        if not chain_id:
            chain_id = "SOM_CHAIN_" + hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        # 根据是否存在现有实现，选择不同的初始化方式
        if '_existing_implementation' in globals() and _existing_implementation:
            # 使用现有松麦经济链实现
            self.som_chain = SomEconomyChain(chain_id=chain_id)
            # 子链适配器
            self.sub_blockchain = SubQuantumBlockchain(
                chain_id=chain_id,
                difficulty=4
            )
            logger.info(f"初始化SOM量子链: {chain_id} (封装现有实现)")
        else:
            # 使用新实现创建子链
            self.sub_blockchain = SubQuantumBlockchain(
                chain_id=chain_id,
                difficulty=4
            )
            logger.info(f"初始化SOM量子链: {chain_id} (新实现)")
        
        # 尝试获取主链
        try:
            self.main_chain = get_qsm_main_chain()
            # 向主链注册
            self.main_chain.register_subchain(
                chain_id=chain_id,
                model_type="SOM",
                features=["economic_transactions", "value_exchange", "merchant_services"]
            )
            logger.info(f"向主链注册SOM量子链: {chain_id}")
        except Exception as e:
            logger.warning(f"无法获取主链或注册子链: {str(e)}")
            self.main_chain = None
        
        # 经济数据
        self.economic_data = SomEconomicData()
        
        # 交易记录
        self.transactions = {}
        
        # 钱包列表
        self.wallets = {}
        
        # 系统钱包
        self.system_wallet_id = self._create_system_wallet()
        
        logger.info(f"SOM量子链初始化完成: {chain_id}")
    
    def _create_system_wallet(self) -> str:
        """创建系统钱包"""
        wallet_id = "SOM_SYSTEM_WALLET_" + hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        # 创建系统钱包
        wallet_data = {
            "wallet_id": wallet_id,
            "creation_time": time.time(),
            "wallet_type": "SYSTEM",
            "balance": 1000000000.0,  # 初始系统币总量
            "transaction_count": 0
        }
        
        # 保存钱包
        self.wallets[wallet_id] = wallet_data
        
        # 更新经济数据
        self.economic_data.total_supply = 1000000000.0
        self.economic_data.circulating_supply = 0.0  # 系统钱包中的币还未流通
        
        logger.info(f"创建系统钱包: {wallet_id}")
        return wallet_id
    
    def create_wallet(self, node_id: str, wallet_type: str = "STANDARD") -> str:
        """创建钱包
        
        Args:
            node_id: 节点ID
            wallet_type: 钱包类型
            
        Returns:
            钱包ID
        """
        # 生成钱包ID
        wallet_id = f"WALLET_{node_id}_{int(time.time())}"
        
        # 创建钱包
        wallet_data = {
            "wallet_id": wallet_id,
            "node_id": node_id,
            "creation_time": time.time(),
            "wallet_type": wallet_type,
            "balance": 0.0,
            "transaction_count": 0
        }
        
        # 保存钱包
        self.wallets[wallet_id] = wallet_data
        
        # 更新经济数据
        self.economic_data.active_wallets += 1
        
        # 记录到区块链
        if hasattr(self, 'som_chain'):
            # 使用现有实现
            pass  # 现有实现会自动处理
        else:
            # 使用新实现
            transaction_data = {
                "type": SomTransactionTypes.SYSTEM_EVENT.value,
                "event": "wallet_creation",
                "wallet_id": wallet_id,
                "node_id": node_id,
                "wallet_type": wallet_type,
                "timestamp": time.time()
            }
            self.sub_blockchain.add_transaction(node_id, "SYSTEM", 0, transaction_data)
        
        logger.info(f"创建钱包: {wallet_id} 节点: {node_id} 类型: {wallet_type}")
        
        # 奖励新钱包
        self.reward_wallet(wallet_id, "wallet_creation", 10.0)
        
        return wallet_id
    
    def reward_wallet(self, wallet_id: str, reason: str, amount: float) -> str:
        """奖励钱包
        
        Args:
            wallet_id: 钱包ID
            reason: 奖励原因
            amount: 奖励金额
            
        Returns:
            交易ID
        """
        if wallet_id not in self.wallets:
            logger.warning(f"钱包不存在: {wallet_id}")
            return None
        
        # 生成交易ID
        tx_id = f"TX_{wallet_id}_{int(time.time())}"
        
        # 创建奖励交易
        transaction_data = {
            "type": SomTransactionTypes.REWARD.value,
            "tx_id": tx_id,
            "from_wallet": self.system_wallet_id,
            "to_wallet": wallet_id,
            "amount": amount,
            "reason": reason,
            "timestamp": time.time()
        }
        
        # 记录到区块链
        if hasattr(self, 'som_chain'):
            # 使用现有实现
            tx_id = self.som_chain.create_som_coin(amount, self.wallets[wallet_id].get("node_id", "unknown"))
        else:
            # 使用新实现
            self.sub_blockchain.add_transaction(
                self.system_wallet_id, wallet_id, amount, transaction_data
            )
        
        # 更新钱包余额
        self.wallets[wallet_id]["balance"] += amount
        self.wallets[wallet_id]["transaction_count"] += 1
        
        # 更新经济数据
        self.economic_data.circulating_supply += amount
        self.economic_data.transaction_count += 1
        
        # 保存交易记录
        self.transactions[tx_id] = transaction_data
        
        logger.info(f"奖励钱包: {wallet_id} 金额: {amount} 原因: {reason}")
        return tx_id
    
    def transfer(self, from_wallet: str, to_wallet: str, amount: float, memo: str = "") -> str:
        """转账
        
        Args:
            from_wallet: 源钱包ID
            to_wallet: 目标钱包ID
            amount: 金额
            memo: 备注
            
        Returns:
            交易ID
        """
        # 验证钱包
        if from_wallet not in self.wallets:
            logger.warning(f"源钱包不存在: {from_wallet}")
            return None
        
        if to_wallet not in self.wallets:
            logger.warning(f"目标钱包不存在: {to_wallet}")
            return None
        
        # 验证余额
        if self.wallets[from_wallet]["balance"] < amount:
            logger.warning(f"余额不足: {from_wallet} 余额: {self.wallets[from_wallet]['balance']} 需要: {amount}")
            return None
        
        # 生成交易ID
        tx_id = f"TX_{from_wallet}_{to_wallet}_{int(time.time())}"
        
        # 创建转账交易
        transaction_data = {
            "type": SomTransactionTypes.COIN_TRANSFER.value,
            "tx_id": tx_id,
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "amount": amount,
            "memo": memo,
            "timestamp": time.time()
        }
        
        # 记录到区块链
        if hasattr(self, 'som_chain'):
            # 使用现有实现
            tx_id = self.som_chain.transfer_som_coin(
                self.wallets[from_wallet].get("node_id", "unknown"),
                self.wallets[to_wallet].get("node_id", "unknown"),
                amount,
                memo
            )
        else:
            # 使用新实现
            self.sub_blockchain.add_transaction(
                from_wallet, to_wallet, amount, transaction_data
            )
        
        # 更新钱包余额
        self.wallets[from_wallet]["balance"] -= amount
        self.wallets[to_wallet]["balance"] += amount
        self.wallets[from_wallet]["transaction_count"] += 1
        self.wallets[to_wallet]["transaction_count"] += 1
        
        # 更新经济数据
        self.economic_data.transaction_count += 1
        
        # 保存交易记录
        self.transactions[tx_id] = transaction_data
        
        logger.info(f"转账: {from_wallet} -> {to_wallet} 金额: {amount} 备注: {memo}")
        return tx_id
    
    def get_wallet_balance(self, wallet_id: str) -> float:
        """获取钱包余额
        
        Args:
            wallet_id: 钱包ID
            
        Returns:
            余额
        """
        if wallet_id not in self.wallets:
            logger.warning(f"钱包不存在: {wallet_id}")
            return 0.0
        
        return self.wallets[wallet_id]["balance"]
    
    def get_economic_status(self) -> Dict:
        """获取经济状态
        
        Returns:
            经济状态数据
        """
        return self.economic_data.to_dict()
    
    def create_som_coin(self, amount: float, reason: str = "system_issuance") -> str:
        """创建松麦币
        
        Args:
            amount: 创建数量
            reason: 创建原因
            
        Returns:
            交易ID
        """
        # 生成交易ID
        tx_id = f"TX_CREATION_{int(time.time())}"
        
        # 创建松麦币创建交易
        transaction_data = {
            "type": SomTransactionTypes.COIN_CREATION.value,
            "tx_id": tx_id,
            "amount": amount,
            "reason": reason,
            "timestamp": time.time()
        }
        
        # 记录到区块链
        if hasattr(self, 'som_chain'):
            # 使用现有实现
            tx_id = self.som_chain.create_som_coin(amount, "SYSTEM")
        else:
            # 使用新实现
            self.sub_blockchain.add_transaction(
                "SYSTEM", self.system_wallet_id, amount, transaction_data
            )
        
        # 更新系统钱包余额
        self.wallets[self.system_wallet_id]["balance"] += amount
        
        # 更新经济数据
        self.economic_data.total_supply += amount
        
        # 保存交易记录
        self.transactions[tx_id] = transaction_data
        
        logger.info(f"创建松麦币: {amount} 原因: {reason}")
        return tx_id
    
    def sync_with_main_chain(self) -> bool:
        """与主链同步
        
        Returns:
            是否同步成功
        """
        if not self.main_chain:
            logger.warning("无法同步：主链未连接")
            return False
        
        try:
            # 向主链报告状态
            state_data = {
                "chain_id": self.sub_blockchain.chain_id,
                "model_type": "SOM",
                "economic_data": self.economic_data.to_dict(),
                "wallet_count": len(self.wallets),
                "transaction_count": len(self.transactions),
                "timestamp": time.time()
            }
            
            # 发送状态更新
            self.main_chain.process_cross_chain_transaction(
                from_chain=self.sub_blockchain.chain_id,
                to_chain="QSM_MAIN_CHAIN",
                data=state_data
            )
            
            logger.info(f"与主链同步成功: {self.sub_blockchain.chain_id}")
            return True
        except Exception as e:
            logger.error(f"与主链同步失败: {str(e)}")
            return False
    
    def export_to_json(self, file_path: str) -> None:
        """导出链数据到JSON文件
        
        Args:
            file_path: 文件路径
        """
        export_data = {
            "chain_id": self.sub_blockchain.chain_id,
            "economic_data": self.economic_data.to_dict(),
            "transactions": self.transactions,
            "wallets": self.wallets,
            "timestamp": time.time()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"导出链数据到: {file_path}")

# 全局单例实例
_som_chain_instance = None

def get_som_chain() -> SomQuantumChain:
    """获取SOM链单例实例"""
    global _som_chain_instance
    if _som_chain_instance is None:
        _som_chain_instance = SomQuantumChain()
    return _som_chain_instance 

"""
"""
量子基因编码: QE-SOM-99AE75E56FA8
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
