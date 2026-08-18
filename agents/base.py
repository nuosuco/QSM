"""
QNT Agent 基类
"""
import time
import uuid
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class AgentStatus(Enum):
    IDLE = "idle"
    TRAINING = "training"
    TRADING = "trading"
    OBSERVING = "observing"
    COLLAPSING = "collapsing"


@dataclass
class AgentMemory:
    """Agent记忆"""
    experiences: List[Dict[str, Any]] = field(default_factory=list)
    max_capacity: int = 1000
    
    def add(self, experience: Dict[str, Any]):
        self.experiences.append(experience)
        if len(self.experiences) > self.max_capacity:
            self.experiences = self.experiences[-self.max_capacity//2:]
    
    def recall(self, k: int = 10) -> List[Dict[str, Any]]:
        return self.experiences[-k:]


class AgentBase:
    """Agent基类"""
    
    def __init__(self, agent_id: str = None, name: str = "", role: str = "general"):
        self.agent_id = agent_id or str(uuid.uuid4())[:8]
        self.name = name or f"Agent-{self.agent_id}"
        self.role = role
        self.status = AgentStatus.IDLE
        self.memory = AgentMemory()
        self.created_at = time.time()
        self.actions_taken = 0
        self.success_rate = 0.0
    
    def think(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """思考 - 根据观察生成决策"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "observation": observation,
            "decision": self._decide(observation),
            "confidence": 0.5,
            "timestamp": time.time()
        }
    
    def _decide(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """具体决策逻辑（子类重写）"""
        return {"action": "hold", "reason": "default"}
    
    def learn(self, experience: Dict[str, Any]):
        """学习 - 从经验中更新"""
        self.memory.add(experience)
        self._update_from_experience(experience)
    
    def _update_from_experience(self, experience: Dict[str, Any]):
        """根据经验更新内部状态"""
        action = experience.get("action", "")
        success = experience.get("success", False)
        
        if success:
            self.actions_taken += 1
            self.success_rate = min(1.0, self.success_rate + 0.05)  # 小幅提升成功率
        else:
            self.success_rate = max(0.0, self.success_rate - 0.1)  # 失败时降低
        
        # 根据action类型调整阈值
        if action == "arbitrage":
            if hasattr(self, 'spread_threshold'):
                self.spread_threshold = max(0.01, self.spread_threshold - 0.005 if success else self.spread_threshold + 0.005)
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "status": self.status.value,
            "memory_size": len(self.memory.experiences),
            "actions_taken": self.actions_taken,
            "success_rate": self.success_rate,
            "created_at": self.created_at
        }
    
    def __repr__(self):
        return f"Agent({self.name}, role={self.role})"


class ArbAgent(AgentBase):
    """价差套利Agent"""
    
    def __init__(self, **kwargs):
        super().__init__(role="arb", **kwargs)
        self.spread_threshold = 0.05  # 5bp
    
    def _decide(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        spread_pct = observation.get("spread_pct", 0)
        if spread_pct > self.spread_threshold:
            return {"action": "arbitrage", "spread": spread_pct, "direction": "long_short"}
        return {"action": "hold"}


class MarketMakerAgent(AgentBase):
    """做市Agent"""
    
    def __init__(self, **kwargs):
        super().__init__(role="market_maker", **kwargs)
        self.spread = 0.1  # 10bp
    
    def _decide(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        mid = observation.get("mid_price", 0)
        if mid > 0:
            return {
                "action": "post_orders",
                "bid": mid * (1 - self.spread/200),
                "ask": mid * (1 + self.spread/200),
                "size": observation.get("order_size", 100)
            }
        return {"action": "hold"}


class TrendAgent(AgentBase):
    """趋势跟踪Agent"""
    
    def __init__(self, lookback: int = 20, **kwargs):
        super().__init__(role="trend", **kwargs)
        self.lookback = lookback
        self.prices: List[float] = []
    
    def _decide(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        price = observation.get("price", 0)
        if price > 0:
            self.prices.append(price)
            if len(self.prices) > self.lookback:
                self.prices = self.prices[-self.lookback:]
            
            if len(self.prices) >= 5:
                trend = sum(self.prices[i] - self.prices[i-1] 
                           for i in range(1, len(self.prices))) / len(self.prices)
                if trend > 0.001:
                    return {"action": "long", "trend": trend}
                elif trend < -0.001:
                    return {"action": "short", "trend": trend}
        return {"action": "hold"}


def create_agent(agent_type: str = "general", **kwargs) -> AgentBase:
    """工厂函数创建Agent"""
    agents = {
        "arb": ArbAgent,
        "market_maker": MarketMakerAgent,
        "trend": TrendAgent,
        "general": AgentBase
    }
    cls = agents.get(agent_type, AgentBase)
    return cls(**kwargs)
