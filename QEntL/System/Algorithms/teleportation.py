#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子隐形传态实现
Quantum Teleportation

量子隐形传态允许将量子态从一个位置"传送"到另一个位置，
利用量子纠缠和经典通信实现。
"""

import numpy as np
from typing import Tuple
import random


class QuantumTeleportation:
    """量子隐形传态"""
    
    def __init__(self):
        """初始化量子隐形传态系统"""
        # 量子门定义
        self.H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        self.X = np.array([[0, 1], [1, 0]])
        self.Z = np.array([[1, 0], [0, -1]])
        self.CNOT = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ])
    
    def create_bell_pair(self) -> np.ndarray:
        """
        创建Bell态 |Φ+⟩ = (|00⟩ + |11⟩) / √2
        
        Returns:
            Bell态向量
        """
        # 从 |00⟩ 开始
        state = np.array([1, 0, 0, 0], dtype=complex)
        
        # 在第一个量子比特上应用Hadamard门
        H_2q = np.kron(self.H, np.eye(2))
        state = H_2q @ state
        
        # 应用CNOT门
        state = self.CNOT @ state
        
        return state
    
    def prepare_state(self, alpha: complex, beta: complex) -> np.ndarray:
        """
        准备要传送的量子态 |ψ⟩ = α|0⟩ + β|1⟩
        
        Args:
            alpha: |0⟩ 振幅
            beta: |1⟩ 振幅
            
        Returns:
            单量子比特态向量
        """
        # 归一化
        norm = np.sqrt(abs(alpha)**2 + abs(beta)**2)
        alpha = alpha / norm
        beta = beta / norm
        
        return np.array([alpha, beta], dtype=complex)
    
    def teleport(self, psi: np.ndarray) -> Tuple[int, int, np.ndarray]:
        """
        执行量子隐形传态
        
        Args:
            psi: 要传送的量子态 |ψ⟩ = α|0⟩ + β|1⟩
            
        Returns:
            (测量结果1, 测量结果2, 恢复的量子态)
        """
        # 步骤1：创建Bell对
        bell_pair = self.create_bell_pair()
        
        # 步骤2：Alice拥有量子比特0（要传送的态）和量子比特1（Bell对的一半）
        # Bob拥有量子比特2（Bell对的另一半）
        
        # 初始三量子比特态：|ψ⟩₀ ⊗ |Φ+⟩₁₂
        # |ψ⟩₀ = α|0⟩ + β|1⟩
        # |Φ+⟩₁₂ = (|00⟩ + |11⟩)/√2
        
        # 构建初始态
        state = np.zeros(8, dtype=complex)
        for i in range(2):
            for j in range(4):
                state[i * 4 + j] = psi[i] * bell_pair[j]
        
        # 步骤3：Alice对量子比特0和1应用CNOT（以0为控制）
        CNOT_01 = np.zeros((8, 8), dtype=complex)
        for i in range(8):
            # 如果量子比特0是|1⟩，翻转量子比特1
            if (i // 4) % 2 == 1:
                CNOT_01[i, i ^ 2] = 1  # 翻转量子比特1
            else:
                CNOT_01[i, i] = 1
        
        state = CNOT_01 @ state
        
        # 步骤4：Alice对量子比特0应用Hadamard门
        H_0 = np.kron(self.H, np.eye(4))
        state = H_0 @ state
        
        # 步骤5：Alice测量量子比特0和1
        # 计算测量概率
        probs = np.abs(state) ** 2
        
        # 模拟测量
        measurement = random.choices(range(8), weights=probs)[0]
        m1 = (measurement // 4) % 2  # 量子比特0的测量结果
        m2 = (measurement // 2) % 2  # 量子比特1的测量结果
        
        # Bob的量子比特（量子比特2）现在处于与测量结果相关的态
        # Bob需要根据测量结果应用修正
        
        # 提取Bob的量子比特态
        bob_state = np.zeros(2, dtype=complex)
        for i in range(2):
            idx = m1 * 4 + m2 * 2 + i
            bob_state[i] = state[idx]
        
        # 归一化
        norm = np.linalg.norm(bob_state)
        if norm > 0:
            bob_state = bob_state / norm
        
        # 步骤6：Bob根据测量结果应用修正
        if m2 == 1:
            bob_state = self.X @ bob_state
        if m1 == 1:
            bob_state = self.Z @ bob_state
        
        return m1, m2, bob_state
    
    def verify_teleportation(self, original: np.ndarray, received: np.ndarray) -> float:
        """
        验证传态是否成功
        
        Args:
            original: 原始量子态
            received: 接收到的量子态
            
        Returns:
            保真度（越接近1越好）
        """
        # 计算保真度 F = |⟨ψ_original|ψ_received⟩|²
        fidelity = abs(np.vdot(original, received)) ** 2
        return fidelity


class TeleportationTest:
    """量子隐形传态测试"""
    
    def __init__(self):
        self.teleport = QuantumTeleportation()
        self.test_results = []
    
    def test_bell_pair_creation(self):
        """测试Bell对创建"""
        print("\n=== 测试Bell对创建 ===")
        
        bell = self.teleport.create_bell_pair()
        
        # |Φ+⟩ = (|00⟩ + |11⟩) / √2
        expected = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)
        
        success = np.allclose(bell, expected)
        print(f"Bell态: {bell}")
        print(f"期望: {expected}")
        print(f"测试{'通过' if success else '失败'}")
        
        self.test_results.append({"test": "bell_pair", "success": success})
        return success
    
    def test_state_preparation(self):
        """测试态准备"""
        print("\n=== 测试态准备 ===")
        
        # 测试 |0⟩
        psi = self.teleport.prepare_state(1, 0)
        expected = np.array([1, 0], dtype=complex)
        success1 = np.allclose(psi, expected)
        
        # 测试 |+⟩ = (|0⟩ + |1⟩) / √2
        psi = self.teleport.prepare_state(1, 1)
        expected = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
        success2 = np.allclose(psi, expected)
        
        print(f"|0⟩: {success1}")
        print(f"|+⟩: {success2}")
        
        success = success1 and success2
        self.test_results.append({"test": "state_preparation", "success": success})
        return success
    
    def test_teleportation(self):
        """测试完整传态过程"""
        print("\n=== 测试量子隐形传态 ===")
        
        # 测试多个随机态
        fidelities = []
        
        for i in range(10):
            # 随机态
            theta = random.random() * np.pi
            phi = random.random() * 2 * np.pi
            alpha = np.cos(theta / 2)
            beta = np.sin(theta / 2) * np.exp(1j * phi)
            
            original = self.teleport.prepare_state(alpha, beta)
            m1, m2, received = self.teleport.teleport(original)
            
            fidelity = self.teleport.verify_teleportation(original, received)
            fidelities.append(fidelity)
            
            print(f"  试验 {i+1}: m1={m1}, m2={m2}, 保真度={fidelity:.4f}")
        
        avg_fidelity = np.mean(fidelities)
        success = avg_fidelity > 0.95
        
        print(f"\n平均保真度: {avg_fidelity:.4f}")
        print(f"测试{'通过' if success else '失败'}")
        
        self.test_results.append({"test": "teleportation", "success": success})
        return success
    
    def test_specific_states(self):
        """测试特定态的传态"""
        print("\n=== 测试特定态传态 ===")
        
        test_states = [
            ("|0⟩", 1, 0),
            ("|1⟩", 0, 1),
            ("|+⟩", 1, 1),
            ("|-⟩", 1, -1),
        ]
        
        all_success = True
        for name, a, b in test_states:
            original = self.teleport.prepare_state(a, b)
            m1, m2, received = self.teleport.teleport(original)
            fidelity = self.teleport.verify_teleportation(original, received)
            
            success = fidelity > 0.95
            all_success = all_success and success
            print(f"  {name}: 保真度={fidelity:.4f} {'✓' if success else '✗'}")
        
        self.test_results.append({"test": "specific_states", "success": all_success})
        return all_success
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 50)
        print("量子隐形传态测试套件")
        print("=" * 50)
        
        self.test_bell_pair_creation()
        self.test_state_preparation()
        self.test_teleportation()
        self.test_specific_states()
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print("\n" + "=" * 50)
        print(f"测试结果: {passed}/{total} 通过")
        print("=" * 50)
        
        return passed == total


if __name__ == "__main__":
    # 运行测试
    suite = TeleportationTest()
    all_passed = suite.run_all_tests()
    
    if all_passed:
        print("\n✅ 量子隐形传态验证成功！")
    else:
        print("\n❌ 部分测试失败")
    
    # 演示
    print("\n" + "=" * 50)
    print("量子隐形传态演示")
    print("=" * 50)
    
    teleport = QuantumTeleportation()
    
    # 传送 |+⟩ 态
    print("\n传送 |+⟩ = (|0⟩ + |1⟩)/√2:")
    original = teleport.prepare_state(1, 1)
    m1, m2, received = teleport.teleport(original)
    fidelity = teleport.verify_teleportation(original, received)
    
    print(f"原始态: {original}")
    print(f"测量结果: m1={m1}, m2={m2}")
    print(f"接收态: {received}")
    print(f"保真度: {fidelity:.4f}")
