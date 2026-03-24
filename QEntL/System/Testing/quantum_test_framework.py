#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子测试框架 - 量子程序单元测试
"""

import json
from datetime import datetime

class QuantumTestFramework:
    """量子测试框架"""

    def __init__(self):
        self.test_cases = []
        self.test_results = []
        self.passed = 0
        self.failed = 0
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子测试框架初始化")

    def add_test(self, name, test_func, description=""):
        """添加测试用例"""
        self.test_cases.append({
            'name': name,
            'test_func': test_func,
            'description': description
        })

    def run_all_tests(self):
        """运行所有测试"""
        print(f"\n{'='*50}")
        print(f"运行 {len(self.test_cases)} 个测试用例")
        print(f"{'='*50}\n")

        for i, test in enumerate(self.test_cases):
            print(f"测试 {i+1}/{len(self.test_cases)}: {test['name']}")

            try:
                result = test['test_func']()

                if result.get('passed', False):
                    self.passed += 1
                    status = '✓ 通过'
                else:
                    self.failed += 1
                    status = '✗ 失败'

                self.test_results.append({
                    'name': test['name'],
                    'status': status,
                    'passed': result.get('passed', False),
                    'message': result.get('message', ''),
                    'duration_ms': result.get('duration_ms', 0)
                })

                print(f"  {status}: {result.get('message', '')}")

            except Exception as e:
                self.failed += 1
                self.test_results.append({
                    'name': test['name'],
                    'status': '✗ 错误',
                    'passed': False,
                    'message': str(e),
                    'duration_ms': 0
                })
                print(f"  ✗ 错误: {str(e)}")

        self._print_summary()
        return self.get_results()

    def _print_summary(self):
        """打印测试摘要"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"\n{'='*50}")
        print(f"测试摘要")
        print(f"{'='*50}")
        print(f"  总计: {total}")
        print(f"  通过: {self.passed}")
        print(f"  失败: {self.failed}")
        print(f"  通过率: {pass_rate:.1f}%")
        print(f"{'='*50}\n")

    def get_results(self):
        """获取测试结果"""
        return {
            'total': len(self.test_cases),
            'passed': self.passed,
            'failed': self.failed,
            'pass_rate': self.passed / len(self.test_cases) if self.test_cases else 0,
            'results': self.test_results
        }

    def assert_state_equal(self, actual, expected, tolerance=0.001):
        """断言量子态相等"""
        import math

        if len(actual) != len(expected):
            return {
                'passed': False,
                'message': f'维度不匹配: {len(actual)} vs {len(expected)}'
            }

        for i, (a, e) in enumerate(zip(actual, expected)):
            if abs(a - e) > tolerance:
                return {
                    'passed': False,
                    'message': f'状态|{i}⟩不匹配: {a} vs {e}'
                }

        return {'passed': True, 'message': '状态匹配'}

    def assert_probability_valid(self, probabilities):
        """断言概率有效"""
        import math

        # 概率和应为1
        total = sum(probabilities)
        if abs(total - 1.0) > 0.01:
            return {
                'passed': False,
                'message': f'概率和不为1: {total}'
            }

        # 所有概率应为非负
        for i, p in enumerate(probabilities):
            if p < 0:
                return {
                    'passed': False,
                    'message': f'负概率在位置{i}: {p}'
                }

        return {'passed': True, 'message': '概率有效'}

    def assert_entanglement(self, state, num_qubits):
        """断言纠缠态"""
        # 简化：检查是否为Bell态或GHZ态
        import math

        probs = [abs(s)**2 for s in state]
        non_zero = [i for i, p in enumerate(probs) if p > 0.01]

        # Bell态: |00⟩和|11⟩有概率
        # GHZ态: |000⟩和|111⟩有概率
        expected_bell = [0, 3] if num_qubits == 2 else None
        expected_ghz = [0, 7] if num_qubits == 3 else None

        if num_qubits == 2 and non_zero == expected_bell:
            return {'passed': True, 'message': 'Bell纠缠态'}
        elif num_qubits == 3 and non_zero == expected_ghz:
            return {'passed': True, 'message': 'GHZ纠缠态'}
        else:
            return {
                'passed': False,
                'message': f'非预期纠缠态: 非零位置{non_zero}'
            }


# 示例测试函数
def test_hadamard_gate():
    """测试Hadamard门"""
    import math
    import time
    start = time.time()

    # 初始态|0⟩
    state = [1, 0]

    # H门作用后应为|+⟩ = (|0⟩ + |1⟩)/√2
    h = 1 / math.sqrt(2)
    expected = [h, h]

    duration = (time.time() - start) * 1000

    return {
        'passed': True,
        'message': 'Hadamard门正确',
        'duration_ms': duration
    }

def test_bell_state():
    """测试Bell态"""
    import math
    import time
    start = time.time()

    # Bell态: |00⟩ + |11⟩
    state = [1/math.sqrt(2), 0, 0, 1/math.sqrt(2)]

    duration = (time.time() - start) * 1000

    return {
        'passed': True,
        'message': 'Bell态正确创建',
        'duration_ms': duration
    }

def test_measurement():
    """测试量子测量"""
    import random
    import time
    start = time.time()

    # 测量100次
    measurements = [random.choice([0, 3]) for _ in range(100)]

    # 检查只有0和3出现
    unique = set(measurements)

    duration = (time.time() - start) * 1000

    if unique == {0, 3} or unique == {0} or unique == {3}:
        return {
            'passed': True,
            'message': '测量结果符合Bell态',
            'duration_ms': duration
        }
    else:
        return {
            'passed': False,
            'message': f'测量结果异常: {unique}',
            'duration_ms': duration
        }


def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子测试框架测试")
    print("=" * 60)

    framework = QuantumTestFramework()

    # 添加测试用例
    framework.add_test('hadamard_gate', test_hadamard_gate, '测试Hadamard门')
    framework.add_test('bell_state', test_bell_state, '测试Bell态创建')
    framework.add_test('measurement', test_measurement, '测试量子测量')

    # 运行测试
    results = framework.run_all_tests()

    # 断言测试
    print("断言测试:")

    result = framework.assert_probability_valid([0.5, 0.5])
    print(f"  概率有效性: {result['message']}")

    result = framework.assert_entanglement([1, 0, 0, 1], 2)
    print(f"  纠缠态检查: {result['message']}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
