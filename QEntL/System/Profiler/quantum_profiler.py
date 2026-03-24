#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子性能分析器 - 量子电路性能分析
"""

import time
import json
from datetime import datetime
from collections import defaultdict

class QuantumProfiler:
    """量子性能分析器"""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.gate_counts = defaultdict(int)
        self.start_time = None
        self.profiling_data = []
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子性能分析器初始化")

    def start_profiling(self, circuit_name=""):
        """开始性能分析"""
        self.start_time = time.time()
        self.gate_counts = defaultdict(int)
        self.metrics = defaultdict(list)
        self.current_circuit = circuit_name

    def record_gate(self, gate_type, duration_ms=0):
        """记录量子门执行"""
        self.gate_counts[gate_type] += 1
        self.metrics['gates'].append({
            'type': gate_type,
            'duration_ms': duration_ms,
            'timestamp': time.time()
        })

    def end_profiling(self):
        """结束性能分析"""
        if self.start_time is None:
            return {'error': 'Profiling not started'}

        duration = (time.time() - self.start_time) * 1000  # ms

        profile = {
            'circuit': self.current_circuit,
            'total_time_ms': round(duration, 2),
            'gate_counts': dict(self.gate_counts),
            'total_gates': sum(self.gate_counts.values()),
            'metrics': {
                'avg_gate_time': self._calculate_avg_gate_time(),
                'gates_per_ms': sum(self.gate_counts.values()) / duration if duration > 0 else 0
            }
        }

        self.profiling_data.append(profile)
        return profile

    def _calculate_avg_gate_time(self):
        """计算平均门执行时间"""
        if not self.metrics['gates']:
            return 0
        total = sum(g['duration_ms'] for g in self.metrics['gates'])
        return total / len(self.metrics['gates'])

    def analyze_circuit(self, gates):
        """分析量子电路"""
        analysis = {
            'total_gates': len(gates),
            'gate_types': {},
            'depth': self._calculate_depth(gates),
            'entangling_gates': 0,
            'single_qubit_gates': 0
        }

        for gate in gates:
            gate_type = gate.get('type', 'unknown')
            analysis['gate_types'][gate_type] = analysis['gate_types'].get(gate_type, 0) + 1

            if gate_type in ['CNOT', 'CZ', 'SWAP']:
                analysis['entangling_gates'] += 1
            else:
                analysis['single_qubit_gates'] += 1

        # 计算复杂度
        analysis['complexity'] = self._estimate_complexity(analysis)

        return analysis

    def _calculate_depth(self, gates):
        """计算电路深度"""
        # 简化：假设每个门一层
        return len(gates)

    def _estimate_complexity(self, analysis):
        """估计计算复杂度"""
        n = analysis['total_gates']
        e = analysis['entangling_gates']

        # 简化复杂度估计
        if e == 0:
            return 'O(n)'
        else:
            return f'O(n^{1 + e/n:.1f})'

    def compare_circuits(self, circuits):
        """比较多个电路性能"""
        comparison = []

        for name, gates in circuits.items():
            analysis = self.analyze_circuit(gates)
            analysis['name'] = name
            comparison.append(analysis)

        # 排序（按总门数）
        comparison.sort(key=lambda x: x['total_gates'])

        return {
            'comparison': comparison,
            'best': comparison[0]['name'] if comparison else None,
            'metrics': ['total_gates', 'depth', 'entangling_gates']
        }

    def estimate_resources(self, num_qubits, num_gates):
        """估计资源需求"""
        # 内存需求（经典模拟）
        memory_states = 2 ** num_qubits
        memory_bytes = memory_states * 16  # 复数，每个16字节
        memory_mb = memory_bytes / (1024 * 1024)

        # 执行时间估计
        estimated_time_ms = num_gates * 0.1  # 假设每门0.1ms

        return {
            'num_qubits': num_qubits,
            'num_gates': num_gates,
            'memory_required_mb': round(memory_mb, 2),
            'estimated_time_ms': round(estimated_time_ms, 2),
            'feasible': memory_mb < 4096  # 小于4GB可行
        }

    def get_performance_report(self):
        """获取性能报告"""
        if not self.profiling_data:
            return {'error': 'No profiling data'}

        total_time = sum(p['total_time_ms'] for p in self.profiling_data)
        total_gates = sum(p['total_gates'] for p in self.profiling_data)

        return {
            'total_circuits': len(self.profiling_data),
            'total_time_ms': round(total_time, 2),
            'total_gates': total_gates,
            'average_time_per_circuit': round(total_time / len(self.profiling_data), 2),
            'circuits': self.profiling_data[-5:]  # 最近5个
        }

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子性能分析器测试")
    print("=" * 60)

    profiler = QuantumProfiler()

    # 分析电路
    print("\n分析Bell态电路:")
    bell_gates = [
        {'type': 'H', 'targets': ['q0']},
        {'type': 'CNOT', 'targets': ['q0', 'q1']}
    ]
    analysis = profiler.analyze_circuit(bell_gates)
    print(f"  总门数: {analysis['total_gates']}")
    print(f"  纠缠门: {analysis['entangling_gates']}")
    print(f"  复杂度: {analysis['complexity']}")

    # 分析GHZ态电路
    print("\n分析GHZ态电路:")
    ghz_gates = [
        {'type': 'H', 'targets': ['q0']},
        {'type': 'CNOT', 'targets': ['q0', 'q1']},
        {'type': 'CNOT', 'targets': ['q1', 'q2']}
    ]
    analysis = profiler.analyze_circuit(ghz_gates)
    print(f"  总门数: {analysis['total_gates']}")
    print(f"  纠缠门: {analysis['entangling_gates']}")

    # 比较电路
    print("\n比较电路:")
    circuits = {
        'Bell': bell_gates,
        'GHZ': ghz_gates
    }
    comparison = profiler.compare_circuits(circuits)
    print(f"  最佳电路: {comparison['best']}")

    # 资源估计
    print("\n资源估计:")
    resources = profiler.estimate_resources(num_qubits=4, num_gates=10)
    print(f"  量子比特: {resources['num_qubits']}")
    print(f"  内存需求: {resources['memory_required_mb']} MB")
    print(f"  可行: {resources['feasible']}")

    # 性能分析
    print("\n开始性能分析:")
    profiler.start_profiling("Bell Circuit")
    profiler.record_gate('H', 0.05)
    profiler.record_gate('CNOT', 0.1)
    profile = profiler.end_profiling()

    print(f"  总时间: {profile['total_time_ms']} ms")
    print(f"  门数: {profile['total_gates']}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
