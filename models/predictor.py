"""
QNT 预测模型
"""
import numpy as np
import torch
import torch.nn as nn
from typing import List, Dict, Any, Optional
try:
    from ..nstate.pool import SuperpositionPool
except ImportError:
    from nstate.pool import SuperpositionPool


class MarketPredictor(nn.Module):
    """市场预测模型 - 轻量Transformer"""
    
    def __init__(self, input_dim: int = 10, hidden_dim: int = 64, 
                 output_dim: int = 1, num_heads: int = 4, num_layers: int = 2):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim, nhead=num_heads, dim_feedforward=hidden_dim*2,
            dropout=0.1, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        self.output_layer = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, output_dim)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.input_proj(x)
        x = self.transformer(x)
        return self.output_layer(x[:, -1, :])  # 取最后一步输出


class NStatePredictor:
    """N态叠加态预测器 - 基于中华的N态训练方法"""
    
    def __init__(self, input_dim: int = 10, num_states: int = 8, 
                 hidden_dim: int = 64, collapse_interval: int = 10):
        self.input_dim = input_dim
        self.num_states = num_states
        self.collapse_interval = collapse_interval
        
        # N态并行池
        self.pool = SuperpositionPool(num_states=num_states, weight_dim=input_dim)
        
        # 可选：每个态配备独立神经网络
        self.networks = [
            MarketPredictor(input_dim, hidden_dim) 
            for _ in range(num_states)
        ]
        
        self.training_history: List[Dict[str, Any]] = []
        self.current_epoch = 0
    
    def train_step(self, inputs: np.ndarray, targets: np.ndarray):
        """N态并行训练一步"""
        # 1. 各态独立训练
        self.pool.train_step(inputs, float(targets[0]))
        
        # 2. 各态神经网络训练
        for i, net in enumerate(self.networks):
            net.train()
            optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
            inp = torch.FloatTensor(inputs).unsqueeze(0)
            tgt = torch.FloatTensor([targets[0]])
            
            pred = net(inp)
            loss = nn.MSELoss()(pred, tgt)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        self.current_epoch += 1
        
        # 3. 定期坍缩
        if self.current_epoch % self.collapse_interval == 0:
            collapse_result = self.pool.collapse()
            self._apply_collapse(collapse_result)
        
        # 记录历史
        self.training_history.append({
            "epoch": self.current_epoch,
            "pool_status": self.pool.get_status()
        })
    
    def _apply_collapse(self, collapse_result: Dict[str, Any]):
        """将坍缩结果应用到网络"""
        merged_weights = np.array(collapse_result.get("merged_weights", []))
        if len(merged_weights) == self.input_dim:
            # 所有网络向坍缩结果靠拢
            for net in self.networks:
                for param in net.parameters():
                    param.data += torch.FloatTensor(merged_weights) * 0.01
    
    def predict(self, inputs: np.ndarray) -> Dict[str, Any]:
        """N态集成预测 - 投票机制"""
        self.pool.collapse()  # 先坍缩
        
        predictions = []
        for net in self.networks:
            net.eval()
            with torch.no_grad():
                inp = torch.FloatTensor(inputs).unsqueeze(0)
                pred = net(inp).item()
                predictions.append(pred)
        
        # 集成：加权平均（基于多样性）
        avg_pred = np.mean(predictions)
        std_pred = np.std(predictions)
        
        return {
            "prediction": avg_pred,
            "confidence": 1.0 / (1.0 + std_pred),
            "diversity": std_pred,
            "individual_predictions": predictions,
            "num_states": len(predictions)
        }
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "num_states": self.num_states,
            "current_epoch": self.current_epoch,
            "pool": self.pool.get_status(),
            "networks": len(self.networks)
        }


# 便捷函数
def create_predictor(input_dim: int = 10, num_states: int = 8) -> NStatePredictor:
    return NStatePredictor(input_dim=input_dim, num_states=num_states)
