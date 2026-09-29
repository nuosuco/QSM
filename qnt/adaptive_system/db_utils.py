"""
统一的数据库连接工具 - 所有SQLite连接必须通过这个模块
自动启用busy_timeout，WAL模式只设置一次（PRAGMA journal_mode=WAL需要排他锁，不能每次都调）
"""
import sqlite3
import logging
import os

logger = logging.getLogger('DBUtils')

DEFAULT_TIMEOUT = 30
DEFAULT_BUSY_TIMEOUT = 30000  # 30秒

# 标记WAL是否已设置
_wal_initialized = set()

def _ensure_wal(db_path: str):
    """一次性设置WAL模式（只在第一次连接时执行）"""
    real_path = os.path.abspath(db_path)
    if real_path in _wal_initialized:
        return
    try:
        conn = sqlite3.connect(real_path, timeout=DEFAULT_TIMEOUT)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute(f'PRAGMA busy_timeout={DEFAULT_BUSY_TIMEOUT}')
        conn.commit()
        conn.close()
        _wal_initialized.add(real_path)
        logger.info(f"✅ WAL模式已设置: {real_path}")
    except Exception as e:
        logger.warning(f"WAL设置失败(非致命): {e}")

def get_connection(db_path: str, check_same_thread: bool = False, **kwargs):
    """
    获取SQLite连接，自动确保WAL模式 + busy_timeout

    用法：
        from .db_utils import get_connection
        conn = get_connection('/path/to/db.sqlite')
        # 使用完毕后必须 conn.close()

    2026-09-21 锁库修复：默认 isolation_level=None（autocommit 模式）
    - 旧行为（默认 isolation_level=''）：任何 DML 自动开隐式事务，要等 commit/rollback
      才释放写锁。DataCollector 高频写 tick + 多个模块各自长连接 → 写锁排队，
      表现为 "market_data 写库失败(重试3次仍锁库)"，回测/模拟线程的读也被拖住。
    - 新行为：每条语句自动提交，写锁只在该语句执行期间持有，微秒级；
      需要跨语句原子性的调用方自己 conn.isolation_level = '' + 显式 BEGIN。
    """
    _ensure_wal(db_path)
    kwargs.setdefault('isolation_level', None)  # autocommit
    conn = sqlite3.connect(
        db_path,
        check_same_thread=check_same_thread,
        timeout=DEFAULT_TIMEOUT,
        **kwargs
    )
    # busy_timeout 每次都设（这个不需要排他锁）
    conn.execute(f'PRAGMA busy_timeout={DEFAULT_BUSY_TIMEOUT}')
    return conn
