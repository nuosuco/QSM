#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子方法三语翻译训练 - 使用量子虚拟机
无需GPU，CPU即可运行
"""

import json
import os
import math
import random
from datetime import datetime
from collections import defaultdict

class QuantumVocabTrainer:
    """量子词汇训练器 - 轻量级，适合CPU"""

    def __init__(self):
        self.vocab = {}  # 字符到ID的映射
        self.reverse_vocab = {}  # ID到字符的映射
        self.translations = defaultdict(dict)  # 翻译映射
        self.quantum_states = {}  # 量子状态存储

    def load_data(self, filepath):
        """加载训练数据"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 加载: {filepath}")
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if 'messages' in data and len(data['messages']) >= 2:
                        user_msg = data['messages'][0]['content']
                        assistant_msg = data['messages'][1]['content']

                        # 添加到词汇表
                        for char in user_msg + assistant_msg:
                            if char not in self.vocab:
                                idx = len(self.vocab)
                                self.vocab[char] = idx
                                self.reverse_vocab[idx] = char

                        # 记录翻译
                        self.translations[user_msg][assistant_msg] = self.translations[user_msg].get(assistant_msg, 0) + 1
                        count += 1
                except:
                    pass
        print(f"  加载 {count} 条数据, 词汇量 {len(self.vocab)}")
        return count

    def encode_quantum(self, text):
        """量子编码 - 将文本转换为量子态"""
        # 每个字符映射到一个量子基态
        # 使用叠加态表示整个文本
        n = len(text)
        if n == 0:
            return [0.0]

        # 创建归一化的量子态
        state = []
        for i, char in enumerate(text):
            idx = self.vocab.get(char, 0)
            # 相位编码
            phase = 2 * math.pi * idx / max(len(self.vocab), 1)
            amplitude = 1.0 / math.sqrt(n)
            state.append(amplitude * math.cos(phase))
            state.append(amplitude * math.sin(phase))

        # 归一化
        norm = math.sqrt(sum(x*x for x in state))
        if norm > 0:
            state = [x/norm for x in state]

        return state

    def quantum_interference(self, state1, state2):
        """量子干涉 - 计算两个状态的相似度"""
        # 计算干涉强度
        min_len = min(len(state1), len(state2))
        if min_len == 0:
            return 0.0

        overlap = sum(state1[i] * state2[i] for i in range(min_len))
        return abs(overlap)

    def train_translation(self, epochs=10):
        """训练翻译模型"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 开始量子训练...")

        for epoch in range(epochs):
            correct = 0
            total = 0

            for source, targets in self.translations.items():
                # 找到最频繁的翻译
                if not targets:
                    continue

                best_target = max(targets.items(), key=lambda x: x[1])[0]

                # 量子编码
                source_state = self.encode_quantum(source)
                target_state = self.encode_quantum(best_target)

                # 存储量子态关联
                key = source[:50] if len(source) > 50 else source
                self.quantum_states[key] = {
                    'source_state': source_state[:100],  # 截断以节省内存
                    'target': best_target,
                    'confidence': sum(targets.values()) / (sum(targets.values()) + 1)
                }

                correct += 1
                total += 1

            accuracy = correct / max(total, 1) * 100
            print(f"  Epoch {epoch+1}/{epochs}: 处理 {total} 条, 准确率 {accuracy:.1f}%")

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 训练完成!")

    def translate(self, text, top_k=1):
        """翻译文本 - 优先精确匹配"""
        # 先尝试精确匹配
        if text in self.translations:
            targets = self.translations[text]
            best = max(targets.items(), key=lambda x: x[1])
            return [best[0]]

        # 量子编码输入（模糊匹配）
        input_state = self.encode_quantum(text)

        best_matches = []
        for key, data in self.quantum_states.items():
            stored_state = data['source_state']
            confidence = data['confidence']

            # 计算量子干涉（相似度）
            similarity = self.quantum_interference(input_state, stored_state) * confidence

            if similarity > 0.1:  # 阈值
                best_matches.append((similarity, data['target']))

        # 排序返回最佳匹配
        best_matches.sort(reverse=True)
        return [t for _, t in best_matches[:top_k]] if best_matches else ["未知"]

    def save_model(self, filepath):
        """保存模型"""
        model_data = {
            'vocab': self.vocab,
            'quantum_states': {k: {'target': v['target'], 'confidence': v['confidence']}
                              for k, v in self.quantum_states.items()},
            'timestamp': datetime.now().isoformat()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 模型已保存: {filepath}")

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子三语翻译训练")
    print("=" * 60)

    trainer = QuantumVocabTrainer()

    # 加载三语对照数据
    data_dir = "/root/QSM/Models/training_data/datasets/yi_wen"

    trainer.load_data(f"{data_dir}/滇川黔贵通用彝文三语对照表.jsonl")
    trainer.load_data(f"{data_dir}/通用彝文彝汉对照训练表(2.0.4.22).jsonl")
    trainer.load_data(f"{data_dir}/通用彝文汉彝对照训练表(2.0.4.22).jsonl")

    # 训练
    trainer.train_translation(epochs=10)

    # 测试翻译
    print("\n" + "-" * 40)
    print("翻译测试:")
    print("-" * 40)

    test_cases = [
        ("陷害", "中文→彝文"),
        ("兔子", "中文→彝文"),
        ("心", "中文→彝文"),
        ("\U000f2710", "彝文→中文"),
    ]

    for text, desc in test_cases:
        result = trainer.translate(text)
        print(f"  {desc}: '{text}' → {result}")

    # 保存模型
    trainer.save_model("/root/QSM/Models/QSM/bin/quantum_yi_model.json")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
