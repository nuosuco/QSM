        def search_ingredient(ing: str) -> list:
            """搜索单个食材，不限页数，搜够不同品牌2款就停"""
            result = []
            local_titles = set()
            local_brands = set()
            page_num = 1
            while len(result) < 2:
                try:
                    sub_items = _shop._search_taobao(f"{ing} 有机", page_num, 2, "")
                except Exception:
                    sub_items = []
                if not sub_items:
                    page_num += 1
                    if page_num > 5:
                        break
                    continue
                for item in sub_items:
                    title = item.get('title', '')
                    brand = item.get('shop_name', '') or ''
                    # 只保留标题里有"有机"的商品
                        continue
                    if title and title not in local_titles and not _shop._is_excluded(item):
                        if ing.lower() in title.lower():
                            local_titles.add(title)
                            if brand not in local_brands:
                                local_brands.add(brand)
                                result.append(item)
                            elif len(result) < 2:
                                result.append(item)
                page_num += 1
            return result
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_map = {
                executor.submit(search_ingredient, ing): ing
                for ing in ingredient_names
            }
            # 不用超时机制，全部等所有结果回来
            concurrent.futures.wait(future_map, timeout=None)
            print(f"[小麦助手] 搜索完成，products: {len(products)}个")
            for future in future_map:
                try:
                    items = future.result()
                    for item in items:
                        title = item.get('title', '')
                        if title and title not in seen_titles:
                            seen_titles.add(title)
                            products.append(item)
                except Exception:
                    pass

    try:
        conn = get_user_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (user_id, session_id, user_message, assistant_reply, tizhi, zhengxing)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            request.user_id or 'anonymous',
            request.session_id or 'default',
            request.message[:500],
            result["reply"][:2000],
            result.get('tizhi', ''),
            result.get('zhengxing', ''),
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"保存对话历史失败: {e}")

    return ChatResponse(
        reply=result["reply"],
        tizhi=result.get("tizhi"),
        zhengxing=result.get("zhengxing"),
        recommendations=result.get("recommendations", []),
        products=products,
        session_id=request.session_id or "default"
    )

# ========== 商品搜索接口 ==========

@app.get("/api/products/categories")
async def get_product_categories():
    from services.shop import ShopService
    shop = ShopService()
    categories = shop.get_categories()
    return {"categories": categories}

@app.get("/api/products/search")
async def search_products(
    keyword: str,
    platform: str = "taobao",
    page: int = 1,
    page_size: int = 10,
    sort: str = ""
):
    from services.shop import ShopService
    shop = ShopService()

    search_kw = shop.get_category_keyword(keyword) if keyword else ''
    if not search_kw and keyword:
        search_kw = keyword

    items = shop.search(search_kw, platform=platform, page=page, page_size=page_size, sort=sort)

    return {
        "keyword": keyword,
        "search_keyword": search_kw,
        "platform": platform,
        "total": len(items),
        "from_cache": 0,
        "items": items
    }

# ========== 知识库接口 ==========

@app.get("/api/knowledge/yaoshi")
async def get_yaoshi_tongyuan():
    from services.knowledge import KnowledgeService
    ks = KnowledgeService()
    return ks.get_yaoshi_list()

@app.get("/api/knowledge/tizhi")
async def get_tizhi_list():
    from services.knowledge import KnowledgeService
    ks = KnowledgeService()
    return ks.get_tizhi_list()

@app.get("/api/knowledge/shiliao")
async def get_shiliao(zhengxing: Optional[str] = None):
    from services.knowledge import KnowledgeService
    ks = KnowledgeService()
    return ks.get_shiliao(zhengxing)

# ========== 签到接口 ==========

@app.get("/api/checkin/status")
async def checkin_status(user_id: str):
    now = get_beijing_now()
    today = now.strftime('%Y-%m-%d')

    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM checkin_records WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "checked_in_today": row['last_date'] == today,
            "total_points": row['total_points'],
            "streak": row['streak'],
            "today": today
        }

    return {
        "checked_in_today": False,
        "total_points": 0,
        "streak": 0,
        "today": today
    }

