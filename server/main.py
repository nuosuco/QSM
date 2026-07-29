"""
SOM 松麦 - 后端服务入口
小麦SOM = Qwen3.5 2B + RAG知识库
"""
import json
import os
import sys
import sqlite3
import time as time_module
from pathlib import Path
from datetime import datetime, timezone, timedelta

# 确保服务脚本可从任意目录启动
_server_dir = Path(__file__).resolve().parent
if str(_server_dir) not in sys.path:
    sys.path.insert(0, str(_server_dir))
_parent = str(_server_dir.parent)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from services.api_auth import APIAuthMiddleware
from pydantic import BaseModel
from typing import Optional, List

# 加载配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

app = FastAPI(
    title="SOM 松麦 API",
    description="小麦SOM - 中医辨证 + 有机食品推荐",
    version="1.1.1"
)

# CORS - 允许网页版、小程序调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 鉴权 + 限流（som.skill 开放平台）
app.add_middleware(APIAuthMiddleware)

# ========== 数据模型（所有模型集中定义，避免引用顺序问题） ==========

class ChatRequest(BaseModel):
    """对话请求 - 小麦SOM问诊"""
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    """对话响应"""
    reply: str
    tizhi: Optional[str] = None
    zhengxing: Optional[str] = None
    recommendations: List[dict] = []
    products: List[dict] = []
    session_id: str
    provider: Optional[str] = None
    model: Optional[str] = None

class CheckinRequest(BaseModel):
    """签到请求"""
    user_id: str

class CheckinResponse(BaseModel):
    """签到响应"""
    success: bool
    points: int = 0
    total_points: int = 0
    message: str = ""

class ClearHistoryRequest(BaseModel):
    user_id: str

class SearchAddRequest(BaseModel):
    user_id: str
    keyword: str
    platform: str = "taobao"

class FavoriteAddRequest(BaseModel):
    user_id: str
    item_id: str
    title: str = ""
    price: str = ""
    image: str = ""
    url: str = ""
    platform: str = ""
    shop_name: str = ""

class FavoriteRemoveRequest(BaseModel):
    user_id: str
    item_id: str

class FeedbackRequest(BaseModel):
    """用户反馈请求"""
    user_id: str
    content: str
    feedback_type: str = "suggestion"
    contact: str = ""
    page_url: str = ""
    user_agent: str = ""

# ===== 用户系统 / 体质评测 模型 =====

class UserRegisterRequest(BaseModel):
    """匿名用户注册/识别"""
    user_id: str

class UserLoginRequest(BaseModel):
    """手机号登录（带匿名ID合并）"""
    phone: str
    anonymous_user_id: Optional[str] = None

class SendCodeRequest(BaseModel):
    """发送验证码（短信/邮箱）"""
    target: str  # 手机号或邮箱
    channel: str = "sms"  # sms | email
    country_code: str = "+86"  # 国家码，默认中国

class VerifyCodeLoginRequest(BaseModel):
    """验证码登录"""
    target: str  # 手机号或邮箱
    code: str
    channel: str = "sms"  # sms | email
    country_code: str = "+86"
    anonymous_user_id: Optional[str] = None

class WechatLoginRequest(BaseModel):
    """微信小程序登录"""
    code: str  # wx.login() 返回的 code
    anonymous_user_id: Optional[str] = None

class BindPhoneRequest(BaseModel):
    """微信用户绑定手机号"""
    user_id: str
    phone: str
    code: str  # 短信验证码
    country_code: str = "+86"

class UserProfileUpdateRequest(BaseModel):
    user_id: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None

class TizhiSaveRequest(BaseModel):
    """保存体质评测记录"""
    user_id: str
    tizhi: str
    zhengxing: Optional[str] = None
    symptoms: Optional[str] = None
    advice: Optional[str] = None
    source: str = "chat"

class TokenVerifyRequest(BaseModel):
    token: str

# ========== 静态文件托管（网页版前端） ==========

WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.isdir(WEB_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(WEB_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(WEB_DIR, "js")), name="js")
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

    @app.get("/")
    async def serve_web():
        from fastapi.responses import FileResponse
        return FileResponse(os.path.join(WEB_DIR, "index.html"))

