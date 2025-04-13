"""
松麦子链实现

这个模块实现了松麦子链，专注于松麦生态系统中的经济交易。
子链管理松麦币、价值转移和经济循环，并与主链保持量子纠缠。
"""

import os
import sys
import json
import logging
import datetime
import hashlib
import uuid
from typing import List, Dict, Any, Optional

# 导入量子区块链核心
from quantum_economy.blockchain.quantum_chain import (
    QuantumChain, 
    QuantumTransaction,
    QuantumState
)
from quantum_economy.blockchain.quantum_asset import QuantumAsset

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("weq_chain.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SomChain")

class SomEconomyChain:
    """松麦经济子链实现"""
    
    def __init__(self, chain_id: str = None, main_chain_id: str = None):
        """初始化松麦经济子链
        
        Args:
            chain_id: 链唯一标识，如不提供则自动生成
            main_chain_id: 主链ID，用于建立与主链的纠缠
        """
        # 初始化核心组件
        self.quantum_chain = QuantumChain(
            chain_id=chain_id, 
            chain_type="economy"
        )
        
        # 主链ID
        self.main_chain_id = main_chain_id
        
        # 经济状态
        self.economy_state = {
            "weq_coin": {
                "total_supply": 0,
                "circulating_supply": 0,
                "current_value": 1.0,  # 初始价值，1 SOM = 1.0 单位标准价值
                "last_update": datetime.datetime.now().isoformat()
            },
            "transactions": {},
            "assets": {},
            "merchants": {},
            "products": {},
            "rewards": {},
            "parameters": {
                "reward_rate": 0.02,  # 奖励率
                "inflation_rate": 0.005,  # 通胀率
                "transaction_fee": 0.001  # 交易费率
            }
        }
        
        logger.info(f"初始化松麦经济子链: {self.quantum_chain.chain_id}, 主链: {main_chain_id}")
    
    def create_weq_coin(self, amount: float, creator_id: str = "system") -> str:
        """创建松麦币
        
        Args:
            amount: 创建数量
            creator_id: 创建者ID
            
        Returns:
            交易ID
        """
        # 确保数量为正数
        if amount <= 0:
            logger.warning(f"创建松麦币数量必须为正数: {amount}")
            return None
        
        # 创建松麦币
        tx_data = {
            "type": "weq_coin_creation",
            "amount": amount,
            "creator_id": creator_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 创建交易
        tx = QuantumTransaction(tx_data=tx_data, chain_ids=[self.quantum_chain.chain_id])
        
        # 添加到链
        self.quantum_chain.add_transaction(tx)
        
        # 更新经济状态
        self.economy_state["weq_coin"]["total_supply"] += amount
        self.economy_state["weq_coin"]["circulating_supply"] += amount
        self.economy_state["weq_coin"]["last_update"] = datetime.datetime.now().isoformat()
        
        # 记录交易
        self.economy_state["transactions"][tx.tx_id] = {
            "tx_id": tx.tx_id,
            "type": "weq_coin_creation",
            "amount": amount,
            "creator_id": creator_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        logger.info(f"创建松麦币: {amount}, 创建者: {creator_id}, 交易ID: {tx.tx_id}")
        return tx.tx_id
    
    def transfer_weq_coin(self, from_id: str, to_id: str, amount: float, memo: str = "") -> str:
        """转移松麦币
        
        Args:
            from_id: 转出方ID
            to_id: 转入方ID
            amount: 转移数量
            memo: 备注信息
            
        Returns:
            交易ID
        """
        # 确保数量为正数
        if amount <= 0:
            logger.warning(f"转移松麦币数量必须为正数: {amount}")
            return None
        
        # 创建松麦币转移交易
        tx_data = {
            "type": "weq_coin_transfer",
            "from_id": from_id,
            "to_id": to_id,
            "amount": amount,
            "memo": memo,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 计算交易费
        fee = amount * self.economy_state["parameters"]["transaction_fee"]
        
        # 创建交易
        tx = QuantumTransaction(tx_data=tx_data, chain_ids=[self.quantum_chain.chain_id])
        
        # 添加到链
        self.quantum_chain.add_transaction(tx)
        
        # 记录交易
        self.economy_state["transactions"][tx.tx_id] = {
            "tx_id": tx.tx_id,
            "type": "weq_coin_transfer",
            "from_id": from_id,
            "to_id": to_id,
            "amount": amount,
            "fee": fee,
            "memo": memo,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        logger.info(f"转移松麦币: {amount}, 从 {from_id} 到 {to_id}, 交易ID: {tx.tx_id}")
        return tx.tx_id
    
    def register_merchant(self, merchant_id: str, merchant_data: Dict) -> Dict:
        """注册商家
        
        Args:
            merchant_id: 商家ID
            merchant_data: 商家数据
            
        Returns:
            商家信息
        """
        if merchant_id in self.economy_state["merchants"]:
            logger.warning(f"商家 {merchant_id} 已注册")
            return self.economy_state["merchants"][merchant_id]
        
        # 创建商家记录
        merchant_info = {
            "merchant_id": merchant_id,
            "registration_time": datetime.datetime.now().isoformat(),
            "profile": merchant_data,
            "products": [],
            "transactions": [],
            "reputation": 5.0,  # 初始信誉分数，满分10分
            "status": "active"
        }
        
        # 注册商家
        self.economy_state["merchants"][merchant_id] = merchant_info
        
        # 创建注册交易
        tx_data = {
            "type": "merchant_registration",
            "merchant_id": merchant_id,
            "profile": merchant_data
        }
        
        # 创建交易
        tx = QuantumTransaction(tx_data=tx_data, chain_ids=[self.quantum_chain.chain_id])
        
        # 添加到链
        self.quantum_chain.add_transaction(tx)
        
        # 记录交易
        merchant_info["transactions"].append(tx.tx_id)
        self.economy_state["transactions"][tx.tx_id] = {
            "tx_id": tx.tx_id,
            "type": "merchant_registration",
            "merchant_id": merchant_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        logger.info(f"注册商家: {merchant_id}")
        return merchant_info
    
    def add_product(self, merchant_id: str, product_data: Dict) -> str:
        """添加商品
        
        Args:
            merchant_id: 商家ID
            product_data: 商品数据
            
        Returns:
            商品ID
        """
        if merchant_id not in self.economy_state["merchants"]:
            logger.warning(f"商家 {merchant_id} 不存在")
            return None
        
        # 生成商品ID
        product_id = str(uuid.uuid4())
        
        # 创建商品记录
        product_info = {
            "product_id": product_id,
            "merchant_id": merchant_id,
            "creation_time": datetime.datetime.now().isoformat(),
            "data": product_data,
            "status": "active"
        }
        
        # 添加商品
        self.economy_state["products"][product_id] = product_info
        
        # 更新商家商品列表
        self.economy_state["merchants"][merchant_id]["products"].append(product_id)
        
        # 创建商品添加交易
        tx_data = {
            "type": "product_addition",
            "merchant_id": merchant_id,
            "product_id": product_id,
            "product_data": product_data
        }
        
        # 创建交易
        tx = QuantumTransaction(tx_data=tx_data, chain_ids=[self.quantum_chain.chain_id])
        
        # 添加到链
        self.quantum_chain.add_transaction(tx)
        
        # 记录交易
        self.economy_state["merchants"][merchant_id]["transactions"].append(tx.tx_id)
        self.economy_state["transactions"][tx.tx_id] = {
            "tx_id": tx.tx_id,
            "type": "product_addition",
            "merchant_id": merchant_id,
            "product_id": product_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        logger.info(f"添加商品: {product_id}, 商家: {merchant_id}")
        return product_id
    
    def process_purchase(self, user_id: str, product_id: str, quantity: int, payment_method: str = "weq_coin") -> str:
        """处理购买交易
        
        Args:
            user_id: 用户ID
            product_id: 商品ID
            quantity: 购买数量
            payment_method: 支付方式
            
        Returns:
            交易ID
        """
        if product_id not in self.economy_state["products"]:
            logger.warning(f"商品 {product_id} 不存在")
            return None
        
        product = self.economy_state["products"][product_id]
        merchant_id = product["merchant_id"]
        
        # 确保商家存在
        if merchant_id not in self.economy_state["merchants"]:
            logger.warning(f"商家 {merchant_id} 不存在")
            return None
        
        # 确保商品状态正常
        if product["status"] != "active":
            logger.warning(f"商品 {product_id} 状态不正常: {product['status']}")
            return None
        
        # 计算总价
        unit_price = float(product["data"]["price"])
        total_price = unit_price * quantity
        
        # 创建购买交易
        tx_data = {
            "type": "purchase",
            "user_id": user_id,
            "merchant_id": merchant_id,
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price,
            "payment_method": payment_method,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 创建交易
        tx = QuantumTransaction(tx_data=tx_data, chain_ids=[self.quantum_chain.chain_id])
        
        # 添加到链
        self.quantum_chain.add_transaction(tx)
        
        # 计算奖励
        reward_amount = total_price * self.economy_state["parameters"]["reward_rate"]
        
        # 记录奖励
        reward_id = str(uuid.uuid4())
        self.economy_state["rewards"][reward_id] = {
            "reward_id": reward_id,
            "user_id": user_id,
            "amount": reward_amount,
            "transaction_id": tx.tx_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "pending"
        }
        
        # 记录交易
        self.economy_state["transactions"][tx.tx_id] = {
            "tx_id": tx.tx_id,
            "type": "purchase",
            "user_id": user_id,
            "merchant_id": merchant_id,
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price,
            "reward_id": reward_id,
            "payment_method": payment_method,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        logger.info(f"处理购买: 用户 {user_id}, 商品 {product_id}, 数量 {quantity}, 总价 {total_price}, 交易ID: {tx.tx_id}")
        return tx.tx_id
    
    def claim_reward(self, reward_id: str) -> str:
        """申领奖励
        
        Args:
            reward_id: 奖励ID
            
        Returns:
            交易ID
        """
        if reward_id not in self.economy_state["rewards"]:
            logger.warning(f"奖励 {reward_id} 不存在")
            return None
        
        reward = self.economy_state["rewards"][reward_id]
        
        # 确保奖励状态为待领取
        if reward["status"] != "pending":
            logger.warning(f"奖励 {reward_id} 状态不为待领取: {reward['status']}")
            return None
        
        user_id = reward["user_id"]
        amount = reward["amount"]
        
        # 创建奖励申领交易
        tx_data = {
            "type": "reward_claim",
            "reward_id": reward_id,
            "user_id": user_id,
            "amount": amount,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 创建交易
        tx = QuantumTransaction(tx_data=tx_data, chain_ids=[self.quantum_chain.chain_id])
        
        # 添加到链
        self.quantum_chain.add_transaction(tx)
        
        # 更新奖励状态
        self.economy_state["rewards"][reward_id]["status"] = "claimed"
        self.economy_state["rewards"][reward_id]["claim_time"] = datetime.datetime.now().isoformat()
        self.economy_state["rewards"][reward_id]["claim_transaction_id"] = tx.tx_id
        
        # 记录交易
        self.economy_state["transactions"][tx.tx_id] = {
            "tx_id": tx.tx_id,
            "type": "reward_claim",
            "reward_id": reward_id,
            "user_id": user_id,
            "amount": amount,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        logger.info(f"申领奖励: {reward_id}, 用户 {user_id}, 数量 {amount}, 交易ID: {tx.tx_id}")
        return tx.tx_id
    
    def adjust_weq_coin_value(self) -> float:
        """调整松麦币价值
        
        根据经济状态和交易活跃度动态调整松麦币价值
        
        Returns:
            新的松麦币价值
        """
        # 获取最近24小时的交易量
        recent_transactions = []
        now = datetime.datetime.now()
        for tx_id, tx in self.economy_state["transactions"].items():
            tx_time = datetime.datetime.fromisoformat(tx["timestamp"])
            if (now - tx_time).total_seconds() < 24 * 60 * 60:  # 24小时内
                recent_transactions.append(tx)
        
        transaction_volume = sum([tx.get("total_price", 0) for tx in recent_transactions if tx.get("type") == "purchase"])
        
        # 获取流通中的松麦币供应量
        circulating_supply = self.economy_state["weq_coin"]["circulating_supply"]
        
        # 简单的价值调整算法，实际应用中可以使用更复杂的经济模型
        if circulating_supply > 0:
            activity_factor = transaction_volume / circulating_supply
            current_value = self.economy_state["weq_coin"]["current_value"]
            
            # 应用通胀率
            inflation_rate = self.economy_state["parameters"]["inflation_rate"]
            
            # 新价值 = 当前价值 * (1 + 活跃度因子 - 通胀率)
            new_value = current_value * (1 + activity_factor - inflation_rate)
            
            # 限制价值变化幅度，防止剧烈波动
            max_change = 0.05  # 最大变化率为5%
            if new_value > current_value * (1 + max_change):
                new_value = current_value * (1 + max_change)
            elif new_value < current_value * (1 - max_change):
                new_value = current_value * (1 - max_change)
            
            # 更新价值
            self.economy_state["weq_coin"]["current_value"] = new_value
            self.economy_state["weq_coin"]["last_update"] = datetime.datetime.now().isoformat()
            
            logger.info(f"调整松麦币价值: {current_value} -> {new_value}, 交易量: {transaction_volume}, 流通量: {circulating_supply}")
            return new_value
        else:
            logger.warning("无法调整松麦币价值，流通量为0")
            return self.economy_state["weq_coin"]["current_value"]
    
    def mine_block(self) -> Dict:
        """挖掘新区块
        
        Returns:
            区块信息
        """
        # 调用量子链的挖矿方法
        block = self.quantum_chain.mine_block()
        
        # 经济子链的每个区块会自动调整松麦币价值
        self.adjust_weq_coin_value()
        
        logger.info(f"挖掘新区块: {block['block_id']}, 包含 {len(block['transactions'])} 笔交易")
        return block
    
    def get_weq_coin_info(self) -> Dict:
        """获取松麦币信息
        
        Returns:
            松麦币信息
        """
        return self.economy_state["weq_coin"]
    
    def get_merchant_info(self, merchant_id: str) -> Optional[Dict]:
        """获取商家信息
        
        Args:
            merchant_id: 商家ID
            
        Returns:
            商家信息或None
        """
        if merchant_id in self.economy_state["merchants"]:
            return self.economy_state["merchants"][merchant_id]
        else:
            logger.warning(f"商家 {merchant_id} 不存在")
            return None
    
    def get_product_info(self, product_id: str) -> Optional[Dict]:
        """获取商品信息
        
        Args:
            product_id: 商品ID
            
        Returns:
            商品信息或None
        """
        if product_id in self.economy_state["products"]:
            return self.economy_state["products"][product_id]
        else:
            logger.warning(f"商品 {product_id} 不存在")
            return None
    
    def get_transaction_info(self, tx_id: str) -> Optional[Dict]:
        """获取交易信息
        
        Args:
            tx_id: 交易ID
            
        Returns:
            交易信息或None
        """
        if tx_id in self.economy_state["transactions"]:
            return self.economy_state["transactions"][tx_id]
        else:
            logger.warning(f"交易 {tx_id} 不存在")
            return None
    
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "quantum_chain": self.quantum_chain.to_dict(),
            "main_chain_id": self.main_chain_id,
            "economy_state": self.economy_state
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SomEconomyChain':
        """从字典恢复子链"""
        economy_chain = cls(main_chain_id=data.get("main_chain_id"))
        economy_chain.quantum_chain = QuantumChain.from_dict(data["quantum_chain"])
        economy_chain.economy_state = data["economy_state"]
        return economy_chain
    
    def save_to_file(self, filepath: str) -> bool:
        """保存子链状态到文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            是否成功保存
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
            logger.info(f"成功保存经济子链状态到 {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存经济子链状态失败: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'SomEconomyChain':
        """从文件加载子链状态
        
        Args:
            filepath: 文件路径
            
        Returns:
            子链对象
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.info(f"成功从 {filepath} 加载经济子链状态")
            return cls.from_dict(data)
        except Exception as e:
            logger.error(f"加载经济子链状态失败: {e}")
            return None 

"""
"""
量子基因编码: QE-SOM-D4E656DB0AC7
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
