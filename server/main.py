"""
SOM 松麦 - 后端服务入口
小麦SOM = Qwen3.5 2B + RAG知识库
"""
import json
import os
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
    用户描述症状 → AI辨证 → 推荐养生方案 → 推荐商品
    
    这个接口被以下端调用：
    - 网页版 som.top
    - 微信小程序
    - AI购物助手
    - 未来Skill / 腾讯AI搜索
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
        for rec in result["recommendations"][:3]:
            items = shop.search(rec["name"], platform="taobao", page_size=3)
            products.extend(items)

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
    items = shop.search(keyword, platform=platform, page=page, page_size=page_size, sort=sort)
    return {"keyword": keyword, "platform": platform, "total": len(items), "items": items}

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

# ========== 启动 ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=CONFIG["server"]["host"],
        port=CONFIG["server"]["port"],
        reload=CONFIG["server"]["debug"]
    )
