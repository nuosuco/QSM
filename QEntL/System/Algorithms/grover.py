#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grover搜索算法完整实现
Grover's Search Algorithm

Grover算法是量子搜索算法，可以在无序数据库中以O(√N)复杂度找到目标项。
经典算法需要O(N)复杂度。
"""

import numpy as np
from typing import List, Tuple, Optional, Callable
import math


class GroverSearch:
    """Grover搜索算法"""
    
    def __init__(self, n_qubits: int):
        """
        初始化Grover搜索
        
        Args:
            n_qubits: 数据库量子比特数（数据库大小为2^n_qubits）
        """
        self.n_qubits = n_qubits
        self.n_states = 2 ** n_qubits
        self._init_gates()
    
    def _init_gates(self):
        """初始化量子门"""
        self.H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        self.X = np.array([[0, 1], [1, 0]], dtype=complex)
        self.Z = np.array([[1, 0], [0, -1]], dtype=complex)
    
    def hadamard_all(self) -> np.ndarray:
        """生成所有量子比特的Hadamard变换"""
        H_n = np.eye(1, dtype=complex)
        for _ in range(self.n_qubits):
            H_n = np.kron(H_n, self.H)
        return H_n
    
    def oracle(self, target: int) -> np.ndarray:
        """
        构建Oracle算子
        
        Oracle将目标态的相位翻转：|x⟩ → (-1)^f(x)|x⟩
        其中f(x) = 1当且仅当x = target
        
        Args:
            target: 目标索引
            
        Returns:
            Oracle矩阵
        """
        oracle_matrix = np.eye(self.n_states, dtype=complex)
        oracle_matrix[target, target] = -1
        return oracle_matrix
    
    def diffuser(self) -> np.ndarray:
        """
        构建扩散算子（Grover扩散算子）
        
        D = 2|s⟩⟨s| - I
        其中|s⟩是均匀叠加态
        
        Returns:
            扩散矩阵
        """
        # |s⟩ = H|0⟩，均匀叠加态
        H_n = self.hadamard_all()
        zero_state = np.zeros(self.n_states, dtype=complex)
        zero_state[0] = 1
        
        s = H_n @ zero_state
        
        # D = 2|s⟩⟨s| - I
        D = 2 * np.outer(s, s.conj()) - np.eye(self.n_states, dtype=complex)
        
        return D
    
    def optimal_iterations(self) -> int:
        """
        计算最优迭代次数
        
        Returns:
            最优迭代次数
        """
        # 最优迭代次数约为 π√N / 4
        return int(np.round(np.pi * np.sqrt(self.n_states) / 4))
    
    def search(self, target: int, iterations: Optional[int] = None) -> Tuple[np.ndarray, float]:
        """
        执行Grover搜索
        
        Args:
            target: 目标索引
            iterations: 迭代次数（None则使用最优值）
            
        Returns:
            (最终态, 目标态概率)
        """
        if iterations is None:
            iterations = self.optimal_iterations()
        
        # 步骤1：初始化所有量子比特为|0⟩
        state = np.zeros(self.n_states, dtype=complex)
        state[0] = 1
        
        # 步骤2：应用Hadamard门创建均匀叠加态
        H_n = self.hadamard_all()
        state = H_n @ state
        
        # 步骤3：构建Oracle和扩散算子
        O = self.oracle(target)
        D = self.diffuser()
        
        # 步骤4：迭代应用Grover算子
        grover_operator = D @ O
        
        for i in range(iterations):
            state = grover_operator @ state
            prob = np.abs(state[target]) ** 2
        
        final_prob = np.abs(state[target]) ** 2
        
        return state, final_prob
    
    def measure(self, state: np.ndarray) -> int:
        """
        测量量子态
        
        Args:
            state: 量子态向量
            
        Returns:
            测量结果（索引）
        """
        probs = np.abs(state) ** 2
        return np.random.choice(self.n_states, p=probs)
    
    def multi_search(self, targets: List[int], iterations: Optional[int] = None) -> Tuple[np.ndarray, dict]:
        """
        多目标Grover搜索
        
        Args:
            targets: 目标索引列表
            iterations: 迭代次数
            
        Returns:
            (最终态, 各目标概率)
        """
        if iterations is None:
            # 多目标时迭代次数调整
            n_targets = len(targets)
            iterations = int(np.round(np.pi * np.sqrt(self.n_states / n_targets) / 4))
        
        # 构建多目标Oracle
        oracle_matrix = np.eye(self.n_states, dtype=complex)
        for target in targets:
            oracle_matrix[target, target] = -1
        
        # 初始化
        state = np.zeros(self.n_states, dtype=complex)
        state[0] = 1
        H_n = self.hadamard_all()
        state = H_n @ state
        
        # 扩散算子
        D = self.diffuser()
        
        # 迭代
        grover_operator = D @ oracle_matrix
        for _ in range(iterations):
            state = grover_operator @ state
        
        # 计算各目标概率
        target_probs = {t: np.abs(state[t]) ** 2 for t in targets}
        
        return state, target_probs


class GroverTest:
    """Grover算法测试"""
    
    def __init__(self):
        self.test_results = []
    
    def test_single_target(self):
        """测试单目标搜索"""
        print("\n=== 测试单目标Grover搜索 ===")
        
        for n_qubits in [2, 3, 4]:
            grover = GroverSearch(n_qubits)
            target = np.random.randint(0, 2 ** n_qubits)
            
            state, prob = grover.search(target)
            
            print(f"  {n_qubits}量子比特: 目标={target}, 概率={prob:.4f}")
            
            # 测量
            measurements = [grover.measure(state) for _ in range(100)]
            success_rate = measurements.count(target) / 100
            print(f"    测量成功率: {success_rate:.2%}")
            
            self.test_results.append({
                "test": f"single_target_{n_qubits}q",
                "success": success_rate > 0.8
            })
    
    def test_optimal_iterations(self):
        """测试最优迭代次数计算"""
        print("\n=== 测试最优迭代次数 ===")
        
        for n_qubits in [2, 3, 4, 5]:
            grover = GroverSearch(n_qubits)
            opt_iter = grover.optimal_iterations()
            expected = int(np.round(np.pi * np.sqrt(2 ** n_qubits) / 4))
            
            match = opt_iter == expected
            print(f"  {n_qubits}量子比特: 计算={opt_iter}, 期望={expected} {'✓' if match else '✗'}")
            
            self.test_results.append({
                "test": f"optimal_iter_{n_qubits}q",
                "success": match
            })
    
    def test_multi_target(self):
        """测试多目标搜索"""
        print("\n=== 测试多目标Grover搜索 ===")
        
        grover = GroverSearch(3)
        targets = [0, 3]  # 两个目标
        
        state, target_probs = grover.multi_search(targets)
        
        print(f"  目标: {targets}")
        print(f"  各目标概率: {target_probs}")
        
        total_prob = sum(target_probs.values())
        print(f"  总目标概率: {total_prob:.4f}")
        
        self.test_results.append({
            "test": "multi_target",
            "success": total_prob > 0.7
        })
    
    def test_probability_amplification(self):
        """测试概率放大"""
        print("\n=== 测试概率放大过程 ===")
        
        grover = GroverSearch(3)
        target = 5
        
        # 初始概率（均匀分布）
        initial_prob = 1 / grover.n_states
        
        # 最终概率
        state, final_prob = grover.search(target, iterations=grover.optimal_iterations())
        
        amplification = final_prob / initial_prob
        
        print(f"  初始概率: {initial_prob:.4f}")
        print(f"  最终概率: {final_prob:.4f}")
        print(f"  放大倍数: {amplification:.2f}x")
        
        self.test_results.append({
            "test": "probability_amplification",
            "success": amplification > grover.n_states / 2
        })
    
    def test_oracle_construction(self):
        """测试Oracle构建"""
        print("\n=== 测试Oracle构建 ===")
        
        grover = GroverSearch(2)
        
        for target in range(4):
            O = grover.oracle(target)
            
            # 验证：Oracle应该只翻转目标态的相位
            test_state = np.zeros(4, dtype=complex)
            test_state[target] = 1
            
            result = O @ test_state
            expected = -test_state
            
            match = np.allclose(result, expected)
            print(f"  目标{target}: {'✓' if match else '✗'}")
            
            self.test_results.append({
                "test": f"oracle_target_{target}",
                "success": match
            })
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 50)
        print("Grover搜索算法测试套件")
        print("=" * 50)
        
        self.test_oracle_construction()
        self.test_optimal_iterations()
        self.test_single_target()
        self.test_multi_target()
        self.test_probability_amplification()
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print("\n" + "=" * 50)
        print(f"测试结果: {passed}/{total} 通过")
        print("=" * 50)
        
        return passed == total


if __name__ == "__main__":
    # 运行测试
    suite = GroverTest()
    all_passed = suite.run_all_tests()
    
    if all_passed:
        print("\n✅ Grover算法验证成功！")
    else:
        print("\n❌ 部分测试失败")
    
    # 演示
    print("\n" + "=" * 50)
    print("Grover搜索演示")
    print("=" * 50)
    
    # 3量子比特，目标=5
    print("\n在8个元素中搜索目标元素5:")
    grover = GroverSearch(3)
    target = 5
    
    print(f"最优迭代次数: {grover.optimal_iterations()}")
    
    state, prob = grover.search(target)
    print(f"目标态概率: {prob:.4f}")
    
    # 多次测量
    print("\n100次测量结果:")
    measurements = [grover.measure(state) for _ in range(100)]
    success_count = measurements.count(target)
    print(f"找到目标次数: {success_count}/100 ({success_count}%)")
    
    # 演示概率放大过程
    print("\n概率放大过程:")
    for i in range(5):
        state, prob = grover.search(target, iterations=i)
        print(f"  迭代{i}次: 概率={prob:.4f}")
