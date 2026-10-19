"""
SOM 松麦 - 后端服务入口
小麦SOM = Qwen3.5 2B + RAG知识库
"""
import json
import asyncio
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

from fastapi import FastAPI, HTTPException, Query, Response, Request
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
    images: object = None  # 2026-10-19 小蕊加: 多图, 前端传 JSON 数组(list), 也可传 JSON 字符串串, 统一落库成 JSON 串

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
            images TEXT,
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

    # 2026-10-19 小蕊加: 旧库 product_favorites 没有 images 列时自动 ALTER
    try:
        _cols = [r[1] for r in cursor.execute('PRAGMA table_info(product_favorites)').fetchall()]
        if 'images' not in _cols:
            cursor.execute('ALTER TABLE product_favorites ADD COLUMN images TEXT')
            print('[init] product_favorites 已加 images 列')
    except Exception as _e:
        print('[init] product_favorites images 列处理:', _e)
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

# 2026-10-19 分享图去重缓存: {content_md5: (png_bytes, ts, share_url)}, 60s 内同内容秒回
_share_image_dedup = {}
# 2026-10-20 中华反馈「分享图加载慢/出不来」: 去重表原只在内存, 服务重启即清空,
# 每次都要 Pillow 重新渲染(3~6s)+生成 300~450KB 长图, 微信再下载几秒 → 体感很慢。
# 磁盘持久化: 同内容 10min 内(重启也不丢)直接复用已存好的 jpg 直链文件, 秒级返回。
_SHARE_DEDUP_FILE = os.path.join(os.path.dirname(__file__) or '.', 'data', 'share_dedup.json')

def _dedup_load():
    import json as _json
    try:
        if os.path.isfile(_SHARE_DEDUP_FILE):
            with open(_SHARE_DEDUP_FILE, encoding='utf-8') as _fh:
                for _k, (_ts, _url) in _json.load(_fh).items():
                    _share_image_dedup[_k] = (b'', _ts, _url)  # 重启后只留 ts+url, 命中时直读文件
    except Exception:
        pass

def _dedup_save():
    import json as _json
    try:
        os.makedirs(os.path.dirname(_SHARE_DEDUP_FILE), exist_ok=True)
        with open(_SHARE_DEDUP_FILE, 'w', encoding='utf-8') as _fh:
            _json.dump({k: [v[1], v[2]] for k, v in _share_image_dedup.items() if isinstance(v, tuple)}, _fh)
    except Exception:
        pass

_dedup_load()

# ========== API 路由 ==========

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "SOM松麦后端", "version": "1.1.1"}

# ========== 小麦SOM 对话接口 ==========

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    from services.chat_engine import chat_with_llm

    # 2026-10-16 小蕊修: 阻塞工作(LLM+商品搜索+存档)放线程池, 不卡事件循环
    # (同 chat_vision 的"短路"问题, 见 _chat_vision_work 注释)
    return await asyncio.to_thread(_chat_work, request, chat_with_llm)

def _chat_work(request, chat_with_llm):
    # 加载当前会话的历史对话（传给LLM，让小麦记住上下文）
    history = []
    if request.session_id:
        try:
            conn = get_user_db()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT user_message, assistant_reply, created_at FROM chat_history WHERE session_id = ? ORDER BY created_at DESC LIMIT 10',
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
            result["reply"][:4000],
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
                advice=result["reply"][:4000],
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


@app.api_route("/api/share/content-image", methods=["GET", "POST"])
async def share_content_image(request: Request):
    """辨证内容分享图 v3: 服务端 Pillow 渲染 PNG(帽子形象图+文案+底部码不压字)
    2026-10-16 小蕊补(中华反馈「分享图不能用微信分享」): 额外把 PNG 存到
    data/share_tmp/ 并返回 X-Share-Url(http 直链)——微信 WebView 里 http 图片
    才能稳定长按保存, data URL 长按不一定出保存菜单。
    2026-10-19 小蕊补(中华反馈分享图生成失败): 加 GET 兜底——旧版 js(手机微信缓存)
    用 GET 调本接口拿到 405 直接挂掉, 现 GET/POST 都支持, 新旧版前端都能出图。
    GET 参数: text=辨证文案(必填), site_url=站点URL(可选)。"""
    if request.method == "GET":
        text = (request.query_params.get("text") or "养生参考").strip()
        site_url = request.query_params.get("site_url") or ""
        site_url = site_url or (os.environ.get("SOM_SITE_URL", "").strip() or "https://som.top")
    else:
        body = await request.json()
        text = (body.get("text") or "养生参考").strip()
        site_url = body.get("site_url") or ""
        site_url = site_url or (os.environ.get("SOM_SITE_URL", "").strip() or "https://som.top")
    from services.share_image import render_content_share_image
    # 2026-10-19 中华反馈「分享图加载太慢, 根本加载不完」: 相同内容(前 2000 字)
    # 60s 内复用已渲染的 token, 不重复 Pillow 渲染(3~6s), 直接回已存在直链(秒级)。
    import hashlib
    _key = hashlib.md5(text[:2000].encode('utf-8')).hexdigest()
    _dedup = _share_image_dedup.get(_key)
    # 10min 磁盘去重: 命中且直链文件仍在 → 不重新渲染, 复用已存好的图
    _dedup_hit = bool(_dedup and (time_module.time() - _dedup[1]) < 600 and _dedup[2])
    if _dedup_hit:
        _tok = _dedup[2].rsplit('/', 1)[-1]
        _jf = os.path.join(_SHARE_TMP_DIR, _tok + '.jpg')
        _pf = os.path.join(_SHARE_TMP_DIR, _tok + '.png')
        _fp = _jf if os.path.isfile(_jf) else (_pf if os.path.isfile(_pf) else None)
        if not _fp:
            _dedup_hit = False
    if _dedup_hit:
        png = open(_fp, 'rb').read()
        share_url = _dedup[2]
    else:
        png = render_content_share_image(text, site_url)
        share_url = _save_share_tmp(png, 'content')
        _share_image_dedup[_key] = (png, time_module.time(), share_url)
        if len(_share_image_dedup) > 50:
            _oldest = sorted(_share_image_dedup.items(), key=lambda kv: kv[1][1])[:15]
            for k, _ in _oldest:
                _share_image_dedup.pop(k, None)
        _dedup_save()
    # 2026-10-19 中华反馈「分享图夹杂代码/加载不了」: 统一返回 JPEG(体积 2MB→43KB,
    # 微信按 Content-Type 解析, 之前存 jpg 但 Content-Type 写 image/png → 花屏出代码)。
    from PIL import Image
    import io as _io
    _im = Image.open(_io.BytesIO(png))
    if _im.mode in ('RGBA', 'P'):
        _im = _im.convert('RGB')
    _buf = _io.BytesIO()
    _im.save(_buf, 'JPEG', quality=75, optimize=True)
    _jpg = _buf.getvalue()
    return Response(content=_jpg, media_type="image/jpeg",
                    headers={"Content-Disposition": "inline; filename=som-share.jpg",
                             **({"X-Share-Url": share_url} if share_url else {})})


