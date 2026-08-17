"""
SOM 松麦 - 用户反馈服务
收集用户反馈、建议、Bug报告等
"""
import sqlite3
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, List

SERVER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SERVER_DIR, 'data')
FEEDBACK_DB_PATH = os.path.join(DATA_DIR, 'feedback.db')


def init_feedback_db():
    """初始化反馈数据库"""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(FEEDBACK_DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            feedback_type TEXT DEFAULT 'suggestion',
            content TEXT NOT NULL,
            contact TEXT DEFAULT '',
            page_url TEXT DEFAULT '',
            user_agent TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            reply TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            replied_at TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status)
    ''')

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(FEEDBACK_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class FeedbackService:
    """用户反馈服务"""

    def __init__(self):
        init_feedback_db()

    def submit(self, user_id: str, content: str, feedback_type: str = 'suggestion',
               contact: str = '', page_url: str = '', user_agent: str = '') -> dict:
        """提交反馈"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO feedback (user_id, feedback_type, content, contact, page_url, user_agent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, feedback_type, content[:2000], contact[:200], page_url[:500], user_agent[:500]))
            conn.commit()
            feedback_id = cursor.lastrowid
            return {"success": True, "id": feedback_id, "message": "感谢您的反馈！我们会认真对待每一条建议 🙏"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def get_list(self, user_id: Optional[str] = None, status: Optional[str] = None,
                 limit: int = 20, offset: int = 0) -> dict:
        """获取反馈列表"""
        conn = get_db()
        cursor = conn.cursor()

        conditions = []
        params = []

        if user_id:
            conditions.append('user_id = ?')
            params.append(user_id)
        if status:
            conditions.append('status = ?')
            params.append(status)

        where = 'WHERE ' + ' AND '.join(conditions) if conditions else ''

        cursor.execute(f'SELECT COUNT(*) FROM feedback {where}', params)
        total = cursor.fetchone()[0]

        cursor.execute(f'''
            SELECT * FROM feedback {where}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', params + [limit, offset])
        rows = cursor.fetchall()
        conn.close()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [dict(r) for r in rows]
        }

    def get_stats(self) -> dict:
        """反馈统计"""
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM feedback')
        total = cursor.fetchone()[0]

        cursor.execute('SELECT feedback_type, COUNT(*) as cnt FROM feedback GROUP BY feedback_type')
        types = {row['feedback_type']: row['cnt'] for row in cursor.fetchall()}

        cursor.execute('SELECT status, COUNT(*) as cnt FROM feedback GROUP BY status')
        statuses = {row['status']: row['cnt'] for row in cursor.fetchall()}

        conn.close()
        return {
            "total": total,
            "by_type": types,
            "by_status": statuses,
        }


# 初始化
init_feedback_db()