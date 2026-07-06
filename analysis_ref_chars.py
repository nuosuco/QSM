#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""参考集字符统计：重复字符分析"""
import json
from collections import Counter

REF = "/root/QSM/data/滇川黔贵通用彝文三语对照表.jsonl"

def yi_set(s):
    return [c for c in s if '\U000F2700' <= c <= '\U000F344F']

chars = Counter()
empty_lines = 0
valid = 0
no_meta_yi = 0
lines = 0

with open(REF, encoding='utf-8') as f:
    for line in f:
        lines += 1
        obj = json.loads(line)
        meta = obj.get('metadata', {})
        yi = meta.get('yi_character', '')
        if not yi:
            no_meta_yi += 1
            continue
        valid += 1
        for c in yi_set(yi):
            chars[c] += 1

print(f"总行数: {lines}")
print(f"有效行(含 yi_character): {valid}")
print(f"无 yi_character 的行: {no_meta_yi}")
print(f"独立字符数: {len(chars)}")
print(f"最大重复: {max(chars.values())}")

# 出现多次的字符
dupes = {c:n for c,n in chars.items() if n > 1}
print(f"\n出现>1次的字符数: {len(dupes)}")
for c,n in sorted(dupes.items(), key=lambda x:-x[1])[:15]:
    print(f"  U+{ord(c):04X}  '{c}'  ×{n}")
