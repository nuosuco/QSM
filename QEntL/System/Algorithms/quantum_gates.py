#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM完整量子门库
Comprehensive Quantum Gate Library

包含所有常用量子门和自定义门构建器
"""

import numpy as np
from typing import List, Tuple, Optional, Union
import cmath


class QuantumGates:
    """量子门库"""
    
    # ==================== 单量子比特门 ====================
    
    @staticmethod
    def I() -> np.ndarray:
        """恒等门 I"""
        return np.array([[1, 0], [0, 1]], dtype=complex)
    
    @staticmethod
    def X() -> np.ndarray:
        """Pauli-X门（NOT门）"""
        return np.array([[0, 1], [1, 0]], dtype=complex)
    
    @staticmethod
    def Y() -> np.ndarray:
        """Pauli-Y门"""
        return np.array([[0, -1j], [1j, 0]], dtype=complex)
    
    @staticmethod
    def Z() -> np.ndarray:
        """Pauli-Z门"""
        return np.array([[1, 0], [0, -1]], dtype=complex)
    
    @staticmethod
    def H() -> np.ndarray:
        """Hadamard门"""
        return np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    
    @staticmethod
    def S() -> np.ndarray:
        """相位门 S（√Z）"""
        return np.array([[1, 0], [0, 1j]], dtype=complex)
    
    @staticmethod
    def S_dagger() -> np.ndarray:
        """S†门"""
        return np.array([[1, 0], [0, -1j]], dtype=complex)
    
    @staticmethod
    def T() -> np.ndarray:
        """T门（π/8门）"""
        return np.array([[1, 0], [0, cmath.exp(1j * np.pi / 4)]], dtype=complex)
    
    @staticmethod
    def T_dagger() -> np.ndarray:
        """T†门"""
        return np.array([[1, 0], [0, cmath.exp(-1j * np.pi / 4)]], dtype=complex)
    
    # ==================== 旋转门 ====================
    
    @staticmethod
    def RX(theta: float) -> np.ndarray:
        """
        绕X轴旋转门
        
        Args:
            theta: 旋转角度（弧度）
        """
        return np.array([
            [np.cos(theta / 2), -1j * np.sin(theta / 2)],
            [-1j * np.sin(theta / 2), np.cos(theta / 2)]
        ], dtype=complex)
    
    @staticmethod
    def RY(theta: float) -> np.ndarray:
        """
        绕Y轴旋转门
        
        Args:
            theta: 旋转角度（弧度）
        """
        return np.array([
            [np.cos(theta / 2), -np.sin(theta / 2)],
            [np.sin(theta / 2), np.cos(theta / 2)]
        ], dtype=complex)
    
    @staticmethod
    def RZ(theta: float) -> np.ndarray:
        """
        绕Z轴旋转门
        
        Args:
            theta: 旋转角度（弧度）
        """
        return np.array([
            [cmath.exp(-1j * theta / 2), 0],
            [0, cmath.exp(1j * theta / 2)]
        ], dtype=complex)
    
    @staticmethod
    def U(theta: float, phi: float, lambda_: float) -> np.ndarray:
        """
        通用单量子比特门 U(θ, φ, λ)
        
        U = RZ(φ) · RY(θ) · RZ(λ)
        
        Args:
            theta: Y旋转角度
            phi: 第一个Z旋转角度
            lambda_: 第二个Z旋转角度
        """
        return np.array([
            [np.cos(theta / 2), -cmath.exp(1j * lambda_) * np.sin(theta / 2)],
            [cmath.exp(1j * phi) * np.sin(theta / 2), cmath.exp(1j * (phi + lambda_)) * np.cos(theta / 2)]
        ], dtype=complex)
    
    # ==================== 双量子比特门 ====================
    
    @staticmethod
    def CNOT() -> np.ndarray:
        """受控NOT门（CX）"""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
    
    @staticmethod
    def CZ() -> np.ndarray:
        """受控Z门"""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, -1]
        ], dtype=complex)
    
    @staticmethod
    def CY() -> np.ndarray:
        """受控Y门"""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, -1j],
            [0, 0, 1j, 0]
        ], dtype=complex)
    
    @staticmethod
    def SWAP() -> np.ndarray:
        """SWAP门"""
        return np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ], dtype=complex)
    
    @staticmethod
    def ISWAP() -> np.ndarray:
        """iSWAP门"""
        return np.array([
            [1, 0, 0, 0],
            [0, 0, 1j, 0],
            [0, 1j, 0, 0],
            [0, 0, 0, 1]
        ], dtype=complex)
    
    @staticmethod
    def CRX(theta: float) -> np.ndarray:
        """受控RX门"""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, np.cos(theta / 2), -1j * np.sin(theta / 2)],
            [0, 0, -1j * np.sin(theta / 2), np.cos(theta / 2)]
        ], dtype=complex)
    
    @staticmethod
    def CRY(theta: float) -> np.ndarray:
        """受控RY门"""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, np.cos(theta / 2), -np.sin(theta / 2)],
            [0, 0, np.sin(theta / 2), np.cos(theta / 2)]
        ], dtype=complex)
    
    @staticmethod
    def CRZ(theta: float) -> np.ndarray:
        """受控RZ门"""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, cmath.exp(-1j * theta / 2), 0],
            [0, 0, 0, cmath.exp(1j * theta / 2)]
        ], dtype=complex)
    
    @staticmethod
    def CP(theta: float) -> np.ndarray:
        """受控相位门"""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, cmath.exp(1j * theta)]
        ], dtype=complex)
    
    # ==================== 三量子比特门 ====================
    
    @staticmethod
    def Toffoli() -> np.ndarray:
        """Toffoli门（CCX）"""
        # 8x8矩阵
        T = np.eye(8, dtype=complex)
        T[6, 6] = 0
        T[7, 7] = 0
        T[6, 7] = 1
        T[7, 6] = 1
        return T
    
    @staticmethod
    def Fredkin() -> np.ndarray:
        """Fredkin门（CSWAP）"""
        # 8x8矩阵
        F = np.eye(8, dtype=complex)
        # 当控制位为1时，交换后两个量子比特
        F[5, 5] = 0
        F[6, 6] = 0
        F[5, 6] = 1
        F[6, 5] = 1
        return F
    
    # ==================== 辅助函数 ====================
    
    @staticmethod
    def tensor_product(*gates: np.ndarray) -> np.ndarray:
        """
        计算多个门的张量积
        
        Args:
            *gates: 量子门列表
            
        Returns:
            张量积结果
        """
        result = gates[0]
        for gate in gates[1:]:
            result = np.kron(result, gate)
        return result
    
    @staticmethod
    def controlled_gate(gate: np.ndarray, n_controls: int = 1) -> np.ndarray:
        """
        创建受控门
        
        Args:
            gate: 单量子比特门
            n_controls: 控制量子比特数
            
        Returns:
            受控门矩阵
        """
        dim = 2 ** (n_controls + 1)
        C = np.eye(dim, dtype=complex)
        
        # 目标门作用在最后一个量子比特
        target_start = dim - 2
        target_end = dim
        
        # 将门的元素放入正确的位置
        C[target_start:target_end, target_start:target_end] = gate
        
        return C
    
    @staticmethod
    def power_gate(gate: np.ndarray, power: float) -> np.ndarray:
        """
        计算门的幂次
        
        Args:
            gate: 量子门
            power: 幂次
            
        Returns:
            门^power
        """
        # 使用矩阵对角化
        eigenvalues, eigenvectors = np.linalg.eig(gate)
        powered_eigenvalues = eigenvalues ** power
        return eigenvectors @ np.diag(powered_eigenvalues) @ np.linalg.inv(eigenvectors)


class QuantumGateTest:
    """量子门测试"""
    
    def __init__(self):
        self.gates = QuantumGates()
        self.test_results = []
    
    def test_unitarity(self):
        """测试幺正性"""
        print("\n=== 测试幺正性 ===")
        
        single_gates = [
            ('I', self.gates.I()),
            ('X', self.gates.X()),
            ('Y', self.gates.Y()),
            ('Z', self.gates.Z()),
            ('H', self.gates.H()),
            ('S', self.gates.S()),
            ('T', self.gates.T()),
        ]
        
        all_passed = True
        for name, gate in single_gates:
            # U†U = I
            is_unitary = np.allclose(gate.conj().T @ gate, np.eye(gate.shape[0]))
            print(f"  {name}: {'✓' if is_unitary else '✗'}")
            all_passed = all_passed and is_unitary
        
        self.test_results.append({"test": "unitarity", "success": all_passed})
        return all_passed
    
    def test_commutation(self):
        """测试对易关系"""
        print("\n=== 测试对易关系 ===")
        
        # [X, Y] = 2iZ
        comm_XY = self.gates.X() @ self.gates.Y() - self.gates.Y() @ self.gates.X()
        expected_comm = 2j * self.gates.Z()
        
        success1 = np.allclose(comm_XY, expected_comm)
        print(f"  [X, Y] = 2iZ: {'✓' if success1 else '✗'}")
        
        # [X, Z] = -2iY
        comm_XZ = self.gates.X() @ self.gates.Z() - self.gates.Z() @ self.gates.X()
        expected_comm = -2j * self.gates.Y()
        
        success2 = np.allclose(comm_XZ, expected_comm)
        print(f"  [X, Z] = -2iY: {'✓' if success2 else '✗'}")
        
        self.test_results.append({"test": "commutation", "success": success1 and success2})
        return success1 and success2
    
    def test_squares(self):
        """测试平方关系"""
        print("\n=== 测试平方关系 ===")
        
        tests = [
            ('X² = I', self.gates.X() @ self.gates.X(), self.gates.I()),
            ('Y² = I', self.gates.Y() @ self.gates.Y(), self.gates.I()),
            ('Z² = I', self.gates.Z() @ self.gates.Z(), self.gates.I()),
            ('H² = I', self.gates.H() @ self.gates.H(), self.gates.I()),
            ('S² = Z', self.gates.S() @ self.gates.S(), self.gates.Z()),
        ]
        
        all_passed = True
        for name, result, expected in tests:
            passed = np.allclose(result, expected)
            print(f"  {name}: {'✓' if passed else '✗'}")
            all_passed = all_passed and passed
        
        self.test_results.append({"test": "squares", "success": all_passed})
        return all_passed
    
    def test_rotations(self):
        """测试旋转门"""
        print("\n=== 测试旋转门 ===")
        
        # RX(π) = X
        rx_pi = self.gates.RX(np.pi)
        success1 = np.allclose(1j * rx_pi, self.gates.X())
        print(f"  RX(π) ∝ X: {'✓' if success1 else '✗'}")
        
        # RY(π) = Y
        ry_pi = self.gates.RY(np.pi)
        success2 = np.allclose(1j * ry_pi, self.gates.Y())
        print(f"  RY(π) ∝ Y: {'✓' if success2 else '✗'}")
        
        # RZ(π) = Z
        rz_pi = self.gates.RZ(np.pi)
        success3 = np.allclose(1j * rz_pi, self.gates.Z())
        print(f"  RZ(π) ∝ Z: {'✓' if success3 else '✗'}")
        
        self.test_results.append({"test": "rotations", "success": success1 and success2 and success3})
        return success1 and success2 and success3
    
    def test_two_qubit_gates(self):
        """测试双量子比特门"""
        print("\n=== 测试双量子比特门 ===")
        
        # CNOT² = I
        cnot_sq = self.gates.CNOT() @ self.gates.CNOT()
        success1 = np.allclose(cnot_sq, np.eye(4))
        print(f"  CNOT² = I: {'✓' if success1 else '✗'}")
        
        # SWAP² = I
        swap_sq = self.gates.SWAP() @ self.gates.SWAP()
        success2 = np.allclose(swap_sq, np.eye(4))
        print(f"  SWAP² = I: {'✓' if success2 else '✗'}")
        
        self.test_results.append({"test": "two_qubit", "success": success1 and success2})
        return success1 and success2
    
    def test_three_qubit_gates(self):
        """测试三量子比特门"""
        print("\n=== 测试三量子比特门 ===")
        
        # Toffoli² = I
        toffoli_sq = self.gates.Toffoli() @ self.gates.Toffoli()
        success1 = np.allclose(toffoli_sq, np.eye(8))
        print(f"  Toffoli² = I: {'✓' if success1 else '✗'}")
        
        # Fredkin² = I
        fredkin_sq = self.gates.Fredkin() @ self.gates.Fredkin()
        success2 = np.allclose(fredkin_sq, np.eye(8))
        print(f"  Fredkin² = I: {'✓' if success2 else '✗'}")
        
        self.test_results.append({"test": "three_qubit", "success": success1 and success2})
        return success1 and success2
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 50)
        print("量子门库测试")
        print("=" * 50)
        
        self.test_unitarity()
        self.test_commutation()
        self.test_squares()
        self.test_rotations()
        self.test_two_qubit_gates()
        self.test_three_qubit_gates()
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print("\n" + "=" * 50)
        print(f"测试结果: {passed}/{total} 通过")
        print("=" * 50)
        
        return passed == total


if __name__ == "__main__":
    suite = QuantumGateTest()
    all_passed = suite.run_all_tests()
    
    if all_passed:
        print("\n✅ 量子门库验证成功！")
    else:
        print("\n❌ 部分测试失败")
    
    # 演示门的使用
    print("\n" + "=" * 50)
    print("量子门库使用示例")
    print("=" * 50)
    
    gates = QuantumGates()
    
    print("\n基本门:")
    print(f"  H = \n{gates.H()}")
    print(f"  X = \n{gates.X()}")
    
    print("\n旋转门:")
    print(f"  RX(π/4) = \n{gates.RX(np.pi/4)}")
    
    print("\n双量子比特门:")
    print(f"  CNOT = \n{gates.CNOT()}")
    
    print("\n三量子比特门:")
    print(f"  Toffoli shape: {gates.Toffoli().shape}")
