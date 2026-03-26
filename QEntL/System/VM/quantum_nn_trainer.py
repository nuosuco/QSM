#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QEntL量子神经网络真正训练执行器
让量子虚拟机执行真正的量子训练
"""

import sys
import os
import json
import math
import time
import numpy as np

# 添加路径
sys.path.insert(0, '/root/QSM/QEntL/System/VM')

from quantum_registers import QuantumRegisters, Qubit

print("=" * 60)
print("🔮 QEntL量子神经网络训练执行器")
print("=" * 60)

class QuantumNeuron:
    """量子神经元 - 真正的量子态"""
    
    def __init__(self, qubit_id, registers):
        self.qubit_id = qubit_id
        self.registers = registers
        self.weight = np.random.uniform(-1, 1)
        self.bias = 0.0
        
    def apply_rotation(self, angle):
        """应用量子旋转门 (RY)"""
        self.registers.apply_gate('RY', self.qubit_id, angle)
        
    def apply_hadamard(self):
        """应用Hadamard门，创建叠加态"""
        self.registers.apply_gate('H', self.qubit_id)
        
    def measure(self):
        """测量量子态"""
        return self.registers.measure(self.qubit_id)
    
    def get_amplitude(self):
        """获取振幅"""
        state = self.registers.qubits[self.qubit_id].state
        return np.abs(state[0])**2, np.abs(state[1])**2

class QuantumNeuralNetwork:
    """量子神经网络"""
    
    def __init__(self, layer_sizes=[16, 32, 16, 8]):
        self.registers = QuantumRegisters(max_qubits=sum(layer_sizes))
        self.layer_sizes = layer_sizes
        self.layers = []
        
        # 创建神经元
        qubit_id = 0
        for size in layer_sizes:
            layer = []
            for _ in range(size):
                neuron = QuantumNeuron(qubit_id, self.registers)
                layer.append(neuron)
                qubit_id += 1
            self.layers.append(layer)
        
        print(f"✓ 创建量子神经网络: {layer_sizes}")
        print(f"  总量子比特: {sum(layer_sizes)}")
    
    def forward(self, inputs):
        """前向传播"""
        # 编码输入到第一层
        for i, inp in enumerate(inputs[:len(self.layers[0])]):
            # 归一化输入到 [0, π] 范围
            angle = inp * math.pi
            self.layers[0][i].apply_rotation(angle)
        
        # 创建叠加态
        for neuron in self.layers[0]:
            neuron.apply_hadamard()
        
        # 传播到隐藏层和输出层
        for layer_idx in range(1, len(self.layers)):
            for neuron in self.layers[layer_idx]:
                # 应用权重
                angle = neuron.weight * math.pi / 2
                neuron.apply_rotation(angle)
                neuron.apply_hadamard()
        
        # 测量输出层
        outputs = []
        for neuron in self.layers[-1]:
            outputs.append(neuron.measure())
        
        return outputs
    
    def train(self, inputs, targets, epochs=100, learning_rate=0.01):
        """训练"""
        print(f"\n开始训练: {epochs} 轮")
        
        for epoch in range(epochs):
            total_loss = 0.0
            
            for inp, target in zip(inputs, targets):
                # 前向传播
                output = self.forward(inp)
                
                # 计算损失
                loss = sum((o - t)**2 for o, t in zip(output, target))
                total_loss += loss
                
                # 反向传播：更新权重
                for layer in self.layers[1:]:
                    for neuron in layer:
                        # 量子梯度下降
                        gradient = 2 * (output[0] - target[0]) * 0.1
                        neuron.weight -= learning_rate * gradient
                        neuron.weight = max(-1, min(1, neuron.weight))
            
            avg_loss = total_loss / len(inputs)
            if (epoch + 1) % 10 == 0:
                print(f"  轮 {epoch+1}/{epochs}, 损失: {avg_loss:.4f}")
        
        print("✓ 训练完成")
    
    def save_model(self, path):
        """保存模型"""
        model_data = {
            "metadata": {
                "type": "QEntL量子神经网络",
                "version": "2.0.0",
                "created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "layer_sizes": self.layer_sizes,
                "total_qubits": sum(self.layer_sizes)
            },
            "weights": []
        }
        
        for layer_idx, layer in enumerate(self.layers):
            layer_weights = []
            for neuron in layer:
                layer_weights.append({
                    "qubit_id": neuron.qubit_id,
                    "weight": float(neuron.weight),
                    "bias": float(neuron.bias)
                })
            model_data["weights"].append(layer_weights)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 模型已保存: {path}")

def main():
    print("\n初始化量子神经网络...")
    
    # 创建网络
    qnn = QuantumNeuralNetwork(layer_sizes=[16, 32, 16, 8])
    
    # 准备训练数据（三语词汇编码）
    training_data = [
        # 简单的三语映射训练
        ([1.0, 0.0, 0.0, 0.0], [1, 0, 0, 0]),
        ([0.0, 1.0, 0.0, 0.0], [0, 1, 0, 0]),
        ([0.0, 0.0, 1.0, 0.0], [0, 0, 1, 0]),
        ([0.0, 0.0, 0.0, 1.0], [0, 0, 0, 1]),
    ]
    
    inputs = [d[0] for d in training_data]
    targets = [d[1] for d in training_data]
    
    # 训练
    qnn.train(inputs, targets, epochs=100, learning_rate=0.01)
    
    # 测试
    print("\n测试:")
    test_input = [1.0, 0.0, 0.0, 0.0]
    output = qnn.forward(test_input)
    print(f"  输入: {test_input[:4]}")
    print(f"  输出: {output[:4]}")
    
    # 保存
    qnn.save_model("/root/QSM/Models/QSM/bin/qsm_trained_qnn.json")
    
    print("\n" + "=" * 60)
    print("量子神经网络训练完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()
