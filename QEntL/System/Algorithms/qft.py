#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子傅里叶变换（QFT）实现
Quantum Fourier Transform

QFT是量子计算的核心算法，用于：
- 量子相位估计
- Shor算法
- 量子信号处理
"""

import numpy as np
from typing import List, Optional
import cmath


class QuantumFourierTransform:
    """量子傅里叶变换"""
    
    def __init__(self, n_qubits: int):
        """
        初始化QFT
        
        Args:
            n_qubits: 量子比特数
        """
        self.n_qubits = n_qubits
        self.n_states = 2 ** n_qubits
    
    def qft_matrix(self) -> np.ndarray:
        """
        构建QFT矩阵
        
        QFT矩阵元素：ω^jk / √N
        其中 ω = e^(2πi/N)
        """
        N = self.n_states
        omega = cmath.exp(2j * cmath.pi / N)
        
        # 构建矩阵
        matrix = np.zeros((N, N), dtype=complex)
        for j in range(N):
            for k in range(N):
                matrix[j, k] = omega ** (j * k) / np.sqrt(N)
        
        return matrix
    
    def qft_circuit_gates(self) -> List[dict]:
        """
        生成QFT量子门序列
        
        QFT电路结构：
        1. 对每个量子比特j，应用Hadamard门
        2. 对每个k > j，应用受控相位门R_k
        
        Returns:
            门序列列表
        """
        gates = []
        
        for j in range(self.n_qubits):
            # Hadamard门
            gates.append({
                "name": "H",
                "qubit": j,
                "description": f"H on qubit {j}"
            })
            
            # 受控相位门
            for k in range(j + 1, self.n_qubits):
                # 相位角度
                angle = 2 * np.pi / (2 ** (k - j + 1))
                gates.append({
                    "name": "CR",
                    "control": k,
                    "target": j,
                    "angle": angle,
                    "description": f"CR from {k} to {j} with angle {angle:.4f}"
                })
        
        # 交换量子比特（反转顺序）
        for i in range(self.n_qubits // 2):
            gates.append({
                "name": "SWAP",
                "qubit1": i,
                "qubit2": self.n_qubits - 1 - i,
                "description": f"SWAP qubits {i} and {self.n_qubits - 1 - i}"
            })
        
        return gates
    
    def apply_qft(self, state: np.ndarray) -> np.ndarray:
        """
        对量子态应用QFT
        
        Args:
            state: 输入量子态向量
            
        Returns:
            变换后的量子态
        """
        # 使用矩阵乘法
        qft_mat = self.qft_matrix()
        return qft_mat @ state
    
    def apply_inverse_qft(self, state: np.ndarray) -> np.ndarray:
        """
        应用逆QFT
        
        Args:
            state: 输入量子态向量
            
        Returns:
            逆变换后的量子态
        """
        qft_mat = self.qft_matrix()
        # 逆QFT是QFT矩阵的共轭转置
        return np.conj(qft_mat.T) @ state
    
    @staticmethod
    def phase_gate(angle: float) -> np.ndarray:
        """相位门"""
        return np.array([
            [1, 0],
            [0, cmath.exp(1j * angle)]
        ], dtype=complex)
    
    @staticmethod
    def controlled_phase(angle: float) -> np.ndarray:
        """受控相位门"""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, cmath.exp(1j * angle)]
        ], dtype=complex)


class QFTTestSuite:
    """QFT测试套件"""
    
    def __init__(self):
        self.test_results = []
    
    def test_basic_qft(self, n_qubits: int = 2):
        """测试基本QFT"""
        print(f"\n=== 测试 {n_qubits} 量子比特QFT ===")
        
        qft = QuantumFourierTransform(n_qubits)
        
        # 测试基态 |0⟩
        initial_state = np.zeros(2 ** n_qubits, dtype=complex)
        initial_state[0] = 1
        
        # 应用QFT
        transformed = qft.apply_qft(initial_state)
        
        # QFT(|0⟩) = 均匀叠加态
        expected = np.ones(2 ** n_qubits, dtype=complex) / np.sqrt(2 ** n_qubits)
        
        # 检查结果
        success = np.allclose(transformed, expected)
        
        print(f"输入: |{'0' * n_qubits}⟩")
        print(f"输出概率: {np.abs(transformed) ** 2}")
        print(f"期望概率: {np.abs(expected) ** 2}")
        print(f"测试{'通过' if success else '失败'}")
        
        self.test_results.append({
            "test": "basic_qft",
            "n_qubits": n_qubits,
            "success": success
        })
        
        return success
    
    def test_inverse_qft(self, n_qubits: int = 2):
        """测试逆QFT"""
        print(f"\n=== 测试逆QFT ===")
        
        qft = QuantumFourierTransform(n_qubits)
        
        # 创建随机量子态
        np.random.seed(42)
        state = np.random.rand(2 ** n_qubits) + 1j * np.random.rand(2 ** n_qubits)
        state = state / np.linalg.norm(state)
        
        # QFT然后逆QFT应该回到原态
        transformed = qft.apply_qft(state)
        recovered = qft.apply_inverse_qft(transformed)
        
        success = np.allclose(recovered, state)
        
        print(f"原态与恢复态距离: {np.linalg.norm(recovered - state):.6e}")
        print(f"测试{'通过' if success else '失败'}")
        
        self.test_results.append({
            "test": "inverse_qft",
            "n_qubits": n_qubits,
            "success": success
        })
        
        return success
    
    def test_qft_periodicity(self, n_qubits: int = 3):
        """测试QFT周期性"""
        print(f"\n=== 测试QFT周期检测 ===")
        
        qft = QuantumFourierTransform(n_qubits)
        N = 2 ** n_qubits
        
        # 创建周期为2的态
        state = np.zeros(N, dtype=complex)
        for i in range(0, N, 2):
            state[i] = 1
        state = state / np.linalg.norm(state)
        
        # 应用QFT
        transformed = qft.apply_qft(state)
        
        # 检查峰值位置
        probs = np.abs(transformed) ** 2
        peaks = np.where(probs > 0.1)[0]
        
        print(f"周期态概率分布: {probs}")
        print(f"峰值位置: {peaks}")
        
        # 周期为2时，峰值应该在N/2和0处
        expected_peaks = [0, N // 2]
        success = all(p in peaks for p in expected_peaks)
        
        print(f"测试{'通过' if success else '失败'}")
        
        self.test_results.append({
            "test": "periodicity",
            "n_qubits": n_qubits,
            "success": success
        })
        
        return success
    
    def test_qft_gates(self, n_qubits: int = 2):
        """测试QFT门序列生成"""
        print(f"\n=== 测试QFT门序列 ===")
        
        qft = QuantumFourierTransform(n_qubits)
        gates = qft.qft_circuit_gates()
        
        print(f"生成 {len(gates)} 个量子门:")
        for i, gate in enumerate(gates):
            print(f"  {i+1}. {gate.get('description', gate['name'])}")
        
        success = len(gates) > 0
        
        self.test_results.append({
            "test": "gate_generation",
            "n_qubits": n_qubits,
            "success": success
        })
        
        return success
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 50)
        print("QFT测试套件")
        print("=" * 50)
        
        # 运行各项测试
        self.test_basic_qft(2)
        self.test_basic_qft(3)
        self.test_inverse_qft(2)
        self.test_qft_periodicity(3)
        self.test_qft_gates(2)
        
        # 统计结果
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print("\n" + "=" * 50)
        print(f"测试结果: {passed}/{total} 通过")
        print("=" * 50)
        
        return passed == total


if __name__ == "__main__":
    # 运行测试套件
    suite = QFTTestSuite()
    all_passed = suite.run_all_tests()
    
    if all_passed:
        print("\n✅ QFT实现验证成功！")
    else:
        print("\n❌ 部分测试失败")
    
    # 演示QFT门序列
    print("\n" + "=" * 50)
    print("QFT门序列示例（3量子比特）")
    print("=" * 50)
    
    qft = QuantumFourierTransform(3)
    gates = qft.qft_circuit_gates()
    
    print(f"\n总共 {len(gates)} 个量子门:")
    for gate in gates:
        print(f"  {gate}")
