"""
SOM 统一认证服务
- 手机号 + 短信验证码登录（阿里云 SMS）
- 邮箱 + 邮件验证码登录（SMTP）
- 微信小程序登录（wx.login → openid）
- 统一账号：同一个 phone/email/openid 对应同一个 user_id
"""

import json
import os
import random
import secrets
import smtplib
import string
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText

# ---------- 配置 ----------

AUTH_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "auth_config.json")

def _load_auth_config() -> dict:
    """加载认证配置（阿里云SMS、SMTP邮箱、微信小程序）"""
    defaults = {
        "sms": {
            "enabled": False,
            "provider": "aliyun",
            "access_key_id": "",
            "access_key_secret": "",
            "sign_name": "",
            "template_code": "",
            "region": "cn-hangzhou"
        },
        "email": {
            "enabled": False,
            "smtp_host": "",
            "smtp_port": 465,
            "smtp_user": "",
            "smtp_pass": "",
            "from_name": "SOM松麦",
            "use_ssl": True
        },
        "wechat": {
            "enabled": False,
            "appid": "",
            "secret": ""
        },
        "code_length": 6,
        "code_expire_minutes": 5,
        "code_cooldown_seconds": 60,
        "max_attempts_per_hour": 10
    }
    if os.path.exists(AUTH_CONFIG_PATH):
        try:
            with open(AUTH_CONFIG_PATH, "r") as f:
                cfg = json.load(f)
            # 合并默认值
            for section in ["sms", "email", "wechat"]:
                if section in cfg:
                    defaults[section].update(cfg[section])
            for k in ["code_length", "code_expire_minutes", "code_cooldown_seconds", "max_attempts_per_hour"]:
                if k in cfg:
                    defaults[k] = cfg[k]
        except Exception:
            pass
    return defaults


# ---------- 验证码存储（内存 + 数据库双保险） ----------

_code_store = {}  # {target: {code, created_at, attempts}}

def _generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def _check_cooldown(target: str, cooldown: int) -> bool:
    """检查是否在冷却期内"""
    entry = _code_store.get(target)
    if entry and (time.time() - entry["created_at"]) < cooldown:
        return False
    return True


def _check_rate_limit(target: str, max_per_hour: int) -> bool:
    """简单频率限制"""
    entry = _code_store.get(target)
    if entry and entry.get("hour_count", 0) >= max_per_hour:
        return False
    return True


# ---------- 短信发送 ----------

def normalize_phone(phone: str, country_code: str = "+86") -> str:
    """
    统一手机号为 E.164 格式：+国家码+号码
    例：('13800138000', '+86') → '+8613800138000'
         ('+14155551234', '') → '+14155551234'
    """
    phone = (phone or "").strip().replace("-", "").replace(" ", "")
    if phone.startswith("+"):
        return phone
    cc = (country_code or "+86").strip()
    if not cc.startswith("+"):
        cc = "+" + cc
    # 去掉号码前面多余的0（某些国家习惯加0）
    phone = phone.lstrip("0")
    return cc + phone


def is_china_phone(e164_phone: str) -> bool:
    """判断是否中国大陆手机号"""
    return e164_phone.startswith("+86") and len(e164_phone) == 14


