"""
QNT 跨链桥接模块
"""
import hashlib
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class BridgeStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CrossChainTicket:
    """跨链票据"""
    ticket_id: str
    source_chain: str
    target_chain: str
    amount: float
    token: str
    sender: str
    receiver: str
    status: BridgeStatus
    timestamp: float
    hash_lock: str
    secret_hash: Optional[str] = None


class CrossChainBridge:
    """跨链桥接器"""
    
    def __init__(self, chain_id: str, supported_chains: List[str]):
        self.chain_id = chain_id
        self.supported_chains = supported_chains
        self._tickets: Dict[str, CrossChainTicket] = {}
        self._locked_assets: Dict[str, float] = {}
    
    def create_ticket(self, target_chain: str, amount: float, 
                      token: str, receiver: str) -> str:
        """创建跨链票据"""
        if target_chain not in self.supported_chains:
            raise ValueError(f"Unsupported chain: {target_chain}")
        
        ticket_id = hashlib.sha256(
            f"{self.chain_id}:{target_chain}:{amount}:{token}:{receiver}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        # 生成密钥和哈希锁
        secret = hashlib.sha256(f"{ticket_id}:{time.time()}".encode()).hexdigest()
        hash_lock = hashlib.sha256(secret.encode()).hexdigest()
        
        ticket = CrossChainTicket(
            ticket_id=ticket_id,
            source_chain=self.chain_id,
            target_chain=target_chain,
            amount=amount,
            token=token,
            sender=receiver,
            receiver=receiver,
            status=BridgeStatus.PENDING,
            timestamp=time.time(),
            hash_lock=hash_lock
        )
        
        self._tickets[ticket_id] = ticket
        self._locked_assets[token] = self._locked_assets.get(token, 0) + amount
        
        return ticket_id
    
    def claim_ticket(self, ticket_id: str, secret: str) -> bool:
        """认领跨链票据"""
        if ticket_id not in self._tickets:
            return False
        
        ticket = self._tickets[ticket_id]
        
        # 验证哈希锁
        if hashlib.sha256(secret.encode()).hexdigest() != ticket.hash_lock:
            ticket.status = BridgeStatus.FAILED
            return False
        
        ticket.status = BridgeStatus.COMPLETED
        self._locked_assets[ticket.token] -= ticket.amount
        
        return True
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """获取票据状态"""
        if ticket_id not in self._tickets:
            return None
        
        ticket = self._tickets[ticket_id]
        return {
            'ticket_id': ticket.ticket_id,
            'source_chain': ticket.source_chain,
            'target_chain': ticket.target_chain,
            'amount': ticket.amount,
            'token': ticket.token,
            'sender': ticket.sender,
            'receiver': ticket.receiver,
            'status': ticket.status.value,
            'timestamp': ticket.timestamp
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取桥接统计"""
        total_locked = sum(self._locked_assets.values())
        completed = sum(1 for t in self._tickets.values() if t.status == BridgeStatus.COMPLETED)
        
        return {
            'chain_id': self.chain_id,
            'supported_chains': self.supported_chains,
            'total_tickets': len(self._tickets),
            'completed': completed,
            'total_locked': total_locked,
            'locked_assets': dict(self._locked_assets)
        }


class AtomicSwap:
    """原子交换"""
    
    @staticmethod
    def create_offer(chain_a: str, chain_b: str, 
                     amount_a: float, amount_b: float,
                     secret: str) -> Dict[str, Any]:
        """创建原子交换报价"""
        hash_a = hashlib.sha256(secret.encode()).hexdigest()
        hash_b = hashlib.sha256((secret + ":b").encode()).hexdigest()
        
        return {
            'chain_a': chain_a,
            'chain_b': chain_b,
            'amount_a': amount_a,
            'amount_b': amount_b,
            'hash_a': hash_a,
            'hash_b': hash_b,
            'status': 'pending',
            'timestamp': time.time()
        }
    
    @staticmethod
    def verify_secret(secret: str, hash_expected: str) -> bool:
        """验证密钥"""
        return hashlib.sha256(secret.encode()).hexdigest() == hash_expected


# 全局桥接器实例
bridges = {}


def get_bridge(chain_id: str) -> Optional[CrossChainBridge]:
    """获取桥接器实例"""
    return bridges.get(chain_id)


def create_bridge(chain_id: str, supported_chains: List[str]) -> CrossChainBridge:
    """创建桥接器实例"""
    bridge = CrossChainBridge(chain_id, supported_chains)
    bridges[chain_id] = bridge
    return bridge
