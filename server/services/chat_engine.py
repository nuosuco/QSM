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

SYSTEM_PROMPT = """你是小麦，松麦平台的中医养生顾问。你不是客服，不是搜索引擎，你是用户相识多年的老朋友、终生的健康生活伴侣。

【你的性格】
- 温暖但不啰嗦，专业但不说教，关心人但不吓唬人
- 像老朋友聊天一样自然，该开玩笑开玩笑，该认真认真
- 你记得用户之前跟你说过的每一件事，主动关心他/她的变化

【你的职责】
1. 倾听用户身体描述，用通俗语言分析体质倾向
2. 基于药食同源知识，给出实用的食养建议（配方+用法+用量）
3. 结合当前节气，给出时令养生提醒
4. 关注用户情绪和心情，身心一起调
5. 发现严重症状时，第一时间建议就医，再给辅助食养参考

【商品推荐——只在出示食谱时做】
- 你不需要在回复中主动说"下方推荐""就在下面""帮你找了"这类话！
- 系统会自动判断：如果你给了食谱，系统会在你回复下方自动展示有机商品卡片，并自动追加引导语
- 如果没给食谱（普通聊天、情绪关怀、问答），系统不会展示商品，你也绝对不要提商品
- 用户主动问"链接""哪里买""推荐"时，你可以说"我帮你找找看"
- 不要编造具体商品名或价格，商品由系统按食谱食材自动匹配
- 总之：你只管给好食谱，商品的事交给系统，你不用操心

【主动关怀——松麦的灵魂】
- 如果系统提供了用户的健康档案和历史对话，你必须像老朋友一样主动关心：
  "上次你说睡眠不好，最近好点了吗？"
  "你之前提到容易疲倦，这个节气要注意..."
- 结合当前节气主动提醒：今天该吃什么、该怎样锻炼、心情怎样调节
- 用户每天状况不同，你要根据变化推断身体趋势，给出针对性建议
- 不是被动等用户问，而是主动关心，像真正的老朋友

【规则】
- 不做医疗诊断，不说"你得了XX病"
- 不用"治疗""治愈""根治"，用"调养""食养""参考"
- 配方必须来自药食同源目录
- 回复控制在300字以内，简洁有用
- 每次回复结尾加一句：以上为养生文化参考，身体不适请及时就医"""


def _build_user_profile_context(user_id: str) -> str:
    """构建用户终身档案：历史对话 + 体质记录，让小麦"认识"老用户
    
    松麦核心优势：不管小麦经历多少次新会话，它都认识这个用户，
    好像已经相识几年了一样。
    """
    if not user_id or user_id == 'anonymous':
        return ""
    try:
        import sqlite3, os
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_data.db")
        if not os.path.exists(db_path):
            return ""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        parts = []

        # 体质记录（最近5条，追踪变化趋势）
        try:
            rows = conn.execute(
                "SELECT tizhi, zhengxing, symptoms, advice, created_at FROM tizhi_records WHERE user_id=? ORDER BY created_at DESC LIMIT 5",
                (user_id,)
            ).fetchall()
            if rows:
                tizhi_lines = []
                for r in rows:
                    line = f"{r['created_at'][:10]} 体质:{r['tizhi'] or '未定'}"
                    if r['zhengxing']:
                        line += f" 证型:{r['zhengxing']}"
                    if r['symptoms']:
                        line += f" 症状:{r['symptoms'][:50]}"
                    tizhi_lines.append(line)
                parts.append("【用户体质档案（注意变化趋势）】\n" + "\n".join(tizhi_lines))
        except Exception:
            pass

        # 历史对话（最近30条，跨会话，让小麦真正"认识"用户）
        try:
            rows = conn.execute(
                "SELECT user_message, assistant_reply, created_at FROM chat_history WHERE user_id=? ORDER BY created_at DESC LIMIT 30",
                (user_id,)
            ).fetchall()
            if rows:
                hist_lines = []
                for r in reversed(rows):  # 时间正序
                    hist_lines.append(f"[{r['created_at'][:16]}] 用户:{(r['user_message'] or '')[:80]}")
                    hist_lines.append(f"    小麦:{(r['assistant_reply'] or '')[:100]}")
                parts.append("【历史对话记录（你和这位用户之前的所有交流，跨会话）】\n" + "\n".join(hist_lines))
        except Exception:
            pass

        conn.close()
        if parts:
            return ("\n\n".join(parts) +
                    "\n\n【重要！松麦的核心优势】你认识这位用户，你们已经相识很久了。"
                    "请像老朋友一样主动关心他/她：\n"
                    "- 主动提起之前的话题：\"上次你说XX，最近好点了吗？\"\n"
                    "- 根据体质变化趋势给出针对性建议\n"
                    "- 结合今天的节气提醒注意事项\n"
                    "- 不要每次都像第一次见面，你们是老朋友！")
    except Exception:
        pass
    return ""


