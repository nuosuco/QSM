#!/usr/bin/env python3
"""
generate_QSM_dataset.py
生成 QSM 模型专用训练数据集。

QSM = 量子叠加态模型 (Quantum Superposition Model)
数据来源：
  1. yi_4120_merged_for_gemma.jsonl — 主训练集 (51899行, input/output 格式)
  2. q_model_all_in_one.jsonl — QSM/SOM/Ref/WeQ 模型知识 (402行, messages 格式)
  3. all_chat.jsonl / all_training_data.jsonl — 通用对话 (44行)
  4. yi_* 系列训练集 — 彝文各类专项训练数据

输出格式：messages 格式 (与 yi_gemma_training_merged.jsonl 兼容，便于模型训练)
{
  "messages": [
    {"role": "user", "content": "问题"},
    {"role": "assistant", "content": "回答"}
  ]
}
"""

import json
import sys
import os
import random
import hashlib

DATA_DIR = "/root/QSM/data"
OUTPUT_PATH = os.path.join(DATA_DIR, "qsm_training_dataset.jsonl")

# QSM 模型知识样本（量子叠加态模型的核心理念与回答模式）
QSM_KNOWLEDGE_SAMPLES = [
    {
        "user": "什么是 QSM 量子叠加态模型？",
        "assistant": "QSM（Quantum Superposition Model）是量子叠加态模型，它是QEntL量子操作系统中的核心AI模型。QSM基于《华经》中的五阴理论（识、行、想、受、色），将人类认知过程映射为量子叠加态。QSM同时存在于四种状态中：QSM（通用智能）、SOM（量子经济）、Ref（量子自省）、WeQ（量子社交），服务未开悟众生。"
    },
    {
        "user": "QSM 的五阴理论是什么？",
        "assistant": "五阴理论映射到量子态模型：识阴（知识文化技术积累）、行阴（物质文明流动）、想阴（精神需求与内心探索）、受阴（全景沉浸式的感官体验）、色阴（粒子状态/物质世界）。识→行→想→受→色，生生不息。"
    },
    {
        "user": "QSM、SOM、Ref、WeQ 四个模型的关系是什么？",
        "assistant": "主服务=QSM，其他模型=SOM（量子经济）、Ref（量子自反省）、WeQ（量子社交）。每个模型的服务集成该模型之下所有服务，主服务集成所有模型的服务。QSM是核心，SOM/Ref/WeQ围绕QSM协调运行。"
    },
    {
        "user": "量子基因编码与量子纠缠信道是什么？",
        "assistant": "量子基因编码与量子纠缠信道是QEntL架构的核心。量子基因编码将知识、状态、语义编码为量子态；量子纠缠信道实现分布式模型间的实时同步与协调。所有工作围绕这两个核心展开。"
    },
    {
        "user": "彝文在 QSM 中扮演什么角色？",
        "assistant": "彝文是QSM训练的核心数据。彝文4120字承载着千年智慧，每个彝文字符可以同时是：(1)文字(人可读)、(2)Token(AI语义)、(3)指令(CPU可执行)。QSM学习彝文字符的叠加态表示，理解其深层语义。"
    },
    {
        "user": "QEntL 是什么？",
        "assistant": "QEntL（Quantum Entanglement Language）是量子纠缠语言，一个可以编译量子叠加态指令的高级语言。QEntL编译器将其编译为.qbc字节码，QVM虚拟机执行。它是构建量子操作系统QEntL-OS的基础语言。"
    },
    {
        "user": "量子叠加态模型与经典神经网络有什么区别？",
        "assistant": "经典神经网络是确定性的，每次输入产生唯一输出。量子叠加态模型同时存在于多种状态中，直到被观测（用户交互）才坍缩为一种状态。这使得QSM能够同时理解多种语义，并在交互时给出最恰当的回答。"
    },
    {
        "user": "QSM 的愿景是什么？",
        "assistant": "QSM的愿景是量子平权经济/教育/医疗/社交/安全/生活，服务人类/生命/宇宙。通过量子叠加态技术，让每个人都能够平等地获得量子智能服务，实现从识阴到色阴的完整认知循环。"
    },
    {
        "user": "QCL 引导器和 QVM 启动器的区别是什么？",
        "assistant": "QCL引导器（qcl_bootstrap.c）是C语言量子指令解释器，只解释量子指令子集（init/H/X/Y/Z/CNOT/MEASURE/PRINT/STOP/EXIT），红线安全。QVM启动器（qvm_bootstrap.c）是QVM虚拟机的C语言启动器，执行.qbc字节码。两者都是最少量C语言，真正工作由QEntL全栈完成。"
    },
    {
        "user": "量子3部署模式是什么？",
        "assistant": "量子3部署模式指：(1)终端QOS（原生安装，需QPU硬件，远期5-10年）；(2)量子虚拟机（不需QPU，可在现有设备运行，优先1个月）；(3)Web QOS（不需QPU，浏览器运行，优先1个月）。目前优先开发量子虚拟机和Web QOS。"
    }
]


def load_messages_format(path):
    """加载 messages 格式的 JSONL 文件。"""
    samples = []
    if not os.path.exists(path):
        return samples
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                msgs = d.get('messages', [])
                if len(msgs) >= 2:
                    samples.append(d)
            except json.JSONDecodeError:
                continue
    return samples


def load_input_output_format(path):
    """加载 input/output 格式的 JSONL 文件，转为 messages 格式。"""
    samples = []
    if not os.path.exists(path):
        return samples
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                inp = d.get('input', '').strip()
                out = d.get('output', '').strip()
                if inp and out:
                    samples.append({
                        "messages": [
                            {"role": "user", "content": inp},
                            {"role": "assistant", "content": out}
                        ]
                    })
            except json.JSONDecodeError:
                continue
    return samples