# ========== 数据库初始化 ==========

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
USER_DB_PATH = os.path.join(DATA_DIR, 'user_data.db')

def init_user_db():
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkin_records (
            user_id TEXT PRIMARY KEY,
            last_date TEXT,
            total_points INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            session_id TEXT,
            user_message TEXT,
            assistant_reply TEXT,
            tizhi TEXT,
            zhengxing TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            keyword TEXT NOT NULL,
            platform TEXT DEFAULT 'taobao',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            title TEXT,
            price TEXT,
            image TEXT,
            url TEXT,
            platform TEXT,
            shop_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, item_id)
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_user ON search_history(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fav_user ON product_favorites(user_id)')

    conn.commit()
    conn.close()

init_user_db()

def get_user_db():
    conn = sqlite3.connect(USER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_beijing_now():
    utc_now = datetime.now(timezone.utc)
    beijing_tz = timezone(timedelta(hours=8))
    return utc_now.astimezone(beijing_tz)

# ========== API 路由 ==========

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "SOM松麦后端", "version": "1.1.1"}

# ========== 小麦SOM 对话接口 ==========

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    from services.chat_engine import chat_with_llm

    # 加载当前会话的历史对话（传给LLM，让小麦记住上下文）
    history = []
    if request.session_id:
        try:
            conn = get_user_db()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT user_message, assistant_reply FROM chat_history WHERE session_id = ? ORDER BY created_at DESC LIMIT 10',
                (request.session_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            for row in reversed(rows):  # 时间正序
                history.append({"role": "user", "content": row["user_message"]})
                history.append({"role": "assistant", "content": row["assistant_reply"]})
        except Exception as e:
            print(f"加载会话历史失败: {e}")

    result = chat_with_llm(request.message, history=history, user_id=request.user_id)

    products = result.get("products", [])

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
        session_id=request.session_id or "default",
        provider=result.get("provider"),
        model=result.get("model")
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

# ========== 淘口令接口 ==========

@app.get("/api/products/tpwd")
async def create_tpwd(url: str, text: str = ""):
    from services.shop import ShopService
    shop = ShopService()
    result = shop.create_tpwd(url, text)
    return result

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

# ========== LLM 状态监控 ==========

@app.get("/api/llm/status")
async def llm_status():
    """LLM 服务商状态（不暴露密钥）"""
    from services import llm_router
    return llm_router.get_status()

# ========== 图片辨证接口（看舌苔） ==========

class VisionChatRequest(BaseModel):
    """图片辨证请求"""
    message: str = "请观察这张舌头照片，从中医角度分析舌色、舌苔、舌形，给出体质倾向和食养建议。"
    image_url: str
    user_id: Optional[str] = None

@app.post("/api/chat/vision")
async def chat_vision(request: VisionChatRequest):
    """图片理解辨证（看舌苔、看食材等）"""
    from services import llm_router, rag

    system_prompt = """你是小麦SOM，一位经验丰富的中医养生顾问，擅长舌诊。
请观察用户发来的图片，从以下角度分析：
1. 舌色（淡红/淡白/红/紫暗）
2. 舌苔（薄白/白腻/黄腻/少苔）
3. 舌形（胖大/瘦薄/齿痕/裂纹）
4. 综合判断可能的体质倾向
5. 给出2-3条食养建议（用药食同源食材）

注意：
- 用通俗易懂的语言，不堆砌术语
- 结尾必须加：以上为养生文化参考，不构成医疗诊断，身体不适请及时就医
- 如果图片不是舌头或看不清，礼貌说明并建议重新拍摄"""

    # RAG 上下文（基于用户消息）
    context = rag.build_context(request.message, max_chars=1500)
    if context:
        system_prompt += f"\n\n【参考知识】\n{context}"

    result = llm_router.vision(
        request.message,
        request.image_url,
        system_prompt=system_prompt,
        temperature=0.5,
    )

    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error", "图片分析失败"),
            "reply": "抱歉，我暂时无法分析这张图片。请确保图片清晰、光线充足，或者直接用文字描述你的身体状况，我一样可以帮你分析。"
        }

    # 保存对话记录
    try:
        conn = get_user_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (user_id, session_id, user_message, assistant_reply, tizhi, zhengxing)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            request.user_id or 'anonymous',
            request.session_id or 'vision',
            f'[图片辨证] {request.message[:200]}',
            result["content"][:2000],
            '', '',
        ))
        conn.commit()
        conn.close()
    except Exception:
        pass

    return {
        "success": True,
        "reply": result["content"],
        "provider": result.get("provider"),
        "model": result.get("model"),
    }

