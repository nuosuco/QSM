#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子计算工具库
提供量子计算常用工具和辅助函数

主要功能：
1. 量子门操作工具
2. 量子态可视化
3. 量子电路分析
4. 性能测量工具
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import time
import math

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit_aer import AerSimulator
    from qiskit.quantum_info import Statevector, DensityMatrix
    import qiskit
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


class QuantumGateLibrary:
    """量子门库"""
    
    # 单量子比特门
    SINGLE_QUBIT_GATES = {
        'I': np.array([[1, 0], [0, 1]]),
        'X': np.array([[0, 1], [1, 0]]),
        'Y': np.array([[0, -1j], [1j, 0]]),
        'Z': np.array([[1, 0], [0, -1]]),
        'H': np.array([[1, 1], [1, -1]]) / np.sqrt(2),
        'S': np.array([[1, 0], [0, 1j]]),
        'T': np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]]),
    }
    
    # 旋转门参数
    ROTATION_GATES = ['RX', 'RY', 'RZ', 'PHASE']
    
    # 双量子比特门
    TWO_QUBIT_GATES = ['CNOT', 'CZ', 'SWAP', 'ISWAP']
    
    # 三量子比特门
    THREE_QUBIT_GATES = ['TOFFOLI', 'FREDKIN']
    
    @classmethod
    def get_gate_matrix(cls, gate_name: str, params: List[float] = None) -> np.ndarray:
        """获取门矩阵"""
        if gate_name in cls.SINGLE_QUBIT_GATES:
            return cls.SINGLE_QUBIT_GATES[gate_name]
        
        if params and gate_name == 'RX':
            theta = params[0]
            return np.array([
                [np.cos(theta/2), -1j*np.sin(theta/2)],
                [-1j*np.sin(theta/2), np.cos(theta/2)]
            ])
        
        if params and gate_name == 'RY':
            theta = params[0]
            return np.array([
                [np.cos(theta/2), -np.sin(theta/2)],
                [np.sin(theta/2), np.cos(theta/2)]
            ])
        
        if params and gate_name == 'RZ':
            theta = params[0]
            return np.array([
                [np.exp(-1j*theta/2), 0],
                [0, np.exp(1j*theta/2)]
            ])
        
        if gate_name == 'CNOT':
            return np.array([[1,0,0,0], [0,1,0,0], [0,0,0,1], [0,0,1,0]])
        
        if gate_name == 'SWAP':
            return np.array([[1,0,0,0], [0,0,1,0], [0,1,0,0], [0,0,0,1]])
        
        return None
    
    @classmethod
    def list_all_gates(cls) -> Dict:
        """列出所有门"""
        return {
            'single_qubit': list(cls.SINGLE_QUBIT_GATES.keys()),
            'rotation': cls.ROTATION_GATES,
            'two_qubit': cls.TWO_QUBIT_GATES,
            'three_qubit': cls.THREE_QUBIT_GATES
        }


class QuantumStateTools:
    """量子态工具"""
    
    @staticmethod
    def create_basis_state(n_qubits: int, state_index: int) -> np.ndarray:
        """创建基态"""
        dim = 2 ** n_qubits
        state = np.zeros(dim)
        state[state_index] = 1
        return state
    
    @staticmethod
    def create_superposition_state(n_qubits: int) -> np.ndarray:
        """创建叠加态"""
        dim = 2 ** n_qubits
        return np.ones(dim) / np.sqrt(dim)
    
    @staticmethod
    def create_bell_state(bell_type: str = 'phi_plus') -> np.ndarray:
        """创建Bell态"""
        if bell_type == 'phi_plus':
            return np.array([1, 0, 0, 1]) / np.sqrt(2)
        elif bell_type == 'phi_minus':
            return np.array([1, 0, 0, -1]) / np.sqrt(2)
        elif bell_type == 'psi_plus':
            return np.array([0, 1, 1, 0]) / np.sqrt(2)
        elif bell_type == 'psi_minus':
            return np.array([0, 1, -1, 0]) / np.sqrt(2)
        return np.array([1, 0, 0, 1]) / np.sqrt(2)
    
    @staticmethod
    def compute_probability(state: np.ndarray) -> np.ndarray:
        """计算测量概率"""
        return np.abs(state) ** 2
    
    @staticmethod
    def compute_entropy(probabilities: np.ndarray) -> float:
        """计算冯诺依曼熵"""
        entropy = 0
        for p in probabilities:
            if p > 0:
                entropy -= p * np.log2(p)
        return entropy
    
    @staticmethod
    def compute_fidelity(state1: np.ndarray, state2: np.ndarray) -> float:
        """计算保真度"""
        return abs(np.vdot(state1, state2)) ** 2


