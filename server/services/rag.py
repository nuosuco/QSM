# -*- coding: utf-8 -*-
"""
SOM RAG 检索服务
从知识库 JSON 中检索相关内容，为 LLM 提供上下文
轻量级实现：关键词匹配 + 相关性排序，不依赖向量数据库
"""
import json
import os
import re
from typing import List, Optional

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "shared", "knowledge")

_cache = {}


def _load_json(filename: str) -> dict:
    if filename in _cache:
        return _cache[filename]
    path = os.path.join(KNOWLEDGE_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _cache[filename] = data
    return data


def _extract_keywords(text: str) -> List[str]:
    """从用户消息中提取关键词（简单分词）"""
    # 去掉标点和数字
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', ' ', text)
    words = text.split()
    # 保留2字以上的词
    keywords = [w for w in words if len(w) >= 2]
    # 常见症状/食材关键词
    symptom_words = [
        '失眠', '多梦', ' fatigue', '疲劳', '乏力', '气短', '怕冷', '手脚冰凉',
        '口干', '口苦', '上火', '便秘', '腹泻', '腹胀', '食欲', '消化不良',
        '头晕', '头痛', '耳鸣', '眼花', '心悸', '胸闷', '焦虑', '抑郁',
        '湿气', '痰多', '咳嗽', '咽痛', '感冒', '发烧', '出汗', '盗汗',
        '腰酸', '腰痛', '膝盖', '关节', '水肿', '肥胖', '消瘦',
        '面色', '苍白', '萎黄', '暗沉', '长痘', '皮肤', '干燥', '油腻',
        '月经', '痛经', '经期', '白带', '备孕', '产后',
        '舌苔', '舌色', '舌质', '齿痕', '裂纹',
        '枸杞', '红枣', '山药', '薏米', '茯苓', '百合', '莲子', '黄芪',
        '当归', '陈皮', '山楂', '菊花', '决明子', '酸枣仁', '桂圆', '黑芝麻',
        '补气', '补血', '滋阴', '壮阳', '健脾', '祛湿', '清热', '解毒',
        '安神', '助眠', '明目', '润肺', '养胃', '补肾', '疏肝', '理气',
    ]
    for sw in symptom_words:
        if sw in text and sw not in keywords:
            keywords.append(sw)
    return keywords


def search_yaoshi(keywords: List[str], limit: int = 5) -> List[dict]:
    """检索药食同源食材"""
    data = _load_json("yaoshi_tongyuan.json")
    results = []
    for name, info in data.items():
        score = 0
        text = f"{name} {info.get('gongxiao', '')} {info.get('xingwei', '')}"
        for kw in keywords:
            if kw in text:
                score += 2
            if kw in name:
                score += 3
        if score > 0:
            results.append({"name": name, "score": score, **info})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def search_tizhi(keywords: List[str], limit: int = 3) -> List[dict]:
    """检索体质类型"""
    data = _load_json("tizhi.json")
    items = data if isinstance(data, list) else data.get("items", [])
    results = []
    for item in items:
        score = 0
        text = f"{item.get('name', '')} {item.get('desc', '')} {item.get('features', '')}"
        for kw in keywords:
            if kw in text:
                score += 2
        if score > 0:
            results.append({"score": score, **item})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def search_shiliao(keywords: List[str], limit: int = 3) -> List[dict]:
    """检索食疗方案"""
    data = _load_json("shiliao.json")
    results = []
    for key, value in data.items():
        score = 0
        text = f"{key} {json.dumps(value, ensure_ascii=False)}"
        for kw in keywords:
            if kw in text:
                score += 2
            if kw in key:
                score += 3
        if score > 0:
            results.append({"name": key, "score": score, "detail": value})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def search_bianzheng(keywords: List[str], limit: int = 3) -> List[dict]:
    """检索辨证规则"""
    data = _load_json("bianzheng.json")
    results = []
    if isinstance(data, dict):
        for key, value in data.items():
            score = 0
            text = f"{key} {json.dumps(value, ensure_ascii=False)}"
            for kw in keywords:
                if kw in text:
                    score += 2
            if score > 0:
                results.append({"name": key, "score": score, "detail": value})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def build_context(user_message: str, max_chars: int = 3000) -> str:
    """
    根据用户消息构建 RAG 上下文
    返回格式化的知识片段，供 LLM 参考
    """
    keywords = _extract_keywords(user_message)
    if not keywords:
        return ""

    parts = []

    # 1. 药食同源食材
    yaoshi = search_yaoshi(keywords, limit=5)
    if yaoshi:
        parts.append("【相关药食同源食材】")
        for item in yaoshi:
            parts.append(f"- {item['name']}：性味{item.get('xingwei','')}，归经{item.get('guijing','')}，功效{item.get('gongxiao','')}")
            if item.get('jinji'):
                parts.append(f"  禁忌：{item['jinji']}")

    # 2. 体质参考
    tizhi = search_tizhi(keywords, limit=2)
    if tizhi:
        parts.append("\n【相关体质参考】")
        for item in tizhi:
            parts.append(f"- {item.get('name','')}：{item.get('desc','')}")
            if item.get('diet') or item.get('yangsheng'):
                parts.append(f"  调养：{item.get('diet') or item.get('yangsheng','')}")

    # 3. 食疗方案
    shiliao = search_shiliao(keywords, limit=2)
    if shiliao:
        parts.append("\n【相关食疗方案】")
        for item in shiliao:
            detail = item.get("detail", {})
            if isinstance(detail, dict):
                recipe = detail.get("recipe", detail.get("配方", ""))
                usage = detail.get("usage", detail.get("用法", ""))
                parts.append(f"- {item['name']}：{recipe}。{usage}")
            else:
                parts.append(f"- {item['name']}：{detail}")

    # 4. 辨证参考
    bianzheng = search_bianzheng(keywords, limit=2)
    if bianzheng:
        parts.append("\n【辨证参考】")
        for item in bianzheng:
            parts.append(f"- {item['name']}：{json.dumps(item.get('detail',''), ensure_ascii=False)[:200]}")

    context = "\n".join(parts)
    if len(context) > max_chars:
        context = context[:max_chars] + "\n...(已截断)"
    return context