# ========== som.skill API 管理 ==========

@app.get("/api/skill/status")
async def skill_status():
    """som.skill 开放平台状态"""
    from services.api_auth import get_auth_status
    return get_auth_status()

@app.post("/api/skill/register-key")
async def skill_register_key(name: str = Query(...), rate_limit: int = Query(60)):
    """注册新的 API Key（内部调用）"""
    from services.api_auth import register_api_key
    key = register_api_key(name, rate_limit)
    return {"success": True, "api_key": key, "name": name, "rate_limit": rate_limit}

@app.post("/api/skill/revoke-key")
async def skill_revoke_key(api_key: str = Query(...)):
    """撤销 API Key（内部调用）"""
    from services.api_auth import revoke_api_key
    success = revoke_api_key(api_key)
    return {"success": success}

# ========== 节气养生 API ==========

@app.get("/api/jieqi/current")
async def jieqi_current():
    """获取当前节气养生建议"""
    from services.jieqi import get_jieqi_advice
    return get_jieqi_advice()

@app.get("/api/jieqi/all")
async def jieqi_all():
    """获取全部二十四节气列表"""
    from services.jieqi import get_all_jieqi
    return {"jieqi_list": get_all_jieqi()}

# ========== 护眼训练 API ==========

@app.get("/api/eye-exercise")
async def eye_exercise():
    """护眼训练方案"""
    return {
        "exercises": [
            {
                "name": "远近交替",
                "duration": "3分钟",
                "steps": "看远处5秒→看近处5秒，交替进行",
                "benefit": "锻炼睫状肌，缓解视疲劳"
            },
            {
                "name": "眼球转动",
                "duration": "2分钟",
                "steps": "上下左右各转5圈，顺时针逆时针各5圈",
                "benefit": "促进眼部血液循环"
            },
            {
                "name": "热敷双眼",
                "duration": "5分钟",
                "steps": "搓热双手掌心，轻敷双眼，重复3次",
                "benefit": "缓解干涩，放松眼肌"
            },
            {
                "name": "20-20-20法则",
                "duration": "随时",
                "steps": "每用眼20分钟，看20英尺（6米）外，持续20秒",
                "benefit": "国际公认的护眼法则"
            }
        ],
        "foods": ["枸杞", "菊花", "决明子", "桑葚", "蓝莓", "胡萝卜"],
        "tea": "枸杞菊花茶、决明子茶",
        "tips": "中医认为肝开窍于目，养眼先养肝。少熬夜，多食绿色蔬菜。"
    }

# ========== 用户系统 API ==========

@app.post("/api/user/register")
async def user_register(request: UserRegisterRequest):
    """匿名用户注册/识别（不用登录即可用）"""
    from services.user_system import get_or_create_anonymous
    user = get_or_create_anonymous(request.user_id)
    return {"success": True, "user": user}

@app.get("/api/user/profile")
async def user_profile(user_id: str):
    """获取用户信息"""
    from services.user_system import get_user, get_latest_tizhi
    user = get_user(user_id)
    if not user:
        return {"success": False, "error": "user not found"}
    user["latest_tizhi"] = get_latest_tizhi(user_id)
    return {"success": True, "user": user}

@app.post("/api/user/login")
async def user_login(request: UserLoginRequest):
    """手机号登录，合并匿名数据"""
    from services.user_system import login_by_phone
    if not request.phone or len(request.phone) < 6:
        raise HTTPException(status_code=400, detail="手机号格式不正确")
    result = login_by_phone(request.phone, anonymous_user_id=request.anonymous_user_id)
    return {"success": True, **result}

