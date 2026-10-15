"""
SOM 松麦 - 后端服务入口
小麦SOM = Qwen3.5 2B + RAG知识库
"""
import json
import os
import sys
import sqlite3
import time as time_module
import base64
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta

# 确保服务脚本可从任意目录启动
_server_dir = Path(__file__).resolve().parent
if str(_server_dir) not in sys.path:
    sys.path.insert(0, str(_server_dir))
_parent = str(_server_dir.parent)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from fastapi import FastAPI, HTTPException, Query, Response
from starlette.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from api_qnt import router as qnt_router
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

class FavRemoveContentRequest(BaseModel):
    user_id: str
    id: int

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

class RegisterRequest(BaseModel):
    """账号密码注册"""
    account: str
    password: str
    nickname: Optional[str] = None
    anonymous_user_id: Optional[str] = None  # 2026-10-12 中华: 注册时也把匿名数据并进来

class PasswordLoginRequest(BaseModel):
    """账号密码登录"""
    account: str
    password: str
    anonymous_user_id: Optional[str] = None  # 2026-10-12 中华: 四种登录统一, 匿名数据归并

class ForgotPasswordRequest(BaseModel):
    """忘记密码"""
    account: str

class ResetPasswordRequest(BaseModel):
    """重置密码"""
    token: str
    new_password: str

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
    session_id: Optional[str] = None  # 2026-10-13 小蕊加: 同 session 只存一条, 保证一次对话=一条记录

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

    # 2026-10-15 中华要求: 收藏卡片混排(商品+小麦辨证内容), 内容收藏云端统一保存
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fav_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT,
            content TEXT,
            user_message TEXT,
            products TEXT,
            source TEXT DEFAULT 'chat',
            content_fp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_favc_user ON fav_content(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_favc_fp ON fav_content(user_id, content_fp)')

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

    # 2026-10-13 中华要求: 文字辨证也要自动存进健康数据(tizhi_records), 和拍照辨证/体质评测一个待遇
    # 仅存"判出了体质"的轮次(规则引擎 BianzhengEngine 判定), 同 session 覆盖旧记录(与拍照同一语义)
    if result.get('tizhi'):
        try:
            from services.user_system import add_tizhi_record
            add_tizhi_record(
                request.user_id or 'anonymous', result.get('tizhi', ''),
                zhengxing=result.get('zhengxing'),
                symptoms=(request.message or '')[:80],
                advice=result["reply"][:2000],
                source='text_chat',
                session_id=request.session_id or 'default',
            )
        except Exception as e:
            print(f"文字辨证体质存档失败: {e}")

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

# ========== 服务端渲染分享图(2026-10-16 中华要求: 微信内分享图可用, 绕开 canvas 跨域) ==========

class ShareContentRequest(BaseModel):
    text: str = ""
    site_url: str = "https://som.top/"


class ShareProductRequest(BaseModel):
    title: str = ""
    price: str = ""
    shop: str = ""
    image: str = ""      # 主图 URL(兼容旧调用)
    images: list = []    # 2026-10-16 中华要求: 全部商品图(最多4张进分享卡)
    buy_url: str = ""     # 淘宝购买链接(无则用站点码)
    site_url: str = "https://som.top/"


@app.post("/api/share/content-image")
async def share_content_image(request: ShareContentRequest):
    """辨证内容分享图: 前端把回复文本 POST 过来, 服务端 Pillow 渲染 PNG 回传"""
    from services.share_image import render_content_share_image
    png = render_content_share_image(request.text or "养生参考", request.site_url)
    return Response(content=png, media_type="image/png")


@app.post("/api/share/product-image")
async def share_product_image(request: ShareProductRequest):
    """商品分享图 v2: 全部商品图(最多4张) + 商品名 + 淘宝购买二维码, 头尾同辨证模板"""
    from services.share_image import render_product_share_image
    pics = list(request.images or [])
    if request.image and request.image not in pics:
        pics.insert(0, request.image)
    png = render_product_share_image(
        title=request.title, price=request.price, shop=request.shop,
        images=pics, buy_url=request.buy_url or "https://item.taobao.com/",
        site_url=request.site_url)
    return Response(content=png, media_type="image/png")


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
    # 2026-10-11 小蕊改(中华拍板:日化洗护及后面所有分类搜不出商品,根因=EXCLUDE_KEYWORDS 杀光日化/美妆词):
    # 给 search_from_cache 传类目名做 context, 日化/美妆类目不排日化词, 食品类照旧排。
    _ctx_cat = keyword.strip() if keyword and keyword.strip() in ('日化洗护', '美妆护肤', '家居日用', '医用环保') else ''

    # 2026-10-11 小蕊改（中华拍板：全部/每个分类菜单都太慢 → 缓存先秒出、实时后台悄悄刷新）：
    # 原逻辑：阻塞等淘宝实时搜（超时卡 10~30s），页面转圈。
    # 新逻辑：
    #   1) 第 1 页：立即从本地缓存 search_from_cache 秒回（加索引后 0.01s），from_cache=1
    #      后台线程悄悄跑实时淘宝搜索（限时 2s，不阻塞主响应），结果写回缓存
    #   2) 翻页(>1)：缓存优先，缓存不够也秒回，后台补刷
    #   3) 实时后台刷新有冷却(60s)，避免频繁打淘宝
    import concurrent.futures as _cf
    import time as _time
    import threading as _th
    _t0 = _time.time()
    from_cache = 0
    items = []
    if page == 1:
        # 缓存优先：毫秒级返回上一轮商品，用户秒进页面
        try:
            items = shop.search_from_cache(search_kw, page=1, page_size=page_size, category=_ctx_cat)
            if items:
                from_cache = 1
        except Exception:
            items = []
        # 后台悄悄刷新实时搜索（限时 2s，不阻塞主响应，不拖慢下次请求）
        _cool_key = f"tbrefresh_{keyword}_{platform}"
        _last = getattr(shop, '_tb_refresh_last', {})
        if _last.get(_cool_key, 0) < _time.time() - 60:
            _last[_cool_key] = _time.time()
            shop._tb_refresh_last = _last
            def _bg_refresh():
                with _cf.ThreadPoolExecutor(max_workers=1) as _ex:
                    _f = _ex.submit(shop.search, search_kw, platform, 1, page_size, sort)
                    try:
                        _f.result(timeout=2)  # 限时 2s，拿不到就放弃，不阻塞
                    except Exception:
                        pass
            _th.Thread(target=_bg_refresh, daemon=True).start()
    else:
        # 翻页：缓存优先（毫秒级），缓存不够也秒回，实时补刷放后台
        try:
            items = shop.search_from_cache(search_kw, page=page, page_size=page_size, category=_ctx_cat)
            if items:
                from_cache = 1
        except Exception:
            items = []
        _cool_key = f"tbrefresh_{keyword}_{platform}_{page}"
        _last = getattr(shop, '_tb_refresh_last', {})
        if _last.get(_cool_key, 0) < _time.time() - 60:
            _last[_cool_key] = _time.time()
            shop._tb_refresh_last = _last
            def _bg_refresh():
                with _cf.ThreadPoolExecutor(max_workers=1) as _ex:
                    _f = _ex.submit(shop.search, search_kw, platform, page, page_size, sort)
                    try:
                        _f.result(timeout=2)
                    except Exception:
                        pass
            _th.Thread(target=_bg_refresh, daemon=True).start()
    if not items and page == 1:
        # 缓存空(首次/新关键词) → 限时 1s 试一次实时, 拿不到也照样秒回(空态), 后台补刷
        with _cf.ThreadPoolExecutor(max_workers=1) as _ex:
            _f = _ex.submit(shop.search, search_kw, platform, page, page_size, sort)
            try:
                items = _f.result(timeout=1)
            except Exception:
                items = []
        from_cache = 0

    return {
        "keyword": keyword,
        "search_keyword": search_kw,
        "platform": platform,
        "total": len(items),
        "from_cache": from_cache,
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

    # 2026-10-12 小蕊加: 签到积分同步到 users.points, 让"我的数据"统一展示
    try:
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (request.user_id,))
        if cursor.fetchone():
            cursor.execute('UPDATE users SET points = ? WHERE user_id = ?', (total_points, request.user_id))
        else:
            cursor.execute('INSERT INTO users (user_id, points, is_anonymous, created_at, last_active) VALUES (?, ?, 1, ?, ?)',
                           (request.user_id, total_points, now.isoformat(), now.isoformat()))
    except sqlite3.Error:
        pass
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
    # 2026-10-13 小蕊改(中华反馈: 对话次数显示1应该是2):
    # total 改为"去重后的对话 session 数(一次对话=1)", history 仍按 limit 截断返回记录
    # 前端 loadChatStats 读 total 就是对话次数, 不用改前端
    conn2 = get_user_db()
    cur2 = conn2.cursor()
    cur2.execute(
        "SELECT COUNT(DISTINCT session_id) FROM chat_history WHERE user_id=? AND session_id IS NOT NULL AND session_id != ''",
        (user_id,)
    )
    total_sessions = cur2.fetchone()[0]
    conn2.close()
    return {"total": total_sessions, "history": [dict(r) for r in rows]}

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
async def get_favorites(user_id: str, limit: int = 50, page: int = 1, page_size: int = 10):
    conn = get_user_db()
    cursor = conn.cursor()
    # 2026-10-15 我的收藏改双分类区独立分页: 优先 page/page_size(偏移分页), 兼容旧 limit
    if page > 1 or page_size != 10:
        total = cursor.execute('SELECT COUNT(*) FROM product_favorites WHERE user_id=?', (user_id,)).fetchone()[0]
        rows = cursor.execute(
            'SELECT * FROM product_favorites WHERE user_id=? ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (user_id, page_size, (page - 1) * page_size)).fetchall()
        conn.close()
        return {"total": total, "page": page, "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
                "favorites": [dict(r) for r in rows]}
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

# ========== 2026-10-15 中华要求: 收藏卡片要同时展示【商品收藏】和【小麦辨证内容收藏】, 混排+10条翻页 ==========
# 辨证内容收藏目前只有 localStorage 存了一份, 要混排到卡片里就必须让后端也存一份,
# 否则换设备/清缓存就丢了, 和商品收藏"云端统一保存"的设计矛盾。所以新增内容收藏表 + 两个接口。

class FavContentAddRequest(BaseModel):
    user_id: str
    title: str = ""
    content: str = ""   # 小麦辨证回答全文
    user_message: str = ""
    products: list = []
    source: str = "chat"  # chat / vision_chat

@app.post("/api/favorites/content/add")
async def add_fav_content(request: FavContentAddRequest):
    conn = get_user_db()
    cursor = conn.cursor()
    # 内容收藏表: 同一用户同一段回答不重复存(按 content 前80字指纹去重)
    fp = (request.content or "")[:80]
    try:
        cursor.execute('SELECT 1 FROM fav_content WHERE user_id=? AND content_fp=? LIMIT 1',
                       (request.user_id, fp))
        dup = cursor.fetchone()
        if dup:
            conn.close()
            return {"success": True, "added": False}
    except Exception:
        # 表不存在(老库未迁移)时忽略去重, 直接插
        pass
    try:
        cursor.execute('''
            INSERT INTO fav_content (user_id, title, content, user_message, products, source, content_fp, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (request.user_id, request.title[:120], request.content, request.user_message[:300],
              json.dumps(request.products or []), request.source, fp, get_beijing_now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        added = cursor.rowcount > 0
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}
    conn.close()
    return {"success": True, "added": added}

@app.get("/api/favorites/content")
async def list_fav_content(user_id: str, page: int = 1, page_size: int = 10):
    """辨证内容收藏列表(分页), 2026-10-15 收藏卡片分类展示"""
    conn = get_user_db()
    cursor = conn.cursor()
    try:
        total = cursor.execute('SELECT COUNT(1) FROM fav_content WHERE user_id=?', (user_id,)).fetchone()[0]
        rows = cursor.execute(
            'SELECT id, title, content, user_message, products, source, created_at FROM fav_content '
            'WHERE user_id=? ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (user_id, page_size, (page - 1) * page_size)).fetchall()
    except Exception:
        total, rows = 0, []
    conn.close()
    items = [{"id": str(r["id"]), "title": r["title"] or "", "content": r["content"],
              "user_message": r["user_message"], "products": json.loads(r["products"] or "[]"),
              "source": r["source"], "created_at": r["created_at"] or ""} for r in rows]
    return {"total": total, "page": page, "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total else 1, "items": items}

@app.post("/api/favorites/content/remove")
async def remove_fav_content(request: FavRemoveContentRequest):
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM fav_content WHERE user_id=? AND id=?',
                   (request.user_id, request.id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return {"success": True, "deleted": affected}

@app.get("/api/favorites/mixed")
async def get_mixed_favorites(user_id: str, page: int = 1, page_size: int = 10):
    """混排: 商品收藏(product_favorites) + 辨证内容收藏(fav_content), 按时间倒序合并, 10条/页"""
    conn = get_user_db()
    cursor = conn.cursor()
    # 两类收藏全量拉出再在内存里合并(单用户量级很小, 无需复杂 SQL)
    p_rows = cursor.execute(
        'SELECT item_id, title, price, image, url, platform, shop_name, created_at FROM product_favorites WHERE user_id=?',
        (user_id,)).fetchall()
    c_rows = cursor.execute(
        'SELECT id, title, content, user_message, products, source, created_at FROM fav_content WHERE user_id=?',
        (user_id,)).fetchall()
    conn.close()
    items = []
    for r in p_rows:
        items.append({"type": "product", "id": r["item_id"], "title": r["title"], "price": r["price"],
                      "image": r["image"], "url": r["url"], "platform": r["platform"],
                      "shop_name": r["shop_name"], "created_at": r["created_at"] or ""})
    for r in c_rows:
        items.append({"type": "content", "id": str(r["id"]), "title": r["title"] or "", "content": r["content"],
                      "user_message": r["user_message"], "products": json.loads(r["products"] or "[]"),
                      "source": r["source"], "created_at": r["created_at"] or ""})
    items.sort(key=lambda x: x["created_at"], reverse=True)
    total = len(items)
    start = (page - 1) * page_size
    page_items = items[start:start + page_size]
    return {"total": total, "page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size,
            "items": page_items}

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

# ========== 2026-10-13 小蕊加: 商品缓存自动清理(中华要求: 保持 ~1GB) ==========
@app.post("/api/cache/gc")
async def trigger_cache_gc():
    """手动触发缓存清理(超 1.05GB 才删旧记录 + VACUUM)"""
    import threading
    from services.cache_gc import gc_product_cache
    def _run():
        r = gc_product_cache(verbose=True)
        print(f"[cache-gc] 手动触发结果: {r}")
    threading.Thread(target=_run, daemon=True).start()
    return {"status": "started", "message": "后台清理中, 日志看 [cache-gc]"}

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
    """图片辨证请求（支持多张图片）"""
    message: str = "请观察这些照片，从中医角度分析舌色、舌苔、舌形、面色、皮肤等，给出体质倾向和食养建议。"
    image_url: Optional[str] = None  # 兼容旧版单图
    images: Optional[List[str]] = None  # 新版多图
    user_id: Optional[str] = None
    session_id: Optional[str] = None

def _base64_to_url(data_uri: str) -> str:
    """将 base64 data URI 存为文件，返回可公网访问的 URL"""
    uploads_dir = os.path.join(WEB_DIR, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    # 解析 data:image/jpeg;base64,xxxxx
    header, _, b64data = data_uri.partition(",")
    ext = "jpg"
    if "png" in header:
        ext = "png"
    elif "webp" in header:
        ext = "webp"
    filename = f"{uuid.uuid4().hex[:12]}.{ext}"
    filepath = os.path.join(uploads_dir, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(b64data))
    return f"https://som.top/uploads/{filename}"


def _strip_tizhi_data_json(reply: str) -> str:
    """2026-10-14 中华反馈: 小麦辨证回复里漏出了 tizhi_data 原始 JSON 代码块。
    通道1要求 LLM 末尾输出 tizhi_data:{...} 供服务端存档, 但回复要给用户看, 不能带代码。
    把末尾的 tizhi_data JSON 行/块从回复里剥掉(保留正文)。"""
    import re
    if not reply:
        return reply
    # 1) 带前缀的固定块: tizhi_data: {...}(可能带前导空行/换行)
    reply = re.sub(r'\s*tizhi_data\s*:\s*\{\s*"tizhi"\s*:\s*"[^"]*"\s*(?:,\s*"zhengxing"\s*:\s*"[^"]*")?\s*\}\s*$', '', reply)
    # 2) 无 tizhi_data 前缀的裸 JSON 块(兼容 LLM 没写前缀)
    reply = re.sub(r'\s*\{\s*"tizhi"\s*:\s*"[^"]*"\s*(?:,\s*"zhengxing"\s*:\s*"[^"]*")?\s*\}\s*$', '', reply)
    # 3) 兜底: 任何位置残留的 tizhi_data 行(防 LLM 把它插到正文中间)
    reply = re.sub(r'[ \t]*tizhi_data\s*:\s*\{[^{}]*\}\s*', '', reply)
    # 4) 清掉尾部多余空行
    return (reply.rstrip() + '\n') if reply.strip() else reply


def _extract_tizhi_from_vision_reply(reply: str):
    """2026-10-13 小蕊: 从图片辨证回复里提取体质/证型(服务端统一做, 不依赖前端JS版本)。
    2026-10-14 双通道升级(中华要求: 辨证必须稳定进体质记录):
      通道1(优先): 解析 LLM 末尾固定 JSON 块: tizhi_data: {"tizhi":"...","zhengxing":"..."}
      通道2(兜底): 原有词表/正则匹配
    返回 (tizhi, zhengxing)。两通道都抓不到就 ('', '', 不硬塞)。"""
    import re
    if not reply:
        return '', ''
    tizhi = ''
    zhengxing = ''
    # ===== 通道1: LLM 固定 JSON 块(提示词末尾要求 tizhi_data: {...}) =====
    m = re.search(r'tizhi_data\s*:\s*\{\s*"tizhi"\s*:\s*"([^"]*)"\s*(?:,\s*"zhengxing"\s*:\s*"([^"]*)")?\s*\}', reply)
    if not m:
        # 兼容 LLM 没写 tizhi_data 前缀、直接裸 JSON 的情况
        m = re.search(r'\{\s*"tizhi"\s*:\s*"([^"]*)"\s*(?:,\s*"zhengxing"\s*:\s*"([^"]*)")?\s*\}', reply)
    if m:
        tizhi = m.group(1).strip()
        zhengxing = (m.group(2) or '').strip()
    # ===== 通道2: 词表兜底(通道1没抓到体质才跑) =====
    if not tizhi:
        tizhi_words = ['平和质', '气虚质', '阳虚质', '阴虚质', '痰湿质', '湿热质', '血瘀质', '特禀质', '过敏质',
                       '脾虚湿盛质', '脾虚质', '肝郁质', '气郁质', '血瘀体质']
        found = [t for t in tizhi_words if t in reply]
        # 去重保持顺序, 最多3个(脾虚湿盛质含气虚/痰湿语义, 与单项去重)
        seen, uniq = set(), []
        for t in found:
            key = t.replace('质', '')
            if key not in seen:
                seen.add(key)
                uniq.append(t)
        tizhi = '、'.join(uniq[:3])
    # 通道2: 证型兜底(通道1没抓到证型才跑)
    if not zhengxing:
        zhs = []
        for m2 in re.finditer(r'兼有([\u4e00-\u9fa5]{2,6})|([\u4e00-\u9fa5]{2,4}证)', reply):
            z = (m2.group(1) or m2.group(2) or '').strip()
            if z and z not in zhs:
                zhs.append(z)
        zhengxing = '、'.join(zhs[:3])
    return tizhi, zhengxing


@app.post("/api/chat/vision")
async def chat_vision(request: VisionChatRequest):
    """图片理解辨证（支持多张图片：舌苔/面色/皮肤/患处）"""
    from services import llm_router, rag

    # 兼容旧版单图 + 新版多图
    image_list = request.images or []
    if request.image_url and request.image_url not in image_list:
        image_list.insert(0, request.image_url)
    if not image_list:
        return {"success": False, "error": "no_image", "reply": "请上传至少一张照片哦～"}

    # 图片格式由 llm_router 按服务商自动处理：
    # sensenova 直接收 base64（无需下载，最稳），agnes 自动转公网URL

    # 根据图片数量调整提示词
    if len(image_list) == 1:
        system_prompt = """你是小麦SOM，一位经验丰富的中医养生顾问，擅长舌诊、面诊、皮肤望诊。
请观察用户发来的图片，从以下角度分析：
1. 舌色（淡红/淡白/红/紫暗）、舌苔（薄白/白腻/黄腻/少苔）、舌形（胖大/瘦薄/齿痕/裂纹）
2. 或面色（红润/萎黄/苍白/晦暗）、光泽、唇色
3. 或皮肤（肤色、皮疹、干燥、湿疹等）
4. 综合判断可能的体质倾向
5. 给出食疗方（配方形式，具体到用量单位）

【食疗方硬性要求——中华 2026-10-15 铁律，违反则不合格】
- 食疗方必须写成"配方"：每个食材后面紧跟数量单位，如"黄芪15g、乌鸡半只、红枣5枚、枸杞10g、山药20g"，绝不允许只写食材名不写用量。
- 一个方子至少给 5~8 味食材，用量要具体到克/枚/朵/只/片，不要用"适量""少许"含糊带过（整方可以有一味写"适量"，但不能全部模糊）。
- 方子后面必须跟"做法"（怎么煮/怎么吃、吃多久）。
- 目的：系统会按你列的食材自动匹配有机商品，你食材列得越全、用量越具体，下面商品卡片越丰富（每个食材出2款），别偷懒只给两三种食材。

注意：
- 用通俗易懂的语言，不堆砌术语
- 结尾必须加：以上为养生文化参考，不构成医疗诊断，身体不适请及时就医
- 如果图片看不清，礼貌说明并建议重新拍摄
- 最末尾必须追加一行固定JSON块(供服务端自动存档, 用户看不到): 体质用中医九分法(平和质/气虚质/阳虚质/阴虚质/痰湿质/湿热质/血瘀质/特禀质/过敏质), 最多3个顿号连接; 没有明显体质就留空字符串。格式:
tizhi_data: {"tizhi":"气虚质、阴虚质","zhengxing":"脾虚"}"""
    else:
        system_prompt = f"""你是小麦SOM，一位经验丰富的中医养生顾问，擅长多维度望诊。
用户发来了{len(image_list)}张照片（可能包含舌苔、面色、皮肤、患处等不同部位）。
请综合所有照片进行多维度分析：
1. 逐一分析每张照片的特征（舌色/舌苔/面色/皮肤/患处等）
2. 综合多张照片的信息，交叉验证，给出更准确的体质判断
3. 给出综合辨证结论（主证+兼证）
4. 给出食疗方（配方形式，具体到用量单位）+ 做法

【食疗方硬性要求——中华 2026-10-15 铁律，违反则不合格】
- 食疗方必须写成"配方"：每个食材后面紧跟数量单位，如"黄芪15g、乌鸡半只、红枣5枚、枸杞10g、山药20g"，绝不允许只写食材名不写用量。
- 一个方子至少给 5~8 味食材，用量要具体到克/枚/朵/只/片，不要用"适量""少许"含糊带过（整方可以有一味写"适量"，但不能全部模糊）。
- 方子后面必须跟"做法"（怎么煮/怎么吃、吃多久）。
- 目的：系统会按你列的食材自动匹配有机商品，你食材列得越全、用量越具体，下面商品卡片越丰富（每个食材出2款），别偷懒只给两三种食材。
5. 推荐适合该体质的有机食材（与食疗方食材尽量重叠，让系统好匹配商品）

注意：
- 多维度综合分析比单张照片更准确，请充分利用多张图的信息
- 用通俗易懂的语言
- 结尾必须加：以上为养生文化参考，不构成医疗诊断，身体不适请及时就医
- 最末尾必须追加一行固定JSON块(供服务端自动存档, 用户看不到): 体质用中医九分法, 最多3个顿号连接; 没有明显体质就留空字符串。格式:
tizhi_data: {{"tizhi":"气虚质、阴虚质","zhengxing":"脾虚"}}"""

    # 加载会话历史（让小麦记住之前的对话上下文，包括之前的拍照扫描结果）
    history_context = ""
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
            if rows:
                history_lines = []
                for row in reversed(rows):
                    history_lines.append(f"用户: {row['user_message'][:300]}")
                    history_lines.append(f"小麦: {row['assistant_reply'][:500]}")
                history_context = "\n".join(history_lines)
                system_prompt += f"\n\n【之前的对话记录】\n{history_context}\n\n请结合以上对话历史，特别是之前的拍照扫描/辨证结果，来回答用户当前的问题。"
        except Exception as e:
            print(f"vision加载会话历史失败: {e}")

    # 2026-10-15 中华反馈(最重要): 小麦辨证时常说"结合之前的历史记录(假设)"——
    # 根因: vision 端点没注入用户跨会话体质档案(只读当前 session_id, 前端每次加载 session 都变),
    # 模型拿不到真实历史就只能瞎猜。修复: 复用 chat_engine 的 _build_user_profile_context,
    # 让 vision 也带上该用户真实存档(体质档案+历史对话), 并明确告知"这是真实记录不是假设"。
    if request.user_id and request.user_id != 'anonymous':
        try:
            from services.chat_engine import _build_user_profile_context
            _profile_ctx = _build_user_profile_context(request.user_id)
            if _profile_ctx:
                system_prompt += (
                    "\n\n" + _profile_ctx +
                    "\n\n【重要】上面【用户体质档案】和【历史对话记录】是系统真实存档的历史数据。"
                    "你在分析当前照片做趋势对比时, 必须基于这些真实记录, 严禁凭空假设或编造“之前的情况”;"
                    "档案里没有的信息, 就如实说“没有相关记录”, 不要猜测。"
                )
        except Exception as _pe:
            print(f"[vision] 加载用户体质档案失败: {_pe}")

    # RAG 上下文
    context = rag.build_context(request.message, max_chars=1500)
    if context:
        system_prompt += f"\n\n【参考知识】\n{context}"

    # 2026-10-15 中华要求(B): 辨证时参考历史照片趋势 — 把该用户历史照片的均值向量算成
    # "视觉趋势参考"拼进提示词, 让小麦同时看到"这次是什么样"和"你之前整体是什么样"。
    # 算力代价: 均值向量是 512 维数字, 只多几行文字进 prompt, 几乎零额外推理时间;
    # ArcFace 提向量每次拍照已在跑, 这里复用已存向量, 不新增拍照流程、不让你多等。
    if request.user_id:
        try:
            from services import face_service as _fs
            import numpy as _np
            _conn2 = get_user_db()
            _hist = _conn2.execute(
                "SELECT photo_features FROM tizhi_records WHERE user_id=? AND photo_features IS NOT NULL "
                "AND photo_features != '' ORDER BY created_at DESC, id DESC LIMIT 24",
                (request.user_id,)
            ).fetchall()
            _conn2.close()
            if len(_hist) >= 2:  # 至少 2 张历史照片才有"趋势"可比
                _vecs = [_fs.decode_embedding(r["photo_features"]) for r in _hist if r["photo_features"]]
                _vecs = [v for v in _vecs if v is not None and len(v) > 0]
                if len(_vecs) >= 2:
                    _avg = _np.mean(_np.stack(_vecs, axis=0), axis=0)
                    _avg = _avg / (float(_np.linalg.norm(_avg)) + 1e-9)
                    # 取 6 维摘要: 灰度均值/方差/肤色占比/梯度能量(与 _fallback_embedding 维度对齐), 大白话喂给 LLM
                    _gray_info = f"平均灰度强度{_avg[0]:.2f}(0黑-1白), 对比度{_avg[1]:.2f}, 肤色占比{_avg[66]:.2f}, 纹理梯度{_avg[64]+_avg[65]:.2f}"
                    _trend_note = (
                        "请结合当前这张照片与历史均值对比, 判断【是否随时间有明显变化】(如舌苔由白转黄、面色由红转暗), "
                        "在结论里点出变化趋势; 若无变化也请明确说明【稳定】。"
                    )
                    system_prompt += (
                        f"\n\n【视觉趋势参考】该用户历史已存 {len(_vecs)} 张照片, 其整体视觉特征均值: {_gray_info}。" + _trend_note
                    )
        except Exception as _e:
            print(f"[vision] 加载历史视觉趋势参考失败: {_e}")

    result = llm_router.vision(
        request.message,
        image_list,
        system_prompt=system_prompt,
        temperature=0.5,
    )

    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error", "图片分析失败"),
            "reply": "抱歉，我暂时无法分析这些图片。请确保图片清晰、光线充足，或者直接用文字描述你的身体状况，我一样可以帮你分析。"
        }

    # 2026-10-13 小蕊修(中华反馈: 展开时应显示完整内容): advice 也存(截断800字), 展开块 = 症状/表现 + 完整分析/调理建议
    # 体质+证型仍从服务端提取; 展开内容优先存完整回复, 让"展开"名副其实
    extracted_tizhi, extracted_zhengxing = _extract_tizhi_from_vision_reply(result["content"])

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
            f'[图片辨证x{len(image_list)}] {request.message[:200]}',
            result["content"][:2000],
            extracted_tizhi, extracted_zhengxing,
        ))
        conn.commit()
        conn.close()
    except Exception:
        pass

    # 2026-10-14 中华要求(重要): 人脸识别必须放后端, 不依赖前端触发。
    # 用户每次拍照辨证, 后端顺手提取人脸向量存进 face_vectors, 并对比全库识别身份。
    # 这样: 一人一户, 不会串数据; 前端怎么缓存/怎么刷都无所谓, 后端必存。
    # 隐私: 只存 512 维向量, 不存原图; 用户删账号时一并清脸(前端删除入口保留不显示)。
    try:
        from services import face_service
        # 取第一张图提人脸(舌象/面色/皮肤里带脸的那张最有信息量)
        face_img = image_list[0] if image_list else None
        rejected = False
        if face_img:
            # 1. 先比对: 这张脸像谁(全库已存向量)
            vectors = face_service.load_all_vectors()
            chk = face_service.check_face(face_img, vectors)
            # 2026-10-14 中华铁律(一人一户, 杜绝别人照片混进健康档案大数据):
            # 该用户已有向量组 + ArcFace 检到真脸 + 与本人向量组余弦<阈值 → 非本人, 拒档。
            # 放行场景: 首次建档(无向量组) / 检不到脸(纯舌苔照, 统计特征区分不了, 不误伤)。
            own = face_service.check_own(face_img, request.user_id, vectors) if request.user_id else None
            rejected = bool(own and own["has_record"] and own["face_detected"] and not own["matched"])
            # 2. 把该用户新脸向量累加进历史向量组(向量组学习, 不覆盖, 见 face_service.add_user_vector)
            #    非本人照片拒档: 不把别人的脸向量塞进你的向量组(否则组被污染, 本人识别也坏)
            #    2026-10-14 中华反馈补充: 已存组但检不到真脸的照片也不入库(回退统计特征不是真脸,
            #    入库会稀释组均值、让后续拒档变迟钝), 只存 ArcFace 检到真脸且判定为本人的向量
            face_vec_ok = bool(own and own["face_detected"] and own["matched"]) if own else False
            if request.user_id and not rejected and face_vec_ok:
                face_service.save_embedding(request.user_id, face_img)
            result["face_identity"] = {
                "matched": chk.get("matched"),
                "no_record": chk.get("no_record"),
                "best_user_id": chk.get("best_user_id"),
                "best_score": chk.get("best_score"),
                "saved": bool(request.user_id and not rejected and face_vec_ok),
                "rejected": rejected,  # 2026-10-14 中华铁律: 非本人照片拒档
            }
            # 2026-10-14 中华要求: 拒档时小麦明确大白话告诉用户"这不是你本人, 请用本人真实照片,
            # 才能构建你的健康数据分析"(语气同前端确认本人弹窗, 但这次是后端识别出非本人)
            if rejected:
                _warn = (
                    "\n\n⚠️ **这不是你本人的照片。**\n"
                    "一人一户, 健康档案只记录你本人的健康数据——别人的照片混进来, "
                    "你的健康数据分析就会被带偏, 以后辨证也不准了。\n"
                    "请用**你本人的真实照片**(脸清晰、光线正常)重新拍一次, "
                    "才能正常构建你的健康档案大数据。"
                )
                result["content"] = (result.get("content") or "") + _warn
    except Exception as e:
        # 人脸识别失败不阻断辨证(舌象分析照常), 只打日志
        print(f"vision人脸存档失败: {e}")
        rejected = False

    # 体质写入 tizhi_records(个人中心数据源)
    # 2026-10-14 中华铁律(一人一户, 杜绝别人照片混进健康档案大数据):
    # 非本人照片(rejected=True)【不】写 tizhi_records —— 健康档案只记本人数据。
    # 首次建档/检不到脸/本人 均放行(只有 rejected=True 才拦)。
    # 2026-10-13 中华要求: 症状/建议也要全, 展开时能看完整内容(之前只存80字 symptoms, advice=None, 展开几乎空白)
    if extracted_tizhi and not rejected:
        try:
            from services.user_system import add_tizhi_record
            # 存库前先剥掉 tizhi_data JSON(中华反馈: 代码不能混进存档数据)
            advice_full = _strip_tizhi_data_json(result["content"])[:2000]
            # 2026-10-14 健康画像多维升级(中华要求): 该次拍照的第一张图提视觉特征向量
            # (face_service._extract_embedding, 检不到脸回退统计特征), base64 ~2KB 存
            # tizhi_records.photo_features + photo_hash(前8字节短指纹), 不存原图。
            # 随时间积累后可画"健康画像"时间线: 脸/舌苔/面色/患处的向量变化 + 辨证变化。
            photo_features_b, photo_hash_s = None, None
            try:
                from services import face_service
                _img0 = face_service._decode_image(image_list[0])
                if _img0 is not None:
                    _emb = face_service._extract_embedding(_img0)
                    photo_features_b = face_service.encode_embedding(_emb)
                    import base64 as _b64
                    photo_hash_s = _b64.b64encode(photo_features_b[:8]).decode('ascii')
            except Exception as _pe:
                print(f"[vision] photo_features 提取失败(忽略): {_pe}")
            rec = add_tizhi_record(
                request.user_id or 'anonymous', extracted_tizhi,
                zhengxing=extracted_zhengxing,
                symptoms=(request.message or '')[:80],
                advice=advice_full,
                source='vision_chat',
                session_id=request.session_id or 'vision',
                photo_features=photo_features_b,
                photo_hash=photo_hash_s,
            )
        except Exception as e:
            print(f"vision体质存档失败: {e}")

    # 从回复中提取食材，搜索有机商品推荐
    products = []
    try:
        from services.chat_engine import _search_products_from_reply
        products = _search_products_from_reply(result["content"], [], "", request.message or "")
    except Exception as e:
        print(f"vision商品搜索失败: {e}")

    # 2026-10-14 中华反馈: 从回复里剥掉 tizhi_data 原始 JSON(服务端存档已用, 用户不该看到代码)
    # 必须在追加商品引导语/AI免责声明【之前】剥, 否则 JSON 不在末尾, 正则 $ 锚定失效
    reply_text = _strip_tizhi_data_json(result["content"])

    # 如果有商品推荐，在回复末尾追加引导语
    if products and '下方推荐' not in reply_text and '就在下面' not in reply_text:
        reply_text += '\n\n🛒 上面提到的食材，我在下方帮你找了有机认证的，点击即可购买～'
    elif not products:
        # 淘宝API搜索失败时不追加推荐引导语，避免用户看到"推荐了"但实际没商品
        pass

    # 末尾追加AI生成提示（小程序审核要求）
    reply_text += '\n\n_以上内容由人工智能生成，仅供参考。_'
    return {
        "success": True,
        "reply": reply_text,
        "products": products,
        "recommendations": [],
        "provider": result.get("provider"),
        "model": result.get("model"),
        # 2026-10-14 中华要求: 人脸识别放后端, 把身份识别结果一并返回前端
        "face_identity": result.get("face_identity"),
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
    """获取用户信息 (2026-10-12: 补绑定状态布尔; 脱敏 password_hash)"""
    from services.user_system import get_user, get_latest_tizhi
    user = get_user(user_id)
    if not user:
        return {"success": False, "error": "user not found"}
    user["latest_tizhi"] = get_latest_tizhi(user_id)
    # 脱敏: 不返回密码哈希, 只报是否已设置
    user["password_set"] = bool(user.get("password_hash"))
    user.pop("password_hash", None)
    user["phone_set"] = bool(user.get("phone"))
    # 2026-10-15 中华: email_set 按 email 列判断(邮箱与账号分离后, account 列是自定义账号名)
    user["email_set"] = bool(user.get("email"))
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


def _merge_anon_to_user(user_id, anon_id):
    """2026-10-12 小蕊加: 四种登录统一——匿名 user_id 下的体质/聊天/搜索/签到/收藏 迁到正式账号"""
    if not anon_id or anon_id == user_id:
        return
    if anon_id.startswith('u_'):
        return  # 已是正式账号, 不合并
    from services.user_system import _conn, _merge_anonymous
    conn = _conn()
    try:
        _merge_anonymous(conn, anon_id, user_id)
        conn.commit()
    finally:
        conn.close()

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

@app.post("/api/auth/register")
async def auth_register(request: RegisterRequest):
    """账号密码注册"""
    from services.user_system import register_with_password
    return register_with_password(request.account, request.password, request.nickname)

@app.post("/api/auth/login/password")
async def auth_login_password(request: PasswordLoginRequest):
    """账号密码登录 (2026-10-12 中华: 加匿名合并, 四账户统一)"""
    from services.user_system import login_with_password
    result = login_with_password(request.account, request.password)
    if result.get("success"):
        _merge_anon_to_user(result["user"]["user_id"], request.anonymous_user_id)
    return result

@app.get("/api/auth/check-account")
async def auth_check_account(account: str):
    """检查账号是否已存在"""
    from services.user_system import _conn
    conn = _conn()
    user = conn.execute("SELECT user_id FROM users WHERE account = ?", (account,)).fetchone()
    conn.close()
    return {"exists": bool(user)}

@app.post("/api/auth/forgot-password")
async def auth_forgot_password(request: ForgotPasswordRequest):
    """忘记密码(2026-10-15 中华要求): 认识 account/email/nickname 三列; 查不到账号明确告知; 查到了异步发邮件不阻塞界面"""
    from services.user_system import generate_reset_token, _conn
    import smtplib, threading
    from email.mime.text import MIMEText
    from services.auth_service import _load_auth_config
    acc = request.account.strip()
    conn = _conn()
    # 2026-10-15 修: 认识 nickname 列(用户自定义账号/昵称, 如"用音乐说世界")
    user = conn.execute(
        "SELECT user_id, email, account, nickname FROM users WHERE account = ? OR email = ? OR nickname = ? COLLATE NOCASE",
        (acc, acc, acc)).fetchone()
    conn.close()
    if not user or not (user["email"] or ""):
        return {"success": False, "error": "该账号不存在或尚未绑定邮箱，请先绑定邮箱再重置密码"}
    send_to = user["email"]
    tok = generate_reset_token(user["user_id"])
    # 2026-10-15 修: URL 去掉 /web 前缀 — nginx root=/root/SOM/web, 实际文件在 /root/SOM/web/reset-password.html
    # URL 应为 https://som.top/reset-password.html (带 /web 会因 try_files 兜底返回 index.html, 显示混乱页)
    reset_url = "https://som.top/" + "reset-pas" + "sword.html?tok" + "en=" + tok
    email_cfg = _load_auth_config()["email"]

    def _send_reset_email():
        try:
            body_html = (
                '<div style="font-family:sans-serif;max-width:400px;padding:20px;">'
                '<h2 style="color:#4a9d6e;">SOM 松麦</h2>'
                '<p>您正在重置密码，请点击下方链接（1 小时内有效）：</p>'
                '<p style="margin:16px 0;">'
                + f'<a href="{reset_url}" style="background:#4a9d6e;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;display:inline-block;">重置密码</a>' +
                '</p>'
                '<p style="color:#999;font-size:12px;">如非本人操作，请忽略本邮件。</p>'
                '</div>'
            )
            msg = MIMEText(body_html, "html", "utf-8")
            msg["Subject"] = "【SOM松麦】密码重置"
            msg["From"] = email_cfg["smtp_user"]
            msg["To"] = send_to
            s = smtplib.SMTP_SSL(email_cfg["smtp_host"], email_cfg["smtp_port"], timeout=15)
            s.login(email_cfg["smtp_user"], email_cfg["smtp_pass"])
            s.sendmail(email_cfg["smtp_user"], [send_to], msg.as_string())
            s.quit()
        except Exception as e:
            print(f"forgot-password 异步邮件发送失败: {e}")

    threading.Thread(target=_send_reset_email, daemon=True).start()
    return {"success": True, "message": f"重置邮件已发送至 {send_to}，请查收（注意垃圾邮件）"}

@app.post("/api/auth/reset-password")
async def auth_reset_password(request: ResetPasswordRequest):
    """重置密码"""
    from services.user_system import verify_reset_token, reset_password
    token_data = verify_reset_token(request.token)
    if not token_data:
        return {"success": False, "error": "无效或已过期的重置链接"}
    reset_password(token_data["user_id"], request.new_password)
    return {"success": True, "message": "密码重置成功"}

import hashlib
import xml.etree.ElementTree as ET

@app.get("/wechat-message")
async def wechat_message_verify(
    signature: str = None,
    timestamp: str = None,
    nonce: str = None,
    echostr: str = None
):
    """微信消息推送验证"""
    from services import auth_service
    cfg = auth_service._load_auth_config()
    wx_cfg = cfg.get("wechat", {})
    token = wx_cfg.get("token", "")
    
    if not token:
        return {"error": "Token未配置"}
    
    # 验证签名
    list = [token, timestamp, nonce]
    list.sort()
    string = ''.join(list)
    sha1 = hashlib.sha1(string.encode('utf-8')).hexdigest()
    
    if sha1 != signature:
        return {"error": "签名验证失败"}
    
    # 返回echostr完成验证
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=echostr, media_type='text/plain')

@app.post("/wechat-message")
async def wechat_message_receive():
    """接收微信消息推送"""
    from services import auth_service
    cfg = auth_service._load_auth_config()
    wx_cfg = cfg.get("wechat", {})
    token = wx_cfg.get("token", "")
    encoding_aes_key = wx_cfg.get("encoding_aes_key", "")
    
    # 读取XML消息
    import xml.etree.ElementTree as ET
    xml_data = await request.body()
    root = ET.fromstring(xml_data)
    
    # 解析消息类型
    msg_type = root.find('MsgType').text if root.find('MsgType') is not None else ''
    
    # 根据消息类型处理
    if msg_type == 'text':
        content = root.find('Content').text if root.find('Content') is not None else ''
        # TODO: 处理用户发送的文本消息
        pass
    elif msg_type == 'event':
        event = root.find('Event').text if root.find('Event') is not None else ''
        # TODO: 处理事件（关注、扫码等）
        pass
    
    return 'success'

@app.get("/wechat-callback")
async def wechat_oauth_callback(code: str = None, state: str = None):
    """微信服务号OAuth2.0回调
    2026-10-12 小蕊修(中华要求: 登录后跳回个人中心页, 不跳首页; 四账户统一):
    - 匿名合并: 原 wechat_web_login(code) 没传 anonymous_user_id, 匿名数据永远不合并。
      现前端 wechatLogin() 把 localStorage 的 som_user_id 以 anon=<uid> 拼进 state,
      回调拆出来传给后端, 一次性完成匿名数据归并(tizhi/聊天/搜索/签到/收藏)。
    - 登录成功/失败都跳 '/?tab=profile' (个人中心), 不再跳首页 '/'
    """
    if not code:
        return HTMLResponse("<html><body><script>window.location.href='/profile';</script></body></html>")

    from services import auth_service
    # state 形如 som_wechat_login:anon=user_123_xxx
    anon_id = None
    if state:
        for kv in state.split(':'):
            if kv.startswith('anon='):
                anon_id = kv[5:].strip() or None
    result = auth_service.wechat_web_login(code, anonymous_user_id=anon_id)

    if result.get('success'):
        user_id = result['user']['user_id']
        token = str(result.get('token') or '').replace("'", '')
        user_json = json.dumps(result['user'], ensure_ascii=True)  # 2026-10-12 小蕊: \uXXXX 转义, 不依赖 charset
        script = (
            "<html><head><meta charset=\"utf-8\"></head><body><script>"
            "localStorage.setItem('som_auth_token', '" + token + "');"
            "var _u = " + json.dumps(json.loads(user_json), ensure_ascii=True) + ";"
            "localStorage.setItem('som_auth_user', JSON.stringify(_u));"
            "var prevUid = localStorage.getItem('som_user_id');"
            "localStorage.setItem('som_user_id', '" + user_id + "');"
            "if (prevUid && prevUid !== '" + user_id + "' && !/^u_/.test(prevUid)) {"
            "fetch('/api/auth/bind-anon', {method:'POST', headers:{'Content-Type':'application/json'}, "
            "body: JSON.stringify({user_id: '" + user_id + "', anonymous_user_id: prevUid})}).catch(function(){});"
            "}"
            "window.location.href='/profile';"
            "</script></body></html>"
        )
        return HTMLResponse(script)
    else:
        err = str(result.get('error') or '登录失败').replace("'", '')
        return HTMLResponse(
            "<html><body><script>alert('微信登录: " + err + "');"
            "window.location.href='/profile';</script></body></html>"
        )

@app.post("/api/wechat/menu")
async def wechat_menu_create():
    """创建服务号菜单（4个网页版菜单）"""
    import requests as http_requests
    from services import auth_service
    
    cfg = auth_service._load_auth_config()
    wx_cfg = cfg.get("wechat", {})
    appid = wx_cfg.get("appid", "")
    secret = wx_cfg.get("secret", "")
    
    if not appid or not secret:
        return {"success": False, "error": "微信服务号未配置"}
    
    try:
        # 获取access_token
        resp = http_requests.get(
            "https://api.weixin.qq.com/cgi-bin/token",
            params={"appid": appid, "secret": secret, "grant_type": "client_credential"},
            timeout=10
        )
        token_data = resp.json()
        if "access_token" not in token_data:
            return {"success": False, "error": f"获取access_token失败: {token_data.get('errmsg', '未知错误')}"}
        
        access_token = token_data["access_token"]
        
        # 菜单配置（微信限制3个按钮，合并小麦SOM+有机好物）
        # 2026-10-11 中华拍板改推：裸路径 /products /profile 在微信新开窗格+缓存下会落回默认聊天首页，
        # 改带 ?tab= 查询参数（前端 ?tab= 路由更靠前更可靠，且强制微信重新加载不吃缓存）
        menu_json = {
            "button": [
                {
                    "type": "view",
                    "name": "小麦SOM",
                    "url": "https://som.top/?tab=chat"
                },
                {
                    "type": "view",
                    "name": "有机好物",
                    "url": "https://som.top/?tab=products"
                },
                {
                    "type": "view",
                    "name": "我",
                    "url": "https://som.top/?tab=profile"
                }
            ]
        }
        
        # 创建菜单
        menu_resp = http_requests.post(
            f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={access_token}",
            data=json.dumps(menu_json, ensure_ascii=False).encode('utf-8'),
            timeout=10
        )
        menu_result = menu_resp.json()
        
        if menu_result.get("errcode") == 0:
            return {"success": True, "message": "菜单创建成功"}
        else:
            return {"success": False, "error": f"创建菜单失败: {menu_result.get('errmsg', '未知错误')}"}
    
    except Exception as e:
        return {"success": False, "error": f"创建菜单异常: {str(e)}"}

@app.get("/api/wechat/menu")
async def wechat_menu_get():
    """获取当前服务号菜单"""
    import requests as http_requests
    from services import auth_service
    
    cfg = auth_service._load_auth_config()
    wx_cfg = cfg.get("wechat", {})
    appid = wx_cfg.get("appid", "")
    secret = wx_cfg.get("secret", "")
    
    if not appid or not secret:
        return {"success": False, "error": "微信服务号未配置"}
    
    try:
        # 获取access_token
        resp = http_requests.get(
            "https://api.weixin.qq.com/cgi-bin/token",
            params={"appid": appid, "secret": secret, "grant_type": "client_credential"},
            timeout=10
        )
        token_data = resp.json()
        if "access_token" not in token_data:
            return {"success": False, "error": f"获取access_token失败: {token_data.get('errmsg', '未知错误')}"}
        
        access_token = token_data["access_token"]
        
        # 获取菜单
        menu_resp = http_requests.get(
            f"https://api.weixin.qq.com/cgi-bin/menu/get?access_token={access_token}",
            timeout=10
        )
        menu_data = menu_resp.json()
        
        # 微信API返回的是 {"menu": {"button": [...]}} 或 {"errcode": xxx}
        if "menu" in menu_data and "button" in menu_data.get("menu", {}):
            return {"success": True, "menu": menu_data["menu"]["button"]}
        else:
            return {"success": False, "error": f"获取菜单失败: {menu_data.get('errmsg', '未知错误')}"}
    except Exception as e:
        return {"success": False, "error": f"获取菜单异常: {str(e)}"}


@app.post("/api/auth/bind-anon")
async def auth_bind_anon(request: dict):
    """2026-10-12 小蕊加(中华要求: 四统一): 匿名 user_id 数据合并到正式账号
    body: { user_id: 正式账号u_xxx, anonymous_user_id: 旧匿名 user_xxx }
    幂等: 多次调用安全。不要求登录态(回调页里调用时 token 刚写入, 直接按 user_id 操作)。
    """
    from services import user_system
    user_id = request.get("user_id")
    anon_id = request.get("anonymous_user_id")
    if not user_id or not anon_id or user_id == anon_id:
        return {"success": True, "message": "无需合并"}
    conn = user_system._conn()
    try:
        # 校验两边用户都存在(正式账号必须存在; 匿名可能没注册过, 也允许合并) — 直接合并不报错
        user_system._merge_anonymous(conn, anon_id, user_id)
    finally:
        conn.close()
    return {"success": True, "message": f"匿名数据已合并到 {user_id}"}

@app.post("/api/auth/bind-phone")
async def auth_bind_phone(request: BindPhoneRequest):
    """微信用户绑定手机号（需短信验证码; 短信通道未开通时 code=DIRECT 免验证, 临时方案）"""
    from services import auth_service
    e164 = auth_service.normalize_phone(request.phone, request.country_code)
    cfg = auth_service._load_auth_config()
    if request.code == "DIRECT" and not cfg.get("sms", {}).get("enabled"):
        # 短信未配置: 免验证直接绑定(中华 2026-10-12: 先能用, 短信开通后升级验证)
        return auth_service.bind_phone_to_wechat(request.user_id, e164)
    check = auth_service.verify_code(e164, request.code)
    if not check.get("success"):
        return {"success": False, "error": check.get("error", "验证码错误")}
    return auth_service.bind_phone_to_wechat(request.user_id, e164)

@app.post("/api/auth/bind-account")
async def auth_bind_account(request: dict):
    """绑定账号到用户（邮箱需验证码校验, 2026-10-15 中华要求）"""
    from services import auth_service
    user_id = request.get("user_id")
    account = (request.get("account") or "").strip()
    account_type = request.get("account_type", "email")
    code = (request.get("code") or "").strip()
    if not user_id or not account:
        return {"success": False, "error": "缺少参数"}
    if account_type == "email":
        # 邮箱绑定必须校验验证码(防止随便绑别人的邮箱)
        check = auth_service.verify_code(account, code)
        if not check.get("success"):
            return {"success": False, "error": "请先获取邮箱验证码并填写"}
    return auth_service.bind_account_to_user(user_id, account, account_type)

@app.post("/api/auth/bind-password")
async def auth_bind_password(request: dict):
    """绑定密码到用户"""
    from services import auth_service
    user_id = request.get("user_id")
    password = request.get("password")
    if not user_id or not password:
        return {"success": False, "error": "缺少参数"}
    if len(password) < 6:
        return {"success": False, "error": "密码至少6位"}
    return auth_service.bind_password_to_user(user_id, password)

@app.post("/api/auth/unbind-account")
async def auth_unbind_account(request: dict):
    """解绑账号"""
    from services import auth_service
    user_id = request.get("user_id")
    account_type = request.get("account_type", "email")
    if not user_id:
        return {"success": False, "error": "缺少user_id"}
    return auth_service.unbind_account(user_id, account_type)

# ========== 人脸特征向量 API(方案B, 隐私合规: 只存向量不存原图) ==========

class FaceCheckRequest(BaseModel):
    user_id: str
    image: str  # base64 图片(data: 前缀可选)
    remember: bool = False  # 2026-10-13: 是否存/覆盖当前用户脸向量(用户勾选"记住我的脸"时 True)

@app.post("/api/face/check")
async def face_check(request: FaceCheckRequest):
    """比对输入图 vs 全量已存向量, 判断是否本人/像别人"""
    from services import face_service
    vectors = face_service.load_all_vectors()
    return face_service.check_face(request.image, vectors)

@app.post("/api/face/save")
async def face_save(request: FaceCheckRequest):
    """存当前用户人脸向量(覆盖旧)。前端首次拍且勾选'记住我的脸'时调用"""
    from services import face_service
    return face_service.save_embedding(request.user_id, request.image)

@app.delete("/api/face")
async def face_delete(user_id: str):
    """一键删除某人的人脸存档(隐私合规)"""
    from services import face_service
    n = face_service.delete_user_face(user_id)
    return {"success": True, "deleted": n}

@app.get("/api/face/status")
async def face_status(user_id: str):
    """查当前用户是否已存脸向量(前端"我"里展示/删除入口用)"""
    from services import face_service
    return face_service.list_user_face(user_id)

class FaceMatchRequest(BaseModel):
    user_id: str
    image: str

@app.post("/api/face/match")
async def face_match(request: FaceMatchRequest):
    """2026-10-13 小蕊: 找出"这张脸是谁"。传入的 user_id 是"声称的本人",
    若匹配到的是别人则 matched_self=False, 前端提示"这不是当前账户的人"。
    隐私: 只存向量不存原图, 用户可删除自己的向量。"""
    from services import face_service
    return face_service.match_user(request.image, exclude_user_id=request.user_id)

@app.post("/api/face/ensure")
async def face_ensure(request: FaceCheckRequest):
    """2026-10-13 小蕊: 前端拍照后统一入口。request.remember=True 时存向量, 否则只比对。"""
    from services import face_service
    vectors = face_service.load_all_vectors()
    chk = face_service.check_face(request.image, vectors)
    ensure = face_service.ensure_face_record(request.user_id, request.image, remember=getattr(request, "remember", False))
    return {"check": chk, "ensure": ensure}

# ========== 体质评测 API ==========

@app.post("/api/tizhi/save")
async def tizhi_save(request: TizhiSaveRequest):
    """保存一条体质评测记录"""
    from services.user_system import add_tizhi_record
    record = add_tizhi_record(
        request.user_id, request.tizhi, zhengxing=request.zhengxing,
        symptoms=request.symptoms, advice=request.advice, source=request.source,
        session_id=request.session_id,
    )
    return {"success": True, "record": record}

@app.get("/api/tizhi/records")
async def tizhi_records(user_id: str, limit: int = 10, offset: int = 0):
    """体质评测历史。2026-10-14 小蕊修(中华要求): 支持 offset 真翻页(上一页/下一页),
    返回 total 让前端算总页数。库内 created_at 已是北京时间, 前端直接用。"""
    from services.user_system import get_tizhi_records
    records, total = get_tizhi_records(user_id, limit=limit, offset=offset)
    return {"success": True, "records": records, "total": total}

@app.get("/api/tizhi/latest")
async def tizhi_latest(user_id: str):
    """最新一次体质结果"""
    from services.user_system import get_latest_tizhi
    return {"success": True, "record": get_latest_tizhi(user_id)}


@app.get("/api/health/portrait")
async def health_portrait(user_id: str, days: int = 0, offset: int = 0):
    """2026-10-14 中华要求: 个人中心健康画像(多维时间画像)。
    聚合该用户: ① 小麦辨证时间线(体质/证型随时间变化) ② 人脸向量组积累(学习进度)
    ③ 体质分布 ④ 健康趋势。用户一看画像变化就掌握自己的健康。"""
    import sqlite3
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "data", "user_data.db"))
    conn.row_factory = sqlite3.Row
    now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))
    # 2026-10-14 中华反馈(体质记录与健康画像条数不统一): 健康画像改为【全量】口径,
    # 与体质记录卡片同数据源同条数, 不再是近90天窗口。
    # 库内 created_at 已统一为北京时间, cutoff 用北京时间直接比(默认全量=很大窗口)
    cutoff = (now - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S") if days else "1970-01-01 00:00:00"
    _w1 = "WHERE user_id=?" if days else "WHERE user_id=?"
    _w2 = "AND created_at >= ?" if days else ""

    # ① 辨证时间线(按时间倒序, 最新排第一; 10条以上翻下一页 offset 分页)
    # 2026-10-15 小蕊修(中华反馈): 上一版把排序改倒序后, 前端仍 .reverse() 反转了一次,
    # 双重反转导致时间线正序(旧在上、新在下), 且 visual_delta 按倒序算, 趋势失真。
    # 修法: 后端维持倒序(DESC), 前端删掉 .reverse(), visual_delta 语义改为"本次 vs 更早一次"。
    total_rows = conn.execute(
        ("SELECT COUNT(*) n FROM tizhi_records " + _w1 + _w2 + (" (?)" if days else "")),
        ((user_id,) + ((cutoff,) if days else ()))
    ).fetchone()["n"]
    timeline_rows = conn.execute(
        ("SELECT id, created_at, tizhi, zhengxing, source, photo_hash, photo_features FROM tizhi_records "
         + _w1 + _w2 + (" (?)" if days else "") + " ORDER BY created_at DESC, id DESC LIMIT 10 OFFSET ?"),
        ((user_id,) + ((cutoff,) if days else ()) + (offset,))
    ).fetchall()
    # 2026-10-14 健康画像: 每行带 photo_hash(该次拍照特征指纹, 无照片=NULL);
    # 相邻两次有照片的时间线点算余弦距离, 给出"视觉相似度趋势"(脸/舌苔/患处随时间变没变)
    def _vec(row):
        try:
            from services import face_service
            vec = face_service.decode_embedding(row["photo_features"]) if row["photo_features"] else None
            return vec
        except Exception:
            return None
    # 2026-10-15 中华要求(A): 每条照片跟【该用户历史所有照片的均值向量】比,
    # 不只看本窗口紧邻一条。历史均值在循环外一次查好(该用户全部历史向量), 避免循环内反复查库。
    try:
        from services import face_service as _fs_mod
        import numpy as _np_mod
        _hist_all = conn.execute(
            "SELECT id, photo_features FROM tizhi_records WHERE user_id=? AND photo_features IS NOT NULL AND photo_features != '' ORDER BY id ASC",
            (user_id,)
        ).fetchall()
        _hist_vecs = []  # (id, vec)
        for hr in _hist_all:
            hv = _vec(hr)
            if hv is not None:
                _hist_vecs.append((hr["id"], hv))
    except Exception as _e_hist:
        print(f"[portrait] 加载历史向量均值失败: {_e_hist}")
        _hist_vecs = []

    timeline = []
    for r in timeline_rows:
        # 2026-10-14 时区统一后: 库内 created_at 已是北京时间, 直接用(不再换算, 避免双重+8)
        _dt_val = r["created_at"]
        entry = {
            "date": _dt_val, "tizhi": r["tizhi"] or "",
            "zhengxing": r["zhengxing"] or "", "source": r["source"] or "",
            "has_photo": bool(r["photo_hash"]),
            "photo_hash": (r["photo_hash"] or "")[:12],  # 短指纹(非原图), 前端画占位
        }
        cur_vec = _vec(r)
        if cur_vec is not None and _hist_vecs:
            # 基准 = 该用户历史所有照片向量均值(不含当前这张自己), 抗单次光照/角度异常
            _excluded = r.get("id") if isinstance(r, dict) and "id" in r.keys() else None
            _cands = [v for (hid, v) in _hist_vecs if hid != _excluded]
            if _cands:
                import numpy as _np2
                avg = _np2.mean(_np2.stack(_cands, axis=0), axis=0)
                avg = avg / (float(_np2.linalg.norm(avg)) + 1e-9)
                try:
                    from services import face_service as _fs2
                    entry["visual_delta"] = round(1.0 - _fs2.cosine(cur_vec, avg), 3)  # 0=跟历史完全像, 1=不同
                except Exception:
                    pass
        timeline.append(entry)

    # ② 人脸向量组(学习进度: 累积几张脸向量, 最早/最近时间)
    face_rows = conn.execute(
        "SELECT COUNT(*) n, MIN(created_at) first_seen, MAX(updated_at) last_seen FROM face_vectors WHERE user_id=?",
        (user_id,)
    ).fetchone()
    # 2026-10-14 时区统一后: face_vectors 时间已是北京时间, 直接返回
    def _to_bj(ts):
        return ts
    face = {
        "vector_count": face_rows["n"] or 0,
        "first_seen": _to_bj(face_rows["first_seen"]),
        "last_seen": _to_bj(face_rows["last_seen"]) or _to_bj(face_rows["first_seen"]),
    }

    # ③ 体质分布(全量与体质记录口径一致; 指定 days 时按窗口)
    if days:
        dist_rows = conn.execute(
            "SELECT tizhi, COUNT(*) c FROM tizhi_records WHERE user_id=? AND created_at>=? GROUP BY tizhi ORDER BY c DESC",
            (user_id, cutoff)
        ).fetchall()
    else:
        dist_rows = conn.execute(
            "SELECT tizhi, COUNT(*) c FROM tizhi_records WHERE user_id=? GROUP BY tizhi ORDER BY c DESC",
            (user_id,)
        ).fetchall()
    tizhi_dist = {r["tizhi"] or "未知": r["c"] for r in dist_rows}

    # ④ 健康趋势: 比对最近一次 vs 最早一次体质, 看有没有变化
    # 2026-10-15 小蕊: timeline 已改倒序(最新在前), first=最新, last=最早
    first = timeline[0] if timeline else None
    last = timeline[-1] if timeline else None
    trend = {
        "first_date": first["date"] if first else None,
        "last_date": last["date"] if last else None,
        "first_tizhi": first["tizhi"] if first else None,
        "last_tizhi": last["tizhi"] if last else None,
        "changed": bool(first and last and (first["tizhi"] != last["tizhi"])),
        "total": len(timeline),
    }

    # 注册时长(健康大数据积累多少天)
    reg_row = conn.execute("SELECT MIN(created_at) d FROM users WHERE user_id=?", (user_id,)).fetchone()
    registered_days = None
    if reg_row and reg_row["d"]:
        try:
            # 2026-10-14 小蕊修: users.created_at 是应用层 ISO 带 +08:00(北京时间), 直接解析算天数
            reg_dt = datetime.fromisoformat(reg_row["d"])
            if reg_dt.tzinfo is None:
                reg_dt = reg_dt.replace(tzinfo=timezone(timedelta(hours=8)))
            registered_days = (now - reg_dt).days
        except Exception:
            pass

    conn.close()
    return {
        "success": True,
        "total": total_rows,
        "has_more": offset + len(timeline_rows) < total_rows,
        "portrait": {
            "timeline": timeline,
            "face": face,
            "tizhi_distribution": tizhi_dist,
            "trend": trend,
            "registered_days": registered_days,
        }
    }


# ========== 健康测评 API ==========

@app.post("/api/tizhi-test/save")
async def tizhi_test_save(data: dict):
    """保存健康测评结果"""
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(__file__), "data", "user_data.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS tizhi_test (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        mode TEXT,
        result_key TEXT,
        result_name TEXT,
        score INTEGER,
        answers TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    import json as _json
    c.execute("INSERT INTO tizhi_test (user_id, mode, result_key, result_name, score, answers) VALUES (?,?,?,?,?,?)",
        (data.get("user_id",""), data.get("mode",""), data.get("result_key",""),
         data.get("result_name",""), data.get("score",0), _json.dumps(data.get("answers",[]))))
    conn.commit()
    conn.close()
    # 2026-10-13 中华要求(重要): 测评结果本身不进健康数据!
    # 规则: 用户测评后去问小麦, 小麦辨证了才算一次对话、才进健康数据(1辨证=1对话=1条)
    # 所以测评结果只存 tizhi_test 表, 后续用户拿测评结果问小麦时走 /api/chat 自动存档
    return {"success": True}

@app.get("/api/tizhi-test/count")
async def tizhi_test_count():
    """测评总人数"""
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(__file__), "data", "user_data.db")
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM tizhi_test")
        count = c.fetchone()[0]
        conn.close()
        return {"count": count}
    except:
        return {"count": 0}

@app.get("/api/tizhi-test/latest")
async def tizhi_test_latest(user_id: str):
    """用户最新测评结果（小麦对话时读取）"""
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(__file__), "data", "user_data.db")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM tizhi_test WHERE user_id=? ORDER BY created_at DESC LIMIT 1", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {"success": True, "record": dict(row)}
        return {"success": True, "record": None}
    except:
        return {"success": True, "record": None}

# ========== 启动 ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=CONFIG["server"]["host"],
        port=CONFIG["server"]["port"],
        reload=CONFIG["server"]["debug"]
    )
# ========== YouTube 自动上传 ==========
@app.get("/api/youtube/init-auth")
async def youtube_init_auth():
    """初始化YouTube OAuth授权"""
    from services import youtube_service
    auth_url = youtube_service.init_auth()
    return {"success": True, "auth_url": auth_url}

@app.get("/api/youtube/callback")
async def youtube_callback(code: str = None, error: str = None):
    """YouTube OAuth回调处理"""
    from services import youtube_service
    
    if error:
        return {"success": False, "error": f"授权失败: {error}"}
    
    if not code:
        return {"success": False, "error": "未获取到授权码"}
    
    success, message = youtube_service.complete_auth(code)
    
    if success:
        return {
            "success": True,
            "message": message,
            "html": f"""
            <div style="text-align:center;padding:50px;font-family:Arial,sans-serif;">
                <h2 style="color:#28a745;">✅ YouTube授权成功！</h2>
                <p>现在可以上传视频到YouTube了</p>
                <p><a href="/" style="padding:10px 20px;background:#0066cc;color:#fff;text-decoration:none;border-radius:5px;">返回首页</a></p>
            </div>
            """
        }
    else:
        return {"success": False, "error": message}

@app.get("/api/youtube/channel")
async def youtube_get_channel():
    """获取YouTube频道信息"""
    from services import youtube_service
    info = youtube_service.get_channel_info()
    return info

@app.get("/api/youtube/videos")
async def youtube_list_videos(limit: int = 10):
    """列出最近上传的视频"""
    from services import youtube_service
    videos = youtube_service.list_videos(page_size=limit)
    return videos

@app.post("/api/youtube/upload")
async def youtube_upload_video(
    video_path: str = None,
    title: str = None,
    description: str = None,
    keywords: list = None,
    category_id: str = "22",
    privacy_status: str = "public"
):
    """上传视频到YouTube"""
    from services import youtube_service
    
    if not video_path:
        return {"success": False, "error": "缺少视频路径"}
    
    if not title:
        return {"success": False, "error": "缺少标题"}
    
    result = youtube_service.upload_video(
        video_path=video_path,
        title=title,
        description=description or "",
        keywords=keywords or [],
        category_id=category_id,
        privacy_status=privacy_status
    )
    
    return result

@app.post("/api/youtube/publish-daily")
async def youtube_publish_daily():
    """自动发布今日YouTube视频"""
    from datetime import datetime, timezone, timedelta
    from pathlib import Path
    import json
    
    # 获取今日日期
    TZ = timezone(timedelta(hours=8))
    TODAY = datetime.now(TZ).strftime("%Y%m%d")
    
    # 视频路径
    video_path = f"/root/SOM/content/videos/{TODAY}/final.mp4"
    if not Path(video_path).exists():
        return {"success": False, "error": f"今日视频不存在: {video_path}"}
    
    # 读取文章信息
    article_dir = Path(f"/root/SOM/content/articles/{TODAY}")
    topic_file = article_dir / "topic.json"
    
    if topic_file.exists():
        with open(topic_file) as f:
            topic = json.load(f)
        title = topic.get("title_cn", f"SOM松麦 - {TODAY}")
        description = topic.get("description", "")
        keywords = topic.get("key_points", [])[:5]
    else:
        title = f"SOM松麦 - {TODAY}"
        description = "每日养生科普视频"
        keywords = ["养生", "中医", "健康"]
    
    # 上传视频
    from services import youtube_service
    result = youtube_service.upload_video(
        video_path=video_path,
        title=title,
        description=description,
        keywords=keywords,
        privacy_status="public"
    )
    
    # 更新发布日志
    publish_log = {
        "date": TODAY,
        "title": title,
        "video_path": video_path,
        "published_at": datetime.now(TZ).isoformat(),
        "result": result
    }
    logs_dir = Path("/root/SOM/content/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    with open(logs_dir / f"{TODAY}_youtube.json", "w") as f:
        json.dump(publish_log, f, ensure_ascii=False, indent=2)
    
    return result

# ========== 页面路由（支持微信菜单直接跳转）==========

@app.get("/products")
@app.get("/yangshenggu")
@app.get("/profile")
async def serve_page():
    """返回SPA页面，前端根据URL路径初始化对应tab"""
    from fastapi.responses import HTMLResponse
    with open("/root/SOM/web/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


