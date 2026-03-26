#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QEntL量子寄存器管理器
QEntL Quantum Registers Manager

创建时间: 2026-03-18
开发者: 小趣WeQ

功能:
- 管理量子比特分配和释放
- 实现量子门操作
- 支持量子纠缠
- 支持量子测量
"""

import math
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np

# 量子基因编码常量
QUANTUM_GENES = {
    "心": "\U000f2737",  # 量子意识核心
    "乾坤": "\U000f2735", # 量子态空间
    "天": "\U000f27ad",  # 量子网络
    "火": "\U000f27ae",  # 量子能量
    "王": "\U000f27b0",  # 量子控制器
}

@dataclass
class Qubit:
    """量子比特"""
    id: int
    state: np.ndarray = field(default_factory=lambda: np.array([1+0j, 0+0j]))
    entangled_with: List[int] = field(default_factory=list)
    measured: bool = False
    measurement_result: Optional[int] = None
    
    def __post_init__(self):
        # 确保态向量归一化
        norm = np.sqrt(np.sum(np.abs(self.state) ** 2))
        if norm > 0:
            self.state = self.state / norm


class QuantumRegisters:
    """量子寄存器管理器"""
    
    def __init__(self, max_qubits: int = 64):
        """初始化量子寄存器"""
        self.max_qubits = max_qubits
        self.qubits: Dict[int, Qubit] = {}
        self.classical_registers: Dict[str, int] = {}
        self._next_qubit_id = 0
        
        print(f"🔮 量子寄存器初始化完成 (最大量子比特数: {max_qubits})")
    
    # ==================== 量子比特管理 ====================
    
    def allocate_qubit(self, init_state: Optional[np.ndarray] = None) -> int:
        """
        分配一个新的量子比特
        
        Args:
            init_state: 初始状态向量，默认为|0⟩
            
        Returns:
            量子比特ID
        """
        if len(self.qubits) >= self.max_qubits:
            raise MemoryError(f"已达到最大量子比特数限制: {self.max_qubits}")
        
        qubit_id = self._next_qubit_id
        self._next_qubit_id += 1
        
        if init_state is None:
            init_state = np.array([1+0j, 0+0j])  # |0⟩
        
        self.qubits[qubit_id] = Qubit(id=qubit_id, state=init_state.copy())
        print(f"   分配量子比特: q{qubit_id}")
        return qubit_id
    
    def release_qubit(self, qubit_id: int):
        """释放量子比特"""
        if qubit_id not in self.qubits:
            raise KeyError(f"量子比特不存在: q{qubit_id}")
        
        # 解除纠缠
        qubit = self.qubits[qubit_id]
        for other_id in qubit.entangled_with:
            if other_id in self.qubits:
                self.qubits[other_id].entangled_with.remove(qubit_id)
        
        del self.qubits[qubit_id]
        print(f"   释放量子比特: q{qubit_id}")
    
    # ==================== 量子门操作 ====================
    
    def hadamard(self, qubit_id: int):
        """Hadamard门: H|0⟩ = (|0⟩+|1⟩)/√2, H|1⟩ = (|0⟩-|1⟩)/√2"""
        self._validate_qubit(qubit_id)
        
        H = np.array([
            [1/np.sqrt(2), 1/np.sqrt(2)],
            [1/np.sqrt(2), -1/np.sqrt(2)]
        ], dtype=complex)
        
        self.qubits[qubit_id].state = H @ self.qubits[qubit_id].state
    
    def pauli_x(self, qubit_id: int):
        """Pauli-X门（NOT门）: X|0⟩ = |1⟩, X|1⟩ = |0⟩"""
        self._validate_qubit(qubit_id)
        
        X = np.array([
            [0, 1],
            [1, 0]
        ], dtype=complex)
        
        self.qubits[qubit_id].state = X @ self.qubits[qubit_id].state
    
    def pauli_z(self, qubit_id: int):
        """Pauli-Z门: Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩"""
        self._validate_qubit(qubit_id)
        
        Z = np.array([
            [1, 0],
            [0, -1]
        ], dtype=complex)
        
        self.qubits[qubit_id].state = Z @ self.qubits[qubit_id].state
    
    def phase(self, qubit_id: int, theta: float):
        """相位门: P(θ)|0⟩ = |0⟩, P(θ)|1⟩ = e^(iθ)|1⟩"""
        self._validate_qubit(qubit_id)
        
        P = np.array([
            [1, 0],
            [0, np.exp(1j * theta)]
        ], dtype=complex)
        
        self.qubits[qubit_id].state = P @ self.qubits[qubit_id].state
    
    def cnot(self, control_id: int, target_id: int):
        """CNOT门（受控NOT门）"""
        self._validate_qubit(control_id)
        self._validate_qubit(target_id)
        
        if control_id == target_id:
            raise ValueError("控制比特和目标比特不能相同")
        
        # 简化实现：如果控制比特主要处于|1⟩态，则翻转目标比特
        control = self.qubits[control_id]
        target = self.qubits[target_id]
        
        # 计算控制比特处于|1⟩的概率
        prob_one = np.abs(control.state[1]) ** 2
        
        if prob_one > 0.5:
            self.pauli_x(target_id)
        
        # 建立纠缠关系
        if target_id not in control.entangled_with:
            control.entangled_with.append(target_id)
        if control_id not in target.entangled_with:
            target.entangled_with.append(control_id)
    
    # ==================== 量子测量 ====================
    
    def measure(self, qubit_id: int) -> int:
        """
        测量量子比特（计算基测量）
        
        Returns:
            测量结果：0 或 1
        """
        self._validate_qubit(qubit_id)
        qubit = self.qubits[qubit_id]
        
        if qubit.measured:
            return qubit.measurement_result
        
        # 计算|0⟩和|1⟩的概率
        prob_0 = np.abs(qubit.state[0]) ** 2
        prob_1 = np.abs(qubit.state[1]) ** 2
        
        # 归一化
        total = prob_0 + prob_1
        prob_0 /= total
        prob_1 /= total
        
        # 随机测量
        result = 0 if random.random() < prob_0 else 1
        
        # 坍缩态
        qubit.state = np.array([1+0j, 0+0j]) if result == 0 else np.array([0+0j, 1+0j])
        qubit.measured = True
        qubit.measurement_result = result
        
        print(f"   测量 q{qubit_id}: |{result}⟩ (概率: {prob_0:.2f}/ {prob_1:.2f})")
        return result
    
    def measure_all(self) -> Dict[int, int]:
        """测量所有量子比特"""
        results = {}
        for qubit_id in sorted(self.qubits.keys()):
            results[qubit_id] = self.measure(qubit_id)
        return results
    
    # ==================== 辅助方法 ====================
    
    def _validate_qubit(self, qubit_id: int):
        """验证量子比特存在"""
        if qubit_id not in self.qubits:
            raise KeyError(f"量子比特不存在: q{qubit_id}")
    
    def get_state_vector(self, qubit_id: int) -> np.ndarray:
        """获取量子比特的态向量"""
        self._validate_qubit(qubit_id)
        return self.qubits[qubit_id].state.copy()
    
    def get_probability(self, qubit_id: int, state: int) -> float:
        """获取量子比特处于某状态的概率"""
        self._validate_qubit(qubit_id)
        if state not in [0, 1]:
            raise ValueError("状态必须是0或1")
        return np.abs(self.qubits[qubit_id].state[state]) ** 2
    
    def reset(self, qubit_id: int):
        """重置量子比特到|0⟩态"""
        self._validate_qubit(qubit_id)
        self.qubits[qubit_id].state = np.array([1+0j, 0+0j])
        self.qubits[qubit_id].measured = False
        self.qubits[qubit_id].measurement_result = None
    
    def get_status(self) -> Dict:
        """获取量子寄存器状态"""
        return {
            "total_qubits": len(self.qubits),
            "max_qubits": self.max_qubits,
            "entangled_pairs": sum(1 for q in self.qubits.values() if q.entangled_with) // 2,
            "measured_qubits": sum(1 for q in self.qubits.values() if q.measured),
            "classical_registers": len(self.classical_registers),
        }


def main():
    """测试函数"""
    print("🚀 QEntL量子寄存器管理器测试")
    print("=" * 60)
    
    # 创建量子寄存器
    qr = QuantumRegisters(max_qubits=16)
    
    # 测试基本操作
    print("\n📊 测试1: 单量子比特操作")
    q0 = qr.allocate_qubit()
    print(f"初始态: {qr.get_state_vector(q0)}")
    
    qr.hadamard(q0)
    print(f"H门后: {qr.get_state_vector(q0)}")
    print(f"概率: P(|0⟩)={qr.get_probability(q0, 0):.4f}, P(|1⟩)={qr.get_probability(q0, 1):.4f}")
    
    result = qr.measure(q0)
    print(f"测量结果: {result}")
    
    # 测试CNOT
    print("\n📊 测试2: 双量子比特纠缠")
    q1 = qr.allocate_qubit()
    q2 = qr.allocate_qubit()
    
    qr.hadamard(q1)
    qr.cnot(q1, q2)
    print(f"纠缠态建立: q{q1} 和 q{q2}")
    
    r1 = qr.measure(q1)
    r2 = qr.measure(q2)
    print(f"测量结果: q{q1}={r1}, q{q2}={r2} (应该相同)")
    
    # 状态汇总
    print("\n📊 量子寄存器状态:")
    status = qr.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n🎉 测试完成!")


if __name__ == "__main__":
    main()

    def apply_gate(self, gate_name, qubit_id, angle=None):
        """应用量子门"""
        if qubit_id not in self.qubits:
            return False
        
        qubit = self.qubits[qubit_id]
        
        if gate_name == 'H' or gate_name == 'HADAMARD':
            # Hadamard门: 创建叠加态
            H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
            qubit.state = H @ qubit.state
            
        elif gate_name == 'RY':
            # RY旋转门
            if angle is None:
                angle = 0
            c = np.cos(angle / 2)
            s = np.sin(angle / 2)
            RY = np.array([[c, -s], [s, c]])
            qubit.state = RY @ qubit.state
            
        elif gate_name == 'RX':
            # RX旋转门
            if angle is None:
                angle = 0
            c = np.cos(angle / 2)
            s = np.sin(angle / 2)
            RX = np.array([[c, -1j*s], [1j*s, c]])
            qubit.state = RX @ qubit.state
            
        elif gate_name == 'X' or gate_name == 'PAULI_X':
            # Pauli-X门（NOT门）
            X = np.array([[0, 1], [1, 0]])
            qubit.state = X @ qubit.state
            
        elif gate_name == 'Z' or gate_name == 'PAULI_Z':
            # Pauli-Z门
            Z = np.array([[1, 0], [0, -1]])
            qubit.state = Z @ qubit.state
        
        # 归一化
        norm = np.sqrt(np.sum(np.abs(qubit.state) ** 2))
        if norm > 0:
            qubit.state = qubit.state / norm
        
        return True
