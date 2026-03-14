#!/usr/bin/env python3
"""
Grover量子搜索算法实现
版本: v0.2.0
量子基因编码: QGC-VM-GROVER-20260308

Grover算法是量子搜索算法，可以在无序数据库中以O(√N)的复杂度找到目标项
"""

import numpy as np
from typing import List, Callable

class GroverSearch:
    """Grover搜索算法"""
    
    def __init__(self, num_qubits: int = 3):
        self.num_qubits = num_qubits
        self.num_states = 2 ** num_qubits
        self.state = self._init_state()
        
    def _init_state(self) -> np.ndarray:
        """初始化均匀叠加态"""
        state = np.ones(2 ** self.num_qubits) / np.sqrt(2 ** self.num_qubits)
        return state
    
    def oracle(self, target: int) -> np.ndarray:
        """
        Oracle函数：标记目标状态
        将目标状态的相位翻转
        """
        oracle_matrix = np.eye(self.num_states)
        oracle_matrix[target, target] = -1
        return oracle_matrix
    
    def diffusion(self) -> np.ndarray:
        """
        扩散算子（Grover算子）
        D = 2|s⟩⟨s| - I, 其中|s⟩是均匀叠加态
        """
        s = np.ones(self.num_states) / np.sqrt(self.num_states)
        diffusion_matrix = 2 * np.outer(s, s) - np.eye(self.num_states)
        return diffusion_matrix
    
    def search(self, target: int, iterations: int = None) -> int:
        """
        执行Grover搜索
        
        Args:
            target: 目标状态的索引
            iterations: 迭代次数（默认为最优次数）
        
        Returns:
            测量结果
        """
        if iterations is None:
            # 最优迭代次数 ≈ π/4 * √N
            iterations = int(np.pi / 4 * np.sqrt(self.num_states))
        
        print(f"\n=== Grover搜索演示 ===")
        print(f"量子比特数: {self.num_qubits}")
        print(f"搜索空间大小: {self.num_states}")
        print(f"目标状态: |{target:0{self.num_qubits}b}⟩")
        print(f"迭代次数: {iterations}")
        
        # 重置状态
        self.state = self._init_state()
        
        # Grover迭代
        for i in range(iterations):
            # 应用Oracle
            self.state = self.oracle(target) @ self.state
            
            # 应用扩散算子
            self.state = self.diffusion() @ self.state
            
            # 计算目标状态的概率
            prob = abs(self.state[target]) ** 2
            print(f"  迭代 {i+1}: 目标概率 = {prob:.4f}")
        
        # 测量
        probabilities = np.abs(self.state) ** 2
        result = np.random.choice(self.num_states, p=probabilities)
        
        print(f"\n测量结果: |{result:0{self.num_qubits}b}⟩")
        print(f"搜索{'成功' if result == target else '失败'}！")
        
        return result
    
    def get_probabilities(self) -> np.ndarray:
        """获取所有状态的概率分布"""
        return np.abs(self.state) ** 2


def demo():
    """演示Grover搜索"""
    # 3量子比特系统，搜索空间8个状态
    grover = GroverSearch(num_qubits=3)
    
    # 搜索目标状态 |101⟩ (二进制) = 5 (十进制)
    target = 5
    result = grover.search(target)
    
    return result


if __name__ == "__main__":
    demo()
