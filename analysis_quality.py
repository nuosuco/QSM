#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""训练数据质量分析 + 彝文覆盖率验证"""

import json, re, sys
from collections import Counter

TRAIN_FILE = "/root/QSM/data/yi_4120_merged_for_gemma.jsonl"
REF_FILE   = "/root/QSM/data/滇川黔贵通用彝文三语对照表.jsonl"

# 彝文统一码范围：U+F2700–U+F344F (滇川黔贵通用彝文)
def yi_set(s):
    return {c for c in s if '\U000F2700' <= c <= '\U000F344F'}

# ---------- 1. 读取参考集（4120 字）----------
ref_chars = set()
with open(REF_FILE, encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        meta = obj.get('metadata', {})
        yi = meta.get('yi_character', '')
        if yi:
            ref_chars.update(yi_set(yi))

print(f"== 参考集: {len(ref_chars)} 个独立彝文字符 ==")

# ---------- 2. 扫描训练数据 ----------
total, bad_json = 0, 0
role_counter = Counter()          # role 分布 (messages)
has_input_yi, has_output_yi = 0, 0
has_input_no_output_yi = 0       # 单侧
has_output_no_input_yi = 0
has_both_yi = 0
no_yi = 0
bad_format = 0

train_chars = set()
n_messages_format = 0
n_io_format = 0

with open(TRAIN_FILE, encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        total += 1
        try:
            obj = json.loads(line)
        except:
            bad_json += 1
            continue

        # 判断格式
        if 'messages' in obj:
            n_messages_format += 1
            msgs = obj['messages']
            roles = [m.get('role','?') for m in msgs]
            role_counter.update(roles)
            text = ' '.join(m.get('content','') for m in msgs)
            cy = yi_set(text)
            train_chars.update(cy)
            if cy:
                # 检查单侧
                user_text = ''
                assistant_text = ''
                for m in msgs:
                    if m.get('role') == 'user':
                        user_text += m.get('content','')
                    elif m.get('role') == 'assistant':
                        assistant_text += m.get('content','')
                u_yi = yi_set(user_text)
                a_yi = yi_set(assistant_text)
                if u_yi and a_yi: has_both_yi += 1
                elif u_yi and not a_yi: has_input_no_output_yi += 1
                elif not u_yi and a_yi: has_output_no_input_yi += 1
                else: pass  # shouldn't happen
            else:
                no_yi += 1
        elif 'input' in obj and 'output' in obj:
            n_io_format += 1
            inp = obj.get('input','')
            out = obj.get('output','')
            train_chars.update(yi_set(inp + out))
            i_yi = yi_set(inp)
            o_yi = yi_set(out)
            if i_yi and o_yi: has_both_yi += 1
            elif i_yi and not o_yi: has_input_no_output_yi += 1
            elif not i_yi and o_yi: has_output_no_input_yi += 1
            else: no_yi += 1
            role_counter['input'] += 1
            role_counter['output'] += 1
        else:
            bad_format += 1

# ---------- 3. 覆盖率 ----------
covered = train_chars & ref_chars
uncovered = ref_chars - train_chars
coverage = len(covered) / len(ref_chars) * 100 if ref_chars else 0

# ---------- 报告 ----------
print("\n" + "="*60)
print("训练数据质量分析报告")
print("="*60)
print(f"\n[样本数]")
print(f"  总行数:       {total}")
print(f"  有效 JSON:    {total - bad_json}")
print(f"  解析失败:     {bad_json}")
print(f"  messages 格式: {n_messages_format}")
print(f"  input/output 格式: {n_io_format}")
print(f"  异常格式:     {bad_format}")

print(f"\n[格式分布]")
print(f"  messages(user/assistant): {n_messages_format}")
print(f"  含 input/output 字段:     {n_io_format}")

print(f"\n[角色分布]")
for k,v in role_counter.most_common():
    print(f"  {k}: {v}")

print(f"\n[单侧彝文检查]")
print(f"  user/assistant 都有彝文:   {has_both_yi}")
print(f"  仅 user 有 (assistant无):  {has_input_no_output_yi}")
print(f"  仅 assistant有 (user无):   {has_output_no_input_yi}")
print(f"  双方均无彝文:             {no_yi}")

print(f"\n[彝文字符统计]")
print(f"  参考集字符数:             {len(ref_chars)}")
print(f"  训练数据独立彝文:         {len(train_chars)}")
print(f"  训练数据覆盖参考集:       {len(covered)}")
print(f"  训练数据未覆盖参考集:     {len(uncovered)}")
print(f"  覆盖率:                   {coverage:.2f}%")

if uncovered:
    ex = ''.join(sorted(uncovered)[:20])
    print(f"  未覆盖样例(前20):       {ex}  (U+{hex(ord(ex[0]))[2:].upper()})")

# 训练数据中不在参考集的字符
extra = train_chars - ref_chars
if extra:
    print(f"  训练数据独有的彝文:     {len(extra)} 个 (不在4120参考集中)")