@app.post("/api/checkin/do")
async def do_checkin(request: CheckinRequest):
    now = get_beijing_now()
    today = now.strftime('%Y-%m-%d')
    yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')

    conn = get_user_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM checkin_records WHERE user_id = ?', (request.user_id,))
    row = cursor.fetchone()

    if row and row['last_date'] == today:
        conn.close()
        return CheckinResponse(success=False, message="今天已经签到过了")

    if row:
        last_date = row['last_date']
        total_points = row['total_points']
        streak = row['streak']
        streak = streak + 1 if last_date == yesterday else 1
        total_points += 10
        cursor.execute('UPDATE checkin_records SET last_date = ?, total_points = ?, streak = ? WHERE user_id = ?',
                       (today, total_points, streak, request.user_id))
    else:
        total_points = 10
        streak = 1
        cursor.execute('INSERT INTO checkin_records (user_id, last_date, total_points, streak) VALUES (?, ?, ?, ?)',
                       (request.user_id, today, total_points, streak))

    conn.commit()
    conn.close()

    return CheckinResponse(success=True, points=10, total_points=total_points,
                           message=f"签到成功！连续签到{streak}天，获得10积分")

# ========== 对话历史接口 ==========

@app.get("/api/chat/history")
async def get_chat_history(user_id: str, limit: int = 20):
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
                   (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return {"total": len(rows), "history": [dict(r) for r in rows]}

@app.get("/api/chat/history/session")
async def get_session_history(session_id: str):
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_history WHERE session_id = ? ORDER BY created_at ASC',
                   (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return {"total": len(rows), "history": [dict(r) for r in rows]}

@app.post("/api/chat/history/clear")
async def clear_chat_history(request: ClearHistoryRequest):
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (request.user_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return {"success": True, "deleted": affected}

# ========== 搜索历史接口 ==========

@app.get("/api/search/history")
async def get_search_history(user_id: str, limit: int = 20):
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT keyword, platform, MAX(created_at) as last_searched
        FROM search_history WHERE user_id = ?
        GROUP BY keyword ORDER BY last_searched DESC LIMIT ?
    ''', (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return {"total": len(rows), "history": [dict(r) for r in rows]}

@app.post("/api/search/history/add")
async def add_search_history(request: SearchAddRequest):
    conn = get_user_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO search_history (user_id, keyword, platform) VALUES (?, ?, ?)',
                       (request.user_id, request.keyword, request.platform))
        conn.commit()
    finally:
        conn.close()
    return {"success": True}

@app.post("/api/search/history/clear")
async def clear_search_history(request: ClearHistoryRequest):
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM search_history WHERE user_id = ?', (request.user_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return {"success": True, "deleted": affected}

# ========== 商品收藏接口 ==========

@app.get("/api/favorites")
async def get_favorites(user_id: str, limit: int = 50):
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM product_favorites WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
                   (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return {"total": len(rows), "favorites": [dict(r) for r in rows]}

@app.post("/api/favorites/add")
async def add_favorite(request: FavoriteAddRequest):
    conn = get_user_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO product_favorites
            (user_id, item_id, title, price, image, url, platform, shop_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (request.user_id, request.item_id, request.title, request.price,
              request.image, request.url, request.platform, request.shop_name))
        conn.commit()
        added = cursor.rowcount > 0
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}
    conn.close()
    return {"success": True, "added": added}

@app.post("/api/favorites/remove")
async def remove_favorite(request: FavoriteRemoveRequest):
    """移除收藏商品（使用POST body）"""
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM product_favorites WHERE user_id = ? AND item_id = ?',
                   (request.user_id, request.item_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return {"success": True, "deleted": affected}

@app.post("/api/favorites/batch-check")
async def batch_check_favorites(user_ids: dict = None):
    """批量检查商品是否已收藏（POST请求）"""
    # 支持 query 参数格式: ?user_id=xxx&item_ids=id1,id2,id3
    pass

@app.get("/api/favorites/batch-check")
async def batch_check_favorites_get(user_id: str, item_ids: str = ""):
    """批量检查商品是否已收藏"""
    if not item_ids:
        return {"favorites": {}}
    ids_list = [x.strip() for x in item_ids.split(",") if x.strip()]
    conn = get_user_db()
    cursor = conn.cursor()
    favorites = {}
    for item_id in ids_list:
        cursor.execute('SELECT 1 FROM product_favorites WHERE user_id = ? AND item_id = ?',
                       (user_id, item_id))
        favorites[item_id] = cursor.fetchone() is not None
    conn.close()
    return {"favorites": favorites}

@app.get("/api/favorites/check")
async def check_favorite(user_id: str, item_id: str):
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM product_favorites WHERE user_id = ? AND item_id = ?',
                   (user_id, item_id))
    exists = cursor.fetchone() is not None
    conn.close()
    return {"favorited": exists}

# ========== 缓存统计接口 ==========

@app.get("/api/cache/stats")
async def cache_stats():
    from services.shop import ShopService
    shop = ShopService()
    return shop.get_cache_stats()

# ========== 每日养生建议接口 ==========

@app.get("/api/daily-tip")
async def daily_tip():
    import random
    beijing_tz = timezone(timedelta(hours=8))
    today = datetime.now(beijing_tz).strftime('%Y-%m-%d')

    tips = [
        {"title": "今日养生：早睡早起", "content": "子时（23:00-1:00）是胆经当令，最好提前入睡。睡前可用温水泡脚15分钟，助眠安神。", "tip_type": "作息", "emoji": "🌙"},
        {"title": "今日养生：喝杯枸杞红枣茶", "content": "枸杞滋补肝肾，红枣补中益气。取枸杞10g、红枣3枚，沸水冲泡，代茶饮。", "tip_type": "食疗", "emoji": "🍵"},
        {"title": "今日养生：健脾祛湿", "content": "湿气重的人适合喝薏米赤小豆汤。薏米50g、赤小豆50g，提前浸泡4小时后煮粥。", "tip_type": "食疗", "emoji": "🥣"},
        {"title": "今日养生：穴位按摩", "content": "按揉足三里穴（膝盖外膝眼下四横指），每次3-5分钟，可健脾和胃、补中益气。", "tip_type": "穴位", "emoji": "💆"},
        {"title": "今日养生：情绪调节", "content": "肝郁则百病生。建议做深呼吸练习：吸气4秒、屏息4秒、呼气6秒，重复10次。", "tip_type": "情志", "emoji": "🧘"},
        {"title": "今日养生：适量运动", "content": "春捂秋冻，适度运动最养人。推荐八段锦或太极，晨起练习30分钟，气血通畅。", "tip_type": "运动", "emoji": "🏃"},
        {"title": "今日养生：滋阴润燥", "content": "常感口干咽燥？试试百合银耳羹：百合20g、银耳15g，炖煮至粘稠，加冰糖调味。", "tip_type": "食疗", "emoji": "🍯"},
        {"title": "今日养生：补肾固精", "content": "黑芝麻核桃糊：黑芝麻30g、核桃仁20g、黑米30g，炒香磨碎冲糊食用，补肾乌发。", "tip_type": "食疗", "emoji": "🫘"},
        {"title": "今日养生：疏肝解郁", "content": "玫瑰花5朵、合欢花5g，沸水冲泡代茶饮。适合心情烦躁、压力大时饮用，疏肝解郁安神。", "tip_type": "食疗", "emoji": "🌹"},
        {"title": "今日养生：健脑益智", "content": "核桃仁30g、黑芝麻20g、桂圆肉15g，同煮20分钟食用。补脑益智，适合用脑过度者。", "tip_type": "食疗", "emoji": "🧠"},
        {"title": "今日养生：温经散寒", "content": "生姜5片、红枣6枚、红糖20g，加水煮15分钟趁热饮用。适合手脚冰凉、怕冷体质。", "tip_type": "食疗", "emoji": "🔥"},
        {"title": "今日养生：清肝明目", "content": "枸杞15g、菊花10g、决明子10g，沸水冲泡焖10分钟。适合长时间看手机电脑、眼睛干涩者。", "tip_type": "食疗", "emoji": "👁️"},
        {"title": "今日养生：健脾开胃", "content": "山楂10g、陈皮6g、麦芽10g，加水煮15分钟代茶饮。适合食欲不振、饭后腹胀者。", "tip_type": "食疗", "emoji": "🍊"},
        {"title": "今日养生：润肺止咳", "content": "雪梨1个去核，纳入川贝粉3g、冰糖适量，隔水蒸1小时。适合干咳少痰、咽干者。", "tip_type": "食疗", "emoji": "🍐"},
        {"title": "今日养生：安神助眠", "content": "酸枣仁15g、百合10g、莲子15g，加水煎煮30分钟，睡前1小时饮用。适合失眠多梦者。", "tip_type": "食疗", "emoji": "😴"},
        {"title": "今日养生：补气养血", "content": "黄芪15g、当归5g、红枣5枚、乌鸡半只，慢炖2小时。适合面色苍白、容易疲劳者。", "tip_type": "食疗", "emoji": "💪"},
        {"title": "今日养生：祛湿减肥", "content": "荷叶10g、山楂15g、陈皮6g，沸水冲泡焖15分钟。适合体胖困重、血脂偏高者。", "tip_type": "食疗", "emoji": "🏋️"},
        {"title": "今日养生：护发养颜", "content": "桑葚15g、黑芝麻20g、枸杞10g，磨粉冲糊食用。适合脱发白发、皮肤干燥者。", "tip_type": "食疗", "emoji": "💇"},
        {"title": "今日养生：艾灸保健", "content": "艾灸足三里、关元穴各10分钟，每周3次。可提升免疫力、健脾和胃、补中益气。", "tip_type": "穴位", "emoji": "🔥"},
        {"title": "今日养生：摩腹养胃", "content": "晨起空腹，顺时针摩腹100次，再逆时针100次。可促进肠道蠕动、改善消化功能。", "tip_type": "穴位", "emoji": "🤲"},
        {"title": "今日养生：叩齿固齿", "content": "晨起叩齿36次，舌抵上腭，津液咽下。可固齿健肾、生津养胃。", "tip_type": "作息", "emoji": "🦷"},
        {"title": "今日养生：提肛养肾", "content": "每天做提肛运动100次，吸气时收紧肛门，呼气时放松。可固肾益气、改善痔疮。", "tip_type": "运动", "emoji": "💪"},
        {"title": "今日养生：鸣天鼓", "content": "双手掌心紧按耳朵，手指放在后脑，食指弹中指上，耳中闻咚咚声。做36次，可健脑益智。", "tip_type": "穴位", "emoji": "👂"},
    ]

    seed = sum(ord(c) for c in today)
    random.seed(seed)
    tip = random.choice(tips)
    return {"date": today, **tip}

# ========== 用户反馈接口 ==========

@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    """提交用户反馈"""
    from services.feedback import FeedbackService
    fs = FeedbackService()
    return fs.submit(
        user_id=request.user_id,
        content=request.content,
        feedback_type=request.feedback_type,
        contact=request.contact,
        page_url=request.page_url,
        user_agent=request.user_agent,
    )

@app.get("/api/feedback/list")
async def get_feedback_list(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """获取反馈列表"""
    from services.feedback import FeedbackService
    fs = FeedbackService()
    return fs.get_list(user_id=user_id, status=status, limit=limit, offset=offset)

@app.get("/api/feedback/stats")
async def get_feedback_stats():
    """反馈统计"""
    from services.feedback import FeedbackService
    fs = FeedbackService()
    return fs.get_stats()

# ========== 数据统计面板接口 ==========

@app.get("/api/stats/dashboard")
async def get_dashboard():
    """获取综合数据面板"""
    from services.stats import StatsService
    ss = StatsService()
    return ss.get_dashboard()

# ========== 缓存预热管理接口 ==========

@app.get("/api/cache/warmup/status")
async def get_warmup_status():
    """获取缓存预热状态"""
    import sqlite3
    db_path = os.path.join(DATA_DIR, 'product_cache.db')
    if not os.path.exists(db_path):
        return {"status": "no_cache", "total": 0, "keywords": []}
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM product_cache')
        total = cursor.fetchone()[0]
        cursor.execute('SELECT * FROM crawl_status ORDER BY last_crawled DESC')
        rows = cursor.fetchall()
        conn.close()
        keywords = []
        for row in rows:
            keywords.append({
                "keyword": row[0],
                "platform": row[1],
                "page_crawled": row[2],
                "items_found": row[3],
                "last_crawled": row[4],
                "status": row[5],
            })
        return {"status": "ok", "total": total, "keywords": keywords}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/cache/warmup/trigger")
async def trigger_warmup():
    """触发缓存预热（异步）"""
    import subprocess
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'cache_warmup.py')
    try:
        subprocess.Popen(
            ['python3.11', script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return {"success": True, "message": "缓存预热已触发"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/stats/users")
async def get_user_stats():
    """用户统计"""
    from services.stats import StatsService
    ss = StatsService()
    return ss.get_user_stats()

@app.get("/api/stats/products")
async def get_product_stats():
    """商品缓存统计"""
    from services.stats import StatsService
    ss = StatsService()
    return ss.get_product_stats()

@app.get("/api/stats/chat")
async def get_chat_stats():
    """对话统计"""
    from services.stats import StatsService
    ss = StatsService()
    return ss.get_chat_stats()

@app.get("/api/stats/checkin")
async def get_checkin_stats():
    """签到统计"""
    from services.stats import StatsService
    ss = StatsService()
    return ss.get_checkin_stats()

# ========== 启动 ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=CONFIG["server"]["host"],
        port=CONFIG["server"]["port"],
        reload=CONFIG["server"]["debug"]
    )