# -*- coding: utf-8 -*-
"""
SOM LLM API 路由层
- 多服务商自动切换（一个用完/限流自动跳下一个）
- 支持文本对话、图片理解（vision）、图片生成
- 全部兼容 OpenAI 格式
- 冷却机制：额度耗尽的服务商短期内跳过
"""
import json
import os
import time
import requests
from typing import Optional, List

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "llm_providers.json")

# 冷却记录：{provider_name: 冷却到期时间戳}
_cooldowns = {}
# 轮询计数器：{provider_name: 当前key索引}
_round_robin = {}


def _load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def _is_cooled_down(name: str) -> bool:
    """检查服务商是否在冷却期内"""
    if name not in _cooldowns:
        return False
    if time.time() < _cooldowns[name]:
        return True
    del _cooldowns[name]
    return False


def _set_cooldown(name: str, seconds: int):
    _cooldowns[name] = time.time() + seconds


def _get_api_key(provider: dict) -> str:
    """获取服务商的 API key（支持多 key 轮询）"""
    keys = provider.get("api_keys") or []
    if keys:
        name = provider["name"]
        idx = _round_robin.get(name, 0)
        key = keys[idx % len(keys)]
        _round_robin[name] = idx + 1
        return key
    return provider.get("api_key", "")


def _get_providers_for(capability: str) -> list:
    """按优先级返回支持指定能力的服务商列表"""
    cfg = _load_config()
    providers = []
    for p in cfg["providers"]:
        if not p.get("enabled", True):
            continue
        if capability in p.get("models", {}):
            providers.append(p)
    providers.sort(key=lambda x: x.get("priority", 99))
    return providers


def _call_openai(base_url: str, api_key: str, model: str, messages: list,
                 timeout: int = 15, temperature: float = 0.7,
                 connect_timeout: int = 5) -> dict:
    """调用 OpenAI 兼容接口，返回 {success, content, error, status_code}
    timeout: 读取超时（秒），connect_timeout: 连接超时（秒）
    """
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload,
                             timeout=(connect_timeout, timeout))
        if resp.status_code == 429 or resp.status_code == 402:
            return {"success": False, "error": "quota_exceeded", "status_code": resp.status_code}
        if resp.status_code != 200:
            return {"success": False, "error": resp.text[:200], "status_code": resp.status_code}
        data = resp.json()
        message = data["choices"][0]["message"]
        content = message.get("content") or ""
        # 推理模型（如 sensenova）把分析结果放在 reasoning/reasoning_content 字段，
        # content 可能为空 —— 此时回退到 reasoning，不能误判为失败
        if not content.strip():
            content = message.get("reasoning") or message.get("reasoning_content") or ""
        if not content or not content.strip():
            return {"success": False, "error": "empty_response", "status_code": 200}
        return {"success": True, "content": content}
    except requests.exceptions.ConnectTimeout:
        return {"success": False, "error": "connect_timeout", "status_code": 0}
    except requests.exceptions.ReadTimeout:
        return {"success": False, "error": "read_timeout", "status_code": 0}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "timeout", "status_code": 0}
    except Exception as e:
        return {"success": False, "error": str(e)[:200], "status_code": 0}


def chat(user_message: str, system_prompt: str = "", history: list = None,
         temperature: float = 0.7) -> dict:
    """
    文本对话，自动切换服务商。
    返回 {success, content, provider, model, error}
    """
    cfg = _load_config()
    timeout = cfg.get("timeout_seconds", 15)
    connect_timeout = cfg.get("connect_timeout", 5)
    cooldown = cfg.get("cooldown_seconds", 3600)
    timeout_cooldown = cfg.get("timeout_cooldown_seconds", 300)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    providers = _get_providers_for("chat")
    errors = []

    for p in providers:
        name = p["name"]
        if _is_cooled_down(name):
            continue
        model = p["models"]["chat"]
        api_key = _get_api_key(p)
        result = _call_openai(p["base_url"], api_key, model, messages,
                              timeout, temperature, connect_timeout)
        if result["success"]:
            return {
                "success": True,
                "content": result["content"],
                "provider": name,
                "model": model,
            }
        # 额度耗尽 → 长冷却
        if result.get("status_code") in (429, 402):
            _set_cooldown(name, cooldown)
        # 超时/连接失败 → 短冷却（避免每次请求都白等）
        elif result["error"] in ("timeout", "connect_timeout", "read_timeout"):
            _set_cooldown(name, timeout_cooldown)
        errors.append(f"{name}: {result['error']}")

    return {"success": False, "content": "", "error": " | ".join(errors)}


def vision(user_message: str, image_url, system_prompt: str = "",
           temperature: float = 0.7) -> dict:
    """
    图片理解（看舌苔、面色、皮肤、患处等），需要支持 image 输入的服务商。
    image_url: 单张图片URL/base64，或多张图片的列表（兼容旧版）

    图片格式策略（2026-07-31 实测确认）：
    - base64 data URI 直接传给所有服务商（sensenova + agnes 均实测支持）
    - 无需转存公网 URL，省去磁盘IO和nginx依赖，链路更短更快
    """
    cfg = _load_config()
    # vision 处理图片较慢，用更宽松的超时（不用 chat 的 15s 短超时）
    timeout = cfg.get("vision_timeout_seconds", 45)
    connect_timeout = cfg.get("connect_timeout", 5)
    cooldown = cfg.get("cooldown_seconds", 3600)
    timeout_cooldown = cfg.get("timeout_cooldown_seconds", 300)

    # 兼容单图(str)和多图(list)
    if isinstance(image_url, str):
        image_list = [image_url]
    else:
        image_list = list(image_url or [])
    if not image_list:
        return {"success": False, "content": "", "error": "no image provided"}

    def _build_messages(images):
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        user_content = [{"type": "text", "text": user_message}]
        for u in images:
            user_content.append({"type": "image_url", "image_url": {"url": u}})
        msgs.append({"role": "user", "content": user_content})
        return msgs

    providers = _get_providers_for("vision")
    errors = []

    for p in providers:
        name = p["name"]
        if _is_cooled_down(name):
            continue
        # 所有服务商直接收 base64/原始URL（2026-07-31 实测 sensenova+agnes 均支持）
        messages = _build_messages(image_list)
        model = p["models"]["vision"]
        api_key = _get_api_key(p)
        result = _call_openai(p["base_url"], api_key, model, messages,
                              timeout, temperature, connect_timeout)
        if result["success"]:
            return {
                "success": True,
                "content": result["content"],
                "provider": name,
                "model": model,
            }
        if result.get("status_code") in (429, 402):
            _set_cooldown(name, cooldown)
        elif result["error"] in ("timeout", "connect_timeout", "read_timeout"):
            _set_cooldown(name, timeout_cooldown)
        errors.append(f"{name}: {result['error']}")

    return {"success": False, "content": "", "error": " | ".join(errors)}


def get_status() -> dict:
    """返回所有服务商状态（供监控用）"""
    cfg = _load_config()
    status = []
    for p in cfg["providers"]:
        status.append({
            "name": p["name"],
            "enabled": p.get("enabled", True),
            "cooled_down": _is_cooled_down(p["name"]),
            "models": p.get("models", {}),
            "priority": p.get("priority", 99),
        })
    return {"providers": status, "cooldowns": {k: v for k, v in _cooldowns.items()}}