@app.post("/api/user/token/verify")
async def user_token_verify(request: TokenVerifyRequest):
    """校验登录 token"""
    from services.user_system import verify_token, get_user
    user_id = verify_token(request.token)
    if not user_id:
        return {"success": False, "valid": False}
    return {"success": True, "valid": True, "user": get_user(user_id)}

@app.post("/api/user/profile/update")
async def user_profile_update(request: UserProfileUpdateRequest):
    """更新昵称/头像"""
    from services.user_system import update_profile
    user = update_profile(request.user_id, nickname=request.nickname, avatar=request.avatar)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return {"success": True, "user": user}

# ========== 统一认证 API（全球手机号 + 邮箱 + 微信） ==========

@app.get("/api/auth/status")
async def auth_status():
    """查询各登录方式的配置状态"""
    from services import auth_service
    return auth_service.get_auth_status()

@app.post("/api/auth/send-code")
async def auth_send_code(request: SendCodeRequest):
    """发送验证码（短信或邮箱）"""
    from services import auth_service
    target = (request.target or "").strip()
    if not target:
        raise HTTPException(status_code=400, detail="请输入手机号或邮箱")

    if request.channel == "email":
        # 简单邮箱格式校验
        if "@" not in target or "." not in target.split("@")[-1]:
            raise HTTPException(status_code=400, detail="邮箱格式不正确")
        return auth_service.send_email_code(target)
    else:
        # 手机号：简单长度校验
        digits = target.replace("+", "").replace("-", "").replace(" ", "")
        if len(digits) < 6 or len(digits) > 15:
            raise HTTPException(status_code=400, detail="手机号格式不正确")
        return auth_service.send_sms_code(target, request.country_code)

@app.post("/api/auth/login")
async def auth_login(request: VerifyCodeLoginRequest):
    """验证码登录（手机号/邮箱统一）"""
    from services import auth_service
    target = (request.target or "").strip()

    # 手机号统一为 E.164
    if request.channel == "sms":
        target = auth_service.normalize_phone(target, request.country_code)

    # 校验验证码
    check = auth_service.verify_code(target, request.code)
    if not check.get("success"):
        return {"success": False, "error": check.get("error", "验证码错误")}

    # 登录/注册
    result = auth_service.login_or_register(
        target, request.channel, anonymous_user_id=request.anonymous_user_id
    )
    return {"success": True, **result}

@app.post("/api/auth/wechat-login")
async def auth_wechat_login(request: WechatLoginRequest):
    """微信小程序登录"""
    from services import auth_service
    return auth_service.wechat_login(request.code, anonymous_user_id=request.anonymous_user_id)

@app.post("/api/auth/bind-phone")
async def auth_bind_phone(request: BindPhoneRequest):
    """微信用户绑定手机号（需短信验证码）"""
    from services import auth_service
    e164 = auth_service.normalize_phone(request.phone, request.country_code)
    check = auth_service.verify_code(e164, request.code)
    if not check.get("success"):
        return {"success": False, "error": check.get("error", "验证码错误")}
    return auth_service.bind_phone_to_wechat(request.user_id, e164)

# ========== 体质评测 API ==========

@app.post("/api/tizhi/save")
async def tizhi_save(request: TizhiSaveRequest):
    """保存一条体质评测记录"""
    from services.user_system import add_tizhi_record
    record = add_tizhi_record(
        request.user_id, request.tizhi, zhengxing=request.zhengxing,
        symptoms=request.symptoms, advice=request.advice, source=request.source,
    )
    return {"success": True, "record": record}

@app.get("/api/tizhi/records")
async def tizhi_records(user_id: str, limit: int = 50):
    """体质评测历史"""
    from services.user_system import get_tizhi_records
    return {"success": True, "records": get_tizhi_records(user_id, limit=limit)}

@app.get("/api/tizhi/latest")
async def tizhi_latest(user_id: str):
    """最新一次体质结果"""
    from services.user_system import get_latest_tizhi
    return {"success": True, "record": get_latest_tizhi(user_id)}

# ========== 启动 ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=CONFIG["server"]["host"],
        port=CONFIG["server"]["port"],
        reload=CONFIG["server"]["debug"]
    )