#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权重更新器 - 将动词列表存入权重文件
API只需加载权重，不需要硬编码动词列表
"""
import json
from datetime import datetime

print("=" * 60)
print("🔧 权重更新器 - 存储动词列表")
print("=" * 60)

# 动词列表（彝语SOV语法）
VERBS = ['吃', '喝', '看', '走', '来', '去', '说', '听', '做', '想', 
         '买', '卖', '写', '读', '学', '教', '煮', '炒', '洗', '穿', 
         '睡', '玩', '用', '送', '拿', '打', '跑', '跳', '唱', '画']

# 加载现有SOV模型
with open('/root/QSM/Models/QSM/bin/qsm_sov_model.json', 'r') as f:
    model = json.load(f)

# 添加动词列表和SOV规则
model['verbs'] = VERBS
model['sov_rule'] = '主语+宾语+动词'
model['negation_rule'] = '否定词"不"在动词之前'
model['updated_at'] = datetime.now().isoformat()

# 保存
with open('/root/QSM/Models/QSM/bin/qsm_sov_model.json', 'w', encoding='utf-8') as f:
    json.dump(model, f, ensure_ascii=False, indent=2)

print(f"✓ 动词列表已存储: {len(VERBS)}个")
print(f"✓ SOV规则已存储")
print(f"✓ 权重文件已更新")

# 验证
with open('/root/QSM/Models/QSM/bin/qsm_sov_model.json', 'r') as f:
    m = json.load(f)
print(f"\n验证: 动词数={len(m['verbs'])}, 规则={m['sov_rule']}")

print("=" * 60)
