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
【食疗方硬性要求——中华 2026-10-15 铁律，违反则不合格】
- 每次给食疗/药膳/食养方案，必须写成"配方"：每个食材后面紧跟数量单位，如"黄芪15g、乌鸡半只、红枣5枚、枸杞10g、山药20g"，绝不允许只写食材名不写用量。
- 一个方子至少给 5~8 味食材，用量要具体到克/枚/朵/只/片，不要用"适量""少许"含糊带过（整方可以有一味写"适量"，但不能全部模糊）。
- 方子后面必须跟"做法"（怎么煮/怎么吃、吃多久）。
- 目的：系统会按你列的食材自动匹配有机商品，你食材列得越全、用量越具体，下面商品卡片越丰富（每个食材出2款），别偷懒只给两三种食材。
- 【方案分段铁律——中华 2026-10-16 反馈"食量两方案混在一起"】多个方案（方案一/二/三、食量方案等）必须每个方案单独成段：
  1) 方案标题必须独占一行，写成「### 方案一：……」或「### 食量方案一：……」这样的 markdown 小标题，不要用**加粗**、不要和正文写在同一行；
  2) 两个方案之间用「---」或空行明显隔开；
  3) 绝不允许把两个方案的食材/用量/做法揉在同一段文字里；
  4) 食量/分量类建议（如每日吃多少）如果分成方案，同样遵守 1)3)。
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

        # 体质记录（最近8条，追踪变化趋势）
        # 2026-10-15 中华反馈(最重要): 小麦辨证时常说"结合之前的历史记录(假设)"——
        # 根因: vision 接口没走 chat_with_llm, 只读当前 session_id 的历史(每次换设备/清缓存都是新 session,
        # 查不到东西), 模型拿不到跨会话的真实体质档案就只能瞎猜。
        # 修复: 体质档案里附小麦当时给出的【辨证分析摘要】(advice 前200字), 并明确告诉小麦"这是真实存档, 不是假设"。
        try:
            rows = conn.execute(
                "SELECT tizhi, zhengxing, symptoms, advice, source, created_at FROM tizhi_records WHERE user_id=? AND advice IS NOT NULL AND advice != '' ORDER BY created_at DESC LIMIT 8",
                (user_id,)
            ).fetchall()
            if rows:
                tizhi_lines = []
                for r in reversed(rows):  # 时间正序: 旧的在前, 新的在后
                    line = f"{r['created_at'][:10]} 体质:{r['tizhi'] or '未定'}"
                    if r['zhengxing']:
                        line += f" 证型:{r['zhengxing']}"
                    if r['symptoms'] and r['source'] != 'vision_chat':
                        line += f" 症状:{r['symptoms'][:50]}"
                    if r['advice']:
                        line += f"\n    当时辨证分析:{str(r['advice'])[:200].replace(chr(10), ' ')}"
                    tizhi_lines.append(line)
                parts.append(
                    "【用户体质档案（这是该用户历史存档的真实记录，不是假设！）】\n"
                    + "\n".join(tizhi_lines) +
                    "\n以上为系统从健康档案读取的真实历史数据。涉及\"之前/上次/历史\"的表述时必须以此为准，"
                    "不得凭空假设；档案里没有的信息就明确说明没有记录，不得编造。"
                )
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
        from datetime import datetime
        from services.jieqi import get_jieqi_advice
        advice = get_jieqi_advice()
        if advice and advice.get('jieqi'):
            now = datetime.now()
            lines = [
                f"【今天是 {now.year}年{now.month}月{now.day}日，当前节气：{advice['jieqi']}（{advice.get('season','')}季）】",
                f"⚠️ 以上日期和节气是系统实时计算的，绝对准确。如果历史对话中出现不同的节气/日期描述，那是旧数据，必须忽略，以本条为准！",
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

    # 7. 末尾追加AI生成提示（小程序审核要求）
    reply += "\n\n_以上内容由人工智能生成，仅供参考。_".replace("\n\n", "\n\n")

    return {
        "reply": reply,
        "tizhi": tizhi,
        "zhengxing": zhengxing,
        "recommendations": recommendations,
        "products": products,
        "provider": llm_result.get("provider", "fallback"),
        "model": llm_result.get("model", "bianzheng_engine"),
    }


def _extract_ingredient_plan_map(reply: str) -> list:
    """返回 [(食材名, 所属方案标签), ...]; 老格式/无分段时标签为 ''(前端显示为通用推荐)。
    2026-10-16 小蕊加(中华反馈「方案二方案三商品没输出」): 前端商品卡片按方案分组显示。"""
    names, labels = _extract_ingredients_labeled(reply)
    return list(zip(names, labels))


def _extract_ingredients_from_reply(reply: str) -> list:
    """从回复中提取所有食材（含多食谱方案食材），按出现顺序返回去重食材名, 不过滤排骨/猪骨

    2026-10-16 小蕊改(中华反馈「方案二方案三商品没输出」):
    旧版全篇正则会把「做法」里的句子(加清水/小火煲/连续7天/冲入沸水...)误当食材,
    且全篇匹配后去重, 共享食材(红枣/麦冬)被方案一占用, 方案二三的独有食材搜索被挤掉。
    新逻辑: 先按「方案一/方案二/方案三」(或 食谱一/食疗方N)分段, 每段只从【配方行】提食材,
    每段单独去重后按方案顺序拼接 → 3 个方案的食材全部进商品搜索, 卡片按方案分组。"""
    import re as _re

    # 分段: 匹配 方案一/方案二/方案三/方案1-9/食谱一/食疗方二/方子一 等段头
    _seg_pat = _re.compile(
        r'(?:^|\n)\s*(?:###?\s*)?(?:方案|食谱|食疗方|调理方|药膳方|方子)\s*([一二三1-9])\s*[:：、]?')
    names, labels = _extract_ingredients_labeled(reply)
    return names


def _extract_ingredients_labeled(reply: str) -> tuple:
    """返回 (食材名列表去重, 对应方案标签列表); 老格式标签为 \'\'
    2026-10-16 小蕊重写(中华反馈「方案二三没商品」): 逐行识别「方案N」段头,
    段内只认真配方行(食材+用量结构), 做法/加料/调味/分隔线一律不进食材提取。
    老格式(无方案分段)回退全篇提取(剥做法段), 保持旧行为不炸。"""
    import re as _re2
    lines = reply.split('\n')
    # 1) 逐行找「方案一/二/三」段头(行首, 可带 markdown 井号), 避免正文里的「方案一」字样误判
    _head_pat = _re2.compile(r'^[\s#*]*(?:食量|份量|剂量|用量)?(?:方案|食谱|食疗方|调理方|药膳方|方子|食材方|药膳)(?:\s*([一二三四五六七八九1-9]))?[:：、]?')
    _NUM_CN = {'一':'一','二':'二','三':'三','4':'四','5':'五','6':'六','7':'七','8':'八','9':'九'}
    segs = []  # [(方案标签, 段内行文本)]
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        m2 = _head_pat.match(s)
        if m2:
            end = i + 1
            while end < len(lines):
                s2 = lines[end].strip()
                if _head_pat.match(s2):
                    break
                end += 1
            # 2026-10-16 小蕊补: 无序号段头(如「食疗方:」「食谱:」) → 标签''(通用推荐, 前端分组为「推荐商品」)
            # 段内统一 = 段头行段头之后的文字(如有) + 后续行(直到下一段头/段尾)
            tail = s[m2.end():].strip()
            seg_lines = ([tail] if tail else []) + lines[i+1:end]
            # 2026-10-16 小蕊补(中华反馈「食量两方案没分段」): LLM 可能写「食量方案一」「份量方案二」,
            # 段头带「食量/份量/剂量/用量」前缀时也认段头, 标签保留前缀(前端商品卡按标签分组, 食量方案一般无配方行, 不影响)
            prefix = ''
            for _p in ('食量方案', '份量方案', '剂量方案', '用量方案'):
                if s.startswith(_p):
                    prefix = _p[:2]  # 食量/份量/剂量/用量
                    break
            if m2.group(1):
                num_cn = _NUM_CN.get(m2.group(1), m2.group(1))
                segs.append((f"{prefix}方案{num_cn}" if prefix else f"方案{num_cn}", '\n'.join(seg_lines)))
            else:
                segs.append(('', '\n'.join(seg_lines)))
            i = end
        else:
            i += 1

    seen = set()
    out_names = []
    out_labels = []

    def _push(name, label):
        if name not in seen:
            seen.add(name)
            out_names.append(name)
            out_labels.append(label)

    def _append(name, label):
        out_names.append(name)
        out_labels.append(label)

    if not segs:
        # 老格式/单方/纯文字聊天: 全篇提取, 只剥「独立 做法:」行(锚行首), 行内「。做法:」不影响
        # (行内老格式「食疗方：黄芪15g...。做法：煮水...」做法词在行中, 不剥, 全篇提食材不丢)
        whole = _re2.sub(
            r'(?:^|\n)\s*(?:[-*#]*\s*)?(?:做法|食用方法|服用方法|步骤|喝法|用法|材料处理)\s*[：:]?[\s\S]*$',
            '', reply, flags=_re2.M)
        _extract_from_text(whole, seen, out_names, push=_append)
        return out_names, out_labels

    # 2) 多方案: 段内只认真配方行(含「食材+用量」结构)
    # 用量结构: 数字(可带 ~区间) + 单位(g/克/毫升/ml/朵/片/枚/粒/只/条/根/块/个/碗/勺/杯/袋/包/瓶/盒/罐/颗/斤/两),
    # 或 中药剂量单位(钱), 或 半/适量/少许。食材名为 2-6 汉字。
    _dosage_re = _re2.compile(
        r'([一-龥]{2,6})\s*[：:]?\s*[（(]?\s*'
        r'(?:\d+(?:[-~]\d+)?|半|适量|少许)'
        r'\s*'
        r'[gG克毫升mlML朵片枚粒只条根块个碗勺杯袋包瓶盒罐颗斤两钱]?')
    for label, seg_text in segs:
        # 段内逐行: 只保留「真配方行」——含 食材+用量 结构, 且不是做法/加料/调味/分隔线
        recipe_lines = []
        for ln in seg_text.split('\n'):
            s = ln.strip().lstrip('#').strip()
            s = s.replace('**', '').strip()
            # 分隔线/空行/标题行直接跳
            if not s or s.startswith('---') or s.startswith('***'):
                continue
            # 做法/加料/调味/频率句子一律排除(不进食材提取)
            if _re2.search(
                r'做法|食用方法|服用方法|步骤|喝法|用法|材料处理|提前|加料|加水|加清水|加盐|调味|煲汤|煮粥|焖|冲泡|代茶|取出|放入|砂锅|保温杯|去渣|药包|焯水|浸泡|煮沸|小火|大火|烧开后|转为|连服|每周|每日|隔日',
                s):
                continue
            # 真配方行: 至少有一个 食材+用量 结构匹配(如「沙参15g」「银耳半朵」「瘦肉150g」)
            if _dosage_re.search(s):
                recipe_lines.append(s)
        if recipe_lines:
            _extract_from_text(' '.join(recipe_lines), seen, out_names, push=_append, label=label)
        else:
            # 2026-10-16 小蕊补(中华反馈「老格式食疗方商品没了」):
            # 段内无真配方行(如老格式单行「食疗方：黄芪15g...。做法：...」被做法词整行排除),
            # 回退整段全篇提取(不剥行内做法), 兼容老格式不丢食材。
            _extract_from_text(seg_text, seen, out_names, push=_append, label=label)
    return out_names, out_labels


def _extract_from_text(text: str, seen: set, out: list, push=None, label: str = ""):
    """从一段配方文本提食材(食材名+用量), 全回复级去重(seen)。
    push(name, label) 钩子: 有则用它记录(支持方案标签); 无则直接 out.append(name)(老调用兼容)。"""
    import re as _re
    # 2026-10-16 小蕊补(中华反馈「商品还是只有2个」):
    # 正则贪婪匹配「中文2-6字 + 数字/适量/少许」时, 会把小标题、功效词、症状词
    # 当食材(如「食养建议」「健脾补气」「为主」), 白白占用匹配名额,
    # 导致下方商品卡片偏少。补全过滤词表。
    skip_words = {
        # 原过滤词
        '水', '盐', '调味', '给你', '每周', '每天', '每次', '每日',
        '连吃', '连服', '煮水', '煮粥', '代茶饮', '方子', '食谱', '食材',
        '分钟', '小时',
        # 标题 / 引导词
        '食养建议', '食疗建议', '食疗方', '食疗方案', '养生建议', '养生方',
        '调理方案', '调理方', '推荐', '建议', '饮食禁忌', '忌口',
        '综合判断', '综合辨证', '辨证', '体质', '体质倾向', '主证', '兼证',
        '要点', '分析', '观察', '望诊', '舌诊', '面诊', '舌象', '舌色',
        '舌苔', '舌形', '面色', '唇色', '皮疹', '趋势', '变化', '结论',
        '总结', '参考', '分析要点',
        '多吃', '少吃', '避免', '尽量', '不宜', '可以适当',
        '配合', '搭配', '注意', '禁忌', '为主', '为主食', '适量用',
        # 功效词（模型常用 4-6 字，最容易被误当食材）
        '健脾补气', '健脾益气', '补气养血', '益气养血', '补气生津',
        '滋阴清热', '滋阴润燥', '益气养阴', '养阴清热', '益气健脾',
        '健脾祛湿', '祛湿化痰', '清热解毒', '温补脾肾', '温阳散寒',
        '活血化瘀', '疏肝理气', '固表止汗', '生津止渴', '平肝潜阳',
        '补肾固精', '安神助眠', '宁心安神', '润肺止咳', '养心安神',
        '补肝肾', '益肝肾', '健脾', '益气', '养阴', '清热',
        '滋阴', '祛湿', '化湿', '理气', '活血', '化瘀', '安神', '养血',
        # 做法步骤词(中华反馈 2026-10-16: 做法句子被误当食材)
        '加清水', '大火', '小火', '砂锅', '煮至', '转小火', '沸后', '后转',
        '大火烧', '烧开后', '焯水', '泡发', '提前浸泡', '纱布包', '药包',
        '待水', '降温', '冲入', '焖泡', '反复冲泡', '可反复', '食用', '连服',
        '每日', '连续', '每周', '早晚', '温热食用', '调味', '去渣', '取药',
        # 做法动词短语(中华反馈 2026-10-16: 「开后转小火煲/所有材料加水/芡实提前浸泡」混进食材)
        '转小火煲', '转小火', '小火煮', '大火煮', '小火煲', '大火烧', '烧开后',
        '开后转', '所有材料', '材料加', '材料放', '提前浸泡', '提前泡', '提前',
        '洗净', '洗净切', '切块', '切小', '撕小朵', '焯水', '沸后', '水开后',
        '加水', '加入', '取出', '放砂锅', '砂锅', '保温杯', '冲入沸水',
        '焖', '焖泡', '泡水', '冲泡', '煮至', '煮粥', '煲汤', '代茶饮', '代茶',
        '食用', '服用', '温热', '温服', '趁热', '待凉', '放凉', '加少许', '调味',
        # 整句做法片段(2-6字贪婪匹配截出来的句子碎片, 中华反馈 2026-10-16)
        '开后转小火煲', '开后转小火', '转小火煲一小时', '小火煲一小时',
        '大火烧开后', '烧开后转', '煮沸后', '沸腾', '水开后', '沸后',
        # 食量/份量类(中华反馈 2026-10-16「食量两方案」): 非食材, 不进商品搜索
        '食量', '份量', '剂量', '用量', '每日食量', '连用', '分早晚', '早晚各',
        '两次', '一次', '天量', '餐量', '饭量',
    }

    # 1. 匹配所有 "食材名+用量" 的模式，兼容多种 LLM 输出格式：
    #    黄芪15g / 黄芪：15g / 黄芪（15g）/ 乌鸡半只 / 红枣5枚 / 黄芪15-20g / 冰糖适量
    dosage_pattern = (
        r"([一-龥]{2,6})"          # 食材名（2-6个汉字）
        r"\s*[：:]?\s*"            # 可选冒号（中英文）
        r"[（(]?\s*"               # 可选左括号
        r"(?:\d+(?:[-~]\d+)?|半|适量|少许)"  # 数字（可带范围）/半/适量/少许
        r"\s*"
        r"[gG克毫升mlML朵片枚粒只条根块个碗勺杯袋包瓶盒罐颗斤两]?"  # 单位（适量/少许时可省略）
    )
    matches = _re.findall(dosage_pattern, text)
    for m in matches:
        m = m.strip()
        if m not in seen and m not in skip_words and 2 <= len(m) <= 6:
            seen.add(m)
            (push(m, label) if push else out.append(m))

    # 2. 提取肉类/禽类食材（排骨、猪骨、乌鸡、瘦肉等，它们就是需要推荐的食材）
    meat_pattern = r"(?:加)?(排骨|猪骨|乌鸡|鸡肉|瘦肉|羊肉|牛肉|鸭肉|鸽子|鲫鱼|鲈鱼|猪蹄)"
    meat_matches = _re.findall(meat_pattern, text)
    for m in meat_matches:
        m_clean = m.strip()
        if m_clean not in seen and 2 <= len(m_clean) <= 6:
            seen.add(m_clean)
            (push(m_clean, label) if push else out.append(m_clean))


def _search_products_from_reply(reply: str, recommendations: list, zhengxing: str = None,
                               user_message: str = "", history: list = None) -> list:
    """从回复文本中提取食材名，按食谱顺序每个食材推荐2款不同品牌商品"""
    from services.shop import ShopService
    import concurrent.futures

    # 1. 从回复中按食谱顺序提取所有食材
    ingredient_names, plan_labels = _extract_ingredients_labeled(reply)
    # 每个食材对应的方案标签(与 ingredient_names 一一对应); 前端按标签分组展示商品卡片
    _ing_plan = dict(zip(ingredient_names, plan_labels))

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

    # 食材别名表：标题里不一定出现原词（如"大米"商品标题常写"有机米/五常大米/稻花香"）
    # 匹配标题时，原词或任一别名命中即算匹配；搜索词也用别名扩展提高命中率
    INGREDIENT_ALIASES = {
        '大米': ['米', '稻花香', '粳米', '五常大米', '东北大米', '珍珠米', '胚芽米'],
        '老鸭': ['鸭', '老鸭', '麻鸭'],
        '乌鸡': ['乌鸡', '乌骨鸡'],
        '排骨': ['排骨', '肋排', '猪排骨'],
        '瘦肉': ['瘦肉', '猪瘦肉', '里脊'],
        '生姜': ['生姜', '姜', '老姜', '嫩姜'],
        '薏米': ['薏米', '薏仁', '薏苡仁'],
        '山药': ['山药', '淮山', '铁棍山药'],
        '绿豆': ['绿豆'],
        '莲藕': ['莲藕', '藕', '莲菜'],
        '苦瓜': ['苦瓜'],
        '陈皮': ['陈皮', '新会陈皮'],
        '茯苓': ['茯苓', '云苓'],
        '冰糖': ['冰糖', '黄冰糖', '老冰糖', '多晶冰糖'],
    }

    # 加工制品排除词：松麦只推原材料食材，不推加工饮品/保健品
    PROCESSED_EXCLUDE = ['原浆', '口服液', '饮料', '饮品', '冲剂', '胶囊', '片剂', '丸剂', '糖浆',
                         '精华液', '面膜', '护肤', '注射', '颗粒剂', '含片', '泡腾片', '软糖',
                         '代餐', '奶昔', '果汁', '酵素', '益生菌粉',
                         '膏方', '养生膏', '桑椹膏', '秋梨膏', '阿胶膏', '固元膏']

    # 全局非食材排除："有机玻璃/有机板/有机盒"等日用品，标题带"有机"但不是食材
    # 对所有食材搜索生效（不只易混淆药材）
    NON_FOOD_EXCLUDE = ['玻璃', '亚克力', '压克力', '卡槽', '插槽', '插纸', '展示架', '展示盒',
                        '收纳盒', '收纳箱', '置物架', '相框', '画框', '标牌', '广告牌',
                        '板材', '片材', '管材', '型材', '零件', '配件', '模具',
                        '玩具', '文具', '办公', '家具', '灯具', '窗帘', '地毯',
                        '搅拌机', '反应器', '反应釜', '反应罐', '储罐', '容器', '塔器',
                        '振动筛', '颗粒机', '制粒机', '粉体', '粉料', '不锈钢',
                        '粉碎机', '研磨机', '打粉机', '切片机', '烘干机', '包装机', '封口机']

    def search_one(ing: str) -> list:
        """搜索单个食材，严格只返回2个不同品牌的有机认证商品。
        铁律：标题必须含"有机"，必须是原材料食材，不推加工制品。"""
        result = []
        local_brands = set()
        is_amb = ing in AMBIGUOUS
        aliases = INGREDIENT_ALIASES.get(ing, [])
        # 搜索词：始终带"有机"，原词+别名扩展提高命中率
        queries = [f"{ing} 有机", f"有机 {ing}", f"有机{ing}"]
        for al in aliases[:3]:
            if al != ing:
                queries.append(f"有机 {al}")
        if is_amb:
            queries.append(f"有机 {ing} 中药材")

        def _title_match(title: str) -> bool:
            """标题是否命中该食材（原词或任一别名）"""
            tl = title.lower()
            if ing.lower() in tl:
                return True
            return any(al.lower() in tl for al in aliases)

        for q in queries:
            if len(result) >= 2:
                break
            # 2026-10-17 中华铁律(90s总预算): 每查询词最多翻 4 页(40个商品位),
            # 凑够 2 个不同品牌就停; 翻页上限收紧, 单次搜索不再死磕, 保整体耗时
            for page in range(1, 5):
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
                    # 铁律1：标题必须含"有机"（松麦只卖有机认证）
                    if '有机' not in title:
                        continue
                    # 铁律2：食材必须是商品主体，不能只是搭配提及
                    # 如"有机玉竹...搭沙参麦冬百合煲汤"，百合只是搭配，商品是玉竹
                    if not _title_match(title):
                        continue
                    # 检查食材是否出现在"搭/送/赠"之前（之后的是搭配推荐，不是商品本身）
                    main_part = title
                    for sep in ['搭', '送', '赠']:
                        idx = title.find(sep)
                        if 0 < idx < len(main_part):
                            main_part = title[:idx]
                    if not _title_match(main_part):
                        continue
                    # 铁律3：排除加工制品（原浆/口服液/饮品等不是食材）
                    if any(w in title for w in PROCESSED_EXCLUDE):
                        continue
                    # 铁律4：全局排除非食材日用品（有机玻璃/亚克力/卡槽等）
                    if any(w in title for w in NON_FOOD_EXCLUDE):
                        continue
                    # 易混淆药材：额外排除日用品（帽/挡风/针织等）
                    if is_amb and any(w in title for w in ['帽', '挡风', '针织', '婴', '童', '罩', '衣', '杯', '睡袋', '包巾', '安抚', 't恤', 'T恤', '服饰', '母婴']):
                        continue
                    if title and not shop._is_excluded(item):
                        if brand not in local_brands:
                            local_brands.add(brand)
                            result.append(item)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_map = {executor.submit(search_one, ing): ing for ing in ingredient_names}
        # 2026-10-17 中华铁律: 辨证总耗时不超过90秒。
        # LLM视觉最多90s, 商品搜索并发收结果最多30s(凑到多少回多少), 保证整体不超90s
        concurrent.futures.wait(future_map, timeout=30)
        # 按原食材顺序收集结果, 每个商品打上所属方案标签(前端按方案分组显示商品卡片)
        for ing in ingredient_names:
            for future in future_map:
                if future_map[future] == ing:
                    try:
                        items = future.result()
                        plan = _ing_plan.get(ing, '')
                        for it in items:
                            it['plan'] = plan  # 方案一/二/三, 老格式为 ''
                            products.append(it)
                    except Exception:
                        pass
                    break

    return products
import re

# 症状关键词(命中即认为该句在自述症状)
_symptom_kw = [
    "瘙痒", "痒", "疼", "痛", "红肿", "皮疹", "起疹", "湿疹", "风团", "荨麻疹", "疱疹", "水泡",
    "口干", "口苦", "口臭", "反酸", "胃酸", "烧心", "胃胀", "腹胀", "腹痛", "腹泻", "拉肚子",
    "便秘", "便溏", "便稀", "尿频", "尿急", "夜尿", "失眠", "多梦", "嗜睡", "乏力", "疲倦",
    "气短", "胸闷", "心悸", "心慌", "盗汗", "自汗", "怕冷", "怕热", "畏寒", "畏风", "手脚冰凉",
    "潮热", "腰膝酸软", "腰酸", "腿软", "脱发", "掉发", "月经", "痛经", "白带", "咳嗽",
    "咳", "痰多", "咽干", "咽痒", "喉咙", "鼻塞", "流涕", "水肿", "浮肿", "虚胖", "消瘦",
    "口疮", "溃疡", "牙龈", "关节痛", "关节", "酸痛", "麻木", "抽筋", "恶心", "呕吐",
    "没胃口", "食欲", "消化不良", "打嗝", "嗳气", "反胃", "多汗", "冷汗", "耳鸣", "眼干", "眼涩",
]
_seen = set()
_SYMPTOM_KW = [k for k in _symptom_kw if not (k in _seen or _seen.add(k))]
# 长短有序: 先匹配长词(瘙痒 先于 痒), 加粗时不叠星号
_SYMPTOM_KW_SORTED = sorted(_SYMPTOM_KW, key=len, reverse=True)

# "已好"状态词
# "已好"状态词(2026-10-22 中华定论: 必须是【确定彻底好了】才进已好转台账开撤方计时; "减轻了/缓解了/好多了"等是【还没彻底好】的意思, 不进台账, 仍按主诉对照)
_RESOLVED_KW = ["已经好", "早就好", "好了", "痊愈", "没事了", "现在不", "不痒了", "不痛了", "不疼了", "不发作", "没有了"]
# 2026-10-22 中华定论: "减轻了/缓解了/好多了"是"还没彻底好", 不进已好转台账(不算撤方计时), 仍按主诉/观察对照。只有上面这些明确的"已好"词才开 D 天计时。
# "假症状"状态词(用户明确否认/口误, 优先级最高)
_FAKE_KW = ["打错字", "打错了", "打错", "说错", "误打", "误说", "其实是", "搞错", "弄错", "没有这个症状", "没有此症状", "并不是", "不是"]

_SENT_SPLIT = re.compile(r"[。！？；!?\n]+")


def _find_symptom_kws(msg):
    """找出该消息里提到的症状词(去重, 按长度排)。"""
    return [kw for kw in _SYMPTOM_KW_SORTED if kw in msg]


def _classify_one(msg, created_at):
    """对单条用户消息分类: 返回 (kind, symptom, line, date) 或 None。"""
    msg = (msg or "").strip()
    if not msg:
        return None
    hits = _find_symptom_kws(msg)
    # 先判 fake
    kind = None
    for fk in _FAKE_KW:
        if fk in msg:
            kind = "fake"
            break
    if kind is None:
        for rk in _RESOLVED_KW:
            if rk in msg:
                kind = "resolved"
                break
    if kind is None and not hits:
        return None
    if kind is None:
        kind = "complaint"
    # fake 且没提到具体症状词时, 也接受(用户泛泛说"刚才那个是打错的")
    if kind == "fake" and not hits:
        # 找含 fake 词的句段
        sents = [s.strip() for s in _SENT_SPLIT.split(msg) if s.strip()]
        best = msg[:80]
        for s in sents:
            if any(fk in s for fk in _FAKE_KW):
                best = s
                break
        return ("fake", "", best, (created_at or "")[:10])
    # 取命中症状词最多的句段
    sents = [s.strip() for s in _SENT_SPLIT.split(msg) if s.strip()]
    best, best_score = msg[:80], 0
    for s in sents:
        sc = sum(1 for kw in hits if kw in s)
        if sc > best_score:
            best, best_score = s, sc
    if not hits:
        return ("complaint", "", best, (created_at or "")[:10])
    # 症状词加粗: 先用占位符避免短词命中已替换的长词(叠星号)
    s = best
    for i, kw in enumerate(hits):
        s = s.replace(kw, f"\x00{i}\x00")
    for i, kw in enumerate(hits):
        s = s.replace(f"\x00{i}\x00", f"**{kw}**")
    return (kind, hits[0], s, (created_at or "")[:10])


def extract_user_symptoms(rows):
    """rows: [(user_message, created_at), ...] 时间正序。
    返回 {"complaint": [...], "resolved": [...], "fake": [...]}。
    按症状名去重, 同症状多状态时取【最近一次】的状态(后发生的覆盖先前的)。"""
    # 每个症状名: 记最后一条 (kind, line, date) + 巩固台账(consol_count=已好后再确认已好的次数)
    last_by_sym = {}
    for um, ca in rows:
        r = _classify_one(um, ca)
        if not r:
            continue
        kind, sym, line, date = r
        if not sym:
            # 无具体症状词的 fake 单独记
            key = "|fake"
            last_by_sym[key] = {"kind": "fake", "line": line, "date": date}
            continue
        key = sym
        rec = last_by_sym.get(key)
        if rec is None or rec["date"] <= date:
            if rec is None:
                rec = {"kind": kind, "line": line, "date": date,
                       "consol_count": 0, "first_complaint_date": None, "resolved_date": None}
            # 首次 complaint 记日期(给"隔了多久"用)
            if kind == "complaint" and rec["first_complaint_date"] is None:
                rec["first_complaint_date"] = date
            # 已好: 第一次记 resolved_date; 之后每次再出现"已好"=一次巩固(consol_count+1)
            if kind == "resolved":
                if rec["resolved_date"] is None:
                    rec["resolved_date"] = date
                elif date != rec["resolved_date"]:
                    rec["consol_count"] += 1
            # 已好又被复发(变回 complaint) → 巩固清零重来
            if kind == "complaint" and rec["resolved_date"] is not None:
                rec["consol_count"] = 0
            last_by_sym[key] = rec
    out = {"complaint": [], "resolved": [], "fake": []}
    for key, v in last_by_sym.items():
        sym = key if key and not key.startswith("|") else ""
        prefix = f"- {v['date']} 自述【{sym}】" if sym else f"- {v['date']}"
        if v["kind"] == "resolved":
            # 给小麦可数的巩固台账: 已好日期 + 巩固次数, 让它自己推理该减没减
            extra = f"【已好·巩固{v['consol_count']}次】" if v.get("consol_count") else "【已好】"
            # 2026-10-22 改"按时间撤方": 用户"已好"通常只说一次, N 不会涨, 撤减必须按
            # "说好之后过了几天"算(7天内可留巩固食材; 7天起默认不再加, 仅提示防复发)。
            # 这里把 resolved_date 与当前日期差算出来喂给小麦, 让它数得清天数。
            days_since = None
            if v.get("resolved_date"):
                try:
                    from datetime import date as _dt
                    y, m, dd = (int(x) for x in v["resolved_date"].split("-"))
                    today = _dt.today()
                    days_since = (today - _dt(y, m, dd)).days
                except Exception:
                    days_since = None
            if days_since is not None and days_since >= 0:
                extra += f"·说好已{days_since}天"
            out[v["kind"]].append(f"{prefix}: {v['line']} {extra}")
        else:
            out[v["kind"]].append(f"{prefix}: {v['line']}")
    return out


def render_symptom_block(rows):
    """拼进 vision/文本 prompt 的【用户自述症状(高亮)】块, 含三铁律。rows 时间正序 [(msg, created_at)]。"""
    c = extract_user_symptoms(rows)
    if not any(c.values()):
        return ""
    parts = ["【用户自述症状(高亮·必须逐条对照)】"]
    if c["complaint"]:
        parts.append("■ 历史主诉症状(本次辨证必须回应/对照, 即使照片看不出来也要提, 可写'照片未见明显异常, 但结合主诉仍建议...'):")
        parts.extend(c["complaint"])
    if c["resolved"]:
        parts.append("■ 用户后来说过【已好】的症状(要记住这是历史症状, 本次提示可能复发/注意观察/调护防复; "
                     "【已好·巩固N次】=该症状说好之后又反复确认N次已好。N 越大、隔的日子越久, "
                     "下次开方就该把它的巩固食材逐步撤掉——巩固到位的旧症状不必再长期加食材, 这是小麦的长期记忆, 要数得清):")
        parts.extend(c["resolved"])
    if c["fake"]:
        parts.append("■ 用户明确否认/打错字的症状(假症状, 本次必须绕过, 不得当作真实症状分析, 可末尾附注'已确认非真实症状'):")
        parts.extend(c["fake"])
    return "\n".join(parts)