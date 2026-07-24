"""
SOM 松麦 - 后端服务入口
小麦SOM = Qwen3.5 2B + RAG知识库
"""
import json
import os
import sys
from pathlib import Path

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

    # 2. 根据辨证结果搜索商品
    products = []
    if result.get("recommendations"):
        seen_ids = set()
        for rec in result["recommendations"][:3]:
            items = shop.search(rec["name"], platform="taobao", page_size=3)
            for item in items:
                item_key = item.get('item_id', '') or item.get('title', '')
                if item_key not in seen_ids:
                    seen_ids.add(item_key)
                    products.append(item)
            if len(products) >= 6:
                break

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

# 本地签到记录（生产环境应使用数据库）
_checkin_records = {}  # user_id -> {last_date, total_points, streak}

@app.get("/api/checkin/status")
async def checkin_status(user_id: str):
    """获取签到状态"""
    from datetime import datetime, timezone, timedelta
    beijing_tz = timezone(timedelta(hours=8))
    today = datetime.now(beijing_tz).strftime('%Y-%m-%d')
    
    record = _checkin_records.get(user_id, {})
    checked_in_today = record.get('last_date') == today
    
    return {
        "checked_in_today": checked_in_today,
        "total_points": record.get('total_points', 0),
        "streak": record.get('streak', 0),
        "today": today
    }

@app.post("/api/checkin/do")
async def do_checkin(request: CheckinRequest):
    """执行签到"""
    from datetime import datetime, timezone, timedelta
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    today = now.strftime('%Y-%m-%d')
    yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    
    record = _checkin_records.get(request.user_id, {
        'last_date': '',
        'total_points': 0,
        'streak': 0
    })
    
    if record.get('last_date') == today:
        return CheckinResponse(
            success=False,
            message="今天已经签到过了"
        )
    
    # 计算连续签到
    if record.get('last_date') == yesterday:
        record['streak'] = record.get('streak', 0) + 1
    else:
        record['streak'] = 1
    
    record['last_date'] = today
    record['total_points'] = record.get('total_points', 0) + 10
    _checkin_records[request.user_id] = record
    
    return CheckinResponse(
        success=True,
        points=10,
        total_points=record['total_points'],
        message=f"签到成功！连续签到{record['streak']}天，获得10积分"
    )

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
