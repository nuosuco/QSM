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
            password_hash TEXT,
            account TEXT UNIQUE,
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

    # 密码重置token表
    c.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT,
            photo_features BLOB,    -- 2026-10-14 照片视觉特征向量(base64 float32), 健康画像多维趋势用, 不存原图
            photo_hash TEXT        -- 2026-10-14 照片视觉指纹(短字符串), 健康画像趋势比对用
        )
    ''')
    # 2026-10-14 向量组学习(老库迁移): tizhi_records 若缺新列则补上(幂等)
    try:
        _tcols = [r[1] for r in c.execute('PRAGMA table_info(tizhi_records)').fetchall()]
        if 'session_id' not in _tcols:
            c.execute('ALTER TABLE tizhi_records ADD COLUMN session_id TEXT')
        if 'photo_features' not in _tcols:
            c.execute('ALTER TABLE tizhi_records ADD COLUMN photo_features BLOB')
        if 'photo_hash' not in _tcols:
            c.execute('ALTER TABLE tizhi_records ADD COLUMN photo_hash TEXT')
    except Exception as e:
        print(f'[user_system] tizhi_records 迁移(忽略): {e}')

    # 2026-10-13 小蕊加: 人脸特征向量表(方案B)
    # 只存 512 维 float 向量的 base64 压缩 + 创建时间, 不存原图/不存可逆人脸信息
    # 用户可一键删除自己的存档(隐私合规)
    c.execute('''
        CREATE TABLE IF NOT EXISTS face_vectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            embedding BLOB NOT NULL,        -- base64 压缩的 512 维 float32 向量 (~512*4 字节 ~ 2KB)
            model_version TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT NULL
        )
    ''')
    # 2026-10-14 向量组学习: 不再 UNIQUE(user_id, model_version), 允许一个用户存多条历史脸向量
    c.execute('CREATE INDEX IF NOT EXISTS idx_face_user ON face_vectors(user_id, model_version)')
    # 兼容旧库: 若已有 UNIQUE 约束的旧表, 迁移去 UNIQUE(保留数据)
    try:
        tsql = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='face_vectors'").fetchone()[0]
        if 'UNIQUE(user_id, model_version)' in tsql.replace(' ', ''):
            old_rows = conn.execute("SELECT id, user_id, embedding, model_version, created_at FROM face_vectors").fetchall()
            conn.execute("ALTER TABLE face_vectors RENAME TO face_vectors_old")
            conn.execute('''CREATE TABLE face_vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                embedding BLOB NOT NULL,
                model_version TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT NULL
            )''')
            conn.execute("INSERT INTO face_vectors (id, user_id, embedding, model_version, created_at) "
                         "SELECT id, user_id, embedding, model_version, created_at FROM face_vectors_old")
            conn.execute("DROP TABLE face_vectors_old")
            print('[user_system] face_vectors 迁移: 去掉 UNIQUE, 支持向量组学习')
    except Exception as e:
        print(f'[user_system] face_vectors 迁移检查(忽略): {e}')
    conn.commit()

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
                     symptoms: str = None, advice: str = None, source: str = "chat",
                     session_id: str = None,
                     photo_features: bytes = None, photo_hash: str = None) -> dict:
    """存体质记录。
    2026-10-12 中华要求: 用户中心数据是健康大数据, 要压缩到最小存储——
    只留关键字段, symptoms/advice 截断存摘要, 不存整段原文。
    2026-10-13 中华规则(重要): 小麦辨证一次 = 一次对话 = 一条记录, 一一对应。
    所以【不去重】——每次辨证调用都新增一条, 同 session 多次辨证就是多条。
    session_id 仍记录(追溯用), 但不再用它覆盖旧记录。
    """
    def _clip(s, n):
        if not s: return s
        s = s.replace('\n', ' ')
        return s[:n] if len(s) > n else s
    symptoms_c = _clip(symptoms, 500)
    # 2026-10-13 中华反馈: 自动记录的 advice 被截到 500 字显得"不完整、混乱"(换行被压成空格)。
    # advice 存完整原文 + 保留换行(展开时 markdown 渲染); 仅极端情况(>4000字)才截断防膨胀。
    advice_c = advice if advice else None
    if advice_c and len(advice_c) > 4000:
        advice_c = advice_c[:4000]
    conn = _conn()
    # 2026-10-14 时区统一: created_at 显式存北京时间(UTC+8), 不用 SQLite CURRENT_TIMESTAMP(UTC),
    # 与 face_vectors(_now()) 及前端显示口径一致, 避免时间顺序混乱。
    from datetime import datetime, timezone, timedelta as _td
    _ca = datetime.now(timezone.utc).astimezone(timezone(_td(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    cur = conn.execute(
        "INSERT INTO tizhi_records (user_id, tizhi, zhengxing, symptoms, advice, source, session_id, photo_features, photo_hash, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, tizhi, zhengxing, symptoms_c, advice_c, source, session_id, photo_features, photo_hash, _ca),
    )
    rid = cur.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM tizhi_records WHERE id = ?", (rid,)).fetchone()
    conn.close()
    return dict(row)


def get_tizhi_records(user_id: str, limit: int = 50, offset: int = 0) -> tuple:
    conn = _conn()
    # 2026-10-13 中华规则: 小麦辨证一次=一次对话=一条记录, 一一对应
    # 所以【不按 session 去重】, 直接返回最新 limit 条(每次辨证=一条)
    total = conn.execute(
        "SELECT COUNT(*) n FROM tizhi_records WHERE user_id=?", (user_id,)
    ).fetchone()["n"]
    rows = conn.execute(
        "SELECT * FROM tizhi_records WHERE user_id=? ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
        (user_id, limit, offset)
    ).fetchall()
    conn.close()
    # 2026-10-14 时区统一: 库内 created_at 已是北京时间(UTC+8), 直接返回, 不再换算
    return [dict(r) for r in rows], total


def get_latest_tizhi(user_id: str):
    conn = _conn()
    row = conn.execute(
        "SELECT * FROM tizhi_records WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


init_user_system()

# ========== 密码相关函数 ==========

import hashlib
import secrets

def hash_password(password: str) -> str:
    """密码哈希"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}${password_hash}"

def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    if not password_hash or '$' not in password_hash:
        return False
    parts = password_hash.split('$')
    if len(parts) != 2:
        return False
    salt, stored_hash = parts
    computed_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return computed_hash == stored_hash

def generate_reset_token(user_id: str) -> str:
    """生成密码重置token"""
    token = secrets.token_urlsafe(32)
    from datetime import datetime, timezone, timedelta
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    conn = _conn()
    conn.execute(
        "INSERT INTO password_reset_tokens (token, user_id, expires_at) VALUES (?, ?, ?)",
        (token, user_id, expires_at.isoformat())
    )
    conn.commit()
    conn.close()
    return token

def verify_reset_token(token: str) -> dict:
    """验证密码重置token"""
    from datetime import datetime, timezone
    conn = _conn()
    row = conn.execute(
        "SELECT * FROM password_reset_tokens WHERE token = ? AND used = 0 AND expires_at > ?",
        (token, datetime.now(timezone.utc).isoformat())
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def reset_password(user_id: str, new_password: str) -> bool:
    """重置密码"""
    new_hash = hash_password(new_password)
    conn = _conn()
    conn.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (new_hash, user_id))
    conn.execute("UPDATE password_reset_tokens SET used = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

def register_with_password(account: str, password: str, nickname: str = None) -> dict:
    """用账号+密码注册"""
    import secrets as secrets_mod
    conn = _conn()
    
    # 检查账号是否已存在
    existing = conn.execute("SELECT user_id FROM users WHERE account = ?", (account,)).fetchone()
    if existing:
        conn.close()
        return {"success": False, "error": "账号已存在"}
    
    user_id = "u_" + secrets_mod.token_hex(12)
    password_hash = hash_password(password)
    now = _now_beijing().isoformat()
    
    conn.execute(
        "INSERT INTO users (user_id, account, password_hash, nickname, is_anonymous, created_at, last_active) VALUES (?, ?, ?, ?, 0, ?, ?)",
        (user_id, account, password_hash, nickname or account, now, now)
    )
    conn.commit()
    conn.close()
    
    return {"success": True, "user_id": user_id}

def login_with_password(account: str, password: str, anonymous_user_id: str = None) -> dict:
    """用账号+密码登录（自动注册新用户）
    
    2026-10-15 自动绑定邮箱: 登录成功后, 若同昵称的已有账号绑了邮箱,
    则自动把邮箱归并到当前账号(一人一户, 邮箱前缀匹配或昵称匹配)。
    """
    conn = _conn()
    # 2026-10-15 修复: 先在 account 列找; 找不到再去 email/nickname 列找同一个人(邮箱前缀匹配),
    # 找到了就登录(不盲注册新号)。彻底杜绝"邮箱行有密码、昵称行没密码→填昵称又建新号"的双账户问题。
    row = conn.execute("SELECT * FROM users WHERE account = ?", (account,)).fetchone()
    
    if not row:
        # 2026-10-15 修复: 邮箱前缀匹配——用户输入邮箱或邮箱前缀, 都能找到邮箱行(不盲注册新号)
        norm = account.lower().strip()
        row = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password_hash IS NOT NULL ORDER BY last_active DESC LIMIT 1",
            (norm,)
        ).fetchone() or conn.execute(
            "SELECT * FROM users WHERE email LIKE ? AND password_hash IS NOT NULL ORDER BY last_active DESC LIMIT 1",
            (f"{norm}@%",)
        ).fetchone()
    
    if not row:
        # 2026-10-15 修复: 昵称匹配(兼容旧数据带"养生用户"前缀的昵称), 排除匿名归档账号
        norm = account.strip()
        for alias in (norm, f"养生用户{norm}"):
            row = conn.execute(
                "SELECT * FROM users WHERE nickname = ? AND is_anonymous = 0 AND password_hash IS NOT NULL ORDER BY last_active DESC LIMIT 1",
                (alias,)
            ).fetchone()
            if row:
                break
    
    if not row:
        # 真正的新用户: 才注册
        user_id = f"user_pw_{int(time.time())}"
        password_hash = hash_password(password)
        # 2026-10-15 中华要求: 昵称不加"养生用户"前缀, 直接用账号名(简短好记)
        conn.execute("INSERT INTO users (user_id, account, password_hash, nickname, created_at, is_anonymous) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, account, password_hash, account, int(time.time()), 0))
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not row:
            conn.close()
            return {"success": False, "error": "账号创建失败"}
    
    
    if not row:
        conn.close()
        return {"success": False, "error": "账号不存在"}
    
    if not row["password_hash"]:
        conn.close()
        return {"success": False, "error": "该账号未设置密码，请使用其他方式登录"}
    
    if not verify_password(password, row["password_hash"]):
        conn.close()
        return {"success": False, "error": "密码错误"}
    
    # 2026-10-15 自动绑定邮箱: 检查同昵称的已有账号是否绑了邮箱
    _auto_bind_email_for_password(conn, row)
    
    # 匿名数据归并
    if anonymous_user_id and anonymous_user_id != row["user_id"]:
        _merge_anonymous(conn, anonymous_user_id, row["user_id"])
    
    # 生成token
    token = _issue_token(conn, row["user_id"])
    
    user = dict(conn.execute("SELECT * FROM users WHERE user_id = ?", (row["user_id"],)).fetchone())
    user.pop("password_hash", None)
    conn.close()
    
    return {"success": True, "user": user, "token": token}


def _auto_bind_email_for_password(conn, user_row):
    """2026-10-15 自动绑定邮箱: 密码登录时自动把同昵称/邮箱前缀匹配到的邮箱绑上。
    
    匹配规则:
    1. 当前账号已有 email → 跳过
    2. 找同昵称的其他账号, 且其绑了邮箱 → 把邮箱搬过来(把对方 email 置空, 避免撞唯一约束)
    3. 匹配失败则静默跳过, 不影响登录
    """
    user_id = user_row["user_id"]
    account = user_row["account"]
    
    # 1. 已有邮箱就不动
    if user_row["email"]:
        return
    
    nickname = user_row["nickname"] or account
    
    # 2. 找同昵称且绑了邮箱的其他账号(排除匿名归档账号)
    candidates = conn.execute(
        "SELECT user_id, email, account FROM users WHERE nickname = ? AND email IS NOT NULL AND user_id != ? AND is_anonymous = 0 ORDER BY last_active DESC LIMIT 1",
        (nickname, user_id)
    ).fetchone()
    
    if not candidates:
        # 也试试邮箱前缀匹配: 账号名 == 邮箱前缀
        candidates = conn.execute(
            "SELECT user_id, email, account FROM users WHERE email IS NOT NULL AND user_id != ? AND is_anonymous = 0 "
            "AND email LIKE ? ESCAPE '\\' ORDER BY last_active DESC LIMIT 1",
            (user_id, f"{account}@%")
        ).fetchone()
    
    if not candidates:
        return
    
    # 3. 把邮箱搬过来(对方 email 置空, 避免撞唯一约束)
    conn.execute("UPDATE users SET email = NULL WHERE user_id = ?", (candidates["user_id"],))
    conn.execute("UPDATE users SET email = ? WHERE user_id = ?", (candidates["email"], user_id))
    conn.commit()
    print(f"[auto_bind_email] 密码账号 {user_id}({account}) 自动绑定邮箱 {candidates['email']}")