class QuantumCircuitAnalyzer:
    """量子电路分析器"""
    
    def __init__(self):
        self.simulator = AerSimulator() if QISKIT_AVAILABLE else None
    
    def count_gates(self, circuit_description: Dict) -> Dict:
        """统计门数量"""
        results = {
            'total_gates': 0,
            'single_qubit': 0,
            'two_qubit': 0,
            'multi_qubit': 0,
            'depth': 0
        }
        
        gates = circuit_description.get('gates', [])
        for gate in gates:
            results['total_gates'] += 1
            n_qubits = gate.get('n_qubits', 1)
            if n_qubits == 1:
                results['single_qubit'] += 1
            elif n_qubits == 2:
                results['two_qubit'] += 1
            else:
                results['multi_qubit'] += 1
        
        results['depth'] = circuit_description.get('depth', results['total_gates'])
        
        return results
    
    def estimate_resources(self, n_qubits: int, depth: int) -> Dict:
        """估算资源需求"""
        results = {
            'n_qubits': n_qubits,
            'depth': depth,
            'state_vector_size': 2 ** n_qubits,
            'estimated_memory_mb': 0,
            'estimated_time_s': 0
        }
        
        # 内存估算（复数double）
        results['estimated_memory_mb'] = (2 ** n_qubits) * 16 / (1024 * 1024)
        
        # 时间估算（简化）
        results['estimated_time_s'] = depth * n_qubits * 0.001
        
        return results
    
    def analyze_circuit(self, n_qubits: int, gate_sequence: List[str]) -> Dict:
        """分析电路"""
        results = {
            'n_qubits': n_qubits,
            'gate_count': len(gate_sequence),
            'gates': gate_sequence,
            'gate_types': {},
            'valid': True
        }
        
        for gate in gate_sequence:
            results['gate_types'][gate] = results['gate_types'].get(gate, 0) + 1
        
        return results


class QuantumPerformanceMeasurer:
    """量子性能测量"""
    
    def __init__(self):
        self.simulator = AerSimulator() if QISKIT_AVAILABLE else None
        self.measurements = []
    
    def measure_gate_time(self, gate_name: str, n_qubits: int = 2, shots: int = 1024) -> Dict:
        """测量门执行时间"""
        results = {
            'gate': gate_name,
            'n_qubits': n_qubits,
            'shots': shots,
            'execution_time_ms': 0
        }
        
        if not QISKIT_AVAILABLE:
            return results
        
        try:
            start_time = time.time()
            
            qr = QuantumRegister(n_qubits, 'q')
            qc = QuantumCircuit(qr)
            
            # 应用门
            if gate_name == 'H':
                for i in range(n_qubits):
                    qc.h(i)
            elif gate_name == 'CNOT':
                for i in range(n_qubits - 1):
                    qc.cx(i, i + 1)
            elif gate_name == 'X':
                for i in range(n_qubits):
                    qc.x(i)
            
            cr = ClassicalRegister(n_qubits, 'c')
            qc.add_register(cr)
            qc.measure(qr, cr)
            
            job = self.simulator.run(qc, shots=shots)
            job.result()
            
            elapsed = (time.time() - start_time) * 1000
            results['execution_time_ms'] = elapsed
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def benchmark_circuit(self, n_qubits_list: List[int] = None) -> Dict:
        """基准测试"""
        if n_qubits_list is None:
            n_qubits_list = [2, 4, 6, 8]
        
        results = {
            'benchmarks': [],
            'summary': {}
        }
        
        for n_qubits in n_qubits_list:
            benchmark = {
                'n_qubits': n_qubits,
                'h_gate_time': self.measure_gate_time('H', n_qubits),
                'cnot_gate_time': self.measure_gate_time('CNOT', n_qubits)
            }
            results['benchmarks'].append(benchmark)
        
        return results
    
    def measure_fidelity(self, ideal_state: np.ndarray, actual_counts: Dict, shots: int) -> float:
        """测量保真度"""
        dim = len(ideal_state)
        actual_probs = np.zeros(dim)
        
        for state, count in actual_counts.items():
            idx = int(state, 2)
            actual_probs[idx] = count / shots
        
        ideal_probs = np.abs(ideal_state) ** 2
        
        # 保真度
        fidelity = np.sum(np.sqrt(ideal_probs * actual_probs)) ** 2
        return fidelity


