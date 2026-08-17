"""
QNT Trainer - N态训练管理器
"""
import time
import numpy as np
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from nstate.pool import SuperpositionPool


@dataclass
class TrainingConfig:
    """训练配置"""
    num_states: int = 8
    weight_dim: int = 10
    learning_rate: float = 0.001
    batch_size: int = 32
    max_rounds: int = 10000
    collapse_interval: int = 100
    min_improvement: float = 1e-6


@dataclass
class TrainingStats:
    """训练统计"""
    rounds: int = 0
    best_score: float = 0.0
    avg_loss: float = 0.0
    convergence_round: int = 0
    collapses: int = 0
    elapsed_seconds: float = 0.0


class TrainingManager:
    """训练管理器"""
    
    def __init__(self, config: Optional[TrainingConfig] = None):
        self.config = config or TrainingConfig()
        self.pool: Optional[SuperpositionPool] = None
        self.stats = TrainingStats()
        self._loss_history: List[float] = []
        self._score_history: List[float] = []
        self._start_time: float = 0.0
    
    def initialize(self, num_states: Optional[int] = None, weight_dim: Optional[int] = None):
        """初始化训练池"""
        n = num_states or self.config.num_states
        d = weight_dim or self.config.weight_dim
        self.pool = SuperpositionPool(num_states=n, weight_dim=d)
        self.stats = TrainingStats()
    
    def train_step(self, input_data: np.ndarray, target: float) -> float:
        """训练单步"""
        if self.pool is None:
            raise RuntimeError("Pool not initialized")
        
        loss = self.pool.train_step(input_data, target)
        self._loss_history.append(loss)
        self.stats.rounds += 1
        
        # 定期坍缩
        if self.stats.rounds % self.config.collapse_interval == 0 and self.stats.rounds > 0:
            collapses = self.pool.collapse()
            self.stats.collapses += len(collapses)
        
        return loss
    
    def train_batch(self, inputs: np.ndarray, targets: np.ndarray) -> float:
        """批量训练"""
        total_loss = 0.0
        for i in range(min(len(inputs), self.config.batch_size)):
            loss = self.train_step(inputs[i], targets[i])
            total_loss += loss
        return total_loss / max(len(inputs), 1)
    
    def train_loop(self, 
                   data_fn: Callable[[int], tuple],
                   max_rounds: Optional[int] = None) -> TrainingStats:
        """训练循环"""
        self._start_time = time.time()
        self.stats.convergence_round = 0
        
        rounds = max_rounds or self.config.max_rounds
        
        for i in range(rounds):
            input_data, target = data_fn(i)
            loss = self.train_step(input_data, target)
            
            # 检查收敛
            if len(self._loss_history) >= 10:
                recent = [l for l in self._loss_history[-10:] if l is not None]
                if recent and max(recent) - min(recent) < self.config.min_improvement:
                    self.stats.convergence_round = i + 1
                    break
            
            # 进度打印
            if (i + 1) % 100 == 0:
                avg_loss = np.mean(self._loss_history[-10:])
                print(f"  Round {i+1}/{rounds}, Loss: {avg_loss:.6f}, Collapses: {self.stats.collapses}")
        
        self.stats.elapsed_seconds = time.time() - self._start_time
        valid_losses = [l for l in self._loss_history if l is not None and not np.isnan(l) and not np.isinf(l)]
        self.stats.avg_loss = np.mean(valid_losses) if valid_losses else 0.0
        
        return self.stats
    
    def get_best_weights(self) -> Optional[np.ndarray]:
        """获取最佳权重（坍缩后）"""
        if self.pool is None:
            return None
        return self.pool.get_best_weights()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'rounds': self.stats.rounds,
            'collapses': self.stats.collapses,
            'avg_loss': self.stats.avg_loss,
            'convergence_round': self.stats.convergence_round,
            'elapsed_seconds': self.stats.elapsed_seconds,
            'loss_history_length': len(self._loss_history)
        }
    
    def reset(self):
        """重置训练"""
        self.pool = None
        self.stats = TrainingStats()
        self._loss_history = []
        self._score_history = []
