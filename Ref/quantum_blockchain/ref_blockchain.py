"""
Ref Quantum Blockchain
Ref量子区块链 - 实现量子引用模型的子链区块链，专注于系统自我修复和引用优化
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
    from quantum_core.quantum_blockchain.QSM_main_chain import get_QSM_main_chain
except ImportError:
    print("无法导入量子区块链核心，请确保已安装相关依赖")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ref_blockchain.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Ref区块链")

class RefTransactionTypes(Enum):
    """Ref交易类型"""
    BUG_REPORT = "bug_report"                # 错误报告
    REPAIR_OPERATION = "repair_operation"    # 修复操作
    OPTIMIZATION = "optimization"            # 优化
    SYSTEM_MONITOR = "system_monitor"        # 系统监控
    COIN_CREATION = "coin_creation"          # 松麦币创建
    COIN_TRANSFER = "coin_transfer"          # 松麦币转账
    WALLET_CREATION = "wallet_creation"      # 钱包创建
    REWARD = "reward"                        # 奖励
    SYSTEM_EVENT = "system_event"            # 系统事件

@dataclass
class RefWalletInfo:
    """Ref钱包信息"""
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
    def from_dict(cls, data: Dict) -> 'RefWalletInfo':
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
class RefCoinTransaction:
    """Ref币交易"""
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
    def from_dict(cls, data: Dict) -> 'RefCoinTransaction':
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

@dataclass
class BugReport:
    """错误报告"""
    bug_id: str
    reporter_id: str
    component: str
    description: str
    severity: int  # 1-5, 5最严重
    timestamp: float
    status: str  # 'open', 'verified', 'fixed', 'closed'
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "bug_id": self.bug_id,
            "reporter_id": self.reporter_id,
            "component": self.component,
            "description": self.description,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BugReport':
        """从字典创建错误报告"""
        return cls(
            bug_id=data.get("bug_id", ""),
            reporter_id=data.get("reporter_id", ""),
            component=data.get("component", ""),
            description=data.get("description", ""),
            severity=data.get("severity", 1),
            timestamp=data.get("timestamp", 0.0),
            status=data.get("status", "open")
        )

@dataclass
class RepairOperation:
    """修复操作"""
    repair_id: str
    bug_id: str
    repairer_id: str
    repair_method: str
    changes: Dict
    timestamp: float
    success: bool
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "repair_id": self.repair_id,
            "bug_id": self.bug_id,
            "repairer_id": self.repairer_id,
            "repair_method": self.repair_method,
            "changes": self.changes,
            "timestamp": self.timestamp,
            "success": self.success
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RepairOperation':
        """从字典创建修复操作"""
        return cls(
            repair_id=data.get("repair_id", ""),
            bug_id=data.get("bug_id", ""),
            repairer_id=data.get("repairer_id", ""),
            repair_method=data.get("repair_method", ""),
            changes=data.get("changes", {}),
            timestamp=data.get("timestamp", 0.0),
            success=data.get("success", False)
        )

class RefQuantumChain:
    """Ref量子链实现"""
    
    def __init__(self, chain_id: str = None):
        """初始化Ref量子链
        
        Args:
            chain_id: 链唯一标识，如不提供则自动生成
        """
        if not chain_id:
            chain_id = "REF_CHAIN_" + hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
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
                model_type="Ref",
                features=["bug_tracking", "self_repair", "system_optimization"]
            )
            logger.info(f"向主链注册Ref量子链: {chain_id}")
        except Exception as e:
            logger.warning(f"无法获取主链或注册子链: {str(e)}")
            self.main_chain = None
        
        # 错误报告
        self.bug_reports = {}
        
        # 修复操作
        self.repair_operations = {}
        
        # 系统健康状态
        self.system_health = {
            "overall_health": 1.0,  # 1.0 = 100% 健康
            "components": {},
            "recent_repairs": 0,
            "pending_bugs": 0,
            "optimization_level": 0.8  # 初始优化水平
        }
        
        # 钱包系统
        self.wallets = {}
        
        # 系统钱包
        self.system_wallet_id = self._create_system_wallet()
        
        # 交易记录
        self.transactions = {}
        
        logger.info(f"Ref量子链初始化完成: {chain_id}")
    
    def _create_system_wallet(self) -> str:
        """创建系统钱包"""
        wallet_id = "REF_SYSTEM_WALLET_" + hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
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
        wallet_id = f"REF_WALLET_{node_id}_{int(time.time())}"
        
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
            "type": RefTransactionTypes.WALLET_CREATION.value,
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
        tx_id = f"REF_TX_{wallet_id}_{int(time.time())}"
        
        # 创建奖励交易
        transaction_data = {
            "type": RefTransactionTypes.REWARD.value,
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
        tx_id = f"REF_TX_{from_wallet}_{to_wallet}_{int(time.time())}"
        
        # 创建转账交易
        transaction_data = {
            "type": RefTransactionTypes.COIN_TRANSFER.value,
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
    
    def create_som_coin(self, amount: float, reason: str = "ref_chain_issuance") -> str:
        """创建松麦币
        
        Args:
            amount: 创建数量
            reason: 创建原因
            
        Returns:
            交易ID
        """
        # 生成交易ID
        tx_id = f"REF_CREATION_{int(time.time())}"
        
        # 创建松麦币创建交易
        transaction_data = {
            "type": RefTransactionTypes.COIN_CREATION.value,
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
        
        logger.info(f"Ref子链创建松麦币: {amount} 原因: {reason}")
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
    
    def get_wallet_info(self, wallet_id: str) -> Optional[RefWalletInfo]:
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
        return RefWalletInfo(
            wallet_id=wallet_data["wallet_id"],
            node_id=wallet_data["node_id"],
            creation_time=wallet_data["creation_time"],
            balance=wallet_data["balance"],
            last_active=wallet_data.get("last_active", wallet_data["creation_time"]),
            transaction_count=wallet_data["transaction_count"],
            wallet_type=wallet_data["wallet_type"],
            features=wallet_data.get("features", [])
        )
    
    def report_bug(self, reporter_id: str, component: str, description: str, severity: int = 3) -> str:
        """报告错误
        
        Args:
            reporter_id: 报告者ID
            component: 组件名称
            description: 错误描述
            severity: 严重程度 (1-5)
            
        Returns:
            错误ID
        """
        # 验证严重程度
        if severity < 1 or severity > 5:
            severity = 3  # 默认中等严重程度
        
        # 生成错误ID
        bug_id = f"BUG_{component}_{int(time.time())}"
        
        # 创建错误报告
        bug_data = BugReport(
            bug_id=bug_id,
            reporter_id=reporter_id,
            component=component,
            description=description,
            severity=severity,
            timestamp=time.time(),
            status="open"
        )
        
        # 保存错误报告
        self.bug_reports[bug_id] = bug_data.to_dict()
        
        # 更新系统健康状态
        self.system_health["pending_bugs"] += 1
        if component not in self.system_health["components"]:
            self.system_health["components"][component] = 1.0
        self.system_health["components"][component] -= 0.1 * severity / 5.0
        self.system_health["components"][component] = max(0.0, self.system_health["components"][component])
        self._update_overall_health()
        
        # 记录到区块链
        transaction_data = {
            "type": RefTransactionTypes.BUG_REPORT.value,
            "bug_id": bug_id,
            "reporter_id": reporter_id,
            "component": component,
            "severity": severity,
            "timestamp": time.time()
        }
        self.sub_blockchain.add_transaction(reporter_id, "SYSTEM", 0, transaction_data)
        
        logger.info(f"报告错误: {bug_id}, 组件: {component}, 报告者: {reporter_id}, 严重程度: {severity}")
        
        # 奖励报告者
        reporter_wallet = None
        for wallet_id, wallet in self.wallets.items():
            if wallet["node_id"] == reporter_id:
                reporter_wallet = wallet_id
                break
        
        # 如果报告者有钱包，则奖励
        if reporter_wallet:
            # 根据严重程度确定奖励金额
            reward_amount = severity * 2.0  # 严重程度越高，奖励越多
            self.reward_wallet(reporter_wallet, "bug_report", reward_amount)
            logger.info(f"奖励报告者 {reporter_id} 错误报告: {reward_amount} 松麦币")
        
        return bug_id
    
    def repair_bug(self, repairer_id: str, bug_id: str, repair_method: str, changes: Dict) -> str:
        """修复错误
        
        Args:
            repairer_id: 修复者ID
            bug_id: 错误ID
            repair_method: 修复方法
            changes: 变更内容
            
        Returns:
            修复ID
        """
        # 验证错误ID
        if bug_id not in self.bug_reports:
            logger.warning(f"错误不存在: {bug_id}")
            return None
        
        # 获取错误报告
        bug_report = BugReport.from_dict(self.bug_reports[bug_id])
        
        # 生成修复ID
        repair_id = f"REPAIR_{bug_id}_{int(time.time())}"
        
        # 创建修复操作
        repair_data = RepairOperation(
            repair_id=repair_id,
            bug_id=bug_id,
            repairer_id=repairer_id,
            repair_method=repair_method,
            changes=changes,
            timestamp=time.time(),
            success=True  # 默认修复成功
        )
        
        # 保存修复操作
        self.repair_operations[repair_id] = repair_data.to_dict()
        
        # 更新错误状态
        bug_report.status = "fixed"
        self.bug_reports[bug_id] = bug_report.to_dict()
        
        # 更新系统健康状态
        self.system_health["pending_bugs"] -= 1
        self.system_health["recent_repairs"] += 1
        component = bug_report.component
        if component in self.system_health["components"]:
            self.system_health["components"][component] += 0.15  # 修复后健康度上升
            self.system_health["components"][component] = min(1.0, self.system_health["components"][component])
        self._update_overall_health()
        
        # 记录到区块链
        transaction_data = {
            "type": RefTransactionTypes.REPAIR_OPERATION.value,
            "repair_id": repair_id,
            "bug_id": bug_id,
            "repairer_id": repairer_id,
            "timestamp": time.time()
        }
        self.sub_blockchain.add_transaction(repairer_id, "SYSTEM", 0, transaction_data)
        
        logger.info(f"修复错误: {bug_id}, 修复ID: {repair_id}, 修复者: {repairer_id}")
        
        # 奖励修复者
        repairer_wallet = None
        for wallet_id, wallet in self.wallets.items():
            if wallet["node_id"] == repairer_id:
                repairer_wallet = wallet_id
                break
        
        # 如果修复者有钱包，则奖励
        if repairer_wallet:
            # 根据错误严重程度确定奖励金额
            severity = bug_report.severity
            reward_amount = severity * 5.0  # 严重程度越高，修复奖励越多
            self.reward_wallet(repairer_wallet, "bug_repair", reward_amount)
            logger.info(f"奖励修复者 {repairer_id} 错误修复: {reward_amount} 松麦币")
        
        return repair_id
    
    def optimize_system(self, optimizer_id: str, component: str, optimization_type: str, changes: Dict) -> str:
        """优化系统
        
        Args:
            optimizer_id: 优化者ID
            component: 组件名称
            optimization_type: 优化类型
            changes: 变更内容
            
        Returns:
            优化ID
        """
        # 生成优化ID
        optimization_id = f"OPT_{component}_{int(time.time())}"
        
        # 创建优化数据
        optimization_data = {
            "optimization_id": optimization_id,
            "optimizer_id": optimizer_id,
            "component": component,
            "optimization_type": optimization_type,
            "changes": changes,
            "timestamp": time.time(),
            "success": True  # 默认优化成功
        }
        
        # 更新系统健康状态
        if component not in self.system_health["components"]:
            self.system_health["components"][component] = 0.8
        self.system_health["components"][component] += 0.05  # 优化后健康度小幅上升
        self.system_health["components"][component] = min(1.0, self.system_health["components"][component])
        self.system_health["optimization_level"] += 0.02  # 整体优化水平提升
        self.system_health["optimization_level"] = min(1.0, self.system_health["optimization_level"])
        self._update_overall_health()
        
        # 记录到区块链
        transaction_data = {
            "type": RefTransactionTypes.OPTIMIZATION.value,
            "optimization_id": optimization_id,
            "optimizer_id": optimizer_id,
            "component": component,
            "optimization_type": optimization_type,
            "timestamp": time.time()
        }
        self.sub_blockchain.add_transaction(optimizer_id, "SYSTEM", 0, transaction_data)
        
        logger.info(f"优化系统: {optimization_id}, 组件: {component}, 优化者: {optimizer_id}, 类型: {optimization_type}")
        
        # 奖励优化者
        optimizer_wallet = None
        for wallet_id, wallet in self.wallets.items():
            if wallet["node_id"] == optimizer_id:
                optimizer_wallet = wallet_id
                break
        
        # 如果优化者有钱包，则奖励
        if optimizer_wallet:
            # 根据优化类型确定奖励金额
            reward_amount = 8.0  # 基础优化奖励
            if optimization_type == "performance":
                reward_amount = 12.0  # 性能优化奖励更多
            elif optimization_type == "security":
                reward_amount = 15.0  # 安全优化奖励最多
            
            self.reward_wallet(optimizer_wallet, "system_optimization", reward_amount)
            logger.info(f"奖励优化者 {optimizer_id} 系统优化: {reward_amount} 松麦币")
        
        return optimization_id
    
    def monitor_system(self, component: str, metrics: Dict) -> str:
        """监控系统
        
        Args:
            component: 组件名称
            metrics: 监控指标
            
        Returns:
            监控ID
        """
        # 生成监控ID
        monitor_id = f"MONITOR_{component}_{int(time.time())}"
        
        # 创建监控数据
        monitor_data = {
            "monitor_id": monitor_id,
            "component": component,
            "metrics": metrics,
            "timestamp": time.time()
        }
        
        # 记录到区块链
        transaction_data = {
            "type": RefTransactionTypes.SYSTEM_MONITOR.value,
            "monitor_id": monitor_id,
            "component": component,
            "timestamp": time.time()
        }
        self.sub_blockchain.add_transaction("MONITOR_SYSTEM", "SYSTEM", 0, transaction_data)
        
        logger.info(f"监控系统: {monitor_id}, 组件: {component}")
        return monitor_id
    
    def _update_overall_health(self) -> None:
        """更新整体系统健康状态"""
        # 计算组件健康度平均值
        component_health = 1.0
        if self.system_health["components"]:
            component_health = sum(self.system_health["components"].values()) / len(self.system_health["components"])
        
        # 计算错误影响
        bug_factor = max(0.0, 1.0 - 0.1 * self.system_health["pending_bugs"])
        
        # 计算整体健康度
        self.system_health["overall_health"] = (
            component_health * 0.6 +
            bug_factor * 0.3 +
            self.system_health["optimization_level"] * 0.1
        )
    
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
                "model_type": "Ref",
                "system_health": self.system_health,
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
            "bug_reports": self.bug_reports,
            "repair_operations": self.repair_operations,
            "system_health": self.system_health,
            "wallets": self.wallets,
            "transactions": self.transactions,
            "timestamp": time.time()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"导出链数据到: {file_path}")

# 全局单例实例
_ref_chain_instance = None

def get_ref_chain() -> RefQuantumChain:
    """获取Ref链单例实例"""
    global _ref_chain_instance
    if _ref_chain_instance is None:
        _ref_chain_instance = RefQuantumChain()
    return _ref_chain_instance 

"""

"""
量子基因编码: QE-REF-B255B2071EFB
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
