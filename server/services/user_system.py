# -*- coding: utf-8 -*-
"""
SOM 用户系统 + 体质评测记录
- 匿名ID注册/识别（不用登录即可用）
- 轻量登录（手机号），登录后合并匿名数据
- token 会话（纯标准库实现，无第三方依赖）
- 体质评测独立存档（tizhi_records）
"""
import os
import sqlite3
import secrets
import hashlib
import time
from datetime import datetime, timezone, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
USER_DB_PATH = os.path.join(DATA_DIR, "user_data.db")

TOKEN_TTL = 60 * 60 * 24 * 30  # token 有效期 30 天


def _now_beijing():
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))


def _conn():
    conn = sqlite3.connect(USER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_user_system():
    """建表：users / auth_tokens / tizhi_records。幂等，可重复调用。"""
    conn = _conn()
    c = conn.cursor()

    # 用户主表（统一账号：phone / email / wechat_openid 三合一）
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            phone TEXT UNIQUE,
            email TEXT UNIQUE,
            wechat_openid TEXT UNIQUE,
            nickname TEXT DEFAULT '养生用户',
            avatar TEXT,
            is_anonymous INTEGER DEFAULT 1,
            points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 验证码表（短信/邮箱通用）
    c.execute('''
        CREATE TABLE IF NOT EXISTS verify_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            code TEXT NOT NULL,
            channel TEXT NOT NULL DEFAULT 'sms',
            purpose TEXT NOT NULL DEFAULT 'login',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0
        )
    ''')

    # 登录 token
    c.execute('''
        CREATE TABLE IF NOT EXISTS auth_tokens (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        )
    ''')

    # 体质评测记录（核心数据，独立存档）
    c.execute('''
        CREATE TABLE IF NOT EXISTS tizhi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            tizhi TEXT NOT NULL,
            zhengxing TEXT,
            symptoms TEXT,
            advice TEXT,
            source TEXT DEFAULT 'chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('CREATE INDEX IF NOT EXISTS idx_token_user ON auth_tokens(user_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_tizhi_user ON tizhi_records(user_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_openid ON users(wechat_openid)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_codes_target ON verify_codes(target)')

    # 迁移：已有数据库加新字段（幂等）
    existing_cols = [row[1] for row in c.execute('PRAGMA table_info(users)').fetchall()]
    if 'email' not in existing_cols:
        c.execute('ALTER TABLE users ADD COLUMN email TEXT UNIQUE')
    if 'wechat_openid' not in existing_cols:
        c.execute('ALTER TABLE users ADD COLUMN wechat_openid TEXT UNIQUE')

    conn.commit()
    conn.close()


# ---------- 用户 ----------

def get_or_create_anonymous(user_id: str) -> dict:
    """确保匿名用户存在，返回用户信息。"""
    conn = _conn()
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    now = _now_beijing().isoformat()
    if not row:
        conn.execute(
            "INSERT INTO users (user_id, is_anonymous, created_at, last_active) VALUES (?, 1, ?, ?)",
            (user_id, now, now),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    else:
        conn.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (now, user_id))
        conn.commit()
    conn.close()
    return dict(row)


def get_user(user_id: str):
    conn = _conn()
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_profile(user_id: str, nickname: str = None, avatar: str = None):
    conn = _conn()
    fields, vals = [], []
    if nickname is not None:
        fields.append("nickname = ?"); vals.append(nickname)
    if avatar is not None:
        fields.append("avatar = ?"); vals.append(avatar)
    if fields:
        vals.append(user_id)
        conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?", vals)
        conn.commit()
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------- 登录 / token ----------

def _hash_phone(phone: str) -> str:
    return hashlib.sha256(phone.encode()).hexdigest()[:16]


def login_by_phone(phone: str, anonymous_user_id: str = None) -> dict:
    """
    手机号登录。若该手机号已注册，复用账号；否则新建正式账号。
    若带 anonymous_user_id，把匿名数据合并进正式账号。
    返回 {user, token}
    """
    phone = (phone or "").strip()
    conn = _conn()
    now = _now_beijing().isoformat()

    row = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
    if row:
        user_id = row["user_id"]
        conn.execute("UPDATE users SET is_anonymous = 0, last_active = ? WHERE user_id = ?", (now, user_id))
    else:
        user_id = "u_" + secrets.token_hex(12)
        conn.execute(
            "INSERT INTO users (user_id, phone, is_anonymous, created_at, last_active) VALUES (?, ?, 0, ?, ?)",
            (user_id, phone, now, now),
        )
    conn.commit()

    # 合并匿名数据（把旧 user_id 的记录改挂到正式账号下）
    if anonymous_user_id and anonymous_user_id != user_id:
        _merge_anonymous(conn, anonymous_user_id, user_id)

    token = _issue_token(conn, user_id)
    user = dict(conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone())
    conn.close()
    return {"user": user, "token": token}


def _merge_anonymous(conn, anon_id: str, target_id: str):
    """把匿名用户产生的数据迁移到正式账号。冲突记录直接改 user_id。"""
    tables = ["tizhi_records", "chat_history", "search_history", "checkin_records"]
    for t in tables:
        try:
            conn.execute(f"UPDATE {t} SET user_id = ? WHERE user_id = ?", (target_id, anon_id))
        except sqlite3.Error:
            pass
    # 收藏表有 UNIQUE(user_id,item_id)，逐条处理避免冲突
    try:
        rows = conn.execute("SELECT item_id FROM product_favorites WHERE user_id = ?", (target_id,)).fetchall()
        existing = {r["item_id"] for r in rows}
        for r in conn.execute("SELECT * FROM product_favorites WHERE user_id = ?", (anon_id,)).fetchall():
            if r["item_id"] not in existing:
                conn.execute("UPDATE product_favorites SET user_id = ? WHERE id = ?", (target_id, r["id"]))
    except sqlite3.Error:
        pass
    conn.commit()


def _issue_token(conn, user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    expires = _now_beijing() + timedelta(seconds=TOKEN_TTL)
    conn.execute(
        "INSERT INTO auth_tokens (token, user_id, expires_at) VALUES (?, ?, ?)",
        (token, user_id, expires.isoformat()),
    )
    conn.commit()
    return token


def verify_token(token: str):
    """校验 token，返回 user_id 或 None。过期自动清理。"""
    if not token:
        return None
    conn = _conn()
    row = conn.execute("SELECT * FROM auth_tokens WHERE token = ?", (token,)).fetchone()
    if not row:
        conn.close()
        return None
    if row["expires_at"] < _now_beijing().isoformat():
        conn.execute("DELETE FROM auth_tokens WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        return None
    conn.close()
    return row["user_id"]


# ---------- 体质评测记录 ----------

def add_tizhi_record(user_id: str, tizhi: str, zhengxing: str = None,
                     symptoms: str = None, advice: str = None, source: str = "chat") -> dict:
    conn = _conn()
    cur = conn.execute(
        "INSERT INTO tizhi_records (user_id, tizhi, zhengxing, symptoms, advice, source) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, tizhi, zhengxing, symptoms, advice, source),
    )
    rid = cur.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM tizhi_records WHERE id = ?", (rid,)).fetchone()
    conn.close()
    return dict(row)


def get_tizhi_records(user_id: str, limit: int = 50) -> list:
    conn = _conn()
    rows = conn.execute(
        "SELECT * FROM tizhi_records WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_tizhi(user_id: str):
    conn = _conn()
    row = conn.execute(
        "SELECT * FROM tizhi_records WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


init_user_system()
