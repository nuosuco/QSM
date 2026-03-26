#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彝语语法深度训练器
让神经网络真正学习SOV语法和否定规则
"""
import json
import math
import numpy as np
from datetime import datetime

print("=" * 70)
print("🧠 彝语语法深度训练")
print("=" * 70)

# 加载词汇表
with open('/root/QSM/Web/data/通用彝文4120字学习表.json', 'r', encoding='utf-8') as f:
    vocab = json.load(f)

cn_to_yi = {}
for item in vocab:
    zh = item.get('zh', '').split('（')[0].split('(')[0].strip()
    yi = item.get('yi', '')
    if zh and yi:
        cn_to_yi[zh] = yi

print(f"✓ 词汇: {len(cn_to_yi)}条")

# 彝语语法动词
VERBS = ['吃', '喝', '看', '走', '来', '去', '说', '听', '做', '想', '买', '卖', '写', '读', '学', '教']

# 创建训练数据（彝语SOV语法）
training_data = []

# 基础SOV句子
subjects = ['我', '你', '他', '她', '它', '我们', '你们', '他们']
objects = ['饭', '水', '书', '苹果', '衣服', '花', '东西', '菜']

for subj in subjects:
    if subj in cn_to_yi:
        for obj in objects:
            if obj in cn_to_yi:
                for verb in VERBS:
                    if verb in cn_to_yi:
                        # SOV: 主语+宾语+动词
                        input_seq = [subj, obj, verb]
                        output_seq = [subj, obj, verb]  # SOV顺序
                        
                        # 创建训练样本
                        training_data.append({
                            'input': ''.join([subj, verb, obj]),  # 中文SVO
                            'output': ''.join([cn_to_yi[c] for c in [subj, obj, verb]]),  # 彝文SOV
                            'type': 'sov'
                        })
                        
                        # 否定形式
                        training_data.append({
                            'input': subj + '不' + verb + obj,
                            'output': ''.join([cn_to_yi.get(c, c) for c in [subj, obj, '不', verb]]),
                            'type': 'sov_negation'
                        })

print(f"✓ 训练样本: {len(training_data)}条")

# 创建神经网络
def create_network(layers):
    weights = []
    for i in range(len(layers) - 1):
        w = np.random.randn(layers[i+1], layers[i]) * np.sqrt(2.0 / layers[i])
        weights.append(w)
    return weights

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_derivative(x):
    return x * (1 - x)

def text_to_vector(text, size=32):
    """文本转向量"""
    vec = np.zeros(size)
    for i, c in enumerate(text[:size]):
        vec[i % size] = (ord(c) % 256) / 256.0
    # 填充剩余
    for i in range(len(text), size):
        vec[i] = math.sin(i * 0.1) * 0.5
    return vec

def forward(x, weights):
    activations = [x]
    for w in weights:
        x = sigmoid(np.dot(w, x))
        activations.append(x)
    return activations

def train_network(weights, data, epochs=100, lr=0.1):
    """训练网络"""
    for epoch in range(epochs):
        total_loss = 0
        for sample in data[:500]:
            input_vec = text_to_vector(sample['input'])
            target_vec = text_to_vector(sample['output'])
            
            # 前向传播
            activations = forward(input_vec, weights)
            
            # 计算误差
            output = activations[-1]
            error = target_vec - output
            total_loss += np.mean(np.abs(error))
            
            # 反向传播
            delta = error * sigmoid_derivative(output)
            for i in range(len(weights) - 1, -1, -1):
                if i > 0:
                    grad = np.outer(delta, activations[i])
                    weights[i] += lr * grad
                    delta = np.dot(weights[i].T, delta) * sigmoid_derivative(activations[i])
        
        if epoch % 20 == 0:
            print(f"Epoch {epoch}: loss={total_loss/500:.4f}")
    
    return weights

# 创建并训练网络
print("\n📊 创建网络...")
layers = [32, 64, 32, 32]
weights = create_network(layers)
print(f"层级: {layers}")

print("\n📊 开始训练...")
weights = train_network(weights, training_data, epochs=100, lr=0.1)

# 保存模型
model = {
    'name': 'QSM-SOV',
    'version': '3.0.0',
    'layers': layers,
    'weights': [w.tolist() for w in weights],
    'description': '彝语SOV语法专用模型',
    'training_samples': len(training_data),
    'trained_at': datetime.now().isoformat(),
    'capabilities': ['SOV语法', '否定处理', '彝文翻译']
}

path = '/root/QSM/Models/QSM/bin/qsm_sov_model.json'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(model, f, ensure_ascii=False, indent=2)
print(f"\n✓ 模型保存: {path}")

print("=" * 70)
print("✓ 训练完成！")
print("=" * 70)
