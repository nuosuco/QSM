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

SYSTEM_PROMPT = """你是小麦SOM，一位温暖、专业、有耐心的中医养生顾问。你是用户终生的健康生活伴侣。

你的职责：
1. 认真倾听用户的身体描述，用通俗语言分析可能的体质倾向
2. 基于药食同源知识，给出实用的食养建议（配方+用法）
3. 语气温和亲切，像老朋友聊天，不说教、不吓唬人
4. 每次回复结尾加一句：以上为养生文化参考，身体不适请及时就医

【商品推荐机制（你必须知道）】
- 系统会自动在你回复下方展示有机商品卡片（带图片、价格、购买链接）
- 你不需要说"不能发链接"，商品卡片会自动出现
- 当你给出食谱建议时，自然地提一句："对应的有机食材我帮你找好了，就在下面哦～"
- 用户问"哪里买""链接""推荐"时，告诉他："就在下方推荐里，点击就能购买～"
- 不要编造具体商品名或价格，商品由系统自动匹配

重要规则：
- 不做医疗诊断，不说"你得了XX病"
- 不用"治疗""治愈""根治"等医疗用语，用"调养""食养""参考"
- 配方必须来自药食同源目录，不推荐药材
- 如果用户描述严重症状，优先建议就医，再给辅助食养参考
- 回复控制在300字以内，简洁有用
- 记住用户之前说过的身体状况，像老朋友一样关心他/她"""


def _build_user_profile_context(user_id: str) -> str:
    """构建用户终身档案：历史对话 + 体质记录，让小麦“认识”老用户"""
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

        # 体质记录（最近3条）
        try:
            rows = conn.execute(
                "SELECT tizhi, zhengxing, symptoms, created_at FROM tizhi_records WHERE user_id=? ORDER BY created_at DESC LIMIT 3",
                (user_id,)
            ).fetchall()
            if rows:
                tizhi_lines = []
                for r in rows:
                    line = f"{r['created_at'][:10]} 体质:{r['tizhi'] or '未定'}"
                    if r['symptoms']:
                        line += f" 症状:{r['symptoms'][:40]}"
                    tizhi_lines.append(line)
                parts.append("【用户体质档案】\n" + "\n".join(tizhi_lines))
        except Exception:
            pass

        # 历史对话（最近10条，跨会话）
        try:
            rows = conn.execute(
                "SELECT user_message, assistant_reply, created_at FROM chat_history WHERE user_id=? ORDER BY created_at DESC LIMIT 10",
                (user_id,)
            ).fetchall()
            if rows:
                hist_lines = []
                for r in reversed(rows):  # 时间正序
                    hist_lines.append(f"[{r['created_at'][:16]}] 用户:{(r['user_message'] or '')[:60]}")
                    hist_lines.append(f"    小麦:{(r['assistant_reply'] or '')[:80]}")
                parts.append("【历史对话记录（你和这位用户之前的交流）】\n" + "\n".join(hist_lines))
        except Exception:
            pass

        conn.close()
        if parts:
            return "\n\n".join(parts) + "\n\n【重要】你认识这位用户，请像老朋友一样关心他/她，记住他/她之前的身体状况，主动跟进关心。"
    except Exception:
        pass
    return ""


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

    # 5. 从回复中提取食材名，搜索商品（传入证型+用户消息+历史）
    products = _search_products_from_reply(
        reply, recommendations, zhengxing=zhengxing,
        user_message=user_message, history=history
    )

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


