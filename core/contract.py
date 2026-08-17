"""
QNT 智能合约基础框架
"""
import hashlib
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ContractType(Enum):
    TOKEN = "token"
    DEFI = "defi"
    GOVERNANCE = "governance"
    NSTATE = "nstate"


@dataclass
class ContractCall:
    """合约调用记录"""
    caller: str
    contract_id: str
    method: str
    args: List[Any] = field(default_factory=list)
    timestamp: float = 0.0
    tx_hash: str = ""
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            import time
            self.timestamp = time.time()
    
    def compute_hash(self) -> str:
        data = f"{self.caller}:{self.contract_id}:{self.method}:{json.dumps(self.args)}:{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()


class SmartContract:
    """智能合约基类"""
    
    def __init__(self, contract_id: str, creator: str, contract_type: ContractType):
        self.contract_id = contract_id
        self.creator = creator
        self.contract_type = contract_type
        self.state: Dict[str, Any] = {}
        self.history: List[ContractCall] = []
        self.created_at: float = __import__('time').time()
    
    def call(self, caller: str, method: str, *args) -> Dict[str, Any]:
        """调用合约方法"""
        call = ContractCall(
            caller=caller,
            contract_id=self.contract_id,
            method=method,
            args=list(args),
            timestamp=__import__('time').time()
        )
        call.tx_hash = call.compute_hash()
        self.history.append(call)
        
        # 路由到具体方法
        if hasattr(self, method):
            result = getattr(self, method)(caller, *args)
            return {"success": True, "result": result, "tx_hash": call.tx_hash}
        else:
            return {"success": False, "error": f"Method {method} not found", "tx_hash": call.tx_hash}
    
    def get_state(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "type": self.contract_type.value,
            "creator": self.creator,
            "state": self.state.copy(),
            "call_count": len(self.history),
            "created_at": self.created_at
        }


class QNTToken(SmartContract):
    """QNT代币合约"""
    
    def __init__(self, total_supply: float = 1_000_000.0):
        super().__init__("QNT-Token", "system", ContractType.TOKEN)
        self.state["total_supply"] = total_supply
        self.state["balances"] = {"system": total_supply}
        self.state["allowances"] = {}
    
    def transfer(self, caller: str, to: str, amount: float) -> bool:
        """转账"""
        if caller not in self.state["balances"]:
            self.state["balances"][caller] = 0.0
        if to not in self.state["balances"]:
            self.state["balances"][to] = 0.0
        
        if self.state["balances"][caller] < amount:
            return False
        
        self.state["balances"][caller] -= amount
        self.state["balances"][to] += amount
        return True
    
    def mint(self, to: str, amount: float) -> bool:
        """铸造"""
        if self.state.get("total_supply", 0) + amount > self.state["total_supply"]:
            return False
        self.state["balances"][to] = self.state["balances"].get(to, 0) + amount
        return True
    
    def balance_of(self, address: str) -> float:
        """查询余额"""
        return self.state["balances"].get(address, 0.0)


class QNTGovernance(SmartContract):
    """治理合约"""
    
    def __init__(self, voting_delay: int = 1, voting_period: int = 100):
        super().__init__("QNT-Governance", "system", ContractType.GOVERNANCE)
        self.state["proposals"] = []
        self.state["voting_delay"] = voting_delay
        self.state["voting_period"] = voting_period
        self.state["quorum"] = 0.4
    
    def propose(self, caller: str, description: str, targets: List[str]) -> int:
        """创建提案"""
        proposal_id = len(self.state["proposals"])
        proposal = {
            "id": proposal_id,
            "proposer": caller,
            "description": description,
            "targets": targets,
            "votes_for": 0,
            "votes_against": 0,
            "created_at": __import__('time').time()
        }
        self.state["proposals"].append(proposal)
        return proposal_id
    
    def vote(self, caller: str, proposal_id: int, support: bool) -> bool:
        """投票"""
        if proposal_id >= len(self.state["proposals"]):
            return False
        
        proposal = self.state["proposals"][proposal_id]
        balance = caller  # 简化：用地址代表权重
        
        if support:
            proposal["votes_for"] += balance
        else:
            proposal["votes_against"] += balance
        
        return True


class NStateContract(SmartContract):
    """N态训练合约"""
    
    def __init__(self, num_states: int = 8):
        super().__init__("QNT-NState", "system", ContractType.NSTATE)
        self.state["num_states"] = num_states
        self.state["states"] = []
        self.state["collapses"] = []
    
    def add_state(self, state_id: int, weights: List[float]) -> bool:
        """添加叠加态"""
        state = {
            "id": state_id,
            "weights": weights,
            "created_at": __import__('time').time()
        }
        self.state["states"].append(state)
        return True
    
    def collapse(self) -> Dict[str, Any]:
        """观测坍缩"""
        if len(self.state["states"]) < 2:
            return {"error": "not enough states"}
        
        # 加权平均合并
        total_weight = sum(len(s["weights"]) for s in self.state["states"])
        merged = [0.0] * len(self.state["states"][0]["weights"])
        
        for state in self.state["states"]:
            w = len(state["weights"]) / total_weight
            for i in range(len(merged)):
                merged[i] += state["weights"][i] * w
        
        collapse_record = {
            "timestamp": __import__('time').time(),
            "states_merged": len(self.state["states"]),
            "merged_weights": merged
        }
        self.state["collapses"].append(collapse_record)
        self.state["states"] = []  # 清空
        
        return collapse_record
