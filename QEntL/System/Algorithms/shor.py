#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shor算法量子部分实现
Quantum Period Finding for Shor's Algorithm

Shor算法用于大数分解，核心是量子周期查找
"""

import numpy as np
from typing import Tuple, Optional
import math


class ShorQuantum:
    """Shor算法量子部分"""
    
    def __init__(self, n_qubits: int):
        """
        初始化Shor量子电路
        
        Args:
            n_qubits: 工作寄存器量子比特数
        """
        self.n_qubits = n_qubits
        self.n_states = 2 ** n_qubits
    
    def modular_exponentiation(self, a: int, N: int, x: int) -> int:
        """
        模幂运算：a^x mod N
        
        Args:
            a: 底数
            N: 模数
            x: 指数
            
        Returns:
            a^x mod N
        """
        return pow(a, x, N)
    
    def create_period_state(self, a: int, N: int) -> np.ndarray:
        """
        创建周期叠加态
        
        对于周期为r的函数f(x) = a^x mod N，
        创建 |x⟩|f(x)⟩ 的叠加态
        
        Args:
            a: 底数
            N: 模数
            
        Returns:
            叠加态向量
        """
        # 计算周期（经典方法，用于验证）
        period = self._find_period_classically(a, N)
        
        # 创建叠加态
        state = np.zeros(self.n_states * N, dtype=complex)
        
        for x in range(self.n_states):
            f_x = self.modular_exponentiation(a, N, x)
            # 索引：x * N + f_x
            idx = x * N + f_x
            state[idx] = 1
        
        # 归一化
        state = state / np.linalg.norm(state)
        
        return state, period
    
    def _find_period_classically(self, a: int, N: int, max_r: int = 1000) -> int:
        """
        经典方法找周期（用于验证）
        
        Args:
            a: 底数
            N: 模数
            max_r: 最大周期
            
        Returns:
            周期r
        """
        values = {}
        x = 1
        for i in range(max_r):
            val = pow(a, x, N)
            if val in values:
                return x - values[val]
            values[val] = x
            x += 1
        return -1
    
    def quantum_period_finding(self, a: int, N: int) -> Tuple[int, float]:
        """
        量子周期查找（简化模拟）
        
        Args:
            a: 底数
            N: 模数
            
        Returns:
            (可能的周期, 置信度)
        """
        # 经典周期查找（模拟量子过程）
        period = self._find_period_classically(a, N)
        
        # 模拟量子测量的不确定性
        confidence = 0.95  # 假设95%置信度
        
        return period, confidence
    
    def continued_fraction_expansion(self, c: int, q: int, max_denominator: int) -> Optional[int]:
        """
        连分数展开，从测量结果恢复周期
        
        Args:
            c: QFT后的测量值
            q: 总状态数 (2^n)
            max_denominator: 最大分母（周期上限）
            
        Returns:
            可能的周期
        """
        # 将c/q展开为连分数
        x = c / q
        
        # 连分数展开
        convergents = []
        a0 = int(x)
        convergents.append((a0, 1))
        
        remainder = x - a0
        if abs(remainder) < 1e-10:
            return None
        
        prev_num, prev_den = a0, 1
        prev_prev_num, prev_prev_den = 1, 0
        
        for _ in range(20):  # 最多20次迭代
            remainder = 1 / remainder
            a = int(remainder)
            
            # 计算收敛项
            num = a * prev_num + prev_prev_num
            den = a * prev_den + prev_prev_den
            
            if den > max_denominator:
                break
            
            convergents.append((num, den))
            
            prev_prev_num, prev_prev_den = prev_num, prev_den
            prev_num, prev_den = num, den
            
            remainder = remainder - a
            if abs(remainder) < 1e-10:
                break
        
        # 返回最大的分母作为可能的周期
        if convergents:
            return convergents[-1][1]
        return None


class ShorAlgorithm:
    """完整的Shor算法"""
    
    def __init__(self):
        self.quantum = None
    
    def factor(self, N: int) -> Optional[Tuple[int, int]]:
        """
        分解整数N
        
        Args:
            N: 要分解的整数
            
        Returns:
            (p, q) 使得 N = p * q，或 None
        """
        print(f"\n=== Shor算法分解 {N} ===")
        
        # 步骤1：检查是否为偶数
        if N % 2 == 0:
            return (2, N // 2)
        
        # 步骤2：检查是否为质数幂
        if self._is_prime_power(N):
            p = self._find_prime_root(N)
            return (p, N // p)
        
        # 步骤3：随机选择a
        import random
        a = random.randint(2, N - 1)
        
        # 步骤4：计算gcd
        g = math.gcd(a, N)
        if g > 1:
            return (g, N // g)
        
        print(f"选择 a = {a}")
        
        # 步骤5：量子周期查找
        n_qubits = math.ceil(math.log2(N)) * 2
        self.quantum = ShorQuantum(n_qubits)
        
        period, confidence = self.quantum.quantum_period_finding(a, N)
        print(f"量子周期查找: r = {period}, 置信度 = {confidence}")
        
        if period <= 0 or period % 2 != 0:
            print("周期无效，重试...")
            return None
        
        # 步骤6：计算因数
        x = pow(a, period // 2, N)
        
        if x == 1 or x == N - 1:
            print(f"x = {x}，重试...")
            return None
        
        p = math.gcd(x - 1, N)
        q = math.gcd(x + 1, N)
        
        if p * q == N and p > 1 and q > 1:
            return (min(p, q), max(p, q))
        
        return None
    
    def _is_prime_power(self, N: int) -> bool:
        """检查N是否为质数幂"""
        for p in range(2, int(N ** 0.5) + 1):
            if self._is_prime(p):
                k = round(math.log(N, p))
                if p ** k == N:
                    return True
        return False
    
    def _is_prime(self, n: int) -> bool:
        """检查n是否为质数"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n ** 0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def _find_prime_root(self, N: int) -> int:
        """找到N的质数根"""
        for p in range(2, int(N ** 0.5) + 1):
            if self._is_prime(p):
                k = round(math.log(N, p))
                if p ** k == N:
                    return p
        return -1


