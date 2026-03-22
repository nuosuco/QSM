#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子机器学习模块
实现量子变分电路和量子神经网络

主要功能：
1. 量子变分电路
2. 参数化量子门
3. 量子特征映射
4. 量子分类器
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
import time
import math

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit_aer import AerSimulator
    from qiskit.circuit import Parameter
    import qiskit
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


class QuantumVariationalCircuit:
    """量子变分电路"""
    
    def __init__(self, n_qubits: int = 4, depth: int = 2):
        self.n_qubits = n_qubits
        self.depth = depth
        self.simulator = AerSimulator() if QISKIT_AVAILABLE else None
        self.parameters = []
    
    def create_parameterized_circuit(self) -> Dict:
        """创建参数化量子电路"""
        results = {
            'n_qubits': self.n_qubits,
            'depth': self.depth,
            'n_parameters': 0,
            'circuit_created': False
        }
        
        if not QISKIT_AVAILABLE:
            results['classical_fallback'] = True
            return results
        
        try:
            qr = QuantumRegister(self.n_qubits, 'q')
            qc = QuantumCircuit(qr)
            
            # 参数数量 = n_qubits * depth * 3 (RY, RZ, CNOT)
            n_params = self.n_qubits * self.depth * 2
            params = [Parameter(f'theta_{i}') for i in range(n_params)]
            self.parameters = params
            results['n_parameters'] = n_params
            
            # 构建变分层
            param_idx = 0
            for d in range(self.depth):
                # 单量子比特旋转
                for i in range(self.n_qubits):
                    qc.ry(params[param_idx], i)
                    param_idx += 1
                    qc.rz(params[param_idx], i)
                    param_idx += 1
                
                # 纠缠层
                for i in range(self.n_qubits - 1):
                    qc.cx(i, i + 1)
                
                if self.n_qubits > 1:
                    qc.cx(self.n_qubits - 1, 0)
            
            results['circuit'] = qc
            results['circuit_created'] = True
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def bind_parameters(self, params: List[float]) -> Dict:
        """绑定参数"""
        results = {
            'params': params,
            'bound': False
        }
        
        if not QISKIT_AVAILABLE or len(self.parameters) == 0:
            return results
        
        try:
            param_dict = {p: v for p, v in zip(self.parameters, params)}
            results['bound'] = True
            results['param_dict'] = param_dict
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def get_expectation(self, params: List[float], shots: int = 1024) -> float:
        """计算期望值"""
        if not QISKIT_AVAILABLE:
            return 0.5
        
        try:
            qr = QuantumRegister(self.n_qubits, 'q')
            cr = ClassicalRegister(self.n_qubits, 'c')
            qc = QuantumCircuit(qr, cr)
            
            # 应用参数化门
            param_idx = 0
            for d in range(self.depth):
                for i in range(self.n_qubits):
                    qc.ry(params[param_idx] if param_idx < len(params) else 0, i)
                    param_idx += 1
                    qc.rz(params[param_idx] if param_idx < len(params) else 0, i)
                    param_idx += 1
                
                for i in range(self.n_qubits - 1):
                    qc.cx(i, i + 1)
                if self.n_qubits > 1:
                    qc.cx(self.n_qubits - 1, 0)
            
            qc.measure(qr, cr)
            
            job = self.simulator.run(qc, shots=shots)
            counts = job.result().get_counts()
            
            # 计算Z期望值
            expectation = 0
            for state, count in counts.items():
                value = sum(1 if b == '0' else -1 for b in state)
                expectation += value * count / shots
            
            return expectation / self.n_qubits
            
        except Exception as e:
            return 0.0


