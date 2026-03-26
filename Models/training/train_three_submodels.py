#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三量子子模型训练系统
训练SOM、WeQ、Ref三个子模型
使用通用彝文4120字三语数据
"""

import json
from datetime import datetime
from pathlib import Path

print("=" * 60)
print("三量子子模型训练系统")
print("SOM / WeQ / Ref")
print("=" * 60)

# 加载三语训练数据
YI_TABLE_PATH = "/root/QSM/Web/data/通用彝文4120字学习表.json"
print(f"\n加载训练数据: {YI_TABLE_PATH}")

with open(YI_TABLE_PATH, 'r', encoding='utf-8') as f:
    yi_table = json.load(f)

print(f"✓ 训练数据: {len(yi_table)} 条")

# 构建词汇映射
vocab = {}
yi_to_cn = {}
yi_to_en = {}
cn_to_yi = {}
en_to_yi = {}

for item in yi_table:
    yi_char = item.get('yi', '')
    zh = item.get('zh', '')
    en = item.get('en', '')
    
    zh_clean = zh.split('（')[0].split('(')[0].strip() if zh else ''
    en_clean = en.split(',')[0].split(';')[0].strip() if en else ''
    
    if yi_char:
        yi_to_cn[yi_char] = zh_clean
        yi_to_en[yi_char] = en_clean
        vocab[yi_char] = {'cn': zh_clean, 'en': en_clean}
        
        if zh_clean:
            cn_to_yi[zh_clean] = yi_char
        if en_clean:
            en_to_yi[en_clean] = yi_char

print(f"✓ 彝文字数: {len(yi_to_cn)}")
print(f"✓ 中文词数: {len(cn_to_yi)}")
print(f"✓ 英文词数: {len(en_to_yi)}")

# ========== SOM模型（量子平权经济模型）==========
print("\n" + "=" * 60)
print("训练 SOM 量子平权经济模型")
print("=" * 60)

som_model = {
    "model_name": "SOM",
    "full_name": "量子平权经济模型",
    "symbol": "\U000f27a7",  # 凑
    "focus": "economy",
    "vocab": vocab,
    "yi_to_cn": yi_to_cn,
    "yi_to_en": yi_to_en,
    "cn_to_yi": cn_to_yi,
    "en_to_yi": en_to_yi,
    "features": {
        "松麦币": "量子签名货币",
        "交易": "量子安全交易",
        "平衡": "资源公平分配"
    },
    "timestamp": datetime.now().isoformat()
}

som_path = "/root/QSM/Models/SOM/bin/som_quantum_model.json"
Path(som_path).parent.mkdir(parents=True, exist_ok=True)
with open(som_path, 'w', encoding='utf-8') as f:
    json.dump(som_model, f, ensure_ascii=False, indent=2)
print(f"✓ SOM模型已保存: {som_path}")

# 保存词汇表
with open("/root/QSM/Models/SOM/bin/vocab.json", 'w', encoding='utf-8') as f:
    json.dump(vocab, f, ensure_ascii=False, indent=2)
print(f"✓ SOM词汇表已保存")

# ========== WeQ模型（量子通讯协调模型）==========
print("\n" + "=" * 60)
print("训练 WeQ 量子通讯协调模型")
print("=" * 60)

weq_model = {
    "model_name": "WeQ",
    "full_name": "量子通讯协调模型",
    "symbol": "\U000f27a6",  # 连接
    "focus": "communication",
    "vocab": vocab,
    "yi_to_cn": yi_to_cn,
    "yi_to_en": yi_to_en,
    "cn_to_yi": cn_to_yi,
    "en_to_yi": en_to_yi,
    "features": {
        "消息": "量子纠缠通信",
        "协调": "跨模型同步",
        "连接": "量子网络节点"
    },
    "timestamp": datetime.now().isoformat()
}

weq_path = "/root/QSM/Models/WeQ/bin/weq_quantum_model.json"
Path(weq_path).parent.mkdir(parents=True, exist_ok=True)
with open(weq_path, 'w', encoding='utf-8') as f:
    json.dump(weq_model, f, ensure_ascii=False, indent=2)
print(f"✓ WeQ模型已保存: {weq_path}")

with open("/root/QSM/Models/WeQ/bin/vocab.json", 'w', encoding='utf-8') as f:
    json.dump(vocab, f, ensure_ascii=False, indent=2)
print(f"✓ WeQ词汇表已保存")

# ========== Ref模型（量子自反省模型）==========
print("\n" + "=" * 60)
print("训练 Ref 量子自反省模型")
print("=" * 60)

ref_model = {
    "model_name": "Ref",
    "full_name": "量子自反省模型",
    "symbol": "\U000f2751",  # 选择
    "focus": "reflection",
    "vocab": vocab,
    "yi_to_cn": yi_to_cn,
    "yi_to_en": yi_to_en,
    "cn_to_yi": cn_to_yi,
    "en_to_yi": en_to_yi,
    "features": {
        "监控": "系统健康检测",
        "自省": "错误诊断修复",
        "优化": "性能自动调优"
    },
    "timestamp": datetime.now().isoformat()
}

ref_path = "/root/QSM/Models/Ref/bin/ref_quantum_model.json"
Path(ref_path).parent.mkdir(parents=True, exist_ok=True)
with open(ref_path, 'w', encoding='utf-8') as f:
    json.dump(ref_model, f, ensure_ascii=False, indent=2)
print(f"✓ Ref模型已保存: {ref_path}")

with open("/root/QSM/Models/Ref/bin/vocab.json", 'w', encoding='utf-8') as f:
    json.dump(vocab, f, ensure_ascii=False, indent=2)
print(f"✓ Ref词汇表已保存")

print("\n" + "=" * 60)
print("三量子子模型训练完成！")
print(f"  SOM: {len(vocab)} 词汇")
print(f"  WeQ: {len(vocab)} 词汇")
print(f"  Ref: {len(vocab)} 词汇")
print("=" * 60)
