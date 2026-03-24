#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QEntL量子动态文件系统 - 增强训练
增加训练数据和训练轮次，让模型更智能
"""

import json
import os
import hashlib
import math
import random
import time
from datetime import datetime
from typing import Dict, List, Set, Tuple
from collections import defaultdict

print("=" * 60)
print("🌟 QEntL量子神经网络 - 增强训练")
print("=" * 60)

# 路径
QSM_ROOT = "/root/QSM"
TRAINING_DATA = f"{QSM_ROOT}/Models/training_data/datasets/yi_wen/"
OUTPUT_DIR = f"{QSM_ROOT}/Models/QSM/bin/"
YI_VOCAB = f"{QSM_ROOT}/Models/QSM/bin/quantum_yi_model.json"

# 量子基因
QUANTUM_GENES = {
    "心": "\U000f2737",
    "乾坤": "\U000f2735",
    "天": "\U000f27ad",
    "火": "\U000f27ae",
    "王": "\U000f27b0"
}


class QuantumNeuron:
    """量子神经元"""
    
    def __init__(self, content: str):
        self.content = content
        self.hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        self.amplitude = 1.0
        self.phase = random.uniform(0, 2 * math.pi)
        self.superposition_states = []
        self.entangled_with = set()
        self.learning_rate = 0.1
        self.momentum = 0.9
        self.prev_update = 0
        self.access_count = 0  # 访问次数（智力指标）
    
    def quantum_state(self) -> complex:
        return self.amplitude * (math.cos(self.phase) + 1j * math.sin(self.phase))
    
    def probability(self) -> float:
        return self.amplitude ** 2
    
    def superpose(self, other_neurons: List['QuantumNeuron']):
        self.superposition_states = other_neurons
        total = math.sqrt(1 + sum(n.amplitude ** 2 for n in other_neurons))
        self.amplitude = self.amplitude / total
        for n in other_neurons:
            n.amplitude = n.amplitude / total
    
    def entangle(self, other: 'QuantumNeuron', strength: float = 1.0):
        self.entangled_with.add(other.hash)
        other.entangled_with.add(self.hash)
        avg_phase = (self.phase + other.phase) / 2
        self.phase = avg_phase + random.uniform(-0.1, 0.1)
        other.phase = avg_phase + random.uniform(-0.1, 0.1)
    
    def measure(self) -> str:
        self.access_count += 1  # 增加访问计数
        if not self.superposition_states:
            return self.content
        probs = [self.probability()]
        for n in self.superposition_states:
            probs.append(n.probability())
        total = sum(probs)
        r = random.random() * total
        cumulative = probs[0]
        if r < cumulative:
            return self.content
        for i, n in enumerate(self.superposition_states):
            cumulative += probs[i + 1]
            if r < cumulative:
                n.access_count += 1
                return n.content
        return self.content
    
    def learn(self, target_amplitude: float, target_phase: float):
        amp_update = self.learning_rate * (target_amplitude - self.amplitude)
        self.amplitude += amp_update + self.momentum * self.prev_update
        self.prev_update = amp_update
        phase_diff = target_phase - self.phase
        while phase_diff > math.pi:
            phase_diff -= 2 * math.pi
        while phase_diff < -math.pi:
            phase_diff += 2 * math.pi
        self.phase += self.learning_rate * phase_diff
        self.amplitude = max(0.01, min(1.0, self.amplitude))


class QuantumDynamicFilesystemNN:
    """量子动态文件系统神经网络"""
    
    def __init__(self):
        self.neurons: Dict[str, QuantumNeuron] = {}
        self.entanglement_matrix = defaultdict(dict)
        self.training_history = []
        print(f"\n📁 初始化量子神经网络")
    
    def load_all_data(self) -> List[Tuple[str, str]]:
        """加载所有训练数据"""
        print(f"\n📊 加载训练数据...")
        data = []
        
        # 加载三语对照表
        data_file = f"{TRAINING_DATA}滇川黔贵通用彝文三语对照表.jsonl"
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line)
                    if 'messages' in item and len(item['messages']) >= 2:
                        chinese = item['messages'][0].get('content', '')
                        yi = item['messages'][1].get('content', '')
                        if chinese and yi:
                            data.append((chinese, yi))
                except:
                    pass
        
        # 加载彝汉对照
        data_file2 = f"{TRAINING_DATA}通用彝文彝汉对照训练表(2.0.4.22).jsonl"
        with open(data_file2, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line)
                    if 'messages' in item and len(item['messages']) >= 2:
                        chinese = item['messages'][0].get('content', '')
                        yi = item['messages'][1].get('content', '')
                        if chinese and yi:
                            data.append((chinese, yi))
                except:
                    pass
        
        # 加载完整词汇表作为额外训练数据
        with open(YI_VOCAB, 'r', encoding='utf-8') as f:
            yi_data = json.load(f)
            for yi_char, info in yi_data.get('quantum_states', {}).items():
                target = info.get('target', '')
                cn_part = target.split('|')[0].strip()
                if cn_part and yi_char:
                    data.append((cn_part, yi_char))
        
        print(f"   总训练样本: {len(data)} 条")
        return data
    
    def initialize_quantum_weights(self, training_data: List[Tuple[str, str]]):
        """初始化量子权重"""
        print(f"\n⚛️ 初始化量子权重...")
        
        for chinese, yi in training_data:
            if chinese not in self.neurons:
                self.neurons[chinese] = QuantumNeuron(chinese)
            if yi not in self.neurons:
                self.neurons[yi] = QuantumNeuron(yi)
            
            self.neurons[chinese].entangle(self.neurons[yi])
            h1 = self.neurons[chinese].hash
            h2 = self.neurons[yi].hash
            self.entanglement_matrix[h1][h2] = 1.0
            self.entanglement_matrix[h2][h1] = 1.0
        
        print(f"   创建神经元: {len(self.neurons)} 个")
        print(f"   纠缠关系: {len(self.entanglement_matrix)} 组")
    
    def quantum_parallel_training(self, epochs: int = 20):
        """量子并行训练 - 增加轮次"""
        print(f"\n🌀 开始量子并行训练 ({epochs} 轮)...")
        
        start_time = time.time()
        
        for epoch in range(epochs):
            epoch_loss = 0
            
            for content, neuron in self.neurons.items():
                neighbors = []
                for h in neuron.entangled_with:
                    for c, n in self.neurons.items():
                        if n.hash == h:
                            neighbors.append(n)
                            break
                
                if neighbors:
                    neuron.superpose(neighbors[:3])
                
                # 根据访问次数调整目标（智力体现）
                # 越多被访问，振幅应该越高
                base_amp = 0.5
                intelligence_bonus = min(0.3, neuron.access_count * 0.01)
                target_amp = min(1.0, base_amp + intelligence_bonus)
                target_phase = math.pi / 4
                
                neuron.learn(target_amp, target_phase)
                epoch_loss += (target_amp - neuron.amplitude) ** 2
            
            avg_loss = epoch_loss / len(self.neurons)
            self.training_history.append({
                'epoch': epoch + 1,
                'loss': avg_loss,
                'time': time.time() - start_time
            })
            
            if (epoch + 1) % 5 == 0:
                print(f"   Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.6f}")
        
        print(f"\n✓ 训练完成，用时: {time.time() - start_time:.2f}秒")
    
    def save_quantum_weights(self):
        """保存量子权重"""
        print(f"\n💾 保存量子权重...")
        
        weights = {
            'metadata': {
                'type': 'QEntL量子权重文件',
                'version': '2.0.0',
                'created': datetime.now().isoformat(),
                'neuron_count': len(self.neurons),
                'quantum_genes': QUANTUM_GENES,
                'training_history': self.training_history[-10:]
            },
            'neurons': {},
            'entanglements': dict(self.entanglement_matrix)
        }
        
        for content, neuron in self.neurons.items():
            weights['neurons'][content] = {
                'hash': neuron.hash,
                'amplitude': neuron.amplitude,
                'phase': neuron.phase,
                'probability': neuron.probability(),
                'quantum_state': str(neuron.quantum_state()),
                'entangled_count': len(neuron.entangled_with),
                'intelligence': neuron.access_count  # 智力指标
            }
        
        output_path = f"{OUTPUT_DIR}qsm_quantum_trained_weights.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(weights, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 已保存: {output_path}")
        print(f"   文件大小: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
        
        return output_path


# 主训练
if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"QEntL量子神经网络 - 增强训练")
    print(f"{'='*60}")
    
    qnn = QuantumDynamicFilesystemNN()
    training_data = qnn.load_all_data()
    qnn.initialize_quantum_weights(training_data)
    
    # 增加训练轮次到20轮
    qnn.quantum_parallel_training(epochs=20)
    
    weights_file = qnn.save_quantum_weights()
    
    print(f"\n🧪 测试翻译:")
    test_words = ['心', '天', '火', '你好', '做饭', '人', '是']
    for word in test_words:
        if word in qnn.neurons:
            neuron = qnn.neurons[word]
            result = neuron.measure()
            print(f"   {word} -> {result} (智力: {neuron.access_count})")
        else:
            print(f"   {word} -> 未训练")
    
    print(f"\n{'='*60}")
    print(f"增强训练完成！")
    print(f"{'='*60}")
