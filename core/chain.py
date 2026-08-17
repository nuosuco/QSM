"""
QNT 区块链 - 链式结构
"""
import time
from typing import List, Optional, Dict, Any
from .block import Block, GenesisBlock


class QNTChain:
    """量子叠加态区块链"""
    
    def __init__(self, difficulty: int = 4):
        self.difficulty = difficulty
        self.chain: List[Block] = [GenesisBlock()]
        self.pending_transactions: List[Dict[str, Any]] = []
        self.state_ledger: Dict[str, float] = {"system": 1_000_000.0}  # QNT代币总量
        self.superposition_states: List[Dict[str, Any]] = []  # 叠加态记录
        self.collapses: List[Dict[str, Any]] = []  # 坍缩记录
    
    @property
    def last_block(self) -> Block:
        """获取最新区块"""
        return self.chain[-1]
    
    def add_transaction(self, sender: str, receiver: str, amount: float) -> bool:
        """添加待处理交易"""
        if amount <= 0:
            return False
        if sender not in self.state_ledger or self.state_ledger[sender] < amount:
            return False
        
        tx = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "timestamp": time.time(),
            "id": f"{sender}:{amount}:{time.time()}"
        }
        self.pending_transactions.append(tx)
        print(f"📝 Transaction added: {sender} -> {receiver} ({amount} QNT)")
        return True
    
    def mine_pending_transactions(self) -> Optional[int]:
        """挖矿并打包待处理交易"""
        if not self.pending_transactions:
            return None
        
        previous_hash = self.last_block.hash
        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions.copy(),
            previous_hash=previous_hash
        )
        
        print(f"⛏️  Mining block {block.index}...")
        block.mine(self.difficulty)
        
        # 更新账本
        for tx in block.transactions:
            self.state_ledger[tx["sender"]] -= tx["amount"]
            receiver = tx["receiver"]
            self.state_ledger[receiver] = self.state_ledger.get(receiver, 0) + tx["amount"]
        
        self.chain.append(block)
        
        # 记录叠加态
        self._record_superposition(block)
        
        # 清空待处理
        self.pending_transactions.clear()
        
        print(f"✅ Block {block.index} mined! Hash: {block.hash[:32]}...")
        return block.index
    
    def _record_superposition(self, block: Block):
        """记录叠加态（简化实现）"""
        state = {
            "block_index": block.index,
            "state_root": block.state_root,
            "timestamp": time.time(),
            "ledger_snapshot": self.state_ledger.copy()
        }
        self.superposition_states.append(state)
        
        # 保留最近100个状态
        if len(self.superposition_states) > 100:
            self.superposition_states = self.superposition_states[-100:]
    
    def collapse_observation(self) -> Dict[str, Any]:
        """观测坍缩 - 合并所有叠加态为一个确定状态"""
        if len(self.superposition_states) < 2:
            return {"status": "no_states_to_collapse"}
        
        # 简化坍缩：取最新状态
        latest = self.superposition_states[-1]
        collapse = {
            "timestamp": time.time(),
            "states_merged": len(self.superposition_states),
            "resulting_state": latest["state_root"],
            "ledger_after_collapse": latest["ledger_snapshot"].copy()
        }
        
        self.collapses.append(collapse)
        self.superposition_states.clear()
        
        print(f"🔭 Observation collapse! Merged {collapse['states_merged']} states")
        return collapse
    
    def is_valid(self) -> bool:
        """验证整个链的有效性"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # 验证链接
            if current.previous_hash != previous.hash:
                print(f"❌ Invalid link at block {i}")
                return False
            
            # 验证工作量证明
            if not current.is_valid(self.difficulty):
                print(f"❌ Invalid proof at block {i}")
                return False
        
        return True
    
    def get_balance(self, address: str) -> float:
        """查询地址余额"""
        return self.state_ledger.get(address, 0.0)
    
    def get_chain_info(self) -> Dict[str, Any]:
        """获取链信息"""
        return {
            "height": len(self.chain),
            "latest_hash": self.last_block.hash,
            "pending_transactions": len(self.pending_transactions),
            "total_supply": sum(self.state_ledger.values()),
            "superposition_states": len(self.superposition_states),
            "collapses": len(self.collapses),
            "addresses": len(self.state_ledger)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化整条链"""
        return {
            "chain": [block.to_dict() for block in self.chain],
            "state_ledger": self.state_ledger,
            "superposition_states": self.superposition_states,
            "collapses": self.collapses
        }
    
    def __repr__(self):
        return f"QNTChain(height={len(self.chain)}, states={len(self.superposition_states)})"


# 便捷函数
def create_genesis_chain(difficulty: int = 4) -> QNTChain:
    """创建创世链"""
    return QNTChain(difficulty=difficulty)