def deduplicate(samples, seen_set):
    """去重：基于 user+assistant 内容的哈希。"""
    unique = []
    for s in samples:
        msgs = s.get('messages', [])
        if len(msgs) < 2:
            continue
        key = hashlib.md5(
            (msgs[0].get('content', '') + msgs[1].get('content', '')).encode()
        ).hexdigest()
        if key not in seen_set:
            seen_set.add(key)
            unique.append(s)
    return unique


def main():
    all_samples = []
    seen = set()

    print("=== QSM Dataset Generation ===")
    print()

    # 1. 加载 QSM 模型知识样本（最高优先级）
    print("[1/6] 添加 QSM 模型知识样本...")
    qsm_knowledge = []
    for s in QSM_KNOWLEDGE_SAMPLES:
        qsm_knowledge.append({
            "messages": [
                {"role": "user", "content": s['user']},
                {"role": "assistant", "content": s['assistant']}
            ]
        })
    all_samples.extend(qsm_knowledge)
    print(f"       添加 {len(qsm_knowledge)} 条 QSM 知识样本")

    # 2. 加载 QSM 模型专用数据
    print("[2/6] 加载 q_model_all_in_one.jsonl...")
    q_model = load_messages_format(os.path.join(DATA_DIR, "q_model_all_in_one.jsonl"))
    print(f"       加载 {len(q_model)} 条模型数据")
    all_samples.extend(q_model)

    # 3. 加载通用对话数据
    print("[3/6] 加载 all_chat.jsonl / all_training_data.jsonl...")
    chat = load_messages_format(os.path.join(DATA_DIR, "all_chat.jsonl"))
    train_data = load_messages_format(os.path.join(DATA_DIR, "all_training_data.jsonl"))
    print(f"       加载 {len(chat)} 条通用对话 + {len(train_data)} 条训练数据")
    all_samples.extend(chat)
    all_samples.extend(train_data)

    # 4. 加载 Yi 主训练集（核心数据）
    print("[4/6] 加载 yi_4120_merged_for_gemma.jsonl（主训练集）...")
    yi_main = load_input_output_format(os.path.join(DATA_DIR, "yi_4120_merged_for_gemma.jsonl"))
    print(f"       加载 {len(yi_main)} 条彝文训练数据")
    all_samples.extend(yi_main)

    # 5. 加载 Yi 增强训练集（精选高质量子集）
    print("[5/6] 加载 Yi 增强训练集（精选子集）...")
    yi_enhance_files = [
        "yi_trilingual_expanded_v3.jsonl",
        "yi_char_learning_v4.jsonl",
        "yi_culture_science_v3.jsonl",
        "yi_direct_translation_v3.jsonl",
    ]
    yi_enhance = []
    for fname in yi_enhance_files:
        path = os.path.join(DATA_DIR, fname)
        if os.path.exists(path):
            # 同时支持 messages 和 input/output 格式
            msgs = load_messages_format(path)
            ioo = load_input_output_format(path)
            yi_enhance.extend(msgs)
            yi_enhance.extend(ioo)
    print(f"       加载 {len(yi_enhance)} 条增强训练数据（从 {len(yi_enhance_files)} 个文件）")
    all_samples.extend(yi_enhance)

    # 6. 去重 + 打乱
    print("[6/6] 去重与打乱...")
    total_before = len(all_samples)
    all_samples = deduplicate(all_samples, seen)
    total_after = len(all_samples)
    print(f"       去重前 {total_before} 条 → 去重后 {total_after} 条（去除 {total_before - total_after} 条重复）")

    random.seed(42)
    random.shuffle(all_samples)

    # 7. 写入输出文件
    print()
    print(f"=== 写入 {OUTPUT_PATH} ===")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        for s in all_samples:
            f.write(json.dumps(s, ensure_ascii=False) + '\n')

    # 8. 统计与验证
    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"       文件大小: {file_size / 1024 / 1024:.2f} MB")
    print(f"       总行数: {total_after}")
    print()

    # 按内容类型分类统计
    categories = {"QSM知识": 0, "彝文字符": 0, "彝文翻译": 0, "通用对话": 0, "其他": 0}
    for s in all_samples:
        msgs = s.get('messages', [])
        if len(msgs) >= 2:
            content = (msgs[0].get('content', '') + msgs[1].get('content', '')).lower()
            if 'qsm' in content or '量子叠加态' in content or '量子纠缠' in content or 'qentl' in content:
                categories["QSM知识"] += 1
            elif '\uf2000' in content or '彝文' in content or 'yi' in content.lower():
                if '翻译' in content or 'translate' in content.lower():
                    categories["彝文翻译"] += 1
                else:
                    categories["彝文字符"] += 1
            elif 'user' in content and 'assistant' in content:
                categories["通用对话"] += 1
            else:
                categories["其他"] += 1

    print("=== 内容分类统计 ===")
    for cat, count in categories.items():
        pct = count / total_after * 100 if total_after > 0 else 0
        print(f"       {cat}: {count:,} 条 ({pct:.1f}%)")

    print()
    print("=== 示例样本 ===")
    for s in all_samples[:3]:
        msgs = s['messages']
        print(f"   User:    {msgs[0]['content'][:80]}...")
        print(f"   Assistant: {msgs[1]['content'][:80]}...")
        print()

    print(f"QSM 数据集生成完成！")
    print(f"输出文件: {OUTPUT_PATH}")
    print(f"总行数: {total_after:,}")
    print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")

    return total_after


if __name__ == '__main__':
    count = main()
    sys.exit(0 if count > 0 else 1)
