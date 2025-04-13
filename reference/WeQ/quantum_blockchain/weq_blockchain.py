"""
WeQ Quantum Blockchain
WeQ量子区块链 - 实现量子意向模型的子链区块链，专注于对话内容处理、知识记录及智能交互
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
except ImportError:
    print("无法导入量子区块链核心，请确保已安装相关依赖")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("weq_blockchain.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("WeQ区块链")

class WeqTransactionTypes(Enum):
    """WeQ交易类型"""
    DIALOGUE_RECORD = "dialogue_record"        # 对话记录
    KNOWLEDGE_CREATION = "knowledge_creation"  # 知识创建
    INTERACTION_EVENT = "interaction_event"    # 交互事件
    MODEL_UPDATE = "model_update"              # 模型更新
    COIN_CREATION = "coin_creation"            # 松麦币创建
    COIN_TRANSFER = "coin_transfer"            # 松麦币转账
    WALLET_CREATION = "wallet_creation"        # 钱包创建
    REWARD = "reward"                          # 奖励
    SYSTEM_EVENT = "system_event"              # 系统事件

@dataclass
class WeqDialogueData:
    """WeQ对话数据"""
    dialogue_id: str
    user_id: str
    content: str
    timestamp: float
    context: Dict
    metrics: Dict
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "dialogue_id": self.dialogue_id,
            "user_id": self.user_id,
            "content": self.content,
            "timestamp": self.timestamp,
            "context": self.context,
            "metrics": self.metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WeqDialogueData':
        """从字典创建对话数据"""
        return cls(
            dialogue_id=data.get("dialogue_id", ""),
            user_id=data.get("user_id", ""),
            content=data.get("content", ""),
            timestamp=data.get("timestamp", 0.0),
            context=data.get("context", {}),
            metrics=data.get("metrics", {})
        )

@dataclass
class WeqWalletInfo:
    """WeQ钱包信息"""
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
    def from_dict(cls, data: Dict) -> 'WeqWalletInfo':
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
class WeqCoinTransaction:
    """WeQ币交易"""
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
    def from_dict(cls, data: Dict) -> 'WeqCoinTransaction':
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

class WeqQuantumChain:
    """WeQ量子链实现"""
    
    def __init__(self, chain_id: str = None):
        """初始化WeQ量子链
        
        Args:
            chain_id: 链唯一标识，如不提供则自动生成
        """
        if not chain_id:
            chain_id = "WEQ_CHAIN_" + hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        # 创建子链
        self.sub_blockchain = SubQuantumBlockchain(
            chain_id=chain_id,
            difficulty=4
        )
        
        # 尝试获取主链
        try:
            self.main_chain = get_qsm_main_chain()
            # 向主链注册
            self.main_chain.register_subchain(
                chain_id=chain_id,
                model_type="WeQ",
                features=["dialogue_processing", "knowledge_management", "intent_recognition"]
            )
            logger.info(f"向主链注册WeQ量子链: {chain_id}")
        except Exception as e:
            logger.warning(f"无法获取主链或注册子链: {str(e)}")
            self.main_chain = None
        
        # 对话记录
        self.dialogues = {}
        
        # 知识库
        self.knowledge_base = {}
        
        # 交互统计
        self.interaction_stats = {
            "total_dialogues": 0,
            "total_knowledge_items": 0,
            "active_users": 0,
            "dialogue_quality_score": 0.0
        }
        
        # 钱包系统
        self.wallets = {}
        
        # 系统钱包
        self.system_wallet_id = self._create_system_wallet()
        
        # 交易记录
        self.transactions = {}
        
        logger.info(f"WeQ量子链初始化完成: {chain_id}")
    
    def _create_system_wallet(self) -> str:
        """创建系统钱包"""
        wallet_id = "WEQ_SYSTEM_WALLET_" + hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
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
        wallet_id = f"WEQ_WALLET_{node_id}_{int(time.time())}"
        
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
            "type": WeqTransactionTypes.WALLET_CREATION.value,
            "wallet_id": wallet_id,
            "node_id": node_id,
            "wallet_type": wallet_type,
            "timestamp": time.time()
        }
        self.sub_blockchain.add_transaction("SYSTEM", node_id, 0, transaction_data)
        
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
        tx_id = f"WEQ_TX_{wallet_id}_{int(time.time())}"
        
        # 创建奖励交易
        transaction_data = {
            "type": WeqTransactionTypes.REWARD.value,
            "tx_id": tx_id,
            "from_wallet": self.system_wallet_id,
            "to_wallet": wallet_id,
            "amount": amount,
            "reason": reason,
            "timestamp": time.time()
        }
        
        # 记录到区块链
        self.sub_blockchain.add_transaction(
            self.system_wallet_id, wallet_id, amount, transaction_data
        )
        
        # 更新钱包余额
        self.wallets[wallet_id]["balance"] += amount
        self.wallets[wallet_id]["transaction_count"] += 1
        self.wallets[wallet_id]["last_active"] = time.time()
        
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
        tx_id = f"WEQ_TX_{from_wallet}_{to_wallet}_{int(time.time())}"
        
        # 创建转账交易
        transaction_data = {
            "type": WeqTransactionTypes.COIN_TRANSFER.value,
            "tx_id": tx_id,
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "amount": amount,
            "memo": memo,
            "timestamp": time.time()
        }
        
        # 记录到区块链
        self.sub_blockchain.add_transaction(
            from_wallet, to_wallet, amount, transaction_data
        )
        
        # 更新钱包余额
        self.wallets[from_wallet]["balance"] -= amount
        self.wallets[to_wallet]["balance"] += amount
        self.wallets[from_wallet]["transaction_count"] += 1
        self.wallets[to_wallet]["transaction_count"] += 1
        self.wallets[from_wallet]["last_active"] = time.time()
        self.wallets[to_wallet]["last_active"] = time.time()
        
        # 保存交易记录
        self.transactions[tx_id] = transaction_data
        
        logger.info(f"转账: {from_wallet} -> {to_wallet} 金额: {amount} 备注: {memo}")
        return tx_id
    
    def create_som_coin(self, amount: float, reason: str = "weq_chain_issuance") -> str:
        """创建松麦币
        
        Args:
            amount: 创建数量
            reason: 创建原因
            
        Returns:
            交易ID
        """
        # 生成交易ID
        tx_id = f"WEQ_CREATION_{int(time.time())}"
        
        # 创建松麦币创建交易
        transaction_data = {
            "type": WeqTransactionTypes.COIN_CREATION.value,
            "tx_id": tx_id,
            "amount": amount,
            "reason": reason,
            "timestamp": time.time()
        }
        
        # 记录到区块链
        self.sub_blockchain.add_transaction(
            "SYSTEM", self.system_wallet_id, amount, transaction_data
        )
        
        # 更新系统钱包余额
        self.wallets[self.system_wallet_id]["balance"] += amount
        
        # 保存交易记录
        self.transactions[tx_id] = transaction_data
        
        logger.info(f"WeQ子链创建松麦币: {amount} 原因: {reason}")
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
    
    def get_wallet_info(self, wallet_id: str) -> Optional[WeqWalletInfo]:
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
        return WeqWalletInfo(
            wallet_id=wallet_data["wallet_id"],
            node_id=wallet_data["node_id"],
            creation_time=wallet_data["creation_time"],
            balance=wallet_data["balance"],
            last_active=wallet_data.get("last_active", wallet_data["creation_time"]),
            transaction_count=wallet_data["transaction_count"],
            wallet_type=wallet_data["wallet_type"],
            features=wallet_data.get("features", [])
        )
    
    def record_dialogue(self, user_id: str, content: str, context: Dict = None, metrics: Dict = None) -> str:
        """记录对话
        
        Args:
            user_id: 用户ID
            content: 对话内容
            context: 上下文信息
            metrics: 对话质量指标
            
        Returns:
            对话ID
        """
        # 生成对话ID
        dialogue_id = f"DIALOGUE_{user_id}_{int(time.time())}"
        
        # 创建对话数据
        dialogue_data = WeqDialogueData(
            dialogue_id=dialogue_id,
            user_id=user_id,
            content=content,
            timestamp=time.time(),
            context=context or {},
            metrics=metrics or {"quality": 0.8, "relevance": 0.7}
        )
        
        # 保存对话记录
        self.dialogues[dialogue_id] = dialogue_data.to_dict()
        
        # 更新交互统计
        self.interaction_stats["total_dialogues"] += 1
        if user_id not in [d["user_id"] for d in self.dialogues.values()]:
            self.interaction_stats["active_users"] += 1
        
        # 计算对话质量分数
        quality_score = dialogue_data.metrics.get("quality", 0.8)
        relevance_score = dialogue_data.metrics.get("relevance", 0.7)
        new_quality_score = (quality_score + relevance_score) / 2
        self.interaction_stats["dialogue_quality_score"] = (
            (self.interaction_stats["dialogue_quality_score"] * (self.interaction_stats["total_dialogues"] - 1) + new_quality_score) /
            self.interaction_stats["total_dialogues"]
        )
        
        # 记录到区块链
        transaction_data = {
            "type": WeqTransactionTypes.DIALOGUE_RECORD.value,
            "dialogue_id": dialogue_id,
            "user_id": user_id,
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            "timestamp": time.time(),
            "metrics": metrics or {"quality": 0.8, "relevance": 0.7}
        }
        self.sub_blockchain.add_transaction(user_id, "SYSTEM", 0, transaction_data)
        
        logger.info(f"记录对话: {dialogue_id}, 用户: {user_id}")
        
        # 根据对话质量奖励用户
        if quality_score > 0.7:
            # 查找用户钱包
            user_wallet = None
            for wallet_id, wallet in self.wallets.items():
                if wallet["node_id"] == user_id:
                    user_wallet = wallet_id
                    break
            
            # 如果用户有钱包，则奖励
            if user_wallet:
                reward_amount = quality_score * 5  # 根据质量奖励0-5个松麦币
                self.reward_wallet(user_wallet, "quality_dialogue", reward_amount)
                logger.info(f"奖励用户 {user_id} 高质量对话: {reward_amount} 松麦币")
        
        return dialogue_id
    
    def create_knowledge(self, creator_id: str, knowledge_type: str, content: Dict, tags: List[str] = None) -> str:
        """创建知识
        
        Args:
            creator_id: 创建者ID
            knowledge_type: 知识类型
            content: 知识内容
            tags: 标签列表
            
        Returns:
            知识ID
        """
        # 生成知识ID
        knowledge_id = f"KNOWLEDGE_{knowledge_type}_{int(time.time())}"
        
        # 创建知识数据
        knowledge_data = {
            "knowledge_id": knowledge_id,
            "creator_id": creator_id,
            "knowledge_type": knowledge_type,
            "content": content,
            "tags": tags or [],
            "creation_time": time.time(),
            "updates": [],
            "references": []
        }
        
        # 保存知识
        self.knowledge_base[knowledge_id] = knowledge_data
        
        # 更新交互统计
        self.interaction_stats["total_knowledge_items"] += 1
        
        # 记录到区块链
        transaction_data = {
            "type": WeqTransactionTypes.KNOWLEDGE_CREATION.value,
            "knowledge_id": knowledge_id,
            "creator_id": creator_id,
            "knowledge_type": knowledge_type,
            "content_hash": hashlib.sha256(json.dumps(content).encode()).hexdigest(),
            "timestamp": time.time(),
            "tags": tags or []
        }
        self.sub_blockchain.add_transaction(creator_id, "KNOWLEDGE_BASE", 0, transaction_data)
        
        logger.info(f"创建知识: {knowledge_id}, 类型: {knowledge_type}, 创建者: {creator_id}")
        
        # 奖励知识创建者
        creator_wallet = None
        for wallet_id, wallet in self.wallets.items():
            if wallet["node_id"] == creator_id:
                creator_wallet = wallet_id
                break
        
        # 如果创建者有钱包，则奖励
        if creator_wallet:
            # 根据知识类型确定奖励金额
            reward_amount = 10.0  # 基础奖励
            if knowledge_type == "concept":
                reward_amount = 15.0  # 概念知识奖励更多
            elif knowledge_type == "procedure":
                reward_amount = 20.0  # 过程性知识奖励最多
            
            self.reward_wallet(creator_wallet, "knowledge_creation", reward_amount)
            logger.info(f"奖励创建者 {creator_id} 知识贡献: {reward_amount} 松麦币")
        
        return knowledge_id
    
    def record_interaction(self, user_id: str, interaction_type: str, data: Dict) -> str:
        """记录交互事件
        
        Args:
            user_id: 用户ID
            interaction_type: 交互类型
            data: 交互数据
            
        Returns:
            事件ID
        """
        # 生成事件ID
        event_id = f"EVENT_{interaction_type}_{int(time.time())}"
        
        # 记录到区块链
        transaction_data = {
            "type": WeqTransactionTypes.INTERACTION_EVENT.value,
            "event_id": event_id,
            "user_id": user_id,
            "interaction_type": interaction_type,
            "data": data,
            "timestamp": time.time()
        }
        self.sub_blockchain.add_transaction(user_id, "SYSTEM", 0, transaction_data)
        
        logger.info(f"记录交互事件: {event_id}, 类型: {interaction_type}, 用户: {user_id}")
        return event_id
    
    def update_weq_model(self, updater_id: str, model_component: str, update_data: Dict) -> str:
        """更新WeQ模型
        
        Args:
            updater_id: 更新者ID
            model_component: 模型组件
            update_data: 更新数据
            
        Returns:
            更新ID
        """
        # 生成更新ID
        update_id = f"UPDATE_{model_component}_{int(time.time())}"
        
        # 记录到区块链
        transaction_data = {
            "type": WeqTransactionTypes.MODEL_UPDATE.value,
            "update_id": update_id,
            "updater_id": updater_id,
            "model_component": model_component,
            "update_data": update_data,
            "timestamp": time.time()
        }
        self.sub_blockchain.add_transaction(updater_id, "MODEL_REGISTRY", 0, transaction_data)
        
        logger.info(f"更新WeQ模型: {update_id}, 组件: {model_component}, 更新者: {updater_id}")
        return update_id
    
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
                "model_type": "WeQ",
                "interaction_stats": self.interaction_stats,
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
            "dialogues": self.dialogues,
            "knowledge_base": self.knowledge_base,
            "interaction_stats": self.interaction_stats,
            "wallets": self.wallets,
            "transactions": self.transactions,
            "timestamp": time.time()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"导出链数据到: {file_path}")

# 全局单例实例
_weq_chain_instance = None

def get_weq_chain() -> WeqQuantumChain:
    """获取WeQ链单例实例"""
    global _weq_chain_instance
    if _weq_chain_instance is None:
        _weq_chain_instance = WeqQuantumChain()
    return _weq_chain_instance 

"""
"""
量子基因编码: QE-WEQ-2A4DE481F894
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
