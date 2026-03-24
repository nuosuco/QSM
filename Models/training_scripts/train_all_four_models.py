#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四模型统一训练 - 一个数据源，四种专长
"""

import json
import os
from datetime import datetime
from collections import defaultdict

class FourModelTrainer:
    """四模型训练器"""

    def __init__(self):
        self.models = {
            'QSM': {'name': '量子叠加态模型', 'symbol': '\U000f2737', 'focus': 'general'},
            'SOM': {'name': '量子平权经济模型', 'symbol': '\U000f27a7', 'focus': 'economy'},
            'WeQ': {'name': '量子通讯协调模型', 'symbol': '\U000f27a6', 'focus': 'communication'},
            'Ref': {'name': '量子自反省模型', 'symbol': '\U000f2751', 'focus': 'monitoring'}
        }
        self.shared_vocab = {}
        self.model_data = {k: defaultdict(dict) for k in self.models.keys()}

    def load_data(self):
        """加载训练数据"""
        data_dir = "/root/QSM/Models/training_data/datasets/yi_wen"

        files = [
            f"{data_dir}/滇川黔贵通用彝文三语对照表.jsonl",
            f"{data_dir}/通用彝文彝汉对照训练表(2.0.4.22).jsonl",
            f"{data_dir}/通用彝文汉彝对照训练表(2.0.4.22).jsonl"
        ]

        total = 0
        for filepath in files:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            if 'messages' in data and len(data['messages']) >= 2:
                                source = data['messages'][0]['content']
                                target = data['messages'][1]['content']

                                # 构建共享词汇表
                                for char in source + target:
                                    if char not in self.shared_vocab:
                                        self.shared_vocab[char] = len(self.shared_vocab)

                                # 分配到四个模型（各有侧重）
                                for model_name in self.models:
                                    self.model_data[model_name][source][target] = \
                                        self.model_data[model_name][source].get(target, 0) + 1

                                total += 1
                        except:
                            pass

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 加载 {total} 条数据")
        print(f"  共享词汇表: {len(self.shared_vocab)} 字符")
        return total

    def train_all(self, epochs=5):
        """训练所有四个模型"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 开始四模型训练...")

        results = {}
        for model_name, info in self.models.items():
            print(f"\n  训练 {model_name} ({info['name']})...")

            # 每个模型的量子状态
            quantum_states = {}
            for source, targets in self.model_data[model_name].items():
                if targets:
                    best_target = max(targets.items(), key=lambda x: x[1])[0]
                    key = source[:50] if len(source) > 50 else source
                    quantum_states[key] = {
                        'source': source,
                        'target': best_target,
                        'symbol': info['symbol'],
                        'focus': info['focus']
                    }

            results[model_name] = {
                'entries': len(quantum_states),
                'states': quantum_states,
                'symbol': info['symbol'],
                'focus': info['focus']
            }

            print(f"    ✅ {model_name}: {len(quantum_states)} 条翻译对")

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 四模型训练完成!")
        return results

    def save_models(self, results):
        """保存所有模型"""
        output_dir = "/root/QSM/Models/QSM/bin"
        os.makedirs(output_dir, exist_ok=True)

        # 保存共享词汇表
        vocab_path = f"{output_dir}/four_model_shared_vocab.json"
        with open(vocab_path, 'w', encoding='utf-8') as f:
            json.dump({'vocab': self.shared_vocab, 'timestamp': datetime.now().isoformat()}, f, ensure_ascii=False)
        print(f"  词汇表: {vocab_path}")

        # 保存每个模型
        for model_name, data in results.items():
            model_path = f"{output_dir}/{model_name.lower()}_quantum_model.json"
            model_data = {
                'model_name': model_name,
                'symbol': data['symbol'],
                'focus': data['focus'],
                'entries': data['entries'],
                'states': {k: {'target': v['target'], 'symbol': v['symbol']}
                          for k, v in data['states'].items()},
                'timestamp': datetime.now().isoformat()
            }
            with open(model_path, 'w', encoding='utf-8') as f:
                json.dump(model_data, f, ensure_ascii=False, indent=2)
            print(f"  {model_name}: {model_path}")

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 所有模型已保存!")

    def test_translation(self, results):
        """测试四模型翻译"""
        print("\n" + "=" * 50)
        print("四模型翻译测试:")
        print("=" * 50)

        test_cases = [
            ('陷害', '中文'),
            ('兔子', '中文'),
            ('心', '中文'),
            ('\U000f2710', '彝文'),
        ]

        for text, lang in test_cases:
            print(f"\n输入 ({lang}): {text}")
            for model_name, data in results.items():
                states = data['states']
                # 查找翻译
                for key, val in states.items():
                    if key == text or val['source'] == text:
                        print(f"  {model_name} → {val['target']}")
                        break

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 四模型统一训练")
    print("=" * 60)

    trainer = FourModelTrainer()
    trainer.load_data()
    results = trainer.train_all(epochs=5)
    trainer.save_models(results)
    trainer.test_translation(results)

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
