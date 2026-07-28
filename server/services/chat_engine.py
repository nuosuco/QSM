# -*- coding: utf-8 -*-
"""
SOM 新版对话引擎
LLM（自然语言）+ RAG（知识库）+ 辨证引擎（规则）三合一
- LLM 负责"嘴"：自然对话、温暖表达
- RAG 负责"脑"：提供专业知识上下文
- 辨证引擎负责"判断"：体质/证型判定（规则，可控）
"""
import re
from typing import Optional
from services import llm_router, rag
from services.bianzheng import BianzhengEngine

SYSTEM_PROMPT = """你是小麦SOM，一位温暖、专业、有耐心的中医养生顾问。

你的职责：
1. 认真倾听用户的身体描述，用通俗语言分析可能的体质倾向
2. 基于药食同源知识，给出实用的食养建议（配方+用法）
3. 推荐适合的有机食材，但绝不强推销
4. 语气温和亲切，像朋友聊天，不说教、不吓唬人
5. 每次回复结尾加一句：以上为养生文化参考，身体不适请及时就医

重要规则：
- 不做医疗诊断，不说"你得了XX病"
- 不用"治疗""治愈""根治"等医疗用语，用"调养""食养""参考"
- 配方必须来自药食同源目录，不推荐药材
- 如果用户描述严重症状，优先建议就医，再给辅助食养参考
- 回复控制在300字以内，简洁有用"""


def chat_with_llm(user_message: str, history: list = None) -> dict:
    """
    新版对话：LLM + RAG + 辨证引擎
    返回 {reply, tizhi, zhengxing, recommendations, products}
    """
    # 1. RAG 检索知识上下文
    context = rag.build_context(user_message, max_chars=2500)

    # 2. 构建 system prompt（含 RAG 上下文）
    system = SYSTEM_PROMPT
    if context:
        system += f"\n\n【参考知识（仅供内部参考，不要直接复述给用户）】\n{context}"

    # 3. 调用 LLM 生成回复
    llm_result = llm_router.chat(
        user_message,
        system_prompt=system,
        history=history,
        temperature=0.7,
    )

    if llm_result.get("success"):
        reply = llm_result["content"]
    else:
        # LLM 挂了，降级到规则引擎
        engine = BianzhengEngine()
        result = engine.analyze(user_message)
        reply = result.get("reply", "抱歉，我暂时有点不舒服，请稍后再试。")

    # 4. 辨证引擎判定体质/证型（规则，可控，不依赖LLM）
    engine = BianzhengEngine()
    bz_result = engine.analyze(user_message)
    tizhi = bz_result.get("tizhi")
    zhengxing = bz_result.get("zhengxing")
    recommendations = bz_result.get("recommendations", [])

    # 5. 从回复中提取食材名，搜索商品
    products = _search_products_from_reply(reply, recommendations)

    return {
        "reply": reply,
        "tizhi": tizhi,
        "zhengxing": zhengxing,
        "recommendations": recommendations,
        "products": products,
        "provider": llm_result.get("provider", "fallback"),
        "model": llm_result.get("model", "bianzheng_engine"),
    }


def _search_products_from_reply(reply: str, recommendations: list) -> list:
    """从回复文本中提取食材名，并行搜索商品"""
    from services.shop import ShopService
    import concurrent.futures

    # 提取食材名
    ingredient_names = []

    # 方法1：从配方文字提取
    recipe_match = re.findall(r'配方[：:](.+?)(?:\n|—|：|。)', reply, re.DOTALL)
    if recipe_match:
        text = recipe_match[0]
        parts = re.split(r'[、,，;；]', text)
        for part in parts:
            part = part.strip()
            name = re.sub(r'[\d.]+(?:[gG克毫升mlML枚粒只条根片块个半只碗勺杯袋包瓶盒罐]*)', '', part).strip()
            name = re.sub(r'(半只|少许|适量|若干|少量|各)$', '', name).strip()
            if name and 2 <= len(name) <= 6 and name not in ingredient_names:
                ingredient_names.append(name)

    # 方法2：从推荐列表提取
    if not ingredient_names:
        ingredient_names = [r.get("name", "") for r in recommendations if r.get("name")]

    # 方法3：从回复中匹配常见食材
    if not ingredient_names:
        common_foods = ['枸杞', '红枣', '山药', '薏米', '茯苓', '百合', '莲子', '黄芪',
                        '当归', '陈皮', '山楂', '菊花', '决明子', '酸枣仁', '桂圆', '黑芝麻',
                        '赤小豆', '银耳', '核桃', '黑豆', '黑米', '燕麦', '小米']
        for food in common_foods:
            if food in reply and food not in ingredient_names:
                ingredient_names.append(food)

    if not ingredient_names:
        return []

    # 并行搜索
    shop = ShopService()
    products = []
    seen_titles = set()

    def search_one(ing: str) -> list:
        result = []
        local_titles = set()
        local_brands = set()
        for page in range(1, 6):
            try:
                items = shop._search_taobao(f"{ing} 有机", page, 2, "")
            except Exception:
                items = []
            if not items:
                continue
            for item in items:
                title = item.get('title', '')
                brand = item.get('shop_name', '') or ''
                if '有机' not in title:
                    continue
                if title and title not in local_titles and not shop._is_excluded(item):
                    if ing.lower() in title.lower():
                        local_titles.add(title)
                        if brand not in local_brands or len(result) < 2:
                            local_brands.add(brand)
                            result.append(item)
            if len(result) >= 2:
                break
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(search_one, ing): ing for ing in ingredient_names[:6]}
        concurrent.futures.wait(futures, timeout=15)
        for future in futures:
            try:
                items = future.result()
                for item in items:
                    title = item.get('title', '')
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        products.append(item)
            except Exception:
                pass

    return products