def send_sms_code(phone: str, country_code: str = "+86") -> dict:
    """发送短信验证码（支持全球手机号）"""
    cfg = _load_auth_config()
    sms_cfg = cfg["sms"]

    e164 = normalize_phone(phone, country_code)

    if not sms_cfg.get("enabled"):
        return {"success": False, "error": "短信服务未配置，请联系管理员"}

    if not _check_cooldown(e164, cfg["code_cooldown_seconds"]):
        return {"success": False, "error": f"发送太频繁，请{cfg['code_cooldown_seconds']}秒后再试"}

    if not _check_rate_limit(e164, cfg["max_attempts_per_hour"]):
        return {"success": False, "error": "今日发送次数已达上限，请明天再试"}

    code = _generate_code(cfg["code_length"])

    # 阿里云 SMS
    try:
        from alibabacloud_dysmsapi20170525.client import Client
        from alibabacloud_dysmsapi20170525 import models as dysms_models
        from alibabacloud_tea_openapi import models as open_api_models

        config = open_api_models.Config(
            access_key_id=sms_cfg["access_key_id"],
            access_key_secret=sms_cfg["access_key_secret"],
        )
        config.endpoint = f"dysmsapi.{sms_cfg.get('region', 'cn-hangzhou')}.aliyuncs.com"
        client = Client(config)

        # 国际短信用国际签名/模板（如果配置了的话）
        sign = sms_cfg["sign_name"]
        tpl = sms_cfg["template_code"]
        if not is_china_phone(e164):
            sign = sms_cfg.get("intl_sign_name", sign)
            tpl = sms_cfg.get("intl_template_code", tpl)

        request = dysms_models.SendSmsRequest(
            phone_numbers=e164,
            sign_name=sign,
            template_code=tpl,
            template_param=json.dumps({"code": code}),
        )
        response = client.send_sms(request)
        body = response.body
        if body.code != "OK":
            return {"success": False, "error": f"短信发送失败: {body.message}"}
    except ImportError:
        return {"success": False, "error": "短信SDK未安装"}
    except Exception as e:
        return {"success": False, "error": f"短信发送异常: {str(e)[:100]}"}

    # 存储验证码
    expire_at = time.time() + cfg["code_expire_minutes"] * 60
    _code_store[e164] = {
        "code": code,
        "created_at": time.time(),
        "expires_at": expire_at,
        "attempts": 0,
        "hour_count": _code_store.get(e164, {}).get("hour_count", 0) + 1,
        "channel": "sms"
    }

    # 脱敏显示
    masked = e164[:4] + "****" + e164[-4:] if len(e164) > 8 else e164
    return {"success": True, "message": f"验证码已发送至 {masked}"}


# ---------- 邮件发送 ----------

