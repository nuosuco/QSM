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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List

# 加载配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

app = FastAPI(
    title="SOM 松麦 API",
    description="小麦SOM - 中医辨证 + 有机食品推荐",
    version="1.0.0"
)

# CORS - 允许网页版、小程序调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 数据模型 ==========

class ChatRequest(BaseModel):
    """对话请求 - 小麦SOM问诊"""
    message: str
    session_id: Optional[str] = None  # 用户会话ID
    user_id: Optional[str] = None     # 用户ID

class ProductSearchRequest(BaseModel):
    """商品搜索请求"""
    keyword: str
    platform: Optional[str] = "taobao"  # taobao / jd / all
    page: int = 1
    page_size: int = 10

class ChatResponse(BaseModel):
    """对话响应"""
    reply: str
    tizhi: Optional[str] = None       # 体质判断
    zhengxing: Optional[str] = None   # 证型
    recommendations: List[dict] = []  # 推荐食材
    products: List[dict] = []         # 推荐商品
    session_id: str

class ProductItem(BaseModel):
    """商品信息"""
    title: str
    price: str
    image: str
    url: str
    platform: str
    commission_rate: Optional[str] = None
    shop_name: Optional[str] = None

# ========== 静态文件托管（网页版前端） ==========

WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.isdir(WEB_DIR):
    # 挂载静态文件目录
    app.mount("/css", StaticFiles(directory=os.path.join(WEB_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(WEB_DIR, "js")), name="js")
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

    @app.get("/")
    async def serve_web():
        from fastapi.responses import FileResponse
        return FileResponse(os.path.join(WEB_DIR, "index.html"))

# ========== API路由 ==========

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "SOM松麦后端"}

