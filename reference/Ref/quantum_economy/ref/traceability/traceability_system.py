"""
松麦溯源系统实现

这个模块实现了松麦溯源系统，用于追踪产品从生产到销售的全过程。
溯源系统利用量子区块链技术确保数据的可信性和不可篡改性。
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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("traceability.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Traceability")

class SomTraceabilitySystem:
    """松麦溯源系统实现"""
    
    def __init__(self, chain_id: str = None, main_chain_id: str = None):
        """初始化松麦溯源系统
        
        Args:
            chain_id: 链唯一标识，如不提供则自动生成
            main_chain_id: 主链ID，用于建立与主链的纠缠
        """
        # 初始化核心组件
        self.quantum_chain = QuantumChain(
            chain_id=chain_id, 
            chain_type="traceability"
        )
        
        # 主链ID
        self.main_chain_id = main_chain_id
        
        # 溯源状态
        self.traceability_state = {
            "products": {},
            "producers": {},
            "supply_chain_records": {},
            "certifications": {},
            "trace_queries": {},
            "parameters": {
                "record_expiry_days": 3650,  # 溯源记录有效期，默认10年
                "verification_threshold": 0.95  # 验证阈值
            }
        }
        
        logger.info(f"初始化松麦溯源系统: {self.quantum_chain.chain_id}, 主链: {main_chain_id}")
    
    def register_producer(self, producer_id: str, producer_data: Dict) -> Dict:
        """注册生产者
        
        Args:
            producer_id: 生产者ID
            producer_data: 生产者数据
            
        Returns:
            生产者信息
        """
        if producer_id in self.traceability_state["producers"]:
            logger.warning(f"生产者 {producer_id} 已注册")
            return self.traceability_state["producers"][producer_id]
        
        # 创建生产者记录
        producer_info = {
            "producer_id": producer_id,
            "registration_time": datetime.datetime.now().isoformat(),
            "profile": producer_data,
            "products": [],
            "certifications": [],
            "records": [],
            "quantum_signature": self._generate_quantum_signature(),
            "reputation": 5.0,  # 初始信誉分数，满分10分
            "status": "active"
        }
        
        # 注册生产者
        self.traceability_state["producers"][producer_id] = producer_info
        
        # 创建注册交易
        tx_data = {
            "type": "producer_registration",
            "producer_id": producer_id,
            "profile": producer_data
        }
        
        # 创建交易
        tx = QuantumTransaction(tx_data=tx_data, chain_ids=[self.quantum_chain.chain_id])
        
        # 添加到链
        self.quantum_chain.add_transaction(tx)
        
        # 记录交易
        producer_info["records"].append(tx.tx_id)
        
        logger.info(f"注册生产者: {producer_id}")
        return producer_info
    
    def register_product(self, producer_id: str, product_data: Dict) -> str:
        """注册产品
        
        Args:
            producer_id: 生产者ID
            product_data: 产品数据
            
        Returns:
            产品ID
        """
        if producer_id not in self.traceability_state["producers"]:
            logger.warning(f"生产者 {producer_id} 不存在")
            return None
        
        # 生成产品ID
        product_id = str(uuid.uuid4())
        
        # 创建产品记录
        product_info = {
            "product_id": product_id,
            "producer_id": producer_id,
            "registration_time": datetime.datetime.now().isoformat(),
            "data": product_data,
            "supply_chain_stages": [],
            "certifications": [],
            "quantum_signature": self._generate_quantum_signature(),
            "status": "registered"
        }
        
        # 注册产品
        self.traceability_state["products"][product_id] = product_info
        
        # 更新生产者产品列表
        self.traceability_state["producers"][producer_id]["products"].append(product_id)
        
        # 创建注册交易
        tx_data = {
            "type": "product_registration",
            "product_id": product_id,
            "producer_id": producer_id,
            "product_data": product_data
        }
        
        # 创建交易
        tx = QuantumTransaction(tx_data=tx_data, chain_ids=[self.quantum_chain.chain_id])
        
        # 添加到链
        self.quantum_chain.add_transaction(tx)
        
        # 记录交易
        self.traceability_state["producers"][producer_id]["records"].append(tx.tx_id)
        
        logger.info(f"注册产品: {product_id}, 生产者: {producer_id}")
        return product_id
    
    def add_certification(self, entity_id: str, entity_type: str, certification_data: Dict) -> str:
        """添加认证
        
        Args:
            entity_id: 实体ID（产品ID或生产者ID）
            entity_type: 实体类型（'product'或'producer'）
            certification_data: 认证数据
            
        Returns:
            认证ID
        """
        # 检查实体类型
        if entity_type not in ["product", "producer"]:
            logger.warning(f"无效的实体类型: {entity_type}")
            return None
        
        # 检查实体是否存在
        if entity_type == "product" and entity_id not in self.traceability_state["products"]:
            logger.warning(f"产品 {entity_id} 不存在")
            return None
        elif entity_type == "producer" and entity_id not in self.traceability_state["producers"]:
            logger.warning(f"生产者 {entity_id} 不存在")
            return None
        
        # 生成认证ID
        certification_id = str(uuid.uuid4())
        
        # 创建认证记录
        certification_info = {
            "certification_id": certification_id,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "issuance_time": datetime.datetime.now().isoformat(),
            "expiry_time": certification_data.get("expiry_time"),
            "data": certification_data,
            "quantum_signature": self._generate_quantum_signature(),
            "status": "active"
        }
        
        # 注册认证
        self.traceability_state["certifications"][certification_id] = certification_info
        
        # 更新实体认证列表
        if entity_type == "product":
            self.traceability_state["products"][entity_id]["certifications"].append(certification_id)
        else:  # entity_type == "producer"
            self.traceability_state["producers"][entity_id]["certifications"].append(certification_id)
        
        # 创建认证交易
        tx_data = {
            "type": "certification_issuance",
            "certification_id": certification_id,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "certification_data": certification_data
        }
        
        # 创建交易
        tx = QuantumTransaction(tx_data=tx_data, chain_ids=[self.quantum_chain.chain_id])
        
        # 添加到链
        self.quantum_chain.add_transaction(tx)
        
        logger.info(f"添加认证: {certification_id}, 实体类型: {entity_type}, 实体ID: {entity_id}")
        return certification_id
    
    def record_supply_chain_stage(self, product_id: str, stage_data: Dict) -> str:
        """记录供应链阶段
        
        Args:
            product_id: 产品ID
            stage_data: 阶段数据
            
        Returns:
            记录ID
        """
        if product_id not in self.traceability_state["products"]:
            logger.warning(f"产品 {product_id} 不存在")
            return None
        
        # 生成记录ID
        record_id = str(uuid.uuid4())
        
        # 添加时间戳
        if "timestamp" not in stage_data:
            stage_data["timestamp"] = datetime.datetime.now().isoformat()
        
        # 创建记录
        record_info = {
            "record_id": record_id,
            "product_id": product_id,
            "stage_type": stage_data.get("stage_type", "unknown"),
            "timestamp": stage_data["timestamp"],
            "location": stage_data.get("location"),
            "data": stage_data,
            "previous_record_id": None,  # 默认为首个记录
            "quantum_signature": self._generate_quantum_signature(),
            "status": "active"
        }
        
        # 获取产品当前供应链阶段
        product_stages = self.traceability_state["products"][product_id]["supply_chain_stages"]
        if product_stages:
            # 如果有先前的记录，设置前向引用
            record_info["previous_record_id"] = product_stages[-1]
        
        # 注册记录
        self.traceability_state["supply_chain_records"][record_id] = record_info
        
        # 更新产品供应链阶段
        self.traceability_state["products"][product_id]["supply_chain_stages"].append(record_id)
        
        # 更新产品状态
        self.traceability_state["products"][product_id]["status"] = stage_data.get("new_product_status", self.traceability_state["products"][product_id]["status"])
        
        # 创建记录交易
        tx_data = {
            "type": "supply_chain_record",
            "record_id": record_id,
            "product_id": product_id,
            "stage_data": stage_data
        }
        
        # 创建交易
        tx = QuantumTransaction(tx_data=tx_data, chain_ids=[self.quantum_chain.chain_id])
        
        # 添加到链
        self.quantum_chain.add_transaction(tx)
        
        logger.info(f"记录供应链阶段: {record_id}, 产品: {product_id}, 阶段类型: {stage_data.get('stage_type', 'unknown')}")
        return record_id
    
    def trace_product(self, product_id: str, query_data: Dict = None) -> Dict:
        """追溯产品
        
        Args:
            product_id: 产品ID
            query_data: 查询数据
            
        Returns:
            追溯结果
        """
        if product_id not in self.traceability_state["products"]:
            logger.warning(f"产品 {product_id} 不存在")
            return {"error": "产品不存在"}
        
        # 获取产品信息
        product = self.traceability_state["products"][product_id]
        
        # 获取生产者信息
        producer_id = product["producer_id"]
        producer = self.traceability_state["producers"].get(producer_id)
        
        # 获取供应链记录
        supply_chain_records = []
        for record_id in product["supply_chain_stages"]:
            if record_id in self.traceability_state["supply_chain_records"]:
                supply_chain_records.append(self.traceability_state["supply_chain_records"][record_id])
        
        # 获取认证信息
        certifications = []
        for cert_id in product["certifications"]:
            if cert_id in self.traceability_state["certifications"]:
                certifications.append(self.traceability_state["certifications"][cert_id])
        
        # 创建追溯结果
        trace_result = {
            "product_id": product_id,
            "product_data": product["data"],
            "producer": {
                "producer_id": producer_id,
                "profile": producer["profile"] if producer else None
            },
            "supply_chain": supply_chain_records,
            "certifications": certifications,
            "status": product["status"],
            "verification": self._verify_product_integrity(product_id)
        }
        
        # 记录查询
        query_id = str(uuid.uuid4())
        self.traceability_state["trace_queries"][query_id] = {
            "query_id": query_id,
            "product_id": product_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "query_data": query_data or {},
            "result_summary": {
                "verification_status": trace_result["verification"]["status"],
                "supply_chain_stages_count": len(supply_chain_records),
                "certifications_count": len(certifications)
            }
        }
        
        # 创建查询交易
        tx_data = {
            "type": "product_trace_query",
            "query_id": query_id,
            "product_id": product_id,
            "query_data": query_data or {}
        }
        
        # 创建交易
        tx = QuantumTransaction(tx_data=tx_data, chain_ids=[self.quantum_chain.chain_id])
        
        # 添加到链
        self.quantum_chain.add_transaction(tx)
        
        logger.info(f"追溯产品: {product_id}, 查询ID: {query_id}")
        return trace_result
    
    def _verify_product_integrity(self, product_id: str) -> Dict:
        """验证产品完整性
        
        Args:
            product_id: 产品ID
            
        Returns:
            验证结果
        """
        if product_id not in self.traceability_state["products"]:
            return {"status": "error", "message": "产品不存在"}
        
        product = self.traceability_state["products"][product_id]
        
        # 验证供应链完整性
        chain_integrity = True
        chain_messages = []
        
        # 检查供应链各阶段的完整性
        previous_record_id = None
        for i, record_id in enumerate(product["supply_chain_stages"]):
            if record_id not in self.traceability_state["supply_chain_records"]:
                chain_integrity = False
                chain_messages.append(f"记录 {record_id} 不存在")
                continue
            
            record = self.traceability_state["supply_chain_records"][record_id]
            
            # 检查连续性
            if i > 0 and record["previous_record_id"] != previous_record_id:
                chain_integrity = False
                chain_messages.append(f"记录 {record_id} 的前向引用不正确")
            
            previous_record_id = record_id
        
        # 验证认证有效性
        cert_validity = True
        cert_messages = []
        
        now = datetime.datetime.now()
        for cert_id in product["certifications"]:
            if cert_id not in self.traceability_state["certifications"]:
                cert_validity = False
                cert_messages.append(f"认证 {cert_id} 不存在")
                continue
            
            cert = self.traceability_state["certifications"][cert_id]
            
            # 检查状态
            if cert["status"] != "active":
                cert_validity = False
                cert_messages.append(f"认证 {cert_id} 状态不正常: {cert['status']}")
            
            # 检查是否过期
            if cert["expiry_time"]:
                expiry_time = datetime.datetime.fromisoformat(cert["expiry_time"])
                if now > expiry_time:
                    cert_validity = False
                    cert_messages.append(f"认证 {cert_id} 已过期")
        
        # 综合评估
        verification_score = 0.0
        if chain_integrity and cert_validity:
            verification_score = 1.0
        elif chain_integrity:
            verification_score = 0.7
        elif cert_validity:
            verification_score = 0.5
        
        # 判断验证状态
        verification_threshold = self.traceability_state["parameters"]["verification_threshold"]
        if verification_score >= verification_threshold:
            status = "verified"
        elif verification_score >= 0.5:
            status = "partially_verified"
        else:
            status = "verification_failed"
        
        return {
            "status": status,
            "score": verification_score,
            "chain_integrity": chain_integrity,
            "cert_validity": cert_validity,
            "chain_messages": chain_messages,
            "cert_messages": cert_messages
        }
    
    def generate_qr_code_data(self, product_id: str) -> Dict:
        """生成产品QR码数据
        
        Args:
            product_id: 产品ID
            
        Returns:
            QR码数据
        """
        if product_id not in self.traceability_state["products"]:
            logger.warning(f"产品 {product_id} 不存在")
            return {"error": "产品不存在"}
        
        product = self.traceability_state["products"][product_id]
        
        # 创建QR码数据
        qr_data = {
            "product_id": product_id,
            "name": product["data"].get("name", "未命名产品"),
            "producer_id": product["producer_id"],
            "registration_time": product["registration_time"],
            "quantum_signature": product["quantum_signature"],
            "verification_url": f"https://ref.top/trace/{product_id}",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 创建QR码数据交易
        tx_data = {
            "type": "qr_code_generation",
            "product_id": product_id,
            "qr_data": qr_data
        }
        
        # 创建交易
        tx = QuantumTransaction(tx_data=tx_data, chain_ids=[self.quantum_chain.chain_id])
        
        # 添加到链
        self.quantum_chain.add_transaction(tx)
        
        logger.info(f"生成产品QR码数据: {product_id}")
        return qr_data
    
    def _generate_quantum_signature(self) -> str:
        """生成量子签名"""
        # 实际应用中会使用量子随机数生成器
        # 这里使用伪随机数简化
        random_bytes = os.urandom(16)
        signature = hashlib.sha256(random_bytes).hexdigest()
        return signature
    
    def mine_block(self) -> Dict:
        """挖掘新区块
        
        Returns:
            区块信息
        """
        # 调用量子链的挖矿方法
        block = self.quantum_chain.mine_block()
        
        logger.info(f"挖掘新区块: {block['block_id']}, 包含 {len(block['transactions'])} 笔交易")
        return block
    
    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "quantum_chain": self.quantum_chain.to_dict(),
            "main_chain_id": self.main_chain_id,
            "traceability_state": self.traceability_state
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SomTraceabilitySystem':
        """从字典恢复溯源系统"""
        traceability_system = cls(main_chain_id=data.get("main_chain_id"))
        traceability_system.quantum_chain = QuantumChain.from_dict(data["quantum_chain"])
        traceability_system.traceability_state = data["traceability_state"]
        return traceability_system
    
    def save_to_file(self, filepath: str) -> bool:
        """保存溯源系统状态到文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            是否成功保存
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
            logger.info(f"成功保存溯源系统状态到 {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存溯源系统状态失败: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'SomTraceabilitySystem':
        """从文件加载溯源系统状态
        
        Args:
            filepath: 文件路径
            
        Returns:
            溯源系统对象
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.info(f"成功从 {filepath} 加载溯源系统状态")
            return cls.from_dict(data)
        except Exception as e:
            logger.error(f"加载溯源系统状态失败: {e}")
            return None 

"""

"""
量子基因编码: QE-TRA-48B53B63A106
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
