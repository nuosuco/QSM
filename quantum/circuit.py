"""
QNT Quantum - 量子叠加态核心算法
"""
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time


@dataclass
class QuantumState:
    """量子态"""
    state_id: int
    amplitude: np.ndarray
    phase: float
    energy: float
    created_at: float = field(default_factory=time.time)
    
    @property
    def probability(self) -> np.ndarray:
        """概率幅"""
        return np.abs(self.amplitude) ** 2
    
    def collapse(self) -> int:
        """波函数坍缩"""
        probs = self.probability
        return np.random.choice(len(probs), p=probs / probs.sum())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'state_id': self.state_id,
            'amplitude_norm': float(np.linalg.norm(self.amplitude)),
            'phase': float(self.phase),
            'energy': float(self.energy),
            'collapsed_dim': int(self.collapse())
        }


class QuantumCircuit:
    """量子回路"""
    
    def __init__(self, num_qubits: int = 4):
        self.num_qubits = num_qubits
        self.gates: List[Dict[str, Any]] = []
        self.states: List[QuantumState] = []
    
    def apply_hadamard(self, qubit: int):
        """应用Hadamard门"""
        self.gates.append({'type': 'H', 'qubit': qubit})
    
    def apply_pauli_x(self, qubit: int):
        """应用Pauli-X门"""
        self.gates.append({'type': 'X', 'qubit': qubit})
    
    def apply_cnot(self, control: int, target: int):
        """应用CNOT门"""
        self.gates.append({'type': 'CNOT', 'control': control, 'target': target})
    
    def initialize_state(self, state_id: int, noise: float = 0.1) -> QuantumState:
        """初始化量子态"""
        amplitude = np.random.randn(self.num_qubits) * noise
        amplitude = amplitude / np.linalg.norm(amplitude)
        phase = np.random.uniform(0, 2 * np.pi)
        energy = np.random.uniform(0.1, 1.0)
        
        state = QuantumState(state_id, amplitude, phase, energy)
        self.states.append(state)
        return state
    
    def measure(self, state: QuantumState) -> int:
        """测量量子态"""
        return state.collapse()
    
    def get_state_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        return {
            'num_qubits': self.num_qubits,
            'num_gates': len(self.gates),
            'num_states': len(self.states),
            'gates': self.gates,
            'states': [s.to_dict() for s in self.states]
        }


class QuantumOptimizer:
    """量子优化器 - 用于N态权重优化"""
    
    def __init__(self, dim: int, learning_rate: float = 0.01):
        self.dim = dim
        self.lr = learning_rate
        self.best_weights: Optional[np.ndarray] = None
        self.best_score = -float('inf')
    
    def optimize(self, scores: List[float], weights_list: List[np.ndarray]) -> np.ndarray:
        """量子进化优化"""
        if not scores or not weights_list:
            return np.zeros(self.dim)
        
        # 选择最佳权重
        best_idx = np.argmax(scores)
        self.best_score = scores[best_idx]
        self.best_weights = weights_list[best_idx].copy()
        
        # 量子扰动生成新权重
        perturbation = np.random.randn(self.dim) * self.lr
        new_weights = self.best_weights + perturbation
        new_weights = new_weights / (np.linalg.norm(new_weights) + 1e-10)
        
        return new_weights
    
    def get_best(self) -> Optional[np.ndarray]:
        return self.best_weights.copy() if self.best_weights is not None else None
