import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互模式
import matplotlib.pyplot as plt
from typing import List, Dict, Any
import json
import os

class QuantumVisualizer:
    def __init__(self):
        # 设置暗色主题
        plt.style.use('dark_background')
    
    def visualize_quantum_state(self, quantum_state: np.ndarray, title: str = "量子态可视化") -> None:
        """可视化量子态"""
        plt.figure(figsize=(10, 6))
        
        # 绘制量子态
        plt.subplot(2, 1, 1)
        plt.plot(quantum_state, 'o-', color='#8B5CF6')
        plt.title(title)
        plt.ylabel('振幅')
        plt.grid(True, alpha=0.3)
        
        # 绘制能量波动
        plt.subplot(2, 1, 2)
        energy = np.abs(quantum_state)**2
        plt.plot(energy, 'o-', color='#3B82F6')
        plt.title('能量分布')
        plt.ylabel('概率')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
    
    def save_visualization(self, filename: str = "quantum_state.png") -> str:
        """保存可视化结果"""
        plt.savefig(filename)
        plt.close()
        return filename
    
    def generate_html(self, quantum_state: np.ndarray, progress: float = 0.0) -> str:
        """生成HTML显示"""
        return f"""
        <div class="quantum-visualization">
            <div class="quantum-state">
                <h3>量子态信息</h3>
                <pre>{json.dumps(quantum_state.tolist(), indent=2)}</pre>
            </div>
            <div class="quantum-progress">
                <div class="progress-bar">
                    <div class="progress" style="width: {progress*100}%"></div>
                </div>
                <span class="progress-text">{progress*100:.1f}%</span>
            </div>
        </div>
        """ 

"""
"""
量子基因编码: QE-QUA-6E9BD4BABD90
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
