"""
QSM Main Quantum Blockchain
QSM主量子区块链 - 实现量子叠加态模型的主量子区块链，负责管理子链通信和协调
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
from dataclasses import dataclass, field
import threading
import asyncio
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入量子区块链核心
try:
    from quantum_core.quantum_blockchain.quantum_blockchain_core import (
        MainQuantumBlockchain, 
        SubQuantumBlockchain,
        QuantumBlock,
        _existing_implementation
    )
    if _existing_implementation:
        from quantum_economy.blockchain.main_chain import (
            MainChain,
            CrossChainTransaction
        )
except ImportError:
    print("无法导入量子区块链核心，请确保已安装相关依赖")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("qsm_main_chain.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("QSM主链")

class MainChainTransactionTypes(Enum):
    """主链交易类型"""
    SUBCHAIN_REGISTRATION = "subchain_registration"  # 子链注册
    CROSS_CHAIN_TRANSACTION = "cross_chain_tx"      # 跨链交易
    IDENTITY_VERIFICATION = "identity_verification"  # 身份验证
    GLOBAL_STATE_UPDATE = "global_state_update"      # 全局状态更新
    COIN_CREATION = "coin_creation"                  # 松麦币创建
    COIN_TRANSFER = "coin_transfer"                  # 松麦币转账
    WALLET_CREATION = "wallet_creation"              # 钱包创建
    REWARD = "reward"                                # 奖励
    SYSTEM_EVENT = "system_event"                    # 系统事件

@dataclass
class SubchainInfo:
    """子链信息"""
    chain_id: str                       # 子链ID
    model_type: str                     # 模型类型 (WeQ, SOM, Ref)
    registration_time: float            # 注册时间
    last_sync_time: float = 0.0         # 上次同步时间
    block_height: int = 0               # 区块高度
    status: str = "active"              # 状态
    features: List[str] = field(default_factory=list)  # 功能列表
    version: str = "1.0.0"              # 版本
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "chain_id": self.chain_id,
            "model_type": self.model_type,
            "registration_time": self.registration_time,
            "last_sync_time": self.last_sync_time,
            "block_height": self.block_height,
            "status": self.status,
            "features": self.features,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SubchainInfo':
        """从字典创建子链信息"""
        return cls(
            chain_id=data["chain_id"],
            model_type=data["model_type"],
            registration_time=data["registration_time"],
            last_sync_time=data.get("last_sync_time", 0.0),
            block_height=data.get("block_height", 0),
            status=data.get("status", "active"),
            features=data.get("features", []),
            version=data.get("version", "1.0.0")
        )

@dataclass
class CrossChainTransactionInfo:
    """跨链交易信息"""
    tx_id: str                          # 交易ID
    source_chain_id: str                # 源链ID
    target_chain_id: str                # 目标链ID
    tx_data: Dict                       # 交易数据
    status: str = "pending"             # 状态
    timestamp: float = field(default_factory=time.time)  # 时间戳
    confirmation_time: float = 0.0      # 确认时间
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "tx_id": self.tx_id,
            "source_chain_id": self.source_chain_id,
            "target_chain_id": self.target_chain_id,
            "tx_data": self.tx_data,
            "status": self.status,
            "timestamp": self.timestamp,
            "confirmation_time": self.confirmation_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CrossChainTransactionInfo':
        """从字典创建跨链交易信息"""
        return cls(
            tx_id=data["tx_id"],
            source_chain_id=data["source_chain_id"],
            target_chain_id=data["target_chain_id"],
            tx_data=data["tx_data"],
            status=data.get("status", "pending"),
            timestamp=data.get("timestamp", time.time()),
            confirmation_time=data.get("confirmation_time", 0.0)
        )

@dataclass
class QsmWalletInfo:
    """QSM钱包信息"""
    wallet_id: str
    node_id: str
    creation_time: float
    balance: float
    last_active: float
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
            "transaction_count": self.transaction_count,
            "wallet_type": self.wallet_type,
            "features": self.features
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'QsmWalletInfo':
        """从字典创建钱包信息"""
        return cls(
            wallet_id=data.get("wallet_id", ""),
            node_id=data.get("node_id", ""),
            creation_time=data.get("creation_time", 0.0),
            balance=data.get("balance", 0.0),
            last_active=data.get("last_active", 0.0),
            transaction_count=data.get("transaction_count", 0),
            wallet_type=data.get("wallet_type", "STANDARD"),
            features=data.get("features", [])
        )

@dataclass
class QsmCoinTransaction:
    """QSM币交易"""
    transaction_id: str
    from_wallet: str
    to_wallet: str
    amount: float
    timestamp: float
    transaction_type: str
    data: Dict[str, Any]
    signature: str
    
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
    def from_dict(cls, data: Dict) -> 'QsmCoinTransaction':
        """从字典创建交易"""
        return cls(
            transaction_id=data.get("transaction_id", ""),
            from_wallet=data.get("from_wallet", ""),
            to_wallet=data.get("to_wallet", ""),
            amount=data.get("amount", 0.0),
            timestamp=data.get("timestamp", 0.0),
            transaction_type=data.get("transaction_type", ""),
            data=data.get("data", {}),
            signature=data.get("signature", "")
        )

class QsmMainChain:
    """QSM主量子链实现"""
    
    def __init__(self, chain_id: str = "QSM_MAIN_CHAIN"):
        """初始化QSM主量子链
        
        Args:
            chain_id: 链唯一标识，建议保持默认值
        """
        # 初始化主链
        self.main_blockchain = MainQuantumBlockchain(
            chain_id=chain_id,
            difficulty=5  # 主链难度更高
        )
        
        # 子链注册表
        self.subchains = {}
        
        # 量子纠缠关系
        self.entanglements = {}
        
        # 全局状态
        self.global_state = {
            "registered_subchains": {},
            "cross_chain_transactions": {},
            "identity_registry": {},
            "economic_data": {
                "total_supply": 0.0,
                "circulating_supply": 0.0,
                "transaction_count": 0
            }
        }
        
        # 钱包系统
        self.wallets = {}
        
        # 系统钱包
        self.system_wallet_id = self._create_system_wallet()
        
        # 交易记录
        self.transactions = {}
        
        logger.info(f"QSM主量子链初始化完成: {chain_id}")
    
    def _create_system_wallet(self) -> str:
        """创建系统钱包"""
        wallet_id = "QSM_SYSTEM_WALLET_" + hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        # 创建系统钱包
        wallet_data = {
            "wallet_id": wallet_id,
            "node_id": "SYSTEM",
            "creation_time": time.time(),
            "wallet_type": "SYSTEM",
            "balance": 1000000000.0,  # 初始系统币总量
            "transaction_count": 0,
            "last_active": time.time(),
            "features": ["system_operations", "coin_creation", "reward_distribution"]
        }
        
        # 保存钱包
        self.wallets[wallet_id] = wallet_data
        
        # 更新经济数据
        self.global_state["economic_data"]["total_supply"] = 1000000000.0
        
        logger.info(f"创建QSM系统钱包: {wallet_id}")
        return wallet_id
    
    def register_subchain(self, chain_id: str, model_type: str, features: List[str]) -> bool:
        """注册子链
        
        Args:
            chain_id: 子链ID
            model_type: 模型类型 (SOM|WeQ|Ref)
            features: 子链功能列表
            
        Returns:
            注册是否成功
        """
        if chain_id in self.subchains:
            logger.warning(f"子链已注册: {chain_id}")
            return False
        
        # 创建子链注册信息
        subchain_info = {
            "chain_id": chain_id,
            "model_type": model_type,
            "features": features,
            "registration_time": time.time(),
            "last_active": time.time(),
            "status": "active"
        }
        
        # 保存子链信息
        self.subchains[chain_id] = subchain_info
        self.global_state["registered_subchains"][chain_id] = subchain_info
        
        # 创建与子链的量子纠缠
        self._create_entanglement(chain_id)
        
        # 记录到区块链
        transaction_data = {
            "type": MainChainTransactionTypes.SUBCHAIN_REGISTRATION.value,
            "chain_id": chain_id,
            "model_type": model_type,
            "features": features,
            "timestamp": time.time()
        }
        self.main_blockchain.add_transaction("SYSTEM", chain_id, 0, transaction_data)
        
        logger.info(f"注册子链: {chain_id}, 类型: {model_type}")
        return True
    
    def _create_entanglement(self, chain_id: str) -> None:
        """创建与子链的量子纠缠关系
        
        Args:
            chain_id: 子链ID
        """
        # 生成量子纠缠密钥
        entanglement_key = hashlib.sha256(f"{self.main_blockchain.chain_id}_{chain_id}_{time.time()}".encode()).hexdigest()
        
        # 保存纠缠关系
        self.entanglements[chain_id] = {
            "entanglement_key": entanglement_key,
            "creation_time": time.time(),
            "last_sync": time.time(),
            "sync_count": 0,
            "channel_quality": 1.0  # 初始纠缠通道质量
        }
        
        logger.info(f"创建与子链 {chain_id} 的量子纠缠")
    
    def process_cross_chain_transaction(self, from_chain: str, to_chain: str, data: Dict) -> str:
        """处理跨链交易
        
        Args:
            from_chain: 源链ID
            to_chain: 目标链ID
            data: 交易数据
            
        Returns:
            交易ID
        """
        # 验证源链
        if from_chain not in self.subchains and from_chain != self.main_blockchain.chain_id:
            logger.warning(f"源链未注册: {from_chain}")
            return None
        
        # 验证目标链
        if to_chain not in self.subchains and to_chain != self.main_blockchain.chain_id:
            logger.warning(f"目标链未注册: {to_chain}")
            return None
        
        # 生成交易ID
        tx_id = f"CROSS_TX_{from_chain}_{to_chain}_{int(time.time())}"
        
        # 创建跨链交易
        transaction_data = {
            "type": MainChainTransactionTypes.CROSS_CHAIN_TRANSACTION.value,
            "tx_id": tx_id,
            "from_chain": from_chain,
            "to_chain": to_chain,
            "data": data,
            "timestamp": time.time()
        }
        
        # 记录到区块链
        self.main_blockchain.add_transaction(from_chain, to_chain, 0, transaction_data)
        
        # 保存交易记录
        self.global_state["cross_chain_transactions"][tx_id] = transaction_data
        
        # 更新纠缠关系
        if from_chain in self.entanglements:
            self.entanglements[from_chain]["last_sync"] = time.time()
            self.entanglements[from_chain]["sync_count"] += 1
        
        if to_chain in self.entanglements:
            self.entanglements[to_chain]["last_sync"] = time.time()
            self.entanglements[to_chain]["sync_count"] += 1
        
        logger.info(f"处理跨链交易: {from_chain} -> {to_chain}, 交易ID: {tx_id}")
        return tx_id
    
    def update_global_state(self, state_key: str, state_value: Any) -> bool:
        """更新全局状态
        
        Args:
            state_key: 状态键
            state_value: 状态值
            
        Returns:
            更新是否成功
        """
        # 更新全局状态
        self.global_state[state_key] = state_value
        
        # 记录到区块链
        transaction_data = {
            "type": MainChainTransactionTypes.GLOBAL_STATE_UPDATE.value,
            "state_key": state_key,
            "timestamp": time.time()
        }
        self.main_blockchain.add_transaction("SYSTEM", "GLOBAL_STATE", 0, transaction_data)
        
        logger.info(f"更新全局状态: {state_key}")
        return True
    
    def verify_identity(self, entity_id: str, identity_proof: Dict) -> bool:
        """验证身份
        
        Args:
            entity_id: 实体ID
            identity_proof: 身份证明
            
        Returns:
            验证是否成功
        """
        # 验证身份证明
        # 实际实现中应该有更复杂的验证逻辑
        is_valid = True
        
        if is_valid:
            # 保存身份记录
            self.global_state["identity_registry"][entity_id] = {
                "entity_id": entity_id,
                "verification_time": time.time(),
                "status": "verified"
            }
            
            # 记录到区块链
            transaction_data = {
                "type": MainChainTransactionTypes.IDENTITY_VERIFICATION.value,
                "entity_id": entity_id,
                "timestamp": time.time()
            }
            self.main_blockchain.add_transaction("IDENTITY_VERIFIER", entity_id, 0, transaction_data)
            
            logger.info(f"验证身份: {entity_id}")
            return True
        else:
            logger.warning(f"身份验证失败: {entity_id}")
            return False
    
    def create_wallet(self, node_id: str, wallet_type: str = "STANDARD") -> str:
        """创建钱包
        
        Args:
            node_id: 节点ID
            wallet_type: 钱包类型
            
        Returns:
            钱包ID
        """
        # 生成钱包ID
        wallet_id = f"QSM_WALLET_{node_id}_{int(time.time())}"
        
        # 创建钱包
        wallet_data = {
            "wallet_id": wallet_id,
            "node_id": node_id,
            "creation_time": time.time(),
            "wallet_type": wallet_type,
            "balance": 0.0,
            "transaction_count": 0,
            "last_active": time.time(),
            "features": []
        }
        
        # 保存钱包
        self.wallets[wallet_id] = wallet_data
        
        # 记录到区块链
        transaction_data = {
            "type": MainChainTransactionTypes.WALLET_CREATION.value,
            "wallet_id": wallet_id,
            "node_id": node_id,
            "wallet_type": wallet_type,
            "timestamp": time.time()
        }
        self.main_blockchain.add_transaction("SYSTEM", node_id, 0, transaction_data)
        
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
        tx_id = f"QSM_TX_{wallet_id}_{int(time.time())}"
        
        # 创建奖励交易
        transaction_data = {
            "type": MainChainTransactionTypes.REWARD.value,
            "tx_id": tx_id,
            "from_wallet": self.system_wallet_id,
            "to_wallet": wallet_id,
            "amount": amount,
            "reason": reason,
            "timestamp": time.time()
        }
        
        # 记录到区块链
        self.main_blockchain.add_transaction(
            self.system_wallet_id, wallet_id, amount, transaction_data
        )
        
        # 更新钱包余额
        self.wallets[wallet_id]["balance"] += amount
        self.wallets[wallet_id]["transaction_count"] += 1
        self.wallets[wallet_id]["last_active"] = time.time()
        
        # 更新经济数据
        self.global_state["economic_data"]["circulating_supply"] += amount
        self.global_state["economic_data"]["transaction_count"] += 1
        
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
        tx_id = f"QSM_TX_{from_wallet}_{to_wallet}_{int(time.time())}"
        
        # 创建转账交易
        transaction_data = {
            "type": MainChainTransactionTypes.COIN_TRANSFER.value,
            "tx_id": tx_id,
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "amount": amount,
            "memo": memo,
            "timestamp": time.time()
        }
        
        # 记录到区块链
        self.main_blockchain.add_transaction(
            from_wallet, to_wallet, amount, transaction_data
        )
        
        # 更新钱包余额
        self.wallets[from_wallet]["balance"] -= amount
        self.wallets[to_wallet]["balance"] += amount
        self.wallets[from_wallet]["transaction_count"] += 1
        self.wallets[to_wallet]["transaction_count"] += 1
        self.wallets[from_wallet]["last_active"] = time.time()
        self.wallets[to_wallet]["last_active"] = time.time()
        
        # 更新经济数据
        self.global_state["economic_data"]["transaction_count"] += 1
        
        # 保存交易记录
        self.transactions[tx_id] = transaction_data
        
        logger.info(f"转账: {from_wallet} -> {to_wallet} 金额: {amount} 备注: {memo}")
        return tx_id
    
    def create_som_coin(self, amount: float, reason: str = "main_chain_issuance") -> str:
        """创建松麦币
        
        Args:
            amount: 创建数量
            reason: 创建原因
            
        Returns:
            交易ID
        """
        # 生成交易ID
        tx_id = f"QSM_CREATION_{int(time.time())}"
        
        # 创建松麦币创建交易
        transaction_data = {
            "type": MainChainTransactionTypes.COIN_CREATION.value,
            "tx_id": tx_id,
            "amount": amount,
            "reason": reason,
            "timestamp": time.time()
        }
        
        # 记录到区块链
        self.main_blockchain.add_transaction(
            "SYSTEM", self.system_wallet_id, amount, transaction_data
        )
        
        # 更新系统钱包余额
        self.wallets[self.system_wallet_id]["balance"] += amount
        
        # 更新经济数据
        self.global_state["economic_data"]["total_supply"] += amount
        
        # 保存交易记录
        self.transactions[tx_id] = transaction_data
        
        logger.info(f"QSM主链创建松麦币: {amount} 原因: {reason}")
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
    
    def get_wallet_info(self, wallet_id: str) -> Optional[QsmWalletInfo]:
        """获取钱包信息
        
        Args:
            wallet_id: 钱包ID
            
        Returns:
            钱包信息
        """
        if wallet_id not in self.wallets:
            logger.warning(f"钱包不存在: {wallet_id}")
            return None
        
        wallet_data = self.wallets[wallet_id]
        return QsmWalletInfo(
            wallet_id=wallet_data["wallet_id"],
            node_id=wallet_data["node_id"],
            creation_time=wallet_data["creation_time"],
            balance=wallet_data["balance"],
            last_active=wallet_data.get("last_active", wallet_data["creation_time"]),
            transaction_count=wallet_data["transaction_count"],
            wallet_type=wallet_data["wallet_type"],
            features=wallet_data.get("features", [])
        )
    
    def get_economic_status(self) -> Dict:
        """获取经济状态
        
        Returns:
            经济状态数据
        """
        return self.global_state["economic_data"]
    
    def export_to_json(self, file_path: str) -> None:
        """导出链数据到JSON文件
        
        Args:
            file_path: 文件路径
        """
        export_data = {
            "chain_id": self.main_blockchain.chain_id,
            "subchains": self.subchains,
            "entanglements": self.entanglements,
            "global_state": self.global_state,
            "wallets": self.wallets,
            "transactions": self.transactions,
            "timestamp": time.time()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"导出链数据到: {file_path}")

# 全局单例实例
_qsm_main_chain_instance = None

def get_qsm_main_chain() -> QsmMainChain:
    """获取QSM主链单例实例"""
    global _qsm_main_chain_instance
    if _qsm_main_chain_instance is None:
        _qsm_main_chain_instance = QsmMainChain()
    return _qsm_main_chain_instance

"""
"""
量子基因编码: QE-QSM-E75CAC606669
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
