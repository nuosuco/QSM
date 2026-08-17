"""
QNT N态并行训练 - 叠加态Agent
"""
import random
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time


@dataclass
class StateAgent:
    """单个叠加态Agent"""
    state_id: int
    weights: np.ndarray
    learning_rate: float = 0.001
    memory: List[Dict[str, Any]] = field(default_factory=list)
    
    def predict(self, input_data: np.ndarray) -> float:
        """预测"""
        if len(input_data) != len(self.weights):
            input_data = np.resize(input_data, len(self.weights))
        return float(np.dot(self.weights, input_data))
    
    def update(self, input_data: np.ndarray, target: float):
        """更新权重（梯度下降）"""
        prediction = self.predict(input_data)
        error = target - prediction
        gradient = error * input_data
        self.weights += self.learning_rate * gradient
        
        # 记录记忆
        self.memory.append({
            "input": input_data.tolist(),
            "target": target,
            "prediction": prediction,
            "error": error,
            "timestamp": time.time()
        })
        
        # 限制记忆大小
        if len(self.memory) > 1000:
            self.memory = self.memory[-500:]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "weights": self.weights.tolist(),
            "learning_rate": self.learning_rate,
            "memory_size": len(self.memory),
            "last_error": self.memory[-1]["error"] if self.memory else 0.0
        }
    
    @classmethod
    def random_init(cls, state_id: int, weight_dim: int = 10) -> 'StateAgent':
        """随机初始化"""
        weights = np.random.randn(weight_dim) * 0.1
        return cls(state_id=state_id, weights=weights)


class SuperpositionPool:
    """N态并行训练池"""
    
    def __init__(self, num_states: int = 8, weight_dim: int = 10):
        self.num_states = num_states
        self.weight_dim = weight_dim
        self.agents: List[StateAgent] = []
        self.training_rounds = 0
        self.collapses: List[Dict[str, Any]] = []
        
        # 创建N态
        for i in range(num_states):
            agent = StateAgent.random_init(i, weight_dim)
            # 每个态略有不同的初始权重
            agent.weights += np.random.randn(weight_dim) * 0.05
            self.agents.append(agent)
        
        print(f"🔬 Created {num_states} superposition states")
    
    def train_step(self, input_data: np.ndarray, target: float):
        """各态独立训练一步"""
        for agent in self.agents:
            agent.update(input_data, target)
        
        self.training_rounds += 1
    
    def train_batch(self, inputs: np.ndarray, targets: np.ndarray):
        """批量训练"""
        for i in range(len(targets)):
            self.train_step(inputs[i], targets[i])
    
    def collapse(self) -> Dict[str, Any]:
        """观测坍缩 - 合并所有态"""
        if len(self.agents) < 2:
            return {"status": "not_enough_states"}
        
        # 计算各态表现
        performances = []
        for agent in self.agents:
            if agent.memory:
                avg_error = np.mean([abs(m["error"]) for m in agent.memory[-100:]])
                performances.append((agent, avg_error))
        
        # 按表现排序
        performances.sort(key=lambda x: x[1])
        
        # 加权合并：表现好的权重更大
        total_perf = sum(1.0 / (p[1] + 1e-10) for p in performances)
        merged_weights = np.zeros(self.weight_dim)
        
        for agent, error in performances:
            weight = (1.0 / (error + 1e-10)) / total_perf
            merged_weights += agent.weights * weight
        
        collapse_result = {
            "round": self.training_rounds,
            "states_merged": len(self.agents),
            "best_agent": performances[0][0].state_id,
            "best_error": performances[0][1],
            "merged_weights": merged_weights.tolist(),
            "diversity": self._calculate_diversity()
        }
        
        self.collapses.append(collapse_result)
        
        # 重新初始化各态（基于坍缩结果，但引入新变异）
        self._reinitialize_from_collapse(merged_weights)
        
        print(f"🔭 Collapse #{len(self.collapses)}: merged {len(self.agents)} states, "
              f"best error={collapse_result['best_error']:.6f}")
        
        return collapse_result
    
    def _reinitialize_from_collapse(self, merged_weights: np.ndarray):
        """基于坍缩结果重新初始化"""
        diversity = 0.3
        for i, agent in enumerate(self.agents):
            # 每个态围绕坍缩结果做不同方向的变异
            noise = np.random.randn(self.weight_dim) * diversity
            agent.weights = merged_weights + noise
            agent.weights += np.random.randn(self.weight_dim) * 0.01  # 额外随机
            agent.memory.clear()  # 清空记忆
    
    def _calculate_diversity(self) -> float:
        """计算态多样性"""
        if len(self.agents) < 2:
            return 0.0
        weights_matrix = np.array([a.weights for a in self.agents])
        # 平均 pairwise 距离
        distances = []
        for i in range(len(weights_matrix)):
            for j in range(i+1, len(weights_matrix)):
                dist = np.linalg.norm(weights_matrix[i] - weights_matrix[j])
                distances.append(dist)
        return np.mean(distances) if distances else 0.0
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "num_states": self.num_states,
            "training_rounds": self.training_rounds,
            "collapses": len(self.collapses),
            "diversity": self._calculate_diversity(),
            "agents": [a.to_dict() for a in self.agents]
        }
    
    def __repr__(self):
        return f"SuperpositionPool(states={self.num_states}, rounds={self.training_rounds})"


# 便捷函数
def create_pool(num_states: int = 8, weight_dim: int = 10) -> SuperpositionPool:
    return SuperpositionPool(num_states=num_states, weight_dim=weight_dim)