# ========== 小麦SOM 对话接口 ==========

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    小麦SOM核心对话接口
    """
    from services.bianzheng import BianzhengEngine
    from services.shop import ShopService

    engine = BianzhengEngine()
    shop = ShopService()

    # 1. 辨证分析
    result = engine.analyze(request.message)

    # 2. 根据辨证结果搜索商品（带超时保护，最长5秒）
    products = []
    if result.get("recommendations"):
        seen_ids = set()
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_map = {
                executor.submit(shop.search, rec["name"], "taobao", 1, 3): rec["name"]
                for rec in result["recommendations"][:3]
            }
            for future in concurrent.futures.as_completed(future_map, timeout=5):
                try:
                    items = future.result()
                    for item in items:
                        item_key = item.get('item_id', '') or item.get('title', '')
                        if item_key and item_key not in seen_ids:
                            seen_ids.add(item_key)
                            products.append(item)
                except Exception:
                    pass
                if len(products) >= 6:
                    break

    # 3. 保存对话历史到数据库
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
    """
    获取商品分类目录
    有机认证食品 + 药食同源食材分类
    """
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
    """
    商品搜索接口
    支持淘宝、京东双平台
    自动过滤：只返回有机认证、药食同源、健康环保认证产品
    sort: 空=综合, price_asc=价格最低, price_desc=价格最高, sales=销量最高, credit=评价最高
    """
    from services.shop import ShopService
    shop = ShopService()
    
    # 如果是分类名，先转成搜索关键词
    search_kw = shop.get_category_keyword(keyword) if keyword else ''
    if not search_kw and keyword:
        search_kw = keyword
    
    # 优先从数据库缓存查
    items = shop.search_from_cache(keyword=search_kw, page=page, page_size=page_size)
    if len(items) < page_size:
        # 缓存不足，调淘宝API实时搜索
        items = shop.search(search_kw, platform=platform, page=page, page_size=page_size, sort=sort)
    return {"keyword": keyword, "search_keyword": search_kw, "platform": platform, "total": len(items), "items": items}

# ========== 知识库接口 ==========

@app.get("/api/knowledge/yaoshi")
async def get_yaoshi_tongyuan():
    """获取药食同源食材库"""
    from services.knowledge import KnowledgeService
    ks = KnowledgeService()
    return ks.get_yaoshi_list()

@app.get("/api/knowledge/tizhi")
async def get_tizhi_list():
    """获取体质分类"""
    from services.knowledge import KnowledgeService
    ks = KnowledgeService()
    return ks.get_tizhi_list()

@app.get("/api/knowledge/shiliao")
async def get_shiliao(zhengxing: Optional[str] = None):
    """获取食疗方案"""
    from services.knowledge import KnowledgeService
    ks = KnowledgeService()
    return ks.get_shiliao(zhengxing)

# ========== 签到接口 ==========

class CheckinRequest(BaseModel):
    """签到请求"""
    user_id: str

class CheckinResponse(BaseModel):
    """签到响应"""
    success: bool
    points: int = 0
    total_points: int = 0
    message: str = ""

# ========== 数据库初始化 ==========

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
USER_DB_PATH = os.path.join(DATA_DIR, 'user_data.db')

def init_user_db():
    """初始化用户数据库"""
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    # 签到记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkin_records (
            user_id TEXT PRIMARY KEY,
            last_date TEXT,
            total_points INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0
        )
    ''')
    
    # 对话历史表
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
    
    # 搜索历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            keyword TEXT NOT NULL,
            platform TEXT DEFAULT 'taobao',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 商品收藏表
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
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_user ON search_history(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fav_user ON product_favorites(user_id)')
    
    conn.commit()
    conn.close()

init_user_db()

def get_user_db():
    """获取用户数据库连接"""
    conn = sqlite3.connect(USER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_beijing_now():
    """获取当前北京时间"""
    utc_now = datetime.now(timezone.utc)
    beijing_tz = timezone(timedelta(hours=8))
    return utc_now.astimezone(beijing_tz)

# ========== 签到接口 ==========

@app.get("/api/checkin/status")
async def checkin_status(user_id: str):
    """获取签到状态（数据库持久化）"""
    now = get_beijing_now()
    today = now.strftime('%Y-%m-%d')
    
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM checkin_records WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        checked_in_today = row['last_date'] == today
        return {
            "checked_in_today": checked_in_today,
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
    """执行签到（数据库持久化）"""
    now = get_beijing_now()
    today = now.strftime('%Y-%m-%d')
    yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    
    conn = get_user_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM checkin_records WHERE user_id = ?', (request.user_id,))
    row = cursor.fetchone()
    
    if row and row['last_date'] == today:
        conn.close()
        return CheckinResponse(
            success=False,
            message="今天已经签到过了"
        )
    
    if row:
        last_date = row['last_date']
        total_points = row['total_points']
        streak = row['streak']
        
        if last_date == yesterday:
            streak += 1
        else:
            streak = 1
        
        total_points += 10
        
        cursor.execute('''
            UPDATE checkin_records 
            SET last_date = ?, total_points = ?, streak = ?
            WHERE user_id = ?
        ''', (today, total_points, streak, request.user_id))
    else:
        total_points = 10
        streak = 1
        cursor.execute('''
            INSERT INTO checkin_records (user_id, last_date, total_points, streak)
            VALUES (?, ?, ?, ?)
        ''', (request.user_id, today, total_points, streak))
    
    conn.commit()
    conn.close()
    
    return CheckinResponse(
        success=True,
        points=10,
        total_points=total_points,
        message=f"签到成功！连续签到{streak}天，获得10积分"
    )

# ========== 对话历史接口 ==========

@app.get("/api/chat/history")
async def get_chat_history(user_id: str, limit: int = 20):
    """获取对话历史"""
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM chat_history 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "total": len(rows),
        "history": [dict(r) for r in rows]
    }

@app.get("/api/chat/history/session")
async def get_session_history(session_id: str):
    """获取特定会话的对话历史"""
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM chat_history 
        WHERE session_id = ? 
        ORDER BY created_at ASC
    ''', (session_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "total": len(rows),
        "history": [dict(r) for r in rows]
    }

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

# ========== 对话历史接口 ==========

@app.get("/api/chat/history")
async def get_chat_history(user_id: str, limit: int = 20):
    """获取对话历史"""
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM chat_history 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "total": len(rows),
        "history": [dict(r) for r in rows]
    }

@app.get("/api/chat/history/session")
async def get_session_history(session_id: str):
    """获取特定会话的对话历史"""
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM chat_history 
        WHERE session_id = ? 
        ORDER BY created_at ASC
    ''', (session_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "total": len(rows),
        "history": [dict(r) for r in rows]
    }

@app.post("/api/chat/history/clear")
async def clear_chat_history(request: ClearHistoryRequest):
    """清空对话历史"""
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
    """获取搜索历史"""
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT keyword, platform, MAX(created_at) as last_searched
        FROM search_history 
        WHERE user_id = ? 
        GROUP BY keyword
        ORDER BY last_searched DESC 
        LIMIT ?
    ''', (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "total": len(rows),
        "history": [dict(r) for r in rows]
    }

@app.post("/api/search/history/add")
async def add_search_history(request: SearchAddRequest):
    """添加搜索历史"""
    conn = get_user_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO search_history (user_id, keyword, platform)
            VALUES (?, ?, ?)
        ''', (request.user_id, request.keyword, request.platform))
        conn.commit()
    finally:
        conn.close()
    return {"success": True}

@app.post("/api/search/history/clear")
async def clear_search_history(request: ClearHistoryRequest):
    """清空搜索历史"""
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
    """获取收藏商品列表"""
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM product_favorites
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "total": len(rows),
        "favorites": [dict(r) for r in rows]
    }

@app.post("/api/favorites/add")
async def add_favorite(request: FavoriteAddRequest):
    """添加商品收藏"""
    conn = get_user_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO product_favorites 
            (user_id, item_id, title, price, image, url, platform, shop_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.user_id,
            request.item_id,
            request.title,
            request.price,
            request.image,
            request.url,
            request.platform,
            request.shop_name,
        ))
        conn.commit()
        added = cursor.rowcount > 0
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}
    conn.close()
    return {"success": True, "added": added}

@app.post("/api/favorites/remove")
async def remove_favorite(user_id: str, item_id: str):
    """移除收藏商品（支持query参数和body两种方式）"""
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM product_favorites
        WHERE user_id = ? AND item_id = ?
    ''', (user_id, item_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return {"success": True, "deleted": affected}

@app.get("/api/favorites/check")
async def check_favorite(user_id: str, item_id: str):
    """检查是否已收藏"""
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 1 FROM product_favorites
        WHERE user_id = ? AND item_id = ?
    ''', (user_id, item_id))
    exists = cursor.fetchone() is not None
    conn.close()
    return {"favorited": exists}

# ========== 缓存统计接口 ==========

@app.get("/api/cache/stats")
async def cache_stats():
    """获取商品缓存统计"""
    from services.shop import ShopService
    shop = ShopService()
    return shop.get_cache_stats()

# ========== 每日养生建议接口 ==========

@app.get("/api/daily-tip")
async def daily_tip():
    """获取每日养生建议"""
    import random
    from datetime import datetime, timezone, timedelta
    beijing_tz = timezone(timedelta(hours=8))
    today = datetime.now(beijing_tz).strftime('%Y-%m-%d')
    
    tips = [
        {
            "title": "今日养生：早睡早起",
            "content": "子时（23:00-1:00）是胆经当令，最好提前入睡。睡前可用温水泡脚15分钟，助眠安神。",
            "tip_type": "作息",
            "emoji": "🌙"
        },
        {
            "title": "今日养生：喝杯枸杞红枣茶",
            "content": "枸杞滋补肝肾，红枣补中益气。取枸杞10g、红枣3枚，沸水冲泡，代茶饮。",
            "tip_type": "食疗",
            "emoji": "🍵"
        },
        {
            "title": "今日养生：健脾祛湿",
            "content": "湿气重的人适合喝薏米赤小豆汤。薏米50g、赤小豆50g，提前浸泡4小时后煮粥。",
            "tip_type": "食疗",
            "emoji": "🥣"
        },
        {
            "title": "今日养生：穴位按摩",
            "content": "按揉足三里穴（膝盖外膝眼下四横指），每次3-5分钟，可健脾和胃、补中益气。",
            "tip_type": "穴位",
            "emoji": "💆"
        },
        {
            "title": "今日养生：情绪调节",
            "content": "肝郁则百病生。建议做深呼吸练习：吸气4秒、屏息4秒、呼气6秒，重复10次。",
            "tip_type": "情志",
            "emoji": "🧘"
        },
        {
            "title": "今日养生：适量运动",
            "content": "春捂秋冻，适度运动最养人。推荐八段锦或太极，晨起练习30分钟，气血通畅。",
            "tip_type": "运动",
            "emoji": "🏃"
        },
        {
            "title": "今日养生：滋阴润燥",
            "content": "常感口干咽燥？试试百合银耳羹：百合20g、银耳15g，炖煮至粘稠，加冰糖调味。",
            "tip_type": "食疗",
            "emoji": "🍯"
        },
        {
            "title": "今日养生：补肾固精",
            "content": "黑芝麻核桃糊：黑芝麻30g、核桃仁20g、黑米30g，炒香磨碎冲糊食用，补肾乌发。",
            "tip_type": "食疗",
            "emoji": "🫘"
        },
        {
            "title": "今日养生：疏肝解郁",
            "content": "玫瑰花5朵、合欢花5g，沸水冲泡代茶饮。适合心情烦躁、压力大时饮用，疏肝解郁安神。",
            "tip_type": "食疗",
            "emoji": "🌹"
        },
        {
            "title": "今日养生：健脑益智",
            "content": "核桃仁30g、黑芝麻20g、桂圆肉15g，同煮20分钟食用。补脑益智，适合用脑过度者。",
            "tip_type": "食疗",
            "emoji": "🧠"
        },
        {
            "title": "今日养生：温经散寒",
            "content": "生姜5片、红枣6枚、红糖20g，加水煮15分钟趁热饮用。适合手脚冰凉、怕冷体质。",
            "tip_type": "食疗",
            "emoji": "🔥"
        },
        {
            "title": "今日养生：清肝明目",
            "content": "枸杞15g、菊花10g、决明子10g，沸水冲泡焖10分钟。适合长时间看手机电脑、眼睛干涩者。",
            "tip_type": "食疗",
            "emoji": "👁️"
        },
        {
            "title": "今日养生：健脾开胃",
            "content": "山楂10g、陈皮6g、麦芽10g，加水煮15分钟代茶饮。适合食欲不振、饭后腹胀者。",
            "tip_type": "食疗",
            "emoji": "🍊"
        },
        {
            "title": "今日养生：润肺止咳",
            "content": "雪梨1个去核，纳入川贝粉3g、冰糖适量，隔水蒸1小时。适合干咳少痰、咽干者。",
            "tip_type": "食疗",
            "emoji": "🍐"
        },
        {
            "title": "今日养生：安神助眠",
            "content": "酸枣仁15g、百合10g、莲子15g，加水煎煮30分钟，睡前1小时饮用。适合失眠多梦者。",
            "tip_type": "食疗",
            "emoji": "😴"
        },
        {
            "title": "今日养生：补气养血",
            "content": "黄芪15g、当归5g、红枣5枚、乌鸡半只，慢炖2小时。适合面色苍白、容易疲劳者。",
            "tip_type": "食疗",
            "emoji": "💪"
        },
        {
            "title": "今日养生：祛湿减肥",
            "content": "荷叶10g、山楂15g、陈皮6g，沸水冲泡焖15分钟。适合体胖困重、血脂偏高者。",
            "tip_type": "食疗",
            "emoji": "🏋️"
        },
        {
            "title": "今日养生：护发养颜",
            "content": "桑葚15g、黑芝麻20g、枸杞10g，磨粉冲糊食用。适合脱发白发、皮肤干燥者。",
            "tip_type": "食疗",
            "emoji": "💇"
        },
        {
            "title": "今日养生：艾灸保健",
            "content": "艾灸足三里、关元穴各10分钟，每周3次。可提升免疫力、健脾和胃、补中益气。",
            "tip_type": "穴位",
            "emoji": "🔥"
        },
        {
            "title": "今日养生：摩腹养胃",
            "content": "晨起空腹，顺时针摩腹100次，再逆时针100次。可促进肠道蠕动、改善消化功能。",
            "tip_type": "穴位",
            "emoji": "🤲"
        },
        {
            "title": "今日养生：叩齿固齿",
            "content": "晨起叩齿36次，舌抵上腭，津液咽下。可固齿健肾、生津养胃。",
            "tip_type": "作息",
            "emoji": "🦷"
        },
        {
            "title": "今日养生：提肛养肾",
            "content": "每天做提肛运动100次，吸气时收紧肛门，呼气时放松。可固肾益气、改善痔疮。",
            "tip_type": "运动",
            "emoji": "💪"
        },
        {
            "title": "今日养生：鸣天鼓",
            "content": "双手掌心紧按耳朵，手指放在后脑，食指弹中指上，耳中闻咚咚声。做36次，可健脑益智。",
            "tip_type": "穴位",
            "emoji": "👂"
        },
    ]
    # 用日期作为种子，保证同一天返回相同建议
    seed = sum(ord(c) for c in today)
    random.seed(seed)
    tip = random.choice(tips)
    return {"date": today, **tip}

# ========== 启动 ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=CONFIG["server"]["host"],
        port=CONFIG["server"]["port"],
        reload=CONFIG["server"]["debug"]
    )