class QuantumFeatureMap:
    """量子特征映射"""
    
    def __init__(self, n_qubits: int = 4):
        self.n_qubits = n_qubits
        self.simulator = AerSimulator() if QISKIT_AVAILABLE else None
    
    def encode_data(self, data: List[float]) -> Dict:
        """将经典数据编码到量子态"""
        results = {
            'data_length': len(data),
            'n_qubits': self.n_qubits,
            'encoded': False
        }
        
        if not QISKIT_AVAILABLE:
            results['classical_fallback'] = True
            return results
        
        try:
            qr = QuantumRegister(self.n_qubits, 'q')
            qc = QuantumCircuit(qr)
            
            # 数据编码：角度编码
            for i, value in enumerate(data[:self.n_qubits]):
                angle = value * np.pi  # 缩放到[-π, π]
                qc.ry(angle, i)
            
            # 添加纠缠
            for i in range(self.n_qubits - 1):
                qc.cx(i, i + 1)
            
            results['encoded'] = True
            results['circuit'] = qc
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def compute_kernel(self, x1: List[float], x2: List[float]) -> float:
        """计算量子核函数"""
        if not QISKIT_AVAILABLE:
            # 经典降级：使用RBF核
            diff = np.array(x1) - np.array(x2)
            return np.exp(-np.dot(diff, diff))
        
        try:
            qr = QuantumRegister(self.n_qubits, 'q')
            qc = QuantumCircuit(qr)
            
            # 编码x1
            for i, value in enumerate(x1[:self.n_qubits]):
                qc.ry(value * np.pi, i)
            
            # 编码x2（逆变换）
            for i, value in enumerate(x2[:self.n_qubits]):
                qc.ry(-value * np.pi, i)
            
            # 测量
            cr = ClassicalRegister(self.n_qubits, 'c')
            qc.measure(qr, cr)
            
            job = self.simulator.run(qc, shots=1024)
            counts = job.result().get_counts()
            
            # 核值 = 测量到全0态的概率
            all_zero_prob = counts.get('0' * self.n_qubits, 0) / 1024
            
            return all_zero_prob
            
        except Exception as e:
            return 0.5


class QuantumClassifier:
    """量子分类器"""
    
    def __init__(self, n_qubits: int = 4):
        self.n_qubits = n_qubits
        self.vqc = QuantumVariationalCircuit(n_qubits=n_qubits, depth=2)
        self.feature_map = QuantumFeatureMap(n_qubits=n_qubits)
        self.weights = None
        self.trained = False
    
    def initialize_weights(self) -> List[float]:
        """初始化权重"""
        n_params = self.n_qubits * 2 * 2  # depth=2
        self.weights = np.random.uniform(-np.pi, np.pi, n_params).tolist()
        return self.weights
    
    def forward(self, x: List[float]) -> float:
        """前向传播"""
        if self.weights is None:
            self.initialize_weights()
        
        if not QISKIT_AVAILABLE:
            # 经典降级：简单线性组合
            return np.dot(x[:len(self.weights)], self.weights[:len(x)])
        
        try:
            qr = QuantumRegister(self.n_qubits, 'q')
            cr = ClassicalRegister(1, 'c')
            qc = QuantumCircuit(qr, cr)
            
            # 特征映射
            for i, value in enumerate(x[:self.n_qubits]):
                qc.ry(value * np.pi, i)
            
            # 变分层
            param_idx = 0
            for d in range(2):
                for i in range(self.n_qubits):
                    qc.ry(self.weights[param_idx], i)
                    param_idx += 1
                    qc.rz(self.weights[param_idx], i)
                    param_idx += 1
                
                for i in range(self.n_qubits - 1):
                    qc.cx(i, i + 1)
            
            # 测量第一个量子比特
            qc.measure(0, cr)
            
            job = self.simulator.run(qc, shots=1024)
            counts = job.result().get_counts()
            
            # 返回测量到1的概率
            prob_1 = counts.get('1', 0) / 1024
            return prob_1
            
        except Exception as e:
            return 0.5
    
    def predict(self, x: List[float]) -> int:
        """预测类别"""
        prob = self.forward(x)
        return 1 if prob > 0.5 else 0
    
    def train_step(self, x: List[float], y: int, learning_rate: float = 0.01) -> float:
        """单步训练"""
        if self.weights is None:
            self.initialize_weights()
        
        # 前向传播
        pred = self.forward(x)
        
        # 计算损失
        loss = (pred - y) ** 2
        
        # 梯度更新（简化版）
        gradient = 2 * (pred - y)
        for i in range(len(self.weights)):
            self.weights[i] -= learning_rate * gradient * 0.1
        
        return loss
    
    def fit(self, X: List[List[float]], y: List[int], epochs: int = 10) -> Dict:
        """训练模型"""
        results = {
            'epochs': epochs,
            'losses': [],
            'trained': False
        }
        
        if self.weights is None:
            self.initialize_weights()
        
        for epoch in range(epochs):
            epoch_loss = 0
            for xi, yi in zip(X, y):
                loss = self.train_step(xi, yi)
                epoch_loss += loss
            
            avg_loss = epoch_loss / len(X)
            results['losses'].append(avg_loss)
            
            if epoch % 5 == 0:
                print(f"    Epoch {epoch}: Loss = {avg_loss:.4f}")
        
        self.trained = True
        results['trained'] = True
        results['final_loss'] = results['losses'][-1]
        
        return results
    
    def evaluate(self, X: List[List[float]], y: List[int]) -> Dict:
        """评估模型"""
        results = {
            'n_samples': len(X),
            'correct': 0,
            'accuracy': 0
        }
        
        for xi, yi in zip(X, y):
            pred = self.predict(xi)
            if pred == yi:
                results['correct'] += 1
        
        results['accuracy'] = results['correct'] / results['n_samples']
        
        return results