@app.api_route("/api/share/product-image", methods=["GET", "POST"])
async def share_product_image(request: Request):
    """商品分享图 v2: 全部商品图(最多4张) + 商品名 + 淘宝购买二维码, 头尾同辨证模板
    2026-10-19 小蕊补: 加 GET 兜底(旧版 js 缓存用 GET 调本接口会 405 失败),
    GET 参数: item_id/title/price/shop/image/images(逗号分隔多张图,可选)/buy_url/site_url。"""
    if request.method == "GET":
        q = request.query_params
        title = q.get("title") or "推荐商品"
        price = q.get("price") or ""
        shop = q.get("shop") or ""
        image = q.get("image") or ""
        images = [x for x in (q.get("images") or "").split(",") if x]
        buy_url = q.get("buy_url") or ("https://s.click.taobao.com/" + q["item_id"] if q.get("item_id") else "https://item.taobao.com/")
        site_url = q.get("site_url") or ""
        site_url = site_url or (os.environ.get("SOM_SITE_URL", "").strip() or "https://som.top")
    else:
        body = await request.json()
        title = body.get("title") or "推荐商品"
        price = body.get("price") or ""
        shop = body.get("shop") or ""
        image = body.get("image") or ""
        images = list(body.get("images") or [])
        buy_url = body.get("buy_url") or ""
        site_url = body.get("site_url") or ""
        site_url = site_url or (os.environ.get("SOM_SITE_URL", "").strip() or "https://som.top")
    from services.share_image import render_product_share_image
    pics = [x for x in images if x]
    if image and image not in pics:
        pics.insert(0, image)
    # 2026-10-20 商品分享图磁盘去重: 同商品+同图 10min 内秒级复用, 不重复渲染+下载商品图
    import hashlib as _hl2
    _pkey = _hl2.md5(('p|' + title + '|' + price + '|' + '|'.join(pics) + '|' + (buy_url or '')).encode('utf-8')).hexdigest()
    _pdedup = _share_image_dedup.get(_pkey)
    _phit = bool(_pdedup and (time_module.time() - _pdedup[1]) < 600 and _pdedup[2])
    if _phit:
        _tok = _pdedup[2].rsplit('/', 1)[-1]
        _jf = os.path.join(_SHARE_TMP_DIR, _tok + '.jpg')
        _pf = os.path.join(_SHARE_TMP_DIR, _tok + '.png')
        _fp = _jf if os.path.isfile(_jf) else (_pf if os.path.isfile(_pf) else None)
        if not _fp:
            _phit = False
    if _phit:
        png = open(_fp, 'rb').read()
        share_url = _pdedup[2]
    else:
        png = render_product_share_image(
            title=title, price=price, shop=shop,
            images=pics, buy_url=buy_url or "https://item.taobao.com/",
            site_url=site_url)
        share_url = _save_share_tmp(png, 'product')
        _share_image_dedup[_pkey] = (png, time_module.time(), share_url)
        if len(_share_image_dedup) > 50:
            _oldest = sorted(_share_image_dedup.items(), key=lambda kv: kv[1][1])[:15]
            for k, _ in _oldest:
                _share_image_dedup.pop(k, None)
        _dedup_save()
    # 2026-10-19 商品分享图同样改 JPEG, 体积从 ~1.4MB 砍到 ~150KB
    from PIL import Image
    import io as _io
    _im = Image.open(_io.BytesIO(png))
    if _im.mode in ('RGBA', 'P'):
        _im = _im.convert('RGB')
    _buf = _io.BytesIO()
    _im.save(_buf, 'JPEG', quality=75, optimize=True)
    _jpg = _buf.getvalue()
    return Response(content=_jpg, media_type="image/jpeg",
                    headers={"Content-Disposition": "inline; filename=som-product.jpg",
                             **({"X-Share-Url": share_url} if share_url else {})})


# ========== 2026-10-16 小蕊加: 分享图 http 直链(微信内长按保存→手动分享) ==========
# 注意: os/time/uuid 顶部已 import(time 以 time_module 别名), 不用重复 import

_SHARE_TMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "share_tmp")


def _save_share_tmp(png: bytes, kind: str) -> str:
    """PNG 存到 data/share_tmp/{token}.png, 返回 /api/share/file/{token} 相对直链。
    顺带清 24h 前的旧文件。失败不影响分享图本身(返回'')。"""
    try:
        os.makedirs(_SHARE_TMP_DIR, exist_ok=True)
        # 2026-10-19 中华反馈「分享图加载不完/太慢」根治: PNG 不压缩, 商品图+二维码
        # 一张 1.4~2MB, 微信里下载要十几秒。转 JPEG 质量 82, 体积砍到 ~250KB(快 5~8 倍)。
        # 旧 .png 文件继续保留可读(下面 share_file 同时查 .png/.jpg), 新图一律 .jpg。
        from PIL import Image
        import io as _io
        _im = Image.open(_io.BytesIO(png))
        if _im.mode in ('RGBA', 'P'):
            _im = _im.convert('RGB')
        _buf = _io.BytesIO()
        _im.save(_buf, 'JPEG', quality=75, optimize=True)
        _jpg = _buf.getvalue()
        now = time_module.time()
        for f in os.listdir(_SHARE_TMP_DIR):
            p = os.path.join(_SHARE_TMP_DIR, f)
            try:
                if os.path.isfile(p) and now - os.path.getmtime(p) > 86400:
                    os.remove(p)
            except Exception:
                pass
        token = uuid.uuid4().hex
        with open(os.path.join(_SHARE_TMP_DIR, token + '.jpg'), 'wb') as fh:
            fh.write(_jpg)
        return "/api/share/file/" + token
    except Exception:
        return ""