class QuantumVisualizationTools:
    """量子可视化工具"""
    
    @staticmethod
    def format_state_vector(state: np.ndarray, precision: int = 4) -> List[str]:
        """格式化状态向量"""
        n_qubits = int(np.log2(len(state)))
        formatted = []
        
        for i, amplitude in enumerate(state):
            if abs(amplitude) > 1e-10:
                basis = format(i, f'0{n_qubits}b')
                formatted.append(f"|{basis}⟩: {amplitude:.{precision}f}")
        
        return formatted
    
    @staticmethod
    def format_probabilities(probabilities: np.ndarray, threshold: float = 0.01) -> List[Dict]:
        """格式化概率分布"""
        n_qubits = int(np.log2(len(probabilities)))
        results = []
        
        for i, prob in enumerate(probabilities):
            if prob > threshold:
                basis = format(i, f'0{n_qubits}b')
                results.append({
                    'state': basis,
                    'probability': prob,
                    'percentage': f"{prob * 100:.2f}%"
                })
        
        return results
    
    @staticmethod
    def create_text_histogram(probabilities: np.ndarray, width: int = 50) -> str:
        """创建文本直方图"""
        lines = []
        n_qubits = int(np.log2(len(probabilities)))
        
        for i, prob in enumerate(probabilities):
            if prob > 0.001:
                basis = format(i, f'0{n_qubits}b')
                bar_len = int(prob * width)
                bar = '█' * bar_len
                lines.append(f"|{basis}⟩ {bar} {prob:.3f}")
        
        return '\n'.join(lines)


class QuantumToolkitDemo:
    """量子工具库演示"""
    
    def __init__(self):
        self.gates = QuantumGateLibrary()
        self.state_tools = QuantumStateTools()
        self.analyzer = QuantumCircuitAnalyzer()
        self.measurer = QuantumPerformanceMeasurer()
        self.visualizer = QuantumVisualizationTools()
    
    def run_demonstration(self) -> Dict:
        """运行演示"""
        print("=" * 60)
        print("量子计算工具库演示")
        print("=" * 60)
        
        results = {
            'qiskit_available': QISKIT_AVAILABLE,
            'tests': {}
        }
        
        # 测试1：量子门库
        print("\n[1] 测试量子门库...")
        gates_list = self.gates.list_all_gates()
        results['tests']['gates'] = gates_list
        print(f"    单量子比特门: {len(gates_list['single_qubit'])}个")
        print(f"    双量子比特门: {len(gates_list['two_qubit'])}个")
        
        # 测试2：量子态工具
        print("\n[2] 测试量子态工具...")
        bell_state = self.state_tools.create_bell_state('phi_plus')
        fidelity = self.state_tools.compute_fidelity(bell_state, bell_state)
        results['tests']['state'] = {'fidelity': fidelity}
        print(f"    Bell态保真度: {fidelity:.4f}")
        
        # 测试3：电路分析
        print("\n[3] 测试电路分析...")
        resource_estimate = self.analyzer.estimate_resources(n_qubits=4, depth=10)
        results['tests']['analysis'] = resource_estimate
        print(f"    状态向量大小: {resource_estimate['state_vector_size']}")
        
        # 测试4：性能测量
        print("\n[4] 测试性能测量...")
        benchmark = self.measurer.benchmark_circuit([2, 4])
        results['tests']['benchmark'] = benchmark
        print(f"    基准测试数: {len(benchmark['benchmarks'])}")
        
        print("\n" + "=" * 60)
        print("量子工具库演示完成")
        print("=" * 60)
        
        return results


def test_quantum_toolkit():
    """测试量子工具库"""
    demo = QuantumToolkitDemo()
    results = demo.run_demonstration()
    return results


if __name__ == "__main__":
    test_quantum_toolkit()