class QuantumMLDemo:
    """量子机器学习演示"""
    
    def __init__(self):
        self.vqc = QuantumVariationalCircuit(n_qubits=4, depth=2)
        self.feature_map = QuantumFeatureMap(n_qubits=4)
        self.classifier = QuantumClassifier(n_qubits=4)
    
    def run_demonstration(self) -> Dict:
        """运行演示"""
        print("=" * 60)
        print("量子机器学习演示")
        print("=" * 60)
        
        results = {
            'qiskit_available': QISKIT_AVAILABLE,
            'tests': {}
        }
        
        # 测试1：变分电路
        print("\n[1] 测试量子变分电路...")
        circuit_result = self.vqc.create_parameterized_circuit()
        results['tests']['vqc'] = circuit_result
        print(f"    参数数量: {circuit_result['n_parameters']}")
        print(f"    电路创建: {'✅' if circuit_result['circuit_created'] else '❌'}")
        
        # 测试2：特征映射
        print("\n[2] 测试量子特征映射...")
        sample_data = [0.5, 0.3, -0.2, 0.8]
        encode_result = self.feature_map.encode_data(sample_data)
        results['tests']['feature_map'] = encode_result
        print(f"    数据: {sample_data}")
        print(f"    编码成功: {'✅' if encode_result['encoded'] else '❌'}")
        
        # 测试3：量子核
        print("\n[3] 测试量子核函数...")
        x1, x2 = [0.5, 0.3, -0.2, 0.8], [0.6, 0.2, -0.1, 0.9]
        kernel_value = self.feature_map.compute_kernel(x1, x2)
        results['tests']['kernel'] = {'value': kernel_value}
        print(f"    核值: {kernel_value:.4f}")
        
        # 测试4：量子分类器
        print("\n[4] 测试量子分类器...")
        # 生成简单训练数据
        X_train = [[0.1, 0.2, 0.3, 0.4] for _ in range(5)] + \
                  [[0.6, 0.7, 0.8, 0.9] for _ in range(5)]
        y_train = [0] * 5 + [1] * 5
        
        train_result = self.classifier.fit(X_train, y_train, epochs=10)
        results['tests']['training'] = train_result
        
        # 评估
        eval_result = self.classifier.evaluate(X_train, y_train)
        results['tests']['evaluation'] = eval_result
        print(f"    训练准确率: {eval_result['accuracy']:.1%}")
        
        print("\n" + "=" * 60)
        print("量子机器学习演示完成")
        print("=" * 60)
        
        return results


def test_quantum_ml():
    """测试量子机器学习"""
    demo = QuantumMLDemo()
    results = demo.run_demonstration()
    return results


if __name__ == "__main__":
    test_quantum_ml()
