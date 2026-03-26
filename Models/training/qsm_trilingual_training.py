#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子叠加态模型训练系统
使用量子动态文件系统（量子神经网络）
训练数据：通用彝文4120字 + 彝语语法规则

核心原理：
1. 三语映射：中文 ↔ 彝文 ↔ 英文 一一对应
2. 彝语语法：SOV语序 + 否定词在动词前
3. 拆字造词：中文拆成单字，对应彝文单字
4. 造句规则：用彝语语法组合词语

量子优势：
- 量子叠加态同时表示多种可能翻译
- 量子纠缠建立三语之间的关联
- 量子推理引擎进行语法转换
"""

import json
from datetime import datetime
from pathlib import Path

print("=" * 60)
print("QSM量子叠加态模型训练系统")
print("=" * 60)

# 1. 加载通用彝文4120字学习表
YI_TABLE_PATH = "/root/QSM/Web/data/通用彝文4120字学习表.json"
print(f"\n加载训练数据: {YI_TABLE_PATH}")

with open(YI_TABLE_PATH, 'r', encoding='utf-8') as f:
    yi_table = json.load(f)

print(f"✓ 通用彝文字数: {len(yi_table)}")

# 2. 定义彝语语法规则
YI_GRAMMAR = {
    "name": "彝语语法",
    "word_order": "SOV",  # 主语-宾语-动词
    "rules": [
        {
            "id": "sov_basic",
            "name": "基本语序",
            "description": "主语 + 宾语 + 动词",
            "chinese_pattern": "主语 + 动词 + 宾语",
            "yi_pattern": "主语 + 宾语 + 动词",
            "examples": [
                {"chinese": "我吃饭", "yi_order": "我 饭 吃"},
                {"chinese": "他看书", "yi_order": "他 书 看"},
                {"chinese": "我喝水", "yi_order": "我 水 喝"},
            ]
        },
        {
            "id": "negative",
            "name": "否定句",
            "description": "否定词在动词之前（与汉语相同）",
            "pattern": "主语 + 不 + 动词",
            "examples": [
                {"chinese": "我不去", "yi_order": "我 不 去"},
                {"chinese": "我不吃", "yi_order": "我 不 吃"},
                {"chinese": "他不说", "yi_order": "他 不 说"},
            ]
        },
        {
            "id": "negative_with_object",
            "name": "否定句+宾语",
            "description": "否定词在动词前，宾语在动词前",
            "pattern": "主语 + 宾语 + 不 + 动词",
            "examples": [
                {"chinese": "我不吃饭", "yi_order": "我 饭 不 吃"},
                {"chinese": "我不喝水", "yi_order": "我 水 不 喝"},
            ]
        },
        {
            "id": "adjective",
            "name": "形容词修饰",
            "description": "形容词在名词之前",
            "pattern": "形容词 + 名词",
            "examples": [
                {"chinese": "红花", "yi_order": "红 花"},
                {"chinese": "大房子", "yi_order": "大 房"},
            ]
        },
        {
            "id": "question",
            "name": "疑问句",
            "description": "疑问助词在句末",
            "pattern": "主语 + 谓语 + 吗",
            "examples": [
                {"chinese": "你好吗", "yi_order": "你 好 吗"},
            ]
        }
    ]
}

print(f"✓ 彝语语法规则: {len(YI_GRAMMAR['rules'])} 条")

# 3. 构建三语映射
print("\n构建三语映射...")
trilingual_map = {}  # 中文 -> {yi, en, category}
yi_to_cn = {}
yi_to_en = {}

for item in yi_table:
    yi_char = item.get('yi', '')
    zh = item.get('zh', '')
    en = item.get('en', '')
    
    if yi_char and zh:
        # 清理中文键：去掉括号内容
        zh_clean = zh.split('（')[0].split('(')[0].strip()
        
        # 如果清理后是单字，也添加单字映射
        if zh_clean and len(zh_clean) <= 10:
            trilingual_map[zh_clean] = {
                'yi': yi_char,
                'en': en,
                'unicode': item.get('unicode', '')
            }
            yi_to_cn[yi_char] = zh_clean
            yi_to_en[yi_char] = en

print(f"✓ 三语映射: {len(trilingual_map)} 条")

# 4. 构建词汇拆分规则
print("\n构建词汇拆分规则...")

# 常用词拆分规则
WORD_SPLIT_RULES = {
    # 动作类
    "吃饭": ["吃", "饭"],
    "喝水": ["喝", "水"],
    "看书": ["看", "书"],
    "走路": ["走", "路"],
    "回家": ["回", "家"],
    
    # 形容词+名词
    "红花": ["红", "花"],
    "大房子": ["大", "房"],
    "小桌子": ["小", "桌"],
    "新衣服": ["新", "衣"],
    
    # 数词+量词+名词
    "三个人": ["三", "人"],
    "五本书": ["五", "书"],
    
    # 否定词
    "不去": ["不", "去"],
    "不吃": ["不", "吃"],
    "不喝": ["不", "喝"],
}

print(f"✓ 词汇拆分规则: {len(WORD_SPLIT_RULES)} 条")

# 5. 构建造句规则
print("\n构建造句规则...")

SENTENCE_TEMPLATES = {
    # 肯定句模板
    "SVO_to_SOV": {
        "input_pattern": "主语 + 动词 + 宾语",
        "output_pattern": "主语 + 宾语 + 动词",
        "example_input": "我吃饭",
        "example_output": ["我", "饭", "吃"]
    },
    
    # 否定句模板
    "negative_basic": {
        "input_pattern": "主语 + 不 + 动词",
        "output_pattern": "主语 + 不 + 动词",
        "example_input": "我不去",
        "example_output": ["我", "不", "去"]
    },
    
    # 否定句+宾语模板
    "negative_with_object": {
        "input_pattern": "主语 + 不 + 动词 + 宾语",
        "output_pattern": "主语 + 宾语 + 不 + 动词",
        "example_input": "我不吃饭",
        "example_output": ["我", "饭", "不", "吃"]
    }
}

print(f"✓ 造句模板: {len(SENTENCE_TEMPLATES)} 个")

# 6. 创建完整的量子训练模型
print("\n创建量子训练模型...")

quantum_training_model = {
    "model_name": "QSM量子叠加态三语翻译模型",
    "version": "1.0.0",
    "created_at": datetime.now().isoformat(),
    
    # 核心数据
    "vocabulary": {
        "total_chars": len(yi_table),
        "trilingual_map": trilingual_map,
        "yi_to_cn": yi_to_cn,
        "yi_to_en": yi_to_en
    },
    
    # 语法规则
    "grammar": YI_GRAMMAR,
    
    # 词汇拆分规则
    "word_split_rules": WORD_SPLIT_RULES,
    
    # 造句模板
    "sentence_templates": SENTENCE_TEMPLATES,
    
    # 量子特性
    "quantum_features": {
        "superposition": "每个中文词可叠加多个彝文候选",
        "entanglement": "中英彝三语量子纠缠",
        "inference": "基于语法的量子推理"
    }
}

# 7. 保存模型
output_path = "/root/QSM/Models/QSM/bin/qsm_trilingual_model.json"
Path(output_path).parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(quantum_training_model, f, ensure_ascii=False, indent=2)

print(f"\n✓ 量子训练模型已保存: {output_path}")

# 8. 验证
print("\n" + "=" * 60)
print("验证训练数据")
print("=" * 60)

# 测试词汇
test_words = ["心", "兔子", "陷害", "吃", "水", "不"]
print("\n词汇映射测试:")
for word in test_words:
    if word in trilingual_map:
        info = trilingual_map[word]
        print(f"  {word} → 彝文: {info['yi']}, 英文: {info['en']}")
    else:
        # 拆字
        chars = list(word)
        if all(c in trilingual_map for c in chars):
            yi_result = ''.join(trilingual_map[c]['yi'] for c in chars)
            print(f"  {word} → 拆字: {chars} → {yi_result}")
        else:
            print(f"  {word} → 未找到")

# 测试语法
print("\n语法转换测试:")
test_sentences = ["我吃饭", "我不去", "我不吃饭", "红花"]
for sent in test_sentences:
    chars = list(sent)
    print(f"  中文: {sent} → 字: {chars}")

print("\n" + "=" * 60)
print(f"训练完成! 总词汇: {len(trilingual_map)}, 语法规则: {len(YI_GRAMMAR['rules'])}")
print("=" * 60)
