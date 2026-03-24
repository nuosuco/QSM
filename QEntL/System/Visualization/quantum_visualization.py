#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子可视化模块 - 量子态可视化工具
"""

import math
import json
from datetime import datetime

class QuantumVisualization:
    """量子态可视化"""

    def __init__(self):
        self.visualizations = []
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子可视化模块初始化")

    def bloch_sphere(self, alpha, beta):
        """
        布洛赫球可视化
        alpha: |0⟩振幅
        beta: |1⟩振幅
        """
        # 归一化
        norm = math.sqrt(abs(alpha)**2 + abs(beta)**2)
        if norm == 0:
            alpha, beta = 1, 0
        else:
            alpha /= norm
            beta /= norm

        # 计算布洛赫球坐标
        # |ψ⟩ = α|0⟩ + β|1⟩
        # θ = 2 arccos(|α|)
        # φ = arg(β) - arg(α)
        
        theta = 2 * math.acos(min(1, abs(alpha)))
        
        if abs(alpha) > 0:
            phi = math.atan2(beta.imag if hasattr(beta, 'imag') else 0, 
                           beta.real if hasattr(beta, 'real') else beta)
        else:
            phi = 0

        # 笛卡尔坐标
        x = math.sin(theta) * math.cos(phi)
        y = math.sin(theta) * math.sin(phi)
        z = math.cos(theta)

        return {
            'type': 'bloch_sphere',
            'coordinates': {
                'theta': theta,
                'phi': phi,
                'x': round(x, 4),
                'y': round(y, 4),
                'z': round(z, 4)
            },
            'probabilities': {
                'p0': round(abs(alpha)**2, 4),
                'p1': round(abs(beta)**2, 4)
            },
            'state': f'|ψ⟩ = {alpha:.3f}|0⟩ + {beta:.3f}|1⟩'
        }

    def qubit_bar_chart(self, state_vector):
        """
        量子比特概率柱状图数据
        """
        probabilities = []
        for i, amp in enumerate(state_vector):
            prob = abs(amp)**2 if hasattr(amp, '__abs__') else abs(amp)**2
            probabilities.append({
                'basis': f'|{i}⟩',
                'probability': round(prob, 4),
                'amplitude': complex(amp) if not isinstance(amp, complex) else amp
            })

        return {
            'type': 'probability_distribution',
            'num_states': len(state_vector),
            'probabilities': probabilities,
            'dominant_state': max(probabilities, key=lambda x: x['probability'])
        }

    def entanglement_matrix(self, num_qubits):
        """
        纠缠矩阵可视化
        显示量子比特之间的纠缠关系
        """
        matrix = []
        for i in range(num_qubits):
            row = []
            for j in range(num_qubits):
                if i == j:
                    row.append(1.0)  # 自身
                else:
                    # 模拟纠缠度（实际应从状态计算）
                    row.append(round(0.5 + 0.5 * math.cos(i + j), 3))
            matrix.append(row)

        return {
            'type': 'entanglement_matrix',
            'num_qubits': num_qubits,
            'matrix': matrix,
            'description': '量子比特纠缠程度矩阵'
        }

    def quantum_circuit_diagram(self, gates):
        """
        量子电路图数据
        """
        diagram = []
        qubit_lines = [[] for _ in range(4)]  # 假设最多4量子比特

        for gate in gates:
            gate_type = gate.get('type', 'unknown')
            target = gate.get('target', 0)
            control = gate.get('control', None)

            for q in range(len(qubit_lines)):
                if q == target:
                    qubit_lines[q].append(gate_type)
                elif control is not None and q == control:
                    qubit_lines[q].append('●')
                else:
                    qubit_lines[q].append('│')

        return {
            'type': 'circuit_diagram',
            'gates': gates,
            'qubit_lines': qubit_lines,
            'total_gates': len(gates)
        }

    def state_evolution(self, states):
        """
        量子态演化可视化
        """
        evolution = []
        for i, state in enumerate(states):
            if isinstance(state, list):
                probs = [abs(s)**2 for s in state]
            else:
                probs = [abs(state)**2, 1 - abs(state)**2]

            evolution.append({
                'step': i,
                'probabilities': probs,
                'entropy': self._calculate_entropy(probs)
            })

        return {
            'type': 'state_evolution',
            'steps': len(evolution),
            'evolution': evolution,
            'entropy_change': [e['entropy'] for e in evolution]
        }

    def _calculate_entropy(self, probs):
        """计算冯诺依曼熵"""
        entropy = 0
        for p in probs:
            if 0 < p < 1:
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    def measurement_histogram(self, measurements, shots=1000):
        """
        测量结果直方图数据
        """
        counts = {}
        for m in measurements[:shots]:
            key = str(m)
            counts[key] = counts.get(key, 0) + 1

        # 排序并计算概率
        sorted_counts = sorted(counts.items(), key=lambda x: -x[1])

        return {
            'type': 'measurement_histogram',
            'shots': min(len(measurements), shots),
            'counts': dict(sorted_counts),
            'probabilities': {k: round(v/shots, 4) for k, v in sorted_counts}
        }

    def export_visualization(self, visualization, format='json'):
        """导出可视化数据"""
        if format == 'json':
            return json.dumps(visualization, indent=2, ensure_ascii=False)
        return visualization

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子可视化模块测试")
    print("=" * 60)

    viz = QuantumVisualization()

    # 布洛赫球测试
    print("\n布洛赫球可视化:")
    result = viz.bloch_sphere(1/math.sqrt(2), 1/math.sqrt(2))
    print(f"  坐标: ({result['coordinates']['x']}, {result['coordinates']['y']}, {result['coordinates']['z']})")
    print(f"  概率: P(0)={result['probabilities']['p0']}, P(1)={result['probabilities']['p1']}")

    # 概率分布测试
    print("\n量子态概率分布:")
    state = [1/math.sqrt(2), 0, 0, 1/math.sqrt(2)]  # Bell态
    result = viz.qubit_bar_chart(state)
    print(f"  状态数: {result['num_states']}")
    print(f"  主导态: {result['dominant_state']['basis']}")

    # 纠缠矩阵测试
    print("\n纠缠矩阵:")
    result = viz.entanglement_matrix(4)
    print(f"  量子比特数: {result['num_qubits']}")

    # 量子电路测试
    print("\n量子电路图:")
    gates = [
        {'type': 'H', 'target': 0},
        {'type': 'CNOT', 'control': 0, 'target': 1},
        {'type': 'Z', 'target': 1}
    ]
    result = viz.quantum_circuit_diagram(gates)
    print(f"  门数: {result['total_gates']}")

    # 测量直方图测试
    print("\n测量直方图:")
    import random
    measurements = [random.choice(['00', '11']) for _ in range(1000)]
    result = viz.measurement_histogram(measurements, shots=1000)
    print(f"  测量次数: {result['shots']}")
    print(f"  结果分布: {result['probabilities']}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
