#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 yi_training_pipeline 读取训练数据的能力"""
import json, os

TRAIN = "/root/QSM/data/yi_4120_merged_for_gemma.jsonl"

# Pipeline 期望的格式：messages（含 role/content）
# Pipeline 提取方式：grep '"content":' 然后正则提取彝文

pipeline_expect_messages = True
actual_format = "input/output"

issues = []

# 1. 字段名检查
with open(TRAIN, encoding='utf-8') as f:
    sample = json.loads(f.readline())

if 'messages' not in sample:
    issues.append("❌ 训练数据不含 'messages' 字段（pipeline 期望 messages 格式）")

if 'input' in sample and 'output' in sample:
    issues.append("ℹ️  实际格式: 'input'/'output' 字段（对话式，但非 OpenAI messages 格式）")

# 2. 检查 grep '"content":' 能否匹配
import subprocess
result = subprocess.run(
    ["grep", "-c", '"content"', TRAIN], capture_output=True, text=True
)
content_matches = int(result.stdout.strip())
issues.append(f"grep '\"content\"' 匹配行数: {content_matches} / 51899")

# 3. 检查 grep '"input"' / '"output"' 匹配
for key in ['input', 'output']:
    r = subprocess.run(
        ["grep", "-c", f'"{key}"', TRAIN], capture_output=True, text=True
    )
    issues.append(f"grep '\"{key}\"' 匹配行数: {r.stdout.strip()} / 51899")

# 4. Pipeline data_analysis.json 保存路径
model_dir = "/root/QSM/models/yi_qns"
da_path = os.path.join(model_dir, "data_analysis.json")
issues.append(f"\nPipeline 输出路径: {da_path}")
issues.append(f"  文件存在: {os.path.exists(da_path)}")
if os.path.exists(da_path):
    with open(da_path) as f:
        da = json.load(f)
    issues.append(f"  unique_yi_chars: {da.get('unique_yi_chars')}")

# 5. 结论
print("="*60)
print("yi_training_pipeline 数据读取兼容性检查")
print("="*60)
for i in issues:
    print(i)

print("\n⚠️  格式不兼容问题:")
print("  Pipeline analyze_data() 使用 grep '\"content\":' 提取")
print("  但训练数据是 {\"input\": ..., \"output\": ...} 格式")
print("  → Pipeline 无法从训练数据中提取 content/彝文")
print("  → 需要适配 input/output 格式或转换数据")
