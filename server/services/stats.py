"""
SOM 松麦 - 数据统计服务
提供用户活跃度、商品缓存、对话统计等数据面板
"""
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Optional

SERVER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SERVER_DIR, 'data')
USER_DB_PATH = os.path.join(DATA_DIR, 'user_data.db')
PRODUCT_DB_PATH = os.path.join(DATA_DIR, 'product_cache.db')


class StatsService:
    """数据统计服务"""

    def get_user_db(self):
        conn = sqlite3.connect(USER_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def get_product_db(self):
        conn = sqlite3.connect(PRODUCT_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def get_dashboard(self) -> dict:
        """获取综合数据面板"""
        return {
            "users": self.get_user_stats(),
            "products": self.get_product_stats(),
            "chat": self.get_chat_stats(),
            "checkin": self.get_checkin_stats(),
            "system": self.get_system_stats(),
        }

    def get_user_stats(self) -> dict:
        """用户统计"""
        try:
            conn = self.get_user_db()
            cursor = conn.cursor()

            # 总用户数（有签到记录的）
            cursor.execute('SELECT COUNT(DISTINCT user_id) FROM checkin_records')
            total_users = cursor.fetchone()[0]

            # 今日签到用户数
            from datetime import timezone, timedelta
            beijing_tz = timezone(timedelta(hours=8))
            today = datetime.now(beijing_tz).strftime('%Y-%m-%d')
            cursor.execute('SELECT COUNT(*) FROM checkin_records WHERE last_date = ?', (today,))
            today_checkin = cursor.fetchone()[0]

            # 对话用户数
            cursor.execute('SELECT COUNT(DISTINCT user_id) FROM chat_history')
            chat_users = cursor.fetchone()[0]

            # 收藏用户数
            cursor.execute('SELECT COUNT(DISTINCT user_id) FROM product_favorites')
            fav_users = cursor.fetchone()[0]

            conn.close()
            return {
                "total_users": total_users,
                "today_checkin": today_checkin,
                "chat_users": chat_users,
                "favorite_users": fav_users,
                "total_points": self._get_total_points(),
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_total_points(self) -> int:
        """获取总积分发放量"""
        try:
            conn = self.get_user_db()
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(total_points) FROM checkin_records')
            total = cursor.fetchone()[0] or 0
            conn.close()
            return total
        except:
            return 0

    def get_product_stats(self) -> dict:
        """商品缓存统计"""
        try:
            conn = self.get_product_db()
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM product_cache')
            total = cursor.fetchone()[0]

            cursor.execute('SELECT platform, COUNT(*) as cnt FROM product_cache GROUP BY platform')
            platforms = {row['platform']: row['cnt'] for row in cursor.fetchall()}

            # 缓存过期统计（超过24小时未更新）
            cursor.execute('''
                SELECT COUNT(*) FROM product_cache 
                WHERE updated_at < datetime('now', '-1 day')
            ''')
            stale = cursor.fetchone()[0]

            # 最新更新时间
            cursor.execute('SELECT MAX(updated_at) FROM product_cache')
            latest_update = cursor.fetchone()[0]

            conn.close()
            return {
                "total": total,
                "platforms": platforms,
                "stale_items": stale,
                "latest_update": latest_update,
            }
        except Exception as e:
            return {"error": str(e), "total": 0, "platforms": {}, "stale_items": 0}

    def get_chat_stats(self) -> dict:
        """对话统计"""
        try:
            conn = self.get_user_db()
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM chat_history')
            total = cursor.fetchone()[0]

            # 今日对话数
            from datetime import timezone, timedelta
            beijing_tz = timezone(timedelta(hours=8))
            today = datetime.now(beijing_tz).strftime('%Y-%m-%d')
            cursor.execute('SELECT COUNT(*) FROM chat_history WHERE date(created_at) = ?', (today,))
            today_count = cursor.fetchone()[0]

            # 不同session数
            cursor.execute('SELECT COUNT(DISTINCT session_id) FROM chat_history')
            sessions = cursor.fetchone()[0]

            conn.close()
            return {
                "total_chats": total,
                "today_chats": today_count,
                "total_sessions": sessions,
            }
        except Exception as e:
            return {"error": str(e)}

    def get_checkin_stats(self) -> dict:
        """签到统计"""
        try:
            conn = self.get_user_db()
            cursor = conn.cursor()

            # 连续签到最长
            cursor.execute('SELECT MAX(streak) FROM checkin_records')
            max_streak = cursor.fetchone()[0] or 0

            # 积分排行榜（Top 10）
            cursor.execute('''
                SELECT user_id, total_points, streak, last_date 
                FROM checkin_records 
                ORDER BY total_points DESC 
                LIMIT 10
            ''')
            leaderboard = [dict(row) for row in cursor.fetchall()]

            conn.close()
            return {
                "max_streak": max_streak,
                "leaderboard": leaderboard,
            }
        except Exception as e:
            return {"error": str(e)}

    def get_system_stats(self) -> dict:
        """系统运行状态"""
        import psutil
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            return {
                "cpu_percent": cpu,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used // (1024 * 1024),
                "memory_total_mb": memory.total // (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used // (1024 * 1024 * 1024),
                "disk_total_gb": disk.total // (1024 * 1024 * 1024),
            }
        except ImportError:
            return {
                "note": "psutil not installed, system stats unavailable",
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_percent": 0,
            }
        except Exception as e:
            return {"error": str(e)}