def send_email_code(email: str) -> dict:
    """发送邮件验证码"""
    cfg = _load_auth_config()
    email_cfg = cfg["email"]

    if not email_cfg.get("enabled"):
        return {"success": False, "error": "邮件服务未配置，请联系管理员"}

    if not _check_cooldown(email, cfg["code_cooldown_seconds"]):
        return {"success": False, "error": f"发送太频繁，请{cfg['code_cooldown_seconds']}秒后再试"}

    if not _check_rate_limit(email, cfg["max_attempts_per_hour"]):
        return {"success": False, "error": "今日发送次数已达上限，请明天后再试"}

    code = _generate_code(cfg["code_length"])

    # SMTP 发送
    try:
        subject = f"【SOM松麦】验证码：{code}"
        body_html = f"""
        <div style="font-family: sans-serif; max-width: 400px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4a9d6e;">SOM 松麦</h2>
            <p>您的验证码是：</p>
            <p style="font-size: 32px; font-weight: bold; color: #333; letter-spacing: 4px;">{code}</p>
            <p style="color: #666;">{cfg['code_expire_minutes']} 分钟内有效，请勿泄露给他人。</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">SOM 松麦 · 中医辨证 · 有机养生</p>
        </div>
        """
        msg = MIMEText(body_html, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = f"{email_cfg['from_name']} <{email_cfg['smtp_user']}>"
        msg["To"] = email

        if email_cfg.get("use_ssl", True):
            server = smtplib.SMTP_SSL(email_cfg["smtp_host"], email_cfg["smtp_port"], timeout=15)
        else:
            server = smtplib.SMTP(email_cfg["smtp_host"], email_cfg["smtp_port"], timeout=15)
            server.starttls()

        server.login(email_cfg["smtp_user"], email_cfg["smtp_pass"])
        server.sendmail(email_cfg["smtp_user"], [email], msg.as_string())
        server.quit()
    except Exception as e:
        return {"success": False, "error": f"邮件发送失败: {str(e)[:100]}"}

    # 存储验证码
    expire_at = time.time() + cfg["code_expire_minutes"] * 60
    _code_store[email] = {
        "code": code,
        "created_at": time.time(),
        "expires_at": expire_at,
        "attempts": 0,
        "hour_count": _code_store.get(email, {}).get("hour_count", 0) + 1,
        "channel": "email"
    }

    return {"success": True, "message": f"验证码已发送至 {email}"}


# ---------- 验证码校验 ----------

def verify_code(target: str, code: str) -> dict:
    """校验验证码，返回 {success, error?}"""
    entry = _code_store.get(target)
    if not entry:
        return {"success": False, "error": "请先获取验证码"}

    if time.time() > entry["expires_at"]:
        del _code_store[target]
        return {"success": False, "error": "验证码已过期，请重新获取"}

    if entry["attempts"] >= 5:
        del _code_store[target]
        return {"success": False, "error": "错误次数过多，请重新获取验证码"}

    entry["attempts"] += 1

    if entry["code"] != code.strip():
        return {"success": False, "error": f"验证码错误，还剩{5 - entry['attempts']}次机会"}

    # 验证成功，删除
    del _code_store[target]
    return {"success": True}


# ---------- 统一登录/注册 ----------

def login_or_register(target: str, channel: str, anonymous_user_id: str = None) -> dict:
    """
    统一登录入口：验证通过后调用
    - channel: 'phone' | 'email'
    - target: 手机号或邮箱
    - anonymous_user_id: 匿名用户ID（用于合并数据）
    返回 {user, token}
    """
    from services import user_system

    conn = user_system._conn()
    now = user_system._now_beijing().isoformat()

    # 查找已有用户
    field = "phone" if channel == "phone" else "email"
    row = conn.execute(f"SELECT * FROM users WHERE {field} = ?", (target,)).fetchone()

    if row:
        user_id = row["user_id"]
        conn.execute("UPDATE users SET is_anonymous = 0, last_active = ? WHERE user_id = ?", (now, user_id))
    else:
        # 新用户
        user_id = "u_" + secrets.token_hex(12)
        nickname = f"养生用户{target[-4:]}" if channel == "phone" else f"养生用户{target.split('@')[0][:6]}"
        conn.execute(
            f"INSERT INTO users (user_id, {field}, nickname, is_anonymous, created_at, last_active) VALUES (?, ?, ?, 0, ?, ?)",
            (user_id, target, nickname, now, now),
        )

    conn.commit()

    # 合并匿名数据
    if anonymous_user_id and anonymous_user_id != user_id:
        user_system._merge_anonymous(conn, anonymous_user_id, user_id)

    token = user_system._issue_token(conn, user_id)
    user = dict(conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone())
    conn.close()

    # 不返回敏感字段
    user.pop("phone", None)
    user.pop("email", None)
    user.pop("wechat_openid", None)

    return {"user": user, "token": token}


# ---------- 微信小程序登录 ----------

def wechat_login(code: str, anonymous_user_id: str = None) -> dict:
    """
    小程序 wx.login() 的 code → 换 openid → 登录/注册
    """
    import requests as http_requests

    cfg = _load_auth_config()
    wx_cfg = cfg["wechat"]

    if not wx_cfg.get("enabled"):
        return {"success": False, "error": "微信登录未配置"}

    # 用 code 换 openid
    try:
        resp = http_requests.get(
            "https://api.weixin.qq.com/sns/jscode2session",
            params={
                "appid": wx_cfg["appid"],
                "secret": wx_cfg["secret"],
                "js_code": code,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        data = resp.json()
        if "openid" not in data:
            return {"success": False, "error": f"微信登录失败: {data.get('errmsg', '未知错误')}"}
        openid = data["openid"]
    except Exception as e:
        return {"success": False, "error": f"微信接口异常: {str(e)[:100]}"}


def wechat_web_login(code: str) -> dict:
    """
    微信服务号OAuth2.0网页授权：code → 换access_token → 换openid → 登录/注册
    """
    import requests as http_requests

    cfg = _load_auth_config()
    wx_cfg = cfg["wechat"]

    if not wx_cfg.get("enabled"):
        return {"success": False, "error": "微信服务号登录未配置"}

    # 用 code 换 access_token
    try:
        resp = http_requests.get(
            "https://api.weixin.qq.com/sns/oauth2/access_token",
            params={
                "appid": wx_cfg["appid"],
                "secret": wx_cfg["secret"],
                "code": code,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        data = resp.json()
        if "openid" not in data:
            return {"success": False, "error": f"微信授权失败: {data.get('errmsg', '未知错误')}"}
        openid = data["openid"]
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
    except Exception as e:
        return {"success": False, "error": f"微信接口异常: {str(e)[:100]}"}

    # 获取用户信息（可选，需要snsapi_userinfo权限）
    nickname = "微信用户"
    try:
        user_resp = http_requests.get(
            "https://api.weixin.qq.com/sns/userinfo",
            params={
                "access_token": access_token,
                "openid": openid,
                "lang": "zh_CN",
            },
            timeout=10,
        )
        user_data = user_resp.json()
        if "nickname" in user_data:
            nickname = user_data["nickname"]
    except Exception:
        pass

    # 查找/创建用户
    from services import user_system
    conn = user_system._conn()
    now = user_system._now_beijing().isoformat()

    row = conn.execute("SELECT * FROM users WHERE wechat_openid = ?", (openid,)).fetchone()

    if row:
        user_id = row["user_id"]
        conn.execute("UPDATE users SET is_anonymous = 0, last_active = ? WHERE user_id = ?", (now, user_id))
    else:
        user_id = "u_" + secrets.token_hex(12)
        conn.execute(
            "INSERT INTO users (user_id, wechat_openid, nickname, is_anonymous, created_at, last_active) VALUES (?, ?, ?, 0, ?, ?)",
            (user_id, openid, nickname, now, now),
        )

    conn.commit()
    conn.close()

    token = user_system._issue_token(conn, user_id) if conn else None
    user = dict(conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()) if conn else None
    
    if user:
        user.pop("phone", None)
        user.pop("email", None)
        user.pop("wechat_openid", None)

    return {"success": True, "user": user, "token": token}

    # 查找/创建用户
    from services import user_system

    conn = user_system._conn()
    now = user_system._now_beijing().isoformat()

    row = conn.execute("SELECT * FROM users WHERE wechat_openid = ?", (openid,)).fetchone()

    if row:
        user_id = row["user_id"]
        conn.execute("UPDATE users SET is_anonymous = 0, last_active = ? WHERE user_id = ?", (now, user_id))
    else:
        user_id = "u_" + secrets.token_hex(12)
        conn.execute(
            "INSERT INTO users (user_id, wechat_openid, nickname, is_anonymous, created_at, last_active) VALUES (?, ?, ?, 0, ?, ?)",
            (user_id, openid, "微信用户", now, now),
        )

    conn.commit()

    if anonymous_user_id and anonymous_user_id != user_id:
        user_system._merge_anonymous(conn, anonymous_user_id, user_id)

    token = user_system._issue_token(conn, user_id)
    user = dict(conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone())
    conn.close()

    user.pop("phone", None)
    user.pop("email", None)
    user.pop("wechat_openid", None)

    return {"success": True, "user": user, "token": token}


def bind_phone_to_wechat(user_id: str, phone: str) -> dict:
    """微信用户绑定手机号（统一账号关键步骤）"""
    from services import user_system

    conn = user_system._conn()

    # 检查手机号是否已被其他账号使用
    existing = conn.execute("SELECT user_id FROM users WHERE phone = ? AND user_id != ?", (phone, user_id)).fetchone()
    if existing:
        # 手机号已有账号 → 合并到当前微信账号
        user_system._merge_anonymous(conn, existing["user_id"], user_id)
        conn.execute("UPDATE users SET phone = NULL WHERE user_id = ?", (existing["user_id"],))

    conn.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))
    conn.commit()
    conn.close()

    return {"success": True, "message": "手机号绑定成功"}


# ---------- 状态查询 ----------

def get_auth_status() -> dict:
    """返回各登录方式的配置状态（不暴露密钥）"""
    cfg = _load_auth_config()
    return {
        "sms": {"enabled": cfg["sms"].get("enabled", False), "provider": cfg["sms"].get("provider", "aliyun")},
        "email": {"enabled": cfg["email"].get("enabled", False)},
        "wechat": {"enabled": cfg["wechat"].get("enabled", False)},
        "code_expire_minutes": cfg["code_expire_minutes"],
    }
