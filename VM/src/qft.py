#!/usr/bin/env python3
"""
量子傅里叶变换(QFT)实现
版本: v0.2.0
量子基因编码: QGC-VM-QFT-20260308

QFT是许多量子算法的核心组件，包括Shor算法
"""

import numpy as np
from typing import List

class QuantumFourierTransform:
    """量子傅里叶变换"""
    
    def __init__(self, num_qubits: int = 3):
        self.num_qubits = num_qubits
        self.num_states = 2 ** num_qubits
        self.state = self._init_state()
        
        # 基本量子门
        self.H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        
    def _init_state(self) -> np.ndarray:
        """初始化量子态"""
        state = np.zeros(2 ** self.num_qubits, dtype=complex)
        state[0] = 1.0
        return state
    
    def phase_gate(self, k: int) -> np.ndarray:
        """
        相位门 R_k
        
        R_k = |1 0|
              |0 e^(2πi/2^k)|
        """
        phase = np.exp(2j * np.pi / (2 ** k))
        return np.array([[1, 0], [0, phase]])
    
    def apply_qft(self) -> np.ndarray:
        """
        应用量子傅里叶变换
        
        QFT将计算基态|j⟩变换为叠加态:
        |j⟩ → 1/√N Σ_k e^(2πijk/N) |k⟩
        """
        print(f"\n=== QFT演示 ===")
        print(f"量子比特数: {self.num_qubits}")
        print(f"输入状态: {self._state_to_string()}")
        
        # QFT电路构建
        for i in range(self.num_qubits):
            # 应用Hadamard门
            self._apply_single_gate(self.H, i)
            
            # 应用受控相位门
            for j in range(i + 1, self.num_qubits):
                phase = self.phase_gate(j - i + 1)
                self._apply_controlled_phase(phase, j, i)
        
        # 交换量子比特顺序
        for i in range(self.num_qubits // 2):
            self._swap(i, self.num_qubits - 1 - i)
        
        print(f"输出状态: {self._state_to_string()}")
        
        return self.state
    
    def _apply_single_gate(self, gate: np.ndarray, qubit: int):
        """应用单量子比特门"""
        # 构建全算子
        full_gate = np.eye(1)
        for i in range(self.num_qubits - 1, -1, -1):
            if i == qubit:
                full_gate = np.kron(full_gate, gate)
            else:
                full_gate = np.kron(full_gate, np.eye(2))
        self.state = full_gate @ self.state
    
    def _apply_controlled_phase(self, phase: np.ndarray, control: int, target: int):
        """应用受控相位门"""
        for i in range(self.num_states):
            # 检查控制比特是否为1
            if (i >> control) & 1:
                # 应用相位到目标比特
                if (i >> target) & 1:
                    self.state[i] *= phase[1, 1]
    
    def _swap(self, qubit1: int, qubit2: int):
        """交换两个量子比特"""
        self.state = self.state.reshape([2] * self.num_qubits)
        self.state = np.swapaxes(self.state, qubit1, qubit2)
        self.state = self.state.reshape(self.num_states)
    
    def _state_to_string(self) -> str:
        """将状态向量转换为字符串表示"""
        components = []
        for i in range(self.num_states):
            if abs(self.state[i]) > 0.001:
                amplitude = self.state[i]
                components.append(f"{amplitude:.3f}|{i:0{self.num_qubits}b}⟩")
        return " + ".join(components) if components else "0"
    
    def set_state(self, state_index: int):
        """设置初始状态为特定计算基态"""
        self.state = np.zeros(self.num_states, dtype=complex)
        self.state[state_index] = 1.0
        print(f"设置初始状态: |{state_index:0{self.num_qubits}b}⟩")


def demo():
    """演示QFT"""
    qft = QuantumFourierTransform(num_qubits=3)
    
    # 设置初始状态为 |5⟩ = |101⟩
    qft.set_state(5)
    
    # 应用QFT
    result = qft.apply_qft()
    
    return result


if __name__ == "__main__":
    demo()
