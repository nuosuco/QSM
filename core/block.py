"""
QNT 区块链 - 区块数据结构
"""
import hashlib
import time
from typing import List, Optional, Dict, Any


class Block:
    """量子叠加态区块链中的单个区块"""
    
    def __init__(
        self,
        index: int,
        timestamp: float,
        transactions: List[Dict[str, Any]],
        previous_hash: str,
        nonce: int = 0,
        state_root: Optional[str] = None
    ):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions or []
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.state_root = state_root or self._calculate_state_root()
        self.hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """计算区块哈希"""
        block_string = f"{self.index}:{self.timestamp}:{self.previous_hash}:" \
                       f"{self.hash_transactions()}:{self.nonce}:{self.state_root}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def hash_transactions(self) -> str:
        """计算交易哈希（Merkle Root 简化版）"""
        if not self.transactions:
            return hashlib.sha256(b"").hexdigest()
        
        tx_strings = [f"{tx.get('sender', '')}:{tx.get('receiver', '')}:{tx.get('amount', 0)}" 
                      for tx in self.transactions]
        combined = "".join(tx_strings)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _calculate_state_root(self) -> str:
        """计算叠加态账本根哈希"""
        # 简化实现：基于交易列表计算
        if not self.transactions:
            return hashlib.sha256(b"genesis").hexdigest()
        states = [f"{tx.get('sender', '')}={tx.get('amount', 0)}" 
                  for tx in self.transactions]
        return hashlib.sha256(",".join(states).encode()).hexdigest()
    
    def mine(self, difficulty: int = 4) -> bool:
        """工作量证明挖矿"""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self._calculate_hash()
            if self.nonce % 10000 == 0:
                print(f"⛏️  Mining block {self.index}... nonce={self.nonce}")
        return True
    
    def is_valid(self, difficulty: int = 4) -> bool:
        """验证区块有效性"""
        target = "0" * difficulty
        return self.hash[:difficulty] == target
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "state_root": self.state_root,
            "hash": self.hash
        }
    
    def __repr__(self):
        return f"Block(index={self.index}, hash={self.hash[:16]}...)"


class GenesisBlock(Block):
    """创世区块"""
    
    def __init__(self):
        super().__init__(
            index=0,
            timestamp=time.time(),
            transactions=[],
            previous_hash="0" * 64,
            nonce=0,
            state_root=hashlib.sha256(b"genesis").hexdigest()
        )
        self.hash = self._calculate_hash()
    
    def __repr__(self):
        return "GenesisBlock(🌌)"
