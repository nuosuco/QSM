"""
松麦钱包核心实现

这个模块实现了松麦钱包核心，用于管理用户的松麦币和其他数字资产。
钱包基于量子密钥生成器和量子钱包协议，提供安全的资产管理功能。
"""

import os
import sys
import json
import logging
import datetime
import hashlib
import uuid
import base64
from typing import List, Dict, Any, Optional, Tuple

# 导入量子区块链核心
from quantum_economy.blockchain.quantum_chain import (
    QuantumTransaction,
    QuantumState
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("wallet.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SomWallet")

class QuantumKeyDeriver:
    """量子密钥派生器"""
    
    def __init__(self, q_gene: bytes):
        """初始化量子密钥派生器
        
        Args:
            q_gene: 量子基因数据，用于生成密钥
        """
        self.q_gene = q_gene
        self.salt = os.urandom(16)
    
    def derive_key_pair(self) -> Tuple[str, str]:
        """派生密钥对
        
        Returns:
            (私钥, 公钥)元组
        """
        # 实际应用中会使用量子密钥生成算法
        # 这里使用伪随机数和哈希函数简化
        
        # 生成私钥
        private_key_base = hashlib.pbkdf2_hmac(
            'sha256', 
            self.q_gene, 
            self.salt, 
            100000
        )
        private_key = base64.b64encode(private_key_base).decode('utf-8')
        
        # 从私钥生成公钥
        public_key_base = hashlib.sha256(private_key_base).digest()
        public_key = base64.b64encode(public_key_base).decode('utf-8')
        
        return private_key, public_key
    
    def sign_transaction(self, private_key: str, data: Dict) -> str:
        """用私钥签名交易
        
        Args:
            private_key: 私钥
            data: 交易数据
            
        Returns:
            签名
        """
        # 序列化数据
        data_str = json.dumps(data, sort_keys=True)
        
        # 计算签名
        private_key_bytes = base64.b64decode(private_key)
        signature_base = hashlib.sha256(private_key_bytes + data_str.encode('utf-8')).digest()
        signature = base64.b64encode(signature_base).decode('utf-8')
        
        return signature
    
    @staticmethod
    def verify_signature(public_key: str, data: Dict, signature: str) -> bool:
        """验证签名
        
        Args:
            public_key: 公钥
            data: 交易数据
            signature: 签名
            
        Returns:
            是否有效
        """
        # 序列化数据
        data_str = json.dumps(data, sort_keys=True)
        
        try:
            # 计算期望的签名
            public_key_bytes = base64.b64decode(public_key)
            expected_sig_base = hashlib.sha256(public_key_bytes + data_str.encode('utf-8')).digest()
            expected_sig = base64.b64encode(expected_sig_base).decode('utf-8')
            
            # 验证签名
            return signature == expected_sig
        except Exception as e:
            logger.error(f"验证签名失败: {e}")
            return False


class SomWallet:
    """松麦钱包实现"""
    
    def __init__(self, user_id: str, q_gene: bytes = None):
        """初始化松麦钱包
        
        Args:
            user_id: 用户ID
            q_gene: 量子基因数据，如不提供则自动生成
        """
        # 如果未提供量子基因数据，则生成
        if q_gene is None:
            q_gene = os.urandom(32)
        
        # 初始化量子密钥派生器
        self.key_deriver = QuantumKeyDeriver(q_gene)
        
        # 用户ID
        self.user_id = user_id
        
        # 生成密钥对
        self.private_key, self.public_key = self.key_deriver.derive_key_pair()
        
        # 钱包地址是公钥的哈希
        self.wallet_address = hashlib.sha256(self.public_key.encode('utf-8')).hexdigest()
        
        # 钱包状态
        self.wallet_state = {
            "user_id": user_id,
            "wallet_address": self.wallet_address,
            "public_key": self.public_key,
            "creation_time": datetime.datetime.now().isoformat(),
            "last_updated": datetime.datetime.now().isoformat(),
            "balances": {
                "ref_coin": 0.0
            },
            "transactions": [],
            "assets": [],
            "contacts": {},
            "settings": {
                "default_fee": 0.001,  # 默认交易费率
                "auto_sync": True,     # 自动同步
                "security_level": "high"  # 安全级别
            }
        }
        
        logger.info(f"初始化松麦钱包: {self.wallet_address}, 用户: {user_id}")
    
    def get_balance(self, asset_type: str = "ref_coin") -> float:
        """获取资产余额
        
        Args:
            asset_type: 资产类型，默认为松麦币
            
        Returns:
            余额
        """
        return self.wallet_state["balances"].get(asset_type, 0.0)
    
    def deposit(self, amount: float, asset_type: str = "ref_coin", source: str = "external", memo: str = "") -> str:
        """存入资产
        
        Args:
            amount: 金额
            asset_type: 资产类型，默认为松麦币
            source: 来源
            memo: 备注
            
        Returns:
            交易ID
        """
        # 确保金额为正数
        if amount <= 0:
            logger.warning(f"存入金额必须为正数: {amount}")
            return None
        
        # 确保资产类型存在
        if asset_type not in self.wallet_state["balances"]:
            self.wallet_state["balances"][asset_type] = 0.0
        
        # 生成交易ID
        tx_id = str(uuid.uuid4())
        
        # 创建交易记录
        tx = {
            "tx_id": tx_id,
            "type": "deposit",
            "asset_type": asset_type,
            "amount": amount,
            "source": source,
            "memo": memo,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        # 更新余额
        self.wallet_state["balances"][asset_type] += amount
        
        # 记录交易
        self.wallet_state["transactions"].append(tx)
        
        # 更新钱包状态
        self.wallet_state["last_updated"] = datetime.datetime.now().isoformat()
        
        logger.info(f"存入资产: {amount} {asset_type}, 来源: {source}, 交易ID: {tx_id}")
        return tx_id
    
    def withdraw(self, amount: float, asset_type: str = "ref_coin", destination: str = "external", memo: str = "") -> str:
        """提取资产
        
        Args:
            amount: 金额
            asset_type: 资产类型，默认为松麦币
            destination: 目标
            memo: 备注
            
        Returns:
            交易ID
        """
        # 确保金额为正数
        if amount <= 0:
            logger.warning(f"提取金额必须为正数: {amount}")
            return None
        
        # 确保资产类型存在并且余额充足
        if asset_type not in self.wallet_state["balances"]:
            logger.warning(f"资产类型 {asset_type} 不存在")
            return None
        
        current_balance = self.wallet_state["balances"][asset_type]
        if current_balance < amount:
            logger.warning(f"余额不足: 当前 {current_balance} {asset_type}, 需要 {amount}")
            return None
        
        # 生成交易ID
        tx_id = str(uuid.uuid4())
        
        # 创建交易记录
        tx = {
            "tx_id": tx_id,
            "type": "withdraw",
            "asset_type": asset_type,
            "amount": amount,
            "destination": destination,
            "memo": memo,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        # 更新余额
        self.wallet_state["balances"][asset_type] -= amount
        
        # 记录交易
        self.wallet_state["transactions"].append(tx)
        
        # 更新钱包状态
        self.wallet_state["last_updated"] = datetime.datetime.now().isoformat()
        
        logger.info(f"提取资产: {amount} {asset_type}, 目标: {destination}, 交易ID: {tx_id}")
        return tx_id
    
    def transfer(self, to_address: str, amount: float, asset_type: str = "ref_coin", memo: str = "") -> str:
        """转账
        
        Args:
            to_address: 接收方钱包地址
            amount: 金额
            asset_type: 资产类型，默认为松麦币
            memo: 备注
            
        Returns:
            交易ID
        """
        # 确保不是转给自己
        if to_address == self.wallet_address:
            logger.warning("不能转账给自己")
            return None
        
        # 确保金额为正数
        if amount <= 0:
            logger.warning(f"转账金额必须为正数: {amount}")
            return None
        
        # 确保资产类型存在并且余额充足
        if asset_type not in self.wallet_state["balances"]:
            logger.warning(f"资产类型 {asset_type} 不存在")
            return None
        
        # 计算手续费
        fee = amount * self.wallet_state["settings"]["default_fee"]
        total_amount = amount + fee
        
        current_balance = self.wallet_state["balances"][asset_type]
        if current_balance < total_amount:
            logger.warning(f"余额不足: 当前 {current_balance} {asset_type}, 需要 {total_amount} (含手续费 {fee})")
            return None
        
        # 生成交易ID
        tx_id = str(uuid.uuid4())
        
        # 创建交易数据
        tx_data = {
            "tx_id": tx_id,
            "type": "transfer",
            "from_address": self.wallet_address,
            "to_address": to_address,
            "asset_type": asset_type,
            "amount": amount,
            "fee": fee,
            "memo": memo,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 签名交易
        signature = self.key_deriver.sign_transaction(self.private_key, tx_data)
        tx_data["signature"] = signature
        
        # 创建交易记录
        tx = {
            **tx_data,
            "status": "pending"
        }
        
        # 更新余额
        self.wallet_state["balances"][asset_type] -= total_amount
        
        # 记录交易
        self.wallet_state["transactions"].append(tx)
        
        # 更新钱包状态
        self.wallet_state["last_updated"] = datetime.datetime.now().isoformat()
        
        logger.info(f"转账: {amount} {asset_type} 到 {to_address}, 手续费: {fee}, 交易ID: {tx_id}")
        
        # 在实际应用中，这里会将交易广播到网络
        # 简化版本中直接确认交易
        self._confirm_transaction(tx_id)
        
        return tx_id
    
    def _confirm_transaction(self, tx_id: str) -> bool:
        """确认交易
        
        Args:
            tx_id: 交易ID
            
        Returns:
            是否成功确认
        """
        # 查找交易
        tx = None
        for t in self.wallet_state["transactions"]:
            if t["tx_id"] == tx_id:
                tx = t
                break
        
        if not tx:
            logger.warning(f"交易 {tx_id} 不存在")
            return False
        
        # 更新交易状态
        tx["status"] = "confirmed"
        tx["confirmation_time"] = datetime.datetime.now().isoformat()
        
        logger.info(f"确认交易: {tx_id}")
        return True
    
    def get_transaction_history(self, asset_type: str = None, limit: int = 10) -> List[Dict]:
        """获取交易历史
        
        Args:
            asset_type: 资产类型，如不提供则返回所有类型
            limit: 返回的最大交易数量
            
        Returns:
            交易列表
        """
        # 筛选交易
        if asset_type:
            filtered_txs = [tx for tx in self.wallet_state["transactions"] if tx.get("asset_type") == asset_type]
        else:
            filtered_txs = self.wallet_state["transactions"]
        
        # 按时间排序，最新的在前
        sorted_txs = sorted(
            filtered_txs,
            key=lambda tx: datetime.datetime.fromisoformat(tx["timestamp"]),
            reverse=True
        )
        
        # 限制数量
        return sorted_txs[:limit]
    
    def add_contact(self, name: str, wallet_address: str, memo: str = "") -> bool:
        """添加联系人
        
        Args:
            name: 联系人名称
            wallet_address: 钱包地址
            memo: 备注
            
        Returns:
            是否成功添加
        """
        if name in self.wallet_state["contacts"]:
            logger.warning(f"联系人 {name} 已存在")
            return False
        
        # 添加联系人
        self.wallet_state["contacts"][name] = {
            "name": name,
            "wallet_address": wallet_address,
            "memo": memo,
            "creation_time": datetime.datetime.now().isoformat()
        }
        
        # 更新钱包状态
        self.wallet_state["last_updated"] = datetime.datetime.now().isoformat()
        
        logger.info(f"添加联系人: {name}, 地址: {wallet_address}")
        return True
    
    def update_settings(self, settings: Dict) -> bool:
        """更新设置
        
        Args:
            settings: 新设置
            
        Returns:
            是否成功更新
        """
        # 更新设置
        for key, value in settings.items():
            if key in self.wallet_state["settings"]:
                self.wallet_state["settings"][key] = value
        
        # 更新钱包状态
        self.wallet_state["last_updated"] = datetime.datetime.now().isoformat()
        
        logger.info(f"更新设置: {settings}")
        return True
    
    def backup(self) -> Dict:
        """备份钱包数据
        
        Returns:
            备份数据
        """
        backup_data = {
            "wallet_state": self.wallet_state,
            "public_key": self.public_key,
            "backup_time": datetime.datetime.now().isoformat()
        }
        
        logger.info(f"备份钱包: {self.wallet_address}")
        return backup_data
    
    def export_private_key(self, password: str) -> str:
        """导出加密私钥
        
        Args:
            password: 密码，用于加密私钥
            
        Returns:
            加密的私钥
        """
        # 实际应用中会使用强加密算法
        # 这里使用简单的异或加密简化
        password_hash = hashlib.sha256(password.encode('utf-8')).digest()
        private_key_bytes = base64.b64decode(self.private_key)
        
        # 确保密码哈希长度与私钥相同
        if len(password_hash) < len(private_key_bytes):
            password_hash = password_hash * (len(private_key_bytes) // len(password_hash) + 1)
        password_hash = password_hash[:len(private_key_bytes)]
        
        # 异或加密
        encrypted_bytes = bytes(a ^ b for a, b in zip(private_key_bytes, password_hash))
        encrypted_key = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        logger.info(f"导出加密私钥: {self.wallet_address}")
        return encrypted_key
    
    @classmethod
    def import_private_key(cls, user_id: str, encrypted_key: str, password: str) -> 'SomWallet':
        """从加密私钥导入钱包
        
        Args:
            user_id: 用户ID
            encrypted_key: 加密的私钥
            password: 密码，用于解密私钥
            
        Returns:
            松麦钱包对象
        """
        try:
            # 解密私钥
            encrypted_bytes = base64.b64decode(encrypted_key)
            password_hash = hashlib.sha256(password.encode('utf-8')).digest()
            
            # 确保密码哈希长度与加密私钥相同
            if len(password_hash) < len(encrypted_bytes):
                password_hash = password_hash * (len(encrypted_bytes) // len(password_hash) + 1)
            password_hash = password_hash[:len(encrypted_bytes)]
            
            # 异或解密
            private_key_bytes = bytes(a ^ b for a, b in zip(encrypted_bytes, password_hash))
            private_key = base64.b64encode(private_key_bytes).decode('utf-8')
            
            # 创建钱包
            wallet = cls(user_id)
            wallet.private_key = private_key
            
            # 从私钥重新生成公钥
            public_key_base = hashlib.sha256(private_key_bytes).digest()
            wallet.public_key = base64.b64encode(public_key_base).decode('utf-8')
            
            # 重新计算钱包地址
            wallet.wallet_address = hashlib.sha256(wallet.public_key.encode('utf-8')).hexdigest()
            wallet.wallet_state["wallet_address"] = wallet.wallet_address
            wallet.wallet_state["public_key"] = wallet.public_key
            
            logger.info(f"从加密私钥导入钱包: {wallet.wallet_address}, 用户: {user_id}")
            return wallet
        except Exception as e:
            logger.error(f"从加密私钥导入钱包失败: {e}")
            return None
    
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "wallet_state": self.wallet_state,
            "public_key": self.public_key
            # 注意：不包含私钥
        }
    
    @classmethod
    def from_dict(cls, data: Dict, user_id: str = None) -> 'SomWallet':
        """从字典恢复钱包
        
        Args:
            data: 钱包数据
            user_id: 用户ID，如不提供则使用数据中的用户ID
            
        Returns:
            松麦钱包对象
        """
        # 如果未提供用户ID，则使用数据中的用户ID
        if user_id is None:
            user_id = data["wallet_state"]["user_id"]
        
        # 创建钱包
        wallet = cls(user_id)
        
        # 恢复钱包状态
        wallet.wallet_state = data["wallet_state"]
        wallet.public_key = data["public_key"]
        wallet.wallet_address = wallet.wallet_state["wallet_address"]
        
        logger.info(f"从字典恢复钱包: {wallet.wallet_address}, 用户: {user_id}")
        return wallet
    
    def save_to_file(self, filepath: str) -> bool:
        """保存钱包状态到文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            是否成功保存
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
            logger.info(f"成功保存钱包状态到 {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存钱包状态失败: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str, user_id: str = None) -> 'SomWallet':
        """从文件加载钱包状态
        
        Args:
            filepath: 文件路径
            user_id: 用户ID，如不提供则使用文件中的用户ID
            
        Returns:
            松麦钱包对象
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.info(f"成功从 {filepath} 加载钱包状态")
            return cls.from_dict(data, user_id)
        except Exception as e:
            logger.error(f"加载钱包状态失败: {e}")
            return None
    
    # QuantumWalletAPI 兼容接口
    def quantum_transfer(self, asset_qubit: Dict) -> Dict:
        """量子转账
        
        与量子钱包协议兼容的方法
        
        Args:
            asset_qubit: 资产量子位，包含转账信息
            
        Returns:
            转账结果
        """
        # 解析资产量子位
        to_address = asset_qubit.get("to_address")
        amount = asset_qubit.get("amount", 0.0)
        asset_type = asset_qubit.get("asset_type", "ref_coin")
        memo = asset_qubit.get("memo", "")
        
        # 执行转账
        tx_id = self.transfer(to_address, amount, asset_type, memo)
        
        if tx_id:
            return {
                "success": True,
                "tx_id": tx_id,
                "message": f"成功转账 {amount} {asset_type} 到 {to_address}"
            }
        else:
            return {
                "success": False,
                "message": "转账失败"
            } 

"""

"""
量子基因编码: QE-WAL-D92FB93CA133
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
