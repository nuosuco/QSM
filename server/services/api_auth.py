# -*- coding: utf-8 -*-
"""
SOM API 鉴权 + 限流中间件
为 som.skill 开放平台做准备
- API Key 鉴权（X-API-Key header）
- 滑动窗口限流（每key每分钟N次）
- 白名单路径（健康检查等不需要鉴权）
"""
import time
import hashlib
import secrets
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# API Key 存储（生产环境应存数据库/Redis）
# 格式: {api_key: {"name": "xxx", "rate_limit": 60, "created_at": timestamp}}
_api_keys = {}

# 限流记录: {api_key: [timestamp1, timestamp2, ...]}
_rate_limits = {}

# 白名单路径（不需要鉴权）
WHITELIST_PATHS = [
    "/",
    "/api/health",
    "/docs",
    "/openapi.json",
    "/redoc",
]

# 默认限流：每分钟60次
DEFAULT_RATE_LIMIT = 60


def generate_api_key(prefix: str = "som") -> str:
    """生成 API Key"""
    return f"{prefix}_{secrets.token_hex(16)}"


def register_api_key(name: str, rate_limit: int = DEFAULT_RATE_LIMIT) -> str:
    """注册新的 API Key"""
    key = generate_api_key()
    _api_keys[key] = {
        "name": name,
        "rate_limit": rate_limit,
        "created_at": time.time(),
    }
    return key


def revoke_api_key(api_key: str) -> bool:
    """撤销 API Key"""
    if api_key in _api_keys:
        del _api_keys[api_key]
        _rate_limits.pop(api_key, None)
        return True
    return False


def list_api_keys() -> list:
    """列出所有 API Key（脱敏）"""
    result = []
    for key, info in _api_keys.items():
        masked = key[:8] + "..." + key[-4:]
        result.append({
            "key": masked,
            "name": info["name"],
            "rate_limit": info["rate_limit"],
            "created_at": info["created_at"],
        })
    return result


def _check_rate_limit(api_key: str, limit: int) -> bool:
    """滑动窗口限流检查"""
    now = time.time()
    window = 60  # 1分钟窗口

    if api_key not in _rate_limits:
        _rate_limits[api_key] = []

    # 清理过期记录
    _rate_limits[api_key] = [t for t in _rate_limits[api_key] if now - t < window]

    if len(_rate_limits[api_key]) >= limit:
        return False

    _rate_limits[api_key].append(now)
    return True


class APIAuthMiddleware(BaseHTTPMiddleware):
    """API 鉴权 + 限流中间件"""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # 白名单放行
        if path in WHITELIST_PATHS or not path.startswith("/api/"):
            return await call_next(request)

        # 获取 API Key
        api_key = request.headers.get("X-API-Key", "")

        # 如果没有配置任何 key，暂时放行（开发模式）
        if not _api_keys:
            return await call_next(request)

        # 验证 Key
        if api_key not in _api_keys:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or missing API Key", "detail": "请在请求头中添加 X-API-Key"}
            )

        # 限流检查
        key_info = _api_keys[api_key]
        if not _check_rate_limit(api_key, key_info["rate_limit"]):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "detail": f"每分钟最多 {key_info['rate_limit']} 次请求"}
            )

        return await call_next(request)


# ========== 管理接口（供内部调用） ==========

def get_auth_status() -> dict:
    """获取鉴权状态"""
    return {
        "enabled": bool(_api_keys),
        "total_keys": len(_api_keys),
        "keys": list_api_keys(),
    }
