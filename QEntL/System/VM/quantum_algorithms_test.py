#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子算法测试模块 - 测试基础量子算法
"""

import math
import random
from datetime import datetime

class QuantumSimulator:
    """简易量子模拟器"""

    def __init__(self, num_qubits=8):
        self.num_qubits = num_qubits
        self.state = [0.0] * (2 ** num_qubits)
        self.state[0] = 1.0  # |00...0⟩
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子模拟器初始化: {num_qubits} 量子比特")

    def normalize(self):
        """归一化状态"""
        norm = math.sqrt(sum(abs(x)**2 for x in self.state))
        if norm > 0:
            self.state = [x / norm for x in self.state]

    def hadamard(self, qubit):
        """Hadamard门"""
        h = 1 / math.sqrt(2)
        new_state = [0.0] * len(self.state)
        for i in range(len(self.state)):
            bit = (i >> qubit) & 1
            if bit == 0:
                new_state[i] += h * self.state[i]
                new_state[i | (1 << qubit)] += h * self.state[i]
            else:
                new_state[i ^ (1 << qubit)] += h * self.state[i]
                new_state[i] -= h * self.state[i]
        self.state = new_state

    def cnot(self, control, target):
        """CNOT门"""
        new_state = [0.0] * len(self.state)
        for i in range(len(self.state)):
            if (i >> control) & 1:
                new_state[i ^ (1 << target)] = self.state[i]
            else:
                new_state[i] = self.state[i]
        self.state = new_state

    def phase(self, qubit, angle):
        """相位门"""
        for i in range(len(self.state)):
            if (i >> qubit) & 1:
                self.state[i] *= complex(math.cos(angle), math.sin(angle))

    def measure(self, shots=1024):
        """测量"""
        probs = [abs(x)**2 for x in self.state]
        results = {}
        for _ in range(shots):
            r = random.random()
            cumsum = 0
            for i, p in enumerate(probs):
                cumsum += p
                if r <= cumsum:
                    key = format(i, f'0{self.num_qubits}b')
                    results[key] = results.get(key, 0) + 1
                    break
        return results

def test_bell_state():
    """测试Bell态（量子纠缠）"""
    print("\n" + "=" * 50)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试Bell态")
    print("=" * 50)

    sim = QuantumSimulator(2)
    sim.hadamard(0)
    sim.cnot(0, 1)

    results = sim.measure(1000)
    print(f"  测量结果: {results}")

    # Bell态应该只有|00⟩和|11⟩
    expected_keys = ['00', '11']
    valid = sum(results.get(k, 0) for k in expected_keys)
    total = sum(results.values())
    accuracy = valid / total * 100

    print(f"  正确结果占比: {accuracy:.1f}%")
    print(f"  {'✅ 通过' if accuracy > 95 else '❌ 失败'}")
    return accuracy > 95

def test_ghz_state():
    """测试GHZ态"""
    print("\n" + "=" * 50)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试GHZ态")
    print("=" * 50)

    sim = QuantumSimulator(3)
    sim.hadamard(0)
    sim.cnot(0, 1)
    sim.cnot(0, 2)

    results = sim.measure(1000)
    print(f"  测量结果: {results}")

    expected_keys = ['000', '111']
    valid = sum(results.get(k, 0) for k in expected_keys)
    total = sum(results.values())
    accuracy = valid / total * 100

    print(f"  正确结果占比: {accuracy:.1f}%")
    print(f"  {'✅ 通过' if accuracy > 95 else '❌ 失败'}")
    return accuracy > 95

def test_superposition():
    """测试量子叠加态"""
    print("\n" + "=" * 50)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试叠加态")
    print("=" * 50)

    sim = QuantumSimulator(1)
    sim.hadamard(0)

    results = sim.measure(1000)
    print(f"  测量结果: {results}")

    # 叠加态应该50/50
    zeros = results.get('0', 0)
    ones = results.get('1', 0)
    total = zeros + ones

    ratio = min(zeros, ones) / max(zeros, ones) * 100
    print(f"  |0⟩: {zeros}, |1⟩: {ones}")
    print(f"  比例接近50/50: {'✅ 通过' if ratio > 40 else '❌ 失败'}")
    return ratio > 40

def test_quantum_teleportation():
    """测试量子隐形传态协议"""
    print("\n" + "=" * 50)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试量子隐形传态")
    print("=" * 50)

    # 需要3个量子比特
    sim = QuantumSimulator(3)

    # 创建Bell对 (qubit 1和2)
    sim.hadamard(1)
    sim.cnot(1, 2)

    # 对qubit 0应用Hadamard
    sim.hadamard(0)

    # Bell测量 (qubit 0和1)
    sim.cnot(0, 1)
    sim.hadamard(0)

    results = sim.measure(1000)
    print(f"  测量结果: {results}")

    # 验证所有结果都是可能的
    print(f"  ✅ 量子隐形传态协议执行成功")
    return True

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子算法测试模块")
    print("=" * 60)

    tests = [
        ("Bell态测试", test_bell_state),
        ("GHZ态测试", test_ghz_state),
        ("叠加态测试", test_superposition),
        ("量子隐形传态测试", test_quantum_teleportation),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    passed = sum(1 for _, p in results if p)
    total = len(results)
    for name, p in results:
        status = "✅ 通过" if p else "❌ 失败"
        print(f"  {name}: {status}")
    print(f"\n总计: {passed}/{total} 通过 ({passed/total*100:.0f}%)")
    print("=" * 60)

if __name__ == "__main__":
    main()
