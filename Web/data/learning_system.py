#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM学习系统 v1.0
从用户对话中学习新知识
"""
import json
import os
from datetime import datetime

LEARN_FILE = '/root/QSM/Web/data/learned_knowledge.json'

def load_learned():
    """加载已学习的知识"""
    if os.path.exists(LEARN_FILE):
        with open(LEARN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_learned(knowledge):
    """保存学习的知识"""
    with open(LEARN_FILE, 'w', encoding='utf-8') as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)

def learn(question, answer):
    """学习新的问答对"""
    learned = load_learned()
    learned[question] = {
        'answer': answer,
        'learned_at': datetime.now().isoformat(),
        'source': 'user_dialog'
    }
    save_learned(learned)
    return f"已学习: {question} → {answer}"

def get_learned_answer(question):
    """获取学习的答案"""
    learned = load_learned()
    if question in learned:
        return learned[question]['answer'], 'learned'
    return None, None

def export_to_knowledge_base():
    """导出到知识库"""
    learned = load_learned()
    
    # 加载现有知识库
    kb_file = '/root/QSM/Web/data/qsm_knowledge_base.json'
    if os.path.exists(kb_file):
        with open(kb_file, 'r', encoding='utf-8') as f:
            kb = json.load(f)
    else:
        kb = {'knowledge': {}}
    
    # 合并学习的内容
    for q, v in learned.items():
        kb['knowledge'][q] = v['answer']
    
    # 保存
    with open(kb_file, 'w', encoding='utf-8') as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
    
    return len(learned)

if __name__ == '__main__':
    # 测试
    print(learn("测试问题", "测试答案"))
    print(get_learned_answer("测试问题"))
    print(f"导出: {export_to_knowledge_base()}条")
