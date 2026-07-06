#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""彝文字符分布统计"""
import json
from collections import Counter

TRAIN = "/root/QSM/data/yi_4120_merged_for_gemma.jsonl"

def yi_set(s):
    return {c for c in s if '\U000F2700' <= c <= '\U000F344F'}

# 每个样本含多少个独立彝文字符的分布
dist = Counter()
total_chars_per_sample = Counter()
longest = 0
longest_sample = None

with open(TRAIN, encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        obj = json.loads(line)
        text = obj.get('input','') + obj.get('output','')
        yi = yi_set(text)
        n = len(yi)
        dist[n] += 1
        total_chars_per_sample[i] = n
        if n > longest:
            longest = n
            longest_sample = obj

print("每个样本独立彝文字符数分布:")
print(f"  {'字符数':>6}  {'样本数':>8}  {'累计':>8}  {'占比':>6}")
cum = 0
for k in range(0, 11):
    v = dist.get(k, 0)
    cum += v
    print(f"  {k:>6}  {v:>8}  {cum:>8}  {v/51899*100:5.1f}%")
print(f"  {'10+':>6}  {sum(v for k,v in dist.items() if k>10):>8}")
print(f"  最多: {longest} 个字符")

# 样本内容长度分布
print("\n文本长度统计 (chars):")
inp_lens = []
out_lens = []
with open(TRAIN, encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        inp_lens.append(len(obj.get('input','')))
        out_lens.append(len(obj.get('output','')))

print(f"  input 平均: {sum(inp_lens)/len(inp_lens):.1f} chars")
print(f"  output 平均: {sum(out_lens)/len(out_lens):.1f} chars")
print(f"  input 范围: {min(inp_lens)} - {max(inp_lens)}")
print(f"  output 范围: {min(out_lens)} - {max(out_lens)}")
