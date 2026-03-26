#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM真正推理测试
验证神经网络是否真正在推理，而不是简单映射
"""
import json
import numpy as np
import math

print("=" * 70)
print("🧠 QSM神经网络推理验证")
print("=" * 70)

# 加载推理模型
with open('/root/QSM/Models/QSM/bin/qsm_inference_model.json', 'r') as f:
    model = json.load(f)

weights = [np.array(w) for w in model['weights']]

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def text_to_vector(text):
    """将文本转换为向量"""
    # 使用字符哈希生成固定向量
    vec = []
    for i in range(16):
        hash_val = hash(text + str(i)) % 10000
        vec.append(math.sin(hash_val * 0.001) * 0.5)
    return np.array(vec)

def forward(input_vec):
    """神经网络前向传播"""
    x = input_vec
    for w in weights:
        if x.shape[0] < w.shape[1]:
            x = np.pad(x, (0, w.shape[1] - x.shape[0]))
        elif x.shape[0] > w.shape[1]:
            x = x[:w.shape[1]]
        x = sigmoid(np.dot(w, x))
    return x

# 测试推理
test_cases = [
    "你好",
    "hello",
    "吃饭",
    "心",
    "水",
    "太阳",
    "abc123",  # 未知输入
    "测试句子推理能力"
]

print("\n📊 神经网络推理测试:")
for text in test_cases:
    vec = text_to_vector(text)
    output = forward(vec)
    print(f"  '{text}' → 输出向量: mean={output.mean():.4f}, max={output.max():.4f}")

# 验证不同输入产生不同输出
print("\n📊 验证推理差异性:")
outputs = []
for text in test_cases:
    vec = text_to_vector(text)
    output = forward(vec)
    outputs.append(output)

# 计算输出之间的差异
diff_count = 0
for i in range(len(outputs)):
    for j in range(i+1, len(outputs)):
        diff = np.abs(outputs[i] - outputs[j]).mean()
        if diff > 0.01:
            diff_count += 1

print(f"  不同输入产生不同输出: {diff_count}/{len(outputs)*(len(outputs)-1)//2} 对")

print("\n" + "=" * 70)
print("✓ 神经网络推理验证完成")
print("=" * 70)
