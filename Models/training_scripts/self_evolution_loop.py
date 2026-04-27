#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QSM自我进化循环 - 用当前模型生成翻译 → 自动评估 → 收集反馈数据"""

import json, os, requests, random, time

API_URL = "http://127.0.0.1:8000"
DATA_DIR = "/root/.openclaw/workspace/QSM/data"
FEEDBACK_DIR = "/root/.openclaw/workspace/QSM/feedback"

os.makedirs(FEEDBACK_DIR, exist_ok=True)

# 测试用例
test_cases = [
    # 基础字词翻译
    {"input": "心", "direction": "zh2yi", "expected_category": "single_char"},
    {"input": "火", "direction": "zh2yi", "expected_category": "single_char"},
    {"input": "天", "direction": "zh2yi", "expected_category": "single_char"},
    {"input": "水", "direction": "zh2yi", "expected_category": "single_char"},
    {"input": "山", "direction": "zh2yi", "expected_category": "single_char"},
    # 句子级
    {"input": "你好", "direction": "zh2yi", "expected_category": "sentence"},
    {"input": "谢谢", "direction": "zh2yi", "expected_category": "sentence"},
    {"input": "再见", "direction": "zh2yi", "expected_category": "sentence"},
    # 彝文到中文
    {"direction": "yi2zh", "expected_category": "yi_to_zh"},
]

# 加载三语对照表获取测试样本
trilingual_path = os.path.join(DATA_DIR, "滇川黔贵通用彝文三语对照表.jsonl")
if os.path.exists(trilingual_path):
    with open(trilingual_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 100: break
            item = json.loads(line)
            meta = item.get('metadata', {})
            yi = meta.get('yi_character', '')
            zh = meta.get('chinese', '')
            if yi and zh:
                test_cases.append({"input": zh, "direction": "zh2yi", "expected_yi": yi, "expected_category": "trilingual"})
                test_cases.append({"input": yi, "direction": "yi2zh", "expected_zh": zh, "expected_category": "trilingual_reverse"})

def evaluate():
    """运行一轮自我评估"""
    results = []
    correct = 0
    total = 0
    
    for tc in test_cases:
        try:
            resp = requests.post(f"{API_URL}/translate", 
                json={"direction": tc["direction"], "text": tc["input"]},
                timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                translated = data.get("translated", "")
                result = {
                    "input": tc["input"],
                    "direction": tc["direction"],
                    "output": translated,
                    "category": tc.get("expected_category", "unknown"),
                    "timestamp": time.time()
                }
                
                # 自动评估（如果有期望输出）
                if "expected_yi" in tc:
                    result["expected"] = tc["expected_yi"]
                    result["match"] = (translated == tc["expected_yi"])
                    if result["match"]: correct += 1
                    total += 1
                elif "expected_zh" in tc:
                    result["expected"] = tc["expected_zh"]
                    result["match"] = (tc["expected_zh"] in translated)
                    if result["match"]: correct += 1
                    total += 1
                
                results.append(result)
        except Exception as e:
            results.append({"error": str(e), "input": tc["input"]})
    
    # 保存反馈
    feedback_file = os.path.join(FEEDBACK_DIR, f"eval_{int(time.time())}.json")
    with open(feedback_file, 'w', encoding='utf-8') as f:
        json.dump({"results": results, "correct": correct, "total": total, 
                    "accuracy": correct/total if total > 0 else 0}, f, ensure_ascii=False, indent=2)
    
    print(f"评估完成: {correct}/{total} = {correct/total*100:.1f}% (总{len(results)}测试)")
    return correct, total

if __name__ == "__main__":
    print("=" * 40)
    print("QSM自我进化评估循环")
    print("=" * 40)
    evaluate()