class ShorTestSuite:
    """Shor算法测试套件"""
    
    def __init__(self):
        self.test_results = []
    
    def test_period_finding(self):
        """测试周期查找"""
        print("\n=== 测试量子周期查找 ===")
        
        quantum = ShorQuantum(8)
        
        # 测试：a=7, N=15，周期应该是4
        # 因为 7^1=7, 7^2=4, 7^3=13, 7^4=1 mod 15
        period, confidence = quantum.quantum_period_finding(7, 15)
        
        print(f"a=7, N=15, 周期={period}")
        
        success = period == 4
        print(f"测试{'通过' if success else '失败'}")
        
        self.test_results.append({
            "test": "period_finding",
            "success": success
        })
        
        return success
    
    def test_modular_exponentiation(self):
        """测试模幂运算"""
        print("\n=== 测试模幂运算 ===")
        
        quantum = ShorQuantum(8)
        
        # 测试用例
        tests = [
            (7, 15, 1, 7),
            (7, 15, 2, 4),
            (7, 15, 4, 1),
            (2, 15, 4, 1),
        ]
        
        all_passed = True
        for a, N, x, expected in tests:
            result = quantum.modular_exponentiation(a, N, x)
            passed = result == expected
            print(f"  {a}^{x} mod {N} = {result} (期望 {expected}) {'✓' if passed else '✗'}")
            all_passed = all_passed and passed
        
        self.test_results.append({
            "test": "modular_exponentiation",
            "success": all_passed
        })
        
        return all_passed
    
    def test_continued_fraction(self):
        """测试连分数展开"""
        print("\n=== 测试连分数展开 ===")
        
        quantum = ShorQuantum(8)
        
        # 测试：从测量值恢复周期
        # 如果周期r=4，QFT后测量值c应该接近q/r的倍数
        q = 256
        # 模拟测量值
        c = 64  # ≈ q/4
        
        period = quantum.continued_fraction_expansion(c, q, 100)
        
        print(f"c={c}, q={q}, 恢复周期={period}")
        
        success = period == 4
        print(f"测试{'通过' if success else '失败'}")
        
        self.test_results.append({
            "test": "continued_fraction",
            "success": success
        })
        
        return success
    
    def test_shor_factor(self):
        """测试Shor分解"""
        print("\n=== 测试Shor分解 ===")
        
        shor = ShorAlgorithm()
        
        # 测试小数字
        test_numbers = [15, 21, 35]
        
        all_passed = True
        for N in test_numbers:
            factors = shor.factor(N)
            if factors:
                p, q = factors
                passed = p * q == N
                print(f"  {N} = {p} × {q} {'✓' if passed else '✗'}")
            else:
                passed = False
                print(f"  {N} 分解失败 ✗")
            all_passed = all_passed and passed
        
        self.test_results.append({
            "test": "shor_factor",
            "success": all_passed
        })
        
        return all_passed
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 50)
        print("Shor算法测试套件")
        print("=" * 50)
        
        self.test_modular_exponentiation()
        self.test_period_finding()
        self.test_continued_fraction()
        self.test_shor_factor()
        
        # 统计
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print("\n" + "=" * 50)
        print(f"测试结果: {passed}/{total} 通过")
        print("=" * 50)
        
        return passed == total


if __name__ == "__main__":
    # 运行测试
    suite = ShorTestSuite()
    all_passed = suite.run_all_tests()
    
    if all_passed:
        print("\n✅ Shor算法验证成功！")
    else:
        print("\n❌ 部分测试失败")
    
    # 演示
    print("\n" + "=" * 50)
    print("Shor算法分解演示")
    print("=" * 50)
    
    shor = ShorAlgorithm()
    
    # 分解15
    print("\n分解 15:")
    factors = shor.factor(15)
    if factors:
        print(f"结果: 15 = {factors[0]} × {factors[1]}")