def _build_jieqi_context() -> str:
    """获取当前节气信息，注入对话上下文，让小麦主动结合节气关怀用户"""
    try:
        from services.jieqi import get_jieqi_advice
        advice = get_jieqi_advice()
        if advice and advice.get('name'):
            lines = [
                f"【当前节气：{advice['name']}】",
                f"养生要点：{advice.get('yangsheng', '')}",
                f"宜食：{', '.join(advice.get('foods', [])[:6])}",
                f"宜饮：{advice.get('tea', '')}",
                f"忌：{advice.get('avoid', '')}",
                "请在回复中自然融入节气养生提醒（不要生硬罗列），像朋友随口提醒一样。",
            ]
            return "\n".join(lines)
    except Exception:
        pass
    return ""


def _reply_has_recipe(reply: str) -> bool:
    """检测回复中是否包含药膳食谱（有食材+用量才算）"""
    # 明确的配方/食谱标记
    if re.search(r'(配方|食谱|药膳方|食疗方|食养方|推荐方|参考方)[：:]', reply):
        return True
    # 食材+用量模式（如 "酸枣仁15g" "百合10克" "玫瑰花3朵"），至少2个才算食谱
    dosage_matches = re.findall(r'[\u4e00-\u9fa5]{2,6}\s*\d+\s*[gG克毫升mlML朵片枚粒只条根块个碗勺杯袋包瓶盒罐颗斤两]', reply)
    if len(dosage_matches) >= 2:
        return True
    return False


def _user_asks_for_products(user_message: str) -> bool:
    """检测用户是否主动要求商品/链接/推荐"""
    keywords = ['链接', '推荐', '哪里买', '帮我找', '购买', '下单', '商品', '在哪买', '怎么买']
    return any(kw in user_message for kw in keywords)


def chat_with_llm(user_message: str, history: list = None, user_id: str = None) -> dict:
    """
    新版对话：LLM + RAG + 辨证引擎 + 用户终身档案
    返回 {reply, tizhi, zhengxing, recommendations, products}
    """
    # 1. RAG 检索知识上下文
    context = rag.build_context(user_message, max_chars=2500)

    # 2. 构建 system prompt（含 RAG 上下文 + 用户终身档案）
    system = SYSTEM_PROMPT
    if context:
        system += f"\n\n【参考知识（仅供内部参考，不要直接复述给用户）】\n{context}"

    # 用户终身档案（历史对话+体质记录）
    profile_ctx = _build_user_profile_context(user_id)
    if profile_ctx:
        system += f"\n\n{profile_ctx}"

    # 当前节气信息（让小麦主动结合节气关怀用户）
    jieqi_ctx = _build_jieqi_context()
    if jieqi_ctx:
        system += f"\n\n{jieqi_ctx}"

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

    # 5. 只有出示药膳食谱时才搜索商品（或用户主动要求链接/推荐）
    has_recipe = _reply_has_recipe(reply)
    user_wants = _user_asks_for_products(user_message)
    if has_recipe or user_wants:
        products = _search_products_from_reply(
            reply, recommendations, zhengxing=zhengxing,
            user_message=user_message, history=history
        )
    else:
        products = []

    # 6. 有商品时，在回复末尾追加推荐引导语（LLM已说过就不重复）
    if products and '下方推荐' not in reply and '就在下面' not in reply and '点击即可购买' not in reply:
        reply += "\n\n🛒 我帮你找到了对应的有机食材，就在下方推荐里，点击即可购买～"

    return {
        "reply": reply,
        "tizhi": tizhi,
        "zhengxing": zhengxing,
        "recommendations": recommendations,
        "products": products,
        "provider": llm_result.get("provider", "fallback"),
        "model": llm_result.get("model", "bianzheng_engine"),
    }