@app.api_route("/api/share/file/{token}", methods=["GET", "HEAD"])
# 2026-10-20 中华反馈「商品分享图加载识别或生成失败」: 微信 <img>/长按识别流程
# 会先发 HEAD 探活, 原来只声明 @app.get → HEAD 405 被拒 → 识别管线放弃,
# 只下了几 KB 就断(nginx 日志实锤 8192/40960 字节)。加 HEAD + 短缓存。
async def share_file(token: str):
    """分享图 http 直链: 微信内 <img src> 指这里, 长按→保存图片→发微信好友。"""
    import re as _re
    if not _re.fullmatch(r'[a-f0-9]{32}', token):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="bad token")
    p = os.path.join(_SHARE_TMP_DIR, token + '.jpg')
    if not os.path.isfile(p):
        p = os.path.join(_SHARE_TMP_DIR, token + '.png')
    if not os.path.isfile(p):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="not found")
    with open(p, 'rb') as fh:
        data = fh.read()
    # 2026-10-19 中华反馈「分享图夹杂代码/加载不了」: 微信 WebView 按 Content-Type 解析,
    # 我 m 版改存 .jpg 但这里还写死 image/png → JPEG 字节被当 PNG 解码 → 花屏/出代码。
    # 按真实文件后缀返回 media_type, 新图 .jpg=image/jpeg, 旧图 .png=image/png。
    _is_jpg = p.endswith('.jpg')
    return Response(content=data, media_type="image/jpeg" if _is_jpg else "image/png",
                    headers={
                        "Content-Disposition": "inline; filename=som-share." + ("jpg" if _is_jpg else "png"),
                        "Cache-Control": "public, max-age=604800",  # 7天: token 本身就是随机指纹, 可强缓存
                    })


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
    # 2026-10-20 中华反馈「连续签到8天变1天」: streak 改从历史表 checkin_daily 往回连续数
    # (每天签到达一条日期, 永不因 last_date 单字段误判丢连续)。close 前查完。
    _seen = set()
    _streak = 0
    if row:
        _seen = {r[0] for r in cursor.execute(
            'SELECT check_date FROM checkin_daily WHERE user_id = ?', (user_id,)).fetchall()}
        if row['last_date'] in _seen:
            _streak = 1
            _d = datetime.strptime(row['last_date'], '%Y-%m-%d')
            while True:
                _d -= timedelta(days=1)
                if _d.strftime('%Y-%m-%d') not in _seen:
                    break
                _streak += 1
                if _streak > 3650:
                    break
    conn.close()

    if row:
        return {
            "checked_in_today": row['last_date'] == today,
            "total_points": row['total_points'],
            "streak": _streak,
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
        total_points += 10
    else:
        total_points = 10

    # 2026-10-20 中华反馈「连续签到8天变1天」: 旧算法只比 last_date 是否=昨天,
    # 中间漏一天/时区边界误判就把 streak 归1, 累积连续天数全丢。
    # 现改为: 写签到历史表 checkin_daily(每日一条), streak 从今天往回连续数, 永不丢。
    cursor.execute('INSERT OR IGNORE INTO checkin_daily (user_id, check_date) VALUES (?, ?)',
                   (request.user_id, today))
    streak = 1
    cur2 = cursor.execute('SELECT check_date FROM checkin_daily WHERE user_id = ? ORDER BY check_date DESC',
                          (request.user_id,))
    _seen = {r[0] for r in cur2.fetchall()}
    _d = datetime.strptime(today, '%Y-%m-%d')
    while True:
        _d -= timedelta(days=1)
        if _d.strftime('%Y-%m-%d') not in _seen:
            break
        streak += 1
        if streak > 3650:
            break

    if row:
        cursor.execute('UPDATE checkin_records SET last_date = ?, total_points = ?, streak = ? WHERE user_id = ?',
                       (today, total_points, streak, request.user_id))
    else:
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
async def get_favorites(request: Request, user_id: str, limit: int = 50, page: int = 1, page_size: int = 10):
    conn = get_user_db()
    cursor = conn.cursor()
    # 2026-10-15 我的收藏改双分类区独立分页: 优先 page/page_size(偏移分页), 兼容旧 limit
    # 2026-10-19 根治: 旧条件 `page>1 or page_size!=10` 在默认参数下恒为 False,
    # 前端正常传 page=1&page_size=10 也走旧 limit 分支 → 响应缺 total_pages,
    # 前端 hasMore 恒 false, 「加载更多」按钮永不显示, 分页形同虚设。
    # 现改为: 调用方显式带了 page/page_size 查询参数才走旧 limit 兼容分支,
    # 否则一律分页分支(返回 total_pages)。显式判断用 request.query_params,
    # 因为 FastAPI 默认值让 page/page_size 变量本身无法区分"显式传了"还是"默认"。
    _qp = dict(request.query_params)
    if "page" not in _qp and "page_size" not in _qp:
        # 旧调用方(只带 limit, 不分页): 保持原行为, 不破坏任何现存调用
        cursor.execute('SELECT * FROM product_favorites WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
                       (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        out = []
        for r in rows:
            d = dict(r); d['image'] = _clean_fav_image(d.get('image')); out.append(d)
        return {"total": len(out), "favorites": out}
    total = cursor.execute('SELECT COUNT(*) FROM product_favorites WHERE user_id=?', (user_id,)).fetchone()[0]
    rows = cursor.execute(
        'SELECT * FROM product_favorites WHERE user_id=? ORDER BY created_at DESC LIMIT ? OFFSET ?',
        (user_id, page_size, (page - 1) * page_size)).fetchall()
    conn.close()
    favs = []
    for r in rows:
        d = dict(r); d['image'] = _clean_fav_image(d.get('image')); favs.append(d)
    return {"total": total, "page": page, "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "favorites": favs}

def _clean_images(images):
    """2026-10-19 小蕊加: 把前端传来的 images 统一成 JSON 数组串存单列。
    兼容: list[URL] / JSON 数组字符串 / 单个 URL 串 / 空。
    非 http URL 全部过滤掉, 避免脏数据进库。"""
    if images is None:
        return ""
    if isinstance(images, list):
        lst = images
    elif isinstance(images, str):
        s = images.strip()
        if not s:
            return ""
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                lst = parsed
            else:
                lst = [s]
        except Exception:
            lst = [s]
    else:
        return ""
    clean = [u for u in lst if isinstance(u, str) and u.strip().startswith("http")]
    # 去重保序
    seen = set(); out = []
    for u in clean:
        u = u.strip()
        if u in seen: continue
        seen.add(u); out.append(u)
    return json.dumps(out, ensure_ascii=False) if out else ""

def _clean_fav_image(image):
    """2026-10-16 小蕊修: 收藏 image 字段历史上被写脏过——
    前端某版本把整个 images 数组 JSON 串(带转义引号, 逗号)直接存进 image,
    导致收藏卡片 <img src> 加载失败。
    清洗: 能解析成 JSON 数组取第一张; 含多URL取第一段; 单URL原样返回。
    2026-10-18 中华要求强化: 写路径也过一遍清洗(源头堵死),
    反复截断到只留第一个 http URL, 尾部残留引号/逗号/反斜杠全剥掉。"""
    s = (image or "").strip()
    if not s:
        return ""
    # 1) JSON 数组串 → 取第一张
    if s.startswith("["):
        try:
            arr = json.loads(s)
            if isinstance(arr, list) and arr:
                s = str(arr[0]).strip()
        except Exception:
            pass
    # 2) 反复截断: 只要段里还有第二个 http 起点(下一个 URL), 就截到它前面
    for _ in range(30):
        _i = s.find("http")
        if _i > 0:
            s = s[_i:]
        _next = s.find("http", 4)
        if _next < 0:
            break
        s = s[:_next].rstrip().rstrip('",').strip()
        if not s.startswith("http"):
            break
    # 3) 尾部残留引号/逗号/反斜杠剥掉
    while s and s[-1] in '\"",':
        s = s[:-1].rstrip()
    return s

@app.post("/api/favorites/add")
async def add_favorite(request: FavoriteAddRequest):
    conn = get_user_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO product_favorites
            (user_id, item_id, title, price, image, url, platform, shop_name, images)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (request.user_id, request.item_id, request.title, request.price,
              _clean_fav_image(request.image), request.url, request.platform, request.shop_name,
              _clean_images(request.images)))
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


def _chat_vision_work(request, image_list):
    """chat_vision 阻塞工作(LLM调用+人脸+商品搜索+存档), 由 asyncio.to_thread 调起。
    2026-10-16 小蕊加。返回与原 chat_vision 相同结构。
    2026-10-17 中华铁律: 辨证总耗时不超过90秒。全流程 80s deadline——
    LLM最多60s + 人脸~3s + 商品搜索最多25s, 超预算就跳过商品搜索直接返回辨证。
    """
    import time as _time
    _vision_deadline = _time.time() + 80  # 全流程硬预算(留10s余量给存档/序列化/nginx)
    from services import llm_router, rag
    # 图片格式由 llm_router 按服务商自动处理：
    # sensenova 直接收 base64（无需下载，最稳），agnes 自动转公网URL

    # 根据图片数量调整提示词
    if len(image_list) == 1:
        system_prompt = """你是小麦SOM，一位经验丰富的老中医，擅长望闻问切四诊合参，看的是【人】不是【部位清单】。

【辨证原则——像真正的老中医一样，看见什么辨什么，绝不局限于固定几项】
1. 望（照片里一切看得清的异常都要看, 清单只是提示不是边界, 看见任何异常都要写出来并辨证）：
   - 舌头：舌色（淡红/淡白/红/紫暗/舌尖红）、舌苔（薄白/白腻/黄腻/黄燥/少苔/无苔/花剥/剥苔）、舌形（胖大/瘦薄/齿痕/裂纹/点刺/瘀斑）、舌下络脉（紫暗/迂曲, 拍舌下照时看）
   - 眼睛：眼神（有神/疲惫/散漫）、眼白（清白/发黄/血丝）、眼袋、眼睑（浮肿/色暗）、瞳孔色泽、老年黄斑样浑浊
   - 面色：红润/萎黄/苍白/晦暗/潮红、光泽、油光、斑疹（老年斑/肝斑/痤疮/血痣/痣/色素斑/痘印）
   - 唇：唇色（淡白/淡红/深红/紫暗）、唇周（干燥/脱屑/口角炎）
   - 皮肤：润燥、皮疹（湿疹/荨麻疹/瘙痒）、脓疱/粉刺、血痣、老年斑、面色斑点
   - 头发：黑/黄/白/灰、油腻、干燥、稀疏、早白（30岁前白发）
   - 颈部/体态：消瘦/肥胖、颈纹、皮肤松弛
   - 患处/其他任何照片里看得清的身体信息
   看得清就都要说; 看不清的部位如实说看不清, 严禁编造。
2. 问（问诊）：用户文字里描述的症状/不适（失眠、疲倦、口苦、大便、月经、出汗、怕冷怕热、腰膝、情绪等）逐条纳入，与望诊一起综合推理辨证。
   【问诊症状必入三方案铁律——2026-10-20 中华要求】问诊里报出的每个症状/不适，都必须跟望诊一样参与辨证、落到主证/兼证上，最终并入三个食疗方案（方案一主证/方案二兼证/方案三固本）里对应调理；严禁把某个症状单独甩到回复末尾"只给建议不给配方"。若某症状需要单独方向，也必须并入三方案之一（或替换为有配方的方案），不允许"只提一句建议、不给配方"。
3. 照片证据 + 文字症状 + 该用户【全部历史照片、全部历史辨证、全部历史对话】交叉印证（提示词里会给, 必须逐条对照; 没有记录就如实说没有, 严禁编造）。
4. 【见症即诊铁律——诊断不限于九种体质】发现什么异常就诊断什么, 不套体质: 皮肤老年斑/血痣/痘→辨血瘀/湿热; 眼白发黄→肝胆湿热; 头发早白→肝肾不足; 夜尿多→肾阳虚; 口苦→肝胆; 失眠→心脾两虚/阴虚火旺; 便秘→肠燥; 便溏→脾虚泄泻; 潮热盗汗→阴虚内热; 乏力懒言→气虚; 怕冷→阳虚; 怕热→阴虚火旺; 痰多→痰湿; 胁痛→肝郁; 腰酸→肾虚; 头晕→肝阳上亢/气血亏虚……诊断要覆盖: 所有症状+病状+可能疾病+医治方向(食疗/起居/穴位/预防/生活调摄)+必要就医提醒, 像真正给病人治病的老年中医, 不是只填九体质模板。
5. 【章节结构铁律——中华 2026-10-20 定稿，必须按此顺序输出，不得增删章节】
   回复正文只含以下章节（用小节标题 ## 标注），顺序固定：
   ## 一、望诊：把照片里看得清的各部位（舌/眼/面/唇/皮肤/发/颈/患处）画一张【规范表格】，表头『部位 | 本次表现』，一眼看清，简单。
   ## 二、问诊：把闻诊(气味/声音)与切诊(脉象/按触)都折算成问诊文字描述纳入；画一张【问诊·现在与历史对照表】，固定三行数据：
       第一行『现在』：本次用户自述/报出的症状（可多个，顿号连写）；
       第二行『历史』：该用户历史上报过的症状（来自全部历史对话/辨证记录，可多个，带日期，如"腹胀(2026-10-13)"）；
       第三行『变化』：逐条判现在 vs 历史——好了写 ✅已好转/消失了，没好写 ⚠️仍在/反复了，新发写 ➕新增；表头『问诊项 | 现在 | 历史 | 变化』。
       这样"现在不腹胀了、但历史有腹胀"一眼就知道好了没、会不会复发。
   ## 三、综合辨证：把望诊(照片)+问诊(现在与历史)一起综合推理，给出主证+兼证+可能疾病+医治方向(食疗/起居/穴位/预防/生活调摄)+必要就医提醒。望与问的"现在"和"历史"证据都要写进辨证依据，说明每个证候对应哪条照片/文字/历史。
   ## 四、三个食疗方案（侧重点不同）：方案一主证/方案二兼证/方案三固本，各独立成段+配方+做法。
   ## 五、症状-方案映射表：markdown 表格，表头『症状 | 落在哪个方案 | 方案里对应食材』，把"现在+历史"每个主诉症状逐行对应到三方案之一。
   后面再叮嘱/总结即可。严禁把问诊/历史症状单独甩到末尾只给建议不给配方。
6. 【方案侧重铁律——中华 2026-10-17c 要求，违反则不合格】必须给满3个食疗方，且三者侧重点【必须不同、不得雷同、不得换汤不换药】：
   - 方案一：针对本次辨出的【主证】（最突出的证候），标题写"方案一：XXX（主证·XX证）"
   - 方案二：针对【兼证/次要证候】（与方案一完全不同的调理方向，食材组合必须与方案一明显不同，**方案二里不得出现方案一里的主药**），标题写"方案二：XXX（兼证·XX证）"
   - 方案三：做【整体固本/防复发】（长期调理方向，如健脾固本、补肾、安神等），标题写"方案三：XXX（固本·XX方向）"
   每个方子独立成段，配方形式、用量具体到单位。
   【自查】输出前默念：方案二和方案一的核心主药有没有重复？有就换方向重写。

【食疗方硬性要求——中华 2026-10-15 铁律，违反则不合格】
- 必须给满3个食疗方案（方案一/方案二/方案三，侧重点不同：如一个健脾、一个养阴、一个祛湿），每个方子都独立成段、独立配方+做法。
- 食疗方必须写成"配方"：每个食材后面紧跟数量单位，如"黄芪15g、乌鸡半只、红枣5枚、枸杞10g、山药20g"，绝不允许只写食材名不写用量。
- 每个方子至少给 5~8 味食材，用量要具体到克/枚/朵/只/片，不要用"适量""少许"含糊带过（整方可以有一味写"适量"，但不能全部模糊）。
- 每个方子后面必须跟"做法"（怎么煮/怎么吃、吃多久）。
- 【2026-10-17b 排版铁律】每个方案内部严格分两段，中间空一行：
  第一段：固定以"**配方：**"开头（这两个字加粗，后面紧跟中文冒号），食材+用量顿号连写成一行，这一行末尾必须加句号。
  空一行。
  第二段：固定以"**做法：**"开头（这两个字加粗，后面紧跟中文冒号），写怎么煮/怎么吃/吃多久。
  配方和做法严禁混在同一行同一句里。示例：
  **配方：** 黄芪15g、西洋参10g、麦冬15g、玉竹15g、百合15g、枸杞10g、山药20g、乌鸡半只、红枣5枚、生姜3片。
  **做法：** 乌鸡切块焯水去腥，所有药材洗净，与乌鸡、红枣、生姜一同放入砂锅，加清水约1500ml，大火烧开后转小火慢炖1.5小时，加少许盐调味即可。
- 【2026-10-18m 排版铁律】正文到三个食疗方 + 总结提醒结束即可【到此为止】，不要在正文里写"以上为养生文化参考""以上内容由人工智能生成""🛒推荐"这类尾部内容——服务端会统一在结尾追加固定的三段尾部（养生参考 → 🛒推荐 → AI声明），你正文里再写一遍就会重复。
- 目的：系统会按你列的食材自动匹配有机商品，你食材列得越全、用量越具体，下面商品卡片越丰富（每个食材出2款），别偷懒只给两三种食材。

注意：
- 用通俗易懂的语言，不堆砌术语
- 【排版铁律】整篇回复分段清晰：每个大块之间空一行即可，不要使用"---"分隔线、不要使用"==="等装饰符号；小节标题用"##"或加粗即可。
- 【表格铁律——中华 2026-10-20 定稿】三处固定画规范 markdown 表格(表头行 + 一行 |---|---| 分隔线 + 数据行，列数一致，单格≤15字)：
   ① 望诊表『部位 | 本次表现』；
   ② 问诊·现在与历史对照表『问诊项 | 现在 | 历史 | 变化』——现在/历史可各含多个症状(顿号连写)，变化行用 ✅已好转/⚠️仍在/➕新增 小图标；
   ③ 症状-方案映射表『症状 | 落在哪个方案 | 方案里对应食材』。
   正文叙述(综合辨证/食疗方案/叮嘱)仍用段落，不硬塞表格。
- 结尾必须加：以上为养生文化参考，不构成医疗诊断，身体不适请及时就医
- 如果图片看不清，礼貌说明并建议重新拍摄
- 最末尾必须追加一行固定JSON块(供服务端自动存档, 用户看不到): 体质用中医九分法(平和质/气虚质/阳虚质/阴虚质/痰湿质/湿热质/血瘀质/特禀质/过敏质), 最多3个顿号连接; 没有明显体质就留空字符串。格式:
tizhi_data: {"tizhi":"气虚质、阴虚质","zhengxing":"脾虚"}"""
    else:
        system_prompt = f"""你是小麦SOM，一位经验丰富的老中医，擅长望闻问切四诊合参，看的是【人】不是【部位清单】。
用户发来了{len(image_list)}张照片（可能包含舌苔、面色、眼睛、皮肤、患处等不同部位）。

【辨证原则——像真正的老中医一样，看见什么辨什么，绝不局限于固定几项】
1. 望：逐张分析每张照片里【一切看得清的异常, 清单只是提示不是边界, 看见任何异常都要写出来并辨证】——舌头(舌色/舌苔/舌形/舌下络脉)、眼睛(眼神/眼白发黄/眼袋/眼睑/老年黄斑)、面色(红润/萎黄/苍白/晦暗/斑疹:老年斑/肝斑/痤疮/血痣/痘印)、唇(唇色/唇周)、皮肤(润燥/皮疹/脓疱/血痣/老年斑)、头发(黑/黄/白/油腻/稀疏/早白)、颈部体态、患处……看得清就都要说, 看不清如实说明, 严禁编造。
2. 问（问诊）：用户文字里描述的症状/不适逐条纳入，与望诊一起综合推理辨证。
   【问诊症状必入三方案铁律——2026-10-20 中华要求】问诊里报出的每个症状/不适，都必须跟望诊一样参与辨证、落到主证/兼证上，最终并入三个食疗方案（方案一主证/方案二兼证/方案三固本）里对应调理；严禁把某个症状单独甩到回复末尾"只给建议不给配方"。若某症状需要单独方向，也必须并入三方案之一（或替换为有配方的方案），不允许"只提一句建议、不给配方"。
3. 综合所有照片 + 文字症状 + 该用户【全部历史照片、全部历史辨证、全部历史对话】交叉印证（提示词里会给, 必须逐条对照; 没有记录就如实说没有, 严禁编造）。
4. 【见症即诊铁律——诊断不限于九种体质】发现什么异常就诊断什么, 不套体质: 皮肤老年斑/血痣/痘→辨血瘀/湿热; 眼白发黄→肝胆湿热; 头发早白→肝肾不足; 夜尿多→肾阳虚; 口苦→肝胆; 失眠→心脾两虚/阴虚火旺; 便秘→肠燥; 便溏→脾虚泄泻; 潮热盗汗→阴虚内热; 乏力懒言→气虚; 怕冷→阳虚; 怕热→阴虚火旺; 痰多→痰湿; 胁痛→肝郁; 腰酸→肾虚; 头晕→肝阳上亢/气血亏虚……诊断要覆盖: 所有症状+病状+可能疾病+医治方向(食疗/起居/穴位/预防/生活调摄)+必要就医提醒, 像真正给病人治病的老年中医, 不是只填九体质模板。
5. 【章节结构铁律——中华 2026-10-20 定稿，必须按此顺序输出，不得增删章节】
   回复正文只含以下章节（用小节标题 ## 标注），顺序固定：
   ## 一、望诊：逐张把照片里看得清的各部位（舌/眼/面/唇/皮肤/发/颈/患处）画一张【规范表格】，表头『部位 | 本次表现』，一眼看清，简单。
   ## 二、问诊：把闻诊(气味/声音)与切诊(脉象/按触)都折算成问诊文字描述纳入；画一张【问诊·现在与历史对照表】，固定三行数据：
       第一行『现在』：本次用户自述/报出的症状（可多个，顿号连写）；
       第二行『历史』：该用户历史上报过的症状（来自全部历史对话/辨证记录，可多个，带日期，如"腹胀(2026-10-13)"）；
       第三行『变化』：逐条判现在 vs 历史——好了写 ✅已好转/消失了，没好写 ⚠️仍在/反复了，新发写 ➕新增；表头『问诊项 | 现在 | 历史 | 变化』。
       这样"现在不腹胀了、但历史有腹胀"一眼就知道好了没、会不会复发。
   ## 三、综合辨证：把望诊(照片)+问诊(现在与历史)一起综合推理，给出主证+兼证+可能疾病+医治方向(食疗/起居/穴位/预防/生活调摄)+必要就医提醒。望与问的"现在"和"历史"证据都要写进辨证依据，说明每个证候对应哪条照片/文字/历史。
   ## 四、三个食疗方案（侧重点不同）：方案一主证/方案二兼证/方案三固本，各独立成段+配方+做法。
   ## 五、症状-方案映射表：markdown 表格，表头『症状 | 落在哪个方案 | 方案里对应食材』，把"现在+历史"每个主诉症状逐行对应到三方案之一。
   后面再叮嘱/总结即可。严禁把问诊/历史症状单独甩到末尾只给建议不给配方。
6. 【方案侧重铁律——中华 2026-10-17c 要求，违反则不合格】必须给满3个食疗方，且三者侧重点【必须不同、不得雷同、不得换汤不换药】：
   - 方案一：针对【主证】（最突出的证候），标题写"方案一：XXX（主证·XX证）"
   - 方案二：针对【兼证/次要证候】（与方案一完全不同的调理方向，食材组合必须与方案一明显不同，**方案二里不得出现方案一里的主药**），标题写"方案二：XXX（兼证·XX证）"
   - 方案三：做【整体固本/防复发】（长期调理方向），标题写"方案三：XXX（固本·XX方向）"
   每个方子独立成段 + 做法，配方形式、用量具体到单位。
   【自查】输出前默念：方案二和方案一的核心主药有没有重复？有就换方向重写。

【食疗方硬性要求——中华 2026-10-15 铁律，违反则不合格】
- 必须给满3个食疗方案（方案一/方案二/方案三，侧重点不同：如一个健脾、一个养阴、一个祛湿），每个方子都独立成段、独立配方+做法。
- 食疗方必须写成"配方"：每个食材后面紧跟数量单位，如"黄芪15g、乌鸡半只、红枣5枚、枸杞10g、山药20g"，绝不允许只写食材名不写用量。
- 每个方子至少给 5~8 味食材，用量要具体到克/枚/朵/只/片，不要用"适量""少许"含糊带过（整方可以有一味写"适量"，但不能全部模糊）。
- 每个方子后面必须跟"做法"（怎么煮/怎么吃、吃多久）。
- 【2026-10-17b 排版铁律】每个方案内部严格分两段，中间空一行：
  第一段：固定以"**配方：**"开头（这两个字加粗，后面紧跟中文冒号），食材+用量顿号连写成一行，这一行末尾必须加句号。
  空一行。
  第二段：固定以"**做法：**"开头（这两个字加粗，后面紧跟中文冒号），写怎么煮/怎么吃/吃多久。
  配方和做法严禁混在同一行同一句里。示例：
  **配方：** 黄芪15g、西洋参10g、麦冬15g、玉竹15g、百合15g、枸杞10g、山药20g、乌鸡半只、红枣5枚、生姜3片。
  **做法：** 乌鸡切块焯水去腥，所有药材洗净，与乌鸡、红枣、生姜一同放入砂锅，加清水约1500ml，大火烧开后转小火慢炖1.5小时，加少许盐调味即可。
- 【2026-10-18m 排版铁律】正文到三个食疗方 + 总结提醒结束即可【到此为止】，不要在正文里写"以上为养生文化参考""以上内容由人工智能生成""🛒推荐"这类尾部内容——服务端会统一在结尾追加固定的三段尾部（养生参考 → 🛒推荐 → AI声明），你正文里再写一遍就会重复。
- 目的：系统会按你列的食材自动匹配有机商品，你食材列得越全、用量越具体，下面商品卡片越丰富（每个食材出2款），别偷懒只给两三种食材。
5. 推荐适合该体质的有机食材（与食疗方食材尽量重叠，让系统好匹配商品）

注意：
- 多维度综合分析比单张照片更准确，请充分利用多张图的信息
- 用通俗易懂的语言
- 【排版铁律】整篇回复分段清晰：每个大块之间空一行即可，不要使用"---"分隔线、不要使用"==="等装饰符号；小节标题用"##"或加粗即可。
- 【表格铁律——中华 2026-10-20 定稿】三处固定画规范 markdown 表格(表头行 + 一行 |---|---| 分隔线 + 数据行，列数一致，单格≤15字)：
   ① 望诊表『部位 | 本次表现』；
   ② 问诊·现在与历史对照表『问诊项 | 现在 | 历史 | 变化』——现在/历史可各含多个症状(顿号连写)，变化行用 ✅已好转/⚠️仍在/➕新增 小图标；
   ③ 症状-方案映射表『症状 | 落在哪个方案 | 方案里对应食材』。
   正文叙述(综合辨证/食疗方案/叮嘱)仍用段落，不硬塞表格。
- 结尾必须加：以上为养生文化参考，不构成医疗诊断，身体不适请及时就医
- 最末尾必须追加一行固定JSON块(供服务端自动存档, 用户看不到): 体质用中医九分法, 最多3个顿号连接; 没有明显体质就留空字符串。格式:
tizhi_data: {{"tizhi":"气虚质、阴虚质","zhengxing":"脾虚"}}"""

    # 加载会话历史（让小麦记住之前的对话上下文，包括之前的拍照扫描结果）
    # 2026-10-18n 升级(中华要求): 问诊要能读到用户给小麦说的所有历史对话——
    # 原来只读当前 session_id(前端每次刷新/换设备 session 就变, 读不到历史),
    # 现在跨会话全量拉该用户的历史对话(按 user_id), 让小麦真正掌握用户的完整病历/历史症状。
    history_context = ""
    if request.user_id and request.user_id != 'anonymous':
        try:
            conn = get_user_db()
            cursor = conn.cursor()
            cursor.execute(
                # 2026-10-20 中华: 症状块全量拉该用户全部历史对话(不限窗口)——vision 存档的用户消息
                # 是固定模板([图片辨证x1]...), 自述症状句全被顶掉, 靠 LIMIT 截窗口根本捞不到
                # (如 10-14 皮肤瘙痒在 100 条外)。全量拉 + 渲染端按症状词过滤, 只取有症状词的行。
                # 历史对话存档上限 ~200 轮, 全量拉内存可承受; 对话窗口(喂 prompt 的)仍截 30 轮。
                'SELECT user_message, assistant_reply, created_at FROM chat_history WHERE user_id = ? ORDER BY created_at ASC',
                (request.user_id,)
            )
            all_rows = cursor.fetchall()
            rows = all_rows[-30:]  # 喂 prompt 的对话窗口: 最近 30 轮(截断用)
            conn.close()
            if rows:
                # 2026-10-20 中华加固: 截断放宽 400→1500(用户自述症状句常超过400字, 之前被砍丢),
                # 且自述症状句用完整原文(不截断), 避免"皮肤瘙痒"被截断丢字。
                history_lines = []
                for row in reversed(rows):
                    _um_full = row['user_message'] or ''
                    _ar_full = row['assistant_reply'] or ''
                    # 含症状词的用户消息用全文(不截断), 普通消息截到1500
                    _um = _um_full if any(_kw in _um_full for _kw in ("痒", "痛", "症", "病", "不", "好")) else _um_full[:1500]
                    _ar = _ar_full[:1500]
                    history_lines.append(f"用户: {_um}")
                    history_lines.append(f"小麦: {_ar}")
                history_context = "\n".join(history_lines)
                system_prompt += (
                    f"\n\n【用户的全部历史对话记录（跨会话, 共 {len(rows)} 轮真实存档, 非假设）】\n{history_context}\n\n"
                    "【问诊铁律】上面的历史对话是这位用户和之前的小麦的真实往来(问诊记录)。"
                    "辨证时必须结合这些真实病历: 用户之前说过什么症状/不适/调理反馈, 小麦给过什么判断, 据此对照本次照片。"
                    "严禁编造历史对话里不存在的内容, 没有记录的就如实说没有记录。"
                )
                # 2026-10-20 中华加固②+③: 从历史对话里抽「用户自述症状」三分类高亮块单独喂给小麦,
                # 解决"之前说皮肤瘙痒现在没加了"——自述症状句在历史堆里容易被淹没, 单独高亮+三铁律。
                # 2026-10-20 中华三催: 去掉 try 静默吞错(原 try/except 把异常吞掉, 症状块偶发没喂进 prompt,
                # 小麦就漏了历史主诉症状/腹胀/瘙痒)。失败打印完整 traceback 并降级喂全量原文, 绝不静默。
                try:
                    from services.chat_engine import render_symptom_block as _sym_block
                    _sym_rows = [(r['user_message'], r['created_at']) for r in reversed(all_rows)]
                    _sym_ctx = _sym_block(_sym_rows)
                except Exception as _se:
                    import traceback as _tb
                    print("vision症状高亮块生成失败(降级全量原文): " + str(_se))
                    print(_tb.format_exc())
                    _sym_ctx = ""
                if _sym_ctx:
                    system_prompt += (
                        "\n\n" + _sym_ctx +
                        "\n\n【自述症状对照五铁律(务必逐条执行, 不得遗漏任何一条)】"
                        "① 历史主诉症状: 必须写进【综合辨证】段的主证/兼证里(不是只提一句), 即使照片看不出来也要作为辨证依据。"
                        "② 已好的历史症状: 记住是【历史症状】, 本次提示可能复发/注意观察/调护防复, 别再说'没这个症状'。"
                        "③ 假症状(用户否认/打错字): 本次必须绕过, 不得当作真实症状分析, 可在末尾附注'该症状已确认非真实'。"
                        "④ 【主诉症状入三方案铁律】每个历史主诉症状必须落到三个食疗方案之一(方案一主证/方案二兼证/方案三固本), 该方案标题里标明对应症状(如'兼证·皮肤瘙痒')。"
                        "⑤ 【症状-方案映射表(画表, 规范)】三个方案开完后, 附一节'症状-方案映射表'，用 markdown 表格: 表头『症状 | 落在哪个方案 | 方案里对应食材』，每个历史主诉症状一行(症状名带来源日期，如'皮肤瘙痒(2026-10-14)')。表格必须规范: 表头行 + 一行 |---|---| 分隔线 + 数据行，列数一致，每格文字精简(食材顿号连写，≤20字)。也严禁把症状单独甩到回复最后只给建议不给配方。"
                    )
                else:
                    # 症状块抽取失败降级: 把全量历史里含症状词的行直接喂给小麦(保历史主诉不漏)
                    _sym_kw = ("痒","痛","症","病","不","好","乏","胀","溏","虚","热","寒","汗","眠","咳","痰","痛","酸","麻","肿")
                    _fallback_lines = []
                    for r in reversed(all_rows):
                        _um = (r['user_message'] or '')
                        if any(k in _um for k in _sym_kw):
                            _fallback_lines.append(f"({r['created_at'][:10]}) {_um}")
                    if _fallback_lines:
                        system_prompt += (
                            "\n\n【用户自述症状(降级直读, 逐条对照)】\n" + "\n".join(_fallback_lines)
                        )
        except Exception as e:
            print(f"vision加载用户全部历史对话失败: {e}")
    if request.session_id:
        try:
            conn = get_user_db()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT user_message, assistant_reply, created_at FROM chat_history WHERE session_id = ? ORDER BY created_at DESC LIMIT 10',
                (request.session_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            if rows:
                _sess_lines = []
                for row in reversed(rows):
                    _sess_lines.append(f"用户: {(row['user_message'] or '')[:300]}")
                    _sess_lines.append(f"小麦: {(row['assistant_reply'] or '')[:300]}")
                _sess_ctx = "\n".join(_sess_lines)
                if _sess_ctx and _sess_ctx not in history_context:
                    system_prompt += f"\n\n【本次会话最近的对话】\n{_sess_ctx}"
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
                        "同时请结合【用户体质档案】里的历史辨证结论(之前的体质/证型判断), 分析本次结果与历史辨证是否一致、"
                        "哪些在改善、哪些还没好转、有无新出现的证候。"
                    )
                    system_prompt += (
                        f"\n\n【视觉趋势参考】该用户历史已存 {len(_vecs)} 张照片, 其整体视觉特征均值: {_gray_info}。" + _trend_note
                    )
                    _has_photo_trend = True
                else:
                    _has_photo_trend = False
            else:
                _has_photo_trend = False
            # 2026-10-17 中华要求: 历史辨证内容也要一起对比 — 把该用户最近的历史辨证结论拉出来拼进提示词,
            # 即使历史照片不足 2 张(没有视觉趋势), 只要有历史辨证记录也要做"本次 vs 历史"对比
            try:
                _conn3 = get_user_db()
                _hist_tz = _conn3.execute(
                    "SELECT created_at, tizhi, zhengxing, advice FROM tizhi_records "
                    "WHERE user_id=? AND (tizhi IS NOT NULL AND tizhi != '' OR advice IS NOT NULL AND advice != '') "
                    "ORDER BY created_at DESC, id DESC LIMIT 20",
                    (request.user_id,)
                ).fetchall()
                _conn3.close()
                if _hist_tz:
                    _hz_lines = []
                    for _r in reversed(_hist_tz):
                        _adv = (_r['advice'] or '')
                        # 取 advice 里的"主证/兼证"部分给 LLM 做对照 (不取全部, 避免 prompt 爆炸)
                        import re as _re3
                        _main = _re3.search(r'主证[：:]\s*([一-龥、，,]+)', _adv)
                        _sec  = _re3.search(r'兼证[：:]\s*([一-龥、，,]+)', _adv)
                        _hz = "{} 体质:{} 证型:{}".format(
                            str(_r['created_at'] or '')[:10],
                            _r['tizhi'] or '未定',
                            _r['zhengxing'] or '未定')
                        if _main: _hz += " 主证:{}".format(_main.group(1)[:40])
                        if _sec:  _hz += " 兼证:{}".format(_sec.group(1)[:40])
                        _hz_lines.append(_hz)
                    _hist_note = (
                        "\n\n【历史辨证记录(真实存档, 非假设)】该用户之前的辨证结论(旧→新):\n"
                        + "\n".join(_hz_lines)
                        + "\n【铁律】本次辨证必须在分析里加一节【与历史对比】: 逐条对照上面历史记录, "
                          "点出哪些证候/体质延续了、哪些好转了、哪些是新出现的; 若本次与某次历史一致, "
                          "明确说与该日期那次相同; 若全部历史都查不到, 才说暂无历史记录。严禁编造不存在的历史结论。"
                        "\n【铁律】照片里能看到的部位(舌头/眼睛/面色/皮肤等)必须逐一写进分析, "
                          "看不清楚的部位就如实说看不清, 严禁编造。"
                    )
                    system_prompt += _hist_note
            except Exception as _e3:
                print("[vision] 拼接历史辨证记录失败:", _e3)
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
            result["content"][:4000],  # 2026-10-20 中华: 2000→4000(原截断在方案二三+叮嘱+尾部三段前, 收藏/分享图读不全)
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
            advice_full = _strip_tizhi_data_json(result["content"])[:4000]
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
    # 2026-10-17 中华铁律(90s总预算): 预算耗尽(到deadline还有不足25s)就跳过商品搜索,
    # 直接带辨证结果返回, 不默默等
    products = []
    if _time.time() < _vision_deadline - 25:
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
    # 2026-10-18 中华要求: 尾部固定顺序三段: 养生参考 → 🛒推荐 → AI声明; 去重去下划线
    # 🛒 推荐句是代码后面统一追加的, 若 LLM 自己也写了, 先剥掉(服务端统一加)
    import re as _re2c
    # 剥掉 LLM 写的 AI 生成声明(含 _ 下划线版)
    _ai_pat = r'(?:^|\n)\s*[_*]*以上内容由人工智能生成，仅供参考。[_*]*(?=\n|$)'
    while _re2c.search(_ai_pat, reply_text):
        reply_text = _re2c.sub(_ai_pat, '', reply_text)
    # 剥掉 LLM 写的 🛒 推荐句(服务端统一在结尾加)
    _cart_pat = r'(?:^|\n)\s*🛒[\s\S]{0,60}?点击即可购买[～~。]?\s*(?=\n|$)'
    while _re2c.search(_cart_pat, reply_text):
        reply_text = _re2c.sub(_cart_pat, '', reply_text)
    # "以上为养生文化参考" 若多次, 只保留第一次
    _ref_pat = r'(?:^|\n)\s*以上为养生文化参考，不构成医疗诊断，身体不适请及时就医(?=\n|$)'
    _refs = list(_re2c.finditer(_ref_pat, reply_text))
    if len(_refs) > 1:
        for m in reversed(_refs[:-1]):
            _s, _e = m.span()
            _ls = reply_text.rfind('\n', 0, _s) + 1
            _le = reply_text.find('\n', _e)
            if _le < 0: _le = len(reply_text)
            reply_text = reply_text[:_ls] + reply_text[_le:]
    reply_text = reply_text.rstrip()
    # 统一按固定顺序追加: 养生参考(若LLM没写) → 🛒推荐 → AI声明
    if not reply_text.endswith('以上为养生文化参考，不构成医疗诊断，身体不适请及时就医'):
        reply_text += '\n\n以上为养生文化参考，不构成医疗诊断，身体不适请及时就医'
    reply_text += '\n\n🛒 上面提到的食材，我在下方帮你找了有机认证的，点击即可购买～'
    reply_text += '\n\n以上内容由人工智能生成，仅供参考。'
    # 合并多余空行
    reply_text = _re2c.sub(r'\n{3,}', '\n\n', reply_text).rstrip()

    # 2026-10-18 小蕊修: LLM 写 "### 2. 面色 & 眼部" 但内容含皮肤/头发/唇,
    # 服务端按该节实际内容补全标题(把出现的项目补进标题, 不再错位)
    # 2026-10-18l 升级(中华反馈"题目只提到两样, 内容三样合在一起"): 不再只补标题,
    # 直接重写该节正文——按节内实际出现的项目, 逐条断开成独立段落(一行一项),
    # 标题也只写节内真实出现的项目。标题与内容从此严格一致。
    import re as _re2a
    _ITEM_WORDS = [('面色', '面色'), ('眼神', '眼神'), ('眼袋', '眼周'), ('眼睑', '眼周'),
                   ('眼部', '眼周'), ('皮肤', '皮肤'), ('头发', '头发'), ('唇色', '唇色'),
                   ('唇', '唇色'), ('气色', '气色')]
    def _fix_section_title(m):
        _title, _body = m.group(1), m.group(2)
        _t = _title[5:].strip() if _title[:5].startswith('###') else _title
        _present = []
        for _kw, _label in _ITEM_WORDS:
            if _label in _t:  # 标题已含, 保持原顺序标记
                _present.append(_label)
            elif _kw in _body:
                _present.append(_label)
        if not _present:
            return m.group(0)
        # 正文逐条断开: 把 "面色：xxx 眼神：xxx 皮肤：xxx" 这类连排(含表格外的列表/行内)改成一行一项
        _lines = []
        for _bl in _body.split('\n'):
            _s = _bl.strip()
            if not _s:
                _lines.append('')
                continue
            # 行内含多个 "项目：" 起始点(如 "面色：...眼神：...皮肤：...") → 在第二个起拆行
            _m2 = list(_re2a.finditer(r'(面色|眼神|眼周|皮肤|头发|唇色|气色)\s*[:：]', _s))
            if len(_m2) >= 2:
                _first = _s[:_m2[1].start()].rstrip()
                _lines.append(_first)
                for _j in range(1, len(_m2)):
                    _seg_end = _m2[_j + 1].start() if _j + 1 < len(_m2) else len(_s)
                    _lines.append(_s[_m2[_j].start():_seg_end].rstrip())
            else:
                _lines.append(_bl)
        # 标题重写: 只用真实出现的项目, 连词用 "、"
        _new_title = '### ' + _title[len('###'):].split(' ')[0].split('.')[0].strip() + '. ' + '、'.join(_present)
        _num = _re2a.match(r'###\s*(\d+)', _title)
        if _num:
            _new_title = '### ' + _num.group(1) + '. ' + '、'.join(_present)
        return _new_title + '\n' + '\n'.join(_lines).strip('\n')
    reply_text = _re2a.sub(r'(###\s*\d+\.\s*[^\n]+)([\s\S]*?)(?=\n###\s*\d+\.|\n## |\n以上|🛒|$)', _fix_section_title, reply_text)

    # 2026-10-18p 重写(主证/兼证/体质倾向拆段): 旧版整行抽取的正则抓不到 LLM 实际输出
    # (如 "**主证**：...  **兼证**：...  体质倾向：..." 挤一行, 或 ** 夹在关键词与冒号之间),
    # 导致三项常被整体移到全文末尾(连 AI 声明后面都跑出去了)。改为逐行线性扫描:
    # 1) 行内含多个关键词项 → 按行拆开, 一项一行; 2) 三项全齐时按 体质倾向→主证→兼证 排序
    #    (缺哪项跳哪项), 每项之间空一行; 3) 保持原位(在辨证结论段内), 不再整段移位。
    import re as _re2l
    _ITEM_LINE = _re2l.compile(r'\*{0,2}(体质倾向|主证|兼证)\s*\*{0,2}\s*[：:]')
    _raw_lines = reply_text.split('\n')
    _new_lines = []
    _items = []  # [order, label, line_text]
    _order_map = {'体质倾向': 0, '主证': 1, '兼证': 2}
    _drop_this_line = False
    for _l in _raw_lines:
        _stripped = _l.strip()
        _hits = list(_ITEM_LINE.finditer(_stripped))
        if len(_hits) >= 1:
            # 这一行属于 主证/兼证/体质 项: 按关键词起点切成若干项
            _segs = []
            for _j, _h in enumerate(_hits):
                _seg_start = _h.start()
                _seg_end = _hits[_j + 1].start() if _j + 1 < len(_hits) else len(_stripped)
                _segs.append(_stripped[_seg_start:_seg_end].rstrip())
            if len(_hits) == 1:
                # 只有单项 → 保留这一行原样(可能带 ** 加粗), 记录用于排序
                _lbl = _hits[0].group(1)
                _items.append((_order_map[_lbl], _lbl, _stripped))
                # 行原样保留在原地(不摘除), 只靠排序+空行处理
                _new_lines.append(_stripped)
            else:
                # 多项挤一行 → 原地只放回第一项, 其余各项按序重插(后面 _idx_map 统一处理)
                for _seg in _segs:
                    _lbl2 = _re2l.match(r'\*{0,2}(体质倾向|主证|兼证)', _seg)
                    _items.append((_order_map[_lbl2.group(1)], _lbl2.group(1), _seg))
                _new_lines.append(_segs[0])
            _drop_this_line = False
        else:
            _new_lines.append(_l)
            _drop_this_line = False
    # 若一行里挤了多项, 需要把其余各项也放回去: 找到 _new_lines 里第一项位置, 按序插入其余项
    if _items:
        # 找 _new_lines 中出现的各项行, 重排为 体质倾向→主证→兼证, 项间空一行
        # 策略: 找到最早出现的 _items 项在 _new_lines 的下标, 把该处起连续的项行替换成按序排列的三行
        _idx_map = []  # (position_in_new_lines, item_tuple)
        _seen_pos = set()
        for _ord_i, _lbl, _txt in _items:
            # 定位: 第一次出现 _txt (作为整行) 在 _new_lines 中的位置
            for _pi, _pl in enumerate(_new_lines):
                if _pl.strip() == _txt and _pi not in _seen_pos:
                    _idx_map.append((_pi, _ord_i, _lbl, _txt))
                    _seen_pos.add(_pi)
                    break
        _idx_map.sort(key=lambda x: x[0])
        if len(_idx_map) >= 2:
            # 多行情况: 原地逐项替换为按序排列 + 空行分隔
            _first_pos = _idx_map[0][0]
            _ordered = sorted(_idx_map, key=lambda x: x[1])
            _ordered_texts = [t[3] for t in _ordered]
            # 从后往前删掉原来占位, 再在第一个位置插回按序文本
            for _pos in sorted([t[0] for t in _idx_map], reverse=True):
                if _pos != _first_pos:
                    del _new_lines[_pos]
            _insert_block = _ordered_texts[0]
            if len(_ordered_texts) > 1:
                _insert_block = '\n\n'.join(_ordered_texts)
            _new_lines[_first_pos] = _insert_block
        elif len(_idx_map) == 1:
            pass  # 只有一项, 无需重排
    reply_text = '\n'.join(_new_lines)
    # 兜底: 汉字后紧跟 兼证/体质倾向/主证 行首词时, 断行(兼容 **关键词**： 加粗写法)
    _strong_pat = _re2l.compile(r'([\u4e00-\u9fff])\s*(?=\*{0,2}(?:兼证|体质倾向|主证)\*{0,2}\s*[：:])')
    reply_text = _strong_pat.sub(r'\1\n', reply_text)



    # 2026-10-17d 中华要求(方案二雷同): 服务端检测 3 方案食材重叠度,
    # 方案二与方案一重叠 >40% → 追加更正提示(兜底, 正常不应触发)
    # 2026-10-17d 中华要求(方案二雷同): 服务端检测 3 方案食材重叠度,
    # 若方案二与方案一重叠 >50%, 在回复后追加一行提醒"方案二应与方案一方向不同"
    import re as _re2b
    # 2026-10-17e 归一: LLM 偶尔输出 "**配方：** 方： 麦冬15g..." (开头多了"方："前缀), 剥掉
    # 2026-10-17h 修: 容忍 ** 后任意空白 + 全角/半角冒号 + 方后可能还有空格
    reply_text = _re2b.sub(r'(\*\*配方：\*\*)\s*方\s*[:：]\s*', r'\1 ', reply_text)
    reply_text = _re2b.sub(r'(\*\*做法：\*\*)\s*方\s*[:：]\s*', r'\1 ', reply_text)
    # 2026-10-18 补: LLM 还会输出 "**做法：** 法： 铁皮石斛..." (做法行首多"法："前缀), 剥掉
    reply_text = _re2b.sub(r'(\*\*做法：\*\*)\s*法\s*[:：]\s*', r'\1 ', reply_text)
    reply_text = _re2b.sub(r'(\*\*配方：\*\*)\s*法\s*[:：]\s*', r'\1 ', reply_text)
    _plan_blocks = _re2b.findall(r'方案[一二三][^\n]*\n+\*\*配方：\*\*\s*([\s\S]*?)(?=\n\n\*\*做法|\n###|\n## |\n以上|🛒|$)', reply_text)
    if len(_plan_blocks) >= 2:
        def _extract_ingredients(txt):
            # 取食材名(去掉用量数字单位): "黄芪15g" → "黄芪"
            return set(_re2b.findall(r'([\u4e00-\u9fff]{1,6})(?:\d+(?:\.\d+)?\s*(?:g|克|枚|朵|只|片|颗|粒|个|根|支|条|瓣|勺|汤匙|毫升|ml|ML)|个|枚|朵|只|片|颗|粒|根|支|条|瓣|勺|汤匙)?\s*(?:[、,，]|$)', txt))
        _i1 = _extract_ingredients(_plan_blocks[0])
        _i2 = _extract_ingredients(_plan_blocks[1])
        _i3 = _extract_ingredients(_plan_blocks[2]) if len(_plan_blocks) > 2 else set()
        _overlap_12 = (_i1 & _i2) if _i1 and _i2 else set()
        _overlap_23 = (_i2 & _i3) if _i2 and _i3 else set()
        _dup = len(_overlap_12) > max(len(_i1),1)*0.4 or len(_overlap_23) > max(len(_i2),1)*0.4
        if _dup:
            reply_text += ('\n\n⚠️ 注意：方案二与方案一食材重叠较多，建议在实际执行时根据主证/兼证侧重调整用量与主次；'
                          '方案三作为长期固本调理，可与前两方交替使用。')

    # 2026-10-17b 中华要求: 配方/做法 排版铁律 服务端兜底规范化——
    # LLM 有时输出 "配方：xxx" 不加粗/不加分号, 前端 mdToHtml 只认 **xxx** 加粗,
    # 这里统一: 配方行 → **配方：**xxx。  做法行 → **做法：**xxx
    _lines = reply_text.split('\n')
    _new_lines = []
    for _l in _lines:
        _s = _l.lstrip()
        if _s.startswith('配方：') or _s.startswith('配方:') or _s.startswith('**配方：**') or _s.startswith('**配方:**'):
            _prefix = '配方'
            _body = _s[len(_prefix)+1:].lstrip('：:').strip()
            # 去掉可能已有的 ** 包裹
            _body = _body.replace('**','')
            # 2026-10-17g 归一: LLM 偶尔在配方行首多写一个"方："(如 "**配方：** 方： 麦冬15g..."), 剥掉
            # 2026-10-18k 补: 同理剥"法："前缀
            import re as _re2g
            _body = _re2g.sub(r'^方[:：]\s*', '', _body)
            _body = _re2g.sub(r'^法[:：]\s*', '', _body)
            if not _body.endswith('。') and _body:
                _body += '。'
            _new_lines.append('**配方：** ' + _body)
        elif _s.startswith('做法：') or _s.startswith('做法:') or _s.startswith('**做法：**') or _s.startswith('**做法:**'):
            _body = _s[3:].lstrip('：:').strip()
            _body = _body.replace('**','')
            _body = _re2g.sub(r'^方[:：]\s*', '', _body)
            _body = _re2g.sub(r'^法[:：]\s*', '', _body)
            _new_lines.append('**做法：** ' + _body)
        else:
            _new_lines.append(_l)
    reply_text = '\n'.join(_new_lines)
    # 2026-10-20 中华反馈「小麦输出内容没分段排版、把__这些符号删了、尾部三段也要分开、重点字要突出」:
    # 前次误删 ** 加粗 → 重点字不突出, 这次恢复加粗; 删装饰线 ---/===/___, 段起点词强制断行。
    import re as _re2d
    _TILE_WORDS = ('养生文化参考', '🛒', '人工智能生成')
    _lines = reply_text.split('\n')
    _clean = []
    for _l in _lines:
        _s = _l.strip()
        if not _s:
            _clean.append('')
            continue
        # ① 独立装饰线(---/===/___/****) → 空行; **加粗**保留(重点字突出)
        if _re2d.fullmatch(r'-{2,}|={2,}|\*{4,}|_{2,}', _s):
            _clean.append('')
            continue
        # ②b | markdown 表格行 → 保留(中华 2026-10-20 要表格对照清晰), 只修正格式: 表头行加粗, 数据行原样
        #     分隔行 |---|---| 保留(前端 mdToHtml 靠它渲染表格); 列数不一致时补齐首行列数(防错位)
        if _re2d.match(r'^\|', _s):
            _clean.append(_s)
            continue
        # ② 行首 ## 标题符删掉(保留标题文字)
        _s2 = _re2d.sub(r'^\s*#{1,6}\s*', '', _s)
        # ③ 行首列表符 -/* 删掉(保留 **加粗** 内容)
        _s2 = _re2d.sub(r'^\s*[-*]\s+(?!\*)', '', _s2)
        # ④ 行内 --- 分隔符(挤一行时粘在行内) 删掉
        _s2 = _re2d.sub(r'\s*-{3,}\s*', ' ', _s2)
        # ⑤ 段起点词(仅结构性词 方案一/二/三、配方、做法)前紧跟长句(>4字) → 强制断行独立成段。
        #    主证/兼证/望诊/辨证 等常嵌句子里, 不用来断行(否则"方案一：健脾益气汤（主证·脾气虚弱证）"被截断)。
        _STRUCT_KWS = ('方案一', '方案二', '方案三', '配方', '做法')
        import re as _re2d5
        _pat5 = _re2d5.compile('|'.join(_re2d5.escape(k) for k in _STRUCT_KWS))
        _matches = list(_pat5.finditer(_s2))
        _split_pts = [m.start() for m in _matches if m.start() > 4]
        if _split_pts:
            _prev = 0
            for _bp in _split_pts:
                _clean.append(_s2[_prev:_bp].rstrip())
                _prev = _bp
            _clean.append(_s2[_prev:].rstrip())
        else:
            _clean.append(_s2)
    # ⑥ 尾部三段挤一行 → 拆开
    _final = []
    for _l in _clean:
        _s = _l.strip()
        if not _s:
            _final.append('')
            continue
        # 同一行里同时出现两段尾部词 → 拆开
        _hits = [(w, _s.find(w)) for w in _TILE_WORDS if w in _s]
        if len(_hits) >= 2:
            _hits.sort(key=lambda x: x[1])
            # 按尾部词起点切段
            _segs = []
            for _j, (_w, _pos) in enumerate(_hits):
                _seg_end = _hits[_j+1][1] if _j+1 < len(_hits) else len(_s)
                _segs.append(_s[_pos:_seg_end].rstrip())
            _final.extend(_segs)
        else:
            _final.append(_s)
    # ⑦ 多个连续空行压缩成单个
    _out = []
    _prev_blank = False
    for _l in _final:
        if _l.strip():
            _out.append(_l)
            _prev_blank = False
        else:
            if not _prev_blank:
                _out.append('')
            _prev_blank = True
    # 去头尾空行
    while _out and not _out[0].strip(): _out.pop(0)
    while _out and not _out[-1].strip(): _out.pop()
    reply_text = '\n'.join(_out)
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

    # 2026-10-16 小蕊修(中华反馈「前面卡住后面全卡住」): LLM/人脸/淘宝搜索全是阻塞调用,
    # 原实现在 async 事件循环线程里直接跑, 一个慢请求(淘宝搜索最坏90s)会卡死整个服务,
    # 后续所有请求(新拍照/收藏/分享图)全部排队 → "短路"。放 to_thread 后互不影响。
    return await asyncio.to_thread(_chat_vision_work, request, image_list)


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


