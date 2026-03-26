#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QEntL量子权重推理引擎
使用振幅和相位进行量子推理
"""

import json
import math

print("=== QEntL量子权重推理引擎 ===")

# 加载量子权重
with open('/root/QSM/Models/QSM/bin/qsm_quantum_trained_weights.json', 'r') as f:
    data = json.load(f)

neurons = data.get('neurons', {})
entanglements = data.get('entanglements', {})

# 构建hash到内容的映射
hash_to_content = {}
for content, n_data in neurons.items():
    if isinstance(n_data, dict):
        h = n_data.get('hash', '')
        if h:
            hash_to_content[h] = content

print(f"✓ 加载神经元: {len(neurons)}")
print(f"✓ 加载纠缠关系: {len(entanglements)}")
print(f"✓ Hash映射: {len(hash_to_content)}")

def quantum_inference(input_text, top_k=5):
    """量子推理 - 基于振幅和相位"""
    if input_text not in neurons:
        return None
    
    input_neuron = neurons[input_text]
    input_amp = input_neuron.get('amplitude', 0)
    input_phase = input_neuron.get('phase', 0)
    input_hash = input_neuron.get('hash', '')
    
    # 找纠缠关系
    candidates = []
    
    # 1. 直接纠缠
    if input_hash in entanglements:
        for ent_hash, strength in entanglements[input_hash].items():
            if ent_hash in hash_to_content:
                ent_content = hash_to_content[ent_hash]
                if ent_content in neurons:
                    ent_neuron = neurons[ent_content]
                    ent_amp = ent_neuron.get('amplitude', 0)
                    ent_phase = ent_neuron.get('phase', 0)
                    
                    # 量子相似度：振幅乘积 * cos(相位差)
                    phase_sim = math.cos(input_phase - ent_phase)
                    amp_sim = input_amp * ent_amp
                    score = amp_sim * phase_sim * strength
                    
                    candidates.append({
                        'content': ent_content,
                        'score': score,
                        'method': 'entanglement'
                    })
    
    # 2. 相位相似
    for content, n_data in neurons.items():
        if content == input_text:
            continue
        phase = n_data.get('phase', 0)
        amp = n_data.get('amplitude', 0)
        
        # 相位相似度
        phase_diff = abs(input_phase - phase)
        if phase_diff < math.pi / 4:  # 相位相近
            phase_sim = math.cos(phase_diff)
            score = amp * phase_sim
            candidates.append({
                'content': content,
                'score': score,
                'method': 'phase'
            })
    
    # 排序并返回
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates[:top_k]

# 测试推理
print("\n=== 量子推理测试 ===")
test_words = ['心', '水', '火', '天']
for word in test_words:
    results = quantum_inference(word)
    if results:
        print(f"\n{word} -> 推理结果:")
        for r in results[:3]:
            content = r['content']
            if len(content) > 10:
                content = content[:10] + '...'
            print(f"  {content} (score={r['score']:.4f}, method={r['method']})")
    else:
        print(f"\n{word} -> 未找到")
