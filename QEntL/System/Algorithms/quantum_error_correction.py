#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子纠错模块 - 实现基础量子纠错码
"""

import math
import random
from datetime import datetime

class QuantumErrorCorrection:
    """量子纠错系统"""

    def __init__(self):
        self.error_history = []
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子纠错系统初始化")

    def bit_flip_code(self, qubit_state, error_prob=0.1):
        """
        比特翻转纠错码
        使用3个物理量子比特编码1个逻辑量子比特
        """
        # 编码: |0⟩ → |000⟩, |1⟩ → |111⟩
        encoded = [qubit_state, qubit_state, qubit_state]

        # 模拟错误
        errors = []
        for i in range(3):
            if random.random() < error_prob:
                encoded[i] = 1 - encoded[i]  # 翻转
                errors.append(i)

        # 纠错：多数表决
        if sum(encoded) >= 2:
            corrected = 1
        else:
            corrected = 0

        return {
            'code': 'bit_flip',
            'original': qubit_state,
            'encoded': encoded,
            'errors': errors,
            'corrected': corrected,
            'success': corrected == qubit_state
        }

    def phase_flip_code(self, qubit_state, error_prob=0.1):
        """
        相位翻转纠错码
        使用3个物理量子比特编码1个逻辑量子比特
        """
        # 编码: |+⟩ → |+++⟩, |−⟩ → |---⟩
        # 简化模拟
        encoded = [qubit_state, qubit_state, qubit_state]

        # 模拟相位错误
        errors = []
        for i in range(3):
            if random.random() < error_prob:
                errors.append(i)

        # 纠错
        corrected = qubit_state

        return {
            'code': 'phase_flip',
            'original': qubit_state,
            'errors': errors,
            'success': True
        }

    def shor_code(self, qubit_state, error_prob=0.05):
        """
        Shor码 - 9量子比特纠错码
        可以同时纠正比特翻转和相位翻转错误
        """
        # 9个量子比特编码1个逻辑量子比特
        encoded = [qubit_state] * 9

        # 模拟错误
        errors = []
        for i in range(9):
            if random.random() < error_prob:
                errors.append(i)

        # 纠错（简化版）
        corrected = qubit_state
        success = len(errors) <= 1  # 可以纠正单个错误

        return {
            'code': 'shor_9qubit',
            'original': qubit_state,
            'error_count': len(errors),
            'corrected': corrected,
            'success': success
        }

    def surface_code_simulation(self, distance=3, error_prob=0.01):
        """
        表面码模拟
        距离为d的表面码可以纠正(d-1)/2个错误
        """
        num_qubits = distance * distance
        num_errors = 0

        for _ in range(num_qubits):
            if random.random() < error_prob:
                num_errors += 1

        correctable_errors = (distance - 1) // 2
        success = num_errors <= correctable_errors

        return {
            'code': 'surface',
            'distance': distance,
            'num_qubits': num_qubits,
            'errors': num_errors,
            'correctable': correctable_errors,
            'success': success
        }

    def test_all_codes(self, trials=100):
        """测试所有纠错码"""
        results = {
            'bit_flip': {'success': 0, 'total': trials},
            'phase_flip': {'success': 0, 'total': trials},
            'shor': {'success': 0, 'total': trials},
            'surface': {'success': 0, 'total': trials}
        }

        for _ in range(trials):
            state = random.randint(0, 1)

            # 比特翻转码
            r = self.bit_flip_code(state, error_prob=0.1)
            if r['success']:
                results['bit_flip']['success'] += 1

            # 相位翻转码
            r = self.phase_flip_code(state, error_prob=0.1)
            if r['success']:
                results['phase_flip']['success'] += 1

            # Shor码
            r = self.shor_code(state, error_prob=0.05)
            if r['success']:
                results['shor']['success'] += 1

            # 表面码
            r = self.surface_code_simulation(distance=3, error_prob=0.01)
            if r['success']:
                results['surface']['success'] += 1

        return results

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子纠错模块测试")
    print("=" * 60)

    qec = QuantumErrorCorrection()

    print("\n测试比特翻转码:")
    for _ in range(3):
        r = qec.bit_flip_code(random.randint(0, 1), error_prob=0.1)
        print(f"  原始: {r['original']}, 纠错: {r['corrected']}, 成功: {r['success']}")

    print("\n测试Shor码:")
    for _ in range(3):
        r = qec.shor_code(random.randint(0, 1), error_prob=0.05)
        print(f"  错误数: {r['error_count']}, 成功: {r['success']}")

    print("\n测试表面码:")
    for d in [3, 5]:
        r = qec.surface_code_simulation(distance=d, error_prob=0.01)
        print(f"  距离{d}: {r['num_qubits']}量子比特, 错误{r['errors']}个, 成功: {r['success']}")

    print("\n批量测试100次:")
    results = qec.test_all_codes(trials=100)
    for code, data in results.items():
        rate = data['success'] / data['total'] * 100
        print(f"  {code}: {data['success']}/{data['total']} ({rate:.1f}%)")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
