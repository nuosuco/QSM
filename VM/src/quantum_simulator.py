#!/usr/bin/env python3
"""
QEntL量子模拟器
版本: v0.2.0
量子基因编码: QGC-VM-QUANTUM-SIM-20260308

实现8量子比特的量子计算模拟
"""

import numpy as np
from typing import List, Tuple

class QuantumSimulator:
    """量子计算模拟器"""
    
    def __init__(self, num_qubits: int = 8):
        self.num_qubits = num_qubits
        self.state = self._init_state()
        
        # 量子门定义
        self.gates = {
            'I': np.eye(2),  # 恒等门
            'X': np.array([[0, 1], [1, 0]]),  # Pauli-X门
            'Y': np.array([[0, -1j], [1j, 0]]),  # Pauli-Y门
            'Z': np.array([[1, 0], [0, -1]]),  # Pauli-Z门
            'H': np.array([[1, 1], [1, -1]]) / np.sqrt(2),  # Hadamard门
            'S': np.array([[1, 0], [0, 1j]]),  # S门
            'T': np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]]),  # T门
        }
        
        print(f"⚛️ 量子模拟器初始化完成")
        print(f"   量子比特数: {num_qubits}")
        print(f"   状态空间: {2**num_qubits} 维")
    
    def _init_state(self) -> np.ndarray:
        """初始化量子态为 |0...0⟩"""
        state = np.zeros(2 ** self.num_qubits, dtype=complex)
        state[0] = 1.0
        return state
    
    def apply_gate(self, gate_name: str, qubit: int):
        """应用单量子比特门"""
        if gate_name not in self.gates:
            raise ValueError(f"未知量子门: {gate_name}")
        
        gate = self.gates[gate_name]
        
        # 构建全门的张量积
        full_gate = np.eye(1)
        for i in range(self.num_qubits - 1, -1, -1):
            if i == qubit:
                full_gate = np.kron(full_gate, gate)
            else:
                full_gate = np.kron(full_gate, np.eye(2))
        
        self.state = full_gate @ self.state
    
    def apply_cnot(self, control: int, target: int):
        """应用CNOT门"""
        # CNOT门的实现：控制为1时翻转目标比特
        new_state = self.state.copy()
        for i in range(2 ** self.num_qubits):
            if (i >> control) & 1:
                j = i ^ (1 << target)
                new_state[i] = self.state[j]
                new_state[j] = self.state[i]
        self.state = new_state
    
    def measure(self, qubit: int) -> int:
        """测量指定量子比特"""
        # 计算测量概率
        prob_0 = 0.0
        prob_1 = 0.0
        
        for i in range(2 ** self.num_qubits):
            if (i >> qubit) & 1:
                prob_1 += abs(self.state[i]) ** 2
            else:
                prob_0 += abs(self.state[i]) ** 2
        
        # 随机测量
        result = 1 if np.random.random() < prob_1 else 0
        
        # 坍缩波函数
        for i in range(2 ** self.num_qubits):
            if ((i >> qubit) & 1) != result:
                self.state[i] = 0.0
        
        # 归一化
        self.state = self.state / np.linalg.norm(self.state)
        
        return result
    
    def get_probabilities(self) -> np.ndarray:
        """获取所有基态的概率"""
        return np.abs(self.state) ** 2
    
    def get_state_vector(self) -> np.ndarray:
        """获取状态向量"""
        return self.state
    
    def reset(self):
        """重置量子态"""
        self.state = self._init_state()
        print("🔄 量子态已重置为 |0...0⟩")


def demo():
    """演示量子计算"""
    print("\n=== 量子模拟器演示 ===\n")
    
    # 创建3量子比特系统
    sim = QuantumSimulator(num_qubits=3)
    
    # 演示Hadamard门
    print("\n1. 应用Hadamard门到第0个量子比特:")
    sim.apply_gate('H', 0)
    probs = sim.get_probabilities()
    for i, p in enumerate(probs):
        if p > 0.001:
            print(f"   |{i:03b}⟩: {p:.4f}")
    
    # 演示CNOT门
    print("\n2. 应用CNOT门(控制=0, 目标=1):")
    sim.apply_cnot(0, 1)
    probs = sim.get_probabilities()
    for i, p in enumerate(probs):
        if p > 0.001:
            print(f"   |{i:03b}⟩: {p:.4f}")
    
    # 演示测量
    print("\n3. 测量所有量子比特:")
    results = [sim.measure(i) for i in range(3)]
    print(f"   测量结果: |{results[0]}{results[1]}{results[2]}⟩")
    
    print("\n=== 演示完成 ===\n")


if __name__ == "__main__":
    demo()