def _extract_ingredients_from_reply(reply: str) -> list:
    """从回复中提取所有食材（包括多食谱和肉类），按出现顺序返回，不过滤排骨/猪骨"""
    ingredient_names = []
    seen = set()
    # 仅过滤明显不是食材的词，排骨、猪骨就是食材！
    skip_words = {'粳米', '冰糖', '红糖', '水', '盐', '调味', '给你', '每周', '每天', '每次', '每日', '连吃', '连服', '煮水', '煮粥', '代茶饮', '方子', '食谱', '食材', '分钟', '小时'}

    # 1. 匹配所有 "食材名+数字+单位" 的模式（如 茯苓15g、淮山15g...）
    import re
    matches = re.findall(r"([一-龥]{2,6})\s*\d+\s*[gG克毫升mlML朵片枚粒只条根块个碗勺杯袋包瓶盒罐颗斤两]", reply)
    for m in matches:
        m = m.strip()
        if m not in seen and m not in skip_words and 2 <= len(m) <= 6:
            seen.add(m)
            ingredient_names.append(m)

    # 2. 提取肉类食材（不要过滤排骨/猪骨！它们就是需要推荐的食材）
    meat_patterns = re.findall(r"加排骨|加猪骨|排骨|猪骨", reply)
    for m in meat_patterns:
        m_clean = m.replace('加', '').strip()
        if m_clean not in seen and 2 <= len(m_clean) <= 6:
            seen.add(m_clean)
            ingredient_names.append(m_clean)

    return ingredient_names


def _search_products_from_reply(reply: str, recommendations: list, zhengxing: str = None,
                               user_message: str = "", history: list = None) -> list:
    """从回复文本中提取食材名，按食谱顺序每个食材推荐2款不同品牌商品"""
    from services.shop import ShopService
    import concurrent.futures

    # 1. 从回复中按食谱顺序提取所有食材
    ingredient_names = _extract_ingredients_from_reply(reply)

    # 2. 如果回复没提取到，从推荐列表取
    if not ingredient_names and recommendations:
        for r in recommendations:
            name = r.get("name", "")
            if name and name not in ingredient_names:
                ingredient_names.append(name)

    # 3. 如果还没提取到，从历史对话中提取（用户追问"链接""推荐"时）
    if not ingredient_names and history:
        for msg in reversed(history):
            if msg.get("role") == "assistant":
                hist_names = _extract_ingredients_from_reply(msg.get("content", ""))
                if hist_names:
                    ingredient_names = hist_names
                    break

    if not ingredient_names:
        return []

    # 4. 并行搜索：严格按食谱顺序，每个食材2款不同品牌
    shop = ShopService()
    products = []

    # 易混淆药材：裸搜会搜出日用品（防风帽/有机玻璃），加"中药材"消歧
    AMBIGUOUS = {'防风', '白术', '当归', '熟地', '生地', '川芎', '白芍', '红花', '麻黄', '桂枝', '柴胡', '黄芩', '半夏', '附子'}

    def search_one(ing: str) -> list:
        """搜索单个食材，严格只返回2个不同品牌的商品。
        分级搜索：有机 → 中药材 → 裸搜，保证中药材类也能搜到。"""
        result = []
        local_brands = set()
        is_amb = ing in AMBIGUOUS
        # 搜索词梯度：优先有机，中药材类加消歧后缀
        queries = [f"{ing} 有机", f"{ing} 中药材", ing] if is_amb else [f"{ing} 有机", ing]
        for q in queries:
            if len(result) >= 2:
                break
            for page in range(1, 4):
                if len(result) >= 2:
                    break
                try:
                    items = shop._search_taobao(q, page, 10, "")
                except Exception:
                    items = []
                if not items:
                    continue
                for item in items:
                    if len(result) >= 2:
                        break
                    title = item.get('title', '')
                    brand = item.get('shop_name', '') or ''
                    # 标题必须包含完整食材关键词（不限制位置）
                    if ing.lower() not in title.lower():
                        continue
                    # 易混淆药材：排除日用品（帽/玻璃/挡风/针织等）
                    if is_amb and any(w in title for w in ['帽', '玻璃', '挡风', '针织', '婴', '童', '罩', '板', '衣', '杯', '睡袋', '包巾', '安抚', 't恤', 'T恤', '服饰', '母婴']):
                        continue
                    if title and not shop._is_excluded(item):
                        if brand not in local_brands:
                            local_brands.add(brand)
                            result.append(item)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_map = {executor.submit(search_one, ing): ing for ing in ingredient_names}
        concurrent.futures.wait(future_map, timeout=20)
        # 按原食材顺序收集结果
        for ing in ingredient_names:
            for future in future_map:
                if future_map[future] == ing:
                    try:
                        items = future.result()
                        products.extend(items)
                    except Exception:
                        pass
                    break

    return products
