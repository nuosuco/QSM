#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强训练 - 更多动词和句型
"""
import json
import math
import numpy as np
from datetime import datetime

print("=" * 60)
print("🧠 增强训练 - 扩展动词和句型")
print("=" * 60)

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

# 扩展动词列表
VERBS = ['吃', '喝', '看', '走', '来', '去', '说', '听', '做', '想',
         '买', '卖', '写', '读', '学', '教', '煮', '炒', '洗', '穿',
         '睡', '玩', '用', '送', '拿', '打', '跑', '跳', '唱', '画',
         '坐', '站', '住', '放', '拿', '找', '问', '答', '等', '爱']

# 更多主语和宾语
subjects = ['我', '你', '他', '她', '它', '我们', '你们', '他们', '大家', '谁']
objects = ['饭', '水', '书', '苹果', '衣服', '花', '菜', '茶', '酒', '肉',
           '电影', '音乐', '学校', '家', '路', '车', '电话', '信', '事', '工作']

def text_to_vec(text):
    vec = []
    for i in range(32):
        if i < len(text):
            vec.append((ord(text[i]) % 1000) / 1000.0)
        else:
            vec.append(0.0)
    return np.array(vec)

# 创建训练数据
training_data = []
for subj in subjects:
    if subj not in cn_to_yi:
        continue
    for obj in objects:
        if obj not in cn_to_yi:
            continue
        for verb in VERBS:
            if verb not in cn_to_yi:
                continue
            
            # SOV: 主语+宾语+动词
            svo = subj + verb + obj
            sov = cn_to_yi[subj] + cn_to_yi[obj] + cn_to_yi[verb]
            training_data.append({
                'input': svo,
                'output': sov,
                'input_vec': text_to_vec(svo),
                'output_vec': text_to_vec(sov)
            })
            
            # 否定
            if '不' in cn_to_yi:
                neg_svo = subj + '不' + verb + obj
                neg_sov = cn_to_yi[subj] + cn_to_yi[obj] + cn_to_yi['不'] + cn_to_yi[verb]
                training_data.append({
                    'input': neg_svo,
                    'output': neg_sov,
                    'input_vec': text_to_vec(neg_svo),
                    'output_vec': text_to_vec(neg_sov)
                })

print(f"✓ 训练样本: {len(training_data)}条")

# 加载现有模型
try:
    with open('/root/QSM/Models/QSM/bin/qsm_sov_model.json', 'r') as f:
        model = json.load(f)
    weights = [np.array(w) for w in model['weights']]
    print(f"✓ 加载现有模型继续训练")
except:
    # 创建新网络
    layers = [32, 64, 32, 32]
    weights = []
    for i in range(len(layers) - 1):
        w = np.random.randn(layers[i+1], layers[i]) * 0.5
        weights.append(w)
    print(f"✓ 创建新网络: {layers}")

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_deriv(x):
    return x * (1 - x)

# 训练
print("\n📊 训练中...")
lr = 0.1
for epoch in range(300):
    total_loss = 0
    for sample in training_data:
        x = sample['input_vec']
        y_target = sample['output_vec']
        
        activations = [x]
        for w in weights:
            x = sigmoid(np.dot(w, x))
            activations.append(x)
        
        error = y_target - activations[-1]
        total_loss += np.mean(error ** 2)
        
        delta = error * sigmoid_deriv(activations[-1])
        for i in range(len(weights) - 1, -1, -1):
            grad = np.outer(delta, activations[i])
            weights[i] += lr * grad
            if i > 0:
                delta = np.dot(weights[i].T, delta) * sigmoid_deriv(activations[i])
    
    if epoch % 60 == 0:
        print(f"Epoch {epoch}: loss={total_loss/len(training_data):.6f}")

# 保存
model = {
    'name': 'QSM-SOV-Enhanced',
    'version': '5.0.0',
    'layers': [32, 64, 32, 32],
    'weights': [w.tolist() for w in weights],
    'verbs': VERBS,
    'sov_rule': '主语+宾语+动词',
    'negation_rule': '否定词在动词前',
    'training_samples': len(training_data),
    'trained_at': datetime.now().isoformat(),
    'description': '增强版SOV模型，更多动词和句型'
}

with open('/root/QSM/Models/QSM/bin/qsm_sov_model.json', 'w', encoding='utf-8') as f:
    json.dump(model, f, ensure_ascii=False, indent=2)

print(f"\n✓ 模型保存，动词数: {len(VERBS)}")
print("=" * 60)
