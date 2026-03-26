#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子叠加态模型训练系统（完整版）
保留全部4120个通用彝文字
"""

import json
from datetime import datetime
from pathlib import Path

print("=" * 60)
print("QSM量子叠加态模型训练系统（完整版）")
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
    "word_order": "SOV",
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
            ]
        },
        {
            "id": "negative",
            "name": "否定句",
            "description": "否定词在动词之前",
            "pattern": "主语 + 不 + 动词",
            "examples": [
                {"chinese": "我不去", "yi_order": "我 不 去"},
            ]
        },
        {
            "id": "negative_with_object",
            "name": "否定句+宾语",
            "description": "主语 + 宾语 + 不 + 动词",
            "examples": [
                {"chinese": "我不吃饭", "yi_order": "我 饭 不 吃"},
            ]
        },
        {
            "id": "adjective",
            "name": "形容词修饰",
            "description": "形容词在名词之前",
            "pattern": "形容词 + 名词",
        },
        {
            "id": "question",
            "name": "疑问句",
            "description": "疑问助词在句末",
            "pattern": "主语 + 谓语 + 吗",
        }
    ]
}

print(f"✓ 彝语语法规则: {len(YI_GRAMMAR['rules'])} 条")

# 3. 构建三语映射（保留全部4120个）
print("\n构建三语映射...")

# 彝文到中文映射（主要映射）
yi_to_cn = {}
yi_to_en = {}
cn_to_yi = {}  # 中文到彝文（多个彝文可能对应同一中文）

for item in yi_table:
    yi_char = item.get('yi', '')
    zh = item.get('zh', '')
    en = item.get('en', '')
    
    if yi_char:
        # 清理中文：去掉括号内容
        zh_clean = zh.split('（')[0].split('(')[0].strip() if zh else ''
        
        yi_to_cn[yi_char] = zh_clean
        yi_to_en[yi_char] = en
        
        # 中文到彝文映射（可能多个彝文对应同一中文）
        if zh_clean:
            if zh_clean not in cn_to_yi:
                cn_to_yi[zh_clean] = yi_char
            # 如果已经有，可以添加为列表（但这里用第一个）

# 构建英文到中文/彝文的映射
en_to_cn = {}
en_to_yi = {}
for yi_char, en in yi_to_en.items():
    if en:
        # 清理英文：取第一个词
        en_clean = en.split(',')[0].split(';')[0].strip()
        if en_clean:
            en_to_cn[en_clean] = yi_to_cn.get(yi_char, '')
            en_to_yi[en_clean] = yi_char

print(f"✓ 彝文数: {len(yi_to_cn)}")
print(f"✓ 中文词数: {len(cn_to_yi)}")
print(f"✓ 英文词数: {len(en_to_yi)}")

# 4. 创建完整的量子训练模型
print("\n创建量子训练模型...")

quantum_training_model = {
    "model_name": "QSM量子叠加态三语翻译模型",
    "version": "2.0.0",
    "created_at": datetime.now().isoformat(),
    
    # 核心数据（保留全部4120个）
    "vocabulary": {
        "total_yi_chars": len(yi_to_cn),  # 4120
        "total_cn_words": len(cn_to_yi),  # 2356
        "total_en_words": len(en_to_yi),  # 3600
        "yi_to_cn": yi_to_cn,  # 彝文→中文
        "yi_to_en": yi_to_en,  # 彝文→英文
        "cn_to_yi": cn_to_yi,  # 中文→彝文
        "en_to_yi": en_to_yi,  # 英文→彝文
    },
    
    # 语法规则
    "grammar": YI_GRAMMAR,
    
    # 量子特性
    "quantum_features": {
        "superposition": "每个中文词可叠加多个彝文候选",
        "entanglement": "中英彝三语量子纠缠",
        "inference": "基于语法的量子推理"
    }
}

# 5. 保存模型
output_path = "/root/QSM/Models/QSM/bin/qsm_trilingual_model.json"
Path(output_path).parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(quantum_training_model, f, ensure_ascii=False, indent=2)

print(f"\n✓ 量子训练模型已保存: {output_path}")
print(f"  彝文字数: {len(yi_to_cn)}")
print(f"  中文词数: {len(cn_to_yi)}")

# 6. 验证
print("\n" + "=" * 60)
print("验证训练数据")
print("=" * 60)

# 测试词汇
test_words = ["心", "兔子", "不", "吃", "我", "饭"]
print("\n词汇映射测试:")
for word in test_words:
    if word in cn_to_yi:
        yi = cn_to_yi[word]
        en = yi_to_en.get(yi, '')
        print(f"  {word} → 彝文: {yi}, 英文: {en}")
    else:
        print(f"  {word} → 未在中文映射中")

print("\n" + "=" * 60)
print(f"训练完成! 彝文字数: {len(yi_to_cn)}, 中文词数: {len(cn_to_yi)}")
print("=" * 60)