def _search_products_from_reply(reply: str, recommendations: list, zhengxing: str = None,
                               user_message: str = "", history: list = None) -> list:
    """从回复文本中提取食材名，并行搜索商品"""
    from services.shop import ShopService
    from services.bianzheng import SHILIAO_DB
    import concurrent.futures

    # 提取食材名
    ingredient_names = []

    # 方法1：从配方文字提取（LLM 回复带"配方："格式时）
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

    # 方法2：从食疗方数据库提取（按证型查 SHILIAO_DB，恢复原版5食材逻辑）
    if not ingredient_names and zhengxing:
        # zhengxing 可能是 "气虚、脾虚湿盛" 这种多证型
        for zheng in zhengxing.split('、'):
            zheng = zheng.strip()
            shiliao = SHILIAO_DB.get(zheng)
            if shiliao and shiliao.get('recipe'):
                parts = re.split(r'[、,，;；]', shiliao['recipe'])
                for part in parts:
                    part = part.strip()
                    name = re.sub(r'[\d.]+(?:[gG克毫升mlML枚粒只条根片块个半只碗勺杯袋包瓶盒罐]*)', '', part).strip()
                    name = re.sub(r'(半只|少许|适量|若干|少量|各)$', '', name).strip()
                    # 过滤掉非食材（粳米、冰糖、红糖等主食/调料）
                    skip = ['粳米', '冰糖', '红糖', '水', '盐', '调味']
                    if name and 2 <= len(name) <= 6 and name not in ingredient_names and name not in skip:
                        ingredient_names.append(name)
                if ingredient_names:
                    break  # 用一个证型的食疗方就够了

    # 方法3：从推荐列表提取
    if not ingredient_names:
        ingredient_names = [r.get("name", "") for r in recommendations if r.get("name")]

    # 方法4：当前消息无匹配时，从历史对话中提取食材（用户追问"链接""推荐"时）
    if not ingredient_names and history:
        # 从历史 assistant 回复中提取配方
        for msg in reversed(history):
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                # 先试配方匹配
                hist_recipe = re.findall(r'配方[：:](.+?)(?:\n|—|：|。)', content, re.DOTALL)
                if hist_recipe:
                    parts = re.split(r'[、,，;；]', hist_recipe[0])
                    for part in parts:
                        part = part.strip()
                        name = re.sub(r'[\d.]+(?:[gG克毫升mlML枚粒只条根片块个半只碗勺杯袋包瓶盒罐]*)', '', part).strip()
                        name = re.sub(r'(半只|少许|适量|若干|少量|各)$', '', name).strip()
                        if name and 2 <= len(name) <= 6 and name not in ingredient_names:
                            ingredient_names.append(name)
                if ingredient_names:
                    break
                # 再试常见食材匹配
                common_foods = ['枸杞', '红枣', '山药', '薏米', '茯苓', '百合', '莲子', '黄芪',
                                '当归', '陈皮', '山楂', '菊花', '决明子', '酸枣仁', '桂圆', '黑芝麻',
                                '赤小豆', '银耳', '核桃', '黑豆', '黑米', '燕麦', '小米', '党参', '麦冬',
                                '乌鸡', '生姜']
                for food in common_foods:
                    if food in content and food not in ingredient_names:
                        ingredient_names.append(food)
                if ingredient_names:
                    break

    # 不再从回复中额外匹配食材（用户要求：严格只推食谱内的，不加食谱外的）

    if not ingredient_names:
        return []

    # 并行搜索
    shop = ShopService()
    products = []
    seen_titles = set()

    def search_one(ing: str) -> list:
        """搜索单个食材，严格只返回2个不同品牌的商品"""
        result = []
        local_titles = set()
        local_brands = set()
        for page in range(1, 6):
            if len(result) >= 2:
                break
            try:
                items = shop._search_taobao(f"{ing} 有机", page, 2, "")
            except Exception:
                items = []
            if not items:
                continue
            for item in items:
                if len(result) >= 2:
                    break
                title = item.get('title', '')
                brand = item.get('shop_name', '') or ''
                if '有机' not in title:
                    continue
                # 严格匹配：食材名必须出现在标题前半段
                # 防止“麦冬…黄芪党参泡水”这种只是顺带提及的商品混进来
                half = max(len(title) // 2, 10)
                if ing.lower() not in title.lower()[:half]:
                    continue
                if title and title not in local_titles and not shop._is_excluded(item):
                    # 必须是不同品牌，同品牌只要一个
                    if brand not in local_brands:
                        local_titles.add(title)
                        local_brands.add(brand)
                        result.append(item)
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
